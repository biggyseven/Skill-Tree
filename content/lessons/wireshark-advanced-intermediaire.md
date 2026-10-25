# Analyse Wireshark avancée --- Niveau intermédiaire

Ce cours prolonge le niveau débutant. Il ne recommence pas depuis zéro :
il suppose que le lecteur sait déjà ouvrir une capture, sélectionner une
interface, appliquer un filtre d'affichage simple, reconnaître les
couches Ethernet/IP/TCP/UDP, suivre un flux TCP et repérer les requêtes
DNS ou HTTP/TLS. Le travail intermédiaire consiste à passer d'une
observation ponctuelle à une enquête reproductible : formuler une
hypothèse, choisir les paquets qui peuvent la confirmer, distinguer
symptômes et causes, puis documenter la conclusion avec des preuves.

L'objectif n'est pas de mémoriser une liste de filtres. Il s'agit
d'apprendre à construire une lecture cohérente du trafic, à comprendre
les limites d'une capture, à comparer plusieurs points d'observation et
à éviter les conclusions trop rapides. Les exemples utilisent des
adresses privées fictives et des noms de domaine réservés à la
documentation. Adaptez les interfaces, adresses et ports à votre
laboratoire.

> **ENCADRÉ --- MISE EN CONTEXTE**
>
> Vous êtes technicien réseau dans une petite organisation. Plusieurs
> utilisateurs signalent que l'application de gestion est lente, mais
> seuls certains postes semblent touchés. Le serveur répond aux tests de
> connectivité et le problème disparaît parfois après quelques minutes.
> Votre mission est de déterminer si le ralentissement provient de la
> résolution DNS, de l'établissement TCP, de la retransmission, de la
> négociation TLS, du serveur ou d'un élément intermédiaire. Vous ne
> devez pas conclure « le réseau est lent » sans isoler une preuve
> observable.

## 1. Passer d'une lecture de paquets à une enquête

Une enquête Wireshark commence par une question précise. « Pourquoi
Internet est lent ? » est trop large. « Le client 192.0.2.25 établit-il
une connexion TCP au port 443 du serveur 198.51.100.40, et combien de
temps s'écoule entre SYN et SYN/ACK ? » est vérifiable. Une question
opérationnelle doit identifier un symptôme, une population concernée,
une période, une destination et une mesure attendue.

Avant de capturer, notez l'heure du problème, le nom de l'application,
le poste concerné, le réseau utilisé, le résultat attendu et les étapes
pour reproduire le défaut. Si possible, capturez un essai normal et un
essai défaillant dans des conditions proches. Cette comparaison est
souvent plus utile qu'une capture isolée, car elle fait ressortir les
différences plutôt que de noyer l'analyse dans tous les paquets
présents.

Évitez de modifier plusieurs variables en même temps. Si vous changez le
DNS, le VPN et le Wi-Fi entre deux essais, vous ne saurez pas quelle
modification a influencé le résultat. Consignez chaque changement et son
heure. Pour une enquête sérieuse, conservez la capture originale en
lecture seule et réalisez les annotations sur une copie. Calculez
éventuellement une empreinte du fichier afin de pouvoir démontrer que la
capture n'a pas été altérée.

Un bon compte rendu sépare quatre éléments : faits observés,
interprétation, hypothèses restantes et action suivante. « Trois
retransmissions TCP sont visibles » est un fait. « Le serveur est en
panne » est une interprétation qui exige d'autres preuves. Des
retransmissions peuvent être dues à une perte réelle, à une capture
incomplète, à un chemin asymétrique ou à des mécanismes d'offload de la
carte réseau. La discipline consiste à ne jamais confondre le paquet
affiché et la cause supposée.

## 2. Comprendre la topologie et le point de capture

Wireshark ne voit que ce qui arrive à son point de capture. Sur un poste
client, vous observez généralement les paquets de cette machine, pas
l'ensemble des échanges du réseau local. Un commutateur ne transmet pas
automatiquement tout le trafic de tous ses ports vers votre ordinateur.
Pour examiner un autre équipement, il faut un port miroir configuré
correctement, un TAP réseau, une capture sur l'équipement lui-même ou
une méthode de télémétrie adaptée.

Dessinez une topologie minimale : client, point d'accès éventuel,
commutateur, routeur, pare-feu, proxy, VPN et serveur. Indiquez les
adresses et interfaces pertinentes, les éventuels NAT et les frontières
de chiffrement. Pour chaque capture, consignez le lieu d'observation, le
sens du trafic, la méthode de capture et les pertes éventuelles
signalées par l'outil. Deux captures réalisées à des endroits différents
peuvent montrer des tailles, des adresses et des horaires légèrement
différents sans que l'une soit nécessairement erronée.

Un NAT peut modifier les adresses IP et les ports entre deux points
d'observation. Un proxy peut terminer une connexion TCP et en créer une
seconde : le client et le serveur ne sont alors pas les deux extrémités
d'un même flux. Un tunnel VPN ajoute une enveloppe extérieure qui masque
une partie du trafic intérieur. Il faut donc éviter de suivre une
conversation uniquement par son adresse IP si un équipement
intermédiaire peut la réécrire.

Pour corréler deux captures, utilisez plusieurs indices : horodatage,
ports, drapeaux TCP, numéros de séquence relatifs ou absolus, longueur,
contenu non chiffré et événements applicatifs connus. La synchronisation
des horloges est essentielle. Si les systèmes ont des horloges décalées,
comparez d'abord les événements communs et estimez le décalage avant de
tirer des conclusions sur la latence.

## 3. Filtres de capture et filtres d'affichage

Les filtres de capture et les filtres d'affichage répondent à des
besoins différents. Le filtre de capture, basé sur la syntaxe
libpcap/BPF, décide quels paquets seront enregistrés. Un paquet exclu à
la capture ne pourra pas être récupéré après coup. Le filtre d'affichage
agit après l'enregistrement : il masque temporairement les paquets qui
ne correspondent pas, mais ne les supprime pas du fichier.

Pour une enquête exploratoire, privilégiez souvent une capture
suffisamment large, dans les limites de confidentialité et de stockage,
puis utilisez des filtres d'affichage pour affiner l'analyse. Pour une
capture longue sur un lien très chargé, un filtre de capture peut être
nécessaire. Il faut toutefois vérifier que ce filtre ne supprime pas les
messages de contrôle qui permettront d'expliquer la panne. Filtrer
uniquement TCP/443 peut, par exemple, faire disparaître les échanges DNS
qui précèdent la connexion ou les messages ICMP associés au diagnostic.

Exemples de filtres d'affichage utiles :

``` wireshark
ip.addr == 192.0.2.25
ip.src == 192.0.2.25 && tcp.dstport == 443
tcp.flags.syn == 1 && tcp.flags.ack == 0
tcp.analysis.retransmission
tcp.analysis.duplicate_ack
tcp.analysis.zero_window
dns
tls.handshake
icmp || icmpv6
```

Les noms exacts des champs disponibles dépendent de la version et du
protocole décodé. Utilisez l'autocomplétion de la barre de filtre et la
référence des champs de votre version. Les parenthèses clarifient les
expressions composées, particulièrement lorsque `and` et `or` sont
mélangés. Testez chaque partie séparément avant de combiner les
conditions. Un filtre qui ne retourne aucun paquet ne prouve pas qu'il
n'y a pas de trafic : il peut simplement être trop restrictif, viser le
mauvais champ ou ne pas correspondre à la version du protocole observée.

## 4. Lire une connexion TCP comme une chronologie

Une connexion TCP classique débute par le three-way handshake : SYN du
client, SYN/ACK du serveur, puis ACK du client. La présence du SYN ne
prouve pas que le serveur a reçu la demande. La présence du SYN/ACK
montre qu'un paquet de réponse a atteint le point de capture, mais pas
forcément qu'il a atteint l'application cliente si la capture est prise
ailleurs. L'ACK final indique que l'établissement a progressé, mais il
ne prouve pas que la requête applicative a réussi.

Filtre de départ :

``` wireshark
ip.addr == 192.0.2.25 && tcp.port == 443
```

Sélectionnez un paquet, puis utilisez « Follow TCP Stream » pour isoler
la conversation. Vérifiez les numéros de séquence, les ACK, les options
TCP négociées, les fenêtres annoncées et le temps écoulé entre les
étapes. L'affichage en numéros relatifs est pratique pour comprendre le
flux ; les numéros absolus peuvent être utiles lors d'une comparaison
technique entre captures. Notez quel mode est utilisé pour éviter de
mélanger les deux représentations.

Un délai avant le SYN/ACK peut correspondre à un filtrage silencieux,
une route défaillante, une surcharge ou une perte. Un RST reçu
rapidement indique plutôt un refus explicite ou une fermeture par une
pile TCP ou un équipement intermédiaire. Un RST ne signifie pas
automatiquement que le serveur applicatif est hors service : un
pare-feu, un proxy ou un service qui n'écoute pas peut produire ce
résultat. Examinez les adresses Ethernet, les TTL/hop limit, le moment
d'apparition et le point de capture.

