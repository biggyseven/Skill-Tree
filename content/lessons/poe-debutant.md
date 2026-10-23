# PoE — Débutant
## Comprendre l'alimentation électrique par Ethernet

**Niveau :** Débutant  
**Prérequis :** connaissances élémentaires des réseaux Ethernet et du rôle d'un switch.  
**Objectif général :** comprendre comment un équipement réseau reçoit de l'énergie électrique par Ethernet, identifier les équipements compatibles et réaliser un premier diagnostic.

---

## Objectifs pédagogiques

À la fin de ce cours, tu dois être capable de :

- expliquer le principe du Power over Ethernet ;
- distinguer le PSE du PD ;
- comprendre les grandes étapes précédant l'alimentation d'un appareil ;
- différencier puissance électrique et débit Ethernet ;
- reconnaître les principaux standards PoE ;
- expliquer la différence entre puissance disponible, puissance réservée et consommation mesurée ;
- diagnostiquer un premier problème d'alimentation ;
- respecter les précautions essentielles lors d'une installation PoE.

---

# 1. Pourquoi le PoE existe-t-il ?

Dans un réseau traditionnel, un appareil peut nécessiter deux connexions différentes.

La première est une connexion réseau, généralement assurée par un câble Ethernet. Elle permet à l'équipement d'envoyer et de recevoir des informations.

La seconde est une connexion électrique. Elle peut être assurée par un adaptateur secteur raccordé à une prise murale.

Prenons l'exemple d'une caméra de surveillance installée au plafond. Pour fonctionner, elle doit recevoir les données du réseau et disposer d'une alimentation. Sans PoE, l'installation peut nécessiter un câble Ethernet et un adaptateur secteur à proximité de la caméra.

Le **Power over Ethernet (PoE)** permet de transporter les données et l'énergie électrique à travers une même liaison Ethernet compatible.

Cette technologie est utilisée notamment pour :

- les téléphones IP ;
- les caméras réseau ;
- les points d'accès Wi-Fi ;
- les interphones réseau ;
- certains équipements de contrôle d'accès ;
- des capteurs et équipements industriels compatibles.

Le principal avantage est la simplification du raccordement. Il est possible de centraliser une partie de l'alimentation au niveau des switches et de gérer certains aspects de l'alimentation depuis l'infrastructure réseau.

Le PoE ne supprime toutefois pas le besoin d'une source électrique. Le switch doit recevoir de l'énergie et disposer d'une capacité suffisante pour alimenter les équipements qui lui sont raccordés.

## 1.1 Installation classique et installation PoE

Sans PoE :

```text
                    Câble Ethernet
Switch réseau ───────────────────────── Caméra IP
                                            │
                                            │ Adaptateur secteur
                                            │
                                       Prise électrique
```

Avec une liaison PoE compatible :

```text
Switch PoE ───────── Câble Ethernet ───────── Caméra IP
```

La deuxième installation peut être plus simple, notamment lorsque la caméra est éloignée d'une prise électrique.

Il faut cependant vérifier les caractéristiques de la caméra et du switch avant l'installation. La présence d'un connecteur RJ45 aux deux extrémités ne suffit pas à établir la compatibilité électrique.

## 1.2 Les avantages et les limites

Le PoE apporte plusieurs avantages :

**Centralisation de l'alimentation.** Les équipements peuvent recevoir leur énergie depuis les switches ou injecteurs prévus à cet effet.

**Souplesse d'installation.** Il est souvent plus simple de déplacer un équipement si le nouveau point dispose d'un câble Ethernet adapté et d'une couverture réseau appropriée.

**Administration facilitée.** Selon le matériel, l'administrateur peut observer l'état PoE des ports et commander certaines opérations d'alimentation à distance.

**Réduction des adaptateurs locaux.** Un adaptateur secteur individuel peut devenir inutile si le PD est compatible et si la puissance reçue est suffisante.

Il existe aussi des limites :

- le switch doit disposer d'un budget PoE suffisant ;
- un port peut avoir une limite de puissance inférieure à celle dont le PD a besoin ;
- une panne du switch peut affecter simultanément plusieurs appareils ;
- le câblage doit être adapté aux conditions électriques ;
- un mauvais choix de matériel ou une mauvaise configuration peut provoquer un refus d'alimentation.

---

