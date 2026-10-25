# DHCP & DNS — Niveau Intermédiaire

> **Format des schémas :** diagrammes textuels ASCII/Unicode intégrés directement dans ce fichier. Aucun SVG, PNG, lien d’image ou dossier externe n’est nécessaire.
>
> **Progression :** ce niveau prolonge les bases DHCP/DNS du niveau débutant. Il se concentre sur les échanges multi-VLAN, la résilience, les mises à jour dynamiques, les zones DNS, la sécurité et le dépannage méthodique.

**Domaine :** services réseau et infrastructure IP  
**Niveau :** Intermédiaire  
**Prérequis :** adressage IPv4/IPv6, VLAN, routage de base, cycle DORA, notion de bail DHCP, résolution DNS récursive et autoritaire, enregistrements DNS courants.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois pouvoir :

- concevoir un service DHCP pour plusieurs VLAN et sous-réseaux ;
- expliquer le rôle de `giaddr`, des options DHCP et du relais ;
- analyser un renouvellement, une réaffectation, un conflit ou un épuisement de pool ;
- distinguer une réservation, une exclusion, une option et une politique d’affectation ;
- expliquer les modèles de haute disponibilité DHCP et leurs limites ;
- comprendre DHCPv6 avec état, DHCPv6 sans état et SLAAC ;
- concevoir une architecture de résolveurs DNS récursifs et de serveurs autoritaires ;
- gérer les zones directes et inverses, les délégations, les transferts de zone et les mises à jour dynamiques ;
- diagnostiquer les problèmes de cache, de TTL, de délégation, de DNSSEC et de transport ;
- sécuriser DHCP et DNS sans confondre disponibilité, intégrité et confidentialité ;
- produire un compte rendu de dépannage reproductible.


## 1. Architecture de référence : séparer les rôles

DHCP et DNS sont souvent administrés par la même équipe, parfois hébergés sur les mêmes serveurs, mais leurs rôles protocolaires restent distincts. DHCP fournit une configuration au client. DNS publie ou résout des noms. Une architecture robuste identifie séparément les clients, les relais, les serveurs DHCP, les résolveurs récursifs et les serveurs autoritaires.

### Schéma 1 — Architecture logique multi-VLAN

```text
                 VLAN 10 — Utilisateurs
       +--------------------------------------+
       | PC-A          PC-B          PC-C     |
       +------------------+-------------------+
                          |
                    [Passerelle L3]
                          |
          +---------------+----------------+
          |                                |
   DHCP relay / helper              DNS récursif interne
          |                                |
          v                                v
   +--------------+                +------------------+
   | Serveur DHCP |                | Cache + politiques|
   | Pools/VLAN   |                | DNS des clients   |
   +--------------+                +--------+---------+
                                            |
                                    requêtes autorisées
                                            v
                                  +---------------------+
                                  | DNS autoritaires    |
                                  | zones internes/publiques
                                  +---------------------+
```

Le relais DHCP se trouve généralement sur l’interface de couche 3 qui reçoit les diffusions des clients. Le serveur DHCP peut être dans un autre sous-réseau : le relais transforme la demande locale en requête unicast vers le serveur configuré et ajoute les informations qui permettent d’identifier le réseau du client. Le résolveur DNS, lui, reçoit les requêtes DNS du client et effectue le travail de résolution selon sa configuration.

### Principes d’architecture

1. **Un sous-réseau doit correspondre à une politique DHCP identifiable.** Le serveur doit savoir quel pool et quelles options appliquer.
2. **Les clients utilisent des résolveurs approuvés.** Éviter de distribuer des adresses DNS qui ne sont pas joignables ou qui ne connaissent pas les zones internes requises.
3. **Les zones autoritaires ne sont pas des caches récursifs ouverts.** Un serveur public autoritaire n’a généralement aucune raison d’accepter la récursion pour tout Internet.
4. **Les chemins réseau doivent être vérifiés.** Un service peut fonctionner localement mais échouer à travers une ACL, un pare-feu, un relais ou un NAT.
5. **Les rôles et les journaux doivent être identifiables.** Documenter quel serveur détient les baux, qui répond à la récursion, et quel serveur est maître ou secondaire pour chaque zone.


## 2. DHCPv4 multi-sous-réseaux et relais

### 2.1 Pourquoi la diffusion ne traverse-t-elle pas les routeurs ?

Au démarrage, un client qui n’a pas encore d’adresse IPv4 envoie généralement un DHCPDISCOVER avec une adresse source `0.0.0.0` vers l’adresse de broadcast `255.255.255.255`, en UDP source 68 vers UDP destination 67. Les routeurs ne relaient pas automatiquement cette diffusion au-delà du domaine local. Sans relais, un serveur situé dans un autre sous-réseau peut donc rester invisible au client.

### Schéma 2 — DHCP sans relais et avec relais

```text
SANS RELAIS                         AVEC RELAIS

PC VLAN 10                          PC VLAN 10
   | broadcast                         | broadcast local
   v                                   v
[Switch L2]                       [Passerelle L3]
   X  le routeur ne relaie pas         | relais DHCP configuré
   X  la diffusion IP                  | requête unicast
                                       v
                                  [Serveur DHCP]
                                  choisit le pool VLAN 10
```

Le relais n’est pas un deuxième serveur DHCP et ne distribue pas lui-même le bail. Il transmet la requête au serveur, puis retransmet la réponse vers le client. Selon le constructeur et le protocole, le relais peut être configuré sous des formes telles que `ip helper-address`, mais il faut vérifier les fonctions associées à cette commande sur la plateforme utilisée.

### 2.2 Le champ `giaddr`

Dans DHCPv4, le champ `giaddr` (*gateway IP address*) indique l’adresse du relais utilisée pour aider le serveur à déterminer le sous-réseau d’origine du client. Le serveur utilise généralement cette information pour sélectionner le scope approprié. Le relais peut également transmettre des informations supplémentaires, par exemple au moyen de l’option 82 lorsque cette fonction est activée et prise en charge.

### Schéma 3 — Comment le serveur identifie le bon scope

```text
Client VLAN 20             Relais L3                 Serveur DHCP
192.168.20.0/24                 |                          |
      | DHCPDISCOVER             |                          |
      |------------------------->|                          |
      |                           | giaddr = 192.168.20.1   |
      |                           |------------------------->|
      |                           |                          | sélection du scope
      |                           |                          | 192.168.20.0/24
      |                           |<-------------------------|
      |<--------------------------| réponse relayée          |

Le serveur ne choisit pas le pool uniquement d'après l'adresse IP du serveur.
Il doit identifier le réseau client via les informations du relais.
```

