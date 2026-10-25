# VPN et tunnels — Niveau Intermédiaire

## 1. Parcours pratique — du VPN fonctionnel au VPN maîtrisé

À ce niveau, l'objectif n'est plus seulement de reconnaître un VPN ou de comprendre le principe d'un tunnel. Il faut être capable d'analyser un scénario, de choisir une technologie adaptée, de prévoir le routage, de vérifier les mécanismes de sécurité et de diagnostiquer une panne à partir d'indices.

Ce parcours pratique est particulièrement utile si tu sais déjà expliquer ce qu'est un tunnel, distinguer encapsulation et chiffrement, et identifier les grandes familles de VPN. Si ces notions restent fragiles, révise d'abord le cours Débutant.

### Étape 1 — Lire le besoin avant de choisir la technologie

Pour chaque scénario, réponds à ces questions avant de configurer quoi que ce soit :

- Qui doit communiquer avec qui ?
- Les deux extrémités sont-elles des routeurs, des pare-feu, des serveurs ou des utilisateurs nomades ?
- Le trafic doit-il être confidentiel, authentifié, ou simplement transporté dans un tunnel ?
- Les adresses des réseaux distants se chevauchent-elles ?
- Le tunnel doit-il relier deux sites ou connecter plusieurs sites ?
- La solution doit-elle tolérer une adresse IP publique dynamique ou un changement de lien Internet ?

Exemple : deux agences doivent échanger des données privées par Internet. Le besoin inclut la confidentialité et l'intégrité : un VPN site-à-site IPsec est un candidat naturel. Un tunnel GRE seul ne répond pas au besoin de chiffrement.

### Étape 2 — Dessiner le chemin logique et le chemin réel

Le chemin logique représente les réseaux qui communiquent. Le chemin réel représente les adresses publiques et les équipements utilisés pour transporter le tunnel.

```text
RÉSEAUX LOGIQUES
LAN A 192.168.10.0/24
        |
   [Routeur A]
        |
   === VPN IPsec ===
        |
   [Routeur B]
        |
LAN B 192.168.20.0/24

TRANSPORT SUR INTERNET
IP publique A: 203.0.113.10
        |
     Internet
        |
IP publique B: 198.51.100.20
```

Les adresses de documentation ci-dessus sont réservées aux exemples. Dans un véritable déploiement, remplace-les par les adresses réellement attribuées.

**À faire :** sur un schéma, identifie les adresses des LAN, les adresses des pairs VPN, le type de tunnel et les routes nécessaires.

### Étape 3 — Vérifier le plan d'adressage et le routage

Avant de soupçonner le chiffrement, vérifie que les réseaux sont distincts et que les routes existent dans les deux sens.

```text
LAN A : 192.168.10.0/24
LAN B : 192.168.20.0/24

Routeur A :
  réseau local : 192.168.10.0/24
  réseau distant via VPN : 192.168.20.0/24

Routeur B :
  réseau local : 192.168.20.0/24
  réseau distant via VPN : 192.168.10.0/24
```

Si les deux sites utilisent `192.168.1.0/24`, les routes deviennent ambiguës : un hôte peut considérer la destination distante comme locale. Il faut généralement renuméroter un site ou mettre en place une traduction d'adresses adaptée, en évaluant les effets sur les applications.

### Étape 4 — Distinguer établissement du tunnel et transport des données

Un tunnel peut être établi sans que les applications puissent communiquer. Sépare les contrôles :

1. **Plan de contrôle :** les pairs se joignent-ils et négocient-ils les paramètres de sécurité ?
2. **État du tunnel :** les associations de sécurité sont-elles présentes et actives ?
3. **Plan de données :** les paquets correspondant au trafic attendu sont-ils chiffrés, transmis et déchiffrés ?
4. **Routage et filtrage :** les routes et les règles de pare-feu autorisent-elles les flux dans les deux sens ?
5. **Hôtes :** les passerelles, les routes locales et les pare-feu des machines sont-ils corrects ?

### Étape 5 — Interpréter des symptômes