La fin d'une connexion peut utiliser FIN/ACK pour une fermeture ordonnée
ou RST pour une réinitialisation. Les captures peuvent ne contenir qu'un
côté de l'échange. Ne supposez pas que l'absence d'un FIN prouve une
fermeture anormale : le processus de capture peut avoir commencé trop
tard, s'être terminé trop tôt ou avoir perdu des paquets.

## 5. Retransmissions, ACK dupliqués et pertes

Wireshark peut signaler des retransmissions TCP, des retransmissions
rapides, des ACK dupliqués ou des segments hors ordre. Ces annotations
sont des heuristiques calculées à partir des paquets présents dans la
capture. Elles aident à repérer des anomalies, mais ne sont pas des
verdicts sur la cause racine. Une capture prise sur une machine
utilisant des mécanismes d'offload peut montrer des segments qui ne
correspondent pas exactement aux trames réellement envoyées sur le fil.

Une retransmission apparaît lorsque l'émetteur renvoie des données qui
n'ont pas été acquittées dans le délai attendu ou après certains indices
de perte. Les ACK dupliqués peuvent indiquer que le récepteur attend un
segment manquant alors que des segments ultérieurs arrivent. Une
retransmission rapide peut survenir avant l'expiration du temporisateur,
lorsque les indices de perte sont suffisants. Les segments hors ordre
peuvent provenir du réseau, de chemins multipath, d'une capture sur un
seul point ou de l'ordre de livraison à l'outil de capture.

Filtres :

``` wireshark
tcp.analysis.retransmission
tcp.analysis.fast_retransmission
tcp.analysis.duplicate_ack
tcp.analysis.out_of_order
```

Analysez la séquence temporelle autour de l'événement. Quel segment
manque ? Le récepteur continue-t-il à acquitter le même numéro ?
L'émetteur finit-il par retransmettre ? La donnée retransmise est-elle
ensuite acquittée ? Les retransmissions se produisent-elles uniquement
dans un sens ? La latence augmente-t-elle avant la perte ? Ces questions
permettent de construire une hypothèse cohérente.

Pour confirmer une perte réseau, capturez idéalement aux deux extrémités
ou à plusieurs points stratégiques. Si le paquet est visible à la sortie
du client mais absent à l'entrée du serveur, la zone de recherche se
resserre. Si le paquet est visible aux deux endroits, cherchez plutôt
une perte dans la pile, un problème d'ACK retour ou une interprétation
erronée due à la capture. Sur un réseau de production, évitez les
conclusions absolues basées sur une seule capture.

## 6. Fenêtre TCP, contrôle de flux et zero window

Le contrôle de flux TCP permet au récepteur d'annoncer la quantité de
données qu'il peut accepter. Une fenêtre annoncée très faible ou nulle
peut ralentir l'émetteur sans qu'une congestion réseau soit
nécessairement en cause. Un événement « TCP ZeroWindow » indique
généralement que le récepteur annonce qu'il ne peut plus accepter de
données à cet instant. Il faut alors examiner l'activité de la machine
réceptrice, les délais d'application et la reprise de la fenêtre.

Filtres utiles :

``` wireshark
tcp.analysis.zero_window
tcp.analysis.window_update
tcp.window_size_value
```

L'échelle de fenêtre TCP est négociée lors de l'établissement. La valeur
affichée peut être la fenêtre brute ou la fenêtre calculée après
application du facteur d'échelle, selon le champ choisi et la version de
Wireshark. Ne comparez pas des valeurs sans vérifier leur signification.
Une grande fenêtre ne prouve pas à elle seule que le débit sera élevé :
la congestion, la perte, le RTT, la capacité de traitement et les
limites applicatives influencent également le débit.

Quand un zero window apparaît, identifiez l'extrémité qui l'annonce. Si
le serveur annonce une fenêtre nulle, l'application serveur peut lire
les données trop lentement, être bloquée ou manquer de ressources. Si le
client l'annonce, l'application cliente peut ne pas consommer assez
rapidement les réponses. Examinez la durée de l'état, les sondes de
fenêtre et les mises à jour qui suivent.

Distinguez contrôle de flux et contrôle de congestion. Le premier
protège le récepteur contre un dépassement de ses buffers ; le second
régule le débit en fonction de l'état du chemin. Les symptômes peuvent
se ressembler, mais les remèdes diffèrent. Ajouter de la bande passante
ne corrige pas une application qui ne lit plus son socket. À l'inverse,
augmenter les buffers ne résout pas nécessairement une perte sur le
chemin.

## 7. Mesurer les délais et la latence

Les horodatages de paquets sont la base d'une analyse temporelle, mais
ils doivent être interprétés selon la précision et la méthode de
capture. Un écart entre deux paquets sur une seule capture mesure un
intervalle observé au point de capture, pas nécessairement le RTT exact
du réseau. Pour estimer un RTT TCP, examinez le temps entre l'envoi d'un
segment et l'ACK qui en confirme la réception, en vous assurant que
l'ACK correspond bien aux données étudiées.

Utilisez les colonnes de temps relatif ou de delta temporel pour rendre
une séquence lisible. La fonction « Set Time Reference » permet de
prendre un paquet comme origine pour les événements suivants. Dans les
statistiques, les graphiques d'IO et les graphiques de flux peuvent
révéler des pauses, des rafales ou une période de récupération après une
perte. Un graphique aide à localiser l'intervalle intéressant ; il ne
remplace pas l'inspection des paquets.

Pour comparer deux captures, synchronisez les horloges ou calculez leur
décalage à partir d'événements communs. Une différence de 200 ms entre
les horodatages de deux hôtes peut venir d'une horloge décalée, et non
d'un délai de transmission. Si vous mesurez le RTT à partir d'une
capture unique sur le client, le décalage d'horloge entre client et
serveur n'intervient pas de la même façon que dans une comparaison
multi-hôtes.

Soyez prudent avec les timestamps générés par les cartes réseau, les
buffers de capture et les mécanismes de déchargement. Sur un hôte très
chargé, le moment où Wireshark reçoit une trame peut être différent du
moment exact où elle a circulé sur le support. Pour des mesures de
performance précises, utilisez des points de capture adaptés, vérifiez
la charge CPU et, si nécessaire, une instrumentation spécialisée.

## 8. DNS : distinguer résolution lente et application lente

Une application peut sembler lente parce que la résolution DNS tarde,
échoue ou interroge plusieurs serveurs. Filtrez les requêtes et réponses
DNS, puis associez chaque identifiant de transaction à sa réponse.
Observez le délai, le code de réponse, le type de requête et les
retransmissions. Une réponse NXDOMAIN signifie que le nom demandé
n'existe pas selon le serveur interrogé ; SERVFAIL indique un échec de
traitement ; une absence de réponse peut être due à une perte, à un
filtrage ou à un serveur indisponible.

Filtres de base :

``` wireshark
dns
dns.flags.response == 0
dns.flags.response == 1
dns.time > 1
```

Le champ `dns.time` peut être disponible pour les réponses appariées
dans certaines versions de Wireshark. Si un filtre ne fonctionne pas,
vérifiez l'autocomplétion et la version. Une capture peut manquer la
requête initiale si le cache du système ou de l'application répond déjà.
L'absence de DNS ne signifie donc pas que le nom n'a pas été résolu ; la
réponse peut provenir d'un cache local, d'un proxy ou d'un canal
chiffré.

DNS over HTTPS (DoH) et DNS over TLS (DoT) changent la visibilité. Une
capture peut montrer une connexion HTTPS ou TLS vers un résolveur, mais
pas nécessairement les noms demandés. Pour comprendre ce trafic, il faut
des journaux côté client ou résolveur, une configuration de laboratoire
contrôlée ou des métadonnées complémentaires. Ne tentez pas de
contourner le chiffrement ; recherchez des preuves autorisées et
proportionnées à l'incident.

Pour isoler un problème DNS, comparez la durée de résolution avec le
délai total de l'application. Si la résolution prend 20 ms mais que la
connexion TLS prend deux secondes, DNS n'est probablement pas la cause
principale du délai mesuré. Si la première requête échoue puis une
seconde réussit, examinez les serveurs interrogés, les délais de
retransmission et la politique de bascule du résolveur.

## 9. TLS : lire la négociation sans prétendre déchiffrer

Une capture TLS permet souvent de repérer le début de la négociation,
les versions proposées, les suites cryptographiques, les extensions et
certains messages d'alerte. Elle ne révèle pas automatiquement le
contenu applicatif. TLS 1.3 chiffre une plus grande partie de la
négociation que les anciennes versions, et les champs visibles dépendent
de la version, des extensions et du point de capture. Ne supposez pas
que chaque champ historique est disponible.

Filtres :

``` wireshark
tls
tls.handshake
tls.handshake.type == 1
tls.alert_message
```

Le ClientHello peut donner des indices sur la version proposée, les
suites et les extensions. Le ServerHello indique les choix retenus. La
présence d'un ClientHello sans réponse visible peut indiquer une perte,
un filtrage, un serveur qui ne répond pas ou simplement une capture
incomplète. Une alerte TLS peut être émise par le client ou le serveur :
identifiez l'émetteur avant d'attribuer la faute.

