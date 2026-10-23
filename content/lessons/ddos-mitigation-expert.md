# Attaques DDoS et Mitigation - Expert

**Niveau :** EXPERT

À ce niveau, la défense contre les attaques par déni de service distribué (DDoS) ne se limite plus à augmenter la capacité d'un serveur ou à ajouter une règle de filtrage. Il faut concevoir une architecture de résilience de bout en bout, capable de distinguer une surcharge légitime d'une attaque, d'absorber ou détourner les volumes dépassant les capacités locales, de protéger les plans de contrôle et de gestion, et de maintenir un service acceptable pendant une dégradation contrôlée.

Le travail d'un ingénieur expert consiste à relier plusieurs domaines : routage interdomaines, télémétrie, ingénierie de trafic, protection des applications, capacité des opérateurs, gestion d'incident et gouvernance. Une mitigation techniquement efficace peut être opérationnellement dangereuse si elle détourne aussi le trafic légitime, provoque une fuite de routes, surcharge le pare-feu ou masque les preuves nécessaires à l'analyse.

Ce cours poursuit les niveaux Débutant et Intermédiaire. Il suppose que les notions de volumétrie, de paquets par seconde, de connexions, de saturation de file, de CDN, de scrubbing, de RTBH, de FlowSpec, de WAF et de limitation de débit sont déjà connues. L'objectif est de passer de l'utilisation de mécanismes isolés à la conception, la validation et l'exploitation d'une défense multicouche.

> **Analogie** : Une défense DDoS à grande échelle ressemble à un système d'urgence métropolitain. Les capteurs repèrent l'incident, le centre de contrôle évalue sa portée, les routes sont réorganisées avant que les rues locales soient bloquées, des équipes spécialisées absorbent le surplus, et les services essentiels disposent de voies prioritaires. Une bonne stratégie ne cherche pas seulement à « arrêter les voitures » : elle garde les accès critiques ouverts et évite que la réponse elle-même crée un second accident.

---

<style>
/* Animations CSS des schémas DDoS. Les classes sont utilisées à la place des balises d’animation SVG SMIL,
   souvent retirées par les nettoyeurs HTML. */
.ddos-expert-svg { display:block; width:100%; min-width:640px; height:auto; }
.ddos-expert-svg .ddos-flow-left,
.ddos-expert-svg .ddos-flow-right { animation-iteration-count:infinite; animation-timing-function:linear; }
.ddos-expert-svg .ddos-flow-left { animation-name:ddosExpertFlowLeft; }
.ddos-expert-svg .ddos-flow-right { animation-name:ddosExpertFlowRight; }
.ddos-expert-svg .ddos-flow-fast { animation-duration:.7s; }
.ddos-expert-svg .ddos-flow-normal { animation-duration:1.1s; }
.ddos-expert-svg .ddos-flow-slow { animation-duration:1.5s; }
.ddos-expert-svg .ddos-packet-a { animation:ddosExpertPacket 1.1s ease-in-out infinite; }
.ddos-expert-svg .ddos-packet-b { animation:ddosExpertPacket 1.1s ease-in-out infinite; animation-delay:.55s; }
@keyframes ddosExpertFlowLeft { from { stroke-dashoffset:0; } to { stroke-dashoffset:-28; } }
@keyframes ddosExpertFlowRight { from { stroke-dashoffset:0; } to { stroke-dashoffset:28; } }
@keyframes ddosExpertPacket { 0%,100% { opacity:.3; } 50% { opacity:1; } }
@media (prefers-reduced-motion: reduce) {
  .ddos-expert-svg .ddos-flow-left,
  .ddos-expert-svg .ddos-flow-right,
  .ddos-expert-svg .ddos-packet-a,
  .ddos-expert-svg .ddos-packet-b {
    animation-duration:.01ms !important; animation-iteration-count:1 !important;
  }
}
</style>

## 1. La théorie et les algorithmes

### 1.1 Modéliser la capacité réelle de service

La capacité annoncée d'un lien ou d'un serveur n'est pas nécessairement sa capacité utile. Une interface à 10 Gbit/s peut atteindre sa limite de paquets par seconde avec des paquets petits avant que le compteur de bits n'indique une saturation complète. Un pare-feu peut avoir un débit nominal élevé mais être limité par le nombre de nouvelles connexions, le coût d'inspection, la mémoire d'état ou les performances TLS. Un service applicatif peut saturer sur un pool de threads, un cache miss ou une dépendance en aval alors que le réseau reste relativement calme.

Il faut donc définir un budget de capacité par couche et par dimension. Les unités ne sont pas interchangeables :

| Dimension | Mesure utile | Symptôme typique |
|---|---|---|
| Bande passante | bit/s et octets/s | lien congestionné, pertes en amont |
| Paquets | paquets/s | CPU réseau élevé, petites trames nombreuses |
| Connexions | nouvelles connexions/s, connexions simultanées | table d'état ou backlog saturé |
| Transport | retransmissions, resets, taux d'échec de handshake | perte, filtrage ou asymétrie |
| TLS | handshakes/s, coût CPU, sessions réutilisées | CPU TLS ou crypto saturé |
| HTTP | requêtes/s, latence par percentile, taux d'erreur | pool applicatif ou dépendance saturée |
| Données | lectures/s, écritures/s, IOPS, connexions DB | base de données ou stockage saturé |
| État | mémoire, entrées de suivi, sessions | table de connexions ou cache plein |

La capacité exploitable doit intégrer une marge. Si le débit maximal mesuré en laboratoire est \(C\), il est imprudent de considérer \(C\) comme une cible opérationnelle durable. Une capacité planifiée peut être calculée comme \(C_{planifiée}=C \times u\), où \(u\) est un facteur d'utilisation prudent, par exemple 0,6 à 0,75 selon la variabilité et les objectifs de disponibilité. Le facteur ne doit pas être choisi arbitrairement : il découle des mesures de pointe, de la croissance, du temps de réaction et des dépendances partagées.

La même démarche doit être appliquée à chaque composant. Un goulot d'étranglement se déplace lorsque la défense évolue : après avoir déchargé le TLS vers un proxy, la base de données peut devenir le facteur limitant ; après l'activation d'un scrubbing, le tunnel de retour peut devenir trop étroit ; après une règle FlowSpec, le routeur peut manquer de ressources TCAM ou d'entrées de politique.

### 1.2 Construire une carte des plans réseau et des dépendances

Une architecture résiliente sépare clairement les plans de données, de contrôle et de gestion. Le plan de données transporte les paquets. Le plan de contrôle calcule et distribue les décisions de routage et de politique. Le plan de gestion fournit l'administration, la télémétrie, l'orchestration et les accès opérateur. Une attaque peut viser chacun de ces plans, directement ou indirectement.

