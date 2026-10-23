
# EIGRP – Intermédiaire

Maintenant que vous savez configurer EIGRP et vérifier qu’il fonctionne, entrons dans les mécanismes qui expliquent **pourquoi** ça marche, et comment **diagnostiquer** quand ça ne marche pas.


## 1. Comprendre la métrique EIGRP

### 1.1 La formule simplifiée

Par défaut, EIGRP utilise :

    Métrique = 256 × (Bande passante + Délai)

Avec :
- **Bande passante** = `10 000 000 / bande passante en kbps`. Plus la bande passante est **grande**, plus ce nombre est **petit**.
- **Délai** = `délai en microsecondes / 10`. Plus le délai est **grand**, plus ce nombre est **grand**.

> **Conséquence** : un lien **rapide** donne une **petite** métrique. Un lien **lent** donne une **grande** métrique. EIGRP préfère toujours la plus petite métrique.

### 1.2 Exemple concret

Deux chemins possibles entre R1 et un réseau distant :

| Chemin | Bande passante | Délai | Calcul | Métrique |
|--------|----------------|-------|--------|----------|
| A (via Gi0/0) | 1 Gbps = 1 000 000 kbps | 100 µs | 256 × (10 + 10) | **5 120** |
| B (via Gi0/1) | 100 Mbps = 100 000 kbps | 100 µs | 256 × (100 + 10) | **28 160** |

→ EIGRP choisit le **chemin A** (métrique 5 120, plus petite).

### 1.3 Le piège de la bande passante « configurée »

EIGRP ne mesure **pas** la bande passante réelle. Il lit la valeur **configurée** sur l’interface avec la commande `bandwidth`.

    interface GigabitEthernet0/0
     bandwidth 100000     ! 100 Mbps déclarés

Si l’interface est physiquement 1 Gbps mais configurée à 100 Mbps, EIGRP calculera la métrique d’un lien 100 Mbps. **Vérifiez toujours** avec :

    show interface GigabitEthernet0/0 | include BW

---

## 2. Le Successor et le Feasible Successor en détail

### 2.1 Les trois distances à connaître

| Terme | Définition simple |
|-------|-------------------|
| **FD** (Feasible Distance) | La distance **totale** de **mon** routeur vers la destination, en passant par un voisin donné. |
| **RD** (Reported Distance) | La distance que **le voisin** annonce, depuis **lui**, vers la destination. |
| **FC** (Feasibility Condition) | La règle : un voisin est un **plan B valide** si sa **RD < ma FD**. |

### 2.2 Exemple chiffré

                    R1 (moi)
                   /        \
             via R2          via R3
        FD = 10 000        FD = 15 000
        RD = 5 000         RD = 8 000

- **Successor** : R2 (FD 10 000, le plus petit).
- **R3 est-il Feasible Successor ?** On vérifie : `RD(R3) = 8 000 < FD(R1) = 10 000` → **oui**.
- R3 est donc un **plan B valide**. Si R2 tombe, R1 bascule sur R3 **instantanément**.

### 2.3 Pourquoi cette règle empêche les boucles

Si R3 annonçait une RD **supérieure** à la FD de R1, cela pourrait signifier que R3 passe **par R1** pour joindre la destination. Accepter R3 comme plan B créerait une boucle. La Condition de Faisabilité élimine ce risque.

> **Analogie** : vous demandez à un ami un itinéraire de secours. S’il vous répond « passe par moi », mais que lui-même passe par vous, vous tournez en rond. La FC vérifie que l’ami ne dépend pas de vous.

### 2.4 Que se passe-t-il si aucun Feasible Successor n’existe ?

EIGRP passe en état **Active** : il envoie des **Query** à ses voisins pour leur demander s’ils connaissent un chemin. C’est plus lent (quelques secondes), mais ça fonctionne.

Si un voisin ne répond pas dans le **SIA timer** (3 minutes par défaut), EIGRP coupe le voisinage. C’est le fameux **Stuck in Active** (SIA), un problème classique des réseaux EIGRP mal conçus.

---

## 3. Les fonctionnalités intermédiaires indispensables

### 3.1 Le Stub : le meilleur ami de la stabilité