# 2. Les deux rôles fondamentaux : PSE et PD

Il existe deux termes essentiels à connaître avant d'étudier les standards.

## 2.1 PSE : Power Sourcing Equipment

Le **PSE** est l'équipement qui fournit l'énergie électrique sur la liaison PoE.

Les exemples courants sont :

- un switch Ethernet muni de ports PoE ;
- un injecteur PoE compatible ;
- un équipement réseau conçu pour fournir de l'alimentation à un autre équipement.

Tous les switches ne fournissent pas nécessairement du PoE. Certains modèles possèdent uniquement des interfaces de données.

Même lorsqu'un switch prend en charge le PoE, tous ses ports ne disposent pas nécessairement des mêmes capacités. Il faut consulter les caractéristiques précises du matériel.

## 2.2 PD : Powered Device

Le **PD** est l'appareil qui reçoit l'énergie électrique.

Par exemple :

- un téléphone IP ;
- une caméra IP ;
- un point d'accès Wi-Fi ;
- un terminal de contrôle d'accès ;
- un appareil industriel compatible.

Le PD doit être conçu pour recevoir l'alimentation selon un standard et un niveau de puissance compatibles. Il faut donc consulter sa fiche technique avant de le raccorder.

## 2.3 Relation entre le PSE et le PD

```text
        PSE                                      PD
  ┌──────────────┐                        ┌──────────────┐
  │  Switch PoE  │ ─── Ethernet + PoE ──> │  Caméra IP   │
  │              │                        │              │
  │ Fournit      │                        │ Reçoit       │
  │ l'énergie    │                        │ l'énergie    │
  └──────────────┘                        └──────────────┘
```

Le PSE est la source de puissance. Le PD est le récepteur.

Le câble Ethernet relie les deux appareils, mais le fonctionnement dépend aussi des mécanismes de détection et d'alimentation, de la compatibilité des équipements et de la disponibilité de puissance.

---

# 3. Schéma animé — Une liaison Ethernet transporte les données et l'énergie