<div style="max-width:100%;overflow-x:auto;margin:1.25rem auto;padding:.75rem;border:1px solid #52525b;border-radius:16px;background:#18181b;color:#e4e4e7">
<svg class="ddos-expert-svg" viewBox="0 0 760 355" role="img" aria-label="Architecture de défense DDoS avec plan de données, plan de contrôle et plan de gestion" style="display:block;width:100%;height:auto">
  <defs>
    <marker id="expert-arrow-a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a1a1aa"/></marker>
  </defs>
  <rect x="12" y="12" width="736" height="102" rx="12" fill="#27272a" stroke="#71717a"/>
  <text x="30" y="35" fill="#e4e4e7" font-size="14" font-weight="700">PLAN DE DONNÉES</text>
  <rect x="30" y="49" width="130" height="45" rx="7" fill="#172554" stroke="#60a5fa"/>
  <text x="95" y="68" text-anchor="middle" fill="#dbeafe" font-size="11">Transit / Peering</text><text x="95" y="82" text-anchor="middle" fill="#dbeafe" font-size="10">capacité amont</text>
  <rect x="210" y="49" width="130" height="45" rx="7" fill="#14532d" stroke="#4ade80"/>
  <text x="275" y="68" text-anchor="middle" fill="#dcfce7" font-size="11">Scrubbing / CDN</text><text x="275" y="82" text-anchor="middle" fill="#dcfce7" font-size="10">absorption</text>
  <rect x="390" y="49" width="130" height="45" rx="7" fill="#3f1d2e" stroke="#fb7185"/>
  <text x="455" y="68" text-anchor="middle" fill="#ffe4e6" font-size="11">Edge / Pare-feu</text><text x="455" y="82" text-anchor="middle" fill="#ffe4e6" font-size="10">filtrage local</text>
  <rect x="570" y="49" width="150" height="45" rx="7" fill="#3f3f46" stroke="#a1a1aa"/>
  <text x="645" y="68" text-anchor="middle" fill="#f4f4f5" font-size="11">Services protégés</text><text x="645" y="82" text-anchor="middle" fill="#d4d4d8" font-size="10">application / données</text>
  <path d="M160 72 H205 M340 72 H385 M520 72 H565" stroke="#a1a1aa" stroke-width="2" marker-end="url(#expert-arrow-a)"/>
  <rect x="12" y="128" width="736" height="95" rx="12" fill="#27272a" stroke="#71717a"/>
  <text x="30" y="151" fill="#e4e4e7" font-size="14" font-weight="700">PLAN DE CONTRÔLE</text>
  <rect x="30" y="165" width="205" height="42" rx="7" fill="#312e81" stroke="#a5b4fc"/>
  <text x="132" y="182" text-anchor="middle" fill="#e0e7ff" font-size="11">BGP / politique de routage</text><text x="132" y="196" text-anchor="middle" fill="#c7d2fe" font-size="10">annonces et détournement</text>
  <rect x="277" y="165" width="205" height="42" rx="7" fill="#312e81" stroke="#a5b4fc"/>
  <text x="379" y="182" text-anchor="middle" fill="#e0e7ff" font-size="11">RTBH / FlowSpec</text><text x="379" y="196" text-anchor="middle" fill="#c7d2fe" font-size="10">politiques distribuées</text>
  <rect x="524" y="165" width="196" height="42" rx="7" fill="#312e81" stroke="#a5b4fc"/>
  <text x="622" y="182" text-anchor="middle" fill="#e0e7ff" font-size="11">Validation et garde-fous</text><text x="622" y="196" text-anchor="middle" fill="#c7d2fe" font-size="10">authentification, portée, TTL</text>
  <path d="M132 165 V118 M379 165 V118 M622 165 V118" stroke="#a5b4fc" stroke-width="1.5" stroke-dasharray="4 5" class="ddos-flow-left ddos-flow-normal"></path>
  <rect x="12" y="237" width="736" height="106" rx="12" fill="#27272a" stroke="#71717a"/>
  <text x="30" y="260" fill="#e4e4e7" font-size="14" font-weight="700">PLAN DE GESTION ET OBSERVABILITÉ</text>
  <rect x="30" y="274" width="205" height="48" rx="7" fill="#422006" stroke="#fbbf24"/>
  <text x="132" y="293" text-anchor="middle" fill="#fef3c7" font-size="11">Télémétrie / NetFlow</text><text x="132" y="307" text-anchor="middle" fill="#fde68a" font-size="10">compteurs, latence, pertes</text>
  <rect x="277" y="274" width="205" height="48" rx="7" fill="#422006" stroke="#fbbf24"/>
  <text x="379" y="293" text-anchor="middle" fill="#fef3c7" font-size="11">SIEM / corrélation</text><text x="379" y="307" text-anchor="middle" fill="#fde68a" font-size="10">seuils et chronologie</text>
  <rect x="524" y="274" width="196" height="48" rx="7" fill="#422006" stroke="#fbbf24"/>
  <text x="622" y="293" text-anchor="middle" fill="#fef3c7" font-size="11">Orchestrateur d'incident</text><text x="622" y="307" text-anchor="middle" fill="#fde68a" font-size="10">approbation et journal</text>
  <path d="M132 274 V225 M379 274 V225 M622 274 V225" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="4 5" class="ddos-flow-right ddos-flow-slow"></path>
</svg>
</div>

La carte doit documenter les points de concentration : routeurs d'entrée, liens transit, tunnels GRE ou IPsec, concentrateurs, scrubbing, load balancers, DNS autoritatifs, systèmes d'identité, services de journalisation et consoles d'administration. Un service de mitigation qui dépend du même lien saturable que le trafic attaqué n'est pas un vrai mécanisme d'absorption. Une console de gestion exposée sur le même plan que le service public peut devenir inaccessible au moment où elle est la plus nécessaire.

### 1.3 Taxonomie des attaques et implications opérationnelles

Les attaques volumétriques cherchent à saturer la capacité de transmission. Les attaques protocolaires consomment des ressources des équipements ou des tables d'état. Les attaques applicatives cherchent à imposer un coût élevé par requête, souvent en imitant le trafic valide. Les campagnes hybrides changent de vecteur pendant la réponse, exploitent les dépendances et ciblent simultanément plusieurs services.

| Famille | Signal à corréler | Défense généralement pertinente | Risque de faux positif |
|---|---|---|---|
| Flood UDP volumétrique | bit/s, pps, distribution ports | scrubbing amont, ACL validées, filtrage fournisseur | bloquer un protocole métier |
| SYN flood | nouvelles connexions/s, SYN/ACK, état | SYN cookies/proxy, limites de création d'état | pénaliser clients à forte latence |
| Amplification | tailles asymétriques, protocoles réflecteurs | anti-spoofing, filtrage amont, fermeture des services exposés | filtrer une source partagée |
| HTTP flood | RPS, latence, cache hit, identité | WAF, cache, quotas graduels, challenge adapté | bloquer des pics légitimes |
| TLS handshake flood | handshakes/s, CPU, reprises | terminaison TLS distribuée, limites, réutilisation | bloquer clients anciens |
| Slow connections | durée, sockets inactifs, pool épuisé | timeouts, limites de connexions, proxy | interrompre clients lents légitimes |
| DNS flood | QPS, NXDOMAIN, types et sources | rate limiting DNS, Anycast, filtrage ciblé | perturber résolveurs partagés |

Aucun indicateur ne suffit seul. Une hausse de requêtes peut correspondre à une campagne marketing ; une hausse de SYN peut refléter un déploiement massif ; un grand nombre d'échecs HTTP peut venir d'une panne en aval. L'analyse doit comparer plusieurs dimensions, les références historiques, les services affectés et les changements récents.

### 1.4 Détection : baseline, seuils et détection adaptative

Une baseline utile décrit non seulement la moyenne, mais aussi les cycles, la saisonnalité, les distributions et les corrélations. Les percentiles p50, p95 et p99 de latence, le taux de nouvelles connexions, la proportion de cache misses, la diversité des ASN sources et les erreurs applicatives sont souvent plus informatifs qu'une moyenne globale.

Les seuils statiques sont simples à exploiter mais peuvent générer des alertes bruyantes. Les seuils adaptatifs tiennent compte de l'heure, du jour, de l'événement et de la variabilité historique. Ils ne doivent pas apprendre aveuglément pendant une attaque : si le modèle considère progressivement la charge malveillante comme normale, il perd sa capacité de détection. Prévoir une baseline protégée, des fenêtres de gel et des mécanismes de validation opérateur.

<div style="max-width:100%;overflow-x:auto;margin:1.25rem auto;padding:.75rem;border:1px solid #52525b;border-radius:16px;background:#18181b;color:#e4e4e7">
<svg class="ddos-expert-svg" viewBox="0 0 720 290" role="img" aria-label="Pipeline animé de détection DDoS, de la collecte à la mitigation" style="display:block;width:100%;height:auto">
  <defs><marker id="expert-arrow-b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a1a1aa"/></marker></defs>
  <rect x="15" y="25" width="130" height="60" rx="9" fill="#172554" stroke="#60a5fa"/><text x="80" y="49" text-anchor="middle" fill="#dbeafe" font-size="12">Collecte</text><text x="80" y="66" text-anchor="middle" fill="#bfdbfe" font-size="10">Flow / logs / probes</text>
  <rect x="185" y="25" width="130" height="60" rx="9" fill="#27272a" stroke="#a1a1aa"/><text x="250" y="49" text-anchor="middle" fill="#f4f4f5" font-size="12">Normalisation</text><text x="250" y="66" text-anchor="middle" fill="#d4d4d8" font-size="10">fenêtres temporelles</text>
  <rect x="355" y="25" width="130" height="60" rx="9" fill="#422006" stroke="#fbbf24"/><text x="420" y="49" text-anchor="middle" fill="#fef3c7" font-size="12">Détection</text><text x="420" y="66" text-anchor="middle" fill="#fde68a" font-size="10">règles + anomalies</text>
  <rect x="525" y="25" width="180" height="60" rx="9" fill="#3f1d2e" stroke="#fb7185"/><text x="615" y="49" text-anchor="middle" fill="#ffe4e6" font-size="12">Validation du contexte</text><text x="615" y="66" text-anchor="middle" fill="#fecdd3" font-size="10">impact / faux positifs</text>
  <path d="M145 55 H180 M315 55 H350 M485 55 H520" stroke="#a1a1aa" stroke-width="2" marker-end="url(#expert-arrow-b)"/>
  <path d="M80 105 V120 H420 V105" stroke="#60a5fa" stroke-width="2" fill="none" stroke-dasharray="5 7" class="ddos-flow-left ddos-flow-slow"></path>
  <text x="250" y="140" text-anchor="middle" fill="#93c5fd" font-size="11">Comparaison à la baseline protégée</text>
  <rect x="75" y="165" width="170" height="58" rx="9" fill="#14532d" stroke="#4ade80"/><text x="160" y="189" text-anchor="middle" fill="#dcfce7" font-size="12">Mitigation graduelle</text><text x="160" y="206" text-anchor="middle" fill="#bbf7d0" font-size="10">cache / rate limit / scrubbing</text>
  <rect x="275" y="165" width="170" height="58" rx="9" fill="#312e81" stroke="#a5b4fc"/><text x="360" y="189" text-anchor="middle" fill="#e0e7ff" font-size="12">Mesure de l'effet</text><text x="360" y="206" text-anchor="middle" fill="#c7d2fe" font-size="10">pertes / latence / erreurs</text>
  <rect x="475" y="165" width="170" height="58" rx="9" fill="#27272a" stroke="#a1a1aa"/><text x="560" y="189" text-anchor="middle" fill="#f4f4f5" font-size="12">Ajustement / retrait</text><text x="560" y="206" text-anchor="middle" fill="#d4d4d8" font-size="10">TTL / validation / audit</text>
  <path d="M615 85 V151 H160 V160 M245 194 H270 M445 194 H470" fill="none" stroke="#a1a1aa" stroke-width="2" marker-end="url(#expert-arrow-b)"/>
  <path d="M560 223 V252 H360 V228" fill="none" stroke="#4ade80" stroke-width="2" stroke-dasharray="5 7" class="ddos-flow-right ddos-flow-slow"></path>
  <text x="460" y="273" text-anchor="middle" fill="#86efac" font-size="11">Boucle de retour contrôlée</text>
