# QoS — Niveau Intermédiaire

> **Fichier :** `qos-intermediaire.md`  
> **Parcours :** Réseaux — Intermédiaire  
> **Prérequis :** avoir étudié `qos-debutant.md`, maîtriser les bases de DiffServ, DSCP, classification, marquage, policing, shaping et MQC.  
> **Objectif :** concevoir, déployer, vérifier et dépanner une politique QoS multi-classes, y compris sur les liaisons WAN et les tunnels, en raisonnant à partir des objectifs et des compteurs plutôt que de copier des commandes.


## Objectifs pédagogiques

À la fin de ce cours, tu devrais pouvoir :

- traduire un SLA applicatif en classes, objectifs de performance et règles mesurables ;
- construire un plan de marquage DiffServ cohérent de l’accès au WAN ;
- concevoir des policies MQC à plusieurs classes et comprendre les politiques hiérarchiques ;
- choisir entre LLQ, CBWFQ, shaping, policing, WRED/AQM et ECN selon le problème constaté ;
- expliquer les risques d’une file prioritaire mal dimensionnée, d’un mauvais trust boundary ou d’un remarking inattendu ;
- analyser QoS sur WAN, MPLS et tunnels sans supposer que les marquages traversent le réseau inchangés ;
- vérifier le fonctionnement en combinant configuration, compteurs matériels, captures et mesures applicatives ;
- planifier un changement, un test sous congestion et une procédure de retour arrière.

## Comment utiliser ce niveau

Le cours ne reprend pas toute la définition de la QoS ni chaque valeur DSCP comme si tu découvrais le sujet. Il part du principe que les notions du niveau débutant sont connues. Ici, l’effort porte sur la conception cohérente, les interactions entre mécanismes, les différences de plateforme et l’interprétation des preuves. Les exemples Cisco IOS/IOS XE sont des modèles pédagogiques : la prise en charge des commandes varie selon la famille matérielle, la version logicielle, le type d’interface et le chemin du paquet dans l’ASIC. Toujours confirmer la syntaxe dans le guide de la plateforme ciblée.

## 1. Partir des objectifs métier, pas des commandes

### 1.1 Construire une matrice de besoins

Avant de créer des classes, identifie les applications, les chemins empruntés, le nombre d’utilisateurs simultanés, les périodes de pointe et les symptômes qu’il faut éviter. Une classe appelée `VOICE` n’a aucune valeur si elle ne correspond pas à du trafic réellement reconnu, ou si l’interface congestionnée n’applique pas la politique attendue.

Une matrice de conception comporte au minimum : le type de trafic, la source autorisée, la destination, le DSCP d’entrée, le DSCP attendu dans le domaine, le mécanisme de sortie, le débit estimé, le seuil d’admission ou le profil, les métriques de validation et la personne responsable. Ajoute aussi les règles pour les paquets non reconnus, les flux chiffrés ou les marques invalides.

### Schéma 1 — Cycle de conception QoS

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Cycle de conception QoS"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Cycle de conception QoS</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Du besoin métier à la preuve mesurée</text><rect x="28" y="142" width="144" height="96" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="100.0" y="184.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">1. Mesurer</text><text x="100.0" y="204.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">SLA, files, drops</text><rect x="218" y="142" width="144" height="96" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="290.0" y="184.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">2. Classer</text><text x="290.0" y="204.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Applications / rôles</text><rect x="408" y="142" width="144" height="96" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="480.0" y="184.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">3. Marquer</text><text x="480.0" y="204.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP / CoS</text><rect x="598" y="142" width="144" height="96" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="670.0" y="184.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">4. Protéger</text><text x="670.0" y="204.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">LLQ, CBWFQ, AQM</text><rect x="788" y="142" width="144" height="96" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="860.0" y="184.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">5. Vérifier</text><text x="860.0" y="204.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Compteurs / tests</text><line x1="172" y1="190" x2="216" y2="190" stroke="#93c5fd" stroke-width="3"/><polygon points="216.0,190.0 204.0,183.0 204.0,197.0" fill="#93c5fd"/><line x1="362" y1="190" x2="406" y2="190" stroke="#93c5fd" stroke-width="3"/><polygon points="406.0,190.0 394.0,183.0 394.0,197.0" fill="#93c5fd"/><line x1="552" y1="190" x2="596" y2="190" stroke="#93c5fd" stroke-width="3"/><polygon points="596.0,190.0 584.0,183.0 584.0,197.0" fill="#93c5fd"/><line x1="742" y1="190" x2="786" y2="190" stroke="#93c5fd" stroke-width="3"/><polygon points="786.0,190.0 774.0,183.0 774.0,197.0" fill="#93c5fd"/><text x="480" y="284" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="middle">La politique découle des objectifs mesurés, pas d’une liste de commandes copiées.</text><text x="480" y="313" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Valider aussi le trafic non prioritaire et le comportement en panne.</text></svg>

### 1.2 Définir un SLO exploitable

Un objectif doit être mesurable. « La voix doit être bonne » ne permet pas de décider si le déploiement a réussi. Un SLO utile définit la population mesurée, la période, le sens, le percentile ou l’agrégat, le point de mesure et les limites acceptables. Les exigences exactes dépendent du codec, du terminal, du fournisseur voix et de la conception.

Exemple de formulation : « Durant les heures ouvrées, le 95e percentile du RTT entre le site A et le contrôleur voix reste sous la limite validée, la perte observée reste sous le seuil convenu et aucune classe temps réel ne présente de drops persistants sur le WAN ». Les seuils chiffrés doivent provenir du SLA de l’application ou d’une baseline pertinente, pas être choisis arbitrairement.

### 1.3 Trouver l’endroit réellement congestionné

La QoS prend surtout de la valeur à l’endroit où une ressource est disputée. Dans une liaison WAN contractée à 20 Mbit/s, un routeur avec une interface Ethernet physique à 1 Gbit/s peut ne voir aucune congestion physique, alors que l’opérateur façonne ensuite le trafic à 20 Mbit/s. Un shaping local légèrement inférieur au débit de service peut faire apparaître la file sur l’équipement administré, mais seulement si le débit réel et les surcharges sont compris.

Un diagramme de réseau doit montrer les interfaces et les sens. Les mesures faites sur le mauvais port, dans le mauvais sens ou sur une moyenne trop longue peuvent cacher le problème. Une politique egress (sortante) ne traite pas automatiquement la congestion egress d’un autre équipement ou la congestion du sens retour.

### 1.4 Établir une baseline

Avant changement, collecte au moins : débit par classe ou application si disponible, DSCP observé, utilisation des interfaces, drops, erreurs physiques, occupation des files, latence, gigue, pertes et journaux de l’application. Note les horaires et les scénarios de reproduction. Enregistrer uniquement le débit moyen est insuffisant : des rafales courtes peuvent remplir une file sans apparaître clairement dans des moyennes de cinq minutes.

**Livrable de conception :** une matrice de classes approuvée, un schéma des points de congestion, les SLO retenus, la configuration de référence, les commandes de validation et des critères explicites de retour arrière.

## 2. Construire un domaine DiffServ cohérent

### 2.1 DSCP est une convention, pas une magie de bout en bout

Les valeurs DSCP n’imposent pas d’elles-mêmes le comportement d’un réseau. Un DSCP EF (46), par exemple, n’assure pas que chaque saut accordera une priorité stricte ; il faut que chaque équipement conserve la marque, la mappe à la bonne classe et programme la file correspondante. Une frontière peut accepter le DSCP d’un système géré, le réécrire selon une politique locale ou le remettre à zéro pour du trafic non fiable.

### Schéma 2 — Domaine DiffServ et frontières

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Domaine DiffServ et frontières"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Domaine DiffServ et frontières</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Marquage, contrats de service et remapping</text><rect x="25" y="135" width="155" height="92" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="102.5" y="175.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Accès LAN</text><text x="102.5" y="195.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">marquage initial</text><rect x="225" y="135" width="155" height="92" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="302.5" y="175.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Domaine entreprise</text><text x="302.5" y="195.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">PHB cohérents</text><rect x="425" y="135" width="155" height="92" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="502.5" y="175.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Frontière WAN</text><text x="502.5" y="195.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">policing / remark</text><rect x="625" y="135" width="145" height="92" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="697.5" y="175.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Réseau opérateur</text><text x="697.5" y="195.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">classes contractuelles</text><rect x="815" y="135" width="120" height="92" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="875.0" y="175.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Site distant</text><text x="875.0" y="195.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">remap si besoin</text><line x1="180" y1="180" x2="225" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="225.0,180.0 213.0,173.0 213.0,187.0" fill="#93c5fd"/><line x1="380" y1="180" x2="425" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="425.0,180.0 413.0,173.0 413.0,187.0" fill="#93c5fd"/><line x1="580" y1="180" x2="625" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="625.0,180.0 613.0,173.0 613.0,187.0" fill="#93c5fd"/><line x1="770" y1="180" x2="815" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="815.0,180.0 803.0,173.0 803.0,187.0" fill="#93c5fd"/><text x="480" y="282" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP a une signification locale tant qu’un contrat ou une politique de bout en bout ne la fixe pas.</text><text x="480" y="309" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Documenter ce qui est conservé, réécrit, supprimé ou traduit aux frontières.</text></svg>

Documente les limites de domaine : LAN, WAN privé, fournisseur, Internet, tunnel overlay, interconnexion avec un tiers. À chaque frontière, réponds à quatre questions : quelles marques sont acceptées ? quelles marques sont traduites ? quelles garanties sont contractées ? que se passe-t-il avec le trafic inconnu ou non conforme ? Sans accord entre domaines, la marque locale doit être traitée comme un indice, pas comme une garantie universelle.

