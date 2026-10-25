# WAR GAME RÉSEAU — Incident OSPF : « Routeur muet »

**Fichier :** `incident-ospf.md`  
**Type :** simulation d'incident réseau / investigation guidée  
**Domaine :** routage dynamique IPv4 — OSPFv2  
**Niveau :** intermédiaire (avec extensions expert)  
**Durée indicative :** 90 à 150 minutes  
**Mode :** solo ou équipe de 2 à 4 personnes  
**Notation :** 100 points  
**Environnement cible :** Cisco IOS/IOS XE ; encadrés de correspondance FRRouting (FRR) lorsque pertinent

> **Objectif de la mission :** rétablir le routage dynamique entre le cœur réseau et un site distant, sans redémarrer les équipements à l'aveugle ni masquer le problème par une route statique inutile.
>
> **Règle du jeu :** lisez le brief et les éléments de preuve dans l'ordre. Arrêtez-vous avant la section « Solution détaillée » pour jouer réellement l'incident. Toutes les informations, les commandes, les indices, le plan de correction, les validations et le débriefing sont contenus dans ce seul fichier.


# 1. Brief de l'incident

## 1.1. Le ticket reçu par l'équipe réseau

**Incident :** INC-OSPF-042  
**Priorité :** P2 — perte de connectivité partielle  
**Début estimé :** 09:17  
**Déclarant :** équipe applicative du site distant  
**Symptôme utilisateur :** « L'application du site distant ne répond plus depuis le siège. Le lien réseau semble actif, mais le site n'apparaît plus dans les routes. »

Depuis le siège, les utilisateurs ne peuvent plus joindre le réseau `192.168.30.0/24` du site distant. Le réseau du siège reste joignable depuis les équipements du cœur. Les interfaces Ethernet semblent actives. Aucun changement réseau n'a été annoncé dans le ticket de changement.

Le NOC indique :

- le ping entre les adresses IP du lien de transit fonctionne depuis un équipement de test ;
- le routeur du site distant répond à une connexion d'administration déjà ouverte ;
- le réseau du site distant n'apparaît plus dans la table de routage OSPF du routeur central ;
- aucun redémarrage ni changement de configuration n'est autorisé sans hypothèse étayée.

Votre mission consiste à identifier pourquoi le routeur distant est « muet » pour OSPF, à corriger la cause, puis à démontrer que le rétablissement est durable.

## 1.2. Ce que vous devez livrer

À la fin de la simulation, vous devez fournir :

1. une chronologie des vérifications ;
2. les preuves distinguant une panne IP d'une panne OSPF ;
3. la cause racine et le mécanisme technique ;
4. un plan de correction à faible risque ;
5. les commandes utilisées avant et après correction ;
6. les résultats prouvant le retour à l'état nominal ;
7. les mesures préventives et les éléments à documenter dans le ticket.

## 1.3. Contraintes opérationnelles

- Ne pas redémarrer les routeurs comme première action.
- Ne pas désactiver globalement les ACL ou les mécanismes de sécurité.
- Ne pas ajouter une route statique pour cacher la panne OSPF.
- Ne pas changer les timers, l'aire ou le type de réseau sans preuve.
- Ne pas modifier plusieurs paramètres à la fois : une correction, une validation.
- En production, vérifier les procédures de changement, la sauvegarde et le plan de retour arrière avant toute modification.


# 2. Topologie de référence

## 2.1. Schéma logique

```text
                    RÉSEAU DU SIÈGE
                      192.168.10.0/24
                              |
                      G0/1 192.168.10.1
                         +---------+
                         |   R1    |  Router ID : 1.1.1.1
                         |  CORE   |  OSPF process 10, area 0
                         +---------+
                      G0/0 10.0.12.1/30
                              |
                  Lien de transit 10.0.12.0/30
                              |
                      G0/0 10.0.12.2/30
                         +---------+
                         |   R2    |  Router ID : 2.2.2.2
                         | DISTRIB.|  OSPF process 10, area 0
                         +---------+
                      G0/1 10.0.23.1/30
                              |
                  Lien de transit 10.0.23.0/30
                              |
                      G0/0 10.0.23.2/30
                         +---------+
                         |   R3    |  Router ID : 3.3.3.3
                         |  SITE   |  OSPF process 10, area 0
                         +---------+
                      G0/1 192.168.30.1/24
                              |
                   RÉSEAU DU SITE DISTANT
                      192.168.30.0/24
```

## 2.2. Plan d'adressage

| Équipement | Interface | Adresse | Fonction |
|---|---|---|---|
| R1 | G0/0 | `10.0.12.1/30` | Transit vers R2 |
| R1 | G0/1 | `192.168.10.1/24` | LAN siège |
| R2 | G0/0 | `10.0.12.2/30` | Transit vers R1 |
| R2 | G0/1 | `10.0.23.1/30` | Transit vers R3 |
| R3 | G0/0 | `10.0.23.2/30` | Transit vers R2 |
| R3 | G0/1 | `192.168.30.1/24` | LAN du site distant |

**Réseaux attendus dans OSPF :** `10.0.12.0/30`, `10.0.23.0/30`, `192.168.10.0/24` et `192.168.30.0/24`.  
**Aire utilisée dans ce scénario :** area 0 pour tous les liens et LAN, afin de ne pas mélanger le diagnostic avec une architecture multi-aires.  
**Process ID local :** 10. Le Process ID est local au routeur Cisco ; il n'a pas besoin d'être identique entre voisins.  
**Router IDs attendus :** R1=`1.1.1.1`, R2=`2.2.2.2`, R3=`3.3.3.3`.

