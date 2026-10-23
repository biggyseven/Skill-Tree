---
node_id: troubleshooting-intermediaire
title: Méthodologie de dépannage - Intermédiaire
---

# Méthodologie de dépannage - Intermédiaire

**Niveau :** INTERMÉDIAIRE

Ce cours prolonge le niveau Débutant. Il considère acquis la description d’un symptôme, la délimitation du périmètre, les contrôles élémentaires IP/DNS et l’habitude de valider une correction. L’objectif n’est plus seulement de savoir quelle commande lancer, mais de construire un diagnostic reproductible à partir d’hypothèses, de mesures, de journaux et de captures de paquets.

Un incident réel ne respecte pas toujours l’ordre des couches du modèle OSI. Un utilisateur peut signaler une application lente alors que le problème est une fenêtre de congestion TCP, une résolution DNS différente selon le site, une route de retour absente, un MTU trop faible sur un tunnel ou une règle de sécurité appliquée dans un seul sens. Le technicien intermédiaire apprend à séparer ces causes en produisant des preuves ciblées plutôt qu’en accumulant des commandes.

Les exemples utilisent Windows, des outils courants de type Linux et Cisco IOS/IOS XE. Les sorties sont illustratives et les syntaxes varient selon la version, le matériel et les licences. Les commandes `show` et les captures sont généralement des opérations d’observation ; les commandes de configuration, de clear, de debug ou de changement de route peuvent avoir un impact opérationnel. Toute intervention sur un environnement partagé doit respecter la procédure de changement et les droits du technicien.

Le fil conducteur est la méthode **observer → formuler → discriminer → corriger → prouver**. Chaque investigation doit répondre à une question précise, définir le résultat attendu, préserver les traces utiles et aboutir à une conclusion dont le niveau de certitude correspond aux éléments recueillis.

> **Analogie** : Le dépannage intermédiaire ressemble à une enquête technique. Un témoignage permet de choisir où regarder, mais ne suffit pas à établir une cause. Une capture, un compteur d’interface, une table de routage et un journal sont des pièces différentes ; c’est leur concordance dans le temps qui permet de reconstituer le mécanisme de la panne.

---

## 1. La théorie et les algorithmes

### 1.1 Passer du symptôme à une hypothèse vérifiable

Au niveau Débutant, on apprend à écrire ce qui échoue et à établir le périmètre. Au niveau Intermédiaire, on transforme cette description en hypothèses concurrentes et en tests qui permettent de les départager. Une bonne hypothèse décrit un mécanisme possible et une observation qui devrait apparaître si elle est vraie.

Exemple : « Le partage SMB est inaccessible depuis le VLAN 30, mais accessible depuis le VLAN 20. » Plusieurs hypothèses sont plausibles : une ACL inter-VLAN bloque TCP/445 ; le serveur possède une route de retour incorrecte ; une politique du serveur autorise une seule plage source ; le client résout le nom vers une adresse différente ; le flux suit un chemin asymétrique. Le simple fait que le partage ne s’ouvre pas ne permet pas de choisir entre ces explications.

Utilisez une table de diagnostic. Elle doit être assez courte pour rester exploitable pendant l’incident :

| Hypothèse | Indice attendu si elle est vraie | Test discriminant | Risque / limite |
|---|---|---|---|
| Résolution DNS incorrecte | Le nom renvoie une adresse inattendue ou différente | Interroger le DNS utilisé puis comparer au résolveur attendu | Une réponse correcte ne garantit pas que l’application utilise ce résolveur |
| Filtrage de TCP/445 | SYN visible côté client, mais pas côté serveur, ou rejet explicite | Tester le port puis capturer de part et d’autre si possible | Les captures peuvent être perturbées par offload ou point de collecte |
| Route retour absente | Requête atteint le serveur, réponse part vers une autre passerelle | Consulter la table de routage du serveur et le chemin retour | Un traceroute ne montre pas toujours toutes les décisions de routage |
| Service à l’écoute absent | SYN reçu mais rejet par RST ou aucun socket sur le port | Vérifier l’écoute locale et les journaux du service | Les contrôles nécessitent les autorisations de l’équipe serveur |
| MTU/PMTUD défaillant | Échange initial établi, transfert de gros volumes bloqué | Comparer petits et gros paquets, inspecter ICMP Packet Too Big | Les tests de ping ne reproduisent pas toutes les tailles TCP |

La colonne « test discriminant » est essentielle. Un test qui pourrait donner exactement le même résultat pour toutes les hypothèses n’aide pas beaucoup. Si l’on soupçonne un filtrage applicatif, pinguer encore la passerelle apporte peu ; vérifier l’établissement TCP, les compteurs de règle ou la présence du SYN aux deux extrémités est généralement plus informatif.

Ne confondez pas **corrélation** et **causalité**. Un compteur qui augmente au moment de l’incident est un indice ; il faut comprendre s’il est lié au flux concerné et s’il précède le symptôme. Un événement de journal proche de l’heure ne prouve pas automatiquement qu’il a provoqué la panne. Comparez l’horodatage, la source, la destination, le protocole et l’état du service.

> **Piège :** énoncer une hypothèse sous la forme d’une certitude (« c’est forcément le DNS ») pousse à ne chercher que les preuves qui la confirment. Écrivez plutôt : « l’hypothèse DNS serait renforcée si le nom renvoyait une adresse inattendue, alors que la connexion directe à l’adresse fonctionne ».

### 1.2 Définir le flux exact avant d’investiguer

Une panne doit être ramenée, autant que possible, à un **tuple de flux** : adresse IP source, port source, adresse IP destination, port destination et protocole. Ajoutez la direction, l’interface ou le VLAN d’entrée, l’heure et le contexte applicatif. Pour TCP/443, par exemple, la règle pertinente dépend souvent de l’adresse source et destination ainsi que de la direction du premier paquet de la session.

Les noms peuvent masquer plusieurs adresses. Un service réparti derrière plusieurs enregistrements DNS, un équilibreur de charge, un proxy ou un CDN peut être atteint par des chemins différents suivant le poste, le site ou la famille IP choisie. Relevez les résultats de résolution, l’adresse réellement contactée et le port réellement ouvert. Ne vous contentez pas du nom de service affiché dans le navigateur.

Les cinq questions minimales sont :

1. Quelle source précise initie la connexion ?
2. Quelle destination et quel port sont attendus ?
3. Quel résultat est observé : expiration, refus, erreur DNS, reset, lenteur, transfert partiel ?
4. À quel point du trajet le paquet est-il visible ou absent ?
5. La situation de référence utilise-t-elle exactement le même chemin et la même politique ?

Pour un flux TCP, la distinction entre **timeout**, **connection refused** et **connection reset** oriente le diagnostic, sans suffire à l’établir :

- *Timeout* : aucune réponse utilisable n’est arrivée pendant l’intervalle attendu. Le paquet initial peut être filtré, perdu, routé ailleurs ou traité par un service silencieux.
- *Refused* : une réponse active, souvent TCP RST, indique généralement que la destination est joignable mais qu’aucun service n’accepte ce port, ou qu’un dispositif rejette explicitement le flux.
- *Reset* pendant une session : une session déjà établie est interrompue par un reset provenant d’un hôte ou d’un dispositif intermédiaire. Il faut identifier qui l’a envoyé et à quel moment.

Le message d’erreur du client est un indice, pas une carte exacte du réseau. Les applications peuvent convertir plusieurs erreurs de transport en un message générique. Les proxys et équilibreurs peuvent répondre à la place du serveur final.

### 1.3 Distinguer plan de contrôle, plan de données et plan de gestion

Sur un équipement réseau, le **plan de contrôle** apprend ou calcule les informations nécessaires à l’acheminement : voisinages, routes, état des protocoles. Le **plan de données** transfère réellement les paquets sur la base de ces informations. Le **plan de gestion** permet l’administration, la télémétrie et la configuration. Un routeur peut répondre en SSH et posséder des routes, tout en ayant une interface de transit saturée ou une ACL qui bloque le trafic utilisateur.

Cette séparation explique plusieurs observations trompeuses :

- Un équipement répond à `ping` adressé à son interface de gestion, mais ne transfère plus correctement le trafic via une interface de transit.
- La table de routage contient une route, mais la table de transfert matérielle ou une politique de sécurité ne réalise pas le résultat attendu.
- Un protocole de routage reste établi alors que les paquets applicatifs sont filtrés ailleurs.
- L’accès en SSH à un routeur fonctionne par le réseau d’administration, sans prouver que la route retour d’un client de production est correcte.

