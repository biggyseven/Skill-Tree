# QoS — Niveau Débutant

> **Fichier :** `qos-debutant.md`  
> **Parcours :** Réseaux — Débutant  
> **Thème :** Quality of Service (QoS), DiffServ, DSCP, classification, files, policing et shaping  
> **Objectif :** comprendre pourquoi la QoS est nécessaire, comment elle fonctionne et comment construire une première politique simple sans dégrader le trafic.


## Objectifs pédagogiques

À la fin de ce cours, tu devrais être capable de :

- expliquer les effets de la congestion et distinguer bande passante, latence, gigue et perte ;
- décrire les fonctions de classification, marquage, policing, shaping, mise en file et ordonnancement ;
- reconnaître le champ DS de l’en-tête IP, le DSCP et les valeurs courantes comme EF, AF, CS et Default;
- différencier le marquage IP (DSCP) du marquage Ethernet 802.1Q PCP/CoS ;
- identifier la frontière de confiance et comprendre pourquoi un terminal ne doit pas nécessairement être cru ;
- lire une configuration Cisco basée sur `class-map`, `policy-map` et `service-policy` ;
- vérifier une politique avec les commandes adaptées à la plateforme et interpréter les compteurs de base ;
- construire un mini-laboratoire, tester sous congestion et diagnostiquer un problème simple.

## Prérequis

Connaître les bases d’IPv4, d’Ethernet, des commutateurs, des routeurs, des interfaces et des applications TCP/UDP. Il n’est pas nécessaire de connaître déjà les mécanismes QoS avancés : ils seront introduits progressivement.

## 1. Pourquoi la QoS existe-t-elle ?

La **Quality of Service (QoS)** est un ensemble de politiques et de mécanismes qui différencient le traitement des paquets selon les besoins du trafic. Sur un réseau peu chargé, la plupart des applications peuvent fonctionner convenablement sans traitement différencié. Lorsque plusieurs flux se disputent une interface, une file d’attente ou une capacité WAN, la QoS permet d’organiser ce partage.

La QoS ne fabrique pas de capacité supplémentaire. Elle sert à répartir plus intelligemment une ressource limitée et à contrôler certains profils de trafic. Si un lien de 10 Mbit/s reçoit durablement 18 Mbit/s de trafic, la différence ne peut pas être transmise par magie : il faut réduire les émissions, ajouter de la capacité, supprimer du trafic ou décider quel trafic recevra quel traitement.

### 1.1 Une analogie utile

Imagine une route à une seule voie de sortie. Les véhicules représentent les paquets et la voie représente le débit disponible. Quand il y a peu de véhicules, tout passe vite. Quand le trafic se densifie, une file se forme. Une ambulance peut avoir besoin d’un traitement prioritaire, les véhicules ordinaires continuent à avancer, et les poids lourds peuvent être soumis à des règles spécifiques. Mais si le volume total dépasse continuellement la capacité de la route, la file ne disparaît pas uniquement parce qu’on a donné une priorité à l’ambulance.

En réseau, la QoS peut :

- reconnaître les paquets ou les flux ;
- leur appliquer une classe de service ;
- contrôler leur débit ou leurs rafales ;
- organiser des files d’attente et l’accès au lien ;
- éviter ou gérer certaines congestions selon les capacités de l’équipement.

### Schéma 1 — Chaîne de traitement QoS

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Chaîne de traitement QoS"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Chaîne de traitement QoS</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Reconnaître, marquer, conditionner, mettre en file puis transmettre</text><rect x="22" y="136" width="132" height="102" rx="12" fill="#102c3f" stroke="#38bdf8" stroke-width="2"/><text x="88.0" y="181.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Trafic entrant</text><text x="88.0" y="201.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Voix / vidéo / data</text><rect x="178" y="136" width="132" height="102" rx="12" fill="#16284a" stroke="#818cf8" stroke-width="2"/><text x="244.0" y="181.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Classifier</text><text x="244.0" y="201.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">ACL, DSCP, ports</text><rect x="334" y="136" width="132" height="102" rx="12" fill="#123a3b" stroke="#2dd4bf" stroke-width="2"/><text x="400.0" y="181.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Marquer</text><text x="400.0" y="201.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP / CoS</text><rect x="490" y="136" width="132" height="102" rx="12" fill="#42321a" stroke="#fbbf24" stroke-width="2"/><text x="556.0" y="181.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Conditionner</text><text x="556.0" y="201.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Policer ou shaping</text><rect x="646" y="136" width="132" height="102" rx="12" fill="#3a2147" stroke="#c084fc" stroke-width="2"/><text x="712.0" y="181.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Mettre en file</text><text x="712.0" y="201.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Queues et scheduler</text><rect x="802" y="136" width="132" height="102" rx="12" fill="#123b2e" stroke="#4ade80" stroke-width="2"/><text x="868.0" y="181.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Lien sortant</text><text x="868.0" y="201.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Débit physique</text><line x1="154" y1="187" x2="174" y2="187" stroke="#94a3b8" stroke-width="3"/><polygon points="174.0,187.0 162.0,180.0 162.0,194.0" fill="#94a3b8"/><line x1="310" y1="187" x2="330" y2="187" stroke="#94a3b8" stroke-width="3"/><polygon points="330.0,187.0 318.0,180.0 318.0,194.0" fill="#94a3b8"/><line x1="466" y1="187" x2="486" y2="187" stroke="#94a3b8" stroke-width="3"/><polygon points="486.0,187.0 474.0,180.0 474.0,194.0" fill="#94a3b8"/><line x1="622" y1="187" x2="642" y2="187" stroke="#94a3b8" stroke-width="3"/><polygon points="642.0,187.0 630.0,180.0 630.0,194.0" fill="#94a3b8"/><line x1="778" y1="187" x2="798" y2="187" stroke="#94a3b8" stroke-width="3"/><polygon points="798.0,187.0 786.0,180.0 786.0,194.0" fill="#94a3b8"/><text x="480" y="280" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">La QoS agit sur le trafic et surtout quand une ressource devient disputée.</text><text x="480" y="309" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" text-anchor="middle">Elle ne crée pas de bande passante physique supplémentaire.</text></svg>


### 1.2 La QoS n’est pas un outil qui accélère tout

La QoS est surtout utile lorsqu’une ressource devient disputée : lien WAN lent, uplink surchargé, sortie d’un routeur, liaison montante d’un commutateur ou autre ressource d’émission. Elle n’est pas une solution universelle à une panne DNS, à une boucle de routage, à un serveur surchargé ou à une mauvaise couverture Wi-Fi.

Un bon projet QoS commence donc par des mesures, une description des applications, des objectifs de performance et une localisation de la congestion. Sans ces éléments, une politique peut déplacer le problème plutôt que le résoudre.

## 2. Les métriques essentielles

### 2.1 Bande passante et débit utile

La **bande passante** d’un lien désigne sa capacité de transmission nominale, généralement exprimée en kbit/s, Mbit/s ou Gbit/s. Le **débit utile** correspond au trafic effectivement transporté, après prise en compte des protocoles, des retransmissions et des autres limites du système. Un lien Gigabit Ethernet ne garantit pas qu’une application obtiendra 1 Gbit/s de débit utile de bout en bout.

Il est important de distinguer :

- **capacité nominale** : vitesse annoncée de l’interface ou du service ;
- **débit mesuré** : quantité de données transférée pendant une durée ;
- **débit disponible** : capacité résiduelle sur un chemin à un instant donné ;
- **débit engagé** : valeur contractualisée dans un service, lorsqu’un contrat de ce type existe.

### 2.2 Latence

La latence est le temps nécessaire pour qu’un paquet ou une information traverse le chemin mesuré. On parle de délai aller simple lorsqu’un sens précis est mesuré et de RTT (*Round-Trip Time*) lorsqu’on mesure l’aller-retour. Un ping fournit généralement une mesure d’aller-retour, pas automatiquement une mesure d’aller simple.

La latence se compose notamment du délai de propagation, du temps de sérialisation, du traitement des équipements, et du temps passé dans les files. La QoS agit surtout sur le traitement et l’attente dans les files ; elle ne peut pas raccourcir la distance physique entre deux continents.

### 2.3 Gigue

La **gigue** décrit la variation du délai d’arrivée des paquets. La voix et la vidéo interactive sont sensibles à ces variations. Un mécanisme de tampon de gigue côté application peut absorber une partie des variations, au prix d’un délai supplémentaire. Une gigue faible est souhaitable, mais la mesure exacte dépend de la méthode de calcul.