## 2.3. État nominal attendu

```text
R1 : voisin R2 en FULL ; route OSPF vers 192.168.30.0/24
R2 : voisins R1 et R3 en FULL ; routes vers les deux LAN
R3 : voisin R2 en FULL ; route OSPF vers 192.168.10.0/24

R1# show ip ospf neighbor
Neighbor ID     State          Address       Interface
2.2.2.2         FULL/-         10.0.12.2     GigabitEthernet0/0

R2# show ip ospf neighbor
Neighbor ID     State          Address       Interface
1.1.1.1         FULL/-         10.0.12.1     GigabitEthernet0/0
3.3.3.3         FULL/-         10.0.23.2     GigabitEthernet0/1

R3# show ip ospf neighbor
Neighbor ID     State          Address       Interface
2.2.2.2         FULL/-         10.0.23.1     GigabitEthernet0/0
```

Les formats exacts des commandes de sortie varient selon les versions et les plateformes. Les exemples de ce document sont des sorties de laboratoire illustratives, et non des captures garanties d'une version précise.


# 3. Rappel ciblé : ce qu'OSPF doit accomplir

## 3.1. Le rôle d'OSPF

OSPF (Open Shortest Path First) est un protocole de routage à état de liens. Les routeurs découvrent leurs voisins, forment des adjacences lorsque les conditions sont réunies, synchronisent leur base d'état de liens (LSDB), puis calculent les chemins à l'aide de l'algorithme SPF.

Une interface Ethernet opérationnelle ne garantit pas à elle seule qu'OSPF fonctionne. Il faut différencier plusieurs couches :

```text
Physique / lien      : interface et protocole de ligne opérationnels ?
Connectivité IP      : adresses et sous-réseaux corrects ?
Découverte OSPF      : messages Hello envoyés et reçus ?
Adjacence OSPF       : voisin en état FULL lorsque requis ?
Base de données      : LSDB cohérente et LSAs présentes ?
Calcul de routes     : préfixe calculé et installé dans la RIB ?
Plan de données      : le paquet peut-il réellement atteindre sa destination ?
```

## 3.2. États de voisinage à reconnaître

| État | Signification opérationnelle | Piste de diagnostic |
|---|---|---|
| `Down` | Aucun Hello valide reçu récemment, ou voisin absent | Interface, émission/réception Hello, filtrage, voisin réellement actif |
| `Attempt` | État utilisé dans certains réseaux NBMA avec voisins configurés | Configuration du voisin et connectivité NBMA |
| `Init` | Hello reçu, mais communication bidirectionnelle pas encore confirmée | Hello unidirectionnels, ACL, Router ID non vu dans le Hello reçu |
| `2-Way` | Communication bidirectionnelle établie | Normal sur Ethernet entre certains routeurs DROther ; vérifier le rôle DR/BDR |
| `ExStart` | Négociation initiale de l'échange de bases | MTU, négociation maître/esclave, Router ID, séquences DBD |
| `Exchange` | Descriptions de bases échangées | DBD et cohérence de l'échange |
| `Loading` | Demandes de LSAs complémentaires | LS Request/Update, pertes de paquets, LSDB |
| `Full` | Adjacence synchronisée | État attendu entre voisins devant former une adjacence complète |

Sur un lien Ethernet configuré en broadcast, deux routeurs peuvent rester en `2-Way` lorsque l'un ou les deux ne sont pas DR/BDR et qu'une adjacence complète n'est pas requise entre eux. Ne diagnostiquez donc pas toute entrée `2-Way` comme une panne sans connaître le type de réseau et le rôle des routeurs.

## 3.3. Les principaux paramètres de compatibilité

Selon le type de réseau et la configuration, vérifiez notamment :

- les adresses IP, masques et connectivité directe ;
- l'activation d'OSPF sur la bonne interface ;
- l'area ID et le type d'aire ;
- les Hello/Dead intervals ;
- l'authentification OSPF lorsqu'elle est configurée ;
- le type de réseau OSPF ;
- le MTU et les échanges de paquets DBD ;
- l'absence de Router ID dupliqué ;
- l'absence de filtrage des paquets IP protocol 89 ;
- l'état passif ou actif de l'interface ;
- les ressources CPU/mémoire si les symptômes sont intermittents.

Le protocole OSPF utilise le numéro de protocole IP 89, et non TCP ou UDP. Les adresses multicast courantes d'OSPFv2 comprennent `224.0.0.5` (AllSPFRouters) et `224.0.0.6` (AllDRouters).

## 3.4. Différence entre voisinage, LSDB et route

Un voisin `FULL` prouve que l'adjacence est synchronisée ; il ne garantit pas automatiquement qu'un préfixe applicatif particulier est annoncé et installé.

Pour un préfixe absent, contrôlez successivement :

1. le routeur d'origine possède-t-il une route valide vers le préfixe ?
2. ce réseau est-il inclus dans OSPF et, le cas échéant, annoncé en mode passif ?
3. le LSA correspondant est-il présent dans la LSDB ?
4. la route est-elle calculée et acceptée dans la RIB ?
5. une route de meilleure préférence ou une politique ne la masque-t-elle pas ?
6. le retour est-il possible depuis le réseau distant ?


# 4. Ouverture de l'incident : règles de jeu

## 4.1. Informations connues au départ

Vous êtes l'ingénieur d'astreinte. Vous avez accès en lecture à R1, R2 et R3. Vous pouvez demander un nombre raisonnable de commandes de diagnostic. Vous pouvez ensuite proposer une seule modification avant de refaire les vérifications.

