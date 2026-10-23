
# Le matériel réseau — Niveau intermédiaire

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** connaître les équipements réseau, les supports de transmission, les ports et les notions élémentaires d'adressage.  
> **Objectif :** choisir et dimensionner du matériel réseau adapté, comprendre les interfaces et modules, planifier une installation et diagnostiquer méthodiquement les problèmes physiques.

---

## Sommaire

1. Objectifs et méthode de conception
2. Choisir un switch
3. Comprendre les ports et les capacités
4. Concevoir une architecture physique
5. Choisir les câbles et modules optiques
6. Dimensionner le PoE
7. Alimentations, refroidissement et baies
8. Routeurs et pare-feu matériels
9. Redondance et disponibilité
10. Diagnostic matériel structuré
11. Atelier de dimensionnement
12. Étude de panne
13. Évaluation corrigée
14. Préparation du niveau expert

---

# 1. Objectifs et méthode de conception

## 1.1 Passer de l'identification au choix technique

Au niveau débutant, nous avons identifié le rôle des équipements et leurs principaux composants.

Au niveau intermédiaire, nous devons déterminer quel matériel convient réellement à une installation.

Un switch peut disposer de 48 ports tout en étant inadapté à un déploiement si ses uplinks sont trop limités, si son budget PoE est insuffisant ou si ses fonctions de supervision ne répondent pas aux exigences.

Le choix du matériel doit tenir compte de l'ensemble de la chaîne : terminaux, câbles, interfaces, alimentation, architecture et exploitation.

## 1.2 Objectifs pédagogiques

À la fin du cours, vous serez capable de :

- comparer plusieurs modèles de switches ;
- comprendre les notions de débit par port, capacité de commutation et débit de transfert ;
- identifier les limites des uplinks ;
- préparer un plan de câblage ;
- distinguer les principales familles de modules optiques ;
- calculer un budget PoE élémentaire ;
- prévoir l'alimentation et le refroidissement ;
- comprendre le rôle d'une baie réseau ;
- diagnostiquer une liaison instable ou sous-performante ;
- reconnaître les limites d'une simple vérification de lien.

## 1.3 Les questions à poser avant d'acheter

Avant de sélectionner un appareil, précisez :

1. combien de ports sont nécessaires aujourd'hui ;
2. combien de ports sont prévus après extension ;
3. quels débits sont requis ;
4. quels terminaux ont besoin du PoE ;
5. quelles distances doivent être couvertes ;
6. quelles fonctions de routage et de segmentation sont nécessaires ;
7. quels mécanismes de redondance sont souhaités ;
8. comment l'équipement sera administré, surveillé et remplacé en cas de panne.

Une fiche technique doit être interprétée dans ce contexte. La caractéristique la plus élevée n'est pas nécessairement la plus utile pour le besoin réel.

---

# 2. Choisir un switch

## 2.1 Nombre de ports

Les switches d'accès offrent couramment 8, 24 ou 48 ports cuivre, mais d'autres formats existent.

Le nombre de ports doit couvrir les terminaux actuels, les ports réservés, les uplinks et une marge raisonnable pour l'évolution.

Exemple : si un étage compte 34 terminaux filaires, un switch de 48 ports peut sembler suffisant. Mais il faut également examiner les points d'accès, téléphones IP, imprimantes, extensions et besoins d'alimentation.

La capacité en nombre de ports ne doit pas être confondue avec la capacité de traitement globale.

## 2.2 Débit par port

Les interfaces peuvent prendre en charge différents débits Ethernet, par exemple 1 Gb/s, 2,5 Gb/s, 5 Gb/s, 10 Gb/s ou davantage selon le matériel.

Le débit utilisable dépend des capacités des deux extrémités et du support.

Une interface 10 Gb/s connectée à un terminal 1 Gb/s ne transforme pas le terminal en appareil 10 Gb/s. Le lien négocie un mode compatible selon les possibilités des interfaces.

## 2.3 Capacité de commutation

La capacité de commutation, souvent annoncée en Gb/s ou Tb/s, représente une caractéristique de la plateforme.

Il faut vérifier la méthode de calcul de la valeur publiée : elle peut exprimer une capacité totale théorique incluant plusieurs directions ou ports.

Elle ne doit pas être interprétée isolément comme une garantie du débit utile pour toutes les combinaisons de trafic.

## 2.4 Débit de transfert en paquets

Certains fabricants indiquent un débit maximal en paquets par seconde (pps).

Cette valeur complète la capacité de commutation. Le traitement de nombreux petits paquets peut imposer des exigences différentes de celles d'un trafic composé de grands paquets.

Pour comparer des matériels, identifiez les conditions de mesure, la taille des paquets et les fonctionnalités activées.

## 2.5 Uplinks

Les uplinks relient le switch aux autres équipements du réseau.