### 2.4 Perte de paquets

Une perte se produit lorsqu’un paquet n’atteint pas sa destination ou est éliminé en chemin. Les causes comprennent les files pleines, les erreurs physiques, les politiques de filtrage, les pannes de lien et les problèmes d’acheminement. Une perte peut provoquer des retransmissions TCP, réduire le débit utile ou dégrader fortement une application temps réel qui ne retransmet pas ses paquets à temps.

### Schéma 2 — Les quatre dimensions

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Les quatre dimensions à surveiller"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Les quatre dimensions à surveiller</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Capacité, latence, gigue et perte ne décrivent pas la même chose</text><rect x="35" y="120" width="205" height="150" rx="14" fill="#101f33" stroke="#1d4ed8" stroke-width="2"/><text x="137" y="158" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" text-anchor="middle">Bande passante</text><text x="137" y="195" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Capacité du lien</text><text x="137" y="228" fill="#a7f3d0" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" text-anchor="middle">Mbit/s ou Gbit/s</text><rect x="265" y="120" width="205" height="150" rx="14" fill="#101f33" stroke="#0f766e" stroke-width="2"/><text x="367" y="158" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" text-anchor="middle">Latence</text><text x="367" y="195" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Temps aller ou aller-retour</text><text x="367" y="228" fill="#a7f3d0" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" text-anchor="middle">ms</text><rect x="495" y="120" width="205" height="150" rx="14" fill="#101f33" stroke="#7e22ce" stroke-width="2"/><text x="597" y="158" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" text-anchor="middle">Gigue</text><text x="597" y="195" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Variation de latence</text><text x="597" y="228" fill="#a7f3d0" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" text-anchor="middle">ms</text><rect x="725" y="120" width="205" height="150" rx="14" fill="#101f33" stroke="#b45309" stroke-width="2"/><text x="827" y="158" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700" text-anchor="middle">Perte</text><text x="827" y="195" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Paquets non livrés</text><text x="827" y="228" fill="#a7f3d0" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" text-anchor="middle">%</text><text x="480" y="318" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Une application sensible à la latence peut souffrir même si le débit moyen semble correct.</text></svg>


### 2.5 Exemple d’interprétation

Une application peut utiliser seulement 500 kbit/s et pourtant être inutilisable si ses paquets subissent des délais ou des pertes importants. À l’inverse, un transfert de sauvegarde peut tolérer de la latence et chercher surtout à exploiter la capacité disponible. Il est donc préférable de définir les objectifs par application plutôt que d’attribuer arbitrairement une priorité haute à tout le trafic.

| Type de trafic | Sensibilité typique | Approche initiale |
|---|---|---|
| Voix interactive | Latence, gigue et perte | Classe temps réel maîtrisée, contrôle du débit |
| Visioconférence | Latence, gigue, perte, débit | Classe dédiée selon les besoins réels |
| Transactions métier | Réactivité et fiabilité | Garantie raisonnable, congestion maîtrisée |
| Sauvegarde / transfert massif | Débit, moins sensible au délai | Partage de bande passante, limitation si nécessaire |
| Navigation et usage général | Variable | Best effort ou classes métier définies |
| Supervision réseau | Fiabilité et accès aux équipements | Traitement adapté, sans confondre avec le trafic utilisateur |

Ces associations sont des points de départ. L’application, l’architecture, le SLA et les capacités matérielles déterminent les objectifs réels.

## 3. Le principe DiffServ et le champ DS

La plupart des déploiements IP modernes s’appuient sur l’architecture **Differentiated Services (DiffServ)**. Au lieu de maintenir un état de réservation pour chaque flux sur chaque routeur, DiffServ classe les paquets en agrégats et utilise une marque dans l’en-tête IP pour indiquer le traitement attendu à chaque saut.

### 3.1 DSCP et ECN

Dans IPv4, le champ historiquement appelé ToS a été redéfini pour inclure le champ DS. Dans IPv6, un champ Traffic Class joue un rôle correspondant. Le champ DS fait 8 bits : six bits pour le **DSCP** (*Differentiated Services Code Point*) et deux bits pour **ECN** (*Explicit Congestion Notification*). DSCP permet de choisir un PHB (*Per-Hop Behavior*) selon la politique de l’équipement. ECN permet à certains chemins compatibles de signaler une congestion sans nécessairement supprimer le paquet.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="DSCP et ECN dans le champ DS"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">DSCP et ECN dans le champ DS</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Le champ DS occupe 8 bits dans l’en-tête IPv4/IPv6</text><text x="480" y="92" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="400" text-anchor="middle">Champ DS de l’en-tête IP : 8 bits</text><rect x="42" y="130" width="92" height="86" rx="8" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="88" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DSCP bit 5</text><text x="88" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="154" y="130" width="92" height="86" rx="8" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="200" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DSCP bit 4</text><text x="200" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="266" y="130" width="92" height="86" rx="8" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="312" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DSCP bit 3</text><text x="312" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="378" y="130" width="92" height="86" rx="8" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="424" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DSCP bit 2</text><text x="424" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="490" y="130" width="92" height="86" rx="8" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="536" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DSCP bit 1</text><text x="536" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="602" y="130" width="92" height="86" rx="8" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="648" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">DSCP bit 0</text><text x="648" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="714" y="130" width="92" height="86" rx="8" fill="#713f12" stroke="#f59e0b" stroke-width="2"/><text x="760" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">ECN bit 1</text><text x="760" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><rect x="826" y="130" width="92" height="86" rx="8" fill="#713f12" stroke="#f59e0b" stroke-width="2"/><text x="872" y="165" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" text-anchor="middle">ECN bit 0</text><text x="872" y="191" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="middle">1 bit</text><line x1="42" y1="235" x2="682" y2="235" stroke="#22d3ee" stroke-width="4"/><text x="362" y="261" fill="#67e8f9" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="middle">DSCP = 6 bits : choisit le comportement par saut (PHB)</text><line x1="714" y1="235" x2="918" y2="235" stroke="#f59e0b" stroke-width="4"/><text x="816" y="261" fill="#fcd34d" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">ECN = 2 bits</text><text x="480" y="313" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Ne pas confondre la valeur DSCP, le nom de classe et la file réellement configurée.</text></svg>


**Important :** un DSCP n’est pas une réservation de ressources et ne garantit pas, à lui seul, une latence donnée. Si un équipement ignore le DSCP, le réécrit ou ne dispose pas de la file correspondante, la marque n’obtient pas le traitement escompté.

### 3.2 Valeurs courantes

Les valeurs suivantes sont souvent rencontrées. Elles doivent être intégrées dans une politique cohérente de bout en bout ; elles ne forment pas à elles seules une configuration universelle.

| Nom | Valeur DSCP décimale | Usage courant possible | Précaution |
|---|---:|---|---|
| Default / DF | 0 | Trafic best effort | Valeur de base |
| CS1 | 8 | Trafic de faible priorité / scavenger dans certains designs | Ne pas l’utiliser sans politique documentée |
| AF11 / AF12 / AF13 | 10 / 12 / 14 | Classe AF1, différentes priorités de perte | Le chiffre final indique une préférence de perte, pas une priorité absolue |
| AF21 / AF22 / AF23 | 18 / 20 / 22 | Classe AF2 | Traitement dépendant du PHB et de la file |
| AF31 / AF32 / AF33 | 26 / 28 / 30 | Classe AF3 | À réserver à un besoin métier défini |
| AF41 / AF42 / AF43 | 34 / 36 / 38 | Classe AF4 | Usage dépendant du design |
| EF | 46 | Voix interactive dans de nombreux designs | La file prioritaire doit être limitée et dimensionnée |
| CS6 | 48 | Contrôle réseau selon la politique | Doit être réservé aux usages autorisés |
| CS7 | 56 | Usage local spécialisé dans certains designs | Ne pas propager sans politique explicite |

