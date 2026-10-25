# IPv6 — Niveau Débutant

**Niveau :** Débutant  
**Durée indicative :** 4 à 6 heures, selon les laboratoires  
**Prérequis :** connaître les bases d'IPv4, les notions d'adresse IP, de masque/préfixe, de passerelle, de commutation Ethernet et de ping. Aucun cours IPv6 antérieur n'est requis.  
**Environnement recommandé :** Windows 10/11 ou Linux, Packet Tracer ou une maquette Cisco compatible IPv6, accès à un terminal et, si possible, Wireshark.

Ce cours constitue le premier niveau de la série IPv6. Il construit les fondations nécessaires aux futurs cours **`ipv6-intermediaire.md`** et **`ipv6-expert.md`** : format et types d'adresses, préfixes, configuration de base, autoconfiguration, découverte des voisins, routage simple et dépannage méthodique. Les niveaux suivants devront s'appuyer sur ces acquis plutôt que répéter toutes les définitions.

> **Convention pédagogique :** les préfixes `2001:db8::/32` et les adresses qui en dérivent sont réservés à la documentation. Utilise-les dans les exercices, pas comme adresses publiques de production. Les commandes Cisco ci-dessous sont des exemples IOS/IOS XE ; vérifie la syntaxe et les fonctions prises en charge par ton équipement ou ton simulateur.

## Objectifs pédagogiques

À la fin du cours, tu devrais pouvoir :

- expliquer pourquoi IPv6 a été développé et en quoi il diffère d'IPv4 ;
- lire une adresse IPv6 et appliquer correctement les règles de simplification ;
- reconnaître les types d'adresses IPv6 les plus fréquents ;
- interpréter un préfixe comme `/64` et déterminer si deux adresses appartiennent au même préfixe dans les exemples simples ;
- expliquer le rôle d'une adresse link-local et d'une adresse globale ;
- distinguer SLAAC, DHCPv6 avec état et DHCPv6 sans état à un niveau introductif ;
- décrire le rôle de Router Solicitation, Router Advertisement, Neighbor Solicitation et Neighbor Advertisement ;
- configurer une interface IPv6 sur un poste et sur un routeur Cisco compatible ;
- vérifier l'adresse, la route, le voisinage et la connectivité ;
- diagnostiquer les erreurs courantes sans désactiver arbitrairement ICMPv6 ni modifier plusieurs paramètres à la fois.

## Comment utiliser ce cours

Progresse dans l'ordre : commence par la notation et les préfixes, puis étudie les types d'adresses et la manière dont un hôte apprend sa configuration. Ensuite, suis les schémas SVG et les diagrammes textuels. Termine par les laboratoires : tu dois d'abord observer l'état initial, faire une modification ciblée, vérifier le résultat et noter ce que tu as appris.

Les animations illustrent des échanges logiques. Elles ne représentent pas un chronométrage réel, un format exact de trame ou une garantie que chaque système implémente tous les mécanismes de manière identique. Certains lecteurs Markdown neutralisent les SVG ou les animations intégrées ; dans ce cas, ouvre le bloc SVG dans un navigateur moderne ou consulte les diagrammes textuels de remplacement.


## 1. Pourquoi IPv6 ?

### 1.1. Le contexte

IPv4 utilise des adresses de 32 bits. Son espace contient environ 4,3 milliards de valeurs théoriques, dont une partie est réservée à des usages particuliers. L'expansion d'Internet, la multiplication des appareils connectés et la nécessité de disposer de plans d'adressage évolutifs ont rendu l'espace IPv4 public insuffisant pour attribuer une adresse publique à chaque interface selon un modèle simple de bout en bout.

IPv6 utilise des adresses de 128 bits. Il apporte un espace immense, une structure d'en-tête différente, un rôle important accordé à ICMPv6 et des mécanismes de configuration et de découverte adaptés à IPv6. Il n'est pas simplement « IPv4 avec davantage de chiffres » : certains comportements, outils et règles de sécurité sont différents.

La transition ne s'est pas produite partout en une seule fois. Beaucoup de réseaux exploitent IPv4 et IPv6 simultanément : c'est la **double pile** (*dual stack*). D'autres utilisent des tunnels ou des mécanismes de traduction pour relier des environnements qui ne partagent pas la même version IP. Ce cours se concentre d'abord sur le fonctionnement IPv6 natif.

### 1.2. Ce qu'IPv6 ne résout pas automatiquement

Une adresse plus longue ne rend pas un réseau automatiquement sécurisé, rapide ou correctement routé. Il faut toujours un plan d'adressage cohérent, des routes, une politique de filtrage, une résolution DNS adaptée, une supervision et une documentation. Les adresses IPv6 peuvent être attribuées automatiquement, mais « automatique » ne veut pas dire « sans contrôle ».

IPv6 ne supprime pas non plus la nécessité d'un pare-feu. Les politiques doivent couvrir IPv4 et IPv6 lorsque les deux piles sont actives. Un service peut être protégé en IPv4 mais exposé en IPv6 si les règles ne sont pas cohérentes.

### 1.3. Différences essentielles entre IPv4 et IPv6

| Sujet | IPv4 | IPv6 |
|---|---|---|
| Taille d'adresse | 32 bits | 128 bits |
| Écriture courante | Décimale pointée, ex. `192.0.2.10` | Hexadécimale en groupes séparés par `:`, ex. `2001:db8::10` |
| Broadcast IP | Existe | Pas de broadcast IPv6 ; multicast utilisé pour des fonctions de groupe |
| Résolution du voisin local | ARP | Neighbor Discovery Protocol (NDP), fondé sur ICMPv6 |
| Configuration automatique | DHCPv4 notamment | SLAAC et/ou DHCPv6 selon le réseau |
| Fragmentation par les routeurs | IPv4 peut être fragmenté selon les conditions et les drapeaux | Les routeurs IPv6 ne fragmentent pas les paquets en transit ; la source peut fragmenter selon le mécanisme prévu |
| Découverte du routeur | Peut utiliser DHCP et protocoles locaux ; dépend de l'architecture | Router Advertisement (RA) fait partie de Neighbor Discovery |
| Vérification du chemin MTU | ICMP selon le cas | ICMPv6 Packet Too Big joue un rôle important dans PMTUD |

Ne retiens pas ces différences comme une liste isolée. Elles expliquent pourquoi des habitudes IPv4 ne doivent pas être copiées mécaniquement sur IPv6. Par exemple, une capture IPv6 ne montrera pas de requête ARP ; tu y verras plutôt des messages ICMPv6 de découverte des voisins.

## 2. Lire une adresse IPv6

### 2.1. Les huit groupes

Une adresse IPv6 fait 128 bits. Elle est généralement affichée sous forme de huit groupes hexadécimaux de 16 bits, séparés par des deux-points. Chaque groupe peut contenir de un à quatre chiffres hexadécimaux lorsqu'on omet les zéros de tête.

```text
Adresse complète : 2001:0db8:0000:0000:02aa:00ff:fe28:9c5a
                    |---| |---| |---| |---| |---| |---| |---| |---|
                    16 bits par groupe × 8 groupes = 128 bits
```

Les chiffres hexadécimaux vont de `0` à `9`, puis de `a` à `f` (les majuscules sont aussi valides). La représentation textuelle peut varier tout en décrivant exactement la même valeur binaire.

### 2.2. Règle 1 : supprimer les zéros au début d'un groupe

Dans chaque groupe, les zéros placés au début peuvent être retirés. Ils ne peuvent pas être retirés au milieu ou à la fin si cela change la valeur.

```text
0db8  devient db8
000a  devient a
00f0  devient f0
0000  devient 0
```

Exemple :

```text
2001:0db8:0000:0000:0000:0000:0000:0025
2001:db8:0:0:0:0:0:25
```

Ces deux écritures désignent la même adresse. Il ne faut pas confondre la suppression des zéros de tête avec la suppression de tous les zéros d'un groupe : `00f0` devient `f0`, pas `f`.

### 2.3. Règle 2 : compresser une séquence de groupes nuls avec `::`

Une séquence contiguë d'un ou plusieurs groupes `0000` peut être remplacée par `::`. Cette compression ne peut apparaître **qu'une seule fois** dans une adresse, car le nombre de groupes omis doit pouvoir être déterminé sans ambiguïté.

```text
2001:0db8:0000:0000:0000:0000:0000:0025
→ 2001:db8::25
```

Une adresse telle que `2001:db8::25` peut être réécrite en huit groupes en comptant ceux déjà présents et en remplissant la séquence `::` par le nombre de groupes nuls nécessaire.

À éviter :

```text
2001:db8::1::5   ← invalide : deux occurrences de ::
```

Si plusieurs séquences de zéros de même longueur existent, la convention d'écriture canonique privilégie la première séquence la plus longue. En pratique, l'essentiel pour un débutant est de savoir lire et développer une adresse sans inventer ni supprimer de groupes.

