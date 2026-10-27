# Sécurité des services réseau

> **Mise en contexte**

Un réseau peut avoir des routeurs correctement configurés, des VLAN bien séparés et des pare-feu stricts tout en restant fragile si les services qui permettent aux machines de se découvrir, de s'authentifier, de synchroniser leur heure et d'échanger des données sont mal protégés. DNS, DHCP, NTP, TLS, SSH, LDAP, Kerberos, RADIUS, SNMP, Syslog, HTTP, SMTP et les services de fichiers rendent le réseau utilisable. Ils constituent aussi des points d'appui essentiels pour l'administration, la disponibilité et la sécurité.

Ce cours suit l'introduction aux SIEM. Il apprend à analyser la fonction d'un service, ses dépendances, ses ports, son exposition, ses journaux et ses contrôles de sécurité. Tu apprendras à diagnostiquer un problème sans ouvrir aveuglément tous les ports, à sécuriser les protocoles d'administration et à produire des preuves utiles pour le SIEM.

**Résultats attendus :** savoir dessiner les flux nécessaires, reconnaître les services critiques, comprendre les enjeux DNS/DHCP/NTP, expliquer TLS et la validation des certificats, sécuriser les accès d'administration, choisir des contrôles adaptés aux services AAA, supervision et journalisation, tester la connectivité avec les outils natifs, enquêter sur une anomalie et documenter les changements.

**Précaution :** exécute les commandes dans un laboratoire ou sur des systèmes dont tu as l'autorisation. Les commandes de diagnostic ci-dessous sont en lecture ou en observation lorsque cela est indiqué. Ne lance pas de scan large, de tentative d'authentification répétée, de modification de zone DNS, de rotation de clé ou de changement de pare-feu sur la production sans procédure approuvée.

## 1. Comprendre le rôle des services réseau

Un service réseau fournit une fonction consommée par d'autres systèmes. Il peut répondre à une requête, accorder une adresse, authentifier un utilisateur, distribuer une configuration, maintenir l'heure ou transporter une donnée. Il s'appuie généralement sur un protocole, une adresse d'écoute, un processus serveur, une politique d'accès, des dépendances et des journaux.

Il faut distinguer trois notions. Le **protocole** définit les messages et règles d'échange. Le **service** désigne la fonction fournie par un système ou une application. Le **port** est un identifiant de transport utilisé par TCP ou UDP pour joindre un processus. Le fait qu'un port soit ouvert ne prouve ni que le bon service est derrière, ni que sa version est sûre, ni que son accès devrait être autorisé. Les numéros usuels sont des repères de diagnostic, pas une vérité issue de la seule observation d'un port.

~~~text
Client
  │ requête vers destination:port
  ▼
Réseau / route / ACL / pare-feu
  │ le trafic est-il autorisé ?
  ▼
Socket d'écoute du serveur
  │ le processus est-il actif ?
  ▼
Application / protocole / authentification
  │ l'opération est-elle permise ?
  ▼
Réponse + journalisation + supervision
~~~

La sécurité d'un service se raisonne selon plusieurs propriétés : disponibilité, confidentialité, intégrité, authenticité, autorisation, traçabilité et capacité de restauration. Une disponibilité élevée sans authentification peut exposer des données. Un chiffrement robuste sans validation de l'identité du serveur laisse possible une connexion au mauvais interlocuteur. Une authentification correcte sans contrôle d'autorisation peut permettre à un compte valide d'effectuer une action interdite.

### 1.1 Dépendances et impact en chaîne

Des services se dépendent souvent les uns des autres. Une application peut utiliser DNS pour trouver son serveur, NTP pour valider correctement les horaires, un annuaire pour authentifier les utilisateurs, TLS pour protéger sa session et Syslog ou un agent pour exporter ses traces. Une panne du DNS peut donner l'impression que l'application est en panne même si son processus fonctionne. Un décalage horaire peut perturber les tickets Kerberos, les certificats et la corrélation des journaux.

~~~text
Client ── DNS ──► adresse du serveur
  │                  │
  ├── DHCP : adresse, passerelle et résolveur
  ├── NTP : horloge cohérente
  └── TLS / identité : confiance dans le serveur
                         │
                         ▼
                 Application métier
                         │
            LDAP / Kerberos / RADIUS
                         │
                         ▼
                 accès et autorisation
                         │
                         ▼
                journaux / supervision
~~~

Lors d'un incident, ne corrige pas immédiatement la dernière alerte visible. Remonte les dépendances. Si un client ne parvient pas à se connecter, la cause peut être une mauvaise résolution, un port filtré, un certificat expiré, un refus d'authentification, une permission manquante ou un service arrêté. Chaque hypothèse exige un test différent.

### 1.2 Ports courants et précautions

Les ports courants permettent d'orienter le diagnostic : DNS utilise habituellement TCP/UDP 53 ; DHCPv4 UDP 67/68 ; NTP UDP 123 ; HTTP TCP 80 ; HTTPS TCP 443 ; SSH TCP 22 ; LDAP TCP/UDP 389 selon l'opération et l'usage ; LDAPS généralement TCP 636 ; Kerberos utilise principalement TCP/UDP 88 ; Syslog peut employer plusieurs transports et ports selon la configuration ; SNMP utilise habituellement UDP 161 pour les requêtes et 162 pour les traps ; SMTP utilise couramment TCP 25 entre serveurs et 587 pour la soumission authentifiée, avec d'autres mécanismes selon l'architecture. RADIUS emploie traditionnellement UDP 1812 pour l'authentification et UDP 1813 pour la comptabilité, mais les déploiements hérités peuvent différer.

Ces valeurs ne doivent pas devenir des règles universelles. Les produits peuvent avoir des ports personnalisés, des proxys, du NAT ou des tunnels. Les ports UDP ne répondent pas toujours à une sonde générique. Un test qui échoue peut signifier paquet perdu, filtrage, absence de service, réponse retardée ou contrôle de sécurité. Avant de changer une ACL, vérifie la destination, le protocole, le sens du flux et la fonction exacte qui l'utilise.

~~~text
Matrice de flux utile
Client / zone | Destination | Service | Sens | Motif métier
Postes        | DNS interne | TCP/UDP 53 | aller/retour | résolution
Postes        | DHCP       | UDP 67/68  | broadcast/relay | attribution IP
Admin         | serveurs   | TCP 22 / 3389 selon politique | contrôlé | administration
Applications  | annuaire   | LDAP/TLS/Kerberos selon design | interne | identité
Équipements   | collecteur | Syslog sécurisé | sortant vers collecteur | audit
Supervision   | équipements| SNMPv3 | depuis poller autorisé | métriques
~~~

Une matrice réelle doit comporter les sources et destinations exactes, propriétaire, environnement, justification, protocole, port, authentification, chiffrement, mécanisme de journalisation, règle de pare-feu, date de revue et personne qui approuve. Elle évite les règles trop générales telles que « autoriser tout le VLAN serveur vers le réseau d'administration ».

## 2. DNS : résolution, confiance et protection

Le Domain Name System traduit des noms en informations de ressources : adresses, serveurs de messagerie, alias, délégations ou autres enregistrements. Il est souvent la première dépendance d'une connexion. Une réponse DNS incorrecte peut orienter un client vers la mauvaise destination ; une réponse absente peut empêcher un service de fonctionner malgré une application saine.

Les enregistrements les plus courants comprennent **A** pour une adresse IPv4, **AAAA** pour IPv6, **CNAME** pour un alias, **MX** pour le routage du courrier, **TXT** pour différents usages textuels comme SPF selon le contexte, **NS** pour les serveurs faisant autorité et **PTR** pour la résolution inverse. **SOA** décrit des paramètres de zone et un serveur principal logique. Les enregistrements DNS ont des durées de vie (TTL) qui influencent le cache ; après un changement, les clients peuvent continuer à utiliser une réponse tant que sa durée de vie reste valide.

~~~text
Application demande api.exemple.test
             │
             ▼
Stub resolver du client
             │
             ▼
Résolveur récursif configuré
             │
      cache valide ?
        ├── oui ──► répondre du cache
        └── non
             │
       racine / TLD / zone autoritative
             │
             ▼
Réponse avec TTL ──► cache du résolveur ──► client
~~~

Un **résolveur récursif** recherche les réponses au nom du client et peut les mettre en cache. Un **serveur faisant autorité** publie les données d'une zone. Ces rôles ne sont pas identiques ; ils peuvent être fournis par le même produit, mais la configuration de l'accès doit les distinguer. Les serveurs autoritatifs internes, les résolveurs des postes et les zones privées doivent être séparés selon l'architecture. N'expose pas l'administration ni les transferts de zone à tout Internet sans justification.

### 2.1 Zones internes, split DNS et transferts

Une organisation peut utiliser des noms privés accessibles seulement depuis le réseau interne et des réponses publiques différentes pour ses services exposés. Ce modèle de DNS à vues différentes doit être conçu pour éviter les fuites d'informations internes. Les noms de contrôleurs, systèmes de gestion et adresses privées peuvent renseigner un attaquant sur l'architecture.

