# Haute disponibilité des réseaux — Niveau Débutant

**Niveau :** Débutant  
**Durée indicative :** 4 à 6 heures, selon les laboratoires  
**Prérequis :** connaître les bases de la commutation Ethernet, des VLAN, des adresses IP, des passerelles et des commandes `ping` / `traceroute`. Aucune expérience préalable de la haute disponibilité n'est requise.  
**Environnement recommandé :** Packet Tracer ou une maquette virtuelle pour les réseaux, deux hôtes de test, un terminal Windows ou Linux et, si possible, Wireshark.

Ce cours est le premier niveau de la série **Haute disponibilité (HA)**. Il construit les fondations utiles aux cours futurs `ha-intermediaire.md` et `ha-expert.md`. Le niveau Intermédiaire pourra ensuite approfondir les protocoles de redondance, la convergence, la synchronisation d'état, les clusters, le routage dynamique et les tests de bascule. Le niveau Expert traitera l'ingénierie de résilience à grande échelle, les domaines de panne, l'automatisation, les scénarios multi-sites et la validation de continuité d'activité.

Le mot **HA** signifie ici *High Availability*, ou **haute disponibilité** : concevoir un service pour qu'il reste accessible malgré certaines pannes. Le cours se concentre principalement sur les réseaux d'entreprise et leurs services, tout en reliant ces concepts aux serveurs, aux applications, à l'alimentation électrique et au stockage.

> **Convention pédagogique :** les adresses des exemples sont réservées à la documentation ou aux laboratoires. Les configurations Cisco sont des modèles illustratifs ; la syntaxe et les fonctionnalités dépendent de la plate-forme. Toute modification qui affecte une passerelle, un trunk ou un protocole de routage doit être testée dans un environnement maîtrisé avant une intervention réelle.


## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- expliquer la différence entre disponibilité, redondance, tolérance aux pannes et reprise après sinistre ;
- identifier un point unique de défaillance (*Single Point of Failure*, SPOF) dans une petite architecture ;
- distinguer un fonctionnement actif/passif d'un fonctionnement actif/actif ;
- comprendre les objectifs RTO et RPO et les limites des pourcentages de disponibilité ;
- décrire les grandes familles de redondance : alimentation, liens, commutateurs, passerelles, routes et services ;
- comprendre le principe d'une passerelle virtuelle et d'un basculement HSRP ou VRRP ;
- reconnaître pourquoi LACP et STP répondent à des problèmes différents ;
- élaborer un plan de surveillance, un test de bascule et une procédure de retour arrière ;
- lire des schémas SVG de topologie et de séquence et comprendre ce qu'ils représentent ;
- vérifier une disponibilité avec des observations et des preuves plutôt qu'avec un simple ping isolé.


## 1. Comprendre la haute disponibilité

### 1.1. Disponibilité : un service doit être utilisable, pas seulement allumé

Un équipement peut être allumé tout en étant incapable de rendre le service attendu. Un routeur peut répondre à une commande de gestion mais ne plus transférer correctement les paquets. Un serveur DNS peut être en fonctionnement mais ne plus répondre aux clients. Un lien Ethernet peut afficher un état « up » alors que des erreurs, une MTU inadaptée ou une mauvaise configuration empêchent certains flux de passer.

La disponibilité se mesure donc du point de vue d'un **service défini**. Par exemple : « un utilisateur du VLAN Administration peut ouvrir une session HTTPS vers le portail interne » est une cible plus utile que « le routeur est allumé ». Une conception HA doit préciser ce qui doit rester disponible, pour qui, par quel chemin et avec quel niveau de performance acceptable.

Les services à considérer peuvent inclure :

- l'accès au réseau local ;
- la passerelle par défaut et le routage vers les autres réseaux ;
- la résolution DNS ;
- l'attribution des paramètres réseau via DHCP ou DHCPv6 ;
- l'authentification et l'autorisation ;
- les applications métier ;
- le stockage et les données ;
- la supervision et l'administration.

Si une application dépend d'un DNS unique, d'un seul commutateur d'accès et d'un seul routeur, ajouter un second serveur applicatif ne garantit pas à lui seul sa haute disponibilité. Tous les maillons nécessaires au parcours utilisateur doivent être étudiés.

### 1.2. Schéma : le service dépend d'une chaîne complète

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 220" role="img" aria-label="Le service dépend de toute la chaîne" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha1-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha1-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha1-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="218" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Le service dépend de toute la chaîne</text>
<path d="M 144 119 L 159 119" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha1-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="2.5s" repeatCount="indefinite" path="M 144 119 L 159 119" rotate="auto"/></circle>
<path d="M 291 119 L 306 119" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha1-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="2.68s" repeatCount="indefinite" path="M 291 119 L 306 119" rotate="auto"/></circle>
<path d="M 438 119 L 453 119" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha1-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="2.86s" repeatCount="indefinite" path="M 438 119 L 453 119" rotate="auto"/></circle>
<path d="M 585 119 L 600 119" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha1-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.04s" repeatCount="indefinite" path="M 585 119 L 600 119" rotate="auto"/></circle>
<path d="M 732 119 L 747 119" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha1-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2199999999999998s" repeatCount="indefinite" path="M 732 119 L 747 119" rotate="auto"/></circle>
<rect x="18" y="85" width="126" height="68" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="81.0" y="123.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Utilisateur</text>
<rect x="165" y="85" width="126" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="228.0" y="116.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Accès</text>
<text x="228.0" y="131.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">réseau</text>
<rect x="312" y="85" width="126" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="375.0" y="123.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Passerelle</text>
<rect x="459" y="85" width="126" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="522.0" y="116.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">DNS et</text>
<text x="522.0" y="131.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">services</text>
<rect x="606" y="85" width="126" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="669.0" y="116.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Répartiteur</text>
<text x="669.0" y="131.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">de charge</text>
<rect x="753" y="85" width="126" height="68" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="816.0" y="116.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Application</text>
<text x="816.0" y="131.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">et données</text>
<text x="450" y="184" fill="#94a3b8" font-size="12" text-anchor="middle">Une dépendance critique sans secours peut interrompre le service, même si les autres composants fonctionnent.</text>
</svg>
</div>

**Comment lire le schéma :** le parcours s'arrête si un composant essentiel devient indisponible et qu'aucun mécanisme de remplacement n'existe. Cette chaîne doit être examinée de bout en bout. La redondance de la passerelle ne protège pas d'une panne DNS, et la redondance d'un serveur applicatif ne corrige pas une route de retour manquante.

### 1.3. Redondance, résilience et tolérance aux pannes

La **redondance** consiste à disposer de plusieurs ressources capables d'assurer une même fonction : deux liens, deux commutateurs, deux alimentations, plusieurs serveurs ou plusieurs chemins de routage. Elle apporte une possibilité de remplacement, mais elle ne garantit pas automatiquement le bon fonctionnement.

La **résilience** désigne la capacité d'un système à encaisser une perturbation, à limiter ses effets et à retrouver un fonctionnement conforme. Cela inclut la détection, la décision de bascule, le transfert de l'activité, la surveillance et la réparation du composant défaillant.

La **tolérance aux pannes** correspond à la capacité du système à continuer à fournir le service malgré certaines défaillances. Une tolérance stricte à la panne peut exiger que l'interruption soit imperceptible pour les utilisateurs ; ce niveau coûte généralement davantage et dépend du type de charge.

La **reprise après sinistre** (*Disaster Recovery*, DR) concerne le rétablissement après un événement de grande portée : perte d'un site, incendie, corruption majeure des données ou panne durable d'une région. La HA vise souvent à gérer des défaillances courantes avec une interruption limitée ; la DR s'intéresse à la capacité de repartir depuis un autre environnement ou des sauvegardes. Les deux approches se complètent.

| Notion | Question principale | Exemple |
|---|---|---|
| Redondance | Existe-t-il un autre composant ? | Deux routeurs raccordés au même LAN |
| Basculement (*failover*) | Comment l'autre composant reprend-il le service ? | La passerelle de secours devient active |
| Résilience | Le service survit-il à la perturbation et récupère-t-il ? | La panne est détectée, la route change et l'application reste joignable |
| HA | Quelle disponibilité est fournie en fonctionnement courant ? | Portail interne encore accessible après la perte d'un routeur |
| DR | Comment rétablir le service après une perte majeure ? | Activation d'un environnement distant à partir de données répliquées |

### 1.4. Le point unique de défaillance (SPOF)

Un **SPOF** (*Single Point of Failure*) est un composant ou une dépendance dont la panne suffit à interrompre le service visé. Il ne s'agit pas forcément d'un appareil physique. Un câble commun à deux routeurs, une alimentation partagée, un seul opérateur télécom, une seule configuration DNS, un compte administrateur unique ou une mauvaise mise à jour appliquée simultanément aux deux nœuds peuvent être des SPOF.

