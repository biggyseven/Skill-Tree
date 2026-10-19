#!/bin/sh
set -e

# Aller : ns-a -> ns-b en passant par ns-router
ip netns exec ns-a ping -c 1 -W 2 10.0.2.20 > /dev/null
echo "ns-a peut joindre ns-b via ns-router"

# Retour : ns-b -> ns-a, ce qui valide la passerelle de ns-b
ip netns exec ns-b ping -c 1 -W 2 10.0.1.10 > /dev/null
echo "ns-b peut joindre ns-a via ns-router"

exit 0