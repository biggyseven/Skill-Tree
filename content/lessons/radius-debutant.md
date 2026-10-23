<style>.radius-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.radius-visual *{box-sizing:border-box}.radius-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.radius-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.radius-visual svg .small{font-size:12px;fill:#a1a1aa}.radius-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.radius-visual svg .accent-blue{fill:#93c5fd}.radius-visual svg .accent-green{fill:#86efac}.radius-visual svg .accent-amber{fill:#fcd34d}.radius-visual svg .accent-red{fill:#fda4af}.radius-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.radius-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.radius-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.radius-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.radius-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.radius-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:radiusFlow 0.95s linear infinite;will-change:stroke-dashoffset}.radius-visual svg .flow-blue{stroke:#60a5fa}.radius-visual svg .flow-green{stroke:#4ade80}.radius-visual svg .flow-amber{stroke:#fbbf24}.radius-visual svg .flow-red{stroke:#fb7185}.radius-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.radius-visual svg .packet{animation:radiusPulse 1.25s ease-in-out infinite;transform-box:fill-box;transform-origin:center;filter:drop-shadow(0 0 2px currentColor)}.radius-visual svg .packet.delay-1{animation-delay:.35s}.radius-visual svg .packet.delay-2{animation-delay:.7s}.radius-visual svg .packet.delay-3{animation-delay:1.05s}.radius-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7}.radius-visual__note{color:#94a3b8;font-size:.8rem;line-height:1.65;margin:.5rem .35rem .2rem}.radius-visual__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}.radius-visual__card{background:#111827;border:1px solid #334155;border-radius:12px;padding:.85rem;color:#e4e4e7;min-width:0}.radius-visual__card strong{display:block;color:#f8fafc;margin-bottom:.35rem}.radius-visual__card p{margin:0;color:#cbd5e1;font-size:.9rem;line-height:1.6}.radius-visual__legend{display:flex;flex-wrap:wrap;gap:.6rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.4rem .3rem}.radius-visual__dot{display:inline-block;width:.6rem;height:.6rem;border-radius:50%;margin-right:.35rem}.radius-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.radius-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.radius-visual details p{margin:.6rem 0 0}.radius-visual a{color:#93c5fd}@keyframes radiusFlow{to{stroke-dashoffset:-32}}@keyframes radiusPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.radius-visual{padding:6px}}@media(prefers-reduced-motion:reduce){.radius-visual svg .flow,.radius-visual svg .packet{animation:none!important}.radius-visual{scroll-behavior:auto!important}}</style>

# Authentification centralisée avec RADIUS — Débutant

**Niveau :** DÉBUTANT

RADIUS est un protocole qui permet de centraliser les décisions d’accès à un réseau. Au lieu de créer une politique et un compte séparés sur chaque switch, borne Wi-Fi, concentrateur VPN ou équipement d’administration, l’organisation peut faire vérifier les demandes par un serveur commun.

Dans un réseau d’entreprise, la question ne se limite pas à « le mot de passe est-il correct ? ». Il faut aussi savoir quel utilisateur ou appareil demande l’accès, depuis quel équipement, à quel service, et avec quels droits. RADIUS transporte les informations utiles entre l’équipement d’accès et le serveur AAA ; le serveur applique une politique ; l’équipement reçoit une décision puis l’applique localement.

Le cours part des notions de base et progresse vers un petit laboratoire. Il distingue la fonction du protocole de celle de l’annuaire ou de la méthode EAP. Les configurations sont des exemples d’apprentissage : les commandes disponibles et la syntaxe exacte dépendent du modèle, du système et de sa version.

> **Analogie** : RADIUS ressemble à un poste de contrôle central dans un bâtiment. Le lecteur de badge à la porte représente le switch ou le point d’accès : il transmet la demande et applique le résultat. Le service de sécurité central représente le serveur RADIUS : il vérifie l’identité et les règles. Le journal des passages représente l’accounting.

---

## 1. La théorie et les algorithmes

### 1.1 Le problème que RADIUS résout

Un réseau comporte souvent plusieurs points d’entrée : commutateurs Ethernet, bornes Wi-Fi, VPN, accès distants et parfois interfaces d’administration. Si chaque équipement conserve sa propre liste de comptes, l’équipe réseau doit gérer plusieurs bases locales. Quand un employé quitte l’entreprise, un compte peut être désactivé sur un équipement et oublié sur un autre.

L’authentification centralisée réduit cette dispersion. Les équipements d’accès deviennent des clients du service RADIUS ; ils demandent une décision à un serveur central. Le serveur peut utiliser sa propre base de comptes ou interroger une source d’identité, selon la solution installée.

La centralisation n’abolit pas tous les comptes locaux. Un compte local d’urgence, protégé et testé, peut rester nécessaire pour la maintenance lorsque le service central est indisponible. Il doit toutefois être limité, surveillé et traité comme un mécanisme de secours, pas comme un moyen de contourner la politique normale.

### 1.2 AAA : trois fonctions différentes

AAA signifie **Authentication, Authorization, Accounting**.

| Fonction | Question | Exemple |
|---|---|---|
| Authentification | Qui ou quoi demande l’accès ? | Un compte valide, un certificat machine ou une méthode EAP autorisée |
| Autorisation | Que peut faire ce sujet après vérification ? | VLAN attribué, rôle, ACL, profil VPN ou niveau de service |
| Accounting | Que s’est-il passé pendant la session ? | Début, fin, durée, identifiant de session et compteurs si disponibles |

Ces fonctions se complètent, mais ne sont pas interchangeables. Un résultat d’authentification valide ne devrait pas donner automatiquement des droits administratifs. L’autorisation doit respecter le moindre privilège. L’accounting permet de comprendre l’usage d’un service et de reconstruire une chronologie ; il n’est pas, à lui seul, une preuve complète de tout ce que l’utilisateur a fait.

> **Piège :** confondre « identité authentifiée » et « droits illimités ». Un employé authentifié peut n’avoir accès qu’à un VLAN bureautique ; un administrateur réseau peut recevoir un rôle différent. Le serveur doit appliquer des règles explicites en fonction de l’identité, du type d’accès et du contexte.

### 1.3 Les rôles du système

Quatre composants sont fréquemment présents :

1. **Supplicant** : le poste ou l’appareil qui demande un accès, par exemple un ordinateur en 802.1X.
2. **Authenticator / NAS** : l’équipement réseau qui contrôle le point d’accès et joue le rôle de client RADIUS. NAS signifie *Network Access Server* ; le terme peut désigner un switch, un point d’accès, un VPN ou un équipement similaire.
3. **Serveur RADIUS** : reçoit et évalue les requêtes, puis émet les réponses protocolaires.
4. **Source d’identité et de politiques** : base locale du serveur, annuaire d’entreprise, magasin de certificats ou autre mécanisme pris en charge.

L’authenticator et le serveur RADIUS ne sont pas le même élément, même si, dans un laboratoire, ils peuvent parfois être hébergés sur une même machine. L’équipement d’accès demeure responsable de l’application effective du résultat : ouverture de port, affectation d’un VLAN ou établissement d’une session VPN.

## Schéma animé 1 — Architecture d’une authentification centralisée

<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark">
<svg viewBox="0 0 1000 360" role="img" aria-label="Architecture RADIUS avec poste, équipement d’accès, serveur, annuaire et journaux" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px">
<text x="24" y="30" text-anchor="start" font-size="19" fill="#f4f4f5" font-weight="700" class="title">Architecture RADIUS — rôles séparés</text>
<rect x="25" y="78" width="190" height="142" rx="12" fill="#111827" stroke="#64748b" stroke-width="1.6" class="node"/>
<text x="120" y="105" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="120" dy="0">Poste / téléphone</tspan><tspan x="120" dy="21">Supplicant</tspan></text>
<text x="120" y="153" text-anchor="middle" font-size="14" fill="#cbd5e1"><tspan x="120" dy="0">Identité / EAP</tspan><tspan x="120" dy="25">Demande l’accès</tspan></text>
<rect x="270" y="78" width="205" height="142" rx="12" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6" class="node node-green"/>
<text x="372" y="105" text-anchor="middle" font-size="16" fill="#f8fafc" font-weight="700" class="title"><tspan x="372" dy="0">Switch / point d’accès</tspan></text>
<text x="372" y="140" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="372" dy="0">Client RADIUS / NAS</tspan><tspan x="372" dy="24">Applique port, VLAN, rôle</tspan><tspan x="372" dy="24">Ce n’est pas le serveur</tspan></text>
<rect x="535" y="78" width="205" height="142" rx="12" fill="#10243b" stroke="#60a5fa" stroke-width="1.6" class="node node-blue"/>
<text x="637" y="105" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="637" dy="0">Serveur RADIUS</tspan></text>
<text x="637" y="140" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="637" dy="0">Évalue identité et règles</tspan><tspan x="637" dy="24">Accept / Reject / Challenge</tspan><tspan x="637" dy="24">Centralise la politique</tspan></text>
<rect x="790" y="55" width="185" height="90" rx="12" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6" class="node node-amber"/>
<text x="882" y="82" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="882" dy="0">Annuaire</tspan></text>
<text x="882" y="108" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="882" dy="0">Comptes / groupes</tspan><tspan x="882" dy="21">Source d’identité</tspan></text>
<rect x="790" y="195" width="185" height="90" rx="12" fill="#111827" stroke="#64748b" stroke-width="1.6" class="node"/>
<text x="882" y="222" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="882" dy="0">Journaux</tspan></text>
<text x="882" y="248" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="882" dy="0">Accept / Reject</tspan><tspan x="882" dy="21">Accounting / sessions</tspan></text>
<path d="M215 150 H270" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="260,144 271,150 260,156" fill="#4ade80"/>
<circle cx="242" cy="150" r="5" fill="#4ade80" class="packet"><animateMotion path="M-27 0 L28 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="242" y="133" text-anchor="middle" font-size="12" fill="#86efac" font-weight="700">EAPOL / accès</text>
<path d="M475 150 H535" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-blue"/>
<polygon points="525,144 536,150 525,156" fill="#60a5fa"/>
<circle cx="506" cy="150" r="5" fill="#60a5fa" class="packet delay-1"><animateMotion path="M-31 0 L29 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="505" y="133" text-anchor="middle" font-size="12" fill="#93c5fd" font-weight="700">RADIUS</text>
<path d="M740 104 H765 V96 H790" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-amber"/>
<polygon points="780,90 791,96 780,102" fill="#fbbf24"/>
<circle cx="765" cy="96" r="5" fill="#fbbf24" class="packet delay-2"><animateMotion path="M-25 8 L0 8 L0 0 L25 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<path d="M740 185 H765 V238 H790" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="780,232 791,238 780,244" fill="#4ade80"/>
<circle cx="765" cy="214" r="5" fill="#4ade80" class="packet delay-3"><animateMotion path="M-25 -29 L0 -29 L0 24 L25 24" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="330" text-anchor="middle" font-size="14" fill="#a1a1aa">L’équipement applique la décision ; le serveur RADIUS évalue la politique.</text>
</svg>
</div>
<p class="radius-visual__caption">Les pointillés se déplacent en continu et les pastilles traversent les liaisons grâce à une animation SVG native. Si le lecteur retire les balises d’animation SVG, les pointillés CSS et les pastilles pulsantes restent le mode de secours. Les pastilles animées représentent les échanges. Le poste ne parle pas forcément directement à RADIUS : en 802.1X, il dialogue avec le switch ou le point d’accès, qui relaie l’authentification au serveur.</p>

## Schéma animé 2 — Le cycle de décision RADIUS

<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark">
<svg viewBox="0 0 1000 405" role="img" aria-label="Cycle RADIUS montrant Access Request, Accept, Reject et Challenge" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px">
<text x="24" y="30" text-anchor="start" font-size="19" fill="#f4f4f5" font-weight="700" class="title">Cycle de décision RADIUS</text>
<rect x="45" y="52" width="250" height="72" rx="12" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6" class="node node-green"/>
<text x="170" y="80" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="170" dy="0">Client RADIUS / NAS</tspan></text>
<text x="170" y="104" text-anchor="middle" font-size="13" fill="#cbd5e1">Switch · point d’accès · VPN</text>
<rect x="705" y="52" width="250" height="72" rx="12" fill="#10243b" stroke="#60a5fa" stroke-width="1.6" class="node node-blue"/>
<text x="830" y="80" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="830" dy="0">Serveur RADIUS</tspan></text>
<text x="830" y="104" text-anchor="middle" font-size="13" fill="#cbd5e1">Identité · règles · politiques</text>
<path d="M295 155 H705" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-blue"/>
<polygon points="695,149 706,155 695,161" fill="#60a5fa"/>
<circle cx="500" cy="155" r="5" fill="#60a5fa" class="packet"><animateMotion path="M-205 0 L205 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="143" text-anchor="middle" font-size="14" fill="#93c5fd" font-weight="700">1 · Access-Request</text>
<path d="M705 218 H295" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="305,212 294,218 305,224" fill="#4ade80"/>
<circle cx="500" cy="218" r="5" fill="#4ade80" class="packet delay-1"><animateMotion path="M205 0 L-205 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="205" text-anchor="middle" font-size="14" fill="#86efac" font-weight="700">2a · Access-Accept</text>
<path d="M705 277 H295" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-red"/>
<polygon points="305,271 294,277 305,283" fill="#fb7185"/>
<circle cx="500" cy="277" r="5" fill="#fb7185" class="packet delay-2"><animateMotion path="M205 0 L-205 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="264" text-anchor="middle" font-size="14" fill="#fda4af" font-weight="700">2b · Access-Reject</text>
<path d="M705 336 H295" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-amber"/>
<polygon points="305,330 294,336 305,342" fill="#fbbf24"/>
<circle cx="500" cy="336" r="5" fill="#fbbf24" class="packet delay-3"><animateMotion path="M205 0 L-205 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="323" text-anchor="middle" font-size="14" fill="#fcd34d" font-weight="700">2c · Access-Challenge</text>
<text x="500" y="382" text-anchor="middle" font-size="13" fill="#a1a1aa">Accept autorise selon la politique · Reject refuse · Challenge poursuit l’échange.</text>
</svg>
</div>
<p class="radius-visual__caption">Accept, Reject et Challenge correspondent à des décisions distinctes. Un Challenge poursuit la conversation ; il ne signifie pas à lui seul un « oui » ou un « non » définitif.</p>

## Schéma animé 3 — Authentification 802.1X avec RADIUS

<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark">
<svg viewBox="0 0 1000 430" role="img" aria-label="Échanges entre supplicant, authenticator et serveur RADIUS dans 802.1X" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px">
<text x="24" y="30" text-anchor="start" font-size="19" fill="#f4f4f5" font-weight="700" class="title">802.1X, EAP et RADIUS : trois rôles distincts</text>
<rect x="25" y="55" width="250" height="86" rx="12" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6" class="node node-green"/>
<text x="150" y="83" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="150" dy="0">1 · Supplicant</tspan></text>
<text x="150" y="112" text-anchor="middle" font-size="13" fill="#cbd5e1">Ordinateur / téléphone</text>
<rect x="375" y="55" width="250" height="86" rx="12" fill="#10243b" stroke="#60a5fa" stroke-width="1.6" class="node node-blue"/>
<text x="500" y="83" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="500" dy="0">2 · Authenticator</tspan></text>
<text x="500" y="112" text-anchor="middle" font-size="13" fill="#cbd5e1">Switch / point d’accès</text>
<rect x="725" y="55" width="250" height="86" rx="12" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6" class="node node-amber"/>
<text x="850" y="83" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="850" dy="0">3 · Serveur AAA</tspan></text>
<text x="850" y="112" text-anchor="middle" font-size="13" fill="#cbd5e1">RADIUS + méthode EAP</text>
<path d="M275 184 H375" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="365,178 376,184 365,190" fill="#4ade80"/>
<circle cx="323" cy="184" r="5" fill="#4ade80" class="packet"><animateMotion path="M-48 0 L52 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="325" y="169" text-anchor="middle" font-size="13" fill="#86efac" font-weight="700">EAPOL / EAP</text>
<path d="M625 235 H725" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-blue"/>
<polygon points="715,229 726,235 715,241" fill="#60a5fa"/>
<circle cx="674" cy="235" r="5" fill="#60a5fa" class="packet delay-1"><animateMotion path="M-49 0 L51 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="674" y="219" text-anchor="middle" font-size="13" fill="#93c5fd" font-weight="700">RADIUS + EAP</text>
<path d="M725 284 H625" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-amber"/>
<polygon points="635,278 624,284 635,290" fill="#fbbf24"/>
<circle cx="674" cy="284" r="5" fill="#fbbf24" class="packet delay-2"><animateMotion path="M51 0 L-49 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="674" y="301" text-anchor="middle" font-size="13" fill="#fcd34d" font-weight="700">Challenge / résultat</text>
<path d="M375 335 H275" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="285,329 274,335 285,341" fill="#4ade80"/>
<circle cx="323" cy="335" r="5" fill="#4ade80" class="packet delay-3"><animateMotion path="M52 0 L-48 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="325" y="320" text-anchor="middle" font-size="13" fill="#86efac" font-weight="700">Résultat appliqué</text>
<rect x="80" y="365" width="840" height="45" rx="12" fill="#111827" stroke="#334155" stroke-width="1.6" class="node"/>
<text x="500" y="393" text-anchor="middle" font-size="14" fill="#e4e4e7">Le port reste contrôlé jusqu’à l’application de la décision et des attributs autorisés.</text>
</svg>
</div>
<p class="radius-visual__caption">802.1X décrit le contrôle d’accès au port ; EAP transporte la méthode d’authentification ; RADIUS transporte les messages entre l’équipement d’accès et le serveur AAA. Un Access-Accept ne suffit pas si la politique locale, le VLAN ou le port sont mal configurés.</p>

## Schéma animé 4 — Comptabilisation d’une session

<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark">
<svg viewBox="0 0 1000 345" role="img" aria-label="Accounting RADIUS avec Accounting Start, Interim Update et Accounting Stop" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px">
<text x="24" y="30" text-anchor="start" font-size="19" fill="#f4f4f5" font-weight="700" class="title">Comptabilisation d’une session</text>
<rect x="50" y="52" width="260" height="75" rx="12" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6" class="node node-green"/>
<text x="180" y="80" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="180" dy="0">NAS / client</tspan></text>
<text x="180" y="105" text-anchor="middle" font-size="13" fill="#cbd5e1">Suit la session et les compteurs</text>
<rect x="690" y="52" width="260" height="75" rx="12" fill="#10243b" stroke="#60a5fa" stroke-width="1.6" class="node node-blue"/>
<text x="820" y="80" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="820" dy="0">Serveur accounting</tspan></text>
<text x="820" y="105" text-anchor="middle" font-size="13" fill="#cbd5e1">Collecte et stockage</text>
<path d="M310 91 H690" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-blue"/>
<polygon points="680,85 691,91 680,97" fill="#60a5fa"/>
<circle cx="500" cy="91" r="5" fill="#60a5fa" class="packet"><animateMotion path="M-190 0 L190 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="77" text-anchor="middle" font-size="13" fill="#93c5fd" font-weight="700">Événements de session</text>
<rect x="40" y="178" width="285" height="92" rx="12" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6" class="node node-green"/>
<text x="182" y="207" text-anchor="middle" font-size="16" fill="#f8fafc" font-weight="700" class="title"><tspan x="182" dy="0">1 · Accounting-Start</tspan></text>
<text x="182" y="235" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="182" dy="0">Début de session</tspan><tspan x="182" dy="20">Identifiant et heure</tspan></text>
<rect x="358" y="178" width="285" height="92" rx="12" fill="#111827" stroke="#64748b" stroke-width="1.6" class="node"/>
<text x="500" y="207" text-anchor="middle" font-size="16" fill="#f8fafc" font-weight="700" class="title"><tspan x="500" dy="0">2 · Interim-Update</tspan></text>
<text x="500" y="235" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="500" dy="0">Mise à jour périodique</tspan><tspan x="500" dy="20">État / compteurs disponibles</tspan></text>
<rect x="675" y="178" width="285" height="92" rx="12" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6" class="node node-amber"/>
<text x="817" y="207" text-anchor="middle" font-size="16" fill="#f8fafc" font-weight="700" class="title"><tspan x="817" dy="0">3 · Accounting-Stop</tspan></text>
<text x="817" y="235" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="817" dy="0">Fin de session</tspan><tspan x="817" dy="20">Compteurs finaux</tspan></text>
<path d="M325 224 H358" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="348,218 359,224 348,230" fill="#4ade80"/>
<circle cx="342" cy="224" r="5" fill="#4ade80" class="packet delay-1"><animateMotion path="M-17 0 L16 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<path d="M643 224 H675" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-amber"/>
<polygon points="665,218 676,224 665,230" fill="#fbbf24"/>
<circle cx="660" cy="224" r="5" fill="#fbbf24" class="packet delay-2"><animateMotion path="M-17 0 L15 0" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="500" y="319" text-anchor="middle" font-size="14" fill="#a1a1aa">L’accounting décrit la session ; il ne remplace pas la décision d’autorisation.</text>
</svg>
</div>
<p class="radius-visual__caption">L’accounting décrit la session et aide à reconstituer une chronologie ; il ne remplace pas la décision d’autorisation. Les attributs précis dépendent de la plateforme et de la politique.</p>

## Schéma animé 5 — Redondance et traitement d’un timeout

<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark">
<svg viewBox="0 0 1000 420" role="img" aria-label="Redondance RADIUS montrant primaire, timeout, secondaire et décision locale" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px">
<text x="24" y="30" text-anchor="start" font-size="19" fill="#f4f4f5" font-weight="700" class="title">Redondance et traitement d’un timeout</text>
<rect x="25" y="155" width="220" height="100" rx="12" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6" class="node node-green"/>
<text x="135" y="186" text-anchor="middle" font-size="16" fill="#f8fafc" font-weight="700" class="title"><tspan x="135" dy="0">Équipement d’accès</tspan></text>
<text x="135" y="212" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="135" dy="0">Client RADIUS / NAS</tspan><tspan x="135" dy="21">Applique la politique</tspan></text>
<rect x="365" y="55" width="250" height="82" rx="12" fill="#10243b" stroke="#60a5fa" stroke-width="1.6" class="node node-blue"/>
<text x="490" y="84" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="490" dy="0">Serveur primaire</tspan></text>
<text x="490" y="110" text-anchor="middle" font-size="13" fill="#cbd5e1">Réponse attendue</text>
<rect x="365" y="270" width="250" height="82" rx="12" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6" class="node node-amber"/>
<text x="490" y="299" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="490" dy="0">Serveur secondaire</tspan></text>
<text x="490" y="325" text-anchor="middle" font-size="13" fill="#cbd5e1">Relève selon la politique</text>
<rect x="740" y="155" width="235" height="100" rx="12" fill="#111827" stroke="#64748b" stroke-width="1.6" class="node"/>
<text x="857" y="186" text-anchor="middle" font-size="17" fill="#f8fafc" font-weight="700" class="title"><tspan x="857" dy="0">Décision locale</tspan></text>
<text x="857" y="212" text-anchor="middle" font-size="13" fill="#cbd5e1"><tspan x="857" dy="0">Accept / Reject</tspan><tspan x="857" dy="21">Secours et journaux</tspan></text>
<path d="M245 180 H300 V96 H365" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-blue"/>
<polygon points="355,90 366,96 355,102" fill="#60a5fa"/>
<circle cx="300" cy="132" r="5" fill="#60a5fa" class="packet"><animateMotion path="M-55 48 L0 48 L0 -36 L65 -36" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="307" y="82" text-anchor="middle" font-size="12" fill="#93c5fd" font-weight="700">1 · Primaire</text>
<path d="M615 96 H665 V180 H740" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-green"/>
<polygon points="730,174 741,180 730,186" fill="#4ade80"/>
<circle cx="665" cy="130" r="5" fill="#4ade80" class="packet delay-1"><animateMotion path="M-50 -34 L0 -34 L0 50 L75 50" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="674" y="82" text-anchor="middle" font-size="12" fill="#86efac" font-weight="700">Réponse</text>
<path d="M490 137 V270" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-amber"/>
<polygon points="484,260 490,271 496,260" fill="#fbbf24"/>
<circle cx="490" cy="205" r="5" fill="#fbbf24" class="packet delay-2"><animateMotion path="M0 -68 L0 65" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="512" y="207" text-anchor="start" font-size="12" fill="#fcd34d" font-weight="700">Timeout / retry</text>
<path d="M615 311 H680 V230 H740" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round" class="flow flow-amber"/>
<polygon points="730,224 741,230 730,236" fill="#fbbf24"/>
<circle cx="680" cy="275" r="5" fill="#fbbf24" class="packet delay-3"><animateMotion path="M-65 36 L0 36 L0 -45 L60 -45" dur="2.1s" calcMode="linear" repeatCount="indefinite" /></circle>
<text x="681" y="296" text-anchor="middle" font-size="12" fill="#fcd34d" font-weight="700">2 · Secours</text>
<text x="500" y="390" text-anchor="middle" font-size="13" fill="#a1a1aa">Valider les secrets, politiques et délais du secondaire ; définir fail-open ou fail-closed.</text>
</svg>
</div>
<p class="radius-visual__caption">Un timeout indique une absence de réponse dans le délai prévu, pas forcément un identifiant incorrect. La stratégie fail-open/fail-closed doit être définie, documentée et testée.</p>

## 2. Configuration et pratique

### 2.1 Préparer un petit laboratoire

Le laboratoire comprend un switch Cisco (ou un équipement émulé compatible), un serveur RADIUS de test, un poste d’administration et un lien IP entre le switch et le serveur. Les adresses suivantes sont purement illustratives :

| Élément | Adresse exemple | Rôle |
|---|---|---|
| Switch de laboratoire | `192.0.2.10/24` | Client RADIUS / NAS |
| Serveur RADIUS | `192.0.2.20/24` | Authentification et accounting |
| Passerelle du segment | `192.0.2.1` | Routage éventuel |
| VLAN utilisateur | `192.0.2.0/24` pour un exemple isolé | Segment de test, à adapter |

Le bloc `192.0.2.0/24` est réservé à la documentation et ne doit pas être utilisé comme adressage de production. Adapter toutes les adresses, les noms de groupe et les commandes à l’équipement réel.

Avant d’activer AAA pour l’accès administratif, créer ou vérifier un compte de secours local protégé, s’assurer de disposer d’un accès console, et sauvegarder la configuration. Sur un switch en production, effectuer ces opérations pendant une fenêtre de maintenance approuvée.

### 2.2 Configurer le client RADIUS côté serveur

Le serveur doit connaître chaque équipement autorisé à émettre des requêtes. Dans un serveur RADIUS, la définition d’un client contient généralement son adresse source attendue, un nom de référence et un secret partagé.

Exemple conceptuel de déclaration d’un switch dans un fichier de configuration de style FreeRADIUS :

```text
client switch-lab {
    ipaddr = 192.0.2.10
    secret = RemplacerParUnSecretDeLaboratoireLongEtUnique
    shortname = switch-lab
}
```

Ce fragment est une illustration ; l’emplacement des fichiers et la syntaxe peuvent varier selon la version du serveur. Un secret contenant des espaces ou caractères spéciaux peut exiger une syntaxe ou un échappement adapté. Dans un environnement réel, ne copier pas ce texte littéralement. Les permissions des fichiers de configuration doivent limiter la lecture aux administrateurs autorisés.

Le serveur doit ensuite avoir une politique d’authentification appropriée. Pour un laboratoire, on peut commencer par un utilisateur de test. En production, privilégier des mécanismes d’identité gérés et les méthodes adaptées au type d’accès plutôt qu’un compte générique commun.

### 2.3 Exemple Cisco IOS : déclarer un serveur RADIUS

Sur de nombreuses versions Cisco IOS/IOS XE, la configuration de serveur passe par `radius server` et des commandes AAA. La syntaxe dépend de la plateforme et des versions ; certains anciens appareils utilisent une syntaxe `radius-server host` différente.

Exemple moderne indicatif :

```text
configure terminal
!
radius server RAD-LAB
 address ipv4 192.0.2.20 auth-port 1812 acct-port 1813
 key RemplacerParUnSecretDeLaboratoireLongEtUnique
!
aaa new-model
!
end
```

N’activer pas aveuglément AAA sur un équipement distant : cette commande change les méthodes utilisées pour les connexions administratives. La partie suivante illustre l’idée des listes de méthodes, mais doit être adaptée au logiciel exact.

### 2.4 Préserver l’accès local avant le changement

Un exemple de préparation d’un compte local de secours pourrait ressembler à ceci, selon les exigences de la plateforme :

```text
configure terminal
username secours privilege 15 secret ChoisirUnSecretRobusteEtUnique
ip domain-name lab.example
crypto key generate rsa modulus 2048
ip ssh version 2
end
```

Cette séquence est indicative : la génération de clés peut demander une interaction et les commandes exactes dépendent de la version. Éviter les comptes `privilege 15` qui sont utilisés quotidiennement. Le compte de secours doit être conservé dans un coffre de secrets, son usage doit générer une alerte et il faut tester l’accès console avant de modifier la méthode d’authentification distante.

> **Danger :** une erreur dans une liste AAA peut verrouiller les administrateurs hors du switch. N’appliquez pas une configuration AAA sur l’unique chemin d’accès distant sans accès console ou mécanisme de retour arrière vérifié.

### 2.5 Définir les méthodes AAA d’administration

Sur IOS, un modèle de commande courant est `aaa authentication login`. Un exemple de méthode locale d’abord, puis RADIUS selon la liste configurée, varie dans son interprétation selon la méthode et l’ordre. Dans le cas de listes de méthodes IOS, l’équipement tente généralement la méthode suivante lorsqu’une méthode précédente ne répond pas, mais un refus d’authentification explicite n’entraîne pas forcément le même comportement qu’un timeout.

Exemple indicatif de liste nommée :

```text
configure terminal
aaa authentication login ADMIN-LOGIN group radius local
line vty 0 4
 login authentication ADMIN-LOGIN
 transport input ssh
end
```

Ne l’appliquez pas sans vérifier les détails du constructeur et les contraintes d’accès. L’ordre `group radius local` n’est pas identique à `local group radius`. Le repli local dépend du comportement de l’implémentation et de la nature de l’échec. Certaines politiques demandent une liste distincte pour l’authentification, l’autorisation EXEC et la comptabilisation.

Sur plusieurs plateformes, on peut configurer explicitement l’autorisation EXEC et l’accounting :

```text
aaa authorization exec default group radius local
aaa accounting exec default start-stop group radius
```

Ces lignes sont des exemples de syntaxe, pas une politique universelle. Si la plate-forme utilise une commande différente, suivre sa documentation et tester en console dans un laboratoire. L’authentification, l’autorisation EXEC et l’accounting sont trois étapes différentes, et chacune peut échouer indépendamment.

### 2.6 Méthode de mise en service sans se verrouiller

Procédure de laboratoire recommandée :

1. Sauvegarder la configuration existante et noter l’adresse de gestion.
2. Vérifier que le compte de secours local fonctionne en console ou sur un accès de test.
3. Vérifier la connectivité IP vers le serveur RADIUS depuis l’adresse source réellement utilisée.
4. Autoriser le switch comme client côté serveur, avec un secret identique des deux côtés.
5. Configurer le serveur RADIUS et définir une méthode de test non privilégiée.
6. Ajouter une liste AAA sans l’appliquer d’abord à toutes les lignes administratives.
7. Tester sur un accès parallèle ou une session de laboratoire ; conserver la console ouverte.
8. Consulter les journaux RADIUS et du switch. Corriger les erreurs avant le déploiement.
9. Appliquer progressivement la liste à l’accès visé, avec un retour arrière préparé.
10. Vérifier le login central, le rôle obtenu, le comportement du compte de secours et les journaux.

Ce processus est plus sûr qu’un copier-coller complet en une seule fois. Le test doit couvrir aussi bien la réponse Accept que le Reject et l’indisponibilité serveur, car le comportement peut être différent.

### 2.7 Vérification de base

Selon la version de Cisco IOS/IOS XE, les commandes utiles peuvent inclure :

```text
show running-config | section aaa
show running-config | section radius
show aaa servers
show logging
show users
show privilege
ping 192.0.2.20 source 192.0.2.10
```

Certains appareils ne prennent pas en charge toutes ces commandes ou exigent une forme différente. Une commande `ping` réussie démontre uniquement que l’ICMP fonctionne entre les points testés ; elle ne prouve pas que les échanges UDP 1812/1813, le secret partagé et les politiques RADIUS sont corrects.

Du côté du serveur, consulter le journal d’authentification en mode debug de test lorsque c’est approprié. Un serveur RADIUS peut offrir un mode foreground/debug permettant de détailler les requêtes et décisions. N’activer pas un mode très verbeux durablement en production : il peut générer beaucoup de données et exposer des informations sensibles.

### 2.8 Exercice de test minimal

Préparer au moins ces quatre essais et documenter le résultat attendu :

| Test | Situation | Résultat attendu |
|---|---|---|
| T1 | Identité de test valide | Accept et rôle prévu |
| T2 | Identité inconnue ou mot de passe invalide | Reject explicite |
| T3 | Serveur arrêté ou filtré | Timeout identifiable, puis comportement de secours documenté |
| T4 | Secret client/serveur volontairement différent dans le laboratoire | Échec contrôlé, diagnostic clair, puis restauration du secret correct |

Pour T4, effectuer l’essai dans un réseau isolé uniquement. Ne pas altérer le secret d’un réseau de production. Après chaque essai, confirmer l’état final de la session et vérifier que les journaux contiennent les informations nécessaires sans inclure de secret en clair.

### 2.9 Exemple d’accounting : ce qu’il faut contrôler

Une fois l’accounting configuré, générer une nouvelle session de test. Vérifier :

- qu’un événement de début est envoyé si la plateforme le permet ;
- qu’une mise à jour périodique est envoyée seulement si elle a été configurée ;
- qu’un événement de fin est enregistré lorsque la session est terminée ;
- que l’identifiant de session permet de relier les messages ;
- que l’heure est cohérente entre NAS, serveur RADIUS et système de journaux ;
- que l’absence d’un Stop peut être repérée et traitée comme une donnée potentiellement incomplète.

Une absence de Stop n’implique pas toujours une action malveillante. Une panne, un redémarrage du NAS, une perte de paquets ou un problème de configuration peut expliquer une session incomplète. Il faut corréler les informations plutôt que conclure sur un unique événement.

---

## 3. Dépannage et sécurité

### 3.1 Méthode de diagnostic

Décomposer le problème en couches :

1. **Transport IP** : le NAS peut-il joindre l’adresse prévue ? La route retour existe-t-elle ? L’adresse source reçue correspond-elle au client autorisé ?
2. **Filtrage** : le pare-feu autorise-t-il UDP 1812 et/ou 1813 dans les deux sens ? Une ACL intermédiaire bloque-t-elle ces paquets ?
3. **Identité du client RADIUS** : le serveur reconnaît-il l’adresse source et le NAS-Identifier ?
4. **Secret partagé** : les deux valeurs concordent-elles et le bon client est-il sélectionné ?
5. **Politique d’identité** : l’utilisateur ou la méthode EAP est-il reconnu ? Le groupe ou la règle correspond-il ?
6. **Réponse et attributs** : Accept, Reject ou Challenge ? Le NAS sait-il appliquer les attributs retournés ?
7. **Application locale** : accès SSH/802.1X/VPN, VLAN ou autorisation EXEC effectivement appliqué ?
8. **Accounting** : les événements de session ont-ils été envoyés et conservés ?

> **Astuce :** commencez par déterminer si le serveur a vu la requête. Si aucune requête n’arrive au journal du serveur, chercher d’abord dans le chemin IP, les ACL, la source et les ports. Si le serveur voit la requête, mais la refuse, examiner les identifiants et la politique. Si le serveur répond Accept, mais l’accès échoue, examiner le NAS et l’autorisation locale.

### 3.2 Symptôme : timeout RADIUS

Un timeout signifie que le client n’a pas reçu une réponse utilisable dans le délai configuré. Les causes fréquentes sont un serveur arrêté, une erreur de routage, un pare-feu qui bloque le trafic, une adresse de client incorrecte, une surcharge ou une réponse qui se perd sur le chemin retour.

Procédure de diagnostic :

- noter l’heure précise et le NAS concerné ;
- tester la connectivité IP depuis la bonne interface ou adresse source ;
- capturer le trafic sur le serveur ou le chemin lorsque c’est autorisé ;
- vérifier si le serveur reçoit l’Access-Request ;
- examiner les compteurs de retransmission et la charge du serveur ;
- vérifier que la réponse peut retourner à l’adresse source du NAS ;
- tester le serveur secondaire si la politique de redondance le prévoit.

Le ping est utile mais insuffisant. Certains réseaux filtrent ICMP tout en autorisant RADIUS, ou le contraire. Le test final doit observer le flux RADIUS lui-même ou un test natif du produit.

### 3.3 Symptôme : secret partagé incorrect

Les signes dépendent de l’implémentation : le serveur peut signaler un authenticator invalide, ignorer la requête ou enregistrer une erreur liée au client. Une erreur de secret peut ressembler à un timeout lorsque le serveur ne répond pas à une requête qu’il ne peut pas valider.

Vérifier la définition du client côté serveur et s’assurer qu’il s’agit bien de l’adresse IP source réellement utilisée par le NAS. Un switch avec plusieurs interfaces peut envoyer les demandes depuis une interface de gestion différente de celle attendue. Il faut confirmer le secret de manière sécurisée, éviter de l’afficher dans des journaux ou de l’envoyer par messagerie, puis effectuer un test immédiat après correction.

Ne pas corriger ce problème en mettant un secret simple identique sur tous les équipements. Chaque client devrait avoir une identité de configuration propre, et les secrets doivent être gérés selon les capacités de la plateforme.

### 3.4 Symptôme : Reject explicite

Si le serveur répond Access-Reject, le transport a probablement fonctionné suffisamment pour permettre un échange de décision, mais il reste à comprendre la raison du refus. Cela peut venir d’une identité inconnue, d’un compte désactivé, d’une méthode non autorisée, d’une règle de groupe, d’un certificat, d’une contrainte horaire ou d’un contexte non conforme.

Comparer l’heure de l’événement au journal du serveur, vérifier le nom présenté, le NAS, le service demandé, la méthode d’authentification et les attributs de contexte. S’assurer que les noms d’utilisateur ne changent pas entre le supplicant et le serveur à cause d’un domaine, d’un suffixe ou d’un format différent.

Les journaux doivent expliquer les refus avec suffisamment de contexte pour le dépannage tout en limitant les données personnelles exposées. Un message de refus ne devrait pas détailler à un utilisateur externe toute la logique interne de défense.

### 3.5 Symptôme : Access-Accept mais accès toujours refusé

Le serveur peut accepter l’identité et renvoyer des attributs que le NAS ne prend pas en charge, ou que sa configuration empêche d’appliquer. Dans le cas de 802.1X, un port peut rester bloqué si l’échange EAP ne se termine pas comme attendu, si le VLAN n’existe pas, si un profil local est prioritaire, ou si les exigences de contrôle d’accès ne sont pas satisfaites.

Vérifications à effectuer :

- confirmer que le message Accept correspond au bon NAS, au bon utilisateur et au bon instant ;
- examiner les attributs effectivement renvoyés sans divulguer des données sensibles ;
- consulter l’état de session et les journaux côté switch ou borne ;
- vérifier que le VLAN, l’ACL, le rôle ou le profil existe et est pris en charge ;
- tester la connectivité du poste après autorisation ;
- vérifier si une politique locale de sécurité prend le dessus.

Ne pas conclure que RADIUS est défectueux uniquement parce que la session ne fonctionne pas. Il existe plusieurs étapes entre une acceptation centrale et le service final.

### 3.6 Méthode d’investigation 802.1X/EAP

Quand l’accès Wi-Fi ou filaire échoue, localiser l’étape exacte :

- le client ne commence pas l’échange EAPOL ;
- l’équipement d’accès ne relaie pas EAP vers RADIUS ;
- le serveur reçoit les requêtes mais la méthode EAP est incompatible ;
- le client rejette le certificat du serveur ou ne peut pas le valider ;
- l’identité ou les autorisations ne correspondent pas à la politique ;
- le serveur accepte, mais l’équipement n’applique pas l’autorisation.

Il faut vérifier les certificats et l’horloge des clients/serveurs, la confiance dans l’autorité de certification, les noms attendus du serveur, les versions de méthode et la disponibilité de la source d’identité. Éviter de recommander de désactiver la validation des certificats pour « faire fonctionner » le Wi-Fi : cela peut ouvrir la voie à un faux serveur d’authentification.

### 3.7 Secret partagé, transport et protections

Le secret partagé RADIUS/UDP ne remplace pas le chiffrement du canal. La protection traditionnelle du champ `User-Password` ne signifie pas que l’ensemble des attributs et du paquet est chiffré. Des informations contextuelles, telles que le nom d’utilisateur ou des identifiants du NAS, peuvent être visibles selon le flux et les protections utilisées.

Recommandations de base :

- placer le trafic RADIUS dans un réseau de confiance segmenté ;
- limiter l’accès du serveur aux clients RADIUS connus ;
- filtrer les sources et destinations, sans exposer le port RADIUS à Internet ;
- employer des secrets robustes et spécifiques ;
- surveiller l’ajout de nouveaux clients, les échecs et les changements de configuration ;
- évaluer RADIUS sur TLS/DTLS et ses profils disponibles lorsque le matériel et les logiciels le supportent ;
- valider le certificat et la politique de confiance pour les transports TLS ;
- documenter la compatibilité, le mode de repli et le plan de migration.

Les standards évoluent. La RFC 9765, publiée en avril 2025, définit un profil expérimental appelé RADIUS/1.1 pour RADIUS sur TLS ou DTLS, où des mécanismes historiques basés sur MD5 peuvent être supprimés. Ce profil ne change pas RADIUS/UDP et ne doit pas être considéré comme pris en charge partout. La RFC 9813 publiée en juillet 2025 donne des considérations opérationnelles pour l’usage de TLS-PSK avec RADIUS/TLS et RADIUS/DTLS. Avant d’envisager une migration, vérifier les documents officiels et la compatibilité des implémentations.

### 3.8 Contrôle de l’accounting et des journaux

L’accounting peut échouer alors que l’authentification fonctionne. Les ports, politiques et destinations peuvent être configurés séparément. Vérifier le serveur accounting, les types de messages, les accusés de réception et les journaux de stockage. S’assurer que l’espace disque et la rotation des journaux sont surveillés.

Les journaux doivent être horodatés avec une source de temps fiable. Le NAS, le serveur RADIUS, l’annuaire et le SIEM devraient avoir une synchronisation cohérente, par exemple via NTP correctement configuré. Sans cela, une chronologie d’incident peut être difficile à reconstruire.

Limiter les droits sur les journaux, définir une durée de conservation appropriée et protéger les exports. Les rapports ne doivent pas révéler de secrets, de données d’authentification ou des informations personnelles au-delà de ce qui est nécessaire.

### 3.9 Redondance, capacité et résilience

La redondance RADIUS demande plus que deux adresses IP. Les deux serveurs doivent avoir des configurations de clients compatibles, des secrets concordants pour chaque NAS, des sources d’identité disponibles et des politiques suffisamment cohérentes. Les certificats, les chaînes de confiance et les profils de transport doivent être alignés si un mode sécurisé est utilisé.

Il faut tester le basculement dans des conditions contrôlées : arrêt propre d’un service, filtrage temporaire du chemin, retour à la normale et comportement lorsqu’un serveur refuse explicitement. Enregistrer les temps de basculement et vérifier les journaux des deux serveurs. Un test de failover qui vérifie seulement que « le login marche » peut masquer un accounting perdu ou un rôle incorrect.

Prévoir le dimensionnement pour les pointes : démarrage du parc au même moment, reprise après une panne Wi-Fi, reconnexion VPN ou redémarrage massif. Utiliser les métriques de requêtes par seconde, latence des réponses, erreurs et nombre de demandes en attente lorsque la solution les expose.

### 3.10 Réduire l’exposition des comptes de secours

Les comptes locaux d’urgence sont utiles mais doivent être fortement contrôlés. Utiliser un compte individualisé ou un mécanisme de coffre lorsque possible, limiter le nombre d’administrateurs qui peuvent le consulter, déclencher une alerte à chaque usage et changer le secret après une intervention si la procédure le prescrit.

Ne pas considérer un mot de passe dans une configuration locale comme une stratégie complète. Il faut protéger la console, limiter SSH aux réseaux d’administration, utiliser un chiffrement de gestion, sauvegarder la configuration de manière sécurisée et auditer les tentatives échouées.

### 3.11 Cas pratique A — le switch ne reçoit pas de réponse

**Situation :** après l’ajout d’un serveur, les connexions administratives échouent après plusieurs secondes. Les logs du switch indiquent des timeouts RADIUS.

**Investigation :** vérifier l’adresse du serveur, la route, l’adresse source du NAS, la règle de pare-feu UDP 1812, puis la présence de requêtes au serveur. Si la requête n’arrive pas au serveur, le problème se situe probablement avant le moteur de politique. Si elle arrive mais aucune réponse n’est émise, consulter le journal du serveur et sa liste de clients configurés.

**Résolution illustrée :** la requête est envoyée depuis l’adresse de management secondaire, tandis que le serveur n’autorise que l’ancienne adresse source. Mettre à jour la définition du client avec la bonne adresse, puis retester. La correction doit être accompagnée d’un contrôle d’inventaire pour éviter d’autoriser une plage trop large.

**Validation :** login de test accepté, mauvais identifiant refusé, secours local vérifié et entrée de journal présente. Faire une sauvegarde après les tests.

### 3.12 Cas pratique B — l’utilisateur est accepté mais placé dans le mauvais VLAN

**Situation :** le serveur RADIUS répond Access-Accept, mais un ordinateur d’un service est placé dans le VLAN par défaut.

**Hypothèses :** le serveur ne renvoie pas les attributs attendus ; les attributs ont un nom ou une valeur non pris en charge ; le VLAN n’existe pas ; la fonction de VLAN dynamique est désactivée ; un profil statique prime sur le résultat.

**Investigation :** comparer les attributs de la réponse à la documentation du constructeur, vérifier le VLAN sur le switch, consulter les journaux d’autorisation et confirmer l’identité ou le groupe qui correspond à la règle. Tester sur un port isolé avec un poste de test.

**Correction :** corriger la règle ou la configuration de VLAN dynamique, ne pas attribuer le VLAN administratif à titre de contournement. Vérifier que le poste obtient une adresse IP adaptée et ne peut pas joindre des ressources interdites.

### 3.13 Cas pratique C — authentification en marche, accounting absent

**Situation :** les utilisateurs se connectent normalement, mais aucun événement de session n’apparaît dans les rapports.

**Investigation :** vérifier si l’accounting est activé pour le bon type d’accès, si UDP 1813 est autorisé, si la bonne destination est définie et si le serveur enregistre les messages Start/Stop. Vérifier les réponses Accounting-Response, les journaux du NAS et l’heure système.

**Correction :** activer l’accounting pour le service approprié, corriger le chemin réseau ou la destination, puis effectuer une session de test de bout en bout. Vérifier également la gestion des sessions qui étaient déjà ouvertes avant la correction.

### 3.14 Checklist avant production

- [ ] Inventaire des NAS : nom, adresse source, fonction, propriétaire et emplacement.
- [ ] Secrets uniques et gérés en coffre ; aucun secret en clair dans les scripts ou dépôts.
- [ ] Serveur primaire et secondaire testés, si utilisés.
- [ ] Ports et flux autorisés uniquement depuis les équipements attendus.
- [ ] Les décisions Accept, Reject et les timeouts ont été testés.
- [ ] Le comportement fail-open/fail-closed est validé par le propriétaire du service.
- [ ] Les comptes de secours sont documentés et leur accès est testé.
- [ ] L’accounting enregistre les événements réellement nécessaires.
- [ ] Les horloges et la rotation des journaux sont surveillées.
- [ ] La procédure de retour arrière est disponible.
- [ ] La configuration de la plate-forme a été vérifiée avec sa documentation exacte.

---

## Points à retenir

1. **RADIUS est un protocole AAA** : il transporte des informations et des décisions entre un équipement d’accès et un serveur central.
2. **Le NAS est le client RADIUS** dans de nombreux déploiements ; un poste en 802.1X utilise plutôt EAP/EAPOL côté accès.
3. **Access-Request, Access-Accept, Access-Reject et Access-Challenge** ont des rôles distincts. Challenge signifie que l’échange doit se poursuivre.
4. **L’authentification, l’autorisation et l’accounting sont différents** et doivent être testés séparément.
5. **1812/UDP et 1813/UDP** sont les ports historiques assignés courants pour l’authentification et l’accounting RADIUS.
6. **Le secret partagé protège la relation client-serveur, pas tout le trafic utilisateur** et ne remplace pas un transport sécurisé sur un réseau non fiable.
7. **Un Accept ne garantit pas que le service final fonctionne** : l’équipement d’accès doit appliquer la réponse et la configuration locale doit être cohérente.
8. **Un timeout n’est pas un Reject.** Le premier oriente vers le transport, la disponibilité et le traitement de la requête ; le second vers une décision du serveur.
9. **Le secours doit être planifié.** La disponibilité ne doit pas provoquer une autorisation non contrôlée par accident.
10. **Vérifier dans le lecteur réel** le rendu des styles et des SVG animés : l’HTML du cours ne contient aucun script ni gestionnaire d’événement, mais la politique DOMPurify de l’application peut modifier les balises autorisées.

## Exercices corrigés

### Exercice 1

Un switch envoie des Access-Request, mais le serveur ne reçoit rien. Quelle famille de causes faut-il vérifier en premier ?

**Correction :** vérifier le chemin IP, la route retour, l’adresse source réelle, les ACL/pare-feu et la destination UDP 1812. Examiner les journaux du serveur et, si autorisé, une capture réseau. Il est prématuré de modifier le mot de passe utilisateur tant que la requête n’atteint pas le serveur.

### Exercice 2

Le serveur renvoie Access-Reject pour un seul utilisateur, alors que les autres peuvent se connecter au même switch. Quelles pistes sont les plus pertinentes ?

**Correction :** examiner l’identité exacte, l’état du compte, la méthode d’authentification, le groupe, la règle de politique et la méthode EAP éventuelle. Comme les autres utilisateurs passent par le même équipement, le chemin de base et le secret du NAS sont moins suspects, sans être impossibles comme causes.

### Exercice 3

Une réponse Access-Accept arrive, mais le client reste dans le VLAN par défaut. Que faut-il faire ?

**Correction :** comparer les attributs retournés avec ceux attendus par le constructeur, vérifier que le VLAN existe et que l’équipement prend en charge l’affectation dynamique. Lire l’état de session sur le switch/AP. Ne pas augmenter les privilèges ou déplacer le client dans un VLAN de confiance pour contourner le symptôme.

### Exercice 4

Expliquez la différence entre le secret RADIUS du switch et le mot de passe d’un utilisateur.

**Correction :** le secret RADIUS est partagé entre un client RADIUS et le serveur pour sécuriser certains mécanismes du protocole historique. Le mot de passe ou autre facteur appartient à l’authentification de l’identité. Le secret du NAS n’est pas envoyé comme un mot de passe d’utilisateur et doit être géré séparément.

### Exercice 5

L’authentification fonctionne, mais aucune session n’apparaît dans les rapports. Donnez trois vérifications.

**Correction :** vérifier que l’accounting est activé pour le bon service, que UDP 1813 et la bonne destination sont configurés, puis que le serveur accepte et stocke les messages Start/Stop. Contrôler aussi l’heure et les journaux du NAS.

---

## Glossaire

| Terme | Définition |
|---|---|
| AAA | Authentification, autorisation et comptabilisation/traçabilité |
| Access-Accept | Réponse RADIUS indiquant que la demande est acceptée selon la politique |
| Access-Challenge | Réponse demandant de poursuivre un échange d’authentification |
| Access-Reject | Réponse RADIUS qui refuse la demande |
| Access-Request | Message client vers serveur portant la demande d’accès |
| Accounting | Enregistrement d’informations sur le cycle de vie d’une session |
| Authenticator | Switch, point d’accès ou équipement qui contrôle l’accès réseau |
| EAP | Framework pour plusieurs méthodes d’authentification |
| EAPOL | Transport de messages EAP sur le lien local, utilisé notamment par 802.1X |
| Fail-closed | Maintenir le refus lorsque la décision centrale n’est pas accessible |
| Fail-open | Autoriser certains accès en mode dégradé lors d’une indisponibilité, selon une politique contrôlée |
| MAB | Contournement 802.1X basé sur une adresse MAC, moins robuste qu’une identité cryptographique |
| NAS | Network Access Server, nom courant pour l’équipement client RADIUS |
| RADIUS | Protocole AAA pour les équipements d’accès et les serveurs centralisés |
| Secret partagé | Secret client-serveur RADIUS, distinct du mot de passe utilisateur |
| Supplicant | Client qui demande l’accès, souvent un poste en 802.1X |
| VLAN dynamique | Attribution d’un VLAN selon une politique d’accès, si le NAS le prend en charge |

## Références et lectures complémentaires

- [RFC 2865 — Remote Authentication Dial In User Service (RADIUS)](https://www.rfc-editor.org/rfc/rfc2865.html) — spécification de base RADIUS. Cette RFC a été mise à jour par plusieurs textes, dont RFC 9765. 
- [RFC 2866 — RADIUS Accounting](https://www.rfc-editor.org/rfc/rfc2866.html) — messages d’accounting.
- [RFC 3580 — IEEE 802.1X RADIUS Usage Guidelines](https://www.rfc-editor.org/rfc/rfc3580.html) — interaction RADIUS et accès 802.1X.
- [RFC 3579 — RADIUS Support for EAP](https://www.rfc-editor.org/rfc/rfc3579.html) — transport des messages EAP dans RADIUS.
- [RFC 5080 — Common RADIUS Implementation Issues and Suggested Fixes](https://www.rfc-editor.org/rfc/rfc5080.html) — considérations opérationnelles et problèmes d’implémentation.
- [RFC 9765 — RADIUS/1.1: Leveraging ALPN to Remove MD5](https://www.rfc-editor.org/rfc/rfc9765.html) — profil expérimental pour RADIUS/TLS et RADIUS/DTLS publié en avril 2025 ; il ne modifie pas RADIUS/UDP.
- [RFC 9813 — Operational Considerations for Using TLS-PSKs with RADIUS](https://www.rfc-editor.org/rfc/rfc9813.html) — bonnes pratiques publiées en juillet 2025 pour la transition vers RADIUS/TLS et DTLS avec PSK.
- Documentation officielle du constructeur du switch, de la borne Wi-Fi, du concentrateur VPN et du serveur RADIUS utilisés en laboratoire. Vérifier les commandes exactes, les types de réponse, les attributs et les versions supportées.

> **Astuce :** conservez une copie datée de la configuration RADIUS du serveur et de celle de chaque NAS, sans y inclure les secrets en clair. Associez chaque changement à un essai fonctionnel, un essai négatif et un plan de retour arrière.