### 2.2 Normaliser sans écraser des classes utiles

Un réseau peut recevoir des marques hétérogènes venant d’équipements variés. La normalisation consiste à traduire ces entrées vers un modèle local contrôlé. Cela peut être fait par identité de terminal, interface, rôle, ACL, application ou combinaison d’attributs. Évite de multiplier les classes sans besoin : une politique impossible à auditer finira par contenir des exceptions contradictoires.

Le plan de mappage peut distinguer : temps réel strictement contrôlé, signalisation, vidéo interactive, transactions métier, trafic de données général, sauvegarde/scavenger et contrôle du réseau. Ces noms sont organisationnels ; les DSCP correspondants et les mécanismes associés doivent être écrits dans une matrice officielle. N’attribue pas automatiquement EF à tout paquet UDP ou AF41 à toute vidéo détectée par port.

### 2.3 Frontière de confiance et usurpation de DSCP

Un poste utilisateur peut définir des valeurs DSCP arbitraires. Si le réseau accorde un traitement privilégié sur cette seule valeur, l’utilisateur peut saturer une file prioritaire. Le trust boundary doit reposer sur une règle explicite : par exemple, faire confiance au marquage d’un téléphone correctement identifié sur un port configuré à cet effet, tandis que les PC, ports invités ou segments non maîtrisés sont reclassés.

La politique doit préserver les cas légitimes : un PC derrière un téléphone, un poste avec softphone, le trafic de contrôle d’un équipement ou le trafic d’une borne Wi-Fi. Le comportement varie selon la plateforme et le design. Teste les paquets réels et le marquage à chaque frontière plutôt que de supposer que `mls qos trust dscp`, `auto qos` ou une commande apparentée a le même effet sur toutes les générations d’équipements.

### 2.4 DSCP, PCP, classe interne et champ TC MPLS

Il faut distinguer au moins quatre espaces possibles : DSCP dans l’en-tête IP (6 bits), PCP/CoS dans l’étiquette VLAN 802.1Q (3 bits), champs internes de QoS du matériel, et Traffic Class (TC, historiquement EXP) dans l’en-tête MPLS (3 bits). Un équipement peut configurer des tables de conversion entre ces espaces, mais aucune correspondance universelle ne doit être supposée. Le tunnel ajoute une autre question : la QoS inspecte-t-elle le paquet interne, l’en-tête externe, ou une valeur copiée entre les deux ?

### 2.5 Une matrice indicative à faire approuver

| Classe locale | Exemple de marquage possible | Traitement de sortie possible | Vérification essentielle |
|---|---|---|---|
| Voix interactive autorisée | EF 46 | LLQ plafonnée, admission maîtrisée | Drops LLQ, gigue, perte voix |
| Signalisation critique | CS3/CS5 selon le système | Garantie adaptée, pas forcément LLQ | Établissement des appels / sessions |
| Vidéo interactive | AF4x ou classe locale documentée | Garantie ou partage pondéré | RTT, perte, débit simultané |
| Transactions métier | AF2x/AF3x selon le contrat | CBWFQ / partage des ressources | Temps de transaction en pointe |
| Données générales | DF 0 ou classe locale | Best effort / bande passante restante | Absence de famine |
| Sauvegarde massive | DF ou CS1 si convention validée | Shaping/policing ou ressources restantes | Impact sur les autres classes |
| Contrôle réseau | Classes réservées selon le design | Protection sans surcharge inutile | Stabilité des protocoles et CPU |

Cette matrice n’est pas un modèle universel. Un service peut avoir des classes différentes et un réseau opérateur peut mapper les DSCP vers ses propres classes. La conception finale doit être explicite et testée.

## 3. MQC avancé : de la classe à l’interface

### 3.1 Séparer `class-map`, `policy-map` et `service-policy`

La Modular QoS CLI (MQC) sépare trois décisions : le `class-map` décrit le trafic reconnu ; le `policy-map` définit les actions ; `service-policy` applique la policy sur une interface et dans une direction. Cette séparation facilite la réutilisation mais ne garantit pas que chaque combinaison de match et d’action est supportée par l’équipement.

### Schéma 3 — MQC et politique hiérarchique

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="MQC et politique hiérarchique"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">MQC et politique hiérarchique</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Classification, actions et point d’application</text><rect x="35" y="110" width="250" height="74" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="160.0" y="141.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">CLASS-MAP</text><text x="160.0" y="161.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">match dscp / ACL / protocoles</text><rect x="355" y="110" width="250" height="74" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="480.0" y="141.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">POLICY-MAP</text><text x="480.0" y="161.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">actions pour chaque classe</text><rect x="675" y="110" width="250" height="74" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="800.0" y="141.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">SERVICE-POLICY</text><text x="800.0" y="161.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">interface et direction</text><line x1="285" y1="147" x2="355" y2="147" stroke="#93c5fd" stroke-width="3"/><polygon points="355.0,147.0 343.0,140.0 343.0,154.0" fill="#93c5fd"/><line x1="605" y1="147" x2="675" y2="147" stroke="#93c5fd" stroke-width="3"/><polygon points="675.0,147.0 663.0,140.0 663.0,154.0" fill="#93c5fd"/><rect x="130" y="245" width="280" height="72" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="270.0" y="275.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Policy parent</text><text x="270.0" y="295.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">shape / plafond agrégé</text><rect x="550" y="245" width="280" height="72" rx="10" fill="#5b21b6" stroke="#c084fc" stroke-width="2"/><text x="690.0" y="275.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Policy enfant</text><text x="690.0" y="295.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">queues et classes métier</text><line x1="410" y1="280" x2="550" y2="280" stroke="#c084fc" stroke-width="3"/><polygon points="550.0,280.0 538.0,273.0 538.0,287.0" fill="#c084fc"/><text x="480.0" y="265" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">service-policy</text><text x="480" y="355" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">L’imbrication HQoS exacte dépend des fonctions supportées par le matériel et IOS XE.</text></svg>

Les class-maps avec `match-any` reconnaissent un paquet si au moins un critère correspond, tandis que `match-all` exige la conjonction des critères selon la sémantique du système. L’ordre d’évaluation et le traitement des classes peuvent différer selon le type de policy. Les classes peuvent se chevaucher : il faut savoir quelle classe gagne dans le contexte donné et vérifier les compteurs. Ne construis pas une classe « VOICE » avec `match udp` sans limiter davantage : elle risque d’attraper une grande partie du trafic UDP.

### 3.2 Exemple de classification basée sur DSCP

Exemple conceptuel IOS/IOS XE, à valider sur la plateforme cible :

```text
class-map match-any CM-VOICE
 match dscp ef
!
class-map match-any CM-BUSINESS
 match dscp af21 af22 af23
!
class-map match-any CM-BULK
 match dscp cs1
!
```

Cette configuration part du principe que le marquage entrant a été validé par la frontière de confiance. Si les marques ne sont pas fiables, il faut une politique d’entrée qui classe et/ou réécrit avant de baser la sortie uniquement sur les DSCP. Le comportement de `match dscp` avec plusieurs valeurs et la syntaxe exacte peuvent varier : teste la configuration dans l’environnement cible.

### 3.3 Concevoir une policy de sortie

Exemple pédagogique d’une interface WAN de routeur IOS XE. Les valeurs de bande passante doivent être calculées selon la capacité réellement façonnée et le trafic mesuré :

```text
policy-map WAN-CHILD
 class CM-VOICE
  priority percent 10
 class CM-BUSINESS
  bandwidth percent 25
 class CM-BULK
  bandwidth percent 5
 class class-default
  fair-queue
!
interface GigabitEthernet0/0/0
 service-policy output WAN-CHILD
```

Ce bloc illustre le sens du design, pas une recette universelle. `priority percent`, `bandwidth percent`, `fair-queue` et leur compatibilité dépendent de la plateforme et du contexte. La limite de priorité ne signifie pas que la voix peut utiliser arbitrairement le réseau : il faut estimer le nombre d’appels, le codec, l’overhead IP/UDP/RTP, les rafales et prévoir un contrôle d’admission. Si la classe prioritaire dépasse sa part permise, le résultat sera celui du policer ou du comportement de la plateforme.

### 3.4 Ne pas confondre bande passante garantie et réservation absolue

Une action `bandwidth` dans une policy de scheduling exprime généralement un minimum ou une pondération lorsque l’interface est congestionnée ; elle ne réserve pas toujours la capacité au repos comme un tunnel RSVP-TE. La sémantique dépend de l’algorithme et du système. Les pourcentages de classes doivent être cohérents, mais la manière de traiter la capacité non consommée varie. Mesure le comportement sous congestion plutôt que de lire seulement la configuration.

### 3.5 Vérifier les match et les compteurs

Après application, vérifier la policy dans la bonne direction et sur la bonne interface. Une classe à zéro paquet peut signaler un mauvais DSCP attendu, un trafic absent, un sens erroné, un class-map trop restrictif ou un compteur non exposé par le matériel. Un compteur qui augmente prouve que le paquet a été classé à cet endroit, mais ne démontre pas à lui seul que l’application obtient la performance souhaitée.

Commandes souvent rencontrées sur IOS/IOS XE, à confirmer :

```text
show class-map
show policy-map
show policy-map interface GigabitEthernet0/0/0 output
show interfaces GigabitEthernet0/0/0
show running-config interface GigabitEthernet0/0/0
```

Certaines versions n’acceptent pas le mot-clé `output` dans la commande d’inspection ou disposent de commandes supplémentaires pour le chemin matériel/QFP. Utilise l’aide CLI et le guide de configuration correspondant au modèle exact.

## 4. LLQ et CBWFQ : faire des arbitrages mesurés

### 4.1 LLQ : priorité stricte avec garde-fous

