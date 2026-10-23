# Analyse Wireshark avancée — Niveau débutant

Ce cours ouvre un parcours progressif d’analyse réseau avec Wireshark. Le mot « avancée » décrit le type de questions que nous allons apprendre à poser : pourquoi une connexion échoue, à quel moment un protocole attend une réponse, comment distinguer une perte réelle d’un simple artefact de capture, ou encore comment formuler une conclusion qu’un autre technicien pourra vérifier. Le niveau débutant signifie que chaque opération est présentée étape par étape, sans supposer que l’on maîtrise déjà l’analyse experte des paquets.

Le document constitue la première étape d’une progression **Débutant → Intermédiaire → Expert**. Les futurs niveaux pourront reprendre les acquis de celui-ci pour approfondir l’analyse multi-points, les problèmes de performance complexes, les conversations multiplexées, la corrélation temporelle entre plusieurs capteurs et l’automatisation. Ce premier cours installe les fondamentaux sans les traiter comme des évidences.

L’objectif n’est pas de mémoriser une longue liste de filtres. Il est de développer une méthode : recueillir le bon trafic, identifier la conversation utile, reconstruire sa chronologie, inspecter les champs pertinents, formuler une hypothèse, puis chercher une preuve qui la confirme ou la réfute. Wireshark est un analyseur de protocoles ; il décrit ce que le point de capture a observé et ce que ses dissectors savent interpréter. Il n’est ni un détecteur magique de toutes les pannes ni un observateur omniscient de l’ensemble du réseau.

## Comment utiliser ce cours

Progresse dans l’ordre des chapitres. Pour chaque notion, lis l’explication, observe le schéma, applique le filtre d’affichage sur une capture de laboratoire, puis écris une phrase décrivant ce que tu as réellement vu. Les adresses et domaines utilisés dans les exemples sont fictifs ou réservés à la documentation. Remplace-les par ceux de ton environnement de test.

Les manipulations de capture doivent être faites sur une machine et un réseau que tu es autorisé à analyser. Une capture peut contenir des identifiants, des adresses internes, des cookies, des jetons de session ou des données personnelles. Réduis la collecte au strict nécessaire, protège les fichiers et ne partage pas une capture brute sans vérifier ce qu’elle contient.

### Résultats attendus à la fin

Tu devras pouvoir ouvrir une capture, distinguer filtre de capture et filtre d’affichage, sélectionner une conversation, lire les colonnes principales, comprendre les drapeaux TCP élémentaires, suivre une résolution DNS, repérer les étapes visibles d’une connexion TLS, interpréter avec prudence les alertes d’Expert Information, exporter des éléments utiles et rédiger un compte rendu reproductible. Tu sauras aussi dire quand les preuves ne suffisent pas et quand une capture prise à un seul endroit ne permet pas de conclure.

---

## 1. À quoi sert réellement Wireshark ?

Wireshark enregistre ou ouvre des paquets, puis tente de les interpréter à partir des formats de protocoles qu’il reconnaît. Pour un paquet Ethernet transportant IPv4, TCP puis TLS, l’interface peut présenter successivement les informations de liaison, les adresses IP, les ports et drapeaux TCP, puis les éléments TLS accessibles. Cette lecture facilite le passage entre l’enveloppe réseau et l’échange applicatif.

Il faut distinguer trois choses. Premièrement, le paquet tel qu’il a été capturé : une suite d’octets, accompagnée d’informations de temps et de capture. Deuxièmement, la dissection : l’interprétation de ces octets selon les formats connus. Troisièmement, l’hypothèse de l’analyste : une explication de ce que la séquence signifie dans le contexte. La dissection peut être correcte alors que l’hypothèse est fausse. Une retransmission TCP signalée par Wireshark est un indice calculé depuis la séquence observée, pas une preuve automatique que tel routeur précis a supprimé le segment.

Une capture montre uniquement ce que l’interface et le mécanisme de capture ont pu observer. Une capture sur le poste client ne prouve pas directement ce qui est arrivé à un routeur distant. Une capture sur un serveur ne présente pas nécessairement le même point de vue que celle du client. Des paquets peuvent être perdus avant d’atteindre le capteur, être omis par surcharge de capture ou avoir été regroupés par des fonctions de déchargement matériel. Il faut donc noter le point d’observation avant de tirer une conclusion.

Wireshark est particulièrement utile pour comprendre la chronologie : qui a envoyé le premier paquet, quelle réponse est arrivée, quel délai s’est écoulé, si une connexion a été établie, si une requête DNS a reçu une réponse, si des retransmissions sont visibles et si l’échange s’arrête au même endroit lors de plusieurs essais. Il aide aussi à isoler des conversations spécifiques plutôt que de raisonner à partir d’un simple « Internet est lent ».

### Exemple de bonne et de mauvaise conclusion

Conclusion trop forte : « Wireshark montre une retransmission, donc le routeur du fournisseur perd des paquets. » Cette phrase nomme une cause et un responsable sans preuve suffisante. Conclusion mieux étayée : « La capture côté client montre la retransmission du segment portant la plage de séquence observée, sans ACK correspondant dans cette capture pendant la fenêtre examinée. Une perte ou un retard est possible ; il faut comparer avec une capture à l’autre extrémité et vérifier les limites du point de capture. » La seconde phrase indique le fait observé, la portée de l’inférence et la vérification nécessaire.



## 2. Comprendre le point de capture

Avant d’ouvrir les détails d’un paquet, identifie l’endroit où il a été capturé : poste client, serveur, port miroir d’un commutateur, interface d’un pare-feu, interface physique ou interface de tunnel. Le point d’observation change ce qui est visible. Une capture faite avant encapsulation peut montrer le paquet intérieur, alors qu’une capture réalisée sur l’interface extérieure d’un VPN montre le paquet encapsulé. Une capture Wi-Fi en mode station ordinaire ne fournit pas nécessairement tous les échanges radio qui seraient visibles en mode moniteur.

Le dessin suivant rappelle que le même échange peut apparaître différemment selon le capteur. Les points d’écoute sont des vues partielles ; ils ne doivent pas être confondus avec un enregistrement complet de chaque lien traversé.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" role="img" aria-labelledby="wireshark-capture-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="wireshark-capture-title">Du réseau à la capture Wireshark</title>
<defs><marker id="arr1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#80cbc4"/></marker></defs>
<text x="450" y="30" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Observer sans confondre les points de vue</text>
<rect x="30" y="75" width="170" height="90" rx="12" fill="#193b52" stroke="#69b7d5" stroke-width="2"/><text x="115" y="108" fill="#fff" text-anchor="middle" font-size="16" font-weight="700">Client</text><text x="115" y="132" fill="#d5e9f0" text-anchor="middle" font-size="12">Navigateur / OS</text>
<rect x="270" y="75" width="170" height="90" rx="12" fill="#3a2c55" stroke="#b39ddb" stroke-width="2"/><text x="355" y="108" fill="#fff" text-anchor="middle" font-size="16" font-weight="700">Réseau</text><text x="355" y="132" fill="#e7ddf7" text-anchor="middle" font-size="12">Switch / routeur / AP</text>
<rect x="510" y="75" width="170" height="90" rx="12" fill="#224938" stroke="#80cbc4" stroke-width="2"/><text x="595" y="108" fill="#fff" text-anchor="middle" font-size="16" font-weight="700">Serveur</text><text x="595" y="132" fill="#d7f4e7" text-anchor="middle" font-size="12">Service distant</text>
<rect x="735" y="75" width="135" height="90" rx="12" fill="#593b22" stroke="#ffcc80" stroke-width="2"/><text x="802" y="108" fill="#fff" text-anchor="middle" font-size="16" font-weight="700">Capture</text><text x="802" y="132" fill="#ffead0" text-anchor="middle" font-size="12">Point d'écoute</text>
<path d="M200 120 H260 M440 120 H500 M680 120 H725" stroke="#80cbc4" stroke-width="3" marker-end="url(#arr1)" fill="none"/>
<circle r="7" fill="#ffeb3b"><animateMotion dur="4s" repeatCount="indefinite" path="M200 120 H260 M440 120 H500 M680 120 H725"/></circle>
<path d="M802 165 V205 H450" stroke="#ffcc80" stroke-width="2" stroke-dasharray="6 5" fill="none"/><rect x="270" y="205" width="360" height="58" rx="9" fill="#172832" stroke="#ffcc80"/><text x="450" y="229" fill="#fff" font-size="14" text-anchor="middle">Wireshark interprète les paquets vus ici</text><text x="450" y="247" fill="#ffd9a6" font-size="12" text-anchor="middle">Une capture ne montre pas automatiquement tout le trajet</text>
</svg>

**À observer :** le point de capture détermine quelles trames sont visibles. La capture n’est pas une carte complète du réseau ; elle est une observation située dans le temps et dans l’espace.

### Questions à documenter avant la collecte

1. Qui rencontre le problème : un poste, plusieurs postes, un site ou tous les utilisateurs ?
2. Quelle destination, quel service, quel port et quelle fenêtre de temps sont concernés ?
3. Le trafic est-il capturé sur l’interface qui porte réellement la connexion ?
4. Utilise-t-on un VPN, un proxy, une carte virtuelle, un pont, un conteneur ou une interface Wi-Fi ?
5. Le système dispose-t-il de plusieurs interfaces actives, d’une adresse IPv4 et d’une adresse IPv6, ou de routes multiples ?
6. La capture a-t-elle commencé avant le début du symptôme et s’est-elle terminée après sa manifestation ?

Une collecte commencée après l’établissement de la session peut manquer le SYN initial et rendre moins évidente la négociation TCP. Une capture arrêtée trop tôt peut ne pas montrer le délai d’attente qui permettrait de distinguer une réponse lente d’une absence de réponse. Une capture trop longue, à l’inverse, peut devenir difficile à examiner et augmenter le risque d’exposition de données sensibles. Le but est de collecter assez de contexte pour expliquer l’incident, pas de tout enregistrer sans limite.

### Préparation d’un laboratoire simple

Pour apprendre, utilise un poste client, une destination de test et un service connu. Note l’adresse, le nom DNS, le protocole, le port attendu, l’heure et l’action qui déclenche le symptôme. Commence avec un test contrôlé : ouverture d’une page de test, résolution d’un nom précis ou connexion à un serveur local. Change un seul paramètre à la fois. Si tu changes simultanément le DNS, le navigateur, le VPN et le pare-feu, il devient beaucoup plus difficile d’attribuer une amélioration à une cause.

Sur un environnement Windows, Linux ou macOS, la liste des interfaces affichées par Wireshark peut contenir des interfaces physiques et virtuelles. Le trafic local peut emprunter une interface inattendue selon les routes et les logiciels actifs. Vérifie les compteurs de paquets de chaque interface et, si nécessaire, capture brièvement sur une interface à la fois pour établir laquelle contient l’échange recherché.