Un routeur **stub** est un routeur qui n’est **pas un point de transit**. Il annonce ses réseaux connectés, mais ne sert pas de chemin vers d’autres réseaux.

    router eigrp 100
     eigrp stub connected summary

**Pourquoi c’est important ?** Dans une topologie hub-and-spoke (un siège et 50 agences), si le siège perd une route, il envoie une Query à toutes les agences. Sans stub, chaque agence relaie la Query, et le réseau entier est perturbé. Avec stub, chaque agence répond immédiatement « je ne connais pas », et la Query s’arrête.

> **Règle** : **tout routeur qui n’est pas un point de transit doit être stub.**

### 3.2 La summarisation : réduire le bruit

La summarisation consiste à annoncer **un seul réseau** au lieu de plusieurs. Par exemple, annoncer `10.0.0.0/16` au lieu de `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`, etc.

    interface Serial0/0
     ip summary-address eigrp 100 10.0.0.0 255.255.0.0

**Avantages** :
- Table de routage plus petite.
- Moins de Query en cas de panne (le résumé reste stable même si un sous-réseau tombe).
- Convergence plus rapide.

### 3.3 La variance : utiliser plusieurs chemins

Par défaut, EIGRP installe **une seule route** par destination. La **variance** permet d’installer **plusieurs chemins** de métrique proche, pour répartir le trafic (load-balancing).

    router eigrp 100
     variance 2

Avec `variance 2` et une meilleure métrique de 10 000, toutes les routes **Feasible Successor** dont la métrique est ≤ **20 000** seront installées.

> **Attention** : la variance ne s’applique **qu’aux Feasible Successors**. Une route avec une métrique plus faible mais qui viole la FC ne sera **jamais** installée, même avec une variance énorme.

### 3.4 `passive-interface` : la sécurité de base

    router eigrp 100
     passive-interface default
     no passive-interface GigabitEthernet0/0
     no passive-interface GigabitEthernet0/1

- `passive-interface default` : **toutes** les interfaces sont passives par défaut.
- `no passive-interface X` : active EIGRP sur les interfaces de **transit** uniquement.

**Résultat** : aucun Hello n’est envoyé vers les PC, les serveurs ou les interfaces de management. Un utilisateur malveillant ne peut pas former de voisinage EIGRP avec votre routeur.

### 3.5 L’authentification : empêcher les intrus

Sans authentification, n’importe qui peut brancher un routeur et former un voisinage EIGRP avec le vôtre. **Sur tous les liens de transit, activez MD5 ou SHA-256.**

    key chain EIGRP-KEYS
     key 1
      key-string MonMotDePasseSecret
      cryptographic-algorithm hmac-sha-256

    interface GigabitEthernet0/0
     ip authentication mode eigrp 100 hmac-sha-256
     ip authentication key-chain eigrp 100 EIGRP-KEYS

> **À retenir** : les deux routeurs doivent avoir **la même key-chain, la même clé et le même algorithme**. Sinon, le voisinage ne monte pas.

---

## 4. Dépannage : les 6 scénarios les plus courants

### 4.1 « Mes voisins ne montent pas »

**Checklist rapide** :

| Vérification | Commande | Cause possible |
|--------------|----------|----------------|
| Même AS ? | `show ip protocols` | Un routeur en AS 100, l’autre en AS 200. |
| Même subnet/masque ? | `show ip interface brief` | Interfaces dans deux sous-réseaux différents. |
| `passive-interface` ? | `show ip protocols` | L’interface est passive, aucun Hello n’est envoyé. |
| Authentification identique ? | `show key chain` | Clé différente, algorithme différent. |
| Multicast filtré ? | `show ip mroute 224.0.0.10` | Une ACL bloque le multicast EIGRP. |
| Logs ? | `show log | include DUAL` | Message explicite (`auth failure`, `K-value mismatch`). |

**Le réflexe** : `show ip eigrp neighbors` + `show log`. Les logs EIGRP sont très bavards et indiquent souvent la cause exacte.

### 4.2 « Le voisinage monte puis tombe en boucle »

Souvent causé par :
- **MTU incohérente** entre les deux interfaces (EIGRP ne forme pas de voisinage si les MTU diffèrent, sauf si `no ip split-horizon` ou configuration spécifique).
- **Lien instable** (SFP défectueux, câble abîmé).
- **CPU saturé** sur un routeur (les Hello sont envoyés en retard).

