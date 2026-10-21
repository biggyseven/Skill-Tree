#!/bin/sh
set -e
ip netns exec r2 ping -c 1 -W 2 192.168.2.254 > /dev/null
echo "Incident resolu : la route est corrigee, le ping passe."
exit 0