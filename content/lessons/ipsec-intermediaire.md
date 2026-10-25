# VPN IPsec (IKEv2, ESP) — Intermédiaire

**Niveau :** INTERMÉDIAIRE

À ce niveau, on suppose que les notions de base sont déjà acquises : un VPN IPsec protège des paquets IP, IKEv2 négocie les paramètres et ESP protège les données. L’objectif est maintenant de comprendre pourquoi deux équipements qui semblent correctement configurés peuvent ne pas former un tunnel stable, comment analyser les associations de sécurité (SA), et comment déployer une solution exploitable au-delà d’un simple laboratoire.

Le cours progresse depuis les bases du niveau Débutant vers les décisions de conception : correspondance des propositions cryptographiques, sélecteurs de trafic, routage, NAT Traversal, MTU/MSS, renouvellement des clés, redondance et analyse des compteurs. Les exemples Cisco IOS/IOS XE sont des modèles de laboratoire : les commandes, les capacités et la syntaxe varient selon la plateforme et la version. Toujours vérifier la documentation de l’équipement et tester avant une mise en production.

> **Analogie** : imagine deux bâtiments avec un sas sécurisé. IKEv2 est le protocole par lequel les responsables du sas vérifient l’identité, choisissent les règles et remettent les clés. ESP est le dispositif qui protège réellement les colis pendant leur transport. Un sas ouvert ne prouve pas que le bon colis est autorisé, et un colis chiffré ne prouve pas qu’il prend le bon chemin.


## 1. La théorie et les algorithmes

## 1.1 Rappels utiles et objectifs de sécurité

IPsec est une suite de mécanismes opérant à la couche IP. Il peut fournir confidentialité, intégrité, authentification de l’origine des données et protection anti-rejeu selon les paramètres négociés. Il ne garantit pas à lui seul la disponibilité, l’innocuité d’un poste compromis, ni la sécurité des applications après déchiffrement.

| Élément | Rôle | À ne pas confondre avec |
|---|---|---|
| IKEv2 | Authentifier les pairs, négocier les algorithmes et gérer les SA | Le chiffrement de chaque paquet utilisateur |
| IKE SA | Canal protégé pour la gestion IKE | L’unique SA de données du tunnel |
| Child SA | Paramètres de protection du trafic IPsec | Un compte utilisateur ou une session applicative |
| ESP | Encapsulation et protection des paquets IP | Une solution de routage ou de filtrage complète |
| Sélecteurs TS_i / TS_r | Décrire les flux qui doivent être protégés | Les routes IP installées dans la table de routage |
| NAT-T | Encapsuler ESP dans UDP lorsqu’il faut traverser un NAT | Un chiffrement supplémentaire |
| DPD / liveness | Détecter qu’un pair ne répond plus | Une garantie de convergence immédiate |

Un VPN peut réussir la négociation IKE tout en ne transportant aucun trafic. Les causes courantes se situent alors dans les Child SA, les sélecteurs, le routage, les ACL, le NAT, les politiques de sécurité ou les hôtes eux-mêmes.

## 1.2 Architecture de référence