## 3. Installer le vocabulaire : trame, paquet, segment et conversation

Les mots « trame », « paquet » et « segment » sont souvent employés de façon approximative. Pour l’analyse, il est utile de distinguer les couches. Ethernet ou le Wi-Fi transportent des unités de couche liaison ; IP porte des paquets de couche réseau ; TCP transporte des segments ; UDP transporte des datagrammes. Wireshark peut présenter les quatre couches dans une seule ligne de paquet parce qu’elles sont encapsulées les unes dans les autres. Un paquet capturé n’est pas nécessairement une unité égale à un message applicatif : une réponse HTTP peut être répartie sur de nombreux segments TCP, et un segment TCP peut contenir plusieurs unités de données d’application selon le protocole et les circonstances.

Le modèle en couches est un outil pratique pour poser les questions dans un ordre utile. La liaison permet de comprendre les adresses locales et les VLAN visibles ; IP décrit le trajet logique, la source, la destination et les sauts restants ; TCP ou UDP décrit le transport ; DNS, HTTP, TLS ou un autre protocole applicatif porte la signification propre au service. La réalité inclut des encapsulations et des exceptions, mais l’approche par couches évite de sauter directement à l’application lorsqu’une connexion ne s’établit même pas.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-labelledby="layers-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="layers-title">Lecture en couches d'un paquet</title>
<text x="450" y="28" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Du cadre Ethernet à l'application</text>
<g font-size="14" text-anchor="middle"><rect x="60" y="58" width="780" height="44" rx="7" fill="#17435b" stroke="#69b7d5"/><text x="450" y="85" fill="#fff">Ethernet / Wi-Fi — adresses de couche liaison</text><rect x="95" y="111" width="710" height="44" rx="7" fill="#3d305c" stroke="#b39ddb"/><text x="450" y="138" fill="#fff">IP — adresses source/destination, TTL ou Hop Limit</text><rect x="130" y="164" width="640" height="44" rx="7" fill="#214e3a" stroke="#80cbc4"/><text x="450" y="191" fill="#fff">TCP ou UDP — ports, séquence, acquittements</text><rect x="165" y="217" width="570" height="44" rx="7" fill="#664423" stroke="#ffcc80"/><text x="450" y="244" fill="#fff">DNS, HTTP, TLS ou autre protocole applicatif</text></g>
<path d="M30 82 H51 M65 135 H86 M100 188 H121 M135 241 H156" stroke="#ffeb3b" stroke-width="3"/><circle r="6" fill="#ffeb3b"><animateMotion dur="5s" repeatCount="indefinite" path="M30 82 H51 M65 135 H86 M100 188 H121 M135 241 H156"/></circle>
<text x="450" y="293" fill="#d8e5ec" font-size="13" text-anchor="middle">Développez une couche à la fois : chaque champ répond à une question différente.</text>
<text x="450" y="313" fill="#9fb2bd" font-size="12" text-anchor="middle">Les protocoles réels peuvent être encapsulés et les dissections peuvent être incomplètes.</text>
</svg>

### Les quatre panneaux usuels de l’interface

La liste des paquets donne une ligne par paquet capturé et les colonnes telles que le numéro, le temps relatif, les adresses source et destination, le protocole, la longueur et un résumé. Le panneau de détails développe l’arbre des protocoles pour le paquet choisi. Le panneau d’octets affiche les octets bruts et leur représentation textuelle quand c’est applicable. La barre de filtre d’affichage permet de limiter les paquets présentés à ceux qui satisfont une expression. Le nom ou la place exacte de certains panneaux peut varier selon les préférences d’affichage et la version.

Choisis un paquet dans la liste, puis développe les blocs par couche. Si tu sélectionnes un paquet DNS sur UDP, tu dois pouvoir retrouver l’en-tête Ethernet ou équivalent, l’en-tête IP, le port UDP, puis les champs DNS comme l’identifiant de transaction, le type de requête et les éventuels enregistrements de réponse. La lecture systématique est plus fiable que la recherche d’un libellé rouge ou d’un résumé spectaculaire.

### Colonnes personnalisées utiles

Pour un premier profil, garde les colonnes temps, source, destination, protocole, longueur et résumé. Plus tard, ajoute les ports TCP ou UDP, les numéros de séquence et d’acquittement, la fenêtre TCP, le temps de réponse DNS ou un champ applicatif pertinent. Ajouter toutes les colonnes possibles rend l’affichage confus. Un analyste expérimenté adapte les colonnes à une question précise et change de profil quand la question change.



## 4. Capturer sans perdre l’information utile

Une capture doit être assez large pour garder le contexte, mais assez ciblée pour être exploitable. Au démarrage, sélectionner la bonne interface est souvent plus important que choisir immédiatement un filtre. Un filtre de capture peut réduire le volume enregistré, mais il peut aussi exclure un paquet essentiel si l’hypothèse initiale est incorrecte. Lors d’un premier diagnostic, quand l’espace le permet et que la confidentialité est maîtrisée, il peut être préférable de collecter un intervalle court sans filtre de capture strict, puis d’appliquer des filtres d’affichage pour explorer le fichier.

Les filtres de capture et d’affichage ne sont pas la même langue. Les filtres de capture utilisent la syntaxe fournie par libpcap, par exemple `host 192.0.2.20 and port 443`. Les filtres d’affichage utilisent les champs disséqués de Wireshark, par exemple `ip.addr == 192.0.2.20 && tcp.port == 443`. La première syntaxe décide ce qui est conservé pendant la capture ; la seconde masque ou montre les paquets dans une capture déjà disponible. Une erreur de filtre de capture peut supprimer définitivement de la collecte les paquets nécessaires à la future analyse.

Pour un exercice, si tu veux observer la connexion d’un poste vers un serveur HTTPS connu, commence par une courte capture sur l’interface réellement utilisée. Déclenche une seule action. Arrête la capture après la réponse ou après l’expiration d’un délai raisonnable. Enregistre le fichier dans un dossier de laboratoire avec un nom explicite comme `test_https_client_2026-10-22.pcapng`, sans inscrire de secret dans le nom. Dans le compte rendu, indique le point de capture, l’heure et l’action reproduite.

### Capture en direct et lecture d’un fichier

Capturer en direct permet d’observer un symptôme immédiat ; lire un fichier existant permet de répéter l’analyse sans reproduire l’incident. Une capture fournie par un collègue peut cependant omettre le contexte, le fuseau horaire ou le point de capture. Demande, lorsque c’est utile, l’interface, la version de Wireshark, la commande ou la méthode de collecte, ainsi que l’heure exacte du test. Ces informations évitent d’interpréter comme un délai réseau une différence d’horloge entre plusieurs systèmes.

Ne commence pas par activer tous les protocoles de déchiffrement ou par exporter l’ensemble des objets applicatifs. La première passe est souvent descriptive : volume, durée, adresses, protocoles majeurs, nombre de conversations et erreurs de capture éventuelles. Détermine ensuite quelle partie répond à la question d’incident. Cette discipline réduit les risques et aide à expliquer pourquoi certains paquets sont inclus dans le dossier de preuve.

### Formats de fichiers

Wireshark utilise notamment le format pcapng, qui peut conserver des métadonnées liées aux interfaces et à la capture. D’autres outils produisent du pcap. Les deux peuvent être utiles, mais l’import ou la conversion peut perdre certaines métadonnées. Si une analyse dépend d’une information de capture particulière, conserve le fichier original et effectue les transformations sur une copie. Ne renomme pas simplement un fichier pour prétendre le convertir : utilise une fonction ou un outil prévu à cet effet.



## 5. Les filtres d’affichage : le geste qui fait gagner du temps

Les filtres d’affichage sont l’outil quotidien de l’analyste. Ils réduisent le bruit tout en laissant intact le fichier source. Un filtre `dns` présente les paquets que Wireshark reconnaît comme DNS. Un filtre `tcp` limite l’affichage au trafic TCP. Un filtre fondé sur une adresse permet de se concentrer sur une machine. Un filtre combinant protocole, adresse et indicateur TCP permet de répondre à une question plus étroite. Les noms de champs sont généralement en minuscules, et la grammaire exige une syntaxe précise : `==` sert aux égalités, `&&` combine des conditions et `||` exprime une alternative.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 320" role="img" aria-labelledby="filters-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="filters-title">Affiner une analyse avec les filtres d'affichage</title><text x="450" y="30" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Réduire le bruit sans perdre le contexte</text>
<rect x="40" y="68" width="820" height="45" rx="8" fill="#253847" stroke="#7a9bab"/><text x="450" y="96" text-anchor="middle" fill="#fff" font-size="15">Capture complète : ARP, DNS, TCP, TLS, UDP, ICMP…</text>
<path d="M450 113 V143" stroke="#80cbc4" stroke-width="3"/><path d="M442 135 L450 145 L458 135" stroke="#80cbc4" stroke-width="3" fill="none"/>
<rect x="100" y="147" width="700" height="45" rx="8" fill="#1c4a3a" stroke="#80cbc4"/><text x="450" y="175" text-anchor="middle" fill="#fff" font-size="15">Filtre : ip.addr == 192.0.2.20</text>
<path d="M450 192 V222" stroke="#80cbc4" stroke-width="3"/><path d="M442 214 L450 224 L458 214" stroke="#80cbc4" stroke-width="3" fill="none"/>
<rect x="160" y="226" width="580" height="43" rx="8" fill="#48365c" stroke="#b39ddb"/><text x="450" y="253" text-anchor="middle" fill="#fff" font-size="15">Affiner ensuite : tcp.analysis.retransmission</text>
<circle r="6" fill="#ffeb3b"><animateMotion dur="4s" repeatCount="indefinite" path="M450 115 V140 M450 194 V220"/></circle>
<text x="450" y="296" fill="#d8e5ec" text-anchor="middle" font-size="12">Un filtre d'affichage masque des paquets à l'écran : il ne les supprime pas du fichier.</text>
</svg>

Voici des filtres utiles au début. Les adresses de l’exemple sont documentaires ; remplace-les par les adresses réelles de ton laboratoire.

| Question | Filtre d’affichage |
|---|---|
| Voir le trafic DNS reconnu | `dns` |
| Afficher uniquement TCP | `tcp` |
| Afficher les paquets vers ou depuis un hôte IPv4 | `ip.addr == 192.0.2.20` |
| Voir une conversation TCP sur le port HTTPS | `tcp.port == 443` |
| Voir les SYN initiaux sans ACK | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| Repérer des retransmissions TCP signalées | `tcp.analysis.retransmission` |
| Afficher les réponses ICMP | `icmp` |
| Afficher le trafic TLS reconnu | `tls` |
| Voir des requêtes HTTP classiques lorsqu’elles sont décodées | `http.request` |
| Limiter un diagnostic à DNS et TCP | `dns || tcp` |

