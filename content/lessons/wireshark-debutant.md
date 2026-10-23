<style>
.ws-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.2rem 0;padding:.75rem;border:1px solid #23384f;border-radius:14px;background:#080f19;color:#e6eef8;box-sizing:border-box}
.ws-diagram svg{display:block;width:100%;height:auto;max-width:100%}
.ws-diagram .flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}
@keyframes wsDash{to{stroke-dashoffset:-30}}
@media(prefers-reduced-motion:reduce){.ws-diagram .flow{animation:none!important}}
</style>

# Analyse de paquets avec Wireshark — Niveau Débutant

**Niveau :** Débutant  
**Domaine :** Réseaux informatiques, diagnostic et sécurité défensive  
**Objectif :** apprendre à capturer un trafic autorisé, lire les champs d’un paquet, distinguer les filtres de capture des filtres d’affichage et utiliser les échanges réseau pour diagnostiquer un problème.

Ce cours privilégie la méthode : poser une question, capturer au bon endroit, isoler un échange, examiner ses champs et formuler une conclusion qui reste proportionnée aux preuves. Wireshark peut rendre un réseau très visible, mais il ne connaît pas automatiquement le contexte métier et ne peut pas montrer un paquet qu’il n’a pas observé.

> **Règle de sécurité :** capture uniquement le trafic de tes appareils, de ton laboratoire ou d’un réseau pour lequel tu as reçu une autorisation. Une capture peut contenir des adresses internes, des identifiants, des messages privés ou des données personnelles. Ne collecte pas le trafic d’autres personnes pour satisfaire ta curiosité.

## 1. À quoi sert Wireshark ?

Wireshark est un analyseur de protocoles réseau. Il peut capturer des paquets depuis une interface disponible ou ouvrir un fichier de capture produit par Wireshark ou un outil compatible. Il affiche ensuite les trames et les champs qu’il sait décoder : adresses MAC, IP source et destination, ports TCP/UDP, indicateurs TCP, requêtes DNS, messages DHCP, paquets ICMP, négociation TLS et bien d’autres éléments.

Il sert notamment à :

- vérifier si une requête quitte effectivement un poste et si une réponse revient ;
- comprendre une résolution DNS, une négociation TCP ou un échange DHCP ;
- repérer des retransmissions TCP, des réponses refusées ou des délais inhabituels ;
- confirmer quels protocoles sont réellement présents dans une capture ;
- mesurer des conversations et repérer quels hôtes échangent le plus de données ;
- apprendre les protocoles en observant leurs champs dans un laboratoire.

Wireshark n’est pas un outil qui « répare » le réseau. Il ne remplace ni les journaux du serveur, ni les tests de routage, ni les compteurs des commutateurs et pare-feu. Il observe les paquets visibles depuis un point donné. Un paquet absent de la capture peut ne pas avoir été émis, avoir été perdu avant le point d’observation, être passé par une autre interface, ou avoir été écarté par un filtre.

### 1.1 La capture dépend du point d’observation

Imagine que tu regardes une route depuis une fenêtre : tu vois ce qui passe devant toi, pas ce qui se déroule dans une autre rue. De la même manière, une capture sur le PC client ne montre pas nécessairement le trafic après le pare-feu, sur le serveur ou sur un autre chemin réseau.

Sur un réseau commuté, une carte réseau ordinaire ne reçoit généralement pas tous les échanges unicast entre les autres machines. Pour observer un autre segment, il faut un point de capture adapté : port miroir/SPAN, TAP réseau, capture sur le serveur ou outil de capture fourni par l’infrastructure, le tout avec autorisation. Le mode promiscuité ne transforme pas à lui seul un port de switch ordinaire en sonde universelle.

## 2. Comprendre ce qu’est un paquet

Les données applicatives sont encapsulées dans une suite d’en-têtes. Le niveau exact dépend du réseau et du protocole : une trame Ethernet peut transporter un paquet IP, qui contient un segment TCP ou un datagramme UDP, qui lui-même transporte des données applicatives.

