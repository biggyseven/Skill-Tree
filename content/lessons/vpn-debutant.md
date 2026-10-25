# VPN et tunnels — Niveau Débutant

> **Niveau :** Débutant  
> **Objectif :** comprendre le rôle d'un VPN, suivre le trajet des paquets, distinguer tunnel et chiffrement, puis apprendre à vérifier et dépanner une petite liaison VPN.


## Sommaire

1. Parcours pratique du débutant
2. Objectifs pédagogiques
3. Les problèmes qu'un VPN résout
4. Les notions indispensables
5. Tunnel, encapsulation et chiffrement
6. Les principaux types de VPN
7. GRE, IP-in-IP, IPsec, TLS et WireGuard
8. Comment fonctionne IPsec
9. Routage et adressage
10. NAT, pare-feu et ports
11. MTU et fragmentation
12. Sécurité et bonnes pratiques
13. Lire un schéma de VPN
14. Laboratoire guidé
15. Vérifications et dépannage
16. Erreurs fréquentes
17. Exercices pratiques
18. Quiz de validation
19. Liste de contrôle
20. Glossaire
21. Pour aller plus loin


## 1. Parcours pratique du débutant

Le but n'est pas de mémoriser immédiatement tous les protocoles. Il faut d'abord comprendre le problème, visualiser le trajet des paquets, puis apprendre à vérifier chaque étape.

### Étape 1 — Comprendre le besoin

Une entreprise possède deux bureaux : le site A à Douala et le site B à Yaoundé. Les deux bureaux doivent communiquer via Internet pour accéder à des serveurs et échanger des données.

Un VPN (*Virtual Private Network*, ou réseau privé virtuel) permet de créer une liaison logique protégée au-dessus du réseau de transport.

```text
Réseau du site A           Internet             Réseau du site B
192.168.10.0/24                                  192.168.20.0/24
      |                                                |
   [Routeur A] ======= tunnel VPN sécurisé ======= [Routeur B]
```

**À retenir :** un VPN ne remplace pas Internet. Il utilise Internet ou un autre réseau de transport pour créer une liaison logique entre deux extrémités.

### Étape 2 — Suivre un paquet de bout en bout

Un ordinateur `192.168.10.10` veut communiquer avec un serveur `192.168.20.20`.

1. L'ordinateur constate que le serveur se trouve dans un autre sous-réseau.
2. Il envoie le paquet à sa passerelle par défaut.
3. Le routeur A consulte sa table de routage et choisit le tunnel pour joindre `192.168.20.0/24`.
4. Le paquet d'origine est encapsulé dans un paquet externe destiné au routeur B.
5. Le paquet externe traverse le réseau de transport.
6. Le routeur B reçoit le paquet, vérifie la protection si elle est utilisée, puis retire l'encapsulation.
7. Le paquet interne est acheminé vers le serveur.

```text
PAQUET INTERNE AVANT LE TUNNEL
Source :      192.168.10.10
Destination : 192.168.20.20

                  |
                  v
           [Routeur A]
      Encapsulation du paquet
                  |
                  v

PAQUET EXTERNE SUR INTERNET
Source externe :      IP WAN du routeur A
Destination externe : IP WAN du routeur B
Contenu :             paquet interne encapsulé et éventuellement chiffré

                  |
                  v
           [Routeur B]
      Vérification et décapsulation
                  |
                  v

PAQUET INTERNE APRÈS LE TUNNEL
Source :      192.168.10.10
Destination : 192.168.20.20
```

**À retenir :** les adresses internes identifient les machines des réseaux locaux. Les adresses externes permettent de transporter le tunnel entre les passerelles.

### Étape 3 — Préparer le plan d'adressage

Avant de configurer le VPN, note les informations importantes.

| Élément | Site A | Site B |
|---|---|---|
| Réseau LAN | `192.168.10.0/24` | `192.168.20.0/24` |
| Passerelle LAN | `192.168.10.1` | `192.168.20.1` |
| Adresse WAN | IP WAN du routeur A | IP WAN du routeur B |
| Réseau distant | `192.168.20.0/24` | `192.168.10.0/24` |

Les adresses WAN exactes dépendront de ton laboratoire ou de ton réseau réel.

Vérifie deux choses :

- les réseaux LAN des deux sites ne se chevauchent pas ;
- chaque routeur possède un chemin vers le réseau distant.

Si les deux sites utilisent `192.168.1.0/24`, le routage devient ambigu. Il est généralement préférable de renuméroter l'un des sites.

### Étape 4 — Distinguer les fonctions réseau

Il faut séparer plusieurs notions qui sont souvent confondues.

| Fonction | Rôle |
|---|---|
| Routage | Choisir le chemin emprunté par un paquet |
| Tunnel | Transporter un paquet à l'intérieur d'une autre enveloppe |
| Chiffrement | Empêcher les tiers de lire le contenu protégé |
| Authentification | Vérifier l'identité d'un utilisateur ou d'un pair |
| Intégrité | Détecter une modification non autorisée |
| Pare-feu | Autoriser ou refuser le trafic selon des règles |

GRE, par exemple, fournit un mécanisme d'encapsulation, mais ne chiffre pas le trafic à lui seul. IPsec peut fournir chiffrement, intégrité et authentification selon la configuration.

### Étape 5 — Vérifier le VPN dans le bon ordre

Lorsqu'un VPN ne fonctionne pas, évite de modifier toutes les commandes à la fois.