Un filtre vide ne signifie pas forcément qu’aucun paquet correspondant n’a traversé le réseau. Il peut y avoir plusieurs raisons : la collecte a utilisé un autre point, le protocole n’est pas reconnu comme tu le pensais, la connexion emploie un transport différent, le trafic a été exclu lors de la capture ou le champ a changé selon la version et le dissector. Vérifie le nom du champ dans le panneau de détails et la référence de filtre de ta version. Si le filtre devient rouge, ne le laisse pas tel quel en espérant qu’il fonctionne : corrige la syntaxe.

### Construire un filtre progressivement

Ne commence pas par une expression longue avec six conditions. Vérifie d’abord `dns`, puis ajoute l’adresse de destination, puis le type de transaction ou la fenêtre de temps. Si le résultat devient vide à une étape, tu sais quelle condition a éliminé les paquets. Cette méthode est plus pédagogique et plus efficace qu’un filtre complexe copié sans compréhension.

### Les pièges logiques

Les champs IP source et destination appartiennent à la couche réseau ; les ports appartiennent au transport. `ip.addr == X` est une façon pratique de chercher un hôte IPv4 en source ou destination. Il faut toutefois traiter IPv6 également si le service peut l’utiliser. Un filtre `tcp.port == 443` ne montre pas l’ensemble de l’activité HTTPS si le navigateur utilise HTTP/3 sur QUIC/UDP. De même, `http.request` n’affichera pas le contenu d’une session HTTPS chiffrée simplement parce que le serveur sert une page Web. Le filtre doit correspondre au protocole réellement utilisé, pas uniquement au service attendu.



## 6. Une méthode d’analyse au lieu d’une chasse aux couleurs

Quand une capture paraît complexe, évite de cliquer sur chaque ligne sans plan. Commence par définir le symptôme en termes observables : « le navigateur met vingt secondes puis affiche une erreur », « la résolution DNS échoue », « la connexion TCP n’est jamais établie », ou « le téléchargement démarre puis se fige ». Associe le symptôme à une fenêtre de temps et à une seule opération de reproduction. Ensuite, reconstruis le chemin des événements depuis le début de la tentative.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 320" role="img" aria-labelledby="workflow-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="workflow-title">Méthode de triage reproductible d'une capture</title><text x="450" y="28" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Une méthode d'analyse reproductible</text>
<g font-size="13" text-anchor="middle"><rect x="35" y="58" width="185" height="58" rx="8" fill="#17435b" stroke="#69b7d5"/><text x="127" y="82" fill="#fff" font-weight="700">1. Contexte</text><text x="127" y="100" fill="#d5e9f0">Qui / où / quand ?</text><rect x="250" y="58" width="185" height="58" rx="8" fill="#3d305c" stroke="#b39ddb"/><text x="342" y="82" fill="#fff" font-weight="700">2. Périmètre</text><text x="342" y="100" fill="#e7ddf7">Flux et direction</text><rect x="465" y="58" width="185" height="58" rx="8" fill="#214e3a" stroke="#80cbc4"/><text x="557" y="82" fill="#fff" font-weight="700">3. Chronologie</text><text x="557" y="100" fill="#d7f4e7">SYN, données, ACK</text><rect x="680" y="58" width="185" height="58" rx="8" fill="#664423" stroke="#ffcc80"/><text x="772" y="82" fill="#fff" font-weight="700">4. Hypothèse</text><text x="772" y="100" fill="#ffead0">Fait contre supposition</text></g>
<path d="M220 87 H242 M435 87 H457 M650 87 H672" stroke="#80cbc4" stroke-width="3"/><path d="M234 81 L242 87 L234 93 M449 81 L457 87 L449 93 M664 81 L672 87 L664 93" stroke="#80cbc4" stroke-width="3" fill="none"/>
<path d="M772 116 V151 H450 V170" fill="none" stroke="#ffcc80" stroke-width="2.5" stroke-dasharray="6 5"/><path d="M442 160 L450 170 L458 160" stroke="#ffcc80" stroke-width="2.5" fill="none"/>
<rect x="235" y="173" width="430" height="55" rx="9" fill="#273b4a" stroke="#69b7d5"/><text x="450" y="196" fill="#fff" text-anchor="middle" font-size="14" font-weight="700">5. Test de validation</text><text x="450" y="214" fill="#d3e5ec" text-anchor="middle" font-size="12">Reproduire, comparer, conserver la preuve</text>
<path d="M450 228 V250" stroke="#80cbc4" stroke-width="2.5"/><path d="M442 242 L450 252 L458 242" stroke="#80cbc4" stroke-width="2.5" fill="none"/><text x="450" y="278" fill="#d8e5ec" text-anchor="middle" font-size="13">Conclusion = observation + hypothèse + validation + limite de certitude</text><circle r="6" fill="#ffeb3b"><animateMotion dur="7s" repeatCount="indefinite" path="M35 87 H220 H435 H650 H772 V151 H450 V170 V228 V250"/></circle>
</svg>

Une méthode de triage commence par la question : la capture contient-elle la tentative attendue ? Si aucune trace n’apparaît, il est prématuré de diagnostiquer DNS ou TCP. Vérifie l’interface, le point de capture et les filtres. Si des paquets apparaissent, repère la première requête et la première réponse correspondante. Si la requête est répétée, recherche le délai entre les tentatives. Si une réponse arrive, vérifie si l’étape suivante a eu lieu. L’incident peut se produire après la résolution DNS, par exemple au moment d’ouvrir une connexion TCP ou de négocier TLS.

Le principe consiste à ne pas confondre « paquet observé » et « action applicative réussie ». Le SYN sortant prouve qu’une tentative de connexion a été émise depuis le point observé ; il ne prouve pas que le serveur a reçu le SYN. Le SYN-ACK prouve qu’une réponse a atteint le point de capture, mais une capture prise sur un port miroir peut omettre ou réordonner certaines trames. Une réponse DNS avec une adresse prouve qu’un résolveur a répondu ; elle ne prouve pas que la connexion vers cette adresse réussira.

### Écrire une hypothèse testable

Une bonne hypothèse indique ce qui devrait être visible si elle est correcte. Par exemple : « Si l’échec vient d’une absence de réponse DNS, la requête devrait apparaître sans réponse correspondante avant la fin de la tentative. » Teste ensuite si la capture montre cette séquence. Si une réponse DNS arrive rapidement, il faut déplacer la recherche vers l’étape suivante plutôt que continuer à accuser le DNS sans argument. Autre exemple : « Si le client tente TCP vers le serveur, je devrais observer un SYN vers l’adresse et le port visés. » Si ce SYN manque, explore l’interface, le proxy, le cache, le transport alternatif ou la période de capture.

### Distinguer faits, inférences et causes

Dans tes notes, crée trois catégories. Les faits sont des champs ou des événements directement visibles : heure, adresse, port, drapeau, code d’erreur ou nombre de tentatives. Les inférences sont des explications compatibles avec ces faits : serveur lent, perte, filtre de sécurité, route asymétrique ou mauvais point de capture. Les causes confirmées sont les explications validées par une observation supplémentaire ou un test discriminant. Cette séparation donne au rapport une valeur technique et évite que des suppositions deviennent des conclusions définitives après plusieurs transferts de ticket.



## 7. TCP : lire l’établissement, les données et les acquittements

TCP est un protocole orienté connexion. Pour commencer une nouvelle session classique, le client envoie généralement un segment SYN, le serveur répond par SYN-ACK, puis le client confirme avec ACK. Les données sont ensuite transportées avec des numéros de séquence et des acquittements. Cette séquence aide à déterminer si la connexion a été établie ou si le problème est apparu avant l’échange applicatif. Il existe des particularités de pile, des tentatives répétées, des options TCP et des mécanismes modernes ; dans ce cours, le handshake à trois étapes sert de modèle initial.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" role="img" aria-labelledby="tcp-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="tcp-title">Échange TCP et retransmission</title>
<text x="450" y="28" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Lire une conversation TCP dans le temps</text>
<text x="230" y="60" fill="#9dd7ed" text-anchor="middle" font-size="16" font-weight="700">Client</text><text x="670" y="60" fill="#b9e6ce" text-anchor="middle" font-size="16" font-weight="700">Serveur</text><path d="M230 75 V300 M670 75 V300" stroke="#58717f" stroke-width="2" stroke-dasharray="5 5"/>
<path d="M240 95 L655 95" stroke="#80cbc4" stroke-width="2.5"/><path d="M645 89 L655 95 L645 101" stroke="#80cbc4" stroke-width="2.5" fill="none"/><text x="450" y="87" fill="#d7f4e7" text-anchor="middle" font-size="13">SYN</text>
<path d="M660 130 L245 130" stroke="#ffcc80" stroke-width="2.5"/><path d="M255 124 L245 130 L255 136" stroke="#ffcc80" stroke-width="2.5" fill="none"/><text x="450" y="122" fill="#ffddb0" text-anchor="middle" font-size="13">SYN, ACK</text>
<path d="M240 165 L655 165" stroke="#80cbc4" stroke-width="2.5"/><path d="M645 159 L655 165 L645 171" stroke="#80cbc4" stroke-width="2.5" fill="none"/><text x="450" y="157" fill="#d7f4e7" text-anchor="middle" font-size="13">ACK — connexion établie</text>
<path d="M240 202 L655 202" stroke="#80cbc4" stroke-width="2.5" stroke-dasharray="8 5"/><path d="M645 196 L655 202 L645 208" stroke="#80cbc4" stroke-width="2.5" fill="none"/><text x="450" y="194" fill="#d7f4e7" text-anchor="middle" font-size="13">Données TCP — segment X</text>
<path d="M660 239 L245 239" stroke="#ff8a80" stroke-width="2.5" stroke-dasharray="5 5"/><path d="M255 233 L245 239 L255 245" stroke="#ff8a80" stroke-width="2.5" fill="none"/><text x="450" y="231" fill="#ffc1bc" text-anchor="middle" font-size="13">ACK absent ou retardé ? À vérifier</text>
<path d="M240 276 L655 276" stroke="#ff8a80" stroke-width="2.5"/><path d="M645 270 L655 276 L645 282" stroke="#ff8a80" stroke-width="2.5" fill="none"/><text x="450" y="268" fill="#ffc1bc" text-anchor="middle" font-size="13">Retransmission possible du segment X</text>
<circle r="6" fill="#ffeb3b"><animateMotion dur="7s" repeatCount="indefinite" path="M240 95 L655 95 M660 130 L245 130 M240 165 L655 165 M240 202 L655 202 M660 239 L245 239 M240 276 L655 276"/></circle>
<text x="450" y="321" fill="#d8e5ec" font-size="12" text-anchor="middle">Une retransmission est un indice, pas une preuve automatique de perte sur le réseau.</text>
</svg>

