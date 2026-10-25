
# Attaques DDoS et Mitigation - Intermédiaire

**Niveau :** INTERMÉDIAIRE

Ce cours prolonge les notions du niveau Débutant. Il ne se limite plus à distinguer les attaques volumétriques, protocolaires et applicatives : il apprend à relier les symptômes observés aux métriques réseau, à localiser le point de saturation, à sélectionner une mesure de mitigation adaptée et à vérifier qu’elle protège réellement le service sans bloquer excessivement les utilisateurs légitimes.

La difficulté principale d’un incident DDoS est rarement de constater une hausse de trafic. Elle est de comprendre quelle ressource manque en premier, à quel endroit du chemin réseau elle se trouve, et si la mesure envisagée agit avant ou après ce point. Un serveur peut être sain alors que son accès Internet est saturé ; une liaison peut être disponible alors qu’une table d’état de pare-feu est épuisée ; un débit HTTP modéré peut masquer un coût applicatif élevé.

Les exemples combinent équipements réseau, télémétrie de flux, pare-feu, reverse proxy, CDN, DNS et procédures de réponse. Les commandes sont des modèles à adapter : les noms de plateformes, versions logicielles, règles de routage et politiques de sécurité doivent être vérifiés avant toute application en production.

L’objectif opérationnel est de savoir **mesurer, classifier, atténuer, valider et documenter**. Toute simulation de ce cours est locale et pédagogique ; elle ne génère aucun trafic réseau et ne demande pas de reproduire une attaque contre un système réel.

> **Analogie** : imagine un stade avec plusieurs portes, un contrôle de sécurité, un couloir d’attente et des guichets. Si trop de personnes arrivent, le goulot d’étranglement peut se situer sur la route, à la porte, au contrôle ou au guichet. Ajouter des guichets n’aide pas si la route est bloquée. La mitigation efficace traite le problème à l’endroit où il apparaît, tout en laissant passer les visiteurs autorisés.


## 1. La théorie et les algorithmes

### 1.1. Modéliser le service à protéger

Un service disponible dépend d’une chaîne de ressources : connectivité de l’opérateur, capacité des liens, routeurs, pare-feu, équilibrage de charge, reverse proxy, serveur applicatif, base de données et dépendances externes. Une attaque peut viser une seule ressource, mais les symptômes sont parfois visibles ailleurs. Une application qui répond lentement peut être victime d’un épuisement de connexions, d’une saturation CPU, d’une dépendance DNS dégradée ou d’une congestion bien en amont.

Avant de choisir une règle, il faut construire une représentation du chemin du trafic et relever les capacités nominales de chaque étape. Le maillon qui sature en premier détermine l’efficacité de la mitigation. Une règle sur le serveur ne récupère pas une liaison d’accès déjà pleine ; un CDN ne protège pas automatiquement un service exposé sur une adresse IP d’origine encore accessible directement.

| Ressource | Indicateurs utiles | Symptôme classique | Mesures envisageables |
|---|---|---|---|
| Accès opérateur | Débit entrant, pps, pertes sur interface | Tous les services d’un site deviennent inaccessibles | Filtrage ou scrubbing en amont, coordination opérateur |
| Routeur de bordure | CPU, files, drops, capacité de transfert | Pertes en bordure, latence élevée pour plusieurs réseaux | Vérifier la capacité réelle, filtrage validé, mitigation opérateur |
| Pare-feu stateful | Sessions, nouvelles connexions/s, CPU, mémoire | Timeouts malgré une liaison non saturée | Réduire les états inutiles, protection adaptée au produit, filtrage en amont |
| Équilibreur / reverse proxy | Requêtes/s, connexions, files, codes HTTP | 5xx, latence élevée ou file qui augmente | Limites par route, mise en cache, capacité et protection applicative |
| Application | CPU, mémoire, threads, durée des requêtes | Certaines routes sont lentes, même avec un débit modeste | WAF, quotas, cache, optimisation et limitation ciblée |
| Base de données | Connexions actives, files, verrous, latence | L’application s’effondre sur les opérations dynamiques | Cache, pools et quotas ; atténuation au point d’entrée |
| DNS autoritatif | QPS, taux de réponses, latence, erreurs | Le site semble « hors ligne » alors que ses serveurs répondent | Anycast, redondance, ACL adaptées, protection DNS spécialisée |

### 1.2. Dépasser la taxonomie de base

Les catégories du niveau Débutant restent utiles, mais un diagnostic intermédiaire doit aussi qualifier **l’unité de pression** et le **coût par requête**.

- **Attaque volumétrique** : le volume en bits par seconde (bit/s) remplit la capacité d’un circuit ou d’une interface. Le trafic peut être constitué de paquets assez grands pour maximiser le débit.
- **Attaque à haut débit de paquets** : le nombre de paquets par seconde (pps) devient déterminant. De petits paquets peuvent coûter cher à traiter, même lorsque le débit en bit/s reste modéré.
- **Épuisement d’état** : le nombre de nouvelles connexions, de sessions ou d’entrées de suivi dépasse la capacité d’un pare-feu, d’un équilibreur ou du système cible.
- **Pression applicative** : une route HTTP, une recherche, une génération de rapport ou une authentification consomme beaucoup de CPU, de mémoire ou de ressources de base de données. Le coût est lié au travail effectué, pas seulement au nombre d’octets.
- **Attaque multi-vecteur** : plusieurs familles de trafic exercent une pression simultanée, parfois avec des variations destinées à contourner une protection trop rigide.
- **Carpet bombing** : le trafic malveillant se répartit sur de nombreuses adresses ou destinations d’un même réseau, rendant moins efficace une défense qui ne surveille qu’une IP.
- **Attaque à faible débit apparent** : le volume total peut sembler normal, mais certaines requêtes retiennent longtemps des ressources ou sollicitent une opération coûteuse.
- **Flash crowd** : hausse légitime et soudaine d’activité, par exemple après une annonce. Les symptômes ressemblent à ceux d’une attaque ; la différence doit être évaluée à partir du comportement, des routes sollicitées et des données de contexte, pas d’un simple pic de trafic.

La présence d’adresses sources nombreuses n’est pas, à elle seule, une preuve suffisante. Une attaque distribuée peut employer des sources usurpées ou des équipements compromis, tandis que des clients légitimes peuvent partager une adresse publique via NAT. Le filtrage fondé uniquement sur l’IP source peut donc produire des faux positifs.

### 1.3. Mesurer la pression : bit/s, pps, connexions et requêtes

Les métriques répondent à des questions différentes :

