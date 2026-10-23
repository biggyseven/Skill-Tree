---
node_id: nat-intermediaire
title: NAT & PAT - Intermédiaire
---

# NAT & PAT - Intermédiaire

**Niveau :** Intermédiaire

Network Address Translation (NAT) et Network Address Port Translation (NAPT), souvent appelé PAT ou NAT overload dans la documentation Cisco, sont des mécanismes qui modifient certaines informations d’adressage des paquets IP lorsqu’ils traversent un équipement de couche 3. Ils sont couramment utilisés à la frontière entre un réseau privé et un réseau externe, mais aussi dans les interconnexions entre réseaux qui utilisent des espaces d’adressage qui se chevauchent. Pour comprendre leur intérêt, il faut d’abord distinguer l’adressage utilisé à l’intérieur d’un domaine administratif de l’adressage qui doit être routable dans un autre domaine.

Le NAT traditionnel a été décrit dans la RFC 3022. Il permet de faire correspondre des adresses d’un espace à celles d’un autre espace. Avec le NAT de base, une adresse interne est traduite en une autre adresse, en général selon une relation un-à-un ou un ensemble de correspondances déterminées. Avec NAPT/PAT, l’équipement traduit également les identifiants de transport — notamment les ports TCP et UDP — afin que plusieurs flux issus de plusieurs hôtes puissent partager une même adresse IPv4 globale. Cette utilisation économise l’espace IPv4 public, mais elle crée un état de traduction que l’équipement doit conserver et exploiter pour le trafic de retour.

Dans les réseaux d’entreprise, NAT n’est pas une fonction isolée. Il dépend du plan d’adressage, du routage, des listes de contrôle d’accès, des politiques de sécurité, des chemins aller et retour, du DNS et parfois des VPN ou des services applicatifs. Une configuration peut sembler correcte à la lecture de ses lignes tout en échouant parce que l’interface n’est pas déclarée `inside` ou `outside`, que la route de retour est absente, que l’ACL ne correspond pas à la bonne source, que le pool public est épuisé ou que le trafic emprunte un chemin asymétrique.

Ce cours approfondit le fonctionnement de NAT/PAT au niveau intermédiaire. Il étudie les types de traduction, la terminologie inside/outside, la création et l’expiration des entrées, les effets sur les en-têtes, la configuration Cisco IOS/IOS XE, les méthodes de vérification ainsi que les principaux scénarios de dépannage. Les exemples utilisent IPv4 et une syntaxe IOS classique ; les variantes disponibles doivent être confirmées sur la plateforme et la version réellement utilisées.

> **Analogie** : Imagine une entreprise installée dans un immeuble où chaque employé possède un numéro de bureau interne, mais où les visiteurs ne peuvent appeler que le numéro public de l’accueil. Pour un courrier sortant, l’accueil remplace l’adresse interne par l’adresse officielle de l’entreprise. Si plusieurs employés téléphonent en même temps depuis une même ligne publique, l’accueil utilise aussi des extensions temporaires pour savoir à qui remettre chaque appel entrant. L’adresse publique représente l’« inside global », l’adresse interne l’« inside local », et les extensions jouent le rôle des ports traduits par PAT.
>
> La comparaison a toutefois une limite importante : le NAT n’est pas un standard de sécurité équivalent à un pare-feu. L’accueil peut garder une table des appels en cours, mais ce registre ne constitue pas à lui seul une politique complète d’autorisation. Un service explicitement publié par une traduction statique peut rester accessible si le routage et les filtres le permettent. De même, certains protocoles transportent des adresses ou des ports dans leur charge utile ; remplacer uniquement l’en-tête IP peut ne pas suffire à maintenir leur fonctionnement. Il faut donc considérer NAT comme une fonction de traduction d’adresses et d’état, puis traiter séparément le filtrage, la sécurité et la compatibilité applicative.

---

## 1. La théorie et les algorithmes

### 1.1. Pourquoi NAT existe

IPv4 utilise des adresses sur 32 bits, ce qui limite le nombre d’adresses possibles. Les plages privées définies par la RFC 1918 — `10.0.0.0/8`, `172.16.0.0/12` et `192.168.0.0/16` — sont destinées à un usage interne et ne sont pas annoncées globalement dans l’Internet public. Deux organisations peuvent donc employer les mêmes plages privées indépendamment, sans coordination entre elles.

Un routeur de bordure ne peut pas simplement transmettre sur l’Internet un paquet dont la source est une adresse privée et s’attendre à ce que les réponses soient acheminées correctement. NAT permet de traduire ces adresses en adresses globalement routables, lorsque le réseau dispose d’une telle adresse ou d’un pool attribué. Le PAT va plus loin : plusieurs hôtes privés peuvent partager une même adresse globale, chaque flux étant associé à une traduction distincte.

Les cas d’usage principaux sont les suivants :

- accès sortant de plusieurs hôtes privés avec une seule adresse IPv4 publique ;
- publication contrôlée d’un serveur interne via une traduction statique d’adresse ou de port ;
- conservation d’un plan d’adressage privé malgré un changement de fournisseur ;
- interconnexion de domaines qui utilisent accidentellement des préfixes identiques, avec une conception plus avancée ;
- traduction d’adresses entre zones ou contextes réseau dans certaines architectures d’entreprise.

NAT ne résout pas tous les problèmes d’adressage. Il ajoute de l’état, rend certains diagnostics plus complexes et peut compliquer les applications qui initient des connexions entrantes ou échangent des adresses dans leurs messages applicatifs. Il ne remplace ni un plan d’adressage rigoureux ni une politique de sécurité réseau.

### 1.2. Terminologie inside/outside

Dans la terminologie classique de NAT, « inside » et « outside » désignent les côtés logique et administratif de la traduction, pas simplement la gauche ou la droite d’un schéma. En IOS traditionnel, l’administrateur marque les interfaces avec `ip nat inside` et `ip nat outside`.

| Terme | Signification | Exemple |
|---|---|---|
| **Inside local** | Adresse de l’hôte interne telle qu’elle est connue dans le réseau inside | `192.168.10.25` |
| **Inside global** | Adresse qui représente cet hôte côté outside après traduction | `203.0.113.10` |
| **Outside global** | Adresse réelle de l’hôte externe dans le réseau global | `198.51.100.80` |
| **Outside local** | Adresse de l’hôte externe telle qu’elle est représentée à l’intérieur du réseau inside ; elle peut être identique à outside global | `198.51.100.80` |

Les blocs `203.0.113.0/24` et `198.51.100.0/24` sont réservés à la documentation et aux exemples par la RFC 5737. Ils ne doivent pas être utilisés comme adresses publiques de production sur l’Internet.

La terminologie se comprend mieux en suivant un paquet sortant. Un ordinateur `192.168.10.25` initie un flux vers un serveur `198.51.100.80`. Le routeur NAT remplace l’adresse source privée par une adresse globale — par exemple `203.0.113.10` — et, dans le cas du PAT, peut aussi remplacer le port source. L’adresse du serveur externe ne change pas nécessairement. Pour le flux de retour, le routeur reconnaît l’entrée d’état et effectue la traduction inverse vers l’hôte privé et, le cas échéant, vers son port d’origine.

Ces noms ne signifient pas que l’adresse inside local est intrinsèquement « fausse » ou que l’adresse inside global est nécessairement attribuée directement à une interface du routeur. Avec certaines configurations, une adresse de pool ou une adresse de traduction peut être distincte de l’adresse de l’interface outside. Il faut examiner le plan d’adressage, le routage amont et la fonction exacte du mécanisme configuré.

