# Dépannage réseau — Méthode, outils et cas réels (CCNA / Admin Réseau)

> **Objectif** : acquérir une méthode reproductible pour diagnostiquer les pannes réseau, de la couche physique à l'application. Le cours couvre les outils Cisco et Linux, l'analyse de captures, les symptômes typiques, les pannes intermittentes et la documentation d'incident. Il vise la pratique : chaque section se termine par des commandes et une décision.

---

## 1. La méthode avant les commandes

Un bon technicien ne tape pas des commandes au hasard. Il suit une démarche :

1. **Définir le problème** : qui, quoi, où, quand, depuis quand ?
2. **Collecter les faits** : adresses, VLAN, routes, logs, heure, changements récents.
3. **Délimiter** : un poste, un VLAN, un site, un service ?
4. **Formuler une hypothèse** : couche physique, L2, L3, DNS, firewall, application.
5. **Tester** : une variable à la fois, avec un test reproductible.
6. **Corriger** : changement minimal, réversible.
7. **Vérifier** : le test initial passe, pas de régression.
8. **Documenter** : cause racine, correctif, prévention.

```text
Symptôme -> Faits -> Hypothèses -> Tests -> Correctif -> Vérification
   ^                                                  |
   +------------------ documentation ----------------+
```

### 1.1 Questions à poser

- Qu'est-ce qui a changé ? (mise à jour, câble, VLAN, ACL, DNS)
- Le problème est-il permanent ou intermittent ?
- Touche-t-il un poste, un subnet, un site, un service ?
- Le ping IP fonctionne-t-il ? Le DNS ? Le port TCP ?
- Y a-t-il un message d'erreur exact ?
- Depuis quand ? À quelle heure ?
- D'autres utilisateurs sont-ils affectés ?

### 1.2 Ne pas confondre corrélation et cause

Un utilisateur signale une panne après une mise à jour. La mise à jour est un suspect, pas une preuve. Il faut vérifier les logs, les changements de configuration et les tests. Une panne peut venir d'un câble débranché au même moment.

---

## 2. Les couches et les symptômes

| Couche | Symptômes typiques | Outils |
|---|---|---|
| 1 Physique | Pas de lien, erreurs CRC, lenteur | `ip link`, `ethtool`, `show interfaces` |
| 2 Liaison | VLAN, MAC, STP, boucle | `show vlan`, `show mac`, `bridge` |
| 3 Réseau | Pas de ping, pas de route | `ip route`, `show ip route`, `traceroute` |
| 4 Transport | Port fermé, timeout | `nc`, `ss`, `telnet`, `nmap` |
| 5-7 Application | DNS, HTTP, TLS, auth | `dig`, `curl`, `openssl`, logs |

### 2.1 Approche bottom-up

Commencer par la couche 1 et remonter. Adaptée aux problèmes physiques et aux nouveaux câblages.

### 2.2 Approche top-down

Commencer par l'application et descendre. Adaptée aux services et aux utilisateurs finaux.

### 2.3 Divide and conquer

Tester au milieu (ping passerelle, ping serveur) et diviser l'espace de recherche. Souvent la plus rapide.

---

## 3. Outils de base

### 3.1 ping

```bash
ping -c 4 10.10.1.1
ping -c 4 10.20.2.20
ping -M do -s 1472 10.20.2.20
ping -I eth0 10.20.2.20
```

```cisco
ping 10.20.2.20
ping 10.20.2.20 source Gi0/0
ping 10.20.2.20 size 1500 df-bit
```

Le ping teste ICMP echo, pas TCP. Un ping qui échoue ne prouve pas que le service est down ; un ping qui réussit ne prouve pas que le port 443 est ouvert.

### 3.2 traceroute / mtr

```bash
traceroute -n 10.20.2.20
mtr -rw 10.20.2.20
```

```cisco
traceroute 10.20.2.20
```

`traceroute` montre le chemin et les pertes. `mtr` combine ping et traceroute en continu.

### 3.3 ss / netstat

```bash
ss -tulpn
ss -tnp
ss -tn state established
ss -s
```

`ss` remplace `netstat` pour les sockets. Vérifier l'écoute, les connexions et les queues.

### 3.4 dig / nslookup

```bash
dig example.com
dig +short example.com
dig @10.10.1.53 example.com
dig +trace example.com
```

