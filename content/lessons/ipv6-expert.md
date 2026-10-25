# IPv6 — Niveau Expert : architecture, résilience, sécurité et exploitation

**Niveau :** Expert  
**Durée indicative :** 6 à 10 heures, selon les laboratoires  
**Prérequis :** avoir terminé `ipv6-debutant.md` et `ipv6-intermediaire.md`, savoir lire les préfixes IPv6, interpréter les RA et les échanges NDP, configurer un adressage statique, manipuler DHCPv6, lire une table de routage et diagnostiquer un problème de MTU.  
**Environnement recommandé :** maquette autorisée avec routeurs et commutateurs IPv6, Cisco IOS/IOS XE ou environnement équivalent, deux à quatre hôtes Linux/Windows, Wireshark, accès aux journaux, et éventuellement un simulateur capable d'exécuter OSPFv3/BGP.

Ce cours est la troisième étape de la série IPv6. Le niveau Débutant a établi la lecture d'adresses, les préfixes, SLAAC, NDP et la configuration élémentaire. Le niveau Intermédiaire a approfondi la conception de préfixes, DHCPv6, les routes, OSPFv3, DNS AAAA, la double pile, PMTUD et les protections RA/NDP. Le niveau Expert suppose ces acquis : il ne recommence pas les définitions une par une, mais apprend à concevoir, prouver, sécuriser et exploiter une architecture IPv6 à plusieurs sites.

> **Principe d'exploitation :** une architecture IPv6 n'est pas maîtrisée parce qu'un ping fonctionne. Il faut pouvoir expliquer l'origine du préfixe, la sélection de l'adresse source, le prochain saut choisi, la politique de routage, la décision de filtrage, le comportement DNS, la visibilité dans les journaux et le plan de retour arrière. Toute commande de changement doit être validée pour le modèle et la version réellement utilisés.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- concevoir un plan IPv6 hiérarchique qui facilite l'agrégation, la délégation et la croissance sans renumérotation permanente ;
- définir une stratégie de délégation de préfixes pour les sites, VLAN, succursales et routeurs clients ;
- analyser les conséquences d'un changement de préfixe, de durée de vie RA ou de délégation DHCPv6-PD ;
- concevoir une politique de routage IPv6 utilisant routes statiques, OSPFv3 et BGP lorsque le besoin le justifie ;
- distinguer l'état des adjacences, la présence d'une route, sa sélection et le transfert réel du paquet ;
- maîtriser les interactions entre GUA, ULA, DNS, choix d'adresse source et applications en double pile ;
- créer une politique de sécurité IPv6 cohérente avec IPv4 sans neutraliser les messages ICMPv6 nécessaires ;
- analyser les risques liés à NDP, aux annonces RA, à DHCPv6, aux en-têtes d'extension et au plan de contrôle ;
- localiser une panne PMTUD, une route retour manquante, une fuite de préfixe ou une mauvaise politique DNS à partir de preuves ;
- planifier une migration IPv4/IPv6 ou IPv6-only avec des critères de succès mesurables et un retour arrière ;
- automatiser des contrôles de préfixes et produire un rapport d'incident reproductible.

## Comment utiliser ce cours

Lis les sections 1 à 5 pour bâtir la stratégie d'adressage et de délégation. Étudie ensuite les sections 6 à 10 pour les protocoles de routage et les services applicatifs. Les sections 11 à 16 abordent la sécurité, la coexistence et l'observabilité. Termine par les laboratoires : chaque exercice exige de recueillir une preuve avant de modifier la configuration, puis d'effectuer un contrôle après changement.

Les schémas SVG illustrent des chemins de paquets ou de contrôle précis ; ils ne représentent pas un chronométrage normatif ni toutes les variations d'implémentation. Si ton lecteur Markdown neutralise les animations SVG, les schémas textuels, les explications et les tableaux gardent leur valeur pédagogique. Le code des SVG est intégré directement au fichier ; aucun fichier image distinct n'est requis.


## 1. Ce qui change au niveau Expert

### 1.1 Passer de la configuration à la gouvernance de l'architecture

Au niveau débutant, la question est souvent : « pourquoi mon hôte n'a-t-il pas de route IPv6 ? ». Au niveau intermédiaire, elle devient : « quel RA a été reçu, quel indicateur a été annoncé et quelle route a été installée ? ». Au niveau expert, il faut répondre en plus à des questions d'architecture : qui est autorisé à annoncer un préfixe, quelle source est de référence pour l'allocation, comment les changements se propagent, comment détecter une incohérence avant qu'elle affecte plusieurs sites, et comment revenir à l'état précédent sans créer un incident plus vaste.

Dans un réseau d'entreprise, IPv6 traverse plusieurs équipes et composants : opérateur, routeur de bordure, réseau WAN, réseau de campus, commutateurs d'accès, services DHCPv6/DNS, pare-feu, postes, serveurs, VPN et supervision. Une panne observable sur un terminal peut donc résulter d'une défaillance de plan d'adressage, de routage, de découverte de voisins, de résolution de nom, de filtrage, de MTU ou de sélection d'adresse. L'expert ne traite pas ces éléments comme un seul bloc ; il construit des hypothèses concurrentes et cherche des observations qui permettent de les départager.

Une bonne architecture possède au minimum une source de vérité pour les préfixes, une convention de nommage, des frontières de routage explicites, des règles de filtrage documentées, un inventaire des RA autorisés, des mécanismes de surveillance et des procédures de changement. Une feuille de calcul isolée ne suffit pas si elle diverge des configurations effectives. Le plan d'adressage doit être relié à l'automatisation, aux demandes de changement et aux données de supervision.

### 1.2 Les plans de contrôle, de données et de gestion

Il est utile de séparer trois domaines :

| Domaine | Questions clés | Exemples d'éléments |
|---|---|---|
| Plan de contrôle | Comment les équipements apprennent-ils les routes et voisinages ? | OSPFv3, BGP, NDP, RA, DHCPv6-PD |
| Plan de données | Le paquet est-il transféré vers la bonne interface ? | FIB, ACL matérielle, MTU, next-hop, pare-feu |
| Plan de gestion | Peut-on administrer, mesurer et auditer le réseau ? | SSH, télémétrie, syslog, API, sauvegardes |

La présence d'une route dans la table de routage ne prouve pas que le paquet peut être transmis : l'interface peut être indisponible, la résolution de voisin peut échouer, une ACL peut le bloquer ou le MTU peut empêcher le transfert d'un paquet volumineux. Inversement, la connectivité locale peut fonctionner même si le service d'administration est indisponible. Le diagnostic expert doit identifier le domaine concerné avant de proposer une modification.

### 1.3 Définir des objectifs de service IPv6

Pour une fonction critique, formule des critères mesurables : taux de succès des sondes IPv6, délai de convergence toléré, taux d'échec de résolution AAAA, durée acceptable de renumérotation, disponibilité d'au moins deux chemins vers un site et délai maximal de détection d'un RA inattendu. Ces objectifs doivent être adaptés à l'application ; un outil de supervision qui ne vérifie que le ping vers une passerelle ne détecte pas forcément une panne HTTPS, DNS ou PMTUD.

Un test de disponibilité doit utiliser une destination et un service représentatifs. Par exemple, une sonde applicative peut résoudre le nom attendu, établir une session TLS, contrôler le certificat puis demander un endpoint de santé. Un test complémentaire par adresse IPv6 fixe aide à séparer DNS et transport. Les sondes ne doivent pas créer une charge incontrôlée ni contourner les règles de sécurité en vigueur.


## 2. Concevoir un plan d'adressage hiérarchique

### 2.1 Allocation, délégation et agrégation sont trois problèmes différents

L'allocation décrit la portion d'espace attribuée à une organisation par son fournisseur ou son registre. La délégation décrit la façon dont cette portion est distribuée aux sites, clients ou routeurs. L'agrégation décrit comment plusieurs routes spécifiques peuvent être représentées par un préfixe moins spécifique lorsqu'elles forment un bloc contigu et que l'annonce agrégée est sûre.

Une erreur de conception consiste à attribuer des préfixes au hasard à chaque VLAN. Le réseau peut fonctionner localement pendant un temps, mais les annonces de routage deviennent nombreuses, les résumés difficiles et la migration d'un site coûteuse. Une hiérarchie simple réserve des blocs aux régions, puis aux sites, puis aux segments, sans exiger que chaque niveau reçoive toujours exactement la même taille. La taille dépend des besoins, des politiques et de l'espace réellement attribué.

### 2.2 Exemple de plan hiérarchique

L'exemple ci-dessous utilise un préfixe de documentation. Il sert uniquement à apprendre la logique de découpage ; `2001:db8::/32` n'est pas un préfixe public à déployer en production.

```text
Préfixe de documentation : 2001:db8:1200::/40
|
+-- Région Nord : 2001:db8:1200::/44
|   +-- Site N1 : 2001:db8:1200::/48
|   |   +-- VLAN utilisateurs : 2001:db8:1200:10::/64
|   |   +-- VLAN serveurs    : 2001:db8:1200:20::/64
|   |   +-- VLAN gestion     : 2001:db8:1200:30::/64
|   +-- Site N2 : 2001:db8:1201::/48
|
+-- Région Sud : 2001:db8:1210::/44
    +-- Site S1 : 2001:db8:1210::/48
```

Ce schéma est illustratif. Vérifie les frontières binaires et les tailles avant d'adopter une convention réelle : le texte des adresses ne doit pas être utilisé comme substitut au calcul de préfixes. Une méthode reproductible consiste à choisir la taille du bloc agrégé, compter les bits consacrés aux régions et sites, puis documenter les plages réservées et les blocs non attribués.

### 2.3 Pourquoi le /64 reste habituel sur un LAN

Un LAN Ethernet utilisant SLAAC repose normalement sur un préfixe de sous-réseau de 64 bits et un identifiant d'interface de 64 bits dans l'architecture usuelle. Il est donc généralement pertinent de réserver un `/64` à chaque segment LAN, même lorsque le nombre d'hôtes est faible. Le calcul « seulement dix postes, donc un `/124` suffit » applique la logique de conservation des adresses IPv4 à un mécanisme IPv6 dont les pratiques d'interface et d'autoconfiguration sont différentes.

Cela ne signifie pas que tout lien IPv6 doit obligatoirement être un `/64` : les liens point-à-point et certains usages spécialisés peuvent employer d'autres préfixes selon la conception, les équipements et les normes applicables. Il faut cependant éviter d'improviser des tailles de préfixe plus longues sur un LAN SLAAC et de conclure ensuite que l'échec de configuration automatique est un défaut du routeur.

### 2.4 Réserver et documenter l'espace non utilisé

Le plan doit distinguer les préfixes actifs, réservés, candidats, en maintenance, retirés et bloqués. Un bloc non utilisé ne doit pas être interprété comme disponible sans vérifier son propriétaire et les éventuelles dépendances de routage. Lors d'une fusion de sites ou d'une acquisition, les chevauchements d'adresses sont plus faciles à gérer s'ils ont été anticipés.

Un inventaire robuste associe à chaque préfixe : identifiant, bloc, site, VLAN ou fonction, passerelle, mécanisme de configuration des hôtes, serveur DHCPv6 éventuel, route de résumé, règle de pare-feu, propriétaire et statut. Pour les blocs publics, indique également la source d'allocation et le chemin de propagation externe. Les adresses de documentation ne doivent jamais être copiées sans remplacement dans un environnement réel.

### 2.5 Agrégation des routes : bénéfices et danger du trou noir

Si un routeur de région détient plusieurs préfixes de sites contigus, il peut annoncer un résumé vers le cœur. Cela réduit la taille des tables et masque certaines modifications internes. Toutefois, annoncer un agrégat ne crée pas de connectivité vers tous ses sous-préfixes. Si le routeur annonce un résumé qui couvre un site absent et ne possède pas de route spécifique vers ce site, il peut recevoir du trafic destiné à un préfixe inexistant et le rejeter localement, voire le faire boucler selon les routes par défaut et l'architecture.

