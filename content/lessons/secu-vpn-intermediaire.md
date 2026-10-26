# VPN Site-to-Site et d'accès distant

> **Mise en contexte**
>
> Deux bureaux doivent partager des applications internes sans exposer leurs réseaux à l'ensemble d'Internet. En parallèle, les administrateurs et les employés en déplacement doivent accéder à certaines ressources depuis l'extérieur. Un VPN (*Virtual Private Network*, réseau privé virtuel) crée un chemin logique protégé sur un réseau qui n'est pas entièrement fiable. Mais un tunnel chiffré n'est pas, à lui seul, une politique d'accès : une fois connecté, un utilisateur ou un site distant ne doit recevoir que les droits nécessaires.
>
> Ce cours présente les VPN Site-to-Site et d'accès distant, les bases de la cryptographie appliquée aux tunnels, IPsec/IKE, les notions de pairs, sélecteurs, routes et politiques, les certificats, les mécanismes d'authentification, les architectures de segmentation, les journaux et les méthodes de dépannage. Les configurations exactes dépendent du fabricant et de la version. Les exemples sont pédagogiques et doivent être utilisés seulement sur un réseau de laboratoire ou un équipement autorisé.

## 1. Objectifs pédagogiques et prérequis

À la fin de ce cours, tu devras savoir différencier un VPN Site-to-Site d'un VPN d'accès distant, expliquer les rôles de l'encapsulation et du chiffrement, distinguer IPsec/IKE de TLS-VPN, comprendre les notions de pair, de tunnel, de réseau local et distant, de sélecteur et de route, connaître les fonctions de l'authentification par clé prépartagée et par certificat, décrire le rôle de MFA, expliquer le split tunneling et le full tunneling, sécuriser les accès distants, diagnostiquer un tunnel inactif ou un trafic unidirectionnel, interpréter les journaux et organiser un changement réversible.

Les prérequis utiles sont les adresses IPv4, les routes, les sous-réseaux, le NAT, les ACL, TCP/UDP et les principes de base du chiffrement et des certificats. Les termes cryptographiques sont expliqués au fur et à mesure. Les commandes et exemples de configuration varient selon les équipements : un exemple générique sert à raisonner, pas à remplacer la documentation de la version utilisée.

## 2. Qu'est-ce qu'un VPN ?

Un VPN crée une communication logique protégée entre des hôtes, des réseaux ou des dispositifs de passerelle. Il utilise des mécanismes de sécurité pour fournir une combinaison de confidentialité, d'intégrité, d'authentification et de protection contre certaines manipulations ou relectures, selon le protocole et la configuration.

Le chiffrement rend le contenu plus difficile à lire pour un observateur qui ne possède pas les clés. L'intégrité permet de détecter une modification non autorisée des données. L'authentification vérifie l'identité d'un pair ou la possession d'un secret attendu. La protection anti-rejeu aide à empêcher qu'un paquet enregistré soit simplement retransmis pour répéter une action.

Le VPN ne rend pas automatiquement sûr le terminal de l'utilisateur, le serveur distant, l'application ou le réseau local après le déchiffrement. Si un appareil est compromis, il peut transmettre des données à l'intérieur d'un tunnel valide. Il faut combiner le VPN avec l'authentification forte, les correctifs, la segmentation, les politiques de pare-feu et la surveillance.

## 3. VPN Site-to-Site et accès distant

### VPN Site-to-Site

Un VPN Site-to-Site relie généralement deux passerelles réseau, par exemple les routeurs ou pare-feu de deux bureaux. Les équipements établissent un tunnel ou une association de sécurité, puis protègent le trafic entre des réseaux définis. Les postes utilisateurs n'ont pas nécessairement besoin d'exécuter un client VPN individuel, car leurs paquets sont protégés par les passerelles.

Exemple conceptuel :

~~~text
LAN A 192.168.10.0/24
         |
     [GW-A]
         ||
         || tunnel protégé sur Internet
         ||
     [GW-B]
         |
LAN B 10.20.0.0/16
~~~

Les deux passerelles doivent disposer d'une politique cohérente : adresses des pairs, sous-réseaux locaux et distants, paramètres cryptographiques, authentification, routes et règles de sécurité. Une phase de négociation réussie ne garantit pas que les routes ou les règles autorisent le trafic applicatif.

### VPN d'accès distant

Un VPN d'accès distant relie un terminal individuel, comme un portable géré, à une passerelle de l'organisation. Le terminal lance un client ou utilise un client intégré au système. La connexion peut nécessiter une identité utilisateur, un certificat d'appareil, un facteur supplémentaire ou une conformité du terminal.

Ce modèle convient aux employés en déplacement ou en télétravail. Il exige de contrôler qui peut se connecter, quels systèmes ou zones chaque groupe peut atteindre, comment les appareils sont maintenus et comment révoquer un accès. Un utilisateur authentifié ne devrait pas être placé automatiquement dans le même réseau de confiance que les administrateurs.

## 4. Choisir entre IPsec et VPN basé sur TLS

IPsec est un ensemble de mécanismes de sécurité de couche IP, fréquemment utilisé pour les VPN Site-to-Site et aussi pour certaines solutions d'accès distant. IKE négocie des paramètres et des associations de sécurité. Dans les déploiements courants, IPsec protège les paquets IP dans un tunnel ou dans un mode de transport ; le mode tunnel est fréquent pour relier des réseaux.

Les VPN basés sur TLS ou des protocoles dérivés utilisent des mécanismes autour de TLS pour protéger une connexion à un concentrateur. Ils peuvent fonctionner à travers des réseaux où certains chemins IPsec sont bloqués, mais le comportement dépend du produit et des ports configurés. Une solution peut fournir un accès de couche réseau ou un accès plus ciblé à certaines applications.

Le choix doit prendre en compte les équipements, les clients compatibles, les besoins d'accès, la gestion des identités, les performances, l'exploitation, la journalisation, les contraintes réseau et la possibilité de mettre à jour les composants. Le nom du protocole ne suffit pas à évaluer la sécurité : la version, les suites cryptographiques, l'authentification et la politique comptent.

## 5. Notions fondamentales d'IPsec

IPsec protège les paquets IP selon une politique. Les deux concepts souvent évoqués sont AH (*Authentication Header*) et ESP (*Encapsulating Security Payload*). ESP peut fournir confidentialité, intégrité et authentification selon la suite sélectionnée. AH ne chiffre pas le contenu et est moins courant dans les VPN modernes ; les interactions avec NAT peuvent également le rendre peu pratique.

