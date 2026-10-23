<style>
.ws-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.2rem 0;padding:.75rem;border:1px solid #23384f;border-radius:14px;background:#080f19;color:#e6eef8;box-sizing:border-box}
.ws-diagram svg{display:block;width:100%;height:auto;max-width:100%}
.ws-diagram .flow{stroke-dasharray:8 7;animation:wsmiDash 2s linear infinite}
@keyframes wsmiDash{to{stroke-dashoffset:-30}}
@media(prefers-reduced-motion:reduce){.ws-diagram .flow{animation:none!important}}
</style>

# Analyse de paquets avec Wireshark — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Domaine :** Réseaux, diagnostic, analyse de performances et sécurité défensive  
**Prérequis :** savoir lancer une capture, reconnaître les adresses MAC/IP et les ports, appliquer des filtres simples et identifier les principaux protocoles.  
**Objectif :** passer d’une simple lecture de paquets à une enquête reproductible : définir une hypothèse, capturer au bon endroit, reconstruire un flux, mesurer les délais, distinguer les symptômes des causes possibles et documenter une conclusion étayée.

> **Cadre d’utilisation :** travaille sur ton propre ordinateur, un laboratoire ou un réseau pour lequel tu disposes d’une autorisation explicite. Les captures peuvent contenir des données personnelles, des jetons de session ou des informations internes. Ne diffuse pas un fichier PCAPNG brut sans vérifier ce qu’il contient.

## 1. La méthode d’analyse intermédiaire

Au niveau débutant, on apprend à repérer un protocole et à lire des champs. Au niveau intermédiaire, la compétence centrale consiste à répondre à une question précise sans se laisser distraire par tous les paquets visibles.

Une enquête solide suit une boucle simple :

1. **Définir le symptôme** : lenteur, délai DNS, connexion refusée, perte apparente, négociation TLS qui n’aboutit pas ou comportement intermittent.
2. **Formuler une hypothèse testable** : par exemple « la requête DNS reçoit-elle une réponse tardive ? » plutôt que « le réseau est cassé ».
3. **Choisir le point d’observation** : client, serveur, interface de sortie du routeur, port miroir ou TAP. Le point détermine ce que la capture peut démontrer.
4. **Capturer une reproduction courte** : noter l’heure, l’action effectuée, l’interface et les éventuels filtres de capture.
5. **Isoler l’échange** : adresse, port, protocole, identifiant de flux, requête et réponse.
6. **Mesurer et confronter les indices** : délais, numéros de séquence, retransmissions, réponses DNS, drapeaux TCP, volumes et statistiques.
7. **Conclure avec un niveau de confiance** : distinguer ce qui est observé de ce qui reste une hypothèse et indiquer la prochaine vérification utile.

### 1.1 Le principe de la preuve limitée

Une capture prouve ce qui a été observé au point de capture. Elle ne prouve pas automatiquement ce qui se passe sur les interfaces invisibles. Si un SYN sort du client et qu’aucun SYN-ACK n’apparaît, plusieurs explications restent possibles : serveur indisponible, filtrage, problème de routage, perte de retour, mauvaise interface de capture ou limitation de capture. Il faut observer l’autre côté ou vérifier les journaux et compteurs pour réduire l’incertitude.

### Schéma 1 — Une enquête réseau se construit à partir de plusieurs points d’observation

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" role="img" aria-label="Schéma d'une enquête réseau : le client échange avec un serveur à travers un réseau ; des points de capture client, réseau et serveur fournissent des observations complémentaires."><defs><marker id="wsm1a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="wsm1b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#72e4a5"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.line{stroke:#66d9ff;stroke-width:2.5;fill:none;marker-end:url(#wsm1a)}.obs{stroke:#72e4a5;stroke-width:2;stroke-dasharray:5 5;fill:none}.flow{stroke-dasharray:8 7;animation:wsmiDash 2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="34" y="75" width="170" height="92" rx="12" fill="#142d45" stroke="#66d9ff" stroke-width="2"/><text x="119" y="105" class="t">Client</text><text x="119" y="128" class="s">10.10.1.20</text><text x="119" y="147" class="s">Capture A</text><rect x="355" y="75" width="190" height="92" rx="12" fill="#20283a" stroke="#ffc46b" stroke-width="2"/><text x="450" y="105" class="t">Réseau / pare-feu</text><text x="450" y="128" class="s">NAT, ACL, routage</text><text x="450" y="147" class="s">Capture B</text><rect x="696" y="75" width="170" height="92" rx="12" fill="#16382e" stroke="#72e4a5" stroke-width="2"/><text x="781" y="105" class="t">Serveur</text><text x="781" y="128" class="s">10.10.8.40</text><text x="781" y="147" class="s">Capture C</text><path d="M204 101H350" class="line flow"/><path d="M545 101H691" class="line flow"/><path d="M696 143H550" fill="none" stroke="#72e4a5" stroke-width="2.5" marker-end="url(#wsm1b)"/><path d="M355 143H209" fill="none" stroke="#72e4a5" stroke-width="2.5" marker-end="url(#wsm1b)"/><rect x="74" y="224" width="752" height="78" rx="12" fill="#101d2b" stroke="#344963"/><text x="450" y="250" class="t">Comparer des observations corrélées</text><text x="450" y="272" class="s">Horodatage · 5-tuple · numéros TCP · requêtes/réponses · compteurs réseau</text><text x="450" y="289" class="s">Une différence entre points localise une zone à examiner, mais ne désigne pas à elle seule la cause.</text><path d="M119 167V213" class="obs"/><path d="M450 167V213" class="obs"/><path d="M781 167V213" class="obs"/></svg></div>

## 2. Préparer une capture exploitable

### 2.1 Capturer au bon endroit

Avant d’appuyer sur le bouton de capture, réponds à quatre questions :

- **Quel appareil émet la requête ?** Le poste utilisateur, un serveur, une passerelle ou un proxy ?
- **Quelle interface porte le trafic ?** Ethernet, Wi-Fi, VPN, loopback, adaptateur de machine virtuelle ou interface de conteneur ?
- **Quel moment reproduit le problème ?** Une seule action reproductible vaut mieux qu’une capture de plusieurs heures sans contexte.
- **Quel est le point de référence ?** Pour connaître ce que le client a envoyé, capture côté client ; pour vérifier ce que le serveur a reçu, capture côté serveur ou sur un point réseau adapté.

Sur un switch Ethernet, le mode promiscuité d’une carte ne permet généralement pas de voir les échanges unicast des autres ports. Il peut être nécessaire de configurer un port miroir (SPAN), d’utiliser un TAP ou de capturer sur l’un des hôtes. Il faut vérifier le sens miroir, les VLAN inclus et les compteurs de perte de capture.

### 2.2 Quand utiliser un filtre de capture ?

Les filtres de capture réduisent ce qui est enregistré pendant la capture. Ils utilisent la syntaxe du mécanisme de capture, généralement dérivée de libpcap/BPF. Ils sont efficaces pour réduire le volume mais une erreur peut exclure définitivement les paquets nécessaires.

Exemples courants à adapter au laboratoire :

| But | Filtre de capture possible |
|---|---|
| DNS sur UDP ou TCP | `port 53` |
| Un hôte IPv4 précis | `host 192.0.2.10` |
| Un service TCP | `tcp port 443` |
| Trafic entre deux hôtes | `host 192.0.2.10 and host 198.51.100.20` |
| ICMP IPv4 | `icmp` |
| Exclure le trafic SSH | `not port 22` |

