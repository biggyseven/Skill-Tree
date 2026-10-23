
# Attaques DDoS et mitigation - Débutant

**Niveau :** DÉBUTANT

Une attaque par déni de service cherche à rendre un système, une application ou une connexion réseau indisponible, ou à dégrader fortement ses performances. Lorsqu'une multitude de machines ou de sources participent simultanément, on parle de déni de service distribué, ou **DDoS** (*Distributed Denial of Service*). Le problème peut toucher un site Web, une API, un serveur DNS, un VPN, un pare-feu, un routeur ou même la liaison Internet d'une entreprise.

La mitigation DDoS consiste à préserver l'accès des utilisateurs légitimes, à limiter les effets du trafic malveillant et à rétablir le service. Il ne s'agit pas simplement de « bloquer une adresse IP » : les sources peuvent être très nombreuses, changer rapidement, être usurpées ou appartenir à des équipements compromis. La protection efficace combine donc préparation, observation, filtrage à plusieurs niveaux, coordination avec le fournisseur d'accès et retour d'expérience.

Ce cours présente les concepts essentiels et une méthode de travail adaptée à un débutant en réseau. Il privilégie les actions défensives, les commandes d'observation et les tests contrôlés. Les exemples sont pédagogiques : les seuils et configurations réels doivent être ajustés au trafic normal, à la capacité des équipements et aux engagements de service.

À la fin, l'apprenant doit pouvoir reconnaître les signes d'une saturation, distinguer un incident de capacité d'une panne applicative, savoir quelles informations collecter, appliquer les premières mesures sans aggraver la situation et déterminer quand solliciter l'opérateur ou un prestataire de mitigation.

> **Analogie** : imagine une boutique avec une seule porte. En période normale, les clients entrent et sont servis. Pendant un DDoS, une foule immense occupe l'entrée, parfois sans acheter quoi que ce soit. Le problème n'est pas nécessairement la qualité du vendeur : la porte, le trottoir ou la capacité de la boutique peut être saturé. Il faut gérer les files, filtrer les accès abusifs et, si la foule bloque la rue entière, demander de l'aide aux autorités qui contrôlent la rue. Un pare-feu placé à l'intérieur de la boutique ne suffit pas toujours si l'accès extérieur est déjà bouché.

---

## 1. La théorie et les algorithmes

### 1.1. DoS et DDoS : définitions

Un **DoS** (*Denial of Service*) est une action qui empêche ou dégrade l'utilisation normale d'un service. Elle peut provenir d'une seule source, d'un bogue, d'une mauvaise configuration ou d'une surcharge non malveillante. Un **DDoS** est un DoS distribué : de nombreuses sources envoient du trafic ou sollicitent une ressource de façon coordonnée ou simultanée.

Il est important de distinguer quatre situations :

| Situation | Exemple observable | Question à se poser |
|---|---|---|
| Pic légitime | Beaucoup de clients se connectent pendant une promotion | Le pic correspond-il à une activité attendue ? |
| Surcharge accidentelle | Une tâche planifiée déclenche trop de requêtes internes | Quel changement ou traitement a provoqué la charge ? |
| DoS provenant d'une source | Une seule origine consomme une ressource de façon anormale | Peut-on limiter cette source sans bloquer des utilisateurs partagés ? |
| DDoS distribué | De nombreuses sources convergent vers le même service | Où peut-on filtrer le trafic avant qu'il ne sature la capacité ? |

Un DDoS n'implique pas toujours une intrusion dans le système ciblé. Le service peut rester correctement sécurisé contre le vol de données tout en devenant inaccessible. Inversement, une panne n'est pas automatiquement un DDoS : une panne de DNS, un défaut de routage, une application bloquée ou une rupture de fibre peuvent produire des symptômes similaires.

### 1.2. Disponibilité et ressources qui peuvent être saturées

La disponibilité est la capacité à fournir le service requis lorsqu'un utilisateur autorisé en a besoin. Un attaquant peut essayer d'épuiser plusieurs types de ressources :

- **Bande passante du lien** : la quantité de données qui arrive dépasse la capacité de la connexion Internet ou d'un lien interne.
- **Capacité de traitement des paquets** : un routeur, un pare-feu, un répartiteur de charge ou une carte réseau reçoit plus de paquets par seconde qu'il ne peut en traiter.
- **État des connexions** : l'équipement conserve des tables de sessions ou de connexions qui se remplissent.
- **CPU et mémoire** : la validation, le chiffrement, le traitement de chaque requête ou la gestion des journaux consomme trop de ressources.
- **Ressources applicatives** : les fils d'exécution, connexions à la base de données, caches, files de travail ou services externes deviennent saturés.
- **Dépendances** : DNS, identité, stockage, paiement, API tierce ou réseau du fournisseur devient indisponible.

Une règle essentielle en mitigation est d'identifier **la ressource limitante**. Ajouter des serveurs Web ne résout pas forcément une liaison Internet saturée. Augmenter la bande passante ne corrige pas forcément une requête coûteuse qui consomme tout le CPU applicatif. Le bon traitement dépend de l'endroit où se forme le goulot d'étranglement.

### 1.3. Grandes familles de DDoS

Les familles suivantes sont utiles pour orienter le diagnostic. Les appellations se recoupent parfois : une campagne peut combiner plusieurs catégories.

#### A. Attaques volumétriques

Elles cherchent à remplir la capacité de transport avec un grand volume de trafic. Les indicateurs utiles sont généralement le débit entrant en bits par seconde, le nombre de paquets par seconde, l'utilisation du lien et les compteurs d'interface. Si le trafic entrant atteint la capacité du lien, le trafic légitime peut être perdu avant même d'arriver au pare-feu ou au serveur.

**Conséquence pratique :** le filtrage effectué uniquement sur le serveur peut arriver trop tard. Il faut parfois que le fournisseur d'accès, un réseau de distribution ou un service de scrubbing filtre le trafic en amont.

#### B. Attaques visant les protocoles et l'état réseau

Certaines attaques sollicitent le traitement de protocoles réseau ou les tables d'état des équipements. La charge peut se mesurer davantage en paquets par seconde, en connexions actives, en nouvelles connexions par seconde ou en taux d'abandon qu'en débit brut. Un faible volume en octets peut tout de même consommer beaucoup de CPU ou de mémoire si chaque paquet requiert un traitement coûteux.

**Conséquence pratique :** observer les compteurs de connexions, les ressources CPU, les abandons et les journaux du pare-feu. Les protections spécifiques dépendent de l'équipement et doivent être testées avant un incident.

#### C. Attaques de couche applicative

Elles ciblent un service précis, souvent HTTP ou HTTPS. Les requêtes peuvent ressembler à du trafic ordinaire, tout en demandant un traitement coûteux ou en arrivant beaucoup trop fréquemment. Les symptômes peuvent être un temps de réponse élevé, une file d'attente qui grossit, un pool de connexions épuisé ou une base de données surchargée, alors que le débit réseau ne semble pas extraordinaire.

**Conséquence pratique :** examiner les métriques applicatives, les chemins d'URL les plus sollicités, les codes de réponse, la latence et la capacité des dépendances. Il faut éviter de considérer chaque client qui envoie de nombreuses requêtes comme malveillant : des applications mobiles, des proxys et des réseaux d'entreprise peuvent partager une adresse IP publique.

#### D. Réflexion et amplification

Dans certaines attaques, des systèmes tiers répondent à une requête en envoyant une réponse plus volumineuse vers la cible. Si l'adresse source est usurpée, la victime reçoit des réponses qu'elle n'a pas demandées. Les services Internet exposés et mal configurés peuvent être abusés comme intermédiaires involontaires.

La réponse défensive comprend le filtrage des adresses source usurpées à la périphérie des réseaux, la sécurisation des services accessibles publiquement, la désactivation des services inutiles et la limitation appropriée des réponses. Une organisation doit également s'assurer qu'elle ne fournit pas elle-même un service ouvert pouvant être abusé comme amplificateur.

> **Piège :** le nom d'une attaque ne suffit pas pour choisir une mesure. Deux incidents qualifiés de « DDoS » peuvent être radicalement différents. Avant d'activer une règle, confirmez la ressource saturée, le service touché et le point de congestion.

### 1.4. Pourquoi bloquer les adresses IP ne suffit pas