Les transferts de zone répliquent les enregistrements entre serveurs autorisés. Ils doivent être limités aux serveurs secondaires légitimes, et les modifications dynamiques doivent être autorisées uniquement par des identités et systèmes prévus. Lorsqu'un enregistrement est modifié sans approbation, examine l'acteur, l'heure, la zone, le nom du record, la valeur précédente et la nouvelle valeur si elles sont consignées.

Les journaux DNS ont deux objectifs distincts : l'observation des requêtes et l'audit des changements de configuration. La disponibilité de chaque catégorie dépend du logiciel et de ses paramètres. Sur Windows Server, la documentation Microsoft décrit des journaux DNS d'audit qui couvrent notamment certaines modifications de serveur, zone et enregistrement. Vérifie la version et le canal exact dans l'Observateur d'événements.

### 2.2 DNSSEC, DoT et DoH

**DNSSEC** ajoute des mécanismes cryptographiques d'authenticité de l'origine et d'intégrité des données DNS, y compris une preuve authentifiée de non-existence dans les cas pris en charge. Il ne chiffre pas les noms demandés et ne fournit pas à lui seul le contrôle d'accès ou la protection contre toutes les attaques par déni de service. Il dépend d'une chaîne de confiance et d'une gestion correcte des signatures et clés.

**DNS over TLS (DoT)** et **DNS over HTTPS (DoH)** protègent le transport entre le client et le résolveur en utilisant TLS. Ils peuvent réduire l'observation ou la modification par un intermédiaire réseau, mais ils ne remplacent pas DNSSEC : le chiffrement de transport protège le canal vers le résolveur, alors que DNSSEC vérifie l'intégrité et l'origine des données DNS selon sa chaîne de confiance. Un client configuré pour utiliser un résolveur chiffré externe peut également contourner les journaux DNS internes ou les politiques de filtrage. Cette conséquence doit être gérée par l'architecture et les politiques des terminaux, pas par l'hypothèse que le chiffrement DNS signifie que tout est sûr.

~~~text
DNS classique : client ── requête DNS ──► résolveur
DoT / DoH       : client ══ canal TLS ══► résolveur
DNSSEC          : réponse signée + chaîne de confiance vérifiable

DoT/DoH : confidentialité du transport jusqu'au résolveur
DNSSEC  : authenticité/intégrité des données DNS signées
Aucun de ces mécanismes ne remplace tous les autres contrôles.
~~~

### 2.3 Diagnostic DNS

Sous Windows, la commande suivante résout un enregistrement A à l'aide du mécanisme DNS configuré sur la machine :

~~~powershell
Resolve-DnsName portal.example.com -Type A
~~~

Remplace le nom par un nom de laboratoire ou une destination autorisée. Le résultat attendu indique un ou plusieurs enregistrements et les informations associées selon le résolveur. Une absence de réponse peut venir du nom inexistant, du DNS configuré, d'un timeout, d'un suffixe de recherche ou d'une politique. Pour vérifier un serveur DNS particulier :

~~~powershell
Resolve-DnsName portal.example.com -Server 192.0.2.53 -Type A
~~~

L'adresse 192.0.2.53 est un exemple réservé à la documentation ; remplace-la uniquement par l'adresse du résolveur de ton laboratoire. Ce test compare deux chemins de résolution, mais ne prouve pas à lui seul quel composant est fautif.

Sous Linux, si l'outil dig est installé :

~~~bash
dig portal.example.com A
dig @192.0.2.53 portal.example.com A
dig portal.example.com MX
dig portal.example.com SOA
~~~

**dig** affiche la réponse, son autorité et des détails de protocole. Une requête directe évite le chemin du résolveur configuré, mais elle doit être faite sur une cible autorisée. Utilise un nom connu de test et compare réponse, TTL, serveur interrogé et délai. N'utilise pas le mode trace sur des réseaux où les requêtes directes vers des serveurs externes ne sont pas autorisées.

### 2.4 Symptômes DNS fréquents

Une adresse incorrecte peut provenir d'une ancienne entrée en cache, d'une modification non propagée, d'une vue DNS différente ou d'un enregistrement mal configuré. Une réponse de type NXDOMAIN signifie que la source interrogée indique que le nom n'existe pas dans ce contexte ; elle ne prouve pas que le nom n'existe dans toutes les vues possibles. Une erreur SERVFAIL peut correspondre à un problème de résolution, de validation DNSSEC ou de serveur amont. Le diagnostic doit identifier le résolveur, le record, le TTL, l'autorité et la portée de l'échec.

Ne vide pas tous les caches sur un poste de production comme première action. Un cache permet d'éviter des recherches répétées et sa suppression peut modifier temporairement le comportement. Capture d'abord la réponse, le serveur interrogé et le moment ; puis applique la procédure de changement approuvée si le cache est en cause.

## 3. DHCP et gestion des adresses IP

DHCP automatise la distribution de paramètres réseau comme l'adresse IP, le masque, la passerelle, les résolveurs DNS et la durée du bail. En DHCPv4, le modèle courant est souvent décrit par DORA : Discover, Offer, Request, Acknowledge. Le client demande une configuration, le serveur propose une adresse, le client demande le bail et le serveur confirme. Des mécanismes de relais peuvent transférer les demandes entre sous-réseaux.

~~~text
Client sans adresse
    │ DHCPDISCOVER
    ▼
Réseau local / relais DHCP
    │
    ▼
Serveur DHCP ── DHCPOFFER
    │
    ◄── DHCPREQUEST
    │
    └── DHCPACK : IP, masque, passerelle, DNS, durée du bail
~~~

Le serveur DHCP s'appuie sur des plages ou étendues, réservations, exclusions, options et durée de bail. L'adresse attribuée n'est pas forcément liée à l'identité humaine du client : elle peut être réutilisée, modifiée par une réservation ou observée à un autre moment. Pour une investigation, rapproche l'heure du bail, l'adresse MAC si elle est disponible et légitimement collectée, l'identité du port de commutation ou du point d'accès, ainsi que les journaux de connexion.

### 3.1 Risques et contrôles

Un serveur DHCP non autorisé peut distribuer une passerelle ou un résolveur contrôlé par un acteur non fiable. Les contrôles possibles comprennent des serveurs autorisés, un relais configuré, des VLAN de confiance et, sur les commutateurs qui le prennent en charge, DHCP snooping. La protection doit être conçue pour l'équipement réel et le mode de déploiement ; activer une fonction sans connaître les ports de confiance peut interrompre l'attribution d'adresses.

Le renouvellement des baux, les étendues saturées, les conflits d'adresses et les relais mal configurés sont des causes classiques d'incidents. Si des clients reçoivent une adresse mais pas de passerelle, inspecte les options et le scope concerné. Si seuls des clients d'un VLAN sont touchés, vérifie le relais, la route et les règles entre VLAN avant de conclure que le service global est arrêté.

~~~text
VLAN 10 ── relais autorisé ──► serveur DHCP
VLAN 20 ── relais autorisé ──► serveur DHCP
VLAN 30 ── relais manquant ──X serveur DHCP

Symptôme : un seul sous-réseau ne reçoit plus de baux.
Pistes : relais, SVI/passerelle, ACL, étendue et journal du serveur.
~~~

Sous Windows Server, le module PowerShell DHCP peut fournir des informations de configuration si le rôle et les outils d'administration sont présents :

~~~powershell
Get-DhcpServerv4Scope -ComputerName DHCP-LAB-01
~~~

Cette commande est en lecture seule et requiert le module approprié ainsi que les permissions de gestion. Elle liste les scopes IPv4 du serveur ciblé. Si la commande n'est pas reconnue, le module peut ne pas être installé ; ne modifie pas les rôles du serveur pour contourner le problème. Consulte les événements DHCP du serveur et compare l'état de l'étendue et sa capacité.

### 3.2 Baux, inventaire et traçabilité

La gestion d'adresses IP (IPAM) maintient la relation entre sous-réseaux, plages, réservations, noms, usages et propriétaires. Un IPAM bien géré réduit les conflits et aide à expliquer l'utilisation d'une adresse à un instant précis. Il doit être aligné avec les données DHCP, DNS, l'inventaire d'actifs et les contrôles d'accès réseau. L'adresse IP d'aujourd'hui ne suffit pas à attribuer un événement de la semaine précédente si les baux ont changé.

Les journaux DHCP peuvent enregistrer les demandes, accords, refus, renouvellements et changements de configuration selon le produit. Sur Windows Server, la documentation du journal d'événements DHCP distingue les canaux opérationnels, administratifs, système, notification de filtres et audit. Les scopes modifiés doivent être rapprochés de la personne ou du processus autorisé, de l'heure et de la demande de changement.

## 4. Synchronisation horaire avec NTP

Le Network Time Protocol synchronise les horloges des machines avec des serveurs de temps. L'heure exacte est essentielle pour les certificats, les tickets Kerberos, les logs, les bases de données, les tâches planifiées et les corrélations de sécurité. Un système qui dérive peut créer des erreurs d'authentification et rendre une investigation chronologique peu fiable.

