# DHCP & DNS — Niveau Débutant

> **Format des schémas :** diagrammes textuels ASCII intégrés directement dans le Markdown. Aucun fichier image ou dossier externe n’est requis.

> **Parcours :** Réseaux informatiques → Services d’infrastructure  
> **Niveau :** Débutant  
> **Prérequis :** notions d’adresse IPv4, masque, passerelle, VLAN et fonctionnement général d’un réseau IP.  
> **Objectif final :** expliquer, configurer, vérifier et dépanner un service DHCP et une résolution DNS dans un petit réseau d’entreprise.

## Comment utiliser ce cours

Ce chapitre est conçu pour être étudié dans l’ordre. Les premières sections expliquent le besoin auquel répond chaque service ; les sections suivantes suivent les paquets sur le réseau, présentent la configuration et finissent par le dépannage. Il est normal de ne pas mémoriser toutes les options dès la première lecture. L’objectif initial est de comprendre les échanges et d’être capable d’isoler une panne méthodiquement.

Les adresses utilisées dans les exemples sont réservées à un laboratoire fictif. Il faut les remplacer par le plan IP réel avant toute mise en production. Les commandes Cisco sont données à titre pédagogique : leur disponibilité et leur syntaxe exacte peuvent varier selon la plateforme, la famille IOS/IOS XE et la version.

## Objectifs d’apprentissage

À la fin du cours, tu dois pouvoir :

- expliquer pourquoi un poste a besoin d’une adresse IP, d’un masque, d’une passerelle et de serveurs DNS ;
- décrire le cycle DHCPv4 Discover, Offer, Request, ACK et le renouvellement d’un bail ;
- concevoir un scope DHCP sans distribuer une adresse déjà réservée ;
- expliquer le rôle d’un relais DHCP quand le client et le serveur sont dans des sous-réseaux différents ;
- distinguer un serveur DNS récursif d’un serveur autoritaire ;
- lire les enregistrements A, AAAA, CNAME, MX, NS, SOA, PTR, TXT et SRV ;
- comprendre le cache, le TTL, NXDOMAIN et les retards de mise à jour perçus ;
- utiliser les commandes usuelles de Windows, Linux et Cisco pour vérifier DHCP et DNS ;
- appliquer des protections de base contre les serveurs DHCP illégitimes et les réponses DNS indésirables ;
- documenter un dépannage avec des faits observables plutôt qu’avec des suppositions.

## 1. Pourquoi DHCP et DNS sont indispensables

Dans un réseau IP, un poste doit disposer d’une configuration cohérente avant de pouvoir communiquer au-delà de son lien local. La configuration comprend habituellement une adresse, un préfixe ou masque, une passerelle par défaut, au moins un résolveur DNS et parfois d’autres paramètres : domaine de recherche, serveur NTP, serveur de démarrage réseau ou paramètres propres à une application.

Il est possible de configurer tous ces éléments manuellement sur chaque appareil. Cette approche reste utile pour des équipements à adresse stable, mais devient pénible dès que plusieurs dizaines ou milliers de postes sont concernés. Une modification de passerelle ou de serveur DNS devrait alors être répétée partout ; une seule faute de frappe peut isoler un appareil. **DHCP** distribue automatiquement des paramètres IP selon une politique centrale. **DNS** permet aux applications d’utiliser des noms plutôt que de retenir des adresses numériques.

Ces services sont complémentaires, mais ils ne réalisent pas le même travail. DHCP peut donner au poste l’adresse du résolveur DNS, mais il ne résout pas lui-même `intranet.exemple.test`. DNS peut renvoyer une adresse IP pour ce nom, mais il ne fournit pas nécessairement au poste sa propre adresse ni sa passerelle.

**Schéma 1 — Les deux services et le poste client**

```text
+----------------+       DHCP: config IP       +----------------+
| Serveur DHCP   | --------------------------> | Poste client   |
| Bail, options  | <-------------------------- | IP / GW / DNS  |
+----------------+                             +-------+--------+
                                                        |
                                                        | requete DNS
                                                        v
                                               +----------------+
                                               | Resolveur DNS  |
                                               | Cache + reponse|
                                               +-------+--------+
                                                       |
                                               adresse IP retour
```

### Exemple concret

Imaginons un ordinateur connecté au VLAN 10. Il doit recevoir l’adresse `192.168.10.50/24`, utiliser `192.168.10.1` comme passerelle et interroger le résolveur `192.168.100.53`. DHCP fournit cette configuration. Quand l’utilisateur saisit `portail.exemple.test`, le système demande ensuite à DNS quelle adresse correspond à ce nom. Si le poste reçoit une adresse correcte mais que le serveur DNS est mal configuré ou injoignable, une application peut échouer par son nom tout en restant accessible par son adresse IP.

Ce contraste est un outil de diagnostic important : **connectivité IP** et **résolution de noms** sont deux étapes séparées. Une panne de l’une ne prouve pas automatiquement une panne de l’autre.

## 2. Préparer un plan d’adressage exploitable

Avant de configurer DHCP, il faut connaître le sous-réseau de chaque VLAN, la passerelle, les plages réservées, les équipements à IP fixe et le volume attendu de clients. Un scope correspond à une plage d’adresses et aux paramètres que le serveur applique à un réseau logique. Le serveur ne doit pas distribuer l’adresse de la passerelle, les adresses des serveurs fixes ni les adresses retenues pour les imprimantes ou les équipements d’infrastructure.

Pour ce laboratoire, nous utilisons les paramètres suivants :

| Élément | Valeur du laboratoire | Raison |
|---|---|---|
| VLAN utilisateurs | VLAN 10 | Réseau d’accès des postes |
| Sous-réseau | `192.168.10.0/24` | 254 adresses hôtes théoriques |
| Passerelle | `192.168.10.1` | Interface L3 du VLAN |
| Adresses réservées / fixes | `192.168.10.1–49` | Passerelle, serveurs et périphériques documentés |
| Pool dynamique | `192.168.10.50–220` | Adresses distribuées aux clients |
| Réserve non distribuée | `192.168.10.221–254` | Extension, tests ou affectations futures |
| DNS interne | `192.168.100.53` | Résolveur d’entreprise, joignable depuis ce VLAN |
| Domaine de recherche | `exemple.test` | Nom réservé à un environnement de test |

Le masque `/24` correspond à `255.255.255.0`. Le réseau est `192.168.10.0`, l’adresse de broadcast IPv4 est `192.168.10.255` et les adresses hôtes généralement utilisables vont de `.1` à `.254`. La capacité théorique n’est pas égale au nombre d’adresses du pool dynamique : la plage proposée dans ce laboratoire en contient 171, de `.50` à `.220` inclus.

**Schéma 2 — Un scope organisé en exclusions, pool et réserve**

```text
Exemple de sous-reseau : 192.168.10.0/24

.1        .10                 .200      .220       .254
 |---------|===================|----------|----------|
 Passerelle   Pool distribue       Reserve   Equipements fixes
              par DHCP             DHCP

Exclusions conseillees : .1-.19 et .201-.254
Pool dynamique         : .20-.200
Reservation            : IP liee a une MAC/identite precise
Attention : une exclusion ne cree pas une reservation.
```

### Les erreurs de planification les plus courantes

- **Pool trop petit :** les adresses sont toutes louées, même si le réseau semble calme. Vérifier le nombre de baux actifs, leur durée et le nombre de clients qui se connectent brièvement.
- **Adresse statique dans le pool :** un serveur configuré manuellement peut partager une adresse avec un poste qui l’a reçue par DHCP. Utiliser des exclusions, des réservations ou une plage distincte documentée.
- **Mauvais masque :** un poste peut considérer un destinataire comme local alors qu’il doit passer par la passerelle, ou l’inverse.
- **Passerelle erronée :** le client reçoit une adresse et peut parler à des voisins du VLAN, mais pas atteindre les autres sous-réseaux.
- **Mauvais DNS :** les applications échouent sur les noms alors que les pings vers certaines adresses fonctionnent.
- **Scopes qui se chevauchent :** deux configurations incohérentes peuvent proposer la même adresse ou des paramètres contradictoires.

L’adresse du serveur DHCP lui-même est normalement configurée de façon stable ou réservée dans le réseau d’administration. Le service doit être protégé contre une panne et contre toute distribution non autorisée.

## 3. DHCPv4 : rôle et vocabulaire

DHCP signifie **Dynamic Host Configuration Protocol**. Il suit un modèle client-serveur. Le client demande une configuration ; le serveur gère les adresses et fournit des paramètres. Une *lease* (bail) indique pendant combien de temps le client peut utiliser l’adresse attribuée. Le bail n’est donc pas une affectation permanente, même si, selon la politique, il peut être renouvelé souvent ou être très long.

DHCPv4 repose sur UDP, habituellement le port 67 côté serveur et le port 68 côté client. Un client qui ne possède pas encore d’adresse IPv4 peut envoyer une requête broadcast sur son réseau local. Les broadcasts IP ne sont normalement pas routés d’un sous-réseau vers un autre ; ce point explique pourquoi on configure un **relais DHCP** lorsque le serveur est distant.

Le serveur peut gérer trois usages historiques définis dans la spécification DHCP :

- **Allocation dynamique :** une adresse est louée pour une durée limitée puis rendue disponible selon les règles de bail ; c’est le cas courant des postes utilisateurs.
- **Allocation automatique :** le serveur choisit une adresse selon sa politique et peut conserver durablement l’association.
- **Allocation manuelle :** l’administrateur choisit l’adresse et le serveur la transmet au client. Une réservation par identifiant client est souvent utilisée dans les environnements pratiques.

Une réservation n’est pas la même chose qu’une configuration statique faite directement sur le poste. Dans un cas, l’adresse est toujours administrée par DHCP ; dans l’autre, le poste utilise sa propre configuration et l’administrateur doit garantir qu’elle ne sera pas louée à quelqu’un d’autre.

