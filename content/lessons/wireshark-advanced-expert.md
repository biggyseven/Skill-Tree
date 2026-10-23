# Wireshark avancé — Diagnostic réseau de niveau expert

> **Encadré de mise en contexte**
>
> **Niveau :** Expert  
> **Place dans la série :** ce module prolonge les bases de capture, les filtres d’affichage, la lecture des échanges Ethernet/IP/TCP/UDP et les premiers diagnostics protocolaires. Il ne recommence pas depuis zéro : il transforme ces acquis en méthode d’investigation reproductible, capable de distinguer un fait observé d’une hypothèse.
>
> **Public visé :** ingénieurs réseau, SRE, administrateurs systèmes, analystes sécurité et personnes chargées d’incidents difficiles à reproduire.
>
> **Prérequis :** savoir choisir une interface de capture, appliquer des filtres de capture et d’affichage, suivre un flux TCP, interpréter les champs IPv4/IPv6, DNS et TLS, et exporter une capture pcapng.
>
> **Objectifs opérationnels :** établir une chaîne de preuve, analyser les symptômes TCP sans surinterpréter les annotations Wireshark, diagnostiquer MTU/PMTUD, TLS, DNS et asymétrie, maîtriser les filtres avancés, corréler plusieurs captures et produire un rapport technique vérifiable.
>
> **Environnement de laboratoire :** Wireshark récent, captures pcapng issues d’un environnement autorisé, deux points de capture si possible, et accès aux journaux systèmes correspondants. Les exemples d’adresses et de chronologies sont pédagogiques.
>
> **Règle de méthode :** aucune étiquette d’analyse ne remplace la vérification du paquet, de son contexte, de la topologie et du point où il a été capturé.

## 1. L’état d’esprit expert : observer, prouver, limiter

Un analyste débutant cherche souvent « le paquet qui explique la panne ». Un analyste expert construit plutôt une chaîne d’arguments. Il détermine d’abord ce que la capture pouvait voir, identifie ensuite les événements établis, compare plusieurs explications possibles, puis formule une conclusion proportionnée aux données disponibles.

Une capture n’est jamais une copie omnisciente du réseau. Elle dépend du point de capture, de la direction observée, des pertes du système de capture, de la taille de capture (*snap length*), des fonctions d’offload de la carte réseau, de la synchronisation des horloges et de la capacité du décodeur à reconnaître le protocole. Une absence de paquet dans le fichier signifie d’abord « paquet non observé dans cette capture », et non « paquet inexistant sur le réseau ».