**Vérification** : `show interface` (erreurs, CRC, drops) et `show processes cpu`.

### 4.3 « La route n’est pas dans la table de routage »

La route est dans `show ip eigrp topology` mais pas dans `show ip route` :

- **Cause 1** : ce n’est pas le Successor, c’est un Feasible Successor. C’est **normal** : seul le Successor est installé.
- **Cause 2** : une route statique ou un autre protocole a une **distance administrative** plus faible. EIGRP interne = 90, statique = 1, OSPF = 110. La route la plus « crue » gagne.
- **Cause 3** : un `distribute-list` filtre la route.
- **Cause 4** : la variance est insuffisante pour installer un multipath.

**Vérification** : `show ip eigrp topology all-links` (inclut les routes non-feasibles), `show ip route`, `show ip protocols`.

### 4.4 « Stuck in Active (SIA) »

**Symptôme** : message dans les logs : `%DUAL-3-SIA: Route X stuck-in-active state`.

**Cause** : un routeur en état Active n’a pas reçu toutes les Reply dans le SIA timer (3 min).

**Solutions** :
1. **Stub** sur les sites distants (empêche les Query en cascade).
2. **Summarisation** aux frontières (masque les instabilités).
3. Vérifier qu’aucun `distribute-list` ne bloque les Reply.
4. Vérifier la charge CPU des routeurs voisins.
5. En dernier recours, augmenter temporairement le SIA timer (`timers active-time 5`) pour diagnostiquer.

> **Règle d’or** : **un réseau EIGRP bien conçu n’a pas de SIA**. Si vous en avez, c’est que la topologie ou les filtres sont mal pensés.

### 4.5 « La métrique est bizarre »

Deux routeurs annoncent la même destination avec des métriques très différentes :

- **Vérifiez `bandwidth` et `delay`** sur les interfaces : `show interface | include BW|DLY`.
- **Vérifiez que les K-values sont par défaut** : `show ip protocols | include K`.
- **Vérifiez qu’il n’y a pas de wide metrics** (Named Mode) vs classic metrics.

### 4.6 « J’ai ajouté un routeur et tout a planté »

Souvent, le nouveau routeur avait une **configuration EIGRP résiduelle** avec un **numéro de révision** élevé ou des routes incorrectes. **Avant de brancher un routeur d’occasion** :

1. Effacer la configuration : `erase startup-config`.
2. Recharger : `reload`.
3. Vérifier `show ip eigrp topology` après le démarrage.

---

## 5. Les bonnes pratiques à adopter dès maintenant

1. **Toujours `no auto-summary`** dans un réseau moderne.
2. **Toujours `passive-interface default`** puis `no passive-interface` sur les liens de transit.
3. **Toujours un `eigrp router-id` explicite** (ex. `eigrp router-id 1.1.1.1`) — sinon EIGRP choisit une IP au hasard, ce qui peut changer après un reboot.
4. **Toujours l’authentification** (MD5 ou SHA-256) sur les liens de transit.
5. **Toujours `eigrp stub`** sur les routeurs qui ne sont pas des points de transit.
6. **Toujours la summarisation** aux frontières (siège → agences, campus → WAN).
7. **Toujours vérifier `show ip eigrp neighbors`** en premier quand quelque chose ne marche pas.
8. **Toujours documenter** les AS, les router-IDs et les résumés dans un schéma d’adressage.

---

## 6. Comparaison rapide avec OSPF (pour situer)

| Critère | EIGRP | OSPF |
|---------|-------|------|
| **Constructeur** | Cisco (RFC 7868 depuis 2016) | Standard ouvert |
| **Configuration** | Simple (`network`) | Plus verbeuse (areas, types de réseaux) |
| **Convergence** | Très rapide (DUAL) | Rapide (SPF) |
| **Plan B** | Feasible Successor (instantané) | Recalcul SPF |
| **Scalabilité** | Très bonne | Excellente (areas) |
| **Multi-constructeurs** | Bonne (FRR) mais moins répandu | Excellente |

> **En pratique** : dans un environnement **100 % Cisco**, EIGRP est un excellent choix pour sa simplicité. Dans un environnement **multi-constructeurs**, OSPF est souvent préféré. Les deux sont d’excellents protocoles.

