
# Le matériel réseau — Niveau expert

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** maîtriser les équipements réseau, les interfaces, les modules optiques, le PoE et le dimensionnement élémentaire.  
> **Objectif :** concevoir, dimensionner et maintenir une infrastructure réseau matérielle performante, sécurisée et résiliente, y compris dans les conditions de charge et les situations de panne.


## Sommaire

1. Démarche d'ingénierie matérielle
2. Architecture interne des switches et routeurs
3. Évaluer les performances réelles
4. Dimensionner les liens et les chemins de trafic
5. Ingénierie optique et budget de liaison
6. Alimentation, PoE et distribution électrique
7. Refroidissement et contraintes physiques
8. Haute disponibilité et domaines de panne
9. Fiabilité et cycle de vie matériel
10. Mesures, télémétrie et analyse matérielle
11. Sélection technique et validation
12. Architecture de référence
13. Atelier expert
14. Étude de défaillance
15. Évaluation corrigée


# 1. Démarche d'ingénierie matérielle

## 1.1 Le matériel doit être évalué dans son contexte

Une infrastructure réseau doit satisfaire des exigences de capacité, de disponibilité, de sécurité et d'exploitation.

Le choix d'un équipement ne peut donc pas se résumer à la comparaison de son nombre de ports ou de sa vitesse maximale annoncée.

Il faut évaluer :

- les caractéristiques des interfaces ;
- la capacité de traitement ;
- les tables de commutation et de routage ;
- les fonctionnalités activées ;
- les performances avec le profil de trafic attendu ;
- les besoins énergétiques ;
- la dissipation thermique ;
- la diversité des chemins ;
- les limites en mode dégradé ;
- le support logiciel et les conditions de remplacement.

Le matériel doit être sélectionné à partir des besoins techniques mesurables et des conséquences de son indisponibilité.

## 1.2 Objectifs experts

À la fin de ce cours, vous serez capable de :

1. expliquer les rôles des principaux blocs matériels d'une plateforme réseau ;
2. interpréter les métriques de capacité et de transfert ;
3. distinguer capacité nominale et performances dans un scénario précis ;
4. dimensionner des uplinks selon plusieurs profils de trafic ;
5. calculer un budget optique ;
6. analyser les contraintes d'alimentation et de refroidissement ;
7. identifier les dépendances physiques communes ;
8. concevoir des stratégies de redondance adaptées ;
9. évaluer la fiabilité et la maintenabilité d'un parc matériel ;
10. mettre en place une méthode de validation avant réception et après installation ;
11. structurer une procédure de remplacement et de récupération ;
12. distinguer les mesures observées des hypothèses sur l'origine d'une panne.

## 1.3 Transformer les besoins en critères de sélection

Avant de consulter les fiches techniques, définissez :

**Capacité :** ports, débits, trafic agrégé, nombre de routes, de sessions et de règles.

**Disponibilité :** tolérance à la perte d'un lien, d'un module, d'une alimentation ou d'un équipement.

**Sécurité :** segmentation, isolation de la gestion, capacités de filtrage et maintenance logicielle.

**Exploitation :** inventaire, supervision, pièces de rechange, procédures de remplacement et documentation.

**Évolution :** croissance des terminaux, futurs débits, besoins PoE et contraintes de compatibilité.

Chaque exigence doit être associée à un critère de vérification.


# 2. Architecture interne des switches et routeurs

## 2.1 Le plan de données matériel

Un switch ou un routeur peut utiliser des circuits spécialisés pour accélérer certaines opérations de transfert.

Parmi les composants que l'on peut rencontrer :

- **ASIC :** circuit intégré spécialisé pour des fonctions déterminées ;
- **NPU :** processeur réseau conçu pour traiter certains travaux de paquets ;
- **CPU de contrôle :** processeur exécutant des fonctions de gestion et de contrôle ;
- **mémoire de paquets et buffers :** mémoire utilisée pour stocker temporairement des données en attente de traitement ou de transmission ;
- **interfaces physiques (PHY) :** circuits qui assurent les fonctions physiques nécessaires à la transmission sur un support ;
- **tables de transfert :** structures utilisées pour retrouver les décisions de commutation ou de routage.

La conception exacte varie selon le constructeur et la génération de l'équipement. Il n'est pas possible de déduire les performances d'un appareil de la seule présence d'un ASIC ou d'un processeur donné.

## 2.2 Traitement du trafic

Un paquet ou une trame reçu par un équipement peut nécessiter plusieurs opérations :

1. réception par l'interface physique ;
2. vérifications et traitement de couche liaison ;
3. recherche des informations de transfert ;
4. application des politiques et traitements pris en charge ;
5. mise en file d'attente si la sortie est momentanément indisponible ;
6. transmission sur le lien de sortie.

Les fonctions réelles, leur ordre et leur implémentation varient selon la plateforme et les fonctionnalités activées.

Certaines opérations peuvent être accélérées par le matériel ; d'autres peuvent dépendre du logiciel ou de ressources de contrôle.

## 2.3 CPU de contrôle et transfert matériel

Le processeur de contrôle traite notamment des tâches de gestion et certains échanges de protocoles.

Le trafic utilisateur est souvent transféré dans des circuits spécialisés afin de ne pas solliciter le CPU pour chaque paquet de transit.

Cependant, certains paquets destinés à l'équipement lui-même, certaines exceptions ou certaines fonctions particulières peuvent nécessiter un traitement différent.

Une utilisation élevée du CPU ne signifie donc pas systématiquement que le débit de transit est saturé. Inversement, un CPU peu utilisé ne garantit pas l'absence de congestion ou d'un problème de transfert.

## 2.4 Buffers et files d'attente

