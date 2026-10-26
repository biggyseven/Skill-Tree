# Introduction aux pare-feu

## Encadré de mise en contexte

Imagine une entreprise avec plusieurs espaces : les postes des employés, les serveurs contenant les données, le réseau Wi-Fi des visiteurs et une zone qui héberge le site Internet public. Tous ces équipements communiquent grâce aux réseaux. Mais tous ne devraient pas pouvoir communiquer avec tous les autres.

Un poste utilisateur n'a normalement aucune raison de se connecter directement à l'interface d'administration d'un routeur. Un visiteur connecté au Wi-Fi ne devrait pas pouvoir parcourir les dossiers partagés des employés. Un serveur Web public ne devrait pas pouvoir atteindre librement les bases de données internes.

Le pare-feu sert notamment à appliquer ces restrictions. Il examine les communications réseau et décide, selon des règles définies, lesquelles doivent être autorisées, bloquées ou parfois journalisées.

Le pare-feu n'est toutefois pas une protection magique. Il peut autoriser par erreur une communication dangereuse, être mal configuré ou ne pas comprendre ce qui se passe à l'intérieur d'un échange chiffré. Il doit donc faire partie d'une stratégie plus large associant mises à jour, authentification robuste, segmentation, sauvegardes, supervision et bonnes pratiques d'administration.

Dans ce cours, tu vas apprendre à comprendre les pare-feu, à lire leurs règles, à vérifier leur fonctionnement et à concevoir une politique simple et cohérente. Les manipulations de configuration seront réalisées uniquement sur un environnement autorisé et contrôlé.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu devras savoir :

- Expliquer le rôle d'un pare-feu et ses limites.
- Distinguer un pare-feu réseau d'un pare-feu installé sur un poste ou un serveur.
- Comprendre le filtrage de paquets, l'inspection avec état et les fonctions de filtrage applicatif.
- Lire une règle en identifiant sa source, sa destination, son protocole, son port, sa direction et son action.
- Expliquer les politiques par défaut et le principe du moindre privilège.
- Comprendre la différence entre filtrage, traduction d'adresses (NAT) et segmentation.
- Concevoir des règles simples entre plusieurs zones réseau.
- Examiner la configuration d'un pare-feu sous Windows et Linux.
- Dépanner une communication bloquée sans ouvrir tous les ports.
- Lire des journaux de pare-feu et documenter une modification.
- Éviter les erreurs courantes qui réduisent fortement la sécurité.

## 2. Qu'est-ce qu'un pare-feu ?

Un pare-feu, ou *firewall*, est un composant matériel, logiciel ou virtuel qui contrôle les communications entre des équipements ou des réseaux.

Il se base sur une politique de sécurité. Cette politique exprime ce qui est autorisé et ce qui ne l'est pas.

Par exemple, un serveur Web peut recevoir des connexions HTTPS sur TCP/443 depuis Internet. En revanche, l'accès SSH d'administration peut être réservé à un réseau d'administration déterminé.

On peut représenter ce principe de la façon suivante :

```text
                  INTERNET
                      |
                      v
              +----------------+
              | Pare-feu réseau|
              +----------------+
                 |          |
           Autorisé       Refusé
                 |          |
                 v          v
          Serveur Web    Accès non prévu
          TCP/443        Base interne,
                         administration,
                         autres services
```

Ce schéma représente une politique simplifiée. Un pare-feu réel ne décide pas uniquement en fonction du nom du service. Il peut prendre en compte les adresses IP, les ports, le protocole, la direction du trafic, l'interface, la zone de sécurité, l'état de la connexion et d'autres critères selon ses capacités.

### 2.1. Pourquoi en a-t-on besoin ?

Un système informatique expose potentiellement des services accessibles à distance. Parmi eux, on peut trouver :

- Un serveur Web.
- Un service de partage de fichiers.
- Un serveur SSH.
- Un service de bureau à distance.
- Une base de données.
- Une API.
- Un service d'administration d'équipements réseau.

Tous ces services n'ont pas à être accessibles à tout le monde.

Le pare-feu permet de réduire les communications possibles. Ce principe réduit la surface d'attaque : moins un service est accessible, moins il peut être directement visé depuis des réseaux qui n'en ont pas besoin.

Il permet également de séparer des environnements. Un poste compromis ne devrait pas pouvoir contacter librement tous les serveurs de l'entreprise.

Un pare-feu contribue enfin au diagnostic et à la supervision. Ses journaux peuvent indiquer qu'une communication a été autorisée ou bloquée, à condition que la journalisation soit activée et configurée correctement.

### 2.2. Le pare-feu n'est pas un antivirus

Un antivirus ou un outil de détection et de réponse sur les terminaux examine notamment les fichiers, les comportements et les activités de la machine.

Un pare-feu contrôle les communications selon les règles et les informations qu'il peut observer.

Les deux outils remplissent des fonctions différentes.

| Situation | Rôle principal du pare-feu | Autres protections utiles |
|---|---|---|
| Un port d'administration ne doit pas être accessible depuis Internet | Bloquer la communication non autorisée | Accès VPN ou bastion, MFA |
| Un fichier malveillant est téléchargé par HTTPS | Le pare-feu peut autoriser la connexion Web | Antivirus/EDR, filtrage Web, sensibilisation |
| Un serveur présente une vulnérabilité sur un service exposé | Réduire les sources pouvant accéder au service | Correctif logiciel, durcissement, supervision |
| Un utilisateur possède un mot de passe compromis | Restreindre l'accès réseau ne suffit pas à lui seul | MFA, gestion des identités, détection |
| Un poste compromis tente de joindre des serveurs internes | Limiter les flux entre zones | EDR, segmentation, contrôle des identités |

Un pare-feu ne garantit donc pas qu'une communication autorisée est légitime ou sans danger. Il applique une politique. La pertinence de cette politique est déterminante.

## 3. Comprendre les communications réseau

Avant d'écrire une règle, il faut comprendre ce qu'elle autorise réellement.

Une communication IP peut être décrite par plusieurs éléments :

- **Adresse IP source :** l'adresse de l'émetteur.
- **Adresse IP destination :** l'adresse du destinataire.
- **Protocole :** par exemple TCP, UDP ou ICMP.
- **Port source :** port utilisé par l'émetteur lorsqu'il s'applique.
- **Port destination :** port du service auquel on souhaite accéder, lorsqu'il s'applique.
- **Direction :** trafic entrant, sortant ou transféré à travers un équipement.
- **Interface ou zone :** côté du réseau par lequel le trafic arrive ou sort.
- **État de connexion :** information utile pour distinguer l'ouverture d'une session des paquets appartenant à un échange déjà suivi.

Prenons un exemple :

```text
Source       : 192.0.2.50
Destination  : 198.51.100.20
Protocole    : TCP
Port source  : 53124
Port cible   : 443
Objectif     : ouvrir une connexion HTTPS
```

Les adresses utilisées ici appartiennent à des plages réservées à la documentation. Elles ne sont pas les adresses d'un serveur réel à joindre.

Dans cet exemple, le client utilise un port source éphémère et se connecte au service HTTPS du serveur sur TCP/443.

Une règle qui autorise TCP/443 en destination ne signifie pas nécessairement que le pare-feu ouvre toutes les connexions du port 443 dans les deux sens. Il faut analyser la direction, le suivi d'état, la politique par défaut et les autres règles actives.

### 3.1. Qu'est-ce qu'un port ?

Un port TCP ou UDP identifie un point de communication utilisé par un service réseau.

Exemples courants :

| Port | Protocole habituel | Usage courant |
|---|---|---|
| TCP/22 | TCP | SSH |
| TCP/25 | TCP | Relais SMTP entre serveurs, selon le contexte |
| TCP/53, UDP/53 | TCP et UDP | DNS, selon le type de requête |
| UDP/67 et UDP/68 | UDP | DHCPv4 |
| TCP/80 | TCP | HTTP |
| TCP/123 | TCP, UDP selon les implémentations | NTP utilise principalement UDP/123 |
| TCP/443 | TCP | HTTPS sur HTTP/1.1 ou HTTP/2 |
| TCP/445 | TCP | SMB |
| TCP/3389 | TCP et parfois UDP selon la configuration | Bureau à distance Windows |

Attention : ces ports sont des conventions, pas des preuves de la nature réelle d'un service. Une application peut utiliser un port non standard. Inversement, une connexion sur TCP/443 n'est pas automatiquement sûre simplement parce qu'elle utilise le port habituellement associé à HTTPS.

Un pare-feu qui autorise uniquement certains ports réduit les communications possibles, mais ne remplace pas l'analyse du service, de l'identité du client ou du contenu lorsque ces contrôles sont possibles.

### 3.2. TCP, UDP et état d'une connexion

TCP établit généralement une connexion suivie par les équipements intermédiaires. Le pare-feu peut s'appuyer sur cet état pour déterminer si un paquet appartient à une connexion autorisée.

UDP ne possède pas le même mécanisme d'établissement de connexion que TCP. Un pare-feu à états peut néanmoins suivre des échanges UDP de manière temporaire.

