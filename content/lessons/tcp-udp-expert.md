# TCP, UDP & Ports — Ingénierie et diagnostic expert

> **Niveau :** Expert  
> **Prérequis :** maîtrise du modèle OSI, d'IP, du routage, de TCP/UDP, des sockets, des ports et de Wireshark.  
> **Objectif :** interpréter les comportements avancés du transport, analyser les symptômes de performance, diagnostiquer des problèmes multi-sauts et produire des conclusions reproductibles fondées sur des preuves.

---

## Sommaire

1. Modèle mental expert du transport
2. Identification des flux et espaces de ports
3. Machine à états TCP et gestion des connexions
4. Séquences, ACK, SACK et récupération de pertes
5. Calcul du RTO et retransmissions
6. Fenêtres, contrôle de flux et contrôle de congestion
7. Débit, RTT et produit bande passante-délai
8. Options TCP et particularités des captures
9. UDP, protocoles applicatifs et contrôle de pertes
10. QUIC et transport moderne
11. Ports, sockets, NAT et pare-feu à état
12. Sécurité et limites du transport
13. Méthodologie d'investigation
14. Laboratoires avancés
15. Exercices experts corrigés
16. Modèle de rapport d'incident
17. Références techniques

---

# 1. Modèle mental expert du transport

TCP et UDP fournissent deux abstractions différentes au-dessus d'IP.

TCP offre un flux d'octets fiable et ordonné entre les extrémités d'une connexion. UDP offre un transport par datagrammes sans intégrer les garanties de livraison et d'ordre fournies par TCP.

À un niveau expert, il ne suffit plus de mémoriser ces différences. Il faut déterminer :

- quelles fonctions sont fournies par le transport ;
- quelles fonctions sont prises en charge par le protocole applicatif ;
- quel état est conservé aux extrémités ;
- quels événements permettent de détecter une perte ;
- comment la congestion et la capacité de réception limitent l'envoi ;
- ce qu'un point de capture permet réellement d'observer ;
- quelles modifications sont apportées par NAT, proxy, tunnel ou pare-feu.

## 1.1 Fiabilité et succès applicatif

Une connexion TCP peut transmettre un flux d'octets de façon fiable alors que le serveur renvoie une erreur HTTP.

La fiabilité TCP concerne le transport des données conformément au protocole. Elle ne garantit pas que :

- le serveur possède toutes les ressources nécessaires ;
- la requête est valide ;
- l'utilisateur est authentifié ;
- une transaction a été validée ;
- une modification en base de données a été effectuée ;
- le client a reçu la totalité des résultats attendus au niveau applicatif.

Dans un diagnostic, il faut donc distinguer le succès du transport du succès du traitement applicatif.

## 1.2 Fiabilité et disponibilité

TCP tente de récupérer certaines pertes en s'appuyant sur des mécanismes de contrôle et de retransmission.

Il ne peut pas garantir qu'un correspondant restera disponible indéfiniment. Une connexion peut être interrompue en raison d'une panne, d'un redémarrage, d'une expiration, d'un filtrage ou d'une décision de fermeture.

De même, UDP ne garantit pas que les datagrammes seront livrés, mais une application utilisant UDP peut construire des mécanismes de fiabilité adaptés à son propre modèle de communication.

---

# 2. Identification des flux et espaces de ports

## 2.1 Le tuple du flux

Un flux TCP ou UDP est généralement identifié par les adresses et ports source et destination, associés au protocole de transport.

Exemple documentaire :

```text
TCP 192.0.2.10:51001 → 198.51.100.80:443
```

L'association doit être interprétée à l'emplacement de la capture.

Un NAT peut modifier certaines adresses et certains ports. Un proxy peut terminer une connexion et en créer une nouvelle. Un tunnel peut ajouter une enveloppe extérieure. Ces opérations changent les informations visibles d'un côté à l'autre.

Par conséquent, des tuples différents ne prouvent pas systématiquement que deux communications indépendantes sont en cause.

## 2.2 Les ports ne suffisent pas à identifier une application

Un port peut être utilisé par un service conventionnel, mais l'affectation n'est pas une preuve universelle du protocole applicatif réellement transmis.

Par exemple, un trafic associé au port 443 peut transporter HTTPS sur TCP ou un échange QUIC sur UDP selon la configuration.

Un service personnalisé peut aussi écouter sur un autre port.

Une analyse fiable identifie le protocole observé, les propriétés du flux et les éléments disponibles de la communication. Elle ne se limite pas à une correspondance entre port et nom de service.

## 2.3 Ports système, enregistrés et dynamiques

L'IANA distingue traditionnellement les plages suivantes :

| Catégorie | Plage |
|---|---|
| Ports système | 0–1023 |
| Ports enregistrés | 1024–49151 |
| Ports dynamiques ou privés | 49152–65535 |

Cette classification porte sur les affectations des ports. Elle ne détermine pas à elle seule la stratégie utilisée par chaque système pour sélectionner ses ports sources temporaires.

Les systèmes d'exploitation peuvent employer des plages éphémères différentes. Les applications peuvent également utiliser des ports sources explicitement configurés, dans les limites des règles applicables.

Consultez le [registre officiel IANA des ports](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml) pour vérifier les affectations.

---

# 3. Machine à états TCP et gestion des connexions

TCP est un protocole avec état. Chaque extrémité maintient des informations nécessaires à la connexion.

Ces informations comprennent notamment les numéros de séquence, les accusés de réception, les fenêtres et les éléments de contrôle.

## 3.1 Établissement actif et passif

Dans l'ouverture active classique, un client envoie un SYN et entre dans un état d'attente de la réponse.

Le serveur peut avoir un socket en écoute. Lorsqu'il reçoit une demande valide, il traite l'ouverture selon la machine à états TCP.

Le three-way handshake est le scénario habituel, mais le comportement observé peut être influencé par les retransmissions, les options TCP, les implémentations et des scénarios particuliers comme l'ouverture simultanée.

## 3.2 Pourquoi SYN n'est-il pas une preuve de connexion établie ?

Un paquet SYN visible en sortie indique une tentative d'ouverture, pas une connexion aboutie.

Pour confirmer l'établissement TCP classique, cherchez la réponse SYN-ACK et l'ACK final, tout en tenant compte du point de capture et des éventuelles pertes.

Si seul le SYN est visible, plusieurs explications demeurent possibles :

- le SYN a été perdu après le point de capture ;
- un pare-feu le supprime silencieusement ;
- l'adresse ou la route est incorrecte ;
- le service n'est pas disponible ;
- la réponse est perdue au retour ;
- la capture est incomplète.

La bonne conclusion est donc : « l'ouverture n'est pas confirmée par les observations disponibles », plutôt que « le serveur est nécessairement arrêté ».

## 3.3 Fermeture, half-close et états persistants

TCP autorise les deux extrémités à fermer indépendamment leur direction d'émission. Une extrémité peut ne plus avoir de données à envoyer tout en continuant à recevoir le flux opposé.