Pour découvrir ces points, dessine le parcours d'un flux et pose systématiquement la question : « Si cet élément tombe en panne, existe-t-il un autre chemin qui fonctionne réellement ? » Vérifie ensuite si ce second chemin possède les adresses, les routes, les autorisations, la capacité et les dépendances nécessaires.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" role="img" aria-label="Identifier les points uniques de défaillance" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha2-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha2-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha2-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="298" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Identifier les points uniques de défaillance</text>
<path d="M 138 112 L 178 112" fill="none" stroke="#94a3b8" stroke-width="2.4" marker-end="url(#ha2-arrow)"/>
<circle r="4.2" fill="#94a3b8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 138 112 L 178 112" rotate="auto"/></circle>
<path d="M 298 112 L 338 112" fill="none" stroke="#94a3b8" stroke-width="2.4" marker-end="url(#ha2-arrow)"/>
<circle r="4.2" fill="#94a3b8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 298 112 L 338 112" rotate="auto"/></circle>
<path d="M 458 112 L 498 112" fill="none" stroke="#94a3b8" stroke-width="2.4" marker-end="url(#ha2-arrow)"/>
<circle r="4.2" fill="#94a3b8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 458 112 L 498 112" rotate="auto"/></circle>
<path d="M 618 112 L 658 112" fill="none" stroke="#94a3b8" stroke-width="2.4" marker-end="url(#ha2-arrow)"/>
<circle r="4.2" fill="#94a3b8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 618 112 L 658 112" rotate="auto"/></circle>
<rect x="18" y="80" width="120" height="64" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="78.0" y="116.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Client</text>
<rect x="178" y="80" width="120" height="64" rx="12" fill="#401d2a" stroke="#fb7185" stroke-width="1.5"/>
<text x="238.0" y="109.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">Switch</text>
<text x="238.0" y="124.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">unique</text>
<rect x="338" y="80" width="120" height="64" rx="12" fill="#401d2a" stroke="#fb7185" stroke-width="1.5"/>
<text x="398.0" y="109.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">Routeur</text>
<text x="398.0" y="124.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">unique</text>
<rect x="498" y="80" width="120" height="64" rx="12" fill="#401d2a" stroke="#fb7185" stroke-width="1.5"/>
<text x="558.0" y="109.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">Pare-feu</text>
<text x="558.0" y="124.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">unique</text>
<rect x="658" y="80" width="120" height="64" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="718.0" y="116.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Application</text>
<path d="M 238 145 V 204 H 449 V 222" fill="none" stroke="#fb7185" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha2-danger)"/>
<path d="M 398 145 V 190 H 449 V 222" fill="none" stroke="#fb7185" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha2-danger)"/>
<path d="M 558 145 V 204 H 449 V 222" fill="none" stroke="#fb7185" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha2-danger)"/>
<rect x="305" y="222" width="290" height="52" rx="12" fill="#401d2a" stroke="#fb7185" stroke-width="1.5"/>
<text x="450.0" y="245.0" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">Panne d’un maillon critique</text>
<text x="450.0" y="260.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">aucun chemin de remplacement</text>
</svg>
</div>

Dans cette architecture, chaque composant au milieu du chemin est un point critique. Ajouter une seconde application derrière le même pare-feu ne supprime pas le SPOF pare-feu. De même, deux routeurs reliés à un seul commutateur d'accès ne protègent pas d'une panne de ce commutateur.

### 1.5. Redondance indépendante et risque partagé

Deux équipements ne sont réellement indépendants que s'ils ne partagent pas toutes les causes possibles de panne. Deux alimentations branchées sur la même prise ou le même onduleur peuvent échouer ensemble. Deux liens optiques placés dans le même fourreau peuvent être coupés par les mêmes travaux. Deux machines virtuelles sur le même hyperviseur peuvent tomber ensemble si celui-ci échoue.

L'indépendance doit être analysée sur plusieurs couches :

- **physique :** chemin de câble, alimentation, refroidissement, baie, bâtiment ;
- **réseau :** interfaces, commutateurs, opérateurs, routeurs, chemins de retour ;
- **système :** hyperviseur, système d'exploitation, noyau, stockage ;
- **service :** DNS, authentification, certificats, configuration et secrets ;
- **exploitation :** même outil de déploiement, même compte, même erreur humaine ou changement simultané.

> **À retenir :** deux composants identiques ne constituent pas forcément deux domaines de panne. La redondance doit être vérifiée contre des causes communes, pas seulement comptée dans un inventaire.


## 2. Objectifs de disponibilité et durée d'interruption

### 2.1. Pourcentages de disponibilité

Un SLA (*Service Level Agreement*) ou un objectif interne peut être exprimé par un pourcentage de disponibilité. Un « neuf » supplémentaire réduit fortement la durée théorique d'indisponibilité autorisée, mais augmente souvent le coût, la complexité des tests et les contraintes d'exploitation.

Sur une année conventionnelle de 365 jours, sans tenir compte de règles particulières d'exclusion des maintenances :

| Objectif indicatif | Temps d'indisponibilité théorique par an |
|---|---:|
| 99 % | environ 3 jours, 15 heures et 36 minutes |
| 99,9 % | environ 8 heures et 46 minutes |
| 99,99 % | environ 52 minutes et 34 secondes |
| 99,999 % | environ 5 minutes et 15 secondes |

Ces valeurs sont des calculs théoriques. Un contrat peut traiter différemment les maintenances planifiées, les incidents partiels, les zones géographiques ou la mesure de la disponibilité. Toujours lire la méthode de mesure, le périmètre et les exclusions.

### 2.2. Calcul simple

La formule générale de disponibilité observée sur une période est :

```text
Disponibilité (%) = temps de service disponible / temps total mesuré × 100
```

Si un service a été disponible pendant 43 170 minutes sur une période de 43 200 minutes, alors :

```text
Disponibilité = 43 170 / 43 200 × 100 = 99,9305... %
Indisponibilité = 43 200 - 43 170 = 30 minutes
```

Le calcul peut être trompeur si le service n'a été mesuré que depuis un seul point. Il faut définir le nombre de sondes, les régions, les parcours utilisateur et le seuil qui constitue un échec. Une application peut réussir depuis le réseau d'administration mais être inaccessible depuis les utilisateurs.

### 2.3. MTBF, MTTR, RTO et RPO

**MTBF** (*Mean Time Between Failures*) : durée moyenne de fonctionnement entre les pannes d'un élément réparable ou d'un service, selon la méthode de calcul utilisée. C'est une mesure statistique, pas une garantie que la prochaine panne surviendra à intervalle régulier.

**MTTR** (*Mean Time To Repair* ou parfois *Restore*) : durée moyenne pour réparer ou rétablir le fonctionnement. Selon l'organisation, la définition peut inclure ou exclure le temps de diagnostic, d'attente de pièce, de restauration et de validation ; il faut donc la définir explicitement.

**RTO** (*Recovery Time Objective*) : durée maximale visée pour rétablir un service après un incident. Si le RTO est de 30 minutes, le plan doit expliquer comment restaurer le service dans cette fenêtre, et les tests doivent le démontrer.

**RPO** (*Recovery Point Objective*) : quantité de données ou période de données qu'il est acceptable de perdre, exprimée fréquemment comme une durée. Un RPO de 15 minutes suppose un mécanisme de sauvegarde ou de réplication dont l'objectif est compatible avec une perte d'au plus 15 minutes ; il ne signifie pas que la récupération elle-même prendra 15 minutes.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 250" role="img" aria-label="RTO : de la panne au service restauré" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha3-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha3-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha3-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="248" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">RTO : de la panne au service restauré</text>
<path d="M 172 130 L 188 130" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha3-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 172 130 L 188 130" rotate="auto"/></circle>
<path d="M 346 130 L 362 130" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha3-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 346 130 L 362 130" rotate="auto"/></circle>
<path d="M 520 130 L 536 130" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha3-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 520 130 L 536 130" rotate="auto"/></circle>
<path d="M 694 130 L 710 130" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha3-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 694 130 L 710 130" rotate="auto"/></circle>
<rect x="22" y="98" width="150" height="64" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="97.0" y="134.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">1. Détection</text>
<rect x="196" y="98" width="150" height="64" rx="12" fill="#3b2c17" stroke="#fbbf24" stroke-width="1.5"/>
<text x="271.0" y="134.0" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">2. Diagnostic</text>
<rect x="370" y="98" width="150" height="64" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="445.0" y="134.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">3. Bascule</text>
<rect x="544" y="98" width="150" height="64" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="619.0" y="127.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">4. Service</text>
<text x="619.0" y="142.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">rétabli</text>
<rect x="718" y="98" width="150" height="64" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="793.0" y="134.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">5. Validation</text>
<rect x="180" y="184" width="390" height="30" rx="8" fill="#312e81" stroke="#818cf8"/><text x="375" y="203" fill="#e0e7ff" font-size="12" font-weight="700" text-anchor="middle">Le RTO couvre la détection, le diagnostic et le rétablissement.</text>
</svg>
</div>

Ce schéma montre pourquoi « la redondance existe » ne suffit pas : détection et bascule font partie du temps de rétablissement. Un mécanisme automatique mal paramétré peut retarder la reprise, basculer à tort ou laisser deux nœuds actifs alors qu'un seul devait l'être.

### 2.4. Choisir un objectif cohérent avec le service

Une application de discussion interne n'a pas nécessairement les mêmes contraintes qu'un système de paiement, qu'un service de téléphonie ou qu'une plateforme de contrôle industriel. Le niveau HA doit être adapté à l'impact métier, aux obligations contractuelles, aux risques de sécurité et au coût acceptable.

Pour chaque service, documente au minimum : le propriétaire métier, les utilisateurs concernés, les périodes critiques, le seuil de panne, le RTO, le RPO lorsqu'il y a des données, les dépendances, les sondes de disponibilité, les personnes à alerter et les critères de retour à la normale.


## 3. Modèles de fonctionnement HA

### 3.1. Actif/passif

Dans une architecture **actif/passif**, un composant fournit le service pendant que l'autre reste prêt à prendre le relais. Le nœud de secours peut être chaud (déjà en fonctionnement et synchronisé), tiède (opérationnel mais avec des étapes de préparation) ou froid (nécessite un démarrage ou une restauration plus longue).