### 2.3 Option 82 : informations de circuit et de distant

L’option 82 (*Relay Agent Information*) permet au relais d’ajouter des informations telles que l’identifiant du circuit et l’identifiant du relais. Elle peut aider à appliquer une politique fondée sur le port d’accès ou le commutateur d’origine, plutôt que sur le seul sous-réseau. Son comportement dépend de la configuration : le relais peut insérer, conserver ou supprimer cette option, et le serveur peut la traiter ou la refuser.

**Attention :** ne suppose pas qu’une option 82 reçue est fiable par nature. Il faut contrôler quels équipements sont autorisés à l’insérer et comment les switches d’accès traitent les informations fournies par un client. Une option 82 mal gérée peut entraîner un refus de bail ou l’application du mauvais scope.

### 2.4 Exemple de configuration conceptuelle Cisco

Exemple illustratif, à adapter au modèle et à la version IOS/IOS XE :

```text
interface Vlan20
 description Passerelle du VLAN 20
 ip address 192.168.20.1 255.255.255.0
 ip helper-address 192.168.100.10
```

Le serveur DHCP doit disposer d’un scope adapté à `192.168.20.0/24`, avec la passerelle `192.168.20.1` et les options DNS correctes. Une commande de relais ne crée pas automatiquement le scope côté serveur.

### 2.5 Contrôles de diagnostic

- Vérifier que l’interface VLAN est `up/up` et que le client est dans le bon VLAN.
- Vérifier la présence du relais sur l’interface qui reçoit les requêtes.
- Vérifier la route entre le relais et le serveur DHCP, dans les deux sens.
- Vérifier UDP 67/68 et les ACL/pare-feu sur le chemin.
- Vérifier que le scope correspondant au réseau relayé existe et dispose d’adresses libres.
- Vérifier les options et les politiques fondées sur l’option 82.
- Capturer les paquets au niveau du client, du relais et du serveur si le symptôme demeure ambigu.


## 3. Cycle DHCP approfondi : états, renouvellement et conflits

Le cycle DORA est un bon modèle de départ, mais il ne couvre pas tous les échanges. Un client qui possède déjà un bail peut tenter de le renouveler sans recommencer systématiquement une découverte complète. Le comportement exact dépend de l’état du client, de la durée du bail et de la réponse du serveur.

### Schéma 4 — DORA et renouvellement d’un bail

```text
NOUVELLE CONFIGURATION
Client                           Serveur DHCP
  |---- DHCPDISCOVER ----------------->|
  |<--- DHCPOFFER ---------------------|
  |---- DHCPREQUEST ------------------>|
  |<--- DHCPACK -----------------------|
  |  adresse + masque + routeur + DNS  |

RENOUVELLEMENT DU BAIL
Client                           Serveur DHCP
  |---- DHCPREQUEST unicast ---------->|  à T1, en général
  |<--- DHCPACK -----------------------|
  |
  | si pas de réponse, nouvelle tentative
  | à T2, le client peut diffuser la demande
  | si le bail expire sans renouvellement : perte du droit d'utiliser l'adresse
```

Dans le modèle classique, T1 est souvent fixé autour de 50 % de la durée du bail et T2 autour de 87,5 %, mais ces valeurs ne doivent pas être considérées comme des constantes universelles dans toutes les implémentations. Les options de bail et le comportement du client peuvent varier.

### 3.1 DHCPREQUEST : plusieurs contextes

Un paquet DHCPREQUEST peut intervenir dans plusieurs situations :

- sélection d’une offre pendant l’acquisition initiale ;
- renouvellement auprès du serveur qui a fourni le bail ;
- rebinding lorsque le client tente de joindre un serveur disponible ;
- vérification ou reprise d’un bail dans certains scénarios.

Il faut interpréter le paquet avec son état, les champs et les options environnantes. Voir uniquement le mot `DHCPREQUEST` dans une capture ne permet pas de conclure à une erreur.

### 3.2 DHCPOFFER sans DHCPACK

Si un serveur propose une adresse mais que le client ne termine pas l’échange, plusieurs causes sont possibles : offre d’un serveur illégitime, réponse perdue, client ayant choisi une autre offre, filtrage réseau, conflit détecté ou incompatibilité de politique. Vérifier si le client envoie un DHCPREQUEST, quel serveur il sélectionne, et si le serveur choisi retourne un DHCPACK ou un DHCPNAK.

### 3.3 DHCPNAK et adresse incorrecte

Un DHCPNAK peut indiquer que le client demande une adresse invalide pour le réseau ou que le serveur estime que la configuration demandée ne peut pas être maintenue. Il ne faut pas le confondre avec un délai d’attente : le NAK est une réponse explicite, alors qu’un silence peut venir d’une perte de paquet, d’un scope indisponible ou d’un serveur absent.

### 3.4 Détection des conflits

Un conflit survient si une adresse est déjà utilisée par un appareil qui n’a pas de bail cohérent avec le serveur, par exemple une adresse statique placée dans le pool dynamique. Les protections varient selon les systèmes : ping de contrôle avant attribution, détection ARP, marquage d’adresse comme conflictuelle ou journalisation. Ces mécanismes ne remplacent pas un plan d’adressage propre.

**Bonne pratique :** exclure les plages d’adresses fixes, documenter les réservations et rechercher l’adresse MAC associée au conflit. Ne pas simplement agrandir le pool : cela peut masquer une duplication plutôt que la résoudre.


## 4. Concevoir les pools, options et réservations

### 4.1 Pool, exclusion et réservation : ne pas les confondre

- **Pool / scope :** réseau et plage à partir desquels le serveur peut attribuer des adresses.
- **Exclusion :** adresse ou plage que le serveur ne doit pas distribuer dynamiquement.
- **Réservation :** association d’un client identifié à une adresse particulière, selon les identifiants reconnus par le serveur.
- **Option :** paramètre remis au client, par exemple passerelle, DNS, domaine de recherche ou serveur NTP.
- **Politique / classe :** règles permettant de choisir une plage ou des options selon le type de client ou d’autres critères.

Une réservation n’est pas forcément une garantie de sécurité. Les critères d’identification et la possibilité d’usurper une identité doivent être considérés. Dans un environnement sensible, compléter DHCP par du contrôle d’accès réseau et des protections de couche 2.

### Schéma 5 — Décision simplifiée d’attribution

```text
              Requête reçue par le serveur
                           |
                           v
                Identifier le réseau client
                 (giaddr / interface / scope)
                           |
                           v
                Appliquer les politiques
                           |
             +-------------+-------------+
             |                           |
     Client réservé ?              Client dynamique
             |                           |
             v                           v
   Vérifier la réservation       Chercher une adresse libre
             |                           |
             +-------------+-------------+
                           |
                           v
                Vérifier exclusions et conflits
                           |
                           v
                 Offre puis attribution
```

