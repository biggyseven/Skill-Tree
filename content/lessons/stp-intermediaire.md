# Rôles, États et RSTP

**Niveau :** Administrateur Réseau Confirmé

Maintenant que le Root Bridge est élu, comment STP choisit-il les autres chemins ? Et comment rendre ce protocole plus rapide (car la version classique est très lente) ?

> **Analogie** : L'élection du Root Bridge, c'est comme choisir le chef de gare. Ensuite, on doit définir quels rails seront utilisés pour aller vers lui (Root Port) et quels rails seront mis hors service (Blocking) pour éviter que deux trains ne se percutent.


## 1. Le calcul des coûts (Path Cost)

Pour choisir le meilleur chemin vers le Root Bridge, STP calcule un **coût**. Ce coût est basé sur la bande passante du lien (plus le lien est rapide, plus le coût est bas). Par exemple : 100 Mbps = 19, 1 Gbps = 4. (Le coût est cumulatif).

## 2. Les Rôles de Ports

Une fois le Root Bridge élu, chaque switch non-root doit choisir ses ports :
1. **Root Port (RP)** : Le port (un seul par switch) qui a le meilleur coût pour atteindre le Root Bridge.
2. **Designated Port (DP)** : Le port sur un segment qui annonce les meilleurs BPDU vers le Root.
3. **Blocking Port** : Tous les autres ports. Ils sont bloqués pour éviter les boucles.

```text
          [ Root Bridge (Prio 32768) ]
                 /              \
           (Coût 4)            (Coût 4)
               /                  \
    [ Switch B ] --------------- [ Switch C ]
                  (Coût 19)

- Le Switch B et C ont un chemin direct vers Root avec un coût de 4 (Root Port).
- Entre B et C (coût 19), l'un des deux ports doit être bloqué pour éviter la boucle.
3. Les États d'un port STP (Le calvaire de la lenteur)
En STP classique, un port met 50 secondes pour s'activer :

Blocking (20 sec) : Ne transfère rien, écoute les BPDU.

Listening (15 sec) : Écoute et participe à l'élection.

Learning (15 sec) : Apprend les adresses MAC.

Forwarding : Transfère normalement les données.

4. RSTP (Rapid Spanning Tree Protocol - 802.1w)
Attendre 50 secondes, c'est inacceptable aujourd'hui. RSTP a été créé pour accélérer la convergence (quelques secondes). Il introduit le rôle d'Alternate Port (prêt à prendre le relais) et la fonction PortFast pour les PC.

text
Switch(config)# spanning-tree mode rapid-pvst
Switch(config-if)# spanning-tree portfast
💡 Astuce : Activez toujours RSTP (rapid-pvst) sur vos switches modernes. C'est plus rapide et standard.
⚠️ Attention : N'activez portfast que sur les ports reliés à des PC (jamais entre deux switches).