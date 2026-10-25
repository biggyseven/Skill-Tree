# Laboratoire de dépannage du routage — `lab_tshoot_route.md`

> **Parcours :** débutant → intermédiaire → expert  
> **Environnements :** Cisco IOS/IOS XE en simulateur ou laboratoire, Linux avec `iproute2`, FRRouting (FRR) et Wireshark/tcpdump.  
> **Fil conducteur :** NovaTech, avec deux LAN reliés par des routeurs intermédiaires.  
> **Objectif :** diagnostiquer une panne de routage en séparant l'adressage, la table de routage, le prochain saut, le protocole dynamique, le plan de données, les politiques de filtrage et le chemin retour.


## 1. Objectifs pédagogiques

À la fin de ce cahier, tu dois pouvoir :

1. distinguer une panne d'adressage local d'une panne de routage ;
2. expliquer comment un routeur choisit une route ;
3. distinguer longueur de préfixe, distance administrative et métrique ;
4. diagnostiquer une route statique incorrecte ou non installée ;
5. repérer les problèmes courants de voisinage OSPF ;
6. diagnostiquer une session BGP inactive, une route absente ou une route reçue mais non installée ;
7. utiliser `show ip route`, `show ip ospf neighbor`, `show bgp summary`, `ip route get` et les outils de capture de façon ciblée ;
8. tester le chemin aller **et** le chemin retour ;
9. reconnaître les effets d'une ACL, d'un pare-feu, d'une VRF, d'une politique de routage ou d'un MTU inadapté ;
10. produire un compte rendu reproductible qui relie le symptôme à une cause prouvée.

Ce laboratoire est construit pour apprendre à raisonner. Une commande n'est utile que si tu sais quelle hypothèse elle teste et quel résultat confirmerait ou invaliderait cette hypothèse.

## 2. Règles de sécurité et préparation

- Réalise les manipulations dans Packet Tracer, GNS3, CML, EVE-NG, Containerlab ou des VM dédiées. N'injecte pas de pannes dans un réseau de production.
- Les adresses `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont réservées à la documentation. Elles conviennent aux exercices, pas à une utilisation publique réelle.
- Avant un changement, enregistre l'état initial : configuration, tables de routage, adjacences, interfaces et résultats de tests.
- Change une seule variable à la fois. Si tu modifies plusieurs routes, timers et filtres ensemble, tu perds la possibilité d'identifier la cause.
- Évite les commandes de débogage verbeuses sur un équipement chargé. Dans un labo, active-les uniquement pendant une durée limitée et désactive-les ensuite.
- N'efface pas les tables ni les sessions avant d'avoir capturé les éléments qui expliquent l'incident.

### Outils recommandés

| Outil | Utilité |
|---|---|
| `ping` | Tester l'ICMP et une partie du chemin IP ; un échec n'identifie pas à lui seul la cause |
| `traceroute` / `tracert` | Observer les sauts qui répondent aux sondes ; certains routeurs filtrent ou limitent les réponses |
| `show ip route` | Examiner les routes IPv4 installées sur Cisco |
| `show ip cef` | Examiner le transfert CEF lorsque disponible |
| `show ip ospf neighbor` | Vérifier les adjacences OSPF |
| `show bgp summary` ou `show ip bgp summary` | Vérifier l'état des sessions BGP selon la plateforme/version |
| `ip route`, `ip route get`, `ip rule` | Examiner les routes et les décisions de routage Linux |
| `tcpdump` / Wireshark | Vérifier où un paquet apparaît ou disparaît |
| `show access-lists`, `nft list ruleset` | Examiner des mécanismes de filtrage pouvant bloquer les flux |

Les noms et options exacts varient selon la plateforme et la version. Vérifie l'aide CLI ou la documentation correspondant au système utilisé.


## 3. Topologie de référence NovaTech

La maquette principale comprend trois routeurs, deux LAN et deux liens de transit.

```text
PC-A                 R1                  R2                  R3                 PC-C
192.0.2.10/24 -- 192.0.2.1 | 10.0.12.1 -- 10.0.12.2 | 10.0.23.1 -- 10.0.23.2 | 198.51.100.1 -- 198.51.100.10/24
      LAN-A                   lien R1-R2                  lien R2-R3                       LAN-C