1. Vérifie que les interfaces sont actives.
2. Vérifie les adresses IP, les masques et les passerelles.
3. Vérifie la connectivité entre les adresses WAN des pairs.
4. Vérifie la configuration et l'état du VPN.
5. Vérifie les routes vers les réseaux distants.
6. Vérifie les règles de pare-feu et de NAT.
7. Vérifie le trafic dans les deux sens.

Un tunnel peut être établi sans que les applications fonctionnent. Le tunnel, le routage, les règles de filtrage et les paramètres des hôtes doivent tous être corrects.

### Étape 6 — Relier les symptômes aux hypothèses

| Symptôme | Première piste à vérifier |
|---|---|
| Les pairs ne sont pas joignables | Adresses WAN, routes, pare-feu |
| Le VPN ne s'établit pas | Authentification, paramètres cryptographiques, négociation |
| Le tunnel est actif mais les LAN ne communiquent pas | Routes, ACL, NAT, sélecteurs de trafic |
| Les petits paquets passent mais pas les gros | MTU, PMTUD, filtrage ICMP |
| Un seul sens fonctionne | Route de retour, ACL, NAT, routage asymétrique |

Ce tableau donne des pistes de diagnostic, pas des certitudes. Chaque hypothèse doit être confirmée par des tests.

### Validation du parcours débutant

Avant de passer à la suite, tu dois pouvoir :

- [ ] expliquer le problème qu'un VPN résout ;
- [ ] dessiner le trajet d'un paquet entre deux LAN ;
- [ ] identifier les adresses internes et externes ;
- [ ] expliquer pourquoi GRE seul ne chiffre pas les données ;
- [ ] citer au moins quatre causes possibles d'un tunnel inutilisable.


## 2. Objectifs pédagogiques

À la fin de ce cours, tu devrais pouvoir :

- définir un VPN et un tunnel ;
- distinguer un VPN site-à-site d'un VPN d'accès distant ;
- expliquer l'encapsulation et la décapsulation ;
- distinguer GRE, IP-in-IP, IPsec, TLS VPN et WireGuard ;
- comprendre le rôle général d'IKE et d'ESP dans IPsec ;
- identifier les éléments d'adressage, de routage et de filtrage nécessaires ;
- expliquer l'effet du surcoût d'encapsulation sur la MTU ;
- suivre une méthode de dépannage structurée.

Ce cours est une introduction. Les commandes exactes dépendent du constructeur, du modèle d'équipement et de la version logicielle.


## 3. Les problèmes qu'un VPN résout

Un VPN est une liaison logique qui utilise un réseau de transport pour connecter des utilisateurs ou des réseaux. Selon la technologie et sa configuration, il peut protéger les communications grâce au chiffrement, à l'authentification et au contrôle d'intégrité.

### 3.1 VPN site-à-site

Il relie généralement deux réseaux locaux, par exemple deux agences. Les passerelles VPN assurent la protection du trafic entre les sites.

```text
LAN A                         INTERNET                         LAN B
192.168.10.0/24                                          192.168.20.0/24
     |                                                        |
 [Passerelle A] ============ tunnel VPN ============ [Passerelle B]
```

Les utilisateurs n'ont pas forcément besoin de lancer un logiciel VPN sur leur ordinateur : les passerelles peuvent gérer le tunnel.

### 3.2 VPN d'accès distant

Il permet à un utilisateur situé hors du bureau de rejoindre certaines ressources internes après authentification.

```text
[Ordinateur distant]
        |
        v
 [Internet ou réseau mobile]
        |
        v
   [Passerelle VPN]
        |
        v
 [Réseau de l'entreprise]
```

Les accès accordés dépendent de l'identité de l'utilisateur, de la politique de sécurité et des ressources autorisées.

### 3.3 Ce qu'un VPN ne garantit pas automatiquement

Un VPN ne garantit pas à lui seul :

- que l'appareil connecté est exempt de logiciel malveillant ;
- que l'utilisateur ne peut accéder qu'aux ressources nécessaires ;
- que les serveurs internes sont correctement sécurisés ;
- que les données restent protégées après leur arrivée à destination ;
- que tout le trafic Internet passe par le VPN.

Le dernier point dépend notamment du routage et de la politique choisie : *full tunnel* ou *split tunnel*.

Le VPN est une composante d'une architecture de sécurité, pas une solution complète à tous les risques.


## 4. Les notions indispensables

### 4.1 Adresse IP et sous-réseau

Une adresse IP identifie une interface sur un réseau. Le préfixe CIDR, comme `/24`, indique la taille du réseau.

Dans `192.168.10.0/24`, les adresses hôtes habituelles vont de `192.168.10.1` à `192.168.10.254`.

Les deux LAN du scénario sont :

- site A : `192.168.10.0/24` ;
- site B : `192.168.20.0/24`.

Un ordinateur du site A comprend que `192.168.20.20` n'appartient pas à son réseau local et transmet donc le paquet à sa passerelle.

### 4.2 Passerelle par défaut

La passerelle est le prochain saut utilisé lorsqu'une destination ne se trouve pas dans un réseau directement connecté.

Si la passerelle de l'ordinateur est incorrecte, le VPN peut être parfaitement configuré et pourtant le trafic de cet ordinateur ne l'atteindra jamais.

### 4.3 Table de routage

Une table de routage associe des destinations à des chemins ou prochains sauts.

Pour le scénario :

- le routeur A doit disposer d'un chemin vers `192.168.20.0/24` ;
- le routeur B doit disposer d'un chemin de retour vers `192.168.10.0/24`.

### 4.4 Adresse interne et adresse externe

