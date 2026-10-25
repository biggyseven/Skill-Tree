# Méthodologie de dépannage - Expert

**Niveau :** EXPERT

Ce cours prolonge les niveaux Débutant et Intermédiaire. Il suppose que le lecteur sait déjà établir une chronologie, tester les couches réseau, lire une capture simple et utiliser les commandes de diagnostic courantes. L’objectif n’est plus seulement de trouver une panne isolée : il s’agit de conduire une investigation reproductible dans un système distribué, avec plusieurs domaines administratifs, des flux chiffrés, des chemins redondants et une télémétrie parfois incomplète.

Au niveau Expert, un diagnostic robuste combine plusieurs sources indépendantes : mesures de l’expérience utilisateur, métriques, journaux, traces applicatives, flux réseau, captures de paquets, tables de routage, compteurs d’interfaces et historique des changements. Chaque source répond à une question différente. Une capture montre ce qui a traversé un point d’observation ; elle n’explique pas automatiquement pourquoi le système a agi ainsi. Un journal montre ce qu’un composant a enregistré ; il ne prouve pas que tous les événements ont été observés. Le rôle de l’ingénieur consiste à relier ces éléments sans confondre corrélation et causalité.

Le cours utilise des exemples Windows, Linux et Cisco IOS/IOS XE, mais les principes s’appliquent également aux environnements SD-WAN, cloud, conteneurs, équilibreurs de charge et pare-feu de nouvelle génération. Les commandes sont des exemples à adapter à la version, aux droits et aux procédures locales. Les opérations qui modifient un système sont explicitement distinguées des commandes d’observation.

> **Analogie** : Diagnostiquer un réseau complexe revient à enquêter sur une chaîne logistique. Une livraison en retard peut provenir de l’entrepôt, d’un contrôle, d’un transporteur ou du destinataire. Il faut horodater les événements, comparer les étapes et identifier le premier endroit où le comportement attendu diverge du comportement réel.


## 1. La théorie et les algorithmes

### 1.1 Du dépannage local à l’investigation systémique

Dans un réseau d’entreprise, un utilisateur peut traverser de nombreux composants avant d’atteindre une application : poste, point d’accès, commutateur, passerelle, pare-feu, tunnel VPN ou SD-WAN, lien opérateur, répartiteur de charge, proxy, serveur applicatif et base de données. Une erreur visible à l’extrémité peut être causée par n’importe lequel de ces éléments, mais aussi par leur interaction.

Un incident complexe se distingue souvent par cinq caractéristiques :

1. **Multiplicité des domaines** : aucune équipe ne possède toute la chaîne.
2. **Intermittence** : le problème dépend de la charge, du chemin ECMP, du membre d’un cluster ou d’une fenêtre temporelle.
3. **Asymétrie** : le chemin aller diffère du chemin retour, ou les paquets ne sont pas capturés au même endroit.
4. **Observabilité partielle** : chiffrement, NAT, encapsulation ou absence de journaux masquent une partie du trajet.
5. **État dynamique** : la configuration, la table de routage, les sessions, la résolution DNS et les politiques peuvent changer pendant l’investigation.

Le premier travail est donc de définir précisément le résultat attendu. « Le réseau est lent » n’est pas une description suffisamment précise. « La connexion TCP vers `app.exemple.net:443` s’établit en moins de 100 ms dans 99 % des cas, mais le 95e percentile dépasse 1,8 s depuis le VLAN 30 entre 10 h 00 et 10 h 20 » est beaucoup plus exploitable.

Une fiche d’incident utile contient au minimum :

| Élément | Question à documenter |
|---|---|
| Impact | Quels utilisateurs, sites, services et fonctions sont touchés ? |
| Début | Quand le premier symptôme confirmé a-t-il été observé ? |
| Étendue | Tous les clients, un sous-réseau, un opérateur, une famille IP ou une région ? |
| Comportement attendu | Quel SLO ou test fonctionnel devrait être respecté ? |
| Comportement réel | Quel taux d’échec, délai, perte ou code d’erreur est mesuré ? |
| Conditions | Charge, heure, version, chemin, DNS, identité, MTU, membre de cluster ? |
| Changements | Quelles modifications précèdent l’incident, y compris automatiques ? |
| Preuves | Quelles métriques, lignes de journal, captures et sorties de commandes appuient l’analyse ? |

> **Piège :** Un rapport « tout fonctionne maintenant » ne clôt pas la recherche de cause racine. Un problème intermittent peut avoir disparu sans être corrigé. Il faut conserver les mesures initiales, décrire le mécanisme probable et prouver que le correctif empêche la récidive.

### 1.2 Séparer symptôme, mécanisme, cause et déclencheur

Ces concepts ne sont pas interchangeables.

- **Symptôme** : ce que l’utilisateur ou la supervision constate, par exemple une requête qui expire.
- **Mécanisme de défaillance** : comment la panne se manifeste, par exemple une retransmission TCP suivie d’un abandon applicatif.
- **Cause racine** : condition structurelle qui rend le mécanisme possible, par exemple une MTU incohérente sur un tunnel.
- **Déclencheur** : événement qui fait apparaître le problème, par exemple une réponse HTTP volumineuse après une mise à jour.
- **Facteurs contributifs** : éléments qui aggravent l’impact, comme un délai de timeout trop court ou l’absence de surveillance IPv6.

Une cause racine doit expliquer les observations majeures, pas simplement coïncider avec elles. Le fait qu’une panne commence après un changement est une piste importante, mais ne constitue pas à lui seul une preuve. Il faut comparer l’état avant/après, déterminer si le changement touche le flux concerné et reproduire, quand c’est sûr, la différence observée.

On peut représenter l’analyse sous la forme :

```text
Déclencheur
    |
    v
Condition latente ----> Mécanisme de défaillance ----> Symptôme visible
    |                              |                          |
    +---- facteurs aggravants -----+                          v
                                                   Impact utilisateur
```

Une bonne analyse identifie également les barrières qui auraient dû empêcher ou limiter l’incident : validation avant changement, tests synthétiques, alertes, redondance, limites de débit, procédure de retour arrière ou documentation.

### 1.3 Formuler des hypothèses discriminantes

Une hypothèse utile prédit des observations vérifiables et peut être réfutée. « Le pare-feu est peut-être en cause » est vague. « Le pare-feu reçoit le SYN du client, mais ne transmet pas le SYN au serveur, alors que la route et la règle de sécurité sont valides » est testable.

Pour chaque hypothèse, écrire :

1. le mécanisme envisagé ;
2. la preuve attendue si l’hypothèse est vraie ;
3. la preuve qui la rendrait improbable ;
4. le point d’observation qui départage les scénarios ;
5. le coût et le risque du test.

