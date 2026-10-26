# Segmentation réseau

> **Mise en contexte**
>
> Un ordinateur compromis dans le réseau bureautique ne devrait pas pouvoir se connecter librement aux serveurs de paie, aux postes d'administration, aux équipements industriels ou aux consoles de sauvegarde. Pourtant, lorsque tous les appareils se trouvent dans un grand réseau plat, un même domaine de confiance, des communications nombreuses et des règles trop larges peuvent permettre à un incident local de se propager. La segmentation réseau réduit ce rayon d'impact en séparant les groupes d'appareils et en contrôlant explicitement les communications entre eux.
>
> La segmentation ne consiste pas seulement à créer des VLAN ou à utiliser des sous-réseaux différents. Elle associe une architecture compréhensible, une politique de flux, des points de contrôle, une gestion des identités, de la supervision et des tests. Ce cours présente la segmentation physique et logique, les VLAN, les zones de sécurité, les ACL, les pare-feu, les sous-réseaux, la microsegmentation, les environnements Cloud, l'accès d'administration, les exceptions, la validation et le dépannage. Les schémas sont volontairement détaillés pour rendre visibles les chemins autorisés et interdits.

## 1. Objectifs pédagogiques et prérequis

À la fin du cours, tu dois savoir expliquer pourquoi un réseau plat augmente le risque, distinguer segmentation L2, segmentation L3 et microsegmentation, concevoir une matrice de flux, choisir une frontière de contrôle, définir des règles de moindre privilège, comprendre les limites d'une séparation par VLAN seule, planifier un déploiement progressif, vérifier IPv4 et IPv6, segmenter les réseaux invités, serveurs, administration et OT, intégrer les principes Zero Trust et dépanner les flux bloqués ou les chemins de contournement.

Les prérequis utiles sont l'adressage IPv4/IPv6, les sous-réseaux, les VLAN, le routage, les trunks 802.1Q, les ACL, les pare-feu et les notions d'authentification. Le cours prolonge les thèmes des pare-feu, du NAT, des VPN, de la sécurité L2, du NGFW et des IDS/IPS. Les adresses documentaires employées dans les exemples sont fictives ; les politiques doivent être adaptées à l'inventaire et à la topologie réels.

## 2. Pourquoi segmenter ?

Dans un réseau plat, de nombreux appareils peuvent se trouver dans le même domaine de diffusion ou disposer de chemins IP très permissifs. Si un poste utilisateur est compromis, l'attaquant peut tenter de découvrir des services, de réutiliser des identifiants, de joindre des serveurs et de se déplacer latéralement. Le contrôle d'accès au périmètre Internet ne suffit pas lorsque le trafic entre hôtes ne franchit pas ce périmètre.

La segmentation divise les actifs en groupes ayant des besoins et niveaux de confiance différents. Les communications entre ces groupes passent par des points de décision : routeur avec ACL, pare-feu stateful, NGFW, contrôles distribués sur les hôtes, ou combinaisons de ces mécanismes. Chaque point applique une politique qui autorise les flux nécessaires et refuse les autres.

**Schéma pédagogique — réseau plat et réseau segmenté**

~~~text
RESEAU PLAT
+----------------------------------------------------------+
| PC-A | PC-B | Imprimante | Serveur paie | Admin | IoT    |
| Tout le monde a potentiellement des chemins trop larges  |
+----------------------------------------------------------+

RESEAU SEGMENTE
+-------------+       +------------------+      +-----------+
| VLAN Users  | ----> | Pare-feu / ACL   | ---> | Serveurs  |
+-------------+       +------------------+      +-----------+
       |                     |                         |
       X                     v                         v
   Admin refuse        règles par flux         zone données
                           |
                           v
                    +---------------+
                    | VLAN Invités  | ---> Internet seulement
                    +---------------+
~~~

L'objectif n'est pas de bloquer toutes les communications. Un serveur Web doit souvent joindre un service applicatif ou une base de données, un poste doit contacter DNS et les services d'identité, et les systèmes de supervision ont besoin de joindre leurs cibles. Une bonne segmentation identifie ces dépendances, puis limite les flux en fonction d'un besoin vérifié.

La segmentation contribue à réduire le rayon d'impact, à isoler des appareils peu fiables, à rendre les règles plus auditables et à faciliter la surveillance. Elle ne remplace pas les correctifs, l'authentification, la sécurité applicative, les sauvegardes ni la réponse à incident. Un acteur qui obtient un accès autorisé à un service vulnérable peut encore agir dans les limites de la politique.

## 3. Segmentation physique, logique et par identité

La segmentation physique utilise des équipements ou des liaisons séparés. Elle peut apporter une séparation forte et un domaine de panne distinct, mais elle augmente le coût, l'espace, le câblage et les besoins d'exploitation. Elle est adaptée lorsque les exigences de sûreté, de réglementation ou d'isolation justifient ce coût.

La segmentation logique utilise notamment les VLAN, les sous-réseaux, les VRF, les ACL et les pare-feu. Plusieurs groupes peuvent partager du matériel tout en utilisant des domaines logiques séparés. La sécurité dépend alors de la configuration et du fait que tous les chemins entre groupes sont contrôlés.

La microsegmentation applique des politiques à une granularité plus fine, parfois au niveau d'un hôte, d'une charge de travail, d'une identité de service ou d'une application. Elle peut réduire les communications latérales même entre ressources hébergées dans un même réseau global. Sa complexité de gestion exige une bonne visibilité des flux et une gouvernance des règles.

**Schéma pédagogique — niveaux de granularité**

~~~text
[Site / zone physique]
        |
        v
[Segmentation L2 : VLAN]
        |
        v
[Segmentation L3 : sous-reseaux / ACL / firewall]
        |
        v
[Segmentation par application et groupe de serveurs]
        |
        v
[Microsegmentation : hote / workload / identite de service]

Plus la granularite augmente, plus l'inventaire et la gouvernance doivent etre precis.
~~~

Une architecture peut combiner les méthodes. Un VLAN utilisateurs distinct de la zone serveur réduit certains chemins, un pare-feu contrôle les flux routés et une politique locale sur le serveur limite les services exposés. Il ne faut pas considérer ces approches comme mutuellement exclusives : elles se complètent si chacune a un objectif et un propriétaire.

## 4. Segmentation L2 : VLAN, domaines de diffusion et limites

Un VLAN sépare un domaine de diffusion Ethernet sur l'infrastructure commutée. Les appareils d'un VLAN partagent généralement le même domaine de diffusion, mais le fait d'être dans des VLAN différents ne définit pas à lui seul la politique IP entre eux. Si le routage inter-VLAN est activé et autorise les flux, les appareils peuvent encore communiquer.

Les ports access relient généralement des terminaux à un VLAN. Les trunks transportent plusieurs VLAN entre équipements, ou vers un point d'accès ou un hyperviseur qui en a besoin. Les trunks doivent être explicitement configurés et leur liste de VLAN limitée au besoin. Les ports inutilisés doivent être désactivés ou isolés selon le processus d'exploitation.

**Schéma pédagogique — VLANs et point de routage**