**Ne lisez pas encore la section « Solution détaillée ».** Le jeu est plus utile si la cause est établie à partir des preuves plutôt que devinée.

## 4.2. Indices initiaux du NOC

- Le réseau `192.168.10.0/24` du siège reste opérationnel.
- Le réseau `192.168.30.0/24` a disparu de la table de routage du cœur.
- Les interfaces de transit sont affichées `up/up`.
- Un ping depuis R2 vers `10.0.23.2` a réussi une fois.
- Les équipes ne disposent pas d'une preuve de panne physique.

Ces éléments ne désignent pas encore une cause unique. Un ping réussi prouve seulement qu'un test IP donné a réussi dans les conditions testées ; il ne prouve ni le bon fonctionnement d'OSPF, ni le passage des paquets multicast OSPF, ni la validité de toutes les directions du trafic.


# 5. Dossier de preuves — Niveau 1

## 5.1. Preuve A : interfaces de R2

Commande :

```text
R2# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     10.0.12.2       YES manual up                    up
GigabitEthernet0/1     10.0.23.1       YES manual up                    up
Loopback0              2.2.2.2         YES manual up                    up
```

**Question A :** qu'apprenez-vous de cette sortie ? Que ne pouvez-vous pas conclure ?

## 5.2. Preuve B : table des voisins de R2

```text
R2# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address       Interface
1.1.1.1           1   FULL/-          00:00:34    10.0.12.1     Gi0/0
```

R2 ne présente aucune entrée pour R3.

**Question B :** quelle hypothèse gagne en priorité lorsque l'interface est `up/up`, mais qu'aucun voisin OSPF n'apparaît ? Donnez au moins trois causes possibles à vérifier.

## 5.3. Preuve C : connectivité du lien de transit

```text
R2# ping 10.0.23.2
!!!!!
Success rate is 100 percent (5/5)
```

**Question C :** ce résultat élimine-t-il toutes les causes de panne OSPF ? Expliquez.

## 5.4. Décision du joueur

Avant de continuer, notez vos commandes suivantes et l'objectif de chacune :

```text
1. ______________________________________________
2. ______________________________________________
3. ______________________________________________
```

Il faut privilégier une séquence courte, probante et non destructive : configuration et état OSPF, interface concernée, paramètres du voisin, puis seulement des outils de diagnostic plus détaillés si les premières preuves ne suffisent pas.


# 6. Dossier de preuves — Niveau 2

## 6.1. Preuve D : état OSPF global de R3

```text
R3# show ip ospf
 Routing Process "ospf 10" with ID 3.3.3.3
 Supports only single TOS(TOS0) routes
 This process is not an autonomous system boundary router
 Number of areas in this router is 1. 1 normal 0 stub 0 nssa
 External flood list length 0
```

OSPF est présent sur R3. Cette sortie ne prouve toutefois pas que le protocole envoie des Hello sur l'interface du transit.

## 6.2. Preuve E : état OSPF sur le lien de R3

```text
R3# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.0.23.2/30, Area 0
  Process ID 10, Router ID 3.3.3.3, Network Type POINT_TO_POINT
  Cost: 10
  No Hellos (Passive interface)
```

**Question E :** quelle ligne est déterminante ? Quel mécanisme peut expliquer à la fois l'interface IP active et l'absence de voisin OSPF ?

## 6.3. Preuve F : configuration OSPF de R3

```text
R3# show running-config | section router ospf
router ospf 10
 router-id 3.3.3.3
 passive-interface default
 no passive-interface GigabitEthernet0/1
 network 10.0.23.0 0.0.0.3 area 0
 network 192.168.30.0 0.0.0.255 area 0
```

**Attention :** `GigabitEthernet0/1` est le LAN `192.168.30.0/24`, alors que le lien vers R2 est `GigabitEthernet0/0` (`10.0.23.2/30`). La configuration a bien rendu le LAN non passif et a laissé l'interface de transit passive par défaut.

**Question F :** identifiez précisément la faute. Quelle modification minimale permettrait de restaurer le voisinage sans rendre les interfaces LAN inutilement bavardes en OSPF ?


# 7. Feuille de diagnostic à remplir

Complétez le tableau avant de consulter le corrigé.

| Question | Votre conclusion | Preuve attendue |
|---|---|---|
| L'interface de transit est-elle active au niveau IP ? |  |  |
| R2 reçoit-il actuellement un voisin OSPF R3 ? |  |  |
| Un ping IP réussi prouve-t-il que les Hello OSPF sont envoyés ? |  |  |
| OSPF est-il lancé sur R3 ? |  |  |
| L'interface de transit envoie-t-elle des Hello ? |  |  |
| Quelle commande a rendu les interfaces passives par défaut ? |  |  |
| Quelle interface doit être explicitement non passive ? |  |  |
| Pourquoi le LAN doit-il rester passif ? |  |  |


# 8. Procédure professionnelle de dépannage OSPF

## 8.1. Étape 1 — confirmer le périmètre

Avant de modifier quoi que ce soit, identifiez :

- quels préfixes sont affectés ;
- depuis quelles sources et vers quelles destinations ;
- si la panne est permanente ou intermittente ;
- si elle concerne un seul voisin ou plusieurs ;
- si le problème touche le plan de contrôle (OSPF) ou le plan de données (transfert des paquets) ;
- si un changement récent est identifié dans les journaux ou les outils de gestion.

Ne confondez pas « application indisponible », « route absente », « voisinage OSPF incomplet » et « lien physique coupé ». Ces symptômes peuvent être liés, mais ils ne sont pas équivalents.

