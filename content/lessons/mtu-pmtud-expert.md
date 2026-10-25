# Dépannage MTU et PMTUD — Niveau expert

> **Suite pédagogique :** ce document constitue la troisième étape du parcours, après `mtu-pmtud-debutant.md` puis `mtu-pmtud-intermediaire.md`. Il ne reprend pas les fondamentaux comme un cours indépendant : il utilise les acquis précédents — MTU, PMTU, MSS, messages ICMP/PTB, calcul d’en-têtes, tests de taille, tunnels et capture de base — pour approfondir les cas ambigus, l’architecture et la validation avancée.

**Public visé :** ingénieurs réseau, administrateurs systèmes expérimentés, spécialistes sécurité réseau, SRE, architectes plateforme et techniciens d’escalade N3/N4.

**Objectif de sortie :** produire une explication vérifiable d’une panne de taille de paquet, distinguer la limite du chemin de celle d’un protocole, localiser une perte sans multiplier les changements, puis déployer une correction proportionnée avec critères de succès et retour arrière.

**Prudence opérationnelle :** les commandes de lecture sont distinguées des actions qui changent l’état. Toute modification d’interface, de pare-feu, de VPN ou d’offload doit être autorisée, documentée et assortie d’une restauration. Les valeurs chiffrées sont des exemples, pas des paramètres universels.

## Progression du parcours : du symptôme à l’analyse experte

Au niveau débutant, l’apprenant reconnaît qu’un paquet peut être trop grand pour un lien et découvre le rôle de la découverte de MTU de chemin. Au niveau intermédiaire, il mesure les tailles, lit les messages de contrôle, isole un tunnel et construit une preuve initiale avec une capture. Le niveau expert traite les situations dans lesquelles plusieurs explications sont plausibles : chemins multiples, politiques de sécurité, messages ICMP mal associés, encapsulation imbriquée, offload matériel, caches obsolètes, transports différents et variations de chemin pendant une connexion.

L’expert ne se contente pas de trouver une taille qui « semble fonctionner ». Il explique ce que mesure cette taille, quel point du chemin la contraint, si la valeur est propre à une direction ou à un flux, pourquoi l’algorithme a réagi ainsi et quelles observations confirmeront la durabilité de la correction. Une mitigation qui résout un seul test mais cache la cause, pénalise tout le trafic ou impose une MTU inutilement basse n’est pas encore une bonne résolution.

Le fil conducteur est de séparer quatre objets : la MTU configurée sur une interface, la PMTU estimée d’un chemin, la taille IP réellement émise et la quantité de données utiles remise à la couche de paquetisation. Ces mesures peuvent différer. Toute valeur publiée sans préciser ce qu’elle représente risque d’induire le diagnostic en erreur.

## Table des matières

1. Modèle d’analyse expert et définition du problème
2. Comptabilité exacte des tailles et budgets d’en-têtes
3. Cache PMTU et évolution du chemin
4. Validation des messages PTB et sécurité
5. PMTUD classique : limites et anomalies
6. PLPMTUD et DPLPMTUD
7. TCP, MSS, retransmissions et faux positifs
8. UDP et QUIC
9. Tunnels et encapsulations imbriquées
10. Routage multipath, asymétrie et politiques de chemin
11. Pare-feu, NAT, middleboxes et ICMP indispensable
12. Capture experte : points de mesure et offloads
13. Diagnostic Linux en profondeur
14. Diagnostic Windows et validation croisée
15. Réseaux virtualisés, conteneurs, cloud et overlay
16. Télémétrie, automatisation et observabilité
17. Procédure de changement en production
18. Schéma : séquence de changement contrôlé
19. Études de cas expertes
20. Laboratoire expert reproductible
21. Matrice de diagnostic avancée
22. Modèle de compte rendu d’incident
23. Exercices de niveau expert avec corrigés
24. Checklist de validation avant clôture
25. Glossaire expert
26. Références techniques officielles
27. Ce qui différencie le niveau expert


## 1. Modèle d’analyse expert et définition du problème

### 1.1 Définir le flux avant de parler de MTU

Un incident ne devrait pas être décrit simplement par « le réseau ne passe pas les gros paquets ». Il faut le rattacher à un flux : adresses source et destination, famille IP, transport, ports pertinents, interfaces d’entrée et de sortie, direction, application, heure, taille observée et chemin présumé. Ces informations permettent de comparer les mesures sans mélanger deux flux semblables du point de vue utilisateur mais acheminés différemment.

Dans un environnement avec NAT, proxy, passerelle VPN ou load balancer, décrivez les tuples visibles à plusieurs points. Le tuple côté client peut différer de celui observé après traduction. Une capture intérieure montre le paquet original ; une capture extérieure voit l’enveloppe du tunnel. Des captures apparemment contradictoires peuvent donc décrire des couches différentes du même échange.

Définissez ce qui échoue exactement. « La page ne charge pas » peut désigner un SYN qui n’aboutit pas, un handshake suivi de données bloquées, des retours qui disparaissent, un datagramme UDP rejeté, un transfert qui s’arrête après quelques secondes ou une application qui réduit ses messages. Ces symptômes ne sont pas équivalents. Le moment de l’échec est un indice, pas une preuve isolée.

### 1.2 Séparer hypothèse, observation et conclusion

L’hypothèse est une explication possible : par exemple, « le message Packet Too Big est filtré par le pare-feu de retour ». L’observation est reproductible : « le routeur de sortie enregistre un PTB à 14:03:12, mais aucune capture du poste source ne le montre ». La conclusion doit rester limitée aux faits : « le message est perdu entre ces deux points ». Elle ne doit pas devenir « le pare-feu A est fautif » tant que l’intervalle exact n’est pas isolé.

Chaque hypothèse doit avoir un test discriminant. Pour suspecter un MTU de tunnel trop faible, comparez les tailles avant et après encapsulation, les compteurs de rejet et les résultats d’un test contrôlé. Pour suspecter une perte générale ou une congestion, comparez petits et grands paquets, répétitions temporelles, taux de perte et sens du flux. Un seul paquet perdu ne prouve pas une panne PMTUD.

Évitez de modifier simultanément la MTU, le MSS clamping, une règle ICMP et les paramètres VPN. Une amélioration après quatre changements n’identifie aucune cause. Faites varier une seule condition à la fois ou construisez un plan d’expérience où chaque variable est explicitement isolée.

### 1.3 Modèle à quatre tailles

Maintenez séparément : MTU d’interface, PMTU estimée au niveau IP, taille maximale du datagramme ou segment de transport, et quantité de données applicatives. Une interface peut être réglée à 1500, une route avoir une estimation effective de 1420, un paquet IPv6 consommer 40 octets d’en-tête fixe et des extensions éventuelles, UDP 8 octets, puis l’application ajouter un en-tête et un tag cryptographique. La donnée utile sera alors nettement inférieure à 1420 octets.

La quantité réellement émise peut être encore plus petite parce que l’application limite ses messages, parce que le transport utilise une taille conservatrice ou parce que des options d’en-tête sont présentes. À l’inverse, une capture côté émetteur peut montrer un « super-paquet » construit par offload et qui n’est jamais envoyé sous cette forme sur le fil. Cette distinction doit être écrite dans le rapport, pas laissée à l’interprétation.

### 1.4 Schéma de raisonnement multicouche

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="exp1-title exp1-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp1-title">Analyse multi-couche d’un chemin IP</title><desc id="exp1-desc">Le paquet intérieur est encapsulé, puis traverse l’underlay. Les captures intérieures et extérieures mesurent des objets différents.</desc>
<defs><marker id="exp1-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
<text x="28" y="34" fill="#f8fafc" font-size="22" font-weight="700">Raisonner sur la bonne couche</text>
<g text-anchor="middle" font-size="14"><rect x="30" y="78" width="170" height="86" rx="10" fill="#132c48" stroke="#60a5fa"/><text x="115" y="108" fill="#f8fafc" font-weight="700">Paquet intérieur</text><text x="115" y="133" fill="#bfdbfe">IP : 1380 B</text>
<rect x="260" y="78" width="180" height="86" rx="10" fill="#3b2b15" stroke="#f59e0b"/><text x="350" y="108" fill="#fff7ed" font-weight="700">Encapsulation</text><text x="350" y="133" fill="#fed7aa">IP/UDP/tunnel</text>
<rect x="500" y="78" width="180" height="86" rx="10" fill="#3b1d2a" stroke="#fb7185"/><text x="590" y="108" fill="#fff1f2" font-weight="700">Paquet extérieur</text><text x="590" y="133" fill="#fecdd3">IP : 1450 B</text>
<rect x="740" y="78" width="190" height="86" rx="10" fill="#142d28" stroke="#34d399"/><text x="835" y="108" fill="#ecfdf5" font-weight="700">Underlay</text><text x="835" y="133" fill="#a7f3d0">MTU disponible : 1420 B</text></g>
<g stroke="#60a5fa" stroke-width="2.5" fill="none" marker-end="url(#exp1-arr)"><path d="M200 120 H257"/><path d="M440 120 H497"/><path d="M680 120 H737"/></g>
<circle r="7" fill="#a7f3d0" stroke="#064e3b" stroke-width="2"><animateMotion dur="7s" repeatCount="indefinite" path="M115,120 L350,120 L590,120 L835,120"/></circle>
<rect x="42" y="205" width="420" height="100" rx="10" fill="#111c2d" stroke="#475569"/><text x="62" y="232" fill="#e2e8f0" font-size="16" font-weight="700">Capture intérieure</text><text x="62" y="257" fill="#cbd5e1" font-size="14">Montre le paquet original avant encapsulation.</text><text x="62" y="280" fill="#cbd5e1" font-size="14">Ne prouve pas la taille du paquet sur le WAN.</text>
<rect x="492" y="205" width="426" height="100" rx="10" fill="#111c2d" stroke="#475569"/><text x="512" y="232" fill="#e2e8f0" font-size="16" font-weight="700">Capture extérieure</text><text x="512" y="257" fill="#cbd5e1" font-size="14">Montre l’enveloppe après encapsulation.</text><text x="512" y="280" fill="#cbd5e1" font-size="14">1450 B dépasse ici le budget de 1420 B.</text>
</svg></div>

Le dessin illustre le cas d’un chemin superposé. La PMTU pertinente pour le paquet IP extérieur ne se déduit pas du seul MTU de l’interface intérieure. Les en-têtes ajoutés par le tunnel consomment le budget extérieur ; une capture intérieure ne montre pas directement cette consommation. Documentez les deux couches, le point de mesure et la taille de paquet à chaque transition.

## 2. Comptabilité exacte des tailles et budgets d’en-têtes

### 2.1 Formule indexée par couche

Pour un paquet IP qui ne doit pas être fragmenté, la contrainte générale s’écrit : `taille du paquet IP ≤ MTU du lien ou PMTU applicable`. Pour calculer les données de transport, soustrayez tous les en-têtes qui existent réellement :

`données transport max = plafond IP − en-tête IP effectif − extensions IP − en-tête transport effectif − surcharge protocolaire`.

Les extensions IPv6 appartiennent au paquet IP, mais ne sont pas comprises dans ses 40 octets fixes. Les options TCP font varier l’en-tête TCP au-delà des 20 octets minimums. Un protocole applicatif peut encore ajouter des informations de cadrage, de chiffrement ou d’authentification. L’expert ne substitue pas des tailles minimales théoriques aux en-têtes observés lorsqu’il cherche une limite exacte.

Dans un overlay, le paquet intérieur devient la charge utile d’une couche extérieure, précédée selon le cas d’une trame Ethernet intérieure, d’un en-tête de tunnel, d’UDP et d’IP extérieur. Les conventions des fournisseurs peuvent inclure ou exclure certains champs de couche 2 dans leur terme « overhead ». Reconstruisez le calcul depuis le format exact plutôt que de recopier une valeur sans contexte.

### 2.2 Exemple TCP IPv4 et IPv6 à 1500

Avec une MTU IP de 1500, IPv4 sans options et TCP sans options, le budget maximal théorique des données TCP est 1460 octets. Avec IPv6 et son en-tête fixe de 40 octets puis TCP minimal de 20 octets, il est de 1440 octets. Ce sont des repères arithmétiques pour des en-têtes minimaux, pas une promesse sur chaque paquet.

Si les options TCP occupent 12 octets supplémentaires, le budget des données baisse de 12 octets. Un en-tête IPv4 avec options consomme également plus que 20 octets. En IPv6, toutes les extensions doivent être prises en compte dans la limite du paquet. Les options ne sont pas « gratuites » simplement parce qu’un ping ordinaire n’en contient pas.

Le MSS annoncé lors du handshake TCP ne doit pas être confondu avec la PMTU. Il décrit une limite de données TCP que le receveur annonce pouvoir accepter, selon les règles de transport. L’émetteur doit aussi respecter le plafond de transmission imposé par IP et par son estimation PMTU. La taille effective d’un segment peut donc être inférieure au MSS annoncé. Le MSS clamping modifie l’annonce de transport ; il ne redéfinit pas la MTU de l’interface et ne corrige pas UDP.

### 2.3 MTU IP, taille de trame et jumbo frames

Dans les références IP de l’IETF, la MTU de lien désigne la taille maximale du paquet IP transportable en une pièce. L’en-tête Ethernet, le FCS, les tags VLAN et le préambule ne sont généralement pas inclus dans cette MTU IP. Un constructeur ou une interface de supervision peut pourtant afficher une taille de trame, de charge utile ou de paquet différente. Les nombres ne se comparent qu’après identification de leur convention.

Dans un réseau VLAN, vérifiez si la balise 802.1Q est incluse dans la limite de trame autorisée et si le chemin prend en charge la taille attendue. Des compteurs de giant, oversize, baby giant ou de rejet peuvent varier selon la plateforme ; consultez le sens attribué par le constructeur au lieu d’appliquer une définition universelle à leur nom.

L’existence d’un lien à jumbo frames ne prouve pas que tout le chemin les prend en charge. Un seul segment plus petit reste contraignant. Les endpoints, hyperviseurs, appliances et interfaces virtuelles peuvent également avoir des limites distinctes. Toute augmentation doit être vérifiée de bout en bout, sinon le changement peut créer une panne précisément à la frontière oubliée.

### 2.4 Calcul d’encapsulation imbriquée

Supposons un paquet intérieur limité à 1400 octets, et un tunnel qui ajoute un en-tête IP extérieur de 20 octets, UDP de 8 octets, un en-tête tunnel de 8 octets et une trame Ethernet intérieure de 14 octets dans sa charge utile. La taille du paquet IP extérieur peut alors être supérieure à 1436 octets. Le calcul doit distinguer la MTU IP extérieure de la taille de trame Ethernet extérieure.

