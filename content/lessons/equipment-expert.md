# Équipements réseau L1/L2 — Niveau expert

> **Fichier :** `equipment-expert.md`  
> **Niveau :** Expert  
> **Prérequis :** maîtriser Ethernet, VLAN, STP/RSTP, LACP, PoE et le diagnostic des compteurs.  
> **Objectif :** concevoir et exploiter une infrastructure L1/L2 robuste, contrôlée et observable ; maîtriser les limites d’une architecture étendue, les mécanismes de sécurité d’accès, le budget optique et le plan de validation.

## 1. Principes de conception

Une architecture L1/L2 de production doit satisfaire plusieurs objectifs simultanés : capacité, résilience, sécurité, capacité d’évolution, facilité de diagnostic, coût total et conformité physique. Il ne suffit pas de choisir « un switch assez rapide » : il faut dimensionner les ports, le débit de commutation, les buffers, l’alimentation, le refroidissement, la redondance, les uplinks, l’optique, l’inventaire, le support logiciel et les pièces de remplacement.

### 1.1. Définir les frontières L2

Un grand domaine L2 simplifie parfois certains besoins de continuité, mais il augmente le périmètre des broadcasts, l’impact d’une boucle, la propagation de certaines pannes et la portée d’une erreur de configuration. Une architecture moderne place souvent des frontières L3 à des endroits planifiés, tout en gardant les VLAN nécessaires à l’accès local.

Il faut choisir le modèle selon les applications, la taille, les besoins de mobilité, la convergence, la sécurité et les capacités des équipements plutôt que selon une règle unique.