Avantages : le rôle est facile à expliquer, les risques de partage d'état peuvent être réduits lorsque le secours ne sert pas activement la charge, et certains systèmes peuvent fonctionner avec une licence ou une architecture plus simple. Inconvénients : la capacité de secours peut rester sous-utilisée ; la bascule doit être testée ; l'état des sessions et des données peut ne pas être complètement synchronisé ; le retour vers le nœud préféré mérite une procédure.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Haute disponibilité active/passive" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha4-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha4-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha4-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="328" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Haute disponibilité active/passive</text>
<path d="M 450 82 L 450 112" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha4-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 82 L 450 112" rotate="auto"/></circle>
<path d="M 450 154 L 242 192" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha4-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 154 L 242 192" rotate="auto"/></circle>
<path d="M 450 154 L 658 192" fill="none" stroke="#94a3b8" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha4-arrow)"/>
<path d="M 302 225 L 598 225" fill="none" stroke="#a78bfa" stroke-width="2.4" marker-end="url(#ha4-arrow)"/>
<circle r="4.2" fill="#a78bfa" stroke="#f8fafc" stroke-width="1"><animateMotion dur="4s" repeatCount="indefinite" path="M 302 225 L 598 225" rotate="auto"/></circle>
<text x="450" y="213" fill="#a78bfa" font-size="11" font-weight="700" text-anchor="middle">synchronisation</text>
<path d="M 650 254 C 642 282 550 287 510 258" fill="none" stroke="#fb7185" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha4-danger)"/>
<text x="600" y="292" fill="#fb7185" font-size="11" font-weight="700" text-anchor="middle">bascule après détection</text>
<rect x="365" y="42" width="170" height="42" rx="12" fill="#152f4a" stroke="#38bdf8" stroke-width="1.5"/>
<text x="450.0" y="67.0" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">Adresse / service virtuel</text>
<rect x="152" y="192" width="180" height="66" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="242.0" y="222.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Nœud A — ACTIF</text>
<text x="242.0" y="237.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">traite le trafic</text>
<rect x="568" y="192" width="180" height="66" rx="12" fill="#202938" stroke="#64748b" stroke-width="1.5"/>
<text x="658.0" y="222.0" fill="#cbd5e1" font-size="12" font-weight="700" text-anchor="middle">Nœud B — PASSIF</text>
<text x="658.0" y="237.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">prêt à reprendre</text>
<text x="450" y="315" fill="#94a3b8" font-size="11" text-anchor="middle">Le modèle exige un mécanisme d’élection, une détection fiable et une stratégie d’état.</text>
</svg>
</div>

Une adresse virtuelle ne se déplace pas toujours par le même mécanisme : elle peut être annoncée par un protocole FHRP, appartenir à un service en cluster, ou être présentée par un répartiteur de charge. Le diagramme décrit le concept, pas une implémentation unique.

### 3.2. Actif/actif

Dans un modèle **actif/actif**, plusieurs nœuds rendent simultanément le service. Cela peut améliorer l'utilisation des ressources et la capacité, mais exige souvent une répartition du trafic et une gestion des états plus complexes. Tous les services ne sont pas naturellement actifs/actifs : une application peut avoir des fichiers locaux, des sessions mémoire ou une base qui ne tolère pas des écritures concurrentes sans coordination.

Il faut distinguer :

- **répartition de charge** : distribuer les requêtes entre plusieurs ressources ;
- **haute disponibilité** : garder le service utilisable quand une ressource échoue ;
- **scalabilité** : ajouter des ressources pour supporter plus de charge ;
- **réplication** : copier des données ou un état entre ressources ;
- **quorum** : règle qui aide un ensemble de nœuds à décider quel groupe peut opérer sans créer deux autorités concurrentes.

Une architecture active/active peut également subir une panne commune du répartiteur, du DNS, du stockage ou d'une dépendance partagée. Il faut donc analyser toute la chaîne et prévoir un comportement lorsque la charge restante dépasse la capacité des nœuds encore vivants.

### 3.3. Basculement (*failover*) et retour (*failback*)

Le **failover** est le transfert du service depuis le composant en panne ou devenu impropre vers un composant qui peut poursuivre le travail. Le **failback** désigne le retour vers la ressource préférée après réparation. Le failback n'est pas forcément automatique : si le composant réparé reste instable, le retour immédiat peut provoquer une nouvelle interruption.

Un bon plan définit :

1. comment détecter l'état anormal ;
2. combien de temps ou combien d'échecs déclenchent la bascule ;
3. comment s'assurer que le secours peut vraiment servir les clients ;
4. comment éviter deux nœuds actifs quand le système exige un seul leader ;
5. comment transférer ou reconstruire l'état ;
6. comment vérifier les flux après bascule ;
7. qui décide du failback, et selon quels critères ;
8. comment revenir en arrière si la bascule échoue.

Le test ne doit pas se limiter à éteindre l'équipement. Des pannes partielles — lien d'amont cassé alors que l'interface reste active, perte de DNS, blocage du plan de contrôle ou état de réplication obsolète — sont fréquentes et peuvent être plus difficiles à détecter.

### 3.4. Split-brain : deux nœuds croient être actifs

Le **split-brain** apparaît dans certains clusters lorsque deux nœuds ou groupes séparés pensent chacun avoir l'autorité d'assurer la même fonction. Cela peut mener à des adresses dupliquées, des écritures concurrentes, des résultats divergents ou des décisions contradictoires.

Ce risque n'est pas résolu par l'ajout d'un troisième équipement au hasard. Selon le système, des mécanismes de quorum, de fencing (isoler le nœud qui ne doit plus agir), de témoin ou de consensus peuvent être nécessaires. Dans les réseaux, il faut aussi comprendre si une partition de communication est une vraie panne, une perte de lien ou un délai temporaire.

Un système doit privilégier un état sûr si l'autorité ne peut pas être déterminée. La disponibilité n'est pas l'unique objectif : continuer à écrire des données contradictoires n'est pas un succès HA.


## 4. Redonder les composants du réseau

### 4.1. Redondance physique et alimentation

Dans les petits réseaux, une panne du seul commutateur d'accès peut déconnecter tous les utilisateurs raccordés à ce commutateur. Deux commutateurs d'accès, deux alimentations ou deux liens ne sont utiles que si la topologie et les terminaux peuvent utiliser les alternatives. Certains postes possèdent une seule interface réseau ; ils ne bénéficient pas automatiquement de deux chemins sans mécanisme supplémentaire ou configuration appropriée.

Les contrôles physiques comprennent la diversité des chemins, la séparation des alimentations, les onduleurs, la capacité de refroidissement, le câblage documenté, les ports disponibles et la compatibilité des modules. Dans les datacenters ou grandes entreprises, les deux chemins doivent éviter les risques communs : même panneau de brassage, même goulotte, même alimentation ou même équipement intermédiaire.

### 4.2. Redondance des liens : LACP ne remplace pas STP

**LACP** (*Link Aggregation Control Protocol*, associé à IEEE 802.1AX) permet de regrouper plusieurs liens physiques compatibles en un agrégat logique. Cela augmente la capacité disponible pour plusieurs flux et protège contre la perte d'un membre du groupe, dans les limites de la configuration restante.

LACP ne garantit pas qu'un flux unique utilisera toute la capacité combinée : la répartition se fait habituellement selon une fonction de hachage appliquée aux caractéristiques du flux. Une mauvaise configuration des membres, une différence de VLAN autorisés ou une interface mal raccordée peut empêcher l'agrégat d'être cohérent.

**STP** empêche les boucles de couche 2 lorsque des liens redondants créent plusieurs chemins entre commutateurs. LACP et STP ont donc des buts différents. Ils peuvent être utilisés ensemble : un agrégat logique est présenté à la topologie de couche 2 comme une liaison, tandis que STP gère les chemins redondants entre les équipements.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="LACP agrège les liens ; STP contrôle les boucles" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha5-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha5-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha5-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="328" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">LACP agrège les liens ; STP contrôle les boucles</text>
<path d="M 178 135 L 355 110" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha5-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="2.6s" repeatCount="indefinite" path="M 178 135 L 355 110" rotate="auto"/></circle>
<path d="M 178 157 L 355 137" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha5-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 178 157 L 355 137" rotate="auto"/></circle>
<path d="M 505 124 L 675 137" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha5-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 505 124 L 675 137" rotate="auto"/></circle>
<path d="M 120 182 C 120 260 715 270 730 182" fill="none" stroke="#fbbf24" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha5-arrow)"/>
<text x="430" y="267" fill="#fbbf24" font-size="11" font-weight="700" text-anchor="middle">chemin alternatif géré par STP</text>
<rect x="28" y="118" width="150" height="64" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="103.0" y="154.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Switch A</text>
<rect x="355" y="88" width="150" height="64" rx="12" fill="#152f4a" stroke="#38bdf8" stroke-width="1.5"/>
<text x="430.0" y="117.0" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">Port-channel</text>
<text x="430.0" y="132.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">LACP : un lien logique</text>
<rect x="675" y="118" width="170" height="64" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="760.0" y="154.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Switch B</text>
<rect x="355" y="225" width="150" height="54" rx="12" fill="#202938" stroke="#64748b" stroke-width="1.5"/>
<text x="430.0" y="249.0" fill="#cbd5e1" font-size="12" font-weight="700" text-anchor="middle">Switch C</text>
<text x="430.0" y="264.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">autre chemin physique</text>
<text x="450" y="302" fill="#94a3b8" font-size="11" text-anchor="middle">Ne confonds pas agrégation de capacité et prévention des boucles : ce sont deux fonctions différentes.</text>
</svg>
</div>

Le dessin est conceptuel : le détail de câblage, les ports de l'agrégat et le rôle STP doivent être adaptés à la topologie. Un agrégat ne doit pas être configuré à l'aveugle entre des équipements qui ne partagent pas le même modèle de LAG ou qui ne supportent pas le même protocole.

### 4.3. Redondance de la passerelle : pourquoi une adresse virtuelle ?

Les hôtes utilisent une adresse de passerelle par défaut. Si cette passerelle est l'adresse physique d'un seul routeur et que celui-ci tombe en panne, les hôtes peuvent conserver leur configuration mais ne plus sortir de leur sous-réseau. Une fonction de redondance de premier saut peut présenter une **passerelle virtuelle** et déplacer la responsabilité du transfert vers un routeur de secours.