### 1.3. NAT statique, NAT dynamique et PAT

Les familles de traduction courantes se distinguent par leur mode de correspondance et par la façon dont elles consomment des adresses globales.

| Type | Correspondance | Ressources globales | Usage courant |
|---|---|---|---|
| NAT statique | Permanente, typiquement une adresse inside vers une adresse globale | Une adresse globale par correspondance un-à-un | Serveur ou équipement qui doit être représenté par une adresse constante |
| NAT dynamique | Créée à la demande depuis un pool d’adresses | Une adresse du pool est nécessaire pour chaque allocation active, selon la configuration | Groupes d’hôtes qui n’ont pas besoin d’une identité globale permanente |
| PAT dynamique / NAT overload | Plusieurs hôtes et flux partagent une ou plusieurs adresses globales grâce aux ports | Très peu d’adresses globales peuvent suffire pour de nombreux flux | Accès sortant des utilisateurs vers Internet |
| PAT statique | Association fixe d’une adresse/port global à une adresse/port interne | Une adresse globale peut publier plusieurs services si les ports sont distincts | Publication ciblée d’un service interne |

Le NAT statique un-à-un conserve une correspondance durable même si aucun flux n’est actif. Selon la plate-forme et la syntaxe, la commande peut également permettre aux connexions initiées de l’extérieur d’atteindre l’adresse interne, à condition que le routage et les politiques de filtrage les autorisent.

Le NAT dynamique alloue les adresses d’un pool selon les besoins. Si toutes les adresses disponibles sont affectées et que les règles applicables n’autorisent pas d’autre traduction, un nouvel hôte peut ne pas obtenir de traduction. La capacité dépend alors du nombre d’adresses, du vieillissement des entrées et du comportement de la plate-forme.

Le PAT distingue les sessions au moyen d’un ensemble d’informations de flux. Pour TCP et UDP, cet ensemble comprend notamment les adresses IP, les ports et le protocole de transport. Le moteur de traduction doit s’assurer qu’une combinaison publiée côté outside ne se confond pas avec une autre entrée en cours. Il peut choisir un port traduit différent du port source original.

Le mot « port » désigne ici un identifiant de transport de couche 4, pas un port physique Ethernet sur un commutateur. PAT ne modifie pas le numéro du port Ethernet : il traduit, lorsque nécessaire, le champ de port TCP ou UDP contenu dans le paquet IP.

### 1.4. NAT de base et NAPT/PAT

Le NAT de base remplace une adresse IP, tandis que NAPT traduit l’adresse et un identifiant de transport. Dans les deux cas, modifier une adresse IP nécessite généralement d’ajuster le checksum de l’en-tête IPv4. Pour TCP et UDP, le checksum de transport couvre un pseudo-en-tête contenant les adresses IP ; la modification des adresses implique donc une correction du checksum TCP/UDP. Lorsqu’un port source ou destination est traduit, le checksum de transport doit aussi être ajusté.

Une exception historique concerne le checksum UDP nul autorisé en IPv4 par les règles applicables à UDP : il ne doit pas être traité comme un checksum non nul à recalculer de la même manière. Les détails sont spécifiés dans les RFC pertinentes. Le routeur gère ces ajustements dans son moteur NAT ; un administrateur n’a pas à recalculer manuellement les checksums dans une configuration IOS ordinaire.

Pour certains messages ICMP de type query — par exemple Echo Request/Reply — l’identifiant ICMP peut jouer un rôle comparable à un numéro de port afin de distinguer les échanges. La traduction doit prendre en compte les champs concernés et les checksums. Il serait donc incorrect de considérer PAT comme limité à une substitution mécanique de ports TCP.

### 1.5. Modèle de flux : exemple PAT sortant

Considérons le réseau suivant :

```text
        Réseau privé / INSIDE                       Réseau public / OUTSIDE

 +-----------------------------+                  +--------------------------+
 | PC-A                        |                  | Serveur Web               |
 | 192.168.10.10:51500         |                  | 198.51.100.80:443         |
 +--------------+--------------+                  +-------------+------------+
                |                                               ^
                | paquet avant NAT                              |
                v                                               |
        +--------------------+                                  |
        | Routeur R1         |----------------------------------+
        | NAT/PAT             |     paquet après NAT
        | inside: G0/0        |     203.0.113.10:40001
        | outside: G0/1       |     -> 198.51.100.80:443
        +--------------------+

        Table PAT (schématique)
        192.168.10.10:51500 <-> 203.0.113.10:40001
```

Le poste initie une connexion TCP vers le port 443 du serveur. Le routeur consulte ses règles de traduction. Si le flux correspond à une règle PAT, il choisit ou retrouve une traduction et inscrit celle-ci dans sa table. Le serveur voit comme source l’adresse globale et le port traduits. La réponse adressée à `203.0.113.10:40001` atteint le routeur, qui recherche l’entrée correspondante et réécrit la destination pour la diriger vers `192.168.10.10:51500`.

L’entrée PAT n’est pas forcément conservée indéfiniment. Les délais d’expiration diffèrent selon le protocole, l’état de la session, l’activité observée et la plate-forme. Une nouvelle tentative après expiration peut entraîner la création d’une autre entrée ou le choix d’un autre port traduit.

### 1.6. Le processus logique de traduction

Le détail interne varie selon le matériel et la version logicielle. Pour comprendre le fonctionnement, on peut toutefois suivre un modèle conceptuel en plusieurs étapes :

1. **Réception et classification** : le routeur reçoit le paquet sur une interface et identifie le sens logique du trafic par rapport aux zones NAT.
2. **Recherche d’une correspondance existante** : il vérifie si le paquet appartient à une traduction déjà connue, selon les informations du flux.
3. **Évaluation des règles** : en l’absence d’une entrée correspondante, le moteur cherche une règle applicable, comme une traduction statique ou une règle dynamique associée à une ACL ou à une route-map.
4. **Allocation d’une ressource** : le moteur choisit une adresse depuis un pool ou une adresse et un port pour PAT, lorsque cette allocation est nécessaire.
5. **Modification du paquet** : les champs IP concernés et éventuellement les ports ou identifiants pertinents sont modifiés ; les checksums nécessaires sont ajustés.
6. **Mise à jour de l’état** : la traduction est créée ou rafraîchie avec les informations de protocole et les temporisateurs applicables.
7. **Routage et transfert** : le paquet doit encore être acheminé correctement vers le prochain saut. NAT et routage sont des fonctions distinctes, même si leur ordre d’exécution exact dépend de la plate-forme.
8. **Traitement du retour** : le paquet de retour doit atteindre le bon équipement NAT et correspondre à une entrée ou une règle de traduction valable.

Ce modèle est pédagogique et ne décrit pas obligatoirement l’ordre exact de chaque étape du pipeline matériel d’un équipement donné. Sur une plate-forme de production, la documentation correspondant à la version IOS/IOS XE et au matériel fait foi.

### 1.7. ACL utilisées pour sélectionner le trafic NAT

Une ACL standard est fréquemment utilisée dans les exemples NAT IOS pour sélectionner les adresses inside locales devant être traduites. Elle ne devient pas pour autant automatiquement une politique de sécurité qui autorise ou refuse le trafic. Dans ce contexte, elle sert de critère de classification pour la règle NAT.

Exemple :

```cisco
access-list 10 permit 192.168.10.0 0.0.0.255
```

La wildcard `0.0.0.255` correspond au masque inverse de `/24`. Cette entrée sélectionne les sources du réseau `192.168.10.0/24` pour la règle NAT qui la référence. Elle ne signifie pas que le routeur permet globalement toutes les communications de ce réseau vers Internet ; le transfert et le filtrage sont traités par d’autres parties de la configuration.