Un filtrage par adresse peut aider lorsqu'une source est clairement abusive et stable. Il est moins efficace face à des milliers de sources et peut produire des faux positifs. Une adresse peut être partagée par une entreprise, un opérateur mobile, un VPN ou plusieurs clients utilisant une traduction d'adresses (NAT). Les listes d'adresses peuvent devenir obsolètes en quelques minutes. Une source affichée dans un paquet n'est pas toujours fiable si l'usurpation est possible.

La défense doit combiner plusieurs méthodes :

1. **Réduire la surface exposée** : ne publier que les services nécessaires et fermer ce qui n'est pas utilisé.
2. **Appliquer des limites proportionnées** : débit, nouvelles connexions, taille des requêtes, durée et concurrence, selon le service.
3. **Filtrer près de l'entrée** : demander au fournisseur ou au réseau de mitigation d'agir avant le goulot d'étranglement.
4. **Distribuer la charge** : CDN, caches, répartition géographique, redondance et architectures tolérantes aux pannes.
5. **Préserver le service essentiel** : prioriser les transactions importantes et permettre une dégradation contrôlée plutôt qu'un arrêt complet.
6. **Surveiller et réviser** : vérifier que la mesure réduit effectivement l'impact sans bloquer les vrais utilisateurs.

### 1.5. Indicateurs à surveiller

Un diagnostic initial s'appuie sur plusieurs sources, idéalement avec une ligne de base du trafic normal.

| Indicateur | Ce qu'il révèle | Limite d'interprétation |
|---|---|---|
| Débit entrant (bit/s) | Volume global sur un lien | Ne décrit pas le coût de chaque paquet ou requête |
| Paquets par seconde (pps) | Charge de traitement des paquets | Dépend des capacités et du type d'équipement |
| Connexions actives / nouvelles connexions | Pression sur les tables d'état | Un pic peut être légitime |
| CPU et mémoire | Saturation de l'équipement ou du serveur | Il faut savoir quel processus consomme la ressource |
| Latence et taux d'erreur | Expérience réelle des utilisateurs | Dépend de la sonde et de son emplacement |
| Codes HTTP (4xx/5xx) | Rejets, erreurs serveur ou montée de charge | Une hausse de 4xx n'indique pas à elle seule une attaque |
| Saturation des pools | Connexions DB, threads, files ou workers épuisés | Demande des métriques applicatives |
| Perte de paquets | Congestion ou problèmes réseau | Peut venir d'une panne non malveillante |

Les **bits par seconde**, les **paquets par seconde** et les **requêtes par seconde** ne sont pas interchangeables. Un flux composé de nombreux petits paquets peut surcharger le traitement sans atteindre un débit énorme. Un petit nombre de requêtes coûteuses peut épuiser l'application. C'est pourquoi un tableau de bord doit couvrir réseau, infrastructure et application.

### 1.6. Ligne de base et seuils d'alerte

Une ligne de base décrit le fonctionnement normal du service : trafic par heure et jour, pics connus, nombre moyen de sessions, distribution des temps de réponse et consommation des ressources. Il ne suffit pas de choisir un seuil universel comme « 80 % de CPU » pour tous les environnements. Une tâche normale peut produire un pic bref sans incident, tandis qu'une saturation durable à un niveau plus faible peut signaler une file d'attente en croissance.

Construisez des seuils adaptés à l'environnement :

- avertissement lorsque le débit, les connexions ou la latence s'écartent nettement de la normale ;
- alerte critique lorsque les utilisateurs échouent, que la capacité approche sa limite ou qu'une perte importante est observée ;
- durée minimale ou règle de confirmation pour limiter les alertes sur un pic transitoire ;
- seuils spécifiques aux services essentiels et à leurs dépendances ;
- alertes indépendantes du réseau pour vérifier la disponibilité depuis l'extérieur.

> **Astuce :** suivez au moins un indicateur de chaque niveau : disponibilité perçue par l'utilisateur, débit/pps réseau, ressources du pare-feu ou du répartiteur, et métriques du serveur. Le croisement de ces données rend le diagnostic beaucoup plus fiable qu'un seul graphe CPU.

### 1.7. Parcours logique de décision

Une méthode élémentaire permet de choisir la prochaine action sans improviser :

```text
                         ALERTE / PLAINTE UTILISATEUR
                                      |
                                      v
                      Confirmer l'impact et l'étendue
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
       Plusieurs services/liens ?                 Un service précis ?
                 |                                         |
                 v                                         v
      Vérifier opérateur, débit,                Vérifier latence, erreurs,
      pertes et route réseau                    journaux et dépendances
                 |                                         |
                 +--------------------+--------------------+
                                      |
                                      v
                         Identifier le goulot
                                      |
                  +-------------------+-------------------+
                  |                   |                   |
                  v                   v                   v
            Lien saturé          Équipement saturé    Application saturée
                  |                   |                   |
                  v                   v                   v
           Opérateur / CDN       Protection réseau     WAF, limites, cache,
           / scrubbing en amont  / capacité / ACL      limitation ciblée
                  |                   |                   |
                  +-------------------+-------------------+
                                      |
                                      v
                         Vérifier l'effet et les faux positifs
                                      |
                                      v
                      Documenter, communiquer, améliorer
```

Cet algorithme est une aide, pas une preuve définitive. Il peut être nécessaire de revenir à une étape précédente lorsqu'une nouvelle mesure contredit l'hypothèse de départ.

### 1.8. Défense en profondeur

La défense en profondeur consiste à répartir les protections sur plusieurs couches. Une architecture simple peut comprendre :

```text
Clients légitimes et sources malveillantes
                   |
                   v
        Fournisseur d'accès / transit
        (filtrage amont, anti-usurpation)
                   |
                   v
        CDN / service anti-DDoS / scrubbing
        (absorption et filtrage distribué)
                   |
                   v
        Routeur de bordure / pare-feu
        (ACL ciblées, protection de contrôle)
                   |
                   v
        Répartiteur de charge / WAF
        (règles HTTP, limites proportionnées)
                   |
                   v
        Application / API / base de données
        (quotas, files bornées, dégradation sûre)
```

Aucune couche n'est infaillible. Si la liaison jusqu'au site est saturée, une règle appliquée sur le serveur n'allège pas cette liaison. Si le trafic atteint le site mais coûte très cher au niveau applicatif, un simple filtrage volumétrique peut être insuffisant. La couche doit correspondre au type de ressource en danger.

> **Danger :** une protection trop agressive peut devenir elle-même un déni de service contre les utilisateurs légitimes. Un quota mal défini, un blocage géographique trop large ou une règle qui rejette tous les clients derrière un même NAT peut faire tomber le service sans attaquant. Toute mesure doit être mesurée, surveillée et réversible.


### 1.9. Simulation visuelle : trafic d'attaque, file d'attente et capacité serveur

Le schéma ci-dessous reprend la logique de la simulation de référence. Les flux bleus représentent le trafic d'attaque, le flux vert les requêtes légitimes, la file au centre les requêtes en attente et le serveur la capacité maximale de traitement. Les chiffres forment un scénario pédagogique : **35 requêtes/s d'attaque + 40 requêtes/s légitimes = 75 requêtes/s**, en dessous d'une capacité serveur de **120 requêtes/s**. Dans ce cas, la file ne grossit pas.

Le cours contient un emplacement reconnu par le frontend (`data-lesson-widget="ddos-overload-v1"`). Si le module Alpine décrit dans le kit d'intégration est installé, ce schéma de secours sera remplacé par la simulation interactive avec curseur d'attaque, compteur de file, pause et réinitialisation. Sans ce module, le schéma animé ci-dessous reste visible. Le contenu du cours n'injecte aucun JavaScript : le comportement interactif est fourni par le frontend de confiance.

### Schéma animé — Filtrer le trafic avant l’application

Ce schéma montre la différence entre les requêtes légitimes, qui continuent vers le service, et le trafic suspect, qui est arrêté par la couche de mitigation. Le diagramme reste lisible même si certaines règles CSS sont retirées : le fond, les contours et les couleurs essentielles sont définis directement dans les éléments SVG.