### 4.2 Options importantes

| Option DHCPv4 | Usage courant | Point de vigilance |
|---|---|---|
| 1 | Masque de sous-réseau | Doit correspondre au réseau du client |
| 3 | Routeur / passerelle | Ne pas fournir une passerelle non joignable |
| 6 | Serveurs DNS | Vérifier l’accessibilité et la cohérence des zones |
| 15 | Nom de domaine | Ne remplace pas la configuration complète du DNS |
| 42 | Serveurs NTP | Utiliser des sources de temps fiables |
| 51 | Durée du bail | Adapter à la mobilité et au volume d’adresses |
| 58 / 59 | T1 / T2 | Paramètres de renouvellement, si configurés |
| 82 | Informations de relais | Dépend du relais et de la politique serveur |

La disponibilité et l’interprétation des options dépendent du protocole et de l’implémentation. Ne pas recopier des options d’un réseau à l’autre sans vérifier leur utilité.

### 4.3 Dimensionner la durée du bail

Une durée courte libère plus rapidement les adresses d’appareils temporaires, mais augmente la fréquence des renouvellements et la charge de journalisation. Une durée longue réduit les échanges de renouvellement, mais des adresses peuvent rester louées à des clients absents pendant une période prolongée. La bonne valeur dépend du contexte : bureaux fixes, Wi-Fi invité, événements, réseau de laboratoire ou terminaux mobiles.

Pour dimensionner, estimer le nombre de clients simultanés, le taux de rotation, la taille du pool et le délai de récupération souhaité. Surveiller les taux d’utilisation et les refus. La règle pratique est de mesurer le comportement réel plutôt que d’adopter une durée unique pour tous les VLAN.

### 4.4 Symptôme : le pool est épuisé

1. Confirmer que le scope correspond au bon sous-réseau.
2. Examiner les baux actifs et expirés.
3. Rechercher des clients qui renouvellent anormalement souvent.
4. Vérifier si des relais envoient des requêtes avec un mauvais `giaddr`.
5. Vérifier les réservations et exclusions trop larges.
6. Contrôler la durée des baux et la rotation des clients.
7. Étendre le sous-réseau uniquement après vérification du plan IP et du routage.


## 5. Haute disponibilité DHCP

Le service DHCP peut devenir un point de panne si un seul serveur dessert de nombreux VLAN. Plusieurs approches existent : mécanisme de failover natif, paire active/standby, partage de charge ou scopes répartis selon une stratégie coordonnée. Les fonctions exactes dépendent du logiciel serveur ; il ne faut pas supposer que deux serveurs configurés avec des plages similaires se synchronisent automatiquement.

### Schéma 6 — Serveurs DHCP redondants

```text
                         Clients VLAN 10
                               |
                         [Relais L3]
                          /        \
                         /          \
                        v            v
                +-------------+  +-------------+
                | DHCP-A      |  | DHCP-B      |
                | état / baux |<->| état / baux |
                +-------------+  +-------------+
                      \\          //
                       \\________//
                   mécanisme de synchronisation
                   défini par l'implémentation
```

### 5.1 Active/standby et partage de charge

Dans un modèle actif/standby, un serveur principal attribue les baux et un serveur secondaire peut prendre le relais selon le mécanisme de haute disponibilité. Dans un modèle de partage de charge, les serveurs se répartissent les demandes. Dans les deux cas, il faut une coordination du bail et un mécanisme défini pour éviter que les deux serveurs attribuent simultanément la même adresse à des clients différents.

### 5.2 Points à valider avant production

- Le mécanisme réplique-t-il les baux, les réservations et les options ?
- Comment la paire détecte-t-elle la perte de son partenaire ?
- Quel est le comportement pendant une partition réseau entre serveurs ?
- Comment se déroule le retour du serveur après une panne ?
- Les scopes sont-ils cohérents sur les deux membres ?
- Les relais connaissent-ils les deux serveurs ?
- Les journaux et alertes permettent-ils d’identifier les changements de rôle ?
- Une procédure de restauration a-t-elle été testée ?

**Attention :** une configuration avec deux adresses `ip helper-address` améliore potentiellement la joignabilité de deux serveurs, mais ne garantit pas à elle seule la synchronisation des baux ni l’absence de doublons.


## 6. DHCPv6, SLAAC et coexistence IPv4/IPv6

DHCPv6 n’est pas simplement DHCPv4 avec des adresses plus longues. En IPv6, la configuration peut combiner les Router Advertisements (RA), SLAAC et DHCPv6. Le réseau peut utiliser DHCPv6 avec état pour attribuer des adresses, DHCPv6 sans état pour fournir d’autres paramètres, ou SLAAC pour que le client construise lui-même une adresse à partir des informations annoncées par le routeur.

### Schéma 7 — Choix de configuration IPv6

```text
                 Routeur IPv6 envoie un RA
                           |
                           v
                 Le client lit les indicateurs
                           |
             +-------------+-------------+
             |                           |
     SLAAC autorisé ?              DHCPv6 indiqué ?
             |                           |
             v                           v
   Construire l'adresse         Interroger le serveur DHCPv6
   à partir du préfixe          pour adresse et/ou options
             |                           |
             +-------------+-------------+
                           |
                           v
                 Tester DNS et connectivité
```

Les indicateurs du RA, souvent décrits par les bits M et O, orientent le comportement des clients, mais les comportements concrets varient selon le système d’exploitation. Il faut tester les postes réels plutôt que déduire leur comportement uniquement de la configuration du routeur.

### 6.1 DHCPv6 et DNS

DHCPv6 peut fournir des serveurs DNS et une liste de recherche de domaine au moyen d’options spécifiques. En IPv6, les informations de serveur DNS peuvent également être annoncées via les mécanismes RA appropriés, selon les capacités des équipements. La configuration effective d’un client peut donc résulter de plusieurs sources : DHCPv6, RA, configuration manuelle ou politique locale.

### 6.2 Relais DHCPv6

Un relais DHCPv6 reçoit les messages des clients sur le lien local et les transmet au serveur. Les messages et les ports ne sont pas identiques à DHCPv4 : DHCPv6 utilise UDP 546 côté client et UDP 547 côté serveur/relais. Le relais transmet des informations de lien afin que le serveur sélectionne le bon préfixe et la bonne politique.

### 6.3 Vérifications IPv6

