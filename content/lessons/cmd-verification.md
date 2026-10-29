# Vérification & Diagnostic (Show, Debug, Ping, Traceroute)

> **Contexte d'utilisation :** ordre de diagnostic pour un incident Cisco IOS / IOS XE. Commence par des commandes non intrusives, formule une hypothèse, collecte des preuves et n'active les debugs qu'avec un périmètre et une fenêtre de temps maîtrisés.

## 1. Première collecte : état général

~~~~text
show clock
show version
show inventory
show running-config
show ip interface brief
show interfaces status
show logging
show processes cpu sorted
~~~~

| Commande | Indication principale |
|---|---|
| show version | Version logicielle, uptime, plateforme, redémarrages |
| show inventory | Matériel et composants déclarés par la plateforme |
| show running-config | Configuration active |
| show startup-config | Configuration prévue après redémarrage |
| show ip interface brief | IP et états administratifs / opérationnels L3 |
| show interfaces status | État et paramètres rapides des ports de switch |
| show interfaces Gi1/0/1 | Compteurs, vitesse, duplex, erreurs, drops et état |
| show logging | Journaux locaux disponibles |
| show processes cpu sorted | Processus consommant du CPU ; disponibilité selon le modèle |
| show memory statistics | Vue mémoire, si prise en charge par l'image |
| show users / show line | Sessions et lignes d'administration |

Toujours enregistrer l'heure et le contexte de la collecte. Quand tu partages une sortie, retire les secrets, clés, adresses sensibles et informations d'identification. Sur un réseau en production, conserver les sorties avant et après changement aide à distinguer une panne nouvelle d'un symptôme préexistant.

## 2. Interface, VLAN et couche 2

~~~~text
show interfaces counters errors
show interfaces GigabitEthernet1/0/1
show interfaces status
show vlan brief
show interfaces trunk
show spanning-tree
show mac address-table dynamic
show cdp neighbors detail
show lldp neighbors detail
~~~~

- Un état administratively down indique généralement une interface configurée en shutdown ; vérifier la configuration avant no shutdown.
- Un état down peut signaler câble, optique, port distant fermé, vitesse ou négociation.
- Les CRC et erreurs physiques peuvent pointer vers un câble, transceiver, connecteur ou problème de couche physique ; regarder l'évolution des compteurs, pas seulement une valeur ancienne.
- Une MAC absente peut venir d'un terminal silencieux, d'un VLAN incorrect, de STP, du port ou de l'apprentissage expiré.
- Un trunk opérationnel peut transporter seulement une partie des VLAN attendus. Vérifier allowed VLAN, VLAN natif et spanning tree.

## 3. Couche 3, ARP et routage

~~~~text
show ip interface brief
show ip route
show ip route 192.0.2.20
show ip arp
show ip protocols
show ip ospf neighbor
show ip eigrp neighbors
show access-lists
~~~~

Commande ARP selon la version : certaines plateformes utilisent show ip arp, d'autres peuvent exposer aussi show arp. Pour IPv6, rechercher les commandes ND appropriées.

| Symptôme | Hypothèse à vérifier |
|---|---|
| Interface L3 sans adresse attendue | Config IP, SVI, sous-interface, VRF |
| Même sous-réseau injoignable | Masque, ARP, VLAN, état interface |
| Réseau distant absent de la table | Route statique, adjacence, annonce, filtre, AD |
| Trafic dans un sens seulement | Route retour, ACL, NAT, asymétrie |
| Voisin de routage absent | Reachability IP, area/AS, timers, authentication, passive-interface |
| Compteurs ACL augmentent sur deny | Règle précise et flux concernés ; confirmer la direction |

## 4. Ping et traceroute : tester une hypothèse

~~~~text
ping 192.0.2.20
ping
traceroute 192.0.2.20
~~~~

Sur IOS, ping et traceroute interactifs peuvent demander une source, un nombre de répétitions, un timeout ou d'autres paramètres. Certaines versions acceptent des options directement sur la ligne de commande ; la syntaxe dépend de l'image.

Le ping teste si un échange ICMP peut réussir entre une source et une destination dans les conditions du test. Un échec ne prouve pas automatiquement une panne de routage : ICMP peut être filtré, la destination peut ne pas répondre ou le chemin retour peut être absent. À l'inverse, un ping réussi ne prouve pas qu'un port TCP ou une application fonctionne.

Le traceroute aide à identifier où les réponses cessent de revenir, mais certains routeurs filtrent ou limitent les messages TTL-expired. Des astérisques ne signifient donc pas forcément que le trafic utilisateur est interrompu. Refaire le test depuis une source pertinente, comparer avec un autre protocole de supervision et examiner les routes aller et retour.

## 5. Utiliser debug avec prudence

Les commandes debug sont intrusives : elles peuvent générer beaucoup de messages, augmenter le CPU, perturber une console lente ou exposer des détails sensibles. Privilégie les compteurs, show, logs et captures externes lorsqu'ils suffisent.

~~~~text
terminal monitor
debug ip ospf adj
! Reproduire le problème pendant une courte fenêtre
undebug all
show logging
~~~~

terminal monitor envoie les messages de console vers une session VTY dans les scénarios pris en charge. Il peut être nécessaire de désactiver le suivi après le test. Les commandes debug disponibles diffèrent selon le protocole et la version ; ne lance pas debug all sur un équipement chargé sans procédure de sécurité validée.

Avant d'activer un debug :
1. Définir l'hypothèse et le protocole étudié.
2. Vérifier CPU, mémoire et niveau de logging.
3. Prévoir une fenêtre brève, un accès de secours et une commande d'arrêt.
4. Limiter le debug au protocole ou à la condition utile.
5. Capturer l'heure de début et de fin.
6. Exécuter undebug all ou no debug all selon la plateforme, puis confirmer que le debug s'est arrêté.

## 6. Sauvegarder des preuves utiles

~~~~text
show clock
show logging
show running-config
show interfaces counters errors
show ip route
show tech-support
~~~~

show tech-support peut produire une sortie volumineuse et consommer des ressources ; demander l'autorisation et respecter la politique d'exploitation avant de l'exécuter. Ne pas envoyer une configuration complète dans un service externe sans revue des secrets, VPN, adresses et données de sécurité.

## 7. Arbre de décision : un hôte ne joint pas un serveur

~~~~text
Le port d'accès est-il up ?
├─ Non → câble, transceiver, shutdown, port err-disabled
└─ Oui
   ├─ Bon VLAN et MAC apprise ?
   │  ├─ Non → VLAN, trunk, STP, terminal
   │  └─ Oui
   ├─ Passerelle joignable ?
   │  ├─ Non → IP/masque, SVI, ARP, ACL locale
   │  └─ Oui
   ├─ Route distante et route retour présentes ?
   │  ├─ Non → routage statique/dynamique
   │  └─ Oui
   └─ Ping IP OK mais application KO ?
      └─ TCP/UDP, ACL, NAT, service et pare-feu hôte
~~~~

**Principe de dépannage :** commencer au lien, progresser de couche en couche, changer une seule variable à la fois et valider avec une commande qui prouve précisément l'hypothèse testée.