- Tunnel inactif : vérifier la connectivité entre pairs, les paramètres IKE, les identifiants, les propositions cryptographiques et les règles de filtrage.
- Tunnel actif, aucun trafic : vérifier les routes, les sélecteurs de trafic, les règles de pare-feu, le NAT et le chemin retour.
- Petits paquets fonctionnels, gros transferts bloqués : suspecter une difficulté de MTU/PMTUD ou un filtrage des messages ICMP nécessaires.
- Un seul sens fonctionne : vérifier les routes de retour, les règles asymétriques et le NAT.
- Coupures périodiques : vérifier les durées de vie des associations, la renégociation, la stabilité du lien et les changements d'adresse publique.

### Étape 6 — Produire une preuve

Une bonne analyse ne se limite pas à « le VPN est up ». Pour chaque test, note :

- l'hôte source et la destination ;
- l'adresse IP et le protocole testés ;
- l'heure du test ;
- le résultat attendu et le résultat obtenu ;
- l'interface ou l'équipement où la capture a été réalisée ;
- les compteurs ou journaux observés.

**Livrable pratique :** un tableau qui relie chaque symptôme à une hypothèse, un test discriminant et une action corrective.

| Symptôme | Hypothèse | Test utile |
|---|---|---|
| Tunnel inactif | Négociation IKE échouée | Examiner les journaux IKE et tester la connectivité entre pairs |
| Tunnel actif, trafic absent | Route ou sélecteur incorrect | Vérifier la table de routage et les sélecteurs de trafic |
| Un seul sens | Route de retour ou filtrage | Tester dans les deux sens et comparer les compteurs |
| Gros transferts bloqués | MTU/PMTUD | Tester progressivement la taille des paquets et examiner les messages ICMP |


## 2. Objectifs pédagogiques

À la fin de ce cours, tu devrais pouvoir :

- distinguer VPN site-à-site, accès distant, VPN routé et VPN fondé sur des politiques ;
- expliquer les différences opérationnelles entre IPsec, GRE, WireGuard et TLS VPN ;
- comprendre les composants de négociation IKEv2 et les associations de sécurité IPsec ;
- analyser les interactions entre routage, NAT, pare-feu et sélecteurs de trafic ;
- raisonner sur les routes statiques, les protocoles de routage au-dessus d'un tunnel et la redondance ;
- diagnostiquer les problèmes de MTU, de fragmentation et de PMTUD ;
- établir un plan de test reproductible et documenter les preuves.

## 3. Modèle mental : les couches d'un VPN

Un VPN n'est pas une seule fonction. Plusieurs mécanismes coopèrent.

```text
Application
    |
Paquet IP original
    |
Routage et sélection du trafic
    |
Encapsulation et/ou protection cryptographique
    |
Paquet transporté sur le réseau public
    |
Décapsulation et vérification
    |
Routage vers le réseau distant
    |
Application distante
```

Les étapes exactes varient selon la technologie. IPsec en mode tunnel protège un paquet IP à l'intérieur d'un nouveau paquet IP. GRE fournit une encapsulation, mais pas de chiffrement par lui-même. WireGuard associe tunnel IP et cryptographie. Les solutions TLS VPN utilisent TLS pour protéger une session, puis acheminent le trafic selon leur architecture.

## 4. VPN site-à-site et accès distant

### 4.1 Site-à-site

Un VPN site-à-site relie généralement deux réseaux à travers des passerelles. Les utilisateurs n'ont pas besoin de lancer chacun une session VPN sur leur poste.

```text
LAN siège                  Internet                 LAN agence
10.10.0.0/16                                     10.20.0.0/16
    |                                                  |
[Passerelle A] ===== tunnel chiffré IPsec ===== [Passerelle B]
```

Points à planifier :

- sous-réseaux locaux et distants ;
- adresses des pairs ;
- politiques cryptographiques compatibles ;
- routes et règles de filtrage ;
- surveillance et procédures de reprise ;
- redondance des passerelles et des accès Internet, si nécessaire.

### 4.2 Accès distant

Un VPN d'accès distant connecte un utilisateur ou un appareil à un réseau d'entreprise.