- Le client reçoit-il un RA et un préfixe cohérent ?
- La route par défaut IPv6 est-elle présente ?
- Le comportement SLAAC/DHCPv6 correspond-il aux indicateurs RA ?
- Le relais DHCPv6 pointe-t-il vers le bon serveur ?
- Le pare-feu autorise-t-il les échanges nécessaires ?
- Les serveurs DNS fournis sont-ils joignables en IPv6 ou accessibles via une route valide ?
- Le nom se résout-il en AAAA, et le service cible accepte-t-il réellement IPv6 ?


## 7. DNS : récursion, autorité et délégation

DNS est un système hiérarchique distribué. Le résolveur récursif travaille pour le client : il utilise son cache et interroge d’autres serveurs si nécessaire. Le serveur autoritaire fournit les données officielles pour une zone qu’il héberge. Ces fonctions peuvent être exécutées sur des serveurs distincts ou, dans certains environnements, sur un même logiciel, mais elles doivent être séparées par configuration et politique de sécurité.

### Schéma 8 — Résolution récursive typique

```text
Client                 Résolveur récursif           Hiérarchie DNS
  |                            |                           |
  |-- A portail.exemple.test ->|                           |
  |                            |-- demande racine ------->|
  |                            |<-- référence TLD --------|
  |                            |-- demande TLD ---------->
  |                            |<-- référence autoritaire-|
  |                            |-- demande autoritaire -->|
  |                            |<-- réponse A ------------|
  |<-- adresse IP -------------|                           |

Si la réponse est encore valide dans le cache, les étapes externes peuvent être évitées.
```

### 7.1 Itératif contre récursif

Dans une résolution récursive, le client demande au résolveur de lui rapporter la réponse finale ou une erreur. Le résolveur peut ensuite réaliser des requêtes itératives vers les serveurs de la hiérarchie : chaque serveur lui indique les informations disponibles ou la prochaine délégation à suivre. Les serveurs racine ne détiennent pas les adresses de tous les hôtes ; ils orientent vers les serveurs des domaines de premier niveau.

### 7.2 Zones, domaines et délégations

Un nom DNS fait partie d’un espace de noms hiérarchique. Une zone est une portion de cet espace administrée comme un ensemble de données autoritaires. Une zone peut contenir des sous-domaines sans que chacun soit nécessairement une zone distincte. Lorsqu’une sous-zone est déléguée, les enregistrements NS dans la zone parente orientent les résolveurs vers les serveurs de la zone enfant. Des enregistrements de glue peuvent être nécessaires pour éviter une dépendance circulaire lorsqu’un serveur de noms se trouve lui-même dans le domaine délégué.

### Schéma 9 — Délégation d’une sous-zone

```text
                  Zone parente : exemple.test
                 +-----------------------------+
                 | NS : ns1.exemple.test       |
                 | délégation : ventes         |
                 +--------------+--------------+
                                |
                       enregistrements NS
                                |
                                v
                 Zone enfant : ventes.exemple.test
                 +-----------------------------+
                 | NS : ns1.ventes.exemple.test|
                 | A : portail -> 192.0.2.80   |
                 +-----------------------------+

La zone parente délègue l'autorité ; elle ne doit pas nécessairement
contenir tous les enregistrements de la zone enfant.
```

### 7.3 Enregistrements et leur usage

| Type | Fonction | Remarque d’exploitation |
|---|---|---|
| A | Nom vers adresse IPv4 | Vérifier la cohérence avec l’adresse réelle du service |
| AAAA | Nom vers adresse IPv6 | Un AAAA incorrect peut provoquer des échecs propres à IPv6 |
| CNAME | Alias vers un autre nom | Le nom aliasé ne doit pas recevoir certains autres types de données au même nom |
| MX | Serveurs de messagerie | La cible est un nom d’hôte, pas directement une adresse IP |
| NS | Serveurs autoritaires d’une zone | Contrôler les délégations côté parent et les données côté enfant |
| SOA | Paramètres de la zone | Serial, timers et serveur principal selon le modèle de zone |
| PTR | Adresse vers nom, en zone inverse | La zone inverse est administrée séparément de la zone directe |
| TXT | Données textuelles diverses | Utilisé notamment pour des politiques de messagerie et de validation |
| SRV | Service, protocole, port et cible | Le client doit savoir interroger ce type d’enregistrement |
| CAA | Autorités de certification autorisées | La prise en compte dépend du processus de délivrance du certificat |

### 7.4 Zones inverses

La résolution inverse utilise des noms sous `in-addr.arpa` pour IPv4 et `ip6.arpa` pour IPv6. Le fait qu’un enregistrement A existe ne crée pas automatiquement un PTR. La zone inverse peut être administrée par une équipe ou un fournisseur différent, particulièrement pour des adresses publiques. Un PTR absent peut affecter certains outils de diagnostic ou contrôles applicatifs, mais ne signifie pas automatiquement que la résolution directe est cassée.


## 8. Cache DNS, TTL et erreurs difficiles à interpréter

Le cache DNS réduit la latence et la charge des serveurs autoritaires. Une réponse mise en cache reste réutilisable pendant une durée déterminée par le TTL. Le TTL n’est pas un ordre de pousser une mise à jour aux clients ; il indique combien de temps la donnée peut être conservée avant de devoir être redemandée. Les caches négatifs peuvent aussi mémoriser l’absence d’un nom ou d’un type d’enregistrement, selon les règles DNS applicables.

### Schéma 10 — Effet du TTL après une modification

```text
Temps T0                 Temps T1                  Temps T2
   |                        |                         |
   v                        v                         v
Réponse ancienne       Admin change A            TTL expiré
TTL = 3600 s           192.0.2.10 -> .20          résolveur redemande
   |                        |                         |
   +---- cache peut continuer à répondre .10 --------+
                            |
                            +-- nouveaux clients sans cache
                                peuvent déjà obtenir .20

La propagation apparente dépend des caches et du TTL restant,
pas d'une diffusion instantanée de la nouvelle donnée.
```

### 8.1 Pourquoi deux postes obtiennent-ils des réponses différentes ?

Causes possibles : résolveurs différents, caches avec des TTL restants différents, vue DNS interne/externe, réponse négative encore en cache, réplication ou transfert de zone en retard, ou enregistrement modifié sur un serveur qui n’est pas celui interrogé. Il faut identifier le résolveur effectivement utilisé par chaque poste et interroger les serveurs autoritaires pour comparer les données.

### 8.2 NXDOMAIN et NODATA

