# Introduction aux pare-feu

> **Mise en contexte**
>
> Une entreprise possède des postes utilisateurs, des serveurs, un réseau Wi-Fi invité et des services accessibles depuis Internet. Tous ces systèmes communiquent, mais ils n'ont pas tous besoin de communiquer entre eux. Un poste utilisateur ne devrait pas administrer un routeur, un invité ne devrait pas lire une base de données interne et un serveur Web public ne devrait pas atteindre librement les ressources internes.
>
> Le pare-feu applique une politique de filtrage qui autorise les communications nécessaires et bloque les autres. Son efficacité dépend de la précision des règles, de leur ordre, de leur validation et de leur maintenance. Ce cours présente les familles de pare-feu, la lecture de règles, le routage et le NAT, la segmentation, les commandes de diagnostic Windows et Linux et une méthode de dépannage.
>
> Les manipulations doivent se faire sur un équipement autorisé. Ne modifie pas à l'aveugle un pare-feu de production ou un serveur administré à distance : une règle incorrecte peut couper l'accès nécessaire au dépannage.

## 1. Objectifs et prérequis

À la fin de ce cours, tu sauras expliquer le rôle du pare-feu, distinguer pare-feu hôte et réseau, comprendre le filtrage sans état et avec état, lire les critères d'une règle, interpréter les politiques par défaut, distinguer routage, NAT et filtrage, examiner Windows Defender Firewall et UFW/nftables, puis construire une méthode de dépannage fondée sur des preuves. Les notions utiles sont les adresses IP, les ports TCP/UDP, les routes, la passerelle et DNS.

## 2. Définition et rôle

Un pare-feu est un composant matériel, logiciel ou virtuel qui contrôle les communications entre une machine, une interface ou plusieurs réseaux selon une politique. Il peut autoriser, bloquer ou rejeter un flux, et enregistrer certains événements si la journalisation est configurée.

~~~text
Internet
   |
   v
[ Pare-feu réseau ]
   |             |
   v             v
Serveur Web   Réseau interne
TCP/443       flux limités
~~~

Un pare-feu réduit les possibilités d'accès à un service et peut séparer les zones. Il ne prouve pas qu'un service autorisé est sain, que l'utilisateur est légitime ou que l'application n'a pas de vulnérabilité. Il ne remplace ni les mises à jour, ni l'antivirus/EDR, ni les contrôles d'identité ni les sauvegardes.

Un pare-feu hôte protège la machine elle-même. Un pare-feu réseau filtre les communications entre interfaces ou zones. La combinaison des deux peut être utile : les échanges entre deux machines du même segment ne traversent pas nécessairement le pare-feu périmétrique.

## 3. Comprendre un flux

Pour décrire une communication, identifie l'adresse IP source, l'adresse IP destination, le protocole, les ports applicables, la direction, l'interface ou la zone et éventuellement l'état de connexion. Certains produits ajoutent l'application, l'utilisateur, la réputation de destination ou d'autres critères.

Exemple pédagogique :

~~~text
Source       : 192.0.2.50
Destination  : 198.51.100.20
Protocole    : TCP
Port source  : 53124
Port cible   : 443
Objectif     : connexion HTTPS
~~~

Les adresses sont réservées à la documentation. Le client emploie souvent un port source éphémère et se connecte au port de service du serveur. Il faut distinguer le port source du port de destination. Une règle qui vise TCP/443 vers le serveur n'ouvre pas automatiquement tous les ports du serveur.

TCP est orienté connexion. UDP ne dispose pas du même établissement de connexion, mais un pare-feu à états peut suivre temporairement ses échanges. ICMP porte des messages de contrôle IP et ne possède pas de ports TCP/UDP. Quelques conventions utiles : SSH utilise souvent TCP/22, HTTP TCP/80, HTTPS souvent TCP/443, SMB TCP/445, le bureau à distance Windows souvent TCP/3389 et NTP généralement UDP/123. DNS utilise généralement UDP/53 et peut employer TCP/53. Le port n'est pas une preuve absolue de la nature d'un service.

## 4. Principales familles

Un filtre de paquets simple regarde des caractéristiques comme les adresses, le protocole et les ports. Il peut autoriser TCP/443 vers un serveur et refuser les communications qui ne correspondent pas. Un filtre sans état ne conserve pas nécessairement le contexte complet d'une session.