~~~text
Référence de temps
      │ NTP
      ▼
Serveur de temps interne
      │ NTP
      ├──► postes
      ├──► serveurs
      ├──► équipements réseau
      └──► collecteurs / plateformes de journalisation
~~~

La hiérarchie de temps doit être documentée. Les appareils internes peuvent synchroniser à partir d'une ou plusieurs références fiables et distribuer le temps aux clients. Ne configure pas chaque serveur au hasard sur une source publique ; les politiques de réseau peuvent exiger une référence interne, des restrictions de sortie ou une stratégie spécifique dans un domaine Windows.

Une dérive peut être causée par une machine virtuelle mal configurée, une source inaccessible, un pare-feu, une référence erronée, un service arrêté ou une batterie matérielle défaillante sur certains équipements. Sur Linux, la commande **timedatectl status** peut montrer si la synchronisation est activée, tandis que **chronyc tracking** fournit des détails si chrony est installé. Le résultat dépend des outils et du système réellement utilisés.

~~~bash
timedatectl status
chronyc tracking
~~~

Ne lance pas ces deux commandes en supposant qu'elles sont toutes deux installées. Elles sont des commandes de consultation. Si chrony n'existe pas, identifie le client de temps réel de la distribution. Sur des machines Windows, **w32tm /query /status** est une commande d'interrogation de l'état du service de temps lorsque le service Windows Time est utilisé.

### 4.1 Sécurité temporelle

Un attaquant qui influence l'heure peut compliquer l'analyse, déclencher des erreurs de certificats ou perturber l'authentification. Limite les serveurs autorisés à fournir le temps et surveille les changements de configuration. Compare les heures sur plusieurs sources indépendantes et consigne toute dérive. Dans une enquête, ne « corrige » pas silencieusement les timestamps originaux ; documente la valeur source, l'écart estimé et toute transformation dans une colonne distincte.

## 5. Authentification et annuaires : LDAP, Kerberos et AAA

L'authentification répond à « qui es-tu ? », tandis que l'autorisation répond à « que peux-tu faire ? ». La comptabilité ou accounting décrit les activités et sessions lorsque le système le supporte. Cette séparation est essentielle : une connexion peut être authentifiée avec succès et rester interdite pour une opération donnée.

### 5.1 LDAP et LDAPS

LDAP fournit un protocole d'accès à des services d'annuaire. Les applications peuvent rechercher des utilisateurs, groupes, attributs et objets de configuration. Le simple fait d'autoriser une connexion LDAP ne donne pas automatiquement un droit d'administration, mais un accès trop large aux attributs peut révéler des informations sensibles.

La sécurité dépend du mode d'authentification, de la confidentialité du transport, des droits de lecture et d'écriture, des comptes de service et des restrictions réseau. Lorsqu'une liaison simple transporte des identifiants sans protection TLS, les secrets peuvent être exposés sur un réseau non fiable. Utilise un mécanisme de protection approuvé et vérifie l'identité du serveur. LDAP sur TLS est souvent appelé LDAPS ; StartTLS peut aussi être disponible selon le serveur et le client. N'active pas une méthode en production avant d'avoir vérifié la compatibilité et les politiques.

### 5.2 Kerberos

Kerberos est un protocole d'authentification réseau fondé sur des tickets et une autorité de confiance. Dans un environnement Active Directory, un poste et un service échangent des tickets délivrés selon le domaine et ses règles. Les horloges sont importantes, les noms de service doivent correspondre et les secrets des comptes de service doivent être gérés correctement.

~~~text
Utilisateur / poste
      │ demande d'authentification
      ▼
KDC / contrôleur de domaine
      │ TGT
      ▼
Poste demande un ticket pour un service
      │
      ▼
KDC délivre ticket de service
      │
      ▼
Application valide le ticket et applique l'autorisation
~~~

Un ticket valide signifie qu'un mécanisme d'authentification a accepté les éléments du protocole dans ce contexte ; il ne prouve pas que chaque action ultérieure est légitime. Des erreurs d'horloge, un SPN incorrect, un mot de passe de compte de service changé sans mise à jour du secret consommateur ou des problèmes DNS peuvent empêcher l'authentification. Pour diagnostiquer, rassemble l'heure, le nom du service, l'identité, le contrôleur de domaine contacté et le résultat natif plutôt que de simplement désactiver Kerberos ou de retomber sur une méthode moins sûre.

### 5.3 RADIUS et TACACS+

RADIUS est utilisé notamment pour l'accès réseau, le Wi-Fi d'entreprise, les VPN et certains scénarios d'accès administratifs. Le client RADIUS — souvent un équipement réseau ou un contrôleur d'accès — envoie la demande au serveur d'authentification qui valide l'identité via un mécanisme configuré. La comptabilité peut enregistrer début, fin et durée d'une session selon le déploiement.

TACACS+ est également utilisé pour l'administration des équipements réseau, mais son modèle et ses fonctions diffèrent de RADIUS. Les choix dépendent des appareils, de la prise en charge, de la gestion des rôles et de la séparation des fonctions. Ne suppose pas que les deux protocoles sont interchangeables dans tous les environnements. Une architecture peut employer RADIUS pour l'accès réseau des utilisateurs et TACACS+ pour les commandes d'administration des routeurs et commutateurs, selon le produit.

~~~text
Administrateur ─► équipement réseau ─► serveur AAA
                      │                    │
                      │ auth request       ├── annuaire / source d'identité
                      │◄── accept/reject   ├── politique de rôle
                      │                    └── accounting si configuré
                      ▼
             CLI / session et commandes
                      │
                      ▼
              Syslog / audit central
~~~

Sécurise les échanges AAA avec un réseau de gestion, des secrets forts et uniques, des restrictions par client, un contrôle des droits d'administration et une journalisation fiable. RADIUS traditionnel ne chiffre pas nécessairement l'ensemble du contenu de tous les attributs comme le ferait un canal TLS ; comprends les propriétés exactes du mode utilisé. Évite de publier des shared secrets dans des scripts, tickets ou captures de configuration.

### 5.4 MFA et accès privilégié

L'authentification multifacteur limite le risque lié à un mot de passe volé, mais elle ne supprime ni l'hameçonnage, ni le détournement de session, ni l'abus d'un compte déjà authentifié. Les comptes d'administration devraient être nominatifs lorsque c'est possible, séparés des comptes ordinaires, limités dans le temps ou par rôle si la plateforme le permet, et surveillés.

Pour chaque identité technique, documente propriétaire, finalité, privilèges, services autorisés, méthode d'authentification, rotation des secrets et alertes associées. Les comptes de service ne devraient pas être utilisés pour des sessions interactives sans justification. Une authentification réussie depuis un hôte nouveau doit déclencher une vérification contextualisée plutôt qu'un verdict automatique.

## 6. SSH et administration à distance

SSH fournit un canal sécurisé pour l'administration distante et certains transferts de fichiers. Il s'appuie sur la confiance dans la clé d'hôte du serveur et sur une méthode d'authentification de l'utilisateur. Les clés publiques/privées évitent de devoir envoyer un mot de passe à chaque connexion, mais la clé privée doit être protégée et les clés d'hôte doivent être vérifiées.

Les mécanismes de durcissement courants consistent à limiter les comptes autorisés, réduire ou interdire la connexion directe du compte root si la procédure d'administration le permet, privilégier une authentification forte, maintenir le logiciel à jour, restreindre l'accès au réseau de gestion et conserver les journaux. Les paramètres exacts dépendent de la distribution et du fichier de configuration. N'applique pas un bloc de configuration copié sur un serveur sans lire le fichier existant et vérifier qu'une console ou un accès de secours est disponible.

~~~text
Administrateur
   │ client SSH + clé vérifiée
   ▼
Pare-feu / bastion d'administration
   │ source et compte autorisés
   ▼
sshd du serveur
   │ authentification, politique et journalisation
   ▼
Session de travail avec droits limités
~~~

Sur un laboratoire Linux, cette commande tente une connexion avec journal de diagnostic et délai limité. Utilise seulement un compte et un serveur que tu contrôles :

~~~bash
ssh -vv -o BatchMode=yes -o ConnectTimeout=5 labuser@server-lab.example
~~~

L'option de verbosité augmente les détails de diagnostic ; le mode BatchMode évite certaines invites interactives ; ConnectTimeout limite le temps d'établissement. La commande peut tout de même créer une tentative de connexion et un événement d'audit : n'en abuse pas sur les services partagés. Les messages peuvent révéler les noms d'hôte ou chemins de clés, donc masque les données sensibles avant de les partager.

Ne désactive jamais la vérification des clés d'hôte pour faire disparaître un avertissement de sécurité. Une modification de clé peut être légitime après reconstruction du serveur, mais elle doit être confirmée par un canal indépendant et documentée. Un avertissement inattendu doit être traité comme un problème de confiance à vérifier.

