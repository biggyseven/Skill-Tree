# DHCP & DNS — Niveau Expert

> **Format des schémas :** diagrammes textuels ASCII/Unicode intégrés directement dans ce fichier. Aucun SVG, PNG, HTML brut ou dossier externe n’est nécessaire.
>
> **Positionnement :** ce niveau s’appuie sur les acquis DHCP/DNS débutant et intermédiaire. Il traite de la conception à grande échelle, de la résilience, des contrôles de sécurité, de l’observabilité et du dépannage fondé sur des preuves.

**Domaine :** services réseau et infrastructure IP  
**Niveau :** Expert  
**Prérequis :** IPv4/IPv6, VLAN, relais DHCP, cycle DORA, DHCPv6/SLAAC, récursion et autorité DNS, zones directes/inverses, TTL, transferts de zone, mises à jour dynamiques, DHCP snooping et notions de DNSSEC.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois pouvoir :

- concevoir des services DHCPv4 et DHCPv6 redondants sur plusieurs sites, VLAN et domaines d’administration ;
- analyser les interactions entre relais, `giaddr`, option 82, politiques de sélection de scope et mécanismes de haute disponibilité ;
- dimensionner les pools à partir de mesures, de la durée des baux et des profils de mobilité ;
- distinguer une panne de disponibilité, un conflit d’adresses, un épuisement de pool et une incohérence de configuration ;
- concevoir une architecture DNS récursive et autoritaire séparée, avec segmentation, vues, délégations et politiques de réponse ;
- comprendre les conséquences opérationnelles des TTL, du cache négatif, des changements d’adresses et des mises à jour dynamiques ;
- mettre en œuvre une stratégie de résilience DNS et un déploiement DNSSEC avec validation et plan de retour arrière ;
- examiner les risques liés aux transferts de zone, aux résolveurs ouverts, à l’empoisonnement de cache et à l’usurpation DHCP ;
- corréler journaux, captures réseau, métriques et données de configuration pour isoler une cause racine ;
- documenter une modification de production avec critères de succès, critères d’arrêt et procédure de rollback.


## 1. Concevoir l’architecture comme un ensemble de services

DHCP et DNS sont souvent présentés comme deux services simples : l’un attribue une configuration IP, l’autre associe des noms et des données. À l’échelle d’une entreprise, ils deviennent toutefois des dépendances critiques. Un poste peut être physiquement connecté et disposer d’un lien Ethernet fonctionnel, mais rester inutilisable si aucun bail ne peut être obtenu ou si les noms internes ne se résolvent plus.

Il faut donc séparer les rôles logiques, même lorsque plusieurs rôles sont hébergés sur un même système :

- **agents DHCP/relais** : transportent les requêtes entre sous-réseaux et ajoutent les informations de contexte prévues par le protocole ;
- **serveurs DHCP** : gèrent les pools, les baux, les réservations, les politiques et les options ;
- **résolveurs récursifs** : reçoivent les questions des clients, utilisent leur cache et interrogent les serveurs nécessaires ;
- **serveurs autoritaires** : publient les données d’une zone et répondent pour cette zone ;
- **outils de gestion et de supervision** : assurent l’inventaire, les sauvegardes, les alertes, la journalisation et les contrôles de changement.

### Schéma 1 — Séparation des rôles et des flux

```text
        CLIENTS / VLANs                         SERVICES CENTRAUX
+-----------------------------+       +----------------------------------+
| VLAN 10   VLAN 20   VLAN 30 |       |                                  |
|   PCs      Wi-Fi    IoT     |       |  +----------------------------+  |
+-----+--------+--------+------+       |  | DHCP-A / DHCP-B             |  |
      |        |        |              |  | pools, baux, politiques     |  |
      +--------+--------+--------------+->+----------------------------+  |
               | relais DHCP           |                                  |
               |                        |  +----------------------------+  |
               +----------------------->|  | Résolveurs récursifs       |  |
                                        |  | cache, ACL, validation     |  |
                                        |  +-------------+--------------+  |
                                        |                |                 |
                                        |  +-------------v--------------+  |
                                        |  | DNS autoritaires           |  |
                                        |  | zones internes/publiques   |  |
                                        |  +----------------------------+  |
                                        +----------------------------------+
```

La topologie logique ne signifie pas que tous les flux sont autorisés. Les relais DHCP doivent atteindre les serveurs DHCP sur les ports prévus par le protocole ; les clients doivent joindre leurs résolveurs ; les résolveurs doivent pouvoir effectuer les requêtes sortantes nécessaires ; les serveurs autoritaires publics ne doivent pas nécessairement accepter la récursion. Les ACL et pare-feu doivent refléter ces rôles, et non appliquer une règle globale « autoriser DNS » sans distinction de source, de destination et de fonction.

### 1.1 Les plans de contrôle et de données

Le plan de données transporte les paquets : une requête DNS UDP/53, une réponse TCP/53, ou un échange DHCP relayé. Le plan de contrôle comprend les bases de baux, les configurations de zones, les relations maître/secondaire, les politiques et les changements administratifs. Une panne du plan de données peut empêcher les clients de joindre un serveur dont la configuration est correcte ; une panne du plan de contrôle peut laisser les requêtes existantes fonctionner tout en empêchant une modification ou une nouvelle attribution.

**Principe de conception :** documenter séparément la disponibilité du service, la disponibilité de son plan de gestion et la fraîcheur de ses données. Une page de supervision verte ne suffit pas si elle ne vérifie que le processus logiciel.

### 1.2 Domaines de panne et blast radius

Éviter de faire dépendre tous les sites d’un seul équipement, d’une seule alimentation, d’un seul chemin WAN ou d’une seule zone de gestion. La redondance ne se mesure pas au nombre de serveurs, mais à l’indépendance des domaines de panne. Deux serveurs dans la même baie, derrière le même commutateur et alimentés par le même onduleur ne constituent pas nécessairement une résilience suffisante.

```text
MAUVAISE INDÉPENDANCE                 MEILLEURE SÉPARATION
+----------------------+              +----------------+  +----------------+
| Site principal       |              | Site A         |  | Site B         |
|  DHCP-A  DHCP-B      |              | DHCP-A         |  | DHCP-B         |
|  même LAN / énergie  |              | chemin WAN A    |  | chemin WAN B    |
+----------+-----------+              +--------+-------+  +-------+--------+
           |                                   |                  |
           +--- panne commune -----------------+------------------+
                                               
La redondance doit être évaluée selon les pannes que l'architecture peut réellement
survivre : serveur, lien, routeur, site, stockage, identité ou erreur de changement.
```


## 2. DHCPv4 à grande échelle : relais, politiques et sélection de scope

### 2.1 Relais : le contexte est aussi important que le paquet

Un client qui ne possède pas encore d’adresse IPv4 envoie typiquement un DHCPDISCOVER local en broadcast. Les routeurs ne propagent pas automatiquement ce broadcast à travers les sous-réseaux. Le relais reçoit la demande, l’envoie au serveur configuré et ajoute les informations qui permettent de déterminer le réseau d’origine. Le serveur choisit ensuite le scope et construit la réponse ; le relais la transmet au client.

### Schéma 2 — Chaîne de décision DHCPv4

```text
CLIENT              RELAIS L3                 SERVEUR DHCP
  |                     |                           |
  | DISCOVER broadcast  |                           |
  |-------------------->|                           |
  |                     | renseigne giaddr          |
  |                     | éventuellement option 82 |
  |                     |------ requête relayée ---->
  |                     |                           | identifie le réseau
  |                     |                           | choisit le scope
  |                     |<------ réponse ------------|
  |<----- OFFER/ACK ----|                           |
  |                     |                           |
```

