# ACL et filtrage avancé

> **Mise en contexte**
>
> Un routeur ou un pare-feu relie plusieurs réseaux tout en pouvant limiter les communications entre eux. Une ACL (*Access Control List*, liste de contrôle d'accès) décrit des critères de trafic et une décision : autoriser certains clients à joindre un serveur HTTPS, refuser l'accès d'un poste précis à un serveur sensible ou limiter les sources capables d'administrer un équipement. Une ACL mal écrite peut laisser passer un trafic qui devrait être bloqué, interrompre un service légitime ou donner une fausse impression de sécurité.
>
> Ce cours approfondit les ACL IPv4 sur les équipements de type Cisco IOS, les masques génériques, les ACL standard et étendues, les entrées nommées, l'ordre de traitement, les directions d'application, la restriction de l'administration, les différences avec les pare-feu à états, la vérification et le dépannage. Les commandes sont destinées à un laboratoire ou à un équipement que tu es autorisé à administrer. Ne copie pas une configuration dans un réseau de production sans analyse, sauvegarde et plan de retour arrière.

## 1. Objectifs pédagogiques et prérequis

À la fin du cours, tu dois être capable d'expliquer le rôle d'une ACL, distinguer une ACL standard d'une ACL étendue, calculer un wildcard à partir d'un masque réseau, interpréter les mots-clés host et any, comprendre eq et range, appliquer le principe de première correspondance, tenir compte du refus implicite, choisir une interface et une direction, écrire une liste numérotée ou nommée, limiter la gestion distante, diagnostiquer une règle inefficace et tester les flux permis comme les flux refusés.

Les prérequis sont les adresses IPv4, les sous-réseaux, TCP, UDP, ICMP, le routage et la lecture d'une interface de routeur. Les exemples utilisent la syntaxe classique de Cisco IOS. Une autre marque ou une autre version du système peut employer une syntaxe ou un modèle d'évaluation différent. Il faut toujours se référer à la documentation correspondant au logiciel réellement installé.

## 2. Qu'est-ce qu'une ACL ?

Une ACL est une liste ordonnée de critères appliqués à du trafic. Selon le type de liste et la plateforme, les critères peuvent comprendre l'adresse source, l'adresse destination, le protocole, le port, la direction ou d'autres caractéristiques. Une entrée permet ou refuse le trafic qui correspond. Certaines implémentations permettent également la journalisation des correspondances.

Une ACL ne chiffre pas les communications et ne prouve pas l'identité d'un utilisateur. Elle prend une décision à partir des informations qu'elle observe. Autoriser TCP/443 vers un serveur ne prouve ni que le serveur est sain, ni que la connexion provient d'un utilisateur légitime, ni que l'application est exempte de vulnérabilités.

Une ACL peut être attachée à une interface de routeur, à une interface logique ou à des mécanismes d'administration. Le lieu où elle s'applique est aussi important que le contenu de la liste. Une ACL définie mais non attachée au chemin pertinent ne filtre pas automatiquement les paquets.

Représentation conceptuelle :

~~~text
Paquet
  |
  v
Entrée 1 : correspond ?
  | oui
  v
Appliquer permit ou deny
  |
  +-- non --> examiner l'entrée suivante
                    |
                    v
             aucune correspondance
                    |
                    v
               refus implicite
~~~

Cette logique ordonnée explique pourquoi la liste doit être lue de haut en bas, et pourquoi une autorisation trop large placée au début peut rendre des refus ultérieurs inutiles.

## 3. ACL standard et ACL étendue

**Schéma pédagogique — Les ACL standard sont généralement centrées sur la source ; les ACL étendues peuvent matcher plus de champs.**

~~~text
Paquet = source + destination + protocole + ports
                |
       +--------+---------+
       |                  |
       v                  v
[ACL standard]       [ACL etendue]
Source principalement Source/destination/protocole/ports

Les capacités et leur ordre d'évaluation varient selon la plateforme.
~~~


### 3.1. ACL standard

Une ACL IPv4 standard classique sélectionne principalement l'adresse IP source. Elle ne sélectionne pas directement un port de destination. Elle est adaptée à des cas où l'origine est le critère principal, par exemple limiter les sources autorisées à utiliser une fonction d'administration.

Exemple conceptuel : autoriser le réseau d'administration 192.168.40.0/24 et refuser les autres sources pour l'accès à une ligne VTY. Cette décision ne distingue pas, à elle seule, SSH d'HTTPS, ni un serveur Web d'un serveur de fichiers.

Les plages classiques d'ACL standard numérotées de Cisco IOS comprennent historiquement 1–99 et 1300–1999, selon les versions et la famille de produits. La syntaxe et les numéros disponibles doivent être confirmés dans le système cible.

### 3.2. ACL étendue

Une ACL étendue peut sélectionner la source, la destination, le protocole et, pour TCP/UDP, les ports. Elle est adaptée aux politiques plus fines, par exemple refuser uniquement TCP/22 d'un réseau utilisateur vers un serveur d'administration tout en laissant d'autres services autorisés.

Les plages classiques d'ACL étendues numérotées Cisco IOS comprennent notamment 100–199 et 2000–2699, selon la version. Une ACL étendue peut aussi être nommée, ce qui rend la configuration plus lisible.

| Propriété | ACL standard classique | ACL étendue classique |
|---|---|---|
| Adresse source | Oui | Oui |
| Adresse destination | Non, dans le modèle standard classique | Oui |
| Protocole IP | Pas de sélection fine dans le modèle standard | Oui |
| Port TCP/UDP | Non | Oui |
| Usage typique | Contrôle fondé principalement sur la source | Contrôle précis source-destination-service |

Le mot « étendue » ne garantit pas une meilleure sécurité. Une ACL étendue avec un permit général prématuré est aussi problématique qu'une ACL standard mal placée. Le choix dépend du besoin réel.

## 4. Ordre d'évaluation et refus implicite

**Schéma pédagogique — Avec une évaluation première correspondance, la règle atteinte en premier prend la décision.**

~~~text
Paquet
  |
  v
[permit source admin vers SSH ?] -- oui --> PERMIT
  | non
  v
[deny source X vers serveur ?] --- oui --> DENY
  | non
  v
[permit HTTPS vers service ?] ---- oui --> PERMIT
  | non
  v
[Refus implicite final]

Une règle jamais atteinte ne produit aucun effet.
~~~


Les ACL classiques sont généralement évaluées dans l'ordre. Le dispositif examine une entrée, vérifie si le trafic correspond, puis applique l'action. Une correspondance décide du traitement du paquet ; les entrées suivantes ne viennent pas annuler cette décision.

Configuration incorrecte pour bloquer un flux précis :

~~~text
access-list 100 permit ip any any
access-list 100 deny ip host 192.168.1.10 host 10.0.0.5
~~~

La première ligne autorise tout le trafic IPv4 correspondant. Le flux qui devait être refusé correspond déjà à cette règle. Le refus plus bas ne vient donc pas annuler l'autorisation.

Ordre logique pour l'objectif du laboratoire :

~~~text
access-list 100 deny ip host 192.168.1.10 host 10.0.0.5
access-list 100 permit ip any any
~~~

Le refus spécifique est évalué avant l'autorisation plus générale. Cette deuxième ligne est requise par le scénario pédagogique qui veut bloquer un seul flux tout en autorisant le reste. Ne la recopie pas automatiquement dans un réseau de production.

### 4.1. Le refus implicite final

Les ACL IPv4 classiques Cisco se terminent normalement par un refus implicite. Si aucune entrée ne correspond, le paquet est refusé. Une liste qui contient uniquement un permit précis ne signifie pas que tous les autres flux sont autorisés.

Exemple :

~~~text
access-list 110 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
~~~

La ligne permet le trafic TCP indiqué vers le serveur Web. Les autres paquets qui rencontrent cette ACL et ne correspondent pas à cette entrée peuvent être refusés par le refus implicite. Avant d'attacher cette liste à une interface, identifie donc tous les flux légitimes qui traversent l'interface dans cette direction : DNS, DHCP dans certaines architectures, administration, applications métier ou autres dépendances.

### 4.2. Pourquoi une règle générale est risquée

La règle « permit ip any any » autorise un ensemble très large de communications IP. Dans le laboratoire, elle isole l'effet d'un refus précis. En production, une autorisation générale peut annuler une segmentation, rendre atteignables des services d'administration et contredire les règles de moindre privilège.

Pour une politique professionnelle restrictive, inventorie les flux requis, permets-les explicitement puis laisse le refus implicite traiter le reste. Pour une politique plus permissive, documente son objectif, son périmètre, son propriétaire et le risque. Il doit être possible d'expliquer pourquoi la règle existe et comment elle sera revue.

## 5. Adresses, host, any et wildcard

**Schéma pédagogique — Le wildcard indique quels bits d'une adresse sont ignorés lors de la comparaison.**

~~~text
Masque reseau /24 : 255.255.255.0
Wildcard             :   0.  0.  0.255

Prefixe               : 192.0.2.0
Plage visee           : 192.0.2.0/24

host 192.0.2.10 = une seule adresse.
any = toutes les adresses dans le champ concerne.
Verifier toujours le sens du wildcard.
~~~


### 5.1. Adresses exactes et toutes les sources

Dans la syntaxe Cisco IOS classique, le mot-clé host suivi d'une adresse correspond à un seul hôte IPv4. Le mot-clé any correspond à toutes les adresses dans le champ concerné.

Exemple :

~~~text
deny ip host 192.168.1.10 host 10.0.0.5
~~~

Cette entrée vise des paquets IP dont la source est 192.168.1.10 et la destination 10.0.0.5.

Autre exemple :

~~~text
permit tcp any host 10.0.0.5 eq 443
~~~

Cette entrée permet TCP à destination du port 443 de cet hôte, depuis toute source. Une telle source universelle est large : si seuls les postes de l'organisation doivent accéder au serveur, spécifie le sous-réseau autorisé.

### 5.2. Calcul d'un wildcard

Le wildcard, ou masque générique, indique quels bits d'une adresse doivent correspondre et quels bits peuvent varier dans la syntaxe ACL Cisco classique. Il est souvent calculé en inversant chaque octet du masque de sous-réseau.

- Un bit à 0 dans le wildcard doit correspondre au bit de l'adresse fournie.
- Un bit à 1 dans le wildcard est ignoré pour la correspondance.

Pour le réseau 192.168.10.0/24, le masque réseau est 255.255.255.0 et le wildcard conventionnel est 0.0.0.255. Ce wildcard cible l'ensemble du dernier octet. Pour un /26, le masque est 255.255.255.192 et le wildcard est 0.0.0.63. Un bloc /26 aligné comme 192.168.10.64/26 contient les adresses de 192.168.10.64 à 192.168.10.127.

~~~text
Masque réseau : 255.255.255.0
Wildcard      :   0.  0.  0.255
Réseau        : 192.168.10.0/24
Plage ciblée  : 192.168.10.0 à 192.168.10.255
~~~

Ne copie pas un masque de sous-réseau à la place du wildcard. Pour un /24, un masque finissant par 0 n'est pas équivalent au wildcard finissant par 255. Vérifie également l'adresse réseau et les limites du bloc : une combinaison incohérente peut correspondre à une plage inattendue.

Pour une adresse unique, host est plus lisible qu'un wildcard composé de zéros. Pour toutes les sources, any est plus clair qu'un masque qui exprime la même intention. La clarté aide à la revue et limite les erreurs.

## 6. Ports, opérateurs et protocoles

Une ACL étendue Cisco IOS classique peut spécifier un port TCP/UDP. L'opérateur eq signifie « égal à », range désigne une plage, gt signifie supérieur à, lt inférieur à et neq différent de. La syntaxe exacte, les noms de services acceptés et la disposition des champs varient selon le système : consulte l'aide intégrée et la documentation de la version.

Exemple HTTPS :

~~~text
permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
~~~

Exemple HTTP :

~~~text
permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 80
~~~

Ces lignes sélectionnent TCP. Elles n'autorisent pas tous les protocoles vers le serveur. HTTP/3 utilise habituellement QUIC sur UDP/443, donc une règle TCP/443 seule ne décrit pas le flux UDP.

Exemple de plage illustrative :

~~~text
permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.20 range 1024 1040
~~~

Une plage ne doit pas être ouverte par simple commodité. Confirme les ports réellement nécessaires auprès du propriétaire de l'application. Si le service utilise des ports dynamiques, examine sa documentation et le modèle de filtrage disponible plutôt que d'autoriser une plage énorme de façon permanente.

DNS utilise souvent UDP/53 mais peut employer TCP/53. SSH utilise généralement TCP/22, et NTP utilise principalement UDP/123. Les numéros de ports sont des conventions, non une preuve du service réel. Vérifie la configuration et le protocole avant d'écrire les règles.

Le mot-clé IP dans une ACL étendue IPv4 classique couvre des paquets IP au-delà d'un seul service TCP. Pour cibler TCP ou UDP en particulier, indique le protocole. ICMP ne possède pas de ports TCP/UDP ; certains messages ICMP sont importants au fonctionnement et au diagnostic du réseau.

Les ACL classiques sont en général sans état. L'option TCP established sur certaines plateformes teste des indicateurs comme ACK ou RST ; elle n'est pas l'équivalent universel d'un suivi de session complet. N'utilise pas cette option comme substitut systématique à un pare-feu stateful.

## 7. Choisir l'interface et la direction

**Schéma pédagogique — La direction in/out se définit du point de vue de l'interface du routeur.**

~~~text
LAN A ---> [Interface routeur] ---> WAN
             ^ in        out ^

ACL in  : examine le paquet quand il entre par cette interface.
ACL out : examine le paquet quand il en sort.

Tracer le chemin du paquet avant de choisir le point d'attachement.
~~~


Sur un routeur, in et out sont définis du point de vue de l'interface où l'ACL est attachée :

- **in** : paquet qui entre dans le routeur par cette interface ;
- **out** : paquet qui quitte le routeur par cette interface.

Inbound ne veut donc pas toujours dire « depuis Internet ». Il faut identifier le réseau relié à l'interface.

Une règle de conception courante place une ACL étendue près de la source afin d'arrêter le trafic non nécessaire avant qu'il traverse l'infrastructure. Les ACL standard, qui examinent principalement la source, sont souvent placées près de la destination pour éviter d'affecter plus de destinations que souhaité. Ce sont des heuristiques, pas des lois absolues : la topologie, le chemin, les flux de retour et l'architecture globale doivent être considérés.

Une ACL appliquée sur la mauvaise interface ou dans la mauvaise direction peut ne jamais voir le paquet. Dessine le trajet, marque l'interface d'entrée et de sortie, puis vérifie que le flux traverse bien l'interface concernée.

## 8. Créer, attacher et vérifier une ACL

Créer une ACL dans la configuration ne signifie pas automatiquement que les paquets sont filtrés. Sur Cisco IOS, on l'attache généralement à une interface et à une direction avec ip access-group.

~~~text
R1(config)# interface FastEthernet0/0
R1(config-if)# ip access-group 100 in
~~~

Cette configuration applique l'ACL IPv4 100 au trafic qui entre dans R1 par Fa0/0. Elle ne l'applique pas à toutes les interfaces, ni à tous les trafics du routeur. Le nom d'interface doit être celui réellement présent sur le matériel ou le simulateur.

Avant d'attacher une ACL, vérifie les flux déjà permis par l'interface. Si elle transporte les demandes de plusieurs services, une liste restrictive peut en bloquer certains à cause du refus implicite. Prépare un accès de gestion de secours, surtout si la modification est faite à distance.

## 9. ACL numérotées et nommées

Les ACL numérotées utilisent un identifiant de la plage compatible avec le type de liste et la version. Elles sont simples pour des laboratoires, mais le numéro explique peu l'intention à un lecteur.

Une ACL nommée peut porter un nom comme USERS-HTTPS ou MGMT-SOURCES. Les listes nommées de Cisco IOS utilisent fréquemment des numéros de séquence qui facilitent l'insertion et la réorganisation des entrées. Les options exactes varient selon la version.

Exemple conceptuel :

~~~text
ip access-list extended USERS-WEB
 10 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 20 deny ip 192.168.10.0 0.0.0.255 192.168.40.0 0.0.0.255 log
 30 permit ip 192.168.10.0 0.0.0.255 any
~~~

La dernière entrée de cet exemple autorise le reste du trafic IP provenant du réseau utilisateurs vers n'importe quelle destination. Elle illustre l'ordre et la journalisation, mais reste large. Si l'objectif est de n'autoriser que quelques services métiers, remplace-la par les flux nécessaires et laisse le refus implicite s'appliquer au reste.

Après une modification, affiche de nouveau l'ACL. Ne supprime pas une entrée parce que son texte semble redondant avant d'avoir examiné les compteurs, l'ordre et le comportement attendu.

## 10. Restreindre le plan d'administration

Les accès SSH, Telnet, interfaces Web ou mécanismes d'administration sont particulièrement sensibles. Il est préférable de les réserver à des postes gérés ou à un sous-réseau de gestion.

Exemple Cisco IOS classique, à adapter et à tester :

~~~text
ip access-list standard MGMT-SOURCES
 permit 192.168.40.0 0.0.0.255
!
line vty 0 4
 access-class MGMT-SOURCES in
 transport input ssh
 login local
~~~

Cette configuration dépend de la version IOS, des comptes locaux et du nombre de lignes VTY. L'ACL de source autorise le réseau de gestion ; le refus implicite bloque les autres sources pour les accès VTY contrôlés par cette liste. Elle ne filtre pas à elle seule tous les paquets traversant les interfaces de données.

Préfère SSH à Telnet lorsque c'est possible, car Telnet ne protège pas correctement les identifiants en transit. Associe le filtrage à des comptes adaptés, des secrets robustes, des mises à jour et une journalisation. Teste depuis une source d'administration autorisée puis depuis une source non autorisée. Si tu es connecté depuis un réseau non inclus dans l'ACL, tu peux perdre ta session ; prépare une console ou un autre accès avant l'application.

## 11. IPv4 et IPv6

Une ACL IPv4 ne contrôle pas automatiquement IPv6. Si le système utilise les deux piles, il faut appliquer et vérifier une politique adaptée à chacune. Les structures et les commandes IPv6 diffèrent selon le fabricant et la version. Ne transpose pas une règle IPv4 en supposant qu'elle possède le même sens.

Pour IPv6, identifie les préfixes, adresses, routes, services et règles qui sont réellement utilisés. Certains messages ICMPv6 participent à des fonctions essentielles comme la découverte des voisins et la découverte de la MTU ; les bloquer sans étude peut provoquer des dysfonctionnements. La vérification doit prendre en compte les tunnels et interfaces virtuelles, qui peuvent offrir des chemins non prévus.

## 12. Journaux et compteurs

Les équipements peuvent compter les paquets correspondant à une entrée et, selon les options, journaliser des événements. Les compteurs aident à déterminer si une règle a vu le trafic attendu. Un compteur nul peut signifier que la source ne génère pas le trafic, que le chemin est différent, que les critères sont incorrects ou que les compteurs ont été réinitialisés. Un compteur positif prouve une correspondance comptabilisée, mais pas à lui seul la réussite de l'application.

La journalisation doit rester exploitable. Une règle de refus très générale avec journalisation peut produire un grand volume d'événements. Configure-la selon les besoins, limite le bruit si la plateforme le permet et protège les journaux. Interprète les événements avec l'heure, la source, la destination, le service et le contexte de changement. Un refus isolé n'est pas automatiquement une attaque.

## 13. Commandes de vérification

Dans un environnement Cisco IOS ou un simulateur compatible, les commandes de lecture utiles sont :

~~~text
show access-lists
show ip access-lists
show ip interface FastEthernet0/0
show running-config interface FastEthernet0/0
show running-config
show ip route
~~~

Les commandes show access-lists et show ip access-lists affichent les listes et peuvent montrer les compteurs. show ip interface aide à savoir si une ACL est appliquée dans une direction sur une interface. show running-config interface montre les paramètres de l'interface, et show ip route aide à vérifier la route.

Le nom exact de l'interface peut être GigabitEthernet, Ethernet ou autre selon le système. Les sorties varient selon l'IOS et le simulateur. Utilise l'aide intégrée et vérifie la version réellement déployée. Ne sauvegarde la configuration permanente qu'après validation.

## 14. Procédure de changement

Avant de modifier une ACL, clarifie le besoin et le propriétaire de l'application, recueille la topologie et la configuration, détermine les sources, destinations, protocoles, ports et directions, vérifie le refus implicite et les règles existantes, sauvegarde et prépare un retour arrière. Si tu administres à distance, garde un canal d'accès de secours.

Applique la modification dans un laboratoire ou pendant une fenêtre approuvée. Vérifie ensuite la liste, son attachement et les compteurs. Teste un flux qui doit fonctionner ainsi que les flux qui doivent échouer. Consigne la date, la raison, l'auteur, les risques, les résultats et la date de revue. Les règles temporaires doivent avoir une échéance claire.

Ne vide pas toute la configuration pour « repartir de zéro ». Un outil central peut gérer les règles et les réécrire, ou une suppression peut couper les communications nécessaires à la restauration. Identifie l'outil qui possède la politique avant toute modification.

## 15. Méthode de dépannage

1. Décris le symptôme et note source, destination, protocole, port et heure.
2. Vérifie adresse IP, masque, route et passerelle.
3. Confirme que le service est actif et à l'écoute sur la bonne adresse.
4. Examine la liste complète, son ordre et les règles d'application.
5. Vérifie l'interface et la direction avec les commandes show appropriées.
6. Recherche les compteurs et journaux qui correspondent au test.
7. Modifie un seul élément à la fois et teste les flux attendus et interdits.
8. Documente la cause et le retour arrière éventuel.

Ne diagnostique pas uniquement avec ping : ICMP et TCP sont différents. Un serveur peut répondre au ping et refuser SSH, ou ne pas répondre au ping alors que son service Web fonctionne. Utilise des tests correspondant au protocole applicatif, et combine-les avec les données des routeurs et de l'hôte.

## 16. TP guidé : bloquer l'attaquant vers le serveur

**Schéma pédagogique — Les tests doivent prouver le refus ciblé et préserver les flux légitimes.**

~~~text
[Hote attaque 192.0.2.50] ---X---> [Serveur 198.51.100.20:443]
[Poste admin 192.0.2.10] ---------> [Serveur 198.51.100.20:443]

Tests attendus:
1. source interdite + service cible : refus
2. source admin + service cible : autorise
3. autres services non demandes : conformes a la politique
4. compteurs et journaux : coherents
~~~


Le laboratoire associé à Skill-Tree contient R1, un commutateur de niveau 2, un PC Attaquant et un serveur Protégé. Fa0/0 sur R1 utilise 192.168.1.1/24 ; le PC Attaquant utilise 192.168.1.10/24. Fa0/1 sur R1 utilise 10.0.0.1/24 et le serveur utilise 10.0.0.5/24.

L'objectif du laboratoire est de créer une ACL étendue numérotée 100, de refuser le trafic IP de 192.168.1.10 vers 10.0.0.5, d'autoriser le reste selon le scénario et d'appliquer l'ACL en entrée sur Fa0/0.

~~~text
R1> enable
R1# configure terminal
R1(config)# access-list 100 deny ip host 192.168.1.10 host 10.0.0.5
R1(config)# access-list 100 permit ip any any
R1(config)# interface FastEthernet0/0
R1(config-if)# ip access-group 100 in
R1(config-if)# end
~~~

Le refus spécifique est placé avant le permit général. Comme la liste est attachée en entrée sur Fa0/0, elle examine les paquets entrant dans R1 depuis le réseau 192.168.1.0/24. La liste ne filtre pas automatiquement toutes les autres interfaces.

La commande permit ip any any correspond à l'objectif du laboratoire, mais c'est une autorisation très large. Elle sert ici à tester le blocage d'une communication spécifique tout en laissant le reste du trafic de test passer. Dans un réseau réel, la politique devrait être construite à partir des besoins légitimes, et une autorisation générale doit être justifiée.

Vérifie le résultat :

~~~text
show access-lists
show ip access-lists 100
show ip interface FastEthernet0/0
show running-config interface FastEthernet0/0
~~~

Il faut confirmer trois critères : l'entrée de refus exacte, le permit général après le refus, et l'ACL 100 appliquée en entrée sur Fa0/0. Dans Skill-Tree, le laboratoire vérifie également ces éléments dans la configuration simulée du routeur.

Depuis le PC Attaquant, tente la communication vers le serveur avec les mécanismes de test disponibles dans le laboratoire. Le flux ciblé doit être bloqué. Si le test ne correspond pas au résultat attendu, vérifie d'abord l'adresse source réelle, la destination, l'ordre des entrées, l'interface et le sens d'application. Ne change pas toute la topologie ou les adresses sans raison.

## 17. TP : autoriser un accès HTTPS précis

Supposons que les postes utilisateurs 192.168.10.0/24 doivent accéder au serveur Web 192.168.20.10 sur TCP/443. Une ACL nommée illustrative pourrait être :

~~~text
ip access-list extended USERS-HTTPS
 10 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
!
interface GigabitEthernet0/0
 ip access-group USERS-HTTPS in
~~~

Cette liste n'autorise que le flux explicitement décrit. L'ACL classique comporte un refus implicite, donc d'autres flux rencontrant la même liste peuvent être bloqués. Avant d'appliquer l'exemple, vérifie si cette interface transporte aussi des demandes de DNS, des services d'administration ou d'autres flux dont dépend la connectivité.

Si le besoin métier est uniquement HTTPS vers cette destination, la précision est utile. Si l'objectif est différent, ne conserve pas une liste minimaliste par réflexe : spécifie les services approuvés et teste leur fonctionnement. Une configuration qui bloque tout n'est pas automatiquement bonne ; elle doit répondre au besoin et rester sécurisée.

## 18. TP : protéger les lignes d'administration

Un sous-réseau d'administration est situé dans 192.168.40.0/24. Les lignes VTY du routeur ne doivent accepter que les sources autorisées. Une ACL standard nommée peut exprimer le réseau source, puis être appliquée avec access-class aux lignes VTY. Cette restriction porte sur l'accès de gestion au routeur ; elle n'est pas la même chose qu'une ACL d'interface contrôlant les paquets vers un serveur.

Avant le changement, vérifie l'adresse source de ta session, la disponibilité de la console ou d'un accès de secours, la configuration des comptes et la syntaxe correspondant à la version IOS. Une source oubliée peut perdre l'accès après l'application. Teste depuis un hôte de gestion approuvé et depuis une autre source qui doit être bloquée.

La protection du plan de gestion doit aussi inclure SSH, des identités appropriées, des secrets robustes, des mises à jour et des journaux. Le filtrage n'est qu'une couche : un poste autorisé mais compromis peut toujours représenter un risque.

## 19. Checklist de revue

Avant d'approuver une ACL, vérifie que :
- le besoin et le propriétaire de la règle sont connus ;
- source, destination, protocole et port correspondent au besoin ;
- le wildcard sélectionne la bonne plage ;
- l'ordre des entrées correspond à la priorité voulue ;
- le refus implicite et les autorisations générales ont été évalués ;
- la liste est attachée à la bonne interface et dans le bon sens ;
- le trafic passe bien par cette interface ;
- les flux de dépendance et le trafic de retour sont compris ;
- IPv6 est traité s'il est utilisé ;
- les compteurs et les journaux correspondent aux tests ;
- la règle n'est pas plus large que nécessaire ;
- une sauvegarde et un retour arrière sont disponibles ;
- la règle possède un responsable et une date de révision.

La checklist n'est pas une formalité. Elle structure l'analyse et évite les erreurs les plus courantes lors d'un changement pressé. Une règle doit rester explicable par une personne autre que son auteur.

## 20. Exercices corrigés

### Exercice 1 — Interpréter host

Que signifie host 192.168.1.10 dans une ACL Cisco IOS classique ?

**Correction :** il correspond à cette adresse unique dans le champ source ou destination où il apparaît. Il ne représente pas tout le réseau 192.168.1.0/24.

### Exercice 2 — Calculer le wildcard d'un /24

Quel wildcard correspond au masque 255.255.255.0 ?

**Correction :** 0.0.0.255. Les octets sont inversés : 255 devient 0, 0 devient 255. Confonds pas wildcard et masque de sous-réseau.

### Exercice 3 — Le reste du trafic est-il permis ?

Une ACL contient uniquement un permit TCP depuis 192.168.10.0/24 vers le serveur 192.168.20.10 sur le port 443. Le reste est-il autorisé ?

**Correction :** non. Le refus implicite final bloque les paquets qui ne correspondent à aucune entrée autorisante. Avant application, il faut inventorier les autres flux nécessaires.

### Exercice 4 — Pourquoi le refus n'agit-il pas ?

Une autorisation ip any any se trouve avant un deny visant un seul hôte.

**Correction :** le trafic correspond d'abord à l'autorisation générale. Place le refus spécifique avant la règle plus large, puis vérifie l'ordre réel et les compteurs.

### Exercice 5 — Que signifie in ?

**Correction :** le paquet entre dans le routeur par l'interface concernée. Cela ne veut pas nécessairement dire qu'il arrive d'Internet ; le réseau branché sur cette interface détermine le sens.

### Exercice 6 — ACL définie mais inactive

**Correction :** vérifie si elle est appliquée à une interface au moyen de ip access-group dans le sens approprié. Examine show ip interface et la configuration de l'interface.

### Exercice 7 — Bloquer seulement SSH vers un serveur

**Correction :** une ACL étendue est adaptée parce qu'elle permet de préciser source, destination, TCP et le port 22. Une ACL standard classique ne permet pas cette granularité de port.

### Exercice 8 — Le flux reste fonctionnel après l'ajout d'un refus

**Correction :** vérifie ordre, adresse source et destination, wildcard, protocole, interface, direction et chemin réel. Les compteurs aident à déterminer si le paquet rencontre la règle.

### Exercice 9 — Pourquoi le permit ip any any du labo est-il risqué en production ?

**Correction :** il autorise très largement le trafic IP et peut neutraliser la segmentation ou des refus attendus. Il doit rester limité à l'objectif pédagogique ou être explicitement justifié dans un contexte précis.

### Exercice 10 — ACL IPv4, mais IPv6 actif

**Correction :** une ACL IPv4 ne contrôle pas automatiquement IPv6. Il faut inventorier les interfaces et services IPv6, vérifier les règles dédiées et tester les flux dans les deux piles si les deux sont utilisées.

## 21. Défi final : politique d'accès entre utilisateurs, Web et administration

### Contexte

R1 relie le réseau utilisateurs 192.168.10.0/24 sur GigabitEthernet0/0 au réseau de serveurs 192.168.20.0/24 sur GigabitEthernet0/1. Le serveur Web utilise 192.168.20.10. Le serveur d'administration SSH utilise 192.168.20.30. Les administrateurs se trouvent dans 192.168.40.0/24.

Les objectifs : autoriser les utilisateurs à atteindre HTTPS sur le serveur Web, bloquer SSH des utilisateurs vers le serveur d'administration, permettre à l'équipe autorisée d'administrer les systèmes et documenter les autres flux. La politique ne doit pas ouvrir tout le réseau pour résoudre un problème limité.

### Correction raisonnée

Commence par confirmer les interfaces, les routes et les adresses réellement utilisées. Vérifie le port du service Web et le port SSH du serveur d'administration. L'entrée HTTPS doit identifier le réseau source, le serveur cible, TCP et le port 443. L'entrée de refus SSH doit viser le réseau utilisateurs, le serveur d'administration, TCP et le port 22, et être située avant toute autorisation plus générale qui laisserait passer le même trafic.

L'accès aux lignes VTY de R1 doit être traité séparément de l'accès au serveur SSH : l'ACL VTY contrôle l'administration du routeur, tandis qu'une ACL d'interface ou un pare-feu hôte contrôle le chemin vers le serveur. Il faut placer chaque contrôle au point qui voit réellement le flux.

Ne choisis pas une entrée permit ip any any par simple commodité. Définis le comportement attendu des autres communications et inventorie les dépendances DNS, mises à jour, authentification, synchronisation horaire et applications métier. Si le laboratoire impose un permit général, note qu'il s'agit d'une contrainte pédagogique et non d'une recommandation générale de production.

Sauvegarde avant le changement et garde un accès de secours. Après l'application, vérifie les ACL et leur interface, puis effectue les tests : HTTPS depuis un utilisateur autorisé, SSH depuis un utilisateur qui devrait être bloqué, SSH depuis la source d'administration permise et accès refusé depuis une source non autorisée. Consigne les résultats et les compteurs.

Le défi est réussi si les flux permis fonctionnent, les flux interdits échouent pour la raison attendue, l'ACL est attachée correctement et une personne tierce peut comprendre la politique.

## 22. Glossaire

**ACL :** liste ordonnée qui applique des décisions à du trafic correspondant à des critères.

**ACL standard :** ACL IPv4 classique fondée principalement sur la source.

**ACL étendue :** ACL qui peut sélectionner source, destination, protocole et ports selon la plateforme.

**Wildcard :** masque de comparaison où 0 impose une correspondance et 1 ignore le bit, dans la syntaxe Cisco classique.

**Refus implicite :** refus final si aucune entrée n'autorise le paquet.

**in/out :** direction du paquet par rapport à l'interface où l'ACL est attachée.

**ACL nommée :** liste identifiée par un nom lisible, souvent avec numéros de séquence.

**Plan de gestion :** interfaces et protocoles utilisés pour administrer des équipements.

**VTY :** lignes virtuelles Cisco utilisées pour la gestion distante, notamment SSH.

**Compteur :** quantité de correspondances comptabilisées pour une entrée, selon le système.

**Pare-feu à états :** dispositif qui suit les sessions pour prendre des décisions selon le contexte.

**Retour arrière :** procédure permettant de revenir à une configuration connue après un changement problématique.

## 23. Références

- Cisco, guide de configuration des ACL IPv4, à adapter à la version IOS réellement utilisée : https://www.cisco.com/c/en/us/support/docs/security/ios-firewall/23602-confaccesslists.html
- RFC 4632, CIDR et allocation des préfixes : https://www.rfc-editor.org/rfc/rfc4632
- RFC 4291, architecture d'adressage IPv6 : https://www.rfc-editor.org/rfc/rfc4291

Les syntaxes évoluent selon les gammes d'équipements et les versions. Vérifie la documentation officielle, utilise l'aide intégrée et valide le comportement dans un laboratoire avant toute modification d'un réseau opérationnel.

Fin du cours.

## 24. Études de cas de dépannage

Les cas suivants reprennent des erreurs fréquentes en laboratoire et en exploitation. Ils donnent une méthode de raisonnement, pas une autorisation d'appliquer aveuglément une règle en production.

### Cas de dépannage 1 — Le trafic ciblé n'est pas bloqué

**Analyse.** Le refus peut être placé après une autorisation générale, l'adresse source réelle peut différer de celle prévue ou l'ACL peut ne pas être appliquée au chemin. Lis toute la liste, vérifie les adresses observées, le wildcard, l'interface et les compteurs. Puis confirme que le paquet entre bien par l'interface où la liste est attachée. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne multiplie pas les refus avant d'avoir localisé le point où le paquet rencontre l'ACL. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 2 — Un sous-réseau correspond à trop d'hôtes

**Analyse.** Le masque réseau peut avoir été copié à la place du wildcard, ou l'adresse de réseau peut être mal alignée. Inverse le masque octet par octet et vérifie les bornes du bloc. Pour un /24, le masque est 255.255.255.0 et le wildcard conventionnel 0.0.0.255. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne laisse pas une règle trop large simplement parce que le premier test fonctionne. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 3 — DNS est bloqué après l'ajout d'une ACL

**Analyse.** Une entrée restrictive ou le refus implicite peut bloquer le résolveur ; DNS peut utiliser UDP/53 et, dans certains cas, TCP/53. Identifie le résolveur, le protocole et le chemin. Autorise uniquement les flux nécessaires puis teste à nouveau la résolution et les restrictions restantes. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne remplace pas la politique par une autorisation générale uniquement pour que les noms se résolvent. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 4 — HTTP fonctionne, HTTPS échoue

**Analyse.** L'ACL peut autoriser TCP/80 seulement, viser une mauvaise destination ou ne pas correspondre à la source réelle. Confirme le port TCP/443, l'adresse de destination, le wildcard, l'ordre des entrées, l'interface et le service TLS du serveur. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne confonds pas l'autorisation de TCP/80 avec l'autorisation de tous les services Web. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 5 — Une ACL standard devrait bloquer seulement SSH

**Analyse.** Une ACL standard classique ne sélectionne pas les ports et ne peut pas exprimer à elle seule ce critère. Conçois une ACL étendue au bon point de passage ou un contrôle dédié du service d'administration. Vérifie que les autres services restent accessibles comme prévu. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne prétends pas qu'un filtre fondé uniquement sur la source distingue SSH des autres services. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 6 — La session d'administration est perdue

**Analyse.** Une ACL VTY peut exclure l'adresse source de la session, ou une ACL de données a pu être appliquée au mauvais endroit. Utilise la console ou le canal de secours, vérifie les lignes VTY et restaure la source autorisée. Documente la cause avant de retenter le changement. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne poursuis pas des modifications depuis une session distante instable. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 7 — L'ACL existe mais n'a aucun effet

**Analyse.** La liste peut être définie mais non appliquée, ou les paquets peuvent emprunter une autre interface. Utilise show ip interface et show running-config interface, identifie les directions et examine la route du flux. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne confonds pas créer une liste et l'appliquer. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 8 — Les compteurs restent à zéro

**Analyse.** Aucun paquet ne correspond, le chemin est différent, ou les compteurs ont été réinitialisés. Reproduis un test simple avec une source connue, confirme l'adresse et observe les compteurs tout en vérifiant l'interface d'entrée. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Un compteur à zéro ne prouve pas à lui seul qu'aucun trafic ne circule. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 9 — Les autres services ne fonctionnent plus après un permit HTTPS

**Analyse.** Le refus implicite bloque les paquets qui ne correspondent pas à la seule entrée autorisante. Inventorie les dépendances de l'interface et ajoute les flux nécessaires à partir d'exigences documentées, puis reteste le reste. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne présume pas qu'une entrée qui permet HTTPS autorise tous les autres services. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 10 — Le trafic est autorisé malgré un deny spécifique

**Analyse.** Une entrée générale située avant la règle spécifique peut prendre la décision en premier. Relis la liste de haut en bas et déplace la règle spécifique avant la généralité selon la procédure de la plateforme. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne considère pas qu'une entrée plus bas annule une action déjà décidée. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 11 — Le /26 vise la mauvaise plage

**Analyse.** L'adresse réseau peut ne pas être alignée sur une frontière de bloc, ou le wildcard est erroné. Pour un /26 aligné, vérifie le masque 255.255.255.192 et le wildcard 0.0.0.63, puis calcule l'adresse réseau avant de déployer. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne devine pas la plage en regardant uniquement le dernier octet. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 12 — Les réponses à l'application échouent

**Analyse.** Une autre ACL dans le sens retour peut bloquer la réponse, ou un flux de dépendance est absent. Dessine le trajet dans les deux sens, identifie les ACL appliquées sur les interfaces et évalue si un pare-feu à états est nécessaire. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** N'ajoute pas une autorisation générale sans comprendre le chemin de retour. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 13 — Le ping échoue après filtrage

**Analyse.** ICMP peut être bloqué, mais l'échec peut aussi provenir d'une route ou d'un hôte indisponible. Vérifie l'objectif du test, le chemin et les journaux ; si nécessaire, autorise uniquement les types ICMP attendus selon la politique. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne prends pas le ping pour un test complet d'un service TCP. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 14 — Un service reste accessible en IPv6

**Analyse.** L'ACL IPv4 ne couvre pas automatiquement la pile IPv6. Inventorie les adresses et routes IPv6, repère les règles dédiées puis teste le flux sur cette pile. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne présume pas que la présence d'une ACL IPv4 protège tous les chemins. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 15 — Le serveur Web devient inaccessible

**Analyse.** La règle peut utiliser une mauvaise source, un wildcard erroné, une direction incorrecte ou un port inadapté. Compare la configuration avant/après, vérifie routes, compteurs et écoute du serveur, puis rétablis uniquement le flux nécessaire. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne retire pas toute la liste sans sauvegarde ni diagnostic. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 16 — Les logs deviennent trop volumineux

**Analyse.** Une règle de journalisation appliquée à beaucoup de paquets peut générer trop d'événements. Limite la journalisation aux cas pertinents et configure un débit approprié si la plateforme le permet. Vérifie que les événements essentiels restent visibles. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne journalise pas sans réflexion chaque paquet sur un lien chargé. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 17 — Une ACL accumule des règles redondantes

**Analyse.** Des ajouts successifs rendent la politique difficile à lire et peuvent masquer son intention. Analyse les compteurs et la dépendance de chaque entrée, regroupe ou supprime après test et conserve une copie de l'ancienne configuration. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne supprime pas une règle uniquement parce qu'elle ressemble à une autre. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 18 — Le trafic contourne le routeur

**Analyse.** Des hôtes du même segment peuvent communiquer directement sans passer par le routeur filtrant. Étudie le chemin réel, ajoute une segmentation ou un contrôle au point de passage approprié et teste la communication latérale. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne présume pas que l'ACL de passerelle voit tous les échanges du LAN. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 19 — L'administration reste accessible aux utilisateurs

**Analyse.** Le contrôle peut être attaché à une interface de données au lieu de la ligne VTY, ou une autre méthode de gestion reste ouverte. Distingue l'accès au routeur de l'accès à un serveur derrière lui. Vérifie les VTY, les sources autorisées, SSH, l'interface Web et les autres méthodes de gestion. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne confonds pas filtrage de transit et filtrage du plan de gestion. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 20 — Le laboratoire demande permit ip any any

**Analyse.** Le scénario veut bloquer un flux ciblé tout en laissant le reste du trafic passer. Exécute l'exercice tel qu'il est défini, vérifie l'ordre et l'application, puis explique dans la documentation que la règle générale est propre à ce scénario. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne copie pas cette permission générale en production sans analyse. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 21 — Le fournisseur utilise une autre syntaxe

**Analyse.** Les ACL diffèrent entre Cisco IOS, d'autres routeurs, les pare-feu logiciels et les services cloud. Traduis d'abord le besoin en source, destination, protocole, port, direction et action ; utilise ensuite la syntaxe documentée pour le produit réel. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne copie pas directement une commande IOS sur un système différent. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 22 — Un changement urgent a été fait sans retour arrière

**Analyse.** La modification a été appliquée sans sauvegarde ni canal de récupération. Récupère l'accès via un canal hors bande s'il existe, restaure la configuration connue et ajoute un contrôle préalable au processus de changement. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne transforme pas un dépannage improvisé en méthode normale. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 23 — Un hôte inattendu est autorisé

**Analyse.** Le wildcard ou l'adresse source peut couvrir un ensemble d'adresses plus grand que prévu. Compare les sources observées, calcule la plage et utilise un hôte précis ou un préfixe correct lorsque le besoin le permet. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne remplace pas la vérification d'adresse par le nom d'un poste. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 24 — Les mises à jour ne fonctionnent plus

**Analyse.** Le serveur peut dépendre d'un DNS, d'un proxy ou d'une destination de mise à jour oubliée dans l'inventaire. Consulte la documentation, identifie les destinations et protocoles nécessaires et ajoute une exception limitée et documentée. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** N'autorise pas tout le trafic sortant pour un seul flux manquant. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 25 — Une règle trop permissive est restée après migration

**Analyse.** Une exception de test a été conservée ou le chemin réseau a changé. Compare les flux attendus à la configuration, vérifie les points de passage et retire les règles obsolètes après validation. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne te fie pas au commentaire historique si la topologie a changé. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 26 — Une règle TCP ne bloque pas UDP sur le même port

**Analyse.** Les critères de protocole sont distincts : une entrée TCP ne couvre pas automatiquement UDP. Confirme les protocoles réellement utilisés par l'application et écris les règles requises pour chacun. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne considère pas le numéro de port comme une description complète du protocole. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 27 — La configuration disparaît au redémarrage

**Analyse.** La configuration courante a été modifiée mais n'a peut-être pas été enregistrée dans la configuration de démarrage. Après validation, applique la procédure de sauvegarde propre à la plateforme et confirme l'état après redémarrage dans un laboratoire. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne sauvegarde pas une ACL non testée qui pourrait couper l'administration. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 28 — L'adresse source est différente après NAT

**Analyse.** Le dispositif ACL peut observer une adresse traduite plutôt que l'adresse originale. Identifie le point de traduction et les adresses vues avant/après NAT ; adapte la règle au trafic réellement visible au point de filtrage. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne suppose pas que la source d'origine est visible partout. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 29 — Le port semble ouvert, mais l'application ne répond pas

**Analyse.** Le service peut être arrêté, mal configuré ou parler un autre protocole que celui du test. Examine les sockets, les journaux applicatifs, l'adresse d'écoute et la requête client. Corrige le service si le filtrage n'est pas la cause. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne conclus pas uniquement à partir d'un affichage de port. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

### Cas de dépannage 30 — La politique n'est pas maintenable

**Analyse.** Des règles non nommées, non justifiées ou sans propriétaire sont difficiles à réviser. Utilise des noms explicites, documente chaque entrée et fixe des dates de revue pour les exceptions. Consigne les faits observables avant la modification et traite un paramètre à la fois pour pouvoir identifier la cause réelle.

**Erreur à éviter.** Ne privilégie pas une configuration compacte au détriment de la compréhension. Après la correction, teste le flux autorisé et au moins un flux qui doit rester interdit. Note les résultats, la cause retenue, le responsable et la date de revue.

Fin du cours.