C'est le principe de l'inspection avec état : le dispositif conserve une table des communications observées et applique des décisions selon le contexte de chaque session.

La logique est différente d'un filtrage qui examinerait chaque paquet comme un événement entièrement indépendant.

## 4. Les principales familles de pare-feu

### 4.1. Le filtrage de paquets sans suivi d'état

Un filtre de paquets simple examine des caractéristiques du trafic, telles que les adresses IP, le protocole et les ports lorsque ceux-ci existent.

Exemple de règle conceptuelle :

```text
Si :
  destination = serveur Web
  protocole = TCP
  port destination = 443

Alors :
  autoriser
```

Ce type de filtrage peut être efficace et peu coûteux en ressources. Cependant, un filtrage sans état ne comprend pas à lui seul l'ensemble du contexte d'une session. Il faut que sa politique prenne correctement en compte les paquets nécessaires dans les deux sens.

Il ne faut pas confondre ce modèle simplifié avec tous les pare-feu modernes : beaucoup associent filtrage de paquets et suivi d'état.

### 4.2. Le pare-feu à états (*stateful firewall*)

Un pare-feu à états suit les connexions et peut tenir compte de leur progression.

Lorsqu'un client interne ouvre une session Web sortante autorisée, le pare-feu mémorise des informations sur l'échange. Les paquets de réponse appartenant à cette session peuvent alors être reconnus comme du trafic de retour attendu.

Cela ne veut pas dire que toutes les nouvelles connexions entrantes seront acceptées. Une réponse correspondant à une connexion autorisée est différente d'une nouvelle tentative de connexion initiée depuis Internet.

```text
Client interne          Pare-feu à états             Serveur Web
      |                        |                          |
      |--- demande autorisée ->|------------------------->|
      |                        |                          |
      |                        |<-------------------------|
      |<-- réponse suivie -----|                          |
      |                        |                          |
```

Le suivi d'état facilite l'application d'une politique cohérente. Il ne garantit toutefois pas que les applications sont exemptes de vulnérabilités ni que toutes les communications suivies sont légitimes.

### 4.3. Le pare-feu hôte

Un pare-feu hôte est installé sur l'équipement qu'il protège. Il peut s'agir d'un ordinateur Windows, d'un serveur Linux ou d'un autre terminal.

Il permet notamment de limiter les connexions reçues par cette machine et, selon sa configuration, certaines connexions qu'elle initie.

Avantages :

- Protection même lorsque le poste se connecte à différents réseaux.
- Règles spécifiques au système ou à certains programmes.
- Possibilité de protéger des serveurs sans dépendre uniquement du périmètre réseau.
- Réduction de certaines communications latérales entre machines.

Limites :

- Une mauvaise configuration locale peut exposer des services.
- Les politiques peuvent être difficiles à administrer à grande échelle sans gestion centralisée.
- La compromission de la machine peut affecter la confiance accordée à ses informations.
- Les règles doivent rester compatibles avec les besoins légitimes du système.

Windows Defender Firewall est un exemple de pare-feu hôte. Sur Ubuntu, UFW fournit une interface simple pour gérer des règles de filtrage hôte, tandis que Netfilter et nftables constituent une partie importante du mécanisme de filtrage Linux.

### 4.4. Le pare-feu réseau

Un pare-feu réseau contrôle des communications entre des réseaux, des zones ou des interfaces.

Il peut se trouver entre Internet et le réseau d'une entreprise, entre un réseau utilisateur et un réseau de serveurs, ou entre des zones internes ayant des niveaux de confiance différents.

Il centralise une partie de la politique de sécurité et peut protéger plusieurs équipements à la fois.

Il ne remplace pas automatiquement le pare-feu hôte. Si le trafic circule entre deux machines du même segment sans traverser le pare-feu réseau, la politique du périmètre peut ne jamais le voir.

### 4.5. Le proxy et le pare-feu applicatif

Un proxy agit comme intermédiaire pour certains protocoles. Selon son rôle et sa configuration, il peut authentifier les utilisateurs, appliquer des règles d'accès ou journaliser les requêtes.

Un pare-feu applicatif peut analyser des informations plus proches de la couche applicative. Par exemple, un pare-feu applicatif Web (WAF) se concentre sur certaines attaques et requêtes visant des applications Web HTTP.

Un WAF ne remplace pas complètement un pare-feu réseau. Il vise une autre catégorie de risques.

Un proxy Web, un pare-feu réseau et un WAF peuvent donc être complémentaires.

### 4.6. Le NGFW

Un NGFW (*Next-Generation Firewall*) combine généralement plusieurs fonctions, selon le constructeur et la licence : filtrage réseau, suivi d'état, inspection applicative, identification de certaines applications, intégration à des renseignements sur les menaces et fonctionnalités de prévention d'intrusion.

Il faut étudier les capacités réellement activées. Le nom commercial « nouvelle génération » ne suffit pas à prouver qu'une configuration est bien sécurisée.

Les fonctions d'inspection approfondie peuvent également avoir des limites : protocoles non reconnus, trafic chiffré, performances, faux positifs, certificats, exceptions et mises à jour des moteurs de détection.

### 4.7. Résumé des types de pare-feu

| Type | Ce qu'il contrôle principalement | Exemple d'usage |
|---|---|---|
| Filtrage de paquets | Caractéristiques réseau des paquets | Filtrage de base |
| Pare-feu à états | Paquets et contexte des sessions suivies | Filtrage TCP/UDP avec retour de session |
| Pare-feu hôte | Trafic entrant/sortant d'un système | Protection d'un PC ou serveur |
| Pare-feu réseau | Trafic entre interfaces ou zones | Séparation Internet, utilisateurs et serveurs |
| Proxy | Requêtes relayées par un intermédiaire | Contrôle d'accès à certains services |
| WAF | Certaines requêtes et attaques visant des applications Web | Protection complémentaire d'un site Web |
| NGFW | Plusieurs mécanismes réseau et applicatifs | Politique intégrée pour des réseaux d'entreprise |

## 5. Les règles de pare-feu

Une règle formalise une décision de sécurité.

Elle doit répondre à des questions claires :

1. Quel trafic est concerné ?
2. D'où vient-il ?
3. Où va-t-il ?
4. Quel service ou protocole est utilisé ?
5. Dans quel sens la communication se produit-elle ?
6. Quelle action faut-il appliquer ?
7. Dans quelles conditions la règle est-elle valable ?

### 5.1. Les critères d'une règle

Les critères fréquents sont les suivants :

- **Source :** adresse IP, sous-réseau, groupe d'adresses ou zone.
- **Destination :** adresse IP, sous-réseau, groupe d'adresses ou zone.
- **Protocole :** TCP, UDP, ICMP ou autre protocole pris en charge.
- **Port :** un port précis ou une plage de ports, lorsqu'il s'applique.
- **Interface ou zone :** réseau d'où vient le trafic ou vers lequel il part.
- **Direction :** entrant, sortant ou transféré.
- **État de la connexion :** nouvelle connexion, connexion suivie ou autre état reconnu par le pare-feu.
- **Action :** autoriser, bloquer ou rejeter, selon les possibilités du dispositif.
- **Journalisation :** enregistrer les événements qui respectent certains critères.

Tous les produits ne représentent pas les règles de la même manière. Certains proposent également des filtres liés à un programme, à un utilisateur ou à un type de service.

### 5.2. Exemple : autoriser HTTPS vers un serveur Web

Supposons que le serveur Web de documentation utilise l'adresse `192.168.20.10` et que les clients autorisés se trouvent dans `192.168.10.0/24`.

Une règle conceptuelle pourrait être :

```text
Nom         : Clients_vers_Web_HTTPS
Source      : 192.168.10.0/24
Destination : 192.168.20.10
Protocole   : TCP
Port cible  : 443
Action      : Autoriser
Justification : Accès HTTPS à la documentation
```

Le fait d'autoriser cette communication n'implique pas qu'il faut autoriser les clients à accéder à tous les ports du serveur. Une règle ouverte à tous les protocoles et tous les ports accorderait une capacité très supérieure au besoin exprimé.

### 5.3. Autoriser, bloquer ou rejeter

Les termes varient selon les outils, mais on rencontre généralement trois comportements.

**Autoriser (allow/accept)** : laisser passer la communication lorsqu'elle correspond à la règle et aux conditions d'évaluation.

**Bloquer silencieusement (drop)** : abandonner le paquet sans répondre. Le client peut alors attendre une expiration de délai.

**Rejeter (reject)** : refuser explicitement la communication, lorsque le dispositif prend en charge ce comportement. Le client reçoit une indication de refus adaptée au protocole et à la configuration.

Le silence peut limiter certaines informations communiquées à l'émetteur, mais il peut aussi rendre le dépannage moins direct. Le rejet permet parfois de diagnostiquer plus facilement un refus. Le choix dépend de la politique, du protocole et du contexte.

### 5.4. L'ordre des règles