![Pipeline d'analyse expert Wireshark](schemas/pipeline-analyse.svg)

### 1.1 Distinguer les niveaux de certitude

Dans le rapport, classez chaque énoncé dans l’une de ces catégories :

- **Observation :** « Le fichier contient un segment TCP avec `Seq=...`, capturé à 12:03:14.221. »
- **Interprétation protocolaire :** « Le segment porte le drapeau RST ; l’émetteur visible dans cette capture est l’adresse X. »
- **Hypothèse :** « Un équipement intermédiaire pourrait rejeter la connexion. »
- **Conclusion corroborée :** « La capture côté client montre le SYN sortant ; la capture côté serveur ne le montre pas, tandis que les compteurs de l’équipement intermédiaire indiquent un rejet correspondant. »
- **Limite :** « La capture ne couvre pas le segment entre le routeur et le serveur ; elle ne permet pas de localiser précisément la perte à elle seule. »

L’expertise se manifeste moins par le nombre de filtres connus que par la qualité de la preuve et la précision des limites annoncées.

### 1.2 Préserver la provenance de la capture

Avant toute analyse, conservez le fichier original en lecture seule, calculez un hash cryptographique, notez l’heure de collecte, le fuseau, l’interface, le point réseau, le filtre de capture, la version de Wireshark/dumpcap, la taille maximale des paquets et les compteurs de paquets perdus si disponibles. Travaillez sur une copie et consignez les transformations : découpage, fusion, export des objets ou anonymisation.

Le format pcapng peut contenir des informations par interface et des horodatages utiles, mais leur présence ne garantit pas que les horloges des différents capteurs soient synchronisées. Un hash prouve l’intégrité du fichier depuis son calcul ; il ne prouve ni l’exhaustivité de la capture ni l’exactitude de l’horloge.

## 2. Une méthode d’investigation reproductible

Utilisez un protocole de travail constant afin de réduire les biais de confirmation.

1. **Définir le symptôme.** Qui est affecté ? Depuis quand ? Quel nom DNS, quelle adresse, quel port, quel protocole et quel résultat attendu ?
2. **Délimiter la transaction.** Identifier client, serveur, proxy, NAT, répartiteur de charge, VPN et éventuels chemins différents.
3. **Valider la qualité de la capture.** Examiner les compteurs de drops, les paquets tronqués, les horodatages et les interfaces.
4. **Trouver la première divergence.** Comparer le déroulement attendu avec celui qui est réellement visible. La première anomalie apparente n’est pas nécessairement la cause racine.
5. **Formuler au moins deux hypothèses.** Pour chaque hypothèse, préciser ce qui devrait être observé si elle était vraie et ce qui l’infirmerait.
6. **Chercher une corroboration indépendante.** Deuxième point de capture, journaux, compteurs d’interface, métriques applicatives ou traces système.
7. **Reproduire si possible.** Modifier une variable à la fois : réseau, MTU, DNS, version TLS, chemin ou charge.
8. **Rédiger une conclusion limitée aux faits.** Inclure les éléments qui soutiennent la conclusion, les explications alternatives écartées et les inconnues restantes.

### 2.1 Le choix du point de capture

Une capture sur le client permet de voir ce que la pile réseau du client présente à l’interface de capture, mais pas nécessairement ce qui arrive sur le fil après les transformations matérielles. Une capture sur le serveur observe l’autre extrémité. Une capture sur un port miroir dépend de la configuration SPAN/TAP, de la congestion du miroir et du comportement du commutateur.

Pour localiser une perte, capturez simultanément des deux côtés d’un segment lorsque c’est possible. Corrélez les paquets par adresses, ports, séquences TCP, identifiants utiles et empreintes de contenu, en tenant compte du NAT et des transformations intermédiaires. Si les horloges ne sont pas alignées, les temps absolus peuvent être trompeurs ; les séquences et l’ordre local restent souvent plus robustes.

## 3. Filtres avancés : précision sans faux sentiment de certitude

Les filtres d’affichage et les filtres de capture ont des rôles différents. Un filtre d’affichage masque des paquets dans la vue sans les supprimer du fichier. Un filtre de capture décide en amont quels paquets sont enregistrés ; une erreur de filtre peut rendre impossible l’examen ultérieur d’un événement manquant.

### 3.1 Filtres d’affichage utiles

| Intention | Filtre d’affichage |
|---|---|
| Hôte source ou destination | `ip.addr == 192.0.2.10` |
| IPv6 d’un endpoint | `ipv6.addr == 2001:db8::10` |
| Port TCP | `tcp.port == 443` |
| SYN initial sans ACK | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| RST TCP | `tcp.flags.reset == 1` |
| Retransmissions signalées par l’analyse TCP | `tcp.analysis.retransmission` |
| Dup ACK signalés | `tcp.analysis.duplicate_ack` |
| Fenêtre TCP nulle | `tcp.window_size_value == 0` |
| DNS en erreur | `dns.flags.rcode != 0` |
| ClientHello TLS | `tls.handshake.type == 1` |
| Alertes TLS | `tls.alert_message` |
| Paquets IPv4 avec bit DF | `ip.flags.df == 1` |
| ICMPv4 destination inaccessible | `icmp.type == 3` |
| ICMPv6 Packet Too Big | `icmpv6.type == 2` |

Les champs disponibles peuvent varier selon la version et le dissector. Si un champ ne fonctionne pas, utilisez l’autocomplétion de la barre de filtre, ouvrez l’arbre de détails du paquet et vérifiez le nom exact du champ. Une expression valide peut aussi renvoyer zéro résultat simplement parce que la capture ne contient pas le protocole recherché.

### 3.2 Construire une expression complexe

Exemple : examiner les connexions HTTPS d’un hôte tout en repérant les anomalies TCP :

```wireshark
ip.addr == 192.0.2.10 &&
tcp.port == 443 &&
(tcp.flags.reset == 1 || tcp.analysis.retransmission)
```

Pour limiter l’analyse à un échange DNS avec un code de réponse non nul :

```wireshark
dns && dns.flags.response == 1 && dns.flags.rcode != 0
```

N’empilez pas les conditions au hasard. Commencez par une expression large, vérifiez les résultats, puis ajoutez une contrainte à la fois. Pour documenter une analyse, enregistrez les filtres utilisés et indiquez si les résultats reposent sur un filtre d’affichage ou un filtre de capture.

### 3.3 Champs, valeurs et conversations

Les noms de champs sont préférables aux recherches textuelles approximatives. `tcp.port == 443` interroge une valeur protocolaire décodée ; une recherche de la chaîne « 443 » peut trouver un nombre sans rapport dans une charge utile. Utilisez **Statistics → Conversations**, **Endpoints**, **Protocol Hierarchy**, **I/O Graphs** et **Flow Graph** comme vues complémentaires, non comme substituts à la lecture des paquets.

Le suivi de flux TCP reconstitue les données observées dans le flux. Il ne garantit pas que les octets étaient disponibles à l’application au même instant, ni que la capture contient chaque segment. Avec TLS, le suivi montre généralement des enregistrements chiffrés, sauf si un mécanisme de déchiffrement autorisé est correctement configuré.

## 4. TCP en profondeur : séquences, ACK, fenêtres et temps

TCP est un flux d’octets, pas une suite de messages applicatifs. Les segments transportent des plages de séquence ; les ACK sont généralement cumulatifs et indiquent le prochain octet attendu. SACK peut signaler des blocs reçus hors ordre, sans transformer l’ACK cumulatif en accusé individuel de chaque segment.

![Chronologie TCP](schemas/chronologie-tcp.svg)

### 4.1 Analyser une retransmission sans surinterpréter

Wireshark ajoute des annotations d’analyse TCP, par exemple retransmission, retransmission rapide, ACK dupliqué ou segment hors ordre. Elles sont extrêmement utiles, mais ce sont des inférences calculées à partir de la capture et de son contexte. Elles ne constituent pas une preuve automatique de perte sur le réseau.

Une retransmission peut être compatible avec plusieurs scénarios : perte du segment, perte de l’ACK, réordonnancement, délai inhabituel, capture incomplète, visibilité unidirectionnelle ou effets des offloads. Pour décider, vérifiez :

- la séquence et la longueur des données ;
- les ACK reçus avant et après le segment suspect ;
- l’existence éventuelle de SACK ;
- les intervalles temporels et le seuil de retransmission ;
- la direction de la capture et la présence des deux sens ;
- les duplications éventuelles causées par un port miroir ;
- les métriques et traces de l’autre endpoint.

Un ACK dupliqué ne signifie pas toujours qu’un segment est perdu : il peut être provoqué par une arrivée hors ordre. Un « fast retransmission » indique que l’algorithme de l’émetteur a probablement réagi à des ACK répétés, mais la capture doit être suffisamment complète pour que cette interprétation soit solide.

### 4.2 Fenêtre annoncée et contrôle de congestion

La fenêtre annoncée par le récepteur représente la quantité de données qu’il est prêt à recevoir, après prise en compte du facteur d’échelle négocié pendant l’établissement de la connexion. La fenêtre de congestion de l’émetteur est un état local de contrôle de congestion et n’est généralement pas directement visible comme une valeur explicite dans chaque paquet.

Une fenêtre nulle peut indiquer que le récepteur ne dispose momentanément plus d’espace tampon. Observez les annonces de fenêtre, les sondes de fenêtre persistante, les délais entre la fenêtre nulle et sa réouverture et la charge applicative. Ne concluez pas immédiatement à une panne réseau : un processus qui lit lentement les données, une saturation de ressources ou une application bloquée peuvent produire le même symptôme.

### 4.3 RST, fermeture normale et demi-fermeture

FIN signifie qu’un côté a terminé l’envoi de données dans un sens ; il ne ferme pas nécessairement immédiatement le sens opposé. RST réinitialise la connexion. Pour attribuer un RST, vérifiez son adresse source visible, le contexte de séquence et la topologie. Un pare-feu, un proxy ou un équipement intermédiaire peut produire un RST qui semble venir de l’endpoint à cause de l’adresse source ou du chemin observé.

Ne déduisez pas l’identité du processus émetteur à partir du seul paquet. Il faut des journaux endpoint, des données de socket ou des traces système pour rattacher un événement réseau à un processus.

### 4.4 Offloads et paquets qui semblent impossibles

Les fonctions TSO/GSO peuvent faire apparaître, dans une capture prise avant segmentation, de gros blocs TCP qui dépassent la MTU de l’interface. GRO/LRO peut agréger plusieurs segments à la réception. Les sommes de contrôle peuvent sembler incorrectes lorsqu’elles sont vérifiées avant que le matériel ait rempli les champs correspondants.

Avant de déclarer un paquet malformé ou une MTU violée, documentez l’interface de capture et les offloads actifs. Si nécessaire, faites une capture à un point matériel différent ou désactivez temporairement un offload dans un laboratoire contrôlé, en notant l’impact sur les performances. Une capture logicielle locale n’est pas toujours identique aux trames réellement transmises sur le média.

## 5. MTU, MSS et PMTUD : diagnostiquer les pannes sélectives

Les pannes de MTU sont particulièrement trompeuses : l’établissement TCP et les petites requêtes réussissent, mais les transferts plus volumineux se bloquent. La MTU est la taille maximale du paquet de couche réseau transportable sur un lien donné ; la MSS TCP décrit la quantité maximale de données TCP dans un segment, sans compter les en-têtes IP et TCP. Les options TCP et les en-têtes IPv6 peuvent modifier la relation pratique entre ces valeurs.

### 5.1 PMTUD classique et variantes

Avec IPv4, le mécanisme classique Path MTU Discovery utilise le bit DF et les messages ICMP « Fragmentation Needed » pour informer l’émetteur qu’un paquet ne peut pas traverser un lien sans fragmentation. Si ces messages ICMP sont bloqués, le chemin peut devenir une « black hole MTU » : les petits paquets passent, tandis que les paquets plus gros disparaissent sans retour exploitable.

Avec IPv6, les routeurs ne fragmentent pas les paquets en transit. Ils peuvent envoyer ICMPv6 Packet Too Big ; le nœud source adapte alors la taille d’envoi ou fragmente selon les règles IPv6. Bloquer ICMPv6 de façon indiscriminée peut donc casser des communications légitimes et des fonctions de découverte essentielles.

PLPMTUD (*Packetization Layer Path MTU Discovery*) cherche à inférer la MTU utilisable à la couche de paquetisation, au moyen de sondes et d’observations de livraison, et peut mieux résister à certains filtrages ICMP. Le comportement exact dépend de l’implémentation et du protocole.

### 5.2 Signes dans Wireshark

- SYN et SYN/ACK visibles, puis données volumineuses qui cessent d’avancer.
- Retransmissions répétées des mêmes plages de séquence.
- ICMPv4 Destination Unreachable / Fragmentation Needed, ou ICMPv6 Packet Too Big, éventuellement absent au point de capture.
- Succès des petites requêtes et échec des réponses volumineuses.
- Différence de comportement selon le VPN, le tunnel, le chemin IPv4/IPv6 ou le réseau d’accès.
- MSS annoncée compatible avec un lien local mais incompatible avec l’encapsulation réelle sur le chemin.

Ces signes ne suffisent pas isolément. Une congestion, une perte, un filtrage, une limitation applicative ou un problème de serveur peuvent ressembler à un problème de MTU. La preuve la plus forte vient de la corrélation entre tailles de paquets, événement ICMP, comportement de retransmission et résultat d’un test contrôlé.

### 5.3 Procédure de diagnostic

1. Comparez une transaction courte et une transaction qui échoue, en conservant les mêmes endpoints et le même protocole.
2. Relevez les MSS dans le SYN et le SYN/ACK, puis tenez compte des en-têtes réels et des éventuels tunnels.
3. Filtrez les paquets ICMP pertinents et examinez le contenu cité dans l’erreur, lorsqu’il est présent.
4. Capturez simultanément avant et après le tunnel ou le segment suspect.
5. Réalisez des tests de taille progressive avec un outil adapté et autorisé. Ne supposez pas qu’un ping bloqué prouve une panne ICMP ou une MTU erronée.
6. Si une réduction temporaire de MTU/MSS fait disparaître le symptôme, traitez-la comme un indice fort, puis trouvez le segment ou la règle responsable.
7. Vérifiez la configuration ICMP, les politiques de tunnel et les limites de MTU de bout en bout avant de conclure.

### 5.4 Fragmentation : ce que la capture permet d’affirmer

Pour IPv4, examinez le champ Fragment Offset et le drapeau More Fragments ; l’identification sert à associer les fragments d’un même datagramme dans le contexte approprié. Le premier fragment contient l’en-tête transport, mais les fragments suivants ne portent pas nécessairement un en-tête TCP/UDP complet. Les fragments peuvent arriver dans le désordre ou être perdus, et la réassemblage dépend des données disponibles.

Pour IPv6, examinez l’en-tête Fragment et les en-têtes d’extension. Une capture tronquée ou un filtre de capture trop restrictif peut empêcher le réassemblage. Évitez d’affirmer qu’un paquet est absent du chemin si la capture n’enregistre qu’une partie des fragments ou si le point d’observation est après réassemblage.

## 6. TLS : isoler la négociation, le certificat et l’application

TLS ajoute une couche de sécurité au-dessus du transport. Wireshark peut analyser une grande partie de la négociation visible, mais le contenu applicatif reste chiffré sans secrets de session appropriés et autorisés. Le fait qu’un paquet TLS soit visible ne signifie pas que le contenu HTTP soit disponible.

![Arbre de diagnostic TLS](schemas/arbre-diagnostic-tls.svg)

### 6.1 Ordre d’analyse

1. Confirmez que TCP s’établit correctement.
2. Localisez le ClientHello et examinez les versions proposées, les suites cryptographiques, les extensions, le SNI si visible, ALPN et les groupes pris en charge.
3. Identifiez les messages de négociation réellement présents : ServerHello, messages d’authentification, Finished et alertes éventuelles.
4. Relevez qui envoie l’alerte dans le point de capture observé, puis vérifiez si le flux est complet.
5. Si la négociation réussit, examinez la couche applicative, les délais, les codes de réponse et les échanges avec le proxy ou le backend.

Avec TLS 1.3, une partie importante des messages après ServerHello est chiffrée. L’absence d’un message lisible dans l’arbre de paquets n’indique donc pas nécessairement qu’il n’a pas été envoyé. Les versions récentes de TLS, les mécanismes de confidentialité du ClientHello et les variations d’implémentation peuvent également limiter ce qui est visible.

### 6.2 Déchiffrement autorisé

Pour analyser le contenu TLS dans un environnement dont vous avez l’autorisation, Wireshark peut utiliser un fichier de secrets de session, par exemple un fichier de clés exporté par l’application cliente via un mécanisme compatible. Le certificat serveur seul ne suffit généralement pas à déchiffrer les sessions modernes utilisant l’échange de clés éphémères.

Protégez le fichier de secrets comme une donnée hautement sensible : il peut permettre de lire le contenu des sessions capturées correspondantes. Évitez de l’inclure dans un rapport ou de le partager avec la capture. Vérifiez que les secrets correspondent à la session et que la capture contient les messages nécessaires. Un déchiffrement réussi dans Wireshark est une aide à l’analyse, pas une autorisation à consulter des données qui ne vous appartiennent pas.

### 6.3 Certificats, SNI et ALPN

Un échec TLS peut provenir d’un nom d’hôte incohérent, d’un certificat expiré ou non approuvé, d’une horloge incorrecte, d’une politique de versions, d’une incompatibilité de suites ou d’un intermédiaire qui termine TLS. La capture ne révèle pas toujours la cause exacte ; confrontez-la aux journaux du client et du serveur.

SNI permet généralement au client d’indiquer le nom de serveur souhaité pendant la négociation, lorsqu’il est visible. ALPN permet de négocier un protocole applicatif comme HTTP/2. Si le client et le serveur choisissent des protocoles différents de ceux attendus, l’application peut échouer même lorsque la négociation cryptographique a réussi.

## 7. DNS : distinguer résolution, transport et cache

Une panne « DNS » peut désigner plusieurs phénomènes : requête non envoyée, perte, absence de réponse, réponse négative, serveur inaccessible, réponse lente, cache obsolète, divergence entre résolveurs, DNS chiffré ou application qui utilise une adresse déjà mise en cache. Déterminez d’abord si la capture observe le client vers le résolveur ou le résolveur vers l’autorité.

### 7.1 Lecture d’un échange

Vérifiez l’identifiant de transaction dans le contexte du transport, les noms interrogés, le type de requête, le drapeau QR, le code RCODE, les sections Answer/Authority/Additional et le temps entre requête et réponse. Une réponse NXDOMAIN signifie que le nom interrogé n’existe pas selon le serveur qui répond ; SERVFAIL signifie que le résolveur n’a pas pu fournir une réponse exploitable. REFUSED indique un refus de traitement. Les causes profondes exigent souvent les journaux du résolveur ou des autorités.

DNS peut utiliser UDP ou TCP. La troncature d’une réponse UDP peut provoquer une nouvelle tentative en TCP. DNS over TLS et DNS over HTTPS chiffrent le transport DNS et ne seront pas décodés comme DNS ordinaire sans visibilité ou déchiffrement approprié.

### 7.2 Filtres et questions utiles

```wireshark
dns
dns.flags.response == 1 && dns.flags.rcode != 0
dns.qry.name contains "example"
udp.port == 53 || tcp.port == 53
```

Demandez-vous si la requête part réellement, si elle arrive au résolveur, si une réponse revient, si elle correspond à la requête, si le client l’accepte et si l’application utilise effectivement ce résultat. Ne concluez pas à un cache défectueux à partir d’une seule réponse : comparez TTL, résolveurs, clients et chronologie.

## 8. IPv4/IPv6, ICMP et chemins asymétriques

Une application peut préférer IPv6, échouer sur ce chemin puis retomber sur IPv4 — ou ne pas retomber assez rapidement. Pour comparer les chemins, identifiez les adresses réellement utilisées, les tentatives concurrentes et les délais de connexion. Une capture limitée à IPv4 ne permet pas de conclure sur le comportement IPv6.

ICMP n’est pas uniquement un protocole de diagnostic « facultatif ». Des messages ICMP utiles au fonctionnement IP peuvent être nécessaires à la découverte de MTU et à la gestion d’erreurs. Les bloquer tous peut provoquer des pannes difficiles à reconnaître. Interprétez chaque message avec son type, son code, son contenu cité et le point où il est capturé.

L’asymétrie peut être normale en présence de routage multipath, de répartition de charge, de NAT ou de chemins différents à l’aller et au retour. Elle devient un problème lorsque des états réseau, des ACL ou des mécanismes stateful supposent un chemin symétrique. Pour l’établir, comparez les observations aux frontières du réseau et documentez les transformations d’adresse et de port.

## 9. Capture multipoint et corrélation temporelle

Une analyse multipoint exige une stratégie de corrélation. Les horloges NTP/PTP réduisent l’écart, mais il faut mesurer ou borner l’erreur. Un paquet observé à 10:00:00.010 sur le client et à 10:00:00.002 sur le serveur ne signifie pas qu’il a voyagé dans le temps : l’écart peut refléter une désynchronisation.

### 9.1 Procédure

- Décrivez précisément chaque capteur : interface, sens, position topologique et configuration.
- Synchronisez les horloges et notez la méthode ainsi que l’incertitude connue.
- Identifiez les transformations entre les points : NAT, tunnel, proxy, réécriture, segmentation et agrégation.
- Corrélez avec les séquences TCP, les tailles, les drapeaux et les données communes.
- Établissez une chronologie locale par capteur avant de comparer les temps absolus.
- Recherchez la première frontière où un événement attendu cesse d’être observé.
- Vérifiez que le capteur n’a pas perdu de paquets et que le miroir n’a pas été surchargé.

La fusion de fichiers peut faciliter la visualisation mais ne corrige pas les horloges et ne supprime pas les ambiguïtés. Conservez les fichiers originaux et consignez la méthode de fusion.

## 10. Performance : latence, débit, files d’attente et temps applicatif

Une durée élevée entre une requête et une réponse n’identifie pas automatiquement la couche responsable. Elle peut inclure la latence réseau, le traitement serveur, une file d’attente, un verrou applicatif, un délai de proxy ou un comportement du client. Il faut séparer les intervalles mesurables et comparer plusieurs transactions.

Utilisez les graphiques d’E/S pour examiner le volume par intervalle, les statistiques de conversation pour comparer les endpoints et les temps de réponse protocolaire lorsqu’ils sont pertinents. Vérifiez le pas temporel, les unités, les filtres actifs et la direction. Une moyenne peut cacher des pointes ; examinez médiane, percentiles et distribution si vos outils d’observabilité les fournissent.

### 10.1 Débit et fenêtre

Un débit inférieur aux attentes peut être lié à la congestion, à la perte, au RTT, à une fenêtre réceptrice limitée, à un contrôle de congestion, au CPU, au stockage, à un proxy ou à un plafond applicatif. Une approximation classique relie le débit soutenable à la quantité de données en vol et au RTT, mais elle ne remplace pas la mesure et ne modélise pas tous les algorithmes modernes.

Cherchez la progression des séquences, les ACK, les pertes apparentes, la fenêtre annoncée, les silences, les pauses d’application et les changements de taille de segment. Comparez un transfert de référence dans des conditions similaires. Pour une conclusion sur la congestion, complétez la capture par des compteurs d’interface, des métriques de file d’attente et les données de l’endpoint.

## 11. Automatisation et analyse reproductible avec TShark

TShark permet d’exécuter des analyses en ligne de commande, de sélectionner des champs et de créer des extractions reproductibles. Les exemples ci-dessous sont des modèles à adapter à votre version et à votre environnement.

Lister les champs d’une capture :

```bash
tshark -r incident.pcapng -T fields \
  -e frame.number -e frame.time_relative \
  -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport \
  -e tcp.flags -e tcp.seq -e tcp.ack -e tcp.len
```

Filtrer les retransmissions signalées par l’analyse TCP :

```bash
tshark -r incident.pcapng \
  -Y 'tcp.analysis.retransmission' \
  -T fields -e frame.number -e frame.time_relative \
  -e ip.src -e ip.dst -e tcp.stream -e tcp.seq -e tcp.len
```

Analyser les erreurs DNS :

```bash
tshark -r incident.pcapng \
  -Y 'dns.flags.response == 1 && dns.flags.rcode != 0' \
  -T fields -e frame.number -e frame.time_relative \
  -e ip.src -e ip.dst -e dns.qry.name -e dns.flags.rcode
```

Vérifiez le code de sortie, la version de TShark et la disponibilité des champs. Ne copiez pas une commande dans un environnement de production sans comprendre le filtre et les données qu’elle expose. Les exports CSV peuvent contenir des noms d’hôtes, des adresses, des jetons ou des métadonnées sensibles ; traitez-les comme les captures originales.

### 11.1 Éviter les erreurs d’automatisation

- N’utilisez pas une annotation `tcp.analysis.*` comme verdict sans vérification.
- Conservez le filtre exact et la version du logiciel avec le résultat.
- Distinguez un champ absent d’un champ vide et d’une valeur zéro.
- Évitez de supposer que tous les paquets ont le même ensemble de champs.
- Testez les scripts sur des captures de référence contenant des cas normaux et anormaux.
- Faites valider les conclusions critiques par une seconde méthode ou un second analyste.

## 12. Sécurité, confidentialité et limites de la preuve

Les captures peuvent contenir des identifiants, des données personnelles, des cookies, des jetons d’authentification, des noms internes et des informations métier. Réduisez le périmètre de collecte, contrôlez les accès, définissez une durée de conservation et anonymisez uniquement sur une copie. L’anonymisation peut casser les corrélations si les adresses, les ports ou les identifiants sont transformés de façon incohérente.

Un rapport sérieux doit distinguer ce qui est directement visible, ce qui est inféré et ce qui n’est pas observable. Une capture réseau peut montrer qu’une réponse est arrivée à une interface, mais pas nécessairement que l’application l’a lue. Elle peut montrer un segment sortant du point de capture sans prouver qu’il a atteint le destinataire. Elle peut montrer un RST sans identifier le processus qui l’a généré.

## 13. Études de cas guidées

### Cas A — HTTPS se connecte, puis se bloque

**Symptôme :** le handshake TCP réussit ; le ClientHello est visible ; la connexion semble progresser, puis les données volumineuses sont réémises.

**Hypothèses concurrentes :** PMTUD bloqué, perte sur le chemin, serveur qui cesse de répondre, inspection TLS, problème de fenêtre ou capture incomplète.

**Plan d’analyse :** comparer les tailles de segments, rechercher ICMP, relever MSS et éventuels tunnels, examiner les ACK et capturer de part et d’autre du point suspect. Tester avec une taille de paquet réduite dans un environnement contrôlé. Si la réduction de taille restaure le transfert et qu’un message Packet Too Big/Fragmentation Needed est bloqué à une frontière identifiée, la piste MTU devient fortement corroborée.

**Conclusion acceptable :** décrire le comportement reproduit et la frontière où les observations divergent. Ne pas déclarer « la MTU est la cause » si la seule preuve est une retransmission.

### Cas B — DNS répond, mais l’application échoue

**Symptôme :** une réponse DNS valide est présente, pourtant le client n’atteint pas le service.

**Hypothèses :** adresse retournée incorrecte pour ce réseau, réponse mise en cache, préférence IPv6, port bloqué, TLS échoué, proxy ou application qui n’utilise pas le résultat observé.

**Plan :** corréler la réponse DNS avec l’adresse de destination réellement utilisée ; vérifier TTL et résolveur ; suivre le flux TCP vers cette adresse ; comparer IPv4 et IPv6 ; examiner ensuite TLS et la réponse applicative.

**Leçon :** une résolution réussie ne prouve pas la connectivité au service ni la réussite de la transaction applicative.

### Cas C — Wireshark signale des sommes de contrôle incorrectes

**Symptôme :** de nombreux paquets sortants semblent avoir des checksums incorrects dans une capture locale.

**Hypothèses :** offload de checksum, corruption réelle, capture prise avant finalisation matérielle, troncature ou mauvais décodage.

**Plan :** identifier le point de capture et les offloads ; comparer à une capture sur TAP ou sur l’autre endpoint ; vérifier si les paquets sont reçus correctement. Ne désactivez pas les offloads en production sans évaluer le coût.

**Leçon :** une anomalie d’affichage locale ne suffit pas à prouver que les trames envoyées sur le réseau sont corrompues.

### Cas D — Le client voit un RST venant du serveur

**Symptôme :** le client reçoit un RST dont l’adresse source correspond au serveur.

**Hypothèses :** serveur qui refuse ou ferme la connexion, pare-feu injectant un reset, proxy intermédiaire, connexion devenue invalide ou paquet hors contexte.

**Plan :** comparer la capture des deux côtés, séquences et ACK, journaux du serveur et compteurs des équipements intermédiaires. Rechercher si le RST existe réellement à la sortie du serveur.

**Leçon :** l’adresse source IP visible n’identifie pas à elle seule le composant physique ou logiciel qui a généré le paquet.

## 14. Exercices de niveau expert

### Exercice 1 — Retransmission ou réordonnancement ?

Une capture contient trois segments de données, deux ACK identiques, puis une retransmission apparente. Écrivez deux hypothèses et listez les champs nécessaires pour les départager. Précisez ce que changerait une capture unidirectionnelle.

### Exercice 2 — Black hole MTU

Un transfert HTTPS s’arrête après quelques kilo-octets. Les petites requêtes réussissent. Construisez une séquence de tests permettant de distinguer MTU, perte aléatoire, fenêtre nulle et serveur lent. Indiquez les observations qui confirmeraient ou affaibliraient chaque hypothèse.

### Exercice 3 — Échec TLS

Le TCP est établi et un ClientHello est visible, mais aucune réponse lisible du serveur n’apparaît. Énumérez les explications possibles : perte, capture asymétrique, version TLS, inspection intermédiaire, réponse chiffrée ou problème de décodeur. Proposez un test indépendant pour chacune.

### Exercice 4 — Corrélation multipoint

Deux captures semblent montrer un paquet au serveur avant son émission côté client. Élaborez un plan qui traite la synchronisation des horloges, le NAT, les doublons de SPAN et l’identification des paquets. Rédigez une conclusion qui n’exagère pas ce que les temps permettent d’affirmer.

### Exercice 5 — Rapport d’incident

À partir d’une capture réelle autorisée, livrez :
- le contexte et le périmètre ;
- les points de capture et leurs limites ;
- les filtres exacts ;
- une chronologie numérotée par paquets ;
- les hypothèses considérées ;
- les éléments qui les confirment ou les réfutent ;
- la cause la mieux étayée et le niveau de confiance ;
- les actions correctives et les vérifications après correction.

## 15. Modèle de compte rendu

```text
Titre :
Incident / identifiant :
Date et fuseau :
Analyste :
Symptôme rapporté :
Impact et périmètre :
Fichiers et empreintes :
Version Wireshark / TShark :
Points de capture :
Filtres appliqués :
Qualité de capture / pertes / troncature :
Chronologie des faits :
Observations confirmées :
Hypothèses concurrentes :
Tests de corroboration :
Conclusion :
Niveau de confiance :
Limites et inconnues :
Actions recommandées :
Vérification après correction :
```

Le niveau de confiance doit refléter la qualité et l’indépendance des éléments : **faible** si la capture est partielle et plusieurs explications restent plausibles ; **modéré** si plusieurs observations cohérentes soutiennent une explication mais qu’une frontière critique n’est pas observée ; **élevé** lorsque la reproduction, les captures multipoints et une source indépendante convergent. Évitez une précision numérique artificielle si elle n’est pas fondée sur une méthode de mesure explicite.

## 16. Checklist avant de conclure

- [ ] Le point de capture et la direction sont documentés.
- [ ] Les pertes de capture et la troncature ont été évaluées.
- [ ] Les offloads et le rôle des équipements intermédiaires sont considérés.
- [ ] Les filtres sont enregistrés et reproductibles.
- [ ] Les séquences, ACK, tailles et temps ont été examinés dans leur contexte.
- [ ] Au moins deux hypothèses concurrentes ont été évaluées.
- [ ] Les événements critiques ont été corroborés par une seconde source lorsque possible.
- [ ] Les limites de visibilité et de synchronisation sont explicites.
- [ ] Les données sensibles sont protégées.
- [ ] La conclusion ne dépasse pas les preuves disponibles.

## 17. Références techniques à consulter

Pour approfondir ou vérifier un comportement dépendant d’une implémentation, consultez les documentations officielles et les RFC pertinentes :

- Documentation officielle Wireshark : guides utilisateur, filtres d’affichage, références des champs et manuels de TShark.
- RFC 9293 : spécification actuelle de TCP.
- RFC 5681 : contrôle de congestion TCP.
- RFC 1191 : Path MTU Discovery pour IPv4.
- RFC 8201 : Path MTU Discovery pour IPv6.
- RFC 8899 : Packetization Layer Path MTU Discovery.
- RFC 8446 : TLS 1.3.
- RFC 1034 et RFC 1035 : concepts et implémentation de base du DNS.

Les détails d’interface et certains champs évoluent selon les versions. Lorsque l’analyse dépend d’un comportement précis, vérifiez la documentation correspondant à la version utilisée et conservez la version dans le rapport.

---

## Synthèse opérationnelle

L’analyse experte avec Wireshark ne consiste pas à reconnaître immédiatement une couleur ou une annotation. Elle consiste à reconstruire un échange, à comprendre ce que le point de capture pouvait réellement observer, à confronter les séquences et les temps aux règles du protocole, puis à chercher une preuve indépendante. Les symptômes TCP, MTU, DNS et TLS se recouvrent souvent : une même pause peut être compatible avec une perte, un chemin asymétrique, une application lente ou une capture incomplète.

Une bonne conclusion nomme les faits, décrit le mécanisme le plus probable, indique les preuves qui le soutiennent et précise les limites restantes. C’est cette discipline qui transforme une capture en diagnostic défendable et en correction vérifiable.