Ces expressions ne sont pas des filtres d’affichage. Vérifie leur syntaxe dans la fenêtre de filtre de capture avant de lancer une collecte importante. Avec un filtre de capture incorrect, Wireshark ne peut pas restaurer les paquets qui n’ont jamais été enregistrés.

### 2.3 Filtre d’affichage : filtrer sans supprimer

Le filtre d’affichage sélectionne les paquets visibles sans effacer les autres paquets de la capture. Il utilise une syntaxe plus riche, avec des noms de champs de protocoles comme `ip.addr`, `tcp.flags.syn`, `dns.flags.rcode` et `tcp.analysis.retransmission`. Les noms des champs peuvent évoluer avec les versions ; la boîte de dialogue d’expression et la référence de filtres de ta version sont les sources les plus sûres.

### Schéma 2 — Ne pas confondre filtre de capture et filtre d’affichage

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-label="Comparaison entre filtre de capture qui choisit les paquets enregistrés et filtre d'affichage qui masque temporairement les paquets hors critères sans les supprimer du fichier."><defs><marker id="wsm2a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="wsm2b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#72e4a5"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.a{stroke:#66d9ff;stroke-width:2.5;fill:none;marker-end:url(#wsm2a)}.b{stroke:#72e4a5;stroke-width:2.5;fill:none;marker-end:url(#wsm2b)}.flow{stroke-dasharray:8 7;animation:wsmiDash 2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="35" y="34" width="830" height="124" rx="12" fill="#101d2b" stroke="#344963"/><text x="450" y="58" class="t">1. Pendant la capture — filtre de capture</text><rect x="62" y="76" width="190" height="58" rx="8" fill="#172b43" stroke="#66d9ff"/><text x="157" y="99" class="t">Trafic entrant</text><text x="157" y="118" class="s">Tous les paquets vus</text><path d="M252 105H322" class="a flow"/><rect x="328" y="76" width="244" height="58" rx="8" fill="#332b19" stroke="#ffc46b"/><text x="450" y="99" class="t">Filtre BPF</text><text x="450" y="118" class="s">ex. port 53</text><path d="M572 105H644" class="a flow"/><rect x="650" y="76" width="188" height="58" rx="8" fill="#16382e" stroke="#72e4a5"/><text x="744" y="99" class="t">Fichier capturé</text><text x="744" y="118" class="s">Paquets retenus seulement</text><rect x="35" y="182" width="830" height="142" rx="12" fill="#101d2b" stroke="#344963"/><text x="450" y="206" class="t">2. Après la capture — filtre d’affichage</text><rect x="62" y="226" width="190" height="70" rx="8" fill="#172b43" stroke="#66d9ff"/><text x="157" y="251" class="t">Fichier complet</text><text x="157" y="270" class="s">Paquets capturés</text><path d="M252 261H322" class="b flow"/><rect x="328" y="226" width="244" height="70" rx="8" fill="#16382e" stroke="#72e4a5"/><text x="450" y="251" class="t">Filtre d’affichage</text><text x="450" y="270" class="s">ex. tcp.analysis.retransmission</text><path d="M572 261H644" class="b flow"/><rect x="650" y="226" width="188" height="70" rx="8" fill="#20283a" stroke="#c1a4ff"/><text x="744" y="251" class="t">Vue limitée</text><text x="744" y="270" class="s">Les autres paquets restent</text></svg></div>

## 3. Maîtriser les filtres d’affichage

Les filtres deviennent plus puissants lorsqu’on combine plusieurs champs sans rendre l’expression trop opaque. Commence par un filtre simple, valide le résultat, puis ajoute un critère à la fois.

### 3.1 Opérateurs et exemples utiles

| Objectif | Filtre d’affichage |
|---|---|
| Montrer DNS | `dns` |
| TCP seulement | `tcp` |
| Adresse source ou destination | `ip.addr == 192.0.2.10` |
| Source précise | `ip.src == 192.0.2.10` |
| Port de destination TCP | `tcp.dstport == 443` |
| Plusieurs conditions | `tcp && ip.addr == 192.0.2.10` |
| Un ou plusieurs hôtes | `ip.addr == 192.0.2.10 || ip.addr == 198.51.100.20` |
| SYN sans ACK | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| RST TCP | `tcp.flags.reset == 1` |
| Retransmissions reconnues | `tcp.analysis.retransmission` |
| Fenêtre TCP nulle | `tcp.analysis.zero_window` |
| Réponse DNS avec code d’erreur | `dns.flags.rcode != 0` |
| ICMP | `icmp` |
| Paquets plus grands que 1 400 octets | `frame.len > 1400` |
| Délai depuis le paquet précédent supérieur à 1 seconde | `frame.time_delta > 1` |

Les filtres ci-dessus sont des exemples, pas une garantie que chaque capture contiendra ces cas. Certains noms de champs et leur disponibilité peuvent changer selon les versions et les dissectors actifs. Utilise l’autocomplétion de ta version de Wireshark si un champ est refusé.

### 3.2 Parenthèses et logique

`&&` signifie « ET », `||` signifie « OU » et `!` signifie « NON ». Les parenthèses rendent les intentions explicites.

Exemple :

```text
(ip.addr == 192.0.2.10 || ip.addr == 198.51.100.20) && tcp
```

Ce filtre montre le trafic TCP lié à l’un ou l’autre des hôtes. Sans parenthèses, la priorité des opérateurs peut donner un résultat différent de l’intention du lecteur. Pour diagnostiquer une expression, simplifie-la et vérifie chaque partie séparément.

### 3.3 Champs présents, comparaisons et ensembles

Un filtre peut rechercher la présence d’un champ, comparer une valeur ou combiner plusieurs champs. Exemple : `tcp.options.mss_val` cible les paquets où le champ de MSS TCP est décodé, tandis que `tcp.window_size_value < 4096` cherche une fenêtre annoncée faible dans le contexte décodé. Vérifie l’intitulé exact de la version utilisée ; les champs « fenêtre brute » et « fenêtre calculée » ne sont pas interchangeables.

Pour éviter les erreurs de logique, évite les expressions géantes copiées d’un forum. Écris une expression courte, garde-la dans une note, puis ajoute une condition après avoir confirmé ce que la précédente fait. Les filtres nommés/sauvegardés sont utiles pour les contrôles répétitifs.

### 3.4 Limiter à un flux TCP

Sélectionne un paquet du flux, puis utilise **Follow → TCP Stream** ou le filtre de conversation proposé par Wireshark. Le filtre `tcp.stream eq N` isole généralement le flux TCP indexé N dans le fichier de capture. La valeur N doit être celle de ta capture, pas une constante universelle. Ce filtre facilite la lecture de la négociation et des segments associés, mais n’ajoute aucune donnée absente du fichier.

### 3.5 Afficher un champ sous forme de colonne

Lorsqu’un champ mérite d’être comparé sur beaucoup de lignes, clique dessus dans le panneau des détails et utilise la fonction d’application en colonne. Des colonnes utiles incluent les ports, `tcp.stream`, `tcp.len`, les écarts temporels ou les codes de réponse DNS. Les colonnes personnalisées réduisent les changements de panneau pendant l’analyse.