| Hypothèse | Prédiction | Test discriminant |
|---|---|---|
| Perte réseau sur le trajet | Le paquet est visible en amont, absent en aval ou retransmis sans ACK | Captures synchronisées et compteurs d’interface |
| Serveur saturé | La connexion atteint l’hôte, mais le temps de traitement ou la file d’attente augmente | Mesures applicatives, CPU, files, accept queue et traces |
| DNS défaillant | La résolution varie ou pointe vers des destinations différentes | Comparaison A/AAAA, TTL, résolveurs et test direct par IP |
| Politique de sécurité incorrecte | Une règle ou une décision de politique correspond au flux bloqué | Journal de décision, identifiant de règle, tuple exact du flux |
| MTU/PMTUD | Les petits échanges réussissent, mais certains volumes se bloquent | Traces ICMP, essais de taille contrôlée et captures sur le tunnel |

> **Astuce :** Choisissez d’abord le test qui divise le mieux l’espace des causes. Une capture au bon point d’étranglement peut être plus informative que dix commandes sur un poste déjà fonctionnel.

### 1.4 Raisonnement probabiliste et discipline des preuves

Le dépannage expert ressemble à une mise à jour progressive de confiance. Une observation augmente ou diminue la plausibilité d’une hypothèse ; elle ne la transforme pas instantanément en certitude. Une méthode inspirée du raisonnement bayésien peut aider :

\[
P(H \mid E) = \frac{P(E \mid H)P(H)}{P(E)}
\]

Ici, `H` est une hypothèse et `E` une preuve. Il n’est généralement pas nécessaire de calculer des probabilités exactes : la valeur pratique est de rendre explicites les croyances initiales et la force de chaque observation. Deux preuves issues du même capteur ne sont pas nécessairement indépendantes. Par exemple, une alerte et un tableau de bord peuvent partager le même agent défectueux.

Attribuer un niveau de confiance peut aider à distinguer :

- **Confirmé** : la cause reproduit le symptôme et son traitement supprime le mécanisme de défaillance ;
- **Fortement probable** : plusieurs preuves convergent, mais une expérience de confirmation manque ;
- **Possible** : compatible avec les symptômes, sans preuve discriminante ;
- **Écarté pour le périmètre testé** : contradiction observée dans des conditions clairement définies.

Ne jamais écrire « impossible » quand le test ne couvrait qu’un seul client ou une seule fenêtre temporelle. Écrire plutôt « non reproduit depuis le VLAN 30 pendant la fenêtre 10 h 00–10 h 15 ».

### 1.5 Les signaux d’observabilité et leurs limites

Un système de production peut fournir plusieurs grandes catégories de télémétrie :

| Signal | Utile pour | Limites importantes |
|---|---|---|
| Métriques | Tendance, saturation, erreurs, latence, taux | Agrégation ; une moyenne peut cacher des pointes |
| Journaux | Événements, décisions, erreurs et contexte | Format variable, pertes, horloges désynchronisées |
| Traces distribuées | Latence par étape et propagation d’un appel | Échantillonnage, propagation d’identifiant incomplète |
| Flux réseau (NetFlow/IPFIX ou équivalent) | Conversations, volumes, ports, tendances | Souvent pas de contenu ni de chronologie paquet par paquet |
| Capture PCAP | Séquence exacte des paquets au point de capture | Point de vue local, pertes de capture, chiffrement, offload |
| État/configuration | Route, ACL, NAT, sessions, voisinage, versions | État ponctuel qui peut avoir changé après la panne |
| Tests synthétiques | Vérification régulière d’un parcours utilisateur | Un scénario synthétique n’imite pas tous les clients |

Ces signaux doivent être reliés par des attributs cohérents : heure UTC, identifiant de requête, adresse source/destination, port, protocole, VLAN/VRF, interface, identifiant de session, chemin et version. Les adresses peuvent être réécrites par NAT ; il faut donc enregistrer les traductions et les horodatages correspondants.

Il est préférable d’aligner les systèmes sur une source temporelle fiable et de surveiller l’écart d’horloge. Une différence de quelques secondes peut inverser l’ordre apparent d’événements très rapprochés. Pour les captures distribuées, noter le décalage estimé entre capteurs et l’incertitude de cette correction.

> **Danger :** Les journaux et PCAP peuvent contenir des identifiants, des adresses internes, des noms d’hôtes, des jetons d’authentification ou des données applicatives. Limitez la collecte au périmètre nécessaire, contrôlez les accès, chiffrez le stockage et définissez une durée de conservation.

### 1.6 Captures synchronisées et localisation du premier écart

Une capture isolée permet de voir ce qu’un point d’observation a reçu ou émis. Elle ne permet pas toujours de déterminer si un paquet a été perdu avant ou après ce point. Pour localiser une rupture, capturer le même flux à plusieurs endroits : client, sortie de passerelle, entrée du pare-feu, sortie du pare-feu et serveur, par exemple.

Pour chaque capture, consigner :

- l’interface exacte et le sens du trafic ;
- le filtre de capture et sa possible capacité à exclure des paquets utiles ;
- l’heure, le fuseau, la source temporelle et l’écart estimé ;
- la capacité du système de capture, le taux de perte et les éventuels drops du noyau ;
- les opérations NAT, encapsulation, déduplication ou offload susceptibles de modifier ce qui apparaît ;
- le début et la fin du scénario de test.

Le tuple de flux doit être défini avant de comparer : protocole, IP/port source, IP/port destination, et éventuellement identifiants de tunnel, VLAN ou VRF. Après un NAT, les tuples attendus sont différents : il faut relier le flux avant traduction au flux après traduction avec les tables de sessions ou les journaux NAT.

```text
Client              Routeur/pare-feu                Serveur
  | SYN, t0                 |                           |
  |------------------------>| SYN, t1                   |
  |                         |-------------------------->| (absent ?)
  |<-- retransmission ------|                           |

Si le SYN est observé à l'entrée mais pas à la sortie, enquêter sur la décision locale,
la politique, le routage, la capacité de capture et l'interface de sortie avant d'accuser l'opérateur.
```

Les captures doivent être assez proches temporellement pour que les différences d’horloge ne ressemblent pas à de la latence réseau. Si la synchronisation est insuffisante, comparer surtout la présence, la séquence et les numéros TCP plutôt que les durées absolues.

### 1.7 Lire TCP sans tirer de conclusion hâtive

TCP fournit des indices puissants, mais les étiquettes de l’analyseur sont des interprétations, pas toujours des preuves de panne. Les retransmissions peuvent résulter de pertes, de réordonnancement, d’ACK retardés ou d’une capture incomplète. Un « duplicate ACK » ne prouve pas à lui seul qu’un lien est défectueux.

Points à analyser :

- **Établissement** : SYN, SYN-ACK et ACK ; localiser quel segment manque et où il disparaît.
- **Retransmission** : vérifier si le segment initial est visible ailleurs et si un ACK correspondant a été reçu.
- **RTT** : calculer des tendances et percentiles ; éviter les conclusions fondées sur un paquet atypique.
- **Fenêtre de réception** : vérifier si le récepteur annonce une fenêtre réduite ou nulle ; distinguer saturation applicative et congestion réseau.
- **RST** : déterminer qui l’a émis, sur quel point de capture et après quel événement.
- **FIN** : examiner la fermeture normale, les délais d’application et les connexions qui restent ouvertes.
- **Réordonnancement** : comparer numéros de séquence et ACKs sur des captures complètes ; les points de capture peuvent réordonner l’apparence des paquets.
- **MSS/PMTU** : le handshake révèle MSS annoncée, mais une poignée de main réussie ne prouve pas que les paquets plus volumineux traverseront le chemin.