Le nom de serveur (SNI) peut être visible dans certaines captures, sauf
lorsque des mécanismes tels qu'Encrypted Client Hello le masquent. Le
certificat et les paramètres exacts visibles dépendent de la version TLS
et des conditions de capture. La visibilité évolue avec les protocoles :
une méthode d'analyse valable pour TLS 1.2 peut ne pas être applicable à
TLS 1.3.

Si vous êtes autorisé à analyser une session de laboratoire, Wireshark
peut utiliser des secrets de session fournis par une application
compatible, par exemple via un fichier de clés TLS. Cela doit être fait
avec le consentement approprié et en protégeant strictement les secrets.
Ne confondez pas la clé privée du certificat serveur avec les secrets de
session : dans les configurations modernes, la clé privée seule ne
permet généralement pas de déchiffrer une capture TLS enregistrée.

## 10. HTTP/2, HTTP/3 et QUIC

HTTP/2 fonctionne généralement au-dessus de TCP et TLS. Plusieurs flux
applicatifs peuvent partager une seule connexion TCP, de sorte qu'un
problème TCP peut affecter plusieurs requêtes simultanément. HTTP/3
utilise QUIC au-dessus d'UDP, avec chiffrement intégré et mécanismes de
transport distincts. Une capture d'HTTP/3 ne se lit donc pas comme une
session TCP classique, même si Wireshark peut décoder certains éléments
lorsque les conditions le permettent.

Pour HTTP/2, recherchez les messages de négociation de protocole, les
flux multiplexés et les durées entre requêtes et réponses. Pour QUIC,
identifiez les datagrammes UDP, les versions QUIC et les éventuels
messages décodables. Les numéros de flux et la structure visibles
dépendent du déchiffrement et de la version. Si le contenu n'est pas
déchiffrable, la taille et la temporalité des datagrammes peuvent encore
aider, mais ne suffisent pas à connaître le contenu applicatif.

Un changement de protocole peut expliquer pourquoi deux navigateurs sur
le même réseau se comportent différemment. L'un peut utiliser HTTP/3
alors que l'autre reste sur HTTP/2. Comparez les essais sans modifier
simultanément les autres variables et tenez compte du cache, des
connexions déjà ouvertes et des mécanismes de repli. Un succès en
TCP/443 ne prouve pas que UDP/443 est autorisé ou performant.

Ne bloquez pas arbitrairement UDP/443 en production pour « forcer TCP »
sans évaluer les effets. Cela peut modifier le comportement des
applications, le temps de connexion et la charge. Si un test comparatif
est nécessaire, faites-le dans un environnement contrôlé, documentez la
configuration et restaurez-la après l'expérience.

## 11. Capture TLS et confidentialité

Les fichiers PCAP et PCAPNG peuvent contenir des données sensibles :
noms d'hôtes, adresses, cookies, jetons, requêtes, métadonnées
d'utilisateurs et parfois du contenu applicatif en clair. Traitez une
capture comme un journal potentiellement confidentiel. Définissez une
finalité, limitez la durée, choisissez un emplacement protégé et
partagez uniquement avec les personnes qui ont besoin d'y accéder.

Avant d'envoyer une capture à un tiers, vérifiez les règles internes,
les obligations légales et le consentement applicable. L'anonymisation
des adresses ne suffit pas toujours : les noms DNS, horaires, tailles de
transfert et identifiants applicatifs peuvent permettre de reconnaître
une activité. Préférez un extrait minimal qui conserve les paquets
nécessaires à la démonstration, après validation que l'extrait ne
supprime pas les éléments de causalité.

Une capture chiffrée n'est pas forcément inoffensive. Elle peut révéler
quels services sont utilisés, quand un utilisateur s'est connecté et
combien de données ont été transférées. Un fichier de secrets TLS est
encore plus sensible : il peut permettre de déchiffrer le trafic
correspondant. Ne stockez pas les secrets de session avec les captures
partagées et supprimez-les selon la politique de conservation.

La qualité professionnelle d'une analyse comprend la protection des
données. Notez les personnes autorisées, la période de conservation et
les transformations effectuées. Conservez l'original dans un emplacement
contrôlé si les règles l'exigent, et fournissez une version expurgée
pour les échanges. N'utilisez jamais une capture obtenue sans
autorisation pour examiner des communications privées.

## 12. Expert Information : utile, mais pas infaillible

Le panneau Expert Information regroupe des événements classés par
gravité et catégorie. Il sert de point d'entrée pour repérer les
anomalies, mais ses avertissements sont des interprétations
automatiques. La gravité affichée ne mesure pas directement l'impact
métier. Une note peut signaler un comportement attendu, un artefact de
capture ou un véritable incident. L'analyste doit revenir au paquet et à
la chronologie.

Un grand nombre de retransmissions peut refléter une perte réelle, mais
également un point de capture saturé. Une somme de checksums incorrects
sur une capture locale peut être liée au checksum offloading : la carte
réseau calcule le checksum après que le logiciel de capture a observé le
paquet. Avant de désactiver une fonction ou d'accuser le réseau,
reproduisez la capture à un point indépendant si possible.

Pour chaque événement important, posez trois questions. Premièrement,
est-il reproductible ? Deuxièmement, est-il corrélé au symptôme observé
? Troisièmement, est-il visible depuis un autre point de capture ou
confirmé par un compteur système ? Si l'événement apparaît sur tous les
flux mais que l'application fonctionne normalement, il peut être un
artefact ou un comportement bénin. S'il apparaît uniquement pendant les
incidents et au bon endroit dans la chronologie, il mérite une enquête
plus approfondie.

Le panneau Expert Information ne remplace ni les compteurs d'interface,
ni les journaux du système, ni les métriques de l'application. Il
organise les indices que Wireshark sait inférer à partir de la capture.
Une analyse fiable utilise ces indices comme des pistes, puis les
confronte à des preuves indépendantes.

## 13. Statistiques et graphiques de flux

Les menus Statistics permettent de passer d'un paquet isolé à une vue
d'ensemble : conversations, endpoints, hiérarchie des protocoles,
longueurs de paquets, débits et flux d'E/S. Commencez par vérifier si la
capture contient bien la période et les interfaces attendues. Les
statistiques calculées sur une capture partielle ne représentent pas
nécessairement l'ensemble du trafic réel.

La hiérarchie des protocoles montre la part des protocoles décodés dans
les données capturées. Les conversations aident à identifier les
principaux échanges et à repérer une destination inattendue. Les
graphiques d'E/S peuvent montrer des pauses, des rafales ou des
changements de débit. Choisissez un intervalle cohérent avec le problème
: un intervalle trop large masque les micro-événements, tandis qu'un
intervalle trop fin rend le graphique difficile à lire.

Les statistiques ne prouvent pas la cause. Un flux représentant 80 % des
octets peut être normal pour un transfert de fichier. Un débit faible
peut provenir d'une application qui envoie peu de données, pas d'une
capacité réseau insuffisante. Comparez les volumes à l'objectif attendu
et à une capture de référence. Pour une application interactive, la
latence et la régularité peuvent compter davantage que le débit maximal.

Documentez les paramètres de calcul, la période, les filtres actifs et
les limites du fichier. Une statistique produite après application d'un
filtre ne décrit que les paquets visibles selon ce filtre. Pour éviter
de comparer des résultats incompatibles, utilisez les mêmes filtres et
les mêmes fenêtres temporelles pour les essais avant/après.

## 14. Analyse des resets, refus et fermetures

Les drapeaux RST, FIN et ACK doivent être interprétés dans le contexte
du flux. Un RST indique une réinitialisation de la connexion TCP ; il
peut être émis par un hôte, un pare-feu, un proxy ou un autre équipement
qui intervient dans le chemin. La source IP affichée n'est pas toujours
une preuve suffisante de l'équipement qui a réellement généré le paquet,
notamment si des dispositifs intermédiaires réécrivent ou injectent des
paquets.

Examinez le moment du RST. Survient-il immédiatement après le SYN ?
Après le ClientHello TLS ? Après une période d'inactivité ? En réponse à
des données applicatives ? Comparez le TTL du paquet, les adresses
Ethernet et les captures situées de part et d'autre du pare-feu si elles
sont disponibles. Des différences peuvent suggérer un équipement
intermédiaire, mais aucun indice isolé n'est définitif.

Une fermeture FIN ordonnée indique que l'émetteur ne prévoit plus
envoyer de données dans ce sens ; les deux directions peuvent se fermer
à des moments différents. Un RST peut être légitime, par exemple
lorsqu'une application ferme brutalement un socket ou qu'un port
n'écoute pas. Le terme « connexion réinitialisée » décrit un événement,
pas une attribution de responsabilité.

Pour rédiger une conclusion, utilisez des formulations mesurées : « Un
RST apparaît sur le flux immédiatement après le ClientHello, depuis le
point de capture client. Une capture côté serveur est nécessaire pour
déterminer si le serveur l'a généré ou si un équipement intermédiaire
est impliqué. » Cette formulation est plus utile qu'« un pare-feu bloque
TLS » sans preuve.

## 15. Captures sur des réseaux Wi-Fi

Une capture effectuée sur l'interface Wi-Fi d'un poste montre
généralement le trafic que le système reçoit ou transmet au niveau
réseau. Elle ne fournit pas nécessairement tous les détails des trames
802.11, des retransmissions radio, du signal, des changements de canal
ou des échanges entre autres stations. Une capture en mode moniteur,
réalisée avec un adaptateur compatible et une configuration adaptée,
offre une autre perspective mais demande une compréhension des canaux et
du chiffrement Wi-Fi.

