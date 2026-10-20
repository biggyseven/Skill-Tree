# OSPF avancé : aires, redistribution et dépannage

OSPF est un protocole de routage à état de liens. Les bases — voisinage, LSDB,
coût et plus court chemin — ne suffisent pas dès qu'un réseau grandit. Il faut
structurer les aires, contrôler les LSAs, redistribuer les routes externes et
savoir lire une LSDB pour diagnostiquer un problème.

> Analogie : OSPF est une carte routière partagée. Chaque routeur connaît les
> routes de sa zone et reçoit des résumés des autres zones. Si quelqu'un annonce
> une mauvaise direction ou si une frontière est mal placée, toute la carte peut
> devenir incohérente.

## 1. Rappel du fonctionnement OSPF

Un routeur OSPF découvre ses voisins avec les paquets Hello, échange des
descriptions de LSDB, puis synchronise les LSAs. Une fois la LSDB identique
dans une aire, chaque routeur calcule son plus court chemin avec l'algorithme
SPF.

Les paquets OSPF sont transportés directement dans IP, avec le protocole 89.
Ils ne passent pas par TCP ou UDP. Les multicasts classiques sont :

- `224.0.0.5` : tous les routeurs OSPF ;
- `224.0.0.6` : routeurs DR/BDR.

Un routeur OSPF possède un **Router ID**, souvent une adresse de loopback
stable. Il doit être unique dans le domaine.

### Voisinage

Deux routeurs ne deviennent pas voisins si certains paramètres diffèrent :

- aire ;
- type de réseau ;
- timers Hello et Dead ;
- authentification ;
- MTU sur certains échanges ;
- masque pour les réseaux broadcast ;
- options comme Stub ou NSSA.

Les états de voisinage sont notamment :

```text
Down -> Init -> 2-Way -> ExStart -> Exchange -> Loading -> Full
```

Un état `2-Way` peut être normal entre deux routeurs non-DR d'un segment
broadcast. Un état bloqué en `ExStart` fait souvent penser à un problème de MTU.

## 2. Les aires OSPF

Une aire est un groupe logique de routeurs et de liens. Les routeurs d'une même
aire partagent une LSDB détaillée. Les routeurs de bordure d'aire, les ABR,
résument les informations entre les aires.

```text
             Area 0
          +--------+
          |  ABR1  |
          +---+----+
              |
      +-------+-------+
      |               |
   Area 10         Area 20
   +-----+         +-----+
   | R1  |         | R2  |
   +-----+         +-----+
```

L'aire 0 est la **backbone area**. Les autres aires doivent généralement être
reliées à l'aire 0 par un ABR. Une aire non reliée directement peut utiliser un
lien virtuel, mais cette solution doit rester exceptionnelle.

### Pourquoi plusieurs aires ?

- réduire la taille de la LSDB ;
- limiter la portée des changements de topologie ;
- accélérer le calcul SPF ;
- résumer les routes ;
- isoler certaines parties du réseau.

Un changement dans une aire ne doit pas provoquer un recalcul complet dans
toutes les autres. Les résumés et les routes externes sont contrôlés aux
frontières.

## 3. Les types de routeurs OSPF

| Type | Rôle |
|---|---|
| Internal router | Toutes ses interfaces sont dans une même aire |
| ABR | Relie une aire à l'aire 0 et résume les routes |
| ASBR | Redistribue des routes externes dans OSPF |
| Backbone router | Possède au moins une interface dans l'aire 0 |
| DR/BDR | Élus sur un segment broadcast pour limiter les adjacences |

Un même routeur peut être ABR et ASBR. Un routeur interne ne doit pas recevoir
de LSAs externes s'il est dans une aire Stub.

## 4. Les LSAs

Une LSDB OSPF contient plusieurs types de LSAs. Les plus courants :

| LSA | Nom | Annoncé par | Contenu |
|---|---|---|---|
| Type 1 | Router LSA | Chaque routeur | Liens et coûts dans l'aire |
| Type 2 | Network LSA | DR | Réseau broadcast et routeurs attachés |
| Type 3 | Summary LSA | ABR | Résumé d'un réseau d'une autre aire |
| Type 4 | ASBR Summary LSA | ABR | Localisation d'un ASBR |
| Type 5 | AS External LSA | ASBR | Route externe |
| Type 7 | NSSA External LSA | ASBR dans une NSSA | Route externe traduite en type 5 par l'ABR |