## 4. Le cycle DORA : découvrir, proposer, demander, confirmer

Lorsqu’un client n’a pas de bail utilisable, le scénario classique de DHCPv4 est appelé **DORA** : Discover, Offer, Request, Acknowledge. Il s’agit d’une représentation pédagogique des échanges typiques. Les détails exacts d’adresse source, destination et diffusion dépendent de l’état du client et des champs du message, mais la séquence demeure une excellente première grille de lecture.

**Schéma 3 — Le cycle DORA de DHCPv4**

```text
CLIENT                                      SERVEUR DHCP
  |                                               |
  |---- DHCPDISCOVER (broadcast) ---------------->|
  |<--- DHCPOFFER (proposition d'adresse) --------|
  |---- DHCPREQUEST (choix de l'offre) ---------->|
  |<--- DHCPACK (bail confirme) ------------------|
  |                                               |
  +-- Le client configure IP, masque, passerelle,
      DNS et duree du bail selon les options.

Si le serveur refuse la demande : DHCPNAK.
Si le client abandonne une adresse : DHCPDECLINE.
```

### Étape 1 : DHCPDISCOVER

Le client ne connaît pas encore le serveur disponible. Il envoie un message DHCPDISCOVER pour trouver des serveurs. Au démarrage, le client peut ne pas posséder d’adresse IPv4 ; il utilise donc une communication locale adaptée à cet état. Les champs du message permettent au serveur de relier la réponse à la transaction en cours.

### Étape 2 : DHCPOFFER

Un serveur répond en proposant une adresse et des paramètres, selon le pool disponible et les règles de sélection. Plusieurs serveurs peuvent parfois proposer une offre. Le client ne doit pas considérer une simple offre comme la confirmation finale de son adresse.

### Étape 3 : DHCPREQUEST

Le client indique l’offre qu’il souhaite accepter. Ce message joue aussi d’autres rôles dans le protocole, notamment lors du renouvellement ou de la vérification d’un bail existant. Les serveurs qui ne sont pas sélectionnés peuvent utiliser cette information pour libérer leurs propositions.

### Étape 4 : DHCPACK

Le serveur confirme l’affectation et transmet la configuration retenue. Le client installe alors l’adresse et les options dans sa pile réseau, puis vérifie que l’adresse peut être utilisée selon le comportement prévu par son système. Si la demande ne peut pas être acceptée, le serveur peut répondre par DHCPNAK dans les situations prévues.

### Quels champs retenir en premier ?

Pour débuter, quatre éléments sont particulièrement utiles à reconnaître dans une capture : le type de message DHCP, l’identifiant de transaction, l’adresse proposée et l’identifiant du serveur. En diagnostic, noter seulement « j’ai vu du DHCP » ne suffit pas. Il faut savoir si la capture montre un DISCOVER sans réponse, des OFFER qui ne sont pas suivis d’un REQUEST, ou un ACK reçu par le serveur mais pas par le client.

## 5. Bail, renouvellement et expiration

Un bail DHCP a un cycle de vie. Un client qui dispose encore d’une adresse valide tente habituellement de la renouveler avant l’expiration. Les temporisations par défaut souvent rencontrées pour DHCPv4 sont T1 autour de 50 % du bail et T2 autour de 87,5 %, mais des valeurs peuvent être données explicitement par le serveur. Il ne faut donc pas calculer systématiquement toutes les échéances sans lire les options reçues.

- **T1 — renouvellement :** le client essaie généralement de renouveler le bail auprès du serveur qui l’a accordé, souvent en envoyant une requête unicast s’il connaît sa destination.
- **T2 — rebinding :** si la première tentative n’a pas abouti, le client élargit ses chances et peut envoyer une requête broadcast pour que tout serveur approprié puisse répondre.
- **Expiration :** si le client ne parvient pas à obtenir de prolongation à temps, il ne doit plus continuer à utiliser une adresse dont le bail est arrivé à échéance.

**Schéma 4 — Cycle de vie et renouvellement du bail**

```text
Debut du bail                                     Expiration
   |                                                   |
   v                                                   v
   +-------------------- duree du bail ----------------+
   |                                                   |
   | T1 (souvent 50 %)                                 |
   | Client tente un renouvellement unicast            |
   |---------------------> serveur initial             |
   |                                                   |
   | T2 (souvent 87,5 %)                               |
   | Si echec, demande en broadcast (rebinding)        |
   |---------------------> serveurs disponibles        |
   |                                                   |
   +---- ACK : nouveau bail       Aucun bail : fin ----+
Les valeurs T1/T2 par defaut peuvent varier selon la configuration.
```

### Pourquoi des postes perdent-ils leur adresse après un certain temps ?

Si un PC fonctionne un jour puis perd la connectivité après plusieurs heures ou jours, le bail et les échanges de renouvellement deviennent des pistes sérieuses. Une panne peut venir du serveur, du relais, du VLAN, d’une ACL, d’un routeur qui ne peut plus joindre le serveur, d’un pool épuisé ou d’une réponse qui ne revient plus. Comparer l’heure d’incident avec la durée de bail, l’état du scope et les journaux permet de tester l’hypothèse au lieu de supposer qu’elle est vraie.

Un redémarrage peut masquer temporairement le problème en relançant une transaction initiale ; il ne répare pas nécessairement la cause. Dans un diagnostic rigoureux, collecter d’abord les informations utiles : adresse actuelle, masque, passerelle, serveurs DNS, durée restante, serveur ayant fourni le bail et résultats des captures réseau.

## 6. Options DHCP courantes

L’adresse ne représente qu’une partie de la configuration. Les options DHCP permettent de transmettre au client des paramètres additionnels définis par le protocole ou par des extensions documentées. Voici les options fréquemment rencontrées dans un réseau IPv4 :

| Option | Signification générale | Utilisation |
|---:|---|---|
| 1 | Masque de sous-réseau | Déterminer le préfixe local IPv4 |
| 3 | Routeur | Passerelle par défaut |
| 6 | Serveurs DNS | Résolution de noms |
| 15 | Nom de domaine | Suffixe de domaine pour certains clients |
| 51 | Durée du bail | Temps d’utilisation de l’adresse |
| 54 | Identifiant du serveur DHCP | Identifier le serveur sélectionné |
| 58 / 59 | T1 / T2 | Temporisations de renouvellement, si fournies |
| 66 / 67 | Serveur / nom de fichier de démarrage | Certains scénarios PXE, selon la plateforme |
| 119 | Liste de recherche de domaine | Suffixes de recherche DNS sur les clients compatibles |

Cette liste n’est pas exhaustive. Les clients ne prennent pas tous en charge les mêmes options et n’interprètent pas toutes les options de façon identique. Par exemple, des options de démarrage réseau peuvent dépendre d’un environnement PXE précis. L’administrateur doit vérifier la documentation du système client et du serveur DHCP avant de les ajouter à grande échelle.

**Schéma 5 — L’adresse est accompagnée d’options**

```text
Une offre DHCP ne contient pas uniquement l'adresse IP.

+----------------------+--------------------------------+
| Option               | Exemple                        |
+----------------------+--------------------------------+
| 1 - Masque            | 255.255.255.0                  |
| 3 - Routeur           | 192.168.10.1                   |
| 6 - Serveurs DNS      | 192.168.10.10, 192.168.10.11   |
| 15 - Nom de domaine   | entreprise.example             |
|  lease time           | 8 heures (exemple)              |
+----------------------+--------------------------------+
Client : IP + masque + passerelle + DNS + autres options autorisees.
```

### Bonnes pratiques pour les options

1. **Fournir une passerelle réellement joignable.** Une option Routeur correcte sur le papier mais qui pointe vers une mauvaise interface ne permet pas la connectivité inter-réseaux.
2. **Utiliser des résolveurs adaptés au contexte.** Les postes internes doivent pouvoir résoudre les noms privés requis ; un DNS public ne connaît pas automatiquement les zones internes.
3. **Éviter les listes inutiles.** Trop de suffixes de recherche peut multiplier les requêtes et compliquer le dépannage. Un suffixe doit avoir un usage clair.
4. **Conserver un inventaire des options spéciales.** Noter l’application qui les exige, la portée de l’option, les types de clients et la procédure de test.
5. **Tester la modification sur un scope pilote.** Vérifier les options réellement reçues par un client, et pas uniquement la configuration affichée côté serveur.

## 7. Configurer un serveur DHCP : logique de travail

La configuration exacte dépend de la solution : serveur Windows, serveur Linux (par exemple Kea), équipement spécialisé ou routeur Cisco compatible. Avant de choisir les commandes, définir la politique à appliquer : plage, exclusions, durée du bail, options, réservation, journalisation, redondance et protection contre les réponses illégitimes.

Sur un serveur DHCP, il faut distinguer la configuration de **scope** de la configuration globale. Les paramètres globaux peuvent s’appliquer à plusieurs réseaux ; les paramètres de scope décrivent un sous-réseau précis. Une option locale peut parfois remplacer une option globale. Vérifier l’ordre de priorité retenu par le produit utilisé.

### Exemple pédagogique Cisco IOS/IOS XE

Le fragment ci-dessous illustre le principe d’un pool sur un routeur Cisco prenant en charge le rôle de serveur DHCPv4. Il n’est pas présenté comme une recette universelle. Le rôle serveur doit être autorisé par la politique de l’organisation et la syntaxe doit être vérifiée sur l’équipement réel.

```text
ip dhcp excluded-address 192.168.10.1 192.168.10.49
ip dhcp pool USERS-VLAN10
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 192.168.100.53
 domain-name exemple.test
 lease 7
```

