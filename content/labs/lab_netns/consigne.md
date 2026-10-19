# Lab : routage entre namespaces (3 nœuds)

Trois namespaces réseau sont en place :

    ns-a --veth-a-- [veth-ra] ns-router [veth-rb] --veth-b-- ns-b

Aucune adresse IP n'est configurée. Le routage IP est déjà activé sur
ns-router : tout le travail porte sur l'adressage et les routes.
Le lien ns-a <-> ns-router porte le réseau 10.0.1.0/24, le lien
ns-router <-> ns-b porte le réseau 10.0.2.0/24.

Adressage attendu :
    ns-a      : veth-a  10.0.1.10/24
    ns-router : veth-ra 10.0.1.254/24
    ns-router : veth-rb 10.0.2.254/24
    ns-b      : veth-b  10.0.2.20/24

Objectif : que ns-a joigne ns-b (et inversement) à travers ns-router.

À faire :
1. Configurer les quatre adresses ci-dessus.
2. Donner à ns-a une route vers 10.0.2.0/24 via 10.0.1.254
   (ou une route par défaut via 10.0.1.254).
3. Faire de même pour ns-b via 10.0.2.254.
4. Vérifier avec ping.

Commandes (une par ligne, vide pour terminer) :
    ip netns exec ns-a ip addr add 10.0.1.10/24 dev veth-a
    ip netns exec ns-router ip addr add 10.0.1.254/24 dev veth-ra
    ip netns exec ns-router ip addr add 10.0.2.254/24 dev veth-rb
    ip netns exec ns-b ip addr add 10.0.2.20/24 dev veth-b
    ip netns exec ns-a ip route add default via 10.0.1.254
    ip netns exec ns-b ip route add default via 10.0.2.254
    ip netns exec ns-a ping -c 2 10.0.2.20

Note : `ip netns exec <ns> <cmd>` exécute <cmd> dans le namespace <ns>.
`ip route add default via <gw>` installe la route par défaut ; une route
plus spécifique (`ip route add 10.0.2.0/24 via 10.0.1.254`) convient aussi.