Certains pare-feu évaluent les règles dans un ordre déterminé. D'autres utilisent des mécanismes plus complexes avec objets, priorités, politiques et règles spécifiques.

Considérons cette liste fictive :

```text
Règle 1 : Autoriser toutes les connexions de 192.168.10.0/24 vers 192.168.20.10
Règle 2 : Bloquer TCP/22 de 192.168.10.0/24 vers 192.168.20.10
```

Si le moteur applique la première règle correspondante et s'arrête, la seconde règle peut ne jamais être appliquée à une connexion SSH. La règle large masque alors la règle spécifique.

Ce phénomène est appelé règle masquée ou *shadowed rule* dans certains contextes.

Sur d'autres plateformes, les priorités, les groupes et les types de règles modifient cette logique. Il faut donc consulter la documentation du produit au lieu de supposer que tous les pare-feu appliquent exactement le même ordre.

Une bonne règle est non seulement correcte, mais aussi cohérente avec les autres règles présentes.

### 5.5. Les politiques par défaut

Une politique par défaut indique généralement quelle action appliquer lorsqu'aucune règle applicable ne décide du sort du trafic.

Une stratégie courante consiste à :

- Refuser par défaut les nouvelles connexions entrantes non autorisées.
- N'autoriser que les services nécessaires.
- Évaluer le trafic sortant en fonction des besoins et du niveau de risque.
- Permettre le trafic de retour des connexions autorisées lorsque le fonctionnement à états le prévoit.

Le refus entrant par défaut est particulièrement important pour les terminaux qui ne doivent pas exposer leurs services au réseau.

Pour le trafic sortant, il n'existe pas une seule approche adaptée à toutes les organisations. Une petite structure peut autoriser la majorité des connexions sortantes tout en restreignant certains flux sensibles. Un environnement plus critique peut imposer des destinations et services autorisés plus stricts.

Une politique très restrictive peut renforcer le contrôle, mais elle exige une bonne connaissance des dépendances applicatives, des besoins de mise à jour, du DNS, de l'heure, de l'authentification et des services externes.

**Principe essentiel :** une politique de refus par défaut doit être accompagnée d'une méthode pour identifier, justifier et autoriser les besoins légitimes. Sinon, les utilisateurs peuvent être tentés de contourner les contrôles.

## 6. Trafic entrant, sortant et transféré

### 6.1. Trafic entrant (*inbound*)

Le trafic entrant est évalué par rapport à un équipement ou à une zone protégée lorsque des paquets arrivent depuis un autre réseau.

Exemple : un client Internet tente d'établir une connexion vers un serveur Web public.

La politique doit déterminer si la nouvelle connexion est autorisée, en tenant compte de sa destination, du service publié et des autres contrôles.

### 6.2. Trafic sortant (*outbound*)

Le trafic sortant est initié par un poste ou un serveur vers une destination extérieure à ce système.

Exemples :

- Un poste ouvre un site Web.
- Un serveur contacte un service de mises à jour.
- Une application envoie des données vers une API.

Un poste peut disposer d'un pare-feu très restrictif pour les connexions entrantes mais d'une politique sortante permissive. Cela ne signifie pas qu'il est entièrement protégé : un programme compromis pourrait encore initier des communications sortantes dans la limite des règles autorisées.

### 6.3. Trafic transféré (*forwarded*)

Un pare-feu ou un routeur peut faire transiter des paquets d'un réseau vers un autre.

Exemple :

```text
Réseau utilisateurs
192.168.10.0/24
       |
       v
+------------------+
| Pare-feu / Routeur|
+------------------+
       |
       v
Réseau serveurs
192.168.20.0/24
```

La communication d'un utilisateur vers un serveur passe par le dispositif. La politique de transfert peut autoriser uniquement les services prévus entre les deux réseaux.

Sur Linux, les règles destinées au trafic qui traverse la machine ne sont pas nécessairement les mêmes que celles qui protègent les processus hébergés localement. Il faut distinguer les flux vers la machine elle-même des flux routés à travers elle.

## 7. Pare-feu, NAT et routage : trois notions différentes

Ces mécanismes sont parfois confondus, car ils se trouvent souvent sur le même routeur ou équipement de sécurité.

### 7.1. Le routage

Le routage détermine par quel chemin un paquet IP doit être transmis pour atteindre sa destination.

Il s'agit d'une décision de cheminement réseau.

Un routeur peut disposer de routes vers plusieurs réseaux. Le fait qu'une route existe ne signifie pas automatiquement que toutes les communications sont autorisées par la politique de filtrage.

### 7.2. Le NAT

La traduction d'adresses réseau, ou NAT, modifie certaines adresses IP et parfois des ports pendant le passage d'un paquet.

Un usage courant est de permettre à plusieurs machines privées de partager une adresse IPv4 publique via une traduction de ports, souvent appelée PAT ou NAPT selon le contexte.

Le NAT n'est pas, en lui-même, une politique complète de sécurité. Une traduction d'adresses ne remplace pas un filtrage explicite. Certains routeurs associent le NAT à des règles qui limitent les connexions entrantes, ce qui contribue à entretenir la confusion.

Exemple conceptuel :

```text
Poste privé                Routeur                  Serveur Internet
192.168.10.25:53124  --->  traduction  --->  adresse publique:port
```

La traduction modifie les informations d'adressage. La politique de sécurité détermine quelles communications peuvent traverser l'équipement.

### 7.3. Pourquoi faut-il les distinguer ?

Considérons un serveur avec une adresse IP privée dans un réseau d'entreprise. La présence d'une règle de NAT ne suffit pas pour déterminer quels clients peuvent accéder au serveur. Il faut examiner les règles de filtrage, les interfaces, les routes et la manière dont le produit traite les connexions.

Un diagnostic correct examine donc au moins :

1. L'adresse IP et le masque.
2. La route vers la destination.
3. Le port et le protocole réellement utilisés.
4. Les règles de filtrage actives.
5. Les traductions d'adresses éventuellement appliquées.
6. Les journaux et la réponse du service.

## 8. Segmentation réseau, VLAN et zones de sécurité

La segmentation consiste à séparer un environnement en sous-réseaux ou zones qui n'ont pas tous les mêmes besoins et niveaux de confiance.

Un VLAN peut permettre de séparer logiquement des équipements au niveau du réseau local. Cependant, le simple fait de placer des appareils dans des VLAN différents ne suffit pas à définir les communications autorisées entre ces zones. Il faut une politique de routage et de filtrage appropriée.

### 8.1. Exemple de segmentation d'entreprise

Imaginons les réseaux suivants :

| Zone | Sous-réseau d'exemple | Fonction |
|---|---|---|
| Utilisateurs | `192.168.10.0/24` | Postes des employés |
| Serveurs | `192.168.20.0/24` | Applications et données internes |
| Invités | `192.168.30.0/24` | Visiteurs et appareils personnels |
| Administration | `192.168.40.0/24` | Postes de gestion |
| DMZ | `192.168.50.0/24` | Services publiés vers l'extérieur |

Ces sous-réseaux sont des exemples documentaires.

La politique de sécurité pourrait définir les principes suivants :

- Les utilisateurs accèdent aux applications métier nécessaires.
- Les invités accèdent à Internet, mais pas aux réseaux internes.
- Les administrateurs utilisent un poste ou un réseau d'administration distinct.
- Les serveurs de la DMZ n'atteignent les réseaux internes que pour des besoins justifiés.
- Les bases de données ne sont accessibles que par les applications autorisées.
- Les ports d'administration ne sont pas ouverts largement aux postes utilisateurs.

### 8.2. Représentation simplifiée

```text
                     Internet
                        |
                        v
                  [ Pare-feu ]
                    /   |   \
                   /    |    \
                DMZ   Invités  Utilisateurs
                 |      |          |
             Web public X Internet  |
                 |                 |
                 +------->---------+
                      Flux précis
                           |
                        Serveurs
                           |
                    Données internes
                           ^
                           |
                     Administration
                     accès restreint
```

La représentation ne signifie pas que chaque réseau est relié directement aux autres. Elle montre les catégories de zones et la nécessité de contrôler les flux.

Une segmentation efficace ne repose pas seulement sur les étiquettes des VLAN : elle exige des règles qui empêchent réellement les communications non prévues.

### 8.3. La DMZ

Une DMZ est une zone intermédiaire conçue pour héberger certains services accessibles depuis des réseaux moins fiables, par exemple Internet.

Un serveur Web public peut être placé en DMZ. Si l'application utilise une base de données interne, le flux de la DMZ vers cette base de données doit être limité précisément.

Par exemple, une politique pourrait autoriser le serveur applicatif identifié à joindre un serveur de base de données sur le seul port requis. Elle ne devrait pas lui donner automatiquement accès à tout le réseau interne.

La DMZ ne garantit pas qu'un serveur qui s'y trouve est sûr. Elle limite plutôt les communications possibles lorsqu'un service exposé est compromis.

### 8.4. IPv4 et IPv6