### 2.4. Schéma : les 128 bits et le préfixe

<div class="schema-svg">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-labelledby="s1title s1desc">
<title id="s1title">Structure d'une adresse IPv6</title><desc id="s1desc">Une adresse IPv6 comprend huit groupes de seize bits, soit 128 bits au total. Un préfixe /64 sépare les 64 bits réseau des 64 bits d'identifiant d'interface dans le cas courant d'un LAN.</desc>
<style>.bg{fill:#0b1220}.t{fill:#f8fafc;font:700 20px system-ui}.lab{fill:#cbd5e1;font:14px system-ui}.net{fill:#14532d;stroke:#4ade80;stroke-width:1.5}.iid{fill:#1e3a8a;stroke:#60a5fa;stroke-width:1.5}.small{fill:#94a3b8;font:12px system-ui}</style>
<rect class="bg" width="900" height="330" rx="18"/><text x="28" y="38" class="t">IPv6 : 128 bits au total</text>
<text x="450" y="80" text-anchor="middle" class="lab">2001 : 0db8 : 1234 : 0001 : 0000 : 0000 : 0000 : 0042</text>
<g transform="translate(28 104)"><rect class="net" width="416" height="78" rx="10"/><rect class="iid" x="428" width="416" height="78" rx="10"/><text x="208" y="30" text-anchor="middle" class="t">Préfixe réseau</text><text x="208" y="54" text-anchor="middle" class="lab">64 bits · exemple /64</text><text x="636" y="30" text-anchor="middle" class="t">Identifiant d’interface</text><text x="636" y="54" text-anchor="middle" class="lab">64 bits dans ce schéma</text></g>
<path d="M444 194 V217" stroke="#fbbf24" stroke-width="2" stroke-dasharray="4 4"/><text x="450" y="242" text-anchor="middle" class="lab">Le /64 décrit la longueur du préfixe ; il ne s'écrit pas dans les 128 bits.</text><text x="450" y="276" text-anchor="middle" class="small">Schéma courant pour un LAN Ethernet avec SLAAC, pas une règle universelle pour chaque usage IPv6.</text>
</svg></div>

Dans un LAN Ethernet classique qui utilise SLAAC, un préfixe `/64` est très courant : les 64 premiers bits identifient le préfixe de sous-réseau, et les 64 bits restants constituent l'identifiant d'interface dans ce modèle. Le suffixe n'est pas nécessairement créé à partir de l'adresse MAC : les systèmes modernes peuvent employer des identifiants stables privés ou des adresses temporaires.

Un préfixe `/64` n'est pas une règle universelle pour chaque contexte IPv6. Les liens point à point, les routes agrégées et d'autres usages peuvent employer d'autres longueurs. Pour un LAN qui doit utiliser SLAAC selon le modèle usuel, retiens le `/64` comme valeur de référence et vérifie toujours la conception du réseau.

### 2.5. S'exercer à développer des adresses

Développe chaque adresse en huit groupes de quatre chiffres hexadécimaux :

1. `2001:db8::1`
2. `2001:db8:10:2::a`
3. `fe80::1234`
4. `::1`

Méthode : compte les groupes visibles, calcule combien de groupes sont absents, puis remplace `::` par exactement autant de groupes `0000`. N'ajoute pas un groupe supplémentaire : une adresse IPv6 doit toujours totaliser huit groupes de 16 bits dans sa représentation développée.

**Corrigé :**

```text
2001:db8::1       = 2001:0db8:0000:0000:0000:0000:0000:0001
2001:db8:10:2::a  = 2001:0db8:0010:0002:0000:0000:0000:000a
fe80::1234        = fe80:0000:0000:0000:0000:0000:0000:1234
::1               = 0000:0000:0000:0000:0000:0000:0000:0001
```

## 3. Comprendre les préfixes IPv6

### 3.1. Qu'est-ce qu'un préfixe ?

Le nombre après la barre oblique indique le nombre de bits initiaux qui constituent le préfixe réseau. Dans `2001:db8:10:20::15/64`, les 64 premiers bits forment le préfixe `2001:db8:10:20::/64` ; le reste identifie l'interface dans ce préfixe.

Le préfixe est essentiel : une adresse seule ne suffit pas pour décider si une destination est locale. L'hôte compare la destination aux préfixes de ses routes. Si la destination correspond à un préfixe directement connecté, il tente de joindre le voisin sur ce lien. Sinon, il transmet le paquet à un prochain saut indiqué par la table de routage, souvent le routeur par défaut.

### 3.2. Exemple de LAN

```text
Préfixe du LAN : 2001:db8:10:20::/64
PC-A           : 2001:db8:10:20::10/64
PC-B           : 2001:db8:10:20::20/64
Routeur LAN    : 2001:db8:10:20::1/64
```

Dans cet exemple, les trois interfaces partagent le même préfixe `/64`. PC-A peut chercher PC-B directement sur le lien. Pour une adresse dans `2001:db8:10:30::/64`, il utilisera normalement une route vers un routeur.

### 3.3. Quelques longueurs fréquentes

| Préfixe | Interprétation pédagogique | Exemple d'usage courant |
|---|---|---|
| `/128` | Une adresse précise | Route d'hôte ou adresse d'interface |
| `/64` | Un sous-réseau de LAN IPv6 usuel | LAN Ethernet avec SLAAC |
| `/56` | Bloc pouvant contenir plusieurs sous-réseaux `/64` | Délégation à un site ou à un client, selon politique |
| `/48` | Bloc plus vaste contenant de nombreux `/64` | Site ou organisation, selon allocation |
| `/32` | Agrégat plus vaste dans certains plans d'allocation | Allocation opérateur/organisation selon contexte |

Ces lignes ne constituent pas une règle d'attribution universelle. Les politiques de délégation dépendent des fournisseurs, des registres, de la taille du site et du plan de routage. Pour ce cours, apprends surtout que plus le nombre de bits du préfixe est petit, plus le bloc est grand.

### 3.4. Exercices sur les préfixes

Pour le préfixe `2001:db8:abcd:10::/64`, indique si les adresses suivantes appartiennent au même `/64` :

- A : `2001:db8:abcd:10::5`
- B : `2001:db8:abcd:10::99`
- C : `2001:db8:abcd:11::5`

**Réponse :** A et B partagent le préfixe `2001:db8:abcd:10::/64`. C appartient au préfixe `2001:db8:abcd:11::/64`, qui est différent. Compare les 64 premiers bits, pas seulement le début visuel de l'adresse.

## 4. Types d'adresses IPv6 à connaître

### 4.1. Global unicast

Les adresses *global unicast* sont destinées à l'adressage unicast global selon l'allocation et la politique de routage. Le bloc actuellement connu `2000::/3` correspond à une grande partie de l'espace global unicast. Une adresse globale ne signifie pas que tout Internet peut nécessairement l'atteindre : les routes, les filtres, les politiques d'opérateur et l'état du service comptent toujours.

Les adresses `2001:db8::/32` sont réservées à la documentation. Elles servent dans les manuels, les exemples et les laboratoires. Ne les configure pas comme adresses publiques de production.

### 4.2. Link-local : `fe80::/10`

Les adresses link-local sont valides sur le lien local. Elles servent notamment à Neighbor Discovery et à de nombreux échanges de contrôle. Les routeurs ne les transfèrent pas comme des adresses de destination ordinaires vers d'autres liens. Une interface IPv6 possède normalement une adresse link-local lorsqu'IPv6 est activé, selon le système et sa configuration.

Une adresse link-local peut apparaître dans une commande de route par défaut ou comme adresse du prochain saut. Comme la même plage peut être utilisée sur de nombreux liens, un outil ou une commande peut avoir besoin d'indiquer l'interface de sortie, par exemple un identifiant de zone sur certains systèmes. Ne suppose pas qu'une adresse `fe80::...` est globalement unique.

### 4.3. Loopback : `::1`

`::1/128` est l'adresse de boucle locale IPv6, équivalente dans son rôle à `127.0.0.1` en IPv4. Elle permet de tester la pile IP locale sans passer par le réseau physique. Un ping vers `::1` qui échoue peut indiquer un problème local de pile, de configuration ou de politique ; il ne prouve rien sur le fonctionnement d'un routeur distant.

### 4.4. Adresse non spécifiée : `::`

`::/128` est l'adresse non spécifiée. Elle ne signifie pas « toutes les interfaces » comme une adresse d'écoute peut être interprétée dans certains contextes applicatifs ; au niveau du protocole, elle signifie qu'aucune adresse source précise n'est encore indiquée. Elle apparaît dans des procédures de démarrage et ne doit pas être assignée comme adresse normale à une interface.

### 4.5. Unique local : `fc00::/7`

Les adresses unique local (ULA) sont destinées aux communications locales ou inter-sites privées. En pratique, les préfixes `fd00::/8` sont couramment rencontrés pour des ULA générées localement. Elles ne sont pas destinées à être routées globalement sur Internet, même si elles peuvent être routées dans une organisation selon son architecture.

### 4.6. Multicast : `ff00::/8`

IPv6 utilise le multicast pour envoyer un paquet à un groupe d'interfaces. Il n'existe pas de broadcast IPv6. Certaines adresses multicast sont utilisées pour des groupes bien définis, notamment pour la découverte de voisins. Ne remplace pas « broadcast » par « multicast » sans comprendre le groupe visé et la portée de l'adresse.

### 4.7. Tableau récapitulatif

| Type | Préfixe / exemple | Fonction de base | À retenir |
|---|---|---|---|
| Global unicast | `2000::/3` | Adressage global selon politiques de routage | Routabilité dépend aussi des routes et filtres |
| Documentation | `2001:db8::/32` | Exemples et documentation | Ne pas utiliser en production publique |
| Link-local | `fe80::/10` | Communication sur le lien | Non transférée par les routeurs comme destination ordinaire |
| Loopback | `::1/128` | Test local de la pile | Ne traverse pas le réseau |
| Non spécifiée | `::/128` | Absence d'adresse source définie dans certains échanges | Pas une adresse normale à assigner |
| Unique local | `fc00::/7`, souvent `fd00::/8` | Adressage local/interne | Ne constitue pas une adresse publique globale |
| Multicast | `ff00::/8` | Communication de groupe | IPv6 n'utilise pas le broadcast |

## 5. Configuration automatique : SLAAC et DHCPv6

### 5.1. Pourquoi plusieurs mécanismes ?

IPv6 peut obtenir des informations de configuration de plusieurs façons. Un hôte peut construire une adresse avec **SLAAC** (*Stateless Address Autoconfiguration*) à partir des informations reçues dans les Router Advertisements. Il peut aussi utiliser DHCPv6 pour obtenir certaines informations ou des adresses selon le mode configuré. Les deux mécanismes peuvent coexister.

Il est important de ne pas confondre :

- **SLAAC :** l'hôte utilise les informations du préfixe annoncées par le routeur et génère une adresse selon ses règles locales ;
- **DHCPv6 avec état :** un serveur DHCPv6 attribue et suit des adresses selon le mode prévu ;
- **DHCPv6 sans état :** l'hôte peut obtenir d'autres paramètres via DHCPv6 sans que le serveur attribue nécessairement l'adresse utilisée ;
- **Router Advertisement (RA) :** annonce de routeur ICMPv6 qui fournit des informations de préfixe et de configuration. Les indicateurs du RA influencent le comportement du client.

Les indicateurs exacts et la sélection du mécanisme dépendent de la configuration du routeur et du système client. Ne déduis pas qu'un client utilise DHCPv6 uniquement parce qu'il possède une adresse IPv6.

### 5.2. Étapes générales de SLAAC

1. L'interface active IPv6 et possède une adresse link-local.
2. L'hôte peut envoyer un Router Solicitation (RS) pour solliciter rapidement un RA, ou attendre un RA périodique.
3. Le routeur envoie un Router Advertisement (RA) avec les informations disponibles : préfixes, durée de validité et autres paramètres.
4. Si les conditions sont réunies, l'hôte construit une adresse à partir du préfixe annoncé et d'un identifiant d'interface généré par son système.
5. L'hôte effectue une détection de doublon (DAD) pour vérifier qu'une autre interface n'utilise pas déjà l'adresse sur le lien.
6. L'hôte installe ou actualise ses informations de routage, dont une route par défaut si le RA fournit les informations appropriées.

<div class="schema-svg">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 360" role="img" aria-labelledby="s2title s2desc">
<title id="s2title">SLAAC : découverte du routeur et autoconfiguration</title><desc id="s2desc">Un hôte envoie Router Solicitation. Le routeur répond par Router Advertisement qui fournit le préfixe et des paramètres. L'hôte construit une adresse, vérifie l'absence de doublon et installe une route par défaut si les informations le permettent.</desc>
<style>.bg{fill:#0b1220}.t{fill:#f8fafc;font:700 18px system-ui}.lab{fill:#cbd5e1;font:14px system-ui}.node{fill:#172554;stroke:#60a5fa;stroke-width:1.5}.router{fill:#14532d;stroke:#4ade80;stroke-width:1.5}.line{stroke:#94a3b8;stroke-width:2;fill:none}.pkt{fill:#fbbf24}.small{fill:#94a3b8;font:12px system-ui}</style>
<rect class="bg" width="900" height="360" rx="18"/><text x="28" y="34" class="t">SLAAC : une adresse se configure grâce aux annonces du routeur</text>
<rect class="node" x="42" y="92" width="210" height="78" rx="12"/><text x="147" y="122" text-anchor="middle" class="t">Hôte IPv6</text><text x="147" y="146" text-anchor="middle" class="lab">Adresse link-local</text>
<rect class="router" x="648" y="92" width="210" height="78" rx="12"/><text x="753" y="122" text-anchor="middle" class="t">Routeur</text><text x="753" y="146" text-anchor="middle" class="lab">Émet des RA</text>
<path class="line" d="M252 110 H648"/><path class="line" d="M648 152 H252"/>
<text x="450" y="95" text-anchor="middle" class="lab">Router Solicitation (RS)</text><text x="450" y="174" text-anchor="middle" class="lab">Router Advertisement (RA)</text>
<circle class="pkt"><animateMotion dur="3.2s" repeatCount="indefinite" path="M252 110 H648"/></circle><circle class="pkt"><animateMotion dur="3.2s" begin="1.6s" repeatCount="indefinite" path="M648 152 H252"/></circle>
<g transform="translate(42 218)"><rect x="0" y="0" width="190" height="74" rx="10" fill="#1e293b" stroke="#64748b"/><text x="95" y="27" text-anchor="middle" class="t">1. Recevoir le RA</text><text x="95" y="50" text-anchor="middle" class="lab">Préfixe, drapeaux, durée</text>
<path d="M190 37 H218" class="line"/><path d="M218 37 l-8 -5 v10 z" fill="#94a3b8"/>
<rect x="218" y="0" width="190" height="74" rx="10" fill="#1e293b" stroke="#64748b"/><text x="313" y="27" text-anchor="middle" class="t">2. Construire</text><text x="313" y="50" text-anchor="middle" class="lab">Adresse dans le préfixe</text>
<path d="M408 37 H436" class="line"/><path d="M436 37 l-8 -5 v10 z" fill="#94a3b8"/>
<rect x="436" y="0" width="190" height="74" rx="10" fill="#1e293b" stroke="#64748b"/><text x="531" y="27" text-anchor="middle" class="t">3. Vérifier</text><text x="531" y="50" text-anchor="middle" class="lab">DAD : doublon éventuel</text>
<path d="M626 37 H654" class="line"/><path d="M654 37 l-8 -5 v10 z" fill="#94a3b8"/>
<rect x="654" y="0" width="160" height="74" rx="10" fill="#14532d" stroke="#4ade80"/><text x="734" y="27" text-anchor="middle" class="t">4. Utiliser</text><text x="734" y="50" text-anchor="middle" class="lab">Adresse et routes</text></g>
<text x="450" y="326" text-anchor="middle" class="small">Les détails dépendent des indicateurs RA, du système et de la politique réseau. SLAAC n'est pas synonyme de DHCPv6.</text>
</svg></div>

**Point essentiel :** SLAAC ne signifie pas « le routeur donne directement chaque adresse ». Le routeur annonce un préfixe et des paramètres ; le client construit son adresse en fonction de ce qu'il reçoit et de son implémentation.

### 5.3. Adresse stable et adresse temporaire

Les systèmes modernes peuvent créer un identifiant d'interface stable mais non dérivé directement de l'adresse MAC, ainsi que des adresses temporaires utilisées notamment pour certaines connexions sortantes. Cela limite la possibilité de suivre un appareil uniquement en observant un identifiant d'interface persistant.

Par conséquent, ne suppose pas que les derniers 64 bits correspondent toujours à l'adresse MAC. Cette ancienne méthode a existé, mais elle n'est pas la seule et ne doit pas être la règle d'interprétation pour les appareils actuels.

### 5.4. Comment observer la configuration

Sur un poste, regarde les adresses de chaque interface et les routes. Une interface peut posséder simultanément une adresse link-local et une ou plusieurs adresses unicast supplémentaires. La présence de plusieurs adresses n'est donc pas automatiquement une erreur.

Sous Windows :

```powershell
ipconfig /all
netsh interface ipv6 show addresses
netsh interface ipv6 show route
```

Sous Linux :

```bash
ip -6 address show
ip -6 route show
```

Cherche le préfixe, l'état de l'interface et la route par défaut. Si une adresse est marquée temporaire ou préférée/dépréciée, son état peut refléter le cycle de vie IPv6 plutôt qu'un incident.

## 6. Neighbor Discovery Protocol (NDP)

### 6.1. NDP remplace plusieurs tâches réalisées autrement en IPv4

En IPv4, ARP est couramment utilisé pour associer une adresse IPv4 locale à une adresse MAC. IPv6 utilise le **Neighbor Discovery Protocol (NDP)**, qui s'appuie sur ICMPv6 et réalise plusieurs fonctions : découverte des routeurs, découverte des voisins, résolution des adresses de couche liaison, détection d'adresses dupliquées et suivi de l'accessibilité de certains voisins.

NDP ne se limite donc pas à « ARP en IPv6 ». Il rassemble plusieurs mécanismes qui participent au fonctionnement normal du lien IPv6. Un filtrage incorrect d'ICMPv6 peut perturber l'adressage, la découverte de routeur, la résolution de voisins et d'autres fonctions.

### 6.2. Les quatre messages à reconnaître

| Message | Abréviation | Rôle introductif |
|---|---|---|
| Router Solicitation | RS | Un hôte sollicite rapidement des annonces de routeur |
| Router Advertisement | RA | Un routeur annonce sa présence et des paramètres IPv6 |
| Neighbor Solicitation | NS | Un hôte recherche un voisin ou vérifie une adresse dans certains mécanismes |
| Neighbor Advertisement | NA | Un voisin annonce une information de voisinage ou répond à une sollicitation |

La détection d'adresses dupliquées (DAD) utilise également des Neighbor Solicitation, selon des règles particulières. Un NS envoyé pour DAD ne se lit donc pas exactement comme une recherche ordinaire de l'adresse MAC d'un voisin.

### 6.3. Résolution de voisin

Lorsqu'un hôte veut envoyer un paquet à une autre adresse IPv6 directement connectée, il doit déterminer l'adresse de couche liaison du prochain destinataire. Il envoie une Neighbor Solicitation associée au groupe multicast sollicité de la cible. Le voisin concerné répond normalement par une Neighbor Advertisement. Le résultat peut être enregistré dans le cache des voisins.

<div class="schema-svg">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 320" role="img" aria-labelledby="s3title s3desc">
<title id="s3title">Neighbor Discovery : résolution de voisin IPv6</title><desc id="s3desc">Un hôte cherche l'adresse de couche deux d'un voisin IPv6. Il envoie une Neighbor Solicitation vers une adresse multicast sollicitée. Le voisin répond avec une Neighbor Advertisement et la correspondance peut être ajoutée au cache des voisins.</desc>
<style>.bg{fill:#0b1220}.t{fill:#f8fafc;font:700 18px system-ui}.lab{fill:#cbd5e1;font:14px system-ui}.host{fill:#172554;stroke:#60a5fa;stroke-width:1.5}.line{stroke:#94a3b8;stroke-width:2;fill:none}.pkt{fill:#34d399}.small{fill:#94a3b8;font:12px system-ui}</style>
<rect class="bg" width="900" height="320" rx="18"/><text x="28" y="36" class="t">NDP : découvrir un voisin sans ARP</text>
<rect class="host" x="50" y="90" width="245" height="86" rx="12"/><text x="172" y="120" text-anchor="middle" class="t">Hôte A</text><text x="172" y="146" text-anchor="middle" class="lab">2001:db8:10::10</text>
<rect class="host" x="605" y="90" width="245" height="86" rx="12"/><text x="727" y="120" text-anchor="middle" class="t">Hôte B</text><text x="727" y="146" text-anchor="middle" class="lab">2001:db8:10::20</text>
<path class="line" d="M295 110 H605"/><path class="line" d="M605 156 H295"/><text x="450" y="94" text-anchor="middle" class="lab">Neighbor Solicitation (NS)</text><text x="450" y="178" text-anchor="middle" class="lab">Neighbor Advertisement (NA)</text>
<circle class="pkt"><animateMotion dur="3s" repeatCount="indefinite" path="M295 110 H605"/></circle><circle class="pkt"><animateMotion dur="3s" begin="1.5s" repeatCount="indefinite" path="M605 156 H295"/></circle>
<rect x="95" y="220" width="710" height="56" rx="10" fill="#1e293b" stroke="#64748b"/><text x="450" y="243" text-anchor="middle" class="t">Cache des voisins</text><text x="450" y="263" text-anchor="middle" class="lab">Adresse IPv6 ↔ adresse MAC · état appris et actualisé</text>
<text x="450" y="300" text-anchor="middle" class="small">NS/NA sont des messages ICMPv6. NDP couvre aussi la découverte de routeurs et la détection de doublons.</text>
</svg></div>

### 6.4. Le cache des voisins

Le cache des voisins conserve les informations nécessaires pour joindre les voisins sur le lien. Il peut inclure une adresse IPv6, une adresse de couche liaison et un état qui reflète l'accessibilité ou la fraîcheur de l'information. Les états et leur affichage varient selon le système.

Sous Windows, selon la version :

```powershell
Get-NetNeighbor -AddressFamily IPv6
netsh interface ipv6 show neighbors
```

Sous Linux :

```bash
ip -6 neigh show
```

Un voisin absent du cache ne prouve pas à lui seul une panne. Le cache peut être vide avant le premier échange, l'entrée peut avoir expiré, ou la destination peut être distante et ne pas être résolue directement par l'hôte. Dans ce dernier cas, c'est l'adresse de couche liaison du routeur prochain saut qui importe.

### 6.5. Pourquoi ne pas bloquer aveuglément ICMPv6 ?

ICMPv6 ne sert pas seulement aux commandes de ping. Il transporte des messages nécessaires à plusieurs fonctions du protocole, dont NDP et la découverte du chemin MTU. Un pare-feu doit appliquer une politique réfléchie et tenir compte des types ICMPv6 nécessaires, plutôt que bloquer indistinctement tout ICMPv6.

Cela ne veut pas dire que tous les messages ICMPv6 doivent être autorisés depuis partout sans restriction. Les règles doivent tenir compte de la portée, de la topologie, des fonctions requises et des recommandations du constructeur. Dans un réseau d'entreprise, des mécanismes comme RA Guard ou des protections NDP peuvent être utiles si la plateforme les prend en charge et si leur déploiement est correctement conçu.

## 7. Routage IPv6 : joindre un réseau local ou distant

### 7.1. Adresse locale ou destination distante

Pour décider comment envoyer un paquet, l'hôte consulte sa table de routage. Si la destination appartient à un préfixe directement connecté, l'hôte cherche le voisin sur le lien. Si elle ne correspond pas à une route locale plus spécifique, il utilise la route applicable, souvent la route par défaut `::/0`.

Une route `::/0` signifie que toute destination IPv6 qui ne correspond à aucune route plus spécifique peut être envoyée vers le prochain saut défini. Elle ne signifie pas que la connectivité Internet est garantie : le routeur doit lui-même avoir une route utile, et les filtres et routes de retour doivent permettre la communication.

<div class="schema-svg">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" role="img" aria-labelledby="s4title s4desc">
<title id="s4title">IPv6 : routage local et distant</title><desc id="s4desc">Deux hôtes dans le même préfixe communiquent directement sur le lien. Pour joindre un préfixe distant, l'hôte transmet le paquet au routeur par sa route par défaut, puis les routeurs acheminent le paquet vers le réseau cible.</desc>
<style>.bg{fill:#0b1220}.t{fill:#f8fafc;font:700 18px system-ui}.lab{fill:#cbd5e1;font:14px system-ui}.host{fill:#172554;stroke:#60a5fa;stroke-width:1.5}.router{fill:#14532d;stroke:#4ade80;stroke-width:1.5}.line{stroke:#94a3b8;stroke-width:2;fill:none}.pkt{fill:#fbbf24}.small{fill:#94a3b8;font:12px system-ui}</style>
<rect class="bg" width="900" height="300" rx="18"/><text x="28" y="35" class="t">Le préfixe détermine si le prochain saut est local ou un routeur</text>
<rect class="host" x="35" y="94" width="175" height="76" rx="10"/><text x="122" y="123" text-anchor="middle" class="t">Hôte A</text><text x="122" y="147" text-anchor="middle" class="lab">2001:db8:1::10</text>
<rect class="host" x="268" y="94" width="175" height="76" rx="10"/><text x="355" y="123" text-anchor="middle" class="t">Hôte B</text><text x="355" y="147" text-anchor="middle" class="lab">2001:db8:1::20</text>
<path class="line" d="M210 132 H268"/><circle class="pkt"><animateMotion dur="2.2s" repeatCount="indefinite" path="M210 132 H268"/></circle><text x="238" y="190" text-anchor="middle" class="small">Même préfixe</text>
<rect class="router" x="505" y="94" width="150" height="76" rx="10"/><text x="580" y="123" text-anchor="middle" class="t">Routeur</text><text x="580" y="147" text-anchor="middle" class="lab">Route par défaut</text>
<rect class="host" x="715" y="94" width="150" height="76" rx="10"/><text x="790" y="123" text-anchor="middle" class="t">Hôte C</text><text x="790" y="147" text-anchor="middle" class="lab">2001:db8:2::30</text>
<path class="line" d="M443 132 H505"/><path class="line" d="M655 132 H715"/><circle class="pkt"><animateMotion dur="3.4s" begin="0.5s" repeatCount="indefinite" path="M443 132 H505 L655 132 H715"/></circle>
<text x="580" y="205" text-anchor="middle" class="small">Préfixe distant</text><text x="450" y="253" text-anchor="middle" class="lab">Un hôte n'envoie pas directement une trame au réseau distant : il remet le paquet au prochain saut.</text><text x="450" y="276" text-anchor="middle" class="small">Adresses et préfixes réservés à la documentation ; exemple pédagogique.</text>
</svg></div>

### 7.2. Route par défaut et route link-local

Les routeurs IPv6 annoncent souvent une adresse link-local comme prochain saut pour la route par défaut. C'est normal : les routeurs et les hôtes utilisent des adresses link-local dans les échanges sur le lien. Lorsqu'une adresse link-local est utilisée par une commande, il peut être nécessaire d'indiquer l'interface de sortie pour lever toute ambiguïté.

Ne copie pas une adresse de passerelle trouvée sur un autre réseau. La passerelle doit être celle du lien local et correspondre à la configuration réelle. Un poste peut posséder une adresse globale valide tout en n'ayant aucune route par défaut ; il pourra alors communiquer localement mais échouer pour les destinations distantes.

### 7.3. Routage statique IPv6 sur Cisco IOS : exemple de laboratoire

La configuration suivante illustre l'activation du routage IPv6 et l'attribution d'adresses à deux interfaces. Adapte les noms d'interfaces et les préfixes à ta maquette. Les préfixes de documentation sont utilisés ici pour éviter de suggérer une allocation réelle.

```text
Router(config)# ipv6 unicast-routing
Router(config)# interface GigabitEthernet0/0
Router(config-if)# description LAN-A
Router(config-if)# ipv6 address 2001:db8:10:1::1/64
Router(config-if)# no shutdown
Router(config)# interface GigabitEthernet0/1
Router(config-if)# description LAN-B
Router(config-if)# ipv6 address 2001:db8:10:2::1/64
Router(config-if)# no shutdown
```

Si le routeur doit joindre un préfixe distant via un autre routeur, une route statique peut être configurée selon la topologie et la syntaxe supportée. Exemple illustratif :

```text
Router(config)# ipv6 route 2001:db8:20::/64 2001:db8:10:1::2
```

Cette ligne suppose que le prochain saut `2001:db8:10:1::2` est réellement joignable via une interface connectée. Une route statique ne crée pas la connectivité de couche 2 et ne garantit pas la route de retour. Vérifie la table de routage après la configuration.

Commandes de vérification utiles sur les plateformes compatibles :

```text
Router# show ipv6 interface brief
Router# show ipv6 interface
Router# show ipv6 route
Router# show ipv6 neighbors
Router# ping ipv6 2001:db8:10:2::10
```

La syntaxe exacte de `ping` varie selon les versions IOS et le contexte de commande. Si la forme proposée n'est pas acceptée, utilise l'aide contextuelle `?` de l'équipement.

## 8. Configurer et vérifier IPv6 sur un poste

### 8.1. Windows

Pour observer la configuration existante, commence par les commandes de lecture :

```powershell
ipconfig /all
netsh interface ipv6 show interfaces
netsh interface ipv6 show addresses
netsh interface ipv6 show route
Get-NetIPConfiguration
```

Ne modifie pas une interface de production avant d'avoir noté son état initial. Un poste peut obtenir sa configuration IPv6 par SLAAC, DHCPv6, une configuration statique ou une combinaison de ces méthodes. La présence d'une adresse link-local seule indique que le lien possède une configuration IPv6 locale, mais ne prouve pas qu'une route vers des destinations distantes est disponible.

Pour tester la pile locale :

```powershell
ping ::1
```

Pour tester une adresse de documentation dans un laboratoire, choisis une cible qui existe réellement et qui est configurée dans ta maquette. Un ping vers une adresse d'exemple qui n'existe pas ne peut pas valider ton réseau.

### 8.2. Linux

Commandes de lecture courantes :

```bash
ip -6 address show
ip -6 route show
ip -6 neigh show
ping -6 ::1
```

Sur certaines distributions, la commande `ping` accepte `-6` ; sur d'autres outils, la commande peut être nommée `ping6`. Consulte `man ping` ou l'aide locale. Pour une adresse link-local, l'interface peut devoir être précisée, par exemple avec un suffixe de zone tel que `%eth0`, selon la commande et le système.

### 8.3. Vérifier en couches

Une bonne vérification suit un ordre logique :

1. L'interface est-elle active ?
2. L'adresse attendue est-elle présente ?
3. Le préfixe est-il correct ?
4. Une route vers la destination existe-t-elle ?
5. Le voisin prochain saut est-il résolu si nécessaire ?
6. Le routeur connaît-il une route de retour ?
7. Le pare-feu autorise-t-il le flux utile ?
8. Si l'accès se fait par nom, la résolution DNS renvoie-t-elle la bonne adresse IPv6 ?

Un résultat négatif à une étape doit guider le test suivant. Évite de conclure « IPv6 ne marche pas » parce qu'un seul ping ne répond pas : la cible peut bloquer l'écho ICMPv6, une route peut manquer, ou le service peut écouter uniquement sur IPv4.

## 9. Laboratoire 1 — Lire et classer les adresses

### Objectif

Apprendre à simplifier les adresses, repérer les types les plus courants et interpréter les préfixes.

### Matériel

Aucun équipement spécial : utilise ce fichier, une calculatrice de conversion si nécessaire et un terminal pour vérifier des adresses sur ton poste. Toutes les adresses `2001:db8::/32` sont des exemples de documentation.

### Travail demandé

Classe les adresses suivantes et indique leur rôle principal :

1. `::1`
2. `fe80::a12:34ff:fe56:7890`
3. `2001:db8:10:1::25`
4. `fd12:3456:789a:1::20`
5. `ff02::1`
6. `::`

Ensuite, développe `2001:db8:10:1::25` en huit groupes de quatre chiffres hexadécimaux. Indique si `2001:db8:10:1::25/64` et `2001:db8:10:2::25/64` appartiennent au même sous-réseau `/64`.

### Corrigé

1. `::1` : loopback IPv6.
2. `fe80::...` : link-local.
3. `2001:db8:...` : adresse de documentation au format global unicast d'exemple, non destinée à être utilisée en production publique.
4. `fd12:...` : adresse dans la plage unique local.
5. `ff02::1` : adresse multicast de portée lien local utilisée pour le groupe de tous les nœuds du lien.
6. `::` : adresse non spécifiée, pas une adresse d'interface ordinaire.

Développement : `2001:0db8:0010:0001:0000:0000:0000:0025`. Les deux adresses `/64` ne sont pas dans le même préfixe : le quatrième groupe diffère (`0001` contre `0002`).

## 10. Laboratoire 2 — Observer IPv6 sur Windows ou Linux

### Objectif

Identifier les adresses, les routes et les voisins d'une machine sans modifier sa configuration.

### Étape A — État initial

Sur Windows, exécute :

```powershell
ipconfig /all
netsh interface ipv6 show addresses
netsh interface ipv6 show route
netsh interface ipv6 show neighbors
```

Sur Linux, exécute :

```bash
ip -6 address show
ip -6 route show
ip -6 neigh show
```

Note le nom de l'interface active, son adresse link-local, ses éventuelles adresses unicast, le préfixe et l'existence d'une route par défaut.

### Étape B — Tester la pile locale

```powershell
ping ::1
```

ou sous Linux :

```bash
ping -6 ::1
```

Si ce test échoue, vérifie la pile et les politiques locales avant d'examiner un routeur distant. Si le test réussit, il démontre seulement que la boucle locale IPv6 fonctionne.

### Étape C — Générer un échange de voisinage

Dans un réseau de laboratoire où tu connais un autre hôte IPv6 du même lien, tente un ping vers son adresse. Relis ensuite le cache des voisins. Une entrée peut apparaître si la pile a tenté de résoudre le voisin. Si la cible est dans un autre préfixe, le voisin direct recherché sera généralement le routeur prochain saut, pas l'hôte distant lui-même.

### Étape D — Questions de compte rendu

- Quelles adresses IPv6 sont présentes sur ton interface ?
- L'interface possède-t-elle une adresse globale ou ULA, ou seulement une link-local ?
- Existe-t-il une route par défaut IPv6 ?
- Le cache des voisins contient-il une entrée pour la passerelle ?
- Quelle observation prouve la connectivité locale, et laquelle prouverait la connectivité vers un réseau distant ?

**Critère de réussite :** tu peux expliquer les sorties avec tes propres mots, sans supposer qu'une adresse link-local signifie à elle seule qu'Internet IPv6 fonctionne.

## 11. Laboratoire 3 — Construire un petit réseau IPv6 dans Packet Tracer

### Topologie

```text
PC-A ---- SW1 ---- R1 ---- SW2 ---- PC-B
 LAN-A             |              LAN-B
2001:db8:10:1::/64                2001:db8:10:2::/64
```

Le schéma est logique : adapte les connexions et les noms d'interfaces à ton fichier Packet Tracer. Si ta version ne prend pas en charge une fonction IPv6 donnée, note la limite du simulateur plutôt que d'inventer un résultat.

### Plan d'adressage de laboratoire

| Équipement | Interface | Adresse d'exemple | Préfixe |
|---|---|---|---|
| R1 | Vers LAN-A | `2001:db8:10:1::1` | `/64` |
| PC-A | Carte réseau | `2001:db8:10:1::10` | `/64` |
| R1 | Vers LAN-B | `2001:db8:10:2::1` | `/64` |
| PC-B | Carte réseau | `2001:db8:10:2::10` | `/64` |

Les adresses sont des valeurs de documentation réservées aux exemples. Pour ce laboratoire, configure-les uniquement dans le simulateur. Les PC doivent avoir la passerelle IPv6 correspondant à leur LAN si tu choisis une configuration statique.

### Étapes

1. Place deux PC, deux commutateurs et un routeur possédant deux interfaces Ethernet.
2. Connecte chaque PC à son commutateur et chaque commutateur à une interface du routeur.
3. Configure les adresses IPv6 du routeur et active les interfaces.
4. Active le routage IPv6 si la plateforme le demande.
5. Configure les adresses et passerelles des PC, ou teste SLAAC si ton simulateur et la configuration du routeur le permettent.
6. Vérifie les interfaces et la table de routage du routeur.
7. Depuis PC-A, teste d'abord la passerelle locale, puis PC-B.
8. Si le test distant échoue, vérifie la route de retour, les préfixes, les passerelles et l'état des interfaces.

### Exemple de configuration routeur

```text
R1(config)# ipv6 unicast-routing
R1(config)# interface GigabitEthernet0/0
R1(config-if)# description LAN-A
R1(config-if)# ipv6 address 2001:db8:10:1::1/64
R1(config-if)# no shutdown
R1(config)# interface GigabitEthernet0/1
R1(config-if)# description LAN-B
R1(config-if)# ipv6 address 2001:db8:10:2::1/64
R1(config-if)# no shutdown
```

Si le nom des interfaces est différent dans ta maquette, remplace `GigabitEthernet0/0` et `GigabitEthernet0/1` par les interfaces réellement présentes. Ne colle pas les commandes aveuglément dans un routeur de production.

### Vérification et compte rendu

```text
R1# show ipv6 interface brief
R1# show ipv6 route
R1# show ipv6 neighbors
```

Réponds aux questions suivantes :

- Les deux préfixes sont-ils directement connectés à R1 ?
- Pourquoi PC-A ne résout-il pas directement l'adresse MAC de PC-B si les deux PC sont dans des LAN différents ?
- Quelle table permet de vérifier que le routeur connaît les deux réseaux ?
- Que faut-il vérifier si PC-A atteint sa passerelle mais pas PC-B ?

**Critère de réussite :** PC-A et PC-B peuvent échanger des paquets IPv6 dans le simulateur, et tu peux expliquer les routes et les adresses de prochain saut utilisées.

## 12. Laboratoire 4 — Lire SLAAC et NDP dans Wireshark

### Objectif

Relier les notions théoriques aux messages réellement visibles dans une capture.

### Préparation

Utilise un réseau que tu es autorisé à observer. Lance Wireshark sur l'interface active, puis applique un filtre d'affichage adapté, par exemple :

```text
icmpv6
```

Selon la version de Wireshark, tu peux également rechercher des noms de protocoles ou types ICMPv6 tels que Router Solicitation, Router Advertisement, Neighbor Solicitation et Neighbor Advertisement. Les noms de champs et filtres exacts peuvent varier selon la version.

### Procédure

1. Démarre une capture avant de reconnecter une interface de test ou avant de générer un nouvel échange, si cela est possible sans interrompre un service important.
2. Observe si des Router Advertisements sont visibles sur le lien.
3. Génére un échange vers un voisin local de laboratoire.
4. Repère les NS et NA associés à la découverte du voisin.
5. Compare les adresses IPv6 source/destination et les adresses multicast utilisées.
6. Note ce qui est observé, ce qui est déduit et ce qui reste inconnu.

### Questions

- Un RA est-il une réponse nécessairement envoyée à chaque paquet de données ?
- Quelle est la différence entre RS et RA ?
- Pourquoi un NS peut-il apparaître alors que tu n'as pas lancé explicitement de ping ?
- Que pourrait-il se passer si ICMPv6 nécessaire à NDP est bloqué ?
- La capture prouve-t-elle à elle seule que la route Internet fonctionne ? Pourquoi ?

**Critère de réussite :** tu peux reconnaître les messages de contrôle principaux et expliquer pourquoi ils sont distincts des paquets de données applicatifs.

## 13. Méthode de dépannage IPv6 pour débutant

Quand un poste ne communique pas, travaille par étapes et garde une trace des résultats. L'objectif n'est pas d'appliquer toutes les commandes possibles, mais de trouver le premier élément qui ne correspond pas à la configuration attendue.

<div class="schema-svg">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330" role="img" aria-labelledby="s5title s5desc">
<title id="s5title">Dépannage IPv6 : ordre des vérifications</title><desc id="s5desc">Un arbre de diagnostic vérifie d'abord l'adresse et le préfixe, puis le voisinage local, la route par défaut, les routes distantes, DNS et enfin les politiques de filtrage.</desc>
<style>.bg{fill:#0b1220}.t{fill:#f8fafc;font:700 18px system-ui}.lab{fill:#cbd5e1;font:13px system-ui}.node{fill:#1e293b;stroke:#64748b;stroke-width:1.4}.good{fill:#14532d;stroke:#4ade80;stroke-width:1.4}.line{stroke:#94a3b8;stroke-width:2;fill:none}.small{fill:#94a3b8;font:12px system-ui}</style>
<rect class="bg" width="900" height="330" rx="18"/><text x="28" y="34" class="t">Dépanner dans l'ordre, sans changer plusieurs paramètres à la fois</text>
<rect class="node" x="28" y="70" width="150" height="64" rx="9"/><text x="103" y="94" text-anchor="middle" class="t">1. Adresse</text><text x="103" y="115" text-anchor="middle" class="lab">Préfixe valide ?</text>
<rect class="node" x="205" y="70" width="150" height="64" rx="9"/><text x="280" y="94" text-anchor="middle" class="t">2. Voisin</text><text x="280" y="115" text-anchor="middle" class="lab">NDP / link-local</text>
<rect class="node" x="382" y="70" width="150" height="64" rx="9"/><text x="457" y="94" text-anchor="middle" class="t">3. Route</text><text x="457" y="115" text-anchor="middle" class="lab">Passerelle par défaut</text>
<rect class="node" x="559" y="70" width="150" height="64" rx="9"/><text x="634" y="94" text-anchor="middle" class="t">4. Distant</text><text x="634" y="115" text-anchor="middle" class="lab">Route retour ?</text>
<rect class="good" x="736" y="70" width="136" height="64" rx="9"/><text x="804" y="94" text-anchor="middle" class="t">5. Service</text><text x="804" y="115" text-anchor="middle" class="lab">DNS / filtre</text>
<path class="line" d="M178 102 H205 M355 102 H382 M532 102 H559 M709 102 H736"/><path d="M199 97 l6 5 -6 5 M376 97 l6 5 -6 5 M553 97 l6 5 -6 5 M730 97 l6 5 -6 5" fill="#94a3b8"/>
<g transform="translate(55 176)"><rect class="node" width="790" height="94" rx="12"/><text x="395" y="29" text-anchor="middle" class="t">À chaque étape, collecte une preuve</text><text x="395" y="53" text-anchor="middle" class="lab">Configuration · table de routage · cache des voisins · capture ICMPv6 · journal de pare-feu</text><text x="395" y="75" text-anchor="middle" class="lab">Compare une cible locale et une cible distante ; distingue adresse IP, route et résolution DNS.</text></g>
<text x="450" y="306" text-anchor="middle" class="small">Un ping échoué n'identifie pas seul la cause : l'écho ICMPv6 peut être filtré alors que d'autres services fonctionnent.</text>
</svg></div>

### Étape 1 — Vérifier l'interface et l'adresse

Assure-toi que l'interface est active. Identifie les adresses présentes, leur préfixe et leur état. Une adresse link-local seule peut être normale sur un lien sans configuration globale, mais elle ne fournit pas automatiquement un chemin vers des réseaux distants.

### Étape 2 — Vérifier le préfixe

Compare les adresses et les longueurs de préfixe. Deux adresses qui commencent visuellement de la même façon ne sont pas forcément dans le même sous-réseau. Une longueur de préfixe incorrecte peut conduire le poste à chercher directement un voisin qui devrait être atteint via un routeur, ou l'inverse.

### Étape 3 — Vérifier les routes

Affiche la table de routage IPv6. Cherche la route du préfixe de destination et la route par défaut. Si la destination est distante et qu'aucune route correspondante n'existe, la pile ne saura pas où envoyer le paquet. Une route par défaut présente ne garantit pas que le prochain saut est disponible.

### Étape 4 — Vérifier le voisinage

Si la destination est locale, regarde si une entrée de voisinage se forme. Si la destination est distante, inspecte le voisin prochain saut, généralement le routeur. Une résolution de voisin qui échoue peut être due à un lien, un VLAN, une adresse incorrecte, une protection de couche 2 ou un problème de filtrage.

### Étape 5 — Vérifier le chemin de bout en bout

Un paquet peut atteindre le routeur local sans parvenir au réseau distant. Vérifie les routes intermédiaires, les filtres, la route de retour et la disponibilité du service. Pour les connexions par nom, teste également la résolution DNS, car une application peut recevoir une adresse IPv6 différente de celle que tu as testée manuellement.

### Étape 6 — Éviter les conclusions hâtives

Un ping échoué ne prouve pas nécessairement que la connectivité IPv6 est absente : le destinataire ou un pare-feu peut filtrer les requêtes d'écho. Inversement, un ping réussi ne prouve pas que DNS, TCP, HTTPS ou toutes les applications fonctionnent. Choisis un test adapté au service que tu veux vérifier.

### Tableau des symptômes

| Symptôme | Hypothèses à tester | Première observation utile |
|---|---|---|
| Aucune adresse attendue | RA absent, interface, configuration statique ou client | État interface et adresses |
| Adresse présente, pas de route par défaut | RA ou paramètres de route, configuration du client | Table IPv6 et capture ICMPv6 |
| Hôtes du même LAN injoignables | Préfixe, VLAN, NDP, adresse dupliquée, filtrage | Cache des voisins et capture NS/NA |
| Passerelle joignable, réseau distant non | Route distante, route de retour, ACL/pare-feu | Tables de routage des équipements |
| Adresse IP joignable, nom non résolu | DNS ou enregistrement AAAA | Test de résolution DNS |
| Petits échanges fonctionnent, gros flux échoue | MTU/PMTUD, filtrage ICMPv6 ou tunnel | Capture ICMPv6 et mesures de taille |

## 14. Sécurité IPv6 : premiers réflexes

### 14.1. La double pile doit être sécurisée des deux côtés

Si IPv4 et IPv6 sont actifs, la politique de sécurité doit inclure les deux. Ne suppose pas que désactiver ou filtrer IPv4 suffit à protéger un service. Vérifie quelles adresses d'écoute sont réellement actives, les règles de pare-feu et les routes disponibles.

### 14.2. Contrôler les Router Advertisements

Un Router Advertisement non autorisé peut pousser des paramètres de réseau indésirables aux hôtes du lien. Dans un réseau commuté compatible, RA Guard peut aider à empêcher l'émission d'annonces de routeur depuis des ports où elles ne sont pas légitimes. Il faut toutefois comprendre la topologie, les équipements autorisés et les limites de l'implémentation avant d'activer cette protection.

### 14.3. Protéger NDP et DHCPv6 selon la plateforme

Des fonctions de protection de couche 2 peuvent limiter certaines annonces ou certains comportements de configuration non autorisés. Leur disponibilité et leur syntaxe dépendent du modèle de commutateur et de sa version logicielle. N'active pas une protection au hasard : une configuration incorrecte peut aussi bloquer les échanges légitimes.

### 14.4. Ne pas supprimer ICMPv6 sans analyse

ICMPv6 porte des messages nécessaires au fonctionnement normal d'IPv6. Le filtrage doit être ciblé et documenté. Une politique trop restrictive peut provoquer des pannes difficiles à diagnostiquer, notamment pour NDP et la découverte du MTU du chemin.

### 14.5. Documenter le plan d'adressage

Pour chaque VLAN ou lien, documente le préfixe, la passerelle, la méthode de configuration, les services DNS, les routes et les règles de sécurité. Indique quels équipements sont autorisés à envoyer des RA et comment les changements sont validés. La documentation permet de différencier une adresse légitime d'une configuration inattendue.

## 15. Erreurs fréquentes à éviter

1. **Utiliser deux `::` dans la même adresse.** La compression d'une séquence de zéros ne peut apparaître qu'une seule fois.
2. **Confondre adresse et préfixe.** `2001:db8:10::10` ne suffit pas à déterminer le sous-réseau sans connaître la longueur du préfixe.
3. **Croire que toutes les adresses sont publiques.** Link-local, loopback, unique local, multicast et non spécifiée ont des rôles distincts.
4. **Supposer que l'identifiant d'interface vient toujours de la MAC.** Les systèmes modernes utilisent plusieurs méthodes.
5. **Confondre SLAAC et DHCPv6.** Ils peuvent coexister et remplir des rôles différents.
6. **Chercher ARP dans une capture IPv6.** Cherche plutôt les messages NDP, notamment NS et NA.
7. **Bloquer tout ICMPv6.** Certains messages sont nécessaires au fonctionnement du protocole.
8. **Croire qu'une adresse globale garantit Internet.** Les routes, les filtres et la route de retour restent nécessaires.
9. **Tester uniquement par ping.** Complète avec l'inspection des routes, des voisins, du DNS et du service visé.
10. **Copier des commandes sans adapter les interfaces.** Les noms, fonctions et syntaxes dépendent du matériel et du système.
11. **Utiliser les préfixes de documentation en production publique.** Ils sont conçus pour les exemples et les laboratoires.
12. **Modifier plusieurs paramètres en même temps.** Cela empêche d'identifier la cause et complique le retour arrière.

## 16. Quiz de validation

Réponds d'abord sans regarder le corrigé. Pour les questions à choix multiples, une ou plusieurs réponses peuvent être correctes si cela est indiqué.

### Questions

**1. Quelle est la taille d'une adresse IPv6 ?**

A. 32 bits  
B. 64 bits  
C. 128 bits  
D. 256 bits

**2. Quelle règle est correcte pour `::` ?**

A. Elle peut apparaître plusieurs fois dans une adresse.  
B. Elle remplace une séquence contiguë de groupes nuls et apparaît au plus une fois.  
C. Elle signifie toujours « adresse loopback ».  
D. Elle supprime tous les zéros dans l'adresse.

**3. Quelle adresse est la loopback IPv6 ?**

A. `fe80::1`  
B. `::1`  
C. `ff02::1`  
D. `::`

**4. À quoi sert principalement une adresse link-local ?**

A. À être routée sur Internet.  
B. À des communications et mécanismes de contrôle sur le lien local.  
C. À remplacer le DNS.  
D. À identifier le serveur DHCPv6 dans tous les réseaux.

**5. Quel mécanisme permet à un hôte de recevoir des informations de préfixe d'un routeur IPv6 ?**

A. Router Advertisement.  
B. ARP Reply.  
C. STP BPDU.  
D. DHCPv4 Discover.

**6. Quel protocole IPv6 joue un rôle de résolution des voisins sur le lien ?**

A. ARP.  
B. NDP, avec des messages ICMPv6.  
C. FTP.  
D. STP.

**7. Les adresses `2001:db8::/32` sont-elles adaptées à une allocation publique de production ?**

A. Oui, toujours.  
B. Non, elles sont réservées à la documentation.  
C. Oui, si le préfixe est `/64`.  
D. Seulement sur Windows.

**8. Deux adresses sont-elles dans le même sous-réseau `/64` si leurs quatre premiers groupes hexadécimaux sont identiques ?**

A. Oui, si le préfixe comparé est bien `/64`.  
B. Non, il faut comparer les huit groupes.  
C. Jamais.  
D. Seulement si elles ont la même adresse MAC.

**9. Que signifie une route `::/0` ?**

A. Une route vers la loopback.  
B. La route par défaut IPv6.  
C. Une adresse multicast.  
D. Une route qui bloque IPv6.

**10. Pourquoi ne faut-il pas bloquer indistinctement tout ICMPv6 ?**

A. Parce que tous les messages sont toujours sûrs.  
B. Parce que NDP et d'autres fonctions IPv6 reposent sur des messages ICMPv6.  
C. Parce que cela remplace les routes.  
D. Parce qu'IPv6 n'utilise aucun autre protocole.

**11. Un PC peut-il avoir plusieurs adresses IPv6 sur la même interface ? Explique.**

**12. Pourquoi un hôte qui joint sa passerelle mais pas un serveur distant doit-il vérifier la route de retour et les filtres ?**

**13. Quelle est la différence entre RS et RA ?**

**14. Pourquoi un cache des voisins vide ne prouve-t-il pas forcément une panne ?**

**15. Donne une séquence de quatre vérifications à réaliser quand une application ne fonctionne pas en IPv6.**

### Corrigé expliqué

**1. C — 128 bits.** L'adresse est généralement écrite en huit groupes de 16 bits.

**2. B.** `::` compresse une séquence de groupes nuls. Deux occurrences rendraient ambigu le nombre de groupes remplacés.

**3. B — `::1`.** C'est l'adresse de boucle locale IPv6.

**4. B.** Les link-local sont valides sur le lien et servent notamment aux échanges NDP. Elles ne sont pas transférées par les routeurs comme des destinations ordinaires vers d'autres liens.

**5. A — Router Advertisement.** Le RA annonce des informations de routeur et peut fournir un préfixe utilisable pour SLAAC.

**6. B — NDP/ICMPv6.** NS et NA participent à la découverte et à la résolution des voisins. IPv6 ne s'appuie pas sur ARP.

**7. B.** `2001:db8::/32` est réservé à la documentation. Il sert dans les exemples, pas comme allocation publique de production.

**8. A.** Les quatre premiers groupes correspondent à 64 bits. Si le préfixe est `/64`, deux adresses ayant ces mêmes 64 bits appartiennent au même préfixe, sous réserve que la notation ait été correctement interprétée.

**9. B.** `::/0` est le préfixe de la route par défaut IPv6.

**10. B.** ICMPv6 est utilisé par NDP et par d'autres mécanismes essentiels. Les règles de filtrage doivent être conçues, pas appliquées aveuglément.

**11. Oui.** Une interface peut posséder une link-local, une adresse globale ou ULA, et parfois des adresses temporaires ou plusieurs adresses de préfixes différents. Il faut examiner leur état et leur rôle.

**12.** La passerelle locale peut fonctionner alors qu'un routeur intermédiaire ne connaît pas le réseau distant, que la route de retour manque ou qu'un pare-feu bloque le flux. La connectivité doit être vérifiée dans les deux sens.

**13.** RS est une sollicitation envoyée par un hôte pour demander des annonces ; RA est une annonce envoyée par un routeur avec les informations de configuration appropriées.

**14.** Le cache peut être vide avant le premier échange, une entrée peut avoir expiré, ou la destination peut être distante : l'hôte cherche alors le prochain saut local, pas l'adresse MAC de la machine distante.

**15.** Une bonne réponse peut vérifier : adresse et préfixe, table de routage, cache des voisins, puis route distante/pare-feu/DNS selon le symptôme. L'ordre peut varier, mais chaque étape doit produire une observation vérifiable.

## 17. Fiche de révision rapide

- IPv6 utilise des adresses de **128 bits**, écrites en hexadécimal avec des deux-points.
- Les zéros de tête d'un groupe peuvent être omis.
- `::` compresse une séquence contiguë de groupes nuls et ne doit apparaître qu'une fois par adresse.
- Le `/64` est le préfixe courant d'un LAN Ethernet utilisant SLAAC.
- `::1` est la loopback ; `::` est l'adresse non spécifiée.
- `fe80::/10` est la plage link-local ; `fc00::/7` est la plage ULA.
- `ff00::/8` est la plage multicast ; IPv6 ne définit pas de broadcast.
- SLAAC utilise les informations reçues dans les RA pour construire une adresse si les conditions sont réunies.
- NDP, fondé sur ICMPv6, gère la découverte des routeurs et voisins, la résolution de voisin et des fonctions connexes.
- Une route `::/0` est une route par défaut.
- Une adresse configurée ne prouve pas que la route, le DNS ou le service distant fonctionne.
- Ne bloque pas ICMPv6 sans comprendre les messages requis par le réseau.
- Vérifie dans l'ordre l'interface, l'adresse, le préfixe, les routes, les voisins et le chemin distant.

## 18. Préparation au niveau Intermédiaire

Ce cours fournit les bases de lecture d'adresse, de préfixe et de voisinage. Le niveau **Intermédiaire** devra les réutiliser dans des scénarios plus complexes, notamment :

- concevoir un plan d'adressage IPv6 hiérarchique et déléguer des préfixes ;
- comparer SLAAC, DHCPv6 avec état et sans état, y compris l'interaction avec les indicateurs RA ;
- configurer et dépanner le routage IPv6 statique et les protocoles de routage selon la plateforme étudiée ;
- approfondir NDP, les états du cache des voisins et les captures ICMPv6 ;
- analyser DNS AAAA, double pile et choix d'adresse par les clients ;
- diagnostiquer PMTUD IPv6, filtrage ICMPv6, tunnels et symptômes de connectivité partielle ;
- aborder les contrôles de sécurité RA/NDP et la validation d'un changement.

Le niveau Expert pourra ensuite traiter l'architecture à grande échelle, l'agrégation et la délégation, la résilience du routage, l'observabilité, les stratégies de migration, les contrôles de sécurité avancés et le diagnostic multi-cause. Ces sujets ne sont pas développés ici afin de garder une progression pédagogique cohérente.

## 19. Références et lectures complémentaires

Les références ci-dessous sont des sources normatives ou documentaires pour approfondir les notions. Les RFC décrivent les protocoles ; elles ne remplacent pas la documentation de ta version Windows, Linux, Cisco IOS/IOS XE ou de ton simulateur.

- **RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification** : format de paquet et spécification du protocole IPv6. https://www.rfc-editor.org/rfc/rfc8200
- **RFC 4291 — IP Version 6 Addressing Architecture** : architecture d'adressage IPv6. https://www.rfc-editor.org/rfc/rfc4291
- **RFC 5952 — A Recommendation for IPv6 Address Text Representation** : recommandations de représentation textuelle. https://www.rfc-editor.org/rfc/rfc5952
- **RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)** : Neighbor Discovery. https://www.rfc-editor.org/rfc/rfc4861
- **RFC 4862 — IPv6 Stateless Address Autoconfiguration** : autoconfiguration sans état. https://www.rfc-editor.org/rfc/rfc4862
- **RFC 8415 — Dynamic Host Configuration Protocol for IPv6 (DHCPv6)** : fonctionnement DHCPv6. https://www.rfc-editor.org/rfc/rfc8415
- **RFC 4443 — Internet Control Message Protocol (ICMPv6)** : messages ICMPv6. https://www.rfc-editor.org/rfc/rfc4443
- **Cisco IOS IPv6 Configuration Guide** : vérifier la documentation correspondant à la version de ton système. https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-software/tsd-products-support-series-home.html

## 20. Évaluation finale — scénario de synthèse

Un poste possède l'adresse `2001:db8:10:1::25/64` et veut joindre `2001:db8:10:2::40`. Il peut joindre `2001:db8:10:1::1`, mais pas l'hôte distant. Le nom DNS du service ne résout pas toujours vers la même adresse sur deux postes différents.

Rédige une procédure de diagnostic dans laquelle tu :

1. confirmes que l'adresse du poste et son préfixe sont corrects ;
2. vérifies la route vers le préfixe `2001:db8:10:2::/64` et le prochain saut ;
3. inspectes le cache des voisins pour le prochain saut pertinent ;
4. vérifies les routes et la route de retour sur les routeurs ;
5. testes l'adresse IPv6 du service indépendamment du nom DNS ;
6. examines la résolution DNS et les enregistrements AAAA ;
7. contrôles les politiques de filtrage sans désactiver aveuglément ICMPv6 ;
8. consignes les résultats avant toute modification.

Une réponse solide sépare les faits observés des hypothèses. Elle n'affirme pas qu'une panne DNS est certaine uniquement parce qu'un nom ne fonctionne pas, ni qu'une panne de routage est certaine uniquement parce qu'un ping ne répond pas.

### Grille d'auto-évaluation

| Compétence | À valider |
|---|---|
| Lire et simplifier une adresse | Je peux développer et compresser une adresse sans changer sa valeur. |
| Comprendre un préfixe | Je peux comparer deux adresses en tenant compte de la longueur du préfixe. |
| Classer les adresses | Je distingue global unicast, link-local, loopback, ULA, multicast et non spécifiée. |
| Comprendre SLAAC | Je peux expliquer RS, RA, construction d'adresse et DAD. |
| Comprendre NDP | Je peux expliquer NS, NA et le cache des voisins. |
| Lire une table de routage | Je distingue route connectée, route spécifique et route par défaut. |
| Dépanner méthodiquement | Je collecte des preuves avant de changer la configuration. |
| Appliquer une politique prudente | Je comprends pourquoi IPv6 et ICMPv6 doivent être pris en compte dans la sécurité. |

**Prêt pour la suite ?** Passe au cours `ipv6-intermediaire.md` lorsque tu sais lire les adresses et préfixes sans hésitation, expliquer le rôle de RS/RA et NS/NA, vérifier les routes IPv6 et effectuer le laboratoire Packet Tracer en expliquant chaque étape.