Les deux lignes animées permettent de distinguer visuellement les fonctions transportées. Elles constituent une représentation pédagogique du fonctionnement, et non une simulation de la vitesse réelle des données ou du déplacement des électrons.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 310" role="img" aria-labelledby="poeb1-title">
<title id="poeb1-title">Liaison entre un switch PoE et une caméra réseau</title>
<defs><style>
.poeb1-bg{fill:#101827}.poeb1-card{fill:#1d304b;stroke:#527097;stroke-width:2}.poeb1-h{fill:#f8fafc;font:700 17px Arial,sans-serif}.poeb1-t{fill:#d3deec;font:13px Arial,sans-serif}.poeb1-data{fill:none;stroke:#59baff;stroke-width:4;stroke-dasharray:10 9;animation:poeb1-dash 1.15s linear infinite}.poeb1-power{fill:none;stroke:#ffca6a;stroke-width:4;stroke-dasharray:6 10}.poeb1-status{fill:#4ade80}.poeb1-caption{fill:#aabbd0;font:11px Arial,sans-serif}@keyframes poeb1-dash{to{stroke-dashoffset:-38}}@media(prefers-reduced-motion:reduce){.poeb1-data{animation:none}}
</style></defs>
<rect class="poeb1-bg" width="900" height="310" rx="18"/>
<text class="poeb1-h" x="450" y="33" text-anchor="middle">Deux fonctions, une liaison Ethernet</text>
<rect class="poeb1-card" x="35" y="78" width="195" height="145" rx="12"/>
<text class="poeb1-h" x="132" y="108" text-anchor="middle">Switch PoE</text>
<rect x="72" y="124" width="120" height="36" rx="5" fill="#0c1422" stroke="#7188a8"/>
<g fill="#59baff"><rect x="84" y="135" width="15" height="8" rx="2"/><rect x="105" y="135" width="15" height="8" rx="2"/><rect x="126" y="135" width="15" height="8" rx="2"/><rect x="147" y="135" width="15" height="8" rx="2"/></g>
<circle class="poeb1-status" cx="85" cy="181" r="5"><animate attributeName="opacity" values=".35;1;.35" dur="1.6s" repeatCount="indefinite"/></circle>
<text class="poeb1-t" x="132" y="185" text-anchor="middle">PSE : source</text>
<text class="poeb1-caption" x="132" y="203" text-anchor="middle">Données + énergie</text>
<rect x="264" y="101" width="370" height="98" rx="10" fill="#0b1422" stroke="#415775"/>
<text class="poeb1-t" x="449" y="91" text-anchor="middle">Câble Ethernet compatible</text>
<path class="poeb1-data" d="M230 132 H670"/>
<path class="poeb1-power" d="M230 171 H670"><animate attributeName="stroke-dashoffset" from="0" to="-40" dur="1.05s" repeatCount="indefinite"/></path>
<text x="449" y="124" fill="#9bd7ff" font-size="11" text-anchor="middle">TRANSPORT DES DONNÉES</text>
<text x="449" y="163" fill="#ffe0a0" font-size="11" text-anchor="middle">TRANSFERT D'ÉNERGIE</text>
<rect class="poeb1-card" x="670" y="78" width="195" height="145" rx="12"/>
<text class="poeb1-h" x="767" y="108" text-anchor="middle">Caméra IP</text>
<path d="M730 132 H793 L810 147 V169 H730 Z" fill="#0c1422" stroke="#a8bedb" stroke-width="2"/>
<circle cx="764" cy="150" r="12" fill="#203e61" stroke="#59baff" stroke-width="3"/>
<circle cx="764" cy="150" r="5" fill="#59baff"><animate attributeName="r" values="3;6;3" dur="1.4s" repeatCount="indefinite"/></circle>
<circle class="poeb1-status" cx="730" cy="190" r="5"><animate attributeName="opacity" values=".3;1;.3" dur="1.4s" repeatCount="indefinite"/></circle>
<text class="poeb1-t" x="781" y="194" text-anchor="middle">PD : récepteur</text>
<text class="poeb1-caption" x="450" y="258" text-anchor="middle">Le PSE doit reconnaître le PD et respecter les limites électriques applicables.</text>
<text class="poeb1-caption" x="450" y="278" text-anchor="middle">Les tirets animés illustrent le flux : ils ne représentent pas la vitesse réelle des données.</text>
</svg>

---

# 4. Le rôle du câble Ethernet

Le câblage ne sert pas uniquement à transmettre des informations. Dans une liaison PoE, il fait aussi partie du chemin électrique.

La qualité des conducteurs, les terminaisons, la longueur de la liaison et l'état des connecteurs sont donc importants.

## 4.1 La résistance du câble

Les conducteurs présentent une résistance électrique. Lorsqu'un courant les traverse, une partie de l'énergie est dissipée sous forme de chaleur.

Cette perte explique pourquoi la puissance délivrée par le PSE n'est pas exactement identique à la puissance disponible à l'entrée du PD.

Les défauts suivants doivent attirer l'attention :
- conducteur endommagé ;
- connecteur mal serti ;
- contact de mauvaise qualité ;
- câble écrasé ou détérioré ;
- installation qui ne respecte pas les exigences du câblage ;
- faisceau de câbles soumis à des conditions thermiques inadaptées.

Un câble peut parfois permettre une liaison Ethernet tout en présentant un défaut affectant la fiabilité de l'alimentation. Il ne faut donc pas s'appuyer uniquement sur le voyant de lien pour déclarer une installation correcte.

## 4.2 Contrôles de base

Avant de remplacer le switch, effectuer les vérifications non destructives suivantes :

1. vérifier que le câble est adapté à l'installation ;
2. inspecter les terminaisons et les connecteurs ;
3. contrôler l'état du port ;
4. effectuer un test avec un câble connu comme fonctionnel ;
5. confirmer les capacités du PSE et du PD ;
6. examiner les événements du switch si le matériel les expose.

Ne manipule pas des conducteurs nus ou une source électrique inconnue pour essayer de déterminer si un câble fournit du PoE.

---

# 5. PoE standardisé et PoE passif

L'apparence physique du connecteur ne suffit pas pour établir la compatibilité entre une source électrique et un appareil.

## 5.1 PoE standardisé

Le PoE défini par l'IEEE inclut des mécanismes de détection, de classification et d'alimentation.

Le PSE recherche les caractéristiques électriques attendues d'un PD compatible. Il applique ensuite les procédures correspondant au type de PoE et aux capacités des appareils.

Cette méthode réduit les risques d'alimenter un appareil non prévu pour recevoir l'énergie PoE.

Elle ne garantit toutefois pas qu'un équipement fonctionnera dans tous les cas. Un budget insuffisant, une limite de puissance, un câble défectueux ou une panne peuvent toujours empêcher la mise en service.

## 5.2 PoE passif

L'expression **PoE passif** désigne généralement des solutions qui ne s'appuient pas sur les mêmes mécanismes normalisés de détection avant d'appliquer la tension.

Les produits passifs ne possèdent pas nécessairement la même tension, le même brochage ou les mêmes règles de fonctionnement. Il faut donc vérifier la documentation exacte des deux appareils.

Un équipement qui utilise un connecteur RJ45 n'est pas forcément conçu pour recevoir n'importe quelle tension sur ses conducteurs.

**Règle essentielle :** ne branche jamais une source d'alimentation de type ou de brochage inconnu à un appareil réseau.

---

# 6. Les principaux standards PoE

Les familles IEEE PoE ont évolué pour permettre l'alimentation d'appareils de besoins différents.

| Standard | Type | Puissance maximale de référence côté PSE | Puissance de référence côté PD |
|---|---:|---:|---:|
| IEEE 802.3af | Type 1 | 15,4 W | 12,95 W |
| IEEE 802.3at | Type 2 | 30 W | 25,5 W |
| IEEE 802.3bt | Type 3 | Jusqu'à 60 W | Jusqu'à 51 W |
| IEEE 802.3bt | Type 4 | Jusqu'à 90 W | Jusqu'à 71,3 W |

Ces plafonds permettent de comparer les types. Ils ne signifient pas que chaque appareil consomme la puissance maximale ni qu'un port quelconque peut fournir tous ces niveaux.

La puissance applicable dépend du standard, de la classe, du matériel, de la liaison et de la configuration.

## 6.1 Watts et débit Ethernet

Les watts mesurent la puissance électrique. Les mégabits par seconde et les gigabits par seconde mesurent le débit de données.

Un port capable de délivrer 90 W n'est donc pas nécessairement plus rapide qu'un port capable d'en délivrer 15,4 W.

Il faut distinguer :
- la vitesse du lien Ethernet ;
- le niveau de puissance PoE ;
- la puissance requise par le PD ;
- le budget global du switch.

## 6.2 Choisir un niveau adapté

Le dimensionnement commence par la fiche technique du PD.

Une caméra, un téléphone IP et un point d'accès Wi-Fi n'ont pas nécessairement les mêmes besoins. Même au sein d'une famille de produits, les besoins peuvent varier selon les modèles et les fonctions disponibles.

Avant de sélectionner le switch, vérifier le standard requis, la puissance disponible sur les ports concernés et la capacité totale du système.

---

# 7. Détection et démarrage

Le fonctionnement du PoE comprend plusieurs étapes logiques.

1. Le câble relie le PSE au PD.
2. Le PSE recherche la signature électrique attendue d'un équipement compatible.
3. Le mécanisme de classification applicable contribue à déterminer le niveau de puissance.
4. Une négociation complémentaire peut intervenir selon le standard et les équipements.
5. Le PSE autorise l'alimentation dans les limites admises.
6. Le PSE surveille les conditions de fonctionnement prévues.

Les détails de ces étapes dépendent du standard et du matériel. Il ne faut pas considérer cette séquence générale comme une description exhaustive de chaque type de PoE.

## 7.1 Pourquoi le PSE ne doit-il pas alimenter arbitrairement tous les ports ?

Les ports Ethernet servent à connecter de nombreux types d'appareils. Certains ne sont pas conçus pour recevoir de l'énergie PoE.

La détection normalisée contribue à empêcher une alimentation inappropriée. Elle permet au PSE d'identifier un PD prévu pour le système d'alimentation.

La compatibilité ne se déduit donc pas du seul fait que le câble est branché ou que le voyant Ethernet s'allume.

## 7.2 Schéma animé — Cycle de démarrage

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" role="img" aria-labelledby="poeb2-title">
<title id="poeb2-title">Étapes de démarrage d'une liaison PoE</title>
<defs><style>
.poeb2-bg{fill:#101827}.poeb2-box{fill:#1c2b42;stroke:#425c7c;stroke-width:2}.poeb2-h{fill:#f8fafc;font:700 15px Arial,sans-serif}.poeb2-t{fill:#cfdae8;font:12px Arial,sans-serif}.poeb2-link{fill:none;stroke:#4ddbb0;stroke-width:3;stroke-dasharray:7 8;animation:poeb2-flow 1s linear infinite}.poeb2-bar{fill:#60a5fa}.poeb2-note{fill:#a8b9cf;font:11px Arial,sans-serif}@keyframes poeb2-flow{to{stroke-dashoffset:-30}}@keyframes poeb2-glow{0%,100%{opacity:.45}50%{opacity:1}}.poeb2-active{animation:poeb2-glow 1.6s ease-in-out infinite}@media(prefers-reduced-motion:reduce){.poeb2-link,.poeb2-active{animation:none}}
</style></defs>
<rect class="poeb2-bg" width="900" height="300" rx="18"/>
<text class="poeb2-h" x="450" y="34" text-anchor="middle" font-size="18">Du branchement au fonctionnement</text>
<g>
<rect class="poeb2-box" x="25" y="86" width="190" height="130" rx="12"/>
<rect class="poeb2-bar poeb2-active" x="25" y="86" width="190" height="7" rx="3"/>
<text class="poeb2-h" x="120" y="121" text-anchor="middle">1. Détection</text>
<text class="poeb2-t" x="120" y="148" text-anchor="middle">Vérifier la présence</text><text class="poeb2-t" x="120" y="165" text-anchor="middle">d'une signature PD</text>
<text class="poeb2-t" x="120" y="194" text-anchor="middle">Sans détection valide :</text>
<text class="poeb2-t" x="120" y="207" text-anchor="middle">pas d'alimentation normale</text>
<rect class="poeb2-box" x="245" y="86" width="190" height="130" rx="12"/>
<rect class="poeb2-bar poeb2-active" x="245" y="86" width="190" height="7" rx="3" style="animation-delay:.5s"/>
<text class="poeb2-h" x="340" y="121" text-anchor="middle">2. Classification</text>
<text class="poeb2-t" x="340" y="148" text-anchor="middle">Évaluer les besoins</text><text class="poeb2-t" x="340" y="165" text-anchor="middle">et les capacités prévues</text>
<text class="poeb2-t" x="340" y="194" text-anchor="middle">Classe et négociation</text><text class="poeb2-t" x="340" y="207" text-anchor="middle">selon le standard utilisé</text>
<rect class="poeb2-box" x="465" y="86" width="190" height="130" rx="12"/>
<rect class="poeb2-bar poeb2-active" x="465" y="86" width="190" height="7" rx="3" style="animation-delay:1s"/>
<text class="poeb2-h" x="560" y="121" text-anchor="middle">3. Mise sous tension</text>
<text class="poeb2-t" x="560" y="148" text-anchor="middle">Le PSE fournit l'énergie</text><text class="poeb2-t" x="560" y="165" text-anchor="middle">dans les limites admises</text>
<text class="poeb2-t" x="560" y="194" text-anchor="middle">Le PD démarre</text><text class="poeb2-t" x="560" y="207" text-anchor="middle">si la puissance suffit</text>
<rect class="poeb2-box" x="685" y="86" width="190" height="130" rx="12"/>
<rect class="poeb2-bar poeb2-active" x="685" y="86" width="190" height="7" rx="3" style="animation-delay:1.5s"/>
<text class="poeb2-h" x="780" y="121" text-anchor="middle">4. Surveillance</text>
<text class="poeb2-t" x="780" y="148" text-anchor="middle">Suivre l'état du port</text><text class="poeb2-t" x="780" y="165" text-anchor="middle">et les défauts électriques</text>
<circle cx="780" cy="190" r="6" fill="#4ade80"><animate attributeName="r" values="4;7;4" dur="1.5s" repeatCount="indefinite"/></circle>
<text class="poeb2-t" x="780" y="211" text-anchor="middle">Lien en fonctionnement</text>
</g>
<path class="poeb2-link" d="M215 151 H245 M435 151 H465 M655 151 H685"/>
<text class="poeb2-note" x="450" y="256" text-anchor="middle">Séquence pédagogique : les détails dépendent de la norme, de la classe et du matériel.</text>
<text class="poeb2-note" x="450" y="275" text-anchor="middle">Le branchement seul ne garantit ni l'admission du PD ni une puissance suffisante.</text>
</svg>

---

# 8. Budget PoE : comprendre la capacité du switch

Le budget PoE représente la puissance totale que le switch peut consacrer à l'alimentation des équipements, selon sa configuration et son état.

Il ne faut pas confondre le nombre de ports physiques et la capacité totale du système.

Un switch peut posséder 24 ports PoE sans disposer d'une alimentation suffisante pour fournir simultanément la puissance maximale de chaque port.

## 8.1 Limite individuelle et limite globale

La **limite de port** désigne la puissance maximale prise en charge par un port donné.

Le **budget global** désigne la capacité commune disponible pour l'ensemble des ports.

Ces deux contraintes existent simultanément. Une nouvelle caméra peut être compatible avec un port et pourtant ne pas être admissible parce que le budget total est insuffisant.

Inversement, un budget global disponible ne permet pas de dépasser les limites d'un port donné.

## 8.2 Exemple guidé

Un switch possède un budget PoE utilisable de 180 W.

Ses ports ont déjà des réservations totalisant 120 W. Une nouvelle caméra nécessite une allocation de 35 W.

La marge théorique avant admission est :

`180 W − 120 W = 60 W`

La marge théorique après admission serait :

`60 W − 35 W = 25 W`

Le calcul laisse donc une marge positive.

Il faut toutefois encore vérifier la capacité du port, le standard de la caméra, la puissance exigée par le PD, les priorités et les éventuelles limites configurées.

Le résultat arithmétique constitue un indice utile, pas une autorisation automatique.

## 8.3 Puissance réservée et consommation mesurée

Supposons que le switch réserve 30 W pour un appareil alors que sa consommation instantanée est de 12 W.

Les valeurs représentent deux informations différentes :
- la réservation est la capacité retenue par le système ;
- la mesure indique la puissance observée à un instant précis.

Il ne faut pas supposer que les 18 W de différence sont automatiquement disponibles pour un autre appareil. Le contrôleur peut maintenir la réservation en fonction de la classe ou de sa politique.

## 8.4 Que se passe-t-il quand le budget est insuffisant ?

Le comportement varie suivant le matériel et sa configuration. Un switch peut refuser l'alimentation d'un nouveau port, appliquer une politique de priorité ou signaler une insuffisance de puissance.

L'administrateur doit consulter le statut PoE et les journaux. Il ne faut pas tenter de contourner une limitation sans vérifier les capacités électriques de la liaison et des appareils.

---

# 9. Schéma animé — Dépannage d'un équipement qui ne s'allume pas

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 350" role="img" aria-labelledby="poeb3-title">
<title id="poeb3-title">Arbre de diagnostic d'un équipement qui ne s'allume pas en PoE</title>
<defs><style>
.poeb3-bg{fill:#101827}.poeb3-box{fill:#1e3048;stroke:#58708f;stroke-width:1.7}.poeb3-h{fill:#f8fafc;font:700 14px Arial,sans-serif}.poeb3-t{fill:#d0dbea;font:12px Arial,sans-serif}.poeb3-ok{fill:none;stroke:#48d9ae;stroke-width:3;stroke-dasharray:7 8;animation:poeb3-route 1.1s linear infinite}.poeb3-warn{fill:none;stroke:#ffbd69;stroke-width:3;stroke-dasharray:6 8}.poeb3-note{fill:#9fb2ca;font:11px Arial,sans-serif}@keyframes poeb3-route{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.poeb3-ok{animation:none}}
</style></defs>
<rect class="poeb3-bg" width="900" height="350" rx="18"/>
<text class="poeb3-h" x="450" y="32" text-anchor="middle" font-size="18">Suivre une méthode du physique vers la configuration</text>
<rect class="poeb3-box" x="275" y="55" width="350" height="54" rx="10"/>
<text class="poeb3-h" x="450" y="78" text-anchor="middle">L'appareil n'est pas alimenté</text>
<text class="poeb3-t" x="450" y="96" text-anchor="middle">Commencer par les contrôles non destructifs</text>
<path class="poeb3-ok" d="M450 109 V133 H165 V151 M450 133 H450 V151 M450 133 H735 V151"/>
<rect class="poeb3-box" x="30" y="151" width="270" height="88" rx="10"/>
<text class="poeb3-h" x="165" y="176" text-anchor="middle">1. Câble et port</text>
<text class="poeb3-t" x="165" y="198" text-anchor="middle">Câble testé ? Port activé ?</text>
<text class="poeb3-t" x="165" y="216" text-anchor="middle">Voyant et état du lien ?</text>
<rect class="poeb3-box" x="315" y="151" width="270" height="88" rx="10"/>
<text class="poeb3-h" x="450" y="176" text-anchor="middle">2. Compatibilité PoE</text>
<text class="poeb3-t" x="450" y="198" text-anchor="middle">Norme, PD et tension compatibles ?</text>
<text class="poeb3-t" x="450" y="216" text-anchor="middle">Injecteur ou port réellement PoE ?</text>
<rect class="poeb3-box" x="600" y="151" width="270" height="88" rx="10"/>
<text class="poeb3-h" x="735" y="176" text-anchor="middle">3. Puissance disponible</text>
<text class="poeb3-t" x="735" y="198" text-anchor="middle">Budget et priorités vérifiés ?</text>
<text class="poeb3-t" x="735" y="216" text-anchor="middle">Classe et demande du PD ?</text>
<path class="poeb3-warn" d="M165 239 V265 H450 V281 M450 239 V281 M735 239 V265 H450"/>
<rect x="180" y="281" width="540" height="43" rx="9" fill="#3a2a1a" stroke="#f3b45e" stroke-width="1.5"/>
<text class="poeb3-h" x="450" y="299" text-anchor="middle">Collecter l'état du port et les journaux</text>
<text class="poeb3-t" x="450" y="316" text-anchor="middle">Corriger la cause identifiée puis effectuer un test contrôlé</text>
</svg>

---

# 10. Diagnostiquer les pannes courantes

## 10.1 Le voyant Ethernet reste éteint

Causes possibles :
- câble débranché ou endommagé ;
- port désactivé ;
- absence de liaison Ethernet ;
- problème du PD ;
- mauvais choix de matériel ou mauvais raccordement.

Il faut d'abord vérifier le câble, l'état du port et la compatibilité. Le voyant n'est qu'un indicateur ; il ne remplace pas l'inspection de l'état opérationnel.

## 10.2 Le lien Ethernet fonctionne, mais le PD reste éteint

Un lien Ethernet actif ne prouve pas que la puissance a été accordée.

Il faut examiner le statut PoE distinct du statut du lien. Si le matériel le permet, relever la puissance réservée, l'état de détection, le budget restant et les messages de refus.

## 10.3 Un appareil fonctionne sur un port, mais pas sur un autre

Comparer les ports :
- prise en charge du PoE ;
- limite de puissance ;
- configuration administrative ;
- priorité d'alimentation ;
- budget restant ;
- événements et erreurs.

Tous les ports d'un même switch ne possèdent pas nécessairement les mêmes capacités.

## 10.4 L'appareil démarre puis redémarre

Les causes possibles incluent :
- une puissance insuffisante au démarrage ;
- un câble ou un connecteur défectueux ;
- une limitation de puissance ;
- un problème matériel du PD ;
- un événement électrique signalé par le contrôleur.

Il faut collecter les événements horodatés avant de modifier la configuration. Une augmentation de puissance ne doit être envisagée qu'après vérification des caractéristiques du PSE, du PD et du câble.

## 10.5 Plusieurs appareils tombent simultanément

Lorsque plusieurs équipements sont touchés au même moment, il faut rechercher une cause commune :
- alimentation ou capacité du switch ;
- budget PoE ;
- changement de configuration ;
- problème logiciel ou matériel ;
- perte d'un composant commun de l'installation.

La corrélation temporelle constitue une piste de diagnostic. Elle ne prouve pas à elle seule que la cause est électrique.

---

# 11. Travaux pratiques guidés

Les exercices doivent être réalisés sur du matériel de laboratoire ou une installation dont tu es autorisé à administrer les équipements.

## TP 1 — Inventorier les équipements

1. relever le modèle du switch ;
2. identifier les ports réellement compatibles PoE ;
3. relever le standard et le niveau de puissance supportés ;
4. identifier les PD raccordés ;
5. calculer une marge théorique à partir des réservations connues ;
6. documenter les limitations des ports.

**Livrable attendu :** un tableau contenant port, modèle du PD, standard attendu, allocation connue et état opérationnel.

## TP 2 — Observer le démarrage

1. relever l'état initial d'un port PoE ;
2. connecter un PD compatible ;
3. observer les statuts Ethernet et PoE ;
4. relever les données de classe, réservation ou mesure si elles existent ;
5. déconnecter le PD et noter le changement d'état ;
6. expliquer les observations.

Les commandes doivent provenir de la documentation du constructeur. Une commande Cisco ne doit pas être supposée identique sur un switch d'une autre marque.

## TP 3 — Comparer deux équipements

Choisir deux PD différents et comparer :
- modèle et standard ;
- classe ou allocation ;
- puissance mesurée si disponible ;
- résultat de l'admission ;
- comportement lors de la déconnexion.

Explique pourquoi deux appareils dotés du même connecteur peuvent avoir des besoins de puissance différents.

## TP 4 — Diagnostiquer un refus

Dans un laboratoire, observer un cas où l'alimentation d'un PD est refusée.

Le rapport doit inclure le symptôme, les informations collectées, les hypothèses, les tests réalisés, la cause établie et le résultat final.

N'effectue pas de court-circuit volontaire et n'applique jamais une tension non prévue par le matériel.

---

# 12. Exercices et corrigés

### Questions

1. Quelle est la différence entre PSE et PD ?
2. Pourquoi un connecteur RJ45 ne suffit-il pas à établir la compatibilité PoE ?
3. Quelle différence existe-t-il entre la puissance maximale du PSE et la puissance disponible côté PD ?
4. Pourquoi le budget global reste-t-il important si chaque port possède une limite ?
5. Pourquoi un lien Ethernet actif ne garantit-il pas que l'appareil est alimenté ?
6. Cite quatre causes possibles d'un refus d'alimentation.
7. Pourquoi faut-il relever les événements avant de changer la configuration ?
8. Quelle est la différence entre une réservation et une consommation mesurée ?
9. Quel est le rôle d'un injecteur PoE ?
10. Que faut-il faire avant de raccorder une source PoE dont la nature est inconnue ?

### Corrigé

1. Le PSE fournit l'énergie ; le PD la reçoit.
2. Le connecteur n'identifie ni le standard ni les capacités électriques du matériel.
3. L'énergie subit des pertes dans la liaison, notamment dues à la résistance des conducteurs.
4. Tous les ports partagent une capacité électrique globale.
5. Les états Ethernet et PoE sont distincts.
6. Budget insuffisant, port non-PoE, incompatibilité du PD, limitation de puissance ou câble défectueux.
7. Les événements permettent d'orienter le diagnostic et d'éviter des modifications inutiles.
8. La réservation est une allocation du contrôleur ; la consommation est une mesure à un instant ou sur une période.
9. L'injecteur ajoute une alimentation PoE à une liaison Ethernet.
10. Il faut identifier la tension, le brochage, le standard et la compatibilité à partir de la documentation.

---

# 13. Glossaire

| Terme | Définition |
|---|---|
| PoE | Transport d'énergie et de données sur une liaison Ethernet compatible |
| PSE | Équipement qui fournit la puissance |
| PD | Équipement qui reçoit la puissance |
| Budget global | Capacité destinée à l'alimentation de l'ensemble des ports |
| Limite de port | Puissance maximale prise en charge par une interface |
| Réservation | Capacité retenue par le contrôleur |
| Mesure de consommation | Puissance observée à un instant donné ou sur une période |
| Classe PoE | Classification associée à un niveau de puissance |
| Injecteur | Dispositif qui ajoute l'alimentation à une liaison Ethernet |
| LLDP | Protocole de découverte de voisins de couche 2, pouvant contribuer aux échanges de puissance sur le matériel compatible |

---

# 14. Références

- [Ethernet Alliance — Référence sur IEEE 802.3bt](https://ethernetalliance.org/wp-content/uploads/2018/04/WP_EA_Overview8023bt_FINAL.pdf)
- [Cisco — Dépannage de l'alimentation PoE](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3750/software/troubleshooting/g_power_over_ethernet.html)
- [Microchip — Types et standards PoE](https://developerhelp.microchip.com/xwiki/bin/view/applications/ethernet/poe/standards/)

Pour toute intervention réelle, vérifier les capacités du modèle exact de PSE, du PD, du câble et de la version logicielle.