Sur Cisco IOS/IOS XE, `show ip route` aide à examiner le plan de contrôle IPv4. Selon la plateforme, `show ip cef` ou une commande de table de transfert correspondante aide à comprendre le chemin de données. `show interfaces` fournit l’état et certains compteurs physiques/logiques. Les noms des commandes et le détail disponibles diffèrent selon l’équipement ; vérifiez la documentation de la version utilisée.

Un routeur ne doit pas être considéré comme « en panne » uniquement parce qu’il ne répond pas à une sonde. Certains équipements limitent ICMP ou donnent une priorité faible aux paquets destinés au processeur. Il faut comparer le comportement du trafic transitant avec celui du trafic adressé à l’équipement lui-même.

### 1.4 Mesures de base : latence, pertes, gigue et débit

Une plainte de lenteur est trop vague pour guider une investigation. Mesurez au moins la latence, les pertes, la variabilité de délai et le débit réellement obtenu, en précisant le point de mesure et la période.

- **Latence aller-retour (RTT)** : temps mesuré pour envoyer une sonde et recevoir la réponse. Elle combine les délais aller et retour ; elle ne permet pas, seule, de localiser le retard.
- **Perte** : proportion de sondes ou de segments qui n’ont pas donné la réponse attendue. Une perte ICMP peut être due à une limitation de réponse et ne représente pas nécessairement la perte du trafic applicatif.
- **Gigue** : variation du délai d’un paquet à l’autre. Elle est importante pour la voix, la vidéo interactive et certains protocoles temps réel.
- **Débit** : volume transféré par unité de temps. Un débit faible peut venir de pertes TCP, d’une fenêtre de congestion limitée, d’un serveur lent, d’un lien partagé, de la capacité CPU ou des limites du test lui-même.

Ne comparez pas des mesures qui ne sont pas comparables. Un ping vers une adresse située dans le LAN et un transfert SMB vers un serveur distant n’exercent pas les mêmes chemins ni les mêmes fonctions. Pour comparer deux périodes, gardez autant que possible la même source, la même destination, le même protocole et la même méthode de mesure.

L’occupation d’une interface n’est pas seulement le pourcentage affiché au moment de la commande. Sur des liens rapides, une moyenne faible peut masquer des microbursts ; une interface peut accumuler des rejets de file d’attente sur de très courtes périodes. Les compteurs sur un intervalle connu et leur évolution sont plus utiles qu’une capture ponctuelle.

> **Astuce :** conservez toujours un relevé de référence quand le réseau fonctionne normalement : latence habituelle, débit attendu, compteurs d’erreurs, chemins de routage et services critiques. En incident, cette base aide à distinguer un comportement normal d’une vraie régression.

### 1.5 Lire un échange TCP au lieu de se fier à un seul test

TCP établit habituellement une connexion avec un échange SYN, SYN-ACK puis ACK. Dans une capture :

```text
Client                                  Serveur
  | -------- SYN -----------------------> |
  | <--------------------- SYN, ACK ----- |
  | -------- ACK -----------------------> |
  | ======== données applicatives =====> |
  | <================ réponse ========== |
```

Si le client émet des SYN répétés sans recevoir de SYN-ACK, la connexion n’a pas progressé comme prévu. Cela peut indiquer une perte, un filtrage silencieux, un problème de route ou l’absence de réponse en retour. Une réponse RST suggère plutôt un refus actif. Un handshake réussi suivi d’un blocage sur le transfert de données oriente vers d’autres possibilités : service bloqué après acceptation, inspection applicative, problème TLS, MTU, fenêtre TCP ou perte répétée.

Les retransmissions sont souvent visibles dans une capture, mais elles ne nomment pas leur cause. Elles peuvent résulter d’une perte de paquet, d’un délai excessif, d’une réorganisation ou d’un problème au point de capture. Vérifiez si le même segment est réellement retransmis, si l’ACK attendu manque, si les numéros de séquence sont cohérents et si la capture se fait côté émetteur, côté récepteur ou sur un port miroir.

Les numéros de séquence relatifs affichés par l’outil sont pratiques, mais ne sont pas les numéros absolus du flux. Tenez aussi compte du *window scaling*, des SACK, des accusés de réception cumulatifs et du contrôle de congestion lorsque vous analysez une session difficile. Pour un diagnostic intermédiaire, l’essentiel est de repérer où la progression cesse : établissement, négociation TLS, transfert de données ou fermeture.

Les captures réalisées sur l’hôte peuvent présenter des sommes de contrôle apparemment incorrectes, des segments regroupés ou de grandes unités dus aux fonctions d’offload de la carte réseau. Ce n’est pas toujours un défaut réel sur le fil. Si le doute est important, comparez avec une capture sur un port miroir ou un point d’observation indépendant, lorsque la politique de l’organisation l’autorise.

### 1.6 Utiliser les captures de paquets avec méthode

Une capture doit répondre à une question : « Le SYN atteint-il l’interface du serveur ? », « Le DNS répond-il avec le code attendu ? », « Le client reçoit-il un ICMP Packet Too Big ? ». Enregistrez le point de capture, les filtres, l’heure de début et de fin, le fuseau horaire si pertinent, et les adresses concernées. Une capture massive sans question produit souvent beaucoup de données et peu de réponses.

Dans Wireshark, il faut distinguer le **filtre de capture** (qui limite les paquets enregistrés) du **filtre d’affichage** (qui masque certains paquets dans la capture existante). Par exemple, un filtre de capture BPF `host 192.0.2.50 and tcp port 443` et un filtre d’affichage Wireshark `ip.addr == 192.0.2.50 && tcp.port == 443` utilisent des syntaxes différentes. Le filtre de capture s’applique au début ; un filtre d’affichage peut être modifié à tout moment pour explorer le fichier.

Filtres d’affichage utiles :

```text
ip.addr == 192.0.2.50
ip.src == 192.0.2.10 && tcp.dstport == 443
tcp.flags.syn == 1 && tcp.flags.ack == 0
tcp.analysis.retransmission
dns || dns.flags.response == 1
icmp || icmpv6
```

Ces filtres sont illustratifs ; l’expression disponible dépend de la version de Wireshark et du protocole décodé. Un filtre doit être testé sur les paquets connus pour éviter de masquer le flux qu’on veut justement observer.

Les points de capture n’ont pas tous la même valeur probante. Une capture sur le client montre ce qu’il pense avoir envoyé/reçu ; une capture serveur montre ce qui atteint cet hôte ; une capture sur une interface de pare-feu peut montrer le trafic avant ou après certaines transformations selon le produit. Des captures synchronisées des deux côtés sont particulièrement utiles pour localiser où une requête ou une réponse disparaît.

> **Danger :** les captures peuvent contenir des noms d’hôtes internes, des adresses, des cookies, des métadonnées sensibles ou parfois des données en clair. Limitez le périmètre et la durée, stockez les fichiers dans un espace approuvé et partagez-les selon la politique de sécurité. Ne joignez pas de mots de passe, de clés privées ou de secrets à un ticket.

### 1.7 Diagnostic DNS au-delà de la commande `nslookup`

Le diagnostic intermédiaire compare le résultat du résolveur configuré, le résultat obtenu auprès d’un serveur précis et l’adresse réellement utilisée par le client. En DNS, plusieurs facteurs peuvent différencier les réponses : cache, TTL, enregistrements A/AAAA, split DNS pour les utilisateurs VPN, vues internes/externes, CNAME, DNS proxy ou politique de sécurité.

Commencez par relever la configuration DNS du poste. Ensuite, interrogez le serveur prévu et comparez au serveur utilisé dans le test de référence. Pour isoler le transport, interrogez UDP/53 puis, quand c’est approprié, TCP/53. DNS utilise fréquemment UDP, mais TCP reste nécessaire dans des circonstances prévues par le protocole, notamment pour certaines réponses volumineuses et les transferts de zone entre serveurs autorisés. Un échec sur UDP n’autorise pas à conclure que tout le DNS est hors service.

Exemples Windows :

```powershell
ipconfig /all
nslookup app.intra.example
nslookup app.intra.example 192.0.2.53
Resolve-DnsName app.intra.example -Type A
Resolve-DnsName app.intra.example -Type AAAA
Clear-DnsClientCache
```

La dernière commande modifie le cache du client ; ne l’utilisez pas avant d’avoir enregistré la réponse et l’état qui posaient problème, car elle peut effacer un indice utile. Une réponse DNS correcte n’établit pas à elle seule que TCP fonctionne, que TLS est valide ou que l’application répond.

