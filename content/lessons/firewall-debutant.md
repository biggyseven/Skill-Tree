---
node_id: firewall-debutant
title: Pare-feu & NGFW - Débutant
---
# Pare-feu & NGFW - Débutant
**Niveau :** DÉBUTANT

Un pare-feu (*firewall*) est un composant de sécurité qui contrôle les communications réseau selon une politique définie. Il peut autoriser, bloquer, journaliser ou, selon le produit, inspecter plus profondément certains échanges. On le place souvent entre un réseau interne et Internet, mais il peut aussi protéger des serveurs, séparer des services, filtrer les communications entre VLAN ou contrôler les connexions d'un ordinateur individuel.

Un NGFW (*Next-Generation Firewall*, ou pare-feu de nouvelle génération) reprend les fonctions classiques du pare-feu et y ajoute généralement des capacités d'identification des applications, de prévention d'intrusion, de contrôle plus fin des utilisateurs, de filtrage Web et d'inspection de contenu. Le sigle NGFW ne garantit toutefois pas que toutes ces fonctions sont présentes, activées ou correctement configurées : il faut vérifier les capacités et la licence du produit choisi.

Ce cours présente les bases sans supposer de connaissance préalable en cybersécurité. Il commence par les paquets, les adresses et les ports, puis explique les familles de pare-feu, les politiques de filtrage, les zones de sécurité et les principes de configuration. Les exemples Cisco IOS servent à comprendre les mécanismes de filtrage et ne remplacent pas la documentation de la plateforme réelle. Une ACL IOS, un pare-feu à états et un NGFW dédié ne sont pas des produits interchangeables : leurs capacités et leurs syntaxes diffèrent.

Le fil conducteur est une petite entreprise qui possède un réseau de postes, un serveur Web accessible depuis Internet et un réseau d'administration. L'objectif n'est pas de tout bloquer, mais de permettre les échanges nécessaires tout en réduisant les possibilités d'accès non autorisé. Une politique de pare-feu doit être compréhensible, documentée, testée et révisée lorsque les besoins changent.

> **Analogie** : Imaginez un bâtiment avec plusieurs zones. Le portail vérifie qui entre, les portes intérieures séparent les bureaux, et le registre note certains passages. Un pare-feu joue un rôle comparable pour les communications numériques : il applique des règles aux échanges, mais il ne remplace ni les serrures des serveurs ni la prudence des utilisateurs.

---

## 1. La théorie et les algorithmes

### 1.1. Pourquoi faut-il un pare-feu ?

Un ordinateur communique avec d'autres systèmes pour consulter des sites Web, envoyer des courriels, accéder à des fichiers, synchroniser l'heure ou recevoir des mises à jour. Ces échanges sont utiles, mais une connexion inutile peut aussi devenir un chemin d'attaque. Un service exposé peut contenir une vulnérabilité ; un ordinateur compromis peut essayer de joindre d'autres machines ; un visiteur non autorisé peut rechercher un port ouvert.

Le pare-feu réduit cette surface d'exposition en appliquant une politique de trafic. Cette politique indique quelles communications sont souhaitées et lesquelles doivent être bloquées. Elle se définit à partir de questions concrètes : quelle source peut joindre quelle destination ? Quel protocole ou service est nécessaire ? Dans quel sens la communication doit-elle être permise ? Faut-il enregistrer les tentatives refusées ? Qui approuve une modification de règle ?

Le pare-feu n'est cependant pas une protection magique. Il ne corrige pas à lui seul un logiciel vulnérable, un mot de passe faible ou un utilisateur trompé par un message de phishing. Une communication autorisée peut transporter des données malveillantes, notamment si la règle est trop large ou si le service autorisé est compromis. La sécurité repose donc sur plusieurs couches : mises à jour, authentification, sauvegardes, antivirus/EDR, segmentation, chiffrement, surveillance et formation.

### 1.2. Comprendre un paquet réseau

Pour décider quoi faire, un pare-feu examine des informations présentes dans les communications. Un paquet IP contient notamment une adresse IP source et une adresse IP de destination. Selon le protocole, il peut également contenir des informations de transport, par exemple des ports TCP ou UDP. Les couches réseau et transport sont souvent décrites à l'aide du modèle TCP/IP ou du modèle OSI.

| Élément | Signification simple | Exemple | Utilité pour le filtrage |
|---|---|---|---|
| Adresse IP source | Système qui envoie le paquet | `192.168.10.25` | Autoriser ou refuser l'origine |
| Adresse IP destination | Système visé | `203.0.113.20` | Limiter les destinations accessibles |
| Protocole IP | Type de transport ou de message | TCP, UDP, ICMP | Distinguer les familles de trafic |
| Port source | Port utilisé côté client, souvent temporaire | `51524` | Aide à identifier le flux |
| Port destination | Port du service visé | `443` | Distinguer HTTPS, DNS, SSH, etc. |
| Drapeaux TCP | État ou action TCP, par exemple SYN/ACK | SYN | Utilisé par certains contrôles d'état |
| Interface / zone | Point d'entrée ou de sortie | WAN, LAN, DMZ | Appliquer une politique selon le chemin |

Les adresses de documentation `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` apparaissent dans des exemples pour éviter de donner l'impression qu'une adresse publique fictive appartient réellement à une entreprise. Dans un réseau réel, les valeurs doivent provenir du plan d'adressage approuvé.

Une communication est un échange, pas seulement un paquet isolé. Pour charger une page Web en HTTPS, un poste client initie généralement une connexion TCP vers le serveur sur le port de destination 443. Le serveur envoie ensuite des réponses vers le port temporaire du client. Un filtre qui ne tient compte que d'un paquet dans un seul sens peut mal comprendre ce mécanisme. C'est l'une des raisons pour lesquelles les pare-feu à états sont courants.

### 1.3. Ports et protocoles essentiels au débutant

Un port TCP ou UDP identifie, au sein d'un système, un point de communication logique. Il ne constitue pas à lui seul une preuve de l'application réelle : une application peut utiliser un port inhabituel et un trafic malveillant peut tenter de se faire passer pour un protocole connu. Un filtrage fondé uniquement sur le numéro de port reste néanmoins utile comme première mesure.

| Port courant | Protocole / service habituel | À retenir |
|---:|---|---|
| TCP 22 | SSH | Administration chiffrée ; à limiter aux hôtes d'administration |
| TCP 23 | Telnet | Administration non chiffrée ; à éviter sur les réseaux modernes |
| UDP/TCP 53 | DNS | Résolution de noms ; le besoin exact dépend du rôle DNS |
| UDP 67/68 | DHCP IPv4 | Attribution automatique d'adresses ; dépend de la topologie |
| TCP 80 | HTTP | Web non chiffré ; souvent redirigé vers HTTPS |
| TCP 443 | HTTPS | Web chiffré ; ne signifie pas que tout contenu est sain |
| UDP 123 | NTP | Synchronisation de l'heure |
| TCP 25 | SMTP entre serveurs | Messagerie ; le flux sortant des utilisateurs peut différer |
| TCP 3389 | RDP | Bureau à distance Windows ; accès à restreindre fortement |
| ICMP | Messages de contrôle IP | N'utilise pas de ports TCP/UDP |

Le protocole ICMP ne possède pas de numéro de port TCP/UDP. Il transporte par exemple des messages d'erreur réseau et des requêtes/réponses d'écho utilisées par `ping`. Bloquer tout ICMP sans analyse peut compliquer le diagnostic et certains mécanismes réseau. Inversement, autoriser tout type de trafic de contrôle sans limite n'est pas nécessairement souhaitable. La règle doit correspondre au besoin et au type de message.