Un pare-feu à états suit les communications. Il peut reconnaître un paquet de retour comme appartenant à une connexion autorisée. Cela n'implique pas que toute nouvelle connexion dans le sens opposé sera permise.

Un pare-feu hôte s'exécute sur un terminal ou serveur. Il peut appliquer des règles entrantes et sortantes et rester utile lorsqu'un trafic ne traverse pas le dispositif périmétrique. Windows Defender Firewall et le filtrage de Netfilter sous Linux sont des exemples.

Un pare-feu réseau contrôle les flux entre interfaces ou zones, par exemple entre Internet, les utilisateurs et les serveurs. Un proxy relaie des communications applicatives et peut imposer une authentification ou une politique sur ces requêtes. Un WAF se concentre sur certaines attaques visant des applications Web et complète, sans le remplacer, le filtrage réseau.

Un NGFW associe des fonctions selon le produit : filtrage avec état, identification applicative, prévention d'intrusion ou renseignements sur les menaces. Le nom commercial n'est pas une preuve de sécurité. Vérifie les fonctions activées, les exceptions, les mises à jour et les limites d'inspection, notamment lorsque le trafic est chiffré.

## 5. Lire une règle

Une règle correcte décrit le besoin précis, l'origine, la destination, le protocole, le port ou service, la direction, la zone et l'action.

~~~text
Nom         : Utilisateurs_vers_Web_HTTPS
Source      : 192.168.10.0/24
Destination : 192.168.20.10
Protocole   : TCP
Port cible  : 443
Action      : Autoriser
Justification : accès à une application interne
~~~

Cette règle vise le flux décrit, sous réserve des autres paramètres et règles de la plateforme. Elle n'autorise pas automatiquement tous les ports du serveur. Toute exception doit avoir une justification et un propriétaire.

**Autoriser** laisse passer le trafic correspondant. **Bloquer silencieusement** abandonne généralement le paquet. **Rejeter** peut envoyer une indication de refus. Le choix varie selon le produit et le contexte. Le rejet peut faciliter le diagnostic, tandis que le silence peut limiter certaines informations renvoyées à l'émetteur.

### Ordre et priorités

Certains moteurs appliquent la première règle correspondante ; d'autres utilisent des priorités, groupes ou objets. Une règle large placée avant un refus spécifique peut masquer ce refus si le moteur s'arrête à la première correspondance. Il faut consulter la documentation du produit et examiner la politique complète.

Exemple :

~~~text
Règle 1 : autoriser toutes les connexions vers le serveur
Règle 2 : bloquer SSH vers ce serveur
~~~

Si la première règle l'emporte, la seconde peut ne pas avoir l'effet attendu. L'analyse doit aussi rechercher les règles redondantes, anciennes, temporaires et les exceptions dont le propriétaire n'est plus connu.

## 6. Politique par défaut et moindre privilège

La politique par défaut détermine l'action lorsque le trafic ne correspond à aucune règle qui décide autrement. Une approche courante consiste à refuser les nouvelles connexions entrantes non autorisées et à n'ouvrir que les services nécessaires. La politique sortante dépend du risque et de la capacité de maintenir les dépendances des applications.

Le moindre privilège signifie qu'une machine ou une zone ne reçoit que les capacités réseau nécessaires. Une règle autorisant toutes les sources, toutes les destinations et tous les ports peut annuler la segmentation et exposer des services inutiles. Préfère les sources et destinations précises, un protocole et des ports justifiés, ainsi qu'une date de revue pour les exceptions.

Le refus par défaut doit être préparé. Il faut inventorier les dépendances, prévoir DNS, la synchronisation horaire, les mises à jour et les API nécessaires. Sans cette préparation, la politique peut provoquer une panne et inciter à contourner les contrôles.

Le filtrage sortant mérite aussi une réflexion : un poste dont les connexions entrantes non sollicitées sont bloquées peut toujours initier des connexions vers Internet. Une politique sortante stricte peut limiter les communications d'un logiciel compromis, mais elle exige des tests et un inventaire des destinations nécessaires.

## 7. Entrant, sortant et transféré

Le trafic **entrant** arrive d'un autre réseau vers un hôte ou une zone. Le trafic **sortant** est initié par un hôte vers une destination. Le trafic **transféré** traverse un routeur ou pare-feu pour rejoindre un autre réseau.