Le relais n’est pas un serveur de baux. Il ne doit pas être confondu avec un proxy applicatif générique : il participe à l’échange DHCP et transporte le contexte du réseau client.

### 2.2 `giaddr` et option 82 : ne pas les confondre

Le champ `giaddr` est l’adresse IPv4 du relais utilisée par le serveur pour déterminer le réseau client dans les scénarios relayés. L’option 82 (*Relay Agent Information*) peut ajouter un contexte plus fin, par exemple l’identifiant de circuit ou l’identifiant distant. Elle peut aider à appliquer des politiques par port d’accès, circuit ou équipement, si les relais et le serveur la prennent en charge.

- `giaddr` : contexte de couche 3 fourni par le relais ;
- option 82 : informations supplémentaires sur le circuit ou le relais ;
- adresse IP source du paquet relayé : information de transport, qui ne remplace pas nécessairement les champs de sélection de scope ;
- adresse MAC du client : utile, mais insuffisante pour identifier à elle seule le bon sous-réseau dans tous les environnements.

### Schéma 3 — Sélection du scope avec contexte de relais

```text
PC du VLAN 20        RELAIS (passerelle)              SERVEUR DHCP
192.168.20.0/24      giaddr 192.168.20.1              scopes configurés
      |                       |                              |
      | DHCPDISCOVER          |                              |
      |---------------------->|                              |
      |                       | giaddr=192.168.20.1          |
      |                       | option 82: circuit/port      |
      |                       |----------------------------->|
      |                       |                              | sélectionne le
      |                       |                              | scope 192.168.20.0/24
      |                       |<-----------------------------|
      |<----------------------| réponse relayée              |

Si le scope attendu n'est pas choisi, vérifier d'abord le contexte relayé,
les scopes actifs, les politiques et les exclusions — pas uniquement le pool.
```

### 2.3 Option 82 et confiance

L’option 82 est un mécanisme de contexte, pas une preuve cryptographique d’identité. Un déploiement doit définir quels équipements sont autorisés à insérer, conserver ou supprimer ces informations. Les commutateurs d’accès peuvent être configurés pour ajouter l’option ; le relais ou le serveur doit avoir un comportement défini lorsque l’option arrive d’un port non fiable ou d’un chemin inattendu.

Mesures recommandées :

1. activer DHCP snooping lorsque la plateforme le permet et vérifier la compatibilité avec les relais ;
2. définir les ports de confiance uniquement là où les réponses DHCP légitimes sont attendues ;
3. documenter la politique de traitement de l’option 82 sur chaque frontière ;
4. tester les cas où l’option est absente, dupliquée ou inattendue ;
5. surveiller les messages de rejet sans désactiver aveuglément les protections pour « rétablir le service ».

### 2.4 Dimensionnement des pools et durée des baux

Un pool doit être dimensionné à partir de l’usage réel, et pas seulement du nombre théorique d’utilisateurs. Un réseau Wi-Fi invité avec forte rotation peut avoir besoin d’un nombre d’adresses élevé même si le nombre de clients simultanés moyen est modéré. À l’inverse, des postes fixes avec baux longs et réservations stables consomment le pool de manière prévisible.

Variables à suivre :

- nombre d’adresses utilisables après exclusions et réservations ;
- pic de baux actifs et taux d’occupation ;
- vitesse d’arrivée et de départ des clients ;
- durée moyenne de présence sur le réseau ;
- durée du bail et rythme de renouvellement ;
- marge de croissance et événements exceptionnels (rentrée, conférence, déploiement massif).

Une durée de bail courte accélère la récupération des adresses après le départ d’un client, mais augmente le volume de renouvellements et la dépendance au service DHCP. Une durée longue réduit la fréquence des échanges, mais peut garder des adresses occupées plus longtemps après des changements de mobilité ou de topologie. Il n’existe pas de valeur universelle : tester le profil de clients et les capacités des serveurs.

### Schéma 4 — Lecture d’un pool à partir des mesures

```text
Capacité utilisable du pool :  500 adresses
Baux actifs au pic          :  390 adresses
Réservations/exclusions     :  à comptabiliser séparément selon la plateforme
Marge disponible            :  capacité utilisable - occupation réelle

0%             50%                  80%              100%
|---------------|--------------------|----------------|
[ faible usage ] [ surveiller tendance ] [ alerte / risque d'épuisement ]

Un seuil de 80 % est un exemple de politique, pas une règle protocolaire.
La tendance et le temps restant avant saturation comptent autant que le pourcentage.
```

Les alertes devraient distinguer « pool presque plein » et « pool en croissance rapide ». Une occupation de 82 % stable depuis six mois peut être moins urgente qu’une occupation passée de 50 % à 78 % en deux heures.

### 2.5 Réservations, exclusions et politiques

Une réservation lie un identifiant client à une adresse selon les règles du serveur ; une exclusion retire des adresses de l’allocation dynamique ; une option transmet une valeur de configuration (passerelle, DNS, suffixe, serveur de démarrage, etc.). Les politiques peuvent sélectionner des paramètres selon le réseau, le relais, la classe client ou des attributs pris en charge.

Ne pas utiliser les réservations comme substitut à un plan d’adressage documenté. Une réservation oubliée peut entrer en collision avec une plage statique si la configuration du serveur n’exclut pas l’adresse. Les changements de MAC, les téléphones utilisant une adresse MAC privée et les équipements clonés peuvent aussi modifier l’identifiant vu par le serveur.

### 2.6 Dépannage DHCPv4 par preuve

Procéder dans l’ordre du chemin réel :

1. le client émet-il une demande ?
2. la demande atteint-elle le VLAN et le relais ?
3. le relais l’envoie-t-il au bon serveur ?
4. le serveur reçoit-il les bons `giaddr` et option 82 ?
5. le bon scope est-il sélectionné et dispose-t-il d’adresses ?
6. le serveur émet-il une réponse ?
7. la réponse revient-elle au relais et au client ?
8. le client accepte-t-il la configuration et peut-il utiliser la passerelle ?

```text
Pas de bail
   |
   +-- aucun DISCOVER côté client ? ----> interface, VLAN, pilote, client DHCP
   |
   +-- DISCOVER local, rien côté serveur ? -> relais, route, ACL, UDP 67/68
   |
   +-- requête au serveur, pas d'OFFER ? --> scope, politiques, capacité, logs
   |
   +-- OFFER côté serveur, absent du client ? -> chemin retour, relais, snooping
   |
   +-- bail reçu, réseau inutilisable ? ----> masque, passerelle, DNS, conflit IP
```

Ne pas commencer par redémarrer le serveur : cette action peut effacer des indices, perturber tous les clients et ne pas corriger un relais mal configuré.


## 3. DHCP haute disponibilité : comprendre le modèle avant de basculer

Les mécanismes de haute disponibilité diffèrent selon le produit. Ils peuvent utiliser une relation failover entre deux serveurs, un service de cluster, une réplication de base, une répartition de plages ou un mécanisme propre à une solution réseau. Il faut vérifier précisément ce qui est répliqué : baux, réservations, exclusions, options, politiques, état de partenaire et changements de configuration.

### 3.1 Ce que signifie réellement « redondant »

Deux serveurs capables de répondre ne sont pas automatiquement une paire cohérente. Si les deux gèrent le même pool sans coordination, ils peuvent proposer simultanément une même adresse. Si le serveur secondaire n’a pas reçu une réservation récente, il peut attribuer une adresse qui devait être réservée. Si la base de baux est répliquée mais pas les options, les clients peuvent obtenir une adresse tout en recevant un DNS ou une passerelle incorrects.

