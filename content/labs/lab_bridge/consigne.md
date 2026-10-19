# Lab : bridge Linux et connectivité L2

Deux namespaces (ns1, ns2) ont des IPs dans le même subnet 192.168.100.0/24,
mais le lien L2 entre eux n'est pas établi : les deux interfaces host
(veth1-b, veth2-b) sont down et ne sont pas attachées au bridge br-lab.

Objectif : faire communiquer ns1 et ns2 en attachant les deux veths au bridge.

À faire :
1. Attacher veth1-b au bridge br-lab
2. Attacher veth2-b au bridge br-lab
3. Mettre veth1-b et veth2-b up
4. Vérifier avec ping

Commandes utiles :
    ip link set <if> master br-lab
    ip link set <if> up
    ip netns exec ns1 ping -c 2 192.168.100.2