<div role="img" aria-label="Architecture de mitigation DDoS : les utilisateurs légitimes passent par la mitigation vers l’application ; les sources suspectes sont arrêtées et dirigées vers une zone de trafic rejeté." style="display:block;width:100%;max-width:100%;margin:1.25rem 0;padding:12px;border:1px solid #3f3f46;border-radius:18px;background:#090d14;color:#e4e4e7;overflow:hidden;box-sizing:border-box;">
  <div style="width:100%;max-width:100%;overflow-x:auto;overflow-y:hidden;box-sizing:border-box;">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" width="100%" height="auto" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="ddos-arch-title ddos-arch-desc" style="display:block;width:100%;height:auto;background:#090d14;color:#e4e4e7;">
      <title id="ddos-arch-title">Filtrage DDoS en amont de l’application</title>
      <desc id="ddos-arch-desc">Deux flux distincts : les requêtes légitimes sont acceptées par le service de mitigation ; le trafic suspect est rejeté avant l’application.</desc>
      <rect x="1" y="1" width="958" height="398" rx="16" fill="#090d14" stroke="#27272a" stroke-width="2"/>
      <text x="28" y="34" fill="#f4f4f5" font-size="19" font-family="Arial, sans-serif" font-weight="700">Filtrer tôt, préserver le trafic utile</text>
      <text x="28" y="57" fill="#a1a1aa" font-size="13" font-family="Arial, sans-serif">Flux conceptuels — aucune requête réelle n’est envoyée</text>
      <!-- Ligne légitime -->
      <rect x="26" y="83" width="220" height="92" rx="13" fill="#10251c" stroke="#4ade80" stroke-width="2"/>
      <text x="136" y="112" text-anchor="middle" fill="#f0fdf4" font-size="16" font-family="Arial, sans-serif" font-weight="700">Utilisateurs légitimes</text>
      <text x="136" y="137" text-anchor="middle" fill="#bbf7d0" font-size="13" font-family="Arial, sans-serif">Requêtes attendues</text>
      <text x="136" y="156" text-anchor="middle" fill="#86efac" font-size="12" font-family="Arial, sans-serif">Trafic utile</text>
      <path class="ddos-arch-flow ddos-arch-flow--good" d="M248 129 H354" fill="none" stroke="#4ade80" stroke-width="4" stroke-dasharray="8 12" stroke-linecap="round"/>
      <path d="M344 120 L358 129 L344 138 Z" fill="#4ade80"/>
      <circle class="ddos-arch-packet ddos-arch-packet--good" cx="275" cy="129" r="5" fill="#4ade80"/>
      <circle class="ddos-arch-packet ddos-arch-packet--good" cx="315" cy="129" r="5" fill="#4ade80"/>
      <rect x="362" y="83" width="236" height="92" rx="13" fill="#102338" stroke="#60a5fa" stroke-width="2"/>
      <text x="480" y="112" text-anchor="middle" fill="#eff6ff" font-size="16" font-family="Arial, sans-serif" font-weight="700">Mitigation DDoS</text>
      <text x="480" y="137" text-anchor="middle" fill="#bfdbfe" font-size="13" font-family="Arial, sans-serif">Analyse et filtrage</text>
      <text x="480" y="156" text-anchor="middle" fill="#93c5fd" font-size="12" font-family="Arial, sans-serif">Règles adaptées au service</text>
      <path class="ddos-arch-flow ddos-arch-flow--good" d="M600 129 H706" fill="none" stroke="#4ade80" stroke-width="4" stroke-dasharray="8 12" stroke-linecap="round"/>
      <path d="M696 120 L710 129 L696 138 Z" fill="#4ade80"/>
      <circle class="ddos-arch-packet ddos-arch-packet--good" cx="627" cy="129" r="5" fill="#4ade80"/>
      <circle class="ddos-arch-packet ddos-arch-packet--good" cx="667" cy="129" r="5" fill="#4ade80"/>
      <rect x="714" y="83" width="220" height="92" rx="13" fill="#10251c" stroke="#4ade80" stroke-width="2"/>
      <text x="824" y="112" text-anchor="middle" fill="#f0fdf4" font-size="16" font-family="Arial, sans-serif" font-weight="700">Application</text>
      <text x="824" y="137" text-anchor="middle" fill="#bbf7d0" font-size="13" font-family="Arial, sans-serif">Service disponible</text>
      <text x="824" y="156" text-anchor="middle" fill="#86efac" font-size="12" font-family="Arial, sans-serif">Trafic accepté</text>
      <!-- Ligne suspecte -->
      <rect x="26" y="227" width="220" height="92" rx="13" fill="#30171d" stroke="#fb7185" stroke-width="2"/>
      <text x="136" y="256" text-anchor="middle" fill="#fff1f2" font-size="16" font-family="Arial, sans-serif" font-weight="700">Sources suspectes</text>
      <text x="136" y="281" text-anchor="middle" fill="#fecdd3" font-size="13" font-family="Arial, sans-serif">Trafic anormal</text>
      <text x="136" y="300" text-anchor="middle" fill="#fda4af" font-size="12" font-family="Arial, sans-serif">À qualifier par des preuves</text>
      <path class="ddos-arch-flow ddos-arch-flow--bad" d="M248 273 H354" fill="none" stroke="#fb7185" stroke-width="4" stroke-dasharray="8 12" stroke-linecap="round"/>
      <path d="M344 264 L358 273 L344 282 Z" fill="#fb7185"/>
      <circle class="ddos-arch-packet ddos-arch-packet--bad" cx="275" cy="273" r="5" fill="#fb7185"/>
      <circle class="ddos-arch-packet ddos-arch-packet--bad" cx="315" cy="273" r="5" fill="#fb7185"/>
      <rect x="362" y="227" width="236" height="92" rx="13" fill="#102338" stroke="#60a5fa" stroke-width="2"/>
      <text x="480" y="256" text-anchor="middle" fill="#eff6ff" font-size="16" font-family="Arial, sans-serif" font-weight="700">Mitigation DDoS</text>
      <text x="480" y="281" text-anchor="middle" fill="#bfdbfe" font-size="13" font-family="Arial, sans-serif">Décision selon la politique</text>
      <text x="480" y="300" text-anchor="middle" fill="#93c5fd" font-size="12" font-family="Arial, sans-serif">Filtrer sans bloquer l’utile</text>
      <path class="ddos-arch-flow ddos-arch-flow--drop" d="M600 273 H706" fill="none" stroke="#fb7185" stroke-width="4" stroke-dasharray="8 12" stroke-linecap="round"/>
      <path d="M696 264 L710 273 L696 282 Z" fill="#fb7185"/>
      <rect x="714" y="227" width="220" height="92" rx="13" fill="#272126" stroke="#fb7185" stroke-width="2" stroke-dasharray="6 5"/>
      <text x="824" y="256" text-anchor="middle" fill="#fff1f2" font-size="16" font-family="Arial, sans-serif" font-weight="700">Trafic rejeté</text>
      <text x="824" y="281" text-anchor="middle" fill="#fecdd3" font-size="13" font-family="Arial, sans-serif">N’atteint pas l’application</text>
      <text x="824" y="300" text-anchor="middle" fill="#fda4af" font-size="12" font-family="Arial, sans-serif">Journaliser la décision</text>
      <rect x="26" y="344" width="908" height="36" rx="9" fill="#171b22" stroke="#3f3f46"/>
      <text x="480" y="367" text-anchor="middle" fill="#d4d4d8" font-size="13" font-family="Arial, sans-serif">Important : si le lien amont est déjà saturé, la mitigation doit agir plus près de l’opérateur.</text>
    </svg>
  </div>
</div>

<style>
.ddos-arch-flow{animation:ddos-arch-flow-motion 1.2s linear infinite}
.ddos-arch-flow--drop{animation-duration:.85s}
.ddos-arch-packet{transform-box:fill-box;transform-origin:center;animation:ddos-arch-pulse 1.25s ease-in-out infinite alternate}
.ddos-arch-packet--bad{animation-delay:.25s}
@keyframes ddos-arch-flow-motion{to{stroke-dashoffset:-40}}
@keyframes ddos-arch-pulse{from{opacity:.35;transform:scale(.72)}to{opacity:1;transform:scale(1.25)}}
@media(prefers-reduced-motion:reduce){.ddos-arch-flow,.ddos-arch-packet{animation:none!important}.ddos-arch-flow{stroke-dasharray:5 8}}
</style>