Une association de sécurité (SA) décrit un ensemble de paramètres utilisé pour traiter un flux protégé. Les associations sont orientées et disposent de paramètres tels que les algorithmes, les clés et les identifiants. Le détail dépend du protocole et de la version. Il est donc normal qu'une communication bidirectionnelle implique des états distincts dans chaque sens.

Le mode tunnel encapsule le paquet IP d'origine dans un nouveau paquet IP externe, ce qui permet aux passerelles de transporter les réseaux internes à travers Internet. Le paquet interne porte les adresses des hôtes de la communication protégée ; le paquet externe porte les adresses des pairs qui transportent le tunnel.

~~~text
Paquet original :
[IP source LAN-A | IP cible LAN-B | données]
                  |
                  v encapsulation IPsec
[IP externe GW-A | IP externe GW-B | ESP{paquet original}]
~~~

Les adresses externes des passerelles peuvent être visibles sur le réseau de transport, tandis que les données internes sont protégées dans la charge utile chiffrée. Les métadonnées non chiffrées ne disparaissent pas toutes : la confidentialité doit être évaluée en fonction du protocole et de sa configuration.

## 6. IKE : négociation et clés

IKE, *Internet Key Exchange*, négocie des paramètres de sécurité et contribue à l'établissement des associations utilisées par IPsec. IKEv2 est couramment préféré aux anciens déploiements IKEv1 lorsqu'il est pris en charge et que les exigences le permettent. Il faut consulter les recommandations de sécurité actuelles et la documentation du fabricant.

Pendant la négociation, les pairs doivent s'accorder sur les suites cryptographiques, les groupes de clés, les durées de vie, les identités et la méthode d'authentification. Si aucune proposition compatible n'est commune, la négociation échoue. Si les deux équipements ne s'identifient pas de la même manière, une configuration qui paraît symétrique peut néanmoins ne pas s'établir.

Les propositions doivent utiliser des algorithmes maintenus et suffisamment robustes. Évite les suites obsolètes et les paramètres faibles simplement parce qu'ils permettent à un vieux matériel de se connecter. Une exception de compatibilité doit être documentée, limitée et associée à un plan de remplacement. Ne partage pas les clés ou les secrets dans les journaux, tickets accessibles largement ou captures d'écran.

## 7. Authentifier le pair : secret partagé ou certificat

Une clé prépartagée (PSK) est un secret configuré sur les deux pairs. Elle peut être rapide à mettre en place dans un petit laboratoire, mais elle devient plus difficile à gérer lorsque plusieurs sites ou équipes l'utilisent. Un secret faible est exposé au risque de devinette et un secret copié partout complique la révocation. Les secrets doivent être longs, uniques par relation lorsque c'est possible, stockés de façon protégée et renouvelés selon un processus.

Les certificats permettent une authentification fondée sur une identité émise par une autorité de certification. Chaque équipement possède sa clé privée et un certificat lié à son identité ; le pair vérifie que le certificat est valide et correspond à l'identité attendue. La clé privée ne doit jamais être envoyée à l'autre partie. Le certificat public peut être distribué, mais son authenticité dépend de la chaîne de confiance et des règles de vérification.

Le cycle de vie d'un certificat inclut l'émission, le déploiement, le renouvellement, la révocation et la surveillance de l'expiration. Une panne de tunnel due à un certificat expiré est évitable avec des alertes et des procédures. La révocation doit être conçue pour le cas où une clé privée est compromise, et les horloges doivent être correctes pour que les dates de validité soient interprétées correctement.

## 8. Authentification utilisateur, MFA et posture du terminal

Pour un VPN d'accès distant, la possession d'un mot de passe ne doit pas être considérée comme une preuve suffisante dans tous les contextes. L'authentification multifacteur combine des catégories distinctes, par exemple quelque chose que l'utilisateur connaît, quelque chose qu'il possède ou un facteur biométrique pris en charge par le système. Le MFA résistant à l'hameçonnage est préférable lorsque l'architecture le permet.

Un certificat d'appareil peut prouver que le terminal est géré, mais il ne prouve pas nécessairement que son utilisateur est autorisé à accéder à toutes les applications. Inversement, une identité utilisateur authentifiée ne garantit pas que l'appareil est à jour et protégé. L'accès distant doit combiner identité, appareil, contexte et droits autorisés selon les capacités de l'organisation.

Une politique de posture peut vérifier le chiffrement de disque, l'état de l'antivirus/EDR, les correctifs, le verrouillage, le certificat, la version du système ou d'autres critères. Les contrôles doivent être réalistes et testés pour éviter de bloquer soudainement des utilisateurs essentiels. Un terminal non conforme peut être mis en quarantaine ou recevoir seulement l'accès à un portail de remédiation.

## 9. Plan d'adressage, sous-réseaux et chevauchements

Les réseaux local et distant d'un VPN Site-to-Site doivent pouvoir être distingués. Si les deux sites utilisent la même plage, par exemple 192.168.1.0/24, les routes et sélecteurs peuvent devenir ambigus. Certaines solutions disposent de techniques de traduction ou de proxying pour traiter le chevauchement, mais elles accroissent la complexité et doivent être conçues explicitement.

À long terme, un plan d'adressage cohérent réduit les exceptions. Avant de construire le tunnel, inventorie les préfixes de chaque site, les réseaux invités, l'administration, les plages VPN attribuées aux clients et les services qui doivent être partagés. Les plages de clients distants ne doivent pas recouvrir les réseaux locaux ou les adresses fréquemment utilisées sur les réseaux domestiques.

Un tunnel peut être techniquement établi mais inutilisable si les routes sont absentes, plus spécifiques ou asymétriques. La route aller et la route de retour doivent être cohérentes, et les pare-feu des deux extrémités doivent autoriser les flux nécessaires. Un ping qui échoue ne prouve pas à lui seul que le tunnel cryptographique est en panne.

## 10. Sélecteurs, politiques et routage

Dans un VPN IPsec policy-based, les sélecteurs ou ACL cryptographiques décrivent le trafic à protéger, comme le réseau local A vers le réseau distant B. Les politiques basées sur les routes utilisent une interface de tunnel logique sur laquelle le routage dirige les paquets. Les détails diffèrent selon le fournisseur. Il faut savoir quel modèle est utilisé et comment les paquets sont sélectionnés.

Une ACL qui sélectionne le trafic à chiffrer n'est pas nécessairement une ACL de pare-feu. Les mêmes mots peuvent désigner différents rôles. Il faut documenter séparément les critères d'inclusion dans le tunnel, les autorisations de sécurité et les routes. Une configuration qui autorise un flux dans le pare-feu ne garantit pas qu'il est sélectionné pour le tunnel ; un sélecteur qui comprend le flux ne garantit pas que le pare-feu l'autorise.