### 3.5 curl / openssl

```bash
curl -vk https://example.com
curl -v --resolve example.com:443:10.20.2.20 https://example.com
openssl s_client -connect example.com:443 -servername example.com
```

`curl` teste HTTP/HTTPS, les proxies, les certificats. `openssl s_client` examine TLS.

### 3.6 tcpdump

```bash
tcpdump -eni eth0
tcpdump -eni eth0 host 10.20.2.20
tcpdump -eni eth0 port 443
tcpdump -eni eth0 -w capture.pcap
tcpdump -r capture.pcap -nn
```

Toujours capturer **aux deux extrémités** si possible. Une capture d'un seul côté peut faire croire à une perte alors que le paquet n'a jamais été envoyé.

### 3.7 nmap

```bash
nmap -Pn -p 22,80,443 10.20.2.20
nmap -sT -p- 10.20.2.20
```

Utiliser uniquement sur des réseaux autorisés.

---

## 4. Outils Cisco

```cisco
show interfaces
show interfaces status
show interfaces counters errors
show ip interface brief
show ip route
show ip route 10.20.2.20
show arp
show mac address-table
show vlan brief
show interfaces trunk
show spanning-tree
show logging
show processes cpu
show processes memory
show cdp neighbors
show lldp neighbors
```

### 4.1 Vérifications rapides

```text
1. show ip interface brief   -> interfaces up/up, IP correcte
2. show interfaces status     -> vitesse, duplex, VLAN
3. show ip route <dest>       -> route présente
4. show arp                   -> next-hop résolu
5. ping <next-hop>            -> L2/L3 locale
6. show logging               -> erreurs récentes
```

### 4.2 Logs

```cisco
show logging
show logging | include ERROR
show logging | include LINK
terminal monitor
```

Configurer un syslog centralisé pour conserver les logs après redémarrage.

---

## 5. Diagnostic par symptôme

### 5.1 Pas de lien

```bash
ip link show eth0
ethtool eth0
```

```cisco
show interfaces status
show interfaces Gi0/1
show interfaces transceiver
```

Causes : câble, SFP, port shutdown, vitesse, err-disable, mauvais VLAN, alimentation.

### 5.2 Lien up, pas de ping

1. IP/masque corrects ?
2. VLAN correct ?
3. Passerelle correcte ?
4. ARP résolu ?
5. Route de retour ?
6. ACL/firewall ?
7. NAT ?

### 5.3 Ping OK, service KO

Le réseau IP fonctionne. Vérifier :

```bash
nc -vz 10.20.2.20 443
curl -vk https://10.20.2.20/
ss -tulpn | grep 443
```

Causes : service arrêté, port non écouté, firewall, TLS, proxy, DNS.

### 5.4 DNS KO

```bash
dig example.com
dig @10.10.1.53 example.com
cat /etc/resolv.conf
```

Si `dig @IP` fonctionne mais `dig` sans serveur échoue, le resolver local est mal configuré.

### 5.5 Lent mais fonctionnel

- duplex mismatch ;
- congestion ;
- MTU/fragmentation ;
- retransmissions TCP ;
- DNS lent ;
- perte de paquets ;
- saturation d'un uplink.

```bash
ping -c 100 10.20.2.20
mtr -rw 10.20.2.20
ss -ti
tcpdump -eni eth0 tcp
```

### 5.6 Intermittent

Les pannes intermittentes sont les plus difficiles. Chercher :

- erreurs CRC qui augmentent ;
- STP qui change ;
- roaming Wi-Fi ;
- ARP flapping ;
- route qui bascule ;
- pool DHCP épuisé ;
- bail DNS qui expire ;
- saturation à certaines heures.

Surveiller dans le temps avec des compteurs et des logs, pas seulement un test ponctuel.

---

## 6. Analyse de capture

### 6.1 Un ping qui échoue

```text
Source -> Dest : ICMP echo request
Dest -> Source : ICMP echo reply
```

Si la requête part mais pas de réponse, le problème est après la source. Si la requête n'arrive pas à la destination, le problème est entre les deux. Si la réponse part mais n'arrive pas, le retour est bloqué.

### 6.2 TCP handshake

```text
Client -> Serveur : SYN
Serveur -> Client : SYN-ACK
Client -> Serveur : ACK
```