### Schéma 5 — Modèle conceptuel de haute disponibilité

```text
                    +----------------------+
                    | Clients / relais     |
                    +----------+-----------+
                               |
                     requêtes DHCP relayées
                               |
                +--------------+--------------+
                |                             |
        +-------v--------+            +-------v--------+
        | DHCP-A         |<---------->| DHCP-B         |
        | baux / config  | réplication| baux / config  |
        +----------------+            +----------------+
                |                             |
                +------ supervision ----------+

À valider : état des baux, réservations, options, délai de réplication,
comportement en partition réseau, reprise après panne et procédure de retour.
```

### 3.2 Split-scope et failover ne sont pas la même chose

Un modèle de plages séparées répartit l’espace d’adresses entre serveurs. Il peut fournir une continuité partielle, mais ne signifie pas nécessairement que l’état des baux est partagé. Le failover coordonné, lorsqu’il est proposé, définit des règles de communication et de responsabilité entre partenaires. Les termes exacts, les états et les timers varient selon la solution ; ils ne doivent pas être transposés d’un produit à un autre sans documentation.

### 3.3 Scénarios à tester avant la production

- arrêt brutal d’un serveur ;
- perte du lien entre les partenaires mais maintien de l’accès client ;
- perte du réseau de gestion ;
- retour du partenaire après une longue interruption ;
- modification de réservation pendant que le partenaire est indisponible ;
- restauration d’une sauvegarde ;
- redémarrage simultané des deux serveurs ;
- saturation du pool pendant une période de bascule.

Pour chaque scénario, définir les résultats attendus, les logs à examiner, le délai maximal acceptable et les actions interdites. La partition réseau est particulièrement importante : elle peut faire croire à chaque partenaire que l’autre est indisponible. Le mécanisme HA doit limiter le risque de double attribution et de divergence de base.

### 3.4 Sauvegarde et reprise

Une sauvegarde exploitable comprend les fichiers de configuration, les données de baux lorsque le produit l’exige, les clés ou secrets nécessaires, la documentation des dépendances, et la procédure de restauration. Tester une restauration dans un environnement isolé. Un fichier de sauvegarde non testé n’est pas une preuve de capacité de reprise.


## 4. DHCPv6, SLAAC et réseaux à double pile

IPv6 ne réutilise pas simplement le modèle DHCPv4. Le client peut construire une adresse à partir des annonces de routeur (SLAAC), obtenir certains paramètres via DHCPv6, ou utiliser une combinaison des deux. Les Router Advertisements indiquent notamment les préfixes et des indicateurs qui influencent le comportement des clients. Les détails d’implémentation varient selon les systèmes.

### Schéma 6 — Choix de configuration IPv6

```text
                   +--------------------------+
                   | Router Advertisement     |
                   | préfixe, flags, route    |
                   +------------+-------------+
                                |
                +---------------+----------------+
                |                                |
       SLAAC possible                    DHCPv6 indiqué/utilisé
       adresse construite                selon flags et client
                |                                |
                +----------------+---------------+
                                 |
                       configuration IPv6 finale

SLAAC, DHCPv6 et la distribution des résolveurs DNS sont des fonctions liées,
mais distinctes. Vérifier le comportement réel du système client.
```

### 4.1 DHCPv6 avec état et sans état

Le DHCPv6 avec état peut attribuer des adresses et suivre des associations de ressources. Le DHCPv6 sans état sert plutôt à transmettre des paramètres supplémentaires lorsque l’adresse est obtenue autrement, par exemple avec SLAAC. Les termes « avec état » et « sans état » ne signifient pas que tout le réseau IPv6 possède ou ne possède pas d’état : ils décrivent le rôle du service DHCPv6 dans l’attribution.

### 4.2 Relais DHCPv6 et identification

Le relais DHCPv6 transporte les messages du client vers le serveur et peut inclure des informations de lien ou d’interface. Les champs et options ne sont pas identiques à DHCPv4 : ne pas chercher `giaddr` dans un message DHCPv6. Les analyses doivent utiliser les champs et options propres à DHCPv6, les Router Advertisements et les routes IPv6.

### 4.3 DNS en IPv6

Les clients IPv6 peuvent apprendre des résolveurs via les mécanismes appropriés aux systèmes et à l’architecture, notamment les options DHCPv6 ou les annonces de routeur selon les fonctions prises en charge. Les enregistrements DNS `AAAA` publient des adresses IPv6 ; les zones inverses IPv6 utilisent `ip6.arpa`. La présence d’un enregistrement AAAA ne garantit pas que le chemin IPv6 fonctionne. Tester la connectivité, la MTU, le filtrage et la sélection d’adresse séparément de la résolution DNS.

### 4.4 Doubles piles : une source de faux diagnostics

Une application peut préférer IPv6 et échouer sur ce chemin alors que l’IPv4 fonctionne. Le nom se résout correctement, mais la session échoue : ce n’est pas nécessairement une panne DNS. Comparer les résultats A/AAAA, tester explicitement IPv4 et IPv6, et examiner la préférence d’adresse et le chemin réseau.


## 5. Concevoir une architecture DNS récursive résiliente

### 5.1 Séparer récursion et autorité

Un résolveur récursif cherche les réponses pour les clients, met les résultats en cache et applique des politiques de validation ou de filtrage. Un serveur autoritaire répond pour les zones qu’il héberge. Les rôles peuvent coexister dans certains produits, mais leur séparation réduit l’exposition et simplifie les règles de pare-feu.

### Schéma 7 — Résolveur récursif et serveur autoritaire

```text
CLIENT INTERNE       RÉSOLVEUR RÉCURSIF       HIÉRARCHIE DNS
      |                       |                      |
      | question: app.example |                      |
      |---------------------->|                      |
      |                       | cache ?              |
      |                       |-- sinon : root ------>|
      |                       |<-- referral ----------|
      |                       |-- TLD ---------------->
      |                       |<-- referral ----------|
      |                       |-- autoritaire ------->|
      |                       |<-- réponse finale ----|
      |<-- réponse mise en cache --------------------|

Le client interroge normalement le résolveur configuré. Il n'a pas besoin de
parcourir lui-même toute la hiérarchie DNS dans une résolution récursive classique.
```

La récursion doit être limitée aux clients et réseaux autorisés. Un serveur autoritaire exposé publiquement ne devrait pas devenir un résolveur ouvert par inadvertance. Cela peut créer un risque d’abus, de réflexion/amplification et de consommation de ressources.

### 5.2 Architecture multi-sites

Les sites distants peuvent utiliser des résolveurs locaux pour réduire la latence et continuer à résoudre les noms en cache pendant une interruption WAN. Cependant, les caches locaux peuvent conserver des données qui ne sont plus à jour jusqu’à expiration du TTL. Il faut déterminer quelles zones internes sont résolues localement, via des redirecteurs conditionnels ou via des liens vers les serveurs autoritaires internes.

```text
 SITE A                               SITE B
+----------------------+             +----------------------+
| Clients              |             | Clients              |
|    |                 |             |    |                 |
| [Resolver A]         |==== WAN ====| [Resolver B]         |
| cache / ACL          |             | cache / ACL          |
+---------+------------+             +-----------+----------+
          |                                      |
          +---------------+----------------------+
                          |
                 +--------v---------+
                 | DNS autoritaires |
                 | zones internes   |
                 +------------------+

Question de conception : que doit continuer à résoudre chaque site si le WAN tombe ?
Réponse à documenter : cache, zones locales, secondaires, redirecteurs et limites.
```