SFTP transporte des fichiers au-dessus de SSH et ne doit pas être confondu avec FTP traditionnel. FTP historique peut exposer des identifiants et données si aucun mécanisme de protection supplémentaire n'est utilisé. Préfère SFTP ou une autre méthode approuvée et chiffrée, limite les droits du compte de transfert et surveille les téléchargements et dépôts sensibles.

## 7. TLS, certificats et HTTPS

TLS protège un canal de communication, notamment en contribuant à la confidentialité et à l'intégrité et en authentifiant le serveur selon le mécanisme de certificats ou de clés utilisé. HTTPS associe HTTP à TLS. Un certificat n'est pas simplement un cadenas : le client doit vérifier la chaîne de confiance, les dates, les usages et surtout que l'identité du certificat correspond au nom du service contacté.

Une connexion peut échouer si le certificat est expiré, si la chaîne est incomplète, si le nom demandé ne correspond pas, si l'horloge est fausse, si l'autorité n'est pas approuvée ou si le client et le serveur ne trouvent aucun paramètre TLS commun. Dans une organisation qui utilise une autorité interne, les postes et applications doivent recevoir la racine de confiance selon la procédure prévue. Copier une racine inconnue dans le magasin de certificats pour faire passer un test est dangereux.

~~~text
Client demande https://service.example
       │
       ▼
Serveur présente son certificat
       │
       ├── dates valides ?
       ├── nom conforme au service ?
       ├── chaîne jusqu'à une racine approuvée ?
       ├── usages / contraintes cohérents ?
       └── paramètres TLS compatibles ?
                    │
             toutes vérifications requises passent
                    ▼
             canal TLS établi puis HTTP
~~~

TLS 1.3 est décrit par la spécification IETF la plus récente citée dans les références ci-dessous ; vérifie toujours les standards et versions supportés par les logiciels au moment du déploiement. Le choix du protocole ne suffit pas à prouver la configuration sûre : les certificats, clés, validation de nom, suites compatibles, reprise de session, terminaison TLS et mises à jour doivent être gérés.

### 7.1 Vérifier une connexion

Avec OpenSSL installé, la commande suivante examine une connexion TLS à un service que tu es autorisé à tester :

~~~bash
openssl s_client -connect service.example:443 -servername service.example -verify_return_error
~~~

Le paramètre SNI sélectionne le certificat adapté à un hôte virtuel. Le contrôle de retour d'erreur demande que la validation soit prise en compte. Le résultat fournit des informations sur le certificat, la chaîne, le protocole et le résultat de validation selon la version du client. Sur certaines versions, tu peux devoir utiliser des paramètres supplémentaires pour le magasin d'autorités approuvé ; consulte l'aide de l'installation locale.

Pour obtenir les en-têtes HTTP sans récupérer le corps, **curl -I** peut suffire :

~~~bash
curl -I https://service.example
~~~

Cette commande contacte réellement le service et le résultat dépend de la méthode HEAD prise en charge. Un code HTTP 403 ou 405 ne signifie pas nécessairement que TLS échoue : la connexion peut être sécurisée puis l'application refuser la requête. Sépare le résultat du handshake TLS du code HTTP et du résultat d'autorisation.

Sous Windows, une vérification de connectivité TCP peut utiliser :

~~~powershell
Test-NetConnection service.example -Port 443
~~~

Cela teste la connectivité TCP vers le port demandé, pas la validité du certificat ni le comportement HTTP. Si le test échoue, vérifie DNS, route, ACL, pare-feu et écoute serveur. Si le test réussit mais le navigateur affiche un avertissement de certificat, le diagnostic doit se déplacer vers TLS et la chaîne de confiance.

### 7.2 Cycle de vie des certificats

Chaque certificat doit avoir un propriétaire, un service cible, une date d'expiration, une autorité, un usage, un emplacement de clé privée, une méthode de renouvellement et un contrôle de réussite après renouvellement. La clé privée doit être restreinte ; elle n'a pas sa place dans le dépôt de code ou dans un ticket. Prévois une alerte suffisamment en avance de l'expiration afin d'éviter un renouvellement d'urgence.

Un certificat émis pour api.example.com ne valide pas automatiquement admin.example.com. Les certificats wildcard sont pratiques mais élargissent l'impact si leur clé privée est compromise. Le choix du périmètre doit être fondé sur l'architecture et la capacité de protéger la clé. Après un renouvellement, teste le nom, la chaîne, le protocole négocié et le service réel, pas uniquement le fichier sur disque.

## 8. HTTP, reverse proxy et API

HTTP transporte des requêtes et réponses applicatives. HTTPS ajoute le canal TLS, mais l'application doit encore appliquer authentification, autorisation, validation d'entrée, limites de débit, gestion des erreurs, protection CSRF lorsque pertinente et contrôle des secrets. Un retour 200 signifie que la requête a été traitée selon l'application ; il ne garantit pas que l'action métier est correcte ou que l'utilisateur avait accès à toutes les données attendues.

Un reverse proxy termine souvent TLS, fait du routage par hôte ou chemin, applique certaines politiques et transmet les requêtes aux serveurs backend. Cela crée un point de contrôle utile, mais il faut gérer les en-têtes de proxy, les adresses client, les certificats, les journaux et l'accès direct aux backends. Si les backends peuvent être contactés directement, un acteur peut contourner des contrôles appliqués seulement sur le proxy.

~~~text
Navigateur
   │ HTTPS et certificat public/interne
   ▼
Reverse proxy / WAF
   │ authentification / routage / journal
   ▼
API ou serveur web interne
   │ autorisation applicative
   ▼
Base de données / service métier
~~~

Les journaux HTTP devraient permettre, selon la politique de confidentialité, de distinguer heure, méthode, chemin normalisé, code de réponse, durée, identifiant de requête, client, utilisateur authentifié et backend. Évite de conserver systématiquement le corps de toutes les requêtes : il peut contenir mots de passe, jetons, données personnelles ou pièces jointes. Masque les secrets et limite l'accès aux journaux détaillés.

Les API devraient utiliser des identités distinctes par application, des droits minimaux, une gestion centralisée des secrets, un contrôle des permissions par ressource et des journaux d'audit. Un jeton dans une URL peut finir dans les journaux de proxy, l'historique du navigateur et les référents. Utilise les mécanismes d'authentification et d'autorisation prévus par l'API, ne partage pas les comptes d'intégration et fais tourner les secrets selon une procédure maîtrisée.

### 8.1 Diagnostic HTTP en couches

Un diagnostic robuste sépare : résolution de nom, connectivité TCP, négociation TLS, réponse HTTP, authentification, autorisation et logique métier. Le code 401 indique généralement qu'une authentification est nécessaire ou rejetée selon le contexte ; 403 indique généralement que le serveur refuse l'accès ; 404 peut cacher une ressource volontairement non disponible ou un chemin incorrect ; 5xx indique une erreur côté serveur ou intermédiaire. Les conventions de code ne remplacent pas la documentation de l'application.

Si une API retourne 502, recherche le journal du reverse proxy et celui du backend. Si TLS échoue avant qu'une requête HTTP ne soit envoyée, un journal d'application ne montrera peut-être aucun événement correspondant. La couche à laquelle apparaît le symptôme fournit une piste : commence là où l'échec se produit, puis remonte les dépendances.

## 9. Messagerie : SMTP, soumission, IMAP, SPF, DKIM et DMARC

Le courrier électronique dépend de plusieurs services. SMTP transporte le courrier entre clients et serveurs, ou entre serveurs ; la soumission des messages par les utilisateurs est souvent séparée du transport serveur-à-serveur. IMAP et POP permettent l'accès aux boîtes aux lettres, avec des variations selon les plateformes. Les configurations exactes d'authentification et de chiffrement doivent être vérifiées pour le serveur de messagerie.

SPF publie des informations de politique sur les hôtes autorisés à envoyer du courrier pour un domaine. DKIM signe certains éléments du message avec une clé dont la clé publique est publiée en DNS. DMARC permet au domaine de préciser comment les résultats d'alignement SPF/DKIM doivent être traités et de recevoir des rapports selon la configuration. Ces mécanismes ne garantissent pas que le contenu soit honnête, que l'expéditeur visible soit intuitif ou qu'un message ne soit pas une tentative d'hameçonnage.

~~~text
Application expéditrice
        │ soumission authentifiée
        ▼
Serveur d'envoi ── SMTP ──► serveur destinataire
        │                       │
        ├── SPF : autorisation du serveur émetteur
        ├── DKIM : signature vérifiable
        └── DMARC : alignement et politique du domaine
                                │
                                ▼
                     filtrage + boîte utilisateur
~~~

Les contrôles de sécurité comprennent le chiffrement, l'authentification, la protection contre les relais ouverts, les mises à jour, la gestion des comptes, le filtrage des pièces jointes et la surveillance des changements de configuration. Une configuration SPF ou DMARC erronée peut causer des rejets légitimes, tandis qu'une politique trop permissive facilite l'usurpation. Teste les modifications en fonction de l'architecture et de la documentation du fournisseur.