## 8.2. Étape 2 — vérifier la couche IP

Sur Cisco IOS/IOS XE :

```text
show ip interface brief
show interfaces GigabitEthernet0/0
show ip interface GigabitEthernet0/0
show ip route connected
ping 10.0.23.1
ping 10.0.23.2
```

Les adresses doivent être cohérentes avec `10.0.23.0/30` :

```text
10.0.23.0/30
|
+-- 10.0.23.0 : identifiant de réseau
+-- 10.0.23.1 : adresse de R2
+-- 10.0.23.2 : adresse de R3
+-- 10.0.23.3 : diffusion IPv4 traditionnelle
```

Le ping teste la connectivité ICMP unicast. Pour des causes OSPF, il faut également examiner le traitement de l'IP protocol 89 et du multicast, ainsi que l'état des interfaces et la configuration OSPF.

## 8.3. Étape 3 — examiner le voisinage OSPF

```text
show ip ospf neighbor
show ip ospf interface GigabitEthernet0/0
show ip ospf interface brief
show ip protocols
show running-config | section router ospf
```

Recherchez des signes discriminants :

- aucune entrée de voisin ;
- voisin en `Init` ;
- voisin bloqué en `ExStart` ou `Exchange` ;
- interface passive ;
- mauvais Router ID ;
- mauvaise aire ;
- Hello/Dead timers divergents ;
- type de réseau différent ;
- authentification incohérente ;
- MTU incompatible.

## 8.4. Étape 4 — contrôler les messages et les filtres

Si le problème reste inexpliqué :

- contrôler les ACL entrantes/sortantes sur les équipements concernés ;
- vérifier les pare-feu ou politiques de sécurité entre les interfaces ;
- examiner les compteurs d'erreurs et pertes de paquets ;
- utiliser une capture de paquets si le matériel et le contexte le permettent ;
- utiliser le débogage OSPF uniquement selon les procédures de l'organisation, car un débogage intensif peut consommer des ressources.

Sur certains environnements Cisco, des commandes de débogage d'adjacence OSPF existent, mais leur syntaxe dépend de la plateforme/version. En production, utilisez des diagnostics ciblés, surveillez le CPU, puis désactivez le débogage dès que les informations nécessaires sont recueillies.

## 8.5. Étape 5 — si le voisin est FULL mais la route manque

Suivez cette chaîne de preuve :

```text
Préfixe connecté sur le routeur d'origine ?
            |
            v
Préfixe activé dans OSPF, éventuellement sur une interface passive ?
            |
            v
LSA attendue présente dans la LSDB ?
            |
            v
Route calculée dans la table OSPF ?
            |
            v
Route installée dans la RIB globale/VRF ?
            |
            v
Route de retour présente et flux autorisé ?
```

Une interface passive arrête l'émission des Hello sur l'interface, tout en permettant généralement l'annonce du réseau correspondant par OSPF si cette interface est bien incluse dans le processus. Il est donc utile de distinguer la passivité d'un LAN (souvent souhaitable) de celle d'un lien de transit entre routeurs (souvent une erreur si une adjacence est attendue).


# 9. Correction de l'incident

## 9.1. Cause racine

La cause est une erreur de configuration sur R3 :

```text
passive-interface default
no passive-interface GigabitEthernet0/1
```

Le premier ordre rend passives les interfaces OSPF par défaut. La deuxième ligne rend active l'interface G0/1, qui correspond en réalité au LAN `192.168.30.0/24`. L'interface de transit G0/0 vers R2 reste passive. OSPF ne transmet donc pas de Hello sur le lien où une adjacence est nécessaire.

La connectivité IP du lien reste opérationnelle car l'adresse IP et l'état du lien ne sont pas la cause du défaut. Ce comportement explique pourquoi le ping peut réussir alors que le voisinage OSPF ne se forme pas.

## 9.2. Correction minimale sur Cisco IOS/IOS XE

**Préconditions :** confirmer que l'interface vers R2 est bien `GigabitEthernet0/0`, sauvegarder la configuration et respecter la procédure de changement. Dans le laboratoire, la correction est :

```text
R3# configure terminal
R3(config)# router ospf 10
R3(config-router)# no passive-interface GigabitEthernet0/0
R3(config-router)# end
```

Ne supprimez pas `passive-interface default` par facilité. La stratégie consistant à rendre les interfaces passives par défaut puis à réactiver explicitement les liens de routage évite d'envoyer des Hello OSPF sur des segments utilisateurs où aucun voisinage n'est souhaité.

## 9.3. Vérification immédiate

```text
R3# show ip ospf interface GigabitEthernet0/0
R3# show ip ospf neighbor
R2# show ip ospf neighbor
```

Résultat attendu : R2 et R3 deviennent voisins et atteignent `FULL` sur ce lien point-à-point.

## 9.4. Vérifier l'annonce du LAN distant

Sur R3 :

```text
R3# show ip route connected
R3# show ip ospf database router
```

Sur R2 :

```text
R2# show ip route ospf
R2# show ip route 192.168.30.0
```

Sur R1 :

```text
R1# show ip route 192.168.30.0
R1# show ip route ospf
```

Résultat attendu : le préfixe `192.168.30.0/24` est appris par OSPF depuis R3 et installé sur les routeurs en amont, sauf politique, préférence de route ou autre facteur indépendant qui l'en empêcherait.

## 9.5. Tests de trafic de bout en bout

Utilisez les outils de test disponibles sur le laboratoire :