```text
Ordinateur nomade
       |
 Internet non fiable
       |
[Passerelle VPN]
       |
Réseaux autorisés de l'entreprise
```

Les sujets supplémentaires sont l'authentification des utilisateurs, la gestion des appareils, les droits d'accès, le MFA, la révocation des accès et la journalisation.

### 4.3 Choisir selon le besoin

| Besoin | Approche possible | Point de vigilance |
|---|---|---|
| Relier deux sites avec confidentialité | IPsec site-à-site | Adressage, IKE, routes, filtrage |
| Transporter plusieurs protocoles ou du routage multicast | GRE, souvent protégé par IPsec | GRE seul ne chiffre pas |
| Accès nomade moderne | WireGuard ou TLS VPN selon l'environnement | Gestion des clés, identité et contrôle d'accès |
| Accès applicatif ciblé | VPN applicatif ou solution d'accès privé | Ne pas donner plus d'accès que nécessaire |
| Interconnexion avec plusieurs chemins | IPsec avec routage dynamique, selon le support | Détection de panne et convergence |

Ce tableau propose des familles de solutions, pas une décision universelle. La compatibilité avec les équipements, les politiques de sécurité, les besoins d'exploitation et les exigences réglementaires comptent aussi.

## 5. IPsec : comprendre IKEv2 et les associations de sécurité

IPsec protège le trafic IP. IKEv2 négocie les paramètres, authentifie les pairs et établit les associations de sécurité (SA).

### 5.1 Deux niveaux à distinguer

- **IKE SA :** protège les échanges de contrôle IKE entre les pairs.
- **Child SA :** porte les paramètres de protection du trafic utilisateur, généralement via ESP.

Schéma simplifié :

```text
Pair A                                      Pair B
  |                                            |
  |---- échanges IKE_SA_INIT ----------------->|
  |<--- négociation des algorithmes, DH -------|
  |                                            |
  |---- échanges IKE_AUTH -------------------->|
  |<--- authentification et création Child SA -|
  |                                            |
  |====== trafic utilisateur protégé ESP =====|
```

Cette représentation est conceptuelle : les messages et leur contenu exacts dépendent de la négociation et des options utilisées.

### 5.2 Éléments négociés

Selon la configuration, les pairs négocient notamment :

- les algorithmes de chiffrement et d'intégrité, ou un mode AEAD ;
- le groupe Diffie-Hellman pour l'établissement de secrets ;
- les méthodes d'authentification ;
- les durées de vie et les paramètres de renouvellement ;
- les sélecteurs de trafic ;
- les paramètres des Child SA.

Les deux côtés doivent avoir des propositions compatibles. Une politique de sécurité plus faible ne devrait pas être ajoutée simplement pour contourner un problème de compatibilité.

### 5.3 ESP et AH

- **ESP (Encapsulating Security Payload)** peut assurer confidentialité, intégrité et authentification selon les algorithmes utilisés. C'est le choix courant pour les VPN IPsec.
- **AH (Authentication Header)** protège l'intégrité de certains champs et l'authenticité, mais ne chiffre pas le contenu. Il s'adapte mal aux environnements avec NAT et est peu utilisé pour les VPN modernes.

### 5.4 Ports et NAT-T

Dans de nombreux déploiements IPsec :

- IKE utilise UDP 500 ;
- si la traversée NAT est détectée et négociée, ESP est encapsulé dans UDP 4500 (NAT-T) ;
- ESP sans encapsulation UDP utilise le numéro de protocole IP 50, pas un port TCP ou UDP.

Le pare-feu doit autoriser les flux correspondant à la conception retenue. Les détails peuvent varier selon les équipements et les options activées.

## 6. GRE, IPsec et WireGuard : ne pas confondre leurs rôles

### GRE

GRE encapsule des paquets et peut faciliter le transport de certains protocoles ou la création d'une interface de tunnel. **GRE seul ne fournit pas de chiffrement ni d'authentification cryptographique.**

### GRE sur IPsec

GRE peut transporter du trafic à l'intérieur d'un tunnel, tandis qu'IPsec protège les paquets GRE sur le réseau public. Cette combinaison est utile dans certaines architectures, mais ajoute des en-têtes et de la complexité opérationnelle.