Ce fragment exclut les premières adresses, puis crée un pool correspondant au réseau `192.168.10.0/24`. Il distribue une passerelle, un résolveur DNS, un domaine et une durée de bail. La commande `lease 7` est un exemple de durée exprimée en jours sur de nombreuses versions IOS ; vérifier la grammaire précise prise en charge. Le pool pourrait distribuer toutes les adresses restantes du sous-réseau qui ne sont pas exclues : si la réserve `.221–.254` doit rester non attribuée, il faut une stratégie qui l’exclut aussi ou une plage de pool explicitement limitée, selon les possibilités du logiciel. Cette nuance est essentielle : **une intention écrite dans la documentation ne constitue pas une exclusion effective dans la configuration**.

### Variante : une réservation

Selon la plateforme, une affectation liée à une identité client peut être configurée en définissant un pool dédié avec l’adresse hôte et l’identifiant client attendu. Les formats d’identifiants varient ; ne pas copier une MAC depuis un exemple sans tenir compte du format de client-id que le serveur voit réellement. Tester ensuite que le bon client obtient la réservation et qu’un autre client ne reçoit pas la même adresse.

### Commandes de vérification Cisco

```text
show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
show running-config | section dhcp
```

Selon le logiciel, la disponibilité et la présentation de ces commandes varient. Elles servent typiquement à contrôler l’état des pools, les baux, les conflits et la configuration. Ne pas effacer des bindings ou des conflits à l’aveugle : recueillir les informations avant toute action susceptible de faire perdre l’historique utile.

## 8. Relais DHCP : servir plusieurs VLAN

Une requête DHCP initiale se présente typiquement comme un broadcast local. Les routeurs ne transmettent pas par défaut ce broadcast vers les autres réseaux. Le relais DHCP reçoit la requête sur l’interface du client, puis la relaie vers l’adresse du serveur désigné. Le serveur doit disposer d’un moyen fiable d’identifier le sous-réseau d’origine afin de choisir le scope adapté.

Dans le cas IPv4 classique, le champ `giaddr` joue un rôle dans cette identification ; un relais peut également transmettre des informations de relais, selon l’équipement et les options activées. Le serveur doit avoir une route de retour vers le relais et les politiques de sécurité doivent autoriser les échanges nécessaires. Il est fréquent d’oublier le retour routé : la requête arrive au serveur, mais la réponse ne revient pas jusqu’au client.

**Schéma 6 — Relais entre VLAN et serveur central**

```text
VLAN 10                                      VLAN serveurs
Client DHCP                                  Serveur DHCP
192.168.10.0/24                              10.0.0.20
     |                                            ^
     | Discover (broadcast local)                 | unicast
     v                                            |
+-------------------+   relai DHCP / giaddr   +---+------------+
| Routeur / SVI     | ----------------------> | Reseau IP      |
| interface VLAN 10 |                          | intermediaire  |
+-------------------+                          +----------------+
     |
     +-- configure : ip helper-address 10.0.0.20
Le broadcast ne traverse pas le routeur sans fonction de relais.
```

### Exemple Cisco d’un relais

Supposons que l’interface VLAN du routeur fasse office de passerelle pour `192.168.10.0/24` et que le serveur soit `192.168.100.10`. Sur une plateforme qui utilise cette syntaxe, l’idée générale est :

```text
interface Vlan10
 description Passerelle des postes
 ip address 192.168.10.1 255.255.255.0
 ip helper-address 192.168.100.10
```

`ip helper-address` représente un relais de certains types de broadcasts UDP vers une destination configurée ; sur Cisco, il est souvent utilisé pour DHCP, mais il ne faut pas supposer qu’il ne relaie rien d’autre sans vérifier les options de la plateforme. La commande est placée sur l’interface L3 recevant les broadcasts du client, pas simplement sur l’interface du serveur distant. Sur des switches L3, cette interface peut être une SVI.

### Liste de vérification du relais

- L’interface VLAN est-elle active et possède-t-elle la bonne adresse de passerelle ?
- Le relais vise-t-il le bon serveur, sur le bon chemin IP ?
- Le serveur possède-t-il un scope pour le sous-réseau client ?
- Le serveur peut-il joindre l’adresse de relais / le client selon le fonctionnement attendu ?
- Les ACL ou pare-feu autorisent-ils DHCP et les réponses, ainsi que les métadonnées de relais attendues ?
- Existe-t-il plusieurs relais ou serveurs, et comment leurs réponses sont-elles sélectionnées ?
- Les paquets atteignent-ils le serveur puis reviennent-ils ? Une capture aux deux extrémités peut le démontrer.

Un relais mal configuré peut envoyer les requêtes au bon serveur tout en faisant sélectionner le mauvais scope si l’interface d’origine, les informations de relais ou les pools sont incohérents.

## 9. Réservations, exclusions, conflit et épuisement

Une adresse peut être indisponible parce qu’elle est en bail actif, qu’elle est exclue ou réservée, qu’un conflit a été détecté ou que le pool ne dispose plus d’une adresse répondant aux critères. Il faut distinguer ces situations avant de modifier le scope.

### Exclusions

Une exclusion retire une ou plusieurs adresses de l’allocation dynamique. Elle est utile pour les passerelles, interfaces de routeur, imprimantes configurées manuellement ou autres équipements dont l’adresse n’est pas gérée dynamiquement. Documenter l’exclusion avec le nom de l’équipement et son propriétaire évite qu’une future personne supprime la plage sans comprendre sa raison.

### Réservation

Une réservation associe une identité de client à une adresse déterminée. L’identité peut être une adresse matérielle, un client identifier ou un identifiant défini par le produit. Ce n’est pas toujours strictement la seule adresse MAC qui est utilisée : les environnements modernes peuvent transmettre un identifiant différent ou stable selon le système.

### Détection de conflit

Certains serveurs peuvent tester une adresse avant son attribution et marquer les adresses qui semblent déjà utilisées. Un conflit peut provenir d’une IP statique oubliée dans le pool, d’un poste mal configuré, d’un relais ou d’un serveur illégitime. Ne pas réutiliser une adresse suspecte uniquement parce qu’elle apparaît disponible après une purge ; comprendre la source du conflit et vérifier sur le réseau.

### Épuisement du pool

Mesurer l’utilisation du scope, le nombre de baux actifs, les taux de nouveaux clients, la durée de bail et l’évolution des appareils invités. Une durée trop longue peut maintenir des baux obsolètes ; une durée trop courte peut augmenter le nombre de renouvellements et charger les services. Il n’existe pas une durée parfaite pour tous les réseaux. Le réglage doit être adapté au type de clients, à la mobilité, à la disponibilité des serveurs et aux objectifs opérationnels.

## 10. Introduction à DHCPv6, SLAAC et Router Advertisements

IPv6 ne réutilise pas exactement le cycle DHCPv4. Les hôtes IPv6 découvrent notamment leurs routeurs et préfixes grâce à Neighbor Discovery et aux **Router Advertisements (RA)**. L’autoconfiguration sans état, dite SLAAC, permet à un hôte de construire sa propre adresse à partir du préfixe annoncé et d’un identifiant d’interface généré selon les mécanismes de son système. DHCPv6 peut fournir des adresses et/ou d’autres paramètres, et peut fonctionner en complément de SLAAC.

Une nuance fondamentale : dans le fonctionnement IPv6 courant, **la route par défaut est apprise par les RA**, et non par DHCPv6 comme en DHCPv4. DHCPv6 n’est donc pas le remplacement direct de toutes les fonctions des RA. Il faut comprendre les drapeaux et options RA, les politiques du client et le service DHCPv6 choisi.

**Schéma 7 — Interaction entre RA et DHCPv6**

```text
Routeur IPv6                         Client IPv6
    |                                    |
    |---- Router Advertisement (RA) ---->|
    |     Prefixe + flags M/O             |
    |                                    |
    |  M=0, O=0 : SLAAC seul              | fabrique son adresse
    |  M=0, O=1 : SLAAC + infos DHCPv6    | DNS/autres infos
    |  M=1      : adresse via DHCPv6      | adresse + options
    |                                    |
    |<--- DHCPv6 sollicitation* ----------|
*Les echanges DHCPv6 exacts dependent des flags et du mode choisi.
Le RA reste important pour la passerelle par defaut IPv6.
```

### DHCPv6 avec état et sans état

- **Avec état :** le serveur DHCPv6 attribue une adresse ou un préfixe et maintient une association de bail, suivant le type de ressource demandé.
- **Sans état :** les clients peuvent utiliser SLAAC pour l’adresse, tout en demandant à DHCPv6 des paramètres complémentaires, selon la politique annoncée et la compatibilité des hôtes.
- **Combinaison :** SLAAC et DHCPv6 ne s’excluent pas ; la conception doit être testée sur les systèmes réellement utilisés.

Les clients DHCPv6 utilisent les ports UDP 546 et les serveurs les ports UDP 547. Le relais DHCPv6 a ses propres comportements, différents dans le détail du relais DHCPv4. Il ne faut pas transposer mécaniquement `ip helper-address` à toutes les conceptions IPv6 ; appliquer la configuration correspondant à la plateforme, aux VLAN et au service.

### Quelles questions poser avant le déploiement IPv6 ?

1. Les postes doivent-ils fabriquer leurs adresses par SLAAC, recevoir des adresses avec état, ou utiliser une combinaison ?
2. Comment les RA sont-ils protégés sur les ports d’accès ?
3. Quels serveurs DNS sont annoncés aux clients, et par quel mécanisme ?
4. Le plan de préfixes est-il documenté ?
5. La supervision reconnaît-elle les baux DHCPv6 et les adresses temporaires, qui peuvent compliquer la correspondance entre identités et adresses ?
6. Les règles de pare-feu et de journalisation autorisent-elles les messages IPv6 nécessaires sans ouvrir inutilement d’autres services ?

## 11. DNS : nommer les ressources réseau

Le **Domain Name System (DNS)** est une base de données distribuée, organisée de façon hiérarchique. Il permet de lier des noms à des informations comme des adresses IP, des serveurs de messagerie, des serveurs DNS autoritaires et des paramètres de service. DNS n’est pas un simple répertoire central unique : sa structure permet à différents opérateurs et organisations de gérer séparément des zones tout en conservant un système de noms mondialement cohérent.