- Pas de SYN-ACK : port fermé, firewall, route retour.
- SYN-ACK mais pas d'ACK : client, MTU, firewall.
- Reset : service ou firewall.

### 6.3 Retransmissions

```bash
ss -ti
tcpdump -eni eth0 tcp
```

Des retransmissions fréquentes indiquent une perte, un MTU ou une congestion.

### 6.4 DNS

```bash
tcpdump -eni eth0 port 53
```

Vérifier la requête, la réponse, le code (NOERROR, NXDOMAIN, SERVFAIL) et le TTL.

---

## 7. Cas réels

### 7.1 Cas 1 : le nouveau VLAN ne fonctionne pas

Un VLAN 30 est créé, mais les postes ne ping pas la passerelle. `show vlan brief` montre le VLAN, mais le port est resté en VLAN 1. `show interfaces switchport` confirme. Correction : `switchport access vlan 30`. Vérification : `show vlan brief`, ping.

### 7.2 Cas 2 : le trunk n'autorise pas le VLAN

Le VLAN 30 existe sur les deux switches, mais le trunk n'autorise que 10,20. `show interfaces trunk` montre la liste. Correction : `switchport trunk allowed vlan add 30`. Vérification : MAC table et ping.

### 7.3 Cas 3 : passerelle absente

Les postes ont une IP, mais pas de passerelle. `ip route` est vide. Correction : ajouter la route par défaut ou corriger l'option DHCP 3.

### 7.4 Cas 4 : route de retour manquante

Le ping aller arrive au serveur, mais le serveur n'a pas de route vers le client. `traceroute` depuis le serveur échoue. Correction : ajouter la route ou corriger le routage.

### 7.5 Cas 5 : duplex mismatch

Le lien est up, mais les transferts sont lents et les CRC augmentent. `show interfaces` indique `half-duplex` d'un côté, `full-duplex` de l'autre. Correction : aligner vitesse et duplex, ou laisser l'auto-négociation des deux côtés.

### 7.6 Cas 6 : boucle STP

Le réseau tombe après l'ajout d'un switch. Les LED clignotent, le CPU est à 100 %. `show spanning-tree` montre un root inattendu. Correction : débrancher le lien en boucle, activer STP et BPDU Guard.

### 7.7 Cas 7 : MTU

Les petits paquets passent, les gros échouent. `ping -M do -s 1472` passe, `-s 1473` échoue. Correction : aligner le MTU ou ajuster le MSS.

### 7.8 Cas 8 : DNS interne

Les utilisateurs internes résolvent `app.example.com` vers l'IP publique et sortent, mais le retour est bloqué. Correction : split DNS ou hairpin NAT.

### 7.9 Cas 9 : pool DHCP épuisé

Les nouveaux postes prennent une APIPA. `show ip dhcp pool` montre 100 %. Correction : agrandir le pool, réduire le bail, ajouter un VLAN.

### 7.10 Cas 10 : certificat TLS expiré

Le navigateur affiche une erreur, mais `ping` et `curl -k` fonctionnent. `openssl s_client` montre la date d'expiration. Correction : renouveler le certificat et vérifier la chaîne.

---

## 8. Documentation d'incident

Un bon ticket contient :

```text
Titre :
Impact :
Début / fin :
Symptômes :
Environnement :
Changements récents :
Tests effectués :
Cause racine :
Correctif :
Vérification :
Prévention :
```

### 8.1 Exemple

```text
Titre : VLAN 30 inaccessible après migration
Impact : 40 postes, service interne indisponible
Début : 2024-06-12 09:15
Symptômes : APIPA, ping passerelle KO
Cause : port d'accès resté en VLAN 1
Correctif : switchport access vlan 30
Vérification : 40 postes pingent la passerelle et le service
Prévention : check-list de migration VLAN
```

---

## 9. Prévention

- sauvegardes de configuration ;
- supervision (SNMP, syslog, NetFlow) ;
- alertes sur erreurs CRC, CPU, voisinages ;
- tests de convergence ;
- documentation à jour ;
- changements planifiés et réversibles ;
- accès de secours (console, OOB) ;
- formation et revue de configuration.

---

## 10. Laboratoire

