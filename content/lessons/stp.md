# Spanning Tree Protocol — Boucles, élection et protection (CCNA / Admin Réseau)

> **Objectif** : maîtriser STP sous toutes ses formes (802.1D, PVST+, RSTP, MSTP), comprendre l'élection du root bridge, les rôles et états de ports, les BPDU, les timers, les mécanismes de convergence rapide et les protections de bordure. Le cours insiste sur le diagnostic réel : boucle L2, root bridge indésirable, port err-disabled, incohérence de VLAN, etc.

---

## 1. Le problème : une boucle de niveau 2

Une trame Ethernet n'a pas de **TTL**. Si une trame de diffusion rencontre une boucle physique, elle tourne indéfiniment. En quelques secondes, le réseau est saturé.

```text
        SW1 -------- SW2
         |             |
         |             |
        SW3 -------- SW4

Une broadcast partie de SW1 revient par SW1, repart, etc.
```

Conséquences :

- **broadcast storm** : la bande passante est consommée par les diffusions ;
- **instabilité de la table MAC** : une même MAC apparaît sur plusieurs ports, le switch « flappe » ;
- **CPU élevé** sur les switches et les postes ;
- **perte totale de connectivité** ;
- **duplication de trames** pour certains flux.

STP casse les boucles **logiquement** en bloquant certains ports. La redondance physique reste disponible : si un lien tombe, STP recalcule et active un port de secours.

---

## 2. Les variantes de STP

| Variante | Norme | Instance | Convergence | Usage |
|---|---|---|---|---|
| STP classique | 802.1D | Une par réseau | 30–50 s | Historique |
| PVST+ | Cisco | Une par VLAN | 30–50 s | Ancien Cisco |
| Rapid PVST+ | Cisco | Une par VLAN | 1–3 s | Très courant |
| RSTP | 802.1w | Une par réseau | 1–3 s | Standard |
| MSTP | 802.1s | Plusieurs VLAN par instance | 1–3 s | Grands réseaux |
| MSTP Cisco | 802.1s | Instances + mapping VLAN | 1–3 s | Campus |

**PVST+** fait tourner une instance par VLAN. **MSTP** regroupe les VLANs en instances pour réduire le nombre d'arbres et la charge CPU.

---

## 3. BPDU et élection du root bridge

### 3.1 Contenu d'un BPDU

Un **BPDU** (Bridge Protocol Data Unit) est envoyé toutes les **2 secondes** par le root bridge et relayé par les autres switches. Il contient notamment :

- **Bridge ID** : priorité (2 octets) + MAC (6 octets) ;
- **Root ID** : bridge ID du root vu par l'émetteur ;
- **Root Path Cost** : coût cumulé vers le root ;
- **Port ID** : priorité de port + numéro ;
- **Timers** : hello, forward delay, max age ;
- **Flags** : topology change, proposal/agreement en RSTP.

### 3.2 Élection

Tous les switches s'accordent sur un **root bridge** :

1. plus faible **priorité** de bridge ;
2. si égalité, plus faible **MAC**.

Ensuite, chaque switch choisit son **root port** : le port avec le plus faible coût vers le root. En cas d'égalité : plus faible bridge ID voisin, puis plus faible port ID voisin.

```text
Priorités :
SW1 : 32768.0011.1111.1111
SW2 : 32768.0022.2222.2222
SW3 : 32768.0033.3333.3333

Root = SW1 (MAC la plus faible).
SW2 root port = lien vers SW1 (coût 4 en 1G).
SW3 root port = lien vers SW1 ou SW2 selon le coût.
```

### 3.3 Coûts de chemin (802.1D)

| Débit | Coût 802.1D | Coût long (RSTP/MSTP) |
|---|---:|---:|
| 10 Mbit/s | 100 | 2 000 000 |
| 100 Mbit/s | 19 | 200 000 |
| 1 Gbit/s | 4 | 20 000 |
| 10 Gbit/s | 2 | 2 000 |
| 100 Gbit/s | — | 200 |

Le coût est **cumulé** le long du chemin. Un lien 10G peut être moins coûteux qu'un chemin de deux liens 1G, selon les valeurs.

---

## 4. Rôles et états des ports

### 4.1 Rôles 802.1D

| Rôle | Description |
|---|---|
| Root port | Meilleur chemin vers le root |
| Designated port | Port qui transmet vers un segment, un par segment |
| Blocked / non-designated | Port bloqué pour casser la boucle |
| Disabled | Administrativement down |

### 4.2 États 802.1D

| État | Durée | Forwarding | Apprentissage MAC |
|---|---|---|---|
| Blocking | 20 s (max age) | Non | Non |
| Listening | 15 s | Non | Non |
| Learning | 15 s | Non | Oui |
| Forwarding | — | Oui | Oui |
| Disabled | — | Non | Non |