Ce n’est pas une recommandation universelle de MTU VXLAN. Le type de tunnel, la famille IP extérieure, les extensions, les tags, la sécurité et le point où l’interface présente son MTU modifient le total. Construisez une table contenant chaque champ du paquet extérieur, sa taille exacte, sa couche et la preuve de sa présence. Cette table devient le point de comparaison avec les captures avant et après encapsulation.

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="exp3-title exp3-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp3-title">Budget de taille avant et après encapsulation</title><desc id="exp3-desc">Une barre représente le paquet intérieur, les champs ajoutés construisent la taille extérieure, qui doit rester sous la MTU extérieure.</desc>
<text x="28" y="35" fill="#f8fafc" font-size="22" font-weight="700">Calculer avec une convention de longueur unique</text>
<text x="54" y="83" fill="#cbd5e1" font-size="15">Paquet intérieur</text><rect x="54" y="98" width="588" height="36" rx="5" fill="#2563eb"/><text x="348" y="122" fill="#eff6ff" font-size="15" text-anchor="middle" font-weight="700">1400 B</text>
<text x="54" y="170" fill="#cbd5e1" font-size="15">Ajout extérieur (exemple : 50 B)</text><rect x="54" y="185" width="588" height="36" rx="5" fill="#2563eb"/><rect x="642" y="185" width="21" height="36" rx="2" fill="#f59e0b"/><text x="680" y="208" fill="#fde68a" font-size="15">+50 B</text>
<text x="54" y="258" fill="#cbd5e1" font-size="15">Paquet extérieur calculé</text><rect x="54" y="273" width="609" height="36" rx="5" fill="#fb7185"/><rect x="54" y="273" width="588" height="36" rx="5" fill="#2563eb"/><text x="348" y="297" fill="#eff6ff" font-size="15" text-anchor="middle" font-weight="700">1450 B au total</text>
<line x1="650" y1="246" x2="650" y2="318" stroke="#fbbf24" stroke-width="3" stroke-dasharray="5 4"/><text x="674" y="270" fill="#fde68a" font-size="14">MTU extérieure</text><text x="674" y="291" fill="#fde68a" font-size="14">1420 B</text><text x="674" y="312" fill="#fca5a5" font-size="14">Dépassement : 30 B</text>
<circle r="6" fill="#f8fafc"><animateMotion dur="5s" repeatCount="indefinite" path="M54,116 L642,116 L663,203 L663,291"/></circle>
</svg></div>

Le schéma présente comment expliquer le budget à une équipe. Pour chaque tranche, deux questions doivent avoir une réponse : le champ existe-t-il dans ce paquet précis, et est-il inclus dans la valeur de MTU comparée ? Si l’une des réponses est incertaine, présentez le total comme une hypothèse, pas comme une mesure.

### 2.5 Unité de mesure des outils

Les tests de ping demandent souvent la taille des données ICMP et non la longueur totale IP. Pour un echo IPv4 ordinaire, la longueur totale ajoute normalement l’en-tête IPv4 et l’en-tête ICMP. En IPv6, distinguez l’en-tête IPv6 fixe, les extensions éventuelles et le message ICMPv6. Les captures et compteurs peuvent rapporter la charge utile, le paquet IP, la trame ou le buffer logiciel avant segmentation.

Dans un rapport, écrivez « paquet IPv4 total de 1472 octets observé dans la capture sur le fil » plutôt que « test à 1472 », et « 1444 octets de données ICMP demandés à l’outil » plutôt que « MTU 1444 ». Une valeur numériquement exacte peut être inutilisable si sa sémantique n’est pas précisée.

## 3. Cache PMTU et évolution du chemin

### 3.1 Une estimation dynamique

La PMTU dépend du chemin IP effectif. Elle n’est pas une propriété permanente d’une adresse de destination. Un changement ECMP, une bascule WAN, une route modifiée, un déplacement du client, la création d’un tunnel ou un changement de famille IP peuvent conduire à des liens différents. Deux connexions vers la même adresse peuvent donc rencontrer des PMTU différentes selon la source, le protocole, le tuple, la politique ou l’état du réseau.

La pile peut mémoriser une estimation apprise précédemment. Si la route devient plus contraignante, la taille du cache peut être trop optimiste jusqu’à ce que le mécanisme de découverte réagisse. L’inverse est également possible : le chemin s’améliore, mais une valeur conservatrice subsiste, ce qui réduit les performances sans provoquer d’échec visible.

Vérifiez si le comportement change après une nouvelle connexion, une expiration d’état ou une bascule de route. Un redémarrage qui « corrige » le problème peut purger un cache ou réinitialiser un transport sans démontrer que le routage était défectueux. Le redémarrage est un indice de dépendance à l’état, pas la cause racine.

### 3.2 Trois formes de désynchronisation

Première forme : l’estimation source dépasse la capacité réelle. Les paquets trop grands sont abandonnés ; si un PTB valide revient, l’émetteur peut réduire la taille. S’il n’arrive pas, le flux peut devenir un black hole. Deuxième forme : l’estimation est inférieure à la capacité réelle. Le trafic fonctionne, mais utilise davantage de paquets et plus d’en-têtes pour le même volume de données. Troisième forme : les estimations diffèrent selon la direction ou le chemin sélectionné par différents flux.

Pour départager ces cas, réunissez MTU configuré, route sélectionnée, informations de transport et paquets observés. Vérifiez la durée de vie de l’estimation si la plateforme permet de l’inspecter. Si elle ne montre pas directement la PMTU, utilisez une capture et une série contrôlée de tailles. L’absence d’une commande de lecture n’implique pas l’absence d’état interne.

### 3.3 Chemin retour du PTB

Le message PTB retourne vers la source du paquet abandonné, mais son itinéraire de retour peut différer de celui du paquet initial. Il traverse donc d’autres interfaces, règles de sécurité, équipements NAT et décisions de routage. C’est pourquoi un routeur peut générer un PTB sans que le poste source le reçoive.

Capturez le message sur plusieurs points ou utilisez les journaux du routeur générateur. Si le PTB est présent en sortie du routeur et absent à l’entrée du pare-feu suivant, le problème est dans ce segment. S’il atteint l’hôte mais que le même flux conserve la même taille, examinez la validation, l’association du message, la pile réseau et la couche de paquetisation. Une capture ne prouve pas à elle seule que la pile a accepté l’information ; il faut observer les paquets qui suivent.

## 4. Validation des messages PTB et sécurité

### 4.1 Ne pas faire confiance aveuglément à PTB

Un message ICMP ou ICMPv6 peut influencer la taille des paquets d’un endpoint. Un attaquant capable d’injecter un message qui semble correspondre à un flux peut tenter de réduire excessivement la PMTU ou dégrader le débit. La présence d’un champ MTU ne rend pas le message authentifié. Les implémentations doivent vérifier que l’erreur correspond plausiblement à un paquet réellement émis et au contexte de chemin pertinent.

La validation peut examiner le paquet cité, les adresses, le protocole, les ports disponibles, l’identifiant de connexion ou d’autres informations d’état. Les détails varient selon famille IP, transport et implémentation. L’expert ne décrète ni que tout PTB est valide, ni que tout ICMP est suspect : il vérifie les exigences du protocole concerné et observe la réponse de l’endpoint.

### 4.2 Plausibilité du MTU annoncé

Une valeur sous le minimum exigé par la famille IP peut être rejetée ou traitée par des règles particulières. Pour IPv6, PMTUD ne doit pas faire descendre la PMTU estimée sous la MTU minimale IPv6 de 1280 octets dans le modèle défini par le protocole. Une liaison sous-jacente plus contrainte doit être gérée par la couche de lien ou d’adaptation pertinente. Cela ne permet pas aux tunnels d’ignorer les budgets plus faibles : il faut comprendre à quelle couche s’applique le message.

Un message PTB peut être incompatible avec le paquet cité, l’interface de sortie ou une autre observation de la route. Ne le rejetez pas uniquement parce qu’il n’annonce pas une valeur courante telle que 1500 ou 1492 ; les accès et tunnels peuvent avoir d’autres tailles. Consignez l’adresse du routeur, l’interface de sortie, la valeur annoncée et le paquet concerné puis confrontez ces données aux autres points d’observation.

### 4.3 Paquet cité, NAT et encapsulation

Les erreurs ICMP incluent une partie du paquet original pour que la source associe l’erreur au trafic. Un NAT, un tunnel, une troncature ou un pare-feu peut affecter les champs disponibles. Le traducteur doit maintenir la cohérence des informations citées avec les tuples connus ; sinon, le message peut être bloqué ou ignoré même si le trafic initial passe.

Comparez le paquet original capturé près de l’émetteur aux champs cités dans le PTB. Vérifiez famille IP, adresses, protocole et ports lorsqu’ils sont présents. Pour un tunnel, établissez si l’erreur concerne le paquet extérieur ou le paquet intérieur et quel composant doit traduire ou propager l’information. Ne supposez pas qu’un PTB reçu par une passerelle sera automatiquement transformé en information utile à l’hôte intérieur.

### 4.4 Logs et politiques

Un équipement devrait distinguer un PTB reçu, associé à un flux et rejeté lors d’une validation. Ces états ne sont pas équivalents. Un journal générique « ICMP denied » ne révèle pas toujours si le message était absent, mal formé, hors état ou simplement couvert par une règle de rejet général. Une journalisation temporaire et ciblée sur le message pertinent est préférable à une désactivation globale du filtrage.

L’objectif n’est pas de faire confiance à tout le contrôle réseau. Il est de permettre les messages nécessaires dans les limites du protocole tout en rejetant les entrées incohérentes. Les règles doivent préserver les erreurs utiles aux communications et bloquer les usages non autorisés. Toute politique doit être testée avec les flux et équipements réels.

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="exp6-title exp6-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp6-title">Cycle de vie du message PTB</title><desc id="exp6-desc">Quatre contrôles séparés : génération par le routeur, livraison sur le chemin de retour, validation par la pile source, application au flux.</desc>
<defs><marker id="exp6-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
<text x="28" y="35" fill="#f8fafc" font-size="22" font-weight="700">Un PTB doit passer quatre barrières distinctes</text>
<g text-anchor="middle" font-size="14"><rect x="30" y="85" width="195" height="95" rx="10" fill="#3b1d2a" stroke="#fb7185"/><text x="127" y="115" fill="#fff1f2" font-weight="700">1. Généré ?</text><text x="127" y="141" fill="#fecdd3">Routeur rejette le gros</text><text x="127" y="160" fill="#fecdd3">paquet et crée PTB</text>
<rect x="270" y="85" width="195" height="95" rx="10" fill="#3b2b15" stroke="#f59e0b"/><text x="367" y="115" fill="#fff7ed" font-weight="700">2. Livré ?</text><text x="367" y="141" fill="#fed7aa">Routage retour et ACL</text><text x="367" y="160" fill="#fed7aa">laissent passer le message</text>
<rect x="510" y="85" width="195" height="95" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="607" y="115" fill="#f8fafc" font-weight="700">3. Validé ?</text><text x="607" y="141" fill="#bfdbfe">Le message correspond</text><text x="607" y="160" fill="#bfdbfe">à un flux/paquet plausible</text>
<rect x="750" y="85" width="180" height="95" rx="10" fill="#12352e" stroke="#34d399"/><text x="840" y="115" fill="#ecfdf5" font-weight="700">4. Appliqué ?</text><text x="840" y="141" fill="#a7f3d0">PMTU ajustée et</text><text x="840" y="160" fill="#a7f3d0">paquet adapté émis</text></g>
<g fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#exp6-arr)"><path d="M225 133 H267"/><path d="M465 133 H507"/><path d="M705 133 H747"/></g>
<circle r="7" fill="#fbbf24" stroke="#78350f" stroke-width="2"><animateMotion dur="8s" repeatCount="indefinite" path="M127,133 L367,133 L607,133 L840,133"/></circle>
<text x="480" y="238" fill="#e2e8f0" text-anchor="middle" font-size="16" font-weight="700">Capturez à plusieurs frontières pour localiser la perte</text><text x="480" y="267" fill="#cbd5e1" text-anchor="middle" font-size="14">PTB observé ≠ PTB accepté ≠ PMTU utilisée par le transport.</text><text x="480" y="294" fill="#94a3b8" text-anchor="middle" font-size="13">Les détails diffèrent entre ICMPv4 et ICMPv6.</text>
</svg></div>

Ce schéma sépare quatre étapes : le PTB est-il généré, transmis, validé et appliqué ? Vérifiez chacune par une capture ou un compteur plutôt que de tirer une conclusion d’un compteur ICMP global.

## 5. PMTUD classique : limites et anomalies

### 5.1 Boucle de fonctionnement

Le PMTUD classique commence généralement par une hypothèse liée au premier lien, puis se corrige lorsqu’un routeur ne peut pas transférer un paquet non fragmentable sur son interface de sortie. En IPv4, le scénario classique utilise DF et ICMP Destination Unreachable type 3/code 4. En IPv6, les routeurs intermédiaires ne fragmentent pas : ICMPv6 Packet Too Big, type 2, indique à la source la MTU du prochain lien. Les détails du mécanisme dépendent de la pile, mais la dépendance aux messages de contrôle explique les pannes quand ces messages sont perdus.

Le dépassement peut être révélé seulement lorsqu’un paquet atteint un segment précis. Les petits paquets et les premiers messages de connexion peuvent donc fonctionner, tandis que les données plus grandes échouent. Le handshake TCP peut réussir parce que ses messages initiaux sont petits, puis le transfert se bloquer. Une application UDP qui n’envoie que de petits messages peut sembler fonctionner jusqu’à ce qu’elle utilise un datagramme proche de sa limite.

### 5.2 Black hole réseau et black hole ICMP

Un *packet black hole* est une taille ou classe de paquets qui n’atteint pas la destination. Un *ICMP black hole* est plus précis : le paquet trop grand échoue et l’émetteur ne reçoit pas l’indication PTB qui permettrait de réagir. Les deux peuvent coexister, mais ils ne sont pas synonymes. Un paquet peut être perdu pour une autre raison, ou le PTB peut être bloqué alors que la cause initiale du symptôme est ailleurs.

Pour reconnaître une panne compatible, comparez plusieurs tailles à plusieurs reprises, dans les deux sens, et capturez au plus près de la source et du rejet présumé. Recherchez une taille au-delà de laquelle les paquets disparaissent de façon reproductible, puis vérifiez le PTB. Cette répétabilité est importante : une perte aléatoire par congestion ne doit pas être classée comme black hole à partir d’un seul paquet perdu.

### 5.3 Ne pas présumer d’une adaptation automatique

Tous les transports, applications et tunnels ne réagissent pas de la même manière. Certaines piles gèrent le PMTUD classique dans IP, d’autres implémentent PLPMTUD/DPLPMTUD à la couche transport, certaines applications UDP imposent une taille conservatrice et d’autres la choisissent elles-mêmes. La réception d’un PTB par l’OS ne prouve donc pas que chaque application l’utilise.

Dans le rapport, nommez la couche qui réagit. Par exemple : « après un PTB validé, la taille effective du socket de test diminue » ou « le PTB apparaît sur le pare-feu mais aucune réduction n’est observée dans les datagrammes applicatifs ». Cette précision évite d’attribuer sans preuve le défaut à IP, TCP, une bibliothèque ou le logiciel VPN.

### 5.4 Absence de PTB : interprétation prudente

Certains tests n’envoient jamais de paquets trop grands ; d’autres utilisent un chemin différent ou une taille déjà réduite. L’absence de PTB pendant ces essais ne prouve donc pas que les messages sont bloqués. Pour tester leur circulation, il faut une condition où un équipement génère un PTB contrôlé, ou observer une occurrence réelle, dans un environnement autorisé.

ICMP peut aussi être limité en fréquence. Une série très rapide de tests peut provoquer des retours intermittents sans que tous les PTB soient bloqués. Espacez les sondes, évitez de charger la production et alignez les horodatages des paquets avec les compteurs du routeur.

## 6. PLPMTUD et DPLPMTUD

### 6.1 Pourquoi sonder au niveau de paquetisation

PLPMTUD et DPLPMTUD réduisent la dépendance à la livraison des PTB. La couche qui choisit la taille des unités de transmission explore le chemin avec des sondes et observe si leur livraison est confirmée par le transport ou l’application. Une sonde réussie donne une preuve que la taille testée passe pour le flux concerné. Des échecs persistants peuvent conduire à réduire la taille effective puis à repartir d’une valeur plus conservatrice.

Cela ne supprime pas la nécessité de comprendre ICMP et ne rend pas acceptable le blocage arbitraire de tous les messages de contrôle. Il s’agit d’une méthode de récupération lorsque les PTB sont perdus ou ne peuvent pas être validés. Le détail dépend du transport : un protocole avec accusés de réception peut reconnaître une sonde différemment d’un transport non acquitté qui a besoin de sa propre logique de confirmation.