- **NXDOMAIN :** le nom demandé n’existe pas selon la réponse DNS.
- **NODATA :** le nom peut exister, mais le type d’enregistrement demandé n’est pas présent dans la réponse.
- **SERVFAIL :** le serveur n’a pas pu produire une réponse valide ; la cause peut être une panne amont, un problème DNSSEC ou une erreur de configuration.
- **REFUSED :** le serveur refuse de traiter la requête selon sa politique.
- **Timeout :** aucune réponse n’a été reçue à temps ; cela peut venir du transport, d’un filtrage ou d’un serveur indisponible.

Ne pas confondre ces symptômes. Un `SERVFAIL` n’est pas une preuve que le nom n’existe pas ; un timeout ne prouve pas que l’enregistrement est absent.

### 8.3 UDP et TCP pour DNS

DNS utilise souvent UDP pour les requêtes ordinaires, mais TCP est également nécessaire, notamment pour certaines réponses volumineuses et les transferts de zone. Un pare-feu qui autorise UDP/53 mais bloque TCP/53 peut provoquer des pannes intermittentes, des échecs DNSSEC ou des transferts de zone impossibles. DNS over TLS et DNS over HTTPS utilisent d’autres transports et ports ; leur disponibilité dépend de l’architecture choisie.


## 9. Zones primaires/secondaires, transferts et mises à jour dynamiques

Une zone autoritaire peut être répliquée depuis un serveur principal vers un ou plusieurs serveurs secondaires. Les transferts AXFR transmettent une zone complète ; IXFR permet, lorsqu’il est pris en charge et possible, de transférer les changements incrémentaux. Les secondaires vérifient les paramètres de zone, notamment le serial SOA, et suivent les timers définis par le modèle d’exploitation.

### Schéma 11 — Réplication d’une zone DNS

```text
                 Administrateur / système de mise à jour
                                |
                                v
                       +------------------+
                       | DNS primaire     |
                       | zone + serial    |
                       +--------+---------+
                                |
                      NOTIFY / vérification SOA
                                |
                                v
                       +------------------+
                       | DNS secondaire   |
                       | copie autoritaire|
                       +------------------+
                                |
                       réponses aux clients

Les transferts doivent être autorisés seulement aux secondaires approuvés.
```

### 9.1 Contrôles de transfert de zone

- Déclarer explicitement les secondaires autorisés.
- Limiter AXFR/IXFR aux adresses ou mécanismes d’authentification approuvés.
- Vérifier que le serial SOA progresse correctement après une modification.
- Contrôler les journaux et l’état de synchronisation sur les deux serveurs.
- Vérifier TCP/53 entre les serveurs, ainsi que les ACL.
- Tester les réponses de chaque serveur autoritaire, pas uniquement celles du résolveur.

Un transfert de zone ouvert peut révéler l’inventaire des noms internes ou publics. Les données DNS sont souvent consultables par conception, mais il faut tout de même limiter l’exposition inutile des zones et des noms sensibles.

### 9.2 Mises à jour DNS dynamiques depuis DHCP

Dans un environnement intégré, le serveur DHCP peut enregistrer ou mettre à jour des enregistrements A/PTR à la place du client, ou collaborer avec le client selon le modèle d’identité et les mécanismes de sécurité. La politique doit définir qui crée, actualise et supprime les enregistrements. Il faut aussi gérer les clients qui changent de bail, les noms dupliqués, les machines hors ligne et les enregistrements devenus obsolètes.

### Schéma 12 — Cycle simplifié DHCP et DNS dynamique

```text
Client                Serveur DHCP             DNS autoritaire
  |                         |                         |
  |-- demande de bail ----->|                         |
  |<-- configuration -------|                         |
  |                         |-- mise à jour A/PTR --->|
  |                         |<-- résultat ------------|
  |                         |                         |
  | départ / bail expiré    | politique de nettoyage |
  |------------------------>|-- suppression/MAJ ----->|

La création et le nettoyage doivent être gouvernés par une politique claire.
```

### 9.3 Enregistrements obsolètes et noms réutilisés

Un enregistrement A peut rester après qu’un appareil a quitté le réseau. Un autre appareil peut ensuite recevoir la même adresse, tandis que le DNS conserve encore l’ancien nom. Les causes sont notamment une mise à jour dynamique qui échoue, une politique de nettoyage désactivée, un client qui conserve un nom ancien ou une identité qui n’est pas unique.

Pour dépanner, comparer le bail actuel, l’adresse MAC/identité du client, les journaux DHCP, les données A/PTR et la date de mise à jour. Ne supprimer pas en masse des enregistrements sans vérifier s’ils sont statiques ou utilisés par des applications.


## 10. Sécurité DHCP et DNS

La sécurité se conçoit par couches. DHCP ne fournit pas, à lui seul, une identité cryptographiquement fiable dans tous les environnements. DNS traditionnel n’offre pas automatiquement l’authenticité cryptographique des données. DNSSEC permet de valider l’origine et l’intégrité des données signées, mais ne chiffre pas le contenu des requêtes et n’empêche pas tous les dénis de service.

### 10.1 DHCP snooping

Le DHCP snooping, sur les commutateurs qui le prennent en charge, distingue généralement les ports de confiance des ports non fiables. Les réponses serveur provenant d’un port non fiable peuvent être bloquées. Une table de bindings peut ensuite être utilisée par d’autres fonctions de sécurité, selon la plateforme.

### Schéma 13 — Principe de DHCP snooping

```text
                 Serveur DHCP légitime
                          |
                   port TRUSTED
                          |
                    +-----------+
                    | Switch L2 |
                    +-----------+
                     /         \
          ports UNTRUSTED   port UNTRUSTED
                 |               |
             Poste client    Serveur pirate
                                 X
                    réponses DHCP bloquées
                    si la politique est correctement appliquée
```

La configuration de confiance doit être limitée aux ports qui mènent réellement à un serveur ou à un relais légitime. Déclarer tous les ports comme trusted annule l’essentiel de la protection. Après activation, vérifier les bindings, les compteurs de drops et les impacts sur les téléphones IP, points d’accès et autres appareils qui utilisent DHCP.

### 10.2 Protections DNS

- **Récursion limitée :** ne pas exploiter un résolveur ouvert à tout Internet sans raison et sans contrôles.
- **ACL et segmentation :** autoriser les clients prévus à utiliser le résolveur interne.
- **DNSSEC :** valider les données signées quand l’architecture le permet ; diagnostiquer soigneusement les erreurs de signature.
- **Transferts de zone contrôlés :** limiter AXFR/IXFR aux secondaires approuvés.
- **Mises à jour dynamiques sécurisées :** utiliser les mécanismes d’authentification disponibles plutôt que des mises à jour anonymes.
- **Journalisation et supervision :** surveiller les taux d’échec, les réponses `SERVFAIL`, les volumes inhabituels et les changements de zone.
- **Confidentialité :** envisager DoT/DoH sur les segments et clients appropriés, tout en gardant une politique cohérente avec le filtrage, la supervision et la résolution des noms internes.