Pour une lenteur Wi-Fi, distinguez les symptômes IP/TCP des causes
radio. Les retransmissions TCP peuvent résulter d'une perte sur le
Wi-Fi, mais aussi d'une congestion en amont, d'un problème serveur ou
d'une capture incomplète. Corrélez les captures avec le RSSI, le taux de
retransmission radio, les changements de point d'accès et les journaux
du contrôleur si ces données sont accessibles.

Comparez le même poste au même endroit, sur le même service, avec et
sans connexion filaire si possible. Gardez à l'esprit que le changement
de support peut aussi changer l'adresse IP, la route, le DNS ou la
politique de sécurité. Contrôlez ces variables au lieu d'attribuer toute
différence au Wi-Fi.

Les captures radio peuvent révéler des identifiants et des informations
sur les appareils environnants. Ne capturez que dans un cadre autorisé.
N'essayez pas de contourner les protections d'un réseau tiers ;
privilégiez le réseau de laboratoire ou les outils d'administration
autorisés.

## 16. Offloading, checksum et segmentation

Les fonctions d'offload déplacent certains traitements de la pile réseau
vers la carte réseau. Le checksum offloading peut faire apparaître des
sommes de contrôle invalides dans une capture réalisée avant le calcul
final. Le TCP Segmentation Offload (TSO) et le Generic Segmentation
Offload (GSO) peuvent faire apparaître de grands segments dans une
capture locale, alors que la carte les découpe ensuite en trames
adaptées au MTU du lien. À l'inverse, GRO/LRO peut regrouper plusieurs
segments reçus avant qu'ils soient visibles par l'outil.

Ces phénomènes sont particulièrement importants lors de l'analyse des
tailles de paquets, des checksums et des retransmissions. Un paquet
supérieur au MTU visible dans une capture locale n'implique pas
automatiquement qu'une trame Ethernet de cette taille a circulé sur le
fil. Vérifiez l'interface et le sens de capture, les fonctionnalités
activées et la présence d'un point de capture externe.

Pour confirmer un soupçon, réalisez si possible une capture sur un port
miroir ou un TAP, comparez les résultats et consultez les compteurs de
la carte réseau. Désactiver temporairement l'offload peut être utile
dans un laboratoire, mais ne le faites pas sans autorisation sur un
poste de production : la modification peut affecter les performances et
doit être restaurée après le test.

Consignez précisément la méthode utilisée. Une conclusion fondée sur une
capture locale avec TSO actif doit mentionner cette limite. L'objectif
n'est pas de rendre chaque capture parfaite, mais de connaître ce que
l'instrument mesure réellement.

## 17. TShark : automatiser les vérifications

TShark permet de lire et de filtrer des captures depuis la ligne de
commande. Il est utile pour répéter les mêmes contrôles sur plusieurs
fichiers, extraire des champs ou intégrer des vérifications dans un
rapport. Il ne remplace pas la compréhension du protocole :
l'automatisation peut reproduire une erreur de filtre aussi facilement
qu'une analyse correcte.

Exemples :

``` bash
tshark -r capture.pcapng -Y "tcp.analysis.retransmission"
tshark -r capture.pcapng -Y "dns" -T fields -e frame.time -e ip.src -e dns.qry.name
tshark -r capture.pcapng -q -z conv,tcp
tshark -r capture.pcapng -Y "tls.handshake" -T fields -e frame.number -e ip.src -e tls.handshake.type
```

Sous Windows, utilisez le chemin vers `tshark.exe` ou ajoutez le
répertoire Wireshark au PATH. Vérifiez la syntaxe disponible dans votre
version avec `tshark -h` et la liste des champs avec les options d'aide.
Les noms des champs évoluent selon les versions et les protocoles
reconnus.

Lors d'une extraction, conservez les métadonnées nécessaires à la
reproductibilité : version de TShark, commande complète, filtre, fichier
source et date d'exécution. Évitez de coller des données sensibles dans
des journaux accessibles à tous. Si vous transformez une capture,
conservez l'original conformément à la politique de l'organisation.

Un script peut compter les retransmissions ou mesurer les temps de
réponse DNS, mais ces chiffres doivent être contextualisés. Un nombre
élevé de retransmissions dans une capture de dix minutes n'est pas
comparable à celui d'une capture de dix secondes. Un script doit
signaler les fichiers illisibles, les champs absents et les erreurs de
commande plutôt que produire silencieusement un rapport incomplet.

## 18. Étude de cas : ouverture de site très lente

**Situation.** Un utilisateur indique que le premier chargement d'un
portail prend huit secondes, tandis que les pages suivantes sont
rapides. L'objectif est de déterminer où se trouve le délai :
résolution, établissement TCP, TLS, attente serveur ou transfert.

Commencez par capturer un chargement complet et identifiez le flux
correspondant au nom du portail. Mesurez le délai DNS, le temps entre
SYN et SYN/ACK, le temps de négociation TLS et l'intervalle entre la
requête et la première réponse visible. Si HTTP est chiffré et qu'aucun
secret de session autorisé n'est disponible, vous ne pourrez pas
nécessairement identifier précisément la requête ; utilisez alors les
métadonnées disponibles et les journaux applicatifs.

Comparez ensuite un chargement lent et un chargement rapide. Si DNS est
lent uniquement au premier essai, le cache peut expliquer une partie de
la différence. Si TCP s'établit rapidement mais que la négociation TLS
prend longtemps, examinez les pertes, les retransmissions et la réponse
du serveur. Si la connexion et TLS sont rapides mais qu'un long
intervalle précède les données, les journaux serveur ou applicatifs
deviennent essentiels.

N'oubliez pas les connexions parallèles. Une page moderne peut contacter
plusieurs domaines pour charger scripts, images et API. Le délai perçu
peut venir d'une seule ressource bloquante, et non de la connexion
principale. Utilisez les outils développeur du navigateur en complément
de Wireshark, puis corrélez les horodatages.

**Conclusion attendue.** Un rapport professionnel indique la phase qui
consomme le temps, les paquets ou événements qui l'établissent, les
hypothèses éliminées et les preuves encore nécessaires. Évitez « le
serveur est lent » si la capture ne permet pas de distinguer le
traitement serveur d'un délai applicatif ou d'un équipement
intermédiaire.

## 19. Étude de cas : appels vidéo instables

**Situation.** Les appels vidéo présentent des coupures alors que la
navigation web fonctionne. L'application peut utiliser UDP, RTP/SRTP, un
protocole propriétaire ou QUIC. Une capture réseau peut montrer les
adresses, ports, tailles et horaires, mais le contenu média est
généralement chiffré.

Identifiez d'abord les flux associés à l'appel à partir d'un essai
contrôlé et des journaux de l'application. Examinez les intervalles
entre datagrammes, les changements de destination, les périodes de
silence et les éventuelles pertes visibles. Ne concluez pas qu'un
datagramme manquant dans une capture représente forcément une perte sur
le réseau : il peut ne pas avoir été capturé, être envoyé sur une autre
interface ou utiliser un autre chemin.

Pour une application temps réel, le délai et la gigue peuvent compter
autant que le débit. Une perte occasionnelle peut être masquée par les
mécanismes de correction, alors qu'une rafale de pertes peut entraîner
une coupure perceptible. Wireshark peut calculer certaines statistiques
pour des protocoles décodables, mais les résultats dépendent de la
capture et de la prise en charge du protocole.

Comparez un appel réussi et un appel défaillant sur le même poste, puis
comparez Wi-Fi et Ethernet si cela est autorisé. Vérifiez aussi la
charge CPU, la qualité du signal radio et les métriques de
l'application. Si la capture montre que les datagrammes sortent du poste
mais qu'aucune réponse ne revient, il faut une capture au point distant
ou des journaux de l'infrastructure pour localiser précisément la perte.

Ne capturez pas plus longtemps que nécessaire. Les flux audio et vidéo
peuvent révéler des habitudes personnelles, même lorsque leur contenu
est chiffré.

## 20. Étude de cas : soupçon de MTU ou de PMTUD

**Situation.** Une application ouvre une session mais certaines pages ou
certains transferts se figent. Les petits échanges fonctionnent, alors
que des transferts plus importants échouent. Cette différence peut faire
suspecter un problème MTU/PMTUD, mais elle ne suffit pas à le prouver.

Dans Wireshark, observez les retransmissions, les tailles de segments,
les messages ICMP/ICMPv6 et les éventuelles différences entre les
captures de part et d'autre d'un tunnel. En IPv4, un routeur qui ne peut
pas fragmenter un paquet avec DF positionné peut renvoyer ICMP
Destination Unreachable, Fragmentation Needed (type 3, code 4). En IPv6,
les routeurs ne fragmentent pas les paquets en transit ; le message
Packet Too Big est un message ICMPv6 de type 2. Si ces messages sont
filtrés, la découverte de la MTU peut échouer.

Filtres utiles :

``` wireshark
icmp.type == 3 && icmp.code == 4
icmpv6.type == 2
tcp.analysis.retransmission
```