La couche qui produit les datagrammes doit connaître les en-têtes ajoutés par les couches inférieures. Si une application et le transport mènent chacun une découverte non coordonnée, ils peuvent envoyer des sondes redondantes ou garder des estimations incompatibles. Placez le mécanisme à un niveau cohérent et tenez compte de la surcharge ajoutée sous cette couche.

### 6.2 États conceptuels

Pour raisonner sur une implémentation, distinguez une base conservatrice, une recherche, un état de maintien et un état d’erreur. En base, l’algorithme s’appuie sur une taille connue pour démarrer. En recherche, il envoie des sondes plus grandes. Après confirmation, l’estimation peut monter ; après un échec, il faut distinguer une limite de taille d’une perte générale avant de réduire la valeur.

En maintien, la taille validée est utilisée pour le trafic ordinaire, mais l’algorithme doit pouvoir retester le chemin. L’état d’erreur couvre les situations incohérentes : PTB contradictoires, taille de base impossible ou signaux qui ne permettent pas de conclure. Cette description est un modèle d’analyse, pas l’automate normatif de toutes les implémentations. Pour interpréter une pile donnée, consultez la spécification et sa documentation.

### 6.3 Sonde et perte

Une sonde PLPMTUD n’est pas un paquet d’application envoyé au hasard avec une charge plus grande. L’algorithme doit pouvoir identifier la sonde, connaître sa taille et obtenir un signal exploitable de succès ou d’échec. Les transports acquittés peuvent utiliser les ACK ; un protocole non acquitté ne peut pas supposer qu’une absence de réponse signifie uniquement une limite de taille. Le réseau peut subir de la congestion, la destination peut être indisponible ou la réponse peut être filtrée.

Les implémentations robustes utilisent répétitions, temporisations et règles de confirmation. Une perte isolée ne doit pas provoquer systématiquement une baisse de PMTU. À l’inverse, une récupération existe lorsque la taille actuelle cesse durablement d’atteindre la destination, même sans PTB. L’équilibre entre vitesse de découverte et risque de perte fait partie du compromis de l’algorithme.

### 6.4 DPLPMTUD pour les datagrammes

DPLPMTUD permet à une application ou à un protocole datagramme de vérifier la taille utilisable, de la réduire après détection d’un black hole et de tenter ultérieurement une valeur supérieure. Le protocole peut générer un datagramme de son choix et ajouter du padding pour atteindre la taille de sonde. La taille de la sonde comprend les en-têtes et le remplissage ajoutés par les couches pertinentes, pas seulement la charge utile vue par l’application.

Évitez des hypothèses concurrentes non coordonnées. Si l’application gère DPLPMTUD, vérifiez que la pile ou un autre composant ne fait pas simultanément une découverte incompatible. Convertissez correctement la PMTU en maximum de données applicatives après avoir soustrait IP, extensions, UDP, le cadrage applicatif et les tags de sécurité.

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-labelledby="exp2-title exp2-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp2-title">Machine à états de découverte DPLPMTUD</title><desc id="exp2-desc">Un transport maintient une taille confirmée, sonde une taille supérieure, confirme par preuve de livraison ou revient à une taille sûre après des échecs.</desc>
<defs><marker id="exp2-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
<text x="28" y="34" fill="#f8fafc" font-size="22" font-weight="700">DPLPMTUD : tester sans confondre perte et limite</text>
<g text-anchor="middle" font-size="14"><rect x="30" y="75" width="190" height="86" rx="12" fill="#12352e" stroke="#34d399"/><text x="125" y="105" fill="#ecfdf5" font-weight="700">Taille confirmée</text><text x="125" y="130" fill="#a7f3d0">base sûre actuelle</text>
<rect x="278" y="75" width="190" height="86" rx="12" fill="#142b46" stroke="#60a5fa"/><text x="373" y="105" fill="#f8fafc" font-weight="700">Sonde candidate</text><text x="373" y="130" fill="#bfdbfe">datagramme plus grand</text>
<rect x="526" y="75" width="190" height="86" rx="12" fill="#24334b" stroke="#93c5fd"/><text x="621" y="105" fill="#f8fafc" font-weight="700">Preuve reçue</text><text x="621" y="130" fill="#bfdbfe">taille confirmée</text>
<rect x="774" y="75" width="156" height="86" rx="12" fill="#3b1d2a" stroke="#fb7185"/><text x="852" y="105" fill="#fff1f2" font-weight="700">Échec</text><text x="852" y="130" fill="#fecdd3">réessayer/revenir</text></g>
<g fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#exp2-arr)"><path d="M220 118 H275"/><path d="M468 118 H523"/><path d="M716 118 H771"/><path d="M850 162 V224 H125 V164"/></g>
<text x="496" y="207" fill="#cbd5e1" font-size="13" text-anchor="middle">Échec : conserver la borne sûre, appliquer temporisation et règles de validation</text>
<rect x="80" y="258" width="800" height="78" rx="10" fill="#111c2d" stroke="#475569"/><text x="100" y="285" fill="#e2e8f0" font-size="15" font-weight="700">Points d’expertise</text><text x="100" y="309" fill="#cbd5e1" font-size="14">La perte d’une sonde est un indice, pas une preuve absolue de MTU ; tenir compte de congestion, du délai et du protocole.</text>
<circle r="7" fill="#fbbf24" stroke="#78350f" stroke-width="2"><animateMotion dur="8s" repeatCount="indefinite" path="M125,118 L373,118 L621,118 L852,118 L852,224 L125,224 L125,118"/></circle>
</svg></div>

Le schéma résume un cycle de découverte : base conservatrice, sondes contrôlées, confirmation, maintien et nouvelle recherche après un délai ou un changement de chemin. L’implémentation réelle doit respecter les temporisations et conditions normatives du protocole ; ce dessin ne les remplace pas.

### 6.5 Signes observables

Une sonde peut apparaître comme un paquet plus grand que les données ordinaires, suivie d’un accusé de réception. Des logs peuvent montrer une variation de taille maximale de datagramme. L’absence d’un événement explicitement nommé PLPMTUD ne prouve pas que le mécanisme n’existe pas : certaines piles l’intègrent au transport sans exposer chaque état à l’administrateur.

Croisez les sondes visibles, les accusés de réception, la variation contrôlée de la taille et le comportement après un changement de route. Si le transport est fermé ou propriétaire, notez ce qui est observable et ce qui ne l’est pas. Une amélioration seule ne prouve pas l’usage d’un algorithme précis, car un repli applicatif peut produire un résultat similaire.

## 7. TCP, MSS, retransmissions et faux positifs

### 7.1 MSS annoncé et segmentation réelle

Chaque sens d’une connexion TCP a son contexte de segmentation. L’option MSS envoyée par un endpoint dans un SYN décrit la limite de données TCP qu’il annonce pouvoir recevoir. Le MSS annoncé par A concerne les données que B lui enverra ; l’annonce de B concerne l’autre direction. Une correction de MSS clamping mal placée peut donc limiter un seul sens ou ne pas toucher l’option de handshake pertinente.

L’émetteur tient aussi compte de la limite IP et de son estimation PMTU. La taille du segment réel dépend du MSS du pair, des options TCP, de la PMTU, des limites d’implémentation et de l’état de congestion. Il est normal d’observer des segments inférieurs au MSS. Les captures peuvent aussi présenter une taille différente des paquets réellement sur le fil à cause du segmentation offload.

### 7.2 MSS clamping : une mitigation, pas une preuve

Le MSS clamping réécrit l’annonce MSS du handshake pour empêcher les endpoints de tenter une taille TCP supérieure au plafond choisi. Cela peut stabiliser un tunnel dont la surcharge n’est pas correctement prise en compte. Il ne modifie pas UDP, QUIC ou les autres transports et ne répare pas la circulation des PTB. Si le clamp résout le symptôme TCP, la conclusion est seulement qu’une segmentation TCP plus petite évite le problème ; cela ne démontre pas quel routeur ou message était la cause.

Calculez le plafond depuis le budget réel du tunnel et vérifiez les deux sens. Consignez la règle et son point d’application. Un plafond trop bas masque le défaut au prix d’une efficacité plus faible, notamment sur des transferts à haut débit. Une règle locale peut aussi ne couvrir que certains flux ou chemins.

### 7.3 Perte de taille ou congestion TCP

Une retransmission TCP ne prouve pas un dépassement MTU. TCP retransmet aussi après congestion, réordonnancement, pertes radio ou réponse tardive. Une signature MTU convaincante est une relation reproductible entre taille et livraison : petits segments réussis, segments au-delà d’un seuil perdus, PTB cohérent ou réussite après réduction. Cette signature doit être vérifiée sur le chemin du flux observé.

La congestion peut sembler dépendre de la taille parce que les gros paquets consomment plus de temps de ligne ou déclenchent une politique. Comparez plusieurs tailles à rythme contrôlé, vérifiez la perte des petits paquets et inspectez les compteurs. Un test excessif peut créer sa propre congestion. Alternez les tailles, limitez le débit et rapportez taux de réussite et nombre d’essais.

### 7.4 Indices TCP qui ne concluent pas

Un handshake achevé suivi d’un blocage est compatible avec un black hole, mais aussi avec un proxy, un filtrage applicatif ou une perte générale. Une connexion qui marche à faible débit puis décroche lorsque la fenêtre croît peut évoquer une taille problématique, mais aussi une congestion. Comparez le même flux avec des tailles contrôlées, capturez les deux côtés et observez les ACK.

Les métriques de socket et de retransmission situent le problème sans remplacer la capture. Notez options TCP, séquences, ACK, retransmissions et tailles sur le fil. Avec les captures hôte, prenez en compte TSO/GSO/GRO et la manière dont le paquet parvient à l’outil.

## 8. UDP et QUIC

### 8.1 UDP ne réduit pas universellement la taille

UDP fournit des datagrammes sans les mécanismes d’accusé de réception de TCP. Il ne garantit ni la livraison ni une réduction automatique du message lorsqu’il est perdu. L’application qui envoie de gros datagrammes doit choisir une taille adaptée, définir comment détecter les échecs et décider comment réduire ou fractionner ses messages. La réception d’une erreur ICMP par l’OS ne garantit pas que l’application utilise l’information.

Distinguez la taille maximale du message applicatif, la longueur IP et le datagramme UDP. Pour calculer la taille applicative maximale, soustrayez IP, les extensions, les 8 octets UDP et la structure protocolaire interne. Le chiffrement peut ajouter nonce, tag ou padding. Une constante codée en dur peut fonctionner dans un réseau et échouer dans un VPN, sur mobile ou après un changement de route.

### 8.2 QUIC : 1200 octets désigne la charge utile UDP

QUIC utilise UDP comme enveloppe, mais sa logique de taille porte sur le paquet IP complet. Un datagramme UDP peut contenir un ou plusieurs paquets QUIC avec leurs en-têtes et contenus protégés. RFC 9000 impose au datagramme UDP contenant des paquets Initial une charge utile UDP d’au moins 1200 octets. Cette valeur exclut l’en-tête UDP et l’en-tête IP ; ce n’est donc pas une MTU IP de 1200 octets.

Pour IPv6 sans extension, 40 octets IP + 8 octets UDP + 1200 octets de charge utile donnent un paquet IP de 1248 octets. Pour IPv4 sans option, 20 + 8 + 1200 = 1228 octets. La MTU minimale IPv6 est 1280 ; sur un chemin qui ne prend en charge que cette taille, il reste en principe 1232 octets de charge utile UDP sans extension. Options, extensions et encapsulations modifient le budget.

Un chemin contraint peut empêcher QUIC d’établir ou de valider correctement une connexion s’il ne transporte pas le minimum requis. Le fait que TCP/HTTPS fonctionne ne prouve pas que QUIC fonctionne : protocoles, tailles, mécanismes de validation et chemins peuvent différer. Enregistrez tailles UDP, adresses locales/distantes et résultats de validation du chemin.

### 8.3 DPLPMTUD et migration QUIC

QUIC peut employer PMTUD classique ou DPLPMTUD pour vérifier si une taille de datagramme supérieure traverse le chemin sans fragmentation IP. Une sonde peut ajouter du padding et exploiter les accusés de réception ou la validation du transport. La taille maximale est maintenue pour chaque paire d’adresses locale et distante, car une migration peut changer la route.

Une connexion logique peut survivre à une migration, mais sa taille optimale n’est pas nécessairement valable sur le nouveau chemin. La connectivité peut être validée avant que la taille soit vérifiée. Examinez donc si le chemin nouvellement sélectionné supporte le minimum requis, puis s’il autorise une taille plus grande.

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 355" role="img" aria-labelledby="exp7-title exp7-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp7-title">QUIC Initial : charge utile UDP et longueur IP</title><desc id="exp7-desc">Une charge utile UDP de 1200 octets donne une longueur IP de 1228 octets pour IPv4 minimal et 1248 octets pour IPv6 sans extensions.</desc>
<text x="28" y="34" fill="#f8fafc" font-size="22" font-weight="700">QUIC : 1200 octets n’est pas la longueur IP totale</text>
<text x="60" y="82" fill="#cbd5e1" font-size="15">Même datagramme UDP : 1200 B de charge utile</text>
<rect x="60" y="105" width="650" height="50" rx="6" fill="#2563eb"/><text x="385" y="136" fill="#eff6ff" text-anchor="middle" font-size="16" font-weight="700">Charge utile UDP : 1200 B (contient QUIC)</text>
<rect x="60" y="105" width="50" height="50" rx="6" fill="#f59e0b"/><text x="85" y="135" fill="#451a03" text-anchor="middle" font-size="11" font-weight="700">UDP</text>
<g font-size="15"><text x="60" y="203" fill="#cbd5e1">IPv4 minimal : 20 B IP + 8 B UDP + 1200 B = 1228 B</text><rect x="60" y="216" width="614" height="30" rx="5" fill="#0f766e"/><text x="680" y="237" fill="#a7f3d0">1228 B</text><text x="60" y="279" fill="#cbd5e1">IPv6 de base : 40 B IPv6 + 8 B UDP + 1200 B = 1248 B</text><rect x="60" y="292" width="624" height="30" rx="5" fill="#7c3aed"/><text x="690" y="313" fill="#ddd6fe">1248 B</text></g>
<circle r="6" fill="#f8fafc"><animateMotion dur="5s" repeatCount="indefinite" path="M110,130 L710,130 L710,231 L684,307"/></circle>
</svg></div>

Le schéma oppose des longueurs souvent confondues dans les discussions QUIC. Il faut préciser si « 1200 » désigne la charge utile UDP ou le paquet IP total. Cette confusion est une cause récurrente de calculs inexacts.

### 8.4 Applications UDP autres que QUIC

Pour un protocole maison, RTP, un jeu en ligne, DNS ou un transfert UDP, déterminez si la taille vient du protocole, d’une bibliothèque ou d’une configuration. La segmentation applicative peut éviter la fragmentation IP, mais ajoute des en-têtes, une gestion de perte, un état de réassemblage et des limites de taille. Si l’application ne peut pas être modifiée, réduire prudemment sa taille ou adapter le tunnel peut être une mitigation, à documenter comme telle.

Ne tentez pas de compenser un problème UDP en changeant uniquement le MSS TCP. Un ping réussi ne prouve pas non plus qu’un datagramme applicatif plus grand traverse le chemin : l’outil peut utiliser un autre flux, une autre taille et une autre politique.

## 9. Tunnels et encapsulations imbriquées

### 9.1 Paquet intérieur et paquet extérieur