### Schéma 1 — L’encapsulation des données

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 350" role="img" aria-label="Encapsulation illustrative : données applicatives dans TCP ou UDP, dans IP, puis dans une trame Ethernet ; Wireshark décompose les couches à la lecture."><defs><marker id="wsa2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker></defs><style>.wst2{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.wss2{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.wsarr2{stroke:#66d9ff;stroke-width:2.5;fill:none;marker-end:url(#wsa2)}.flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}@keyframes wsDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><text x="440" y="25" class="wst2">Encapsulation à l’émission (vision simplifiée)</text><rect x="42" y="48" width="796" height="52" rx="9" fill="#172b43" stroke="#66d9ff" stroke-width="2"/><text x="440" y="70" class="wst2">Trame Ethernet</text><text x="440" y="88" class="wss2">En-tête Ethernet + paquet IP + FCS éventuel selon point de capture</text><rect x="100" y="116" width="680" height="52" rx="9" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="440" y="138" class="wst2">Paquet IP</text><text x="440" y="156" class="wss2">Adresses IP source et destination, TTL / Hop Limit, protocole suivant</text><rect x="160" y="184" width="560" height="52" rx="9" fill="#332b19" stroke="#ffc46b" stroke-width="2"/><text x="440" y="206" class="wst2">Segment TCP ou datagramme UDP</text><text x="440" y="224" class="wss2">Ports, état TCP et/ou longueur UDP</text><rect x="220" y="252" width="440" height="52" rx="9" fill="#2b2540" stroke="#c1a4ff" stroke-width="2"/><text x="440" y="274" class="wst2">Données applicatives</text><text x="440" y="292" class="wss2">DNS, HTTP, TLS, DHCP… selon le protocole</text><path class="wsarr2 flow" d="M440 310V330"/><text x="440" y="346" class="wss2">Wireshark affiche les protocoles reconnus, du niveau externe vers le contenu disponible.</text></svg></div>

### 2.1 Trame, paquet, segment et datagramme

Les mots se ressemblent, mais ils ne désignent pas exactement la même couche :

- **Trame Ethernet :** unité de couche liaison. Elle comporte des adresses MAC source et destination, un champ indiquant le type de contenu et, sur le câble, une séquence de contrôle. Selon le matériel et le point de capture, le FCS peut ne pas être présent dans les données capturées.
- **Paquet IP :** unité de couche réseau. En IPv4, tu verras les adresses IP et le TTL. En IPv6, tu verras les adresses IPv6 et le Hop Limit.
- **Segment TCP :** données de transport avec ports, numéro de séquence, numéro d’acquittement et drapeaux comme SYN, ACK, FIN ou RST.
- **Datagramme UDP :** transport sans connexion, avec ports et longueur. UDP n’effectue pas le même mécanisme d’établissement et de retransmission que TCP.
- **Données applicatives :** DNS, HTTP, TLS, DHCP, NTP, SIP ou autre contenu reconnu par le dissector de Wireshark.

Dans les conversations courantes, on dit souvent « paquet » pour désigner toute unité capturée. C’est compréhensible, mais apprendre à nommer la bonne couche rend les diagnostics plus précis.

### 2.2 Adresses MAC et adresses IP

Une adresse **MAC** sert à l’acheminement sur le segment de couche liaison. Une adresse **IP** sert à l’adressage logique et au routage entre réseaux. Dans une capture prise sur un PC, les MAC visibles peuvent être celles du PC et de la passerelle, tandis que l’adresse IP de destination est celle d’un serveur distant. C’est normal : le routeur réécrit l’en-tête de couche liaison pour le prochain lien, mais il conserve habituellement les adresses IP de bout en bout, sauf mécanismes comme le NAT.

Exemple : un poste `192.0.2.10/24` veut joindre `198.51.100.20`. Si la destination n’est pas sur son réseau local, il envoie la trame vers la MAC de sa passerelle, tout en gardant l’IP de destination du serveur distant. Les plages `192.0.2.0/24` et `198.51.100.0/24` sont réservées aux exemples documentaires ; remplace-les par les adresses de ton laboratoire lors des manipulations.

### 2.3 Ports et sockets

Un port TCP ou UDP identifie un point de terminaison de transport sur un hôte. Le port de destination peut aider à reconnaître un service : DNS utilise souvent le port 53, HTTP le port 80 et HTTPS le port 443. Ce sont des conventions, pas des preuves absolues. Un service peut écouter sur un autre port, et l’emploi d’un port 443 ne prouve pas que le contenu est du HTTPS.

Un échange TCP est souvent identifié par le quadruplet source IP, source port, destination IP et destination port, avec le protocole TCP. On parle de flux ou de conversation. Les ports source côté client sont fréquemment éphémères. Ne conclus donc pas que le client est le serveur simplement parce que son numéro de port est élevé.

## 3. Installer et préparer Wireshark

Télécharge l’installateur depuis le site officiel de Wireshark : [wireshark.org](https://www.wireshark.org/). Sous Windows, l’installateur propose généralement Npcap, un composant de capture nécessaire pour intercepter les paquets depuis les interfaces prises en charge. L’installation peut demander des privilèges administrateur. Utilise les options adaptées à ton poste et à la politique de ton organisation.

Sous Linux, l’accès aux interfaces de capture peut dépendre des permissions et de la façon dont le paquet Wireshark est installé. Évite de lancer systématiquement toute l’interface graphique en superutilisateur : configure plutôt le mécanisme d’accès à la capture recommandé par ta distribution et ses consignes de sécurité. Sur macOS, les autorisations et permissions dépendent également de la version et de l’installation.

### 3.1 Vérifier les interfaces disponibles

Au lancement, Wireshark présente souvent une liste d’interfaces telles que :

- Ethernet : carte filaire ;
- Wi-Fi : interface sans fil ;
- Loopback : trafic local entre applications du même poste ;
- VPN ou adaptateur virtuel : interface créée par un client VPN, hyperviseur ou autre logiciel ;
- interfaces de machines virtuelles ou de conteneurs, selon la configuration.

Observe les petits graphiques ou compteurs d’activité lorsqu’ils sont affichés. Ils aident à identifier l’interface qui transporte du trafic. Si tu ne sais pas laquelle choisir, génère une seule activité simple, comme ouvrir une page web de test, et observe quelle interface devient active. La présence de trafic ne garantit pas que ce soit la bonne interface pour le problème étudié.

### 3.2 Capture live et fichier de capture

Une **capture live** est l’enregistrement de paquets au fur et à mesure qu’ils sont vus par le système. Un fichier `.pcapng` conserve les paquets et des métadonnées de capture compatibles avec le format. Un fichier `.pcap` est aussi courant, mais possède des capacités de métadonnées différentes. Les fichiers de capture peuvent être volumineux et contenir des informations sensibles.

Pour une première expérience :

1. Lance Wireshark avec les droits nécessaires à la capture.
2. Sélectionne l’interface réellement utilisée par ton trafic de test.
3. Démarre la capture sans filtre compliqué.
4. Effectue une seule action contrôlée, par exemple demander une résolution DNS ou ouvrir une page de laboratoire.
5. Arrête la capture dès que les paquets utiles sont obtenus.
6. Enregistre le fichier sous un nom descriptif, sans donnée personnelle inutile.
7. Recommence un test indépendant plutôt que de mélanger plusieurs causes dans une énorme capture.

Le nom d’une interface ou les boutons changent légèrement selon la version. Les concepts restent les mêmes : choisir un point d’observation, capturer, arrêter, sauvegarder puis analyser.

## 4. Reconnaître les zones de l’interface

### Schéma 2 — Les trois zones d’analyse

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 390" role="img" aria-label="Interface Wireshark stylisée : barre de filtre, liste des paquets, détails du paquet et octets hexadécimaux."><style>.wst3{font:600 15px system-ui,sans-serif;fill:#eef5ff}.wss3{font:12px system-ui,sans-serif;fill:#c0ccdd}.wsmono3{font:12px ui-monospace,Consolas,monospace;fill:#dbe8f9}.wscall3{font:600 12px system-ui,sans-serif;fill:#66d9ff}</style><rect x="18" y="18" width="844" height="354" rx="12" fill="#0b1421" stroke="#506680" stroke-width="2"/><rect x="30" y="30" width="820" height="36" rx="6" fill="#17273b" stroke="#66d9ff"/><text x="44" y="52" class="wst3">Filtre d’affichage : dns</text><rect x="30" y="78" width="820" height="126" rx="6" fill="#101e2e" stroke="#3e5874"/><text x="44" y="98" class="wss3">N°</text><text x="95" y="98" class="wss3">Temps</text><text x="190" y="98" class="wss3">Source</text><text x="350" y="98" class="wss3">Destination</text><text x="510" y="98" class="wss3">Protocole</text><text x="625" y="98" class="wss3">Info</text><path d="M38 108H842" stroke="#2d4259"/><rect x="38" y="112" width="804" height="24" rx="4" fill="#233e34"/><text x="44" y="129" class="wsmono3">12</text><text x="95" y="129" class="wsmono3">0.000</text><text x="190" y="129" class="wsmono3">192.0.2.10</text><text x="350" y="129" class="wsmono3">192.0.2.53</text><text x="510" y="129" class="wsmono3">DNS</text><text x="625" y="129" class="wsmono3">Standard query A example.net</text><text x="44" y="155" class="wsmono3">13</text><text x="95" y="155" class="wsmono3">0.012</text><text x="190" y="155" class="wsmono3">192.0.2.53</text><text x="350" y="155" class="wsmono3">192.0.2.10</text><text x="510" y="155" class="wsmono3">DNS</text><text x="625" y="155" class="wsmono3">Standard query response</text><text x="44" y="182" class="wss3">Liste des paquets — chaque ligne correspond à une trame capturée.</text><rect x="30" y="216" width="404" height="142" rx="6" fill="#121d2c" stroke="#72e4a5"/><text x="44" y="238" class="wst3">Détails du paquet sélectionné</text><text x="46" y="263" class="wsmono3">▾ Ethernet II</text><text x="64" y="284" class="wsmono3">Source : 00:11:22:33:44:55</text><text x="46" y="306" class="wsmono3">▾ Internet Protocol Version 4</text><text x="64" y="327" class="wsmono3">Source : 192.0.2.10</text><text x="64" y="346" class="wsmono3">Destination : 192.0.2.53</text><rect x="446" y="216" width="404" height="142" rx="6" fill="#17172d" stroke="#c1a4ff"/><text x="460" y="238" class="wst3">Octets du paquet</text><text x="460" y="263" class="wsmono3">0000  00 11 22 33 44 55 66 77</text><text x="460" y="286" class="wsmono3">0010  08 00 45 00 00 3c 1a 2b</text><text x="460" y="309" class="wsmono3">0020  40 00 40 11 c0 a8 00 0a</text><text x="460" y="332" class="wsmono3">0030  c0 a8 00 35 00 35 12 34</text><text x="460" y="350" class="wss3">Exemple illustratif, non lié à une vraie capture.</text></svg></div>

L’interface principale présente généralement trois zones :

1. **Liste des paquets :** une ligne par paquet capturé, avec numéro, temps, source, destination, protocole, longueur et résumé.
2. **Détails du paquet :** une arborescence des protocoles et champs du paquet sélectionné. Développe une branche avec la petite flèche située devant son nom.
3. **Octets du paquet :** représentation hexadécimale et, lorsqu’elle est imprimable, représentation texte des octets capturés.

Clique une ligne dans la liste pour que les deux zones du bas se mettent à jour. Dans les détails, sélectionner un champ met généralement en surbrillance les octets correspondants. Cette relation entre champ décodé et octets est importante : elle relie l’interprétation au contenu effectivement capturé.

### 4.1 Lire la ligne d’un paquet sans se précipiter

Une ligne contenant `DNS` ou `TCP` résume le paquet, mais ne montre pas tout. La colonne **Info** est une aide, pas le diagnostic complet. Sélectionne la ligne, développe les couches et vérifie les adresses, ports, drapeaux, identifiants, codes de réponse et champs pertinents.

Le nom de protocole montré dans la liste est généralement le protocole de plus haut niveau que Wireshark a réussi à reconnaître. Le paquet continue toutefois à contenir les en-têtes des couches inférieures. Une ligne `DNS` comprend par exemple la trame Ethernet, le paquet IP et le datagramme UDP ou le segment TCP approprié.

### 4.2 Numéro de paquet et temps

Le numéro de paquet représente l’ordre dans lequel la trame apparaît dans le fichier. Ce n’est pas une adresse ni une priorité. La colonne de temps peut montrer un temps absolu, un temps relatif au début de la capture ou un temps depuis le paquet précédent, selon les préférences.

Le **delta temporel** entre une requête et une réponse peut indiquer le délai observé au point de capture. Mais il n’inclut pas nécessairement tous les traitements du système, du réseau ou du serveur, et il peut dépendre du point de capture et de l’horloge. Compare des mesures prises dans les mêmes conditions.

## 5. Réaliser une première capture

L’objectif de ce premier atelier est de voir un échange que tu peux reproduire. Il ne faut pas analyser tout Internet ni collecter inutilement un grand volume de données.

### Atelier 1 — Voir son trafic de test

**Préparation :** utilise ton propre ordinateur et un site de test autorisé, ou un service local dans ton laboratoire. La procédure ci-dessous reste volontairement générique afin de fonctionner sur différents systèmes.

1. Ferme les applications qui produisent beaucoup de trafic si cela est possible.
2. Démarre Wireshark sur l’interface active.
3. Commence l’enregistrement puis ouvre un nouvel onglet vers une page que tu es autorisé à consulter.
4. Attends la fin du chargement, puis arrête la capture.
5. Tape `dns` dans la barre du filtre d’affichage si tu veux isoler les paquets DNS visibles.
6. Efface le filtre pour retrouver tous les paquets.
7. Enregistre la capture de laboratoire.

Il se peut que peu ou pas de paquets DNS apparaissent. Le navigateur ou le système peut utiliser un cache DNS, un résolveur chiffré, une connexion existante ou un protocole qui rend le trafic différent de ce que tu attendais. Ce résultat n’indique pas automatiquement une panne.

### 5.1 Pourquoi le trafic peut-il ne pas apparaître ?

Vérifie successivement :

- La bonne interface a-t-elle été sélectionnée ?
- La capture a-t-elle démarré avant l’action de test ?
- Un filtre de capture n’a-t-il pas exclu les paquets ?
- Le trafic est-il passé par une interface VPN, virtuelle ou loopback ?
- Le système a-t-il répondu à partir d’un cache ?
- Le protocole utilisé est-il différent de celui recherché ?
- As-tu le droit de capture et le pilote requis ?

N’essaie pas de « provoquer du trafic » sur des réseaux qui ne t’appartiennent pas. Pour les expériences, utilise des cibles locales, des machines virtuelles ou un environnement de formation.

## 6. Lire un échange DNS

Le DNS associe notamment des noms de domaine à des enregistrements comme IPv4 (`A`) et IPv6 (`AAAA`). Un client envoie une requête à un résolveur. Le résolveur retourne une réponse pouvant contenir des enregistrements, une réponse négative ou un code d’erreur. Il peut aussi ne pas répondre dans le délai attendu.

### Schéma 3 — Requête et réponse DNS

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 330" role="img" aria-label="Échange DNS : le client envoie une requête au résolveur puis reçoit la réponse ; le diagramme donne l'ordre des messages sans prétendre montrer les paquets exacts d'une capture."><defs><marker id="wsa4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="wsg4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#72e4a5"/></marker></defs><style>.wst4{font:600 16px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.wss4{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.wsq4{fill:none;stroke:#66d9ff;stroke-width:3;marker-end:url(#wsa4)}.wsr4{fill:none;stroke:#72e4a5;stroke-width:3;marker-end:url(#wsg4)}.flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}@keyframes wsDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="68" y="26" width="220" height="64" rx="12" fill="#142437" stroke="#66d9ff" stroke-width="2"/><text x="178" y="52" class="wst4">Client</text><text x="178" y="72" class="wss4">192.0.2.10:port éphémère</text><rect x="592" y="26" width="220" height="64" rx="12" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="702" y="52" class="wst4">Résolveur DNS</text><text x="702" y="72" class="wss4">192.0.2.53:53</text><path class="wsq4 flow" d="M178 92V136H702V92"/><rect x="322" y="111" width="236" height="42" rx="9" fill="#1b2c40" stroke="#66d9ff"/><text x="440" y="128" class="wst4">Requête DNS</text><text x="440" y="144" class="wss4">A / AAAA / autre type</text><path class="wsr4 flow" d="M702 168V214H178V168"/><rect x="322" y="190" width="236" height="42" rx="9" fill="#173329" stroke="#72e4a5"/><text x="440" y="207" class="wst4">Réponse DNS</text><text x="440" y="223" class="wss4">Réponse, statut, enregistrements</text><text x="440" y="266" class="wst4">Dans Wireshark : appliquer `dns`, puis comparer requête et réponse.</text><text x="440" y="290" class="wss4">La réponse peut être vide, négative ou absente ; le statut compte autant que l’adresse.</text><text x="440" y="313" class="wss4">DNS peut aussi être chiffré ou transporté autrement selon la configuration du client.</text></svg></div>

### 6.1 Champs à examiner

Clique une requête DNS et cherche des éléments comme :

- **Transaction ID :** identifiant qui aide à faire correspondre une requête et sa réponse dans le contexte DNS concerné.
- **Flags :** indiquent notamment le type de message et certains comportements de résolution.
- **Questions :** nom demandé, type et classe.
- **Answer / Authority / Additional :** sections de réponse, d’autorité et d’informations supplémentaires, selon le message.
- **Response code (RCODE) :** indique le statut du traitement DNS, par exemple réponse normale ou nom inexistant.

Le seul fait de voir une requête DNS ne prouve pas que le nom a été résolu. Recherche la réponse correspondante, son statut et ses enregistrements. Si la réponse semble manquer, vérifie que le point de capture voit les deux sens de l’échange, que la capture a démarré assez tôt et que le client ne réutilise pas une réponse depuis le cache.

### 6.2 Port 53 et DNS chiffré

DNS classique utilise souvent UDP port 53, avec possibilité d’utiliser TCP port 53 dans certaines circonstances. Des technologies de DNS chiffré telles que DoH ou DoT peuvent modifier ce que l’on voit : la capture peut montrer une connexion TLS/HTTPS plutôt que les noms demandés dans les messages DNS classiques. Une capture ordinaire peut donc ne pas dévoiler le nom recherché si le protocole est chiffré ou si l’échange est fait par une application distincte.

### 6.3 Filtres DNS utiles

```text
dns
udp.port == 53
tcp.port == 53
dns.flags.response == 0
dns.flags.response == 1
dns.qry.name == "example.net"
```

Les champs et l’orthographe exacte peuvent dépendre du protocole et de la version. Utilise l’autocomplétion de la barre de filtre ou le menu contextuel d’un champ dans l’arborescence pour construire un filtre sûr plutôt que d’essayer de deviner des noms de champs inconnus.

## 7. Lire une session TCP

TCP est un protocole de transport orienté connexion. Avant d’échanger des données d’application, les deux côtés effectuent souvent une négociation en trois étapes, appelée **three-way handshake**. Elle sert à synchroniser l’état et les numéros de séquence initiaux.

### Schéma 4 — Négociation TCP

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 370" role="img" aria-label="Handshake TCP : SYN du client vers le serveur, SYN-ACK du serveur vers le client puis ACK du client vers le serveur ; ensuite des données et une fermeture possibles."><defs><marker id="wsa5" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="wsg5" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#72e4a5"/></marker><marker id="wsm5" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#ffc46b"/></marker></defs><style>.wst5{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.wss5{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.wsq5{fill:none;stroke:#66d9ff;stroke-width:3;marker-end:url(#wsa5)}.wsr5{fill:none;stroke:#72e4a5;stroke-width:3;marker-end:url(#wsg5)}.wsm5{fill:none;stroke:#ffc46b;stroke-width:3;marker-end:url(#wsm5)}.flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}@keyframes wsDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="45" y="20" width="230" height="54" rx="10" fill="#142437" stroke="#66d9ff" stroke-width="2"/><text x="160" y="42" class="wst5">Client</text><text x="160" y="60" class="wss5">Port source éphémère</text><rect x="605" y="20" width="230" height="54" rx="10" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="720" y="42" class="wst5">Serveur</text><text x="720" y="60" class="wss5">Port de service, ex. 443</text><path class="wsq5 flow" d="M160 80V106H720V80"/><rect x="364" y="88" width="152" height="34" rx="8" fill="#172a40" stroke="#66d9ff"/><text x="440" y="110" class="wst5">SYN</text><path class="wsr5 flow" d="M720 131V156H160V131"/><rect x="350" y="138" width="180" height="34" rx="8" fill="#173329" stroke="#72e4a5"/><text x="440" y="160" class="wst5">SYN, ACK</text><path class="wsq5 flow" d="M160 181V206H720V181"/><rect x="364" y="188" width="152" height="34" rx="8" fill="#172a40" stroke="#66d9ff"/><text x="440" y="210" class="wst5">ACK</text><path class="wsm5 flow" d="M160 232V258H720V232"/><rect x="330" y="240" width="220" height="34" rx="8" fill="#352919" stroke="#ffc46b"/><text x="440" y="262" class="wst5">Données applicatives</text><text x="440" y="305" class="wss5">Le handshake confirme l’établissement TCP, pas la réussite de l’application.</text><text x="440" y="327" class="wss5">Des retransmissions, des RST ou un silence après SYN fournissent des indices, pas un verdict isolé.</text><text x="440" y="349" class="wss5">Une fermeture normale implique généralement FIN/ACK dans les directions appropriées, ou parfois RST.</text></svg></div>

### 7.1 SYN, SYN-ACK et ACK

- **SYN :** le client demande l’établissement de la connexion et présente son numéro de séquence initial.
- **SYN-ACK :** le serveur accepte la demande TCP et acquitte le SYN du client, tout en présentant son propre numéro de séquence.
- **ACK :** le client acquitte le SYN du serveur. La connexion TCP est alors normalement établie.

Une fois la connexion créée, les données applicatives peuvent circuler. Une connexion établie ne signifie pas que la connexion TLS, l’authentification, la requête HTTP ou le traitement métier réussira. Chaque étape doit être observée séparément.

### 7.2 Reconnaître des indices courants

- Plusieurs SYN du client sans SYN-ACK visible : la réponse est absente du point de capture, retardée, filtrée, perdue ou emprunte un autre chemin ; ne désigne pas automatiquement le pare-feu comme responsable.
- SYN suivi rapidement d’un RST : une machine a activement réinitialisé la tentative TCP. Identifie l’émetteur du RST et vérifie le contexte.
- Handshake TCP réussi mais application en échec : examine la suite, par exemple TLS, certificat, requête ou réponse applicative.
- Retransmission TCP : un segment semble avoir dû être retransmis selon l’analyse de Wireshark. Cela peut refléter une perte, un retard, un réordonnancement ou une particularité de capture.
- Dup ACK / out-of-order : c’est un indice d’ordre ou d’acquittement à examiner avec la séquence complète, pas une preuve automatique de défaillance du réseau.

Wireshark peut afficher des messages d’analyse TCP tels que retransmission, retransmission rapide, paquet hors ordre ou ACK dupliqué. Lis-les dans leur contexte : la capture peut elle-même manquer de paquets, présenter un horodatage inhabituel ou se situer à un endroit qui observe un seul côté de l’échange.

### 7.3 Fermeture de connexion

La fermeture TCP peut être effectuée à travers des segments FIN et ACK. Un RST réinitialise la connexion de façon abrupte. Une capture tronquée ou prise au milieu d’un flux peut ne contenir ni handshake ni fermeture complète. Évite donc de considérer qu’un échange est « cassé » uniquement parce que le premier et le dernier paquet ne sont pas présents.

### 7.4 Suivre un flux

Sélectionne un paquet d’une conversation TCP, puis utilise **Analyze → Follow → TCP Stream** (ou l’option équivalente du menu contextuel). Wireshark isole alors le flux et peut présenter les données réassemblées selon le protocole. C’est pratique pour comprendre l’ordre de la conversation.

Pour HTTPS/TLS, le contenu applicatif est généralement chiffré. Sans secrets de session appropriés et dans les limites du protocole, suivre le flux ne révèle pas nécessairement le texte HTTP. Ne cherche pas à extraire ou à divulguer des informations privées d’une capture sans autorisation.

## 8. Les protocoles de base à reconnaître

### 8.1 ARP

ARP permet à un hôte IPv4 de rechercher l’adresse MAC associée à une adresse IPv4 sur un lien local. Une requête ARP est souvent diffusée dans le segment. Une réponse indique normalement l’adresse matérielle annoncée pour l’IP recherchée.

Filtres :

```text
arp
arp.opcode == 1
arp.opcode == 2
```

Une requête ARP sans réponse peut indiquer que l’hôte recherché n’est pas joignable sur le segment, que l’IP ou le VLAN est incorrect, ou que la réponse n’est pas visible dans la capture. Vérifie d’abord le sous-réseau, la passerelle, la table ARP et le point de capture. Une entrée ARP annoncée par un appareil ne garantit pas à elle seule que cet appareil est légitime ; dans un réseau de production, les mécanismes de protection adaptés peuvent être nécessaires.

### 8.2 ICMP et ping

ICMP sert notamment à signaler certains états réseau. La commande `ping` utilise souvent ICMP Echo Request et Echo Reply lorsque le réseau et la cible l’autorisent. Une réponse confirme qu’un paquet ICMP de ce type a effectué le trajet attendu jusqu’au répondant et retour au point d’origine, mais ne prouve pas que le port TCP d’une application fonctionne.

Filtres IPv4 usuels :

```text
icmp
icmp.type == 8
icmp.type == 0
```

Dans le cas d’IPv6, cherche le protocole ICMPv6 (`icmpv6`). Certains appareils ou pare-feu bloquent les réponses Echo tout en autorisant d’autres services ; l’absence de ping ne démontre donc pas à elle seule que l’hôte est hors ligne.

### 8.3 DHCP

DHCP permet à un client IPv4 d’obtenir une configuration réseau, par exemple une adresse IP, un masque, une passerelle et des serveurs DNS. Les noms historiques **Discover, Offer, Request, Acknowledgment** décrivent un scénario courant, souvent résumé en DORA. La séquence exacte peut différer lors du renouvellement, d’une réutilisation de bail ou d’autres cas.

Filtre :

```text
bootp
```

Selon la version, le dissector et les préférences, le protocole peut aussi apparaître sous un nom DHCP. Observe les messages du client, les réponses du serveur et les options proposées. Si un client n’obtient pas de bail, recherche les offres, les confirmations et les identifiants de transaction. Une capture côté client peut ne pas voir toutes les étapes qui se déroulent sur un relais ou un segment différent.

### 8.4 HTTP et HTTPS

HTTP décrit des échanges requête/réponse applicatifs. Le HTTP non chiffré peut apparaître dans la capture si le trafic utilise ce protocole et le point d’observation voit le contenu. HTTPS associe HTTP à TLS : le contenu applicatif est normalement chiffré, mais les adresses IP, ports, volumes, timings et certains métadonnées peuvent rester observables.

Filtres possibles :

```text
http
tls
tcp.port == 80
tcp.port == 443
```

Le filtre de port identifie un numéro de port, pas le contenu ou l’intention de l’application. Les navigateurs peuvent utiliser HTTP/3 sur QUIC, généralement transporté sur UDP. Ainsi, un filtre `tcp.port == 443` peut ne pas montrer l’intégralité du trafic HTTPS si le navigateur utilise HTTP/3. Pour débuter, concentre-toi sur une capture contrôlée plutôt que de supposer qu’un site web doit produire exactement les mêmes paquets sur chaque ordinateur.

### 8.5 UDP

UDP envoie des datagrammes sans établir de session comparable au handshake TCP. Il ne fournit pas à lui seul de retransmission ni d’acquittement de livraison. Plusieurs protocoles s’appuient dessus, dont DNS classique et DHCP. L’application ou un protocole supérieur doit définir le comportement en cas de perte ou de délai.

Filtre de base : `udp`. Puis affine avec un port, une adresse ou un nom de protocole lorsque c’est approprié.

## 9. Les filtres : ta compétence la plus utile

Une capture réelle peut contenir des milliers ou des millions de paquets. Les filtres servent à concentrer ton attention sur l’ensemble pertinent. Il faut distinguer deux familles : **filtre de capture** et **filtre d’affichage**.

### Schéma 5 — Filtre de capture contre filtre d’affichage

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 330" role="img" aria-label="Différence entre filtre de capture appliqué avant l'enregistrement des paquets et filtre d'affichage appliqué après capture sur la liste visible."><defs><marker id="wsa6" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker></defs><style>.wst6{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.wss6{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.wsp6{stroke:#66d9ff;stroke-width:2.7;fill:none;marker-end:url(#wsa6)}.flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}@keyframes wsDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="28" y="35" width="174" height="84" rx="12" fill="#142437" stroke="#66d9ff" stroke-width="2"/><text x="115" y="65" class="wst6">Interface</text><text x="115" y="85" class="wss6">Paquets observés</text><path class="wsp6 flow" d="M207 77H263"/><rect x="270" y="35" width="230" height="84" rx="12" fill="#332719" stroke="#ffc46b" stroke-width="2"/><text x="385" y="61" class="wst6">Filtre de capture</text><text x="385" y="81" class="wss6">Syntaxe libpcap</text><text x="385" y="100" class="wss6">Avant écriture du fichier</text><path class="wsp6 flow" d="M505 77H561"/><rect x="568" y="35" width="284" height="84" rx="12" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="710" y="61" class="wst6">Fichier capturé</text><text x="710" y="81" class="wss6">.pcapng / paquets retenus</text><text x="710" y="100" class="wss6">Les paquets rejetés ne sont pas là</text><path class="wsp6 flow" d="M710 122V176"/><rect x="568" y="183" width="284" height="90" rx="12" fill="#202343" stroke="#a5a4ff" stroke-width="2"/><text x="710" y="210" class="wst6">Filtre d’affichage</text><text x="710" y="231" class="wss6">Syntaxe Wireshark</text><text x="710" y="250" class="wss6">Masque ou montre les paquets</text><path class="wsp6 flow" d="M565 229H500"/><rect x="270" y="183" width="222" height="90" rx="12" fill="#172a40" stroke="#66d9ff" stroke-width="2"/><text x="381" y="210" class="wst6">Analyse ciblée</text><text x="381" y="231" class="wss6">Requête, protocole, hôte</text><text x="381" y="250" class="wss6">Retour possible au fichier entier</text><text x="440" y="309" class="wss6">Astuce débutant : commence souvent sans filtre de capture, puis affine avec les filtres d’affichage.</text></svg></div>

### 9.1 Filtre d’affichage

Le filtre d’affichage s’applique aux paquets présents dans la capture ouverte. Il masque les paquets qui ne correspondent pas, mais ne les supprime pas du fichier. La syntaxe est celle de Wireshark. La barre est souvent verte lorsque l’expression est valide et rouge lorsqu’elle contient une erreur, selon l’apparence choisie.

Exemples pratiques :

| But | Filtre d’affichage |
|---|---|
| Voir uniquement DNS | `dns` |
| Voir uniquement ARP | `arp` |
| Voir ICMP IPv4 | `icmp` |
| Paquets concernant une IP donnée | `ip.addr == 192.0.2.10` |
| Paquets dont la source est cette IP | `ip.src == 192.0.2.10` |
| Paquets dont la destination est cette IP | `ip.dst == 192.0.2.10` |
| TCP sur un port donné | `tcp.port == 443` |
| UDP sur le port DNS classique | `udp.port == 53` |
| SYN TCP avec bit ACK non activé | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| Retransmissions TCP repérées par l’analyse | `tcp.analysis.retransmission` |
| Connexion TCP/flux identifié | `tcp.stream eq 0` |
| TLS | `tls` |

Les valeurs IP du tableau sont des exemples documentaires. Remplace-les par l’adresse réellement observée dans ton laboratoire. Le numéro de stream dépend de la capture et n’est pas une valeur universelle.

Les opérateurs courants comprennent `==`, `!=`, `>`, `<`, `>=`, `<=`, `&&` (ET), `||` (OU) et `!` (NON). Les mots-clés `contains` et `matches` permettent d’autres recherches lorsque le champ les accepte. Les règles entre opérateurs suivent une grammaire spécifique ; emploie des parenthèses si l’expression combine plusieurs conditions.

Exemple :

```text
ip.addr == 192.0.2.10 && (dns || tcp.port == 443)
```

Cette expression affiche les paquets liés à cette IP qui sont reconnus comme DNS ou qui correspondent à TCP sur le port 443. Le sens de `ip.addr` est large : il correspond généralement à la source ou à la destination. Utilise `ip.src` ou `ip.dst` si tu as besoin d’un seul sens.

### 9.2 Filtre de capture

Le filtre de capture, lui, est appliqué pendant l’acquisition. Il écarte les paquets qui ne correspondent pas avant leur enregistrement dans le fichier. Sa syntaxe est celle du langage de filtre libpcap, qui **n’est pas** la syntaxe du filtre d’affichage.

Exemples :

| But | Filtre de capture |
|---|---|
| Hôte source ou destination | `host 192.0.2.10` |
| Paquets vers ou depuis une IP, côté source seulement | `src host 192.0.2.10` |
| Trafic TCP sur le port 443 | `tcp port 443` |
| Trafic UDP sur port 53 | `udp port 53` |
| Trafic ICMP | `icmp` |
| Réseau IPv4 donné | `net 192.0.2.0/24` |
| Exclure le port SSH (selon l’objectif de capture) | `not port 22` |

N’écris pas `ip.addr == ...` dans un champ de filtre de capture en supposant que les deux langages sont identiques. Si tu appliques par erreur un filtre trop restrictif, les paquets rejetés ne seront pas présents dans le fichier : effacer le filtre d’affichage ne les fera pas revenir. C’est pourquoi, au début, il est souvent préférable de capturer sans filtre de capture puis de filtrer l’analyse.

### 9.3 Construire un filtre au lieu de le mémoriser

Lorsque tu trouves un champ utile dans le détail d’un paquet, fais un clic droit dessus et cherche des options comme **Apply as Filter** ou **Prepare as Filter**. Wireshark peut alors remplir la barre avec le champ et la valeur sélectionnés. Cette méthode réduit les erreurs de nom de champ et te permet d’apprendre progressivement la syntaxe.

Si l’expression n’est pas valide :

1. vérifie que tu es dans le filtre d’affichage et non le champ de capture ;
2. vérifie le nom du champ, les guillemets et l’opérateur ;
3. essaie une expression plus simple comme `dns` ou `tcp` ;
4. utilise l’autocomplétion et la documentation officielle du filtre ;
5. élimine un élément à la fois jusqu’à identifier l’erreur.

## 10. Méthode de dépannage reproductible

### Schéma 6 — Une méthode de diagnostic

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 270" role="img" aria-label="Méthode de dépannage en six étapes : question, point de capture, reproduction, filtre, comparaison requête/réponse, conclusion avec limites."><defs><marker id="wsa7" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker></defs><style>.wst7{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.wss7{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.wsarr7{stroke:#66d9ff;stroke-width:2.8;fill:none;marker-end:url(#wsa7)}.flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}@keyframes wsDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="22" y="38" width="126" height="82" rx="10" fill="#142437" stroke="#66d9ff" stroke-width="2"/><text x="85" y="64" class="wst7">1. Question</text><text x="85" y="84" class="wss7">Symptôme exact</text><text x="85" y="101" class="wss7">Heure et cible</text><path class="wsarr7 flow" d="M150 79H166"/><rect x="173" y="38" width="126" height="82" rx="10" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="236" y="64" class="wst7">2. Capture</text><text x="236" y="84" class="wss7">Bonne interface</text><text x="236" y="101" class="wss7">Bon point réseau</text><path class="wsarr7 flow" d="M301 79H317"/><rect x="324" y="38" width="126" height="82" rx="10" fill="#332719" stroke="#ffc46b" stroke-width="2"/><text x="387" y="64" class="wst7">3. Reproduire</text><text x="387" y="84" class="wss7">Une action</text><text x="387" y="101" class="wss7">à la fois</text><path class="wsarr7 flow" d="M452 79H468"/><rect x="475" y="38" width="126" height="82" rx="10" fill="#202343" stroke="#a5a4ff" stroke-width="2"/><text x="538" y="64" class="wst7">4. Filtrer</text><text x="538" y="84" class="wss7">Protocole / hôte</text><text x="538" y="101" class="wss7">Flux pertinent</text><path class="wsarr7 flow" d="M603 79H619"/><rect x="626" y="38" width="126" height="82" rx="10" fill="#142437" stroke="#66d9ff" stroke-width="2"/><text x="689" y="64" class="wst7">5. Comparer</text><text x="689" y="84" class="wss7">Requête / réponse</text><text x="689" y="101" class="wss7">Temps / statut</text><path class="wsarr7 flow" d="M754 79H770"/><rect x="777" y="38" width="81" height="82" rx="10" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="817" y="64" class="wst7">6. Conclure</text><text x="817" y="84" class="wss7">Preuve +</text><text x="817" y="101" class="wss7">limites</text><path d="M817 123V166H85V126" fill="none" stroke="#59718c" stroke-width="2" stroke-dasharray="5 5" marker-end="url(#wsa7)"/><text x="440" y="194" class="wst7">Si le résultat est ambigu, change le point de capture ou reproduis le test.</text><text x="440" y="218" class="wss7">Un paquet absent dans une capture peut être perdu, filtré ou visible ailleurs.</text><text x="440" y="239" class="wss7">Une capture partielle ne prouve pas, à elle seule, qu’un équipement précis est responsable.</text></svg></div>

Une méthode rigoureuse évite de confondre corrélation et causalité. La démarche proposée est la suivante.

### Étape 1 — Formuler le symptôme

Écris précisément ce qui ne fonctionne pas : application, action, cible, heure, réseau utilisé, message d’erreur et fréquence. « Internet ne marche pas » est trop vague. « Depuis le poste A, la résolution de `intranet.example` échoue depuis 10 h 15, tandis que l’accès par IP fonctionne » donne un point de départ testable.

### Étape 2 — Choisir le point de capture

Sur le poste client, tu peux observer ce qu’il transmet et ce qu’il reçoit. Sur le serveur, tu peux observer ce qui lui parvient et ce qu’il renvoie. Pour localiser une perte dans un réseau complexe, il peut être nécessaire de comparer plusieurs captures et de synchroniser correctement les horloges. Les paquets capturés aux deux extrémités peuvent sembler différents à cause du NAT, du routage, de la segmentation, de la désactivation matérielle des sommes de contrôle ou des mécanismes d’agrégation.

### Étape 3 — Reproduire une seule action

Démarre la capture avant le test. Reproduis le problème une seule fois si possible. Note l’heure. Arrête la capture pour éviter d’ajouter du trafic sans rapport. Si le problème est intermittent, répète le même test et conserve séparément les essais réussis et échoués.

### Étape 4 — Réduire le bruit

Commence par un filtre simple : par exemple `dns`, `icmp`, `tcp` ou l’adresse IP concernée. Puis réduis encore par port ou par flux. Ne combine pas immédiatement une dizaine de conditions, car il sera plus difficile de savoir laquelle exclut les paquets qui t’intéressent.

### Étape 5 — Suivre la chaîne logique

Pour une application web, sépare les étapes : résolution DNS, sélection d’une adresse, handshake TCP si utilisé, handshake TLS, requête applicative et réponse. Pour DHCP, cherche les messages de négociation. Pour un accès local IPv4, ARP peut être pertinent. Pour une connectivité IP, ICMP peut offrir un indice, sans être un test complet du service applicatif.

### Étape 6 — Formuler une conclusion limitée aux preuves

Une bonne conclusion dit : « Sur l’interface client, trois SYN ont été vus vers l’adresse X et aucun SYN-ACK n’est apparu avant la fin de la capture. Il faut comparer avec une capture côté serveur ou les journaux du pare-feu pour localiser la cause. »

Une mauvaise conclusion dit : « Le pare-feu bloque le serveur », lorsque tu n’as vu que l’absence de réponse sur le client. La seconde phrase dépasse ce que les données prouvent.

## 11. Atelier guidé : diagnostiquer un accès web

### Schéma 7 — Étapes d’un accès web et points de rupture possibles

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 310" role="img" aria-label="Exemple de résolution d'un problème web avec client, DNS, serveur web : requête DNS puis connexion TCP/TLS ; l'absence de réponse DNS et l'absence de SYN-ACK orientent vers des pistes différentes."><defs><marker id="wsa8" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="wsg8" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#72e4a5"/></marker></defs><style>.wst8{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.wss8{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.wsq8{stroke:#66d9ff;stroke-width:2.7;fill:none;marker-end:url(#wsa8)}.wsr8{stroke:#72e4a5;stroke-width:2.7;fill:none;marker-end:url(#wsg8)}.flow{stroke-dasharray:8 7;animation:wsDash 2s linear infinite}@keyframes wsDash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="25" y="22" width="210" height="54" rx="10" fill="#142437" stroke="#66d9ff" stroke-width="2"/><text x="130" y="44" class="wst8">Client</text><text x="130" y="62" class="wss8">Navigateur</text><rect x="335" y="22" width="210" height="54" rx="10" fill="#332719" stroke="#ffc46b" stroke-width="2"/><text x="440" y="44" class="wst8">Résolveur DNS</text><text x="440" y="62" class="wss8">Port généralement 53</text><rect x="645" y="22" width="210" height="54" rx="10" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="750" y="44" class="wst8">Serveur web</text><text x="750" y="62" class="wss8">IP et port accessibles</text><path class="wsq8 flow" d="M130 82V111H440V82"/><text x="285" y="104" class="wss8">Requête DNS</text><path class="wsr8 flow" d="M440 134V153H130V134"/><text x="285" y="148" class="wss8">Réponse DNS</text><path class="wsq8 flow" d="M130 176V208H750V82"/><text x="440" y="200" class="wss8">SYN vers le serveur (si résolution et choix d’adresse terminés)</text><path class="wsr8 flow" d="M750 229V247H130V229"/><text x="440" y="242" class="wss8">SYN-ACK attendu si TCP aboutit (sinon, observer retransmissions / RST)</text><text x="440" y="278" class="wst8">Séparer les étapes : résolution → TCP → TLS → requête applicative.</text><text x="440" y="296" class="wss8">Un échec dans une étape ne doit pas être attribué automatiquement à la suivante.</text></svg></div>

### 11.1 Scénario A : le nom ne se résout pas

**Symptôme :** le navigateur ne peut pas atteindre le site par nom, mais le message d’erreur ne précise pas toujours l’origine.

**Démarche :**

1. Lance une capture sur l’interface du client.
2. Reproduis une seule résolution DNS dans ton laboratoire.
3. Applique `dns` ; si rien n’apparaît, examine la capture sans filtre et vérifie que le trafic attendu est visible.
4. Cherche la requête : nom, type (`A`, `AAAA` ou autre) et destination.
5. Cherche la réponse, son statut et les enregistrements.
6. Si aucune réponse n’est visible, vérifie le point de capture, le cache, l’utilisation d’un résolveur chiffré et les journaux du résolveur.

**Interprétation :** une réponse négative peut être une réponse valide du DNS signifiant que le nom ou le type demandé ne produit pas de résultat. Une requête sans réponse visible a plusieurs causes possibles. Vérifie avant d’accuser le serveur DNS.

### 11.2 Scénario B : DNS fonctionne, mais la connexion n’aboutit pas

**Symptôme :** le nom se résout, mais le navigateur n’arrive pas à se connecter.

**Démarche :**

1. Identifie l’adresse choisie par l’application ; un nom peut avoir plusieurs adresses.
2. Cherche les paquets TCP ou le trafic correspondant au service.
3. Vérifie si le client émet un SYN.
4. Cherche SYN-ACK ou RST en réponse.
5. Note les retransmissions et les temps d’attente.
6. Si possible, réalise une capture au niveau du serveur et compare les deux côtés.

**Interprétation :** si le client émet des SYN qui ne reçoivent pas de réponse visible, la perte peut se trouver à plusieurs endroits du chemin, ou la réponse peut suivre une route asymétrique non observée. Si un RST arrive, recherche quel hôte l’a envoyé. Si le handshake réussit, poursuis l’analyse au niveau supérieur.

### 11.3 Scénario C : TCP fonctionne, mais la page échoue

Après un handshake TCP réussi, TLS peut échouer à cause d’une version ou suite cryptographique non compatible, d’un problème de certificat, d’un nom de serveur, d’une politique ou d’un intermédiaire réseau. Si TLS s’établit, une erreur peut encore provenir de l’application, d’une authentification, d’un proxy ou d’une réponse HTTP.

Observe le premier moment où le comportement s’écarte de l’attendu. À moins que le contenu ne soit disponible pour analyse, la capture TLS peut ne révéler que les messages de négociation et les métadonnées. Complète le diagnostic avec les journaux applicatifs et les outils système autorisés.

## 12. Statistiques utiles

Les statistiques résument une capture sans exiger la lecture manuelle de chaque paquet. Selon la version et la configuration, le menu **Statistics** propose des outils tels que :

- **Protocol Hierarchy :** répartition du trafic par protocole et couches reconnues ;
- **Conversations :** statistiques par paire d’extrémités, avec paquets, octets, durée et débit estimé ;
- **Endpoints :** synthèse par adresse de destination ;
- **I/O Graphs :** évolution du nombre de paquets ou d’autres compteurs dans le temps ;
- **Packet Lengths :** distribution des tailles de paquets ;
- statistiques spécifiques à un protocole lorsqu’elles sont prises en charge.

### 12.1 Protocol Hierarchy

Cette vue aide à répondre à « quels protocoles occupent le fichier ? » Elle montre les protocoles décodés et leurs proportions. Le résultat reflète la capture et le décodage de Wireshark, pas nécessairement tout le trafic réel du réseau. Une capture filtrée ou prise à une seule interface peut donner une image très incomplète.

### 12.2 Conversations et Endpoints

Les conversations aident à identifier les échanges qui représentent la plus grande part des octets ou des paquets. Les endpoints montrent quels hôtes apparaissent le plus dans la capture. Cela peut aider à trouver le serveur le plus sollicité, un flux volumineux ou une adresse inattendue dans un laboratoire.

Ne transforme pas automatiquement une grande quantité d’octets en preuve d’attaque. Sauvegardes, mises à jour, vidéo, transfert légitime ou erreurs applicatives peuvent aussi provoquer des volumes importants. Le contexte, les durées, les destinations et la comparaison avec le fonctionnement normal sont essentiels.

### 12.3 Expert Information

La vue **Analyze → Expert Information** peut signaler des événements que Wireshark considère notables, notamment certaines anomalies TCP, des retransmissions ou des avertissements de protocole. Le niveau et le type des alertes dépendent des paquets capturés et des dissectors. Ce tableau n’est pas un scanner de vulnérabilités et tous les avertissements n’impliquent pas un incident de sécurité.

Lis chaque événement dans le détail du paquet, puis compare-le à la conversation et aux messages précédents/suivants. Vérifie aussi si la capture présente des pertes ou si elle a été réalisée depuis un point particulier du chemin.

## 13. Erreurs fréquentes au début

### 13.1 Confondre filtre de capture et filtre d’affichage

C’est l’erreur qui peut faire perdre des preuves. Le filtre de capture supprime de la collecte les paquets qui ne correspondent pas. Le filtre d’affichage les masque temporairement. Si une réponse manque à cause d’un filtre de capture, retirer le filtre d’affichage n’aidera pas ; il faudra refaire la capture sans cette restriction.

### 13.2 Penser que chaque paquet correspond à une requête entière

Un message applicatif peut être réparti sur plusieurs segments TCP. Wireshark peut réassembler des parties du flux et présenter des champs générés pour l’analyse. Un paquet TCP unique ne correspond pas nécessairement à une requête HTTP complète ou à un message applicatif entier.

### 13.3 Accuser une adresse à cause d’un nom affiché

La résolution de noms peut remplacer visuellement une adresse par un nom. Ce nom dépend des mécanismes de résolution disponibles et n’est pas forcément la preuve de l’identité d’une machine. Lors d’un diagnostic, conserve l’adresse IP, vérifie le contexte DNS et désactive temporairement certaines résolutions de noms si elles rendent les données ambiguës.

### 13.4 Croire que le rouge ou les couleurs sont une alerte de sécurité

Les couleurs du panneau des paquets sont surtout des règles d’affichage. Elles peuvent distinguer des protocoles ou certains indicateurs et sont configurables. Une ligne colorée ne veut pas automatiquement dire « attaque » ou « panne ». Lis d’abord le protocole, les champs et le contexte.

### 13.5 Interpréter un checksum incorrect comme une corruption certaine

Sur une machine qui transmet, le calcul de checksum peut être effectué par la carte réseau après que Wireshark a observé le paquet ; le paquet capturé peut alors sembler porter un checksum incorrect. Les mécanismes d’agrégation ou de segmentation peuvent également modifier la forme des paquets visibles avant qu’ils ne soient réellement envoyés. Une alerte de checksum doit donc être comparée à d’autres observations, notamment côté réception.

### 13.6 Oublier les limites de capture

Une capture peut être limitée en nombre de paquets, en longueur de paquet, par une règle d’interface ou par un filtre. Une capture tronquée peut rendre certains champs applicatifs indisponibles. Avant de conclure, consulte les propriétés du fichier, les statistiques de capture et les éventuels avertissements de paquets limités.

## 14. Sécurité, confidentialité et hygiène des captures

Une capture peut contenir bien davantage que des informations réseau abstraites. Certains protocoles envoient du contenu en clair ; même avec du chiffrement, des métadonnées restent parfois visibles. Traite les fichiers `.pcapng` comme des données potentiellement sensibles.

Règles pratiques :

- capture la durée et le périmètre strictement nécessaires ;
- évite de collecter les données d’autres utilisateurs sans autorisation explicite ;
- stocke les fichiers dans un emplacement à accès contrôlé ;
- supprime ou anonymise les données sensibles avant de partager une capture ;
- partage le minimum de paquets qui permet de démontrer le problème ;
- ne publie pas des captures internes dans un forum public sans revue préalable ;
- garde le nom du fichier neutre et documente l’interface, l’heure et l’objectif du test.

L’anonymisation n’est pas triviale : remplacer une adresse IP sans cohérence peut casser le sens de la capture ou laisser d’autres identifiants personnels visibles. Pour apprendre, privilégie les jeux de données de formation et les captures fabriquées dans un laboratoire.

## 15. Exercices pratiques

### Exercice 1 — Filtrer une capture

Ouvre une capture de laboratoire. Affiche uniquement DNS, puis seulement ICMP, puis le trafic d’un hôte donné. Pour chacun, note le nombre de paquets visibles avant et après l’application du filtre. Efface les filtres pour revenir à la capture entière.

**Question :** les filtres ont-ils supprimé des paquets du fichier ?

### Exercice 2 — Identifier un handshake TCP

Filtre `tcp`, sélectionne une connexion vers un service autorisé et repère SYN, SYN-ACK puis ACK lorsqu’ils sont présents. Note les IP et ports dans chaque sens. Observe si des données suivent l’établissement.

**Question :** pourquoi un handshake terminé ne prouve-t-il pas qu’une page web se chargera correctement ?

### Exercice 3 — Requête DNS sans réponse visible

Dans un laboratoire, capture une requête DNS et cherche la réponse. Si aucune réponse n’est visible, liste au moins trois hypothèses autres qu’une panne du serveur DNS. Précise comment les vérifier.

### Exercice 4 — Lire les statistiques

Ouvre Protocol Hierarchy et Conversations. Identifie le protocole dominant et la conversation qui transporte le plus d’octets. Explique pourquoi ces résultats décrivent le fichier capturé, pas nécessairement l’ensemble du réseau.

### Exercice 5 — Capture de comparaison

Avec autorisation et lorsque c’est possible, capture le même test depuis le client puis depuis le serveur. Compare l’apparition du SYN, du SYN-ACK et de la requête applicative. Tiens compte des différences d’horloge et des modifications apportées par le réseau.

## 16. Quiz de validation

**1. Wireshark sert principalement à :**
A. remplacer un routeur ; B. capturer et analyser le trafic visible ; C. attribuer automatiquement une IP ; D. supprimer les malwares.

**2. Quelle vue affiche une arborescence de champs pour le paquet sélectionné ?**
A. Packet Details ; B. Endpoints ; C. Capture Options ; D. Conversations.

**3. Quel filtre d’affichage isole le DNS reconnu ?**
A. `dns` ; B. `host dns` ; C. `capture dns` ; D. `port == dns`.

**4. Quel filtre capture correspond au trafic TCP sur le port 443 ?**
A. `tcp.port == 443` ; B. `tcp port 443` ; C. `port.tcp eq 443` ; D. `tcp && 443`.

**5. Dans une session TCP classique, quelle séquence forme le handshake ?**
A. ACK, FIN, SYN ; B. SYN, SYN-ACK, ACK ; C. DNS, ARP, ACK ; D. SYN, RST, FIN.

**6. L’absence d’un paquet dans une capture prouve toujours qu’il n’a pas été envoyé.** Vrai ou faux ?

**7. Le port 443 prouve toujours que le contenu est HTTPS.** Vrai ou faux ?

**8. Quel protocole aide un client IPv4 à trouver la MAC d’un hôte local ?**
A. DNS ; B. ARP ; C. HTTP ; D. TLS.

**9. Une réponse DNS négative signifie nécessairement que le serveur DNS est hors service.** Vrai ou faux ?

**10. Un handshake TCP réussi prouve que l’application fonctionne correctement.** Vrai ou faux ?

### Corrigé

1. **B.** Wireshark analyse le trafic visible depuis un point de capture.
2. **A.** Packet Details présente les protocoles et les champs du paquet choisi.
3. **A.** `dns` est un filtre d’affichage courant.
4. **B.** La syntaxe libpcap de capture utilise `tcp port 443`.
5. **B.** SYN, SYN-ACK puis ACK.
6. **Faux.** Mauvaise interface, filtre, perte, chemin alternatif ou capture tardive peuvent expliquer l’absence.
7. **Faux.** Le numéro de port ne garantit pas le protocole applicatif.
8. **B.** ARP réalise la résolution IPv4 vers MAC sur le réseau local.
9. **Faux.** Une réponse négative peut être une réponse DNS valide.
10. **Faux.** TLS, HTTP ou l’application peuvent encore échouer ensuite.

## 17. Fiche mémo

| Besoin | Premier réflexe |
|---|---|
| Comprendre un paquet | Cliquer la ligne et ouvrir Packet Details |
| Voir le trafic DNS reconnu | `dns` |
| Voir ARP | `arp` |
| Voir un ping IPv4 | `icmp` |
| Isoler une adresse IPv4 | `ip.addr == X.X.X.X` |
| Voir un SYN initial | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| Voir des retransmissions analysées | `tcp.analysis.retransmission` |
| Examiner une conversation | Analyze → Follow → TCP Stream |
| Trouver les plus gros échanges | Statistics → Conversations |
| Résumer les protocoles | Statistics → Protocol Hierarchy |
| Rechercher un problème | Question → bonne interface → reproduire → filtrer → comparer → conclusion limitée |

## 18. Glossaire

- **Capture :** observation et enregistrement de paquets sur une interface ou un point de réseau.
- **Dissector :** composant qui décode les champs d’un protocole reconnu.
- **Filtre de capture :** sélection appliquée au moment de l’acquisition.
- **Filtre d’affichage :** sélection visuelle des paquets d’un fichier ou de la session affichée.
- **Flux TCP :** conversation TCP identifiée par les extrémités et suivie par Wireshark.
- **Handshake :** échange initial qui établit une connexion ou négocie un protocole.
- **Pcapng :** format de fichier de capture utilisé nativement par Wireshark.
- **Retransmission :** nouvel envoi d’un segment TCP quand le protocole estime que la livraison précédente doit être répétée.
- **Point de capture :** endroit du réseau où le trafic est observé.
- **Encapsulation :** insertion des données d’une couche dans l’unité transportée par la couche inférieure.
- **TAP / SPAN :** moyens de fournir une copie du trafic d’un segment à un outil de supervision.
- **TLS :** protocole cryptographique utilisé notamment pour protéger les communications d’applications.

## 19. Pour progresser après le niveau débutant

Quand tu seras à l’aise avec les filtres simples, les champs IP, les requêtes DNS et les handshakes TCP, le niveau intermédiaire pourra approfondir : analyse de TCP (SEQ/ACK, fenêtre, SACK, retransmissions et réordonnancement), lecture de TLS, DHCP et ARP plus détaillés, chronologie des requêtes, métriques de temps, captures sur plusieurs interfaces, `tshark` en ligne de commande, export de champs et méthode de dépannage multi-points.

Le bon objectif n’est pas de mémoriser toutes les colonnes de Wireshark. C’est de pouvoir expliquer un échange réel, justifier chaque hypothèse par les paquets pertinents et reconnaître ce que la capture ne permet pas encore de conclure.

## 20. Références officielles

- [Wireshark User’s Guide](https://www.wireshark.org/docs/wsug_html/) — guide utilisateur général.
- [Capturing Live Network Data](https://www.wireshark.org/docs/wsug_html_chunked/ChapterCapture.html) — démarrage, interfaces et capture.
- [Filtering Packets While Viewing](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkDisplayFilterSection.html) — filtres d’affichage.
- [Filtering While Capturing](https://www.wireshark.org/docs/wsug_html_chunked/ChCapCaptureFilterSection.html) — filtres de capture et syntaxe libpcap.
- [Packet List](https://www.wireshark.org/docs/wsug_html_chunked/ChUsePacketListPaneSection.html), [Packet Details](https://www.wireshark.org/docs/wsug_html_chunked/ChUsePacketDetailsPaneSection.html) et [Packet Bytes](https://www.wireshark.org/docs/wsug_html_chunked/ChUsePacketBytesPaneSection.html) — les zones d’analyse de l’interface.
- [Following Protocol Streams](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvFollowStreamSection.html) — suivre une conversation.
- [Statistics](https://www.wireshark.org/docs/wsug_html_chunked/ChStatistics.html) et [Conversations](https://www.wireshark.org/docs/wsug_html_chunked/ChStatConversations.html) — statistiques de trafic.
- [TShark Manual](https://www.wireshark.org/docs/man-pages/tshark.html) — analyse de captures en ligne de commande.

Les noms des menus, champs et dissectors peuvent varier suivant la version. En cas de doute, consulte le guide correspondant à la version installée et vérifie les filtres dans l’interface avant de les utiliser sur un diagnostic réel.