La convergence classique peut prendre **30 à 50 secondes**. C'est souvent trop long pour la voix et les serveurs.

### 4.3 RSTP : rôles et états

RSTP (802.1w) réduit les états à trois : **Discarding**, **Learning**, **Forwarding**. Il ajoute :

- **Alternate port** : chemin de secours vers le root, prêt à prendre le relais ;
- **Backup port** : secours pour un segment desservi par un autre port du même switch ;
- **Edge port** : port connecté à un terminal, passe immédiatement en forwarding ;
- **Proposal/Agreement** : convergence rapide par négociation ;
- **Sync** : propagation des changements.

| Rôle RSTP | État normal | Rôle |
|---|---|---|
| Root | Forwarding | Vers le root |
| Designated | Forwarding | Vers le segment |
| Alternate | Discarding | Secours vers le root |
| Backup | Discarding | Secours local |
| Disabled | Discarding | Administrativement down |

---

## 5. Timers et topologie

| Timer | Valeur par défaut | Rôle |
|---|---:|---|
| Hello | 2 s | Fréquence des BPDU |
| Forward delay | 15 s | Listening/Learning |
| Max age | 20 s | Durée avant de considérer un BPDU perdu |
| Aging | 300 s | Entrées MAC dynamiques |

En RSTP, les timers sont moins déterminants : la convergence repose sur la négociation. Un `hello` de 2 s reste la base.

### 5.1 Changement de topologie

Quand un lien change, STP doit invalider les tables MAC. En 802.1D, le root envoie des **TCN** (Topology Change Notification) et le root propage un flag **TC** dans ses BPDU. Les switches réduisent alors l'âge des entrées MAC pour reconverger.

En RSTP, les changements sont propagés plus vite et les ports edge ne génèrent pas de changement global.

---

## 6. Configuration Cisco

### 6.1 Mode et priorité

```cisco
spanning-tree mode rapid-pvst
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary
spanning-tree vlan 10 priority 4096
```

`root primary` configure une priorité basse (généralement 24576) et `root secondary` une priorité un peu plus haute. Mieux vaut fixer explicitement la priorité pour éviter les surprises.

### 6.2 Ports d'accès

```cisco
interface Gi0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
```

**PortFast** fait passer le port directement en forwarding. Il ne doit être utilisé que sur des ports connectés à des terminaux, jamais vers un switch. **BPDU Guard** désactive le port si un BPDU est reçu, ce qui protège contre un switch pirate ou un câblage accidentel.

### 6.3 Protections

| Protection | Protège contre | Comportement |
|---|---|---|
| PortFast | Convergence lente | Forwarding immédiat |
| BPDU Guard | Switch non autorisé | Err-disable si BPDU |
| BPDU Filter | BPDU parasites | Ignore/filtre les BPDU |
| Root Guard | Root bridge indésirable | Bloque le port si BPDU supérieur |
| Loop Guard | Perte de BPDU sur port bloqué | Passe en loop-inconsistent |
| UDLD | Boucle unidirectionnelle | Désactive le port |

```cisco
interface Gi0/24
 spanning-tree guard root
!
spanning-tree loopguard default
!
interface Gi0/1
 spanning-tree bpduguard enable
```

### 6.4 Vérification

```cisco
show spanning-tree
show spanning-tree vlan 10
show spanning-tree root
show spanning-tree summary
show spanning-tree interface Gi0/1
show spanning-tree inconsistentports
show spanning-tree detail
```

Exemple de sortie :

```text
SW1# show spanning-tree vlan 10

VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    24586
             Address     0011.1111.1111
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    24586  (priority 24576 sys-id-ext 10)
             Address     0011.1111.1111
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------
Gi0/1               Desg FWD 4         128.1    P2p
Gi0/2               Desg FWD 4         128.2    P2p
Gi0/24              Root FWD 4         128.24   P2p
```

---

## 7. RSTP en pratique

RSTP converge en quelques secondes grâce à la négociation **proposal/agreement** :

1. Un switch désigné envoie une **proposal** avec le bit proposal.
2. Le voisin bloque temporairement ses ports non-edge, répond **agreement**.
3. Le port passe en forwarding.
4. Le processus se propage.

```text
SW1 (root) ---- SW2 ---- SW3
1. SW2 reçoit proposal de SW1.
2. SW2 met ses autres ports en sync (Discarding).
3. SW2 répond agreement.
4. SW2 root port passe en forwarding.
5. SW2 envoie proposal à SW3...
```

Un port **edge** ne participe pas à la négociation et passe immédiatement en forwarding. C'est pourquoi PortFast est essentiel sur les postes.

---

## 8. MSTP