Le nom `www.exemple.test.` se lit de droite à gauche dans la hiérarchie : le point final représente la racine, `test` est le domaine de premier niveau dans cet exemple de laboratoire, `exemple` appartient à ce domaine, et `www` est un nom sous cette zone. Le point final rend le nom absolu (FQDN) ; les interfaces utilisateur l’omettent souvent.

**Schéma 8 — Hiérarchie de la racine vers les zones autoritaires**

```text
                 +------------------+
                 | Serveurs racine  |  .
                 +---------+--------+
                           |
             delegation vers le TLD
                           v
                 +------------------+
                 | Serveurs .com    |  TLD
                 +---------+--------+
                           |
             delegation vers la zone
                           v
                 +------------------+
                 | ns1.example.com  |  autorite
                 +---------+--------+
                           |
                enregistrements de zone
                           v
                 www.example.com -> 203.0.113.20
La racine ne connait pas chaque hote : elle oriente vers le TLD.
```

### Le résolveur récursif et le serveur autoritaire

Le **résolveur récursif** reçoit une question du client et essaie d’obtenir une réponse complète. Il peut utiliser sa mémoire cache ; sinon, il interroge les serveurs nécessaires à la résolution. Le **serveur autoritaire** répond pour une zone dont il détient les données configurées (ou hébergées à travers un système d’autorité équivalent). Il ne faut pas confondre ces rôles, même si certains logiciels ou infrastructures hébergent les deux fonctions.

Le client final est souvent appelé *stub resolver* : il demande au résolveur les informations nécessaires sans parcourir lui-même toute la hiérarchie DNS. Dans une entreprise, le poste utilise habituellement un résolveur interne qui sait répondre aux noms privés et effectuer, selon la politique, des requêtes vers d’autres serveurs. Le résolveur peut également appliquer des contrôles, des politiques de filtrage et de la journalisation.

**Schéma 9 — Parcours typique d’une résolution récursive**

```text
Application       Resolveur         Racine       TLD       Autorite
    |                  |                |          |           |
    |-- A www.ex. ---->|                |          |           |
    |                  |-- qui . ? ---->|          |           |
    |                  |<-- referral ---|          |           |
    |                  |---- qui ex. ------------->|           |
    |                  |<--- referral -------------|           |
    |                  |---------------- qui www.ex. --------->|
    |                  |<--------------- A = 203.0.113.20 -----|
    |<-- reponse ------|                |          |           |
Le resolveur recursif effectue les recherches; le client lui pose une question.
```

### Pourquoi le cache DNS est-il important ?

Le cache permet de réutiliser une réponse pendant une durée déterminée par le TTL (*Time To Live*). Lorsque le client demande de nouveau le même nom et le même type d’enregistrement, le résolveur peut répondre immédiatement à partir du cache, si l’entrée est encore valable et si la politique le permet. Cela diminue les délais et le volume de requêtes vers les serveurs autoritaires.

Le cache explique aussi pourquoi une modification DNS ne paraît pas toujours immédiate. Si un enregistrement avait un TTL de 3 600 secondes, un résolveur qui venait de le mettre en cache peut conserver l’ancienne valeur jusqu’à expiration. Une modification côté autoritaire ne pousse pas automatiquement la nouvelle valeur vers tous les caches du monde. Les clients ont également parfois leur propre cache et certaines applications conservent leur résultat plus longtemps selon leur logique.

Le TTL n’est pas un temps de propagation garanti ; c’est la durée de validité mise en cache d’un résultat. Pour planifier une migration, réduire le TTL suffisamment tôt peut limiter le délai des caches, mais réduire le TTL juste avant le changement n’annule pas les copies déjà mises en cache sous l’ancienne durée.

**Schéma 10 — Cache DNS et TTL**

```text
Premiere requete
Client ---> Resolveur ---> autorite : A = 203.0.113.20, TTL=300 s
                  |
                  +-- stocke la reponse avec un TTL initial de 300 s

Quelques secondes plus tard
Client ---> Resolveur : reponse du cache, TTL restant par ex. 245 s

Quand le TTL atteint zero
Resolveur : entree expiree -> nouvelle resolution si necessaire

Le TTL limite la duree du cache; ce n'est pas un chronometre de panne.
Un changement autoritaire n'efface pas instantanement les caches existants.
```

## 12. Types d’enregistrements DNS à reconnaître

Les données DNS sont organisées en enregistrements, souvent appelés *resource records* (RR). Chaque enregistrement a un propriétaire (nom), un type, une classe, une durée de vie et une donnée spécifique au type.

| Type | Signification | Exemple de rôle |
|---|---|---|
| A | Adresse IPv4 | `web.exemple.test` → `192.0.2.20` |
| AAAA | Adresse IPv6 | `web.exemple.test` → `2001:db8:100::20` |
| CNAME | Nom canonique / alias | `www` pointe vers `web` |
| MX | Échangeur de courrier | Indique un ou plusieurs hôtes de réception des mails |
| NS | Serveur de noms | Identifie l’autorité DNS d’une zone ou délégation |
| SOA | Start of Authority | Paramètres de la zone, numéro de série, temporisations, contact administratif sous forme DNS |
| PTR | Pointeur de nom inverse | Relie une adresse à un nom dans la zone inverse correspondante |
| TXT | Données textuelles | Utilisées notamment par certaines politiques de messagerie et validations de domaine |
| SRV | Localisation d’un service | Décrit cible, port, priorité et poids selon l’application |
| CAA | Autorisation d’autorités de certification | Exprime des politiques liées à l’émission de certificats |

**Schéma 11 — Les types d’enregistrements et leur usage**

```text
+------+----------------------+--------------------------------+
| Type | Signification         | Exemple                        |
+------+----------------------+--------------------------------+
| A    | Nom -> IPv4           | www -> 203.0.113.20            |
| AAAA | Nom -> IPv6           | www -> 2001:db8::20             |
| CNAME| Alias                 | app -> service.example.        |
| MX   | Serveur mail          | 10 mail.example.               |
| NS   | Serveurs de la zone   | ns1.example.                   |
| SOA  | Parametres de zone    | serial, timers, contact        |
| PTR  | IP -> nom             | reverse lookup                 |
| TXT  | Texte / validation   | SPF ou verification de domaine |
+------+----------------------+--------------------------------+
Un CNAME ne doit pas coexister avec d'autres donnees ordinaires au meme nom.
```

### A et AAAA ne sont pas la même chose qu’un CNAME

Un enregistrement A associe directement un nom à une adresse IPv4 ; un AAAA associe un nom à une adresse IPv6. Un CNAME est un alias qui indique le nom canonique à utiliser. Il n’est pas simplement une deuxième adresse, et les règles DNS encadrent son usage au sommet d’une zone et avec d’autres types d’enregistrements. Si une recherche pour `www.exemple.test` renvoie un CNAME vers `app.exemple.test`, le résolveur doit poursuivre la résolution du nom cible pour obtenir une adresse utilisable.

### DNS inverse

Le DNS inverse utilise des zones spécialement organisées pour rechercher un nom à partir d’une adresse. Pour IPv4, l’espace est représenté sous `in-addr.arpa`; pour IPv6, sous `ip6.arpa`. Le PTR est utile pour certains journaux, contrôles et applications, mais **un PTR ne prouve pas à lui seul qu’un hôte est digne de confiance**. Une résolution directe et inverse peuvent être indépendantes et ne sont pas automatiquement synchronisées, sauf mécanisme d’administration conçu à cet effet.

### SOA, NS et délégation

La zone autoritaire comprend typiquement un SOA et des enregistrements NS qui déclarent ses serveurs de noms. Un parent délègue un sous-domaine en publiant les informations nécessaires pour trouver son autorité. Un transfert de zone entre serveur primaire et secondaires, lorsqu’il est utilisé, est un mécanisme distinct de la résolution normale des noms. La sécurité et l’autorisation des transferts doivent être configurées explicitement.

## 13. Résolution DNS étape par étape

Quand un utilisateur lance une application qui doit contacter `portail.exemple.test`, la bibliothèque de résolution du poste vérifie d’abord ses mécanismes locaux : cache, fichier hosts et configuration du résolveur, selon le système et l’application. Si une question DNS est nécessaire, elle est envoyée au résolveur configuré. Celui-ci vérifie son cache ; s’il ne possède pas de réponse utilisable, il résout le nom à travers la hiérarchie ou via les serveurs configurés pour ce domaine.

**Schéma 12 — Résolution DNS récursive, cache et autorité**

```text
+--------+       requete       +-------------------+
| Client | ------------------> | Resolveur recursif|
+--------+ <------------------ +---------+---------+
           reponse                       |
                                         | cache valide ?
                                   +-----+------+
                                   | oui       | non
                                   v           v
                              repondre   Racine -> TLD -> Autorite
                                              |
                                              v
                                        stocker selon TTL
                                              |
                                              +----> reponse client

```

### UDP ou TCP sur le port 53 ?

Les requêtes DNS classiques sont fréquemment envoyées avec UDP, mais les implementations DNS générales doivent prendre en charge TCP aussi. TCP est utilisé notamment pour les transferts de zones et peut être nécessaire pour des messages volumineux ou dans d’autres scénarios. Bloquer TCP/53 partout au motif que « DNS utilise UDP » provoque donc de vrais problèmes d’interopérabilité. La politique pare-feu doit tenir compte des rôles de serveur et des flux requis, notamment les transferts de zone entre serveurs autorisés.

Le port 53 est le port traditionnel du DNS, mais les protocoles DNS chiffrés peuvent utiliser d’autres transports et ports, par exemple DoT ou DoH. Il faut identifier le mécanisme réellement utilisé avant d’appliquer une règle de filtrage.

## 14. DNS interne et externe : séparer les vues