La capture sur un serveur peut afficher des checksums incorrects ou des segments plus grands que le MTU, car les fonctions d’offload NIC (checksum, TSO/GSO/GRO) déplacent certaines opérations. Vérifier le point de capture et l’offload avant de conclure à une corruption sur le réseau. Ne désactivez pas un offload en production sans procédure de changement et mesure de référence.

### 1.8 MTU, PMTUD, fragmentation et trous noirs

Le blocage de certains transferts peut provenir d’une différence de MTU entre un lien physique, un tunnel et un chemin distant. Les petits paquets passent, mais un transfert TLS, un téléchargement ou une réponse volumineuse stagne. Si des messages ICMP indispensables à la découverte de MTU sont filtrés, l’émetteur peut continuer d’envoyer des paquets qui ne passent pas correctement : c’est un scénario de PMTU black hole.

La preuve doit relier taille et direction : reproduire avec des tailles contrôlées, vérifier les flags de fragmentation, observer les ICMP utiles, tester à chaque côté du tunnel et comparer les pertes. Les commandes `ping` qui forcent une taille ou le bit DF sont dépendantes du système ; documenter exactement leur syntaxe et interpréter leurs limites. Une réussite ICMP ne prouve pas que le trafic TCP applicatif est autorisé ou performant.

Quand TCP est concerné, le MSS clamping peut atténuer certains problèmes, mais ne doit pas devenir une correction automatique de tout symptôme de lenteur. Il peut masquer une mauvaise conception MTU et ne traite pas tous les protocoles. Comprendre l’encapsulation réelle : Ethernet, VLAN, PPPoE, GRE, IPsec, VXLAN et autres en-têtes réduisent la charge utile possible.

### 1.9 DNS, IPv4/IPv6 et chemins qui changent

Une panne appelée « DNS » peut être une réponse erronée, une cache obsolète, un mauvais résolveur, une délégation défectueuse, un problème DNSSEC, une différence split-horizon ou un délai réseau vers le résolveur. Comparer les réponses et TTL, interroger plusieurs serveurs autorisés, tester le chemin DNS et séparer le temps de résolution du temps de connexion.

En double pile, comparer A et AAAA, la route IPv4 et la route IPv6, les politiques de pare-feu, PMTU et certificats. Les algorithmes de connexion concurrente tels que Happy Eyeballs peuvent améliorer la connexion perçue en tentant plusieurs adresses, mais ils peuvent aussi masquer une panne IPv6 persistante si seul le parcours IPv4 est finalement utilisé. Surveiller la réussite de chaque famille IP séparément.

En cas de répartiteur de charge ou de CDN, des réponses DNS différentes ne sont pas toujours une anomalie : elles peuvent découler du géo-routage ou de politiques d’équilibrage. La question devient : les destinations effectivement choisies sont-elles saines, cohérentes et accessibles depuis chaque région ?

### 1.10 Routage, ECMP et asymétrie

La route présente dans la RIB (Routing Information Base) n’est pas toujours suffisante pour expliquer le chemin effectif. Il faut examiner la FIB, les politiques de routage, les VRF, les tunnels, l’ECMP, les adjacences, le matériel et les états de session. Selon la plateforme, les commandes disponibles et le niveau d’accès au plan de transfert varient.

Pour une panne qui touche seulement certaines connexions :

1. établir le tuple du flux et le membre de cluster sélectionné ;
2. vérifier toutes les routes possibles, et pas uniquement la route affichée par défaut ;
3. comparer les chemins aller/retour ;
4. contrôler les hachages ECMP, les métriques d’interface et les drops ;
5. examiner si un pare-feu stateful voit les deux directions de la session ;
6. vérifier les changements de voisinage, de BGP/OSPF et les reconvergences récentes.

L’asymétrie n’est pas toujours mauvaise. Elle devient problématique lorsqu’un composant exige un état de session partagé ou lorsque les chemins ont des politiques différentes. Éviter de désactiver globalement ECMP, la sécurité stateful ou un protocole de routage sans preuve et sans analyse de l’impact.

### 1.11 Quantifier la performance : latence, perte, débit et queues

Une investigation de performance doit distinguer plusieurs dimensions :

- **Latence** : temps aller-retour ou temps par étape ; préciser le point de mesure.
- **Gigue** : variation temporelle, surtout importante pour voix/vidéo et systèmes temps réel.
- **Perte** : proportion de paquets absents, en différenciant perte réseau, filtre, discard local et perte de capture.
- **Débit** : volume utile livré par unité de temps, pas seulement débit de ligne.
- **Taux d’erreur applicatif** : erreurs fonctionnelles par requête et par opération.
- **Saturation** : CPU, files, sessions, table d’état, mémoire, débit crypto, liens et capacités d’interface.

Toujours examiner les percentiles (p50, p95, p99) avec le volume d’échantillons. Une moyenne peut masquer des pointes sévères. De même, une alerte basée sur l’utilisation moyenne d’un lien peut manquer une micro-congestion sur une file ou une direction.

Le produit bande passante-délai (BDP) est une estimation de la quantité de données qui peut être en transit :

\[
BDP = \text{débit (bits/s)} \times RTT\text{ (s)}
\]

Sur un chemin de 200 Mbit/s avec un RTT de 80 ms, le BDP est de 16 Mbit, soit environ 2 Mo. Si la fenêtre TCP effective ou les buffers disponibles empêchent suffisamment de données d’être en transit, le débit peut être inférieur au potentiel du lien. Le calcul n’autorise pas à augmenter les buffers sans mesure : des files trop longues augmentent la latence sous charge (bufferbloat).

| Mesure | Indice possible | Confirmation à chercher |
|---|---|---|
| Pertes et retransmissions augmentent avec la charge | Congestion, microbursts ou queue saturée | Compteurs d’interface/queue, tests de charge contrôlés |
| RTT monte sans perte visible | Files profondes ou serveur plus lent | Latence par saut, RTT TCP, temps applicatif |
| Débit bas avec RTT stable | Fenêtre, CPU, policer, capacité serveur ou débit limité | Stats TCP, CPU, QoS, test contrôlé et comparaison de flux |
| Un seul flux est lent, plusieurs flux agrégés sont rapides | Limite par flux, hachage, fenêtre TCP ou CPU monocœur | Plusieurs flux parallèles, stats par queue et par CPU |
| Petites requêtes OK, grosses requêtes bloquées | MTU/PMTUD, inspection ou limite applicative | Tailles contrôlées, ICMP, captures et logs du chemin |

### 1.12 Hôte, NIC et datapath

Un réseau peut être sain du point de vue des interfaces tout en étant limité par l’hôte : CPU, interruptions, files RX/TX, buffers, conntrack, sockets, épuisement de ports éphémères, backlog d’écoute, limite de descripteurs ou contention de mémoire. Dans Linux, RSS répartit les flux reçus entre files matérielles ; RPS/RFS et XPS peuvent modifier la distribution de traitement. Ces paramètres dépendent du pilote, de la carte, du noyau et de la charge. Il faut les mesurer avant de les ajuster.