<style>
.ddos-ref{box-sizing:border-box;margin:1.2rem 0;border:1px solid #4b4d50;border-radius:26px;overflow:hidden;background:#202123;color:#f4f4f5;font-family:inherit;box-shadow:0 8px 28px rgba(0,0,0,.12)}
.ddos-ref *{box-sizing:border-box}
.ddos-ref__stage{padding:18px 20px 12px}
.ddos-ref__svg{display:block;width:100%;height:auto;min-width:620px}
.ddos-ref__scroll{overflow-x:auto;scrollbar-width:thin}
.ddos-ref__label{fill:#f1f5f9;font-size:13px;font-family:inherit}
.ddos-ref__muted{fill:#cbd5e1;font-size:11px;font-family:inherit}
.ddos-ref__blue{fill:#3b82f6}.ddos-ref__green{fill:#37d67a}.ddos-ref__white{fill:#f3f4f6}
.ddos-ref__attack-route{fill:none;stroke:#3b82f6;stroke-width:3;stroke-dasharray:3 13;stroke-linecap:round;animation:ddos-ref-flow 1.2s linear infinite}
.ddos-ref__legit-route{fill:none;stroke:#37d67a;stroke-width:3;stroke-dasharray:3 13;stroke-linecap:round;animation:ddos-ref-flow 1.2s linear infinite}
.ddos-ref__output-route{fill:none;stroke:#cbd5e1;stroke-width:3;stroke-dasharray:5 16;stroke-linecap:round;animation:ddos-ref-flow 1.8s linear infinite}
.ddos-ref__screen{fill:#2666bd;stroke:#5d9cff;stroke-width:1.4}.ddos-ref__screen--good{fill:#1d9b60;stroke:#57e39c}
.ddos-ref__device{fill:#a6bddb;stroke:#dce8fa;stroke-width:1}.ddos-ref__device--good{fill:#70d8a0;stroke:#c9f7dc;stroke-width:1}
.ddos-ref__queue{fill:#242527;stroke:#414347;stroke-width:1.2}.ddos-ref__server{fill:#249e62;stroke:#6ee7a4;stroke-width:1.1}
.ddos-ref__server-line{stroke:#9ae6b4;stroke-width:1.2}
.ddos-ref__separator{border-top:1px solid #45464a}
.ddos-ref__summary{padding:16px 20px 18px;text-align:center;color:#d4d4d8;font-size:.98rem}
.ddos-ref__summary strong{color:#fff}
.ddos-ref__legend{display:flex;flex-wrap:wrap;justify-content:center;gap:.6rem 1.2rem;padding:0 16px 14px;color:#d4d4d8;font-size:.8rem}
.ddos-ref__key{display:inline-flex;align-items:center;gap:.45rem}.ddos-ref__dot{width:.62rem;height:.62rem;border-radius:50%;display:inline-block}.ddos-ref__dot--blue{background:#3b82f6}.ddos-ref__dot--green{background:#37d67a}.ddos-ref__dot--grey{background:#cbd5e1}
.ddos-ref__note{margin:0;padding:12px 18px 16px;border-top:1px solid #45464a;color:#cbd5e1;font-size:.82rem}
@keyframes ddos-ref-flow{to{stroke-dashoffset:-64}}
@media(prefers-reduced-motion:reduce){.ddos-ref__attack-route,.ddos-ref__legit-route,.ddos-ref__output-route{animation:none;stroke-dasharray:4 9}}
@media(max-width:640px){.ddos-ref__stage{padding:12px 12px 8px}.ddos-ref__summary{font-size:.9rem}.ddos-ref__svg{min-width:620px}}
</style>

<div class="ddos-sim-slot" data-lesson-widget="ddos-overload-v1" role="region" aria-label="Simulation DDoS : flux, file d'attente et capacité serveur">
  <div class="ddos-ref" style="box-sizing:border-box;margin:1.2rem 0;border:1px solid #4b4d50;border-radius:26px;overflow:hidden;background:#202123;color:#f4f4f5;font-family:inherit;box-shadow:0 8px 28px rgba(0,0,0,.12);">
    <div class="ddos-ref__stage" style="padding:18px 20px 12px;background:#202123;color:#f4f4f5;">
      <div class="ddos-ref__scroll" style="width:100%;max-width:100%;overflow-x:auto;overflow-y:hidden;">
        <svg class="ddos-ref__svg" style="display:block;width:100%;height:auto;background:#202123;" viewBox="0 0 900 320" role="img" aria-labelledby="ddos-ref-title ddos-ref-desc" xmlns="http://www.w3.org/2000/svg">
          <title id="ddos-ref-title">Trafic DDoS et capacité du serveur</title>
          <desc id="ddos-ref-desc">Trois flux bleus d'attaque et un flux vert légitime convergent vers une file d'attente. Le serveur peut traiter 120 requêtes par seconde et en reçoit 75 dans ce scénario.</desc>
          <text fill="#60a5fa" font-family="Arial, sans-serif" x="56" y="26" class="ddos-ref__label ddos-ref__blue" font-weight="700">Attack 35 /s</text>
          <text fill="#37d67a" font-family="Arial, sans-serif" x="56" y="298" class="ddos-ref__label ddos-ref__green" font-weight="700">Legitimate 40 /s</text>
          <path class="ddos-ref__attack-route" d="M104 68 L360 162"/>
          <path class="ddos-ref__attack-route" d="M104 128 L360 168" style="animation-delay:-.35s"/>
          <path class="ddos-ref__attack-route" d="M104 188 L360 174" style="animation-delay:-.7s"/>
          <path class="ddos-ref__legit-route" d="M104 246 L360 180"/>
          <g transform="translate(64 49)"><rect class="ddos-ref__screen" x="2" y="0" width="35" height="24" rx="2"/><path d="M5 3 H34 V19 H5 Z" fill="#60a5fa"/><path class="ddos-ref__device" d="M0 25 H39 L45 33 H-5 Z"/><path d="M10 28 H29" stroke="#64748b" stroke-width="1.6"/></g>
          <g transform="translate(64 109)"><rect class="ddos-ref__screen" x="2" y="0" width="35" height="24" rx="2"/><path d="M5 3 H34 V19 H5 Z" fill="#60a5fa"/><path class="ddos-ref__device" d="M0 25 H39 L45 33 H-5 Z"/><path d="M10 28 H29" stroke="#64748b" stroke-width="1.6"/></g>
          <g transform="translate(64 169)"><rect class="ddos-ref__screen" x="2" y="0" width="35" height="24" rx="2"/><path d="M5 3 H34 V19 H5 Z" fill="#60a5fa"/><path class="ddos-ref__device" d="M0 25 H39 L45 33 H-5 Z"/><path d="M10 28 H29" stroke="#64748b" stroke-width="1.6"/></g>
          <g transform="translate(64 227)"><rect class="ddos-ref__screen ddos-ref__screen--good" x="2" y="0" width="35" height="24" rx="2"/><path d="M5 3 H34 V19 H5 Z" fill="#4ade80"/><path class="ddos-ref__device ddos-ref__device--good" d="M0 25 H39 L45 33 H-5 Z"/><path d="M10 28 H29" stroke="#166534" stroke-width="1.6"/></g>
          <text fill="#e4e4e7" font-family="Arial, sans-serif" x="405" y="70" text-anchor="middle" class="ddos-ref__label">Wait ~0 s</text>
          <text fill="#e4e4e7" font-family="Arial, sans-serif" x="405" y="93" text-anchor="middle" class="ddos-ref__label" font-weight="700">Queue 0/80</text>
          <rect class="ddos-ref__queue" x="358" y="116" width="98" height="94" rx="12"/>
          <path d="M368 194 H446" stroke="#2e3033" stroke-width="1"/>
          <path class="ddos-ref__output-route" d="M456 163 L522 163"/>
          <path d="M517 156 L526 163 L517 170" fill="none" stroke="#d4d4d8" stroke-width="2"/>
          <g transform="translate(540 124)">
            <rect class="ddos-ref__server" x="0" y="0" width="35" height="24" rx="3"/><rect class="ddos-ref__server" x="0" y="28" width="35" height="24" rx="3"/><rect class="ddos-ref__server" x="0" y="56" width="35" height="24" rx="3"/>
            <path class="ddos-ref__server-line" d="M5 7 H30 M5 14 H30 M5 35 H30 M5 42 H30 M5 63 H30 M5 70 H30"/>
            <circle cx="6" cy="4" r="1.5" fill="#dcfce7"/><circle cx="6" cy="32" r="1.5" fill="#dcfce7"/><circle cx="6" cy="60" r="1.5" fill="#dcfce7"/>
          </g>
          <text fill="#e4e4e7" font-family="Arial, sans-serif" x="557" y="225" text-anchor="middle" class="ddos-ref__label" font-weight="700">Capacity</text>
          <text fill="#e4e4e7" font-family="Arial, sans-serif" x="557" y="244" text-anchor="middle" class="ddos-ref__label" font-weight="700">120 /s</text>
          <path class="ddos-ref__output-route" d="M594 163 H836"/>
          <path d="M827 156 L840 163 L827 170" fill="none" stroke="#d4d4d8" stroke-width="3"/>
          <circle cx="642" cy="163" r="5" fill="#37d67a"/><circle cx="730" cy="163" r="5" fill="#37d67a"/>
          <text fill="#e4e4e7" font-family="Arial, sans-serif" x="748" y="100" text-anchor="middle" class="ddos-ref__label" font-weight="700">75 /s served</text>
        </svg>
      </div>
    </div>
    <div class="ddos-ref__separator" style="border-top:1px solid #45464a;"></div>
    <div class="ddos-ref__summary" style="padding:16px 20px 18px;text-align:center;background:#202123;color:#d4d4d8;font-size:.98rem;"><strong>75 /s</strong> arrive within <strong>120 /s</strong> capacity, so no backlog grows.</div>
    <div class="ddos-ref__legend" style="display:flex;flex-wrap:wrap;justify-content:center;gap:.6rem 1.2rem;padding:0 16px 14px;background:#202123;color:#d4d4d8;font-size:.8rem;"><span class="ddos-ref__key"><span class="ddos-ref__dot ddos-ref__dot--blue"></span>Trafic d'attaque (illustratif)</span><span class="ddos-ref__key"><span class="ddos-ref__dot ddos-ref__dot--green"></span>Trafic légitime</span><span class="ddos-ref__key"><span class="ddos-ref__dot ddos-ref__dot--grey"></span>Traitement du serveur</span></div>
    <p class="ddos-ref__note" style="margin:0;padding:12px 18px 16px;border-top:1px solid #45464a;background:#202123;color:#cbd5e1;font-size:.82rem;"><strong>À retenir :</strong> quand le trafic total dépasse la capacité, la file commence à croître. Lorsqu'elle est pleine, les nouvelles requêtes excédentaires peuvent être rejetées. Le module interactif permet de faire varier le trafic d'attaque et d'observer cette transition.</p>
  </div>
</div>

<details>
  <summary><strong>Comment interpréter cette simulation ?</strong></summary>
  <ol>
    <li>Le trafic total est la somme des requêtes d'attaque et des requêtes légitimes.</li>
    <li>Si le trafic total reste inférieur à la capacité de traitement, le serveur peut absorber l'arrivée sans accumuler de file.</li>
    <li>Si le trafic dépasse durablement la capacité, la file croît jusqu'à sa limite ; les requêtes en trop risquent alors d'être abandonnées.</li>
    <li>Ce modèle est volontairement simplifié : dans un vrai système, les limites peuvent provenir du réseau, du pare-feu, du répartiteur, du CPU, de la base de données ou d'une dépendance externe.</li>
  </ol>
</details>

> **Astuce :** pour le lecteur de cours, garde le schéma de secours dans le Markdown et monte le composant Alpine à partir de `data-lesson-widget="ddos-overload-v1"` après le nettoyage DOMPurify. Le JavaScript et le CSS de la version interactive doivent rester dans les fichiers du frontend, et non dans le contenu fourni par les cours.

---

## 2. Configuration et pratique

Cette section propose un laboratoire défensif. Les commandes sont principalement des commandes d'observation et les configurations sont des exemples à adapter. Ne copiez pas une ACL ou une politique de limitation dans un réseau de production sans comprendre les règles existantes, disposer d'un accès de secours et définir une procédure de retour arrière.

### 2.1. Préparer un inventaire minimal

Avant un incident, consignez les informations suivantes :

| Élément | Information à enregistrer |
|---|---|
| Services publics | Noms DNS, adresses IP, ports et protocoles exposés |
| Dépendances | DNS, CDN, API, base de données, identité, stockage |
| Capacité | Débit souscrit, limites des équipements, limites contractuelles |
| Interlocuteurs | Opérateur, hébergeur, fournisseur anti-DDoS, équipe système |
| Surveillance | Tableaux de bord, alertes, sondes externes, journaux |
| Accès d'urgence | Portail hors bande, accès console, procédure d'authentification |
| Changements | Dernières mises à jour, règles ajoutées, déploiements récents |
| Retour arrière | Configuration sauvegardée et personne habilitée à restaurer |

Conservez les contacts et les identifiants de contrat dans un emplacement de gestion sécurisé et accessible durant un incident. Il ne faut pas dépendre d'un seul service SSO, d'un seul e-mail ou d'une plateforme hébergée sur le domaine qui est en panne pour déclencher les actions d'urgence.

### 2.2. Exemple de topologie de laboratoire

L'entreprise fictive **Alpha** publie un site Web et une API. Les utilisateurs passent par un service CDN/anti-DDoS ; le trafic propre est ensuite envoyé vers un répartiteur de charge et deux serveurs applicatifs. Le réseau dispose d'un routeur de bordure et d'un pare-feu. Un serveur de supervision observe le débit, la latence et les codes d'erreur.

```text
                         Internet
                            |
                   +------------------+
                   | CDN / Anti-DDoS  |
                   +------------------+
                            |
                    Trafic filtré
                            |
                   +------------------+
                   | Routeur / Pare-feu|
                   +------------------+
                            |
                   +------------------+
                   | Load balancer /  |
                   | WAF              |
                   +------------------+
                      /           \
                     v             v
              +-----------+  +-----------+
              | Web/API 1 |  | Web/API 2 |
              +-----------+  +-----------+
                     \             /
                      v           v
                    +----------------+
                    | Base de données|
                    +----------------+

     Supervision indépendante : débit, pps, latence, erreurs, CPU
```

Dans un environnement réel, le CDN et le service anti-DDoS peuvent être intégrés ou séparés. Le routage des flux et l'architecture de filtrage varient selon le prestataire. Il faut vérifier comment le trafic contournerait ou non le CDN : si l'adresse d'origine est directement accessible, un attaquant peut potentiellement tenter de joindre cette adresse au lieu de passer par la protection applicative.

### 2.3. Vérifier l'état du routeur Cisco IOS/IOS XE

Les commandes suivantes servent à observer l'état d'un équipement Cisco. La disponibilité exacte dépend de la plateforme et de la version logicielle.

```text
show clock
show interfaces
show interfaces <interface>
show ip traffic
show processes cpu sorted
show processes memory sorted
show logging
show ip route
show access-lists
```

Objectif des commandes :

- `show clock` vérifie l'heure de l'équipement, utile pour corréler les événements.
- `show interfaces` affiche notamment l'état de l'interface, les compteurs de trafic, les erreurs et les abandons.
- `show ip traffic` expose des compteurs IP disponibles selon la plateforme.
- `show processes cpu sorted` aide à identifier une charge CPU élevée et les processus associés.
- `show processes memory sorted` donne des indications sur la mémoire consommée.
- `show logging` permet de corréler les messages avec l'heure de l'incident.
- `show ip route` vérifie le chemin de routage vers la destination.
- `show access-lists` permet de lire les ACL et, si la plateforme fournit ces compteurs, les correspondances de règles.

Ces commandes sont des points de départ et ne remplacent pas la télémétrie de l'opérateur. Certains compteurs peuvent être agrégés, différés, influencés par l'échantillonnage ou différents selon l'architecture matérielle.

> **Astuce :** commencez par relever une capture des valeurs et de l'heure avant de modifier quoi que ce soit. Répétez les mêmes observations après une mesure. Sans état initial, il sera difficile de prouver qu'une modification a amélioré la situation.

### 2.4. Lire les signes d'un problème de capacité

Une observation isolée ne prouve rien. Cherchez plusieurs indices qui évoluent au même moment :

- trafic entrant qui augmente rapidement ;
- interface proche de sa capacité ou compteur d'abandons qui progresse ;
- latence et perte de paquets qui augmentent depuis plusieurs sondes ;
- CPU ou mémoire élevés sur le pare-feu, le répartiteur ou le serveur ;
- explosion du nombre de connexions ou de requêtes ;
- hausse des réponses HTTP 5xx ou des délais d'expiration ;
- plainte simultanée de plusieurs utilisateurs et de plusieurs fournisseurs d'accès.

La dernière observation est utile : si seules les connexions d'un seul site distant échouent, il peut s'agir d'un problème de chemin réseau ou de résolution DNS. Si plusieurs sondes externes et de nombreux utilisateurs échouent au même instant et que le lien est saturé, une surcharge réseau est plus plausible.

### 2.5. Limiter les requêtes HTTP au niveau applicatif

La limitation de débit (*rate limiting*) permet de fixer une cadence maximale pour certaines actions, par exemple un formulaire de recherche ou une API coûteuse. Elle doit tenir compte du profil normal, du coût de la requête et de la façon dont les utilisateurs partagent une adresse IP. Une limite par IP uniquement peut pénaliser un campus, une entreprise ou un opérateur mobile entier.

Voici un exemple minimal de configuration Nginx illustrant le principe. Il ne constitue pas une valeur universelle de production : le chemin, la clé, le taux et le comportement en cas de dépassement doivent être validés avec les développeurs et mesurés sur une charge normale.

```nginx
http {
    # Exemple pédagogique : zone de limitation par adresse cliente.
    # Choisir la bonne IP cliente si un proxy/CDN est présent.
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 443 ssl;
        server_name api.exemple.invalid;

        location /api/recherche {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://application_backend;
        }
    }
}
```

Points importants :

1. `rate=10r/s` et `burst=20` sont des valeurs d'exemple, pas des recommandations générales.
2. Si Nginx voit uniquement l'adresse du CDN ou d'un proxy, la limitation peut s'appliquer à tous les utilisateurs comme s'ils étaient une seule source. Si l'adresse cliente est restaurée à partir d'un en-tête, cette confiance doit être limitée aux proxys autorisés ; ne faites pas confiance à un en-tête client arbitraire.
3. Le mécanisme protège une partie de la couche applicative, mais ne résout pas une saturation du lien Internet située avant le serveur.
4. Après validation de la syntaxe et sauvegarde de la configuration, déployez progressivement, surveillez les codes 429/503, la latence et les plaintes, puis ajustez ou restaurez la version précédente si les faux positifs sont trop nombreux.

Pour beaucoup d'applications, la limitation est plus efficace lorsqu'elle s'applique à une action coûteuse qu'à l'ensemble du site : connexion, recherche complexe, génération de PDF, envoi d'e-mail, création de session ou endpoint d'API. Elle doit être complétée par l'authentification, des quotas par compte, des files de travail bornées et des délais d'expiration.

### 2.6. Utiliser un CDN ou un service anti-DDoS

Un CDN sert souvent du contenu mis en cache depuis des points de présence proches de l'utilisateur. Un service anti-DDoS peut en plus analyser et filtrer les flux. Les fonctionnalités exactes varient selon le fournisseur et le forfait.

Lors du déploiement, vérifiez :

- que les domaines publics passent bien par le service prévu ;
- que l'origine n'est pas exposée inutilement et que l'accès direct est contrôlé ;
- que les certificats TLS, les en-têtes de proxy et les adresses clientes sont traités correctement ;
- que les règles WAF sont en mode observation avant un blocage généralisé, lorsque c'est possible ;
- que les fichiers statiques sont mis en cache avec des règles cohérentes ;
- que les endpoints dynamiques et les API ont leurs propres limites ;
- que le service de secours ne dépend pas d'une adresse, d'une résolution DNS ou d'un canal de gestion inaccessible durant l'incident ;
- que le contrat précise l'escalade, les notifications, les plafonds, les coûts et les limites de protection.

Un service de mitigation ne remplace pas la maintenance des serveurs, la protection des comptes, les mises à jour ou une architecture résiliente. Le DDoS peut n'être qu'un volet d'un incident plus large.

### 2.7. Filtrage sur routeur et pare-feu : principes prudents

Une ACL peut bloquer un protocole ou un port qui ne doit pas être accessible, mais une ACL générique de « blocage DDoS » n'existe pas. Les règles doivent refléter l'architecture : destinations publiques, ports requis, interfaces et politique d'accès. Une ACL trop large peut interrompre les services normaux ou bloquer l'administration.

Avant d'ajouter une règle :

1. sauvegardez la configuration et identifiez un accès de secours ;
2. documentez l'objectif exact, la source, la destination, le protocole et le sens du flux ;
3. confirmez que le trafic n'est pas nécessaire à un service métier ;
4. appliquez la règle au point approprié, de préférence en amont du goulot si le fournisseur peut intervenir ;
5. observez les compteurs et les journaux ;
6. définissez le critère d'arrêt et le moyen de retour arrière.

Les protections contre l'usurpation d'adresse source, les listes de contrôle de plan de contrôle, la limitation de trafic vers les services d'infrastructure et les mécanismes anti-DDoS propriétaires doivent être utilisés conformément à la documentation de la plateforme. Évitez d'activer une commande copiée d'un autre modèle d'équipement sans vérifier sa signification et ses effets.

### 2.8. Mitigation en amont : quand appeler l'opérateur

Si le lien Internet est saturé, le personnel sur site ne peut pas créer de capacité supplémentaire en filtrant sur le pare-feu qui se trouve derrière le lien. Contactez l'opérateur ou le fournisseur anti-DDoS lorsque :

- l'utilisation du lien atteint durablement la capacité disponible ;
- plusieurs services sont inaccessibles en même temps ;
- des compteurs et sondes montrent une forte perte de paquets en bordure ;
- l'interface de l'équipement est sous pression avant que les règles locales puissent traiter le trafic ;
- la campagne dépasse les capacités ou les responsabilités de l'organisation.

Préparez une fiche d'appel contenant : nom du client et identifiant de contrat, adresses IP ou préfixes touchés, noms de services et ports, heure de début avec fuseau, métriques avant/après, topologie simplifiée, impact métier, changements récents et contacts disponibles. Demandez quelle mesure l'opérateur envisage, son effet secondaire possible et comment sera confirmé le retour à la normale.

Deux mécanismes réseau sont fréquemment cités dans les discussions opérateur :

- **RTBH (Remote Triggered Black Hole)** : détourner vers une route de rejet le trafic destiné à une adresse ou un préfixe. C'est une mesure de dernier recours qui peut rendre la cible totalement inaccessible, mais qui peut protéger le reste du réseau.
- **BGP FlowSpec** : distribuer certaines règles de filtrage à des routeurs capables de les appliquer. Son usage demande une politique, des équipements compatibles et une coordination avec l'opérateur.

Ces mécanismes ne doivent pas être déclenchés au hasard. Leur portée peut dépasser un service unique, et leur configuration est généralement réservée aux équipes réseau expérimentées ou au fournisseur.

### 2.9. Exercices pratiques guidés

#### Laboratoire A — établir le comportement normal

1. Sélectionnez un service de test dont vous êtes responsable.
2. Relevez pendant une période normale le débit entrant, la latence, le taux d'erreur et la consommation CPU.
3. Notez l'heure et la fréquence de collecte.
4. Effectuez uniquement les vérifications fonctionnelles autorisées : connexion au site, résolution DNS et requête applicative simple.
5. Conservez les résultats dans un tableau et identifiez les variations habituelles.

N'effectuez pas de test de charge non autorisé. Pour valider la capacité, utilisez un environnement isolé, un outil de test approuvé et des seuils convenus avec le propriétaire du service.

#### Laboratoire B — simuler la décision sans générer d'attaque

Supposons que les graphiques indiquent : le débit entrant reste faible, le CPU applicatif atteint sa limite, les erreurs 5xx montent et un endpoint de recherche est beaucoup plus sollicité que les autres.

Questions :

1. Le premier goulot semble-t-il être la liaison Internet ou l'application ?
2. Quels journaux et métriques faut-il comparer ?
3. Une limite par IP peut-elle créer des faux positifs ?
4. Quelle mesure réversible peut être testée en premier ?

Réponse indicative : les indices pointent vers l'application, mais doivent être confirmés par les métriques de base de données, de concurrence et de latence. Examinez la répartition des requêtes, le coût de l'endpoint et les dépendances. Une limitation ciblée ou un cache peut être testé progressivement ; fixez une limite adaptée au trafic normal et surveillez les clients légitimes. Si le trafic reste normal mais que le service échoue après un déploiement récent, vérifiez aussi le changement applicatif.

#### Laboratoire C — préparer une fiche d'incident

Remplissez cette fiche pour un incident fictif :

| Champ | Exemple à consigner |
|---|---|
| Heure de début | 14:03 UTC, à confirmer |
| Impact | API lente, erreurs 5xx sur certaines opérations |
| Étendue | Un service public, deux régions d'utilisateurs |
| Réseau | Pas de saturation prouvée à ce stade |
| Application | Latence et concurrence en hausse |
| Changement récent | Nouvelle version déployée à 13:55 UTC |
| Hypothèse | Bug applicatif ou trafic anormal, à distinguer |
| Action initiale | Préserver les mesures, vérifier le déploiement, ne pas bloquer en masse |
| Critère de succès | Latence et erreurs reviennent au niveau de référence |

L'exercice est réussi lorsque les faits sont séparés des hypothèses et que chaque action a un résultat attendu mesurable.

---

## 3. Dépannage et sécurité

### 3.1. Reconnaître un DDoS sans conclure trop vite

Une alerte crédible repose sur des observations corrélées. Les symptômes possibles comprennent :

- augmentation rapide ou anormale du débit, des paquets ou des requêtes ;
- connexions qui expirent alors que le serveur est allumé ;
- échecs depuis plusieurs régions ou opérateurs ;
- interface réseau proche de sa capacité, pertes ou abandons en hausse ;
- forte utilisation CPU ou mémoire sur un équipement réseau ;
- hausse des délais de réponse, des codes 5xx ou des connexions refusées ;
- journaux contenant des motifs de requêtes répétitifs ou une répartition inhabituelle des sources ;
- alertes du fournisseur ou du CDN indiquant une activité anormale.

Aucun de ces signes isolément ne constitue une preuve. Par exemple, un déploiement défectueux peut créer des erreurs 5xx sans trafic anormal. Une mise à jour d'application peut augmenter la consommation CPU ; une panne DNS peut faire croire que le serveur est inaccessible. Le diagnostic compare les données réseau, applicatives et les changements récents.

### 3.2. Procédure de réponse à incident

Une procédure simple peut être divisée en sept phases.

**Phase 1 — Confirmer et qualifier.** Vérifiez les alertes depuis plusieurs sondes, demandez des exemples d'erreurs aux utilisateurs, définissez le service et l'impact. Notez l'heure et le fuseau. Confirmez que l'équipe répond à un incident réel avant de bloquer quoi que ce soit.

**Phase 2 — Préserver les informations.** Sauvegardez les graphiques, compteurs, journaux pertinents et changements récents. Les journaux doivent couvrir la période avant, pendant et après l'incident. Utilisez des horloges synchronisées et enregistrez la méthode de collecte.

**Phase 3 — Localiser le goulot.** Déterminez si le lien, le routeur, le pare-feu, le répartiteur, l'application ou une dépendance est saturé. Cherchez le premier point où le trafic utile ou le traitement attendu échoue.

**Phase 4 — Choisir une mesure proportionnée.** Les options peuvent inclure l'activation d'une protection anti-DDoS existante, une limitation ciblée, une règle WAF, le cache de contenu statique, l'arrêt temporaire d'une fonction coûteuse, l'augmentation contrôlée de capacité ou l'escalade vers l'opérateur. Choisissez la mesure qui agit sur la ressource en cause.

**Phase 5 — Coordonner et communiquer.** Nommez un responsable de l'incident, répartissez les rôles, informez le fournisseur et les interlocuteurs métier. Les messages externes doivent être factuels et validés ; ne publiez pas inutilement des détails sur l'architecture ou les règles de défense.

**Phase 6 — Mesurer l'effet.** Comparez avant et après : disponibilité, latence, taux d'erreur, débit, perte, CPU, coût et plaintes. Une mesure qui réduit le trafic mais fait chuter le taux de réussite des utilisateurs n'est pas une réussite.

**Phase 7 — Stabiliser et apprendre.** Lorsque la situation est maîtrisée, retirez les règles temporaires devenues inutiles, rétablissez les fonctions désactivées, vérifiez le service depuis l'extérieur et documentez les leçons. N'enlevez pas une protection active uniquement parce que le trafic a commencé à baisser : coordonnez la désactivation et surveillez l'éventuel retour de la campagne.

### 3.3. Éviter les erreurs fréquentes

| Erreur | Pourquoi c'est risqué | Bonne pratique |
|---|---|---|
| Bloquer immédiatement toutes les sources inhabituelles | Les sources peuvent être légitimes, partagées ou usurpées | Confirmer les motifs et commencer par une règle ciblée et réversible |
| Ajouter une ACL très large | Peut couper le service ou l'accès d'administration | Écrire, relire et tester une règle fondée sur le besoin réel |
| Augmenter simplement la capacité du serveur | Le lien ou le pare-feu peut être le goulot | Localiser d'abord la ressource saturée |
| Redémarrer tous les équipements | Efface des indices et peut aggraver l'indisponibilité | Collecter l'état puis intervenir selon un plan approuvé |
| Activer une limite très restrictive | Les vrais clients sont rejetés, notamment derrière un NAT | Observer le trafic normal, choisir un seuil adapté, surveiller les faux positifs |
| Laisser l'origine accessible derrière un CDN | Le trafic peut contourner la protection prévue | Restreindre l'origine aux chemins et proxys autorisés |
| Désactiver toutes les fonctions pour soulager le CPU | Le service métier peut devenir inutilisable | Dégrader uniquement la fonction coûteuse et préserver les fonctions essentielles |
| Conserver des règles d'urgence indéfiniment | Elles deviennent difficiles à comprendre et créent une dette de sécurité | Définir propriétaire, date d'expiration et revue post-incident |

> **Piège :** une hausse du trafic peut être la conséquence d'un événement réel, d'une boucle applicative ou d'une configuration erronée. Les mêmes mesures de protection doivent être envisagées, mais la cause doit être comprise avant de conclure à une attaque malveillante.

### 3.4. Sécurité et limites de la collecte

Les journaux et captures contiennent potentiellement des adresses IP, noms de clients, URL, jetons, identifiants ou autres informations sensibles. Collectez uniquement ce qui est nécessaire, limitez l'accès, protégez le stockage, définissez une durée de conservation et appliquez les règles de confidentialité de l'organisation.

Ne partagez pas un fichier de capture complet sur une messagerie publique pour « demander de l'aide ». Supprimez ou masquez les secrets et données personnelles lorsqu'ils ne sont pas nécessaires. Les dossiers d'incident doivent distinguer les faits techniques, les hypothèses, les actions et les décisions. Les journaux d'un fournisseur peuvent utiliser un fuseau horaire différent : notez-le pour éviter une corrélation incorrecte.

### 3.5. Sécuriser les services exposés

La prévention commence bien avant une attaque :

- désactivez les services publics inutiles ;
- mettez à jour les systèmes et bibliothèques exposés ;
- configurez les DNS publics de façon à ne pas fournir de service récursif ouvert ;
- appliquez des limites appropriées aux requêtes DNS et aux API ;
- empêchez autant que possible l'usurpation d'adresse source à la périphérie de vos réseaux ;
- protégez les plans de contrôle des routeurs et pare-feu ;
- bornez les files de travail et le nombre de connexions ;
- utilisez des délais d'expiration et limitez la taille des entrées ;
- mettez en cache les contenus sûrs et peu changeants ;
- séparez les fonctions essentielles des opérations coûteuses ;
- testez les plans de continuité et de reprise ;
- vérifiez que la protection couvre IPv4 et IPv6, si les deux sont utilisés.

Les CAPTCHA et l'authentification ne sont pas des solutions universelles au DDoS. Ils peuvent protéger certaines fonctions applicatives, mais peuvent arriver trop tard pour un lien saturé et ajouter eux-mêmes un coût de traitement. Les protections doivent être placées au bon niveau et leur effet mesuré.

### 3.6. Dégradation contrôlée et priorités métier

Une application résiliente n'a pas forcément besoin de préserver toutes ses fonctions pendant un incident. Elle peut continuer à fournir les fonctions essentielles tout en désactivant temporairement des services non critiques. C'est la **dégradation contrôlée**.

Exemples de mesures à préparer à l'avance :

- afficher une page statique en cas de forte charge ;
- servir des ressources statiques depuis le CDN ;
- mettre temporairement en pause une génération lourde de rapports ;
- mettre en file les tâches différables avec une limite de taille ;
- limiter les recherches complexes ou les requêtes coûteuses ;
- désactiver une intégration tierce non essentielle ;
- définir des quotas différents selon le niveau de service autorisé.

Chaque mode dégradé doit avoir un propriétaire, des critères d'activation, une durée maximale, un message utilisateur et une procédure de restauration. Sans préparation, une fonction désactivée en urgence risque d'être oubliée ou de corrompre des opérations métier.

### 3.7. Déterminer quand escalader

Faites immédiatement appel au responsable réseau ou à l'opérateur lorsque la liaison est saturée, que plusieurs services réseau tombent simultanément, que le trafic atteint une capacité en amont du site ou que les équipements critiques deviennent instables. Sollicitez l'équipe applicative lorsque les graphes réseau ne montrent pas de saturation mais que le CPU, les files, la base de données ou la latence augmentent. Faites intervenir l'équipe sécurité lorsque les indices suggèrent une campagne coordonnée, une tentative d'extorsion, une intrusion associée ou un abus de services exposés.

L'escalade n'est pas un échec : c'est une mesure de maîtrise du risque. L'important est de transmettre des faits exploitables et de garder un journal des actions pour éviter que plusieurs équipes appliquent simultanément des changements contradictoires.

### 3.8. Post-mortem et amélioration continue

Après la résolution, rédigez un retour d'expérience sans chercher à désigner un coupable. Il doit répondre aux questions suivantes :

1. Quel service et quels utilisateurs ont été touchés ?
2. Quand l'incident a-t-il commencé, atteint son maximum et pris fin ?
3. Quels éléments ont confirmé ou infirmé l'hypothèse DDoS ?
4. Quelle ressource était le goulot d'étranglement ?
5. Quelles mesures ont été appliquées et quels effets ont-elles produits ?
6. Y a-t-il eu des faux positifs ou des fonctions métier bloquées ?
7. Qu'est-ce qui a bien fonctionné : alertes, procédures, contacts, automatisation ?
8. Quelles actions correctives ont un responsable et une échéance ?

Mesurez des indicateurs utiles, par exemple le délai entre la détection et l'escalade, le temps de rétablissement, la proportion d'utilisateurs affectés, le nombre de modifications d'urgence, et le taux de faux positifs. Ne cherchez pas uniquement à produire plus d'alertes : l'objectif est de détecter l'impact tôt et de prendre de bonnes décisions.

### 3.9. Cas pratique corrigé : site inaccessible

**Situation :** à 10 h 15, le site de l'entreprise devient très lent. Le tableau de bord indique un débit entrant normal, mais les réponses HTTP 5xx et la latence augmentent. Le CPU des serveurs Web est très élevé. La base de données présente aussi davantage de requêtes longues. Un nouveau filtre de recherche a été déployé vingt minutes auparavant.

**Étape 1 — Faits :** hausse des 5xx, latence, CPU et requêtes longues ; pas de saturation réseau confirmée ; déploiement récent.

**Étape 2 — Hypothèses :** le nouveau filtre coûte trop cher, un trafic réel sollicite davantage ce filtre ou une activité anormale l'exploite. Les faits ne permettent pas encore d'affirmer qu'il s'agit d'un DDoS.

**Étape 3 — Collecte :** comparer les requêtes par route et par statut HTTP, la latence de base de données, les plans d'exécution disponibles, la concurrence, les logs du déploiement et les métriques de trafic par origine si elles sont fiables. Préserver les données avant de redémarrer.

**Étape 4 — Action réversible :** selon le processus de changement, rétablir la version précédente ou désactiver temporairement le filtre coûteux, puis surveiller les métriques. Si les indices montrent aussi un grand volume de requêtes anormales, activer une limite ciblée au niveau WAF ou API en gardant une surveillance des clients légitimes.

**Étape 5 — Validation :** vérifier que la latence, les 5xx et les requêtes longues reviennent à leur niveau normal. Tester les fonctions métier principales depuis plusieurs points d'accès. Confirmer qu'aucune règle temporaire ne bloque les opérations ordinaires.

**Conclusion :** le bon réflexe n'est pas de bloquer immédiatement toutes les adresses sources. Il est de localiser la ressource saturée, vérifier le changement récent, tester une correction proportionnée et ne qualifier l'incident de DDoS que lorsque les preuves le soutiennent.

---

## Points à retenir

- Un DoS rend un service indisponible ou dégradé ; un DDoS fait intervenir de nombreuses sources.
- Il existe des attaques volumétriques, protocolaires et applicatives. Elles peuvent se combiner.
- Le trafic malveillant peut épuiser la bande passante, les paquets par seconde, les tables de connexions, le CPU, la mémoire ou une dépendance applicative.
- Une panne n'est pas automatiquement un DDoS. Il faut croiser métriques réseau, journaux applicatifs, disponibilité externe et changements récents.
- Les bits/s, paquets/s et requêtes/s mesurent des phénomènes différents.
- Le filtrage par IP seul ne suffit pas toujours et peut bloquer des utilisateurs légitimes.
- Si la liaison Internet est saturée avant le site, la mitigation doit être réalisée en amont, souvent par l'opérateur ou un service anti-DDoS.
- Les CDN, WAF, pare-feu, quotas, caches et modes dégradés ont des rôles complémentaires.
- Toute règle d'urgence doit être ciblée, testée, mesurée et réversible.
- Préparer contacts, sauvegardes, accès hors bande, lignes de base et plans de retour arrière avant l'incident réduit le temps de rétablissement.
- Collectez les preuves, protégez les données sensibles, communiquez factuellement et faites un post-mortem après la résolution.

### Checklist rapide d'intervention

- [ ] Confirmer le service touché et l'impact utilisateur.
- [ ] Noter l'heure, le fuseau et les changements récents.
- [ ] Relever débit, pps, pertes, latence, CPU, mémoire, connexions et taux d'erreur.
- [ ] Vérifier plusieurs sondes et chemins réseau.
- [ ] Identifier le goulot : lien, équipement, application ou dépendance.
- [ ] Contacter l'opérateur si le lien ou le réseau amont est saturé.
- [ ] Choisir une mesure proportionnée et réversible.
- [ ] Mesurer l'effet et surveiller les faux positifs.
- [ ] Communiquer aux parties prenantes selon le plan d'incident.
- [ ] Retirer les mesures temporaires après validation et créer des actions correctives.

### Références techniques

1. **IETF — RFC 4732, Internet Denial-of-Service Considerations** : panorama des menaces DoS et des enjeux de conception résiliente. https://www.rfc-editor.org/rfc/rfc4732.html
2. **CISA — UDP-Based Amplification Attacks** : recommandations défensives, coordination opérateur et réduction de l'abus de services UDP. https://www.cisa.gov/ncas/alerts/ta14-017a
3. **OWASP — Denial of Service Cheat Sheet** : inventaire des ressources, limites applicatives, quotas, timeouts, conception résiliente et mitigation. https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
4. **IETF BCP 38 / RFC 2827 — Network Ingress Filtering** : principes de filtrage pour réduire l'usurpation d'adresses sources. https://www.rfc-editor.org/rfc/rfc2827.html
5. **Cloudflare Learning Center — What is a DDoS attack?** : introduction aux attaques DDoS et aux approches de protection. https://www.cloudflare.com/learning/ddos/what-is-a-ddos-attack/
6. **Cisco — Documentation IOS/IOS XE** : vérifier la référence correspondant au modèle, à la version et aux fonctionnalités réellement prises en charge avant d'appliquer une commande. https://www.cisco.com/c/en/us/support/index.html

Les références sont des points de départ. Les recommandations d'exploitation et les commandes doivent toujours être croisées avec la documentation actuelle de vos équipements, le contrat de votre opérateur et la politique de sécurité de votre organisation.