## 2. Architecture redondante de campus

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430" role="img" aria-labelledby="exp1-title exp1-desc" style="width:100%;max-width:1000px;height:auto;display:block">
<title id="exp1-title">Architecture campus redondante</title><desc id="exp1-desc">Des switches d’accès sont redondés vers une paire de distribution ou de cœur. Les liens agrégés et les fonctions de couche 3 sont déployés selon les capacités du constructeur et l’architecture retenue.</desc>
<defs><marker id="exp1-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#60a5fa"/></marker><style>.e1bg{fill:#0a1220}.e1c{fill:#151f32;stroke:#344660;stroke-width:1.5}.e1h{font:700 17px sans-serif;fill:#f1f5f9}.e1t{font:13px sans-serif;fill:#cbd5e1}.e1s{font:12px sans-serif;fill:#9fb0c8}.e1l{fill:none;stroke:#60a5fa;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#exp1-arr);animation:e1flow 1.7s linear infinite}@keyframes e1flow{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.e1l{animation:none}}</style></defs>
<rect class="e1bg" width="1000" height="430" rx="18"/><text class="e1h" x="28" y="34">Campus professionnel : accès, distribution/cœur et frontière L3</text>
<rect class="e1c" x="190" y="63" width="270" height="66" rx="10"/><text class="e1h" x="325" y="91" text-anchor="middle">Distribution / cœur A</text><text class="e1t" x="325" y="113" text-anchor="middle">SVI / routage selon le design</text>
<rect class="e1c" x="540" y="63" width="270" height="66" rx="10"/><text class="e1h" x="675" y="91" text-anchor="middle">Distribution / cœur B</text><text class="e1t" x="675" y="113" text-anchor="middle">Chemin redondant</text>
<rect class="e1c" x="50" y="240" width="270" height="70" rx="10"/><text class="e1h" x="185" y="268" text-anchor="middle">Switch d’accès 1</text><text class="e1t" x="185" y="291" text-anchor="middle">PC · téléphone · AP</text>
<rect class="e1c" x="370" y="240" width="270" height="70" rx="10"/><text class="e1h" x="505" y="268" text-anchor="middle">Switch d’accès 2</text><text class="e1t" x="505" y="291" text-anchor="middle">Postes / imprimantes / IoT</text>
<rect class="e1c" x="690" y="240" width="270" height="70" rx="10"/><text class="e1h" x="825" y="268" text-anchor="middle">Zone serveurs</text><text class="e1t" x="825" y="291" text-anchor="middle">Segmentation contrôlée</text>
<path class="e1l" d="M185 240 L275 129"/><path class="e1l" d="M250 240 L600 129"/><path class="e1l" d="M505 240 L380 129"/><path class="e1l" d="M555 240 L675 129"/><path class="e1l" d="M825 240 L700 129"/>
<rect x="50" y="345" width="910" height="55" rx="10" fill="#102b36" stroke="#267e86"/><text x="70" y="368" style="font:700 15px sans-serif;fill:#99f6e4">Principes</text><text class="e1t" x="170" y="368">Réduire les domaines L2, planifier STP, agréger seulement les liens compatibles,</text><text class="e1t" x="170" y="388">et définir explicitement la passerelle et le comportement de bascule.</text></svg>

### 2.1. Accès, distribution et cœur

- **Accès :** ports de terminaux, téléphones, AP, IoT, contrôle d’identité et alimentation PoE.
- **Distribution/cœur :** agrégation de l’accès, politiques L3, segmentation, routage, QoS et redondance selon la conception.
- **Zone serveurs :** chemins contrôlés vers les services et les environnements d’infrastructure.

Dans un campus plus petit, distribution et cœur peuvent être réunis. Le dessin est conceptuel : ne pas interpréter chaque double lien comme un EtherChannel possible entre deux boîtiers sans vérifier le support de stack, MLAG ou technologie équivalente. Un LAG vers une paire de switches distincts n’est supporté que si la conception multi-châssis correspondante existe et est documentée.

### 2.2. Plan de capacité

Recenser au minimum :

- le nombre de ports actuels et à trois/cinq ans ;
- le nombre de ports PoE et la demande maximale simultanée ;
- les uplinks et leurs taux d’oversubscription ;
- la capacité de forwarding en paquets par seconde et le débit de commutation annoncés ;
- la taille et le comportement des buffers face aux microbursts ;
- les limites de table MAC, VLAN, ACL, routes et groupes multicast ;
- le nombre de transceivers, la consommation électrique et le refroidissement.

Un taux d’oversubscription n’a de sens qu’avec un scénario de trafic : un ratio de ports théorique ne donne pas à lui seul la performance réelle des applications.

## 3. Résilience L2 : STP, LACP et conception des chemins

STP/RSTP et LACP répondent à des problèmes différents : STP évite les boucles L2 en organisant la topologie active ; l’agrégation présente des liens compatibles comme un lien logique et distribue les flux. Ni l’un ni l’autre ne remplace la surveillance, les tests de panne et une bonne conception physique.

Bonnes pratiques d’expert :

1. documenter le root bridge attendu par domaine de commutation ;
2. régler les priorités afin que le chemin racine soit déterministe ;
3. distinguer les ports edge des liens vers d’autres ponts ;
4. employer BPDU Guard, Root Guard et les autres protections selon le rôle et la politique ;
5. auditer tout changement physique ou agrégation avant de le déployer ;
6. tester la perte d’un membre, d’un uplink, d’une alimentation et d’un switch ;
7. mesurer la convergence effective, pas uniquement se fier à une valeur théorique.

Une architecture avec des liens redondants mais sans mécanisme cohérent de prévention de boucle peut être moins fiable qu’une architecture simple. Documenter le rôle de chaque lien et la façon dont il doit se comporter en cas de panne.

## 4. Sécurité de l’accès filaire

La sécurité ne se limite pas au contrôle d’un VLAN. Elle combine identité, segmentation, protection des plans de contrôle, journalisation et réduction de l’exposition des ports inutilisés.

### 4.1. 802.1X et RADIUS

IEEE 802.1X fournit le contrôle d’accès basé sur le port. Le terminal joue généralement le rôle de supplicant, le switch ou AP celui d’authenticator, et le serveur RADIUS peut prendre part à l’authentification et à la décision d’autorisation selon l’architecture.

Des politiques peuvent attribuer un VLAN ou un rôle différent après authentification. Les modes d’échec du serveur d’identité, les terminaux non compatibles et la récupération d’urgence doivent être planifiés et testés.

MAB (*MAC Authentication Bypass*) peut aider à intégrer certains équipements sans supplicant, mais une adresse MAC est usurpable : ce mécanisme est un compromis de compatibilité, pas une authentification forte équivalente à 802.1X.

### 4.2. DHCP snooping, Dynamic ARP Inspection et IP Source Guard

Lorsque la plateforme les prend en charge, ces fonctions aident à limiter certaines usurpations sur des réseaux d’accès :

- **DHCP snooping :** différencie les ports de confiance et non fiables pour certains messages DHCP et peut bâtir une base de bindings.
- **Dynamic ARP Inspection (DAI) :** valide certains messages ARP par rapport à la politique et à la base connue.
- **IP Source Guard :** peut filtrer des paquets selon les informations d’adresse et de port apprises ou configurées.

Ces fonctions ne peuvent pas être activées sans conception. Une mauvaise attribution des ports trusted/untrusted, des serveurs DHCP légitimes, des adresses statiques et des exceptions peut interrompre le service. Prévoir un audit avant activation et une procédure de restauration.

### 4.3. Hygiène des ports et gestion

- désactiver ou isoler les ports non utilisés selon la politique ;
- documenter les ports réservés aux uplinks et empêcher les trunks inattendus ;
- appliquer des contrôles de tempête avec des seuils mesurés et testés ;
- restreindre les accès de gestion et utiliser des protocoles d’administration sécurisés ;
- collecter les logs, les événements de lien, les changements de MAC et l’état STP ;
- ne pas considérer LLDP comme un mécanisme d’authentification ; évaluer l’information révélée selon le contexte.

## 5. Schéma expert — contrôles sur un port d’accès

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400" viewBox="0 0 1000 400" role="img" aria-labelledby="exp2-title exp2-desc" style="width:100%;max-width:1000px;height:auto;display:block">
<title id="exp2-title">Contrôles de sécurité sur un port d’accès</title><desc id="exp2-desc">Le trafic d’un appareil traverse des couches de contrôle : lien physique, authentification 802.1X ou politique de repli, affectation VLAN, contrôles DHCP snooping et inspection ARP, puis commutation.</desc>
<defs><marker id="exp2-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#4de0c1"/></marker><style>.e2bg{fill:#0a1220}.e2c{fill:#151f32;stroke:#344660;stroke-width:1.4}.e2h{font:700 16px sans-serif;fill:#f1f5f9}.e2t{font:13px sans-serif;fill:#cbd5e1}.e2s{font:12px sans-serif;fill:#9fb0c8}.e2l{fill:none;stroke:#4de0c1;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#exp2-arr);animation:e2flow 1.6s linear infinite}@keyframes e2flow{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.e2l{animation:none}}</style></defs>
<rect class="e2bg" width="1000" height="400" rx="18"/><text class="e2h" x="28" y="34">Défense en profondeur au niveau accès</text>
<rect class="e2c" x="25" y="94" width="150" height="90" rx="10"/><text class="e2h" x="100" y="124" text-anchor="middle">Terminal</text><text class="e2t" x="100" y="148" text-anchor="middle">PC / IoT</text><text class="e2s" x="100" y="168" text-anchor="middle">Port physique</text>
<rect class="e2c" x="213" y="94" width="172" height="90" rx="10"/><text class="e2h" x="299" y="121" text-anchor="middle">802.1X</text><text class="e2t" x="299" y="145" text-anchor="middle">Identité / autorisation</text><text class="e2s" x="299" y="166" text-anchor="middle">RADIUS si déployé</text>
<rect class="e2c" x="423" y="94" width="172" height="90" rx="10"/><text class="e2h" x="509" y="121" text-anchor="middle">VLAN / ACL</text><text class="e2t" x="509" y="145" text-anchor="middle">Segment autorisé</text><text class="e2s" x="509" y="166" text-anchor="middle">Politique explicite</text>
<rect class="e2c" x="633" y="94" width="172" height="90" rx="10"/><text class="e2h" x="719" y="121" text-anchor="middle">Snooping / DAI</text><text class="e2t" x="719" y="145" text-anchor="middle">Contrôle DHCP / ARP</text><text class="e2s" x="719" y="166" text-anchor="middle">Selon support</text>
<rect class="e2c" x="843" y="94" width="132" height="90" rx="10"/><text class="e2h" x="909" y="121" text-anchor="middle">Réseau</text><text class="e2t" x="909" y="145" text-anchor="middle">Trafic admis</text><text class="e2s" x="909" y="166" text-anchor="middle">Surveillance</text>
<path class="e2l" d="M175 139 H213"/><path class="e2l" d="M385 139 H423"/><path class="e2l" d="M595 139 H633"/><path class="e2l" d="M805 139 H843"/>
<rect x="25" y="235" width="950" height="118" rx="12" fill="#302127" stroke="#9f4551"/><text x="48" y="263" style="font:700 16px sans-serif;fill:#fca5a5">Points de conception</text><text class="e2t" x="48" y="289">• MAB n’équivaut pas à une authentification forte : c’est souvent une exception pour équipements sans supplicant.</text><text class="e2t" x="48" y="313">• DHCP snooping et DAI exigent une configuration correcte des ports de confiance et de la base de bindings.</text><text class="e2t" x="48" y="337">• Tester les modes d’échec avant déploiement ; documenter les exceptions et prévoir une voie de récupération.</text><text class="e2s" x="25" y="382">Le schéma est conceptuel : ordre et disponibilité des contrôles varient selon l’équipement et l’architecture.</text></svg>

L’ordre du dessin sert à expliquer les concepts, pas à imposer une chaîne interne identique à tous les fabricants. Les contrôles disponibles, leur ordre d’évaluation et le point de prise de décision dépendent du produit et du logiciel.

## 6. Optique : compatibilité et budget optique

Un lien optique valide doit faire correspondre le module, la fibre, la longueur d’onde, le connecteur, le mode de transmission, la distance et la puissance reçue. Deux modules portant le même format SFP ne sont pas automatiquement compatibles.

### 6.1. Vérifications de compatibilité

- débit et PHY Ethernet (par exemple famille SR ou LR selon usage) ;
- fibre multimode ou monomode et type de fibre exact ;
- longueur d’onde et type de connecteur ;
- distance nominale et dispersion/modalité applicables ;
- puissance Tx, sensibilité et surcharge Rx ;
- DOM/DDM si disponible : température, tension, courant, puissance optique Tx/Rx ;
- support constructeur de l’optique et éventuelles restrictions de codage.

Ne pas mélanger des modules SR multimode et LR monomode au hasard, ni supposer qu’une liaison est correcte parce que le transceiver s’insère physiquement dans le port.

### 6.2. Budget optique

<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400" viewBox="0 0 1000 400" role="img" aria-labelledby="exp3-title exp3-desc" style="width:100%;max-width:1000px;height:auto;display:block">
<title id="exp3-title">Budget optique de bout en bout</title><desc id="exp3-desc">Un module optique émetteur envoie le signal dans une fibre à travers connecteurs et épissures. Le récepteur doit recevoir un niveau optique dans sa plage admissible, avec une marge de conception.</desc>
<defs><marker id="exp3-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#fbbf24"/></marker><style>.e3bg{fill:#0a1220}.e3c{fill:#151f32;stroke:#344660;stroke-width:1.4}.e3h{font:700 17px sans-serif;fill:#f1f5f9}.e3t{font:13px sans-serif;fill:#cbd5e1}.e3s{font:12px sans-serif;fill:#9fb0c8}.e3f{fill:none;stroke:#fbbf24;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#exp3-arr);animation:e3flow 1.6s linear infinite}@keyframes e3flow{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.e3f{animation:none}}</style></defs>
<rect class="e3bg" width="1000" height="400" rx="18"/><text class="e3h" x="28" y="34">Lien fibre : vérifier le budget optique et les limites du module</text>
<rect class="e3c" x="30" y="97" width="190" height="93" rx="10"/><text class="e3h" x="125" y="126" text-anchor="middle">Tx optique</text><text class="e3t" x="125" y="150" text-anchor="middle">Puissance émise</text><text class="e3s" x="125" y="171" text-anchor="middle">dBm</text>
<rect class="e3c" x="300" y="97" width="390" height="93" rx="10"/><text class="e3h" x="495" y="126" text-anchor="middle">Fibre + connecteurs + épissures</text><text class="e3t" x="495" y="150" text-anchor="middle">Perte fibre / pertes passives / événements</text><text class="e3s" x="495" y="171" text-anchor="middle">Longueur d’onde et type de fibre adaptés</text>
<rect class="e3c" x="770" y="97" width="200" height="93" rx="10"/><text class="e3h" x="870" y="126" text-anchor="middle">Rx optique</text><text class="e3t" x="870" y="150" text-anchor="middle">Sensibilité / surcharge</text><text class="e3s" x="870" y="171" text-anchor="middle">dBm</text>
<path class="e3f" d="M220 143 H300"/><path class="e3f" d="M690 143 H770"/>
<rect x="30" y="230" width="940" height="105" rx="12" fill="#102b36" stroke="#267e86"/><text x="52" y="258" style="font:700 16px sans-serif;fill:#99f6e4">Modèle de calcul simplifié</text><text class="e3t" x="52" y="284">Puissance reçue ≈ puissance Tx − pertes totales, en dB.</text><text class="e3t" x="52" y="307">Vérifier le niveau Rx prévu dans la plage du module, garder une marge et mesurer le lien installé.</text><text class="e3s" x="30" y="365">Un calcul théorique ne remplace ni la documentation du transceiver ni les mesures optiques/certifications.</text><text class="e3s" x="30" y="385">Ne jamais regarder directement dans une fibre ou un port optique ; inspecter et nettoyer avec des outils adaptés.</text></svg>

La relation de base est :

```text
Puissance reçue estimée (dBm)
  = puissance émise (dBm) - pertes totales du lien (dB)
```

Les pertes totales incluent la fibre, les connecteurs, les épissures et autres éléments passifs pertinents. Le calcul doit être comparé à la plage de réception du module et conserver la marge requise selon la conception, le vieillissement, les réparations et les contraintes du chemin.

Attention aux unités : dBm représente un niveau de puissance référencé à 1 mW ; dB exprime un rapport ou une perte. Un budget théorique ne remplace ni l’inspection des connecteurs ni une mesure de la liaison installée. Pour le diagnostic, vérifier les valeurs Tx/Rx, l’état des connecteurs, la polarité, l’atténuation et la présence éventuelle de courbures excessives.

## 7. PoE à l’échelle d’un site

Établir une matrice qui associe chaque terminal à son besoin énergétique, au port, au standard, au niveau de priorité et à la marge. Examiner également la charge globale du switch, l’alimentation redondante si elle existe, la température et le fonctionnement au redémarrage.

Le budget théorique d’un châssis n’est pas nécessairement entièrement disponible à tous les ports en simultané. La puissance arrivant au terminal peut être inférieure à la puissance fournie par le PSE en raison des limites normatives et des pertes du canal. Pour des AP multi-radio, des caméras PTZ et d’autres terminaux exigeants, confirmer les modes de fonctionnement disponibles lorsque le budget est limité.

Ne pas utiliser une valeur unique « watts PoE » sans préciser le type, la classe et le point de mesure. Les standards, les fiches techniques et la configuration du PSE sont les sources de dimensionnement.

## 8. Multicast, storm control, QoS et MTU

### Multicast et IGMP snooping

Lorsque des applications emploient le multicast IPv4, IGMP snooping peut limiter la diffusion aux ports intéressés en observant les messages IGMP. Les mécanismes sont dépendants de la plateforme et doivent être vérifiés avec un querier approprié dans le domaine concerné. Une mauvaise configuration peut rendre certains flux invisibles aux récepteurs.

### Storm control

Le storm control limite certains types de trafic à haut volume, par exemple broadcast, multicast ou unicast inconnu. Des seuils trop stricts peuvent bloquer du trafic légitime ou aggraver une panne. Baseline, seuil, action et alerte doivent être documentés.

### QoS L2

802.1Q peut transporter un champ de priorité PCP. La présence d’une valeur PCP n’impose pas à elle seule une politique de bout en bout : il faut définir la confiance accordée aux marques à l’entrée, les mappings, les files de sortie, les politiques de congestion et l’interopérabilité des équipements.

### MTU et jumbo frames

Les jumbo frames ne sont pas automatiquement une amélioration universelle. Tous les équipements et chemins concernés doivent prendre en charge les tailles choisies. Une incohérence peut entraîner des pertes sélectives, surtout pour les grands paquets. Documenter la MTU bout à bout, les exceptions et le protocole applicatif concerné.

## 9. Observabilité et métriques utiles

Surveiller les indicateurs pertinents :

- état des ports, erreurs CRC/FCS et symboles ;
- changements répétés de lien et négociations de vitesse ;
- MAC moves, changements STP et notifications de topologie ;
- membres LACP hors service et répartition du trafic ;
- utilisation uplink, drops, files, microbursts si mesurables ;
- puissance PoE consommée et événements de coupure de PD ;
- puissance optique Tx/Rx et température du transceiver ;
- taux de broadcast/multicast et alertes storm control ;
- événements 802.1X/RADIUS et état des terminaux autorisés.

Un compteur isolé ne suffit pas : comparer les tendances, les interfaces voisines, les horodatages et les changements récents. Une hausse de CRC peut indiquer un problème physique ou de compatibilité, tandis qu’une augmentation de drops de sortie peut correspondre à une congestion.

## 10. Runbook de diagnostic expert

### Incident A — Tempête de broadcast

1. Confirmer les symptômes via compteurs de diffusion, CPU, MAC moves et logs.
2. Identifier le VLAN et la fenêtre temporelle.
3. Rechercher un changement récent de câblage, un STP instable ou un équipement bridge non autorisé.
4. Isoler un segment selon la procédure d’exploitation ; éviter des débranchements aveugles sur un cœur en production.
5. Corriger la boucle, valider l’état STP et surveiller les compteurs après rétablissement.

### Incident B — Lien optique instable

1. Collecter les alarmes et mesures DOM/DDM aux deux extrémités.
2. Confirmer le type exact de fibre, le module, les longueurs d’onde et la distance.
3. Vérifier les connecteurs et la polarité avec procédures d’inspection/nettoyage appropriées.
4. Comparer la puissance reçue au budget et aux seuils constructeur.
5. Mesurer la liaison après intervention et documenter le résultat.

### Incident C — Terminal non autorisé ou VLAN incorrect

1. Vérifier l’identité et les journaux 802.1X/RADIUS.
2. Vérifier la politique appliquée et le VLAN/role résultant.
3. Inspecter les ports trusted, les bindings DHCP, les exceptions statiques et les logs DAI si utilisés.
4. Confirmer qu’aucun trunk ou port libre ne peut contourner l’accès prévu.
5. Tester de nouveau avec un terminal autorisé et un scénario non autorisé.

## 11. Étude de cas finale

Un bâtiment possède 250 utilisateurs, 60 téléphones IP, 30 points d’accès Wi-Fi, des caméras PoE, une paire de switches de distribution et des liens fibre entre armoires.

Produire un dossier d’exploitation comprenant :

1. schéma physique et logique ;
2. matrice ports/VLAN/rôle/PoE ;
3. budget global PoE avec marge d’évolution ;
4. capacité des uplinks et scénario de trafic ;
5. root bridge prévu et politique STP ;
6. plan LACP compatible avec les équipements réellement installés ;
7. politique 802.1X et exceptions documentées ;
8. correspondance modules/fibres et calcul de budget optique ;
9. supervision des erreurs, puissances, changements de MAC et authentifications ;
10. procédures de test, bascule, retour arrière et preuve de réception.

La qualité du résultat se juge sur la cohérence entre les schémas, les configurations, les contraintes constructeur, la sécurité et les procédures d’exploitation — pas seulement sur la présence de fonctionnalités avancées.

## 12. Liste de contrôle de réception

- [ ] Les nomenclatures, ports, câbles et optiques correspondent au dossier de conception.
- [ ] Les tests de câble/fibre sont archivés et respectent les exigences du projet.
- [ ] VLAN, trunks, STP et LAG sont vérifiés de bout en bout.
- [ ] Les contrôles de sécurité sont testés avec scénarios autorisés et non autorisés.
- [ ] Le budget PoE tient dans le pire cas documenté.
- [ ] Les alarmes et données de supervision sont exploitables par le support.
- [ ] Une coupure de lien et une panne d’équipement sont testées sans risque non maîtrisé.
- [ ] Le plan de secours et les contacts d’escalade sont disponibles.
- [ ] Les changements et valeurs mesurées sont consignés dans un registre.

## Références techniques

- [IEEE 802.3 — Ethernet Working Group](https://www.ieee802.org/3/) : famille de normes Ethernet, couches physiques et MAC.
- [IEEE 802.1Q-2022 — Bridges and Bridged Networks](https://standards.ieee.org/ieee/802.1q/10323/) : pontage et VLAN ; consulter les amendements applicables.
- [IEEE 802.1AX-2020 — Link Aggregation](https://standards.ieee.org/ieee/149/6768/) : agrégation de liens.
- [IEEE 802.1AB-2026 — Connectivity Discovery](https://standards.ieee.org/ieee/802.1AB/11787/) : découverte de voisins LLDP.
- [IEEE 802.11-2024 — Wireless LAN MAC and PHY](https://standards.ieee.org/ieee/802.11/10548/) : réseau local sans fil.
- [IEEE 802.1X-2020 — Port-Based Network Access Control](https://standards.ieee.org/ieee/C2/10774/802.1X/7345/) : contrôle d’accès par port.
- [IEEE/ISO/IEC 8802-3:2026 — Ethernet](https://www.iso.org/standard/89414.html) : édition ISO/IEC/IEEE publiée en août 2026.
- [IEEE 802.3bt — alimentation PoE sur quatre paires](https://standards.ieee.org/ieee/8802-3_2021_Amd2/10811/).

> Les pages de standards servent à vérifier l’édition et le statut. Pour une installation contractuelle, utiliser le texte normatif applicable, les prescriptions du pays, les règles du bâtiment, ainsi que les documents du constructeur ; ne pas déduire une conformité complète à partir de ce cours seul.