### Schéma 4 — Exemples de DSCP fréquemment rencontrés

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Exemples de DSCP fréquemment rencontrés"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Exemples de DSCP fréquemment rencontrés</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Convention de départ à adapter au design et à la politique</text><rect x="28" y="82" width="904" height="31" rx="6" fill="#064e3b" stroke="#475569" stroke-width="1"/><text x="47" y="103" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">EF</text><text x="280" y="103" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">46</text><text x="360" y="103" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Voix temps réel (si politique maîtrisée)</text><rect x="28" y="119" width="904" height="31" rx="6" fill="#1e3a8a" stroke="#475569" stroke-width="1"/><text x="47" y="140" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">AF41 / AF42 / AF43</text><text x="280" y="140" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">34 / 36 / 38</text><text x="360" y="140" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Vidéo ou données à définir</text><rect x="28" y="156" width="904" height="31" rx="6" fill="#3730a3" stroke="#475569" stroke-width="1"/><text x="47" y="177" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">AF21 / AF22 / AF23</text><text x="280" y="177" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">18 / 20 / 22</text><text x="360" y="177" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Données métier, priorité relative</text><rect x="28" y="193" width="904" height="31" rx="6" fill="#5b21b6" stroke="#475569" stroke-width="1"/><text x="47" y="214" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">CS5</text><text x="280" y="214" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">40</text><text x="360" y="214" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Signalisation applicative selon politique</text><rect x="28" y="230" width="904" height="31" rx="6" fill="#6b21a8" stroke="#475569" stroke-width="1"/><text x="47" y="251" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">CS3</text><text x="280" y="251" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">24</text><text x="360" y="251" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Exemple de classe interactive / signalisation</text><rect x="28" y="267" width="904" height="31" rx="6" fill="#78350f" stroke="#475569" stroke-width="1"/><text x="47" y="288" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">CS1</text><text x="280" y="288" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">8</text><text x="360" y="288" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Scavenger / faible priorité si conçu ainsi</text><rect x="28" y="304" width="904" height="31" rx="6" fill="#334155" stroke="#475569" stroke-width="1"/><text x="47" y="325" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="start">DF / Default</text><text x="280" y="325" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">0</text><text x="360" y="325" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="start">Best effort par défaut</text><text x="480" y="355" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" text-anchor="middle">Ces correspondances sont des conventions de départ, pas une règle universelle.</text></svg>


### 3.3 EF, AF, CS et Default en termes simples

- **EF (*Expedited Forwarding*)** est un comportement défini pour viser une transmission à faible délai, faible gigue et faible perte. Il est souvent utilisé pour la voix, mais il faut une capacité suffisante et un contrôle du trafic.
- **AF (*Assured Forwarding*)** définit plusieurs classes de forwarding et des préférences de perte. AFxy ne signifie pas que la classe AF4 est automatiquement prioritaire sur AF3 sur tous les équipements : le scheduler et la politique locale contrôlent réellement le traitement.
- **CS (*Class Selector*)** fournit des points de code correspondant à des classes de sélection, souvent utilisés comme conventions de classification ou pour du trafic de contrôle.
- **Default / DF** constitue le traitement de base pour le trafic qui n’a pas été affecté à une autre classe.

Évite les raccourcis du type « EF = toujours prioritaire partout » ou « AF41 = priorité maximale ». Il faut connaître la classification, le mappage vers les files, les paramètres de scheduling et les règles de réécriture sur chaque segment.

### 3.4 DSCP et CoS/PCP Ethernet

Le marquage DSCP se trouve dans l’en-tête IP. Le champ PCP d’une étiquette VLAN 802.1Q, souvent appelé CoS dans la documentation Cisco, utilise 3 bits et prend des valeurs de 0 à 7. Il s’agit de deux champs différents, sur des couches différentes, avec des espaces de valeurs différents. Les équipements peuvent être configurés pour mapper PCP vers DSCP, DSCP vers PCP, ou leurs valeurs vers une classe interne. Le mappage réel doit être vérifié.

### Schéma 5 — Frontière de confiance

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Définir la frontière de confiance"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Définir la frontière de confiance</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Le marquage provenant d’un terminal doit être validé par la politique</text><rect x="38" y="128" width="170" height="108" rx="12" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/><text x="123.0" y="166.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">PC / téléphone</text><text x="123.0" y="186.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Marquage potentiellement</text><text x="123.0" y="206.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">non fiable</text><rect x="278" y="128" width="190" height="108" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="373.0" y="166.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Commutateur d’accès</text><text x="373.0" y="186.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Frontière de confiance</text><text x="373.0" y="206.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Vérifier / remarquer</text><rect x="538" y="128" width="170" height="108" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="623.0" y="166.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Réseau cœur</text><text x="623.0" y="186.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Politique DSCP</text><text x="623.0" y="206.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">et files cohérentes</text><rect x="778" y="128" width="142" height="108" rx="12" fill="#3f2a14" stroke="#f59e0b" stroke-width="2"/><text x="849.0" y="176.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">WAN / sortie</text><text x="849.0" y="196.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Contrôle de profil</text><line x1="208" y1="182" x2="278" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="278.0,182.0 266.0,175.0 266.0,189.0" fill="#93c5fd"/><line x1="468" y1="182" x2="538" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="538.0,182.0 526.0,175.0 526.0,189.0" fill="#93c5fd"/><line x1="708" y1="182" x2="778" y2="182" stroke="#93c5fd" stroke-width="3"/><polygon points="778.0,182.0 766.0,175.0 766.0,189.0" fill="#93c5fd"/><text x="480" y="280" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="middle">N’accepter le marquage d’un terminal que si la politique le permet.</text><text x="480" y="309" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Le niveau de confiance se définit par port, rôle, identité et design.</text></svg>


## 4. Les fonctions QoS : de la classification à l’ordonnancement

La QoS n’est pas une commande unique. C’est une chaîne de fonctions qui doivent être conçues ensemble.

### 4.1 Classification : reconnaître le trafic

La classification détermine la classe à laquelle appartient un paquet. Les critères peuvent inclure :

- DSCP existant ;
- adresses IP ou préfixes ;
- protocole IP ;
- ports TCP ou UDP ;
- VLAN, port d’entrée, rôle du port ou identifiant d’application, selon les capacités ;
- ACL ou objet de classification défini par la plateforme.

La classification par port TCP/UDP est simple mais imparfaite : certains protocoles utilisent des ports dynamiques, du chiffrement ou des transports partagés. Dans un réseau géré, il est souvent préférable de classer près de la source à partir de l’identité de l’équipement ou d’une politique reconnue, puis de préserver ou vérifier la marque sur le reste du chemin.

### 4.2 Marquage : inscrire la classe

Le marquage écrit ou réécrit un champ tel que DSCP ou PCP. L’objectif est d’établir une convention partagée par les équipements du domaine. Le marquage est particulièrement utile quand un routeur suivant peut ensuite sélectionner une classe à partir du DSCP au lieu d’inspecter toutes les informations de chaque application.

Une stratégie commune consiste à :

1. identifier le trafic à la frontière ;
2. vérifier si la marque du terminal est digne de confiance ;
3. appliquer la valeur prévue par la politique ;
4. respecter le marquage à l’intérieur du domaine, sauf décision documentée ;
5. reclasser ou réécrire à la frontière d’un domaine externe si les accords de service l’exigent.

### 4.3 Metering et policing

Le *metering* mesure si le trafic correspond au profil. Le **policing** compare généralement le débit et les rafales observés au profil autorisé, souvent à l’aide d’un modèle de seau à jetons. Les paquets non conformes peuvent être supprimés, remis en conformité par re-marquage, ou traités autrement selon la configuration.

Un policer ne lisse pas nécessairement le flux ; il impose une règle de conformité. Une application peut voir des pertes si son trafic dépasse la limite appliquée. Le choix de la limite, de la taille de rafale et de l’action sur les paquets non conformes doit être adapté au trafic attendu.