1. depuis R1, tester `10.0.23.2` ou la destination LAN selon les routes et fonctionnalités de ping disponibles ;
2. tester un hôte réel de `192.168.30.0/24` si présent ;
3. tester aussi le sens retour depuis le LAN distant ;
4. vérifier les routes et éventuels filtres ;
5. confirmer que les services applicatifs répondent et pas uniquement ICMP.

Un ping réussi vers l'adresse d'interface R3 ne prouve pas que l'application du site fonctionne. Le test final doit porter sur la destination et le protocole réels lorsqu'ils sont disponibles.


# 10. Faux correctifs à refuser

## 10.1. Ajouter une route statique vers le LAN distant

Une route statique pourrait rendre le préfixe temporairement joignable, mais elle ne réparerait pas l'absence d'adjacence. Elle peut masquer l'incident et créer une divergence entre le plan de contrôle dynamique et le plan de transfert.

Une route statique n'est pertinente que si elle fait partie d'une conception volontaire, documentée et testée — pas comme substitut automatique à un diagnostic OSPF.

## 10.2. Redémarrer R3 sans preuve

Le redémarrage peut interrompre d'autres services et peut même faire disparaître temporairement les symptômes avant qu'ils ne réapparaissent. Il ne corrige pas une configuration passive incorrecte qui sera relue au démarrage.

## 10.3. Rendre toutes les interfaces non passives

Cette action pourrait rétablir le lien de transit, mais elle augmente inutilement le périmètre de changement. Le LAN utilisateur ne doit pas devenir une zone d'envoi de Hello par simple commodité.

## 10.4. Changer les timers, l'aire ou l'authentification sans preuve

Les symptômes présentés pointent vers l'émission de Hello sur une interface passive. Modifier plusieurs paramètres simultanément réduit la clarté du diagnostic et peut introduire de nouveaux défauts.

## 10.5. Ignorer la route de retour

La présence d'une route à l'aller ne suffit pas. Le chemin retour, les filtres, la passerelle du poste et les politiques applicatives doivent également être vérifiés.


# 11. Laboratoire guidé — reproduire le défaut

> Réalisez cette manipulation uniquement dans un laboratoire isolé, par exemple avec des routeurs virtuels compatibles, des conteneurs FRR ou un simulateur réseau. Les commandes Cisco ne sont pas directement interchangeables avec celles de FRR ou d'autres systèmes.

## 11.1. Configuration de référence — R1

Exemple de configuration Cisco IOS conceptuelle :

```text
hostname R1
!
interface GigabitEthernet0/0
 description TRANSIT-VERS-R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description LAN-SIEGE
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 1.1.1.1
 network 10.0.12.0 0.0.0.3 area 0
 network 192.168.10.0 0.0.0.255 area 0
 passive-interface GigabitEthernet0/1
```

## 11.2. Configuration de référence — R2

```text
hostname R2
!
interface GigabitEthernet0/0
 description TRANSIT-VERS-R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description TRANSIT-VERS-R3
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
router ospf 10
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
```

## 11.3. Configuration de R3 avec l'incident volontaire

```text
hostname R3
!
interface GigabitEthernet0/0
 description TRANSIT-VERS-R2
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description LAN-SITE-DISTANT
 ip address 192.168.30.1 255.255.255.0
 no shutdown
!
router ospf 10
 router-id 3.3.3.3
 passive-interface default
 no passive-interface GigabitEthernet0/1
 network 10.0.23.0 0.0.0.3 area 0
 network 192.168.30.0 0.0.0.255 area 0
```

La faute est volontaire. Avant correction, le lien de transit n'envoie pas les Hello attendus.

## 11.4. Procédure de reproduction

1. Appliquez les configurations dans le laboratoire.
2. Vérifiez `show ip interface brief` sur les trois routeurs.
3. Vérifiez le voisinage OSPF depuis R2 et R3.
4. Comparez le résultat du ping avec l'état OSPF.
5. Affichez les interfaces OSPF de R3.
6. Identifiez la relation entre `passive-interface default` et `no passive-interface`.
7. Corrigez uniquement l'interface de transit.
8. Vérifiez le voisinage, la route et le trafic de bout en bout.

## 11.5. Configuration cible de R3

```text
router ospf 10
 router-id 3.3.3.3
 passive-interface default
 no passive-interface GigabitEthernet0/0
 network 10.0.23.0 0.0.0.3 area 0
 network 192.168.30.0 0.0.0.255 area 0
```

L'interface LAN demeure passive implicitement grâce à `passive-interface default` ; elle reste néanmoins annoncée dans OSPF car son réseau est inclus dans le processus.


# 12. Extension de diagnostic — si la première correction ne suffit pas

Dans un incident réel, plusieurs défauts peuvent coexister. Ne supposez pas que toute panne sera aussi simple que celle de ce scénario.

## 12.1. Aucun voisin après correction

Vérifiez dans cet ordre :

1. la bonne interface et le bon câblage logique ;
2. les adresses IP et les masques ;
3. l'activation OSPF sur les deux interfaces de transit ;
4. la configuration passive des deux côtés ;
5. l'area ID et le type d'aire ;
6. les Hello/Dead timers ;
7. l'authentification ;
8. le type de réseau OSPF ;
9. le filtrage de l'IP protocol 89 et des multicast nécessaires ;
10. les journaux, compteurs d'erreurs et captures de paquets.

## 12.2. Voisin en Init

`Init` suggère que des Hello sont reçus mais que la communication bidirectionnelle n'est pas confirmée. Vérifiez le sens retour des Hello, les ACL et la présence du Router ID local dans les Hello reçus.

## 12.3. Voisin bloqué en ExStart/Exchange

