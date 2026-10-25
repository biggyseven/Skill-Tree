# IS-IS — Niveau Intermédiaire

## Positionnement dans le parcours

Ce cours prolonge **IS-IS — Niveau Débutant**. Il ne reprend donc pas chaque notion depuis zéro : on considère que vous savez déjà lire un NET, distinguer L1 de L2, expliquer le rôle général des IIH/Hello, LSP, CSNP et PSNP, et mettre en route une adjacency simple. Le niveau intermédiaire étudie ce qui se passe derrière ces notions : formation précise des voisinages, synchronisation de la LSDB, sélection des chemins par métrique, comportement sur un réseau multi-accès, vérification d'un domaine à plusieurs routeurs et dépannage méthodique.

> **Cadre des exemples :** les commandes utilisent une syntaxe de type Cisco IOS/IOS XE. Les noms de commandes et les fonctions disponibles varient selon la version, la gamme matérielle et le mode de configuration. Dans un laboratoire réel, vérifiez `?`, la documentation de la version et le résultat des commandes `show` avant d'appliquer une commande en production.

## Compétences visées

À la fin de ce cours, vous devez savoir :

- expliquer comment une adjacency est négociée et pourquoi deux routeurs peuvent se voir sans devenir voisins au niveau attendu ;
- différencier adjacency, LSDB, table de routage et FIB ;
- décrire la synchronisation de la LSDB avec CSNP et PSNP, le numéro de séquence, le checksum et la durée de vie d'un LSP ;
- raisonner sur les métriques IS-IS et privilégier les métriques étendues (wide metrics) ;
- comprendre le rôle du DIS et du pseudonœud sur un réseau broadcast ;
- interpréter les routes L1, L2 et inter-aires, y compris le principe du route leaking ;
- construire et vérifier un petit laboratoire multi-routeurs ;
- diagnostiquer une adjacency instable, une route absente ou un chemin sous-optimal à partir d'indices vérifiables.


## 1. Architecture logique : les quatre états à ne pas confondre

En dépannage, quatre objets sont souvent mélangés alors qu'ils décrivent des étapes différentes.

1. **Adjacency / voisinage** : le routeur a établi une relation IS-IS avec un autre système sur une interface et à un niveau déterminé.
2. **LSDB** (*Link-State Database*) : la base des LSP reçus et conservés pour un niveau. Les routeurs qui partagent une même topologie de niveau doivent converger vers une représentation cohérente des informations diffusées à ce niveau.
3. **RIB** (*Routing Information Base*) : la table de routage qui contient les routes retenues par le processus de routage, après comparaison et application des règles de la plateforme.
4. **FIB** (*Forwarding Information Base*) : la structure utilisée pour transférer réellement les paquets. Une route présente dans une base de protocole ne garantit pas à elle seule que le paquet sera transféré comme prévu : il faut aussi examiner la route active et le prochain saut.

Une adjacency `Up` ne prouve donc pas que tous les préfixes attendus ont été annoncés. Une entrée LSP ne prouve pas qu'une route a été installée dans la RIB. Et une route dans la RIB ne prouve pas que le service de bout en bout fonctionne : les interfaces, ARP/ND, ACL, MTU ou le chemin de retour peuvent encore poser problème.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 300" role="img" aria-labelledby="isis-int-states-title isis-int-states-desc">
  <title id="isis-int-states-title">De l'adjacency au transfert</title>
  <desc id="isis-int-states-desc">Quatre états distincts : voisinage, base de données d'état de liens, table de routage et base de transfert. Des flèches indiquent le flux logique de la découverte à la transmission.</desc>
  <defs><marker id="isis-states-arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#93a4b8"/></marker></defs>
  <rect width="960" height="300" rx="18" fill="#0b1220"/>
  <text x="480" y="34" text-anchor="middle" fill="#f8fafc" font-size="21" font-family="Arial,sans-serif" font-weight="700">Quatre plans de vérification</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="30" y="85" width="200" height="110" rx="12" fill="#142a42" stroke="#60a5fa" stroke-width="1.5"/><text x="130" y="117" fill="#93c5fd" font-size="16" font-weight="700">1. Adjacency</text><text x="130" y="143" fill="#e2e8f0" font-size="13">Le voisin est-il établi ?</text><text x="130" y="165" fill="#94a3b8" font-size="12">Interface / niveau</text>
    <rect x="270" y="85" width="200" height="110" rx="12" fill="#182d3b" stroke="#22d3ee" stroke-width="1.5"/><text x="370" y="117" fill="#67e8f9" font-size="16" font-weight="700">2. LSDB</text><text x="370" y="143" fill="#e2e8f0" font-size="13">Les LSP sont-ils cohérents ?</text><text x="370" y="165" fill="#94a3b8" font-size="12">Topologie connue</text>
    <rect x="510" y="85" width="200" height="110" rx="12" fill="#203126" stroke="#4ade80" stroke-width="1.5"/><text x="610" y="117" fill="#86efac" font-size="16" font-weight="700">3. RIB</text><text x="610" y="143" fill="#e2e8f0" font-size="13">Quelle route est retenue ?</text><text x="610" y="165" fill="#94a3b8" font-size="12">Préfixe / métrique / next-hop</text>
    <rect x="750" y="85" width="180" height="110" rx="12" fill="#342b1b" stroke="#fbbf24" stroke-width="1.5"/><text x="840" y="117" fill="#fcd34d" font-size="16" font-weight="700">4. FIB</text><text x="840" y="143" fill="#e2e8f0" font-size="13">Comment transférer ?</text><text x="840" y="165" fill="#94a3b8" font-size="12">Adjacence L2/ARP/ND</text>
    <path d="M230 140 H264 M470 140 H504 M710 140 H744" stroke="#93a4b8" stroke-width="2.5" marker-end="url(#isis-states-arrow)"/>
    <text x="480" y="242" fill="#cbd5e1" font-size="14">Un contrôle réussi à gauche ne garantit pas les contrôles à droite.</text>
    <text x="480" y="266" fill="#94a3b8" font-size="12">Dépannez dans l'ordre, puis testez le trafic réel dans les deux sens.</text>
  </g>
</svg>

### Exemple de raisonnement

- `show isis neighbors` indique que R2 est voisin de R1 en L2, mais le préfixe `10.50.0.0/16` n'apparaît pas dans la table : examinez la LSDB L2, les TLV de portée IP, le niveau d'annonce et le calcul de route.
- Le LSP annonce bien le préfixe, mais la RIB ne le retient pas : cherchez une route plus préférée, une politique, une métrique inacceptable ou une différence de famille d'adresses.
- La RIB pointe vers R3, mais le ping échoue : vérifiez le prochain saut, l'interface de sortie, les résolutions de voisin, les filtres et le chemin retour.


## 2. Formation et maintien des adjacencies

### 2.1 Les IIH ne sont pas de simples « ping IS-IS »