Les buffers permettent d'absorber temporairement des écarts entre les vitesses d'arrivée et de départ des données.

Lorsqu'un port reçoit plus de trafic qu'il ne peut en transmettre pendant un intervalle, une file peut se remplir. Si la mémoire disponible est insuffisante ou si les politiques de gestion le prévoient, certains paquets sont abandonnés.

La quantité de mémoire de buffers ne suffit toutefois pas à déterminer la performance. La gestion des files, les mécanismes de partage de mémoire, le comportement en congestion et le profil des flux sont également importants.

## 2.5 Schéma simplifié d'une plateforme

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="hw-expert-asic-title hw-expert-asic-desc">
  <title id="hw-expert-asic-title">Architecture matérielle simplifiée d'un switch ou routeur</title>
  <desc id="hw-expert-asic-desc">Les interfaces physiques alimentent le chemin de transfert, qui utilise des tables et des files d'attente. Le CPU de contrôle supervise certaines opérations et échange des informations avec le plan de transfert. L'alimentation et le refroidissement sont des fonctions physiques indépendantes mais essentielles.</desc>
  <defs>
    <marker id="asic-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .as-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .as-control{fill:#302044;stroke:#c4b5fd;stroke-width:2}
      .as-power{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .as-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .as-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .as-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#asic-arrow);animation:as-dash 1.8s linear infinite}
      @keyframes as-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">BLOCS FONCTIONNELS D'UNE PLATEFORME</text>
  <rect class="as-box" x="25" y="80" width="175" height="80" rx="10"/>
  <text class="as-title" x="112" y="109" text-anchor="middle">Interfaces PHY</text>
  <text class="as-text" x="112" y="132" text-anchor="middle">Réception / émission</text>
  <rect class="as-box" x="255" y="80" width="200" height="80" rx="10"/>
  <text class="as-title" x="355" y="109" text-anchor="middle">Moteur de transfert</text>
  <text class="as-text" x="355" y="132" text-anchor="middle">ASIC ou NPU selon le modèle</text>
  <rect class="as-box" x="510" y="80" width="190" height="80" rx="10"/>
  <text class="as-title" x="605" y="109" text-anchor="middle">Tables et buffers</text>
  <text class="as-text" x="605" y="132" text-anchor="middle">Recherche et files d'attente</text>
  <rect class="as-box" x="755" y="80" width="220" height="80" rx="10"/>
  <text class="as-title" x="865" y="109" text-anchor="middle">Interfaces de sortie</text>
  <text class="as-text" x="865" y="132" text-anchor="middle">Transmission des données</text>
  <path class="as-flow" d="M200 120 H247"/>
  <path class="as-flow" d="M455 120 H502"/>
  <path class="as-flow" d="M700 120 H747"/>
  <rect class="as-control" x="255" y="220" width="445" height="70" rx="10"/>
  <text class="as-title" x="477" y="248" text-anchor="middle">CPU et logiciel de contrôle</text>
  <text class="as-text" x="477" y="270" text-anchor="middle">Gestion, protocoles et coordination</text>
  <path class="as-flow" d="M477 220 V169"/>
  <rect class="as-power" x="755" y="220" width="220" height="70" rx="10"/>
  <text class="as-title" x="865" y="248" text-anchor="middle">Énergie et refroidissement</text>
  <text class="as-text" x="865" y="270" text-anchor="middle">Conditions de fonctionnement</text>
  <text class="as-text" x="480" y="333" text-anchor="middle">Ce modèle est conceptuel ; les architectures internes diffèrent selon les fabricants.</text>
  <text class="as-text" x="480" y="355" text-anchor="middle">Les performances doivent être vérifiées sur la plateforme et le profil de trafic retenus.</text>
</svg>


# 3. Évaluer les performances réelles

## 3.1 Capacité annoncée et capacité exploitable

Une fiche technique peut annoncer un débit total, un débit en paquets par seconde, un nombre maximal de routes ou une limite de sessions.

Ces indicateurs répondent à des questions différentes. Ils ne doivent pas être comparés comme s'ils mesuraient la même chose.

Pour interpréter les caractéristiques, vérifiez :

- la définition exacte de chaque métrique ;
- les tailles de paquets utilisées dans les tests ;
- les fonctionnalités activées ;
- le sens de mesure du débit ;
- le nombre de ports simultanément sollicités ;
- les limites des tables et ressources partagées ;
- les conditions de température et d'alimentation, si elles affectent le fonctionnement.

## 3.2 Débit et paquets par seconde

Le débit binaire mesure une quantité de données par unité de temps.

Le débit en paquets par seconde mesure un nombre de paquets traités par unité de temps.

À débit binaire identique, une charge constituée de petits paquets peut nécessiter davantage d'opérations de traitement qu'une charge constituée de paquets plus grands.

Il faut donc choisir un matériel en fonction du profil du trafic attendu, pas simplement du plus grand nombre de Gb/s annoncé.

## 3.3 Taux d'utilisation et congestion

Un port à 90 % d'utilisation ne signifie pas forcément qu'il a déjà abandonné des paquets, mais il peut avoir peu de marge disponible lors des pics.

À l'inverse, une moyenne d'utilisation faible peut masquer des congestions brèves.

Les mesures utiles comprennent :

- les pics d'utilisation ;
- les abandons de paquets ;
- les erreurs de transmission ;
- les files d'attente ;
- la latence ;
- les variations de latence ;
- l'évolution sur des périodes représentatives.

## 3.4 Dimensionnement des uplinks

Supposons qu'un commutateur d'accès possède 48 ports de 1 Gb/s. La somme des débits nominaux de ses ports d'accès est de 48 Gb/s en considérant une seule direction et l'ensemble des ports.

Cela ne signifie pas que l'uplink doit obligatoirement fournir 48 Gb/s : tous les postes n'utilisent pas nécessairement leur débit maximal simultanément, et une partie des échanges peut rester locale.

Inversement, un uplink unique de 1 Gb/s peut être insuffisant si de nombreux utilisateurs accèdent simultanément à des serveurs distants.

Il faut donc évaluer :

1. la part du trafic qui quitte le switch ;
2. la simultanéité des usages ;
3. le profil des applications ;
4. les exigences de latence et de pertes ;
5. le trafic prévu en cas de panne d'un lien ;
6. la croissance attendue.

Un taux de contention peut être utile pour discuter d'une architecture, mais il ne remplace pas des mesures représentatives et une analyse des services.

## 3.5 Tests de performance

Un test de débit doit préciser les conditions de mesure.

Il faut notamment tenir compte de :

- la capacité des deux extrémités ;
- la taille et le type des paquets ;
- le nombre de flux ;
- l'état de la charge réseau ;
- la latence et les pertes ;
- les fonctions de sécurité activées ;
- les restrictions du système d'exploitation et des interfaces.

Un test réalisé entre deux serveurs peut mesurer le chemin complet entre eux. Il ne démontre pas nécessairement la capacité maximale de chaque équipement intermédiaire.


# 4. Dimensionner les liens et les chemins de trafic

## 4.1 Le trafic nominal et le mode dégradé

Un réseau doit être dimensionné pour le fonctionnement normal, mais aussi pour les situations où une partie des chemins devient indisponible.

Exemple : deux uplinks de 10 Gb/s sont configurés entre l'accès et la distribution.

Si les deux sont actifs et fonctionnent correctement, leur capacité globale peut être exploitée selon le mécanisme de répartition. Si un lien tombe, la capacité restante dépend de ce que l'autre lien et les équipements associés peuvent réellement prendre en charge.

Il faut vérifier que le mode dégradé reste acceptable pour les services qui doivent continuer à fonctionner.

## 4.2 Redondance et charge

La redondance apporte de la résilience, mais peut modifier les chemins et la répartition de trafic lors d'une panne.

Le dimensionnement doit examiner :

- la charge avant panne ;
- les chemins qui restent disponibles ;
- la capacité de ces chemins ;
- les effets des changements de routage ou de commutation ;
- les possibles congestions nouvelles ;
- le temps nécessaire à la détection et à la reconvergence.

Un réseau qui reste physiquement connecté peut tout de même subir une forte dégradation du service si le chemin restant est trop limité.

## 4.3 Interfaces et asymétrie

Un chemin peut être limité par une seule interface plus lente ou par un composant intermédiaire.

Une architecture avec des interfaces de 100 Gb/s en cœur ne garantit pas un transfert de 100 Gb/s pour des terminaux raccordés en 1 Gb/s, ni pour un chemin dont un autre élément est plus lent.

Le diagnostic doit examiner l'ensemble du chemin et les conditions de fonctionnement.


# 5. Ingénierie optique et budget de liaison

## 5.1 Vérifier la compatibilité des modules

Avant d'installer des transceivers, vérifiez :

- le format accepté par le port ;
- la compatibilité déclarée par le constructeur ;
- le débit ;
- la longueur d'onde ;
- le type de fibre ;
- la portée spécifiée ;
- le connecteur ;
- la plage de puissance optique ;
- les limitations de température et de fonctionnement.

Les deux extrémités doivent former une paire compatible. Un module de même format physique peut ne pas convenir à la fibre ou au débit de l'autre extrémité.

## 5.2 Budget optique

Le budget optique permet de vérifier que la puissance disponible après les pertes du chemin reste dans les limites du récepteur.

Une approche simplifiée compare la puissance d'émission aux pertes totales, pour estimer la puissance reçue.

\[
P_{\text{reçue}} = P_{\text{émise}} - L_{\text{total}}
\]

Dans cette formule, les puissances sont exprimées en dBm et les pertes en dB.

Les pertes totales peuvent inclure la fibre, les connecteurs, les épissures, les panneaux et les autres composants passifs.

Il faut ensuite vérifier la puissance reçue par rapport aux limites de sensibilité et de surcharge du récepteur, puis appliquer la marge prévue par la conception.

## 5.3 Exemple numérique pédagogique

Supposons, uniquement pour cet exercice, les valeurs suivantes :

- puissance d'émission : 0 dBm ;
- pertes de fibre estimées : 1,2 dB ;
- pertes des connecteurs et épissures : 0,8 dB ;
- autres pertes estimées : 0,5 dB.

La perte totale estimée est :

\[
L_{\text{total}} = 1,2 + 0,8 + 0,5 = 2,5\ \text{dB}
\]

La puissance reçue estimée serait :

\[
P_{\text{reçue}} = 0 - 2,5 = -2,5\ \text{dBm}
\]

Cette valeur n'est pas une validation de liaison à elle seule. Elle doit être comparée à la plage garantie par le module, à la marge attendue et aux mesures effectuées sur le lien réel.

Les valeurs de cet exemple ne correspondent pas à un transceiver particulier.

## 5.4 Trop de puissance peut aussi poser problème

Le récepteur d'un transceiver possède généralement une plage de puissance admise.

Une puissance trop faible peut rendre la réception instable. Une puissance trop forte peut dépasser les limites prévues.

L'analyse doit donc vérifier à la fois la sensibilité et la puissance maximale tolérée.

Il ne faut pas ajouter arbitrairement un atténuateur ou remplacer un module sans avoir établi les niveaux réels et consulté les spécifications.

## 5.5 Diagnostic d'un lien optique

Une démarche adaptée peut comprendre :

1. vérifier les références et la compatibilité des modules ;
2. inspecter les connecteurs selon la procédure de nettoyage ;
3. contrôler la polarité et le chemin de fibre ;
4. consulter les niveaux optiques mesurés si l'équipement les expose ;
5. comparer les valeurs aux plages du transceiver ;
6. observer les erreurs et changements d'état du lien ;
7. mesurer la perte de la liaison avec les instruments appropriés lorsque nécessaire.

Le simple constat que le lien est « up » ne garantit ni la marge optique adéquate ni l'absence d'erreurs lors d'une charge soutenue.

## 5.6 Schéma du budget optique

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="360" viewBox="0 0 1000 360" role="img" aria-labelledby="optical-title optical-desc">
  <title id="optical-title">Chaîne optique et budget de liaison</title>
  <desc id="optical-desc">Le signal part d'un transceiver émetteur, traverse les connecteurs et la fibre, puis atteint le récepteur. Le budget optique compare la puissance émise, les pertes du chemin et les limites du récepteur.</desc>
  <defs>
    <marker id="optical-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .op-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .op-loss{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .op-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .op-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .op-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#optical-arrow);animation:op-dash 1.8s linear infinite}
      @keyframes op-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="358" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DU MODULE ÉMETTEUR AU MODULE RÉCEPTEUR</text>
  <rect class="op-box" x="25" y="92" width="185" height="80" rx="10"/>
  <text class="op-title" x="117" y="121" text-anchor="middle">Transceiver A</text>
  <text class="op-text" x="117" y="144" text-anchor="middle">Puissance émise</text>
  <rect class="op-loss" x="270" y="92" width="190" height="80" rx="10"/>
  <text class="op-title" x="365" y="121" text-anchor="middle">Connecteurs</text>
  <text class="op-text" x="365" y="144" text-anchor="middle">Pertes de connexion</text>
  <rect class="op-loss" x="520" y="92" width="190" height="80" rx="10"/>
  <text class="op-title" x="615" y="121" text-anchor="middle">Fibre optique</text>
  <text class="op-text" x="615" y="144" text-anchor="middle">Atténuation du chemin</text>
  <rect class="op-box" x="770" y="92" width="205" height="80" rx="10"/>
  <text class="op-title" x="872" y="121" text-anchor="middle">Transceiver B</text>
  <text class="op-text" x="872" y="144" text-anchor="middle">Puissance reçue</text>
  <path class="op-flow" d="M210 132 H262"/>
  <path class="op-flow" d="M460 132 H512"/>
  <path class="op-flow" d="M710 132 H762"/>
  <rect class="op-box" x="180" y="230" width="640" height="65" rx="10"/>
  <text class="op-title" x="500" y="256" text-anchor="middle">Contrôle du budget optique</text>
  <text class="op-text" x="500" y="278" text-anchor="middle">Puissance émise − pertes = puissance reçue estimée</text>
  <path class="op-flow" d="M872 172 V205 H820 V238"/>
  <text class="op-text" x="500" y="325" text-anchor="middle">Comparer la mesure à la sensibilité et à la limite maximale du récepteur.</text>
</svg>


# 6. Alimentation, PoE et distribution électrique

## 6.1 Dimensionner l'alimentation de l'ensemble

La puissance nécessaire à une baie ne se réduit pas au total des valeurs nominales des alimentations.

Il faut examiner :

- la consommation prévue en fonctionnement normal ;
- les pointes de consommation ;
- le nombre d'alimentations utilisées ;
- la puissance nécessaire en mode dégradé ;
- les besoins des terminaux PoE ;
- les limites des circuits et des unités de distribution électrique ;
- l'autonomie nécessaire en cas de coupure.

Les chiffres de consommation doivent provenir des spécifications pertinentes ou de mesures représentatives. L'évaluation doit tenir compte de la configuration exacte de l'équipement.

## 6.2 Budget PoE en mode dégradé

Supposons qu'un switch alimente des points d'accès et téléphones IP, et qu'une alimentation puisse tomber en panne.

Le budget PoE en mode normal ne suffit pas à déterminer le comportement lors de la perte d'une alimentation.

Il faut vérifier si la puissance restante couvre les appareils prioritaires et si le constructeur précise des limites supplémentaires en mode de redondance.

Si la puissance n'est plus suffisante, certains terminaux peuvent cesser de fonctionner ou le système peut appliquer un mécanisme de délestage selon ses fonctions.

La politique doit déterminer quels équipements sont prioritaires et quelles alertes indiquent une situation dégradée.

## 6.3 UPS et autonomie

L'autonomie d'un onduleur dépend de plusieurs éléments, dont la puissance de la charge, la technologie de batteries, leur état, les pertes et les conditions de fonctionnement.

Il ne faut pas calculer l'autonomie uniquement en divisant la capacité nominale annoncée par la puissance totale, sans tenir compte des caractéristiques et de la courbe de décharge du fabricant.

Un plan énergétique complet définit :

- la charge électrique de référence ;
- l'autonomie recherchée ;
- les circuits alimentés ;
- les équipements prioritaires ;
- la procédure d'arrêt si l'énergie est épuisée ;
- les tests de batteries et de bascule.

## 6.4 Préparer un test de panne électrique

Un test de perte d'alimentation peut interrompre des services. Il doit être planifié, autorisé et effectué dans des conditions contrôlées.

Avant le test :

1. documenter les circuits et les alimentations ;
2. confirmer l'état des sources redondantes ;
3. identifier les services concernés ;
4. définir les critères de succès et d'arrêt ;
5. préparer la surveillance ;
6. préciser qui peut interrompre le test.

Après le test, vérifiez l'état des équipements, les événements signalés et la reprise complète des services.


# 7. Refroidissement et contraintes physiques

## 7.1 Enveloppe thermique

Chaque équipement possède des limites environnementales définies par son fabricant.

La conception doit tenir compte :

- de la température à l'entrée d'air ;
- de la chaleur produite par les équipements ;
- du débit d'air nécessaire ;
- de la densité de la baie ;
- de l'organisation des câbles ;
- de la présence de composants à forte consommation ;
- des conditions possibles lors d'une défaillance de refroidissement.

Une pièce maintenue à une température ambiante correcte peut néanmoins présenter un point chaud local si le chemin d'air est bloqué ou si les équipements rejettent leur chaleur au mauvais endroit.

## 7.2 Flux d'air

Certains équipements aspirent l'air par l'avant et le rejettent à l'arrière ; d'autres peuvent utiliser une autre organisation.

Des équipements placés côte à côte dans une baie doivent être compatibles avec l'organisation du refroidissement et les règles d'installation de leurs fabricants.

Les obturateurs, chemins de câbles et panneaux doivent être utilisés conformément à la conception thermique. Un changement physique dans la baie peut modifier le flux d'air de plusieurs appareils.

## 7.3 Capacité de refroidissement et densité

La quantité de chaleur produite dépend du fonctionnement réel et des caractéristiques électriques.

Le plan de refroidissement doit donc être dimensionné selon les charges, la densité et les exigences environnementales.

Il faut aussi prévoir la maintenance des ventilateurs, filtres et systèmes de climatisation, ainsi que les moyens de signaler une hausse de température avant qu'elle n'affecte le service.


# 8. Haute disponibilité et domaines de panne

## 8.1 Définir les domaines de panne

Un domaine de panne est un ensemble de composants susceptibles d'être affectés par un même événement.

Exemples :

- un switch ;
- une baie ;
- une salle informatique ;
- un circuit électrique ;
- un chemin de câblage ;
- une fibre commune ;
- un fournisseur de connectivité.

L'analyse de disponibilité doit déterminer si deux composants supposés redondants partagent un domaine de panne commun.

## 8.2 Redondance des composants

La redondance peut concerner :

- les alimentations ;
- les ventilateurs ;
- les modules de commutation ;
- les liens ;
- les chemins de fibres ;
- les équipements complets ;
- les sites ou salles.

Chaque mécanisme possède des limites. Une alimentation redondante ne protège pas contre une panne de l'ensemble du châssis. Deux liens sur le même conduit ne protègent pas contre la coupure de ce conduit.

## 8.3 Diversité physique

Pour concevoir deux chemins véritablement distincts, documentez :

- les ports et modules utilisés ;
- les câbles et panneaux ;
- les conduits ou chemins physiques ;
- les équipements intermédiaires ;
- les alimentations ;
- les salles ou sites ;
- les dépendances aux opérateurs.

La diversité doit être confirmée par des informations d'installation et des vérifications physiques. Elle ne peut pas toujours être déduite d'une simple configuration réseau.

## 8.4 Disponibilité théorique

Une estimation élémentaire de disponibilité peut être exprimée sous la forme :

\[
A = \frac{MTBF}{MTBF + MTTR}
\]

où :

- \(MTBF\) représente le temps moyen entre les défaillances selon le modèle considéré ;
- \(MTTR\) représente le temps moyen nécessaire à la réparation ou à la restauration.

Cette relation est une approximation et dépend des hypothèses de mesure. Le sens exact des métriques doit être défini dans le modèle de fiabilité retenu.

La disponibilité réelle d'un service dépend également des dépendances, des erreurs humaines, des pannes communes, des opérations de maintenance et des mécanismes de bascule.

## 8.5 Pourquoi les tests de bascule sont indispensables

Un dispositif de secours peut être inutilisable à cause d'une mauvaise configuration, d'une batterie défaillante, d'un lien mal raccordé ou d'un mécanisme qui n'a pas été testé.

Il faut valider la bascule dans des conditions représentatives, puis vérifier le rétablissement complet du service.

Les tests de disponibilité doivent avoir des critères de succès, des moyens de surveillance et une procédure d'arrêt maîtrisée.


# 9. Fiabilité et cycle de vie matériel

## 9.1 Fiabilité et maintenabilité

Le choix du matériel doit prendre en compte sa durée de support, la disponibilité des pièces, les délais de réparation et la compétence des équipes chargées de l'exploiter.

Deux modèles affichant des performances semblables peuvent présenter des différences importantes sur ces critères.

Les données de fiabilité annoncées doivent être interprétées avec prudence : les conditions de test, la charge, l'environnement et les hypothèses statistiques peuvent différer de l'exploitation réelle.

## 9.2 Obsolescence et support logiciel

La fin de disponibilité commerciale, la fin de maintenance logicielle et la fin de support sont des événements différents selon la politique du fournisseur.

Avant l'achat, vérifiez :

- les dates de support publiées ;
- les versions logicielles compatibles ;
- la disponibilité des correctifs ;
- les chemins de mise à niveau ;
- les modules et cartes encore pris en charge ;
- les contraintes de migration ;
- les pièces de rechange.

Un équipement physiquement fonctionnel peut devenir un risque opérationnel si les vulnérabilités ne peuvent plus être corrigées.

## 9.3 Inventaire matériel

Un inventaire utile comprend :

- le modèle ;
- l'identifiant de l'actif ;
- le numéro de série, stocké de manière appropriée ;
- la version logicielle ;
- les modules installés ;
- les alimentations ;
- la localisation ;
- les connexions ;
- la date d'installation ;
- le statut du support ;
- la procédure de remplacement ;
- les dépendances importantes.

L'inventaire doit être fiable et mis à jour lors des interventions.

## 9.4 Gestion des pièces de rechange

Les pièces de rechange doivent être compatibles avec les modèles, versions et environnements concernés.

Un stock contenant des modules optiques ou des alimentations non validés ne garantit pas une réparation rapide.

Précisez les composants critiques, les quantités minimales, les conditions de stockage, la vérification périodique et les délais de réapprovisionnement.


# 10. Mesures, télémétrie et analyse matérielle

## 10.1 Données de supervision

Selon le modèle, un équipement peut exposer :

- température et état des ventilateurs ;
- état des alimentations ;
- puissance PoE consommée et allouée ;
- niveaux optiques ;
- changements d'état des interfaces ;
- erreurs et abandons ;
- alarmes matérielles ;
- utilisation des ressources ;
- événements de redémarrage.

Les métriques disponibles dépendent du matériel et du logiciel. Vérifiez ce qui est réellement exposé par la plateforme.

## 10.2 Baseline et évolution

Une mesure instantanée permet d'observer l'état actuel, mais ne suffit pas à identifier une dérive.

Enregistrer les séries temporelles aide à comparer le comportement avant et après une intervention.

Exemples :

- température pendant les heures de pointe ;
- erreurs de réception avant et après remplacement d'un câble ;
- consommation PoE avant et après l'ajout de points d'accès ;
- niveaux optiques après nettoyage des connecteurs ;
- taux d'utilisation des uplinks lors d'un événement connu.

## 10.3 Distinguer corrélation et cause

Une hausse de température observée en même temps qu'une dégradation du trafic ne prouve pas automatiquement que la température est la cause.

Il faut vérifier les seuils, la chronologie, les événements, les autres variables et les recommandations du constructeur.

Un diagnostic doit expliquer quelles observations soutiennent la conclusion et quelles incertitudes restent.

## 10.4 Capture, compteurs et diagnostic

La capture de paquets permet d'observer le trafic à un point précis, tandis que les compteurs donnent des informations sur les interfaces et les erreurs.

Ces données sont complémentaires. Une capture ne voit que ce qui atteint son point d'observation, et un compteur peut être agrégé ou dépendre de l'implémentation.

Pour une panne matérielle, croisez les mesures avec le plan de câblage, l'état des interfaces, les journaux et les conditions de charge.


# 11. Sélection technique et validation

## 11.1 Construire une matrice de sélection

Pour comparer plusieurs équipements, créez un tableau de critères comprenant au minimum :

| Critère | Exigence | Preuve à examiner |
|---|---|---|
| Ports | Nombre, type et débits requis | Fiche technique et configuration |
| Capacité | Profil de trafic attendu | Méthodologie d'essai et capacités annoncées |
| PoE | Puissance par port et budget total | Documentation du modèle |
| Optiques | Modules et distances compatibles | Matrices de compatibilité |
| Redondance | Liens, alimentations et fonctions attendues | Guide matériel et tests |
| Sécurité | Fonctions requises | Documentation logicielle |
| Supervision | Données nécessaires à l'exploitation | Guides des interfaces de gestion |
| Énergie | Charge nominale et dégradée | Mesures et spécifications |
| Refroidissement | Environnement compatible | Guide d'installation |
| Cycle de vie | Support et pièces disponibles | Publications du fournisseur |

Ne donnez pas un score unique sans expliquer comment les exigences critiques sont pondérées.

Certaines exigences doivent constituer des critères obligatoires plutôt que des avantages facultatifs.

## 11.2 Vérifications avant réception

Lors de la réception d'un lot de matériels :

1. contrôler les références commandées ;
2. vérifier les dommages physiques ;
3. comparer les numéros d'actifs à l'inventaire ;
4. vérifier les modules et accessoires ;
5. confirmer les versions logicielles et la compatibilité prévue ;
6. inspecter les alimentations ;
7. vérifier les besoins de montage et de refroidissement ;
8. tester les fonctions prévues dans un environnement adapté ;
9. consigner les écarts ;
10. accepter la réception uniquement selon les critères définis.

## 11.3 Tests de recette

Une recette peut comprendre des essais de :

- liaison et négociation des interfaces ;
- débit selon un profil défini ;
- capacité PoE ;
- redondance ;
- télémétrie ;
- redémarrage et récupération ;
- fonctionnement avec la configuration approuvée ;
- alarmes et supervision ;
- procédures de remplacement.

Les résultats doivent être associés à des versions, des conditions de test et des critères d'acceptation explicites.


# 12. Architecture de référence

## 12.1 Vue physique et opérationnelle

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="410" viewBox="0 0 1000 410" role="img" aria-labelledby="expert-hw-arch-title expert-hw-arch-desc">
  <title id="expert-hw-arch-title">Architecture matérielle résiliente de référence</title>
  <desc id="expert-hw-arch-desc">Les terminaux rejoignent des switches d'accès, qui sont connectés à une distribution redondante. Les équipements de distribution disposent de chemins distincts vers la bordure. L'alimentation et la supervision couvrent l'ensemble, mais leurs propres domaines de panne doivent être étudiés.</desc>
  <defs>
    <marker id="hw-arch-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .ha-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .ha-power{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .ha-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .ha-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .ha-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#hw-arch-arrow);animation:ha-dash 1.8s linear infinite}
      .ha-alt{fill:none;stroke:#c4b5fd;stroke-width:3;stroke-dasharray:7 7;animation:ha-dash 1.8s linear infinite}
      @keyframes ha-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="408" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">MATÉRIEL, DIVERSITÉ DES CHEMINS ET EXPLOITATION</text>
  <rect class="ha-box" x="25" y="85" width="175" height="70" rx="10"/>
  <text class="ha-title" x="112" y="113" text-anchor="middle">Accès</text>
  <text class="ha-text" x="112" y="135" text-anchor="middle">Terminaux + PoE</text>
  <rect class="ha-box" x="280" y="55" width="180" height="70" rx="10"/>
  <text class="ha-title" x="370" y="83" text-anchor="middle">Distribution A</text>
  <text class="ha-text" x="370" y="105" text-anchor="middle">Chemin principal</text>
  <rect class="ha-box" x="280" y="155" width="180" height="70" rx="10"/>
  <text class="ha-title" x="370" y="183" text-anchor="middle">Distribution B</text>
  <text class="ha-text" x="370" y="205" text-anchor="middle">Chemin alternatif</text>
  <rect class="ha-box" x="540" y="85" width="190" height="70" rx="10"/>
  <text class="ha-title" x="635" y="113" text-anchor="middle">Cœur / bordure</text>
  <text class="ha-text" x="635" y="135" text-anchor="middle">Routage et transfert</text>
  <rect class="ha-box" x="790" y="85" width="180" height="70" rx="10"/>
  <text class="ha-title" x="880" y="113" text-anchor="middle">Services distants</text>
  <text class="ha-text" x="880" y="135" text-anchor="middle">Datacenter / WAN</text>
  <path class="ha-flow" d="M200 105 L272 90"/>
  <path class="ha-alt" d="M200 135 L272 190"/>
  <path class="ha-flow" d="M460 90 L532 108"/>
  <path class="ha-alt" d="M460 190 L532 135"/>
  <path class="ha-flow" d="M730 120 H782"/>
  <rect class="ha-power" x="120" y="285" width="320" height="65" rx="10"/>
  <text class="ha-title" x="280" y="312" text-anchor="middle">Alimentation et refroidissement</text>
  <text class="ha-text" x="280" y="333" text-anchor="middle">Capacité en mode normal et dégradé</text>
  <rect class="ha-box" x="560" y="285" width="320" height="65" rx="10"/>
  <text class="ha-title" x="720" y="312" text-anchor="middle">Supervision et inventaire</text>
  <text class="ha-text" x="720" y="333" text-anchor="middle">Alarmes, versions, liens et mesures</text>
  <text class="ha-text" x="500" y="380" text-anchor="middle">Des chemins logiques différents ne garantissent pas une diversité physique.</text>
</svg>

## 12.2 Principes de conception

Une infrastructure matérielle doit garantir, selon ses exigences :

**Capacité :** les équipements et liens traitent les profils de charge prévus.

**Compatibilité :** les interfaces, câbles, modules et alimentations sont validés ensemble.

**Résilience :** les pannes prévues peuvent être tolérées dans les limites définies.

**Observabilité :** les composants exposent assez d'informations pour identifier les dégradations.

**Maintenabilité :** les pièces de rechange, versions, accès et procédures sont maîtrisés.

**Sécurité :** les interventions physiques et les accès de gestion sont contrôlés.

**Récupération :** le remplacement ou la bascule peut être exécuté et vérifié.


# 13. Atelier expert

## Scénario

Une entreprise doit rénover la distribution réseau de son bâtiment principal. Le réseau connecte des postes utilisateurs, des points d'accès Wi-Fi, des serveurs et des systèmes de gestion. Les services doivent rester accessibles pendant les opérations prévues.

Vous devez concevoir la stratégie de sélection et de validation du matériel, sans remplacer directement les équipements de production.

## Étape A — Collecter les besoins

Documentez :

- les ports et débits actuels ;
- le trafic agrégé sur les uplinks ;
- la croissance prévue ;
- les terminaux PoE ;
- les besoins de routage et de sécurité ;
- la densité des fibres et les distances ;
- les exigences de disponibilité ;
- les limites de la baie et des circuits électriques.

## Étape B — Construire une matrice de comparaison

Pour chaque matériel candidat, comparez les caractéristiques obligatoires, les limites, le coût de maintenance et les preuves disponibles.

Les critères essentiels doivent être documentés avant l'attribution de scores.

## Étape C — Dimensionner l'optique et le PoE

Vérifiez la compatibilité des transceivers et le budget optique pour chaque liaison prévue.

Calculez le budget PoE à partir des besoins des terminaux et examinez le mode dégradé en cas de perte d'une alimentation.

## Étape D — Concevoir les domaines de panne

Identifiez les chemins alternatifs et leurs dépendances physiques.

Vérifiez si les liens supposés redondants partagent un même conduit, équipement, circuit ou chemin opérateur.

## Étape E — Définir les tests de recette

Prévoyez des tests de :

- compatibilité et établissement des liens ;
- performances dans des conditions identifiées ;
- charge PoE ;
- défaillance d'un chemin ;
- dégradation d'une alimentation ;
- alarmes et supervision ;
- retour à l'état normal après le test.

## Étape F — Préparer la maintenance

Définissez les sauvegardes, l'identification des câbles, les procédures de remplacement, les pièces de rechange, les critères de retour arrière et les responsables des interventions.

L'atelier est réussi lorsque le choix matériel repose sur des besoins mesurables et une stratégie de validation réaliste.


# 14. Étude de défaillance

## Situation

Un lien entre deux switches est annoncé à 100 Gb/s, mais les utilisateurs observent des pertes et des ralentissements lorsque le trafic est élevé.

## 14.1 Hypothèses possibles

La vitesse du lien ne permet pas d'identifier la cause.

Les hypothèses à examiner incluent :

- congestion sur le lien ou ailleurs dans le chemin ;
- abandons dans les files d'attente ;
- capacité limitée d'un port ou d'un équipement intermédiaire ;
- erreurs physiques ;
- incompatibilité ou défaut d'un transceiver ;
- trafic asymétrique ;
- restriction imposée par une politique de sécurité ou de qualité de service ;
- faibles ressources disponibles sur la plateforme dans la configuration considérée.

## 14.2 Démarche

1. relever les compteurs des interfaces et leur évolution ;
2. vérifier les niveaux optiques lorsqu'ils sont exposés ;
3. examiner les erreurs et changements d'état ;
4. comparer l'utilisation des liens et les files d'attente ;
5. vérifier le chemin complet et la capacité des autres interfaces ;
6. analyser les profils de trafic ;
7. vérifier les règles et fonctions activées ;
8. effectuer un test contrôlé et représentatif lorsque cela est autorisé ;
9. appliquer une correction documentée ;
10. refaire les mesures dans des conditions comparables.

## 14.3 Leçon principale

Une interface rapide ne garantit pas la performance de l'ensemble du chemin.

La performance est une propriété du système : interfaces, capacités de transfert, mémoire, charge, politiques, supports et chemins doivent fonctionner ensemble.


# 15. Évaluation corrigée

## Questions

1. Quel est le rôle d'un ASIC dans une plateforme réseau ?
2. Pourquoi le CPU de contrôle et le plan de données doivent-ils être distingués ?
3. Quelle différence existe entre capacité en Gb/s et débit en paquets par seconde ?
4. Pourquoi les buffers peuvent-ils affecter les performances ?
5. Comment calculer une puissance optique reçue estimée ?
6. Pourquoi faut-il examiner la puissance minimale et maximale du récepteur ?
7. Pourquoi le budget PoE doit-il être vérifié en mode dégradé ?
8. Qu'est-ce qu'un domaine de panne ?
9. Pourquoi la redondance logique ne garantit-elle pas la diversité physique ?
10. Que représente l'estimation simplifiée de disponibilité basée sur MTBF et MTTR ?
11. Pourquoi une baseline de télémétrie est-elle utile ?
12. Pourquoi un test de recette doit-il définir des conditions mesurables ?

## Corrigé

**1. ASIC**

Un circuit spécialisé accélère certaines fonctions de traitement ou de transfert selon la conception de la plateforme.

**2. CPU et plan de données**

Le CPU exécute certaines fonctions de contrôle et de gestion ; le plan de données effectue le transfert des paquets selon l'architecture de l'équipement.

**3. Gb/s et pps**

Le débit en bits par seconde mesure un volume de données par temps ; le débit en paquets par seconde mesure le nombre de paquets traités par temps.

**4. Buffers**

Ils absorbent temporairement les différences entre les débits d'arrivée et de sortie. Une congestion peut remplir les files et conduire à des abandons.

**5. Puissance optique reçue**

On estime la puissance reçue en soustrayant les pertes totales, exprimées en dB, à la puissance d'émission exprimée en dBm.

**6. Limites du récepteur**

Une puissance insuffisante peut rendre la liaison instable, tandis qu'une puissance excessive peut dépasser les limites du module.

**7. PoE en mode dégradé**

La perte d'une alimentation peut réduire la puissance totale disponible. Il faut vérifier que les terminaux prioritaires peuvent continuer à fonctionner.

**8. Domaine de panne**

Ensemble de composants susceptibles de subir les conséquences d'un même événement.

**9. Diversité physique**

Deux chemins logiques peuvent partager une fibre, un conduit, une baie, un circuit ou un équipement intermédiaire.

**10. MTBF et MTTR**

L'estimation donne une indication de la disponibilité sous certaines hypothèses. Elle ne représente pas automatiquement la disponibilité réelle de bout en bout.

**11. Baseline**

Elle permet de comparer le comportement présent à une référence et de repérer des changements significatifs.

**12. Tests de recette mesurables**

Ils rendent possible une décision objective sur la conformité du matériel et sur son aptitude à être accepté.


# Conclusion — Le niveau expert

L'ingénierie matérielle réseau consiste à relier les exigences de l'infrastructure aux capacités mesurables de chaque composant.

Un équipement approprié doit :

- traiter les volumes de trafic attendus ;
- fonctionner avec les supports et modules prévus ;
- respecter les limites énergétiques et thermiques ;
- offrir les fonctions et interfaces nécessaires ;
- permettre le diagnostic ;
- être maintenable pendant son cycle de vie ;
- résister aux scénarios de panne définis ;
- pouvoir être validé avant sa mise en service.

La progression est maintenant complète :

**Débutant :** reconnaître les équipements, ports, câbles et fonctions.

**Intermédiaire :** sélectionner, dimensionner, câbler et dépanner les équipements.

**Expert :** évaluer la capacité réelle, concevoir la résilience et maîtriser la fiabilité du système physique.

**Le meilleur choix matériel n'est pas l'équipement qui affiche le plus grand nombre : c'est celui qui répond aux exigences mesurables, s'intègre correctement à l'architecture et peut être maintenu et vérifié tout au long de son cycle de vie.**


## Références utiles

- IEEE 802.3 — Ethernet : https://standards.ieee.org/ieee/7003/10422/
- IEEE 802.1Q — VLAN et pontage : https://standards.ieee.org/ieee/8802-1Q_2024_Amd.35_2024/11823/802.1Q/10323/
- Documentation PoE Cisco : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/infra/poe/poe-configuration-guide/g-poe/c-poe.html
- Guide des composants matériels Juniper : https://www.juniper.net/documentation/us/en/software/junos/junos-overview/topics/concept/junos-software-routing-platforms-hardware-components.html
- Documentation matérielle Juniper : https://www.juniper.net/documentation/
- Guide matériel des switches Juniper EX9208 : https://www.juniper.net/documentation/us/en/hardware/ex9208/index.html

**Fichier :** `materiel-reseau-expert.md`  
**Niveau :** Expert  
**Fin du cours**
