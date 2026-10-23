# VPN WireGuard — Intermédiaire

**Niveau :** INTERMÉDIAIRE

Ce cours prolonge l’apprentissage de WireGuard : après la création d’un tunnel simple et la lecture d’un fichier de configuration, l’objectif est maintenant de concevoir des topologies réelles, comprendre précisément la sélection des pairs, maîtriser le routage et le filtrage, traiter les contraintes de NAT/MTU et exploiter le VPN de façon observable et sûre.

Les exemples utilisent Linux, `wg` et `wg-quick`. Ils doivent être adaptés aux interfaces, aux distributions, au gestionnaire réseau et aux politiques de sécurité de ton environnement. Les adresses publiques `198.51.100.0/24` et `203.0.113.0/24` sont réservées à la documentation ; elles servent uniquement d’exemples.

> **Analogie** : au niveau Débutant, tu as appris à poser un tunnel protégé entre deux bâtiments. À présent, imagine un réseau logistique : chaque pair est une porte identifiée, `AllowedIPs` représente à la fois le plan d’acheminement vers la bonne porte et la liste des origines admises après déchiffrement. Une clé correcte ne suffit pas si le colis prend la mauvaise route ou si la porte suivante refuse de le transférer.

> **Piège :** ne traite pas l’état WireGuard comme un indicateur universel « VPN connecté ». Un handshake récent valide la communication cryptographique avec un peer, mais ne prouve pas que les routes des LAN, le forwarding, le pare-feu, le DNS et les applications fonctionnent de bout en bout.

---

## 1. Théorie et mécanismes avancés

### 1.1 Rappel ciblé : les composants dont on dépend

WireGuard associe une clé publique à chaque peer et utilise un mécanisme de *cryptokey routing*. Le noyau choisit le peer sortant à partir de la destination intérieure et vérifie, à la réception, que la source du paquet déchiffré appartient aux `AllowedIPs` associés au peer qui l’a envoyé. Sur Linux, `wg` configure l’état WireGuard ; `ip` et le système routent les paquets ; `wg-quick` simplifie la création de l’interface, des adresses, routes et réglages annexes.

Il faut donc séparer quatre questions :

| Question | Responsable principal | Exemple de preuve |
|---|---|---|
| La clé du peer est-elle reconnue et l’échange fonctionne-t-il ? | WireGuard | `wg show wg0` et dernier handshake |
| Quel peer doit recevoir cette destination ? | `AllowedIPs` et table de routage | `wg show wg0 allowed-ips`, `ip route get` |
| Le paquet peut-il traverser la machine ? | Routage Linux, forwarding, nftables/iptables | `sysctl`, règles firewall, compteurs |
| L’application répond-elle ? | Hôte, service, DNS, politique applicative | test TCP/UDP, journaux du service |

> **Astuce :** avant de toucher à la configuration, note l’heure, les adresses sources et destinations, l’interface de sortie attendue et le résultat attendu. Une hypothèse correcte doit prédire une observation vérifiable.

### 1.2 Architecture hub-and-spoke et site-à-site