### 1.4. Les principales familles de pare-feu

**Pare-feu à filtrage de paquets.** Il prend une décision à partir de champs tels que l'adresse source, l'adresse destination, le protocole et les ports. Les listes de contrôle d'accès (*Access Control Lists*, ACL) des routeurs peuvent assurer ce type de filtrage. Cette approche est efficace pour des critères simples, mais elle ne comprend pas nécessairement le contexte complet d'une connexion ni le sens réel d'une application.

**Pare-feu à états (*stateful firewall*).** Il maintient une table de connexions ou d'états. Lorsqu'une connexion autorisée est initiée, le pare-feu enregistre des informations sur le flux et peut reconnaître les paquets de réponse qui appartiennent à cette session. Ainsi, une réponse HTTPS au trafic initié par un poste interne peut être permise sans créer une règle indépendante autorisant toute connexion entrante vers le poste. Cela ne signifie pas que tous les paquets entrants sont sûrs : le pare-feu vérifie qu'ils correspondent à un état valide selon son implémentation.

**Passerelle applicative ou proxy.** Elle relaie certaines communications au nom du client et peut analyser le protocole applicatif. Elle peut fournir un contrôle fin, mais ajoute parfois de la complexité, de la latence ou des exigences de compatibilité. Un proxy Web, par exemple, peut appliquer des politiques sur les URL ou les catégories de sites selon ses capacités.

**Pare-feu hôte.** Il fonctionne sur un ordinateur ou un serveur. Il peut limiter les connexions vers ou depuis ce système. Il reste utile même si le réseau est protégé par un pare-feu périphérique, car un poste peut être compromis ou déplacé vers un autre réseau. Le pare-feu Windows Defender est un exemple de pare-feu hôte.

**Pare-feu réseau.** Il protège un réseau, un groupe de réseaux ou une frontière entre zones. Il peut être un appareil matériel, une fonction logicielle sur un routeur ou un équipement virtuel dans une infrastructure cloud. Son rôle exact dépend de son emplacement, de sa configuration et des fonctions prises en charge.

**NGFW.** Un pare-feu de nouvelle génération peut combiner filtrage réseau, suivi des connexions, identification d'applications, prévention d'intrusion (IPS), filtrage Web, réputation de domaines, contrôle d'identité, inspection de fichiers et déchiffrement TLS dans certains scénarios. Ces capacités varient fortement d'un constructeur et d'une licence à l'autre. Certaines fonctions doivent être activées séparément, recevoir des mises à jour et être correctement réglées.

### 1.5. Différence entre pare-feu classique et NGFW

Un pare-feu classique peut décider : « autoriser les connexions TCP vers le serveur A sur le port 443 ». Un NGFW peut, selon ses capacités, ajouter la question : « s'agit-il de l'application autorisée, l'utilisateur est-il identifié, ce flux contient-il des signes d'exploitation connus, et la destination est-elle réputée dangereuse ? » Cette seconde analyse permet une politique plus riche, mais elle n'est pas infaillible.

| Fonction | Pare-feu à règles réseau classique | NGFW typique, selon produit et licence |
|---|---|---|
| Filtrage IP, protocole et ports | Oui | Oui |
| Suivi des connexions | Souvent | Généralement |
| Identification applicative | Limitée ou absente | Souvent proposée |
| Prévention d'intrusion (IPS) | Pas nécessairement | Souvent proposée |
| Contrôle selon utilisateur | Limité | Disponible sur certains produits/intégrations |
| Filtrage URL / catégories Web | Variable | Souvent proposé |
| Détection par réputation / renseignement de menace | Variable | Souvent proposée |
| Inspection TLS | Non systématique | Possible selon produit et configuration |
| Besoin de tuning et de supervision | Oui | Oui, souvent davantage de paramètres |

Le terme « nouvelle génération » n'est pas une garantie indépendante. Avant un achat, on doit confirmer la capacité exacte, le débit avec les fonctions activées, les limites de sessions, la haute disponibilité, l'administration, la journalisation, le coût des licences et le processus de mise à jour. Une fonction annoncée mais laissée désactivée ne protège pas le trafic.

### 1.6. Comment le pare-feu prend-il une décision ?

De nombreux pare-feu évaluent les règles selon un ordre précis. Une règle peut comparer la zone source, la zone destination, les adresses, les services, les utilisateurs ou les applications, puis déclencher une action. Selon le produit, les règles peuvent être évaluées de haut en bas, par priorité ou selon une logique interne documentée. Il est indispensable de connaître cet ordre avant de modifier la politique.

Dans une liste ACL traditionnelle, l'évaluation se fait de haut en bas et la première entrée correspondante détermine la décision. Une interdiction placée après une autorisation plus large peut ne jamais être atteinte. Les ACL Cisco IOS ont aussi un refus implicite à la fin : si aucune entrée ne permet le paquet, celui-ci est refusé. Les interfaces graphiques des pare-feu dédiés peuvent appliquer des règles et des priorités selon une logique différente ; il faut donc lire leur documentation.

> **Piège :** Une règle « autoriser tout le trafic » placée en haut peut rendre inutiles les règles restrictives qui suivent. Vérifiez l'ordre, la portée, les zones et les compteurs des règles, plutôt que de supposer que toutes les lignes sont évaluées indépendamment.

### 1.7. Politique « refuser par défaut »

Le principe *deny by default* consiste à bloquer les communications qui ne sont pas explicitement autorisées par une politique. Il ne signifie pas que tout est bloqué sans aucune réflexion : l'administrateur commence par recenser les services indispensables, puis autorise le strict nécessaire. C'est généralement plus sûr que de tout autoriser et d'essayer ensuite d'identifier chaque trafic à interdire.

Pour chaque règle, documentez au minimum : la source, la destination, le service ou l'application, l'action, la justification, le propriétaire métier, la date d'approbation et la date de révision prévue. Une règle sans propriétaire ni justification risque de rester en place alors que le besoin a disparu. Une règle trop vague, comme « LAN vers Internet : tout autoriser », doit être examinée au regard des risques et des besoins opérationnels.

Une politique réaliste est une balance entre sécurité et disponibilité. Bloquer sans analyse les DNS, DHCP, la synchronisation NTP ou des messages nécessaires au bon fonctionnement peut perturber tout un site. Autoriser trop largement l'administration à distance peut permettre à un attaquant de se déplacer latéralement. Il faut définir le besoin, tester l'effet de la règle, puis surveiller le résultat.

### 1.8. Flux entrant, sortant et retour de connexion

Le trafic **entrant** arrive depuis une zone externe vers une zone protégée. Il doit être autorisé uniquement lorsqu'un service est réellement destiné à être accessible depuis cette zone. Le trafic **sortant** quitte une zone interne vers un réseau externe. Il mérite également une politique : un poste compromis qui peut joindre n'importe quelle adresse et n'importe quel port dispose de nombreuses possibilités de communication.

Le trafic **interzone** traverse deux zones de sécurité, par exemple le réseau des utilisateurs vers celui des serveurs. Il ne faut pas supposer que le trafic interne est toujours fiable. Séparer les postes utilisateurs, les serveurs, les invités Wi-Fi et l'administration limite les mouvements possibles en cas de compromission.

Un pare-feu à états peut autoriser les paquets de retour d'une connexion initiée par une source autorisée. Ce comportement est différent d'une règle stateless qui ne considère que chaque paquet et dont les règles peuvent devoir prendre en compte les deux sens. Les réponses légitimes ne doivent pas être confondues avec une nouvelle connexion initiée depuis l'extérieur. La façon de distinguer ces cas dépend du protocole et de l'implémentation.

### 1.9. Zones de sécurité et DMZ