Pour un VPN à routes, l'existence d'une route vers l'interface de tunnel ne garantit pas que les sélecteurs, la politique distante et les règles de pare-feu correspondent. Pour un VPN policy-based, un trafic qui ne correspond pas aux sélecteurs peut partir en dehors du tunnel selon les routes et la configuration, ou être abandonné. Un test doit confirmer le chemin réellement emprunté.

## 11. NAT et exemption pour le VPN

Quand les hôtes internes utilisent PAT pour naviguer sur Internet, le trafic destiné au site distant doit souvent être exclu de la traduction afin de conserver les adresses attendues par le tunnel. Le mécanisme exact dépend du produit et de l'ordre de traitement NAT. Une exemption trop large peut affecter la sortie Internet, tandis qu'une exemption manquante peut empêcher le trafic de correspondre aux sélecteurs VPN.

Exemple conceptuel :

~~~text
LAN-A 192.168.10.0/24
   |         \
   |          \-- flux vers Internet : PAT
   |
   +------------- flux vers 10.20.0.0/16 : préserver les adresses
                         |
                         v
                      tunnel VPN
~~~

La politique doit décrire les destinations qui utilisent le VPN et celles qui utilisent la sortie Internet normale. Vérifie les adresses avant et après traduction dans la table NAT et les journaux. Ne crée pas un « no NAT » global sans regarder les autres réseaux de l'entreprise.

## 12. Full tunnel et split tunnel

Avec le **full tunnel**, le trafic IP choisi de l'appareil distant passe par le VPN et est souvent acheminé vers l'infrastructure de l'entreprise, y compris l'accès Internet selon la politique. L'organisation peut ainsi appliquer les contrôles centraux, les filtres DNS ou Web et la journalisation attendue. La charge de bande passante, la latence et la capacité des concentrateurs doivent être dimensionnées.

Avec le **split tunnel**, seuls les réseaux ou destinations désignés passent dans le VPN ; les autres communications sortent directement par le réseau utilisé par l'utilisateur. Cela peut améliorer les performances et réduire le trafic à travers l'entreprise, mais expose certains usages aux protections du réseau local. Il faut déterminer quelles destinations sont incluses et éviter qu'une route ou un DNS mal configuré contourne les contrôles attendus.

Aucun choix n'est universel. La politique dépend de la sensibilité des données, du modèle d'accès, des besoins de performance et des contrôles du terminal. Documente les destinations, les routes, la gestion DNS et les comportements en cas de coupure. Teste les routes effectives depuis un client VPN, et pas seulement la case de configuration.

## 13. VPN d'accès distant : accès par rôle

Un VPN d'accès distant doit donner aux utilisateurs les routes et autorisations nécessaires à leur rôle. Le groupe comptabilité peut accéder aux applications comptables, tandis que l'administration réseau peut accéder aux interfaces de gestion depuis un poste géré. Ces droits ne doivent pas être accordés par défaut à tous les utilisateurs VPN.

Attribue des plages de clients distants distinctes et reconnaissables dans les journaux. Documente la correspondance entre identité, groupe, adresse attribuée et ressources autorisées. Les règles de pare-feu doivent distinguer le pool VPN des réseaux internes, des invités et de l'administration.

Retire rapidement les comptes et certificats qui n'ont plus de justification. Prévois une procédure pour un appareil perdu, un employé parti, un secret divulgué ou un compte suspect. Selon la plateforme, la révocation peut demander de couper les sessions actives, retirer le certificat, révoquer le jeton et bloquer l'identité. Le changement d'un seul mot de passe ne suffit pas forcément si une session est déjà établie.

## 14. Accès d'administration au VPN

Les interfaces d'administration sont des cibles à fort impact. Le fait d'être connecté au VPN ne doit pas suffire pour accéder au réseau d'administration. Utilise une zone de gestion restreinte, un bastion ou une solution d'accès privilégié, des identités individuelles, des clés et une authentification forte.

Les accès administratifs peuvent nécessiter un appareil dédié ou conforme, des privilèges juste-à-temps et une journalisation renforcée. Les sessions doivent être limitées à la durée et aux systèmes nécessaires. L'accès de secours doit exister mais être protégé, testé et journalisé ; il ne doit pas devenir un compte permanent non surveillé.

Les portails VPN et les passerelles doivent être corrigés régulièrement. N'expose pas l'interface de gestion du concentrateur sur le même chemin public que le portail utilisateur si le produit permet de séparer les plans. Les interfaces d'administration doivent être accessibles depuis des sources approuvées uniquement.

## 15. DNS, routes et résolution des noms

Le VPN peut pousser des routes et des serveurs DNS au client. Si les noms internes ne se résolvent pas, le tunnel peut être actif et les routes IP correctes, mais l'utilisateur ne pourra pas utiliser les noms d'applications. Vérifie l'adresse du résolveur, la route vers lui, les règles, les suffixes DNS et les politiques de split DNS.

Une configuration split tunnel peut envoyer les requêtes de certains domaines vers le DNS interne et le reste vers le DNS local ou un résolveur protégé. Le modèle dépend du client. Un DNS incorrect peut aussi divulguer des requêtes internes vers le réseau local ou produire des réponses incohérentes.

Ne commence pas par modifier les serveurs DNS de tous les clients sans identifier la politique du concentrateur. Vérifie les paramètres réellement poussés, puis effectue des tests de résolution avec un nom interne connu et un nom public. La connectivité par adresse IP et la résolution DNS sont deux problèmes distincts.

## 16. MTU, MSS, fragmentation et performance

L'encapsulation ajoute des en-têtes au paquet original. Le tunnel peut donc transporter une charge utile inférieure à la MTU du réseau sous-jacent. Si la MTU et les mécanismes de découverte sont mal gérés, certains flux échouent ou deviennent lents, notamment des transferts volumineux qui n'ont pas la même taille que les petits tests.

La MSS TCP peut être ajustée dans certains déploiements afin de réduire la taille des segments qui traversent le tunnel. La bonne valeur dépend de l'encapsulation, du chemin et de la plateforme. Il ne faut pas copier une valeur trouvée en ligne sans mesurer ni vérifier les recommandations du fabricant.

Les symptômes MTU incluent parfois des connexions qui s'établissent mais des pages qui chargent partiellement, des transferts qui se bloquent ou certains sites inaccessibles. Compare les tailles de paquet, examine les messages ICMP pertinents et teste progressivement. N'autorise pas toutes les communications ou ne désactive pas tous les contrôles comme solution au problème de taille.