```text
Paquet utilisateur
       |
      GRE
       |
      ESP/IPsec
       |
   Réseau public
```

### WireGuard

WireGuard fournit un tunnel IP utilisant une conception cryptographique moderne et une gestion des pairs par clés. Le routage des adresses autorisées et la gestion des clés doivent être conçus avec soin. Les ports et le comportement opérationnel dépendent de la configuration.

### TLS VPN

Les solutions VPN basées sur TLS peuvent offrir un accès distant et, selon le produit, un tunnel IP complet ou un accès plus ciblé. Il faut distinguer les fonctions du protocole TLS de celles du produit VPN qui l'utilise.

## 7. Routage à travers un tunnel

### 7.1 Routage statique

Dans un petit environnement, des routes statiques peuvent suffire. Chaque extrémité doit savoir où envoyer les destinations distantes et disposer d'un chemin retour.

Exemple conceptuel :

```text
Routeur A :
  10.20.0.0/16 -> tunnel vers B

Routeur B :
  10.10.0.0/16 -> tunnel vers A
```

Une route correcte dans un seul sens ne garantit pas une communication bidirectionnelle.

### 7.2 Routage dynamique

Dans des environnements plus grands, un protocole de routage peut fonctionner au-dessus d'un tunnel pris en charge par les équipements. Cela permet d'annoncer des préfixes et de s'adapter aux changements de topologie.

À vérifier :

- quelles interfaces participent au protocole ;
- quelles adresses de voisinage sont utilisées ;
- quels préfixes sont annoncés et acceptés ;
- comment éviter une boucle de routage ;
- comment filtrer les annonces ;
- comment la perte d'un tunnel influence les routes ;
- si le protocole de routage lui-même est authentifié ou protégé.

Le routage dynamique ne remplace pas la sécurité du tunnel. Il faut sécuriser les deux plans.

### 7.3 Routage basé sur des politiques et VPN routés

Un VPN basé sur des politiques sélectionne le trafic à protéger à partir de règles ou de sélecteurs. Un VPN routé expose une interface de tunnel dans la table de routage. Les noms et capacités diffèrent selon les fabricants.

Un mauvais alignement entre routes et sélecteurs peut entraîner un tunnel apparemment actif mais sans trafic utile.

## 8. NAT, pare-feu et sélecteurs de trafic

### 8.1 Le problème du NAT

Le NAT peut modifier les adresses ou les ports avant ou après le traitement VPN. Selon l'ordre des règles et l'architecture, le trafic destiné au tunnel peut être traduit de façon inattendue.

Bonnes pratiques :

1. identifier précisément les sous-réseaux protégés ;
2. déterminer si le trafic VPN doit être exempté du NAT ;
3. appliquer l'exemption avant les règles NAT générales si l'architecture l'exige ;
4. vérifier les règles sur les deux passerelles ;
5. confirmer avec des compteurs ou une capture, et pas seulement avec la configuration affichée.

### 8.2 Sélecteurs de trafic

Les sélecteurs déterminent quelles adresses et quels flux sont couverts par une Child SA dans les déploiements IPsec concernés. Si un côté attend `10.10.0.0/16 ↔ 10.20.0.0/16` et que l'autre propose des plages différentes, la négociation ou le transport peut échouer selon la politique configurée.

### 8.3 Filtrage

Un tunnel peut être établi tout en étant bloqué par les règles du pare-feu. Vérifie séparément :

- le trafic de contrôle entre les pairs ;
- le trafic chiffré sur le réseau public ;
- le trafic décapsulé entre les LAN ;
- les règles locales sur les serveurs et postes ;
- le trafic de retour.

## 9. MTU, encapsulation et PMTUD

Chaque en-tête ajouté réduit la place disponible pour les données utiles. Les tunnels imbriqués, GRE sur IPsec et certaines encapsulations UDP peuvent réduire davantage le MTU effectif.

Symptôme classique : les pings de petite taille réussissent, mais certains sites, transferts ou connexions se bloquent.

Procédure de diagnostic :