Vérifiez aussi IPv4 et IPv6. Un nom peut avoir une réponse A correcte et une réponse AAAA qui dirige le client vers un chemin IPv6 défaillant. Certains logiciels essaient les deux familles selon leur algorithme de sélection, et le symptôme peut prendre la forme d’un délai initial plutôt que d’un échec permanent. Comparez le comportement en forçant chaque destination ou famille avec les outils adaptés, sans désactiver durablement IPv6 comme contournement générique.

Une réponse NXDOMAIN signifie que le nom demandé n’existe pas selon le serveur qui répond ; SERVFAIL indique que le serveur n’a pas pu mener la résolution à bien ; REFUSED signale un refus de traitement. Les codes réduisent les hypothèses mais exigent d’examiner le serveur interrogé, la zone, la délégation, la validation DNSSEC éventuelle et les journaux. Le cache négatif peut prolonger l’effet d’une erreur même après la correction de la zone.

### 1.8 DHCP, relais et baux : localiser la rupture

Quand plusieurs clients ne reçoivent pas de bail, la cause peut être locale au VLAN, liée à un relais DHCP, à une portée épuisée, au serveur ou à une politique réseau. Pour IPv4, l’échange classique suit les étapes Discover, Offer, Request, Acknowledge (DORA), mais les clients qui renouvellent un bail ou reprennent une session peuvent utiliser d’autres échanges. Il ne faut donc pas interpréter toute capture DHCP uniquement avec ce modèle initial.

Sur un réseau routé, la diffusion DHCP du client ne traverse généralement pas les routeurs telle quelle. Un relais (par exemple `ip helper-address` sur certains équipements Cisco) transmet la demande au serveur et ajoute les informations nécessaires à l’identification du réseau client. Si les clients d’un VLAN échouent tandis que ceux des autres VLAN fonctionnent, vérifiez la présence et la validité du relais, la portée correspondante, les options de passerelle/DNS et les éventuelles politiques de sécurité.

Exemples de contrôles Cisco IOS/IOS XE (à adapter) :

```text
show ip interface brief
show running-config interface vlan 30
show ip dhcp binding
show ip dhcp pool
show ip route
show logging
```

La disponibilité de ces commandes dépend du rôle de l’équipement : un commutateur qui relaie DHCP ne tient pas nécessairement les baux lui-même. Ne modifiez pas l’étendue ou les bindings sans connaître les conséquences sur les clients. La suppression de baux peut provoquer une renumérotation massive et rendre le diagnostic plus difficile.

Quand c’est autorisé, une capture sur le VLAN client et une autre côté serveur aide à savoir si Discover arrive, si Offer repart et où l’échange s’arrête. Si Discover apparaît sur le VLAN mais n’arrive pas au serveur, l’investigation porte sur le relais ou le trajet. Si le serveur reçoit la requête et n’émet pas d’offre, examinez sa portée, ses journaux et sa configuration. Si Offer est émis mais n’atteint pas le client, regardez le chemin retour, les VLAN, les ACL et les relais.

### 1.9 Couche 2 : VLAN, trunk, MAC et boucles

Quand l’adressage d’un poste est plausible mais que la communication locale échoue, examinez l’appartenance au VLAN, les trunks et l’apprentissage MAC. Une trame peut entrer par un port access du mauvais VLAN, être étiquetée de manière inattendue sur un trunk, ou atteindre un VLAN où l’interface de passerelle n’existe pas. La simple présence d’un lien physique ne garantit ni que le VLAN est correct ni que le trafic est transmis au bon domaine de diffusion.

Commandes typiques sur Cisco IOS/IOS XE :

```text
show interfaces status
show interfaces gigabitEthernet 1/0/12 switchport
show vlan brief
show interfaces trunk
show mac address-table dynamic
show spanning-tree vlan 30
show etherchannel summary
```

Les noms d’interface, les syntaxes et la disponibilité dépendent du modèle. Les compteurs doivent être observés sur un intervalle, pas seulement lus comme une valeur absolue. Une table MAC qui se vide ou apprend une adresse sur des ports alternants peut signaler une mobilité normale, un changement de topologie ou un problème de boucle ; il faut confirmer avec l’heure et les événements de spanning tree.

Les tempêtes de diffusion, les changements répétés de topologie STP et le déplacement fréquent des adresses MAC peuvent se traduire par des lenteurs intermittentes et des pertes variables. Cherchez les compteurs de broadcast/multicast, les transitions de port, les erreurs et les logs STP. Ne désactivez pas STP pour « tester » : il protège le domaine de couche 2 contre les boucles, et sa suppression peut rendre toute une partie du réseau instable.

Un EtherChannel mal aligné peut être partiellement opérationnel : membres suspendus, paramètres différents, incohérence de VLAN ou répartition de flux qui expose un seul chemin défectueux. Vérifiez la négociation, les membres effectivement actifs, la configuration des deux extrémités et la cohérence des trunks. Un paquet donné ne traverse souvent qu’un membre selon l’algorithme de hachage ; deux tests peuvent donc emprunter des chemins physiques différents.

### 1.10 Routage : route aller, route retour et politiques

Une route présente dans la table n’est pas forcément la route utilisée par le flux dans les deux sens. La sélection peut dépendre du plus long préfixe, de la distance administrative, de la métrique, du routage basé sur des politiques (PBR), de VRF ou d’un mécanisme de redondance. Il faut analyser séparément le chemin aller et le chemin de retour.

Exemples d’observation Cisco :

```text
show ip route 192.0.2.50
show ip cef 192.0.2.50 detail
show ip protocols
show ip ospf neighbor
show ip bgp summary
show ip policy
show access-lists
```

Toutes ces commandes ne sont pas disponibles dans toutes les plateformes ou topologies. Le résultat CEF indique un chemin de transfert calculé dans le contexte de la plateforme ; les détails peuvent dépendre du matériel. Si plusieurs VRF sont utilisées, vérifiez la table de routage dans la VRF du flux et pas seulement la table globale.

Le routage asymétrique se produit quand l’aller et le retour passent par des chemins différents. Il n’est pas forcément incorrect, mais il peut poser problème à un pare-feu stateful qui s’attend à voir la session dans les deux sens, à un NAT qui suit l’état ou à un dispositif de capture placé sur un seul trajet. Une requête peut alors atteindre le serveur tandis que la réponse est envoyée via une passerelle non prévue.

La PBR peut choisir un next-hop différent de celui qu’indique la route classique. Les route-maps, communautés, préférences BGP, routes plus spécifiques ou VRF peuvent également produire des chemins distincts. Lorsqu’un flux échoue, comparez l’adresse source effective, la route la plus spécifique, la règle de politique appliquée, le prochain saut réel et le chemin de retour. Une simple lecture de la route par défaut est insuffisante.

Les traceroutes sont utiles pour produire des indices, mais chaque sonde peut être traitée différemment, certaines interfaces peuvent ne pas répondre, et les chemins aller/retour peuvent différer. Un saut qui ne répond pas n’est pas nécessairement un trou dans le transfert. Combinez traceroute, table de routage, capture et journaux du point de sécurité lorsqu’ils sont disponibles.

### 1.11 ACL et pare-feu : interpréter le rejet et le silence

Un flux peut être bloqué sur un hôte, un routeur, un commutateur de couche 3, un pare-feu central, un pare-feu cloud ou un dispositif d’inspection. Le fait que deux hôtes puissent se pinguer ne signifie pas que le port requis est autorisé. À l’inverse, un ping bloqué ne prouve pas qu’un port TCP est interdit.

Sur Cisco, une ACL est généralement évaluée selon l’ordre des règles et s’arrête à la première correspondance ; une ligne implicite de refus existe à la fin des listes de contrôle courantes. La direction `in` ou `out` décrit le point de vue de l’interface. Avant de modifier une ACL, identifiez l’interface, la direction, le protocole, les adresses, les ports et la règle susceptible de correspondre. `show access-lists` peut montrer des compteurs de correspondance, mais ils peuvent être partagés entre flux et dépendent des fonctionnalités de la plateforme.

Commandes d’observation typiques :

```text
show access-lists
show ip interface
show running-config | section access-list
show logging
```

Le nom et la prise en charge des filtres de sortie peuvent varier. Sur un pare-feu NGFW, l’équivalent peut être la règle de sécurité, la politique NAT, l’identifiant de session, le résultat de l’inspection ou le journal de menace. Il faut aussi distinguer le refus explicite du rejet silencieux : le premier peut envoyer un RST ou un ICMP ; le second peut abandonner le paquet et provoquer un timeout.