Les LSAs ont un âge, un numéro de séquence et une somme de contrôle. Un routeur
ignore un LSA trop ancien ou remplacé par une séquence plus récente.

### Type 1 et Type 2

Le Type 1 décrit les liens du routeur et leurs coûts. Le Type 2 est produit par
le DR sur un réseau multi-accès et décrit les routeurs connectés au segment.
Pour un lien point à point, il n'y a généralement pas de Type 2.

### Type 3

L'ABR résume les réseaux d'une aire vers une autre avec des Type 3. Un résumé
peut être plus ou moins précis. Un résumé trop large peut créer une route
attirante mais inexacte.

### Type 4 et Type 5

Le Type 4 indique où se trouve l'ASBR. Le Type 5 annonce une route externe.
Un routeur interne doit connaître l'ASBR pour joindre le réseau externe.

### Type 7 et NSSA

Une NSSA autorise l'injection de routes externes sous forme de Type 7. L'ABR
peut traduire ces Type 7 en Type 5 vers le reste du domaine, selon la
configuration.

## 5. Les aires spéciales

### Stub

Une aire Stub ne reçoit pas les routes externes Type 5. L'ABR injecte une route
par défaut pour joindre l'extérieur.

```text
Area 10 (Stub)
   R1 -------- ABR -------- Area 0
                 |
             route par défaut
```

Avantages :

- LSDB plus petite ;
- moins de routes à calculer ;
- simplification des routeurs d'accès.

Contraintes :

- pas d'ASBR dans l'aire ;
- pas de routes externes détaillées ;
- tous les routeurs de l'aire doivent être Stub.

### Totally Stubby

Une aire Totally Stubby ne reçoit ni les Type 5 ni les Type 3 détaillés. L'ABR
annonce seulement une route par défaut.

Cette solution est utile pour un site distant qui n'a pas besoin de connaître
toutes les routes du campus.

### NSSA

Une NSSA est une aire Stub qui autorise un ASBR local à injecter des routes
externes en Type 7. L'ABR peut traduire ces routes vers l'aire 0.

```text
Area 20 (NSSA)
   ASBR -------- ABR -------- Area 0
     |
   route externe
```

On utilise une NSSA lorsqu'un site doit redistribuer une route locale tout en
évitant les Type 5 dans son aire.

### Totally NSSA

Une Totally NSSA combine les restrictions des Type 3 et l'autorisation des
Type 7. L'ABR résume fortement et injecte une route par défaut.

### Tableau comparatif

| Type d'aire | Type 3 détaillés | Type 5 | Type 7 | Route par défaut |
|---|---|---|---|---|
| Standard | Oui | Oui | Non | Selon configuration |
| Stub | Oui | Non | Non | Injectée par l'ABR |
| Totally Stubby | Non | Non | Non | Une seule |
| NSSA | Oui | Non | Oui | Souvent injectée |
| Totally NSSA | Non | Non | Oui | Une seule |

## 6. Configuration des aires

Exemple Cisco d'une aire Stub :

```cisco
router ospf 1
 router-id 10.0.0.1
 area 10 stub

interface GigabitEthernet0/1
 ip address 10.10.0.1 255.255.255.0
 ip ospf 1 area 10
```

Exemple NSSA :

```cisco
router ospf 1
 area 20 nssa

interface GigabitEthernet0/1
 ip address 10.20.0.1 255.255.255.0
 ip ospf 1 area 20
```

Les routeurs d'une même aire doivent avoir le même type d'aire. Un routeur
Stub qui parle à un routeur standard ne formera pas une adjacence complète.

### Résumé de routes

Un ABR peut résumer les réseaux d'une aire :

```cisco
router ospf 1
 area 10 range 10.10.0.0 255.255.0.0
```

Un résumé doit couvrir uniquement des réseaux présents et ne pas créer de
chevauchements ambigus.

## 7. Redistribution

La redistribution consiste à injecter dans OSPF des routes venant d'un autre
protocole ou d'une autre source : routes statiques, routes connectées, BGP,
EIGRP, etc.

```text
        OSPF
          |
        ASBR
       /    \
  BGP/static  LAN
```

Exemple Cisco :

```cisco
router ospf 1
 redistribute static subnets
 redistribute connected subnets
 default-information originate
```