Les états `FIN-WAIT`, `CLOSE-WAIT`, `LAST-ACK` et `TIME-WAIT` correspondent à différentes phases de fermeture.

Un diagnostic doit prendre en compte la durée des états et le profil du trafic.

Par exemple, un grand nombre de sockets `CLOSE-WAIT` qui persistent peut justifier l'examen de l'application locale. Des sockets `TIME-WAIT` peuvent être parfaitement normaux pour un service qui ouvre et ferme fréquemment ses connexions.

## 3.4 RST et équipements intermédiaires

Le bit RST indique un comportement de réinitialisation ou de rejet dans le contexte TCP.

Un RST peut provenir du serveur, du client ou d'un équipement intermédiaire capable d'interférer avec le flux.

Pour en déterminer la provenance, examinez :

- le point de capture ;
- l'adresse source du segment ;
- l'état du flux avant le RST ;
- les règles et journaux de sécurité ;
- la présence du même événement sur d'autres interfaces.

L'adresse source visible ne suffit pas toujours à prouver l'origine réelle lorsqu'un dispositif intermédiaire fabrique ou réécrit le trafic.

---

# 4. Séquences, ACK, SACK et récupération des pertes

## 4.1 Séquences TCP

TCP représente les données comme un espace d'octets numérotés.

Les numéros de séquence permettent de suivre l'avancement du flux. Les ACK cumulatifs indiquent généralement le prochain octet attendu par le récepteur.

Une perte dans le flux peut empêcher l'avancement de l'ACK cumulatif alors que d'autres données sont déjà arrivées.

Les applications ne doivent pas interpréter les segments TCP comme des messages indépendants. La segmentation, l'agrégation et le traitement du flux peuvent différer des frontières d'écriture du logiciel.

## 4.2 Données reçues hors ordre

Supposons que le récepteur obtienne les plages A, C et D, mais pas la plage B.

Il peut conserver les données reçues après le trou, selon les capacités et le comportement de son implémentation.

L'ACK cumulatif continue toutefois à refléter le prochain octet attendu. L'émetteur ne dispose donc pas nécessairement de toutes les informations de réception grâce à cet ACK seul.

SACK apporte des informations supplémentaires sur certains blocs de données reçus au-delà du prochain octet cumulativement acquitté.

## 4.3 SACK n'est pas une garantie de récupération immédiate

La présence de SACK ne garantit pas que toutes les pertes seront récupérées sans délai.

La récupération dépend de la négociation des options, du profil de pertes, de la quantité de données en vol, de l'algorithme utilisé et des informations qui parviennent à l'émetteur.

Dans certains scénarios, l'expiration du RTO reste nécessaire.

## 4.4 Schéma SVG animé — Récupération à partir de SACK

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 430" role="img" aria-labelledby="sack-exp-title sack-exp-desc">
<title id="sack-exp-title">Interprétation d'un trou TCP avec SACK</title>
<desc id="sack-exp-desc">Le bloc manquant est coloré en rouge et les blocs reçus hors ordre sont verts. L'indication de récupération pulse indépendamment des segments.</desc>
<rect width="980" height="430" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">SACK : identifier des plages reçues au-delà d'un trou</text>
<g font-family="Arial,sans-serif">
  <text x="50" y="81" font-size="15" font-weight="700" fill="#334155">Espace de séquence illustratif</text>
  <rect x="50" y="103" width="180" height="62" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="140" y="129" text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">Bloc A</text><text x="140" y="149" text-anchor="middle" font-size="13" fill="#14532d">Reçu</text>
  <rect x="248" y="103" width="180" height="62" rx="8" fill="#fecaca" stroke="#b91c1c" stroke-width="2"/>
  <text x="338" y="129" text-anchor="middle" font-size="14" font-weight="700" fill="#991b1b">Bloc B</text><text x="338" y="149" text-anchor="middle" font-size="13" fill="#991b1b">Manquant</text>
  <rect x="446" y="103" width="180" height="62" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="536" y="129" text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">Bloc C</text><text x="536" y="149" text-anchor="middle" font-size="13" fill="#14532d">Reçu hors ordre</text>
  <rect x="644" y="103" width="180" height="62" rx="8" fill="#bbf7d0" stroke="#15803d" stroke-width="2"/>
  <text x="734" y="129" text-anchor="middle" font-size="14" font-weight="700" fill="#14532d">Bloc D</text><text x="734" y="149" text-anchor="middle" font-size="13" fill="#14532d">Reçu hors ordre</text>
  <rect x="45" y="191" width="785" height="82" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="68" y="220" font-size="16" font-weight="700" fill="#1e3a8a">ACK cumulatif</text>
  <text x="68" y="245" font-size="14" fill="#1e3a8a">Indique encore le prochain octet attendu au début du bloc B.</text>
  <rect x="45" y="294" width="785" height="75" rx="10" fill="#dcfce7" stroke="#16a34a" stroke-width="2">
    <animate attributeName="stroke-opacity" values="0.25;1;0.25" dur="3s" repeatCount="indefinite"/>
  </rect>
  <text x="68" y="322" font-size="16" font-weight="700" fill="#166534">Informations SACK</text>
  <text x="68" y="346" font-size="14" fill="#166534">Peuvent signaler les blocs C et D reçus malgré le trou dans le flux.</text>
  <text x="50" y="397" font-size="13" fill="#64748b">L'exemple représente les principes de réception hors ordre ; les plages exactes dépendent du flux observé.</text>
</g>
</svg>

## 4.5 Que rechercher dans Wireshark ?

Pour une investigation de pertes :

1. Identifiez le flux et la direction observée.
2. Notez les numéros de séquence et d'acquittement.
3. Examinez les ACK dupliqués.
4. Vérifiez les options SACK lorsque celles-ci sont présentes.
5. Cherchez les retransmissions et leurs délais.
6. Examinez le point de capture et sa capacité à observer tous les segments.
7. Corrélez avec la fenêtre de réception, le RTT et la congestion.

La présence d'un trou apparent dans une capture peut être causée par une perte de capture. Une capture prise en un seul point ne suffit pas toujours à identifier l'emplacement réel de la perte.

---

# 5. Calcul du RTO et retransmissions

## 5.1 Objectif du retransmission timeout

Le RTO protège TCP contre l'absence d'acquittement des données en attente.

Le système ne peut pas simplement choisir un délai très court et retransmettre dès qu'un ACK tarde légèrement. Les chemins réseau possèdent des délais variables et certains ACK sont retardés par les mécanismes normaux du transport.

À l'inverse, un délai trop long peut ralentir la récupération d'une perte.

L'algorithme de calcul doit donc tenir compte de l'estimation du RTT et de sa variabilité.

## 5.2 RTT échantillonné et ambiguïté des retransmissions

Un RTT mesuré correspond à un événement d'envoi et à la réception d'un retour associé, selon la méthode de mesure.

Lorsqu'un segment est retransmis, un ACK ultérieur peut être difficile à associer de façon certaine à la première transmission ou à la retransmission. Cette ambiguïté doit être considérée dans l'estimation du RTT.