Dans un tunnel, le paquet original est encapsulé dans un paquet transporté par le réseau extérieur. Le paquet intérieur peut respecter la MTU de l’interface virtuelle, mais dépasser le budget après ajout des en-têtes externes. Le routeur extérieur traite la couche qu’il reçoit ; il ne connaît pas nécessairement l’intention applicative associée au paquet intérieur.

Une capture de l’interface virtuelle peut montrer un paquet intérieur de 1400 octets, tandis que la capture physique voit un paquet extérieur de 1460 octets, selon l’encapsulation. Les mesures ne se contredisent pas. Mesurez avant et après encapsulation, le MTU extérieur et la taille réellement présente sur le fil. Déterminez aussi quel composant reçoit le PTB et comment il propage cette information à la couche intérieure.

### 9.2 VPN IPsec : le chiffrement modifie le budget

IPsec en mode tunnel ajoute un en-tête IP externe et des informations de sécurité. Selon le mode, le protocole transporté, l’algorithme, les champs explicites, le padding, le tag d’intégrité et NAT-T, la surcharge varie. Un chiffre fixe sans contexte est seulement une approximation. Les tableaux de fournisseurs sont utiles pour formuler une hypothèse, mais ne remplacent pas une mesure du paquet réel.

Pour calculer la valeur effective, déterminez si ESP est transporté directement sous IP ou encapsulé dans UDP, la version IP externe et la taille de chaque champ présent. Comparez la taille extérieure au MTU de l’interface physique. Si l’équipement traite les PTB extérieurs, vérifiez que l’information est propagée à l’hôte qui produit le paquet intérieur. Une passerelle qui reçoit le PTB sans adapter la taille du tunnel ni informer la source peut laisser le problème intact.

### 9.3 WireGuard, GRE et VXLAN

Même les tunnels aux en-têtes simples doivent être calculés selon la famille IP extérieure. WireGuard transporte une enveloppe IP, UDP et son message de données chiffré avec son tag. Le coût externe diffère entre IPv4 et IPv6. Il faut tout de même vérifier la configuration de chaque endpoint et le chemin réel, car les autres encapsulations ou politiques peuvent modifier le budget disponible.

Pour GRE, comptez l’IP extérieure, l’en-tête GRE et les éventuels champs supplémentaires. Pour VXLAN, l’extérieur utilise généralement UDP sous IP et transporte l’en-tête VXLAN plus une trame Ethernet intérieure. Si l’on raisonne à partir de l’IP intérieur, l’Ethernet intérieur peut faire partie de la charge utile extérieure. Des extensions IPv6, tags, tunnels supplémentaires et mécanismes de sécurité modifient encore le total. Ne retenez pas une valeur « overhead VXLAN » sans vérifier la convention de MTU et le format réellement utilisé.

### 9.4 Encapsulation en cascade

Un paquet peut traverser VXLAN, être transporté dans un VPN, puis passer par un accès PPPoE. Dans ce cas, calculez chaque transition depuis le paquet utile intérieur vers l’extérieur, en ajoutant tous les champs. Un seul chiffre global peut aider à estimer, mais ne suffit pas si les couches se terminent sur des équipements différents ou si elles modifient la famille IP et la fragmentation.

Construisez une table pour chaque transition : taille entrante, champs ajoutés, taille sortante, MTU de sortie, décision du routeur et point de capture. La plus petite contrainte applicable gouverne le paquet final. Si une interface extérieure limite à 1420, cette limite doit être reportée vers la couche qui choisit le paquet intérieur, en soustrayant toutes les surcharges situées sous elle. La valeur obtenue ne se compare pas directement à la MTU de l’interface virtuelle si les deux mesures ne décrivent pas la même couche.

### 9.5 Cartographier les surfaces de panne du tunnel

Les pannes possibles comprennent : paquet intérieur trop grand avant encapsulation, paquet extérieur trop grand après encapsulation, PTB perdu sur le réseau extérieur, équipement de tunnel qui n’abaisse pas la taille intérieure, fragmentation extérieure qui ne peut pas être reconstituée, MTU incohérente entre interfaces virtuelles et physiques ou chemin différent dans un sens. Chacune nécessite un test distinct.

Écrivez la localisation comme une transition vérifiable : « paquet intérieur de 1380 octets accepté sur tun0 ; paquet extérieur de 1448 octets généré ; WAN limité à 1420 ; PTB visible à l’entrée de la passerelle mais non propagé à l’interface intérieure ». Cette description réduit le nombre d’hypothèses restantes et indique où placer la prochaine capture.

<div style="max-width:100%;overflow-x:auto;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="exp9-title exp9-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif"><title id="exp9-title">Encapsulation imbriquée</title><desc id="exp9-desc">Un paquet intérieur traverse deux couches de tunnel qui ajoutent chacune leur surcharge au paquet externe.</desc><defs><marker id="exp9-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs><text x="28" y="34" fill="#f8fafc" font-size="22" font-weight="700">Deux tunnels : compter chaque couche une seule fois</text><g text-anchor="middle" font-size="14"><rect x="35" y="80" width="180" height="90" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="125" y="110" fill="#f8fafc" font-weight="700">Paquet intérieur</text><text x="125" y="137" fill="#bfdbfe">1380 B</text><rect x="270" y="80" width="180" height="90" rx="10" fill="#3b2b15" stroke="#f59e0b"/><text x="360" y="110" fill="#fff7ed" font-weight="700">Tunnel A</text><text x="360" y="137" fill="#fed7aa">+ 40 B</text><rect x="505" y="80" width="180" height="90" rx="10" fill="#3b2b15" stroke="#f59e0b"/><text x="595" y="110" fill="#fff7ed" font-weight="700">Tunnel B</text><text x="595" y="137" fill="#fed7aa">+ 60 B</text><rect x="740" y="80" width="185" height="90" rx="10" fill="#3b1d2a" stroke="#fb7185"/><text x="832" y="110" fill="#fff1f2" font-weight="700">Paquet extérieur</text><text x="832" y="137" fill="#fecdd3">1480 B</text></g><g fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#exp9-arr)"><path d="M215 125 H267"/><path d="M450 125 H502"/><path d="M685 125 H737"/></g><circle r="7" fill="#a7f3d0" stroke="#064e3b" stroke-width="2"><animateMotion dur="7s" repeatCount="indefinite" path="M125,125 L360,125 L595,125 L832,125"/></circle><rect x="65" y="222" width="830" height="72" rx="10" fill="#111c2d" stroke="#475569"/><text x="88" y="250" fill="#e2e8f0" font-size="16" font-weight="700">Exemple de calcul</text><text x="88" y="276" fill="#cbd5e1" font-size="14">1380 + 40 + 60 = 1480 B ; comparer au MTU extérieur réel et vérifier l’overhead de chaque tunnel.</text></svg></div>

## 10. Routage multipath, asymétrie et politiques de chemin

### 10.1 ECMP et chemins de capacité différente

Avec ECMP ou un répartiteur par flux, plusieurs chemins peuvent exister entre les mêmes endpoints. Le choix peut dépendre du tuple IP, des ports, du protocole, des marques de politique ou du hash défini par l’équipement. Deux transferts vers la même destination peuvent donc traverser des sorties différentes et rencontrer des MTU différentes. Un ping et une connexion TCP ne sont pas garantis sur le même chemin si le hash s’appuie sur des champs différents.

Le chemin peut aussi changer pendant une connexion après une panne ou une convergence de routage. Si la nouvelle route est plus contraignante, la valeur PMTU déjà utilisée peut être trop grande. Si le nouveau chemin autorise davantage, une taille conservatrice peut encore limiter le débit. Une panne intermittente peut ainsi être due au chemin sélectionné, plutôt qu’à une MTU changeant de façon aléatoire sur une interface unique.

### 10.2 Asymétrie directionnelle

Le chemin A→B n’est pas forcément identique à B→A. Le retour peut utiliser un autre opérateur, un pare-feu distinct, un VPN différent ou un lien de secours. Les données peuvent passer dans un sens alors que le PTB ou les ACK empruntent un trajet distinct. Un filtrage stateful ou asymétrique peut donc bloquer le message de contrôle sans affecter de la même manière le flux initial.

Mesurez séparément les deux sens et consignez routes, interfaces, PMTU et points de capture. Comparez les compteurs et journaux des deux extrémités. Un simple « ping fonctionne » n’est pas suffisant : l’écho et sa réponse peuvent traverser des règles différentes de celles de l’application affectée.

### 10.3 Reproduire fidèlement un flux ECMP

Conservez le tuple réel : adresses, ports source/destination et protocole. Un ping vers la même IP peut être hashé autrement que la connexion défaillante. Si le port source change, le flux peut basculer vers un autre chemin ; on peut croire qu’une correction MTU fonctionne alors que seul le chemin a changé. Capturez les décisions de routage et d’équilibrage pour le flux concerné, lorsque la plateforme permet de les observer.

Traceroute aide à se repérer, mais ses sondes peuvent être hashées différemment, les réponses des routeurs filtrées et les adresses visibles incomplètes. Utilisez-le comme indice, pas comme preuve de la route complète. La preuve d’une perte liée à la taille doit s’appuyer sur des captures ou des compteurs situés près du point de rupture.

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" role="img" aria-labelledby="exp4-title exp4-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp4-title">ECMP, routes alternatives et MTU différentes</title><desc id="exp4-desc">Un répartiteur sélectionne deux chemins. Un chemin offre une MTU plus petite ou un retour PTB absent, créant un résultat intermittent.</desc>
<defs><marker id="exp4-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs><text x="28" y="34" fill="#f8fafc" font-size="22" font-weight="700">Même destination, chemins différents</text>
<rect x="35" y="135" width="150" height="78" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="110" y="167" fill="#f8fafc" font-size="15" text-anchor="middle" font-weight="700">Source</text><text x="110" y="190" fill="#bfdbfe" font-size="13" text-anchor="middle">flux de test</text>
<rect x="260" y="135" width="160" height="78" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="340" y="167" fill="#f8fafc" font-size="15" text-anchor="middle" font-weight="700">ECMP / hash</text><text x="340" y="190" fill="#bfdbfe" font-size="13" text-anchor="middle">choix du chemin</text>
<rect x="535" y="70" width="180" height="72" rx="10" fill="#12352e" stroke="#34d399"/><text x="625" y="98" fill="#ecfdf5" font-size="15" text-anchor="middle" font-weight="700">Chemin A</text><text x="625" y="122" fill="#a7f3d0" font-size="13" text-anchor="middle">MTU 1500</text>
<rect x="535" y="245" width="180" height="72" rx="10" fill="#3b1d2a" stroke="#fb7185"/><text x="625" y="273" fill="#fff1f2" font-size="15" text-anchor="middle" font-weight="700">Chemin B</text><text x="625" y="297" fill="#fecdd3" font-size="13" text-anchor="middle">MTU 1400 / PTB perdu</text>
<rect x="790" y="135" width="135" height="78" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="857" y="167" fill="#f8fafc" font-size="15" text-anchor="middle" font-weight="700">Destination</text><text x="857" y="190" fill="#bfdbfe" font-size="13" text-anchor="middle">même IP</text>
<g fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#exp4-arr)"><path d="M185 174 H257"/><path d="M420 155 L532 106"/><path d="M420 195 L532 279"/><path d="M715 106 L787 155"/><path d="M715 281 L787 194"/></g>
<path d="M625 146 L625 218 L340 218" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#exp4-arr)"/><text x="482" y="238" fill="#fde68a" font-size="12" text-anchor="middle">retour PTB ?</text>
<circle r="7" fill="#a7f3d0" stroke="#064e3b" stroke-width="2"><animateMotion dur="6s" repeatCount="indefinite" path="M110,174 L340,174 L625,106 L857,174"/></circle><circle r="6" fill="#fb7185"><animateMotion dur="7s" repeatCount="indefinite" path="M110,174 L340,174 L625,281 L625,218 L340,218"/></circle>
<text x="480" y="358" fill="#cbd5e1" font-size="14" text-anchor="middle">Fixer le tuple, comparer plusieurs points et prouver quel chemin porte le flux défaillant.</text></svg></div>

## 11. Pare-feu, NAT, middleboxes et ICMP indispensable

### 11.1 Permettre les erreurs nécessaires sans ouvrir tout ICMP

Le conseil « autoriser ICMP » est trop imprécis pour une politique de production. Les messages ICMP n’ont pas tous le même rôle. Pour PMTUD, les messages qui signalent qu’un paquet ne peut pas être transmis en raison de la MTU ont une fonction précise. La politique doit permettre les messages nécessaires conformément à la famille IP et au contexte stateful, tout en limitant les entrées non pertinentes ou non plausibles.

En IPv4, le message habituel est Destination Unreachable type 3, code 4. En IPv6, Packet Too Big est de type 2. Une politique qui bloque indistinctement ICMPv6 peut casser des fonctions IPv6 fondamentales au-delà de PMTUD. Il ne faut pourtant pas non plus faire une autorisation globale sans tenir compte du rôle, de la portée et de la validation de ces messages.

### 11.2 NAT et états du pare-feu

Un pare-feu stateful peut n’accepter une erreur ICMP que si elle correspond à une connexion connue. Le paquet cité doit être correctement interprété. Si le traducteur ne met pas à jour les champs cités ou si le pare-feu retour ne reconnaît pas le flux, le PTB peut être bloqué. Cela peut produire une situation où l’aller et le retour applicatif passent, mais le message de contrôle ne correspond pas à l’état vu par l’équipement.

Pour diagnostiquer, collectez les traces NAT internes/externes, la règle ICMP appliquée, le tuple du paquet cité et le motif détaillé de rejet. Un compteur global « ICMP dropped » ne localise pas la cause. Des captures aux interfaces intérieure et extérieure révèlent si le message a été reçu, traduit et retransmis. Toute modification doit d’abord être testée sur un flux pilote et avec portée limitée.

### 11.3 Middleboxes, proxy et inspection applicative

Les équipements de sécurité, accélération WAN, proxy, répartiteur de charge et inspection peuvent segmenter, réassembler, réécrire ou encapsuler les paquets. Certains terminent une connexion TCP et en créent une deuxième ; les connexions de chaque côté ont alors des MSS, PMTU et états de socket distincts. Une capture avant le proxy ne reflète pas nécessairement la taille des paquets générés après lui.

Si le trafic traverse un proxy TCP, séparez les deux connexions et mesurez les paramètres des deux côtés. Si l’équipement applique MSS clamping, déterminez quelle annonce MSS reçoit chaque endpoint. Si un accélérateur encapsule le flux, calculez son budget. Une correction sur l’interface client peut n’avoir aucun effet sur la connexion créée par le proxy vers le serveur.

### 11.4 Limitation ICMP et intermittence

Les routeurs peuvent limiter la fréquence des réponses ICMP pour réduire les abus ou la charge de contrôle. Un test qui envoie des dizaines de paquets trop grands par seconde peut produire un comportement différent de celui d’un flux applicatif. Si des PTB n’apparaissent que pour une partie des sondes, examinez rate limiting, files de traitement et règles appliquées par interface.

Ne désactivez pas une limite de sécurité sans en comprendre le rôle. Réduisez d’abord le débit d’essai, espacez les sondes et observez les compteurs. La fréquence des essais, la charge de l’équipement et la méthode de capture doivent figurer dans le protocole expérimental, car elles affectent le résultat.

## 12. Capture experte : points de mesure et offloads

### 12.1 Choisir des captures qui répondent à une question

Une capture est utile si son point est connu et si la question est précise. Une capture source montre ce que la pile expose à la carte, pas nécessairement ce qui sera transmis sur le fil après offload. Une capture sur port miroir proche du routeur peut montrer la trame réellement émise. À l’intérieur d’un tunnel, on voit le paquet intérieur ; à l’extérieur, l’enveloppe. Une capture côté serveur vérifie si le paquet est arrivé et comment il a été reçu.