Les familles de protocoles courantes comprennent HSRP et GLBP dans l'écosystème Cisco et VRRP, standardisé pour IPv4 et IPv6 par l'IETF. Les détails de prise en charge et de configuration varient selon le système. Pour IPv6, la découverte normale de routeur via ICMPv6 et une fonction de redondance de premier saut ne doivent pas être confondues : VRRP fournit un mécanisme de bascule de routeur virtuel ; les RA restent une composante du fonctionnement IPv6 selon l'architecture.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" role="img" aria-label="Séquence de bascule d’une passerelle virtuelle" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha6-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha6-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha6-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Séquence de bascule d’une passerelle virtuelle</text>
<rect x="57" y="53" width="156" height="42" rx="9" fill="#172033" stroke="#475569"/><text x="135" y="78" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Client</text>
<path d="M 135 95 V 355" stroke="#475569" stroke-width="1.3" stroke-dasharray="5 6"/>
<rect x="372" y="53" width="156" height="42" rx="9" fill="#172033" stroke="#475569"/><text x="450" y="78" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Routeur A — actif</text>
<path d="M 450 95 V 355" stroke="#475569" stroke-width="1.3" stroke-dasharray="5 6"/>
<rect x="682" y="53" width="156" height="42" rx="9" fill="#172033" stroke="#475569"/><text x="760" y="78" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Routeur B — secours</text>
<path d="M 760 95 V 355" stroke="#475569" stroke-width="1.3" stroke-dasharray="5 6"/>
<path d="M 135 130 L 450 130" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha6-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 135 130 L 450 130" rotate="auto"/></circle>
<text x="292.5" y="122" fill="#38bdf8" font-size="11" font-weight="700" text-anchor="middle">Trafic vers VIP</text>
<path d="M 450 174 L 135 174" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha6-good)"/>
<text x="292.5" y="166" fill="#34d399" font-size="11" font-weight="700" text-anchor="middle">Transfert normal</text>
<path d="M 450 218 L 760 218" fill="none" stroke="#fb7185" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha6-danger)"/>
<circle r="4.2" fill="#fb7185" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 218 L 760 218" rotate="auto"/></circle>
<text x="605.0" y="210" fill="#fb7185" font-size="11" font-weight="700" text-anchor="middle">Perte / annonces absentes</text>
<path d="M 760 250 C 825 250 825 274 760 274" fill="none" stroke="#a78bfa" stroke-width="2.4" marker-end="url(#ha6-arrow)"/>
<text x="820" y="254" fill="#a78bfa" font-size="11" font-weight="700" text-anchor="middle">Le secours prend le rôle actif</text>
<path d="M 135 306 L 760 306" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha6-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 135 306 L 760 306" rotate="auto"/></circle>
<text x="447.5" y="298" fill="#38bdf8" font-size="11" font-weight="700" text-anchor="middle">Trafic vers la même VIP</text>
<path d="M 760 350 L 135 350" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha6-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 760 350 L 135 350" rotate="auto"/></circle>
<text x="447.5" y="342" fill="#34d399" font-size="11" font-weight="700" text-anchor="middle">Le transfert reprend</text>
<text x="450" y="375" fill="#94a3b8" font-size="11" text-anchor="middle">Modèle conceptuel : durée et déclencheurs exacts dépendent du protocole et de la configuration.</text>
</svg>
</div>

La durée de la perturbation dépend de la détection, des temporisateurs, de l'annonce du nouveau rôle, de la mise à jour des tables réseau et du type de flux. Une bascule ne garantit pas que les sessions existantes survivent : un pare-feu stateful ou une application qui stocke l'état local peut nécessiter une synchronisation complémentaire.

### 4.4. Exemple pédagogique HSRP sur Cisco IOS

La configuration suivante illustre deux routeurs connectés au même VLAN. Les interfaces et numéros de groupe sont des exemples ; il faut les adapter au simulateur et à l'IOS utilisé. Le réseau IPv4 `192.0.2.0/24` est destiné à la documentation, non à la production.

**Routeur R1 :**

```cisco
interface GigabitEthernet0/0
 description VLAN_UTILISATEURS
 ip address 192.0.2.2 255.255.255.0
 standby 10 ip 192.0.2.1
 standby 10 priority 110
 standby 10 preempt delay minimum 30
 standby 10 track GigabitEthernet0/1 20
 no shutdown
```

**Routeur R2 :**

```cisco
interface GigabitEthernet0/0
 description VLAN_UTILISATEURS
 ip address 192.0.2.3 255.255.255.0
 standby 10 ip 192.0.2.1
 standby 10 priority 100
 standby 10 preempt delay minimum 30
 no shutdown
```

**Vérifications possibles selon la plateforme :**

```cisco
show standby brief
show standby
show ip interface brief
show ip route
```

L'exemple décrit HSRP pour IPv4. Il ne constitue pas une configuration IPv6 complète et la syntaxe de suivi d'interface ou de préemption varie selon la version. Avant un test, vérifie la passerelle virtuelle, le rôle actif, la priorité, le suivi de l'amont et les routes de retour. N'utilise pas cet exemple directement sur un réseau de production.

### 4.5. VRRP : une référence standardisée

VRRP version 3 prend en charge IPv4 et IPv6. Il désigne un routeur actif parmi les routeurs participant à une instance et permet au routeur actif de transférer les paquets destinés à l'adresse ou aux adresses virtuelles de cette instance. En cas d'indisponibilité de l'actif, un routeur de secours peut reprendre la responsabilité.

VRRP n'est pas une solution de continuité universelle : il protège la fonction de passerelle selon son domaine d'application. Il ne synchronise pas automatiquement l'état de toutes les applications, ne garantit pas la route amont et ne supprime pas les points uniques de défaillance qui restent partagés.

Dans une conception IPv6, il faut examiner l'interaction entre l'adresse virtuelle, les annonces de routeur, les adresses link-local, les voisins, les routes, les politiques ICMPv6 et le support exact de l'équipement. Consulte la documentation du fabricant et la RFC 9568 avant de définir la procédure de bascule.


## 5. Détecter une panne et décider de la bascule

### 5.1. Les contrôles de santé

Un **health check** est un contrôle qui cherche à déterminer si un composant est apte à servir le trafic attendu. Le contrôle peut être local ou distant, passif ou actif, simple ou applicatif.

Exemples :

- état physique d'une interface ;
- perte de plusieurs sondes ICMP vers une destination ;
- établissement d'une connexion TCP sur un port ;
- requête HTTPS avec vérification d'un code de réponse ;
- test fonctionnel de la base de données ;
- délai ou taux d'erreur dépassant un seuil ;
- surveillance de l'état de réplication et de la fraîcheur des données.

Une vérification superficielle peut déclencher une fausse bascule. Par exemple, le serveur peut répondre au ping alors que l'application ne peut plus accéder à la base de données. À l'inverse, une sonde ICMP filtrée peut conclure à tort qu'un service est indisponible alors que son port applicatif fonctionne.

### 5.2. Éviter le basculement flapping

Le *flapping* est une succession de changements d'état ou de rôle qui se répètent trop souvent. Une sonde trop sensible, une latence variable ou un lien instable peut pousser le service à basculer sans cesse. Cela peut aggraver la situation : sessions interrompues, tables mises à jour constamment, alarmes bruyantes et surcharge de composants.

Les paramètres à définir incluent le seuil d'échec, le nombre de succès nécessaires pour déclarer la reprise, les temporisations, l'hystérésis, le délai de préemption et la dépendance entre plusieurs contrôles. Les valeurs doivent être testées avec des pannes réelles en laboratoire et ne pas être choisies au hasard.

Une bonne pratique est d'exiger des preuves cohérentes. Une panne du seul lien d'amont devrait être détectée même si l'interface LAN du routeur reste « up ». Inversement, la perte d'une seule sonde ou d'un hôte externe qui bloque ICMP ne devrait pas nécessairement déclencher une bascule globale si d'autres contrôles démontrent que le service demeure viable.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" role="img" aria-label="Basculement : une sonde seule ne suffit pas" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha7-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha7-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha7-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Basculement : une sonde seule ne suffit pas</text>
<path d="M 450 78 V 100" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha7-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 78 V 100" rotate="auto"/></circle>
<path d="M 450 146 V 168" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha7-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 146 V 168" rotate="auto"/></circle>
<path d="M 450 213 H 240 V 242" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha7-good)"/>
<text x="330" y="205" fill="#34d399" font-size="11" font-weight="700" text-anchor="middle">NON</text>
<path d="M 450 213 H 655 V 242" fill="none" stroke="#fbbf24" stroke-width="2.4" marker-end="url(#ha7-arrow)"/>
<text x="555" y="205" fill="#fbbf24" font-size="11" font-weight="700" text-anchor="middle">OUI</text>
<path d="M 240 288 V 316 H 450" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha7-good)"/>
<path d="M 655 288 V 316 H 450" fill="none" stroke="#fbbf24" stroke-width="2.4" marker-end="url(#ha7-arrow)"/>
<path d="M 450 316 V 337" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha7-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 316 V 337" rotate="auto"/></circle>
<rect x="335" y="38" width="230" height="40" rx="12" fill="#152f4a" stroke="#38bdf8" stroke-width="1.5"/>
<text x="450.0" y="62.0" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">Sonde de santé</text>
<rect x="335" y="100" width="230" height="46" rx="12" fill="#3b2c17" stroke="#fbbf24" stroke-width="1.5"/>
<text x="450.0" y="127.0" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">Échec confirmé ?</text>
<rect x="125" y="242" width="230" height="46" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="240.0" y="262.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Conserver le rôle</text>
<text x="240.0" y="277.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">et poursuivre les contrôles</text>
<rect x="540" y="242" width="230" height="46" rx="12" fill="#3b2c17" stroke="#fbbf24" stroke-width="1.5"/>
<text x="655.0" y="262.0" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">Compter les échecs</text>
<text x="655.0" y="277.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">appliquer délai / seuil</text>
<rect x="320" y="337" width="260" height="36" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="450.0" y="359.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Bascule approuvée + test utilisateur</text>
<text x="450" y="365" fill="#94a3b8" font-size="10" text-anchor="middle">La sonde doit représenter le service, pas uniquement l’état d’une interface.</text>
</svg>
</div>

### 5.3. Quorum, témoin et fencing

Dans les systèmes à plusieurs nœuds qui détiennent une même autorité, un **quorum** aide à décider quel groupe a le droit de continuer lorsque les membres ne peuvent plus se joindre. Un **témoin** peut fournir un vote supplémentaire selon les mécanismes du produit. Le **fencing** empêche un nœud considéré comme défaillant ou isolé de continuer à écrire ou servir, lorsque le système l'exige.

Ces mécanismes ne doivent pas être appliqués comme de simples recettes. La composition exacte du quorum dépend du nombre de nœuds, des zones de panne et de la technologie. Deux nœuds sans témoin peuvent avoir des difficultés à distinguer une panne de l'autre nœud d'une coupure réseau entre eux. Ajouter un témoin situé dans le même domaine de panne peut ne pas résoudre le risque.