### 5.3 Forwarding, récursion complète et zones conditionnelles

Un résolveur peut effectuer lui-même les étapes de résolution ou transmettre les questions à des redirecteurs. Les redirecteurs conditionnels envoient certaines zones vers des serveurs précis, par exemple `corp.example` vers les DNS internes. Une mauvaise règle de transfert peut provoquer une boucle : le résolveur A transmet à B, B renvoie à A, et les requêtes échouent après un délai ou une limite de récursion.

### Schéma 8 — Boucle de transfert DNS

```text
Résolveur A                         Résolveur B
    |                                   |
    | question zone.corp.example        |
    |---------------------------------->|
    |                                   | redirecteur vers A
    |<----------------------------------|
    | retransmet à B                    |
    |---------------------------------->|  ... boucle

Symptômes : latence, SERVFAIL, journaux de récursion répétée.
Correction : tracer les règles de forwarding et définir un serveur autoritaire
ou un chemin de résolution qui ne renvoie pas la question à son émetteur.
```

### 5.4 Anycast, unicast et diversité

Anycast permet à plusieurs instances d’annoncer la même adresse et de laisser le routage diriger les clients vers une instance proche selon la topologie. Cela peut améliorer la latence et la résilience, mais introduit des exigences d’exploitation : cohérence de configuration, suivi de la santé des instances, comportement lors du retrait d’une route et observation du site réellement atteint. Deux adresses unicast distinctes peuvent être plus faciles à dépanner dans certains environnements. Le choix dépend du nombre de sites, de la maîtrise du routage et des outils de mesure.


## 6. DNS autoritaire : zones, délégations et changements contrôlés

### 6.1 Une zone est une frontière administrative

Un domaine DNS et une zone ne sont pas toujours identiques. Une zone contient les données autoritaires d’une portion de l’espace de noms, et une délégation peut transférer l’autorité d’un sous-domaine à d’autres serveurs. Les enregistrements NS dans la zone parent indiquent la délégation ; la zone enfant doit publier ses propres données autoritaires cohérentes.

### Schéma 9 — Délégation parent/enfant

```text
                 ZONE PARENTE : example.
              +---------------------------+
              | NS pour corp.example      |
              | glue si nécessaire        |
              +-------------+-------------+
                            |
                            | délégation NS
                            v
                 ZONE ENFANT : corp.example
              +---------------------------+
              | SOA, NS, A/AAAA, MX, TXT  |
              | données autoritaires      |
              +---------------------------+

Le parent délègue l'autorité ; il ne contient pas nécessairement toutes les
réponses de la zone enfant. Vérifier les NS aux deux niveaux lors d'un incident.
```

### 6.2 SOA, serial et transferts de zone

Le SOA contient des paramètres administratifs, dont le serial de zone et des temporisations liées au rafraîchissement des secondaires. Le serial doit évoluer selon une politique cohérente lors d’une modification de zone. Les transferts AXFR ou IXFR permettent aux secondaires de récupérer la zone entière ou les différences, selon la prise en charge et les conditions.

Un transfert de zone réussi ne prouve pas que la délégation publique pointe vers les bons serveurs. Inversement, une délégation correcte n’assure pas que les secondaires possèdent la version la plus récente. Vérifier séparément :

- le contenu et le serial sur le primaire ;
- le serial et le contenu sur chaque secondaire ;
- l’autorisation de transfert ;
- la connectivité TCP nécessaire aux transferts ;
- la délégation et les enregistrements NS publiés chez le parent ;
- la cohérence des enregistrements glue lorsque nécessaires.

### 6.3 Changements de zone sans interruption

Un changement DNS doit être préparé en fonction des caches. Réduire le TTL juste avant une modification ne supprime pas les copies déjà mises en cache avec l’ancien TTL : il faut anticiper la baisse, attendre l’expiration des anciens caches, puis effectuer le changement. Après la migration, garder l’ancien service disponible pendant la fenêtre de transition lorsque c’est possible.

```text
AVANT MIGRATION                     APRÈS BASCULE
TTL élevé                            TTL réduit à l'avance
     |                                      |
     | attendre expiration des anciens TTL |
     v                                      v
Changer enregistrement / délégation --> vérifier autorité et cache
     |                                      |
     +--> surveiller clients                +--> conserver rollback possible

Le TTL influence la durée de conservation par les caches ; il ne force pas
un client à rafraîchir immédiatement une réponse déjà obtenue.
```

### 6.4 DNS dynamique et cohérence DHCP/DNS

Dans les environnements où DHCP met à jour DNS, il faut définir qui crée et qui supprime les enregistrements, comment les identités sont authentifiées, et comment les mises à jour sont autorisées. Si le client met à jour son enregistrement A mais que le serveur DHCP met à jour le PTR, les deux côtés peuvent diverger en cas d’échec partiel. Le comportement précis dépend du produit et de la configuration.

Bonnes pratiques :

1. documenter le propriétaire des enregistrements A/AAAA et PTR ;
2. utiliser des mises à jour authentifiées lorsque la plateforme le permet ;
3. appliquer des permissions minimales par zone et par identité ;
4. définir une procédure de nettoyage des enregistrements obsolètes ;
5. surveiller les échecs de mise à jour, pas seulement les réponses DNS ;
6. tester les renouvellements, les changements de nom et les réattributions d’adresse.

### 6.5 Scavenging et enregistrements obsolètes

Le nettoyage automatique peut retirer des enregistrements qui ne sont plus rafraîchis, mais une politique trop agressive peut supprimer un enregistrement valide si les mises à jour sont désactivées ou si le client ne peut pas rafraîchir son horodatage. Une politique trop permissive laisse des entrées anciennes et peut provoquer des erreurs d’accès. Définir les intervalles de non-rafraîchissement et de rafraîchissement selon le produit, puis tester avec des postes représentatifs avant généralisation.


## 7. Cache DNS, TTL et erreurs difficiles à interpréter

### 7.1 Cache positif et cache négatif

Une réponse positive peut être mise en cache pendant le TTL de l’enregistrement. Une réponse négative, telle que NXDOMAIN, peut également être mise en cache selon les règles du protocole et les données SOA pertinentes. C’est pourquoi la création d’un enregistrement après une réponse NXDOMAIN peut ne pas devenir visible immédiatement pour tous les clients.

### Schéma 10 — Pourquoi un changement DNS semble « ne pas marcher »

```text
Client A ---> Resolver : demande host.example
                    |
                    +--> cache NXDOMAIN encore valide
                    |          |
                    |          +--> répond NXDOMAIN sans recontacter l'autorité
                    |
Admin crée l'enregistrement sur le serveur autoritaire
                    |
                    +--> autorité répond maintenant avec une adresse

Le résolveur peut conserver le résultat négatif jusqu'à expiration du cache.
Tester : autorité directement, puis résolveur récursif, puis client final.
```

### 7.2 `NXDOMAIN`, `NODATA`, `SERVFAIL` et `REFUSED`

- **NXDOMAIN** : le nom demandé n’existe pas selon la réponse autoritaire/validée reçue.
- **NODATA** : le nom existe, mais aucun enregistrement du type demandé n’est présent ; ce résultat est souvent représenté par NOERROR avec une réponse vide et une preuve d’autorité appropriée.
- **SERVFAIL** : le serveur n’a pas pu produire une réponse valide ; causes possibles : problème d’autorité, échec de validation DNSSEC, timeout amont ou erreur interne.
- **REFUSED** : le serveur refuse la requête selon sa politique ou sa configuration.

Ne pas traduire ces quatre résultats par « DNS est en panne ». Le code de réponse aide à réduire l’espace des causes possibles.