Pour localiser une perte, deux points qui encadrent la transition suspecte sont souvent plus utiles qu’une grande capture isolée. Capturez simultanément entrée et sortie d’un routeur si possible, puis alignez les horodatages. Si le paquet est visible en entrée mais absent en sortie, examinez routage, MTU de sortie, rejet, fragmentation et politique de sécurité. S’il sort bien mais que la réponse n’arrive pas, poursuivez sur le chemin aval et retour.

### 12.2 TSO, GSO, GRO, LRO et checksum offload

Les mécanismes d’offload déplacent du traitement vers la carte réseau. TSO/GSO permettent de préparer des blocs volumineux avant segmentation ; GRO/LRO peuvent agréger les paquets reçus. Une capture hôte peut donc montrer une unité logicielle plus grande que la MTU, alors que la carte la découpe avant transmission. Une somme de contrôle qui paraît invalide sur la capture sortante peut aussi être calculée plus tard par le matériel.

Ne concluez pas à une violation MTU à partir d’un paquet géant visible uniquement sur une capture hôte. Examinez le point de capture et les offloads, puis comparez à une capture externe sur le fil. Dans un laboratoire, désactiver temporairement un offload peut aider, mais change le comportement mesuré et peut coûter des performances. Évitez ce changement en production sans autorisation, notez l’état avant/après et restaurez-le.

### 12.3 Corrélation par tuple, séquence et heure

L’association entre un paquet et son PTB est plus solide lorsque le paquet cité correspond à l’émission observée et que les horodatages sont cohérents. Pour TCP, les numéros de séquence et les ACK aident à repérer retransmissions et progression du flux. Pour UDP, un protocole applicatif peut fournir un identifiant ; sinon, utilisez tuple, taille et horodatage. Pour QUIC, le chiffrement limite l’inspection du contenu, mais les tailles UDP et les journaux de transport restent utiles.

Une capture peut être tronquée. La longueur capturée n’est alors pas la longueur sur le fil. Vérifiez les champs et l’absence de filtre qui exclurait le PTB. Évitez de filtrer uniquement le port applicatif si cela enlève les messages de contrôle dont dépend l’enquête.

### 12.4 Filtres Wireshark utiles

Ces filtres d’affichage accélèrent les recherches, mais doivent être adaptés à la version de Wireshark. Ils ne retrouvent pas les paquets qui n’ont jamais été capturés.

- `icmp.type == 3 && icmp.code == 4` : ICMPv4 classique de fragmentation nécessaire.
- `icmpv6.type == 2` : ICMPv6 Packet Too Big.
- `tcp.analysis.retransmission` : retransmissions détectées par l’analyseur, sans prouver une cause MTU.
- `udp` : flux UDP, à réduire par adresses et ports lorsque cela convient.
- `ip.len > 1400` ou `ipv6.plen > 1400` : paquets au-delà d’un seuil. Confirmez le sens du champ de longueur utilisé.

Les filtres de capture libpcap ne sont pas identiques aux filtres d’affichage Wireshark. En cas de doute, faites une courte capture peu restrictive sur les interfaces pertinentes, puis filtrez hors ligne. Une capture complète peut contenir des données sensibles ; limitez sa portée, protégez le fichier et suivez les règles de confidentialité.

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" role="img" aria-labelledby="exp5-title exp5-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp5-title">Offloads et différence entre capture hôte et fil</title><desc id="exp5-desc">Un gros buffer logique est segmenté par TSO sur le chemin d’émission, tandis que GRO peut agréger côté réception.</desc>
<defs><marker id="exp5-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
<text x="28" y="34" fill="#f8fafc" font-size="22" font-weight="700">Le point de capture change la représentation</text>
<g><rect x="35" y="75" width="245" height="185" rx="12" fill="#13233a" stroke="#60a5fa"/><text x="157" y="104" fill="#f8fafc" text-anchor="middle" font-size="16" font-weight="700">Hôte émetteur</text><rect x="60" y="124" width="195" height="35" rx="6" fill="#2563eb"/><text x="157" y="147" fill="#eff6ff" text-anchor="middle" font-size="13">Capture pré-TSO</text><text x="157" y="184" fill="#bfdbfe" text-anchor="middle" font-size="14">Gros buffer logiciel</text><text x="157" y="207" fill="#bfdbfe" text-anchor="middle" font-size="14">pas forcément 1 paquet sur le fil</text><text x="157" y="237" fill="#93c5fd" text-anchor="middle" font-size="13">GSO / TSO</text>
<rect x="365" y="75" width="230" height="185" rx="12" fill="#142d28" stroke="#34d399"/><text x="480" y="104" fill="#ecfdf5" text-anchor="middle" font-size="16" font-weight="700">Sur le fil</text><g fill="#047857" stroke="#6ee7b7"><rect x="395" y="130" width="48" height="38" rx="4"/><rect x="450" y="130" width="48" height="38" rx="4"/><rect x="505" y="130" width="48" height="38" rx="4"/></g><g fill="#d1fae5" font-size="11" text-anchor="middle"><text x="419" y="153">P1</text><text x="474" y="153">P2</text><text x="529" y="153">P3</text></g><text x="480" y="194" fill="#a7f3d0" text-anchor="middle" font-size="14">Segments Ethernet/IP distincts</text><text x="480" y="218" fill="#a7f3d0" text-anchor="middle" font-size="13">MTU observée physiquement</text>
<rect x="680" y="75" width="245" height="185" rx="12" fill="#29213a" stroke="#c4b5fd"/><text x="802" y="104" fill="#f5f3ff" text-anchor="middle" font-size="16" font-weight="700">Hôte récepteur</text><g fill="#6d28d9" stroke="#c4b5fd"><rect x="705" y="130" width="48" height="38" rx="4"/><rect x="760" y="130" width="48" height="38" rx="4"/><rect x="815" y="130" width="48" height="38" rx="4"/></g><text x="802" y="194" fill="#ddd6fe" text-anchor="middle" font-size="14">GRO / RSC peut agréger</text><text x="802" y="218" fill="#ddd6fe" text-anchor="middle" font-size="13">segments à l’entrée</text></g>
<g fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#exp5-arr)"><path d="M280 168 H362"/><path d="M595 168 H677"/></g><circle r="6" fill="#fbbf24"><animateMotion dur="5s" repeatCount="indefinite" path="M150,145 L235,145 L405,149 L480,149 L550,149 L790,150"/></circle>
<text x="480" y="306" fill="#e2e8f0" text-anchor="middle" font-size="15" font-weight="700">Pour prouver la taille sur le fil, capturer au bon point.</text><text x="480" y="331" fill="#cbd5e1" text-anchor="middle" font-size="13">Une capture hôte ne doit pas être interprétée sans connaître les offloads actifs.</text>
</svg></div>

### 12.5 Table de corrélation

Pour chaque paquet suspect, consignez heure, interface, sens, adresses, protocole, ports, longueur IP, longueur capturée, charge utile, bit DF IPv4 lorsqu’il s’applique, en-têtes supplémentaires, résultat et identifiant de capture. Pour un PTB, ajoutez type/code, MTU annoncée, routeur source, paquet cité et résultat de validation connu.

Cette table vaut mieux qu’un commentaire « gros paquet perdu ». Elle permet de comparer les mêmes paquets à différents points et de détecter les erreurs de méthode : longueur de trame comparée à longueur IP, ou capture hôte agrégée comparée au fil. Le rapport doit préciser la convention de mesure de chaque outil.

## 13. Diagnostic Linux en profondeur

### 13.1 Observation avant changement

Sur Linux, associez informations d’interface, de route, de socket et de capture. `ip -d link show` expose les propriétés des interfaces ; `ip route get ADRESSE` aide à identifier la route IPv4 ; `ip -6 route get ADRESSE` fait la même chose pour IPv6. Enregistrez les sorties avec date et famille du flux. Si le routage utilise des marques, règles ou tables multiples, reproduisez ces paramètres autant que possible.

`ip link show dev INTERFACE` montre la MTU configurée sur une interface. `ip route show table all` et `ip rule show` peuvent révéler plusieurs tables et politiques. Ne supposez pas que la route principale est utilisée si une marque de socket, un namespace ou un VRF intervient.

```bash
ip -d link show
ip route get 203.0.113.20
ip -6 route get 2001:db8:20::20
ip rule show
ip route show table all
ip -s link show dev eth0
```

Les adresses de documentation sont des exemples. Remplacez-les par les adresses adaptées dans un environnement autorisé. Ces lectures ne changent pas la configuration ; vérifiez néanmoins la documentation locale lorsqu’une option de diagnostic avancée est utilisée.

### 13.2 Ping et longueur IP

`ping -4 -M do -s 1472 DESTINATION` est un repère classique pour un chemin supposé MTU 1500 : 1472 octets de données ICMP + 8 octets ICMP + 20 octets d’en-tête IPv4 minimal = 1500. L’exemple suppose l’absence d’options IPv4 et ne garantit pas que le test utilise le même tuple ou la même route que l’application. Vérifiez la syntaxe de votre version.

En IPv6, l’en-tête fixe fait 40 octets et ICMPv6 Echo ajoute habituellement 8 octets. Pour viser un paquet de 1280 sans extension, la charge utile Echo est donc 1232 octets. Cela ne reproduit pas automatiquement un VPN, QUIC ou un flux ECMP. Variez la taille, notez le taux de réussite et conservez les résultats.

```bash
ping -4 -M do -s 1472 203.0.113.20
ping -4 -M do -s 1400 203.0.113.20
ping -6 -s 1232 2001:db8:20::20
tracepath 203.0.113.20
tracepath6 2001:db8:20::20
```

Une erreur locale d’émission ne signifie pas la même chose qu’un paquet parti puis rejeté par un routeur. Le silence ne prouve pas non plus un PTB perdu : le destinataire peut filtrer Echo, ou un autre élément peut perdre la demande ou la réponse.

### 13.3 Lire l’état TCP et les métriques

`ss -ti` peut exposer retransmissions, congestion et certaines métriques selon le noyau. `ip tcp_metrics show`, si disponible, donne accès à des métriques TCP conservées. Ces sorties décrivent l’état d’une connexion ou un cache ; elles ne constituent pas une PMTU universelle et immuable du système.

Si le résultat dépend du processus, vérifiez namespace, règles de routage, marques et politiques qui modifient l’acheminement. Dans un conteneur, le réseau de l’hôte et celui du namespace ne sont pas identiques. Lancez les observations dans le contexte réseau concerné ou documentez la transition entre eux.

### 13.4 Capture et compteurs noyau

`tcpdump` capture sur une interface donnée, mais offloads et point de capture influencent le résultat. Une commande de base peut être adaptée comme suit :

```bash
tcpdump -ni eth0 -s 0 -w incident.pcap 'icmp or icmp6 or host 203.0.113.20'
```

Adaptez l’expression pour inclure le flux et le retour ICMP sans capturer inutilement tout le trafic sensible. Un filtre trop étroit peut exclure les PTB ou une interface tunnel. Vérifiez l’interface avant de lancer la capture et notez le filtre exact.

`ethtool -k eth0` indique les fonctions d’offload prises en charge si le pilote les expose. `ethtool -K` change l’état ; cela peut toucher la performance et doit être réservé au laboratoire ou à une fenêtre approuvée. Une capture TAP/SPAN est souvent préférable pour confirmer la taille sur le fil, mais le miroir peut lui-même perdre des paquets.

### 13.5 Modifier le MTU Linux

`ip link set dev eth0 mtu 1400` change réellement la configuration active. Avant l’action, notez la valeur initiale, le namespace, le rôle de l’interface et la commande de restauration. Une baisse de MTU peut masquer le défaut en forçant tous les paquets à être plus petits, mais pénaliser les flux qui pourraient utiliser une taille plus élevée. Évitez de modifier toutes les interfaces si le problème ne concerne qu’un tunnel.

Le retour arrière doit contenir la valeur d’origine exacte et être vérifié. Certaines connexions, routes et caches peuvent conserver l’état antérieur. Si la panne disparaît, confirmez le mécanisme par comparaison des tailles et compteurs, au lieu de déclarer automatiquement que la valeur réduite est une solution permanente.

## 14. Diagnostic Windows et validation croisée

### 14.1 Examiner interface et route

Sur Windows, `Get-NetIPInterface` affiche les propriétés des interfaces IP, dont la MTU selon les colonnes disponibles. `Get-NetRoute` et `Get-NetIPConfiguration` aident à comprendre la route et les paramètres locaux. Filtrez sur la bonne famille et la bonne interface : Ethernet, Wi-Fi, VPN, Hyper-V, WSL et interfaces virtuelles peuvent coexister. La MTU d’une interface ne prouve pas que l’application l’utilise.

Un test IPv4 `ping -f -l 1472 ADRESSE` demande 1472 octets de données ICMP ; avec les en-têtes IPv4 et ICMP ordinaires, le total atteint 1500 octets. Une réponse « packet needs to be fragmented » diffère d’un délai d’attente. Conservez le message exact, la taille demandée et l’heure de chaque essai.

```powershell
Get-NetIPInterface | Format-Table ifIndex,InterfaceAlias,AddressFamily,NlMtu,ConnectionState
Get-NetIPConfiguration
Get-NetRoute -AddressFamily IPv4 | Sort-Object RouteMetric
Get-NetRoute -AddressFamily IPv6 | Sort-Object RouteMetric
ping -4 -f -l 1472 203.0.113.20
ping -4 -f -l 1400 203.0.113.20
tracert -d 203.0.113.20
```

Les champs et options peuvent différer selon la version de Windows. `-l` spécifie les données, pas la longueur IP totale. Tracert peut aider à localiser le chemin, mais ne prouve pas que TCP ou UDP emprunte exactement la même route.

### 14.2 Capturer nativement

Sur des versions récentes, `pktmon` peut capturer des événements à travers des composants réseau ; la disponibilité et les commandes dépendent de la version. Wireshark est également utile si son pilote est installé et autorisé. Choisissez l’interface ou le composant à observer : sans cela, la trace peut correspondre à la mauvaise étape.

Dans Hyper-V et les VPN, tenez compte des interfaces virtuelles et des frontières d’encapsulation. Un paquet observé avant encapsulation ne ressemble pas à la trame extérieure. Si le segmentation offload est actif, la capture hôte peut montrer un bloc logiciel plus grand que le paquet sur le fil. Si possible, comparez à une capture externe sur un port miroir ou un TAP correctement dimensionné.

### 14.3 Évaluer et restaurer

Une modification de MTU ou de paramètre de carte doit être limitée à l’interface concernée, consignée et testée avec l’application réelle. Notez le nom, l’index, la famille et la valeur d’origine. Vérifiez les nouvelles tailles, l’état des connexions et les flux qui n’étaient pas au cœur du test. Une amélioration sur une seule connexion n’autorise pas une modification permanente de tout le poste.

Le retour arrière doit être testé. Après restauration, confirmez que la valeur est active sur la bonne interface, que routes et tunnels sont dans l’état prévu et que le test reproduit le comportement de référence. Si l’incident est intermittent, faites assez de répétitions pour éviter de déclarer une victoire prématurée.

## 15. Réseaux virtualisés, conteneurs, cloud et overlay

### 15.1 Pourquoi le réseau logique ne suffit pas

Dans un environnement virtualisé, un paquet peut traverser plusieurs couches avant de rejoindre le réseau physique : namespace du conteneur, veth, bridge, route de l’hôte, overlay VXLAN ou Geneve, interface physique, réseau du fournisseur, puis éventuellement un deuxième overlay. Chaque couche peut appliquer une politique différente. L’MTU affichée dans le conteneur n’est donc pas une description complète de toutes les contraintes du chemin.