Pour limiter la sélection à des sous-réseaux précis, il faut écrire une ACL qui exprime réellement le plan d’adressage souhaité. Une wildcard trop large peut traduire des sources non prévues, tandis qu’une wildcard trop étroite peut laisser certains hôtes sans traduction.

Il faut vérifier l’ACL de façon indépendante et confirmer qu’elle est attachée à la commande NAT prévue. Une ACL présente dans la configuration mais jamais référencée par une règle ne sélectionne aucun flux pour cette règle.

### 1.8. Sens des interfaces NAT

Dans IOS classique, une configuration de source NAT indique normalement quelles interfaces sont du côté inside et du côté outside :

```cisco
interface GigabitEthernet0/0
 ip nat inside
!
interface GigabitEthernet0/1
 ip nat outside
```

La classification dépend du point de vue du routeur. Il faut marquer comme inside l’interface orientée vers les sources internes concernées et comme outside celle orientée vers le réseau externe dans l’exemple. Les réseaux à plusieurs sorties, les VRF, les VPN et certaines variantes NAT peuvent nécessiter des configurations plus avancées.

Un problème très fréquent consiste à placer les commandes `ip nat inside` et `ip nat outside` sur les mauvaises interfaces, ou à oublier une interface logique comme une sous-interface VLAN. Dans ce cas, l’ACL et le pool peuvent sembler corrects, mais les paquets ne sont pas traités par la règle attendue.

Les routes déterminent par ailleurs où le paquet doit aller. Pour l’accès Internet, une route par défaut ou une route équivalente est normalement requise vers le fournisseur. NAT ne crée pas à lui seul la connectivité amont.

### 1.9. Traduction statique d’adresse

Le NAT statique crée une correspondance persistante entre une adresse inside locale et une adresse inside globale :

```cisco
ip nat inside source static 192.168.10.20 203.0.113.20
```

Cette syntaxe indique que l’hôte interne `192.168.10.20` est représenté par `203.0.113.20` dans la traduction inside-source. Elle suppose que l’adresse globale soit utilisable dans le contexte réseau extérieur et que le trafic puisse atteindre le routeur NAT par le routage amont.

Une traduction statique n’ajoute pas automatiquement un service applicatif, ne configure pas le serveur et ne garantit pas que les paquets entrants soient autorisés par une ACL ou un pare-feu. Elle crée une correspondance d’adresses ; la disponibilité du service dépend toujours du routage, du filtrage et de l’écoute du serveur.

Dans les déploiements réels, les blocs publics fournis par un opérateur et les routes vers ces blocs doivent être configurés correctement. L’adresse présentée dans un exemple de documentation ne doit pas être copiée comme adresse publique réelle.

### 1.10. NAT dynamique avec pool

Le NAT dynamique sélectionne une adresse inside global dans un pool quand un hôte interne éligible déclenche un flux. Un exemple IOS classique est :

```cisco
ip nat pool PUBLICS 203.0.113.10 203.0.113.20 netmask 255.255.255.0
access-list 10 permit 192.168.10.0 0.0.0.255
ip nat inside source list 10 pool PUBLICS
```

Le nom `PUBLICS` est un identifiant local pour le pool. La plage d’adresses est uniquement illustrative et utilise un bloc réservé à la documentation. Dans un réseau réel, la plage doit correspondre aux adresses routables attribuées et utilisables pour la traduction.

La quantité d’adresses du pool limite le nombre d’allocations simultanées si chaque hôte ou traduction en consomme une. Si le pool est épuisé, certains nouveaux flux peuvent échouer à obtenir une traduction. Il faut alors inspecter les statistiques, les translations actives et les temporisateurs avant d’augmenter arbitrairement la plage.

La commande `overload` ajoutée à une règle utilisant un pool permet, lorsque la plate-forme le prend en charge, d’utiliser PAT afin de partager des adresses globales entre plusieurs flux. Il faut distinguer le pool NAT dynamique simple d’un pool utilisé en surcharge.

### 1.11. PAT par adresse d’interface

Pour de nombreux petits réseaux ou sites distants, le PAT utilise l’adresse IPv4 de l’interface outside :

```cisco
access-list 10 permit 192.168.10.0 0.0.0.255
ip nat inside source list 10 interface GigabitEthernet0/1 overload
```

Cette règle sélectionne les sources du réseau privé et leur permet de partager l’adresse de l’interface `GigabitEthernet0/1`, avec distinction des flux par les identifiants nécessaires. La commande `overload` est le mot-clé IOS classique pour la surcharge PAT.

Cette forme est pratique lorsque l’interface outside possède une adresse utilisable et stable dans le contexte de l’accès amont. Si l’adresse est dynamique ou que plusieurs connexions fournisseurs doivent être prises en charge, la configuration peut nécessiter des mécanismes adaptés au type d’accès, au routage et à la plate-forme.

Le PAT ne garantit pas la capacité illimitée d’une adresse unique. Les tables d’état, les ports disponibles, les limites de session, les ressources du routeur et les contraintes de certains protocoles peuvent devenir des goulots d’étranglement. La capacité opérationnelle dépend du modèle et du profil de trafic.

### 1.12. PAT statique et publication d’un service

Une traduction de port statique permet de publier un service interne sans exposer tous les ports de l’hôte. Exemple de syntaxe classique :

```cisco
ip nat inside source static tcp 192.168.10.20 443 203.0.113.20 443
```

Cette règle associe le port TCP 443 de l’hôte interne `192.168.10.20` au port TCP 443 de l’adresse globale `203.0.113.20`. La commande n’ouvre pas par elle-même le trafic dans un pare-feu et ne garantit pas qu’un routeur amont sache acheminer l’adresse globale vers cet équipement.

Il est possible, selon les besoins, de publier un port externe différent du port interne. Par exemple, un port global élevé peut être traduit vers un port interne standard, mais ce choix ne remplace pas un contrôle d’accès et ne rend pas un service intrinsèquement sûr.

La publication d’un service doit s’accompagner de mesures de sécurité : mises à jour du serveur, authentification robuste, filtrage des sources si cela est adapté, journalisation, surveillance et segmentation de la machine. Le fait qu’un serveur soit derrière NAT ne le protège pas automatiquement d’un accès non désiré lorsque sa traduction statique permet de l’atteindre.

### 1.13. Traduction du trafic entrant et trafic initié

Un PAT dynamique est généralement construit lorsqu’un hôte inside initie un flux. Le routeur sait alors à quel hôte et à quel port interne associer les paquets de retour. Cela ne signifie pas qu’un hôte externe quelconque peut initier librement une session vers n’importe quel port de cet hôte.

La translation statique d’adresse ou de port établit une correspondance permanente pour la destination publique configurée. Lorsque le trafic entrant atteint le routeur, cette correspondance peut être appliquée ; le routage et les politiques de sécurité doivent néanmoins autoriser le transfert jusqu’au serveur interne.

Il faut distinguer :

- **NAT** : la traduction d’adresses et, selon le cas, d’identifiants de transport ;
- **filtrage stateful** : une politique qui décide si le trafic est autorisé selon les règles et l’état de session ;
- **routage** : la sélection du prochain saut ;
- **service applicatif** : le processus qui écoute réellement sur l’adresse et le port de destination.

Ces fonctions peuvent être intégrées à un même équipement, mais elles restent conceptuellement distinctes. Une règle NAT statique ne remplace pas une politique de filtrage, et une règle de filtrage ne crée pas nécessairement la traduction requise.

### 1.14. NAT et DNS