1. confirmer que les petits paquets traversent le tunnel ;
2. tester des paquets plus grands avec une taille contrôlée ;
3. vérifier si la fragmentation est autorisée ou évitée ;
4. contrôler le passage des messages ICMP utiles à PMTUD ;
5. mesurer l'effet de chaque encapsulation ;
6. ajuster le MTU ou le MSS si nécessaire, en documentant la valeur retenue.

Ne règle pas systématiquement le problème en bloquant la fragmentation ou en réduisant arbitrairement toutes les tailles. Il faut identifier le mécanisme qui échoue et vérifier les conséquences sur les performances.

## 10. Haute disponibilité et résilience

Un tunnel est un composant de la connectivité, pas une stratégie complète de disponibilité.

Éléments à étudier :

- deux accès Internet ou chemins de transport indépendants ;
- redondance des passerelles ;
- détection fiable de la panne du pair ou du chemin ;
- comportement du routage lors de la perte du tunnel ;
- synchronisation d'état, si elle est prise en charge et nécessaire ;
- renouvellement des SA et récupération après panne ;
- tests réguliers de bascule.

Une simple interface « up » ne prouve pas que le chemin de données est fonctionnel. La supervision doit inclure des tests de bout en bout et, si possible, une vérification depuis chaque site.

## 11. Sécurité et exploitation

- Préférer les suites cryptographiques modernes prises en charge et éviter les algorithmes obsolètes.
- Employer des secrets robustes ou, lorsque c'est approprié, des certificats et une authentification par clés.
- Utiliser MFA pour les accès utilisateurs lorsque la solution le permet.
- Limiter les réseaux et services accessibles à travers le VPN.
- Mettre à jour les passerelles et révoquer rapidement les clés ou comptes compromis.
- Journaliser les négociations, échecs d'authentification et changements de configuration.
- Protéger les fichiers de configuration et les sauvegardes, qui peuvent contenir des informations sensibles.
- Ne jamais publier des clés privées, secrets pré-partagés ou captures contenant des identifiants.
- Tester les changements dans un environnement de laboratoire avant le déploiement.

## 12. Méthode de dépannage reproductible

Utilise une méthode en couches plutôt que de modifier plusieurs paramètres simultanément.

```text
1. Connectivité entre les pairs ?
        |
        +-- Non -> lien Internet, routes publiques, ACL, NAT
        |
        +-- Oui
             |
2. Négociation IKE réussie ?
        |
        +-- Non -> authentification, propositions, identifiants, temps
        |
        +-- Oui
             |
3. Child SA / état IPsec actif ?
        |
        +-- Non -> sélecteurs, propositions, politiques
        |
        +-- Oui
             |
4. Compteurs ESP augmentent-ils ?
        |
        +-- Non -> route, sélecteur, NAT, trafic de test
        |
        +-- Oui
             |
5. Le trafic arrive-t-il au LAN distant ?
        |
        +-- Non -> décapsulation, pare-feu, route retour, MTU
        |
        +-- Oui -> vérifier l'hôte et l'application
```

Les libellés et commandes de vérification dépendent du fabricant. Dans un environnement de production, collecte les informations avant de réinitialiser les SA ou de redémarrer le tunnel : ces actions peuvent effacer des indices et interrompre des connexions.

### Tableau d'analyse

| Symptôme | Causes possibles | Vérifications discriminantes |
|---|---|---|
| IKE échoue | Port bloqué, identifiants, propositions incompatibles | Journaux des deux pairs, connectivité UDP 500/4500 |
| IKE actif, aucune Child SA | Sélecteurs ou paramètres de trafic incompatibles | État des SA, journaux de négociation |
| SA active, compteurs sortants nuls | Aucun trafic correspondant, route incorrecte | Générer un trafic de test et examiner la table de routage |
| Compteurs sortants mais pas entrants | Chemin retour, filtrage ou pair distant | Compteurs des deux extrémités et capture réseau |
| Un seul réseau fonctionne | Sélecteurs ou routes incomplets | Tester chaque préfixe séparément |
| Transferts volumineux bloqués | MTU/PMTUD, fragmentation filtrée | Tests de taille et observation ICMP |
| Coupures à intervalle régulier | Renouvellement SA, instabilité du lien, rekey | Journaux horodatés, compteurs et événements WAN |