Le filtre `tcp.flags.syn == 1 && tcp.flags.ack == 0` met en évidence les SYN initiaux selon le décodage de Wireshark. Pour un flux sélectionné, clic droit puis **Follow → TCP Stream** permet de visualiser une reconstruction du flux quand les données nécessaires sont présentes. Cette reconstruction peut aider pour des protocoles en clair ou des données disponibles, mais elle ne supprime pas le chiffrement. Un flux TLS reste protégé sans les éléments nécessaires à son déchiffrement.

### Lire les numéros de séquence

Les numéros de séquence représentent la position des octets dans le flux TCP. Ils ne sont pas des compteurs universels de paquets. Plusieurs segments peuvent transporter des plages d’octets, et un ACK peut confirmer la réception cumulative d’une suite d’octets. Pour apprendre, examine un segment de données, note ses numéros de séquence et de longueur, puis identifie l’ACK correspondant. Garde en tête que Wireshark peut afficher des numéros relatifs pour les rendre plus faciles à suivre ; les valeurs affichées peuvent donc différer de celles du champ brut selon les préférences de l’analyse.

### Retransmission, doublons et hors ordre

Wireshark utilise l’état de la conversation observée pour signaler certains événements TCP, comme des retransmissions, des ACK dupliqués, des segments hors ordre ou des segments précédents qui manquent dans la capture. Ces libellés sont utiles pour orienter l’inspection, mais ils reposent sur ce que l’analyseur a vu et sur ses heuristiques. Une capture qui commence au milieu d’une conversation peut donner l’impression qu’un segment manque alors qu’il a simplement été transmis avant le début de l’enregistrement. Un port miroir saturé, un paquet oublié par le mécanisme de capture ou une capture dont l’horloge a été réordonnée peut compliquer l’interprétation.

Pour vérifier une retransmission, filtre `tcp.analysis.retransmission`, sélectionne quelques paquets et compare les numéros de séquence, les tailles et les ACK reçus. Cherche la cause au lieu de t’arrêter au libellé : manque d’ACK, ACK retardé, réordonnancement, perte sur le chemin, problème de capture ou retransmission spurious possible. Une seule ligne ne suffit pas pour attribuer le problème à un équipement. Compare, si possible, une capture proche de l’émetteur avec une capture proche du récepteur.

### SYN répétés et connexions bloquées

Plusieurs SYN identiques sans SYN-ACK visible peuvent indiquer que la réponse ne revient pas, qu’un pare-feu la supprime, que la destination n’écoute pas, que le trajet retour diffère ou que la capture ne voit pas le trafic réciproque. Le contexte de l’adresse et du port est indispensable. Vérifie si un RST répond à la tentative, si une réponse apparaît sur une autre interface et si le serveur confirme recevoir la demande. Un RST n’est pas identique à un silence : il peut indiquer un refus explicite ou une fermeture selon l’état de la connexion et la pile concernée.

### Latence et temps d’aller-retour

Les valeurs temporelles affichées par Wireshark permettent de mesurer des intervalles dans une capture, mais il faut savoir ce qui est mesuré. Le delta entre un paquet et le suivant n’est pas automatiquement le RTT. Un RTT estimé par TCP ou l’écart entre un segment et son ACK doit être interprété selon l’identification de la correspondance, les ACK cumulatifs et les éventuelles retransmissions. Quand plusieurs paquets portent le même numéro de séquence, une retransmission rend parfois l’attribution de l’ACK ambiguë. Le temps observé inclut les délais des piles, files d’attente et points de capture, pas uniquement le temps passé dans le réseau.



## 8. DNS : observer les questions avant d'accuser le réseau

DNS transforme un nom en informations comme des adresses IPv4 ou IPv6. Pour une première analyse, filtre `dns`, puis repère la question : nom demandé, type d’enregistrement, identifiant de transaction et client/serveur. Recherche ensuite la réponse associée. Le client peut utiliser UDP ou TCP pour DNS, selon les conditions et la configuration. Des résolutions chiffrées comme DoH ou DoT peuvent aussi déplacer la visibilité vers une session HTTPS ou TLS. L’absence de paquets DNS classiques ne prouve donc pas que la résolution ne se produit pas ; le poste peut utiliser un cache, un résolveur local ou un mécanisme chiffré.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-labelledby="dns-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="dns-title">Chronologie d'une résolution DNS</title><text x="450" y="28" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Suivre une résolution DNS en quatre temps</text>
<text x="220" y="63" fill="#9dd7ed" font-size="15" text-anchor="middle">Client</text><text x="675" y="63" fill="#b9e6ce" font-size="15" text-anchor="middle">Résolveur DNS</text><path d="M220 75 V287 M675 75 V287" stroke="#58717f" stroke-width="2" stroke-dasharray="5 5"/>
<path d="M230 105 H662" stroke="#80cbc4" stroke-width="2.5"/><path d="M652 99 L662 105 L652 111" stroke="#80cbc4" stroke-width="2.5" fill="none"/><text x="445" y="97" fill="#d7f4e7" font-size="13" text-anchor="middle">Requête : A / AAAA / nom demandé</text>
<path d="M665 155 H233" stroke="#ffcc80" stroke-width="2.5"/><path d="M243 149 L233 155 L243 161" stroke="#ffcc80" stroke-width="2.5" fill="none"/><text x="445" y="147" fill="#ffddb0" font-size="13" text-anchor="middle">Réponse : adresse ou code d'erreur</text>
<path d="M230 205 H662" stroke="#80cbc4" stroke-width="2.5" stroke-dasharray="6 4"/><path d="M652 199 L662 205 L652 211" stroke="#80cbc4" stroke-width="2.5" fill="none"/><text x="445" y="197" fill="#d7f4e7" font-size="13" text-anchor="middle">Nouvelle connexion vers l'adresse obtenue</text>
<rect x="102" y="235" width="696" height="47" rx="8" fill="#273b4a" stroke="#69b7d5"/><text x="450" y="255" fill="#fff" font-size="13" text-anchor="middle">À inspecter : Transaction ID, qname, qtype, délai, retransmissions</text><text x="450" y="272" fill="#d3e5ec" font-size="11" text-anchor="middle">Une réponse DNS rapide n'exclut pas une panne TCP/TLS ensuite.</text>
<circle r="6" fill="#ffeb3b"><animateMotion dur="5s" repeatCount="indefinite" path="M230 105 H662 M665 155 H233 M230 205 H662"/></circle>
</svg>

### Les champs à examiner

Le nom demandé, souvent présenté comme QNAME, est le nom pour lequel le client souhaite une réponse. QTYPE précise le type de requête, tel que A ou AAAA. L’identifiant de transaction aide à associer la requête et la réponse dans une capture traditionnelle. Vérifie également le bit de réponse, le code de retour et les sections question/réponse. Une réponse peut être valide sans donner l’adresse attendue si le nom n’existe pas, si le type demandé est absent ou si le serveur renvoie un code d’erreur. Il faut alors lire les champs plutôt que conclure que « DNS ne marche pas ».

### Délai et retransmissions

Si plusieurs requêtes apparaissent pour le même nom, vérifie leur écart temporel et si une réponse est arrivée entre les tentatives. Une répétition peut être un mécanisme normal de retry, une deuxième application, une requête A puis AAAA, un changement d’interface ou un nouveau processus. Compare le nom exact, le type et l’identifiant avant de les déclarer identiques. Certaines requêtes utilisent une autre adresse de résolveur après un délai. Un filtrage sur `dns` peut masquer la connexion HTTPS qui suit la résolution, donc retire le filtre pour replacer la réponse dans la chronologie globale.

### Scénario de diagnostic

Supposons qu’un navigateur affiche « site inaccessible ». La capture montre une requête A pour `service.example` et une réponse qui contient `192.0.2.80` en quelques millisecondes. Cet élément affaiblit l’hypothèse d’une absence totale de réponse DNS. Il ne prouve pas que toutes les étapes DNS sont bonnes ni que l’adresse correspond à la destination souhaitée. Ensuite, filtre l’adresse obtenue et examine TCP, TLS ou QUIC selon le transport. Si aucune connexion ne part, vérifie le navigateur, le proxy, l’adresse IPv6, la sélection d’une autre adresse ou une capture sur la mauvaise interface. Si la connexion démarre mais se bloque, déplace l’analyse sur la chronologie transport/application.

### UDP et TCP en DNS

Les grandes réponses ou certaines opérations DNS peuvent se poursuivre en TCP. N’utilise donc pas uniquement une hypothèse UDP. Observe les ports, les indicateurs de troncature éventuels et la séquence de connexion TCP. Quand une capture ne contient que la requête UDP et pas la réponse, vérifie le point de capture, le résolveur choisi, l’adresse de retour et la période de collecte. Une réponse peut être perdue avant le point où la capture est prise ; il faut comparer les observations avant de localiser la perte.



## 9. HTTP, HTTPS et ce que le chiffrement masque

Une requête HTTP en clair peut exposer des méthodes, chemins, en-têtes et codes de réponse. En HTTPS, HTTP est normalement protégé par TLS. Wireshark peut reconnaître des éléments de l’établissement de session et certains métadonnées protocolaires visibles, mais le contenu HTTP chiffré n’est pas automatiquement lisible. La présence d’un paquet TLS ou d’un ClientHello ne signifie pas que la négociation a échoué. Il faut voir la séquence, les réponses, les alertes visibles et le moment où le trafic cesse.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-labelledby="tls-title" style="max-width:100%;height:auto;background:#101820;border-radius:14px">
<title id="tls-title">Ce que Wireshark peut voir pendant TLS</title><text x="450" y="28" fill="#fff" font-size="20" text-anchor="middle" font-weight="700">Visibilité réseau avant et après chiffrement</text>
<rect x="45" y="70" width="230" height="65" rx="10" fill="#17435b" stroke="#69b7d5"/><text x="160" y="96" fill="#fff" text-anchor="middle" font-size="15" font-weight="700">TCP / QUIC</text><text x="160" y="117" fill="#d5e9f0" text-anchor="middle" font-size="12">Adresses, ports, temps</text>
<path d="M275 103 H330" stroke="#80cbc4" stroke-width="3"/><path d="M320 97 L330 103 L320 109" stroke="#80cbc4" stroke-width="3" fill="none"/>
<rect x="335" y="70" width="230" height="65" rx="10" fill="#3d305c" stroke="#b39ddb"/><text x="450" y="96" fill="#fff" text-anchor="middle" font-size="15" font-weight="700">TLS</text><text x="450" y="117" fill="#e7ddf7" text-anchor="middle" font-size="12">Négociation / chiffrement</text>
<path d="M565 103 H620" stroke="#80cbc4" stroke-width="3"/><path d="M610 97 L620 103 L610 109" stroke="#80cbc4" stroke-width="3" fill="none"/>
<rect x="625" y="70" width="230" height="65" rx="10" fill="#224938" stroke="#80cbc4"/><text x="740" y="96" fill="#fff" text-anchor="middle" font-size="15" font-weight="700">Application</text><text x="740" y="117" fill="#d7f4e7" text-anchor="middle" font-size="12">Contenu protégé</text>
<rect x="45" y="175" width="810" height="74" rx="10" fill="#1b2831" stroke="#78909c"/><text x="450" y="199" fill="#fff" text-anchor="middle" font-size="14" font-weight="700">Sans secrets de session ni déchiffrement valide</text><text x="450" y="222" fill="#d8e5ec" text-anchor="middle" font-size="13">On peut analyser la chronologie, les retransmissions, tailles, délais et alertes visibles,</text><text x="450" y="240" fill="#d8e5ec" text-anchor="middle" font-size="13">mais pas déduire le contenu applicatif chiffré à partir du seul trafic TLS.</text>
<circle r="6" fill="#ffeb3b"><animateMotion dur="4s" repeatCount="indefinite" path="M275 103 H330 M565 103 H620"/></circle><text x="450" y="287" fill="#ffcc80" text-anchor="middle" font-size="12">La présence d'un ClientHello n'est pas la preuve que TLS échoue.</text><text x="450" y="306" fill="#9fb2bd" text-anchor="middle" font-size="12">Identifier d'abord la version, les clés disponibles et le point de capture.</text>
</svg>