</svg>
</div>

Un pipeline mature suit une chaîne explicite : collecte, normalisation, agrégation, détection, enrichissement, décision, exécution, mesure et retrait. Chaque étape doit avoir un propriétaire, un délai maximal et un comportement de secours. Une alerte sans action possible ou sans runbook crée du bruit ; une action automatique sans mesure d'effet peut amplifier l'incident.

### 1.5 Architecture multi-couches : empêcher le déplacement du goulot

La défense doit être placée là où la capacité nécessaire existe. Les mécanismes proches de l'application offrent une grande précision mais ne peuvent pas sauver un lien déjà saturé en amont. Les mécanismes opérateur peuvent absorber des volumes importants, mais ils ont moins de contexte applicatif. La stratégie consiste à combiner une capacité d'absorption amont et des politiques de filtrage plus précises à l'edge et dans l'application.

<div style="max-width:100%;overflow-x:auto;margin:1.25rem auto;padding:.75rem;border:1px solid #52525b;border-radius:16px;background:#18181b;color:#e4e4e7">
<svg class="ddos-expert-svg" viewBox="0 0 720 300" role="img" aria-label="Comparaison entre attaque non mitigée et défense multicouche" style="display:block;width:100%;height:auto">
  <text x="18" y="24" fill="#fca5a5" font-size="13" font-weight="700">Sans mitigation amont</text>
  <rect x="18" y="40" width="125" height="48" rx="8" fill="#3f1d2e" stroke="#fb7185"/><text x="80" y="60" text-anchor="middle" fill="#ffe4e6" font-size="11">Flux massif</text><text x="80" y="75" text-anchor="middle" fill="#fecdd3" font-size="10">DDoS</text>
  <path d="M143 64 H245" stroke="#fb7185" stroke-width="5" stroke-dasharray="7 6" class="ddos-flow-left ddos-flow-fast"></path>
  <rect x="245" y="40" width="125" height="48" rx="8" fill="#422006" stroke="#fbbf24"/><text x="307" y="60" text-anchor="middle" fill="#fef3c7" font-size="11">Lien saturé</text><text x="307" y="75" text-anchor="middle" fill="#fde68a" font-size="10">pertes amont</text>
  <path d="M370 64 H455" stroke="#71717a" stroke-width="2" stroke-dasharray="4 6"/>
  <rect x="455" y="40" width="220" height="48" rx="8" fill="#27272a" stroke="#71717a"/><text x="565" y="60" text-anchor="middle" fill="#d4d4d8" font-size="11">Pare-feu local inaccessible</text><text x="565" y="75" text-anchor="middle" fill="#a1a1aa" font-size="10">filtrage trop tardif</text>
  <line x1="18" y1="115" x2="700" y2="115" stroke="#52525b"/>
  <text x="18" y="140" fill="#86efac" font-size="13" font-weight="700">Avec mitigation multicouche</text>
  <rect x="18" y="158" width="115" height="48" rx="8" fill="#3f1d2e" stroke="#fb7185"/><text x="75" y="178" text-anchor="middle" fill="#ffe4e6" font-size="11">Flux DDoS</text><text x="75" y="193" text-anchor="middle" fill="#fecdd3" font-size="10">détecté</text>
  <path d="M133 182 H170" stroke="#fb7185" stroke-width="4" stroke-dasharray="6 5" class="ddos-flow-left ddos-flow-fast"></path>
  <rect x="170" y="158" width="135" height="48" rx="8" fill="#14532d" stroke="#4ade80"/><text x="237" y="178" text-anchor="middle" fill="#dcfce7" font-size="11">Scrubbing amont</text><text x="237" y="193" text-anchor="middle" fill="#bbf7d0" font-size="10">absorption / tri</text>
  <path d="M305 182 H342" stroke="#4ade80" stroke-width="3" stroke-dasharray="5 5" class="ddos-flow-left ddos-flow-normal"></path>
  <rect x="342" y="158" width="110" height="48" rx="8" fill="#172554" stroke="#60a5fa"/><text x="397" y="178" text-anchor="middle" fill="#dbeafe" font-size="11">Edge ACL</text><text x="397" y="193" text-anchor="middle" fill="#bfdbfe" font-size="10">contrôle fin</text>
  <path d="M452 182 H489" stroke="#4ade80" stroke-width="3" stroke-dasharray="5 5" class="ddos-flow-left ddos-flow-normal"></path>
  <rect x="489" y="158" width="186" height="48" rx="8" fill="#27272a" stroke="#4ade80"/><text x="582" y="178" text-anchor="middle" fill="#dcfce7" font-size="11">Service protégé</text><text x="582" y="193" text-anchor="middle" fill="#bbf7d0" font-size="10">trafic utile préservé</text>
  <text x="18" y="242" fill="#a1a1aa" font-size="11">Principe : éliminer ou absorber le trafic avant le premier lien qui ne peut pas l'encaisser.</text>
  <text x="18" y="260" fill="#a1a1aa" font-size="11">Le filtrage local affine la décision ; il ne remplace pas la capacité amont.</text>
</svg>
</div>

Les architectures doivent également traiter le retour du trafic. Avec un service de scrubbing en diversion, l'aller et le retour doivent être conçus pour éviter les chemins asymétriques incompatibles avec les pare-feu à état. Un tunnel GRE ou IPsec peut devenir le goulot ; sa MTU, sa fragmentation, son encapsulation et la capacité de l'équipement de terminaison doivent être testées. Il faut vérifier si les annonces BGP de diversion attirent réellement les préfixes voulus et si le trafic non attaqué est conservé.

### 1.6 RTBH, FlowSpec et politiques de routage : puissance et risques

Remote Triggered Black Hole (RTBH) est utile lorsqu'il faut supprimer rapidement le trafic destiné à une cible, mais la conséquence habituelle est de rendre la cible inaccessible. Il s'agit d'une mesure de dernier recours ou d'une protection très ciblée, pas d'un mécanisme de filtrage intelligent du seul trafic malveillant. Une erreur de communauté, de next-hop ou de préfixe peut entraîner un blackhole plus large que prévu.

BGP FlowSpec peut distribuer des règles de filtrage plus granulaires à travers un réseau compatible. Son efficacité dépend du support constructeur, de l'implémentation, de la capacité matérielle, des politiques d'import, de la cohérence entre routeurs et du contrôle de qui peut annoncer une règle. Une règle de filtrage mal définie peut bloquer des services légitimes ou être utilisée pour provoquer un déni de service. La validation des annonces doit être aussi stricte que celle des routes classiques.

Bonnes pratiques de gouvernance :
- limiter les pairs capables de fournir des règles de mitigation ;
- imposer une politique d'import dédiée, avec des préfixes et composants de match autorisés ;
- limiter la portée, les communautés et la durée de vie opérationnelle ;
- tester en laboratoire les interactions entre règles, priorités et capacités TCAM ;
- journaliser l'émetteur, le motif, le ticket et l'heure de retrait ;
- prévoir un mécanisme de retrait explicite et une procédure de secours si l'orchestrateur tombe en panne.