## 4. Lire TCP au-delà du handshake

### 4.1 Le handshake à trois étapes

L’établissement TCP classique comporte un SYN du client, un SYN-ACK du serveur et un ACK du client. Le premier paquet permet notamment de négocier des options TCP ; le SYN-ACK confirme la réception du SYN et propose le numéro de séquence initial de l’autre extrémité ; l’ACK final confirme la réception de cette proposition.

### Schéma 3 — Établissement TCP et premiers échanges

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-label="Diagramme temporel TCP : client envoie SYN, serveur répond SYN-ACK, client envoie ACK, puis échange illustratif de données et accusé de réception."><defs><marker id="wsm3a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker><marker id="wsm3b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#72e4a5"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.c{stroke:#66d9ff;stroke-width:2.5;fill:none;marker-end:url(#wsm3a)}.r{stroke:#72e4a5;stroke-width:2.5;fill:none;marker-end:url(#wsm3b)}.flow{stroke-dasharray:8 7;animation:wsmiDash 2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><text x="190" y="30" class="t">Client</text><text x="710" y="30" class="t">Serveur</text><path d="M190 44V330M710 44V330" stroke="#344963" stroke-width="2" stroke-dasharray="5 6"/><path d="M200 70L697 102" class="c flow"/><text x="450" y="70" class="s">SYN · Seq=x</text><path d="M700 132L203 164" class="r flow"/><text x="450" y="126" class="s">SYN, ACK · Seq=y · Ack=x+1</text><path d="M200 194L697 224" class="c flow"/><text x="450" y="192" class="s">ACK · Ack=y+1</text><path d="M200 251L697 281" class="c flow"/><text x="450" y="249" class="s">Données applicatives</text><path d="M700 303L203 325" class="r flow"/><text x="450" y="299" class="s">ACK des données</text></svg></div>

Si le handshake n’apparaît pas complet, demande-toi d’abord si la capture a commencé avant le début de la connexion et si le bon côté est observé. Une capture démarrée après l’établissement peut commencer au milieu d’un flux déjà établi. Une capture filtrée sur le port serveur peut également omettre un segment pertinent si le filtre ne correspond pas à ce que tu imaginais.

### 4.2 Numéros de séquence et d’acquittement

TCP présente des numéros de séquence et d’acquittement relatifs dans Wireshark par défaut dans de nombreux contextes. Un ACK indique en général le prochain octet attendu par son émetteur. Si une extrémité a reçu tous les octets jusqu’au numéro N−1, elle peut acquitter N. Les segments avec données avancent le numéro de séquence en fonction du nombre d’octets transportés ; SYN et FIN consomment chacun un numéro de séquence.

Ne compare pas des numéros relatifs entre deux flux différents comme s’ils appartenaient au même compteur. Lorsque tu compares deux captures, vérifie l’option de numérotation relative, le début de la connexion et l’alignement temporel. Les retransmissions, les captures partielles et le mécanisme d’offload réseau peuvent complexifier la lecture.

### 4.3 Fenêtre TCP et contrôle de flux

Le récepteur annonce combien de données il est prêt à recevoir en indiquant une fenêtre. La fenêtre évolue au fil de la consommation du tampon de réception. Un événement « zero window » signifie que le destinataire annonce temporairement une fenêtre nulle ; il peut être occupé, bloqué ou incapable de vider assez vite le tampon. Ce n’est pas automatiquement une panne du réseau : il faut examiner le côté qui annonce la fenêtre, les mises à jour de fenêtre, le débit et les journaux de l’application.

La fenêtre annoncée dans l’en-tête peut être interprétée avec un facteur d’échelle négocié au handshake. Dans Wireshark, distingue la valeur brute de la valeur calculée/échelonnée. Une fenêtre basse, prise seule, ne prouve ni perte ni congestion ; elle peut refléter un contrôle de flux normal.

### 4.4 Retransmission, Dup ACK, perte et réordonnancement

Une retransmission indique qu’un segment semble avoir été renvoyé. Cela peut être lié à une perte, à un ACK perdu, à un réordonnancement, à une duplication ou à une particularité de capture. Wireshark utilise des heuristiques pour marquer certains événements ; il faut lire les paquets autour de l’alerte et, idéalement, corroborer avec une capture à l’autre extrémité ou avec les compteurs du réseau.

- **Retransmission TCP :** un segment déjà envoyé semble être réémis.
- **Dup ACK :** un ACK répète le même prochain octet attendu ; cela peut accompagner un segment manquant ou arrivé dans le désordre.
- **Fast retransmission :** TCP peut retransmettre sans attendre l’expiration du temporisateur lorsqu’il reçoit suffisamment d’ACK dupliqués.
- **RTO :** expiration du délai de retransmission, souvent associée à un silence plus marqué.
- **Out-of-order :** les segments sont observés dans un ordre différent de celui attendu par la séquence TCP ; cela peut être causé par le réseau ou par le point/circuit de capture.

### 4.5 Pourquoi un checksum semble incorrect

Une capture côté émission peut être réalisée avant que la carte réseau calcule le checksum final : checksum offload. Wireshark peut alors afficher une somme de contrôle incorrecte qui sera complétée par la carte avant l’envoi sur le câble. De même, segmentation offload et receive coalescing peuvent faire apparaître des tailles ou regroupements qui ne reflètent pas exactement les trames présentes sur le réseau.

Pour déterminer si un checksum est réellement corrompu, capture si possible sur un point indépendant du poste émetteur (TAP, port miroir bien configuré ou autre hôte) et compare. Ne désactive pas l’offload en production sans comprendre l’impact sur les performances ; une désactivation temporaire dans un laboratoire peut servir d’expérience contrôlée.

### 4.6 Connexion refusée, timeout ou fermeture

Un RST observé immédiatement après une tentative peut indiquer qu’un hôte ou un équipement rejette la connexion ou qu’aucun service n’accepte ce port. Un SYN répété sans réponse indique seulement que la réponse attendue n’est pas visible au point de capture. Une fermeture avec FIN est différente d’une réinitialisation RST. Observe quelle extrémité envoie le drapeau, l’ordre des paquets, le délai et le contexte applicatif avant de conclure.

## 5. Analyse avancée de DNS

### 5.1 Identifier chaque transaction

Filtre `dns`, puis distingue les requêtes des réponses. Vérifie le nom demandé, le type d’enregistrement, l’identifiant de transaction, le champ de réponse, le code de réponse et le temps d’aller-retour observé. L’identifiant aide à rapprocher les messages dans les protocoles qui l’utilisent, mais ne suffit pas à lui seul si plusieurs requêtes se chevauchent ou si la capture est partielle.

Quelques codes courants :

- `NOERROR` : aucune erreur DNS protocolaire indiquée ; cela ne garantit pas que le nom existe ni que l’application fonctionnera.
- `NXDOMAIN` : le nom demandé n’existe pas selon la réponse reçue.
- `SERVFAIL` : le serveur n’a pas pu traiter la requête comme demandé.
- `REFUSED` : le serveur refuse de traiter la requête, souvent en raison d’une politique.
- `FORMERR` : la requête est considérée comme mal formée.