Une application se connecte souvent à un nom DNS qui est résolu en adresse IP. Si un service interne est publié, le DNS public peut pointer vers son adresse globale, tandis qu’un DNS interne peut renvoyer une adresse privée pour les clients situés dans le LAN. Cette approche est souvent appelée DNS split-horizon.

Il faut déterminer si les clients internes doivent emprunter la même traduction que les clients externes. Si un client interne résout le nom en adresse publique, la connexion peut dépendre de la prise en charge du NAT loopback/hairpin par l’équipement. Sans cette capacité ou sans un chemin approprié, le serveur peut être joignable depuis Internet mais pas via son adresse publique depuis le LAN.

Une autre approche consiste à fournir une réponse DNS interne qui pointe directement vers l’adresse privée du serveur. Elle peut simplifier le chemin local, mais la conception doit préserver la cohérence du nom et du certificat TLS, et éviter que les clients reçoivent des adresses inappropriées dans le mauvais contexte.

Le DNS ne crée pas une traduction NAT. Il fournit des correspondances nom/adresse. Les enregistrements DNS, les règles NAT, le routage et le filtrage doivent être cohérents.

### 1.15. NAT loopback ou hairpin NAT

Le NAT loopback, parfois appelé hairpin NAT, permet à un client interne d’utiliser une adresse globale publiée pour joindre un serveur lui aussi situé dans le réseau interne. Le routeur doit alors gérer un paquet qui entre d’un côté logique et retourne vers une zone inside tout en appliquant les translations appropriées.

Ce comportement dépend de la plate-forme et de sa configuration. Dans certains environnements, une simple règle de port forwarding ne suffit pas. Il peut être nécessaire de traduire également la source du client afin que le serveur renvoie la réponse vers l’équipement NAT plutôt que directement vers le client, ce qui pourrait contourner la traduction inverse attendue.

Les symptômes typiques sont les suivants : les clients Internet atteignent le service, les clients internes atteignent le serveur par son adresse privée, mais l’accès interne via le nom public échoue. Avant de changer les règles NAT, vérifie la résolution DNS, le routage local et la prise en charge du hairpin par l’équipement.

### 1.16. Interaction avec le routage et le retour asymétrique

NAT stateful maintient une correspondance entre les paquets aller et retour. Si le paquet sortant passe par un routeur NAT R1, mais que le trafic de retour arrive par une autre sortie ou un autre équipement R2 qui ne possède pas l’état correspondant, la traduction inverse peut échouer. C’est un problème de chemin asymétrique.

Les architectures multi-WAN nécessitent donc une conception cohérente du routage. Si des sessions PAT utilisent une adresse publique d’un fournisseur particulier, les réponses doivent normalement revenir par le chemin capable de traiter la traduction associée. Le routage basé sur des politiques, des routes spécifiques ou une architecture de haute disponibilité peut être nécessaire selon le cas.

Les mécanismes de synchronisation d’état NAT ne sont pas disponibles sur tous les routeurs et toutes les plateformes. Il ne faut pas supposer que deux routeurs partagent automatiquement les entrées de traduction parce qu’ils exécutent des configurations similaires.

### 1.17. NAT, MTU et fragmentation

La traduction modifie les en-têtes et parfois la longueur ou les exigences du paquet lorsque des fonctions supplémentaires sont impliquées. Le NAT traditionnel peut interagir avec la découverte de MTU de chemin (PMTUD), le bit DF en IPv4, les fragments et les messages ICMP d’erreur. Les comportements précis dépendent de l’implémentation et des RFC applicables.

Les symptômes d’un problème de MTU peuvent être trompeurs : de petits pings passent, alors que des connexions TLS, des transferts volumineux ou certaines applications échouent. Il ne faut pas supposer que tout problème intermittent vient de NAT ; vérifie aussi la MTU des liens, le traitement ICMP et les politiques de filtrage.

Pour les paquets fragmentés, les ports TCP/UDP ne sont présents que dans le fragment contenant le début de l’en-tête de transport. Les équipements doivent traiter correctement les fragments et les associer à l’état de traduction. Les règles précises sont dépendantes de la plate-forme et de la version, et les fragments peuvent également poser des enjeux de sécurité.

### 1.18. NAT et protocoles qui transportent des adresses

Certains protocoles insèrent des adresses IP, des ports ou des informations de connexion dans la charge utile. Le remplacement de l’en-tête IP ne modifie pas nécessairement ces champs internes. Historiquement, des mécanismes ALGs (*Application Layer Gateways*) ont été développés pour adapter certaines applications à NAT.

Les ALGs peuvent aider dans certains cas, mais ils peuvent aussi interférer avec des mécanismes modernes de sécurité, d’intégrité ou de chiffrement applicatif. Il ne faut ni activer ni désactiver tous les ALGs sans comprendre les besoins du protocole utilisé et les recommandations de la plate-forme.

Les protocoles qui négocient des flux secondaires, les applications de voix/vidéo et certains protocoles d’accès distant méritent une attention particulière. Lorsque des informations de session sont chiffrées ou protégées par une intégrité cryptographique, un traducteur qui tenterait de réécrire le contenu applicatif risque de ne pas pouvoir le faire correctement.

### 1.19. NAT, VPN et réseaux qui se chevauchent

Les VPN site-à-site transportent parfois des préfixes privés identiques des deux côtés. Si le site A et le site B utilisent tous deux `192.168.1.0/24`, le routage classique ne peut pas distinguer clairement le réseau local de celui du site distant sans mécanisme supplémentaire. Des règles NAT d’overlapping peuvent traduire l’un des espaces afin de créer une représentation non chevauchante dans le tunnel.

Ce scénario diffère du PAT Internet classique. Il peut impliquer des règles de NAT exemption, des ACL spécifiques, des route-maps et des interactions avec le traitement IPsec. L’ordre d’application varie avec la plateforme et le type de VPN ; il faut suivre le guide de configuration approprié plutôt que recopier une recette générique.

Avant d’utiliser NAT pour corriger un chevauchement, il vaut mieux évaluer la possibilité de renuméroter un site. Une traduction peut résoudre temporairement le conflit, mais elle ajoute une couche d’adressage qui doit être documentée et exploitée sur le long terme.

### 1.20. NAT et IPv6

IPv6 offre un espace d’adressage beaucoup plus vaste et n’a pas besoin de NAT pour conserver des adresses de la même manière qu’IPv4. Le modèle recommandé privilégie généralement le routage de bout en bout lorsque c’est possible, accompagné d’un filtrage de pare-feu adapté.

Des mécanismes de traduction IPv6 existent pour des scénarios spécifiques, par exemple certaines transitions entre IPv6 et IPv4, mais ils ne doivent pas être confondus avec le PAT IPv4 classique. NAT66 ou d’autres fonctions de traduction ont des objectifs et des conséquences distincts selon leur contexte.

Une migration vers IPv6 ne doit pas consister simplement à répliquer toutes les habitudes de NAT IPv4. Le design IPv6 doit intégrer le plan d’adressage, les annonces de préfixes, le routage, DNS, la sécurité et le filtrage. L’absence de NAT ne signifie pas qu’un hôte IPv6 doit être exposé sans protection ; les politiques de pare-feu restent essentielles.

### 1.21. CGNAT et limites du partage d’adresses

Les fournisseurs peuvent utiliser un CGNAT (*Carrier-Grade NAT*) pour partager un ensemble limité d’adresses IPv4 publiques entre de nombreux abonnés. La plage `100.64.0.0/10` est définie par la RFC 6598 pour l’espace partagé utilisé dans certains contextes CGN. Elle n’est pas une plage RFC 1918, même si elle n’est pas destinée à être routée globalement.

