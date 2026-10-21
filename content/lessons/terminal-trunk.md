# Aide-mémoire : Restriction de VLAN sur un Trunk (Cisco)

Pour n'autoriser que les VLANs 10 et 20 à passer sur un lien Trunk :
```cisco
Switch(config-if)# switchport trunk allowed vlan 10,20
``` 
**Commande attendue :** `switchport trunk allowed vlan 10,20`