> **Piège :** Une règle qui « fonctionne » sur un routeur de laboratoire peut échouer ou avoir un coût différent sur le matériel de production. Vérifie la compilation matérielle, l'ordre de priorité, le nombre de règles supportées et le comportement en cas de débordement. Ne déploie jamais une politique large sans simulation, approbation et plan de retour arrière.

### 1.7 Anycast, DNS et protection des services de nommage

Anycast permet d'annoncer la même adresse depuis plusieurs sites afin que le routage distribue les clients vers un point de présence généralement proche selon la politique BGP. Il peut répartir une attaque, réduire l'impact local et améliorer la résilience. Il ne garantit pas une distribution uniforme : les décisions de routage, les politiques des opérateurs, la topologie et les points de concentration influencent la charge. Une mauvaise annonce peut attirer trop de trafic vers un site ou rendre le service instable.

Pour le DNS, séparer les rôles est essentiel : serveurs autoritatifs publics, résolveurs récursifs, systèmes de gestion de zones et accès d'administration ne doivent pas partager inutilement les mêmes surfaces d'exposition. Les réponses DNS volumineuses peuvent favoriser l'amplification si des résolveurs ouverts sont exposés. Les protections incluent la fermeture de la récursion aux clients autorisés, les limites de débit adaptées, la redondance autoritative, la validation de la taille des réponses, la surveillance des types de requête et l'utilisation de fournisseurs spécialisés quand les volumes dépassent la capacité locale.

Une mitigation DNS doit être testée avec DNSSEC, EDNS, les réponses tronquées, le TCP fallback et les résolveurs partagés. Une règle qui élimine un grand nombre de requêtes peut aussi empêcher les résolveurs légitimes d'obtenir les enregistrements nécessaires à la reprise d'un service.

### 1.8 Défense applicative et protection de l'origine

Le CDN et le WAF réduisent la surface d'exposition mais ne sont pas une garantie absolue. Si l'adresse d'origine reste accessible directement, l'attaquant peut contourner le point de présence. L'origine doit accepter uniquement les chemins d'accès attendus, par exemple des plages d'adresses du CDN ou un lien privé contrôlé. Les règles d'origine doivent être maintenues à jour et testées pour éviter qu'une mise à jour fournisseur ne provoque une coupure.

La limitation de débit doit tenir compte de l'identité et du coût réel de l'action. Une limite uniquement par adresse IP peut pénaliser les utilisateurs derrière un NAT d'entreprise ou un réseau mobile, tandis qu'une attaque distribuée peut répartir ses requêtes entre de nombreuses adresses. Combiner des dimensions, par exemple compte, jeton, route, empreinte de session et IP avec des plafonds prudents, offre souvent un meilleur compromis.

Le contrôle de coût par requête est fondamental : un endpoint qui effectue plusieurs recherches coûteuses dans la base n'a pas le même budget qu'un endpoint statique servi depuis le cache. Utiliser des quotas par route, des timeouts, des limites de concurrence, des files bornées et des budgets de dépendance. Les opérations coûteuses doivent être protégées contre les requêtes répétées, les paramètres provoquant des scans, les créations de sessions et les traitements synchrones longs.

### 1.9 Télémétrie, corrélation et qualité des signaux

La télémétrie de flux (NetFlow/IPFIX), les compteurs d'interface, les statistiques de file, les logs de pare-feu, les métriques de load balancer, les journaux HTTP et les traces applicatives ne donnent pas la même vue. Il faut les corréler temporellement et documenter leurs limites : échantillonnage, délais d'export, horloges désynchronisées, pertes de logs, cardinalité élevée ou NAT masquant les clients réels.

Une bonne chaîne de détection conserve une distinction entre :
1. le signal brut observé ;
2. l'hypothèse d'attaque ;
3. la confiance attribuée à cette hypothèse ;
4. l'action choisie ;
5. l'effet mesuré après l'action.

Éviter de confondre « attaque détectée » avec « attaque confirmée ». Une alerte de volumétrie peut déclencher une investigation sans déclencher automatiquement un blackhole. Les actions à faible risque peuvent être automatisées avec un seuil de confiance adapté ; les actions à fort impact doivent nécessiter une validation explicite ou des garde-fous particulièrement stricts.

### 1.10 Modèle de décision : automatiser sans perdre le contrôle

L'orchestration peut réduire le temps de réaction, mais doit être conçue comme un système de sûreté. Chaque action doit posséder un périmètre autorisé, une durée maximale, un mécanisme de retrait, un identifiant d'incident et une mesure de succès. Une action qui n'améliore pas les indicateurs après une fenêtre donnée doit être annulée ou escaladée.

Pseudo-algorithme de réponse :

```text
collecter les métriques et vérifier la qualité des données
si perte de télémétrie ou horloges incohérentes :
    alerter l'équipe et désactiver les actions automatiques à fort impact
sinon :
    comparer à la baseline et aux seuils de sécurité
    enrichir avec le service, l'ASN, le protocole et les changements récents
    estimer la confiance et l'impact
    si confiance faible :
        ouvrir une investigation sans filtrage destructif
    si confiance moyenne :
        activer une mesure réversible à faible risque
        mesurer l'effet et vérifier les faux positifs
    si confiance élevée et risque de saturation amont :
        demander/activer le scrubbing selon la procédure approuvée
    si une action de routage est nécessaire :
        valider le préfixe, la portée, l'autorité et la durée
        appliquer la politique
        confirmer l'état réel des routeurs et l'effet sur le trafic
    journaliser la décision, le propriétaire et les conditions de retrait
à chaque étape :
    vérifier disponibilité, latence, pertes et erreurs côté client
```

L'automatisation ne doit pas pouvoir générer une boucle infinie : détection, mitigation, changement de baseline, nouvelle détection, nouvelle mitigation. Introduire des fenêtres de stabilisation, des limites de fréquence, des seuils de retrait et une intervention humaine lorsque les métriques sont contradictoires.

### 1.11 Exemple d'architecture de routage de mitigation

Le schéma suivant illustre une diversion vers un fournisseur de scrubbing. Il est conceptuel : les annonces exactes, communautés BGP, tunnels et politiques dépendent du fournisseur et de l'opérateur.

<div style="max-width:100%;overflow-x:auto;margin:1.25rem auto;padding:.75rem;border:1px solid #52525b;border-radius:16px;background:#18181b;color:#e4e4e7">
<svg class="ddos-expert-svg" viewBox="0 0 720 300" role="img" aria-label="Diversion BGP vers scrubbing et réinjection du trafic propre" style="display:block;width:100%;height:auto">
  <defs><marker id="expert-arrow-c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a1a1aa"/></marker></defs>
  <rect x="20" y="30" width="150" height="58" rx="10" fill="#3f1d2e" stroke="#fb7185"/><text x="95" y="53" text-anchor="middle" fill="#ffe4e6" font-size="12">Internet</text><text x="95" y="70" text-anchor="middle" fill="#fecdd3" font-size="10">trafic mixte</text>
  <rect x="220" y="30" width="170" height="58" rx="10" fill="#312e81" stroke="#a5b4fc"/><text x="305" y="53" text-anchor="middle" fill="#e0e7ff" font-size="12">Annonce de diversion</text><text x="305" y="70" text-anchor="middle" fill="#c7d2fe" font-size="10">BGP / procédure contrôlée</text>
  <rect x="445" y="30" width="245" height="58" rx="10" fill="#14532d" stroke="#4ade80"/><text x="567" y="53" text-anchor="middle" fill="#dcfce7" font-size="12">Réseau de scrubbing</text><text x="567" y="70" text-anchor="middle" fill="#bbf7d0" font-size="10">absorption et classification</text>
  <path d="M170 59 H215 M390 59 H440" stroke="#a1a1aa" stroke-width="2" marker-end="url(#expert-arrow-c)"/>
  <path d="M567 88 V124" stroke="#4ade80" stroke-width="3" stroke-dasharray="5 6" class="ddos-flow-left ddos-flow-normal"></path>
  <rect x="445" y="128" width="245" height="58" rx="10" fill="#14532d" stroke="#4ade80"/><text x="567" y="151" text-anchor="middle" fill="#dcfce7" font-size="12">Trafic propre réinjecté</text><text x="567" y="168" text-anchor="middle" fill="#bbf7d0" font-size="10">tunnel / peering privé</text>
  <rect x="220" y="128" width="170" height="58" rx="10" fill="#27272a" stroke="#a1a1aa"/><text x="305" y="151" text-anchor="middle" fill="#f4f4f5" font-size="12">Edge de l'organisation</text><text x="305" y="168" text-anchor="middle" fill="#d4d4d8" font-size="10">validation et filtrage final</text>
  <rect x="20" y="128" width="150" height="58" rx="10" fill="#27272a" stroke="#a1a1aa"/><text x="95" y="151" text-anchor="middle" fill="#f4f4f5" font-size="12">Service protégé</text><text x="95" y="168" text-anchor="middle" fill="#d4d4d8" font-size="10">origine privée</text>
  <path d="M445 157 H395 M220 157 H175" stroke="#4ade80" stroke-width="3" marker-end="url(#expert-arrow-c)"/>
  <rect x="20" y="225" width="670" height="48" rx="9" fill="#27272a" stroke="#71717a"/>
  <text x="355" y="245" text-anchor="middle" fill="#e4e4e7" font-size="11">Contrôles indispensables</text>
  <text x="355" y="260" text-anchor="middle" fill="#a1a1aa" font-size="10">préfixe exact · route de retour · capacité du tunnel · MTU · authentification · retrait de diversion</text>