Au niveau débutant, la règle est de comprendre la conséquence : un système doit éviter que deux autorités concurrentes modifient simultanément un état qui est censé être unique. Pour les clusters de stockage ou de bases de données, les procédures propres au produit sont indispensables.


## 6. Redonder les services réseau et les dépendances

### 6.1. DNS

Le DNS transforme les noms en adresses utilisées par les clients. Deux serveurs DNS ne fournissent une redondance utile que si les clients peuvent effectivement les interroger, que leurs zones sont cohérentes et que la supervision détecte les erreurs fonctionnelles. Deux adresses DNS pointant vers la même machine ou vers deux serveurs dépendant du même stockage peuvent conserver un SPOF.

Le basculement DNS n'est pas toujours instantané. Les clients, résolveurs intermédiaires et applications mettent des réponses en cache pendant la durée de vie (TTL) indiquée. Un enregistrement changé ne corrige donc pas nécessairement une session en cours. Les applications peuvent également préférer une adresse A ou AAAA selon les résultats et les règles locales.

### 6.2. DHCP et les paramètres d'accès

Un serveur DHCP indisponible peut empêcher de nouveaux clients IPv4 d'obtenir une configuration, même si les commutateurs et les routeurs continuent de transférer des paquets. Les clients possédant déjà un bail peuvent continuer à fonctionner temporairement, ce qui donne l'impression d'un réseau stable alors que les nouveaux clients échouent.

En IPv6, SLAAC, les annonces de routeur, DHCPv6 et les relais peuvent avoir des rôles différents. Une stratégie HA doit définir quelle méthode est utilisée, où se trouvent les serveurs, comment les clients apprennent leurs routes et leurs DNS et ce qui arrive si une source de configuration tombe en panne. La redondance de serveur ne résout pas une erreur commune dans les options distribuées.

### 6.3. Authentification et services d'infrastructure

Un portail ou une application peut être disponible mais inutilisable si l'authentification centralisée, le service de temps, le DNS, la PKI ou un annuaire est indisponible. La haute disponibilité doit inclure les dépendances réelles, tout en évitant de multiplier les accès de secours dangereux.

Les mécanismes de secours doivent garder les mêmes exigences de sécurité : journalisation, authentification forte, droits limités, protection des secrets et capacité de révocation. Un mode de repli qui accepte tout le monde pour préserver la disponibilité n'est pas une conception HA acceptable.

### 6.4. Matrice simple des dépendances

Avant de concevoir le basculement, remplis une matrice de dépendances. Pour chaque service, indique la ressource principale, la ressource de secours, le mécanisme de bascule, le test fonctionnel et la personne responsable.

| Service | Dépendance critique | Contrôle fonctionnel recommandé |
|---|---|---|
| Accès LAN | Commutateur, alimentation, lien | Lien opérationnel + test depuis un poste |
| Passerelle | Routeur, protocole de premier saut, amont | Rôle actif + route distante + test de service |
| DNS | Résolveur et accès réseau | Requête de nom attendue, pas seulement ping du serveur |
| DHCP / DHCPv6 | Serveur, relais, plage et options | Acquisition d'une nouvelle configuration en lab |
| Application | Répartiteur, nœuds, données, identité | Requête applicative et vérification du résultat |
| Stockage | Réplication, quorum, contrôleur, chemins | Test en lecture/écriture et intégrité |


## 7. Répartiteur de charge, cluster et réplication

### 7.1. Le rôle du répartiteur de charge

Un répartiteur de charge reçoit les requêtes d'un point d'entrée et les distribue aux serveurs disponibles selon une politique. Il peut retirer temporairement un serveur qui échoue à un contrôle de santé et envoyer les nouveaux flux vers les serveurs restants.

Le répartiteur lui-même peut devenir un SPOF s'il n'est pas redondant. La redondance peut être réalisée par un cluster, un mécanisme de bascule, une adresse virtuelle ou une solution distribuée. Mais les deux membres doivent avoir une configuration cohérente, et la capacité restante doit être suffisante si l'un tombe en panne.

Les décisions de disponibilité varient selon le type de flux : certaines applications peuvent recommencer une requête sans danger ; d'autres peuvent avoir déjà exécuté une transaction. La reprise doit tenir compte de l'idempotence, du stockage partagé, des sessions, des timeouts et de l'état maintenu localement.

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 310" role="img" aria-label="Cluster applicatif et contrôle de santé" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha8-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha8-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha8-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="308" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Cluster applicatif et contrôle de santé</text>
<path d="M 450 83 V 107" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha8-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 83 V 107" rotate="auto"/></circle>
<path d="M 450 148 L 235 183" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha8-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 148 L 235 183" rotate="auto"/></circle>
<path d="M 450 148 L 450 183" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha8-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 148 L 450 183" rotate="auto"/></circle>
<path d="M 450 148 L 665 183" fill="none" stroke="#fb7185" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha8-danger)"/>
<path d="M 235 228 L 450 250" fill="none" stroke="#a78bfa" stroke-width="2.4" marker-end="url(#ha8-arrow)"/>
<circle r="4.2" fill="#a78bfa" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 235 228 L 450 250" rotate="auto"/></circle>
<path d="M 450 228 L 450 250" fill="none" stroke="#a78bfa" stroke-width="2.4" marker-end="url(#ha8-arrow)"/>
<circle r="4.2" fill="#a78bfa" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 228 L 450 250" rotate="auto"/></circle>
<rect x="345" y="41" width="210" height="42" rx="12" fill="#152f4a" stroke="#38bdf8" stroke-width="1.5"/>
<text x="450.0" y="66.0" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">VIP / répartiteur</text>
<rect x="145" y="183" width="180" height="45" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="235.0" y="209.5" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Serveur A — sain</text>
<rect x="360" y="183" width="180" height="45" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="450.0" y="209.5" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Serveur B — sain</text>
<rect x="575" y="183" width="180" height="45" rx="12" fill="#401d2a" stroke="#fb7185" stroke-width="1.5"/>
<text x="665.0" y="209.5" fill="#ffe4e6" font-size="12" font-weight="700" text-anchor="middle">Serveur C — échec</text>
<rect x="335" y="250" width="230" height="42" rx="12" fill="#2a2346" stroke="#a78bfa" stroke-width="1.5"/>
<text x="450.0" y="268.0" fill="#ede9fe" font-size="12" font-weight="700" text-anchor="middle">Service de données</text>
<text x="450.0" y="283.0" fill="#94a3b8" font-size="10" font-weight="500" text-anchor="middle">dépendance à surveiller</text>
<text x="670" y="250" fill="#fb7185" font-size="11" text-anchor="middle">retiré du pool</text>
</svg>
</div>

Ce schéma illustre la sélection des serveurs selon leur état. Il ne signifie pas que le serveur C est physiquement débranché ; il peut simplement être exclu de la distribution. Il ne signifie pas non plus que le service de données est redondant : il faut analyser séparément le cluster ou la base.

### 7.2. Réplication et cohérence des données

La réplication permet à plusieurs ressources de détenir des copies de données ou d'un état. Les approches synchrones et asynchrones présentent des compromis différents. Dans un modèle synchrone, une opération peut attendre une confirmation distante avant d'être considérée comme terminée, au prix d'une dépendance à la latence et à la disponibilité du chemin de réplication. Dans un modèle asynchrone, les performances peuvent être meilleures mais la copie secondaire peut être en retard.

Un état de réplication « connecté » ne prouve pas que les données sont cohérentes ou assez fraîches pour le RPO visé. La supervision doit inclure le retard de réplication, les erreurs, la capacité du lien, le volume non répliqué et le comportement de reprise après coupure.

Une redondance mal testée peut reproduire immédiatement une suppression ou une corruption sur toutes les copies. Une réplication n'est donc pas une sauvegarde historique indépendante. Il faut des sauvegardes protégées et des tests de restauration, avec une politique de rétention et de contrôle d'intégrité.

### 7.3. Capacité dégradée

Une architecture HA doit préciser si le service peut rester actif à capacité réduite. Si deux nœuds supportent chacun 60 % du pic, le système peut sembler redondant mais ne pourra pas soutenir 100 % de la charge après la panne de l'un d'eux. Le dimensionnement doit tester la capacité restante pendant un incident, et pas uniquement le fonctionnement normal.

Considère également les effets de cascade : le trafic reporté vers le secours peut provoquer une surcharge qui provoque à son tour de nouvelles pannes. La limitation de débit, la mise en file d'attente, les priorités de trafic et la dégradation contrôlée peuvent aider à conserver les fonctions essentielles.


## 8. Supervision et observabilité

### 8.1. Ce qu'il faut mesurer

La supervision doit répondre à trois questions différentes : le composant est-il en fonctionnement, le service répond-il, et la qualité est-elle acceptable ? Une interface active ne prouve pas que le réseau est utilisable ; un serveur qui répond ne prouve pas que la transaction métier fonctionne.

Les indicateurs peuvent inclure :

- état des liens, erreurs physiques, pertes et changements de négociation ;
- rôle actif/veille, état du protocole FHRP et changements de rôle ;
- latence, perte de paquets, temps de résolution DNS et erreurs de connexion ;
- temps de réponse applicatif, taux d'erreur et saturation ;
- retard de réplication et fraîcheur des données ;
- consommation CPU/mémoire, files d'attente, sessions et capacité ;
- changements de configuration, échecs d'authentification et événements de sécurité.

Les sondes doivent être indépendantes autant que possible du composant testé. Une sonde hébergée sur le même serveur ne permet pas d'observer certaines pannes externes. Une supervision qui utilise uniquement le réseau d'administration peut ignorer un problème affectant le réseau utilisateur.

### 8.2. Alarmes utiles plutôt que nombreuses

Chaque alarme importante doit avoir un sens opérationnel : condition de déclenchement, priorité, propriétaire, procédure, seuil de retour à la normale et critère d'escalade. Une avalanche de messages sans action claire conduit à l'épuisement des opérateurs et à la perte de signaux importants.