Les performances dépendent aussi du chiffrement matériel, du débit, du nombre de sessions, de la latence, de la perte de paquets, des chemins opérateur et de la charge de l'équipement. Mesure la situation au lieu d'attribuer chaque lenteur au VPN.

## 17. Redondance et haute disponibilité

Pour un site critique, une seule passerelle VPN peut devenir un point de panne. Des dispositifs redondants, plusieurs liens ou plusieurs pairs peuvent améliorer la disponibilité, mais la conception dépend du protocole, du fournisseur et des routes. Les identités, clés, certificats, politiques et routes doivent être cohérents entre les pairs.

Une bascule ne doit pas seulement être déclarée active : vérifie qu'un nouveau trafic peut s'établir, que les routes convergent, que les applications répondent et que le retour à la passerelle principale ne crée pas d'instabilité. Certains mécanismes conservent des états de session ; d'autres obligent les clients à se reconnecter.

Documente les tests de basculement, la maintenance des pairs, les délais de convergence et les responsables d'escalade. Une haute disponibilité mal testée peut donner une impression de résilience sans fournir une continuité réelle.

## 18. Journalisation et surveillance du VPN

Les journaux utiles comprennent les tentatives d'authentification, les échecs MFA, l'établissement et la fermeture des tunnels, les changements d'adresse attribuée, les paramètres de négociation, les erreurs de certificat, les événements de révocation et les accès vers les ressources sensibles. Le détail et le nom des commandes dépendent de la plateforme.

Surveille les échecs répétés, les connexions depuis des lieux ou appareils inhabituels, les connexions hors des plages attendues et les changements de configuration. Un grand nombre d'échecs n'est pas automatiquement une attaque ; compare-le avec les changements de mot de passe, l'expiration des certificats et les incidents de client. Les logs doivent être horodatés et protégés.

Enregistre les flux nécessaires pour comprendre quels réseaux sont réellement utilisés, tout en suivant les obligations de confidentialité et de conservation des données. Évite de stocker les secrets, clés privées ou jetons dans les tickets ou journaux. Les alertes doivent être associées à des procédures opérationnelles, pas simplement générées sans responsable.

## 19. Commandes et vérifications : approche générale

Il n'existe pas une seule commande portable pour tous les fabricants de VPN. Les noms de commandes varient entre Cisco IOS/IOS XE, ASA/FTD, FortiGate, pfSense, Linux strongSwan et les clients Windows/macOS. La bonne procédure commence par identifier le produit, la version et le modèle de configuration.

Sur un routeur Cisco IOS, des commandes de diagnostic usuelles peuvent inclure, selon la plateforme et les fonctions activées :

~~~text
show crypto ikev2 sa
show crypto ipsec sa
show crypto session
show access-lists
show ip route
show ip nat translations
~~~

Toutes les commandes ne sont pas disponibles sur toutes les versions. Elles servent à examiner l'état IKE, les associations IPsec, les compteurs, les routes, les ACL et les traductions. Dans un autre produit, recherche les équivalents officiels dans la documentation correspondante.

Sur Linux, si strongSwan est utilisé, des commandes comme ipsec statusall ou la commande de gestion swanctl --list-sas peuvent être disponibles selon l'installation et la version. Vérifie l'outil installé avant d'exécuter une commande. Pour le routage et l'adressage, ip address et ip route restent des points de lecture utiles.

Sur un client Windows, examine l'état de l'adaptateur VPN, les adresses attribuées et les routes effectives. Les paramètres et commandes dépendent du type de client VPN et de la politique centralisée. Ne désactive pas le pare-feu de Windows ou l'antivirus pour diagnostiquer un tunnel ; commence par des mesures ciblées et les journaux.

## 20. Procédure de dépannage d'un tunnel inactif

1. Confirme l'état des interfaces, les adresses des pairs et la connectivité IP entre les passerelles.
2. Vérifie les routes vers le pair, les ports ou protocoles nécessaires au modèle de VPN et les règles sur le chemin.
3. Examine la négociation IKE : les pairs s'authentifient-ils et trouvent-ils des propositions communes ?
4. Vérifie l'identité, la PSK ou le certificat, la validité temporelle et l'autorité de certification attendue.
5. Compare les algorithmes, les groupes, les durées de vie et les paramètres configurés des deux côtés.
6. Vérifie la politique IPsec, les sélecteurs, les réseaux locaux et distants, ou la route vers l'interface de tunnel.
7. Examine les ACL de filtrage, la politique NAT et les éventuelles exemptions.
8. Génère un trafic de test depuis une adresse incluse dans la politique, puis consulte les compteurs et journaux.
9. Vérifie le chemin retour et la réponse de l'application.
10. Change un seul élément à la fois et documente les résultats.

Ne modifie pas simultanément la PSK, les algorithmes, les routes et les ACL : si le tunnel revient, tu ne sauras pas quelle correction était nécessaire, et tu risques d'introduire une faiblesse ou un défaut supplémentaire.

## 21. Dépanner un tunnel établi mais sans trafic

Un état IKE établi signifie que la phase de négociation correspondante a réussi. Cela ne prouve pas que la politique de données, les sélecteurs, le routage et le pare-feu laissent passer le trafic requis. Les compteurs d'encapsulation et de décapsulation peuvent aider à déterminer si les deux côtés voient des paquets.

Si les compteurs d'émission augmentent mais que les compteurs de réception restent à zéro, vérifie le pair distant, le réseau de transport, le filtrage entre les pairs et le trafic qui revient. Si les compteurs d'émission et de réception augmentent mais que l'application ne répond pas, examine les règles internes, les routes, DNS, le service cible et les pare-feu hôtes.

Vérifie que les adresses sources et destinations du test correspondent aux sélecteurs ou à la route de tunnel. Un test depuis le mauvais VLAN ou une source qui n'est pas incluse dans la politique peut ne pas déclencher IPsec. Un test ping seul peut être trompeur si ICMP est bloqué ou si le service ne répond pas à ICMP.

## 22. Dépanner l'accès distant d'un utilisateur

Commence par savoir si l'utilisateur ne peut pas s'authentifier, si le client ne peut pas établir le tunnel, si le tunnel est établi sans accès aux ressources ou si une seule application échoue. Chaque symptôme correspond à des couches différentes.

Pour un échec d'authentification, vérifie l'identité, MFA, l'horloge, le certificat, l'état du compte et les journaux d'identité. Pour un tunnel inactif, examine les versions client, le réseau local, les paramètres de passerelle et les certificats. Pour un tunnel établi mais une application indisponible, vérifie l'adresse attribuée, les routes, DNS, les ACL et la politique par rôle.