Les organisations disposent souvent de noms internes, comme `intranet.corp.example`, qui ne doivent pas être exposés publiquement ou qui pointent vers des adresses privées. Le DNS public peut publier une version différente de certains noms, afin que les clients Internet atteignent des services publics alors que les clients internes utilisent un chemin privé. Cette approche est souvent appelée **split-horizon DNS** ou DNS à vues, selon le produit.

Elle ne doit pas être improvisée. Il faut définir qui répond à chaque zone, qui peut effectuer des requêtes récursives, quels clients peuvent interroger les serveurs internes, comment les données sont mises à jour et comment les changements sont testés. Une divergence entre la vue interne et la vue externe est parfois souhaitée, mais elle doit être documentée afin d’éviter que les applications internes utilisent accidentellement une destination publique ou inversement.

**Schéma 13 — Vue DNS interne et vue DNS publique**

```text
                 nom : portail.example.com
                             |
                 +-----------+-----------+
                 |                       |
          Client interne            Client Internet
                 |                       |
                 v                       v
          +-------------+          +--------------+
          | DNS interne |          | DNS public   |
          +------+------+          +------+-------+
                 |                        |
          10.20.0.50                 198.51.100.50
          adresse privee              adresse publique

Les vues split-DNS peuvent retourner des reponses differentes
selon l'origine de la requete. Les politiques doivent rester coherentes.
```

### Résolution conditionnelle et transfert de requêtes

Un résolveur interne peut transmettre les requêtes d’un domaine déterminé vers des serveurs spécialisés : par exemple les zones d’une filiale, d’un partenaire ou d’un environnement cloud. Cette règle doit être aussi spécifique que nécessaire et ne doit pas créer une boucle entre deux résolveurs. Une configuration de forwarding ne remplace pas la responsabilité de définir les zones autoritaires, les délégations et les règles de sécurité.

### NXDOMAIN et NODATA

- **NXDOMAIN** signifie que le nom demandé n’existe pas selon la réponse autoritaire, sous réserve des particularités et mécanismes DNS concernés.
- **NODATA** signifie que le nom existe, mais qu’aucun enregistrement du type demandé n’est disponible dans la réponse autoritaire.

Il est utile de les distinguer : par exemple, le nom `serveur.exemple.test` peut avoir un enregistrement A, mais pas d’AAAA. Une requête AAAA peut donc donner une réponse sans données de ce type, sans que le nom entier soit inexistant.

Les réponses négatives peuvent être mises en cache pendant un TTL négatif dérivé des données de zone. Une entrée négative mise en cache explique pourquoi un nom qui vient d’être créé reste temporairement introuvable depuis certains clients.

**Schéma 14 — Le cache négatif DNS**

```text
Client ---- demande nom inexistant ----> Resolveur
   ^                                      |
   |                                      v
   |                                 Serveur autoritaire
   |                                      |
   |<------ NXDOMAIN + preuve -------------+
                                          |
                           cache negatif (duree limitee)
                                          |
Nouvelle demande pendant le TTL negatif -> reponse sans nouvelle recherche
Apres expiration -> nouvelle tentative vers l'autorite
Un NXDOMAIN signifie que le nom n'existe pas; NODATA signifie que le
nom existe, mais pas le type d'enregistrement demande.
```

## 15. DHCP et DNS dynamiques : comment garder les noms à jour

Dans un environnement où les postes changent d’adresse fréquemment, les administrateurs peuvent associer DHCP à des mises à jour DNS dynamiques (*Dynamic DNS*). Le but est de maintenir les enregistrements à jour quand un client obtient ou libère un bail. Le comportement précis dépend des rôles confiés au client et au serveur DHCP, du logiciel DNS, de la zone ciblée et des autorisations configurées.

Le point central est l’**identité** : qui a le droit de créer, remplacer ou supprimer un enregistrement ? Une mise à jour non authentifiée peut permettre à un client de modifier un nom qui ne lui appartient pas. Dans les environnements Microsoft, on rencontre par exemple des modèles avec mises à jour dynamiques sécurisées et des identités de compte de service. Il faut se référer à la documentation de la solution installée plutôt que de transposer une commande d’un produit à un autre.

**Schéma 15 — Cycle d’une mise à jour DNS dynamique**

```text
Client / serveur DHCP      DNS autoritaire       Resolveur
        |                         |                    |
        |-- mise a jour secure -->|                    |
        |                         |-- serial / zone    |
        |                         |                    |
        |                         |<--- requete --------|
        |                         |---- reponse ------>|
        |                         |             cache selon TTL
        |                         |                    |
DHCP peut mettre a jour A/PTR selon politique et identite.
Verifier authentification, droits, nom attribue et nettoyage des enregistrements.
```

### Nettoyage des enregistrements obsolètes

Un poste peut disparaître alors que son bail ou ses enregistrements DNS restent présents. Une politique de nettoyage (*scavenging* dans certains produits) permet de retirer des enregistrements vieillissants, mais elle doit être réglée avec prudence. Si elle s’exécute trop tôt, elle peut retirer le nom d’un appareil encore actif ; si elle n’est jamais utilisée, les anciennes entrées s’accumulent.

Avant de l’activer, documenter les intervalles de rafraîchissement, le comportement de mise à jour des clients, le rôle des serveurs DNS et les propriétaires des enregistrements statiques. Tester d’abord sur une zone de laboratoire et prévoir une sauvegarde. Les noms des serveurs, contrôleurs de domaine et équipements critiques ne devraient pas dépendre d’un nettoyage opaque.

## 16. DHCPv4 en pratique sur les postes

### Windows

Commandes courantes à lancer dans `cmd.exe` :

```text
ipconfig /all
ipconfig /release
ipconfig /renew
ipconfig /flushdns
ipconfig /displaydns
nslookup portail.exemple.test
```

`ipconfig /all` affiche les paramètres réseau détaillés, dont l’adresse, le masque, la passerelle, les DNS, le serveur DHCP et, selon la configuration, les heures de bail. `/release` abandonne le bail DHCP IPv4 sur les interfaces concernées ; `/renew` tente d’en obtenir ou d’en renouveler un. Ces commandes modifient l’état du client et doivent être utilisées en comprenant leur effet, notamment si l’accès distant dépend de cette interface. `/flushdns` vide le cache client, mais ne vide pas le cache des résolveurs intermédiaires.

### Linux

Selon la distribution et le gestionnaire réseau, on peut utiliser :

```text
ip address
ip route
resolvectl status
resolvectl query portail.exemple.test
dig portail.exemple.test A
dig portail.exemple.test AAAA
```

Les commandes exactes de renouvellement DHCP varient selon NetworkManager, systemd-networkd, dhclient ou d’autres clients. Éviter d’exécuter une commande issue d’une autre distribution sans vérifier le service qui contrôle l’interface. `ip address` et `ip route` permettent de constater l’adresse et la table de routage ; `resolvectl` n’est disponible que sur les systèmes qui utilisent systemd-resolved.

### Tester séparément l’IP et les noms

1. Vérifier que l’interface est active et possède une adresse cohérente.
2. Vérifier le masque et la route par défaut.
3. Tester la passerelle par son adresse IP.
4. Tester une destination IP connue et autorisée.
5. Interroger explicitement le serveur DNS avec `nslookup` ou `dig`.
6. Comparer une requête par nom et une requête par adresse IP, en tenant compte du pare-feu et du fait qu’un serveur peut répondre à ICMP différemment de l’application testée.

Ne pas conclure qu’un service est opérationnel parce que le ping réussit. ICMP peut être filtré tandis que DNS fonctionne, ou le ping peut réussir alors que le port applicatif est bloqué.

## 17. Vérifier DNS avec nslookup et dig

`nslookup` est souvent présent sur Windows et Linux. Il permet de tester une résolution par nom et, selon son mode, d’interroger un serveur explicite. Par exemple :

```text
nslookup portail.exemple.test
nslookup portail.exemple.test 192.168.100.53
nslookup -type=MX exemple.test 192.168.100.53
```

La deuxième commande aide à distinguer la configuration du résolveur du poste d’un défaut propre au serveur ciblé. Le paramètre de type permet d’interroger d’autres enregistrements ; la syntaxe exacte peut varier légèrement selon l’implémentation.

Avec `dig`, disponible sur de nombreux Linux et dans des outils additionnels pour d’autres systèmes :

```text
dig portail.exemple.test A
dig @192.168.100.53 portail.exemple.test A
dig exemple.test SOA
dig -x 192.0.2.20
dig +trace portail.exemple.test
```

`dig +trace` demande au client d’examiner la chaîne de délégation depuis la racine ; selon le réseau, il doit pouvoir joindre les serveurs concernés. Il ne remplace pas un test normal via le résolveur de l’entreprise. Le `status` de la réponse, les sections ANSWER/AUTHORITY/ADDITIONAL et le TTL sont utiles pour comprendre le résultat.

## 18. Sécurité DHCP : limiter les serveurs et les réponses illégitimes

Un serveur DHCP non autorisé peut distribuer une fausse passerelle ou un faux DNS, détourner le trafic, empêcher l’accès réseau ou faciliter une attaque de type intermédiaire. Les switches administrables peuvent proposer DHCP snooping, qui distingue des chemins fiables (*trusted*) des ports clients non fiables (*untrusted*) et construit des informations d’association entre adresses et ports. Les capacités précises dépendent du modèle et du système du switch.

**Schéma 16 — DHCP snooping et frontière de confiance**

```text
             Port non fiable                    Port fiable
Client -------------------- Switch ---------------- Serveur DHCP
       Discover / Request       |        Offer / ACK
                                |
                       table de bindings
                  (IP, MAC, VLAN, port, bail)
                                |
     Offre venant d'un port non fiable -> bloquee
     Reponse venant du port serveur autorise -> acceptee

Activer DHCP snooping prudemment, definir les uplinks de confiance
et verifier les options supportees sur le modele de switch.
```