### Métrique de départ

Une route redistribuée doit avoir un coût OSPF. Sans métrique de départ, la
redistribution peut être refusée ou utiliser une valeur par défaut. On définit
souvent :

```cisco
router ospf 1
 redistribute static subnets metric 20 metric-type 1
```

- `metric-type 1` : coût externe ajouté au coût interne ;
- `metric-type 2` : coût externe seul, souvent préféré par défaut.

Le choix dépend de la topologie. Le type 1 est souvent utilisé lorsque le coût
interne doit influencer la décision.

### Route-map

Une route-map permet de filtrer et de modifier les routes redistribuées :

```cisco
route-map REDIST-STATIC permit 10
 match ip address prefix-list LAN-ONLY
 set metric 50
 set metric-type type-1
 set tag 100

router ospf 1
 redistribute static subnets route-map REDIST-STATIC
```

Les tags sont utiles pour identifier l'origine d'une route et éviter les
boucles de redistribution.

### Redistribution bidirectionnelle

Quand deux protocoles se redistribuent mutuellement, une route peut revenir
dans son protocole d'origine avec une métrique plus faible. On utilise des
tags, des route-maps et des filtres pour éviter les boucles.

## 8. Dépannage OSPF

### Vérifier le voisinage

```cisco
show ip ospf neighbor
show ip ospf interface brief
show ip ospf interface GigabitEthernet0/1
```

Un voisin bloqué en `INIT` ou `DOWN` indique souvent un problème de Hello,
d'aire, de multicast ou de lien. Un voisin en `EXSTART` peut indiquer une MTU
incompatible.

### Vérifier la LSDB

```cisco
show ip ospf database
show ip ospf database router
show ip ospf database summary
show ip ospf database external
```

On vérifie que les Type 1, 3, 5 ou 7 attendus sont présents et que les âges ne
sont pas anormalement élevés.

### Vérifier les routes

```cisco
show ip route ospf
show ip ospf route
show ip protocols
```

Une route peut être absente parce que le préfixe n'est pas annoncé, filtré,
résumé, ou parce que la métrique est moins bonne qu'une autre source.

### Causes fréquentes

| Symptôme | Cause possible |
|---|---|
| Voisin bloqué en Init | Hello filtré, multicast bloqué, mauvais lien |
| Voisin bloqué en ExStart | MTU différente, problème de paquets DBD |
| Adjacence absente | Aire, timers, authentification ou type d'aire différents |
| Route absente | Réseau non annoncé, filtre, résumé, métrique |
| Route externe absente | Type 5 filtré par Stub, ASBR absent, redistribution |
| Routage asymétrique | Coûts ou résumés incohérents |
| Flapping | Lien instable, BFD trop agressif, boucle de redistribution |

### MTU et OSPF

Sur un lien où les MTU diffèrent, les échanges DBD peuvent rester bloqués. On
peut corriger la MTU ou utiliser `ip ospf mtu-ignore` avec prudence. Mieux vaut
aligner les MTU que masquer le problème.

### Authentification

OSPF peut authentifier les paquets avec un mot de passe en clair ou MD5. Une
clé différente entre deux voisins empêche l'adjacence. Il faut aussi vérifier
la key ID et la key chain.

### Passive interface

Une interface passive annonce le réseau sans envoyer de Hello. C'est utile sur
les interfaces reliées à des postes ou à des réseaux sans voisin OSPF.

```cisco
router ospf 1
 passive-interface GigabitEthernet0/2
```

### Virtual link

Un lien virtuel relie une aire à l'aire 0 à travers une autre aire. Il doit
être configuré avec la bonne aire de transit et le Router ID du voisin. Un lien
virtuel mal configuré peut créer une adjacence incomplète ou un routage
incohérent.

## 9. Cas concrets

### Cas 1 : une route externe absente dans une Stub

Un site Stub ne voit pas une route redistribuée par un ASBR situé dans une
autre aire. C'est normal : une Stub ne reçoit pas les Type 5. Il faut soit
utiliser la route par défaut de l'ABR, soit changer le type d'aire si le site a
réellement besoin des routes externes.

### Cas 2 : deux ABR annoncent des résumés différents

Un résumé trop large attire le trafic vers le mauvais chemin. On vérifie les
préfixes couverts, les coûts et les tables de routage des deux côtés. Un résumé
doit être documenté et testé après modification.

