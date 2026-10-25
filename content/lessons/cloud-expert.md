<style>
.cloude-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.25rem 0;padding:.75rem;border:1px solid #1b3854;border-radius:14px;background:#07111e;color:#e5edf8;box-sizing:border-box}
.cloude-diagram svg{display:block;width:100%;height:auto;min-width:720px}
@media(max-width:720px){.cloude-diagram svg{min-width:720px}}
@media(prefers-reduced-motion:reduce){.cloude-diagram *{animation:none!important}}
</style>

# Cloud Networking — Niveau Expert

**Niveau :** Expert  
**Prérequis :** conception multi-VPC/VNet, CIDR, routage statique et BGP, groupes de sécurité/ACL, VPN, DNS hybride, endpoints privés, équilibrage de charge, observabilité et IaC.  
**Objectif :** concevoir, gouverner, sécuriser et exploiter une architecture réseau cloud d’entreprise à grande échelle, y compris les environnements multi-comptes, multi-régions, hybrides, Kubernetes et multi-cloud.

Le niveau expert ne consiste pas à ajouter le plus grand nombre de services réseau. Il consiste à bâtir une architecture dont les flux sont explicites, les frontières de confiance justifiées, les chemins de panne compris, les changements réversibles et le coût prévisible. Une bonne architecture doit fonctionner en régime normal, mais aussi rester compréhensible lors d’une panne de région, d’une fuite de routes, d’une erreur DNS, d’une compromission d’identité ou d’un déploiement défectueux.

Ce cours présente des modèles génériques que l’on retrouve dans les principaux clouds publics. Les noms et comportements exacts ne sont pas interchangeables : AWS Transit Gateway et Cloud WAN, Azure Virtual WAN, ainsi que Google Cloud Network Connectivity Center offrent des capacités de connectivité à grande échelle, mais leurs options, limites, modes de propagation de routes et modèles de facturation diffèrent. Toute conception de production doit être validée dans la documentation du fournisseur, de la région et du service réellement utilisés.

> **Analogie :** au niveau débutant, tu as appris à relier quelques bâtiments ; au niveau intermédiaire, à organiser le trafic d’une ville. Au niveau expert, tu conçois le réseau de transport de plusieurs métropoles : règles de circulation, interconnexions internationales, contrôle d’accès, capacité de secours, surveillance et procédures pour continuer à fonctionner lorsqu’un pont ou un centre de contrôle tombe en panne.


## 1. Le travail d’architecture avant le choix d’un service

### 1.1 Partir des flux métier

Ne commence pas par « faut-il utiliser Transit Gateway ? » ou « faut-il un pare-feu central ? ». Commence par définir les communications nécessaires. Pour chaque flux, consigne :
- **Initiateur et destination** : utilisateur, service, cluster, compte, région, site distant ;
- **Protocole et port** : TCP, UDP, ICMP, HTTP(S), DNS, protocoles spécifiques ;
- **Sens d’initiation** : qui ouvre la connexion et si le retour est attendu ;
- **Identité** : utilisateur, compte de service, workload identity, certificat ou rôle ;
- **Classification des données** : publique, interne, confidentielle, réglementée ;
- **Criticité** : latence, disponibilité, volume, débit et tolérance à la perte ;
- **Propriétaire** : équipe qui approuve, observe et dépanne le flux ;
- **Preuve** : journaux, métriques, test ou règle d’autorisation permettant de vérifier son fonctionnement.

Une matrice de flux permet de détecter les accès transversaux involontaires avant qu’ils deviennent des dépendances en production. Elle constitue aussi une base de tests de sécurité automatisés.

### 1.2 Transformer la matrice en modèle de connectivité

Une méthode robuste sépare quatre décisions :
1. **Topologie** : maillage, hub-and-spoke, WAN managé, connectivité dédiée ou combinaison.
2. **Routage** : qui annonce quelles plages, où les routes sont propagées, quelle sortie est préférée.
3. **Filtrage** : où les flux sont autorisés ou refusés, et si les politiques suivent une identité.
4. **Observabilité** : comment prouver quel chemin a été utilisé, pourquoi un paquet a été accepté/refusé et quel composant a échoué.

Un diagramme n’est pas une configuration. Un dessin montre l’intention ; les routes effectives, les règles attachées et les tests de trafic prouvent le comportement réel.

### 1.3 Principes à décider tôt

- **Adressage durable** : plages sans chevauchement, réserves par région, sous-réseau, cluster et futur site.
- **Segmentation par environnement** : production, développement, test et données sensibles.
- **Connectivité minimale** : aucun transit implicite entre environnements qui n’en ont pas besoin.
- **Sortie explicite** : les flux externes doivent avoir un chemin et une politique identifiables.
- **DNS intentionnel** : le nom résout vers la bonne cible selon le réseau et l’identité du consommateur.
- **Haute disponibilité mesurée** : un chemin de secours doit avoir la capacité utile et être testé.
- **Traçabilité** : chaque changement réseau doit être attribuable, révisable et réversible.
- **Coût par flux** : NAT, transfert inter-région, inspection, endpoints et logs font partie du design.

### 1.4 Limiter le rayon d’impact

Le « blast radius » est l’ensemble des ressources pouvant être affectées par une panne, une erreur ou une compromission. Des comptes/projets distincts, des plans d’adressage séparés, des rôles d’administration, des domaines de routage et des politiques par environnement peuvent réduire ce rayon. À l’inverse, un hub unique mal protégé ou une route par défaut propagée partout peut devenir un point de panne ou d’accès transversal.

L’objectif n’est pas d’isoler chaque ressource au point de rendre les opérations impossibles. Il s’agit de rendre les dépendances explicites, les accès proportionnés et les pannes localisées.

## 2. Plan d’adressage à grande échelle et IPAM

### 2.1 Concevoir une hiérarchie de plages

Une convention d’adressage doit être assez stable pour que les équipes puissent comprendre une route à partir de son préfixe. Une organisation peut réserver des blocs par région, domaine métier, environnement ou type de réseau. Il n’existe pas une convention universelle : le plus important est d’éviter les chevauchements et de formaliser l’allocation.

Exemple conceptuel :

| Domaine | Plage illustrative | Règle |
|---|---|---|
| Région A, production | `10.64.0.0/12` | Sous-blocs alloués aux workloads |
| Région A, non-production | `10.80.0.0/12` | Isolation d’environnement |
| Région B, production | `10.96.0.0/12` | Bloc réservé à l’expansion régionale |
| Services partagés | `10.112.0.0/16` | DNS, sécurité, supervision |
| Réseaux locaux | `172.20.0.0/16` | Inventoriés avant toute connexion |
| Laboratoires isolés | Bloc distinct validé | Pas de peering par défaut |

Ces plages servent uniquement d’exemple. Les plages RFC 1918 sont privées, mais elles peuvent déjà être utilisées par un partenaire, un VPN utilisateur, des conteneurs ou une filiale. Le statut « privé » ne rend pas une plage automatiquement disponible.

### 2.2 IPAM : allocation, inventaire et audit

Un système de gestion des adresses IP (IPAM) doit répondre à des questions opérationnelles : quelle équipe possède le préfixe, à quel environnement appartient-il, quels réseaux y sont routés, quelles réserves restent disponibles, et qui a approuvé une allocation ?

Un processus d’allocation mature comprend :
1. inventaire automatique des réseaux cloud et locaux ;
2. contrôle du chevauchement avant création ;
3. attribution d’un bloc à une équipe, une région et un environnement ;
4. génération des sous-réseaux depuis le plan validé ;
5. synchronisation des données IPAM avec IaC et CMDB si elle existe ;
6. détection périodique des réseaux non déclarés et des dérives ;
7. procédure de renumérotation avec dépendances et retour arrière.

L’IPAM doit inclure les plages de pods/services Kubernetes, les VPN utilisateurs, les réseaux des acquisitions et les plages de fournisseurs lorsque celles-ci doivent être jointes. Les oublier crée des conflits tardifs, souvent au moment d’une migration critique.

### 2.3 Agrégation des routes et résumé des préfixes

L’agrégation résume plusieurs routes plus spécifiques en un préfixe plus large. Elle peut réduire le nombre de routes propagées, mais un résumé incorrect attire du trafic vers un réseau qui ne possède pas réellement toute la plage annoncée.

Exemple : annoncer `10.64.0.0/12` n’est sûr que si l’annonceur peut acheminer correctement toutes les destinations que ce résumé prétend couvrir, ou si la politique est conçue pour rejeter/traiter correctement les portions non utilisées. L’agrégation réduit la taille des tables, mais elle peut masquer une route manquante si elle est trop large.

### 2.4 Chevauchements entre CIDR, pods et services

Les chevauchements entre les plages VPC/VNet, sites locaux, pods, services Kubernetes, VPN utilisateurs et partenaires doivent être détectés avant la mise en service. L’encapsulation ou la traduction peuvent offrir une solution temporaire, mais créent des limites de visibilité et de dépannage. Le meilleur remède est souvent une renumérotation planifiée avant que les dépendances deviennent nombreuses.

### Schéma 1 — IPAM et flux d’approbation d’une allocation