### Lire une réponse HTTP quand elle est visible

Sur un service HTTP non chiffré de laboratoire, `http.request` peut montrer les requêtes décodées. Examine méthode, chemin, en-tête Host, code d’état et relation temporelle avec la requête précédente. Une réponse 404 indique que le serveur HTTP a répondu que la ressource n’était pas trouvée dans le contexte de la requête ; elle n’est pas équivalente à une panne de routage. Une réponse 500 signale une réponse du serveur, mais ne fournit pas à elle seule la cause interne. Une réponse 301 ou 302 peut rediriger le client vers une autre URL, déclenchant ensuite une nouvelle résolution DNS ou connexion.

### TLS : début, attente et échec

Dans une capture TLS, relève le ClientHello si visible, les versions et extensions présentées, le comportement du pair et l’endroit exact où la séquence cesse. Suivant la version et le protocole, les champs visibles diffèrent. Une capture ne contenant qu’un ClientHello peut signifier que le serveur ne répond pas au point capturé, que la réponse a été perdue ou que la collecte ne l’a pas enregistrée. Si un serveur répond par une alerte TLS, inspecte le type d’alerte et le moment où elle survient. N’invente pas de contenu applicatif en clair à partir de longueurs et de temps uniquement.

### Déchiffrement en laboratoire

Le déchiffrement exige les éléments cryptographiques appropriés pour la session et une configuration compatible avec la version du protocole. Si l’application peut exporter des secrets de session pour un laboratoire, configure Wireshark selon sa documentation officielle, protège le fichier de secrets et retire-le des livrables après l’exercice. Le fichier qui permet de déchiffrer peut être plus sensible que la capture elle-même : toute personne qui le possède pourrait potentiellement lire le trafic correspondant. N’utilise pas ce mécanisme pour contourner une protection ou examiner du trafic dont l’accès n’est pas autorisé.

### Ne pas confondre TLS et QUIC

HTTP/3 utilise QUIC au-dessus d’UDP. Un filtre `tcp` n’affichera pas tout le trafic Web chiffré. Une session QUIC peut être décodée à différents niveaux selon la version, les secrets disponibles et les champs de la capture. Si l’utilisateur dit « HTTPS », vérifie le protocole effectivement transporté au lieu de supposer que toutes les connexions Web empruntent TCP/443. La capture doit guider le diagnostic, pas une convention de port mémorisée.



## 10. Statistiques : passer de la ligne isolée à la vue d'ensemble

Wireshark propose plusieurs vues statistiques utiles pour comprendre un fichier avant d’examiner les paquets un par un. La hiérarchie des protocoles estime la composition de la capture ; les conversations regroupent les échanges entre endpoints ; les points de terminaison résument les hôtes observés ; les graphes de flux TCP représentent l’évolution d’une conversation ; les graphiques de débit peuvent aider à visualiser les périodes d’activité. L’emplacement exact des menus peut dépendre de la version et des options activées.

Ne traite jamais une statistique comme une vérité complète sans examiner ses limites. Si la capture ne voit qu’un sens de la conversation, une vue de conversations sous-estimera les échanges. Si un point miroir supprime des paquets, les tailles et les taux seront biaisés. Si la collecte commence après le début du flux, le nombre de SYN et la première latence ne seront pas complets. Une statistique est une synthèse du fichier observé, pas un remplacement des vérifications de paquets.

### Hiérarchie des protocoles

Cette vue répond à une question simple : quelle part du fichier est associée à chaque protocole décodé ? Elle aide à reconnaître si une capture est dominée par DNS, TCP, TLS, QUIC, ARP ou un autre type d’échange. Elle peut aussi attirer l’attention sur un protocole inattendu. Les pourcentages dépendent toutefois du niveau d’encapsulation, des options de comptage et du trafic capturé. Ne compare pas deux pourcentages provenant de captures prises à des points différents sans comprendre leur périmètre.

### Conversations et endpoints

Les conversations regroupent le trafic entre deux endpoints selon le protocole, souvent avec des adresses et ports. Elles aident à identifier quel flux domine le volume ou à isoler la connexion affectée. Note les adresses et ports, puis applique un filtre de conversation depuis la liste ou construis ton propre filtre pour garder une trace claire du périmètre. Si plusieurs sessions vers le même service apparaissent, distingue-les à partir des ports source, des horaires et des séquences TCP. Un serveur peut répondre à plusieurs clients et un client peut ouvrir plusieurs connexions simultanées.

### Graphes TCP

Le graphe de flux TCP peut aider à voir les segments, les acquittements et les silences dans l’ordre temporel. Utilise-le après avoir sélectionné une conversation pertinente. Un graphique peut révéler un schéma répétitif : données envoyées, ACK absent, retransmission, pause, puis reprise. Ce motif peut soutenir l’hypothèse d’une perte ou d’un retard, mais il ne localise pas la cause si le fichier ne contient qu’un point de capture. Compare les tailles, les séquences et les temps avec la table des paquets avant de prendre une décision.



## 11. Expert Information : utile, mais jamais verdict automatique

La fenêtre **Analyze → Expert Information** regroupe des remarques produites par les dissectors, avec différents niveaux de gravité ou catégories. Certains avertissements signalent des séquences TCP inhabituelles, des retransmissions détectées, des checksums qui semblent incorrects ou une dissection incomplète. C’est un bon point de départ pour repérer ce qui mérite une inspection, mais ce n’est pas un rapport définitif de causes racines.

Les mentions « Warning » ou « Error » doivent être replacées dans le contexte du paquet et du point de capture. Des checksums qui paraissent mauvais sur un poste émetteur peuvent provenir du checksum offloading : le paquet est observé avant que la carte réseau calcule réellement le checksum. Certaines captures de trafic sortant montrent des segments très grands qui reflètent une segmentation prise en charge par la carte ou le système, et non une trame réellement envoyée avec cette taille sur le fil. Ces effets ne doivent pas être qualifiés automatiquement de panne réseau.

Pour chaque entrée intéressante, sélectionne le paquet concerné, développe l’arbre de protocole, note le champ et le contexte, puis compare avec les paquets précédents et suivants. Quand un message indique une séquence TCP suspecte, cherche si la capture commence au milieu de la connexion. Quand le message évoque une erreur de checksum, vérifie le point de capture et les fonctions de déchargement matériel. Quand le dissector ne reconnaît pas un protocole, vérifie si le port est standard, si un port non standard est utilisé ou si une configuration Decode As pourrait être appropriée dans un laboratoire.

Les informations d’expert peuvent être nombreuses sur une capture riche. Il est inutile de résoudre tous les avertissements si un incident précis est en cours. Filtre ou limite les éléments pertinents à la conversation en cause et garde une trace de ceux qui expliquent directement le symptôme. Les avertissements non liés peuvent être documentés séparément, mais ils ne doivent pas détourner le diagnostic principal.

### Exemple : checksum TCP incorrect dans une capture sortante

Un développeur fournit une capture prise sur son ordinateur et dit que des checksums TCP apparaissent incorrects. La conclusion immédiate « le réseau corrompt les paquets » n’est pas justifiée. Si la capture est faite avant le calcul matériel du checksum, Wireshark peut voir un champ encore provisoire. Pour confirmer, répète la capture à un point après transmission ou compare avec une capture côté réception. En laboratoire, on peut désactiver temporairement un offload pour comprendre l’effet, mais cette modification ne doit pas être appliquée en production sans justification. Si le checksum est aussi invalide côté réception, la piste devient plus crédible, mais l’attribution doit toujours être documentée.



## 12. Filtres plus précis et expressions reproductibles

Une analyse reproductible repose sur des filtres faciles à expliquer. Plutôt que de conserver une expression gigantesque non documentée, crée une suite de filtres nommés dans tes notes : d’abord l’hôte, ensuite le protocole, ensuite l’événement. Par exemple, pour examiner une connexion HTTPS vers un serveur documentaire, commence par `ip.addr == 192.0.2.80`, passe à `tcp.port == 443`, isole la conversation, puis examine `tcp.analysis.retransmission`. Si le trafic utilise IPv6, adapte le périmètre avec les champs IPv6 ; si le navigateur utilise QUIC, intègre le transport UDP.

### Opérateurs et parenthèses

Utilise `&&` et `||` avec des parenthèses lorsque la priorité logique pourrait être ambiguë. Une expression qui signifie « port 53 et soit une adresse source A, soit une adresse destination B » n’est pas identique à une expression qui exige l’adresse A et le port pour tous les cas. Lorsqu’un résultat est surprenant, décompose le filtre et vérifie chaque partie séparément. Le but d’un filtre est de rendre explicite le périmètre, pas de masquer une supposition.

### Champs présents et valeurs

Certains filtres recherchent la présence d’un champ ; d’autres comparent sa valeur. Un champ absent n’est pas toujours équivalent à un champ qui contient la valeur zéro. Le protocole peut ne pas avoir été décodé, le champ peut ne pas être applicable au paquet, ou les données peuvent être tronquées. Pour de nombreuses questions, l’opérateur de présence et une comparaison explicite n’ont pas le même comportement. Consulte le filtre de champ actuel et observe l’arbre du paquet avant d’interpréter les résultats.

### Contrôle de cohérence

Après un filtre, regarde combien de paquets restent et si leur séquence correspond à la question. Si une expression qui devait montrer le SYN n’affiche rien, retire les conditions supplémentaires jusqu’à retrouver la tentative. Si une expression de retransmission révèle des événements dans plusieurs conversations, limite-la au flux en cause. Une requête de filtre correcte mais appliquée au mauvais intervalle de capture peut conduire à une conclusion erronée ; la syntaxe et le contexte doivent être contrôlés ensemble.