### Schéma 6 — Modèle de policing

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Policing : modèle conceptuel du seau à jetons"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Policing : modèle conceptuel du seau à jetons</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Conformité au profil, dépassement et action configurée</text><text x="480" y="88" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="400" text-anchor="middle">Modèle simplifié du seau à jetons</text><rect x="45" y="130" width="182" height="100" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="136.0" y="164.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Seau de jetons</text><text x="136.0" y="185.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Taux de remplissage</text><text x="136.0" y="206.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">CIR</text><rect x="310" y="130" width="182" height="100" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="401.0" y="164.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Paquet entrant</text><text x="401.0" y="185.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Besoin de jetons</text><text x="401.0" y="206.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">selon sa taille</text><rect x="575" y="104" width="162" height="78" rx="12" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="656.0" y="137.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Conforme</text><text x="656.0" y="158.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">transmettre</text><rect x="575" y="208" width="162" height="78" rx="12" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="656.0" y="241.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Hors profil</text><text x="656.0" y="262.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">remark ou drop</text><rect x="790" y="152" width="132" height="82" rx="12" fill="#334155" stroke="#94a3b8" stroke-width="2"/><text x="856.0" y="187.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Trafic en</text><text x="856.0" y="208.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">sortie</text><line x1="227" y1="180" x2="310" y2="180" stroke="#93c5fd" stroke-width="3"/><polygon points="310.0,180.0 298.0,173.0 298.0,187.0" fill="#93c5fd"/><line x1="492" y1="165" x2="575" y2="143" stroke="#93c5fd" stroke-width="3"/><polygon points="575.0,143.0 561.6,139.3 565.2,152.8" fill="#93c5fd"/><line x1="492" y1="195" x2="575" y2="247" stroke="#93c5fd" stroke-width="3"/><polygon points="575.0,247.0 568.5,234.7 561.1,246.6" fill="#93c5fd"/><line x1="737" y1="143" x2="790" y2="184" stroke="#93c5fd" stroke-width="3"/><polygon points="790.0,184.0 784.8,171.1 776.2,182.2" fill="#93c5fd"/><line x1="737" y1="247" x2="790" y2="208" stroke="#93c5fd" stroke-width="3"/><polygon points="790.0,208.0 776.2,209.5 784.5,220.8" fill="#93c5fd"/><text x="480" y="333" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">Le détail du seau, des rafales et des actions dépend de la configuration et du matériel.</text></svg>


### 4.4 Shaping

Le **shaping** retarde les paquets dans un tampon afin de faire respecter un débit moyen ou un profil. Il peut être utile lorsqu’un lien physique rapide dessert un service opérateur plus lent : le routeur local façonne le trafic à une valeur cohérente avec le débit de service, ce qui peut déplacer le point de congestion vers un équipement que l’administrateur contrôle.

Le shaping introduit cependant du délai et peut lui aussi subir une saturation du tampon. Il doit être dimensionné pour le débit du service et la politique de files. Les commandes et leur portée varient selon les plateformes.

### Schéma 7 — Policing contre shaping

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Policing et shaping : deux objectifs différents"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Policing et shaping : deux objectifs différents</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Limiter un profil n’est pas la même chose que lisser une rafale</text><rect x="42" y="105" width="172" height="78" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="128.0" y="138.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Arrivée en rafales</text><text x="128.0" y="159.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">10 Mbit/s</text><rect x="392" y="82" width="176" height="112" rx="12" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="480.0" y="122.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">POLICING</text><text x="480.0" y="143.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Dépassement :</text><text x="480.0" y="164.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">remark / drop</text><rect x="392" y="225" width="176" height="112" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="480.0" y="265.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">SHAPING</text><text x="480.0" y="286.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Met en tampon</text><text x="480.0" y="307.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">puis lisse</text><rect x="744" y="153" width="172" height="82" rx="12" fill="#1e3a2a" stroke="#4ade80" stroke-width="2"/><text x="830.0" y="188.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Lien limité</text><text x="830.0" y="209.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">5 Mbit/s</text><line x1="214" y1="143" x2="392" y2="135" stroke="#f87171" stroke-width="3"/><polygon points="392.0,135.0 379.7,128.5 380.3,142.5" fill="#f87171"/><text x="303.0" y="124" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">policer</text><line x1="214" y1="150" x2="392" y2="280" stroke="#2dd4bf" stroke-width="3"/><polygon points="392.0,280.0 386.4,267.3 378.2,278.6" fill="#2dd4bf"/><text x="303.0" y="223" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="400" text-anchor="middle">shaper</text><line x1="568" y1="135" x2="744" y2="184" stroke="#f87171" stroke-width="3"/><polygon points="744.0,184.0 734.3,174.0 730.6,187.5" fill="#f87171"/><line x1="568" y1="280" x2="744" y2="204" stroke="#2dd4bf" stroke-width="3"/><polygon points="744.0,204.0 730.2,202.3 735.8,215.2" fill="#2dd4bf"/><text x="480" y="356" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Le policer agit sur la conformité ; le shaper régule le débit en retardant les paquets.</text></svg>


### 4.5 Mise en file et scheduling

Lorsque plusieurs paquets souhaitent sortir par une même interface, le scheduler décide quel paquet ou quelle classe sera servi. Les équipements peuvent offrir plusieurs mécanismes : files à priorité stricte, files pondérées, garanties de bande passante, partage des ressources restantes et autres variantes dépendant du matériel.

Une file dite prioritaire peut être servie avant les autres files, mais la politique doit empêcher le trafic prioritaire de monopoliser indéfiniment l’interface. Les commandes comme `priority`, `bandwidth` ou leurs variantes expriment des politiques dont la sémantique exacte dépend du système. Il faut lire la documentation de la plateforme concernée.

### Schéma 8 — Files de sortie

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Queues de sortie et ordonnancement"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Queues de sortie et ordonnancement</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">La file d’attente devient cruciale quand plusieurs paquets se disputent le lien</text><rect x="28" y="139" width="150" height="88" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="103.0" y="177.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Paquets prêts</text><text x="103.0" y="198.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">à sortir</text><line x1="178" y1="183" x2="234" y2="183" stroke="#93c5fd" stroke-width="3"/><polygon points="234.0,183.0 222.0,176.0 222.0,190.0" fill="#93c5fd"/><rect x="238" y="86" width="336" height="48" rx="8" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="252" y="105" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="start">Voix EF</text><text x="252" y="123" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="start">Priorité contrôlée</text><rect x="238" y="147" width="336" height="48" rx="8" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="252" y="166" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="start">Contrôle CS6</text><text x="252" y="184" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="start">Minimum garanti</text><rect x="238" y="208" width="336" height="48" rx="8" fill="#5b21b6" stroke="#c084fc" stroke-width="2"/><text x="252" y="227" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="start">Données AF</text><text x="252" y="245" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="start">Partage / garantie</text><rect x="238" y="269" width="336" height="48" rx="8" fill="#334155" stroke="#94a3b8" stroke-width="2"/><text x="252" y="288" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="start">Best effort</text><text x="252" y="306" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="400" text-anchor="start">Ressources restantes</text><line x1="574" y1="183" x2="660" y2="183" stroke="#93c5fd" stroke-width="3"/><polygon points="660.0,183.0 648.0,176.0 648.0,190.0" fill="#93c5fd"/><rect x="664" y="139" width="258" height="88" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="793.0" y="167.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Scheduler</text><text x="793.0" y="188.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Choisit le prochain paquet</text><text x="793.0" y="209.1" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">selon la politique</text><text x="480" y="354" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Les garanties et pourcentages doivent rester compatibles avec la capacité réelle du lien.</text></svg>


### 4.6 Gestion de congestion et AQM

Quand les tampons se remplissent, les équipements doivent décider comment gérer les paquets. Le mécanisme le plus simple est la mise en file jusqu’à saturation, puis la suppression des paquets supplémentaires (*tail drop*). Il peut entraîner une forte latence et des pertes groupées.

Des mécanismes d’**Active Queue Management (AQM)**, comme des variantes de RED/WRED ou des mécanismes modernes dépendant du matériel, peuvent signaler ou gérer la congestion avant que la file ne soit totalement remplie. Leur disponibilité, leur configuration et leur interaction avec ECN dépendent du matériel et du logiciel. AQM n’est pas une recette qui doit être activée sans mesure : il faut suivre les instructions de la plateforme et tester.

### 4.7 Résumé des mécanismes

| Fonction | Question | Exemple de résultat |
|---|---|---|
| Classification | « De quel trafic s’agit-il ? » | Affecter un paquet à VOICE ou DATA |
| Marquage | « Quelle classe annoncer ? » | Écrire DSCP EF ou AF21 |
| Policing | « Le flux respecte-t-il son profil ? » | Transmettre, re-marquer ou supprimer |
| Shaping | « À quel rythme émettre ? » | Mettre en tampon puis lisser les rafales |
| Queuing | « Où attendre si la sortie est occupée ? » | Placer le paquet dans une file |
| Scheduling | « Quelle file est servie ensuite ? » | Priorité, garantie ou partage pondéré |
| AQM | « Comment gérer une file qui grossit ? » | Signaler ou supprimer certains paquets avant saturation totale |

## 5. La frontière de confiance

Une politique QoS correcte ne consiste pas à croire n’importe quelle marque reçue. Un terminal utilisateur peut émettre des paquets DSCP EF sans être une source de voix autorisée. Si le réseau traite automatiquement toute marque EF comme prioritaire, une machine mal configurée ou malveillante peut saturer la file prioritaire et nuire aux véritables appels.