### 10.3 DNSSEC : ce que cela fait et ne fait pas

DNSSEC permet au résolveur validant de vérifier les signatures et la chaîne de confiance des données DNS signées. Il peut aider à détecter des données modifiées ou non authentiques. Il ne chiffre pas les noms recherchés, ne garantit pas qu’un service est sûr et ne remplace pas TLS. Une erreur de signature, un DS parent incohérent ou une horloge très incorrecte peut conduire un résolveur validant à retourner `SERVFAIL` alors qu’un résolveur non validant semble répondre.


## 11. Méthode de dépannage intégrée

Le dépannage efficace suit le chemin réel du paquet et sépare les hypothèses. Commencer par définir le symptôme exact : aucun bail, mauvaise passerelle, DNS inaccessible, nom non résolu, réponse différente selon le client ou lenteur intermittente.

### Schéma 14 — Arbre de diagnostic DHCP

```text
Client sans adresse attendue
            |
            v
Le lien/VLAN est-il correct ? ---- non ---> corriger accès/VLAN
            |
           oui
            v
Le client émet-il DISCOVER ? ----- non ---> vérifier client / capture
            |
           oui
            v
Le relais reçoit-il la requête ? - non ---> VLAN / relais / L2
            |
           oui
            v
Le serveur reçoit-il la requête ? - non --> route / ACL / UDP 67-68
            |
           oui
            v
Scope et adresse disponibles ? --- non ---> scope / pool / politique
            |
           oui
            v
Offer, Request, ACK visibles ? ---- non ---> analyser l'étape manquante
```

### Schéma 15 — Arbre de diagnostic DNS

```text
Nom inaccessible
      |
      v
Le client utilise-t-il le bon résolveur ? -- non --> DHCP / config locale
      |
     oui
      v
Le résolveur répond-il ? -------------------- non --> route / ACL / service
      |
     oui
      v
Réponse DNS : laquelle ?
      |
      +-- NXDOMAIN --> nom / zone / cache négatif
      +-- SERVFAIL --> amont / DNSSEC / délégation
      +-- REFUSED  --> ACL / politique de récursion
      +-- timeout  --> transport / pare-feu / surcharge
      +-- mauvaise IP --> cache / vue DNS / enregistrement / TTL
```

### 11.1 Commandes utiles côté client

**Windows :**

```powershell
ipconfig /all
ipconfig /release
ipconfig /renew
ipconfig /flushdns
nslookup portail.exemple.test
nslookup -type=SOA exemple.test
nslookup -type=NS exemple.test
```

`ipconfig /release` et `/renew` modifient le bail du client ; les utiliser avec prudence sur une session distante. `ipconfig /flushdns` vide le cache du résolveur local Windows, mais ne vide pas les caches des serveurs DNS intermédiaires.

**Linux :** les commandes disponibles dépendent de la distribution et du gestionnaire réseau. Exemples courants :

```bash
ip address
ip route
resolvectl status
resolvectl query portail.exemple.test
dig portail.exemple.test A
dig @192.168.100.53 portail.exemple.test A
dig +trace portail.exemple.test
dig exemple.test SOA
dig exemple.test NS
```

`dig +trace` suit la délégation depuis la racine et peut être bloqué si la machine ne peut pas interroger directement les serveurs nécessaires. Une requête directe vers un serveur autoritaire permet de comparer la donnée autoritaire avec la réponse du résolveur.

### 11.2 Captures Wireshark

Pour DHCPv4, utiliser le filtre d’affichage `dhcp` ou, selon la version de Wireshark, `bootp`. Observer les identifiants de transaction, les adresses source/destination, `giaddr`, les options et la séquence des messages. Pour DHCPv6, filtrer `dhcpv6`. Pour DNS, filtrer `dns` puis examiner le type demandé, l’identifiant de transaction, le code de réponse, le TTL et les drapeaux de récursion/autorité.

Une capture sur un seul point peut ne pas montrer où le paquet a été perdu. Quand c’est possible, comparer une capture côté client et côté serveur, ou relever les compteurs d’interface et de pare-feu sur le chemin.

### 11.3 Tableau symptômes → pistes

| Symptôme | Pistes prioritaires | Vérification discriminante |
|---|---|---|
| Client reçoit `169.254.x.x` en IPv4 | Aucun bail DHCP abouti | Capture DORA et état du scope |
| Certains VLAN seulement échouent | Relais ou scope | `giaddr`, helper, pool du sous-réseau |
| Mauvaise passerelle reçue | Option 3 ou mauvais scope | Comparer les options de l’ACK |
| Bail obtenu, noms internes KO | DNS distribué ou zone interne | `ipconfig /all`, requête au résolveur interne |
| DNS lent au premier accès | Cache froid, timeout amont | Mesurer chaque serveur et observer les délais |
| Un poste a une ancienne IP DNS | Cache intermédiaire, TTL, vues | Interroger résolveur puis autoritaire |
| `SERVFAIL` seulement sur un validateur | DNSSEC ou chaîne de délégation | Journaux du validateur, DS/DNSKEY/signatures |
| Secondaire DNS ancien | Transfert, SOA serial, TCP/53 | Comparer SOA sur primaire et secondaire |
| PTR incorrect mais A correct | Zone inverse distincte | Interroger le PTR et vérifier l’autorité inverse |


## 12. Laboratoire guidé : trois VLAN, deux serveurs DNS

### Topologie

```text
                 +-------------------------+
                 | Routeur / switch L3     |
                 | VLAN 10: 192.168.10.1   |
                 | VLAN 20: 192.168.20.1   |
                 | VLAN 30: 192.168.30.1   |
                 +-----------+-------------+
                             |
                 relais vers 192.168.100.10
                             |
                 +-----------v-------------+
                 | Serveur DHCP            |
                 | scopes 10 / 20 / 30     |
                 +-------------------------+

Clients VLAN 10 : utilisateurs
Clients VLAN 20 : téléphones / équipements
Clients VLAN 30 : Wi-Fi invité
DNS interne : 192.168.100.53
DNS invité : résolveur séparé selon politique
```

### Plan d’adressage proposé

| VLAN | Sous-réseau | Passerelle | Pool dynamique | DNS annoncé |
|---|---|---|---|---|
| 10 | `192.168.10.0/24` | `192.168.10.1` | `.50–.220` | `192.168.100.53` |
| 20 | `192.168.20.0/24` | `192.168.20.1` | `.50–.220` | `192.168.100.53` |
| 30 | `192.168.30.0/24` | `192.168.30.1` | `.50–.240` | résolveur invité dédié |