Une **zone de sécurité** regroupe des interfaces ou des réseaux ayant un niveau de confiance et un besoin de communication comparables. Les noms usuels sont LAN (réseau interne), WAN (réseau externe), DMZ (zone démilitarisée pour certains services publics), SERVEURS et ADMIN. Ces noms sont des conventions : c'est la politique de flux qui leur donne un sens.

Une **DMZ** est souvent utilisée pour isoler des serveurs qui doivent être accessibles depuis Internet, comme un serveur Web ou une passerelle de messagerie. Le serveur public ne doit pas bénéficier automatiquement des mêmes droits que les postes internes. Si le serveur Web est compromis, les règles interzones doivent limiter sa capacité à atteindre les bases de données, les postes utilisateurs ou les interfaces d'administration.

Exemple de segmentation :

```text
                    INTERNET
                        |
                 [ Pare-feu / NGFW ]
                   /      |       \
                  /       |        \
               WAN       DMZ       LAN
                         |          |
                    [Serveur Web] [Postes]
                         |          |
                    Flux limités   [Admin]

Politique illustrative :
- Internet -> Serveur Web : HTTPS uniquement si nécessaire
- Internet -> Postes : refus par défaut
- Serveur Web -> Base de données : uniquement le port requis
- Postes -> Administration : refus sauf besoin approuvé
- Administration -> Équipements : protocoles d'admin autorisés et journalisés
```

Dans une architecture complète, l'administration est préférable depuis une zone dédiée, avec authentification forte et des postes administrateurs durcis. Placer un serveur dans une DMZ ne le rend pas automatiquement sûr. Les systèmes doivent être mis à jour, durcis, surveillés et configurés pour n'exposer que les services utiles.

### 1.10. NAT et pare-feu : notions différentes

La traduction d'adresses réseau (*Network Address Translation*, NAT) modifie des informations d'adressage, parfois aussi des ports. Par exemple, plusieurs appareils privés peuvent partager une adresse IP publique pour sortir vers Internet. Une règle NAT et une règle de filtrage peuvent coexister sur le même équipement, mais elles répondent à des objectifs différents : le NAT traduit ; la politique de pare-feu décide si le trafic est permis.

Une traduction d'adresse ne constitue pas à elle seule une politique de sécurité suffisante. Il ne faut pas conclure que tout trafic est bloqué uniquement parce qu'une adresse privée n'est pas directement routable depuis Internet. La configuration exacte d'un équipement influence les flux possibles. Les règles de filtrage, de traduction, de routage et de suivi d'état doivent être cohérentes, et leur ordre de traitement varie selon les plateformes.

Dans certains scénarios de publication de serveur, une adresse publique est traduite vers une adresse privée de DMZ. Il faut vérifier qu'une règle de sécurité n'autorise que le service prévu. Une redirection NAT mal accompagnée d'une règle restrictive peut exposer un service de façon inattendue ; une règle de filtrage mal placée peut aussi bloquer le service légitime.

### 1.11. Menaces que le pare-feu peut aider à réduire

Un pare-feu peut limiter les connexions non autorisées, réduire l'exposition des ports d'administration, segmenter un réseau, bloquer certaines destinations malveillantes et, selon ses fonctions, détecter des motifs d'attaque. Un NGFW muni d'un IPS à jour peut repérer certaines signatures ou comportements associés à des exploitations connues. Le résultat dépend toutefois de la visibilité du trafic, de la version des signatures, du chiffrement, de la politique et des faux positifs.

Les attaques par déni de service (DoS/DDoS) cherchent à rendre un service indisponible en saturant la bande passante, les connexions ou les ressources applicatives. Certains pare-feu limitent le débit ou le nombre de sessions, mais un équipement local ne peut pas toujours absorber une attaque qui remplit déjà le lien Internet. La réponse peut exiger l'aide du fournisseur d'accès, un service de protection DDoS ou une architecture distribuée.

Les logiciels malveillants peuvent utiliser des connexions sortantes, des domaines récemment créés, des services légitimes détournés ou des canaux chiffrés. Le filtrage sortant, les contrôles applicatifs et les renseignements de menace peuvent réduire certains risques, mais aucune règle ne détecte toutes les menaces. Les journaux, les outils de détection sur les postes et les procédures de réponse aux incidents restent importants.

### 1.12. Limites et erreurs de compréhension

Un pare-feu réseau ne voit pas toujours ce qui se passe à l'intérieur d'une application chiffrée. L'inspection TLS peut améliorer la visibilité, mais elle a des implications de confidentialité, de compatibilité, de gestion de certificats et de performance. Elle peut être impossible ou non souhaitable pour certaines applications. Il faut évaluer le cadre légal, informer les utilisateurs lorsque requis et exclure les flux sensibles selon la politique applicable.

Un pare-feu qui autorise HTTPS ne certifie pas que le site consulté est légitime, et le port 443 peut transporter d'autres usages. Un pare-feu ne connaît pas automatiquement l'intention du trafic. Les fonctions d'identification applicative améliorent l'analyse, mais peuvent être perturbées par les mises à jour applicatives, les techniques d'évasion, les tunnels ou le chiffrement. Il faut mesurer les résultats plutôt que se fier à une étiquette commerciale.

Un pare-feu mal administré peut lui-même devenir un point de défaillance. Les mots de passe d'administration doivent être robustes, l'accès de gestion doit être limité, les configurations sauvegardées, les mises à jour planifiées et les journaux protégés. La haute disponibilité réduit certains risques d'arrêt, mais elle ne corrige pas automatiquement une règle erronée : une politique fautive peut être synchronisée sur les deux membres d'un cluster.

### 1.13. Méthode simple pour concevoir une règle

Avant de créer une règle, formulez-la sous forme de phrase : « Les postes du réseau utilisateurs doivent accéder aux serveurs DNS approuvés en UDP/TCP 53, et aucune autre destination DNS n'est nécessaire sans justification ». Cette formulation permet de vérifier le but, la source, la destination, le service et les limites.

Procédez ensuite ainsi :

1. Identifiez le service métier et son propriétaire.
2. Déterminez les hôtes ou sous-réseaux source et destination.
3. Confirmez le protocole et les ports nécessaires à partir de la documentation du service.
4. Identifiez le sens d'initiation de la connexion et les besoins de retour.
5. Décidez si le trafic doit être journalisé et à quel niveau.
6. Placez la règle à un endroit cohérent avec l'ordre d'évaluation.
7. Testez un cas autorisé et au moins un cas qui doit être refusé.
8. Documentez le résultat et planifiez une révision.

Cette méthode vaut mieux qu'une règle ajoutée uniquement parce qu'un utilisateur dit « Internet ne marche pas ». Le dépannage doit d'abord établir où le flux échoue et quels services doivent fonctionner. Une règle temporaire d'autorisation générale peut masquer le problème et créer une exposition durable.

---

## 2. Configuration et pratique

### 2.1. Scénario de laboratoire

On considère un routeur Cisco IOS de laboratoire entre un petit réseau interne et un réseau externe simulé. Le réseau LAN utilise `192.168.10.0/24` et l'interface interne du routeur porte l'adresse `192.168.10.1`. Le réseau WAN est fourni par le simulateur. L'objectif pédagogique est de comprendre les ACL IPv4 : autoriser certains flux, refuser les autres et examiner les compteurs. Une ACL de routeur n'offre pas automatiquement toutes les fonctions d'un NGFW.

```text
PC-LAN 192.168.10.10 ---- G0/0 [ROUTEUR] G0/1 ---- Réseau extérieur de labo
                                |
                         Filtrage ACL IOS

Exemples de services à autoriser selon le besoin :
- DNS vers un résolveur approuvé
- HTTPS vers une destination de test
- Administration SSH depuis un poste d'admin identifié
```