Les règles avec état suivent l’établissement et la fin des sessions. Une connexion peut être autorisée à l’aller puis perturbée par une route retour différente, une expiration de session ou une table d’état saturée. Examinez l’événement correspondant à la session précise, pas seulement le compteur global. Ne créez pas de règle `permit ip any any` comme expérience : une exception trop large peut masquer la cause et ouvrir un risque de sécurité.

### 1.12 NAT, adresse source et traçage de session

Le NAT change une ou plusieurs adresses, et parfois des ports. Pour suivre une session, il peut être nécessaire de corréler le tuple avant et après translation. Le client peut croire joindre `10.20.30.40:443`, alors que l’équipement de bord traduit la destination vers une adresse serveur différente. Le serveur peut voir une adresse source traduite, pas celle du client original.

Sur Cisco IOS/IOS XE, les commandes `show ip nat translations` et `show ip nat statistics` peuvent aider selon l’implémentation. Sur un pare-feu, utilisez l’identifiant de session et les champs pré-NAT/post-NAT. Vérifiez si la règle de sécurité évalue la destination avant ou après translation conformément au fonctionnement documenté du produit. Les plateformes ne partagent pas toutes la même sémantique.

Quand une session est établie mais ne reçoit aucune réponse, vérifiez la translation, l’itinéraire vers la destination traduite, le retour, la durée de vie de l’état et l’éventuelle collision de ports. Un changement d’adresse source peut aussi avoir un effet sur les listes d’autorisation d’un serveur distant. Si une application fonctionnait depuis un site mais échoue depuis un autre, comparez les adresses sources réellement vues par le service.

Évitez de vider toute la table NAT pour un seul flux en production. Cela pourrait interrompre de nombreuses connexions et détruire un élément de preuve. Préférez l’observation de la session concernée, si les outils le permettent, et coordonnez tout effacement ciblé avec l’équipe responsable.

### 1.13 MTU, MSS et « panne des gros paquets »

Le MTU définit la taille maximale d’un paquet de couche liaison transmis sans fragmentation à ce niveau. Les tunnels VPN, PPPoE, l’encapsulation, certains chemins opérateur et les superpositions réseau consomment une partie de la taille disponible. Le MTU de bout en bout peut donc être inférieur à celui du LAN.

Un symptôme classique est un handshake TCP qui réussit, suivi d’un chargement qui reste bloqué quand des données plus grandes commencent à circuler. Les petits pings passent, mais les grosses réponses échouent. Cela peut venir d’un PMTUD défaillant, souvent lorsque les messages ICMP « fragmentation needed » en IPv4 ou « Packet Too Big » en IPv6 sont filtrés ou perdus. L’application et TCP peuvent alors attendre ou retransmettre sans progression.

Pour IPv4, le mécanisme PMTUD est décrit notamment dans la RFC 1191. Pour IPv6, la RFC 8201 explique que la découverte dépend des messages ICMPv6 Packet Too Big ; bloquer ces messages peut créer un « black hole » pour les paquets trop grands. Il ne faut donc pas considérer tout ICMP comme superflu. La solution n’est pas automatiquement d’abaisser le MTU partout : mesurez d’abord le chemin et appliquez une correction ciblée.

Sous Windows, `ping` permet des tests de taille, par exemple :

```powershell
ping 198.51.100.25 -f -l 1472
```

Cette commande est un exemple IPv4 : la charge ICMP et les en-têtes IPv4/ICMP ajoutent de la taille au paquet. Ajustez la taille progressivement et tenez compte du fait que des équipements peuvent filtrer ICMP. Les résultats ne sont pas définitifs s’il n’y a pas de réponse. Sous Linux, l’option adaptée peut ressembler à `ping -M do -s 1472 198.51.100.25`, selon l’implémentation installée.

Pour TCP, la MSS annonce la taille maximale de segment TCP que le pair souhaite recevoir ; elle tient compte des en-têtes IP/TCP. Un ajustement MSS sur un point contrôlé peut contourner certains problèmes de tunnel, mais il ne doit pas être appliqué sans connaître le chemin et les effets. Capturez les SYN/SYN-ACK, comparez la MSS annoncée, cherchez les messages ICMP pertinents et vérifiez si les retransmissions correspondent aux gros segments.

> **Piège :** ne déduisez pas automatiquement que le MTU est fautif parce qu’un ping volumineux échoue. Le destinataire ou un pare-feu peut filtrer les réponses ICMP. Le diagnostic devient solide quand la taille influence de façon reproductible le transfert, que les captures montrent les paquets concernés et que le chemin est cohérent avec l’hypothèse.

### 1.14 Problèmes de performance et compteurs d’interface

Les compteurs servent à distinguer une erreur physique, une congestion et un problème situé plus haut dans la pile. Sur un port Ethernet, surveillez notamment les erreurs CRC/FCS, les erreurs d’alignement, les drops, les overruns, les resets de lien, les collisions sur des environnements qui les utilisent encore et les transitions d’état. Les noms exacts varient selon le fabricant et la version.

Un compteur cumulatif de 100 erreurs n’indique pas nécessairement une panne actuelle. Il faut savoir s’il progresse pendant l’incident. Relevez les valeurs, attendez un intervalle contrôlé puis relisez-les. Une interface qui accumule progressivement des CRC peut suggérer câble, connecteur, transceiver ou problème de port. Des drops sans erreurs physiques peuvent plutôt être liés à une congestion, une file d’attente, un policer ou un buffer insuffisant.

Exemples Cisco :

```text
show interfaces gigabitEthernet 1/0/12
show interfaces counters errors
show processes cpu sorted
show platform hardware fed switch active fwd-asic drops exceptions
show logging | include LINK|LINEPROTO|SPANTREE
```

La commande matérielle d’exemple n’est pas universelle et peut être invalide sur d’autres modèles ; consultez la référence de la plateforme et n’exécutez pas de commandes inconnues en production. `show processes cpu sorted` reflète le processeur de contrôle, pas nécessairement le débit du plan de données. Un équipement avec CPU bas peut encore perdre du trafic dans une file matérielle.

Les duplex mismatches, la négociation de vitesse incohérente et les câbles défectueux peuvent produire de la retransmission, du débit instable ou des erreurs. Sur des liaisons modernes, la vérification doit suivre les recommandations de la plateforme : ne forcez pas vitesse et duplex au hasard. Une modification incohérente aux deux extrémités peut aggraver le problème.

### 1.15 Pannes intermittentes et corrélation temporelle

Une panne intermittente est difficile parce que le système peut être normal au moment où le technicien teste. Il faut donc associer les symptômes à l’heure exacte, à la durée, à la source, à la destination et aux événements qui se produisent à cette période. Une collecte continue mais peu intrusive est souvent plus utile qu’une session de commandes lancée une seule fois.

Établissez une ligne du temps à partir de journaux, compteurs, supervision, événements de changement, métriques serveur et retours d’utilisateurs. Vérifiez la synchronisation NTP des équipements : si l’horloge du pare-feu est décalée de plusieurs minutes par rapport au serveur, la corrélation devient incertaine. Conservez le fuseau et la source des horodatages. Ne déduisez pas l’ordre causal de deux lignes de journal sans vérifier les décalages éventuels.

Les phénomènes récurrents aux heures de pointe font envisager la congestion, les sauvegardes, les tâches planifiées, les renouvellements, les basculements ou les changements de route. Un problème limité à certaines conversations TCP peut aussi venir d’un hachage ECMP qui envoie certains flux vers un chemin défectueux. Comparez plusieurs connexions et, si possible, les chemins empruntés par leur tuple.

Il est souvent utile d’organiser une collecte préventive limitée : ping à faible fréquence vers quelques destinations autorisées, compteurs d’interface à intervalle régulier, télémétrie de files et journaux de sécurité. Évitez les sondes agressives qui risquent elles-mêmes de produire de la charge ou de fausser les observations.

### 1.16 Considérer IPv4 et IPv6 séparément

Un service peut fonctionner en IPv4 et échouer en IPv6, ou l’inverse. Les routes, ACL, pare-feu, DNS, MTU et chemins d’administration ne sont pas nécessairement identiques pour les deux familles. Si un nom renvoie à la fois A et AAAA, le client peut choisir une famille puis tenter l’autre selon son implémentation et les délais observés.

Vérifiez : l’adresse source et la destination réellement utilisées, la route IPv4/IPv6, la passerelle, les règles de filtrage, les messages ICMP/ICMPv6 utiles, les voisins locaux et la réponse de l’application. Ne concluez pas qu’IPv6 est responsable uniquement parce qu’il est activé. Les différences de chemin ou de politique doivent être prouvées.