- **bit/s** : la capacité de transmission est-elle consommée ?
- **pps** : le chemin de traitement des paquets peut-il suivre le rythme ?
- **Nouvelles connexions/s** : les mécanismes d’établissement et de suivi d’état sont-ils sous pression ?
- **Connexions simultanées** : la capacité des tables, des sockets et des pools est-elle atteinte ?
- **Requêtes/s** : combien de demandes applicatives arrivent ? Cette mesure doit être associée à la route et au coût de traitement.
- **Latence p50, p95 et p99** : la majorité des utilisateurs ou les cas les plus lents sont-ils affectés ? Une moyenne seule peut masquer une minorité d’utilisateurs en grande difficulté.
- **Taux d’erreur** : les timeouts, réponses 429, 5xx, resets et pertes augmentent-ils ? Le sens du code dépend de la couche qui l’émet.
- **Ressource consommée** : CPU, mémoire, file, descripteurs, pool de connexions, bande passante de sortie ou quota d’un service tiers.

Une valeur absolue est moins informative qu’une comparaison avec une référence normale. Il faut enregistrer les profils habituels selon l’heure, le jour, la saisonnalité et les événements connus. Une hausse de 300 % n’a pas la même signification pour un service qui varie naturellement beaucoup et pour un service stable. Le seuil ne remplace pas le contexte : il déclenche une investigation.

### 1.4. Comprendre la capacité et les files d’attente

Un modèle pédagogique utile consiste à comparer le débit offert au débit de service. Si un serveur traite jusqu’à 120 requêtes par seconde et reçoit 40 requêtes légitimes plus 95 requêtes indésirables par seconde, le débit total offert vaut 135 requêtes/s. Le surplus théorique est de 15 requêtes/s. Si une file peut contenir 80 requêtes et que le surplus reste approximativement constant, elle peut se remplir en environ 80 / 15, soit 5,3 secondes.

Ce calcul est une approximation, pas une prédiction exacte pour un système réel. Les temps de traitement varient, les clients retentent leurs demandes, les requêtes n’ont pas toutes le même coût et les mécanismes de rejet peuvent intervenir à plusieurs niveaux. Il sert surtout à expliquer pourquoi une file finie offre un tampon temporaire, pas une capacité illimitée.

La stabilité dépend aussi de la variabilité. Même si la charge moyenne se trouve juste sous la capacité maximale, des rafales peuvent créer une attente. Une marge de capacité est donc nécessaire pour absorber les pointes et les travaux non uniformes. Il faut surveiller les percentiles de latence et la profondeur des files, et pas uniquement le pourcentage moyen d’utilisation.

> **Piège :** ne conclus pas qu’un service est sûr parce que son débit moyen reste inférieur à sa capacité nominale. Une interface peut être proche de sa limite, une table d’état peut être pleine, ou certaines requêtes peuvent consommer dix fois plus de ressources que les requêtes ordinaires.

### 1.5. Schéma animé : localiser la saturation avant d’agir

Le schéma suivant est volontairement **visuel et non interactif**. Les flux bleus représentent du trafic suspect, le flux vert le trafic légitime ; les tirets animés montrent le sens des flux. L’objectif est de distinguer une mitigation placée en amont de la ressource saturée d’une règle appliquée trop tard. Si le CSS est supprimé par une politique de sécurité du lecteur, le schéma statique reste compréhensible.