```

### Plan d'adressage

| Segment | Interface | Adresse | Rôle |
|---|---|---|---|
| LAN-A | R1 LAN | `192.0.2.1/24` | Passerelle de PC-A |
| LAN-A | PC-A | `192.0.2.10/24` | Hôte de test |
| Transit R1–R2 | R1 | `10.0.12.1/30` | Prochain saut vers R2 |
| Transit R1–R2 | R2 | `10.0.12.2/30` | Interface de retour vers R1 |
| Transit R2–R3 | R2 | `10.0.23.1/30` | Prochain saut vers R3 |
| Transit R2–R3 | R3 | `10.0.23.2/30` | Interface de retour vers R2 |
| LAN-C | R3 LAN | `198.51.100.1/24` | Passerelle de PC-C |
| LAN-C | PC-C | `198.51.100.10/24` | Hôte de test |

Le premier objectif est de permettre à PC-A et PC-C de communiquer. Le chemin aller passe par R1, R2 et R3 ; le retour doit également être possible. L'absence d'une route retour constitue une cause très fréquente d'échec apparent alors que la route aller existe.

### Vérification de départ

Avant les exercices, assure-toi que chaque routeur connaît ses réseaux directement connectés et que chaque PC a la bonne passerelle.

Sur Cisco :

```text
show ip interface brief
show ip route connected
show ip route
show arp
```

Sur Linux :

```bash
ip -br address
ip route show
ip neigh show
```

Depuis PC-A, teste d'abord la passerelle `192.0.2.1`. Depuis PC-C, teste `198.51.100.1`. Si ces tests locaux échouent, ne commence pas par modifier OSPF ou BGP : le problème est plus proche de l'hôte, de l'interface ou du segment local.


## 4. La méthode de dépannage : du symptôme à la cause

### Étape 1 — Définir exactement le flux en panne

Note la source, la destination, le protocole, le port si pertinent, le réseau source, le réseau destination, l'heure de début et l'étendue de l'incident. « Le réseau ne fonctionne pas » n'est pas un symptôme assez précis.

Questions utiles :

- Un poste est-il touché ou tous les postes d'un VLAN ?
- Une seule destination échoue-t-elle ou toutes les destinations distantes ?
- Le ping de la passerelle fonctionne-t-il ?
- Le trafic échoue-t-il dans un seul sens ?
- L'incident affecte-t-il IPv4, IPv6 ou les deux ?
- Une modification de route, de filtre ou d'interface précède-t-elle le problème ?

### Étape 2 — Vérifier l'adresse et la passerelle sur la source

Un hôte ayant un masque trop large peut considérer une destination distante comme locale et envoyer des requêtes ARP au lieu d'envoyer le paquet à sa passerelle. À l'inverse, un masque trop étroit peut envoyer une destination locale vers la passerelle inutilement.

Linux :

```bash
ip -br address
ip route show
ip route get 198.51.100.10
ip neigh show
```

Windows :

```text
ipconfig /all
route print
arp -a
```

`ip route get` indique la décision de routage que le noyau Linux appliquerait à cette destination depuis le contexte courant. Il ne prouve pas que le prochain saut est joignable ni que toute la route fonctionne.

### Étape 3 — Vérifier la route dans chaque routeur du chemin

Sur chaque routeur, demande-toi :

1. Existe-t-il une route vers le préfixe de destination ?
2. S'agit-il de la route la plus spécifique qui correspond à la destination ?
3. Le prochain saut est-il joignable et résolu ?
4. Quelle est la source de la route : connected, static, OSPF, BGP, autre ?
5. Le paquet est-il envoyé vers l'interface attendue ?
6. Le routeur suivant sait-il atteindre le réseau de destination ?
7. Existe-t-il une route retour vers le préfixe source ?

Cisco :

```text
show ip route 198.51.100.10
show ip route 192.0.2.10
show ip cef 198.51.100.10
show arp
```

Linux :

```bash
ip route get 198.51.100.10
ip route show table all
ip neigh show
```

### Étape 4 — Vérifier le chemin réel

Un `traceroute` aide à localiser la zone où les sondes cessent de recevoir une réponse, mais il ne révèle pas forcément tous les routeurs : certains limitent les réponses ICMP ou filtrent les sondes. Une capture de paquets sur une interface stratégique peut montrer si le paquet entre et ressort du routeur.

Linux :

```bash
traceroute -n 198.51.100.10
```

Sur certains systèmes, `tracepath` ou `traceroute` doit être installé séparément. Sous Windows, `tracert 198.51.100.10` peut être utilisé.

### Étape 5 — Examiner les politiques et les couches adjacentes

Si la route semble correcte, inspecte les ACL, pare-feu, VRF, politiques de routage, NAT, MTU et paramètres de forwarding. Un chemin visible dans la table de routage n'est pas une garantie de réussite applicative.


## 5. TP 1 — Panne locale ou panne de routage ?

**Niveau :** débutant  
**Objectif :** ne pas confondre un problème d'hôte avec une route absente.

### Situation de départ

PC-A (`192.0.2.10/24`) doit joindre sa passerelle R1 (`192.0.2.1/24`).

### Manipulation A — Tout fonctionne

1. Vérifie l'adresse, le masque et l'état du lien de PC-A.
2. Vérifie l'adresse et l'état de l'interface LAN de R1.
3. Ping la passerelle depuis PC-A.
4. Consulte ARP sur PC-A et R1.

### Manipulation B — Mauvais masque

Modifie temporairement le masque de PC-A pour le rendre incorrect. Teste d'abord la passerelle locale, puis une adresse du réseau distant. Compare les entrées de voisinage et les paquets ARP à l'aide d'une capture si possible.

Restaure immédiatement le masque `/24` après l'observation.

### Manipulation C — Mauvaise passerelle

Définis une passerelle qui n'est pas l'interface de R1. Vérifie si l'hôte peut toujours joindre des destinations locales et s'il peut joindre le réseau distant.

### Résultat attendu

Une mauvaise passerelle touche principalement les destinations qui doivent sortir du sous-réseau. Une erreur de masque peut modifier la décision locale ou distante de l'hôte. Les deux problèmes doivent être identifiés à partir de l'adresse, du masque, de la table de routage et des voisins — pas en ajoutant une route sur R2 ou R3.

**À rendre :** une comparaison des trois états, avec l'indice le plus utile dans chaque cas.


## 6. TP 2 — Route statique absente et route retour oubliée

**Niveau :** débutant → intermédiaire  
**Objectif :** corriger une connectivité unidirectionnelle.

### Étape A — Configurer les réseaux connectés

Configure toutes les interfaces selon le plan d'adressage. Sur chaque routeur, vérifie que ses sous-réseaux directement connectés sont installés. Ne passe à la suite que lorsque les voisins sur les liens de transit peuvent se joindre par leurs adresses directement connectées.

### Étape B — Ajouter les routes statiques

Exemple de commandes Cisco IOS. Adapte les noms d'interface et confirme les adresses réelles avant de les appliquer.

Sur R1, route vers LAN-C :

```text
ip route 198.51.100.0 255.255.255.0 10.0.12.2
```

Sur R2, routes vers les deux LAN :

```text
ip route 192.0.2.0 255.255.255.0 10.0.12.1
ip route 198.51.100.0 255.255.255.0 10.0.23.2
```

Sur R3, route vers LAN-A :

```text
ip route 192.0.2.0 255.255.255.0 10.0.23.1
```

Vérifie ensuite les routes :

```text
show ip route
show ip route 198.51.100.10
show ip route 192.0.2.10
```

### Étape C — Provoquer l'oubli de la route retour

Retire temporairement sur R3 la route vers `192.0.2.0/24` ou désactive l'annonce dynamique de ce réseau, selon la variante choisie. Depuis PC-A, tente de joindre PC-C ; observe ensuite le chemin retour.

Le paquet peut atteindre PC-C, mais la réponse de PC-C ne saura plus comment rejoindre `192.0.2.10`. Le symptôme depuis le client est un timeout, même si le chemin aller est correct.

### Dépannage attendu

1. Vérifier la route de R1 vers LAN-C.
2. Vérifier le passage par R2 et la route vers LAN-C.
3. Vérifier la route connectée de R3 vers LAN-C.
4. Vérifier la route de R3 vers LAN-A.
5. Capturer le flux dans les deux sens si le résultat n'est pas évident.

**À rendre :** sorties de `show ip route` avant et après la panne et explication du chemin aller/retour.


## 7. TP 3 — Route par défaut mal configurée

**Niveau :** intermédiaire  
**Objectif :** comprendre le comportement d'une route par défaut et ses limites.

Une route par défaut correspond à une destination pour laquelle aucune route plus spécifique n'est disponible. Elle ne doit pas remplacer les routes spécifiques nécessaires à la topologie et son prochain saut doit être correctement résolu.

### Manipulation

Sur R1, supprime la route statique vers LAN-C et ajoute, dans un premier temps, une route par défaut vers R2 :

```text
no ip route 198.51.100.0 255.255.255.0 10.0.12.2
ip route 0.0.0.0 0.0.0.0 10.0.12.2
```

Vérifie la table et le chemin vers PC-C. Ensuite, provoque une erreur dans le prochain saut de la route par défaut et observe si la route est installée et utilisée comme attendu.

Sur certains équipements, une route statique utilisant une interface de sortie et une route statique utilisant un prochain saut sont traitées différemment, notamment sur un réseau multi-accès. Dans le labo, préfère un prochain saut explicite sur un lien point-à-point lorsque c'est adapté.

### Questions

- Pourquoi la route par défaut ne corrige-t-elle pas forcément une panne de route retour ?
- Que se passe-t-il si un routeur possède une route plus spécifique vers le même réseau ?
- Pourquoi une route par défaut dont le prochain saut est incorrect peut-elle conduire à une perte de trafic ?


## 8. TP 4 — Comprendre la sélection de route

**Niveau :** intermédiaire → avancé

Trois notions doivent être distinguées :

1. **Correspondance du préfixe :** pour transférer un paquet, on sélectionne la route de préfixe le plus long qui correspond à l'adresse de destination (longest-prefix match).
2. **Choix entre sources de routage pour un même préfixe :** la distance administrative, dans les plateformes qui l'utilisent, contribue à choisir entre les routes apprises par différentes sources.
3. **Choix au sein du protocole :** la métrique ou les attributs propres au protocole déterminent la préférence parmi ses chemins candidats.

Ces critères ne constituent pas une seule comparaison globale : le mécanisme exact dépend du système et du contexte. La sélection par préfixe le plus long est une étape essentielle du transfert, tandis que la RIB contient les routes retenues selon les règles de la plateforme.

### Exercice A — Route plus spécifique

Suppose que le routeur dispose de ces routes :

```text
192.0.2.0/24      via 10.0.12.2
192.0.2.128/25    via 10.0.23.2
0.0.0.0/0         via 10.0.12.2
```

Explique quelle route serait utilisée pour une destination `192.0.2.200` et quelle route conviendrait à `192.0.2.50`, en supposant que ces routes soient installées et leurs prochains sauts utilisables.

### Exercice B — Routes concurrentes

Dans un simulateur, installe une route statique et apprends le même préfixe par OSPF. Observe laquelle est installée selon les valeurs de distance administrative de ta plateforme. N'assume pas que la métrique OSPF sera comparée directement à la distance administrative de la route statique.

### Exercice C — Route présente dans la table de protocole, absente de la RIB

Pour un protocole dynamique, compare la table du protocole, la table de routage installée et le prochain saut. Une route peut être reçue ou visible dans la base d'un protocole sans être retenue dans la table utilisée pour le transfert, par exemple à cause d'une meilleure route concurrente, d'un prochain saut non résolu ou d'une politique.

**À rendre :** un tableau Destination / Routes correspondantes / Route retenue / Justification.


## 9. TP 5 — Dépanner un voisinage OSPF

**Niveau :** intermédiaire  
**Prérequis :** la topologie de référence et les interfaces IP fonctionnent.

### 9.1 Configurer OSPF

Exemple Cisco IOS en aire 0. Adapte les numéros de processus et les interfaces si ta plateforme l'exige.

R1 :

```text
router ospf 10
 router-id 1.1.1.1
 network 192.0.2.0 0.0.0.255 area 0
 network 10.0.12.0 0.0.0.3 area 0