Commandes de diagnostic varient selon le système. Sous Windows, `Get-NetIPConfiguration`, `Get-NetRoute`, `Resolve-DnsName` et `Test-NetConnection` apportent des informations. Sur Cisco IOS XE, les commandes commencent souvent par `show ipv6 route`, `show ipv6 neighbors` ou `show ipv6 interface brief`. La prise en charge détaillée diffère selon la plateforme.

Un contrôle de sécurité trop simpliste peut autoriser certains flux IPv4 tout en bloquant les messages de contrôle nécessaires à IPv6. ICMPv6 comprend plusieurs fonctions importantes pour IPv6, comme la découverte de voisin et la découverte de MTU. Il ne doit pas être filtré comme si tous ses messages étaient des pings facultatifs.

### 1.17 Construire une procédure reproductible

Pour chaque test, consignez : l’heure, l’équipement source, la destination, le contexte de connexion, la commande ou le filtre, le résultat attendu, le résultat réel et l’interprétation. Notez aussi ce que le test **ne** permet pas de conclure. Cette dernière information empêche un résultat limité de devenir une affirmation trop large.

Un plan de test est d’autant plus fort qu’il contient un résultat attendu avant l’exécution. Exemple : « Si le problème provient uniquement de la résolution DNS, alors une connexion vers l’adresse IP correcte devrait au moins atteindre le service, sous réserve que TLS, l’hébergement virtuel et les règles applicatives ne dépendent pas du nom. » Si le test échoue, l’hypothèse DNS seule n’explique pas l’ensemble du problème ; il faut revisiter le modèle plutôt que d’ignorer le résultat.

Appliquez la règle du changement minimal : si un test démontre que l’ACL `in` sur le VLAN 30 refuse TCP/445, ne modifiez pas également le DNS, les routes et le MTU. Changez une variable à la fois, si possible, et comparez avec le résultat précédent. Une intervention qui corrige tout simultanément empêche d’identifier la cause et accroît le risque de régression.

> **Astuce :** pour les incidents complexes, gardez un journal d’hypothèses avec trois états : « non testé », « renforcé par une preuve » et « réfuté par une preuve ». Évitez les étiquettes « vrai/faux » tant que les données ne suffisent pas. Cela rend les échanges avec le serveur, la sécurité et l’équipe réseau beaucoup plus efficaces.

---

## 2. Configuration et pratique

Cette partie fournit des commandes pour assembler une investigation intermédiaire. Les lignes sont des exemples ; elles ne remplacent pas la documentation de la version utilisée. L’ordre privilégié est : collecter d’abord les éléments non intrusifs, réaliser ensuite un test ciblé, puis seulement envisager une modification autorisée.

### 2.1 Préparer le dossier d’incident

Avant les commandes, créez une fiche comprenant au minimum :

| Champ | Exemple |
|---|---|
| Identifiant | INC-2026-1042 |
| Début observé | 09:17, heure locale, 22/10/2026 |
| Périmètre | Postes du VLAN 30 vers le serveur applicatif |
| Flux attendu | TCP/443 vers `app.intra.example` |
| Résultat observé | SYN répétés, pas de réponse au client |
| Changement récent | Nouvelle politique de filtrage déployée la veille |
| Tests déjà effectués | Résolution DNS, `Test-NetConnection`, comparaison avec VLAN 20 |
| Risque / impact | Application métier indisponible pour 12 utilisateurs |
| Responsable / autorisation | Équipe réseau, fenêtre de changement selon procédure |

N’incluez pas les mots de passe, les tokens, les chaînes privées ou des exports de configuration complets sans besoin. Masquez les secrets des configurations avant de les joindre au ticket. Le dossier doit permettre de reprendre l’investigation, pas d’exposer des informations sensibles.

### 2.2 Tests ciblés sous Windows

```powershell
# Paramètres de l’interface et des serveurs DNS
Get-NetIPConfiguration
Get-NetIPInterface
Get-DnsClientServerAddress
Get-NetRoute -AddressFamily IPv4

# Résolution et cache DNS
Resolve-DnsName app.intra.example -Type A
Resolve-DnsName app.intra.example -Type AAAA
Get-DnsClientCache

# Port et chemin réseau
Test-NetConnection app.intra.example -Port 443 -InformationLevel Detailed
tracert -d 192.0.2.50
pathping 192.0.2.50

# Interfaces et compteurs TCP (aperçu)
Get-NetAdapter
Get-NetTCPConnection -State Established
```

Utilisez les commandes par rapport à une question. `Test-NetConnection -Port 443` indique si la connexion TCP a été établie vers la destination qui a été résolue ; il ne valide pas l’ensemble de la négociation TLS ni la santé de l’application. `tracert -d` évite les résolutions de noms des sauts pour accélérer la lecture, mais ne garantit pas que tous les sauts répondront. `pathping` peut envoyer des sondes pendant un certain temps : utilisez-le en tenant compte de la politique réseau et de la charge.

Comparez le DNS, l’adresse de destination, le port et le résultat avec un poste de référence dans une situation équivalente. Ne copiez jamais son adresse IP statique pour « voir si cela marche », car cela peut produire un conflit d’adresses. Pour un test avec IP directe, gardez en tête que des applications HTTPS utilisent le nom pour le SNI, le certificat et l’hébergement virtuel ; une connexion directe peut échouer pour des raisons différentes.

### 2.3 Tests courants sur un hôte Linux

```bash
ip -br address
ip route get 192.0.2.50
ip neigh show
resolvectl status
resolvectl query app.intra.example
ss -tnp
curl -v --connect-timeout 5 https://app.intra.example/
tracepath 192.0.2.50
```

Les commandes `resolvectl` supposent un système qui utilise systemd-resolved ; d’autres distributions s’appuient sur d’autres outils. `ss -tnp` peut nécessiter des privilèges pour voir les processus d’autres utilisateurs. `curl -v` est utile pour repérer l’étape de l’échec, mais sa sortie peut contenir des éléments internes et doit être partagée avec discernement.

`ip route get` est particulièrement utile pour connaître la route sélectionnée pour une destination précise, y compris l’interface et l’adresse source qui seront utilisées par le noyau. Cela peut révéler qu’un client choisit une interface VPN, une VRF ou une source différente de celle supposée. Ce résultat local ne prouve toutefois pas le chemin complet à travers le réseau.

### 2.4 Collecte courte avec tcpdump

Sur un hôte Linux où l’on possède les permissions nécessaires :

```bash
sudo tcpdump -ni any host 192.0.2.50 and tcp port 443 -c 300 -w /tmp/inc-1042.pcap
```

L’option `-i any` n’existe pas ou ne se comporte pas de la même manière sur tous les systèmes ; l’interface doit être choisie explicitement si nécessaire. L’option `-c` limite le nombre de paquets, tandis que le filtre réduit le trafic conservé. Assurez-vous que le stockage est autorisé et que le fichier sera supprimé ou archivé selon la politique prévue.

Pour observer le DNS :

```bash
sudo tcpdump -ni eth0 '(udp port 53 or tcp port 53) and host 192.0.2.53' -c 200
```

Une absence de réponse dans cette capture peut vouloir dire que le serveur ne répond pas, mais aussi que la capture se fait sur la mauvaise interface, que le flux utilise un autre résolveur ou qu’un mécanisme chiffré de résolution contourne le port 53. Vérifiez d’abord le contexte réel.

### 2.5 Vérifications Cisco IOS/IOS XE

Exemples d’observation :

```text
show clock detail
show logging
show interfaces status
show interfaces gigabitEthernet 1/0/12
show interfaces counters errors
show vlan brief
show interfaces trunk
show mac address-table dynamic
show spanning-tree vlan 30
show ip interface brief
show ip route 192.0.2.50
show ip cef 192.0.2.50 detail
show access-lists
show arp
show ip nat translations
show ip nat statistics
```

Ces commandes servent des objectifs différents et ne sont pas toutes disponibles sur toutes les plateformes. `show clock detail` est utile pour comprendre l’horodatage ; `show interfaces counters errors` permet de relever l’évolution des erreurs ; `show ip route` et CEF aident à comprendre le chemin sélectionné ; les commandes VLAN/STP ciblent la couche 2 ; les ACL/NAT sont pertinentes uniquement si ces fonctions sont en place.

Pour l’interprétation, conservez la sortie brute et comparez-la à une deuxième lecture après un intervalle défini. Ne réinitialisez pas les compteurs avant de les avoir capturés et compris. L’effacement de compteurs, la modification d’ACL et le lancement de debugs peuvent affecter l’investigation et parfois le fonctionnement de l’équipement.

### 2.6 Utiliser le debug avec prudence