</svg>
</div>

Avant activation, confirmer que le fournisseur annonce et accepte le préfixe, que le trafic revient par le chemin attendu, que le tunnel peut supporter le débit propre, que la MTU ne provoque pas de fragmentation problématique et que les contrôles anti-spoofing sont cohérents. Après activation, vérifier les routes effectives depuis plusieurs points de vue, les compteurs d'encapsulation, les pertes, la latence et les erreurs applicatives.

### 1.12 Résilience des services critiques

Tous les services ne doivent pas être traités de la même manière. Une API d'authentification, le DNS autoritatif, le portail client, le système de paiement et la télémétrie peuvent avoir des priorités différentes. Définir des niveaux de service en mode normal et en mode dégradé. Par exemple, conserver les endpoints de lecture essentiels tout en désactivant temporairement les rapports coûteux, les exports volumineux ou les recherches non indispensables.

La dégradation doit être explicite et testée. Une réponse HTTP 503 avec Retry-After peut être préférable à des timeouts qui provoquent des retries synchronisés. Les clients doivent utiliser un backoff exponentiel avec jitter. Les circuits breakers empêchent une dépendance saturée de consommer les ressources de toute l'application. Les files doivent être bornées : une file infinie transforme une surcharge transitoire en épuisement mémoire et en latence extrême.

### 1.13 Sécurité du plan de gestion pendant un incident

Le plan de gestion doit rester accessible et fiable quand le plan de données est sous pression. Utiliser des accès administratifs hors bande lorsque c'est possible, des chemins de gestion restreints, une authentification forte, des rôles distincts et des journaux centralisés. Les outils de mitigation ne doivent pas dépendre d'une console exposée uniquement derrière le même service public en panne.

Les accès d'urgence doivent être prévus, contrôlés et testés. « Break glass » ne signifie pas compte partagé permanent : les identifiants d'urgence doivent être protégés, surveillés, utilisés avec justification et révoqués ou renouvelés après usage. La séparation des rôles réduit le risque qu'une personne ou un compte compromis puisse simultanément modifier les routes, supprimer les journaux et désactiver les alertes.

### 1.14 Mesures de réussite et objectifs de service

Le nombre de paquets rejetés ne suffit pas à démontrer une mitigation réussie. Les objectifs doivent être exprimés du point de vue du client : disponibilité, latence p95/p99, taux de succès, durée d'indisponibilité, intégrité des transactions et délai de retour à un état stable. Les indicateurs réseau sont nécessaires pour expliquer le résultat, mais ne remplacent pas les sondes synthétiques de bout en bout.

| Indicateur | Question à laquelle il répond | Attention |
|---|---|---|
| Temps de détection (TTD) | Combien de temps avant de reconnaître l'incident ? | dépend de la qualité de baseline |
| Temps de mitigation (TTM) | Combien de temps avant un effet mesurable ? | distinguer action lancée et effet confirmé |
| Taux de succès synthétique | Le client peut-il accomplir son parcours ? | tester plusieurs régions et réseaux |
| Latence p95/p99 | Les utilisateurs subissent-ils une dégradation ? | la moyenne masque les queues longues |
| Faux positifs | Le filtrage rejette-t-il des clients légitimes ? | instrumenter les rejets et les exceptions |
| Capacité résiduelle | Quelle marge reste sur chaque couche ? | inclure tunnels, CPU, état et dépendances |
| Temps de retrait | Peut-on désactiver proprement la mitigation ? | tester avant l'incident réel |

### 1.15 Modèle de menace et limites des protections

La défense doit considérer l'attaquant qui change de vecteur, distribue la charge, exploite les protocoles permis, vise les fournisseurs ou attaque les dépendances. Une architecture peut être résiliente au débit mais vulnérable à une faible quantité de requêtes très coûteuses. Elle peut résister à une attaque sur un préfixe mais échouer si le DNS, l'identité, le système de paiement ou le fournisseur de télémétrie est indisponible.

Définir explicitement les limites de confiance : qui peut annoncer une règle de routage, qui peut changer les ACL, quelles plages d'origine sont autorisées, comment sont protégés les secrets des tunnels, et quels événements exigent une approbation humaine. Les scénarios doivent inclure la panne du fournisseur de scrubbing, la perte de la télémétrie, l'indisponibilité du contrôleur d'automatisation et une action de mitigation erronée.

### 1.16 Simulation de la dynamique d'une attaque

Le schéma suivant illustre la relation entre trafic entrant, capacité de service, file bornée et rejets. Les valeurs sont indicatives et l'animation est visuelle : elle ne mesure pas le réseau réel. L'objectif est de raisonner sur le surplus de trafic et sur le délai avant saturation.

<div style="max-width:100%;overflow-x:auto;margin:1.25rem auto;padding:.75rem;border:1px solid #52525b;border-radius:16px;background:#18181b;color:#e4e4e7">
<svg class="ddos-expert-svg" viewBox="0 0 760 340" role="img" aria-label="Schéma animé : trafic entrant, file d’attente bornée, capacité de service et comportement lors d’une saturation" style="display:block;width:100%;min-width:680px;height:auto">
  <defs><marker id="expert-queue-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a1a1aa"/></marker></defs>
  <text x="25" y="25" fill="#e4e4e7" font-size="14" font-weight="700">Arrivée du trafic</text>
  <rect x="25" y="45" width="145" height="83" rx="9" fill="#172554" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="97" y="73" text-anchor="middle" fill="#dbeafe" font-size="13" font-weight="700">Trafic total</text>
  <text x="97" y="94" text-anchor="middle" fill="#bfdbfe" font-size="12">légitime + attaque</text>
  <text x="97" y="112" text-anchor="middle" fill="#93c5fd" font-size="11">débit variable</text>
  <path d="M170 88 H205" stroke="#fb7185" stroke-width="4" stroke-dasharray="7 6" class="ddos-flow-left ddos-flow-fast"/>
  <polygon points="198,82 208,88 198,94" fill="#fb7185"/>

  <rect x="210" y="36" width="290" height="104" rx="10" fill="#27272a" stroke="#a1a1aa" stroke-width="1.5"/>
  <text x="355" y="59" text-anchor="middle" fill="#f4f4f5" font-size="13" font-weight="700">File d’attente bornée</text>
  <text x="355" y="78" text-anchor="middle" fill="#d4d4d8" font-size="11">Capacité mémoire finie</text>
  <line x1="230" y1="88" x2="480" y2="88" stroke="#52525b" stroke-width="1"/>
  <g fill="#22c55e">
    <rect x="234" y="101" width="24" height="26" rx="4" class="ddos-packet-a"/>
    <rect x="266" y="101" width="24" height="26" rx="4" class="ddos-packet-b"/>
    <rect x="298" y="101" width="24" height="26" rx="4" class="ddos-packet-a"/>
    <rect x="330" y="101" width="24" height="26" rx="4" class="ddos-packet-b"/>
    <rect x="362" y="101" width="24" height="26" rx="4" class="ddos-packet-a"/>
    <rect x="394" y="101" width="24" height="26" rx="4" class="ddos-packet-b"/>
    <rect x="426" y="101" width="24" height="26" rx="4" class="ddos-packet-a"/>
    <rect x="458" y="101" width="24" height="26" rx="4" class="ddos-packet-b"/>
  </g>
  <path d="M500 88 H535" stroke="#4ade80" stroke-width="3" stroke-dasharray="6 6" class="ddos-flow-left ddos-flow-normal"/>
  <polygon points="528,82 538,88 528,94" fill="#4ade80"/>

  <rect x="540" y="45" width="190" height="83" rx="9" fill="#14532d" stroke="#4ade80" stroke-width="1.5"/>
  <text x="635" y="73" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">Service</text>
  <text x="635" y="94" text-anchor="middle" fill="#bbf7d0" font-size="12">capacité maximale</text>
  <text x="635" y="112" text-anchor="middle" fill="#86efac" font-size="11">débit de traitement limité</text>

  <rect x="25" y="163" width="705" height="132" rx="10" fill="#27272a" stroke="#52525b"/>
  <text x="45" y="188" fill="#e4e4e7" font-size="13" font-weight="700">Lire le comportement de la file</text>
  <circle cx="52" cy="213" r="5" fill="#60a5fa"/>
  <text x="68" y="217" fill="#dbeafe" font-size="12">Entrée &lt; capacité : la file reste vide ou se résorbe.</text>
  <circle cx="52" cy="241" r="5" fill="#fbbf24"/>
  <text x="68" y="245" fill="#fde68a" font-size="12">Entrée &gt; capacité : la file augmente selon le surplus.</text>
  <circle cx="52" cy="269" r="5" fill="#fb7185"/>
  <text x="68" y="273" fill="#fecdd3" font-size="12">File pleine : les nouvelles requêtes peuvent être rejetées.</text>
  <text x="25" y="320" fill="#a1a1aa" font-size="11">Capacité utile selon la couche : lien, paquets/s, état, TLS, application ou dépendance.</text>