<div class="cloude-diagram">
<svg viewBox="0 0 1000 350" width="100%" role="img" aria-label="Processus IPAM de demande, contrôle de chevauchement, approbation et publication du CIDR avec flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce1" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce1g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.ce1t{font:14px Arial,sans-serif;fill:#e5edf8}.ce1s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce1f{fill:none;stroke:#38bdf8;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce1);animation:ce1dash 1.6s linear infinite}@keyframes ce1dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="110" width="165" height="90" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="102" y="140" class="ce1t" text-anchor="middle" font-weight="bold">Équipe applicative</text><text x="102" y="163" class="ce1s" text-anchor="middle">Demande de plage</text><text x="102" y="182" class="ce1s" text-anchor="middle">Région / usage</text>
<rect x="235" y="110" width="175" height="90" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.6"/><text x="322" y="140" class="ce1t" text-anchor="middle" font-weight="bold">Service IPAM</text><text x="322" y="163" class="ce1s" text-anchor="middle">Inventaire global</text><text x="322" y="182" class="ce1s" text-anchor="middle">Réserve hiérarchique</text>
<path d="M185 155 H230" class="ce1f" marker-end="url(#ce1)"/>
<rect x="460" y="110" width="175" height="90" rx="12" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.6"/><text x="547" y="140" class="ce1t" text-anchor="middle" font-weight="bold">Contrôles</text><text x="547" y="163" class="ce1s" text-anchor="middle">Chevauchement</text><text x="547" y="182" class="ce1s" text-anchor="middle">Quota / politique</text><path d="M410 155 H455" class="ce1f" marker-end="url(#ce1)"/>
<rect x="685" y="110" width="140" height="90" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="755" y="140" class="ce1t" text-anchor="middle" font-weight="bold">Approbation</text><text x="755" y="163" class="ce1s" text-anchor="middle">Propriétaire</text><text x="755" y="182" class="ce1s" text-anchor="middle">Réseau / sécurité</text><path d="M635 155 H680" class="ce1f" marker-end="url(#ce1)"/>
<rect x="865" y="110" width="115" height="90" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="922" y="140" class="ce1t" text-anchor="middle" font-weight="bold">Publication</text><text x="922" y="163" class="ce1s" text-anchor="middle">IaC / DNS</text><text x="922" y="182" class="ce1s" text-anchor="middle">Inventaire</text><path d="M825 155 H860" class="ce1f" marker-end="url(#ce1)"/>
<path d="M547 200 V260 H322 V205" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#ce1)"/><text x="430" y="284" class="ce1s" text-anchor="middle">Si conflit : correction de la demande, aucune allocation</text>
<text x="20" y="325" class="ce1s">La flèche représente le processus d’approbation ; le préfixe n’est utilisable qu’après publication cohérente dans les outils et configurations.</text>
</svg>
</div>

## 3. Routage et transit à l’échelle de l’entreprise

### 3.1 Choisir une topologie selon le trafic

Les topologies communes incluent :
- **Maillage complet** : chemins directs nombreux, mais explosion des relations à mesure que le nombre de réseaux augmente.
- **Hub-and-spoke** : un hub connecte les spokes ; simple pour centraliser des services, mais risque de concentration.
- **Transit managé** : un service gère de nombreuses connexions et tables de routage.
- **WAN global** : connectivité entre régions et sites avec segmentation et politiques centralisées, selon les capacités du fournisseur.
- **Topologie hybride** : mélange de peerings directs, hubs régionaux et services de transit.

Le choix doit suivre la matrice de flux. Si la majorité des spokes doit communiquer entre eux, un hub est potentiellement adapté. Si des flux directs à faible latence sont exigés entre quelques réseaux, un peering ciblé peut être plus simple. Les modèles peuvent coexister, à condition que les routes et leurs préférences soient explicites.

### 3.2 Peering : connectivité directe ne signifie pas transit

Le peering entre deux réseaux virtuels permet généralement l’échange de trafic entre leurs préfixes annoncés ou pris en charge, sous réserve des politiques. Il ne transforme pas automatiquement l’un des réseaux en routeur pour les réseaux tiers. La transitivité, l’utilisation de passerelles partagées et les exceptions varient d’un fournisseur à l’autre.

Ne suppose pas que si A rejoint B et B rejoint C alors A peut traverser B pour atteindre C. Vérifie les routes effectives et la fonctionnalité de transit explicitement documentée.

### 3.3 Domaines de routage et segmentation logique

Les grands hubs managés peuvent proposer plusieurs tables ou domaines de routage. Ils servent à isoler certains groupes de réseaux : production, test, partenaires, services communs, inspection ou réseaux réglementés.

Une table de routage distincte n’est pas à elle seule une frontière de sécurité. Elle contrôle le chemin réseau, alors que les règles de pare-feu et d’identité contrôlent l’autorisation. Un design complet combine :
- tables de routage séparées ;
- propagation/association explicites des routes ;
- filtrage aux frontières pertinentes ;
- contrôle des annonces dynamiques ;
- logs et tests de chemins autorisés/interdits.

### 3.4 Route par défaut et évasion du chemin d’inspection

Une route par défaut propagée largement peut faire sortir des flux par une passerelle inattendue ou contourner un dispositif d’inspection. Les exceptions DNS, les endpoints privés et les plages de service peuvent aussi changer le chemin effectif. Fais une revue des routes réelles, pas uniquement du modèle IaC.

Les questions à poser sont :
- Qui peut annoncer une route par défaut ?
- Cette annonce traverse-t-elle les domaines de routage voulus ?
- Le trafic Internet sort-il régionalement ou via une inspection centrale ?
- Les ressources privées passent-elles par le NAT attendu ?
- Les flux intra-région ou vers les services natifs évitent-ils l’inspection requise ?
- Le retour suit-il le chemin compatible avec l’état des firewalls ?

### Schéma 2 — Transit central avec domaines séparés

<div class="cloude-diagram">
<svg viewBox="0 0 1000 470" width="100%" role="img" aria-label="Transit gateway avec tables de routage séparées pour production et test, sortie inspection et site local, flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce2b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce2g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><marker id="ce2y" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#fbbf24"/></marker><style>.ce2t{font:14px Arial,sans-serif;fill:#e5edf8}.ce2s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce2f{fill:none;stroke:#38bdf8;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce2b);animation:ce2dash 1.6s linear infinite}.ce2g{fill:none;stroke:#34d399;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce2g);animation:ce2dash 1.6s linear infinite}@keyframes ce2dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="25" y="45" width="220" height="95" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="135" y="75" class="ce2t" text-anchor="middle" font-weight="bold">VPC Prod</text><text x="135" y="98" class="ce2s" text-anchor="middle">10.64.0.0/16</text><text x="135" y="119" class="ce2s" text-anchor="middle">Routes domaine Prod</text>
<rect x="25" y="315" width="220" height="95" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="135" y="345" class="ce2t" text-anchor="middle" font-weight="bold">VPC Test</text><text x="135" y="368" class="ce2s" text-anchor="middle">10.80.0.0/16</text><text x="135" y="389" class="ce2s" text-anchor="middle">Routes domaine Test</text>
<rect x="340" y="95" width="315" height="270" rx="18" fill="#111d30" stroke="#a78bfa" stroke-width="2"/><text x="497" y="125" class="ce2t" text-anchor="middle" font-weight="bold">Hub de transit managé</text>
<rect x="370" y="150" width="255" height="75" rx="11" fill="#211d3a" stroke="#a78bfa" stroke-width="1.4"/><text x="497" y="179" class="ce2t" text-anchor="middle">Table / domaine PROD</text><text x="497" y="202" class="ce2s" text-anchor="middle">Routes strictement approuvées</text>
<rect x="370" y="250" width="255" height="75" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="497" y="279" class="ce2t" text-anchor="middle">Table / domaine TEST</text><text x="497" y="302" class="ce2s" text-anchor="middle">Séparé par politique</text>
<path d="M245 95 H285 V185 H365" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#ce2g)"/><path d="M245 362 H285 V287 H365" fill="none" stroke="#38bdf8" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#ce2b)"/>
<rect x="735" y="45" width="240" height="95" rx="12" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.6"/><text x="855" y="75" class="ce2t" text-anchor="middle" font-weight="bold">Inspection / FW</text><text x="855" y="98" class="ce2s" text-anchor="middle">Sortie contrôlée</text><text x="855" y="119" class="ce2s" text-anchor="middle">Journalisation</text>
<rect x="735" y="315" width="240" height="95" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="855" y="345" class="ce2t" text-anchor="middle" font-weight="bold">VPN / liaison dédiée</text><text x="855" y="368" class="ce2s" text-anchor="middle">Réseau d’entreprise</text><text x="855" y="389" class="ce2s" text-anchor="middle">Préfixes filtrés</text>
<path d="M655 170 H695 V95 H730" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#ce2y)"/><path d="M735 117 H700 V205 H660" fill="none" stroke="#fbbf24" stroke-width="2.2" marker-end="url(#ce2b)"/><path d="M655 290 H695 V362 H730" fill="none" stroke="#38bdf8" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#ce2b)"/><path d="M735 385 H700 V335 H660" fill="none" stroke="#38bdf8" stroke-width="2.2" marker-end="url(#ce2b)"/>
<text x="340" y="430" class="ce2s">Les routes et tables sont illustratives : la séparation des domaines doit être implémentée avec les fonctions du fournisseur.</text><text x="340" y="450" class="ce2s">Une table distincte ne suffit pas sans politiques de filtrage et vérification des routes effectives.</text>
</svg>
</div>

Ce schéma illustre une intention : la production et le test n’utilisent pas automatiquement les mêmes destinations. Les flèches indiquent les chemins logiques ; elles ne signifient pas que chaque flux est autorisé. Le hub et les domaines de routage réels dépendent du service choisi.

### 3.5 Choisir entre services managés et appliances virtuelles

Une appliance virtuelle (NVA) peut fournir des fonctions spécialisées : pare-feu, inspection TLS, IDS/IPS, routage avancé, filtrage d’URL ou connexion SD-WAN. Un service managé réduit une partie de l’exploitation, tandis qu’une appliance peut donner plus de contrôle et d’options. Cette comparaison n’est pas absolue : les services managés peuvent offrir des fonctions avancées et les appliances exigent un travail important de mise à jour, de capacité et de haute disponibilité.

Évalue :
- capacité soutenue et comportement en pointe ;
- nombre de sessions et nouvelles connexions par seconde ;
- latence ajoutée ;
- prise en charge des protocoles et IPv6 ;
- symétrie de routage et HA ;
- mises à jour, licences et support ;
- logs, API et intégration IaC ;
- modèle de facturation et coûts de données.

## 4. Inspection centralisée et sorties réseau

### 4.1 Trafic north-south et east-west

Le trafic **north-south** traverse une frontière entre un environnement et l’extérieur, par exemple Internet vers une application. Le trafic **east-west** circule entre composants internes ou réseaux cloud. Ces termes décrivent une orientation logique ; ils ne disent pas si le flux est sûr ou dangereux.

Les architectures historiques inspectaient principalement le trafic au périmètre. Dans les clouds, les charges sont distribuées et les communications internes peuvent s’étendre à plusieurs VPC, projets, comptes, clusters et régions. La visibilité des flux internes et l’application des politiques deviennent donc essentielles.

### 4.2 Forcer une sortie centrale : avantages et risques

La sortie centrale peut appliquer des politiques homogènes, simplifier les listes d’IP publiques et centraliser les logs. Elle augmente toutefois la dépendance au hub, le coût de transfert et parfois la latence. Une seule région de sortie peut devenir un goulot si les workloads d’autres régions doivent tout faire transiter par elle.

Une sortie régionale peut réduire la latence et le transfert inter-région, mais multiplie les points de configuration. Un compromis est d’utiliser des politiques centralisées et des points de sortie régionaux, avec une gouvernance et une télémétrie communes.

### 4.3 Exemptions et risques de contournement

Les endpoints privés, les réseaux de services, certaines communications de contrôle, le trafic de sauvegarde et les appels aux métadonnées peuvent suivre des chemins spéciaux. Documente ces exceptions et teste si elles sont réellement nécessaires. Les exceptions doivent avoir un propriétaire, une justification et des logs lorsque c’est approprié.

### Schéma 3 — Flux sortant avec inspection et retour symétrique

<div class="cloude-diagram">
<svg viewBox="0 0 1000 390" width="100%" role="img" aria-label="Flux sortant depuis VM privée via routeur, pare-feu, NAT et Internet, avec flèches de retour pour la session" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce3g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><marker id="ce3b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><style>.ce3t{font:14px Arial,sans-serif;fill:#e5edf8}.ce3s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce3f{fill:none;stroke:#34d399;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce3g);animation:ce3dash 1.5s linear infinite}@keyframes ce3dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="120" width="160" height="100" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="44" y="143" width="28" height="28" rx="3" fill="none" stroke="#34d399" stroke-width="2"/><path d="M44 151 H72 M50 160 H66" stroke="#34d399" stroke-width="1.5"/><text x="120" y="157" class="ce3t" text-anchor="middle" font-weight="bold">VM privée</text><text x="100" y="195" class="ce3s" text-anchor="middle">Source interne</text>
<rect x="235" y="120" width="155" height="100" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><path d="M258 146 H290 V178 H258 Z M264 152 H284 M264 160 H284" fill="none" stroke="#38bdf8" stroke-width="1.6"/><text x="330" y="154" class="ce3t" text-anchor="middle" font-weight="bold">Routeur</text><text x="310" y="192" class="ce3s" text-anchor="middle">Route effective</text>
<rect x="445" y="120" width="155" height="100" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.6"/><path d="M470 143 L495 133 L520 143 V175 L495 185 L470 175 Z M495 133 V185" fill="none" stroke="#c4b5fd" stroke-width="1.6"/><text x="548" y="154" class="ce3t" text-anchor="middle" font-weight="bold">Pare-feu</text><text x="522" y="192" class="ce3s" text-anchor="middle">Politique + état</text>
<rect x="655" y="120" width="140" height="100" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><path d="M683 153 H713 M698 138 V168 M683 153 L690 146 M683 153 L690 160 M713 153 L706 146 M713 153 L706 160" fill="none" stroke="#38bdf8" stroke-width="1.7"/><text x="747" y="181" class="ce3t" text-anchor="middle" font-weight="bold">NAT</text><text x="725" y="201" class="ce3s" text-anchor="middle">Traduction</text>
<rect x="850" y="120" width="130" height="100" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><circle cx="915" cy="153" r="18" fill="none" stroke="#38bdf8" stroke-width="1.7"/><path d="M897 153 H933 M915 135 C904 144 904 162 915 171 M915 135 C926 144 926 162 915 171" stroke="#38bdf8" stroke-width="1.5" fill="none"/><text x="915" y="190" class="ce3t" text-anchor="middle" font-weight="bold">Internet</text>
<path d="M180 155 H230" class="ce3f" marker-end="url(#ce3g)"/><path d="M390 155 H440" class="ce3f" marker-end="url(#ce3g)"/><path d="M600 155 H650" class="ce3f" marker-end="url(#ce3g)"/><path d="M795 155 H845" class="ce3f" marker-end="url(#ce3g)"/>
<path d="M850 200 H810 V280 H520 V225" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#ce3b)"/><text x="675" y="307" class="ce3s" text-anchor="middle">Réponse de la session : vérifier le suivi d’état et le chemin retour</text>
<text x="20" y="350" class="ce3s">Flux vert : connexion initiée depuis la VM vers l’extérieur. Bleu : retour lié à la session, selon le NAT et le pare-feu utilisés.</text><text x="20" y="371" class="ce3s">Si le retour contourne le pare-feu à état, la session peut échouer ou être moins inspectée que prévu.</text>
</svg>
</div>

Le chemin de retour affiché est schématique. Les détails NAT, les adresses source observées et le suivi d’état dépendent des produits. Teste la symétrie avant de déployer une inspection dans le chemin critique.

## 5. Architecture multi-régions et reprise après sinistre

### 5.1 Multi-zone n’est pas multi-région

La haute disponibilité multi-zone vise à tolérer la perte d’un domaine d’infrastructure dans une région. Le multi-région vise à limiter l’impact d’une panne plus large, d’une indisponibilité régionale ou d’un besoin de proximité géographique. Il introduit toutefois des problèmes supplémentaires :
- réplication des données et cohérence ;
- propagation DNS ;
- routage global vers la région active ;
- dépendances aux services managés régionaux ;
- identité, certificats et secrets répliqués ;
- coûts de trafic inter-région ;
- risques de divergence de configuration.

### 5.2 Actif-actif, actif-passif et active-active logique

- **Actif-passif** : une région traite les requêtes principales et une région secondaire se prépare à prendre le relais. La capacité de secours doit être suffisante, même si elle est réduite au repos.
- **Actif-actif** : plusieurs régions traitent des requêtes simultanément. Cela peut améliorer la proximité et la disponibilité, mais impose de maîtriser les données, les sessions, les écritures concurrentes et les dépendances régionales.
- **Actif-actif par composant** : certains services sont actifs partout, tandis que d’autres disposent d’un leader ou d’une région d’écriture. Le terme doit être précisé par couche plutôt que d’être appliqué à tout le système.

### 5.3 RTO et RPO

Le **RTO** (Recovery Time Objective) est le délai cible de reprise. Le **RPO** (Recovery Point Objective) est la perte de données maximale visée, exprimée en durée. Les valeurs découlent des objectifs métier, non du simple choix d’un service réseau.

Une bascule DNS peut sembler rapide, mais les caches, TTL, connexions persistantes et comportements clients retardent le déplacement réel du trafic. Le basculement du réseau doit donc être coordonné avec les services applicatifs, les données, les sessions et la supervision.

### 5.4 Réplication des routes et dépendances

Les routes entre régions doivent être explicitement conçues. Une interconnexion globale peut être redondante tout en ayant un point de défaillance dans le DNS, l’inspection centrale ou les identités. Il faut examiner le plan de contrôle, le plan de données et les systèmes d’exploitation.

Ne suppose pas qu’une route présente dans une région se propage automatiquement à l’autre. Vérifie les politiques d’import/export, les routes les plus spécifiques, les réseaux qui ne doivent pas être propagés et le comportement en cas de perte du hub ou du tunnel.

### Schéma 4 — Bascule régionale avec entrée globale

<div class="cloude-diagram">
<svg viewBox="0 0 1000 465" width="100%" role="img" aria-label="Clients vers DNS et répartiteur global, distribution vers région A principale et région B de reprise avec flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce4b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce4g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><marker id="ce4y" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#fbbf24"/></marker><style>.ce4t{font:14px Arial,sans-serif;fill:#e5edf8}.ce4s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce4f{fill:none;stroke:#38bdf8;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce4b);animation:ce4dash 1.5s linear infinite}.ce4g{fill:none;stroke:#34d399;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce4g);animation:ce4dash 1.5s linear infinite}@keyframes ce4dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="170" width="135" height="90" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="87" y="201" class="ce4t" text-anchor="middle" font-weight="bold">Clients</text><text x="87" y="225" class="ce4s" text-anchor="middle">Web / API</text>
<rect x="200" y="170" width="145" height="90" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.6"/><text x="272" y="199" class="ce4t" text-anchor="middle" font-weight="bold">DNS / GSLB</text><text x="272" y="222" class="ce4s" text-anchor="middle">Santé + politique</text><text x="272" y="242" class="ce4s" text-anchor="middle">Région choisie</text><path d="M155 214 H195" class="ce4f" marker-end="url(#ce4b)"/>
<rect x="410" y="35" width="550" height="165" rx="16" fill="#0a1727" stroke="#34d399" stroke-width="1.7"/><text x="685" y="61" class="ce4t" text-anchor="middle" font-weight="bold">Région A — Primaire</text><rect x="445" y="86" width="140" height="80" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="515" y="112" class="ce4t" text-anchor="middle">Load balancer</text><text x="515" y="135" class="ce4s" text-anchor="middle">Entrée régionale</text><rect x="630" y="86" width="290" height="80" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><text x="775" y="112" class="ce4t" text-anchor="middle">Workloads + données</text><text x="775" y="135" class="ce4s" text-anchor="middle">Région active</text><path d="M585 126 H625" class="ce4g" marker-end="url(#ce4g)"/>
<rect x="410" y="260" width="550" height="165" rx="16" fill="#0a1727" stroke="#fbbf24" stroke-width="1.7"/><text x="685" y="286" class="ce4t" text-anchor="middle" font-weight="bold">Région B — Secours / active selon design</text><rect x="445" y="311" width="140" height="80" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="515" y="337" class="ce4t" text-anchor="middle">Load balancer</text><text x="515" y="360" class="ce4s" text-anchor="middle">Entrée régionale</text><rect x="630" y="311" width="290" height="80" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.4"/><text x="775" y="337" class="ce4t" text-anchor="middle">Workloads + données</text><text x="775" y="360" class="ce4s" text-anchor="middle">Capacité de reprise</text><path d="M585 351 H625" class="ce4g" marker-end="url(#ce4g)"/>
<path d="M345 195 H375 V126 H440" class="ce4f" marker-end="url(#ce4b)"/><path d="M345 235 H375 V351 H440" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="8 6" marker-end="url(#ce4y)"/>
<text x="20" y="305" class="ce4s">La politique d’entrée peut préférer A</text><text x="20" y="325" class="ce4s">et n’envoyer vers B qu’en cas de</text><text x="20" y="345" class="ce4s">défaillance ou de stratégie répartie.</text><text x="20" y="395" class="ce4s">À tester : santé régionale, réplication DB,</text><text x="20" y="415" class="ce4s">TTL DNS, capacité de secours et retour à la normale.</text>
</svg>
</div>

Le diagramme simplifie l’entrée mondiale. Selon le produit, le routage global peut être fourni par DNS, anycast, un réseau global ou une combinaison. Chaque option possède des propriétés de cache et de convergence différentes.

### 5.5 Exercice de bascule

Un exercice sérieux doit vérifier :
- le signal qui déclenche la bascule ;
- le fait que le service dans la région secondaire soit réellement prêt ;
- la cohérence et le point de reprise des données ;
- les routes et politiques de sécurité ;
- les secrets, certificats et identités ;
- l’évolution DNS et le comportement des clients ;
- la capacité des ressources secondaires ;
- le processus de retour vers la région principale ;
- les preuves et métriques collectées ;
- les impacts sur les coûts pendant et après l’incident.

Ne fais pas de test de bascule en production sans autorisation, plan de communication, critères d’arrêt et capacité de retour arrière.

## 6. Sécurité Zero Trust au niveau réseau

### 6.1 Ne pas confondre emplacement et confiance

Une machine située dans un sous-réseau privé n’est pas automatiquement digne de confiance. Un réseau VPN n’accorde pas par définition le droit d’atteindre tous les services. L’architecture Zero Trust met l’accent sur la ressource, l’identité, l’état du dispositif, la politique et le contexte de la requête plutôt que sur la seule localisation réseau.

NIST SP 800-207 formalise cette approche : la présence sur un LAN ou dans un réseau d’entreprise ne doit pas être traitée comme une preuve suffisante de confiance. Dans un réseau cloud, le réseau offre un chemin, tandis que les contrôles d’identité et d’autorisation déterminent qui peut utiliser le service.

### 6.2 Identité de workload

Les charges de travail doivent utiliser des identités gérées ou des mécanismes équivalents, plutôt que des secrets durables copiés dans des images. L’identité permet d’évaluer les droits de service à service et peut être combinée à TLS mutuel, à des politiques applicatives et à une segmentation réseau.

Principes :
- identité unique par service ou workload lorsque possible ;
- privilèges limités à la fonction ;
- rotation et révocation des credentials ;
- absence de secret codé en dur dans l’image ou le dépôt ;
- journaux de décisions d’autorisation ;
- séparation des identités de déploiement et des identités d’exécution.

### 6.3 Microsegmentation

La microsegmentation applique des politiques fines autour des workloads ou de groupes de workloads. Elle peut être réalisée par des politiques réseau, des agents, des groupes de sécurité, des identités de services ou des services de maillage. La granularité et les garanties varient.

Ne crée pas des centaines de règles manuelles sans gouvernance. Utilise des labels contrôlés, des modèles, des revues, des tests automatiques et des alertes de dérive. Les labels qui déterminent la politique deviennent eux-mêmes une surface de sécurité : qui peut les modifier et comment les changements sont-ils audités ?

### 6.4 TLS et mTLS

TLS protège le canal entre les extrémités. mTLS (TLS mutuel) ajoute une authentification par certificat du client et du serveur lorsque cette configuration est utilisée. Cela peut renforcer le service-to-service, mais la gestion du cycle de vie des certificats, la révocation, l’identité attendue et les exceptions doivent être traitées.

Le chiffrement en transit n’empêche pas une application autorisée d’exposer des données à un mauvais destinataire. Il faut encore authentifier, autoriser, vérifier les entrées et protéger les logs.

### 6.5 Contrôles de sortie

Une politique Zero Trust doit aussi limiter les connexions sortantes. Une charge compromise peut essayer d’exfiltrer des données ou contacter une infrastructure malveillante. Les contrôles de sortie peuvent inclure :
- destinations privées explicitement autorisées ;
- DNS contrôlé et logs de résolution ;
- proxies ou services de filtrage ;
- règles L3/L4 et contrôles applicatifs adaptés ;
- inspection et détection selon les contraintes ;
- surveillance des nouveaux domaines et des destinations inhabituelles ;
- réduction des accès directs à Internet pour les workloads qui n’en ont pas besoin.

Le filtrage par nom de domaine ne fonctionne pas de façon identique pour tous les protocoles et toutes les architectures chiffrées. Vérifie la couverture réelle et les contournements possibles.

### Schéma 5 — Zero Trust : identité, politique, canal et service

<div class="cloude-diagram">
<svg viewBox="0 0 1000 390" width="100%" role="img" aria-label="Workload client passe par une décision de politique et un canal mTLS pour atteindre une API, avec flèches" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce5b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce5g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.ce5t{font:14px Arial,sans-serif;fill:#e5edf8}.ce5s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce5f{fill:none;stroke:#34d399;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce5g);animation:ce5dash 1.5s linear infinite}@keyframes ce5dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="110" width="190" height="130" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><rect x="45" y="132" width="30" height="30" rx="3" fill="none" stroke="#38bdf8" stroke-width="1.7"/><path d="M45 142 H75 M51 151 H69" stroke="#38bdf8" stroke-width="1.4"/><text x="133" y="144" class="ce5t" text-anchor="middle" font-weight="bold">Workload A</text><text x="115" y="182" class="ce5s" text-anchor="middle">Identité de service</text><text x="115" y="203" class="ce5s" text-anchor="middle">Credential court</text><text x="115" y="223" class="ce5s" text-anchor="middle">Demande vers API B</text>
<rect x="275" y="90" width="200" height="170" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.7"/><path d="M315 124 L342 113 L369 124 V154 L342 166 L315 154 Z M342 113 V166" fill="none" stroke="#c4b5fd" stroke-width="1.7"/><text x="405" y="133" class="ce5t" text-anchor="middle" font-weight="bold">Policy Engine</text><text x="375" y="190" class="ce5s" text-anchor="middle">Identité / contexte</text><text x="375" y="211" class="ce5s" text-anchor="middle">Droits / ressource</text><text x="375" y="232" class="ce5s" text-anchor="middle">Autoriser ou refuser</text>
<rect x="545" y="90" width="190" height="170" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><path d="M580 122 L600 113 L620 122 V149 L600 159 L580 149 Z" fill="none" stroke="#38bdf8" stroke-width="1.7"/><text x="657" y="134" class="ce5t" text-anchor="middle" font-weight="bold">Canal TLS/mTLS</text><text x="640" y="188" class="ce5s" text-anchor="middle">Confidentialité</text><text x="640" y="209" class="ce5s" text-anchor="middle">Identité des pairs</text><text x="640" y="230" class="ce5s" text-anchor="middle">Certificat valide</text>
<rect x="800" y="110" width="180" height="130" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="890" y="145" class="ce5t" text-anchor="middle" font-weight="bold">API B</text><text x="890" y="176" class="ce5s" text-anchor="middle">Authentification</text><text x="890" y="197" class="ce5s" text-anchor="middle">Autorisation métier</text><text x="890" y="218" class="ce5s" text-anchor="middle">Audit</text>
<path d="M210 175 H270" class="ce5f" marker-end="url(#ce5g)"/><path d="M475 175 H540" class="ce5f" marker-end="url(#ce5g)"/><path d="M735 175 H795" class="ce5f" marker-end="url(#ce5g)"/>
<text x="20" y="300" class="ce5s">Le réseau fournit la connectivité, mais la décision dépend de l’identité et de la politique.</text><text x="20" y="323" class="ce5s">Un flux L3/L4 autorisé ne signifie pas qu’une requête métier doit être acceptée.</text><text x="20" y="346" class="ce5s">La validation des certificats, l’autorisation applicative et les logs restent nécessaires.</text>
</svg>
</div>

Le modèle combine identité et chemin réseau. Le composant nommé « Policy Engine » est conceptuel : les produits réels peuvent répartir la décision entre l’identité cloud, le proxy, le service mesh, l’application et une passerelle d’accès.

## 7. Réseau Kubernetes et workloads conteneurisés

### 7.1 Les couches de réseau Kubernetes

Kubernetes introduit des objets et des chemins supplémentaires :
- adresse du nœud ;
- adresse du Pod ;
- Service ClusterIP ;
- NodePort ou LoadBalancer selon le besoin ;
- Ingress ou Gateway API selon l’implémentation ;
- DNS interne ;
- réseau overlay ou routage natif fourni par le CNI ;
- politiques réseau inter-Pods.

La topologie réelle dépend du plugin CNI, du mode réseau du cluster, des intégrations cloud et de la façon dont les adresses sont allouées. Ne transpose pas une hypothèse d’un fournisseur ou CNI à un autre.

### 7.2 CNI et chemin Pod-à-Pod

Le CNI (Container Network Interface) est une interface d’intégration pour la configuration réseau des conteneurs. Le plugin sélectionné peut utiliser des overlays, des routes natives, des fonctions eBPF ou d’autres mécanismes. Ces choix influencent les performances, la visibilité, les NetworkPolicies et le dépannage.

Pour suivre un flux entre deux Pods, il faut savoir :
1. si les Pods sont sur le même nœud ;
2. si les adresses sont routables depuis le VPC/VNet ;
3. si le plugin encapsule le trafic ;
4. si le trafic traverse un équipement de sécurité cloud ;
5. si les politiques réseau du cluster autorisent le flux ;
6. si le service de destination et la résolution DNS sont corrects.

Les détails d’encapsulation et de visibilité des IP peuvent changer selon le CNI et les options de cluster.

### 7.3 NetworkPolicy : intention et prise en charge

Les objets Kubernetes NetworkPolicy définissent certains contrôles L3/L4 pour les Pods sélectionnés, à condition que l’implémentation réseau prenne en charge leur application. Leur création seule ne garantit pas que le plugin applique la politique.

Une politique de moindre privilège doit envisager l’ingress et l’egress, DNS, les métriques, les probes de santé, la communication avec les dépendances et les flux d’administration. Une politique qui bloque DNS ou les probes peut rendre un workload inutilisable même si ses règles applicatives principales sont correctes.

### 7.4 Ingress, Gateway API et load balancing

L’Ingress Kubernetes est un objet d’API dont le comportement dépend d’un contrôleur. Gateway API fournit un modèle plus extensible pour certains scénarios de routage, mais sa prise en charge varie. Le contrôleur peut créer ou configurer un load balancer cloud, un proxy ou des ressources propres au cluster.

Il faut suivre le chemin réel : client → entrée globale/regionale → load balancer → service Kubernetes → Pod. Identifie où se terminent TLS, l’authentification et le WAF ; savoir qu’un objet Ingress existe ne suffit pas.

### 7.5 Service mesh et identité service-to-service

Un service mesh peut fournir des identités de workloads, du mTLS, de la télémétrie et des politiques au niveau applicatif. Il n’est pas un remplacement automatique des NetworkPolicies ou du routage cloud. Le réseau doit acheminer le trafic entre les proxies, les politiques doivent être cohérentes, et les équipes doivent comprendre comment les erreurs se propagent entre les couches.

Attention à la complexité : service mesh, CNI, NetworkPolicy, pare-feu cloud et gateway peuvent se superposer. Construis un diagramme de flux réel par requête et définis qui possède chaque politique.

### Schéma 6 — Trajet d’une requête de l’utilisateur jusqu’au Pod

<div class="cloude-diagram">
<svg viewBox="0 0 1000 430" width="100%" role="img" aria-label="Client, DNS, load balancer, ingress controller, service Kubernetes, pods et politiques réseau, avec flèches de direction" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce6b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce6g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.ce6t{font:13px Arial,sans-serif;fill:#e5edf8}.ce6s{font:11px Arial,sans-serif;fill:#a9bdd5}.ce6f{fill:none;stroke:#34d399;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce6g);animation:ce6dash 1.5s linear infinite}@keyframes ce6dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="95" width="120" height="80" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="80" y="125" class="ce6t" text-anchor="middle">Client</text><text x="80" y="147" class="ce6s" text-anchor="middle">HTTPS</text>
<rect x="170" y="95" width="120" height="80" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="230" y="125" class="ce6t" text-anchor="middle">DNS</text><text x="230" y="147" class="ce6s" text-anchor="middle">Public/private</text>
<rect x="320" y="95" width="150" height="80" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="395" y="125" class="ce6t" text-anchor="middle">Load balancer</text><text x="395" y="147" class="ce6s" text-anchor="middle">Cloud provider</text>
<rect x="500" y="95" width="150" height="80" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="575" y="125" class="ce6t" text-anchor="middle">Gateway / Ingress</text><text x="575" y="147" class="ce6s" text-anchor="middle">Contrôleur</text>
<path d="M140 135 H165" class="ce6f" marker-end="url(#ce6g)"/><path d="M290 135 H315" class="ce6f" marker-end="url(#ce6g)"/><path d="M470 135 H495" class="ce6f" marker-end="url(#ce6g)"/>
<rect x="690" y="65" width="285" height="300" rx="14" fill="#0a1727" stroke="#60a5fa" stroke-width="1.6"/><text x="832" y="90" class="ce6t" text-anchor="middle" font-weight="bold">Cluster Kubernetes</text>
<rect x="715" y="110" width="235" height="55" rx="9" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="832" y="132" class="ce6t" text-anchor="middle">Service (ClusterIP)</text><text x="832" y="151" class="ce6s" text-anchor="middle">Sélectionne endpoints</text>
<rect x="715" y="200" width="105" height="75" rx="9" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><text x="767" y="227" class="ce6t" text-anchor="middle">Pod A</text><text x="767" y="248" class="ce6s" text-anchor="middle">API</text><rect x="840" y="200" width="110" height="75" rx="9" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><text x="895" y="227" class="ce6t" text-anchor="middle">Pod B</text><text x="895" y="248" class="ce6s" text-anchor="middle">API</text>
<path d="M650 135 H685 V137 H710" class="ce6f" marker-end="url(#ce6g)"/><path d="M832 165 V195" class="ce6f" marker-end="url(#ce6g)"/><path d="M820 237 H835" class="ce6f" marker-end="url(#ce6g)"/>
<rect x="715" y="300" width="235" height="42" rx="8" fill="#211d3a" stroke="#a78bfa" stroke-width="1.3"/><text x="832" y="326" class="ce6t" text-anchor="middle">CNI + NetworkPolicy</text>
<path d="M832 275 V295" fill="none" stroke="#a78bfa" stroke-width="2.3" stroke-dasharray="6 4" marker-end="url(#ce6b)"/>
<text x="20" y="235" class="ce6s">Une panne peut se trouver</text><text x="20" y="255" class="ce6s">à chaque couche :</text><text x="20" y="275" class="ce6s">DNS, LB, contrôleur, Service,</text><text x="20" y="295" class="ce6s">Pod, CNI ou policy.</text><text x="20" y="390" class="ce6s">Les flèches représentent le flux utilisateur vers le workload ; les réponses et la santé sont à analyser séparément.</text>
</svg>
</div>

## 8. Réseau multi-cloud et stratégie d’interconnexion

### 8.1 Éviter le « réseau universel » prématuré

Une architecture multi-cloud peut être nécessaire pour des raisons de souveraineté, d’acquisition, de résilience, de services spécialisés ou de stratégie fournisseur. Relier tous les réseaux de tous les clouds en un seul grand domaine peut toutefois augmenter la complexité et le rayon d’impact.

Avant de relier deux clouds, précise :
- les applications réellement dépendantes ;
- les flux nécessaires et leur volume ;
- les classes de données ;
- les exigences de latence et de disponibilité ;
- les plans IP et le DNS ;
- les propriétaires de sécurité de chaque côté ;
- les routes autorisées, les filtrages et l’identité ;
- la stratégie en cas d’indisponibilité d’un fournisseur.

### 8.2 Modèles de connectivité inter-cloud

Les options incluent VPN chiffrés, services d’interconnexion d’opérateurs, appliances SD-WAN, réseau de transit tiers ou architectures où les applications communiquent via des APIs publiques protégées. Aucun modèle n’est meilleur en toute situation. Le VPN peut être plus rapide à mettre en place mais dépend du transport et des capacités des passerelles ; l’interconnexion privée peut apporter de la prévisibilité mais exige des circuits, une redondance et des coûts supplémentaires.

### 8.3 DNS, PKI et identité entre clouds

Les différences d’identité, de DNS privé et de gestion de certificats deviennent rapidement plus importantes que la simple connexion IP. Établis une stratégie :
- résolveurs et redirecteurs ;
- noms de service stables ;
- certificats et autorités de confiance approuvés ;
- rotation et révocation des secrets ;
- identités de service sans clés longues durées lorsque possible ;
- logs avec corrélation entre clouds.

Ne donne pas à un réseau « confiance par défaut » uniquement parce qu’il appartient à une autre organisation ou au même groupe d’entreprise.

### 8.4 Coût et egress

Le transfert sortant peut coûter beaucoup plus que le calcul lorsque de grandes quantités de données franchissent les régions, les clouds ou des réseaux tiers. Cartographie les volumes en gigaoctets par flux et sépare :
- trafic interne à une zone ;
- trafic interzone ;
- trafic interrégion ;
- trafic vers Internet ;
- trafic entre fournisseurs ;
- trafic dupliqué par la réplication ou l’observabilité.

Pour chaque flux élevé, évalue si l’architecture doit rapprocher le service, utiliser un cache, effectuer une réplication plus sélective ou supprimer une dépendance réseau.

### Schéma 7 — Interconnexion de deux clouds avec zone de transit contrôlée

<div class="cloude-diagram">
<svg viewBox="0 0 1000 415" width="100%" role="img" aria-label="Cloud A et cloud B reliés à une zone de transit opérateur avec inspection et VPN ou circuit privé, flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce7b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce7g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.ce7t{font:14px Arial,sans-serif;fill:#e5edf8}.ce7s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce7f{fill:none;stroke:#38bdf8;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce7b);animation:ce7dash 1.6s linear infinite}@keyframes ce7dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="80" width="265" height="250" rx="16" fill="#0a1727" stroke="#38bdf8" stroke-width="1.7"/><text x="152" y="107" class="ce7t" text-anchor="middle" font-weight="bold">Cloud A</text><rect x="48" y="135" width="210" height="75" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.3"/><text x="153" y="163" class="ce7t" text-anchor="middle">Réseau applicatif</text><text x="153" y="185" class="ce7s" text-anchor="middle">Routes contrôlées</text><rect x="48" y="235" width="210" height="65" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.3"/><text x="153" y="261" class="ce7t" text-anchor="middle">Gateway A</text><text x="153" y="282" class="ce7s" text-anchor="middle">VPN / circuit privé</text>
<rect x="370" y="100" width="260" height="210" rx="16" fill="#111d30" stroke="#fbbf24" stroke-width="1.7"/><text x="500" y="128" class="ce7t" text-anchor="middle" font-weight="bold">Transit / opérateur</text><rect x="400" y="155" width="200" height="65" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.3"/><path d="M428 175 L447 166 L466 175 V197 L447 206 L428 197 Z" fill="none" stroke="#fbbf24" stroke-width="1.5"/><text x="530" y="182" class="ce7t" text-anchor="middle">Inspection</text><text x="530" y="202" class="ce7s" text-anchor="middle">Routage / contrôle</text><text x="500" y="258" class="ce7s" text-anchor="middle">Politique explicite de transit</text><text x="500" y="280" class="ce7s" text-anchor="middle">Pas de confiance implicite</text>
<rect x="715" y="80" width="265" height="250" rx="16" fill="#0a1727" stroke="#34d399" stroke-width="1.7"/><text x="847" y="107" class="ce7t" text-anchor="middle" font-weight="bold">Cloud B</text><rect x="743" y="135" width="210" height="75" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.3"/><text x="848" y="163" class="ce7t" text-anchor="middle">API / workload</text><text x="848" y="185" class="ce7s" text-anchor="middle">Identité et TLS</text><rect x="743" y="235" width="210" height="65" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.3"/><text x="848" y="261" class="ce7t" text-anchor="middle">Gateway B</text><text x="848" y="282" class="ce7s" text-anchor="middle">VPN / circuit privé</text>
<path d="M258 267 H365" class="ce7f" marker-end="url(#ce7b)"/><path d="M600 188 H710" class="ce7f" marker-end="url(#ce7b)"/><path d="M715 295 H635 V295" fill="none" stroke="#34d399" stroke-width="2.2" stroke-dasharray="7 5" marker-end="url(#ce7g)"/><path d="M370 205 H320 V300 H260" fill="none" stroke="#34d399" stroke-width="2.2" stroke-dasharray="7 5" marker-end="url(#ce7g)"/>
<text x="20" y="365" class="ce7s">Flèches bleues : chemin de demande conceptuel ; vertes : retour vers l’origine.</text><text x="20" y="387" class="ce7s">En production, redondance, BGP, routage retour, DNS et règles de chaque fournisseur doivent être explicitement validés.</text>
</svg>
</div>

Ce modèle n’est pas une recommandation universelle de faire transiter tout le trafic dans un opérateur. Il illustre la nécessité de choisir et d’observer un chemin explicite entre environnements.

## 9. Performance, latence, MTU et capacité

### 9.1 Comprendre la latence de bout en bout

La latence totale inclut la distance et les délais du transport, les files d’attente, les appliances d’inspection, le chiffrement/déchiffrement, les proxies, l’équilibrage et le traitement applicatif. Un traceroute peut aider, mais certains hops ne répondent pas ou ne représentent pas toute la réalité du chemin cloud. Mesure à la fois le réseau et l’application.

Évite de diagnostiquer la performance avec un seul test ponctuel. Utilise :
- percentiles de latence (p50, p95, p99) ;
- débit et saturation ;
- pertes et retransmissions ;
- taux d’erreur ;
- nombre de connexions et nouvelles connexions par seconde ;
- temps passé dans les dépendances ;
- tests synthétiques depuis les zones pertinentes ;
- comparaison avant/après un changement.

### 9.2 BDP et fenêtres TCP

Le Bandwidth-Delay Product (BDP) estime le volume de données qui peut être « en vol » pour remplir une liaison : débit multiplié par RTT. Sur une liaison à grand débit et RTT élevé, les fenêtres TCP et la congestion peuvent limiter le débit si les paramètres ou les implémentations ne suivent pas.

Un débit faible ne signifie pas forcément une bande passante insuffisante. Il peut provenir de pertes, de limitations de sessions, de chiffrement, de congestion, de quotas, de files d’attente ou du serveur distant. Utilise des tests adaptés et autorisés, dans un environnement représentatif.

### 9.3 MTU, MSS et tunnels

Les tunnels VPN et certains overlays ajoutent des en-têtes. Si le paquet transporté dépasse la MTU du chemin et que la découverte de MTU ne fonctionne pas correctement, des flux peuvent se figer de façon intermittente. Les petits paquets passent alors que les gros transferts échouent.

Contrôles possibles :
- MTU configurée aux interfaces ;
- overhead de l’encapsulation ;
- messages ICMP nécessaires à la découverte de MTU ;
- négociation TCP MSS si utilisée ;
- interfaces et appliances sur l’ensemble du chemin ;
- chemins différents au retour ;
- tests IPv4 et IPv6.

Ne réduis pas la MTU de façon aveugle : mesure le chemin et garde une trace du changement.

### 9.4 Saturation des appliances

Le nombre de paquets par seconde, les nouvelles connexions par seconde, le volume de données, les fonctions d’inspection activées et la taille des sessions peuvent saturer un pare-feu à des moments différents. Un débit théorique élevé sur une fiche technique peut supposer un jeu de règles et un profil de paquets précis.

Dimensionne par scénario de charge, prévois une marge pour les pics et les bascules, vérifie la licence et teste le comportement en cas de perte d’un nœud. Une architecture qui passe en régime normal mais sature quand le trafic se reporte sur un nœud survivant n’est pas réellement résiliente.

### Schéma 8 — Mesure du chemin et points de latence

<div class="cloude-diagram">
<svg viewBox="0 0 1000 365" width="100%" role="img" aria-label="Client, edge, réseau cloud, inspection, application et base de données avec flèches et points de mesure de latence" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce8" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><style>.ce8t{font:13px Arial,sans-serif;fill:#e5edf8}.ce8s{font:11px Arial,sans-serif;fill:#a9bdd5}.ce8f{fill:none;stroke:#38bdf8;stroke-width:3;stroke-dasharray:7 5;marker-end:url(#ce8);animation:ce8dash 1.6s linear infinite}@keyframes ce8dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="95" width="125" height="80" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="82" y="125" class="ce8t" text-anchor="middle">Client</text><text x="82" y="147" class="ce8s" text-anchor="middle">RUM / probe</text>
<rect x="180" y="95" width="135" height="80" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.4"/><text x="247" y="125" class="ce8t" text-anchor="middle">Edge / WAF</text><text x="247" y="147" class="ce8s" text-anchor="middle">TLS / queue</text>
<rect x="350" y="95" width="135" height="80" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="417" y="125" class="ce8t" text-anchor="middle">Transit</text><text x="417" y="147" class="ce8s" text-anchor="middle">RTT / drops</text>
<rect x="520" y="95" width="135" height="80" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.4"/><text x="587" y="125" class="ce8t" text-anchor="middle">Inspection</text><text x="587" y="147" class="ce8s" text-anchor="middle">Sessions / CPU</text>
<rect x="690" y="95" width="135" height="80" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><text x="757" y="125" class="ce8t" text-anchor="middle">Application</text><text x="757" y="147" class="ce8s" text-anchor="middle">P95 / erreurs</text>
<rect x="860" y="95" width="120" height="80" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><text x="920" y="125" class="ce8t" text-anchor="middle">Base</text><text x="920" y="147" class="ce8s" text-anchor="middle">Requêtes</text>
<path d="M145 135 H175" class="ce8f" marker-end="url(#ce8)"/><path d="M315 135 H345" class="ce8f" marker-end="url(#ce8)"/><path d="M485 135 H515" class="ce8f" marker-end="url(#ce8)"/><path d="M655 135 H685" class="ce8f" marker-end="url(#ce8)"/><path d="M825 135 H855" class="ce8f" marker-end="url(#ce8)"/>
<path d="M82 220 H920" stroke="#334155" stroke-width="1.5"/><circle cx="82" cy="220" r="5" fill="#38bdf8"><animateMotion path="M 0 0 Q 0 -4 0 0 Q 0 4 0 0" dur="2s" repeatCount="indefinite"/></circle><circle cx="247" cy="220" r="5" fill="#a78bfa"><animateMotion path="M 0 0 Q 0 -4 0 0 Q 0 4 0 0" dur="2s" repeatCount="indefinite"/></circle><circle cx="417" cy="220" r="5" fill="#38bdf8"><animateMotion path="M 0 0 Q 0 -4 0 0 Q 0 4 0 0" dur="2s" repeatCount="indefinite"/></circle><circle cx="587" cy="220" r="5" fill="#fbbf24"><animateMotion path="M 0 0 Q 0 -4 0 0 Q 0 4 0 0" dur="2s" repeatCount="indefinite"/></circle><circle cx="757" cy="220" r="5" fill="#34d399"><animateMotion path="M 0 0 Q 0 -4 0 0 Q 0 4 0 0" dur="2s" repeatCount="indefinite"/></circle><circle cx="920" cy="220" r="5" fill="#34d399"><animateMotion path="M 0 0 Q 0 -4 0 0 Q 0 4 0 0" dur="2s" repeatCount="indefinite"/></circle>
<text x="20" y="265" class="ce8t">Mesure par segment, puis corrèle avec la trace applicative.</text><text x="20" y="290" class="ce8s">Ne somme pas naïvement des mesures qui couvrent des périmètres différents.</text><text x="20" y="313" class="ce8s">Compare les percentiles et les erreurs, pas seulement la moyenne et le débit maximal.</text>
</svg>
</div>

## 10. Observabilité réseau et télémétrie

### 10.1 Plans de contrôle et de données

Le **plan de contrôle** gère la configuration et la programmation des ressources : création de réseaux, association de tables, politiques et annonces de routes. Le **plan de données** transporte effectivement les paquets. Une API de configuration disponible ne garantit pas que le plan de données se comporte comme prévu, et inversement.

Lors d’un incident, sépare les questions :
- Le changement est-il accepté par le plan de contrôle ?
- La configuration a-t-elle été appliquée aux ressources effectives ?
- Le plan de données a-t-il acheminé les paquets ?
- Le service cible a-t-il reçu et traité le flux ?
- Les logs couvrent-ils la bonne zone, interface et fenêtre temporelle ?

### 10.2 Flow logs, capture et mirroring

Les journaux de flux fournissent des métadonnées, souvent agrégées, sur des communications acceptées ou refusées. Ils ne montrent pas nécessairement les charges utiles, les erreurs applicatives ou chaque paquet individuel. La capture de paquets peut fournir un niveau de détail supplémentaire, mais elle requiert une portée, un stockage et des contrôles de confidentialité rigoureux.

Une stratégie de collecte doit spécifier :
- les interfaces et réseaux collectés ;
- les flux ou champs inclus ;
- la rétention et le coût ;
- le contrôle d’accès aux logs ;
- la synchronisation des horloges ;
- la corrélation avec les identifiants de requête ;
- le masquage ou la protection des données sensibles ;
- les règles d’alerte et d’escalade.

### 10.3 SLO réseau

Un SLO (Service Level Objective) définit un objectif mesurable associé à une expérience attendue. Pour le réseau, cela peut inclure disponibilité d’un chemin, latence p95/p99, taux de perte, temps de résolution DNS ou délai de rétablissement. Il faut définir le point de mesure et le périmètre, sinon deux équipes peuvent annoncer des chiffres incompatibles.

Un SLO doit être relié aux conséquences métier. La disponibilité d’un tunnel VPN ne suffit pas si l’application n’est pas joignable ; l’état « healthy » d’un load balancer n’est pas une preuve de réussite pour tous les parcours clients.

### 10.4 Corréler la télémétrie

Pour suivre une requête de bout en bout :
- horloges synchronisées ;
- identifiant de corrélation dans l’application ;
- journaux DNS et sécurité accessibles ;
- métriques des gateways et appliances ;
- logs d’équilibrage de charge ;
- événements de configuration ;
- traces distribuées si le système le permet ;
- tags pour région, environnement, compte, cluster et service.

### Schéma 9 — Chaîne de télémétrie et réponse à l’incident

<div class="cloude-diagram">
<svg viewBox="0 0 1000 400" width="100%" role="img" aria-label="Ressources réseau, collecte métriques logs traces, corrélation, alerte et intervention avec flèches" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ce9b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="ce9g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.ce9t{font:14px Arial,sans-serif;fill:#e5edf8}.ce9s{font:12px Arial,sans-serif;fill:#a9bdd5}.ce9f{fill:none;stroke:#38bdf8;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#ce9b);animation:ce9dash 1.5s linear infinite}@keyframes ce9dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="80" width="190" height="110" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="115" y="109" class="ce9t" text-anchor="middle" font-weight="bold">Ressources</text><text x="115" y="134" class="ce9s" text-anchor="middle">Routes / FW / VPN</text><text x="115" y="155" class="ce9s" text-anchor="middle">LB / DNS / workloads</text><text x="115" y="175" class="ce9s" text-anchor="middle">Événements de config</text>
<rect x="280" y="80" width="190" height="110" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="375" y="109" class="ce9t" text-anchor="middle" font-weight="bold">Collecteurs</text><text x="375" y="134" class="ce9s" text-anchor="middle">Métriques / logs</text><text x="375" y="155" class="ce9s" text-anchor="middle">Traces / flow logs</text><text x="375" y="175" class="ce9s" text-anchor="middle">Capture contrôlée</text><path d="M210 135 H275" class="ce9f" marker-end="url(#ce9b)"/>
<rect x="540" y="80" width="190" height="110" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="635" y="109" class="ce9t" text-anchor="middle" font-weight="bold">Corrélation</text><text x="635" y="134" class="ce9s" text-anchor="middle">Temps / request ID</text><text x="635" y="155" class="ce9s" text-anchor="middle">Région / service</text><text x="635" y="175" class="ce9s" text-anchor="middle">Baseline / anomalies</text><path d="M470 135 H535" class="ce9f" marker-end="url(#ce9b)"/>
<rect x="800" y="80" width="175" height="110" rx="12" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="887" y="109" class="ce9t" text-anchor="middle" font-weight="bold">Alerte / incident</text><text x="887" y="134" class="ce9s" text-anchor="middle">Runbook</text><text x="887" y="155" class="ce9s" text-anchor="middle">Owner / escalade</text><text x="887" y="175" class="ce9s" text-anchor="middle">Preuves collectées</text><path d="M730 135 H795" class="ce9f" marker-end="url(#ce9b)"/>
<rect x="280" y="255" width="450" height="90" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="505" y="283" class="ce9t" text-anchor="middle" font-weight="bold">Réponse opérationnelle</text><text x="505" y="307" class="ce9s" text-anchor="middle">Confirmer impact → identifier le changement → réduire le risque</text><text x="505" y="327" class="ce9s" text-anchor="middle">Restaurer → valider → documenter les causes et actions</text><path d="M887 190 V220 H730 V300" fill="none" stroke="#34d399" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#ce9g)"/><path d="M280 300 H155 V190" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="7 5" marker-end="url(#ce9b)"/><text x="20" y="380" class="ce9s">Le circuit de retour d’expérience doit améliorer les règles, les tests, les alertes et les procédures.</text>
</svg>
</div>

## 11. DDoS, WAF et protections du plan de données

### 11.1 Distinguer les couches d’attaque

Les attaques de saturation peuvent viser le réseau, le transport ou l’application. Les protections et les signaux diffèrent :
- volumétrie ou paquets anormaux ;
- épuisement de connexions ou nouvelles connexions ;
- requêtes HTTP coûteuses ou abusives ;
- charge sur la base de données ou les dépendances ;
- attaques distribuées qui paraissent légitimes isolément.

Une protection DDoS du fournisseur, un CDN, un WAF, un load balancer et un pare-feu réseau répondent à des problèmes différents. Le simple fait d’avoir un WAF ne garantit pas la protection de tous les protocoles ou de l’origine. L’architecture doit empêcher, dans la mesure du possible, l’accès direct à l’origine qui contournerait les protections.

### 11.2 Protéger l’origine

Pour une application publiée, vérifie :
- que les serveurs d’origine ne sont pas exposés en parallèle du point d’entrée voulu ;
- que seules les sources autorisées atteignent l’origine ;
- que la confiance dans les en-têtes transmis par le proxy est configurée correctement ;
- que les contrôles TLS sont cohérents entre edge, proxy et origine ;
- que l’accès d’administration est séparé ;
- que les logs distinguent les requêtes clients et les connexions de proxy ;
- que les limites applicatives et capacités des dépendances sont adaptées.

### 11.3 Dépendances partagées et amplification

Un service peut être mis en difficulté même si la bande passante réseau demeure disponible. Des requêtes coûteuses peuvent épuiser les threads, pools de connexions, caches ou bases de données. La protection doit combiner limitation de débit, quotas, files d’attente, caches, contrôles d’identité et mécanismes de dégradation maîtrisée.

### 11.4 Exercices d’incident DDoS

Définis qui peut activer les protections, comment contacter le fournisseur, quelles métriques déclenchent l’escalade, comment conserver les preuves et comment éviter de bloquer le trafic légitime. Les tests de charge doivent être autorisés, bornés et effectués dans un environnement adapté. Ne lance pas un test volumétrique contre des infrastructures tierces sans autorisation explicite.

## 12. Gouvernance multi-comptes, landing zones et séparation des rôles

### 12.1 Réseau partagé et équipes produit

Une organisation de taille entreprise peut répartir les responsabilités :
- équipe plateforme réseau : plan d’adressage, transit, DNS, connectivité hybride ;
- équipe sécurité : exigences de filtrage, inspection, certificats, logs ;
- équipe produit : flux métier, configuration de workload, tests de santé ;
- opérations/SRE : SLO, alertes, incidents, capacité et reprise ;
- FinOps : coûts de transfert, allocation des dépenses, optimisation.

La séparation doit éviter deux écueils : centraliser chaque petite décision au point de bloquer les équipes, ou permettre à chaque équipe de modifier librement les routes et frontières partagées.

### 12.2 Landing zone réseau

Une landing zone réseau met en place les fondations : hiérarchie de comptes/projets, réseau central ou modèle de transit, segmentation, DNS, accès d’administration, collecte des logs, politiques et automatisation. Les détails changent par fournisseur et par organisation, mais la démarche consiste à établir des garde-fous avant de déployer des applications.

### 12.3 Garder des frontières explicites

- Les environnements de test ne doivent pas accéder à la production par commodité.
- Les outils d’administration ne doivent pas partager une identité privilégiée avec les workloads.
- Les réseaux partenaires doivent être filtrés par préfixe et par flux.
- Les services partagés doivent être inventoriés et limités aux consommateurs nécessaires.
- Les annonces de route doivent être attribuées à des sources approuvées.
- Les exceptions doivent avoir une échéance et un propriétaire.

### 12.4 Contrôle de dérive

Compare périodiquement l’état réel aux définitions approuvées. La dérive peut venir d’un changement manuel, d’une opération d’urgence, d’une ressource créée hors pipeline ou d’un comportement managé. Identifie les différences, évalue le risque puis réconcilie de façon contrôlée. Évite d’écraser automatiquement un correctif d’incident encore nécessaire avant de comprendre sa raison.

## 13. Infrastructure as Code et pipelines de changement réseau

### 13.1 Le réseau comme code testé

L’IaC permet de revoir et reproduire les changements, mais elle ne les rend pas automatiquement sûrs. Un module réutilisé peut déployer une règle trop large dans de nombreux environnements. Les tests doivent donc traiter les propriétés de sécurité et de connectivité, et pas seulement la syntaxe.

Pipeline de base :
1. validation syntaxique et formatage ;
2. lint et politique de sécurité ;
3. calcul d’un plan de changement ;
4. revue par les propriétaires du réseau et des workloads ;
5. test dans un environnement de préproduction ;
6. tests de routes et de flux ;
7. approbation et fenêtre de déploiement si nécessaire ;
8. application progressive ;
9. vérification post-changement et comparaison aux SLO ;
10. possibilité de rollback documenté.

### 13.2 Tests automatisés de flux

Un test peut vérifier qu’un flux attendu fonctionne, et qu’un flux interdit échoue. Les tests doivent tenir compte des faux positifs : certains ports sont temporairement ouverts par une sonde, un service répond depuis un proxy au lieu de la cible prévue, ou un cache DNS masque une mauvaise configuration. Mesure la source et la destination exactes.

Tests importants :
- entrée publique uniquement sur les ports approuvés ;
- absence d’accès direct Internet vers les bases privées ;
- segmentation entre production et non-production ;
- utilisation attendue des endpoints privés ;
- routes de secours présentes et testables ;
- accès d’administration restreint ;
- absence d’annonces de préfixes non approuvés.

### 13.3 Changer le réseau sans perdre le contrôle

Les changements de route, DNS, pare-feu et annonces BGP peuvent affecter beaucoup de ressources. Utilise des changements progressifs lorsque possible : un petit sous-réseau, une région, un préfixe précis ou un groupe de workloads. Prévois une durée d’observation, des métriques de réussite et une condition d’arrêt.

### 13.4 Secrets et fournisseurs IaC

Les credentials de déploiement doivent être à privilèges réduits, de durée courte si possible, et séparés par environnement. Les secrets ne doivent pas apparaître dans les plans, les logs ou le dépôt. Les rôles du pipeline ne doivent pas être capables de modifier sans contrôle toutes les politiques de sécurité centrales.

## 14. Gestion de l’incident réseau : runbooks experts

### 14.1 Les cinq premières minutes

Lorsqu’une application devient inaccessible :
1. déterminer le périmètre et l’impact métier ;
2. vérifier les alertes de changement récent ;
3. préciser la source, destination, protocole, port et heure ;
4. distinguer résolution DNS, établissement TCP/TLS et réponse applicative ;
5. éviter de modifier plusieurs couches en même temps ;
6. désigner un responsable de l’incident et garder un journal des actions.

### 14.2 Route disparue ou annonce incorrecte

Signaux : plusieurs sous-réseaux perdent des destinations, chemin de secours indisponible, routes absentes ou nouvelle route plus spécifique. Actions :
- examiner événements de contrôle et annonces BGP ;
- comparer les routes attendues et effectives ;
- identifier la source de la route ;
- mesurer l’étendue du préfixe affecté ;
- corriger ou retirer la route avec approbation d’urgence ;
- vérifier les deux directions et observer la convergence.

N’annonce pas une route plus large comme remède improvisé sans comprendre les effets sur le trafic non concerné.

### 14.3 Panne de firewall/NVA

Vérifie les sessions, la santé des nœuds, le nombre de connexions, le débit, les drops, les mises à jour et les routes. En cas de failover, surveille si les sessions existantes sont conservées ou recréées, et si le chemin retour traverse bien le nouveau nœud. Un basculement qui rétablit les nouvelles connexions tout en abandonnant les anciennes peut être conforme au mécanisme, mais doit être compris dans le plan de reprise.

### 14.4 Panne DNS

Compare plusieurs résolveurs et sources de vérité, puis vérifie les zones, les délégations, les redirecteurs, les liens aux VPC/VNet et les caches. Ne modifie pas précipitamment un enregistrement public si le problème concerne une zone privée. Capture la réponse DNS, le TTL, le nom exact, le résolveur utilisé et l’adresse cible.

### 14.5 Panne interrégionale

Vérifie l’entrée globale, l’état des endpoints régionaux, le plan de routage, les services de réplication et la capacité secondaire. La panne peut être partielle : l’API est disponible dans une région, mais le service d’identité, de DNS ou de données ne l’est pas. La reprise doit valider le parcours métier complet, et pas uniquement la connectivité IP.

### 14.6 Communication et preuve

En incident majeur, le journal doit préciser les heures, symptômes, hypothèses, actions, décisions, résultats de tests et impacts. Après rétablissement, rédige une analyse sans blâme : facteurs contributifs, détection manquée, facteurs d’amplification et actions concrètes assignées. Une action comme « améliorer la surveillance » doit devenir un test, un seuil, une alerte, un propriétaire et une échéance.

## 15. Modélisation des pannes et tests de résilience

### 15.1 Identifier les dépendances communes

Une architecture à deux chemins peut encore dépendre :
- d’un seul service DNS ;
- d’un seul système d’identité ;
- d’un seul circuit opérateur ;
- d’une seule région d’inspection ;
- d’un seul compte de gestion ;
- d’un seul pipeline qui peut modifier toutes les routes ;
- d’un seul plan IP non documenté.

Le nombre de liens sur un diagramme ne prouve pas la diversité. Identifie les composants réellement indépendants et les dépendances partagées.

### 15.2 Tests de résilience contrôlés

Un test de résilience doit avoir un objectif, un périmètre, des préconditions, une autorisation, des métriques, une limite de risque et un rollback. Exemples :
- désactiver un lien de secours dans un lab ;
- simuler la perte d’une cible derrière un load balancer ;
- vérifier une annonce de route retirée ;
- bloquer un flux non critique pour confirmer une alerte ;
- simuler l’indisponibilité d’un résolveur secondaire ;
- tester l’accès à une API après rotation d’un certificat.

Ne teste pas une panne réelle sur un environnement critique sans accord et procédure formels.

### 15.3 Capacité de secours

Le lien ou la région secondaire doit porter le trafic nécessaire au scénario considéré. Une route de secours qui ne peut supporter que 20 % de la charge peut convenir à une dégradation contrôlée, mais pas à une bascule totale. Documente la capacité, le seuil de saturation et les fonctions qui seront dégradées en priorité.

## 16. Cas pratique expert : architecture globale d’entreprise

### Contexte

Une entreprise possède des workloads dans deux régions d’un cloud, un réseau de bureaux et un second cloud utilisé par une équipe data. Elle exploite des API publiques, des services privés, Kubernetes, des bases de données managées et des services d’administration. Elle doit réduire les communications transversales, garder les chemins d’accès aux données sensibles privés et prouver la connectivité en audit.

### Étape 1 — Définir les domaines de confiance

Propose au minimum :
- réseau d’entrée publique/edge ;
- environnements de production par région ;
- non-production ;
- données sensibles ;
- hub de connectivité ;
- administration ;
- réseau d’entreprise ;
- domaine inter-cloud limité ;
- réseau/plan de contrôle Kubernetes et réseaux applicatifs si requis.

Ne crée pas automatiquement un VPC par microservice. La segmentation doit correspondre aux risques, aux propriétaires, aux politiques et aux limites opérationnelles.

### Étape 2 — Dessiner les flux

Établis des flux précis : client → edge → API ; API → base de données ; workloads → observabilité ; administrateur → bastion ; région A → réplication région B ; réseau data cloud secondaire → API dédiée. Marque également les flux explicitement interdits.

### Étape 3 — Choisir le transit

Compare un hub régional managé avec des liens directs ciblés. Documente quelles tables de routage reçoivent les routes, quels préfixes sont annoncés, quelles routes sont bloquées et si le trafic doit traverser une inspection centrale. Assure-toi que les flux régionaux critiques ne dépendent pas involontairement d’une seule région du hub.

### Étape 4 — Sécuriser l’accès aux services

Pour chaque service natif cloud, choisis endpoint privé, accès via réseau managé ou service public fortement protégé. Vérifie la résolution DNS, le chemin de données réel, les identités, les droits IAM, le chiffrement et les journaux. Les ressources de données ne doivent pas être considérées comme sûres uniquement parce qu’elles possèdent une IP privée.

### Étape 5 — Concevoir la reprise interrégionale

Fixe RTO/RPO par application. Détermine la région de reprise, la capacité, les données répliquées, la stratégie d’entrée globale, les routes, les certificats et le DNS. Écris la séquence de bascule et celle de retour, avec les tests qui prouvent que la fonction métier est rétablie.

### Étape 6 — Gouverner avec IaC

Versionne les CIDR et les politiques centrales. Déploie les ressources de transit et de sécurité via des rôles de pipeline à portée limitée. Ajoute des contrôles qui empêchent l’exposition accidentelle de services administratifs ou de données. Réconcilie les ressources hors code de façon contrôlée.

### Étape 7 — Instrumenter l’exploitation

Collecte les routes, événements de configuration, flow logs, logs DNS, journaux du load balancer et signaux applicatifs. Pose des alertes sur les changements de route, les nouveaux endpoints publics, les baisses de santé, l’augmentation des refus et la saturation. Corrèle l’ensemble par région, environnement et service.

### Étape 8 — Prouver la conception

Livrables :
- diagramme logique et diagramme des zones de défaillance ;
- inventaire IPAM et registre des routes ;
- matrice des flux ;
- cartographie des identités et des frontières de sécurité ;
- tests d’accès autorisés et interdits ;
- procédure de bascule ;
- procédure d’incident ;
- estimation de coûts ;
- revue de risque et responsables de remédiation.

## 17. Questions d’évaluation expert

1. Pourquoi l’agrégation de préfixes peut-elle réduire la taille des tables tout en introduisant un risque de trou noir ?
2. Quelle différence y a-t-il entre topologie, routage et autorisation réseau ?
3. Pourquoi le peering direct ne fournit-il pas nécessairement de transit ?
4. Quelles dépendances cachées peuvent rendre un hub unique vulnérable malgré plusieurs liens d’accès ?
5. Pourquoi une inspection centralisée peut-elle créer des problèmes de latence ou de symétrie ?
6. Comment les règles avec état diffèrent-elles d’ACL sans état lors d’une panne de chemin retour ?
7. Pourquoi des endpoints privés nécessitent-ils une stratégie DNS explicite ?
8. En quoi Zero Trust dépasse-t-il le simple filtrage IP ?
9. Que doit-on vérifier avant d’activer NetworkPolicy dans Kubernetes ?
10. Pourquoi un service mesh ne remplace-t-il pas le routage cloud ou toutes les NetworkPolicies ?
11. Quels sont les risques d’une route par défaut propagée à tous les spokes ?
12. Quels tests valident réellement une bascule multi-région ?
13. Pourquoi la haute disponibilité du réseau ne garantit-elle pas celle de l’application ?
14. Comment distinguer un problème de MTU d’un problème de capacité ou d’application ?
15. Quels signaux faut-il corréler pour prouver qu’un flux a échoué au niveau du pare-feu ?
16. Pourquoi un pipeline IaC doit-il avoir des rôles limités par environnement ?
17. Quels facteurs faut-il considérer pour comparer VPN et connexion dédiée ?
18. Comment mesurer la capacité d’un chemin de secours ?
19. Pourquoi une connexion chiffrée ne remplace-t-elle pas une autorisation applicative ?
20. Quels risques le multi-cloud ajoute-t-il au DNS, à l’identité et à l’egress ?
21. Comment protéger l’origine d’une application placée derrière un CDN/WAF ?
22. Qu’est-ce qu’un SLO réseau utile et comment éviter qu’il soit ambigu ?
23. Pourquoi le plan de contrôle et le plan de données doivent-ils être vérifiés séparément ?
24. Quelles preuves doivent être conservées après un changement réseau critique ?
25. Comment réduire le rayon d’impact d’une erreur de routage ?

### Corrigé synthétique

1. Un résumé trop large peut attirer du trafic vers des destinations non réellement joignables par l’annonceur.
2. La topologie décrit les connexions ; le routage choisit la cible du paquet ; l’autorisation décide si le flux est permis.
3. Le transit entre réseaux tiers est souvent non fourni par le peering ; il dépend du fournisseur et de fonctionnalités distinctes.
4. DNS, identité, inspection, compte de gestion, opérateur, route par défaut ou région du hub.
5. Le trafic fait un détour, subit un traitement supplémentaire et peut contourner le composant au retour.
6. Le mécanisme avec état suit la session ; une ACL sans état peut exiger des règles séparées dans chaque sens.
7. Le nom peut résoudre vers une adresse publique au lieu du chemin privé souhaité.
8. Zero Trust fonde les décisions sur l’identité et le contexte de la ressource, pas sur le seul emplacement.
9. La compatibilité CNI et les flux requis pour DNS, health checks, métriques, administration et dépendances.
10. Le mesh gère certaines fonctions service-to-service, mais les paquets doivent toujours être acheminés et des politiques réseau restent utiles.
11. Un trafic peut sortir par un chemin inattendu, contourner l’inspection ou atteindre des destinations non nécessaires.
12. Santé globale, capacité, données, DNS, routes, identité, temps de bascule et parcours métier.
13. Une application dépend aussi des données, des identités, des secrets, du DNS et de ses dépendances.
14. Comparer tailles de paquets, MTU, pertes/retransmissions, charge, latence et logs applicatifs.
15. Le flux exact, les logs de filtrage, les routes effectives, la synchronisation temporelle et les compteurs d’interface.
16. Pour limiter l’impact d’un pipeline compromis ou d’une erreur de déploiement.
17. Performance, chiffrement, redondance réelle, dépendances opérateur, temps de mise en place, coûts et capacité.
18. Mesures de débit/latence en charge et test de bascule avec la charge attendue.
19. Un service peut accepter une connexion chiffrée d’un client qui ne devrait pas disposer du droit métier.
20. Résolution de noms, routage, identité, chiffrement, egress, coûts et logs dispersés.
21. Empêcher l’accès direct à l’origine, limiter les sources, vérifier les en-têtes et journaliser les requêtes de confiance.
22. Une métrique avec point de mesure, périmètre, percentile/seuil et conséquence métier définis.
23. Un changement accepté peut ne pas avoir produit le chemin effectif attendu ; un chemin disponible peut transporter un flux bloqué par l’application.
24. Ticket, approbation, diff IaC, routes et politiques avant/après, tests, résultats, logs et rollback.
25. Limiter les préfixes propagés, séparer les domaines, appliquer les revues et tester les changements progressivement.

## 18. Checklist de revue finale

### Architecture et adressage
- [ ] Les domaines de confiance sont définis par le risque et les flux.
- [ ] L’IPAM couvre cloud, réseau local, conteneurs, VPN et partenaires.
- [ ] Les blocs sont non chevauchants ou les exceptions sont documentées.
- [ ] Les résumés de route couvrent réellement les destinations annoncées.
- [ ] Les dépendances et points de panne communs sont identifiés.

### Routage et transit
- [ ] Les routes effectives sont vérifiées dans tous les domaines concernés.
- [ ] La propagation des routes est autorisée par source et destination.
- [ ] Le comportement non transitif des peerings est compris.
- [ ] La route par défaut n’ouvre pas involontairement de nouveau chemin.
- [ ] L’inspection, le NAT et le retour sont compatibles.
- [ ] Le plan de secours possède la capacité nécessaire.

### Sécurité
- [ ] Les flux autorisés et interdits sont documentés.
- [ ] Les identités et droits de workloads sont séparés des accès humains.
- [ ] Les services sensibles exigent une authentification appropriée.
- [ ] Les contrôles de sortie sont adaptés au risque.
- [ ] Les règles Kubernetes sont réellement prises en charge et testées.
- [ ] L’origine des applications ne contourne pas l’edge prévu.
- [ ] Les logs de sécurité sont accessibles, protégés et conservés selon la politique.

### Résilience et exploitation
- [ ] RTO et RPO sont définis par service.
- [ ] La bascule a été testée, y compris DNS et données.
- [ ] Les tests montrent le bon fonctionnement et le blocage des flux interdits.
- [ ] Les runbooks donnent des actions sûres, des métriques et une condition d’arrêt.
- [ ] Les changements critiques sont versionnés, approuvés et réversibles.
- [ ] Les quotas, coûts d’egress, d’inspection et de journaux sont estimés.

## 19. Glossaire expert

- **Blast radius** : ensemble des ressources affectées par une erreur, une panne ou une compromission.
- **CNI** : interface d’intégration réseau des conteneurs ; le comportement dépend du plugin.
- **Egress** : trafic sortant d’un workload ou d’un réseau.
- **East-west** : trafic entre composants ou réseaux internes.
- **Flow logs** : journaux de métadonnées sur les flux réseau.
- **Hub-and-spoke** : topologie centralisée avec un hub et plusieurs réseaux périphériques.
- **IPAM** : gestion centralisée de l’allocation et de l’inventaire des adresses IP.
- **mTLS** : TLS avec authentification mutuelle par certificat dans une configuration adaptée.
- **NVA** : appliance réseau virtuelle, comme un pare-feu ou routeur logiciel.
- **North-south** : trafic traversant une frontière réseau logique.
- **NetworkPolicy** : objet Kubernetes exprimant certains contrôles de flux L3/L4 pour des Pods.
- **Peering** : relation de connectivité directe entre réseaux ; les propriétés de transit dépendent de la plateforme.
- **Plan de contrôle** : composants qui configurent et programment les ressources réseau.
- **Plan de données** : composants qui transportent effectivement les paquets.
- **RPO** : objectif de perte de données acceptable, en général exprimé comme durée.
- **RTO** : délai cible de reprise.
- **SLO** : objectif mesurable de fiabilité ou de performance d’un service.
- **Transit gateway** : service de connectivité qui relie un ensemble de réseaux selon une politique de routage.
- **Zero Trust** : approche qui évite d’accorder une confiance implicite basée uniquement sur la position réseau.

## 20. Références officielles

### Architecture cloud et transit
- AWS Well-Architected Framework : https://docs.aws.amazon.com/wellarchitected/
- AWS Transit Gateway : https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html
- AWS Cloud WAN : https://docs.aws.amazon.com/network-manager/latest/cloudwan/what-is-cloudwan.html
- Azure Virtual WAN — topologie réseau : https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/virtual-wan-network-topology
- Azure hub-and-spoke : https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke
- Google Cloud Network Connectivity Center : https://docs.cloud.google.com/network-connectivity/docs/network-connectivity-center

### Sécurité et Zero Trust
- NIST SP 800-207, Zero Trust Architecture : https://csrc.nist.gov/pubs/sp/800/207/final
- Google Cloud Private Google Access / VPC Service Controls : https://docs.cloud.google.com/vpc-service-controls/docs/private-connectivity

### Kubernetes et réseau
- Kubernetes — Services, Load Balancing and Networking : https://kubernetes.io/docs/concepts/services-networking/
- Kubernetes — Network Policies : https://kubernetes.io/docs/concepts/services-networking/network-policies/

### Protocoles et adressage
- IETF RFC 1918, adresses IPv4 privées : https://www.rfc-editor.org/rfc/rfc1918
- IETF RFC 4632, CIDR : https://www.rfc-editor.org/rfc/rfc4632
- IETF RFC 8200, IPv6 : https://www.rfc-editor.org/rfc/rfc8200
- IETF RFC 4271, BGP-4 : https://www.rfc-editor.org/rfc/rfc4271

Les références fournisseurs décrivent les capacités et limites concrètes à vérifier avant un déploiement. Les RFC décrivent les protocoles ou conventions ; elles ne remplacent pas la documentation opérationnelle du service cloud utilisé.


## À retenir

Le niveau expert consiste à contrôler **la topologie, le routage, les politiques, l’identité, la résilience et l’observabilité comme un système unique**. Le réseau doit conserver un comportement prévisible en cas de panne, d’erreur de route, de compromission ou de changement. Une architecture n’est prête que lorsque les chemins autorisés et interdits ont été testés, les bascules ont été exercées, les dépendances communes sont connues et les changements sont gouvernés.

**Règle visuelle maintenue pour tous les cours :** chaque schéma représentant un circuit ou un échange inclut des flèches directionnelles explicites ; les équipements utiles sont représentés ou nommés ; les échanges bidirectionnels montrent les deux directions lorsqu’elles sont pertinentes ; les chemins d’inspection, de transit, de sortie et de retour sont identifiables. Les SVG sont autonomes, en thème sombre, avec des couleurs définies dans les éléments et des animations natives sans JavaScript.