Les commandes `debug` peuvent générer un volume important de messages, augmenter la charge CPU ou impacter la stabilité selon le modèle et le volume de trafic. Ne les lancez pas à l’aveugle sur un équipement de production. Vérifiez le risque, la syntaxe et la façon correcte de les arrêter dans la documentation de la plateforme ; définissez une fenêtre courte et un filtre si disponibles.

Préférez d’abord les commandes `show`, les compteurs de règles, les journaux existants, les outils de capture intégrés et la télémétrie. Si un debug ciblé est indispensable, notez l’heure de début, l’heure d’arrêt, l’identité de l’opérateur, les paramètres et le résultat attendu. Confirmez ensuite que le debug est arrêté et que la charge est revenue à la normale.

> **Danger :** ne lancez jamais une commande copiée depuis un forum sans comprendre sa portée, particulièrement `clear`, `debug`, `reload`, `shutdown`, les commandes de suppression de table ou les modifications d’ACL/routes. Le fait qu’une commande soit utilisée en dépannage ne signifie pas qu’elle est sans risque.

### 2.7 Analyse d’une capture Wireshark : scénario TCP/443

Scénario : depuis `192.0.2.10`, le client tente d’atteindre `192.0.2.50:443`. Commencez par le filtre d’affichage :

```text
ip.addr == 192.0.2.50 && tcp.port == 443
```

Interprétez les possibilités :

- SYN répétés, sans SYN-ACK : le client n’observe pas de réponse au SYN. Il faut voir si le paquet apparaît du côté serveur ou sur une interface intermédiaire.
- SYN puis RST : l’équipement qui génère le RST refuse le port ou rejette activement la connexion. Identifiez la source du RST, qui peut ne pas être le serveur final.
- Handshake complet, puis alerte TLS : la connectivité TCP existe ; concentrez-vous sur le certificat, le SNI, les suites/protocoles supportés, le proxy ou l’inspection TLS selon les messages capturés.
- Handshake complet, puis retransmissions sur les données : regardez la progression des ACK, les tailles, les pertes et les éventuels messages ICMP de MTU.
- Fermeture FIN normale : la session a été fermée proprement au niveau TCP, mais cela ne prouve pas que l’opération applicative a réussi.

L’observation doit être corrélée au journal du serveur ou du pare-feu. Si un SYN apparaît au client mais n’apparaît pas sur une capture serveur synchronisée, le problème se situe dans le chemin entre les deux points ou dans la visibilité de la capture. Si le SYN arrive au serveur et que le serveur répond, mais que cette réponse ne réapparaît pas chez le client, examinez le chemin retour.

### 2.8 Vérifier l’impact de la correction

Avant d’effectuer le changement, écrivez le test qui devra réussir et les effets secondaires à surveiller. Après le changement, répétez le test exact avec la même source, la même destination, le même protocole et un intervalle comparable. Vérifiez aussi une fonction voisine qui pourrait être affectée par la modification.

Une validation utile répond à quatre questions :

1. Le symptôme initial a-t-il disparu dans les mêmes conditions ?
2. Les compteurs/journaux confirment-ils le mécanisme de correction supposé ?
3. Les services similaires qui partageaient la ressource fonctionnent-ils encore ?
4. Le changement est-il documenté et le retour arrière reste-t-il possible ?

Ne clôturez pas un incident simplement parce que la commande de configuration a été acceptée. Un changement syntaxiquement valide peut ne pas être celui qui correspond au flux, et un service peut fonctionner brièvement tout en étant encore instable.

---

## 3. Dépannage et sécurité

Cette partie applique les méthodes précédentes à des cas transversaux. Chaque cas fournit un symptôme, les preuves à recueillir, un chemin de diagnostic et les actions à éviter.

### 3.1 Cas pratique A — DNS correct, service TCP inaccessible

**Contexte :** plusieurs postes résolvent `crm.intra.example` vers `192.0.2.50`. Les postes du VLAN 20 accèdent au service, ceux du VLAN 30 reçoivent un timeout sur TCP/443.

**Étape 1 — Confirmer la différence.** Depuis un poste de chaque VLAN, enregistrez la résolution, l’adresse effective, l’heure et le résultat de `Test-NetConnection` ou de l’outil équivalent. Si le nom donne des adresses différentes, investiguez les DNS et le contexte de résolution avant de comparer les flux.

**Étape 2 — Tester le port exact.** Un ping n’est pas discriminant si ICMP est autorisé de la même façon dans les deux VLAN. Utilisez un test TCP/443 et vérifiez si l’erreur diffère : timeout, refus ou erreur applicative.

**Étape 3 — Comparer la règle de sécurité.** Identifiez les interfaces et directions traversées par le VLAN 30. Examinez les compteurs des ACL ou le journal NGFW pour la source et la destination exactes. Un refus explicite dans le journal fournit une preuve plus forte qu’un simple timeout.

**Étape 4 — Capturer si nécessaire.** Une capture côté client et côté serveur permet de savoir si le SYN arrive et si la réponse part. En cas de SYN reçu au serveur mais de SYN-ACK absent, regardez la pile locale, le service et le pare-feu de l’hôte. Si le SYN-ACK sort du serveur mais n’arrive pas au client, étudiez la route retour et les politiques intermédiaires.

**Étape 5 — Corriger avec le périmètre minimal.** Une règle ciblée pour les sources et destinations prévues est préférable à une ouverture générale. Faites valider par le propriétaire du service et la sécurité, puis testez le port, l’application et les flux voisins.

**Ce qu’il faut noter :** hypothèse de départ, flux exact, identifiant de règle concernée, résultat avant/après et preuve qui localise le point de rejet. « Pare-feu réparé » est trop vague ; « la règle R-218 ne couvrait pas le sous-réseau source du VLAN 30, le journal a confirmé le refus et la règle a été ajustée au flux autorisé » est reproductible.

### 3.2 Cas pratique B — Handshake TCP réussi, chargement bloqué

**Contexte :** l’application s’ouvre, puis reste bloquée au moment de télécharger un document volumineux. Les pages simples fonctionnent et le serveur est joignable.

Hypothèses raisonnables : MTU de chemin réduit sur VPN/tunnel, messages ICMP de PMTUD bloqués, proxy ou inspecteur qui interrompt les données, serveur qui cesse d’émettre, perte importante ou problème de fenêtre TCP.

1. Relevez si le problème se reproduit uniquement via le VPN, sur certains sites ou avec certains volumes.
2. Capturez le début de la session et le moment du blocage ; notez les numéros de séquence, les retransmissions et les ACK.
3. Comparez les tailles des segments qui progressent et de ceux qui restent bloqués.
4. Recherchez ICMP « fragmentation needed » ou ICMPv6 « Packet Too Big » aux points visibles. N’ignorez pas ces messages au seul motif qu’ils utilisent ICMP.
5. Vérifiez le MTU des interfaces tunnel et de l’underlay, les annonces MSS et le comportement du pare-feu, selon les outils autorisés.
6. N’appliquez une correction de MTU/MSS qu’après avoir localisé la contrainte et en coordination avec le propriétaire du tunnel.

La conclusion « c’est le MTU » nécessite plus que le fait qu’un ping volumineux échoue. Elle doit être soutenue par une dépendance à la taille, un chemin qui comporte une encapsulation ou une interface plus restrictive et une observation de la progression TCP/ICMP.

### 3.3 Cas pratique C — Lenteur intermittente entre deux réseaux

**Contexte :** certains transferts vers un serveur distant sont rapides, d’autres très lents. Les pings moyens paraissent acceptables. La topologie utilise plusieurs chemins de sortie.

**Hypothèses :** pertes ponctuelles, un membre d’EtherChannel endommagé, un chemin ECMP défectueux, congestion de file, charge serveur variable, inspection stateful saturée ou une application qui fait varier la taille des données.

- Capturez deux flux comparables et enregistrez les tuples complets ; un hachage ECMP peut assigner les flux à des chemins différents.
- Comparez les routes, next-hops et interfaces empruntées autant que l’architecture le permet.
- Échantillonnez les compteurs d’erreurs, drops et files sur une période qui englobe le symptôme.
- Comparez les retransmissions TCP, la latence et le débit ; un RTT acceptable ne signifie pas qu’il n’y a aucune perte.
- Corrélez les événements avec les changements de topologie, les alertes de l’équipement et les journaux du serveur.

Ne réinitialisez pas immédiatement les interfaces ou le bundle : une remise à zéro peut faire disparaître les compteurs et modifier l’état du chemin. Rassemblez les preuves avant un changement. Si une interface semble en cause, faites valider par l’équipe responsable la méthode sûre de test ou de remplacement.