Avant de coller une configuration dans un équipement réel, confirmez la plateforme, les noms d'interfaces, la version IOS/IOS XE, la connectivité de gestion et le mécanisme de retour arrière. Les commandes exactes diffèrent entre les routeurs, les commutateurs de couche 3 et les appliances NGFW. Utilisez un laboratoire Cisco Packet Tracer ou un environnement isolé pour les premières expérimentations.

### 2.2. Examiner l'équipement avant de modifier les règles

Sur un équipement Cisco IOS compatible, les commandes de lecture suivantes permettent de comprendre l'état du système :

```text
enable
show version
show ip interface brief
show running-config
show access-lists
show ip route
```

`show version` présente des informations sur le logiciel et le matériel. `show ip interface brief` résume l'état des interfaces et leurs adresses. `show running-config` affiche la configuration active ; son contenu peut comprendre des éléments sensibles et doit être traité avec précaution. `show access-lists` permet d'afficher les ACL et, selon la plateforme, des compteurs de correspondance. `show ip route` aide à vérifier si le chemin vers la destination existe.

Ces commandes ne prouvent pas à elles seules qu'une communication doit réussir. Un flux peut être affecté par le routage, le NAT, une ACL sur une autre interface, une politique de pare-feu à états, une règle sur le serveur ou une panne applicative. Le diagnostic doit suivre le chemin du paquet et tenir compte de l'endroit où le filtrage est appliqué.

### 2.3. Construire une ACL standard simple

Les ACL standard IPv4 filtrent principalement sur l'adresse IP source. Dans la syntaxe numérotée classique, les ACL standard utilisent des plages de numéros historiques, tandis que les ACL nommées améliorent souvent la lisibilité. Les fonctionnalités exactes et la disponibilité des commandes dépendent de la version du logiciel.

Exemple de création d'une ACL standard nommée qui autorise seulement le réseau de laboratoire `192.168.10.0/24` :

```text
configure terminal
ip access-list standard LAN-EXEMPLE
 permit 192.168.10.0 0.0.0.255
exit
end
show access-lists LAN-EXEMPLE
```

Le masque générique `0.0.0.255` indique que les trois premiers octets doivent correspondre et que le dernier octet peut varier. Cette ACL autorise le réseau source indiqué, mais l'exemple ne l'applique à aucune interface ; il ne filtre donc pas encore le trafic du routeur. Les ACL doivent être attachées à une interface ou à un autre mécanisme qui les utilise avant d'affecter les paquets concernés.

Une ACL qui contient un seul `permit` inclut implicitement un `deny` à la fin. Il faut donc bien vérifier quelles sources seront affectées avant d'attacher la liste. La position de l'ACL standard est importante : comme elle ne vérifie pas la destination, on l'applique traditionnellement avec prudence, souvent près de la destination dans les conceptions classiques. Cela n'est pas une règle universelle applicable à tous les types de pare-feu.

### 2.4. Comprendre les masques génériques (*wildcard masks*)

Une wildcard mask est utilisée dans de nombreuses ACL Cisco pour indiquer quels bits d'une adresse doivent correspondre. Un bit `0` dans le masque signifie que le bit de l'adresse doit correspondre ; un bit `1` signifie que ce bit peut varier. Elle ressemble à l'inverse d'un masque de sous-réseau, sans être présentée de la même manière dans toutes les syntaxes réseau.

| Réseau ou adresse à faire correspondre | Wildcard Cisco courante | Signification |
|---|---|---|
| Un seul hôte `192.168.10.25` | `0.0.0.0` | Tous les bits doivent correspondre |
| Réseau `192.168.10.0/24` | `0.0.0.255` | Les 24 premiers bits correspondent |
| Réseau `10.20.0.0/16` | `0.0.255.255` | Les 16 premiers bits correspondent |
| Toute adresse IPv4 | `255.255.255.255` | Aucun bit d'adresse n'est imposé |

Une erreur de wildcard peut élargir la règle au-delà de l'intention. Par exemple, confondre `0.0.0.255` et `255.255.255.0` change complètement la correspondance dans une ACL Cisco. Après la configuration, relisez la liste telle qu'elle apparaît avec `show access-lists`, vérifiez les compteurs, puis testez les sources autorisées et interdites.

### 2.5. Créer une ACL étendue de base

Les ACL étendues permettent généralement de filtrer sur les adresses source et destination, les protocoles et les ports. L'exemple ci-dessous illustre une politique de laboratoire qui autorise les postes du LAN à joindre un serveur de test en HTTPS et refuse explicitement les autres flux IP vers ce serveur. Il faut adapter les adresses, l'ordre et les autres services à un exercice précis.

```text
configure terminal
ip access-list extended LAN-VERS-SERVEUR-WEB
 permit tcp 192.168.10.0 0.0.0.255 host 203.0.113.20 eq 443
 deny ip 192.168.10.0 0.0.0.255 host 203.0.113.20 log
 permit ip 192.168.10.0 0.0.0.255 any
exit
end
show access-lists LAN-VERS-SERVEUR-WEB
```

Le mot-clé `host` représente une adresse unique. `eq 443` correspond au port de destination 443 dans cette syntaxe. L'ordre a une importance : la première entrée autorise le flux HTTPS vers le serveur ; la deuxième enregistre et refuse les autres paquets IP de ce réseau vers ce serveur ; la troisième autorise les autres flux IP du LAN vers les autres destinations.

Cette configuration est uniquement un exemple didactique et elle est volontairement large pour les destinations autres que `203.0.113.20`. Elle ne représente pas nécessairement une politique sécurisée de sortie vers Internet. Dans un vrai réseau, les services nécessaires doivent être établis à partir des besoins opérationnels, les réponses aux connexions doivent être prises en compte, et d'autres règles peuvent exister ailleurs dans le chemin.

> **Astuce :** N'ajoutez pas un `permit ip any any` simplement pour « faire fonctionner » le réseau. Cette règle autorise tout trafic IP qui atteint cette position dans la liste et peut rendre inefficaces les restrictions que vous vouliez appliquer.

### 2.6. Appliquer une ACL à une interface

Sur un routeur Cisco IOS, une ACL peut être appliquée à une interface dans le sens entrant (`in`) ou sortant (`out`). Le sens se détermine par rapport au routeur : `in` signifie que le paquet arrive sur l'interface ; `out` signifie qu'il quitte l'interface. Le meilleur emplacement dépend du besoin, du type de liste, de la topologie et du coût du filtrage.

Exemple de syntaxe illustrative :

```text
configure terminal
interface GigabitEthernet0/0
 ip access-group LAN-VERS-SERVEUR-WEB in
exit
end
show ip interface GigabitEthernet0/0
show access-lists LAN-VERS-SERVEUR-WEB
```

Ne copiez pas cet exemple sans valider la direction et l'interface. Une ACL appliquée au mauvais endroit peut couper l'accès administratif, bloquer des services indispensables ou ne jamais voir le flux visé. Les règles d'une ACL s'appliquent aux paquets traversant l'interface dans le sens configuré, et non de façon abstraite à « tout le réseau ».

Avant une modification distante, prévoyez un accès console ou une voie de secours et préparez le retour à la configuration précédente. Une erreur de filtrage sur le chemin d'administration peut vous déconnecter. Dans un environnement de production, utilisez une procédure de changement approuvée, une sauvegarde et une fenêtre de maintenance adaptée.

### 2.7. Filtrer l'accès d'administration aux lignes VTY