La **frontière de confiance** définit où l’organisation valide le marquage. Dans un réseau campus, le port d’accès, le commutateur, le téléphone IP ou un composant d’identité peuvent participer à cette décision selon le design. On peut faire confiance aux marques de certains équipements gérés et re-marquer les flux provenant d’équipements non fiables.

Quelques principes :

- définir un modèle de classification/marking documenté ;
- ne pas accepter automatiquement les valeurs hautes de tous les ports ;
- protéger la classe de priorité avec une limite ou une politique adaptée ;
- appliquer les règles cohérentes aux deux sens lorsque nécessaire ;
- vérifier les compteurs réels au point d’application.

### Schéma 9 — Le chemin d’un paquet

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Chemin d’un paquet à travers un équipement"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Chemin d’un paquet à travers un équipement</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Les fonctions et points d’application varient selon le matériel</text><rect x="25" y="126" width="158" height="102" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="104.0" y="171.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Entrée interface</text><text x="104.0" y="191.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Classifier / marquer</text><rect x="222" y="126" width="158" height="102" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="301.0" y="171.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Routage</text><text x="301.0" y="191.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Choix du next-hop</text><rect x="419" y="126" width="158" height="102" rx="12" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="498.0" y="171.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">File de sortie</text><text x="498.0" y="191.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Scheduler / AQM</text><rect x="616" y="126" width="158" height="102" rx="12" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="695.0" y="171.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Lien encombré</text><text x="695.0" y="191.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Attente / drop</text><rect x="813" y="126" width="122" height="102" rx="12" fill="#1e3a2a" stroke="#4ade80" stroke-width="2"/><text x="874.0" y="171.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">Sortie</text><text x="874.0" y="191.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Réseau</text><line x1="183" y1="177" x2="222" y2="177" stroke="#93c5fd" stroke-width="3"/><polygon points="222.0,177.0 210.0,170.0 210.0,184.0" fill="#93c5fd"/><line x1="380" y1="177" x2="419" y2="177" stroke="#93c5fd" stroke-width="3"/><polygon points="419.0,177.0 407.0,170.0 407.0,184.0" fill="#93c5fd"/><line x1="577" y1="177" x2="616" y2="177" stroke="#93c5fd" stroke-width="3"/><polygon points="616.0,177.0 604.0,170.0 604.0,184.0" fill="#93c5fd"/><line x1="774" y1="177" x2="813" y2="177" stroke="#93c5fd" stroke-width="3"/><polygon points="813.0,177.0 801.0,170.0 801.0,184.0" fill="#93c5fd"/><text x="480" y="283" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Le traitement exact dépend de la plateforme : ASIC, type d’interface, direction et politique.</text><text x="480" y="311" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">La congestion se traite à l’endroit où la ressource est réellement disputée.</text></svg>


## 6. Construire une politique de service simple

Il n’existe pas de table universelle de DSCP adaptée à toutes les entreprises. Le tableau suivant représente un **exemple de départ** à adapter :

| Classe proposée | Types de trafic possibles | Marque de départ possible | Principes de traitement |
|---|---|---|---|
| VOICE | Médias voix temps réel reconnus | EF (46) | Priorité contrôlée, débit maximum dimensionné, mesure de perte/gigue |
| SIGNALING | Signalisation VoIP | CS3 ou CS5 selon le design | Garantie raisonnable, ne pas confondre avec les médias voix |
| BUSINESS | Transactions métier importantes | AF21 (18), selon le plan | Garantie ou partage adapté, limite et suivi des pertes |
| VIDEO | Visioconférence | AF41 ou autre marque validée | Classer selon les besoins, valider le traitement du trafic réel |
| BULK | Sauvegardes ou transferts volumineux | Default ou classe spécifique | Utiliser les ressources restantes, éventuellement limiter |
| SCAVENGER | Trafic de faible priorité clairement identifié | CS1 (8), si le design le prévoit | Faible priorité, sans casser les usages fondamentaux |
| DEFAULT | Trafic général non classé ailleurs | DF (0) | Best effort et ressources résiduelles équitables |

### Schéma 10 — Classes de service

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Classes de service QoS"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Classes de service : des besoins différents</text><text x="480" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Exemple de convention, à définir de bout en bout</text><rect x="75" y="91" width="810" height="48" rx="9" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="98" y="121" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" text-anchor="start">EF / 46</text><text x="270" y="121" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" text-anchor="start">Voix interactive : priorité limitée et dimensionnée</text><rect x="75" y="151" width="810" height="48" rx="9" fill="#1e3a8a" stroke="#60a5fa" stroke-width="2"/><text x="98" y="181" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" text-anchor="start">AF4x</text><text x="270" y="181" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" text-anchor="start">Vidéo ou application interactive : ressources selon le design</text><rect x="75" y="211" width="810" height="48" rx="9" fill="#5b21b6" stroke="#c084fc" stroke-width="2"/><text x="98" y="241" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" text-anchor="start">AF2x / AF3x</text><text x="270" y="241" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" text-anchor="start">Données métier : partage ou garantie mesurée</text><rect x="75" y="271" width="810" height="48" rx="9" fill="#334155" stroke="#94a3b8" stroke-width="2"/><text x="98" y="301" fill="#ffffff" font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700" text-anchor="start">DF / 0</text><text x="270" y="301" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" text-anchor="start">Trafic général : best effort</text><text x="480" y="350" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">La marque seule ne garantit aucun traitement si les équipements ne l’appliquent pas.</text></svg>

**Éviter une erreur fréquente :** choisir une marque n’implique pas qu’une file ou une bande passante réservée apparaisse automatiquement. Il faut configurer et vérifier la correspondance entre la classe, les actions, la file et l’interface de sortie.

## 7. QoS Cisco avec MQC

Cisco utilise fréquemment la **Modular QoS CLI (MQC)** sur IOS/IOS XE. Le modèle logique sépare la reconnaissance du trafic, les actions et le point où la politique est appliquée.

- `class-map` décrit les critères de classification ;
- `policy-map` associe les classes à des actions ;
- `service-policy` applique une politique à une interface, dans une direction.

### Schéma 11 — MQC en trois étapes

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Modular QoS CLI : class-map, policy-map, service-policy"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Modular QoS CLI : class-map, policy-map, service-policy</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Modèle Cisco courant ; syntaxe et fonctionnalités selon plateforme</text><rect x="45" y="133" width="240" height="108" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="165.0" y="170.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="600" text-anchor="middle">CLASS-MAP</text><text x="165.0" y="192.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">Quoi reconnaître ?</text><text x="165.0" y="214.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">DSCP, ACL, protocoles</text><rect x="360" y="133" width="240" height="108" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="480.0" y="170.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="600" text-anchor="middle">POLICY-MAP</text><text x="480.0" y="192.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">Quel traitement ?</text><text x="480.0" y="214.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">priority, bandwidth, police</text><rect x="675" y="133" width="240" height="108" rx="12" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="795.0" y="170.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="600" text-anchor="middle">SERVICE-POLICY</text><text x="795.0" y="192.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">Où et quel sens ?</text><text x="795.0" y="214.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">interface in / out</text><line x1="285" y1="187" x2="360" y2="187" stroke="#93c5fd" stroke-width="3"/><polygon points="360.0,187.0 348.0,180.0 348.0,194.0" fill="#93c5fd"/><line x1="600" y1="187" x2="675" y2="187" stroke="#93c5fd" stroke-width="3"/><polygon points="675.0,187.0 663.0,180.0 663.0,194.0" fill="#93c5fd"/><text x="480" y="291" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">Modular QoS CLI : séparer classification, action et point d’application.</text><text x="480" y="322" fill="#a7f3d0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">Vérification Cisco courante : show policy-map interface</text></svg>


### 7.1 Exemple pédagogique de politique de sortie

L’exemple ci-dessous illustre une structure MQC courante. Les mots-clés supportés, les unités des commandes, les pourcentages et les contraintes de matériel varient selon le modèle et la version IOS/IOS XE. Ne pas coller aveuglément la configuration en production.

```text
class-map match-any CM-VOICE
 match dscp ef

class-map match-any CM-BUSINESS
 match dscp af21 af22 af23

class-map match-any CM-SCAVENGER
 match dscp cs1

policy-map PM-WAN-OUT
 class CM-VOICE
  priority percent 10
 class CM-BUSINESS
  bandwidth percent 25
 class CM-SCAVENGER
  bandwidth percent 5
 class class-default
  fair-queue

interface GigabitEthernet0/0/1
 description WAN - EXEMPLE A ADAPTER
 service-policy output PM-WAN-OUT
```