## 13. Laboratoire pratique : deux sites IPsec

### Objectif

Construire et diagnostiquer un scénario de deux LAN reliés par un tunnel IPsec. Le laboratoire peut être réalisé sur simulateur ou sur équipements compatibles ; les commandes exactes sont propres à la plateforme.

### Topologie

```text
PC-A
192.168.10.10/24
   |
LAN A 192.168.10.0/24
   |
[GW-A]
203.0.113.10
   |
   +---------- Internet / réseau de transit ----------+
                                                      |
                                                   [GW-B]
                                              198.51.100.20
                                                      |
                                      LAN B 192.168.20.0/24
                                                      |
                                                    PC-B
                                              192.168.20.10/24
```

### Travaux demandés

1. Vérifier que les deux LAN utilisent des sous-réseaux distincts.
2. Décrire les adresses publiques des pairs et les chemins de transport.
3. Définir les paramètres IKE/IPsec compatibles selon la plateforme.
4. Créer les règles de filtrage nécessaires entre pairs.
5. Définir les routes et les sélecteurs pour les deux LAN.
6. Déterminer si une exemption NAT est nécessaire.
7. Tester la connectivité de PC-A vers PC-B, puis dans le sens inverse.
8. Observer l'état IKE, les Child SA et les compteurs de trafic.
9. Simuler une panne : retirer une route, bloquer un flux ou créer un désaccord de sélecteurs dans le laboratoire.
10. Identifier le premier point où le comportement diffère de l'attendu, puis corriger une seule cause à la fois.

### Rapport de laboratoire

Documente la topologie, les paramètres non secrets, les routes, les règles, les tests exécutés, les résultats et la cause racine. N'inclus jamais de secret partagé ni de clé privée dans le rapport.

## 14. Exercices d'analyse

### Exercice 1 — Tunnel actif, applications injoignables

Le statut IPsec est actif. Les compteurs sortants augmentent, mais les compteurs entrants restent à zéro.

Questions :
1. Quelles hypothèses sont plausibles ?
2. Quelles données faut-il recueillir sur le pair distant ?
3. Pourquoi redémarrer immédiatement le tunnel n'est-il pas le meilleur premier geste ?

### Exercice 2 — Chevauchement d'adresses

Deux sites utilisent `192.168.1.0/24`.

Questions :
1. Pourquoi une route vers le réseau distant peut-elle être ambiguë ?
2. Quelle solution privilégier si une renumérotation est possible ?
3. Quels risques faut-il considérer si une traduction d'adresses est utilisée ?

### Exercice 3 — Petits paquets seulement

Une connexion fonctionne pour de petits échanges, mais les transferts volumineux se bloquent.

Questions :
1. Quel mécanisme réseau faut-il suspecter ?
2. Quel rôle joue PMTUD ?
3. Quels tests permettent de confirmer l'hypothèse ?

### Exercice 4 — Choix technologique

Un réseau doit transporter du routage dynamique et certains trafics multicast, tout en protégeant les données sur Internet.

Questions :
1. Pourquoi GRE seul est-il insuffisant pour la confidentialité ?
2. Dans quels cas GRE sur IPsec peut-il être envisagé ?
3. Quelles autres solutions compatibles avec l'équipement faut-il comparer ?

## 15. Quiz de validation

**1. Quelle affirmation est correcte ?**

A. GRE chiffre toujours les paquets.  
B. IKEv2 négocie les paramètres et authentifie les pairs.  
C. Une SA active garantit que toutes les applications fonctionnent.  
D. ESP utilise toujours un port TCP.

**2. Dans IPsec, que transporte principalement une Child SA ?**

A. Le trafic utilisateur protégé.  
B. Les requêtes DNS uniquement.  
C. Les routes publiques Internet.  
D. Les journaux du pare-feu.

**3. Un tunnel est actif mais aucun paquet utile ne traverse. Quelle vérification est pertinente ?**