Compare avec un compte et un appareil de référence autorisés. Ne copie pas l'identité ou le certificat d'un collègue. Évite de désactiver MFA ou les contrôles de posture comme solution temporaire. Si un accès d'urgence est nécessaire, fais-le via une procédure approuvée et limitée dans le temps.

## 23. Plan de déploiement

Un déploiement fiable commence par le besoin métier, l'inventaire des réseaux et le modèle de confiance. Définis les ressources accessibles, les utilisateurs ou sites concernés, l'authentification, la méthode de chiffrement, le plan d'adressage, le DNS, les routes, le NAT, les règles de filtrage et les exigences de disponibilité.

Teste d'abord deux hôtes et deux réseaux non sensibles. Valide la connectivité, le refus des flux non autorisés, les journaux, la perte temporaire du tunnel, la révocation d'un compte et le comportement de reprise. Élargis ensuite à un groupe pilote, recueille les problèmes, et déploie de façon progressive avec une méthode de retrait.

Documente les responsabilités pour la passerelle, le fournisseur d'identité, le client, les certificats, les routes et le pare-feu. Les problèmes VPN sont souvent transverses : le réseau, l'identité, les systèmes et l'application peuvent tous contribuer. Un propriétaire unique du dépannage doit coordonner l'analyse sans effacer les frontières de responsabilité.

## 24. Réponse à incident VPN

Si un compte VPN est soupçonné d'être compromis, identifie les sessions actives et les ressources atteintes. Selon la procédure, révoque l'accès, désactive l'identité, retire ou révoque le certificat/jeton, termine les sessions existantes et conserve les journaux utiles. Changer un mot de passe ne garantit pas que les sessions actuelles sont terminées.

Si une passerelle est vulnérable ou compromise, coordonne une réponse avec les responsables réseau et sécurité. Préserve les configurations et logs, vérifie les versions et les accès administratifs, applique les correctifs via une procédure et analyse les routes et politiques. Une passerelle compromise peut fournir un chemin vers plusieurs réseaux ; la réponse doit considérer les ressources derrière le tunnel.

Après incident, recherche la cause racine : MFA absent, secret partagé, certificat non révoqué, terminal non maintenu, route trop large, accès d'administration trop permissif ou absence d'alerte. Corrige la cause et teste les contrôles. Documente ce qui est prouvé, les hypothèses, la portée et les mesures restantes.

## 25. Exercices corrigés

### Exercice 1 — Site-to-Site ou accès distant ?

Deux bureaux doivent communiquer entre leurs sous-réseaux de façon permanente. Quel modèle convient généralement ?

**Correction :** un VPN Site-to-Site, si les passerelles et les réseaux le permettent. Il relie les réseaux à travers leurs équipements de bordure, tandis que l'accès distant est destiné à relier un terminal individuel à une passerelle.

### Exercice 2 — Le tunnel est établi mais l'application échoue

Cite quatre causes possibles au-delà de la négociation IKE.

**Correction :** routes absentes ou asymétriques, sélecteurs incorrects, ACL de filtrage, mauvaise exemption NAT, pare-feu hôte, DNS ou application à l'arrêt. Il faut vérifier les compteurs et le chemin du flux avant de modifier la négociation.

### Exercice 3 — Un utilisateur VPN est administrateur de tout le réseau

Pourquoi est-ce risqué ?

**Correction :** la connexion VPN ne doit pas conférer automatiquement un accès privilégié. Applique une politique par rôle, une zone de gestion séparée et une authentification forte. Autorise seulement les systèmes et ports nécessaires à la fonction de l'utilisateur.

### Exercice 4 — Certificat expiré

Que faut-il examiner ?

**Correction :** date d'expiration, heure système, chaîne de confiance, nom attendu, renouvellement et éventuelle révocation. Prévois des alertes avant l'expiration pour éviter une panne.

### Exercice 5 — Split tunnel

Quelle différence avec un full tunnel ?

**Correction :** en split tunnel, seuls les réseaux ou destinations sélectionnés passent par le VPN, tandis que d'autres flux sortent directement par le réseau local. En full tunnel, le trafic sélectionné pour le tunnel inclut généralement l'accès Internet selon la politique. Chacun a des implications de sécurité, de performance et de supervision.

### Exercice 6 — Réseaux qui se chevauchent

Deux sites utilisent le même sous-réseau. Pourquoi est-ce problématique ?

**Correction :** les routes et sélecteurs deviennent ambigus ; un poste ne distingue pas facilement une destination locale de celle du site distant. Renumérote si possible. Si ce n'est pas réalisable, conçois explicitement une solution de traduction ou de proxy compatible avec les équipements.

### Exercice 7 — Les compteurs sortants augmentent mais les entrants restent à zéro

Quelles pistes examiner ?

**Correction :** vérifier le pair distant, le transport, le filtrage entre les pairs, la politique du site distant et le chemin retour. Si la phase IKE est établie, ne conclus pas que toutes les politiques de données sont correctes.

### Exercice 8 — DNS interne échoue, DNS public fonctionne

**Correction :** vérifie les paramètres DNS poussés au client, la route vers le résolveur interne, les suffixes DNS et les règles qui permettent la requête. Un tunnel actif ne garantit pas que le client utilise le bon serveur DNS.

### Exercice 9 — Pourquoi la PSK doit-elle être unique ?

**Correction :** la réutilisation multiplie l'impact d'une fuite. Une PSK longue et unique par relation est plus facile à révoquer de façon ciblée ; pour un déploiement à nombreux pairs, les certificats peuvent mieux soutenir le cycle de vie d'identité.

### Exercice 10 — Une règle NAT doit-elle s'appliquer aux réseaux du VPN ?

**Correction :** selon l'architecture, le trafic destiné au réseau distant doit souvent être exclu de la traduction Internet pour préserver les adresses attendues. Vérifie sélecteurs, routes, ordre NAT et règles ; l'exemption ne remplace pas le filtrage.

## 26. Défi final — relier deux sites et des utilisateurs distants

### Contexte

Le siège dispose du réseau 192.168.10.0/24 et d'un réseau d'administration 192.168.40.0/24. Le site distant possède 10.20.0.0/16. Les employés nomades doivent accéder à une application du siège, mais pas à l'interface de gestion des équipements. Les deux sites doivent échanger les flux métier et maintenir le trafic Internet selon leur politique de sécurité.

### Correction détaillée

**Étape 1 — Définir le périmètre.** Inventorie les réseaux, hôtes, services, passerelles, routes et propriétaires. Confirme que les préfixes ne se chevauchent pas et que les clients VPN utilisent un pool qui n'entre pas en conflit avec les réseaux locaux usuels.