Ces catégories ne sont pas interchangeables. Les règles qui protègent les connexions entrantes d'un serveur ne décrivent pas nécessairement les communications qu'il initie. Sous Linux, le trafic destiné à la machine elle-même peut passer par des chaînes différentes de celles du trafic routé.

Un test précis doit indiquer la source réelle, la destination, le protocole et le port, le sens et le chemin. Il ne suffit pas de dire « ouvrir HTTPS » sans savoir depuis quel réseau, vers quel service et pour quelle raison.

## 8. Routage, NAT et filtrage

Le routage choisit le prochain saut d'un paquet. Le NAT traduit des adresses IP, et certaines formes de NAT traduisent aussi les ports. Une traduction d'adresses n'est pas une politique complète de sécurité. Certains équipements combinent traduction et filtrage, d'où la nécessité de vérifier les deux fonctions séparément.

Pour diagnostiquer un flux, examine l'adressage, la route, l'adresse finale après traduction, le protocole, le port et les règles. Une redirection de port peut exposer un service interne à un réseau externe ; elle doit être documentée et limitée.

Ne considère pas qu'un équipement est sûr simplement parce qu'il utilise une adresse privée. Les services peuvent être accessibles depuis le réseau local ou à travers une traduction. La sécurité vient de la politique d'accès, pas du seul plan d'adressage.

## 9. Segmentation, VLAN et DMZ

La segmentation sépare les équipements en zones : utilisateurs, serveurs, invités, administration et DMZ. Un VLAN crée un domaine logique de niveau 2, mais le routage entre VLAN peut permettre des communications ; il faut donc appliquer un filtrage approprié.

Les invités devraient pouvoir accéder à Internet tout en étant isolés des sous-réseaux internes. Les postes utilisateurs accèdent aux applications prévues, pas à toutes les interfaces de gestion. Les serveurs sensibles ne devraient être joignables que par les clients qui en ont besoin.

La DMZ héberge souvent les services accessibles depuis Internet. Si un serveur Web dépend d'une base de données interne, autorise le serveur applicatif vers la base sur le seul port requis et refuse le reste des communications de la DMZ vers le réseau interne. Teste les flux depuis un client dans chaque zone.

## 10. IPv4, IPv6 et ICMP

Une politique IPv4 correcte ne garantit pas que les communications IPv6 sont filtrées de façon équivalente. Vérifie si IPv6 est actif, les adresses, les routes, les services en écoute et les règles. Ne le désactive pas sans comprendre les dépendances du système.

ICMP sert aux messages de contrôle et de diagnostic. Bloquer absolument tous les messages ICMP peut gêner le diagnostic ou des mécanismes comme la découverte de la MTU. Il faut autoriser les messages nécessaires selon l'architecture et le risque, sans ouvrir toutes les communications.

## 11. Journalisation

Les journaux peuvent renseigner l'heure, la source, la destination, le protocole, les ports, la règle appliquée et l'action. Leur détail dépend du produit. Ils peuvent aider à déterminer où un flux est bloqué et à corréler une panne avec une modification.

Un refus isolé ne prouve pas une attaque. Il peut correspondre à un client mal configuré, un flux attendu mais non documenté ou une activité non autorisée. Regroupe les événements par source, destination, fréquence, horaire et service, puis compare avec les activités légitimes.

La journalisation doit être équilibrée : collecter chaque paquet peut générer trop d'événements, alors que ne rien journaliser rend les diagnostics difficiles. Protège l'accès aux journaux, fixe la rétention et évite de collecter des données sensibles inutiles. Pour les flux critiques, vérifie que l'horloge est correcte et que les événements peuvent être corrélés.

## 12. Windows Defender Firewall : commandes de lecture

Les profils courants de Windows comprennent Domaine, Privé et Public. Un profil décrit une catégorie de réseau ; il ne garantit pas à lui seul qu'un réseau est digne de confiance.

Pour afficher l'état des profils :

~~~powershell
Get-NetFirewallProfile |
    Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
~~~

Pour examiner les règles activées :

~~~powershell
Get-NetFirewallRule -Enabled True |
    Select-Object DisplayName, Direction, Action, Profile
~~~

Pour examiner les règles entrantes :