### 7.3 TTL : outil de conception, pas garantie instantanée

Un TTL faible augmente le nombre de requêtes et la charge potentielle des résolveurs et des autorités, mais permet une propagation plus rapide après expiration des caches conformes. Un TTL élevé réduit les requêtes répétées mais prolonge la présence de données anciennes. Les applications peuvent ajouter leur propre cache au-delà du cache DNS du système ; un test dans un navigateur peut donc différer d’un test `dig`/`nslookup`.

### 7.4 UDP et TCP sur DNS

DNS utilise souvent UDP pour les requêtes courantes, mais TCP fait partie du fonctionnement normal : transferts de zone, réponses nécessitant TCP, et reprises après troncature en sont des exemples. Un pare-feu qui autorise UDP/53 mais bloque TCP/53 peut provoquer des pannes partielles et difficiles à reproduire. Le transport chiffré DNS (DoT, DoH) change le chemin et le contrôle réseau ; il ne remplace pas la nécessité d’une architecture de résolution cohérente.


## 8. DNSSEC : intégrité, chaîne de confiance et exploitation

DNSSEC permet de valider cryptographiquement l’origine et l’intégrité des données DNS signées. Il ne chiffre pas les requêtes et ne garantit pas la confidentialité. La validation repose sur une chaîne de confiance depuis une ancre de confiance vers les délégations signées et les données de zone. Une configuration incorrecte des clés, signatures ou DS peut rendre un nom inaccessible pour les résolveurs validants, souvent avec `SERVFAIL`.

### Schéma 11 — Chaîne de confiance DNSSEC

```text
Ancre de confiance (racine)
          |
          | DNSKEY / RRSIG validés
          v
Zone parente signée
          |
          | DS dans la zone parente
          v
Zone enfant signée
          |
          | DNSKEY / RRSIG
          v
Réponse validée pour le nom demandé

Une rupture de chaîne (DS incohérent, signature expirée, clé incorrecte) peut
faire échouer la validation même si l'enregistrement A/AAAA existe sur l'autorité.
```

### 8.1 KSK, ZSK et rotation de clés

Les termes KSK (*Key Signing Key*) et ZSK (*Zone Signing Key*) sont utilisés dans certains modèles de gestion pour distinguer les fonctions de signature. Les détails de rotation dépendent de la politique et du logiciel. Toute rotation doit coordonner les clés DNSKEY, les signatures, les DS publiés chez le parent et les délais de cache. Une rotation mal séquencée peut créer une rupture de confiance.

### 8.2 Diagnostiquer un échec DNSSEC

1. comparer la réponse avec validation et sans validation depuis un environnement de test autorisé ;
2. vérifier les horodatages et la validité des signatures ;
3. examiner DNSKEY, DS et RRSIG ;
4. vérifier les changements récents de clés ou de délégation ;
5. contrôler l’heure des systèmes qui signent et valident ;
6. ne pas désactiver globalement la validation comme première solution ;
7. si une mesure d’urgence est nécessaire, la limiter, la documenter et la retirer dès que la chaîne est réparée.

### 8.3 NSEC et NSEC3

Les mécanismes de preuve d’inexistence permettent à DNSSEC de signer les réponses négatives. Les choix de paramètres influencent la confidentialité de l’énumération et les coûts de calcul. Ils doivent être configurés selon la plateforme et la politique de zone. Il ne faut pas présenter NSEC3 comme une garantie absolue contre l’énumération, ni le choisir sans considérer la charge de validation.


## 9. Menaces et durcissement opérationnel

### 9.1 Menaces DHCP

Les menaces courantes incluent les serveurs DHCP non autorisés, l’épuisement du pool par de nombreuses identités clientes, l’usurpation de réponses, les options malveillantes et les erreurs de confiance sur les relais. Les protections disponibles varient selon les commutateurs et serveurs.

- DHCP snooping : distinguer ports fiables et non fiables et contrôler les messages ;
- limitation de débit : réduire les rafales abusives, en tenant compte des démarrages massifs légitimes ;
- contrôle de l’option 82 : définir les frontières de confiance ;
- segmentation : limiter la portée d’un domaine de diffusion ;
- surveillance : détecter les changements anormaux de baux, de serveurs et de taux de DISCOVER.

### Schéma 12 — Serveur DHCP non autorisé

```text
                    VLAN utilisateur
+-----------+       +-------------------+       +--------------------+
| Client    |------>| Switch d'accès    |------>| DHCP légitime      |
+-----------+       |                   |       +--------------------+
                    | port fiable  -----+------------------------------
                    | port non fiable   |
                    +--------+----------+
                             |
                             +------> serveur DHCP rogue
                                     offre une passerelle/DNS faux

Contrôle : DHCP snooping et ports de confiance configurés selon la topologie.
Vérifier les fonctions exactes de la plateforme et les exceptions nécessaires.
```

### 9.2 Menaces DNS

Les risques comprennent la récursion ouverte, l’empoisonnement de cache, l’abus d’amplification, les transferts de zone non autorisés, la modification des enregistrements, les erreurs de délégation et les politiques de filtrage trop larges. DNSSEC protège l’intégrité des données signées mais ne remplace ni les ACL, ni le contrôle d’accès aux zones, ni la supervision.

Mesures recommandées :

- autoriser la récursion uniquement aux réseaux qui en ont besoin ;
- restreindre les transferts de zone aux secondaires autorisés ;
- séparer les vues internes et externes si nécessaire et documenter les différences ;
- appliquer les correctifs et suivre les annonces de sécurité du logiciel utilisé ;
- limiter les accès d’administration et protéger les secrets de mise à jour ;
- surveiller les pics de requêtes, les taux de SERVFAIL/NXDOMAIN et les changements de délégation ;
- éviter les règles de pare-feu qui laissent croire que tout trafic DNS est digne de confiance.

### 9.3 DoT/DoH et contrôle d’entreprise

DNS over TLS et DNS over HTTPS chiffrent le transport entre le client et un résolveur compatible. Ils peuvent améliorer la confidentialité sur le réseau local, mais compliquent la visibilité et l’application de politiques lorsque les clients utilisent des résolveurs non gérés. La stratégie doit être explicite : résolveurs autorisés, mécanismes de configuration, journaux disponibles, exigences de confidentialité et traitement des appareils personnels. Bloquer simplement un port peut être insuffisant si l’application utilise un transport différent.

### 9.4 Limites de la journalisation

Les journaux peuvent contenir des noms internes, des identifiants de clients et des informations de navigation. Collecter uniquement ce qui est nécessaire, définir la durée de conservation et contrôler les accès. La sécurité opérationnelle comprend aussi la minimisation des données et la protection des sauvegardes.


## 10. Observabilité : mesurer ce que le client ressent

La supervision doit combiner disponibilité du processus, tests fonctionnels et métriques de qualité. Un serveur peut répondre au ping tout en refusant la récursion. Un serveur DHCP peut être joignable mais ne plus disposer d’adresses libres. Un DNS autoritaire peut répondre correctement alors que la délégation publique pointe ailleurs.

### 10.1 Indicateurs DHCP

- occupation des pools et vitesse de croissance ;
- taux de DISCOVER, OFFER, REQUEST, ACK et NAK ;
- durée de traitement et taux d’échec ;
- conflits détectés et adresses déclarées en conflit ;
- état de réplication/partenaire HA ;
- nombre de requêtes relayées et erreurs du relais ;
- changements de configuration et échecs de sauvegarde.

### 10.2 Indicateurs DNS