Vérifiez les tailles réellement observées au bon point de capture et
tenez compte de l'offload. Comparez le comportement avec et sans VPN
uniquement dans un test autorisé et documenté. Un tunnel ajoute des
en-têtes, ce qui réduit la taille utile disponible dans le paquet
extérieur. Une MSS mal adaptée peut contribuer au problème, mais il faut
mesurer le chemin et examiner les messages de contrôle avant de modifier
la configuration.

Le résultat attendu est une chaîne de preuves : paquets trop grands sur
un segment, absence ou présence des messages PTB nécessaires,
retransmissions cohérentes avec le blocage, et amélioration après une
correction contrôlée. Le seul fait que « les gros fichiers échouent »
n'est pas une preuve suffisante d'un problème MTU.

## 21. Étude de cas : connexion qui se réinitialise

**Situation.** Une application affiche « connexion réinitialisée » après
une ou deux secondes. La capture contient un handshake TCP complet, puis
un ClientHello TLS, suivi d'un RST. Plusieurs causes sont possibles :
rejet côté serveur, politique de sécurité, proxy, inspection TLS,
incompatibilité de protocole ou problème applicatif.

Construisez une chronologie paquet par paquet. Confirmez que le RST
appartient au bon flux et notez l'adresse source, le port, le TTL et le
délai après le ClientHello. Recherchez si la réponse vient du serveur
attendu ou d'un intermédiaire. Si possible, capturez simultanément côté
client et côté serveur. Si le RST apparaît côté client mais n'existe pas
dans la capture serveur, un équipement intermédiaire devient une
hypothèse importante, sans être automatiquement prouvé tant que les
captures et les horloges ne sont pas validées.

Examinez les journaux du service, du proxy et du pare-feu. Vérifiez si
l'échec concerne tous les clients ou seulement un sous-réseau, un
certificat, une version TLS ou un nom d'hôte. Un test vers la même
adresse IP mais avec un autre nom peut modifier SNI et la sélection du
service : interprétez donc ce test avec prudence.

Ne désactivez pas la sécurité TLS pour contourner l'incident. Si une
comparaison de version ou de configuration est nécessaire, utilisez un
environnement de test et restaurez les paramètres. Une analyse
professionnelle localise le point où le comportement diverge et propose
la prochaine vérification, au lieu d'attribuer immédiatement la faute à
un seul composant.

## 22. Méthode de comparaison avant/après

Une modification réseau doit être évaluée par une comparaison équitable.
Définissez une hypothèse et un critère de succès avant le changement.
Par exemple : « La modification réduit le temps de réponse DNS médian
sous 100 ms sur dix essais identiques » ou « le nombre de
retransmissions observées sur le flux de test diminue sans dégrader le
débit ». Un objectif mesurable évite de déclarer la correction réussie
uniquement parce qu'un essai semble meilleur.

Réalisez plusieurs essais, car les réseaux sont variables. Gardez la
même destination, la même application, le même poste, la même route et
des conditions aussi proches que possible. Notez les différences
inévitables, notamment le cache DNS, la réutilisation de connexions, le
contenu dynamique et les changements de charge. Pour une application
Web, un essai froid et un essai chaud ne sont pas directement
comparables sans explication.

Conservez les captures avant et après avec des noms distincts et des
notes d'exécution. Utilisez les mêmes filtres et les mêmes méthodes de
calcul. Si une modification de MTU, de MSS ou de filtrage ICMP est
envisagée, testez d'abord en laboratoire ou selon une procédure de
changement approuvée. Prévoyez une stratégie de retour arrière.

Une correction réussie doit être confirmée par le symptôme métier et par
des mesures techniques. Si les retransmissions diminuent mais que le
délai utilisateur ne change pas, le problème initial n'est peut-être pas
résolu. Si le service s'améliore mais que les captures ne montrent
aucune différence, d'autres mesures peuvent être nécessaires. Le compte
rendu doit expliquer ce qui a été prouvé et ce qui reste inconnu.

## 23. Laboratoire guidé : établir une ligne de base TCP

**Préparation.** Utilisez deux machines de laboratoire ou une
application de test que vous êtes autorisé à joindre. Notez les
adresses, l'interface et l'heure. Lancez Wireshark sur l'interface
adéquate, démarrez la capture, ouvrez une connexion vers un service
connu, puis arrêtez la capture après la fin de l'essai. N'enregistrez
pas inutilement le trafic d'autres utilisateurs.

**Analyse.** Appliquez un filtre sur l'adresse du client et le port du
service. Repérez le SYN, le SYN/ACK et l'ACK final. Mesurez le temps
entre le SYN et le SYN/ACK, puis identifiez la première donnée
applicative. Suivez le flux et vérifiez la fermeture. Ajoutez les
colonnes de delta temporel, longueur et ports si elles facilitent la
lecture.

**Questions.** Le handshake est-il complet ? Quelle est la durée
d'établissement ? Y a-t-il des retransmissions ? Les données
arrivent-elles en rafales ? Le serveur envoie-t-il une fermeture FIN ou
un RST ? La capture contient-elle les deux directions ? Quelles
conclusions sont certaines et lesquelles demandent un autre point
d'observation ?

**Livrable.** Rédigez un résumé de dix lignes : objectif, topologie,
méthode, filtre, observations mesurées, anomalies, limites de capture,
conclusion et prochaine action. Une bonne réponse peut conclure
qu'aucune anomalie TCP évidente n'est visible, sans prétendre que tout
le réseau fonctionne parfaitement. La portée de la conclusion doit
correspondre exactement à la portée de l'observation.

## 24. Laboratoire guidé : DNS et établissement TLS

**Objectif.** Distinguer le délai de résolution DNS du délai
d'établissement de la connexion sécurisée. Choisissez un service de test
et démarrez une capture avant d'ouvrir l'application. Évitez de
réutiliser une connexion déjà ouverte si vous voulez mesurer un
établissement complet ; un cache ou une connexion persistante peut
masquer certaines étapes.

Filtrez `dns` et repérez la requête, son identifiant, le type demandé et
la réponse correspondante. Mesurez le temps de réponse et notez le code
de retour. Ensuite, filtrez `tcp.port == 443` ou le port réellement
utilisé. Repérez le handshake TCP et les messages TLS décodables.
Mesurez les intervalles sans supposer que chaque attente est due au
serveur.

Répétez le test après un délai, puis comparez les résultats. Si aucune
requête DNS n'apparaît au second essai, le cache peut être responsable.
Si DNS répond rapidement mais que TLS tarde, examinez les
retransmissions et la chronologie du handshake. Si le service utilise
QUIC, le trafic peut être UDP et la méthode d'analyse doit être adaptée.

**Compte rendu.** Présentez un tableau avec phase, heure de début, heure
de fin, durée, preuve et limites. Ne publiez pas de données personnelles
ni de secrets. Si le contenu TLS n'est pas déchiffré, dites-le
explicitement. Le but du laboratoire est d'apprendre à séparer les
phases d'une connexion et à formuler une conclusion reproductible.

## 25. Laboratoire guidé : repérer une perte simulée

Ce laboratoire doit être effectué uniquement dans un environnement que
vous contrôlez. Utilisez un simulateur réseau ou une machine de test
pour introduire une perte limitée et réversible. Ne configurez pas de
perte sur un réseau de production. Capturez le trafic avant la
manipulation, pendant l'essai et après le retour à l'état normal.

Établissez une ligne de base avec un transfert de taille connue. Pendant
la simulation, observez les retransmissions TCP, les ACK dupliqués et
l'évolution des délais. Si la perte est placée dans un seul sens, les
symptômes peuvent différer de ceux d'une perte dans les deux sens. Si la
capture ne se trouve pas sur le segment où la perte est introduite, les
paquets manquants peuvent être difficiles à interpréter.

Après l'essai, retirez la règle de perte et vérifiez qu'elle a
effectivement disparu. Répétez le transfert pour confirmer le retour à
la ligne de base. Comparez les statistiques et conservez les commandes
de configuration dans votre cahier de laboratoire, sans appliquer ces
commandes sur une infrastructure non autorisée.

Le résultat attendu n'est pas un nombre universel de retransmissions,
car il dépend du timing et du comportement de TCP. Le résultat attendu
est une explication de la séquence observée : segment envoyé, absence
d'ACK ou ACK dupliqués, retransmission éventuelle, puis reprise de la
progression. Distinguez les événements induits volontairement des
anomalies indépendantes du laboratoire.

## 26. Construire un rapport d'incident lisible

Un rapport de capture doit permettre à une autre personne de reproduire
l'analyse. Indiquez le contexte, l'impact, l'heure, le périmètre, le
point de capture, la version de Wireshark, les filtres appliqués et les
hypothèses étudiées. Incluez des numéros de trame, des horodatages et
les champs utiles. Une capture d'écran seule est rarement suffisante :
elle peut masquer le filtre, les paquets précédents et le contexte
temporel.

Structure conseillée :

1.  **Symptôme et impact** : qui est touché, depuis quand et sur quelle
    fonction.
2.  **Méthode** : où et comment la capture a été prise.
3.  **Observations** : faits mesurés avec références de trames.
4.  **Interprétation** : explication la plus cohérente avec les faits.
5.  **Hypothèses restantes** : éléments qui ne peuvent pas être
    départagés.
