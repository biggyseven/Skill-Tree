
# EIGRP – Débutant

**Public :** Techniciens réseau, étudiants en réseaux, administrateurs juniors souhaitant monter en compétence.

**Objectif :** Comprendre EIGRP pas à pas, savoir le configurer sur Cisco IOS, diagnostiquer les problèmes simples, et acquérir les réflexes des niveaux intermédiaires.


## 1. C’est quoi le routage, déjà ?

Avant de parler d’EIGRP, rappelons le décor.

Un **routeur** est un équipement qui relie plusieurs réseaux. Son travail : regarder l’adresse IP de destination d’un paquet, et décider **par quelle interface** l’envoyer pour qu’il arrive à bon port.

Pour prendre cette décision, le routeur consulte sa **table de routage**. Cette table contient des lignes du type :

    Destination         Passerelle         Interface
    10.20.0.0/24        192.168.1.2        Gi0/1
    172.16.0.0/16       192.168.1.3        Gi0/1

Deux façons de remplir cette table :

1. **À la main** (routes statiques) : l’administrateur écrit chaque ligne. Précis, mais ingérable sur un grand réseau.
2. **Automatiquement** (protocoles de routage dynamique) : les routeurs s’échangent leurs informations et construisent la table tout seuls. **EIGRP fait partie de cette famille.**

> **Analogie** : imaginez un réseau de routes entre villes. Les routes statiques, c’est un panneau que vous plantez vous-même à chaque carrefour. EIGRP, c’est un GPS qui discute avec les autres GPS pour connaître les meilleurs itinéraires, et qui se met à jour quand une route est fermée.

---

## 2. EIGRP en trois phrases

- **EIGRP** (Enhanced Interior Gateway Routing Protocol) est un protocole de routage **dynamique** créé par Cisco en 1993.
- Il permet aux routeurs de **s’échanger leurs réseaux** et de **calculer le meilleur chemin** automatiquement.
- Il est réputé pour sa **convergence rapide** : quand un lien tombe, EIGRP retrouve un chemin alternatif en **quelques secondes**, souvent instantanément.

> **Convergence** = le temps que mettent tous les routeurs à être d’accord sur la nouvelle topologie après un changement.

---

## 3. Les notions de base à retenir

### 3.1 Le voisinage

Deux routeurs EIGRP qui se parlent s’appellent des **voisins** (neighbors). Ils s’envoient régulièrement des petits paquets **Hello** pour se dire « je suis toujours là ».

    R1  ──────  Hello !  ──────►  R2
        ◄─────  Hello !  ───────
       
    → Ils deviennent voisins EIGRP.

Si R2 arrête d’envoyer des Hello pendant un certain temps (le **hold-time**), R1 considère que R2 est tombé et retire les routes apprises par lui.

### 3.2 Les réseaux annoncés

Chaque routeur EIGRP **annonce** les réseaux auxquels il est directement connecté. Par exemple, si R1 a une interface dans `10.0.0.0/24`, il dit à ses voisins : « je connais le réseau 10.0.0.0/24, voici ma distance pour y aller ».

### 3.3 La métrique

Pour choisir le **meilleur chemin**, EIGRP calcule une **métrique** : un nombre. **Plus la métrique est petite, meilleur est le chemin.**

Par défaut, EIGRP se base sur deux critères :
- la **bande passante** (un lien rapide est préféré) ;
- le **délai** (un lien moins lent est préféré).

> **Analogie** : pour aller de Paris à Lyon, vous comparez les itinéraires. La métrique, c’est comme un score qui combine la vitesse de la route et le temps de trajet. Le chemin avec le plus petit score gagne.

### 3.4 Le Successor et le Feasible Successor

C’est le cœur d’EIGRP, mais retenez juste l’idée générale pour l’instant :

- **Successor** : le **meilleur chemin**, celui qui est installé dans la table de routage. C’est celui qu’on utilise.
- **Feasible Successor** : un **chemin de secours valide**, déjà connu, qui peut prendre le relais **immédiatement** si le Successor tombe.

> **Analogie** : vous avez un itinéraire habituel pour aller au travail (Successor). Vous en connaissez un autre, un peu plus long mais fiable (Feasible Successor). Si le premier est bloqué, vous prenez le second sans réfléchir. C’est exactement ce que fait EIGRP.

C’est pour cela qu’EIGRP converge vite : **il n’a pas besoin de recalculer**, il a déjà un plan B.

---

## 4. Configurer EIGRP : le minimum vital

### 4.1 La topologie d’exemple

    Réseau 10.0.0.0/24          Réseau 10.0.1.0/24
         |                            |
    ┌────┴────┐                  ┌────┴────┐
    │   R1    │──── 192.168.1.0/30 ───│   R2    │
    │Gi0/0    │                  │Gi0/0    │
    └─────────┘                  └─────────┘