### Principes de mise en place

- Définir clairement les ports par lesquels les réponses DHCP légitimes sont autorisées à entrer : vers un serveur ou un relais connu.
- Laisser les ports utilisateurs dans le profil non fiable par défaut, si c’est cohérent avec l’architecture et la documentation du constructeur.
- Examiner l’impact sur les téléphones IP, points d’accès, hyperviseurs et équipements qui hébergent plusieurs clients.
- Tester le renouvellement des baux, les mécanismes de redondance et les changements de topologie avant généralisation.
- Activer la journalisation et surveiller les compteurs, pas seulement l’état de la configuration.

Dans certains environnements Cisco, DHCP snooping est aussi une base utilisée par d’autres protections de couche 2, comme Dynamic ARP Inspection ou IP Source Guard. Leur dépendance et leur portée doivent être vérifiées sur le matériel exact. Ne jamais déclarer en *trusted* tous les ports par facilité : cela réduit fortement l’intérêt du contrôle.

## 19. Sécurité DNS : récursivité, zones et confidentialité

Un serveur autoritaire public doit répondre pour les zones dont il a la charge. Un résolveur récursif destiné aux utilisateurs ne doit généralement pas être exposé sans contrôle à Internet : un résolveur ouvert peut être abusé pour des attaques par réflexion/amplification ou pour consommer des ressources. Séparer les rôles réduit les risques et rend les politiques plus faciles à appliquer.

Les transferts de zone (AXFR/IXFR) doivent être limités aux serveurs secondaires et partenaires explicitement autorisés. Les mises à jour dynamiques doivent être authentifiées ou encadrées par une politique adaptée au produit. Restreindre la récursivité aux réseaux attendus, maintenir le logiciel à jour, contrôler les journaux et disposer de copies des zones sont des pratiques de base.

### DNSSEC, DoT et DoH ne résolvent pas le même problème

- **DNSSEC** permet la validation de l’authenticité d’origine et de l’intégrité des données DNS selon une chaîne de confiance. Il ne chiffre pas à lui seul les noms demandés et ne cache pas les requêtes à un observateur réseau.
- **DNS over TLS (DoT)** protège la confidentialité et l’intégrité du transport entre un client et un résolveur qui prennent en charge ce service.
- **DNS over HTTPS (DoH)** transporte les requêtes DNS sur HTTPS. Il peut améliorer la confidentialité du transport, mais pose aussi des questions de visibilité et de politique d’entreprise.

Le choix dépend de l’organisation, de ses clients, de sa politique de journalisation, de sa capacité de résolution interne et du modèle de menace. Un client qui utilise un résolveur public chiffré peut contourner les règles prévues autour du résolveur interne si les contrôles ne sont pas conçus pour ce scénario. Les politiques doivent être transparentes, respecter les exigences légales applicables et éviter de casser la résolution des noms privés.

**Schéma 17 — Sécuriser les rôles DHCP et DNS**

```text
+----------------+    DHCP controle    +------------------+
| Clients / VLAN | ------------------> | Serveur DHCP      |
+-------+--------+                      +------------------+
        |                                       |
        | requetes DNS                          | mises a jour
        v                                       v
+----------------+                      +------------------+
| DNS recursif   | ---- requetes ------> | DNS autoritaire  |
| controle ACL   |                       | mises a jour      |
+----------------+                      +------------------+

Protections : segmentation, ACL, DHCP snooping, DNSSEC selon besoin,
restriction des transferts de zone, journalisation et sauvegardes.
```

## 20. Pannes typiques et méthode de diagnostic

Un bon dépannage sépare les couches. Le constat initial doit préciser le symptôme, les postes affectés, le VLAN, l’heure de début, les changements récents et si l’échec concerne toutes les applications ou seulement certains noms.

**Schéma 18 — Arbre de diagnostic DHCP/DNS**

```text
PROBLEME : « le poste ne fonctionne pas »
          |
          v
Adresse IP valide ? ---- NON ---> verifier lien, VLAN, DHCP, relais
          |
         OUI
          v
Passerelle joignable ? -- NON ---> verifier masque, gateway, VLAN, ACL
          |
         OUI
          v
IP cible joignable ? ---- NON ---> verifier routage, pare-feu, service
          |
         OUI
          v
Nom DNS resolu ? -------- NON ---> tester resolveur, cache, zone, TTL
          |
         OUI
          v
Service accessible : tester port, TLS, application et chemin retour
```

### Cas A — Le poste n’a pas d’adresse IPv4 attendue

1. Vérifier l’état de lien, le VLAN, le port access/trunk et l’état de l’interface.
2. Observer l’adresse : une adresse automatique locale (par exemple `169.254.0.0/16` sur de nombreux clients Windows) indique que le client n’a pas obtenu de configuration DHCPv4 utilisable, mais ne donne pas la cause exacte.
3. Capturer le trafic : y a-t-il un DISCOVER ? Le serveur ou le relais reçoit-il ? Une OFFER revient-elle ? Le client envoie-t-il REQUEST ? Reçoit-il ACK ou NAK ?
4. Vérifier le scope, les exclusions, les baux, les conflits et la durée de bail.
5. Vérifier les relais et chemins de retour si le serveur est distant.
6. Vérifier DHCP snooping, ACL, pare-feu et mécanismes de sécurité L2.

### Cas B — Le poste a une adresse mais ne joint pas les réseaux distants

Vérifier le masque et la passerelle. Tester la passerelle, puis la route vers le serveur ou la destination. Une bonne adresse du bon sous-réseau ne garantit pas une bonne route. Dans un VLAN, plusieurs postes peuvent communiquer localement alors que leur passerelle est indisponible. Examiner la table ARP/neighbor et les journaux du switch/routeur.

### Cas C — L’adresse IP fonctionne mais le nom échoue

1. Examiner les DNS affichés par le client.
2. Interroger explicitement chaque résolveur attendu.
3. Comparer les réponses A, AAAA et CNAME, ainsi que le code de réponse.
4. Vérifier la zone autoritaire, la délégation, le CNAME cible, les enregistrements expirés et le cache négatif.
5. Tester UDP et TCP 53 lorsque le scénario le justifie ; ne pas bloquer TCP automatiquement.
6. Examiner le DNS split-horizon et le suffixe de recherche.
7. Considérer aussi le cache local de l’application et la configuration du navigateur.

### Cas D — Le DNS public fonctionne, mais le nom interne ne fonctionne plus

Vérifier que le poste interroge le résolveur interne, que celui-ci connaît la zone privée et que les clients ne contournent pas ce résolveur via une configuration chiffrée externe. Examiner la connectivité à la zone, l’état des serveurs internes, les vues DNS, le forwarding conditionnel, les délégations et les droits de mise à jour dynamique.

### Cas E — Les nouveaux noms échouent pendant quelques minutes

Le problème peut venir du cache négatif : un résolveur peut avoir mis en cache que le nom n’existait pas avant sa création. Vérifier le TTL négatif, le contenu SOA, la manière dont la zone a été mise à jour et le résolveur effectivement interrogé. Vider uniquement le cache du poste n’efface pas le cache du résolveur central.

## 21. Capture réseau : quoi observer ?

Avec Wireshark, appliquer un filtre adapté, par exemple `bootp` pour le DHCPv4 dans les versions de Wireshark qui utilisent ce nom de protocole, ou `dhcp` selon la version, puis `dns` pour les paquets DNS. Les filtres d’affichage et noms exacts peuvent changer suivant l’outil et les dissectors installés. La capture doit se trouver au bon endroit : un port de poste, l’interface VLAN du relais ou l’interface côté serveur n’observe pas les mêmes étapes.

Pour DHCP, corréler les messages par identifiant de transaction, adresse matérielle ou identifiant client, option serveur, adresse proposée, champ `giaddr` et options reçues. Pour DNS, examiner le nom demandé, le type, le serveur questionné, l’identifiant de transaction, les drapeaux, le code de réponse, les sections de l’answer/authority/additional et le temps de réponse. Une capture peut révéler l’absence de réponse, mais elle ne prouve pas toujours pourquoi le composant n’a pas répondu : il faut la croiser avec les journaux du serveur, les compteurs et la configuration.

### Capture côté client ou côté serveur ?

- **Client seulement :** démontre ce qu’il émet et ce qu’il reçoit ; si aucun retour n’apparaît, le défaut peut être dans n’importe quel composant intermédiaire.
- **Relais :** permet de comparer le broadcast reçu, le paquet relayé et le retour reçu sur la même interface ou sur des interfaces différentes.
- **Serveur :** confirme si le paquet atteint le service et si une réponse est générée. Un paquet entrant sans réponse dirige l’enquête vers le service, la politique ou le scope.
- **Deux extrémités :** comparer les horodatages et les identifiants des transactions peut localiser une perte ou un blocage sur le chemin.

## 22. Laboratoire pratique : DHCP et DNS pour un VLAN utilisateur

### Topologie et paramètres

**Schéma 19 — Topologie du laboratoire**

```text
                 +----------------------+
                 | R1 / passerelle VLAN |
                 | 192.168.10.1         |
                 +----------+-----------+
                            |
                      VLAN 10 / LAN
                            |
                   +--------+--------+
                   | Switch + clients|
                   +--------+--------+
                            |
                         reseau IP
                            |
                 +----------+-----------+
                 | Serveur infra        |
                 | DHCP 10.0.0.20       |
                 | DNS  10.0.0.53       |
                 +----------------------+

Tester d'abord DHCP, puis passerelle, puis DNS, enfin HTTP/HTTPS.
```

Le laboratoire utilise un PC dans VLAN 10, un switch L2, une passerelle L3 qui relaie les requêtes et deux services centralisés (DHCP et DNS) ou un serveur qui héberge les deux rôles. Plan d’adressage d’exemple : VLAN 10 `192.168.10.0/24`, passerelle `192.168.10.1`, serveur DHCP `192.168.100.10`, serveur DNS `192.168.100.53`. Le serveur DNS peut être différent du serveur DHCP.

