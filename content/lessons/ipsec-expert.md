# VPN IPsec (IKEv2, ESP) — Expert

<style>
.ipsecx-diagram { width:100%; max-width:100%; overflow:hidden; margin:1.4rem 0 1.8rem; padding:.65rem; border:1px solid #3f3f46; border-radius:1rem; background:#101113; box-sizing:border-box; }
.ipsecx-svg { display:block; width:100%; max-width:100%; min-width:0; height:auto; }
.ipsecx-svg text { fill:#e4e4e7; font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; font-size:13px; }
.ipsecx-svg .x-title { fill:#fafafa; font-size:16px; font-weight:700; }
.ipsecx-svg .x-small { fill:#a1a1aa; font-size:11px; }
.ipsecx-svg .x-cyan { fill:#67e8f9; }
.ipsecx-svg .x-green { fill:#86efac; }
.ipsecx-svg .x-amber { fill:#fcd34d; }
.ipsecx-svg .x-red { fill:#fca5a5; }
.ipsecx-svg .x-card { fill:#18181b; stroke:#52525b; stroke-width:1.4; }
.ipsecx-svg .x-card-blue { fill:#142b3a; stroke:#60a5fa; stroke-width:1.5; }
.ipsecx-svg .x-card-green { fill:#14291e; stroke:#4ade80; stroke-width:1.5; }
.ipsecx-svg .x-card-amber { fill:#302617; stroke:#fbbf24; stroke-width:1.5; }
.ipsecx-svg .x-card-red { fill:#321a20; stroke:#fb7185; stroke-width:1.5; }
.ipsecx-svg .x-line { fill:none; stroke:#71717a; stroke-width:2.4; }
.ipsecx-svg .x-flow { fill:none; stroke:#22d3ee; stroke-width:3; stroke-dasharray:8 10; animation:ipsecx-flow 1.5s linear infinite; }
.ipsecx-svg .x-flow-green { fill:none; stroke:#4ade80; stroke-width:3; stroke-dasharray:7 9; animation:ipsecx-flow 1.1s linear infinite; }
.ipsecx-svg .x-flow-amber { fill:none; stroke:#fbbf24; stroke-width:3; stroke-dasharray:7 9; animation:ipsecx-flow 1.8s linear infinite; }
.ipsecx-svg .x-pulse { transform-box:fill-box; transform-origin:center; animation:ipsecx-pulse 2.2s ease-in-out infinite; }
.ipsecx-svg .x-packet { animation:ipsecx-packet 4s linear infinite; }
.ipsecx-svg .x-packet-delay { animation-delay:1.2s; }
.ipsecx-svg .x-dash { stroke-dasharray:5 6; }
.ipsecx-note { margin:.6rem 0 1.5rem; border-left:3px solid #22d3ee; padding:.75rem 1rem; background:#18181b; color:#d4d4d8; }
@keyframes ipsecx-flow { to { stroke-dashoffset:-34; } }
@keyframes ipsecx-pulse { 0%,100% { opacity:.62; filter:none; } 50% { opacity:1; filter:brightness(1.25); } }
@keyframes ipsecx-packet { 0% { transform:translateX(0); opacity:0; } 12% { opacity:1; } 85% { opacity:1; } 100% { transform:translateX(430px); opacity:0; } }
@media(max-width:640px) { .ipsecx-diagram { padding:.35rem; } .ipsecx-svg { min-width:0; } }
@media(prefers-reduced-motion:reduce) { .ipsecx-svg *, .ipsecx-diagram * { animation:none!important; transition:none!important; scroll-behavior:auto!important; } }
</style>

**Niveau :** EXPERT

Ce cours prolonge les niveaux Débutant et Intermédiaire. Il suppose que le lecteur sait déjà distinguer IKE SA et Child SA, lire les états de base d'un tunnel, interpréter les sélecteurs et dépanner les problèmes courants de NAT-T, de routage et de MTU. L'objectif expert est différent : concevoir une architecture IPsec observable, résiliente et vérifiable, comprendre les frontières cryptographiques, analyser les comportements de convergence et préparer des changements reproductibles sans casser la connectivité.

IPsec n'est pas un produit unique. C'est un ensemble de protocoles, de transformations cryptographiques, de politiques, de SA et de décisions de routage. Une implémentation peut être cryptographiquement saine et néanmoins échouer à cause de sélecteurs incorrects, de chemins asymétriques, d'une mauvaise identité IKE, d'un MTU mal calculé ou d'une stratégie de basculement incohérente. Le niveau Expert traite l'ensemble du système et les interactions entre ses composants.

Les exemples Cisco IOS/IOS XE sont des modèles conceptuels : commandes, noms de commandes, fonctions disponibles et syntaxe varient selon la plateforme et la version. Vérifier les guides du constructeur et tester dans un laboratoire avant toute production. Les commandes de diagnostic sont privilégiées ; toute action qui supprime une SA ou modifie le routage doit être exécutée dans une fenêtre contrôlée.

> **Analogie** : un déploiement IPsec à grande échelle ressemble à un réseau de postes-frontières. IKEv2 est le protocole par lequel les postes s'identifient, négocient les règles et renouvellent leurs autorisations ; ESP est le mécanisme qui protège les colis sur le trajet. Les routes définissent les itinéraires, les sélecteurs décrivent les colis autorisés, et la supervision vérifie que les postes fonctionnent réellement. Un poste « ouvert » ne garantit ni un itinéraire correct, ni la livraison.


## 1. La théorie et les algorithmes

## 1.1 Modèle mental expert : cinq plans à distinguer

Pour analyser un incident IPsec, séparer au minimum cinq plans :

| Plan | Question | Preuves typiques | Erreur classique |
|---|---|---|---|
| Identité et authentification | Qui est le pair distant ? | Identité IKE, certificat, chaîne PKI, PSK, horloge | Confondre adresse IP et identité IKE |
| Négociation | Quelles protections ont été convenues ? | IKE SA, Child SA, propositions et sélecteurs | Se fier uniquement à un statut « UP » |
| Sécurité des données | Quels paquets sont acceptés et protégés ? | SPI, compteurs ESP, anti-rejeu, traces d'interface | Diagnostiquer un filtre réseau sans regarder la SA |
| Routage et transfert | Quel chemin prend le paquet ? | RIB/FIB, PBR, VRF, ECMP, ACL, NAT | Supposer que créer une SA installe toute la route |
| Exploitation | Le système est-il stable et observable ? | Journaux corrélés, métriques, alertes, tests synthétiques | Ne mesurer que la présence du tunnel |

La bonne méthode consiste à identifier le premier plan où le comportement observé diverge du comportement attendu. Une preuve positive dans un plan ne prouve pas le bon fonctionnement des suivants.

### Schéma 1 — Plans de fonctionnement IPsec

<div class="ipsecx-diagram" role="img" aria-label="Cinq plans distincts d’un VPN IPsec : identité, négociation IKE, protection ESP, routage et exploitation. Les flux animés indiquent la chaîne de preuves à vérifier.">
<svg class="ipsecx-svg" viewBox="0 0 1000 330" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="28" text-anchor="middle">Diagnostiquer IPsec par plans, pas par intuition</text>
  <path class="x-flow" d="M90 94 H908"/><polygon points="900,87 914,94 900,101" fill="#22d3ee"/>
  <g class="x-pulse"><rect class="x-card-blue" x="30" y="62" width="170" height="76" rx="11"/><text x="115" y="88" text-anchor="middle">1. Identité</text><text class="x-small" x="115" y="111" text-anchor="middle">certificat / PSK</text></g>
  <g><rect class="x-card" x="222" y="62" width="170" height="76" rx="11"/><text x="307" y="88" text-anchor="middle">2. Négociation</text><text class="x-small" x="307" y="111" text-anchor="middle">IKE / Child SA</text></g>
  <g class="x-pulse"><rect class="x-card-green" x="414" y="62" width="170" height="76" rx="11"/><text x="499" y="88" text-anchor="middle">3. Protection</text><text class="x-small" x="499" y="111" text-anchor="middle">ESP / anti-rejeu</text></g>
  <g><rect class="x-card" x="606" y="62" width="170" height="76" rx="11"/><text x="691" y="88" text-anchor="middle">4. Transfert</text><text class="x-small" x="691" y="111" text-anchor="middle">RIB / FIB / ACL</text></g>
  <g class="x-pulse"><rect class="x-card-amber" x="798" y="62" width="170" height="76" rx="11"/><text x="883" y="88" text-anchor="middle">5. Exploitation</text><text class="x-small" x="883" y="111" text-anchor="middle">logs / sondes</text></g>
  <path class="x-line x-dash" d="M115 138 V178 H883 V138"/><text class="x-small" x="500" y="171" text-anchor="middle">Chaque étage doit être prouvé séparément</text>
  <rect class="x-card" x="115" y="205" width="770" height="75" rx="13"/><text x="500" y="232" text-anchor="middle" class="x-title">Preuves croisées</text><text x="500" y="255" text-anchor="middle">états IKE + compteurs ESP + route choisie + test applicatif + chronologie d'événements</text>
  <circle class="x-packet" cx="115" cy="94" r="5" fill="#67e8f9"/><circle class="x-packet x-packet-delay" cx="115" cy="94" r="5" fill="#67e8f9"/>
</svg></div>

## 1.2 IKEv2 : machine à états, authentification et rekey

IKEv2 établit une IKE SA à travers IKE_SA_INIT, puis authentifie les pairs et négocie normalement une première Child SA dans IKE_AUTH. Une IKE SA existante peut gérer d'autres Child SA, en supprimer, ou en renouveler les paramètres. Les messages INFORMATIONAL peuvent transporter des notifications, des demandes de suppression ou des échanges de contrôle. CREATE_CHILD_SA sert notamment à créer des Child SA supplémentaires ou à renouveler des SA existantes ; la sémantique précise dépend du type de rekey et des capacités de l'implémentation.

Il faut distinguer quatre identités :

- **Adresse de transport du pair** : adresse IP externe à laquelle IKE est envoyé, éventuellement transformée par NAT.
- **Identité IKE (IDi / IDr)** : identifiant logique présenté par le pair. Elle peut être une adresse, un FQDN ou une identité liée à un certificat.
- **Sujet et SAN du certificat** : éléments évalués selon la politique PKI du pair ; le simple fait qu'un certificat soit signé ne suffit pas à valider l'identité attendue.
- **Réseaux protégés** : sélecteurs TS_i/TS_r qui décrivent les flux de la Child SA. Ils ne sont pas les identités des passerelles.

Une panne lors d'un changement de fournisseur, de nom DNS ou d'IP publique peut donc provenir de l'une de ces identités sans que les autres changent. Les journaux doivent conserver les identités effectivement observées, sans divulguer de secrets.

### Schéma 2 — Négociation et renouvellement IKEv2

<div class="ipsecx-diagram" role="img" aria-label="Séquence IKEv2 avec IKE_SA_INIT, IKE_AUTH, Child SA, puis rekey et suppression contrôlée de l'ancienne association.">
<svg class="ipsecx-svg" viewBox="0 0 1000 365" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="27" text-anchor="middle">Cycle de vie d'une session IPsec</text>
  <rect class="x-card-blue" x="55" y="48" width="210" height="48" rx="10"/><text x="160" y="77" text-anchor="middle">Pair A : initiateur</text>
  <rect class="x-card-blue" x="735" y="48" width="210" height="48" rx="10"/><text x="840" y="77" text-anchor="middle">Pair B : répondeur</text>
  <path class="x-flow" d="M265 119 H735"/><polygon points="725,112 739,119 725,126" fill="#22d3ee"/><text x="500" y="111" text-anchor="middle">IKE_SA_INIT — propositions, DH, nonces</text>
  <path class="x-flow-green" d="M735 165 H265"/><polygon points="275,158 261,165 275,172" fill="#4ade80"/><text x="500" y="157" text-anchor="middle">Réponse : paramètres choisis / détection NAT</text>
  <rect class="x-card" x="290" y="181" width="420" height="52" rx="10"/><text x="500" y="203" text-anchor="middle">IKE_AUTH</text><text class="x-small" x="500" y="220" text-anchor="middle">identités · authentification · Child SA initiale</text>
  <path class="x-flow-green" d="M265 256 H735"/><polygon points="725,249 739,256 725,263" fill="#4ade80"/><text x="500" y="248" text-anchor="middle">ESP : trafic protégé</text>
  <path class="x-flow-amber" d="M265 300 H735"/><polygon points="725,293 739,300 725,307" fill="#fbbf24"/><text x="500" y="292" text-anchor="middle">CREATE_CHILD_SA : renouvellement coordonné</text>
  <rect class="x-card-amber" x="290" y="318" width="420" height="36" rx="8"/><text x="500" y="341" text-anchor="middle">Ancienne SA retirée après transition selon l'implémentation</text>
</svg></div>

Une erreur de rekey peut se manifester comme une panne périodique : le tunnel monte, transporte des paquets puis se bloque autour d'une expiration. Pour analyser ce cas, corréler les événements autour des durées de vie, les identifiants de SA, les SPI, les propositions de rekey et les compteurs avant/après. Ne pas supposer que tous les constructeurs ont les mêmes marges de renouvellement ou le même comportement en cas de collision de rekey.

### IKE SA, Child SA et sens de transmission

Une SA ESP est unidirectionnelle. Une connexion bidirectionnelle exige généralement au moins une SA pour chaque sens. Le SPI identifie la SA côté réception ; il n'est pas un identifiant global de tunnel et peut changer après un renouvellement. Les outils d'observation doivent donc associer SPI, pair, direction, algorithmes, compteurs et période temporelle.

Les métriques utiles comprennent : paquets encapsulés, octets encapsulés, paquets décapsulés, paquets rejetés, erreurs d'intégrité, anti-rejeu, échecs de sélection et pertes observées sur les interfaces. Une hausse des compteurs sortants sans hausse des compteurs entrants ne prouve pas que l'Internet bloque ESP : le pair distant peut avoir une route incorrecte, une policy qui ne sélectionne pas le flux, une SA non synchronisée ou un équipement filtrant les retours.

## 1.3 Cryptographie : choix défendables et rotation

La négociation cryptographique doit être gouvernée par une politique explicite et versionnée. Le but n'est pas de multiplier les suites possibles « pour la compatibilité », mais de réduire les combinaisons aux algorithmes pris en charge, encore jugés sûrs par l'organisation et adaptés à la plateforme.

Principes pratiques :

- Préférer des suites modernes recommandées par les standards et la politique cryptographique de l'organisation, par exemple des algorithmes AEAD tels qu'AES-GCM lorsque les deux extrémités les prennent en charge correctement.
- Éviter les algorithmes et groupes faibles ou dépréciés ; définir un plan de retrait des exceptions héritées au lieu de les conserver indéfiniment.
- Distinguer intégrité/authentification IKE, chiffrement et intégrité ESP, groupes Diffie–Hellman, PRF et dérivation de clés.
- Définir les paramètres de durée de vie et les critères de rekey. Les temporisations sont un outil opérationnel ; elles ne remplacent pas une politique de cryptographie correcte.
- Mesurer les performances de l'algorithme sur le matériel réel, y compris lors des rekeys et sous perte de paquets. Le support théorique d'un algorithme ne garantit pas le débit attendu.
- Documenter toute dérogation, son propriétaire, sa date d'expiration et les preuves qu'elle est nécessaire.

### Forward secrecy et groupes DH

La confidentialité persistante (forward secrecy) vise à limiter l'effet d'une compromission ultérieure de clés à long terme sur les sessions passées. Elle dépend des échanges éphémères et de la manière dont les clés sont dérivées et renouvelées. Il faut vérifier les paramètres réellement négociés et les capacités de l'implémentation, pas uniquement la configuration voulue. Les groupes autorisés doivent suivre les recommandations actuelles de la politique cryptographique interne et des standards applicables.

> **Piège :** une configuration affichant « AES-GCM » n'est pas, à elle seule, une preuve de sécurité de bout en bout. Il faut aussi vérifier l'authentification des pairs, les groupes cryptographiques, la génération et la protection des clés, la validation des certificats, les politiques de contrôle d'accès et les journaux.

## 1.4 Certificats, PKI et identité des pairs

Les certificats facilitent l'exploitation d'un parc de passerelles quand la gestion des secrets partagés devient difficile. En contrepartie, ils introduisent des dépendances : chaîne de confiance, dates de validité, usages de clé, SAN/nom attendu, révocation, distribution de CRL/OCSP lorsque c'est applicable, synchronisation horaire et rotation sans interruption.

Checklist de validation d'un certificat :

1. Le certificat est-il valide au regard de l'horloge des deux équipements ?
2. Sa chaîne remonte-t-elle à une ancre de confiance attendue et non à une autorité ajoutée de façon improvisée ?
3. L'identité présentée correspond-elle à l'ID IKE attendu par la politique de l'autre côté ?
4. Les usages du certificat et la politique de signature conviennent-ils à l'authentification IKE ?
5. Le renouvellement du certificat a-t-il été testé avant expiration ?
6. Les certificats et clés privés sont-ils protégés, avec droits d'accès restreints et sauvegardes contrôlées ?
7. Les procédures d'urgence de révocation et de remplacement ont-elles été répétées en laboratoire ?

Un certificat renouvelé peut être accepté par un pair mais rejeté par un autre qui épingle une identité trop précise. Il faut séparer la validation cryptographique de la chaîne et la validation de l'identité logique. Ne jamais contourner une validation de certificat à long terme pour rétablir temporairement un tunnel ; si une exception est incontournable, elle doit être limitée, journalisée, datée et supprimée après résolution.

### Schéma 3 — Validation PKI pour IKE

<div class="ipsecx-diagram" role="img" aria-label="Contrôles de certificat en chaîne : date, chaîne de confiance, usages et identité attendue avant d'autoriser IKE_AUTH.">
<svg class="ipsecx-svg" viewBox="0 0 1000 290" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="25" text-anchor="middle">Décider d'accepter l'identité IKE</text>
  <rect class="x-card-blue" x="28" y="75" width="150" height="70" rx="10"/><text x="103" y="102" text-anchor="middle">Certificat reçu</text><text class="x-small" x="103" y="122" text-anchor="middle">IDi / IDr</text>
  <path class="x-flow" d="M178 110 H223"/><polygon points="214,103 228,110 214,117" fill="#22d3ee"/>
  <rect class="x-card" x="230" y="75" width="150" height="70" rx="10"/><text x="305" y="101" text-anchor="middle">Dates + usages</text><text class="x-small" x="305" y="122" text-anchor="middle">horloge / EKU</text>
  <path class="x-flow" d="M380 110 H425"/><polygon points="416,103 430,110 416,117" fill="#22d3ee"/>
  <rect class="x-card" x="432" y="75" width="150" height="70" rx="10"/><text x="507" y="101" text-anchor="middle">Chaîne PKI</text><text class="x-small" x="507" y="122" text-anchor="middle">CA de confiance</text>
  <path class="x-flow" d="M582 110 H627"/><polygon points="618,103 632,110 618,117" fill="#22d3ee"/>
  <rect class="x-card" x="634" y="75" width="150" height="70" rx="10"/><text x="709" y="101" text-anchor="middle">Nom attendu</text><text class="x-small" x="709" y="122" text-anchor="middle">SAN / ID IKE</text>
  <path class="x-flow-green" d="M784 110 H829"/><polygon points="820,103 834,110 820,117" fill="#4ade80"/>
  <rect class="x-card-green x-pulse" x="836" y="75" width="135" height="70" rx="10"/><text x="903" y="102" text-anchor="middle">IKE_AUTH</text><text class="x-small" x="903" y="122" text-anchor="middle">autorisé</text>
  <path class="x-line" d="M305 145 V187 H507 V145 M507 187 H709 V145"/>
  <rect class="x-card-red" x="230" y="207" width="555" height="48" rx="10"/><text class="x-red" x="507" y="236" text-anchor="middle">Tout échec doit conduire à un refus explicite et à un journal utile</text>
</svg></div>

## 1.5 Child SA, Traffic Selectors et politiques de chiffrement

Les sélecteurs TS_i et TS_r représentent les plages de trafic proposées pour une Child SA. Ils ne sont pas identiques à la table de routage, aux ACL du pare-feu ni au NAT. Certains équipements négocient des sélecteurs plus étroits que ceux demandés si leurs politiques l'autorisent ; d'autres attendent une correspondance stricte. Documenter les flux attendus des deux côtés évite les configurations qui semblent similaires mais ne décrivent pas le même trafic.

Pour un incident, collecter :

- préfixes locaux et distants attendus, dont les masques exacts ;
- TS_i/TS_r effectivement négociés ;
- interface, VRF et contexte de sécurité concernés ;
- route de sortie pour la destination de test ;
- traduction NAT avant/après sélection IPsec, selon la plateforme ;
- ACL/politique qui autorise le flux clair dans le LAN ;
- SA et compteurs correspondant au sens du trafic.

Les réseaux chevauchants exigent une décision de conception. Les options peuvent comprendre une renumérotation, une traduction d'adresses encadrée, des VRF distinctes ou des proxies applicatifs. Ajouter des sélecteurs plus larges ne résout pas un chevauchement ; cela peut au contraire créer une exposition involontaire ou une ambiguïté d'acheminement.

## 1.6 Mode tunnel, route-based et policy-based

En mode tunnel, ESP protège le paquet IP original et ajoute un en-tête extérieur. Une interface tunnel virtuelle (VTI) expose un point logique de routage et facilite souvent l'emploi de routes statiques ou de protocoles dynamiques, lorsque la plateforme le permet. Les approches policy-based sélectionnent plus directement les flux par les politiques IPsec et peuvent être adaptées à des environnements plus simples ou à des contraintes de plateforme.

| Critère | Route-based / VTI | Policy-based |
|---|---|---|
| Sélection du chemin | Routage vers une interface tunnel | Politique cryptographique basée sur des sélecteurs |
| Protocoles dynamiques | Souvent plus naturel, selon plateforme | Support variable, parfois plus complexe |
| Dépannage | Route, tunnel, SA et filtres | Route, sélecteurs, SA et filtres |
| Plusieurs préfixes | Souvent plus évolutif | Risque de nombreuses combinaisons de politiques |
| Compatibilité | Dépend de l'OS/équipement | Large historique de déploiement, mais syntaxe variable |
| Risque majeur | Route récursive ou VRF incohérente | Sélecteurs trop larges, oubli d'un flux ou NAT conflictuel |

Un routage récursif survient si la route vers le pair externe lui-même est envoyée dans le tunnel qui dépend de ce pair. Le contrôle de route vers l'adresse publique du pair est critique. Prévoir une route sous-jacente explicite, une surveillance du chemin externe et des vérifications après tout changement de routage.

### Schéma 4 — Route vers le pair et route dans le tunnel

<div class="ipsecx-diagram" role="img" aria-label="Deux décisions distinctes : une route sous-jacente atteint l'adresse publique du pair pour construire IKE, et les préfixes internes prennent le chemin du tunnel après établissement.">
<svg class="ipsecx-svg" viewBox="0 0 1000 325" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="26" text-anchor="middle">Deux chemins à ne pas confondre</text>
  <rect class="x-card-blue" x="35" y="62" width="190" height="68" rx="11"/><text x="130" y="88" text-anchor="middle">Passerelle locale</text><text class="x-small" x="130" y="110" text-anchor="middle">IP externe locale</text>
  <path class="x-flow-amber" d="M225 83 H770"/><polygon points="760,76 774,83 760,90" fill="#fbbf24"/><text x="500" y="73" text-anchor="middle" class="x-amber">Route underlay vers le pair public</text>
  <rect class="x-card-amber" x="775" y="62" width="190" height="68" rx="11"/><text x="870" y="88" text-anchor="middle">Pair distant</text><text class="x-small" x="870" y="110" text-anchor="middle">IP externe distante</text>
  <rect class="x-card" x="35" y="178" width="190" height="68" rx="11"/><text x="130" y="204" text-anchor="middle">Préfixe local</text><text class="x-small" x="130" y="225" text-anchor="middle">10.10.0.0/16</text>
  <path class="x-flow-green" d="M225 212 H770"/><polygon points="760,205 774,212 760,219" fill="#4ade80"/><text x="500" y="201" text-anchor="middle" class="x-green">Route overlay via tunnel IPsec</text>
  <rect class="x-card-green" x="775" y="178" width="190" height="68" rx="11"/><text x="870" y="204" text-anchor="middle">Préfixe distant</text><text class="x-small" x="870" y="225" text-anchor="middle">10.20.0.0/16</text>
  <rect class="x-card-red" x="205" y="268" width="590" height="40" rx="9"/><text class="x-red" x="500" y="293" text-anchor="middle">Si le pair public emprunte son propre tunnel : risque de route récursive et de panne</text>
</svg></div>

## 1.7 NAT Traversal, pare-feu et ports

IKE utilise typiquement UDP 500 ; quand la traversée NAT est détectée et négociée, le trafic IKE et ESP encapsulé passe généralement par UDP 4500. ESP natif utilise le numéro de protocole IP 50, qui n'est pas un port TCP/UDP. Une politique qui n'autorise que « le port ESP » est donc mal formulée si elle ne distingue pas protocole IP et numéro de port.

Dans un réseau complexe, vérifier les règles sur chaque frontière : pare-feu local, pare-feu opérateur, NAT en bordure, ACL sur la passerelle distante et filtres de l'hébergeur. Examiner si les translations restent stables et si le pair distant voit l'adresse et le port attendus. Un NAT qui expire l'état UDP ou change le mapping peut interrompre un tunnel apparemment stable. Les keepalives NAT-T et les mécanismes de détection de vie doivent être dimensionnés avec prudence : trop agressifs, ils augmentent le trafic de contrôle et peuvent amplifier les effets de perte momentanée.

Le fait que le trafic de données soit encapsulé en UDP 4500 ne change pas le besoin de valider les paramètres ESP, les routes et les sélecteurs. NAT-T résout le transport à travers un NAT ; ce n'est pas un contrôle d'accès applicatif et ce n'est pas une protection contre une mauvaise politique IPsec.

## 1.8 MTU, PMTUD, MSS et fragmentation

L'encapsulation IPsec ajoute de l'overhead : en-tête externe, ESP, champs de séquence, éventuel vecteur d'initialisation, tag d'authentification et padding. L'overhead exact dépend du mode, de l'algorithme, d'IPv4/IPv6 extérieur et de la présence de NAT-T. Il ne faut donc pas retenir une valeur universelle de « MTU IPsec ».

Le symptôme classique est une connectivité de petits paquets qui fonctionne alors que les transferts volumineux se bloquent, surtout avec TCP ou TLS. Examiner les messages ICMP Packet Too Big / fragmentation needed, les compteurs de fragmentation, les retransmissions, les tailles MSS annoncées et le comportement de PMTUD sur le chemin. Les mécanismes de clamp MSS peuvent aider pour TCP, mais ils ne corrigent pas tous les problèmes : ils ne couvrent pas UDP, les datagrammes applicatifs ni nécessairement les chemins IPv6.

### Démarche de mesure

1. Mesurer le MTU sur le chemin externe non chiffré si c'est autorisé et représentatif.
2. Déterminer l'overhead réel de la combinaison IPsec négociée.
3. Inspecter les tailles des paquets après encapsulation et les messages ICMP de retour.
4. Comparer petits flux, gros flux TCP et datagrammes UDP de tailles graduelles.
5. Appliquer une seule modification contrôlée (MTU tunnel, MSS clamp ou traitement PMTUD) puis répéter les mêmes tests.
6. Conserver les mesures avant/après et vérifier que le remède ne crée pas de régression sur d'autres chemins.

### Schéma 5 — Où se cachent les octets supplémentaires ?

<div class="ipsecx-diagram" role="img" aria-label="Un paquet IP intérieur est encapsulé dans ESP et un en-tête IP extérieur ; l'overhead réduit l'espace disponible avant la MTU du chemin.">
<svg class="ipsecx-svg" viewBox="0 0 1000 260" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="27" text-anchor="middle">Encapsulation : paquet intérieur et overhead</text>
  <rect class="x-card-green" x="30" y="62" width="940" height="55" rx="9"/><rect x="45" y="74" width="100" height="31" rx="5" fill="#166534"/><text x="95" y="94" text-anchor="middle">IP interne</text><rect x="151" y="74" width="768" height="31" rx="5" fill="#1d4d34"/><text x="535" y="94" text-anchor="middle">Données du paquet original</text>
  <path class="x-flow" d="M50 146 H950"/><polygon points="940,139 954,146 940,153" fill="#22d3ee"/>
  <rect class="x-card-blue" x="30" y="168" width="112" height="49" rx="7"/><text x="86" y="188" text-anchor="middle">IP externe</text><text class="x-small" x="86" y="205" text-anchor="middle">+ header</text>
  <rect class="x-card-amber" x="150" y="168" width="132" height="49" rx="7"/><text x="216" y="188" text-anchor="middle">ESP header</text><text class="x-small" x="216" y="205" text-anchor="middle">SPI / seq</text>
  <rect class="x-card-green" x="290" y="168" width="536" height="49" rx="7"/><text x="558" y="188" text-anchor="middle">Paquet interne chiffré + padding éventuel</text><text class="x-small" x="558" y="205" text-anchor="middle">taille variable selon le trafic et les algorithmes</text>
  <rect class="x-card" x="834" y="168" width="136" height="49" rx="7"/><text x="902" y="188" text-anchor="middle">Tag / trailer</text><text class="x-small" x="902" y="205" text-anchor="middle">+ UDP si NAT-T</text>
  <text class="x-small" x="500" y="245" text-anchor="middle">Le MTU utile dépend de l'overhead négocié : mesure et vérifie PMTUD plutôt que deviner.</text>
</svg></div>

## 1.9 Anti-rejeu, séquences et pertes

ESP utilise des numéros de séquence et peut appliquer une fenêtre anti-rejeu. Les paquets reçus hors fenêtre ou déjà vus peuvent être rejetés. Les chemins à fort réordonnancement, l'ECMP, le multipath ou certaines files matérielles peuvent donc déclencher des compteurs anti-rejeu même si le trafic n'est pas malveillant. Augmenter la fenêtre sans diagnostic ni contrôle de compatibilité n'est pas une réponse universelle : cela modifie une barrière de sécurité et doit être évalué des deux côtés.

Les compteurs « replay », « integrity failure » ou « authentication failed » n'ont pas tous la même signification. Des rejets anti-rejeu peuvent indiquer du réordonnancement, une duplication, une SA ancienne encore active ou une attaque de rejeu. Des erreurs d'intégrité peuvent signaler une corruption, une clé/SA incohérente, des paquets arrivés sur la mauvaise SA ou une implémentation défectueuse. Collecter les événements, les numéros de séquence si disponibles, les SPI, les changements de topologie et les statistiques d'interface avant de conclure.

## 1.10 Sécurité des clés, rotation et séparation des rôles

Les clés privées et secrets pré-partagés doivent être traités comme des secrets de production. Ne jamais les intégrer à un fichier de configuration partagé, un ticket d'incident, une capture ou un dépôt Git. Un secret de laboratoire doit être distinct du secret de production et être tourné après un exercice si son exposition est possible.

Mesures de gouvernance :

- Stockage protégé des clés privées, permissions minimales et séparation entre opérateurs et approbateurs.
- Certificats par pair lorsque le parc le justifie, plutôt qu'un secret partagé identique à l'échelle de tous les sites.
- Processus de rotation avec chevauchement contrôlé si la plateforme le permet et tests de rollback.
- Inventaire des pairs, identités, certificats, suites cryptographiques, durées de vie et propriétaires opérationnels.
- Procédure d'urgence pour révoquer une identité compromise et reconstruire une SA sans contourner les contrôles.
- Journalisation suffisante pour l'audit sans consigner de matériel secret ou de contenu sensible inutile.

## 1.11 HA, rekey et convergence

La haute disponibilité IPsec est une combinaison de redondance du chemin sous-jacent, de disponibilité des pairs, de gestion de l'état IKE/ESP et de convergence du routage. Le basculement d'un lien n'implique pas que les SA soient transportables sans interruption vers un autre pair. Certaines solutions synchronisent une partie de l'état, d'autres recréent les SA après basculement. Ce comportement doit être prouvé dans un test de panne, pas déduit du fait que deux équipements ont une configuration identique.

Dimensions à planifier :

- Détection de panne du chemin externe, avec des seuils qui évitent les bascules lors de micro-coupures.
- Cohérence des adresses et identités IKE lors du basculement.
- Synchronisation des clés et SA, si la plateforme la prend en charge, et traitement des numéros de séquence.
- Convergence des routes overlay, suppression des routes orphelines et prévention de la récursion.
- Comportement des applications longues : sessions TCP, transactions TLS, VoIP et flux UDP.
- Déclenchement et récupération : temps de détection, temps d'établissement de la SA, temps d'installation de route et temps de rétablissement de l'application.

### Schéma 6 — Basculement sans confondre état et connectivité

<div class="ipsecx-diagram" role="img" aria-label="Chemin primaire et chemin secondaire d'un VPN. La supervision vérifie le pair, la SA, les routes et un test applicatif avant de considérer le service rétabli.">
<svg class="ipsecx-svg" viewBox="0 0 1000 320" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="26" text-anchor="middle">Failover : mesurer le service de bout en bout</text>
  <rect class="x-card-blue" x="35" y="70" width="170" height="58" rx="10"/><text x="120" y="94" text-anchor="middle">Site source</text><text class="x-small" x="120" y="112" text-anchor="middle">route locale</text>
  <path class="x-flow-green" d="M205 84 H415"/><polygon points="405,77 419,84 405,91" fill="#4ade80"/>
  <rect class="x-card-green x-pulse" x="420" y="60" width="205" height="65" rx="10"/><text x="522" y="85" text-anchor="middle">Tunnel primaire</text><text class="x-small" x="522" y="105" text-anchor="middle">SA + route + trafic</text>
  <path class="x-flow-green" d="M625 84 H815"/><polygon points="805,77 819,84 805,91" fill="#4ade80"/>
  <rect class="x-card-green" x="820" y="70" width="145" height="58" rx="10"/><text x="892" y="94" text-anchor="middle">Site distant</text><text class="x-small" x="892" y="112" text-anchor="middle">application</text>
  <path class="x-flow-amber" d="M205 165 H415"/><polygon points="405,158 419,165 405,172" fill="#fbbf24"/><path class="x-flow-amber" d="M625 165 H815"/><polygon points="805,158 819,165 805,172" fill="#fbbf24"/>
  <rect class="x-card-amber" x="420" y="141" width="205" height="48" rx="10"/><text x="522" y="161" text-anchor="middle">Tunnel secondaire</text><text class="x-small" x="522" y="178" text-anchor="middle">chemin de secours</text>
  <path class="x-line" d="M120 128 V229 H892 V128"/><path class="x-flow" d="M120 229 H890"/><polygon points="880,222 894,229 880,236" fill="#22d3ee"/>
  <rect class="x-card" x="244" y="210" width="536" height="76" rx="11"/><text x="512" y="236" text-anchor="middle" class="x-title">Sonde de service</text><text class="x-small" x="512" y="256" text-anchor="middle">IKE / Child SA · routes · compteurs · transaction applicative</text><text class="x-small" x="512" y="273" text-anchor="middle">ne déclarer le retour que lorsque le service répond</text>
</svg></div>

## 1.12 Routage dynamique, BGP/OSPF et filtrage

Faire passer un protocole de routage dans un tunnel peut faciliter l'adaptation aux changements de préfixes, mais augmente la complexité opérationnelle. Le protocole de routage possède sa propre authentification et sa politique de voisinage ; la protection IPsec ne remplace pas ses contrôles. Filtrer les préfixes annoncés, éviter les routes par défaut involontaires, utiliser des limites de préfixes, définir les préférences de chemin et documenter les mécanismes de prévention des boucles.

Avec BGP, valider les politiques d'import/export, les communautés, les préfixes autorisés, les chemins de secours et le comportement lors d'une perte de tunnel. Avec OSPF, valider les types de réseau, les timers, MTU d'adjacence si concernés et l'absence d'annonce involontaire de routes. Les commandes exactes dépendent de la plateforme ; ne pas recopier une configuration de routage sans l'adapter au plan d'adressage et à la topologie.

Les filtres doivent distinguer au minimum :

- trafic IKE vers les adresses de pairs ;
- ESP natif ou ESP encapsulé en UDP 4500 selon la négociation ;
- trafic utilisateur autorisé après décapsulation ;
- protocole de routage qui circule dans le tunnel ;
- trafic d'administration vers la passerelle ;
- sondes de surveillance et messages ICMP nécessaires à la découverte MTU lorsque c'est approprié.

Une règle qui autorise l'établissement IPsec n'autorise pas automatiquement tous les flux décapsulés. Filtrer à la bonne frontière et consigner ce que chaque ACL doit autoriser.

## 1.13 VRF, multi-tenant et chevauchement d'adresses

Dans une architecture multi-tenant, la VRF ou le contexte de routage isole la table de routage, pas forcément toutes les ressources du plan de contrôle. Vérifier la prise en charge de l'IPsec par VRF, les interfaces source IKE, les routes externes, les interfaces VTI et l'attachement des politiques. Un paquet peut être reçu dans une VRF mais chercher sa route de réponse dans une autre.

Les réseaux chevauchants compliquent les sélecteurs et la classification. Une NAT de chevauchement doit être explicite, limitée aux plages concernées et documentée de bout en bout. Vérifier les effets sur DNS, les journaux, les ACL et les outils de supervision qui voient parfois des adresses traduites plutôt que les adresses d'origine. Toute translation doit être cohérente dans les deux sens et compatible avec les sélecteurs réellement négociés.

## 1.14 Modéliser la disponibilité et la capacité

Le dimensionnement doit tenir compte du débit chiffré soutenu, des paquets par seconde, de la taille moyenne des paquets, des fonctions activées, du nombre de tunnels et de SA, du coût des rekeys, du niveau de journalisation et des scénarios de basculement. Un appareil capable de chiffrer un gros flux de paquets volumineux peut être limité par les petits paquets à débit de paquets élevé. Vérifier aussi le débit avec inspection ou filtrage supplémentaires.

Une mesure utile par scénario inclut :

- débit et pps réellement acheminés ;
- CPU, accélérateur crypto, mémoire et utilisation des files ;
- latence moyenne et percentiles p95/p99 ;
- taux de perte, retransmissions et paquets rejetés ;
- durée de rekey et impact observable ;
- nombre de tunnels/SA actifs et taux d'établissement ;
- temps de convergence de route et de rétablissement applicatif.

Ne pas dimensionner sur une seule valeur commerciale de débit « VPN » sans vérifier les conditions de mesure, les algorithmes, les tailles de paquets et les fonctions incluses. Prévoir une marge correspondant à la croissance attendue et au scénario de panne où le pair restant absorbe plus de trafic.

### Schéma 7 — Capacité : débit, paquets et marge de résilience

<div class="ipsecx-diagram" role="img" aria-label="Visualisation de la capacité IPsec selon le débit, le nombre de paquets et la réserve nécessaire pour absorber un basculement.">
<svg class="ipsecx-svg" viewBox="0 0 1000 295" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="27" text-anchor="middle">La capacité VPN est un ensemble de contraintes</text>
  <rect class="x-card-green" x="35" y="65" width="280" height="86" rx="12"/><text x="175" y="91" text-anchor="middle">Débit chiffré</text><text class="x-small" x="175" y="112" text-anchor="middle">Gb/s selon paquet et suite</text><rect x="55" y="127" width="240" height="8" rx="4" fill="#27272a"/><rect class="x-pulse" x="55" y="127" width="170" height="8" rx="4" fill="#4ade80"/>
  <rect class="x-card-blue" x="360" y="65" width="280" height="86" rx="12"/><text x="500" y="91" text-anchor="middle">Paquets par seconde</text><text class="x-small" x="500" y="112" text-anchor="middle">PPS, tailles petites et mixtes</text><rect x="380" y="127" width="240" height="8" rx="4" fill="#27272a"/><rect class="x-pulse" x="380" y="127" width="190" height="8" rx="4" fill="#60a5fa"/>
  <rect class="x-card-amber" x="685" y="65" width="280" height="86" rx="12"/><text x="825" y="91" text-anchor="middle">Marge de basculement</text><text class="x-small" x="825" y="112" text-anchor="middle">capacité restante après panne</text><rect x="705" y="127" width="240" height="8" rx="4" fill="#27272a"/><rect class="x-pulse" x="705" y="127" width="125" height="8" rx="4" fill="#fbbf24"/>
  <path class="x-flow" d="M175 173 V209 H825 V173"/><polygon points="815,202 829,209 815,216" fill="#22d3ee"/>
  <rect class="x-card" x="220" y="221" width="560" height="50" rx="10"/><text x="500" y="242" text-anchor="middle">Valider sous charge et en situation de panne</text><text class="x-small" x="500" y="259" text-anchor="middle">débit + pps + latence + pertes + temps de convergence</text>
</svg></div>

## 1.15 Observabilité : logs, métriques et tests synthétiques

Un tableau de bord « tunnel UP » est insuffisant. L'observabilité doit relier les événements du contrôle IKE aux compteurs ESP, aux routes, aux métriques de l'interface externe et à des tests applicatifs contrôlés. Les horodatages doivent être synchronisés ; sinon, un événement de rekey peut apparaître après la panne qu'il a provoquée ou l'inverse.

### Données recommandées

| Signal | Exemple | Utilité |
|---|---|---|
| Événements IKE | pair, échange, notification, motif d'échec | Localiser l'étape de négociation |
| Identifiants SA | SPI entrée/sortie, algorithmes, durée de vie | Lier compteurs et logs à la bonne génération de SA |
| Compteurs ESP | encapsulation, décapsulation, erreurs, anti-rejeu | Identifier le sens où le trafic s'arrête |
| Routage | préfixe, next-hop, VRF, interface, changement | Vérifier le chemin réellement choisi |
| Interfaces | pertes, erreurs, débit, drops de file | Chercher une congestion ou une panne sous-jacente |
| Test synthétique | ping adapté, TCP, HTTPS ou transaction applicative | Mesurer la disponibilité réelle du service |
| Changements | déploiement, rotation cert, mise à jour, modification ACL | Corréler une régression à une action |

Les logs IKE peuvent contenir des identités internes, des adresses publiques ou des détails de topologie. Les protéger comme des données opérationnelles. Ne jamais journaliser ou exporter les clés, PSK ou données privées inutiles. Les niveaux de debug très détaillés doivent être activés brièvement, filtrés si possible et arrêtés une fois les preuves collectées.

### Schéma 8 — Corrélation de preuves pour un incident

<div class="ipsecx-diagram" role="img" aria-label="Corrélation des journaux IKE, compteurs ESP, routage, interfaces et sondes applicatives dans une chronologie d'incident.">
<svg class="ipsecx-svg" viewBox="0 0 1000 330" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="26" text-anchor="middle">Une chronologie commune révèle le premier écart</text>
  <text x="130" y="72">IKE / rekey</text><text x="130" y="117">ESP in/out</text><text x="130" y="162">Routage</text><text x="130" y="207">Interface</text><text x="130" y="252">Test applicatif</text>
  <path class="x-line" d="M285 67 H940 M285 112 H940 M285 157 H940 M285 202 H940 M285 247 H940"/>
  <path class="x-flow" d="M290 67 H940"/><path class="x-flow-green" d="M290 112 H625"/><path class="x-flow-amber" d="M290 157 H730"/>
  <circle class="x-pulse" cx="610" cy="67" r="7" fill="#fbbf24"/><circle class="x-pulse" cx="625" cy="112" r="7" fill="#4ade80"/><circle class="x-pulse" cx="730" cy="157" r="7" fill="#fbbf24"/><circle class="x-pulse" cx="600" cy="202" r="7" fill="#fb7185"/><circle class="x-pulse" cx="520" cy="247" r="7" fill="#fb7185"/>
  <path class="x-line x-dash" d="M520 48 V275"/><text class="x-red" x="535" y="291">début du symptôme</text>
  <rect class="x-card" x="300" y="300" width="640" height="24" rx="6"/><text class="x-small" x="620" y="316" text-anchor="middle">Synchroniser les horloges ; conserver les IDs/SPI et les horodatages</text>
</svg></div>

## 1.16 Menaces et limites de sécurité

IPsec protège la confidentialité et l'intégrité des paquets selon les paramètres négociés, mais n'empêche pas un poste autorisé compromis d'envoyer du trafic malveillant. Il ne remplace pas l'authentification utilisateur, le durcissement, les ACL, la segmentation ni l'inspection applicative. Le trafic décapsulé doit être traité comme un flux réseau ordinaire et soumis à des contrôles adaptés.

Risques à examiner :

- clés ou certificats compromis ;
- PSK réutilisé sur un trop grand nombre de sites ;
- identité IKE trop laxiste ;
- sélecteurs trop larges qui étendent la confiance au-delà du besoin ;
- routes dynamiques acceptées sans filtre ;
- plan de gestion exposé depuis les réseaux de transit ;
- debug contenant trop d'information ;
- basculement vers un chemin de secours moins filtré ;
- équipement ou accélérateur cryptographique vulnérable, non corrigé ou mal configuré ;
- anciens algorithmes conservés pour un pair qui n'est plus censé être actif.

Adopter une approche de moindre privilège : réduire les préfixes autorisés, filtrer les flux après décapsulation, isoler l'administration, restreindre les origines IKE, auditer les identités et surveiller les changements de paramètres négociés.

## 1.17 Migration et interopérabilité multi-constructeurs

La migration d'un tunnel doit commencer par une fiche de référence : identité des pairs, IPs externes, mode, versions, propositions IKE et ESP, méthodes d'authentification, sélecteurs, durée de vie, NAT-T, MTU/MSS, routes, ACL, journaux et tests applicatifs. Les chaînes de configuration équivalentes entre constructeurs ne sont pas toujours sémantiquement identiques ; comparer les paramètres négociés et les comportements effectifs, pas seulement les noms des profils.

Approche de migration recommandée :

1. Inventorier les tunnels et leur usage réel ; éliminer les SA et politiques obsolètes après validation du propriétaire.
2. Vérifier les capacités de chaque extrémité et fixer les suites acceptées.
3. Construire un tunnel pilote avec un préfixe ou service non critique.
4. Réaliser un échange de tests bidirectionnel et capturer les métriques de référence.
5. Tester rekey, perte de peer, perte de lien, reprise et redémarrage contrôlé.
6. Préparer un plan de bascule avec contrôle de route, règle de pare-feu et retour arrière.
7. Migrer par lots et surveiller les résultats par catégorie de service.
8. Retirer les anciennes politiques et clés après confirmation, puis mettre à jour l'inventaire.

Ne pas conserver deux chemins actifs non maîtrisés vers les mêmes préfixes sans comprendre l'ECMP, la symétrie, les SA et les politiques de sélection. Une migration qui « fonctionne » pour un ping peut encore casser des transferts TCP, le DNS, une application utilisant UDP ou une transaction longue.


## 2. Configuration et pratique

Les configurations ci-dessous décrivent la logique à déployer sur des routeurs Cisco compatibles avec le type de VPN choisi. Elles ne sont pas universelles : les plateformes IOS, IOS XE, ASA et les équipements de sécurité dédiés ont des syntaxes et des modèles différents. Il est interdit de coller le bloc sans avoir vérifié les noms d'interface, les capacités IKEv2, les méthodes d'authentification et le support des interfaces tunnel sur le matériel concerné.

## 2.1 Laboratoire de référence

| Élément | Site A | Site B |
|---|---|---|
| LAN | `10.10.0.0/16` | `10.20.0.0/16` |
| Passerelle LAN | `10.10.0.1` | `10.20.0.1` |
| Adresse WAN illustrative | `198.51.100.10` | `203.0.113.20` |
| Identité IKE | `gw-a.example.test` | `gw-b.example.test` |
| Authentification de laboratoire | Certificat de test ou PSK non réutilisé | Certificat de test ou PSK non réutilisé |

Les blocs d'adresses WAN ci-dessus proviennent des plages de documentation RFC 5737 ; ils ne sont pas des adresses routables à utiliser dans un déploiement réel. Le LAN, les identités et les secrets doivent être adaptés au laboratoire.

## 2.2 Stratégie de profil avant les commandes

Avant de configurer un pair, écrire une matrice explicite. Cela évite d'entasser des propositions dans l'espoir de faire fonctionner l'interopérabilité.

| Paramètre | Décision attendue | Validation |
|---|---|---|
| IKE version | IKEv2 selon politique | État IKE et échange réussi |
| Authentification | Certificat préféré dans un parc administré ; PSK unique pour laboratoire simple | Identité distante validée, secret hors dépôt |
| Cryptographie IKE | Suite moderne approuvée et commune | Proposition réellement négociée |
| Cryptographie ESP | Suite ESP approuvée, de préférence AEAD si support commun | Child SA et algorithmes affichés |
| PFS / groupe DH pour Child SA | Valeur conforme à la politique et capacités | Même groupe proposé et accepté |
| TS_i / TS_r | Préfixes précis nécessaires au service | Sélecteurs installés concordants |
| Durées de vie | Valeurs compatibles, rekey anticipé selon plateforme | Renouvellement observé en laboratoire |
| NAT-T | Activé si le chemin peut contenir du NAT | Capture/compteurs UDP 4500 |
| MTU / MSS | Mesure sur chemin réel | Tests de gros flux et ICMP PMTUD |
| Routage | Route-based ou policy-based choisi explicitement | Route de pair et route des préfixes contrôlées |

## 2.3 Configuration illustrative IKEv2

Exemple conceptuel pour une plateforme Cisco IOS/IOS XE qui prend en charge les profils IKEv2 et IPsec compatibles. La syntaxe de certificat, le profil de chiffrement ESP, les sélecteurs et l'attachement à une interface tunnel peuvent varier. Le but est de montrer les composants à vérifier, non de fournir un copier-coller universel.

```text
! Exemple conceptuel — adapter à la version et au matériel
crypto ikev2 proposal IKEV2-PROP
 encryption aes-gcm-256
 prf sha384
 group 19
!
crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROP
!
! Profil d'identité/authentification : compléter selon certificat ou PSK
crypto ikev2 profile IKEV2-PEER-B
 match identity remote fqdn gw-b.example.test
 authentication remote pre-share
 authentication local pre-share
 keyring local KEYRING-TO-B
!
! Transformer ce modèle en une configuration validée pour l'image IOS XE cible.
! Ne pas publier de secret réel dans le cours, le dépôt ou un ticket.
```

Important : les mots-clés et leur disponibilité diffèrent selon les versions. Certaines plateformes exigent une proposal distincte pour AES-GCM, d'autres organisent les transformations d'une façon différente. Vérifier la documentation exacte avant de configurer l'équipement. Un profil IKEv2 incomplet ne constitue pas un tunnel fonctionnel : il faut aussi la politique ESP, la SA ou la VTI, la sélection de trafic, les routes, les ACL et la vérification des deux sens.

## 2.4 Vérifications sans interruption

Commencer par les commandes de lecture :

```text
show crypto ikev2 sa
show crypto ikev2 profile
show crypto ipsec sa
show crypto session detail
show ip route
show interfaces
show logging
```

Les noms et la disponibilité de ces commandes dépendent de la plateforme. Chercher notamment : l'identité du pair, l'état de la IKE SA, les Child SA, les suites négociées, les compteurs encaps/decaps, les erreurs anti-rejeu, les routes vers les préfixes, les erreurs d'interface et les messages de rekey. Sauvegarder la sortie en la nettoyant des informations sensibles avant de la partager.

### Comparer les compteurs

1. Noter les compteurs ESP au début d'un test.
2. Générer un seul flux de test autorisé (par exemple ICMP ou HTTPS entre deux hôtes de laboratoire).
3. Noter les compteurs immédiatement après.
4. Refaire le test dans le sens inverse.
5. Comparer les compteurs du pair distant et l'état de la route.
6. Répéter avec un flux plus volumineux seulement lorsque les petits flux fonctionnent.

Cette méthode donne plus de preuves qu'un seul ping lancé sans connaître la route utilisée. Pour une application critique, utiliser une sonde de transaction qui reproduit le comportement réel, avec un compte de test et un périmètre d'accès réduit.

## 2.5 Captures de paquets

Une capture peut prouver que les échanges IKE sont visibles sur l'interface, que du UDP 4500 est transporté, qu'ESP natif est utilisé, ou que des messages ICMP liés à la MTU reviennent. Elle ne permet pas nécessairement de lire le contenu chiffré du trafic utilisateur. Dans un environnement multi-pair, filtrer par adresses externes et par protocole ; pour NAT-T, considérer UDP 500 et UDP 4500 ; pour ESP natif, considérer le numéro de protocole IP 50.

Les captures doivent être proportionnées et protégées : durée brève, filtre ciblé, stockage contrôlé, suppression après expiration, absence de secrets et partage uniquement avec les équipes qui en ont besoin. Même chiffrée, une capture peut exposer les métadonnées de communication, les adresses publiques, les périodes d'activité et certains éléments de négociation.

## 2.6 Tests de validation en production

Un changement n'est pas validé uniquement parce que l'IKE SA est présente. Utiliser une matrice de tests :

| Test | Résultat attendu | Preuve |
|---|---|---|
| Établissement du pair | Identité et algorithmes conformes | Logs IKE + état SA |
| Connectivité A vers B | Le service autorisé répond | Sondes et compteurs ESP |
| Connectivité B vers A | Retour conforme à la politique | Sondes et compteurs ESP |
| Flux hors politique | Bloqué conformément au modèle d'accès | Logs de sécurité / test négatif |
| Transfert volumineux | Pas de blocage inattendu lié au MTU | Test de transfert et capture ciblée |
| Rekey | Renouvellement sans interruption non acceptable | Logs de durée de vie et sonde de service |
| Panne du WAN primaire | Chemin secondaire opérationnel dans le SLA | Chronologie de basculement |
| Certificat proche expiration | Renouvellement testable, identités acceptées | Test PKI contrôlé |
| Redémarrage contrôlé | Reconstitution du tunnel et routes correctes | Test post-redémarrage |
| Test sécurité | Administration non exposée au LAN distant par défaut | Vérification ACL / segmentation |

> **Astuce :** enregistrer les résultats sous forme de modèle reproductible : heure, pair, version, scénario, sortie des commandes, métriques avant/après et validation par le propriétaire du service. Une bonne fiche d'essai permet de comparer plusieurs versions logicielles et plusieurs constructeurs.


## 3. Dépannage et sécurité

## 3.1 Runbook expert en neuf étapes

1. **Définir l'impact** : quels sites, quels préfixes, quels protocoles, quel début, quelle portée et quelle criticité ?
2. **Figer le contexte** : changements récents, rekey, certificat, mise à jour, opérateur, panne électrique ou modification de route.
3. **Vérifier le transport sous-jacent** : IP publique du pair, UDP 500/4500 ou ESP natif, NAT et filtres sur tout le chemin.
4. **Examiner IKE** : état, identités, échange ayant échoué, propositions, certificat et horloge.
5. **Examiner Child SA** : TS réellement négociés, algorithmes ESP, SPI, anti-rejeu et durée de vie.
6. **Examiner le chemin interne** : RIB/FIB, VRF, route récursive, PBR, NAT, ACL et retour.
7. **Analyser la MTU et les performances** : tailles, ICMP, MSS, pps, CPU, files, erreurs et pertes de capture.
8. **Corriger une hypothèse à la fois** : procédure de changement, preuve avant/après, tests positifs et négatifs.
9. **Clore et prévenir la répétition** : surveillance, documentation, post-mortem et retrait des exceptions temporaires.

### Schéma 9 — Arbre de diagnostic IPsec

<div class="ipsecx-diagram" role="img" aria-label="Arbre de dépannage expert : transport, IKE SA, Child SA, compteurs, routage, MTU puis validation applicative.">
<svg class="ipsecx-svg" viewBox="0 0 1000 420" xmlns="http://www.w3.org/2000/svg">
  <text class="x-title" x="500" y="26" text-anchor="middle">Trouver le premier plan en échec</text>
  <rect class="x-card-blue" x="350" y="45" width="300" height="48" rx="10"/><text x="500" y="74" text-anchor="middle">1. Pair externe joignable ?</text>
  <path class="x-flow" d="M500 93 V118"/><polygon points="493,109 500,123 507,109" fill="#22d3ee"/><text class="x-green" x="520" y="111">Oui</text>
  <rect class="x-card" x="350" y="123" width="300" height="48" rx="10"/><text x="500" y="152" text-anchor="middle">2. IKE SA établie ?</text>
  <path class="x-flow" d="M500 171 V196"/><polygon points="493,187 500,201 507,187" fill="#22d3ee"/>
  <rect class="x-card" x="350" y="201" width="300" height="48" rx="10"/><text x="500" y="230" text-anchor="middle">3. Child SA / TS concordants ?</text>
  <path class="x-flow" d="M500 249 V274"/><polygon points="493,265 500,279 507,265" fill="#22d3ee"/>
  <rect class="x-card-green" x="350" y="279" width="300" height="48" rx="10"/><text x="500" y="308" text-anchor="middle">4. Compteurs ESP progressent ?</text>
  <path class="x-flow" d="M500 327 V350"/><polygon points="493,341 500,355 507,341" fill="#22d3ee"/>
  <rect class="x-card-amber" x="350" y="355" width="300" height="48" rx="10"/><text x="500" y="384" text-anchor="middle">5. Routage / MTU / application</text>
  <!-- Branches de diagnostic raccordées aux bords des cartes : aucun trait ne traverse un libellé. -->
  <path class="x-line x-dash" d="M350 69 H270 V144 H220"/>
  <text class="x-red" x="286" y="104" text-anchor="middle">Non</text>
  <rect class="x-card-red" x="20" y="112" width="200" height="65" rx="10"/><text class="x-red" x="120" y="138" text-anchor="middle">PAIR INJOIGNABLE</text><text class="x-small" x="120" y="157" text-anchor="middle">transport / ACL / NAT</text>
  <rect class="x-card-red" x="700" y="112" width="280" height="65" rx="10"/><text class="x-red" x="840" y="138" text-anchor="middle">IKE en échec</text><text class="x-small" x="840" y="157" text-anchor="middle">identité / propositions / certificat</text>
  <path class="x-line" d="M650 147 H700"/>
  <text class="x-red" x="675" y="132" text-anchor="middle">Non</text>
  <path class="x-line x-dash" d="M350 225 H270 V301 H220"/>
  <text class="x-amber" x="282" y="263" text-anchor="middle">Non</text>
  <rect class="x-card-amber" x="20" y="265" width="200" height="72" rx="10"/><text class="x-amber" x="120" y="290" text-anchor="middle">TS / Child SA</text><text class="x-small" x="120" y="309" text-anchor="middle">sélecteurs / ESP</text><text class="x-small" x="120" y="325" text-anchor="middle">rekey / anti-rejeu</text>
  <text class="x-small" x="500" y="415" text-anchor="middle">Toujours confirmer par une sonde applicative et des compteurs corrélés.</text>
</svg></div>

## 3.2 Tunnel UP, trafic absent

Causes possibles, dans l'ordre où elles peuvent être éliminées efficacement :

- le test n'utilise pas la route attendue ;
- la route vers le pair externe est récursive ou passe dans la mauvaise VRF ;
- la destination ou la source ne correspond pas aux TS de la Child SA ;
- le NAT transforme le flux avant la politique cryptographique ;
- une ACL bloque le trafic clair après décapsulation ;
- un hôte distant a une route de retour ou une passerelle erronée ;
- un flux retour emprunte un autre tunnel ou un autre chemin ECMP ;
- une SA est établie mais les paquets arrivent sur un SPI qui n'est plus actif ;
- la policy du pair distant n'autorise pas le même flux ;
- la connectivité IP existe mais le service écoute sur une autre adresse ou un autre port.

Méthode : lancer un flux identifiable, mesurer les compteurs avant/après sur les deux extrémités, suivre la route et prendre une capture à une frontière appropriée. Éviter de modifier plusieurs éléments en même temps : une correction simultanée du NAT, de l'ACL et de la route rend la cause racine impossible à établir.

## 3.3 Tunnel instable au moment du rekey

Collecter les logs d'au moins une fenêtre complète avant et après l'expiration prévue. Comparer les durées de vie IKE et ESP, les SPI, les événements CREATE_CHILD_SA, les erreurs de proposition, la charge CPU et les pertes du chemin externe. Considérer les écarts d'horloge, le packet loss, les rekeys concurrents, les limites de SA sur l'équipement et les mécanismes propres au constructeur.

Un redémarrage ou une suppression manuelle des SA peut temporairement rétablir le trafic mais détruit des preuves. Ne l'utiliser qu'après collecte initiale, dans une fenêtre approuvée et avec un plan de rétablissement. Une solution durable exige une cause reproductible : paramètres incohérents, bug corrigé par version, limitation de ressource ou défaut de transport.

## 3.4 Asymétrie, ECMP et anti-rejeu

Avec plusieurs chemins de transport, des paquets d'une même SA peuvent être réordonnés ou suivre des chemins qui ont des pertes différentes. Le pair distant peut rejeter de vieux paquets hors de la fenêtre anti-rejeu. Confirmer le phénomène avec compteurs, captures, chronologie et comportement après stabilisation du chemin. Examiner aussi si plusieurs équipements partagent ou non le même état de SA et comment ils gèrent les numéros de séquence en haute disponibilité.

Les réponses possibles incluent l'amélioration du routage pour conserver une meilleure symétrie, la synchronisation d'état si le produit la prend en charge et une adaptation réfléchie de la fenêtre anti-rejeu après analyse des risques. Ne pas désactiver complètement l'anti-rejeu comme solution rapide sans évaluation explicite.

## 3.5 Panne de MTU et trafic partiellement bloqué

Si les petits paquets fonctionnent, commencer par établir la taille seuil qui échoue. Vérifier PMTUD et ICMP, la taille MSS, les paquets fragmentés, les journaux et le MTU des interfaces internes et externes. Un clamp MSS trop agressif réduit les performances et n'aide pas les flux UDP ; un clamp trop large laisse le problème intact. Documenter la MTU de bout en bout, car le chemin peut être variable selon le tunnel ou le fournisseur.

## 3.6 Certificat invalide ou pair inattendu

Si IKE_AUTH échoue après IKE_SA_INIT, relever l'identité effectivement présentée, l'identité attendue, la chaîne de certificat, les dates, la politique de validation et les notifications. Ne pas supprimer la validation de certificat pour « tester ». Dans un laboratoire, utiliser une PKI isolée avec des certificats à durée limitée ; en production, passer par la procédure de rotation/revocation et obtenir une approbation pour tout changement de confiance.

## 3.7 Sécurité des interventions

Les commandes debug, la capture, le clear de SA et les modifications d'ACL/routage peuvent perturber un service. Classer les actions :

| Action | Risque | Contrôle recommandé |
|---|---|---|
| Lire les états et compteurs | Faible | Collecte horodatée et filtrée |
| Capture courte ciblée | Modéré : métadonnées sensibles | Filtre, accès restreint, durée limitée |
| Activer debug détaillé | Modéré à élevé : CPU/logs | Fenêtre courte, niveau minimal, arrêt vérifié |
| Effacer une SA | Interruption possible | Approbation, impact prévu, retour et test |
| Modifier sélecteurs/routage/ACL | Élevé | Backup, change plan, tests positifs/négatifs, rollback |
| Désactiver anti-rejeu ou validation de pair | Très élevé | À éviter comme remède ; exception formelle et immédiate à retirer si autorisée |

> **Danger :** ne jamais coller une clé privée, une PSK, un secret TACACS/RADIUS ou un fichier de configuration non nettoyé dans le dépôt, le cours, un ticket public ou une conversation non approuvée. Les preuves de dépannage doivent conserver le contexte utile, pas les secrets.

## 3.8 Étude de cas A — tunnel actif, HTTPS bloqué après rekey

**Symptômes :** les routes existent ; la IKE SA reste établie ; le petit ping fonctionne ; les transferts HTTPS se figent environ à la même période plusieurs fois par jour.

**Hypothèses concurrentes :** taille MTU, rekey Child SA, chemin retour, ressource crypto, bug logiciel. Ne pas choisir la première hypothèse seulement parce que les transferts sont volumineux.

**Collecte :** horodatages précis, durée de vie Child SA, logs CREATE_CHILD_SA, SPI avant/après, compteurs ESP, retransmissions TCP, ICMP PMTUD et CPU. Tester petit flux et gros flux autour du rekey, sans créer de charge excessive.

**Discrimination :** si le blocage coïncide exactement avec un rekey et les deux pairs montrent une nouvelle Child SA incohérente, inspecter négociation et compatibilité. Si le rekey aboutit mais seules les tailles au-dessus d'un seuil échouent, analyser MTU/PMTUD. Si une seule direction perd ses compteurs, examiner retour et routage. Modifier un seul paramètre et répéter le même test.

**Prévention :** alerte sur les échecs de rekey, sonde HTTPS, vérification des tailles de paquets et procédure de changement versionnée.

## 3.9 Étude de cas B — basculement WAN avec pertes anti-rejeu

**Symptômes :** lors de la perte du circuit principal, le routage bascule mais les applications ont de longues interruptions. Les journaux distants montrent des paquets hors fenêtre anti-rejeu.

**Hypothèses :** réordonnancement sur le nouveau chemin, SA non synchronisée entre membres HA, SPI ancien encore utilisé, différence de MTU, ou convergence lente de route. Confirmer quelle SA a reçu les paquets et quand l'ancien chemin est réellement coupé.

**Action contrôlée :** mesurer la chronologie détection → route → négociation/reprise SA → première requête applicative réussie. Vérifier le modèle HA de la plateforme, sa prise en charge de la réplication SA et des numéros de séquence, puis tester en laboratoire la panne et le retour au chemin primaire. N'élargir la fenêtre anti-rejeu qu'après analyse du comportement et de la sécurité.

**Résultat attendu :** délai de reprise mesuré, aucun chemin orphelin, politique filtrante équivalente sur le secours, et procédure de retour testée.

## 3.10 Étude de cas C — interopérabilité multi-constructeurs

**Symptômes :** IKE SA s'établit mais la Child SA échoue ou ne sélectionne qu'un sous-ensemble des sous-réseaux. Les configurations utilisent des noms d'algorithmes qui semblent équivalents.

**Hypothèses :** propositions ESP non identiques, mode de PFS différent, TS trop larges, identité/certificat interprété différemment, tunnel route-based d'un côté et policy-based de l'autre, NAT exemption ou ordre de politique.

**Méthode :** comparer paramètres réellement négociés des deux côtés ; établir une table commune qui note algorithme, clé, intégrité/AEAD, groupe PFS, sélecteurs et durée de vie. Tester d'abord un couple de préfixes réduit, puis étendre par lots. Ne pas ouvrir une suite plus faible à tous les pairs pour résoudre un seul cas d'interopérabilité.

## 3.11 Checklist d'acceptation experte

- [ ] Identité des pairs validée de manière stricte et documentée.
- [ ] Certificats/PSK gérés et renouvelables sans secret dans le dépôt.
- [ ] Propositions IKE et ESP conformes à la politique cryptographique.
- [ ] Child SA et TS réels vérifiés dans chaque sens.
- [ ] Routage externe du pair protégé contre la récursion.
- [ ] Routes LAN, VRF, NAT et ACL vérifiées sur le chemin réel.
- [ ] NAT-T/ESP autorisés au bon niveau du pare-feu.
- [ ] Anti-rejeu activé et compteurs surveillés.
- [ ] MTU/PMTUD testés sur les flux réels, pas seulement par petits paquets.
- [ ] Rekey et expiration de certificat testés en laboratoire.
- [ ] Scénarios de panne WAN et failover testés, délais mesurés.
- [ ] Tests applicatifs positifs et négatifs documentés.
- [ ] Logs synchronisés, alertes utiles et données sensibles protégées.
- [ ] Plan de retour arrière, sauvegarde et propriétaire du service connus.
- [ ] Inventaire à jour des pairs, versions, SA attendues et dérogations cryptographiques.


## Points à retenir

- Séparer identité, négociation, protection des données, routage et exploitation ; chacune de ces couches exige sa propre preuve.
- IKE SA et Child SA ont des rôles distincts. Un IKE actif ne garantit pas le transfert utilisateur.
- Les SA ESP sont unidirectionnelles ; les compteurs et SPI doivent être interprétés par direction et dans le temps.
- Les sélecteurs de trafic, la route, le NAT et l'ACL ne sont pas des objets interchangeables ; analyser leur interaction.
- Les choix cryptographiques doivent être étroits, actuels, compatibles et mesurés sur la plateforme réelle.
- Les certificats exigent une validation d'identité complète et une procédure d'expiration/rotation.
- MTU et PMTUD doivent être vérifiés avec les tailles de paquets réelles ; une petite requête qui passe ne valide pas les transferts volumineux.
- La haute disponibilité doit être validée de bout en bout : détection, état SA, routes, filtres, puis service applicatif.
- Les diagnostics à haute valeur associent logs IKE, compteurs ESP, routage, métriques d'interface, captures ciblées et tests synthétiques corrélés.
- Tout changement doit être reproductible, accompagné de preuves avant/après, de tests négatifs et d'un rollback validé.

## Références et lectures complémentaires

- **IETF — RFC 7296**, *Internet Key Exchange Protocol Version 2 (IKEv2)* : échanges IKE, authentification, Child SA, rekey et notifications.
- **IETF — RFC 4303**, *IP Encapsulating Security Payload (ESP)* : format ESP, séquences et traitement anti-rejeu.
- **IETF — RFC 4301**, *Security Architecture for the Internet Protocol* : architecture IPsec, SPD et SAD.
- **IETF — RFC 3947 / RFC 3948**, détection NAT et encapsulation UDP d'ESP.
- **IETF — RFC 7383**, fragmentation des messages IKEv2 lorsque prise en charge.
- **IETF — RFC 8229**, TCP Encapsulation of IKE and IPsec Packets, pour des environnements de transport spécifiques.
- **IETF — RFC 8200**, IPv6, notamment les exigences de traitement de la MTU et des messages ICMPv6 associés.
- **NIST SP 800-77 Rev. 1**, *Guide to IPsec VPNs* : conception, déploiement, opérations et sécurité des VPN IPsec.
- Documentation officielle Cisco IOS XE / IKEv2 / IPsec correspondant précisément au modèle et à la version utilisés.
- Documentation du constructeur sur la synchronisation des SA en HA, l'accélération cryptographique, les limites de tunnels et les compteurs anti-rejeu.

Les références sont à consulter dans leur version publiée et applicable à la plateforme. Les politiques cryptographiques peuvent évoluer ; toute suite, groupe ou durée de vie doit être évalué face aux recommandations actuelles de l'organisation avant une mise en production.