- latence de résolution médiane et percentiles élevés ;
- taux de succès, NXDOMAIN, SERVFAIL et REFUSED ;
- taux de cache hit/miss ;
- disponibilité de la récursion et de l’autorité testées séparément ;
- fraîcheur des secondaires et écarts de serial ;
- échecs de validation DNSSEC ;
- taux de réponses TCP et échecs de transport ;
- changements de délégation, NS, DS et glue.

### Schéma 13 — Supervision à plusieurs couches

```text
                  TESTS DEPUIS UN CLIENT
                           |
          +----------------+----------------+
          |                                 |
     Test DHCP                         Test DNS
          |                                 |
  obtention d'un bail              résolution A/AAAA
  options attendues                récursion + autorité
          |                                 |
          +----------------+----------------+
                           |
                    métriques/logs
                           |
               corrélation et alerte utile

Un ping teste la connectivité IP ; il ne prouve pas le bon fonctionnement
DHCP, la récursion DNS, la fraîcheur d'une zone ou la validation DNSSEC.
```

### 10.3 Alertes utiles, pas seulement des seuils

Une alerte devrait fournir une conséquence, une mesure et une première piste. Exemple : « le pool VLAN 40 est à 88 % et croît de 4 % par heure ; saturation estimée avant deux heures » est plus utile que « pool supérieur à 80 % ». De même, « SERVFAIL augmente uniquement sur les réponses validées DNSSEC après une modification DS » est plus actionnable qu’une alerte générique « DNS indisponible ».

### 10.4 Synchronisation horaire et corrélation

Les journaux DHCP, DNS, routeurs, pare-feu et postes doivent partager une heure fiable. Sans synchronisation, l’ordre apparent des événements peut être trompeur. Conserver les identifiants de requête lorsque disponibles, les adresses sources, les interfaces, les VLAN, les codes de réponse et les horodatages. Masquer les données personnelles non nécessaires avant de partager une capture ou un journal.


## 11. Méthode de dépannage avancé

Un dépannage expert sépare les symptômes, les hypothèses et les preuves. Il commence par définir le périmètre : un client, un VLAN, un site, une zone DNS, un type de requête, IPv4 ou IPv6, récursif ou autoritaire. Ensuite, il cherche le premier point du chemin où le comportement observé diverge du comportement attendu.

### 11.1 Arbre de décision DHCP

```text
Le client n'a pas de configuration utilisable
 |
 +-- Pas de requête DHCP visible sur le client
 |     -> service client, interface, VLAN, pilote, état du lien
 |
 +-- Requête visible sur le VLAN, pas sur le serveur
 |     -> relais, route, ACL, option de relais, UDP 67/68
 |
 +-- Serveur reçoit la requête, mais pas de réponse
 |     -> scope, politique, pool, réservation, base, logs serveur
 |
 +-- Serveur répond, client ne reçoit rien
 |     -> chemin retour, relais, snooping, filtrage, capture aux deux extrémités
 |
 +-- Client reçoit un bail, mais l'accès échoue
       -> masque, route par défaut, DNS, conflit IP, ACL, IPv6 prioritaire
```

### 11.2 Arbre de décision DNS

```text
Le nom ne se résout pas correctement
 |
 +-- Résolution directe vers l'autorité correcte ?
 |      |
 |      +-- NON -> zone, délégation, NS, serial, données autoritaires
 |      +-- OUI
 |           |
 |           +-- Résolution via le récursif correcte ?
 |                  |
 |                  +-- NON -> cache, forwarding, ACL, DNSSEC, transport
 |                  +-- OUI
 |                       |
 |                       +-- Client final échoue ?
 |                              -> cache local/applicatif, VPN, DoH/DoT,
 |                                 sélection IPv4/IPv6, suffixe de recherche
```

### 11.3 Captures et outils

Les commandes exactes dépendent de l’OS et du produit. Utiliser les outils disponibles pour comparer les points du chemin :

- `ipconfig /all`, `ipconfig /renew`, `ipconfig /flushdns` sur Windows, avec prudence sur l’impact des renouvellements ;
- `Get-DnsClientServerAddress`, `Resolve-DnsName` et les journaux système sur Windows ;
- `ip addr`, `ip route`, `resolvectl status`, `dig` et `tcpdump` sur Linux ;
- `dig +trace` pour examiner la délégation depuis un poste d’analyse autorisé ;
- captures Wireshark avec filtres `bootp`/DHCP, `dhcpv6` et `dns` selon la version ;
- commandes du serveur pour les baux, la réplication, les zones et les événements.

Une commande de diagnostic ne doit pas être présentée comme universelle : les noms d’outils, les droits requis et les effets peuvent varier. Ne jamais lancer un test intrusif sur un réseau de production sans autorisation.

### 11.4 Éviter les conclusions hâtives

- « Le serveur répond au ping, donc le service est bon » : faux, le test ne valide pas l’application.
- « Le nom existe dans la console, donc tous les clients doivent le voir » : faux, cache et délégation peuvent diverger.
- « Le bail a été obtenu, donc le réseau est configuré correctement » : faux, une passerelle ou un DNS erroné suffit à bloquer les applications.
- « Ça marche si je désactive DNSSEC » : cela indique une piste de validation, pas une correction durable.
- « Il suffit de réduire le TTL maintenant » : les caches ayant reçu l’ancien TTL peuvent le conserver jusqu’à son expiration.


## 12. Laboratoire de synthèse multi-sites

### 12.1 Topologie et plan d’adressage

```text
                         SITE CENTRAL
              +--------------------------------+
              | DHCP-A              DHCP-B     |
              | DNS-R1              DNS-R2     |
              | DNS-AUTH-1          DNS-AUTH-2 |
              +----------------+---------------+
                               |
                         WAN / VPN redondé
                    +----------+----------+
                    |                     |
                 SITE A                SITE B
            +---------------+      +---------------+
            | VLAN 10 users |      | VLAN 20 users |
            | VLAN 11 voice |      | VLAN 21 IoT   |
            | relais DHCP   |      | relais DHCP   |
            | clients DNS   |      | clients DNS   |
            +---------------+      +---------------+
```

Exemple de plan :

| Segment | IPv4 | Passerelle | Politique DHCP |
|---|---|---|---|
| Site A utilisateurs | `10.10.10.0/24` | `10.10.10.1` | bail standard, DNS internes |
| Site A voix | `10.10.11.0/24` | `10.10.11.1` | options voix selon plateforme |
| Site B utilisateurs | `10.20.20.0/24` | `10.20.20.1` | bail standard, DNS internes |
| Site B IoT | `10.20.21.0/24` | `10.20.21.1` | accès limité, réservations documentées |

Ces plages sont des exemples de laboratoire, pas une recommandation universelle. Les options voix et les politiques IoT dépendent des équipements et des exigences de sécurité.

### 12.2 Scénario A — Le pool se remplit rapidement

**Symptôme :** les nouveaux clients d’un VLAN échouent, tandis que les clients déjà connectés continuent de fonctionner.

**Hypothèses :** pool épuisé, baux trop longs pour un réseau à forte rotation, clients fantômes, serveur rogue, relais qui sélectionne le mauvais scope, ou croissance légitime.

**Plan de test :** mesurer l’occupation dans le temps ; comparer le nombre de baux et le nombre de clients observés ; vérifier les événements DHCP ; examiner les options 82 et `giaddr` ; vérifier les exclusions/réservations ; calculer la croissance et l’heure estimée de saturation.

**Correction durable :** augmenter le pool si l’adressage le permet, ajuster la durée des baux après mesure, supprimer les incohérences identifiées et alerter sur la vitesse de croissance. Ne pas raccourcir arbitrairement tous les baux sans évaluer la charge créée.