La Low Latency Queueing associe, dans de nombreuses implémentations Cisco, un traitement prioritaire strict à une limite ou un mécanisme de contrôle. L’objectif est de réduire l’attente de paquets sensibles au délai en période de congestion. Le piège principal est de déclarer trop de trafic « prioritaire » : chaque classe ajoutée augmente la charge de ce compartiment privilégié et peut affecter les autres classes.

### Schéma 4 — LLQ et CBWFQ

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="LLQ et CBWFQ"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">LLQ et CBWFQ</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Priorité limitée et garanties des autres classes</text><rect x="25" y="143" width="150" height="80" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="100.0" y="177.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Paquets entrants</text><text x="100.0" y="197.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">classes QoS</text><line x1="175" y1="183" x2="235" y2="183" stroke="#93c5fd" stroke-width="3"/><polygon points="235.0,183.0 223.0,176.0 223.0,190.0" fill="#93c5fd"/><rect x="240" y="93" width="330" height="58" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="405.0" y="116.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">LLQ / priorité</text><text x="405.0" y="135.92000000000002" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Trafic temps réel plafonné</text><rect x="240" y="170" width="330" height="58" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="405.0" y="193.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">CBWFQ / garantie</text><text x="405.0" y="212.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Part de bande passante</text><rect x="240" y="247" width="330" height="58" rx="10" fill="#334155" stroke="#94a3b8" stroke-width="2"/><text x="405.0" y="270.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Best effort</text><text x="405.0" y="289.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Reste des ressources</text><line x1="570" y1="183" x2="665" y2="183" stroke="#93c5fd" stroke-width="3"/><polygon points="665.0,183.0 653.0,176.0 653.0,190.0" fill="#93c5fd"/><rect x="670" y="142" width="260" height="82" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="800.0" y="177.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Scheduler de sortie</text><text x="800.0" y="197.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">arbitre en cas de congestion</text><text x="480" y="348" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Une file prioritaire excessive peut retarder voire affamer les autres classes.</text></svg>

Dimensionne la voix à partir du débit de paquet réel, pas seulement du débit audio brut. Chaque paquet transporte des en-têtes Ethernet, IP, UDP, RTP, parfois une encapsulation de tunnel, et peut être envoyé avec des intervalles fixes. Les petits paquets ont une surcharge relative importante. Prends en compte les appels simultanés dans chaque sens, les codecs, le silence supprimé le cas échéant, l’overhead et le scénario de pic.

### 4.2 CBWFQ et trafic de données

CBWFQ répartit les ressources entre classes définies lorsque plusieurs classes sont en concurrence. L’objectif est d’assurer une part cohérente au trafic métier sans lui donner nécessairement une priorité stricte. Une classe de transaction peut nécessiter une garantie raisonnable et faible latence ; un transfert de sauvegarde peut consommer la capacité restante ou recevoir une limite.

Si toutes les classes sont actives, les parts annoncées doivent être interprétées dans la capacité réellement disponible après shaping et autres frais. Une classe à faible pourcentage peut malgré tout utiliser davantage de capacité lorsque les autres classes sont inactives, selon la politique et la plateforme. Précise si tu veux une garantie minimale, un plafond maximal ou les deux : ce sont des intentions différentes.

### 4.3 Identifier les symptômes d’une LLQ surchargée

Signaux typiques : hausse de drops sur la classe prioritaire, variation de gigue, débit voix plus important que prévu, DSCP EF visible sur des flux de données, ou file LLQ utilisée par des applications non autorisées. Vérifie d’abord les match réels et la frontière de confiance, puis la demande de trafic et la limite configurée. Augmenter le plafond sans diagnostiquer peut seulement déplacer la congestion vers les autres classes.

### 4.4 Estimer le budget voix

Une estimation simple doit être explicite. Si un flux produit `N` paquets par seconde et que chaque paquet consomme `L` octets sur le lien après encapsulation, alors le débit approximatif par sens vaut `N × L × 8` bits/s. Multiplie par les appels simultanés et ajoute une marge justifiée par la variabilité. Ne mélanger pas le débit payload et le débit au niveau du lien. Le calcul exact dépend du codec, de la périodicité RTP, de l’encapsulation, de la compression d’en-têtes éventuelle et de la méthode de mesure.

### 4.5 Exemple de calcul

Supposons, à titre pédagogique, 50 appels simultanés, chaque appel consommant environ 100 kbit/s par sens sur le réseau après prise en compte de l’overhead :

- voix estimée par sens : `50 × 100 kbit/s = 5 000 kbit/s`, soit 5 Mbit/s ;
- sur un service 20 Mbit/s, cela représente 25 % du débit nominal ;
- une LLQ à 10 % serait insuffisante pour cette hypothèse si la plateforme limite la classe à environ 2 Mbit/s ;
- une LLQ à 30 % pourrait être une hypothèse à tester, mais ne doit pas être configurée sans vérifier le contrat, la marge, l’admission et les autres flux prioritaires.

Ces nombres sont illustratifs, pas des recommandations. Le débit réel d’un appel dépend fortement du codec, du packetization interval et de l’encapsulation. Le bon dimensionnement part de mesures réelles et de la capacité contractuelle du chemin.

## 5. HQoS : façonner le service puis ordonnancer ses classes

### 5.1 Pourquoi une hiérarchie est utile

Une interface Ethernet de routeur peut fonctionner à 1 Gbit/s alors que le service opérateur est limité à 20 Mbit/s. Si la congestion se produit plus loin dans le réseau, les paquets peuvent être éliminés avant que la policy de sortie locale ne les traite comme prévu. Un parent shaping proche du débit contractuel peut limiter l’envoi vers le service et faire apparaître la file de congestion au niveau du routeur contrôlé ; une policy enfant organise ensuite les classes dans ce débit façonné.

### Schéma 5 — HQoS parent/enfant

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="HQoS parent/enfant"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">HQoS parent/enfant</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Le plafond de service et l’ordonnancement classe par classe</text><rect x="28" y="138" width="165" height="90" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="110.5" y="177.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Interface WAN</text><text x="110.5" y="197.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">100 Mb/s physique</text><line x1="193" y1="183" x2="255" y2="183" stroke="#93c5fd" stroke-width="3"/><polygon points="255.0,183.0 243.0,176.0 243.0,190.0" fill="#93c5fd"/><rect x="260" y="105" width="290" height="66" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="405.0" y="132.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Parent : shape 20 Mb/s</text><text x="405.0" y="152.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">plafond du service opérateur</text><line x1="405" y1="171" x2="405" y2="209" stroke="#93c5fd" stroke-width="3"/><polygon points="405.0,209.0 412.0,197.0 398.0,197.0" fill="#93c5fd"/><rect x="260" y="213" width="290" height="72" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="405.0" y="243.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Enfant : classes / files</text><text x="405.0" y="263.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">LLQ, garanties, drops</text><line x1="550" y1="249" x2="625" y2="249" stroke="#93c5fd" stroke-width="3"/><polygon points="625.0,249.0 613.0,242.0 613.0,256.0" fill="#93c5fd"/><rect x="630" y="210" width="300" height="78" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="780.0" y="243.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Scheduler physique</text><text x="780.0" y="263.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">priorise dans le débit façonné</text><text x="480" y="338" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Exemple conceptuel : la syntaxe et les niveaux HQoS varient selon la plateforme.</text></svg>

### 5.2 Modèle conceptuel

- **Policy parent :** plafonner le débit agrégé du service avec `shape average` ou l’action correspondante si la plateforme la prend en charge.
- **Policy enfant :** séparer voix, signalisation, données métier, trafic général et bulk ; configurer LLQ, garanties, file d’attente et éventuellement AQM selon les fonctions disponibles.
- **Interface :** appliquer la policy parent au point de sortie prévu, vérifier la compatibilité des policies imbriquées et mesurer le résultat.

La hiérarchie disponible n’est pas la même sur tous les routeurs et commutateurs. Certains équipements n’acceptent que deux niveaux, certains imposent des restrictions selon le sens, et certaines actions ne se combinent pas. Ne déduis pas le support de HQoS de la seule présence de `policy-map` dans la CLI : vérifie la documentation officielle du modèle.

### 5.3 Choisir le débit de shaping

La valeur du parent doit être dérivée du débit réellement utilisable, pas simplement du débit physique. L’encapsulation, le transport Ethernet opérateur, les VLAN, les tunnels et la manière dont le fournisseur mesure le débit peuvent influer. Une valeur légèrement inférieure au débit de service est parfois utile pour conserver la congestion au point de contrôle local, mais la marge à retenir dépend de la définition du service et des mesures. Un shaping trop bas réduit inutilement le débit ; un shaping trop haut ne protège pas efficacement contre la file de l’opérateur.

### 5.4 Queue-limit et buffers

La taille des buffers influence la capacité à absorber des rafales et le délai ajouté. Un tampon plus grand peut réduire certains drops courts mais augmente potentiellement la latence sous charge ; un tampon trop petit peut entraîner des pertes répétées. Les paramètres et les modèles de buffers varient largement entre plates-formes, ASIC et versions. Évite de copier des valeurs absolues d’un autre équipement sans examiner le débit, la taille des paquets, le délai acceptable et les mécanismes AQM disponibles.

### 5.5 Shaping n’est pas toujours disponible partout

Les policies sur sous-interfaces, port-channels, circuits Ethernet virtuels, tunnels et interfaces physiques peuvent avoir des restrictions différentes. Sur certains équipements, une policy d’entrée a d’autres capacités que la policy de sortie. Avant l’exploitation, teste la commande sur le même type d’interface que la production et vérifie que la policy se programme matériellement au lieu de supposer que son apparition dans le running-config suffit.