Ce plan est fictif et suppose que les routes et politiques de sécurité autorisent les communications nécessaires. Ne distribue pas le DNS interne aux invités si cela leur donne accès à des noms ou services qui doivent rester privés.

### Étapes du laboratoire

1. Créer les trois VLAN et les interfaces de passerelle.
2. Configurer le relais DHCP sur chaque interface L3 concernée.
3. Créer un scope par sous-réseau sur le serveur DHCP.
4. Définir les exclusions, la durée de bail et les options.
5. Connecter un client par VLAN et vérifier l’ACK reçu.
6. Vérifier la passerelle et les serveurs DNS réellement installés sur chaque client.
7. Tester la résolution d’un nom interne et d’un nom externe autorisé.
8. Simuler une panne du serveur DHCP principal si un mécanisme de haute disponibilité est disponible.
9. Modifier un enregistrement DNS de laboratoire et observer l’effet du TTL.
10. Consigner les commandes, résultats et écarts observés.

### Critères de réussite

- Chaque client reçoit une adresse dans le bon sous-réseau.
- La passerelle et les options DNS correspondent au VLAN.
- Aucun pool ne distribue les adresses réservées.
- Les clients invités ne peuvent pas interroger les zones internes non autorisées.
- Les serveurs DNS autoritaires et récursifs sont identifiés clairement.
- Les journaux DHCP et DNS permettent de retracer un bail et une requête.
- Une panne simulée déclenche le comportement attendu, sans attribution de doublons.


## 13. Études de cas corrigées

### Cas 1 — Le VLAN 20 ne reçoit aucun bail

**Contexte :** le VLAN 10 fonctionne. Le serveur DHCP est accessible depuis le routeur. Les clients du VLAN 20 n’obtiennent qu’une adresse automatique locale.

**Démarche :** vérifier d’abord le VLAN et l’état de l’interface L3, puis le relais sur l’interface du VLAN 20. Dans la capture côté serveur, vérifier si `giaddr` correspond à `192.168.20.1`. Si la requête arrive mais qu’aucune offre ne sort, vérifier le scope et la politique serveur. Si l’offre sort mais n’arrive pas au client, comparer la capture côté serveur et côté client.

**Conclusion :** ne pas ajouter un deuxième serveur au hasard. Identifier l’étape exacte qui manque dans la séquence.

### Cas 2 — Le bail est correct mais le nom interne ne se résout pas

**Contexte :** le client possède une adresse, un masque et une passerelle corrects. Le nom `git.intra.exemple.test` échoue, mais un site public se résout.

**Démarche :** vérifier le serveur DNS annoncé par DHCP, puis envoyer une requête explicitement au résolveur interne. Interroger ensuite le serveur autoritaire pour la zone interne. Contrôler si le client utilise un VPN, un DNS chiffré ou une politique locale qui remplace le résolveur annoncé.

**Conclusion :** le problème est probablement lié à la vue DNS interne, à la distribution du résolveur ou à la route/ACL vers celui-ci, pas nécessairement au bail DHCP lui-même.

### Cas 3 — Un enregistrement modifié semble ne pas changer

**Contexte :** l’administrateur change un A de `192.0.2.10` vers `192.0.2.20`. Certains clients reçoivent encore l’ancienne adresse.

**Démarche :** interroger le serveur autoritaire directement, puis le résolveur utilisé par le client. Comparer les TTL restants. Vérifier que la modification a été faite sur la bonne zone et que le secondaire a reçu le nouveau serial. Vider le cache local seulement après avoir établi où se trouve la donnée ancienne.

**Conclusion :** la mise à jour autoritaire, le transfert de zone et le cache client sont trois étapes distinctes.

### Cas 4 — Le DNS renvoie `SERVFAIL` après l’activation de DNSSEC

**Contexte :** le nom répondait avant l’activation de la signature. Un résolveur validant échoue, tandis qu’un résolveur non validant semble fonctionner.

**Démarche :** vérifier la signature et sa période de validité, les DNSKEY, le DS publié chez le parent, la chaîne de délégation et l’heure système. Examiner les journaux du validateur et tester les serveurs autoritaires. Ne pas désactiver globalement la validation sans comprendre la cause.

**Conclusion :** une erreur DNSSEC peut produire un `SERVFAIL` même si les enregistrements existent.

### Cas 5 — Un serveur secondaire DNS ne se met plus à jour

**Contexte :** le primaire contient la nouvelle donnée, mais le secondaire continue de fournir l’ancienne.

**Démarche :** comparer le SOA serial, vérifier la notification, le rafraîchissement et le transport TCP/53, puis contrôler les autorisations de transfert et les journaux. Vérifier que le secondaire est autoritaire pour la zone attendue et qu’il ne sert pas une copie obsolète d’une autre zone.

**Conclusion :** le fait que le primaire soit à jour ne garantit pas que tous les secondaires le soient immédiatement.


## 14. Quiz de validation

Réponds avant de lire le corrigé.

1. Pourquoi un relais DHCP est-il nécessaire lorsque le serveur se trouve dans un autre sous-réseau ?
2. À quoi sert `giaddr` ?
3. Une configuration avec deux `ip helper-address` garantit-elle la synchronisation des baux ?
4. Quelle différence existe entre une exclusion et une réservation DHCP ?
5. Pourquoi un client peut-il recevoir une adresse IPv6 via SLAAC sans utiliser DHCPv6 pour l’adresse ?
6. Quelle différence fonctionnelle sépare un résolveur récursif d’un serveur autoritaire ?
7. Pourquoi un changement DNS n’est-il pas visible immédiatement chez tous les clients ?
8. Que signifie `NXDOMAIN` et en quoi diffère-t-il de `SERVFAIL` ?
9. À quoi servent les enregistrements NS de délégation ?
10. Pourquoi faut-il autoriser et contrôler TCP/53 entre serveurs DNS ?
11. DNSSEC chiffre-t-il les requêtes DNS ?
12. Quel est le rôle de DHCP snooping sur un switch compatible ?
13. Pourquoi un enregistrement A peut-il être correct alors que le PTR est absent ou faux ?
14. Quelles observations permettent de distinguer un problème de relais d’un problème de scope DHCP ?
15. Pourquoi faut-il comparer la réponse du résolveur à celle du serveur autoritaire ?

### Corrigé

