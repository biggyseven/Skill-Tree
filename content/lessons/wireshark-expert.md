<style>
.wsx-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.2rem 0;padding:.75rem;border:1px solid #26384d;border-radius:14px;background:#080d16;color:#e8eff9;box-sizing:border-box}
.wsx-diagram svg{display:block;width:100%;height:auto;max-width:100%}
.wsx-diagram .flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}
@keyframes wsxDash{to{stroke-dashoffset:-30}}
@media(prefers-reduced-motion:reduce){.wsx-diagram .flow{animation:none!important}}
</style>

# Analyse de paquets avec Wireshark — Niveau Expert

**Niveau :** Expert  
**Domaine :** ingénierie réseau, performance, protocoles chiffrés, capture à grande échelle et investigation défensive  
**Prérequis :** savoir utiliser les filtres Wireshark, suivre un flux TCP, lire une négociation TLS, interpréter les retransmissions et utiliser les statistiques de base.  
**Objectif :** conduire une analyse reproductible et techniquement défendable sur une capture complexe, différencier perte réelle et artefact d’observation, relier les symptômes aux mécanismes de transport et d’application, automatiser l’extraction d’indices et produire un rapport accompagné de preuves.

> **Cadre d’utilisation :** travaille uniquement sur des équipements, réseaux et captures que tu es autorisé à examiner. Une capture peut contenir des données personnelles, des identifiants, des cookies, des jetons, des noms internes ou des contenus métier. La décryption TLS n’est à utiliser qu’avec l’autorisation appropriée et des secrets obtenus légitimement. Protège les PCAP, les fichiers de secrets et les exports comme des données sensibles.

## Parcours du cours

1. Méthode expert et limites de la preuve.
2. Concevoir une capture robuste et mesurer la perte de capture.
3. Reconstituer les conversations et corréler plusieurs points d’observation.
4. Diagnostiquer TCP : séquence, RTT, retransmission, fenêtre et congestion.
5. Distinguer les problèmes de transport, de chemin réseau et d’application.
6. Analyser TLS, HTTP/2, QUIC et HTTP/3 sans confondre visibilité et déchiffrement.
7. Traiter DNS, MTU, IPv6, NAT et chemins asymétriques.
8. Automatiser les recherches avec TShark et les outils de la suite Wireshark.
9. Utiliser les statistiques et construire un rapport d’incident reproductible.
10. Réaliser trois ateliers d’investigation avec corrigés et critères de conclusion.

## 1. La posture de l’analyste expert

À un niveau avancé, le but n’est pas de « regarder tous les paquets ». Il s’agit de tester une hypothèse avec le minimum de biais possible. Un paquet est une observation située : il est vu à un endroit, à un instant, après certaines opérations effectuées par le système d’exploitation, le pilote, la carte réseau, le commutateur ou un équipement intermédiaire.

### 1.1 Séparer observation, interprétation et conclusion

Une bonne note distingue toujours trois catégories :

- **Observation directe :** « le client a émis trois SYN à destination de `198.51.100.30:443` ; aucun SYN-ACK n’apparaît dans cette capture ».
- **Interprétation :** « l’établissement TCP n’est pas visible comme réussi au point client ».
- **Hypothèses à vérifier :** « service indisponible, filtrage, route de retour défaillante, capture incomplète ou mauvais point d’observation ».

Ne transforme pas une étiquette du panneau Expert en verdict automatique. Une retransmission identifiée par Wireshark indique un motif compatible avec une retransmission dans la séquence observée ; elle ne prouve pas à elle seule que le réseau physique a perdu le paquet. De même, « Previous segment not captured » peut provenir d’un début de capture tardif, d’une perte au point de capture, d’un paquet absent du fichier, ou d’un réel trou dans la séquence observée.

### 1.2 Le modèle causal en couches

Pour une application lente, examine les causes possibles dans un ordre qui permet de les distinguer :

1. **Application :** temps de calcul, file interne, base de données, limite de concurrence, attente d’une dépendance.
2. **Transport :** handshake, retransmission, fenêtre de réception, congestion, réinitialisation et fermeture.
3. **Réseau :** chemin aller/retour, routage asymétrique, MTU, fragmentation, ACL, NAT et équilibrage.
4. **Accès et capture :** Wi-Fi, duplex, erreurs d’interface, offload, buffers et pertes au collecteur.
5. **Mesure :** horloge, précision du timestamp, filtre de capture trop restrictif, troncature du paquet ou fichier incomplet.

Cette liste n’est pas une règle selon laquelle il faut systématiquement diagnostiquer la couche basse en premier. C’est une grille pour ne pas attribuer trop vite la cause à la première alerte visible.