6.  **Action proposée** : test suivant, responsable et critère de
    réussite.
7.  **Protection des données** : emplacement, accès et durée de
    conservation.

Évitez les formulations absolues quand la capture est partielle.
Préférez « aucun SYN/ACK n'est visible au point de capture client
pendant la fenêtre étudiée » à « le serveur ne répond jamais ». La
première phrase décrit précisément l'observation ; la seconde dépasse
les preuves disponibles.

Lorsque vous recommandez une modification, expliquez le risque, le
périmètre, la procédure de validation et le retour arrière. Le rapport
doit aider à prendre une décision technique, pas seulement montrer que
Wireshark a été utilisé.

## 27. Erreurs d'interprétation fréquentes

**Erreur : un checksum invalide signifie forcément une corruption.** Une
capture locale peut être prise avant le calcul final par la carte
réseau. Vérifiez l'offload et un point externe.

**Erreur : une retransmission prouve que le routeur a perdu le paquet.**
La retransmission indique un manque d'acquittement ou une détection de
perte ; elle ne localise pas la cause. Capturez à plusieurs points et
consultez les compteurs.

**Erreur : le serveur est responsable parce que son IP apparaît dans le
flux.** Un proxy ou un pare-feu peut terminer ou modifier la connexion.
Examinez la topologie et les points de capture.

**Erreur : aucune requête DNS signifie que DNS n'a pas été utilisé.** Le
cache, DoH, DoT, un proxy ou une connexion persistante peuvent expliquer
l'absence de requête visible.

**Erreur : un port ouvert prouve que l'application fonctionne.** Le
handshake TCP ne garantit pas la réussite de TLS ou de la requête
applicative.

**Erreur : la plus grosse conversation est forcément le problème.** Le
volume dépend de l'usage ; comparez au comportement attendu et à la
chronologie de l'incident.

**Erreur : les messages Expert Information sont des verdicts.** Ce sont
des indices calculés ; vérifiez les paquets et les limites de capture.

**Erreur : une capture chiffrée ne contient rien de sensible.** Les
métadonnées peuvent révéler des usages, des destinations et des
habitudes. Appliquez les règles de confidentialité.

## 28. Schéma : chaîne d'analyse reproductible