Il faut distinguer un avertissement d'une panne confirmée. Une seule sonde échouée peut être un faux positif ; plusieurs observations indépendantes concordantes renforcent l'hypothèse. En revanche, une alarme qui se déclenche uniquement après plusieurs minutes peut rendre le RTO impossible à respecter. Les seuils doivent être testés.

### 8.3. Avant/après : conserver des preuves

Pendant un changement, conserve les sorties de commande, les journaux, les horodatages, les résultats de sondes et la description de l'état attendu. Après le changement, mesure les mêmes indicateurs et compare-les. Cela rend le changement vérifiable et permet de revenir en arrière si le résultat s'écarte de la cible.

Un rapport d'incident utile indique :

1. l'impact utilisateur observé ;
2. l'heure du début et la durée ;
3. les changements récents pertinents ;
4. les observations confirmées ;
5. les hypothèses non encore prouvées ;
6. la correction appliquée ;
7. la validation de retour au service ;
8. les actions préventives et leur propriétaire.


## 9. Test de bascule : la disponibilité doit être démontrée

### 9.1. Pourquoi tester ?

Un système ne devient pas hautement disponible parce qu'il possède deux composants. Le secours peut être éteint, mal configuré, désynchronisé, non supervisé ou incapable de supporter la charge. Les droits, certificats, routes et secrets peuvent avoir expiré sur le nœud secondaire sans que personne le remarque avant l'incident.

Les tests doivent être planifiés, autorisés et exécutés dans un environnement approprié. Pour une production, définir une fenêtre, un périmètre, les communications aux utilisateurs, les critères d'arrêt et une procédure de retour arrière. Évite d'effectuer une coupure improvisée pour « voir si ça marche ».

### 9.2. Plan de test en cinq phases

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 250" role="img" aria-label="Test de bascule : une procédure mesurable" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha9-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha9-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha9-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="248" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Test de bascule : une procédure mesurable</text>
<path d="M 148 129 L 158 129" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha9-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 148 129 L 158 129" rotate="auto"/></circle>
<path d="M 294 129 L 304 129" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha9-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 294 129 L 304 129" rotate="auto"/></circle>
<path d="M 440 129 L 450 129" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha9-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 440 129 L 450 129" rotate="auto"/></circle>
<path d="M 586 129 L 596 129" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha9-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 586 129 L 596 129" rotate="auto"/></circle>
<path d="M 732 129 L 742 129" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha9-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3s" repeatCount="indefinite" path="M 732 129 L 742 129" rotate="auto"/></circle>
<rect x="20" y="95" width="128" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="84.0" y="133.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">1. Préparer</text>
<rect x="166" y="95" width="128" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="230.0" y="126.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">2. État</text>
<text x="230.0" y="141.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">initial</text>
<rect x="312" y="95" width="128" height="68" rx="12" fill="#3b2c17" stroke="#fbbf24" stroke-width="1.5"/>
<text x="376.0" y="126.0" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">3. Panne</text>
<text x="376.0" y="141.0" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">contrôlée</text>
<rect x="458" y="95" width="128" height="68" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="522.0" y="126.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">4. Mesurer</text>
<text x="522.0" y="141.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">la bascule</text>
<rect x="604" y="95" width="128" height="68" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="668.0" y="133.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">5. Valider</text>
<rect x="750" y="95" width="128" height="68" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="814.0" y="126.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">6. Restaurer</text>
<text x="814.0" y="141.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">et documenter</text>
<text x="450" y="192" fill="#94a3b8" font-size="12" text-anchor="middle">Mesure au même point avant, pendant et après ; garde une condition d’arrêt et un retour arrière.</text>
</svg>
</div>

**Préparer :** identifier le composant visé et les ressources restantes. Vérifier que le plan de retour arrière est indépendant de la ressource que l'on va couper.

**Mesurer l'état initial :** noter les rôles, les routes, les liens, les sessions, les résultats applicatifs et l'heure. Vérifier que les tests passent avant la coupure.

**Provoquer une panne maîtrisée :** simuler uniquement le cas prévu, avec l'autorisation nécessaire. Commencer dans le laboratoire, pas sur un service non préparé.

**Mesurer le basculement :** relever l'heure de détection, le moment du changement de rôle et le moment où le service est à nouveau utilisable. Le délai de bascule peut différer du délai de rétablissement applicatif.

**Valider, restaurer et documenter :** tester les flux importants, vérifier les journaux et mettre fin au scénario selon la procédure. Ne termine pas le test au premier ping réussi.

### 9.3. Types de panne à prévoir

Un test de défaillance doit être précis. Des scénarios distincts comprennent :

- perte d'une interface LAN ;
- perte du lien amont seulement ;
- arrêt complet du routeur actif ;
- perte d'accès à un service DNS ;
- perte d'un membre LACP ;
- indisponibilité applicative sur un serveur encore allumé ;
- retard de réplication dépassant un seuil ;
- coupure du canal de contrôle mais maintien du plan de données ;
- retour du composant préféré après réparation.

Ces scénarios ne sont pas interchangeables. Un mécanisme qui détecte l'arrêt complet d'un appareil peut ne pas détecter la panne d'un service en amont. Il faut tester les défauts correspondant aux risques identifiés lors de la conception.

### 9.4. Exemple de fiche de test

| Champ | Exemple à renseigner |
|---|---|
| Service visé | Passerelle du VLAN utilisateurs |
| État initial | R1 actif, R2 secours, route amont valide |
| Scénario | Perte contrôlée du lien amont de R1 |
| Sonde | Requête applicative depuis un client du VLAN |
| Critère de bascule | R2 assume le rôle et le service reprend dans le délai visé |
| Critère d'arrêt | Perte simultanée de R2 ou impact sur un autre service essentiel |
| Retour arrière | Restaurer le lien, vérifier les rôles puis appliquer la stratégie de failback approuvée |
| Preuves | Horodatages, sorties `show`, captures et résultat applicatif |

Le seuil de réussite doit être fixé avant l'expérience. Si l'équipe décide du délai acceptable après avoir vu le résultat, le test ne démontre pas un objectif de disponibilité défini.


## 10. Procédure d'incident et retour arrière

### 10.1. Priorités pendant l'incident

Le premier objectif est de protéger les utilisateurs et d'éviter d'aggraver la panne. Il faut déterminer rapidement le service concerné, l'étendue de l'impact, l'heure de début et les changements récents. Évite les commandes destructives ou globales avant d'avoir collecté un minimum de preuves.

Un modèle de décision simple :

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" role="img" aria-label="Diagnostic : isoler le domaine de panne" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha10-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha10-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha10-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Diagnostic : isoler le domaine de panne</text>
<path d="M 450 75 V 96" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha10-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 75 V 96" rotate="auto"/></circle>
<path d="M 450 139 V 157" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha10-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 139 V 157" rotate="auto"/></circle>
<path d="M 450 201 L 225 231" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha10-good)"/>
<text x="326" y="208" fill="#34d399" font-size="11" font-weight="700" text-anchor="middle">LOCALE</text>
<path d="M 450 201 L 675 231" fill="none" stroke="#fbbf24" stroke-width="2.4" marker-end="url(#ha10-arrow)"/>
<text x="572" y="208" fill="#fbbf24" font-size="11" font-weight="700" text-anchor="middle">COMMUNE</text>
<path d="M 225 276 L 450 301" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha10-good)"/>
<path d="M 675 276 L 450 301" fill="none" stroke="#fbbf24" stroke-width="2.4" marker-end="url(#ha10-arrow)"/>
<path d="M 450 344 V 355" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha10-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 344 V 355" rotate="auto"/></circle>
<rect x="345" y="34" width="210" height="41" rx="12" fill="#152f4a" stroke="#38bdf8" stroke-width="1.5"/>
<text x="450.0" y="58.5" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">Incident signalé</text>
<rect x="315" y="96" width="270" height="43" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="450.0" y="121.5" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Définir le service et l’impact</text>
<rect x="340" y="157" width="220" height="44" rx="12" fill="#3b2c17" stroke="#fbbf24" stroke-width="1.5"/>
<text x="450.0" y="183.0" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">Domaine de panne ?</text>
<rect x="110" y="231" width="230" height="45" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="225.0" y="250.5" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Isoler composant</text>
<text x="225.0" y="265.5" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">ou chemin</text>
<rect x="560" y="231" width="230" height="45" rx="12" fill="#3b2c17" stroke="#fbbf24" stroke-width="1.5"/>
<text x="675.0" y="250.5" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">Examiner dépendances</text>
<text x="675.0" y="265.5" fill="#fef3c7" font-size="12" font-weight="700" text-anchor="middle">partagées</text>
<rect x="320" y="301" width="260" height="43" rx="12" fill="#2a2346" stroke="#a78bfa" stroke-width="1.5"/>
<text x="450.0" y="326.5" fill="#ede9fe" font-size="12" font-weight="700" text-anchor="middle">Correction ciblée / bascule</text>
<rect x="315" y="355" width="270" height="28" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="450.0" y="373.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">Test multi-points + compte rendu</text>
</svg>
</div>

### 10.2. Le retour arrière doit être préparé à l'avance

Une procédure de rollback doit répondre à des questions concrètes : quelle configuration restaurer, dans quel ordre, avec quel accès de secours, comment éviter un état mixte et quel test prouve le retour à la normale ? Une sauvegarde non testée ne suffit pas.

Pour les changements réseau, stocke les configurations avant/après et connais les moyens de gestion hors bande lorsque disponibles. Pour une application, la version précédente, les migrations de schéma et la compatibilité des données doivent être prises en compte. Revenir simplement au binaire précédent peut échouer si la base a déjà été modifiée de façon irréversible.

### 10.3. Ne pas confondre réparation, bascule et failback

La **réparation** remet un composant en état. Le **failover** déplace l'activité vers une ressource disponible. Le **failback** ramène l'activité vers la ressource préférée, parfois après resynchronisation. Ce sont trois opérations différentes.

Après réparation, le composant peut avoir besoin de se synchroniser, de recevoir sa configuration ou de vérifier son état de santé avant de redevenir candidat. Un retour trop rapide peut provoquer un deuxième incident. Le failback doit être inclus dans les tests HA dès la phase de conception.