Les règles de mesure et de gestion du temporisateur sont définies par la spécification TCP et les documents associés.

## 5.3 Temporisateur expiré

Après une expiration du RTO, TCP peut retransmettre les données en attente et appliquer un backoff du temporisateur conformément aux règles en vigueur.

Ce comportement ralentit la répétition des envois si aucune réponse n'est obtenue, plutôt que d'envoyer indéfiniment au même rythme.

Une capture qui montre plusieurs retransmissions de la même plage de séquence doit être étudiée avec leurs intervalles et les ACK observés.

## 5.4 Schéma SVG animé — Temporisation de retransmission

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 400" role="img" aria-labelledby="rto-exp-title rto-exp-desc">
<title id="rto-exp-title">Temporisateur de retransmission TCP</title>
<desc id="rto-exp-desc">Une ligne de temps montre une transmission, l'absence d'ACK visible et une retransmission. Les intervalles du minuteur s'allongent pour illustrer le backoff sans représenter des durées réelles.</desc>
<rect width="960" height="400" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">RTO : retransmettre en l'absence d'ACK</text>
<g font-family="Arial,sans-serif">
  <text x="45" y="84" font-size="15" font-weight="700" fill="#334155">Temps croissant →</text>
  <path d="M70 143 H885" stroke="#64748b" stroke-width="3"/>
  <path d="M872 133 l13 10 -13 10" fill="none" stroke="#64748b" stroke-width="3"/>
  <rect x="80" y="112" width="126" height="62" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="143" y="137" text-anchor="middle" font-size="14" font-weight="700" fill="#1e3a8a">Envoi</text><text x="143" y="157" text-anchor="middle" font-size="13" fill="#1e3a8a">Données</text>
  <rect x="270" y="112" width="155" height="62" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="347" y="137" text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">Attente</text><text x="347" y="157" text-anchor="middle" font-size="13" fill="#92400e">RTO initial</text>
  <rect x="485" y="112" width="145" height="62" rx="8" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
  <text x="557" y="137" text-anchor="middle" font-size="14" font-weight="700" fill="#991b1b">Expiration</text><text x="557" y="157" text-anchor="middle" font-size="13" fill="#991b1b">Retransmission</text>
  <rect x="690" y="112" width="195" height="62" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <text x="787" y="137" text-anchor="middle" font-size="14" font-weight="700" fill="#5b21b6">Nouvelle attente</text><text x="787" y="157" text-anchor="middle" font-size="13" fill="#5b21b6">RTO adapté</text>
  <rect x="270" y="202" width="155" height="12" rx="5" fill="#fcd34d">
    <animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/>
  </rect>
  <rect x="485" y="202" width="145" height="12" rx="5" fill="#f87171">
    <animate attributeName="opacity" values="1;0.25;1" dur="2.3s" repeatCount="indefinite"/>
  </rect>
  <rect x="690" y="202" width="195" height="12" rx="5" fill="#a78bfa">
    <animate attributeName="width" values="195;170;195" dur="3.5s" repeatCount="indefinite"/>
  </rect>
  <text x="70" y="264" font-size="15" font-weight="700" fill="#334155">À examiner lors d'un incident</text>
  <text x="70" y="291" font-size="14" fill="#475569">RTT estimé, variabilité du délai, ACK reçus, retransmissions et emplacement de la capture.</text>
  <text x="70" y="322" font-size="14" fill="#475569">Plusieurs retransmissions ne localisent pas à elles seules le point de perte.</text>
  <text x="70" y="363" font-size="13" fill="#64748b">Diagramme conceptuel : ni les durées ni les proportions ne représentent un algorithme mesuré.</text>
</g>
</svg>

---

# 6. Fenêtres, contrôle de flux et contrôle de congestion

## 6.1 Fenêtre de réception : `rwnd`

La fenêtre de réception exprime la quantité de données que le récepteur peut annoncer comme acceptable dans le contexte du flux.

Une fenêtre nulle peut indiquer que le récepteur ne peut pas accepter davantage de données pour le moment.

Pour analyser ce cas, examinez les annonces de fenêtre et leur évolution, puis vérifiez l'application qui consomme les données ainsi que les ressources du système.

## 6.2 Fenêtre de congestion : `cwnd`

La fenêtre de congestion limite la quantité de données que l'émetteur est autorisé à avoir en vol selon son algorithme.

Elle tient compte de la congestion présumée sur le chemin.

`rwnd` et `cwnd` ne représentent donc pas le même mécanisme.

Dans un modèle simplifié, la quantité de données en vol doit respecter les limites associées à ces deux fenêtres, ainsi que d'autres contraintes pertinentes.

## 6.3 Pourquoi le débit peut-il plafonner ?

Un transfert TCP peut être limité par :

- la fenêtre annoncée par le récepteur ;
- la fenêtre de congestion ;
- la capacité disponible sur le réseau ;
- les pertes et la récupération ;
- la latence aller-retour ;
- la puissance de traitement des extrémités ;
- les mécanismes d'offload ;
- les politiques de sécurité ;
- l'application et sa manière de produire ou consommer les données.

Un test de débit faible ne suffit donc pas à diagnostiquer la congestion.

Il faut déterminer quel mécanisme limite effectivement l'envoi.

## 6.4 Schéma SVG animé — Fenêtres TCP

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 430" role="img" aria-labelledby="window-exp-title window-exp-desc">
<title id="window-exp-title">Fenêtre de réception et fenêtre de congestion TCP</title>
<desc id="window-exp-desc">Deux barres montrent la limite du récepteur et la limite de congestion. Une troisième barre s'adapte de façon animée à la plus petite des deux limites pour illustrer la contrainte commune.</desc>
<rect width="980" height="430" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">Ce qui limite les données en vol</text>
<g font-family="Arial,sans-serif">
  <text x="55" y="87" font-size="16" font-weight="700" fill="#334155">Fenêtre de réception (rwnd)</text>
  <rect x="55" y="101" width="800" height="35" rx="7" fill="#e2e8f0"/>
  <rect x="55" y="101" width="610" height="35" rx="7" fill="#bbf7d0" stroke="#15803d" stroke-width="2">
    <animate attributeName="width" values="610;470;610" dur="4.5s" repeatCount="indefinite"/>
  </rect>
  <text x="55" y="163" font-size="16" font-weight="700" fill="#334155">Fenêtre de congestion (cwnd)</text>
  <rect x="55" y="177" width="800" height="35" rx="7" fill="#e2e8f0"/>
  <rect x="55" y="177" width="500" height="35" rx="7" fill="#bfdbfe" stroke="#2563eb" stroke-width="2">
    <animate attributeName="width" values="500;680;500" dur="5.2s" repeatCount="indefinite"/>
  </rect>
  <text x="55" y="241" font-size="16" font-weight="700" fill="#334155">Données autorisées en vol (modèle simplifié)</text>
  <rect x="55" y="255" width="800" height="35" rx="7" fill="#e2e8f0"/>
  <rect x="55" y="255" width="500" height="35" rx="7" fill="#ddd6fe" stroke="#7c3aed" stroke-width="2">
    <animate attributeName="width" values="500;470;500" dur="4.1s" repeatCount="indefinite"/>
  </rect>
  <text x="55" y="327" font-size="14" fill="#334155">Le contrôle de flux protège la capacité annoncée par le récepteur.</text>
  <text x="55" y="352" font-size="14" fill="#334155">Le contrôle de congestion limite l'injection de données dans le réseau.</text>
  <text x="55" y="383" font-size="13" fill="#64748b">Les barres sont illustratives : elles ne mesurent pas les fenêtres d'une connexion réelle.</text>