Le paquet interne contient les données entre les hôtes des LAN. Le paquet externe transporte ce trafic entre les extrémités du tunnel.

```text
+------------------------------------------------------+
| En-tête externe : IP WAN A -> IP WAN B               |
|                                                      |
|  +------------------------------------------------+  |
|  | En-tête de tunnel et protection éventuelle     |  |
|  |                                                |  |
|  |  +------------------------------------------+  |  |
|  |  | Paquet interne : LAN A -> LAN B          |  |  |
|  |  +------------------------------------------+  |  |
|  +------------------------------------------------+  |
+------------------------------------------------------+
```

La structure exacte dépend du protocole. Ce dessin est conceptuel et ne représente pas tous les formats de paquet.


## 5. Tunnel, encapsulation et chiffrement

### 5.1 Encapsulation

L'encapsulation consiste à placer un paquet dans une autre enveloppe afin de le transporter à travers un réseau. À l'arrivée, le destinataire retire cette enveloppe : c'est la décapsulation.

```text
AVANT LE TUNNEL
[En-tête IP interne][TCP/UDP][Données]

PENDANT LE TRANSPORT
[En-tête IP externe][En-tête de tunnel/protection][Paquet interne]

APRÈS DÉCAPSULATION
[En-tête IP interne][TCP/UDP][Données]
```

L'encapsulation ajoute des octets. Cette surcharge est importante pour la MTU et les performances.

### 5.2 Le tunnel n'est pas forcément chiffré

Un tunnel définit un moyen d'acheminer des paquets. Le chiffrement protège la confidentialité. Certaines technologies, comme GRE, ne chiffrent pas les données par elles-mêmes.

| Technologie | Tunnel ou encapsulation | Chiffrement intégré |
|---|---|---|
| GRE seul | Oui | Non |
| IP-in-IP seul | Oui | Non |
| IPsec ESP configuré pour le chiffrement | Oui, selon le mode | Oui |
| VPN TLS | Selon l'implémentation | Oui, via TLS |
| WireGuard | Oui | Oui |

La sécurité réelle dépend des algorithmes, des clés, de l'authentification et de la configuration.

### 5.3 Confidentialité, intégrité et authentification

- **Confidentialité :** les tiers ne peuvent pas facilement lire le contenu chiffré.
- **Intégrité :** les modifications non autorisées peuvent être détectées.
- **Authentification :** chaque extrémité vérifie l'identité du pair selon le mécanisme utilisé.
- **Protection anti-rejeu :** certains mécanismes détectent ou rejettent la répétition de paquets capturés précédemment.

Ces propriétés sont complémentaires. Une connexion chiffrée n'est pas nécessairement correctement authentifiée ou autorisée.


## 6. Les principaux types de VPN

### 6.1 Site-à-site

Utilisé pour relier des LAN, souvent entre routeurs ou pare-feu. Les routes définissent les réseaux accessibles via le tunnel.

### 6.2 Accès distant

Utilisé par les employés ou administrateurs en déplacement. L'utilisateur se connecte à une passerelle VPN puis accède aux ressources autorisées.

### 6.3 Full tunnel et split tunnel

- **Full tunnel :** le trafic configuré du client, souvent toute sa sortie IP, passe par le VPN.
- **Split tunnel :** seules certaines destinations, par exemple les réseaux internes, passent par le VPN ; le reste utilise la connexion locale.

Le split tunneling peut améliorer l'efficacité, mais doit être évalué selon les exigences de sécurité.

### 6.4 VPN de couche 2 ou de couche 3

Certains services transportent des trames de couche 2 ; d'autres acheminent des paquets IP de couche 3.

Le choix a des conséquences sur la conception, les broadcasts, l'apprentissage des adresses et le dépannage. Pour débuter, il est conseillé de maîtriser les VPN routés de couche 3.


## 7. GRE, IP-in-IP, IPsec, TLS et WireGuard

### 7.1 GRE

GRE (*Generic Routing Encapsulation*) encapsule un paquet dans un autre paquet IP. Il peut transporter différents types de protocoles et s'utilise parfois pour créer une interface tunnel entre routeurs.

**Limite essentielle :** GRE seul ne fournit ni chiffrement ni authentification cryptographique du trafic. Pour protéger les communications, GRE peut être associé à IPsec.

### 7.2 IP-in-IP

IP-in-IP place un paquet IP à l'intérieur d'un autre paquet IP. Le mécanisme est conceptuellement simple, mais ne fournit pas en lui-même la confidentialité ni l'authentification.

### 7.3 IPsec

IPsec est une suite de protocoles de sécurité pour IP. Il peut protéger le trafic au niveau IP et sert fréquemment aux VPN site-à-site et d'accès distant.

- **IKE / IKEv2 :** négociation des paramètres, authentification des pairs et établissement des associations de sécurité.
- **ESP :** fournit généralement la protection du trafic, avec chiffrement et contrôles d'intégrité selon la suite choisie.
- **Mode tunnel :** protège le paquet IP d'origine en l'encapsulant dans un nouveau paquet IP.
- **Mode transport :** protège principalement la charge utile du paquet IP d'origine ; il est utilisé dans des scénarios spécifiques.

AH existe dans la suite IPsec, mais ESP est le mécanisme le plus courant pour les VPN modernes. Les détails dépendent de l'équipement et de la configuration.

### 7.4 VPN fondé sur TLS

Les VPN TLS utilisent TLS pour protéger le canal entre un client et une passerelle. Ils sont fréquents pour l'accès distant.