Un hôte peut voir des drops de paquets avant même que la pile IP n’enregistre une erreur classique. Sur Linux, examiner par exemple `ip -s link`, `ethtool -S`, `nstat`, `ss -s`, `ss -tin`, `mpstat`, `sar`, `top` ou les compteurs applicatifs. Certaines commandes exigent des privilèges et certains champs dépendent de la distribution et du pilote.

Pour un serveur, distinguer le temps passé dans la file d’attente, le temps CPU, le temps de traitement de la requête et les appels dépendants (base, cache, API tierce). Une simple mesure de ping ne révèle pas la latence de l’application. Pour les services derrière un répartiteur, comparer les métriques par membre et vérifier les health checks, la persistance, les connexions longues et l’éventuelle surcharge d’un seul nœud.

### 1.13 Changements, baselines et expérimentation sûre

Un changement peut être manuel, automatisé, piloté par contrôleur, issu d’un déploiement applicatif ou déclenché par une convergence dynamique. Maintenir une chronologie des changements qui associe heure, responsable/service, différence de configuration, validation, test et retour arrière. Conserver les états avant/après : versions, route, règles, politiques QoS, MTU, certificats, configuration de charge et santé des nœuds.

La meilleure expérience est souvent un test A/B maîtrisé : un client affecté et un client témoin, une route ou un membre différent, un flux autorisé et un flux refusé, ou une fenêtre avant/après. Ne changer qu’une variable à la fois lorsque c’est possible. Si plusieurs modifications sont imposées par une urgence, documenter lesquelles ont été réalisées et quelle preuve permet d’attribuer le résultat à chacune.

> **Danger :** N’effectuez pas de « test correctif » en production qui efface l’état utile, redémarre un cluster, désactive une ACL, coupe un tunnel ou vide les compteurs sans préparation. Un test peut interrompre le service, détruire une preuve ou faire disparaître un symptôme intermittent.

### 1.14 Algorithme expert de localisation du premier écart

```text
ENTRÉES : symptôme reproductible ou fenêtre d'incident, chemin supposé, service attendu

1. Définir le résultat attendu et l'impact utilisateur.
2. Fixer une fenêtre temporelle et enregistrer les horloges.
3. Obtenir un flux de référence : tuple, requête, réponse et identifiant de corrélation.
4. Collecter métriques, journaux, état et captures disponibles sans changer le système.
5. Construire une séquence attendue des événements, de la source à la destination.
6. Aligner les observations et marquer le premier point où l'événement attendu manque ou diverge.
7. Formuler deux ou trois hypothèses qui expliquent ce premier écart.
8. Choisir un test sûr qui distingue les hypothèses.
9. Répéter dans les mêmes conditions et comparer avec un témoin sain.
10. Corriger le mécanisme prouvé, sous changement contrôlé.
11. Valider les parcours utilisateur, les métriques et l'absence de régression.
12. Documenter cause, preuves, limites et prévention.

SORTIE : cause étayée, correction réversible, test de validation et actions préventives
```

> **Piège :** Ne commencez pas par le composant le plus complexe ou le plus visible. Commencez par le premier point où deux observations indépendantes cessent de correspondre au comportement attendu.


## 2. Configuration et pratique

Les exemples ci-dessous montrent une méthode d’investigation. Les noms d’interfaces, les options de capture, les commandes de debug et les formats de sortie diffèrent selon les versions. Adapter chaque exemple au système cible et à sa politique de changement.

### 2.1 Scénario de laboratoire : application intermittente

Topologie de référence :

```text
Poste VLAN 30
10.30.0.25
    |
    v
SW-ACCESS ----- GW-CAMPUS (SVI 10.30.0.1)
                       |
                       v
                  FW-PERIMETRE
                  NAT / politiques
                       |
                       v
                  WAN / SD-WAN
                       |
                       v
                LB-APP (VIP 172.20.10.50:443)
                       |
               +-------+-------+
               v               v
           APP-01            APP-02
        172.20.20.11      172.20.20.12
```

Symptôme : 2 % des requêtes HTTPS dépassent trois secondes. Le ping de la VIP réussit. Une capture ponctuelle ne montre pas d’échec évident.

La bonne investigation ne conclut pas « le réseau est bon » parce que le ping réussit. Le ping peut suivre une politique différente, cibler une adresse différente du membre final et ne pas reproduire la taille, le protocole ou la charge d’une requête réelle. Il faut définir un identifiant de requête, mesurer le temps DNS, TCP, TLS et application séparément, obtenir le membre de pool sélectionné, puis corréler la même requête dans les journaux et captures disponibles.

Plan de collecte :

1. Exécuter un test HTTPS horodaté depuis un client sain et un client affecté.
2. Collecter temps DNS, temps de connexion, handshake TLS, premier octet et durée totale.
3. Corréler le résultat avec le membre APP-01 ou APP-02, le chemin WAN et le lien.
4. Consulter les changements et les health checks du répartiteur.
5. Capturer le même tuple à l’entrée et à la sortie du pare-feu, puis sur le membre concerné si autorisé.
6. Comparer les p95/p99 par membre et par zone avant de modifier quoi que ce soit.
7. Formuler des hypothèses, tester une variable à la fois et documenter ce qui les réfute.

### 2.2 Outils Windows pour une collecte reproductible

Commandes d’observation courantes :

```powershell
# Adresse, passerelle, DNS, DHCP et état d'interface
ipconfig /all

# Table de routage et cache ARP/voisins IPv4
route print
arp -a

# Résolution explicite auprès d'un résolveur choisi
Resolve-DnsName app.exemple.net -Server 10.30.0.10 -Type A
Resolve-DnsName app.exemple.net -Server 10.30.0.10 -Type AAAA

# Tester une connexion TCP vers le port de service
Test-NetConnection app.exemple.net -Port 443 -InformationLevel Detailed

# Itinéraire ; le résultat dépend du protocole et du filtrage ICMP
tracert -d app.exemple.net

# Vérifier la configuration IPv6
Get-NetIPConfiguration
Get-NetRoute -AddressFamily IPv6
```

Pour une mesure HTTPS, un outil comme `curl` peut séparer certaines phases. La syntaxe dépend de la version installée ; vérifier `curl --help` et enregistrer le résultat avec l’horodatage.

```powershell
curl.exe -sS -o NUL -w "dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} first_byte=%{time_starttransfer} total=%{time_total}`n" https://app.exemple.net/
```

Cette commande produit une mesure côté client. Elle ne désigne pas automatiquement le réseau comme cause d’un délai élevé : `time_starttransfer` comprend notamment les délais du serveur et des dépendances applicatives. Comparer plusieurs répétitions, et préserver le code de sortie, les erreurs TLS et la réponse HTTP.

Pour la capture sur Windows, utiliser l’outil approuvé localement (par exemple Wireshark/Npcap ou `pktmon` selon la version et les règles de sécurité). Avant de lancer une capture, définir le filtre, la durée, le volume maximum et le chemin de stockage. Si l’on collecte plusieurs interfaces, identifier chaque interface ; une capture sur une interface virtuelle peut représenter des paquets différents de ceux qui atteignent la carte physique.

### 2.3 Outils Linux et analyse côté hôte

Collecter les faits de base avant d’installer un nouvel agent ou de redémarrer un service :

```bash
# Interface, routes et voisins
ip -s link
ip address show
ip route show table all
ip -6 route show table all
ip neigh show

