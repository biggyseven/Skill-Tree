#!/bin/sh
set -e

# Les deux ports doivent être membres du bridge...
ip link show veth1-b | grep -q "master br-lab"
ip link show veth2-b | grep -q "master br-lab"

# ...et le trafic doit réellement passer.
ip netns exec ns1 ping -c 1 -W 2 192.168.100.2 > /dev/null

echo "L2 établi, ping OK"
exit 0