**Étape 2 — Choisir les modèles.** Utilise un tunnel Site-to-Site entre les passerelles pour le trafic entre les deux bureaux, et une solution d'accès distant pour les employés nomades. Les deux modèles ne sont pas interchangeables : ils présentent des identités, routes et règles distinctes.

**Étape 3 — Définir l'authentification.** Choisis des paramètres cryptographiques maintenus et une authentification robuste des pairs. Les certificats peuvent simplifier la gestion d'identité à grande échelle ; une PSK doit être unique, forte et stockée correctement. Pour les utilisateurs, impose MFA et un contrôle de posture lorsque le modèle le permet.

**Étape 4 — Construire les routes et sélecteurs.** Définis les réseaux autorisés à se joindre par le tunnel. Vérifie les routes aller et retour. Assure-toi que l'ACL ou la politique de sélection IPsec vise les bons préfixes. Utilise une exemption NAT pour les flux du tunnel si la plateforme et l'architecture l'exigent.

**Étape 5 — Appliquer le moindre privilège.** Autorise les employés distants vers l'application utile, mais refuse les interfaces d'administration. Réserve le réseau de gestion aux comptes et appareils autorisés. Le site distant ne doit pas accéder automatiquement à toutes les zones du siège.

**Étape 6 — Choisir le routage d'accès distant.** Décide explicitement si le client utilise un full tunnel ou un split tunnel. Configure les routes, le DNS, les suffixes et la journalisation associés. Vérifie que le choix correspond au risque et aux besoins de performance.

**Étape 7 — Tester.** Vérifie l'établissement IKE, les associations IPsec, les compteurs d'encapsulation/décapsulation, la route retour et les règles de pare-feu. Teste l'application depuis un hôte autorisé du site distant, un utilisateur VPN permis et une source qui doit être refusée.

**Étape 8 — Préparer la continuité et la révocation.** Teste la perte et le rétablissement du tunnel, la rotation de secret ou le renouvellement de certificat et la révocation d'un utilisateur. Confirme comment terminer les sessions actives lors d'un incident.

**Étape 9 — Documenter et surveiller.** Note les paramètres, propriétaires, routes, groupes, journaux, alertes et plans de retour arrière. Revois les droits périodiquement et retire les accès devenus inutiles.

Le défi est réussi si les deux sites échangent uniquement les flux prévus, l'utilisateur distant accède à son application sans obtenir les privilèges du réseau d'administration, le trafic suit les routes attendues et les refus peuvent être justifiés à partir des journaux.

## 27. Checklist de validation

Avant de déclarer un VPN opérationnel, vérifie :
- les identités des pairs et l'authentification ;
- les algorithmes et versions maintenus ;
- les certificats, dates, chaîne de confiance et révocation le cas échéant ;
- les réseaux locaux et distants ainsi que les chevauchements ;
- les routes dans les deux sens ;
- les sélecteurs ou l'interface de tunnel et le modèle de routage ;
- le traitement NAT et les exemptions nécessaires ;
- les règles de pare-feu sur les passerelles et les hôtes ;
- le DNS et les routes poussées aux clients ;
- le choix full tunnel ou split tunnel ;
- les journaux, alertes et synchronisation horaire ;
- le test d'accès autorisé et de refus d'accès ;
- la procédure de révocation et de coupure de session ;
- le plan de retour arrière et le propriétaire opérationnel.

Cette checklist ne remplace pas la documentation du fabricant, mais elle évite de déclarer le tunnel opérationnel parce que la seule négociation cryptographique a réussi.

## 28. Glossaire

**VPN :** réseau privé virtuel qui protège un chemin de communication selon un protocole et une configuration.

**Site-to-Site :** VPN reliant généralement deux passerelles et les réseaux derrière elles.

**Accès distant :** VPN reliant un terminal individuel à une passerelle de l'organisation.

**IPsec :** suite de protocoles qui sécurise les paquets IP.

**ESP :** mécanisme IPsec fréquemment utilisé pour protéger la charge utile du tunnel.

**IKE / IKEv2 :** mécanismes de négociation et de gestion des associations de sécurité pour IPsec.

**SA :** association de sécurité contenant des paramètres utilisés pour traiter le trafic protégé.

**PSK :** clé prépartagée, secret configuré sur les deux pairs.

**Certificat :** document signé qui lie une identité à une clé publique selon une chaîne de confiance.

**MFA :** authentification multifacteur.

**Sélecteur :** critère décrivant le trafic associé à une politique VPN dans certains modèles.

**Full tunnel :** modèle où le trafic défini, souvent l'ensemble du trafic IP du client, est acheminé via le VPN.

**Split tunnel :** modèle où seuls certains réseaux ou destinations utilisent le VPN.

**Exemption NAT :** règle qui préserve les adresses pour certains flux au lieu de les traduire.

**MTU / MSS :** tailles maximales utiles pour un paquet IP et un segment TCP.

**DMZ :** zone réseau séparée où sont placés certains services exposés.

**Retour arrière :** procédure qui restaure une configuration connue après un changement problématique.

## 29. Références officielles

- RFC 4301, Security Architecture for the Internet Protocol : https://www.rfc-editor.org/rfc/rfc4301
- RFC 7296, Internet Key Exchange Protocol Version 2 (IKEv2) : https://www.rfc-editor.org/rfc/rfc7296
- NIST SP 800-77 Rev. 1, Guide to IPsec VPNs : https://csrc.nist.gov/pubs/sp/800/77/r1/final
- NIST SP 800-46 Rev. 2, Guide to Enterprise Telework, Remote Access, and BYOD Security : https://csrc.nist.gov/pubs/sp/800/46/r2/final
- Cisco, guides de configuration IPsec/IKE selon le système : https://www.cisco.com/c/en/us/support/security/next-generation-firewall-ngfw/series.html
- strongSwan, documentation officielle : https://docs.strongswan.org/

Les réglages exacts dépendent du fabricant, de la version, de l'architecture et des exigences de sécurité. Vérifie les recommandations actuelles pour les algorithmes et la version réellement utilisés. Ne déploie pas une configuration de laboratoire directement en production.

Fin du cours.

## 30. Cas de diagnostic et de mise en production

Ces situations complémentaires exercent les réflexes nécessaires pour diagnostiquer un VPN sans confondre négociation, routage, filtrage, identité et application.

### Cas de dépannage 1 — Phase IKE ne s'établit pas