Une architecture *hub-and-spoke* relie plusieurs sites à un concentrateur. Le concentrateur possède une entrée `[Peer]` distincte pour chaque spoke, avec une clé publique distincte et les préfixes associés à ce site. Les spokes connaissent le préfixe du concentrateur et les réseaux qu’ils doivent atteindre à travers lui. WireGuard ne crée pas à lui seul un maillage complet entre spokes : le hub doit activer le forwarding et son système doit savoir router entre les interfaces et sous-réseaux concernés.

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .blue-text{fill:#93c5fd}.wg-visual svg .green-text{fill:#86efac}.wg-visual svg .amber-text{fill:#fcd34d}.wg-visual svg .red-text{fill:#fda4af}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.wg-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.wg-visual details p{margin:.6rem 0 0}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}.wg-visual a{color:#93c5fd}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 410" role="img" aria-label="Architecture WireGuard multi-site hub-and-spoke. Chaque spoke présente des sous-réseaux distincts et un peer sur le concentrateur." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="408" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">Architecture hub-and-spoke — préfixes explicites par peer</text><rect x="375" y="76" width="250" height="112" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="500" y="104" text-anchor="middle" class="title" fill="#f4f4f5">Concentrateur WireGuard</text><text x="500" y="130" text-anchor="middle" fill="#e4e4e7">wg0 · 10.200.0.1/24</text><text x="500" y="153" text-anchor="middle" class="small" fill="#a1a1aa">Un peer distinct par site</text><rect x="36" y="250" width="250" height="106" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="161" y="278" text-anchor="middle" class="title" fill="#f4f4f5">Site A / peer A</text><text x="161" y="305" text-anchor="middle" fill="#e4e4e7">wg0 · 10.200.0.2/32</text><text x="161" y="329" text-anchor="middle" class="small" fill="#a1a1aa">LAN 10.10.0.0/24</text><rect x="714" y="250" width="250" height="106" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="839" y="278" text-anchor="middle" class="title" fill="#f4f4f5">Site B / peer B</text><text x="839" y="305" text-anchor="middle" fill="#e4e4e7">wg0 · 10.200.0.3/32</text><text x="839" y="329" text-anchor="middle" class="small" fill="#a1a1aa">LAN 10.20.0.0/24</text><path d="M270 250 L410 188" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><path d="M730 250 L590 188" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="340" cy="219" r="5" class="packet" fill="#60a5fa"/><circle cx="660" cy="219" r="5" class="packet delay-2" fill="#4ade80"/><rect x="330" y="260" width="340" height="66" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="285" text-anchor="middle" class="title" fill="#f4f4f5">Routage LAN ↔ wg0 ↔ LAN</text><text x="500" y="307" text-anchor="middle" class="small" fill="#a1a1aa">Routes système + IP forwarding + pare-feu</text><text x="500" y="382" text-anchor="middle" class="small" fill="#a1a1aa">Les AllowedIPs côté hub ne doivent pas attribuer les mêmes préfixes à plusieurs spokes.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Dans un hub-and-spoke, le concentrateur possède un peer par site. Chaque peer doit annoncer un ensemble de préfixes non ambigus. WireGuard transporte les paquets, mais les routes système, le forwarding et le pare-feu doivent également autoriser le trajet.</p></div>

Dans une architecture site-à-site, le préfixe LAN annoncé par chaque peer doit être stable et non ambigu. Si deux spokes annoncent chacun `10.20.0.0/24`, le hub ne peut pas deviner quel site tu veux atteindre. Il faut renuméroter, employer une translation contrôlée ou créer une architecture de routage distincte qui résout explicitement ce chevauchement. Une clé distincte par site facilite la révocation et l’attribution des journaux.

### 1.3 `AllowedIPs` : le mécanisme qu’il faut vraiment comprendre

`AllowedIPs` n’est pas simplement une liste de réseaux distants. Cette valeur sert à la sélection cryptographique du peer à l’émission et au contrôle de la source du paquet intérieur reçu. Pour chaque destination intérieure, WireGuard recherche le préfixe correspondant le plus spécifique. Si un paquet est déchiffré depuis un peer mais porte une adresse source qui ne lui est pas autorisée, le paquet intérieur ne doit pas être accepté comme trafic valide de ce peer.

Exemple d’une passerelle A qui atteint le LAN B :

```ini
[Peer]
PublicKey = <CLE_PUBLIQUE_B>
AllowedIPs = 10.200.0.2/32, 10.20.0.0/24
```

Ce réglage associe au peer B son adresse de tunnel `10.200.0.2` ainsi que le LAN distant `10.20.0.0/24`. À l’autre extrémité, il faut des préfixes cohérents pour les réseaux de A. Les adresses de tunnel `/32` attribuées à des peers doivent être uniques sur la passerelle, et les sous-réseaux des sites ne doivent pas se chevaucher sans stratégie explicite.

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .blue-text{fill:#93c5fd}.wg-visual svg .green-text{fill:#86efac}.wg-visual svg .amber-text{fill:#fcd34d}.wg-visual svg .red-text{fill:#fda4af}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.wg-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.wg-visual details p{margin:.6rem 0 0}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}.wg-visual a{color:#93c5fd}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 360" role="img" aria-label="Flux de sélection WireGuard. Le noyau consulte la destination dans AllowedIPs pour choisir le peer sortant, puis vérifie la source intérieure déchiffrée à la réception." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="358" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">AllowedIPs — sélection sortante et validation entrante</text><rect x="35" y="75" width="265" height="92" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="167" y="103" text-anchor="middle" class="title" fill="#f4f4f5">Émission</text><text x="167" y="129" text-anchor="middle" fill="#e4e4e7">Destination IP intérieure</text><text x="167" y="149" text-anchor="middle" class="small" fill="#a1a1aa">Quel peer possède ce préfixe ?</text><rect x="367" y="75" width="265" height="92" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="499" y="103" text-anchor="middle" class="title" fill="#f4f4f5">Table cryptokey routing</text><text x="499" y="129" text-anchor="middle" fill="#e4e4e7">Longest-prefix match</text><text x="499" y="149" text-anchor="middle" class="small" fill="#a1a1aa">Choix du peer et clé publique</text><rect x="699" y="75" width="265" height="92" rx="12" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="831" y="103" text-anchor="middle" class="title" fill="#f4f4f5">Chiffrement vers le peer</text><text x="831" y="129" text-anchor="middle" fill="#e4e4e7">Paquet encapsulé en UDP</text><text x="831" y="149" text-anchor="middle" class="small" fill="#a1a1aa">Transport extérieur</text><path d="M300 121 H367" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><path d="M632 121 H699" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="334" cy="121" r="5" class="packet" fill="#60a5fa"/><circle cx="665" cy="121" r="5" class="packet delay-2" fill="#4ade80"/><path d="M831 167 V210 H499 V239" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9"/><rect x="225" y="239" width="550" height="81" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="267" text-anchor="middle" class="title" fill="#f4f4f5">Réception après déchiffrement</text><text x="500" y="291" text-anchor="middle" fill="#e4e4e7">La source intérieure doit appartenir aux AllowedIPs du peer</text><text x="500" y="309" text-anchor="middle" class="small" fill="#a1a1aa">Sinon, le paquet intérieur est rejeté même si l’authentification a réussi.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">AllowedIPs est à la fois un mécanisme de sélection du peer à l’émission et une vérification de préfixe source à la réception. Sur Linux, `wg-quick` ajoute aussi les routes système déduites des préfixes, sauf si sa gestion des routes est désactivée ou personnalisée.</p></div>

Sur Linux, `wg-quick` déduit généralement les routes à ajouter des `AllowedIPs`. La configuration WireGuard proprement dite ne remplace pas toute la table de routage système. Pour les scénarios avancés, `Table = off` permet de ne pas ajouter ces routes automatiquement ; l’administrateur doit alors créer et maintenir les routes ou règles de routage nécessaires. Ne mets pas `Table = off` simplement pour « réparer » une route sans comprendre l’effet de ce changement.

> **Piège :** ajouter `0.0.0.0/0` à un peer n’est pas une simple autorisation générale. Ce préfixe signifie que le peer peut être sélectionné pour presque toute destination IPv4. Avec `wg-quick`, cela entraîne généralement un traitement spécial des routes par défaut. Il faut vérifier les effets sur l’endpoint, le DNS et IPv6.

### 1.4 Split tunnel et full tunnel

En *split tunnel*, seuls les préfixes explicitement indiqués dans `AllowedIPs` sont dirigés vers le VPN : les réseaux privés passent dans le tunnel, tandis que le reste peut continuer à utiliser la passerelle locale. Cette méthode limite le trafic envoyé vers le concentrateur, mais demande de définir exactement les réseaux internes et le comportement DNS.

En *full tunnel*, le pair prend la route par défaut, par exemple `0.0.0.0/0`, et éventuellement `::/0` pour IPv6. L’accès Internet peut alors sortir par la passerelle VPN. Il faut aussi contrôler le routage de l’adresse extérieure du serveur WireGuard pour éviter de boucler l’envoi de l’endpoint dans le tunnel lui-même. `wg-quick` possède une logique spécifique pour les routes par défaut et le *fwmark* ; si tu écris des règles de routage manuellement, reproduis et vérifie la logique au lieu de mélanger plusieurs stratégies.

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .blue-text{fill:#93c5fd}.wg-visual svg .green-text{fill:#86efac}.wg-visual svg .amber-text{fill:#fcd34d}.wg-visual svg .red-text{fill:#fda4af}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.wg-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.wg-visual details p{margin:.6rem 0 0}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}.wg-visual a{color:#93c5fd}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 370" role="img" aria-label="Comparaison split tunnel et full tunnel. En split tunnel seuls les préfixes privés passent dans le tunnel ; en full tunnel la route par défaut IPv4 et éventuellement IPv6 passe dans WireGuard." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="368" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">Split tunnel et full tunnel — deux politiques de routage</text><rect x="28" y="59" width="455" height="275" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="255" y="88" text-anchor="middle" class="title" fill="#f4f4f5">Split tunnel</text><rect x="54" y="109" width="155" height="58" rx="9" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="131" y="133" text-anchor="middle" class="title" fill="#f4f4f5">Poste</text><text x="131" y="153" text-anchor="middle" class="small" fill="#a1a1aa">10.8.0.2</text><rect x="294" y="109" width="155" height="58" rx="9" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="371" y="133" text-anchor="middle" class="title" fill="#f4f4f5">Réseau privé</text><text x="371" y="153" text-anchor="middle" class="small" fill="#a1a1aa">10.20.0.0/16</text><path d="M209 137 H294" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="251" cy="137" r="5" class="packet" fill="#4ade80"/><rect x="54" y="206" width="155" height="58" rx="9" class="node" fill="#111827" stroke="#64748b"/><text x="131" y="230" text-anchor="middle" class="title" fill="#f4f4f5">Internet public</text><text x="131" y="250" text-anchor="middle" class="small" fill="#a1a1aa">Route locale</text><path d="M131 167 V206" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8"/><text x="255" y="294" text-anchor="middle" class="small" fill="#a1a1aa">Seuls les préfixes sélectionnés vont dans wg0.</text><rect x="517" y="59" width="455" height="275" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="744" y="88" text-anchor="middle" class="title" fill="#f4f4f5">Full tunnel</text><rect x="543" y="109" width="155" height="58" rx="9" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="620" y="133" text-anchor="middle" class="title" fill="#f4f4f5">Poste</text><text x="620" y="153" text-anchor="middle" class="small" fill="#a1a1aa">Toutes destinations</text><rect x="783" y="109" width="155" height="58" rx="9" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="860" y="133" text-anchor="middle" class="title" fill="#f4f4f5">Passerelle VPN</text><text x="860" y="153" text-anchor="middle" class="small" fill="#a1a1aa">Sortie Internet</text><path d="M698 137 H783" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="741" cy="137" r="5" class="packet" fill="#4ade80"/><rect x="663" y="210" width="155" height="58" rx="9" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="740" y="234" text-anchor="middle" class="title" fill="#f4f4f5">0.0.0.0/0</text><text x="740" y="254" text-anchor="middle" class="small" fill="#a1a1aa">et ::/0 si requis</text><path d="M860 167 V188 H740 V210" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9"/><text x="744" y="294" text-anchor="middle" class="small" fill="#a1a1aa">DNS, IPv6, kill switch et route de l’endpoint à contrôler.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Le split tunnel n’envoie que certains préfixes au VPN. Le full tunnel demande une route par défaut à travers le peer et doit traiter aussi les fuites IPv6, le DNS et l’exception de routage nécessaire pour joindre l’endpoint public.</p></div>

Un full tunnel correctement conçu doit examiner au moins :

- **IPv4 et IPv6** : si IPv4 est tunnelé mais pas IPv6, le navigateur peut continuer à sortir en IPv6 par la connexion locale. Si le VPN doit forcer tout le trafic, la route et le filtrage IPv6 font partie du design.
- **DNS** : choisir un résolveur joignable via le chemin voulu, définir les domaines de recherche nécessaires et vérifier ce qui arrive lorsque le tunnel tombe.
- **Endpoint du VPN** : son adresse publique doit rester joignable par le réseau extérieur ; les règles de routage ne doivent pas encapsuler par erreur la route permettant d’établir le tunnel.
- **Kill switch** : si la politique exige l’absence de trafic hors tunnel, le pare-feu doit bloquer les sorties non voulues, tout en laissant passer l’UDP vers l’endpoint et les exceptions de gestion explicitement autorisées.
- **Réseaux locaux** : l’accès à une imprimante, une passerelle de gestion ou un portail captif peut nécessiter une exception délibérée, documentée et testée.

> **Danger :** un kill switch improvisé peut couper SSH, DNS ou la possibilité de rétablir le tunnel. Teste toute modification de règles d’accès à distance avec une console de secours ou un mécanisme de retour arrière planifié.

### 1.5 Encapsulation, MTU et PMTUD

WireGuard encapsule les paquets IP intérieurs dans un transport UDP et un paquet IP extérieur. Chaque enveloppe consomme une partie de la MTU du chemin. Une MTU intérieure trop élevée peut faire fonctionner les petits pings tout en bloquant les transferts HTTPS, les paquets avec options supplémentaires ou les sessions applicatives qui transportent de gros segments.

Une valeur proche de `1420` est parfois un point de départ raisonnable lorsque le réseau sous-jacent offre une MTU de 1500 octets, mais ce n’est pas une règle universelle : l’IPv6 extérieur, le chemin à travers PPPoE, certains tunnels imbriqués ou le cloud peuvent réduire la taille disponible. `wg-quick` calcule généralement une MTU automatique à partir du chemin ; un réglage manuel doit venir d’un test, pas d’une valeur copiée sans examen.

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .blue-text{fill:#93c5fd}.wg-visual svg .green-text{fill:#86efac}.wg-visual svg .amber-text{fill:#fcd34d}.wg-visual svg .red-text{fill:#fda4af}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.wg-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.wg-visual details p{margin:.6rem 0 0}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}.wg-visual a{color:#93c5fd}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 360" role="img" aria-label="Chemin d’un paquet dans WireGuard : paquet IP intérieur, encapsulation UDP et IP extérieur, transfert Internet, authentification et déchiffrement chez le pair distant." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="358" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">Encapsulation : ce qui est visible et ce qui est protégé</text><rect x="34" y="66" width="275" height="70" rx="10" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="171" y="93" text-anchor="middle" class="title" fill="#f4f4f5">Paquet IP intérieur</text><text x="171" y="117" text-anchor="middle" fill="#e4e4e7">Source privée → destination privée</text><path d="M309 101 H368" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><circle cx="338" cy="101" r="5" class="packet" fill="#60a5fa"/><rect x="368" y="57" width="267" height="88" rx="10" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="501" y="83" text-anchor="middle" class="title" fill="#f4f4f5">Paquet WireGuard</text><text x="501" y="107" text-anchor="middle" fill="#e4e4e7">UDP + données authentifiées/chiffrées</text><text x="501" y="128" text-anchor="middle" class="small" fill="#a1a1aa">En-tête extérieur nécessaire au transport</text><path d="M635 101 H694" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="664" cy="101" r="5" class="packet delay-1" fill="#4ade80"/><rect x="694" y="66" width="272" height="70" rx="10" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="830" y="93" text-anchor="middle" class="title" fill="#f4f4f5">Réseau Internet</text><text x="830" y="117" text-anchor="middle" fill="#e4e4e7">Adresse IP/UDP d’endpoint visible</text><path d="M830 136 V178 H500 V208" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9"/><rect x="298" y="208" width="404" height="77" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="236" text-anchor="middle" class="title" fill="#f4f4f5">Peer destinataire</text><text x="500" y="260" text-anchor="middle" fill="#e4e4e7">Authentifie, déchiffre puis valide la source intérieure</text><text x="500" y="325" text-anchor="middle" class="small" fill="#a1a1aa">Le tunnel n’efface pas les besoins de routage ni de filtrage aux extrémités.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Les équipements intermédiaires doivent transporter le paquet extérieur jusqu’à l’endpoint UDP. Le paquet IP intérieur est protégé cryptographiquement, mais l’adresse de l’endpoint et certaines caractéristiques de trafic restent observables.</p></div>

Méthode de diagnostic recommandée :

1. Confirmer que le handshake fonctionne et que les compteurs évoluent.
2. Comparer un ping de petite taille avec un test dont la taille est contrôlée.
3. Sous Linux, tester sans fragmentation IPv4 si le chemin le permet, par exemple `ping -M do -s 1372 <adresse>` ; le payload doit être ajusté au total des en-têtes et à la famille IP. Cette valeur n’est qu’un test, pas une MTU à copier.
4. Utiliser `tracepath` ou des captures pour chercher où les paquets disparaissent et vérifier si les messages ICMP nécessaires à PMTUD sont bloqués.
5. Réduire temporairement la MTU de `wg0` pour confirmer l’hypothèse, puis choisir une valeur adaptée et documentée. Ne laisse pas une valeur réduite au hasard si la performance en dépend.

Le MSS TCP peut aussi être ajusté par le pare-feu pour éviter que des segments trop grands soient émis dans un tunnel dont la MTU est plus faible, mais le clamp MSS ne résout pas les problèmes UDP, ICMP, QUIC ou toutes les formes de PMTUD. Il doit répondre à une contrainte observée.

### 1.6 NAT, endpoints dynamiques et roaming

WireGuard n’exige pas que l’endpoint d’un peer reste toujours identique. Lorsqu’un paquet authentifié arrive depuis une nouvelle adresse IP/port extérieur, l’implémentation peut apprendre le nouvel endpoint source pour ce peer. Cela permet les changements de réseau d’un ordinateur portable ou d’un téléphone. Ce mécanisme ne remplace pas la sécurité des clés : seuls les paquets authentifiés peuvent mettre à jour l’endpoint du peer concerné.

Le peer derrière NAT initie généralement les échanges vers un pair accessible publiquement. S’il doit recevoir des paquets après une période d’inactivité, le mapping de traduction peut avoir expiré. `PersistentKeepalive = 25` est une valeur souvent utilisée dans ce cas ; elle envoie périodiquement un paquet pour maintenir l’état. Ne l’active pas partout : si le peer n’a pas besoin de recevoir du trafic spontané derrière un état NAT, le maintien périodique augmente inutilement le trafic.

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .blue-text{fill:#93c5fd}.wg-visual svg .green-text{fill:#86efac}.wg-visual svg .amber-text{fill:#fcd34d}.wg-visual svg .red-text{fill:#fda4af}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.wg-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.wg-visual details p{margin:.6rem 0 0}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}.wg-visual a{color:#93c5fd}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 350" role="img" aria-label="Peer WireGuard derrière NAT : un client initie vers un endpoint public, le serveur apprend la source authentifiée et PersistentKeepalive maintient l’association NAT si nécessaire." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="348" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">NAT, endpoint dynamique et PersistentKeepalive</text><rect x="36" y="77" width="245" height="94" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="158" y="105" text-anchor="middle" class="title" fill="#f4f4f5">Peer mobile / NAT</text><text x="158" y="130" text-anchor="middle" fill="#e4e4e7">Adresse privée changeante</text><text x="158" y="151" text-anchor="middle" class="small" fill="#a1a1aa">Initiateur ou pair nomade</text><rect x="378" y="77" width="245" height="94" rx="12" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="500" y="105" text-anchor="middle" class="title" fill="#f4f4f5">NAT / pare-feu</text><text x="500" y="130" text-anchor="middle" fill="#e4e4e7">Mapping UDP temporaire</text><text x="500" y="151" text-anchor="middle" class="small" fill="#a1a1aa">État de retour nécessaire</text><rect x="719" y="77" width="245" height="94" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="841" y="105" text-anchor="middle" class="title" fill="#f4f4f5">Peer public</text><text x="841" y="130" text-anchor="middle" fill="#e4e4e7">Endpoint UDP connu</text><text x="841" y="151" text-anchor="middle" class="small" fill="#a1a1aa">Écoute sur le port configuré</text><path d="M281 111 H378" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><path d="M623 136 H719" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="329" cy="111" r="5" class="packet" fill="#60a5fa"/><circle cx="671" cy="136" r="5" class="packet delay-2" fill="#4ade80"/><rect x="123" y="220" width="754" height="75" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="247" text-anchor="middle" class="title" fill="#f4f4f5">PersistentKeepalive = 25 (uniquement si le scénario le justifie)</text><text x="500" y="272" text-anchor="middle" fill="#e4e4e7">Paquet périodique sortant pour maintenir l’état NAT, pas une sonde de santé complète</text><path d="M158 171 V195 H250 V220" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8"/><path d="M841 171 V195 H750 V220" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8"/><text x="500" y="326" text-anchor="middle" class="small" fill="#a1a1aa">WireGuard peut apprendre un nouvel endpoint après un paquet authentifié reçu du peer.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Le peer derrière NAT initie généralement vers le pair public. WireGuard peut mettre à jour l’endpoint après réception authentifiée. `PersistentKeepalive` est utile lorsqu’un mapping doit rester ouvert pour recevoir du trafic après une période d’inactivité ; il n’est pas nécessaire dans toutes les configurations.</p></div>

Ne confonds pas trois choses :

- **Endpoint configuré** : la destination initiale à laquelle un peer peut envoyer.
- **Endpoint appris** : la source extérieure du dernier trafic authentifié reçu.
- **Dernier handshake** : l’heure du dernier échange cryptographique observable ; il ne s’agit pas d’une session TCP permanente.

### 1.7 Clés, identité et cycle de vie

Une clé privée WireGuard reste secrète sur le système qui la possède. Elle ne doit pas être copiée dans une capture, un ticket d’incident, un dépôt Git ou un message. La clé publique est le moyen usuel d’identifier le peer à configurer sur l’autre extrémité. Utilise une identité cryptographique distincte par appareil ou par site lorsque c’est possible, afin de pouvoir révoquer un seul peer.

Le changement de clé statique est une opération de coordination : générer la nouvelle paire de clés, installer la clé publique correspondante sur l’autre extrémité, déployer la clé privée locale dans un stockage protégé, vérifier le handshake, puis supprimer l’ancienne autorisation selon le plan de migration. N’invalide pas simultanément toutes les clés lors d’une modification distante sans accès de secours.

WireGuard établit et renouvelle ses clés de session automatiquement selon son protocole ; les administrateurs n’ont généralement pas besoin de lancer manuellement un rekey comme dans certains autres VPN. Le cycle de vie opérationnel qu’ils doivent gérer porte surtout sur les clés statiques des appareils, l’ajout/retrait des peers, la rotation contrôlée et la sauvegarde sûre des configurations.

---

## 2. Configuration et pratique

### 2.1 Plan du laboratoire site-à-site

Le laboratoire utilise deux passerelles Linux : A possède un endpoint public de démonstration et B initie depuis un réseau potentiellement derrière NAT. Les plages publiques ci-dessous sont réservées à la documentation ; elles doivent être remplacées dans un environnement réel.

| Paramètre | Passerelle A | Passerelle B |
|---|---|---|
| Endpoint d’exemple | `198.51.100.10:51820` | Connexion sortante vers A |
| Adresse WireGuard | `10.200.0.1/24` | `10.200.0.2/24` |
| LAN local | `10.10.0.0/24` | `10.20.0.0/24` |
| Port UDP | Écoute UDP 51820 | Port source généralement dynamique |
| Préfixes distants utiles | `10.20.0.0/24` | `10.10.0.0/24` |

Avant la configuration, vérifie les paquets logiciels, les droits administrateur, la connectivité IP et l’accès console. L’UDP 51820 doit être autorisé vers A à la frontière publique et dans le pare-feu local s’il est actif. Les adresses publiques ci-dessus ne fonctionnent pas sur Internet : ce sont des adresses de documentation.

### 2.2 Préparer les clés proprement

Sur **chaque** machine, crée un fichier de clé privée avec des permissions restrictives. Ne réutilise pas une même clé privée sur deux machines.

```bash
sudo install -d -m 700 /etc/wireguard
sudo sh -c 'umask 077; wg genkey > /etc/wireguard/privatekey'
sudo sh -c 'wg pubkey < /etc/wireguard/privatekey > /etc/wireguard/publickey'
sudo chmod 600 /etc/wireguard/privatekey
sudo chmod 644 /etc/wireguard/publickey
sudo cat /etc/wireguard/publickey
```

La commande `cat` doit afficher uniquement la clé publique à communiquer au pair. Ne colle jamais le contenu de `privatekey` dans un rapport ou dans une conversation. Sur un vrai serveur, protège aussi les sauvegardes, les droits d’accès et les permissions du compte administrateur.

### 2.3 Configuration de la passerelle A

Le contenu suivant est un modèle. Remplace `<CLE_PRIVEE_A>` et `<CLE_PUBLIQUE_B>` par les valeurs générées localement. Ne laisse pas les chevrons dans le vrai fichier.

```ini
# /etc/wireguard/wg0.conf sur la passerelle A
[Interface]
Address = 10.200.0.1/24
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_A>

[Peer]
# Passerelle B
PublicKey = <CLE_PUBLIQUE_B>
AllowedIPs = 10.200.0.2/32, 10.20.0.0/24
```

A ne nécessite pas un `Endpoint` statique pour B si B se trouve derrière NAT et initie la communication. Après réception d’un paquet WireGuard authentifié, A peut apprendre l’endpoint réel de B. Les `AllowedIPs` côté A représentent l’adresse de tunnel de B et le LAN accessible derrière B.

### 2.4 Configuration de la passerelle B

```ini
# /etc/wireguard/wg0.conf sur la passerelle B
[Interface]
Address = 10.200.0.2/24
PrivateKey = <CLE_PRIVEE_B>

[Peer]
# Passerelle A, joignable publiquement
PublicKey = <CLE_PUBLIQUE_A>
Endpoint = 198.51.100.10:51820
AllowedIPs = 10.200.0.1/32, 10.10.0.0/24
PersistentKeepalive = 25
```

`PersistentKeepalive = 25` est ici un choix de laboratoire car B peut être derrière NAT et doit pouvoir recevoir du trafic A après une période d’inactivité. Sur un peer qui n’a pas cette contrainte, retire ce paramètre. Si le LAN de B doit rester accessible uniquement au trafic initié depuis B, la politique de pare-feu doit le dire explicitement ; le tunnel ne remplace pas cette politique.

Démarre et vérifie l’interface sur chaque machine :

```bash
sudo chmod 600 /etc/wireguard/wg0.conf
sudo wg-quick up wg0
sudo wg show wg0
ip address show dev wg0
ip route show
```

Pour arrêter le tunnel pendant un test planifié :

```bash
sudo wg-quick down wg0
```

> **Danger :** ne redémarre pas un tunnel sur une machine distante à travers ce même tunnel sans prévoir une console ou une fenêtre de retour arrière. Une route par défaut ou une règle de pare-feu incorrecte peut te couper l’accès administratif.

### 2.5 Activer le forwarding IP si la machine route entre deux réseaux

Une passerelle qui doit transférer les paquets entre son LAN et `wg0` a généralement besoin du forwarding IPv4 ; IPv6 doit être traité séparément si les réseaux IPv6 transitent réellement par elle.

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Pour le rendre persistant, crée une configuration adaptée à la distribution, par exemple dans `/etc/sysctl.d/` et vérifie son application au démarrage. N’active pas le forwarding sur un poste qui ne doit pas fonctionner comme routeur.

Le pare-feu doit autoriser les flux nécessaires dans la chaîne de transit (*FORWARD*) et, sur certaines topologies, filtrer l’accès vers ou depuis l’interface WireGuard. Les règles exactes dépendent de nftables, iptables, firewalld ou ufw et de la politique du site. N’applique pas une règle d’acceptation générale de tout trafic provenant de `wg0` sur une machine multi-usage. Préfère les sous-réseaux, ports et directions requis.

### 2.6 Routes et préfixes

Quand `wg-quick` est utilisé avec son comportement par défaut, il ajoute habituellement les routes correspondant aux `AllowedIPs`. Vérifie les résultats au lieu de déduire la route de la seule configuration :

```bash
ip route get 10.20.0.10
ip route get 10.10.0.10
ip rule show
ip route show table all
wg show wg0 allowed-ips
```

Sur A, une destination comme `10.20.0.10` doit normalement être sélectionnée via `wg0`. Sur B, `10.10.0.10` doit être sélectionnée via `wg0`. Si la route pointe vers une autre interface, inspecte les tables, métriques, préfixes qui se chevauchent et éventuelles règles de routage par politique.

### 2.7 Vérifier handshake, compteurs et connectivité

```bash
sudo wg show wg0
sudo wg show wg0 latest-handshakes
sudo wg show wg0 transfer
ip -s link show dev wg0
ping -I wg0 10.200.0.1
ping -I wg0 10.200.0.2
```

Le ping des adresses de tunnel est un premier test, pas le test de bout en bout final. Ensuite, teste une machine du LAN A vers une machine du LAN B avec une source explicite lorsque c’est utile. Vérifie la route de retour sur la destination et le filtrage de chaque côté. Un ping peut être bloqué par un pare-feu même si TCP/HTTPS fonctionne ; à l’inverse, un ping réussi ne prouve pas qu’un service applicatif est disponible.

Pour observer le transport extérieur pendant la négociation :

```bash
sudo tcpdump -ni any udp port 51820
```

Cette capture peut montrer les datagrammes extérieurs, mais pas le contenu IP intérieur chiffré. Elle ne doit pas contenir les clés privées. Protège les PCAP, car les métadonnées, adresses et heures de connexion restent sensibles.

---

## 3. Scénarios intermédiaires

### 3.1 Ajouter un troisième peer au concentrateur

Pour ajouter un site C, génère une clé distincte et attribue-lui une adresse de tunnel unique, par exemple `10.200.0.4/32`, ainsi qu’un LAN distinct `10.30.0.0/24`. Sur le hub, ajoute un bloc `[Peer]` séparé avec sa clé publique et :

```ini
AllowedIPs = 10.200.0.4/32, 10.30.0.0/24
```

Sur C, l’autre côté configure la clé publique du hub, son endpoint public et les préfixes du tunnel et des LAN auxquels il doit accéder. Si C est derrière NAT, il peut initier vers le hub et n’a pas nécessairement besoin que le hub connaisse à l’avance son endpoint.

Pour que A et B puissent communiquer avec le LAN de C, les deux doivent avoir une route vers `10.30.0.0/24` pointant vers le hub, et le hub doit autoriser le transfert entre les peers. La configuration de WireGuard ne propage pas automatiquement les routes sur tous les spokes. Il faut annoncer/configurer le plan de routage séparément ou déployer un système d’automatisation qui maintient les routes de façon cohérente.

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .blue-text{fill:#93c5fd}.wg-visual svg .green-text{fill:#86efac}.wg-visual svg .amber-text{fill:#fcd34d}.wg-visual svg .red-text{fill:#fda4af}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.wg-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.wg-visual details p{margin:.6rem 0 0}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}.wg-visual a{color:#93c5fd}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 390" role="img" aria-label="Chemin de trafic intersite : hôte source, routeur, forwarding, pare-feu, interface WireGuard, tunnel puis routeur et hôte distant. Le succès nécessite chaque étape." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="388" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">Un tunnel actif ne garantit pas la connectivité LAN-à-LAN</text><rect x="24" y="93" width="150" height="80" rx="10" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="99" y="121" text-anchor="middle" class="title" fill="#f4f4f5">Hôte A</text><text x="99" y="145" text-anchor="middle" fill="#e4e4e7">10.10.0.10</text><rect x="214" y="93" width="150" height="80" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="289" y="121" text-anchor="middle" class="title" fill="#f4f4f5">Route / FIB</text><text x="289" y="145" text-anchor="middle" class="small" fill="#a1a1aa">Préfixe distant ?</text><rect x="404" y="93" width="180" height="80" rx="10" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="494" y="121" text-anchor="middle" class="title" fill="#f4f4f5">Firewall / forward</text><text x="494" y="145" text-anchor="middle" class="small" fill="#a1a1aa">FORWARD + NAT</text><rect x="624" y="93" width="150" height="80" rx="10" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="699" y="121" text-anchor="middle" class="title" fill="#f4f4f5">Interface wg0</text><text x="699" y="145" text-anchor="middle" fill="#e4e4e7">Peer sélectionné</text><rect x="814" y="93" width="162" height="80" rx="10" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="895" y="121" text-anchor="middle" class="title" fill="#f4f4f5">Hôte B</text><text x="895" y="145" text-anchor="middle" fill="#e4e4e7">10.20.0.10</text><path d="M174 133 H214" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><path d="M364 133 H404" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9"/><path d="M584 133 H624" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><path d="M774 133 H814" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><circle cx="194" cy="133" r="5" class="packet" fill="#60a5fa"/><circle cx="384" cy="133" r="5" class="packet delay-1" fill="#fbbf24"/><circle cx="604" cy="133" r="5" class="packet delay-2" fill="#4ade80"/><circle cx="794" cy="133" r="5" class="packet delay-3" fill="#4ade80"/><rect x="94" y="231" width="812" height="95" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="260" text-anchor="middle" class="title" fill="#f4f4f5">Vérifications à chaque frontière</text><text x="500" y="286" text-anchor="middle" fill="#e4e4e7">Route aller · AllowedIPs · forwarding · filtre · route retour · source autorisée</text><text x="500" y="308" text-anchor="middle" class="small" fill="#a1a1aa">Le tunnel chiffré n’ajoute pas automatiquement le forwarding IP sur Linux.</text><text x="500" y="362" text-anchor="middle" class="small" fill="#a1a1aa">Tester dans les deux sens avec des sources et destinations explicites.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Un handshake confirme l’échange cryptographique avec un pair ; il ne confirme ni les routes des LAN, ni les règles de forwarding, ni le chemin de retour. Diagnostique chaque frontière séparément.</p></div>

### 3.2 Site-à-site et route retour

Un problème fréquent est un paquet qui atteint le LAN distant, mais la réponse n’arrive pas. La route aller peut être correcte tandis que le routeur de destination ignore le réseau source VPN ou renvoie la réponse par la passerelle Internet normale. Vérifie :

- la route de retour vers le réseau VPN ou LAN distant sur la passerelle de destination ;
- l’adresse source observée par l’hôte distant ;
- les règles de pare-feu locales et de transit ;
- toute traduction NAT qui modifie la source ;
- la correspondance des préfixes `AllowedIPs` sur les deux extrémités.

Évite d’ajouter du masquerading sur le trafic interne par réflexe. Le routage sans NAT conserve les adresses sources et facilite l’audit. Le NAT peut être utile si le réseau distant n’a pas de route retour ou si les préfixes se chevauchent, mais il doit être documenté et limité au flux concerné.

### 3.3 Full tunnel sur Linux : contrôler les routes par défaut

Pour un client full tunnel, un bloc peer peut utiliser :

```ini
AllowedIPs = 0.0.0.0/0, ::/0
```

Cela indique que toutes les destinations IPv4 et IPv6 devraient être associées au peer. Avec `wg-quick`, le cas des routes par défaut est traité spécialement, notamment à l’aide de règles de routage et d’un `fwmark` lorsque nécessaire. C’est préférable à l’ajout manuel et aveugle d’une route `default dev wg0`, qui pourrait aussi envoyer l’endpoint WireGuard dans le tunnel et casser le transport.

Valide après activation :

```bash
ip route show
ip rule show
ip route get <ADRESSE_IP_DE_L_ENDPOINT>
ip -6 route show
```

L’endpoint doit rester joignable via le chemin extérieur approprié. Si le DNS du système change automatiquement, vérifie aussi que le résolveur configuré est accessible et qu’il n’existe pas de fuite de résolution non souhaitée. Le comportement de DNS dans `wg-quick` dépend de la prise en charge de `resolvconf` ou de l’intégration fournie par la distribution ; les environnements NetworkManager/systemd-resolved peuvent utiliser d’autres mécanismes.

### 3.4 IPv6 dans un tunnel

Pour transporter IPv6, chaque interface doit recevoir une adresse IPv6 pertinente, les `AllowedIPs` doivent contenir les préfixes IPv6 attendus et le système doit avoir des routes et règles de pare-feu IPv6 compatibles. Ne suppose pas que configurer uniquement une adresse IPv4 neutralise IPv6 sur une machine à double pile.

Dans un site-à-site, évite de réutiliser le même préfixe IPv6 sur plusieurs sites sans design spécifique. Vérifie l’ICMPv6 nécessaire au fonctionnement normal de IPv6 et ne le bloque pas globalement. Les règles IPv6 et IPv4 doivent être auditées séparément, y compris les règles de transit et les conditions d’accès à l’administration.

### 3.5 Plusieurs routes, plusieurs peers et préfixes qui se chevauchent

Un même peer peut recevoir plusieurs préfixes séparés par des virgules. Dans une architecture multi-peer, les routes plus spécifiques peuvent distinguer des destinations, mais deux peers ne doivent pas revendiquer le même préfixe de façon ambiguë. Le *longest-prefix match* aide à sélectionner une route plus spécifique, mais ne résout pas la confusion d’adressage ni la politique d’identité.

Si tu dois connecter deux organisations qui utilisent le même réseau privé, considère en priorité une renumérotation ou un plan NAT limité. L’usage de `AllowedIPs = 0.0.0.0/0` sur plusieurs peers n’est pas une solution à une collision de réseaux : cela modifie fortement la sélection du trafic et peut rendre le comportement inattendu.

### 3.6 Routage par politique

Les environnements avancés peuvent nécessiter que seuls certains flux — par exemple, le sous-réseau de gestion ou le trafic d’une application — passent par le VPN. Linux fournit `ip rule`, plusieurs tables et des marques de paquets. `wg-quick` permet `Table = off` ou le choix d’une table, mais dès qu’un design fait intervenir des règles manuelles, il faut une convention claire : quelle table reçoit les routes, qui pose le *fwmark*, quelle priorité possède chaque règle et comment supprimer les règles à l’arrêt.

Avant une configuration de routage par politique :

1. Dessine les chemins attendus pour les flux autorisés et ceux qui doivent rester locaux.
2. Inspecte l’état existant avec `ip rule show`, `ip route show table all` et `ip route get`.
3. Ajoute un nombre minimal de règles et vérifie le chemin de l’endpoint public.
4. Teste l’activation et la désactivation du tunnel ; vérifie que les règles temporaires sont retirées.
5. Documente les priorités, marques et tables dans le runbook, et prévois un retour arrière.

> **Danger :** `PostUp` et `PreDown` dans `wg-quick` exécutent des commandes shell. Ce sont des outils puissants, pas des options de configuration anodines. Vérifie chaque commande, son idempotence, son effet au redémarrage et sa suppression à l’arrêt ; ne copie pas un script provenant d’un tiers sans audit.

---

## 4. Dépannage structuré

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 455" role="img" aria-label="Arbre de diagnostic WireGuard. Étapes centrales : endpoint UDP, handshake récent, AllowedIPs, routes et forwarding, enfin MTU/DNS/application. Les branches latérales indiquent les causes à examiner." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="453" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">Arbre de diagnostic — trouver la première couche en échec</text><rect x="285" y="53" width="430" height="52" rx="10" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="500" y="84" text-anchor="middle" class="title" fill="#f4f4f5">1. Endpoint UDP atteint ?</text><path d="M500 105 V130" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><rect x="285" y="130" width="430" height="52" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="161" text-anchor="middle" class="title" fill="#f4f4f5">2. Handshake récent ?</text><path d="M500 182 V207" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><rect x="285" y="207" width="430" height="52" rx="10" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="500" y="238" text-anchor="middle" class="title" fill="#f4f4f5">3. AllowedIPs / peer corrects ?</text><path d="M500 259 V284" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9"/><rect x="285" y="284" width="430" height="52" rx="10" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="500" y="315" text-anchor="middle" class="title" fill="#f4f4f5">4. Route, retour et forwarding OK ?</text><path d="M500 336 V361" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8"/><rect x="285" y="361" width="430" height="52" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="392" text-anchor="middle" class="title" fill="#f4f4f5">5. MTU, DNS et application</text><rect x="24" y="130" width="220" height="52" rx="10" class="node-red" fill="#30151b" stroke="#fb7185"/><text x="134" y="152" text-anchor="middle" class="title" fill="#f4f4f5">Pas de handshake</text><text x="134" y="171" text-anchor="middle" class="small" fill="#fda4af">Endpoint · UDP · clés</text><path d="M285 156 H244" class="flow flow-red" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 9"/><rect x="756" y="284" width="220" height="52" rx="10" class="node-red" fill="#30151b" stroke="#fb7185"/><text x="866" y="306" text-anchor="middle" class="title" fill="#f4f4f5">Handshake OK</text><text x="866" y="325" text-anchor="middle" class="small" fill="#fda4af">LAN injoignable</text><path d="M715 310 H756" class="flow flow-red" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 9"/><text x="500" y="438" text-anchor="middle" class="small" fill="#a1a1aa">Comparer captures, compteurs et routes ; ne modifier qu’une variable à la fois.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Partir de l’observation : écoute UDP, dernier handshake, compteurs, correspondance du peer, route réellement choisie, forwarding, MTU puis DNS/applications. Un handshake seul ne valide pas tout le chemin.</p></div>


### 4.1 Symptôme : aucun handshake récent

Un handshake qui ne se met pas à jour peut résulter d’un endpoint incorrect, d’un port UDP bloqué, d’une clé publique distante erronée, d’une absence de trafic déclencheur ou d’un pare-feu qui ne permet pas les réponses. Procède par preuves :

1. Vérifie `wg show wg0` et confirme que le peer est bien présent.
2. Confirme que l’endpoint configuré est correct et que le serveur écoute sur le port attendu.
3. Lance une capture UDP sur l’interface extérieure des deux côtés si possible.
4. Vérifie le pare-feu local et les règles de sécurité chez l’hébergeur ou l’opérateur.
5. Compare les clés publiques échangées sans jamais afficher ni partager les clés privées.
6. Génère un trafic de test ciblé pour déclencher une tentative d’échange et observe les compteurs.

Un pair qui n’a encore échangé aucun trafic peut ne pas afficher de handshake récent : cela ne signifie pas automatiquement un incident. En revanche, si du trafic doit passer et que rien ne part vers l’endpoint, examine d’abord la route vers la destination et les `AllowedIPs`.

### 4.2 Symptôme : handshake présent, LAN inaccessible

Dans ce cas, la couche cryptographique fonctionne probablement, mais il peut manquer une route, le forwarding, une règle de transit ou le chemin retour. Utilise :

```bash
wg show wg0
ip route get 10.20.0.10
ip route get 10.10.0.10
ip -s link show dev wg0
sysctl net.ipv4.ip_forward
```

Puis teste depuis la passerelle elle-même, ensuite depuis un hôte du LAN. Si le tunnel fonctionne depuis le routeur mais pas depuis un hôte, recherche le forwarding ou le pare-feu. Si le paquet quitte un LAN mais ne revient pas, vérifie la route de retour et le filtrage côté destination.

### 4.3 Symptôme : petits paquets OK, gros transferts bloqués

C’est compatible avec un problème MTU/PMTUD ou un filtrage ICMP, mais il faut le démontrer. Compare des tests de taille différente, observe les compteurs et teste une réduction temporaire de MTU sur l’interface VPN. Si le test change le résultat, choisis une MTU adaptée au chemin et examine les messages nécessaires à PMTUD. Un simple clamp MSS peut aider TCP mais ne règle pas toutes les applications.

### 4.4 Symptôme : tunnel actif, résolution DNS impossible

Teste d’abord une adresse IP de destination. Si l’IP est joignable mais pas le nom, examine le résolveur choisi, les routes vers celui-ci, les suffixes de recherche et la politique de full tunnel/split tunnel. Si un DNS interne doit être utilisé dans le VPN, assure-toi que ce serveur est dans les préfixes acheminés au peer et que son pare-feu autorise UDP/TCP 53 depuis les sources concernées.

Ne conclus pas que DNS est en panne si l’adresse IP elle-même n’est pas joignable. Il peut s’agir d’un incident de routage plus bas dans la pile.

### 4.5 Symptôme : le VPN fonctionne puis échoue après inactivité

Un peer derrière NAT peut perdre son mapping UDP après une période sans trafic. Si ce peer doit être joignable depuis l’autre extrémité sans échange initié par lui, teste un `PersistentKeepalive` raisonnable — souvent 25 secondes — puis observe si le comportement s’améliore. Laisse-le désactivé si le scénario n’en a pas besoin. Vérifie aussi si l’adresse publique du peer change et si le dernier endpoint appris est cohérent avec le réseau courant.

### 4.6 Symptôme : trafic envoyé au mauvais peer

Examine les `AllowedIPs` pour trouver des préfixes en double, des plages trop larges ou une route plus spécifique inattendue. `wg show wg0 allowed-ips` affiche l’association entre peers et préfixes. `ip route get <destination>` révèle ensuite la route système choisie. Les deux observations doivent être cohérentes : une route peut diriger vers `wg0`, mais les `AllowedIPs` peuvent encore ne pas associer le préfixe à un peer valide.

### 4.7 Capture sans exposer de secrets

```bash
sudo tcpdump -ni <interface-externe> udp port 51820
sudo tcpdump -ni wg0 host 10.20.0.10
wg show wg0 transfer
```

La première capture observe le transport extérieur ; la deuxième, sur `wg0`, peut voir le trafic IP intérieur en clair sur l’hôte local. Les captures de l’interface VPN peuvent donc contenir des données applicatives sensibles. Réduis la durée et les filtres, protège le fichier PCAP et supprime-le conformément à la politique de conservation.

---

## 5. Sécurité et exploitation

### 5.1 Gestion des clés et accès d’administration

<div class="wg-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1a1aa}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgFlow 1.25s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .delay-1{animation-delay:.35s}.wg-visual svg .delay-2{animation-delay:.7s}.wg-visual svg .delay-3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}@keyframes wgFlow{to{stroke-dashoffset:-32}}@keyframes wgPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.wg-visual{padding:6px}.wg-visual svg text{font-size:18px}.wg-visual svg .small{font-size:15px}.wg-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 310" role="img" aria-label="Rotation sûre d'une clé WireGuard en quatre étapes : préparer une nouvelle clé, autoriser la nouvelle clé publique sur le pair distant, vérifier le handshake, puis révoquer l'ancienne clé." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="998" height="308" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title" fill="#f4f4f5">Rotation de clé — préserver une voie de retour</text><rect x="26" y="75" width="210" height="105" rx="11" class="node-blue" fill="#10243b" stroke="#60a5fa"/><text x="131" y="103" text-anchor="middle" class="title" fill="#f4f4f5">1. Préparer</text><text x="131" y="129" text-anchor="middle" fill="#e4e4e7">Nouvelle paire</text><text x="131" y="151" text-anchor="middle" class="small" fill="#a1a1aa">Privée protégée</text><rect x="270" y="75" width="210" height="105" rx="11" class="node-amber" fill="#2b2110" stroke="#fbbf24"/><text x="375" y="103" text-anchor="middle" class="title" fill="#f4f4f5">2. Autoriser</text><text x="375" y="129" text-anchor="middle" fill="#e4e4e7">Installer la clé publique</text><text x="375" y="151" text-anchor="middle" class="small" fill="#a1a1aa">Sur le pair distant</text><rect x="514" y="75" width="210" height="105" rx="11" class="node-green" fill="#0d2a20" stroke="#4ade80"/><text x="619" y="103" text-anchor="middle" class="title" fill="#f4f4f5">3. Valider</text><text x="619" y="129" text-anchor="middle" fill="#e4e4e7">Handshake et trafic</text><text x="619" y="151" text-anchor="middle" class="small" fill="#a1a1aa">Test aller/retour</text><rect x="758" y="75" width="216" height="105" rx="11" class="node-red" fill="#30151b" stroke="#fb7185"/><text x="866" y="103" text-anchor="middle" class="title" fill="#f4f4f5">4. Révoquer</text><text x="866" y="129" text-anchor="middle" fill="#e4e4e7">Retirer l’ancienne clé</text><text x="866" y="151" text-anchor="middle" class="small" fill="#a1a1aa">Après validation</text><path d="M236 127 H270" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9"/><path d="M480 127 H514" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9"/><path d="M724 127 H758" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9"/><circle cx="253" cy="127" r="5" class="packet" fill="#60a5fa"/><circle cx="497" cy="127" r="5" class="packet delay-1" fill="#4ade80"/><circle cx="741" cy="127" r="5" class="packet delay-2" fill="#fbbf24"/><rect x="122" y="218" width="756" height="55" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="241" text-anchor="middle" class="title" fill="#f4f4f5">Ne jamais envoyer une clé privée à l’autre extrémité</text><text x="500" y="261" text-anchor="middle" class="small" fill="#a1a1aa">Sauvegarde sûre, fenêtre de changement et accès de secours avant la bascule.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Une rotation sûre est un changement coordonné de configuration, pas l’envoi de la clé privée au peer distant. Prépare la nouvelle identité, autorise la clé publique, valide le handshake et les flux, puis retire l’ancienne clé selon le plan de bascule.</p></div>

- Génère une paire de clés par appareil ou passerelle lorsque l’architecture le permet.
- Limite les permissions du fichier contenant `PrivateKey` ; les comptes non administrateurs ne doivent pas le lire.
- N’insère jamais de clé privée dans un cours, un dépôt Git, une image de conteneur, un ticket ou une commande enregistrée dans l’historique shell.
- Lorsqu’un appareil est perdu ou un membre part, retire sa clé publique de la configuration des pairs autorisés et déploie la modification sur les nœuds concernés.
- Garde une procédure d’urgence pour récupérer les configurations et remplacer une clé compromise.
- Ne confonds pas la capacité d’un peer à joindre une adresse avec son autorisation à utiliser tous les services de cette adresse.

### 5.2 Filtrage et moindre privilège

Le modèle WireGuard sait quel peer a protégé un paquet et quels préfixes lui sont associés, mais il ne constitue pas à lui seul une politique fine d’application. Des règles de pare-feu doivent décider si le peer peut joindre SSH, DNS, une base de données, un service de sauvegarde ou seulement un sous-ensemble du LAN.

Un plan d’autorisation utile précise :

| Source | Destination | Services autorisés | Exemple de politique |
|---|---|---|---|
| Poste d’administration VPN | Hôtes de gestion | SSH/HTTPS d’administration | Autoriser depuis un groupe d’adresses géré |
| Spoke A | LAN du hub | Services métiers nécessaires | Autoriser uniquement les ports requis |
| Spoke A | LAN du spoke B | Aucun par défaut, sauf besoin explicite | Interdire le transit entre spokes non autorisés |
| Réseau extérieur | Port UDP WireGuard | Uniquement port d’écoute sur endpoint public | Autoriser le transport, pas les services internes |

Le choix exact dépend des règles de l’organisation. Les commandes `PostUp`/`PostDown` pour créer des règles doivent être conçues comme du code d’infrastructure, revues et testées avant la production.

### 5.3 Secrets, journaux et métadonnées

WireGuard réduit les éléments à gérer, mais une exploitation sûre nécessite toujours des journaux pertinents. Enregistre les changements de configuration, l’ajout/retrait de clés publiques, les redémarrages du service, les erreurs de routage et les mesures des compteurs. Évite de journaliser les clés privées et protège les captures de paquets. Les endpoints, les heures de handshake et les volumes peuvent être sensibles même si le contenu est chiffré.

### 5.4 Mise à jour et compatibilité

Les commandes et la prise en charge de WireGuard varient selon le noyau, la version des utilitaires, la distribution et les mécanismes de gestion réseau. Vérifie les versions de `wg`, `wg-quick`, du noyau et les options reconnues avant de déployer une fonctionnalité avancée. Sur les postes gérés par NetworkManager ou une autre couche de gestion, évite d’avoir plusieurs outils concurrents qui modifient simultanément les routes et DNS.

> **Astuce :** dans un changement réseau, la documentation doit décrire l’état attendu (`wg show`, routes, règles, DNS), pas seulement les commandes tapées. Cette description rend possible une validation reproductible après une mise à jour ou un remplacement de serveur.

### 5.5 Haute disponibilité et limites d’architecture

WireGuard n’offre pas un cluster avec synchronisation automatique des états entre deux serveurs comme certains produits VPN spécialisés. Une architecture redondante requiert généralement des endpoints alternatifs, un mécanisme de bascule, un routage cohérent, un plan de clés sur les deux côtés et des tests de reprise. Il faut décider si le peer apprend un nouvel endpoint, comment le DNS ou le routage externe présente la passerelle active et quelle interruption est acceptable.

Sur un hub qui héberge de nombreux peers, la perte du hub affecte potentiellement tous les spokes. Deux hubs peuvent réduire ce risque, mais chaque peer et chaque LAN doivent posséder un plan clair de routes primaires/secondaires. Ne distribue pas une configuration à plusieurs hubs sans réfléchir aux préfixes, aux destinations qui peuvent être annoncées par les deux peers et à l’asymétrie de retour.

---

## 6. Laboratoires guidés

### Laboratoire A — site-à-site simple

**Objectif :** établir la connectivité entre `10.10.0.0/24` et `10.20.0.0/24` avec `10.200.0.1` et `10.200.0.2` comme adresses de tunnel.

1. Génère une paire de clés distincte sur chaque passerelle.
2. Installe les configurations de A et B des sections 2.3 et 2.4.
3. Autorise UDP 51820 vers A et active le forwarding IPv4 uniquement si les machines doivent router les LAN.
4. Lance `wg-quick up wg0` et vérifie le handshake.
5. Contrôle les routes pour une adresse d’hôte de chaque LAN.
6. Vérifie la route retour et le pare-feu de transit.
7. Teste ping puis un service TCP de laboratoire depuis un hôte de chaque LAN.
8. Note les compteurs avant et après le test et l’heure du dernier handshake.

**Critères de réussite :** clés privées non exposées, peers uniques, handshake valide, routes aller/retour correctes, firewall limité aux flux nécessaires, test applicatif concluants dans les deux sens selon la politique retenue.

### Laboratoire B — identifier une erreur AllowedIPs

Introduis volontairement dans un environnement de test une plage distante incorrecte. Observe la route choisie par `ip route get`, puis inspecte `wg show wg0 allowed-ips`. Explique la différence entre une route de système qui mène à `wg0` et l’association du préfixe à un peer dans la table WireGuard. Corrige un seul élément puis répète le test.

**Question :** pourquoi un handshake réussi n’assure-t-il pas que le paquet à destination du LAN sera chiffré pour le peer attendu ?

### Laboratoire C — gros transferts et MTU

Compare un ping simple, un ping avec taille plus grande (si ta plateforme le permet) et un transfert HTTPS/TCP de laboratoire. Observe les compteurs et la capture. Si une réduction temporaire de MTU rétablit les transferts, note la valeur testée, la famille IP extérieure et les indices PMTUD disponibles. Rétablis ensuite la configuration de départ, puis applique un réglage justifié et revalide.

### Laboratoire D — peer derrière NAT

Place un client derrière une box NAT ou simule une inactivité. Vérifie le fonctionnement au début, attends l’expiration éventuelle de l’état NAT et teste à nouveau. Ajoute `PersistentKeepalive = 25` uniquement sur le peer qui en a besoin, observe la différence et explique pourquoi cette option ne remplace ni un test applicatif ni la supervision.

---

## 7. Points à retenir

- WireGuard identifie chaque peer par sa clé publique, mais les routes, les règles de pare-feu et les services restent des éléments séparés.
- `AllowedIPs` participe à la sélection du peer sortant et à la validation des sources intérieures reçues.
- `wg-quick` ajoute généralement les routes déduites de `AllowedIPs`, mais les configurations avancées peuvent désactiver ou remplacer ce comportement.
- Dans un hub-and-spoke, les préfixes associés aux peers doivent être uniques et les spokes ne découvrent pas automatiquement les routes des autres sites.
- Un handshake récent prouve une communication cryptographique récente ; il ne garantit pas la connectivité applicative.
- Le full tunnel implique d’étudier IPv4, IPv6, DNS, route de l’endpoint, kill switch et chemins de gestion.
- `PersistentKeepalive` est facultatif et particulièrement utile pour certains peers derrière NAT qui doivent rester joignables après inactivité.
- MTU et PMTUD peuvent expliquer des pannes qui n’affectent que les gros paquets ou certaines applications.
- Une clé par appareil, des permissions restrictives, la rotation planifiée et la révocation rapide limitent l’impact d’un appareil compromis.
- Toute modification à distance des routes ou règles de pare-feu nécessite un accès de secours et un plan de retour arrière.

## 8. Exercices corrigés

### Exercice 1 — Choix du peer

**Énoncé :** sur le hub, un peer a `AllowedIPs = 10.200.0.2/32, 10.20.0.0/24`. À quelle machine associes-tu la destination `10.20.0.50` ?

**Corrigé :** à ce peer, si aucun autre préfixe plus spécifique ou design de routage ne détourne la destination. Le `10.200.0.2/32` correspond à l’adresse de tunnel du peer ; `10.20.0.0/24` correspond à son LAN.

### Exercice 2 — Handshake récent, ping LAN échoué

**Énoncé :** le handshake se met à jour, les compteurs augmentent mais `10.20.0.10` reste injoignable depuis `10.10.0.10`. Quelles couches vérifies-tu ?

**Corrigé :** route A vers le LAN B, `AllowedIPs` des deux pairs, forwarding IPv4, règles de transit, route retour sur B et sur l’hôte de destination, règles hôte locales et éventuellement le filtrage ICMP. Le handshake ne valide pas le chemin des sous-réseaux.

### Exercice 3 — MTU

**Énoncé :** les petits pings passent mais un téléchargement HTTPS se bloque. Une MTU WireGuard réglée plus bas semble réparer le problème. Quelle est la suite correcte ?

**Corrigé :** mesurer davantage, observer les paquets et les éventuels messages ICMP/PMTUD, confirmer l’effet dans les deux directions puis choisir une valeur compatible avec le vrai chemin. Ne pas retenir une MTU basse sans documenter l’impact et le pourquoi.

### Exercice 4 — Full tunnel

**Énoncé :** après avoir mis `AllowedIPs = 0.0.0.0/0, ::/0`, le tunnel s’établit mais le client perd l’accès Internet ou ne peut plus joindre l’endpoint. Quelles vérifications sont prioritaires ?

**Corrigé :** `ip rule show`, tables de routage IPv4/IPv6, traitement spécial des routes par défaut par `wg-quick`, route de l’endpoint public, DNS, firewall/killswitch et connectivité de la passerelle VPN vers Internet. Ne pas ajouter une nouvelle route par défaut avant de comprendre la route actuelle.

### Exercice 5 — NAT et keepalive

**Énoncé :** un peer nomade peut établir le tunnel mais le hub ne peut plus lui envoyer de trafic après une période d’inactivité.

**Corrigé :** regarder l’endpoint actuellement appris, le dernier handshake et la politique NAT/firewall. Si le peer se trouve derrière un mapping UDP qui expire et qu’il doit recevoir du trafic initié par le hub, un `PersistentKeepalive` modéré peut maintenir l’état. Il ne dispense pas de tester la connectivité et le pare-feu.

### Exercice 6 — Préfixes qui se chevauchent

**Énoncé :** deux sites distants utilisent tous les deux `192.168.1.0/24`. Pourquoi les ajouter tels quels au hub ne suffit-il pas ?

**Corrigé :** le hub ne peut pas choisir un site unique pour la même destination au seul moyen de la route ; les préfixes sont ambigus. Il faut renuméroter si possible, ou concevoir une translation/segmentation explicitement, avec des routes et règles de filtrage cohérentes.

## 9. Glossaire

| Terme | Définition |
|---|---|
| Peer | Participant WireGuard identifié par une clé publique. |
| Endpoint | Adresse extérieure IP/port vers laquelle le peer envoie des datagrammes WireGuard. |
| Cryptokey routing | Association des préfixes IP et des clés publiques qui détermine le peer choisi et les sources admises. |
| AllowedIPs | Liste de préfixes associés à un peer et utilisés par la sélection/validation du trafic intérieur. |
| Full tunnel | Politique qui envoie la route par défaut à travers le VPN. |
| Split tunnel | Politique qui envoie uniquement certains préfixes dans le VPN. |
| PersistentKeepalive | Paquet périodique optionnel pour garder un état NAT/firewall actif. |
| MTU | Taille maximale d’un paquet de niveau liaison accepté sans fragmentation au niveau concerné. |
| PMTUD | Découverte de la MTU effective le long du chemin. |
| Kill switch | Politique qui bloque les flux hors du tunnel lorsque le VPN ne doit pas être contourné. |

## 10. Références et lectures complémentaires

- WireGuard — **Quick Start**, configuration, clés, endpoints et PersistentKeepalive : https://www.wireguard.com/quickstart/
- WireGuard — documentation générale et architecture : https://www.wireguard.com/
- `wg-quick(8)` — gestion de l’interface, routes, DNS, MTU, Table et hooks : https://man7.org/linux/man-pages/man8/wg-quick.8.html
- Dépôt officiel `wireguard-tools` — implémentation de `wg` et `wg-quick` : https://git.zx2c4.com/wireguard-tools/
- Noise Protocol Framework — base conceptuelle du handshake utilisé par WireGuard : https://noiseprotocol.org/noise.html
- Linux `ip-route(8)` et `ip-rule(8)` — routage et routage par politique : https://man7.org/linux/man-pages/man8/ip-route.8.html et https://man7.org/linux/man-pages/man8/ip-rule.8.html

---

> **Astuce :** avant de valider une architecture WireGuard, écris cinq éléments sur une seule fiche : identité de chaque peer, `AllowedIPs`, routes système, règles de forwarding et chemin retour. Si ces cinq éléments sont cohérents et observables, le diagnostic et la maintenance deviennent bien plus simples.