### Étape 1 — Valider l’adressage

- Vérifier l’adresse du poste et confirmer qu’elle appartient au pool annoncé.
- Vérifier le masque et la passerelle.
- Vérifier que les plages réservées ne sont pas distribuées.
- Confirmer que le pool contient assez d’adresses pour les clients testés.

### Étape 2 — Valider DHCP

- Observer DORA lorsque le client demande une adresse neuve ou lorsque l’environnement permet un renouvellement contrôlé.
- Contrôler le scope et les baux sur le serveur.
- Si le service est distant, confirmer le relais et le retour routé.
- Tester l’effet d’une panne contrôlée dans un laboratoire, pas sur le réseau de production.

### Étape 3 — Valider DNS

- Depuis le client, examiner la liste des résolveurs.
- Interroger `portail.exemple.test` via le résolveur attendu.
- Interroger un type A ou AAAA selon les enregistrements de laboratoire.
- Vérifier le TTL, puis modifier une réponse dans une zone de test afin d’observer le comportement de cache.
- Vérifier le résultat depuis un deuxième client afin de comparer le cache local et le cache du résolveur.

### Étape 4 — Tester les échecs un par un

Dans un environnement isolé, réaliser des tests contrôlés : supprimer temporairement l’option DNS dans le scope, interrompre le chemin vers le relais, utiliser un nom de test inexistant et observer le cache négatif. Ne pas provoquer de panne sur un serveur ou un réseau utilisé par d’autres personnes. Réinitialiser les paramètres après chaque test et noter les observations.

### Étape 5 — Écrire un rapport d’incident

Le rapport doit mentionner : contexte et heure, symptôme exact, périmètre affecté, adresses et options observées, résultats de chaque commande, captures disponibles, cause démontrée, correction, test de validation, risque résiduel et action préventive. Éviter les conclusions du type « DHCP était cassé » si les seules preuves montrent que le client ne recevait pas d’OFFER : le relais, le pool ou le retour réseau peuvent en être la cause.

## 23. Exercices corrigés

### Exercice 1 — Calcul de pool

Le réseau est `192.168.30.0/24`. La passerelle utilise `.1`, les serveurs fixes `.2` à `.19`, et les imprimantes `.20` à `.39`. L’administrateur choisit le pool `.50` à `.220`.

**Correction :** le masque /24 permet les adresses hôtes `.1` à `.254`. Les plages fixes `.1–.39` sont en dehors du pool `.50–.220`, donc elles ne se chevauchent pas. Les adresses `.40–.49` et `.221–.254` restent hors de cette plage précise et ne seront pas distribuées par ce pool si la configuration est strictement limitée à `.50–.220`. Il reste 171 adresses dans cette plage inclusive. Il faut aussi vérifier la syntaxe du serveur, les réservations et l’existence d’autres pools concurrents.

### Exercice 2 — DHCP sans réponse

Le client envoie DHCPDISCOVER ; aucune offre n’apparaît dans sa capture. Le serveur est situé dans un sous-réseau distant.

**Correction :** cette capture ne suffit pas à accuser le serveur. Vérifier si le broadcast arrive à la passerelle, si le relais est configuré, si les paquets relayés atteignent le serveur, si le scope correspondant existe et si les réponses reviennent. Faire une capture au relais et côté serveur pour localiser l’étape manquante.

### Exercice 3 — Adresse IP valide, nom impossible à résoudre

Le PC a `192.168.10.51/24`, une passerelle correcte, mais ne résout pas `fichiers.exemple.test`. Un test par IP vers le service réussit.

**Correction :** examiner le résolveur attribué, interroger le DNS explicitement, vérifier les enregistrements A/AAAA/CNAME, la zone interne, le suffixe de recherche et les caches. Le fait que l’IP fonctionne réduit la probabilité d’une panne générale de routage, mais ne prouve pas que tous les flux DNS sont autorisés.

### Exercice 4 — Un enregistrement vient d’être créé, mais NXDOMAIN persiste

**Correction :** vérifier la présence du record sur le serveur autoritaire, puis identifier le résolveur interrogé et la durée du cache négatif. Le cache du poste et celui du résolveur sont séparés. Une mise à jour autoritaire ne purge pas automatiquement les caches déjà remplis.

### Exercice 5 — Un client reçoit une mauvaise passerelle

**Correction :** comparer l’option Router du message ACK avec la configuration du scope, la configuration globale et les options spécifiques au client ou au VLAN. Si le serveur héberge plusieurs scopes, vérifier que le relais permet d’identifier le bon sous-réseau. Ne pas changer arbitrairement la passerelle sur le poste sans corriger la source du paramètre.

## 24. Quiz de validation

1. À quoi servent DHCP et DNS, et pourquoi l’un ne remplace-t-il pas l’autre ?
2. Quel est l’ordre des quatre étapes DORA ?
3. Pourquoi un broadcast DHCPv4 ne traverse-t-il pas normalement un routeur ?
4. Quel est le rôle d’un relais DHCP ?
5. Quelle différence y a-t-il entre une réservation et une adresse configurée statiquement sur le client ?
6. À quoi servent les options DHCP Router et DNS ?
7. Quelle est la différence entre un serveur récursif et un serveur autoritaire ?
8. À quoi servent A, AAAA et CNAME ?
9. Que représente le TTL et pourquoi un changement DNS peut-il ne pas être visible immédiatement ?
10. Que signifie NXDOMAIN ? Quelle différence avec une réponse sans données pour le type demandé ?
11. Pourquoi le DNS doit-il prendre en charge UDP et TCP ?
12. Quel est le rôle de DHCP snooping ?
13. Dans un déploiement IPv6 courant, d’où vient la route par défaut ?
14. DNSSEC chiffre-t-il les requêtes DNS ?
15. Quelle méthode permet d’éviter de confondre une panne IP et une panne DNS ?

### Réponses synthétiques

1. DHCP fournit des paramètres réseau ; DNS traduit des noms en informations de service. 2. Discover, Offer, Request, ACK. 3. Les routeurs ne retransmettent pas automatiquement les broadcasts de lien local. 4. Il relaie les requêtes vers le serveur distant et fournit des informations d’origine nécessaires au choix du scope. 5. La réservation reste gérée par le serveur ; la configuration statique se trouve sur le client. 6. Router indique la passerelle par défaut ; DNS désigne les résolveurs. 7. Le récursif cherche une réponse complète pour le client ; l’autoritaire répond pour les zones dont il a la charge. 8. A = IPv4, AAAA = IPv6, CNAME = alias. 9. Le TTL limite la durée de cache ; les copies déjà mises en cache peuvent rester valides jusqu’à expiration. 10. NXDOMAIN indique que le nom n’existe pas ; NODATA indique que le nom existe mais n’a pas de record du type demandé. 11. UDP est fréquent, mais TCP est indispensable pour certains scénarios, notamment les transferts de zones et les réponses volumineuses. 12. Il limite les réponses DHCP non autorisées sur les ports non fiables et peut alimenter une base de bindings. 13. Généralement des Router Advertisements. 14. Non : DNSSEC apporte validation d’origine et intégrité, pas la confidentialité du transport. 15. Tester chaque couche séparément, consulter la configuration et capturer les paquets aux bons points.

## 25. Checklist de mise en service

### DHCP

- [ ] Chaque VLAN a un sous-réseau et un scope documentés.
- [ ] Les adresses fixes, exclusions et réservations sont inventoriées.
- [ ] Masque, passerelle, DNS et domaine sont vérifiés sur un client réel.
- [ ] Les durées de bail sont adaptées à la mobilité et à la capacité du pool.
- [ ] Les relais et chemins de retour sont testés.
- [ ] La protection contre les serveurs DHCP indésirables est évaluée.
- [ ] Les journaux, alertes, sauvegardes et procédures de restauration sont disponibles.

### DNS

- [ ] Les zones, enregistrements, TTL et délégations sont documentés.
- [ ] Les résolveurs clients sont les bons pour leur réseau et leur usage.
- [ ] Les zones internes ne sont pas exposées par erreur sur la vue publique.
- [ ] Récursivité, transferts de zone et mises à jour dynamiques sont contrôlés.
- [ ] DNS répond via UDP et TCP selon les besoins.
- [ ] Les réponses négatives et les caches sont pris en compte dans le plan de migration.
- [ ] Les journaux, la supervision et les sauvegardes de zones sont testés.

### Validation du service

- [ ] Un client neuf obtient une configuration attendue.
- [ ] Un client existant renouvelle son bail selon la politique.
- [ ] Le client joint sa passerelle et une destination autorisée.
- [ ] Les enregistrements A/AAAA nécessaires se résolvent depuis les bons résolveurs.
- [ ] Les enregistrements critiques et les résolutions inverses sont vérifiés si requis.
- [ ] Le comportement lors d’une panne de composant a été testé en laboratoire.
- [ ] Les changements et résultats sont documentés, y compris les limites connues.

## 26. Glossaire

