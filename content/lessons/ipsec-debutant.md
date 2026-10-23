
# VPN IPsec (IKEv2, ESP) — Débutant

**Niveau :** Débutant

Un VPN IPsec permet de protéger des communications IP à travers un réseau qui n’est pas entièrement fiable, par exemple Internet. IPsec n’est pas une application unique : c’est un ensemble de mécanismes qui associe une politique de sécurité, des associations de sécurité, des algorithmes cryptographiques et des protocoles de transport. IKEv2 aide les deux extrémités à s’authentifier et à négocier les paramètres nécessaires ; ESP protège ensuite les paquets de données.

Dans ce cours, nous allons construire une compréhension progressive. Nous commencerons par la finalité du tunnel et les rôles des équipements, puis nous distinguerons IKEv2 d’ESP, étudierons les modes tunnel et transport et finirons par une configuration de laboratoire, les vérifications et les méthodes de dépannage. Les commandes sont illustratives : leur syntaxe peut changer selon le constructeur, le modèle et la version logicielle.

Le but n’est pas de mémoriser une longue séquence de commandes sans comprendre ce qu’elles font. L’objectif est de pouvoir expliquer pourquoi un tunnel est nécessaire, comment ses paramètres sont négociés, quels paquets sont protégés, et comment localiser un échec sans modifier toute la configuration au hasard.