La route de résumé doit refléter une politique de propriété réelle. Une route de rejet/discard pour le résumé peut être utilisée pour éviter une boucle par défaut, mais sa configuration exacte dépend du système. Il faut vérifier que les routes plus spécifiques sont présentes lorsqu'elles sont nécessaires, que la route de résumé est annoncée seulement par le bon domaine et que la route de retour existe pour chaque préfixe actif.

<div class="lesson-figure">
<svg width="900" height="390" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 390" role="img" aria-label="Hiérarchie de préfixes IPv6 et agrégation des routes" style="font-family:Arial,sans-serif">
  <rect x="10" y="10" width="880" height="370" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="38" fill="#e2e8f0" text-anchor="middle" font-size="18" font-weight="700">Plan hiérarchique : blocs attribués puis routes résumées</text>
  <rect x="310" y="55" width="280" height="54" rx="10" fill="#172554" stroke="#60a5fa"/>
  <text x="450" y="77" fill="#dbeafe" text-anchor="middle" font-size="14" font-weight="700">Bloc attribué</text><text x="450" y="95" fill="#bfdbfe" text-anchor="middle" font-size="12">2001:db8:1200::/40 (exemple)</text>
  <path d="M450 109 V132 H220 V154 M450 132 H680 V154" fill="none" stroke="#64748b" stroke-width="2.5"/>
  <rect x="80" y="154" width="280" height="54" rx="10" fill="#064e3b" stroke="#34d399"/><text x="220" y="176" fill="#d1fae5" text-anchor="middle" font-size="14" font-weight="700">Région Nord</text><text x="220" y="194" fill="#a7f3d0" text-anchor="middle" font-size="12">blocs de sites contigus</text>
  <rect x="540" y="154" width="280" height="54" rx="10" fill="#164e63" stroke="#22d3ee"/><text x="680" y="176" fill="#cffafe" text-anchor="middle" font-size="14" font-weight="700">Région Sud</text><text x="680" y="194" fill="#a5f3fc" text-anchor="middle" font-size="12">blocs de sites contigus</text>
  <path d="M220 208 V231 H115 V252 M220 231 H325 V252 M680 208 V231 H575 V252 M680 231 H785 V252" fill="none" stroke="#64748b" stroke-width="2.5"/>
  <g font-size="12" text-anchor="middle"><rect x="55" y="252" width="180" height="48" rx="8" fill="#1e293b" stroke="#94a3b8"/><text x="145" y="271" fill="#e2e8f0">Site N1 /48</text><text x="145" y="288" fill="#94a3b8">LAN en /64</text><rect x="205" y="252" width="180" height="48" rx="8" fill="#1e293b" stroke="#94a3b8"/><text x="295" y="271" fill="#e2e8f0">Site N2 /48</text><text x="295" y="288" fill="#94a3b8">LAN en /64</text><rect x="515" y="252" width="180" height="48" rx="8" fill="#1e293b" stroke="#94a3b8"/><text x="605" y="271" fill="#e2e8f0">Site S1 /48</text><text x="605" y="288" fill="#94a3b8">LAN en /64</text><rect x="665" y="252" width="180" height="48" rx="8" fill="#1e293b" stroke="#94a3b8"/><text x="755" y="271" fill="#e2e8f0">Site S2 /48</text><text x="755" y="288" fill="#94a3b8">LAN en /64</text></g>
  <path d="M82 328 H818" stroke="#475569" stroke-width="1.5" stroke-dasharray="5 6"/>
  <text x="450" y="350" fill="#fde68a" text-anchor="middle" font-size="13" font-weight="700">L'agrégat doit représenter des préfixes réellement joignables</text><text x="450" y="368" fill="#cbd5e1" text-anchor="middle" font-size="11">Une annonce de résumé ne remplace ni les routes spécifiques, ni les routes retour.</text>
  <circle r="5.5" fill="#86efac"><animateMotion path="M450 109 V132 H220 V154" dur="3.2s" repeatCount="indefinite"/></circle>
</svg>
</div>

> **Point de contrôle :** un résumé doit être validé avec la liste des préfixes réellement actifs. Avant annonce, simule ou calcule quels sous-réseaux il couvre et quelles routes spécifiques existent derrière le point d'agrégation.


## 3. Délégation de préfixes et renumérotation contrôlée

### 3.1 Comprendre DHCPv6 Prefix Delegation dans l'architecture

Dans un réseau de fournisseur, un routeur client peut demander un bloc IPv6 afin de l'utiliser sur ses interfaces LAN. Le mécanisme DHCPv6 Prefix Delegation (PD) délègue un préfixe au routeur demandeur ; ce n'est pas la même opération que fournir une adresse à un hôte terminal. Le routeur client subdivise ensuite le bloc qui lui a été attribué, selon la politique du fournisseur et les capacités de son système, pour desservir les LAN internes.

Le bloc délégué peut changer : l'abonnement, le lien d'accès ou la politique fournisseur peuvent provoquer une renumérotation. Un système robuste ne code pas en dur le préfixe courant dans toutes les configurations et listes d'accès. Il doit propager les nouvelles informations, conserver l'ancien préfixe pendant une période de transition définie et retirer ensuite les adresses obsolètes de manière contrôlée. Le comportement dépend du client PD, du serveur, du CPE et de l'implémentation RA.

### 3.2 Durées de vie préférée et valide

Dans SLAAC, l'option de préfixe d'un RA peut communiquer une durée de vie préférée et une durée de vie valide. Une adresse dont la durée de vie préférée est expirée peut devenir dépréciée et ne devrait normalement plus être sélectionnée pour initier de nouvelles connexions lorsque des adresses plus adaptées existent ; elle peut toutefois rester valide et être utilisée pour des connexions existantes pendant une période. Quand la durée de vie valide expire, l'adresse ne doit plus être utilisée.

Cela permet une renumérotation gracieuse : annoncer le nouveau préfixe, le rendre disponible, puis réduire progressivement la préférence de l'ancien avant son expiration. Ce processus doit être coordonné avec DNS, pare-feu, supervision, routes et applications. Une durée de vie mal choisie peut avoir deux conséquences opposées : des clients qui conservent longtemps un préfixe obsolète, ou une interruption trop rapide avant que les systèmes aient mis à jour les enregistrements et les sessions.

### 3.3 Stratégie de renumérotation d'un LAN

Une procédure sûre comprend :

1. enregistrer la configuration initiale et les préfixes annoncés ;
2. attribuer le nouveau préfixe dans le système de référence et configurer le routage amont ;
3. ajuster le RA pour annoncer le nouveau préfixe avec les paramètres validés ;
4. contrôler que les hôtes créent une adresse et réussissent DAD ;
5. vérifier les routes, DNS, filtrage et accès aux services ;
6. conserver le préfixe précédent pendant la période planifiée, si l'architecture le permet ;
7. diminuer sa durée de vie préférée puis suivre l'expiration ;
8. retirer les routes, règles et enregistrements anciens une fois les dépendances vérifiées ;
9. documenter la durée réelle de transition et les exceptions.

Il ne faut pas modifier tous les éléments en même temps sans observation intermédiaire. Si le nouveau RA est annoncé avant que le routeur ait une route valide, les hôtes peuvent former des adresses correctes mais perdre la connectivité. Si DNS est mis à jour avant que le service accepte le nouveau préfixe, certaines connexions échoueront. La séquence exacte dépend de la capacité à héberger temporairement les deux préfixes.

<div class="lesson-figure">
<svg width="900" height="330" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-label="Délégation d'un préfixe IPv6 du fournisseur au routeur client puis aux LAN internes" style="font-family:Arial,sans-serif">
  <rect x="10" y="10" width="880" height="310" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="38" text-anchor="middle" fill="#e2e8f0" font-size="18" font-weight="700">DHCPv6-PD : le bloc est délégué au routeur, pas à chaque PC</text>
  <rect x="42" y="92" width="190" height="72" rx="11" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="137" y="119" text-anchor="middle" fill="#dbeafe" font-size="15" font-weight="700">Fournisseur</text><text x="137" y="140" text-anchor="middle" fill="#bfdbfe" font-size="12">serveur DHCPv6-PD</text>
  <rect x="355" y="92" width="190" height="72" rx="11" fill="#064e3b" stroke="#34d399" stroke-width="2"/><text x="450" y="119" text-anchor="middle" fill="#d1fae5" font-size="15" font-weight="700">Routeur CPE</text><text x="450" y="140" text-anchor="middle" fill="#a7f3d0" font-size="12">reçoit un bloc /56 (ex.)</text>
  <path d="M232 128 H355" stroke="#60a5fa" stroke-width="4" fill="none"/><circle r="5.5" fill="#93c5fd"><animateMotion path="M232 128 H355" dur="2.3s" repeatCount="indefinite"/></circle>
  <rect x="670" y="78" width="180" height="54" rx="10" fill="#164e63" stroke="#22d3ee"/><text x="760" y="100" text-anchor="middle" fill="#cffafe" font-size="13" font-weight="700">LAN utilisateurs /64</text><text x="760" y="117" text-anchor="middle" fill="#a5f3fc" font-size="11">RA + SLAAC</text>
  <rect x="670" y="158" width="180" height="54" rx="10" fill="#164e63" stroke="#22d3ee"/><text x="760" y="180" text-anchor="middle" fill="#cffafe" font-size="13" font-weight="700">LAN serveurs /64</text><text x="760" y="197" text-anchor="middle" fill="#a5f3fc" font-size="11">préfixe distinct</text>
  <path d="M545 114 H610 V105 H670 M610 105 V185 H670" stroke="#34d399" stroke-width="3" fill="none"/>
  <circle r="5" fill="#86efac"><animateMotion path="M545 114 H610 V105 H670" dur="2.8s" repeatCount="indefinite"/></circle>
  <rect x="50" y="235" width="800" height="60" rx="10" fill="#111827" stroke="#475569"/><text x="450" y="258" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">Contrôles indépendants</text><text x="450" y="278" text-anchor="middle" fill="#cbd5e1" font-size="12">Préfixe délégué • route amont • sous-préfixes LAN • RA clients • route de retour</text>
</svg>
</div>

### 3.4 DHCPv6-PD et RFC actuelles

