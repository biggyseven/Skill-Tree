# INCIDENT 01 : Le routeur muet

**Alerte critique** : Le reseau 192.168.2.0/24 est injoignable depuis le routeur R2.

Les interfaces sont UP et les adresses IP sont correctes.
A toi de trouver pourquoi le trafic ne passe pas et de corriger le probleme.

**Indice** : Regarde la table de routage de R1 (`ip netns exec r1 ip route`).