Distinguez trois plans d’observation. Le **plan applicatif** montre les datagrammes ou segments que le programme tente d’émettre. Le **plan réseau virtuel** montre le paquet à l’entrée et à la sortie d’une interface veth, bridge, tunnel ou interface de service mesh. Le **plan physique** montre ce qui est effectivement placé sur le lien après segmentation et encapsulation. Une divergence entre ces vues est souvent attendue ; elle devient un indice lorsqu’elle ne correspond plus au comportement supposé.

L’overlay consomme une partie de la taille autorisée sur le réseau sous-jacent. Si un paquet intérieur possède une taille de 1500 octets et que VXLAN/Geneve, UDP et un nouvel en-tête IP sont ajoutés, le paquet extérieur peut dépasser la MTU physique. La quantité exacte dépend des options, de la famille IP extérieure, des extensions, des tags et de l’implémentation. N’utilisez pas une valeur universelle copiée d’un autre cluster : mesurez et calculez le budget de votre encapsulation réelle.

<div style="max-width: 100%; overflow-x: auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" role="img" aria-labelledby="svg-cloud-title svg-cloud-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="svg-cloud-title">Chemin du paquet dans un réseau cloud</title><desc id="svg-cloud-desc">Un paquet traverse conteneur, veth, overlay et interface physique ; l’encapsulation ajoute des octets et peut dépasser la MTU.</desc>
<defs><marker id="cloud-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
<text x="32" y="34" fill="#f8fafc" font-size="22" font-weight="700">MTU : de l’espace intérieur au fil physique</text>
<g font-size="14" text-anchor="middle"><rect x="30" y="75" width="155" height="92" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="107" y="105" fill="#f8fafc" font-weight="700">Conteneur</text><text x="107" y="129" fill="#bfdbfe">paquet interne</text><text x="107" y="149" fill="#bfdbfe">ex. 1450 B</text>
<rect x="220" y="75" width="155" height="92" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="297" y="105" fill="#f8fafc" font-weight="700">veth / bridge</text><text x="297" y="129" fill="#bfdbfe">même IP interne</text><text x="297" y="149" fill="#bfdbfe">routage hôte</text>
<rect x="410" y="75" width="155" height="92" rx="10" fill="#3b2b15" stroke="#f59e0b"/><text x="487" y="105" fill="#fff7ed" font-weight="700">Overlay</text><text x="487" y="129" fill="#fed7aa">IP/UDP + VXLAN</text><text x="487" y="149" fill="#fed7aa">octets ajoutés</text>
<rect x="600" y="75" width="155" height="92" rx="10" fill="#3b1d2a" stroke="#fb7185"/><text x="677" y="105" fill="#fff1f2" font-weight="700">Interface physique</text><text x="677" y="129" fill="#fecdd3">MTU du lien</text><text x="677" y="149" fill="#fecdd3">risque de dépassement</text>
<rect x="790" y="75" width="140" height="92" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="860" y="105" fill="#f8fafc" font-weight="700">Réseau distant</text><text x="860" y="129" fill="#bfdbfe">décapsulation</text><text x="860" y="149" fill="#bfdbfe">puis livraison</text></g>
<g stroke="#60a5fa" stroke-width="2.5" fill="none" marker-end="url(#cloud-arrow)"><path d="M185 121 H217"/><path d="M375 121 H407"/><path d="M565 121 H597"/><path d="M755 121 H787"/></g>
<path d="M65 218 H895" stroke="#334155" stroke-width="1.5"/><text x="65" y="247" fill="#e2e8f0" font-size="16" font-weight="700">Mesurer séparément</text><g font-size="14" fill="#cbd5e1"><text x="65" y="273">1. taille interne avant encapsulation</text><text x="360" y="273">2. taille externe après encapsulation</text><text x="680" y="273">3. limite physique réellement utilisable</text></g>
<rect x="65" y="296" width="830" height="43" rx="8" fill="#251f14" stroke="#f59e0b"/><text x="480" y="322" fill="#fde68a" font-size="15" text-anchor="middle">Si l’outer packet dépasse la MTU du lien, il faut corriger le budget ou la stratégie PMTU.</text>
<circle r="7" fill="#a7f3d0" stroke="#064e3b" stroke-width="2"><animateMotion dur="6s" repeatCount="indefinite" path="M108,121 L297,121 L487,121 L677,121 L860,121"/></circle>
</svg>
</div>

### 15.2 CNI Kubernetes et MTU de cluster

Un cluster Kubernetes peut utiliser un plugin CNI qui crée des routes directes, un overlay, des tunnels chiffrés, des interfaces veth ou une combinaison de ces dispositifs. La bonne MTU dépend de l’architecture active et des fonctions activées sur chaque nœud. Une valeur copiée d’un environnement sans chiffrement peut être trop élevée dans un environnement qui ajoute WireGuard ou IPsec.

Établissez une fiche par type de nœud : système d’exploitation, version du noyau, CNI et version, mode overlay ou routé, chiffrement activé, MTU de l’interface physique, MTU des interfaces virtuelles, famille IP extérieure et présence de services mesh. Vérifiez ensuite un chemin entre deux pods sur des nœuds différents, puis un chemin entre pod et service externe. Un test pod-à-pod sur le même nœud peut éviter l’overlay et donner un faux sentiment de sécurité.

Une modification de MTU doit être traitée comme une modification de réseau distribuée. Les pods déjà démarrés peuvent conserver des interfaces anciennes tandis que les nouveaux adoptent une configuration différente. La validation doit donc couvrir les anciens et nouveaux pods, plusieurs nœuds, les chemins IPv4 et IPv6 concernés, ainsi que les charges UDP et TCP réelles. Documentez la période de convergence et le retour arrière.

### 15.3 Cloud public et limites des données visibles

Dans le cloud, l’hyperviseur, la carte réseau virtuelle et le fabric du fournisseur peuvent masquer des détails du chemin physique. Vous ne pourrez pas toujours capturer chaque frontière. Dans ce cas, combinez la documentation prise en charge par le fournisseur, les métriques de l’instance, les captures dans le système invité, les tests entre zones et la comparaison entre flux. Ne prétendez pas connaître une MTU physique interne que vous ne pouvez pas observer.

Les tests doivent refléter le chemin facturé et utilisé par l’application : région, zone, peering, NAT, passerelle VPN, load balancer, interface publique ou endpoint privé peuvent modifier le chemin. Les adresses de test doivent être des cibles autorisées. Un paquet réussi entre deux instances de la même zone ne valide pas automatiquement le trajet vers Internet ou vers un réseau d’entreprise.

## 16. Télémétrie, automatisation et observabilité

### 16.1 Mesurer une hypothèse au lieu de surveiller une seule valeur

Une alerte « MTU différente de 1500 » n’est généralement pas un diagnostic. Une valeur plus faible peut être parfaitement correcte sur un tunnel, tandis qu’une MTU de 1500 peut être erronée si le transport extérieur ne peut pas l’accommoder. La télémétrie utile associe le contexte de chemin à un symptôme observé : famille IP, cinq-tuple si disponible, interface d’entrée, interface de sortie, direction, taille testée, message ICMP reçu, identifiant de tunnel et horodatage.

Dans un système de production, collectez au minimum les compteurs d’erreurs et de drops des interfaces, les compteurs de tunnel si exposés, les retransmissions TCP, les timeouts d’application, les erreurs de sockets, les compteurs pare-feu pertinents et les événements ICMP filtrés. Chaque signal doit être interprété avec ses limites. Une retransmission n’indique pas à elle seule un problème MTU ; un compteur d’interface sans erreur ne prouve pas que le routeur intermédiaire n’a pas écarté le paquet.

### 16.2 Approche de mesure non intrusive

Une sonde active peut envoyer quelques tailles de datagrammes vers des destinations de mesure approuvées, avec un taux limité et un intervalle contrôlé. Les sondes doivent être identifiables et leurs résultats rattachés au chemin. Commencez par une petite charge et augmentez progressivement. Lorsque l’application ou le réseau est déjà chargé, évitez les balayages de tailles agressifs qui génèrent du trafic inutile ou ressemblent à un test de charge.

Les sondes qui utilisent ICMP Echo ne reproduisent pas nécessairement la politique réservée à TCP, UDP ou QUIC. Pour les applications sensibles, une sonde au niveau transport ou un test synthétique proche du protocole réel peut être plus représentatif. Documentez cette différence, afin que le résultat ne soit pas présenté comme une preuve de taille universelle.

### 16.3 Modèle de données d’incident

Associez chaque observation à un identifiant d’essai. Enregistrez au minimum : heure de début et de fin, source et destination anonymisées si nécessaire, famille IP, protocole, port si pertinent, interface et namespace, MTU locale, taille du paquet testée, DF ou comportement équivalent, résultat de la sonde, ICMP/PTB observé, point de capture, version du noyau, route sélectionnée et changement récent. Cette structure permet de comparer des tests sans mélanger des chemins différents.

Les journaux contenant adresses, ports, charges utiles, identifiants de client ou chemins internes peuvent être sensibles. Appliquez les règles internes de rétention, de contrôle d’accès et de minimisation. La traçabilité est utile ; une capture intégrale durable sans nécessité augmente les risques de confidentialité et de sécurité.

### 16.4 Seuils et alertes

Ne créez pas d’alerte unique qui déclenche une réduction globale de MTU. Un automate qui réagit à une seule sonde ratée peut provoquer une oscillation : il réduit la MTU, la sonde réussit, il l’augmente, la sonde échoue à nouveau. Une logique fiable exige répétitions, temporisation, validation sur plusieurs essais, borne minimale et maximale, historique du dernier changement et possibilité d’annulation.

Privilégiez une alerte corrélée, par exemple : hausse simultanée de retransmissions sur une classe de destinations, échec reproductible au-dessus d’une taille et absence du PTB attendu sur un point de capture. Même cette combinaison déclenche une investigation, pas une preuve absolue. L’algorithme doit pouvoir dire « données insuffisantes » au lieu de deviner.

## 17. Procédure de changement en production

### 17.1 Préparation et contrôle du risque

Avant de changer MTU, MSS ou politique ICMP, établissez le périmètre, l’impact, les propriétaires du service, la fenêtre de changement, les critères de succès, les critères d’arrêt, la restauration et les preuves à collecter. Identifiez les services qui traversent le même segment, y compris les flux secondaires, la supervision, l’accès distant et les plans de contrôle. Une réparation qui coupe la supervision peut compliquer le retour arrière.

Capturez l’état initial des interfaces, routes, tunnel, règles de pare-feu, paramètres TCP, métriques et symptômes applicatifs. Conservez les commandes exactes et leur sortie. Faites un test de référence avec tailles petite, moyenne et grande, dans chaque famille IP utilisée. Répétez suffisamment pour distinguer un phénomène intermittent d’un comportement stable, en restant raisonnable côté trafic.

### 17.2 Déploiement progressif

Appliquez d’abord le changement au plus petit périmètre permettant de valider l’hypothèse : un hôte de test, une interface de tunnel, un pool canari ou un chemin non critique. Ne modifiez pas simultanément MTU, MSS clamping, filtrage ICMP et route, car un résultat positif ne permettrait pas d’identifier l’action efficace. S’il y a une contrainte de temps et que plusieurs actions sont nécessaires pour restaurer le service, consignez chacune d’elles et programmez une analyse après rétablissement.

Après le premier changement, vérifiez la taille réellement observée, la route, les messages ICMP et le comportement de l’application. Testez une connexion neuve, puis une connexion persistante si le protocole s’y prête. Contrôlez à la fois le chemin aller et le retour. Étendez ensuite le déploiement par étapes, en arrêtant au premier indice de régression.

### 17.3 Critères de succès et retour arrière

Les critères doivent être mesurables : diminution du taux de timeout, réussite répétée de datagrammes jusqu’à la taille visée, absence d’erreur nouvelle sur les flux contrôles, maintien de la latence attendue et visibilité des messages PMTU nécessaires. Définissez les tailles et les protocoles dans le plan d’essai. « Le site s’ouvre » ne suffit pas si les transferts volumineux échouent toujours.

Retournez en arrière si les symptômes augmentent, si un autre service devient instable, si le changement empêche le plan de contrôle de fonctionner ou si les mesures ne confirment pas l’hypothèse. Le retour arrière doit restituer les valeurs initiales documentées, non des valeurs estimées. Vérifiez ensuite que l’environnement revient réellement à son état attendu.

### 17.4 Après le changement

Rédigez ce qui était observé, l’hypothèse testée, les commandes exécutées, les valeurs avant et après, les résultats par famille et transport, ainsi que les effets secondaires. Séparez le fait observé de l’interprétation. Exemple : « la charge utile UDP de 1380 octets échouait avant la modification et a réussi dix fois après » est un fait ; « le VPN avait forcément la mauvaise MTU » est une interprétation qui demande davantage de preuves.

Une solution temporaire doit porter un propriétaire, une date de réexamen, une condition de retrait et une dette technique explicite. Une valeur de MTU réduite peut rester plusieurs années après disparition du contexte qui l’avait motivée, et créer une fragmentation de capacité invisible lors de l’évolution du réseau.

## 18. Schéma 4 — séquence de changement contrôlé

<div style="max-width:100%;overflow-x:auto;">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="exp8-title exp8-desc" style="width:100%;height:auto;background:#0b1220;border-radius:12px;font-family:Arial,sans-serif">
<title id="exp8-title">Changement contrôlé en production</title><desc id="exp8-desc">Le changement suit une séquence de référence, hypothèse, modification limitée, validation et décision de déploiement ou retour arrière.</desc><defs><marker id="exp8-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs><text x="28" y="35" fill="#f8fafc" font-size="22" font-weight="700">Changer une variable, prouver le résultat</text>
<g text-anchor="middle" font-size="14"><rect x="30" y="90" width="160" height="82" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="110" y="119" fill="#f8fafc" font-weight="700">1. Référence</text><text x="110" y="145" fill="#bfdbfe">état / mesure</text><rect x="220" y="90" width="160" height="82" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="300" y="119" fill="#f8fafc" font-weight="700">2. Hypothèse</text><text x="300" y="145" fill="#bfdbfe">test discriminant</text><rect x="410" y="90" width="160" height="82" rx="10" fill="#3b2b15" stroke="#f59e0b"/><text x="490" y="119" fill="#fff7ed" font-weight="700">3. Canari</text><text x="490" y="145" fill="#fed7aa">changement limité</text><rect x="600" y="90" width="160" height="82" rx="10" fill="#12352e" stroke="#34d399"/><text x="680" y="119" fill="#ecfdf5" font-weight="700">4. Valider</text><text x="680" y="145" fill="#a7f3d0">succès mesuré</text><rect x="790" y="90" width="140" height="82" rx="10" fill="#142b46" stroke="#60a5fa"/><text x="860" y="119" fill="#f8fafc" font-weight="700">5. Décider</text><text x="860" y="145" fill="#bfdbfe">étendre/revenir</text></g><g fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#exp8-arr)"><path d="M190 131 H217"/><path d="M380 131 H407"/><path d="M570 131 H597"/><path d="M760 131 H787"/></g>
<path d="M860 173 V231 H490 V175" stroke="#fb7185" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#exp8-arr)"/><text x="676" y="218" fill="#fecdd3" font-size="13" text-anchor="middle">Critère d’arrêt → restauration</text><circle r="7" fill="#fbbf24"><animateMotion dur="7s" repeatCount="indefinite" path="M110,131 L300,131 L490,131 L680,131 L860,131 L860,231 L490,231 L490,131"/></circle><text x="480" y="292" fill="#cbd5e1" text-anchor="middle" font-size="14">Les valeurs initiales, les preuves et le retour arrière doivent être prêts avant le changement.</text></svg></div>