~~~powershell
Get-NetFirewallRule -Enabled True -Direction Inbound |
    Select-Object DisplayName, Action, Profile
~~~

Pour afficher les filtres de ports :

~~~powershell
Get-NetFirewallRule -Enabled True | Get-NetFirewallPortFilter
~~~

Pour les filtres d'adresses :

~~~powershell
Get-NetFirewallRule -Enabled True | Get-NetFirewallAddressFilter
~~~

Pour consulter les paramètres plus globaux des profils :

~~~powershell
netsh advfirewall show allprofiles
~~~

Ces commandes sont destinées à la lecture. Les résultats doivent être interprétés ensemble : un filtre de port isolé ne prouve pas qu'un service est accessible. Le profil actif, les autres filtres, la politique centralisée et le chemin réseau comptent aussi.

## 13. Linux : UFW, nftables et ports à l'écoute

Sur Ubuntu avec UFW, les commandes suivantes consultent l'état et les règles :

~~~bash
sudo ufw status verbose
sudo ufw status numbered
~~~

Si le système utilise nftables, on peut afficher le jeu de règles :

~~~bash
sudo nft list ruleset
~~~

Pour examiner les sockets en écoute :

~~~bash
sudo ss -lntup
~~~

Ces commandes sont principalement des commandes de lecture. Si UFW est inactif, cela ne prouve pas que l'hôte est dépourvu d'autres règles. Identifie le mécanisme qui gère réellement les règles avant de modifier quoi que ce soit.

Un service en écoute n'est pas nécessairement accessible depuis l'extérieur. Il faut examiner son adresse d'écoute, le pare-feu hôte, les routes et le filtrage réseau. De même, un service inaccessible peut être arrêté plutôt que bloqué par une règle.

## 14. Modification prudente et retour arrière

Avant un changement, clarifie le besoin, repère la règle et l'équipement concernés, vérifie les dépendances et sauvegarde la configuration pertinente. Prépare un accès de secours si tu administres la machine à distance. Définis une fenêtre de changement, les tests de validation et une procédure de retour arrière.

Après la modification, confirme que le flux voulu fonctionne et que les flux interdits restent refusés. Consulte les journaux, documente le résultat et retire les règles temporaires lorsque leur besoin s'achève. Une règle doit avoir une justification, un responsable et une date de révision.

Ne vide pas toutes les règles pour « repartir de zéro ». Une modification destructive peut couper une session ou supprimer une protection gérée par un autre outil. Les outils de configuration peuvent réécrire les règles automatiquement ; il faut identifier le propriétaire de la politique.

## 15. Méthode de dépannage

1. Précise le symptôme, la source, la destination, le port, le protocole et l'heure.
2. Vérifie le nom DNS, l'adresse IP, le masque, la passerelle et la route.
3. Confirme que le service fonctionne et écoute sur la bonne adresse.
4. Examine le pare-feu hôte puis les équipements traversés.
5. Recherche les événements correspondants dans les journaux.
6. Vérifie la direction, la zone, la priorité et l'état de connexion des règles.
7. Formule la correction minimale, puis reteste le flux attendu et les flux interdits.
8. Documente la cause, le changement et le retour arrière éventuel.

Sous Windows, un test TCP ciblé se fait avec :

~~~powershell
Test-NetConnection -ComputerName 192.0.2.20 -Port 443
~~~

L'adresse est documentaire : remplace-la uniquement par le serveur de ton laboratoire autorisé. Un résultat négatif indique que le test TCP n'a pas abouti ; il ne prouve pas que le pare-feu est la cause. Le service peut être arrêté, la route manquante ou un autre équipement impliqué.

Ne désactive pas le pare-feu complet pour dépanner. Identifie la cause avec des commandes de lecture et les journaux, puis teste une modification précise dans un environnement autorisé.

## 16. Laboratoire : politique de filtrage entre zones

Utilise les sous-réseaux fictifs suivants : utilisateurs 192.168.10.0/24, serveurs 192.168.20.0/24, invités 192.168.30.0/24, administration 192.168.40.0/24 et DMZ 192.168.50.0/24.

Les postes utilisateurs doivent accéder aux applications nécessaires ; les invités peuvent accéder à Internet mais pas directement aux réseaux internes ; l'administration est réservée aux sources gérées ; un serveur Web public n'accepte que les services publiés. Si le serveur applicatif a besoin d'une base de données interne, autorise seulement sa source et le port réel requis.