<style>
.ipsec-viz{margin:1.8rem 0;padding:1rem;border:1px solid #3f3f46;border-radius:1rem;background:#18181b;color:#e4e4e7}
.ipsec-viz__heading{margin:0 0 .35rem;color:#f4f4f5;font-size:1rem;font-weight:700}
.ipsec-viz__caption{margin:0 0 .9rem;color:#a1a1aa;font-size:.88rem;line-height:1.6}
.ipsec-viz__scroll{width:100%;max-width:100%;overflow-x:auto;overscroll-behavior-x:contain}
.ipsec-viz__svg{display:block;width:100%;min-width:760px;height:auto}
.ipsec-viz__svg text{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;fill:#e4e4e7;font-size:14px}
.ipsec-viz__svg .small{font-size:12px;fill:#a1a1aa}
.ipsec-viz__svg .label{font-size:15px;font-weight:700;fill:#f4f4f5}
.ipsec-viz__svg .blue-text{fill:#93c5fd}
.ipsec-viz__svg .green-text{fill:#86efac}
.ipsec-viz__svg .amber-text{fill:#fcd34d}
.ipsec-viz__svg .red-text{fill:#fca5a5}
.ipsec-viz__svg .box{fill:#27272a;stroke:#52525b;stroke-width:1.5}
.ipsec-viz__svg .box-blue{fill:#172554;stroke:#60a5fa;stroke-width:1.5}
.ipsec-viz__svg .box-green{fill:#052e16;stroke:#4ade80;stroke-width:1.5}
.ipsec-viz__svg .box-amber{fill:#422006;stroke:#fbbf24;stroke-width:1.5}
.ipsec-viz__svg .path-base{fill:none;stroke:#71717a;stroke-width:2.5}
.ipsec-viz__svg .path-animated{fill:none;stroke:#60a5fa;stroke-width:3;stroke-dasharray:8 10;animation:ipsecDash 1.4s linear infinite}
.ipsec-viz__svg .path-green{fill:none;stroke:#4ade80;stroke-width:3;stroke-dasharray:8 10;animation:ipsecDash 1.5s linear infinite}
.ipsec-viz__svg .path-amber{fill:none;stroke:#fbbf24;stroke-width:3;stroke-dasharray:7 9;animation:ipsecDash 1.2s linear infinite}
.ipsec-viz__svg .packet{fill:#93c5fd;animation:ipsecPacketPulse 1.3s ease-in-out infinite}
.ipsec-viz__svg .packet-green{fill:#4ade80;animation:ipsecPacketPulse 1.3s ease-in-out infinite}
.ipsec-viz__svg .step{animation:ipsecStep 4.8s ease-in-out infinite}
.ipsec-viz__svg .step-2{animation-delay:1.2s}
.ipsec-viz__svg .step-3{animation-delay:2.4s}
.ipsec-viz__svg .step-4{animation-delay:3.6s}
.ipsec-viz__svg .shield{fill:#14532d;stroke:#4ade80;stroke-width:2}
.ipsec-viz__note{margin:.75rem 0 0;color:#a1a1aa;font-size:.8rem;line-height:1.55}
.ipsec-viz__legend{display:flex;flex-wrap:wrap;gap:.7rem 1rem;margin-top:.8rem;color:#d4d4d8;font-size:.8rem}
.ipsec-viz__key{display:inline-flex;align-items:center;gap:.4rem}
.ipsec-viz__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:999px;background:#60a5fa}
.ipsec-viz__dot--green{background:#4ade80}
.ipsec-viz__dot--amber{background:#fbbf24}
@keyframes ipsecDash{to{stroke-dashoffset:-36}}
@keyframes ipsecPacketPulse{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes ipsecStep{0%,15%,100%{opacity:.72}6%{opacity:1;filter:brightness(1.6)}}
@media(max-width:640px){.ipsec-viz{padding:.7rem}.ipsec-viz__svg{min-width:760px}.ipsec-viz__caption{font-size:.82rem}}
@media(prefers-reduced-motion:reduce){.ipsec-viz *,.ipsec-viz *::before,.ipsec-viz *::after{animation-duration:.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}
</style>


> **Analogie** : imagine deux bâtiments qui doivent s’échanger des dossiers par une rue publique. IKEv2 est la procédure où les responsables vérifient l’identité de l’autre bâtiment, se mettent d’accord sur la serrure et produisent les clés. ESP est l’enveloppe scellée utilisée pour transporter chaque dossier. Le tunnel ne rend pas la rue privée ; il protège les dossiers pendant leur traversée.

## Objectifs d’apprentissage

À la fin du cours, tu devrais être capable de :

- définir VPN, IPsec, IKEv2, ESP, SA et NAT Traversal ;
- différencier confidentialité, intégrité, authentification et protection contre le rejeu ;
- expliquer les échanges IKE_SA_INIT et IKE_AUTH sans les confondre avec le transport des données ;
- distinguer le mode tunnel du mode transport ;
- reconnaître UDP 500, UDP 4500 et ESP directement sur IP ;
- lire une architecture site-à-site et définir les sous-réseaux protégés ;
- comprendre les principaux blocs d’une configuration Cisco de laboratoire ;
- utiliser les commandes de vérification les plus courantes ;
- diagnostiquer méthodiquement un tunnel qui ne monte pas ou qui monte sans transporter les données ;
- appliquer les précautions de sécurité et de changement avant une mise en production.

## 1. Comprendre le besoin : pourquoi un VPN IPsec ?

Une entreprise possède parfois plusieurs sites. Chaque site dispose d’un réseau local et d’une connexion Internet. Les utilisateurs d’un site doivent accéder à un serveur situé dans l’autre. Le routage IP ordinaire permet d’acheminer des paquets, mais il ne chiffre pas leur contenu à lui seul. Sur le réseau public, un observateur peut souvent voir des informations d’en-tête et peut tenter d’intercepter ou d’altérer des paquets si aucune protection appropriée n’est utilisée.

IPsec apporte une protection au niveau IP. Il peut chiffrer les données, détecter certaines altérations et authentifier l’origine des paquets selon la transformation choisie. Il n’empêche toutefois pas toutes les attaques possibles. Un VPN ne corrige pas une application vulnérable, ne remplace pas les règles de pare-feu et ne garantit pas qu’un poste infecté envoie uniquement du trafic sain.

### 1.1 Les trois rôles fréquents d’un VPN

| Type | Extrémités du tunnel | Exemple | Point d’attention |
|---|---|---|---|
| Site-à-site | Deux passerelles de sécurité | Siège ↔ agence | Définir précisément les sous-réseaux autorisés |
| Accès distant | Un poste et une passerelle | Télétravailleur ↔ entreprise | Identité utilisateur, état de l’appareil et MFA selon la solution |
| Hôte-à-hôte | Deux systèmes IPsec | Serveur A ↔ serveur B | Gestion des clés et compatibilité sur les deux systèmes |

Dans un VPN site-à-site classique, les postes utilisateurs n’ont pas besoin de connaître les mécanismes IPsec. Leur passerelle protège le trafic qui correspond à une politique. Sur Internet, les paquets voyagent entre les adresses publiques des passerelles ; à l’intérieur du paquet protégé se trouvent les adresses privées des hôtes qui communiquent.

Un accès distant fonctionne sur le même socle conceptuel, mais les contraintes d’identité et d’adressage sont différentes. L’utilisateur peut être derrière un routeur domestique NAT et son adresse publique peut changer. La configuration doit aussi gérer les plages attribuées aux clients, les DNS, les routes et les politiques d’accès.

### 1.2 Ce que le VPN protège — et ce qu’il ne protège pas

La confidentialité empêche un observateur de lire le contenu protégé sans la clé appropriée. L’intégrité permet au destinataire de détecter des modifications non autorisées du paquet protégé. L’authentification permet de vérifier qu’un pair possède la preuve cryptographique attendue. La protection contre le rejeu limite l’acceptation de paquets capturés puis renvoyés par un tiers.

Mais le chiffrement ne masque pas nécessairement les adresses IP externes, les volumes, la fréquence des échanges ou la durée des sessions. Dans un mode tunnel, les adresses IP intérieures sont protégées dans l’enveloppe ESP, mais les adresses externes restent disponibles pour l’acheminement. Un adversaire peut aussi bloquer Internet, saturer une liaison, attaquer une passerelle ou exploiter une machine autorisée. Un VPN améliore la sécurité du transport, il ne rend pas le réseau invulnérable.

> **Piège :** « Le tunnel est établi » ne signifie pas « toutes les applications sont sécurisées ». Le tunnel indique que des paramètres cryptographiques sont actifs. Les droits d’accès, le routage, le pare-feu, les mises à jour des postes et la sécurité des serveurs restent nécessaires.

### 1.3 Éléments d’une architecture

Les extrémités d’un tunnel sont souvent appelées pairs IPsec ou passerelles VPN. Elles peuvent être des routeurs, des pare-feu, des concentrateurs VPN ou des hôtes. Chaque pair détient une politique indiquant le trafic à protéger, les identités attendues, les algorithmes autorisés et les durées de vie.

Le tunnel logique n’est pas une fibre dédiée. Il s’agit de paquets IPsec qui circulent sur un chemin IP existant. Le réseau public continue à router les paquets selon leur en-tête externe. Si le chemin réseau devient indisponible, les mécanismes cryptographiques ne peuvent pas réparer la connectivité sous-jacente. C’est pourquoi le dépannage doit commencer par l’adresse et le chemin de transport avant de se concentrer sur les négociations cryptographiques.

### Schéma 1 — Architecture d’un VPN IPsec site-à-site

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">Du LAN A au LAN B : qui chiffre et qui déchiffre ?</p>
  <p class="ipsec-viz__caption">Les passerelles IPsec protègent le trajet public. Les postes communiquent avec leurs adresses privées à l’intérieur du tunnel ; les adresses publiques servent au transport entre les passerelles.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 300" role="img" aria-label="Deux LAN privés sont reliés par deux passerelles IPsec. Un chemin animé représente le tunnel chiffré sur Internet.">
      <rect class="box-green" x="22" y="65" width="175" height="150" rx="13"/>
      <text class="label green-text" x="109" y="91" text-anchor="middle">LAN A</text>
      <text x="109" y="115" text-anchor="middle">192.168.10.0/24</text>
      <rect class="box" x="43" y="135" width="132" height="55" rx="8"/>
      <text x="109" y="158" text-anchor="middle">PC / serveur</text>
      <text class="small" x="109" y="177" text-anchor="middle">trafic privé</text>
      <path class="path-base" d="M197 163 H245"/>
      <path class="path-green" d="M197 163 H245"/>
      <rect class="box-blue" x="245" y="80" width="180" height="120" rx="12"/>
      <text class="label blue-text" x="335" y="107" text-anchor="middle">Passerelle A</text>
      <text x="335" y="132" text-anchor="middle">IKEv2 + IPsec</text>
      <text class="small" x="335" y="155" text-anchor="middle">IP publique A</text>
      <text class="small" x="335" y="176" text-anchor="middle">chiffre / déchiffre</text>
      <path class="path-animated" d="M425 140 H555"/>
      <text class="label blue-text" x="490" y="88" text-anchor="middle">Tunnel IPsec</text>
      <text class="small" x="490" y="108" text-anchor="middle">réseau public / Internet</text>
      <rect class="box" x="455" y="164" width="70" height="36" rx="7"/>
      <text class="small" x="490" y="186" text-anchor="middle">ESP</text>
      <circle class="packet" cx="444" cy="140" r="6"/>
      <circle class="packet" cx="478" cy="140" r="6" style="animation-delay:.4s"/>
      <circle class="packet" cx="512" cy="140" r="6" style="animation-delay:.8s"/>
      <rect class="box-blue" x="555" y="80" width="180" height="120" rx="12"/>
      <text class="label blue-text" x="645" y="107" text-anchor="middle">Passerelle B</text>
      <text x="645" y="132" text-anchor="middle">IPsec + IKEv2</text>
      <text class="small" x="645" y="155" text-anchor="middle">IP publique B</text>
      <text class="small" x="645" y="176" text-anchor="middle">vérifie / déchiffre</text>
      <path class="path-base" d="M735 163 H783"/>
      <path class="path-green" d="M735 163 H783"/>
      <rect class="box-green" x="783" y="65" width="175" height="150" rx="13"/>
      <text class="label green-text" x="870" y="91" text-anchor="middle">LAN B</text>
      <text x="870" y="115" text-anchor="middle">192.168.20.0/24</text>
      <rect class="box" x="804" y="135" width="132" height="55" rx="8"/>
      <text x="870" y="158" text-anchor="middle">PC / serveur</text>
      <text class="small" x="870" y="177" text-anchor="middle">trafic privé</text>
      <text class="small" x="490" y="245" text-anchor="middle">À l’intérieur : adresses privées · Sur Internet : en-têtes externes entre les passerelles</text>
      <text class="small" x="490" y="268" text-anchor="middle">La clé ne circule pas en clair : IKEv2 négocie et authentifie les associations de sécurité.</text>
    </svg>
  </div>
  <div class="ipsec-viz__legend"><span class="ipsec-viz__key"><i class="ipsec-viz__dot ipsec-viz__dot--green"></i>Trafic du LAN</span><span class="ipsec-viz__key"><i class="ipsec-viz__dot"></i>Tunnel protégé</span></div>
  <p class="ipsec-viz__note">Lecture : les segments verts représentent le trafic privé avant chiffrement et après déchiffrement ; le segment bleu représente le transport IPsec entre les passerelles.</p>
</div>



## 2. Les composants fondamentaux : IPsec, IKEv2 et ESP

Ces termes désignent des fonctions différentes. Les confondre rend le dépannage difficile.

### 2.1 IPsec : le cadre de protection

IPsec définit des mécanismes de sécurité pour les datagrammes IP. Il s’appuie notamment sur une politique de sécurité et sur l’état cryptographique associé aux flux protégés. Les politiques déterminent ce qui doit être protégé, contourné ou rejeté. Les associations de sécurité décrivent la façon dont un paquet sera protégé ou vérifié.

IPsec peut utiliser différents protocoles de sécurité. Dans les VPN contemporains, ESP est très courant parce qu’il peut fournir confidentialité, intégrité et authentification selon les algorithmes choisis. AH existe dans les standards, mais il est rarement pratique pour un VPN traversant des dispositifs NAT, car les modifications des en-têtes IP peuvent entrer en conflit avec ses vérifications.

### 2.2 IKEv2 : négocier et maintenir l’état de sécurité

IKEv2 signifie Internet Key Exchange version 2. Il est utilisé pour authentifier les pairs, effectuer un échange de clés, négocier les algorithmes et établir des associations de sécurité. Il contribue aussi au renouvellement des clés, aux suppressions de SA et à certains échanges d’information.

IKEv2 n’est pas le protocole qui transporte directement chaque paquet utilisateur à l’intérieur du tunnel. Il négocie l’état qui permet ensuite à IPsec/ESP de protéger les données. Il fonctionne généralement sur UDP 500. Lorsque la traversée NAT est activée, les communications IKE et ESP encapsulées utilisent couramment UDP 4500.

### 2.3 ESP : protéger les paquets de données

ESP signifie Encapsulating Security Payload. C’est le protocole de protection utilisé pour transporter les données IP de manière sécurisée. Selon la transformation négociée, ESP peut chiffrer la charge utile et vérifier son intégrité et son authenticité. Les suites AEAD comme AES-GCM combinent chiffrement et authentification. Certaines suites plus anciennes utilisent une transformation de chiffrement accompagnée d’une fonction d’intégrité distincte.

ESP intègre également un numéro de séquence pour chaque paquet et peut utiliser une fenêtre anti-rejeu. Un paquet en double ou qui arrive en dehors de la fenêtre acceptée peut être rejeté, selon la configuration et l’état du pair. Cette protection n’est pas une correction universelle des paquets réordonnés : il faut que les mécanismes et paramètres des deux extrémités soient compatibles.

### Schéma 3 — Ce qu’ESP apporte à un paquet

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">ESP protège la charge utile selon les algorithmes négociés</p>
  <p class="ipsec-viz__caption">ESP peut fournir confidentialité, intégrité et authentification des données, ainsi qu’une protection contre le rejeu via des numéros de séquence et une fenêtre anti-rejeu.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 300" role="img" aria-label="Schéma d’un paquet IPsec ESP avec en-tête IP externe, SPI et numéro de séquence ESP, données protégées, padding, Next Header et données d’authentification.">
      <text class="label" x="490" y="30" text-anchor="middle">Paquet transmis en mode tunnel (vue simplifiée)</text>
      <rect class="box" x="25" y="78" width="150" height="96" rx="8"/>
      <text class="label" x="100" y="108" text-anchor="middle">IP externe</text>
      <text class="small" x="100" y="132" text-anchor="middle">source = pair A</text>
      <text class="small" x="100" y="151" text-anchor="middle">dest. = pair B</text>
      <rect class="box-blue" x="182" y="78" width="155" height="96" rx="8"/>
      <text class="label" x="259" y="108" text-anchor="middle">En-tête ESP</text>
      <text class="small" x="259" y="132" text-anchor="middle">SPI + séquence</text>
      <text class="small" x="259" y="151" text-anchor="middle">choix de la SA</text>
      <rect class="box-green" x="344" y="78" width="330" height="96" rx="8"/>
      <text class="label green-text" x="509" y="107" text-anchor="middle">Données protégées</text>
      <text x="509" y="131" text-anchor="middle">Paquet IP intérieur</text>
      <text class="small" x="509" y="151" text-anchor="middle">charge chiffrée + padding + Next Header</text>
      <rect class="box-amber" x="681" y="78" width="270" height="96" rx="8"/>
      <text class="label amber-text" x="816" y="108" text-anchor="middle">Tag / intégrité</text>
      <text class="small" x="816" y="132" text-anchor="middle">selon la transformation</text>
      <text class="small" x="816" y="151" text-anchor="middle">GCM : chiffrement authentifié</text>
      <path class="path-animated" d="M35 210 H944"/>
      <circle class="packet" cx="70" cy="210" r="6"/>
      <circle class="packet" cx="130" cy="210" r="6" style="animation-delay:.3s"/>
      <circle class="packet" cx="190" cy="210" r="6" style="animation-delay:.6s"/>
      <circle class="packet" cx="250" cy="210" r="6" style="animation-delay:.9s"/>
      <text class="small" x="490" y="246" text-anchor="middle">L’ESP exact varie selon la suite cryptographique ; le tag n’est pas toujours un champ séparé de la même façon.</text>
      <text class="small" x="490" y="268" text-anchor="middle">L’en-tête IP externe reste visible pour le routage. En mode tunnel, l’en-tête IP intérieur est protégé.</text>
    </svg>
  </div>
  <p class="ipsec-viz__note">ESP est le protocole IP 50 quand il est transporté directement sur IP. Avec NAT-T, ESP est encapsulé dans UDP, généralement sur le port 4500.</p>
</div>



### 2.4 Une Security Association (SA)

Une Security Association est un ensemble de paramètres qui indique comment protéger ou interpréter un flux de paquets. Elle inclut notamment un identifiant appelé SPI, des paramètres cryptographiques, des clés et un état de séquence. Une SA ESP protège généralement le trafic dans un seul sens. Une communication bidirectionnelle utilise donc normalement une SA sortante et une SA entrante, et les pairs gèrent les états correspondants.

Il existe deux niveaux qu’il ne faut pas mélanger :

- **IKE SA** : protège les échanges de contrôle IKE entre les deux pairs et établit le contexte nécessaire aux négociations suivantes.
- **Child SA** : transporte le trafic protégé par ESP (ou AH dans des cas spécifiques). Elle est créée après la négociation IKE initiale et peut être renouvelée sans refaire toute l’authentification du pair.

Une sortie d’état peut donc montrer une IKE SA établie mais aucune Child SA exploitable. Le pair a pu être authentifié, alors que les sélecteurs ou les propositions ESP ne correspondent pas. De même, des SA actives ne garantissent pas que les routes envoient le trafic voulu vers le dispositif VPN.

### 2.5 Identité et clés : deux méthodes communes

La preuve d’identité peut utiliser une clé prépartagée (PSK) ou des certificats avec une infrastructure à clés publiques (PKI). Une PSK est une valeur secrète configurée aux deux extrémités. Elle doit être unique au tunnel, suffisamment robuste et stockée de façon protégée. Elle ne doit jamais être copiée dans un document de cours partagé ni publiée dans un dépôt Git.

Les certificats permettent de lier une identité à une clé publique selon les règles de validation d’une PKI. Leur usage demande de gérer les autorités de certification, les dates de validité, les noms attendus, la révocation selon les capacités de la solution et le renouvellement. Les certificats facilitent souvent l’exploitation d’un grand nombre de pairs, mais ne sont pas automatiquement plus sûrs si la validation des identités est mal configurée.

> **Danger :** une PSK affichée dans une capture, un terminal partagé ou un dépôt devient une information compromise. Utilise des valeurs fictives dans les cours, remplace-les avant un laboratoire réel et fais tourner le secret s’il a été exposé.

## 3. Les échanges IKEv2 en mots simples

La négociation IKEv2 commence habituellement par deux échanges principaux. Les messages transportés sur le réseau peuvent être retransmis en cas de perte ; la description ci-dessous est une vue pédagogique des objectifs, pas une liste exhaustive de champs de protocole.

### 3.1 IKE_SA_INIT : établir le socle cryptographique

Pendant IKE_SA_INIT, l’initiateur propose des suites cryptographiques et les deux pairs réalisent les éléments nécessaires à l’échange de clés, généralement avec Diffie-Hellman. Ils contribuent également des valeurs aléatoires appelées nonces. Les nonces et le secret partagé calculé permettent de dériver les clés qui protègent les échanges IKE.

Le fait qu’un pair accepte une proposition ne prouve pas encore que l’identité distante est autorisée. À cette étape, les pairs se mettent en place pour protéger l’échange d’authentification à venir. Des incompatibilités de chiffrement, d’intégrité, de fonction pseudo-aléatoire ou de groupe Diffie-Hellman peuvent faire échouer cette étape.

L’échange de clés Diffie-Hellman n’envoie pas la clé finale en clair. Il permet aux deux côtés, à partir de paramètres publics et de leur valeur privée respective, de calculer un secret commun. La sécurité repose aussi sur la robustesse des groupes, des algorithmes et de la mise en œuvre.

### 3.2 IKE_AUTH : prouver les identités

IKE_AUTH transporte les éléments d’authentification et les paramètres qui permettent de négocier la première Child SA. Selon le choix retenu, les pairs valident la preuve liée à leur PSK ou à leur certificat. Ils échangent aussi des éléments de politique, dont les Traffic Selectors (TS), qui définissent les flux concernés.

Une erreur d’identité peut empêcher la négociation même si la clé ou le mot de passe semble correct. Par exemple, le profil local peut attendre une adresse IP comme identité distante tandis que le pair présente un FQDN, ou le certificat peut ne pas correspondre au nom configuré. Il faut vérifier l’identité effectivement utilisée, pas seulement l’adresse publique.

### 3.3 Après la mise en place initiale

Une fois la IKE SA et une Child SA actives, ESP peut protéger les paquets correspondant aux sélecteurs et aux politiques locales. IKEv2 peut ensuite créer de nouvelles Child SA, renouveler les clés, supprimer une SA ou transporter des informations de gestion. Les deux extrémités n’ont pas nécessairement les mêmes textes de journalisation, même lorsqu’elles décrivent la même erreur.

### Schéma 2 — Les deux échanges initiaux IKEv2

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">IKEv2 met d’accord les deux pairs avant le transport des données</p>
  <p class="ipsec-viz__caption">Les messages initiaux se déroulent en deux échanges logiques : IKE_SA_INIT, puis IKE_AUTH. Une première Child SA IPsec est généralement établie pendant l’authentification initiale.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 350" role="img" aria-label="Chronologie IKEv2 : propositions cryptographiques et échange Diffie-Hellman, puis authentification des identités et création de la Child SA.">
      <text class="label blue-text" x="220" y="35" text-anchor="middle">Initiateur A</text>
      <text class="label green-text" x="760" y="35" text-anchor="middle">Répondeur B</text>
      <path class="path-base" d="M220 50 V319"/>
      <path class="path-base" d="M760 50 V319"/>
      <g class="step">
        <rect class="box-blue" x="48" y="65" width="310" height="61" rx="9"/>
        <text class="label" x="203" y="88" text-anchor="middle">1. IKE_SA_INIT →</text>
        <text class="small" x="203" y="109" text-anchor="middle">algorithmes, DH, nonces</text>
        <path class="path-animated" d="M360 96 H625"/>
        <polygon points="617,89 631,96 617,103" fill="#60a5fa"/>
      </g>
      <g class="step step-2">
        <rect class="box-green" x="620" y="137" width="310" height="61" rx="9"/>
        <text class="label" x="775" y="160" text-anchor="middle">← 2. IKE_SA_INIT</text>
        <text class="small" x="775" y="181" text-anchor="middle">choix retenu, DH, nonce</text>
        <path class="path-green" d="M620 168 H360"/>
        <polygon points="368,161 354,168 368,175" fill="#4ade80"/>
      </g>
      <g class="step step-3">
        <rect class="box-blue" x="48" y="210" width="310" height="61" rx="9"/>
        <text class="label" x="203" y="233" text-anchor="middle">3. IKE_AUTH →</text>
        <text class="small" x="203" y="254" text-anchor="middle">identité, preuve, sélecteurs</text>
        <path class="path-animated" d="M360 241 H625"/>
        <polygon points="617,234 631,241 617,248" fill="#60a5fa"/>
      </g>
      <g class="step step-4">
        <rect class="box-green" x="620" y="282" width="310" height="52" rx="9"/>
        <text class="label" x="775" y="303" text-anchor="middle">← IKE_AUTH</text>
        <text class="small" x="775" y="321" text-anchor="middle">authentification et Child SA</text>
        <path class="path-green" d="M620 306 H360"/>
        <polygon points="368,299 354,306 368,313" fill="#4ade80"/>
      </g>
    </svg>
  </div>
  <p class="ipsec-viz__note">Les animations mettent en évidence l’ordre des étapes. Dans la réalité, IKEv2 utilise des messages précis et des temporisations ; le dessin reste une vue pédagogique, pas une capture de paquet.</p>
</div>



### 3.4 Pourquoi « IKE est up » ne suffit pas

Il faut examiner plusieurs états distincts :

1. **Transport IP vers le pair** : les adresses publiques et le chemin fonctionnent-ils ?
2. **IKE SA** : la négociation et l’authentification du pair sont-elles réussies ?
3. **Child SA** : la proposition ESP, les sélecteurs et les paramètres de données ont-ils été acceptés ?
4. **Trafic protégé** : les paquets attendus sont-ils chiffrés, reçus et déchiffrés ?
5. **Application** : le routage et les règles permettent-ils à l’application de répondre ?

C’est cette séparation qui guide le dépannage. Si l’IKE SA est absente, la vérification commence par les ports, le chemin, les propositions et l’identité. Si IKE est active mais que les compteurs ESP restent à zéro, il faut examiner les sélecteurs, les routes, les ACL et la génération de trafic. Si les compteurs sortants augmentent mais pas les entrants, le problème peut se trouver dans le chemin retour, les règles amont ou la configuration distante.

> **Piège :** ne supprime pas toutes les SA dès qu’une application ne répond pas. Une suppression d’état peut interrompre d’autres flux et effacer des indices utiles. Collecte d’abord les compteurs, l’état et les journaux.

## 4. Les modes IPsec : tunnel et transport

### 4.1 Mode tunnel

En mode tunnel, le paquet IP original est encapsulé dans un nouveau paquet IP. L’en-tête extérieur indique les adresses des extrémités du tunnel, souvent les adresses publiques des passerelles. Le paquet intérieur contient les adresses des systèmes des réseaux privés. ESP protège le paquet intérieur, de sorte que l’observateur extérieur ne voit pas directement les adresses IP internes dans le paquet chiffré.

C’est le mode classique pour un VPN site-à-site entre deux passerelles. Il permet aux machines des réseaux locaux de communiquer sans qu’elles aient elles-mêmes besoin de gérer IPsec. Les passerelles prennent en charge l’encapsulation à l’émission et la validation/décapsulation à la réception.

Le mode tunnel ajoute des octets : un en-tête IP externe, un en-tête ESP, des informations de fin et éventuellement une balise d’authentification. Cela réduit la taille maximale de la charge utile disponible pour une MTU donnée. Les chemins qui tolèrent 1500 octets pour un paquet IP classique peuvent nécessiter une adaptation pour les paquets encapsulés.

### 4.2 Mode transport

En mode transport, l’en-tête IP original reste l’en-tête de routage du paquet. ESP protège la charge utile selon les règles du protocole, sans ajouter une seconde enveloppe IP complète. Ce mode est utilisé dans certains scénarios hôte-à-hôte, ou pour des cas où les deux extrémités IPsec sont les systèmes qui communiquent.

Le mode transport n’est pas simplement « meilleur » parce qu’il ajoute moins d’en-têtes. Le choix dépend du type de connexion, du comportement attendu des équipements, de l’architecture et de la politique de sécurité. Pour un premier laboratoire de réseaux entre deux sous-réseaux distincts, le mode tunnel est le plus facile à visualiser.

### Schéma 4 — Mode tunnel et mode transport

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">Le mode indique quelles parties du paquet sont enveloppées par IPsec</p>
  <p class="ipsec-viz__caption">Le mode tunnel est très courant entre passerelles de sites. Le mode transport protège principalement la charge utile IP d’une communication entre les hôtes IPsec.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 350" role="img" aria-label="Comparaison des modes tunnel et transport à l'aide de blocs séparés pour l'en-tête IP et la charge utile.">
      <text class="label blue-text" x="240" y="35" text-anchor="middle">Mode tunnel</text>
      <text class="small" x="240" y="56" text-anchor="middle">nouvel en-tête IP externe</text>
      <rect class="box-blue" x="25" y="82" width="135" height="70" rx="8"/>
      <text x="92" y="110" text-anchor="middle">IP externe</text>
      <text class="small" x="92" y="131" text-anchor="middle">visible</text>
      <rect class="box-green" x="168" y="82" width="145" height="70" rx="8"/>
      <text x="240" y="110" text-anchor="middle">ESP + paquet</text>
      <text class="small" x="240" y="131" text-anchor="middle">intérieur protégé</text>
      <rect class="box" x="321" y="82" width="135" height="70" rx="8"/>
      <text x="388" y="110" text-anchor="middle">Tag ESP</text>
      <text class="small" x="388" y="131" text-anchor="middle">authentification</text>
      <path class="path-animated" d="M35 180 H450"/>
      <text class="small" x="240" y="204" text-anchor="middle">LAN A — passerelle — Internet — passerelle — LAN B</text>
      <line x1="490" y1="30" x2="490" y2="315" stroke="#52525b" stroke-dasharray="4 7"/>
      <text class="label green-text" x="725" y="35" text-anchor="middle">Mode transport</text>
      <text class="small" x="725" y="56" text-anchor="middle">conserve l’en-tête IP du paquet</text>
      <rect class="box-blue" x="530" y="82" width="150" height="70" rx="8"/>
      <text x="605" y="110" text-anchor="middle">IP original</text>
      <text class="small" x="605" y="131" text-anchor="middle">visible</text>
      <rect class="box-green" x="688" y="82" width="150" height="70" rx="8"/>
      <text x="763" y="110" text-anchor="middle">En-tête ESP</text>
      <text class="small" x="763" y="131" text-anchor="middle">charge protégée</text>
      <rect class="box" x="846" y="82" width="108" height="70" rx="8"/>
      <text x="900" y="110" text-anchor="middle">Données</text>
      <text class="small" x="900" y="131" text-anchor="middle">chiffrées</text>
      <path class="path-green" d="M536 180 H948"/>
      <text class="small" x="725" y="204" text-anchor="middle">Souvent hôte à hôte : l’identité IP originale reste exposée</text>
      <rect class="box" x="115" y="240" width="750" height="62" rx="10"/>
      <text class="label" x="490" y="265" text-anchor="middle">Mémo</text>
      <text x="490" y="286" text-anchor="middle">Tunnel : protège un paquet IP complet dans un nouveau paquet. Transport : protège la charge utile du paquet original.</text>
    </svg>
  </div>
</div>



### 4.3 Comment lire les en-têtes

Dans le mode tunnel, l’adresse de destination de l’en-tête IP externe est la passerelle distante. Le routeur Internet n’a pas besoin de comprendre les adresses IP internes pour acheminer le paquet jusqu’à cette passerelle. Après validation d’ESP, la passerelle distante récupère le paquet intérieur puis le route vers le réseau de destination.

Le contenu ESP n’est pas automatiquement visible pour les outils intermédiaires. Une capture réalisée sur Internet peut montrer l’adresse source/destination externe, ESP ou UDP 4500, les longueurs et les temporisations. Elle ne devrait pas révéler le contenu applicatif qui est correctement chiffré. Une capture réalisée sur le LAN avant chiffrement ou après déchiffrement peut au contraire voir le paquet d’origine.

## 5. UDP 500, UDP 4500, ESP et NAT Traversal

IKEv2 utilise normalement UDP 500. ESP directement sur IP utilise le numéro de protocole IP 50 ; ce n’est ni un port TCP ni un port UDP. Il s’agit d’une différence importante : une règle de pare-feu « autoriser UDP 50 » ne permet pas ESP directement sur IP.

### 5.1 Pourquoi NAT peut compliquer IPsec

Un équipement NAT modifie les adresses IP et souvent les ports TCP/UDP. Certains mécanismes de sécurité utilisent des données associées aux en-têtes ou aux adresses des extrémités. Une transformation NAT peut donc interrompre une session IPsec qui ne prévoit pas cette situation. De nombreux pare-feu et routeurs peuvent laisser passer UDP plus facilement qu’un protocole IP distinct, et certaines configurations ne laissent pas ESP brut traverser la chaîne.

NAT Traversal (NAT-T) permet de transporter ESP dans UDP lorsque la présence d’un NAT est détectée. IKEv2 échange des informations de détection et les deux pairs passent couramment à UDP 4500 pour les communications concernées. IKE et ESP peuvent alors partager le transport UDP 4500 dans des formats distinguables par leur encapsulation.

### Schéma 5 — Détection de NAT et NAT Traversal

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">Quand un NAT est détecté, ESP passe généralement dans UDP</p>
  <p class="ipsec-viz__caption">IKE commence normalement sur UDP 500. Si les pairs détectent un NAT entre eux, les paquets IKE et ESP sont généralement encapsulés sur UDP 4500 afin de traverser l’équipement NAT.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 270" role="img" aria-label="Étapes NAT Traversal : échanges IKE UDP 500, détection du NAT, puis paquets ESP encapsulés dans UDP 4500 à travers le NAT.">
      <rect class="box-blue" x="20" y="72" width="180" height="104" rx="10"/>
      <text class="label blue-text" x="110" y="100" text-anchor="middle">Pair VPN A</text>
      <text x="110" y="126" text-anchor="middle">IKE UDP 500</text>
      <text class="small" x="110" y="150" text-anchor="middle">détection NAT</text>
      <rect class="box-amber" x="250" y="64" width="180" height="120" rx="10"/>
      <text class="label amber-text" x="340" y="92" text-anchor="middle">Routeur NAT</text>
      <text x="340" y="118" text-anchor="middle">modifie IP/UDP</text>
      <text class="small" x="340" y="143" text-anchor="middle">peut gêner ESP brut</text>
      <text class="small" x="340" y="162" text-anchor="middle">garde l’état UDP</text>
      <rect class="box-green" x="480" y="72" width="180" height="104" rx="10"/>
      <text class="label green-text" x="570" y="100" text-anchor="middle">Pair VPN B</text>
      <text x="570" y="126" text-anchor="middle">NAT détecté</text>
      <text class="small" x="570" y="150" text-anchor="middle">passe à UDP 4500</text>
      <path class="path-animated" d="M200 124 H250"/>
      <path class="path-amber" d="M430 124 H480"/>
      <text class="small" x="225" y="104" text-anchor="middle">500</text>
      <text class="small" x="455" y="104" text-anchor="middle">500 / 4500</text>
      <rect class="box" x="700" y="72" width="250" height="104" rx="10"/>
      <text class="label" x="825" y="100" text-anchor="middle">ESP encapsulé dans UDP</text>
      <text x="825" y="126" text-anchor="middle">UDP 4500</text>
      <text class="small" x="825" y="150" text-anchor="middle">traverse le NAT</text>
      <path class="path-green" d="M660 124 H700"/>
      <text class="small" x="490" y="220" text-anchor="middle">Sans NAT-T : ESP directement sur IP (protocole IP 50), sans port TCP ou UDP.</text>
      <text class="small" x="490" y="242" text-anchor="middle">Le comportement dépend des équipements, mais UDP 500 et UDP 4500 sont les ports usuels IKEv2/NAT-T.</text>
    </svg>
  </div>
</div>



### 5.2 Règles de pare-feu à vérifier

Pour un site-à-site fréquent, les règles doivent être étudiées aux frontières réelles du chemin :

| Trafic | Utilité | Port / protocole habituel |
|---|---|---|
| IKEv2 | Négociation de clés et authentification | UDP 500 |
| IKEv2/ESP NAT-T | Traversée NAT | UDP 4500 |
| ESP sans NAT-T | Données IPsec directement sur IP | Protocole IP 50 |
| ICMP nécessaire au diagnostic/PMTUD | Erreurs réseau et MTU | ICMP, selon politique |

Il n’est pas nécessaire d’ouvrir arbitrairement tous les ports entre les réseaux. Les règles entrantes doivent restreindre la source aux adresses des pairs attendus lorsque ces adresses sont stables. Les règles de trafic intérieur doivent elles aussi respecter le besoin métier : permettre uniquement les sous-réseaux et ports applicatifs nécessaires quand l’architecture le permet.

Une règle qui laisse passer UDP 500 peut suffire au début de la négociation IKE, tout en laissant échouer les données si UDP 4500 ou ESP est bloqué. À l’inverse, permettre les ports nécessaires ne résout pas un problème d’identité ou d’algorithme. Les règles du pare-feu et l’état du protocole doivent être évalués séparément.

## 6. Cryptographie : les paramètres sans les mathématiques lourdes

Les deux pairs doivent avoir au moins une suite de paramètres compatible. La négociation ne signifie pas qu’ils prennent automatiquement « le plus sûr » des choix imaginables ; ils doivent choisir parmi les algorithmes proposés et autorisés par leur configuration.

### 6.1 Chiffrement

Le chiffrement transforme le contenu en données inintelligibles pour un observateur dépourvu de clé. Des algorithmes modernes tels qu’AES sont utilisés dans les déploiements IPsec. AES-GCM est une transformation de chiffrement authentifié : elle combine chiffrement et vérification d’intégrité/authenticité du contenu. Des suites AES-CBC plus anciennes peuvent exister dans certaines installations ou pour des contraintes d’interopérabilité, souvent avec une fonction d’intégrité distincte.

Ne choisis pas une suite uniquement parce qu’elle figure dans un ancien exemple de configuration. Vérifie les recommandations de la version logicielle et du constructeur. Évite les algorithmes obsolètes et les configurations qui réduisent inutilement la sécurité pour faire fonctionner un tunnel. La compatibilité doit être recherchée sans réintroduire des choix faibles.

### 6.2 Intégrité et authentification

L’intégrité permet au destinataire de détecter une altération. L’authentification de pair répond à une autre question : « à quelle identité suis-je connecté ? ». Une session peut être chiffrée tout en utilisant une mauvaise politique d’identité ou en authentifiant le mauvais pair. C’est pourquoi la validation des identités et le choix des algorithmes doivent faire partie de la conception.

### 6.3 Diffie-Hellman et dérivation des clés

IKEv2 utilise un échange de clés afin que les pairs calculent un secret commun sans envoyer ce secret directement sur le réseau. Le groupe cryptographique définit les paramètres du calcul. Les valeurs Diffie-Hellman, les nonces et les autres éléments de l’échange participent à la dérivation des clés utilisées pour protéger IKE et établir les clés des Child SA.

Il n’est pas nécessaire de calculer les secrets à la main dans un premier cours. En revanche, il est important de savoir que le groupe DH fait partie de la négociation et que les deux côtés doivent être compatibles. Si un côté n’autorise qu’un groupe et que l’autre n’en propose aucun en commun, la négociation peut échouer avant l’authentification.

### 6.4 Numéros de séquence et rejeu

ESP utilise des numéros de séquence pour repérer certains paquets répétés. Le destinataire maintient un état anti-rejeu et peut rejeter les paquets dupliqués ou trop anciens. Les réseaux peuvent réordonner des paquets, surtout avec plusieurs chemins ; la fenêtre anti-rejeu doit donc fonctionner correctement avec les paramètres et capacités des deux pairs.

> **Astuce :** lorsqu’un journal annonce une erreur de proposition cryptographique, compare les catégories séparément : chiffrement, intégrité, PRF, groupe DH, mode et paramètres ESP. Une longue ligne de configuration est plus facile à contrôler si chaque paramètre est vérifié indépendamment.

## 7. Exemple de laboratoire : deux routeurs site-à-site

Ce laboratoire est volontairement simplifié. Il sert à reconnaître la structure d’une configuration IPsec, pas à être collé sans adaptation dans un réseau de production. La syntaxe IKEv2 dépend de la plateforme et de sa version ; certains équipements préfèrent des interfaces tunnel virtuelles (VTI) alors que d’autres utilisent une crypto map.

### 7.1 Topologie et plan d’adressage

| Élément | Site A | Site B |
|---|---|---|
| LAN local | 192.168.10.0/24 | 192.168.20.0/24 |
| Passerelle LAN | 192.168.10.1 | 192.168.20.1 |
| Adresse publique de laboratoire | 203.0.113.1 | 203.0.113.2 |
| Pair distant | 203.0.113.2 | 203.0.113.1 |
| Réseau à protéger | 192.168.10.0/24 ↔ 192.168.20.0/24 | 192.168.20.0/24 ↔ 192.168.10.0/24 |

Les adresses publiques appartiennent au bloc réservé à la documentation `203.0.113.0/24` ; elles ne doivent pas être utilisées telles quelles comme adresses publiques réelles sur Internet. Dans un simulateur, remplace-les par les adresses de ton laboratoire. Les noms de sous-réseaux doivent être inversés logiquement dans l’ACL du site B : « local » et « distant » ne signifient pas la même chose à chaque extrémité.

Le LAN A génère le trafic destiné au LAN B. Le routage normal doit déjà permettre au trafic d’atteindre la passerelle IPsec de son site. La politique IPsec identifie ensuite le trafic à protéger, selon la méthode de configuration retenue. Si la passerelle n’a pas de route vers le réseau local distant ou si un pare-feu local bloque le trafic, la simple création du tunnel ne rend pas le flux fonctionnel.

### 7.2 Principes à préparer avant les commandes

Avant de configurer, note les paramètres nécessaires :

- l’identité distante que chaque routeur doit accepter ;
- la méthode d’authentification, par exemple une PSK forte pour un simple laboratoire ;
- les algorithmes IKE ;
- les algorithmes ESP ;
- le mode IPsec ;
- les sous-réseaux autorisés ;
- les règles de transport entre les deux adresses publiques ;
- les routes de retour ;
- les limites éventuelles de NAT et de MTU.

Deux pairs doivent être compatibles, mais la configuration n’est pas toujours textuellement identique. Les clés locales et distantes, les noms d’identité et les réseaux source/destination sont généralement spécifiques à chaque côté.

### 7.3 Exemple conceptuel Cisco IOS/IOS XE

Les lignes ci-dessous illustrent les principaux blocs d’une crypto map IKEv2. Elles utilisent des valeurs de documentation. La syntaxe exacte et le support des algorithmes varient selon le modèle et la version logicielle. Pour un nouveau déploiement, consulte les recommandations cryptographiques de ta plateforme et privilégie une suite moderne prise en charge, par exemple une transformation ESP AEAD telle qu’AES-GCM si elle correspond aux exigences d’interopérabilité.

Exemple de site A :

```text
! Exemple de laboratoire uniquement
! Ne pas réutiliser de secret de production dans un cours ou un dépôt.
crypto ikev2 proposal IKEV2-PROP
 encryption aes-cbc-256
 integrity sha256
 group 14

crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROP

crypto ikev2 keyring IKEV2-KEYRING
 peer SITE-B
  address 203.0.113.2
  pre-shared-key local <SECRET_SITE_A>
  pre-shared-key remote <SECRET_SITE_B>

crypto ikev2 profile IKEV2-PROFILE
 match identity remote address 203.0.113.2 255.255.255.255
 authentication local pre-share
 authentication remote pre-share
 keyring local IKEV2-KEYRING

crypto ipsec transform-set ESP-SET esp-aes 256 esp-sha256-hmac
 mode tunnel

ip access-list extended VPN-TRAFFIC
 permit ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255

crypto map VPN-MAP 10 ipsec-isakmp
 set peer 203.0.113.2
 set ikev2-profile IKEV2-PROFILE
 set transform-set ESP-SET
 match address VPN-TRAFFIC

interface GigabitEthernet0/0
 crypto map VPN-MAP
```

Cette configuration n’est pas un bloc universel prêt à exécuter. Certaines versions utilisent une syntaxe différente pour les profils ou les clés, certains systèmes ont besoin d’un paramètre d’authentification différent, et une suite AES-GCM peut nécessiter d’autres lignes que l’exemple CBC/HMAC ci-dessus. Vérifie la documentation de la version avant de reprendre ces commandes. Le choix d’une PSK n’est approprié ici que pour présenter la structure ; une PKI est généralement plus facile à gérer lorsqu’il existe beaucoup de pairs.

> **Danger :** ne colle pas un exemple de cours dans un routeur de production sans sauvegarde, revue et plan de retour arrière. Les commandes d’une crypto map et les ACL associées peuvent détourner ou interrompre du trafic existant. Les adresses d’exemple et les secrets entre chevrons doivent être remplacés.

### 7.4 Ce que doit contenir le côté B

Le site B doit connaître l’adresse du pair A et l’identité qu’il attend. Il doit autoriser les réseaux dans le sens inverse, c’est-à-dire le LAN B vers le LAN A, et appliquer la politique sur l’interface appropriée. Les deux côtés doivent négocier des paramètres compatibles.

La proposition IKE, le profil, le keyring, la transform-set, l’ACL et la crypto map constituent des blocs distincts. S’il existe une configuration NAT qui masque les adresses internes, il faudra peut-être exclure le trafic VPN de la traduction d’adresses, selon la plateforme et l’ordre de traitement. Dans d’autres architectures, une politique ou un profil de tunnel gère le trafic d’une manière différente. Ne transpose pas la méthode crypto map vers une VTI sans adapter la logique de routage.

### 7.5 Politique de filtrage et accès minimal

Le fait que le tunnel soit chiffré ne veut pas dire que tous les ports entre les sites doivent être ouverts. Si les employés du site A n’ont besoin que d’accéder à un service applicatif du site B, la politique de sécurité doit limiter l’accès à ce service quand c’est possible. Les sous-réseaux sont une première barrière ; les règles de pare-feu côté LAN permettent souvent une politique plus précise.

Un tunnel IPsec peut devenir un chemin de contournement si les réseaux distants sont considérés comme entièrement fiables. Il faut appliquer les mêmes exigences de segmentation, de supervision et de moindre privilège aux flux reçus par le tunnel qu’aux flux d’un réseau interne classique. Les journaux doivent permettre de savoir qui communique, vers quelle destination et selon quelle règle, sans exposer inutilement les secrets cryptographiques.

## 8. Routage, NAT et sélecteurs

### 8.1 Politique de trafic

Dans une approche policy-based, une ACL ou une politique indique quels paquets doivent être protégés. L’ACL ne chiffre pas à elle seule le paquet ; elle sélectionne le trafic associé à la politique IPsec. Dans une approche route-based avec VTI, le tunnel a une interface logique et le routage dirige les préfixes attendus vers cette interface. Les détails varient selon les constructeurs, mais la question fondamentale est toujours : **quel mécanisme identifie le trafic qui entre dans IPsec ?**

Une erreur de sélecteur peut provoquer un tunnel sans transport de données. Par exemple, le site A propose `192.168.10.0/24` vers `192.168.20.0/24`, alors que le site B attend `192.168.20.0/24` vers un autre sous-réseau. IKE peut parvenir à authentifier les pairs, mais la création de la Child SA peut échouer ou les paquets voulus peuvent ne pas correspondre à la politique.

### Schéma 7 — Choix de sélecteurs de trafic

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">Le chiffrement ne protège que le trafic correspondant à la politique</p>
  <p class="ipsec-viz__caption">Les Traffic Selectors et la politique locale définissent quels flux peuvent être associés à une Child SA. Des sélecteurs qui ne correspondent pas des deux côtés peuvent empêcher le tunnel de transporter le flux attendu.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 285" role="img" aria-label="Des flux provenant d'un LAN sont comparés aux sélecteurs réseau. Le trafic correspondant passe dans l'association ESP, les autres flux ne l'utilisent pas.">
      <rect class="box" x="20" y="76" width="180" height="132" rx="10"/>
      <text class="label" x="110" y="104" text-anchor="middle">Flux sortants</text>
      <text class="small" x="110" y="130" text-anchor="middle">192.168.10.10 →</text>
      <text class="small" x="110" y="151" text-anchor="middle">192.168.20.20</text>
      <text class="small" x="110" y="178" text-anchor="middle">et autres destinations</text>
      <path class="path-animated" d="M200 140 H265"/>
      <rect class="box-blue" x="265" y="65" width="210" height="152" rx="10"/>
      <text class="label blue-text" x="370" y="93" text-anchor="middle">Politique / sélecteurs</text>
      <text x="370" y="121" text-anchor="middle">local : 192.168.10.0/24</text>
      <text x="370" y="145" text-anchor="middle">distant : 192.168.20.0/24</text>
      <text class="small" x="370" y="177" text-anchor="middle">adresse, protocole, ports</text>
      <path class="path-green" d="M475 117 H560"/>
      <path class="path-amber" d="M475 180 H560"/>
      <rect class="box-green" x="560" y="76" width="180" height="76" rx="9"/>
      <text class="label green-text" x="650" y="103" text-anchor="middle">Correspondance</text>
      <text x="650" y="126" text-anchor="middle">Child SA ESP</text>
      <rect class="box-amber" x="560" y="164" width="180" height="55" rx="9"/>
      <text class="label amber-text" x="650" y="187" text-anchor="middle">Hors sélecteurs</text>
      <text class="small" x="650" y="207" text-anchor="middle">autre politique / route</text>
      <path class="path-green" d="M740 114 H795"/>
      <rect class="box" x="795" y="76" width="160" height="76" rx="9"/>
      <text class="label" x="875" y="103" text-anchor="middle">Chiffrement</text>
      <text class="small" x="875" y="126" text-anchor="middle">flux autorisé</text>
      <path class="path-base" d="M740 191 H795"/>
      <rect class="box" x="795" y="164" width="160" height="55" rx="9"/>
      <text class="small" x="875" y="187" text-anchor="middle">pas dans cette SA</text>
      <text class="small" x="490" y="252" text-anchor="middle">Le bon état IKE n’assure pas à lui seul que les routes, ACL, NAT et sélecteurs autorisent le flux souhaité.</text>
    </svg>
  </div>
</div>



### 8.2 NAT et exclusion du trafic interne

Dans une configuration site-à-site, le trafic vers le réseau distant doit généralement conserver des adresses source/destination correspondant à la politique IPsec. Si une règle NAT traduit ces adresses avant que la politique IPsec ne les sélectionne, le trafic peut ne plus correspondre aux sélecteurs. Certaines plateformes traitent des exceptions NAT spéciales avant la crypto map ; d’autres ont une logique différente. Il faut comprendre l’ordre de traitement exact de l’équipement utilisé.

### 8.3 Routage aller et retour

Le trafic doit disposer d’une route dans les deux sens. Un paquet peut entrer dans le tunnel, être déchiffré, puis être abandonné par un filtre ou renvoyé vers une mauvaise passerelle. Un test à sens unique n’est pas une preuve de connectivité complète. Il faut tester de A vers B puis de B vers A, et examiner à la fois les compteurs IPsec et les journaux du pare-feu.

### 8.4 MTU et MSS

Chaque encapsulation ajoute de l’en-tête. Si la MTU disponible sur le chemin est inférieure à la taille du paquet encapsulé, des paquets peuvent être fragmentés ou rejetés. Le problème se remarque parfois sous la forme de petits pings qui réussissent, mais de transferts HTTPS ou de copie de fichiers qui se bloquent.

Le PMTUD (Path MTU Discovery) s’appuie sur des messages de contrôle afin d’ajuster la taille des paquets. Si les messages ICMP nécessaires sont bloqués, le système peut garder une taille inadaptée. Certains équipements appliquent un ajustement MSS pour TCP. Il faut valider les valeurs avec des tests et une capture réseau plutôt que d’appliquer une valeur arbitraire.

## 9. Durée de vie des SA, renouvellement et stabilité

Une SA n’est pas destinée à rester indéfiniment avec les mêmes clés. Les durées de vie et le renouvellement permettent de renouveler les clés et l’état cryptographique. IKEv2 peut créer une nouvelle Child SA, puis transférer progressivement l’usage à la nouvelle SA. L’ancienne SA est ensuite supprimée lorsque les conditions prévues par l’implémentation sont remplies.

Il faut distinguer la durée de vie de l’IKE SA de celle des Child SA. Les deux ne sont pas nécessairement identiques. Certaines plateformes parlent de rekey, d’autres d’expiration de SA, et les journaux peuvent montrer des minuteries distinctes. Si une session tombe régulièrement à intervalle fixe, vérifie les durées de vie, la synchronisation, le rekey, la stabilité de transport et les journaux aux deux extrémités.

### Schéma 6 — La vie d’une Security Association

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">Les SA sont créées, utilisées, renouvelées puis supprimées</p>
  <p class="ipsec-viz__caption">IKE SA et Child SA sont des états distincts. Le renouvellement permet de remplacer les clés avant expiration, sans attendre une interruption prolongée.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 245" role="img" aria-label="Cycle de vie d'une association de sécurité : négociation, établissement, chiffrement des données, rekey, basculement et suppression.">
      <path class="path-animated" d="M145 108 H235 M375 108 H465 M605 108 H695 M835 108 H903"/>
      <polygon points="228,101 242,108 228,115" fill="#60a5fa"/>
      <polygon points="458,101 472,108 458,115" fill="#60a5fa"/>
      <polygon points="688,101 702,108 688,115" fill="#60a5fa"/>
      <polygon points="896,101 910,108 896,115" fill="#60a5fa"/>
      <g class="step">
        <rect class="box-blue" x="20" y="70" width="125" height="76" rx="9"/>
        <text class="label" x="82" y="96" text-anchor="middle">Négocier</text>
        <text class="small" x="82" y="119" text-anchor="middle">IKE_SA_INIT</text>
      </g>
      <g class="step step-2">
        <rect class="box-green" x="235" y="70" width="140" height="76" rx="9"/>
        <text class="label" x="305" y="96" text-anchor="middle">Authentifier</text>
        <text class="small" x="305" y="119" text-anchor="middle">IKE_AUTH</text>
      </g>
      <g class="step step-3">
        <rect class="box-blue" x="465" y="70" width="140" height="76" rx="9"/>
        <text class="label" x="535" y="96" text-anchor="middle">Protéger</text>
        <text class="small" x="535" y="119" text-anchor="middle">Child SA ESP</text>
      </g>
      <g class="step step-4">
        <rect class="box-amber" x="695" y="70" width="140" height="76" rx="9"/>
        <text class="label" x="765" y="96" text-anchor="middle">Rekey</text>
        <text class="small" x="765" y="119" text-anchor="middle">nouvelle SA</text>
      </g>
      <rect class="box" x="840" y="70" width="125" height="76" rx="9"/>
      <text class="label" x="902" y="96" text-anchor="middle">Supprimer</text>
      <text class="small" x="902" y="119" text-anchor="middle">fin de session</text>
      <text x="490" y="188" text-anchor="middle">Les SA ESP sont unidirectionnelles : les deux sens du trafic utilisent généralement des SA différentes.</text>
      <text class="small" x="490" y="210" text-anchor="middle">Ne pas confondre durée de vie de l’IKE SA, durée de vie des Child SA et temporisations de rekey propres au constructeur.</text>
    </svg>
  </div>
</div>



Une reconnexion fréquente peut aussi être liée à des pertes de paquets, un changement d’adresse publique, une expiration d’état NAT ou à un pare-feu intermédiaire. Une observation ponctuelle ne suffit pas à établir la cause. Il faut corréler les logs IKE, les compteurs ESP et le trafic réseau aux instants précis où le tunnel change d’état.

> **Astuce :** note l’heure exacte de chaque baisse de tunnel, ainsi que la dernière négociation réussie. La corrélation des deux pairs autour du même horodatage est souvent beaucoup plus utile qu’une capture de configuration seule.

## 10. Vérification sur un équipement Cisco

Les commandes disponibles changent selon le modèle et la version. Les familles de commandes suivantes sont souvent utiles pour comprendre l’état des négociations et des paquets :

```text
show crypto ikev2 sa
show crypto ipsec sa
show crypto session detail
show access-lists
show ip route
show interfaces
show logging
```

- `show crypto ikev2 sa` : montre les sessions IKEv2 connues et leur état.
- `show crypto ipsec sa` : donne des informations sur les associations ESP et les compteurs de paquets.
- `show crypto session detail` : donne une vue synthétique des sessions selon les fonctions disponibles.
- `show access-lists` : permet de voir les règles et parfois les compteurs correspondants.
- `show ip route` : vérifie le chemin vers le pair et vers les préfixes distants.
- `show interfaces` : fournit l’état d’interface, les erreurs et les compteurs.
- `show logging` : rassemble les événements récents utiles au diagnostic.

Dans `show crypto ipsec sa`, compare notamment les paquets encapsulés/chiffrés et les paquets décapsulés/déchiffrés. Si le compteur sortant augmente, mais que le compteur entrant reste nul, l’autre extrémité peut ne pas envoyer de retour, le trajet retour peut être bloqué ou le paquet peut être rejeté avant l’arrivée. Si aucun compteur ne bouge alors que l’application génère du trafic, examine d’abord le routage, les sélecteurs et l’emplacement de la crypto map.

### 10.1 Quatre observations classiques

| Observation | Pistes à vérifier |
|---|---|
| Aucune IKE SA | Transport IP, UDP 500, identité du pair, politique IKE, NAT et ACL de bordure |
| IKE SA présente, Child SA absente | Paramètres ESP, sélecteurs, identité, règles de négociation |
| ESP sortant augmente, entrant reste à zéro | Pair distant, route retour, pare-feu amont, NAT et chemin retour |
| Compteurs des deux sens augmentent, application en échec | Pare-feu LAN, routage interne, DNS, MTU/MSS, règle applicative |

Ces observations sont des indices, pas des diagnostics automatiques. Une interface peut utiliser d’autres noms de compteurs ou des mécanismes d’accélération matérielle qui modifient la façon dont les statistiques sont présentées. Collecte les données de chaque côté avant de conclure.

### 10.2 Les commandes de debug

Les commandes de debug cryptographique peuvent générer beaucoup de messages et consommer des ressources, surtout sous forte charge. Elles doivent être utilisées avec prudence et uniquement quand elles sont disponibles et comprises pour la version concernée. Dans un réseau de production, privilégie d’abord l’état des SA, les compteurs et les journaux de niveau approprié. Si un debug est nécessaire, limite sa durée, documente les commandes exécutées et arrête-le dès que les informations utiles ont été collectées.

> **Danger :** ne publie pas une sortie de debug sans la relire. Elle peut inclure des identités internes, des adresses publiques, des noms de profils et d’autres informations opérationnelles sensibles. Les clés correctement mises en œuvre ne doivent pas apparaître en clair, mais il ne faut jamais supposer qu’une sortie est automatiquement sans risque.

## 11. Dépannage pas à pas

### Schéma 8 — Dépanner sans deviner

<div class="ipsec-viz">
  <p class="ipsec-viz__heading">Trouver la première étape qui échoue</p>
  <p class="ipsec-viz__caption">Commence par vérifier la connectivité et les politiques, puis sépare l’établissement IKE de la création de la Child SA et du passage des paquets.</p>
  <div class="ipsec-viz__scroll">
    <svg class="ipsec-viz__svg" viewBox="0 0 980 330" role="img" aria-label="Arbre de dépannage IPsec : connectivité, IKE SA, Child SA, compteurs ESP puis routage et MTU. Chaque échec oriente vers une famille de vérifications.">
      <rect class="box-blue" x="355" y="16" width="270" height="47" rx="9"/>
      <text class="label" x="490" y="45" text-anchor="middle">1. IP publique joignable ?</text>
      <path class="path-animated" d="M490 63 V88"/>
      <rect class="box" x="340" y="88" width="300" height="47" rx="9"/>
      <text class="label" x="490" y="117" text-anchor="middle">2. IKE SA établie ?</text>
      <path class="path-animated" d="M490 135 V160"/>
      <rect class="box" x="340" y="160" width="300" height="47" rx="9"/>
      <text class="label" x="490" y="189" text-anchor="middle">3. Child SA / ESP présente ?</text>
      <path class="path-animated" d="M490 207 V232"/>
      <rect class="box-green" x="340" y="232" width="300" height="47" rx="9"/>
      <text class="label green-text" x="490" y="261" text-anchor="middle">4. Compteurs ESP augmentent ?</text>
      <path class="path-green" d="M640 111 H735"/>
      <rect class="box-amber" x="735" y="88" width="225" height="47" rx="9"/>
      <text class="label amber-text" x="847" y="117" text-anchor="middle">Ports 500/4500, PSK, ID</text>
      <path class="path-green" d="M640 183 H735"/>
      <rect class="box-amber" x="735" y="160" width="225" height="47" rx="9"/>
      <text class="label amber-text" x="847" y="189" text-anchor="middle">Propositions, sélecteurs</text>
      <path class="path-green" d="M640 255 H735"/>
      <rect class="box-amber" x="735" y="232" width="225" height="47" rx="9"/>
      <text class="label amber-text" x="847" y="261" text-anchor="middle">ACL, NAT, route, MTU</text>
      <text class="small" x="490" y="309" text-anchor="middle">Collecter l’état et les compteurs avant de modifier la configuration.</text>
    </svg>
  </div>
  <p class="ipsec-viz__note">Cet arbre est un ordre de triage, pas un ordre absolu : certains équipements affichent des états et des compteurs différents.</p>
</div>


### Étape 1 — Confirmer le besoin et le chemin

Avant de modifier le VPN, définis le flux exact : adresse source, adresse destination, protocole, ports applicatifs et sens de la connexion. Vérifie que les deux machines existent et que les interfaces des passerelles sont opérationnelles. Le test doit être réalisé depuis les bons hôtes ; un ping lancé depuis la passerelle ne reproduit pas nécessairement la même politique que le trafic utilisateur.

### Étape 2 — Vérifier l’atteignabilité des pairs

Les adresses publiques doivent être routables entre elles. Des ACL amont ou un pare-feu Internet peuvent bloquer UDP 500/4500 ou ESP direct. Si le pair est derrière un NAT, confirme que les règles de redirection et la détection NAT sont cohérentes. Vérifie les logs de bordure et les compteurs plutôt que de présumer que « l’Internet fonctionne ».

### Étape 3 — Séparer IKE de Child SA

Lis l’état IKE et les messages d’échec. Si l’échec apparaît au cours de la proposition, compare les algorithmes et groupes autorisés. Si IKE arrive jusqu’à l’authentification puis échoue, vérifie l’identité, la PSK ou la validation du certificat. Si IKE est active et que la Child SA ne l’est pas, compare les paramètres ESP et les Traffic Selectors.

### Étape 4 — Vérifier les compteurs ESP

Génère un trafic contrôlé depuis un hôte du LAN A vers un hôte du LAN B. Note les compteurs avant le test, puis relis-les. Si les paquets sortants ne progressent pas, la politique n’attrape peut-être pas le trafic. Si les paquets sortent mais que le pair ne les reçoit pas, le problème se situe peut-être sur le chemin externe. Si le pair reçoit et déchiffre, continue l’investigation dans le LAN de destination.

### Étape 5 — Contrôler le retour et les applications

Un serveur de destination doit disposer d’une route de retour vers le réseau source. Le pare-feu local peut refuser le protocole ou le port demandé. DNS peut traduire le nom vers une mauvaise adresse ; une application peut être arrêtée. Une fois ESP confirmé dans les deux sens, élargis le diagnostic au routage interne, au pare-feu et à l’application.

### Étape 6 — Vérifier les gros paquets et les flux longs

Si de petits paquets fonctionnent mais pas les transferts volumineux, soupçonne MTU, PMTUD, fragmentation et MSS. Réalise des tests de taille progressive avec un outil adapté, vérifie les messages ICMP nécessaires et compare la taille des paquets sur le LAN puis sur l’interface externe. Ne modifie la MSS qu’après avoir établi que la taille du paquet encapsulé est en cause.

### Étape 7 — Corriger une seule hypothèse à la fois

Sauvegarde la configuration, formule la cause supposée et choisis le test qui la confirme. Applique une modification restreinte, puis vérifie les mêmes métriques qu’avant la modification. Si le résultat n’est pas meilleur ou si un effet de bord apparaît, restaure la configuration précédente et reconsidère l’hypothèse.

> **Piège :** changer simultanément la PSK, le groupe DH, les durées de vie, l’ACL et la route peut parfois faire fonctionner le tunnel, mais empêche d’apprendre la vraie cause. Une correction doit être explicable et reproductible.

## 12. Sécurité et exploitation

### 12.1 Protéger les secrets

Utilise des secrets uniques et robustes, des certificats gérés, une méthode de stockage appropriée et des permissions limitées sur la configuration. Les secrets ne doivent pas apparaître dans les fichiers de cours, captures d’écran, tickets ou dépôts Git. Si une PSK est exposée, traite-la comme compromise : évalue son périmètre, renouvelle-la et vérifie qu’elle a été remplacée aux deux extrémités.

### 12.2 Choisir des algorithmes modernes

Les options autorisées doivent suivre les recommandations du constructeur et les standards actuels. Désactive les algorithmes faibles ou obsolètes quand ils ne sont plus requis. Une compatibilité ancienne peut parfois nécessiter une exception temporaire, mais celle-ci doit avoir un propriétaire, une échéance et une justification documentée. Ne laisse pas une proposition très faible activée « au cas où ».

### 12.3 Réduire la confiance accordée au réseau distant

Un réseau distant n’est pas forcément fiable parce qu’il passe dans IPsec. Filtre les flux entre les sites, limite les préfixes annoncés si le routage dynamique est utilisé, journalise les accès importants et surveille les anomalies. Un partenaire ou une agence peut avoir des postes compromis ; le chiffrement protégera le transport de données, mais ne neutralisera pas une machine déjà autorisée.

### 12.4 Supervision

Surveille l’état de l’IKE SA, les Child SA, les durées de vie, les changements de pair, les compteurs d’encapsulation et de décapsulation, les pertes et les alarmes de certificat. Les métriques doivent être corrélées à l’expérience des applications. Un tunnel déclaré « up » mais sans trafic utile ou avec une perte très élevée n’est pas sain.

Une bonne alerte différencie la perte totale du tunnel, un volume de trafic nul inattendu, un nombre élevé d’échecs d’authentification et un problème de performance applicative. Le niveau de gravité dépend du service transporté. La procédure de réponse doit indiquer qui intervient, quelles preuves collecter et comment revenir à un état connu.

### 12.5 Préparer les changements

Une fenêtre de changement doit préciser les équipements concernés, la configuration avant/après, les tests d’acceptation, les conséquences probables et le plan de retour arrière. Les modifications cryptographiques ou les renouvellements de certificats peuvent affecter les deux pairs. Vérifie que tu as un accès d’administration indépendant du tunnel à modifier, lorsqu’il s’agit d’un routeur administré à distance.

## 13. Cas pratiques guidés

### Cas 1 — Le tunnel ne se négocie pas

**Symptôme :** aucune IKE SA n’apparaît sur le site A.

**Hypothèses possibles :** adresse de pair erronée, transport UDP bloqué, mauvais chemin, politique IKE incompatible ou pair distant indisponible.

**Méthode :** vérifier les interfaces, la route vers l’adresse publique distante, les règles de bordure et les journaux IKE. Confirmer que l’adresse du pair et les ports sont corrects. Ne pas commencer par modifier tous les paramètres cryptographiques avant d’avoir vérifié que les échanges atteignent réellement le pair.

**Résultat attendu :** l’équipement montre des tentatives IKE et une cause identifiable si l’échange est refusé. Si aucune tentative n’apparaît à l’autre extrémité, concentrer l’investigation sur le chemin externe.

### Cas 2 — IKE est active, mais la Child SA ne l’est pas

**Symptôme :** l’authentification réussit, mais aucun trafic n’est chiffré pour les sous-réseaux visés.

**Hypothèses possibles :** transform-set incompatible, mode différent, sélecteurs divergents ou politique de trafic incorrecte.

**Méthode :** comparer les propositions ESP et les adresses exactes des réseaux protégés. Vérifier les ACL des deux côtés, l’ordre des règles et les règles de traduction NAT. Confirmer que la Child SA est créée et que les compteurs correspondent au trafic testé.

**Résultat attendu :** la proposition ESP est acceptée et les deux directions ont des SA actives correspondant aux réseaux attendus.

### Cas 3 — Le ping marche, mais une application se bloque

**Symptôme :** les petits paquets fonctionnent, mais un transfert de fichier reste bloqué.

**Hypothèses possibles :** MTU trop élevée pour le chemin encapsulé, ICMP nécessaire à PMTUD filtré, MSS inadéquate ou règle de pare-feu spécifique à l’application.

**Méthode :** vérifier les compteurs IPsec dans les deux sens, tester des tailles progressivement plus grandes, consulter les captures et observer les messages ICMP pertinents. Vérifier ensuite le port applicatif et les règles du pare-feu LAN.

**Résultat attendu :** identifier la taille ou la condition où le flux se dégrade, corriger le mécanisme à l’origine du problème et répéter les tests de connectivité ainsi que le transfert réel.

### Cas 4 — Le tunnel se reconnecte régulièrement

**Symptôme :** la connexion tombe ou renégocie à intervalle stable.

**Hypothèses possibles :** rekey mal coordonné, expiration de SA, changement d’adresse, expiration d’état NAT, perte de paquets ou certificat arrivé à expiration.

**Méthode :** aligner les événements des deux pairs sur une ligne temporelle. Comparer les durées de vie IKE/Child SA, les journaux de rekey, les événements d’interface et les états NAT. Ne pas désactiver la rotation des clés simplement pour masquer le problème.

**Résultat attendu :** associer la coupure à une transition ou à un événement vérifié, puis corriger un paramètre précis.

## 14. Exercices de vérification

Essaie de répondre sans consulter immédiatement les corrigés. Le but est d’apprendre à distinguer l’état du contrôle (IKE) de l’état des données (ESP).

### Questions

1. Quelle est la différence principale entre IKEv2 et ESP ?
2. Pourquoi un tunnel site-à-site utilise-t-il fréquemment le mode tunnel ?
3. Quel transport est généralement utilisé par IKEv2 au démarrage ?
4. Quel est le numéro de protocole IP d’ESP lorsqu’il n’est pas encapsulé dans UDP ?
5. Pourquoi voit-on souvent UDP 4500 sur un tunnel qui traverse un NAT ?
6. Que représente une Child SA et pourquoi le trafic bidirectionnel utilise-t-il normalement des associations dans les deux sens ?
7. L’IKE SA est active, mais la Child SA manque. Quelles familles de paramètres faut-il comparer ?
8. Les compteurs de chiffrement augmentent, mais aucun paquet entrant n’est compté. Que faut-il examiner ?
9. Pourquoi peut-on voir de petits pings fonctionner alors que de gros transferts échouent ?
10. Pourquoi faut-il éviter de modifier cinq paramètres avant d’avoir confirmé une hypothèse ?

### Corrigés

1. IKEv2 authentifie les pairs et négocie les SA ; ESP protège les paquets de données.
2. Le mode tunnel permet d’encapsuler un paquet IP intérieur complet et de relier des réseaux privés à travers les passerelles.
3. UDP 500, puis potentiellement UDP 4500 si NAT Traversal est utilisé.
4. ESP utilise le protocole IP 50. Ce n’est pas un numéro de port.
5. NAT-T encapsule les paquets ESP dans UDP afin de traverser plus facilement les équipements NAT et les pare-feu.
6. La Child SA représente l’état de protection des données. Les SA ESP sont généralement unidirectionnelles, donc chaque sens a son propre état.
7. Transformations ESP, mode, sélecteurs de trafic, profils et politique de négociation.
8. Le pair distant, la route retour, les ACL amont, le NAT et le chemin réseau dans le sens retour.
9. L’encapsulation réduit l’espace disponible dans la MTU. PMTUD, ICMP, fragmentation ou MSS peuvent être en cause.
10. Cela brouille la relation entre cause et effet, empêche de savoir quelle correction a été déterminante et augmente le risque d’effet de bord.

## 15. Checklist de validation d’un VPN IPsec

Avant de déclarer le tunnel opérationnel, vérifie chaque point.

- [ ] Les interfaces et routes vers les pairs publics sont correctes.
- [ ] Les règles de bordure autorisent les échanges IKEv2 requis.
- [ ] Les identités distantes et la méthode d’authentification sont conformes à la politique.
- [ ] Les propositions IKE sont compatibles et utilisent des algorithmes approuvés.
- [ ] Une IKE SA est établie sur les deux pairs.
- [ ] Une Child SA ESP est active et correspond aux sélecteurs prévus.
- [ ] Les compteurs sortants et entrants progressent lors d’un test contrôlé.
- [ ] Le routage et les règles de pare-feu autorisent les applications nécessaires.
- [ ] Le chemin retour est vérifié.
- [ ] Des paquets de taille normale et des transferts applicatifs réussissent.
- [ ] Les événements de rekey sont compris et supervisés.
- [ ] Les secrets ne sont pas présents dans le dépôt ou les documents.
- [ ] La configuration a été sauvegardée et le retour arrière est prêt.
- [ ] Les propriétaires, les préfixes autorisés, les règles et les contacts de support sont documentés.

## Points à retenir

- **IPsec** est un ensemble de mécanismes de protection de paquets IP, et non un simple logiciel de tunnel.
- **IKEv2** négocie les paramètres, authentifie les pairs et maintient les associations de sécurité.
- **ESP** transporte les données protégées et peut apporter chiffrement, intégrité et protection contre le rejeu selon la suite choisie.
- Une **IKE SA** protège le contrôle IKE ; une **Child SA** protège généralement les flux de données. Ne confonds pas les deux.
- Le **mode tunnel** ajoute un en-tête IP externe autour du paquet intérieur ; le **mode transport** conserve l’en-tête IP original.
- **UDP 500** est utilisé couramment pour IKEv2. **UDP 4500** est utilisé pour NAT Traversal. ESP direct est le protocole IP 50.
- Un tunnel actif ne prouve pas que les routes, sélecteurs, ACL, NAT, DNS et applications sont correctement configurés.
- Le dépannage doit suivre une méthode : chemin, IKE, Child SA, compteurs ESP, puis routage et application.
- Une configuration cryptographique sûre doit suivre les recommandations du constructeur et les standards actuels.
- Toute modification doit être testée et assortie d’une procédure de retour arrière.

### Références et lectures complémentaires

- IETF, **RFC 4301 — Security Architecture for the Internet Protocol** : https://www.rfc-editor.org/rfc/rfc4301
- IETF, **RFC 4303 — IP Encapsulating Security Payload (ESP)** : https://www.rfc-editor.org/rfc/rfc4303
- IETF, **RFC 7296 — Internet Key Exchange Protocol Version 2 (IKEv2)** : https://www.rfc-editor.org/rfc/rfc7296
- IETF, **RFC 8247 — Algorithm Implementation Requirements and Usage Guidance for IKEv2** : https://www.rfc-editor.org/rfc/rfc8247
- IETF, **RFC 8221 — Cryptographic Algorithm Implementation Requirements and Usage Guidance for ESP and AH** : https://www.rfc-editor.org/rfc/rfc8221
- NIST, **SP 800-77 Rev. 1 — Guide to IPsec VPNs** : https://csrc.nist.gov/pubs/sp/800/77/r1/final
- Documentation officielle Cisco, guides de configuration IPsec/IKEv2 pour la version IOS/IOS XE effectivement utilisée : https://www.cisco.com/

Les RFC définissent les comportements du protocole ; elles ne garantissent pas que toutes les commandes exposées par une plateforme sont identiques. Pour un équipement réel, vérifie toujours la documentation adaptée à son modèle et à sa version logicielle.