**Analyse.** La connectivité IP entre les pairs peut être absente, les paramètres cryptographiques incompatibles ou l'authentification incorrecte. Vérifie les adresses des pairs, les routes et le filtrage du transport, puis compare les propositions, l'identité attendue, la PSK ou les certificats et l'horloge sur les deux extrémités. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne change pas tous les paramètres à la fois ; cela masque la cause et peut affaiblir la politique. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 2 — IKE est établi mais aucun trafic ne traverse le tunnel

**Analyse.** La négociation ne garantit pas que les sélecteurs, les routes, les ACL et le chemin retour sont corrects. Génère un trafic source-destination inclus dans la politique et observe les compteurs d'encapsulation et de décapsulation. Examine les routes, les sélecteurs et les règles de filtrage aux deux extrémités. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne déclare pas le VPN fonctionnel uniquement parce que l'état IKE est actif. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 3 — Le tunnel ne fonctionne que dans un sens

**Analyse.** La route de retour peut être absente, les sélecteurs asymétriques ou le filtrage d'un site différent de l'autre. Vérifie les routes dans les deux sens, les préfixes locaux/distants négociés et les journaux des deux pairs. Teste une paire d'adresses connue, puis une autre si nécessaire. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne corrige pas seulement l'extrémité qui affiche l'erreur sans vérifier l'autre côté. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 4 — Certificat expiré sur une passerelle

**Analyse.** La négociation peut échouer lorsque le certificat ne se trouve plus dans sa période de validité ou que l'horloge est incorrecte. Vérifie l'heure, l'expiration, la chaîne de confiance, le nom d'identité et l'état de révocation. Renouvelle par le processus approuvé puis valide le tunnel. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne contourne pas durablement la validation du certificat pour rétablir le service. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 5 — PSK copiée sur plusieurs sites

**Analyse.** La réutilisation du même secret augmente l'impact d'une fuite et complique la révocation ciblée. Inventorie les pairs qui partagent le secret, crée des secrets uniques et robustes selon les relations et organise une rotation contrôlée. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne transmets pas les secrets dans un ticket public ou une capture d'écran. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 6 — Deux sites utilisent le même préfixe IP

**Analyse.** Les routes vers les réseaux local et distant peuvent être ambiguës ; les hôtes peuvent considérer la destination comme locale. Privilégie une renumérotation planifiée. Si elle est impossible, conçois une solution de traduction ou de proxy explicitement supportée et documente les limites. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne masque pas le chevauchement en ajoutant des routes concurrentes non documentées. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 7 — Utilisateurs connectés mais DNS interne échoue

**Analyse.** Le client peut ne pas recevoir le bon résolveur, la route DNS peut manquer ou le suffixe interne peut être incorrect. Vérifie les paramètres poussés au client, l'adresse du résolveur, les routes et les règles vers DNS. Teste séparément résolution interne et publique. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne change pas le DNS de tous les clients sans connaître la politique du VPN. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 8 — Split tunnel ne route pas un sous-réseau précis

**Analyse.** Le préfixe peut manquer dans la liste de routes, se chevaucher avec un réseau local ou être ignoré par le client. Inspecte la table de routage effective sur le client, les routes poussées et les politiques du concentrateur. Vérifie les préfixes et la passerelle attendue. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne suppose pas que la connexion VPN installe automatiquement toutes les routes internes. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 9 — Full tunnel provoque une baisse de performance

**Analyse.** Le trafic Internet du client passe par le concentrateur, ce qui peut saturer la bande passante ou augmenter la latence. Mesure débit, latence, charge du concentrateur, perte de paquets et chemin Internet. Compare avec la capacité prévue et vérifie les dépendances DNS et MTU. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne passe pas immédiatement en split tunnel sans analyser les conséquences de sécurité. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 10 — Une application se bloque avec des transferts volumineux

**Analyse.** L'encapsulation peut diminuer la MTU utile ; certains paquets peuvent être trop grands ou les messages de découverte bloqués. Compare les petits et grands transferts, examine les messages ICMP utiles et applique les recommandations MTU/MSS de la plateforme après mesure. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne désactive pas tous les contrôles réseau pour résoudre un problème de taille. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 11 — Le tunnel tombe après rotation de clé

**Analyse.** Les pairs peuvent ne pas utiliser la même configuration ou un changement a pu toucher une association active. Compare la procédure de rotation et les paramètres des deux côtés, vérifie l'heure et les journaux, puis rétablis une configuration cohérente avec le plan d'accès de secours. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne reviens pas à un algorithme faible simplement pour faire établir le tunnel. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 12 — MFA fonctionne mais les ressources restent inaccessibles

**Analyse.** L'identité a été validée mais le groupe, le pool d'adresses, les routes ou la politique d'accès peuvent être incorrects. Vérifie les attributs de groupe, l'adresse VPN attribuée, les règles par rôle et le chemin vers le serveur cible. Compare avec un utilisateur de référence autorisé. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne donne pas à tout le pool VPN les droits d'un administrateur pour corriger un accès limité. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 13 — Un utilisateur parti conserve une session active

**Analyse.** La révocation du compte ou du secret ne met pas nécessairement fin à toutes les sessions déjà établies. Désactive l'identité, termine les sessions actives selon la plateforme, révoque certificat ou jeton si nécessaire et examine les journaux d'accès. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne considère pas le changement de mot de passe comme preuve que les sessions existantes sont terminées. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 14 — Passerelle VPN non corrigée

**Analyse.** Un logiciel obsolète peut contenir des vulnérabilités connues, surtout lorsque le portail est exposé à Internet. Inventorie la version, consulte les avis officiels du fournisseur, prépare une fenêtre et un retour arrière puis applique les correctifs approuvés. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne laisse pas une interface publique sans maintenance au seul motif que le tunnel fonctionne. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 15 — Les compteurs d'émission augmentent mais pas la réception

**Analyse.** Les paquets peuvent être perdus en chemin, filtrés chez le pair distant ou envoyés vers une mauvaise route. Vérifie la connectivité entre pairs, les protocoles du tunnel, les règles amont/aval, l'adresse distante et le trafic de retour. Corrèle les journaux des deux extrémités. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne conclus pas que le chiffrement local est en cause sans examiner le chemin externe. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 16 — Les compteurs augmentent dans les deux sens mais l'application échoue

**Analyse.** Le tunnel transporte des paquets, mais l'application peut être arrêtée, DNS incorrect ou le pare-feu hôte peut refuser le flux. Teste l'application, l'adresse et le port, consulte les journaux du serveur et contrôle les règles internes, routes et permissions. Vérifie aussi les noms et certificats. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne continue pas de modifier IKE lorsque les preuves montrent que les paquets atteignent les réseaux internes. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 17 — Un réseau VPN atteint le réseau d'administration sans besoin