Les lignes VTY sont utilisées pour des sessions de gestion distante sur les équipements Cisco. Restreindre les adresses sources autorisées est une mesure utile, mais elle doit s'accompagner d'une authentification forte, de SSH plutôt que de Telnet, d'une gestion sécurisée des secrets et de mises à jour. L'ACL VTY limite les sources autorisées à ouvrir une session de ligne de commande ; elle n'est pas la même chose qu'une ACL filtrant le trafic transitant à travers le routeur.

Exemple conceptuel à adapter à la plateforme et au mécanisme d'authentification :

```text
configure terminal
ip access-list standard ADMIN-AUTORISES
 permit host 192.168.10.50
 deny any log
exit
line vty 0 4
 access-class ADMIN-AUTORISES in
 transport input ssh
exit
end
```

Dans cet exemple, seul le poste `192.168.10.50` est autorisé par cette ACL à accéder aux lignes VTY. Vérifiez la plage réelle des lignes VTY sur le matériel, l'existence de SSH, l'authentification, les privilèges et la configuration complète avant tout déploiement. L'adresse IP source seule n'est pas une identité forte : elle peut être usurpée dans certains contextes et ne remplace pas des mécanismes d'authentification sûrs.

### 2.8. Différence entre ACL IOS et pare-feu à états

Une ACL appliquée au trafic transitant par un routeur examine les paquets selon les critères configurés, mais une ACL seule n'assure pas nécessairement le suivi de l'état TCP de la même façon qu'un pare-feu à états. Une règle qui autorise les connexions initiées depuis le LAN et une règle retour correspondante doivent être conçues avec soin si l'outil de filtrage est stateless. Les ports source dynamiques et le fonctionnement des protocoles rendent l'écriture de règles de retour manuelles délicate.

Un pare-feu à états conserve des informations sur les connexions et peut autoriser les paquets de retour appartenant à une session autorisée, sans ouvrir pour autant une nouvelle connexion entrante vers toute adresse interne. Toutefois, le mécanisme exact dépend du produit : il faut apprendre les états de connexion, les règles de politique et les particularités de la plateforme concernée.

Cisco IOS/IOS XE peut proposer des fonctions de pare-feu à états, notamment le Zone-Based Policy Firewall (ZBF), sur les versions et équipements compatibles. Ce mécanisme repose sur des zones, des classes de trafic et des politiques. Il est distinct des ACL classiques et des NGFW dédiés. Les commandes du ZBF ne doivent pas être mélangées à l'aveugle avec une autre méthode de filtrage sur une même interface ; consultez le guide correspondant à la version exacte du logiciel.

### 2.9. Modèle conceptuel de politiques par zones

Dans un pare-feu à zones, on associe des interfaces à des zones comme LAN, WAN ou DMZ, puis on définit les flux autorisés entre ces zones. De nombreux modèles à zones adoptent une posture restrictive entre les zones tant qu'une politique explicite n'a pas été créée. C'est une approche plus structurée que d'ajouter des listes isolées sans vue générale des communications.

Une matrice simple peut servir à préparer les règles :

| Source | Destination | Besoin | Décision de conception |
|---|---|---|---|
| LAN utilisateurs | DNS approuvés | Résoudre les noms | Autoriser uniquement les services nécessaires |
| LAN utilisateurs | DMZ / serveur Web | Administration ou usage métier précis | Limiter selon le rôle réel |
| Internet | Serveur Web en DMZ | Publication HTTPS | Autoriser uniquement le service publié |
| Internet | LAN utilisateurs | Aucun accès direct attendu | Refuser par défaut |
| Poste administrateur | Équipements réseau | SSH/HTTPS de gestion | Autoriser depuis la zone d'administration, journaliser |
| Serveur Web en DMZ | Base de données | Accès applicatif précis | Autoriser uniquement destination et port nécessaires |
| Wi-Fi invité | LAN interne | Aucun besoin normal | Refuser ; fournir seulement l'accès Internet requis |

La matrice doit être validée avec les propriétaires des applications. Les exceptions temporaires doivent être identifiées comme telles, avec une date d'expiration. Sans cette discipline, les règles s'accumulent et deviennent difficiles à comprendre. Une documentation claire facilite les audits, les dépannages et le remplacement d'un équipement.

### 2.10. Notions pratiques liées aux NGFW

Un NGFW dédié est souvent administré par une interface graphique, une console en ligne de commande ou une plateforme centralisée. L'administrateur crée des objets d'adresse et de service, choisit les zones source et destination, sélectionne les utilisateurs ou applications si nécessaire, définit l'action, puis configure la journalisation et les fonctions d'inspection. Les intitulés diffèrent selon les constructeurs ; l'important est de comprendre la logique, pas de mémoriser une interface particulière.

Lorsqu'une politique NGFW utilise l'identification applicative, il faut vérifier ce que l'équipement considère comme cette application, les conditions de détection et les cas où le flux reste classé comme inconnu. Une politique peut être trop restrictive et casser un service si elle n'autorise que des applications identifiées avec certitude sans prévoir de procédure de découverte. À l'inverse, autoriser toute application inconnue peut offrir une voie de contournement. Une phase d'observation contrôlée, suivie d'un ajustement, peut aider à bâtir une politique fiable.

Les fonctions IPS, antivirus réseau ou filtrage de fichiers doivent être dimensionnées et maintenues. Les mises à jour des signatures et du moteur sont essentielles, tout comme l'analyse des alertes. Les règles de prévention peuvent provoquer des faux positifs ; en production, les exclusions doivent être limitées, documentées et revues. Une exclusion permanente et large finit souvent par réduire la visibilité précisément là où elle était nécessaire.

L'inspection HTTPS approfondie, parfois appelée déchiffrement TLS, exige de comprendre les certificats et la confiance des postes clients. Elle peut être incompatible avec certaines applications, appareils personnels ou services sensibles. Une organisation doit définir les flux concernés, les exceptions, la protection des journaux et les obligations de confidentialité. Il ne faut jamais activer cette fonction uniquement parce qu'un tableau de bord la propose : son impact technique et organisationnel doit être évalué.

### 2.11. Journalisation et lecture des événements

Une règle peut être configurée pour journaliser les correspondances, mais journaliser chaque paquet de tous les flux peut produire un volume énorme et consommer des ressources. Les journaux doivent aider à répondre à une question : quelles communications sont refusées, quelle règle s'applique, à quelle heure, depuis quelle source, vers quelle destination et avec quel résultat ? Le niveau approprié dépend du risque et de l'environnement.

Pour commencer, journalisez les événements importants comme les tentatives d'administration refusées, les accès entrants non prévus vers des serveurs, les violations de règles sensibles et les modifications de configuration. Envoyez les journaux vers un collecteur central si cela est possible ; les données conservées uniquement sur le pare-feu peuvent disparaître lors d'une panne ou d'une compromission. Protégez les accès aux journaux et synchronisez les horloges afin que les événements de plusieurs équipements puissent être corrélés.

Les logs peuvent contenir des adresses IP, des noms d'utilisateur, des URL ou d'autres métadonnées sensibles. Limitez les accès, définissez une durée de rétention cohérente avec les besoins et les obligations applicables, et évitez de consigner inutilement des données privées. La collecte doit être proportionnée au risque et à l'objectif de sécurité.

### 2.12. Test de base après une modification

Après toute modification de pare-feu, testez aussi bien les communications qui doivent fonctionner que celles qui doivent échouer. Un seul test réussi n'est pas suffisant : il faut vérifier que la règle n'a pas autorisé davantage que prévu. Utilisez plusieurs sources lorsque le contrôle dépend de l'adresse IP ou de la zone.