</g>
</svg>

## 6.5 Algorithmes de congestion

TCP ne possède pas un unique algorithme de congestion universel.

Les implémentations peuvent utiliser différentes variantes conformes aux spécifications applicables.

Les principes classiques incluent :

- démarrage progressif ;
- évitement de congestion ;
- récupération rapide ;
- adaptation après une perte ou un autre signal de congestion.

CUBIC est un algorithme largement déployé, particulièrement étudié pour les réseaux à débit élevé et les chemins à longue distance. Sa spécification est disponible dans le [RFC 9438](https://www.rfc-editor.org/rfc/rfc9438.html).

Les implémentations peuvent différer. Il ne faut pas déduire l'algorithme exact d'une connexion uniquement à partir d'un symptôme de débit.

---

# 7. Débit, RTT et produit bande passante-délai

## 7.1 Le produit bande passante-délai

Le produit bande passante-délai, souvent noté BDP, représente la quantité de données qui peut être présente sur un chemin en fonction de son débit et de son délai.

Dans un modèle simplifié :

`BDP = capacité du chemin × RTT`

Supposons un chemin de 100 Mbit/s avec un RTT de 80 ms.

Conversion :

```text
RTT = 0,08 seconde
Capacité = 100 000 000 bits/s

BDP = 100 000 000 × 0,08
    = 8 000 000 bits
    = 1 000 000 octets
```

Ce calcul donne un BDP d'environ un million d'octets dans ce modèle simplifié.

Il ne constitue pas une prédiction du débit applicatif. Les pertes, les fenêtres, les files d'attente, les autres flux, les coûts de protocole et la capacité de traitement peuvent modifier fortement le résultat.

## 7.2 Pourquoi la fenêtre compte-t-elle ?

Si une fenêtre autorise trop peu de données en vol par rapport au BDP du chemin, l'émetteur peut devoir attendre des ACK avant d'envoyer davantage de données.

Cela peut limiter l'utilisation de la capacité du réseau, particulièrement lorsque le RTT est élevé.

Les options de fenêtre, la taille des buffers, le contrôle de congestion et l'application peuvent donc influencer le débit réellement obtenu.

## 7.3 Ne pas confondre débit et latence

Un transfert peut atteindre un débit élevé tout en subissant une latence importante.

À l'inverse, une petite requête peut présenter une réponse rapide sans nécessiter un débit élevé.

Pour une application interactive, il faut considérer le délai et sa variabilité. Pour un transfert volumineux, il faut également examiner le débit, les pertes, la fenêtre, la congestion et la capacité du chemin.

## 7.4 Schéma SVG animé — Effet du RTT sur un envoi par fenêtres

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 970 420" role="img" aria-labelledby="bdp-exp-title bdp-exp-desc">
<title id="bdp-exp-title">Données en vol et délai aller-retour</title>
<desc id="bdp-exp-desc">Deux panneaux illustrent une petite fenêtre de données en vol et une fenêtre plus importante sur le même modèle de chemin. Les barres d'occupation s'animent indépendamment pour représenter l'effet de la quantité de données en vol.</desc>
<rect width="970" height="420" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">BDP : quantité de données en vol</text>
<g font-family="Arial,sans-serif">
  <rect x="35" y="75" width="425" height="265" rx="12" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="2"/>
  <text x="60" y="109" font-size="17" font-weight="700" fill="#334155">Fenêtre limitée</text>
  <text x="60" y="134" font-size="13" fill="#475569">Peu de données en vol</text>
  <rect x="60" y="166" width="370" height="35" rx="7" fill="#e2e8f0"/>
  <rect x="60" y="166" width="95" height="35" rx="7" fill="#bfdbfe" stroke="#2563eb" stroke-width="2">
    <animate attributeName="width" values="95;120;95" dur="3s" repeatCount="indefinite"/>
  </rect>
  <text x="60" y="231" font-size="14" fill="#334155">Une fenêtre trop petite peut</text>
  <text x="60" y="252" font-size="14" fill="#334155">laisser la capacité du chemin</text>
  <text x="60" y="273" font-size="14" fill="#334155">sous-utilisée.</text>
  <rect x="510" y="75" width="425" height="265" rx="12" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="2"/>
  <text x="535" y="109" font-size="17" font-weight="700" fill="#334155">Fenêtre adaptée</text>
  <text x="535" y="134" font-size="13" fill="#475569">Plus de données en vol</text>
  <rect x="535" y="166" width="370" height="35" rx="7" fill="#e2e8f0"/>
  <rect x="535" y="166" width="310" height="35" rx="7" fill="#bbf7d0" stroke="#15803d" stroke-width="2">
    <animate attributeName="width" values="310;340;310" dur="3.5s" repeatCount="indefinite"/>
  </rect>
  <text x="535" y="231" font-size="14" fill="#334155">Une quantité de données en vol</text>
  <text x="535" y="252" font-size="14" fill="#334155">adaptée au chemin peut améliorer</text>
  <text x="535" y="273" font-size="14" fill="#334155">l'utilisation de la capacité.</text>
  <text x="35" y="377" font-size="13" fill="#64748b">Illustration conceptuelle, sans mesure de débit : la performance dépend aussi de la congestion, des pertes et des extrémités.</text>
</g>
</svg>

---

# 8. Options TCP et particularités des captures

## 8.1 MSS et Window Scale

MSS annonce une taille de données TCP proposée pour les segments, hors en-têtes TCP et IP.

Window Scale permet de représenter des fenêtres de réception plus grandes. Ces options sont négociées au début de la connexion, sous réserve des règles applicables.

Pour comprendre un débit limité, examinez les options négociées, les fenêtres annoncées, les séquences et les ACK plutôt que de supposer qu'une seule option explique le résultat.

## 8.2 SACK

SACK ajoute des informations de réception qui facilitent l'identification de certaines pertes. Il ne remplace pas les numéros de séquence ou les ACK cumulatifs, et n'est pas une garantie de récupération sans délai.

## 8.3 Timestamps et autres options

TCP peut utiliser des options supplémentaires pour certains mécanismes de fonctionnement et d'observation.

Leurs effets dépendent de la négociation, de l'implémentation et des équipements du chemin. Un équipement intermédiaire peut aussi modifier le trafic ou ses options dans certaines architectures.

Ne concluez pas qu'une option est absente partout simplement parce qu'elle n'apparaît pas dans une capture prise à un seul endroit.

## 8.4 Checksum apparent incorrect

Une capture effectuée sur l'émetteur peut montrer un checksum incorrect parce que le calcul est délégué à la carte réseau et se produit après le point de capture.

Les mécanismes d'offload peuvent aussi modifier les frontières des segments visibles sur l'hôte.

Avant de déclarer une corruption réelle, vérifiez :

- le point de capture ;
- les propriétés de la carte réseau ;
- les offloads utilisés ;
- la présence du même phénomène dans une capture externe ;
- les effets de l'agrégation et de la segmentation matérielles.

Une capture externe peut fournir une observation plus proche des paquets transmis sur le lien, mais elle possède elle aussi ses propres limites.

---

# 9. UDP, protocoles applicatifs et contrôle des pertes

## 9.1 UDP ne signifie pas absence d'état applicatif

UDP ne fournit pas de connexion avec état équivalente à TCP, mais une application peut suivre des échanges et conserver un état.

Un protocole applicatif peut enregistrer :

- l'identifiant d'une requête ;
- l'identité logique du pair ;
- la durée de validité de l'échange ;
- les messages attendus ;
- le nombre de tentatives ;
- les données déjà traitées.

Ce comportement est contrôlé par l'application, et non garanti par UDP lui-même.

## 9.2 Identifiants, retransmissions et déduplication

Lorsqu'un protocole applicatif basé sur UDP ajoute de la fiabilité, il doit traiter les duplications possibles.

Si une requête est retransmise après la perte supposée de sa réponse, le serveur peut recevoir plusieurs exemplaires de la même requête.

Sans mécanisme de déduplication ou d'idempotence adapté, l'application risque d'exécuter deux fois une opération.

Les conséquences dépendent du type de transaction. Une opération de lecture répétable ne présente pas les mêmes risques qu'une opération financière ou qu'une modification d'état.

Il faut distinguer les propriétés de transport des garanties applicatives.

## 9.3 Délai, ordre et tolérance à la perte

Une application temps réel peut décider qu'un ancien message n'a plus d'utilité au moment de sa réception.

Une autre application peut exiger la réception de tous les messages dans leur ordre logique.

UDP permet de choisir des mécanismes spécifiques, mais oblige l'application à concevoir leur comportement si elle souhaite davantage que la livraison par datagramme offerte par le transport.

## 9.4 UDP et fragmentation

La fragmentation peut ajouter des risques et des contraintes de fonctionnement lorsque les datagrammes sont trop volumineux pour le chemin.

Pour les applications qui utilisent UDP, il faut considérer la MTU disponible, les en-têtes d'encapsulation et le comportement souhaité face aux pertes.

Un succès local de l'envoi ne prouve pas que l'intégralité du datagramme sera reçue par l'application distante.

---

# 10. QUIC et transport moderne

QUIC fournit un transport moderne au-dessus d'UDP. Il combine des mécanismes de connexion, des flux, du contrôle de flux, de la sécurité et de la gestion des pertes.

HTTP/3 utilise QUIC.

## 10.1 Pourquoi QUIC utilise-t-il UDP ?

UDP fournit la base de datagrammes IP sur laquelle QUIC construit sa logique de transport.

Cela permet à QUIC d'intégrer directement différents mécanismes au niveau du protocole supérieur, au lieu de dépendre entièrement du comportement de TCP.

QUIC utilise notamment TLS pour négocier et protéger la communication. Sa spécification définit le fonctionnement du transport et des paramètres de connexion.

## 10.2 Flux QUIC

QUIC prend en charge des flux de données multiplexés.

La perte de données dans un flux n'implique pas nécessairement le même type de blocage applicatif que dans un protocole qui place tout le contenu dans un unique flux d'octets TCP.

Cependant, QUIC n'élimine pas toutes les contraintes du réseau, toutes les pertes ou tous les délais. Les données retransmises, les mécanismes de congestion et l'état du chemin restent importants.

## 10.3 Migration du chemin

QUIC possède des mécanismes qui permettent, sous certaines conditions, de maintenir la connexion malgré un changement du chemin réseau.

Cela peut être utile dans des environnements où l'interface ou le chemin du client change, mais le comportement exact dépend du protocole, des identifiants de connexion et de la configuration.

Lorsqu'un flux UDP change d'adresse source, il ne faut donc pas automatiquement supposer qu'il s'agit d'une nouvelle session QUIC, pas plus qu'il ne faut conclure qu'une application UDP quelconque prend en charge une migration similaire.

## 10.4 Diagnostic HTTP/3

Pour une application Web moderne :

1. Déterminez quel protocole de transport est réellement utilisé.
2. Vérifiez si le trafic est TCP ou UDP.
3. Identifiez les éventuels changements de chemin.
4. Vérifiez les règles de filtrage correspondant à chaque transport.
5. Distinguez la connexion de transport de la réponse applicative.
6. Examinez les captures et journaux disponibles au bon emplacement.

Le port 443 ne signifie pas exclusivement TCP. Les flux HTTP/3 basés sur QUIC utilisent couramment UDP/443.

---

# 11. Ports, sockets, NAT et pare-feu à état

## 11.1 Liaison d'un socket

Lorsqu'une application demande à utiliser un port, le système doit vérifier les règles de liaison et la disponibilité du point d'extrémité.

Selon le système et la configuration, plusieurs applications ne peuvent pas nécessairement lier les mêmes adresses et ports de la manière souhaitée.

Les capacités de partage de port et les règles de réutilisation dépendent du système d'exploitation et des options choisies.

Pour un diagnostic, relevez :

- l'adresse locale associée ;
- le port ;
- le protocole ;
- l'état du socket ;
- le processus propriétaire lorsque cette information est disponible ;
- les erreurs de liaison éventuelles.

## 11.2 NAT et suivi d'état

Une traduction NAT peut être associée à une entrée d'état temporaire.

Le dispositif conserve les informations requises pour associer les paquets de retour au flux traduit, selon le mécanisme utilisé.

Une entrée supprimée, expirée ou incorrecte peut interrompre une communication même lorsque le service distant fonctionne.

L'investigation doit comparer les informations internes et externes du flux, puis vérifier l'état de traduction et les journaux du dispositif.

## 11.3 Pare-feu à état et asymétrie

Un pare-feu à état suit les échanges selon ses mécanismes.

Une route asymétrique peut produire une difficulté lorsque le trafic retour ne traverse pas l'équipement qui détient l'état attendu.

L'asymétrie n'est pas automatiquement interdite ni toujours problématique. Elle devient importante lorsque les politiques et le fonctionnement des équipements nécessitent de voir les deux directions.

Pour confirmer ce scénario, examinez les routes aller et retour, les états des connexions, les journaux de filtrage et les captures effectuées aux points appropriés.

---

# 12. Sécurité et limites du transport

TCP et UDP ne fournissent pas, à eux seuls, un ensemble complet de garanties de sécurité applicative.

Les numéros de port ne sont pas un mécanisme d'authentification.

Un port habituel de service ne prouve pas que le protocole attendu est utilisé. Un trafic visible sur UDP ou TCP ne garantit pas que l'application est digne de confiance.

Les propriétés de confidentialité, d'intégrité ou d'authentification doivent être assurées par les mécanismes appropriés au protocole et au contexte.

## 12.1 Risques de disponibilité

Des volumes élevés de tentatives de connexion ou des datagrammes anormaux peuvent solliciter les ressources du système et des équipements intermédiaires.

Le diagnostic de ces problèmes doit respecter les autorisations et les procédures de sécurité de l'organisation.

Lors d'une capture, évitez de collecter ou de diffuser des données confidentielles qui ne sont pas nécessaires à l'investigation.

## 12.2 Données sensibles dans les captures

Les captures peuvent inclure des métadonnées, des noms d'hôtes, des adresses internes et parfois des contenus applicatifs non chiffrés.

Conservez-les conformément aux règles de l'organisation. Partagez uniquement les données nécessaires avec les personnes autorisées et masquez les secrets lorsque cela est possible sans rendre le diagnostic inexploitable.

---

# 13. Méthodologie d'investigation experte

Une investigation avancée doit séparer les faits, les hypothèses et les conclusions.

## 13.1 Définir le symptôme précisément

Exemples :

- la connexion TCP n'achève pas le handshake ;
- l'établissement TCP réussit, mais les données applicatives n'avancent pas ;
- les transferts volumineux subissent des retransmissions ;
- les connexions se terminent immédiatement avec RST ;
- les clients rencontrent des blocages intermittents ;
- l'accès au service fonctionne sur TCP mais échoue sur le transport réellement utilisé par HTTP/3.

Un symptôme précis permet de choisir les bons points d'observation.

## 13.2 Cartographier les points de terminaison

Identifiez :

- l'adresse et le port source ;
- l'adresse et le port destination ;
- le protocole de transport ;
- les éventuels NAT ;
- les proxys qui terminent les connexions ;
- les tunnels traversés ;
- les pare-feu qui suivent l'état des flux ;
- les interfaces où le trafic peut être capturé.

La représentation doit être basée sur l'architecture réelle, et non sur une topologie supposée.

## 13.3 Corréler les captures

Les captures multi-points peuvent aider à localiser une divergence entre l'émission et la réception.

Pour les corréler, utilisez les informations pertinentes : tuple, séquences, ACK, chronologie, paramètres IP et transformations connues.

Un paquet IP qui passe par un routeur peut apparaître avec une trame de liaison différente. Un proxy peut terminer une connexion et en créer une autre. Une capture locale peut être influencée par les offloads.

Ne recherchez donc pas systématiquement une identité parfaite des paquets à tous les points.

## 13.4 Établir la première divergence

Exemple de raisonnement :

- le client transmet un SYN ;
- le SYN est visible à proximité du routeur d'entrée ;
- il est absent près du serveur ;
- les captures sont complètes dans la fenêtre temporelle étudiée ;
- les journaux du pare-feu montrent un rejet correspondant.

Ce faisceau de preuves est beaucoup plus fort qu'une simple absence de réponse au client.

Sans confirmation sur la capture, les journaux ou la topologie, l'absence observée peut toutefois provenir d'un défaut de collecte et non d'une perte réelle.

## 13.5 Valider la correction

Après une correction :

1. Reproduisez le test initial.
2. Vérifiez que le symptôme a disparu dans les mêmes conditions.
3. Testez un scénario voisin.
4. Contrôlez les métriques et journaux pertinents.
5. Documentez les limites de la validation.
6. Conservez un plan de retour arrière pour les changements importants.

Le rétablissement apparent d'un seul flux ne prouve pas que tous les scénarios affectés sont corrigés.

---

# 14. Schéma SVG animé — Corrélation de captures multi-points

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 440" role="img" aria-labelledby="capture-exp-title capture-exp-desc">
<title id="capture-exp-title">Localiser une divergence entre captures réseau</title>
<desc id="capture-exp-desc">Trois points d'observation successifs indiquent le même flux. Une ligne active entre les premiers points pulse tandis qu'une divergence est signalée entre le second et le troisième. Le dessin représente une méthode d'analyse et non une panne mesurée.</desc>
<rect width="980" height="440" rx="18" fill="#f8fafc"/>
<text x="28" y="38" font-size="23" font-family="Arial,sans-serif" font-weight="700" fill="#0f172a">Corréler les observations d'un même flux</text>
<g font-family="Arial,sans-serif">
  <rect x="35" y="110" width="240" height="100" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="155" y="143" text-anchor="middle" font-size="17" font-weight="700" fill="#1e3a8a">Capture A</text>
  <text x="155" y="169" text-anchor="middle" font-size="14" fill="#1e3a8a">Côté client</text>
  <text x="155" y="190" text-anchor="middle" font-size="13" fill="#1e3a8a">SYN observé</text>
  <rect x="370" y="110" width="240" height="100" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="490" y="143" text-anchor="middle" font-size="17" font-weight="700" fill="#166534">Capture B</text>
  <text x="490" y="169" text-anchor="middle" font-size="14" fill="#166534">Après le transit</text>
  <text x="490" y="190" text-anchor="middle" font-size="13" fill="#166534">SYN observé</text>
  <rect x="705" y="110" width="240" height="100" rx="12" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
  <text x="825" y="143" text-anchor="middle" font-size="17" font-weight="700" fill="#991b1b">Capture C</text>
  <text x="825" y="169" text-anchor="middle" font-size="14" fill="#991b1b">Côté serveur</text>
  <text x="825" y="190" text-anchor="middle" font-size="13" fill="#991b1b">SYN absent dans l'exemple</text>
  <path d="M275 160 H365" stroke="#2563eb" stroke-width="4" stroke-dasharray="10 8">
    <animate attributeName="stroke-dashoffset" values="0;-40" dur="1.5s" repeatCount="indefinite"/>
  </path>
  <path d="M353 149 l12 11 -12 11" fill="none" stroke="#2563eb" stroke-width="3"/>
  <path d="M610 160 H700" stroke="#b91c1c" stroke-width="4" stroke-dasharray="10 8" opacity="0.35"/>
  <path d="M630 145 L680 175 M680 145 L630 175" stroke="#b91c1c" stroke-width="4">
    <animate attributeName="stroke-opacity" values="0.3;1;0.3" dur="2.3s" repeatCount="indefinite"/>
  </path>
  <rect x="55" y="265" width="870" height="100" rx="12" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="80" y="295" font-size="16" font-weight="700" fill="#334155">Interprétation prudente</text>
  <text x="80" y="322" font-size="14" fill="#334155">La première divergence oriente l'investigation vers l'intervalle entre B et C.</text>
  <text x="80" y="344" font-size="14" fill="#334155">Avant de conclure, validez les points de capture, les pertes de collecte et les transformations du flux.</text>
  <text x="35" y="402" font-size="13" fill="#64748b">Le schéma est une méthode de raisonnement, pas une preuve qu'un équipement donné perd le trafic.</text>
</g>
</svg>

---

# 15. Laboratoires avancés

## TP 1 — Diagnostic d'un handshake incomplet

**Objectif :** localiser les points à vérifier quand une connexion TCP ne s'établit pas.

1. Identifiez un service autorisé à tester.
2. Capturez le flux à proximité du client.
3. Si possible, obtenez une seconde capture proche du serveur.
4. Notez les SYN, SYN-ACK, ACK et retransmissions.
5. Relevez les adresses, ports, interfaces et heures.
6. Vérifiez le filtrage et les routes entre les points.
7. Comparez les observations avant de conclure.

**Validation attendue :** un rapport qui détermine ce qui est établi par les captures et ce qui reste hypothétique.

## TP 2 — Comparer RTT et débit

**Objectif :** comprendre pourquoi le délai et la quantité de données en vol influencent le débit.

1. Mesurez le RTT vers une cible autorisée.
2. Relevez le débit réellement obtenu par un transfert contrôlé.
3. Calculez un BDP approximatif.
4. Examinez la fenêtre et les retransmissions si une capture adaptée est disponible.
5. Comparez les résultats à plusieurs moments, en maintenant le test aussi constant que possible.
6. Expliquez les limites de cette estimation.

**Attention :** un BDP estimé ne permet pas de déterminer seul la taille optimale des buffers ou la performance d'une application.

## TP 3 — Examiner un comportement UDP

**Objectif :** distinguer le succès de l'envoi local du succès de la communication.

1. Identifiez un protocole UDP autorisé à analyser.
2. Déterminez à quoi ressemble une requête valide.
3. Capturez la requête et la réponse éventuelle.
4. Comparez les tuples et le contenu des datagrammes.
5. Examinez les règles de sécurité et les captures distantes disponibles.
6. Documentez pourquoi l'absence de réponse est significative ou non pour ce protocole.

## TP 4 — Étudier HTTP/3

**Objectif :** distinguer QUIC de TCP.

1. Utilisez un environnement où HTTP/3 est pris en charge et autorisé.
2. Capturez le trafic du client.
3. Vérifiez si le flux utilise UDP et QUIC.
4. Comparez le comportement avec une connexion basée sur TCP si le client et le serveur le permettent.
5. Tenez compte du fait que le contenu applicatif protégé ne sera pas directement lisible dans une capture ordinaire.
6. Notez les différences sans en déduire que l'un des transports est toujours supérieur.

## TP 5 — Investigation d'un NAT

**Objectif :** mettre en correspondance les flux observés de part et d'autre d'une traduction.

1. Choisissez un flux autorisé et documenté.
2. Relevez le tuple interne.
3. Relevez le tuple externe.
4. Examinez l'état de traduction disponible.
5. Vérifiez les règles et journaux de sécurité.
6. Déterminez si le trafic retour est associé à la traduction attendue.
7. Documentez les preuves qui établissent la relation entre les deux observations.

---

# 16. Exercices experts corrigés

## Exercice 1 — ACK sans avancement

Une capture présente plusieurs ACK avec le même numéro d'acquittement, tandis que des données plus récentes sont visibles dans le sens aller.

Que peut-on en déduire ? Pourquoi ne faut-il pas conclure immédiatement à une perte sur un routeur précis ?

### Corrigé

Des ACK qui n'avancent pas peuvent être compatibles avec un trou dans l'espace de séquence. Le récepteur peut avoir reçu certaines données hors ordre sans pouvoir faire avancer l'ACK cumulatif.

Une perte est une hypothèse possible, mais la capture doit être complète et correctement placée. Les informations SACK, les captures distantes et la chronologie peuvent aider à établir ce qui se passe.

## Exercice 2 — Fenêtre nulle

Le client reçoit une annonce de fenêtre TCP nulle de la part du serveur. L'application semble lente.

Quelles pistes devez-vous examiner ?

### Corrigé

Examinez la progression de la fenêtre, les éventuelles sondes de fenêtre, la vitesse de consommation des données par l'application, l'état du serveur et les ressources disponibles. Il faut aussi vérifier si le phénomène est temporaire ou persistant.

La fenêtre nulle indique une contrainte de réception annoncée dans le contexte observé, pas automatiquement une congestion réseau.

## Exercice 3 — RTT élevé et faible débit

Un transfert TCP affiche un RTT élevé et un débit faible. Citez au moins cinq facteurs qui peuvent l'expliquer.

### Corrigé

Le débit peut être limité par une fenêtre trop petite par rapport au BDP, une congestion, des pertes, des retransmissions, la capacité du récepteur, les performances de l'émetteur, la stratégie de l'application, des limitations de sécurité ou un chemin particulièrement lent.

Le RTT élevé n'identifie pas à lui seul la cause.

## Exercice 4 — SYN sans SYN-ACK

Une capture côté client montre plusieurs SYN sans SYN-ACK visible. Le serveur fonctionne pour d'autres utilisateurs.

Construisez une investigation qui distingue un problème de chemin, de filtrage et de capture.

### Corrigé

Vérifiez d'abord que les autres utilisateurs utilisent le même chemin et le même contexte de sécurité. Obtenez si possible une capture proche du serveur et examinez les routes, les politiques de sécurité et les journaux du chemin.

Si les SYN arrivent au serveur mais qu'aucune réponse ne quitte son interface, investiguez son état local. Si les SYN ne sont visibles que côté client, recherchez une divergence entre les points de capture et validez que la collecte distante est complète.

## Exercice 5 — UDP avec retransmissions applicatives

Un protocole applicatif au-dessus d'UDP retransmet les requêtes après un délai. Le serveur reçoit parfois deux exemplaires d'une même requête.

Pourquoi ce comportement peut-il être normal ? Quel risque l'application doit-elle prendre en charge ?

### Corrigé

Si la réponse a été perdue ou retardée, le client peut avoir renvoyé une requête que le serveur a déjà reçue. UDP ne garantit pas l'unicité de livraison des messages.

L'application doit prévoir l'identification des requêtes et, si nécessaire, la déduplication ou l'idempotence afin d'éviter l'exécution involontaire de deux opérations.

## Exercice 6 — Checksum invalide côté émetteur

Une capture locale montre des checksums TCP qui semblent incorrects. Une capture faite sur un équipement externe montre des checksums corrects.

Quelle explication faut-il considérer ?

### Corrigé

Un offload de checksum peut faire que la capture locale observe le paquet avant que la carte réseau n'ait calculé le checksum final. Il faut vérifier les paramètres de l'interface, les offloads et les points de capture avant de conclure à une corruption du trafic.

## Exercice 7 — HTTP/3 indisponible

Une application Web fonctionne lorsque HTTP/2 sur TCP est utilisé, mais ne parvient pas à établir HTTP/3 dans un environnement où QUIC est normalement pris en charge.

Quelles vérifications sont pertinentes ?

### Corrigé

Vérifiez si le client tente réellement une connexion QUIC, si UDP est autorisé sur le chemin, si le serveur est configuré pour HTTP/3 et si les réponses associées à la négociation sont visibles. Examinez les règles de pare-feu et les éventuels chemins de repli. La réussite de TCP/443 ne démontre pas l'accessibilité d'UDP/443.

## Exercice 8 — NAT et ports réécrits

Une capture interne montre une connexion source TCP `192.0.2.25:51000` vers `198.51.100.80:443`. Une capture externe montre `203.0.113.10:62001` vers la même destination.

Quelle information supplémentaire aide à démontrer qu'il s'agit du même flux ?

### Corrigé

Il faut corréler les horaires, l'état de traduction NAT, les entrées de connexion, le protocole et les informations du flux observé. Le fait que les adresses et le port source diffèrent peut être cohérent avec un NAT, mais le rapprochement doit être confirmé par les éléments disponibles.

## Exercice 9 — `CLOSE-WAIT` persistant

Une application serveur accumule des sockets en `CLOSE-WAIT`.

Comment investiguer le problème sans supposer immédiatement une fuite de mémoire ?

### Corrigé

Vérifiez la durée et la fréquence des états, le comportement attendu de l'application, les journaux, la gestion des exceptions et la fermeture des sockets. Une rétention prolongée peut révéler que l'application ne termine pas sa fermeture, mais le diagnostic doit s'appuyer sur les comportements réels du processus et sur une reproduction du phénomène.

---

# 17. Modèle de rapport d'incident transport

## 17.1 Informations générales

- Date et heure :
- Service affecté :
- Client et serveur :
- Adresses et ports :
- Protocole :
- Nombre d'utilisateurs affectés :
- Impact :
- Conditions de reproduction :

## 17.2 Architecture et points d'observation

- Adresse et port source :
- Adresse et port destination :
- Route aller connue :
- Route retour connue :
- NAT ou proxy :
- Tunnel :
- Pare-feu :
- Emplacement des captures :
- Limites de collecte :

## 17.3 Observations

Pour chaque test :

- Heure du test :
- Commande ou filtre utilisé :
- Résultat attendu :
- Résultat constaté :
- Paquets ou événements pertinents :
- Journaux associés :
- Hypothèses compatibles avec le résultat :

## 17.4 Causes envisagées

| Hypothèse | Éléments à rechercher | Statut |
|---|---|---|
| Filtrage silencieux | ACL, journaux et divergence entre captures | À confirmer |
| Perte sur le chemin | Captures aux extrémités et autres points disponibles | À confirmer |
| Récepteur incapable de consommer les données | Fenêtre TCP, états applicatifs, métriques du serveur | À confirmer |
| Problème de congestion | Retransmissions, RTT, variation de débit, files d'attente | À confirmer |
| Traduction NAT incohérente | États de traduction et tuples des deux côtés | À confirmer |
| Erreur applicative | Réponse applicative et journaux du service | À confirmer |

## 17.5 Conclusion et validation

- Cause racine retenue :
- Preuves qui la soutiennent :
- Autres hypothèses examinées :
- Correction effectuée :
- Plan de retour arrière :
- Résultat des tests après correction :
- Limites du diagnostic :
- Actions préventives :

Une cause racine doit être soutenue par des preuves suffisantes. Si plusieurs explications restent possibles, le rapport doit les distinguer au lieu d'en sélectionner arbitrairement une.

---

# 18. Glossaire expert

**ACK cumulatif :** acquittement TCP indiquant le prochain octet attendu dans le flux.

**BDP :** produit bande passante-délai, représentant la quantité de données associée à la capacité et au RTT d'un chemin dans un modèle donné.

**Cwnd :** fenêtre de congestion, utilisée par l'émetteur TCP pour limiter les données en vol.

**Déduplication :** mécanisme applicatif qui reconnaît plusieurs exemplaires d'une même opération ou requête.

**Fenêtre de réception :** limite annoncée par le récepteur quant à la capacité de réception dans le flux TCP.

**Middlebox :** équipement intermédiaire susceptible de filtrer, traduire, inspecter, terminer ou transformer des communications.

**NAT :** mécanisme de traduction d'informations d'adressage et, parfois, de ports.

**Offload :** délégation de certains traitements réseau à la carte réseau ou au matériel.

**QUIC :** protocole de transport au-dessus d'UDP intégrant notamment des flux, une gestion des pertes et un mécanisme de sécurité.

**RTO :** temporisateur de retransmission TCP.

**RTT :** délai aller-retour mesuré dans le contexte considéré.

**SACK :** mécanisme qui permet à TCP de communiquer des informations supplémentaires sur les données reçues hors ordre.

**Socket :** interface de communication ou point d'extrémité, selon le contexte.

**Tuple :** combinaison du protocole et des adresses et ports source/destination qui caractérise un flux.

---

# 19. Références techniques officielles

Pour approfondir la norme et les mécanismes, consultez directement :

- [RFC 9293 — Transmission Control Protocol (TCP)](https://www.rfc-editor.org/rfc/rfc9293.html)
- [RFC 768 — User Datagram Protocol (UDP)](https://www.rfc-editor.org/rfc/rfc768.html)
- [RFC 6298 — Calcul du temporisateur de retransmission TCP](https://www.rfc-editor.org/rfc/rfc6298.html)
- [RFC 2018 — TCP Selective Acknowledgment Options](https://www.rfc-editor.org/rfc/rfc2018.html)
- [RFC 9438 — CUBIC for Fast and Long-Distance Networks](https://www.rfc-editor.org/rfc/rfc9438.html)
- [RFC 9000 — QUIC: A UDP-Based Multiplexed and Secure Transport](https://www.rfc-editor.org/rfc/rfc9000.html)
- [RFC 9001 — Using TLS to Secure QUIC](https://www.rfc-editor.org/rfc/rfc9001.html)
- [Registre officiel IANA des services et ports](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml)

---

## Conclusion générale

L'ingénierie TCP/UDP consiste à distinguer les garanties fournies par le transport de celles attendues par l'application.

TCP gère un flux d'octets avec des mécanismes de fiabilité, d'ordre, de contrôle de flux et de congestion. UDP transporte des datagrammes ; si l'application a besoin de fiabilité, d'identification de messages ou de récupération des pertes, ces fonctions doivent être intégrées à son protocole supérieur. QUIC montre qu'un protocole au-dessus d'UDP peut lui-même fournir des mécanismes de transport avancés.

Un bon diagnostic expert repose sur la corrélation des captures, des états, des séquences, des fenêtres, des routes et des journaux. Les observations doivent être reliées au point précis où elles ont été effectuées, et les conclusions doivent rester proportionnées aux preuves.

La maîtrise des ports, des sockets, du NAT et des pare-feu complète cette analyse en permettant de suivre une communication depuis l'application cliente jusqu'au service distant sans confondre ouverture locale, connexion de transport et réussite applicative.