## 6. Policing, shaping, rafales et modèles de jetons

### 6.1 Comprendre CIR, Bc et Be

Un policer fondé sur un seau à jetons mesure la conformité par rapport à un profil. Le CIR est le débit engagé ou configuré, Bc est un paramètre de rafale engagée et Be peut représenter une rafale supplémentaire dans les modèles qui l’emploient. L’interprétation et les options exactes dépendent de l’algorithme et de la plateforme. Les valeurs de burst ne se choisissent pas au hasard : elles doivent permettre le trafic réel attendu sans contourner le profil voulu.

### Schéma 6 — Policing et seau à jetons

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Policing et seau à jetons"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Policing et seau à jetons</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">CIR, rafales et actions de conformité</text><rect x="28" y="123" width="185" height="92" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="120.5" y="163.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Trafic entrant</text><text x="120.5" y="183.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">débit variable</text><line x1="213" y1="170" x2="275" y2="170" stroke="#93c5fd" stroke-width="3"/><polygon points="275.0,170.0 263.0,163.0 263.0,177.0" fill="#93c5fd"/><rect x="280" y="85" width="260" height="100" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="410.0" y="119.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Seau à jetons</text><text x="410.0" y="139.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">CIR / Bc / Be</text><text x="410.0" y="159.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">conformité mesurée</text><line x1="540" y1="128" x2="620" y2="128" stroke="#4ade80" stroke-width="3"/><polygon points="620.0,128.0 608.0,121.0 608.0,135.0" fill="#4ade80"/><text x="580.0" y="114" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">conforme</text><line x1="540" y1="170" x2="620" y2="235" stroke="#f87171" stroke-width="3"/><polygon points="620.0,235.0 615.1,222.0 606.3,232.9" fill="#f87171"/><text x="580.0" y="205" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">excès</text><rect x="625" y="88" width="300" height="75" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="775.0" y="120.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Conforme</text><text x="775.0" y="140.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">transmettre / compter</text><rect x="625" y="210" width="300" height="75" rx="10" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="775.0" y="242.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Non conforme</text><text x="775.0" y="262.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">drop ou remark</text><text x="480" y="333" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Le policer décide immédiatement ; le shaper met en attente si son tampon dispose de place.</text></svg>

Une rafale courte peut dépasser le débit moyen sans être forcément non conforme si le seau contient assez de jetons. Un flux durablement supérieur au CIR épuise ces jetons et déclenche les actions définies. Le policer peut transmettre les paquets conformes et supprimer ou remarquer ceux qui dépassent. Les résultats doivent être vérifiés avec les compteurs de conformité et d’excès lorsque le système les expose.

### 6.2 Choisir l’action sur les paquets excédentaires

Trois intentions courantes ne sont pas équivalentes : supprimer le trafic qui dépasse le contrat ; re-marquer le trafic excédentaire pour le faire passer dans une classe moins favorisée ; ou le transmettre avec un autre traitement selon la politique contractuelle. Le choix dépend du type de service, de la tolérance de perte et de ce que le fournisseur accepte. Si un policer re-marque vers une classe non reconnue plus loin, cette stratégie peut ne pas fonctionner comme prévu.

### 6.3 Policer en entrée ou en sortie

Un policer d’entrée limite le trafic au moment où il arrive sur l’interface ou le point de policy. Il peut être utile pour contrôler l’usage d’un accès utilisateur ou protéger un domaine. Un policer de sortie limite les paquets avant leur émission depuis le point concerné, avec la sémantique matérielle qui lui est propre. Le point d’application est essentiel : un policer ne peut pas restaurer des paquets déjà perdus dans un équipement en amont.

### 6.4 Comparer policer et shaper sous rafales

Le policer décide si le trafic respecte le profil et agit rapidement ; le shaper retient les paquets en tampon pour lisser le débit. Le premier peut engendrer une perte brusque ; le second introduit de l’attente et peut perdre des paquets si le tampon est plein. Aucun mécanisme n’est « meilleur » dans l’absolu : ils répondent à des objectifs différents. Pour un accès WAN contracté, le shaping est souvent étudié en sortie ; pour appliquer un profil strict à un abonné, un policer peut être requis par la politique.

## 7. AQM, WRED, ECN et bufferbloat

### 7.1 Pourquoi la taille de file compte

Une longue file réduit parfois la perte lors d’une rafale mais peut ajouter des dizaines ou centaines de millisecondes d’attente. La latence ressentie par l’application peut alors augmenter fortement même lorsque le lien n’est pas entièrement saturé sur la moyenne. Ce problème est souvent décrit comme *bufferbloat*. Mesurer un RTT sous charge et examiner les drops/occupations de files aide à le distinguer d’une latence de propagation.

### Schéma 7 — Tail drop et AQM

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Tail drop et AQM"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Tail drop et AQM</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Courbes conceptuelles de profondeur de file</text><text x="480" y="90" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">File d’attente en fonction du temps (illustration conceptuelle)</text><line x1="90" y1="300" x2="900" y2="300" stroke="#94a3b8" stroke-width="2"/><line x1="90" y1="130" x2="90" y2="300" stroke="#94a3b8" stroke-width="2"/><text x="56" y="208" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Profondeur</text><text x="90" y="323" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="start">temps →</text><line x1="100" y1="280" x2="230" y2="255" stroke="#60a5fa" stroke-width="4"/><line x1="230" y1="255" x2="360" y2="210" stroke="#60a5fa" stroke-width="4"/><line x1="360" y1="210" x2="495" y2="165" stroke="#60a5fa" stroke-width="4"/><line x1="495" y1="165" x2="620" y2="145" stroke="#60a5fa" stroke-width="4"/><line x1="620" y1="145" x2="760" y2="125" stroke="#60a5fa" stroke-width="4"/><line x1="760" y1="125" x2="885" y2="115" stroke="#60a5fa" stroke-width="4"/><line x1="100" y1="280" x2="230" y2="255" stroke="#4ade80" stroke-width="4"/><line x1="230" y1="255" x2="360" y2="220" stroke="#4ade80" stroke-width="4"/><line x1="360" y1="220" x2="495" y2="202" stroke="#4ade80" stroke-width="4"/><line x1="495" y1="202" x2="620" y2="208" stroke="#4ade80" stroke-width="4"/><line x1="620" y1="208" x2="760" y2="190" stroke="#4ade80" stroke-width="4"/><line x1="760" y1="190" x2="885" y2="201" stroke="#4ade80" stroke-width="4"/><text x="745" y="111" fill="#93c5fd" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">Tail drop : croissance jusqu’au plafond</text><text x="735" y="230" fill="#86efac" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">AQM : contrôle plus précoce de la file</text><text x="480" y="360" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Courbes schématiques, pas des mesures ni des seuils à recopier.</text></svg>

### 7.2 Tail drop

Avec tail drop, les paquets entrent dans la file jusqu’à saturation ; les paquets supplémentaires sont supprimés. En présence de flux TCP synchronisés, plusieurs sessions peuvent réduire simultanément leur débit puis le réaugmenter, ce qui crée des oscillations. Tail drop reste simple et peut être approprié dans des contextes précis, mais il n’est pas une solution complète de congestion.

### 7.3 WRED et seuils

WRED (*Weighted Random Early Detection*) applique des règles de rejet probabilistes avant que la file ne soit entièrement saturée, potentiellement en différenciant des classes ou des valeurs selon l’implémentation. Son comportement dépend du calcul de la profondeur moyenne, des seuils, de la probabilité et de la classification. Les seuils doivent être testés et ne doivent pas être copiés d’une documentation d’un autre matériel ou d’une version sans validation.

### 7.4 ECN

ECN permet à certains chemins de signaler une congestion dans les en-têtes IP, lorsque les extrémités et les équipements le prennent en charge. Dans les mécanismes compatibles, un paquet ECN-capable peut être marqué congestion-experienced au lieu d’être supprimé, et l’extrémité peut adapter son débit. ECN n’est pas une simple étiquette QoS et ne fonctionne pas automatiquement de bout en bout : il faut vérifier transport, terminaux, réseau et comportement effectif.

### Schéma 8 — WRED et ECN

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="WRED et ECN"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">WRED et ECN</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Signalement et suppression selon la configuration</text><rect x="32" y="130" width="175" height="100" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="119.5" y="174.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Congestion modérée</text><text x="119.5" y="194.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">queue qui monte</text><line x1="207" y1="180" x2="270" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="270.0,180.0 258.0,173.0 258.0,187.0" fill="#93c5fd"/><rect x="275" y="105" width="190" height="150" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="370.0" y="164.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">AQM / WRED</text><text x="370.0" y="184.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">selon seuils</text><text x="370.0" y="204.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">classe et DSCP</text><line x1="465" y1="150" x2="545" y2="120" stroke="#4ade80" stroke-width="3"/><polygon points="545.0,120.0 531.3,117.7 536.2,130.8" fill="#4ade80"/><text x="505.0" y="110" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">ECN-capable</text><line x1="465" y1="207" x2="545" y2="250" stroke="#f87171" stroke-width="3"/><polygon points="545.0,250.0 537.7,238.2 531.1,250.5" fill="#f87171"/><text x="505.0" y="240" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">drop / mark</text><rect x="550" y="82" width="365" height="77" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="732.5" y="115.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">ECN négocié / supporté</text><text x="732.5" y="135.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">marque de congestion si applicable</text><rect x="550" y="220" width="365" height="77" rx="10" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="732.5" y="253.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Suppression sélective</text><text x="732.5" y="273.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">ou traitement de congestion</text><text x="480" y="341" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">WRED/ECN exigent un chemin compatible ; l’activation seule ne garantit pas le résultat.</text></svg>