</svg>
</div>

Le taux de remplissage d'une file bornée peut être approximé par la différence entre débit entrant et débit de service lorsque cette différence est positive. Dans une vraie infrastructure, les arrivées sont variables et les mécanismes de rejet ne sont pas nécessairement uniformes. Les files peuvent être réparties, priorisées, gérées par classes ou affectées par les retransmissions. Utiliser ce modèle comme aide de raisonnement, pas comme prédiction exacte de production.

---

## 2. Configuration et pratique

### 2.1 Principes de configuration en environnement de production

Les exemples ci-dessous sont des patrons de raisonnement et doivent être adaptés au modèle de routeur, à la version IOS/IOS XE, aux capacités du fournisseur et à la politique de l'organisation. Ne copie pas une règle de mitigation en production sans valider la syntaxe, la portée, les interactions avec les autres politiques et les conséquences sur le trafic légitime.

La première étape consiste à établir un état de référence :
- interfaces, débits, erreurs et drops ;
- routes actives, voisins BGP, préfixes annoncés et reçus ;
- CPU, mémoire, buffers, table d'état et ressources matérielles ;
- métriques de service et tests synthétiques ;
- changements de configuration récents ;
- chemin de gestion et accès de secours.

### 2.2 Diagnostic initial Cisco IOS / IOS XE

```text
show interfaces
show interfaces counters errors
show processes cpu sorted
show memory statistics
show ip route
show ip bgp summary
show ip bgp
show logging
show access-lists
show platform hardware qfp active statistics drop
```

Toutes les commandes ne sont pas disponibles sur toutes les plateformes. La commande QFP, par exemple, est propre à certaines familles IOS XE. Vérifier la documentation correspondant au matériel avant de l'utiliser. Capturer les compteurs à plusieurs instants afin de calculer un delta : un compteur cumulatif élevé ne prouve pas à lui seul qu'un incident est en cours.

Sur une plateforme qui supporte les flux, utiliser un export NetFlow/IPFIX correctement dimensionné. Le taux d'échantillonnage doit être documenté : un échantillonnage réduit le coût, mais peut manquer les microbursts et biaiser l'estimation des petits flux. La télémétrie doit être exportée vers une infrastructure qui n'est pas elle-même dépendante du service attaqué.

### 2.3 Exemple de protection du plan de contrôle

La protection du plan de contrôle (CoPP/CPPr selon la plateforme) vise les paquets destinés au routeur lui-même, par exemple certaines catégories de trafic de routage ou d'administration. Elle ne remplace pas la mitigation du trafic transitant vers un serveur. Une politique trop agressive peut interrompre les sessions BGP, les protocoles de voisinage ou les opérations d'administration.

Avant d'appliquer CoPP :
1. inventorier les protocoles réellement nécessaires ;
2. mesurer les profils normaux et les pointes légitimes ;
3. classer les catégories de trafic de contrôle ;
4. prévoir des seuils, des compteurs et une période d'observation ;
5. tester les scénarios de convergence et de perte d'un voisin ;
6. confirmer l'accès de gestion de secours.

Exemple conceptuel de structure, à adapter à la syntaxe exacte de la plateforme :

```text
class-map match-any CONTROL-PLANE-CRITICAL
 match protocol bgp
!
policy-map CONTROL-PLANE-POLICY
 class CONTROL-PLANE-CRITICAL
  police <débit-validé> conform-action transmit exceed-action drop
 class class-default
  police <débit-validé> conform-action transmit exceed-action drop
!
control-plane
 service-policy input CONTROL-PLANE-POLICY
```

Les valeurs entre chevrons sont des paramètres à déterminer à partir des mesures ; ce bloc n'est pas prêt à être collé tel quel. Selon l'équipement, la syntaxe de classification peut différer et `match protocol bgp` peut ne pas être disponible. L'expert vérifie les compteurs par classe et observe l'effet sur les sessions de routage avant de considérer la politique comme stable.

> **Danger :** Une mauvaise limite CoPP peut transformer un pic de trafic en perte de voisinage BGP, en instabilité de routage ou en perte d'accès distant. Toute modification du plan de contrôle doit prévoir un accès hors bande, une fenêtre d'observation et une procédure de retour arrière.

### 2.4 ACL et filtrage d'entrée

Le filtrage anti-spoofing limite l'arrivée de paquets dont l'adresse source ne devrait pas être observée sur l'interface concernée. Le filtrage doit respecter le rôle de l'interface : une règle correcte pour un accès client peut être incorrecte pour un transit ou un lien avec des préfixes multiples. Les listes de contrôle doivent être revues avec les équipes réseau et sécurité.

Exemple pédagogique d'ACL nommée :

```text
ip access-list extended EDGE-INGRESS-REVIEW
 remark Exemple a adapter apres inventaire des flux legitimes
 permit ip <prefixes-sources-autorises> <wildcard> any
 deny ip any any log
!
interface <interface-entree>
 ip access-group EDGE-INGRESS-REVIEW in
```

Les éléments entre chevrons sont des placeholders, pas des commandes littérales. Une ACL réelle doit préserver les protocoles et les sources nécessaires, et la journalisation d'un volume élevé peut saturer CPU, mémoire ou stockage de logs. Il faut mesurer le coût des logs et éviter de générer un événement pour chaque paquet d'un flood. Des compteurs, des échantillons ou des agrégations peuvent être plus appropriés.

### 2.5 RTBH : procédure plutôt que commande isolée

Une procédure RTBH doit vérifier au minimum :
- le préfixe exact à blackholer ;
- l'autorité qui valide la demande ;
- la communauté et le next-hop prévus ;
- la politique d'import/export ;
- la propagation attendue chez les voisins ;
- la confirmation que le trafic vers la cible diminue ;
- la durée maximale et la procédure de retrait.

La configuration précise dépend du design BGP. Ne pas inventer une communauté universelle : les communautés RTBH sont définies par chaque opérateur ou organisation. Avant de déployer, tester avec un préfixe de laboratoire et vérifier les annonces depuis les routeurs concernés. Un blackhole est destructif pour la disponibilité de la cible ; il peut être préférable de détourner le trafic vers un scrubbing lorsque la continuité du service est prioritaire.

### 2.6 FlowSpec : validation et retrait

Les règles FlowSpec peuvent matcher plusieurs champs selon l'implémentation : préfixes source/destination, protocole, ports, indicateurs TCP ou autres composants supportés. La validation doit garantir que les annonces ne dépassent pas le périmètre autorisé. Il faut également tester la priorité entre règles et les capacités matérielles.

Checklist d'une règle :
- correspondance minimale nécessaire ;
- impact sur trafic légitime estimé ;
- approbation et ticket d'incident ;
- routeur(s) et périmètre concernés ;
- expiration ou rappel de revue ;
- mesure de l'effet et du taux de faux positifs ;
- commande ou mécanisme de retrait connu avant activation.

> **Astuce :** Conserve un journal d'état « avant / pendant / après » pour chaque action de mitigation. Cela permet de distinguer une amélioration due à la règle, la fin naturelle d'un pic ou un changement de route simultané.

### 2.7 Protection applicative : limites, quotas et timeouts

Un proxy applicatif doit limiter les ressources consommées par une requête. Les paramètres de timeout, de taille de corps, de nombre de connexions, de concurrence et de taille des files doivent être cohérents avec les usages légitimes. Des valeurs trop basses peuvent casser les uploads, les connexions mobiles ou les requêtes lentes ; des valeurs trop élevées favorisent l'épuisement des ressources.

Exemple Nginx illustratif :