Lorsqu’un client possède déjà un routeur qui fait PAT, puis que le fournisseur applique encore un NAT, la connexion est souvent décrite comme du double NAT. Cela peut fonctionner pour les connexions sortantes, mais rendre plus difficiles l’hébergement de services, l’accès distant entrant et certaines applications pair-à-pair.

Avant de publier un serveur depuis un accès résidentiel, il faut vérifier si l’adresse outside du routeur est réellement une adresse publique, si elle correspond à l’adresse observée depuis Internet, et si le fournisseur permet les connexions entrantes. Une adresse privée ou CGNAT sur l’interface WAN peut empêcher un port forwarding local d’être suffisant.

### 1.22. Capacité, état et temporisation PAT

PAT n’est pas illimité. Il utilise des identifiants de flux, des structures d’état et des ressources matérielles ou logicielles. Les limites dépendent de la plateforme, du nombre de flux simultanés, de la vitesse des nouveaux flux, du type de trafic et des fonctions de sécurité activées.

Les temporisateurs de traduction permettent de supprimer les entrées inactives. Les valeurs varient suivant les protocoles et l’implémentation ; elles ne doivent pas être présumées universelles. Des entrées trop persistantes peuvent consommer des ressources, tandis que des expirations trop courtes peuvent perturber certaines applications à faible activité.

Les administrateurs doivent surveiller les statistiques NAT, le nombre de translations, l’utilisation des pools et les éventuels échecs d’allocation. Une hausse du trafic ou des sessions simultanées peut révéler un besoin d’ajuster l’architecture plutôt que simplement de changer des temporisateurs.

### 1.23. NAT n’est pas un pare-feu

NAT et pare-feu répondent à des questions différentes. NAT répond à la question « quelle adresse/port doit représenter ce flux ? ». Le pare-feu répond à la question « ce trafic est-il autorisé ? ». Certains équipements intègrent les deux fonctions et peuvent appliquer un suivi d’état, mais une translation n’équivaut pas à une règle explicite de sécurité.

Une règle PAT de sortie permet typiquement à des hôtes internes de créer des sessions vers des destinations externes. Cela n’implique pas nécessairement qu’un hôte externe puisse initier une session arbitraire vers le LAN, car la traduction dynamique et la politique de filtrage peuvent empêcher ce comportement. Toutefois, le fait que les connexions entrantes non sollicitées soient souvent non routées par défaut ne transforme pas NAT en contrôle de sécurité complet.

Les traductions statiques et les port-forwardings sont particulièrement importants à examiner. Ils peuvent rendre un service joignable de l’extérieur lorsque les routes et les règles de sécurité le permettent. Toute publication doit être limitée au strict nécessaire et faire l’objet d’une analyse de risque.

> **Piège :** Une ACL référencée par une commande NAT pour sélectionner les sources n’est pas automatiquement une ACL de filtrage. De même, un port forwarding n’est pas une garantie de sécurité. Pour chaque flux, analyse séparément la traduction, le routage aller et retour, puis la politique de filtrage et le service applicatif. Cette séparation évite de croire qu’une règle NAT « permit » autorise nécessairement le paquet à traverser toutes les politiques du routeur.

```text
                 FLUX SORTANT PAT — VUE LOGIQUE

  Hôte inside                 Routeur NAT                         Hôte outside
  192.168.10.10               Inside / Outside                    198.51.100.80
  TCP 51500                    Table de traduction                 TCP 443
       |                              |                                |
       | Src 192.168.10.10:51500      |                                |
       |----------------------------->|                                |
       |                              | Src devient                    |
       |                              | 203.0.113.10:40001             |
       |                              |------------------------------->|
       |                              |                                |
       |                              | <-------------------------------|
       |                              | Réponse vers 203.0.113.10:40001|
       |                              | Recherche de l'entrée PAT      |
       | <-----------------------------                                |
       | Destination rétablie : 192.168.10.10:51500                    |

  La route de retour doit repasser par l'équipement qui possède l'état
  de traduction, sauf architecture explicitement conçue pour l'éviter.
```

---

## 2. Configuration et Pratique

### 2.1. Topologie et plan d’adressage de laboratoire

Le laboratoire suivant illustre un routeur R1 qui relie un LAN privé à un réseau amont simulant Internet. Les adresses globales utilisent des plages réservées à la documentation : elles sont adaptées aux exemples et non à une mise en production.

| Équipement | Interface | Adresse | Rôle |
|---|---|---|---|
| PC-A | NIC | `192.168.10.10/24` | Client inside |
| PC-B | NIC | `192.168.10.20/24` | Exemple de serveur inside |
| R1 | G0/0 | `192.168.10.1/24` | Interface inside |
| R1 | G0/1 | `203.0.113.2/24` | Interface outside de laboratoire |
| Routeur amont | Interface LAN | `203.0.113.1/24` | Passerelle simulée |
| Serveur externe | NIC | `198.51.100.80/24` | Destination externe, sur un réseau routé de test |

Pour simplifier la pratique, la présence effective de la route entre les blocs de documentation doit être assurée dans le simulateur ou le laboratoire. Dans un environnement réel, utilisez les adresses et les routes fournies par l’opérateur.

```text
      LAN inside                       WAN / réseau de test
  192.168.10.0/24                       203.0.113.0/24

 PC-A .10          G0/0 .1         G0/1 .2        .1 routeur amont
+--------+         +----------------------+     +----------------+
| PC-A   |---------| R1                   |-----| Routeur amont  |---- réseau externe
+--------+         | NAT / PAT             |     +----------------+
                   +----------------------+
                          |
                   PC-B / serveur interne
                   192.168.10.20
```

### 2.2. Configuration de base des interfaces

```cisco
hostname R1
!
interface GigabitEthernet0/0
 description LAN_INSIDE
 ip address 192.168.10.1 255.255.255.0
 ip nat inside
 no shutdown
!
interface GigabitEthernet0/1
 description WAN_OUTSIDE_LAB
 ip address 203.0.113.2 255.255.255.0
 ip nat outside
 no shutdown
!
ip route 0.0.0.0 0.0.0.0 203.0.113.1
```

La première interface est côté LAN privé ; la seconde est côté réseau amont. La route par défaut indique où acheminer les destinations qui ne sont pas couvertes par une route plus précise. Elle ne doit être utilisée que si l’adresse du prochain saut est réellement joignable sur l’interface outside.

Le routage doit être valide dans les deux sens. La configuration NAT présentée plus bas peut traduire les paquets sortants, mais la table de routage et les équipements amont doivent être capables d’acheminer les paquets et les réponses.

### 2.3. Configurer PAT avec l’adresse de l’interface outside

Pour donner accès au réseau externe au sous-réseau privé, la configuration IOS classique est :

```cisco
access-list 10 permit 192.168.10.0 0.0.0.255
!
ip nat inside source list 10 interface GigabitEthernet0/1 overload
```

La règle référence l’ACL 10, utilise l’adresse de G0/1 comme adresse inside globale et active `overload` pour permettre à plusieurs flux de partager cette adresse grâce aux identifiants de transport.

L’ACL ne définit pas à elle seule les routes. Il faut également que les interfaces soient marquées correctement, que l’adresse outside soit fonctionnelle et que le routeur dispose d’un chemin vers les destinations externes.

Après la configuration, génère un flux depuis PC-A, par exemple vers un serveur HTTP/HTTPS de test, puis observe la traduction. Le simple fait de saisir la configuration ne crée pas nécessairement une entrée dynamique avant qu’un flux compatible ne traverse l’équipement.