### 7.5 AQM moderne et matériel

Des implémentations plus récentes peuvent prendre en charge des mécanismes de gestion de files adaptés au matériel, mais leur présence, leur activation et leurs interactions avec les classes sont spécifiques. Le bon processus consiste à : identifier le goulot d’étranglement, mesurer la latence et les drops sous charge, lire les fonctions supportées, commencer par un profil limité, faire un test reproductible, comparer avant/après, puis élargir si les objectifs sont atteints.

## 8. DSCP, tunnels, MPLS et domaines opérateur

### 8.1 Le cas des tunnels

Dans un tunnel, le paquet original possède son en-tête interne, et l’encapsulation ajoute un en-tête externe. La politique sous-jacente peut classer le paquet externe, tandis que l’application est identifiée dans le paquet interne. Selon la technologie et la configuration, la marque interne peut être copiée dans l’en-tête externe, conservée séparément, ou perdue à une frontière. Les fonctions de pré-classification comme `qos pre-classify` existent dans certains contextes Cisco, mais la syntaxe et les cas d’utilisation varient selon le type de tunnel et la plateforme.

### Schéma 10 — QoS et tunnels

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="QoS et tunnels"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">QoS et tunnels</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">En-tête interne et en-tête externe</text><rect x="30" y="142" width="160" height="92" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="110.0" y="182.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Paquet IP</text><text x="110.0" y="202.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP interne</text><line x1="190" y1="188" x2="250" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="250.0,188.0 238.0,181.0 238.0,195.0" fill="#93c5fd"/><rect x="255" y="115" width="205" height="145" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="357.5" y="172.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Encapsulation tunnel</text><text x="357.5" y="192.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">en-tête externe</text><text x="357.5" y="212.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP extérieur</text><line x1="460" y1="188" x2="520" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="520.0,188.0 508.0,181.0 508.0,195.0" fill="#93c5fd"/><rect x="525" y="142" width="170" height="92" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="610.0" y="182.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Réseau underlay</text><text x="610.0" y="202.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">QoS externe</text><line x1="695" y1="188" x2="755" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="755.0,188.0 743.0,181.0 743.0,195.0" fill="#93c5fd"/><rect x="760" y="142" width="170" height="92" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="845.0" y="182.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Décapsulation</text><text x="845.0" y="202.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">interne exposé</text><text x="480" y="305" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Le traitement du paquet interne à l’entrée du tunnel dépend des fonctionnalités disponibles.</text><text x="480" y="333" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Vérifier pre-classify, copy/propagate DSCP et le comportement réel du tunnel.</text></svg>

Sur GRE/IPsec, DMVPN, certains VPN ou des overlay SD-WAN, teste au minimum : classification avant et après encapsulation, DSCP externe envoyé, traitement par les routeurs underlay, comportement à la décapsulation, direction de policy et compteurs sous trafic chiffré. Le chiffrement masque certains champs et empêche l’analyse applicative traditionnelle, mais les en-têtes externes visibles peuvent toujours permettre une QoS underlay selon les règles appliquées.

### 8.2 QoS sur MPLS

Dans un réseau MPLS, le champ TC (Traffic Class, appelé historiquement EXP dans certaines documentations) compte trois bits. Un réseau peut mapper DSCP vers TC à l’imposition du label, préserver ou modifier TC pendant le transport et appliquer une politique au retrait du label. Les comportements uniform, pipe et short-pipe sont des modèles de propagation des informations QoS IP/MPLS, avec une prise en charge et une configuration qui dépendent du réseau et du fournisseur.

### Schéma 9 — QoS IP vers MPLS

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="QoS IP vers MPLS"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">QoS IP vers MPLS</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">DSCP, TC MPLS et frontières de mappage</text><rect x="30" y="135" width="160" height="90" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="110.0" y="174.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">IP entrant</text><text x="110.0" y="194.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP EF / AF</text><line x1="190" y1="180" x2="250" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="250.0,180.0 238.0,173.0 238.0,187.0" fill="#93c5fd"/><rect x="255" y="135" width="200" height="90" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="355.0" y="174.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Entrée MPLS</text><text x="355.0" y="194.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">mapping DSCP → TC</text><line x1="455" y1="180" x2="515" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="515.0,180.0 503.0,173.0 503.0,187.0" fill="#93c5fd"/><rect x="520" y="135" width="160" height="90" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="600.0" y="174.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Label MPLS</text><text x="600.0" y="194.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">TC / EXP 3 bits</text><line x1="680" y1="180" x2="740" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="740.0,180.0 728.0,173.0 728.0,187.0" fill="#93c5fd"/><rect x="745" y="135" width="185" height="90" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="837.5" y="174.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Sortie / frontière</text><text x="837.5" y="194.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">mapping explicite</text><text x="480" y="278" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Ne pas supposer que DSCP et TC MPLS sont automatiquement préservés ou équivalents.</text><text x="480" y="307" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Vérifier les règles de classification, imposition, swap, egress et les contrats opérateur.</text></svg>

Ne présume pas que DSCP 46 donne toujours TC 5 ni que le réseau opérateur mappe la classe de façon constante. Exige un tableau de mappage, teste les classes aux frontières et mesure la perte et la latence sous charge. Si la liaison est un service opérateur, il faut connaître le profil acheté et la méthode de mesure contractuelle.

### 8.3 Congestion et shaping côté client

Un WAN peut être physiquement rapide entre le routeur et le modem tout en étant commercialement limité à un débit plus faible. Si le client émet au-delà du débit contractuel, la congestion peut se produire au niveau du policer du fournisseur, qui ne maîtrise pas la classification interne souhaitée par l’entreprise. Un shaping contrôlé en sortie peut déplacer le point de file au CPE. Il faut cependant laisser une marge adaptée à l’overhead et valider le comportement bidirectionnel.

### Schéma 11 — QoS WAN et débit opérateur

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="QoS WAN et débit opérateur"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">QoS WAN et débit opérateur</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Shaping sur le débit réel de service</text><rect x="30" y="138" width="170" height="95" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="115.0" y="180.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">LAN / accès</text><text x="115.0" y="200.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">classes de trafic</text><line x1="200" y1="185" x2="255" y2="185" stroke="#93c5fd" stroke-width="3"/><polygon points="255.0,185.0 243.0,178.0 243.0,192.0" fill="#93c5fd"/><rect x="260" y="122" width="205" height="125" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="362.5" y="179.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Routeur d’agence</text><text x="362.5" y="199.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">HQoS / shaping</text><line x1="465" y1="185" x2="520" y2="185" stroke="#93c5fd" stroke-width="3"/><polygon points="520.0,185.0 508.0,178.0 508.0,192.0" fill="#93c5fd"/><rect x="525" y="138" width="170" height="95" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="610.0" y="180.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Accès opérateur</text><text x="610.0" y="200.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">CIR / contrat</text><line x1="695" y1="185" x2="750" y2="185" stroke="#93c5fd" stroke-width="3"/><polygon points="750.0,185.0 738.0,178.0 738.0,192.0" fill="#93c5fd"/><rect x="755" y="138" width="175" height="95" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="842.5" y="180.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Siège / cloud</text><text x="842.5" y="200.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">mesures bout en bout</text><text x="480" y="292" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Le débit façonné doit tenir compte du débit réel du service, de l’encapsulation et des rafales.</text><text x="480" y="321" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Mesurer dans les deux sens : le chemin retour peut suivre une autre politique.</text></svg>

### 8.4 Asymétrie des chemins

Le trafic aller et retour peut traverser des équipements différents, des liens avec un autre débit ou un autre profil QoS. Un test unidirectionnel ne prouve pas la performance dans le sens retour. Pour une application interactive, mesure les deux directions lorsque la méthode le permet et vérifie les politiques des deux interfaces. Les connexions TCP sont particulièrement sensibles à un retour affecté par la perte d’ACK ou un chemin congestionné.

## 9. QoS pour IPv6 et environnements mixtes

IPv6 utilise le champ Traffic Class pour les informations DSCP/ECN, selon les principes de DiffServ. Le modèle de politique peut être similaire à celui d’IPv4, mais les critères de classification, ACL et commandes varient selon l’OS et la plateforme. Vérifie que les policies couvrent aussi IPv6 et que les marques ne sont pas ignorées par des chemins différents.

Dans les environnements double pile, il est possible qu’IPv4 et IPv6 empruntent des routes différentes ou reçoivent un traitement différent. Un test IPv4 réussi ne prouve pas que la politique IPv6 fonctionne. Il faut valider la classe réelle, les compteurs et les résultats applicatifs pour les deux protocoles. Sur certains équipements, la configuration d’une seule policy peut couvrir les deux familles ; ailleurs, des détails de classification ou des restrictions diffèrent.

## 10. Analyse et dépannage à partir des preuves

### 10.1 Une méthode de diagnostic reproductible

Quand une application est dégradée, évite de commencer par changer les pourcentages de la policy. Commence par localiser le moment, le sens, la source et la destination ; reproduis le problème ; mesure la latence sous charge ; puis suit les preuves dans l’ordre du chemin : classification, marquage, politique de sortie, file, lien, opérateur et application distante.