~~~text
             [Commutateur d'acces]
             /         |         \
            v          v          v
        VLAN 10     VLAN 20     VLAN 30
        Employes    Imprimantes  Invites
            \          |          /
             \         |         /
              v        v        v
              [Commutateur L3 / passerelles]
                            |
                            v
                    [ACL ou pare-feu]
                            |
             +--------------+--------------+
             v              v              v
          Services       Internet       Zone admin
~~~

La segmentation L2 aide à contenir les diffusions et à organiser les rôles. Elle n'empêche pas un utilisateur de joindre une destination située dans un autre VLAN si le routage et les politiques l'autorisent. Il faut également considérer les attaques au sein du VLAN, telles que l'usurpation ARP, les serveurs DHCP non autorisés et les erreurs de configuration de trunk ; les contrôles L2 sont traités dans le cours précédent.

Évite de créer un VLAN sans sous-réseau, propriétaire, passerelle, politique ou justification clairement documentés. Une liste de VLAN immense sans documentation crée des dépendances invisibles. À l'inverse, regrouper imprimantes, invités, serveurs et postes dans un seul VLAN simplement parce qu'ils se trouvent au même étage peut élargir le rayon d'impact.

## 5. Segmentation L3 : sous-réseaux, routage et frontières

Un sous-réseau définit une plage d'adresses IP et aide à déterminer si une destination est directement connectée ou doit être atteinte par une passerelle. Les sous-réseaux sont utiles pour structurer l'adressage, le routage et les points d'application de politique. Mais un sous-réseau n'est pas automatiquement une frontière de sécurité : un routeur peut permettre des communications entre tous les sous-réseaux.

La frontière de sécurité existe là où une décision d'accès est effectivement appliquée. Cela peut être un pare-feu entre zones, une ACL de couche 3, une politique distribuée ou un pare-feu hôte. Une architecture doit montrer ce point de contrôle et garantir que le flux ne dispose pas d'un autre chemin qui le contourne.

**Schéma pédagogique — sous-réseau et contrôle inter-zones**

~~~text
192.0.2.0/24 Users ----\
                        \
                         [Routage L3] --- [Politique ACL / pare-feu]
                        /                          |
198.51.100.0/24 Servers-                           +--> permit flux necessaires
                                                   +--> deny le reste par politique

Les adresses differentes ne garantissent pas un refus sans contrôle d'acces.
~~~

Lorsqu'un flux doit être contrôlé, vérifie l'interface et le sens de la règle, la route aller, la route retour, le NAT éventuel et les ACL qui peuvent déjà s'appliquer. Une route peut être correcte tandis que le pare-feu refuse le flux, ou l'inverse. La validation doit inclure les deux directions et les tests qui doivent échouer.

Le plan d'adressage doit éviter les chevauchements, faciliter l'agrégation lorsque cela est approprié et réserver des plages dédiées aux serveurs, clients VPN, invités, gestion et IoT. Les routes doivent être cohérentes avec la frontière choisie. Une segmentation difficile à comprendre sera plus susceptible de produire des exceptions larges et des erreurs pendant les changements.

## 6. Concevoir des zones de sécurité

Une zone de sécurité regroupe des interfaces ou réseaux qui partagent une politique commune. Les zones fréquentes comprennent WAN/Internet, postes utilisateurs, serveurs applicatifs, données, DMZ, invités, administration, partenaires, VPN et environnements de test. La classification doit suivre la fonction et le risque, pas uniquement la localisation physique.

**Schéma pédagogique — architecture de zones**

~~~text
                          [Internet]
                              |
                         [Pare-feu]
                   ___________|____________
                  |           |            |
                  v           v            v
                [DMZ]      [Users]      [VPN users]
                  |           |            |
             Web publie       |       ressources selon role
                  |           v
                  |     [Pare-feu interne]
                  |       /            \
                  v      v              v
             [Backend] [Services]    [Admin]
                  |
                  v
             [Base de donnees]
~~~

La DMZ contient généralement des services exposés qui ne devraient pas avoir un accès implicite au LAN ou aux données. Les communications du Web vers l'application ou de l'application vers la base doivent être définies individuellement, avec les ports et destinations nécessaires. Les services publiés ne devraient pas disposer d'un accès général aux postes ou à l'administration.

Une zone n'est pas une confiance absolue. Deux serveurs de la même zone peuvent avoir des exigences différentes, et un appareil compromis dans une zone « interne » reste un risque. Des règles par hôte ou application peuvent être nécessaires pour les actifs sensibles. Le modèle de confiance doit préciser les flux autorisés et les voies d'accès administratives.

## 7. Inventaire des actifs et classification

La segmentation commence par l'inventaire : identité de l'appareil, propriétaire, fonction, système d'exploitation, criticité, emplacement logique, adresse, données manipulées, dépendances et mode de maintenance. Sans inventaire, la politique repose sur des hypothèses et les exceptions deviennent permanentes.

Classe les actifs d'après les besoins de confidentialité, d'intégrité et de disponibilité, puis identifie ceux dont la compromission aurait un impact disproportionné. Les données sensibles, les systèmes d'administration, les sauvegardes, les contrôleurs d'identité et les équipements OT exigent souvent des chemins plus strictement contrôlés que les postes utilisateurs ordinaires.

**Schéma pédagogique — classification vers la politique**

~~~text
[Inventaire actif]
       |
       v
[Fonction + proprietaire + criticite + donnees]
       |
       v
[Classe de protection]
       |
       v
[Zone / sous-reseau / identite]
       |
       v
[Flux autorises + controles + journaux]
       |
       v
[Test, approbation et revue periodique]
~~~

L'inventaire doit refléter les appareils dynamiques : postes portables, machines virtuelles, conteneurs, téléphones, capteurs IoT et identités de service. Une adresse IP peut être réattribuée, un service peut changer de serveur et un groupe Cloud peut se modifier automatiquement. La politique doit se baser sur des critères durables lorsqu'ils sont disponibles et garder une traçabilité des changements.

Les exceptions doivent être identifiées, avoir un responsable, une raison, un périmètre et une échéance. Un appareil non inventorié ne doit pas automatiquement recevoir les droits d'un appareil connu. Utilise un réseau de quarantaine ou un accès de remédiation adapté lorsque l'architecture permet ce traitement.

## 8. Construire une matrice de flux

La matrice de flux décrit qui doit joindre quoi, pour quelle raison et par quel service. Elle constitue la base de la politique ; elle évite les règles vagues qui autorisent « users vers servers any ». Les sources d'information incluent les documents d'architecture, les propriétaires applicatifs, les journaux, les captures autorisées et les tests fonctionnels.

**Schéma pédagogique — matrice de flux**

~~~text
+------------+-------------+--------------+-----------+--------------+
| Source     | Destination | Application  | Decision  | Justification|
+------------+-------------+--------------+-----------+--------------+
| Users      | DNS interne | DNS          | Permit    | Resolution   |
| Users      | Paie        | HTTPS         | Permit    | Application  |
| Invites    | LAN interne | Any           | Deny      | Isolation    |
| Admin host | Equipements | SSH/HTTPS     | Permit    | Gestion      |
| Web DMZ    | DB          | Port exact    | Permit    | Application  |
+------------+-------------+--------------+-----------+--------------+

Chaque ligne doit avoir un proprietaire, un test et des logs utiles.
~~~

Pour construire la matrice, pars des flux essentiels puis vérifie-les dans un environnement d'observation. Les journaux doivent être interprétés avec prudence : l'absence de trafic pendant une courte période ne signifie pas qu'un flux n'est jamais nécessaire. Recueille des périodes représentatives et vérifie les traitements mensuels, les sauvegardes, la haute disponibilité, les accès de maintenance et les scénarios de reprise.

Un flux autorisé doit préciser les sources, destinations et services nécessaires. Lorsque l'application utilise des dépendances multiples, documente-les plutôt que d'ouvrir une large plage sans justification. Les flux interdits doivent eux aussi être explicitement testés, notamment l'accès des invités aux serveurs, celui des utilisateurs aux interfaces de gestion et les communications inutiles entre zones.

## 9. Politique de moindre privilège entre segments

Le moindre privilège signifie n'autoriser que les communications nécessaires à un usage. Une politique par défaut de refus peut être utile, mais elle doit être introduite avec un inventaire et une procédure de changement qui protègent la disponibilité. Le but n'est pas de créer des refus sans comprendre les dépendances, mais de définir une politique claire et vérifiable.

**Schéma pédagogique — décision d'accès**

~~~text
Tentative de connexion
        |
        v
[Identifier source / destination / service / identite]
        |
        v
[Existe-t-il une ligne approuvee dans la matrice ?]
        |
      +---+---+
      |       |
     oui     non
      |       |
      v       v
[Controle   [Refus + journal]
 additionnel]
      |
      v
[Autoriser uniquement si les conditions sont remplies]
~~~

Pour chaque règle, indique la source, la destination, l'application ou le port, la direction, l'action, la justification, le propriétaire, la journalisation et la durée si elle est temporaire. L'ordre de traitement dépend du produit : certaines règles utilisent la première correspondance, d'autres regroupent plusieurs étapes de politique. Consulte la documentation de la plateforme et vérifie la règle effectivement appliquée.

Évite les règles génériques qui contournent l'intention, telles que « utilisateurs vers toutes les zones, tous ports », « serveurs vers Internet sans restriction » ou « toute adresse du VPN vers réseau d'administration ». Si une exception est nécessaire en urgence, limite-la, surveille-la et planifie sa suppression ou sa validation formelle.

## 10. Segmentation et routeurs/pare-feu

Les points de contrôle possibles incluent ACL sur les interfaces L3, pare-feu stateful entre zones, NGFW avec identification applicative, pare-feu hôte, contrôles d'accès réseau et politiques distribuées. Le choix dépend de la visibilité requise, du volume de trafic, de la latence, des compétences opérationnelles et de la possibilité de tracer les décisions.

Une ACL de routeur peut être efficace pour des critères simples sur les adresses, protocoles et ports. Un pare-feu stateful peut suivre les sessions et simplifier le traitement du trafic retour. Un NGFW peut ajouter le contexte d'application, d'utilisateur et des profils de sécurité, lorsque la visibilité et les fonctions sont disponibles. Un pare-feu hôte protège même lorsque le flux ne traverse pas la frontière réseau centrale.

**Schéma pédagogique — contrôles en défense en profondeur**

~~~text
[Terminal]
   |
   v
[Port access / 802.1X / controle L2]
   |
   v
[VLAN / sous-reseau]
   |
   v
[ACL L3 ou pare-feu inter-zones]
   |
   v
[NGFW / inspection applicative si necessaire]
   |
   v
[Serveur avec pare-feu hote et droits minimaux]
   |
   v
[Journaux / detection / revue]
~~~

Des contrôles en double peuvent être utiles s'ils ont des rôles distincts. Ils deviennent problématiques lorsque personne ne comprend quel équipement a bloqué le flux ou lorsqu'une règle plus large sur un chemin alternatif contourne les restrictions. Documente le propriétaire de chaque frontière et garde une méthode de diagnostic qui suit les adresses et les règles de bout en bout.

Ne suppose pas que le routage inter-VLAN est automatiquement limité. Les passerelles L3 et les routes peuvent assurer la connectivité mais nécessiter des ACL explicites. Vérifie également IPv6, car une politique uniquement IPv4 peut laisser un autre chemin ouvert si IPv6 est activé.

## 11. Microsegmentation des serveurs

Un réseau de serveurs ne devrait pas nécessairement être un domaine de confiance unique. Le Web, les services applicatifs, les bases de données, l'identité, la supervision et les sauvegardes ont des fonctions différentes. Une règle de segmentation peut limiter la communication à l'application et aux dépendances réellement nécessaires, au lieu d'autoriser chaque serveur à joindre les autres.

**Schéma pédagogique — flux applicatifs à granularité fine**

~~~text
Internet
   |
   v
[Serveur Web / DMZ]
   | HTTPS interne autorise
   v
[Serveur applicatif]
   | port DB requis seulement
   v
[Base de donnees]
   ^
   | administration depuis bastion uniquement
[Bastion / zone admin]

Le Web ne se connecte pas directement a tous les serveurs.
~~~

La microsegmentation peut être appliquée via des politiques de pare-feu distribuées, une politique réseau de virtualisation, des pare-feu hôtes ou des identités de charges de travail. Il faut comprendre les possibilités de la plateforme, les flux requis et les dépendances de haute disponibilité. Les règles doivent suivre les identités et rôles autant que possible lorsque les adresses changent fréquemment.

La granularité augmente les besoins d'exploitation : une règle peut casser lors d'un redéploiement, une identité de service peut changer ou une nouvelle dépendance peut être introduite par une mise à jour. Il faut automatiser l'inventaire et les tests lorsque c'est approprié, sans laisser un système automatisé accorder des droits excessifs à la suite d'une erreur de classification.

## 12. Segmenter les accès d'administration

Le plan de gestion est particulièrement sensible : commutateurs, routeurs, pare-feu, hyperviseurs, plateformes de sauvegarde, annuaires et consoles de sécurité peuvent offrir un accès étendu. Il devrait être accessible depuis des sources dédiées, des comptes individuels, une MFA lorsque disponible, et un processus de privilèges contrôlés.

**Schéma pédagogique — chemin d'administration**

~~~text
[Poste d'administration géré]
            |
            v
   [MFA / identité / appareil conforme]
            |
            v
        [Bastion]
            |
            v
    [Pare-feu de gestion]
       /       |       \
      v        v        v
 [Switchs] [Serveurs] [NGFW]

Un poste utilisateur ordinaire n'a pas de chemin direct vers les interfaces admin.
~~~

Le poste d'administration ne doit pas servir à la navigation quotidienne et au courrier général si la politique de l'organisation peut les séparer. Les sessions doivent être limitées aux systèmes et actions nécessaires, journalisées, et retirées rapidement lorsque les droits ne sont plus justifiés. Prévois un chemin de secours protégé qui ne dépend pas exclusivement du réseau que tu risques de couper lors d'un changement.

La segmentation de gestion ne remplace pas les autorisations applicatives ni la sécurité de l'identité. Un utilisateur qui peut atteindre le bastion n'a pas automatiquement le droit de se connecter à chaque équipement. Les règles doivent définir les rôles, destinations, ports et mécanismes de traçabilité.

## 13. Réseaux invités, BYOD et IoT

Les invités, appareils personnels et objets connectés présentent des profils de mise à jour, d'identité et de gestion différents de ceux des appareils administrés. Ils doivent avoir des accès limités et ne pas rejoindre implicitement les mêmes réseaux que les systèmes internes. Pour les invités, l'objectif est souvent d'autoriser Internet et les services de portail nécessaires tout en refusant les sous-réseaux privés internes.

Les appareils IoT peuvent être difficiles à authentifier ou mettre à jour. Place-les dans des segments dédiés, limite leurs destinations aux serveurs de gestion et services nécessaires, surveille les changements de comportement et documente les exceptions. Ne donne pas à une caméra ou une imprimante les mêmes accès qu'à un poste de travail simplement parce qu'elle se trouve dans le bureau.

**Schéma pédagogique — politique pour invités et objets connectés**

~~~text
[Wi-Fi invite] ----> [DNS / portail / Internet autorises]
       |
       X------> [LAN utilisateurs]
       X------> [Serveurs internes]
       X------> [VLAN gestion]

[IoT / imprimantes] ---> destinations de supervision et services necessaires
       |
       X------> [Administration generale]
~~~

Un réseau invité peut partager une infrastructure physique avec le réseau interne, mais doit être séparé logiquement et contrôlé sur les points de routage. Configure également l'isolation client à client si le modèle sans fil le permet et si elle correspond au besoin. Un SSID invité seul ne garantit pas que les chemins filaires sont isolés.

Teste le refus des flux vers les serveurs, les interfaces de gestion, les imprimantes sensibles et les autres clients, ainsi que l'accès Internet nécessaire. Si un appareil doit joindre une ressource spécifique, crée une exception documentée pour cette destination, pas un accès général au réseau interne.

## 14. DMZ et services exposés

Une DMZ héberge des services qui doivent être atteignables depuis un réseau moins fiable, tout en limitant leur accès aux systèmes internes. Les règles doivent contrôler le trafic vers la DMZ, depuis la DMZ et entre ses composants. Il est souvent nécessaire d'autoriser un flux Internet vers un serveur Web, puis un flux du Web vers l'application, et enfin un flux de l'application vers une base. Ces flux n'impliquent pas d'autoriser la DMZ vers tout le LAN.

**Schéma pédagogique — application Web segmentée**

~~~text
Internet
   |
   v
[NGFW / publication HTTPS]
   |
   v
[DMZ: serveur Web]
   |
   | flux précis vers le backend
   v
[Zone applicative]
   |
   | port base de donnees requis
   v
[Zone donnees]

Refuser Web/DMZ --> postes utilisateurs, gestion et services non necessaires.
~~~

Les serveurs de la DMZ doivent être corrigés, surveillés et configurés avec des droits limités. L'administration doit partir du chemin approuvé, idéalement via bastion et MFA. Les services de gestion ne doivent pas être exposés à Internet ou ouverts depuis toute la DMZ.

Un service publié peut être protégé par NAT, mais la traduction n'est pas une décision de sécurité complète. Le pare-feu doit appliquer une politique, et les routes retour doivent être correctes. Vérifie que le backend ne peut pas initier arbitrairement des connexions vers la base, les postes ou les interfaces d'administration.

## 15. Segmentation des environnements Cloud

Dans le Cloud, les frontières logiques peuvent inclure des VPC ou VNet, sous-réseaux, tables de routage, groupes de sécurité, ACL réseau, pare-feu Cloud, identités IAM et politiques d'application. Les noms varient selon le fournisseur. Une séparation des sous-réseaux n'empêche pas automatiquement les communications si les routes et politiques autorisent les flux.

La conception doit combiner les chemins réseau avec les identités et les autorisations de service. Les groupes de sécurité souvent associés aux interfaces ou charges de travail diffèrent d'ACL appliquées au sous-réseau ; les comportements de stateful/stateless, l'ordre et la granularité dépendent du fournisseur. Consulte la documentation de la plateforme réellement utilisée.

**Schéma pédagogique — réseau Cloud segmenté**

~~~text
                 [Internet Gateway / Edge]
                           |
                     [Pare-feu Cloud]
                           |
                +----------+-----------+
                |                      |
                v                      v
           [Subnet DMZ]           [Subnet prive]
           load balancer          /          \
                |                v            v
                +----------> [App]        [Base de donnees]
                                 |
                           IAM / politiques
                                 |
                           journaux Cloud
~~~

Une charge de travail peut changer d'adresse, être recréée ou utiliser des identités de service ; une règle fondée uniquement sur une adresse temporaire peut ne plus correspondre à l'actif attendu. Utilise les groupes, tags, rôles et mécanismes approuvés lorsque cela améliore la fiabilité, mais vérifie comment ils sont assignés et par qui.

Contrôle les chemins d'accès public, les endpoints privés, la connectivité hybride, les peering, les passerelles, les services partagés et les routes entre comptes ou projets. Les chemins que les équipes ont oubliés sont souvent ceux qui créent une segmentation apparente sans isolation réelle.

## 16. Segmentation et Zero Trust

Le principe Zero Trust refuse de considérer un appareil ou un utilisateur comme automatiquement fiable parce qu'il se trouve sur le réseau interne. L'accès à une ressource devrait dépendre de l'identité, de l'état de l'appareil, du contexte et de la politique applicable. La segmentation réseau reste utile mais ne remplace pas les décisions centrées sur la ressource.

**Schéma pédagogique — confiance explicite**

~~~text
[Utilisateur] + [Appareil] + [Contexte]
               |
               v
       [Authentification]
               |
               v
       [Decision d'autorisation]
               |
       +-------+-------+
       |               |
       v               v
[Application A]   [Application B]
droits precis     acces refuse si non requis

Etre dans un VLAN interne n'equivaut pas a avoir tous les droits.
~~~

Une architecture Zero Trust peut combiner segmentation, identité, MFA, posture de l'appareil, politiques applicatives et surveillance continue. Les décisions doivent être proportionnées et testées pour ne pas confondre sécurité forte et indisponibilité. La ségrégation du réseau reste une couche, pas l'unique base de décision.

Il faut également traiter les comptes techniques et les identités machine. Un service peut avoir besoin d'accéder à un autre service, mais le chemin doit être explicite et limité. Les secrets, certificats et jetons doivent être protégés, et les autorisations revues à mesure que les applications évoluent.

## 17. IPv6 : segmentation symétrique et vérifiable

Si IPv6 est actif, les politiques doivent couvrir les adresses et routes IPv6 ainsi que les mécanismes associés. Une architecture sécurisée en IPv4 mais permissive en IPv6 peut permettre à certains flux de contourner les restrictions prévues. L'équipe doit savoir si IPv6 est pris en charge, désactivé explicitement ou partiellement actif dans les systèmes, VLAN et services.

Les adresses temporaires, les adresses link-local, Neighbor Discovery, Router Advertisements et les mécanismes d'autoconfiguration font partie du modèle IPv6. Ne copie pas simplement une ACL IPv4 en changeant le protocole. Vérifie le comportement des équipements, les groupes multicast nécessaires, les règles ICMPv6 indispensables et les contrôles compatibles avec le réseau.

**Schéma pédagogique — éviter une politique asymétrique**

~~~text
Flux IPv4: poste ---> ACL IPv4 ---> serveur     [politique controlee]
Flux IPv6: poste ---> chemin IPv6 direct ---> serveur ? [risque si oublie]

Validation:
1. Inventorier IPv4 ET IPv6
2. Verifier routes et ACL de chaque famille
3. Tester acces autorise et refus
4. Superviser les deux chemins
~~~

Désactiver IPv6 à un endroit tout en le laissant actif ailleurs n'est pas une méthode cohérente. La décision doit être explicite, documentée et testée. Si IPv6 est nécessaire, sa sécurité doit faire partie de la matrice de flux, des tests, du monitoring et de la réponse à incident.

## 18. Segmentation des réseaux OT/ICS

Les réseaux opérationnels contrôlent des processus physiques et peuvent avoir des besoins de disponibilité, de latence et de compatibilité différents des réseaux bureautiques. Il est courant de séparer postes opérateurs, systèmes de contrôle, automates, serveurs d'historique, postes d'ingénierie et accès fournisseur. Les chemins doivent être documentés et contrôlés par des frontières adaptées à l'architecture.

**Schéma pédagogique — zones OT simplifiées**

~~~text
[IT entreprise]
      |
 [Pare-feu / DMZ industrielle]
      |
[Services de mediation / historien]
      |
 [Pare-feu cellule OT]
      |
[HMI / poste ingenierie]
      |
[PLC / automates / equipements terrain]

Les acces fournisseur et administration sont explicites, limites et journalises.
~~~

Évite les connexions directes non contrôlées entre Internet, le réseau bureautique et les automates. L'accès fournisseur doit être approuvé, limité dans le temps, authentifié, surveillé et révoqué après usage. Les règles doivent prendre en compte les protocoles nécessaires, les dépendances et l'effet potentiel d'un blocage.

Le déploiement doit être coordonné avec les responsables OT. Une règle testée sur un serveur bureautique peut être inappropriée sur un équipement industriel. Commence par cartographier et observer, teste en laboratoire ou sur un environnement représentatif, prépare le rollback et ne modifie pas les protections actives sans autorisation.

## 19. Segmentation et identité : 802.1X, NAC et quarantaine

Le contrôle d'accès réseau peut attribuer un VLAN, un rôle ou une politique en fonction de l'identité et du type d'appareil. 802.1X et un serveur d'authentification peuvent décider si un terminal est autorisé à accéder à un segment. Les appareils qui ne supportent pas l'authentification peuvent nécessiter un traitement particulier, par exemple MAB avec une politique plus limitée, mais l'adresse MAC n'est pas une preuve robuste d'identité.

Un NAC peut combiner identité, posture, inventaire et politique. Les détails varient selon l'architecture. Un appareil inconnu ou non conforme peut être placé dans une zone de quarantaine qui permet l'accès aux services de remédiation, mais pas aux ressources sensibles.

**Schéma pédagogique — décision NAC**

~~~text
[Appareil se connecte au port / Wi-Fi]
                |
                v
     [Identification / authentification]
                |
                v
        [Posture / inventaire]
                |
        +-------+---------+
        |                 |
        v                 v
[Conforme / autorise] [Inconnu / non conforme]
        |                 |
        v                 v
[Role / VLAN attendu] [Quarantaine / remediation]
        |                 |
        v                 v
[Flux necessaires]   [Correction puis revalidation]
~~~

Le mode fail-open peut permettre à un appareil de se connecter si le serveur d'authentification est indisponible, alors que fail-closed peut interrompre des utilisateurs légitimes. Le comportement d'urgence doit être décidé et testé, en particulier pour les équipements critiques. Les exceptions doivent être documentées et surveillées.

Ne confonds pas authentification réseau et autorisation à toutes les ressources. Un utilisateur peut être authentifié mais ne nécessiter que l'accès à une application. Les politiques inter-zones, l'accès applicatif et les droits sur les serveurs restent nécessaires.

## 20. Supervision, journaux et validation continue

Une segmentation est réellement efficace seulement si les règles actives correspondent au design et si les chemins non autorisés sont refusés. Les journaux doivent enregistrer les flux importants, les refus pertinents, les modifications de règle, les changements de route et les événements NAC ou d'identité. Les logs sont utiles lorsqu'ils fournissent l'heure, la source, la destination, le service, la règle et l'action.

**Schéma pédagogique — validation d'un contrôle**

~~~text
[Flux documente dans la matrice]
                |
                v
       [Regle de controle configuree]
                |
                v
       [Test flux autorise] ----> doit reussir
                |
                v
       [Test flux interdit] ----> doit echouer
                |
                v
       [Journaux / compteurs / routes]
                |
                v
       [Revue + preuve + ticket]
~~~

Une règle peut paraître correcte dans la configuration mais ne pas être attachée à la bonne interface ou ne pas couvrir IPv6. Un flux peut également passer par un chemin secondaire. Le test doit donc confirmer le comportement sur le chemin réel et inclure au moins un accès autorisé et un accès qui doit être refusé.

La surveillance de la dérive compare l'état réel à l'état approuvé. Cela peut inclure des routes, ACL, règles de pare-feu, objets, tags Cloud, VLAN et exceptions. Toute différence n'est pas forcément malveillante, mais elle doit être expliquée. Une revue périodique évite que les anciennes règles et projets temporaires deviennent un réseau plat à nouveau.

## 21. Déployer progressivement et préparer le retour arrière

Une segmentation peut interrompre des services si les dépendances n'ont pas été identifiées. Déploie par phases : cartographie, observation, pilote, validation, extension progressive et revue. Commence avec un groupe limité et des flux bien compris, surtout lorsque les applications sont critiques ou que l'accès de gestion peut être affecté.

Avant un changement, sauvegarde la configuration, vérifie l'accès de secours, documente les commandes ou actions, identifie les critères de succès et prépare le rollback. Le rollback doit restaurer un état connu sans supprimer les journaux ou la preuve du défaut. Les changements doivent être horodatés et associés à un propriétaire.

Évite de remplacer un ensemble de règles par une ouverture générale lorsque le service tombe. Si une mesure d'urgence est indispensable, encadre-la par une approbation, un périmètre minimal, une durée courte et une surveillance accrue. Une correction est terminée lorsque le flux requis fonctionne, les refus attendus restent en place et les logs démontrent le résultat.

## 22. Procédure de dépannage d'un flux inter-segments

1. Note la source, la destination, le protocole, les ports, l'heure et le résultat attendu.
2. Vérifie les adresses, masques, passerelles et routes aller/retour.
3. Détermine si les hôtes sont dans des VLAN ou zones différents et quel équipement route entre eux.
4. Identifie l'ACL ou la règle de pare-feu appliquée et son sens.
5. Vérifie le NAT éventuel, les objets avant/après traduction et la session stateful.
6. Consulte les journaux et compteurs du point de contrôle.
7. Vérifie les règles hôtes, DNS, identité, application et posture de l'appareil.
8. Teste IPv4 et IPv6 séparément si les deux sont activés.
9. Compare avec une source de référence autorisée et un flux qui doit être refusé.
10. Change un élément à la fois, documente la preuve et teste l'absence de régression.

Une panne applicative n'est pas toujours une panne de segmentation. Le service peut être arrêté, le DNS mal configuré ou le certificat expiré. Inversement, le fait qu'un ping fonctionne ne prouve pas que le service métier a besoin ou doit avoir accès aux mêmes ports. Diagnostique le flux précis plutôt que d'ouvrir le segment entier.

## 23. Travaux pratiques guidés

### TP 1 — Segmenter un petit réseau d'agence

**Contexte :** une agence possède des postes, des imprimantes, un réseau invité, des serveurs internes et un réseau de gestion. Les invités ne doivent pas joindre les imprimantes, les serveurs ou les interfaces de gestion. Les postes doivent accéder à DNS, aux services d'identité et à une application métier. Les administrateurs utilisent un poste dédié.

**Travail demandé :** définis les VLAN et sous-réseaux, dessine les points de routage, écris une matrice de flux, configure les contrôles appropriés en laboratoire et teste les accès autorisés et les refus.

**Correction attendue :** utilise des segments distincts pour utilisateurs, imprimantes/IoT, invités, serveurs et gestion selon le besoin. Le routage inter-segments passe par une politique de contrôle. Le VLAN invité peut accéder à Internet et aux services de portail nécessaires, mais pas aux ressources internes. L'administration est réservée au poste et à l'identité approuvés. Teste DNS, application métier, refus invité-vers-serveur et refus utilisateur-vers-interface de gestion.

### TP 2 — Construire une matrice pour une application à trois couches

**Contexte :** un portail Web se trouve dans une DMZ, un serveur applicatif dans une zone privée et une base de données dans une zone de données. Les utilisateurs accèdent au portail par HTTPS. Le serveur Web communique vers l'application sur un service précis, puis l'application vers la base sur le port requis.

**Travail demandé :** dessine le chemin, liste les flux, détermine les autorisations, prévois les journaux et ajoute les tests négatifs.

**Correction attendue :** autorise Internet vers le portail publié seulement sur le service exposé. Autorise le Web vers l'application uniquement sur le port nécessaire, puis l'application vers la base uniquement sur le service prévu. Refuse l'accès direct d'Internet à la base, l'accès de la DMZ aux postes et les connexions d'administration en dehors du bastion. Vérifie la route retour, NAT et journaux.

### TP 3 — Mettre en place une quarantaine pour les appareils inconnus

**Contexte :** les ports d'accès reçoivent des postes gérés, des imprimantes et certains appareils inconnus. L'organisation veut empêcher un appareil inconnu d'accéder directement aux serveurs, tout en permettant son identification et sa remédiation.

**Travail demandé :** propose un mécanisme d'identification, une zone de quarantaine, les flux de remédiation et les critères de sortie de quarantaine. Explique la décision en cas de panne de l'authentification.

**Correction attendue :** utilise 802.1X/NAC lorsque l'environnement le supporte, avec une politique restreinte pour les appareils incompatibles et contrôlée. Les ressources de quarantaine se limitent aux services d'identification, de mise à jour et de remédiation. Le comportement fail-open/fail-closed doit être choisi selon la criticité et testé. L'appareil sort de quarantaine après vérification de l'identité et de l'état de conformité.

## 24. Exercices corrigés

### Exercice 1 — Deux VLAN, aucune ACL

Deux VLAN ont des sous-réseaux différents et peuvent se joindre librement. La segmentation est-elle complète ?

**Correction :** non. Les VLAN séparent les domaines de diffusion L2, mais le routeur ou commutateur L3 autorise les flux inter-VLAN. Ajoute et valide une politique à la frontière de routage, selon le besoin.

### Exercice 2 — Les invités doivent imprimer

Une équipe demande un accès du VLAN invité à toutes les imprimantes internes. Quelle démarche adopter ?

**Correction :** vérifie le besoin, le type de service, les imprimantes autorisées et les risques. Préfère un service d'impression ou une destination dédiée, et autorise seulement les ports nécessaires. Ne donne pas aux invités accès à tout le VLAN imprimantes.

### Exercice 3 — Serveur Web vers base de données

Pourquoi ne pas autoriser toute la DMZ vers le VLAN données ?

**Correction :** un service Web compromis pourrait alors tenter d'atteindre toutes les bases et serveurs. Limite le flux au serveur applicatif ou hôte attendu, au port nécessaire et au sens prévu. Utilise les journaux et tests négatifs pour confirmer la restriction.

### Exercice 4 — Règle temporaire devenue permanente

Que faut-il faire ?

**Correction :** identifier le propriétaire, analyser les compteurs sur une période adaptée, faire confirmer le besoin puis supprimer ou formaliser la règle. Une exception doit avoir un périmètre, une justification et une date de revue.

### Exercice 5 — IPv4 bloqué, IPv6 fonctionne

Que révèle ce cas ?

**Correction :** la politique peut avoir été appliquée uniquement à IPv4 alors qu'un chemin IPv6 reste disponible. Inventorie les interfaces et routes IPv6, applique une politique équivalente et teste explicitement les deux familles.

### Exercice 6 — L'application ne fonctionne plus après segmentation

Quelle méthode suivre ?

**Correction :** identifie le flux précis, les dépendances et les règles rencontrées. Utilise les logs, compteurs et une matrice pour déterminer ce qui manque, puis ajoute une règle minimale si le besoin est confirmé. Ne permets pas tout trafic pour masquer la cause.

### Exercice 7 — Un appareil inconnu est branché sur un port d'accès

Quelles protections pourraient s'appliquer ?

**Correction :** 802.1X/NAC, une politique MAB limitée pour les appareils incompatibles, un VLAN de quarantaine, port security et contrôle physique selon le contexte. L'adresse MAC seule n'est pas une preuve robuste d'identité.

### Exercice 8 — Les serveurs d'une même zone se parlent tous

Quel risque cela crée-t-il ?

**Correction :** la compromission d'un serveur peut offrir des chemins de déplacement latéral. Identifie les communications nécessaires et applique une politique par application ou hôte si le risque le justifie. Vérifie que la granularité reste administrable.

### Exercice 9 — Une DMZ peut-elle initier une connexion vers le LAN ?

**Correction :** uniquement lorsqu'un flux précis est nécessaire et explicitement autorisé. Les communications de la DMZ vers le réseau interne doivent être limitées, journalisées et révisées. Une publication Web ne justifie pas l'accès général à l'intérieur.

### Exercice 10 — Le pare-feu a une règle correcte, mais le flux échoue

Que faut-il vérifier ?

**Correction :** route aller/retour, ACL sur une autre interface, NAT, état de session, pare-feu hôte, DNS et service cible. Le flux peut également contourner le point de contrôle prévu. Suis le chemin de bout en bout.

### Exercice 11 — Un projet Cloud utilise un peering

Pourquoi faut-il réévaluer la segmentation ?

**Correction :** le peering, les routes et les règles Cloud peuvent ouvrir un chemin entre réseaux ou comptes. Vérifie les tables de routage, groupes de sécurité, ACL, pare-feu, endpoints et accès publics après chaque modification.

### Exercice 12 — Réseau OT et réseau bureautique

Pourquoi séparer ces environnements ?

**Correction :** ils ont des besoins, risques et contraintes de disponibilité différents. La séparation limite les chemins directs et aide à contrôler les accès fournisseur et d'administration. Toute modification doit être coordonnée avec les responsables OT et testée prudemment.

## 25. Défi final — architecturer la segmentation d'une entreprise

### Contexte

Une entreprise possède des utilisateurs internes, une DMZ Web, des serveurs applicatifs, une base de données, un réseau invité Wi-Fi, des imprimantes et appareils IoT, un réseau de gestion, un VPN nomade et un petit réseau OT. Elle doit protéger les données sensibles, conserver l'accès métier et réduire les mouvements latéraux.

### Correction détaillée

**Étape 1 — Inventorier et classer.** Documente les actifs, propriétaires, données, criticité, versions et dépendances. Identifie les comptes et appareils administratifs, les services partagés, les systèmes de sauvegarde et les actifs OT.

**Étape 2 — Définir les zones.** Crée des segments cohérents pour utilisateurs, invités, IoT/imprimantes, DMZ, application, données, gestion, VPN et OT, selon la taille et les besoins réels. Documente l'adressage et les points de routage.

**Étape 3 — Construire la matrice.** Liste source, destination, application/service, justification, propriétaire, action et journaux. Vérifie les dépendances DNS, identité, NTP, mises à jour, supervision et sauvegarde au lieu de les ouvrir de façon générale.

**Étape 4 — Définir les contrôles.** Utilise VLAN et routage pour la structure, ACL/pare-feu pour contrôler les flux inter-zones, pare-feu hôte ou microsegmentation pour les actifs sensibles, NAC pour l'accès réseau lorsque disponible, et journaux centralisés pour surveiller les décisions.

**Étape 5 — Protéger l'administration.** Réserve le plan de gestion aux postes et identités approuvés, utilise MFA et un bastion lorsque possible, et conserve un accès de secours protégé. Les utilisateurs ordinaires et les invités ne doivent pas joindre directement les interfaces d'administration.

**Étape 6 — Traiter Cloud, IPv6 et OT.** Vérifie les routes et politiques de chaque famille d'adresses, les chemins de peering Cloud et les communications OT. Ne suppose pas que les contrôles IPv4 s'appliquent automatiquement à IPv6 ou qu'un VLAN OT peut être modifié sans risque opérationnel.

**Étape 7 — Tester les flux positifs et négatifs.** Vérifie le portail métier, DNS et identité, les accès d'administration autorisés, le refus invité-vers-LAN, le refus DMZ-vers-postes et les flux serveur non nécessaires. Observe les journaux et les compteurs.

**Étape 8 — Déployer et réviser.** Commence en observation ou par pilote, sauvegarde les configurations, prépare le rollback et applique progressivement. Mets à jour l'inventaire et la matrice après les changements. Revois les exceptions, les règles inutilisées et les dérives périodiquement.

Le défi est réussi lorsque les groupes d'actifs et leurs frontières sont documentés, chaque flux nécessaire a une justification, les chemins interdits échouent comme prévu et les journaux permettent de prouver la décision.

## 26. Checklist de validation

- Les actifs, propriétaires, criticités et dépendances sont documentés.
- Les zones ont des fonctions et politiques explicites.
- Les VLAN ne sont pas confondus avec une autorisation de routage.
- Les ACL, pare-feu et routes sont vérifiés de bout en bout.
- La matrice comprend DNS, identité, NTP, mises à jour et sauvegardes.
- Les invités, IoT, imprimantes et appareils inconnus sont isolés selon le besoin.
- La DMZ ne dispose pas d'un accès général au LAN.
- Les interfaces d'administration sont réservées aux sources approuvées.
- IPv4 et IPv6 ont une politique cohérente.
- Les flux Cloud et les connexions hybrides sont contrôlés.
- Les exceptions ont un propriétaire, un motif et une date de revue.
- Les flux autorisés et refusés ont été testés.
- Les journaux et compteurs sont centralisés et exploitables.
- Un rollback et un accès de secours sont disponibles.
- Les changements font l'objet d'une revue périodique.

## 27. Glossaire

**Segmentation réseau :** séparation d'actifs en groupes avec des chemins et autorisations contrôlés.

**VLAN :** domaine de diffusion logique au niveau 2.

**Sous-réseau :** plage d'adresses IP utilisée pour l'adressage et le routage.

**Zone de sécurité :** ensemble d'interfaces ou réseaux partageant un modèle de politique.

**Microsegmentation :** contrôle d'accès très granulaire entre hôtes, services ou charges de travail.

**DMZ :** zone séparée destinée notamment à des services exposés ou de médiation.

**ACL :** liste de règles qui autorisent ou refusent des paquets selon les critères pris en charge.

**NAC :** contrôle d'accès réseau fondé sur l'identité, la conformité ou le type de terminal.

**802.1X :** contrôle d'accès au port fondé sur l'authentification.

**Lateral movement :** déplacements d'un attaquant d'un système vers d'autres ressources après un accès initial.

**Zero Trust :** approche qui n'accorde pas une confiance implicite uniquement à cause de la localisation réseau ou de la propriété d'un appareil.

**Plan de gestion :** interfaces et services permettant d'administrer les équipements.

**Quarantaine :** zone à droits restreints pour un appareil inconnu ou non conforme.

**Matrice de flux :** tableau des communications nécessaires, des décisions de politique et de leurs justifications.

**Dérive de configuration :** différence entre la configuration réellement déployée et l'état approuvé.

## 28. Références officielles

- NIST SP 800-207, Zero Trust Architecture : https://csrc.nist.gov/pubs/sp/800/207/final. Le document explique pourquoi la confiance ne doit pas être accordée uniquement en fonction de l'emplacement réseau ou de la propriété de l'appareil.
- NIST SP 800-82 Rev. 3, Guide to Operational Technology (OT) Security : https://csrc.nist.gov/pubs/sp/800/82/r3/final. Il couvre la segmentation, l'isolation et les contraintes de sécurité et de disponibilité propres à l'OT.
- CISA, Enhanced Visibility and Hardening Guidance for Communications Infrastructure : https://www.cisa.gov/resources-tools/resources/enhanced-visibility-and-hardening-guidance-communications-infrastructure. La recommandation soutient une segmentation forte et le contrôle des flux entre groupes d'appareils.
- Cisco, Cloud Campus LAN Design Guide : https://www.cisco.com/c/en/us/solutions/collateral/enterprise/design-zone-campus/cloud-campus-lan-design-guide.html. Le guide fournit des exemples de conception de segments, VLAN et sous-réseaux pour des réseaux de campus.

Ces références donnent des principes et exemples de conception. Les mécanismes exacts et la terminologie diffèrent selon les fabricants, les versions et les environnements. Avant le déploiement, consulte la documentation correspondant au matériel et à la plateforme utilisés, puis teste les chemins réels, les flux autorisés et les refus attendus.

Fin du cours.

## 29. Cas de dépannage — 30 situations supplémentaires

### Cas de dépannage 1 — Les VLAN existent mais chaque poste peut joindre les serveurs

**Analyse.** Le routage inter-VLAN est probablement permissif ou une autre route contourne les règles attendues. Trace le chemin source-destination, identifie le point L3 et la règle appliquée, puis teste les flux dans les deux sens. Ajoute une politique explicite si le besoin est confirmé. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne considère pas la création d'un VLAN comme la preuve qu'un flux est refusé. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 2 — Les invités atteignent les imprimantes internes

**Analyse.** Une règle inter-zone, un peering ou un chemin secondaire peut autoriser l'accès. Vérifie les routes et politiques IPv4/IPv6, l'isolation Wi-Fi et les règles réellement appliquées. Si l'impression invité est requise, expose un service intermédiaire ou une destination précisément limitée. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne donne pas au VLAN invité accès à tout le sous-réseau des imprimantes. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 3 — Une application métier cesse de fonctionner après segmentation

**Analyse.** Une dépendance légitime comme DNS, identité, mise à jour, base de données ou NTP peut avoir été omise. Collecte le flux exact avec source, destination et service, examine les logs et la matrice, puis valide avec le propriétaire applicatif. Ajoute uniquement le flux nécessaire. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne remplace pas la règle de refus par une autorisation any-any. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 4 — Les utilisateurs peuvent accéder au plan de gestion

**Analyse.** L'interface d'administration peut être exposée dans une zone trop large ou avoir des règles de source permissives. Isole les interfaces, limite les sources au poste ou bastion approuvé et vérifie MFA, logs et accès de secours. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne coupe pas l'accès existant avant d'avoir validé un chemin de secours. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 5 — Le serveur Web de la DMZ peut initier des connexions vers tout le LAN

**Analyse.** La politique de sortie DMZ est trop permissive ou ne distingue pas les destinations. Cartographie les dépendances Web/backend, autorise seulement les destinations et ports nécessaires et vérifie les flux refusés vers utilisateurs et gestion. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne traite pas tous les serveurs de la DMZ comme des hôtes de confiance. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 6 — Les règles semblent correctes mais le trafic les contourne

**Analyse.** Une route alternative, une passerelle secondaire ou un chemin IPv6 peut contourner le point de contrôle. Compare le schéma réel au chemin observé, vérifie les routes, trunks, liens de secours et politiques IPv6, puis teste depuis plusieurs sources représentatives. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne suppose pas que le trafic traverse toujours le pare-feu central. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 7 — Une règle temporaire reste active depuis plusieurs mois

**Analyse.** Le processus de cycle de vie n'a pas de propriétaire ou de date de révision efficace. Examine les compteurs sur une durée représentative, confirme le besoin, supprime ou formalise la règle et teste les services concernés. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne conserve pas une ouverture seulement parce qu'elle a évité un incident autrefois. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 8 — Une adresse IP a été réattribuée mais garde les anciens droits

**Analyse.** La politique dépend d'un mappage IP statique périmé ou d'une identité mal actualisée. Vérifie l'inventaire, DHCP/IPAM, l'identité de l'appareil et l'attachement de règle. Privilégie les critères fiables et actualisés lorsqu'ils sont disponibles. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne considère pas qu'une adresse IP identifie définitivement un utilisateur ou un appareil. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 9 — Un poste invité accède au réseau interne en IPv6

**Analyse.** La politique a été conçue uniquement en IPv4 alors qu'IPv6 est actif. Inventorie IPv6, les routes et les ACL des passerelles, puis teste la connectivité invitée vers les destinations internes et ajuste la politique. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne suppose pas que les règles IPv4 s'appliquent automatiquement à IPv6. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 10 — Une nouvelle VNet/VPC Cloud obtient trop de connectivité

**Analyse.** Les routes, peering, groupes de sécurité ou règles de pare-feu ont pu ouvrir des chemins non prévus. Examine les tables de routage, accès publics, endpoints, règles entrantes/sortantes et identités de service. Valide le flux réel après modification. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne considère pas une séparation de sous-réseaux Cloud comme une isolation garantie. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 11 — Le bastion est accessible depuis tous les utilisateurs

**Analyse.** Le réseau de gestion ou la politique d'identité est trop large. Limite l'accès au bastion aux appareils, identités et facteurs approuvés, puis restreins les destinations derrière le bastion. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne confonds pas l'accès au bastion avec un droit d'administrer tous les systèmes. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 12 — Un outil de sauvegarde est bloqué après un changement

**Analyse.** Le job peut utiliser une destination, un port ou une fenêtre qui n'était pas dans la matrice. Consulte l'historique, le propriétaire, les routes et les logs ; valide le flux nécessaire et reteste la restauration ou une tâche témoin. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne permets pas au serveur de sauvegarde d'atteindre tous les systèmes sur tous les ports sans analyse. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 13 — Les services de découverte ne fonctionnent plus entre VLAN

**Analyse.** Certains mécanismes reposent sur la diffusion ou le multicast, qui ne traverse pas automatiquement les frontières L3. Identifie le protocole et l'usage, puis choisis un relais ou une découverte centralisée supportée si nécessaire. Limite le périmètre de l'exception. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne mets pas tous les appareils dans un seul VLAN uniquement pour restaurer une découverte automatique. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 14 — Une règle de pare-feu ne semble jamais utilisée

**Analyse.** Le flux peut être absent, le point de collecte trop court ou une autre règle peut correspondre en premier. Examine compteurs, logs, ordre et périodes de maintenance, puis confirme auprès du propriétaire avant suppression. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne supprime pas une règle basée uniquement sur l'absence de trafic pendant une courte fenêtre. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 15 — Les postes d'administration sont utilisés pour la navigation quotidienne

**Analyse.** Le poste privilégié est davantage exposé aux pièces jointes, sites et logiciels non nécessaires. Sépare les usages, protège le poste, limite les destinations et impose MFA/contrôles adaptés aux privilèges. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne donne pas une confiance implicite à un poste parce qu'il appartient à l'équipe IT. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 16 — Un appareil IoT n'a pas de supplicant 802.1X

**Analyse.** Le terminal peut nécessiter une méthode d'identification alternative avec droits limités. Classe l'appareil, utilise MAB ou une exception compatible seulement si approuvée, et place-le dans une zone restreinte aux services nécessaires. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne transforme pas l'échec 802.1X en accès total au réseau. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 17 — Les flux autorisés fonctionnent mais les tests de refus réussissent aussi

**Analyse.** Une règle d'autorisation peut être trop large ou un autre chemin peut contourner la politique. Teste les compteurs et la règle réellement appliquée, examine les routes et le filtrage hôte puis resserre les critères. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne considère pas le succès des seuls tests positifs comme validation complète. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 18 — L'accès fournisseur est maintenu après la fin de l'intervention

**Analyse.** Le compte, la route ou l'exception temporaire n'a pas été retiré. Vérifie l'accord, ferme la fenêtre, révoque les comptes/jetons, retire les règles et examine les journaux de la période. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne maintiens pas un chemin d'accès fournisseur permanent sans propriétaire et justification. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 19 — Le réseau OT devient inaccessible après une nouvelle ACL

**Analyse.** La règle peut avoir bloqué un protocole de contrôle ou une dépendance indispensable. Coordonne l'analyse avec l'équipe OT, utilise le rollback préparé et examine les logs avant de corriger en laboratoire ou en fenêtre approuvée. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne teste pas de modifications au hasard sur les automates en production. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 20 — Une segmentation par groupe Cloud ne s'applique pas à une charge nouvellement créée

**Analyse.** Le tag, rôle, groupe ou automatisation d'enrôlement n'a pas été appliqué ou a changé. Vérifie le pipeline de déploiement, l'identité de la charge, les politiques associées et les journaux Cloud. Teste l'état final avant de publier le service. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne présume pas que toute nouvelle ressource hérite correctement des contrôles. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 21 — Un serveur compromis peut scanner les autres serveurs de la même zone

**Analyse.** La zone est trop large ou l'accès latéral n'est pas contrôlé à granularité suffisante. Identifie les communications nécessaires, puis évalue un pare-feu hôte ou une microsegmentation avec tests d'application. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne crée pas de microsegmentation sans inventaire et responsable de chaque règle. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 22 — Le réseau invité reçoit une adresse interne mais atteint quand même le LAN

**Analyse.** L'adressage n'est qu'une partie de la politique ; une route et une règle peuvent autoriser l'accès. Vérifie l'isolation L2, la passerelle, les règles inter-zones et le chemin IPv6. Teste des cibles privées connues qui doivent être refusées. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne confonds pas une plage d'adresses réservée aux invités avec une politique de sécurité. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 23 — Un nouveau VLAN a été ajouté sans mise à jour de supervision

**Analyse.** Le réseau peut être fonctionnel mais absent du monitoring et des contrôles de dérive. Ajoute le segment dans l'inventaire, les journaux, la supervision et les tests, puis vérifie la couverture des capteurs. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne considère pas l'absence d'alerte comme rassurante pour un segment qui n'est pas surveillé. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 24 — Le trafic retour est bloqué malgré une règle autorisée

**Analyse.** L'état de session, la route retour ou un filtrage asymétrique peut être incohérent. Examine les routes aller/retour, les sessions stateful, NAT et les compteurs aux points de contrôle. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne remplace pas une politique stateful par une ouverture générale dans les deux sens. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 25 — Des règles dupliquées divergent entre équipements

**Analyse.** La politique peut avoir été copiée manuellement et ne plus être cohérente. Compare les règles et objets, définis la source de vérité, déploie via processus contrôlé et teste les chemins sur chaque équipement. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne laisse pas des copies manuelles sans version ni propriétaire. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 26 — Une exception de microsegmentation bloque un déploiement applicatif

**Analyse.** Le déploiement peut introduire une nouvelle dépendance ou une identité de workload inattendue. Analyse les événements, valide le flux auprès du propriétaire et ajuste la politique pour les rôles nécessaires, puis ajoute un test automatisé si possible. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne passe pas tous les workloads en mode permissif pour accélérer le déploiement. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 27 — La politique est cohérente mais les journaux manquent

**Analyse.** La journalisation peut être désactivée, la collecte indisponible ou les champs filtrés. Vérifie le système de collecte, l'heure, les destinations log et un flux de test ; assure-toi que les refus critiques sont enregistrés. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne valide pas un contrôle dont les décisions ne peuvent pas être auditées lorsque les logs sont requis. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 28 — Une VM migre et perd sa politique réseau

**Analyse.** La politique peut dépendre d'un port physique, d'une adresse ou d'un attachement qui ne suit pas le workload. Vérifie les groupes de sécurité, tags, vSwitch, VLAN, identités et mécanismes de migration. Teste la politique après déplacement. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne suppose pas que le réseau virtuel conserve automatiquement tous les contrôles. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 29 — Le réseau est segmenté mais un compte compromis accède à plusieurs ressources

**Analyse.** La segmentation réduit certains chemins, mais le compte peut avoir des droits applicatifs ou d'identité trop larges. Examine les permissions, sessions, MFA, accès par rôle et l'étendue des droits. Combine segmentation avec moindre privilège et réponse à incident. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne présente pas la segmentation réseau comme un substitut aux contrôles d'identité. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

### Cas de dépannage 30 — La règle inter-zone autorise le port attendu mais pas le protocole applicatif

**Analyse.** Le service peut dépendre de plusieurs flux, d'un DNS, d'un service d'identité ou de retours différents. Capture le flux autorisé, identifie les dépendances et confirme les ports auprès du propriétaire. Ajoute une règle limitée puis reteste les refus. Note les adresses, les zones, les routes, le protocole, les identifiants de règle et les changements récents. Compare la configuration déployée à la matrice approuvée avant de modifier quoi que ce soit.

**Erreur à éviter.** Ne permets pas tous les ports simplement parce que le protocole principal a été identifié. Après correction, vérifie un flux autorisé, un flux interdit et les journaux correspondants. Actualise l'inventaire, la matrice et la procédure de retour arrière si nécessaire.

## 30. Défi final — architecturer la segmentation d'une entreprise

### Contexte

Une entreprise possède des utilisateurs internes, une DMZ Web, des serveurs applicatifs, une base de données, un réseau invité Wi-Fi, des imprimantes et appareils IoT, un réseau de gestion, un VPN nomade et un petit réseau OT. Elle doit protéger les données sensibles, conserver l'accès métier et réduire les mouvements latéraux.

### Correction détaillée

**Étape 1 — Inventorier et classer.** Documente les actifs, propriétaires, données, criticité, versions et dépendances. Identifie les comptes et appareils administratifs, les services partagés, les systèmes de sauvegarde et les actifs OT.

**Étape 2 — Définir les zones.** Crée des segments cohérents pour utilisateurs, invités, IoT/imprimantes, DMZ, application, données, gestion, VPN et OT, selon la taille et les besoins réels. Documente l'adressage et les points de routage.

**Étape 3 — Construire la matrice.** Liste source, destination, application/service, justification, propriétaire, action et journaux. Vérifie les dépendances DNS, identité, NTP, mises à jour, supervision et sauvegarde au lieu de les ouvrir de façon générale.

**Étape 4 — Définir les contrôles.** Utilise VLAN et routage pour la structure, ACL/pare-feu pour contrôler les flux inter-zones, pare-feu hôte ou microsegmentation pour les actifs sensibles, NAC pour l'accès réseau lorsque disponible, et journaux centralisés pour surveiller les décisions.

**Étape 5 — Protéger l'administration.** Réserve le plan de gestion aux postes et identités approuvés, utilise MFA et un bastion lorsque possible, et conserve un accès de secours protégé. Les utilisateurs ordinaires et les invités ne doivent pas joindre directement les interfaces d'administration.

**Étape 6 — Traiter Cloud, IPv6 et OT.** Vérifie les routes et politiques de chaque famille d'adresses, les chemins de peering Cloud et les communications OT. Ne suppose pas que les contrôles IPv4 s'appliquent automatiquement à IPv6 ou qu'un VLAN OT peut être modifié sans risque opérationnel.

**Étape 7 — Tester les flux positifs et négatifs.** Vérifie le portail métier, DNS et identité, les accès d'administration autorisés, le refus invité-vers-LAN, le refus DMZ-vers-postes et les flux serveur non nécessaires. Observe les journaux et les compteurs.

**Étape 8 — Déployer et réviser.** Commence en observation ou par pilote, sauvegarde les configurations, prépare le rollback et applique progressivement. Mets à jour l'inventaire et la matrice après les changements. Revois les exceptions, les règles inutilisées et les dérives périodiquement.

Le défi est réussi lorsque les groupes d'actifs et leurs frontières sont documentés, chaque flux nécessaire a une justification, les chemins interdits échouent comme prévu et les journaux permettent de prouver la décision.

## 31. Checklist de validation

- Les actifs, propriétaires, criticités et dépendances sont documentés.
- Les zones ont des fonctions et politiques explicites.
- Les VLAN ne sont pas confondus avec une autorisation de routage.
- Les ACL, pare-feu et routes sont vérifiés de bout en bout.
- La matrice comprend DNS, identité, NTP, mises à jour et sauvegardes.
- Les invités, IoT, imprimantes et appareils inconnus sont isolés selon le besoin.
- La DMZ ne dispose pas d'un accès général au LAN.
- Les interfaces d'administration sont réservées aux sources approuvées.
- IPv4 et IPv6 ont une politique cohérente.
- Les flux Cloud et les connexions hybrides sont contrôlés.
- Les exceptions ont un propriétaire, un motif et une date de revue.
- Les flux autorisés et refusés ont été testés.
- Les journaux et compteurs sont centralisés et exploitables.
- Un rollback et un accès de secours sont disponibles.
- Les changements font l'objet d'une revue périodique.

## 32. Glossaire

**Segmentation réseau :** séparation d'actifs en groupes avec des chemins et autorisations contrôlés.

**VLAN :** domaine de diffusion logique au niveau 2.

**Sous-réseau :** plage d'adresses IP utilisée pour l'adressage et le routage.

**Zone de sécurité :** ensemble d'interfaces ou réseaux partageant un modèle de politique.

**Microsegmentation :** contrôle d'accès granulaire entre hôtes, services ou charges de travail.

**DMZ :** zone séparée destinée notamment à des services exposés ou de médiation.

**ACL :** liste de règles qui autorisent ou refusent des paquets selon les critères pris en charge.

**NAC :** contrôle d'accès réseau fondé sur l'identité, la conformité ou le type de terminal.

**802.1X :** contrôle d'accès au port fondé sur l'authentification.

**Lateral movement :** déplacement d'un attaquant d'un système vers d'autres ressources après un accès initial.

**Zero Trust :** approche qui n'accorde pas une confiance implicite uniquement à cause de la localisation réseau ou de la propriété d'un appareil.

**Plan de gestion :** interfaces et services permettant d'administrer les équipements.

**Quarantaine :** zone à droits restreints pour un appareil inconnu ou non conforme.

**Matrice de flux :** tableau des communications nécessaires, des décisions de politique et de leurs justifications.

**Dérive de configuration :** différence entre la configuration réellement déployée et l'état approuvé.

## 33. Références officielles

- NIST SP 800-207, Zero Trust Architecture : https://csrc.nist.gov/pubs/sp/800/207/final. Il explique pourquoi la confiance ne doit pas dépendre uniquement de l'emplacement réseau ou de la propriété de l'appareil.
- NIST SP 800-82 Rev. 3, Guide to Operational Technology (OT) Security : https://csrc.nist.gov/pubs/sp/800/82/r3/final. Il couvre la segmentation et l'isolation en tenant compte des exigences OT.
- CISA, Enhanced Visibility and Hardening Guidance for Communications Infrastructure : https://www.cisa.gov/resources-tools/resources/enhanced-visibility-and-hardening-guidance-communications-infrastructure. Il recommande une segmentation forte et le contrôle des flux entre groupes d'appareils.
- Cisco, Cloud Campus LAN Design Guide : https://www.cisco.com/c/en/us/solutions/collateral/enterprise/design-zone-campus/cloud-campus-lan-design-guide.html. Il contient des exemples de conception de segments, VLAN et sous-réseaux.

Ces références donnent des principes et exemples de conception. Les mécanismes exacts diffèrent selon les fabricants, les versions et les environnements. Avant le déploiement, consulte la documentation correspondant au matériel et à la plateforme utilisés, puis teste les chemins réels, les flux autorisés et les refus attendus.

Fin du cours.