Une erreur fréquente consiste à créer des règles IPv4 sans vérifier la politique IPv6.

Un réseau peut utiliser IPv4 et IPv6 simultanément. Un service bloqué sur une adresse IPv4 peut rester joignable par IPv6 si la configuration et les règles le permettent.

Lors d'un audit, il faut vérifier :

- Si IPv6 est utilisé ou activé.
- Les règles de filtrage IPv6.
- Les adresses et routes IPv6.
- Les services qui écoutent sur IPv6.
- Les différences éventuelles entre les politiques IPv4 et IPv6.

Désactiver IPv6 sans analyse n'est pas une solution universelle : certains environnements et applications en dépendent. La bonne démarche consiste à comprendre la configuration réellement utilisée et à appliquer une politique cohérente aux protocoles présents.

## 9. Le principe du moindre privilège appliqué au réseau

Le moindre privilège signifie qu'un utilisateur, un programme ou un service ne doit disposer que des autorisations nécessaires pour réaliser son travail.

Appliqué aux réseaux, il consiste à limiter :

- Les sources qui peuvent contacter un service.
- Les destinations accessibles depuis un poste.
- Les ports et protocoles autorisés.
- Les communications entre les zones.
- Les accès d'administration.
- La durée d'existence d'une exception.
- Les règles trop larges qui ne sont plus nécessaires.

### 9.1. Exemple de mauvaise règle

```text
Source      : toutes les adresses
Destination : tous les serveurs
Port        : tous les ports
Protocole   : tous
Action      : autoriser
```

Cette règle donne une autorisation extrêmement large. Si elle est appliquée à une zone sensible, elle peut annuler l'effet recherché par de nombreuses règles plus précises.

Elle peut parfois être requise dans un scénario très particulier et documenté, mais elle doit provoquer une revue de sécurité. Il faut pouvoir expliquer pourquoi elle existe, quelles sont ses limites et comment elle sera remplacée ou contrôlée.

### 9.2. Exemple de règle plus précise

```text
Source      : serveur applicatif identifié
Destination : serveur de base de données identifié
Protocole   : TCP
Port cible  : port de la base de données prévu
Action      : autoriser
Justification : accès de l'application à ses données
Expiration  : date de revue définie
```

Le numéro de port dépend du moteur de base de données et de la configuration réelle. Il faut le confirmer plutôt que choisir un numéro au hasard.

La règle précise la communication nécessaire au lieu d'ouvrir le réseau entier.

### 9.3. Le filtrage sortant

Le filtrage sortant mérite une attention particulière. Un système qui ne reçoit aucune connexion entrante non sollicitée peut malgré tout communiquer avec des destinations externes.

Selon le risque, l'organisation peut décider de limiter les communications sortantes aux services nécessaires : DNS vers les résolveurs autorisés, mises à jour vers les destinations approuvées, accès Web par un proxy, communications applicatives vers les API prévues.

Une politique sortante stricte demande une bonne préparation. Il faut inventorier les dépendances et surveiller les événements bloqués afin de détecter les communications indispensables oubliées. Elle ne doit pas être mise en place à l'aveugle sur un système de production.

## 10. Services courants et précautions de filtrage

Une règle correcte dépend du service réel. Il faut éviter de considérer un numéro de port comme une preuve suffisante.

### 10.1. SSH et administration à distance

SSH est souvent utilisé pour administrer des machines Linux ou d'autres équipements.

Le limiter au réseau d'administration réduit le nombre de sources qui peuvent tenter de s'y connecter.

Une politique de ce type ne remplace pas la sécurisation des comptes, les clés d'accès, la gestion des privilèges, la journalisation et les mises à jour.

### 10.2. HTTP et HTTPS

HTTP utilise traditionnellement TCP/80 et HTTPS utilise généralement TCP/443, notamment pour HTTP/1.1 et HTTP/2. HTTP/3 utilise QUIC, qui repose sur UDP, généralement UDP/443.

Il faut vérifier les protocoles réellement employés par l'application. Une règle limitée à TCP/443 ne permet pas automatiquement de décrire tous les flux possibles d'un navigateur moderne.

Autoriser un port Web ne garantit pas que la destination est digne de confiance. Des logiciels malveillants peuvent également utiliser des protocoles Web autorisés.

### 10.3. DNS

Les clients utilisent DNS pour résoudre des noms en adresses IP.

DNS utilise souvent UDP/53, mais TCP/53 intervient aussi dans des circonstances légitimes. D'autres mécanismes chiffrés de résolution DNS peuvent être employés, avec d'autres ports ou transports.

Une politique DNS cohérente doit tenir compte des résolveurs autorisés et du modèle de l'environnement. Bloquer au hasard une partie de DNS peut provoquer des pannes difficiles à comprendre.

### 10.4. SMB et partage de fichiers

SMB est fréquemment utilisé pour le partage de fichiers en environnement Windows. TCP/445 est couramment associé à SMB.

L'accès à ce service doit être limité aux réseaux et systèmes qui en ont réellement besoin. Il est généralement risqué d'exposer largement les services de partage de fichiers à Internet.

La limitation réseau doit être accompagnée d'autorisations de fichiers appropriées, de mises à jour et d'une authentification sécurisée.

### 10.5. ICMP

ICMP transporte notamment des messages de diagnostic et des informations d'erreur IP. Il ne faut pas assimiler ICMP à TCP ou UDP ni lui appliquer des ports qui n'ont pas de sens pour ce protocole.

Bloquer absolument tous les messages ICMP sans analyse peut gêner le diagnostic ou certaines fonctions réseau, notamment celles liées à la découverte de la MTU. Les politiques doivent tenir compte des usages nécessaires et des risques concernés.

## 11. Journaux et supervision

Une politique réseau ne peut pas être administrée correctement si personne ne sait ce qui est autorisé, ce qui est refusé et ce qui se produit en cas de changement.

Les journaux de pare-feu peuvent enregistrer :

- Les paquets ou connexions bloqués.
- Certains flux autorisés.
- L'heure de l'événement.
- Les adresses source et destination.
- Le protocole et les ports associés.
- L'interface ou la zone concernée, selon le produit.
- Des informations sur la règle correspondante, si le dispositif les fournit.

La quantité de détails dépend de l'équipement et de la configuration.

### 11.1. Que signifie un événement de refus ?

Un paquet bloqué peut avoir plusieurs causes :

- Un client tente réellement une communication non autorisée.
- Une application utilise un service non prévu.
- Une règle a été oubliée.
- Un service légitime utilise une destination ou un port inattendu.
- Un programme est mal configuré.
- Une activité malveillante explore des ports ou tente d'accéder à un service.

Un seul événement ne prouve pas à lui seul une attaque. Il doit être interprété avec le contexte : fréquence, source, destination, heure, activité de l'application et autres alertes.

### 11.2. La journalisation doit être utile

Si tous les paquets de tous les réseaux sont enregistrés sans stratégie, les journaux peuvent devenir trop volumineux et rendre les événements importants difficiles à trouver.

À l'inverse, ne journaliser aucun événement empêche certains diagnostics et réduit la visibilité.

Une approche raisonnée consiste à journaliser les événements importants, à régler la taille et la rétention des journaux, à protéger leur accès et à vérifier qu'ils peuvent être consultés lorsque nécessaire.

Il faut aussi éviter d'enregistrer inutilement des données sensibles. Les règles de conservation et d'accès doivent être définies selon les besoins et les obligations de l'organisation.

### 11.3. Comment analyser un refus

Exemple fictif :

```text
Heure       : 10:42:18
Source      : 192.168.10.25
Destination : 192.168.20.10
Protocole   : TCP
Port cible  : 445
Action      : DROP
```

Avant de changer la politique, pose-toi ces questions :

1. Quel appareil possède l'adresse source ?
2. Quel service est hébergé à destination ?
3. Ce service doit-il réellement être accessible depuis cette source ?
4. La demande correspond-elle à une action attendue de l'utilisateur ?
5. Existe-t-il une règle plus précise ou une règle masquée ?
6. Le flux apparaît-il seulement après une modification récente ?
7. Le refus est-il produit par le pare-feu hôte, le pare-feu réseau ou un autre équipement ?

Si l'utilisateur essaie d'accéder à un partage de fichiers qui ne fait pas partie de ses autorisations, le refus peut être la bonne décision. Il ne faut pas automatiquement ouvrir TCP/445 pour faire disparaître l'erreur.

## 12. Gérer proprement le cycle de vie des règles

Une bonne politique de pare-feu n'est pas seulement une collection de règles. Elle exige une gestion des changements.

Chaque règle importante devrait disposer d'une justification et d'un propriétaire.

Selon le contexte, il peut être utile de documenter :

- Le nom de la règle.
- Sa source et sa destination.
- Le protocole et les ports.
- L'action.
- Le motif métier ou technique.
- Le service responsable.
- La date de création.
- La personne ou l'équipe qui l'a approuvée.
- La date de revue ou d'expiration.
- Les tests réalisés.
- Les dépendances et risques connus.