## 11. Laboratoire 1 — Cartographier les SPOF

**Objectif :** apprendre à transformer une topologie en parcours de service et à détecter les points de défaillance uniques.

**Matériel :** un dessin de réseau réel simplifié ou la topologie Packet Tracer de ton choix. Il est possible de faire ce laboratoire sans équipement en utilisant le diagramme fourni.

### Étapes

1. Dessine le chemin d'un poste utilisateur vers une application importante.
2. Ajoute les dépendances DNS, passerelle, pare-feu, authentification et stockage si elles sont nécessaires.
3. Pour chaque élément, imagine une panne complète et une panne partielle.
4. Indique si une ressource de remplacement existe réellement et si elle est indépendante.
5. Attribue un propriétaire et un test de disponibilité pour chaque composant critique.
6. Classe les SPOF par impact et facilité de réduction.

**Livrable :** une topologie annotée, une liste des SPOF et trois actions de réduction du risque classées par priorité.

**Critère de réussite :** chaque service critique doit avoir un parcours documenté, ses dépendances et un test vérifiable. Il ne suffit pas d'écrire « deux serveurs » sans expliquer leur point d'entrée, leurs données et leurs dépendances communes.


## 12. Laboratoire 2 — Passerelle redondante dans une maquette

**Objectif :** comprendre l'effet d'une passerelle virtuelle et mesurer la différence entre bascule du rôle et rétablissement applicatif.

### Topologie logique

<div class="lesson-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" role="img" aria-label="Redondance de passerelle" style="width:100%;height:auto;font-family:Arial,Helvetica,sans-serif">
<defs><marker id="ha11-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker><marker id="ha11-danger" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker><marker id="ha11-good" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
<rect x="1" y="1" width="898" height="298" rx="16" fill="#0b1220" stroke="#334155"/>
<text x="24" y="29" fill="#e2e8f0" font-size="17" font-weight="700">Redondance de passerelle</text>
<path d="M 450 95 V 121" fill="none" stroke="#38bdf8" stroke-width="2.4" marker-end="url(#ha11-arrow)"/>
<circle r="4.2" fill="#38bdf8" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 95 V 121" rotate="auto"/></circle>
<path d="M 450 163 L 265 202" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha11-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 450 163 L 265 202" rotate="auto"/></circle>
<path d="M 450 163 L 635 202" fill="none" stroke="#94a3b8" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha11-arrow)"/>
<path d="M 265 248 L 450 269" fill="none" stroke="#34d399" stroke-width="2.4" marker-end="url(#ha11-good)"/>
<circle r="4.2" fill="#34d399" stroke="#f8fafc" stroke-width="1"><animateMotion dur="3.2s" repeatCount="indefinite" path="M 265 248 L 450 269" rotate="auto"/></circle>
<path d="M 635 248 L 450 269" fill="none" stroke="#94a3b8" stroke-width="2.4" stroke-dasharray="7 6" marker-end="url(#ha11-arrow)"/>
<rect x="345" y="48" width="210" height="47" rx="12" fill="#152f4a" stroke="#38bdf8" stroke-width="1.5"/>
<text x="450.0" y="75.5" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">PC utilisateur</text>
<rect x="345" y="121" width="210" height="42" rx="12" fill="#172033" stroke="#475569" stroke-width="1.5"/>
<text x="450.0" y="146.0" fill="#e2e8f0" font-size="12" font-weight="700" text-anchor="middle">Switch de couche 2</text>
<rect x="175" y="202" width="180" height="46" rx="12" fill="#10352f" stroke="#34d399" stroke-width="1.5"/>
<text x="265.0" y="229.0" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">R1 — prioritaire</text>
<rect x="545" y="202" width="180" height="46" rx="12" fill="#202938" stroke="#64748b" stroke-width="1.5"/>
<text x="635.0" y="229.0" fill="#cbd5e1" font-size="12" font-weight="700" text-anchor="middle">R2 — secours</text>
<rect x="340" y="269" width="220" height="24" rx="12" fill="#2a2346" stroke="#a78bfa" stroke-width="1.5"/>
<text x="450.0" y="285.0" fill="#ede9fe" font-size="12" font-weight="700" text-anchor="middle">Réseau amont</text>
<text x="450" y="290" fill="#94a3b8" font-size="10" text-anchor="middle">La passerelle virtuelle doit rester la même pour les clients lors de la bascule.</text>
</svg>
</div>

### Étapes

1. Dans Packet Tracer ou une maquette Cisco compatible, configure un LAN et deux routeurs comme dans le guide de la plate-forme.
2. Définis l'adresse de passerelle virtuelle et vérifie le rôle actif et le rôle de secours avec les commandes adaptées.
3. Depuis un PC, teste la passerelle et un service de destination stable.
4. En laboratoire, provoque une panne contrôlée prévue par le scénario.
5. Note l'heure du défaut, le changement de rôle et la première réussite complète du service.
6. Rétablis l'état du laboratoire, vérifie le failback et documente les différences.

**Limite :** Packet Tracer ne reproduit pas toutes les fonctionnalités de chaque équipement réel. Si le simulateur ne prend pas en charge la commande ou le comportement voulu, consigne la limite et utilise une maquette compatible ; ne conclus pas que le protocole réel fonctionne exactement comme le simulateur.

**Livrable :** table avant/pendant/après, commandes de vérification, durée de bascule mesurée, résultat d'un test applicatif et procédure de rollback.


## 13. Laboratoire 3 — Redondance de liens : LACP et STP

**Objectif :** expliquer quelle panne LACP peut absorber et à quoi sert STP dans la topologie.

### Étapes

1. Dessine deux commutateurs reliés par deux liens physiques destinés à former un agrégat.
2. Vérifie que les deux extrémités utilisent des paramètres compatibles : même groupe, mode LACP, vitesse/duplex et politiques de couche 2 conformes à la plate-forme.
3. Contrôle que l'agrégat est formé et que les membres sont opérationnels.
4. Teste la connectivité depuis un poste situé derrière chaque commutateur.
5. Dans un laboratoire, coupe un membre de l'agrégat et observe si le trafic reste disponible ; mesure la capacité restante.
6. Examine séparément le rôle STP lorsqu'une autre liaison redondante existe dans la topologie.
7. Restaure l'ensemble et confirme l'absence d'erreurs persistantes.

**Question clé :** pourquoi la présence de deux câbles n'implique-t-elle pas automatiquement une protection contre toutes les boucles ?

**Réponse attendue :** les liens doivent être regroupés ou organisés de manière cohérente. LACP forme un agrégat lorsque ses conditions sont satisfaites ; STP gère les chemins redondants de couche 2. Une configuration incompatible peut entraîner des ports non membres, une boucle ou une interruption.


## 14. Laboratoire 4 — Test de santé trop simple

**Objectif :** démontrer qu'un ping ne suffit pas toujours pour juger si un service est disponible.

### Scénario

Un serveur répond au ping, mais le portail HTTPS qu'il héberge renvoie une erreur parce que l'application ne peut plus joindre sa base de données.

### Étapes

1. Écris les contrôles disponibles : ping, port TCP, requête HTTPS, vérification métier et état de la dépendance.
2. Pour chaque contrôle, indique ce qu'un succès prouve et ce qu'il ne prouve pas.
3. Définis une sonde applicative qui valide le parcours réel sans effectuer d'action dangereuse.
4. Propose une stratégie de retrait du serveur du répartiteur lorsqu'il est allumé mais incapable de servir correctement.
5. Définis les protections contre une fausse bascule et les exigences pour déclarer le rétablissement.

**Livrable :** matrice des sondes, seuils proposés, action de bascule et critère de validation. Les seuils sont des choix à tester, pas des valeurs universelles.


## 15. Laboratoire 5 — RTO, RPO et capacité de secours

**Objectif :** traduire des objectifs métier en contraintes de conception vérifiables.

Une entreprise veut garder accessible une application de gestion pendant les pannes courantes. Elle demande un RTO de 20 minutes, un RPO de 5 minutes et une capacité suffisante pour servir 100 % des utilisateurs pendant la perte d'un nœud.

### Travail à réaliser

1. Liste les composants dont la panne peut interrompre le parcours utilisateur.
2. Pour chaque dépendance, indique le mécanisme de secours et le temps estimé à mesurer.
3. Vérifie si le temps de détection, de bascule, de reconstruction et de validation tient dans le RTO.
4. Vérifie si la stratégie de sauvegarde ou de réplication est compatible avec le RPO, puis précise comment le prouver.
5. Calcule la capacité nécessaire après perte d'un nœud.
6. Défini un test de panne et une méthode de mesure indépendante.
7. Rédige le risque restant et la décision que doit prendre le propriétaire métier.

**Attention :** le RTO et le RPO sont des objectifs. Ils ne prouvent rien sans tests, données de mesure et processus de reprise documenté.


## 16. Laboratoire 6 — Incident multi-cause

**Objectif :** appliquer une méthode d'analyse sans changer plusieurs variables au hasard.

### Symptômes observés

- certains postes accèdent encore au réseau local ;
- de nouveaux postes ne reçoivent plus leur configuration ;
- le serveur applicatif répond au ping depuis le VLAN d'administration, mais les utilisateurs ne peuvent pas ouvrir de session ;
- le routeur principal est toujours allumé ;
- la supervision indique des pertes intermittentes sur le lien amont.

### Démarche

1. Sépare les symptômes par service : DHCP, passerelle, routage, application et supervision.
2. Collecte les horodatages et les changements récents.
3. Vérifie si une panne commune explique plusieurs symptômes ou si plusieurs problèmes indépendants existent.
4. Contrôle la connectivité au service DHCP depuis le parcours de relais, et pas uniquement le serveur lui-même.
5. Vérifie le rôle de la passerelle et son état d'amont ; n'assimile pas un routeur allumé à une passerelle pleinement opérationnelle.
6. Compare les résultats de test depuis plusieurs points du réseau.
7. Formule deux hypothèses, puis choisis un test qui permet de les départager.
8. N'applique qu'une correction à la fois ; vérifie le service et prépare un rollback.

**Livrable :** une chronologie, les preuves disponibles, les hypothèses rejetées, la cause confirmée ou encore incertaine et la validation du rétablissement.