```

R2 :

```text
router ospf 10
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
```

R3 :

```text
router ospf 10
 router-id 3.3.3.3
 network 10.0.23.0 0.0.0.3 area 0
 network 198.51.100.0 0.0.0.255 area 0
```

Les commandes `network` ci-dessus illustrent la syntaxe Cisco. Sur d'autres systèmes ou sur une configuration OSPF par interface, la méthode est différente. Les commandes de configuration n'activent pas automatiquement OSPF sur des liens que la plateforme ne considère pas correspondants.

### 9.2 Vérifier les adjacences et les routes

```text
show ip ospf neighbor
show ip ospf interface brief
show ip protocols
show ip route ospf
show ip ospf database
```

Attendu : R1 établit une adjacence avec R2 sur le lien de transit, R2 avec R1 et R3, et R3 avec R2. Les préfixes distants doivent apparaître dans les routes OSPF si les annonces et la sélection de route sont correctes.

### 9.3 Injecter des pannes une par une

**Panne A — Mauvaise aire.** Configure temporairement le lien de transit de R1 dans une aire différente de celle de R2. Vérifie l'état des voisins et les journaux. Restaure l'aire 0.

**Panne B — OSPF absent sur une interface.** Retire le réseau de transit des commandes `network`, ou désactive OSPF sur l'interface dans un modèle par interface. Observe la disparition de l'adjacence ou l'absence de route.

**Panne C — Interface passive.** Configure par erreur une interface de transit en mode passif. Dans beaucoup d'implémentations, une interface passive n'envoie pas de paquets Hello et ne forme pas de voisinage, même si son réseau peut être annoncé selon la configuration. Confirme le comportement exact sur le système utilisé.

**Panne D — Coût inattendu.** Modifie le coût OSPF d'un lien et observe le changement de chemin. Vérifie la table et le trafic, pas uniquement la configuration.

### 9.4 Diagnostic d'un état OSPF

Un voisinage qui ne se forme pas peut être lié à l'adressage, au masque, à l'aire, aux timers Hello/Dead, au type de réseau, à l'authentification, à MTU, à un filtre ou au fait qu'OSPF ne soit pas activé sur l'interface. Si l'état reste bloqué en `EXSTART` ou `EXCHANGE`, examine notamment la MTU et l'échange des descriptions de base de données, sans supposer que la MTU est toujours la cause.

**À rendre :** état voisin avant/après chaque panne, route distante concernée et explication de la cause.


## 10. TP 6 — Une adjacence OSPF existe, mais la route manque

**Niveau :** avancé

### Scénario

R1 et R2 sont voisins OSPF, mais PC-A ne peut pas atteindre LAN-C. Le voisinage est établi, donc il serait incorrect de conclure que tout OSPF fonctionne.

### Méthode

1. Sur R3, vérifie que LAN-C est actif et apparaît comme route connectée.
2. Vérifie qu'OSPF est activé sur l'interface LAN-C ou que le préfixe est annoncé par le mécanisme prévu.
3. Vérifie la base LSDB : le réseau attendu y est-il représenté ?
4. Vérifie si R2 apprend le préfixe.
5. Vérifie si R1 le reçoit et l'installe dans sa RIB.
6. Contrôle les filtres, les politiques, les résumés et les routes concurrentes.
7. Vérifie le retour vers LAN-A.

### Commandes utiles

```text
show ip route 198.51.100.0
show ip ospf database
show ip ospf interface brief
show ip protocols
show ip route
```

### Pannes possibles à explorer

- le LAN-C n'est pas annoncé dans OSPF ;
- le réseau est inclus dans une configuration de façon incorrecte ;
- la route est filtrée ou résumée de façon inattendue ;
- une route concurrente est retenue ;
- le préfixe est visible dans la LSDB mais pas installé dans la RIB ;
- une redistribution ou une frontière d'aire introduit une politique inattendue.

**Critère de réussite :** tu dois préciser à quelle étape le préfixe disparaît : source, annonce, réception, filtrage, sélection ou installation.


## 11. TP 7 — Dépanner une session BGP

**Niveau :** avancé  
**Environnement :** deux routeurs Cisco de laboratoire ou FRRouting. Le peering BGP nécessite une connectivité IP entre les adresses de voisinage.

### Variante FRR : topologie minimale

Ajoute un lien point-à-point entre deux routeurs de laboratoire :

- R1 : `10.0.12.1/30`, AS 65010 ;
- R2 : `10.0.12.2/30`, AS 65020 ;
- un préfixe de test derrière chaque routeur.

Exemple de configuration FRR sur R1 :

```text
configure terminal
router bgp 65010
 bgp router-id 1.1.1.1
 neighbor 10.0.12.2 remote-as 65020
 address-family ipv4 unicast
  neighbor 10.0.12.2 activate
  network 192.0.2.0/24
 exit-address-family