Ils peuvent utiliser des ports cuivre multigigabits ou des interfaces optiques.

Si plusieurs switches d'accès concentrent leur trafic sur un seul uplink insuffisant, cet uplink peut devenir un goulot d'étranglement.

Il faut donc étudier le trafic agrégé, les destinations, les flux entre utilisateurs et serveurs et les besoins de redondance.

## 2.6 Tableau de sélection

| Critère | Question de conception |
|---|---|
| Ports d'accès | Combien de terminaux doivent être connectés ? |
| Débit par port | Quels débits les terminaux requièrent-ils ? |
| Uplinks | Quel débit doit remonter vers la distribution ? |
| VLAN | L'appareil prend-il en charge les fonctions de segmentation nécessaires ? |
| Routage | Le switch doit-il assurer du routage de couche 3 ? |
| PoE | Quelle puissance totale est nécessaire ? |
| Supervision | Quelles données et fonctions d'administration sont requises ? |
| Redondance | Quelles alimentations et liaisons de secours sont nécessaires ? |
| Environnement | Le refroidissement, le bruit et les dimensions conviennent-ils ? |
| Support logiciel | Pendant combien de temps les mises à jour sont-elles prévues ? |

---

# 3. Comprendre les ports et les capacités

## 3.1 Interfaces cuivre

Les ports cuivre Ethernet utilisent généralement des connecteurs modulaires compatibles avec le câblage à paires torsadées.

Le débit et la distance supportés dépendent de la technologie Ethernet, du câble, de la qualité de la pose et de l'environnement.

Les câbles doivent être correctement terminés. Une liaison peut fonctionner tout en présentant des erreurs qui augmentent avec la charge ou la température.

## 3.2 Ports SFP et QSFP

Des équipements professionnels proposent des logements pour modules amovibles, notamment :

- SFP ;
- SFP+ ;
- SFP28 ;
- QSFP+ ;
- QSFP28 ;
- d'autres formats selon la plateforme.

Ces appellations correspondent à des familles de formats et de capacités. Le format mécanique, le débit, l'encodage, la compatibilité logicielle et les supports optiques sont des éléments distincts.

Un logement qui accepte physiquement un module ne garantit pas son fonctionnement dans toutes les configurations.

## 3.3 Uplink et agrégation de liens

Un uplink simple relie un switch à un équipement amont.

Une agrégation de liens peut réunir plusieurs liaisons Ethernet dans un groupe logique, souvent avec LACP lorsque la technologie et les deux extrémités le prennent en charge.

Cette agrégation peut augmenter la capacité globale disponible pour différents flux et améliorer la tolérance à la perte d'un lien.

Elle ne garantit pas qu'un flux unique atteindra la somme des débits des liens physiques, car la répartition repose généralement sur un mécanisme de hachage ou d'équilibrage.

## 3.4 Exemple de dimensionnement

Supposons que quatre switches d'accès disposent chacun d'un uplink de 10 Gb/s vers un équipement de distribution.

Le fait que leur somme théorique atteigne 40 Gb/s ne signifie pas que chaque switch disposera toujours de 10 Gb/s de débit utile sans contention.

Il faut examiner :

- le trafic simultané ;
- la destination des flux ;
- les capacités des uplinks ;
- les éventuels chemins alternatifs ;
- les mécanismes de répartition ;
- les limitations de la plateforme ;
- les scénarios de panne où une partie des liens n'est plus disponible.

Le dimensionnement doit considérer les conditions normales et les modes dégradés.

## 3.5 Lire correctement une fiche technique

Les valeurs publiées doivent être associées à une définition précise.

Par exemple, « 176 Gb/s de capacité » n'indique pas nécessairement le débit utile pour une seule direction ni celui d'un flux précis.

De même, le nombre de ports, les capacités de routage, la table MAC maximale, la mémoire de buffers et le nombre de règles pris en charge peuvent être soumis à des limites différentes.

Une comparaison pertinente vérifie les propriétés qui comptent pour l'architecture envisagée.

---

# 4. Concevoir une architecture physique

## 4.1 Accès, distribution et cœur

Dans certaines architectures de campus, les équipements sont organisés en couches :

- **Accès :** connexion des utilisateurs, terminaux et points d'accès ;
- **Distribution :** agrégation, routage et politiques selon la conception ;
- **Cœur :** transport rapide entre les blocs de distribution ou les domaines majeurs.

Cette organisation dépend de la taille et des objectifs de l'infrastructure. Les petites installations peuvent utiliser une architecture simplifiée.