A. La couleur des câbles.  
B. Les routes, sélecteurs, règles de pare-feu et compteurs.  
C. La résolution DNS publique uniquement.  
D. La vitesse du processeur du poste uniquement.

**4. Pourquoi PMTUD est-il important ?**

A. Il chiffre les paquets.  
B. Il découvre les MTU du chemin afin d'éviter des problèmes liés aux paquets trop grands.  
C. Il remplace le routage.  
D. Il distribue les clés privées.

**5. Quelle affirmation décrit correctement ESP sans NAT-T ?**

A. Il utilise toujours UDP 500.  
B. Il utilise le protocole IP 50.  
C. Il utilise TCP 443 dans tous les cas.  
D. Il n'a besoin d'aucune règle de pare-feu.

### Réponses

1. B — IKEv2 négocie et protège les échanges de contrôle.
2. A — Les Child SA protègent le trafic utilisateur selon les paramètres convenus.
3. B — Le statut du tunnel ne garantit ni le routage ni l'autorisation du trafic.
4. B — PMTUD aide à déterminer la taille de paquet adaptée au chemin.
5. B — ESP est le protocole IP numéro 50 ; avec NAT-T, il est généralement encapsulé dans UDP 4500.

## 16. Checklist avant mise en service

- [ ] Les réseaux locaux et distants sont documentés et ne se chevauchent pas involontairement.
- [ ] Les pairs sont identifiés et joignables.
- [ ] Les paramètres IKE et IPsec sont compatibles et suffisamment robustes.
- [ ] Les méthodes d'authentification et les secrets sont gérés de manière sûre.
- [ ] Les règles de pare-feu autorisent les échanges nécessaires, sans ouvrir plus que nécessaire.
- [ ] Les routes et les sélecteurs correspondent au trafic attendu.
- [ ] Le NAT est traité intentionnellement.
- [ ] Les tests fonctionnent dans les deux sens.
- [ ] Le MTU et les gros transferts ont été vérifiés.
- [ ] La journalisation et la supervision sont opérationnelles.
- [ ] Les scénarios de panne et de reprise ont été testés.
- [ ] La documentation ne contient aucun secret.

## 17. Glossaire

- **Child SA :** association de sécurité qui porte les paramètres de protection du trafic utilisateur IPsec.
- **ESP :** protocole IPsec couramment utilisé pour protéger le trafic.
- **IKEv2 :** protocole de négociation et d'authentification pour IPsec.
- **MTU :** taille maximale d'un paquet transmissible sur un lien sans fragmentation à ce niveau.
- **NAT-T :** encapsulation d'ESP dans UDP pour faciliter la traversée de NAT.
- **PMTUD :** mécanisme de découverte du MTU du chemin.
- **SA (Security Association) :** ensemble de paramètres de sécurité unidirectionnels définissant comment un trafic est protégé.
- **Sélecteur de trafic :** critères qui identifient les flux couverts par une association de sécurité dans les configurations concernées.
- **VPN site-à-site :** tunnel reliant des réseaux via des passerelles.
- **WireGuard :** technologie VPN basée sur un tunnel IP et des mécanismes cryptographiques modernes.

## 18. Références pour approfondir

- RFC 4301 — Security Architecture for the Internet Protocol (IPsec).
- RFC 4303 — IP Encapsulating Security Payload (ESP).
- RFC 7296 — Internet Key Exchange Protocol Version 2 (IKEv2).
- RFC 3947 et RFC 3948 — négociation et encapsulation UDP d'IPsec pour la traversée NAT.
- RFC 2784 — Generic Routing Encapsulation (GRE).
- RFC 8201 — Path MTU Discovery for IP version 6.

Consulte les versions et mises à jour pertinentes des RFC avant un déploiement réel.

## Conclusion

Au niveau intermédiaire, la compétence clé est de relier les mécanismes entre eux : une négociation IKE réussie ne garantit pas que le routage, les sélecteurs, le NAT, le pare-feu et le MTU soient corrects. Une démarche structurée, des tests dans les deux sens et des preuves collectées à chaque étape permettent de passer d'un simple statut « VPN actif » à un diagnostic fiable.