- **ACK :** message DHCP confirmant une demande acceptée.
- **Autoritaire :** serveur qui détient les données officielles d’une zone DNS.
- **Bail :** durée d’utilisation d’une adresse attribuée par DHCP.
- **Cache :** copie temporaire d’une réponse ou d’une information utile.
- **CNAME :** enregistrement qui désigne un nom canonique cible.
- **DHCP :** protocole de configuration dynamique des hôtes IP.
- **DORA :** séquence Discover, Offer, Request, Acknowledge de DHCPv4.
- **DNS :** système de noms distribué et hiérarchique.
- **FQDN :** nom de domaine pleinement qualifié.
- **Giaddr :** champ d’adresse IP de relais utilisé dans DHCPv4 pour représenter le relais / réseau d’origine selon le scénario.
- **Lease :** bail d’adresse.
- **NS :** enregistrement qui identifie un serveur de noms pour une zone.
- **NXDOMAIN :** code indiquant que le nom demandé n’existe pas.
- **Option DHCP :** donnée de configuration transportée dans un message DHCP.
- **RA :** Router Advertisement IPv6, utilisé notamment pour annoncer des préfixes et le routeur par défaut.
- **Récursif :** résolveur qui cherche une réponse complète pour un client.
- **Relay :** équipement qui relaie les requêtes DHCP hors du réseau local du client.
- **Scope :** ensemble des adresses et paramètres attribuables à un sous-réseau.
- **SLAAC :** autoconfiguration sans état IPv6.
- **SOA :** enregistrement qui décrit des paramètres essentiels d’une zone DNS.
- **TTL :** durée de vie d’une information mise en cache.


## 28. Comprendre l’expiration et le cache négatif sans confondre les couches

Le diagnostic des services d’infrastructure gagne en précision lorsqu’on sépare trois horloges : le bail d’adresse, le TTL des réponses DNS positives et le TTL des réponses DNS négatives. Ces mécanismes n’ont ni la même fonction ni nécessairement la même durée. Le bail DHCP indique au client combien de temps il peut utiliser son adresse ; le TTL DNS détermine combien de temps une réponse peut être réutilisée par un cache ; le cache négatif conserve temporairement l’information qu’une question n’a pas obtenu les données attendues.

**Schéma 20 — Trois durées indépendantes**

```text
DHCP : duree du bail
[attribution]-------------------------------[expiration / renouvellement]

DNS : TTL du cache
[reponse mise en cache]---------[expiration entree]

Application : duree de session / cache local
[connexion ou cache applicatif]---------------[fin / revalidation]

Ces horloges sont independantes. Un nouveau bail ne vide pas
necessairement le cache DNS; la fin du TTL ne renouvelle pas le bail DHCP.
```

### Scénario guidé : « Internet fonctionne, mais l’application ne s’ouvre pas »

Un client dispose d’une adresse IPv4 valide. La passerelle répond et l’accès à une destination par adresse IP fonctionne. L’application utilise `erp.exemple.test`, mais le nom ne se résout pas. Il existe au moins six pistes différentes : un résolveur incorrect reçu par DHCP, un serveur DNS injoignable, une zone interne non chargée, un enregistrement manquant, une réponse négative encore en cache ou une règle de filtrage DNS.

La méthode la plus courte n’est pas de redémarrer immédiatement le poste. Commencer par relever la configuration avec `ipconfig /all` ou la commande équivalente, puis interroger explicitement le résolveur affiché. Si le résolveur ne répond pas, tester la connectivité vers lui et consulter ses journaux. S’il répond `NXDOMAIN`, vérifier la zone autoritaire et la délégation. S’il répond avec la mauvaise adresse, comparer la vue DNS utilisée et le cache. Si la réponse est correcte mais l’application échoue, examiner ensuite le port applicatif, le certificat, le proxy et la configuration locale de l’application.

Ce processus montre pourquoi il faut éviter des formulations vagues comme « le réseau ne marche pas ». Décrire le point précis qui échoue accélère la collaboration entre équipe réseau, systèmes, sécurité et applicatif.

## 29. Matrice de dépannage rapide

| Symptôme observé | Vérification immédiate | Piste suivante |
|---|---|---|
| Adresse `169.254.x.x` sur Windows IPv4 | DHCPDISCOVER / renew / état interface | VLAN, relais, scope, serveur, DHCP snooping |
| Adresse IP correcte mais pas de passerelle utilisable | Masque, option Router, ARP/neighbor | SVI, trunk, passerelle, conflit IP |
| Plusieurs clients d’un seul VLAN échouent en même temps | Scope et interface de relais de ce VLAN | Pool épuisé, helper, ACL ou panne SVI |
| Tous les clients échouent dans plusieurs VLAN | État des serveurs et services centraux | DHCP/DNS, routage du réseau serveurs, sécurité |
| Une adresse IP fonctionne mais le nom ne fonctionne pas | `nslookup` / `dig` vers le DNS configuré | Zone, cache, forwarding, split-horizon |
| Un seul nom échoue | Type de réponse et enregistrement | CNAME, TTL négatif, erreur de zone |
| Les noms publics fonctionnent, les noms privés non | Serveur DNS reçu et vue utilisée | Résolveur interne, zone privée, VPN/ACL |
| Les changements DNS ne sont pas visibles partout | TTL positif/négatif, caches client et récursif | Délégation, autorité, client qui utilise un autre DNS |
| Le renouvellement fonctionne en VLAN local mais pas distant | Captures client, relais, serveur | `giaddr`, routes retour, ACL, options relais |
| Résolutions intermittentes | Comparer plusieurs résolveurs et horodatages | Autorité secondaire, DNS anycast, pertes réseau, charge |

Une bonne matrice n’est pas une liste qui donne automatiquement la cause : elle propose un ordre d’investigation à confirmer. Dans un rapport, noter la preuve qui a permis d’écarter une hypothèse.

## 30. Principes de conception de production

### Disponibilité et redondance

Éviter de dépendre d’un unique serveur DHCP ou DNS pour l’ensemble d’un site sans plan de continuité. Plusieurs serveurs DNS peuvent être annoncés aux clients, mais deux adresses ne suffisent pas à garantir qu’ils fournissent des réponses cohérentes. La conception doit tenir compte des zones, de la réplication, de la dépendance réseau, de la capacité, de la surveillance et de la procédure de restauration.

Pour DHCP, les solutions de haute disponibilité peuvent utiliser des relations de failover, des mécanismes de split-scope dans certains environnements historiques ou des architectures de redondance propres au produit. Il ne faut pas activer simultanément des pools indépendants qui se chevauchent sans coordination : cela risque d’attribuer la même adresse à plusieurs clients. Le comportement exact de la haute disponibilité est propre au produit et à la version ; le tester en panne contrôlée est indispensable.

### Observabilité

Surveiller le taux d’utilisation de chaque scope, les erreurs de serveur, les conflits, les refus, les temps de réponse DNS, les réponses SERVFAIL/NXDOMAIN, la taille et l’évolution du cache, l’échec des transferts de zone et la réussite des contrôles synthétiques. Une moyenne correcte peut masquer quelques clients affectés ; répartir les mesures par site, VLAN, service et serveur aide à réduire le périmètre.

### Gestion de changement

Avant de modifier un pool ou une zone, sauvegarder la configuration et l’état important, documenter les enregistrements et valeurs actuelles, déterminer le TTL pertinent et prévoir un test de retour arrière. Après le changement, valider depuis un client réel, pas uniquement depuis la console du serveur. Pour une modification DNS, tester la réponse autoritaire et le résolveur utilisé par le client.

### Documentation à conserver

- diagrammes de sous-réseaux, VLAN et relais ;
- scopes, exclusions, réservations, options et durée de bail ;
- rôles DNS, zones, délégations, transferts, TTL et propriétaires ;
- règles de pare-feu et ACL autorisant les flux nécessaires ;
- procédures de sauvegarde, restauration et test de bascule ;
- résultats de recette et coordonnées de l’équipe responsable.

## 31. Synthèse : les règles d’or

1. **DHCP attribue et renouvelle des paramètres IP ; DNS résout des noms.** Les deux services interagissent mais ne doivent pas être confondus.
2. **Une transaction DHCP doit être suivie de bout en bout.** Identifier le premier message manquant avant de corriger la configuration.
3. **Le relais est un composant actif de la chaîne.** Son interface d’origine, les scopes et le chemin de retour doivent être cohérents.
4. **Le DNS fonctionne par zones, délégations et caches.** Un changement autoritaire n’efface pas immédiatement les données déjà mises en cache.
5. **UDP/53 n’est pas le seul chemin DNS.** TCP/53 doit être supporté ; les transferts de zone et les réponses volumineuses peuvent en dépendre.
6. **IPv6 a ses propres mécanismes.** RA, SLAAC et DHCPv6 doivent être conçus ensemble ; la route par défaut vient typiquement des RA.
7. **La sécurité doit protéger les rôles et les identités.** Contrôler les ports DHCP de confiance, les mises à jour DNS dynamiques, les transferts de zones et l’accès récursif.
8. **Un dépannage est une démonstration.** Collecter des données, comparer les chemins et documenter la cause exacte avant de déclarer une résolution.


## 32. Références techniques

Les ressources suivantes permettent d’approfondir le protocole et de vérifier les détails normatifs. Les guides des constructeurs et des systèmes d’exploitation doivent compléter les RFC pour les syntaxes et choix de déploiement concrets.

- [RFC 2131 — Dynamic Host Configuration Protocol (DHCPv4)](https://www.rfc-editor.org/rfc/rfc2131.html)
- [RFC 2132 — DHCP Options and BOOTP Vendor Extensions](https://www.rfc-editor.org/rfc/rfc2132.html)
- [RFC 1034 — Domain Names: Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034.html)
- [RFC 1035 — Domain Names: Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035.html)
- [RFC 2308 — Negative Caching of DNS Queries](https://www.rfc-editor.org/rfc/rfc2308.html)
- [RFC 4033 — DNS Security Introduction and Requirements](https://www.rfc-editor.org/rfc/rfc4033.html)
- [RFC 7766 — DNS Transport over TCP](https://www.rfc-editor.org/rfc/rfc7766.html)
- [RFC 7858 — DNS over TLS](https://www.rfc-editor.org/rfc/rfc7858.html)
- [RFC 8484 — DNS over HTTPS](https://www.rfc-editor.org/rfc/rfc8484.html)
- [RFC 9915 — Dynamic Host Configuration Protocol for IPv6 (DHCPv6)](https://www.rfc-editor.org/rfc/rfc9915.html)
- [Cisco IOS XE — Configuring DNS](https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_configuring_dns.html)


**Fin du cours.**