### Schéma 1 — Une conclusion fiable corrèle plusieurs observations

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" role="img" aria-label="Trois points de capture côté client, réseau et serveur alimentent une comparaison temporelle. La corrélation aide à localiser une différence sans attribuer automatiquement la cause."><defs><marker id="wsx1a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker><marker id="wsx1b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#76e5ab"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.5;marker-end:url(#wsx1a)}.b{fill:none;stroke:#76e5ab;stroke-width:2.5;marker-end:url(#wsx1b)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="30" y="45" width="180" height="92" rx="12" fill="#142b42" stroke="#69d9ff" stroke-width="2"/><text x="120" y="73" class="t">Client</text><text x="120" y="95" class="s">Capture A</text><text x="120" y="115" class="s">Ce qui est envoyé</text><rect x="360" y="45" width="180" height="92" rx="12" fill="#322a1b" stroke="#ffca72" stroke-width="2"/><text x="450" y="73" class="t">Point réseau</text><text x="450" y="95" class="s">Capture B</text><text x="450" y="115" class="s">Ce qui traverse</text><rect x="690" y="45" width="180" height="92" rx="12" fill="#16372d" stroke="#76e5ab" stroke-width="2"/><text x="780" y="73" class="t">Serveur</text><text x="780" y="95" class="s">Capture C</text><text x="780" y="115" class="s">Ce qui arrive</text><path d="M210 76H355" class="a flow"/><path d="M540 76H685" class="a flow"/><path d="M690 112H545" class="b"/><path d="M360 112H215" class="b"/><rect x="75" y="205" width="750" height="90" rx="12" fill="#101b29" stroke="#334961"/><text x="450" y="230" class="t">Corrélation et preuve</text><text x="450" y="254" class="s">Timestamp · tuple IP/ports/protocole · SEQ/ACK · identifiants applicatifs</text><text x="450" y="275" class="s">Comparer les différences localise une zone de recherche ; les journaux et compteurs établissent la cause.</text><path d="M120 137V195" stroke="#6d8aaa" stroke-width="1.5" stroke-dasharray="4 5" fill="none"/><path d="M450 137V195" stroke="#6d8aaa" stroke-width="1.5" stroke-dasharray="4 5" fill="none"/><path d="M780 137V195" stroke="#6d8aaa" stroke-width="1.5" stroke-dasharray="4 5" fill="none"/></svg></div>

### 1.3 Construire un arbre d’hypothèses

Pour une page HTTPS qui « tourne longtemps », on peut poser ces branches :

- le DNS prend-il du temps avant que l’adresse soit connue ?
- le handshake TCP est-il retardé ou répété ?
- le handshake TLS progresse-t-il jusqu’aux messages attendus ?
- la requête applicative est-elle envoyée immédiatement après la connexion ?
- la réponse du serveur arrive-t-elle tard, ou arrive-t-elle en temps utile mais le client la consomme-t-il lentement ?
- existe-t-il des flux parallèles, une redirection, un proxy, du QUIC/HTTP/3, ou une connexion réutilisée qui rend le chemin différent de ce que l’on suppose ?

Une capture ne montre pas toujours l’événement initial. Le navigateur peut avoir résolu le nom plus tôt, réutiliser une connexion ou utiliser une autre interface. Noter le contexte de reproduction reste essentiel.

## 2. Concevoir une capture fiable

### 2.1 Choisir le point d’observation

Les principaux points ont des avantages et des limites :

| Point | Ce qu’il montre bien | Risques d’interprétation |
|---|---|---|
| Client | émission applicative, interfaces locales, erreurs visibles au poste | offload, trafic VPN encapsulé, chemin effectif différent après le poste |
| Serveur | requêtes reçues, réponses produites, pression du serveur | ne voit pas nécessairement ce qui est arrivé avant lui ou ce qui est perdu au retour |
| SPAN/mirror | trafic sélectionné sur un switch | miroir saturé, sens mal configuré, oversubscription du port de destination |
| TAP réseau | observations dédiées sur le lien concerné | placement et capacité du TAP, visibilité limitée à ce lien |
| Pare-feu/NAT | traduction, décision de filtrage, sessions | l’interface, la direction et le point avant/après NAT doivent être connus |
| Hôte virtualisé/conteneur | interface virtuelle et trafic local | ponts, veth, overlay, offload et duplication possible entre points |

La capture sur une carte en mode promiscuité ne garantit pas la visibilité des communications unicast d’autres machines sur un réseau commuté. Il faut un SPAN, un TAP ou un point terminal autorisé. Pour un tunnel VPN, une capture avant chiffrement et une capture sur l’interface physique ne montrent pas les mêmes couches.

### 2.2 Mesurer la perte au point de capture

Un fichier incomplet peut fabriquer des symptômes qui ressemblent à de la perte réseau. Pendant une capture, relève si possible :

- les paquets reçus par le mécanisme de capture ;
- les paquets abandonnés par le noyau ou la bibliothèque de capture ;
- les limites du buffer et du collecteur ;
- le nombre de paquets réellement écrits dans le fichier ;
- l’utilisation CPU, l’activité disque et le débit du lien ;
- la présence de limites de taille/snapshot length ou de filtres actifs.

Les compteurs exacts varient selon le système, le pilote, la méthode de capture et la version. Une capture distante, un TAP ou un SPAN peut perdre des paquets sans que ce soit visible comme une perte du trafic applicatif. Conserve le rapport de fin de capture et les paramètres qui ont servi à la collecter.

### 2.3 Capture circulaire et collecte bornée

Sur des liens à débit élevé, éviter de conserver indéfiniment un fichier gigantesque. Le mode de fichiers circulaires peut garder une fenêtre d’historique limitée, en faisant tourner plusieurs fichiers par durée ou par taille. Choisis une durée assez large pour inclure le contexte qui précède et suit l’incident ; sinon, les premiers paquets nécessaires à l’interprétation peuvent avoir été écrasés.

Avec `dumpcap`, par exemple, la syntaxe précise des options dépend de la version. Vérifie `dumpcap -h` sur la machine cible. Une collecte de laboratoire typique peut s’effectuer sur une interface choisie, avec des fichiers limités et un filtre réduit uniquement lorsque les protocoles attendus sont connus.

### 2.4 Snapshot length, troncature et taille des paquets

La longueur de capture détermine combien d’octets de chaque paquet sont conservés. Une troncature diminue le volume mais peut empêcher la reconstruction TCP, l’analyse d’un certificat ou l’interprétation d’un protocole applicatif. Elle n’est pas toujours visible si l’analyste ne vérifie pas les indicateurs de longueur capturée et de longueur sur le fil. Pour un diagnostic approfondi, conserve les paquets complets lorsque les autorisations, la capacité de stockage et la politique de confidentialité le permettent.

### 2.5 Les horloges sont une mesure, pas une vérité absolue

Pour comparer deux captures, synchronise les horloges quand c’est possible et note la source de temps. NTP/chrony ou une source équivalente réduit généralement la dérive, mais un timestamp matériel ou logiciel peut encore être placé à un stade différent du chemin. Si deux captures affichent un écart de 5 ms, ne conclus pas à un délai réseau de 5 ms tant que tu n’as pas vérifié la synchronisation, le point d’horodatage et la précision des deux horloges.

### Schéma 2 — Une collecte de qualité conserve aussi sa propre métrologie

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Pipeline de collecte avec trafic, interface de capture, buffers, écriture PCAPNG et contrôle de qualité des pertes, timestamps et troncature."><defs><marker id="wsx2a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker><marker id="wsx2b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#7ee6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b7c8dc;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.5;marker-end:url(#wsx2a)}.b{fill:none;stroke:#7ee6b0;stroke-width:2.3;marker-end:url(#wsx2b)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="25" y="55" width="150" height="78" rx="10" fill="#142b42" stroke="#69d9ff"/><text x="100" y="84" class="t">Trafic</text><text x="100" y="105" class="s">Sur le lien</text><rect x="220" y="55" width="150" height="78" rx="10" fill="#1b2635" stroke="#8ba8c8"/><text x="295" y="84" class="t">NIC / SPAN</text><text x="295" y="105" class="s">Point observé</text><rect x="415" y="55" width="150" height="78" rx="10" fill="#342a1a" stroke="#ffca72"/><text x="490" y="84" class="t">Buffer</text><text x="490" y="105" class="s">Drops possibles</text><rect x="610" y="55" width="260" height="78" rx="10" fill="#16372d" stroke="#7ee6b0"/><text x="740" y="84" class="t">PCAPNG + métadonnées</text><text x="740" y="105" class="s">Interface · temps · filtres · compteurs</text><path d="M175 94H215" class="a flow"/><path d="M370 94H410" class="a flow"/><path d="M565 94H605" class="a flow"/><rect x="80" y="200" width="740" height="80" rx="12" fill="#101b29" stroke="#344961"/><text x="450" y="225" class="t">Contrôle qualité obligatoire</text><text x="450" y="247" class="s">Drops de capture · taille tronquée · timestamps · filtre de capture · stockage</text><text x="450" y="266" class="s">Si la collecte est incomplète, documenter la limite avant d’interpréter les trous dans les flux.</text><path d="M490 133V190" class="b"/><path d="M740 133V190" class="b"/></svg></div>

### 2.6 Offload, GRO, LRO, TSO et paquets « anormaux »

Une capture effectuée localement peut montrer des paquets avant certaines opérations de carte réseau. Les mécanismes d’offload de checksum peuvent laisser apparaître une somme de contrôle sortante comme incorrecte ou partielle, alors que la carte la calcule avant émission. TSO/GSO peuvent présenter une grande unité avant segmentation ; GRO/LRO peuvent regrouper des paquets reçus avant qu’ils soient remis aux couches supérieures. L’affichage ne correspond alors pas nécessairement un à un aux trames réellement présentes sur le câble.

Méthode :

1. vérifie si l’alerte concerne un paquet localement émis ;
2. compare avec une capture distante ou sur le fil ;
3. consulte les options d’offload du pilote et du système ;
4. évite de désactiver l’offload sur un système de production sans fenêtre de changement ni justification ;
5. documente la méthode de capture et son effet potentiel.

### 2.7 Préserver l’intégrité et les données sensibles

Pour un dossier d’incident, conserve l’original en lecture seule, calcule une empreinte cryptographique (par exemple SHA-256), travaille sur une copie et consigne les filtres appliqués. N’exporte pas de charges utiles ni de secrets dans un rapport de routine. Si la capture doit être partagée, vérifie l’approche de minimisation : fichier filtré, paquet anonymisé, échantillon, ou notes structurées. L’anonymisation peut elle-même altérer les sommes, les longueurs, la topologie ou les identifiants ; marque explicitement les transformations.

## 3. Reconstituer un flux et corréler plusieurs captures

### 3.1 Identifier correctement une conversation

Le tuple classique d’un flux TCP ou UDP comporte protocole, IP source, port source, IP destination et port destination. Il faut aussi tenir compte de l’interface, du VLAN, de la direction et du contexte NAT si plusieurs segments sont comparés. Les ports peuvent être réutilisés dans le temps ; un simple couple IP/port peut donc mélanger des conversations différentes si les captures sont concaténées ou si les temps sont espacés.

Utilise **Follow TCP Stream** ou les statistiques Conversations comme outils de navigation, pas comme preuve autonome que le flux a été observé dans son intégralité. Le numéro `tcp.stream` est attribué dans le contexte d’une capture ; il n’est pas un identifiant universel permettant de corréler deux fichiers indépendants.

### 3.2 Comparer avant et après NAT

Un NAT peut changer l’adresse et le port source ; un proxy L7 termine une connexion et en crée une autre. Dans les deux cas, le flux côté client et le flux côté serveur ne partagent pas nécessairement le même tuple TCP, les mêmes numéros de séquence, ni la même négociation TLS. Corrèle via une combinaison d’horodatage, de volume, de séquences requête/réponse, de journal de session NAT et de données de l’équipement intermédiaire. Ne suppose pas qu’un proxy est un simple câble transparent.

### 3.3 Corrélation temporelle sans mélanger les horloges

Si deux fichiers sont alignés, assure-toi que les événements comparés appartiennent à la même requête. Les nombres de séquence TCP ne s’alignent pas nécessairement après un proxy, et les heures peuvent être décalées. Des marqueurs applicatifs, IDs de requête, identifiants DNS, taille de réponse et caractéristiques de burst peuvent aider. Pour un diagnostic de perte, la preuve la plus utile est souvent : paquet vu au point A, paquet correspondant absent à B, compteurs de capture fiables, et observations de part et d’autre du segment.

### Schéma 3 — Corréler n’est pas comparer uniquement les numéros de paquet

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Deux captures indépendantes à gauche et à droite sont reliées via des clés de corrélation comme heure corrigée, identifiant applicatif, tuple IP et journaux NAT, pas par le numéro local du paquet."><defs><marker id="wsx3a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#edf5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b8c8db;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.3;marker-end:url(#wsx3a)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="35" y="35" width="235" height="100" rx="12" fill="#142b42" stroke="#69d9ff" stroke-width="2"/><text x="152" y="61" class="t">Capture A · client</text><text x="152" y="84" class="s">Packet 104, seq 1001</text><text x="152" y="104" class="s">IP/port privés</text><rect x="630" y="35" width="235" height="100" rx="12" fill="#16372d" stroke="#7ee6b0" stroke-width="2"/><text x="747" y="61" class="t">Capture B · serveur</text><text x="747" y="84" class="s">Packet 59, séquence différente</text><text x="747" y="104" class="s">Adresse possiblement NATée</text><rect x="300" y="175" width="300" height="110" rx="12" fill="#20283a" stroke="#c1a4ff" stroke-width="2"/><text x="450" y="202" class="t">Clés de corrélation</text><text x="450" y="224" class="s">ID de requête · contenu autorisé</text><text x="450" y="244" class="s">temps aligné · journal NAT/proxy</text><text x="450" y="264" class="s">volumes et ordre des événements</text><path d="M152 135L335 170" class="a flow"/><path d="M747 135L565 170" class="a flow"/><text x="450" y="310" class="s">Le numéro de trame et le numéro tcp.stream sont locaux au fichier.</text></svg></div>

### 3.4 Comprendre les séquences et la réassemblage TCP

Le numéro de séquence TCP représente une position dans le flux d’octets, pas un numéro de paquet. Un segment portant `SEQ=5001` avec 1 000 octets de données couvre les octets 5001 à 6000 ; l’ACK cumulatif `ACK=6001` signifie que le récepteur attend ensuite l’octet 6001. SYN et FIN consomment chacun un numéro de séquence. Les SACK peuvent préciser d’autres plages reçues, sans remplacer la signification de l’ACK cumulatif.

Un flux réassemblé peut dépendre des données disponibles dans les deux directions, de l’ordre des paquets, des paramètres de réassemblage et du fait que le captureur ait commencé suffisamment tôt. Un flux visible en texte n’implique pas que toutes les données intermédiaires soient présentes ou que le protocole applicatif soit complet. Sur un protocole chiffré, l’outil ne révèle le contenu applicatif que si les secrets et les mécanismes requis sont disponibles.

## 4. Expertise TCP : diagnostic par mécanisme

### 4.1 Le handshake et les délais d’établissement

Pour une connexion TCP simple, le handshake comporte généralement SYN, SYN-ACK puis ACK. Mesure séparément :

- **délai SYN → SYN-ACK :** inclut le chemin aller, le traitement côté service et le chemin retour ; il n’est pas forcément égal au RTT mesuré par un ping ;
- **délai SYN-ACK → ACK :** dépend du client, du scheduling et du chemin retour ; un ACK retardé ou perdu peut brouiller la lecture ;
- **délai handshake → première donnée applicative :** révèle parfois une attente cliente, un échange TLS ou un délai de traitement en amont.

Un SYN répété peut signaler l’absence de réponse dans la fenêtre d’attente, mais vérifie le point de capture, l’adresse après NAT, une éventuelle asymétrie et la présence d’un pare-feu silencieux. Un RST est une réponse active de réinitialisation ; son origine apparente dans les adresses ne suffit pas à dire quel équipement l’a généré si des middleboxes peuvent forger ou injecter des réponses.

### 4.2 Lire correctement l’ACK et la retransmission

Filtres d’affichage utiles, à vérifier dans la référence de la version installée :

| Recherche | Filtre |
|---|---|
| Flux TCP numéro 12 | `tcp.stream == 12` |
| Retransmissions repérées | `tcp.analysis.retransmission` |
| Retransmission rapide suspectée | `tcp.analysis.fast_retransmission` |
| ACK dupliqués | `tcp.analysis.duplicate_ack` |
| Segment hors ordre soupçonné | `tcp.analysis.out_of_order` |
| Segment précédent absent de capture | `tcp.analysis.lost_segment` |
| RTO/expiration de temporisation observée | `tcp.analysis.rto` |
| Fenêtre annoncée nulle | `tcp.analysis.zero_window` |
| Paquet SYN sans ACK | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |

Les labels Wireshark sont des déductions faites à partir de la trace et de l’état de l’analyseur. Le réordonnancement réseau peut faire apparaître un segment comme suspect avant que les segments suivants n’arrivent dans le fichier. Le démarrage tardif, la perte à la capture, le multi-chemin, les paquets dupliqués et les captures concaténées compliquent l’interprétation. N’utilise donc pas « retransmission détectée » comme synonyme automatique de « perte sur le lien X ».

### Schéma 4 — Motif compatible avec une perte et retransmission rapide

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 365" role="img" aria-label="Échange TCP illustrant la livraison de segments 1000, 2000 puis 3000 avec un trou pour le segment 2000. Des ACK cumulatifs répétés demandent la séquence manquante avant retransmission, puis l’ACK avance."><defs><marker id="wsx4a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker><marker id="wsx4b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ffca72"/></marker><marker id="wsx4c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#7ee6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#edf5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b8c8db;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.4;marker-end:url(#wsx4a)}.b{fill:none;stroke:#ffca72;stroke-width:2.4;marker-end:url(#wsx4b)}.c{fill:none;stroke:#7ee6b0;stroke-width:2.4;marker-end:url(#wsx4c)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><text x="210" y="29" class="t">Émetteur</text><text x="690" y="29" class="t">Récepteur</text><path d="M210 43V335" stroke="#54708d" stroke-width="1.5" stroke-dasharray="4 6"/><path d="M690 43V335" stroke="#54708d" stroke-width="1.5" stroke-dasharray="4 6"/><path d="M220 72H680" class="a flow"/><text x="450" y="63" class="s">SEQ 1000 — données livrées</text><path d="M680 112H220" class="c"/><text x="450" y="103" class="s">ACK 2000 — prochain octet attendu</text><path d="M220 150H540" class="b flow"/><path d="M548 140L564 160M564 140L548 160" stroke="#ff6b78" stroke-width="4" stroke-linecap="round"/><text x="450" y="141" class="s">SEQ 2000 — segment perdu / absent à l’observation</text><path d="M220 188H680" class="a flow"/><text x="450" y="179" class="s">SEQ 3000 — segment suivant atteint le récepteur</text><path d="M680 222H220" class="b"/><text x="450" y="213" class="s">ACK 2000 — ACK cumulatif répété</text><path d="M680 256H220" class="b"/><text x="450" y="247" class="s">ACK 2000 — autre ACK répété</text><path d="M220 290H680" class="c flow"/><text x="450" y="281" class="s">Retransmission SEQ 2000</text><path d="M680 324H220" class="c"/><text x="450" y="315" class="s">ACK progresse vers 4000 (si plage contiguë reçue)</text></svg></div>

Le schéma représente un scénario simplifié. Le nombre d’ACK répétés, l’emploi de SACK, les algorithmes de congestion et le seuil de retransmission varient selon l’implémentation et le contexte. La séquence est compatible avec une perte, mais le même motif à un point de capture peut être influencé par un mauvais point d’observation ou du réordonnancement.

### 4.3 Retransmission rapide, RTO, spurious et réordonnancement

Une retransmission rapide survient typiquement lorsqu’un expéditeur reçoit suffisamment d’indices de données manquantes sans attendre l’expiration du temporisateur. Une retransmission RTO survient après temporisation. Une retransmission dite *spurious* est une retransmission qui peut avoir été déclenchée alors que les données correspondantes étaient déjà arrivées ; cela peut se produire notamment lorsque les ACK sont retardés ou que le réseau réordonne les segments.

Analyse recommandée :

1. active les colonnes `tcp.seq`, `tcp.ack`, `tcp.len`, `tcp.analysis.ack_rtt` et `tcp.window_size` ;
2. suis le même flux dans les deux directions ;
3. trouve la plage d’octets et les ACK répétés associés ;
4. compare temps inter-paquets, SACK éventuels et numéros de séquence ;
5. vérifie si le même motif apparaît dans une capture au récepteur ;
6. sépare la preuve d’un trou observable de l’hypothèse sur son origine.

### 4.4 RTT et délai ACK : ce que mesure la capture

Le champ `tcp.analysis.ack_rtt` estime le délai entre un segment et l’ACK correspondant dans la trace. La mesure dépend de ce qui a été capturé, de l’ambiguïté d’ACK, de la direction visible et des règles de l’analyseur. Ce n’est pas nécessairement le même que le RTT de l’application ou celui d’une sonde ICMP. Une valeur qui change peut indiquer une variabilité de chemin, un délai de traitement, un ACK retardé ou simplement une différence dans le point de capture.

Un RTT stable mais élevé peut allonger la durée nécessaire à la montée du débit, surtout si la fenêtre de données en vol est limitée. Un RTT variable et une perte probable peuvent déclencher des diminutions de débit, mais l’analyse doit rester fondée sur les données et idéalement être corrélée avec les statistiques de l’interface, de la congestion et du serveur.

### 4.5 Fenêtre de réception, fenêtre zéro et backpressure

La fenêtre annoncée dans TCP indique la quantité de données que le récepteur est prêt à accepter, après application éventuelle du facteur d’échelle négocié. Une **fenêtre zéro** signifie que le récepteur demande temporairement à l’émetteur de cesser d’envoyer des données nouvelles. Elle peut être liée à une application qui ne lit pas assez vite le socket, à une pression mémoire, à une limitation du service ou à une pause interne. Ce n’est pas d’abord une preuve de congestion du réseau.

Pour différencier :

- observe quel côté annonce la fenêtre nulle ;
- regarde combien de temps elle persiste ;
- vérifie le rythme de lecture et la reprise via mises à jour de fenêtre ;
- cherche les sondes de fenêtre nulle et les ACK associés ;
- corrèle les événements à l’utilisation CPU/mémoire et aux files applicatives du récepteur.

### 4.6 Débit, congestion et fenêtre en vol

Le débit soutenu est contraint par plusieurs facteurs : capacité du lien, RTT, fenêtre de congestion de l’émetteur, fenêtre de réception, pertes, pacing, files d’attente et comportement applicatif. Une approximation utile pour comprendre la fenêtre est le produit bande passante-délai (BDP) :

\[
\text{BDP (bits)} = \text{débit cible (bits/s)} \times \text{RTT (s)}
\]

Exemple : un chemin de 1 Gbit/s et 40 ms de RTT a un BDP d’environ 40 Mbits, soit 5 Mo. Pour saturer le chemin sans pertes ni autres limites, il faut pouvoir maintenir suffisamment de données en vol. Ce calcul est une intuition de dimensionnement, pas une prédiction exacte du débit d’un flux.

Une capture seule ne montre pas toujours directement la fenêtre de congestion interne de l’émetteur. Elle permet de voir des indices — fenêtres annoncées, ACK, pertes suspectées, pacing, bursts — mais une analyse rigoureuse peut nécessiter les compteurs de l’hôte, les traces noyau ou les métriques de transport de l’application.

### 4.7 ACK retardés, ACK compression et effets de capture

Un ACK n’est pas nécessairement envoyé un par segment : les piles peuvent retarder ou regrouper des ACK dans certaines limites. L’ACK compression peut rendre des ACK qui devraient être espacés visibles en rafale, ce qui peut influencer la cadence de l’émetteur et l’interprétation des graphiques. Un SPAN surchargé ou une capture logicielle peut aussi modifier les intervalles apparents. Avant de tirer une conclusion sur le pacing, vérifie le lieu de capture, les timestamps et les compteurs de pertes.

### 4.8 Événements de fermeture et RST

FIN/ACK est une fermeture ordonnée de chaque direction TCP ; un FIN n’indique pas nécessairement que les deux sens s’arrêtent au même instant. RST réinitialise la connexion. Des RST peuvent venir de l’application, du système, d’un pare-feu, d’un proxy ou d’un dispositif de sécurité. Compare la capture à proximité de chaque extrémité et les journaux du service avant de nommer l’émetteur réel. Un segment tardif après la fermeture, une réutilisation de tuple ou des données observées en double peuvent également compliquer la chronologie.

## 5. Déduire la cause d’une lenteur sans surinterpréter

### 5.1 Décomposer le temps d’une transaction

Pour une transaction comportant DNS, TCP, TLS et HTTP, on peut mesurer séparément :

- temps de résolution DNS visible ;
- délai d’établissement TCP ;
- durée de la négociation TLS ;
- délai entre fin de négociation et première requête ;
- temps entre requête et premier octet de réponse ;
- durée de réception du corps ;
- délai de traitement client après réception.

Ces composantes ne sont pas toujours toutes visibles. Une connexion peut être réutilisée ; DNS peut venir du cache ; une requête peut emprunter HTTP/3 sur QUIC ; le contenu peut être servi depuis un cache ou un proxy ; le navigateur peut démarrer plusieurs connexions en parallèle. Marque les intervalles réellement mesurables et évite de reconstituer une chronologie qui n’est pas présente dans le fichier.

### 5.2 Distinguer « serveur lent » d’un chemin lent

Un délai requête-réponse mesuré entre client et serveur contient le temps de traitement de l’application ainsi que les temps aller-retour, les files d’attente et les opérations intermédiaires. Pour attribuer un délai à l’application, cherche une capture côté serveur : instant de réception de la requête, instant d’émission de la réponse, et journaux de traitement. Si la requête arrive rapidement mais que la réponse n’est générée que bien plus tard, l’attente se trouve probablement après l’arrivée au serveur ; encore faut-il corréler les horloges et tenir compte du buffering ou du proxy.

### Schéma 5 — Décomposer le temps d’une requête

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 355" role="img" aria-label="Chronologie simplifiée d'une transaction DNS, TCP, TLS, requête et réponse HTTP, avec les intervalles à mesurer plutôt que d'attribuer tout le délai au serveur."><defs><marker id="wsx5a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker><marker id="wsx5b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#7ee6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#edf5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b8c8dc;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.3;marker-end:url(#wsx5a)}.b{fill:none;stroke:#7ee6b0;stroke-width:2.3;marker-end:url(#wsx5b)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><text x="130" y="30" class="t">Client</text><text x="770" y="30" class="t">Serveur</text><path d="M130 45V330M770 45V330" stroke="#54708d" stroke-width="1.5" stroke-dasharray="4 6"/><path d="M140 72H760" class="a flow"/><text x="450" y="63" class="s">DNS éventuel</text><path d="M140 111H760" class="a flow"/><text x="450" y="102" class="s">SYN</text><path d="M760 148H140" class="b"/><text x="450" y="139" class="s">SYN-ACK</text><path d="M140 178H760" class="a"/><text x="450" y="169" class="s">ACK puis négociation TLS</text><path d="M140 218H760" class="a flow"/><text x="450" y="209" class="s">Requête applicative</text><path d="M760 268H140" class="b flow"/><text x="450" y="250" class="s">Réponse / premier octet / corps</text><rect x="255" y="295" width="390" height="35" rx="8" fill="#332a1b" stroke="#ffca72"/><text x="450" y="317" class="s">Mesurer chaque segment de temps séparément</text></svg></div>

### 5.3 Graphiques et statistiques utiles

- **I/O Graphs :** débit ou nombre de paquets par intervalle, selon un filtre ; utile pour repérer les silences, rafales ou baisses.
- **TCP Stream Graphs :** chronologie des séquences, RTT ou débit selon le graphique disponible ; utile pour voir des trous, plateaux et reprises.
- **Conversations / Endpoints :** top des pairs, volumes et durée d’activité.
- **Protocol Hierarchy :** répartition des protocoles dans la capture, en gardant à l’esprit que le chiffrement masque des sous-protocoles.
- **Expert Information :** point d’entrée pour trier des motifs suspects, jamais remplacement de l’analyse chronologique.
- **Capture File Properties :** interfaces, durée, paquets, commentaires, limites et informations de collecte disponibles dans le fichier.

Avant de partager un graphique, préciser la période, les unités, le filtre et si la valeur provient de paquets, d’octets sur le fil ou de données réassemblées. Les graphes de débit peuvent différer suivant l’intervalle et le traitement des paquets groupés.

## 6. TLS, HTTP/2, QUIC et HTTP/3

### 6.1 Comprendre le niveau de visibilité

TLS protège la confidentialité et l’intégrité des données applicatives, tout en laissant apparaître certaines métadonnées selon le protocole, sa version, le ClientHello, les extensions négociées et la présence de mécanismes comme ECH. Dans une capture, on peut souvent identifier les IP/ports, des durées, des tailles, certains messages de handshake et des alertes visibles. Cela ne signifie pas que l’analyste peut lire les URL complètes, les en-têtes HTTP ou les corps chiffrés.

Avec TLS 1.3, le contenu de plusieurs messages du handshake devient chiffré après ServerHello. La disponibilité et la visibilité de SNI ou d’autres métadonnées dépendent des extensions et du chemin réellement suivi. Ne promets donc pas qu’un champ sera toujours visible dans toutes les captures.

### 6.2 Déchiffrer TLS dans un laboratoire autorisé

Wireshark peut déchiffrer les sessions lorsqu’on lui fournit les secrets de session appropriés. Le mécanisme du **key log file** est généralement le moyen le plus flexible, y compris pour des échanges utilisant (EC)DHE. Une clé privée RSA de serveur ne fonctionne que dans des scénarios anciens et restreints : par exemple, elle ne déchiffre pas les sessions TLS 1.3 et ne fonctionne pas lorsque l’échange de clés ne permet pas la récupération attendue.

Procédure de laboratoire :

1. utilise une machine cliente et un service de test dont tu contrôles l’accès ;
2. active la production de secrets de session côté client avec le mécanisme supporté par l’application ;
3. protège le fichier de secrets et évite de le joindre à un rapport non protégé ;
4. configure le chemin du key log dans les préférences du protocole TLS de Wireshark ;
5. capture le handshake et le trafic applicatif correspondant ;
6. active la réassemblage TCP si nécessaire et vérifie que la capture contient tous les segments ;
7. compare la vue déchiffrée avec la requête/réponse de l’application de test ;
8. supprime ou archive les secrets selon la politique définie après le laboratoire.

Le key log permet de lire le contenu des sessions correspondantes. Il constitue donc un secret sensible, même s’il ne s’agit pas d’une clé privée serveur réutilisable. N’essaie pas de contourner le chiffrement d’un tiers : l’obtention et l’utilisation de secrets doivent être explicitement autorisées.

### Schéma 6 — Le déchiffrement dépend des secrets de la session

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 335" role="img" aria-label="Une capture TLS contient des enregistrements chiffrés. Un fichier de secrets de session obtenu depuis un client de laboratoire autorisé permet à Wireshark de déchiffrer certaines sessions correspondantes, pas toutes les captures arbitraires."><defs><marker id="wsx6a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker><marker id="wsx6b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#7ee6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#edf5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b8c8dc;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.4;marker-end:url(#wsx6a)}.b{fill:none;stroke:#7ee6b0;stroke-width:2.4;marker-end:url(#wsx6b)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="35" y="45" width="245" height="80" rx="12" fill="#142b42" stroke="#69d9ff"/><text x="157" y="73" class="t">Capture réseau</text><text x="157" y="96" class="s">Records TLS chiffrés</text><rect x="330" y="45" width="245" height="80" rx="12" fill="#322a1b" stroke="#ffca72"/><text x="452" y="73" class="t">Wireshark</text><text x="452" y="96" class="s">Dissecteur TLS</text><rect x="625" y="45" width="240" height="80" rx="12" fill="#16372d" stroke="#7ee6b0"/><text x="745" y="73" class="t">Vue lisible</text><text x="745" y="96" class="s">Uniquement si secrets adaptés</text><path d="M280 85H325" class="a flow"/><path d="M575 85H620" class="b flow"/><rect x="290" y="190" width="320" height="85" rx="12" fill="#20283a" stroke="#c1a4ff"/><text x="450" y="217" class="t">Key log file</text><text x="450" y="239" class="s">Secrets de session générés</text><text x="450" y="258" class="s">par une application autorisée</text><path d="M450 190V132" class="b"/><text x="450" y="315" class="s">Une capture seule ne contient généralement pas les secrets nécessaires.</text></svg></div>

### 6.3 Lire le handshake et les alertes TLS

Dans les versions de TLS récentes, repère le ClientHello, les versions et suites proposées, les extensions, le ServerHello, puis les messages chiffrés ou visibles selon la version et les secrets. Pour analyser un échec :

- le ClientHello est-il capturé entièrement ?
- une réponse serveur arrive-t-elle ?
- existe-t-il une alerte TLS visible et dans quel sens ?
- le handshake se bloque-t-il après un message précis ?
- le client envoie-t-il un RST ou ferme-t-il la connexion ?
- la capture démarre-t-elle au milieu d’une session déjà établie ?
- un proxy termine-t-il TLS et ouvre-t-il une seconde session ?

Une alerte TLS n’explique pas toujours la cause racine. Par exemple, une alerte liée à un certificat peut dépendre de la confiance, du nom, de la date, d’un certificat intermédiaire manquant ou d’une politique client. Le message d’alerte, les journaux de l’application et le contexte PKI doivent être rapprochés.

### 6.4 HTTP/2 : multiplexage et temps de service

HTTP/2 transporte plusieurs flux logiques au sein d’une seule connexion TCP/TLS. Les trames de plusieurs requêtes peuvent donc s’entrelacer. Un retard TCP qui affecte un segment peut bloquer la remise en ordre du flux d’octets et retarder plusieurs flux HTTP/2, même si certaines trames des autres flux ont été reçues. Ce phénomène est lié au transport TCP ordonné et ne signifie pas qu’une seule requête applicative a été lente.

Pour diagnostiquer HTTP/2 :

1. identifie la connexion et vérifie si plusieurs streams sont actifs ;
2. en laboratoire, déchiffre la session si le contenu détaillé est indispensable ;
3. regarde la relation entre les délais TCP, les trames DATA/HEADERS et les IDs de stream ;
4. mesure le délai requête-réponse par stream, pas seulement la durée totale de la connexion ;
5. rapproche les résultats des timings navigateur ou des journaux serveur.

### 6.5 QUIC et HTTP/3 : ne pas chercher TCP partout

QUIC fonctionne au-dessus d’UDP et intègre des fonctions de transport ainsi que TLS 1.3. HTTP/3 utilise QUIC ; une capture peut donc montrer de l’UDP, souvent sur le port 443, sans handshake TCP associé. Le port seul ne suffit pas pour identifier à coup sûr le protocole, car les services peuvent utiliser des ports non standards ou d’autres protocoles sur les mêmes ports.

Pour QUIC, Wireshark peut décoder les paquets pris en charge et, si les secrets TLS appropriés sont disponibles, déchiffrer les charges utiles correspondantes. Le support dépend de la version Wireshark et de la version du protocole. Une capture qui commence après le début d’une connexion, des datagrammes perdus ou des secrets absents peuvent empêcher l’analyse complète. Ne marque pas comme « paquet perdu TCP » un phénomène observé sur QUIC : les mécanismes de perte et de retransmission sont différents.

Filtres et recherches de départ à tester dans la version utilisée : `quic`, `udp.port == 443`, `tls.handshake`, `tcp.stream == N`, `http2` et `http3` lorsqu’ils sont reconnus. La liste exacte des champs doit être vérifiée dans la Display Filter Reference. Le nom de champ `http3` et sa disponibilité peuvent varier avec la version et les dissectors compilés.

## 7. DNS, IPv6, MTU, fragmentation et NAT

### 7.1 DNS : latence, cache et retransmission

Une requête DNS et sa réponse peuvent être séparées par des délais qui incluent le cache local, le résolveur récursif, le transport UDP/TCP ou le chiffrement DNS. Les identifiants de transaction doivent être interprétés avec l’adresse, les ports, le nom demandé et les horodatages ; ils ne sont pas universels à travers tous les résolveurs. Le même nom peut produire des résultats différents selon A/AAAA, le split DNS, le CDN, la géolocalisation ou l’état du cache.

Enquête structurée :

- identifie la première requête et sa réponse correspondante ;
- contrôle le code de réponse (RCODE), la troncature et le transport TCP éventuel ;
- cherche plusieurs essais, des réponses tardives ou des serveurs alternatifs ;
- vérifie si le système utilise DoT/DoH ou un cache qui rend les requêtes classiques invisibles ;
- compare le nom, le TTL et les adresses rendues au poste et au résolveur ;
- ne confonds pas « le nom se résout » avec « le service sur l’adresse est joignable ».

### 7.2 IPv4, IPv6 et chemins distincts

Un nom peut retourner des enregistrements A et AAAA et l’application peut tenter IPv6 et IPv4 avec un comportement de sélection ou de repli. Une capture qui ne montre qu’un seul chemin ne suffit pas à déclarer que l’autre est absent ou sain. Filtre séparément `ip` et `ipv6`, vérifie les interfaces et adresses réellement utilisées, puis analyse les délais de chaque tentative.

IPv6 utilise des extensions d’en-tête et une approche différente de la fragmentation par rapport à IPv4. Les messages ICMPv6, dont Packet Too Big, peuvent être indispensables au fonctionnement PMTUD. Les bloquer peut provoquer des symptômes où de petits échanges fonctionnent mais des réponses plus grandes se bloquent. Il faut distinguer ce motif d’un problème de résolution ou d’une fenêtre TCP.

### 7.3 MTU, MSS et Path MTU Discovery

MSS TCP limite la taille des données TCP dans un segment ; elle est généralement annoncée dans le SYN et dépend de la MTU et de l’en-tête. Mais MSS n’est pas la même chose que la MTU, et des tunnels, VLAN, IPsec, VXLAN ou autres encapsulations peuvent réduire la MTU effective. Une communication peut établir TCP correctement et échouer ensuite sur des paquets plus grands.

Indices à chercher :

- connexion établie mais certains transferts bloqués ;
- retransmissions répétées sur des segments de grande taille ;
- messages ICMP/ICMPv6 Fragmentation Needed ou Packet Too Big absents ou bloqués ;
- variation de comportement entre IPv4/IPv6 ou entre réseaux ;
- MSS inattendue sur SYN/SYN-ACK ;
- capture à un point qui ne montre pas la fragmentation ou l’encapsulation complète.

### Schéma 7 — Symptôme compatible avec un problème de MTU

<div class="wsx-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Le client envoie un segment important sur un chemin avec MTU plus basse. Un message de retour Packet Too Big est requis pour ajuster le paquet ; si le message est bloqué, les gros paquets peuvent être retransmis sans succès tandis que de petits échanges fonctionnent."><defs><marker id="wsx7a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#69d9ff"/></marker><marker id="wsx7b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ffca72"/></marker><marker id="wsx7c" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#7ee6b0"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#edf5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b8c8dc;text-anchor:middle}.a{fill:none;stroke:#69d9ff;stroke-width:2.4;marker-end:url(#wsx7a)}.b{fill:none;stroke:#ffca72;stroke-width:2.4;marker-end:url(#wsx7b)}.c{fill:none;stroke:#7ee6b0;stroke-width:2.4;marker-end:url(#wsx7c)}.flow{stroke-dasharray:8 7;animation:wsxDash 2.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="30" y="55" width="185" height="82" rx="12" fill="#142b42" stroke="#69d9ff"/><text x="122" y="83" class="t">Client</text><text x="122" y="106" class="s">Segment important</text><rect x="357" y="55" width="185" height="82" rx="12" fill="#322a1b" stroke="#ffca72"/><text x="449" y="83" class="t">Tunnel / route</text><text x="449" y="106" class="s">MTU inférieure</text><rect x="685" y="55" width="185" height="82" rx="12" fill="#16372d" stroke="#7ee6b0"/><text x="777" y="83" class="t">Serveur</text><text x="777" y="106" class="s">N'attend rien reçu</text><path d="M215 82H352" class="a flow"/><text x="283" y="72" class="s">paquet trop grand</text><path d="M542 82H680" class="b"/><text x="612" y="72" class="s">bloqué ou perdu</text><path d="M357 122H220" class="c"/><text x="289" y="148" class="s">ICMP PTB doit revenir</text><rect x="120" y="200" width="660" height="78" rx="12" fill="#101b29" stroke="#344961"/><text x="450" y="224" class="t">Vérifier MTU / MSS / ICMP</text><text x="450" y="247" class="s">Petits paquets OK + gros transferts bloqués : indice, pas verdict définitif</text><text x="450" y="265" class="s">Comparer les deux côtés et les compteurs du tunnel ou du routeur.</text></svg></div>

### 7.4 Fragmentation et réassemblage

Une capture au mauvais point peut ne montrer qu’un fragment ou qu’un côté du réassemblage. Le premier fragment IPv4 contient généralement l’en-tête transport, alors que les fragments suivants peuvent ne pas exposer les ports. Les fragments peuvent arriver hors ordre ou manquer. Les pare-feu et les chemins de tunnel ajoutent des contraintes. Utilise les champs de fragmentation et les informations de réassemblage, puis contrôle si la capture dispose de tous les fragments nécessaires.

### 7.5 NAT, asymétrie et load balancing

NAT peut modifier adresses/ports ; un répartiteur peut envoyer des flux distincts à plusieurs serveurs ; le retour peut emprunter un chemin différent. Si le captureur n’observe qu’un seul sens, certains ACK semblent manquer alors qu’ils circulent sur un autre lien. Compare les points de capture à chaque extrémité, les journaux de session et les compteurs du load balancer. Pour TCP, une asymétrie n’est pas forcément un problème ; elle le devient si les états de pare-feu ou les routes de retour ne la supportent pas correctement.

## 8. Outils en ligne de commande et automatisation

L’interface graphique est idéale pour explorer, mais une enquête répétable doit pouvoir réexécuter les mêmes sélections, produire les mêmes colonnes et consigner les versions. La suite Wireshark fournit notamment `tshark`, `dumpcap`, `capinfos`, `editcap` et `mergecap`. Les options disponibles évoluent ; utilise les pages de manuel de la version installée (`tshark -h`, `dumpcap -h`, etc.).

### 8.1 Lire une capture et filtrer

Exemples pour un fichier `incident.pcapng` :

```bash
# Version et capacités générales
tshark --version
capinfos incident.pcapng

# Afficher les paquets qui correspondent à un filtre d'affichage
tshark -r incident.pcapng -Y 'tcp.analysis.retransmission'

# Afficher un ensemble limité de champs
tshark -r incident.pcapng -Y 'dns' -T fields \
  -e frame.time_epoch -e ip.src -e ip.dst \
  -e dns.qry.name -e dns.flags.rcode

# Obtenir des statistiques de conversations TCP (selon options/version)
tshark -r incident.pcapng -q -z conv,tcp
```

Le filtre avec `-Y` est un filtre d’affichage. Le filtre de capture `-f` suit la syntaxe BPF/libpcap et s’applique à la capture live, pas de la même façon à un fichier déjà enregistré. Ne remplace pas aveuglément `-Y` par `-f` : les deux syntaxes ne sont pas interchangeables.

### 8.2 Capture live avec dumpcap

Pour une capture autorisée, commence par découvrir les interfaces avec la commande prévue par la version installée (`dumpcap -D`). Puis sélectionne explicitement l’interface plutôt que de laisser l’outil en choisir une implicitement. Exemple de forme de commande (adapte le numéro et les options à ton système) :

```bash
dumpcap -i 2 -a duration:120 -w capture-lab.pcapng
```

Pour un usage prolongé, ajoute des limites de fichier ou un buffer circulaire après avoir consulté `dumpcap -h`. Vérifie le répertoire de sortie, l’espace disponible, les droits, les compteurs de pertes signalés et le moment où la collecte s’arrête. Une capture qui s’est arrêtée faute d’espace disque doit être décrite comme incomplète.

### 8.3 Éditer, fusionner et normaliser des fichiers

- `editcap` sert notamment à sélectionner ou découper des plages, ajuster certaines propriétés et produire des fichiers dérivés.
- `mergecap` rassemble plusieurs fichiers de capture, généralement dans l’ordre temporel des paquets selon les timestamps disponibles.
- `capinfos` affiche des propriétés, la durée, les nombres de paquets et d’autres métadonnées du fichier.

Avant de fusionner des fichiers multi-interface, conserve la documentation de chaque source : les horloges peuvent être décalées, les paquets peuvent être vus plusieurs fois et les interfaces ne partagent pas forcément le même référentiel temporel. Fusionner des captures ne résout pas ces problèmes de mesure.

### 8.4 Colonnes et export de champs

Pour une enquête TCP, extraire heure, tuple, séquence, ACK, longueur et indicateurs aide à repérer les motifs répétitifs. Exemple :

```bash
tshark -r incident.pcapng \
  -Y 'tcp.stream == 12' \
  -T fields \
  -e frame.number -e frame.time_epoch \
  -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport \
  -e tcp.seq -e tcp.ack -e tcp.len \
  -e tcp.flags -e tcp.window_size_value
```

Vérifie si la configuration du désassembleur utilise des numéros de séquence relatifs ou absolus et note ce choix. Pour corréler plusieurs fichiers, conserve le timestamp absolu et n’utilise pas le numéro de trame comme identifiant global.

### 8.5 Reproductibilité et scripts

Un workflow de production doit archiver : nom et SHA-256 de l’original, version Wireshark/TShark, système, interface, durée, filtre de capture, options de capture, compteur de pertes, filtres d’analyse et commandes utilisées. Évite d’écrire un script qui transforme toutes les alertes du panneau Expert en « incident confirmé ». Un pipeline robuste produit des candidats à investiguer puis laisse place à la vérification contextuelle.

## 9. Requêtes d’analyse et pièges fréquents

Les filtres ci-dessous sont des points de départ ; la référence des champs Wireshark correspondant à la version installée reste la source exacte.

| Question | Filtre de départ |
|---|---|
| TCP et hôte précis | `tcp && ip.addr == 192.0.2.10` |
| Flux TCP spécifique | `tcp.stream == 12` |
| SYN initial | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| RST | `tcp.flags.reset == 1` |
| ACK avec données absentes suspectées | `tcp.analysis.ack_lost_segment` |
| Retransmission | `tcp.analysis.retransmission` |
| RTO | `tcp.analysis.rto` |
| Fenêtre zéro | `tcp.analysis.zero_window` |
| Checksum TCP mauvais selon dissector | `tcp.checksum.status == 2` si ce champ et cette valeur sont disponibles dans la version |
| DNS avec erreur | `dns.flags.rcode != 0` |
| DNS troncature | `dns.flags.truncated == 1` |
| ICMP/ICMPv6 | `icmp || icmpv6` |
| Gros paquets observés | `frame.len > 1400` |
| Trafic UDP/443 candidat QUIC | `udp.port == 443` puis analyser le protocole décodé |
| Alertes TLS visibles | `tls.alert_message` si le champ est pris en charge dans la version |

Attention à `tcp.checksum.status`: les champs de checksum et les valeurs exactes disponibles dépendent de la version du dissector et des préférences. Il vaut mieux utiliser la saisie semi-automatique des champs et vérifier un paquet témoin avant d’automatiser un filtre de production.

### 9.1 Les cinq pièges de raisonnement à éviter

1. **Confondre alerte et cause.** L’alerte décrit un motif dans les données observées ; elle ne localise pas automatiquement l’équipement fautif.
2. **Supposer que Wireshark a vu le câble.** La capture locale peut se situer avant un offload, une segmentation ou un regroupement de paquets.
3. **Comparer des horodatages non synchronisés.** L’écart entre deux systèmes inclut le décalage de leurs horloges.
4. **Prendre le port pour une preuve de protocole.** UDP/443 est compatible avec QUIC, mais le port ne constitue pas une preuve unique.
5. **Lire du texte sensible sans nécessité.** Une reconstruction de flux peut exposer des données privées ; sélectionne seulement ce qui est nécessaire au diagnostic.

## 10. Construire un rapport d’investigation défendable

Un rapport doit permettre à un autre ingénieur de reproduire le raisonnement sans avoir assisté à l’incident.

### Structure recommandée

1. **Résumé exécutif :** impact, périmètre, période et conclusion à niveau de confiance explicite.
2. **Environnement :** clients/serveurs concernés, protocoles, interfaces, équipements intermédiaires et topologie utile.
3. **Méthode de collecte :** point d’observation, horloges, version, filtres, longueur de capture, limites et compteurs de drops.
4. **Intégrité des fichiers :** noms, tailles, empreintes, source, conservation de l’original et transformations.
5. **Chronologie :** trames et timestamps pertinents avec filtres utilisés et événements d’application corrélés.
6. **Observations :** faits visibles, mesures et captures d’écran recadrées sans secrets inutiles.
7. **Hypothèses testées :** hypothèse, élément qui la soutient, élément qui la contredit, prochaine validation.
8. **Conclusion :** ce qui est établi, ce qui est probable et ce qui n’est pas prouvé.
9. **Actions :** mesure immédiate, correction durable et vérification de non-récurrence.

### Exemple de conclusion prudente

> La capture réalisée sur l’interface du client montre trois émissions SYN sans SYN-ACK visible pendant la fenêtre étudiée. La connexion n’est donc pas établie au point d’observation dans cette trace. Cette observation est compatible avec une absence de réponse, un filtrage, un problème de chemin de retour ou une capture incomplète. Les compteurs de perte du captureur sont nuls selon le rapport de collecte, mais aucune capture côté serveur n’est disponible. La cause exacte n’est donc pas localisée. Étape suivante : collecter simultanément côté serveur et vérifier les journaux du pare-feu/NAT pour la même période.

Cette conclusion est plus utile qu’un diagnostic catégorique non démontré, car elle dit ce qui est connu et identifie la meilleure prochaine expérience.

## 11. Atelier expert 1 — Transfert HTTPS lent

### Situation

Un utilisateur signale que le téléchargement d’un fichier HTTPS commence rapidement mais stagne après quelques secondes. Une capture côté client montre TCP établi, TLS négocié, puis plusieurs événements de retransmission sur des segments de données. La fenêtre de réception semble ouverte et il n’existe pas de DNS visible immédiatement avant cette connexion.

### Démarche

1. Isoler le flux avec `tcp.stream == N` et vérifier le tuple dans les deux directions.
2. Créer les colonnes `tcp.seq`, `tcp.ack`, `tcp.len`, `tcp.analysis.ack_rtt` et `tcp.window_size`.
3. Repérer les plages de séquence réémises et les ACK associés ; déterminer si l’analyseur voit un ACK cumulatif bloqué, des SACK ou du réordonnancement.
4. Examiner les graphiques Sequence Number et RTT si la version les propose ; noter la période exacte du plateau.
5. Vérifier si la fenêtre de réception devient nulle, si l’émetteur continue à envoyer, et quand les ACK progressent.
6. Chercher les messages ICMP/ICMPv6 utiles et comparer petits échanges et segments plus grands pour une éventuelle piste MTU.
7. Reproduire avec une capture côté serveur ou un point réseau ; contrôler les pertes du SPAN et les offloads si les données proviennent du client.
8. Corréler la durée et le débit avec les métriques du serveur et du lien.

### Corrigé raisonné

Le fait établi est que la trace côté client contient des retransmissions reconnues pendant la stagnation. Si les ACK cessent de progresser sur une plage, cela renforce l’hypothèse d’un trou de données ou d’un problème d’observation. Cela ne suffit pas à identifier le lien responsable. Un problème de MTU est plausible si seuls les grands paquets échouent et que les signaux PMTUD sont absents ; une saturation ou perte peut être plausible si les compteurs réseau correspondent ; l’application peut être en cause si la fenêtre est nulle. La conclusion ne doit être finalisée qu’après comparaison au second point ou lecture de compteurs supplémentaires.

## 12. Atelier expert 2 — Handshake TLS interrompu

### Situation

Une application affiche parfois une erreur TLS après une mise à jour de certificat. La capture comporte un ClientHello puis un message de serveur ; les paquets suivants sont chiffrés ou ne sont plus observés. L’erreur n’apparaît pas à chaque essai.

### Démarche

1. Vérifier que la capture contient le début complet de chaque connexion et identifier si le client réutilise des sessions.
2. Comparer les essais réussis et échoués, en distinguant IP de destination, IPv4/IPv6, SNI visible, version TLS et négociations proposées.
3. Rechercher une alerte TLS visible ; noter le sens, la trame et le moment.
4. Vérifier les journaux client et serveur, la chaîne de certificats, les intermédiaires, les dates et le nom attendu.
5. Si c’est autorisé et nécessaire, utiliser un client de test avec key log pour observer les messages déchiffrables ; protéger le fichier de secrets.
6. Vérifier si un proxy d’inspection TLS termine la connexion : il peut présenter un certificat différent et créer une seconde session vers le serveur.
7. Comparer les chemins IPv4 et IPv6 et la résolution DNS si l’incident n’affecte qu’une partie des clients.

### Corrigé raisonné

Un certificat mis à jour peut révéler une chaîne intermédiaire manquante, une incompatibilité de nom ou une différence de confiance entre postes, mais la seule coïncidence temporelle n’en est pas la preuve. Les messages visibles dans le handshake et l’alerte fournissent des indices ; le journal de validation du client est souvent nécessaire pour identifier la raison précise. Une connexion TLS qui disparaît de la capture peut être due à un paquet perdu par le captureur, à un autre chemin ou à une terminaison proxy. Documenter le niveau de preuve est obligatoire.

## 13. Atelier expert 3 — Microcoupures sur un réseau IPv6

### Situation

Le service fonctionne en général, mais certains transferts IPv6 restent bloqués après un petit échange initial. IPv4 semble normal. La capture montre peu d’ICMPv6, des paquets TCP de grande taille et des retransmissions.

### Démarche

1. Séparer les flux IPv4 et IPv6 et confirmer que l’application a réellement choisi IPv6 pendant l’échec.
2. Comparer MSS des SYN, tailles des segments et progression ACK.
3. Chercher ICMPv6 Packet Too Big et examiner si la MTU annoncée serait compatible avec le tunnel ou le chemin.
4. Capturer, avec autorisation, aux deux extrémités ou sur le routeur qui porte le tunnel ; déterminer où un paquet cesse d’être visible.
5. Vérifier les règles ACL/pare-feu sur ICMPv6 sans désactiver globalement les protections.
6. Contrôler les offloads et les compteurs d’interface pour éviter de confondre segmentation locale et paquet réellement présent sur le fil.
7. Effectuer un test contrôlé avec tailles de paquets différentes, en documentant précisément les paramètres et le chemin.

### Corrigé raisonné

Le motif est compatible avec un problème de MTU/PMTUD, mais nécessite une validation. La preuve serait renforcée si les grands paquets concernés sont vus à la sortie d’un côté mais pas à l’entrée de l’autre, si la MTU du lien est inférieure à la taille effective, ou si un message Packet Too Big requis est bloqué. Il faut aussi écarter un service qui ne traite pas les données, une route asymétrique et les pertes de capture.

## 14. Atelier d’automatisation — Construire un rapport reproductible

L’objectif est de produire des éléments utiles et non un rapport qui révèle tout le contenu des communications. Sur une capture de laboratoire, la chaîne peut être :

1. enregistrer l’empreinte SHA-256 du fichier original ;
2. relever version, durée, nombre de paquets et interfaces avec `capinfos` ;
3. extraire les métadonnées de DNS, SYN, RST, retransmissions et flux concernés avec `tshark -T fields` ;
4. calculer les comptes par catégorie, en précisant les filtres exacts ;
5. créer un tableau de chronologie trié et une liste d’hypothèses ;
6. afficher manuellement les flux prioritaires dans Wireshark ;
7. joindre à la note uniquement les extraits indispensables et une trace des commandes ;
8. conserver la capture originale et documenter l’anonymisation de toute copie diffusée.

Un script ne doit pas exporter les charges utiles par défaut. Limite les champs aux éléments nécessaires (timestamps, adresses pseudonymisées quand possible, ports, protocoles, tailles, IDs de requête non sensibles) et prévois un contrôle humain avant la diffusion.

## 15. Exercices de validation

### Exercice 1 — Les retransmissions sont-elles la preuve d’une perte physique ?

**Réponse attendue :** non. Elles sont des indices calculés à partir de l’ordre et des séquences observés. Le réordonnancement, le point de capture, l’incomplétude du fichier, les pertes du collecteur ou les caractéristiques de l’hôte peuvent créer des motifs analogues. Corrèle une capture au récepteur, des compteurs et la chronologie avant de localiser la perte.

### Exercice 2 — Pourquoi `tcp.stream == 8` n’est-il pas une clé de corrélation entre deux fichiers ?

**Réponse attendue :** les index de stream sont attribués par l’analyseur dans le contexte de chaque capture. Le même index peut désigner un flux différent dans un autre fichier. Utilise les tuples, horodatages alignés, identifiants applicatifs et informations de NAT/proxy, avec les limites de chaque méthode.

### Exercice 3 — Un checksum sortant apparaît invalide. Que vérifier ?

**Réponse attendue :** si le paquet a été capturé localement avant offload, si le checksum est partiel et si une capture distante confirme le problème. Ne désactive pas l’offload en production sans justification. Documente le point d’observation.

### Exercice 4 — Peut-on lire HTTP/2 dans n’importe quelle capture TLS ?

**Réponse attendue :** non. La charge utile TLS est chiffrée. Il faut disposer des secrets de session appropriés et d’une capture suffisamment complète ; il faut aussi que Wireshark reconnaisse le protocole correspondant. Les métadonnées visibles ne remplacent pas le contenu HTTP déchiffré.

### Exercice 5 — UDP/443 prouve-t-il qu’il s’agit de HTTP/3 ?

**Réponse attendue :** non. C’est un indice compatible avec QUIC, mais le décodage doit confirmer le protocole, et des services peuvent utiliser d’autres ports ou d’autres protocoles. Le port seul n’est pas une identification définitive.

### Exercice 6 — Une fenêtre TCP nulle indique-t-elle une congestion du lien ?

**Réponse attendue :** pas nécessairement. Elle indique que le récepteur annonce qu’il ne peut pas accepter de nouvelles données à cet instant. Inspecte le côté qui annonce la fenêtre, le processus de lecture, les buffers et les mises à jour de fenêtre.

### Exercice 7 — Un écart de 12 ms entre deux captures prouve-t-il un délai de 12 ms dans le réseau ?

**Réponse attendue :** non, pas sans vérifier les horloges, leur source, l’horodatage matériel/logiciel, le placement des captures et l’identité de l’événement comparé. L’écart peut contenir une erreur de synchronisation.

### Exercice 8 — La capture montre un SYN client mais aucun paquet côté serveur. Quelle conclusion peut-on écrire ?

**Réponse attendue :** le SYN est visible au point client et aucun paquet correspondant n’est visible dans la capture serveur durant la fenêtre étudiée. Cela localise une différence d’observation, mais il faut vérifier l’alignement temporel, les pertes de capture, le NAT et le bon point de collecte avant d’assigner une cause.

### Exercice 9 — Pourquoi conserver le filtre de capture et le rapport de drops ?

**Réponse attendue :** le filtre peut exclure des paquets utiles, et les pertes du captureur peuvent créer des trous artificiels. Sans ces paramètres, une autre personne ne peut pas correctement évaluer la complétude et la reproductibilité de l’analyse.

### Exercice 10 — Quel élément prouve le mieux qu’un délai est côté application serveur ?

**Réponse attendue :** une chronologie corrélée côté serveur montrant que la requête est reçue à un moment donné et que la réponse est générée/émise plus tard, corroborée si possible par les journaux et métriques applicatifs. Une seule durée mesurée côté client inclut réseau, files, proxy et serveur.

## 16. Check-list expert avant conclusion

- [ ] L’objectif de l’analyse est formulé en une question testable.
- [ ] Le point d’observation et l’interface ont été identifiés.
- [ ] La version de Wireshark/TShark et les paramètres de collecte sont consignés.
- [ ] Les drops, la troncature, les filtres et les timestamps ont été évalués.
- [ ] L’original est préservé et son empreinte est consignée.
- [ ] Le tuple, la direction, le contexte NAT/proxy et l’index du flux ont été vérifiés.
- [ ] Les analyses TCP sont confirmées dans la chronologie et non prises isolément.
- [ ] Les effets d’offload, de segmentation et de réassemblage sont envisagés.
- [ ] Les protocoles chiffrés sont décrits en fonction de la visibilité réelle.
- [ ] Les hypothèses alternatives ont été listées et les données manquantes explicitées.
- [ ] Les filtres, champs et commandes du rapport sont reproductibles.
- [ ] Les exports sont minimisés et ne révèlent pas de secrets inutiles.

## 17. Glossaire essentiel

- **ACK cumulatif :** accuse réception de tous les octets contigus jusqu’à un point du flux TCP.
- **BDP :** produit bande passante-délai, qui aide à estimer la quantité de données à maintenir en vol.
- **Capture drop :** paquet perdu par le mécanisme de capture ou le collecteur, distinct d’une perte sur le réseau.
- **ECN :** mécanisme de notification explicite de congestion, visible dans les champs appropriés lorsque le chemin et les extrémités le prennent en charge.
- **GRO/LRO :** mécanismes de regroupement de paquets reçus qui peuvent influencer l’apparence de la capture locale.
- **Key log :** fichier qui contient des secrets de sessions destinés notamment au déchiffrement TLS dans un outil d’analyse autorisé.
- **MSS :** taille maximale de données TCP annoncée dans une connexion, différente de la MTU de lien.
- **Offload :** transfert d’une partie du traitement réseau à la carte ou au matériel.
- **PCAPNG :** format de capture extensible qui peut conserver des métadonnées et plusieurs interfaces.
- **PMTUD :** découverte de la MTU de chemin ; dépend de la réception des signaux réseau nécessaires.
- **RTO :** retransmission temporisée lorsque l’expéditeur estime qu’un segment n’a pas été accusé dans le délai attendu.
- **SACK :** accusés de réception sélectifs qui indiquent des plages de données reçues au-delà d’un trou.
- **SPAN/TAP :** méthodes d’observation du trafic sur un équipement ou via un dispositif physique dédié.
- **TSO/GSO :** mécanismes qui regroupent ou déportent la segmentation des paquets émis.
- **Tuple :** combinaison du protocole, des adresses IP et des ports qui aide à identifier un flux.

## 18. Références techniques

Consulte la documentation de la même version que celle installée, surtout pour les champs de filtre et options CLI.

- [Guide utilisateur officiel de Wireshark](https://www.wireshark.org/docs/wsug_html/)
- [Référence officielle des filtres d’affichage](https://www.wireshark.org/docs/dfref/)
- [Référence des champs TCP](https://www.wireshark.org/docs/dfref/t/tcp.html)
- [Manuel officiel TShark](https://www.wireshark.org/docs/man-pages/tshark.html)
- [Manuel officiel dumpcap](https://www.wireshark.org/docs/man-pages/dumpcap.html)
- [Documentation Wireshark sur TLS et le déchiffrement](https://wiki.wireshark.org/TLS/)
- [Documentation de capture et d’offload](https://wiki.wireshark.org/capturesetup/offloading)
- [Manuel officiel capinfos](https://www.wireshark.org/docs/man-pages/capinfos.html)
- [Manuel officiel editcap](https://www.wireshark.org/docs/man-pages/editcap.html)
- [Manuel officiel mergecap](https://www.wireshark.org/docs/man-pages/mergecap.html)

---

## À retenir

L’expertise Wireshark est moins une collection de filtres qu’une discipline de mesure. Il faut savoir où les paquets ont été capturés, quels effets l’hôte peut introduire, ce que les séquences TCP indiquent réellement, ce que le chiffrement cache, et ce qui reste impossible à déduire d’un seul fichier. Une conclusion forte se construit en séparant les faits des hypothèses, en corrélant les bons points de mesure et en rendant chaque étape reproductible.