```text
# Depuis un poste de laboratoire, selon les outils disponibles :
ping 192.168.10.1
nslookup example.com
curl -I https://example.com
tracert 203.0.113.20       # Windows
traceroute 203.0.113.20    # Linux/macOS, si installé
```

Les commandes dépendent du système. Un échec de `ping` ne prouve pas toujours que l'hôte est inaccessible, car ICMP peut être filtré alors que HTTPS fonctionne. Un `nslookup` réussi prouve seulement que la résolution demandée a reçu une réponse ; il ne vérifie pas les autorisations HTTP ou les règles entre autres zones. Faites correspondre chaque test au besoin métier.

> **Danger :** Ne testez pas une règle destructive ou une politique d'administration directement sur un équipement de production sans sauvegarde, autorisation et moyen de récupération. Une configuration de pare-feu peut couper l'accès au réseau entier, y compris à l'outil utilisé pour corriger l'erreur.

---

## 3. Dépannage et sécurité

### 3.1. Commencer par localiser le point de blocage

Lorsqu'une application ne fonctionne pas, évitez de modifier immédiatement le pare-feu. Vérifiez d'abord si le poste possède une adresse IP valide, une passerelle par défaut et des serveurs DNS corrects. Ensuite, vérifiez la route, la résolution de nom, la disponibilité de la destination et les journaux des équipements placés sur le chemin. Une panne peut provenir du client, du réseau local, du routeur, du pare-feu, du NAT, du serveur ou de l'application.

Une méthode de diagnostic progressive consiste à tester :

1. La connectivité locale vers la passerelle.
2. La présence d'une adresse et d'une route appropriées.
3. La résolution DNS si l'accès se fait par nom.
4. La connectivité vers l'adresse de destination, en tenant compte du filtrage ICMP.
5. Le port ou le service réellement requis.
6. Les journaux et compteurs de la règle attendue.
7. La réponse de l'application côté serveur.

Un chemin réseau peut comporter plusieurs filtres : pare-feu hôte du client, ACL de commutateur ou routeur, pare-feu du site, pare-feu cloud, groupe de sécurité cloud et pare-feu de serveur. Il faut identifier quel composant voit le trafic. Une règle permissive sur le premier pare-feu ne suffit pas si un second équipement bloque le flux.

### 3.2. Pannes fréquentes et pistes de vérification

| Symptôme | Causes possibles | Vérifications utiles |
|---|---|---|
| Le site ne répond pas par son nom | DNS indisponible ou mauvaise configuration | Résoudre le nom, comparer avec l'IP, vérifier la destination DNS |
| Le site ne répond pas, mais d'autres sites fonctionnent | Règle de destination, panne serveur, filtrage applicatif | Contrôler adresse, port, logs et disponibilité du serveur |
| Le service marche depuis le LAN mais pas depuis Internet | Publication NAT, règle WAN, route, DNS public | Vérifier la traduction, le filtrage entrant et le chemin retour |
| Une application ne fonctionne que parfois | États expirés, perte réseau, inspection ou serveur instable | Comparer les horaires, la table de sessions et les événements |
| Un administrateur ne peut plus se connecter | ACL VTY, SSH, route, identifiants, source non autorisée | Utiliser la console de secours et consulter les journaux |
| Le ping échoue mais le Web fonctionne | ICMP bloqué ou limité | Tester le service TCP approprié, ne pas se fier au ping seul |
| Un flux autorisé est quand même refusé | Mauvaise règle, ordre, zone ou règle suivante | Examiner l'ordre d'évaluation, le sens et les compteurs |
| Les connexions sortantes sont lentes | Inspection, surcharge, MTU, problème hors pare-feu | Comparer les métriques, la charge, les logs et le réseau environnant |

Le tableau propose des pistes, pas des conclusions automatiques. Par exemple, des lenteurs peuvent provenir d'un fournisseur d'accès, du DNS, d'un serveur distant ou d'une application, même si elles sont signalées après une modification du pare-feu. Il faut comparer des mesures avant/après et rechercher des preuves.

### 3.3. Erreurs d'ACL courantes

**Mauvais ordre des règles.** Une règle large placée avant une règle précise peut capturer le trafic avant que la règle restrictive soit examinée. Lisez la politique du haut vers le bas pour une ACL Cisco classique et vérifiez les règles effectivement comptabilisées.

**Erreur d'adresse ou de wildcard.** Une faute dans le réseau source ou la wildcard change le groupe de machines concernées. Contrôlez le plan d'adressage et testez des adresses représentatives, dont une adresse qui doit être autorisée et une autre qui doit être refusée.

**Mauvais sens d'application.** Une ACL en entrée et une ACL en sortie ne voient pas le paquet au même endroit. Dessinez le trajet et indiquez le sens des interfaces pour éviter de bloquer le trafic de réponse sans le vouloir.

**Oubli du refus implicite.** Dans les ACL traditionnelles concernées, un paquet qui ne correspond à aucune entrée est refusé. Ajouter un `permit` ciblé peut être suffisant, mais doit être placé correctement. N'ajoutez pas une autorisation générale sans comprendre l'effet sur les autres flux.

**Règle trop large.** `permit ip any any` peut être utile dans un environnement de laboratoire très contrôlé, mais sur un chemin sensible il peut autoriser plus de trafic que souhaité. Il faut expliquer, limiter et réviser chaque autorisation générale.

**Effet sur l'administration.** Une ACL mal appliquée peut couper la session distante. Préparez une console ou un accès hors bande, effectuez les changements par étapes, sauvegardez la configuration initiale et vérifiez la capacité de retour arrière.

### 3.4. Pourquoi il faut éviter les exceptions permanentes

Lorsqu'un service est bloqué, une exception temporaire peut aider à isoler la cause, mais elle doit être limitée par source, destination, service et durée autant que possible. L'exception doit avoir un propriétaire, une justification et une date d'expiration. À la fin du test, restaurez la règle correcte et vérifiez que l'exception n'est plus présente.

Les environnements réels souffrent souvent de règles anciennes qui ont été ajoutées pour résoudre une urgence et jamais retirées. Elles augmentent la complexité et peuvent permettre un accès qui n'est plus nécessaire. Un nettoyage des règles doit s'appuyer sur les compteurs, les journaux, l'inventaire des applications et la validation des responsables ; l'absence de correspondance pendant une courte période ne prouve pas toujours qu'une règle est inutile.

### 3.5. Sécuriser l'administration du pare-feu

Le plan de gestion doit être protégé séparément du trafic utilisateur. Limitez les accès de gestion à une zone et à des postes dédiés. Utilisez des comptes nominatifs, des mots de passe forts, une authentification multifacteur quand elle est proposée, et un contrôle des privilèges. Évitez de publier l'interface d'administration sur Internet si ce n'est pas absolument nécessaire ; un accès via VPN ou réseau de gestion peut être plus approprié.

Remplacez les identifiants par défaut et supprimez les comptes inutiles. Utilisez des protocoles chiffrés tels que SSH ou HTTPS pour l'administration, plutôt que Telnet ou des interfaces non chiffrées. Stockez les secrets dans un coffre approprié et ne les copiez pas dans des documents ou scripts accessibles à tous. Les comptes de service doivent disposer du minimum de privilèges nécessaire.

Gardez le système à jour selon une procédure maîtrisée : suivez les avis du fournisseur, évaluez l'impact, sauvegardez la configuration, testez les changements si possible et gardez un plan de restauration. Une mise à jour ne doit pas être improvisée, mais ne doit pas non plus être repoussée indéfiniment par confort. Les équipements en fin de support posent un risque et doivent être planifiés pour remplacement.

### 3.6. Sauvegarde, haute disponibilité et continuité