### 12.1. Avant une modification

Avant de modifier une politique de production :

1. Recueillir la configuration actuelle.
2. Comprendre l'impact de la règle envisagée.
3. Vérifier les services et dépendances.
4. Préparer un plan de retour arrière.
5. Disposer d'un moyen d'administration de secours.
6. Définir des tests de validation.
7. Appliquer le changement dans la fenêtre prévue.
8. Confirmer le résultat à partir des journaux et des tests fonctionnels.

Une sauvegarde de configuration est utile, mais il faut également savoir comment la restaurer.

### 12.2. Les règles temporaires

Les exceptions temporaires sont fréquemment créées pendant un dépannage ou une migration. Elles peuvent devenir permanentes si personne ne les réexamine.

Une règle temporaire doit préciser le besoin, le périmètre, le responsable et une date de fin ou de revue.

À échéance, il faut la supprimer, la renouveler après justification ou la transformer en règle permanente approuvée.

### 12.3. La haute disponibilité

Certains environnements utilisent deux pare-feu ou plusieurs dispositifs afin de limiter l'interruption du service en cas de panne.

La haute disponibilité peut fonctionner en actif/passif ou avec d'autres architectures selon le produit.

Elle exige une configuration cohérente, une synchronisation adaptée et des procédures de test. La présence de deux équipements ne garantit pas automatiquement la continuité : une panne commune, une erreur de configuration partagée ou un mauvais basculement peut toujours provoquer une interruption.

## 13. Examiner le pare-feu de Windows

Windows Defender Firewall protège l'ordinateur en contrôlant certaines communications entrantes et sortantes selon ses règles et ses profils.

Les profils habituels sont :

- **Domaine :** pour certains environnements gérés appartenant à un domaine d'entreprise.
- **Privé :** pour les réseaux considérés comme privés et approuvés.
- **Public :** pour les réseaux publics ou moins fiables.

Le nom du profil n'est pas une garantie absolue. Il faut vérifier l'affectation réelle et la politique utilisée.

### 13.1. Vérifier l'état des profils

Dans PowerShell, ouvre une session disposant des droits nécessaires pour lire la configuration, puis exécute :

```powershell
Get-NetFirewallProfile |
    Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction
```

Cette commande est une commande de lecture. Elle affiche l'état des profils et les actions par défaut visibles dans la configuration.

Pour examiner le profil Public :

```powershell
Get-NetFirewallProfile -Name Public
```

Pour afficher les règles :

```powershell
Get-NetFirewallRule |
    Select-Object DisplayName, Enabled, Direction, Action, Profile
```

Ces commandes n'activent ni ne désactivent le pare-feu.

### 13.2. Examiner une règle et ses filtres

Les règles Windows peuvent être associées à des filtres qui définissent les adresses, les ports ou d'autres critères.

Pour afficher les règles entrantes activées :

```powershell
Get-NetFirewallRule -Enabled True -Direction Inbound |
    Select-Object DisplayName, Action, Profile
```

Pour examiner les filtres de ports associés aux règles :

```powershell
Get-NetFirewallRule -Enabled True |
    Get-NetFirewallPortFilter
```

Pour examiner les filtres d'adresses :

```powershell
Get-NetFirewallRule -Enabled True |
    Get-NetFirewallAddressFilter
```

Ces résultats doivent être interprétés en lien avec les règles associées. Il ne faut pas conclure qu'un port est ouvert ou fermé uniquement à partir d'un extrait de sortie : les profils, les filtres, les stratégies administrées et d'autres mécanismes peuvent entrer en jeu.

### 13.3. Tester un service

Supposons que tu veuilles vérifier l'accessibilité d'un service TCP sur un serveur que tu es autorisé à tester.

```powershell
Test-NetConnection -ComputerName 192.0.2.20 -Port 443
```

L'adresse est un exemple documentaire : remplace-la par l'adresse de ton serveur autorisé.

Le résultat peut indiquer si la tentative TCP a réussi. Si elle échoue, cela ne prouve pas automatiquement que le pare-feu est responsable. Le service peut être arrêté, l'adresse incorrecte, la route absente ou un autre équipement peut bloquer le flux.

### 13.4. Activer un pare-feu Windows : attention au contexte

La commande suivante peut activer la protection de tous les profils :