## 4.2 Schéma physique d'un réseau d'entreprise

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="phys-title phys-desc">
  <title id="phys-title">Organisation physique d'un réseau de campus</title>
  <desc id="phys-desc">Les équipements d'accès connectent les terminaux, les switches de distribution agrègent les liens et le cœur transporte le trafic vers les équipements de bordure. Les liaisons directionnelles sont animées avec des tirets et sans particule mobile.</desc>
  <defs>
    <marker id="phys-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .ph-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .ph-core{fill:#302044;stroke:#c4b5fd;stroke-width:2}
      .ph-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .ph-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .ph-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#phys-arrow);animation:ph-dash 1.8s linear infinite}
      @keyframes ph-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="388" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DE L'ACCÈS AU CŒUR DU RÉSEAU</text>
  <rect class="ph-box" x="30" y="70" width="190" height="75" rx="10"/>
  <text class="ph-title" x="125" y="100" text-anchor="middle">Terminaux</text>
  <text class="ph-text" x="125" y="123" text-anchor="middle">PC, téléphones, AP</text>
  <rect class="ph-box" x="280" y="70" width="190" height="75" rx="10"/>
  <text class="ph-title" x="375" y="100" text-anchor="middle">Switch d'accès</text>
  <text class="ph-text" x="375" y="123" text-anchor="middle">Ports terminaux</text>
  <rect class="ph-box" x="530" y="70" width="190" height="75" rx="10"/>
  <text class="ph-title" x="625" y="100" text-anchor="middle">Distribution</text>
  <text class="ph-text" x="625" y="123" text-anchor="middle">Agrégation et politiques</text>
  <rect class="ph-core" x="780" y="70" width="190" height="75" rx="10"/>
  <text class="ph-title" x="875" y="100" text-anchor="middle">Cœur / bordure</text>
  <text class="ph-text" x="875" y="123" text-anchor="middle">Transport vers l'extérieur</text>
  <path class="ph-flow" d="M220 108 H272"/>
  <path class="ph-flow" d="M470 108 H522"/>
  <path class="ph-flow" d="M720 108 H772"/>
  <rect class="ph-box" x="180" y="220" width="640" height="80" rx="12"/>
  <text class="ph-title" x="500" y="249" text-anchor="middle">Infrastructure physique</text>
  <text class="ph-text" x="500" y="273" text-anchor="middle">Baies, câblage, fibres, alimentations, refroidissement et documentation</text>
  <path class="ph-flow" d="M375 145 V192 H350 V212"/>
  <path class="ph-flow" d="M625 145 V192 H650 V212"/>
  <text class="ph-text" x="500" y="337" text-anchor="middle">Le nombre de couches et les rôles précis dépendent du dimensionnement.</text>
  <text class="ph-text" x="500" y="357" text-anchor="middle">Les liens et les équipements doivent être choisis pour les flux attendus et les pannes possibles.</text>
</svg>

## 4.3 Baie et câblage structuré

Une baie réseau organise les équipements, les panneaux de brassage et les câbles.

Le panneau de brassage termine les câbles du câblage structuré. Des cordons relient ensuite les ports du panneau aux ports des switches.

Cette organisation sépare le câblage permanent du brassage actif et améliore la maintenance.

Une installation doit respecter les règles de câblage, le rayon de courbure, les cheminements, l'identification et les contraintes de poids et de ventilation.

## 4.4 Marquage et documentation

Chaque câble devrait posséder une identification cohérente aux deux extrémités, reliée à un plan de ports et à un emplacement.

Une documentation utile précise notamment :

- l'origine et la destination ;
- le type de câble ;
- la longueur approximative ;
- le panneau et le port ;
- l'équipement et son interface ;
- la date et le résultat des tests ;
- les éventuelles réserves.

Un câble non identifié augmente le temps d'intervention et le risque de déconnecter un service incorrect.

---

# 5. Choisir les câbles et modules optiques

## 5.1 Vérifier la chaîne complète

Une liaison optique dépend de plusieurs éléments :

- l'interface du premier équipement ;
- le transceiver d'émission ;
- le type de fibre ;
- les connecteurs et panneaux intermédiaires ;
- le transceiver de réception ;
- l'interface de l'équipement distant.

Les deux extrémités doivent être compatibles, notamment en débit, longueur d'onde et type de fibre.

## 5.2 SFP ne signifie pas « compatible avec tout »

Deux modules utilisant le même format physique peuvent fonctionner avec des technologies optiques différentes.

Les caractéristiques à vérifier comprennent :

- le format du module ;
- le débit et le protocole pris en charge ;
- la longueur d'onde ;
- la fibre monomode ou multimode ;
- le connecteur optique ;
- la distance spécifiée ;
- la puissance optique d'émission et la sensibilité du récepteur ;
- la compatibilité avec l'équipement et sa version logicielle.

Les indications commerciales telles que SR, LR ou ER sont associées à des familles d'interfaces. Leur usage doit être vérifié dans la documentation du matériel retenu.

## 5.3 Budget optique

Pour une liaison fibre, il faut s'assurer que la puissance reçue se trouve dans la plage acceptée par le récepteur.

Le calcul doit tenir compte notamment de :