MSTP regroupe les VLANs en **instances**. Chaque instance a son propre arbre, mais plusieurs VLANs peuvent partager une instance.

```cisco
spanning-tree mode mst
spanning-tree mst configuration
 name CAMPUS
 revision 1
 instance 1 vlan 10,20
 instance 2 vlan 30,40
 exit
spanning-tree mst 1 root primary
spanning-tree mst 2 root secondary
```

Vérification :

```cisco
show spanning-tree mst configuration
show spanning-tree mst 1
show spanning-tree mst 1 detail
```

**Attention** : le nom, la révision et le mapping doivent être identiques sur tous les switches du domaine MST. Une différence crée des arbres incohérents.

---

## 9. STP sous Linux

Linux peut faire du bridging avec STP via le bridge kernel ou `mstpd`.

### 9.1 Bridge avec STP

```bash
ip link add name br0 type bridge
ip link set br0 type bridge stp_state 1
ip link set br0 type bridge hello_time 200
ip link set eth0 master br0
ip link set eth1 master br0
ip link set br0 up
ip link set eth0 up
ip link set eth1 up
```

Vérification :

```bash
ip -d link show br0
bridge link show
bridge fdb show
cat /sys/class/net/br0/bridge/stp_state
```

### 9.2 mstpd / RSTP

```bash
apt install mstpd
systemctl enable --now mstpd
mstpctl showbridge
mstpctl showport br0
mstpctl showtree br0
```

`mstpd` est plus adapté aux topologies complexes et au RSTP. Pour un simple bridge Linux, le STP kernel suffit souvent.

### 9.3 Diagnostic

```bash
tcpdump -eni eth0 stp
bridge -d link show
ip -s link show eth0
journalctl -u mstpd -f
```

Les BPDU sont des trames multicast `01:80:C2:00:00:00`. Une capture permet de voir le root ID et les timers.

---

## 10. Dépannage STP

### 10.1 Boucle L2

Symptômes : CPU à 100 %, broadcast storm, perte de connectivité, MAC qui flappent.

```cisco
show interfaces | include input rate
show mac address-table | include Dynamic
show spanning-tree inconsistentports
show logging | include SPANTREE
```

Actions : débrancher un lien suspect, vérifier les trunks, vérifier `show spanning-tree` sur tous les switches, rechercher un switch non managé ou un câble en boucle.

### 10.2 Root bridge indésirable

Un switch d'accès avec une priorité basse (ou une MAC faible) devient root. Le trafic traverse des liens lents.

```cisco
show spanning-tree root
show spanning-tree vlan 10
```

Solution : fixer la priorité sur le cœur de réseau et activer **Root Guard** sur les ports d'accès.

```cisco
spanning-tree vlan 10 priority 4096
interface Gi0/1
 spanning-tree guard root
```

### 10.3 Port err-disabled par BPDU Guard

Un poste ou un petit switch envoie des BPDU sur un port PortFast. Le port passe en `err-disabled`.

```cisco
show interfaces status err-disabled
show logging | include BPDU
```

Correction : retirer le switch pirate, corriger le câblage, puis réactiver :

```cisco
interface Gi0/1
 shutdown
 no shutdown
```

### 10.4 Port bloqué en `loop-inconsistent`

Loop Guard a détecté une perte de BPDU sur un port qui devrait en recevoir. Cela indique souvent une boucle unidirectionnelle ou un problème de lien.

```cisco
show spanning-tree inconsistentports
show interfaces status
```

### 10.5 Convergence lente

Vérifier le mode (`show spanning-tree summary`), les timers, la présence de PortFast, et les liens redondants. En 802.1D, 30–50 s est normal ; en RSTP, quelques secondes.

### 10.6 Cas réel : téléphone IP qui perd son VLAN

Un téléphone IP est connecté à un port avec PortFast et BPDU Guard. Le téléphone envoie parfois des BPDU (fonction de switch intégré). Le port est err-disabled. Solution : désactiver BPDU Guard sur ce port ou isoler le téléphone, puis vérifier la documentation du constructeur.

### 10.7 Cas réel : boucle après ajout d'un switch de test

Un technicien branche un switch non configuré sur deux prises du même VLAN. STP devrait bloquer, mais le switch de test a STP désactivé. Le réseau tombe. Leçon : toujours activer STP et BPDU Guard sur les ports d'accès, et documenter les switches non autorisés.

---

## 11. Bonnes pratiques

- Un root bridge stable, choisi explicitement, jamais un switch d'accès.
- RSTP ou MSTP partout, pas de mélange incohérent.
- PortFast + BPDU Guard sur tous les ports terminaux.
- Root Guard sur les ports orientés vers le bas.
- Loop Guard sur les liens trunk critiques.
- UDLD sur les liens fibre.
- Documenter le mapping MST et les priorités.
- Surveiller les changements de topologie (`show spanning-tree detail`, syslog).
- Tester la convergence après chaque changement.