# Statistiques réseau et sockets
nstat -az
ss -s
ss -tin
ss -lntp

# Statistiques CPU et système (si installés)
vmstat 1 10
mpstat -P ALL 1 10
sar -n DEV,EDEV,TCP,ETCP 1 10

# Processus et état des services
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head
systemctl status nom-service
journalctl -u nom-service --since '10 minutes ago'
```

Ne copiez pas aveuglément les sorties contenant des identifiants ou des paramètres secrets. `ss -lntp` et d’autres outils peuvent révéler des ports et des processus internes ; les journaux applicatifs peuvent contenir des données personnelles. Conserver la sortie horodatée, les unités, la durée de l’échantillonnage et la charge pendant le test.

Exemples de capture courte :

```bash
# Capture limitée au flux de laboratoire ; ajuster l'interface et les adresses
sudo tcpdump -ni eth0 -s 0 -c 500 -w /var/tmp/incident-app.pcap \
  'host 172.20.20.11 and tcp port 443'

# Vue lisible d'un flux précis ; ne remplace pas l'original PCAP
sudo tcpdump -nn -tttt -r /var/tmp/incident-app.pcap
```

En production, appliquer des limites de taille et de temps, un emplacement de stockage autorisé et des permissions strictes. Pour une capture prolongée, utiliser une stratégie de fichiers circulaires/ring buffer lorsqu’elle est prise en charge et s’assurer que la capture elle-même ne surcharge pas l’hôte.

### 2.4 Cisco IOS/IOS XE : vérifications avant tout debug

Collecter d’abord l’état non intrusif et horodaté :

```text
show clock detail
show version
show logging
show interfaces status
show interfaces counters errors
show interfaces <interface>
show ip interface brief
show ip route <adresse-destination>
show ip cef <adresse-destination> detail
show arp
show ip nat translations
show ip nat statistics
show access-lists
show ip access-lists
show processes cpu sorted
```

Toutes les commandes ne sont pas présentes sur tous les équipements ou versions. Certaines sorties peuvent être coûteuses, volumineuses ou révéler des informations sensibles. La syntaxe exacte pour la FIB/CEF, les ACL, le NAT et la capture doit être confirmée sur la plateforme en question. En IPv6, utiliser les commandes équivalentes de la famille IPv6 et examiner les voisins ND.

Évaluer les compteurs avant et après un test connu : CRC, input errors, output drops, overruns, queue drops, changements de duplex/vitesse et transitions d’état. Un compteur cumulatif ne permet pas de dater l’erreur ; l’écart entre deux observations prises avec le même intervalle est souvent plus informatif.

`debug` peut affecter les performances, remplir la console ou exposer des détails sensibles. En production, l’utiliser uniquement avec le filtre le plus restrictif possible, une durée très courte et l’accord prévu dans la procédure. Préférer les journaux ciblés, les compteurs et les fonctions de capture intégrées lorsque celles-ci répondent à la question. Toujours définir la méthode de désactivation et le retour à l’état normal avant d’activer un debug.

### 2.5 Filtres Wireshark ciblés

Les filtres d’affichage aident à analyser un PCAP déjà collecté. Ils sont distincts des filtres de capture : le premier masque des paquets à l’écran ; le second peut empêcher leur enregistrement.

```text
# Flux TCP entre un client et un serveur
ip.addr == 10.30.0.25 && ip.addr == 172.20.10.50 && tcp.port == 443

# Handshake TCP
 tcp.flags.syn == 1

# Retransmissions signalées par l'analyseur TCP
 tcp.analysis.retransmission || tcp.analysis.fast_retransmission

# ACK dupliqués ; à interpréter dans le contexte du flux
 tcp.analysis.duplicate_ack

# Réinitialisations TCP
 tcp.flags.reset == 1

# DNS classique
 dns

# ICMP IPv4 et ICMPv6
 icmp || icmpv6

# Client IPv6 uniquement
 ipv6.addr == 2001:db8:30::25
```

Les champs et noms de filtres peuvent évoluer avec les versions ; consulter la référence Wireshark. Les annotations d’analyse TCP sont des heuristiques utiles, mais doivent être recoupées avec numéros de séquence, ACKs, points de capture et pertes possibles du capteur.

Pour chaque problème, commencer par isoler un seul flux, puis élargir aux autres conversations. L’analyse « Follow TCP Stream » peut faciliter la compréhension d’un protocole en clair, mais les charges TLS resteront chiffrées sans clés de session valides et autorisées. Ne pas chercher à contourner le chiffrement : utiliser les logs et traces de l’application, les journaux TLS, ou une instrumentation légitime.

### 2.6 Bâtir une chronologie multi-source

Créer une table unique qui rassemble les observations, en notant la source de chaque donnée :

| Temps UTC | Source | Événement | Identifiant | Confiance |
|---|---|---|---|---|
| 09:41:10.120 | Client | Résolution DNS terminée | req-7f2a | Élevée |
| 09:41:10.145 | Client | SYN envoyé | tuple A | Élevée |
| 09:41:10.147 | FW entrée | SYN observé | tuple A | Élevée |
| 09:41:10.148 | FW sortie | SYN absent dans capture | tuple traduit attendu | Moyenne |
| 09:41:10.151 | Journal FW | Décision de politique enregistrée | session 84219 | Élevée |
| 09:41:13.200 | Client | Timeout applicatif | req-7f2a | Élevée |

Dans cet exemple, l’absence du SYN en sortie n’est pas encore une preuve certaine : l’interface de sortie ou le filtre de capture peut être incorrect, la session peut ne pas être corrélée, ou le décalage temporel peut être significatif. La ligne de journal associée aide à départager ces possibilités. Chaque conclusion doit dire quel élément est directement observé et quel élément est inféré.

### 2.7 Automatiser la collecte sans créer une nouvelle panne

L’automatisation est utile pour collecter le même ensemble d’éléments sur plusieurs sites et réduire les erreurs humaines. Elle doit respecter les principes suivants :

- **Lecture seule par défaut** : les premiers scripts collectent l’état, sans modifier la configuration.
- **Périmètre explicite** : liste d’hôtes autorisés, durée limite, nombre maximal de processus et taille maximale des fichiers.
- **Gestion sûre des secrets** : ne pas placer de mots de passe dans les arguments de commande, les journaux ou le code source.
- **Sorties normalisées** : horodatage UTC, identifiant d’hôte, version d’outil, unité des mesures et statut d’erreur.
- **Échec visible** : signaler les données manquantes ; ne pas les remplacer par zéro, ce qui pourrait faire croire à une absence de problème.
- **Idempotence et permissions minimales** : éviter toute action destructive et limiter les droits de l’agent.
- **Contrôle de charge** : éviter de déclencher simultanément de lourdes captures sur tous les équipements.

Pseudocode d’un collecteur sûr :

```text
pour chaque cible approuvée :
    vérifier que la cible est dans le périmètre
    ouvrir un dossier d'incident avec permissions restrictives
    enregistrer l'heure UTC, le nom de la cible et sa version
    exécuter seulement les commandes d'observation prévalidées
    imposer un timeout à chaque commande
    enregistrer stdout, stderr, code de retour et durée
    calculer le hash des fichiers exportés
    si la collecte échoue, consigner l'erreur sans inventer de valeur
    vérifier la taille totale et la politique de rétention