Les **IS-IS Hello (IIH)** sont les PDU de découverte et de maintien des voisins. Leur format et leurs conditions diffèrent selon qu'il s'agit d'un lien point-à-point ou d'un réseau broadcast. Ils transportent notamment des informations qui permettent aux routeurs de vérifier que les paramètres indispensables sont compatibles. IS-IS fonctionne directement sur la couche liaison de données (Ethernet utilise l'encapsulation IS-IS prévue à cet effet) : il ne dépend pas d'une session TCP ni d'une adresse IPv4 de voisin pour établir le protocole.

Sur une liaison IP point-à-point, les adresses IP doivent être configurées pour transporter le trafic IP, mais l'adjacency IS-IS n'est pas formée en ouvrant une session TCP entre ces adresses. Cette distinction est utile : un ping IP entre deux interfaces peut fonctionner alors que l'adjacency IS-IS ne se forme pas, ou le voisinage IS-IS peut exister alors qu'un problème IP de couche supérieure empêche le ping d'un préfixe.

### 2.2 Conditions à contrôler

Selon le type de réseau, le niveau activé et la plateforme, les points suivants peuvent empêcher ou limiter le voisinage :

- **Interface incorrecte ou protocole non activé** : IS-IS doit être lié à l'interface où l'on attend les Hello.
- **Type de circuit / niveau incompatible** : une interface configurée uniquement en L1 ne peut pas fournir un voisinage L2 sur ce lien. Une interface L1/L2 laisse le routeur participer aux deux niveaux lorsque le voisin est lui aussi compatible.
- **Adresse d'aire** : la formation L1 requiert une aire compatible. Les règles sont différentes pour L2, qui permet de relier des aires différentes.
- **Authentification** : une configuration d'authentification incompatible peut provoquer le rejet des PDU, selon la portée et les fonctions utilisées.
- **Paramètres de lien / encapsulation** : le type de réseau, la prise en charge du protocole sur le média ou une erreur de câblage peuvent empêcher les Hello d'arriver.
- **Timers** : les intervalles et les durées de maintien peuvent influencer la détection des pertes et les instabilités, même si ce n'est pas toujours une exigence de valeur identique dans toutes les implémentations.
- **MTU et taille des LSP** : une MTU inadéquate peut affecter l'échange ou le traitement de certaines PDU, même si les Hello initiaux passent.

Ne concluez pas qu'une adjacency est impossible à partir d'un seul paramètre sans vérifier l'état observé et la documentation correspondant au système utilisé.

### 2.3 Niveau du routeur et niveau de l'interface

Il faut examiner séparément le **type de système** configuré globalement et le **type de circuit** de l'interface. Un routeur configuré `level-1-2` peut héberger une interface qui ne participe qu'à un seul niveau. Ce n'est pas nécessairement une erreur : une conception peut limiter un lien à L2 pour l'ossature, ou à L1 dans une aire.

Exemple conceptuel :

```text
R1 (L1/L2 global) ---- lien réservé à L2 ---- R2 (L1/L2 global)
```

Même si les deux routeurs sont L1/L2 globalement, ce lien peut être configuré pour L2 seulement. Il ne faut alors pas chercher de voisinage L1 sur cette interface.

### 2.4 États d'adjacence

Les libellés précis varient selon le système. Beaucoup de sorties affichent un état tel que `Up` lorsque la relation est établie. Sur les liaisons broadcast, l'élection du DIS et l'identification du pseudonœud ajoutent des informations qu'il faut lire en complément. En cas de panne intermittente, la durée pendant laquelle le voisin est resté actif, la fréquence des transitions et les journaux sont souvent plus utiles qu'une capture ponctuelle.

**Méthode de diagnostic :** vérifiez d'abord la présence et l'état de l'interface ; observez ensuite les voisins et le niveau ; contrôlez enfin la LSDB. Ne commencez pas par modifier les timers « au hasard » : vous risquez de masquer la cause ou d'aggraver la stabilité.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="isis-adj-title isis-adj-desc">
  <title id="isis-adj-title">Arbre de décision pour une adjacency absente</title>
  <desc id="isis-adj-desc">Un arbre de dépannage vérifie l'interface, l'activation d'IS-IS, les niveaux et l'aire, puis les paramètres de lien, l'authentification et les compteurs.</desc>
  <defs><marker id="isis-adj-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#8494a8"/></marker></defs>
  <rect width="960" height="350" rx="18" fill="#0b1220"/><text x="480" y="32" fill="#f8fafc" text-anchor="middle" font-size="21" font-weight="700" font-family="Arial,sans-serif">Adjacency absente : contrôler dans cet ordre</text>
  <g font-family="Arial,sans-serif" text-anchor="middle" font-size="13">
    <rect x="335" y="53" width="290" height="46" rx="9" fill="#172b42" stroke="#60a5fa"/><text x="480" y="81" fill="#dbeafe" font-weight="700">1. Interface up / bons compteurs ?</text>
    <path d="M480 99 V117" stroke="#8494a8" stroke-width="2" marker-end="url(#isis-adj-arrow)"/>
    <rect x="335" y="122" width="290" height="46" rx="9" fill="#172b42" stroke="#60a5fa"/><text x="480" y="150" fill="#dbeafe" font-weight="700">2. IS-IS activé sur cette interface ?</text>
    <path d="M480 168 V186" stroke="#8494a8" stroke-width="2" marker-end="url(#isis-adj-arrow)"/>
    <rect x="335" y="191" width="290" height="46" rx="9" fill="#2a2619" stroke="#fbbf24"/><text x="480" y="219" fill="#fef3c7" font-weight="700">3. Niveaux et aire compatibles ?</text>
    <path d="M480 237 V255" stroke="#8494a8" stroke-width="2" marker-end="url(#isis-adj-arrow)"/>
    <rect x="220" y="260" width="520" height="49" rx="9" fill="#183329" stroke="#34d399"/><text x="480" y="281" fill="#d1fae5" font-weight="700">4. Type de réseau, authentification, MTU et journaux</text><text x="480" y="298" fill="#a7f3d0" font-size="11">Comparer les deux extrémités ; modifier un paramètre à la fois</text>
    <text x="75" y="76" text-anchor="start" fill="#fca5a5" font-size="12">Non → couche liaison</text><text x="75" y="145" text-anchor="start" fill="#fca5a5" font-size="12">Non → configuration</text><text x="75" y="214" text-anchor="start" fill="#fcd34d" font-size="12">Non → niveau / aire</text>
  </g>
</svg>


## 3. LSP : diffusion, synchronisation et fraîcheur des données

### 3.1 Ce qu'un LSP représente

Chaque routeur origine ses propres **Link State PDUs (LSP)**. Un LSP peut inclure l'identité du routeur, ses voisins, les informations de portée de niveau, des préfixes IP et d'autres informations encodées dans des **TLV** (*Type-Length-Value*). Les détails précis dépendent des extensions, de la famille IP et du constructeur.

Un LSP n'est pas un paquet envoyé uniquement à un voisin qui demanderait une route. C'est un élément d'une base d'état de liens distribué. Le mécanisme de flooding diffuse les changements à travers les adjacencies du niveau correspondant, et chaque routeur s'en sert pour reconstituer la topologie pertinente.

### 3.2 Numéro de séquence, checksum et lifetime

Un LSP porte plusieurs éléments utiles à la cohérence de la base :

- **LSP ID** : identifie le LSP, en général lié au System ID d'origine et à un identifiant de fragment. Un routeur peut avoir plusieurs fragments lorsque ses informations ne tiennent pas dans un seul LSP.
- **Sequence number** : aide à reconnaître la version la plus récente d'un LSP de même identité. Quand une information change, la nouvelle version est normalement annoncée avec un numéro supérieur.
- **Checksum** : permet de détecter une corruption du contenu selon le mécanisme défini par le protocole.
- **Remaining lifetime / hold time** : limite la durée de conservation d'une information qui ne serait plus rafraîchie. Quand le LSP expire, il est retiré de la base conformément aux règles de purge.

Un numéro de séquence plus grand n'est pas un « coût plus élevé » : il s'agit d'une version de l'information, pas d'une métrique de routage.

### 3.3 CSNP et PSNP : résumé et acquittement

Les **Complete Sequence Number PDUs (CSNP)** décrivent un résumé des LSP présents dans la base, afin de comparer ce qu'un routeur possède et ce que l'autre annonce. Les **Partial Sequence Number PDUs (PSNP)** portent des entrées ciblées : elles peuvent demander des LSP manquants ou acquitter des informations, selon le contexte d'échange et le type de réseau.

Le point essentiel n'est pas de mémoriser une seule règle simplifiée comme « CSNP égale demande » : un CSNP est un inventaire ; un PSNP est un message partiel utilisé dans les mécanismes de synchronisation. Ces messages aident les routeurs à détecter et réparer une divergence de LSDB.

### 3.4 Base par niveau

Il existe une LSDB L1 et une LSDB L2 distinctes lorsque le routeur participe aux deux niveaux. Les LSP de niveau 1 et de niveau 2 ne sont pas interchangeables. Un routeur L1/L2 conserve les deux bases et exécute les calculs correspondants. Ainsi, un préfixe visible dans la LSDB L2 peut ne pas apparaître dans la LSDB L1 d'un routeur situé dans une aire, à moins que le préfixe ait été annoncé ou fuité vers ce niveau selon les règles applicables.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="isis-lsp-title isis-lsp-desc">
  <title id="isis-lsp-title">Synchronisation d'une base d'état de liens</title>
  <desc id="isis-lsp-desc">Deux routeurs comparent leurs LSP à l'aide de CSNP. Un LSP manquant ou obsolète est demandé ou annoncé avec PSNP puis flooding, jusqu'à convergence.</desc>
  <defs><marker id="isis-lsp-arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" fill="#93a4b8"/></marker></defs>
  <rect width="960" height="350" rx="18" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" font-size="21" fill="#f8fafc" font-family="Arial,sans-serif" font-weight="700">Réparer une divergence de LSDB</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="80" y="66" width="270" height="86" rx="12" fill="#142a42" stroke="#60a5fa"/><text x="215" y="93" fill="#93c5fd" font-size="17" font-weight="700">Routeur A</text><text x="215" y="117" fill="#e2e8f0" font-size="13">LSDB : LSP 1, 2, 3</text><text x="215" y="137" fill="#94a3b8" font-size="12">Manque la version récente de 4</text>
    <rect x="610" y="66" width="270" height="86" rx="12" fill="#183329" stroke="#34d399"/><text x="745" y="93" fill="#6ee7b7" font-size="17" font-weight="700">Routeur B</text><text x="745" y="117" fill="#e2e8f0" font-size="13">LSDB : LSP 1, 2, 3, 4</text><text x="745" y="137" fill="#94a3b8" font-size="12">Possède une version plus récente</text>
    <path d="M350 87 H603" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#isis-lsp-arrow)"/><text x="476" y="75" fill="#bfdbfe" font-size="12">CSNP : inventaire</text>
    <path d="M610 134 H357" stroke="#34d399" stroke-width="2.5" marker-end="url(#isis-lsp-arrow)"/><text x="481" y="153" fill="#a7f3d0" font-size="12">PSNP : demande / acquittement ciblé</text>
    <rect x="170" y="201" width="620" height="53" rx="10" fill="#2c2619" stroke="#fbbf24"/><text x="480" y="223" fill="#fef3c7" font-weight="700" font-size="15">Flooding de la version la plus récente</text><text x="480" y="241" fill="#fde68a" font-size="12">Contrôle du numéro de séquence, checksum et lifetime</text>
    <path d="M480 254 V274" stroke="#93a4b8" stroke-width="2" marker-end="url(#isis-lsp-arrow)"/>
    <rect x="260" y="281" width="440" height="43" rx="10" fill="#17372e" stroke="#34d399"/><text x="480" y="307" fill="#d1fae5" font-size="15" font-weight="700">LSDB cohérentes au niveau concerné</text>
  </g>
</svg>

### 3.5 Le flooding n'est pas le calcul SPF

Deux étapes complémentaires se produisent :

1. **Flooding / synchronisation** : les routeurs reçoivent les LSP et font converger leur base d'état de liens.
2. **Calcul SPF** : le routeur calcule les chemins à partir de la topologie disponible, puis met à jour les routes candidates.

Une panne peut donc concerner l'un ou l'autre mécanisme. Si un LSP ne traverse pas une adjacency, la LSDB peut être incomplète. Si la LSDB est cohérente mais que la route n'est pas retenue, cherchez plutôt les informations de préfixe, la métrique, le niveau, les politiques et la sélection de route.


## 4. Les métriques et le choix du chemin

### 4.1 Coût d'un chemin

IS-IS choisit les chemins en se basant sur les métriques annoncées pour les liens. En termes simples, le coût d'un chemin est la somme des métriques des liens qui le composent, dans la topologie et le niveau considérés. Si plusieurs chemins offrent un coût égal et que la plateforme autorise l'ECMP, plusieurs prochains sauts peuvent être installés. Le nombre de chemins multiples et la manière de les programmer dépendent de la plateforme.

Il ne faut pas assimiler automatiquement la métrique à la bande passante réelle. Si tous les liens ont la même valeur par défaut, le calcul risque de favoriser le nombre de sauts plutôt que la capacité ou la politique souhaitée. Dans une conception maîtrisée, documentez les métriques et vérifiez qu'elles représentent la préférence voulue.

### 4.2 Métriques étroites et métriques étendues

Les anciennes **narrow metrics** sont limitées et peuvent devenir insuffisantes dans des réseaux modernes. Les **wide metrics** ont été introduites pour permettre une plage de métrique plus large et prennent en charge les extensions modernes de portée et d'ingénierie de trafic. Pour les nouveaux laboratoires et déploiements, utilisez de préférence le style wide lorsque tous les équipements et la conception le permettent.

Sous une syntaxe Cisco classique :

```text
router isis CORE
 metric-style wide
```

Cette commande illustre l'intention ; le contexte exact et la compatibilité du mode de métrique sont à confirmer dans le guide de la version utilisée. Dans un réseau existant, ne basculez pas le style de métrique sans vérifier les autres routeurs et les TLV utilisés : les migrations doivent être planifiées.

### 4.3 Déterminer le meilleur chemin

Supposons une topologie avec deux chemins entre R1 et R4 :

- voie A : R1—R2—R4, coûts `10 + 20 = 30` ;
- voie B : R1—R3—R4, coûts `15 + 25 = 40`.

Dans cette topologie simplifiée et pour le même niveau de routage, le chemin par R2 a un coût total plus bas. Si le coût de R2—R4 augmente à 35, la voie A passe à 45 et la voie B à 40 : le chemin par R3 devient préférable après recalcul et convergence.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 345" role="img" aria-labelledby="isis-metric-title isis-metric-desc">
  <title id="isis-metric-title">Comparer deux chemins par métrique</title>
  <desc id="isis-metric-desc">Un chemin via R2 a un coût total initial de 30, contre 40 via R3. Après changement du lien R2-R4 de 20 à 35, ce chemin coûte 45 et la route via R3 à 40 devient meilleure.</desc>
  <rect width="960" height="345" rx="18" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" font-size="21" fill="#f8fafc" font-family="Arial,sans-serif" font-weight="700">Le coût total décide, pas le nombre de routeurs seul</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <circle cx="100" cy="170" r="33" fill="#172e49" stroke="#60a5fa" stroke-width="2"/><text x="100" y="176" fill="#dbeafe" font-size="17" font-weight="700">R1</text>
    <circle cx="390" cy="95" r="33" fill="#172e49" stroke="#60a5fa" stroke-width="2"/><text x="390" y="101" fill="#dbeafe" font-size="17" font-weight="700">R2</text>
    <circle cx="390" cy="250" r="33" fill="#172e49" stroke="#60a5fa" stroke-width="2"/><text x="390" y="256" fill="#dbeafe" font-size="17" font-weight="700">R3</text>
    <circle cx="690" cy="170" r="33" fill="#183329" stroke="#34d399" stroke-width="2"/><text x="690" y="176" fill="#d1fae5" font-size="17" font-weight="700">R4</text>
    <path d="M132 160 L357 105" stroke="#60a5fa" stroke-width="3"/><path d="M132 181 L357 240" stroke="#94a3b8" stroke-width="3"/><path d="M423 105 L658 160" stroke="#60a5fa" stroke-width="3"/><path d="M423 240 L658 181" stroke="#94a3b8" stroke-width="3"/>
    <text x="245" y="119" fill="#93c5fd" font-size="14" font-weight="700">10</text><text x="245" y="229" fill="#cbd5e1" font-size="14" font-weight="700">15</text><text x="540" y="119" fill="#93c5fd" font-size="14" font-weight="700">20 → 35</text><text x="540" y="229" fill="#cbd5e1" font-size="14" font-weight="700">25</text>
    <rect x="740" y="75" width="185" height="87" rx="10" fill="#142a42" stroke="#60a5fa"/><text x="832" y="100" fill="#93c5fd" font-size="13" font-weight="700">Avant</text><text x="832" y="124" fill="#e2e8f0" font-size="13">via R2 = 30</text><text x="832" y="145" fill="#e2e8f0" font-size="13">via R3 = 40</text>
    <rect x="740" y="190" width="185" height="87" rx="10" fill="#183329" stroke="#34d399"/><text x="832" y="215" fill="#6ee7b7" font-size="13" font-weight="700">Après changement</text><text x="832" y="239" fill="#e2e8f0" font-size="13">via R2 = 45</text><text x="832" y="260" fill="#d1fae5" font-size="13" font-weight="700">via R3 = 40</text>
    <text x="480" y="319" fill="#94a3b8" font-size="12">Le résultat concerne la topologie et le niveau de routage considérés.</text>
  </g>
</svg>

### 4.4 Métrique par interface et par niveau

Sur certaines versions Cisco IOS/IOS XE, une commande comme `isis metric 20 level-2` peut appliquer une métrique spécifique au niveau indiqué. Vérifiez la syntaxe de votre version avant de l'utiliser. Un lien de transit peut avoir une préférence différente en L1 et en L2, mais cette souplesse doit être documentée : des valeurs incohérentes compliquent les diagnostics et peuvent produire des chemins inattendus.

Exemple conceptuel, à adapter et vérifier dans l'aide de l'équipement :

```text
interface GigabitEthernet0/0
 isis metric 20 level-2
```

Après modification, comparez les métriques annoncées dans la LSDB et le prochain saut choisi par la RIB. Ne vous contentez pas de lire la configuration : vérifiez que l'information est réellement diffusée et que le calcul produit l'effet voulu.

### 4.5 Coût, bande passante et politique

Une valeur faible indique généralement une préférence plus forte lorsqu'on compare des chemins par la même métrique. Cela ne signifie pas que le trafic empruntera automatiquement le lien physiquement le plus rapide. Si vous voulez exprimer une préférence de capacité, vous devez concevoir et documenter une politique de métrique appropriée, en tenant compte des chemins de secours et des objectifs d'ingénierie de trafic.


## 5. DIS et pseudonœud sur les réseaux broadcast

### 5.1 Pourquoi élire un DIS ?

Sur un réseau broadcast multi-accès, comme un segment Ethernet partagé par plusieurs routeurs IS-IS, le **Designated Intermediate System (DIS)** joue un rôle particulier dans la représentation et la synchronisation de ce segment. Il est élu par niveau. Il contribue à réduire la complexité de la description de la connectivité du LAN en utilisant un **pseudonœud** : un identifiant logique pour représenter le segment partagé dans la topologie.

Le pseudonœud n'est pas un routeur physique supplémentaire. Il ne transfère pas de paquets et ne remplace pas le DIS. Il s'agit d'une représentation topologique décrite au moyen d'un LSP de pseudonœud, permettant de modéliser la relation entre le segment et les systèmes qui y sont attachés.

### 5.2 Élection et conséquences opérationnelles

Le DIS est choisi selon les règles de priorité et de départage prévues par le protocole et l'implémentation. Une priorité configurée plus élevée est généralement favorisée ; en cas d'égalité, d'autres règles comme l'identifiant de système interviennent. Contrairement au DR d'OSPF, le DIS IS-IS peut être préempté par un routeur nouvellement arrivé qui gagne l'élection, selon les règles de protocole. Ne transposez donc pas automatiquement vos réflexes OSPF à IS-IS.

Le DIS peut changer sans que le réseau soit entièrement en panne. Toutefois, il faut vérifier que l'élection, le pseudonœud et la base d'état de liens se stabilisent correctement si des changements fréquents apparaissent.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 330" role="img" aria-labelledby="isis-dis-title isis-dis-desc">
  <title id="isis-dis-title">DIS et pseudonœud dans un LAN Ethernet</title>
  <desc id="isis-dis-desc">Trois routeurs sont connectés au même LAN. R2 est élu DIS. Un pseudonœud logique représente le segment partagé dans la topologie ; il n'est pas un routeur physique.</desc>
  <rect width="960" height="330" rx="18" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" font-size="21" font-family="Arial,sans-serif" fill="#f8fafc" font-weight="700">Réseau broadcast : DIS et pseudonœud</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="85" y="80" width="790" height="55" rx="14" fill="#172435" stroke="#64748b" stroke-width="1.5"/><text x="480" y="113" fill="#e2e8f0" font-size="16" font-weight="700">Segment Ethernet partagé</text>
    <path d="M210 135 V166 M480 135 V166 M750 135 V166" stroke="#94a3b8" stroke-width="2.5"/>
    <rect x="145" y="166" width="130" height="62" rx="10" fill="#142a42" stroke="#60a5fa"/><text x="210" y="190" fill="#dbeafe" font-size="16" font-weight="700">R1</text><text x="210" y="210" fill="#93c5fd" font-size="12">Voisin IS-IS</text>
    <rect x="415" y="166" width="130" height="62" rx="10" fill="#183329" stroke="#34d399" stroke-width="2"/><text x="480" y="190" fill="#d1fae5" font-size="16" font-weight="700">R2</text><text x="480" y="210" fill="#6ee7b7" font-size="12">DIS élu</text>
    <rect x="685" y="166" width="130" height="62" rx="10" fill="#142a42" stroke="#60a5fa"/><text x="750" y="190" fill="#dbeafe" font-size="16" font-weight="700">R3</text><text x="750" y="210" fill="#93c5fd" font-size="12">Voisin IS-IS</text>
    <path d="M210 228 V250 H480 V270 M480 228 V270 M750 228 V250 H480" stroke="#34d399" stroke-width="2.5" fill="none"/>
    <rect x="350" y="270" width="260" height="42" rx="9" fill="#203126" stroke="#34d399"/><text x="480" y="296" fill="#bbf7d0" font-size="14" font-weight="700">Pseudonœud logique du LAN</text>
  </g>
</svg>

### 5.3 À vérifier sur un LAN

- L'interface est-elle bien vue comme broadcast, ou a-t-elle été configurée en point-à-point ?
- Le voisinage est-il établi sur le niveau concerné ?
- Quel routeur est DIS en L1 et en L2, le cas échéant ?
- Le LSP de pseudonœud apparaît-il dans la LSDB ?
- Une élection fréquente correspond-elle à des changements physiques, à une priorité modifiée ou à un autre problème de stabilité ?

Dans un laboratoire avec deux routeurs directement connectés sur une interface Ethernet, le comportement peut changer si le lien est explicitement configuré comme point-à-point. Ne cherchez alors pas à imposer un DIS : il n'y a pas de LAN multi-accès à représenter de la même façon.


## 6. L1/L2, routes inter-aires et route leaking

### 6.1 La vue L1/L2

Un routeur L1/L2 maintient la vue de son aire au niveau 1 et la vue de l'ossature au niveau 2. Cela ne signifie pas que chaque détail de chaque aire est automatiquement placé dans chaque LSDB L1. Les bases sont distinctes. Le rôle du routeur frontière est de fournir la connectivité inter-aires selon les règles d'annonce et de sélection du protocole.

Sans autre politique, un routeur L1 qui cherche une destination extérieure à son aire peut avoir besoin d'utiliser une route par défaut ou un chemin vers un routeur L1/L2. Cette stratégie réduit les détails nécessaires aux routeurs de bord d'accès, mais peut parfois amener un trafic à sortir par un routeur L1/L2 qui n'est pas le meilleur point de sortie global.

### 6.2 Route leaking : principe, pas simple redistribution

Le **route leaking** permet, selon les extensions et les capacités de l'implémentation, de rendre certaines informations de routage du niveau 2 visibles au niveau 1. Un routeur L1 peut alors comparer des destinations inter-aires plus précises au lieu de seulement suivre une route par défaut ou de choisir un point de sortie peu optimal.

Le leaking ne doit pas être confondu avec une redistribution arbitraire entre deux protocoles différents. Il s'agit d'un mécanisme de diffusion contrôlée entre niveaux IS-IS, avec des règles de marquage qui empêchent qu'une route fuité soit réannoncée sans discernement et crée une boucle. L'implémentation, la syntaxe et les filtres exacts dépendent de la plateforme et des TLV de métrique utilisés.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 340" role="img" aria-labelledby="isis-leak-title isis-leak-desc">
  <title id="isis-leak-title">Pourquoi utiliser le route leaking</title>
  <desc id="isis-leak-desc">Deux sorties L1/L2 relient une aire L1 à l'ossature L2. Sans route précise, un routeur L1 peut choisir la sortie la plus proche dans son aire, même si une autre sortie est meilleure vers la destination. Le leaking sélectionné peut apporter une meilleure information inter-aire.</desc>
  <rect width="960" height="340" rx="18" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" fill="#f8fafc" font-size="21" font-family="Arial,sans-serif" font-weight="700">Route leaking : rendre le choix inter-aire plus précis</text>
  <rect x="35" y="65" width="365" height="225" rx="16" fill="#14263b" stroke="#60a5fa"/><text x="217" y="91" text-anchor="middle" fill="#93c5fd" font-size="16" font-weight="700">Aire L1</text>
  <rect x="560" y="65" width="365" height="225" rx="16" fill="#1b2d2b" stroke="#34d399"/><text x="742" y="91" text-anchor="middle" fill="#6ee7b7" font-size="16" font-weight="700">Domaine L2</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <rect x="75" y="145" width="105" height="56" rx="9" fill="#1d3553" stroke="#93c5fd"/><text x="127" y="169" fill="#f8fafc" font-size="14" font-weight="700">R1</text><text x="127" y="186" fill="#bfdbfe" font-size="11">Routeur L1</text>
    <rect x="265" y="112" width="105" height="56" rx="9" fill="#263b3c" stroke="#6ee7b7"/><text x="317" y="136" fill="#f8fafc" font-size="14" font-weight="700">R2</text><text x="317" y="153" fill="#a7f3d0" font-size="11">L1/L2</text>
    <rect x="265" y="215" width="105" height="56" rx="9" fill="#263b3c" stroke="#6ee7b7"/><text x="317" y="239" fill="#f8fafc" font-size="14" font-weight="700">R3</text><text x="317" y="256" fill="#a7f3d0" font-size="11">L1/L2</text>
    <rect x="620" y="135" width="115" height="60" rx="9" fill="#15372e" stroke="#34d399"/><text x="677" y="160" fill="#d1fae5" font-size="14" font-weight="700">R4</text><text x="677" y="178" fill="#a7f3d0" font-size="11">Destination proche</text>
    <rect x="790" y="135" width="105" height="60" rx="9" fill="#15372e" stroke="#34d399"/><text x="842" y="160" fill="#d1fae5" font-size="14" font-weight="700">R5</text><text x="842" y="178" fill="#a7f3d0" font-size="11">Autre sortie</text>
    <path d="M180 159 L259 140" stroke="#fbbf24" stroke-width="3"/><path d="M180 178 L259 241" stroke="#94a3b8" stroke-width="3"/><path d="M370 140 L615 160" stroke="#34d399" stroke-width="3"/><path d="M370 241 L785 180" stroke="#34d399" stroke-width="3"/>
    <text x="475" y="115" fill="#fcd34d" font-size="12">Sortie la plus proche</text><text x="475" y="239" fill="#a7f3d0" font-size="12">Peut-être meilleur chemin total</text>
    <text x="480" y="317" fill="#cbd5e1" font-size="12">Le leaking apporte de l'information plus précise, mais doit être filtré et contrôlé.</text>
  </g>
</svg>

### 6.3 Ce qu'il faut décider avant de l'activer

1. Quels préfixes ont besoin d'être connus au niveau 1 ? Évitez de fuiter inutilement toute la table L2.
2. Quel problème corrige-t-on : une sortie sous-optimale, la visibilité de loopbacks ou un besoin de routage précis ?
3. Les filtres et marqueurs de route empêchent-ils les annonces de retour non désirées ?
4. Tous les routeurs concernés prennent-ils en charge la même famille de TLV / le même style de métrique ?
5. Comment mesurer le résultat : route installée, prochain saut, chemin aller et chemin retour ?

Les commandes héritées trouvées sur d'anciennes versions IOS peuvent être différentes des syntaxes modernes. Pour un cours intermédiaire, sachez expliquer le mécanisme et lire le résultat avant de mémoriser une commande qui peut ne pas exister sur votre plateforme.


## 7. Extensions IPv4/IPv6 et informations transportées

IS-IS a été conçu avec des TLV extensibles. Cette structure permet d'annoncer plusieurs familles de protocoles et d'ajouter des capacités sans changer toute la logique du protocole. Integrated IS-IS annonce notamment les préfixes IPv4 via les TLV appropriés ; IPv6 utilise des extensions définies dans les standards, dont RFC 5308, ainsi que le mécanisme de métriques étendues.

Points pratiques :

- La participation d'une interface à IS-IS ne remplace pas la configuration d'adresses IP sur cette interface.
- Il faut distinguer « adjacency IS-IS formée » de « préfixe IPv4 ou IPv6 annoncé ».
- Une route IPv4 présente ne prouve pas que la reachability IPv6 a été activée et annoncée.
- Les modes IPv6 *single-topology* et *multi-topology* ont des contraintes de compatibilité ; ils doivent être planifiés sur l'ensemble du niveau concerné.
- Les commandes pour activer IPv6, régler sa métrique et choisir le mode varient selon l'OS et la version.

Dans un environnement dual-stack, vérifiez les deux familles séparément : voisins, base de données, préfixes annoncés, RIB et tests de bout en bout IPv4 puis IPv6.


## 8. Interfaces passives et portée des annonces

Une interface **passive** est utilisée, selon l'implémentation, pour annoncer le préfixe associé sans établir de voisinage IS-IS sur ce lien. C'est utile pour des interfaces de loopback ou des LAN utilisateurs où il n'y a pas de routeur IS-IS à découvrir. Elle permet d'annoncer un réseau connecté tout en évitant d'envoyer des Hello sur une interface orientée vers des terminaux.

La sémantique exacte de la commande `passive-interface` dépend du système et de la configuration IS-IS utilisée. Il faut vérifier ce qui est annoncé dans la LSDB : ne supposez pas que l'interface est simplement « désactivée » ou que son préfixe est automatiquement inclus dans tous les niveaux.

### Bonnes pratiques

- Déclarer explicitement les interfaces de transit qui doivent former des adjacencies.
- Rendre passives les interfaces d'extrémité lorsque le design prévoit d'annoncer leurs préfixes sans voisinage IS-IS local.
- Contrôler la portée de niveau pour chaque préfixe.
- Ne pas activer des adjacencies sur des réseaux d'accès sans raison opérationnelle claire.


## 9. Laboratoire guidé : quatre routeurs, deux chemins

### 9.1 Topologie et plan d'adressage

Le laboratoire utilise quatre routeurs dans une seule aire de niveau 2 afin de mettre l'accent sur le flooding, les métriques et la sélection de chemin. Toutes les interfaces de transit sont point-à-point dans cet exemple conceptuel ; adaptez les noms de ports à votre équipement ou simulateur. Les adresses sont des exemples de documentation/lab et ne doivent pas être copiées dans un réseau de production sans plan d'adressage.

```text
               coût 10              coût 20
        R1 ------------- R2 ---------------- R4
         \                                      /
          \ coût 15                  coût 25  /
           --------------- R3 ----------------

Loopback de test sur R4 : 10.44.44.4/32
```

| Lien | Raccordement | IPv4 côté A | IPv4 côté B | Coût L2 visé |
|---|---|---|---|---:|
| R1–R2 | G0/0 ↔ G0/0 | 10.0.12.1/30 | 10.0.12.2/30 | 10 |
| R1–R3 | G0/1 ↔ G0/0 | 10.0.13.1/30 | 10.0.13.2/30 | 15 |
| R2–R4 | G0/1 ↔ G0/0 | 10.0.24.1/30 | 10.0.24.2/30 | 20 |
| R3–R4 | G0/1 ↔ G0/1 | 10.0.34.1/30 | 10.0.34.2/30 | 25 |

NET suggérés :

| Routeur | NET | System ID |
|---|---|---|
| R1 | `49.0002.0000.0000.0001.00` | `0000.0000.0001` |
| R2 | `49.0002.0000.0000.0002.00` | `0000.0000.0002` |
| R3 | `49.0002.0000.0000.0003.00` | `0000.0000.0003` |
| R4 | `49.0002.0000.0000.0004.00` | `0000.0000.0004` |

Les System ID doivent être uniques dans le domaine concerné. Le NET inclut l'aire `49.0002` et se termine par NSEL `00`.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="isis-lab-title isis-lab-desc">
  <title id="isis-lab-title">Topologie du laboratoire IS-IS avec quatre routeurs</title>
  <desc id="isis-lab-desc">R1 est relié à R2 par un lien de coût 10 et à R3 par un lien de coût 15. R2 est relié à R4 par un lien de coût 20 et R3 à R4 par un lien de coût 25. Le coût total est 30 via R2 et 40 via R3.</desc>
  <rect width="960" height="360" rx="18" fill="#0b1220"/><text x="480" y="34" text-anchor="middle" font-size="21" fill="#f8fafc" font-family="Arial,sans-serif" font-weight="700">Laboratoire : route de coût minimal</text>
  <g font-family="Arial,sans-serif" text-anchor="middle">
    <circle cx="130" cy="180" r="40" fill="#142a42" stroke="#60a5fa" stroke-width="2"/><text x="130" y="186" fill="#dbeafe" font-size="19" font-weight="700">R1</text>
    <circle cx="410" cy="95" r="40" fill="#142a42" stroke="#60a5fa" stroke-width="2"/><text x="410" y="101" fill="#dbeafe" font-size="19" font-weight="700">R2</text>
    <circle cx="410" cy="265" r="40" fill="#142a42" stroke="#60a5fa" stroke-width="2"/><text x="410" y="271" fill="#dbeafe" font-size="19" font-weight="700">R3</text>
    <circle cx="720" cy="180" r="40" fill="#183329" stroke="#34d399" stroke-width="2"/><text x="720" y="186" fill="#d1fae5" font-size="19" font-weight="700">R4</text>
    <path d="M166 164 L374 108" stroke="#60a5fa" stroke-width="4"/><path d="M166 196 L374 252" stroke="#94a3b8" stroke-width="3"/><path d="M446 108 L684 164" stroke="#60a5fa" stroke-width="4"/><path d="M446 252 L684 196" stroke="#94a3b8" stroke-width="3"/>
    <text x="265" y="120" fill="#93c5fd" font-size="14" font-weight="700">10.0.12.0/30 · 10</text><text x="265" y="244" fill="#cbd5e1" font-size="14" font-weight="700">10.0.13.0/30 · 15</text><text x="565" y="120" fill="#93c5fd" font-size="14" font-weight="700">10.0.24.0/30 · 20</text><text x="565" y="244" fill="#cbd5e1" font-size="14" font-weight="700">10.0.34.0/30 · 25</text>
    <rect x="790" y="91" width="140" height="56" rx="9" fill="#15372e" stroke="#34d399"/><text x="860" y="113" fill="#d1fae5" font-size="12" font-weight="700">Loopback R4</text><text x="860" y="132" fill="#e2e8f0" font-size="12">10.44.44.4/32</text><path d="M755 165 L790 140" stroke="#34d399" stroke-width="2.5"/>
    <text x="480" y="325" fill="#93c5fd" font-size="14" font-weight="700">Chemin via R2 = 30</text><text x="480" y="345" fill="#cbd5e1" font-size="13">Chemin via R3 = 40 — le chemin via R2 doit être préféré.</text>
  </g>
</svg>

### 9.2 Configuration type pour R1

L'exemple illustre un style de configuration Cisco IOS courant. Les commandes d'interface et le processus exact peuvent varier ; vérifiez la syntaxe disponible sur votre image IOS/IOS XE ou simulateur.

```text
configure terminal
!
router isis CORE
 net 49.0002.0000.0000.0001.00
 is-type level-2-only
 metric-style wide
!
interface GigabitEthernet0/0
 description Vers-R2
 ip address 10.0.12.1 255.255.255.252
 ip router isis CORE
 isis network point-to-point
 isis metric 10 level-2
 no shutdown
!
interface GigabitEthernet0/1
 description Vers-R3
 ip address 10.0.13.1 255.255.255.252
 ip router isis CORE
 isis network point-to-point
 isis metric 15 level-2
 no shutdown
end
```

R2, R3 et R4 doivent être configurés de façon cohérente, avec leurs NET uniques, leurs propres adresses, le processus IS-IS appliqué aux interfaces de transit, la même intention de niveau et les métriques prévues. La configuration d'une loopback sur R4 doit aussi être annoncée selon les commandes prises en charge par la plateforme, souvent via une interface logique et une configuration passive ou un mécanisme d'annonce équivalent. Ne supposez pas que l'adresse de loopback apparaît automatiquement dans IS-IS sans vérifier la LSDB.

### 9.3 Ordre de vérification

Après activation, exécutez les contrôles et notez les résultats avant de changer les métriques :

```text
show isis neighbors
show isis database
show isis database detail
show ip route isis
show ip route 10.44.44.4
show interfaces
```

Sur certaines plateformes, les commandes peuvent être `show clns neighbors`, `show isis neighbors detail` ou avoir des variantes selon le système. Utilisez `show ?` et `show isis ?` pour connaître les formes acceptées.

Checklist du résultat attendu :

- R1 voit R2 et R3 au niveau 2 ;
- R2 et R3 voient R4 au niveau 2 ;
- la LSDB L2 contient les informations des routeurs et les préfixes attendus ;
- R1 connaît `10.44.44.4/32` ;
- la route utilise normalement le premier saut vers R2 avec les coûts donnés ;
- un ping vers la loopback fonctionne, et le chemin retour est également valide.

### 9.4 Expérience : changer le coût

Modifiez la métrique L2 de R2–R4 de 20 à 35, en veillant à appliquer le changement à l'interface adaptée sur R2 ou R4 selon la plateforme et à ne pas modifier par inadvertance les autres niveaux. Le coût par R2 devrait alors devenir 45, tandis que le chemin par R3 reste 40. Après propagation du nouveau LSP et recalcul, R1 devrait préférer la voie R3 pour atteindre la loopback de R4.

Observez successivement :

1. la configuration locale de la métrique ;
2. le nouveau coût annoncé dans la LSDB ;
3. la route retenue et son prochain saut ;
4. la connectivité avant et après le changement ;
5. le temps de convergence observé dans ce laboratoire.

Cette expérience permet de séparer la modification de configuration, le flooding du LSP, le calcul SPF et l'installation de la route. La convergence réelle dépend de plusieurs timers, de la charge du routeur et de l'implémentation.


## 10. Commandes de contrôle : question, commande, interprétation

| Question | Commande type Cisco | Ce qu'il faut chercher |
|---|---|---|
| Quels voisins sont établis ? | `show isis neighbors` | État, interface, type de circuit, niveau et durée de voisinage selon la sortie. |
| Quels LSP sont dans la base ? | `show isis database` | Identifiants LSP, fragments, numéros de séquence, durées de vie. |
| Que contient un LSP ? | `show isis database detail` | Préfixes annoncés, voisins, métriques, niveau et indicateurs disponibles. |
| IS-IS a-t-il appris la route ? | `show ip route isis` | Route installée, type L1/L2/IA selon la plateforme, métrique et prochain saut. |
| Quel chemin vers une destination ? | `show ip route <préfixe>` | La route active et le ou les next-hops retenus. |
| Quelles métriques sont appliquées ? | `show running-config` / commande d'interface | Configuration réelle, sans oublier de vérifier la métrique diffusée dans la LSDB. |
| Y a-t-il des événements ? | `show logging` | Voisinages qui montent/descendent, changements de configuration, erreurs et horodatages. |

Ne traitez pas ces commandes comme une interface universelle : les plateformes Juniper, Nokia, Arista et les systèmes Linux ont d'autres syntaxes. Le raisonnement de fond demeure néanmoins le même : voisinage → LSDB → calcul/route → transfert.


## 11. Dépannage intermédiaire par symptômes

### Symptôme A — un voisin est absent

1. Vérifiez que l'interface physique et le protocole de couche liaison sont actifs.
2. Confirmez que le processus IS-IS est appliqué à la bonne interface.
3. Comparez le niveau autorisé globalement et celui du circuit.
4. Pour L1, vérifiez la compatibilité des adresses d'aire ; ne demandez pas une adjacency L1 si les aires sont incompatibles.
5. Comparez authentification, type de réseau et journaux sur les deux extrémités.
6. Examinez les compteurs, les pertes et les erreurs de couche liaison.

**Évitez :** changer les métriques pour tenter de réparer une adjacency. La métrique influence le coût du chemin, pas la compatibilité fondamentale du voisinage.

### Symptôme B — voisin `Up`, préfixe absent de la LSDB

- Le préfixe est-il réellement connecté ou présent dans la table locale ?
- L'interface qui porte ce préfixe est-elle annoncée dans IS-IS, ou rendue passive selon le design ?
- Le préfixe appartient-il à la bonne famille IP ?
- Est-il annoncé au bon niveau ?
- Les informations nécessaires apparaissent-elles dans le LSP originaire, ou ont-elles été filtrées par une fonction de la plateforme ?

Si le préfixe n'apparaît même pas dans le LSP du routeur qui devrait l'annoncer, concentrez-vous sur l'annonce locale. Si le LSP est correct localement mais absent ailleurs, regardez plutôt le flooding, les adjacencies et la synchronisation.

### Symptôme C — le préfixe est dans la LSDB mais pas dans la RIB

Les causes possibles comprennent une route plus préférée d'un autre protocole, un préfixe non installable, une politique, une métrique ou une portée de niveau inattendue. Vérifiez d'abord si le préfixe est admissible dans le calcul de la topologie concernée, puis comparez la route candidate et la route installée. Une route n'est pas « manquante » simplement parce qu'elle n'est pas la route active.

### Symptôme D — mauvais chemin / sortie sous-optimale

1. Écrivez les chemins possibles et additionnez leurs métriques annoncées.
2. Vérifiez le niveau utilisé : comparer une métrique L1 avec une métrique L2 sans tenir compte de la hiérarchie peut conduire à une conclusion fausse.
3. Contrôlez les annonces inter-aires, la route par défaut et le route leaking éventuel.
4. Recherchez une différence entre la configuration de métrique et la métrique réellement diffusée.
5. Après correction, confirmez le next-hop de la RIB et testez le flux dans les deux sens.

### Symptôme E — le voisinage monte puis tombe

Consultez l'heure des transitions et corrélez-les avec les changements d'interface, les erreurs physiques, les CPU élevés, les pertes, les timers et les journaux d'authentification. Une minuterie trop agressive peut amplifier des pertes brèves ; elle ne doit toutefois pas servir de solution de contournement à une liaison défectueuse. Collectez des preuves avant de modifier les paramètres.

### Symptôme F — IPv4 fonctionne, IPv6 non

Ne concluez pas que le protocole entier est en panne. Vérifiez les adresses IPv6 des interfaces, l'activation de la famille IPv6 dans IS-IS, les TLV annoncés, le mode single/multi-topology et la RIB IPv6. Exécutez des commandes de vérification IPv6 dédiées à la plateforme. La présence d'un voisinage IS-IS commun ne garantit pas que chaque famille IP soit correctement annoncée.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="isis-triage-title isis-triage-desc">
  <title id="isis-triage-title">Matrice de dépannage IS-IS</title>
  <desc id="isis-triage-desc">Un tableau relie quatre symptômes à la zone de contrôle prioritaire : adjacency, LSDB, RIB et transfert. Les contrôles sont progressifs.</desc>
  <rect width="960" height="360" rx="18" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" font-size="21" fill="#f8fafc" font-family="Arial,sans-serif" font-weight="700">Choisir le bon niveau de dépannage</text>
  <g font-family="Arial,sans-serif" font-size="13">
    <rect x="40" y="60" width="880" height="44" rx="8" fill="#172435"/><text x="58" y="87" fill="#cbd5e1" font-weight="700">Symptôme</text><text x="305" y="87" fill="#cbd5e1" font-weight="700">Première vérification</text><text x="650" y="87" fill="#cbd5e1" font-weight="700">Suite logique</text>
    <rect x="40" y="112" width="880" height="48" rx="8" fill="#142a42" stroke="#315274"/><text x="58" y="141" fill="#dbeafe">Voisin absent</text><text x="305" y="141" fill="#e2e8f0">Interface, niveau, aire</text><text x="650" y="141" fill="#cbd5e1">Type de circuit, auth., logs</text>
    <rect x="40" y="168" width="880" height="48" rx="8" fill="#142c36" stroke="#155e75"/><text x="58" y="197" fill="#cffafe">Préfixe absent de la LSDB</text><text x="305" y="197" fill="#e2e8f0">LSP source / annonce locale</text><text x="650" y="197" fill="#cbd5e1">Niveau, flooding, filtres</text>
    <rect x="40" y="224" width="880" height="48" rx="8" fill="#203126" stroke="#276749"/><text x="58" y="253" fill="#d1fae5">LSDB OK, route absente</text><text x="305" y="253" fill="#e2e8f0">RIB et niveau de routage</text><text x="650" y="253" fill="#cbd5e1">Sélection, politique, métrique</text>
    <rect x="40" y="280" width="880" height="48" rx="8" fill="#342b1b" stroke="#92400e"/><text x="58" y="309" fill="#fef3c7">Route OK, trafic échoue</text><text x="305" y="309" fill="#e2e8f0">Next-hop, interface, voisins IP</text><text x="650" y="309" fill="#cbd5e1">ACL, MTU, retour, test applicatif</text>
  </g>
</svg>


## 12. Sécurité et stabilité de conception

IS-IS étant un protocole de routage interne, ses PDU influencent directement les chemins. Une configuration négligée peut provoquer des annonces indésirables, des instabilités ou des routes sous-optimales. Les mécanismes disponibles sont spécifiques à l'implémentation ; intégrez la sécurité au plan de conception plutôt que d'ajouter des paramètres sans vérifier leur portée.

- **Authentification des PDU** : lorsqu'elle est prise en charge et prévue par la politique, configurez une méthode cohérente à la bonne portée et testez les transitions de clé conformément aux procédures de votre organisation.
- **Contrôle de l'annonce** : limitez les interfaces participantes, utilisez les interfaces passives de manière réfléchie et évitez de créer des adjacencies avec des équipements qui ne doivent pas faire partie du domaine.
- **Métriques documentées** : tenez un plan de métrique qui explique la préférence de chaque chemin et les routes de secours.
- **Changements progressifs** : modifiez une variable à la fois, conservez une configuration de retour arrière et comparez la LSDB ainsi que la table de routage avant/après.
- **Surveillance** : journalisez les transitions de voisins, surveillez la stabilité de la LSDB et testez les chemins principaux comme les chemins de secours.
- **Éviter les hypothèses de version** : une commande disponible dans une ancienne version ou un guide d'une autre gamme peut se comporter différemment sur votre équipement.

L'authentification ne remplace pas la segmentation administrative, le contrôle d'accès à la gestion ni la sécurisation globale des routeurs.


## 13. Bonnes pratiques avant mise en production

### Avant le déploiement

- Établir un plan d'adressage IP, un plan NET et des System ID uniques.
- Définir clairement la portée L1/L2 et vérifier la continuité de l'ossature L2.
- Choisir un style de métrique cohérent, généralement wide pour un nouveau déploiement compatible.
- Définir les interfaces de transit et celles qui doivent être passives.
- Déterminer les besoins IPv4/IPv6 et le mode de topologie compatible.
- Préparer les commandes de validation et le plan de retour arrière.

### Après le déploiement

- Confirmer les adjacencies attendues sur chaque lien.
- Comparer les LSDB à un autre routeur du même niveau, si nécessaire.
- Vérifier qu'aucun préfixe important n'est absent ou annoncé dans une portée inattendue.
- Vérifier les routes installées, les métriques et les next-hops.
- Tester ping/traceroute et le chemin retour, avec une destination représentative.
- Déclencher une panne contrôlée en laboratoire afin de vérifier la convergence et le chemin de secours.

### Lors d'une modification

Sauvegardez la configuration ; documentez l'état attendu ; faites un changement isolé ; observez les voisins ; observez les LSP ; contrôlez la RIB et enfin le trafic. Si le résultat s'écarte de l'attendu, revenez au dernier état connu et analysez les données collectées plutôt que d'empiler des corrections.


## 14. Exercices d'application

### Exercice 1 — niveau incompatible

R1 est configuré globalement en L1/L2. Son interface vers R2 est réglée L1 uniquement. R2 est L1/L2 et son interface correspondante est L2 uniquement. La connectivité IP de l'interface fonctionne, mais il n'existe pas de voisinage IS-IS sur ce lien.

**Question :** quelle est la première piste à vérifier ?

**Correction :** comparez le niveau autorisé sur les deux interfaces. Le fait que les routeurs soient L1/L2 globalement ne signifie pas que chaque interface participe aux deux niveaux. La correction doit être cohérente avec le design de ce lien ; ne changez pas les métriques pour résoudre ce problème.

### Exercice 2 — le préfixe est dans la LSDB mais pas dans la RIB

Le LSP de R4 apparaît dans la LSDB L2 de R1 et annonce `10.44.44.4/32`. Pourtant, `show ip route 10.44.44.4` affiche une route statique.

**Question :** IS-IS est-il nécessairement en panne ?

**Correction :** non. Le préfixe peut être appris via IS-IS sans gagner la sélection de la route active. Vérifiez la préférence administrative ou la distance de la route, la configuration de route statique et la règle de sélection de la plateforme. Supprimez ou modifiez une route seulement si cela correspond au design et si l'impact est compris.

### Exercice 3 — calculer le coût

Deux chemins vers une destination : R1–R2–R4 avec des métriques 10 et 35 ; R1–R3–R4 avec 15 et 25.

**Question :** quel chemin a le coût total inférieur ?

**Correction :** via R2 : `10 + 35 = 45`. Via R3 : `15 + 25 = 40`. Pour la même topologie et le même niveau, la voie via R3 est donc préférable selon les métriques données.

### Exercice 4 — comprendre CSNP/PSNP

R1 et R2 ont une adjacency opérationnelle, mais leurs LSDB ne sont pas encore identiques.

**Question :** quel rôle jouent CSNP et PSNP ?

**Correction :** un CSNP permet de résumer la base connue ; un PSNP permet d'échanger des entrées ciblées pour demander ou acquitter des informations. Ces mécanismes contribuent à corriger les divergences et à synchroniser les LSP.

### Exercice 5 — IPv4 fonctionne, IPv6 échoue

Les voisins L2 sont actifs et le préfixe IPv4 du serveur est présent dans la LSDB. Aucun préfixe IPv6 attendu ne se trouve dans la RIB IPv6.

**Question :** quelle chaîne de vérification suivre ?

**Correction :** vérifier les adresses IPv6, l'activation IS-IS IPv6, le TLV/format annoncé, le mode single-topology ou multi-topology, la LSDB IPv6 et la RIB IPv6. Tester la famille IPv6 séparément du succès IPv4.


## 15. Quiz de validation

Répondez avant de consulter les corrections.

1. Quelle est la différence entre adjacency et LSDB ?
2. Quel rôle le numéro de séquence d'un LSP joue-t-il ?
3. Quelle est la fonction principale d'un CSNP ?
4. À quoi sert un PSNP dans la synchronisation ?
5. Pourquoi ne faut-il pas assimiler la métrique à la bande passante réelle ?
6. Deux chemins coûtent 27 et 32. Lequel est préféré si les autres conditions sont équivalentes ?
7. Un routeur est L1/L2 globalement. Peut-il avoir une interface participant seulement à L2 ?
8. Pourquoi un DIS n'est-il pas identique au DR OSPF dans tous ses comportements ?
9. Le préfixe figure dans la LSDB mais n'apparaît pas dans la RIB. Citez deux hypothèses à examiner.
10. Pourquoi contrôler la FIB et le trafic après avoir vérifié la RIB ?
11. Quel problème le route leaking peut-il aider à résoudre ?
12. Quelles vérifications sont nécessaires lorsque IPv4 fonctionne mais IPv6 échoue ?

### Corrections

1. L'adjacency décrit le voisinage établi sur un lien ; la LSDB stocke les informations d'état de liens utilisées pour reconstruire la topologie.
2. Il permet de différencier les versions d'un LSP de même identité. Ce n'est pas une métrique de coût.
3. Fournir un résumé de la base des LSP, pour permettre la comparaison et la détection des informations manquantes ou obsolètes.
4. Transporter des entrées ciblées, pouvant servir à demander des LSP manquants ou à acquitter des informations selon l'échange.
5. La métrique est une valeur de routage configurée/annoncée ; elle ne correspond à la capacité physique du lien que si la politique de conception le prévoit.
6. Le chemin coûtant 27, à conditions égales dans la même topologie/niveau.
7. Oui. Le type global du routeur et le type de circuit d'une interface sont deux paramètres distincts.
8. IS-IS et OSPF n'ont pas exactement les mêmes règles d'élection et de préemption du système désigné ; il faut connaître les règles propres à IS-IS.
9. Route plus préférée dans un autre protocole, politique ou filtre, niveau/portée inadaptés, métrique ou condition d'installation non satisfaite.
10. La RIB montre la décision de routage, mais le transfert dépend aussi du next-hop résolu, de l'interface, des règles de filtrage, de MTU et du chemin retour.
11. Rendre certains préfixes L2 plus précis visibles en L1 afin d'améliorer la sélection de sortie inter-aire ; c'est à contrôler pour ne pas multiplier inutilement les routes.
12. Adresse IPv6, activation de la famille, TLV annoncés, mode de topologie, LSDB IPv6, RIB IPv6 et test de connectivité dans les deux sens.


## 16. Aide-mémoire opérationnelle

### Ordre de diagnostic

```text
Interface et couche liaison
        ↓
Adjacency et niveau (L1/L2)
        ↓
LSDB du bon niveau : LSP, fragments, préfixes, métriques
        ↓
Calcul de chemin et route retenue dans la RIB
        ↓
Next-hop résolu et entrée de transfert
        ↓
Ping/traceroute et test applicatif, aller-retour
```

### Rappels

- **IIH** : découverte et maintien des voisins.
- **LSP** : informations d'état de liens originiées par un système.
- **CSNP** : résumé des LSP de la base.
- **PSNP** : informations partielles utilisées pour demander ou acquitter des LSP.
- **LSDB** : base d'état de liens séparée par niveau.
- **SPF** : calcul du chemin à partir de la topologie.
- **Métrique** : coût d'un lien/chemin, pas numéro de version du LSP.
- **DIS** : rôle particulier sur un réseau broadcast multi-accès ; il contribue à la représentation du segment avec un pseudonœud.
- **Route leaking** : diffusion contrôlée de certaines routes entre niveaux pour améliorer la visibilité inter-aire.
- **Wide metrics** : plage plus large et meilleure base pour les extensions modernes, sous réserve de compatibilité.


## 17. Sources et lectures complémentaires

Les explications du cours s'appuient sur les standards et la documentation constructeur suivants. Les exemples de configuration restent illustratifs et doivent être comparés à la version réellement utilisée.

- **RFC 1195 — Use of OSI IS-IS for routing in TCP/IP and dual environments** : <https://www.rfc-editor.org/rfc/rfc1195>
- **RFC 5308 — Routing IPv6 with IS-IS** : <https://www.rfc-editor.org/rfc/rfc5308>
- **Cisco — Customizing IS-IS for Your Network Design** : <https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_irs-netd-0.html>
- **Cisco — IS-IS Route Leaking Overview** : <https://www.cisco.com/c/en/us/support/docs/ip/integrated-intermediate-system-to-intermediate-system-is-is/13796-route-leak.html>

Les standards définissent le comportement du protocole ; le guide d'une version précise du système d'exploitation détermine les syntaxes et les fonctions effectivement disponibles sur l'équipement.


## Passage au niveau expert

Le niveau expert doit approfondir l'ingénierie et le comportement à grande échelle : conception multi-aires avancée, convergence et réglage des timers, contrôle de flooding, optimisation SPF/PRC, overload bit, TLV et extensions, route leaking complexe, interaction avec MPLS/Segment Routing, TE, IPv6 multi-topology, évolutivité de la LSDB et analyse de captures IS-IS. Il devra réutiliser les mécanismes expliqués ici sans répéter intégralement le niveau débutant.