- R1 a l’interface Gi0/0 dans `10.0.0.1/24` et Gi0/1 dans `192.168.1.1/30`.
- R2 a l’interface Gi0/0 dans `192.168.1.2/30` et Gi0/1 dans `10.0.1.1/24`.
- Objectif : que R1 apprenne `10.0.1.0/24` et que R2 apprenne `10.0.0.0/24`.

### 4.2 Configuration sur R1

    R1(config)# router eigrp 100
    R1(config-router)# network 10.0.0.0 0.0.0.255
    R1(config-router)# network 192.168.1.0 0.0.0.3
    R1(config-router)# no auto-summary
    R1(config-router)# exit

### 4.3 Configuration sur R2

    R2(config)# router eigrp 100
    R2(config-router)# network 10.0.1.0 0.0.0.255
    R2(config-router)# network 192.168.1.0 0.0.0.3
    R2(config-router)# no auto-summary
    R2(config-router)# exit

### 4.4 Ce que signifient ces commandes

| Commande | Rôle |
|----------|------|
| `router eigrp 100` | Active le processus EIGRP avec le numéro **100**. Ce numéro doit être **identique** sur tous les routeurs qui doivent devenir voisins. |
| `network 10.0.0.0 0.0.0.255` | Active EIGRP sur les interfaces dont l’IP est dans `10.0.0.0/24`. Le `0.0.0.255` est un **masque wildcard** (l’inverse du masque). |
| `no auto-summary` | Empêche EIGRP de résumer automatiquement les réseaux aux frontières de classe. **Toujours le mettre** dans un réseau moderne. |

> **Astuce** : le wildcard `0.0.0.255` correspond au masque `255.255.255.0`. Règle simple : `wildcard = 255.255.255.255 − masque`.

### 4.5 Vérifier que ça marche

    R1# show ip eigrp neighbors

Résultat attendu :

    IP address      Interface   Hold   Uptime   Q Cnt   SRTT   RTO
    192.168.1.2     Gi0/1       13     00:02:15 0       12     200

Ensuite, vérifiez les routes apprises :

    R1# show ip route eigrp

Résultat attendu :

    D    10.0.1.0/24 [90/281600] via 192.168.1.2, 00:02:15, GigabitEthernet0/1

- **D** = route apprise par EIGRP (D pour DUAL).
- **90** = distance administrative d’EIGRP interne (plus c’est bas, plus la route est crue).
- **281600** = la métrique EIGRP.

> **Et voilà !** R1 sait maintenant joindre `10.0.1.0/24` grâce à EIGRP.

---

## 5. Les erreurs de débutant à éviter

### 5.1 Oublier `no auto-summary`

Sans cette commande, EIGRP peut résumer `10.0.1.0/24` en `10.0.0.0/8` et créer des routes fausses. **Toujours la mettre.**

### 5.2 Mettre un numéro d’AS différent

    R1 : router eigrp 100
    R2 : router eigrp 200

→ **Ils ne deviennent jamais voisins.** Le numéro d’AS doit être **identique** sur tous les routeurs du domaine.