1. Simuler un duplex mismatch et observer les compteurs.
2. Créer une boucle L2 et vérifier STP.
3. Configurer un trunk sans le VLAN 30 et diagnostiquer.
4. Ajouter une ACL qui bloque le retour et corriger.
5. Capturer un handshake TCP et identifier un port fermé.
6. Configurer un MTU différent et tester avec `ping -M do`.

---

## 11. Mémo

```bash
ip -br addr
ip route
ip neigh
ss -tulpn
dig +short example.com
curl -vk https://example.com
tcpdump -eni eth0
mtr -rw 10.20.2.20
```

```cisco
show ip interface brief
show interfaces status
show ip route
show arp
show vlan brief
show interfaces trunk
show spanning-tree
show logging
```

---

## 12. Points clés

- Une méthode vaut mieux que des commandes aléatoires.
- Tester couche par couche, puis dans les deux sens.
- `ping` ne teste pas TCP ; `curl`/`nc` testent le service.
- Une capture aux deux extrémités évite les fausses conclusions.
- Les pannes intermittentes exigent des mesures dans le temps.
- La documentation et la prévention font partie du dépannage.
- Toujours vérifier le retour, le DNS, le MTU et les ACL.
- Un changement à la fois, avec un plan de rollback.

> **Exercice** : un utilisateur ne joint pas `https://app.example.com`, mais `ping app.example.com` fonctionne. Donnez trois causes et les commandes de vérification. Réponse : service arrêté (`ss -tulpn`), firewall (`nc -vz`), certificat/TLS (`openssl s_client`), proxy (`curl -v`), DNS (`dig`).

---

## 13. Dépannage Wi-Fi

Le Wi-Fi ajoute des causes physiques et de couche 2 que le filaire ne connaît pas : interférences, couverture, roaming, canaux, authentification.

### 13.1 Symptômes et causes

| Symptôme | Causes probables |
|---|---|
| Association impossible | Mot de passe, RADIUS, SSID, bande, 802.1X |
| IP absente | DHCP, VLAN, relais, pool épuisé |
| Débit faible | Signal, interférence, canal, nb clients |
| Déconnexions | Roaming, couverture, puissance, driver |
| Ping intermittent | Air congestionné, retransmissions, roaming |
| Un seul site KO | Contrôleur, tunnel, VLAN, DHCP |

### 13.2 Commandes client

```bash
nmcli device wifi list
nmcli connection show
iw dev wlan0 link
iw dev wlan0 station dump
ip -s link show wlan0
resolvectl status
```

### 13.3 Diagnostic contrôleur

```cisco
show ap summary
show ap name <AP> config general
show client summary
show client detail <MAC>
show wlan summary
show sysinfo
```

Vérifier le RSSI, le SNR, le canal, la puissance, le taux de retransmission et le roaming. Un signal à −75 dBm peut fonctionner mais être instable ; viser −65 dBm ou mieux.

### 13.4 Canaux et interférences

En 2,4 GHz, seuls les canaux 1, 6 et 11 sont non chevauchants. En 5 GHz, privilégier les canaux larges (40/80 MHz) avec une puissance adaptée. Un canal trop large réduit la portée et augmente les interférences.

### 13.5 Roaming

Un client qui reste accroché à un AP lointain provoque lenteur et déconnexions. Le contrôleur peut utiliser `11k/11v/11r`, un seuil RSSI et une puissance minimale. Vérifier que le client supporte ces fonctions.

### 13.6 Cas réel : Wi-Fi OK, pas d'IP

Le client s'associe mais reste en APIPA. Le VLAN du SSID n'a pas de relais DHCP. Correction : ajouter `ip helper-address` sur l'interface du VLAN ou corriger le mapping SSID/VLAN.

---

## 14. Supervision et observabilité

Le dépannage réactif ne suffit pas. La supervision permet de détecter les signaux faibles avant la panne.

### 14.1 Métriques à surveiller

- erreurs CRC et drops sur les interfaces ;
- CPU et mémoire des équipements ;
- température et alimentation ;
- voisinages OSPF/BGP ;
- utilisation des pools DHCP ;
- latence et perte vers les services critiques ;
- certificats TLS (expiration) ;
- logs d'erreur et de sécurité ;
- saturation des liens.

### 14.2 SNMP