```

Les changements automatiques devraient utiliser un flux séparé : approbation, sauvegarde d’état, validation syntaxique, test limité, plan de retour arrière, exécution et vérification post-changement.

### 2.8 Laboratoire 1 — Le handshake est établi, mais HTTPS est lent

**Situation.** Les SYN/SYN-ACK/ACK arrivent rapidement. Pourtant, le temps avant le premier octet est parfois supérieur à deux secondes.

**Démarche :**

1. Mesurer séparément DNS, connexion TCP, handshake TLS, premier octet et durée totale depuis le même client.
2. Confirmer que les requêtes lentes et rapides utilisent le même nom, la même famille IP, le même VIP et le même membre de pool — ou relever leurs différences.
3. Vérifier si le délai apparaît avant ou après l’établissement TLS.
4. Corréler `request-id`, code HTTP, membre du pool et durée des dépendances côté serveur.
5. Contrôler les files d’attente, CPU, sessions et délais du proxy/lb, sans supposer que la connectivité TCP garantit la santé applicative.
6. Comparer un appel lent et un appel rapide dans la même fenêtre.

**Interprétation.** Si TCP et TLS sont rapides mais le premier octet lent, privilégier l’investigation applicative, les files serveur et les dépendances aval. Si le handshake TLS est lent, analyser les certificats, le CPU cryptographique, les échanges intermédiaires et le trajet réseau. Si les temps changent selon le membre du pool, comparer directement les membres et leur configuration.

### 2.9 Laboratoire 2 — Seuls les gros transferts échouent

**Situation.** Un accès SSH et une petite page Web fonctionnent, mais le téléchargement d’un fichier volumineux stagne après quelques kilo-octets.

**Démarche :**

1. Reproduire avec un fichier de test non sensible et consigner la taille qui échoue.
2. Comparer un test de petite charge utile à un test de grande charge utile.
3. Capturer le flux de part et d’autre d’un tunnel, si autorisé.
4. Examiner MSS négociée, retransmissions, tailles de segments et messages ICMP pertinents.
5. Mesurer la MTU du chemin à l’aide d’une méthode adaptée au système et au type d’encapsulation.
6. Vérifier si le pare-feu, le tunnel ou l’opérateur applique une politique particulière aux fragments ou aux messages ICMP.
7. Tester la correction dans un environnement contrôlé, puis valider IPv4, IPv6, les flux de retour et d’autres applications.

**Interprétation.** Un seuil de taille reproductible et une absence de retour ICMP nécessaire peuvent appuyer l’hypothèse PMTU. Une corrélation avec un seul membre de pool peut plutôt indiquer une MTU incohérente sur ce membre ou son chemin. Ne changez pas globalement le MTU avant d’avoir localisé le segment concerné.

### 2.10 Laboratoire 3 — Dégradation intermittente liée à ECMP

**Situation.** Certaines connexions réussissent, d’autres expirent. L’interface n’affiche pas une saturation moyenne.

**Démarche :**

1. Enregistrer les tuples des flux qui réussissent et de ceux qui échouent.
2. Chercher un regroupement par sous-réseau source, port source, destination, famille IP ou membre de cluster.
3. Examiner les chemins ECMP, compteurs d’interface et état de chaque lien.
4. Comparer le chemin aller et le chemin retour pour les flux concernés.
5. Capturer les segments sur plusieurs sorties possibles et vérifier si la perte se produit sur un seul chemin.
6. Contrôler la chronologie de BGP/OSPF, des adjacences, de la maintenance et de la convergence.
7. Privilégier une correction ciblée et réversible ; éviter de désactiver ECMP sans preuve.

**Interprétation.** Si les échecs se regroupent sur un prochain saut, vérifier ce chemin, l’ACL, le MTU, les erreurs physiques et les files. Si tous les flux d’un hôte sont affectés quel que soit le chemin, revenir aux couches hôte, identité, DNS ou application.

### 2.11 Laboratoire 4 — Le tableau de bord est vert, mais les utilisateurs sont impactés

Un indicateur de disponibilité peut ne tester qu’un port TCP ou un endpoint simple. Il peut réussir tandis que l’authentification, la recherche en base, un chemin IPv6 ou une région précise est défaillant.

Construire des tests synthétiques qui couvrent le parcours utilisateur réel sans modifier les données de production. Mesurer par zone et par famille IP ; vérifier les identifiants de test, les dépendances et les résultats fonctionnels, pas seulement le code HTTP. Surveiller les erreurs et latences par dimensions utiles sans créer une cardinalité ingérable dans le système de métriques.

Un SLO peut, par exemple, être défini autour d’un taux de requêtes correctes et d’une latence sous un seuil. Le seuil et la fenêtre sont des choix de service, non des valeurs universelles. Une alerte doit correspondre à un impact ou à une consommation de budget d’erreur significative, plutôt qu’à chaque variation minime d’une métrique interne.


## 3. Dépannage et sécurité

### 3.1 Triage et priorisation de l’incident

Avant de chercher une cause, classer l’impact : nombre d’utilisateurs, fonctions métier, zones, criticité, durée, risques de sécurité et existence d’un contournement. Définir un responsable d’incident, un canal de communication et un rythme de mise à jour. Séparer le travail d’investigation de la communication : les hypothèses ne doivent pas être présentées comme des faits établis.

Un incident de disponibilité peut aussi cacher un incident de sécurité. Des changements d’ACL inattendus, une hausse inhabituelle des connexions, une anomalie DNS, un nouvel équipement ou des échecs d’authentification massifs doivent être traités selon le processus de réponse aux incidents de l’organisation. Dans ce cas, préserver les éléments nécessaires à l’analyse forensique avant une remise en état qui les détruirait, lorsque la sécurité immédiate permet de le faire.

### 3.2 Préserver l’intégrité des preuves

Pour chaque pièce collectée, consigner l’origine, l’heure UTC, la méthode, l’opérateur ou l’automate, le système source, le périmètre, les transformations appliquées et la somme de contrôle du fichier. Conserver l’original en lecture seule lorsque la procédure l’exige ; faire l’analyse sur une copie de travail. Le hash prouve que le fichier n’a pas changé depuis son calcul, mais ne prouve pas à lui seul que la capture initiale était complète ou exacte.

Ne pas supprimer les paquets « inutiles » de l’original. Une capture filtrée est une dérivée ; garder le filtre, l’outil, sa version et les paramètres. Si l’horloge est incorrecte, ne jamais remplacer silencieusement les horodatages : enregistrer les temps d’origine et la correction estimée dans les notes.

> **Danger :** Une capture contenant un flux applicatif non chiffré peut contenir des secrets réutilisables. Le partage d’un PCAP par messagerie non sécurisée ou dans un ticket accessible largement est un incident de confidentialité potentiel.

### 3.3 Sécurité pendant l’investigation

L’ingénieur de dépannage doit parfois accéder à des systèmes privilégiés ; cela ne justifie pas de contourner les contrôles. Utiliser des comptes nominatifs, MFA, accès temporaires et droits minimums. Les scripts ne doivent pas enregistrer de mots de passe ou de jetons en clair. Masquer les informations sensibles avant de partager les sorties avec des personnes qui n’ont pas besoin d’y accéder.

Précautions essentielles :

- limiter les captures à l’hôte, au service et à la fenêtre pertinents ;
- ne pas activer une inspection TLS ou un déchiffrement sans autorisation, cadre juridique et configuration approuvée ;
- ne pas exporter des configurations complètes contenant des secrets vers un ticket public ;
- contrôler qui peut lire les logs d’authentification, les PCAP et les données de flux ;
- traiter les scripts de collecte comme des outils de production : revue, tests, journalisation et contrôle d’accès ;
- respecter les politiques internes de conservation et d’effacement.

### 3.4 Quand lancer un debug ou une capture en production

Une capture très large peut perdre des paquets, remplir un disque, augmenter la charge CPU ou exposer un contenu sensible. Un debug sur routeur peut provoquer des pics CPU ou saturer la console. Avant toute action intrusive, répondre par écrit à ces questions :

1. Quelle hypothèse cette action testera-t-elle ?
2. Quelle observation précise permettra de conclure ?
3. Quelle est la durée maximale ?
4. Quel est le risque d’impact et comment sera-t-il détecté ?
5. Qui autorise l’action et qui peut l’interrompre ?
6. Où seront stockées les preuves et qui y aura accès ?
7. Comment restaurer l’état normal et vérifier que l’outil est arrêté ?

Si ces questions ne peuvent pas recevoir de réponse claire, commencer par une méthode moins intrusive : compteurs, journal de décision, échantillonnage de flux, capture sur un équipement dédié ou reproduction dans un environnement de test.

### 3.5 Réduire les faux positifs et les angles morts

Chaque système d’observabilité a un biais. Un agent qui ne voit pas les paquets abandonnés au niveau NIC peut déclarer le réseau sain. Une capture SPAN peut perdre des paquets lorsque le port source dépasse la capacité du port miroir. Une trace distribuée peut ne pas suivre l’appel aval si le contexte n’est pas propagé. Un flux NetFlow échantillonné peut sous-estimer un court pic. Un test synthétique depuis le siège peut manquer une panne de sortie Internet régionale.

Documenter ces limitations dans le rapport : couverture de capture, taux d’échantillonnage, interfaces observées, visibilité après NAT, statut de chiffrement, disponibilité des logs et écarts d’horloge. Quand l’absence d’un événement est centrale à la conclusion, il faut prouver que le capteur aurait été capable de l’observer.

> **Piège :** « Je ne le vois pas dans la capture » n’équivaut pas à « le paquet n’a pas existé ». Cela peut signifier que le point de capture était incorrect, que le filtre l’a exclu, que l’interface miroir a perdu le paquet ou que le protocole masque le détail recherché.

### 3.6 Séparer les erreurs de mesure des erreurs réseau

Un test peut être faussé par DNS local, cache navigateur, proxy, pool de connexions, offload NIC, résolveur intermédiaire ou limitations de l’outil. Avant de comparer des mesures, normaliser : même protocole, même famille IP, même point de départ, mêmes destinations, mêmes tailles de charge utile, mêmes conditions de cache et même durée. Décrire les différences lorsqu’une normalisation est impossible.

Ne pas comparer directement une mesure ICMP à la latence d’une requête HTTPS : les politiques QoS, les chemins et la charge sont différents. Ne pas utiliser un test de débit mono-flux pour conclure sur l’agrégat multi-flux, ni un test local au datacenter pour conclure sur une connexion distante. Un résultat nul peut signifier « outil non disponible », « privilège refusé » ou « aucune donnée » ; conserver le code de retour et stderr.

### 3.7 Contrôle des changements et retour arrière

Une correction doit être étroite, traçable et réversible. Avant l’application :

- capturer l’état et la configuration actuels ;
- définir le périmètre attendu et les systèmes qui peuvent être affectés ;
- créer un plan de test avec mesures initiales ;
- obtenir l’approbation requise et vérifier la sauvegarde ;
- définir un seuil de retour arrière et la personne autorisée à l’exécuter.

Après l’application :

- vérifier le statut de la configuration et des sessions ;
- tester le parcours fonctionnel complet depuis un client affecté et un client témoin ;
- vérifier les métriques, journaux, erreurs et p95/p99 ;
- vérifier les chemins IPv4/IPv6 et les flux de retour pertinents ;
- surveiller assez longtemps pour couvrir le rythme de récurrence du problème ;
- consigner les changements exacts et le résultat.

Une baisse immédiate du taux d’erreur après un changement est encourageante, mais la validation doit tenir compte de la variabilité naturelle, de la saisonnalité de charge et de la possibilité que plusieurs causes coexistent.

### 3.8 Conduire un post-mortem sans blâme

Un post-mortem utile explique les conditions qui ont permis à l’incident de se produire et de durer. Il ne doit pas s’arrêter à une erreur humaine ou à un composant défaillant. Des questions plus utiles sont : pourquoi le changement était-il possible sans test détectant le problème ? Pourquoi le monitoring n’a-t-il pas détecté l’impact ? Quelle procédure a rendu le retour arrière difficile ? Quelle information manquait à l’équipe de garde ?

Structure suggérée :

1. **Résumé** : impact, durée, services et utilisateurs touchés.
2. **Chronologie** : heures, événements, décisions et niveau de confiance.
3. **Détection** : quelle alerte ou quel signal a révélé l’incident ?
4. **Cause et mécanisme** : preuve étayée, alternatives écartées et limites.
5. **Facteurs contributifs** : architecture, changement, tests, supervision, processus.
6. **Résolution** : action corrective et validation mesurée.
7. **Prévention** : tâches avec responsable, priorité et date cible.
8. **Leçons** : améliorations de détection, de réponse et de résilience.

Éviter une longue liste d’actions vagues. Chaque action doit avoir un propriétaire, une échéance, un critère de réussite mesurable et un lien avec un facteur précis de l’incident.

### 3.9 Construire des playbooks et des runbooks

Un **runbook** décrit une procédure reproductible, par exemple comment collecter l’état d’une interface ou vérifier une route. Un **playbook** décrit une stratégie guidée pour un type d’incident, avec des décisions conditionnelles et des actions d’escalade. Les deux doivent être versionnés et testés dans des exercices.

Un playbook expert inclut :

- les symptômes déclencheurs et la portée du scénario ;
- les données minimales à collecter et les accès nécessaires ;
- les commandes exactes par plateforme et leurs limites ;
- les résultats attendus et les embranchements de décision ;
- les conditions d’arrêt et d’escalade ;
- les opérations interdites sans autorisation ;
- la procédure de retour arrière ;
- les critères de clôture et les éléments à joindre au rapport.

Les runbooks doivent rester courts pour la première intervention, tout en reliant vers les procédures détaillées. Mettre à jour le document après chaque exercice ou incident qui révèle une ambiguïté. Un playbook que personne n’a testé n’est pas une preuve de préparation.

### 3.10 Indicateurs opérationnels qui améliorent le dépannage

Les indicateurs utiles évaluent la qualité de la réponse, pas seulement le nombre de tickets fermés. Exemples :

| Indicateur | Utilité | Précaution |
|---|---|---|
| MTTD (temps moyen de détection) | Évalue la rapidité de détection | Préciser le début de la fenêtre et le mode de calcul |
| MTTA (temps moyen d’accusé de prise en charge) | Évalue la réponse initiale | Ne confondre avec la résolution réelle |
| MTTR (défini explicitement) | Suit le temps de restauration/résolution | Le terme peut signifier réparation, réponse ou récupération ; fixer une définition |
| Taux de récurrence | Détecte les correctifs qui ne traitent pas la cause | Relier les incidents par cause, pas uniquement par catégorie |
| Part d’incidents avec chronologie complète | Évalue la qualité d’investigation | Ne pas encourager la collecte excessive de données personnelles |
| Couverture des parcours synthétiques | Révèle les angles morts du monitoring | Mesurer la représentativité des parcours et des régions |
| Durée jusqu’à une première hypothèse testable | Suit la capacité de cadrage | Ne pas encourager une hypothèse hâtive qui remplace les preuves |

L’objectif est d’améliorer le système et la méthode, pas de classer les personnes. Les indicateurs de temps doivent tenir compte de la gravité, de la complexité et des dépendances externes.

### 3.11 Réponse aux incidents de cybersécurité

Si les indices pointent vers une compromission, un déni de service, une exfiltration ou une altération de configuration, activer le processus de réponse aux incidents approprié. La priorité est de limiter le risque, préserver les preuves utiles et coordonner les équipes autorisées. Les actions de confinement doivent être évaluées selon l’impact métier : isoler un segment peut protéger les données mais interrompre un service critique.

Suivre les procédures internes et les recommandations actuelles de gestion d’incident ; le NIST SP 800-61 Rev. 3 (finalisé en avril 2025) intègre la réponse aux incidents dans la gestion du risque et dans le Cybersecurity Framework 2.0. Cette approche ne remplace pas les obligations réglementaires, contractuelles ou locales de notification.

### 3.12 Checklist de clôture d’un incident expert

Avant de déclarer l’incident résolu, vérifier :

- [ ] L’impact et la fenêtre de l’incident sont documentés.
- [ ] Les symptômes ont été reproduits ou les limites de reproduction sont explicites.
- [ ] Les preuves originales sont conservées selon la politique prévue.
- [ ] Les sources ont des horodatages et des limites de mesure documentés.
- [ ] La cause proposée explique les principales observations et les alternatives testées.
- [ ] Le correctif est approuvé, ciblé et assorti d’un retour arrière.
- [ ] Le parcours complet fonctionne pour un client affecté et un témoin.
- [ ] Les métriques techniques et fonctionnelles sont revenues à leur niveau attendu.
- [ ] Les chemins, familles IP, sites ou membres concernés ont été vérifiés.
- [ ] Les changements de production sont consignés.
- [ ] Les actions préventives ont un responsable, une échéance et un critère de réussite.
- [ ] Le runbook, les alertes et la documentation ont été corrigés si nécessaire.


## Points à retenir

- L’investigation experte vise le premier écart entre le comportement attendu et le comportement observé, pas le composant le plus suspect au départ.
- Un symptôme, un mécanisme, une cause racine et un déclencheur sont des notions différentes. Une cause doit expliquer les preuves et permettre un test de confirmation.
- Les métriques, journaux, traces, flux et captures se complètent ; aucune source ne décrit seule toute la chaîne.
- Une capture doit être documentée : point, interface, direction, filtre, capacité, horloge et pertes éventuelles.
- L’absence de paquet dans un PCAP n’est concluante que si la capacité d’observation du capteur est connue.
- Les annotations TCP sont des indices. Examiner les numéros de séquence, ACK, retransmissions, fenêtres, RST, chemin retour et limites du point de capture.
- Les p95/p99, les erreurs applicatives et la latence par étape sont souvent plus utiles que les moyennes et le ping seul.
- Une panne partielle peut venir d’ECMP, d’un membre de pool, d’IPv6, de NAT, de PMTU, d’une file ou d’un hôte ; comparer les flux qui réussissent à ceux qui échouent.
- Les outils de collecte peuvent eux-mêmes perturber la production ou exposer des données sensibles. Toute action intrusive doit avoir une hypothèse, une limite et un plan d’arrêt.
- Un correctif n’est validé que lorsque le parcours complet est testé, les métriques sont stables et le risque de régression est contrôlé.
- Le post-mortem doit transformer les preuves en améliorations mesurables de l’architecture, de l’observabilité et des procédures.


## Références techniques

1. **NIST SP 800-61 Rev. 3** — *Incident Response Recommendations and Considerations for Cybersecurity Risk Management: A CSF 2.0 Community Profile*, avril 2025 : https://csrc.nist.gov/pubs/sp/800/61/r3/final
2. **IETF RFC 9293** — *Transmission Control Protocol (TCP)* : https://www.rfc-editor.org/rfc/rfc9293.html
3. **IETF RFC 8305** — *Happy Eyeballs Version 2: Better Connectivity Using Concurrency* : https://www.rfc-editor.org/rfc/rfc8305.html
4. **IETF RFC 4821** — *Packetization Layer Path MTU Discovery* : https://www.rfc-editor.org/rfc/rfc4821.html
5. **Wireshark Wiki** — Display Filters et distinction entre filtre d’affichage et filtre de capture : https://wiki.wireshark.org/DisplayFilters
6. **Linux Kernel Documentation** — Scaling in the Linux Networking Stack (RSS, RPS, RFS, XPS) : https://docs.kernel.org/networking/scaling.html
7. **Cisco** — Documentation officielle de dépannage, de capture et de surveillance pour la version et la plateforme IOS/IOS XE concernées : https://www.cisco.com/c/en/us/support/index.html
8. **IETF RFC 7011** — *Specification of the IP Flow Information Export (IPFIX) Protocol for the Exchange of Flow Information* : https://www.rfc-editor.org/rfc/rfc7011.html
9. **OpenTelemetry Documentation** — Concepts de métriques, traces et logs : https://opentelemetry.io/docs/concepts/
10. **NIST Cybersecurity Framework 2.0** — ressources de gestion du risque et de réponse aux incidents : https://www.nist.gov/cyberframework

Les normes, manuels et commandes évoluent. Consulter la documentation officielle correspondant aux versions logicielles, licences et plateformes réellement déployées avant d’exécuter une commande ou de modifier un environnement de production.