Les ports et mécanismes exacts dépendent du produit : ne suppose pas qu'un VPN TLS utilise toujours un port ou un mode unique.

### 7.5 WireGuard

WireGuard est un protocole VPN moderne, conçu pour être relativement simple et utiliser un ensemble limité de primitives cryptographiques. Il s'appuie sur des clés publiques et une configuration de pairs.

Le port UDP souvent rencontré par défaut est `51820`, mais il peut être modifié.

### Comparaison rapide

| Technologie | Usage typique | Protection cryptographique intégrée ? |
|---|---|---|
| GRE | Tunnel flexible entre routeurs | Non, pas seul |
| IP-in-IP | Encapsulation IP simple | Non, pas seul |
| IPsec | Site-à-site et accès distant | Oui, selon la configuration |
| VPN TLS | Surtout accès distant | Oui, via TLS |
| WireGuard | Site-à-site ou accès distant | Oui |

Ne choisis pas une technologie uniquement parce qu'elle est populaire : considère la compatibilité, les besoins, l'exploitation et la politique de sécurité.


## 8. Comment fonctionne IPsec

IPsec peut paraître complexe si l'on mélange la négociation initiale et le transport des données. Il faut séparer ces deux étapes.

### 8.1 Étape A — Négocier et authentifier

Dans un déploiement IKEv2 courant, les deux pairs :

1. se contactent ;
2. négocient des paramètres cryptographiques compatibles ;
3. s'authentifient, par exemple avec une clé prépartagée ou des certificats ;
4. établissent les associations de sécurité nécessaires.

Les paramètres doivent correspondre aux politiques des deux côtés. Un désaccord sur l'authentification, les algorithmes, les identifiants ou les paramètres d'échange peut empêcher la négociation.

### 8.2 Étape B — Protéger les données

Une fois les associations de sécurité établies, ESP peut protéger le trafic correspondant à la politique VPN. Les routeurs encapsulent ou protègent les paquets selon le mode choisi, puis les transmettent.

```text
Routeur A                                      Routeur B
   |                                               |
   |---- négociation IKE / authentification ------>|
   |<--- paramètres et associations établis ------|
   |                                               |
   |====== données protégées par ESP =============>|
   |<===== données protégées par ESP ==============|
```

### 8.3 Ports et protocoles à connaître

Pour IPsec avec IKE :

- UDP `500` est généralement utilisé pour IKE ;
- UDP `4500` est utilisé pour NAT-T lorsque nécessaire ;
- ESP est le protocole IP numéro `50` : ce n'est pas un port TCP ou UDP.

AH est le protocole IP numéro `51`. GRE utilise le protocole IP numéro `47`, et non un port TCP/UDP.

Les règles de pare-feu dépendent de l'architecture réelle et de la présence de NAT.

### 8.4 NAT-T

Le NAT peut modifier les adresses IP et les ports. Comme ESP n'est pas un flux TCP ou UDP ordinaire, certains dispositifs NAT nécessitent un mécanisme particulier.

NAT Traversal encapsule généralement ESP dans UDP `4500` pour traverser ce type d'environnement.

```text
Sans NAT-T :
[IP externe][ESP][données protégées]

Avec NAT-T :
[IP externe][UDP 4500][ESP][données protégées]
```

Le schéma est simplifié. Le comportement exact dépend du protocole et de l'implémentation.

### 8.5 Clés prépartagées et certificats

Une clé prépartagée (*pre-shared key*, PSK) est un secret connu des deux extrémités.

Elle doit être aléatoire, suffisamment robuste et stockée de façon sécurisée. Évite les mots de passe simples, les clés réutilisées partout et les secrets enregistrés dans des fichiers accessibles.

Les certificats reposent sur une infrastructure de confiance. Ils peuvent être mieux adaptés aux environnements plus grands, mais demandent une gestion de leur cycle de vie.


## 9. Routage et adressage

### 9.1 Le tunnel ne crée pas automatiquement les routes

Un tunnel peut être établi tandis que les routeurs ignorent encore comment atteindre les réseaux distants.

Il faut une route statique, un protocole de routage adapté ou une politique de routage prévue par la solution.

Exemple logique :

- sur A : destination `192.168.20.0/24` via le tunnel ;
- sur B : destination `192.168.10.0/24` via le tunnel.

Les commandes exactes varient selon la plateforme.

### 9.2 Route aller et route retour

La communication doit fonctionner dans les deux sens. Le site A peut envoyer un paquet au site B, mais si B ne dispose pas d'un chemin de retour vers A, la réponse peut être perdue.

```text
ALLER
PC-A -> passerelle A -> VPN -> passerelle B -> serveur B

RETOUR
serveur B -> passerelle B -> VPN -> passerelle A -> PC-A
```

### 9.3 Réseaux qui se chevauchent

Si les deux LAN utilisent le même préfixe, le routage classique ne permet pas de distinguer naturellement les deux réseaux.

La meilleure solution est souvent de renuméroter l'un des sites. Certaines architectures permettent d'utiliser de la traduction d'adresses ou des mécanismes plus avancés, mais ils complexifient le diagnostic.

### 9.4 Routage statique ou dynamique

- **Statique :** simple pour une liaison stable et quelques réseaux.
- **Dynamique :** utile lorsque le nombre de réseaux augmente ou que les routes doivent s'adapter automatiquement.

Le routage dynamique dans un tunnel exige de concevoir correctement les voisins, les métriques, les filtres et la prévention des boucles. Il n'est pas nécessaire pour tous les petits VPN.