### 3.4 Cas pratique D — VPN établi, mais une application ne passe pas

Un statut VPN « connecté » confirme une partie de l’établissement du tunnel, pas que toutes les routes, sélecteurs, DNS et règles d’accès sont corrects. Il peut exister une route manquante pour le préfixe de l’application, un chevauchement d’adressage, un split tunnel incomplet, une politique d’accès insuffisante ou un problème de retour.

Commencez par identifier la destination réellement utilisée et l’adresse source du client VPN. Examinez la table de route avant et après l’établissement du tunnel. Confirmez que le préfixe de destination est associé à l’interface attendue et qu’il n’est pas capturé par une route locale plus spécifique ou un réseau domestique qui chevauche le réseau d’entreprise.

Ensuite, vérifiez le flux complet : résolution DNS selon la politique VPN, route côté réseau d’entreprise, ACL/pare-feu, route de retour vers la plage d’adresses VPN et état de la session. Si le ping échoue mais que TCP/443 passe, ne changez pas les routes sur la seule base de l’ICMP. Si le tunnel est opérationnel mais une seule application est inaccessible, gardez la portée ciblée.

Évitez de désactiver la sécurité du poste ou de modifier globalement les préférences de tunnel. Les journaux VPN peuvent contenir des identifiants et des informations internes ; partagez uniquement les extraits nécessaires et masquez les secrets.

### 3.5 Cas pratique E — DHCP fonctionne dans un VLAN, pas dans l’autre

**Contexte :** les clients du VLAN 10 reçoivent un bail, ceux du VLAN 30 s’auto-attribuent une adresse ou ne reçoivent aucun bail. Le serveur DHCP semble actif.

1. Confirmez le périmètre avec plusieurs clients du VLAN 30 et un client de référence.
2. Vérifiez le VLAN réellement affecté aux ports et le trunk jusqu’à la passerelle.
3. Vérifiez l’interface VLAN, son état et la configuration du relais DHCP (`ip helper-address` lorsque cette méthode est utilisée).
4. Contrôlez qu’une portée correspond au sous-réseau du VLAN 30 et qu’elle dispose d’adresses libres.
5. Avec une capture autorisée, observez l’arrivée du Discover, l’émission de l’Offer et le retour vers le client.
6. Vérifiez les journaux, les options de passerelle et de DNS, ainsi que les politiques de filtrage DHCP.

Ne créez pas une nouvelle plage d’adresses sans vérifier l’absence de chevauchement et sans connaître les options attendues. Ne supprimez pas les baux existants pour tenter de forcer les clients à renouveler : cela peut amplifier l’incident et compliquer l’analyse.

### 3.6 Cas pratique F — Le nom fonctionne depuis le LAN, pas depuis le VPN

Cette différence est souvent liée au split DNS, à l’accès au serveur DNS interne, aux suffixes de recherche ou à des réponses différentes selon la source. Mais il faut d’abord identifier quel résolveur est utilisé dans les deux contextes. Un navigateur peut aussi garder des connexions et caches actifs indépendamment du cache DNS du système.

Comparez `Resolve-DnsName` ou l’outil correspondant sans et avec VPN, le serveur DNS utilisé, les enregistrements A/AAAA, les TTL et la route vers le résolveur. Vérifiez que le tunnel autorise DNS vers le serveur prévu et que la route de retour existe. Ensuite, comparez la connexion au service à l’adresse obtenue tout en considérant TLS/SNI et l’hébergement virtuel.

Ne résolvez pas durablement le problème avec une entrée manuelle dans `hosts` ou un DNS public, car cela peut contourner la politique interne, produire des résultats incohérents et masquer la cause. Le bon résultat est une résolution fiable via les mécanismes approuvés.

### 3.7 Transformer l’incident en compte rendu exploitable

Un compte rendu technique comprend :

- **Résumé métier :** qui a été affecté, quel service, pendant combien de temps.
- **Périmètre :** sites, VLAN, appareils, adresses et flux touchés.
- **Chronologie :** début observé, alertes, modifications, tests, correction et validation.
- **Observations :** sorties de commandes, extraits de journaux et captures référencées, avec horodatage.
- **Hypothèses testées :** test, résultat attendu, résultat constaté et conséquence pour chaque hypothèse.
- **Cause racine :** mécanisme confirmé, ou mention explicite du degré d’incertitude s’il reste des points à vérifier.
- **Action de rétablissement :** changement exact, responsable, approbation et retour arrière possible.
- **Prévention :** supervision, capacité, documentation, tests de changement ou correction durable.

Distinguez la cause immédiate et les conditions qui ont permis l’incident. Exemple : la panne immédiate est une règle qui oublie le nouveau sous-réseau ; la cause organisationnelle peut être l’absence de tests de flux après l’ajout du VLAN. Une recommandation préventive doit être actionnable, avoir un propriétaire et être suivie dans le temps.

### 3.8 Escalade efficace entre équipes

Une escalade vers le serveur, la sécurité, le fournisseur ou l’équipe WAN doit contenir des preuves ciblées. Évitez de transmettre uniquement « le réseau ne marche pas ». Indiquez la source, la destination, le port, l’heure avec fuseau, le type d’échec, les tests comparatifs et le point où la trace change.

Pour une escalade serveur, il est utile de préciser si la connexion atteint l’hôte, si le service écoute et si une réponse est envoyée. Pour le pare-feu, fournissez le tuple avant/après NAT si pertinent et l’identifiant de session ou de règle. Pour l’opérateur, fournissez la période, les points d’extrémité, la mesure répétée, les erreurs d’interface disponibles et les identifiants des circuits sans exposer inutilement les données de sécurité.

Énoncez ce qui a été exclu et comment. « Le DNS a renvoyé la même adresse depuis les deux VLAN ; le SYN est visible côté client et absent sur la capture serveur à l’heure correspondante » est plus utile que « on a testé tout ». Évitez de déclarer une équipe responsable avant d’avoir identifié la frontière où le comportement diffère.

### 3.9 Hygiène de sécurité pendant les opérations

Le dépannage peut accroître le risque si le technicien contourne des mécanismes de contrôle. Les règles suivantes s’appliquent :

- privilégier l’observation non intrusive avant les changements ;
- limiter les captures à une source, une destination et une durée utiles ;
- ne jamais divulguer les secrets présents dans des configurations ou des journaux ;
- préserver les preuves lorsqu’un incident peut être lié à une compromission ;
- faire approuver les changements et prévoir un retour arrière ;
- éviter les ouvertures temporaires trop larges et les désactivations de sécurité globales ;
- vérifier que les commandes de debug ou de collecte sont arrêtées après la fenêtre de test ;
- consigner l’identité de l’opérateur, les heures, les actions et le résultat.

Si les indices suggèrent une activité malveillante, une fuite de données ou un changement non autorisé, suivez le processus de réponse à incident de l’organisation et impliquez l’équipe sécurité. Une restauration précipitée à l’état « normal » peut détruire des preuves. Le dépannage de disponibilité et l’investigation de sécurité doivent être coordonnés.

> **Danger :** la pression pour rétablir le service ne justifie pas une modification non autorisée, un redémarrage aveugle ou une désactivation temporaire de toutes les règles. Une action rapide mais non contrôlée peut provoquer une panne plus large, créer une brèche ou rendre la cause racine indémontrable.

### 3.10 Indicateurs de fin d’investigation

Un incident est prêt à être clôturé lorsque le service est validé dans des conditions équivalentes au symptôme initial, que l’impact restant est connu, que les parties concernées sont informées et que le compte rendu permet de retracer les tests et changements. Il n’est pas nécessaire que toute incertitude théorique disparaisse, mais elle doit être documentée.

Pour une panne intermittente, une courte période sans récidive peut être insuffisante. Définissez une période de surveillance adaptée à la fréquence du problème : si l’incident revenait toutes les heures, une validation de deux minutes n’est pas convaincante. Utilisez les métriques qui révélaient le symptôme et indiquez clairement ce que la fenêtre d’observation permet d’affirmer.

Une cause racine peut aussi rester probable mais non confirmée si les preuves manquent. Dans ce cas, dites-le : « le service a été rétabli par la correction X ; les données disponibles suggèrent Y, mais la capture n’a pas été réalisée au point Z ». La transparence est plus utile qu’une certitude inventée.

---

## Points à retenir