**Ce que l’exemple fait conceptuellement :**

1. `CM-VOICE` reconnaît les paquets qui ont le DSCP EF ; la configuration suppose que la marque a été produite ou validée par une frontière de confiance.
2. `CM-BUSINESS` reconnaît des valeurs AF21 à AF23, soit des codepoints d’une classe AF donnée.
3. `CM-SCAVENGER` reconnaît les paquets CS1.
4. `PM-WAN-OUT` associe un comportement à chaque classe.
5. `service-policy output` associe cette politique au trafic sortant de l’interface visée.

`priority percent 10` n’est pas un chiffre magique. Si le codec, l’encapsulation, le nombre d’appels simultanés et les rafales ne sont pas correctement évalués, la classe prioritaire peut être sous-dimensionnée ou trop permissive. Selon la plateforme, le comportement exact du LLQ et les contrôles de priorité diffèrent. La valeur de 10 % n’est qu’un exemple illustratif.

Pour un équipement sans support des commandes présentées, il faut consulter la documentation QoS correspondant précisément au modèle et à la version du logiciel. Certaines politiques peuvent également nécessiter une hiérarchie de policies ou un point d’attache différent.

### 7.2 Exemple de policing à l’entrée

Cet exemple est conceptuel et à adapter aux capacités du routeur. Il illustre l’idée de classer un trafic connu, puis de limiter son débit :

```text
class-map match-any CM-BULK
 match access-group name ACL-BULK

policy-map PM-INGRESS-LIMIT
 class CM-BULK
  police 2000000 conform-action transmit exceed-action set-dscp-transmit cs1 violate-action drop

interface GigabitEthernet0/0/0
 service-policy input PM-INGRESS-LIMIT
```

Une ACL `ACL-BULK` doit être définie et vérifiée séparément ; elle ne doit pas cibler par accident des services critiques. La syntaxe détaillée d’un policer et ses actions peuvent varier. Mesure le trafic, décide comment traiter le dépassement et valide les compteurs avant le déploiement.

### 7.3 Vérification

Selon la plateforme, les commandes suivantes sont souvent utiles :

```text
show policy-map
show policy-map interface GigabitEthernet0/0/1
show class-map
show interfaces GigabitEthernet0/0/1
show running-config interface GigabitEthernet0/0/1
```

La commande `show policy-map interface` est particulièrement utile sur les plateformes qui la supportent : on peut y rechercher les paquets classés, les compteurs par classe, les paquets abandonnés, les statistiques de policing et d’autres compteurs disponibles. La forme des sorties varie selon la plateforme.




## 8. Où appliquer la politique ?

Une politique QoS peut être attachée à l’entrée (*input*) ou à la sortie (*output*) d’une interface selon les fonctions employées. Une politique d’entrée peut classer et marquer un trafic qui entre dans l’équipement ; les fonctions de file d’attente sont souvent liées à la sortie, car c’est là que les paquets se disputent le lien. Les restrictions et exceptions réelles varient par plate-forme.

Le bon emplacement se choisit en fonction de la ressource congestionnée. Une politique de sortie sur un port d’accès non congestionné ne résoudra pas nécessairement une file sur le WAN. Sur une interface physique de 1 Gbit/s qui dessert un service opérateur à 20 Mbit/s, une politique de shaping peut être nécessaire afin de gérer la congestion au point maîtrisé par l’entreprise.

### Schéma 12 — Topologie de laboratoire

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Topologie du laboratoire QoS"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Topologie du laboratoire QoS</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Téléphone IP, données, point de confiance et lien WAN contraint</text><rect x="30" y="115" width="180" height="80" rx="12" fill="#14532d" stroke="#4ade80" stroke-width="2"/><text x="120.0" y="149.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Téléphone IP</text><text x="120.0" y="170.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">DSCP EF validé</text><rect x="30" y="245" width="180" height="80" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="120.0" y="279.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">PC / données</text><text x="120.0" y="300.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Best effort / AF</text><rect x="302" y="174" width="190" height="90" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="397.0" y="213.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="600" text-anchor="middle">Switch L3</text><text x="397.0" y="235.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="400" text-anchor="middle">Trust boundary</text><rect x="580" y="174" width="170" height="90" rx="12" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="665.0" y="213.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">Routeur WAN</text><text x="665.0" y="234.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">Policy-map out</text><rect x="810" y="174" width="120" height="90" rx="12" fill="#1e3a2a" stroke="#4ade80" stroke-width="2"/><text x="870.0" y="213.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="600" text-anchor="middle">WAN</text><text x="870.0" y="234.6" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="400" text-anchor="middle">10 Mb/s</text><line x1="210" y1="155" x2="302" y2="205" stroke="#93c5fd" stroke-width="3"/><polygon points="302.0,205.0 294.8,193.1 288.1,205.4" fill="#93c5fd"/><line x1="210" y1="285" x2="302" y2="235" stroke="#93c5fd" stroke-width="3"/><polygon points="302.0,235.0 288.1,234.6 294.8,246.9" fill="#93c5fd"/><line x1="492" y1="219" x2="580" y2="219" stroke="#93c5fd" stroke-width="3"/><polygon points="580.0,219.0 568.0,212.0 568.0,226.0" fill="#93c5fd"/><line x1="750" y1="219" x2="810" y2="219" stroke="#93c5fd" stroke-width="3"/><polygon points="810.0,219.0 798.0,212.0 798.0,226.0" fill="#93c5fd"/><text x="480" y="355" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">Objectif : préserver la voix pendant la congestion, sans affamer les autres classes.</text></svg>


## 9. Laboratoire guidé

### 9.1 Objectif

Créer un mini-réseau comprenant un téléphone IP, un poste de données, un commutateur d’accès, un routeur vers un WAN à capacité réduite et un hôte de test. L’objectif n’est pas d’imposer un design de production, mais de montrer comment la QoS s’observe sous charge.

### 9.2 Plan d’adressage proposé

| Équipement / interface | Adresse ou rôle |
|---|---|
| PC données | 192.0.2.10/24 (adresse de documentation) |
| Téléphone IP | 192.0.2.20/24 (adresse de documentation) |
| Interface LAN du routeur / passerelle | 192.0.2.1/24 |
| Réseau distant de test | 198.51.100.0/24 (adresse de documentation) |
| Lien WAN | Capacité volontairement contrainte dans le laboratoire |

Les préfixes `192.0.2.0/24` et `198.51.100.0/24` sont réservés aux exemples/documentation ; ils ne sont pas destinés à la configuration sur un réseau public réel. Évite le double emploi de la même adresse pour le routeur et la passerelle : dans ton simulateur, choisis un plan sans chevauchement et documente précisément les interfaces.

### 9.3 Étapes de travail

1. **Établir la référence.** Teste la connectivité avant d’ajouter la QoS ; vérifie les erreurs physiques, le routage et le débit WAN.
2. **Définir les classes.** Identifie la voix, les données métier, le trafic volumineux et le trafic par défaut ; écris les règles de classification.
3. **Définir la confiance.** Décide qui peut marquer EF ou AF et où la marque est validée. Ne prends pas le DSCP des clients comme vérité universelle.
4. **Créer les classes MQC.** Adapte les commandes disponibles dans IOS/IOS XE à la plateforme réelle ou au simulateur.
5. **Créer et attacher une policy.** Commence par une politique simple, applique-la dans la bonne direction et garde une méthode de retour arrière.
6. **Produire une charge contrôlée.** Génère du trafic best effort et un flux temps réel de test, si l’environnement s’y prête.
7. **Mesurer sous charge.** Observe RTT, gigue, pertes, débit par classe, files et drops avant et après.
8. **Vérifier les effets secondaires.** Confirme que la classe prioritaire ne monopolise pas le lien et que les autres classes conservent les ressources prévues.
9. **Sauvegarder et documenter.** Note le matériel, la version, les interfaces, les compteurs, les résultats et la configuration validée.

### 9.4 Critères de réussite

Le laboratoire est réussi quand tu peux démontrer que les paquets sont classés comme prévu, que les compteurs changent quand les flux passent, que les marques sont cohérentes, et que l’effet de la politique est mesuré sous congestion. Le simple fait qu’un ping fonctionne à vide ne suffit pas pour démontrer qu’une politique QoS est correcte.

## 10. Méthode de dépannage en 7 étapes