Pour chaque règle, écris source, destination, protocole, port, direction, action et justification. Les besoins inconnus doivent être confirmés par le propriétaire de l'application. Teste depuis un client de chaque zone et vérifie les refus attendus. Si IPv6 est utilisé, valide aussi sa politique.

## 17. Erreurs courantes

Une règle « tout autoriser » peut annuler la segmentation. Une priorité incorrecte peut masquer un refus spécifique. NAT ne remplace pas le filtrage. Une politique entrante stricte ne limite pas automatiquement les connexions sortantes. IPv6 peut avoir des règles différentes. Un port ouvert n'assure pas que l'application est saine. Un refus ne prouve pas une attaque. Un test négatif ne prouve pas que le pare-feu est seul en cause.

Il faut aussi éviter d'ouvrir un service d'administration à tous les utilisateurs parce qu'un poste n'arrive pas à se connecter. Vérifie la source réellement nécessaire, le service, les règles locales et les journaux. Toute exception temporaire devrait avoir un propriétaire et une échéance.

## 18. Exercices corrigés

**1. Quel type de pare-feu protège un portable sur plusieurs réseaux ?** Le pare-feu hôte, complété par les politiques centrales si l'appareil est géré.

**2. Que signifie autoriser TCP/443 vers un serveur ?** Cela autorise le flux correspondant aux critères de la règle, pas tous les ports et pas nécessairement une application saine.

**3. NAT protège-t-il automatiquement un service ?** Non. Il faut vérifier séparément la traduction et les règles de filtrage.

**4. Le ping fonctionne mais SSH échoue.** Vérifie que SSH tourne, son port et son adresse d'écoute, puis le filtrage local et réseau.

**5. Pourquoi une règle tous ports est-elle risquée ?** Elle permet plus que le besoin et peut exposer des services inutiles.

**6. Un refus prouve-t-il une attaque ?** Non. Analyse source, destination, fréquence et contexte.

**7. Un VLAN suffit-il ?** Non. Le routage peut permettre des flux ; vérifie les règles inter-zones.

**8. Pourquoi vérifier IPv6 ?** Les règles IPv4 ne garantissent pas une politique identique pour IPv6.

**9. Que fait nft list ruleset ?** Il affiche les règles nftables sans les modifier.

**10. Quelles précautions avant une modification distante ?** Sauvegarde, accès de secours, fenêtre de changement, tests et retour arrière.

## 19. Défi final

Une petite entreprise possède un réseau utilisateurs 192.168.10.0/24, des serveurs internes 192.168.20.0/24, un réseau invité 192.168.30.0/24, l'administration 192.168.40.0/24 et une DMZ 192.168.50.0/24. Le serveur Web public dépend d'une base de données interne. Les utilisateurs doivent accéder aux applications métier ; les invités doivent accéder à Internet ; l'administration ne doit être ouverte qu'aux sources prévues.

**Correction :** définis l'objectif de chaque zone et vérifie le routage réel ; autorise les protocoles publiés vers le serveur Web ; limite les flux de la DMZ vers la base à la source applicative et au port exact ; restreins l'administration à un réseau ou bastion prévu ; bloque les accès directs des invités vers les zones internes ; journalise les refus importants et les flux sensibles ; prépare une sauvegarde, un accès de secours et un retour arrière ; teste les flux autorisés et les flux interdits depuis des clients réels ; vérifie IPv4 et IPv6 lorsque cela s'applique ; documente chaque règle avec un propriétaire et une date de revue.

La politique est correcte si elle satisfait les besoins métiers sans autorisations générales non justifiées et si le comportement réel correspond aux règles documentées. Si une application échoue, corrige la cause identifiée au lieu d'ouvrir le réseau entier.

## 20. Glossaire et références

