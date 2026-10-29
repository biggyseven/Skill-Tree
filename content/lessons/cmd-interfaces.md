# Interfaces & VLANs (Switchport, Trunk, Router-on-a-stick)

> **Contexte d'utilisation :** référence rapide pour configurer des ports d'accès, des trunks 802.1Q et un routage inter-VLAN. Les exemples utilisent des VLAN 10, 20 et 99 ; adapte les identifiants, ports, IP et règles à ton plan d'adressage.

## 1. Créer les VLAN et configurer les ports d'accès

~~~~text
enable
configure terminal
vlan 10
 name UTILISATEURS
vlan 20
 name SERVEURS
vlan 99
 name MANAGEMENT
!
interface GigabitEthernet1/0/10
 description Poste-equipe-A
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
!
interface range GigabitEthernet1/0/11-12
 description Postes-equipe-B
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
end
copy running-config startup-config
~~~~

PortFast est destiné aux ports de périphériques finaux, pas à un lien entre switches. BPDU Guard protège un port edge contre la réception inattendue de BPDU ; selon la politique STP, une violation peut placer le port en état err-disabled. Ne pas l'activer aveuglément sur des ports connectés à des switches, bridges ou hyperviseurs qui émettent des BPDU.

## 2. Commandes de consultation

| Commande | Utilité |
|---|---|
| show vlan brief | VLAN existants, statut et ports d'accès associés |
| show interfaces status | État, VLAN, duplex, vitesse et type de ports |
| show interfaces Gi1/0/10 switchport | Mode administratif/opérationnel et VLAN du port |
| show interfaces Gi1/0/10 | Erreurs, vitesse, duplex, compteurs et état physique |
| show mac address-table dynamic | Associations MAC / VLAN / port apprises |
| show spanning-tree vlan 10 | État STP et rôle des ports pour un VLAN |
| show interfaces trunk | Trunks actifs, VLAN autorisés et VLAN natif |
| show running-config interface Gi1/0/10 | Configuration appliquée à un port |

## 3. Trunk 802.1Q entre switches

~~~~text
configure terminal
interface GigabitEthernet1/0/48
 description Uplink-vers-SW-DIST-01
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,99
 no shutdown
end
show interfaces trunk
show interfaces GigabitEthernet1/0/48 switchport
~~~~

Sur de nombreux switches Catalyst modernes, le trunk utilise 802.1Q par défaut et la commande switchport trunk encapsulation dot1q n'existe pas. Sur d'anciennes plateformes multi-encapsulation, elle peut être nécessaire avant switchport mode trunk. Toujours confirmer la syntaxe pour le modèle et l'IOS.

- Les deux extrémités doivent avoir une configuration compatible.
- Le VLAN natif doit être cohérent des deux côtés ; un décalage peut entraîner des erreurs de segmentation et des alertes.
- Limiter allowed vlan aux VLAN réellement nécessaires, en prévoyant les VLAN de gestion et de supervision requis.
- Les VLAN autorisés administrativement ne sont pas forcément tous actifs ou autorisés en pratique sur le chemin : vérifier le trunk et STP.
- Une configuration trunk ne crée pas automatiquement le routage entre VLAN.

## 4. Router-on-a-stick

Cette architecture transporte plusieurs VLAN sur un même lien physique vers un routeur. Chaque sous-interface du routeur reçoit une encapsulation 802.1Q et une adresse IP servant généralement de passerelle du VLAN.

~~~~text
! Sur le switch : port relié au routeur
interface GigabitEthernet1/0/1
 description Vers-R1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 no shutdown

! Sur R1 : interface physique et sous-interfaces
interface GigabitEthernet0/0
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
!
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99 native
 ip address 192.168.99.1 255.255.255.0
~~~~

Le mot-clé native ne doit être utilisé que si le VLAN natif du trunk est bien celui prévu. Il existe une dépendance importante : l'interface physique doit être active, les VLAN doivent exister côté switch, les VLAN doivent être autorisés sur le trunk et les adresses doivent correspondre au plan IP. Le routage entre VLAN doit être activé sur le routeur si nécessaire.

Sur un switch de couche 3, une solution différente est possible avec des interfaces VLAN (SVI) et ip routing :

~~~~text
ip routing
interface vlan 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
interface vlan 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
~~~~

Une SVI peut rester down si le VLAN n'existe pas, si aucun port actif ne lui permet de monter, ou selon les conditions de la plateforme. Vérifie l'état réel au lieu de conclure à une faute d'adressage.

## 5. Vérifications rapides

~~~~text
show vlan brief
show interfaces trunk
show spanning-tree vlan 10
show mac address-table dynamic vlan 10
show ip interface brief
show ip route connected
ping 192.168.10.1
~~~~

| Symptôme | Causes probables |
|---|---|
| Poste sans réseau local | Mauvais VLAN access, port down, câblage, négociation, port err-disabled |
| VLAN fonctionne sur un switch mais pas sur un autre | VLAN absent, non autorisé sur un trunk, STP ou native VLAN incohérent |
| Poste joint sa passerelle mais pas un autre VLAN | Routage inter-VLAN, ACL, masque ou route retour |
| Sous-interface du routeur injoignable | Interface physique, encapsulation, VLAN sur le switch ou adresse IP |
| Une SVI reste down/down | VLAN absent/inactif ou aucune condition de port actif répondant aux règles de la plateforme |
| Erreurs d'interface qui augmentent | Câble, optique, vitesse/duplex, congestion ou défaut matériel |

## 6. Arbre de décision : isoler le problème

~~~~text
Le lien physique est-il up/up ?
├─ Non → câble, transceiver, shutdown, vitesse et erreurs
└─ Oui
   ├─ Port access : VLAN attendu ?
   │  └─ Non → corriger switchport access vlan
   └─ Trunk : VLAN présent et autorisé aux deux bouts ?
      ├─ Non → créer/autoriser le VLAN, comparer le trunk
      └─ Oui
         ├─ MAC apprise dans le bon VLAN ?
         │  └─ Non → vérifier émission du terminal et STP
         └─ Passerelle joignable ?
            ├─ Non → SVI/sous-interface, IP, masque
            └─ Oui → routage, ACL et route de retour
~~~~

**À retenir :** VLAN = segmentation de couche 2 ; trunk = transport de plusieurs VLAN ; SVI ou sous-interface = point de couche 3. Vérifie les trois séparément.