### 12.3 Scénario B — Une zone interne échoue uniquement sur un site

**Symptôme :** les noms internes se résolvent au siège, mais échouent sur le site distant ; les noms publics fonctionnent.

**Hypothèses :** redirecteur conditionnel absent ou incorrect, ACL intersite, cache négatif, serveur autoritaire interne inaccessible, suffixe de recherche différent, ou configuration DNS distribuée par DHCP différente.

**Plan de test :** afficher la configuration DNS reçue par un client du site ; interroger directement le résolveur local ; interroger l’autorité interne depuis un chemin autorisé ; comparer les réponses et TTL ; vérifier les journaux du forwarding et les routes/ACL.

**Correction durable :** corriger la règle de forwarding ou la connectivité ; valider les options DHCP ; ajouter une sonde fonctionnelle depuis le site ; documenter le comportement attendu pendant une coupure WAN.

### 12.4 Scénario C — SERVFAIL après changement DNSSEC

**Symptôme :** certains résolveurs validants répondent SERVFAIL après une modification de zone ou de délégation ; un test sans validation semble fonctionner.

**Hypothèses :** DS incohérent chez le parent, signatures expirées, DNSKEY manquante, horloge erronée ou propagation incomplète des clés.

**Plan de test :** vérifier la chaîne parent/enfant, les DS/DNSKEY/RRSIG, les dates de signature et les journaux de validation ; comparer plusieurs résolveurs indépendants ; identifier l’heure et le changement exacts.

**Correction durable :** restaurer une chaîne de confiance cohérente selon la procédure de gestion des clés ; ne pas laisser la validation désactivée comme solution permanente.

### 12.5 Scénario D — Le basculement DHCP crée des incohérences

**Symptôme :** après une panne de partenaire, certains clients obtiennent une adresse mais reçoivent des options différentes ou rencontrent des conflits.

**Hypothèses :** réplication incomplète, politiques non synchronisées, partenaire revenu dans un état inattendu, ou modèle de répartition mal compris.

**Plan de test :** consulter l’état HA, comparer la configuration des deux serveurs, vérifier les baux et réservations, examiner les logs de réplication, tester un petit nombre de clients contrôlés.

**Correction durable :** réparer la synchronisation, clarifier les responsabilités des partenaires, corriger les procédures de retour et automatiser un contrôle de cohérence de configuration.


## 13. Plan de changement et critères de retour arrière

Un changement DHCP/DNS doit définir le périmètre, les dépendances, les tests, les critères d’arrêt et le rollback avant l’intervention. Les changements d’adressage, de délégation ou de DNSSEC peuvent affecter des clients qui ne sont pas immédiatement visibles dans les tests internes.

### Checklist avant changement

- [ ] sauvegarde de la configuration et des données requises ;
- [ ] inventaire des serveurs, relais, zones, délégations et redirecteurs concernés ;
- [ ] vérification des accès d’administration et de la synchronisation horaire ;
- [ ] estimation du risque et du nombre de clients impactés ;
- [ ] plan de tests positif et négatif ;
- [ ] critères de succès mesurables ;
- [ ] critères d’arrêt explicites ;
- [ ] procédure de retour arrière et durée estimée ;
- [ ] personne responsable de la décision de rollback ;
- [ ] communication aux équipes utilisatrices.

### Checklist après changement

- [ ] nouveaux clients obtiennent les bonnes options DHCP ;
- [ ] renouvellement de bail testé sur un client représentatif ;
- [ ] résolution récursive interne et publique vérifiée ;
- [ ] réponses autoritaires et délégations contrôlées ;
- [ ] transfert de zone et serial vérifiés si concernés ;
- [ ] validation DNSSEC vérifiée si concernée ;
- [ ] journaux, métriques et alertes examinés ;
- [ ] résultats et écarts consignés ;
- [ ] anciennes configurations retirées seulement après la fenêtre de sécurité.

### Exemple de critères de rollback

- taux d’échec DHCP supérieur au seuil convenu pendant la fenêtre d’observation ;
- augmentation importante de SERVFAIL ou échec de validation DNSSEC ;
- divergences de zone entre primaire et secondaires ;
- clients recevant une passerelle ou un résolveur incorrect ;
- perte de la capacité à administrer ou restaurer le service.

Les seuils chiffrés doivent être définis à partir de la base de référence du réseau. Il n’existe pas de seuil universel valable pour tous les environnements.


## 14. Exercices de conception et de dépannage corrigés

### Exercice 1 — Sélection de scope incorrecte

**Situation :** un client du VLAN `10.40.30.0/24` reçoit une adresse du pool `10.40.10.0/24`.

**Correction attendue :** vérifier l’interface relais réellement utilisée, le `giaddr`, l’option 82 et les règles de sélection/politiques du serveur. Vérifier aussi les scopes qui se chevauchent et la configuration du relais. Ne pas corriger le problème en créant simplement une réservation pour le client : cela masque la cause et ne répare pas le VLAN.

### Exercice 2 — Le DNS répond NXDOMAIN après création d’un enregistrement

**Situation :** l’autorité répond avec l’adresse attendue, mais le résolveur d’entreprise continue à répondre NXDOMAIN.

**Correction attendue :** examiner le cache négatif et son expiration, vérifier que la question est posée au résolveur prévu, puis tester après expiration ou purger le cache selon les procédures autorisées. Vérifier qu’aucune autre zone ou vue ne répond pour le même nom.

### Exercice 3 — Une zone secondaire ne suit plus les changements

**Situation :** le primaire possède un serial plus récent, mais le secondaire sert encore l’ancienne adresse.

**Correction attendue :** vérifier SOA, notifications, rafraîchissement, connectivité TCP, autorisation de transfert, journaux du secondaire et éventuels problèmes de serial. Vérifier ensuite que la délégation mène bien aux serveurs attendus.

### Exercice 4 — DNSSEC et SERVFAIL

**Situation :** la réponse non validée fonctionne, mais les résolveurs validants échouent.

**Correction attendue :** inspecter la chaîne DS/DNSKEY/RRSIG, les signatures et l’heure. Établir le point exact de rupture et réparer la zone ou la délégation. La désactivation globale de la validation n’est pas une solution finale.

### Exercice 5 — Double pile et application lente

**Situation :** le nom se résout, mais l’application met longtemps à se connecter ; IPv4 fonctionne rapidement et IPv6 échoue.

**Correction attendue :** comparer les enregistrements A/AAAA, tester chaque famille explicitement, vérifier le routage et le filtrage IPv6, les Router Advertisements et la MTU. Ne pas attribuer automatiquement la lenteur à DNS : la résolution peut être correcte alors que le chemin IPv6 est défaillant.

### Exercice 6 — DHCP HA et option incohérente

**Situation :** après basculement, les clients reçoivent une adresse valide mais un résolveur différent.

**Correction attendue :** comparer les options et politiques des partenaires, vérifier la réplication et la procédure de reprise, puis tester la cohérence sur un client. Une base de baux synchronisée n’implique pas nécessairement que toute la configuration l’est.


## 15. Quiz de validation

**1. Quelle est la fonction principale de `giaddr` en DHCPv4 relayé ?**  
A. Chiffrer la requête  B. Identifier le contexte de réseau client  C. Définir le TTL DNS  D. Remplacer le masque du client

**2. Pourquoi deux serveurs DHCP ne sont-ils pas automatiquement une paire HA sûre ?**  
A. Parce que DHCP ne peut avoir qu’un serveur  B. Parce que les baux et politiques peuvent diverger  C. Parce que DNS utilise TCP  D. Parce que les clients n’utilisent pas d’IP