```nginx
http {
    limit_req_zone $binary_remote_addr zone=per_ip:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;

    server {
        location /api/ {
            limit_req zone=per_ip burst=20 nodelay;
            limit_conn conn_per_ip 20;

            client_header_timeout 10s;
            client_body_timeout 15s;
            send_timeout 15s;
            proxy_connect_timeout 3s;
            proxy_read_timeout 20s;
            proxy_send_timeout 20s;

            proxy_pass http://application_pool;
        }
    }
}
```

Cet exemple n'est pas un profil universel de production. Le taux de 10 requêtes/s et les limites de connexions doivent être adaptés au trafic réel, à la route et à l'identité. Une limite basée uniquement sur l'IP peut pénaliser les utilisateurs derrière un NAT ; la clé doit être choisie avec soin si l'identité authentifiée est disponible. Ne configure pas de confiance aveugle dans `X-Forwarded-For` : n'accepter cette information que depuis des proxies connus et correctement configurés.

### 2.8 Observabilité des métriques et alertes

Créer des tableaux de bord séparés par couche et un tableau de synthèse de l'expérience client. Les alertes doivent préciser le signal, le seuil, la fenêtre temporelle, l'impact attendu, le propriétaire et l'action recommandée. Une alerte « trafic élevé » sans contexte ne suffit pas.

Exemples de corrélations :
- interface ingress en hausse + pertes en sortie + latence synthétique en hausse : possible saturation réseau ;
- débit normal + CPU TLS élevé + handshakes/s en hausse : possible attaque protocolaire ou changement client ;
- requêtes/s modérées + p99 très élevé + pool DB saturé : possible endpoint coûteux ;
- rejets WAF en hausse + taux de succès stable : mitigation peut être efficace ;
- rejets WAF en hausse + taux de succès client en baisse : vérifier faux positifs ;
- trafic entrant normal mais origine inaccessible : vérifier DNS, routage, ACL, tunnel et dépendances.

### 2.9 Laboratoire : reproduire et observer sans générer de trafic hostile

Pour un laboratoire, utiliser des métriques synthétiques, des traces enregistrées ou un simulateur local plutôt que lancer un flood vers des systèmes réels. Le but est de comprendre les relations entre capacité, file, latence et rejet. Un test de charge autorisé doit être limité, planifié, isolé, avec un seuil d'arrêt automatique et une supervision de l'équipe responsable.

Scénario de laboratoire :
1. établir une baseline de 40 requêtes/s légitimes ;
2. définir une capacité de service illustrative de 120 requêtes/s ;
3. augmenter graduellement la charge simulée ;
4. observer la file, les rejets, la latence et le taux de succès ;
5. appliquer une limite ou simuler une mitigation amont ;
6. vérifier la récupération après réduction du trafic ;
7. documenter les limites du modèle et les résultats.

Ne pas confondre un simulateur pédagogique et un test de performance réel. Les résultats réels dépendent des tailles de paquets, des distributions d'arrivée, des retransmissions, du protocole, du matériel et des comportements clients.

### 2.10 Runbook d'incident de niveau expert

**Phase A — Qualification**
- identifier les services et les régions touchés ;
- confirmer l'heure de début et les changements récents ;
- vérifier la qualité des données et la synchronisation des horloges ;
- distinguer saturation du lien, des paquets, de l'état, du TLS ou de l'application ;
- ouvrir un canal d'incident et nommer un responsable de décision.

**Phase B — Stabilisation**
- protéger l'accès de gestion et la collecte de preuves ;
- contacter les opérateurs ou le fournisseur de mitigation si la saturation est amont ;
- appliquer d'abord les mesures réversibles et ciblées ;
- préserver les endpoints et parcours critiques ;
- éviter les changements multiples non mesurés.

**Phase C — Mesure**
- suivre les métriques avant/après ;
- vérifier le taux de succès de clients synthétiques depuis plusieurs réseaux ;
- surveiller les faux positifs et les dépendances ;
- vérifier l'état des routes, tunnels, sessions et compteurs ;
- ajuster une variable à la fois lorsque c'est possible.

**Phase D — Retour à la normale**
- retirer les mesures temporaires dans l'ordre convenu ;
- vérifier que les annonces et politiques ont été supprimées partout ;
- restaurer les quotas ou services désactivés ;
- confirmer les métriques et la qualité de service ;
- préserver les logs et chronologies pour le post-mortem.

### 2.11 Exemple de matrice de décision

| Observation | Hypothèse prioritaire | Première action | Action à éviter sans validation |
|---|---|---|---|
| Lien d'entrée saturé, service inaccessible | volume supérieur à la capacité amont | contacter transit/scrubbing, confirmer destination | filtrage uniquement sur le serveur |
| CPU routeur élevé, BGP instable | pression sur plan de contrôle ou paquet-per-seconde | vérifier CoPP, CPU et classes de trafic | appliquer un policer arbitraire |
| RPS élevé, cache hit faible | attaque applicative ou changement de contenu | examiner routes, identité et cache | bloquer une région entière immédiatement |
| Tunnels de scrubbing saturés | capacité d'encapsulation insuffisante | vérifier capacité, MTU et retour | augmenter les annonces sans capacité validée |
| Rejets élevés et succès client en baisse | faux positifs ou règle trop large | réduire la portée et comparer les traces | empiler de nouvelles règles non testées |
| Télémétrie absente | panne de collecte ou perte de gestion | restaurer la visibilité, réduire l'automatisation risquée | considérer l'absence de métriques comme absence d'attaque |

---

## 3. Dépannage et sécurité

### 3.1 Méthode de dépannage structurée

Un incident DDoS complexe demande de séparer les symptômes, les hypothèses et les faits confirmés. Construire une chronologie commune : début du trafic anormal, changements de routes, alertes de capacité, dégradation des services, actions prises et effet observé. Utiliser des horloges synchronisées et noter les écarts entre les systèmes.

Procéder du plus large au plus précis :
1. confirmer l'impact client avec des sondes indépendantes ;
2. déterminer le premier point où la perte ou la latence apparaît ;
3. comparer les compteurs d'entrée et de sortie ;
4. identifier le type de ressource épuisée ;
5. confirmer ou écarter les changements légitimes ;
6. appliquer une mesure réversible ;
7. mesurer l'effet et les faux positifs ;
8. retirer ou conserver la mesure selon les critères de succès.

Ne pas tirer de conclusion à partir d'un seul graphe. Un trafic qui diminue peut signifier que la mitigation fonctionne, que l'attaquant a changé de vecteur ou que le lien est tellement saturé que les mesures ne remontent plus correctement.

### 3.2 Cas pratique 1 : le scrubbing est activé mais le service reste lent

**Symptômes :** le volume entrant sur le lien principal baisse après la diversion, mais la latence p99 reste élevée et le taux d'erreur applicatif ne revient pas à la normale.

**Hypothèses à tester :**
- le trafic malveillant résiduel coûteux passe encore ;
- le retour du trafic propre emprunte un chemin asymétrique ;
- le tunnel de réinjection est saturé ou provoque de la fragmentation ;
- la base de données ou un service partagé a déjà accumulé une file ;
- les clients réessaient trop agressivement ;
- le cache est froid après une modification de route.

**Procédure :**
1. comparer les métriques avant et après scrubbing, par couche ;
2. vérifier les pertes et compteurs d'encapsulation du tunnel ;
3. vérifier la MTU et le chemin aller-retour ;
4. corréler la latence avec les pools applicatifs et la base de données ;
5. tester un parcours client de bout en bout ;
6. ajuster la politique une seule fois, puis mesurer ;
7. documenter les symptômes qui persistent malgré la baisse volumétrique.

**Conclusion possible :** la diversion protège le lien, mais ne résout pas nécessairement la pression déjà présente dans l'application. La mitigation réseau et la récupération applicative sont deux tâches distinctes.

### 3.3 Cas pratique 2 : FlowSpec réduit l'attaque mais bloque des clients

**Symptômes :** le trafic baisse nettement, mais certains clients ou réseaux ne peuvent plus joindre le service.

**Analyse :**
- vérifier les champs matchés par la règle ;
- vérifier si le port ou protocole est partagé avec un usage légitime ;
- vérifier l'ordre de priorité et les interactions avec les autres règles ;
- analyser la répartition des rejets par préfixe, ASN, protocole et route ;
- confirmer que la règle a été distribuée uniquement aux routeurs attendus.

**Correction :** retirer ou restreindre la règle, tester une correspondance plus précise et mesurer les rejets. Ne pas résoudre un faux positif en ajoutant une exception très large sans analyse : les exceptions peuvent devenir une voie de contournement.

**Prévention :** chaque règle doit être associée à un ticket, un propriétaire, une date de révision, une métrique d'effet et une méthode de retrait testée.

