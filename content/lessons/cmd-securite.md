# Sécurité & ACL (Access-lists, Port-security, DHCP Snooping)

> **Contexte d'utilisation :** fiche de sécurité de couche 2/3 pour des switches et routeurs Cisco. Les exemples bloquent ou autorisent des plages de documentation. Valide toujours les sources, destinations et impacts métier avant d'appliquer une ACL en production.

## 1. ACL : principes à garder en tête

Une ACL est une liste ordonnée de règles. Le routeur ou switch examine les entrées selon le type d'ACL et l'endroit où elle est appliquée. Une ACL se termine implicitement par un refus : si aucun ACE ne correspond, le trafic est rejeté. Cette règle explique de nombreuses pannes après une configuration apparemment correcte.

| Type | Correspondance typique | Usage |
|---|---|---|
| ACL standard numérotée ou nommée | Adresse IPv4 source | Contrôler une origine, souvent près de la destination |
| ACL étendue | Protocole, source, destination, ports selon le protocole | Filtrage précis, souvent près de la source |
| ACL VTY avec access-class | Sources d'administration | Limiter les adresses pouvant ouvrir une session sur les lignes |
| ACL IPv6 | Champs IPv6 selon la syntaxe disponible | Filtrage IPv6 ; ne pas recycler une ACL IPv4 |

## 2. Exemple d'ACL étendue IPv4

~~~~text
configure terminal
ip access-list extended USERS-TO-SERVERS
 remark Autoriser HTTPS vers le serveur d'exemple
 permit tcp 192.168.10.0 0.0.0.255 host 192.0.2.20 eq 443
 remark Bloquer le reste du flux vers ce serveur
 deny ip 192.168.10.0 0.0.0.255 host 192.0.2.20 log
 remark Conserver les autres destinations pour ce sous-réseau
 permit ip 192.168.10.0 0.0.0.255 any
!
interface Vlan10
 ip access-group USERS-TO-SERVERS in
end
show access-lists
show ip interface Vlan10
~~~~

Une ACL en entrée sur Vlan10 filtre le trafic reçu par cette interface L3. L'interface, la direction et la notion de source doivent être soigneusement vérifiées. Sur un routeur-on-a-stick, l'ACL peut se trouver sur une sous-interface ; sur un switch L3, elle peut être sur une SVI. Les options disponibles diffèrent selon la plateforme.

| Commande | Rôle |
|---|---|
| ip access-list extended NOM | Crée / édite une ACL nommée |
| permit / deny | Autorise ou refuse le trafic correspondant |
| remark | Documente l'intention |
| ip access-group NOM in / out | Applique l'ACL à une interface L3 |
| show access-lists | Affiche les entrées et compteurs de correspondance |
| show ip interface ... | Confirme les ACL attachées et leur direction |
| no ip access-list extended NOM | Supprime une ACL ; vérifier d'abord qu'elle n'est pas utilisée |

**Précaution :** ne remplace pas une ACL complète par un bloc minimal sans comprendre les autres flux requis. La dernière ligne de l'exemple autorise les autres destinations du sous-réseau ; supprime-la uniquement si une politique « refus par défaut » est prévue et que toutes les autorisations nécessaires sont énumérées.

## 3. ACL pour l'accès SSH aux VTY

~~~~text
ip access-list standard ADMIN-SSH
 permit 192.168.99.0 0.0.0.255
 deny any log
!
line vty 0 4
 access-class ADMIN-SSH in
 transport input ssh
 login local
~~~~

Autoriser le réseau d'administration prévu, pas simplement un grand sous-réseau parce qu'il est commode. Avant d'appliquer access-class, confirmer que l'IP source utilisée est bien dans la liste. Garder une console ou une voie d'accès de secours jusqu'au test d'une nouvelle session SSH.

## 4. Port-security sur un port d'accès

~~~~text
interface GigabitEthernet1/0/10
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
~~~~

| Option | Comportement |
|---|---|
| maximum 2 | Autorise jusqu'à deux adresses MAC sécurisées sur le port |
| mac-address sticky | Apprend et inscrit les MAC observées selon les règles de la plateforme |
| violation protect | Abandonne silencieusement les trames violant la limite |
| violation restrict | Abandonne les trames non conformes et compte/logue l'événement sans arrêter généralement le port |
| violation shutdown | Met le port en état d'erreur lors d'une violation, selon la plateforme |

Choisir le mode en fonction de la politique. Sticky ne veut pas dire qu'une MAC sera automatiquement correcte pour toujours : il faut gérer les changements légitimes, téléphones IP, docks, petits switches et virtualisation. Un port qui doit accepter plusieurs périphériques peut nécessiter une limite différente ou une autre méthode de contrôle.

~~~~text
show port-security
show port-security interface GigabitEthernet1/0/10
show port-security address
show interfaces status
~~~~

Si le port devient err-disabled, identifier la cause avant de le réactiver. La commande recovery ou shutdown/no shutdown ne constitue pas un correctif si le périphérique non autorisé est encore branché.

## 5. DHCP Snooping

DHCP Snooping aide à empêcher un serveur DHCP non autorisé de distribuer des paramètres réseau sur les VLAN protégés. Les ports faisant face aux serveurs DHCP légitimes ou aux relais nécessaires sont généralement marqués trusted ; les ports utilisateurs restent untrusted par défaut.

~~~~text
ip dhcp snooping
ip dhcp snooping vlan 10,20
!
interface GigabitEthernet1/0/48
 description Uplink-vers-serveur-DHCP-ou-relais-approuve
 ip dhcp snooping trust
!
interface range GigabitEthernet1/0/10-24
 ip dhcp snooping limit rate 15
~~~~

La commande trust est sensible : sur un port d'accès utilisateur, elle peut annuler une partie de la protection. La limite de débit doit être adaptée à la plateforme, au type de port et à la densité de clients. Certains déploiements nécessitent une base de bindings persistante et une attention à la haute disponibilité. Suivre la documentation de la version avant de l'activer sur un réseau qui utilise déjà DHCP.

~~~~text
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
~~~~

## 6. Renforts de couche 2 souvent associés

| Contrôle | Pourquoi | Vigilance |
|---|---|---|
| spanning-tree portfast sur ports edge | Accélère l'accès des hôtes finaux | Ne pas appliquer à un lien entre switches |
| spanning-tree bpduguard enable | Protège un port edge s'il reçoit une BPDU inattendue | Comprendre la réaction err-disabled |
| VLAN de gestion séparé | Isole les interfaces d'administration | Contrôler routage et ACL de management |
| Désactivation des ports inutilisés | Réduit la surface d'accès physique | Documenter les ports réservés |
| DAI / IP Source Guard si pris en charge | S'appuie souvent sur les bindings DHCP Snooping | Valider compatibilité, exceptions et statique |

## 7. Arbre de décision avant une règle de sécurité

~~~~text
Quel actif dois-je protéger ?
├─ Administration → ACL VTY, SSH, AAA, accès de secours
├─ Serveur / service IP → ACL étendue, sens et ports requis
└─ Accès de couche 2 → Port-security, DHCP Snooping, STP edge
   ├─ Port trusted absolument nécessaire ?
   │  └─ Non → rester untrusted
   └─ Flux légitimes documentés ?
      ├─ Non → inventorier et tester en lab
      └─ Oui → appliquer, compter les correspondances, surveiller
~~~~

**Bon réflexe :** prévoir une règle explicite, la documenter, vérifier les compteurs et le chemin retour, puis observer les journaux. Une ACL ne remplace pas AAA, le durcissement des comptes, les mises à jour ni la segmentation.
