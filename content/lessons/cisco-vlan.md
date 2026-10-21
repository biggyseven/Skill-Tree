# Aide-mémoire : Configuration VLAN (Cisco)

Pour configurer un port en mode Trunk (pour transporter plusieurs VLANs) :
```cisco
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
``` 
**Commande attendue :** `switchport mode trunk`