Vérifiez l'MTU, les paramètres d'interface, le Router ID et les échanges DBD. Ne désactivez pas le contrôle MTU comme premier réflexe : corriger l'incohérence est généralement préférable à contourner le garde-fou.

## 12.4. Voisin Full, préfixe absent

Contrôlez la connectivité du réseau d'origine, les instructions `network`, les interfaces passives, la LSDB, les politiques de filtrage, la table de routage et les routes concurrentes. Un voisinage sain ne garantit pas que chaque préfixe attendu est correctement annoncé.

## 12.5. Routes intermittentes

Examinez les changements d'état des interfaces, les compteurs d'erreurs, la stabilité de l'alimentation et du support, la perte de paquets, la charge CPU, les événements de routage et les modifications de configuration. Comparez l'heure des flaps avec celle des pertes de service.


# 13. Correspondance FRRouting (FRR)

Sur FRR, les commandes de consultation courantes comprennent :

```text
show ip ospf
show ip ospf interface
show ip ospf neighbor
show ip ospf database
show ip route ospf
```

La configuration de passivité dépend de la version et de la structure de configuration du démon `ospfd`. Dans de nombreux environnements FRR, on configure l'interface OSPF passive ou l'interface à exclure de la passivité à partir du contexte OSPF approprié. Consultez la documentation de la version installée avant de copier la syntaxe de configuration.

**À retenir :** les commandes de diagnostic sont conceptuellement similaires d'une plateforme à l'autre ; la syntaxe et certains comportements peuvent différer.


# 14. Exercice d'analyse de sorties

## Exercice 1 — « Lien actif, voisin absent »

Sortie :

```text
R3# show ip interface brief
GigabitEthernet0/0  10.0.23.2  YES manual  up  up

R3# show ip ospf interface GigabitEthernet0/0
No Hellos (Passive interface)
```

**Questions :**

1. Quelle couche est opérationnelle ?
2. Quelle couche pose problème ?
3. Quelle commande de configuration vérifiez-vous ?
4. Quelle correction minimale proposez-vous ?

### Correction

L'interface physique et logique est opérationnelle. Le problème concerne le fonctionnement OSPF sur cette interface : elle est passive et n'envoie pas les Hello requis. Vérifiez `passive-interface default` et les exceptions `no passive-interface`. Si G0/0 relie R3 à R2 et doit former une adjacence, rendez explicitement G0/0 non passive.

## Exercice 2 — « Voisin FULL, route absente »

R2 affiche R3 en `FULL`, mais `192.168.30.0/24` n'est pas dans sa table de routage.

**Questions :**

1. Pourquoi ne faut-il pas corriger automatiquement le voisinage ?
2. Quels éléments examiner sur R3 ?
3. Que vérifier sur R2 avant de conclure à un défaut d'annonce ?

### Correction

Le voisinage fonctionne, donc le diagnostic doit porter sur l'annonce du préfixe et son installation. Sur R3, vérifier la route connectée vers `192.168.30.0/24`, son inclusion dans OSPF et la LSDB. Sur R2, contrôler les LSAs, les routes calculées, la RIB, les politiques et les routes concurrentes.

## Exercice 3 — « Ping réussi, application inaccessible »

Le ping vers `10.0.23.2` fonctionne, mais l'application du site distant n'est pas joignable.

**Questions :**

1. Le ping valide-t-il le chemin applicatif ?
2. Quels contrôles suivent le test ICMP ?
3. Quel rôle joue la route de retour ?

### Correction

Le ping confirme seulement qu'un test ICMP a réussi entre les points testés. Il faut vérifier la route vers l'hôte applicatif, le port et le protocole de l'application, les filtres, la passerelle de l'hôte, les journaux du service et le chemin retour.

## Exercice 4 — « Reste bloqué en ExStart »

Deux routeurs détectent un voisin, mais l'adjacence n'atteint pas `FULL`.

**Questions :**

1. Quelle catégorie de paquet est impliquée dans l'étape ExStart/Exchange ?
2. Quelle incohérence classique peut empêcher la progression ?
3. Pourquoi ne pas appliquer immédiatement une commande de contournement ?

### Correction

Cette phase implique les paquets Database Description (DBD). Une incohérence de MTU est une cause classique, parmi d'autres. Il faut comparer les configurations et les caractéristiques d'interface, puis corriger la cause plutôt que désactiver le contrôle sans justification.


# 15. Challenge final — Incident « Routeur muet »

**Barème : 100 points**  
**Durée recommandée :** 45 à 60 minutes  
**Mode :** sans consulter la solution détaillée de la section 16 avant d'avoir rédigé votre diagnostic.

## 15.1. Scénario

Le support applicatif signale que le siège ne peut plus joindre le service hébergé dans `192.168.30.0/24`. Le routeur R3 répond à une session d'administration existante. Les utilisateurs du LAN siège `192.168.10.0/24` accèdent toujours à leurs services locaux.

La topologie et le plan d'adressage sont ceux de la section 2. Les trois routeurs exécutent OSPFv2 dans l'aire 0.

## 15.2. Éléments remis au joueur

**Sortie 1 — R2 :**

```text
R2# show ip ospf neighbor
Neighbor ID     State        Address       Interface
1.1.1.1         FULL/-       10.0.12.1     GigabitEthernet0/0
```

**Sortie 2 — R3 :**

```text
R3# show ip interface brief
Interface              IP-Address      Status     Protocol
GigabitEthernet0/0     10.0.23.2       up         up
GigabitEthernet0/1     192.168.30.1    up         up
```