Le schéma suivant illustre une enquête qui part d'un symptôme, collecte
une capture, construit une chronologie, teste une hypothèse et confirme
la correction. Il est volontairement générique : il ne remplace pas les
détails propres à chaque incident.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 300" width="100%" role="img" aria-label="Chaîne d’analyse Wireshark">
<style>
.t{font:16px Arial,sans-serif;fill:#f8fafc}.s{font:13px Arial,sans-serif;fill:#dbeafe}
.n{fill:#172554;stroke:#60a5fa;stroke-width:2}.g{fill:#14532d;stroke:#4ade80;stroke-width:2}
.a{stroke:#93c5fd;stroke-width:3;fill:none;stroke-linecap:round;stroke-dasharray:9 9;animation:dash 1.4s linear infinite}
@keyframes dash{to{stroke-dashoffset:-36}}
@media(prefers-reduced-motion:reduce){.a{animation:none}}
</style>
<rect width="960" height="300" rx="18" fill="#0b1220"/>
<text x="480" y="32" text-anchor="middle" class="t" font-size="21">Une enquête reproductible</text>
<g transform="translate(28,78)"><rect class="n" width="160" height="90" rx="12"/><text x="80" y="35" text-anchor="middle" class="t">1. Symptôme</text><text x="80" y="59" text-anchor="middle" class="s">Question précise</text></g>
<path class="a" d="M190 123 H220"/>
<g transform="translate(222,78)"><rect class="n" width="160" height="90" rx="12"/><text x="80" y="35" text-anchor="middle" class="t">2. Capture</text><text x="80" y="59" text-anchor="middle" class="s">Point identifié</text></g>
<path class="a" d="M384 123 H414"/>
<g transform="translate(416,78)"><rect class="n" width="160" height="90" rx="12"/><text x="80" y="35" text-anchor="middle" class="t">3. Chronologie</text><text x="80" y="59" text-anchor="middle" class="s">Paquets et délais</text></g>
<path class="a" d="M578 123 H608"/>
<g transform="translate(610,78)"><rect class="n" width="140" height="90" rx="12"/><text x="70" y="35" text-anchor="middle" class="t">4. Hypothèse</text><text x="70" y="59" text-anchor="middle" class="s">Preuve attendue</text></g>
<path class="a" d="M752 123 H782"/>
<g transform="translate(784,78)"><rect class="g" width="148" height="90" rx="12"/><text x="74" y="35" text-anchor="middle" class="t">5. Validation</text><text x="74" y="59" text-anchor="middle" class="s">Avant / après</text></g>
<text x="480" y="220" text-anchor="middle" class="s">Si la preuve manque : améliorer le point de capture, pas deviner la cause.</text>
<circle r="6" fill="#facc15"><animateMotion dur="6s" repeatCount="indefinite" path="M188 123 L220 123 L382 123 L414 123 L576 123 L608 123 L750 123 L782 123"/></circle>
</svg>
</div>

## 29. Schéma : localiser un délai dans les phases de connexion

Une session peut être découpée en résolution, établissement transport,
négociation TLS et échange applicatif. Le délai visible dans chaque
phase oriente les vérifications suivantes, mais il faut tenir compte du
cache, des connexions persistantes et des protocoles qui multiplexent
plusieurs requêtes.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 280" width="100%" role="img" aria-label="Phases et délais d’une connexion">
<style>.t{font:16px Arial;fill:#f8fafc}.s{font:13px Arial;fill:#cbd5e1}.b{stroke-width:2;rx:9}.line{stroke:#94a3b8;stroke-width:2;stroke-dasharray:6 6}@media(prefers-reduced-motion:reduce){animateMotion{display:none}}</style>
<rect width="960" height="280" rx="16" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" class="t" font-size="21">Décomposer le temps perçu</text>
<line x1="70" y1="142" x2="890" y2="142" class="line"/>
<rect x="70" y="92" width="180" height="90" class="b" fill="#1e3a8a" stroke="#60a5fa"/><text x="160" y="123" text-anchor="middle" class="t">DNS</text><text x="160" y="148" text-anchor="middle" class="s">Résolution / cache</text>
<rect x="270" y="92" width="180" height="90" class="b" fill="#164e63" stroke="#22d3ee"/><text x="360" y="123" text-anchor="middle" class="t">TCP ou QUIC</text><text x="360" y="148" text-anchor="middle" class="s">Établissement</text>
<rect x="470" y="92" width="180" height="90" class="b" fill="#4c1d95" stroke="#c084fc"/><text x="560" y="123" text-anchor="middle" class="t">TLS</text><text x="560" y="148" text-anchor="middle" class="s">Négociation visible</text>
<rect x="670" y="92" width="220" height="90" class="b" fill="#14532d" stroke="#4ade80"/><text x="780" y="123" text-anchor="middle" class="t">Application</text><text x="780" y="148" text-anchor="middle" class="s">Requête / première réponse</text>
<circle r="7" fill="#facc15"><animateMotion dur="5s" repeatCount="indefinite" path="M70 142 H890"/></circle>
<text x="480" y="225" text-anchor="middle" class="s">Mesurer chaque intervalle ; un long délai n’identifie pas à lui seul la cause.</text>
</svg>
</div>

## 30. Schéma : triangulation avec plusieurs points de capture

Une capture côté client, une capture au niveau du pare-feu et une
capture côté serveur permettent de resserrer la zone où un paquet
disparaît ou un délai apparaît. Les horloges doivent être synchronisées
ou leur décalage estimé ; le NAT, le proxy et le tunnel peuvent modifier
ce que chaque point observe.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 300" width="100%" role="img" aria-label="Corrélation entre trois points de capture">
<style>.t{font:16px Arial;fill:#f8fafc}.s{font:13px Arial;fill:#cbd5e1}.n{fill:#172554;stroke:#60a5fa;stroke-width:2}.p{stroke:#34d399;stroke-width:3;fill:none;stroke-dasharray:10 8;animation:move 1.5s linear infinite}@keyframes move{to{stroke-dashoffset:-36}}@media(prefers-reduced-motion:reduce){.p{animation:none}}</style>
<rect width="960" height="300" rx="16" fill="#0b1220"/><text x="480" y="32" text-anchor="middle" class="t" font-size="21">Trianguler avec plusieurs captures</text>
<rect x="50" y="88" width="210" height="100" rx="12" class="n"/><text x="155" y="124" text-anchor="middle" class="t">Point A</text><text x="155" y="150" text-anchor="middle" class="s">Client</text>
<rect x="375" y="88" width="210" height="100" rx="12" class="n"/><text x="480" y="124" text-anchor="middle" class="t">Point B</text><text x="480" y="150" text-anchor="middle" class="s">Pare-feu / tunnel</text>
<rect x="700" y="88" width="210" height="100" rx="12" class="n"/><text x="805" y="124" text-anchor="middle" class="t">Point C</text><text x="805" y="150" text-anchor="middle" class="s">Serveur</text>
<path class="p" d="M260 138 H375 M585 138 H700"/>
<text x="480" y="230" text-anchor="middle" class="s">Comparer les paquets, les horloges, les NAT et les transformations de tunnel.</text>
<text x="480" y="254" text-anchor="middle" class="s">Un paquet absent d’une capture n’est pas automatiquement perdu sur le réseau.</text>
</svg>
</div>

## 31. Exercices d'application

**Exercice 1 --- Handshake lent.** Le SYN part à 10:00:00.000 et le
SYN/ACK arrive à 10:00:00.240. Quelle durée mesurez-vous ? Peut-on en
déduire que le serveur a traité la requête pendant 240 ms ? Expliquez
pourquoi la durée inclut le chemin aller-retour et le traitement
éventuel, et pourquoi une capture unique ne permet pas de séparer ces
contributions.

**Exercice 2 --- DNS.** La requête DNS obtient une réponse en 15 ms,
puis le ClientHello est suivi d'une attente de 1,5 seconde. Quelle
hypothèse est la plus directement soutenue ? Quelles informations
supplémentaires permettraient de distinguer perte, attente de serveur,
inspection intermédiaire ou autre cause ?

**Exercice 3 --- Retransmissions.** Wireshark signale plusieurs
retransmissions, mais une capture prise sur un port miroir ne les montre
pas. Donnez au moins trois explications possibles : points d'observation
différents, pertes de capture, offload ou différence de période.
Proposez le test qui permettrait de les départager.

**Exercice 4 --- RST après TLS.** Un RST suit le ClientHello. Pourquoi
n'est-il pas suffisant d'accuser le serveur ? Indiquez comment corréler
les captures et quels journaux vérifier.

**Exercice 5 --- QUIC.** Le navigateur utilise UDP/443, mais le filtre
TCP/443 ne montre rien. Est-ce une panne ? Expliquez le rôle de
HTTP/3/QUIC et les vérifications nécessaires.

**Exercice 6 --- MTU.** Les gros transferts échouent et les petits
réussissent. Quels messages ICMP/ICMPv6 recherchez-vous ? Pourquoi
faut-il examiner l'offload, les tunnels et les captures aux points
adéquats ?

**Exercice 7 --- Confidentialité.** Un collègue demande le fichier PCAP
complet pour « jeter un œil ». Quelles vérifications devez-vous faire
avant le partage ? Proposez une version minimale et sûre de la preuve.

**Exercice 8 --- Rapport.** Écrivez une conclusion de trois phrases qui
sépare un fait observé, une interprétation prudente et une prochaine
action vérifiable.

## 32. Corrigé des exercices

**Réponse 1.** L'intervalle observé entre SYN et SYN/ACK est de 240 ms.
Il ne mesure pas uniquement le temps de traitement serveur : il inclut
le chemin aller, le traitement éventuel, le chemin retour et les effets
du point de capture. Une capture au serveur et une mesure de référence
peuvent aider à décomposer le délai.

**Réponse 2.** Le délai est postérieur à la résolution DNS dans cette
chronologie, donc DNS n'explique pas directement les 1,5 seconde
observées. Il faut examiner la progression TLS, les retransmissions, la
réponse du pair, les captures multi-points et les journaux de service ou
de sécurité.

**Réponse 3.** Les captures peuvent observer des interfaces différentes,
l'une peut perdre des paquets, les horodatages peuvent différer,
l'offload peut modifier la segmentation visible, ou les fenêtres
temporelles peuvent ne pas être identiques. Une capture synchronisée à
deux points et la vérification des compteurs de capture permettent
d'avancer.

**Réponse 4.** Le RST peut être injecté par un équipement intermédiaire
ou provenir d'un proxy. Comparez les captures client et serveur,
examinez les caractéristiques du paquet et consultez les journaux du
pare-feu, du proxy et du serveur. N'attribuez pas la cause à partir de
l'adresse source seule.

**Réponse 5.** Ce n'est pas automatiquement une panne : HTTP/3 utilise
QUIC sur UDP. Il faut filtrer UDP/443, examiner les échanges QUIC
visibles et comparer le comportement avec des journaux applicatifs ou
une session de test contrôlée.

**Réponse 6.** Recherchez ICMPv4 type 3/code 4 et ICMPv6 type 2,
examinez la taille des paquets et les retransmissions, puis comparez les
points de capture. Un tunnel réduit la MTU utile ; l'offload peut rendre
les tailles locales trompeuses.

**Réponse 7.** Vérifiez l'autorisation, la finalité, les données
personnelles et les règles de conservation. Fournissez un extrait
minimal expurgé, gardez l'original protégé et ne joignez pas de secrets
TLS.

**Réponse 8.** Exemple : « La capture client montre un SYN retransmis
trois fois sans SYN/ACK visible pendant la fenêtre observée. Cela
suggère une absence de réponse sur le chemin, sans localiser
l'équipement responsable. Une capture simultanée au pare-feu et au
serveur permettra de déterminer où le SYN ou la réponse disparaît. »

## 33. Checklist opérationnelle

Avant la capture : - Définir la question et le critère de réussite. -
Confirmer l'autorisation et le périmètre. - Identifier l'interface, les
adresses, les ports et la topologie. - Noter l'heure et les conditions
de reproduction. - Choisir une durée et une taille de capture
raisonnables.

Pendant la capture : - Reproduire le symptôme une seule fois si
possible. - Noter les actions et leurs horodatages. - Vérifier que les
paquets attendus sont visibles. - Surveiller les pertes de capture et la
charge de l'outil. - Arrêter dès que la preuve nécessaire est collectée.

Après la capture : - Enregistrer l'original et protéger son accès. -
Appliquer des filtres d'affichage reproductibles. - Construire une
chronologie. - Comparer les hypothèses à des faits observables. -
Contrôler les artefacts d'offload et les limites du point de capture. -
Corréler avec les journaux système et applicatifs. - Rédiger les
conclusions et les incertitudes. - Supprimer ou archiver les données
selon la politique applicable.

Avant de clore l'incident : - Reproduire le test après correction. -
Confirmer le résultat métier. - Vérifier qu'aucun changement temporaire
ne reste actif. - Documenter le retour arrière et les enseignements.

## 34. Références et ressources officielles

-   Documentation officielle Wireshark : https://www.wireshark.org/docs/
-   Référence des filtres d'affichage :
    https://www.wireshark.org/docs/dfref/
-   Documentation TShark :
    https://www.wireshark.org/docs/man-pages/tshark.html
-   Page officielle de téléchargement Wireshark :
    https://www.wireshark.org/download.html
-   RFC 9293 --- Transmission Control Protocol :
    https://www.rfc-editor.org/rfc/rfc9293
-   RFC 8446 --- The Transport Layer Security (TLS) Protocol Version 1.3
    : https://www.rfc-editor.org/rfc/rfc8446
-   RFC 9113 --- HTTP/2 : https://www.rfc-editor.org/rfc/rfc9113
-   RFC 9114 --- HTTP/3 : https://www.rfc-editor.org/rfc/rfc9114
-   RFC 9000 --- QUIC: A UDP-Based Multiplexed and Secure Transport :
    https://www.rfc-editor.org/rfc/rfc9000
-   RFC 7766 --- DNS Transport over TCP :
    https://www.rfc-editor.org/rfc/rfc7766
-   RFC 8484 --- DNS Queries over HTTPS (DoH) :
    https://www.rfc-editor.org/rfc/rfc8484

Les menus, noms de champs et capacités de décodage peuvent varier selon
la version de Wireshark. Consultez la documentation correspondant à la
version installée et reproduisez les exercices dans un environnement de
test autorisé.

## 35. Construire des filtres composés sans se piéger

Les filtres complexes deviennent difficiles à relire quand plusieurs
conditions sont enchaînées sans parenthèses. Construisez-les
progressivement : commencez par l'adresse, ajoutez le protocole, puis le
port et enfin l'événement recherché. Après chaque ajout, vérifiez le
nombre de paquets retournés. Si le résultat tombe brutalement à zéro,
examinez la dernière condition ajoutée au lieu de supposer que
l'incident a disparu.

Exemples :

``` wireshark
(ip.addr == 192.0.2.25) && (tcp.port == 443)
(ip.src == 192.0.2.25) && (tcp.flags.syn == 1) && (tcp.flags.ack == 0)
(dns || tls.handshake) && frame.time_relative > 2
(icmp || icmpv6) && frame.len > 100
```

Le dernier exemple est illustratif : la taille de trame seule ne permet
pas d'identifier un message de diagnostic pertinent. Un filtre doit
refléter la question d'analyse et les champs réellement disponibles.
Évitez de copier un filtre trouvé en ligne sans comprendre les
opérateurs, les parenthèses et le sens de chaque champ.

Les filtres d'affichage utilisent les types de champs Wireshark, qui ne
sont pas toujours identiques aux filtres BPF de capture. Par exemple, un
champ booléen, un champ entier et un champ texte ne se comparent pas de
la même manière. Si l'expression est refusée, lisez le message d'erreur
et consultez l'autocomplétion. Une expression valide peut tout de même
être logiquement incorrecte ; testez-la sur une capture connue.

## 36. Réassembler les conversations et comprendre les limites

« Follow TCP Stream » réassemble les données observées pour une
conversation et peut afficher une vue plus lisible que les segments
individuels. Cette vue dépend toutefois des paquets présents dans la
capture. Si un segment manque, le flux réassemblé peut être incomplet.
Le réassemblage ne récupère pas magiquement les données absentes du
fichier et ne garantit pas que l'application a reçu exactement ce qui
apparaît à l'écran.

Dans les protocoles chiffrés, le réassemblage TCP peut présenter des
enregistrements TLS, mais pas le contenu HTTP sans secrets de session
appropriés. Un protocole applicatif peut aussi être multiplexé ou
compressé, ce qui rend la lecture manuelle plus difficile. Ne déduisez
pas la signification métier d'octets que vous ne pouvez pas interpréter
de manière fiable.

Les conversations peuvent être réutilisées, fermées puis rouvertes, ou
partager une même adresse et un même port dans des périodes différentes.
Pour un diagnostic, vérifiez les numéros de séquence, le début et la fin
du flux et les horodatages. Si plusieurs flux sont présents, utilisez le
numéro de flux fourni par Wireshark ou le mécanisme de suivi afin de ne
pas mélanger des connexions distinctes.

Lorsqu'un extrait est exporté, gardez le contexte autour de l'événement.
Un paquet isolé peut sembler anormal alors qu'il est une réponse
attendue à une étape antérieure. L'extrait doit contenir assez de
paquets avant et après l'événement pour expliquer la causalité.

## 37. Comprendre les ports éphémères, NAT et connexions multiples

Un client utilise généralement un port source éphémère pour établir une
connexion vers un port de service. Le port source peut changer entre les
essais et ne doit pas être utilisé seul comme identité durable d'une
application. Le NAT peut également réécrire le port source. Lorsqu'on
compare deux captures, la conversation peut donc apparaître sous des
tuples différents.

Pour corréler les flux, prenez en compte les adresses avant et après
NAT, l'heure, le service, les drapeaux TCP, les numéros de séquence et
la taille des données. Si un proxy termine la connexion, le flux
client-proxy et le flux proxy-serveur sont deux sessions TCP
indépendantes. Le proxy peut acquitter les données côté client avant que
le serveur final les ait traitées, ce qui complique l'interprétation des
délais.

Un navigateur ouvre souvent plusieurs connexions, ou utilise une seule
connexion multiplexée pour de nombreuses requêtes. Le nombre de
conversations n'est donc pas égal au nombre d'actions de l'utilisateur.
Identifiez les connexions par leur destination, leur protocole, leurs
horaires et les indices applicatifs disponibles. En HTTPS, certains
détails nécessitent les outils du navigateur ou les journaux serveur
pour être confirmés.

Ne supposez pas qu'un port non standard signifie qu'un protocole est
absent. Un service peut être déplacé sur un autre port et Wireshark peut
utiliser des heuristiques ou un décodage forcé dans un laboratoire. Le
décodage forcé doit être documenté : il modifie la manière dont les
octets sont interprétés et peut produire une analyse trompeuse si le
protocole choisi est incorrect.

## 38. Distinguer débit, latence, gigue et perte

Le débit est une quantité de données transférées par unité de temps. La
latence décrit un délai entre deux événements ; le RTT mesure un
aller-retour selon la méthode utilisée. La gigue décrit la variation des
délais entre paquets ou événements. La perte représente des données qui
n'arrivent pas à destination ou ne sont pas observées au point attendu.
Ces dimensions sont liées, mais ne sont pas interchangeables.

Un transfert de fichier peut afficher un débit moyen élevé malgré
quelques pauses. Une application vocale peut être inutilisable avec un
débit largement suffisant si la gigue ou les pertes en rafale sont
importantes. Une page Web peut sembler lente à cause du temps d'attente
avant la première réponse, même si le débit une fois le transfert lancé
est élevé. Il faut donc choisir une mesure liée au symptôme métier.

Wireshark permet d'examiner des temps, tailles et séquences, mais les
métriques disponibles dépendent du protocole et de la qualité de la
capture. Pour les appels temps réel, les analyses RTP sont pertinentes
lorsque les paquets RTP sont identifiables et décodables. Pour QUIC ou
un protocole propriétaire chiffré, les métadonnées peuvent être
insuffisantes ; complétez avec les statistiques de l'application.

Lorsqu'un rapport annonce « le réseau a 100 ms de latence », précisez
comment cette valeur a été mesurée, sur quel flux, à quel endroit, sur
quelle période et avec quelle distribution. Une moyenne seule peut
masquer les pointes. La médiane, les percentiles et les valeurs
maximales sont souvent utiles, à condition que l'échantillon soit
suffisant et représentatif.

## 39. Quand la capture elle-même devient le problème

Une capture sur un lien chargé peut perdre des paquets parce que
l'ordinateur, le buffer ou le stockage ne suit pas le débit. Vérifiez
les statistiques de capture et les messages indiquant des paquets
abandonnés par l'outil ou le système. Une capture saturée peut produire
de faux indices de perte et rendre les retransmissions impossibles à
interpréter correctement.

Réduisez le risque en choisissant le bon point de capture, en limitant
raisonnablement la durée, en utilisant un filtre de capture prudent
lorsque c'est nécessaire et en écrivant sur un stockage suffisamment
rapide. Attention : filtrer trop tôt peut exclure les messages de
contrôle utiles. Un filtre doit être décidé en fonction de l'hypothèse,
pas uniquement pour rendre le fichier petit.

Pour un trafic volumineux, utilisez la capture circulaire ou des
fichiers successifs si l'outil et la procédure le permettent. Consignez
la durée et la taille des fichiers, vérifiez qu'ils s'ouvrent
correctement et préservez les segments de temps qui précèdent
l'incident. Une capture commencée après le début du problème peut
manquer les négociations et les premières retransmissions qui expliquent
la situation.

Si la performance de l'ordinateur de capture est douteuse, répétez avec
un équipement dédié ou un TAP adapté. Comparez les compteurs de capture
et les statistiques du système. Le but est de séparer les pertes du
réseau des pertes introduites par l'observateur.

## 40. Tableau de décision rapide

  Observation       Ce qu'elle        Ce qu'elle ne     Prochaine
                    suggère           prouve pas        vérification
  ----------------- ----------------- ----------------- -----------------
  SYN sans SYN/ACK  absence de        serveur           capture autre
  visible           réponse au point  définitivement    point, route,
                    observé           hors service      pare-feu

  SYN/ACK rapide,   TCP s'établit,    application       chronologie
  puis pause        délai ultérieur   serveur seule     TLS/applicative
                                      responsable       

  Retransmissions   données non       localisation      capture
  TCP               acquittées à      exacte de la      multi-points,
                    temps             perte             compteurs

  Zero window       récepteur annonce congestion réseau processus et
                    peu ou pas de                       buffers
                    capacité                            récepteurs

  DNS lent          résolution        DNS comme unique  cache, résolveur,
                    possiblement      cause             phase suivante
                    impliquée                           

  RST après         connexion         RST généré par le capture côté
  ClientHello       réinitialisée     serveur final     serveur et
                    durant TLS                          journaux

  UDP/443 sans      possible          panne du service  décodage QUIC,
  TCP/443           QUIC/HTTP/3                         journaux client

  Checksum invalide possible artefact corruption sur le capture externe,
  sur capture       offload           fil               paramètres NIC
  locale                                                

  Gros transferts   plusieurs         PMTUD comme cause ICMP/PTB,
  figés             hypothèses dont   certaine          tailles, tunnel,
                    MTU                                 captures

  Paquets absents   trafic non        perte réelle sur  statistiques
  dans une capture  observé à cet     le chemin         capture et autre
                    endroit                             point

Ce tableau est une aide à la priorisation, pas un moteur de diagnostic
automatique. Chaque observation doit être replacée dans la chronologie
et confrontée à la topologie.

## 41. Évaluation finale et critères de maîtrise

Vous maîtrisez le niveau intermédiaire si vous pouvez analyser un
incident à partir d'une question précise, choisir un point de capture
pertinent, distinguer les filtres de capture et d'affichage, construire
une chronologie TCP, mesurer les délais avec prudence, reconnaître les
limites de TLS/QUIC et interpréter les annotations Expert Information
comme des indices.

Vous devez aussi être capable de produire une preuve reproductible. Une
autre personne doit pouvoir ouvrir le fichier, appliquer le filtre
indiqué, retrouver les numéros de trame cités et comprendre comment la
conclusion a été obtenue. Si elle ne peut pas reproduire l'observation,
le rapport manque probablement d'informations sur la version, le filtre,
la période ou le point de capture.

Enfin, vous devez savoir dire « je ne peux pas conclure avec cette
capture ». Cette réponse est une compétence, pas un échec. Elle indique
qu'il faut un autre point d'observation, une capture plus complète, un
journal serveur, une métrique applicative ou une reproduction contrôlée.
La précision du diagnostic compte davantage que la certitude affichée.

Le niveau suivant pourra approfondir les analyses multi-points,
l'automatisation de l'investigation, les protocoles chiffrés et les cas
complexes de production. Il devra s'appuyer sur ces méthodes et leurs
limites plutôt que répéter la découverte des menus de base.
