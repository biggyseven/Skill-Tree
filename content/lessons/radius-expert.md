# Authentification centralisée avec RADIUS — Expert

**Niveau :** Expert

Ce cours poursuit les niveaux Débutant et Intermédiaire. Il suppose que les notions de base (Access-Request, Accept/Reject/Challenge, attributs, accounting, RADIUS client/NAS et 802.1X) sont déjà acquises. L’objectif est maintenant de concevoir, sécuriser, exploiter et dépanner une architecture AAA multi-site à partir de preuves mesurables, sans revenir longuement sur les définitions élémentaires.

> **Analogie** : À l’échelle d’une grande organisation, RADIUS ressemble à un service d’identité distribué : les équipements d’accès sont les points de contrôle, les serveurs de politique prennent les décisions, les proxys acheminent les demandes entre domaines, et la télémétrie permet de prouver ce qui s’est réellement passé.

<style>.radius-visual{width:100%;max-width:100%;margin:1rem 0 1.4rem;color:#e4e4e7;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.radius-visual *{box-sizing:border-box}.radius-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.radius-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e4e7;font-size:15px}.radius-visual svg .small{font-size:12px;fill:#a1a1aa}.radius-visual svg .title{font-size:17px;font-weight:700;fill:#f4f4f5}.radius-visual svg .accent-blue{fill:#93c5fd}.radius-visual svg .accent-green{fill:#86efac}.radius-visual svg .accent-amber{fill:#fcd34d}.radius-visual svg .accent-red{fill:#fda4af}.radius-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.radius-visual svg .node-blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.radius-visual svg .node-green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.radius-visual svg .node-amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.radius-visual svg .node-red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.radius-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:radiusFlow 1.25s linear infinite}.radius-visual svg .flow-blue{stroke:#60a5fa}.radius-visual svg .flow-green{stroke:#4ade80}.radius-visual svg .flow-amber{stroke:#fbbf24}.radius-visual svg .flow-red{stroke:#fb7185}.radius-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.radius-visual svg .packet{animation:radiusPulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.radius-visual svg .packet.delay-1{animation-delay:.35s}.radius-visual svg .packet.delay-2{animation-delay:.7s}.radius-visual svg .packet.delay-3{animation-delay:1.05s}.radius-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.9rem;line-height:1.7}.radius-visual__note{color:#94a3b8;font-size:.8rem;line-height:1.65;margin:.5rem .35rem .2rem}.radius-visual__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem}.radius-visual__card{background:#111827;border:1px solid #334155;border-radius:12px;padding:.85rem;color:#e4e4e7;min-width:0}.radius-visual__card strong{display:block;color:#f8fafc;margin-bottom:.35rem}.radius-visual__card p{margin:0;color:#cbd5e1;font-size:.9rem;line-height:1.6}.radius-visual__legend{display:flex;flex-wrap:wrap;gap:.6rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.4rem .3rem}.radius-visual__dot{display:inline-block;width:.6rem;height:.6rem;border-radius:50%;margin-right:.35rem}.radius-visual details{margin:.65rem .2rem .2rem;border:1px solid #334155;border-radius:10px;padding:.65rem .8rem;color:#cbd5e1;background:#0f172a}.radius-visual summary{cursor:pointer;color:#f8fafc;font-weight:650}.radius-visual details p{margin:.6rem 0 0}.radius-visual a{color:#93c5fd}@keyframes radiusFlow{to{stroke-dashoffset:-32}}@keyframes radiusPulse{0%,100%{opacity:.35}50%{opacity:1}}@media(max-width:700px){.radius-visual{padding:6px}.radius-visual__grid{grid-template-columns:1fr}.radius-visual svg text{font-size:18px}.radius-visual svg .small{font-size:15px}.radius-visual svg .title{font-size:20px}}@media(prefers-reduced-motion:reduce){.radius-visual svg .flow,.radius-visual svg .packet{animation:none!important}.radius-visual{scroll-behavior:auto!important}}</style>

---

## 1. Architecture AAA à grande échelle


Un déploiement expert ne se résume pas à déclarer une adresse de serveur et un secret partagé sur chaque équipement. Il doit définir les frontières de confiance, les chemins de secours, les responsabilités d’exploitation et les preuves nécessaires au dépannage. L’architecture comprend souvent des centaines ou des milliers de NAS, des clusters RADIUS, plusieurs magasins d’identités, des proxys de fédération, des systèmes de journalisation et des équipes aux responsabilités différentes.

Les objectifs doivent être mesurables : taux de succès d’authentification, taux de refus attendus, latence de décision, temps de basculement, perte de messages accounting, âge des informations de révocation et capacité à attribuer une session à un utilisateur, un terminal, un point d’accès et une politique. Une architecture peut répondre à toutes les requêtes tout en restant mauvaise si ses refus sont incohérents ou si ses journaux ne permettent pas de reconstruire une session.

### 1.1 Plans logiques et frontières de confiance


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 440" role="img" aria-label="Architecture RADIUS experte avec équipements d’accès, proxys de domaine, cluster RADIUS, annuaire et SIEM" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="28" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Architecture AAA multi-site — chemins explicites</text><rect x="24" y="66" width="190" height="96" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="119" y="91" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Sites / NAS</text><text x="119" y="116" text-anchor="middle" fill="#e4e4e7" font-size="15">Switch · Wi-Fi · VPN</text><text x="119" y="140" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Identité du client vérifiée</text><rect x="270" y="66" width="190" height="96" rx="12" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="365" y="91" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Proxy de domaine</text><text x="365" y="116" text-anchor="middle" fill="#e4e4e7" font-size="15">Realm · routage</text><text x="365" y="140" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Frontière de confiance</text><rect x="520" y="66" width="205" height="96" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="622" y="91" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Cluster RADIUS</text><text x="622" y="116" text-anchor="middle" fill="#e4e4e7" font-size="15">Policy · authenticator</text><text x="622" y="140" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Nœuds redondants</text><rect x="782" y="44" width="190" height="86" rx="12" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="877" y="70" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">IdP / annuaire</text><text x="877" y="96" text-anchor="middle" fill="#e4e4e7" font-size="15">Identités · groupes</text><rect x="782" y="158" width="190" height="86" rx="12" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="877" y="184" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">PKI / révocation</text><text x="877" y="210" text-anchor="middle" fill="#e4e4e7" font-size="15">Certificats EAP-TLS</text><path d="M214 114 H270" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M460 114 H520" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M725 94 H752 V86 H782" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M725 134 H752 V201 H782" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8" stroke-linecap="round"/><circle cx="240" cy="114" r="5" fill="#60a5fa" class="packet"/><circle cx="488" cy="114" r="5" fill="#4ade80" class="packet delay-1"/><circle cx="752" cy="86" r="5" fill="#fbbf24" class="packet delay-2"/><rect x="270" y="245" width="455" height="72" rx="12" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="497" y="273" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Accounting / bus d’événements</text><text x="497" y="297" text-anchor="middle" fill="#e4e4e7" font-size="15">Start · Interim · Stop · CoA · corrélation de session</text><path d="M365 162 V204 H365 V245" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8" stroke-linecap="round"/><path d="M622 162 V211 H622 V245" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="520" y="344" width="452" height="66" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="746" y="371" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">SIEM / observabilité</text><text x="746" y="394" text-anchor="middle" fill="#e4e4e7" font-size="15">SLO · alertes · recherche d’incident</text><path d="M725 280 H746 V344" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="746" cy="321" r="5" fill="#60a5fa" class="packet delay-3"/><text x="28" y="429" class="small" fill="#a1a1aa" font-size="12">Séparer le transport AAA, la décision de politique et les preuves d’exploitation.</text></svg><p class="radius-visual__caption" style="color:#cbd5e1">Les chemins dessinés sont des relations logiques. Selon l’architecture, l’annuaire, la PKI et le SIEM peuvent être servis par des systèmes distincts et des chemins réseau différents.</p></div>


Un proxy RADIUS relaie des requêtes entre domaines ; il ne doit pas être considéré automatiquement comme une source d’identité ou comme le moteur de politique final. Chaque frontière doit documenter qui authentifie le NAS, qui valide le certificat du terminal, qui choisit les attributs d’autorisation et qui conserve les journaux. Les identités de service doivent être différenciées : secret ou certificat NAS, compte de service d’annuaire, certificat du serveur EAP et identité du serveur de transport RADIUS ne sont pas interchangeables.

### 1.2 Découplage des responsabilités

| Fonction | Responsabilité | Preuve de contrôle | Risque si elle est confondue |
|---|---|---|---|
| Identification du NAS | S’assurer que la requête vient d’un équipement déclaré | IP de pair, certificat, inventaire et identité configurée | Équipement usurpé ou mauvais secret |
| Authentification du terminal | Vérifier une preuve utilisateur/appareil | Résultat EAP, validation du certificat, politique d’identité | Accès accordé sur simple nom déclaré |
| Autorisation | Décider VLAN, rôle, ACL, durée ou service | Attributs envoyés et appliqués par le NAS | Acceptation sans privilèges corrects |
| Accounting | Tracer le cycle de vie de session | Acct-Session-Id, événements Start/Interim/Stop | Sessions fantômes ou attribution impossible |
| Transport protégé | Protéger le chemin entre pairs RADIUS | Certificats, version TLS, logs de connexion | Exposition des données et confiance implicite |
| Observabilité | Mesurer le service et relier les événements | Horodatages, identifiants, métriques | Dépannage fondé sur des suppositions |

> **Piège :** Un `Access-Accept` n’est pas une preuve que le terminal a reçu le bon VLAN ou que l’ACL résultante est appliquée. Il prouve uniquement que le serveur a renvoyé une décision positive. Il faut vérifier la réponse NAS et l’état effectif du port ou de la session.

## 2. Contrôle du protocole, identités et proxy

### 2.1 Cycle de décision dans un domaine fédéré


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 410" role="img" aria-label="Flux de requête entre NAS, proxy, serveur home et source d’identité, avec chemin de réponse" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="25" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Proxy et realm : distinguer le transport de la décision</text><rect x="25" y="66" width="170" height="88" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="110" y="94" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">NAS</text><text x="110" y="119" text-anchor="middle" fill="#e4e4e7" font-size="15">Requête reçue</text><rect x="270" y="66" width="190" height="88" rx="12" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="365" y="94" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Proxy RADIUS</text><text x="365" y="119" text-anchor="middle" fill="#e4e4e7" font-size="15">Realm · policy de transit</text><rect x="535" y="66" width="190" height="88" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="630" y="94" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Home RADIUS</text><text x="630" y="119" text-anchor="middle" fill="#e4e4e7" font-size="15">Décision d’accès</text><rect x="790" y="66" width="185" height="88" rx="12" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="882" y="94" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">IdP / annuaire</text><text x="882" y="119" text-anchor="middle" fill="#e4e4e7" font-size="15">Preuve d’identité</text><path d="M195 95 H270" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M460 95 H535" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M725 95 H790" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="232" cy="95" r="5" fill="#60a5fa" class="packet"/><circle cx="497" cy="95" r="5" fill="#fbbf24" class="packet delay-1"/><circle cx="757" cy="95" r="5" fill="#4ade80" class="packet delay-2"/><text x="232" y="82" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">1</text><text x="497" y="82" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">2</text><text x="757" y="82" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">3</text><path d="M882 154 V213 H630 V154" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8" stroke-linecap="round"/><text x="755" y="204" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Résultat d’identité / attributs</text><path d="M630 154 V264 H365 V154" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="498" y="256" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">4 · Réponse relaiée</text><path d="M365 154 V320 H110 V154" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="237" y="311" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">5 · Accept / Reject / Challenge</text><rect x="535" y="337" width="440" height="54" rx="10" class="node-red" fill="#30151b" stroke="#fb7185" stroke-width="1.6"/><text x="755" y="359" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Politique de confiance explicite</text><text x="755" y="379" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Pair connu · certificat/secret · autorisation de relayer</text></svg><p class="radius-visual__caption" style="color:#cbd5e1">Le proxy route et relaie ; le serveur d’origine peut authentifier, autoriser et construire la décision. Le détail exact dépend du proxy et des méthodes utilisées.</p></div>


Les attributs de routage, les realms et les règles de proxy doivent être testés avec des identités autorisées, inconnues, mal formées et ambiguës. Une règle qui route `user@example.net` vers un mauvais domaine peut envoyer une identité à une destination non souhaitée. Éviter d’utiliser uniquement un suffixe de nom d’utilisateur non authentifié comme décision de sécurité sans contrôles complémentaires. La normalisation de casse, les espaces, l’Unicode et les formats d’identité doivent être cohérents entre NAS, proxy, annuaire et journalisation.

Un proxy peut modifier ou ajouter certains attributs pour la traduction entre domaines. Pour chaque attribut critique, documenter la source d’autorité, la transformation permise, la conservation dans les journaux et le comportement lorsque l’attribut manque. Ne jamais supposer qu’un attribut reçu d’un domaine externe peut déclencher sans validation un rôle administrateur ou une ACL privilégiée.

### 2.2 Corrélation des identités de session

Un grand déploiement doit corréler plusieurs identifiants, car un seul identifiant ne suffit pas dans tous les cas. `Acct-Session-Id` est normalement créé par l’équipement d’accès et devrait être interprété avec le NAS, l’adresse appelée, l’identité du terminal, le type d’accès et les horodatages. L’attribut `Calling-Station-Id` peut représenter une adresse MAC ou une autre identité de station selon le NAS ; il n’est pas forcément une identité humaine stable. `NAS-Identifier` et `NAS-IP-Address` n’ont pas la même sémantique et peuvent changer selon le transport ou l’équipement.

Une clé de corrélation opérationnelle utile est souvent composite : domaine/NAS + Acct-Session-Id + fenêtre temporelle + identité normalisée. Toute normalisation doit préserver la valeur originale pour l’investigation. Lors d’une reconnexion, il faut distinguer une nouvelle session d’une session prolongée ou réauthentifiée. Les erreurs de corrélation peuvent créer de faux « utilisateurs simultanés », laisser des accès actifs dans le dashboard après déconnexion ou attribuer une session à la mauvaise personne.

## 3. EAP, certificats et autorisation robuste

### 3.1 Séquence 802.1X / EAP / RADIUS


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 430" role="img" aria-label="Séquence EAP entre supplicant, authenticator NAS et serveur RADIUS avec décision d’autorisation" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="25" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">802.1X : transport EAP et décision AAA</text><rect x="28" y="63" width="245" height="70" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="150" y="90" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Supplicant</text><text x="150" y="114" text-anchor="middle" fill="#e4e4e7" font-size="15">Poste / certificat</text><rect x="377" y="63" width="245" height="70" rx="12" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="499" y="90" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Authenticator</text><text x="499" y="114" text-anchor="middle" fill="#e4e4e7" font-size="15">Switch / point d’accès</text><rect x="727" y="63" width="245" height="70" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="849" y="90" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Serveur RADIUS</text><text x="849" y="114" text-anchor="middle" fill="#e4e4e7" font-size="15">EAP · politique · identité</text><path d="M150 133 V348" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 7"/><path d="M499 133 V348" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 7"/><path d="M849 133 V348" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 7"/><path d="M155 174 H493" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="324" y="162" text-anchor="middle" fill="#e4e4e7" font-size="15">EAPOL / EAP Request</text><path d="M493 215 H155" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="324" y="203" text-anchor="middle" fill="#e4e4e7" font-size="15">EAP Response</text><path d="M504 257 H843" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="674" y="245" text-anchor="middle" fill="#e4e4e7" font-size="15">Access-Request contenant EAP</text><path d="M843 298 H504" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="674" y="286" text-anchor="middle" fill="#e4e4e7" font-size="15">Challenge / résultat EAP</text><path d="M493 337 H155" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><text x="324" y="325" text-anchor="middle" fill="#e4e4e7" font-size="15">Succès transmis au poste</text><circle cx="324" cy="174" r="5" fill="#60a5fa" class="packet"/><circle cx="674" cy="257" r="5" fill="#fbbf24" class="packet delay-1"/><circle cx="674" cy="298" r="5" fill="#4ade80" class="packet delay-2"/><rect x="28" y="365" width="944" height="45" rx="10" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="500" y="393" text-anchor="middle" fill="#e4e4e7" font-size="15">Le port reste contrôlé jusqu’à ce que l’authenticator applique le résultat et les attributs autorisés.</text></svg><p class="radius-visual__caption" style="color:#cbd5e1">EAP transporte la méthode d’authentification. RADIUS transporte les échanges AAA entre l’équipement d’accès et le serveur. Le NAS reste responsable de l’état effectif du port ou de la session.</p></div>


Un certificat valable ne garantit pas à lui seul une autorisation appropriée. La chaîne de confiance, la période de validité, l’usage de clé, l’identité du sujet ou SAN, l’état de révocation et la correspondance avec la politique doivent être vérifiés conformément à la méthode EAP retenue. Pour EAP-TLS, documenter le comportement lorsque la CRL ou le service OCSP est inaccessible : une politique « fail-open » augmente la disponibilité mais peut affaiblir les garanties de révocation ; « fail-closed » améliore la posture de sécurité mais peut provoquer une panne d’accès si la dépendance est indisponible. Le choix doit être conscient, mesuré et testé.

EAP-TLS 1.3 est défini par la RFC 9190, qui met à jour les règles d’EAP-TLS pour TLS 1.3 et clarifie notamment confidentialité d’identité, dérivation de clés et reprise de session. L’interopérabilité doit être validée entre supplicant, NAS et serveur ; ne pas présumer que tous les clients ont le même profil TLS ou la même prise en charge de la reprise.

### 3.2 Autorisation par rôle, posture et attributs

L’autorisation expert devrait être fondée sur des décisions explicites et limitées : rôle d’utilisateur, type de terminal, emplacement réseau, statut de conformité, horaires si cela est requis, type de service et niveau de risque. Le nom d’utilisateur, seul, ne devrait pas déterminer un rôle de privilège élevé. Utiliser une table de décision versionnée plutôt que des règles dispersées et contradictoires.

| Entrées de politique | Exemple de décision | Validation obligatoire |
|---|---|---|
| Utilisateur géré + certificat géré + terminal conforme | VLAN professionnel et ACL limitée | Confirmer attributs appliqués par le NAS |
| Terminal inconnu + accès filaire | VLAN de quarantaine restreint | Confirmer absence de route vers les réseaux internes |
| Appareil IoT déclaré + certificat appareil | Rôle IoT limité à ses services | Tester les flux autorisés et les refus |
| Compte désactivé ou révocation invalide | Refus contrôlé ou état de secours prévu | Tester la décision en cas d’indisponibilité IdP/PKI |
| Administrateur | Accès d’administration dédié et traçable | MFA/contrôle fort selon la plateforme et le contexte |

> **Danger :** Ne pas attribuer un VLAN d’administration sur la seule base d’un attribut reçu d’un proxy non maîtrisé. Les attributs d’autorisation sont une entrée de politique sensible ; limiter les domaines de confiance et journaliser la décision finale.

## 4. Transport RADIUS et modèle de sécurité

### 4.1 RADIUS/UDP, RADIUS/TLS et profils modernes

Le RADIUS classique sur UDP est encore répandu, mais sa protection dépend de la méthode d’authentification, des attributs et des protections historiques prévues par les RFC correspondantes. Un secret partagé fort et unique par client NAS est préférable à une clé commune à tout le parc. Les ACL de transport doivent limiter les sources et destinations. UDP 1812 est couramment utilisé pour l’authentification/autorisation et UDP 1813 pour accounting, mais les ports réellement configurés doivent être documentés et contrôlés.

RADIUS/TLS protège le transport entre pairs avec TLS et authentification mutuelle. La RFC 6614 décrit ce profil expérimental. RADIUS/1.1, défini par la RFC 9765, s’appuie sur ALPN pour retirer MD5 de certaines constructions historiques et est un profil distinct ; il ne faut pas le présenter comme automatiquement disponible ni compatible partout. La RFC 9813 apporte des considérations opérationnelles sur l’usage de TLS-PSK avec RADIUS. Avant de choisir un transport, vérifier les versions supportées par le serveur, les proxys, les NAS et les équipements intermédiaires, puis définir la validation de certificat, la rotation des clés, la révocation et la stratégie de migration.


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 380" role="img" aria-label="Comparaison des chemins RADIUS sur UDP classique et RADIUS sur TLS protégé" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="25" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Transport : frontières de protection</text><text x="35" y="76" class="accent-amber" font-weight="700" fill="#fcd34d" font-size="15">Profil historique : RADIUS/UDP</text><rect x="35" y="92" width="180" height="65" rx="10" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="125" y="119" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">NAS / proxy</text><text x="125" y="140" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Secret partagé</text><rect x="400" y="92" width="200" height="65" rx="10" class="node-red" fill="#30151b" stroke="#fb7185" stroke-width="1.6"/><text x="500" y="119" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Réseau de transit</text><text x="500" y="140" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Limiter par ACL / VPN</text><rect x="785" y="92" width="180" height="65" rx="10" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="875" y="119" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Serveur RADIUS</text><text x="875" y="140" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Validation client</text><path d="M215 125 H400" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M600 125 H785" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="303" cy="125" r="5" fill="#fbbf24" class="packet"/><circle cx="692" cy="125" r="5" fill="#fbbf24" class="packet delay-2"/><line x1="25" y1="190" x2="975" y2="190" stroke="#334155" stroke-width="1"/><text x="35" y="228" class="accent-green" font-weight="700" fill="#86efac" font-size="15">Transport protégé : RADIUS/TLS ou profil compatible pris en charge</text><rect x="35" y="247" width="180" height="65" rx="10" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="125" y="274" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">NAS / proxy</text><text x="125" y="295" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Certificat / confiance</text><rect x="400" y="247" width="200" height="65" rx="10" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="500" y="274" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Canal TLS protégé</text><text x="500" y="295" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Chiffrement + intégrité</text><rect x="785" y="247" width="180" height="65" rx="10" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="875" y="274" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Serveur RADIUS</text><text x="875" y="295" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Certificat vérifié</text><path d="M215 280 H400" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M600 280 H785" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="303" cy="280" r="5" fill="#4ade80" class="packet delay-1"/><circle cx="692" cy="280" r="5" fill="#4ade80" class="packet delay-3"/><text x="35" y="350" class="small" fill="#a1a1aa" font-size="12">Le transport ne remplace pas l’autorisation ni la sécurité des terminaux ; chaque pair et chaque saut doivent être examinés.</text></svg><p class="radius-visual__caption" style="color:#cbd5e1">Les flux sont conceptuels : le choix réel dépend de l’interopérabilité, des recommandations de sécurité et des capacités de chaque équipement. Ne pas activer un profil moderne sans vérifier la prise en charge de bout en bout.</p></div>


### 4.2 Cycle de vie des secrets, certificats et clés

Le plan de gestion doit traiter séparément : (1) secrets RADIUS historiques partagés entre NAS et serveur, (2) certificats et clés privées des pairs TLS, (3) certificats clients EAP, (4) clés de signature des politiques ou de l’automatisation, et (5) identifiants des comptes de service. Pour chacun, définir propriétaire, stockage, durée de validité, procédure de rotation, fenêtre de chevauchement, révocation, preuve de déploiement et procédure de retour arrière.

Une rotation doit être testée avec des clients pilotes et des pairs de secours. Changer le secret uniquement du côté serveur avant le NAS, ou l’inverse, peut interrompre l’authentification. Pour réduire le risque, utiliser une stratégie supportée par le produit (par exemple deux identités transitoires si le système permet de les configurer), puis suivre le succès des requêtes sur chaque équipement. Ne pas copier des secrets dans les captures, les tickets, la sortie de commande ou les exports de configuration sans traitement adapté.

### 4.3 Menaces et contrôles

| Menace | Contrôle préventif | Détection / preuve |
|---|---|---|
| NAS usurpé | Liste de clients exacte, réseau d’administration, transport authentifié lorsque possible | Requêtes depuis source non prévue, échec TLS, changement d’identité NAS |
| Secret partagé divulgué | Secrets uniques, générés aléatoirement, rotation et coffre | Alertes de requêtes anormales et audit des rotations |
| Certificat serveur non validé côté client EAP | Déployer les CA attendues, vérifier noms et chaîne, empêcher l’acceptation aveugle | Logs de chaîne TLS/EAP et tests négatifs |
| Proxy autorisé à relayer trop largement | ACL de domaine, règles de realm explicites, validation des attributs | Comptage par route, alertes de nouveaux domaines et tests de refus |
| Rejeu ou altération de données | Transport sécurisé approprié et protections de protocole/implémentation | Anomalies d’authentification et intégrité des journaux |
| Fuite de données personnelles | Minimisation des attributs et droits d’accès aux logs | Audit d’accès, durée de rétention et rapports de conformité |
| Abus de CoA/Disconnect | Restreindre les émetteurs et valider le NAS cible | Journaux de commande, source, session affectée et résultat |

> **Astuce :** Pour chaque contrôle de sécurité, écrire un test d’acceptation positif et un test négatif. Le test négatif prouve qu’une identité, un certificat ou un proxy non autorisé est réellement rejeté.

## 5. Haute disponibilité et capacité

### 5.1 Redondance sans ambiguïté


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 400" role="img" aria-label="Chemins RADIUS primaire et secondaire avec décision de timeout et retour au service" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="25" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Résilience AAA : tester plus qu’un ping</text><rect x="28" y="80" width="185" height="82" rx="12" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="120" y="108" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">NAS</text><text x="120" y="132" text-anchor="middle" fill="#e4e4e7" font-size="15">Timer / tentative</text><rect x="338" y="52" width="225" height="82" rx="12" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="450" y="81" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">RADIUS primaire</text><text x="450" y="106" text-anchor="middle" fill="#e4e4e7" font-size="15">Réponse nominale</text><rect x="338" y="207" width="225" height="82" rx="12" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="450" y="236" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">RADIUS secondaire</text><text x="450" y="261" text-anchor="middle" fill="#e4e4e7" font-size="15">Chemin de secours</text><rect x="680" y="112" width="285" height="103" rx="12" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="822" y="141" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Mesure de service</text><text x="822" y="166" text-anchor="middle" fill="#e4e4e7" font-size="15">Auth · Accept/Reject</text><text x="822" y="190" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Accounting · latence · perte</text><path d="M213 100 H338" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M213 141 H270 V248 H338" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M563 92 H630 V140 H680" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M563 248 H630 V185 H680" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="275" cy="100" r="5" fill="#4ade80" class="packet"/><circle cx="276" cy="248" r="5" fill="#fbbf24" class="packet delay-2"/><rect x="28" y="320" width="937" height="54" rx="10" class="node-red" fill="#30151b" stroke="#fb7185" stroke-width="1.6"/><text x="496" y="343" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Scénarios de test</text><text x="496" y="362" text-anchor="middle" fill="#e4e4e7" font-size="15">Panne totale · délai · Accept/Reject lent · panne du proxy · perte d’accounting</text></svg><p class="radius-visual__caption" style="color:#cbd5e1">La redondance doit être validée de bout en bout. Un serveur joignable peut échouer sur l’authentification, le service d’identité, le certificat ou l’écriture des journaux.</p></div>


La disponibilité AAA est une chaîne : NAS, réseau de gestion, transport, proxy, moteur RADIUS, annuaire, PKI/EAP, base de politique et dépendances de journalisation. Un test TCP ou ICMP ne valide qu’une petite partie de la chaîne. Définir des sondes synthétiques non privilégiées et des essais périodiques de connexion réelle dans un environnement contrôlé, sans créer une charge qui perturbe les utilisateurs.

Les délais et retransmissions doivent être conçus avec l’ensemble des équipements. Un NAS qui attend trop longtemps avant de retenter peut rallonger l’expérience utilisateur ; un timeout trop faible peut provoquer des doublons, des retransmissions et un basculement inutile durant un pic de latence. Les proxys en cascade amplifient le problème si les délais cumulés sont supérieurs aux attentes du client. Éviter de régler chaque timer indépendamment sans mesurer la latence de bout en bout.

### 5.2 Dimensionnement et files de traitement

La capacité dépend du débit d’authentifications, du pic de reconnexion après une panne Wi-Fi/électrique, du coût des méthodes EAP, de la validation de certificat, de la recherche d’annuaire, des proxys et de l’accounting. Le débit moyen ne suffit pas : dimensionner pour un pic de reconnexion (par exemple un étage entier d’un bâtiment qui revient en ligne) et pour le scénario où un nœud est perdu. Mesurer les temps p50, p95 et p99, le taux d’échec par catégorie et la longueur des files.

Le cache et la reprise de session peuvent améliorer la latence, mais ils introduisent des contraintes sur la révocation, les changements de groupe et la durée de validité de la décision. Documenter la durée de vie des caches et tester la propagation d’une révocation ou d’un changement de rôle. Un cache ancien qui prolonge une ancienne autorisation doit être détectable et conforme à la politique.

### 5.3 Test de basculement sans surprise

1. Enregistrer les métriques de base et confirmer les sessions de référence.
2. Simuler la perte du service primaire dans un environnement autorisé.
3. Vérifier le temps de basculement réel côté NAS et le nombre de tentatives.
4. Vérifier que les Accept/Reject attendus continuent, sans transformer un refus en autorisation.
5. Contrôler l’accounting et identifier les mises à jour manquantes.
6. Restaurer le primaire et observer si le retour arrière provoque une nouvelle vague de reconnexions.
7. Enregistrer les écarts, la charge maximale et les actions correctives.

> **Piège :** Un mode « fail-open » ne doit pas devenir une conséquence involontaire d’un timeout. La décision de permettre l’accès en cas de panne AAA dépend du type de service, du risque et des capacités du NAS ; elle doit être explicitement configurée et testée.

## 6. Accounting, CoA et cycle de vie d’accès


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 405" role="img" aria-label="Cycle de session RADIUS avec Accounting Start, Interim Update, CoA, Disconnect et Stop" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="25" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Session : de l’acceptation à la clôture comptable</text><rect x="30" y="78" width="185" height="75" rx="11" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="122" y="107" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Accès autorisé</text><text x="122" y="131" text-anchor="middle" fill="#e4e4e7" font-size="15">NAS ouvre la session</text><rect x="280" y="78" width="185" height="75" rx="11" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="372" y="107" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Accounting-Start</text><text x="372" y="131" text-anchor="middle" fill="#e4e4e7" font-size="15">Session-ID + heure</text><rect x="530" y="78" width="185" height="75" rx="11" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="622" y="107" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Interim-Update</text><text x="622" y="131" text-anchor="middle" fill="#e4e4e7" font-size="15">Compteurs / durée</text><rect x="780" y="78" width="185" height="75" rx="11" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="872" y="107" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Accounting-Stop</text><text x="872" y="131" text-anchor="middle" fill="#e4e4e7" font-size="15">Cause / fin</text><path d="M215 115 H280" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M465 115 H530" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><path d="M715 115 H780" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="246" cy="115" r="5" fill="#60a5fa" class="packet"/><circle cx="497" cy="115" r="5" fill="#4ade80" class="packet delay-1"/><circle cx="747" cy="115" r="5" fill="#fbbf24" class="packet delay-2"/><rect x="95" y="224" width="330" height="75" rx="11" class="node-red" fill="#30151b" stroke="#fb7185" stroke-width="1.6"/><text x="260" y="253" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">CoA / Disconnect-Request</text><text x="260" y="277" text-anchor="middle" fill="#e4e4e7" font-size="15">Action dynamique contrôlée</text><rect x="575" y="224" width="330" height="75" rx="11" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="740" y="253" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Vérification du NAS</text><text x="740" y="277" text-anchor="middle" fill="#e4e4e7" font-size="15">Résultat · session cible · journal</text><path d="M425 261 H575" class="flow flow-red" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><circle cx="500" cy="261" r="5" fill="#fb7185" class="packet delay-3"/><path d="M740 224 V180 H622 V153" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8" stroke-linecap="round"/><text x="500" y="346" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Ne pas confondre résultat d’authentification et preuve comptable du cycle complet.</text><text x="500" y="374" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Le traitement exact de CoA/Disconnect dépend des extensions et du NAS.</text></svg><p class="radius-visual__caption" style="color:#cbd5e1">L’accounting permet de reconstruire le cycle de vie, mais des paquets peuvent être retardés ou perdus. Les collecteurs doivent gérer les doublons, les mises à jour tardives et les événements reçus dans le désordre.</p></div>


L’accounting ne doit pas être considéré comme une preuve infaillible à lui seul. Les NAS peuvent redémarrer, perdre la connectivité, envoyer des mises à jour répétées ou ne pas envoyer de Stop. Mettre en place une logique de détection de sessions ouvertes trop longtemps, d’événements dupliqués, de compteurs qui diminuent et de Stop sans Start connu. Conserver un indicateur de qualité des données comptables afin que les rapports distinguent les valeurs observées des valeurs estimées.

CoA (Change of Authorization) et Disconnect peuvent modifier ou terminer une session selon les extensions et les capacités de l’équipement. Restreindre les sources qui peuvent émettre ces requêtes, contrôler la cible, protéger le transport, journaliser la demande et le résultat, et vérifier l’état réel côté NAS après l’opération. Une réponse protocolaire positive sans changement effectif de rôle doit déclencher un contrôle complémentaire.

Pour les journaux, minimiser les attributs personnels, définir la durée de conservation, protéger les accès et synchroniser l’heure. Une précision d’horodatage suffisante est nécessaire pour corréler avec Wi-Fi, VPN, DHCP, EDR et pare-feu. Les données sensibles ne doivent pas être envoyées dans des journaux génériques ni incluses inutilement dans les tickets.

## 7. Exploitation des politiques et automatisation

### 7.1 Gouvernance des changements

Les règles AAA doivent être versionnées, relues et testées. Chaque modification devrait contenir : objectif, population ciblée, conditions de succès, tests positifs et négatifs, dépendances, fenêtre de déploiement, métriques observées, responsable, plan de retour arrière et impact sur les sessions existantes. Utiliser un environnement de test qui reproduit au moins un NAS par gamme logicielle et chaque méthode EAP prise en charge.

Une politique devrait être testable sous forme de matrice. Pour chaque combinaison d’identité, de type d’accès et de posture, définir le résultat attendu, les attributs envoyés et l’état qui doit être visible sur le NAS. Contrôler également les cas de défaut : attribut absent, groupe inconnu, annuaire indisponible, certificat expiré, révocation inaccessible, proxy en panne ou réponse retardée. Les politiques fail-safe doivent être explicites.

### 7.2 Automatisation sûre

L’automatisation peut synchroniser les clients NAS, tester les serveurs, vérifier les certificats et comparer les configurations attendues. Elle doit éviter de lire ou d’exporter les secrets en clair. Privilégier les sorties structurées, les contrôles de dérive et un inventaire d’identité stable. Toute action CoA/Disconnect automatisée doit avoir des limites de portée, une validation de session et une trace d’audit.

Exemple de logique de pré-déploiement (pseudo-code) :

```text
charger la politique signée
valider le schéma et les attributs autorisés
vérifier que chaque client NAS existe dans l’inventaire
confirmer la disponibilité des pairs primaires et secondaires
exécuter tests positifs et négatifs sur le banc de test
calculer le différentiel de politique
exiger une revue pour les rôles privilégiés
déployer un lot pilote
observer succès, latence, rejets inattendus et accounting
continuer uniquement si les seuils sont respectés
retour arrière si dérive ou impact hors seuil
```

Ne pas stocker le résultat d’un `Access-Accept` comme preuve complète de l’application d’un rôle. L’automatisation doit suivre la chaîne : demande → décision → attributs renvoyés → réponse de l’équipement → état d’accès observé.

## 8. Observabilité et diagnostic fondé sur les preuves

### 8.1 Tableau de bord opérationnel

Les métriques doivent être ventilées par NAS, version, site, méthode EAP, serveur, proxy, domaine d’identité et résultat. Une hausse des refus peut être un comportement attendu (par exemple, des appareils inconnus bloqués) ou une panne (certificats expirés) ; un taux de succès unique masque ces différences. Distinguer au minimum : refus intentionnels, erreurs de secret/client, timeouts, échecs de certificats, échecs d’annuaire, EAP interrompu, erreurs de transport et échecs comptables.

| Indicateur | Pourquoi le mesurer | Segment utile |
|---|---|---|
| Latence p50/p95/p99 de décision | Détecter une dégradation avant timeout | Site, NAS, méthode, serveur |
| Requêtes/s et retransmissions | Dimensionner et identifier une perte de transport | NAS, interface, proxy |
| Taux de refus par raison | Séparer politique normale de panne technique | EAP, certificat, identité, rôle |
| Files et saturation des workers | Détecter un goulot d’étranglement | Nœud, CPU, mémoire, thread pool |
| Échecs de vérification TLS/PKI | Suivre expiration et dérive de confiance | Certificat, CA, serveur |
| Accounting Start/Interim/Stop manquants | Évaluer l’intégrité des données de session | NAS, site, type d’accès |
| Succès de basculement | Mesurer la résilience réelle | paire primaire/secondaire |

### 8.2 Arbre de dépannage expert


<div class="radius-visual" style="background:#090d14;color:#e4e4e7;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark"><svg viewBox="0 0 1000 510" role="img" aria-label="Arbre de diagnostic RADIUS avec étapes transport, client NAS, authentification, autorisation, accounting et preuve côté équipement" style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><text x="25" y="32" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Trouver la première couche en échec</text><rect x="285" y="52" width="430" height="55" rx="11" class="node-blue" fill="#10243b" stroke="#60a5fa" stroke-width="1.6"/><text x="500" y="85" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">1. La requête atteint-elle le bon serveur ?</text><path d="M500 107 V136" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="285" y="136" width="430" height="55" rx="11" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="500" y="169" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">2. Le NAS / proxy est-il reconnu ?</text><path d="M500 191 V220" class="flow flow-blue" fill="none" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="285" y="220" width="430" height="55" rx="11" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="500" y="253" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">3. L’échange EAP / authentification réussit-il ?</text><path d="M500 275 V304" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="285" y="304" width="430" height="55" rx="11" class="node-green" fill="#0d2a20" stroke="#4ade80" stroke-width="1.6"/><text x="500" y="337" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">4. Les attributs de rôle sont-ils corrects ?</text><path d="M500 359 V388" class="flow flow-green" fill="none" stroke="#4ade80" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="285" y="388" width="430" height="55" rx="11" class="node" fill="#111827" stroke="#64748b" stroke-width="1.6"/><text x="500" y="421" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">5. Le NAS applique-t-il la décision ?</text><path d="M500 443 V466" class="flow flow-muted" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="4 8" stroke-linecap="round"/><text x="500" y="493" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Corréler ensuite accounting, horodatage et état réel de la session.</text><rect x="24" y="136" width="215" height="55" rx="10" class="node-red" fill="#30151b" stroke="#fb7185" stroke-width="1.6"/><text x="131" y="158" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Transport</text><text x="131" y="178" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Route · ACL · TLS · port</text><path d="M285 163 H239" class="flow flow-red" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="761" y="220" width="215" height="55" rx="10" class="node-red" fill="#30151b" stroke="#fb7185" stroke-width="1.6"/><text x="868" y="242" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Identité / EAP</text><text x="868" y="262" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Certificat · méthode · IdP</text><path d="M715 247 H761" class="flow flow-red" fill="none" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/><rect x="761" y="304" width="215" height="55" rx="10" class="node-amber" fill="#2b2110" stroke="#fbbf24" stroke-width="1.6"/><text x="868" y="326" text-anchor="middle" class="title" fill="#f4f4f5" font-size="17" font-weight="700">Politique</text><text x="868" y="346" text-anchor="middle" class="small" fill="#a1a1aa" font-size="12">Groupes · attributs</text><path d="M715 331 H761" class="flow flow-amber" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 9" stroke-linecap="round"/></svg><p class="radius-visual__caption" style="color:#cbd5e1">Mesurer l’endroit du premier écart, plutôt que de modifier simultanément le secret, la politique, le VLAN et les timers. Chaque hypothèse doit prédire une observation.</p></div>


### 8.3 Séquence d’investigation

1. Définir l’impact et la fenêtre temporelle ; comparer à une session saine similaire.
2. Identifier le NAS exact, le pair RADIUS effectif, le serveur, le realm et la méthode EAP.
3. Vérifier transport et identité du client sans révéler le secret partagé.
4. Suivre les identifiants de requête et les horodatages de bout en bout.
5. Séparer échec d’authentification, décision de politique et application des attributs.
6. Contrôler la réponse du NAS et l’état effectif du port ou de la session.
7. Vérifier accounting et corrélation SIEM, en tenant compte des retards et doublons.
8. Appliquer une correction à portée limitée, puis refaire les tests positif et négatif.

Commandes type, à adapter au fournisseur et à la version :

```text
# Cisco IOS / IOS XE — exemples de diagnostic
show aaa servers
show radius statistics
show logging | include RADIUS|AAA|DOT1X
show authentication sessions interface GigabitEthernet1/0/10 details
show dot1x all

# Linux / FreeRADIUS — exemples à adapter
freeradius -XC
radiusd -XC
journalctl -u freeradius --since "15 minutes ago"
tcpdump -ni <interface_admin> host <IP_NAS> and (udp port 1812 or udp port 1813)
```

Les commandes de debug très verbeuses ne doivent être activées que pour une durée limitée, de préférence sur un équipement de test ou pendant une fenêtre contrôlée. Ne pas partager des captures qui révèlent des identifiants personnels ou des attributs sensibles. Dans le cas d’un transport chiffré, une capture réseau peut montrer l’existence et la latence de la connexion TLS mais ne révèle pas nécessairement les messages RADIUS applicatifs.

## 9. Laboratoires et scénarios de production

### Laboratoire 1 — Attribution de rôle erronée

**Situation :** l’utilisateur est authentifié, mais reçoit le VLAN de quarantaine. L’objectif est de localiser si l’erreur vient de l’annuaire, du calcul de politique, de l’attribut envoyé ou du mapping effectué par le NAS.

**Méthode :**

1. Capturer le résultat d’identité (sans exporter les secrets ni les données non nécessaires).
2. Comparer groupe, rôle calculé et attributs RADIUS émis avec la matrice de politique.
3. Vérifier la réponse reçue et l’état de session côté équipement.
4. Vérifier le mapping VLAN, la présence du VLAN sur les trunks, le mode du port et la propagation du rôle.
5. Tester un utilisateur témoin du même profil et une identité qui doit rester en quarantaine.

**Critère de réussite :** la cause est rattachée à une étape prouvée ; le rôle voulu est appliqué et les tests négatifs restent refusés.

### Laboratoire 2 — Tempête de reconnexions après rétablissement

**Situation :** après une panne d’accès, des milliers de clients réessaient de se connecter en même temps. Le taux de succès chute alors que les serveurs semblent en ligne.

**Hypothèses à départager :** saturation des workers RADIUS, limite de connexions TLS, lenteur de l’annuaire, validation de certificats, timeouts trop agressifs, cache de session insuffisant ou limite CPU du NAS.

**Mesures :** requêtes/s, p95/p99, profondeur des files, CPU, temps de recherche d’annuaire, répartition par serveur et taux de retransmission. Tester le retour à la charge normale, puis réduire le débit d’un lot pilote ou répartir la reprise lorsque l’équipement le permet.

**Critère de réussite :** le système conserve le niveau attendu de décision, le comportement de refus reste correct et les files reviennent sous le seuil défini.

### Laboratoire 3 — Comptes actifs après déconnexion

**Situation :** le tableau de bord montre une session encore active après que l’utilisateur a quitté le réseau.

**Méthode :** comparer Accounting-Start, Interim-Update, Stop, état du NAS, DHCP, authentification Wi-Fi/VPN et horodatages. Chercher un NAS qui a redémarré, une réponse Stop perdue, un identifiant de session réutilisé ou un décalage d’horloge. Définir une règle de réconciliation qui ne supprime pas arbitrairement une session active en cas de doute.

**Critère de réussite :** le tableau de bord distingue « active confirmée », « présumée inactive » et « données incomplètes », et chaque transition est traçable.

### Laboratoire 4 — Migration du transport vers TLS

**Situation :** un pilote de serveurs et proxies doit passer du transport UDP classique à un profil de transport sécurisé pris en charge.

**Étapes :** inventorier les capacités, valider la PKI et les noms de pairs, vérifier la date et l’heure, installer les certificats, ouvrir seulement les flux nécessaires, piloter un petit groupe, tester le repli conforme à la politique, observer les erreurs et planifier la rotation. Ne pas supposer que tous les NAS supportent le même profil.

**Critère de réussite :** les pairs valident correctement le certificat, les requêtes et l’accounting sont présents, la latence reste dans le SLO et les tests d’échec sont correctement refusés.

## 10. Gouvernance, SLO et réponse aux incidents

### 10.1 Exemple de SLO

Les valeurs ci-dessous sont des exemples de départ à ajuster aux contraintes opérationnelles ; elles ne constituent pas des normes universelles.

| Indicateur | Exemple de cible | Fenêtre | Action si la cible est dépassée |
|---|---:|---|---|
| Latence p95 de décision | < 300 ms | 5 minutes | Vérifier annuaire, files et répartition de charge |
| Échec technique inattendu | < 0,5 % | 10 minutes | Ventiler par code de raison, NAS et méthode |
| Réussite du basculement | < 10 s sur le scénario validé | Essai planifié | Corriger timers ou disponibilité de dépendances |
| Accounting Stop manquant | < 1 % à 15 minutes | 15 minutes | Identifier pertes, reboot et retards de collecte |
| Certificats critiques proches d’expiration | 0 certificat hors fenêtre de renouvellement | Quotidienne | Renouvellement coordonné et preuve de déploiement |

Un SLO doit avoir un propriétaire, une source de métrique, une méthode de calcul et une procédure d’escalade. Les taux doivent exclure ou séparer les refus attendus ; sinon, une politique de sécurité efficace peut paraître être une panne.

### 10.2 Runbook d’incident AAA

- **Triage :** distinguer tous les sites d’un seul domaine, une méthode EAP d’un seul type de NAS et un problème d’autorisation d’un problème de transport.
- **Contenir :** limiter le périmètre du changement ; ne pas autoriser globalement les accès pour restaurer la disponibilité sans analyse de risque.
- **Collecter :** journaux synchronisés, compteurs, paire utilisée, versions, changements récents et exemples anonymisés.
- **Rétablir :** réorienter vers un nœud sain si le basculement a été testé ; éviter une boucle de basculement.
- **Valider :** tests positif/négatif, VLAN/rôle appliqué, accounting, latence et reprise du trafic.
- **Communiquer :** impact, périmètre, service restant disponible, mesures de contournement et prochaine mise à jour.
- **Améliorer :** cause racine démontrée, actions correctives, propriétaire, échéance et test de non-régression.

> **Danger :** Ne désactive pas la validation du certificat serveur EAP sur les postes pour corriger rapidement une panne. Cette mesure peut permettre à un point d’accès frauduleux de présenter un faux serveur et de récupérer des informations d’authentification. Préférer une correction de chaîne, de nom, de date, de déploiement CA ou de révocation.

## 11. Points à retenir

- Une architecture AAA robuste sépare l’identité du NAS, l’authentification du terminal, l’autorisation, le transport et l’accounting.
- Les proxys établissent des frontières de confiance ; les attributs traversant ces frontières nécessitent une politique d’autorité explicite.
- La redondance doit être évaluée de bout en bout, y compris annuaire, EAP, PKI, comptabilité et latence sous charge.
- L’accounting est une source de preuve essentielle, mais il faut gérer retards, doublons, événements manquants et identifiants réutilisés.
- CoA/Disconnect doit être limité à des émetteurs de confiance et validé sur le NAS réel.
- Le choix entre RADIUS/UDP et un transport protégé dépend des capacités vérifiées de tous les pairs et de la politique de sécurité.
- Une investigation efficace trouve le premier écart mesurable et évite les changements simultanés qui détruisent les preuves.
- Les schémas utilisent des couleurs sombres explicites, une largeur responsive et des animations CSS ; si le lecteur retire les styles, le schéma conserve sa structure et ses couleurs de base autant que le nettoyage le permet.

## 12. Exercices corrigés

### Exercice 1 — Distinguer le refus attendu du défaut technique

**Question :** le taux d’Access-Reject passe de 2 % à 18 %. Quelles données faut-il comparer avant de déclarer un incident ?

**Correction :** comparer les raisons de refus, le site, le type de NAS, la méthode EAP, le statut des certificats et les changements de politique. Si seuls des terminaux inconnus sont rejetés alors que le succès des clients gérés reste stable, cela peut être le résultat attendu d’un contrôle plus strict. Un pic de rejets pour certificats expirés après une mise à jour est plutôt un défaut opérationnel.

### Exercice 2 — Le primaire est déclaré disponible, mais les utilisateurs échouent

**Question :** quelles étapes contrôler ?

**Correction :** vérifier que la requête atteint le bon nœud, que le NAS est reconnu, que le proxy route au bon realm, que l’IdP est joignable, que la méthode EAP et les certificats sont valides, que la politique produit les attributs attendus et que le NAS les applique. Un ping réussi ne prouve pas le fonctionnement AAA.

### Exercice 3 — Comptabilité incohérente

**Question :** comment diagnostiquer une session avec plusieurs Start et aucun Stop ?

**Correction :** rechercher doublons/retransmissions, redémarrage du NAS, absence de réponse accounting, réutilisation d’identifiant, perte de collecte et décalage d’horloge. Définir une réconciliation explicite qui indique le degré de certitude plutôt que d’inventer une heure de fin.

### Exercice 4 — Pourquoi EAP-TLS échoue-t-il après renouvellement du certificat serveur ?

**Correction :** vérifier chaîne de certification, nom/SAN, chaîne intermédiaire, dates, horloge du client, déploiement de la CA, révocation et compatibilité TLS/EAP. Collecter un exemple de client sain et un client en échec. Ne pas contourner le contrôle du certificat.

### Exercice 5 — Quel transport choisir pour un proxy inter-domaines ?

**Correction :** inventorier les prises en charge des deux pairs, la possibilité de validation mutuelle, la politique PKI, la traversée des pare-feu, les performances, la gestion des certificats/PSK et la conformité. La RFC 6614 décrit RADIUS/TLS comme profil expérimental, tandis que RADIUS/1.1 est un profil distinct défini par RFC 9765. Tester la compatibilité et le comportement de repli avant toute migration.

## 13. Glossaire

| Terme | Définition opérationnelle |
|---|---|
| AAA | Authentification, autorisation et accounting |
| NAS | Network Access Server, équipement d’accès qui agit comme client RADIUS |
| EAP | Framework de méthodes d’authentification transporté via 802.1X ou d’autres accès |
| EAP-TLS | Méthode EAP utilisant TLS et des certificats |
| Realm | Suffixe/namespace ou domaine utilisé par une politique de routage d’identité |
| Proxy RADIUS | Relais qui transfère les requêtes entre clients et serveurs RADIUS |
| CoA | Change of Authorization, demande de changement d’une session active |
| Accounting | Enregistrements d’événements et de compteurs du cycle de session |
| SLO | Objectif de niveau de service, défini par une mesure et une fenêtre |
| RADIUS/TLS | Profil de transport RADIUS utilisant TLS |
| RADIUS/1.1 | Profil de transport défini dans RFC 9765, avec ALPN pour supprimer MD5 de constructions historiques |

## 14. Références techniques

- RFC 2865 — Remote Authentication Dial In User Service (RADIUS): https://www.rfc-editor.org/rfc/rfc2865
- RFC 2866 — RADIUS Accounting: https://www.rfc-editor.org/rfc/rfc2866
- RFC 3579 — RADIUS Support for EAP: https://www.rfc-editor.org/rfc/rfc3579
- RFC 5176 — Dynamic Authorization Extensions to RADIUS: https://www.rfc-editor.org/rfc/rfc5176
- RFC 6613 — RADIUS over TCP: https://www.rfc-editor.org/rfc/rfc6613
- RFC 6614 — Transport Layer Security (TLS) Encryption for RADIUS (Experimental): https://www.rfc-editor.org/rfc/rfc6614
- RFC 7360 — Datagram Transport Layer Security (DTLS) as a Transport Layer for RADIUS: https://www.rfc-editor.org/rfc/rfc7360
- RFC 9190 — EAP-TLS 1.3: https://www.rfc-editor.org/rfc/rfc9190
- RFC 9765 — RADIUS/1.1: Leveraging ALPN to Remove MD5: https://www.rfc-editor.org/rfc/rfc9765
- RFC 9813 — Operational Considerations for Using TLS Pre-Shared Keys with RADIUS: https://www.rfc-editor.org/rfc/rfc9813
- RFC 5280 — Internet X.509 Public Key Infrastructure Certificate and CRL Profile: https://www.rfc-editor.org/rfc/rfc5280
- NIST SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management: https://pages.nist.gov/800-63-4/sp800-63b.html

Les commandes et attributs spécifiques restent à vérifier dans la documentation du fournisseur, de la version logicielle et du profil RADIUS réellement déployé. Les RFC définissent le protocole ; elles ne garantissent pas que chaque produit supporte tous les profils ou attributs.