### Schéma 12 — Vérification de bout en bout

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Vérification de bout en bout"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Vérification de bout en bout</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">De la classe configurée au résultat applicatif</text><rect x="22" y="132" width="160" height="100" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="102.0" y="176.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">1. Classe</text><text x="102.0" y="196.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">match réel</text><rect x="208" y="132" width="160" height="100" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="288.0" y="176.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">2. Marque</text><text x="288.0" y="196.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP / PCP</text><rect x="394" y="132" width="160" height="100" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="474.0" y="176.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">3. Action</text><text x="474.0" y="196.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">policer / queue</text><rect x="580" y="132" width="160" height="100" rx="10" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="660.0" y="176.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">4. Hardware</text><text x="660.0" y="196.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">drops / occupancy</text><rect x="766" y="132" width="170" height="100" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="851.0" y="176.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">5. Application</text><text x="851.0" y="196.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">SLA perçu</text><line x1="182" y1="182" x2="208" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="208.0,182.0 196.0,175.0 196.0,189.0" fill="#93c5fd"/><line x1="368" y1="182" x2="394" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="394.0,182.0 382.0,175.0 382.0,189.0" fill="#93c5fd"/><line x1="554" y1="182" x2="580" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="580.0,182.0 568.0,175.0 568.0,189.0" fill="#93c5fd"/><line x1="740" y1="182" x2="766" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="766.0,182.0 754.0,175.0 754.0,189.0" fill="#93c5fd"/><text x="480" y="285" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="middle">Combiner configuration, compteurs, capture et mesure applicative.</text><text x="480" y="313" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Un compteur nul peut indiquer mauvais match, mauvais sens ou compteur non exposé.</text></svg>

### 10.2 Lire les symptômes

| Symptomatique observée | Hypothèse prioritaire | Vérification suivante |
|---|---|---|
| Classe voix à zéro paquet | Mauvais match ou absence de trafic | Confirmer DSCP, ports, sens et interface |
| EF reçoit beaucoup de trafic inattendu | Frontière de confiance insuffisante | Capture près de la source, compteurs de classe, règles de remark |
| Drops dans la classe prioritaire | LLQ trop faible ou surcharge de classe | Volume d’appels, taille paquet, match effectif, admission |
| Gigue hausse sans drops visibles | File cachée, underlay ou endpoint | RTT sous charge, compteurs hardware, mesure applicative |
| Shaping élevé mais débit utile faible | Limite opérateur, overhead, pertes ou TCP | Comparer profils, MTU, retransmissions et compteurs |
| Policy affichée mais pas de compteurs | Policy non programmée ou commande inadaptée | Guide du matériel, statistiques ASIC/QFP, direction |
| IPv4 correct, IPv6 mauvais | Policy ou route différente | Répéter les vérifications sur IPv6 |

### 10.3 Les compteurs ne racontent pas toute l’histoire

Un compte de paquets sur la classe confirme que la classification a eu lieu dans ce point du chemin. Il ne garantit ni la programmation du traitement matériel ni le résultat de bout en bout. Certains compteurs ne sont actualisés qu’à certaines périodes ; certains drops sont comptés ailleurs ; certains équipements cachent les statistiques par classe. Toujours corréler compteurs, captures, tests sous charge et mesures applicatives.

### 10.4 Commandes de vérification Cisco

Exemples usuels selon IOS/IOS XE :

```text
show policy-map
show policy-map interface GigabitEthernet0/0/0
show class-map
show interfaces GigabitEthernet0/0/0
show running-config interface GigabitEthernet0/0/0
show platform hardware ...
```

La dernière commande n’est volontairement pas complétée : les arbres `show platform hardware` sont très spécifiques au modèle et à la version. Utilise l’aide CLI (`show platform hardware ?`) et le guide de dépannage adapté. Pour un équipement Catalyst, un routeur ASR/ISR et une plateforme plus récente, la même commande peut ne pas exister ou afficher d’autres unités. Ne jamais interpréter un compteur sans connaître sa portée et son intervalle de collecte.

### 10.5 Distinguer congestion, panne physique et serveur lent

Les erreurs CRC, la perte de carrier, la saturation CPU, le MTU, une mauvaise route, un serveur surchargé ou une application lente ne seront pas réglés par une policy QoS. Pour isoler le problème, compare les mesures à différents points du chemin, examine les retransmissions TCP, les erreurs d’interface, les files et les ressources des endpoints. La QoS corrige la gestion d’une ressource partagée ; elle ne remplace pas l’analyse réseau générale.

## 11. Matrice de test et critères d’acceptation

Une policy doit être testée dans des conditions représentatives : charge normale, pointe prévisible, trafic de fond massif, nombre attendu d’appels et panne d’un lien si la redondance fait partie du design. Documente les générateurs de trafic, les points de capture, les mesures, la durée et les critères de réussite. N’improvise pas une saturation sur un réseau de production sans fenêtre approuvée, autorisation, limites et plan d’arrêt.

### Schéma 13 — Matrice de classes de service

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Matrice de classes de service"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Matrice de classes de service</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Exemple à adapter à une politique documentée</text><rect x="28" y="93" width="904" height="42" rx="7" fill="#14532d" stroke="#64748b" stroke-width="1"/><text x="43" y="110" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">Voix</text><text x="240" y="110" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">EF / 46</text><text x="485" y="110" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">LLQ dimensionnée</text><text x="750" y="110" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Perte / gigue</text><rect x="28" y="142" width="904" height="42" rx="7" fill="#1e3a8a" stroke="#64748b" stroke-width="1"/><text x="43" y="159" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">Signalisation</text><text x="240" y="159" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">CS3/CS5 selon design</text><text x="485" y="159" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Garantie / contrôle</text><text x="750" y="159" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Établissement session</text><rect x="28" y="191" width="904" height="42" rx="7" fill="#5b21b6" stroke="#64748b" stroke-width="1"/><text x="43" y="208" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">Vidéo interactive</text><text x="240" y="208" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">AF41 ou classe locale</text><text x="485" y="208" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Garantie / partage</text><text x="750" y="208" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">RTT / loss / jitter</text><rect x="28" y="240" width="904" height="42" rx="7" fill="#422006" stroke="#64748b" stroke-width="1"/><text x="43" y="257" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">Transactions</text><text x="240" y="257" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">AF2/AF3 selon design</text><text x="485" y="257" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">CBWFQ / shaping</text><text x="750" y="257" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Temps transaction</text><rect x="28" y="289" width="904" height="42" rx="7" fill="#334155" stroke="#64748b" stroke-width="1"/><text x="43" y="306" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">Bulk / backup</text><text x="240" y="306" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DF ou CS1 maîtrisé</text><text x="485" y="306" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Reste / policer</text><text x="750" y="306" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">Débit, impact</text><text x="480" y="358" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Matrice indicative : adapter au SLA, aux applications et à la plateforme.</text></svg>

Critères possibles à adapter :

- la classe prioritaire reconnaît uniquement les flux autorisés ;
- le trafic temps réel reste dans les objectifs de pertes, de délai et de gigue convenus sous la charge de pointe ;
- les classes métier reçoivent leur partage prévu quand le lien est congestionné ;
- le trafic best effort continue de progresser et ne subit pas une famine inattendue ;
- les compteurs de drops et de policing correspondent aux événements générés ;
- les marquages sont cohérents aux frontières LAN, WAN, tunnel et fournisseur ;
- le retour arrière fonctionne et les équipes peuvent expliquer les commandes utilisées.

### 11.1 Test avant/après

Compare des périodes et des scénarios similaires. Mesure les résultats avec une unité et une direction clairement définies. Un changement QoS peut réduire les drops dans une classe et augmenter l’attente dans une autre ; cela peut être acceptable si le compromis est prévu, mais doit être visible. Documente aussi le trafic non prioritaire pour éviter de déclarer succès uniquement parce que l’application critique s’améliore.

## 12. Laboratoire guidé : WAN congestionné avec plusieurs classes

### 12.1 Topologie et hypothèses

Le lab illustre un petit site avec téléphones, postes métier et sauvegardes. Le CPE est relié à un service opérateur de débit nominal 20 Mbit/s. Une politique de shaping sur le CPE vise à éviter que la congestion se fasse hors du contrôle de l’entreprise. Cette topologie est pédagogique ; elle n’impose pas la même syntaxe sur toutes les familles Cisco.

### Schéma 14 — Laboratoire de synthèse

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Laboratoire de synthèse"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Laboratoire de synthèse</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Voix, données et sauvegarde sur WAN contraint</text><rect x="22" y="115" width="165" height="78" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="104.5" y="148.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Téléphone IP</text><text x="104.5" y="168.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">EF validé</text><rect x="22" y="236" width="165" height="78" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="104.5" y="269.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Postes métier</text><text x="104.5" y="289.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">AF selon politique</text><rect x="22" y="335" width="165" height="45" rx="10" fill="#334155" stroke="#94a3b8" stroke-width="2"/><text x="104.5" y="352.58" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">Sauvegarde</text><text x="104.5" y="370.58" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">DF / faible priorité</text><rect x="275" y="180" width="180" height="95" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="365.0" y="222.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Switch accès</text><text x="365.0" y="242.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">trusted boundary</text><rect x="525" y="180" width="180" height="95" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="615.0" y="222.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Routeur agence</text><text x="615.0" y="242.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">parent shape + child</text><rect x="780" y="180" width="150" height="95" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="855.0" y="222.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">WAN 20 Mb/s</text><text x="855.0" y="242.26" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">service opérateur</text><line x1="187" y1="154" x2="275" y2="205" stroke="#93c5fd" stroke-width="3"/><polygon points="275.0,205.0 268.1,192.9 261.1,205.0" fill="#93c5fd"/><line x1="187" y1="275" x2="275" y2="236" stroke="#93c5fd" stroke-width="3"/><polygon points="275.0,236.0 261.2,234.5 266.9,247.3" fill="#93c5fd"/><line x1="187" y1="357" x2="275" y2="252" stroke="#93c5fd" stroke-width="3"/><polygon points="275.0,252.0 261.9,256.7 272.7,265.7" fill="#93c5fd"/><line x1="455" y1="227" x2="525" y2="227" stroke="#93c5fd" stroke-width="3"/><polygon points="525.0,227.0 513.0,220.0 513.0,234.0" fill="#93c5fd"/><line x1="705" y1="227" x2="780" y2="227" stroke="#93c5fd" stroke-width="3"/><polygon points="780.0,227.0 768.0,220.0 768.0,234.0" fill="#93c5fd"/><text x="480" y="366" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Objectif : prioriser la voix sans affamer le trafic de données.</text></svg>