end
```

Exemple sur R2 :

```text
configure terminal
router bgp 65020
 bgp router-id 2.2.2.2
 neighbor 10.0.12.1 remote-as 65010
 address-family ipv4 unicast
  neighbor 10.0.12.1 activate
  network 198.51.100.0/24
 exit-address-family
end
```

Ces exemples supposent que chaque préfixe `network` existe dans la table de routage correspondante et que l'adressage du lien est configuré. La syntaxe exacte varie selon la version FRR et l'environnement. Pour un déploiement réel, prépare aussi une politique explicite d'import/export : ce labo n'est pas une politique BGP de production.

### Vérifier la session et les préfixes

Dans FRR, selon la version :

```text
show bgp summary
show bgp ipv4 unicast
show bgp neighbors 10.0.12.2
show bgp neighbors 10.0.12.2 advertised-routes
```

Sur Cisco, les commandes usuelles comprennent :

```text
show ip bgp summary
show ip bgp
show ip bgp neighbors
show ip route bgp
```

La syntaxe évolue selon l'OS et la version ; vérifie les commandes prises en charge.

### Lire les états BGP

| État ou symptôme | Ce qu'il indique généralement | Contrôles à mener |
|---|---|---|
| Idle | La session n'a pas encore progressé vers l'établissement | Configuration, activation du voisin, route vers le pair, événements de processus |
| Connect / Active | Tentatives d'établissement TCP mais session non établie | Connectivité TCP/179, ACL, adresse source, AS distant, multihop si pertinent |
| OpenSent / OpenConfirm | L'échange initial BGP progresse mais ne se termine pas | Paramètres de voisinage, capacités et journaux |
| Established, zéro préfixe reçu | La session fonctionne mais aucune route utile n'est reçue/acceptée pour cette famille | Activation de l'address-family, annonces, filtres, politique par défaut, préfixe de réseau présent |
| Préfixe visible dans BGP, absent de la RIB | Route non retenue ou prochain saut non résolu | Route concurrente, next-hop, politique, VRF, table de routage |
| Préfixe installé mais trafic échoue | Le routage seul n'explique pas toute la panne | Route retour, ACL, pare-feu, MTU, chemin réel, état du service |

Les noms et sorties des états peuvent varier quelque peu entre plateformes. BGP utilise TCP, généralement sur le port 179 ; les filtres et la connectivité du pair doivent être vérifiés dans les deux sens.

### Injecter les pannes

1. Configure un mauvais AS distant et observe les journaux de négociation.
2. Bloque TCP/179 uniquement dans le laboratoire et observe l'état de la session.
3. Retire le préfixe `network` ou la route correspondante et vérifie l'annonce.
4. Ajoute une politique qui filtre le préfixe de test ; vérifie la route reçue et la route acceptée.
5. Corrige chaque panne et consigne les preuves.

**Important :** ne laisse pas une session BGP d'entreprise annoncer tous les préfixes sans filtre approprié. Utilise des prefix-lists/route-maps ou les mécanismes de politique pertinents, adaptés à la conception et à la plateforme.


## 12. TP 8 — Route BGP reçue mais non installée

**Niveau :** expert

Une session BGP en `Established` indique que la relation de protocole est établie ; elle ne prouve pas que la route voulue est acceptée, considérée comme meilleure et installée dans la table utilisée pour le transfert.

### Démarche d'analyse

1. Le voisin annonce-t-il le préfixe ?
2. Le routeur local le reçoit-il ?
3. Une politique d'importation le rejette-t-elle ?
4. Le préfixe est-il valide pour l'adresse-family activée ?
5. Le prochain saut est-il joignable ?
6. Une autre route ou une politique de sélection rend-elle ce chemin non gagnant ?
7. La route apparaît-elle dans la table de routage finale ?
8. La route retenue permet-elle un chemin retour cohérent ?

### Commandes à essayer

FRR, selon la version :

```text
show bgp ipv4 unicast
show bgp neighbors 10.0.12.2 routes
show bgp neighbors 10.0.12.2 received-routes
show ip route 198.51.100.0/24
```

Certaines commandes `received-routes` requièrent une fonctionnalité de conservation des routes reçues ou ne sont pas disponibles sans la configuration correspondante. Consulte la documentation de la version exacte.

Cisco IOS/IOS XE, selon la version :

```text
show ip bgp
show ip bgp neighbors
show ip route 198.51.100.0
show ip cef 198.51.100.10
```

### Exercice

Crée deux chemins candidats vers un même préfixe de laboratoire. Modifie une préférence BGP ou une politique d'importation et observe le chemin élu. N'attribue pas un comportement unique à tous les réseaux BGP : l'ordre de sélection comporte de nombreux critères et certains attributs sont propres à l'implémentation ou à la politique.

**À rendre :** le préfixe dans la table BGP, son état de validité, la raison de sa sélection ou non-sélection et son statut dans la RIB.


## 13. TP 9 — La route paraît correcte, mais le ping échoue

**Niveau :** intermédiaire → avancé

Ce scénario oblige à dépasser la seule table de routage.

### Étapes

1. Sur PC-A, confirme l'adresse source et le routage vers `198.51.100.10`.
2. Sur R1, vérifie le préfixe de LAN-C et le prochain saut vers R2.
3. Sur R2, confirme les routes des deux LAN.
4. Sur R3, confirme la route de retour vers LAN-A.
5. Vérifie les ACL d'interface dans le bon sens.
6. Vérifie si une capture voit la requête ICMP entrer et ressortir sur chaque interface pertinente.
7. Contrôle si les réponses sont produites et où elles disparaissent.

Cisco :

```text
show access-lists
show ip interface
show ip route
show ip cef 198.51.100.10
show logging
```

Linux :

```bash
ip route get 198.51.100.10
sudo nft list ruleset
sudo tcpdump -ni any 'icmp and host 198.51.100.10'
```

### Hypothèses possibles

- ACL qui bloque les requêtes ou réponses ICMP ;
- route retour absente ;
- interface avec adresse ou masque incorrect ;
- route sélectionnée via un next-hop non voulu ;
- hôte destination mal configuré ;
- pare-feu hôte qui refuse l'ICMP ;
- VRF ou namespace différent de celui attendu ;
- MTU ou autre problème spécifique au trafic réel, même si les petits pings passent.

### Distinguer route absente et filtrage

Si une route manque, le routeur n'a pas de chemin de transfert conforme au plan prévu. Si une ACL bloque le paquet, le routeur peut posséder une route correcte mais jeter le paquet conformément à sa politique. Cherche les compteurs, les journaux et les captures plutôt que d'ajouter une route statique pour contourner un filtrage.


## 14. TP 10 — Linux : observer la décision de routage

**Niveau :** intermédiaire

Sur Linux, le résultat de routage dépend non seulement de la table principale : des règles de routage par politique (`ip rule`), des VRF, des espaces de noms et d'autres paramètres peuvent influencer la décision.

### Commandes essentielles

```bash
ip -br address
ip route show
ip route show table all
ip rule show
ip route get 198.51.100.10
ip neigh show
```

`ip route get DESTINATION` montre la route calculée dans le contexte de la requête et constitue un moyen rapide de vérifier l'interface, le prochain saut et parfois l'adresse source choisie.

### Panne A — Route manquante

Dans une VM isolée, supprime une route de laboratoire et constate le résultat de `ip route get`. Remets-la ensuite exactement comme prévu.

### Panne B — Routage IP désactivé sur un routeur Linux

Dans une topologie dédiée où la VM joue réellement le rôle de routeur, vérifie :

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

Active le transfert uniquement si ce système doit effectivement router le trafic. Le réglage IPv4 et celui d'IPv6 sont distincts. Sur une VM connectée à un réseau réel, ne modifie pas ces paramètres sans avoir compris les conséquences.

### Panne C — Mauvaise source

Un chemin de retour peut dépendre de l'adresse source choisie par l'hôte. Utilise `ip route get` avec une adresse source ou une interface imposée lorsque c'est pertinent, et compare avec la route réellement attendue.

**À rendre :** captures de `ip route`, `ip rule` et `ip route get` avant et après une panne.


## 15. TP 11 — Routage par politique Linux (`ip rule`)

**Niveau :** expert

Le routage par politique permet de sélectionner une table selon des critères tels qu'une source ou une marque, au lieu de dépendre uniquement de la table principale. Cela peut expliquer pourquoi une route semble présente mais n'est pas utilisée par un flux donné.

### Démonstration conceptuelle

Dans une VM de test, inspecte les règles :

```bash
ip rule show
ip route show table all
ip route get 198.51.100.10 from 192.0.2.10
```

Les numéros de table, priorités et règles dépendent de la configuration. Avant d'en ajouter, documente les règles existantes et choisis des identifiants propres au labo. Une règle plus prioritaire peut capturer le trafic et conduire à une table sans route valide.

### Exercice

Crée deux chemins de laboratoire et deux tables de routage isolées. Ajoute une règle basée sur une adresse source dédiée au test. Compare la décision de `ip route get` pour deux sources différentes et vérifie le trafic réel avec une capture. Supprime ensuite les règles et tables ajoutées au labo.

### Contrôle important

Ne traite pas `ip route show` sans précision comme une représentation complète de tous les chemins possibles : les règles et tables supplémentaires doivent aussi être examinées. Dans une architecture avec VRF, exécute les commandes dans le bon contexte.


## 16. TP 12 — IPv6 : route et chemin retour

**Niveau :** intermédiaire

Reprends la topologie et attribue des préfixes de documentation IPv6 :

- LAN-A : `2001:db8:10::/64` ; R1 `2001:db8:10::1` ; PC-A `2001:db8:10::10` ;
- lien R1–R2 : `2001:db8:12::/64` ; R1 `::1`, R2 `::2` ;
- lien R2–R3 : `2001:db8:23::/64` ; R2 `::1`, R3 `::2` ;
- LAN-C : `2001:db8:30::/64` ; R3 `2001:db8:30::1` ; PC-C `2001:db8:30::10`.

Le préfixe `2001:db8::/32` est réservé aux exemples et à la documentation.

### Vérifications

Cisco :

```text
show ipv6 interface brief
show ipv6 route
show ipv6 neighbors
```

Linux :

```bash
ip -6 address show
ip -6 route show
ip -6 neigh show
ping -6 2001:db8:30::10
traceroute -6 2001:db8:30::10
```

### Pannes à injecter

1. Oublie une route IPv6 retour.
2. Désactive le forwarding IPv6 sur un routeur Linux de labo.
3. Configure un préfixe incorrect sur un côté du lien.
4. Vérifie les règles de pare-feu ICMPv6 sans bloquer aveuglément tous les messages ICMPv6.

### Analyse

IPv4 et IPv6 possèdent des tables et des mécanismes de voisinage distincts. Une route IPv4 correcte ne prouve pas que l'IPv6 est opérationnel. L'adressage link-local et Neighbor Discovery jouent aussi un rôle essentiel dans IPv6.


## 17. TP 13 — VRF ou contexte de routage incorrect

**Niveau :** avancé

Une **VRF** sépare des tables de routage. Deux interfaces peuvent être actives et adresser des réseaux cohérents, mais le flux peut échouer si la route est recherchée dans la mauvaise VRF ou si le partage de routes n'a pas été conçu explicitement.

### Procédure

1. Confirme à quelle VRF appartient l'interface source.
2. Affiche la table de routage de cette VRF, pas uniquement celle par défaut.
3. Confirme que la destination attendue existe dans la bonne table.
4. Vérifie si un route leaking est nécessaire et s'il est configuré de manière ciblée.
5. Vérifie le chemin retour dans le contexte correct.

Commandes possibles sur certains IOS/IOS XE :

```text
show vrf
show ip route vrf NOM_VRF
show ip interface brief
```

La syntaxe précise dépend de la version. Sur Linux, les VRF peuvent être examinées via `ip link`, `ip route show table` et les commandes exécutées dans le contexte adéquat.

### Panne à reproduire

Dans une maquette qui utilise deux VRF, place temporairement une interface dans une VRF incorrecte ou retire une route de la table de test. Vérifie la table dans laquelle le routeur cherche la destination. Restaure ensuite le contexte attendu.

**À rendre :** schéma des VRF, préfixes propres à chacune et justification des routes partagées.


## 18. TP 14 — ECMP, asymétrie et chemins alternatifs

**Niveau :** expert

ECMP (*Equal-Cost Multi-Path*) permet d'utiliser plusieurs chemins considérés équivalents selon la plateforme et le protocole. Une topologie multi-chemins peut améliorer la capacité ou la résilience, mais les flux ne sont pas nécessairement répartis paquet par paquet. De nombreux équipements utilisent du hachage par flux afin de préserver l'ordre des paquets.

### Exercice

Crée deux chemins de coût équivalent entre deux routeurs dans une maquette supportant ECMP. Observe :

- les chemins installés dans la table de routage ;
- les prochains sauts utilisés dans la table de transfert ;
- l'effet d'une panne sur l'un des chemins ;
- la stabilité des flux existants ;
- le chemin retour et l'effet éventuel des pare-feu à état.

### Points de vigilance

- Deux chemins annoncés ne prouvent pas que les deux transportent le trafic attendu.
- Un changement de hachage peut déplacer des flux existants.
- Un pare-feu à état ou un NAT peut mal gérer une asymétrie si la conception ne la prévoit pas.
- Le retour du lien peut provoquer un changement de chemin ou une convergence qui mérite d'être observée.

Documente le comportement constaté dans ta plateforme au lieu de présumer qu'il est universel.


## 19. TP 15 — MTU et PMTUD : petits pings fonctionnels, application en panne

**Niveau :** avancé

Une route valide peut transporter de petits paquets et échouer pour certains paquets plus grands à cause du MTU ou d'un mécanisme de découverte du MTU du chemin (PMTUD) perturbé.

### Procédure

1. Confirme d'abord le chemin avec de petits paquets.
2. Augmente progressivement la taille du paquet dans une maquette adaptée.
3. Observe les éventuels messages ICMP liés à la fragmentation ou au MTU.
4. Inspecte les interfaces et l'encapsulation le long du chemin.
5. Compare le comportement avec une capture aux deux extrémités.

Exemple Linux pour un test IPv4 de type ping sans fragmentation, si le système prend en charge les options utilisées :

```bash
ping -M do -s 1200 -c 3 198.51.100.10
```

La taille `-s` correspond à la charge utile ICMP, pas à la taille totale de la trame. Ajuste-la selon la famille IP et les en-têtes. Les options disponibles et leur interprétation varient selon l'OS.

### Diagnostic

Ne diminue pas la MTU au hasard. Vérifie où l'encapsulation ajoute des en-têtes, si les messages ICMP nécessaires sont bloqués et si le problème concerne uniquement certains flux ou tailles de paquets. Une modification doit être validée sur le chemin complet.


## 20. TP 16 — Lire les captures pour localiser une perte

**Niveau :** avancé

La meilleure capture est prise à un endroit qui permet de distinguer les hypothèses. Capturer partout sans question précise peut générer beaucoup de données sans accélérer le diagnostic.

### Exemple de filtres tcpdump

Sur un routeur Linux de labo :

```bash
sudo tcpdump -ni any 'host 198.51.100.10'
sudo tcpdump -ni eth0 'icmp'
sudo tcpdump -ni eth1 'host 192.0.2.10 and host 198.51.100.10'
```

Remplace les interfaces par celles réellement utilisées. Pour le protocole concerné, capture également TCP/UDP et les ports applicatifs, pas uniquement ICMP.

### Interprétation par interfaces

| Observation | Hypothèse à examiner |
|---|---|
| Paquet absent à l'interface d'entrée | Source, VLAN, lien, capture au mauvais endroit ou filtre en amont |
| Paquet présent à l'entrée mais absent à la sortie | Route, next-hop, VRF, filtre ou problème local de transfert |
| Paquet quitte le routeur mais n'arrive pas au suivant | Underlay, lien, ACL intermédiaire ou capture incorrecte |
| Requête atteint la destination mais aucune réponse n'est créée | Pare-feu hôte, service, politique locale ou application |
| Réponse quitte la destination mais disparaît sur le retour | Route retour, filtrage retour, asymétrie ou NAT |
| ICMP réussit mais application échoue | Port, transport, MTU, politique de sécurité ou service applicatif |

Une capture sur une interface logicielle peut montrer un paquet avant ou après certaines étapes de traitement selon l'OS, les déchargements matériels et le point de capture. Corrobore les observations avec les compteurs et les tables de routage.


## 21. TP 17 — Incident multi-cause : la route existe mais le flux est bloqué

**Niveau :** expert

### Situation

Le support NovaTech rapporte que PC-A ne peut plus accéder à un service sur LAN-C. Les interfaces sont UP ; R1 possède une route vers LAN-C ; R3 peut joindre son réseau local.

### Mission

Diagnostique le problème sans redémarrer les routeurs et sans ajouter une route par défaut comme contournement immédiat.

1. Définis précisément le flux et teste la passerelle locale.
2. Examine la décision de routage sur PC-A, R1, R2 et R3.
3. Confirme que le préfixe de destination est installé sur chaque étape.
4. Vérifie la route retour vers `192.0.2.0/24`.
5. Compare les ACL, les filtres et les compteurs.
6. Capture le flux au point qui distingue le mieux les hypothèses.
7. Vérifie si le trafic applicatif utilise le port et le protocole attendus.
8. Provoque une seule hypothèse à la fois dans le labo.
9. Corrige et effectue les tests de non-régression.
10. Documente la cause racine et une mesure préventive.

### Hypothèses à départager

- route retour manquante ;
- mauvais prochain saut ;
- préfixe plus spécifique inattendu ;
- route installée dans la mauvaise VRF ;
- ACL ou pare-feu ;
- voisin L2 ou résolution ARP/ND ;
- problème de MTU ;
- service destination à l'arrêt ;
- asymétrie ou NAT ;
- problème propre à IPv6 alors qu'IPv4 fonctionne.

### Critère de réussite

Une correction est acceptée seulement si tu peux montrer : la cause, l'indice qui l'a révélée, la modification minimale, le résultat après correction et l'absence de régression sur les flux adjacents.


## 22. Arbre de décision de dépannage

```text
Le flux ne fonctionne pas
          |
          v