---

## 12. Laboratoire

1. Créer trois switches en triangle, vérifier le root et le port bloqué.
2. Changer la priorité pour déplacer le root, observer la convergence.
3. Activer RSTP et mesurer la convergence après coupure d'un lien.
4. Configurer PortFast + BPDU Guard sur un port et brancher un switch pour provoquer l'err-disable.
5. Configurer MSTP avec deux instances et vérifier la répartition de charge.
6. Sous Linux, monter un bridge STP entre deux namespaces et capturer les BPDU.

---

## 13. Mémo

```cisco
show spanning-tree
show spanning-tree root
show spanning-tree vlan 10
show spanning-tree summary
show spanning-tree inconsistentports
show interfaces status err-disabled
show logging | include SPANTREE
```

```bash
bridge link show
bridge fdb show
ip -d link show br0
tcpdump -eni eth0 stp
mstpctl showbridge
```

---

## 14. Points clés

- STP casse les boucles L2 en bloquant des ports ; sans lui, une boucle provoque une tempête.
- Le root bridge est élu par priorité puis MAC.
- Le root port est le meilleur chemin vers le root ; le designated port transmet vers un segment.
- 802.1D converge lentement ; RSTP converge en quelques secondes.
- PortFast est réservé aux terminaux ; BPDU Guard protège les ports d'accès.
- MSTP regroupe les VLANs en instances ; la configuration doit être identique partout.
- Un problème STP se diagnostique avec `show spanning-tree`, les logs et une capture de BPDU.

> **Exercice** : après l'ajout d'un switch, le réseau devient instable. `show spanning-tree` indique que le nouveau switch est root. Quelle est la cause probable et comment la corriger ? Réponse : priorité par défaut plus faible que le cœur, ou MAC plus faible ; fixer la priorité du cœur et activer Root Guard sur les ports d'accès.

---

## 15. Étude de cas : migration d'un campus vers RSTP

Une entreprise dispose de 30 switches en 802.1D, avec un temps de convergence de 45 secondes après chaque coupure. Les utilisateurs subissent des pertes lors des mises à jour. Objectif : passer en Rapid PVST+ sans coupure.

**Inventaire.** Relever les versions IOS, les modules, les trunks, les VLANs et les priorités STP. Identifier les switches qui ne supportent pas RSTP. Vérifier les liens redondants et les boucles volontaires.

**Plan.** Choisir deux switches de cœur comme root primary et root secondary. Définir les priorités par VLAN. Documenter les ports d'accès qui recevront PortFast et BPDU Guard. Prévoir une fenêtre de maintenance par site.

**Migration.** Commencer par les switches d'accès, puis les distributions, puis le cœur. À chaque étape :

```cisco
spanning-tree mode rapid-pvst
show spanning-tree summary
show spanning-tree root
show spanning-tree vlan 10
```

Vérifier que le root reste le même et que les ports alternate apparaissent. Une modification de mode peut provoquer une convergence ; la faire en fenêtre planifiée.

**Validation.** Couper un lien redondant et mesurer la convergence. Vérifier les logs, les changements de topologie et les tables MAC. Tester la voix et les flux critiques.

**Pièges.** Mélanger des switches en 802.1D et RSTP fonctionne grâce à la compatibilité, mais les gains sont perdus sur les segments concernés. Un switch avec une priorité basse peut devenir root. Un port trunk mal configuré peut créer une boucle pendant la migration.

### 15.1 Check-list

```text
[ ] Mode RSTP activé sur tous les switches
[ ] Root primary/secondary définis
[ ] Priorités documentées
[ ] PortFast sur les ports terminaux
[ ] BPDU Guard activé
[ ] Root Guard sur les ports descendants
[ ] Trunks et VLANs vérifiés
[ ] Convergence mesurée
[ ] Logs surveillés
[ ] Rollback préparé
```

### 15.2 Calcul de convergence

En RSTP, la convergence dépend du nombre de sauts et de la négociation. Un lien direct converge en moins d'une seconde ; un réseau de plusieurs switches peut prendre quelques secondes. Mesurer avec des pings continus et `show spanning-tree detail` pour observer les changements.

```bash
ping -i 0.2 -c 100 10.10.1.1 | ts
```

Sur Cisco, `show spanning-tree detail` indique le nombre de changements de topologie et l'heure du dernier changement. Un compteur qui augmente sans raison est un signal d'alerte.

### 15.3 Que retenir de la migration

- Le root doit être stable et documenté.
- RSTP réduit la convergence, mais ne corrige pas une mauvaise topologie.
- Les protections de bordure sont aussi importantes que le mode.
- Tester la convergence fait partie de la recette.