### 12.2 Plan d’adressage d’exemple

| Segment | Sous-réseau | Passerelle typique | Usage |
|---|---|---|---|
| VLAN Voix | `10.10.10.0/24` | `10.10.10.1` | Téléphones IP |
| VLAN Métier | `10.10.20.0/24` | `10.10.20.1` | Postes de travail |
| VLAN Services | `10.10.30.0/24` | `10.10.30.1` | Services autorisés |
| WAN de labo | Selon maquette | Selon opérateur simulé | Trafic contraint |

Ces préfixes sont réservés à la documentation. Évite d’utiliser une plage déjà présente dans ton réseau réel si tu raccordes le lab à du matériel de production.

### 12.3 Exemple MQC simplifié

Le bloc suivant est une base illustrative pour IOS/IOS XE. Vérifie la prise en charge sur ton équipement, remplace les valeurs par ton design et teste la programmation matérielle. L’exemple suppose que les DSCP ont été validés à l’entrée :

```text
class-map match-any CM-VOICE
 match dscp ef
!
class-map match-any CM-BUSINESS
 match dscp af21 af22 af23
!
class-map match-any CM-BULK
 match dscp cs1
!
policy-map WAN-CHILD
 class CM-VOICE
  priority percent 10
 class CM-BUSINESS
  bandwidth percent 30
 class CM-BULK
  bandwidth percent 5
 class class-default
  fair-queue
!
policy-map WAN-PARENT
 class class-default
  shape average 20000000
  service-policy WAN-CHILD
!
interface GigabitEthernet0/0/0
 service-policy output WAN-PARENT
```

**À ne pas copier aveuglément :** la hiérarchie de policies, `shape average`, `priority percent`, `bandwidth percent` et `fair-queue` ne sont pas acceptés partout sous cette forme. La valeur de 20 Mbit/s n’est correcte que si elle correspond au profil de service dans les unités mesurées par la plateforme. Vérifie que l’enfant est réellement appliqué et que les classes sont comptabilisées.

### 12.4 Étapes du laboratoire

1. Sans policy, mesure les débits, le RTT sous charge et les drops de l’interface.
2. Génère séparément du trafic de voix simulé, des transactions et un transfert massif contrôlé.
3. Configure la classification et vérifie que chaque classe reconnaît seulement le trafic voulu.
4. Applique la policy enfant, puis le parent shaping si la plateforme le permet.
5. Répète les tests sous charge simultanée et compare les résultats par classe.
6. Modifie une variable à la fois : shaping, LLQ, bande passante d’une classe ou stratégie de marquage.
7. Observe les compteurs et note les régressions potentielles pour le trafic non prioritaire.
8. Exporte la configuration, les résultats et les limites de la plateforme dans le rapport du lab.

### 12.5 Grille de rendu

| Élément | Preuve demandée |
|---|---|
| Classification | Compteurs qui montent seulement pour le trafic attendu |
| Marquage | Capture ou preuve de DSCP avant/après frontière |
| Shaping | Débit agrégé plafonné au profil attendu sous charge |
| LLQ | Drops et occupation analysés, pas seulement absence de perte |
| CBWFQ | Débit relatif par classe lorsque toutes les classes sont actives |
| Résultat utilisateur | RTT, gigue, perte ou test applicatif pertinent |
| Retour arrière | Configuration précédente restaurée et testée |

## 13. Déploiement sécurisé et gouvernance

### 13.1 Déployer par étapes

Une policy QoS peut modifier les priorités et les pertes sur tout un site. Un déploiement progressif doit commencer par une baseline, une validation sur un port ou un petit site pilote, un test sous charge, une revue des compteurs et un plan de retour arrière. Étends uniquement lorsque les mesures et l’exploitation confirment le résultat.

### Schéma 15 — Déploiement contrôlé

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Déploiement contrôlé"><rect x="1" y="1" width="958" height="398" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Déploiement contrôlé</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Baseline, pilote, extension et retour arrière</text><rect x="28" y="147" width="160" height="100" rx="10" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="108.0" y="191.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">1. Baseline</text><text x="108.0" y="210.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">mesurer sans changement</text><line x1="188" y1="198" x2="216" y2="198" stroke="#93c5fd" stroke-width="3"/><polygon points="216.0,198.0 204.0,191.0 204.0,205.0" fill="#93c5fd"/><rect x="216" y="147" width="160" height="100" rx="10" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="296.0" y="191.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">2. Pilote</text><text x="296.0" y="210.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">un site / un lien</text><line x1="376" y1="198" x2="404" y2="198" stroke="#93c5fd" stroke-width="3"/><polygon points="404.0,198.0 392.0,191.0 392.0,205.0" fill="#93c5fd"/><rect x="404" y="147" width="160" height="100" rx="10" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="484.0" y="191.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">3. Comparer</text><text x="484.0" y="210.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">avant / après</text><line x1="564" y1="198" x2="592" y2="198" stroke="#93c5fd" stroke-width="3"/><polygon points="592.0,198.0 580.0,191.0 580.0,205.0" fill="#93c5fd"/><rect x="592" y="147" width="160" height="100" rx="10" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="672.0" y="191.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">4. Étendre</text><text x="672.0" y="210.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">fenêtre maîtrisée</text><line x1="752" y1="198" x2="780" y2="198" stroke="#93c5fd" stroke-width="3"/><polygon points="780.0,198.0 768.0,191.0 768.0,205.0" fill="#93c5fd"/><rect x="780" y="147" width="160" height="100" rx="10" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="860.0" y="191.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">5. Retour arrière</text><text x="860.0" y="210.92" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">critères explicites</text><text x="480" y="300" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Ne pas déployer à grande échelle avant d’avoir testé congestion, panne et rollback.</text></svg>

### 13.2 Gouvernance de la matrice DSCP

Maintiens une source de vérité documentant les classes, DSCP entrants acceptés, translations aux frontières, utilisateurs autorisés, politiques de files, seuils et équipes propriétaires. Évite les changements ponctuels non documentés : deux équipes peuvent attribuer le même DSCP à des usages contradictoires. Les changements doivent être versionnés et accompagnés des commandes de vérification correspondantes.

### 13.3 Sécurité, contrôle du trafic et prévention de famine

Le marquage doit être considéré comme une donnée d’entrée potentiellement non fiable jusqu’à sa validation. Un attaquant ou une erreur de configuration peut exploiter une classe prioritaire ou remplir les buffers. Les politiques de contrôle d’accès, limites de débit, protections du plan de contrôle et règles de confiance doivent être séparées mais coordonnées. La QoS ne remplace pas le filtrage de sécurité, et le filtrage ne remplace pas la gestion de congestion.

## 14. Études de cas

### Cas 1 — La voix est bonne seule, mauvaise pendant une sauvegarde

**Hypothèse :** l’uplink vers le WAN est congestionné par le transfert massif.  
**Investigation :** relever les drops de file, le marquage voix, le débit de sauvegarde et le point exact de congestion. Vérifier si la policy est sur la bonne interface et dans le bon sens.  
**Correction possible :** shaping parent au débit effectif, LLQ contrôlée pour le trafic voix réel, partage explicite pour données et bulk.  
**Validation :** même test simultané avant/après ; mesurer la voix mais aussi le débit et l’équité des autres classes.

### Cas 2 — La classe EF transporte du trafic inattendu

**Hypothèse :** la frontière de confiance accepte les marques des PC ou d’un réseau invité.  
**Investigation :** capture proche de la source, mapping des ports/VLAN et compteurs d’entrée/sortie.  
**Correction possible :** classer/re-marquer le trafic non fiable, ne faire confiance qu’aux sources prévues, documenter le cas des PC derrière les téléphones.  
**Validation :** générer un paquet DSCP EF depuis un terminal non autorisé et vérifier qu’il n’obtient pas le traitement voix.

### Cas 3 — Policy configurée, statistiques absentes

**Hypothèses :** mauvais sens, mauvais type d’interface, policy non programmée dans le matériel, commandes de statistiques différentes ou trafic qui ne correspond pas.  
**Méthode :** vérifier running-config, `show policy-map interface`, l’interface et la direction ; produire du trafic de test contrôlé ; utiliser les commandes de plateforme documentées. Ne conclus pas que la policy fonctionne uniquement parce que l’application accepte la configuration.

### Cas 4 — Le débit WAN plafonne en dessous de la valeur attendue

**Hypothèses :** shaping trop bas, profil opérateur mesuré différemment, overhead, pertes, MTU, retransmissions TCP ou limitation côté serveur.  
**Méthode :** mesurer séparément débit brut et utile, examiner les retransmissions, tester dans les deux sens, vérifier l’overhead et comparer aux termes du contrat. Ne relève pas automatiquement le shaping sans vérifier la capacité contractuelle et les files en aval.

### Cas 5 — Vidéo dégradée alors que la voix est préservée

**Hypothèses :** la classe vidéo partage insuffisamment les ressources, le trafic vidéo a été mal classé, un tunnel n’applique pas la même marque, ou le serveur est la cause.  
**Méthode :** vérifier le DSCP à l’entrée et à la sortie, le nombre de flux simultanés, les compteurs de la classe vidéo, le sens retour et les métriques du terminal. N’élargis pas la LLQ par réflexe si le besoin réel est une meilleure garantie ou un meilleur partage pour la vidéo.