Les journaux de messagerie sont précieux pour relier message ID, expéditeur authentifié, destinataires, relais, résultat de livraison, filtrage et actions administratives. Évite de copier dans des outils non autorisés le contenu du message ou les pièces jointes. Les métadonnées suffisent parfois à établir la route ; le contenu ne doit être examiné que pour un besoin autorisé.

## 10. SNMP et supervision des équipements

SNMP permet de lire des mesures et, selon les droits, de modifier certaines valeurs des équipements. La supervision peut interroger périodiquement des compteurs ou recevoir des notifications. Les données sont souvent organisées selon des MIB et des identifiants d'objet. La supervision doit respecter le rôle d'un équipement et la sensibilité des informations exposées.

SNMPv1 et SNMPv2c s'appuient sur des communautés partagées qui ne fournissent pas le même modèle de sécurité que SNMPv3. SNMPv3 peut utiliser des modèles de sécurité qui apportent authentification et confidentialité selon la configuration. Il faut choisir un mode adapté aux capacités réelles de l'équipement et ne pas confondre « SNMPv3 activé » avec une configuration sûre si aucun contrôle d'identité, algorithme approprié ou restriction réseau n'est en place.

~~~text
Poller de supervision autorisé
        │ requête SNMP limitée
        ▼
Switch / routeur / serveur
        │ réponse avec compteurs et état
        ▼
Base de métriques / tableau de bord
        ▲
        └── traps ou notifications d'événements selon la configuration
~~~

Place les pollers dans un réseau d'administration, filtre les adresses sources, limite les vues accessibles et sépare les identités de lecture et d'écriture si le produit le permet. Utilise des secrets ou clés uniques, stockés dans un gestionnaire adapté, et surveille les changements de configuration. Les opérations d'écriture SNMP peuvent impacter l'équipement ; elles doivent être réservées à une automatisation approuvée et testée.

Les problèmes fréquents sont une communauté incorrecte dans les anciens systèmes, un utilisateur SNMPv3 mal configuré, une ACL d'agent, un pare-feu ou une différence de version de MIB. La supervision peut indiquer que l'hôte ne répond plus sans que l'hôte soit arrêté : une ACL peut bloquer le poller tandis que le plan de données continue de fonctionner. Corrèle avec les journaux de l'équipement et les tests de connectivité autorisés.

## 11. Syslog, audit et journalisation réseau

Syslog est un mécanisme courant pour transporter des événements générés par systèmes, applications et équipements réseau. Les formats historiques varient ; la spécification moderne décrit un en-tête, un timestamp, un nom d'hôte, un composant, un identifiant de processus, un identifiant de message et des champs structurés optionnels. La façon de transporter les messages est distincte du contenu du message.

~~~text
Serveur / pare-feu / switch / contrôleur
              │
              ├─ syslog local
              ├─ agent de transfert
              └─ transport sécurisé selon capacité
                          │
                          ▼
                    collecteur central
                          │
            parsing, enrichissement, horodatage
                          │
                          ▼
              stockage, règles et investigation
~~~

Le transport UDP historique peut perdre des messages et ne fournit pas un canal fiable et chiffré à lui seul. Lorsque le produit et l'architecture le permettent, privilégie un transport authentifié et protégé, tel que Syslog sur TLS. Vérifie la sémantique réellement supportée de la source et du collecteur ; un port ouvert ne démontre pas que le certificat ou l'identité sont corrects.

Chaque équipement devrait avoir une destination de journalisation documentée et un niveau de messages déterminé par les usages. Un niveau trop élevé peut noyer les événements utiles ; un niveau trop faible peut masquer un changement important. Les journaux d'authentification, de commandes administratives, de configuration, de changement de règle, de perte de connectivité et d'échec du service sont souvent prioritaires.

Les journaux doivent être envoyés vers une infrastructure dont les mêmes administrateurs réseau ne peuvent pas facilement effacer les copies centralisées. Les accès au collecteur, modifications des filtres et suppressions d'archives doivent également être journalisés. Conserve l'heure source et l'heure d'ingestion pour distinguer retard et temps réel.

## 12. Sécuriser les services : principes opérationnels

### 12.1 Minimiser l'exposition

Chaque service doit écouter uniquement sur les interfaces et zones nécessaires. Un serveur de gestion ne doit pas exposer sa console d'administration à tout le réseau utilisateur. Un résolveur récursif interne ne doit pas forcément répondre à des clients Internet. Un service d'annuaire doit limiter les accès à ses ports et opérations. Un collecteur Syslog doit accepter les équipements attendus au lieu de recevoir arbitrairement des messages de sources non vérifiées.

Le principe par défaut devrait être de refuser les flux qui ne sont pas nécessaires, mais une politique de filtrage doit être appliquée et testée par étapes. Pour un service critique, prépare l'accès de secours, une fenêtre de changement, des critères de retour arrière et une vérification après modification. Les règles trop larges rendent l'analyse de risque difficile et élargissent l'impact d'une compromission.

~~~text
Zone utilisateur ──► services publiés nécessaires
Zone serveurs ─────► dépendances internes explicitement listées
Zone admin ────────► bastion / ports d'administration autorisés
Zone supervision ──► pollers et collecteurs dédiés
Zone sécurité ─────► SIEM / sauvegardes protégées
Tout autre flux : refusé et journalisé selon la politique
~~~

### 12.2 Comptes, secrets et privilèges

Les comptes de service doivent avoir une finalité claire et des permissions limitées. Évite le partage d'identités d'administration. Stocke les secrets dans un gestionnaire approuvé, définis le propriétaire, la rotation et la procédure de révocation. Une rotation ne doit pas être effectuée sans identifier toutes les applications qui utilisent le secret, sinon un incident de disponibilité peut en résulter.

Les journaux peuvent accidentellement contenir des mots de passe, jetons ou clés. Limite leur accès, masque les valeurs sensibles à la source lorsque c'est approprié et examine les exports ou tickets où elles auraient été copiées. Si un secret est exposé, traite-le selon la procédure de gestion des secrets et d'incident ; supprimer le texte d'un tableau de bord ne révoque pas la clé déjà divulguée.

### 12.3 Disponibilité et reprise

La disponibilité exige surveillance, capacité suffisante, sauvegarde de configuration et procédure de restauration. Une redondance mal configurée peut répliquer une mauvaise configuration ou partager une dépendance unique. Vérifie l'indépendance des chemins réseau, de l'alimentation, des certificats et de la gestion DNS. Pour les services essentiels, teste la reprise en laboratoire et documente le comportement attendu lors d'une panne de nœud, de lien ou de dépendance.

Une bonne supervision contrôle à la fois le processus, le port, l'opération et la qualité de la réponse. Un processus actif peut être bloqué ; un port accessible peut renvoyer une erreur applicative ; un test HTTP 200 peut venir d'une page de maintenance sans accès à la base métier. Définis un contrôle adapté à la fonction réelle du service.

~~~text
État du service
   ├── processus présent ?
   ├── port attendu en écoute ?
   ├── connectivité depuis le bon réseau ?
   ├── échange protocolaire valide ?
   ├── authentification et autorisation testables ?
   └── journalisation et supervision fonctionnelles ?
La santé complète ne se résume pas à un seul voyant vert.
~~~

## 13. Dépannage : méthode reproductible

Un bon dépannage réduit l'incertitude avec des tests ciblés. Décris le symptôme exact, le périmètre touché, l'heure de début, le dernier changement et le résultat attendu. Détermine s'il s'agit d'un seul client, d'un sous-réseau, d'un serveur ou de tout le service. Compare un cas qui fonctionne et un cas en échec, si c'est sûr et pertinent.

Procède des couches basses vers les fonctions hautes : résolution de nom, route et connectivité, écoute, établissement du protocole, échange TLS si présent, authentification, autorisation et opération applicative. Capture les preuves avant de changer la configuration. Une commande qui échoue doit être interprétée selon ce qu'elle teste réellement.

~~~text
Symptôme
  │
  ▼
Nom résolu correctement ?
  │ oui
  ▼
Route et TCP/UDP accessibles selon le protocole ?
  │ oui
  ▼
Service présent et version attendue ?
  │ oui
  ▼
Handshake / chiffrement valide ?
  │ oui
  ▼
Authentification, autorisation et données correctes ?
  │
  ▼
Logs + dépendances + changements récents
~~~

Une capture réseau peut aider mais doit respecter les autorisations, la confidentialité et les règles de conservation. N'enregistre pas le contenu complet des communications par défaut. Privilégie des filtres étroits, des durées courtes et des métadonnées utiles. La capture peut ne pas montrer ce qui s'est passé si le trafic est chiffré, si l'observation se fait au mauvais point ou si le flux est hors du segment surveillé.

### 13.1 Lire un résultat sans surinterpréter

Une résolution DNS réussie prouve qu'un résolveur a répondu à la requête, mais pas que le service cible est joignable. Un port TCP accessible prouve que la connexion TCP a pu s'établir à cet instant, pas que l'application est saine. Un certificat valide aide à authentifier le nom selon la chaîne et les règles du client, mais n'atteste pas que l'application est exempte de vulnérabilités. Un login réussi indique une authentification acceptée, pas une autorisation universelle.