La spécification DHCPv6 a été mise à jour par **RFC 9915 (janvier 2026)**, qui remplace RFC 8415 et inclut des modifications de comportement et de certaines options. Le fait qu'un équipement affiche toujours des noms ou commandes associés à RFC 8415 ne signifie pas qu'il gère automatiquement tous les changements de la spécification récente. Dans un déploiement réel, se référer au guide du fabricant, à la version du client/serveur et aux fonctionnalités explicitement prises en charge. [Référence IETF](https://datatracker.ietf.org/doc/html/rfc9915)

L'architecture doit documenter les rôles : client DHCPv6, serveur DHCPv6, relais éventuel, routeur qui émet des RA, et système qui injecte les routes du bloc délégué. La disponibilité d'une adresse sur l'interface WAN n'implique pas qu'un préfixe a été délégué. De même, recevoir une délégation n'implique pas que les hôtes LAN disposent déjà d'une route par défaut ou que les filtres autorisent les flux correspondants.


## 4. Maîtriser SLAAC, DHCPv6 et les annonces de routeur à l'échelle

### 4.1 Ne pas confondre les responsabilités

À l'échelle d'un campus, plusieurs mécanismes peuvent fonctionner simultanément. Le RA indique notamment si un routeur peut être utilisé comme routeur par défaut, annonce des préfixes on-link et communique des paramètres. SLAAC permet à un hôte de fabriquer une adresse selon le préfixe et les règles locales. DHCPv6 peut fournir des adresses avec état, des options supplémentaires ou des préfixes délégués. DNS fournit les informations de noms, soit via des options compatibles, soit via une configuration indépendante.

Le réseau doit expliquer clairement quel mécanisme gère chaque besoin. Un hôte peut avoir une GUA SLAAC et également une adresse obtenue par DHCPv6. Il peut posséder plusieurs adresses stables ou temporaires. Une configuration qui suppose exactement une adresse par interface est donc fragile ; les outils de sécurité, les journaux et les ACL doivent tolérer les changements attendus tout en détectant les adresses non autorisées.

### 4.2 Plusieurs routeurs sur un même lien

La présence de deux routeurs IPv6 sur le même VLAN peut assurer la résilience, mais elle demande une conception consciente des Router Advertisements. Chaque routeur peut annoncer une préférence, une durée de vie, des préfixes et des paramètres différents. Les hôtes peuvent installer plusieurs routeurs par défaut et choisir selon les règles et l'état de voisinage. La présence de deux RA n'est pas automatiquement une anomalie ; la question est de savoir si chaque annonce appartient à l'architecture prévue.

En cas de panne partielle, un routeur peut continuer à annoncer sa présence sur le lien tout en ayant perdu sa route amont. Les hôtes peuvent alors tenter des connexions sur un chemin dégradé. Une stratégie de haute disponibilité doit vérifier non seulement l'état de l'interface locale, mais aussi la disponibilité du réseau en amont et la qualité de la route annoncée. Les mécanismes disponibles et leur intégration aux RA varient selon les plateformes ; ne suppose pas qu'une fonction propriétaire est activée par défaut.

<div class="lesson-figure">
<svg width="900" height="360" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-label="Deux routeurs IPv6 et la validation des annonces RA" style="font-family:Arial,sans-serif">
  <rect x="10" y="10" width="880" height="340" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="38" text-anchor="middle" fill="#e2e8f0" font-size="18" font-weight="700">RA multiples : la présence ne prouve pas la qualité du chemin</text>
  <rect x="50" y="72" width="190" height="76" rx="12" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="145" y="101" text-anchor="middle" fill="#dbeafe" font-size="16" font-weight="700">Hôte IPv6</text><text x="145" y="122" text-anchor="middle" fill="#bfdbfe" font-size="12">adresses + routes</text>
  <rect x="355" y="72" width="190" height="76" rx="12" fill="#064e3b" stroke="#34d399" stroke-width="2"/><text x="450" y="101" text-anchor="middle" fill="#d1fae5" font-size="16" font-weight="700">R1 légitime</text><text x="450" y="122" text-anchor="middle" fill="#a7f3d0" font-size="12">RA + route amont OK</text>
  <rect x="660" y="72" width="190" height="76" rx="12" fill="#4c1d1d" stroke="#fb7185" stroke-width="2"/><text x="755" y="101" text-anchor="middle" fill="#ffe4e6" font-size="16" font-weight="700">R2 dégradé</text><text x="755" y="122" text-anchor="middle" fill="#fecdd3" font-size="12">RA, mais amont en panne</text>
  <path d="M145 148 V176 H755 V148 M450 148 V176" stroke="#64748b" stroke-width="3" fill="none"/>
  <path d="M450 148 V176 H145 V148" stroke="#34d399" stroke-width="4" fill="none"/>
  <path d="M755 148 V176 H145 V148" stroke="#fb7185" stroke-width="3" fill="none" stroke-dasharray="7 7"/>
  <circle r="5.5" fill="#86efac"><animateMotion path="M450 148 V176 H145 V148" dur="3s" repeatCount="indefinite"/></circle>
  <circle r="5.5" fill="#fb7185"><animateMotion path="M755 148 V176 H145 V148" dur="3.8s" repeatCount="indefinite"/></circle>
  <text x="450" y="202" text-anchor="middle" fill="#cbd5e1" font-size="13">Contrôler l'émetteur du RA, la route par défaut installée et la joignabilité réelle.</text>
  <rect x="70" y="220" width="760" height="90" rx="12" fill="#111827" stroke="#475569"/><text x="450" y="245" text-anchor="middle" fill="#f8fafc" font-size="14" font-weight="700">Ordre de diagnostic</text><text x="450" y="267" text-anchor="middle" fill="#cbd5e1" font-size="12">1. Capturer les RA  →  2. Identifier les routeurs  →  3. Inspecter les routes  →  4. Tester le service</text><text x="450" y="289" text-anchor="middle" fill="#fbbf24" font-size="12">Ne bloque pas tous les RA : protège les ports utilisateurs et conserve les routeurs approuvés.</text>
</svg>
</div>

### 4.3 DHCPv6, relais et séparation des liens

Un serveur DHCPv6 peut desservir plusieurs segments par l'intermédiaire de relais configurés sur les interfaces des routeurs. Une panne de distribution ne doit pas être traitée immédiatement comme un problème d'adresse : vérifie la présence des RA, l'indicateur pertinent, la connectivité du relais vers le serveur, les règles UDP nécessaires, la sélection du scope et les journaux du serveur.

Les identifiants DUID et IAID jouent un rôle dans l'identification du client et des associations. Leur comportement, leur persistance et les politiques d'attribution dépendent du système client et serveur. Quand un terminal est remplacé, cloné ou réinstallé, l'identité vue par DHCPv6 peut changer, ou au contraire persister selon l'implémentation. Il faut éviter d'établir une politique d'inventaire fondée sur l'hypothèse qu'un identifiant est universellement stable.

### 4.4 Durées de vie et cohérence des services

Les durées de vie RA, les baux DHCPv6, la validité des enregistrements DNS, les caches des clients et les règles de pare-feu n'ont pas nécessairement la même temporalité. Lorsque ces valeurs ne sont pas coordonnées, le réseau peut traverser une fenêtre dans laquelle une adresse reste valide mais n'est plus joignable, ou un nom pointe vers une destination déjà retirée. La conception doit spécifier comment les modifications sont propagées, quel composant est autoritaire et comment valider l'état réel après expiration des caches.


## 5. Architecture du routage IPv6

### 5.1 La route existe-t-elle, est-elle sélectionnée, et est-elle exploitable ?

Le diagnostic expert sépare plusieurs étapes. La route peut être absente. Elle peut exister mais perdre la sélection au profit d'une route plus spécifique ou d'une source de routage préférée. Elle peut être installée dans la table de routage mais ne pas être programmée correctement dans le plan de données. Enfin, la route peut fonctionner en aller simple mais échouer au retour. Chaque cas nécessite une preuve différente.

Les tests doivent identifier le préfixe destination, l'adresse source sélectionnée, l'interface de sortie et le prochain saut. Sur IPv6, le prochain saut est souvent une adresse link-local de routeur ; elle n'est exploitable que dans le contexte de l'interface. Une même adresse link-local peut exister sur plusieurs liens, car sa portée est limitée au lien. La documentation des routes et des captures doit donc toujours indiquer l'interface ou la zone concernée.

### 5.2 Routes statiques : utiles mais sensibles aux changements

Une route statique convient à un petit réseau, une route par défaut contrôlée ou une route de secours bien définie. Elle devient risquée lorsqu'elle est la seule représentation d'une topologie dynamique à nombreux sites. Avant de mettre en place une route statique, documente le préfixe, le prochain saut, l'interface, la route retour, les conditions de retrait et le test qui valide la disponibilité.

Exemple de syntaxe Cisco IOS/IOS XE sur un routeur compatible :

```cisco
ipv6 unicast-routing
!
interface GigabitEthernet0/0
 description LAN-UTILISATEURS
 ipv6 address 2001:db8:1200:10::1/64
 no shutdown
!
ipv6 route 2001:db8:2200::/48 2001:db8:ffff:1::2
ipv6 route ::/0 2001:db8:ffff:1::2
```

Cet extrait est uniquement pédagogique : les adresses sont des préfixes de documentation et ne sont pas destinées à un réseau public réel. La possibilité d'utiliser une adresse de prochain saut seule, la résolution de ce prochain saut, la gestion de routes récursives et le comportement en cas de panne dépendent de la plate-forme. N'ajoute pas une route de secours sans définir comment elle devient active et comment éviter une boucle.

### 5.3 OSPFv3 : conception, voisinages et préfixes

OSPFv3 fournit une distribution de routes à état de liens. L'expert doit examiner l'identité du routeur (Router ID, toujours au format 32 bits), les zones, les interfaces qui participent au protocole, les voisinages, les coûts, les LSAs, la base de données et les routes réellement installées. Une adjacence Full ne prouve pas que tous les préfixes attendus sont annoncés ; un préfixe peut être absent de la configuration, filtré, non redistribué ou non installé pour une autre raison.

Selon la version de Cisco IOS XE, OSPFv3 peut être configuré avec des commandes classiques liées aux interfaces ou avec des Address Families qui permettent de transporter IPv6 et IPv4. Les deux styles ne doivent pas être mélangés sans vérifier les fonctionnalités du code logiciel. L'exemple ci-dessous illustre le modèle interface/area fréquemment rencontré ; adapte la syntaxe au guide correspondant précisément à la version du routeur.

```cisco
ipv6 unicast-routing
ipv6 router ospf 10
 router-id 10.10.10.1
!
interface GigabitEthernet0/0
 ipv6 address 2001:db8:1200:10::1/64
 ipv6 ospf 10 area 0
!
interface GigabitEthernet0/1
 ipv6 address 2001:db8:ffff:1::1/64
 ipv6 ospf 10 area 0
```

Le Router ID doit être unique au sein du domaine de routage OSPF concerné, même s'il est représenté par une forme décimale pointée familière à IPv4. La sélection peut dépendre de la configuration et de l'état des interfaces. Il est préférable de le fixer explicitement et de planifier toute modification, car un changement peut provoquer une nouvelle élection ou un redémarrage de processus selon l'implémentation.

Les commandes de vérification usuelles incluent `show ipv6 ospf`, `show ipv6 ospf neighbor`, `show ipv6 ospf database` et `show ipv6 route ospf`, mais l'intitulé exact change selon IOS/IOS XE et la méthode de configuration. Il faut comparer voisinage, base LSDB, route installée et test de données, plutôt que de considérer une seule sortie comme conclusion.

### 5.4 BGP et annonces IPv6

BGP intervient dans les architectures qui échangent des routes entre systèmes autonomes, dans les réseaux de fournisseurs ou dans certains environnements de grande entreprise. Les annonces de préfixes IPv6 utilisent les mécanismes multiprotocoles de BGP. La politique doit expliciter quels préfixes sont autorisés à être annoncés, quels préfixes sont appris, lesquels sont préférés et comment prévenir une fuite de routes.

Un filtre sortant ne doit pas reposer uniquement sur une longueur de préfixe si l'intention est de limiter la propagation à une allocation organisationnelle déterminée. Utilise des préfixes attendus, des listes d'autorisation ou des politiques équivalentes, et vérifie les annonces effectives à l'aide des sorties de la plate-forme ou des collecteurs disponibles. L'agrégation peut masquer des routes spécifiques utiles ou provoquer un trou noir ; les changements doivent donc avoir un plan de retrait et une validation hors bande.

BGP n'est pas une solution à tous les problèmes de routage. Si deux routeurs d'un même campus doivent échanger des routes internes avec convergence rapide, un IGP peut être adapté. Si une organisation possède plusieurs sorties Internet, de la politique de trafic ou des interconnexions externes, BGP peut devenir pertinent. Le choix dépend du domaine administratif, de la maîtrise des politiques, de la taille, des objectifs de disponibilité et des compétences d'exploitation.

### 5.5 Routage, filtrage et route de retour

Une route aller et une route retour doivent être analysées séparément. Des pare-feu stateful, des chemins asymétriques, des politiques BGP ou des agrégats mal construits peuvent rendre les symptômes trompeurs. Lorsqu'une application reçoit SYN mais pas de SYN-ACK, il faut vérifier si la réponse quitte le serveur, quelle source est sélectionnée, où se trouve la route retour et si un filtre intermédiaire bloque la session. Un ping initié depuis un routeur ne reproduit pas nécessairement le même flux que l'application utilisateur.

### 5.6 Agrégation et défauts de couverture

Le résumé IPv6 simplifie l'échange de routes lorsqu'il représente un ensemble contigu et disponible. Si un site est retiré, déplacé ou isolé, la route résumée peut rester annoncée et attirer du trafic vers un routeur qui n'a plus de route valide. Prévoyez une route de rejet adaptée, les règles de redistribution, la surveillance de disponibilité des routes spécifiques et des tests de chemin de bout en bout. La route de rejet protège de certaines boucles ; elle ne remplace pas la preuve que les sous-préfixes actifs sont correctement routés.


## 6. OSPFv3 : diagnostic à partir de preuves

### 6.1 Distinguer voisinage, LSDB et RIB/FIB

Un voisin OSPFv3 peut être Down, Init, 2-Way, ExStart, Exchange, Loading ou Full selon le type de réseau et l'étape de formation de l'adjacence. Le fait d'observer 2-Way entre deux routeurs sur un segment Ethernet broadcast peut être normal si la relation attendue n'exige pas que tous les routeurs forment une adjacence complète entre eux ; l'élection DR/BDR et la topologie du segment interviennent. À l'inverse, des voisins restant en ExStart ou Exchange peuvent indiquer une incompatibilité de MTU, des problèmes de paquets, un filtrage ou une incohérence de paramètres.

Le bon ordre de diagnostic est : interfaces et adresses link-local, timers et paramètres de zone, état des voisins, paquets Hello/DBD si capture disponible, LSDB, routes candidates, route installée, puis transfert réel. Ne change pas le MTU ou les timers sans preuve : ces modifications peuvent provoquer des adjacences instables ou un impact plus large.

<div class="lesson-figure">
<svg width="900" height="355" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 355" role="img" aria-label="Du voisinage OSPFv3 à la route installée puis au transfert réel du paquet IPv6" style="font-family:Arial,sans-serif">
  <rect x="10" y="10" width="880" height="335" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="38" text-anchor="middle" fill="#e2e8f0" font-size="18" font-weight="700">Du protocole au paquet : trois validations indépendantes</text>
  <rect x="40" y="80" width="240" height="70" rx="11" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="160" y="106" text-anchor="middle" fill="#dbeafe" font-size="15" font-weight="700">1. Contrôle OSPFv3</text><text x="160" y="127" text-anchor="middle" fill="#bfdbfe" font-size="12">voisinage + LSDB</text>
  <rect x="330" y="80" width="240" height="70" rx="11" fill="#064e3b" stroke="#34d399" stroke-width="2"/><text x="450" y="106" text-anchor="middle" fill="#d1fae5" font-size="15" font-weight="700">2. RIB / FIB</text><text x="450" y="127" text-anchor="middle" fill="#a7f3d0" font-size="12">route + next-hop</text>
  <rect x="620" y="80" width="240" height="70" rx="11" fill="#164e63" stroke="#22d3ee" stroke-width="2"/><text x="740" y="106" text-anchor="middle" fill="#cffafe" font-size="15" font-weight="700">3. Transfert réel</text><text x="740" y="127" text-anchor="middle" fill="#a5f3fc" font-size="12">NDP + ACL + MTU + retour</text>
  <path d="M280 115 H330 M570 115 H620" stroke="#64748b" stroke-width="4" fill="none"/><circle r="5.5" fill="#93c5fd"><animateMotion path="M280 115 H330" dur="1.7s" repeatCount="indefinite"/></circle><circle r="5.5" fill="#86efac"><animateMotion path="M570 115 H620" dur="1.7s" repeatCount="indefinite"/></circle>
  <path d="M160 150 V180 H740 V150" stroke="#475569" stroke-width="2" stroke-dasharray="5 6" fill="none"/>
  <rect x="70" y="205" width="760" height="95" rx="12" fill="#111827" stroke="#475569"/><text x="450" y="230" text-anchor="middle" fill="#f8fafc" font-size="14" font-weight="700">Interprétation d'une panne</text><text x="450" y="254" text-anchor="middle" fill="#cbd5e1" font-size="12">Voisin Full ≠ préfixe présent dans la LSDB</text><text x="450" y="274" text-anchor="middle" fill="#cbd5e1" font-size="12">Route dans la RIB ≠ next-hop joignable ni paquet autorisé</text><text x="450" y="291" text-anchor="middle" fill="#fbbf24" font-size="12">Collecte la preuve au niveau précis qui échoue.</text>
</svg>
</div>

### 6.2 Interpréter les routes absentes

Si le voisinage est Full mais qu'un préfixe manque, recherche le routeur qui devrait l'origine, confirme que le préfixe est connecté et inclus dans le mécanisme OSPF prévu, puis examine la LSDB. Un filtre de préfixe, un résumé, un type de zone, une redistribution manquante ou une incohérence de politique peut expliquer l'écart. Le routeur de destination peut aussi préférer une route de même préfixe issue d'une autre source en fonction des distances administratives et des règles de sélection.

Les sorties de commande sont des observations datées. Pour une enquête, conserve les informations du routeur source et du routeur de destination à quelques secondes d'intervalle, et compare leur heure. Un événement de convergence pendant la collecte peut donner deux photos différentes du réseau ; note l'heure, l'interface, l'adresse source et le préfixe exact.

### 6.3 Exemple de matrice de diagnostic

| Observation | Hypothèses principales | Preuve suivante |
|---|---|---|
| Pas de voisin | interface down, Hello absents, authentification/paramètres, multicast local | état interface et capture Hello |
| ExStart/Exchange persistant | MTU, identités, perte ou incohérence DBD | détails du voisin et capture DBD |
| Voisin Full, route absente | préfixe non annoncé, filtre, LSDB ou préférence | LSDB, route source, politique |
| Route présente, trafic perdu | FIB, next-hop, NDP, ACL, MTU ou route retour | test source/destination et capture aux frontières |
| Instabilité répétée | liens instables, timers, surcharge du plan de contrôle, configuration divergente | journaux horodatés et compteurs d'interface |

### 6.4 Sécurité du protocole de routage

Les protocoles IGP doivent être protégés par une politique adaptée aux capacités de la plate-forme : limitation des interfaces où les voisins sont acceptés, authentification lorsqu'elle est disponible et requise, filtrage du plan de contrôle, limitation de débit et surveillance des changements d'adjacence. Une interface LAN d'utilisateur ne doit pas former un voisin OSPFv3 par accident. Les commandes de protection et les détails d'authentification varient ; vérifie la documentation de la version logicielle et teste le mécanisme avant de l'appliquer à une adjacency critique.


## 7. DNS, sélection d'adresse et expérience applicative

### 7.1 Un enregistrement AAAA est une déclaration, pas une preuve de service

Un nom DNS peut renvoyer un enregistrement A et un ou plusieurs AAAA. L'application choisit ensuite une destination en fonction de la résolution, de l'algorithme de sélection d'adresse, de son implémentation et du comportement du réseau. Un AAAA obsolète peut détourner certaines connexions vers un serveur injoignable alors que l'adresse IPv4 fonctionne. Le problème peut être intermittent si plusieurs destinations sont publiées ou si les caches conservent des valeurs pendant des durées différentes.

Lors du diagnostic, collecte la résolution DNS depuis le client touché, note le TTL et la destination réellement essayée, puis teste l'adresse choisie sans changer le nom. Compare ensuite l'accès par nom avec l'accès direct, tout en tenant compte de TLS et du nom d'hôte. Un test sur l'adresse brute peut échouer parce que le serveur choisit son certificat ou sa configuration virtuelle selon le nom ; c'est pourquoi il faut comparer le chemin de transport sans abandonner le test applicatif réel.

### 7.2 Happy Eyeballs et double pile

Les clients modernes peuvent essayer IPv6 et IPv4 selon des stratégies conçues pour éviter une longue attente lorsque l'une des familles fonctionne mal. Les détails exacts dépendent de l'OS, du navigateur et de l'application. Une page qui semble fonctionner ne prouve donc pas que IPv6 est sain : le client peut s'être replié sur IPv4. Inversement, l'application peut choisir IPv6 en premier et révéler un défaut de filtrage ou de routage qui n'existe pas sur IPv4.

Pour l'audit, teste explicitement les deux familles lorsqu'elles sont disponibles, en gardant le même serveur applicatif et des conditions comparables. Une différence de comportement doit être reliée aux traces de résolution, aux routes, aux règles de filtrage et aux journaux du serveur. Ne conseille pas de désactiver IPv6 comme solution par défaut : cela peut masquer le symptôme sans corriger l'infrastructure ni les applications.

### 7.3 Adresses temporaires, stables et journaux

SLAAC peut produire des adresses stables et, selon la politique de l'hôte, des adresses temporaires pour réduire certaines possibilités de corrélation d'activité. Les extensions d'adresses temporaires sont décrites par RFC 8981. Les adresses temporaires peuvent changer, ce qui affecte la corrélation des journaux si l'analyse suppose une adresse permanente par terminal. Pour l'exploitation, relie les observations à l'identité de l'hôte, à l'interface, à l'heure, au préfixe et au contexte de session plutôt qu'à une seule adresse considérée immuable.

Cette approche ne signifie pas que chaque hôte doit toujours employer une adresse temporaire, ni que l'adresse suffit à identifier un utilisateur. Les besoins de serveur, de supervision, de conformité, de vie privée et de dépannage peuvent être différents. Choisis explicitement les règles par catégorie d'appareil et documente les conséquences attendues.

### 7.4 DNS inverse et inventaire

La zone inverse IPv6 utilise la représentation nibble du préfixe dans `ip6.arpa`. Les zones longues sont difficiles à maintenir manuellement ; l'automatisation et une convention de nommage limitent les incohérences. Les enregistrements PTR doivent être traités comme une donnée d'exploitation, sans les considérer comme un mécanisme cryptographique de vérification d'identité. Une résolution inverse différente de l'enregistrement direct peut refléter une politique ou une configuration historique ; il faut comprendre la source autoritaire avant de corriger.


## 8. NDP et sécurité des réseaux de couche 2

### 8.1 Menaces opérationnelles

NDP assure plusieurs fonctions nécessaires à IPv6 sur le lien : découverte de routeur, résolution d'adresse de liaison, annonce et surveillance de voisins, ainsi que redirection dans les situations prévues par le protocole. Un acteur qui partage le lien peut tenter de perturber ces échanges à l'aide de messages falsifiés ou inattendus. Les conséquences peuvent comprendre une route par défaut incorrecte, une résolution de voisin trompeuse, une dégradation de connectivité ou une surcharge des équipements.

La conception de sécurité doit identifier les ports de routeurs, les ports utilisateurs, les trunks et les domaines de confiance. RA Guard peut bloquer des Router Advertisements provenant de ports où ils ne sont pas autorisés. DHCPv6 Guard peut contrôler certains messages serveur DHCPv6 selon la plate-forme. Des protections NDP et mécanismes de validation d'adresse peuvent également exister. Il ne faut pas supposer que chaque produit traite tous les en-têtes d'extension, toutes les encapsulations ou tous les cas de contournement de la même façon.

### 8.2 RA Guard : contrôler la frontière de confiance

Une politique RA Guard doit permettre les annonces des routeurs légitimes et empêcher les hôtes de se présenter comme routeurs. Les ports approuvés doivent être identifiés par topologie et maintenus dans l'inventaire. La politique doit être testée avec des captures avant/après et vérifiée sur le matériel réel ; une règle trop stricte peut bloquer un RA légitime et supprimer la route par défaut des clients.

Il faut aussi considérer les limites d'implémentation : certaines fonctionnalités dépendent de la version, des en-têtes d'extension traités par le matériel, du mode de port et de la plateforme de commutation. Les résultats d'un simulateur ou d'une seule famille de commutateurs ne doivent pas être extrapolés à tous les réseaux. La meilleure procédure est de confirmer la documentation, tester des RA légitimes et non autorisés dans une maquette, puis contrôler les journaux et compteurs de protection.

### 8.3 Ne pas bloquer ICMPv6 indistinctement

ICMPv6 n'est pas simplement l'équivalent d'un ping facultatif. Il transporte les messages nécessaires à NDP ainsi que des erreurs utiles au fonctionnement IP, dont Packet Too Big pour PMTUD. Un filtre qui bloque tout ICMPv6 peut casser la découverte de voisins, la découverte de routeur ou la communication pour certains paquets volumineux, alors que les petites requêtes semblent fonctionner.

La politique doit autoriser les types et codes nécessaires, avec une portée et des restrictions adaptées au rôle de l'interface. Les listes exactes dépendent du contexte et des recommandations correspondant aux équipements. Il faut éviter à la fois le blocage global et la permission illimitée sans contrôle. Teste les messages de contrôle attendus et observe les paquets à la frontière où le filtrage s'applique.

### 8.4 ULA, GUA et limites de la sécurité fondée sur l'obscurité

Les Unique Local Addresses servent à l'adressage interne local et ne sont pas conçues pour être globalement routées sur Internet. Les Global Unicast Addresses peuvent être publiquement routables, mais leur présence ne signifie pas qu'un service doit être accessible de l'extérieur. La sécurité repose sur les politiques de filtrage, l'authentification et le durcissement des hôtes, pas sur l'espoir qu'une adresse longue soit difficile à deviner.

Le NAT IPv4 masque souvent l'adressage privé dans les réseaux traditionnels ; IPv6 n'exige pas un mécanisme équivalent de traduction d'adresses pour fonctionner. Il faut donc traduire les objectifs de sécurité en règles explicites : quel flux est autorisé, vers quel service, depuis quelle zone, avec quel retour d'état et quel niveau de journalisation. Le fait qu'un préfixe GUA soit attribué à un site ne signifie pas qu'il doit être annoncé ou accepté sur toutes les interfaces.

### 8.5 Protection du plan de contrôle

Le plan de contrôle d'un routeur possède des ressources finies. Des volumes élevés de messages adressés au routeur lui-même peuvent empêcher le traitement des paquets valides ou la maintenance d'adjacences. Les politiques de control-plane policing, les ACL de plan de contrôle et les limitations spécifiques aux protocoles doivent protéger les services sans bloquer les échanges essentiels. Établis une base de trafic normale avant de fixer des limites ; une limitation trop agressive peut provoquer elle-même une panne lors d'une convergence ou d'une découverte de voisin.

Les pratiques de sécurité opérationnelle IPv6 et la cohérence de la double pile sont détaillées dans [RFC 9099](https://www.rfc-editor.org/rfc/rfc9099.html). Ce document est un point de départ pour construire des règles adaptées au réseau géré, pas une configuration prête à copier telle quelle.


## 9. En-têtes d'extension, filtrage et visibilité

### 9.1 Pourquoi l'analyse d'un paquet IPv6 peut être plus complexe

L'en-tête IPv6 de base peut être suivi par des en-têtes d'extension avant le protocole de couche supérieure. Cette extensibilité offre des possibilités fonctionnelles, mais pose des défis à certains pare-feu, systèmes de détection, collecteurs et chemins de traitement matériel. Certains équipements appliquent des règles différentes si la chaîne d'en-têtes est inattendue, trop longue ou difficile à parser.

L'objectif de sécurité est de définir quels types de paquets doivent être acceptés dans chaque zone, en tenant compte des fonctions réellement utilisées. Un filtrage générique qui rejette aveuglément tous les paquets contenant des en-têtes d'extension peut casser un usage légitime ou une fonction future ; à l'inverse, accepter toute chaîne sans visibilité peut élargir la surface d'attaque. Les tests doivent inclure les chemins applicatifs réels, la journalisation et la capacité du dispositif à parser le paquet.

### 9.2 Fragmentation IPv6 et PMTUD

Dans IPv6, les routeurs intermédiaires ne fragmentent pas les paquets en transit comme un routeur IPv4 pouvait le faire dans certaines conditions historiques. Le système source peut fragmenter si le protocole et l'implémentation l'exigent, et PMTUD s'appuie sur les messages ICMPv6 Packet Too Big pour apprendre une contrainte de chemin. RFC 8201 décrit le mécanisme et les risques de connexions de type black hole lorsque les messages nécessaires sont bloqués ou perdus. [Référence](https://www.rfc-editor.org/rfc/rfc8201.html)

Un symptôme courant est le suivant : établissement de la connexion réussi, petits échanges OK, puis transfert volumineux bloqué. Cela n'est pas une preuve définitive de PMTUD ; il faut vérifier les captures, la MTU de chaque segment, les tunnels, les filtres et les retransmissions. Le test doit mesurer le chemin et ne pas seulement modifier la MTU jusqu'à ce qu'une application semble fonctionner.

<div class="lesson-figure">
<svg width="900" height="350" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 350" role="img" aria-label="Diagnostic d'une panne PMTUD IPv6 et du message Packet Too Big" style="font-family:Arial,sans-serif">
  <rect x="10" y="10" width="880" height="330" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="38" text-anchor="middle" fill="#e2e8f0" font-size="18" font-weight="700">PMTUD IPv6 : mesurer le chemin et préserver ICMPv6 utile</text>
  <rect x="45" y="80" width="150" height="66" rx="11" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="120" y="107" text-anchor="middle" fill="#dbeafe" font-size="15" font-weight="700">Source</text><text x="120" y="126" text-anchor="middle" fill="#bfdbfe" font-size="11">paquet 1450 B</text>
  <rect x="295" y="80" width="160" height="66" rx="11" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/><text x="375" y="107" text-anchor="middle" fill="#f8fafc" font-size="15" font-weight="700">Routeur</text><text x="375" y="126" text-anchor="middle" fill="#cbd5e1" font-size="11">MTU 1400 B</text>
  <rect x="560" y="80" width="150" height="66" rx="11" fill="#064e3b" stroke="#34d399" stroke-width="2"/><text x="635" y="107" text-anchor="middle" fill="#d1fae5" font-size="15" font-weight="700">Destination</text><text x="635" y="126" text-anchor="middle" fill="#a7f3d0" font-size="11">attend le paquet</text>
  <path d="M195 113 H295" stroke="#60a5fa" stroke-width="4"/><path d="M455 113 H560" stroke="#64748b" stroke-width="4" stroke-dasharray="8 7"/>
  <circle r="6" fill="#93c5fd"><animateMotion path="M195 113 H295" dur="2s" repeatCount="indefinite"/></circle>
  <path d="M375 146 V182 H120 V146" fill="none" stroke="#fbbf24" stroke-width="3" stroke-dasharray="7 7"/>
  <circle r="5.5" fill="#fde68a"><animateMotion path="M375 146 V182 H120 V146" dur="3.2s" repeatCount="indefinite"/></circle>
  <text x="250" y="177" fill="#fde68a" font-size="12" text-anchor="middle">ICMPv6 Packet Too Big</text>
  <rect x="735" y="75" width="125" height="78" rx="10" fill="#4c1d1d" stroke="#fb7185"/><text x="797" y="102" text-anchor="middle" fill="#ffe4e6" font-size="13" font-weight="700">Filtre fautif ?</text><text x="797" y="121" text-anchor="middle" fill="#fecdd3" font-size="11">message bloqué</text><text x="797" y="137" text-anchor="middle" fill="#fecdd3" font-size="11">= black hole</text>
  <rect x="55" y="225" width="790" height="78" rx="12" fill="#111827" stroke="#475569"/><text x="450" y="248" text-anchor="middle" fill="#f8fafc" font-size="14" font-weight="700">Méthode de preuve</text><text x="450" y="271" text-anchor="middle" fill="#cbd5e1" font-size="12">Comparer la taille envoyée, le MTU du lien, le message ICMPv6 et les retransmissions.</text><text x="450" y="289" text-anchor="middle" fill="#fbbf24" font-size="12">Ne règle pas la panne en bloquant ou autorisant tout ICMPv6 sans analyse.</text>
</svg>
</div>

### 9.3 Filtrage des erreurs et des en-têtes

Pour chaque frontière, la politique doit expliciter les paquets de contrôle nécessaires, les transports autorisés, les extensions attendues et les comportements de journalisation. L'équipe de sécurité doit travailler avec l'équipe réseau pour identifier les fonctions légitimes, car la même règle peut toucher PMTUD, tunnels, protocoles de routage, surveillance ou services applicatifs. Les systèmes de détection doivent être capables de conserver assez d'informations pour reconstruire la chaîne d'en-têtes et la décision du filtre.

Une capture prise seulement à la source peut montrer qu'un paquet a été émis sans prouver où il a été perdu. Pour localiser une panne, capture de part et d'autre de la frontière suspecte, compare les timestamps et identifie le point exact de divergence. Les compteurs d'ACL et les journaux du pare-feu complètent la capture ; aucun élément pris isolément ne prouve toujours la cause complète.


## 10. Coexistence, migration et IPv6-only

### 10.1 La double pile comme phase de transition

La double pile offre IPv4 et IPv6 en parallèle, ce qui facilite une migration progressive mais double une partie du travail opérationnel : adressage, routes, filtrage, supervision, DNS, gestion de certificats et procédures d'incident doivent tenir compte des deux familles. Un service peut être accessible par IPv4 et défaillant en IPv6, sans que les utilisateurs remarquent la cause si le client revient automatiquement à IPv4. L'objectif d'un déploiement est donc de rendre chaque famille visible et mesurable.

Avant d'activer IPv6 sur un segment, inventorier les hôtes, les services, les règles de filtrage, les RA attendus, les serveurs DNS, les mécanismes de gestion et les outils de surveillance. Vérifier que l'activation ne crée pas un chemin réseau non couvert par les politiques IPv4 existantes. Le contrôle doit comprendre le poste, le segment local, la sortie du site, les services DNS et les journaux d'application.

### 10.2 NAT64, DNS64 et 464XLAT

NAT64 permet à un client IPv6-only de joindre certaines destinations IPv4 à travers un dispositif de traduction, tandis que DNS64 peut synthétiser des réponses AAAA à partir d'enregistrements A lorsqu'une destination est accessible par le chemin NAT64. Ces mécanismes ne sont pas synonymes : la synthèse DNS n'assure pas le transfert des paquets, et la traduction ne résout pas toutes les dépendances applicatives codées en dur à IPv4.

464XLAT combine généralement une traduction côté client (CLAT) et un traducteur de réseau (PLAT/NAT64) pour prendre en charge certains usages IPv4 sur un réseau d'accès IPv6-only. La compatibilité doit être testée avec les applications, les protocoles embarquant des adresses, les connexions entrantes et les besoins de journalisation. Ces mécanismes ne doivent pas être présentés comme une solution universelle ; il faut inventorier les dépendances IPv4 et mesurer les cas d'usage réellement couverts.

### 10.3 Tunnels et risques de chemin non prévu

Un tunnel IPv6 peut assurer la connectivité à travers une infrastructure qui ne transporte pas nativement IPv6, mais il ajoute de l'encapsulation, de la complexité MTU, des dépendances de supervision et des risques de contournement des politiques. Les tunnels automatiques anciens ou non nécessaires doivent être inventoriés puis désactivés selon une procédure validée. Ne supprime pas un tunnel en production avant d'avoir prouvé qu'aucun flux métier ne l'utilise.

Pour un tunnel, documente l'underlay, les endpoints, l'overhead, le MTU intérieur, le routage interne, les mécanismes de détection de panne et la protection des endpoints. La connectivité de l'underlay ne prouve pas le routage du trafic encapsulé. Une capture doit distinguer le paquet extérieur et le paquet IPv6 intérieur ; la supervision doit pouvoir différencier une panne du tunnel d'une panne du réseau transport.

### 10.4 Plan de migration en phases

Une migration maîtrisée peut suivre ces phases :

1. **Découverte :** inventorier les préfixes, appareils, services, RA, DNS, règles et tunnels existants.
2. **Conception :** décider du plan d'adressage, du routage, de la délégation, du modèle de sécurité et de l'observabilité.
3. **Pilote :** activer IPv6 sur une zone limitée, tester les cas normaux et les pannes contrôlées.
4. **Déploiement :** étendre progressivement avec critères de réussite et contrôle d'impact à chaque lot.
5. **Stabilisation :** examiner les journaux, les échecs AAAA, le trafic IPv6, PMTUD et les tickets.
6. **Optimisation :** corriger les écarts, automatiser les contrôles et préparer le retrait éventuel d'une dépendance devenue obsolète.

Chaque phase a besoin d'un critère vérifiable. « La page s'ouvre » n'est pas suffisant. Il faut par exemple confirmer que l'application utilise bien IPv6 lorsque prévu, que le chemin retour fonctionne, que le pare-feu enregistre les sessions, que DNS correspond au service et que les mécanismes de repli ne masquent pas un défaut.


## 11. Politique de pare-feu IPv6 en entreprise

### 11.1 Traduire la politique métier en règles explicites

La politique de sécurité doit décrire les zones, les services, les flux initiés, les réponses permises et les exceptions. Une GUA sur un serveur ne signifie pas que les flux entrants sont permis ; une ULA ne signifie pas non plus que tout accès interne est fiable. La configuration du pare-feu doit être cohérente avec le routage et l'inventaire des préfixes, faute de quoi un chemin peut exister sans être surveillé ou un flux nécessaire peut être bloqué par une règle héritée.

Les listes d'accès sur routeur et les pare-feu stateful n'ont pas le même comportement. Une ACL stateless peut exiger des règles distinctes pour les directions et les messages de retour ; un pare-feu stateful peut suivre l'état des sessions tout en imposant ses politiques pour l'ouverture initiale. Les règles doivent également préserver les types ICMPv6 nécessaires selon le contexte et s'assurer que les services d'administration ne sont accessibles que depuis les sources autorisées.

### 11.2 Anti-spoofing et validation des sources

L'anti-spoofing IPv6 vise à empêcher un segment d'émettre des paquets avec des adresses sources qu'il n'est pas censé utiliser. Dans un réseau multi-sites, la politique dépend du plan d'adressage, des routes autorisées, des tunnels et des mécanismes d'hébergement de préfixes. Un filtrage trop simpliste peut bloquer une adresse temporaire valide ou un flux de mobilité ; à l'inverse, une règle trop permissive permet à un hôte de se faire passer pour une autre source.

Définis les préfixes attendus par interface ou zone, les exceptions documentées et le traitement des paquets link-local, multicast et non spécifiés dans les contextes où ils sont nécessaires. Le filtrage d'entrée depuis Internet doit empêcher les sources impossibles ou internes non autorisées, tout en respectant les usages de contrôle requis. La politique doit être revue à chaque délégation, renumérotation et changement de route.

### 11.3 Journalisation utile

Un journal de pare-feu doit rendre possible la reconstruction du flux : timestamp précis, interface ou zone, source et destination, protocole/port, décision, identifiant de règle et raison du rejet lorsque disponible. Les adresses temporaires et la renumérotation rendent particulièrement utile l'association de ces événements à un inventaire et à un contexte temporel. Les journaux seuls ne suffisent pas à prouver la cause, mais ils permettent de choisir le point de capture suivant.

### 11.4 Revue périodique de cohérence IPv4/IPv6

La revue doit repérer les services ouverts seulement en IPv6, les règles trop permissives en IPv6, les segments sans RA prévu, les enregistrements AAAA non vérifiés, les routes par défaut inattendues et les différences entre politiques de sécurité par famille. Cette revue doit être automatisée autant que possible et intégrer les exceptions documentées : un écart peut être voulu, mais il doit avoir un propriétaire et une justification.


## 12. Observabilité et automatisation des contrôles

### 12.1 Concevoir la visibilité avant l'incident

Une architecture exploitable rend visibles les états utiles avant qu'une panne se produise. Cela inclut l'état des interfaces, les adresses et préfixes présents, les routes attendues, les adjacences de routage, les compteurs d'erreur, les événements NDP/RA, les échecs DNS, les messages Packet Too Big et les journaux des filtres. Il ne s'agit pas de collecter tous les paquets en permanence, mais d'avoir les bons compteurs, les horodatages cohérents et une méthode de capture ciblée.

Définis des seuils adaptés à ton réseau : hausse des échecs de voisins, apparition de RA sur un port inattendu, disparition d'une route de site, changements répétés de préfixe ou hausse des sessions échouées en IPv6. Les valeurs doivent partir d'une ligne de base et être ajustées après observation. Un seuil arbitraire peut créer trop d'alertes ou, pire, masquer un incident réel.

### 12.2 Contrôler les préfixes de façon automatisée

Un contrôle automatisé peut comparer trois ensembles : les préfixes attendus dans l'inventaire, les préfixes configurés sur les interfaces et les routes effectivement présentes. Il doit signaler les différences, mais ne doit pas effacer ou reconfigurer automatiquement les routes sans validation. Les données d'équipement peuvent avoir des formats différents ; normalise les représentations textuelles avant de comparer les valeurs et leurs longueurs de préfixe.

Le pseudocode suivant montre le principe d'un audit, sans dépendre d'une API propriétaire :

```python
expected = {
    "site-n1-users": "2001:db8:1200:10::/64",
    "site-n1-servers": "2001:db8:1200:20::/64",
}

observed = collect_ipv6_prefixes_from_devices()  # fonction à implémenter

for name, prefix in expected.items():
    if prefix not in observed.get(name, set()):
        print(f"ALERTE: préfixe attendu absent: {name} -> {prefix}")

for name, prefixes in observed.items():
    for prefix in prefixes:
        if prefix not in expected.get(name, ""):
            print(f"À examiner: préfixe non inventorié: {name} -> {prefix}")
```

Ce pseudo-exemple ne peut pas être exécuté tel quel : `collect_ipv6_prefixes_from_devices()` représente l'adaptateur à créer pour l'API, le parseur CLI ou l'inventaire utilisé. Dans un script réel, utilise la bibliothèque standard `ipaddress` de Python pour normaliser et comparer les préfixes, puis produis une sortie JSON/CSV. Ne branche pas un script de correction automatique sur un équipement de production sans mode lecture seule, journalisation, revue et procédure de retour arrière.

### 12.3 Contrôler les routes attendues

Le contrôle des routes ne doit pas comparer seulement les textes. Deux routes peuvent utiliser différentes écritures du même préfixe. Il faut normaliser la valeur réseau et le masque de préfixe, puis comparer la source, la préférence, le next-hop et l'interface selon le modèle attendu. Une route supplémentaire peut être correcte, mais elle doit être expliquée. Le rapport doit classer les écarts en criticité au lieu de supposer que toute différence est un incident.

### 12.4 Validation en mode lecture seule

L'automatisation d'exploitation doit commencer en lecture seule : collecte, comparaison, rapport, validation humaine. La modification automatique doit être une étape distincte qui n'est activée que lorsque le modèle est testé, que les préconditions sont vérifiées et que la voie de retour existe. Une tâche planifiée ne doit pas changer les préfixes ou annonces RA sur la base d'une seule lecture potentiellement partielle.


## 13. Méthode de dépannage experte

### 13.1 Définir le flux exact

Avant d'exécuter des commandes, note la source, la destination, le protocole, le port, le nom DNS, l'heure, le VLAN ou segment, l'adresse source sélectionnée et l'objectif fonctionnel. « IPv6 ne marche pas » est trop vague pour produire une hypothèse vérifiable. Précise par exemple : « depuis le poste A du VLAN 20, la résolution AAAA réussit, un TCP SYN est envoyé vers l'adresse publiée, mais aucun SYN-ACK ne revient ; le test vers l'adresse IPv4 du même service fonctionne ».

### 13.2 Ordre de contrôles

1. État de l'interface et adresses présentes.
2. Préfixe, durée de vie et source de configuration de l'adresse.
3. Table de routage et adresse source choisie.
4. Voisin correspondant au prochain saut, si nécessaire.
5. Traces de route et connectivité retour.
6. Règles de pare-feu/ACL aux frontières.
7. Résolution DNS et destination réellement essayée.
8. MTU/PMTUD, tunnels ou particularités de l'application selon le symptôme.
9. Journaux, compteurs et captures à proximité du point de divergence.

Cet ordre est un point de départ, pas une séquence obligatoire pour tous les cas. Si le symptôme indique clairement que seuls les paquets volumineux échouent, examine tôt PMTUD. Si la destination n'est jamais résolue, l'investigation DNS vient avant une analyse détaillée de la route du service.

### 13.3 Fiche d'incident

Pour chaque hypothèse, consigne :

- **Observation :** ce qui est mesuré, avec l'heure et le point de mesure.
- **Hypothèse :** explication possible, sans la présenter comme un fait.
- **Test discriminant :** observation qui permet de confirmer ou d'écarter l'hypothèse.
- **Résultat :** donnée recueillie, y compris si elle contredit l'hypothèse.
- **Action :** le changement ciblé autorisé.
- **Validation :** test fonctionnel, mesures après changement et surveillance.
- **Retour arrière :** condition de déclenchement et étapes de restauration.

### 13.4 Incidents multi-causes

Plusieurs défauts peuvent coexister. Une route par défaut valide ne corrige pas une règle de pare-feu qui bloque TCP. Un DNS AAAA correct ne prouve pas que le préfixe est annoncé sur le LAN. Une adjacence OSPFv3 Full ne prouve pas que l'agrégat est annoncé à BGP. Lorsque la première correction améliore le symptôme sans le supprimer, ne la retire pas immédiatement ni ne présume que l'hypothèse initiale était totalement fausse ; cherche la cause restante en conservant les preuves.


## 14. Schéma de décision : l'adresse existe, mais le service ne répond pas

<div class="lesson-figure">
<svg width="920" height="490" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 490" role="img" aria-label="Arbre de décision pour diagnostiquer une panne de service IPv6" style="font-family:Arial,sans-serif">
  <rect x="10" y="10" width="900" height="470" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="460" y="38" text-anchor="middle" fill="#e2e8f0" font-size="18" font-weight="700">Arbre de décision : distinguer DNS, route, voisinage et filtrage</text>
  <rect x="320" y="55" width="280" height="48" rx="10" fill="#172554" stroke="#60a5fa" stroke-width="2"/><text x="460" y="84" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">Le service IPv6 échoue</text>
  <path d="M460 103 V128 H170 V150 M460 128 V150 M460 128 H750 V150" fill="none" stroke="#64748b" stroke-width="2.5"/>
  <rect x="65" y="150" width="210" height="55" rx="10" fill="#1e293b" stroke="#94a3b8"/><text x="170" y="173" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">DNS AAAA ?</text><text x="170" y="190" text-anchor="middle" fill="#cbd5e1" font-size="11">Résolution / TTL</text>
  <rect x="355" y="150" width="210" height="55" rx="10" fill="#1e293b" stroke="#94a3b8"/><text x="460" y="173" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">Route / source ?</text><text x="460" y="190" text-anchor="middle" fill="#cbd5e1" font-size="11">RIB + adresse utilisée</text>
  <rect x="645" y="150" width="210" height="55" rx="10" fill="#1e293b" stroke="#94a3b8"/><text x="750" y="173" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">Seulement gros flux ?</text><text x="750" y="190" text-anchor="middle" fill="#cbd5e1" font-size="11">MTU / PMTUD</text>
  <path d="M170 205 V235 M460 205 V235 M750 205 V235" fill="none" stroke="#64748b" stroke-width="2.5"/>
  <rect x="65" y="235" width="210" height="62" rx="10" fill="#064e3b" stroke="#34d399"/><text x="170" y="258" text-anchor="middle" fill="#d1fae5" font-size="12" font-weight="700">Comparer A / AAAA</text><text x="170" y="276" text-anchor="middle" fill="#a7f3d0" font-size="11">Tester par nom puis IP</text>
  <rect x="355" y="235" width="210" height="62" rx="10" fill="#164e63" stroke="#22d3ee"/><text x="460" y="258" text-anchor="middle" fill="#cffafe" font-size="12" font-weight="700">Vérifier next-hop</text><text x="460" y="276" text-anchor="middle" fill="#a5f3fc" font-size="11">Route retour + voisin</text>
  <rect x="645" y="235" width="210" height="62" rx="10" fill="#78350f" stroke="#fbbf24"/><text x="750" y="258" text-anchor="middle" fill="#fef3c7" font-size="12" font-weight="700">Capturer Packet Too Big</text><text x="750" y="276" text-anchor="middle" fill="#fde68a" font-size="11">Comparer MTU et filtres</text>
  <path d="M170 297 V327 H460 V350 M460 297 V350 M750 297 V327 H460" fill="none" stroke="#64748b" stroke-width="2.5"/>
  <rect x="215" y="350" width="490" height="70" rx="12" fill="#111827" stroke="#a78bfa" stroke-width="2"/><text x="460" y="375" text-anchor="middle" fill="#ede9fe" font-size="14" font-weight="700">Localiser la frontière où les observations divergent</text><text x="460" y="396" text-anchor="middle" fill="#c4b5fd" font-size="12">Capture des deux côtés + compteurs de filtre + journaux horodatés</text>
  <text x="460" y="451" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">Une commande isolée ne remplace pas un test discriminant.</text>
  <circle r="5" fill="#67e8f9"><animateMotion path="M460 103 V128 H170 V150" dur="3s" repeatCount="indefinite"/></circle>
</svg>
</div>


## 15. Laboratoire 1 — Concevoir un plan d'adressage multi-sites

**Objectif :** créer une hiérarchie cohérente, annoncer des résumés sûrs et expliquer la stratégie d'allocation.

### Topologie de départ

Une organisation possède un site central, deux agences et une zone hébergée. Le préfixe `2001:db8:4400::/40` est attribué à titre pédagogique. Chaque site possède un réseau utilisateurs, un réseau serveurs et un réseau de gestion. Le nombre de VLAN est susceptible d'augmenter.

### Travail demandé

1. Proposer un bloc à chaque site en évitant les chevauchements.
2. Associer un `/64` à chaque LAN SLAAC et réserver de l'espace non attribué pour la croissance.
3. Déterminer quels résumés peuvent être annoncés sans couvrir des préfixes appartenant à un autre site.
4. Décrire les routes requises sur le cœur et sur les routeurs d'accès.
5. Définir les métadonnées nécessaires dans l'inventaire.
6. Fournir un plan de retour arrière si un résumé incorrect est annoncé.

### Contrôles attendus

- Aucun préfixe ne se chevauche involontairement.
- Les préfixes de documentation ne sont pas présentés comme allocations de production.
- Chaque résumé correspond à une zone de responsabilité clairement identifiée.
- Les routes retour sont incluses dans le raisonnement.

**Livrable :** un tableau d'adressage, un schéma de topologie, la liste des annonces résumées et une liste de tests avant/après.


## 16. Laboratoire 2 — Renumérotation SLAAC contrôlée

**Objectif :** observer l'effet des RA et des durées de vie quand un préfixe est remplacé.

### Préparation

Utilise un LAN isolé contenant un routeur IPv6 et deux postes de test. Choisis un préfixe de documentation et vérifie que la maquette ne rejoint pas un environnement de production. Capture ICMPv6 avec Wireshark ou l'outil disponible.

### Procédure

1. Capturer un RA initial et consigner préfixe, drapeaux, préférence du routeur et durées de vie.
2. Relever les adresses du poste et les routes avant changement.
3. Configurer le nouveau préfixe dans la maquette et faire annoncer le nouveau préfixe conformément à la procédure de laboratoire.
4. Capturer les RA et vérifier la création de l'adresse sur le poste.
5. Contrôler DAD, routes, accès à la passerelle et accès à un service de test.
6. Observer le traitement de l'ancien préfixe et noter la différence entre durée de vie préférée et valide.
7. Restaurer la configuration initiale ou compléter la renumérotation jusqu'à l'état attendu.

### Questions d'analyse

- Le poste peut-il conserver plusieurs adresses durant une transition ?
- Le nouveau préfixe est-il routé avant que le client le sélectionne comme source ?
- Que se passe-t-il si DNS référence encore l'ancienne adresse ?
- Quelle preuve permet de déterminer si un échec vient du RA, du routage ou du service ?

**Attention :** les commandes de configuration de RA et les options de durée de vie sont différentes selon les plateformes. Ne copie pas une valeur de laboratoire dans un réseau de production sans calculer l'effet sur les clients.


## 17. Laboratoire 3 — Diagnostiquer une adjacence OSPFv3

**Objectif :** séparer le problème de voisinage du problème d'annonce de préfixe.

### Préparation

Construis deux routeurs reliés par un lien IPv6, chacun desservant un LAN de documentation distinct. Définis les Router ID explicitement et choisis une zone commune pour le premier test. Sauvegarde la configuration de départ.

### Étapes

1. Vérifier le statut des interfaces, les adresses link-local et le ping local.
2. Activer OSPFv3 sur le lien et vérifier l'apparition du voisin.
3. Contrôler le Router ID, les paramètres d'aire, le type de réseau et les sorties de voisinage.
4. Vérifier la présence des préfixes de LAN dans la base et dans les tables de routage.
5. Dans une maquette, retirer l'activation OSPFv3 sur une interface ou modifier un paramètre ciblé ; observer exactement ce qui change.
6. Restaurer la configuration, puis exécuter un test de données entre les deux LAN.
7. Rédiger une chronologie avec une sortie avant et après chaque modification.

### Critères de réussite

- Tu peux distinguer absence d'adjacence et préfixe absent avec voisin Full.
- Tu identifies la source d'une route et le prochain saut choisi.
- Tu démontres le rétablissement avec un test de données, et pas seulement avec l'état du voisin.


## 18. Laboratoire 4 — Incident PMTUD IPv6

**Objectif :** localiser une panne où une session s'établit mais les échanges volumineux échouent.

1. Tester la connectivité de base et le service applicatif en utilisant des tailles de transfert différentes.
2. Capturer sur la source et à la frontière du segment dont la MTU est contrainte.
3. Rechercher les messages ICMPv6 Packet Too Big et relever la MTU annoncée.
4. Comparer le comportement avec et sans la règle fautive dans un environnement de laboratoire autorisé.
5. Vérifier que les messages nécessaires circulent et que le flux applicatif passe après correction.
6. Documenter la cause et les éléments qui la prouvent.

Ne bloque pas globalement ICMPv6 pour simuler une panne. Réalise le scénario uniquement dans une maquette et restaure ensuite la politique correcte.


## 19. Laboratoire 5 — RA non autorisé et frontière de confiance

**Objectif :** valider une protection de couche 2 contre les annonces de routeur indésirables.

Dans un environnement isolé, capture un RA émis depuis un port de routeur légitime, puis un RA de test émis depuis un port utilisateur. Vérifie la route par défaut installée sur le client. Applique RA Guard selon la documentation du commutateur, en déclarant explicitement les ports de confiance et de non-confiance. Répète les captures, vérifie les journaux et confirme que le RA légitime continue à fonctionner.

Le laboratoire n'est réussi que si la protection bloque le cas non autorisé sans couper le fonctionnement légitime. Les capacités et les limitations de RA Guard diffèrent selon les gammes et versions, en particulier quand des en-têtes d'extension ou certaines formes d'encapsulation sont impliqués.


## 20. Laboratoire 6 — Audit double pile d'un service DNS

**Objectif :** identifier pourquoi un service semble fonctionner alors que sa connectivité IPv6 est défectueuse.

1. Interroger les enregistrements A et AAAA du nom testé et conserver les TTL.
2. Tester le service en forçant l'utilisation IPv4 puis IPv6 avec un outil qui permet de séparer les familles.
3. Comparer l'adresse de destination, l'adresse source, la route, le résultat TCP/TLS et les journaux côté serveur.
4. Vérifier que le pare-feu a des règles cohérentes pour les deux familles.
5. Confirmer si une destination AAAA obsolète, une route retour ou un filtre explique le comportement observé.
6. Rédiger les preuves et proposer la correction la plus ciblée.

La correction peut concerner DNS, routage, pare-feu, serveur ou politique d'adresse source. Ne supprime pas un AAAA sans vérifier si le service est censé fournir une connectivité IPv6.


## 21. Laboratoire 7 — Préfixe délégué à un routeur de succursale

**Objectif :** expliquer la chaîne entre délégation du fournisseur et préfixes LAN.

Dans une maquette supportant DHCPv6-PD, configure ou simule un client routeur et un service de délégation. Observe le préfixe reçu, les routes correspondantes, le RA émis sur le LAN et l'adresse formée par un hôte. Puis simule une nouvelle délégation conforme aux capacités du système, et construis le plan de transition.

Vérifie séparément : le statut de la délégation, la route de l'underlay, la route du bloc délégué, le préfixe annoncé aux clients et l'accessibilité du service distant. Le fait qu'un CPE possède une adresse WAN ne prouve pas que le bloc LAN a été délégué. Utilise les outils et commandes du fournisseur de labo plutôt que de copier une syntaxe d'un autre modèle.


## 22. Laboratoire 8 — Revue de sécurité avant activation IPv6

**Objectif :** réaliser un audit pratique d'un segment candidat à l'activation IPv6.

Produis une checklist qui couvre :

- les routeurs autorisés à émettre des RA ;
- les serveurs DHCPv6 et relais attendus ;
- le préfixe global et les ULA éventuelles ;
- les routes et route de retour ;
- les règles IPv6 sur les pare-feu et ACL ;
- les messages ICMPv6 nécessaires ;
- RA Guard, DHCPv6 Guard et contrôles de sources disponibles ;
- DNS AAAA/PTR et certificats applicatifs ;
- journaux, supervision et tests de connectivité ;
- plan de rollback et propriétaire de chaque changement.

Priorise les résultats par impact et vraisemblance. Chaque écart doit contenir une preuve, un responsable et une action prévue. Une checklist remplie sans test ni sortie de commande ne constitue pas une validation suffisante.


## 23. Scénarios d'incident à résoudre

### Scénario A — Une seule agence a perdu l'accès à Internet IPv6

Les postes ont encore une GUA et peuvent joindre leur routeur local. La route par défaut est présente. Le siège et les autres agences fonctionnent. Les journaux montrent que le problème touche les destinations externes du bloc de l'agence, mais les services internes répondent.

**Questions :** quelles hypothèses sont les plus plausibles ? Quels équipements fournissent la preuve ? Comment différencier un problème d'annonce WAN, un filtre de bordure et une route retour manquante ?

**Méthode attendue :** vérifier le préfixe annoncé et sa délégation, comparer les routes sur le routeur de l'agence et au cœur, inspecter les filtres de bordure et les routes de retour. Tester la destination avec une source précise et conserver les timestamps. L'adresse du poste et la route par défaut locale ne prouvent pas que le préfixe de l'agence est correctement propagé hors du site.

### Scénario B — Une nouvelle adresse apparaît, mais le serveur reste inaccessible

Après une renumérotation, le client possède l'ancien et le nouveau préfixe. La résolution DNS renvoie la nouvelle adresse. La connexion échoue pour certains clients, mais pas d'autres.

**Questions :** quels éléments doivent être comparés entre les clients ? Le problème peut-il être dans les durées de vie, DNS, le routage, le pare-feu ou le serveur ?

**Méthode attendue :** noter adresse source réellement sélectionnée, route, destination AAAA, route retour et politique de filtrage. Comparer les TTL DNS, les durées de vie RA et les journaux. Vérifier que le service écoute sur l'adresse prévue et que le préfixe est routé. Ne retirer l'ancien préfixe que quand la période de transition et les dépendances sont vérifiées.

### Scénario C — La connexion TLS démarre puis s'arrête pendant un transfert

Le handshake TCP et TLS fonctionne, mais un transfert de fichier se fige. Le même utilisateur accède au petit endpoint de santé. L'incident touche un chemin via tunnel.

**Méthode attendue :** mesurer le comportement selon la taille, capturer ICMPv6 aux deux extrémités du tunnel, rechercher Packet Too Big, calculer l'overhead d'encapsulation et vérifier la politique de filtrage. Un ping simple ne suffit pas à confirmer le MTU du chemin applicatif.

### Scénario D — Des routes OSPFv3 sont visibles, mais pas le préfixe attendu

L'adjacence est Full. Le préfixe existe sur le routeur distant mais n'est pas installé sur le routeur consommateur.

**Méthode attendue :** inspecter la LSDB, le type de LSA, l'interface où le préfixe est connecté, les politiques de filtrage/redistribution, la préférence de routes concurrentes et le résultat RIB/FIB. Ne redémarre pas OSPF comme première action : collecte des preuves et cherche le point où le préfixe cesse d'exister dans la chaîne.


## 24. Évaluation finale — 20 questions

Réponds avant de consulter les corrections. Une réponse experte doit expliquer le raisonnement et nommer au moins une preuve à recueillir, pas seulement citer une commande.

1. Pourquoi l'attribution de préfixes hiérarchiques simplifie-t-elle l'exploitation ?
2. Pourquoi un résumé IPv6 peut-il provoquer un trou noir ?
3. Pourquoi un `/64` est-il courant pour SLAAC sur un LAN ?
4. Quelle est la différence entre adresse attribuée au WAN et préfixe délégué par DHCPv6-PD ?
5. Pourquoi la renumérotation doit-elle tenir compte de plusieurs durées de vie ?
6. Deux RA sur un lien constituent-ils toujours une anomalie ?
7. Que prouve une adjacence OSPFv3 Full et que ne prouve-t-elle pas ?
8. Pourquoi le Router ID OSPFv3 est-il encore écrit sur 32 bits ?
9. Pourquoi faut-il tester route aller et route retour séparément ?
10. Pourquoi un AAAA publié ne garantit-il pas l'accessibilité du service ?
11. Quelle différence opérationnelle existe entre une adresse stable et une adresse temporaire ?
12. Pourquoi bloquer ICMPv6 en bloc peut-il créer un black hole ?
13. Quelles informations chercher lorsqu'un flux IPv6 échoue seulement sur les paquets volumineux ?
14. Quelle fonction joue RA Guard et quelles erreurs peut produire une mauvaise politique ?
15. Pourquoi les règles de sécurité IPv4 ne suffisent-elles pas à sécuriser un réseau double pile ?
16. Quelle différence y a-t-il entre NAT64 et DNS64 ?
17. Pourquoi les tunnels compliquent-ils MTU et surveillance ?
18. Quelles données un audit automatisé de préfixes doit-il comparer ?
19. Quelles preuves doivent figurer dans un rapport d'incident reproductible ?
20. Quels critères doivent être vérifiés avant de retirer un ancien préfixe ?

### Corrigés commentés

**1.** Les blocs attribués aux sites restent contigus, les routes peuvent être agrégées et les responsabilités sont identifiables. Le plan doit réserver l'espace de croissance et être relié à un inventaire vérifié.

**2.** Un agrégat peut couvrir un sous-préfixe qui n'est plus joignable. Le routeur annonçant l'agrégat peut attirer le trafic sans disposer d'une route spécifique vers la destination.

**3.** `/64` est le préfixe usuel sur un LAN SLAAC, car le fonctionnement d'autoconfiguration et les pratiques d'interface reposent généralement sur un préfixe de sous-réseau de 64 bits. D'autres longueurs existent pour certains usages, mais ne doivent pas être improvisées sur un LAN ordinaire.

**4.** Une adresse WAN concerne l'interface du routeur client. DHCPv6-PD délègue un bloc que le routeur peut utiliser pour adresser des réseaux en aval. Les deux états doivent être vérifiés indépendamment.

**5.** RA, adresses d'hôtes, DHCPv6, DNS, caches, routes et pare-feu peuvent conserver des états pendant des durées différentes. Un retrait mal séquencé peut laisser une destination publiée mais injoignable.

**6.** Non. Plusieurs routeurs peuvent être légitimes et fournir redondance ou différentes routes. Il faut vérifier qui a émis les RA, si les routeurs sont autorisés et si leurs annonces correspondent à la conception.

**7.** Full indique que l'adjacence a atteint un état complet selon OSPFv3. Cela ne garantit pas que le préfixe attendu est annoncé, installé dans RIB/FIB ou joignable par l'application.

**8.** L'identifiant de routeur est un identifiant de 32 bits utilisé par OSPF, même lorsque la famille d'adresses transportées est IPv6. Il ne s'agit pas d'une adresse IPv6 de l'interface.

**9.** Le trafic retour peut suivre une politique différente, manquer une route, être filtré ou emprunter un chemin asymétrique. Tester une seule direction ne prouve pas que la session complète peut fonctionner.

**10.** AAAA est une donnée DNS. Le préfixe peut ne pas être routé, le service peut ne pas écouter, le filtre peut bloquer ou le chemin de retour peut être absent.

**11.** L'adresse stable aide à maintenir une identité d'adresse dans les cas prévus ; une adresse temporaire peut réduire certaines corrélations mais change plus souvent et complexifie la corrélation des journaux. La politique dépend du type de terminal et du besoin opérationnel.

**12.** ICMPv6 porte notamment les messages NDP et Packet Too Big. Leur blocage peut perturber la découverte des voisins ou PMTUD, ce qui laisse passer certains petits paquets mais casse les transferts plus volumineux.

**13.** Capturer les tailles, les MTU, les messages Packet Too Big, les retransmissions et les points de filtrage aux deux côtés du chemin. Vérifier tunnel/encapsulation et ne pas conclure seulement à partir d'un ping.

**14.** RA Guard limite les annonces de routeur aux ports autorisés. Une mauvaise configuration peut laisser passer un RA malveillant ou bloquer les RA légitimes, supprimant la route par défaut des hôtes.

**15.** IPv6 peut disposer de routes, d'adresses et de services différents. Un chemin IPv6 insuffisamment filtré peut contourner l'intention de la politique IPv4.

**16.** NAT64 traduit des flux entre IPv6 et IPv4 ; DNS64 synthétise des réponses AAAA pour aider un client IPv6 à trouver une destination IPv4 via NAT64. DNS64 seul ne transporte aucun paquet.

**17.** L'encapsulation réduit souvent le MTU intérieur utilisable, ajoute des endpoints et peut créer un chemin de données distinct du réseau de transport. Il faut mesurer les deux niveaux et superviser le tunnel.

**18.** Les préfixes de référence, ceux configurés sur les interfaces et ceux installés/annoncés dans les routes, après normalisation du texte et comparaison des longueurs de préfixe. Les écarts doivent être classés et expliqués.

**19.** Heure, source/destination, protocole, observation, hypothèse, test discriminant, résultat, action, validation et rollback. Les preuves doivent venir des points où le trafic diverge, avec captures et journaux horodatés si possible.

**20.** Les nouvelles adresses et routes fonctionnent, DNS reflète la nouvelle cible, les dépendances et les règles sont mises à jour, l'ancien préfixe n'a plus d'usage actif mesurable, les durées de vie sont arrivées à l'étape attendue et le retour arrière est documenté.


## 25. Checklist de changement IPv6

### Avant

- [ ] Préfixes actuels et cible confirmés dans l'inventaire.
- [ ] Route source et route retour vérifiées.
- [ ] RA/DHCPv6 et durées de vie documentés.
- [ ] Enregistrements DNS A/AAAA/PTR et TTL revus.
- [ ] Pare-feu, ACL, tunnels et messages ICMPv6 requis identifiés.
- [ ] Sauvegarde des configurations et collecte des sorties initiales terminées.
- [ ] Fenêtre, responsable, critères de succès et rollback définis.

### Pendant

- [ ] Une modification ciblée à la fois.
- [ ] Capture ou journal conservé pour chaque étape importante.
- [ ] Vérification sur le routeur, le client et le service.
- [ ] Pas de changement de filtrage global non planifié.

### Après

- [ ] Préfixes, routes, voisins, DNS et service vérifiés.
- [ ] Trafic IPv6 réellement observé (pas seulement repli IPv4).
- [ ] Événements de sécurité et journaux revus.
- [ ] Ancienne configuration retirée selon la procédure et non prématurément.
- [ ] Inventaire, documentation et rapport mis à jour.


## 26. Glossaire ciblé

| Terme | Signification opérationnelle |
|---|---|
| Anycast | Même adresse annoncée depuis plusieurs emplacements ; le routage dirige vers l'instance choisie par les routes |
| BGP | Protocole de routage entre systèmes autonomes et outil de politique de routes à grande échelle |
| DAD | Détection d'adresse dupliquée avant ou pendant la mise en service d'une adresse |
| DHCPv6-PD | Délégation d'un préfixe à un routeur demandeur |
| GUA | Adresse unicast globale |
| FIB | Table utilisée par le plan de données pour le transfert des paquets |
| LSDB | Base des informations d'état de liens pour un protocole comme OSPFv3 |
| NDP | Protocole IPv6 de découverte des voisins et des routeurs, fondé sur ICMPv6 |
| PMTUD | Découverte de la MTU utilisable de bout en bout sur un chemin |
| RA Guard | Protection de couche 2 contrôlant les Router Advertisements selon une politique de ports |
| RIB | Table de routage qui contient des routes candidates/installées selon le système |
| SLAAC | Autoconfiguration IPv6 sans état au moyen d'informations du réseau et de la politique locale |
| ULA | Adresse unicast locale, destinée aux communications internes selon une politique d'organisation |


## 27. Références techniques

Les RFC définissent les mécanismes et exigences protocolaires. Les commandes et capacités opérationnelles doivent être vérifiées dans la documentation de la version réellement utilisée.

- **RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification** : https://www.rfc-editor.org/rfc/rfc8200.html
- **RFC 4291 — IP Version 6 Addressing Architecture** : https://www.rfc-editor.org/rfc/rfc4291.html
- **RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)** : https://www.rfc-editor.org/rfc/rfc4861.html
- **RFC 4862 — IPv6 Stateless Address Autoconfiguration** : https://www.rfc-editor.org/rfc/rfc4862.html
- **RFC 9915 — Dynamic Host Configuration Protocol for IPv6 (DHCPv6), janvier 2026** : https://www.rfc-editor.org/rfc/rfc9915.html
- **RFC 6724 — Default Address Selection for IPv6** : https://www.rfc-editor.org/rfc/rfc6724.html
- **RFC 8981 — Temporary Address Extensions for SLAAC** : https://www.rfc-editor.org/rfc/rfc8981.html
- **RFC 8201 — Path MTU Discovery for IPv6** : https://www.rfc-editor.org/rfc/rfc8201.html
- **RFC 9099 — Operational Security Considerations for IPv6 Networks** : https://www.rfc-editor.org/rfc/rfc9099.html
- **Cisco IOS XE — OSPFv3 Address Families** : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_ip6-route-ospfv3-add-fam-xe.html
- **Cisco IOS XE — IPv6 Routing: OSPFv3** : https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-routing/b-ip-routing/m_ip6-route-ospfv3-xe.html

## Conclusion — Le changement de niveau

Le niveau Expert ne consiste pas à mémoriser davantage de commandes. Il consiste à comprendre la chaîne complète : attribution du préfixe, annonce locale, choix d'adresse source, routage, filtrage, MTU, DNS, transfert et preuve opérationnelle. Un opérateur expert sait expliquer pourquoi un paquet prend un chemin donné, quelle hypothèse est démontrée par une capture, quelle modification est la moins risquée et comment prouver que le service est rétabli.

La suite logique de ce cours est une étude d'architecture IPv6 multi-sites : conception de blocs agrégés, BGP/OSPFv3 à l'échelle, résilience, automatisation, délégation dynamique et observabilité avancée. Les notions élémentaires ne devront être reprises que lorsqu'elles éclairent un problème expert précis.