**Pare-feu :** dispositif qui contrôle les communications selon une politique. **Règle :** critères de trafic et action. **Stateful :** suivi de l'état d'une connexion. **Trafic transféré :** trafic qui traverse un équipement. **NAT :** traduction d'adresses et parfois de ports. **VLAN :** segment logique de niveau 2. **DMZ :** zone intermédiaire pour services exposés. **Proxy :** intermédiaire applicatif. **WAF :** pare-feu applicatif Web. **NGFW :** pare-feu disposant de fonctions réseau et applicatives avancées. **Moindre privilège :** autoriser uniquement le nécessaire. **Journalisation :** enregistrement d'événements. **Règle masquée :** règle qui ne prévaut pas à cause de l'ordre ou de la priorité. **Retour arrière :** restauration après un changement problématique.

Références officielles :
- Microsoft Learn, Get-NetFirewallProfile : https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallprofile
- Microsoft Learn, configurer Windows Firewall par ligne de commande : https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/configure-with-command-line
- Microsoft Learn, journalisation du pare-feu Windows : https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/configure-the-windows-firewall-log
- Ubuntu Server, pare-feu et UFW : https://documentation.ubuntu.com/server/how-to/security/firewalls/
- NIST SP 800-41 Rev. 1, Guidelines on Firewalls and Firewall Policy : https://csrc.nist.gov/pubs/sp/800/41/r1/final

Les options dépendent des versions et du gestionnaire de règles. Vérifie la documentation du système réel et teste les changements dans un environnement de laboratoire.

Fin du cours.

## 21. Études de cas d'application

Les cas suivants servent à exercer un diagnostic méthodique sans transformer toute panne en autorisation générale.

### Cas de diagnostic 1 — HTTPS ne répond pas

**Situation et analyse.** Un test TCP négatif ne prouve pas que le pare-feu est la cause. Vérifie DNS, l'adresse, la route, l'état du service et son adresse d'écoute, puis examine le pare-feu hôte et les journaux du chemin réseau. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Après la correction, teste HTTPS depuis une source autorisée et vérifie que les ports non prévus restent bloqués. Ne désactive pas le pare-feu complet pour faire disparaître le symptôme. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 2 — SSH échoue mais ping réussit

**Situation et analyse.** ICMP et SSH n'utilisent pas le même protocole. Vérifie le service SSH, le port réel, l'adresse d'écoute, les règles locales et celles du réseau. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Valide l'accès depuis la source d'administration et reteste le refus depuis une source non autorisée. N'ouvre pas SSH à toutes les adresses pour restaurer un accès. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 3 — Base de données accessible depuis la DMZ

**Situation et analyse.** Le serveur exposé peut avoir des droits plus larges que nécessaire. Identifie la source applicative et le port réellement utilisé par la base. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Restreins le flux à l'application concernée et vérifie que les autres communications de la DMZ vers les serveurs échouent. Ne laisse pas toute la DMZ accéder à tout le réseau interne. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 4 — Règle de refus sans effet

**Situation et analyse.** Une règle générale antérieure ou une priorité peut masquer la règle spécifique. Consulte le modèle d'évaluation du produit et les journaux. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Teste un flux connu, identifie la règle appliquée et corrige l'ordre ou la portée suivant les conventions du produit. N'empile pas des règles semblables avant d'avoir compris la priorité. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 5 — Perte d'accès d'administration après changement

**Situation et analyse.** Une règle peut avoir bloqué la source ou le port de gestion. Utilise le canal de secours puis compare l'état actuel avec la sauvegarde. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Applique le retour arrière si nécessaire et valide l'accès depuis la source prévue avant de refermer le changement. Ne poursuis pas des modifications à l'aveugle depuis une session distante incertaine. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 6 — NAT considéré comme une autorisation

**Situation et analyse.** La traduction modifie l'adressage mais ne décrit pas toutes les décisions de filtrage. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Inspecte les redirections, les règles et la destination après traduction. Documente les flux entrants attendus et teste-les. Ne présume pas qu'une adresse privée est protégée dans tous les chemins. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 7 — Service accessible en IPv6 seulement

**Situation et analyse.** La politique IPv4 peut ne pas couvrir la pile IPv6. Vérifie l'adresse, la route, les services en écoute et le filtrage IPv6. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Teste l'accès autorisé et interdit avec une connectivité IPv6 réelle. Ne désactive pas IPv6 sans analyser les dépendances. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 8 — Les noms ne se résolvent plus

**Situation et analyse.** Une panne DNS peut être confondue avec un problème de pare-feu Web. Vérifie le résolveur fourni, sa disponibilité, les routes et les règles vers lui. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Compare une résolution depuis un client fonctionnel et consulte les journaux du serveur DNS si disponibles. N'ouvre pas tous les flux sortants pour rétablir DNS. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 9 — Application écoute seulement localement