Les états doivent être enregistrés avec leur environnement et leurs paramètres. Un test local sur le serveur ne teste pas la route depuis le VLAN utilisateur. Un test avec le compte administrateur ne reproduit pas les droits du compte métier. Des résultats comparables nécessitent le même nom, protocole, source, fenêtre temporelle et paramètres pertinents.

## 14. TP 1 — Diagnostiquer DNS, DHCP et NTP

### Objectif et prérequis

Ce TP vérifie le chemin de résolution, les paramètres d'adresse et l'état temporel. Il n'exige aucune plateforme payante. Il utilise une machine Windows ou Linux que tu contrôles et des commandes de consultation. Ne modifie pas la configuration pendant la collecte des observations.

### Étape A — DNS

Sur Windows :

~~~powershell
Resolve-DnsName portal.example.com -Type A
Get-DnsClientServerAddress -AddressFamily IPv4
~~~

Sur Linux, si les outils sont installés :

~~~bash
resolvectl status
dig portal.example.com A
~~~

Remplace le nom par un domaine de laboratoire approprié. Note le résolveur configuré, la réponse, le TTL et les erreurs. Pour isoler un résolveur, interroge-le explicitement avec l'adresse réelle du laboratoire et compare le résultat.

### Étape B — Paramètres DHCP et connectivité

Sur Windows, consulte la configuration IP :

~~~powershell
ipconfig /all
~~~

Examine adresse, masque, passerelle, serveurs DNS, bail et indication DHCP. N'utilise pas aveuglément les commandes qui libèrent ou renouvellent le bail sur une session distante : l'adresse pourrait changer et interrompre la connexion. Sur Linux, **ip address** et **ip route** montrent les interfaces et routes actuelles ; ils ne changent pas la configuration.

~~~bash
ip address
ip route
~~~

### Étape C — Temps

Sous Linux, consulte la synchronisation horaire disponible :

~~~bash
timedatectl status
chronyc tracking
~~~

Exécute **chronyc tracking** seulement si chrony est installé. Sous Windows, lorsque le service Windows Time est utilisé :

~~~powershell
w32tm /query /status
~~~

### Correction attendue

Si le nom se résout mais que la connexion échoue, la prochaine étape est de tester le port et le service, pas de modifier immédiatement le DNS. Si la passerelle ou le résolveur manque dans la configuration DHCP, examine l'étendue, les options et le relais du sous-réseau. Si l'horloge est désynchronisée, identifie la source de temps, la connectivité et le service utilisé. Note l'heure, l'hôte, la commande, le résultat, ce qu'elle prouve et ce qu'elle ne permet pas de conclure.

Le TP est réussi si tu peux expliquer à quel niveau apparaît le premier écart et identifier la source de preuve suivante. Aucun résultat fictif ne doit être écrit comme s'il provenait de ta machine.

## 15. TP 2 — Vérifier la confiance TLS d'un service

### Objectif

Vérifier la résolution, la connectivité TCP, le certificat et la réponse HTTP sans désactiver la validation de sécurité. Utilise un service de laboratoire ou une destination que tu es autorisé à tester. Les exemples doivent être adaptés à ton système.

### Étape A — Connectivité

~~~powershell
Resolve-DnsName service.example -Type A
Test-NetConnection service.example -Port 443
~~~

Cette étape vérifie la résolution et la connexion TCP. Un succès TCP ne valide pas le certificat et ne confirme pas que l'application fonctionne.

### Étape B — TLS et certificat

Avec OpenSSL installé :

~~~bash
openssl s_client -connect service.example:443 -servername service.example -verify_return_error
~~~

Observe le nom demandé, l'émetteur, les dates, la chaîne de certification, la version négociée et le résultat de vérification. Si le certificat appartient à une autorité interne, vérifie que le client dispose de la racine approuvée conformément au déploiement prévu. Ne contourne pas la validation pour déclarer le test réussi.

### Étape C — HTTP

~~~bash
curl -I https://service.example
~~~

Note le statut HTTP et les en-têtes pertinents, sans copier de cookies, jetons ou données personnelles dans un rapport public. Si TLS fonctionne mais que HTTP répond 403, cela signale un refus d'accès à la couche HTTP selon le service, et non nécessairement une panne du canal TLS.

### Correction attendue

Une correction distingue trois résultats : résolution et TCP ; négociation et validation TLS ; traitement HTTP. Si DNS et TCP réussissent mais le certificat échoue, vérifie le nom, la date, la chaîne et l'horloge. Si le handshake réussit mais que le serveur renvoie 5xx, examine les logs du proxy et du backend. Si l'accès est refusé, vérifie l'identité et les permissions au lieu d'assouplir le chiffrement.

Le TP est réussi lorsque la conclusion est fondée sur les résultats réels et que la procédure ne désactive aucun contrôle de validation.

## 16. TP 3 — Analyser une session SSH et les logs de service

### Objectif et précautions

Dans une VM Linux de laboratoire que tu contrôles, teste la connexion d'un utilisateur prévu et corrèle l'heure du client avec les logs de la machine. Ne tente pas de mots de passe multiples et n'utilise pas de compte inconnu sur un serveur partagé.

### Étape A — Diagnostic client

~~~bash
ssh -vv -o BatchMode=yes -o ConnectTimeout=5 labuser@server-lab.example
~~~

Remplace le compte et le nom par ceux fournis dans ton environnement. Le mode verbeux montre les étapes du client ; il peut exposer des chemins et noms d'hôte, donc masque-les avant de partager la sortie. Une erreur de clé d'hôte exige une vérification indépendante et non la désactivation du contrôle.

### Étape B — Journal du serveur

Sur le serveur de laboratoire, examine les événements du service en lecture seule. Selon la distribution, l'unité peut être ssh ou sshd :

~~~bash
sudo journalctl -u ssh --since "30 minutes ago" --no-pager
~~~

Si le service porte le nom sshd, adapte le filtre. Vérifie aussi la source locale de journalisation et les permissions. En cas d'accès refusé, utilise le compte d'administration autorisé du laboratoire.

### Étape C — Interprétation

Associe l'heure client et l'heure serveur, l'identité, la source, le résultat du handshake, la méthode d'authentification et le message de refus. Un refus peut venir d'une clé non autorisée, d'un compte désactivé, d'une politique sshd, d'une permission de fichier ou d'une configuration réseau. Chaque cause exige un correctif différent.

### Correction attendue

Le rapport doit décrire si la connexion TCP a été établie, si la clé d'hôte a été vérifiée, quelle méthode d'authentification a été tentée et quel événement serveur a été corrélé. Il ne doit pas présenter un seul message comme preuve de compromission. La réussite du TP signifie qu'on peut passer du symptôme client à une source serveur et expliquer la prochaine vérification sans modifier de paramètres en aveugle.

## 17. TP 4 — Cartographier et vérifier les flux d'un service

### Scénario

Une application interne se connecte à un annuaire pour authentifier les utilisateurs, à un résolveur pour trouver son endpoint, à un service de temps et à un collecteur de journaux. L'équipe observe que les connexions échouent après un changement de pare-feu. Le but est de produire une matrice de flux testable plutôt que d'autoriser tout le réseau.

### Étapes

1. Identifie le serveur applicatif, l'annuaire, le DNS, NTP et le collecteur dans le laboratoire.
2. Note les ports et protocoles réellement utilisés à partir de la documentation de la configuration.
3. Détermine le sens de chaque connexion et si elle est chiffrée.
4. Compare les règles existantes et le changement approuvé.
5. Exécute des tests ciblés depuis l'hôte source avec l'outil adapté.
6. Vérifie la réussite du protocole applicatif après l'ouverture du flux, pas uniquement le port.
7. Fais relire la règle par le propriétaire du service avant de proposer le déploiement.

### Exemple de matrice fictive

~~~text
Source       Destination        Fonction           Contrôle attendu
APP-LAB      DNS-LAB            résolution         ports DNS nécessaires
APP-LAB      ID-LAB             annuaire / tickets protocole approuvé et TLS si prévu
APP-LAB      NTP-LAB            heure              NTP depuis la source autorisée
APP-LAB      LOG-LAB            journalisation     transport sécurisé si supporté
ADMIN-LAB    APP-LAB            administration    bastion, compte autorisé, audit
~~~

### Correction

N'ouvre que les flux démontrés nécessaires. Si le DNS marche mais l'annuaire échoue, concentre le diagnostic sur le flux d'identité et ses paramètres. Si le port est accessible mais TLS échoue, inspecte la chaîne de certificat et les paramètres de service. Si l'application fonctionne mais les logs ne sont plus reçus, l'incident concerne le flux d'audit et doit être traité séparément.

La matrice doit inclure justification, propriétaire, durée de l'exception, journalisation et plan de retour arrière. Le TP est réussi si chaque flux est lié à une fonction métier, testable et révisable.

## 18. Exercices avec réponses expliquées

### Exercice 1 — DNS et connectivité

**Question :** Resolve-DnsName renvoie une adresse, mais le navigateur ne peut pas accéder au service. Que prouve la réponse DNS ?