```powershell
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

**C'est une commande de modification, pas de diagnostic.** Il faut vérifier que l'environnement est compatible avant de l'exécuter.

Dans un environnement administré par une organisation, la politique de groupe ou une gestion centralisée peut contrôler la configuration. Sur un serveur distant, une mauvaise modification peut interrompre un accès d'administration ou un service métier.

Dans ce cours, commence par les commandes de lecture. Ne change pas les règles d'un poste de production uniquement pour reproduire un exemple pédagogique.

### 13.5. Consulter la configuration de journalisation

La commande suivante permet d'afficher des informations sur la configuration du pare-feu via `netsh` :

```powershell
netsh advfirewall show allprofiles
```

Elle peut notamment aider à examiner l'état et les politiques de profils. Les options disponibles varient suivant la version de Windows.

Pour consulter les paramètres liés aux journaux, on peut également utiliser les fonctions de la console du pare-feu Windows ou les commandes `netsh` documentées par Microsoft.

Ne modifie pas les chemins de journalisation ou les paramètres de sécurité d'un appareil géré sans vérifier les règles de l'organisation.

## 14. Examiner le pare-feu sous Linux

Linux possède le système de filtrage Netfilter dans le noyau. Plusieurs outils permettent de configurer ou d'examiner les règles.

Deux outils fréquemment rencontrés sont :

- **UFW :** interface simplifiée, courante notamment sur Ubuntu.
- **nftables :** outil de gestion des règles du système de filtrage Netfilter.

Des environnements utilisent encore d'autres outils ou configurations. Il faut identifier le mécanisme actif avant d'y apporter une modification.

### 14.1. Vérifier UFW

Sur un système Ubuntu qui utilise UFW :

```bash
sudo ufw status
```

Pour davantage de détails :

```bash
sudo ufw status verbose
```

Pour afficher les règles numérotées :

```bash
sudo ufw status numbered
```

Ces commandes permettent de lire l'état et les règles UFW. Si UFW indique qu'il est inactif, cela ne prouve pas nécessairement qu'aucun filtrage n'est en place : il faut aussi examiner la configuration réelle de Netfilter, les services de sécurité et les éventuelles règles gérées par un autre outil.

### 14.2. Examiner nftables

Sur un système qui utilise nftables, la commande suivante affiche le jeu de règles :

```bash
sudo nft list ruleset
```

Il s'agit d'une commande de lecture. La sortie peut être longue et contenir plusieurs tables, chaînes et règles.

On peut y rechercher des chaînes qui traitent les paquets reçus par la machine, ceux qu'elle émet et les paquets qui la traversent. La terminologie exacte et l'organisation des règles dépendent de la configuration.

Ne vide pas le jeu de règles pour « repartir de zéro » sans avoir compris qui le gère et comment le restaurer.

### 14.3. Vérifier les services en écoute

Pour examiner les ports TCP et UDP en écoute :

```bash
sudo ss -lntup
```

Cette commande affiche les sockets en écoute et, selon les privilèges et les systèmes, les programmes associés.

La présence d'un service en écoute n'implique pas automatiquement qu'il est accessible depuis l'extérieur. Le résultat doit être mis en relation avec les adresses d'écoute, les routes, le pare-feu hôte et le filtrage réseau.

Inversement, l'absence de connexion depuis un client n'indique pas automatiquement une règle de pare-feu incorrecte.

### 14.4. Ajouter une règle UFW dans un laboratoire

Dans un laboratoire Linux isolé, si un serveur de test doit accepter des connexions SSH seulement depuis une adresse d'administration précise, UFW peut exprimer une règle de ce type :

```bash
sudo ufw allow from 192.0.2.10 to any port 22 proto tcp
```

L'adresse `192.0.2.10` est utilisée comme exemple documentaire. Il faut la remplacer par l'adresse correcte du poste autorisé dans le réseau de laboratoire.

Cette commande modifie la configuration. Ne l'exécute pas aveuglément sur un serveur accessible à distance.

Si le service SSH est actuellement utilisé pour administrer la machine, vérifie d'abord les règles en place, les sources autorisées, l'accès de secours et la procédure de restauration. Une règle trop restrictive ou une activation mal préparée peut bloquer l'administration.

### 14.5. Pourquoi éviter les commandes destructrices

Des commandes qui effacent toutes les règles actives peuvent interrompre les connexions et supprimer des protections essentielles. Elles peuvent aussi entrer en conflit avec un gestionnaire de pare-feu qui régénère automatiquement la configuration.

Pour apprendre, privilégie cet ordre :

1. Lire la configuration.
2. Comprendre l'architecture.
3. Exporter ou sauvegarder ce qui doit l'être.
4. Créer un environnement de laboratoire.
5. Tester une modification précise.
6. Vérifier la connectivité et les journaux.
7. Restaurer la configuration de départ si nécessaire.

## 15. Méthode de dépannage d'une communication bloquée

Quand une application ne parvient pas à communiquer, il faut éviter d'ajouter immédiatement une règle générale.

Une démarche méthodique permet d'isoler le problème.

### Étape 1 : préciser le symptôme

Demande-toi :

- Quelle application est concernée ?
- Quelle machine initie la connexion ?
- Quelle est la destination ?
- Quel port et quel protocole l'application utilise-t-elle ?
- Depuis quand le problème apparaît-il ?
- Le problème concerne-t-il tous les utilisateurs ou un seul ?
- Une configuration a-t-elle récemment changé ?

Une description comme « le réseau est bloqué » n'est pas suffisamment précise pour prendre une décision de sécurité.

### Étape 2 : vérifier la résolution du nom

Si l'utilisateur utilise un nom de domaine, il faut vérifier qu'il correspond à la bonne destination.

Un problème DNS peut être confondu avec un blocage du pare-feu. Il faut distinguer une résolution de nom impossible d'une connexion réseau impossible.

### Étape 3 : vérifier la route et l'adresse

Confirme l'adresse IP, le masque, la passerelle et les routes nécessaires. Vérifie que le client tente réellement de joindre le serveur attendu.

Sur Windows, les commandes de diagnostic réseau comme `ipconfig` et `route print` peuvent aider.

Sur Linux, `ip address` et `ip route` permettent d'examiner les adresses et les routes.

Ces commandes sont principalement destinées à la lecture de configuration.

### Étape 4 : vérifier que le service est actif

Un pare-feu ne peut pas rendre fonctionnel un service arrêté.

Sur le serveur, vérifie si l'application est démarrée, si elle écoute sur la bonne adresse et sur le bon port. Les commandes de lecture telles que `ss -lntup` sous Linux et les outils de diagnostic correspondants sous Windows peuvent être utiles.

### Étape 5 : vérifier la règle locale

Examine la politique du pare-feu hôte. Une application peut fonctionner en local mais être bloquée par une règle entrante.

Vérifie aussi si la règle s'applique au profil actif, à la bonne interface et à l'adresse source attendue.

### Étape 6 : vérifier le chemin réseau

Si le trafic traverse un pare-feu réseau, examine ses règles et ses journaux. Vérifie la zone d'entrée, la zone de sortie, la route et les éventuelles traductions d'adresses.

Il faut déterminer à quel endroit le paquet est bloqué. Une règle créée sur le mauvais équipement ne résoudra pas le problème.

### Étape 7 : formuler une correction minimale

Si une règle manque et que la communication est autorisée par la politique, ajoute uniquement les sources, destinations, protocoles et ports nécessaires.

Documente le changement et réalise un test fonctionnel ainsi qu'un test de non-régression.

### Étape 8 : confirmer et documenter

Après la modification :

- Confirme que l'application fonctionne.
- Vérifie qu'une communication non autorisée reste bloquée.
- Examine les journaux.
- Note les règles modifiées.
- Prévois une date de revue pour les exceptions.
- Restaure l'état précédent si les tests révèlent un effet inattendu.

## 16. Erreurs fréquentes à éviter

### Erreur 1 : autoriser tous les ports pour résoudre rapidement un problème

Une règle trop large peut résoudre un symptôme tout en supprimant une protection importante.

Il faut identifier le flux exact qui manque et autoriser uniquement celui-ci.

### Erreur 2 : confondre NAT et pare-feu

Une traduction d'adresse ne constitue pas à elle seule une politique d'accès complète.

Il faut examiner les décisions de filtrage et les chemins réels du trafic.

### Erreur 3 : oublier le trafic sortant

Un poste peut être protégé contre certaines connexions entrantes tout en conservant une liberté très large pour initier des communications.

La politique sortante doit correspondre au niveau de risque et aux besoins du système.

### Erreur 4 : oublier IPv6

Des règles IPv4 correctes ne prouvent pas que le système IPv6 est correctement contrôlé.

Il faut examiner les deux piles si elles sont présentes.

### Erreur 5 : écrire une règle sans vérifier son ordre ou sa priorité

Une règle correcte sur le papier peut être masquée par une autre règle, se trouver dans le mauvais groupe ou ne pas s'appliquer au profil attendu.

Il faut vérifier la façon dont le produit évalue réellement ses règles.

### Erreur 6 : croire qu'un port indique le contenu exact

Le port 443 est couramment utilisé pour HTTPS, mais une politique fondée seulement sur un numéro de port ne comprend pas automatiquement la légitimité du contenu échangé.

### Erreur 7 : bloquer tous les messages ICMP sans réflexion

Une politique ICMP inadaptée peut gêner le diagnostic et certaines fonctions réseau. Il faut autoriser ce qui est nécessaire selon l'environnement, sans rendre les règles excessivement permissives.

### Erreur 8 : oublier les règles temporaires

Une exception créée pendant un incident peut rester active après la fin du dépannage. Les règles temporaires doivent avoir un responsable et une échéance.

### Erreur 9 : modifier un pare-feu distant sans plan de secours

Une mauvaise règle peut supprimer la seule voie d'administration de la machine. Avant d'intervenir, il faut connaître le chemin d'accès et le mécanisme de restauration.

### Erreur 10 : considérer tous les refus comme des attaques

Un refus peut être normal. Il faut étudier le contexte, l'heure, la fréquence et la destination avant de conclure.

### Erreur 11 : ne pas vérifier le service lui-même

Si le service est arrêté ou n'écoute que sur une interface locale, une règle réseau ne résoudra pas le problème.

### Erreur 12 : ne pas retester après la modification

Une modification peut rétablir un service tout en ouvrant un accès supplémentaire. Il faut vérifier les communications attendues et s'assurer que les autres restrictions restent actives.

## 17. TP 1 — Construire une politique de filtrage simple

### Objectif

Définir une politique cohérente entre un réseau utilisateurs, un serveur Web interne et un réseau invité.

### Topologie

```text
Réseau utilisateurs : 192.168.10.0/24
             |
             v
        [ Pare-feu ]
          /       \
         v         v
 Serveurs internes  Réseau invité
 192.168.20.0/24   192.168.30.0/24
```

Le réseau utilisateurs doit accéder à l'application Web interne. Les invités doivent disposer d'un accès Internet, mais ne doivent pas accéder aux serveurs internes.

### Besoins exprimés

1. Les postes utilisateurs doivent accéder au serveur Web interne sur TCP/443.
2. Les invités ne doivent pas accéder aux réseaux utilisateurs ou serveurs.
3. Le serveur Web ne doit pas disposer d'un accès général aux postes utilisateurs.
4. Les connexions entrantes non prévues doivent être bloquées.
5. Les événements importants doivent pouvoir être examinés.

### Travail demandé

Rédige les règles nécessaires avant de configurer un appareil. Identifie les zones source et destination, les services, les actions et les justifications.

### Proposition de correction

| Source | Destination | Service | Action | Justification |
|---|---|---|---|---|
| Utilisateurs | Serveur Web interne | TCP/443 | Autoriser | Application interne |
| Invités | Réseaux internes | Tout trafic vers les sous-réseaux internes | Bloquer | Isolation des invités |
| Serveurs internes | Utilisateurs | Nouveaux flux non autorisés | Bloquer par défaut | Limitation des mouvements latéraux |
| Sources non prévues | Services d'administration | Ports d'administration | Bloquer | Accès réservé |
| Connexions de retour attendues | Session autorisée | Selon l'état suivi | Autoriser selon la politique | Réponse aux communications permises |

Cette correction décrit des principes. La réalisation exacte dépend de l'équipement, du routage, des règles déjà présentes et des besoins des applications.

La politique doit également définir l'accès Internet des invités sans leur permettre d'atteindre les réseaux internes. Elle doit préciser les services nécessaires à leur fonctionnement et ne pas empêcher les communications légitimes de retour.

### Vérifications à réaliser

- Un poste utilisateur autorisé accède au serveur Web interne.
- Un invité ne peut pas ouvrir une connexion directe vers les serveurs internes.
- Les services d'administration ne sont pas accessibles depuis les réseaux non autorisés.
- Les journaux permettent d'identifier les refus importants.
- La configuration reste cohérente pour IPv4 et IPv6 lorsque les deux sont utilisés.

## 18. TP 2 — Examiner une configuration sans la modifier

### Objectif

S'entraîner à diagnostiquer la politique active sur un ordinateur sans changer ses règles.

### Partie A : Windows

Dans PowerShell, exécute :

```powershell
Get-NetFirewallProfile |
    Format-Table Name, Enabled, DefaultInboundAction, DefaultOutboundAction
```

Puis :

```powershell
Get-NetFirewallRule -Enabled True |
    Select-Object -First 20 DisplayName, Direction, Action, Profile
```

Enfin, affiche les règles entrantes actives :

```powershell
Get-NetFirewallRule -Enabled True -Direction Inbound |
    Select-Object DisplayName, Action, Profile