- Une hypothèse utile décrit un mécanisme et un résultat observable qui la renforcerait ou la réfuterait.
- Avant de lancer les outils, identifiez le tuple de flux, la direction, l’heure, le contexte et le point de référence.
- Distinguez le plan de contrôle, le plan de données et le plan de gestion ; l’accès à un équipement ne prouve pas que le trafic transitant fonctionne.
- Un timeout, un refus et un reset TCP sont des symptômes distincts qui orientent les tests sans établir seuls la cause.
- Les captures doivent être réalisées pour répondre à une question et leurs points de collecte doivent être documentés.
- Les filtres de capture et d’affichage Wireshark ne sont pas interchangeables.
- Un handshake TCP réussi suivi d’un blocage peut être lié au MTU/PMTUD, à TLS, à la perte, à l’application ou à l’inspection ; il faut observer l’étape précise de l’échec.
- Le DNS dépend du résolveur réel, des caches, du split DNS, des enregistrements A/AAAA, de la politique et du contexte VPN.
- Pour DHCP, déterminez où l’échange s’arrête : client, VLAN, relais, serveur ou retour.
- En couche 2, comparez VLAN, trunks, tables MAC, STP, EtherChannel et compteurs d’interface sans désactiver les protections.
- Analysez les routes aller et retour, la PBR, les VRF, le NAT et les dispositifs stateful ; la route par défaut ne suffit pas.
- Les compteurs doivent être mesurés dans le temps ; une valeur cumulée ne prouve pas une erreur active.
- Une panne IPv4/IPv6 différenciée demande des tests distincts pour chaque famille, notamment pour DNS, routage et ICMPv6.
- Changez le minimum nécessaire, une variable à la fois, et répétez le test initial après correction.
- Préservez les journaux, les captures et les secrets ; ne désactivez pas globalement la sécurité pour tester une hypothèse.
- Documentez la cause, les limites de preuve, le changement, le retour arrière, la validation et les actions préventives.

### Checklist de dépannage intermédiaire

```text
[ ] Le symptôme, l’impact, l’heure et le périmètre sont établis.
[ ] Le flux exact (source, destination, protocole, ports, direction) est défini.
[ ] Les tests attendus sont écrits avant leur exécution.
[ ] Les observations initiales et les horloges des appareils sont consignées.
[ ] Plusieurs hypothèses concurrentes ont été comparées.
[ ] Les captures/logs sont limitées, sécurisées et synchronisées autant que possible.
[ ] Le chemin aller et le chemin retour ont été examinés.
[ ] DNS, DHCP, TCP, MTU, VLAN, routage et filtrage sont étudiés selon les indices.
[ ] Les compteurs ont été comparés sur un intervalle pertinent.
[ ] Aucune commande intrusive n’a été lancée sans autorisation et plan de sortie.
[ ] Le changement cible le mécanisme démontré et possède un retour arrière.
[ ] Le test initial a été répété et les fonctions voisines ont été validées.
[ ] Les hypothèses restantes, la cause et les actions préventives sont documentées.
```

### Exercices d’auto-évaluation

**Exercice 1 — SYN sans réponse.** La capture côté client montre trois SYN vers TCP/443 sans SYN-ACK. Peut-on conclure que le serveur est en panne ?

**Corrigé :** non. Le SYN peut être filtré, perdu, routé vers une autre destination, ou la réponse peut être perdue sur le retour. Capturez côté serveur ou consultez les journaux du point de sécurité. L’absence du SYN au serveur localise le problème avant ce point, sous réserve de la validité de la capture.

**Exercice 2 — Le nom renvoie une adresse différente en VPN.** Quelle vérification doit précéder toute modification d’ACL ?

**Corrigé :** confirmer le résolveur réellement utilisé, les réponses A/AAAA, le split DNS et la destination choisie par l’application. Tant que les deux tests ne ciblent pas le même service/adresse, une comparaison de filtrage peut être trompeuse.

**Exercice 3 — TCP s’établit, transfert bloqué après quelques octets.** Citez trois hypothèses et une preuve discriminante pour chacune.

**Corrigé :** (1) MTU/PMTUD : transfert dépendant de la taille et messages ICMP/ICMPv6 ou retransmissions de gros segments ; (2) service applicatif bloqué : capture montrant l’absence de données côté serveur et journaux applicatifs cohérents ; (3) inspection/proxy : journal de session ou capture montrant un reset émis par le dispositif. Les preuves doivent être collectées aux points adaptés.

**Exercice 4 — Cent erreurs CRC anciennes.** Pourquoi la valeur absolue est-elle insuffisante ?

**Corrigé :** le compteur peut être cumulatif depuis le dernier reset et ne pas augmenter actuellement. Relevez la valeur puis comparez après un intervalle. Si elle progresse avec le symptôme, inspectez câble, connectique, transceiver et port selon la procédure de maintenance.

**Exercice 5 — Une seule destination est lente via ECMP.** Que faut-il comparer ?

**Corrigé :** les tuples des flux, le next-hop et les interfaces empruntées, les compteurs par chemin, les pertes/retransmissions et les événements à la même heure. Deux connexions vers le même service peuvent être hachées vers des chemins différents.

**Exercice 6 — Un ping échoue mais l’application marche.** Quelle conclusion est autorisée ?

**Corrigé :** seulement que la sonde ICMP n’a pas obtenu de réponse dans ces conditions. Le trafic applicatif peut être autorisé alors qu’ICMP est filtré ou limité. Ne déduisez pas une panne du service sans tester le protocole réellement utilisé.

**Exercice 7 — Le VLAN 30 ne reçoit pas d’adresse DHCP.** Comment séparer relais, portée et retour ?

**Corrigé :** observez le Discover sur le VLAN client, son arrivée côté serveur, l’Offer éventuelle et le retour vers le client. Contrôlez le relais et l’identification du réseau client, la portée et ses journaux, puis le chemin de retour et les politiques de filtrage.

**Exercice 8 — Une ouverture temporaire globale fait fonctionner le service.** Que prouve ce test et que ne prouve-t-il pas ?

**Corrigé :** il suggère un lien avec le filtrage, mais une ouverture trop large ne prouve pas quelle règle ou quel flux est en cause. Revenez à un changement ciblé, identifiez le flux et les journaux, et n’utilisez pas cette ouverture comme solution permanente.

**Exercice 9 — Une commande de debug produit beaucoup de messages.** Que faire ?

**Corrigé :** si cela dépasse le cadre autorisé ou affecte l’équipement, arrêtez le debug selon la documentation de la plateforme, vérifiez l’état de l’équipement et consignez l’action. À l’avenir, privilégiez une collecte ciblée et une fenêtre courte après analyse du risque.

**Exercice 10 — L’incident ne s’est pas reproduit pendant cinq minutes.** Peut-on le clôturer ?

**Corrigé :** cela dépend de la fréquence habituelle du symptôme et de la criticité. Si le problème apparaissait toutes les heures, cinq minutes ne suffit probablement pas. La période de validation doit être annoncée et cohérente avec les métriques qui révélaient l’incident.

### Références techniques

1. Cisco, **Troubleshooting Overview / Troubleshooting and Maintenance** : https://www.cisco.com/c/en/us/support/docs.html
2. Wireshark, **Display Filters** : https://wiki.wireshark.org/DisplayFilters
3. Wireshark, **Capture Filters** : https://wiki.wireshark.org/CaptureFilters
4. IETF, **RFC 9293 — Transmission Control Protocol (TCP)** : https://www.rfc-editor.org/rfc/rfc9293.html
5. IETF, **RFC 1191 — Path MTU Discovery** : https://www.rfc-editor.org/rfc/rfc1191.html
6. IETF, **RFC 8201 — Path MTU Discovery for IP version 6** : https://www.rfc-editor.org/rfc/rfc8201.html
7. IETF, **RFC 1034 — Domain Names: Concepts and Facilities** : https://www.rfc-editor.org/rfc/rfc1034.html
8. IETF, **RFC 1035 — Domain Names: Implementation and Specification** : https://www.rfc-editor.org/rfc/rfc1035.html
9. IETF, **RFC 2131 — Dynamic Host Configuration Protocol** : https://www.rfc-editor.org/rfc/rfc2131.html
10. IETF, **RFC 792 — Internet Control Message Protocol** : https://www.rfc-editor.org/rfc/rfc792.html
11. NIST, **SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management** : https://csrc.nist.gov/pubs/sp/800/61/r3/final

Les RFC décrivent les comportements de protocole ; elles ne remplacent ni les guides spécifiques à l’équipement, ni les procédures de sécurité et de changement de l’organisation. Les outils, options et sorties présentés dans ce cours varient selon la version du système, le modèle réseau et les droits disponibles. En production, vérifiez les commandes dans la documentation correspondant exactement à la plateforme.