**Réponse :** seulement qu'un résolveur a fourni une réponse à la requête. Il faut encore vérifier route, port, service, TLS, HTTP, authentification et autorisation. La résolution réussie ne prouve pas la disponibilité de l'application.

### Exercice 2 — Port ouvert

**Question :** un test TCP vers le port 443 réussit. Peut-on conclure que le certificat est valide ?

**Réponse :** non. Le test établit une connexion TCP, pas une validation TLS. Il faut effectuer un handshake TLS et vérifier nom, dates, chaîne et confiance du client.

### Exercice 3 — DNSSEC

**Question :** quel problème DNSSEC cherche-t-il principalement à traiter, et que ne fait-il pas ?

**Réponse :** DNSSEC fournit des mécanismes d'authenticité d'origine et d'intégrité des données DNS signées. Il ne chiffre pas les noms demandés et ne remplace pas le contrôle d'accès, le filtrage ou la protection complète contre le déni de service.

### Exercice 4 — DoH et logs internes

**Question :** pourquoi une organisation doit-elle gérer l'usage de résolveurs DoH externes ?

**Réponse :** ils chiffrent la communication vers le résolveur, mais peuvent contourner les journaux et politiques des résolveurs internes. Il faut aligner les paramètres des terminaux avec le besoin de confidentialité, d'observabilité et de contrôle.

### Exercice 5 — DHCP et adresse historique

**Question :** une IP était associée à un poste hier. Peut-on attribuer avec certitude une connexion d'aujourd'hui au même poste ?

**Réponse :** non. Les baux peuvent expirer ou l'adresse être réattribuée. Rapproche le timestamp, les baux DHCP, l'identité du port ou du Wi-Fi et les journaux du client.

### Exercice 6 — NTP

**Question :** des événements semblent inversés dans le temps sur deux serveurs. Quelle hypothèse faut-il vérifier ?

**Réponse :** la dérive ou le fuseau de leurs horloges et le retard d'ingestion. Conserve les timestamps originaux, vérifie la synchronisation et documente tout décalage avant d'établir la chronologie.

### Exercice 7 — LDAP

**Question :** qu'est-ce qu'un accès LDAP réussi prouve ?

**Réponse :** qu'une opération d'accès à l'annuaire a été acceptée dans le contexte de la session et des permissions. Cela ne signifie pas que l'identité peut lire ou modifier tous les objets. Vérifie le type de bind, le transport et l'autorisation sur l'opération.

### Exercice 8 — Kerberos

**Question :** pourquoi un décalage horaire peut-il perturber Kerberos ?

**Réponse :** Kerberos utilise des timestamps et des tickets soumis à des contraintes temporelles. Une dérive peut conduire au rejet d'échanges même si le mot de passe est correct. Vérifie NTP, DNS, le service cible et le contrôleur de domaine.

### Exercice 9 — SSH et clé d'hôte

**Question :** le client affiche un changement inattendu de clé d'hôte. Est-il prudent de désactiver la vérification ?

**Réponse :** non. Vérifie le changement via un canal indépendant et confirme la nouvelle clé. L'avertissement peut être dû à une reconstruction légitime, mais peut aussi signaler que le client atteint un autre système.

### Exercice 10 — TLS valide mais HTTP 403

**Question :** que signifie généralement ce résultat ?

**Réponse :** le canal TLS peut être établi et le serveur HTTP refuse l'accès selon sa politique. Examine identité, rôle, ressource, proxy et journaux applicatifs. Ne désactive pas TLS pour corriger un refus d'autorisation.

### Exercice 11 — RADIUS vs SNMP

**Question :** quelle est la différence de fonction principale entre RADIUS et SNMP ?

**Réponse :** RADIUS est employé pour des échanges d'authentification et parfois de comptabilité d'accès réseau ; SNMP sert notamment à consulter ou gérer des données d'équipement. Leur sécurité et leurs journaux doivent être conçus selon le rôle réel.

### Exercice 12 — Syslog UDP

**Question :** pourquoi UDP peut-il être insuffisant pour des logs critiques transportés vers un collecteur ?

**Réponse :** UDP n'offre pas à lui seul de garantie de livraison ni de confidentialité. Selon le support de la source, un transport fiable et protégé comme Syslog sur TLS est préférable. Il faut aussi mesurer pertes, retards et erreurs de réception.

### Exercice 13 — Service de courrier

**Question :** SPF, DKIM et DMARC garantissent-ils qu'un message est honnête ?

**Réponse :** non. Ils contribuent à contrôler l'autorisation d'émission, une signature et l'alignement de domaine. Un message peut réussir ces contrôles et rester frauduleux ou trompeur ; d'autres contrôles et l'analyse du contexte sont nécessaires.

### Exercice 14 — SNMPv3 activé

**Question :** l'activation de SNMPv3 garantit-elle une configuration sécurisée ?

**Réponse :** non. Il faut vérifier le modèle de sécurité, l'authentification, la confidentialité, la gestion des clés, les vues accessibles et les ACL. La version de protocole seule ne remplace pas une revue de configuration.

### Exercice 15 — Service actif mais indisponible

**Question :** le processus est actif, mais le service n'effectue plus l'opération attendue. Quelle suite de diagnostic est pertinente ?

**Réponse :** vérifie port, protocole, dépendances, saturation, authentification, base de données et logs applicatifs. Un processus actif n'implique pas une fonction saine ; le contrôle doit tester une opération adaptée au service.

### Exercice 16 — Changement de pare-feu

**Question :** une nouvelle règle de pare-feu rétablit la connectivité en autorisant toute la plage de serveurs vers tous les ports. Est-ce une solution satisfaisante ?

**Réponse :** non. Elle résout peut-être le symptôme mais ouvre un accès excessif. Identifie le flux exact, la destination, le port, le sens, le propriétaire et les dépendances ; applique une règle minimale avec tests et retour arrière.

### Exercice 17 — Certificat expiré

**Question :** peut-on accepter un certificat expiré si la connexion est interne ?

**Réponse :** pas comme solution durable. L'expiration empêche la validation normale et peut signaler une défaillance de gestion des certificats. Vérifie la chaîne et le propriétaire, renouvelle selon la procédure et teste après renouvellement sans désactiver les contrôles.

### Exercice 18 — Port DNS inaccessible

**Question :** le test d'un port UDP DNS échoue. Cela prouve-t-il que le serveur DNS est arrêté ?

**Réponse :** non. Une sonde générique peut ne pas recevoir la réponse attendue, le trafic peut être filtré ou le service peut ne répondre qu'à certains clients. Utilise une requête DNS réelle vers le résolveur autorisé et inspecte les logs et règles du chemin.

## 19. Défi final — Diagnostiquer une panne de service et un risque de confiance

### Situation

Dans un laboratoire fictif, plusieurs utilisateurs ne parviennent plus à ouvrir une application interne après une modification réseau. Les observations suivantes ont été consignées :

~~~text
08:15Z  Les postes du VLAN 20 obtiennent une adresse DHCP
08:16Z  Resolve-DnsName renvoie une adresse pour app.lab.example
08:17Z  Test-NetConnection app.lab.example -Port 443 réussit
08:18Z  Le navigateur signale un problème de certificat
08:20Z  Le journal proxy montre des connexions TLS échouées pour ce nom
08:22Z  L'équipe constate qu'un second résolveur renvoie une adresse différente
~~~

Ces observations sont inventées pour l'exercice. Elles indiquent des résultats à vérifier, et non une preuve d'attaque. Le point important est de distinguer le problème de résolution, le port accessible, l'identité TLS et les modifications qui ont eu lieu.

### Travail demandé

1. Déterminer ce que chaque observation prouve et ne prouve pas.
2. Proposer un ordre de vérification sans modifier la production.
3. Lister les journaux et changements à inspecter.
4. Décrire les risques d'ignorer l'avertissement de certificat.
5. Écrire un rapport avec des hypothèses et une prochaine action testable.

### Correction pas à pas

**Étape 1 — DHCP.** Le fait que les postes obtiennent une adresse ne prouve pas que toutes les options DHCP sont correctes. Vérifie l'adresse, la passerelle, le résolveur et le bail, puis compare le scope du VLAN 20 avec la configuration approuvée.

**Étape 2 — DNS.** Une réponse DNS existe pour le nom demandé, mais deux résolveurs renvoient des adresses différentes. Cela peut venir du cache, d'une architecture à vues distinctes, d'un changement récent ou d'une configuration incohérente. Compare les serveurs faisant autorité, le TTL, l'enregistrement, la zone et l'heure du changement. Ne remplace pas immédiatement l'entrée sans identifier le résolveur à utiliser.

**Étape 3 — TCP.** Le port 443 répond depuis le poste testé. Cela ne vérifie pas le certificat ni l'application. La connectivité TCP peut être vers une autre machine à cause de la réponse DNS différente.

**Étape 4 — TLS.** L'avertissement de certificat et les échecs TLS doivent être examinés avant de continuer. Vérifie le nom présenté, les dates, la chaîne, le SNI et l'adresse de destination. N'accepte pas le certificat ni ne désactive la validation comme contournement.