```

Travail demandé :

1. Note si chaque profil est activé.
2. Observe les actions par défaut.
3. Identifie quelques règles entrantes autorisées.
4. Relève les noms de règles qui mériteraient une explication.
5. Ne désactive aucune règle pendant cet exercice.

Il ne faut pas conclure qu'une règle est dangereuse simplement parce que son nom est inconnu. Il faut examiner ses filtres, son contexte et la fonction de l'application associée.

### Partie B : Linux

Sur un système de laboratoire Ubuntu avec UFW :

```bash
sudo ufw status verbose
sudo ss -lntup
```

Sur un système géré avec nftables :

```bash
sudo nft list ruleset
```

Travail demandé :

1. Vérifie si UFW est actif.
2. Repère les services en écoute.
3. Compare les ports en écoute avec la politique de filtrage.
4. Note les informations encore manquantes pour savoir si un service est accessible depuis un réseau distant.
5. Ne modifie pas le pare-feu pendant cet exercice.

### Résultat attendu

Tu dois comprendre qu'aucune commande isolée ne donne nécessairement une réponse complète. L'accessibilité d'un service dépend du service lui-même, de son adresse d'écoute, du filtrage hôte, du chemin réseau et des règles des équipements traversés.

## 19. TP 3 — Dépanner un accès HTTPS refusé

### Situation

Une application interne est hébergée sur `192.168.20.10`. Le poste `192.168.10.25` ne parvient plus à y accéder par HTTPS.

Une règle existante autorise certains postes du réseau utilisateurs à accéder au serveur sur TCP/443. L'utilisateur affirme que le pare-feu est responsable.

### Démarche attendue

**Étape 1 : confirmer la destination.** Vérifier que le nom de l'application se résout vers la bonne adresse IP.

**Étape 2 : vérifier la route.** Confirmer que le client peut atteindre le réseau de destination par le chemin prévu.

**Étape 3 : tester le port.** Depuis un poste Windows autorisé, un test TCP peut être réalisé avec :

```powershell
Test-NetConnection -ComputerName 192.168.20.10 -Port 443
```

**Étape 4 : vérifier le serveur.** Confirmer que le serveur Web fonctionne et écoute sur l'adresse et le port attendus.

**Étape 5 : lire la règle.** Vérifier la source, la destination, le protocole, le port, le profil ou la zone concernée ainsi que la priorité de la règle.

**Étape 6 : consulter les journaux.** Chercher les événements correspondants à la source et à la destination, à l'heure du test.

**Étape 7 : corriger uniquement la cause identifiée.** Si la règle manque, en proposer une précise. Si le service est arrêté, résoudre le problème de service plutôt que d'ouvrir davantage le réseau.

### Correction commentée

Un échec de `Test-NetConnection` sur TCP/443 démontre que la connexion TCP n'a pas abouti pendant ce test. Il ne prouve pas à lui seul qu'une règle de pare-feu bloque le flux.

Le blocage peut venir du pare-feu hôte, d'un pare-feu réseau, d'une route incorrecte, d'un service arrêté ou d'un autre problème.

Le diagnostic est terminé seulement lorsque la cause a été identifiée et que les tests confirment le rétablissement du service sans ouvrir des accès inutiles.

## 20. Exercices d'application avec correction

### Exercice 1 — Choisir le bon type de pare-feu

Une entreprise veut protéger chaque ordinateur portable, même lorsque celui-ci est connecté à un réseau externe.

Quel type de pare-feu répond directement à ce besoin ?

**Correction :** un pare-feu hôte. Il est installé sur le terminal et peut appliquer des règles locales lors des changements de réseau. Il doit être complété par une politique adaptée et, dans un environnement géré, par un contrôle centralisé.

### Exercice 2 — Comprendre une règle

Une règle autorise TCP depuis `192.168.10.0/24` vers `192.168.20.10`, sur le port destination 443.

Que signifie-t-elle ?

**Correction :** elle autorise, dans son périmètre d'application et sous réserve des autres règles et paramètres du produit, les communications TCP correspondant à cette source et à cette destination sur le port cible 443. Elle ne donne pas automatiquement accès à tous les ports de `192.168.20.10`.

### Exercice 3 — NAT ou filtrage ?

Un administrateur configure une traduction d'adresse pour un serveur. Peut-il en conclure que seuls les clients autorisés pourront accéder au service ?

**Correction :** non. Le NAT traduit des adresses ou des ports. Le contrôle des communications exige l'examen de la politique de filtrage et de la configuration globale de l'équipement.

### Exercice 4 — L'accès SSH ne fonctionne plus

Un serveur Linux est accessible par ping, mais une connexion SSH échoue. Quelle est la prochaine action raisonnable ?

**Correction :** vérifier le service SSH, son adresse d'écoute et son port, puis contrôler les règles du pare-feu local et du réseau ainsi que les journaux. Le ping ne prouve pas que TCP/22 est autorisé ni que SSH fonctionne.

### Exercice 5 — Une règle trop large

Une règle autorise tous les protocoles entre les utilisateurs et les serveurs. Pourquoi faut-il la revoir ?

**Correction :** elle peut permettre des communications qui n'ont aucun lien avec les besoins des utilisateurs, notamment vers des services d'administration ou des données sensibles. Il faut documenter le besoin réel, identifier les flux nécessaires et réduire le périmètre des autorisations.

### Exercice 6 — Un refus prouve-t-il une attaque ?

Le pare-feu enregistre un paquet bloqué à destination de TCP/445. Peut-on conclure que l'organisation subit une attaque ?

**Correction :** non. Le paquet peut correspondre à un client mal configuré, une tentative légitime non autorisée ou une activité malveillante. Il faut étudier sa source, sa fréquence, la destination, l'activité attendue et les événements associés.

### Exercice 7 — Les invités et le réseau interne

Pourquoi placer les invités dans un VLAN séparé ne suffit-il pas toujours ?

**Correction :** les VLAN séparent logiquement les segments, mais des communications peuvent être autorisées ou routées entre eux. Il faut également appliquer et vérifier les règles empêchant l'accès non souhaité aux réseaux internes.

### Exercice 8 — IPv4 et IPv6

Les connexions vers un service sont bloquées en IPv4. Quelle vérification complémentaire est utile ?

**Correction :** examiner si IPv6 est actif, si le service écoute sur une adresse IPv6 et si la politique de filtrage IPv6 est cohérente. Il ne faut pas supposer que les règles IPv4 couvrent nécessairement les communications IPv6.

### Exercice 9 — Lire une commande

Que fait la commande Linux suivante ?

```bash
sudo nft list ruleset
```

**Correction :** elle affiche le jeu de règles nftables actif. C'est une commande de lecture utile pour examiner la configuration. Elle ne crée ni ne supprime une règle.

### Exercice 10 — Plan de changement

Avant de modifier un pare-feu distant, cite quatre précautions importantes.

**Correction possible :**

1. Comprendre la configuration actuelle et le besoin.
2. Sauvegarder ou exporter la configuration pertinente.
3. Prévoir un accès de secours et un plan de retour arrière.
4. Définir des tests précis et une fenêtre de changement.
5. Documenter la modification et vérifier les journaux après le changement.

Quatre éléments correctement expliqués suffisent.

## 21. Défi final — Sécuriser le réseau d'une petite entreprise

### Contexte

Une petite entreprise possède :

- Des postes utilisateurs dans `192.168.10.0/24`.
- Des serveurs internes dans `192.168.20.0/24`.
- Un réseau Wi-Fi invité dans `192.168.30.0/24`.
- Un réseau d'administration dans `192.168.40.0/24`.
- Un serveur Web public dans une DMZ, `192.168.50.0/24`.

Ces réseaux sont fictifs et servent uniquement à l'exercice.

Les exigences de sécurité sont les suivantes :

1. Les utilisateurs doivent accéder aux applications internes prévues.
2. Les invités doivent accéder à Internet sans accéder aux réseaux internes.
3. Le serveur Web public doit accepter les connexions Web publiées.
4. Le serveur Web public doit pouvoir joindre uniquement le service de base de données dont il a besoin, si cette dépendance est nécessaire à l'application.
5. L'administration des serveurs est réservée au réseau d'administration.
6. Les connexions non prévues doivent être refusées.
7. Les refus importants doivent pouvoir être analysés.
8. Toute exception doit être documentée et réexaminée.

### Travail demandé

Construis une politique comprenant :

- Les zones et les objectifs de protection.
- Les principaux flux autorisés.
- Les flux qui doivent être refusés.
- Les mesures de journalisation.
- Les vérifications permettant de confirmer que la politique fonctionne.
- Les précautions nécessaires avant un changement.

### Correction complète

#### A. Définir les zones

| Zone | Fonction | Niveau de confiance attendu |
|---|---|---|
| Utilisateurs | Accès aux applications métier | Contrôlé |
| Serveurs internes | Applications et données sensibles | Élevé, avec accès restreints |
| Invités | Connexions de visiteurs | Faible |
| Administration | Gestion des équipements et serveurs | Accès fortement restreint |
| DMZ | Publication de services vers l'extérieur | Exposée, avec accès internes limités |

Cette classification n'est pas une affirmation selon laquelle une zone est forcément saine. Elle définit les besoins de contrôle et les restrictions attendues.

#### B. Décrire les autorisations

**Utilisateurs vers applications internes :** n'autoriser que les protocoles et ports exigés par les applications prévues. Les destinations doivent être précisées autant que possible.

**Invités vers Internet :** autoriser les communications nécessaires à l'accès Internet selon la politique de l'entreprise, tout en bloquant les accès directs non autorisés aux réseaux internes.

**Internet vers serveur Web en DMZ :** autoriser uniquement les protocoles publiés et les ports nécessaires. Les services d'administration ne doivent pas devenir accessibles au public.

**DMZ vers base de données :** autoriser le serveur applicatif concerné à joindre la base de données sur le port réel utilisé par l'application. Cette règle ne doit pas donner accès à toute la zone des serveurs internes.

**Administration vers serveurs :** autoriser les connexions d'administration nécessaires depuis les postes ou bastions prévus. Les comptes doivent rester correctement protégés, avec MFA lorsqu'il est pris en charge.

**Flux non prévus :** les refuser selon la politique par défaut, après avoir défini les exceptions indispensables.

#### C. Vérifier la segmentation

La politique doit garantir que les invités ne peuvent pas ouvrir de connexion directe vers les réseaux des utilisateurs, des serveurs ou de l'administration.

Si les serveurs internes ne doivent pas initier de connexions vers les postes utilisateurs, cette restriction doit être définie et testée. Le simple fait d'interdire une connexion dans un sens n'empêche pas nécessairement tous les autres flux possibles : il faut vérifier les sessions nouvelles, les flux de retour et les règles de transfert.

#### D. Protéger l'administration

Le réseau d'administration ne doit pas être ouvert à tous les utilisateurs. Les accès doivent provenir de sources identifiées et respecter une procédure de gestion des privilèges.

La protection réseau est une couche de défense, pas le seul moyen de protection. L'authentification, les droits locaux, le bastion éventuel, les mises à jour et les journaux d'administration demeurent indispensables.

#### E. Mettre en place une journalisation utile

Le pare-feu doit enregistrer les refus importants et, lorsque cela est nécessaire, les communications autorisées jugées sensibles.

Les journaux doivent pouvoir être consultés lors d'un incident. Il faut contrôler leur taille, leur rétention et les droits d'accès. Les événements répétitifs attendus ne doivent pas empêcher l'identification des événements significatifs.

#### F. Préparer les tests

Les tests doivent vérifier au minimum :

- Un utilisateur autorisé peut atteindre l'application métier prévue.
- Un invité peut accéder à Internet si cela est requis.
- Un invité ne peut pas ouvrir une connexion directe vers les serveurs internes.
- Internet ne peut joindre que les services publiés dans la DMZ.
- Le serveur Web ne peut atteindre que les services internes explicitement autorisés.
- Les accès d'administration fonctionnent depuis les sources autorisées, mais sont refusés depuis les autres zones.
- La politique IPv4 et IPv6 est cohérente avec l'environnement réel.
- Les journaux permettent d'expliquer les autorisations et les refus observés.

Les tests doivent être réalisés dans un laboratoire ou dans un environnement de production dont la modification a été approuvée. Les résultats doivent être conservés pour permettre la comparaison après un changement.

#### G. Préparer un retour arrière

Avant d'appliquer la politique, sauvegarder la configuration selon les possibilités du dispositif, noter les règles existantes, identifier la méthode de restauration et s'assurer qu'un accès de secours est disponible.

Après le changement, effectuer les tests fonctionnels et de sécurité. Si un flux indispensable est interrompu, corriger la cause identifiée ou restaurer l'état précédent selon le plan préparé. Il ne faut pas désactiver l'ensemble du pare-feu comme solution de dépannage par défaut.

#### H. Documenter les décisions

Chaque règle importante doit avoir une justification. Une règle doit pouvoir être reliée à un service ou à un besoin métier identifiable.

Les exceptions ont un propriétaire et une date de réexamen. Une revue périodique permet de supprimer les règles inutiles et de détecter les autorisations devenues trop larges.

### Critères d'évaluation du défi

Le défi est réussi si la politique proposée :

- Distingue clairement les zones.
- Identifie les flux nécessaires.
- Limite les services exposés.
- Empêche les invités d'accéder directement aux réseaux internes.
- Réserve l'administration aux sources autorisées.
- Considère le filtrage entrant, sortant et transféré selon le contexte.
- Prévoit une journalisation exploitable.
- Inclut des tests de validation et un retour arrière.
- Tient compte d'IPv4 et d'IPv6 lorsque cela s'applique.
- Évite les autorisations générales sans justification.

Il ne s'agit pas de maximiser le nombre de règles. Il s'agit de définir une politique compréhensible, vérifiable et adaptée aux besoins.

## 22. Glossaire essentiel

**Pare-feu (firewall)** : dispositif matériel ou logiciel qui contrôle des communications selon une politique.

**Règle** : instruction décrivant les caractéristiques d'un trafic et l'action à appliquer.

**Politique par défaut** : décision appliquée lorsque les conditions prévues ne conduisent pas à une autre décision.

**Trafic entrant** : trafic reçu par un système ou une zone depuis l'extérieur de ce périmètre.

**Trafic sortant** : trafic initié ou émis par un système vers une destination extérieure à ce périmètre.

**Trafic transféré** : trafic qui traverse un équipement pour aller d'un réseau à un autre.

**Pare-feu à états** : pare-feu qui suit les connexions pour tenir compte de leur contexte.

**NAT** : mécanisme de traduction d'adresses réseau et, selon les techniques employées, de ports.

**VLAN** : réseau local virtuel qui permet de séparer logiquement des groupes d'équipements.

**Segmentation** : séparation de réseaux ou de systèmes afin de contrôler les communications entre eux.

**DMZ** : zone intermédiaire destinée notamment à héberger certains services accessibles depuis des réseaux moins fiables.

**Proxy** : intermédiaire qui relaie des communications ou des requêtes selon son rôle.

**WAF** : pare-feu applicatif Web destiné à analyser et à filtrer certaines requêtes visant des applications Web.

**NGFW** : pare-feu combinant plusieurs capacités réseau et, selon le produit, applicatives ou de prévention.

**Surface d'attaque** : ensemble des points et voies par lesquels un système peut être exposé à des attaques.

**Moindre privilège** : principe consistant à accorder uniquement les autorisations nécessaires.

**Journalisation** : enregistrement d'événements afin de permettre l'analyse, le diagnostic et la supervision.

**Règle masquée** : règle qui ne produit pas l'effet attendu parce qu'une autre règle ou une autre priorité prévaut selon le moteur d'évaluation.

**Retour arrière** : procédure permettant de revenir à un état connu après une modification problématique.

## 23. Références officielles pour approfondir

Les ressources suivantes permettent d'approfondir les concepts et de vérifier les commandes selon l'environnement utilisé.

- Microsoft Learn, `Get-NetFirewallProfile` : https://learn.microsoft.com/en-us/powershell/module/netsecurity/get-netfirewallprofile
- Microsoft Learn, gestion du pare-feu Windows en ligne de commande : https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/configure-with-command-line
- Microsoft Learn, configuration de la journalisation du pare-feu Windows : https://learn.microsoft.com/en-us/windows/security/threat-protection/windows-firewall/configure-the-windows-firewall-log
- Documentation Ubuntu Server, pare-feu et UFW : https://documentation.ubuntu.com/server/how-to/security/firewalls/
- Documentation de sécurité Ubuntu, fonctions de filtrage et outils associés : https://documentation.ubuntu.com/security/security-features/network/firewall/
- NIST SP 800-41 Rev. 1, *Guidelines on Firewalls and Firewall Policy* : https://csrc.nist.gov/pubs/sp/800/41/r1/final

Les commandes doivent être vérifiées sur la version du système et du produit réellement administrée. Une instruction valable sur une machine de laboratoire n'est pas automatiquement appropriée pour une machine de production.

## Conclusion

Le pare-feu est l'un des outils fondamentaux de la sécurité réseau. Il permet de limiter les communications, de séparer des zones et de rendre certaines attaques plus difficiles. Mais sa valeur dépend de la qualité de sa politique, de la compréhension du réseau et de la rigueur avec laquelle ses règles sont administrées.

La démarche à retenir est simple : **décrire le besoin, identifier le flux exact, limiter les autorisations, vérifier la règle réellement appliquée, tester le résultat et documenter le changement**.

Quand une communication échoue, il faut rechercher la cause avant de modifier la politique. Quand une règle est créée, elle doit répondre à une justification précise et rester limitée au strict nécessaire.

La maîtrise des pare-feu commence par la lecture et la compréhension des règles, puis se consolide par la pratique en laboratoire. C'est cette méthode qui permet de renforcer la sécurité sans bloquer inutilement les services légitimes.

Fin du cours.