Une réponse `NOERROR` peut ne contenir aucun enregistrement demandé (NODATA). Une réponse DNS avec un code d’erreur n’est pas nécessairement la cause primaire du problème applicatif ; vérifie les résolveurs, le suffixe DNS, le cache et le nom exact demandé.

### 5.2 Délais DNS et retransmissions

Pour estimer le délai d’une transaction, compare l’heure de la requête à celle de la réponse correspondante. Vérifie les requêtes réémises, le serveur de destination, UDP versus TCP et les réponses provenant d’un résolveur différent. Un délai observé sur le client peut inclure une attente de réponse, des tentatives vers plusieurs serveurs ou une logique applicative qui ne se voit pas dans cette seule capture.

UDP est fréquent pour les requêtes DNS classiques, mais DNS peut également utiliser TCP, notamment dans certains cas de réponse tronquée, de transfert de zone ou d’autres conditions prévues par le protocole. Ne considère donc pas le trafic DNS/TCP comme forcément anormal. Dans les environnements modernes, DNS over TLS (DoT) et DNS over HTTPS (DoH) peuvent chiffrer la conversation DNS ; le contenu peut alors ne pas apparaître comme des messages DNS traditionnels sans données de déchiffrement ou autre source de visibilité autorisée.

### 5.3 Cache et point de capture

Si aucune requête n’apparaît lorsque l’application ouvre un nom, le résultat peut provenir du cache du système, du navigateur ou d’un résolveur local. L’absence de requête dans une courte capture ne prouve pas que l’application n’a pas demandé de résolution à un moment antérieur. Compare un essai avec cache chaud et, si c’est approprié dans le labo, un essai contrôlé après vidage du cache selon les pratiques du système concerné.

## 6. HTTP, TLS et QUIC : ce que l’on peut réellement lire

### 6.1 HTTP en clair et HTTPS

Sur une connexion HTTP non chiffrée, une capture peut exposer les méthodes, chemins, en-têtes et parfois le contenu. Cela aide à identifier des redirections, réponses d’erreur ou délais applicatifs, mais cette visibilité est aussi un risque pour la confidentialité. Ne capture pas de données de comptes réels ou de sessions personnelles pour t’exercer.

HTTPS protège HTTP avec TLS. Sans déchiffrement autorisé, Wireshark peut encore fournir des informations sur le transport, la négociation TLS et la chronologie, mais le chemin HTTP et son contenu sont généralement chiffrés. Le SNI peut être visible dans certains cas, mais les mécanismes modernes comme ECH peuvent masquer des informations de nom ; les versions, extensions et paramètres de connexion modifient ce qui est observable.

### 6.2 Lire la négociation TLS

Selon la version TLS et les extensions, tu peux voir un ClientHello, un ServerHello et d’autres messages de handshake. Avec TLS 1.3, une grande partie de la négociation après ServerHello est chiffrée. La présence de TLS indique qu’un échange de protocole de sécurité est en cours, pas que le certificat est nécessairement valide pour l’application ou que l’échange applicatif a réussi.

Pour diagnostiquer un problème TLS, relève les messages visibles, alertes éventuelles, versions proposées/négociées et temps d’attente. Corrobore ces éléments avec les journaux du client/serveur et les erreurs présentées à l’utilisateur. Des middleboxes, des politiques de certificats, l’horloge du système et les suites cryptographiques peuvent aussi jouer un rôle.

### 6.3 Déchiffrement autorisé à l’aide de secrets de session

Pour une application dont tu contrôles le client, certaines implémentations permettent d’enregistrer des secrets de session dans un fichier de clés (par exemple via une variable d’environnement prise en charge par le navigateur ou le runtime). Wireshark peut ensuite utiliser ce fichier lorsque le protocole et les secrets permettent le déchiffrement. La méthode exacte dépend de l’application, de la version et de la bibliothèque TLS ; consulte la documentation actuelle de l’outil concerné.

Un fichier de secrets de session est très sensible : il peut rendre lisible le contenu de connexions capturées correspondantes. Stocke-le séparément, limite son accès et détruis-le selon les règles du laboratoire. N’essaie pas de contourner le chiffrement d’utilisateurs ou de services auxquels tu n’es pas autorisé à accéder.

### 6.4 QUIC et HTTP/3

QUIC transporte plusieurs flux au-dessus d’UDP et intègre des mécanismes de sécurité. Le trafic HTTP/3 ne ressemble donc pas simplement à une conversation TCP/443 classique. Le port UDP 443 est courant mais n’est pas une preuve absolue de QUIC ou de HTTP/3. Wireshark peut décoder une partie des métadonnées et, dans les conditions adéquates, davantage de contenu avec les secrets fournis par une session autorisée.

Quand le navigateur utilise QUIC mais que tu filtres seulement `tcp.port == 443`, tu risques de manquer la connexion pertinente. Commence par le protocole ou l’adresse, observe UDP, puis affine. Certains environnements font un repli vers TCP/TLS si QUIC échoue ; cette bascule peut être utile pour expliquer des différences de comportement, mais elle doit être observée et non présumée.

