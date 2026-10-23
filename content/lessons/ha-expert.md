# Haute Disponibilité Avancée : Split Brain, BFD et vPC

**Niveau :** Administrateur Réseau Senior / Expert

La redondance de base ne suffit pas dans les architectures critiques (Datacenters, Cœurs de réseau). Il faut gérer la détection ultra-rapide (BFD), éviter le "Split Brain" (deux routeurs qui se croient tous les deux actifs), et utiliser des technologies multi-châssis comme MLAG ou vPC.

> **Analogie** : Le Split Brain, c'est comme deux capitaines sur le même navire qui ne s'entendent plus et donnent des ordres contradictoires. Le navire (le réseau) risque de se déchirer. BFD, c'est un sonar ultra-rapide qui détecte l'iceberg avant que le navire ne le touche.

## 1. Le Split Brain

Le Split Brain survient lorsque deux routeurs se croient tous les deux actifs (Master ou Active). Cela peut produire deux réponses ARP pour la même IP virtuelle, causant des coupures aléatoires.
Causes fréquentes : lien de heartbeat (lien de contrôle) coupé, VLAN différent, filtrage multicast, authentification différente.

**Prévention** : Lien de heartbeat redondant, configuration identique, supervision des équipements.

## 2. BFD (Bidirectional Forwarding Detection)

Les timers par défaut de VRRP/HSRP (1 à 3 secondes) sont trop lents pour les applications temps réel. BFD est un protocole qui détecte une panne en **millisecondes** (souvent 50 ms) et prévient immédiatement VRRP/HSRP de basculer.

```cisco
interface GigabitEthernet0/1
 vrrp 10 ip 192.168.10.1
 vrrp 10 bfd fast-detect
3. Le délai de préemption (Preempt Delay)
Après un redémarrage, un routeur peut mettre du temps à reconstruire ses tables de routage. S'il reprend le rôle de Master immédiatement, il risque de router du trafic dans le vide.
Le preempt delay permet d'attendre que le routeur soit stable avant de reprendre la main.

cisco
standby 10 preempt delay minimum 180
4. MLAG et vPC (Multi-Chassis Link Aggregation)
Dans un datacenter, si on utilise LACP (agrégation) avec un seul switch et que ce switch tombe, la redondance est perdue.
MLAG (Multi-Chassis) ou vPC (Cisco) permet à deux switches distincts de présenter une seule agrégation logique au serveur. Le serveur croit parler à un seul switch, mais ses liens aboutissent sur deux équipements physiques différents.

text
              Serveur (dual-homed)
                 /            \
         LACP link 1        LACP link 2
               /                \
        Switch A  ====peer-link====  Switch B
          (vPC/MLAG Domain)
Si le Switch A tombe, le Switch B continue de servir le serveur via son lien LACP.

Les deux switches se synchronisent via un peer-link dédié haute capacité.