## 17. Modèles de documents d'exploitation

### 17.1. Inventaire HA

| Champ | Description |
|---|---|
| Service | Nom compréhensible par les utilisateurs |
| Propriétaire | Équipe responsable de son fonctionnement |
| Dépendances | Réseau, DNS, authentification, données, stockage |
| Ressource primaire | Composant qui rend le service en fonctionnement normal |
| Secours | Ressource ou chemin de remplacement |
| Détection | Sonde et conditions d'alerte |
| Bascule | Déclencheur, délai, commande ou automatisme |
| RTO / RPO | Objectifs métier définis |
| Test réalisé | Date, périmètre, résultat mesuré |
| Retour arrière | Conditions et procédure de restauration |

### 17.2. Fiche de changement

```text
CHANGEMENT HA
Service concerné :
Motif :
Risque évalué :
Équipements et liens touchés :
État initial enregistré :
Sauvegarde disponible et vérifiée :
Fenêtre approuvée :
Étapes d'exécution :
Critères de réussite mesurables :
Conditions d'arrêt :
Plan de retour arrière :
Personne qui valide le service :
Résultats et preuves après le changement :
```

### 17.3. Rapport d'incident

Un bon rapport sépare les faits des hypothèses. Il ne doit pas transformer une corrélation temporelle en cause certaine. Par exemple, « le trafic a repris après le redémarrage » ne prouve pas que le redémarrage est la correction définitive. La preuve doit établir le mécanisme qui a échoué, le lien entre ce mécanisme et les symptômes, et le résultat obtenu après correction.

Le rapport doit inclure l'impact, l'heure de début, les composants impliqués, la durée, la cause confirmée ou les incertitudes restantes, les actions effectuées, les risques introduits, le rétablissement validé et les actions préventives avec responsables.


## 18. Exercices d'auto-évaluation avec corrigés

### Question 1

**Pourquoi deux routeurs raccordés au même switch d'accès ne constituent-ils pas une architecture entièrement redondante ?**

**Corrigé :** le switch d'accès demeure un SPOF pour les hôtes raccordés à lui. La redondance des routeurs n'aide pas si les clients perdent le lien vers les deux routeurs à cause de la panne du switch.

### Question 2

**Quelle différence y a-t-il entre failover et failback ?**

**Corrigé :** le failover transfère l'activité de la ressource défaillante vers une ressource de secours ; le failback ramène l'activité vers la ressource préférée après réparation et validation. Le second doit être planifié et testé séparément.

### Question 3

**Un serveur répond au ping mais le site Web ne fonctionne pas. Est-il disponible ?**

**Corrigé :** le serveur est joignable au niveau testé, mais le service Web peut rester indisponible. Il faut une sonde adaptée au port et à l'application, éventuellement à une dépendance comme l'authentification ou la base de données.

### Question 4

**LACP et STP ont-ils la même fonction ?**

**Corrigé :** non. LACP négocie l'agrégation de liens physiques compatibles en une liaison logique ; STP empêche les boucles en sélectionnant une topologie de transfert sans boucle parmi les chemins disponibles.

### Question 5

**Deux alimentations suffisent-elles à éliminer le risque d'alimentation ?**

**Corrigé :** non si elles sont alimentées par la même source unique, le même onduleur non redondant ou un circuit commun susceptible de tomber en panne. Il faut examiner les domaines de panne et l'état de l'alimentation réelle.

### Question 6

**Un objectif de disponibilité de 99,99 % garantit-il que toute panne dure moins de 52 minutes ?**

**Corrigé :** non. Il s'agit d'une moyenne ou d'un budget calculé sur une période selon une méthode donnée. Une seule panne peut durer plus longtemps ; le pourcentage ne définit pas à lui seul la durée maximale d'un incident individuel.

### Question 7

**Pourquoi une bascule automatique peut-elle empirer une situation ?**

**Corrigé :** la sonde peut déclencher sur un faux positif, les deux nœuds peuvent perdre la cohérence, le secours peut être surchargé ou le changement de rôle peut créer un flapping. Les seuils, l'hystérésis, l'état du secours et les règles de quorum doivent être conçus et testés.

### Question 8

**Une réplication est-elle équivalente à une sauvegarde ?**

**Corrigé :** non. La réplication peut propager une suppression ou une corruption. Une sauvegarde historique indépendante et un test de restauration sont nécessaires pour certains scénarios de reprise.

### Question 9

**Quelle mesure démontre le RTO ?**

**Corrigé :** une mesure horodatée depuis le début défini de l'incident jusqu'au rétablissement validé du service selon le test prévu. Il faut préciser quand la mesure commence et quel test marque le retour effectif du service.

### Question 10

**Pourquoi tester le failback après avoir réussi le failover ?**

**Corrigé :** le retour de la ressource préférée peut provoquer une nouvelle interruption ou réintroduire un nœud qui n'est pas encore synchronisé. La procédure de retour fait partie du cycle complet de disponibilité.

### Question 11

**Quel risque existe dans un cluster qui laisse deux nœuds agir comme autorité après une partition du réseau ?**

**Corrigé :** un split-brain, pouvant causer des écritures concurrentes, des états divergents ou des conflits d'adresse. Le système doit définir une règle d'autorité, un quorum ou une autre protection adaptée au produit.

### Question 12

**Quel est l'intérêt d'une sonde depuis un vrai client utilisateur ?**

**Corrigé :** elle valide une plus grande partie du parcours réel — accès, routage, DNS, filtrage et service — là où une sonde locale peut ignorer une dépendance ou un problème de chemin.


## 19. Fiche de révision rapide

- La haute disponibilité s'évalue sur un **service défini**, pas uniquement sur l'état « up » des équipements.
- La redondance n'est utile que si le secours est indépendant, correctement configuré et capable de servir la charge.
- Le SPOF peut être matériel, réseau, logiciel, énergétique, humain ou lié à une dépendance partagée.
- Le failover et le failback sont deux opérations distinctes qui doivent être testées.
- LACP protège les membres d'un agrégat ; STP contrôle les chemins redondants de couche 2.
- HSRP, VRRP et d'autres mécanismes de premier saut peuvent protéger le rôle de passerelle, mais ne remplacent pas le routage, le DNS ou la redondance applicative.
- Un contrôle de santé doit mesurer ce qui importe au service. Un ping seul n'est généralement pas suffisant pour une application complexe.
- RTO et RPO sont des objectifs mesurables à associer à une procédure testée.
- La réplication n'est pas une sauvegarde indépendante.
- Les alarmes, les journaux, les sondes et les tests doivent être assez indépendants pour fournir des preuves utiles.
- Ne provoque pas une panne en production sans autorisation, fenêtre, critères d'arrêt et retour arrière.
- Après chaque bascule, valide le parcours utilisateur, les dépendances et la capacité restante avant de déclarer le service rétabli.


## 20. Glossaire

| Terme | Définition |
|---|---|
| Actif/actif | Modèle dans lequel plusieurs nœuds fournissent simultanément le service |
| Actif/passif | Modèle dans lequel un nœud actif est assisté par un nœud de secours |
| Bascule / failover | Transfert de l'activité vers une ressource alternative |
| Failback | Retour de l'activité vers la ressource préférée après réparation et validation |
| FHRP | Famille de protocoles de redondance de premier saut |
| HA | Haute disponibilité (*High Availability*) |
| Health check | Contrôle qui vérifie si une ressource est apte à fournir le service |
| LACP | Protocole de négociation d'agrégation de liens |
| MTBF | Durée moyenne entre pannes selon une méthode définie |
| MTTR | Durée moyenne de réparation ou de rétablissement selon une méthode définie |
| Quorum | Règle de décision permettant à un ensemble de nœuds de déterminer quel groupe peut opérer |
| RPO | Objectif de point de reprise : quantité ou durée de données qu'il est acceptable de perdre |
| RTO | Objectif de durée de reprise après une panne |
| Réplication | Copie d'un état ou de données vers une autre ressource |
| SLA | Engagement ou objectif de niveau de service |
| Split-brain | Situation où plusieurs groupes croient avoir autorité simultanément |
| SPOF | Point unique de défaillance |
| STP | Protocole de prévention des boucles de couche 2 |
| Témoin | Ressource de vote ou d'arbitrage utilisée par certains clusters |


## 21. Références techniques

Les références suivantes permettent d'approfondir les standards et d'adapter les exemples à l'équipement réel. Elles ne signifient pas que chaque routeur ou commutateur prend en charge toutes les fonctionnalités décrites.

- **IETF — RFC 9568, Virtual Router Redundancy Protocol Version 3 for IPv4 and IPv6** : https://www.rfc-editor.org/rfc/rfc9568.html
- **IEEE — IEEE 802.1AX, Link Aggregation** : https://standards.ieee.org/ieee/802.1AX/6768/
- **Cisco — HSRP configuration / documentation IOS XE** : https://www.cisco.com/c/en/us/support/docs/ip/hot-standby-router-protocol-hsrp/9234-hsrpguidetoc.html
- **Cisco — EtherChannel / LACP configuration** : https://www.cisco.com/c/en/us/support/docs/lan-switching/etherchannel/12023-4.html
- **Cisco — STP configuration guide** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/stp/stp-configuration-guide/m-stp.html

La version logicielle, les limitations de la plate-forme et le contexte de déploiement déterminent la syntaxe réellement utilisable. Les schémas de ce cours sont conceptuels et ne remplacent ni une configuration validée, ni un test de bascule, ni la documentation du constructeur.


## Conclusion — Les fondations de la haute disponibilité

La haute disponibilité est une propriété démontrée par l'architecture, la supervision et les tests, pas une étiquette ajoutée à un équipement. La redondance permet de disposer d'alternatives ; la détection et le failover les activent ; l'observabilité prouve le résultat ; le failback et les procédures de changement permettent de maintenir un état cohérent sur la durée.

Le prochain niveau, `ha-intermediaire.md`, devra s'appuyer sur ces acquis pour concevoir des architectures plus complexes : redondance de passerelles avec suivi d'amont, routage dynamique et convergence, clusters stateful, réplication, gestion du quorum, diversité physique et plans de test reproductibles.