## 13. TShark pour répéter et partager l’analyse

TShark est la version en ligne de commande de l’analyseur de protocoles. Il peut lire une capture, appliquer des filtres, afficher certains champs et écrire une nouvelle capture selon les options utilisées. Pour un débutant, l’intérêt principal est de rendre quelques contrôles reproductibles : compter les occurrences d’un filtre, extraire un tableau de champs et joindre la commande au dossier d’incident. Les options exactes doivent être vérifiées avec `tshark --help` et la page man correspondant à la version installée.

Exemples de laboratoire :

```bash
# Afficher la version installée
tshark --version

# Lire une capture et afficher les paquets DNS décodés
tshark -r capture.pcapng -Y dns

# Extraire les champs usuels de temps, protocole, source et destination
tshark -r capture.pcapng -T fields \
  -e frame.number -e frame.time_relative -e _ws.col.Protocol \
  -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport

# Afficher les retransmissions TCP détectées par Wireshark
tshark -r capture.pcapng -Y 'tcp.analysis.retransmission'
```

Sous Windows, les commandes et chemins doivent être adaptés à l’installation locale de TShark. Sur certaines machines, il faut préciser le chemin complet vers l’exécutable ou lancer le terminal avec des droits autorisés. N’exécute pas ces commandes sur des captures qui ne sont pas destinées à ton analyse : l’accès à une capture n’autorise pas automatiquement la divulgation de son contenu.

### Pourquoi utiliser une sortie de champs

Une sortie de champs peut être importée dans un tableur ou traitée par un script pour comparer plusieurs captures. Il faut néanmoins savoir que le format, les séparateurs et les valeurs absentes doivent être gérés soigneusement. Lorsque les colonnes contiennent des virgules, espaces ou textes libres, un format de sortie mal choisi peut rendre le résultat ambigu. Conserve l’original, documente la commande et conserve le filtre utilisé. Une ligne exportée ne donne pas toute la sémantique du paquet ; garde la capture si une inspection plus détaillée est nécessaire.

### Répéter un test sans détruire la preuve

Utilise le même filtre et le même intervalle de temps sur les captures comparées. N’applique pas une modification directe au seul fichier original. Enregistre des fichiers de travail distincts et indique l’outil et la version. Si tu modifies une capture, par exemple en supprimant certaines trames pour partager un extrait, garde le fichier original dans un emplacement protégé et précise que l’extrait est partiel. Une conclusion tirée d’un extrait doit mentionner les informations qui ont été retirées.



## 14. Horodatage, latence et qualité du capteur

Le temps est essentiel pour comparer une requête et sa réponse. Dans une seule capture, le temps relatif peut permettre d’estimer le délai entre deux événements enregistrés par le même capteur. Quand plusieurs captures sont comparées, l’horloge et sa synchronisation deviennent critiques. Si le client et le serveur n’ont pas la même heure, soustraire simplement leurs horodatages peut donner une valeur trompeuse. Il faut distinguer les temps relatifs à chaque fichier des timestamps absolus et documenter la source de synchronisation.

Les captures en direct peuvent elles-mêmes être affectées par la charge du système, la vitesse de l’interface, la mémoire disponible et le mécanisme de capture. Un hôte fortement sollicité peut abandonner des paquets avant qu’ils soient enregistrés. Certains environnements virtualisés présentent aussi des timestamps et un ordonnancement différents de ceux observés sur le fil. Quand une conclusion dépend de quelques millisecondes, vérifie la qualité du point de capture et évite de présenter une mesure comme plus précise qu’elle ne l’est.

### Estimer la latence sans confusion

La différence de temps entre une requête et sa réponse peut constituer une mesure utile si les deux sont vus par la même capture. Mais le délai inclut plus que le réseau : traitements sur le client, attente dans les files, résolution, traitement par le serveur et délai de retour. Le premier paquet vu par Wireshark peut également être postérieur à l’événement applicatif qui l’a déclenché. Pour comparer les performances, utilise des actions reproductibles et une définition claire du début et de la fin de la mesure.

### Perte de capture contre perte réseau

Si une capture montre un numéro de séquence manquant ou un message « previous segment not captured », plusieurs causes sont possibles. Le capteur peut avoir démarré trop tard, avoir perdu une trame, avoir enregistré les paquets dans un ordre différent, ou observer un flux dont certains segments ont emprunté un chemin différent. La perte réseau demeure une hypothèse possible, mais elle n’est pas la seule. Une deuxième capture au même instant et sur un autre point aide souvent à discriminer les causes.

### Capturer des deux côtés

Pour comprendre où un paquet disparaît, si l’environnement et les autorisations le permettent, effectue une capture près de l’émetteur et une autre près du récepteur. Identifie les deux points et synchronise les horloges autant que possible. Compare les paquets par adresse, ports, séquence TCP, longueur et contenu pertinent. Si un paquet apparaît à l’entrée et pas à la sortie d’un équipement, la piste devient plus précise, mais une capture manquante peut toujours résulter d’une limite du capteur. Les points d’observation et les pertes de collecte doivent figurer dans la conclusion.



## 15. Détecter les problèmes de réseau sans attribuer trop tôt la cause

Les problèmes réels se présentent rarement comme une seule ligne évidente. Un délai d’ouverture de page peut venir d’une résolution lente, d’une connexion TCP qui se répète, d’une négociation TLS prolongée, d’un proxy, d’une redirection, d’une application qui attend une ressource secondaire ou d’une panne de retour. La bonne démarche consiste à localiser la première étape où le comportement attendu n’apparaît plus.

### Cas A : DNS répond, puis plus rien

La capture montre une requête DNS, une réponse avec une adresse, puis aucun SYN vers cette adresse. Ne conclus pas immédiatement que le réseau bloque le SYN : il n’existe pas de SYN visible à analyser dans cette capture. Vérifie si le navigateur a utilisé un proxy, si l’adresse IPv6 a été choisie, si un cache ou un service local est intervenu, si le trafic a été capturé sur la bonne interface et si l’application a effectivement poursuivi. La couche applicative peut ne pas lancer de connexion malgré une résolution réussie.

### Cas B : SYN répétés sans réponse

Le client envoie des SYN répétés vers la même destination et le même port sans réponse visible. C’est compatible avec une réponse qui ne revient pas, un filtrage silencieux, un service inaccessible, un chemin retour différent ou une capture incomplète. Cherche la même tentative côté serveur. Si le serveur ne voit pas les SYN, l’investigation se déplace vers l’amont ou le point de capture du client. Si le serveur reçoit le SYN et envoie un SYN-ACK mais que le client ne le voit pas, examine le trajet retour, les filtres et les points de collecte. Si le serveur ne répond pas malgré la réception, inspecte son état local et les politiques de sécurité.

### Cas C : handshake TCP complet, mais la page échoue

Un handshake TCP complet prouve que les trois étapes de démarrage ont été observées au point de capture. Il ne prouve pas que le service applicatif fonctionnera. Examine ce qui vient ensuite : des données client, une réponse serveur, une négociation TLS, une fermeture RST/FIN, un délai d’attente ou des retransmissions. Dans HTTPS, le contenu de la requête et de la réponse n’est pas nécessairement lisible. La chronologie et les métadonnées peuvent néanmoins localiser le blocage.

### Cas D : TCP retransmet à plusieurs reprises

Les retransmissions peuvent apparaître lorsqu’un segment ou son ACK n’est pas vu par l’émetteur dans le délai attendu. Il peut s’agir d’une perte, d’un retard, d’un réordonnancement, d’une perturbation de capture ou d’un phénomène propre à la pile et au chemin. Regarde si la retransmission est suivie d’un ACK, si le même segment est réémis à des intervalles croissants et si le motif se concentre sur une direction, une taille ou une période. Compare les observations aux deux extrémités avant d’assigner la responsabilité à un appareil.

### Cas E : de petites requêtes passent, les grosses transactions se figent

Ce motif peut orienter vers une question de taille de paquet, MTU, PMTUD, tunnel ou MSS, mais il ne la prouve pas. Filtre les paquets ICMP, inspecte les tailles et observe si les mêmes plages de données sont retransmises sans progression. Note que les fonctions de déchargement matériel peuvent afficher des paquets sortants plus grands que les trames réellement transmises. Compare les captures et teste prudemment un chemin alternatif ou une taille réduite dans un environnement contrôlé. Le diagnostic MTU/PMTUD a ses propres procédures ; ici, le but est d’apprendre à repérer un symptôme de taille sans déclarer la cause sur la seule base de la taille affichée.

### Cas F : une application semble lente, mais TCP paraît sain

Une connexion TCP sans retransmission évidente peut tout de même connaître un temps applicatif élevé. L’application serveur peut attendre une base de données, un verrou, un traitement CPU ou une réponse d’un autre service. Wireshark montre l’absence temporaire de paquets ou le délai entre les échanges, mais ne peut pas observer directement le travail interne d’un processus. Il faut corréler la capture à des journaux, métriques et traces applicatives. Le réseau est une couche de preuve, pas une explication universelle.



## 16. TLS, certificats et limites de l’observation réseau

La négociation TLS permet au client et au serveur d’établir les paramètres cryptographiques qui protégeront la session. Wireshark peut afficher des éléments visibles de cette négociation, mais les détails disponibles varient selon les versions TLS, les extensions, les options de capture et la présence de secrets de session. N’interprète pas tous les échecs comme une simple « erreur de certificat » : l’erreur peut être due à un nom, une politique, une version, une suite cryptographique, une alerte distante, une fermeture intermédiaire ou une coupure réseau.

Pour analyser une négociation, relève l’adresse, le port, le transport, le moment du premier ClientHello, la réponse éventuellement reçue et l’endroit où la séquence cesse. Si un message d’alerte est décodable, note son type et sa position dans l’échange. Si la capture contient uniquement une tentative et se termine immédiatement, ne conclus pas que le pair a rejeté le client : le fichier peut être incomplet, capturé du mauvais côté ou avoir omis la réponse. Répète le test avec une capture complète et, si possible, compare les deux extrémités.

### Certificat visible ou non

Dans certaines négociations TLS, des informations de certificat peuvent être visibles dans la capture ; dans d’autres, selon le protocole et les versions utilisés, elles sont protégées. L’absence de champs lisibles n’indique donc pas nécessairement qu’aucun certificat a été présenté. Il faut connaître la version de TLS et la phase exacte de la négociation. Wireshark n’invente pas un champ quand les données ne sont pas visibles ou déchiffrables.

### Déchiffrement autorisé de sessions de test

Pour une analyse pédagogique autorisée, certaines applications peuvent exporter des secrets de session dans un fichier que Wireshark sait utiliser pour déchiffrer le trafic correspondant. Ce mécanisme doit être mis en place en respectant la documentation de l’application et de Wireshark. Le fichier de secrets est sensible : stocke-le dans un emplacement protégé, limite son accès et supprime-le selon la politique de conservation du laboratoire. Ne joins pas le secret à un ticket externe si ce n’est pas strictement nécessaire. La capacité à lire des données déchiffrées ne signifie pas qu’on doit les collecter toutes.