### 3.4 Cas pratique 3 : le service DNS est disponible mais l'application paraît hors ligne

Vérifier successivement la résolution depuis plusieurs résolveurs, les réponses autoritatives, les TTL, la cohérence des enregistrements, les routes vers les adresses retournées, le certificat TLS, puis le service HTTP. Une propagation de changements DNS ou une divergence entre les sites Anycast peut rendre le problème intermittent. DNSSEC, réponses tronquées ou échec du fallback TCP peuvent également affecter certaines catégories de clients.

Ne pas vider tous les caches ou modifier les TTL à l'aveugle pendant un incident. Les modifications de DNS ont une dynamique temporelle : les caches déjà chargés ne se comportent pas tous de la même façon. Conserver les résultats des requêtes, les horodatages et les points de mesure.

### 3.5 Fausse mitigation : les métriques s'améliorent, les clients échouent

Un compteur de paquets rejetés qui augmente peut sembler confirmer l'efficacité d'une règle. Mais si le taux de succès synthétique baisse, il faut considérer la possibilité d'un faux positif. Croiser les rejets avec les sessions légitimes, les logs WAF, les codes d'erreur et les tests depuis des réseaux variés.

Établir des critères de succès à l'avance. Par exemple, la baisse de latence ne doit pas être obtenue au prix d'une chute importante du taux de succès. Les objectifs exacts sont propres au service et doivent être convenus avec les propriétaires métiers. Si le compromis est inacceptable, réduire la portée de la mitigation et demander une capacité d'absorption plus grande plutôt que de bloquer arbitrairement davantage de clients.

### 3.6 Risques de sécurité liés aux outils de mitigation

Les systèmes d'orchestration peuvent posséder des privilèges élevés sur BGP, les ACL, les WAF et les fournisseurs. Ils doivent être traités comme une surface critique :
- authentification forte et autorisation minimale ;
- séparation entre approbation et exécution pour les actions destructives ;
- secrets de fournisseurs stockés dans un coffre adapté ;
- journalisation append-only ou protégée contre la modification ;
- restrictions de préfixes, ports et durées ;
- validation de l'entrée et protection contre l'injection de commandes ;
- test de retrait et plan de secours si l'orchestrateur est indisponible.

Le système doit échouer de façon sûre. Si la télémétrie est absente ou incohérente, il ne doit pas inventer une confiance élevée. Si un fournisseur ne répond plus, le système doit alerter et suivre la procédure manuelle plutôt que d'appliquer une succession de changements de routage non contrôlés.

### 3.7 Risque d'amplification par les retries et les dépendances

Un incident réseau peut provoquer des retries applicatifs synchronisés, qui augmentent encore la charge. Les clients et services internes doivent utiliser un backoff exponentiel avec jitter, des délais d'expiration cohérents, des limites de concurrence et des circuits breakers. Une requête qui a échoué ne doit pas être relancée indéfiniment sans budget de retry.

Les appels internes sont eux aussi une source de surcharge. Si un endpoint provoque cinq appels en base de données et que le client le réessaie quatre fois, la charge en aval peut être multipliée rapidement. Le budget de requête doit être propagé ou appliqué à chaque dépendance, et les opérations idempotentes doivent être distinguées des opérations qui ne peuvent pas être répétées sans risque.

### 3.8 Protéger les preuves et la chronologie

Pendant une attaque, conserver les éléments nécessaires à l'analyse sans saturer les systèmes de logs. Les données peuvent inclure :
- compteurs d'interfaces et de files ;
- snapshots de routes et de politiques ;
- agrégats NetFlow/IPFIX ;
- échantillons de logs pare-feu, WAF et application ;
- événements de changement et décisions d'orchestration ;
- mesures synthétiques depuis plusieurs régions ;
- horodatages et état des fournisseurs.

Respecter les règles de confidentialité et de rétention. Éviter la collecte disproportionnée de données personnelles. Les journaux doivent être accessibles aux personnes qui gèrent l'incident, mais protégés contre les modifications et les accès non autorisés.

### 3.9 Exercices de table et validation régulière

Un plan DDoS n'est crédible que s'il a été testé. Les exercices doivent inclure :
- attaque volumétrique dépassant la capacité du transit ;
- attaque applicative à faible débit mais à fort coût ;
- panne du fournisseur de scrubbing ;
- tunnel de réinjection saturé ;
- règle FlowSpec trop large ;
- perte de télémétrie pendant la décision ;
- indisponibilité de l'accès de gestion principal ;
- retrait incomplet d'une annonce BGP.

Pour chaque exercice, définir les rôles, les critères d'arrêt, les signaux de réussite, les communications, le plan de retour et la collecte des preuves. Les tests de charge actifs doivent être autorisés, isolés et limités ; les exercices de table peuvent tester la coordination sans générer de trafic.

### 3.10 Checklist de préparation opérationnelle

- [ ] Inventaire des services, propriétaires, dépendances et objectifs de disponibilité à jour.
- [ ] Capacités connues en bit/s, pps, nouvelles connexions/s, TLS/s et RPS.
- [ ] Contacts d'escalade des opérateurs et fournisseurs vérifiés.
- [ ] Préfixes et mécanismes de diversion documentés et validés.
- [ ] Contrôles d'import BGP, FlowSpec et RTBH testés.
- [ ] Accès de gestion hors bande ou procédure d'accès de secours vérifiés.
- [ ] Tableau de bord de télémétrie disponible hors du chemin de service attaqué.
- [ ] Sondes synthétiques indépendantes et parcours clients critiques définis.
- [ ] Runbook, critères de succès et procédure de retrait disponibles.
- [ ] Post-mortem et conservation des preuves intégrés au processus d'incident.

### 3.11 Pièges avancés à éviter

> **Piège :** Confondre la capacité du lien avec la capacité du service. Le débit peut rester modéré alors que la table d'état, le CPU TLS ou la base de données est saturé.

> **Piège :** Déployer une règle sur une métrique unique. Un pic de RPS ou de SYN n'est pas une preuve suffisante pour bloquer une population entière.

> **Piège :** Laisser une mesure temporaire sans date de retrait. Les règles d'urgence oubliées peuvent provoquer une panne des semaines plus tard.

> **Piège :** Faire dépendre la télémétrie, l'administration et la mitigation du même lien public qui subit l'attaque.

> **Danger :** Une annonce BGP incorrecte, une règle FlowSpec trop large ou un blackhole mal ciblé peut rendre injoignables des préfixes légitimes au-delà du service attaqué. Vérifie la portée et le retrait avant toute action.

---

## Points à retenir

- Une défense DDoS experte est une architecture multicouche, pas une règle unique.
- Mesure séparément bit/s, pps, connexions/s, TLS/s, RPS, latence, erreurs et capacité d'état.
- Identifie le premier goulot d'étranglement ; filtrer au serveur ne sauve pas un lien déjà saturé.
- Sépare les plans de données, de contrôle et de gestion et garde un accès d'urgence.
- RTBH, FlowSpec, Anycast et scrubbing sont puissants mais exigent validation, limites et retrait contrôlé.
- Protège l'origine derrière le CDN et adapte les limites au coût réel des routes et aux identités.
- Une mitigation réussie se mesure par l'expérience client, pas seulement par le nombre de paquets rejetés.
- L'automatisation doit être réversible, journalisée, limitée en fréquence et prudente lorsque la télémétrie est dégradée.
- Les exercices et les tests de retrait sont aussi importants que le déclenchement de la mitigation.
- Les schémas SVG de ce cours sont illustratifs ; ils n'exécutent aucun trafic réseau et ne remplacent pas un test autorisé.

### Références techniques

- Cisco, documentation IOS XE — QoS, Control Plane Policing, ACL, BGP et télémétrie : https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe/products-documentation-roadmaps-list.html
- RFC 5635 — Remote Triggered Black Hole Filtering with Unicast Reverse Path Forwarding (uRPF).
- RFC 7999 — BLACKHOLE BGP Community.
- RFC 8955 — Dissemination of Flow Specification Rules.
- RFC 8956 — Dissemination of Flow Specification Rules for IPv6.
- RFC 7454 — BGP Operations and Security.
- RFC 3704 — Ingress Filtering for Multihomed Networks.
- RFC 2827 / BCP 38 — Network Ingress Filtering.
- RFC 4732 — Internet Denial-of-Service Considerations.
- RFC 8484 — DNS Queries over HTTPS (DoH), pour le contexte de transport des requêtes DNS.
- OWASP, Denial of Service Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
- Cloudflare Learning Center, DDoS : https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/
- NGINX documentation, ngx_http_limit_req_module : https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- IETF BCP 38, filtrage des adresses sources usurpées.