**Analyse.** La politique de filtrage ou le routage accorde des droits trop larges aux utilisateurs distants. Sépare le pool VPN de la zone de gestion, limite les flux par rôle et n'autorise l'administration que depuis des appareils et identités approuvés. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne considère pas le tunnel comme un périmètre de confiance suffisant. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 18 — Le pare-feu local bloque le trafic après connexion

**Analyse.** Le client peut avoir reçu un nouveau profil réseau ou une politique locale qui restreint les connexions. Examine le profil actif, les règles hôtes et les journaux du système, puis autorise uniquement l'application et le réseau requis selon la politique. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne désactive pas totalement le pare-feu hôte pour faire fonctionner le VPN. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 19 — NAT modifie la source des flux du VPN

**Analyse.** La règle de sortie Internet peut être appliquée avant l'exemption du trafic destiné au site distant. Vérifie l'ordre NAT, les adresses vues par IPsec, les sélecteurs et la règle d'exemption. Compare avec le trafic réel dans la table de traduction. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne crée pas une exemption NAT universelle qui affecte tout le trafic sortant. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 20 — La négociation échoue après changement d'algorithmes

**Analyse.** Les deux pairs peuvent ne pas avoir de proposition commune ou les suites ne sont pas configurées de façon cohérente. Compare les propositions, groupes de clés, durées de vie, version IKE et méthodes d'authentification aux deux extrémités. Choisis un ensemble pris en charge et maintenu. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne réactive pas des suites obsolètes sans évaluation et exception formelle. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 21 — Le VPN fonctionne sur le réseau domestique mais pas sur Wi-Fi public

**Analyse.** Le réseau public peut filtrer certains protocoles ou ports ; le client peut aussi être affecté par un proxy ou une politique locale. Vérifie les messages client, les protocoles de transport prévus par la solution et les exigences du fournisseur VPN. Utilise uniquement les méthodes de connexion approuvées. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne tente pas de contourner la sécurité du réseau public ni d'utiliser un service VPN inconnu. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 22 — Le tunnel tombe après redémarrage d'un routeur

**Analyse.** La configuration courante n'a pas été sauvegardée, la route ou l'association de sécurité ne se rétablit pas, ou l'identité/certificat n'est plus disponible. Compare la configuration de démarrage, les interfaces, routes, certificats, services et journaux. Teste la reprise dans une fenêtre planifiée. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne sauvegarde pas aveuglément une configuration qui n'a pas été validée. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 23 — Le client VPN reçoit une adresse déjà utilisée sur le LAN

**Analyse.** Le pool de clients chevauche un réseau local fréquent ou le sous-réseau de l'organisation. Choisis un pool documenté, évite les chevauchements connus et teste depuis plusieurs réseaux externes représentatifs. Vérifie les routes après connexion. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne laisse pas un adressage ambigu qui fonctionne uniquement depuis certains réseaux. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 24 — Une passerelle secondaire ne prend pas le relais

**Analyse.** Les paramètres, routes, certificats ou états ne sont pas synchronisés, ou le client ne connaît pas le pair secondaire. Vérifie le mécanisme HA, les tests de basculement, la résolution du nom, les règles et la capacité du secondaire. Valide les nouveaux tunnels et les accès métier. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne considère pas la présence d'une seconde appliance comme preuve de continuité. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 25 — Les journaux ne permettent pas de rattacher un accès à une identité

**Analyse.** Les journaux VPN, d'identité et d'application peuvent avoir des horloges différentes ou manquer d'attributs utiles. Synchronise les horloges et corrèle utilisateur, appareil, adresse VPN, heure et service accédé, en respectant la politique de confidentialité. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne stocke pas les secrets dans les logs pour augmenter artificiellement leur détail. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 26 — Un certificat utilisateur fonctionne sur plusieurs appareils sans contrôle

**Analyse.** La clé privée ou le certificat peut avoir été exporté ou partagé au-delà de l'usage prévu. Évalue la protection de la clé, les règles d'enrôlement, la révocation, l'association à l'appareil et le MFA. Remplace les certificats exposés selon la procédure. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne distribue pas un même fichier de clé privée à tous les employés. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 27 — Le site distant accède à plus de réseaux que prévu

**Analyse.** Les sélecteurs, routes ou règles permettent un accès trop large entre les deux sites. Rédige les flux nécessaires, limite les réseaux annoncés et teste des destinations internes qui doivent rester bloquées. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne remplace pas une segmentation par une confiance implicite dans le tunnel. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 28 — Le tunnel est instable uniquement à forte charge

**Analyse.** La capacité cryptographique, la bande passante, les sessions, la perte ou la fragmentation peuvent être en cause. Mesure CPU, sessions, débit, perte, latence et paramètres MTU pendant la charge. Compare avec les limites publiées du matériel. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne change pas de suites cryptographiques au hasard pour corriger une saturation. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 29 — Un compte échoue après un changement de groupe

**Analyse.** L'attribut d'autorisation, la synchronisation d'identité ou la politique de rôle ne s'est pas propagé comme attendu. Vérifie l'identité, les groupes, les journaux du fournisseur d'identité et les droits associés au profil VPN. Teste l'accès avec un compte de référence. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne donne pas un groupe plus privilégié par simple commodité. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 30 — Le VPN est déclaré actif mais la route de retour est absente

**Analyse.** Le paquet peut être déchiffré au site distant, mais la réponse suit une autre passerelle ou ne sait pas revenir vers le pool distant. Vérifie les routes du réseau cible, la route de retour vers le pool de clients et les politiques de sécurité des deux côtés. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne diagnostique pas uniquement le tunnel ; examine aussi le routage et les pare-feu internes. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

### Cas de dépannage 31 — Un ancien tunnel reste configuré après la fin d'un partenariat

**Analyse.** Une relation et ses secrets peuvent continuer d'autoriser un accès inutile. Confirme la fermeture du besoin, coupe le tunnel suivant le processus, retire les routes, sélecteurs, comptes, certificats et règles associées puis vérifie les journaux. Commence par consigner l'heure, la source, la destination, le message d'erreur et les changements récents. Modifie un paramètre à la fois afin de savoir quelle action a eu un effet.

**Erreur à éviter.** Ne laisse pas des configurations VPN dormantes sans propriétaire et sans date de revue. Après correction, reteste l'accès autorisé et un accès qui doit rester refusé. Note la cause racine, l'action, le propriétaire et la date de revue.

Fin du cours.