La configuration du pare-feu doit être sauvegardée après les changements approuvés et à intervalles réguliers. Protégez les sauvegardes contre l'accès non autorisé ; une configuration peut révéler la topologie, les adresses, les comptes ou des éléments sensibles. Testez la restauration, car un fichier de sauvegarde jamais restauré n'est pas une preuve de reprise réussie.

La haute disponibilité, lorsqu'elle est disponible, peut maintenir le service en cas de panne d'un membre ou d'une liaison. Mais elle implique d'autres questions : la synchronisation des sessions, les liens redondants, le comportement en cas de split-brain, les tests de bascule, les licences et les dépendances externes. Un cluster ne protège pas contre toutes les erreurs de politique, les mises à jour problématiques ou la panne du réseau amont.

Les tests de reprise doivent être planifiés et documentés. Il faut connaître les personnes qui peuvent approuver une modification en urgence, la méthode de contact du fournisseur, les sauvegardes nécessaires et les étapes pour revenir à l'état stable. La continuité dépend autant des procédures que du matériel.

### 3.7. Journalisation et surveillance de sécurité

Surveillez les refus inattendus, les tentatives répétées vers des ports d'administration, les flux depuis des segments qui ne devraient pas communiquer et les changements de configuration non planifiés. Corrélez les événements avec les journaux des serveurs, des postes, du DNS, des VPN et des outils de détection. Une seule ligne de journal fournit rarement le contexte complet d'un incident.

Assurez-vous que l'horloge du pare-feu est synchronisée avec une source de temps fiable. Des horodatages incohérents compliquent la reconstruction d'un incident. Vérifiez la rétention, la capacité de stockage, la protection contre l'altération et l'accès réservé aux personnes autorisées. Les alertes doivent être suffisamment précises pour déclencher une action et suffisamment bien réglées pour éviter la fatigue liée aux faux positifs.

Un refus répété ne signifie pas nécessairement qu'une attaque est en cours : il peut provenir d'une application mal configurée ou d'une destination obsolète. De la même manière, l'absence de refus ne prouve pas qu'il n'y a aucun problème. Il faut comprendre les règles, comparer avec la ligne de base du réseau et analyser les événements dans leur contexte.

### 3.8. Sécurité sortante et limitation des communications

Les politiques se concentrent parfois uniquement sur les connexions entrantes. Pourtant, contrôler les sorties peut réduire le risque qu'un poste compromis communique avec un serveur de commande ou exfiltre des données. Une politique de sortie peut limiter certains services à des serveurs approuvés, restreindre les outils d'administration distante, appliquer une politique DNS et identifier les applications non attendues.

Un filtrage sortant strict nécessite un inventaire des besoins. Bloquer sans plan tous les protocoles autres que HTTPS peut interrompre les mises à jour, les systèmes de gestion, les appels vidéo ou des applications métier. Une approche adaptée consiste à observer les usages, créer une politique explicite, tester les exceptions et suivre les nouvelles demandes. Les connexions sortantes autorisées doivent rester proportionnées au besoin.

Ne présumez pas que tout trafic sur TCP 443 est du Web légitime. Les tunnels et les applications malveillantes peuvent tenter d'utiliser des ports courants. Les NGFW peuvent aider à identifier certaines applications ou destinations, mais l'évasion et le chiffrement limitent parfois la visibilité. Il faut combiner le filtrage avec une protection des terminaux, une gestion des identités et une surveillance appropriée.

### 3.9. Segmentation : réduire les mouvements latéraux

Si tous les appareils peuvent communiquer librement, la compromission d'un poste peut faciliter l'accès à d'autres équipements. La segmentation divise le réseau en parties séparées par des VLAN, des sous-réseaux et/ou des contrôles de sécurité. Le pare-feu peut alors n'autoriser que les flux nécessaires entre postes utilisateurs, serveurs, invités, IoT et administration.

La segmentation n'est utile que si les frontières sont réellement appliquées. Deux VLAN avec routage libre et sans règles restrictives n'offrent pas automatiquement une isolation forte. Il faut également contrôler l'accès aux interfaces de gestion, les protocoles de découverte, les services partagés et les chemins alternatifs comme le Wi-Fi ou le VPN. Le schéma logique doit correspondre au fonctionnement réel du réseau.

Commencez par séparer les catégories qui ont des besoins et des risques différents. Le Wi-Fi invité, par exemple, devrait normalement accéder à Internet sans atteindre les postes et serveurs internes. Les équipements d'administration devraient être joignables uniquement depuis une zone approuvée. Les serveurs accessibles depuis Internet doivent être isolés des réseaux de travail ordinaires.

### 3.10. Procédure de changement recommandée

Une modification de pare-feu devrait suivre une procédure reproductible :

1. Décrire le besoin et le risque associé.
2. Identifier le flux exact : source, destination, service, sens et zones.
3. Vérifier les dépendances et les règles déjà existantes.
4. Obtenir l'approbation prévue par l'organisation.
5. Sauvegarder la configuration et préparer le retour arrière.
6. Appliquer le changement dans une fenêtre adaptée.
7. Tester les accès attendus et les accès qui doivent rester bloqués.
8. Examiner les journaux et compteurs.
9. Documenter le résultat et mettre à jour l'inventaire.
10. Programmer la revue ou l'expiration de la règle si elle est temporaire.

Cette procédure est particulièrement importante pour les règles qui touchent les accès VPN, le routage, l'authentification ou l'administration. Il est préférable de faire une modification ciblée, puis de mesurer son effet, plutôt que de changer simultanément de nombreuses règles : plusieurs changements à la fois rendent les causes des problèmes difficiles à isoler.

### 3.11. Exercice guidé : publier un serveur Web

Considérez l'entreprise fictive suivante : un serveur Web est dans une DMZ avec l'adresse privée `10.10.20.10`. Le pare-feu possède une adresse publique fournie par le fournisseur d'accès. Le site doit être accessible publiquement en HTTPS, mais le serveur Web ne doit pas pouvoir initier librement des connexions vers les postes internes.

Avant de configurer quoi que ce soit, répondez à ces questions :

- Le nom DNS public pointe-t-il vers la bonne adresse publique ?
- Une traduction NAT ou un mécanisme de publication est-il nécessaire ?
- La politique entrante autorise-t-elle uniquement TCP 443 vers le serveur publié ?
- Les autres connexions provenant d'Internet vers la DMZ sont-elles refusées par défaut ?
- Le serveur doit-il joindre une base de données ou un service d'identité ? Si oui, à quelle adresse et sur quel port ?
- L'administration se fait-elle depuis une zone dédiée plutôt que depuis Internet ?
- Les journaux permettent-ils de distinguer les connexions attendues des refus ?
- La règle a-t-elle été testée depuis un réseau extérieur au LAN ?

La conception ne s'arrête pas au pare-feu. Le serveur doit être à jour, ne pas exposer de services inutiles, protéger ses secrets, disposer de sauvegardes et produire des journaux utiles. La base de données ne devrait pas être directement publiée vers Internet. Les données sensibles doivent être protégées selon leur niveau de risque.

### 3.12. Exercice guidé : un poste n'accède pas au Web

Un utilisateur signale qu'il ne peut pas ouvrir un site. Les autres utilisateurs semblent fonctionner. Ne créez pas immédiatement une règle générale. Demandez le nom du site, l'heure du problème, le message exact et si l'accès échoue depuis un autre poste. Déterminez si le souci concerne un seul domaine ou tout le Web.