- l'atténuation de la fibre ;
- l'atténuation des connecteurs ;
- les pertes des épissures ;
- les autres éléments passifs ;
- la marge de conception ;
- les plages minimales et maximales des transceivers.

Une puissance trop faible peut empêcher la réception correcte. Une puissance trop élevée peut également être hors des limites acceptables.

Ne choisissez pas une optique uniquement en fonction de la distance annoncée. Vérifiez aussi la compatibilité, le budget optique et les limites des interfaces.

## 5.4 Inspection et nettoyage

Les connecteurs optiques doivent être inspectés et nettoyés avec des outils adaptés avant le raccordement lorsque la procédure l'exige.

La poussière ou une contamination peut provoquer une perte optique ou des erreurs intermittentes.

Ne regardez jamais directement dans une fibre ou un port optique. Respectez les consignes de sécurité et utilisez les instruments d'inspection appropriés.

## 5.5 Test du câblage cuivre

Un testeur élémentaire peut détecter certaines erreurs de brochage ou des coupures.

Un test de continuité ne garantit toutefois pas que le câble respecte toutes les performances de la catégorie prévue.

Pour certifier une installation de câblage structuré, utilisez un instrument adapté et suivez les normes et critères du projet.

---

# 6. Dimensionner le PoE

## 6.1 Trois limites différentes

Pour un déploiement PoE, il faut distinguer :

1. la puissance maximale prise en charge par chaque port ;
2. le budget de puissance total du switch ;
3. la puissance nécessaire à chaque terminal, compte tenu des règles de dimensionnement applicables.

Un switch peut disposer de nombreux ports PoE sans pouvoir fournir simultanément la puissance maximale sur tous ses ports.

## 6.2 Exemple de calcul élémentaire

Supposons un switch auquel sont connectés :

- 8 téléphones IP, avec un besoin maximal de 7 W chacun ;
- 4 points d'accès, avec un besoin maximal de 20 W chacun.

La somme des besoins retenus dans cet exemple est :

\[
P = (8 \times 7) + (4 \times 20)
\]

\[
P = 56 + 80 = 136\ \text{W}
\]

Le dimensionnement doit ensuite tenir compte des limites de puissance aux ports, des règles de la technologie PoE utilisée, du budget réel du switch et d'une marge définie selon la politique de l'organisation.

Ce calcul n'inclut pas automatiquement les pertes entre le PSE et les appareils ni les exigences supplémentaires propres aux terminaux. Consultez les fiches techniques des deux côtés.

## 6.3 Ne pas confondre les Watts et le débit

Les capacités réseau et les capacités d'alimentation sont des dimensions différentes.

Un switch peut avoir des uplinks rapides tout en disposant d'un faible budget PoE. À l'inverse, un switch PoE puissant peut avoir des interfaces de données insuffisantes pour le trafic agrégé.

Le choix doit évaluer simultanément le débit, la puissance et les fonctions.

## 6.4 Alimentations redondantes

Si un appareil dispose de deux alimentations, vérifiez :

- le mode de redondance annoncé ;
- la puissance disponible lorsqu'une seule alimentation fonctionne ;
- les besoins de la charge PoE ;
- les circuits électriques utilisés ;
- les alertes d'alimentation ;
- les procédures de remplacement à chaud, si le modèle les autorise.

Deux modules d'alimentation branchés sur le même circuit ou la même source défaillante ne garantissent pas une continuité d'alimentation complète.

---

# 7. Alimentations, refroidissement et baies

## 7.1 Alimentation électrique

Avant l'installation, vérifiez la tension, la fréquence, la puissance disponible et les exigences spécifiques des équipements.

Dans une baie importante, la somme de la consommation des équipements doit être comparée à la capacité des circuits et des systèmes d'alimentation.

Il est également nécessaire d'anticiper les pics, les alimentations redondantes et les conditions de fonctionnement en mode dégradé.

## 7.2 UPS et protection électrique

Un onduleur (UPS) peut fournir temporairement de l'énergie en cas de coupure, selon sa capacité et sa charge.

Il peut également offrir des fonctions de conditionnement et de gestion de l'alimentation.

Le choix doit prendre en compte la puissance totale, l'autonomie souhaitée, le type de charge, les batteries, la maintenance et le comportement des appareils lorsque l'autonomie s'épuise.

Un onduleur ne remplace pas une architecture électrique correctement conçue et entretenue.

## 7.3 Refroidissement et flux d'air

Les équipements de réseau produisent de la chaleur. Une baie dense peut nécessiter une gestion attentive du flux d'air.

Vérifiez :

- le sens d'admission et de sortie d'air ;
- les distances et dégagements nécessaires ;
- la température admissible ;
- la charge thermique globale ;
- le nettoyage des filtres ;
- le bon état des ventilateurs ;
- l'effet de la perte d'un ventilateur ou d'une alimentation.