1. Parce que la diffusion locale initiale n’est généralement pas routée ; le relais la transmet au serveur.
2. Il fournit l’adresse du relais qui aide le serveur à identifier le réseau client et le scope.
3. Non. La synchronisation des baux dépend d’un mécanisme de haute disponibilité pris en charge et configuré.
4. L’exclusion empêche une attribution dynamique ; la réservation associe une identité client à une adresse particulière.
5. SLAAC permet au client de construire une adresse à partir du préfixe annoncé par le routeur, selon la configuration et le comportement du client.
6. Le résolveur cherche une réponse pour le client ; le serveur autoritaire publie les données officielles d’une zone.
7. Les caches conservent les réponses jusqu’à expiration du TTL ; plusieurs résolveurs peuvent avoir des TTL restants différents.
8. NXDOMAIN indique que le nom n’existe pas selon la réponse ; SERVFAIL indique que le serveur n’a pas pu produire une réponse valide.
9. Ils orientent les résolveurs vers les serveurs autoritaires de la zone déléguée.
10. Les transferts de zone utilisent TCP ; bloquer TCP/53 peut empêcher la réplication ou certains échanges DNS.
11. Non. DNSSEC authentifie et protège l’intégrité des données signées, mais n’assure pas leur confidentialité.
12. Il peut bloquer des réponses DHCP serveur sur des ports non fiables et soutenir des fonctions de sécurité associées.
13. Les zones directes et inverses sont distinctes et peuvent être administrées par des entités différentes.
14. La capture côté relais/serveur, la valeur de `giaddr`, les compteurs, les journaux et la présence du scope permettent de localiser l’étape fautive.
15. Pour distinguer une donnée autoritaire incorrecte d’une réponse ancienne ou d’un problème de cache/résolveur.


## 15. Checklist opérationnelle

### DHCP

- [ ] Chaque VLAN possède un scope clairement documenté.
- [ ] Le relais est configuré sur l’interface L3 appropriée.
- [ ] `giaddr` et, si utilisé, l’option 82 correspondent à la politique prévue.
- [ ] Les exclusions et réservations sont documentées et sans conflit.
- [ ] Les options passerelle, DNS et domaine sont cohérentes.
- [ ] La durée du bail est adaptée à la mobilité et au volume de clients.
- [ ] La capacité du pool et le nombre de baux libres sont supervisés.
- [ ] Le comportement de haute disponibilité a été testé.
- [ ] DHCP snooping et les ports trusted/untrusted sont validés sur les switches concernés.

### DNS

- [ ] Les résolveurs clients et les serveurs autoritaires sont identifiés.
- [ ] La récursion est limitée aux clients autorisés.
- [ ] Les délégations NS et les éventuels glue records sont cohérents.
- [ ] Les zones primaires/secondaires ont un serial SOA cohérent.
- [ ] Les transferts sont limités aux secondaires autorisés.
- [ ] Les TTL sont adaptés au rythme des changements.
- [ ] Les mises à jour dynamiques et le nettoyage des enregistrements sont documentés.
- [ ] La validation DNSSEC est surveillée si elle est activée.
- [ ] UDP et TCP/53 sont autorisés selon les flux nécessaires.
- [ ] Les réponses A/AAAA et PTR sont vérifiées séparément.

### Dépannage

- [ ] Le symptôme est formulé précisément et avec une heure.
- [ ] Le réseau/VLAN et les routes sont vérifiés avant de conclure à une panne applicative.
- [ ] Les requêtes et réponses ont été observées sur un point pertinent du chemin.
- [ ] Les journaux DHCP/DNS sont comparés aux captures.
- [ ] Les changements réalisés pendant le diagnostic sont consignés.
- [ ] Le résultat final est vérifié depuis le client et le serveur concernés.


## 16. Glossaire essentiel

- **Bail DHCP :** période pendant laquelle le client peut utiliser une adresse attribuée.
- **Scope / pool :** plage d’adresses et paramètres associés à un réseau client.
- **Relais DHCP :** agent qui transmet les requêtes entre le lien client et le serveur.
- **`giaddr` :** champ DHCPv4 portant l’adresse du relais.
- **Option 82 :** informations ajoutées par un agent relais, selon la configuration.
- **SLAAC :** autoconfiguration d’adresse IPv6 à partir des annonces de routeur.
- **Résolveur récursif :** serveur qui effectue les recherches DNS pour le compte du client.
- **Serveur autoritaire :** serveur qui fournit les données officielles d’une zone.
- **Zone DNS :** portion de l’espace de noms administrée comme ensemble autoritaire.
- **Délégation :** transfert d’autorité DNS d’une zone parente vers une zone enfant.
- **TTL :** durée maximale de conservation d’une donnée DNS en cache.
- **NXDOMAIN :** réponse indiquant que le nom n’existe pas selon la zone interrogée.
- **SERVFAIL :** réponse indiquant que le serveur n’a pas pu fournir de réponse valide.
- **AXFR / IXFR :** transfert complet / incrémental d’une zone DNS.
- **DNSSEC :** extensions DNS de signature et de validation cryptographiques des données.
- **DHCP snooping :** fonction de commutation qui limite les réponses DHCP provenant de ports non fiables.


## 17. Références techniques à consulter

Les normes et fonctions peuvent évoluer ; consulter les versions applicables aux équipements du laboratoire.

- RFC 2131 — Dynamic Host Configuration Protocol (DHCPv4) : https://www.rfc-editor.org/rfc/rfc2131
- RFC 2132 — DHCP Options and BOOTP Vendor Extensions : https://www.rfc-editor.org/rfc/rfc2132
- RFC 3046 — DHCP Relay Agent Information Option : https://www.rfc-editor.org/rfc/rfc3046
- RFC 8415 — DHCP for IPv6 : https://www.rfc-editor.org/rfc/rfc8415
- RFC 4861 — Neighbor Discovery for IPv6 : https://www.rfc-editor.org/rfc/rfc4861
- RFC 1034 — Domain Names: Concepts and Facilities : https://www.rfc-editor.org/rfc/rfc1034
- RFC 1035 — Domain Names: Implementation and Specification : https://www.rfc-editor.org/rfc/rfc1035
- RFC 5936 — DNS Zone Transfer Protocol (AXFR) : https://www.rfc-editor.org/rfc/rfc5936
- RFC 4033, RFC 4034 et RFC 4035 — DNS Security Extensions (DNSSEC) : https://www.rfc-editor.org/rfc/rfc4033
- Documentation Cisco — DHCP configuration and relay features : https://www.cisco.com/

> **Règle de travail :** un dépannage n’est terminé que lorsque le symptôme initial est reproduit, la cause est étayée par des observations, la correction est appliquée et le test final confirme le retour au comportement attendu.
