# Routage & OSPF (Routes statiques, OSPF, EIGRP)

> **Contexte d'utilisation :** aide-mémoire Cisco IOS / IOS XE pour dépanner la sélection de routes et établir un routage statique ou dynamique. Les adresses 192.0.2.0/24 et 198.51.100.0/24 sont réservées à la documentation ; remplace-les avant tout usage réel.

## 1. Lecture rapide de la table de routage

~~~~text
show ip interface brief
show ip route
show ip route 192.0.2.10
show ip protocols
show arp
show running-config | section router
~~~~

Codes habituels de show ip route :

| Code | Signification |
|---|---|
| C | Réseau connecté |
| L | Adresse locale d'une interface |
| S | Route statique |
| O | Route OSPF intra-area ou inter-area |
| O IA | Route inter-area OSPF |
| D | Route EIGRP interne |
| EX | Route EIGRP externe |
| * | Route candidate par défaut lorsqu'affichée avec l'entrée concernée |

La table installée est la référence pour le transfert de paquets, mais show ip route ne remplace pas show ip protocols et les commandes de voisinage. Si une route n'apparaît pas, vérifier l'interface, la présence de la route chez le voisin, les filtres, la préférence de source et la joignabilité du next-hop.

## 2. Routes statiques

~~~~text
! Route vers un réseau via le prochain saut
ip route 192.0.2.0 255.255.255.0 198.51.100.2

! Route via une interface de sortie (surtout lien point-à-point)
ip route 192.0.2.0 255.255.255.0 Serial0/0/0

! Route par défaut via le routeur amont
ip route 0.0.0.0 0.0.0.0 198.51.100.1

! Retirer une route exacte
no ip route 192.0.2.0 255.255.255.0 198.51.100.2
~~~~

Une route statique avec next-hop est souvent plus explicite sur Ethernet. Une route uniquement liée à une interface Ethernet peut provoquer une résolution ARP pour de nombreuses destinations et n'est généralement pas le choix approprié pour un réseau multi-accès. La forme adaptée dépend du type de lien, de la plateforme et du plan de routage.

| Besoin | Choix |
|---|---|
| Petit réseau stable | Statique, simple à documenter |
| Sortie Internet unique | Route par défaut vers le routeur amont |
| Route de secours | Route flottante avec distance administrative supérieure |
| Plusieurs chemins et adaptation automatique | Protocole dynamique selon le design |

Avant une modification distante, vérifier qu'une route ne remplace pas celle utilisée pour ton propre accès d'administration. Prévoir une route de retour, pas seulement le chemin aller.

## 3. OSPF : configuration minimale

Exemple pour un routeur de lab ayant les réseaux connectés 10.10.10.0/24 et 10.10.20.0/24 dans l'area 0 :

~~~~text
configure terminal
router ospf 10
 router-id 1.1.1.1
 passive-interface default
 no passive-interface GigabitEthernet0/1
 network 10.10.10.0 0.0.0.255 area 0
 network 10.10.20.0 0.0.0.255 area 0
end
~~~~

Le numéro 10 est un identifiant de processus local, pas nécessairement le même chez tous les routeurs. Le router-id doit être unique dans le domaine OSPF. Les commandes network avec wildcard sélectionnent les interfaces dont l'adresse correspond ; les règles exactes peuvent dépendre du contexte. Sur les versions qui le permettent, la configuration OSPF directement sous interface peut être plus lisible.

Utiliser passive-interface par défaut limite les adjacences sur les interfaces où aucun voisin ne doit exister. Retirer le mode passif uniquement sur les liens de routage attendus. Une interface passive peut annoncer son réseau sans envoyer d'Hello OSPF sur ce lien.

### Contrôle OSPF

~~~~text
show ip ospf
show ip ospf neighbor
show ip ospf interface brief
show ip ospf database
show ip route ospf
show ip protocols
~~~~

Les voisins ne deviennent adjacents que si des paramètres requis concordent : connectivité IP, area, type de réseau, timers, authentification éventuelle, MTU selon les cas et paramètres de sécurité. Router-id dupliqué, ACL, passive-interface ou mauvaise wildcard sont des causes classiques. L'état FULL est habituel sur plusieurs types de liens, mais les états attendus diffèrent selon l'élection DR/BDR et le type de réseau.

## 4. EIGRP : rappel de configuration

Syntaxe classique, si EIGRP est autorisé par l'architecture :

~~~~text
router eigrp 100
 network 10.10.10.0 0.0.0.255
 network 10.10.20.0 0.0.0.255
 passive-interface default
 no passive-interface GigabitEthernet0/1
~~~~

Le numéro 100 est l'AS EIGRP du domaine et doit être cohérent entre voisins en mode classique. Les plateformes modernes peuvent utiliser la configuration EIGRP nommée, dont la syntaxe diffère. Ne pas copier une configuration classique dans un contexte nommé sans l'adapter.

~~~~text
show ip eigrp neighbors
show ip eigrp topology
show ip protocols
show ip route eigrp
~~~~

EIGRP utilise notamment la bande passante et le délai dans sa métrique par défaut. Une route de voisin peut être présente dans la topologie sans être la route installée si une meilleure route est retenue ou si les règles de faisabilité ne sont pas satisfaites. Examiner les voisins, la topologie et la table de routage ensemble.

## 5. Notions à ne pas confondre

| Notion | Utilité |
|---|---|
| Préfixe + masque | Décrit les destinations couvertes |
| Next-hop | Adresse du prochain routeur à joindre |
| Distance administrative (AD) | Préférence entre sources de routes différentes sur un même routeur |
| Métrique | Coût calculé par un protocole pour comparer des chemins de ce protocole |
| Wildcard | Masque inversé utilisé notamment par les commandes network OSPF/EIGRP classiques |
| Route de retour | Chemin de retour vers la source ; souvent oublié dans le dépannage |

La valeur de métrique OSPF ne se compare pas directement à une métrique EIGRP. La distance administrative n'est pas une mesure de performance : c'est un mécanisme local de préférence. Plusieurs routes identiques peuvent être installées en équilibrage si les règles et la plateforme le permettent.

## 6. Arbre de diagnostic d'une route manquante

~~~~text
La route est-elle dans show ip route ?
├─ Oui → vérifier next-hop, interface de sortie, ACL et route retour
└─ Non
   ├─ Le réseau est-il connecté et up/up ?
   │  └─ Non → corriger interface / IP / masque
   ├─ Une route statique existe-t-elle ?
   │  └─ Non → vérifier syntaxe, next-hop et réseau de destination
   └─ Protocole dynamique ?
      ├─ Pas de voisin → IP, area/AS, timers, passive-interface, ACL
      ├─ Voisin actif mais route absente → annonce, wildcard, filtre, résumé
      └─ Route reçue mais non installée → AD, meilleure route, next-hop
~~~~

**Règle d'exploitation :** sauvegarder la configuration précédente, annoncer précisément le préfixe requis, vérifier la table de routage et tester dans les deux sens après chaque changement.