### 2.4. Vérifier PAT

Les commandes principales sont :

```cisco
show ip nat translations
show ip nat translations verbose
show ip nat statistics
show ip route
show access-lists 10
```

`show ip nat translations` affiche les correspondances actives et les informations de flux disponibles. `verbose` fournit des informations supplémentaires sur les plateformes qui le prennent en charge. `show ip nat statistics` donne des statistiques de traduction et des renseignements sur les interfaces marquées inside/outside. `show ip route` confirme le routage, et `show access-lists 10` permet de vérifier les correspondances et les compteurs de l’ACL.

Une fois le trafic généré, il faut vérifier que l’adresse inside local apparaît avec une adresse inside global attendue et, si PAT est appliqué, les identifiants de transport sont cohérents avec la session observée. Les colonnes exactes et la sortie peuvent varier d’une version à l’autre.

### 2.5. Configurer NAT dynamique avec un pool

Si l’organisation possède plusieurs adresses globales réservées à la traduction, elle peut utiliser un pool :

```cisco
no ip nat inside source list 10 interface GigabitEthernet0/1 overload
!
ip nat pool PUBLICS 203.0.113.10 203.0.113.20 netmask 255.255.255.0
access-list 10 permit 192.168.10.0 0.0.0.255
ip nat inside source list 10 pool PUBLICS
```

La première commande supprime l’ancienne règle PAT de l’exemple ; elle ne doit être exécutée en production qu’après évaluation de l’impact sur les flux en cours. Le pool contient des adresses d’exemple. Dans un déploiement réel, ces adresses doivent avoir été attribuées et leur routage doit être prévu.

Avec la configuration dynamique simple, une allocation consomme une adresse du pool selon les règles du moteur NAT. Une variante en surcharge peut permettre de partager les adresses du pool entre plusieurs flux :

```cisco
ip nat inside source list 10 pool PUBLICS overload
```

Vérifie le comportement dans la documentation de la plate-forme utilisée, surtout si des règles NAT supplémentaires, des route-maps ou du NAT pour plusieurs fournisseurs sont déjà présents.

### 2.6. Configurer NAT statique un-à-un

Pour associer durablement un hôte à une adresse globale :

```cisco
ip nat inside source static 192.168.10.20 203.0.113.20
```

Le serveur interne est alors représenté par l’adresse globale configurée. La machine doit posséder une configuration IP correcte, une passerelle appropriée, un service à l’écoute et une politique de sécurité adaptée.

Pour supprimer cette association, IOS classique emploie normalement la forme `no` de la commande avec les mêmes adresses. Il faut comprendre l’effet opérationnel avant de la retirer : toute connexion qui dépend de cette traduction peut être interrompue.

N’expose pas un serveur simplement parce que tu peux créer une traduction. Avant le déploiement, vérifie la nécessité du service, le port effectivement requis, la politique de filtrage, les journaux et la méthode de retour arrière.

### 2.7. Configurer une traduction de port statique

Pour publier un service HTTPS interne sur le port TCP 443 d’une adresse globale :

```cisco
ip nat inside source static tcp 192.168.10.20 443 203.0.113.20 443
```

Le routeur doit pouvoir recevoir le trafic destiné à l’adresse globale. Si le bloc global est directement connecté, il faut également vérifier le traitement de l’adresse et les éventuelles exigences ARP du réseau amont. Si le bloc est routé vers le routeur, la configuration de routage doit refléter ce mode de livraison.

Le serveur doit répondre par le chemin qui permet au routeur de faire la traduction inverse. En présence de plusieurs passerelles ou d’un pare-feu interne, une route de retour différente peut empêcher la connexion de fonctionner même lorsque la traduction statique paraît correcte.

Il est généralement préférable de ne publier que les ports réellement nécessaires. La translation d’un port externe vers un port interne ne remplace pas le chiffrement, l’authentification ou les mesures de durcissement du serveur.

### 2.8. Vérifier la configuration avant les tests

Avant de générer du trafic, vérifie l’ensemble de la configuration pertinente :

```cisco
show running-config | include ip nat
show running-config | section interface GigabitEthernet0/0
show running-config | section interface GigabitEthernet0/1
show ip interface brief
show ip route
show ip protocols
```

La syntaxe des filtres `include` et `section` est disponible sur de nombreuses versions IOS, mais elle n’est pas identique sur toutes les interfaces de ligne de commande. Si une variante n’est pas prise en charge, utilise `show running-config` puis recherche les sections correspondantes.

Vérifie que l’ACL sélectionne exactement le bon sous-réseau, que les interfaces sont classées comme prévu, que le routeur atteint le prochain saut et que les adresses globales appartiennent à un bloc utilisable dans le laboratoire. Ce contrôle prévient de nombreux problèmes qui seraient difficiles à repérer uniquement à partir de la table de traduction.

### 2.9. Plan de test contrôlé

Un test de NAT doit confirmer plusieurs éléments au lieu de seulement vérifier qu’un ping répond.

1. Vérifie qu’un client possède une adresse privée et une passerelle correctes.
2. Confirme que le client peut atteindre son premier saut local.
3. Confirme que le routeur NAT a une route vers la destination externe.
4. Initie un flux compatible avec la règle — par exemple une connexion TCP vers un serveur de test.
5. Observe l’entrée NAT générée.
6. Vérifie sur le serveur externe l’adresse source observée, lorsque tu contrôles ce serveur.
7. Vérifie les compteurs, les journaux et les éventuelles erreurs.
8. Teste le retour et, pour une publication statique, l’accès depuis un réseau extérieur réel au laboratoire.

ICMP peut aider à valider certains éléments, mais un ping ne représente pas tous les comportements TCP/UDP. Les tests doivent correspondre à l’application et au type de traduction déployés.

### 2.10. Nettoyage des entrées de traduction

Les entrées dynamiques expirent selon des temporisateurs ; les entrées statiques demeurent tant que la configuration existe. Sur IOS classique, il est possible d’effacer des traductions dynamiques avec une commande de maintenance appropriée, mais il faut être prudent : effacer toutes les entrées interrompt potentiellement des sessions actives.

Commande généralement disponible :

```cisco
clear ip nat translation *
```

Utilise-la uniquement lorsque l’impact est compris et qu’une interruption est acceptable, de préférence dans un laboratoire ou pendant une fenêtre de maintenance. Certaines entrées statiques ne peuvent pas être effacées par le même moyen car elles sont issues de la configuration et non d’un état dynamique ordinaire.

Pour les diagnostics courants, il est préférable de commencer par `show ip nat translations` et `show ip nat statistics`, plutôt que de supprimer immédiatement la table. La conservation des entrées et des compteurs peut être utile pour déterminer l’origine du problème.

---

## 3. Dépannage et Sécurité

### 3.1. Aucune traduction n’apparaît

Si un hôte interne n’accède pas à l’extérieur et que la table NAT reste vide, ne commence pas par recréer toute la configuration. Contrôle les éléments dans un ordre reproductible.

1. Vérifie l’adresse IP, le masque, la passerelle et la connectivité du client.
2. Vérifie que le paquet atteint bien le routeur NAT.
3. Vérifie les routes vers la destination.
4. Contrôle les interfaces `ip nat inside` et `ip nat outside`.
5. Vérifie si la règle NAT référence l’ACL correcte.
6. Vérifie que l’ACL sélectionne la source du client.
7. Contrôle les journaux et compteurs pour déterminer si les paquets sont traités ou rejetés ailleurs.