### Contenu applicatif absent

Si la capture montre une session TLS mais que le navigateur signale un contenu inattendu, Wireshark peut aider à vérifier les délais, les tailles, les échanges et les fermetures. Il ne permet pas de reconstruire arbitrairement le contenu chiffré à partir de la seule taille des paquets. Pour le contenu applicatif, utilise les journaux et outils autorisés à la couche concernée ou configure une collecte de secrets de session pour une session de test. Indique clairement dans ton rapport ce qui est observable et ce qui demeure caché par le chiffrement.



## 17. Capture sur interfaces virtuelles, VPN et environnements conteneurisés

Dans un environnement moderne, un poste peut avoir plusieurs interfaces : Ethernet, Wi-Fi, adaptateur VPN, bridge de machine virtuelle, veth de conteneur, loopback et interfaces de gestion. Le même flux peut être vu à plusieurs étapes, parfois sous forme intérieure et extérieure si le trafic est encapsulé. Une capture sur le tunnel peut révéler l’adresse privée intérieure et les protocoles encapsulés ; la capture sur l’interface physique peut montrer seulement les paquets extérieurs destinés au pair VPN. Choisir la mauvaise interface peut donner l’impression que le trafic manque ou qu’une adresse de destination est différente.

### Méthode à deux interfaces

Lorsqu’un VPN est en cause, commence par identifier son interface logique et l’interface physique qui porte le tunnel. Capture brièvement le test sur les deux, si cela est autorisé. Sur l’interface logique, recherche la connexion de l’application vers le serveur final. Sur l’interface physique, recherche la conversation vers le pair VPN. Les horaires permettent d’établir une relation, mais ne supposent pas que chaque paquet intérieur corresponde à une seule trame extérieure : encapsulation, agrégation, fragmentation, chiffrement ou multiplexage peuvent modifier cette relation.

### Conteneurs et bridges

Dans un environnement conteneurisé, les points de capture peuvent inclure le namespace réseau du conteneur, le bridge, la carte de l’hôte ou le lien physique. Les adresses source/destination peuvent changer lors du NAT. Si la capture est prise sur le conteneur, elle peut montrer une adresse privée ; à la sortie de l’hôte, le paquet peut porter une adresse traduite. Pour une analyse correcte, note à quel niveau du chemin chaque capture a été prise et rapproche les paquets à partir des ports, des temps et du contexte de traduction.

### Proxy et terminaison TLS intermédiaire

Un proxy peut terminer la première connexion puis en créer une seconde vers le service final. Une capture côté client montrera la conversation entre le client et le proxy ; côté serveur, elle montrera celle entre le proxy et le serveur. Les deux sessions peuvent avoir des numéros de séquence, adresses, ports et caractéristiques TLS différents. Il est donc incorrect de rechercher une correspondance exacte paquet à paquet sans prendre en compte la terminaison de connexion. Le bon objectif consiste à corréler les opérations au niveau approprié, avec les logs du proxy et des horodatages documentés.



## 18. UDP, QUIC et trafic applicatif moderne

TCP n’est pas le seul transport à examiner. De nombreux services utilisent UDP : DNS traditionnel, VoIP, jeux, protocoles de découverte et QUIC. Une analyse limitée à `tcp` peut manquer la partie la plus importante du trafic. Lorsque tu ouvres une page Web, le navigateur peut choisir HTTP/3 sur QUIC plutôt qu’HTTP sur TCP. Le service utilise souvent le port UDP 443, mais le port seul ne suffit pas à prouver la présence de QUIC ; Wireshark doit reconnaître le protocole selon le contexte et la dissection disponible.

UDP ne propose pas de handshake, d’ACK ou de retransmission au niveau du transport comparable à TCP. L’application peut définir ses propres mécanismes de fiabilité et de retry, ou envoyer les datagrammes sans confirmation. Si une requête UDP ne reçoit pas de réponse, observe les datagrammes et les éventuelles réponses applicatives. Ne cherche pas à identifier un « TCP retransmission » dans une conversation purement UDP. Les concepts de temps d’attente et de perte restent pertinents, mais ils doivent être rattachés au protocole réellement utilisé.

### QUIC : une lecture prudente

QUIC combine des fonctions de transport et de sécurité, et HTTP/3 s’appuie sur QUIC. La capture peut montrer des métadonnées de connexion, des datagrammes, des retransmissions au niveau QUIC reconnus par l’analyseur et des messages visibles selon les conditions. Les détails accessibles dépendent des clés, des versions et de la capture. Un filtre `tcp.port == 443` ne suffit donc pas pour analyser tous les échanges Web chiffrés. Vérifie le transport observé, puis choisis les vues et filtres correspondants.

### Réponse UDP absente

Si le client envoie régulièrement des datagrammes vers un service UDP sans réponse visible, vérifie le point de capture, le port, les adresses et la possibilité d’un filtrage silencieux. Compare à l’autre extrémité si possible. La capture de l’émetteur peut montrer un datagramme prêt à partir, mais ne prouve pas que le réseau l’a livré. La capture du récepteur peut montrer qu’il est arrivé, mais elle ne prouve pas nécessairement que l’application l’a traité. Les journaux du service peuvent être requis pour distinguer réception réseau et traitement applicatif.



## 19. Exporter des preuves et produire un compte rendu

Une bonne analyse laisse derrière elle un résultat que d’autres peuvent vérifier. Le dossier devrait contenir la capture originale protégée, le point de capture et l’intervalle temporel, le filtre utilisé, les numéros de paquets pertinents, les observations, les hypothèses encore ouvertes et les tests complémentaires. Le but n’est pas de livrer un récit confiant, mais une explication traçable. Un collègue doit pouvoir ouvrir le fichier, appliquer le filtre et retrouver les paquets mentionnés.

### Structure recommandée du rapport

**Symptôme.** Décris l’échec observable et la manière de le reproduire. **Périmètre.** Indique client, serveur, protocoles, interface de capture, heure et version des outils. **Observations.** Liste les faits, par exemple « requête DNS au paquet 58 ; réponse correspondante au paquet 59 ; premier SYN vers l’adresse obtenue au paquet 63 ». **Interprétation.** Explique ce que ces faits suggèrent sans dépasser le niveau de preuve. **Vérification.** Indique le test qui confirme ou réfute l’hypothèse. **Résultat.** Précise ce qui a changé après correction et comment le succès a été mesuré. **Limites.** Mentionne le point de capture, le trafic manquant, les protocoles chiffrés ou la synchronisation imparfaite des horloges.

### Extraits de capture et confidentialité

Pour transmettre quelques paquets, utilise une méthode d’export de paquets sélectionnés et explique que l’extrait est partiel. Attention aux secrets : même les protocoles en clair peuvent contenir des noms internes, des paramètres personnels, des jetons ou du contenu de formulaire. Les métadonnées chiffrées peuvent aussi révéler les destinations visitées ou la structure d’activité. Avant de joindre un fichier, inspecte-le, limite les données à l’incident et applique la politique de sécurité de l’organisation.

### Notes et annotations

Enregistre les filtres exacts et les numéros de paquets importants. Les commentaires de paquets et les notes dans le rapport peuvent rendre la revue plus efficace, mais évite de modifier l’original de manière qui ferait disparaître la traçabilité. Si tu crées une version expurgée, conserve le fichier source sécurisé et indique le traitement effectué. Une capture expurgée n’est pas équivalente à l’original et peut supprimer justement les échanges nécessaires à une nouvelle hypothèse.



## 20. Laboratoire guidé : enquête sur une page qui ne s’ouvre pas

Le scénario simule une page Web qui ne s’ouvre pas toujours. Le but est de pratiquer la méthode, pas d’obtenir obligatoirement une seule cause. Utilise un service de test que tu contrôles et note l’heure exacte. Capture sur la machine cliente avant de lancer le navigateur, reproduis une fois, puis arrête la capture après le message d’erreur ou la réussite.

**Étape 1 : vérifie le périmètre.** Note la source, l’interface et la durée. Retire les filtres pour vérifier que les paquets attendus existent. **Étape 2 : examine DNS.** Applique `dns`, cherche le nom demandé, le type et la réponse. Si la résolution réussit, note l’adresse renvoyée. **Étape 3 : suis l’adresse.** Enlève le filtre DNS et filtre l’adresse obtenue. Cherche le SYN initial, ou les datagrammes UDP selon le transport. **Étape 4 : inspecte l’établissement.** Si TCP est utilisé, vérifie la séquence SYN, SYN-ACK et ACK, ainsi que les délais. **Étape 5 : inspecte la suite.** Cherche les premiers échanges TLS ou les données applicatives visibles. Identifie le point où les progrès cessent. **Étape 6 : formule une hypothèse.** Ecris les faits et un test qui pourrait réfuter ton explication. **Étape 7 : reproduis.** Capture une seconde tentative identique et compare la chronologie.

### Jeu de résultats A

La requête DNS apparaît, puis une réponse rapide contenant une adresse. Un SYN TCP part vers l’adresse et un SYN-ACK revient. Le client confirme la connexion, envoie un ClientHello TLS, puis la capture ne montre plus de réponse. Cette séquence ne prouve pas que DNS est défaillant, ni que la connexion TCP n’a pas été établie. La zone à examiner se situe après le début de TLS, mais il reste à confirmer si le serveur reçoit le ClientHello, si la réponse emprunte le même chemin et si la capture enregistre correctement les deux sens. Le test discriminant peut être une capture côté serveur ou un journal TLS côté serveur.

### Jeu de résultats B

Une requête DNS est visible, mais aucune réponse ne figure dans le fichier avant plusieurs retries. Cette observation soutient l’hypothèse d’une absence de réponse au point de capture. Elle ne suffit pas à identifier pourquoi : adresse de résolveur incorrecte, filtrage, réponse perdue, capture sur mauvaise interface, transport DNS différent ou cache applicatif dans un autre test restent possibles. Vérifie la destination de la requête et capture du côté du résolveur si l’accès est autorisé. Si celui-ci reçoit la requête et répond, compare le retour sur le chemin vers le client.

### Jeu de résultats C

Le handshake TCP apparaît complet puis le serveur envoie des données, mais le client les acquitte avec retard ou retransmet certaines données. Observe les numéros de séquence, les plages de données, les ACK et les délais. Ne déduis pas instantanément que le serveur a mal configuré TCP : une capture unique ne prouve pas où la perte s’est produite. Compare côté serveur et côté client ; vérifie aussi que les données et les ACK ne sont pas affectés par un artefact de capture. Documente le symptôme avant de proposer un changement.

### Feuille d’exercice