**Sortie 3 — R2 :**

```text
R2# ping 10.0.23.2
!!!!!
Success rate is 100 percent (5/5)
```

**Sortie 4 — R3 :**

```text
R3# show running-config | section router ospf
router ospf 10
 router-id 3.3.3.3
 passive-interface default
 no passive-interface GigabitEthernet0/1
 network 10.0.23.0 0.0.0.3 area 0
 network 192.168.30.0 0.0.0.255 area 0
```

**Sortie 5 — R3 :**

```text
R3# show ip ospf interface GigabitEthernet0/0
GigabitEthernet0/0 is up, line protocol is up
  Internet Address 10.0.23.2/30, Area 0
  No Hellos (Passive interface)
```

## 15.3. Tâches du challenge

**Mission A — Tri des faits (15 points)**  
Distinguez les faits établis, les hypothèses et les éléments encore inconnus.

**Mission B — Diagnostic (20 points)**  
Expliquez pourquoi le ping et l'état `up/up` ne contredisent pas le défaut OSPF.

**Mission C — Cause racine (20 points)**  
Identifiez la ligne de configuration à l'origine de la situation et expliquez pourquoi l'exception passive existante ne concerne pas la bonne interface.

**Mission D — Plan de correction (15 points)**  
Présentez les commandes de correction minimales, les préconditions et le plan de retour arrière.

**Mission E — Validation (20 points)**  
Écrivez les commandes et résultats attendus pour prouver le rétablissement du voisinage, de la route et de la communication de bout en bout.

**Mission F — Prévention (10 points)**  
Proposez au moins trois actions pour éviter la répétition de l'incident.

## 15.4. Conditions de réussite

Le challenge est validé si le joueur :

- ne redémarre pas les équipements à l'aveugle ;
- n'ajoute pas de route statique pour masquer le défaut ;
- trouve la preuve de passivité sur l'interface de transit ;
- corrige uniquement l'interface nécessaire ;
- conserve l'interface LAN passive ;
- vérifie le voisinage, l'annonce du préfixe et le trafic réel ;
- consigne la preuve et les mesures préventives.


# 16. Solution détaillée et débriefing

> Cette section est destinée à la correction du challenge. Lors d'une session en équipe, le facilitateur peut la garder cachée jusqu'à la remise du diagnostic.

## 16.1. Mission A — tri des faits

**Faits établis :**

- G0/0 de R3 est `up/up` avec l'adresse `10.0.23.2`.
- R2 peut joindre cette adresse par ICMP dans le test fourni.
- R2 n'a aucune entrée OSPF pour R3.
- La configuration OSPF de R3 contient `passive-interface default`.
- R3 rend non passive G0/1, mais G0/1 est le LAN et non le lien de transit.
- La sortie de `show ip ospf interface G0/0` indique `No Hellos (Passive interface)`.

**Hypothèse confirmée par preuve :** G0/0 est passive et n'envoie donc pas de Hello OSPF.

**Éléments à vérifier après correction :** état `FULL`, présence de la route vers `192.168.30.0/24`, connectivité applicative et chemin retour.

## 16.2. Mission B — pourquoi ping et OSPF peuvent diverger

ICMP et OSPF sont deux protocoles distincts. Le ping unicast peut fonctionner lorsque les interfaces et le routage local permettent l'échange ICMP, alors qu'OSPF n'envoie aucun Hello sur une interface passive. La réussite d'un ping n'est donc pas une preuve du bon fonctionnement de la découverte de voisins OSPF.

Une interface `up/up` établit une indication sur l'état du lien et du protocole de ligne ; elle ne valide pas l'état du protocole de routage dynamique.

## 16.3. Mission C — cause racine

La configuration :

```text
passive-interface default
no passive-interface GigabitEthernet0/1
```

rend toutes les interfaces passives par défaut, puis rend G0/1 non passive. Or le lien de transit vers R2 se trouve sur G0/0. L'exception est appliquée à la mauvaise interface.

La sortie `No Hellos (Passive interface)` confirme directement le mécanisme.

## 16.4. Mission D — correction et retour arrière

**Avant le changement :**

- confirmer que G0/0 est bien l'interface de transit vers R2 ;
- sauvegarder la configuration ;
- recueillir le voisinage, les routes et l'état des interfaces ;
- annoncer le changement si le réseau est en production.

**Correction minimale :**

```text
R3# configure terminal
R3(config)# router ospf 10
R3(config-router)# no passive-interface GigabitEthernet0/0
R3(config-router)# end
```

**Pourquoi cette correction ?** Elle autorise l'émission/réception des Hello nécessaires sur le lien de routage tout en préservant la stratégie de passivité par défaut.

**Retour arrière :** dans ce scénario, si le changement crée un effet inattendu, rétablir l'état antérieur de l'interface de transit avec :

```text
R3# configure terminal
R3(config)# router ospf 10
R3(config-router)# passive-interface GigabitEthernet0/0
R3(config-router)# end
```

Ce retour arrière remettrait cependant l'incident initial en place. Il ne doit être utilisé qu'en cas de nécessité opérationnelle après évaluation de l'impact, en attendant une correction sûre.

## 16.5. Mission E — validation attendue

**Sur R3 :**

```text
show ip ospf interface GigabitEthernet0/0
show ip ospf neighbor
show ip route connected
show ip ospf database router
```

**Sur R2 :**

```text
show ip ospf neighbor
show ip route 192.168.30.0
show ip route ospf
```

**Sur R1 :**

```text
show ip route 192.168.30.0
show ip route ospf
```

**Résultats attendus :**