## 10. NAT, pare-feu et ports

### 10.1 Le rôle du pare-feu

Les pare-feu doivent autoriser le trafic nécessaire entre les pairs et entre les réseaux internes, sans ouvrir plus que nécessaire.

Le fait que l'interface WAN réponde au ping ne prouve pas que les protocoles VPN sont autorisés.

### 10.2 NAT et trafic protégé

Dans certains scénarios, le trafic LAN-à-LAN doit être exclu de la traduction NAT avant d'être envoyé dans le VPN. Sinon, le paquet peut ne plus correspondre aux réseaux attendus par la politique IPsec.

Exemple conceptuel :

- trafic Internet ordinaire du LAN A : peut être traduit par NAT ;
- trafic de `192.168.10.0/24` vers `192.168.20.0/24` : doit suivre la politique VPN sans traduction inappropriée, selon la conception.

### 10.3 Checklist de filtrage IPsec

Pour un VPN IPsec, vérifie selon le scénario :

- UDP `500` pour IKE ;
- UDP `4500` si NAT-T est utilisé ;
- ESP (protocole IP `50`) si ESP traverse directement le réseau ;
- les règles autorisant le trafic des réseaux internes à travers les interfaces ou zones appropriées.

Ne copie pas une règle générique sans comprendre la topologie. Les règles précises dépendent de l'équipement, du NAT, du mode et de la politique de sécurité.


## 11. MTU et fragmentation

### 11.1 Pourquoi la MTU est importante

La MTU est la taille maximale d'un paquet pouvant être transporté sur une liaison sans fragmentation au niveau considéré.

Un tunnel ajoute des en-têtes et parfois des données de protection. Le paquet encapsulé est donc plus gros que le paquet d'origine.

Si le paquet dépasse la taille supportée sur le chemin, il peut être fragmenté, rejeté ou bloqué par un équipement intermédiaire.

### 11.2 Symptômes courants

- les petits pings fonctionnent, mais les gros échouent ;
- certaines pages s'ouvrent, d'autres restent bloquées ;
- une application transfère peu de données puis se fige ;
- les connexions semblent établies, mais certaines réponses n'arrivent jamais.

Ces symptômes peuvent aussi venir d'autres causes. Il faut tester la MTU plutôt que conclure immédiatement.

### 11.3 PMTUD

Le *Path MTU Discovery* (PMTUD) permet aux hôtes de déterminer une taille adaptée au chemin.

Selon le protocole IP et les équipements, des messages ICMP nécessaires à la découverte de la MTU peuvent être filtrés, ce qui casse la communication de gros paquets.

Bonnes pratiques :

- tenir compte du surcoût d'encapsulation ;
- autoriser les messages ICMP nécessaires au fonctionnement du réseau ;
- tester avec des tailles de paquets progressives ;
- ne pas régler arbitrairement une MTU très basse sans mesurer les conséquences ;
- considérer le MSS TCP lorsque le problème concerne TCP, sans oublier que cela ne règle pas tous les protocoles.

### 11.4 Calcul conceptuel

Si le chemin supporte une MTU de 1500 octets et que le tunnel ajoute un surcoût, le paquet interne ne peut pas toujours occuper les 1500 octets complets.

Le surcoût exact dépend du protocole, des options, des algorithmes et de l'encapsulation. Consulte la documentation de la plateforme et mesure le chemin.


## 12. Sécurité et bonnes pratiques

1. Utiliser des protocoles et algorithmes modernes pris en charge et recommandés par le constructeur.
2. Éviter les secrets faibles ou réutilisés ; protéger les clés et certificats.
3. Limiter l'accès aux seuls réseaux et services nécessaires.
4. Garder les équipements VPN et leurs systèmes à jour.
5. Journaliser les événements utiles sans exposer inutilement les secrets.
6. Surveiller les échecs d'authentification et les changements d'état.
7. Prévoir la rotation et la révocation des clés ou certificats.
8. Tester le renouvellement des associations de sécurité et le rétablissement après coupure.
9. Documenter les pairs, les réseaux protégés, les routes et les règles de filtrage.
10. Ne pas considérer un tunnel établi comme preuve que toutes les politiques de sécurité sont correctes.

### Principe du moindre privilège

Un utilisateur distant n'a pas forcément besoin d'accéder à tout le réseau de l'entreprise. Autorise uniquement les sous-réseaux et services utiles à sa fonction.

### Disponibilité

La protection cryptographique ne suffit pas à garantir la disponibilité. Une panne d'accès Internet, une erreur de routage, une saturation ou une mauvaise MTU peut interrompre les services. Prévois la supervision et, si nécessaire, une liaison de secours.


## 13. Lire un schéma de VPN

Dans un schéma, identifie toujours :

1. les hôtes ;
2. les réseaux LAN ;
3. les passerelles VPN ;
4. les adresses de transport ;
5. le tunnel ;
6. les routes aller et retour ;
7. les points de NAT et de filtrage.

```text
                 RÉSEAU DE TRANSPORT : INTERNET

        WAN A                                      WAN B
   [Passerelle A] ============ VPN ============ [Passerelle B]
        |                                           |
  192.168.10.0/24                            192.168.20.0/24
        |                                           |
      [PC-A]                                    [Serveur-B]
  192.168.10.10                              192.168.20.20
```

Les adresses WAN dépendent du réseau ou du laboratoire utilisé.


## 14. Laboratoire guidé

### 14.1 Objectif

Construire et vérifier la logique d'un VPN site-à-site entre deux routeurs.