Écris quatre lignes : (1) fait le plus certain, (2) première étape où le comportement attendu manque, (3) deux causes possibles, (4) preuve complémentaire qui départagerait ces causes. Si tu ne peux pas fournir la quatrième ligne, ton diagnostic n’est pas terminé. La discipline de formuler un test discriminant est l’une des habitudes les plus importantes pour progresser vers une analyse intermédiaire.



## 21. Laboratoire : explorer une conversation TCP avec un filtre reproductible

Sur une capture de test, applique `tcp`. Choisis une conversation et note les deux endpoints et les ports. Applique ensuite un filtre qui cible la conversation, à partir de l’action Follow Stream ou avec une expression explicite. Vérifie les SYN initiaux et l’ordre des paquets. Si le fichier commence au milieu du flux, indique que le handshake initial n’est pas disponible. Ne fabrique pas une chronologie complète si la capture ne contient qu’une partie de l’échange.

Ensuite, applique `tcp.analysis.retransmission`. Si aucun résultat n’apparaît, cela signifie seulement que Wireshark n’a pas signalé de retransmission dans le contexte capturé avec ce filtre et cette version. Cela ne prouve pas l’absence absolue de perte. Si des résultats apparaissent, examine quelques événements et note le segment, sa séquence, sa longueur, les ACK visibles avant et après et les durées. Demande-toi si les retransmissions se concentrent à un moment, dans une direction ou après un silence.

Utilise ensuite le graphe de flux TCP, si disponible dans la version et le contexte du fichier. Compare-le à la liste de paquets. Les visualisations aident à voir le motif, mais elles peuvent cacher des détails dont tu as besoin pour vérifier les séquences et les temps. Le graphe ne remplace pas la lecture des champs et la vérification de la qualité de capture.

Enfin, écris un mini-compte rendu comme si un autre technicien devait refaire le travail. Inclue le nom du fichier de capture, le filtre exact, la conversation analysée, les numéros de paquet importants, la conclusion provisoire et la prochaine action recommandée. Ce rendu doit être précis, court et traçable. L’analyse réseau est plus utile quand elle produit une décision ou un test, plutôt qu’une accumulation de captures d’écran non commentées.



## 22. Erreurs fréquentes des débutants et comment les corriger

**Erreur : croire qu’un paquet rouge est forcément la panne.** Les couleurs dépendent des règles de coloration et du contexte. Lis les champs et la séquence complète. **Erreur : traiter toutes les retransmissions comme une perte confirmée.** Vérifie les ACK, les numéros de séquence, le début de capture et, si possible, un second point d’observation. **Erreur : supposer que HTTPS veut forcément dire TCP.** Vérifie le transport réel ; QUIC/UDP peut être utilisé. **Erreur : croire que le filtre supprime les paquets du fichier.** Le filtre d’affichage masque des lignes ; il ne modifie pas la capture originale. **Erreur : oublier le point de capture.** Documente toujours où l’observation a été faite.

**Erreur : conclure que le serveur est en panne parce qu’il ne répond pas dans la capture client.** Il peut y avoir filtrage, chemin retour différent, problème de capture, ou adresse de destination incorrecte. **Erreur : confondre un délai entre deux paquets avec une mesure pure du réseau.** Le traitement des machines et de l’application peut contribuer au délai. **Erreur : considérer que l’absence de champs lisibles signifie absence de contenu.** Le chiffrement ou une dissection limitée peut empêcher la lecture. **Erreur : appliquer une expression de filtre complexe sans la tester par étapes.** Décompose les conditions et regarde combien de paquets restent à chaque étape.

**Erreur : capturer un volume énorme sans stratégie.** Une capture trop large peut être difficile à partager et exposer des données inutiles. **Erreur : capturer seulement avec un filtre très strict dès le premier essai.** Tu risques d’exclure le paquet qui réfuterait ton hypothèse. **Erreur : modifier simultanément plusieurs paramètres de réseau.** Tu perds la capacité à distinguer la variable qui a changé le résultat. **Erreur : envoyer le fichier complet à un canal public.** Les captures peuvent contenir des informations sensibles. Le respect des règles de confidentialité fait partie de l’expertise technique.



## 23. Quiz de validation avec corrigé

**Question 1.** Quelle est la différence entre un filtre de capture et un filtre d’affichage ? **Réponse :** le filtre de capture décide quels paquets sont enregistrés au moment de la collecte ; le filtre d’affichage limite les paquets visibles sans les retirer du fichier.

**Question 2.** Une capture montre une requête DNS et une réponse avec une adresse, puis un SYN sans réponse visible. Quelle est la première conclusion raisonnable ? **Réponse :** la résolution a reçu une réponse dans cette capture et l’établissement TCP semble ne pas progresser au point d’observation ; il faut examiner le retour, le serveur et le point de capture avant d’attribuer la cause.

**Question 3.** Une ligne « TCP Retransmission » prouve-t-elle qu’un routeur est fautif ? **Réponse :** non. Elle signale un motif détecté à partir de la séquence observée ; elle ne localise pas la cause.

**Question 4.** Pourquoi `tcp.port == 443` ne suffit-il pas toujours à suivre une connexion Web ? **Réponse :** certaines connexions Web utilisent QUIC sur UDP, et d’autres peuvent passer par proxy, tunnel ou transport différent.

**Question 5.** Un checksum sortant est déclaré incorrect sur une capture locale. Quelle autre explication faut-il envisager ? **Réponse :** le checksum offloading ou un autre effet lié au point de capture, avant de conclure à une corruption en transit.

**Question 6.** Une capture ne contient aucun paquet DNS classique. Peut-on conclure que la résolution de nom n’a pas eu lieu ? **Réponse :** non ; cache, résolveur local, DNS chiffré, autre interface ou collecte incomplète sont possibles.

**Question 7.** Que doit contenir un compte rendu reproductible ? **Réponse :** symptôme, point et fenêtre de capture, fichier original, filtre exact, observations, numéros de paquets, hypothèse, test de validation et limites de l’analyse.

**Question 8.** Pourquoi une capture côté serveur est-elle utile quand le client retransmet un SYN ? **Réponse :** elle aide à déterminer si le SYN atteint le serveur et si celui-ci produit une réponse ; une comparaison des points d’observation peut localiser davantage le segment du chemin à investiguer.

**Question 9.** La présence d’un ClientHello suffit-elle à déclarer que TLS échoue ? **Réponse :** non ; il faut regarder la suite, la réponse éventuelle, les alertes visibles, les délais et la complétude du fichier.

**Question 10.** Quelle est la différence entre un fait et une inférence ? **Réponse :** un fait est directement observable dans le fichier ; une inférence est une explication possible des faits, qui nécessite parfois un test supplémentaire pour être confirmée.



## 24. Checklist de démarrage pour chaque nouvelle capture

- [ ] Le symptôme est formulé avec une action reproductible.
- [ ] Le client, la destination, le protocole et la fenêtre horaire sont identifiés.
- [ ] Le point de capture et l’interface sont notés.
- [ ] Le fichier original est conservé dans un emplacement autorisé.
- [ ] La capture contient bien la tentative attendue.
- [ ] Le filtre initial est simple et peut être expliqué.
- [ ] Les requêtes et réponses sont appariées autant que le protocole le permet.
- [ ] Les numéros de séquence, ACK et délais sont vérifiés pour les flux TCP importants.
- [ ] Les protocoles modernes tels que QUIC/UDP ne sont pas oubliés.
- [ ] Les alertes et couleurs ont été examinées dans le contexte.
- [ ] Les faits sont séparés des hypothèses.
- [ ] Une prochaine vérification permet de confirmer ou de réfuter la cause.
- [ ] Le rapport indique les limites de la capture et les précautions prises pour protéger les données.

Cette checklist ne remplace pas le jugement. Elle garantit simplement que les étapes essentielles ne sont pas oubliées sous la pression d’un incident. Au fil de la progression vers les niveaux intermédiaire et expert, la même méthode restera utile, mais elle sera enrichie par la corrélation multi-points, l’analyse de protocoles plus complexes, l’automatisation et les mesures de performance avancées.



## 25. Références officielles et lectures complémentaires

Les menus, noms de champs et fonctions peuvent varier selon la version installée de Wireshark. Lorsque tu utilises un filtre issu d’un ancien support, vérifie toujours la référence de filtres correspondant à ta version. Les références ci-dessous privilégient la documentation officielle afin de permettre une vérification indépendante.

- [Wireshark User’s Guide](https://www.wireshark.org/docs/wsug_html/) — guide de l’interface, des filtres, des vues statistiques, du suivi des flux et des options de capture.
- [Filtering while viewing](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkDisplayFilterSection.html) — explique la différence entre filtres de capture et filtres d’affichage.
- [Expert Information](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvExpert.html) — documentation de la fenêtre Expert Information et des catégories d’alertes.
- [Display Filter Reference: TCP](https://www.wireshark.org/docs/dfref/t/tcp.html) — référence des champs TCP disponibles et des indicateurs d’analyse tels que les retransmissions et ACK dupliqués.
- [TShark man page](https://www.wireshark.org/docs/man-pages/tshark.html) — référence de l’outil en ligne de commande pour lire et analyser des captures.
- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293) — spécification de référence du protocole TCP.
- [RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3](https://www.rfc-editor.org/rfc/rfc8446) — spécification de TLS 1.3.
- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035) — définition historique et fondamentale du DNS, à compléter avec les RFC DNS plus récentes selon le thème étudié.

Quand une information est importante dans un rapport professionnel, cite la documentation et la version du logiciel effectivement utilisée. Les champs calculés par Wireshark dépendent en partie de ce que l’analyseur a observé et de l’implémentation de ses dissectors : une référence de champ permet de comprendre la définition, tandis que les paquets de la capture permettent de juger le cas concret.

---

## Conclusion : du paquet à une explication vérifiable

La maîtrise de Wireshark ne vient pas de la mémorisation d’un grand nombre de filtres, mais de l’habitude de poser des questions précises et de relier les réponses à des faits. Commence par le point de capture, construis le périmètre de la conversation, lis la chronologie, examine les champs qui répondent à la question et garde la distinction entre l’observation et l’hypothèse. Le résultat doit pouvoir être reproduit par une autre personne et doit indiquer ce qu’il ne permet pas de conclure.

Ce niveau débutant prépare la suite. Au niveau intermédiaire, tu pourras corréler plusieurs flux et points de capture, utiliser des filtres composés plus élaborés, analyser plus précisément les performances TCP, TLS, DNS et QUIC et produire des tableaux de mesure. Au niveau expert, tu approfondiras la corrélation multi-capteurs, les artefacts de capture, l’automatisation, l’investigation de systèmes distribués et les preuves nécessaires pour distinguer une anomalie du transport d’une lenteur applicative. Les mêmes règles de rigueur resteront valables : ne pas confondre un indicateur avec une cause, documenter le point de vue et valider les hypothèses.