- R2 et R3 se découvrent et atteignent `FULL` sur le lien point-à-point ;
- l'interface G0/0 de R3 n'affiche plus `No Hellos (Passive interface)` ;
- `192.168.30.0/24` est annoncée et installée dans la table de routage des routeurs en amont, en l'absence de politique ou de route concurrente qui l'empêcherait ;
- un test depuis le siège vers une destination réelle du LAN distant fonctionne, ainsi que le test retour ;
- l'application répond sur le protocole et le port attendus.

Il ne faut pas inventer un résultat de ping vers un hôte qui n'existe pas dans le laboratoire. Si aucun hôte n'est installé dans `192.168.30.0/24`, documentez la validation de routage et indiquez que le test applicatif reste à effectuer lorsqu'une destination de test sera disponible.

## 16.6. Mission F — prévention

Mesures possibles :

1. standardiser la configuration OSPF avec `passive-interface default` et une liste explicite des interfaces de transit ;
2. documenter le nom, le rôle et l'adresse de chaque interface ;
3. intégrer une vérification de voisinage et de route à chaque changement de routage ;
4. surveiller le nombre de voisins OSPF attendus et les changements d'état ;
5. conserver les configurations précédentes et les tickets de changement ;
6. utiliser des modèles de configuration contrôlés et une revue par un pair ;
7. tester le chemin applicatif complet, pas seulement un ping de transit ;
8. maintenir une documentation du plan d'adressage et des Router IDs.


# 17. Barème détaillé du challenge

| Critère | Points | Pour obtenir tous les points |
|---|---:|---|
| Tri des faits | 15 | Faits, hypothèses et inconnues correctement séparés |
| Diagnostic | 20 | Différence entre connectivité IP et état OSPF expliquée |
| Cause racine | 20 | Interface de transit passive et exception sur mauvaise interface identifiées |
| Correction | 15 | Changement minimal, préconditions et retour arrière décrits |
| Validation | 20 | Voisinage, préfixe, route et trafic de bout en bout vérifiés |
| Prévention | 10 | Trois mesures pertinentes ou davantage |
| **Total** | **100** | **Incident résolu et preuves documentées** |

### Interprétation du score

- **90–100 :** excellente investigation, corrections minimales et validation solide.
- **75–89 :** diagnostic correct, mais une preuve ou une mesure préventive manque.
- **60–74 :** cause probablement trouvée, vérifications incomplètes.
- **Moins de 60 :** revoir la différence entre interface, connectivité IP, voisinage OSPF et annonce de préfixes.


# 18. Modèle de compte rendu d'incident

Copiez ce modèle dans votre système de tickets si nécessaire ; il fait partie du présent support pédagogique.

```text
INCIDENT : INC-OSPF-042 — Routeur muet

Impact : le préfixe 192.168.30.0/24 n'était plus appris depuis le siège.
Détection : absence du voisin OSPF R3 sur R2 et absence de route vers le LAN distant.

Faits observés :
- interfaces de transit up/up ;
- ping IP de transit réussi ;
- absence de voisin R3 dans la table OSPF de R2 ;
- G0/0 de R3 affichée comme interface OSPF passive ;
- passive-interface default configuré ;
- exception no passive-interface définie sur G0/1 au lieu de G0/0.

Cause racine : mauvais choix d'interface dans l'exception de passivité OSPF.

Correction : no passive-interface GigabitEthernet0/0 sous router ospf 10.

Validations :
- voisinage OSPF en FULL ;
- route 192.168.30.0/24 présente dans les tables attendues ;
- connectivité aller/retour testée vers un hôte réel ;
- service applicatif vérifié sur son port réel.

Prévention : revue des interfaces OSPF, contrôle des voisins attendus,
validation des routes après changement, surveillance de la stabilité du voisinage.
```


# 19. Checklist de fin de mission

- [ ] Le périmètre métier de l'incident est documenté.
- [ ] Les interfaces et les adresses IP ont été vérifiées.
- [ ] Les voisins OSPF et leurs états ont été contrôlés.
- [ ] Les interfaces passives et actives ont été comparées au plan réseau.
- [ ] La cause racine est prouvée par une sortie de commande.
- [ ] Une correction minimale a été appliquée.
- [ ] Les tables de routage ont été vérifiées sur plusieurs routeurs.
- [ ] Le trafic aller et retour a été testé.
- [ ] Les commandes et résultats ont été ajoutés au ticket.
- [ ] Le plan de retour arrière et les mesures préventives sont documentés.


# 20. Références techniques

1. **RFC 2328 — OSPF Version 2**, spécification du protocole : https://www.rfc-editor.org/rfc/rfc2328.html
2. **Cisco — Troubleshoot OSPF Neighbor Problems**, états d'adjacence et causes fréquentes : https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/13699-29.html
3. **Cisco — Troubleshoot Common Problems with OSPF** : https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/12151-trouble-main.html
4. **FRRouting — OSPF user documentation**, commandes de consultation et de dépannage : https://docs.frrouting.org/en/latest/ospfd.html

Les commandes de configuration et les sorties de ce laboratoire sont illustratives et orientées Cisco IOS/IOS XE. Vérifiez la documentation de la version et de la plateforme réellement utilisées avant toute intervention sur un réseau en production.


# Fin du fichier `incident-ospf.md`

**Objectif pédagogique atteint :** l'apprenant a suivi une investigation fondée sur des preuves, distingué une panne IP d'une panne de protocole de routage, identifié une erreur de passivité OSPF, appliqué une correction ciblée, validé les routes et le trafic, puis documenté des mesures de prévention.