### Cas 3 : redistribution en boucle

Une route statique est redistribuée dans OSPF, puis revient par un autre
protocole avec une métrique plus faible. On utilise un tag et une route-map
pour bloquer le retour, ou on filtre la source.

### Cas 4 : voisin bloqué en ExStart

Deux routeurs ont des MTU différentes. Les paquets DBD ne s'échangent pas
correctement. On aligne les MTU ou on corrige la configuration de l'interface.
`ip ospf mtu-ignore` peut dépanner temporairement, mais ne règle pas la cause.

### Cas 5 : route par défaut absente

Un routeur d'accès n'a pas de route par défaut. On vérifie si l'ABR injecte
`default-information originate`, si l'aire est Stub et si le routeur reçoit
bien le Type 3 ou le Type 7 attendu.

## 10. Types de réseaux et élection DR/BDR

OSPF adapte son comportement au type de lien. Les types courants sont :

| Type | Comportement |
|---|---|
| Broadcast | Élection d'un DR/BDR, Hellos multicast |
| Point-to-point | Adjacence directe, pas de DR/BDR |
| Non-broadcast (NBMA) | Voisins souvent configurés manuellement |
| Point-to-multipoint | Traité comme une collection de liens point à point |

Sur un segment broadcast, les routeurs élisent un **DR** (Designated Router) et
un **BDR**. Le DR centralise les échanges du réseau et produit le Type 2. Les
autres routeurs forment une adjacence complète avec le DR et le BDR, mais
restent souvent en `2-Way` entre eux.

L'élection utilise la priorité d'interface, puis le Router ID le plus élevé. Le
DR ne peut pas être préempté par un routeur qui arrive après l'élection, sauf
si le DR tombe ou si l'interface est réinitialisée. Pour influencer l'élection,
on peut régler la priorité avant de démarrer OSPF.

```cisco
interface GigabitEthernet0/1
 ip ospf priority 200

interface GigabitEthernet0/2
 ip ospf priority 0
```

Une priorité 0 empêche le routeur d'être DR ou BDR. C'est utile sur un routeur
d'accès ou un routeur peu puissant.

### Aging et rafraîchissement des LSAs

Un LSA possède un âge. Il est rafraîchi périodiquement, généralement toutes
les 30 minutes pour un LSA non externe. Un LSA qui atteint l'âge maximal est
retiré de la LSDB. Une séquence plus récente remplace l'ancienne.

Un âge anormalement élevé, un LSA qui disparaît ou une séquence qui remonte
peuvent indiquer un problème de voisinage, de filtrage ou de stabilité.

### OSPFv3

OSPFv3 route IPv6. Il utilise des Router ID IPv4, mais les adresses IPv6 sont
transportées dans les LSAs. Les concepts d'aires, de DR/BDR et de résumé
restent proches, mais les types de LSAs et la configuration diffèrent. Il ne
faut pas supposer qu'une maquette OSPFv2 est directement transposable sans
vérifier les commandes et les adresses de link-local.

## 11. Bonnes pratiques

- Utiliser des Router ID stables, souvent des loopbacks.
- Documenter les aires, les résumés et les ASBR.
- Éviter les aires trop nombreuses sans nécessité.
- Vérifier la cohérence des types d'aire sur tous les routeurs.
- Utiliser des route-maps pour contrôler la redistribution.
- Taguer les routes redistribuées.
- Surveiller les changements de voisinage et de LSDB.
- Tester les bascules et les résumés avant la production.
- Ne pas masquer une erreur de MTU avec `mtu-ignore` sans corriger la cause.

## 12. À retenir

- L'aire 0 est la backbone ; les ABR relient les autres aires.
- Les Type 3 résument les réseaux ; les Type 5 annoncent les routes externes.
- Une Stub bloque les Type 5 ; une NSSA autorise les Type 7.
- La redistribution nécessite une métrique, un filtrage et souvent des tags.
- Un voisin bloqué en ExStart évoque souvent une MTU différente.
- Une route absente peut venir d'un filtre, d'un résumé ou du type d'aire.
- La LSDB et la table de routage doivent être lues ensemble.

OSPF avancé demande de la méthode : comprendre la frontière, le type de LSA,
la métrique et le chemin réel avant de modifier une configuration.