Une température excessive peut entraîner des alertes, une réduction de fonctionnement ou une panne.

## 7.4 Unités de rack

Les dimensions des équipements montés en rack sont souvent exprimées en unités `U`.

Une unité rack correspond à une hauteur normalisée de 44,45 mm. Les équipements peuvent occuper différentes hauteurs selon leur format.

La compatibilité mécanique doit également tenir compte du poids, de la profondeur, des rails, du dégagement pour les câbles et de la ventilation.

---

# 8. Routeurs et pare-feu matériels

## 8.1 Sélectionner un routeur

Le choix d'un routeur ne dépend pas uniquement du débit nominal de ses interfaces.

Il faut examiner :

- le débit de transfert pour le profil de paquets attendu ;
- les performances avec les fonctions de sécurité activées ;
- le nombre et le type d'interfaces ;
- les capacités de routage ;
- les tables et protocoles requis ;
- les VPN et services nécessaires ;
- la mémoire, le stockage et les fonctions de haute disponibilité ;
- les mécanismes d'administration et de télémétrie.

Un équipement prévu pour un environnement simple peut être insuffisant pour un nombre élevé de routes, de sessions ou de tunnels.

## 8.2 Sélectionner un pare-feu

Les performances d'un pare-feu varient selon les fonctions activées.

Il faut notamment considérer :

- les politiques de filtrage ;
- le nombre de sessions simultanées ;
- les nouvelles connexions par seconde ;
- l'inspection applicative ;
- les VPN ;
- les fonctions de prévention et de détection ;
- la journalisation ;
- les exigences de disponibilité.

Une valeur de débit annoncée sans préciser le profil de trafic et les services activés peut ne pas refléter le comportement réel de l'appareil.

## 8.3 Appliance physique ou fonction virtuelle

Un routeur ou un pare-feu peut être implémenté dans un appareil dédié ou sous la forme d'un logiciel exécuté sur un serveur ou une plateforme virtuelle.

Une version virtuelle dépend alors également de l'hôte, de l'hyperviseur, des interfaces réseau et des ressources affectées.

L'évaluation doit porter sur la solution complète plutôt que sur le seul logiciel ou le seul serveur.

---

# 9. Redondance et disponibilité

## 9.1 Identifier les points uniques de défaillance

Un point unique de défaillance est un composant dont l'indisponibilité peut interrompre une fonction critique sans solution de repli suffisante.

Exemples :

- un unique switch d'accès ;
- un seul uplink ;
- une seule alimentation ;
- une seule liaison opérateur ;
- une seule source électrique ;
- un système de refroidissement sans solution de secours ;
- un unique point de gestion pour plusieurs services.

La gravité dépend des services affectés et de la possibilité de récupération.

## 9.2 Redondance logique et diversité réelle

Deux liaisons redondantes peuvent partager un même chemin physique ou un même équipement intermédiaire.

Si un incident commun affecte ce composant, les deux liens peuvent tomber en même temps.

L'analyse doit examiner les chemins de bout en bout : câbles, panneaux de brassage, fibres, équipements, alimentations, circuits électriques et opérateurs.