Quand une application est dégradée, évite de modifier plusieurs paramètres en même temps. Suis une méthode mesurable :

1. **Définis le symptôme.** Quelle application, quel sens, quelle période, quels sites et quelles personnes ?
2. **Mesure les métriques.** Débit, RTT, gigue, pertes, erreurs physiques, drops et utilisation.
3. **Localise le goulot.** Identifie l’interface et la ressource dont la capacité est disputée.
4. **Vérifie le marquage.** Capture un paquet ou inspecte les compteurs pour confirmer le DSCP réellement présent.
5. **Vérifie la classification.** La classe attendue compte-t-elle les paquets ? Une autre classe les capture-t-elle d’abord ?
6. **Vérifie la file et le profil.** Compteurs de drops, shaping, policer, queue depth, erreurs ou saturation selon la plateforme.
7. **Change une variable, reteste et documente.** Garde un point de comparaison et prévois un retour arrière.

### Schéma 13 — Arbre de dépannage

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Dépannage QoS : du symptôme aux preuves"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Dépannage QoS : du symptôme aux preuves</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Mesurer et corréler avant d’ajuster la configuration</text><rect x="350" y="77" width="260" height="56" rx="12" fill="#422006" stroke="#f59e0b" stroke-width="2"/><text x="480.0" y="110.44" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="600" text-anchor="middle">Symptôme : voix ou appli dégradée</text><rect x="35" y="188" width="200" height="70" rx="12" fill="#172554" stroke="#818cf8" stroke-width="2"/><text x="135.0" y="217.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">1. Mesurer</text><text x="135.0" y="237.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">pertes, RTT, gigue</text><rect x="270" y="188" width="200" height="70" rx="12" fill="#123b3b" stroke="#2dd4bf" stroke-width="2"/><text x="370.0" y="217.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">2. Vérifier le marquage</text><text x="370.0" y="237.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">DSCP réel</text><rect x="505" y="188" width="200" height="70" rx="12" fill="#4c1d1d" stroke="#f87171" stroke-width="2"/><text x="605.0" y="217.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">3. Lire les compteurs</text><text x="605.0" y="237.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">queues / drops</text><rect x="740" y="188" width="185" height="70" rx="12" fill="#1e3a2a" stroke="#4ade80" stroke-width="2"/><text x="832.5" y="217.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="middle">4. Valider le lien</text><text x="832.5" y="237.76" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="400" text-anchor="middle">débit / shaping</text><line x1="410" y1="133" x2="135" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="135.0,188.0 148.1,192.5 145.4,178.8" fill="#93c5fd"/><line x1="435" y1="133" x2="370" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="370.0,188.0 383.7,185.6 374.6,174.9" fill="#93c5fd"/><line x1="525" y1="133" x2="605" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="605.0,188.0 599.1,175.4 591.1,187.0" fill="#93c5fd"/><line x1="550" y1="133" x2="832" y2="188" stroke="#93c5fd" stroke-width="3"/><polygon points="832.0,188.0 821.6,178.8 818.9,192.6" fill="#93c5fd"/><text x="480" y="315" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" text-anchor="middle">Corréler plusieurs preuves avant de changer la politique.</text></svg>


### 10.1 Cas pratiques

**Cas A — La voix se dégrade uniquement quand un transfert de fichier démarre.**  
Possible cause : le trafic data remplit la file de sortie et la voix n’a pas de traitement adapté. Mesures : compteur de drops, utilisation du lien, DSCP EF réel, classification et compteurs de la classe voix. Ne modifie pas d’abord le DSCP sans vérifier le traitement effectif.

**Cas B — EF apparaît dans la capture, mais il n’y a aucun avantage.**  
Possible causes : la policy n’est pas attachée, elle est attachée dans le mauvais sens, l’interface n’applique pas cette fonction, le DSCP est réécrit plus loin ou il n’existe pas de file adaptée. Comparer la marque et les compteurs sur plusieurs points du chemin.

**Cas C — La classe voix est prioritaire mais les données souffrent fortement.**  
Une classe prioritaire trop permissive peut monopoliser la capacité. Mesurer son débit de pointe et vérifier son contrôle, le dimensionnement et les autres classes. Une priorité ne doit pas être utilisée comme solution à un surabonnement permanent.

**Cas D — Le ping est normal, mais la visioconférence est mauvaise.**  
Le ping ne représente pas nécessairement la même classe de service, le même volume de paquets, le même sens ni la même sensibilité à la gigue. Ajouter des mesures adaptées et examiner l’application ainsi que le chemin réel.

## 11. Erreurs fréquentes à éviter

1. Marquer tout trafic critique EF sans contrôle de la charge.
2. Penser que DSCP réserve de la bande passante automatiquement.
3. Faire confiance à tous les terminaux et laisser un client s’octroyer la priorité.
4. Classer uniquement par numéro de port sans connaître le comportement de l’application.
5. Appliquer une politique au mauvais endroit ou dans le mauvais sens.
6. Utiliser un policer en croyant qu’il lissera le trafic comme un shaper.
7. Dimensionner les classes sur le débit moyen sans considérer les rafales et les pointes.
8. Attribuer toute perte à la QoS alors qu’un lien physique ou une MTU peut être en cause.
9. Activer des mécanismes avancés sans connaître les limites du matériel.
10. Valider à vide au lieu de tester dans une situation de congestion contrôlée.

## 12. Exercice corrigé : calculer une enveloppe de voix

Une entreprise possède un accès WAN nominal de 20 Mbit/s et veut prévoir jusqu’à 20 appels VoIP simultanés. Pour cet exercice, on suppose un débit par appel de 100 kbit/s dans chaque direction, **valeur pédagogique qui simplifie l’encapsulation et le contexte codec**.

**Question 1 :** quel ordre de grandeur obtient-on pour 20 appels ?  
Calcul : 20 × 100 kbit/s = 2 000 kbit/s, soit 2 Mbit/s par sens selon l’hypothèse utilisée.

**Question 2 :** est-il correct de définir exactement 2 Mbit/s de capacité prioritaire et de considérer le problème réglé ?  
Non. Il faut vérifier si la valeur inclut les en-têtes et l’encapsulation, si chaque sens est dimensionné séparément, s’il existe d’autres flux temps réel, quelle marge est prévue pour les rafales, et quelles actions de policing et de scheduling sont supportées. Il faut aussi comparer la taille de la classe prioritaire à la capacité de service réelle.

**Question 3 :** pourquoi un policer peut-il dégrader les appels pendant un pic ?  
Parce que les paquets qui dépassent son profil peuvent être abandonnés ou re-marqués selon les actions configurées. La voix étant sensible à la perte et au délai, le profil doit correspondre au trafic autorisé et sa conséquence doit être testée.

## 13. Quiz de validation

**1. Quel est le rôle principal de la QoS ?**  
A. Augmenter la capacité physique d’un lien  
B. Différencier le traitement de classes de trafic et gérer les ressources disputées  
C. Remplacer le routage IP  
D. Chiffrer les paquets

**2. Combien de bits composent DSCP ?**  
A. 2  
B. 3  
C. 6  
D. 8

**3. Où se trouve DSCP ?**  
A. Dans l’en-tête IP  
B. Dans le champ TCP Window  
C. Dans le nom DNS  
D. Dans l’adresse MAC

**4. Quelle différence générale existe entre policing et shaping ?**  
A. Ils sont toujours identiques  
B. Le policing contrôle la conformité et peut supprimer ou re-marquer ; le shaping met en tampon pour lisser le trafic  
C. Le shaping chiffre le trafic  
D. Le policing ne s’applique jamais aux paquets IP

**5. Que fait class-map dans le modèle MQC ?**  
A. Reconnaît les classes de trafic  
B. Crée un tunnel VPN  
C. Configure le routage dynamique  
D. Attribue une adresse IP au poste

**6. Une marque EF garantit-elle automatiquement une file prioritaire sur tous les routeurs ?**  
A. Oui  
B. Non, le comportement dépend de la politique et de la plateforme  
C. Oui uniquement en IPv6  
D. Oui quand le débit est faible

**7. Pourquoi définir une frontière de confiance ?**  
A. Pour que chaque terminal choisisse librement sa priorité  
B. Pour contrôler les marques reçues et éviter les abus ou erreurs de marquage  
C. Pour remplacer les ACL de sécurité  
D. Pour augmenter le débit nominal