**Situation et analyse.** Un service lié à la boucle locale n'accepte pas les connexions distantes même si elles passent le filtrage. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Examine les sockets et la configuration d'écoute, puis expose seulement l'interface nécessaire et teste les accès. Ne suppose pas que tout service en écoute est joignable à travers le réseau. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 10 — Nombre élevé de refus

**Situation et analyse.** Le volume peut venir d'une application défectueuse, du trafic attendu ou d'une activité hostile. Regroupe par source, destination, fréquence et horaire. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Corrèle avec les changements récents et les services attendus, puis ajuste la journalisation pour garder les événements importants. Ne déclare pas automatiquement une attaque à partir du volume. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 11 — Invités et utilisateurs sont dans des VLAN séparés mais communiquent

**Situation et analyse.** Le routage et les règles inter-zones peuvent autoriser des communications. Vérifie la passerelle, le chemin et le filtrage réellement appliqué. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Après correction, teste depuis le réseau invité vers plusieurs ressources internes qui doivent rester inaccessibles. Ne confonds pas séparation VLAN et contrôle complet des flux routés. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 12 — Service sur un port non standard

**Situation et analyse.** Il faut confirmer le port avec le propriétaire et la configuration du service plutôt que deviner. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Vérifie les sockets, le protocole et le client requis, puis limite les règles aux destinations et sources nécessaires. N'ouvre pas toute la plage de ports parce que le service est atypique. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 13 — Serveur communique vers des destinations inconnues

**Situation et analyse.** Une politique sortante permissive peut laisser passer des dépendances mal documentées ou des communications indésirables. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Identifie le processus, les destinations, les horaires et le besoin métier ; vérifie l'éditeur et les journaux avant de bloquer. Ne coupe pas toutes les connexions sortantes sans comprendre les dépendances critiques. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 14 — Règle temporaire du prestataire encore active

**Situation et analyse.** Une exception ancienne peut exposer un service après la fin du besoin. Contacte le propriétaire et confirme si l'accès reste nécessaire. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Retire l'exception si elle est obsolète, vérifie les journaux d'utilisation et fixe une date de revue pour les exceptions futures. Ne garde pas une règle uniquement parce que son origine est oubliée. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 15 — Échec depuis un seul poste

**Situation et analyse.** Le problème peut être local au client, à son profil ou à son segment, pas au pare-feu central. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Compare adresse, DNS, route et politique locale avec un poste autorisé qui fonctionne ; teste ensuite le chemin commun. Ne modifie pas le pare-feu central sans comparaison avec un client de référence. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 16 — Refus ICMP empêche un diagnostic

**Situation et analyse.** La politique peut bloquer des messages de contrôle nécessaires. Identifie le type et l'usage ICMP concernés avant de changer la règle. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Autorise uniquement les messages nécessaires, puis vérifie les diagnostics et les restrictions de sécurité. N'autorise pas tous les protocoles pour rétablir une commande. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 17 — Pannes après une nouvelle politique

**Situation et analyse.** Une dépendance partagée comme DNS, NTP ou une API peut avoir été bloquée. Corrèle l'heure des erreurs avec le changement. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Regroupe les flux affectés, identifie la dépendance commune et rétablis seulement le flux nécessaire ou le plan précédent. Ne crée pas immédiatement une règle générale d'autorisation. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 18 — Haute disponibilité ne bascule pas

**Situation et analyse.** La configuration, l'état des sessions ou le suivi des interfaces peut ne pas être correctement synchronisé. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Vérifie les journaux, la synchronisation et les tests de basculement ; applique la procédure approuvée et contrôle les flux après bascule. Ne simule pas une panne en production sans plan autorisé. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 19 — Port d'administration accessible aux utilisateurs

**Situation et analyse.** La règle accorde un droit trop large. L'administration devrait être limitée au réseau ou bastion prévu. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Réduis les sources, vérifie la procédure d'identification et teste un accès autorisé ainsi qu'un accès interdit. Le mot de passe seul ne compense pas l'exposition réseau. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 20 — Règle de labo ne fonctionne pas en production