---

## 7. Ce que vous devez savoir faire à la fin de ce cours

### Niveau débutant ✅
- Expliquer ce qu’est un protocole de routage dynamique.
- Configurer EIGRP sur deux routeurs Cisco.
- Vérifier que le voisinage est établi (`show ip eigrp neighbors`).
- Vérifier que les routes sont apprises (`show ip route eigrp`).
- Éviter les 5 erreurs de débutant (auto-summary, AS mismatch, wildcard, passive-interface, network mal placé).

### Niveau intermédiaire ✅
- Calculer une métrique EIGRP simple (256 × (BW + Delay)).
- Expliquer la différence entre Successor et Feasible Successor.
- Vérifier la Condition de Faisabilité sur un exemple chiffré.
- Configurer un stub, une summarisation, une variance.
- Configurer `passive-interface` et l’authentification.
- Diagnostiquer un problème de voisinage avec `show log` et `show ip eigrp neighbors`.
- Reconnaître un SIA et proposer une solution (stub + summarisation).

---

## 8. Exercices pratiques (avec réponses)

### Exercice 1 – Calcul de métrique
Un chemin traverse deux liens : 1 Gbps (délai 100 µs) puis 100 Mbps (délai 1 000 µs). Calculez la métrique EIGRP classique.

**Réponse** :
- BW total = 10 000 000 / 100 000 = **100** (le lien le plus lent impose sa bande passante).
- Delay total = (100 + 1 000) / 10 = **110**.
- Métrique = 256 × (100 + 110) = **53 760**.

> **Règle** : la bande passante retenue est **la plus petite** du chemin, le délai est **la somme** des délais.

### Exercice 2 – Condition de Faisabilité
R1 a deux voisins vers la destination X :
- via R2 : FD = 20 000, RD = 15 000.
- via R3 : FD = 25 000, RD = 22 000.

Lesquels sont Successor et Feasible Successor ?

**Réponse** :
- **Successor** : R2 (FD 20 000, la plus petite).
- **R3 est-il FS ?** `RD(R3) = 22 000 < FD(R1) = 20 000` ? **Non.** R3 n’est **pas** Feasible Successor.
- Conséquence : si R2 tombe, R1 passe en **Active** et envoie des Query.

### Exercice 3 – Variance
Meilleure métrique = 8 000. Un Feasible Successor a une métrique de 20 000. Quelle variance faut-il pour l’installer ?

**Réponse** : il faut `variance × 8 000 ≥ 20 000`, donc `variance ≥ 2,5`. On configure **`variance 3`**.

### Exercice 4 – Stub
Pourquoi un routeur d’agence avec un seul lien WAN doit-il être stub ?

**Réponse** : parce qu’il n’est pas un point de transit. S’il n’est pas stub, il relaie les Query du siège vers d’autres routeurs, ce qui peut provoquer des SIA. En stub, il répond immédiatement « je ne connais pas », ce qui stoppe la Query et stabilise le réseau.

### Exercice 5 – Dépannage
Deux routeurs ne deviennent pas voisins. `show ip eigrp neighbors` est vide. `show ip protocols` indique AS 100 sur R1 et AS 200 sur R2. Quelle est la cause ?

**Réponse** : **mismatch d’AS**. Les deux routeurs doivent utiliser le même numéro d’AS (100 ou 200, mais pas les deux). Correction : `router eigrp 100` sur R2, ou `router eigrp 200` sur R1, puis vérifier que le voisinage monte.

---

## 9. Conclusion

EIGRP est un protocole **puissant mais accessible**. Sa simplicité de configuration cache une mécanique profonde (DUAL, Feasible Successor, Condition de Faisabilité), mais vous n’avez pas besoin de tout maîtriser pour l’utiliser efficacement.

**Les trois réflexes à garder** :
1. **`show ip eigrp neighbors`** avant tout diagnostic.
2. **Stub + summarisation** pour éviter les SIA.
3. **Authentification + passive-interface** pour la sécurité de base.

> **Phrase finale** : EIGRP n’est pas difficile — il est **profond**. Commencez par le faire fonctionner, puis cherchez à comprendre **pourquoi** il fonctionne. C’est ainsi qu’on passe de débutant à expert.