Le laboratoire peut être réalisé dans un simulateur compatible, ou dans un environnement prenant réellement en charge le type de VPN étudié. Tous les simulateurs ne prennent pas en charge toutes les fonctions IPsec.

### 14.2 Topologie

```text
PC-A -- LAN A -- R-A -- réseau de transit -- R-B -- LAN B -- PC-B
```

Plan d'adressage des LAN :

| Équipement | Adresse |
|---|---|
| PC-A | `192.168.10.10/24` |
| Passerelle A | `192.168.10.1/24` |
| LAN A | `192.168.10.0/24` |
| PC-B | `192.168.20.20/24` |
| Passerelle B | `192.168.20.1/24` |
| LAN B | `192.168.20.0/24` |

Attribue au réseau de transit un sous-réseau approprié et des adresses compatibles pour les deux interfaces WAN. Les adresses WAN dépendent de la topologie choisie.

### 14.3 Plan de test

Avant de configurer la protection :

1. vérifier les adresses IP et les masques ;
2. tester chaque PC vers sa passerelle locale ;
3. vérifier la connectivité entre les interfaces WAN ;
4. vérifier les routes ;
5. configurer le VPN selon la documentation de l'équipement ;
6. vérifier l'état IKE et IPsec ;
7. tester le trafic LAN-à-LAN ;
8. vérifier les compteurs d'encapsulation et de décapsulation.

### 14.4 Exemples de commandes de vérification Cisco IOS

Les commandes suivantes sont des exemples courants. Leur disponibilité et leur syntaxe peuvent varier selon le modèle, la version IOS et la configuration.

```text
show ip interface brief
show ip route
show access-lists
show crypto isakmp sa
show crypto ikev2 sa
show crypto ipsec sa
```

Selon la version, certains équipements ne prennent pas en charge toutes les commandes ci-dessus. Utilise les commandes appropriées à ta plateforme.

Les compteurs IPsec sont particulièrement utiles :

- les paquets encapsulés indiquent que du trafic est envoyé dans la protection ;
- les paquets décapsulés indiquent que du trafic protégé est reçu et traité ;
- une différence persistante entre les compteurs peut orienter vers un problème de chemin retour, de sélection du trafic ou de filtrage.

### 14.5 Fiche de laboratoire

| Vérification | Résultat | Commentaire |
|---|---|---|
| PC-A atteint sa passerelle | À compléter | |
| PC-B atteint sa passerelle | À compléter | |
| WAN A atteint WAN B | À compléter | |
| Négociation IKE établie | À compléter | |
| Associations IPsec actives | À compléter | |
| Compteurs d'encapsulation évoluent | À compléter | |
| Compteurs de décapsulation évoluent | À compléter | |
| PC-A atteint PC-B | À compléter | |
| Réponse de PC-B vers PC-A | À compléter | |

Ne marque pas une étape comme réussie uniquement parce que la commande ne renvoie pas d'erreur : vérifie l'état, les compteurs et le trafic réel.


## 15. Vérifications et dépannage

Adopte une démarche en couches, de l'élément le plus simple au plus spécifique.

### 15.1 Étape 1 — Vérifier le LAN

- adresse IP et masque du poste ;
- passerelle par défaut ;
- interface LAN active ;
- connectivité entre le poste et sa passerelle.

Si le poste ne peut pas joindre sa passerelle, le tunnel distant n'est pas le premier problème à résoudre.

### 15.2 Étape 2 — Vérifier le transport WAN

- adresse de l'interface WAN ;
- état de l'interface ;
- route par défaut ou route vers le pair ;
- connectivité de base jusqu'à l'adresse de transport distante ;
- ACL et pare-feu intermédiaires.

Un ping bloqué n'indique pas toujours une panne, car ICMP peut être filtré. Utilise plusieurs indices.

### 15.3 Étape 3 — Vérifier la négociation VPN

Pour IPsec, vérifie :

- que les pairs utilisent les adresses attendues ;
- que les paramètres cryptographiques sont compatibles ;
- que les identités correspondent ;
- que la méthode d'authentification et le secret ou certificat sont corrects ;
- que les protocoles nécessaires traversent les pare-feu ;
- que l'horloge et les certificats sont valides lorsque ces éléments s'appliquent.

### 15.4 Étape 4 — Vérifier le trafic protégé

Le tunnel peut être actif mais ne pas sélectionner le trafic souhaité. Vérifie :

- les réseaux locaux et distants configurés ;
- les ACL ou sélecteurs de trafic ;
- les routes vers le réseau distant ;
- les règles NAT ;
- les règles de filtrage après décapsulation ;
- le chemin retour.

### 15.5 Étape 5 — Vérifier la MTU

Si les petits paquets passent mais pas les gros, mesure la taille maximale et vérifie les messages ICMP liés à PMTUD.

Vérifie aussi le MSS TCP lorsque c'est pertinent.

### 15.6 Matrice de dépannage