## 19. Études de cas expertes

### Cas A — Le PTB est reçu, mais la connexion ne s’améliore pas

**Observation :** la capture de l’hôte montre un ICMP Destination Unreachable, fragmentation needed, avec une indication de MTU. Le transfert applicatif échoue encore. Le réflexe ne doit pas être de rejeter le PTB comme inefficace ; il faut vérifier s’il appartient au bon flux et si le système l’a accepté.

**Hypothèses possibles :** le message est lié à un autre cinq-tuple ; la valeur de MTU annoncée ne correspond pas au chemin actuellement sélectionné ; une route avec ECMP a changé ; le paquet trop grand a quitté une interface différente ; le message est observé sur l’hôte mais rejeté par une politique locale ; le problème se situe plus loin, après la taille devenue acceptable ; l’application a conservé un état de connexion existant. Une capture montre l’arrivée sur une interface, pas l’acceptation par la pile transport.

**Méthode :** capturez simultanément, si possible, côté source et sur le lien de sortie. Comparez adresses, protocole, identifiants et informations incluses dans ICMP. Examinez les journaux du pare-feu local, la route de la connexion et les métriques de la pile. Refaites le test avec une nouvelle connexion, puis vérifiez si le paquet adapté est réellement émis. Si aucun paquet adapté n’apparaît, la piste se situe entre livraison du PTB, traitement de pile et état de transport. Si le paquet adapté part et se perd ailleurs, revenez au chemin en aval.

**Conclusion à ne pas tirer trop vite :** « j’ai vu ICMP dans Wireshark » ne signifie pas « la connexion l’a accepté et a recalculé sa taille ». Il faut prouver l’effet observable, pas simplement l’existence du message.

### Cas B — La MTU baisse sur le tunnel, mais certaines applications échouent encore

**Observation :** après une réduction du MTU de l’interface VPN, les pings de grande taille réussissent, mais un service échoue encore pendant les échanges de données. Certains utilisateurs sont affectés, d’autres non.

**Hypothèses :** les flux concernés prennent un autre chemin ou un autre tunnel ; le VPN est actif sur une seule famille IP ; une règle MSS agit uniquement sur certains SYN TCP ; le trafic applicatif utilise UDP ; l’application maintient une connexion établie avant changement ; le problème se trouve dans un overlay supplémentaire ; l’interface MTU changée n’est pas celle utilisée par le processus concerné.

**Méthode :** lister l’interface et la route par destination ; observer la famille IPv4/IPv6 ; comparer les SYN et MSS négociés, puis inspecter la taille des paquets de données. Capturez de part et d’autre du tunnel pour calculer l’écart d’encapsulation. Comparez les cas réussis et échoués avec des mêmes longueurs de charge utiles. Si seuls les flux TCP concernés progressent après MSS clamping, cela suggère une limitation efficace pour ces flux, sans résoudre nécessairement UDP ni les autres tunnels.

**Décision :** corriger la couche où l’incohérence est démontrée. Évitez d’abaisser systématiquement la MTU de toutes les interfaces si un tunnel particulier possède une surcharge anormale.

### Cas C — La sonde ICMP échoue, mais HTTPS fonctionne

**Observation :** Echo Request d’une taille élevée ne reçoit pas de réponse, alors que le navigateur télécharge des ressources volumineuses. Il serait incorrect de déduire immédiatement que la PMTU est faible. Echo et HTTPS diffèrent par protocole, ports, comportement applicatif, chemin possible et politique de filtrage.

**Méthode :** utilisez une sonde qui reproduit la famille IP et le protocole de l’application, ou un test synthétique à travers le même chemin. Examinez les tailles de paquets TLS/TCP ou UDP/QUIC. Confirmez si la sonde Echo a été envoyée, si elle a traversé le routeur et si l’écho de retour a été filtré. Comparez plusieurs répétitions et destinations. Si HTTPS fonctionne uniquement avec des tailles de datagrammes plus petites, l’écart devient une piste utile ; sinon, la sonde ICMP peut simplement ne pas être autorisée.

### Cas D — Le même hôte voit une PMTU différente selon la destination

**Observation :** une destination réussit à 1472 octets de charge utile ICMP IPv4, une autre seulement à 1360. Cette situation peut être normale : la PMTU dépend du chemin, du routage, des tunnels, de l’interface source et parfois du contexte de politique. Il ne faut pas installer une seule valeur globale sur l’hôte en supposant que le réseau entier est identique.

**Méthode :** contrôlez la destination exacte, la famille, la source et la route. Répétez le test, testez un autre chemin ou une route connue si c’est autorisé, et cherchez un point de convergence commun entre les destinations. Le diagnostic doit garder chaque résultat associé à son chemin, plutôt que de retenir uniquement la plus petite valeur et la propager sans justification.

### Cas E — Le MTU du serveur est 9000, celui du WAN 1500

**Observation :** un serveur et son switch local supportent des trames jumbo, mais le chemin vers une destination distante a une limite de 1500. Une MTU locale de 9000 est valide pour certains chemins locaux ; elle ne prouve pas que chaque chemin de sortie supporte ce format. Les routeurs IP peuvent fragmenter en IPv4 seulement lorsque c’est autorisé, ou renvoyer l’information nécessaire pour adapter l’émetteur ; les règles IPv6 sont différentes.

**Méthode :** déterminez où la frontière 9000/1500 est traversée et si l’émetteur connaît la contrainte. Pour les paquets IPv4 avec DF, confirmez le traitement du message ICMP approprié. Pour IPv6, vérifiez le traitement de Packet Too Big. Évitez d’activer une fragmentation aveugle pour « faire marcher » le chemin sans comprendre le coût et les implications.

### Cas F — ECMP rend le problème intermittent

**Observation :** la même sonde réussit neuf fois sur dix, ou les grands transferts réussissent après plusieurs tentatives. Un équilibre de charge peut envoyer les paquets sur des chemins différents, par exemple lorsque le hachage dépend de ports, protocole ou champs du paquet. Un chemin peut avoir une MTU inférieure, ou le retour ICMP peut suivre une voie différente.

**Méthode :** conservez un ensemble d’essais horodatés avec le même cinq-tuple, puis testez plusieurs tuples quand cela est pertinent et autorisé. Comparez les empreintes de route accessibles, les interfaces de sortie, les compteurs et les captures sur plusieurs points. La commande traceroute peut emprunter un hachage différent et n’est pas une preuve parfaite du trajet du transfert original. Demandez les données de télémétrie des routeurs en cas de besoin.

**Correction durable :** harmoniser les capacités des chemins en ECMP, assurer le retour d’informations PMTU ou mettre en place une découverte robuste au niveau du transport. Un abaissement global peut réduire les symptômes, mais ne corrige pas la cause d’un chemin hétérogène.

### Cas G — QUIC échoue alors que TCP vers le même serveur fonctionne

**Observation :** le navigateur ou le client réussit quand QUIC est disponible puis bascule parfois vers TCP ; le problème se manifeste avec une certaine taille de charge utile ou sur certains réseaux.

**Hypothèses :** filtrage UDP ou de messages ICMPv6/IPv4 ; surcharge d’un VPN ; chemin différent entre UDP et TCP ; variation des tailles datagrammes ; mise en œuvre de PMTU du transport ; règle de pare-feu ; offload ou capture mal interprétée. QUIC ne doit pas être diagnostiqué en supposant que la MSS TCP décrit ses paquets.

**Méthode :** capturez les datagrammes UDP/QUIC et la couche IP extérieure sur le même trajet ; vérifiez que les tailles mesurées sont bien des longueurs IP, UDP ou QUIC, car elles ne sont pas interchangeables. Recherchez les PTB et la réaction du client, puis comparez avec le transport de secours. Un QUIC Initial doit respecter les exigences de taille minimale définies par sa spécification, ce qui ne justifie pas de confondre charge utile UDP et longueur IP totale.

## 20. Laboratoire expert reproductible

### 20.1 Objectif et règles de sécurité

Ce laboratoire vise à prouver le comportement du transport et du réseau par une série contrôlée. Utilisez uniquement des machines dont vous avez l’autorisation, un réseau isolé et des flux de test. Ne bloquez pas l’ICMP sur un système de production pour « reproduire » une panne. Préparez un mécanisme de récupération hors bande avant tout changement qui pourrait interrompre votre session d’administration.

Le laboratoire devrait offrir au minimum une source, un routeur capable de modifier la MTU d’une interface, une destination, et une possibilité de capturer chaque côté du routeur. Pour tester les tunnels, ajoutez deux hôtes tunnel et un réseau intermédiaire à MTU connue. Notez les versions, interfaces, familles, routes et valeurs avant le test. L’adressage de documentation ci-dessous doit être remplacé par celui du laboratoire.

### 20.2 Expérience 1 — PMTUD IPv4 classique

Configurez un chemin dont le routeur intermédiaire a une MTU inférieure au paquet testé. Émettez un paquet IPv4 assez grand avec DF activé. Capturez sur l’entrée du routeur, sur la sortie si possible, puis sur le chemin de retour. Le résultat attendu est un message approprié si le routeur ne peut pas transmettre le paquet sans fragmentation. Vérifiez le type/code ICMP et la valeur de MTU annoncée lorsqu’elle est prise en charge.

Répétez le test sans DF seulement dans le laboratoire et uniquement pour observer la différence de comportement. Ce test ne veut pas dire que la fragmentation constitue la meilleure solution d’exploitation. Comptez les fragments si l’implémentation les génère et vérifiez que la destination peut les réassembler. Consignez la taille de paquet originale et les tailles de chaque fragment si visible.

### 20.3 Expérience 2 — panne provoquée par perte des PTB

Dans un réseau de laboratoire isolé, appliquez une règle temporaire qui supprime le message ICMP spécifique utilisé par le scénario. Ne supprimez pas tout l’ICMP sur une infrastructure partagée. Émettez ensuite une séquence de tailles croissantes et faites un transfert long. Observez que les petits paquets peuvent réussir tandis qu’un flux qui dépend de plus grands paquets cesse de progresser. Capturez aux deux côtés du point de filtrage afin de prouver la suppression.

Retirez la règle après le test et validez la restauration. Documentez les compteurs de règle, les heures, les tailles testées et le comportement avant/après. L’expérience doit démontrer le mécanisme, pas enseigner qu’il faut bloquer ICMP en production.

### 20.4 Expérience 3 — comparer PMTUD et PLPMTUD

Quand le transport et la pile du laboratoire le permettent, comparez un test qui dépend d’informations ICMP à un transport disposant d’une stratégie de découverte au niveau paquet. Le résultat attendu dépend de l’implémentation et des paramètres : PLPMTUD a besoin de probes, de règles d’accusé de réception ou d’une preuve de livraison, ainsi que d’une logique de validation. Il ne rend pas l’application insensible à toute perte et peut prendre du temps à converger.

Ne concluez pas qu’un comportement PLPMTUD est présent parce qu’une connexion a survécu une fois à une panne ICMP. Vérifiez la documentation de la pile ou du protocole, observez la taille des probes et la réaction aux pertes. Pour DPLPMTUD, identifiez quelle couche de transport produit les probes et quelles preuves elle exploite.

### 20.5 Expérience 4 — budget d’encapsulation

Établissez un tunnel qui ajoute un en-tête externe et un overhead clairement identifié. Calculez d’abord le maximum intérieur théorique : MTU extérieure moins les en-têtes et options réellement ajoutés. Ensuite, validez à l’aide des captures extérieures. Répétez en changeant un seul paramètre, comme la famille extérieure IPv4/IPv6 ou une option de tunnel, puis recalculez. La mesure doit confirmer la formule, pas remplacer la compréhension de ses composants.

Testez également le chemin de retour et toute la chaîne d’encapsulation. Deux tunnels imbriqués peuvent consommer le budget deux fois ; l’overhead du tunnel intérieur reste encapsulé dans le paquet transmis par le tunnel extérieur. Documentez précisément où la longueur est comptée : paquet intérieur, paquet extérieur, charge utile UDP, ou trame Ethernet.

### 20.6 Feuille de laboratoire

Pour chaque expérience, remplissez ce relevé :

| Champ | Valeur à enregistrer |
|---|---|
| Identifiant de l’essai | Numéro unique et date/heure |
| Environnement | Hôtes, routeur, système et versions |
| Chemin | Interfaces et éventuels tunnels |
| Famille/protocole | IPv4/IPv6, TCP/UDP/ICMP/QUIC |
| Taille demandée | Charge, transport et longueur IP si connues |
| Contrôle de fragmentation | DF ou comportement IPv6 applicable |
| Observation source | Paquet envoyé, erreur locale, timeout |
| Observation routeur | Entrée, sortie, PTB, compteur de règle |
| Observation destination | Réception, fragments, réponse |
| Conclusion | Fait mesuré, hypothèse, confiance |
| Restauration | Commandes et état final vérifié |

## 21. Matrice de diagnostic avancée

La matrice suivante oriente la prochaine mesure à effectuer. Elle ne remplace pas l’analyse du trajet réel : chaque symptôme est compatible avec plusieurs causes.

| Symptôme | Mesure prioritaire | Résultat qui renforce l’hypothèse MTU | Autres pistes à éliminer |
|---|---|---|---|
| Petits échanges OK, transferts longs bloqués | Test de tailles avec transport proche du réel | Échec reproductible au-dessus d’un seuil | Serveur, congestion, filtrage applicatif |
| Ping échoue, application fonctionne | Comparer politiques ICMP et transport réel | Pas de preuve suffisante à ce stade | Echo filtré, rate limit, route distincte |
| SYN/SYN-ACK OK, transfert TCP bloque | Capturer la taille des données et retransmissions | Grand segment répété sans progrès | TLS, proxy, serveur, perte générale |
| QUIC échoue, TCP fonctionne | Capturer UDP/QUIC et PTB | Datagrammes trop grands et réaction absente | UDP filtré, chemin différent, version client |
| Panne uniquement avec VPN | Comparer intérieur/extérieur | Taille extérieure dépasse le lien ou PTB perdu | Politique crypto, route, DNS, tunnel instable |
| Une destination fonctionne, l’autre non | Associer taille et route à chaque destination | PMTU différente ou route spécifique | Pare-feu, route asymétrique, service distant |
| Intermittence selon essais | Conserver tuple, varier tuples de façon contrôlée | Chemins ECMP différents ou PTB irréguliers | Perte aléatoire, congestion, load balancer |
| Trace hôte montre de gros paquets | Capture au fil ou compteurs de segmentation | Offload explique la différence de segmentation | Capture dans mauvaise interface, agrégation |
| PTB visible mais pas d’effet | Vérifier tuple, livraison et état de pile | Message non applicable ou non accepté | Erreur après le point où la PMTU a été réduite |

Une bonne investigation demande toujours : qu’est-ce qui a été observé, qu’est-ce que cette observation prouve réellement, et quelle mesure départage les hypothèses concurrentes ? Les formulations « peut indiquer » et « est compatible avec » sont souvent plus exactes que « signifie ». Réservez « confirmé » à une hypothèse soutenue par une expérience reproductible et une preuve sur le bon trajet.

## 22. Modèle de compte rendu d’incident

### 22.1 Résumé exécutif

Décrivez en quelques phrases le service affecté, les utilisateurs ou chemins concernés, le début de l’incident, l’impact observé, les mesures temporaires et l’état final. Évitez les conclusions techniques non prouvées dans le résumé. Si le mécanisme reste incertain, dites-le explicitement.

### 22.2 Chronologie et preuves