<style>
.ipx-wrap{max-width:100%;overflow-x:auto;margin:1.25rem 0 1.75rem;border:1px solid #3f3f46;border-radius:1rem;background:#111214;padding:.6rem}
.ipx-svg{display:block;width:100%;min-width:760px;height:auto}
.ipx-svg text{font-family:Inter,ui-sans-serif,system-ui,sans-serif;font-size:13px;fill:#e4e4e7}
.ipx-svg .muted{fill:#a1a1aa;font-size:11px}.ipx-svg .title{fill:#fafafa;font-size:15px;font-weight:700}.ipx-svg .site{fill:#18181b;stroke:#71717a;stroke-width:1.5}.ipx-svg .router{fill:#142b3a;stroke:#60a5fa;stroke-width:1.5}.ipx-svg .lan{fill:#14291e;stroke:#4ade80;stroke-width:1.5}.ipx-svg .tunnel{fill:none;stroke:#22d3ee;stroke-width:4;stroke-dasharray:9 9;animation:ipx-flow 1.6s linear infinite}.ipx-svg .plain{fill:none;stroke:#4ade80;stroke-width:3;stroke-dasharray:6 7;animation:ipx-flow 1.1s linear infinite}.ipx-svg .packet{fill:#67e8f9;animation:ipx-packet 4s ease-in-out infinite}.ipx-svg .packet2{animation-delay:1.5s}.ipx-svg .pulse{animation:ipx-pulse 2.1s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.ipx-svg .frame{fill:#18181b;stroke:#52525b;stroke-width:1.3}.ipx-svg .good{fill:#4ade80}.ipx-svg .warn{fill:#fbbf24}.ipx-svg .bad{fill:#f87171}
@keyframes ipx-flow{to{stroke-dashoffset:-36}}
@keyframes ipx-packet{0%{transform:translateX(0);opacity:0}10%{opacity:1}85%{opacity:1}100%{transform:translateX(490px);opacity:0}}
@keyframes ipx-pulse{0%,100%{opacity:.65}50%{opacity:1;filter:brightness(1.4)}}
.ipx-callout{margin:.5rem 0 1.5rem;padding:.85rem 1rem;border-left:3px solid #22d3ee;background:#18181b;color:#d4d4d8;font-size:.92rem}
.ipx-svg:focus{outline:2px solid #22d3ee;outline-offset:2px}
@media(max-width:640px){.ipx-wrap{padding:.35rem}.ipx-svg{min-width:760px}}
@media(prefers-reduced-motion:reduce){.ipx-svg *, .ipx-wrap *{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style>

<div class="ipx-wrap" role="img" aria-label="Architecture VPN IPsec site-à-site : deux réseaux privés sont reliés par deux passerelles et un tunnel protégé sur Internet.">
<svg class="ipx-svg" viewBox="0 0 940 300" xmlns="http://www.w3.org/2000/svg">
  <rect class="site" x="18" y="45" width="260" height="215" rx="16"/><text class="title" x="148" y="70" text-anchor="middle">Site A</text>
  <rect class="lan" x="40" y="95" width="110" height="70" rx="10"/><text x="95" y="121" text-anchor="middle">LAN A</text><text class="muted" x="95" y="142" text-anchor="middle">10.10.0.0/16</text>
  <rect class="router" x="170" y="105" width="86" height="52" rx="10"/><text x="213" y="127" text-anchor="middle">GW A</text><text class="muted" x="213" y="144" text-anchor="middle">IKEv2</text>
  <path class="plain" d="M150 130 H170"/><path class="tunnel" d="M256 131 C330 131 340 131 405 131 S565 131 644 131"/>
  <rect class="site" x="665" y="45" width="257" height="215" rx="16"/><text class="title" x="793" y="70" text-anchor="middle">Site B</text>
  <rect class="router" x="683" y="105" width="86" height="52" rx="10"/><text x="726" y="127" text-anchor="middle">GW B</text><text class="muted" x="726" y="144" text-anchor="middle">IKEv2</text>
  <rect class="lan" x="791" y="95" width="110" height="70" rx="10"/><text x="846" y="121" text-anchor="middle">LAN B</text><text class="muted" x="846" y="142" text-anchor="middle">10.20.0.0/16</text><path class="plain" d="M769 130 H791"/>
  <rect class="frame" x="374" y="88" width="180" height="83" rx="12"/><text class="title" x="464" y="111" text-anchor="middle">Internet</text><text class="muted" x="464" y="132" text-anchor="middle">ESP / NAT-T</text><text class="muted" x="464" y="149" text-anchor="middle">paquets protégés</text>
  <circle class="packet" cx="278" cy="131" r="6"/><circle class="packet packet2" cx="278" cy="131" r="6"/>
  <text class="muted" x="470" y="204" text-anchor="middle">Les routes désignent le chemin ; les SA protègent les paquets.</text><text class="muted" x="470" y="225" text-anchor="middle">Le tunnel ne remplace ni les ACL ni le contrôle des hôtes.</text>
</svg></div>

Le tunnel IPsec protège les paquets sélectionnés entre les extrémités qui possèdent les clés et les paramètres négociés. Dans un VPN site-à-site en mode tunnel, la passerelle encapsule généralement le paquet IP original dans un nouveau paquet IP externe. Les adresses externes servent à acheminer le paquet entre passerelles ; les adresses internes correspondent aux réseaux des sites.

> **Piège :** un tunnel affiché « UP » peut n’être que la preuve d’une négociation de contrôle réussie. Vérifie les compteurs ESP, les routes, les sélecteurs, les règles de pare-feu et la connectivité applicative dans les deux sens.

## 1.3 Échanges IKEv2 : IKE_SA_INIT et IKE_AUTH

IKEv2 utilise des échanges structurés. Pour une mise en place initiale typique, on observe d’abord IKE_SA_INIT, puis IKE_AUTH. La première phase négocie les propositions IKE, échange les valeurs Diffie–Hellman et les nonces, et détecte notamment une éventuelle présence de NAT. L’échange IKE_AUTH protège l’authentification des pairs, confirme les identités et négocie les paramètres de la première Child SA.

<div class="ipx-wrap" role="img" aria-label="Séquence IKEv2 en deux étapes : IKE SA initiale puis authentification et création d’une Child SA.">
<svg class="ipx-svg" viewBox="0 0 940 330" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="26" text-anchor="middle">Négociation IKEv2</text>
  <rect class="router" x="70" y="48" width="190" height="48" rx="10"/><text x="165" y="77" text-anchor="middle">Initiateur</text>
  <rect class="router" x="680" y="48" width="190" height="48" rx="10"/><text x="775" y="77" text-anchor="middle">Répondeur</text>
  <path class="tunnel" d="M260 115 H680"/><polygon points="670,108 684,115 670,122" fill="#22d3ee"/><text x="470" y="106" text-anchor="middle">IKE_SA_INIT → ← réponse</text>
  <rect class="frame pulse" x="285" y="133" width="370" height="58" rx="10"/><text class="title" x="470" y="156" text-anchor="middle">Négocier et dériver les clés IKE</text><text class="muted" x="470" y="176" text-anchor="middle">propositions · DH · nonces · détection NAT</text>
  <path class="tunnel" d="M260 216 H680"/><polygon points="670,209 684,216 670,223" fill="#22d3ee"/><text x="470" y="207" text-anchor="middle">IKE_AUTH → ← réponse</text>
  <rect class="lan pulse" x="285" y="234" width="370" height="58" rx="10"/><text class="title" x="470" y="257" text-anchor="middle">Authentification et Child SA</text><text class="muted" x="470" y="277" text-anchor="middle">identités · certificats/PSK · sélecteurs · ESP</text>
  <text class="muted" x="470" y="318" text-anchor="middle">La négociation ne garantit pas à elle seule le transfert de données.</text>
</svg></div>

Les algorithmes doivent être compatibles sur les deux pairs et conformes aux politiques de sécurité de l’organisation. La liste proposée contient des choix possibles ; le pair distant doit en accepter un ensemble commun. Une erreur de proposition peut empêcher l’établissement de la SA avant même l’authentification. Une erreur de secret partagé ou de validation de certificat apparaît généralement plus tard, pendant IKE_AUTH.

### IKE SA et Child SA

Une IKE SA protège les échanges IKE entre pairs. Une Child SA concerne la protection du trafic IPsec. IKEv2 peut gérer plusieurs Child SA sous une même IKE SA. Dans les implémentations IPsec, la protection du trafic est souvent représentée par des SA distinctes pour chaque direction : une SA est unidirectionnelle, et les paramètres de sortie ne sont pas simplement l’inverse des paramètres d’entrée.

| Symptôme | Piste initiale | Vérification utile |
|---|---|---|
| Aucune IKE SA | Pair non joignable, UDP filtré, proposition incompatible | Connectivité publique, ports UDP 500/4500, logs IKE |
| IKE SA présente, aucune Child SA | Authentification, sélecteurs ou proposition ESP | Journaux IKE_AUTH, politiques et compteurs SA |
| Child SA présente, aucun paquet protégé | Aucune route vers les préfixes, trafic non sélectionné | Table de routage, TS, compteurs encapsulation/décapsulation |
| Paquets sortants uniquement | Trafic retour filtré, route asymétrique, SA distante absente | Compteurs des deux pairs et ACL du LAN |
| Fonctionne puis tombe | Rekey, expiration, changement d’adresse, NAT ou perte de keepalive | Journaux chronologiques et temps de vie des SA |

## 1.4 Proposition cryptographique et interopérabilité

Les propositions IKE et ESP sont distinctes. IKEv2 négocie les paramètres de la SA IKE ; ESP utilise ses propres transformations pour protéger les données. Deux équipements peuvent s’accorder sur IKE mais échouer sur ESP, par exemple si leurs propositions de chiffrement ou d’intégrité ne correspondent pas.

Les algorithmes modernes de chiffrement authentifié tels qu’AES-GCM combinent confidentialité et intégrité dans une seule primitive. Avec certains modes de chiffrement plus anciens comme AES-CBC, un mécanisme d’intégrité séparé est nécessaire. Ne mélange pas les exigences d’intégrité IKE et celles d’ESP : elles appartiennent à des négociations différentes.

**Conseils de conception :**

- Utilise IKEv2 au lieu d’IKEv1 pour les nouveaux déploiements, sauf exception explicitement justifiée par compatibilité.
- Privilégie des suites modernes approuvées par la politique de sécurité et supportées par les deux équipements ; vérifie les recommandations du fournisseur et les références IETF en vigueur.
- Évite les suites obsolètes et ne baisse pas la sécurité pour masquer un problème de compatibilité sans analyse de risque.
- Lorsque les pairs sont administrés par des organisations différentes, documente à l’avance la proposition commune, les identités attendues et le traitement de la rotation des clés.
- Avec des certificats, vérifie les noms d’identité, les dates de validité, la chaîne de confiance et la révocation selon le mécanisme prévu.

> **Danger :** ne copie pas une proposition faible simplement parce qu’un ancien équipement l’accepte. Il vaut mieux identifier la limite de la plateforme, proposer une mise à niveau ou documenter un compromis temporaire qu’affaiblir silencieusement la politique cryptographique.

## 1.5 ESP, numéros de séquence et anti-rejeu

ESP protège les paquets sélectionnés. Il ajoute des champs qui permettent d’identifier la SA, de suivre l’ordre des paquets et d’appliquer les transformations cryptographiques négociées. La protection anti-rejeu rejette généralement les paquets dupliqués ou trop anciens au regard d’une fenêtre de réception. Sur un réseau utilisant plusieurs chemins, de la réordonnance ou des tunnels multiples, les réglages et les compteurs anti-rejeu peuvent aider à expliquer des pertes apparemment aléatoires.

<div class="ipx-wrap" role="img" aria-label="Un paquet IP interne est protégé par ESP, puis encapsulé dans un paquet IP externe ; des champs ESP permettent de retrouver la SA et de contrôler la séquence.">
<svg class="ipx-svg" viewBox="0 0 940 270" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="25" text-anchor="middle">Vue conceptuelle d’un paquet en mode tunnel</text>
  <rect class="frame" x="30" y="62" width="185" height="82" rx="9"/><text class="title" x="122" y="86" text-anchor="middle">IP externe</text><text class="muted" x="122" y="106" text-anchor="middle">GW A → GW B</text><text class="muted" x="122" y="125" text-anchor="middle">routage Internet</text>
  <rect class="router pulse" x="230" y="62" width="120" height="82" rx="9"/><text class="title" x="290" y="85" text-anchor="middle">ESP</text><text class="muted" x="290" y="106" text-anchor="middle">SPI + séquence</text><text class="muted" x="290" y="125" text-anchor="middle">protection</text>
  <rect class="lan" x="365" y="62" width="250" height="82" rx="9"/><text class="title" x="490" y="86" text-anchor="middle">Paquet IP interne chiffré</text><text class="muted" x="490" y="106" text-anchor="middle">IP source/destination privées</text><text class="muted" x="490" y="125" text-anchor="middle">contenu protégé par ESP</text>
  <rect class="frame" x="630" y="62" width="280" height="82" rx="9"/><text class="title" x="770" y="86" text-anchor="middle">Contrôles à la réception</text><text class="muted" x="770" y="106" text-anchor="middle">SPI · intégrité · anti-rejeu</text><text class="muted" x="770" y="125" text-anchor="middle">déchiffrement si validé</text>
  <path class="tunnel" d="M215 103 H230 M350 103 H365 M615 103 H630"/><polygon points="223,97 232,103 223,109" fill="#22d3ee"/><polygon points="358,97 367,103 358,109" fill="#22d3ee"/><polygon points="623,97 632,103 623,109" fill="#22d3ee"/>
  <text x="470" y="183" text-anchor="middle">Le réseau intermédiaire voit les adresses externes et les métadonnées permises par l’encapsulation,</text><text x="470" y="203" text-anchor="middle">mais ne doit pas pouvoir lire le contenu chiffré ni le modifier sans détection.</text><text class="muted" x="470" y="238" text-anchor="middle">Schéma simplifié — l’ordre exact des champs dépend du mode et des transformations négociées.</text>
</svg></div>

Ne considère pas un compteur de paquets ESP comme une preuve que l’application distante répond. La SA peut recevoir et rejeter des paquets, ou protéger un autre flux que celui que l’on teste. Combine compteurs, capture côté LAN et tests applicatifs.

## 1.6 Sélecteurs de trafic : ne pas confondre routage et chiffrement

Les Traffic Selectors, souvent notés TS_i et TS_r, décrivent les adresses, protocoles et ports admissibles dans la Child SA. Les détails de représentation varient par implémentation. Le routage décide où un paquet doit aller ; la politique IPsec décide si ce paquet est protégé. Pour un VPN basé sur des politiques, le sélecteur correspond souvent à une ACL crypto. Pour un tunnel route-based/VTI, le trafic est généralement acheminé par l’interface virtuelle, mais les sélecteurs et les politiques de sécurité doivent toujours être cohérents avec la plateforme.

Exemple de plan d’adressage pour un laboratoire :

| Élément | Site A | Site B |
|---|---|---|
| LAN | `10.10.10.0/24` | `10.20.20.0/24` |
| Passerelle LAN | `10.10.10.1` | `10.20.20.1` |
| Adresse publique de laboratoire | `198.51.100.10` | `203.0.113.20` |
| Réseau de test entre hôtes | `10.10.10.10` | `10.20.20.20` |

Les plages `198.51.100.0/24` et `203.0.113.0/24` sont réservées à la documentation : elles ne doivent pas être copiées telles quelles pour une vraie connexion Internet. Remplace-les par les adresses de ton lab ou celles attribuées par l’opérateur.

Causes fréquentes de non-correspondance : masque incorrect, réseau oublié, préfixes inversés, sélecteurs trop larges ou trop étroits, sous-réseaux chevauchants, NAT appliqué avant la sélection IPsec, ou politique de l’autre pair qui ne permet pas la même plage. Certains équipements négocient un sous-ensemble proposé ; d’autres exigent une correspondance stricte. Lis les logs plutôt que de supposer un comportement universel.

> **Astuce :** pour chaque flux de test, écris explicitement la source, la destination, le protocole et le port attendus. Vérifie ensuite séparément la route, la règle de sécurité, la sélection IPsec et le chemin de retour.

## 1.7 NAT Traversal et ports UDP

IKEv2 utilise traditionnellement UDP 500 ; quand un NAT est détecté, le trafic IKE et ESP peut être transporté sur UDP 4500. ESP natif utilise le protocole IP numéro 50, ce qui n’est pas un port TCP/UDP. Cette distinction est essentielle sur un pare-feu : une règle qui n’autorise que « le port 50 » est mal formulée, tandis qu’une règle TCP/UDP 50 ne correspond pas à ESP natif.

<div class="ipx-wrap" role="img" aria-label="Le tunnel utilise UDP 500 pour IKE au départ ; si un NAT est détecté, ESP est encapsulé dans UDP 4500.">
<svg class="ipx-svg" viewBox="0 0 940 280" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="26" text-anchor="middle">NAT Traversal — chemin de contrôle et de données</text>
  <rect class="lan" x="25" y="64" width="160" height="64" rx="10"/><text class="title" x="105" y="89" text-anchor="middle">Pair A</text><text class="muted" x="105" y="109" text-anchor="middle">IKE initiateur</text>
  <rect class="frame" x="234" y="64" width="168" height="64" rx="10"/><text class="title" x="318" y="89" text-anchor="middle">Routeur NAT</text><text class="muted" x="318" y="109" text-anchor="middle">traduction d’adresse</text>
  <rect class="frame" x="538" y="64" width="160" height="64" rx="10"/><text class="title" x="618" y="89" text-anchor="middle">Internet</text><text class="muted" x="618" y="109" text-anchor="middle">réseau public</text>
  <rect class="lan" x="750" y="64" width="160" height="64" rx="10"/><text class="title" x="830" y="89" text-anchor="middle">Pair B</text><text class="muted" x="830" y="109" text-anchor="middle">IKE répondant</text>
  <path class="tunnel" d="M185 95 H234 M402 95 H538 M698 95 H750"/><polygon points="225,89 235,95 225,101" fill="#22d3ee"/><polygon points="529,89 539,95 529,101" fill="#22d3ee"/><polygon points="741,89 751,95 741,101" fill="#22d3ee"/>
  <rect class="router" x="86" y="163" width="318" height="74" rx="10"/><text class="title" x="245" y="188" text-anchor="middle">Début : IKE sur UDP 500</text><text class="muted" x="245" y="208" text-anchor="middle">IKE_SA_INIT détecte l’éventuel NAT</text><text class="muted" x="245" y="224" text-anchor="middle">authentification et négociation</text>
  <rect class="lan" x="439" y="163" width="410" height="74" rx="10"/><text class="title" x="644" y="188" text-anchor="middle">Si NAT détecté : UDP 4500</text><text class="muted" x="644" y="208" text-anchor="middle">IKE sur 4500 et ESP encapsulé en UDP</text><text class="muted" x="644" y="224" text-anchor="middle">la règle de filtrage doit autoriser le transport requis</text>
  <path class="plain" d="M405 199 H436"/><polygon points="428,193 438,199 428,205" fill="#4ade80"/>
  <text class="muted" x="470" y="263" text-anchor="middle">ESP natif = protocole IP 50 ; UDP 4500 = ESP encapsulé pour traverser le NAT.</text>
</svg></div>

NAT-T ne garantit pas que tous les réseaux intermédiaires autorisent le flux. Un pare-feu peut bloquer UDP 4500, un routeur peut expirer les associations NAT, ou un changement d’IP publique peut affecter le tunnel. Vérifie le chemin aller-retour, les logs du NAT et les compteurs de SA.

## 1.8 Routage, NAT exemption et chemin retour

Les pannes IPsec se trouvent fréquemment hors du moteur cryptographique. Avant d’accuser les algorithmes, valide les routes locales, la route par défaut, le chemin vers l’IP publique distante, et les routes vers les sous-réseaux protégés. L’endpoint doit pouvoir joindre l’adresse publique du peer par le réseau externe sans la faire entrer récursivement dans le tunnel qu’il essaie d’établir.

Pour un VPN policy-based, une règle NAT peut modifier la source avant l’évaluation IPsec et empêcher la correspondance avec l’ACL crypto. Il est courant de créer une exemption NAT pour le trafic inter-sites, selon la manière dont la plateforme ordonne NAT et IPsec. Le terme et le mécanisme exacts diffèrent entre les constructeurs.

Exemple conceptuel de priorité de traitement :

1. Identifier le trafic et la route prévue.
2. Appliquer, selon la plateforme, la traduction d’adresses pertinente ou l’exemption.
3. Évaluer si la politique IPsec protège le paquet.
4. Encapsuler ou transmettre le paquet selon le résultat.
5. Au site distant, vérifier la désencapsulation, les règles de sécurité, le routage du paquet interne et son retour.

Cette séquence est conceptuelle : ne l’applique pas comme un ordre universel à tous les équipements. Utilise la documentation correspondant au modèle précis.

## 1.9 MTU, overhead ESP et MSS TCP

IPsec ajoute de l’overhead : nouvel en-tête IP en mode tunnel, en-tête ESP, champs de séquence, IV/nonce, données de bourrage et tag d’intégrité, et éventuellement en-tête UDP pour NAT-T. L’overhead exact dépend du mode, de l’algorithme, de l’adressage IPv4/IPv6 et des options négociées. Un paquet qui tient sur le LAN peut dépasser le MTU effectif une fois encapsulé.

<div class="ipx-wrap" role="img" aria-label="Un paquet interne augmente de taille avec les en-têtes IP externe, ESP et éventuellement UDP, puis peut dépasser la MTU du chemin.">
<svg class="ipx-svg" viewBox="0 0 940 310" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="24" text-anchor="middle">Encapsulation et risque de dépassement de MTU</text>
  <text x="30" y="62">Paquet interne avant IPsec</text>
  <rect class="lan" x="30" y="77" width="880" height="42" rx="6"/><text class="title" x="470" y="103" text-anchor="middle">En-tête IP interne + TCP/UDP + données</text>
  <text x="30" y="155">Après mode tunnel ESP</text>
  <rect class="frame" x="30" y="170" width="155" height="45" rx="6"/><text x="107" y="197" text-anchor="middle">IP externe</text>
  <rect class="router" x="190" y="170" width="108" height="45" rx="6"/><text x="244" y="197" text-anchor="middle">ESP</text>
  <rect class="router" x="303" y="170" width="95" height="45" rx="6"/><text x="350" y="197" text-anchor="middle">IV/tag</text>
  <rect class="lan" x="403" y="170" width="507" height="45" rx="6"/><text x="656" y="197" text-anchor="middle">Paquet IP interne protégé</text>
  <path class="tunnel" d="M30 239 H795"/><polygon points="787,232 800,239 787,246" fill="#22d3ee"/><line x1="800" y1="226" x2="800" y2="258" stroke="#f87171" stroke-width="3"/><text class="bad" x="813" y="240">MTU</text>
  <text class="muted" x="30" y="280">Réduire le MTU/MSS ou corriger PMTUD peut résoudre les symptômes, mais il faut d’abord mesurer.</text><text class="muted" x="30" y="297">Les nombres d’octets ne sont pas à l’échelle : l’overhead varie selon la suite et le mode.</text>
</svg></div>

Symptômes possibles : petits pings qui passent, mais gros transferts bloqués ; établissement TCP suivi d’un HTTPS qui se fige ; pertes lorsque le flux traverse un chemin différent. Les causes possibles incluent PMTUD cassé, ICMP « fragmentation needed » filtré, PMTU différente selon le chemin ou MSS non adapté.

**Démarche de vérification :**

- Mesure la MTU du chemin et compare les tests avec différentes tailles de paquets.
- Vérifie si les messages ICMP nécessaires à la découverte de MTU sont permis par le chemin.
- Utilise le MSS clamping comme solution encadrée lorsque c’est approprié, plutôt que de réduire arbitrairement la MTU partout.
- Teste les flux UDP séparément : le MSS TCP ne change pas les datagrammes UDP.
- Mesure après encapsulation et sur les interfaces effectives ; ne déduis pas l’overhead exact d’un schéma simplifié.

> **Piège :** une correction MSS peut masquer une PMTUD défectueuse sans traiter les autres protocoles. Documente pourquoi le réglage est nécessaire et revalide les tailles de paquets.

## 1.10 Renouvellement des clés et stabilité

Les SA ont des durées de vie et doivent être renouvelées. Un rekey bien géré permet de créer une nouvelle SA avant de retirer l’ancienne, en limitant l’interruption. Les deux pairs ne doivent pas nécessairement présenter des minuteries identiques, mais ils doivent interopérer avec leur stratégie de renouvellement. Le comportement exact dépend de l’implémentation.

<div class="ipx-wrap" role="img" aria-label="Cycle de vie d’une Child SA : négociation, transfert, renouvellement avant expiration, transition et suppression de l’ancienne SA.">
<svg class="ipx-svg" viewBox="0 0 940 270" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="25" text-anchor="middle">Cycle de vie et renouvellement d’une Child SA</text>
  <rect class="frame pulse" x="25" y="75" width="170" height="75" rx="10"/><text class="title" x="110" y="103" text-anchor="middle">Négociation</text><text class="muted" x="110" y="125" text-anchor="middle">création SA</text>
  <rect class="lan pulse" x="250" y="75" width="170" height="75" rx="10"/><text class="title" x="335" y="103" text-anchor="middle">Transfert</text><text class="muted" x="335" y="125" text-anchor="middle">ESP actif</text>
  <rect class="router pulse" x="475" y="75" width="190" height="75" rx="10"/><text class="title" x="570" y="103" text-anchor="middle">Rekey</text><text class="muted" x="570" y="125" text-anchor="middle">nouvelle SA négociée</text>
  <rect class="lan pulse" x="720" y="75" width="190" height="75" rx="10"/><text class="title" x="815" y="103" text-anchor="middle">Transition</text><text class="muted" x="815" y="125" text-anchor="middle">ancienne supprimée</text>
  <path class="tunnel" d="M195 112 H250 M420 112 H475 M665 112 H720"/><polygon points="243,106 253,112 243,118" fill="#22d3ee"/><polygon points="468,106 478,112 468,118" fill="#22d3ee"/><polygon points="713,106 723,112 713,118" fill="#22d3ee"/>
  <path class="plain" d="M815 150 V196 H110 V150"/><polygon points="104,158 110,148 116,158" fill="#4ade80"/>
  <text class="muted" x="470" y="222" text-anchor="middle">Prévoir des marges, des logs et des compteurs pour observer les rekeys.</text><text class="muted" x="470" y="242" text-anchor="middle">Un échec périodique peut correspondre à une expiration ou à un renouvellement mal négocié.</text>
</svg></div>

Si le tunnel fonctionne pendant une durée prévisible puis s’interrompt, observe les logs et l’état des SA au moment exact du problème. Cherche les changements de SPI, messages CREATE_CHILD_SA, renouvellements d’authentification si applicables, expiration de certificats, timers NAT et basculements de route. Ne résous pas automatiquement le problème en mettant les durées de vie à une valeur très longue : les clés doivent être renouvelées selon une politique cohérente.

## 1.11 Routage route-based et policy-based

| Propriété | Policy-based | Route-based / VTI |
|---|---|---|
| Décision d’entrée | Sélection par politique/ACL crypto | Route vers interface tunnel, avec politique associée |
| Visibilité de la route | Parfois indirecte ou couplée à l’ACL | Interface tunnel visible dans le routage |
| Dynamique de routage | Dépend du fournisseur et du design | Souvent plus simple pour OSPF/BGP au-dessus du tunnel, si supporté |
| Dépannage | Séparer ACL crypto, NAT et route | Vérifier interface virtuelle, route, tunnel, SA et MTU |
| Interopérabilité | Sélecteurs parfois plus stricts | Les détails VTI et TS restent propres à chaque plateforme |

Aucun modèle n’est automatiquement meilleur. Un VTI peut faciliter des architectures multi-sites et le routage dynamique, tandis qu’un VPN policy-based peut convenir à des flux précisément délimités ou à des équipements limités. La décision tient compte de l’interopérabilité, de l’exploitation, de la topologie et des capacités réelles de l’équipement.

## 1.12 Algorithme de diagnostic par couches

<div class="ipx-wrap" role="img" aria-label="Arbre de dépannage IPsec : vérifier transport, IKE SA, Child SA, compteurs ESP, routage et MTU selon le premier résultat qui échoue.">
<svg class="ipx-svg" viewBox="0 0 940 385" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="24" text-anchor="middle">Arbre de décision — localiser la première couche défaillante</text>
  <rect class="frame" x="330" y="43" width="280" height="48" rx="9"/><text class="title" x="470" y="72" text-anchor="middle">1. Pair public joignable ?</text>
  <path class="plain" d="M470 91 V115 H230 V133 M470 115 H710 V133"/><polygon points="224,126 230,136 236,126" fill="#4ade80"/><polygon points="704,126 710,136 716,126" fill="#4ade80"/>
  <rect class="frame" x="80" y="133" width="300" height="48" rx="9"/><text x="230" y="162" text-anchor="middle">Non → routage / ACL / UDP 500/4500</text>
  <rect class="router" x="560" y="133" width="300" height="48" rx="9"/><text x="710" y="162" text-anchor="middle">Oui : IKE SA établie ?</text>
  <path class="tunnel" d="M710 181 V204 H490 V220 M710 204 H745 V220"/><polygon points="484,213 490,223 496,213" fill="#22d3ee"/><polygon points="739,213 745,223 751,213" fill="#22d3ee"/>
  <rect class="frame" x="320" y="220" width="340" height="48" rx="9"/><text x="490" y="249" text-anchor="middle">Non → proposition, authentification, identité</text>
  <rect class="lan" x="675" y="220" width="220" height="48" rx="9"/><text x="785" y="249" text-anchor="middle">Oui : Child SA présente ?</text>
  <path class="plain" d="M785 268 V290 H555 V307 M785 290 H805 V307"/><polygon points="549,300 555,310 561,300" fill="#4ade80"/><polygon points="799,300 805,310 811,300" fill="#4ade80"/>
  <rect class="frame" x="390" y="307" width="330" height="48" rx="9"/><text x="555" y="336" text-anchor="middle">Non → TS, ESP proposal, logs IKE_AUTH</text>
  <rect class="lan" x="735" y="307" width="175" height="48" rx="9"/><text x="822" y="327" text-anchor="middle">Oui : compteurs</text><text class="muted" x="822" y="343" text-anchor="middle">routage / ACL / MTU</text>
  <text class="muted" x="470" y="378" text-anchor="middle">Un test échoue : remonter à la couche la plus proche, plutôt que modifier plusieurs paramètres à la fois.</text>
</svg></div>

Une enquête reproductible commence par une hypothèse et une mesure, pas par une modification aléatoire. Choisis un flux source/destination unique, note l’heure, fais un test simple, observe une seule catégorie de compteurs, puis modifie une variable à la fois.


## 2. Configuration et pratique

## 2.1 Préparer le laboratoire et le plan de changement

Avant de configurer un tunnel, écris les informations nécessaires dans une fiche de compatibilité :

| Paramètre | Pair A | Pair B | Test de cohérence |
|---|---|---|---|
| Adresse publique | `198.51.100.10` (exemple) | `203.0.113.20` (exemple) | Chaque pair connaît l’adresse publique du voisin |
| Réseaux protégés | `10.10.10.0/24` | `10.20.20.0/24` | Pas de chevauchement non prévu |
| Version IKE | IKEv2 | IKEv2 | Les deux côtés acceptent IKEv2 |
| Authentification | PSK pour labo ou certificats | Même méthode prévue | Secret ou identité/certificat cohérent |
| Proposition IKE | Suite approuvée | Suite compatible | Au moins une proposition commune |
| Proposition ESP | Suite approuvée | Suite compatible | Transformations compatibles |
| NAT-T | Selon topologie | Selon topologie | UDP 500/4500 autorisé si nécessaire |
| Durées de vie/rekey | Valeurs documentées | Valeurs interopérables | Renouvellement observé en labo |

Utilise uniquement des secrets factices dans les documents de formation. Les secrets de production doivent provenir d’un coffre adapté ou d’un mécanisme sécurisé de distribution, et ne doivent pas être enregistrés dans un dépôt Git ou des captures de terminal partagées.

## 2.2 Exemple Cisco IOS/IOS XE : modèle policy-based

La configuration suivante montre la structure logique d’un VPN site-à-site sur une plateforme qui prend en charge ces commandes. Les noms de commandes de politique IKEv2, les paramètres cryptographiques disponibles et les commandes de vérification dépendent de la version. Il faut confirmer la syntaxe exacte dans la documentation du modèle.

Exemple conceptuel côté A :

```text
! Exemple de laboratoire seulement — adapter à la plateforme.
crypto ikev2 proposal IKEV2-PROP
 encryption aes-cbc-256
 integrity sha256
 group 14
!
crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROP
!
crypto ikev2 keyring KR-LAB
 peer SITE-B
  address 203.0.113.20
  pre-shared-key local <SECRET_LAB_A>
  pre-shared-key remote <SECRET_LAB_B>
!
crypto ikev2 profile IKEV2-PROFILE
 match identity remote address 203.0.113.20 255.255.255.255
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-LAB
!
crypto ipsec transform-set ESP-LAB esp-aes 256 esp-sha256-hmac
 mode tunnel
!
crypto map VPN-MAP 10 ipsec-isakmp
 set peer 203.0.113.20
 set ikev2-profile IKEV2-PROFILE
 set transform-set ESP-LAB
 match address VPN-TRAFFIC
!
ip access-list extended VPN-TRAFFIC
 permit ip 10.10.10.0 0.0.0.255 10.20.20.0 0.0.0.255
!
interface GigabitEthernet0/0
 description WAN-LAB
 crypto map VPN-MAP
```

**Important :** cette structure pédagogique peut nécessiter des ajustements. Certaines versions utilisent des commandes de chiffrement authentifié différentes, l’association exacte du profil IKEv2 et du crypto map varie, et toutes les versions n’acceptent pas les mêmes propositions. Ne tente pas de corriger une erreur de CLI en supprimant les contrôles de sécurité ; identifie la plateforme et consulte sa référence.

Le côté B doit définir le pair A, le réseau distant `10.10.10.0/24`, le réseau local `10.20.20.0/24`, et une proposition compatible. Les adresses des pairs, les identités et les sélecteurs vus par les deux extrémités doivent se correspondre selon les conventions du fournisseur.

> **Astuce :** écris une matrice à deux colonnes montrant ce que chaque pair considère comme local et distant. Cette simple étape évite les ACL crypto inversées et les TS incohérents.

## 2.3 Exemple route-based / VTI : principes de configuration

Un tunnel route-based associe IPsec à une interface virtuelle. Une fois le tunnel établi, le routage peut envoyer les préfixes distants via cette interface. Le tunnel ne supprime pas le besoin d’authentifier le pair, de choisir les algorithmes, de restreindre les réseaux annoncés et de filtrer les flux autorisés.

Modèle conceptuel, dont la syntaxe doit être adaptée :

```text
! Pseudo-configuration : vérifier la syntaxe du modèle IOS/IOS XE.
interface Tunnel10
 description VPN-SITE-B
 ip address 169.254.100.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.20
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile IPSEC-PROFILE
!
ip route 10.20.20.0 255.255.255.0 Tunnel10
```

L’IP de transit `169.254.100.0/30` est illustrative et doit être remplacée si elle chevauche une plage existante ou si le design exige un autre plan. Selon la plateforme, la syntaxe VTI/IPsec, la protection de tunnel et les restrictions de routage peuvent être différentes.

### Tests à effectuer

1. Confirmer la connectivité entre les adresses publiques des peers.
2. Lire le statut IKE SA et Child SA.
3. Vérifier que l’interface de tunnel est active et correctement adressée, si VTI.
4. Vérifier la route vers chaque préfixe distant.
5. Générer un flux source/destination connu et observer les compteurs de chiffrement/déchiffrement.
6. Confirmer le retour depuis le LAN distant.
7. Tester les flux applicatifs et les tailles de paquets, pas seulement ICMP.

## 2.4 Les commandes de vérification

Sur de nombreuses versions IOS/IOS XE, les commandes suivantes sont utiles ; leur disponibilité varie :

```text
show crypto ikev2 sa
show crypto ipsec sa
show crypto session detail
show access-lists
show ip route
show interfaces tunnel 10
show logging
```

Cherche les champs suivants : état et identité du peer, SPI entrants/sortants, algorithmes négociés, temps de vie, compteurs encaps/decaps, erreurs d’intégrité, anti-rejeu, derniers échanges IKE, et interface/route utilisée. Si les compteurs d’encapsulation augmentent sur A mais les compteurs de décapsulation de B restent à zéro, le problème se situe possiblement sur le chemin externe, le pair B ou la SA attendue. Si les compteurs augmentent dans les deux sens mais que l’application échoue, passe aux ACL du LAN, au routage interne, au MTU et à l’application.

## 2.5 NAT exemption et règles de pare-feu

Dans un design policy-based, le trafic inter-sites doit correspondre à la politique IPsec au moment où la plateforme l’évalue. Si NAT traduit son adresse source avant cette étape, le paquet peut ne plus correspondre à l’ACL attendue. Configure une exemption NAT ou une politique de traduction adaptée selon l’ordre de traitement documenté.

Pour le trafic de contrôle et de données, la matrice de pare-feu doit distinguer :

| Flux | Protocole | But |
|---|---|---|
| IKE | UDP 500 | Négociation initiale, si aucun NAT-T ne fait basculer le flux |
| IKE/NAT-T | UDP 4500 | IKE encapsulé et ESP encapsulé en cas de NAT détecté |
| ESP natif | IP protocol 50 | Données ESP sans encapsulation UDP, quand utilisé |
| Trafic interne protégé | Selon application | Flux LAN autorisé après décapsulation |

N’ouvre pas ces flux depuis n’importe quelle source. Restreins les peers aux adresses attendues quand c’est possible et n’autorise que les réseaux et services qui doivent passer dans le tunnel.

## 2.6 Laboratoire guidé : tunnel établi mais trafic unidirectionnel

**Situation :** IKE SA et Child SA sont établies. Depuis le LAN A, `10.10.10.10` atteint l’interface du peer distant mais ne reçoit aucune réponse du serveur `10.20.20.20`. Les compteurs d’encapsulation augmentent sur A.

**Hypothèses initiales :**

- Le paquet externe atteint le pair B mais la décapsulation échoue.
- Le LAN B ne possède pas de route de retour vers `10.10.10.0/24`.
- Une ACL du pare-feu B bloque le trafic après décapsulation.
- Le serveur B utilise une mauvaise passerelle par défaut.
- Les sélecteurs de la Child SA ne couvrent pas le trafic attendu.

**Méthode :**

1. Note l’heure et exécute un seul test vers une destination connue.
2. Sur A, compare les compteurs d’encapsulation avant et après le test.
3. Sur B, compare les compteurs de décapsulation et les erreurs d’intégrité/rejeu.
4. Vérifie les routes du peer B et du serveur B.
5. Vérifie les ACL du pare-feu côté LAN après décapsulation.
6. Capture côté LAN B, si autorisé, pour savoir si le paquet interne arrive.
7. Corrige une cause à la fois et répète le test.

**Critère de réussite :** paquet reçu sur le LAN B, réponse routée vers le réseau A, compteurs ESP qui augmentent dans les deux sens et test applicatif réussi.

## 2.7 Laboratoire guidé : les petits paquets passent, pas les gros

**Situation :** un ping petit passe dans les deux sens ; une session HTTPS commence mais le chargement se bloque après le handshake.

**Hypothèses :** MTU effective insuffisante, ICMP PMTUD bloqué, MSS trop élevé, différence entre les chemins aller et retour, fragmentation ou filtrage de fragments.

**Diagnostic :**

- Vérifie la taille des paquets et le bit DF si applicable au lab.
- Compare la taille maximale qui traverse le chemin avec le tunnel actif et sans tunnel, en environnement contrôlé.
- Observe les messages ICMP pertinents et les compteurs de fragmentation.
- Confirme si la protection ou un NAT ajoute un overhead supplémentaire.
- Applique un réglage MTU/MSS uniquement lorsqu’il est justifié par les mesures.
- Réteste HTTPS, les transferts volumineux, UDP et IPv6 lorsque ces flux sont dans le périmètre.

> **Piège :** un ping réussi n’est pas une preuve de bon fonctionnement pour les gros segments. Il ne valide ni la MSS TCP ni la PMTUD.

## 2.8 Journalisation et captures

Active une journalisation suffisamment détaillée pour le temps du laboratoire, mais évite de laisser un débogage verbeux permanent sur une plateforme sollicitée. Les commandes de debug et les noms exacts de catégories changent selon la version. Avant toute opération, vérifie le niveau de charge, le buffer de logs et la possibilité de préserver une session d’administration de secours.

Lors d’une capture externe, ESP natif est généralement identifiable comme protocole IP 50 ; les échanges IKE sont visibles sur UDP 500 ou 4500. Avec NAT-T, l’observateur voit des datagrammes UDP 4500 mais le contenu ESP est protégé. Les adresses IP et ports internes peuvent ne pas être directement observables sans capture côté LAN ou au point de terminaison.

Les secrets partagés, clés privées, clés de session, exports complets de configuration et captures internes peuvent être sensibles. Nettoie les captures avant de les partager, restreins les accès et définis une durée de conservation.


## 3. Dépannage et sécurité

## 3.1 Matrice symptômes → hypothèses → preuves

| Symptôme | Hypothèses probables | Preuves à collecter | Action prudente |
|---|---|---|---|
| Aucun échange IKE | Peer inaccessible, route incorrecte, UDP filtré | Ping/trace contrôlée, logs WAN, capture UDP | Corriger transport ou filtrage précis |
| IKE_SA_INIT répété | Proposition commune absente, paquet de réponse perdu, problème NAT | Logs des deux côtés et capture | Harmoniser les suites et vérifier retour |
| IKE_AUTH échoue | PSK incorrecte, identité inattendue, certificat expiré/non approuvé | Logs d’identité et chaîne de certificats | Corriger l’identité ou le secret via canal sécurisé |
| IKE SA active, Child SA absente | Propositions ESP, sélecteurs, PFS/DH incompatibles | Logs IKE et politique IPsec | Comparer les paramètres exacts |
| Child SA active, compteurs nuls | Mauvaise route ou aucun trafic qui correspond | Routes, ACL crypto, sélecteurs | Tester un flux autorisé précis |
| Encapsulation seule | Pair distant absent, filtrage externe ou SA non alignée | Compteurs des deux peers, capture WAN | Isoler chemin, peer ou SPI |
| Décapsulation seule | Trafic retour absent ou route locale incorrecte | Routes, capture LAN, logs pare-feu | Vérifier le retour et les politiques LAN |
| Coupures périodiques | Rekey, timers NAT, changement WAN, DPD ou failover | Logs horodatés et états de SA | Corréler avec événement et tester transition |
| Gros transferts bloqués | MTU, PMTUD, MSS, ICMP filtré | Tests de taille et capture | Corriger MTU/MSS selon preuve |
| Performance faible | CPU crypto saturé, pertes, MTU, débits limités | CPU, throughput, drops, latence | Mesurer le goulot et augmenter la capacité si justifié |

## 3.2 Comprendre les logs et comparer les deux pairs

Les logs IKE doivent être interprétés en contexte. Un message « proposal not chosen » ne signifie pas la même chose qu’un échec de vérification d’identité ou un message d’expiration. Regroupe les événements autour d’un même timestamp, compare les identités, les adresses source et destination, les SPI, les suites et les transitions des SA.

Les points d’observation doivent être symétriques : un message envoyé par A n’implique pas qu’il ait été reçu ou traité par B. Lors d’un incident réel, demande au pair distant des horodatages en UTC ou documente précisément le décalage d’horloge. Un syslog sans horodatage fiable rend l’ordre causal difficile à établir.

Procédure conseillée :

1. Capturer l’état du tunnel sans rien modifier.
2. Définir une plage horaire et un seul test reproductible.
3. Exporter les logs des deux pairs avec les identifiants de SA utiles.
4. Identifier le dernier échange réussi et le premier événement divergent.
5. Formuler une hypothèse vérifiable.
6. Effectuer une seule modification planifiée.
7. Vérifier non seulement la négociation, mais aussi les données et le retour.

## 3.3 Sécurité du plan de gestion

Le VPN est un canal protégé, mais la passerelle qui le termine reste un équipement critique. Restreins l’administration aux réseaux et identités autorisés, utilise un contrôle d’accès robuste, protège les comptes privilégiés, désactive les services d’administration inutiles et garde le firmware à jour. Le trafic décapsulé doit encore être filtré : un tunnel chiffré peut transporter un malware ou un flux non autorisé si les politiques internes sont trop larges.

Privilégie les certificats lorsque l’échelle ou les exigences de gouvernance le justifient ; ils simplifient souvent la gestion de nombreuses identités, mais exigent une PKI opérationnelle, des procédures de renouvellement, de révocation et de contrôle des noms d’identité. Une PSK est simple en laboratoire, mais sa réutilisation à grande échelle complique la rotation et augmente l’impact d’une fuite.

### Durcissement de base

- Préférer IKEv2 et des suites cryptographiques maintenues, approuvées et compatibles.
- Supprimer les propositions faibles inutiles et documenter les exceptions temporaires.
- Restreindre chaque tunnel aux préfixes et services requis.
- Ne pas exposer UDP 500/4500 depuis toutes les sources quand une liste de peers est possible.
- Activer les protections anti-rejeu prévues par la politique et vérifier les compteurs d’erreurs.
- Séparer les réseaux de gestion, de données et de transit.
- Sauvegarder les configurations chiffrées et tester la restauration.
- Renouveler les secrets/certificats et vérifier les dates d’expiration.
- Synchroniser les horloges avec une source fiable et centraliser les logs.
- Revoir les accès, routes et règles après chaque changement topologique.

> **Danger :** ne divulgue jamais une PSK, une clé privée, une clé de session ou un fichier de configuration non expurgé dans une issue publique. Si un secret est exposé, considère-le compromis, révoque ou remplace-le selon la procédure d’incident et vérifie les traces d’utilisation.

## 3.4 Haute disponibilité et basculement WAN

Un VPN redondant doit assurer non seulement la disponibilité du chemin IP, mais aussi la détection des changements, la reconstruction des SA et la convergence du routage. Une bascule peut changer l’adresse source, l’interface, le next-hop ou la route vers le peer. Le VPN peut alors devoir renégocier IKE et Child SA. Le design doit prévoir les timers, la fréquence de surveillance et les conséquences d’une convergence trop agressive.

Schéma logique :

<div class="ipx-wrap" role="img" aria-label="Deux chemins WAN redondants convergent vers une passerelle VPN ; un lien de secours prend le relais après détection d’une panne.">
<svg class="ipx-svg" viewBox="0 0 940 305" xmlns="http://www.w3.org/2000/svg">
  <text class="title" x="470" y="25" text-anchor="middle">Redondance WAN et rétablissement du VPN</text>
  <rect class="lan" x="30" y="105" width="160" height="70" rx="12"/><text class="title" x="110" y="132" text-anchor="middle">LAN protégé</text><text class="muted" x="110" y="153" text-anchor="middle">site local</text>
  <rect class="router" x="260" y="48" width="175" height="60" rx="10"/><text class="title" x="347" y="73" text-anchor="middle">WAN primaire</text><text class="muted" x="347" y="92" text-anchor="middle">pair / chemin A</text>
  <rect class="frame" x="260" y="184" width="175" height="60" rx="10"/><text class="title" x="347" y="209" text-anchor="middle">WAN secours</text><text class="muted" x="347" y="228" text-anchor="middle">pair / chemin B</text>
  <rect class="lan pulse" x="520" y="105" width="170" height="70" rx="12"/><text class="title" x="605" y="132" text-anchor="middle">Passerelle IPsec</text><text class="muted" x="605" y="153" text-anchor="middle">IKE + Child SA</text>
  <rect class="frame" x="760" y="105" width="150" height="70" rx="12"/><text class="title" x="835" y="132" text-anchor="middle">Réseau distant</text><text class="muted" x="835" y="153" text-anchor="middle">préfixes protégés</text>
  <path class="tunnel" d="M190 130 L260 78 M190 151 L260 213 M435 78 L520 122 M435 213 L520 158 M690 140 H760"/><polygon points="512,116 523,122 512,128" fill="#22d3ee"/><polygon points="512,152 523,158 512,164" fill="#22d3ee"/><polygon points="752,134 763,140 752,146" fill="#22d3ee"/>
  <text class="muted" x="470" y="274" text-anchor="middle">Tester la détection, le changement de route, le rekey et le rétablissement des flux applicatifs.</text><text class="muted" x="470" y="292" text-anchor="middle">Un lien redondant n’est utile que si les SA et les routes convergent dans le délai visé.</text>
</svg></div>

### Plan de test HA

- Couper le lien primaire dans une fenêtre autorisée.
- Mesurer le temps de détection, le temps d’établissement/reprise IKE, le temps de convergence route et le rétablissement applicatif.
- Vérifier que le peer distant accepte la nouvelle adresse si elle change.
- Vérifier que les règles firewall/NAT sont valides pour le chemin secondaire.
- Revenir au chemin primaire et observer le comportement de retour pour éviter un flap.
- Conserver les logs et les compteurs, puis corriger les timers seulement à partir des mesures.

## 3.5 Supervision et indicateurs

Le statut du tunnel (`UP/DOWN`) est utile mais insuffisant. Une supervision exploitable suit plusieurs dimensions :

| Indicateur | Pourquoi le surveiller | Alerte possible |
|---|---|---|
| IKE SA et Child SA | État du contrôle et des données | Tunnel down ou SA attendue absente |
| Âge et fréquence de rekey | Renouvellements réussis ou répétitifs | Rekey échoué ou fréquence anormale |
| Compteurs encaps/decaps | Sens réel du trafic protégé | Un seul sens augmente pendant les tests |
| Erreurs intégrité/anti-rejeu | Paquets rejetés ou désordre | Croissance inhabituelle |
| CPU crypto / débit | Capacité du matériel | Utilisation soutenue proche du seuil défini |
| Latence, pertes, gigue | Qualité applicative | Dégradation par rapport à une baseline |
| MTU / fragmentation | Risques sur gros paquets | Transferts volumineux bloqués |
| Expiration certificat | Continuité de l’authentification | Alerte avant expiration selon politique |

Établis une baseline par site et par chemin, puis définis des seuils selon l’usage métier. Un VPN de sauvegarde nocturne et un VPN voix temps réel ne doivent pas forcément avoir les mêmes seuils. Évite les alertes répétitives sans action associée ; chaque alerte critique doit préciser qui intervient et quel diagnostic est attendu.

## 3.6 Dépannage cryptographique : règles de prudence

Un échec crypto peut venir de propositions non communes, d’une identité incorrecte, d’un certificat invalide, d’un secret différent ou d’un groupe DH qui ne correspond pas. Commence par comparer le résultat réellement négocié aux paramètres attendus. Il ne suffit pas de voir le nom de la proposition dans la configuration : elle peut ne pas être utilisée.

Ne baisse pas plusieurs paramètres d’un coup. Une réduction temporaire des propositions peut servir à localiser une incompatibilité uniquement dans un lab ou dans une fenêtre de changement autorisée, avec validation explicite du risque. L’objectif est de retrouver une suite approuvée commune, et non de forcer une négociation affaiblie.

Pour les certificats, vérifie l’heure système avant de conclure à un problème de confiance. Un certificat apparemment expiré peut être lié à une horloge décalée ; inversement, une date locale correcte ne prouve pas que la chaîne ou l’identité est approuvée.

## 3.7 Plan de retour arrière et gestion du changement

Un changement IPsec peut interrompre l’accès distant, notamment si la route de gestion dépend elle-même du tunnel modifié. Avant d’intervenir :

1. Sauvegarde la configuration dans un emplacement sécurisé et vérifie qu’elle est restaurable.
2. Assure-toi qu’un accès hors bande ou local reste disponible.
3. Définis des critères de succès et de retour arrière mesurables.
4. Modifie un seul domaine à la fois : IKE, ESP, sélecteurs, route, NAT ou filtrage.
5. Vérifie état, compteurs et flux réels.
6. Si la fenêtre de changement expire sans succès, reviens à la configuration précédente et collecte les logs.
7. Enregistre les écarts et la cause racine pour éviter de répéter la modification.

> **Astuce :** un retour arrière doit être préparé avant le changement, pas inventé pendant la panne. Le fichier de configuration sauvegardé doit aussi être protégé comme un secret, car il peut contenir des informations d’infrastructure sensibles.


## Points à retenir

- IKEv2 négocie les paramètres et authentifie les pairs ; ESP protège les paquets du plan de données.
- IKE SA et Child SA ont des fonctions distinctes. La réussite de l’une ne prouve pas le bon fonctionnement de l’autre.
- Les routes décident du chemin ; les sélecteurs/politiques décident quels flux sont protégés.
- ESP natif correspond au protocole IP 50. UDP 500 sert à IKE et UDP 4500 à IKE/NAT-T et ESP encapsulé selon le contexte.
- Les propositions IKE et ESP doivent être examinées séparément. Utilise des suites approuvées et compatibles.
- Une panne unidirectionnelle exige de comparer les compteurs et le chemin retour des deux pairs.
- Les transferts bloqués uniquement à grande taille orientent vers MTU, PMTUD, ICMP ou MSS.
- Les interruptions à intervalle régulier invitent à examiner le rekey, les expirations et les événements de redondance.
- Les commandes de débogage peuvent être coûteuses ; préfère une collecte contrôlée et horodatée.
- Un tunnel chiffré ne remplace pas le filtrage des réseaux et services après décapsulation.
- Valide les commandes sur la version logicielle précise et n’exécute jamais directement en production une configuration générique non testée.

## Exercices de révision

### Exercice 1 — IKE actif, aucune donnée

Les deux pairs affichent une IKE SA active mais aucune Child SA. Donne quatre hypothèses à examiner avant de changer la configuration.

**Correction attendue :** authentification et identités pendant IKE_AUTH, proposition ESP incompatible, sélecteurs non correspondants, paramètres PFS/DH ou règles de politique selon la plateforme. Il faut examiner les logs des deux pairs pour trouver le premier échec.

### Exercice 2 — Encapsulation sans décapsulation

Les compteurs d’encapsulation augmentent sur A ; ceux de décapsulation sur B restent inchangés. Quelles preuves recueillir ?

**Correction attendue :** capture WAN, accessibilité et filtrage du pair, adresse source externe réellement utilisée, SPI et SA côté B, logs IKE/ESP horodatés et éventuel NAT intermédiaire. Ensuite seulement, isoler le problème de transport ou le rejet par le pair.

### Exercice 3 — Gros transfert bloqué

Un ping de 64 octets marche, mais un téléchargement important se fige. Pourquoi ne faut-il pas commencer par renouveler la PSK ?

**Correction attendue :** la négociation est probablement fonctionnelle et le symptôme évoque MTU/PMTUD/MSS, fragmentation ou filtrage ICMP. Il faut mesurer les tailles et examiner les paquets, avant de modifier des paramètres cryptographiques sans rapport évident.

### Exercice 4 — Coupure toutes les heures

Énumère les éléments à corréler.

**Correction attendue :** expiration/rekey des Child SA, renouvellement IKE, timers NAT, DPD/liveness, certificat, changement de route ou de lien, journaux des deux pairs, compteurs et horloges synchronisées.

### Exercice 5 — Choix route-based ou policy-based

Un nouveau site doit transporter plusieurs réseaux et exécuter OSPF au-dessus du tunnel. Quel modèle envisager, et quelles limites vérifier ?

**Correction attendue :** envisager un VTI/route-based si la plateforme le supporte ; vérifier support IKE/IPsec, adjacence OSPF, multicast/TTL si requis, sélecteurs, routes de l’endpoint, MTU, redondance et interopérabilité distante. Le choix final dépend du constructeur et du design.

## Références techniques

- IETF, **RFC 7296 — Internet Key Exchange Protocol Version 2 (IKEv2)** : https://www.rfc-editor.org/rfc/rfc7296.html
- IETF, **RFC 4301 — Security Architecture for the Internet Protocol** : https://www.rfc-editor.org/rfc/rfc4301.html
- IETF, **RFC 4303 — IP Encapsulating Security Payload (ESP)** : https://www.rfc-editor.org/rfc/rfc4303.html
- IETF, **RFC 3948 — UDP Encapsulation of IPsec ESP Packets** : https://www.rfc-editor.org/rfc/rfc3948.html
- IETF, **RFC 8247 — IKEv2 Algorithm Implementation Requirements and Usage Guidance** : https://www.rfc-editor.org/rfc/rfc8247.html
- IETF, **RFC 8221 — ESP and AH Algorithm Implementation Requirements** : https://www.rfc-editor.org/rfc/rfc8221.html
- NIST, **SP 800-77 Rev. 1 — Guide to IPsec VPNs** : https://csrc.nist.gov/pubs/sp/800/77/r1/final
- Cisco, documentation de sécurité et VPN IPsec correspondant à la version IOS/IOS XE installée : https://www.cisco.com/c/en/us/support/security/index.html

Les RFC définissent les protocoles ; elles ne garantissent pas que toutes les plateformes prennent en charge toutes les options. La configuration exacte, les suites permises et les commandes de diagnostic doivent toujours être vérifiées dans la documentation du fournisseur et dans la version logicielle réellement déployée.