La source atteint-elle sa passerelle ?
    | oui                         | non
    v                             v
Route vers destination ?      Corriger IP / masque / VLAN / voisin local
    | oui         | non
    v             v
Next-hop et     Identifier la route absente
sortie valides ? puis corriger la source d'annonce
    | oui       | non
    v           v
Filtrage, VRF,  Corriger next-hop / interface / voisinage
MTU, service ou route retour ?
    |
    v
Capture + test retour + validation applicative
```

Cet arbre sert de guide, pas de séquence rigide. Si une capture fournit déjà une preuve forte sur une couche, tu peux adapter l'ordre. Il reste essentiel de distinguer la présence d'une route de la réussite de bout en bout.


## 23. Tableau de commandes récapitulatif

| Objectif | Cisco IOS/IOS XE | Linux / FRR |
|---|---|---|
| Interfaces | `show ip interface brief` | `ip -br address`, `ip link` |
| Routes IPv4 | `show ip route` | `ip route show table all` |
| Route vers destination | `show ip route ADRESSE` | `ip route get ADRESSE` |
| Adjacences OSPF | `show ip ospf neighbor` | `show ip ospf neighbor` selon FRR |
| Routes OSPF | `show ip route ospf` | `show ip route ospf` selon FRR |
| Base OSPF | `show ip ospf database` | `show ip ospf database` selon FRR |
| État BGP | `show ip bgp summary` ou syntaxe version récente | `show bgp summary` |
| Routes BGP | `show ip bgp` | `show bgp ipv4 unicast` |
| Voisins/annonces BGP | `show ip bgp neighbors` | `show bgp neighbors ...` |
| ARP / voisins | `show arp` | `ip neigh show` |
| CEF / transfert | `show ip cef` si disponible | `ip route get`, `ip neigh`, capture |
| ACL / filtrage | `show access-lists`, `show ip interface` | `nft list ruleset` |
| Journaux | `show logging` | `journalctl`, journaux du service |
| Capture | outil de capture disponible sur la plateforme | `tcpdump -ni INTERFACE ...` |
| IPv6 | `show ipv6 route`, `show ipv6 interface brief` | `ip -6 route`, `ip -6 address`, `ip -6 neigh` |

Les commandes affichées sont des exemples communs ; leur syntaxe exacte doit être confirmée selon l'OS et la version.


## 24. Modèle de rapport d'incident

Copie ce modèle pour chaque TP :

```text
Incident / TP :
Date et heure :
Plateforme et version :
Source et destination :
Protocole / port :
Symptôme exact :
Périmètre impacté :
Dernier changement connu :
État interfaces :
Table de routage source :
Routes aux routeurs intermédiaires :
Route retour :
Adjacences (OSPF/BGP si applicables) :
Politique / ACL / VRF :
Capture et compteurs :
Hypothèse testée :
Cause racine confirmée :
Correction minimale :
Tests de non-régression :
Prévention / surveillance :
```

Ne documente pas seulement « redémarré et corrigé ». Cela ne permet pas d'identifier la cause ni d'éviter une récidive.

## 25. Évaluation finale sur 100

| Domaine | Points |
|---|---:|
| Adressage et état des interfaces | 10 |
| Analyse des tables de routage et des next-hops | 15 |
| Routes statiques et chemin retour | 15 |
| Diagnostic OSPF | 15 |
| Diagnostic BGP | 15 |
| Analyse de capture et filtrage | 10 |
| VRF, IPv6, politique de routage ou MTU | 10 |
| Rapport et tests de non-régression | 10 |
| **Total** | **100** |

Le score ne remplace pas la qualité du diagnostic. Une réponse correcte sans preuve n'est pas suffisante pour un exercice de dépannage expert.


## 26. Erreurs fréquentes à éviter

1. Ajouter une route par défaut sans comprendre pourquoi la route spécifique manque.
2. Vérifier seulement le chemin aller et oublier la route retour.
3. Confondre une adjacence OSPF établie avec une annonce correcte de tous les préfixes.
4. Confondre une session BGP `Established` avec une route installée et utilisée.
5. Comparer directement la métrique OSPF à la distance administrative d'une route statique.
6. Oublier le principe du préfixe le plus long lors d'une décision de transfert.
7. Ajouter une route statique pour contourner une ACL ou un problème de filtrage.
8. Supposer que tous les routeurs répondent aux sondes traceroute.
9. Considérer qu'un ping qui réussit garantit que l'application fonctionne.
10. Modifier plusieurs éléments simultanément et perdre la preuve de la cause.
11. Modifier la table ou vider les sessions avant d'avoir sauvegardé l'état de référence.
12. Ignorer le contexte VRF, namespace ou politique de routage.
13. Corriger l'IPv4 sans tester l'IPv6, ou l'inverse.
14. Oublier l'effet de MTU, du NAT ou d'un pare-feu à état sur un chemin asymétrique.
15. Clore l'incident sans mesures préventives ni tests de non-régression.


## 27. Références techniques officielles

- [Cisco — Troubleshoot Common Problems with OSPF](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/12151-trouble-main.html) : diagnostic des adjacences OSPF, des routes et des causes fréquentes de voisinage incomplet.
- [Cisco — Troubleshoot Common BGP Issues](https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/22166-bgp-trouble-main.html) : méthode de dépannage des sessions BGP et des routes.
- [Cisco — `show ip route`, référence des commandes de routage](https://www.cisco.com/c/en/us/td/docs/ios/iproute_pi/command/reference/iri_book/iri_pi2.html) : consultation de la table de routage.
- [Documentation FRRouting — BGP](https://docs.frrouting.org/en/latest/bgp.html) : commandes d'état BGP, tables de routes et voisins. Vérifie la version FRR utilisée, car la syntaxe évolue.
- [Documentation du noyau Linux — IP sysctl](https://docs.kernel.org/networking/ip-sysctl.html) : paramètres réseau du noyau, dont le transfert IPv4/IPv6.

Ces références sont des points de départ. Une syntaxe ou un comportement peut dépendre de la version du routeur, de l'image utilisée ou de l'implémentation du protocole.


## Conclusion

Le dépannage du routage consiste à démontrer comment un paquet est traité à chaque étape. Il faut connaître la source, la destination et le contexte de routage, vérifier la décision de route, confirmer que le prochain saut est exploitable, comprendre les annonces de protocole dynamique, vérifier les politiques et prouver que le retour fonctionne.

Une table de routage correcte est une condition importante, mais elle n'est pas à elle seule la preuve d'une application accessible. La méthode la plus fiable combine état des interfaces, tables de routage, adjacences, compteurs, capture ciblée et tests de bout en bout. Le meilleur résultat est un diagnostic reproductible et une correction minimale, accompagnés de preuves et d'un plan de prévention.