**Situation et analyse.** Les environnements peuvent différer par routes, interfaces, profils et politiques centrales. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Compare les versions, les zones, les adresses, les règles héritées et le propriétaire de configuration, puis prépare une modification ciblée. Ne copie pas une configuration de laboratoire sans vérifier ses hypothèses. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 21 — HTTPS passe mais le navigateur affiche une erreur

**Situation et analyse.** Une connexion TCP réussie n'atteste pas que TLS, le certificat ou l'application sont corrects. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Vérifie le nom d'hôte, l'expiration et la chaîne du certificat, les journaux du service et les versions TLS prises en charge. N'ouvre pas plus de ports lorsque le transport fonctionne déjà. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 22 — Port semble ouvert mais le service ne répond pas

**Situation et analyse.** Le service peut être arrêté, mal configuré ou ne pas parler le protocole attendu. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Vérifie les journaux applicatifs, les sockets, l'adresse d'écoute et la requête envoyée par le client. Ne conclus pas uniquement à partir d'un scanner ou d'un port affiché. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 23 — Règle ne précise pas la justification

**Situation et analyse.** Une règle sans objectif ni propriétaire ne peut pas être revue correctement. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Demande au propriétaire de confirmer le service, la source et la destination ; documente la date, le risque et l'échéance si temporaire. Ne traite pas une règle inconnue comme nécessaire par défaut. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 24 — Après changement, le service fonctionne mais la sécurité baisse

**Situation et analyse.** La correction peut avoir ouvert plus de flux que prévu. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Teste le flux légitime et les communications interdites ; compare la configuration et les journaux avant et après. Ne valide pas uniquement le succès de l'application. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 25 — Ports SMB largement accessibles

**Situation et analyse.** TCP/445 peut exposer le partage de fichiers à des sources qui n'en ont pas besoin. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Limite SMB aux machines et segments autorisés, mets à jour les systèmes et vérifie aussi les permissions applicatives. Ne publie pas SMB largement vers Internet. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 26 — Serveur admin exposé après ajout d'une redirection

**Situation et analyse.** Une redirection NAT peut publier un service vers l'extérieur si le filtrage et la destination ne sont pas maîtrisés. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Désactive la redirection inutile, vérifie les règles et les journaux, puis teste l'exposition dans un environnement autorisé. Ne suppose pas que la présence d'un NAT suffit à bloquer l'accès. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 27 — Le journal ne contient aucun refus

**Situation et analyse.** La journalisation peut être désactivée, filtrée, dirigée ailleurs ou l'événement n'arrive pas au pare-feu étudié. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Vérifie la configuration de journalisation, la bonne horloge, le chemin réseau et les logs de chaque équipement traversé. L'absence de journal ne prouve pas que le trafic n'a pas été bloqué. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 28 — Dépendance de mise à jour échoue après filtrage sortant

**Situation et analyse.** Le serveur peut nécessiter un DNS, un proxy ou une destination de mise à jour non inventoriée. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Consulte la documentation du produit, identifie les destinations et ports requis, puis ajoute une exception documentée et limitée. Ne restaure pas une autorisation sortante globale sans analyser le besoin. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 29 — Appareil du même LAN contourne le pare-feu périmétrique

**Situation et analyse.** Deux machines dans le même segment peuvent communiquer sans traverser le périmètre. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Contrôle la segmentation locale, le pare-feu hôte et les points de routage ; teste le chemin réel de la communication. Ne suppose pas que le pare-feu périmétrique protège tous les échanges latéraux. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

### Cas de diagnostic 30 — Serveur répond aux ports inattendus

**Situation et analyse.** Des services inutiles peuvent être en écoute ou des règles trop larges peuvent les exposer. Commence par consigner source, destination, protocole, port cible, heure, résultat attendu et changements récents. Examine le service sur l'hôte et les règles de chaque point de passage ; une seule capture de la politique ne décrit pas nécessairement le chemin réel.

**Validation.** Inventorie les ports, confirme les besoins auprès du propriétaire et ferme les services inutiles selon procédure ; valide ensuite l'application. Ne ferme pas à l'aveugle un port métier sans vérifier ses dépendances. Après correction, reteste à la fois le flux autorisé et au moins un flux qui doit rester refusé. Documente la cause racine, le changement, le responsable et la date de révision.

Fin du cours.