Résolvez ensuite le nom DNS. Comparez la réponse avec les journaux DNS approuvés. Testez le port HTTPS avec un outil adapté. Recherchez les événements du pare-feu correspondant à l'adresse IP du poste et à l'heure du test. Vérifiez également le pare-feu local du poste, le proxy éventuel, le certificat TLS et le service distant. Une règle NGFW peut bloquer une catégorie ou une application même lorsque le port 443 est ouvert.

Si le journal montre un refus, vérifiez la règle et la raison du refus, puis confirmez avec le propriétaire du service que le besoin est légitime. Si aucune ligne n'apparaît, cela ne signifie pas forcément que le pare-feu est innocent : les logs peuvent être désactivés, le flux peut utiliser un autre équipement ou le paquet peut ne pas atteindre le point d'observation.

### 3.13. Exercice guidé : accès d'administration depuis la mauvaise zone

Supposez que l'interface SSH d'un routeur ne devrait être accessible que depuis le réseau d'administration. Un test révèle qu'un poste du réseau utilisateurs peut ouvrir une session. La première action consiste à vérifier les règles du plan de gestion, l'ACL appliquée aux lignes VTY et les autres moyens d'accès. Il faut également vérifier si SSH est accessible sur une autre interface ou adresse que celle prévue.

La correction doit réduire l'accès aux sources administratives approuvées, confirmer que l'accès légitime continue de fonctionner et journaliser les refus utiles. Un test de sécurité doit couvrir les deux cas : la source d'administration doit réussir, le poste utilisateur doit échouer. Vérifiez ensuite les comptes, les clés ou mots de passe, les privilèges, les versions du logiciel et l'historique des connexions.

Si une session distante est utilisée pour appliquer la restriction, préparez un accès de secours. La règle de contrôle du plan de gestion doit être testée avec prudence afin d'éviter de verrouiller l'équipe d'administration hors de l'équipement.

### 3.14. Sécurité des règles : bonnes pratiques de base

- Autorisez uniquement les flux justifiés et limitez les sources et destinations autant que possible.
- Distinguez les services publiés depuis Internet des services internes et des interfaces d'administration.
- Préférez des objets nommés et documentés à des règles anonymes difficiles à comprendre.
- Évitez les doublons, les règles inutilisées et les exceptions sans date de révision.
- Journalisez les événements importants, sans générer inutilement un volume incontrôlable.
- Sauvegardez la configuration et conservez un plan de retour arrière.
- Testez les accès autorisés et ceux qui doivent rester interdits.
- Mettez à jour l'équipement et les fonctions de sécurité selon une procédure maîtrisée.
- Protégez le compte administrateur et séparez autant que possible le plan de gestion.
- Faites valider les règles sensibles par les propriétaires des applications et les responsables de sécurité.

> **Danger :** Ne confondez jamais « le trafic est autorisé » avec « le trafic est sûr ». Une politique de pare-feu réduit certains chemins de communication ; elle ne garantit ni l'absence de vulnérabilité ni l'innocuité des données qui circulent par un service légitime.

---

## Points à retenir

- Un pare-feu applique une politique de communication entre hôtes, réseaux ou zones.
- Les adresses IP, protocoles, ports, interfaces et zones sont des critères de filtrage courants.
- Les ACL classiques, les pare-feu à états, les proxies, les pare-feu hôtes et les NGFW ont des capacités différentes.
- Un NGFW peut ajouter une identification applicative, un IPS, un filtrage Web ou d'autres fonctions, mais celles-ci dépendent du produit, des licences, des mises à jour et de la configuration.
- Le principe « refuser par défaut » limite les communications aux besoins explicitement autorisés.
- Une règle doit être spécifique, justifiée, documentée, testée et révisée.
- L'ordre d'évaluation est essentiel : une règle large peut rendre une restriction suivante inopérante.
- Le NAT traduit des adresses ou des ports ; il ne remplace pas une politique de filtrage.
- La segmentation réduit les chemins de mouvement latéral, à condition de contrôler réellement les communications entre zones.
- Le trafic entrant, sortant et interzone mérite une politique adaptée ; le réseau interne ne doit pas être considéré comme automatiquement fiable.
- La journalisation, la synchronisation de l'heure et la centralisation des événements facilitent le dépannage et la réponse aux incidents.
- La gestion sécurisée, les sauvegardes, les mises à jour et une procédure de retour arrière sont indispensables.
- Un échec de `ping` ne prouve pas toujours une panne de service, et une règle qui autorise HTTPS ne garantit pas qu'une application est légitime.
- Une configuration doit être testée dans les deux sens : valider les flux requis et s'assurer que les flux non prévus restent bloqués.

### Questions de révision

1. À quoi sert un pare-feu dans un réseau d'entreprise ?
2. Quelle différence y a-t-il entre une adresse IP source et un port de destination ?
3. Pourquoi un pare-feu à états est-il différent d'une ACL stateless ?
4. Que signifie « refuser par défaut » ?
5. Pourquoi les règles doivent-elles être ordonnées et documentées ?
6. Quelle différence existe entre NAT et filtrage de sécurité ?
7. Pourquoi placer un serveur Web public dans une DMZ ?
8. Citez trois fonctions que peut ajouter un NGFW.
9. Pourquoi ne faut-il pas considérer l'échec de `ping` comme une preuve suffisante que le serveur est indisponible ?
10. Quelles précautions prendre avant de modifier à distance une ACL qui protège les lignes d'administration ?
11. Pourquoi faut-il limiter également certaines connexions sortantes ?
12. Quels tests effectuer après une modification de règle ?

### Mini-cas pratiques

**Cas A — Tous les utilisateurs perdent l'accès à Internet après un changement.** Vérifiez la configuration avant/après, l'interface concernée, le sens de l'ACL, l'ordre des règles, le routage, le NAT et les compteurs. Rétablissez un état sûr selon le plan de retour arrière si l'impact est important.

**Cas B — Le serveur Web est joignable depuis Internet sur plusieurs ports.** Vérifiez la publication NAT, les règles entrantes, les services à l'écoute sur le serveur et les autres chemins d'accès. Réduisez l'exposition aux seuls ports autorisés après validation du besoin.

**Cas C — Une nouvelle application métier est bloquée par le NGFW.** Identifiez l'application et ses dépendances, consultez les journaux et la documentation du fournisseur, puis définissez une exception ciblée si elle est légitime. N'ajoutez pas de règle globale pour l'ensemble du réseau.

**Cas D — Les journaux sont trop volumineux pour être analysés.** Identifiez les événements prioritaires, ajustez les niveaux de journalisation lorsque c'est possible, centralisez-les et créez des filtres/alertes. Préservez les événements utiles à la sécurité et à la conformité plutôt que de supprimer toute journalisation.

### Références techniques

- NIST, *Guidelines on Firewalls and Firewall Policy*, Special Publication 800-41 Revision 1 : https://csrc.nist.gov/pubs/sp/800/41/r1/final
- Cisco, *Understand the Zone-Based Policy Firewall Design* : https://www.cisco.com/c/en/us/support/docs/security/ios-firewall/98628-zone-design-guide.html
- Cisco, *Security Configuration Guide: Zone-Based Policy Firewall, Cisco IOS XE* : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_zbf/configuration/xe-3s/sec-data-zbf-xe-book/sec-zone-pol-fw.html
- Cisco, *IOS Firewall — Configuration Examples and TechNotes* : https://www.cisco.com/c/en/us/support/security/ios-firewall/products-configuration-examples-list.html

Ces références donnent un cadre et des exemples, mais les commandes et fonctions disponibles dépendent de la version logicielle, du modèle d'équipement et de la licence. Pour une configuration opérationnelle, consultez le guide officiel correspondant précisément à la plateforme utilisée et testez les changements dans un environnement maîtrisé.