| Symptôme | Causes possibles | Vérifications |
|---|---|---|
| Aucune négociation IKE | Pair inaccessible, UDP filtré, mauvaise identité, paramètres incompatibles | Route WAN, règles, journaux IKE, paramètres |
| IKE établi mais IPsec ne transporte rien | Sélecteurs incorrects, aucun trafic correspondant, proposition ESP incompatible | Générer du trafic attendu, vérifier SA et compteurs |
| Encapsulation augmente, décapsulation reste nulle | Paquets perdus en transit, filtrage, pair distant, NAT ou politique distante | Captures, règles WAN, état distant |
| Tunnel actif, LAN distant inaccessible | Routes, ACL, NAT, passerelle hôte | Table de routage, test de chaque saut, route retour |
| Un seul sens passe | Route de retour manquante, filtrage asymétrique, NAT | Vérifier les deux tables de routage et les ACL |
| Gros transferts bloqués | MTU, PMTUD, fragmentation ou MSS | Tester différentes tailles, examiner ICMP et MTU |
| Le VPN tombe périodiquement | Connectivité instable, durée de vie SA, renouvellement, expiration NAT, ressources | Journaux, compteurs, état WAN et renouvellement des SA |

### 15.7 Méthode de dépannage reproductible

Pour chaque incident, note :

- l'heure du test ;
- les adresses source et destination ;
- le protocole et le type de trafic ;
- le résultat attendu et le résultat observé ;
- les états et compteurs avant et après ;
- la modification unique effectuée ;
- le résultat après cette modification.

Changer plusieurs paramètres à la fois rend la cause difficile à identifier et peut introduire de nouveaux problèmes.


## 16. Erreurs fréquentes

1. **Confondre tunnel et chiffrement.** GRE seul n'est pas un VPN chiffré.
2. **Oublier le chemin retour.** Un paquet peut arriver à destination sans que la réponse puisse revenir.
3. **Supposer que tunnel actif signifie trafic fonctionnel.** Le routage et les règles doivent aussi être corrects.
4. **Utiliser des sous-réseaux qui se chevauchent.** Le routage devient ambigu.
5. **Oublier les règles NAT.** Une traduction inattendue peut faire échouer les sélecteurs IPsec.
6. **Ouvrir trop largement le pare-feu.** N'autorise que ce qui est nécessaire.
7. **Négliger la MTU.** Le surcoût d'encapsulation peut affecter les gros paquets.
8. **Diagnostiquer avec un seul ping.** ICMP peut être filtré et un ping réussi ne valide pas toutes les applications.
9. **Copier des commandes sans vérifier la plateforme.** Les commandes diffèrent selon le modèle et la version.
10. **Laisser des secrets faibles.** Une configuration qui fonctionne n'est pas forcément sûre.


## 17. Exercices pratiques

### Exercice 1 — Identifier les éléments

À partir du schéma suivant, indique les deux LAN, les deux extrémités du tunnel et le réseau de transport.

```text
PC-A -- 192.168.10.0/24 -- R-A ===== Internet ===== R-B -- 192.168.20.0/24 -- PC-B
```

### Exercice 2 — Suivre un paquet

PC-A (`192.168.10.10`) contacte PC-B (`192.168.20.20`).

1. Pourquoi PC-A envoie-t-il le paquet à sa passerelle ?
2. Quel routeur décide d'envoyer le trafic dans le tunnel ?
3. Quel est le rôle de l'adresse IP externe ?
4. Que fait la passerelle B à la réception ?

### Exercice 3 — Choisir une technologie

Associe chaque besoin à une option possible et justifie ta réponse.

- A. Tunnel simple entre routeurs, sans exigence de confidentialité en lui-même.
- B. Protection du trafic IP entre deux passerelles.
- C. Accès distant avec un protocole VPN moderne à base de clés.
- D. Tunnel IP simple sans chiffrement intégré.

Options : GRE, IP-in-IP, IPsec, WireGuard.

### Exercice 4 — Diagnostic

Le tunnel IPsec est indiqué comme actif. PC-A peut joindre sa passerelle, mais pas PC-B. Donne au moins cinq vérifications dans un ordre logique.

### Exercice 5 — MTU

Les petits paquets passent, mais une application de transfert de fichiers échoue. Explique pourquoi la MTU et PMTUD sont des hypothèses pertinentes et cite deux vérifications.

### Exercice 6 — Sécurité

Explique pourquoi il est risqué d'utiliser une clé prépartagée simple et pourquoi le VPN ne dispense pas de filtrer les accès au réseau interne.

### Exercice 7 — Réseaux qui se chevauchent

Les deux sites utilisent `192.168.1.0/24`. Explique le problème de routage et propose une solution simple.

### Exercice 8 — Analyse des compteurs

Après un test :

- les paquets encapsulés augmentent sur A ;
- les paquets décapsulés n'augmentent pas sur A ;
- le pair est indiqué comme actif.

Quelles hypothèses examinerais-tu ? Ne donne pas une cause unique sans preuve.


## 18. Quiz de validation

**1. Que fait un tunnel ?**

A. Il chiffre nécessairement les données.  
B. Il transporte un paquet dans une autre enveloppe logique.  
C. Il remplace la table de routage.

**2. GRE seul chiffre-t-il les données ?**

A. Oui, toujours.  
B. Non.  
C. Uniquement sur Internet.

**3. Quel élément indique où envoyer le trafic vers un réseau distant ?**

A. La table de routage.  
B. Le nom de l'ordinateur.  
C. Le masque de sous-réseau seul.

**4. Quel rôle général joue IKE dans IPsec ?**

A. Il attribue toujours les adresses LAN.  
B. Il négocie les paramètres et contribue à l'authentification et à l'établissement des associations de sécurité.  
C. Il remplace ESP pour toutes les données.

**5. Quel est le numéro de protocole IP d'ESP ?**

A. 6.  
B. 17.  
C. 50.

**6. Quel port UDP est généralement associé à IKE ?**

A. 53.  
B. 500.  
C. 443 uniquement.

**7. Pourquoi un VPN actif peut-il ne pas transporter le trafic attendu ?**