<style>
.ddos-mid-flow { fill: none; stroke-dasharray: 7 11; stroke-linecap: round; animation: ddosMidFlow 1.25s linear infinite; }
.ddos-mid-attack { stroke: #60a5fa; stroke-width: 3; }
.ddos-mid-legit { stroke: #4ade80; stroke-width: 3; }
.ddos-mid-filter { stroke: #fbbf24; stroke-width: 3; }
.ddos-mid-forward { stroke: #a1a1aa; stroke-width: 3; }
.ddos-mid-pulse { animation: ddosMidPulse 1.8s ease-in-out infinite; }
.ddos-mid-caption { fill: #e4e4e7; font: 13px system-ui, sans-serif; }
.ddos-mid-muted { fill: #a1a1aa; font: 11px system-ui, sans-serif; }
.ddos-mid-blue { fill: #60a5fa; }
.ddos-mid-green { fill: #4ade80; }
.ddos-mid-amber { fill: #fbbf24; }
@keyframes ddosMidFlow { to { stroke-dashoffset: -36; } }
@keyframes ddosMidPulse { 0%,100% { opacity: .35; } 50% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .ddos-mid-flow, .ddos-mid-pulse { animation: none !important; } }
</style>

<div style="width:100%;max-width:980px;margin:1.5rem auto;padding:1rem;border:1px solid #3f3f46;border-radius:1.25rem;background:#18181b;overflow-x:auto;">
<svg viewBox="0 0 900 330" role="img" aria-label="Schéma de flux réseau : trafic suspect et trafic légitime passent d'abord par l'opérateur, puis par une couche de mitigation, avant le pare-feu et le serveur." style="width:100%;min-width:620px;height:auto;display:block;">
  <defs><marker id="ddosMidArrowBlue" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker><marker id="ddosMidArrowGreen" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#4ade80"/></marker><marker id="ddosMidArrowGray" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a1a1aa"/></marker></defs>
  <rect x="18" y="30" width="155" height="255" rx="14" fill="#202027" stroke="#52525b"/>
  <text x="95" y="55" text-anchor="middle" class="ddos-mid-caption">Sources</text>
  <rect x="43" y="79" width="105" height="47" rx="8" fill="#172554" stroke="#60a5fa"/><text x="95" y="99" text-anchor="middle" class="ddos-mid-blue" font-size="12">Trafic suspect</text><text x="95" y="115" text-anchor="middle" class="ddos-mid-muted">multi-source</text>
  <rect x="43" y="192" width="105" height="47" rx="8" fill="#14532d" stroke="#4ade80"/><text x="95" y="212" text-anchor="middle" class="ddos-mid-green" font-size="12">Trafic légitime</text><text x="95" y="228" text-anchor="middle" class="ddos-mid-muted">clients réels</text>
  <rect x="210" y="95" width="146" height="123" rx="12" fill="#27272a" stroke="#71717a"/><text x="283" y="123" text-anchor="middle" class="ddos-mid-caption">Opérateur / bordure</text><text x="283" y="145" text-anchor="middle" class="ddos-mid-muted">Débit · pps · pertes</text><text x="283" y="164" text-anchor="middle" class="ddos-mid-muted">Point de saturation ?</text><circle cx="283" cy="190" r="7" fill="#fbbf24" class="ddos-mid-pulse"/>
  <rect x="398" y="75" width="160" height="164" rx="12" fill="#292116" stroke="#fbbf24" stroke-width="1.5"/><text x="478" y="103" text-anchor="middle" class="ddos-mid-amber" font-size="13">Mitigation amont</text><text x="478" y="128" text-anchor="middle" class="ddos-mid-caption">Filtrage / scrubbing</text><text x="478" y="151" text-anchor="middle" class="ddos-mid-muted">Préserve la liaison</text><path d="M439 174 L453 188 L439 202 M453 174 L439 188 L453 202" stroke="#f87171" stroke-width="3" fill="none"/><text x="489" y="190" class="ddos-mid-muted">flux rejetés</text><path d="M467 214 L481 214 L481 203 L495 203 L495 214 L509 214" stroke="#4ade80" stroke-width="2" fill="none"/>
  <rect x="602" y="95" width="120" height="123" rx="12" fill="#202027" stroke="#71717a"/><text x="662" y="123" text-anchor="middle" class="ddos-mid-caption">Pare-feu</text><text x="662" y="145" text-anchor="middle" class="ddos-mid-muted">Politique validée</text><text x="662" y="164" text-anchor="middle" class="ddos-mid-muted">Sessions saines</text>
  <rect x="766" y="112" width="113" height="90" rx="12" fill="#14261c" stroke="#4ade80"/><rect x="788" y="132" width="69" height="13" rx="3" fill="#4ade80"/><rect x="788" y="153" width="69" height="13" rx="3" fill="#4ade80"/><rect x="788" y="174" width="69" height="13" rx="3" fill="#4ade80"/><text x="822" y="222" text-anchor="middle" class="ddos-mid-caption">Service</text>
  <path d="M148 103 L210 132" class="ddos-mid-flow ddos-mid-attack" marker-end="url(#ddosMidArrowBlue)"/><path d="M148 214 L210 184" class="ddos-mid-flow ddos-mid-legit" marker-end="url(#ddosMidArrowGreen)"/><path d="M356 130 L398 130" class="ddos-mid-flow ddos-mid-attack" marker-end="url(#ddosMidArrowBlue)"/><path d="M356 185 L398 185" class="ddos-mid-flow ddos-mid-legit" marker-end="url(#ddosMidArrowGreen)"/><path d="M558 154 L602 154" class="ddos-mid-flow ddos-mid-legit" marker-end="url(#ddosMidArrowGreen)"/><path d="M722 154 L766 154" class="ddos-mid-flow ddos-mid-forward" marker-end="url(#ddosMidArrowGray)"/>
  <text x="450" y="278" text-anchor="middle" class="ddos-mid-caption">Règle de décision : agir avant le premier goulot d’étranglement</text><text x="450" y="299" text-anchor="middle" class="ddos-mid-muted">Une règle sur le serveur ne libère pas une liaison déjà saturée en amont.</text>
</svg>
<p style="color:#a1a1aa;font-size:.8rem;margin:.5rem 0 0;">Schéma conceptuel. Les capacités, les interfaces et l’emplacement de la mitigation dépendent de l’architecture réelle.</p>
</div>

### 1.6. Méthode de triage par couches

Un diagnostic efficace cherche à identifier le premier endroit où le trafic attendu ne se comporte plus normalement.

1. **Accès et opérateur :** comparer débit entrant et capacité de liaison, vérifier les pertes et demander les compteurs côté opérateur si les mesures locales ne voient déjà plus tout le trafic.
2. **Réseau et transport :** examiner pps, erreurs d’interface, files, taux de SYN, réinitialisations TCP, retransmissions, sessions et taux d’établissement.
3. **Périmètre de sécurité :** relever les connexions actives, les nouvelles sessions/s, les drops par règle et la charge du moteur d’inspection. Ne désactive pas l’inspection globale simplement pour faire baisser un compteur.
4. **Proxy, CDN et application :** comparer les routes sollicitées, codes HTTP, latences p95/p99, cache hit ratio, connexions au backend et erreurs de dépendances.
5. **DNS et services communs :** confirmer la résolution depuis plusieurs réseaux et vérifier la santé des serveurs autoritatifs, des résolveurs et des dépendances d’authentification.
6. **Impact utilisateur :** tester des transactions représentatives depuis des emplacements distincts, en privilégiant des sondes autorisées et non agressives.

Il faut horodater les observations et conserver les conditions du test. Un compteur cumulatif sans son delta, une capture sans point de mesure clairement identifié ou un graphique sans fuseau horaire peuvent induire en erreur.

### 1.7. Télémétrie : utiliser plusieurs sources

| Source | Ce qu’elle apporte | Limites à connaître |
|---|---|---|
| SNMP / télémétrie d’interface | Octets, paquets, erreurs, drops, utilisation des files | Agrégation temporelle pouvant masquer une rafale très courte |
| NetFlow / IPFIX / sFlow | Conversations, préfixes, ports, protocoles, volume par flux | Échantillonnage, pertes d’export, visibilité partielle ou champs anonymisés |
| Journaux pare-feu | Décisions de politique, sessions refusées, anomalies | Le journal peut lui-même devenir une charge ; débit limité et règles de collecte nécessaires |
| Journaux CDN / WAF / reverse proxy | Routes, codes HTTP, cache, identité de client observée | L’adresse source n’est fiable que si la chaîne de proxy est correctement configurée |
| Métriques système | CPU, mémoire, sockets, files, descripteurs | Valeurs agrégées pouvant cacher un processus ou un cœur saturé |
| Captures réseau | Drapeaux TCP, tailles, retransmissions, temporisation | Point de capture local, volume important, données potentiellement sensibles |
| Sondes synthétiques | Disponibilité réelle d’une transaction depuis un point donné | Une seule sonde peut être filtrée, mal placée ou confondre une panne locale avec une panne globale |

Une bonne chaîne d’investigation associe métriques agrégées pour repérer l’anomalie, journaux pour décrire le comportement et captures ciblées pour confirmer l’hypothèse. Éviter les captures complètes permanentes sans nécessité : elles peuvent exposer des données personnelles ou des secrets de session.

### 1.8. Mitigation volumétrique : agir en amont

Quand l’accès Internet est saturé, la mitigation doit généralement se faire avant cette liaison : opérateur, centre de scrubbing, service cloud anti-DDoS ou réseau de distribution qui absorbe la charge. Une ACL sur le routeur situé derrière le lien saturé peut protéger certains équipements internes, mais elle ne rend pas la capacité d’accès à nouveau disponible.

Les approches courantes comprennent :

- **Scrubbing :** rediriger le trafic vers une infrastructure spécialisée qui distingue le trafic considéré comme indésirable du trafic qui doit être transmis.
- **CDN / Anycast :** distribuer le trafic sur plusieurs points de présence et rapprocher les demandes des caches ou des capacités de bordure. Cela ne dispense pas de protéger l’origine.
- **RTBH (Remote Triggered Black Hole) :** annoncer, selon une procédure convenue, une route de rejet vers une destination ciblée. C’est un outil de protection ultime qui peut rendre la destination indisponible ; il sert souvent à préserver le reste du réseau.
- **BGP FlowSpec :** distribuer des règles de filtrage dans un périmètre maîtrisé, à condition que l’opérateur et les équipements prennent en charge la fonctionnalité et que la gouvernance limite les règles acceptées.
- **Filtrage chez le fournisseur :** demander une mitigation ciblée avec des critères mesurés et une échéance de réévaluation.

La redirection vers un scrubbing center exige une conception du chemin aller/retour, des annonces de préfixes et des capacités contractuelles. Une mauvaise bascule peut créer un routage asymétrique, un MTU inadapté ou un retour contournant la mitigation. Les paramètres de production doivent donc être validés avec l’opérateur, et non copiés d’un exemple de laboratoire.

### 1.9. Mitigation protocolaire : limiter sans casser le trafic légitime

Une hausse de SYN peut indiquer une pression sur l’établissement TCP, mais le seul ratio SYN/ACK ne permet pas de décider automatiquement qu’il s’agit d’une attaque. Des problèmes de routage ou un serveur qui ne répond plus peuvent aussi produire des écarts. Les SYN cookies, les limites de nouvelles connexions, les mécanismes anti-usurpation et les protections de session doivent être activés selon les capacités documentées de la plateforme.

Les précautions importantes sont les suivantes :

- **SYN cookies et mécanismes équivalents :** utiles contre certains épuisements d’état, mais ne résolvent pas une saturation de bande passante ni une application lente.
- **Limitation des connexions :** dimensionner les seuils sur le comportement réel ; un seuil global peut pénaliser les clients derrière un NAT partagé.
- **ACL et listes de blocage :** écrire des règles précises, avec sens de circulation, ordre, journalisation mesurée et procédure de retour arrière.
- **uRPF et filtrage anti-usurpation :** employer un mode compatible avec la topologie. Le filtrage strict peut rejeter du trafic légitime sur des routes asymétriques ou multihomées.
- **CoPP / protection du plan de contrôle :** distinguer trafic destiné à l’équipement (BGP, OSPF, SSH, SNMP, ICMP nécessaire) du trafic transitant. Un profil trop restrictif peut interrompre l’adjacence de routage ou l’administration.
- **ICMP :** ne pas bloquer aveuglément tous les messages. Certains messages ICMP sont nécessaires au diagnostic et à la découverte de MTU.

### 1.10. Mitigation applicative : contrôler le coût, pas uniquement le nombre

Les attaques applicatives ciblent des routes ou des opérations qui consomment des ressources. La réponse peut inclure cache, challenge, WAF, limites par compte, quotas par clé API, coupe-circuit d’une fonction coûteuse et dégradation contrôlée. La décision doit être liée à la route, à l’identité disponible et au coût réel.

Une limite fixe par adresse IP est simple, mais imparfaite : une entreprise ou un campus peut concentrer des milliers d’utilisateurs derrière une même IP, tandis qu’une attaque distribuée peut utiliser de nombreuses adresses. Combine, selon le service, des limites par IP, par compte authentifié, par clé API, par route et un plafond global. Les comptes privilégiés ont besoin de protections spécifiques contre l’épuisement du service et l’abus d’authentification.

Le cache doit être configuré avec soin. Ne mets pas en cache des réponses personnalisées ou privées sans une clé et des règles explicites. Un cache public peut absorber des lectures identiques, mais une route qui ajoute un paramètre aléatoire, une recherche coûteuse ou une réponse personnalisée peut rester dynamique.

### 1.11. Algorithme de sélection d’une première mesure

```text
ENTRÉES : mesures réseau, métriques applicatives, impact utilisateur, architecture connue

1. Confirmer l'incident avec au moins deux signaux indépendants.
2. Estimer le point de saturation le plus en amont observé.
3. Si la liaison opérateur est pleine :
      ouvrir immédiatement un ticket opérateur / scrubbing ;
      appliquer une mitigation amont convenue.
   Sinon si les états ou le plan de contrôle sont épuisés :
      identifier le protocole et l'équipement concernés ;
      appliquer le profil de protection validé pour cette plateforme.
   Sinon si quelques routes applicatives sont coûteuses :
      activer une règle ciblée, un cache ou un quota révisable.
4. Définir un indicateur de succès avant le changement.
5. Déployer d'abord la mesure la plus étroite et réversible.
6. Vérifier disponibilité, latence, erreurs et taux de faux positifs.
7. Si l'impact légitime augmente : revenir au dernier état stable et réévaluer.
8. Horodater la décision, le responsable, la portée et la durée de la règle.
```

> **Astuce :** écris avant la mitigation ce qui te fera conclure qu’elle fonctionne : par exemple, baisse du débit entrant vers l’origine, stabilité des nouvelles sessions, rétablissement du p95 et succès d’une transaction de référence. « Le graphique semble meilleur » n’est pas un critère de validation.


## 2. Configuration et pratique

### 2.1. Préparer une ligne de base avant l’incident

Un plan de mitigation est plus rapide lorsqu’il existe déjà : inventaire des adresses publiques, diagramme du chemin réseau, capacités de chaque accès, contacts opérateur, règles CDN/WAF, service critique, ports nécessaires, procédures de changement et responsables autorisés. Conserve un instantané de configuration et une copie hors équipement.

La ligne de base doit distinguer un trafic courant, un pic d’activité légitime et un scénario de test approuvé. Un test de charge doit rester dans un environnement possédé ou expressément autorisé, avec des seuils d’arrêt, une surveillance et une fenêtre planifiée. Les exemples ci-dessous sont destinés à l’observation et à la protection d’un service que tu administres.

### 2.2. Diagnostic Cisco IOS / IOS XE en lecture seule

Les commandes exactes et la disponibilité des champs varient selon les versions et les modèles. Commence par collecter des compteurs et des états, puis compare les deltas sur une période connue.

```text
show clock
show interfaces
show interfaces counters errors
show processes cpu sorted
show memory statistics
show ip traffic
show logging
show policy-map control-plane
show platform hardware qfp active statistics drop
```

Interprétation :

- `show clock` fixe le repère temporel des commandes et des journaux.
- `show interfaces` montre le débit, les paquets, les erreurs et certains abandons ; selon la plateforme, les détails de file apparaissent ailleurs.
- `show interfaces counters errors` aide à différencier une erreur physique d’une simple augmentation du trafic.
- `show processes cpu sorted` et les compteurs matériels aident à repérer un point de pression, sans prouver à eux seuls sa cause.
- `show ip traffic` donne des statistiques IP agrégées utiles sur certaines plateformes.
- `show policy-map control-plane` examine les classes de protection du plan de contrôle lorsqu’elles sont configurées.
- Les commandes de plateforme matérielle sont spécifiques à IOS XE et à l’équipement ; ne les exécute pas sur un système qui ne les prend pas en charge.

Ne remets pas des compteurs à zéro sans raison : l’opération peut détruire une partie de la comparaison historique. Note plutôt les valeurs au début et à la fin de la fenêtre, puis calcule la différence.

### 2.3. Exemple de collecte NetFlow / IPFIX

La configuration du collecteur dépend de la version IOS XE, du type de licence, de l’architecture du routeur et du système de supervision. Cet exemple est un squelette de conception, à adapter avec les commandes validées pour l’équipement.

```text
! Schéma conceptuel : noms et paramètres à adapter à la plateforme
flow record DDoS-RECORD
 match ipv4 source address
 match ipv4 destination address
 match ip protocol
 match transport source-port
 match transport destination-port
 collect counter bytes
 collect counter packets
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
!
flow exporter DDoS-EXPORTER
 destination <IP_COLLECTEUR>
 transport udp <PORT_COLLECTEUR>
!
flow monitor DDoS-MONITOR
 record DDoS-RECORD
 exporter DDoS-EXPORTER
```

Les lignes et mots-clés disponibles ne sont pas identiques sur toutes les versions. Vérifie la documentation de la plateforme avant de configurer ou d’attacher un moniteur à une interface. Protège aussi le flux de télémétrie : limite les destinations, surveille les pertes d’export et évite d’exposer inutilement des informations détaillées sur les communications.

Un collecteur doit pouvoir répondre à des questions pratiques : quelles destinations reçoivent la plus grande part du trafic ? Quels protocoles dominent ? Le trafic croît-il sur un seul préfixe ou de nombreux préfixes ? Les plus gros flux sont-ils aussi responsables du nombre de paquets ? Les réponses varient selon l’échantillonnage ; un enregistrement d’échantillonnage doit accompagner les résultats.

### 2.4. Protection du plan de contrôle : principe de configuration

CoPP protège le processeur de contrôle d’un équipement. Il ne constitue pas une solution générique pour le trafic de transit et ne répare pas un accès saturé. Avant de configurer une politique, identifie les protocoles destinés au routeur, les taux normaux, la sensibilité aux pertes et les mécanismes de secours.

Un plan de travail prudent est :

1. inventorier BGP, OSPF, BFD, SSH, SNMP, ICMP et les autres flux de contrôle nécessaires ;
2. relever leurs volumes habituels et les variations pendant un changement de topologie ;
3. créer des classes explicites sur une plateforme de laboratoire ou dans une fenêtre approuvée ;
4. contrôler les compteurs de conformité et d’excès ;
5. tester perte d’adjacence, reprise après panne et accès d’administration ;
6. activer progressivement, conserver une session de secours et préparer une commande de retour arrière validée.

Il serait dangereux de fournir un profil universel avec des valeurs de police arbitraires : un débit sûr sur un routeur de petit site peut être insuffisant pour un cœur de réseau. Le profil doit être dérivé des mesures et de la documentation fabricant.

### 2.5. Limitation applicative côté Nginx

Nginx possède des directives de limitation de débit de requêtes qui peuvent être adaptées à certaines routes. Voici un exemple de laboratoire pour une API non critique ; les seuils ne sont pas universels. Les directives exactes doivent être vérifiées selon la version et la configuration réelle.

```nginx
http {
    # Exemple pédagogique : 10 demandes/s par clé client, selon l'adresse binaire.
    limit_req_zone $binary_remote_addr zone=api_per_client:10m rate=10r/s;

    server {
        listen 443 ssl;
        server_name api.exemple.test;

        location /api/lecture/ {
            limit_req zone=api_per_client burst=20 nodelay;
            proxy_pass http://application_backend;
        }
    }
}
```

À vérifier avant d’utiliser cet exemple :

- la clé `$binary_remote_addr` est-elle l’adresse du vrai client ou celle du proxy amont ?
- le reverse proxy reçoit-il les en-têtes client uniquement de proxys de confiance ?
- les appels normaux peuvent-ils dépasser 10 requêtes/s, notamment les applications qui font plusieurs appels pour une seule action ?
- existe-t-il une route plus coûteuse qui mérite un quota différent ?
- quel code de réponse et quel journal signaleront la limitation ?
- comment revenir rapidement au profil précédent ?

Ne fais pas confiance à un en-tête `X-Forwarded-For` fourni directement par un client. La chaîne de proxy de confiance doit être configurée selon l’architecture réelle ; sinon, un attaquant peut changer la valeur utilisée comme clé de limitation.

### 2.6. Quotas par identité et par opération

Une protection d’API robuste utilise plusieurs garde-fous complémentaires :

| Garde-fou | Exemple de portée | Risque si trop strict |
|---|---|---|
| Par IP | Limiter les pointes d’un même point d’accès | Bloquer une entreprise entière derrière NAT |
| Par compte authentifié | Limite adaptée à un utilisateur | Un compte compromis peut encore consommer son quota |
| Par clé API / client | Limite contractuelle ou de plan | Rotation abusive de clés si l’identité n’est pas gouvernée |
| Par route | Limiter la génération de rapports ou recherche coûteuse | Mauvais chemin ou classification incomplète |
| Globale | Protéger la capacité totale du backend | Un seul client peut monopoliser le budget partagé |
| Par concurrence | Plafonner le nombre de travaux simultanés | Les tâches légitimes longues peuvent être refusées |

Le comportement souhaitable est prévisible : code de réponse documenté, indication de reprise si appropriée, métriques de refus, journaux échantillonnés et possibilité de lever temporairement une limite via une procédure contrôlée. Les réponses de limitation ne doivent pas provoquer une boucle de nouvelles tentatives immédiates ; un mécanisme de temporisation côté client est souvent nécessaire.

### 2.7. CDN, WAF et protection de l’origine

Une architecture CDN/WAF efficace suppose que le trafic vers l’origine passe effectivement par la protection. Contrôle les adresses et les chemins d’accès alternatifs : ancienne IP publique, sous-domaine oublié, port d’administration exposé, service de test ou cible DNS historique. Une origine accessible en direct peut permettre de contourner les règles et de saturer le site même lorsque le nom principal est protégé.

Checklist de conception :

- l’origine n’accepte-t-elle que les plages officielles des points de présence ou des contrôles de santé autorisés ?
- les en-têtes client sont-ils reconstruits par un proxy de confiance ?
- le cache exclut-il les réponses privées et les requêtes non sûres ?
- les règles WAF font-elles la distinction entre une signature connue et un comportement atypique légitime ?
- les exceptions ont-elles une date d’expiration et un propriétaire ?
- les journaux donnent-ils une vue des requêtes bloquées, challengées, mises en cache et transmises à l’origine ?
- les routes d’administration sont-elles protégées par un contrôle d’accès distinct ?

Un WAF n’est pas la réponse à toutes les attaques réseau. Un flux UDP volumétrique peut saturer l’accès bien avant d’atteindre le WAF HTTP. La défense doit couvrir les couches et les points de passage réels.

### 2.8. DNS, résolution et dépendances

Pendant un incident, teste les résolveurs et les serveurs autoritatifs séparément. Une requête DNS qui échoue depuis un seul réseau ne prouve pas que la zone est indisponible mondialement. Considère la latence, le taux de réponse, les erreurs SERVFAIL, les réponses NXDOMAIN, les expirations et les changements récents. Les requêtes légitimes peuvent augmenter à cause de caches expirés, de redémarrages ou d’un effet de retry.

Les actions prudentes consistent à vérifier la redondance autoritative, la distribution anycast s’il y en a une, la santé des résolveurs, les limites de débit documentées et les mécanismes de protection du fournisseur. Évite les changements précipités de TTL pendant l’incident sans comprendre les conséquences de cache et de propagation.

### 2.9. Concevoir des tests de validation contrôlés

Un test de mitigation doit être réalisable sans provoquer un déni de service. Pour un laboratoire ou une fenêtre de test autorisée, utilise une charge synthétique modérée, des utilisateurs de test, des données non sensibles et des seuils d’arrêt explicites. La validation peut aussi utiliser des rejeux de journaux anonymisés, des captures déjà collectées ou un environnement de staging isolé.

Avant le test, fixer :

- le propriétaire du service et la personne qui peut arrêter le test ;
- la fenêtre temporelle et la charge maximale convenue ;
- les métriques de succès et les limites d’arrêt ;
- les tests fonctionnels de base à exécuter ;
- l’ordre de retrait ou de désactivation de la règle ;
- le canal de communication pour signaler une régression.

Une politique qui réduit le débit mais fait chuter le taux de réussite des utilisateurs légitimes n’est pas une réussite. Il faut comparer le taux de blocage suspect, le taux d’erreur légitime et la capacité résiduelle.

> **Danger :** ne transforme pas un exemple de laboratoire en changement de production sans revue. Une mauvaise ACL, une règle WAF trop large, un seuil de limitation trop bas ou une annonce RTBH mal ciblée peut couper le service que l’on cherche à protéger. Les actions de routage doivent suivre une procédure d’escalade et d’approbation.


## 3. Dépannage et sécurité

### 3.1. Runbook des premières minutes

Un runbook décrit qui fait quoi, dans quel ordre, et comment juger le résultat. Il réduit les décisions improvisées lorsqu’un incident évolue rapidement.

**0 à 5 minutes — confirmer et cadrer**

- Confirmer l’impact par une sonde synthétique et un signal indépendant : télémétrie d’interface, erreurs HTTP, journaux ou alerte opérateur.
- Noter l’heure de début, le périmètre, les services atteints et les changements récents.
- Désigner un responsable d’incident et un canal de communication unique.
- Éviter les redémarrages, la suppression de règles et les changements simultanés non documentés.

**5 à 15 minutes — localiser**

- Comparer le débit et les pps à la capacité du premier lien observable.
- Vérifier les drops, la charge de l’équipement, la table de sessions et les erreurs de proxy.
- Comparer plusieurs destinations et routes applicatives.
- Si la saturation est en amont du site, ouvrir immédiatement un contact prioritaire auprès de l’opérateur ou du fournisseur anti-DDoS.

**15 à 30 minutes — appliquer la mesure la plus ciblée**

- Choisir une action alignée sur le point de saturation : mitigation amont, mesure protocolaire ou protection applicative.
- Écrire le périmètre précis, le responsable et les critères de retrait.
- Déployer une seule modification à la fois si la situation le permet, pour préserver la capacité d’attribuer les résultats.

**30 à 60 minutes — vérifier et stabiliser**

- Tester une transaction utilisateur représentative depuis plusieurs points.
- Vérifier p95/p99, erreurs, débit, files et connexions.
- Contrôler les faux positifs et les services secondaires.
- Réduire progressivement une mesure d’urgence si la pression baisse et si le risque est acceptable.

### 3.2. Distinguer attaque, flash crowd et panne interne

| Observation | Hypothèse possible | Contrôle à effectuer |
|---|---|---|
| Débit entrant très supérieur à la base, pertes d’interface | Attaque volumétrique ou pic massif légitime | NetFlow/IPFIX, données opérateur, contexte d’événement |
| Beaucoup de nouvelles connexions, peu de sessions établies | Pression sur l’établissement, retour réseau cassé ou serveur indisponible | Compteurs SYN/ACK, captures aux deux côtés, état serveur |
| Trafic normal, CPU applicatif élevé sur une route précise | Requêtes coûteuses, bug ou abus ciblé | Latence et durée par route, traces, journaux applicatifs |
| Codes 5xx élevés, connexions backend épuisées | Dépendance lente ou pool saturé | Métriques base de données, pool, traces de dépendances |
| DNS en échec sur certains réseaux seulement | Panne locale, propagation ou incident de résolution | Résolution depuis plusieurs résolveurs et réseaux, délégation, TTL |
| Beaucoup de sources IP identiques ou différentes | Peut être une clientèle concentrée ou une attaque distribuée | Comportement, identité, routes, volumes et contexte ; pas l’IP seule |

Il n’est pas toujours possible de classifier immédiatement l’intention. Il est pourtant possible de protéger un service sur la base du comportement et du risque, puis d’affiner l’analyse. La réponse opérationnelle peut être graduelle : plafonner temporairement une route coûteuse pendant que l’équipe détermine si la hausse est légitime.

### 3.3. Cas pratique A : l’accès du site est saturé

**Situation.** La sonde HTTPS n’aboutit plus depuis l’extérieur. Les interfaces internes et les serveurs semblent disponibles, mais le débit entrant sur l’accès opérateur approche sa capacité et les pertes augmentent. Les utilisateurs de plusieurs applications sont touchés.

**Hypothèses.** Le goulot se situe sur la liaison ou juste avant celle-ci ; l’attaque peut viser une IP ou plusieurs services du site. Une ACL sur le pare-feu interne ne rendra pas la bande passante déjà consommée à nouveau disponible.

**Réponse.** Confirmer le point de mesure avec l’opérateur, partager l’IP ou le préfixe ciblé, l’intervalle temporel, les protocoles dominants et les compteurs. Demander l’activation d’une mitigation en amont convenue. Avant une annonce de blackhole, comprendre que la destination pourrait être entièrement inaccessible ; décider avec le responsable de service et l’opérateur si cette option est acceptable.

**Validation.** Le trafic indésirable n’atteint plus l’accès saturé, la perte diminue, la sonde HTTPS répond à nouveau et les autres préfixes restent joignables. La baisse de débit à elle seule ne suffit pas : la disponibilité doit être testée.

### 3.4. Cas pratique B : saturation de l’application derrière un CDN

**Situation.** Le lien ne paraît pas saturé, mais les réponses 5xx montent. Les logs du reverse proxy montrent qu’une route de recherche consomme beaucoup plus de temps que les autres. Le cache hit ratio baisse fortement et les connexions de base de données atteignent leur limite.

**Hypothèses.** Il peut s’agir d’une attaque applicative, d’une utilisation abusive d’une fonctionnalité ou d’un pic de recherche légitime. Le débit brut ne permet pas de trancher.

**Réponse.** Comparer les routes, la distribution des paramètres, les identités disponibles, la durée et le coût backend. Activer une limite temporaire et étroite sur la route coûteuse ; vérifier la clé de client de confiance ; augmenter le cache uniquement pour les réponses réellement partageables ; éventuellement dégrader temporairement une fonction secondaire coûteuse.

**Validation.** Le temps de réponse du backend et le nombre de connexions actives baissent, le taux de succès des parcours critiques remonte, les clients normaux ne sont pas bloqués de façon disproportionnée. Les exceptions d’urgence sont enregistrées avec une expiration.

### 3.5. Cas pratique C : table d’état du pare-feu sous pression

**Situation.** Le débit entrant reste nettement inférieur à la capacité de la liaison, mais les nouvelles connexions sont instables. La table de sessions du pare-feu approche sa limite et les utilisateurs constatent des timeouts. Le CPU peut être élevé ou presque normal selon le produit.

**Hypothèses.** Une hausse de connexions courtes, une configuration de timeout, un problème de retour asymétrique ou une pression délibérée peuvent contribuer au symptôme. Une saturation d’état ne doit pas être confondue avec une saturation de bande passante.

**Réponse.** Collecter le nombre de sessions, le taux d’ouverture, les causes de rejet, les timeouts et les chemins aller/retour. Vérifier si une application saine a soudainement changé son comportement. Utiliser les protections supportées par l’équipement et, si nécessaire, coordonner un filtre ciblé en amont. Ne désactive pas le suivi d’état global comme mesure improvisée : cela pourrait casser les garanties de sécurité et le retour du trafic.

**Validation.** Le nombre de nouvelles sessions revient vers une zone soutenable, les sessions légitimes s’établissent, les compteurs de rejet diminuent et la sécurité stateful reste active sur les flux qui l’exigent.

### 3.6. Trois erreurs fréquentes de mitigation

**Erreur 1 : bloquer un pays ou une grande plage au hasard.** La géolocalisation IP n’est pas une preuve de malveillance. Des utilisateurs légitimes, partenaires, opérateurs mobiles ou services cloud peuvent partager des plages. Si une restriction géographique est utilisée comme mesure temporaire, son périmètre et sa durée doivent être justifiés et évalués.

**Erreur 2 : limiter uniquement par adresse IP.** Cette stratégie est facile à déployer mais ne représente pas toujours une identité utilisateur. Elle peut pénaliser les clients derrière NAT et être contournée par des sources nombreuses. Combine plusieurs clés de limitation et mesure les faux positifs.

**Erreur 3 : activer un journal détaillé sur chaque paquet pendant un flux massif.** L’écriture de journaux peut devenir une nouvelle charge sur le routeur, le pare-feu, le stockage ou le pipeline SIEM. Privilégie les compteurs agrégés, l’échantillonnage, les journaux limités et une capture ciblée quand elle est nécessaire.

### 3.7. Mesurer les faux positifs

Une règle de mitigation doit être jugée sur deux dimensions : le trafic qu’elle réduit et la part du trafic légitime qu’elle affecte. Définis des indicateurs tels que : volume rejeté par règle, taux de challenge réussi, taux d’erreur des clients authentifiés, plaintes utilisateurs, réussites des sondes, erreurs 429/403 et variation des transactions métier.

Quand c’est possible, active les nouvelles règles d’abord en mode observation, compte les correspondances, teste des cas représentatifs puis applique progressivement le blocage. Pour une situation urgente, la phase d’observation peut être courte, mais les métriques de réussite et le plan de retour arrière restent nécessaires.

Une alerte ne doit pas être supprimée simplement parce que la règle a réduit le nombre de requêtes. Si des utilisateurs légitimes échouent, adapte la clé de classification, le seuil, la route, la population ciblée ou la méthode de mitigation.

### 3.8. Sécurité de l’exploitation et gestion des changements

- Utiliser des rôles administratifs nominatifs, MFA et un canal de contrôle indépendant lorsque c’est possible.
- Préparer un diff de configuration et une sauvegarde avant tout changement de politique.
- Faire relire les annonces de routage et les règles à portée large par une seconde personne.
- Définir une durée, un responsable et une condition de retrait pour chaque règle d’urgence.
- Ne jamais publier de journaux contenant des jetons, cookies, données personnelles ou secrets applicatifs dans un ticket public.
- Conserver la chronologie de l’incident, les observations, les hypothèses rejetées et les décisions, sans attribuer une intention sans preuve.
- Tester les procédures en exercice sur un environnement contrôlé, pas en lançant une attaque sur un service public.

### 3.9. Reprise après incident et post-mortem

Après stabilisation :

1. confirmer que la protection est encore nécessaire et retirer les règles temporaires devenues inutiles ;
2. comparer les indicateurs avant, pendant et après l’incident ;
3. vérifier la réussite des scénarios fonctionnels et les faux positifs ;
4. conserver les journaux et captures utiles dans un stockage à accès restreint, avec horodatage fiable ;
5. produire une chronologie et distinguer faits, hypothèses et conclusions ;
6. identifier les lacunes : capacité, supervision, contacts, contrôle d’origine, limites applicatives ou procédure ;
7. attribuer des actions de correction avec responsable et échéance ;
8. rejouer un exercice sûr pour s’assurer que la correction fonctionne.

Un post-mortem efficace cherche à améliorer le système, pas à blâmer une personne. Il indique les signaux qui auraient dû déclencher l’intervention, le délai d’escalade, la décision qui a réduit l’impact et les mesures durables nécessaires.

### 3.10. Checklist opérationnelle

**Avant incident**

- [ ] Capacité et dépendances du service documentées.
- [ ] Contacts opérateur / scrubbing vérifiés.
- [ ] Protections d’origine et chemins alternatifs contrôlés.
- [ ] Seuils de télémétrie et sondes synthétiques testés.
- [ ] Procédure de changement, relecture et retour arrière disponible.

**Pendant incident**

- [ ] Impact confirmé avec plusieurs signaux.
- [ ] Point de saturation estimé et horodaté.
- [ ] Mesures conservées avant changement.
- [ ] Mesure ciblée et réversible sélectionnée.
- [ ] Succès et faux positifs contrôlés après déploiement.
- [ ] Communications coordonnées et décisions enregistrées.

**Après incident**

- [ ] Règles temporaires réévaluées ou retirées.
- [ ] Parcours critiques validés depuis plusieurs points.
- [ ] Preuves stockées de manière sécurisée.
- [ ] Post-mortem et actions d’amélioration planifiés.

> **Danger :** le retour à la normale ne prouve pas que la cause est définitivement corrigée. Le trafic peut avoir cessé temporairement ou changé de vecteur. Maintiens une surveillance renforcée pendant une période définie, puis réduis-la seulement lorsque les métriques et les tests restent stables.


## 4. Laboratoires et exercices corrigés

### Laboratoire 1 — Identifier la métrique limitante

Un site a une liaison de 1 Gbit/s. En temps normal, il reçoit 220 Mbit/s et traite 900 000 paquets/s au maximum sur un équipement particulier. Pendant l’incident, le débit monte à 650 Mbit/s, mais l’équipement perd des paquets et son CPU de traitement atteint une limite documentée.

**Questions :**

1. Est-ce suffisant pour conclure à une saturation de bande passante ?
2. Quelle métrique complémentaire faut-il relever ?
3. Quelle serait la mauvaise première action ?

**Corrigé :** non, 650 Mbit/s est sous la capacité nominale de 1 Gbit/s. Le pps, la taille moyenne des paquets, les drops matériels, les files et la limite de traitement de l’équipement sont déterminants. Bloquer tout le trafic entrant sans identifier le protocole pourrait interrompre les services ; il faut collecter les données, localiser le goulot et coordonner une protection adaptée.

### Laboratoire 2 — Estimer le remplissage d’une file

Un service traite au maximum 120 requêtes/s. Le trafic légitime reste à 40 requêtes/s. Le trafic total mesuré se stabilise à 150 requêtes/s et la file dispose de 100 places.

**Questions :**

1. Quel est le surplus théorique par seconde ?
2. Dans le modèle simplifié, en combien de temps la file atteint-elle sa limite si la situation reste constante ?
3. Pourquoi le résultat réel peut-il varier ?

**Corrigé :** le surplus est 150 − 120 = 30 requêtes/s. La durée théorique est 100 / 30 ≈ 3,33 secondes. Le résultat réel varie avec les temps de service, la concurrence, les rafales, les rejets, les retries clients et le coût hétérogène des requêtes. Il s’agit d’un modèle pédagogique, pas d’une garantie.

### Laboratoire 3 — Choisir entre mitigation amont et règle WAF

Le trafic HTTP vers l’origine est filtré par un CDN, mais la liaison Internet est saturée par un flux UDP. Le tableau WAF indique peu d’anomalies HTTP.

**Corrigé :** le WAF HTTP ne constitue pas le point de contrôle adapté à un flux UDP qui remplit la liaison. Il faut faire intervenir l’opérateur ou une protection réseau en amont, fournir le préfixe et les métriques de trafic, et suivre la procédure autorisée. Le contrôle de l’exposition directe de l’origine reste utile mais ne remplace pas la mitigation du lien.

### Laboratoire 4 — Évaluer une limitation par IP

Une API d’entreprise limite chaque adresse IP à 20 requêtes/s. Après activation, les alertes de saturation diminuent, mais un grand client d’entreprise signale des erreurs 429 pendant ses heures de pointe.

**Corrigé :** l’IP publique peut représenter de nombreux utilisateurs derrière NAT. Il faut analyser les métriques par client et par route, ajuster le seuil à partir de la ligne de base ou ajouter des quotas par compte ou clé API. Un plafond global reste utile pour protéger le backend, mais il ne doit pas être le seul niveau de contrôle.

### Laboratoire 5 — Planifier une règle d’urgence

Tu dois ajouter une règle pour rejeter un type de trafic. Avant le changement, précise les six éléments obligatoires.

**Corrigé possible :** motif et preuve ; équipement et interface concernés ; critère de correspondance exact ; impact potentiel sur les services légitimes ; indicateurs de réussite et de faux positifs ; responsable, durée, surveillance et commande de retour arrière. Une seconde personne valide les règles à grande portée.


## 5. Points à retenir

- La mitigation doit se trouver en amont du premier goulot d’étranglement. Une ACL interne ne libère pas une liaison déjà saturée.
- Le débit en bit/s, les paquets/s, les nouvelles connexions/s, les sessions simultanées et les requêtes/s mesurent des pressions différentes.
- Une attaque applicative peut épuiser une dépendance ou une route coûteuse sans remplir la bande passante.
- La hausse de trafic n’est pas automatiquement malveillante : compare les métriques avec le comportement normal, l’identité et le contexte.
- NetFlow/IPFIX, SNMP, journaux, métriques système, journaux HTTP et captures sont complémentaires ; aucun ne donne toute l’histoire à lui seul.
- Le scrubbing, CDN/Anycast, RTBH, BGP FlowSpec, WAF et limitation de débit ont des rôles différents et des prérequis différents.
- Les règles par IP peuvent pénaliser des clients derrière NAT ; les limites doivent être ciblées et mesurées.
- CoPP protège le plan de contrôle, pas tout le trafic de transit. Des valeurs universelles arbitraires peuvent couper le routage ou l’administration.
- Chaque mesure exige un critère de succès, des métriques de faux positifs, un responsable et une possibilité de retour arrière.
- La validation s’appuie sur des transactions utilisateur, la latence, les erreurs, les files et la capacité résiduelle, pas seulement sur une baisse de trafic.
- Les journaux et captures peuvent contenir des données sensibles ; collecte, conservation et accès doivent rester proportionnés.
- Les changements de production et annonces de routage doivent être approuvés et testés selon les capacités réelles de la plateforme.

### Références et lectures complémentaires

1. IETF, **RFC 2827 — Network Ingress Filtering: Defeating Denial of Service Attacks which employ IP Source Address Spoofing** : https://www.rfc-editor.org/rfc/rfc2827
2. IETF, **RFC 3704 — Ingress Filtering for Multihomed Networks** : https://www.rfc-editor.org/rfc/rfc3704
3. IETF, **RFC 5635 — Remote Triggered Black Hole Filtering with Unicast Reverse Path Forwarding (uRPF)** : https://www.rfc-editor.org/rfc/rfc5635
4. IETF, **RFC 7999 — BLACKHOLE Community** : https://www.rfc-editor.org/rfc/rfc7999
5. IETF, **RFC 8955 — Dissemination of Flow Specification Rules** : https://www.rfc-editor.org/rfc/rfc8955
6. CISA, **Understanding and Responding to Distributed Denial-of-Service Attacks** : https://www.cisa.gov/news-events/news/understanding-and-responding-distributed-denial-service-attacks
7. OWASP, **Denial of Service Cheat Sheet** : https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
8. NIST, **SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management** : https://csrc.nist.gov/pubs/sp/800/61/r3/final
9. Cisco, documentation IOS XE consacrée à la protection du plan de contrôle, à NetFlow et à la télémétrie : https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe/products-installation-and-configuration-guides-list.html
10. NGINX, **ngx_http_limit_req_module** : https://nginx.org/en/docs/http/ngx_http_limit_req_module.html

Les exemples doivent être confrontés à la documentation correspondant à la version réelle de l’équipement ou du logiciel. Les recommandations de mitigation s’inscrivent dans un environnement administré ou explicitement autorisé.