Pour chaque événement, consignez l’heure synchronisée, le composant, l’action, le résultat et la référence de preuve. Une chronologie peut inclure l’apparition du symptôme, première capture, réception d’un PTB, changement approuvé, test de non-régression et restauration. Documentez les éventuels écarts de temps entre appareils : sans synchronisation adéquate, l’ordre des paquets dans des captures multiples peut être mal interprété.

### 22.3 Analyse causale

Séparez les sections suivantes :

- **Symptôme :** ce que l’utilisateur ou la supervision constate.
- **Mécanisme :** ce que le protocole fait ou ne fait pas au moment du défaut.
- **Cause immédiate :** événement technique qui a déclenché l’impact.
- **Cause contributive :** condition qui a rendu le problème probable, par exemple l’absence d’une règle ICMP nécessaire ou un overhead tunnel non budgété.
- **Facteur de détection :** pourquoi la supervision n’a pas identifié le défaut plus tôt.
- **Correctif durable :** changement qui traite le mécanisme confirmé.
- **Prévention :** test, télémétrie, documentation ou garde-fou à introduire.

Ne qualifiez pas automatiquement le blocage d’ICMP comme « cause racine » si vous n’avez pas démontré que le paquet nécessaire était supprimé et que sa suppression empêchait la découverte de la taille du chemin. La cause peut être un MTU de tunnel mal calculé, une route inégale, une mauvaise configuration, ou plusieurs facteurs combinés.

### 22.4 Annexes et protection des données

Joignez les traces nécessaires, mais supprimez ou protégez les charges utiles et les identifiants sensibles lorsque ceux-ci ne sont pas indispensables. Mentionnez les versions d’outils, filtres de capture, interface, direction et limites connues. Une capture partielle doit être identifiée comme telle. Ne présentez pas comme preuve l’absence d’un paquet sur une interface qui n’était pas réellement sur le chemin.

## 23. Exercices de niveau expert avec corrigés

### Exercice 1 — Calcul de budget à travers deux tunnels

Un chemin IP extérieur est supposé offrir une MTU de 1500 octets. Le premier tunnel ajoute 50 octets et le deuxième 36 octets, selon la configuration de l’exercice. Quelle taille maximale de paquet intérieur théorique reste disponible si toutes ces valeurs représentent bien l’overhead complet et qu’aucun autre en-tête n’est ajouté ? Quelles vérifications devez-vous faire avant d’appliquer le résultat en production ?

**Corrigé :** le budget intérieur théorique est 1500 − 50 − 36 = 1414 octets. Ce calcul n’est fiable que si chaque overhead a été mesuré dans la même convention et inclut exactement les champs ajoutés. Il faut vérifier options, famille IP extérieure, tags, éventuelles extensions, chiffrement, deuxième encapsulation, comportement de fragmentation, valeur réelle de MTU de la sous-couche et chemin de retour. Il faut ensuite confirmer au moyen d’une capture sur le lien extérieur.

### Exercice 2 — MSS ne correspond pas à l’MTU entière

Une connexion TCP IPv4 a un MSS annoncé de 1360. Peut-on en déduire que la PMTU est exactement 1400 octets ?

**Corrigé :** non, pas sans contexte. Un MSS annoncé est une limite de données TCP pour le segment dans les conditions de l’annonce ; sa relation habituelle à un MTU IPv4 minimal sans options est 20 octets d’IP + 20 octets de TCP + MSS, mais options IP/TCP, politiques MSS clamping, familles, tunnels et asymétrie changent l’interprétation. 1360 + 40 = 1400 est une estimation classique, pas une preuve absolue de PMTU. La capture des paquets et le contexte de négociation sont nécessaires.

### Exercice 3 — PTB avec valeur absente ou suspecte

Un routeur renvoie un message ICMP IPv4 « fragmentation needed », mais l’indication de MTU ne semble pas exploitable. Quelle est la bonne démarche ?

**Corrigé :** vérifier la version du routeur, le type/code, la validité du message et le contexte du paquet invoqué. RFC 1191 décrit les mécanismes historiques de découverte et la prise en compte de l’information de MTU. Ne pas inventer une valeur arbitraire et ne pas traiter chaque ancien message comme équivalent. Tester avec des tailles connues, observer la limite reproductible, mettre à jour les équipements concernés si pertinent et documenter la limite. Pour les piles modernes, inspecter le comportement réellement pris en charge plutôt que supposer une réaction identique sur toutes les plateformes.

### Exercice 4 — QUIC Initial

Un analyste voit un datagramme contenant un QUIC Initial avec une charge utile UDP de 1200 octets. Quelle longueur IP doit-il s’attendre à voir ?

**Corrigé :** au moins 1228 octets si IPv4 minimal sans options (20 IP + 8 UDP + 1200 UDP payload), ou 1248 octets avec IPv6 de base (40 IPv6 + 8 UDP + 1200 UDP payload), avant extension éventuelle et autres contraintes de chemin. Le chiffre de 1200 octets est la charge utile UDP minimale visée par la spécification QUIC Initial, pas la longueur totale du paquet IP. Les captures et encapsulations doivent être interprétées avec ces couches séparées.

### Exercice 5 — La capture hôte montre 64 Ko

La capture sur un serveur affiche un paquet TCP de dizaines de kilo-octets à destination d’un réseau Ethernet MTU 1500. Peut-on conclure qu’il a été envoyé tel quel sur le fil ?

**Corrigé :** non. GSO/TSO peuvent représenter à un point de capture un gros bloc qui sera segmenté plus tard. RSC/GRO peuvent agréger des segments en réception. Il faut établir où a lieu la segmentation ou l’agrégation, comparer avec une capture extérieure ou des compteurs fiables, puis distinguer une représentation logicielle d’un paquet sur le fil. Ne désactivez pas les offloads sur un serveur critique sans évaluation ; une capture externe est parfois une preuve plus propre.

### Exercice 6 — La baisse du MTU a réparé le service

Le passage d’une MTU d’interface de 1500 à 1380 résout un téléchargement. Quelle conclusion peut-on formuler ?

**Corrigé :** la modification soutient l’hypothèse qu’une taille de paquet ou un mécanisme de segmentation/découverte intervenait dans le problème. Elle ne prouve pas la cause complète. Il faut vérifier si le paquet dépassait un lien du tunnel, si un PTB était perdu, si un chemin différait, ou si un effet secondaire a changé le comportement. Le rapport doit distinguer observation et cause racine. Après rétablissement, un correctif durable doit traiter le budget du chemin ou la découverte et être soumis à des tests de non-régression.

### Exercice 7 — IPv6 en dessous de 1280

Un tunnel semble offrir moins de 1280 octets de PMTU extérieure. Faut-il simplement annoncer une PMTU IPv6 intérieure de 1200 ?

**Corrigé :** ne généralisez pas cette réponse. IPv6 impose un support de base à 1280 octets au niveau de la couche IPv6, et RFC 8201 traite le PMTUD IPv6. Un lien ou tunnel avec un budget inférieur doit suivre les mécanismes et règles applicables à la couche concernée ; il ne faut pas inventer une PMTU IPv6 arbitrairement inférieure. Vérifiez le type d’encapsulation, l’adaptation de lien, la prise en charge du tunnel et le comportement spécifié par l’implémentation.

### Exercice 8 — Le PTB n’arrive que dans une direction

Le transfert échoue de A vers B, mais vous ne voyez pas de PTB dans la capture de A. Que faire avant d’affirmer que le routeur ne génère pas de PTB ?

**Corrigé :** capturez à proximité du point où le paquet trop grand est abandonné, puis sur le retour vers A. Vérifiez l’interface de capture, le filtre, le plan de contrôle, le routage retour, les ACL, la redirection ICMP et les pertes de capture. Le routeur peut générer le message mais celui-ci peut être filtré ou suivre une route différente. Une absence sur la source ne prouve pas une absence de génération.

### Exercice 9 — ECMP et tuple variable

Un test de taille réussit pour un port source et échoue pour un autre. Quelle hypothèse examiner ?

**Corrigé :** certains équipements utilisent des champs du flux pour répartir le trafic entre chemins ECMP. Des ports source différents peuvent donc sélectionner des chemins distincts. Il faut confirmer cette variation avec des traces, une télémétrie de routeur ou des tests contrôlés, en tenant compte des mécanismes de hachage. La différence n’est pas une preuve automatique d’ECMP : NAT, état pare-feu ou politiques par port peuvent également changer le chemin.

### Exercice 10 — Choisir la réparation

Vous observez une MTU de tunnel incohérente, un filtre ICMP trop large et une MSS clamping appliquée à tout le trafic d’un site. Quelle priorité adopter ?

**Corrigé :** établir les preuves et traiter le mécanisme à la bonne couche. Corriger le budget ou la configuration de tunnel quand cela est confirmé ; autoriser les messages ICMP/PTB nécessaires tout en appliquant les contrôles de validation pertinents ; limiter le MSS clamping à un périmètre justifié et tester les chemins TCP concernés. Faire les changements séquentiellement si la situation le permet, conserver un retour arrière et valider UDP, QUIC, IPv4, IPv6 et les services non concernés. Une règle large peut masquer un défaut et créer des effets secondaires, elle ne constitue pas forcément le correctif durable.

## 24. Checklist de validation avant clôture

### Protocole et preuve

- [ ] Le paquet trop grand est identifié avec sa longueur et son contexte exacts.
- [ ] La famille IP, le protocole et le tuple source/destination sont documentés.
- [ ] Le point où le paquet est rejeté ou perdu est localisé autant que possible.
- [ ] Le PTB attendu est recherché sur le bon chemin et son traitement est observé, pas seulement sa présence.
- [ ] Les règles IPv4 et IPv6 sont évaluées séparément.
- [ ] Les captures sont interprétées en tenant compte des offloads et du point d’observation.

### Tunnel et transport

- [ ] L’overhead de chaque encapsulation est calculé sur la configuration réelle.
- [ ] Le budget extérieur et le budget intérieur sont explicitement séparés.
- [ ] Le chemin de retour est testé.
- [ ] TCP/MSS, UDP et QUIC sont testés selon les protocoles réellement utilisés.
- [ ] Les résultats restent associés à la destination et au chemin qui les ont produits.
- [ ] Toute valeur de MTU temporaire possède une justification et une date de réexamen.

### Changement opérationnel

- [ ] L’état initial et les commandes de restauration sont consignés.
- [ ] La portée du changement est minimale.
- [ ] Les critères de succès et d’arrêt sont mesurables.
- [ ] Les tests de non-régression couvrent les services essentiels.
- [ ] Le propriétaire de la correction et les actions de prévention sont identifiés.
- [ ] Le compte rendu distingue faits, hypothèses et conclusions confirmées.

## 25. Glossaire expert

**Black hole PMTUD :** panne dans laquelle un paquet trop grand ne progresse plus et où l’information nécessaire pour réduire la taille ne permet pas d’atteindre ou d’influencer correctement la source. **DPLPMTUD :** Datagram Packetization Layer PMTU Discovery, approche de découverte définie pour des protocoles transport de datagrammes qui s’appuie sur des probes et des preuves de livraison. **ECMP :** Equal-Cost Multi-Path, répartition entre plusieurs chemins de coût égal. **GRO/GSO/TSO :** mécanismes d’agrégation ou de segmentation qui peuvent modifier la représentation des paquets au point de capture. **ICMP/PTB :** messages de contrôle qui signalent notamment qu’un paquet ne peut être transmis en raison de sa taille ; leur type et leurs règles diffèrent entre IPv4 et IPv6. **MSS :** maximum segment size, plafond des données TCP dans un segment. **MTU :** maximum transmission unit d’une interface ou d’un lien selon le contexte. **PMTU :** MTU du chemin entre une source et une destination dans un contexte donné. **PLPMTUD :** Packetization Layer Path MTU Discovery. **Probe :** paquet de test envoyé pour évaluer une limite de taille ou confirmer une taille candidate. **PTB :** Packet Too Big, message ICMPv6 signalant qu’un paquet dépasse la capacité de transmission du prochain lien. **Tuple :** combinaison d’éléments identifiant un flux, habituellement adresses, protocole et ports. **Underlay :** réseau qui transporte les paquets d’un overlay. **Overlay :** réseau logique construit au-dessus d’un réseau sous-jacent par encapsulation ou autres mécanismes.

## 26. Références techniques officielles

Les RFC sont la source normative principale pour les comportements décrits. Les implémentations et versions de systèmes peuvent varier ; confrontez la norme au comportement mesuré et à la documentation du système déployé.

1. **RFC 1191 — Path MTU Discovery (IPv4).** Définit le mécanisme historique IPv4 et l’utilisation des messages ICMP « fragmentation needed ». https://www.rfc-editor.org/rfc/rfc1191.html
2. **RFC 8201 — Path MTU Discovery for IP version 6.** Spécifie le PMTUD IPv6 et le traitement de la taille du chemin. https://www.rfc-editor.org/rfc/rfc8201.html
3. **RFC 4821 — Packetization Layer Path MTU Discovery.** Décrit une approche de découverte à la couche paquetisation, utile lorsque l’information ICMP n’est pas suffisante. https://www.rfc-editor.org/rfc/rfc4821.html
4. **RFC 8899 — Datagram Packetization Layer PMTU Discovery.** Décrit DPLPMTUD et les aspects de découverte au niveau transport/datagramme. https://www.rfc-editor.org/rfc/rfc8899.html
5. **RFC 8900 — IP Fragmentation Considered Fragile.** Explique pourquoi dépendre de la fragmentation IP peut être fragile dans les réseaux réels. https://www.rfc-editor.org/rfc/rfc8900.html
6. **RFC 9293 — Transmission Control Protocol (TCP).** Référence de base sur TCP, y compris des éléments pertinents au MSS et au transport. https://www.rfc-editor.org/rfc/rfc9293.html
7. **RFC 9000 — QUIC: A UDP-Based Multiplexed and Secure Transport.** Référence pour les datagrammes QUIC, les exigences de taille et les contraintes de transport. https://www.rfc-editor.org/rfc/rfc9000.html
8. **RFC 4301 — Security Architecture for the Internet Protocol.** Architecture de sécurité IPsec ; à consulter pour l’analyse de l’encapsulation et des politiques. https://www.rfc-editor.org/rfc/rfc4301.html
9. **RFC 2923 — TCP Problems with Path MTU Discovery.** Document historique sur certains modes de défaillance TCP/PMTUD. https://www.rfc-editor.org/rfc/rfc2923.html

Ces références n’impliquent pas que tous les équipements implémentent toutes les fonctions ou qu’ils se comportent de façon identique. Consignez les versions, le contexte et les résultats expérimentaux. Ne remplacez pas une observation réelle par une phrase de norme hors contexte ; utilisez la norme pour formuler l’hypothèse et interpréter le résultat.

## 27. Ce qui différencie le niveau expert

À ce stade, l’objectif n’est plus simplement de reconnaître un symptôme et de lancer un ping de grande taille. L’objectif est de construire un raisonnement qui résiste aux contre-exemples : paquet et longueur identifiés, chemin associé au test, messages de contrôle suivis, budgets d’encapsulation calculés, comportement du transport observé, effets des offloads considérés et conclusions proportionnées aux preuves. Un expert doit pouvoir expliquer non seulement pourquoi une mesure améliore la connexion, mais aussi ce qu’elle ne prouve pas.

Le dépannage MTU/PMTUD réussi est une enquête sur un chemin, pas la chasse à une valeur magique. La taille pertinente dépend de la destination, du protocole, de l’encapsulation, de la route et des mécanismes de découverte. Une mesure locale est une donnée importante mais limitée. Un changement de MTU peut être un contournement utile, mais il doit être justifié, circonscrit, mesuré et accompagné d’un plan de restauration. La correction durable vise à rendre la taille utilisable et sa découverte cohérentes sur tous les chemins supportés.