## 9.3 Schéma d'une architecture redondante

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-labelledby="red-mid-title red-mid-desc">
  <title id="red-mid-title">Redondance physique entre accès et distribution</title>
  <desc id="red-mid-desc">Deux switches d'accès disposent de chemins vers deux équipements de distribution. Les chemins permettent de représenter une architecture redondante, mais leur indépendance physique doit être vérifiée séparément.</desc>
  <defs>
    <marker id="red-mid-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .rm-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .rm-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .rm-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .rm-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#red-mid-arrow);animation:rm-dash 1.8s linear infinite}
      .rm-alt{fill:none;stroke:#c4b5fd;stroke-width:3;stroke-dasharray:6 7;animation:rm-dash 1.8s linear infinite}
      @keyframes rm-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="368" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DEUX CHEMINS, MAIS PAS NÉCESSAIREMENT DEUX INFRASTRUCTURES INDÉPENDANTES</text>
  <rect class="rm-box" x="25" y="100" width="190" height="74" rx="10"/>
  <text class="rm-title" x="120" y="129" text-anchor="middle">Switch d'accès A</text>
  <text class="rm-text" x="120" y="151" text-anchor="middle">Terminaux</text>
  <rect class="rm-box" x="25" y="225" width="190" height="74" rx="10"/>
  <text class="rm-title" x="120" y="254" text-anchor="middle">Switch d'accès B</text>
  <text class="rm-text" x="120" y="276" text-anchor="middle">Terminaux</text>
  <rect class="rm-box" x="745" y="100" width="190" height="74" rx="10"/>
  <text class="rm-title" x="840" y="129" text-anchor="middle">Distribution A</text>
  <text class="rm-text" x="840" y="151" text-anchor="middle">Chemin 1</text>
  <rect class="rm-box" x="745" y="225" width="190" height="74" rx="10"/>
  <text class="rm-title" x="840" y="254" text-anchor="middle">Distribution B</text>
  <text class="rm-text" x="840" y="276" text-anchor="middle">Chemin 2</text>
  <path class="rm-flow" d="M215 118 C390 55 575 55 737 118"/>
  <path class="rm-alt" d="M215 156 C400 200 570 200 737 260"/>
  <path class="rm-alt" d="M215 260 C390 190 575 190 737 138"/>
  <path class="rm-flow" d="M215 280 C390 345 575 345 737 280"/>
  <text class="rm-text" x="480" y="180" text-anchor="middle">Liens et équipements de secours</text>
  <text class="rm-text" x="480" y="204" text-anchor="middle">À tester et documenter</text>
  <text class="rm-text" x="480" y="334" text-anchor="middle">La redondance n'est effective que si les scénarios de panne sont réellement couverts.</text>
</svg>

## 9.4 Tester la redondance

Un plan de continuité doit préciser :

- le composant dont la panne est simulée ;
- les services qui doivent rester accessibles ;
- les résultats attendus ;
- les délais tolérés ;
- les moyens de surveillance ;
- les conditions de retour à l'état normal ;
- les risques et précautions du test.

Les tests doivent être réalisés dans un cadre autorisé, de préférence sur un environnement de laboratoire avant de toucher une infrastructure critique.

---

# 10. Diagnostic matériel structuré

## 10.1 Distinguer quatre classes de problèmes

Une défaillance peut être physique, électrique, logicielle ou liée à la configuration.

**Physique :** câble endommagé, mauvais connecteur, module optique incompatible.

**Électrique :** alimentation insuffisante, budget PoE dépassé, circuit instable.

**Logiciel :** pilote, micrologiciel ou version du système défectueux.

**Configuration :** port désactivé, vitesse imposée incorrectement, VLAN non autorisé ou interface de routage mal configurée.

La distinction aide à éviter de remplacer le matériel lorsqu'une modification de configuration serait nécessaire, ou inversement.

## 10.2 Arbre de diagnostic

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="375" viewBox="0 0 960 375" role="img" aria-labelledby="diag-mid-title diag-mid-desc">
  <title id="diag-mid-title">Arbre de diagnostic d'une liaison réseau</title>
  <desc id="diag-mid-desc">Le diagnostic commence par le symptôme. Il vérifie l'alimentation, le support physique, l'établissement du lien, puis la configuration et les performances. Chaque échec dirige l'investigation vers une classe de cause distincte.</desc>
  <defs>
    <marker id="diag-mid-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .dm-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .dm-check{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .dm-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .dm-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .dm-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#diag-mid-arrow);animation:dm-dash 1.8s linear infinite}
      @keyframes dm-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="373" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LOCALISER AVANT DE REMPLACER</text>
  <rect class="dm-box" x="25" y="75" width="180" height="68" rx="10"/>
  <text class="dm-title" x="115" y="103" text-anchor="middle">1. Symptôme</text>
  <text class="dm-text" x="115" y="124" text-anchor="middle">Définir le périmètre</text>
  <rect class="dm-check" x="255" y="75" width="180" height="68" rx="10"/>
  <text class="dm-title" x="345" y="103" text-anchor="middle">2. Alimentation</text>
  <text class="dm-text" x="345" y="124" text-anchor="middle">État et puissance</text>
  <rect class="dm-check" x="485" y="75" width="180" height="68" rx="10"/>
  <text class="dm-title" x="575" y="103" text-anchor="middle">3. Support physique</text>
  <text class="dm-text" x="575" y="124" text-anchor="middle">Câble ou optique</text>
  <rect class="dm-check" x="715" y="75" width="220" height="68" rx="10"/>
  <text class="dm-title" x="825" y="103" text-anchor="middle">4. Lien et configuration</text>
  <text class="dm-text" x="825" y="124" text-anchor="middle">Port, débit, VLAN</text>
  <path class="dm-flow" d="M205 109 H247"/>
  <path class="dm-flow" d="M435 109 H477"/>
  <path class="dm-flow" d="M665 109 H707"/>
  <rect class="dm-box" x="165" y="220" width="630" height="75" rx="10"/>
  <text class="dm-title" x="480" y="249" text-anchor="middle">5. Mesures et données complémentaires</text>
  <text class="dm-text" x="480" y="272" text-anchor="middle">Compteurs, erreurs, journaux, versions, tests et état distant</text>
  <path class="dm-flow" d="M825 143 V190 H795 V212"/>
  <text class="dm-text" x="480" y="329" text-anchor="middle">Changer un seul paramètre à la fois lorsque cela est possible.</text>
  <text class="dm-text" x="480" y="349" text-anchor="middle">Ne remplacez un composant que lorsque les observations orientent vers lui.</text>
</svg>

## 10.3 Les compteurs d'erreurs

Les compteurs peuvent signaler différents problèmes, selon l'équipement et l'interface :

- erreurs de réception ;
- erreurs de trames ;
- pertes ou abandons ;
- erreurs de contrôle ;
- changements fréquents d'état du lien ;
- erreurs optiques ou niveaux de puissance hors plage, si le matériel les expose.

Un compteur isolé ne suffit pas toujours. Examinez sa variation dans le temps, l'activité du lien et les conditions de charge.

## 10.4 Les tests de substitution

Un câble de test connu comme fonctionnel peut aider à isoler un défaut physique. Un module optique compatible et documenté peut être utilisé dans les conditions autorisées par le constructeur.

Toute substitution doit être tracée. Ne remplacez pas plusieurs composants en même temps si l'objectif est d'identifier la cause : vous perdriez une partie des informations diagnostiques.

## 10.5 Quand arrêter les tests

Arrêtez l'investigation et appliquez une procédure adaptée si :

- l'équipement présente un dommage électrique ou mécanique ;
- un composant est anormalement chaud ;
- l'accès à une fibre ou une alimentation présente un risque ;
- un test pourrait interrompre un service critique ;
- le périmètre ou l'autorisation n'est pas clairement défini.

La sécurité et la continuité de service priment sur un diagnostic improvisé.

---

# 11. Atelier de dimensionnement

## Scénario

Une petite entreprise prévoit d'équiper un étage comprenant :

- 28 ordinateurs ;
- 10 téléphones IP ;
- 4 points d'accès Wi-Fi ;
- 2 imprimantes ;
- 2 liaisons montantes vers la distribution.

Les besoins exacts en débit et en puissance doivent être confirmés auprès des fabricants. Les nombres ci-dessous décrivent le scénario d'exercice, pas une prescription d'achat définitive.

## Étape A — Calculer le nombre de ports

Le nombre de terminaux filaires considérés est :

\[
28 + 10 + 4 + 2 = 44
\]

Cela représente 44 connexions terminales dans ce scénario. Si deux autres ports sont nécessaires pour des fonctions supplémentaires ou des réserves, ils doivent être ajoutés au dimensionnement.

Si les 44 terminaux sont tous raccordés au même switch, il faut également tenir compte des ports nécessaires aux uplinks et de la manière dont le modèle compte ses interfaces.

## Étape B — Vérifier le PoE

Les téléphones et les points d'accès peuvent utiliser le PoE.

Relevez leur puissance maximale prévue, leur norme PoE et les fonctions activées. Calculez la puissance nécessaire en considérant les usages simultanés et la politique de réserve.

Vérifiez ensuite que le switch prend en charge les exigences par port et le budget total.

## Étape C — Dimensionner les uplinks

Évaluez le trafic agrégé et les chemins disponibles. Déterminez les débits nécessaires pour les communications vers les serveurs, les services Internet et les autres segments.

Les deux uplinks prévus doivent être étudiés selon leur rôle : agrégation active, chemins redondants ou combinaison des deux lorsque l'architecture le permet.

## Étape D — Vérifier l'installation

Prévoyez la baie, les panneaux de brassage, le câblage, l'alimentation, le refroidissement et l'identification des ports.

Si la fibre est utilisée pour les uplinks, choisissez les modules compatibles avec les deux extrémités et avec la distance du lien.

## Étape E — Documenter le choix

La fiche de décision doit indiquer :

- les besoins ;
- les hypothèses de trafic ;
- le nombre de ports ;
- le budget PoE calculé ;
- le type de câblage ;
- les uplinks ;
- les fonctions logicielles nécessaires ;
- les contraintes environnementales ;
- les marges prévues ;
- les limites connues.

Le dimensionnement est terminé lorsque les choix sont justifiés par des données et vérifiés dans les fiches techniques.

---

# 12. Étude de panne

## Situation

Un point d'accès Wi-Fi se met à redémarrer lorsque plusieurs clients se connectent. Le lien Ethernet semble correct au repos.

## Hypothèses possibles

- budget PoE insuffisant ;
- alimentation ou port PoE défaillant ;
- câble endommagé ;
- firmware ou configuration du point d'accès ;
- défaut thermique ;
- problème de compatibilité ou de fonctionnement de l'appareil.

## Démarche

1. Relever les messages et événements du point d'accès.
2. Vérifier les besoins PoE du modèle et les fonctions activées.
3. Examiner le budget disponible du switch et la puissance effectivement allouée.
4. Vérifier les compteurs et l'état du port.
5. Examiner le câble et le chemin physique.
6. Contrôler la température et l'alimentation.
7. Si l'autorisation et les procédures le permettent, tester avec un port, un câble ou une source compatible connue comme fonctionnelle.
8. Mettre en relation les résultats et isoler la cause.
9. Corriger le problème puis vérifier le fonctionnement sous une charge représentative.

Ne concluez pas que le switch est défectueux uniquement parce que le point d'accès redémarre. Le symptôme doit être rattaché à des preuves.

---

# 13. Évaluation corrigée

## Questions

1. Pourquoi le nombre de ports ne suffit-il pas pour choisir un switch ?
2. Quelle différence existe entre capacité de commutation et débit utile d'un flux ?
3. Pourquoi vérifier les deux extrémités d'une liaison optique ?
4. Que doit contenir un calcul de budget optique ?
5. Pourquoi une agrégation de liens n'augmente-t-elle pas toujours le débit d'un seul flux ?
6. Quelle différence existe entre puissance par port et budget PoE total ?
7. Pourquoi deux alimentations ne garantissent-elles pas toujours une disponibilité électrique complète ?
8. Quel est l'intérêt d'une baie et d'un panneau de brassage ?
9. Pourquoi faut-il considérer la perte d'un uplink pendant le dimensionnement ?
10. Pourquoi un test de continuité ne certifie-t-il pas un câblage complet ?
11. Qu'est-ce qu'un point unique de défaillance ?
12. Pourquoi mesurer les compteurs avant et après une modification ?

## Corrigé

**1. Nombre de ports**

Il faut également examiner les débits, les uplinks, les fonctions, le PoE, les tables, l'environnement et la disponibilité.

**2. Capacité et débit utile**

La capacité de commutation est une caractéristique globale de la plateforme selon sa définition. Le débit utile d'un flux dépend aussi des interfaces, des contraintes de traitement et des conditions de trafic.

**3. Extrémités optiques**

Les deux modules, les longueurs d'onde, les supports et les interfaces doivent être compatibles.

**4. Budget optique**

Il tient compte des pertes de fibre, des connecteurs, des épissures, des autres composants passifs et d'une marge de conception par rapport aux limites des transceivers.

**5. Agrégation**

La répartition des flux dépend du mécanisme utilisé ; un flux individuel peut rester sur un seul lien physique.

**6. Puissance PoE**

La puissance par port est une limite locale de l'interface. Le budget total correspond à la puissance globale mise à disposition par le switch et son alimentation.

**7. Alimentations redondantes**

Elles peuvent partager une même source ou ne pas fournir toute la charge en mode dégradé.

**8. Baie et panneau de brassage**

Ils organisent les connexions et facilitent la maintenance, l'identification et le remplacement des cordons.

**9. Perte d'un uplink**

Une architecture peut devoir transporter le trafic par un chemin restant après une panne. La capacité en mode dégradé doit donc être prise en compte.

**10. Test de continuité**

Il détecte certaines erreurs électriques, mais ne prouve pas nécessairement la performance du câblage au débit attendu.

**11. Point unique de défaillance**

C'est un composant dont la panne peut interrompre une fonction essentielle en l'absence de secours suffisant.

**12. Compteurs avant et après**

La comparaison permet de voir si les erreurs ou abandons évoluent avec la modification ou avec les conditions de charge.

---

# 14. Préparation du niveau expert

Le niveau expert approfondira :

- l'analyse des performances des plateformes ;
- les architectures modulaires et distribuées ;
- le dimensionnement du trafic et des buffers ;
- les budgets d'alimentation et les scénarios de panne ;
- l'ingénierie optique ;
- la conception de chemins physiquement diversifiés ;
- l'analyse de fiabilité des composants ;
- les procédures de remplacement et de migration ;
- la surveillance du matériel et la collecte de télémétrie ;
- le diagnostic des pannes intermittentes ;
- les critères de sélection et de cycle de vie du matériel.

**Le niveau intermédiaire apprend à sélectionner, dimensionner et diagnostiquer les composants. Le niveau expert apprend à concevoir une infrastructure matérielle cohérente, mesurable et capable de fonctionner en mode dégradé.**

---

## Références utiles

- IEEE 802.3 — Ethernet : https://standards.ieee.org/ieee/7003/10422/
- IEEE 802.1Q — VLAN et pontage : https://standards.ieee.org/ieee/8802-1Q_2024_Amd.35_2024/11823/802.1Q/10323/
- Documentation PoE Cisco : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/infra/poe/poe-configuration-guide/g-poe/c-poe.html
- Guide des composants matériels de routeur Juniper : https://www.juniper.net/documentation/us/en/software/junos/junos-overview/topics/concept/junos-software-routing-platforms-hardware-components.html
- Guides matériels Juniper : https://www.juniper.net/documentation/
- Guide matériel des switches : https://www.juniper.net/documentation/us/en/hardware/ex9208/index.html

**Fichier :** `materiel-reseau-intermediaire.md`  
**Niveau :** Intermédiaire  
**Fin du cours**