**8. À quel endroit une politique de file de sortie est-elle souvent particulièrement utile ?**  
A. Là où les paquets se disputent la capacité d’émission  
B. Un serveur DNS qui n’est pas sur le chemin  
C. Un port inutilisé  
D. Un poste sans trafic

**9. Quel contrôle est le plus convaincant pour valider une QoS ?**  
A. Le seul fait que l’interface soit up  
B. Le seul ping à vide  
C. Des mesures et compteurs cohérents sous une charge contrôlée  
D. Une marque DSCP présente dans la configuration seulement

**10. Une QoS peut-elle corriger une panne de routage ?**  
A. Oui dans tous les cas  
B. Non, elle ne remplace pas le diagnostic du routage ou des pannes physiques  
C. Oui en donnant CS6 à tout le trafic  
D. Oui si le shaping est activé

### Corrigé du quiz

1. **B** — La QoS organise le traitement de différentes classes et l’usage de ressources limitées.  
2. **C** — DSCP occupe six bits ; les deux autres bits du champ DS concernent ECN.  
3. **A** — DSCP se situe dans l’en-tête IP.  
4. **B** — Le policing contrôle la conformité au profil ; le shaping retarde des paquets pour lisser le débit.  
5. **A** — `class-map` décrit les critères de classification dans MQC.  
6. **B** — Une valeur DSCP seule ne crée pas une file ni une garantie.  
7. **B** — La frontière de confiance vérifie les marques ou décide lesquelles préserver.  
8. **A** — Les queues de sortie gèrent l’accès à une capacité d’émission partagée.  
9. **C** — Il faut valider le comportement et les compteurs sous une charge pertinente.  
10. **B** — La QoS ne remplace pas le dépannage de la couche physique, du routage, des services ou de l’application.

## 14. Checklist avant mise en production

- [ ] Les applications et objectifs de service sont documentés.
- [ ] Les goulots d’étranglement réels ont été identifiés par mesure.
- [ ] Les classes et valeurs DSCP sont définies dans un plan commun.
- [ ] Les marques provenant des sources non fiables sont vérifiées ou réécrites.
- [ ] Le policer et le shaper sont dimensionnés en tenant compte des rafales.
- [ ] Le traitement des files et la limite de la classe prioritaire ont été validés.
- [ ] La politique est appliquée à la bonne interface et dans le bon sens.
- [ ] La compatibilité du matériel et de la version logicielle est confirmée.
- [ ] Les compteurs, pertes et métriques applicatives ont été relevés avant et après.
- [ ] Un test de congestion contrôlé a été réalisé.
- [ ] Un retour arrière et un plan de validation après changement existent.
- [ ] La politique est documentée, révisable et suivie dans le temps.

### Schéma 14 — Checklist de validation

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Checklist de conception QoS"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1220" stroke="#334155" stroke-width="2"/><text x="480.0" y="38" fill="#f8fafc" font-family="Arial, Helvetica, sans-serif" font-size="23" font-weight="700" text-anchor="middle">Checklist de conception QoS</text><text x="480.0" y="64" fill="#cbd5e1" font-family="Arial, Helvetica, sans-serif" font-size="14" text-anchor="middle">Des objectifs mesurables à la validation opérationnelle</text><rect x="48" y="102" width="410" height="55" rx="9" fill="#10263b" stroke="#38bdf8" stroke-width="2"/><rect x="60" y="113" width="32" height="32" rx="6" fill="#164e63" stroke="#22d3ee" stroke-width="1"/><text x="76" y="134" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">1</text><text x="106" y="135" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="start">Définir SLO et applications</text><rect x="498" y="102" width="410" height="55" rx="9" fill="#10263b" stroke="#38bdf8" stroke-width="2"/><rect x="510" y="113" width="32" height="32" rx="6" fill="#164e63" stroke="#22d3ee" stroke-width="1"/><text x="526" y="134" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">2</text><text x="556" y="135" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="start">Classer et marquer à la frontière</text><rect x="48" y="180" width="410" height="55" rx="9" fill="#10263b" stroke="#38bdf8" stroke-width="2"/><rect x="60" y="191" width="32" height="32" rx="6" fill="#164e63" stroke="#22d3ee" stroke-width="1"/><text x="76" y="212" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">3</text><text x="106" y="213" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="start">Dimensionner les classes et files</text><rect x="498" y="180" width="410" height="55" rx="9" fill="#10263b" stroke="#38bdf8" stroke-width="2"/><rect x="510" y="191" width="32" height="32" rx="6" fill="#164e63" stroke="#22d3ee" stroke-width="1"/><text x="526" y="212" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">4</text><text x="556" y="213" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="start">Protéger la priorité contre les abus</text><rect x="48" y="258" width="410" height="55" rx="9" fill="#10263b" stroke="#38bdf8" stroke-width="2"/><rect x="60" y="269" width="32" height="32" rx="6" fill="#164e63" stroke="#22d3ee" stroke-width="1"/><text x="76" y="290" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">5</text><text x="106" y="291" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="start">Appliquer sur la bonne interface/sens</text><rect x="498" y="258" width="410" height="55" rx="9" fill="#10263b" stroke="#38bdf8" stroke-width="2"/><rect x="510" y="269" width="32" height="32" rx="6" fill="#164e63" stroke="#22d3ee" stroke-width="1"/><text x="526" y="290" fill="#fff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">6</text><text x="556" y="291" fill="#e2e8f0" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="600" text-anchor="start">Mesurer sous congestion et documenter</text><text x="480" y="355" fill="#fbbf24" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" text-anchor="middle">La QoS doit être testée avec de la congestion contrôlée, pas seulement avec un ping à vide.</text></svg>


## 15. Glossaire

- **AQM** : Active Queue Management, gestion active des files.
- **CoS / PCP** : champ de priorité 802.1Q dans une trame Ethernet VLAN.
- **DiffServ** : architecture de différenciation du traitement IP par agrégats.
- **DSCP** : codepoint de six bits dans le champ DS.
- **ECN** : mécanisme de notification explicite de congestion.
- **EF** : Expedited Forwarding, comportement par saut souvent associé à la voix.
- **AF** : Assured Forwarding, groupe de comportements avec classes et préférences de perte.
- **Gigue** : variation du délai d’arrivée des paquets.
- **LLQ** : mécanisme de file à faible latence, souvent construit au moyen d’une classe prioritaire dans certaines implémentations Cisco.
- **MQC** : Modular QoS CLI de Cisco, modèle fondé notamment sur class-map, policy-map et service-policy.
- **PHB** : Per-Hop Behavior, traitement appliqué à un agrégat de paquets à un saut.
- **Policing** : contrôle de conformité du trafic à un profil.
- **Shaping** : régulation de l’émission en mettant temporairement les paquets en tampon.
- **Scheduler** : mécanisme de sélection de la file à servir.
- **Tail drop** : élimination des paquets quand la file atteint sa limite.
- **Trust boundary** : point où la politique décide de faire confiance ou non au marquage QoS.

## 16. Références techniques

Les liens ci-dessous servent de sources de référence pour approfondir le cours et vérifier les détails. Pour une configuration en production, utiliser la documentation de la plateforme et de la version exactes.

1. Cisco, *Quality of Service Configuration Guide, IOS XE* : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/quality-of-service/quality-of-service.html
2. Cisco, *Applying QoS Features Using the MQC* : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/quality-of-service/quality-of-service/m_qos-mqc-0.html
3. Cisco, *Quality of Service Configuration Guide — Catalyst 9000* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/qos/quality-of-service-configuration-guide/m-quality-of-service.html
4. IETF, RFC 2474, *Definition of the Differentiated Services Field (DS Field) in the IPv4 and IPv6 Headers* : https://www.rfc-editor.org/rfc/rfc2474.html
5. IETF, RFC 2597, *Assured Forwarding PHB Group* : https://www.rfc-editor.org/rfc/rfc2597.html
6. IETF, RFC 3246, *An Expedited Forwarding PHB* : https://www.rfc-editor.org/rfc/rfc3246.html
7. IETF, RFC 4594, *Configuration Guidelines for DiffServ Service Classes* : https://www.rfc-editor.org/rfc/rfc4594.html


## Résumé final

La QoS commence par une politique de trafic claire : savoir quelles applications existent, quelles performances elles requièrent, où la congestion se produit et quelles ressources doivent être partagées. La classification et le marquage expriment cette politique ; le policing et le shaping contrôlent le trafic ; les files et les schedulers organisent la transmission quand les ressources sont disputées. Enfin, la mesure, les compteurs et les essais sous charge prouvent si la politique fonctionne réellement.
