Bienvenue dans le niveau expert. Ici, nous allons voir comment manipuler la LSDB avec les aires spéciales, comment injecter des routes externes (redistribution) et comment sécuriser le protocole.

## 1. Les Aires Spéciales (Stub, NSSA)

Par défaut, les routeurs d'une aire reçoivent toutes les routes externes (LSA Type 5). Dans un grand réseau, cela peut saturer la mémoire des routeurs d'accès. On utilise donc des aires spéciales.

- **Stub Area** : Ne reçoit pas les LSA Type 5 (routes externes). L'ABR injecte une route par défaut (0.0.0.0) à la place.
- **Totally Stubby** : Ne reçoit ni les routes externes (Type 5), ni les routes inter-aires (Type 3). Seul un résumé par défaut est annoncé.
- **NSSA (Not-So-Stubby Area)** : Comme le Stub, mais permet d'importer des routes externes locales (qui deviennent des LSA Type 7 à l'intérieur, puis Type 5 à la frontière).

```cisco
router ospf 1
 area 1 stub
 area 2 nssa
 area 3 stub no-summary
2. Les LSA Avancés
Type 4 (ASBR Summary) : Généré par l'ABR pour indiquer comment joindre un ASBR (le routeur qui fait la redistribution).

Type 5 (External) : Annonce une route externe (redistribuée) dans tout le domaine OSPF.

Type 7 (NSSA External) : Utilisé dans les NSSA pour les routes externes.

3. Le Summarisation OSPF (Résumé de routes)
Pour réduire la taille des tables de routage, l'ABR peut résumer les réseaux d'une aire.

cisco
router ospf 1
 area 1 range 10.1.0.0 255.255.0.0
Cela résume tous les réseaux 10.1.x.x en un seul bloc 10.1.0.0/16 vers l'Area 0.

4. La Redistribution
La redistribution consiste à injecter des routes venant d'un autre protocole (ex: EIGRP, BGP, Statique) dans OSPF. Le routeur qui fait cela devient un ASBR.

Il faut toujours spécifier une métrique et un type de métrique :

metric-type 1 : Le coût externe est ajouté au coût interne OSPF.

metric-type 2 : Le coût externe est utilisé seul (par défaut).

cisco
router ospf 1
 redistribute static subnets metric 20 metric-type 1
 default-information originate
5. L'Authentification OSPF
Pour éviter qu'un pirate n'injecte de fausses routes, on active l'authentification (MD5 ou SHA).

cisco
interface GigabitEthernet0/1
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 MonMotDePasseSecret
6. Le Virtual Link
Si une aire n'est pas physiquement connectée à l'Area 0 (le backbone), on peut créer un lien virtuel à travers une autre aire.

cisco
router ospf 1
 area 1 virtual-link 2.2.2.2
(Le 2.2.2.2 est le Router-ID du routeur de l'autre côté du lien).