**3. Quel résultat indique généralement que le nom demandé n’existe pas ?**  
A. NXDOMAIN  B. REFUSED  C. ACK  D. OFFER

**4. Que signifie un SERVFAIL dans un scénario DNSSEC ?**  
A. Le nom est forcément inexistant  B. Le serveur n’a pas pu produire une réponse valide ; la validation peut être en cause  C. Le client a obtenu un bail  D. Le TTL est toujours nul

**5. Pourquoi TCP/53 doit-il être pris en compte dans une politique DNS ?**  
A. Il ne sert jamais  B. Il est utilisé notamment pour les transferts de zone et certaines réponses  C. Il remplace DHCP  D. Il sert uniquement à IPv6

**6. Un TTL faible garantit-il que tous les clients verront immédiatement une modification ?**  
A. Oui  B. Non, les caches peuvent avoir conservé l’ancien TTL et certaines applications ont leur propre cache  C. Oui, si le ping fonctionne  D. Seulement pour PTR

**7. DNSSEC chiffre-t-il les questions DNS ?**  
A. Oui  B. Non, il permet la validation de l’origine et de l’intégrité des données signées  C. Uniquement en TCP  D. Uniquement sur les zones privées

**8. Que faut-il tester dans un scénario DHCPv6 ?**  
A. Uniquement `giaddr`  B. RA, comportement SLAAC, messages DHCPv6 et distribution DNS  C. Seulement les enregistrements MX  D. Seulement le TTL

**9. Une zone secondaire ne se met plus à jour. Quel contrôle est pertinent ?**  
A. La couleur du VLAN  B. SOA/serial, notifications, connectivité et autorisation de transfert  C. La MAC du clavier  D. Le masque du résolveur

**10. Quel est le meilleur premier principe de dépannage ?**  
A. Redémarrer tous les serveurs  B. Désactiver les protections  C. Définir le périmètre et localiser le premier point de divergence à l’aide de preuves  D. Modifier tous les TTL

### Réponses expliquées

1. **B** — `giaddr` aide le serveur à identifier le sous-réseau d’origine d’une requête relayée.
2. **B** — la cohérence des baux, réservations, options et politiques dépend du mécanisme HA.
3. **A** — NXDOMAIN indique que le nom n’existe pas selon la réponse reçue ; vérifier toutefois la source autoritaire et le cache.
4. **B** — SERVFAIL est générique et peut notamment refléter un échec de validation DNSSEC.
5. **B** — DNS n’est pas exclusivement UDP ; les transferts et certaines réponses utilisent TCP.
6. **B** — le TTL n’invalide pas les caches instantanément et les applications peuvent conserver leurs propres données.
7. **B** — DNSSEC apporte authentification/intégrité, pas confidentialité du transport.
8. **B** — DHCPv6 doit être étudié avec les RA, SLAAC et la façon dont le client apprend ses résolveurs.
9. **B** — la synchronisation d’une zone dépend de plusieurs mécanismes distincts.
10. **C** — une méthode fondée sur les preuves évite les changements risqués et les conclusions hâtives.


## 16. Glossaire opérationnel

- **Bail DHCP :** période durant laquelle une adresse est attribuée à un client.
- **Scope/pool :** ensemble d’adresses et de paramètres disponibles pour un réseau ou une politique.
- **Relais DHCP :** composant qui transmet les messages entre le réseau client et le serveur DHCP.
- **`giaddr` :** champ DHCPv4 contenant l’adresse du relais dans les échanges relayés.
- **Option 82 :** informations de relais, souvent liées au circuit ou à l’identifiant distant.
- **DHCP snooping :** protection de commutateur qui contrôle les messages DHCP selon les ports et la politique.
- **SLAAC :** configuration automatique d’adresse IPv6 basée sur les annonces de routeur.
- **Résolveur récursif :** serveur qui recherche une réponse DNS pour le client et met en cache les résultats.
- **Serveur autoritaire :** serveur qui publie les données officielles d’une zone.
- **Délégation :** transfert de l’autorité DNS d’une partie de l’espace de noms vers d’autres serveurs.
- **SOA/serial :** données de gestion d’une zone, dont un numéro de version utilisé pour suivre les changements.
- **AXFR/IXFR :** mécanismes de transfert complet ou incrémental de zone.
- **TTL :** durée pendant laquelle un enregistrement peut rester en cache.
- **Cache négatif :** conservation temporaire d’une réponse négative telle que NXDOMAIN.
- **DNSSEC :** extensions DNS permettant de valider cryptographiquement l’origine et l’intégrité des données signées.
- **DS/DNSKEY/RRSIG :** types d’enregistrements utilisés dans la chaîne de validation DNSSEC.
- **DoT/DoH :** DNS transporté respectivement via TLS ou HTTPS.
- **Blast radius :** étendue des systèmes ou utilisateurs touchés par une panne ou une erreur.
- **Rollback :** retour contrôlé à une configuration précédente après échec d’un changement.


## 17. Références techniques et méthode de lecture

Les normes et documents ci-dessous servent de points d’entrée. Vérifier les mises à jour, les errata et la documentation du produit avant une modification de production.

- **DHCPv4 :** RFC 2131 — Dynamic Host Configuration Protocol ; RFC 2132 — DHCP Options and BOOTP Vendor Extensions.
- **Option 82 :** RFC 3046 — DHCP Relay Agent Information Option.
- **DHCPv6 :** RFC 8415 — Dynamic Host Configuration Protocol for IPv6.
- **DNS :** RFC 1034 — Concepts and Facilities ; RFC 1035 — Implementation and Specification.
- **DNS négatif :** RFC 2308 — Negative Caching of DNS Queries.
- **Transferts de zone :** RFC 5936 — DNS Zone Transfer Protocol (AXFR) ; RFC 1995 — Incremental Zone Transfer (IXFR).
- **DNSSEC :** RFC 4033, RFC 4034 et RFC 4035 — DNS Security Introduction, Resource Records et Protocol Modifications.
- **DNS over TLS :** RFC 7858 ; **DNS over HTTPS :** RFC 8484.
- **Documentation constructeur :** guides d’administration DHCP/DNS de la plateforme effectivement déployée, y compris les limites de HA, les commandes de diagnostic et les politiques de mise à jour.

### Méthode de lecture des normes

1. lire d’abord le modèle de protocole et les champs concernés ;
2. vérifier ensuite les exigences de sécurité et les comportements d’erreur ;
3. comparer les recommandations à la version logicielle utilisée ;
4. reproduire les scénarios dans un laboratoire ;
5. documenter les différences entre norme, comportement du produit et politique locale.

Une RFC définit le protocole ou un comportement standardisé ; elle ne garantit pas que toutes les plateformes exposent la même interface de configuration, les mêmes commandes ou la même fonction de haute disponibilité.


## Conclusion

À ce niveau, la maîtrise de DHCP et DNS ne consiste plus à mémoriser quelques commandes. Elle consiste à concevoir des services observables, résilients et contrôlables, puis à diagnostiquer les pannes en séparant les rôles, les chemins et les données. Un bail DHCP correct ne garantit pas un DNS correct ; une réponse DNS valide ne garantit pas que le chemin IP fonctionne ; un serveur redondant ne garantit pas que sa configuration est cohérente.

La pratique experte repose sur quatre réflexes : **définir le périmètre, collecter des preuves, tester chaque couche séparément et documenter la correction avec un plan de retour arrière**. Les schémas textuels de ce cours sont volontairement intégrés au Markdown afin de rester lisibles et portables dans ton lecteur.