**Étape 5 — Journaux.** Récupère les événements DNS d'audit, journaux du proxy, historique de changement de pare-feu et certificats, logs de l'application, horodatages et tickets de changement. Rapproche les heures en tenant compte des fuseaux et retards de livraison.

**Étape 6 — Hypothèses.** La cause peut être un changement DNS autorisé non propagé, un cache ancien, un certificat renouvelé avec le mauvais nom, une mauvaise terminaison TLS du proxy ou une modification non approuvée. Les informations actuelles ne suffisent pas à affirmer une compromission.

**Étape 7 — Action contrôlée.** Reproduis le test sur un poste de laboratoire qui utilise explicitement le résolveur approuvé. Compare les réponses et la validation TLS, puis examine les changements. Propose un correctif minimal avec fenêtre, validation par le propriétaire et retour arrière.

**Exemple de rapport :** « Les clients du VLAN 20 reçoivent une adresse et peuvent établir une connexion TCP au port 443, mais la validation TLS échoue. Deux résolveurs fournissent des adresses différentes. Le lien entre la modification réseau et la différence DNS n'est pas encore établi. La prochaine étape est de comparer les réponses autoritatives, les TTL, les journaux de changement et le certificat présenté par chaque destination. Aucune validation de certificat ne doit être contournée pendant l'enquête. »

Le défi est réussi si la conclusion ne confond pas résolution, TCP, TLS et HTTP, préserve les preuves et propose une vérification précise qui peut être exécutée dans le laboratoire.

## 20. Checklist opérationnelle de sécurisation des services

Avant d'exposer un service :
- Son propriétaire, son usage et les clients autorisés sont documentés.
- Les interfaces d'écoute et les flux nécessaires sont identifiés.
- Le pare-feu limite source, destination, protocole et port au besoin.
- L'authentification et l'autorisation sont testées séparément.
- La version et la configuration sont maintenues selon la politique.
- Le chiffrement et l'identité du serveur sont validés quand applicables.
- Les comptes, secrets et certificats ont un propriétaire et une rotation.
- Les journaux et contrôles de santé sont centralisés et testés.
- Une procédure de changement et de retour arrière est définie.

Pour les services fondamentaux :
- DNS : zones, autorité, résolveurs, TTL, transferts et changements sont contrôlés.
- DHCP : étendues, options, relais, baux et serveurs autorisés sont vérifiés.
- NTP : hiérarchie de temps, sources et dérive sont surveillées.
- LDAP/Kerberos/AAA : droits, protocoles, clients et comptes techniques sont documentés.
- SSH : clés d'hôte, comptes autorisés, accès de gestion et logs sont contrôlés.
- TLS : nom, dates, chaîne, version négociée et renouvellement sont surveillés.
- SNMP : version, sécurité, vues, secrets et pollers autorisés sont définis.
- Syslog : transport, destination, perte, retard et intégrité sont contrôlés.
- Messagerie : authentification, chiffrement et configuration de domaine sont revus.

Après un changement :
- Tests de la fonction réelle depuis le réseau source approprié.
- Résultats avant/après et horodatages consignés.
- Logs de service consultés pour confirmer l'effet.
- Flux non nécessaires supprimés selon le processus.
- Exceptions temporaires expirées et configurations mises à jour.
- Contrôle de supervision validé avant de clore le changement.

## 21. Glossaire

**AAA :** authentification, autorisation et comptabilité des sessions ou activités, selon le système.

**Autoritatif DNS :** serveur qui publie les données de la zone dont il a l'autorité.

**Bail DHCP :** attribution temporaire d'une adresse et de paramètres réseau à un client.

**DoH :** DNS transporté par HTTPS, protégeant le canal jusqu'au résolveur.

**DoT :** DNS transporté par TLS, protégeant le canal jusqu'au résolveur.

**DNSSEC :** extensions qui vérifient l'origine et l'intégrité des données DNS signées ; ne chiffre pas les requêtes.

**IPAM :** gestion des adresses IP, sous-réseaux, réservations et affectations.

**Kerberos :** protocole d'authentification à tickets reposant sur une autorité de confiance.

**LDAPS :** accès LDAP protégé par TLS dans les configurations qui l'emploient.

**MFA :** authentification multifacteur, combinant plusieurs catégories de preuve.

**NTP :** protocole de synchronisation horaire.

**RADIUS :** protocole utilisé pour des échanges d'authentification réseau et, selon la configuration, de comptabilité.

**Reverse proxy :** serveur intermédiaire qui reçoit des requêtes et les transmet aux backends selon la configuration.

**SFTP :** transfert de fichiers utilisant SSH, distinct du FTP traditionnel.

**SNMP :** protocole de supervision et de gestion des équipements.

**SOA :** enregistrement DNS qui porte des paramètres de zone.

**SPF :** mécanisme DNS indiquant des émetteurs autorisés pour le courrier d'un domaine.

**Syslog :** mécanisme et format de transport courant de messages de journalisation.

**TLS :** protocole de protection de canal, avec authentification selon le modèle utilisé.

**TTL :** durée de vie d'une valeur DNS dans le cache.

**Zone DNS :** ensemble de données DNS publié sous une autorité.

## 22. Références officielles et documentation

- IETF RFC Editor, DNS Concepts : RFC 1034, https://www.rfc-editor.org/rfc/rfc1034.html
- IETF RFC Editor, DNS protocol : RFC 1035, https://www.rfc-editor.org/rfc/rfc1035.html
- IETF RFC Editor, DNSSEC — introduction et limites : RFC 4033, https://www.rfc-editor.org/info/rfc4033/
- IETF RFC Editor, DNS over TLS : RFC 7858, mis à jour par RFC 8310, https://www.rfc-editor.org/info/rfc7858/
- IETF RFC Editor, DNS over HTTPS : RFC 8484, https://www.rfc-editor.org/rfc/rfc8484.html
- IETF RFC Editor, DHCPv4 : RFC 2131, https://www.rfc-editor.org/rfc/rfc2131.html
- IETF RFC Editor, DHCPv6 : RFC 8415, https://www.rfc-editor.org/rfc/rfc8415.html
- IETF RFC Editor, NTPv4 et mises à jour : RFC 5905, https://www.rfc-editor.org/rfc/rfc5905.html
- IETF RFC Editor, Kerberos V5 : RFC 4120, https://www.rfc-editor.org/rfc/rfc4120.html
- IETF RFC Editor, LDAP : RFC 4511, https://www.rfc-editor.org/info/rfc4511/
- IETF RFC Editor, RADIUS et ses mises à jour : RFC 2865, https://www.rfc-editor.org/info/rfc2865/
- IETF RFC Editor, SNMPv3 User-based Security Model : RFC 3414, https://www.rfc-editor.org/info/rfc3414/
- IETF RFC Editor, Syslog : RFC 5424, https://www.rfc-editor.org/rfc/rfc5424.html
- IETF RFC Editor, TLS 1.3 : RFC 9846, publié en juillet 2026 et remplaçant RFC 8446, https://www.rfc-editor.org/info/rfc9846/
- IETF RFC Editor, identité de service dans TLS : RFC 9525, https://www.rfc-editor.org/rfc/rfc9525.html
- OpenSSH, manuel officiel client, serveur et configuration : https://www.openssh.org/manual.html
- Microsoft Learn, journaux d'événements DHCP Server : https://learn.microsoft.com/en-us/windows-server/networking/technologies/dhcp/dhcp-server-events
- Microsoft Learn, journaux et diagnostics DNS Server : https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-logging-and-diagnostics
- OpenSSL, documentation officielle : https://docs.openssl.org/
- curl, documentation officielle : https://curl.se/docs/

Les RFC citées peuvent être mises à jour par d'autres documents. Vérifie l'état actuel et la version supportée par les produits avant tout déploiement. La présence d'un protocole dans une norme ne garantit pas qu'un appareil donné le mette en œuvre de façon complète ou sûre. Utilise la documentation correspondant à la version réellement installée et fais valider les changements sensibles.

## 23. Conclusion

La sécurité des services réseau commence par la compréhension de leur rôle et de leurs dépendances. DNS détermine où un nom mène, DHCP fournit des paramètres d'accès, NTP aide à maintenir une chronologie cohérente, les protocoles d'identité contrôlent qui accède, TLS protège les échanges, les outils d'administration permettent les opérations contrôlées et les services de journalisation rendent les comportements vérifiables.

Une configuration sûre doit limiter l'exposition, appliquer l'authentification et l'autorisation, protéger les secrets, surveiller les changements et conserver des journaux exploitables. Le diagnostic doit progresser couche par couche et utiliser les preuves, sans ouvrir aveuglément les ports ni désactiver la validation des certificats pour faire disparaître une erreur.

## 24. Scénarios complémentaires de dépannage

Pour chaque cas, distingue le fait observé, l'hypothèse, l'information manquante, le test contrôlé et la solution minimale. L'objectif est un diagnostic vérifiable plutôt qu'une conclusion automatique d'incident.

Fin du cours.