A. Parce que les routes ou règles peuvent être incorrectes.  
B. Parce qu'un tunnel n'utilise jamais d'adresses IP.  
C. Parce que les réseaux LAN doivent obligatoirement avoir le même préfixe.

**8. Que peut indiquer un échec limité aux gros paquets ?**

A. Toujours un mauvais mot de passe.  
B. Un problème possible de MTU ou PMTUD.  
C. L'absence obligatoire de chiffrement.

**9. Pourquoi faut-il vérifier le chemin retour ?**

A. Parce qu'une communication bidirectionnelle nécessite que les réponses puissent revenir.  
B. Parce que le routeur distant n'a pas besoin de route.  
C. Parce qu'IPsec désactive le routage.

**10. Quelle est une bonne pratique de sécurité ?**

A. Utiliser une clé simple facile à retenir.  
B. Autoriser tous les réseaux internes sans distinction.  
C. Utiliser des secrets robustes et limiter les accès au nécessaire.

### Corrigé

1. **B** — Le tunnel fournit un mécanisme de transport et d'encapsulation.
2. **B** — GRE seul ne fournit pas de chiffrement.
3. **A** — La table de routage permet de choisir le chemin.
4. **B** — IKE négocie les paramètres et établit les associations de sécurité.
5. **C** — ESP correspond au protocole IP 50.
6. **B** — IKE utilise généralement UDP 500 ; NAT-T utilise généralement UDP 4500.
7. **A** — Routes, sélecteurs, NAT et ACL peuvent empêcher le trafic.
8. **B** — La MTU et PMTUD sont des hypothèses importantes, mais pas les seules.
9. **A** — La réponse doit pouvoir retourner à la source.
10. **C** — Des secrets robustes et le moindre privilège sont essentiels.


## 19. Liste de contrôle

Avant de déclarer un VPN opérationnel, vérifie :

- [ ] Les réseaux locaux ne se chevauchent pas.
- [ ] Les interfaces et adresses IP sont correctes.
- [ ] Les deux extrémités peuvent atteindre leurs adresses de transport.
- [ ] Les paramètres de négociation et d'authentification correspondent.
- [ ] Les associations de sécurité sont actives.
- [ ] Les routes aller et retour existent.
- [ ] Les règles de pare-feu autorisent le trafic nécessaire.
- [ ] Le NAT n'altère pas le trafic protégé de manière inattendue.
- [ ] Les compteurs de trafic évoluent dans les deux sens.
- [ ] Les tests applicatifs réussissent, pas uniquement le ping.
- [ ] Les problèmes de MTU et de PMTUD ont été envisagés.
- [ ] Les secrets sont robustes et les accès sont limités.
- [ ] Les journaux et la supervision sont disponibles.


## 20. Glossaire

- **VPN :** réseau privé virtuel, liaison logique utilisant un réseau de transport.
- **Tunnel :** mécanisme de transport d'un paquet dans une autre enveloppe.
- **Encapsulation :** ajout d'une enveloppe ou d'en-têtes autour d'un paquet.
- **Décapsulation :** retrait de l'enveloppe à la sortie du tunnel.
- **IPsec :** suite de protocoles de sécurité pour IP.
- **IKE/IKEv2 :** protocole de négociation et d'authentification utilisé avec IPsec.
- **ESP :** mécanisme IPsec de protection des paquets.
- **GRE :** mécanisme d'encapsulation générique.
- **NAT :** traduction d'adresses réseau.
- **NAT-T :** encapsulation généralement utilisée pour transporter ESP à travers certains dispositifs NAT.
- **MTU :** taille maximale d'un paquet transporté sur une liaison sans fragmentation à ce niveau.
- **PMTUD :** découverte de la MTU du chemin.
- **PSK :** clé prépartagée connue des deux pairs.
- **SA :** association de sécurité décrivant les paramètres de protection d'un flux.
- **ACL :** liste de contrôle d'accès qui autorise ou refuse du trafic.
- **Split tunneling :** envoi d'une partie seulement du trafic du client à travers le VPN.
- **Full tunnel :** envoi du trafic configuré, souvent tout le trafic IP du client, à travers le VPN.


## 21. Pour aller plus loin

Pour approfondir, privilégie la documentation officielle et les standards :

- RFC 4301 — *Security Architecture for the Internet Protocol*.
- RFC 4303 — *IP Encapsulating Security Payload (ESP)*.
- RFC 7296 — *Internet Key Exchange Protocol Version 2 (IKEv2)*.
- RFC 2784 — *Generic Routing Encapsulation (GRE)*.
- Documentation du constructeur pour les commandes et fonctions réellement prises en charge par l'équipement utilisé.

Les RFC décrivent les protocoles ; la documentation du constructeur explique comment ils sont configurés sur une plateforme donnée.


## Conclusion

Un VPN permet de relier des utilisateurs ou des réseaux au travers d'un réseau de transport. Pour comprendre un VPN, il faut séparer cinq éléments : **adressage, routage, encapsulation, protection cryptographique et filtrage**.

La méthode à retenir est simple : dessiner la topologie, vérifier le LAN, vérifier le transport, contrôler l'établissement du tunnel, vérifier les routes aller et retour, examiner les règles NAT et pare-feu, puis tester les applications et la MTU.

Au niveau intermédiaire, l'étape suivante sera d'approfondir la configuration IPsec/IKEv2, les sélecteurs de trafic, les associations de sécurité, les compteurs, les scénarios NAT-T et le dépannage à partir de captures de paquets.