```cisco
snmp-server community RO_MONITOR ro
snmp-server host 10.10.99.20 version 2c RO_MONITOR
snmp-server enable traps
```

Sous Linux :

```bash
snmpwalk -v2c -c public 10.10.1.1 1.3.6.1.2.1.2.2.1
```

### 14.3 Syslog

```cisco
logging host 10.10.99.20
logging trap informational
logging source-interface Loopback0
```

Centraliser les logs permet de corréler un incident avec un changement.

### 14.4 NetFlow / IPFIX

```cisco
interface Gi0/0
 ip flow ingress
!
ip flow-export destination 10.10.99.20 2055
ip flow-export version 9
```

NetFlow montre qui parle à qui, sur quel port, et combien. C'est précieux pour les incidents de congestion.

### 14.5 Alertes utiles

- plus de 10 CRC/min sur un lien ;
- voisin OSPF/BGP down ;
- pool DHCP > 90 % ;
- certificat < 30 jours ;
- perte > 1 % vers le cœur ;
- CPU > 80 % pendant 5 min.

---

## 15. Cas réels supplémentaires

### 15.1 Cas 11 : adresse IP en conflit

Deux postes ont la même IP. Le réseau fonctionne par intermittence, l'ARP flappe. `show arp` et `arping` révèlent deux MAC. Correction : réserver l'IP ou corriger la configuration statique, puis `clear arp-cache`.

### 15.2 Cas 12 : route asymétrique et firewall

Le retour passe par un autre firewall qui n'a pas l'état de la connexion. Le TCP est bloqué. `traceroute` dans les deux sens le montre. Correction : symétriser le routage ou utiliser un firewall stateful actif-actif avec synchronisation.

### 15.3 Cas 13 : épuisement de connexions NAT

Un serveur fait beaucoup de connexions sortantes. La table NAT est pleine, les nouvelles connexions échouent. `show ip nat statistics` montre l'utilisation. Correction : augmenter la plage de ports, répartir sur plusieurs IP publiques, ou réduire les connexions inutiles.

### 15.4 Cas 14 : spanning-tree et lien fibre unidirectionnel

Un lien fibre reçoit mais n'émet pas. STP ne voit pas de BPDU et active le port, créant une boucle. UDLD détecte le lien unidirectionnel et désactive le port. Vérifier les optiques et les connecteurs.

### 15.5 Cas 15 : DNS qui répond mais mauvais résultat

Le resolver renvoie une ancienne IP à cause d'un cache ou d'un TTL long. `dig` montre le TTL restant. Correction : attendre l'expiration, vider le cache, ou corriger la zone. Pour un changement planifié, baisser le TTL avant.

### 15.6 Cas 16 : certificat interne non approuvé

Le navigateur affiche un avertissement, mais `curl -k` fonctionne. La chaîne intermédiaire manque. Correction : installer la CA interne sur les clients ou fournir la chaîne complète sur le serveur.

---

## 16. Check-list de dépannage

```text
[ ] Symptôme décrit précisément
[ ] Impact et périmètre identifiés
[ ] Changements récents vérifiés
[ ] Lien physique et vitesse/duplex
[ ] VLAN et trunk
[ ] Adresse IP, masque, passerelle
[ ] ARP/NDP
[ ] Route aller et retour
[ ] DNS
[ ] Port TCP/UDP et service
[ ] Firewall/ACL/NAT
[ ] Capture aux deux extrémités
[ ] Logs et compteurs
[ ] Correctif testé
[ ] Documentation mise à jour
```

---

## 17. Post-mortem

Après un incident majeur, organiser un post-mortem sans blâme :

1. chronologie factuelle ;
2. impact ;
3. cause racine ;
4. facteurs contributifs ;
5. ce qui a bien fonctionné ;
6. actions correctives avec propriétaires et dates ;
7. mise à jour de la documentation et des tests.

Un post-mortem utile produit des changements concrets, pas seulement un document.

---

## 18. Synthèse

Le dépannage réseau est une discipline de raisonnement. Les commandes changent selon les constructeurs, mais la méthode reste : définir, observer, isoler, tester, corriger, vérifier. Les pannes les plus fréquentes sont rarement exotiques : câble, VLAN, passerelle, route de retour, DNS, ACL, MTU. Savoir les éliminer méthodiquement vaut mieux que connaître mille commandes par cœur.