## 15. Exercices corrigés

### Exercice 1 — Identifier la mauvaise hypothèse

Une équipe configure DSCP EF sur les téléphones et suppose que le trafic sera prioritaire jusque dans le cloud. Quel élément manque ?

**Correction :** la marque ne garantit pas le traitement. Il faut vérifier la confiance, la préservation ou la traduction des DSCP, le mapping vers les files à chaque frontière, le contrat opérateur et les mesures de performance de bout en bout.

### Exercice 2 — Calcul de charge voix

On estime 30 appels simultanés à 90 kbit/s par appel et par sens, overhead déjà inclus. Quelle est l’estimation initiale du débit voix ?

**Correction :** `30 × 90 kbit/s = 2 700 kbit/s`, soit 2,7 Mbit/s par sens. Ajouter une marge basée sur la mesure, vérifier les périodes de pointe et dimensionner la classe à partir de la capacité WAN réellement disponible.

### Exercice 3 — Pourquoi un shaping parent ?

Une interface Ethernet est à 1 Gbit/s, mais le service opérateur limite à 50 Mbit/s. Pourquoi une policy de sortie avec classes mais sans shaping peut-elle ne pas suffire ?

**Correction :** la congestion peut apparaître après le point où la policy locale fait ses décisions, dans un équipement opérateur qui applique son propre profil. Un parent shaping proche du débit réel peut faire gérer la file localement et organiser les classes dans le débit façonné ; la valeur exacte doit être testée et adaptée à la définition du service.

### Exercice 4 — Interpréter un compteur LLQ

La classe voix reconnaît les paquets et voit des drops, mais le RTT est stable. Que faire ?

**Correction :** ne pas conclure immédiatement que la QoS est correcte ou incorrecte. Vérifier volume de trafic, drops exacts, appels simultanés, gigue/perte applicative, fréquence de mesure et autre cause possible. Le RTT seul ne reflète pas toute la qualité voix. Un compteur de drop peut être concentré sur un test ou un sens particulier.

## 16. Quiz de validation

**1. Quel est le rôle de `class-map` dans MQC ?**  
A. Choisir l’interface où s’applique la policy. B. Définir les critères de classification. C. Créer un tunnel. D. Réserver de la bande passante automatiquement.

**2. Pourquoi le DSCP EF ne suffit-il pas à garantir une qualité de voix ?**  
A. Parce que DSCP n’existe que dans IPv6. B. Parce que la marque peut être ignorée, modifiée ou non mappée à une file appropriée. C. Parce que EF signifie best effort. D. Parce que le DSCP réserve toujours 46 % du lien.

**3. Que fait généralement le shaping ?**  
A. Retarde les paquets dans un tampon pour lisser le débit. B. Remplace le routage. C. Accélère le débit physique. D. Supprime tous les paquets EF.

**4. Quelle est la différence principale entre policer et shaper ?**  
A. Aucun. B. Le policer évalue la conformité et peut drop/remark ; le shaper met en tampon pour réguler le débit, dans la limite de ses buffers. C. Le shaper fonctionne uniquement sur IPv6. D. Le policer change le routage.

**5. Pourquoi utiliser HQoS ?**  
A. Pour combiner un plafond agrégé de service avec une politique de classes, lorsque la plateforme le permet. B. Pour remplacer le DSCP par une adresse IP. C. Pour désactiver la congestion. D. Pour automatiser le DNS.

**6. Que prouve un compteur de classe qui augmente ?**  
A. Que l’application est forcément parfaite. B. Que des paquets ont correspondu à la classe au point observé, sans garantir à lui seul le résultat de bout en bout. C. Que le lien opérateur n’a aucune perte. D. Que toutes les files sont matériellement programmées.

**7. Dans un tunnel, quel point doit être vérifié ?**  
A. Uniquement le port TCP 80. B. Le traitement des en-têtes interne et externe, y compris le mapping DSCP. C. Aucun, les tunnels préservent toujours les marques. D. Seulement le nom de l’interface.

**8. Quelle preuve aide à localiser les drops QoS ?**  
A. Une seule capture DNS. B. Compteurs par classe et de sortie, mesure sous charge et corrélation avec l’application. C. Le nombre d’utilisateurs uniquement. D. La longueur du nom de la policy.

**9. Pourquoi une policy prioritaire trop large est-elle risquée ?**  
A. Elle peut consommer une trop grande part de la sortie et dégrader les classes restantes. B. Elle ajoute du débit à la fibre. C. Elle supprime le besoin de mesure. D. Elle améliore toutes les classes dans tous les cas.

**10. Quel est le meilleur ordre de déploiement ?**  
A. Changer tous les routeurs immédiatement. B. Baseline, pilote, test sous charge, comparaison, extension contrôlée et rollback prêt. C. Activer EF sur tous les paquets. D. Supprimer les compteurs avant la validation.

### Réponses du quiz

1. B — la classification est définie dans le `class-map`.  
2. B — DSCP seul n’impose aucun traitement de bout en bout.  
3. A — le shaping régule le rythme en mettant temporairement en tampon.  
4. B — les mécanismes n’ont pas le même comportement face aux excès.  
5. A — HQoS hiérarchise des politiques dans les limites du support matériel.  
6. B — les compteurs valident une partie du chemin, pas toute l’expérience.  
7. B — l’encapsulation modifie la visibilité des champs utilisés par la QoS.  
8. B — il faut combiner plusieurs preuves.  
9. A — un traitement prioritaire excessif peut affamer les autres classes.  
10. B — le déploiement doit être mesuré et réversible.

## 17. Checklist de mise en production

- [ ] Le SLA applicatif et les objectifs de validation sont écrits et mesurables.
- [ ] La matrice DSCP/PCP/classe/file est approuvée et versionnée.
- [ ] La frontière de confiance et les règles de remark sont définies.
- [ ] Les classes disposent de critères distincts et testables.
- [ ] Le budget de voix est calculé avec overhead et appels simultanés.
- [ ] LLQ est contrôlée et le trafic prioritaire autorisé est limité.
- [ ] CBWFQ/partage des ressources protège les classes restantes.
- [ ] Shaping correspond au débit réel du service et à son overhead.
- [ ] La compatibilité HQoS et la programmation matérielle sont confirmées.
- [ ] Les effets de WRED/AQM/ECN sont compris et validés si utilisés.
- [ ] QoS IPv4 et IPv6 a été vérifiée lorsque le réseau est double pile.
- [ ] QoS sous tunnel et propagation DSCP ont été testées.
- [ ] Compteurs de drops, policing, queues et erreurs ont été relevés avant/après.
- [ ] Les mesures applicatives montrent une amélioration conforme au SLO.
- [ ] Les classes non prioritaires ne subissent pas de famine non prévue.
- [ ] Un pilote et un rollback ont été testés.
- [ ] Les commandes utilisées sont compatibles avec le modèle et la version.

## 18. Glossaire

- **AQM** : Active Queue Management, contrôle actif des files d’attente.
- **CBWFQ** : Class-Based Weighted Fair Queuing.
- **CIR/Bc/Be** : paramètres de profil et rafales d’un modèle de policing/shaping.
- **CoS/PCP** : champ de priorité 802.1Q sur 3 bits.
- **DiffServ** : architecture de services différenciés IP.
- **DSCP** : champ de classification DiffServ sur 6 bits.
- **ECN** : Explicit Congestion Notification.
- **HQoS** : QoS hiérarchique, policy parent et policy enfant selon la plateforme.
- **LLQ** : Low Latency Queueing, traitement prioritaire à garde-fous.
- **MQC** : Modular QoS CLI, modèle Cisco de classification et policy.
- **PHB** : Per-Hop Behavior, comportement appliqué à un paquet par un saut.
- **Shaping** : régulation du débit par mise en tampon.
- **Policing** : contrôle d’un profil avec actions de conformité.
- **WRED** : Weighted Random Early Detection.

## 19. Références techniques

Utilise les documents correspondant à la plateforme et à la release réellement déployées. Les guides Cisco ci-dessous sont des points d’entrée ; certains exemples du cours sont volontairement présentés comme modèles à adapter.

- Cisco, **Quality of Service Configuration Guide — Cisco IOS XE 17.x** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/qos/b-quality-of-service.html
- Cisco, **Quality of Service Configuration Guide — Catalyst 9000** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/qos/quality-of-service-configuration-guide/m-quality-of-service.html
- Cisco, **QoS Frequently Asked Questions** : https://www.cisco.com/c/en/us/support/docs/quality-of-service-qos/qos-policing/22833-qos-faq.html
- IETF, **RFC 2474 — Definition of the Differentiated Services Field (DS Field) in the IPv4 and IPv6 Headers** : https://www.rfc-editor.org/rfc/rfc2474
- IETF, **RFC 2475 — An Architecture for Differentiated Services** : https://www.rfc-editor.org/rfc/rfc2475
- IETF, **RFC 3168 — The Addition of Explicit Congestion Notification (ECN) to IP** : https://www.rfc-editor.org/rfc/rfc3168
- IETF, **RFC 4594 — Configuration Guidelines for DiffServ Service Classes** : https://www.rfc-editor.org/rfc/rfc4594


## Conclusion

Au niveau intermédiaire, la réussite QoS ne se mesure pas au nombre de classes ou à la complexité d’une policy. Elle se mesure à la capacité d’expliquer ce qui se passe en période de congestion, de démontrer quelles classes sont reconnues et servies, de préserver les objectifs applicatifs et de repérer les effets secondaires. Chaque valeur doit avoir une raison documentée, chaque changement un test et chaque déploiement un retour arrière. La politique est réussie lorsque le comportement observé correspond aux objectifs convenus — y compris pour le trafic qui n’est pas prioritaire.