Une ACL utilisée pour la traduction peut être correcte sur le papier mais ne jamais correspondre parce qu’elle utilise un mauvais préfixe ou une wildcard incorrecte. Une autre cause fréquente est l’interface inside/outside qui n’est pas celle par laquelle le trafic traverse réellement l’équipement.

L’ordre précis du traitement interne dépend de l’implémentation, mais ce processus de dépannage distingue déjà les problèmes de connectivité, de classification, de traduction et de routage.

### 3.2. La traduction existe, mais la connexion échoue

Une entrée présente dans la table démontre qu’un certain mécanisme de traduction a été créé ou configuré ; elle ne prouve pas que toutes les étapes du flux fonctionnent.

Vérifie ensuite :

- la route vers la destination et vers le prochain saut ;
- la route de retour du serveur distant ;
- les ACL et politiques de pare-feu ;
- l’adresse et le port sur lesquels le serveur écoute ;
- les traductions de ports si PAT ou static PAT est utilisé ;
- le chemin asymétrique ou l’existence d’un deuxième routeur NAT ;
- les éventuels problèmes de MTU, de fragmentation et de messages ICMP.

Il faut déterminer à quel point le paquet disparaît. Lorsque cela est possible, compare les captures de part et d’autre du NAT. La différence entre l’adresse source avant et après traduction permet de confirmer la réécriture, mais la capture doit aussi examiner le port, le protocole, le sens et la présence du paquet de retour.

### 3.3. Le pool NAT est épuisé

Un pool trop petit peut ne plus fournir d’adresse pour une nouvelle translation dynamique. Les sessions existantes peuvent continuer tandis que de nouveaux utilisateurs échouent à se connecter, ce qui donne parfois l’impression d’une panne intermittente.

Les commandes de statistiques et d’affichage de pool varient selon la plateforme. Commence par `show ip nat statistics` et les commandes prises en charge pour inspecter le pool, puis mesure le nombre de translations actives et le rythme de création des flux.

Les solutions potentielles comprennent l’agrandissement d’un pool routable, l’ajustement de la conception de NAT dynamique, le passage à PAT lorsque cela répond au besoin, ou la réduction des sessions inutiles. PAT doit néanmoins être dimensionné selon les limites du système et de ses ports ; il ne résout pas toutes les limites de capacité.

Évite de simplement réduire les temporisateurs sans mesurer le profil de trafic. Des expirations plus courtes peuvent libérer des entrées, mais peuvent aussi nuire aux sessions qui demeurent silencieuses pendant des périodes prolongées.

### 3.4. Erreur d’ACL ou de wildcard

Si une règle NAT sélectionne trop peu de sources, certains sous-réseaux ne seront pas traduits. Si elle sélectionne trop de sources, des réseaux non prévus pourront être traduits. L’effet exact dépend de la règle et de la politique de routage.

La commande `show access-lists` peut afficher les lignes et des compteurs de correspondance. Génère ensuite un flux contrôlé à partir d’un hôte connu et vérifie que la bonne ligne correspond. Compare le réseau sélectionné à l’adresse réelle du client : une ACL qui vise `192.168.10.0/24` ne sélectionnera pas automatiquement un client `192.168.20.10`.

N’utilise pas le compteur ACL comme seule preuve de réussite. Selon l’endroit où le test s’exécute et la nature du trafic, une correspondance peut être comptée sans que la session arrive à destination. Il faut corréler les compteurs ACL avec les translations, le routage et le résultat du test applicatif.

### 3.5. Interfaces inside/outside inversées ou manquantes

Cette erreur est courante lors de la configuration d’un routeur avec plusieurs interfaces, sous-interfaces 802.1Q ou liens de couche 3. Il faut identifier par où le paquet entre et par où il sort réellement, puis confirmer que la classification NAT reflète cette topologie.

Une interface de LAN peut être une sous-interface, par exemple `GigabitEthernet0/0.10`. Si les paquets arrivent sur cette sous-interface mais que seul le port physique est marqué, le comportement peut ne pas correspondre à ce que prévoit la configuration. Le détail dépend de l’organisation des interfaces et des capacités de la plateforme.

Contrôle `show running-config`, `show ip interface brief`, les routes et les interfaces traversées. Ne te fie pas uniquement au nom `G0/0` ou `G0/1` : le rôle dépend de la topologie, et non du numéro de port.

### 3.6. Problèmes de trafic entrant et de port forwarding

Lorsqu’un service interne est inaccessible depuis Internet, vérifie d’abord si le routeur NAT reçoit les paquets destinés à l’adresse globale. Il faut ensuite confirmer qu’une traduction statique de destination ou de port correspond, que le filtrage autorise le flux et que le serveur répond correctement.

Les causes fréquentes sont :

- adresse publique inexistante ou mal routée vers l’équipement ;
- double NAT ou CGNAT du fournisseur ;
- port global mal configuré ;
- service serveur arrêté ou lié à une mauvaise adresse locale ;
- pare-feu du serveur ou du réseau interne ;
- chemin retour qui évite l’équipement NAT ;
- filtrage amont par le fournisseur ;
- DNS qui pointe vers une adresse incorrecte.

Pour isoler le problème, teste le serveur d’abord depuis le LAN, puis valide le routage vers le réseau amont, puis observe un essai entrant depuis un réseau réellement externe. Tester depuis le même LAN en visant le nom public évalue le hairpin NAT, pas exactement le même chemin que celui d’un utilisateur Internet.

### 3.7. Double NAT et CGNAT

Le double NAT survient lorsque deux équipements traduisent successivement les adresses ou ports. Cela peut arriver, par exemple, quand un routeur personnel fait PAT derrière une passerelle de fournisseur qui effectue aussi du NAT.

Les connexions sortantes peuvent fonctionner parfaitement parce que chaque équipement maintient son propre état. En revanche, publier un service nécessite que chaque niveau de NAT connaisse le chemin entrant approprié, ou que le fournisseur fournisse une solution permettant l’accès entrant. Une redirection locale seule ne suffit pas si le routeur amont ne transmet pas le flux à l’adresse WAN du client.

Compare l’adresse WAN affichée par le routeur local à l’adresse source observée par un service externe, et inspecte le préfixe utilisé. Si l’adresse WAN est privée ou dans `100.64.0.0/10`, cela peut indiquer un équipement amont ou du CGNAT. Ce constat ne suffit pas à identifier toute la topologie, mais il justifie une enquête auprès de l’opérateur.

Les options peuvent inclure une adresse publique directement attribuée, un mode bridge, une mise en DMZ contrôlée, des redirections sur le routeur amont, un tunnel sortant vers un point public ou un service de publication spécialisé. Le choix dépend des exigences de sécurité et de l’offre du fournisseur.

### 3.8. Chemins asymétriques et haute disponibilité

Dans une architecture avec deux fournisseurs, un flux sortant peut passer par ISP-A, tandis que la réponse emprunte ISP-B. Si la traduction a été créée sur R1 associé à ISP-A, l’arrivée du retour sur R2 ou par une sortie qui ne possède pas l’état peut provoquer une rupture de session.

Il faut mettre en cohérence le NAT et le routage. Des règles de routage basé sur des politiques, des tables de routage distinctes, des route-maps ou une conception de l’adresse source peuvent être nécessaires selon la topologie. Les commandes exactes et le comportement de la plateforme doivent être vérifiés avant mise en production.

La haute disponibilité doit aussi traiter l’état de traduction. Le basculement du routage vers un routeur qui ne possède pas la session NAT ne garantit pas la continuité des sessions existantes. Certains produits proposent des mécanismes de synchronisation spécifiques, d’autres non. Il est essentiel de distinguer la redondance du prochain saut de la continuité des états NAT.