### 5.3 Utiliser `network` avec le mauvais wildcard

    network 10.0.0.0 255.255.255.0   ← FAUX (c'est un masque, pas un wildcard)
    network 10.0.0.0 0.0.0.255       ← BON

### 5.4 Oublier que `network` active l’interface

`network` ne dit pas « annonce ce réseau » comme on pourrait le croire. Il dit : **« active EIGRP sur toutes les interfaces dont l’IP appartient à ce réseau »**. C’est une nuance importante.

### 5.5 Laisser un voisinage se former sur une interface utilisateur

Si vous mettez `network 0.0.0.0 255.255.255.255` (tout), EIGRP essaie de former des voisinages sur **toutes** les interfaces, y compris vers des PC. Utilisez `passive-interface` :

    router eigrp 100
     passive-interface GigabitEthernet0/2

L’interface reste annoncée, mais **aucun Hello** n’est envoyé dessus.

---

## 6. Première vérification : le tableau de bord

Voici les **5 commandes** que tout débutant doit connaître :

| Commande | Ce qu’elle montre |
|----------|-------------------|
| `show ip eigrp neighbors` | La liste des voisins. **Vide = problème.** |
| `show ip route eigrp` | Les routes apprises par EIGRP (marquées **D**). |
| `show ip eigrp topology` | Les---
node_id: eigrp-debutant
title: EIGRP – Débutant
---

# EIGRP – Débutant

**Public :** Techniciens réseau, étudiants en réseaux, administrateurs juniors souhaitant monter en compétence.

**Objectif :** Comprendre EIGRP pas à pas, savoir le configurer sur Cisco IOS, diagnostiquer les problèmes simples, et acquérir les réflexes des niveaux intermédiaires.

---

## 1. C’est quoi le routage, déjà ?

Avant de parler d’EIGRP, rappelons le décor.

Un **routeur** est un équipement qui relie plusieurs réseaux. Son travail : regarder l’adresse IP de destination d’un paquet, et décider **par quelle interface** l’envoyer pour qu’il arrive à bon port.

Pour prendre cette décision, le routeur consulte sa **table de routage**. Cette table contient des lignes du type :

```text
Destination         Passerelle         Interface
10.20.0.0/24        192.168.1.2        Gi0/1
172.16.0.0/16       192.168.1.3        Gi0/1
Deux façons de remplir cette table :

À la main (routes statiques) : l’administrateur écrit chaque ligne. Précis, mais ingérable sur un grand réseau.

Automatiquement (protocoles de routage dynamique) : les routeurs s’échangent leurs informations et construisent la table tout seuls. EIGRP fait partie de cette famille.

Analogie : imaginez un réseau de routes entre villes. Les routes statiques, c’est un panneau que vous plantez vous-même à chaque carrefour. EIGRP, c’est un GPS qui discute avec les autres GPS pour connaître les meilleurs itinéraires, et qui se met à jour quand une route est fermée.

2. EIGRP en trois phrases
EIGRP (Enhanced Interior Gateway Routing Protocol) est un protocole de routage dynamique créé par Cisco en 1993.

Il permet aux routeurs de s’échanger leurs réseaux et de calculer le meilleur chemin automatiquement.

Il est réputé pour sa convergence rapide : quand un lien tombe, EIGRP retrouve un chemin alternatif en quelques secondes, souvent instantanément.

Convergence = le temps que mettent tous les routeurs à être d’accord sur la nouvelle topologie après un changement.

3. Les notions de base à retenir
3.1 Le voisinage
Deux routeurs EIGRP qui se parlent s’appellent des voisins (neighbors). Ils s’envoient régulièrement des petits paquets Hello pour se dire « je suis toujours là ».

text
   R1  ──────  Hello !  ──────►  R2
       ◄─────  Hello !  ───────
       
   → Ils deviennent voisins EIGRP.
Si R2 arrête d’envoyer des Hello pendant un certain temps (le hold-time), R1 considère que R2 est tombé et retire les routes apprises par lui.

3.2 Les réseaux annoncés
Chaque routeur EIGRP annonce les réseaux auxquels il est directement connecté. Par exemple, si R1 a une interface dans 10.0.0.0/24, il dit à ses voisins : « je connais le réseau 10.0.0.0/24, voici ma distance pour y aller ».

3.3 La métrique
Pour choisir le meilleur chemin, EIGRP calcule une métrique : un nombre. Plus la métrique est petite, meilleur est le chemin.

Par défaut, EIGRP se base sur deux critères :

la bande passante (un lien rapide est préféré) ;

le délai (un lien moins lent est préféré).

Analogie : pour aller de Paris à Lyon, vous comparez les itinéraires. La métrique, c’est comme un score qui combine la vitesse de la route et le temps de trajet. Le chemin avec le plus petit score gagne.

3.4 Le Successor et le Feasible Successor
C’est le cœur d’EIGRP, mais retenez juste l’idée générale pour l’instant :

Successor : le meilleur chemin, celui qui est installé dans la table de routage. C’est celui qu’on utilise.

Feasible Successor : un chemin de secours valide, déjà connu, qui peut prendre le relais immédiatement si le Successor tombe.

Analogie : vous avez un itinéraire habituel pour aller au travail (Successor). Vous en connaissez un autre, un peu plus long mais fiable (Feasible Successor). Si le premier est bloqué, vous prenez le second sans réfléchir. C’est exactement ce que fait EIGRP.

C’est pour cela qu’EIGRP converge vite : il n’a pas besoin de recalculer, il a déjà un plan B.

4. Configurer EIGRP : le minimum vital
4.1 La topologie d’exemple
text
   Réseau 10.0.0.0/24          Réseau 10.0.1.0/24
        |                            |
   ┌────┴────┐                  ┌────┴────┐
   │   R1    │──── 192.168.1.0/30 ───│   R2    │
   │Gi0/0    │                  │Gi0/0    │
   └─────────┘                  └─────────┘
R1 a l’interface Gi0/0 dans 10.0.0.1/24 et Gi0/1 dans 192.168.1.1/30.

R2 a l’interface Gi0/0 dans 192.168.1.2/30 et Gi0/1 dans 10.0.1.1/24.

Objectif : que R1 apprenne 10.0.1.0/24 et que R2 apprenne 10.0.0.0/24.

4.2 Configuration sur R1
cisco
R1(config)# router eigrp 100
R1(config-router)# network 10.0.0.0 0.0.0.255
R1(config-router)# network 192.168.1.0 0.0.0.3
R1(config-router)# no auto-summary
R1(config-router)# exit
4.3 Configuration sur R2
cisco
R2(config)# router eigrp 100
R2(config-router)# network 10.0.1.0 0.0.0.255
R2(config-router)# network 192.168.1.0 0.0.0.3
R2(config-router)# no auto-summary
R2(config-router)# exit
4.4 Ce que signifient ces commandes
Commande	Rôle
router eigrp 100	Active le processus EIGRP avec le numéro 100. Ce numéro doit être identique sur tous les routeurs qui doivent devenir voisins.
network 10.0.0.0 0.0.0.255	Active EIGRP sur les interfaces dont l’IP est dans 10.0.0.0/24. Le 0.0.0.255 est un masque wildcard (l’inverse du masque).
no auto-summary	Empêche EIGRP de résumer automatiquement les réseaux aux frontières de classe. Toujours le mettre dans un réseau moderne.
Astuce : le wildcard 0.0.0.255 correspond au masque 255.255.255.0. Règle simple : wildcard = 255.255.255.255 − masque.

4.5 Vérifier que ça marche
cisco
R1# show ip eigrp neighbors
Résultat attendu :

text
IP address      Interface   Hold   Uptime   Q Cnt   SRTT   RTO
192.168.1.2     Gi0/1       13     00:02:15 0       12     200
Ensuite, vérifiez les routes apprises :

cisco
R1# show ip route eigrp
Résultat attendu :

text
D    10.0.1.0/24 [90/281600] via 192.168.1.2, 00:02:15, GigabitEthernet0/1
D = route apprise par EIGRP (D pour DUAL).

90 = distance administrative d’EIGRP interne (plus c’est bas, plus la route est crue).

281600 = la métrique EIGRP.

Et voilà ! R1 sait maintenant joindre 10.0.1.0/24 grâce à EIGRP.

5. Les erreurs de débutant à éviter
5.1 Oublier no auto-summary
Sans cette commande, EIGRP peut résumer 10.0.1.0/24 en 10.0.0.0/8 et créer des routes fausses. Toujours la mettre.

5.2 Mettre un numéro d’AS différent
text
R1 : router eigrp 100
R2 : router eigrp 200
→ Ils ne deviennent jamais voisins. Le numéro d’AS doit être identique sur tous les routeurs du domaine.

5.3 Utiliser network avec le mauvais wildcard
text
network 10.0.0.0 255.255.255.0   ← FAUX (c'est un masque, pas un wildcard)
network 10.0.0.0 0.0.0.255       ← BON
5.4 Oublier que network active l’interface
network ne dit pas « annonce ce réseau » comme on pourrait le croire. Il dit : « active EIGRP sur toutes les interfaces dont l’IP appartient à ce réseau ». C’est une nuance importante.

5.5 Laisser un voisinage se former sur une interface utilisateur
Si vous mettez network 0.0.0.0 255.255.255.255 (tout), EIGRP essaie de former des voisinages sur toutes les interfaces, y compris vers des PC. Utilisez passive-interface :

cisco
router eigrp 100
 passive-interface GigabitEthernet0/2
L’interface reste annoncée, mais aucun Hello n’est envoyé dessus.

6. Première vérification : le tableau de bord
Voici les 5 commandes que tout débutant doit connaître :

Commande	Ce qu’elle montre
show ip eigrp neighbors	La liste des voisins. Vide = problème.
show ip route eigrp	Les routes apprises par EIGRP (marquées D).
show ip eigrp topology	Les Successors et Feasible Successors (le plan B).
show ip protocols	Le résumé du processus EIGRP (AS, réseaux, filtres).
show ip eigrp interfaces	Les interfaces qui participent à EIGRP.
Réflexe : avant de paniquer, tapez show ip eigrp neighbors. Si la liste est vide, le problème est le voisinage, pas les routes.

 Successors et Feasible Successors (le plan B). |
| `show ip protocols` | Le résumé du processus EIGRP (AS, réseaux, filtres). |
| `show ip eigrp interfaces` | Les interfaces qui participent à EIGRP. |

> **Réflexe** : avant de paniquer, tapez `show ip eigrp neighbors`. Si la liste est vide, le problème est **le voisinage**, pas les routes.