### Schéma 4 — Décider ce que le chiffrement permet d’observer

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Schéma comparant HTTP en clair et HTTPS/TLS : certains champs applicatifs sont visibles en HTTP ; en HTTPS, le transport et une partie du handshake restent visibles mais le contenu est chiffré sauf déchiffrement autorisé par secrets de session."><defs><marker id="wsm4a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker></defs><style>.t{font:600 15px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:12px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.flow{stroke:#66d9ff;stroke-width:2.5;fill:none;stroke-dasharray:8 7;animation:wsmiDash 2s linear infinite}.plain{stroke:#72e4a5;stroke-width:2;fill:none}.enc{stroke:#ffc46b;stroke-width:2;fill:none;stroke-dasharray:6 4}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="28" y="30" width="406" height="256" rx="12" fill="#101d2b" stroke="#72e4a5" stroke-width="2"/><text x="231" y="58" class="t">HTTP non chiffré</text><rect x="56" y="86" width="350" height="68" rx="8" fill="#16382e" stroke="#72e4a5"/><text x="231" y="111" class="t">Transport + contenu</text><text x="231" y="132" class="s">Méthode, chemin, en-têtes, corps (si présents)</text><path d="M231 154V184" class="plain"/><rect x="56" y="188" width="350" height="67" rx="8" fill="#172b43" stroke="#66d9ff"/><text x="231" y="214" class="t">Wireshark peut décoder</text><text x="231" y="235" class="s">mais la capture expose potentiellement des données</text><rect x="466" y="30" width="406" height="256" rx="12" fill="#101d2b" stroke="#ffc46b" stroke-width="2"/><text x="669" y="58" class="t">HTTPS / TLS (sans secrets)</text><rect x="494" y="86" width="350" height="68" rx="8" fill="#332b19" stroke="#ffc46b"/><text x="669" y="111" class="t">Transport + métadonnées</text><text x="669" y="132" class="s">IP/ports, temps, tailles, messages TLS visibles</text><path d="M669 154V184" class="flow"/><rect x="494" y="188" width="350" height="67" rx="8" fill="#2b2540" stroke="#c1a4ff"/><text x="669" y="214" class="t">Contenu applicatif chiffré</text><text x="669" y="235" class="s">Secrets de session autorisés requis pour déchiffrer</text><text x="450" y="313" class="s">Visibilité exacte selon protocole, version, extensions et point de capture.</text></svg></div>

## 7. Comparer les temps et analyser les performances

### 7.1 Temps absolu et temps relatif

Wireshark peut afficher l’heure réelle ou le temps relatif depuis le premier paquet. Le temps relatif est souvent plus commode pour comparer les étapes d’un handshake ou le délai entre une requête et sa réponse. Avant d’interpréter une différence de temps entre plusieurs captures, vérifie que leurs horloges sont synchronisées ou que tu disposes d’un événement commun pour les aligner.

Les horodatages des captures ne sont pas toujours parfaitement représentatifs du moment physique sur le fil : charge système, buffer de capture, horloge de l’interface et agrégation matérielle peuvent introduire des écarts. Pour des mesures très fines, considère le matériel de capture, l’horodatage matériel et la précision des horloges.

### 7.2 Time delta et delta de requête/réponse

`frame.time_delta` représente le temps écoulé depuis la trame précédente dans le contexte de la capture, selon le mode d’affichage sélectionné. Ce n’est pas automatiquement le temps de réponse d’une application. Pour mesurer une transaction DNS, identifie sa requête et la réponse correspondante. Pour HTTP, il faut différencier le délai de handshake TCP, la négociation TLS, l’attente de la première réponse applicative et le transfert du corps.

### 7.3 Conversations, endpoints et hiérarchie des protocoles

Dans **Statistics**, les fenêtres **Conversations**, **Endpoints** et **Protocol Hierarchy** aident à réduire un grand fichier :

- **Conversations** met en évidence les échanges entre pairs, leur durée et les volumes selon les colonnes disponibles.
- **Endpoints** résume les hôtes et adresses observés.
- **Protocol Hierarchy** montre quels protocoles représentent le contenu capturé et aide à repérer une capture dominée par un trafic inattendu.

Ces vues présentent des statistiques de la capture, pas nécessairement celles de l’ensemble du réseau. Si le point de capture ne voit qu’une direction, si un filtre de capture a omis des données ou si un tunnel masque le contenu, les statistiques seront incomplètes.

### 7.4 Graphiques I/O et burst

Les graphiques d’entrée/sortie permettent de représenter le nombre ou le volume de paquets par intervalle. Ils aident à corréler une période de lenteur avec un pic de trafic ou un silence inhabituel. Un pic de paquets n’indique pas à lui seul une saturation ; il faut mettre le débit en relation avec la capacité du lien, la taille des paquets, les files d’attente et les compteurs d’interface.

Des microbursts peuvent être invisibles dans une moyenne calculée sur une longue période. Pour les diagnostiquer, il faut des intervalles fins ou des compteurs/mesures adaptés sur le réseau. Wireshark ne peut pas déduire avec certitude l’occupation d’une file d’attente du seul rythme de paquets observé sur un PC.

### 7.5 Flow Graph et Follow Stream

Le **Flow Graph** donne une vue chronologique des messages entre endpoints. Il est particulièrement utile pour un handshake, un échange requête/réponse ou une fermeture TCP. **Follow Stream** reconstruit les données que Wireshark peut associer à un flux. Ce sont des vues complémentaires : le graphe souligne l’ordre et les délais, tandis que la reconstruction aide à lire le contenu disponible. Elles ne reconstituent pas le contenu chiffré sans les secrets nécessaires et ne compensent pas les pertes de capture.

## 8. Raisonnement par scénarios de dépannage

### 8.1 Scénario A — Le site web est lent

Évite de commencer par « il y a des retransmissions, donc c’est la faute du réseau ». Décompose le temps :

1. La résolution de nom se termine-t-elle rapidement ou existe-t-il plusieurs requêtes/tentatives ?
2. Combien de temps sépare le SYN du SYN-ACK ?
3. Le handshake TCP s’achève-t-il ?
4. Si TLS est utilisé, le handshake est-il retardé ou interrompu ?
5. Quand commence la première réponse applicative visible ?
6. Le débit s’interrompt-il pendant le transfert ? Les fenêtres, ACK et retransmissions apportent-ils des indices ?

Un délai avant le SYN-ACK pourrait concerner le serveur ou le chemin aller/retour ; un délai après le handshake peut être lié à l’application, au chiffrement, à un proxy ou au transfert. Une capture client seule ne permet pas toujours de séparer ces causes. Compare avec les journaux côté serveur ou une capture côté serveur.

### 8.2 Scénario B — SYN sans SYN-ACK visible

Filtre :

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Sélectionne le flux, puis cherche les SYN répétés et tout paquet de réponse. Examine :

- si la cible et le port sont corrects ;
- si une connexion réussit vers d’autres destinations ;
- si l’IP/port sont transformés par NAT ;
- si la capture côté serveur voit arriver le SYN ;
- si le serveur émet un SYN-ACK, un RST ou rien ;
- les compteurs de filtrage, ACL, pare-feu, route et interface.

**Interprétation prudente :** aucune réponse visible au client signifie que la réponse n’est pas présente dans cette capture, pas qu’aucune réponse n’a été émise dans tout le réseau. Deux captures simultanées aux extrémités peuvent réduire fortement l’ambiguïté.

### 8.3 Scénario C — Erreur DNS intermittente

Filtre `dns`, puis trie ou observe les requêtes d’un même nom. Vérifie le serveur questionné, les réponses `NXDOMAIN` ou `SERVFAIL`, les requêtes répétées, les délais et les éventuels échanges DNS/TCP. Si aucune requête n’apparaît, le cache ou un DNS chiffré peut expliquer l’absence de messages DNS visibles. Compare les résultats avec la résolution faite par les outils du système et les journaux du résolveur, en conservant le même nom et le même moment de test.

### 8.4 Scénario D — Transfert TCP qui semble bloqué

Examine `tcp.analysis.retransmission`, `tcp.analysis.duplicate_ack`, `tcp.analysis.zero_window` et les paquets autour de la période figée. Détermine qui n’envoie plus de nouvelles données et qui acquitte le dernier octet. Une fenêtre nulle côté récepteur suggère un problème de capacité de réception ou de consommation côté application. Des retransmissions répétées peuvent suggérer une perte ou un chemin problématique, mais il faut éliminer les artefacts de capture et le réordonnancement.

### 8.5 Scénario E — Paquets trop grands ou problème MTU

Un problème de MTU peut laisser passer les petits échanges et bloquer certains paquets. Sur IPv4, la découverte de MTU de chemin utilise notamment des mécanismes liés à la fragmentation et aux messages ICMP « fragmentation needed ». En IPv6, les routeurs n’effectuent pas la fragmentation en transit ; les messages ICMPv6 Packet Too Big sont importants. Si ces messages sont filtrés, certaines connexions peuvent sembler se figer sur les transferts de taille importante.

Une capture peut révéler des paquets volumineux, des retransmissions ou des messages ICMP associés, mais elle ne démontre pas à elle seule quel équipement bloque le paquet. Vérifie la MTU de chaque lien, les tunnels VPN, l’encapsulation et les politiques ICMP. N’assimile pas une trame Ethernet capturée plus grande à un dépassement MTU sans tenir compte du type d’interface, des en-têtes et de l’offload.

### 8.6 Scénario F — Deux captures ne correspondent pas

Avant de conclure à une perte entre A et B :

- confirme que les deux captures observent la même conversation et la bonne direction ;
- aligne l’heure ou recherche un identifiant de transaction, un tuple et des séquences communes ;
- vérifie les pertes dans les compteurs de capture ;
- prends en compte NAT, proxy, load balancer, tunnels et réécriture d’en-têtes ;
- vérifie les offloads et la manière dont les segments sont présentés aux interfaces.

Quand A contient un segment qui n’apparaît pas à B, ce résultat délimite une zone d’investigation. Il faut encore exclure le mauvais point de capture et les pertes locales de collecte avant d’accuser un lien ou un équipement.

### Schéma 5 — Diagnostic différentiel d’une connexion lente

<div class="ws-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 410" role="img" aria-label="Arbre de décision pour une connexion lente : vérifier DNS, handshake TCP, TLS/application et transfert ; chaque branche dirige vers les preuves à examiner sans conclure hâtivement à une cause unique."><defs><marker id="wsm5a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#66d9ff"/></marker></defs><style>.t{font:600 14px system-ui,sans-serif;fill:#eef5ff;text-anchor:middle}.s{font:11.5px system-ui,sans-serif;fill:#b9c8db;text-anchor:middle}.a{stroke:#66d9ff;stroke-width:2.2;fill:none;marker-end:url(#wsm5a)}.flow{stroke-dasharray:8 7;animation:wsmiDash 2s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style><rect x="300" y="18" width="300" height="52" rx="10" fill="#172b43" stroke="#66d9ff" stroke-width="2"/><text x="450" y="40" class="t">La connexion est lente</text><text x="450" y="57" class="s">Définir les étapes et leurs durées</text><path d="M450 70V95H150V118" class="a flow"/><path d="M450 95V118" class="a flow"/><path d="M450 95H750V118" class="a flow"/><rect x="32" y="122" width="236" height="86" rx="10" fill="#332b19" stroke="#ffc46b" stroke-width="2"/><text x="150" y="145" class="t">DNS lent ?</text><text x="150" y="165" class="s">Req/réponse, délais, code</text><text x="150" y="183" class="s">Cache et résolveur</text><rect x="332" y="122" width="236" height="86" rx="10" fill="#142d45" stroke="#66d9ff" stroke-width="2"/><text x="450" y="145" class="t">Handshake TCP lent ?</text><text x="450" y="165" class="s">SYN/SYN-ACK, RST, retries</text><text x="450" y="183" class="s">Point client et serveur</text><rect x="632" y="122" width="236" height="86" rx="10" fill="#2b2540" stroke="#c1a4ff" stroke-width="2"/><text x="750" y="145" class="t">TCP rapide ?</text><text x="750" y="165" class="s">Examiner TLS et application</text><text x="750" y="183" class="s">Temps de première réponse</text><path d="M150 208V237" class="a flow"/><path d="M450 208V237" class="a flow"/><path d="M750 208V237" class="a flow"/><rect x="32" y="241" width="236" height="72" rx="10" fill="#101d2b" stroke="#ffc46b"/><text x="150" y="263" class="t">Cause à investiguer</text><text x="150" y="283" class="s">DNS, cache, chemin, politique</text><text x="150" y="299" class="s">Confirmer côté résolveur</text><rect x="332" y="241" width="236" height="72" rx="10" fill="#101d2b" stroke="#66d9ff"/><text x="450" y="263" class="t">Localiser l'aller/retour</text><text x="450" y="283" class="s">Capture aux deux extrémités</text><text x="450" y="299" class="s">Routes, ACL, service à l'écoute</text><rect x="632" y="241" width="236" height="72" rx="10" fill="#101d2b" stroke="#c1a4ff"/><text x="750" y="263" class="t">Transfert / application</text><text x="750" y="283" class="s">Fenêtre, retransmission, burst</text><text x="750" y="299" class="s">Logs et mesures côté serveur</text><path d="M150 313V342H450V360" class="a"/><path d="M450 313V360" class="a"/><path d="M750 313V342H450" class="a"/><rect x="220" y="364" width="460" height="34" rx="8" fill="#16382e" stroke="#72e4a5"/><text x="450" y="386" class="t">Conclusion : preuves observées + limites + prochaine vérification</text></svg></div>

## 9. Outils statistiques et analyse répétable

### 9.1 Expert Information : indice, pas verdict

La fenêtre **Expert Information** regroupe des événements relevés par les dissectors, comme retransmissions, erreurs de décodage ou anomalies de protocole. La sévérité et le libellé ne donnent pas toujours la cause racine. Une anomalie peut aussi être un effet du point de capture, d’un offload ou d’une collecte incomplète. Reviens toujours aux paquets concernés et à leurs voisins temporels.

### 9.2 Conversations et comparaison directionnelle

Une conversation peut être évaluée par nombre de paquets, nombre d’octets, durée et volume dans chaque direction lorsqu’il est disponible. Un écart entre les volumes montants et descendants peut être normal selon l’application. Pour l’interpréter, identifie le protocole, les rôles client/serveur, les retransmissions et le point de capture. Les totaux ne sont pas nécessairement des octets « sur le fil » si les données ont été capturées avant ou après certains traitements matériels.

### 9.3 Préserver les conditions du test

Pour pouvoir reproduire une enquête, note :

- date/heure et fuseau utilisés ;
- version de Wireshark et système d’exploitation ;
- interface et point de capture ;
- filtres de capture éventuels ;
- commande/action qui reproduit le symptôme ;
- adresses/ports utiles, masqués dans la note si sensibles ;
- numéro de flux ou de paquet repère ;
- conclusion et degré de confiance ;
- limites connues (capture unidirectionnelle, perte signalée, chiffrement, NAT, données incomplètes).

C’est particulièrement important quand un collègue doit refaire le test ou lorsque tu compares un « avant » et un « après » d’un changement réseau.

## 10. Utiliser TShark pour analyser sans interface graphique

TShark est la version en ligne de commande de l’analyseur de protocoles Wireshark. Il sait lire une capture, afficher les résumés et appliquer des filtres d’affichage. Sa syntaxe de filtre d’affichage est la même famille que celle de Wireshark, tandis que le filtre de capture `-f` utilise la syntaxe de capture, distincte.

### 10.1 Lire une capture existante

```bash
# Afficher un résumé des paquets d'un fichier
 tshark -r essai.pcapng

# Afficher seulement les paquets correspondant au filtre d'affichage
 tshark -r essai.pcapng -Y 'dns'

# Afficher une vue compacte pour TCP et quelques champs utiles
 tshark -r essai.pcapng -Y 'tcp' -T fields \
  -e frame.number -e frame.time_relative \
  -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport \
  -e tcp.stream -e tcp.len
```

Les exemples utilisent un fichier local fictif `essai.pcapng`. Remplace le nom par celui de ton laboratoire et teste d’abord sans exporter de champs sensibles. Les options TShark évoluent ; vérifie `tshark --help` et le manuel livré avec ta version.

### 10.2 Capture avec filtre BPF

```bash
# Exemple conceptuel : interface et filtre de capture à adapter
 tshark -i 1 -f 'tcp port 443' -w session-test.pcapng
```

Le nom ou numéro d’interface varie selon le système ; liste d’abord les interfaces avec `tshark -D`. La commande démarre une collecte live : lance-la seulement avec les permissions nécessaires et sur un réseau autorisé. Arrête la capture après la reproduction du problème afin de limiter la collecte de données privées.

### 10.3 Statistiques via TShark

TShark peut calculer des statistiques protocolaires avec ses options dédiées, souvent combinées avec `-q` pour supprimer le résumé de chaque paquet. Consulte le manuel pour les options `-z` disponibles dans ta version. Pour des automatisations durables, vérifie la version de TShark, les champs utilisés et la sortie attendue ; ne traite pas un format de sortie de console comme une API immuable.

### 10.4 Intégrer les résultats dans un rapport

Pour un rapport technique, exporte seulement les champs nécessaires. Si tu utilises CSV/JSON, définis les noms de champs, leur type et la manière de gérer les valeurs manquantes. Ajoute le filtre exact et la commande utilisée. Un graphique ou un tableau sans la méthode de sélection peut induire en erreur, surtout si la capture contenait un filtre de capture ou des pertes.

## 11. Hygiène, confidentialité et conservation des captures

Une capture PCAPNG peut être plus sensible qu’une capture d’écran : elle contient des métadonnées et, parfois, le contenu complet des communications. Avant de partager un fichier :

1. Ouvre le fichier et vérifie les protocoles et les données applicatives visibles.
2. Retire ou remplace les informations d’identification, adresses et noms internes si elles ne sont pas nécessaires.
3. Préfère des extraits ciblés ou un tableau de champs à une capture intégrale.
4. Si une anonymisation est nécessaire, travaille sur une copie et vérifie les résultats après transformation.
5. Stocke les fichiers dans un emplacement protégé, limite la durée de conservation et supprime les copies inutiles.
6. Ne partage jamais un fichier de secrets TLS de session avec une capture, sauf dans un environnement strictement contrôlé où cela est indispensable et autorisé.

L’export de paquets sélectionnés n’anonymise pas automatiquement toutes les données. Le suivi de flux peut présenter une partie de contenu lisible, mais il faut toujours valider que les secrets, identifiants et informations personnelles ont été retirés.

## 12. Atelier guidé — Comprendre une connexion web qui échoue

### Objectif

Produire une conclusion justifiée sur une tentative de connexion dans un environnement contrôlé. L’exercice n’exige pas d’accès à un site tiers. Utilise un service local de laboratoire, une machine virtuelle ou une capture fournie par un formateur.

### Préparation

- Choisis un client et un serveur dont tu contrôles les deux côtés.
- Note les adresses, le port de service attendu et le chemin réseau.
- Démarre une capture au client et, si possible, une capture simultanée au serveur.
- Reproduis une tentative réussie, puis une tentative en échec configurée dans le laboratoire.
- Enregistre les captures avec des noms et des heures distincts.

### Étape 1 — Identifier le flux

Applique `tcp` ou filtre par IP/port. Repère le SYN initial et note le `tcp.stream`. Utilise Follow TCP Stream ou Flow Graph pour reconstruire la chronologie. S’il n’y a aucun SYN, confirme la bonne interface et le bon moment de capture.

### Étape 2 — Interpréter le handshake

- **SYN, SYN-ACK, ACK :** handshake classique observé. Continue vers les données et éventuels messages TLS/application.
- **SYN et RST :** une extrémité visible rejette ou réinitialise la tentative. Identifie l’émetteur du RST et vérifie le service et les politiques.
- **SYN répétés sans réponse visible :** la réponse est absente du point de capture. Compare avec le serveur et le réseau intermédiaire.
- **Capture commençant après SYN :** les données ne suffisent pas à juger l’établissement initial. Refais une capture complète.

### Étape 3 — Si TLS est utilisé

Repère les messages de handshake visibles, le temps entre eux et toute alerte décodée. Ne conclus pas qu’une connexion est valide simplement parce que TCP s’est établi. Examine les journaux applicatifs, les certificats et l’heure système si le client retourne une erreur TLS.

### Étape 4 — Si la connexion s’établit mais reste lente

Filtre les événements d’analyse TCP. Évalue les délais entre segments, les retransmissions, les ACK dupliqués et les fenêtres. Repère la direction affectée et vérifie si l’application a effectivement envoyé des données. Compare avec les métriques du serveur et, lorsque possible, une capture indépendante.

### Modèle de conclusion

```text
Symptôme observé :
Périmètre et point(s) de capture :
Paquets/flux de référence :
Chronologie mesurée :
Indices principaux :
Hypothèse la mieux étayée :
Autres explications encore possibles :
Vérification suivante recommandée :
Limites de la capture :
```

Une bonne conclusion est précise sans être plus certaine que les preuves. Exemple : « Le client a émis trois SYN vers le port du serveur et aucun SYN-ACK n’est visible dans la capture client. La capture côté serveur est nécessaire pour déterminer si la requête atteint le serveur. » Cette conclusion est plus solide que « le pare-feu bloque le port » lorsque le pare-feu n’a pas été observé directement.

## 13. Exercices d’application

### Exercice 1 — Construire un filtre précis

Tu veux afficher le trafic TCP associé à `192.0.2.25` et repérer les retransmissions. Propose un filtre qui garde le trafic de cet hôte mais ne montre que les paquets marqués comme retransmissions.

**Correction :**

```text
ip.addr == 192.0.2.25 && tcp.analysis.retransmission
```

Ce filtre montre les paquets de retransmission identifiés dans les conversations TCP de cet hôte. Il ne prouve pas que chaque événement signalé correspond à une perte physique ; ouvre le flux et examine les paquets voisins.

### Exercice 2 — Distinguer SYN sans réponse de RST

Dans une capture, le client envoie trois SYN mais ne reçoit aucune réponse visible. Dans une autre, le client reçoit un RST presque immédiatement. Lequel permet de conclure que la destination a répondu au niveau TCP ?

**Correction :** le RST est une réponse TCP observable. L’absence de réponse visible ne permet pas de dire si le serveur est éteint, si un filtre rejette silencieusement la tentative ou si la réponse a été perdue ou capturée ailleurs. Le RST peut être émis par l’hôte cible ou par un équipement intermédiaire ; l’adresse source seule n’est pas toujours une preuve suffisante de son origine réelle.

### Exercice 3 — Un code DNS `NXDOMAIN`

La requête reçoit `NXDOMAIN`. Le réseau est-il nécessairement défaillant ?

**Correction :** non. Le serveur indique que le nom demandé n’existe pas selon sa vue DNS. Vérifie le nom exact, le suffixe, le domaine, le résolveur interrogé et le contexte. Une faute de frappe, une zone absente ou un split DNS mal configuré peuvent être à l’origine du résultat.

### Exercice 4 — Des retransmissions pendant une vidéo

Wireshark identifie plusieurs retransmissions, mais l’utilisateur ne constate aucun gel. Peut-on affirmer que ces retransmissions provoquent une panne ?

**Correction :** non. Évalue leur nombre, leur timing, le flux affecté, les délais et l’impact applicatif. Une capture peut révéler une retransmission récupérée rapidement sans symptôme perceptible. La sévérité se juge en contexte, pas uniquement d’après la couleur d’une ligne.

### Exercice 5 — HTTPS et contenu absent

Le navigateur utilise TCP/443, mais le chemin HTTP n’est pas visible. Est-ce un défaut de Wireshark ?

**Correction :** pas nécessairement. Le contenu HTTPS est chiffré. Wireshark peut analyser le transport et une partie de la négociation TLS, tandis que le contenu applicatif exige un déchiffrement autorisé avec les secrets de session adéquats ou une instrumentation différente. Le port seul ne garantit pas non plus que l’application utilise un protocole donné.

### Exercice 6 — Comparer deux captures

Le client voit un paquet que la capture d’un switch ne montre pas. Cite trois explications avant d’accuser la fabric.

**Correction possible :** port miroir mal configuré ou saturé, point/côté de capture différent, filtres de capture divergents, interface incorrecte, pertes locales de capture, NAT ou tunnel modifiant les champs visibles, horodatage désaligné, ou offload modifiant la représentation des segments. Il faut corréler par séquence et chronologie avant de localiser la perte.

## 14. Quiz de validation

1. Quelle est la différence pratique entre un filtre de capture et un filtre d’affichage ?
2. Pourquoi un `tcp.analysis.retransmission` ne prouve-t-il pas à lui seul une perte de lien ?
3. Que signifie généralement un SYN répété sans SYN-ACK visible ?
4. Pourquoi le mode promiscuité d’un PC ne permet-il pas de voir automatiquement tous les paquets d’un réseau commuté ?
5. Quel est l’intérêt de `tcp.stream eq N` ?
6. Quelle précaution prendre avec les fichiers de secrets TLS ?
7. Pourquoi `frame.time_delta` n’est-il pas forcément le temps de réponse d’une application ?
8. Quelles observations complémentaires sont utiles pour diagnostiquer un problème de MTU ?
9. Que signifie généralement le code DNS `NXDOMAIN` ?
10. Quel rôle joue une capture effectuée côté serveur lorsque le client ne voit pas de réponse ?

### Corrigé du quiz

1. Le filtre de capture limite les paquets enregistrés ; le filtre d’affichage masque temporairement des paquets d’un fichier déjà capturé.
2. Wireshark applique des heuristiques et la capture peut refléter du réordonnancement, des ACK perdus, un point d’observation partiel ou des artefacts d’offload.
3. La réponse attendue n’est pas visible à ce point de capture ; la cause reste à déterminer.
4. Un switch transmet normalement le trafic unicast vers les ports concernés ; une carte réseau ne reçoit pas les échanges des autres ports sans mécanisme d’observation adapté.
5. Il isole les paquets du flux TCP indexé dans ce fichier, utile pour suivre une seule conversation.
6. Les protéger comme des secrets, car ils peuvent permettre de déchiffrer les données de sessions correspondantes.
7. Il mesure l’intervalle depuis la trame précédente, et non nécessairement le délai d’une transaction applicative identifiée.
8. Vérifier les tailles de paquets, messages ICMP liés au PMTUD, MTU des interfaces et tunnels, retransmissions et capture aux deux extrémités.
9. Le nom demandé n’existe pas selon la réponse du résolveur.
10. Elle aide à savoir si la requête atteint le serveur et si une réponse y est générée, ce qui réduit les hypothèses liées au chemin retour.

## 15. Bonnes pratiques avant de clôturer un incident

- **Séparer observation et interprétation.** « Trois SYN capturés » est une observation ; « pare-feu responsable » est une hypothèse à tester.
- **Éviter de capturer trop longtemps.** Une reproduction courte réduit le volume et les données sensibles.
- **Répéter le scénario.** Une seule occurrence peut être affectée par un cache, une route différente ou une condition transitoire.
- **Comparer les deux extrémités si possible.** Cela aide à localiser où les observations divergent.
- **Conserver les filtres exacts.** Un rapport doit être reproductible.
- **Ne pas s’appuyer uniquement sur les couleurs.** Les couleurs sont des règles visuelles configurables, pas des verdicts de panne.
- **Consigner les limites.** Capture partielle, pertes, offload, chiffrement ou horloges non synchronisées peuvent modifier la conclusion.
- **Nettoyer les livrables.** Vérifier que les extraits, exports et captures partagés ne révèlent pas d’identifiants, tokens ou données privées.

## 16. Glossaire intermédiaire

- **BPF/libpcap :** mécanisme et syntaxe souvent employés pour filtrer les paquets au moment de la capture.
- **Dissector :** module qui interprète les octets capturés selon un protocole.
- **Display filter :** filtre qui change les paquets visibles, sans retirer les autres du fichier.
- **Dup ACK :** acquittement TCP répétant le prochain octet attendu.
- **ECN :** mécanisme de notification explicite de congestion, lorsqu’il est pris en charge et utilisé.
- **Flow Graph :** représentation chronologique des échanges entre endpoints dans Wireshark.
- **Handshake :** échange de négociation préalable à une communication, comme TCP ou TLS.
- **MSS :** taille maximale de données TCP annoncée pour un segment, hors en-têtes, dans le contexte de la connexion.
- **MTU :** taille maximale d’un paquet de couche réseau transportable sur une interface ou un lien sans fragmentation à ce niveau.
- **Offload :** traitement effectué par la carte réseau au lieu du logiciel, susceptible d’influencer la représentation des paquets observés sur l’hôte.
- **PCAP/PCAPNG :** formats de fichiers de capture réseau.
- **PMTUD :** découverte de la MTU de chemin, qui s’appuie sur des retours appropriés selon IPv4/IPv6 et le réseau traversé.
- **RTO :** temporisateur de retransmission TCP.
- **SPAN/TAP :** mécanismes pour observer le trafic réseau depuis un point distinct du poste analysé.
- **TShark :** outil d’analyse de protocoles en ligne de commande fourni avec Wireshark.
- **Tuple de flux :** combinaison d’adresses IP, ports et protocole utile à l’identification d’une conversation.
- **Zero Window :** annonce TCP indiquant qu’un récepteur n’accepte temporairement plus de nouvelles données.

## 17. Références officielles

Les menus, options et champs précis peuvent différer selon la version installée. Pour une analyse reproductible, consulte la documentation correspondant à ta version :

- [Wireshark User’s Guide](https://www.wireshark.org/docs/wsug_html/) — fonctionnement général, fenêtres de statistiques, filtres et analyse des flux.
- [Filtering Packets While Viewing](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkDisplayFilterSection.html) — différence et usage des filtres d’affichage.
- [The Analyze Menu](https://www.wireshark.org/docs/wsug_html_chunked/ChUseAnalyzeMenuSection.html) — Follow Stream, filtres de conversation et Expert Information.
- [TShark Manual](https://www.wireshark.org/docs/man-pages/tshark.html) — options de capture, lecture, export et filtres en ligne de commande.
- [TCP Display Filter Reference](https://www.wireshark.org/docs/dfref/t/tcp.html) — champs et indicateurs TCP disponibles.
- [Site officiel Wireshark](https://www.wireshark.org/) — téléchargements et ressources du projet.

---

## À retenir

L’analyse intermédiaire commence lorsqu’on cesse de traiter la capture comme une collection de lignes et qu’on l’utilise comme une chronologie de preuves. Le meilleur filtre dépend de la question ; le meilleur point de capture dépend de ce qu’il faut confirmer ; et la meilleure conclusion ne dépasse jamais les éléments réellement observés. Utilise les filtres pour isoler, les statistiques pour orienter, les détails protocole pour expliquer et une seconde observation indépendante pour renforcer le diagnostic.