### 3.9. NAT et sécurité des hôtes publiés

Les serveurs exposés via static NAT ou port forwarding doivent être considérés comme accessibles depuis les zones autorisées par le routage et le filtrage. Le fait qu’ils utilisent une adresse privée n’est pas une mesure de sécurité suffisante.

Les pratiques recommandées comprennent :

- publier uniquement les services nécessaires ;
- utiliser une politique de filtrage explicite sur la frontière ;
- placer les services accessibles depuis Internet dans une zone adaptée, souvent une DMZ ;
- maintenir le système et l’application à jour ;
- exiger une authentification forte et un chiffrement approprié ;
- journaliser les connexions pertinentes ;
- surveiller les tentatives anormales et les volumes de trafic ;
- documenter les correspondances et les propriétaires des services ;
- supprimer les translations devenues inutiles.

Un port non standard n’est pas un substitut au filtrage ou à l’authentification. Modifier le port externe peut réduire certains bruits de scan simples, mais ne protège pas contre un attaquant capable de détecter le service.

### 3.10. Limites d’algorithmes et compatibilité applicative

NAT peut affecter les applications qui supposent que l’adresse IP ou le port annoncé dans la charge utile correspond à celui de l’en-tête. Les applications qui ouvrent plusieurs connexions, négocient des flux secondaires ou utilisent des informations de connexion incorporées dans des messages peuvent nécessiter un traitement particulier.

Si une application échoue seulement après la traversée du NAT, compare son comportement avec et sans traduction dans un environnement contrôlé. Observe les paquets, les ports négociés, les messages d’erreur et la politique des ALG. N’active pas un ALG au hasard : il peut régler une incompatibilité dans certains scénarios, mais introduire des effets de bord dans d’autres.

Les protocoles modernes peuvent utiliser TLS, des signatures ou des contrôles d’intégrité de bout en bout. Une modification de la charge utile par un ALG peut alors être impossible ou provoquer un échec de validation. La bonne approche consiste à comprendre le protocole et à se référer à la documentation du produit ou du fournisseur de l’application.

### 3.11. Méthode experte de diagnostic par couches

Une procédure reproductible évite de confondre traduction et connectivité. Procède dans cet ordre :

**Couche d’accès** : confirme les VLANs, l’adressage du client, la passerelle et la résolution ARP. Un client qui ne peut pas joindre sa passerelle n’atteindra pas le moteur NAT de manière normale.

**Routage** : valide la route de la destination et le prochain saut. Si le routeur ne sait pas où envoyer le paquet après traduction, NAT ne crée pas la route manquante.

**Classification NAT** : contrôle la direction du flux, les interfaces inside/outside, l’ACL et la règle de traduction. Confirme que le paquet entre et sort sur les interfaces auxquelles la règle s’applique.

**État NAT** : vérifie la présence, les adresses, ports, protocole et l’âge de l’entrée. Compare ces données à la session attendue.

**Politique de sécurité** : contrôle les ACL, le pare-feu, les zones de sécurité et les politiques du serveur. La présence d’une translation ne signifie pas que le paquet est autorisé partout.

**Chemin retour** : confirme que la réponse atteint le routeur qui peut appliquer la traduction inverse. Pour une architecture multi-WAN ou HA, recherche les chemins asymétriques et l’absence de synchronisation d’état.

**Application** : confirme que le service est en écoute et que la session applicative complète se déroule correctement. Un TCP handshake réussi est une preuve différente d’un simple ping.

Cette méthode est volontairement structurée ; selon le symptôme, certains contrôles peuvent être parallélisés. Le principe est de recueillir des preuves à chaque frontière au lieu de modifier aléatoirement la configuration.

### 3.12. Journalisation, supervision et gestion du changement

Surveiller NAT exige de connaître la charge habituelle. Le nombre de translations actives, la consommation des pools, les taux de création et d’expiration, les échecs de session et l’utilisation CPU ou mémoire peuvent signaler une saturation ou une mauvaise configuration.

Les commandes IOS les plus usuelles pour un premier diagnostic sont :

```cisco
show ip nat translations
show ip nat translations verbose
show ip nat statistics
show access-lists
show ip route
show logging
```

Les commandes disponibles, les détails de sortie et les capacités de journalisation diffèrent selon la plateforme. Les fonctions de débogage peuvent générer beaucoup de messages et affecter les performances ; elles doivent être utilisées avec précaution, surtout sur des équipements de production.

Avant toute modification d’une règle NAT, conserve la configuration, identifie le service et les flux affectés, prépare la commande de retour arrière et effectue un test ciblé. Les traductions statiques ont souvent un impact visible immédiat sur les services exposés ; les règles PAT peuvent affecter plusieurs utilisateurs en même temps. Une modification NAT doit donc être traitée comme un changement réseau susceptible d’interrompre des sessions.

> **Astuce :** Pour une première lecture, utilise ensemble `show ip nat translations`, `show ip nat statistics`, `show access-lists` et `show ip route`. Ces quatre vues répondent à quatre questions distinctes : quelle translation existe, que rapporte le moteur NAT, quelle source correspond à la règle, et le routage permet-il d’atteindre le prochain saut ? Ne supprime pas les entrées dynamiques avant d’avoir recueilli ces informations, car elles peuvent être essentielles au diagnostic.

> **Danger :** Une traduction statique ou une redirection de port peut rendre un service interne accessible depuis l’extérieur lorsque le routage et le filtrage le permettent. NAT ne remplace pas un pare-feu et ne protège pas automatiquement le serveur. Avant toute publication, limite les ports, contrôle les sources autorisées si c’est approprié, sécurise et mets à jour l’application, active une journalisation proportionnée et vérifie depuis un réseau réellement externe ce qui est exposé.

---

## Points à retenir

- **NAT et PAT ne sont pas identiques.** NAT traduit les adresses IP ; PAT traduit aussi les identifiants de transport nécessaires pour permettre à plusieurs flux de partager une adresse globale. Le comportement effectif dépend de la règle, de la plateforme et du protocole.

- **La traduction, le routage et la sécurité doivent être diagnostiqués séparément.** Une entrée NAT valide ne garantit pas que le paquet atteigne sa destination, que le retour suive le bon chemin ou que le pare-feu l’autorise. Vérifie les interfaces inside/outside, l’ACL de classification, la table de traduction, la route et le service final.

- **Le PAT économise des adresses, mais introduit de l’état et des limites opérationnelles.** Surveille les traductions actives, les pools, les temporisateurs et les sessions. Le double NAT, le CGNAT, les chemins asymétriques, le DNS et les protocoles qui transportent des adresses dans leur charge utile peuvent compliquer l’accès entrant et le dépannage.

---

## Références techniques

- [RFC 3022 — Traditional IP Network Address Translator (Traditional NAT)](https://www.rfc-editor.org/rfc/rfc3022.html)
- [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918.html)
- [RFC 5737 — IPv4 Address Blocks Reserved for Documentation](https://www.rfc-editor.org/rfc/rfc5737.html)
- [RFC 6598 — IANA-Reserved IPv4 Prefix for Shared Address Space](https://www.rfc-editor.org/rfc/rfc6598.html)
- [RFC 4787 — Network Address Translation Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787.html)
- [Cisco IOS XE — Monitoring and Maintaining NAT](https://www.cisco.com/c/en/us/td/docs/routers/ios/config/17-x/ip-addressing/b-ip-addressing/m_iadnat-monmain-xe.html)
- [Cisco IOS XE — NAT Configuration Guide](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/nat/nat-configuration-guide/nat.html)
