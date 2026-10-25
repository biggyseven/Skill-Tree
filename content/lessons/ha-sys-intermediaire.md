# Clusters Linux Avancés
## Cours intermédiaire — Keepalived, IPVS, HAProxy, Pacemaker, Corosync et DRBD

## 1. Présentation du cours

### 1.1 Objectif général

Dans le niveau débutant, tu as découvert le principe de la haute disponibilité, les adresses IP virtuelles, Keepalived, VRRP, Pacemaker et les premières notions de quorum et de fencing.

Le niveau intermédiaire approfondit ces mécanismes afin de construire des infrastructures plus complètes, capables de gérer plusieurs serveurs, plusieurs ressources et différents types de panne.

Nous allons notamment étudier trois architectures :

1. **Haute disponibilité réseau** : deux instances Keepalived se partagent la responsabilité d’une adresse IP virtuelle.
2. **Équilibrage de charge** : Keepalived et IPVS répartissent le trafic entre plusieurs serveurs applicatifs, tandis que des contrôles de santé identifient les serveurs indisponibles.
3. **Cluster de ressources** : Pacemaker et Corosync coordonnent plusieurs ressources, leurs dépendances, leur placement et leur récupération après incident.

Nous étudierons également DRBD, qui permet de répliquer des périphériques de stockage par blocs entre des machines Linux, et HAProxy, qui fournit un équilibrage de charge applicatif particulièrement adapté aux services HTTP et TCP.

Le but n’est pas simplement de multiplier les composants. Il est de comprendre quel mécanisme contrôle chaque ressource, quelles dépendances existent et comment éviter qu’une panne se transforme en incident général.

### 1.2 Compétences visées

À la fin de ce cours, tu devras être capable de :

- Concevoir une architecture de haute disponibilité correspondant à un besoin précis.
- Distinguer VRRP, IPVS, HAProxy, Pacemaker, Corosync et DRBD.
- Configurer une VIP Keepalived avec des contrôles de santé adaptés.
- Comprendre les priorités, la préemption et les changements d’état VRRP.
- Configurer un service d’équilibrage de charge de niveau 4 avec IPVS.
- Comparer NAT, Direct Routing et Tunneling pour IPVS.
- Configurer des contrôles de santé TCP et HTTP.
- Concevoir une architecture HAProxy protégée par une VIP.
- Administrer les ressources Pacemaker avec `pcs`.
- Définir des groupes, des contraintes d’ordre et des contraintes de placement.
- Comprendre le comportement des ressources en échec.
- Préparer le fencing et le quorum pour un cluster à plusieurs nœuds.
- Comprendre le rôle d’un témoin et de Corosync QDevice.
- Découvrir les principes d’intégration de DRBD et de Pacemaker.
- Planifier les mises à jour et les opérations de maintenance.
- Diagnostiquer des pannes réseau, applicatives et de cluster.
- Organiser la supervision, la sauvegarde et les tests de reprise.

### 1.3 Prérequis

Tu dois maîtriser les éléments suivants :

- Utilisation du terminal Linux.
- Installation des paquets.
- Gestion des services avec `systemctl`.
- Configuration de base des interfaces réseau.
- Adresses IPv4, sous-réseaux et routage.
- Résolution DNS.
- Pare-feu et ports réseau.
- Notions de TCP et UDP.
- Gestion des fichiers et des permissions.
- Notions de haute disponibilité et d’adresse virtuelle.
- Principes de Keepalived et Pacemaker vus au niveau débutant.

Les commandes seront principalement illustrées avec Ubuntu Server et des outils disponibles dans les distributions modernes.

Les versions, les noms de paquets, les agents de ressources et certaines syntaxes peuvent différer entre Ubuntu, Debian, Red Hat Enterprise Linux et ses dérivées. La documentation de la distribution installée doit toujours être vérifiée avant une mise en production.

### 1.4 Architecture pédagogique

Nous utiliserons deux environnements de laboratoire distincts. Cette séparation permet de ne pas mélanger les responsabilités des outils.

**Laboratoire A : Keepalived et équilibrage de charge**

| Élément | Valeur |
|---|---|
| Équilibreur principal | `LB1` |
| IP principale | `192.168.70.11` |
| Équilibreur de secours | `LB2` |
| IP de secours | `192.168.70.12` |
| VIP des clients | `192.168.70.100` |
| Réseau privé des applications | `192.168.80.0/24` |
| Serveur applicatif 1 | `192.168.80.21` |
| Serveur applicatif 2 | `192.168.80.22` |

Les équilibreurs auront une interface côté clients et une interface côté serveurs applicatifs dans le scénario NAT.

**Laboratoire B : Pacemaker et ressources**

| Élément | Valeur |
|---|---|
| Nœud 1 | `node1` |
| Nœud 2 | `node2` |
| Cluster | `app-cluster` |
| VIP applicative | `192.168.90.100` |
| Interface applicative | `ens18` |
| Service étudié | Nginx |
| Outil d’administration | `pcs` |

Les adresses sont fictives. Elles ne doivent être utilisées que dans un réseau de laboratoire qui t’appartient ou dans lequel tu es autorisé à effectuer ces tests.

**Précaution importante :** ne réutilise pas simultanément la même VIP dans deux architectures indépendantes.

## 2. Concevoir une architecture avant de configurer les outils

### 2.1 Identifier le service à protéger

La première question n’est pas « faut-il installer Keepalived ou Pacemaker ? ».

Il faut commencer par identifier le service et les défaillances que l’on veut traiter.

Exemple : un site Web interne doit rester accessible malgré la panne d’un serveur d’équilibrage.

Les risques comprennent :

- La panne d’un équilibreur.
- L’arrêt d’un serveur applicatif.
- Une erreur HTTP sur un backend.
- Une panne d’interface réseau.
- Une perte de communication entre les équilibreurs.
- Une erreur de configuration.
- Une saturation du CPU ou du stockage.
- Une perte de données applicatives.

Tous ces incidents ne sont pas traités par le même mécanisme.

### 2.2 Architecture de bout en bout

Une architecture Web peut être représentée ainsi :

```text
                      CLIENTS
                         |
                         v
                 VIP : 192.168.70.100
                         |
              +----------+----------+
              |                     |
              v                     v
          +--------+            +--------+
          |  LB1   |            |  LB2   |
          | actif  |            | secours|
          +--------+            +--------+
              |                     |
              +----------+----------+
                         |
                   Réseau applicatif
                         |
              +----------+----------+
              |                     |
              v                     v
          +--------+            +--------+
          | APP01  |            | APP02  |
          +--------+            +--------+
```

Keepalived peut protéger le point d’entrée en gérant la VIP.

IPVS ou HAProxy peut répartir le trafic entre plusieurs serveurs applicatifs.

La redondance des équilibreurs ne garantit pas à elle seule que les applications, les fichiers et les bases de données sont disponibles.

### 2.3 Repérer les points uniques de défaillance

Un point unique de défaillance est un composant dont la panne suffit à interrompre le service.

Exemples :

- Un seul équilibreur.
- Un seul commutateur réseau.
- Une seule alimentation.
- Un seul serveur de fichiers.
- Une seule base de données.
- Un stockage commun sans redondance.
- Un unique réseau de communication de cluster.

Ajouter un deuxième serveur ne supprime pas tous les points uniques de défaillance.

Il faut examiner l’architecture de bout en bout, y compris les réseaux, l’alimentation, le stockage, les dépendances applicatives et les mécanismes de restauration.

### 2.4 Définir le RTO et le RPO

Le **RTO** (*Recovery Time Objective*) correspond au délai maximal ciblé pour rétablir un service.

Le **RPO** (*Recovery Point Objective*) correspond à la perte de données temporelle acceptable.

Exemple :

| Service | RTO cible | RPO cible |
|---|---:|---:|
| Passerelle d’accès Web | 1 minute | Sans objet pour son état réseau, sous réserve des connexions |
| Serveur Web statique | 2 minutes | Selon le processus de publication |
| Application métier | 5 minutes | 1 minute |
| Base de données transactionnelle | Selon le besoin métier | Selon la réplication et les sauvegardes |

Ces valeurs sont des objectifs de conception, pas des garanties inhérentes aux logiciels.

Le RTO réel doit être mesuré pendant les tests. Le RPO dépend de la cohérence et de la fréquence de réplication des données.

## 3. Keepalived : maîtriser VRRP au niveau intermédiaire

### 3.1 Rappel du principe

Keepalived peut gérer une adresse virtuelle à l’aide de VRRP.

Plusieurs instances participent à une élection permettant de déterminer laquelle doit porter l’adresse virtuelle.

```text
                       Réseau clients
                            |
                            v
                    VIP 192.168.70.100
                            |
                    Instance active
                            |
                    +-------+-------+
                    |               |
                    v               v
                   LB1             LB2
                 priorité 120    priorité 100
```

Dans un scénario classique, LB1 est le détenteur habituel de la VIP, tandis que LB2 peut prendre le relais si LB1 devient indisponible ou si sa priorité effective devient inférieure à celle de LB2.

VRRP gère le rôle réseau. Il ne réplique pas automatiquement les données applicatives.

### 3.2 Pourquoi la priorité ne suffit pas

La priorité détermine l’instance préférée selon les règles VRRP, mais elle ne démontre pas que le service applicatif fonctionne correctement.

Considérons :

```text
LB1
|
+-- Linux fonctionne
+-- Interface réseau active
+-- Keepalived actif
+-- HAProxy arrêté
```

Si Keepalived ne surveille que les annonces VRRP et les interfaces, il peut considérer que LB1 fonctionne encore correctement.

Il est donc nécessaire d’associer un contrôle de santé au service que l’on veut protéger.

### 3.3 Surveiller une interface réseau

Keepalived permet de suivre des interfaces et d’influencer l’état ou la priorité d’une instance lorsqu’un composant suivi devient indisponible.

Dans une infrastructure comportant deux interfaces, l’une pour les clients et l’autre pour le réseau applicatif, il faut réfléchir aux conséquences d’une panne de chacune d’elles.

Schéma :

```text
LB1
|
+-- ens18 : réseau clients
|
+-- ens19 : réseau applicatif
```

Si `ens19` tombe en panne, la VIP peut rester accessible depuis le réseau clients alors que l’équilibreur ne peut plus joindre les serveurs applicatifs.

Le suivi des interfaces doit donc tenir compte des dépendances réelles.

### 3.4 Contrôles de santé avec `vrrp_script`

La directive `vrrp_script` permet d'exécuter un contrôle périodique.

Le script doit renvoyer un code de sortie permettant à Keepalived de déterminer si le contrôle est réussi.

Exemple de script pour vérifier HAProxy :

```bash
#!/bin/sh

systemctl is-active --quiet haproxy || exit 1

exit 0
```

Ce contrôle vérifie seulement que le service est considéré comme actif par systemd. Il ne prouve pas qu’il transmet correctement les requêtes à l’application.

Pour aller plus loin, le script peut tester un point de santé local configuré pour l’application.

Il ne faut cependant pas écrire un contrôle qui vérifie uniquement la VIP publique depuis le nœud actif : cela peut produire une dépendance circulaire ou un résultat difficile à interpréter.

### 3.5 Exemple de suivi d’un service

Sur LB1, on peut utiliser le principe suivant dans `/etc/keepalived/keepalived.conf` :

```conf
vrrp_script chk_haproxy {
    script "/usr/local/sbin/check_haproxy.sh"
    interval 2
    timeout 2
    fall 2
    rise 2
    weight -30
}
```

Puis l'associer à l'instance :

```conf
track_script {
    chk_haproxy
}
```

Dans cet exemple :

- `interval 2` : intervalle de vérification demandé.
- `timeout 2` : délai maximal de contrôle selon les options prises en charge.
- `fall 2` : nombre d’échecs consécutifs avant que l’état soit considéré comme dégradé.
- `rise 2` : nombre de succès consécutifs avant de considérer le contrôle rétabli.
- `weight -30` : pondération négative appliquée à la priorité lorsque le contrôle est en échec, selon le comportement configuré.

La priorité initiale de LB1 doit être suffisamment élevée pour qu'une dégradation suivie de cette pénalité modifie le comportement comme prévu.

Il faut vérifier les règles de suivi et de préemption de la version installée.

### 3.6 Éviter les scripts de contrôle dangereux

Les scripts exécutés par Keepalived doivent être simples, fiables et protégés.

Bonnes pratiques :

- Employer des chemins absolus.
- Éviter les commandes ambiguës dépendant du `PATH`.
- Gérer explicitement les erreurs.
- Définir un délai maximal.
- Limiter les opérations effectuées par le script.
- Protéger le fichier contre la modification par des utilisateurs non autorisés.
- Ne pas stocker de secrets en clair.
- Tester le code de sortie.
- Vérifier le comportement lorsque le service est arrêté puis redémarré.

Un contrôle qui renvoie toujours le code `0` donne une fausse impression de disponibilité.

Un contrôle qui échoue de manière aléatoire peut, quant à lui, provoquer des basculements inutiles.

### 3.7 Préemption et retour à l’état nominal

Lorsqu’un serveur principal revient après une panne, deux comportements sont possibles selon la configuration :

- Le serveur préféré peut récupérer la VIP.
- Le serveur de secours peut la conserver tant que son état reste acceptable.

Le choix est important.

Le retour automatique sur le serveur préféré peut être utile si celui-ci dispose de meilleures ressources. Toutefois, si le serveur est encore instable, plusieurs changements de rôle rapprochés risquent de perturber le service.

Une politique de retour doit donc tenir compte de la stabilité après reprise.

Il faut notamment tester le scénario suivant :

```text
LB1 actif
   |
   v
Panne de LB1
   |
   v
LB2 prend la VIP
   |
   v
LB1 redémarre
   |
   v
Contrôle de stabilité
   |
   v
Retour sur LB1 ou maintien sur LB2
selon la politique retenue
```

### 3.8 Détecter les changements d’état

Keepalived fournit des mécanismes de notification pouvant être utilisés pour signaler certaines transitions.

Il est possible de les exploiter pour :

- Envoyer une alerte.
- Écrire un message dans un journal.
- Déclencher une collecte de diagnostic.
- Notifier une plateforme de supervision.

Le script de notification ne doit pas bloquer le traitement de l’instance ni accomplir des opérations destructives sans contrôle.

Les alertes devraient indiquer au minimum le nœud, le rôle précédent, le nouveau rôle et l’heure de l’événement lorsque ces informations sont disponibles.

Documentation : [Guide officiel Keepalived](https://keepalived.org/documentation/user-guide/).

## 4. Keepalived et IPVS : équilibrer la charge réseau

### 4.1 VRRP et IPVS sont deux fonctions différentes

Keepalived possède deux grandes familles de fonctions :

**VRRP**

Gère la haute disponibilité d’une adresse virtuelle.

**IPVS**

Utilise la fonction Linux Virtual Server du noyau Linux pour distribuer du trafic réseau vers plusieurs serveurs réels.

IPVS fonctionne principalement au niveau transport, ce qui le rend adapté à certains scénarios TCP et UDP.

Ces deux mécanismes peuvent être utilisés séparément ou combinés.

### 4.2 Architecture avec un pool de serveurs

```text
                     CLIENTS
                        |
                        v
                VIP : 192.168.70.100
                        |
                        v
                  +-----------+
                  | Keepalived|
                  | IPVS      |
                  +-----------+
                        |
              +---------+---------+
              |                   |
              v                   v
          +--------+          +--------+
          | APP01  |          | APP02  |
          | .80.21 |          | .80.22 |
          +--------+          +--------+
```

La fonction IPVS sélectionne un backend en fonction de la politique de planification retenue et des vérifications de santé.

Si un backend échoue à ses contrôles, Keepalived peut le retirer du pool de serveurs réels, suivant le type de contrôle configuré.

### 4.3 Les algorithmes de répartition

Quelques algorithmes courants :

| Algorithme | Principe | Usage typique |
|---|---|---|
| `rr` | Distribution circulaire | Backends comparables |
| `wrr` | Distribution circulaire pondérée | Backends de capacités différentes |
| `lc` | Préférence pour le nombre minimal de connexions actives | Certaines charges variables |
| `wlc` | Least connections pondéré | Pools avec capacités différentes |
| `fo` | Basculement pondéré | Préférence pour un backend et secours |

Ces algorithmes ne mesurent pas nécessairement le temps réel d’exécution des requêtes applicatives.

Un serveur avec peu de connexions peut néanmoins être lent si ses requêtes sont coûteuses.

Le choix doit être validé avec les caractéristiques du trafic et de l’application.

### 4.4 Les méthodes de transmission IPVS

Les trois méthodes historiques principales sont :

**NAT**

L’équilibreur reçoit la requête et la transmet au serveur réel en réalisant les opérations de traduction nécessaires.

Le chemin retour doit être cohérent avec la configuration NAT.

**Direct Routing (DR)**

L’équilibreur transmet les requêtes vers les serveurs réels par un mécanisme de routage direct. Les serveurs répondent aux clients sans faire transiter tous les paquets retour par l’équilibreur.

Cette architecture exige une configuration réseau spécifique.

**Tunneling (TUN)**

L’équilibreur transmet les paquets via un tunnel IP vers les serveurs réels.

Cette méthode nécessite une conception adaptée au réseau et à la prise en charge des tunnels.

### 4.5 Choisir NAT pour le laboratoire

NAT est relativement simple à comprendre pour un laboratoire où les équilibreurs ont deux interfaces :

```text
Réseau clients
192.168.70.0/24
        |
        v
   LB1 / LB2
        |
Réseau applicatif
192.168.80.0/24
        |
        +----------+
        |          |
        v          v
      APP01      APP02
```

Dans ce scénario, les serveurs applicatifs sont placés sur le réseau privé.

Pour que l’équilibreur assure le routage IPv4 dans un scénario IPVS NAT, il faut activer le transfert IP et préparer le chemin retour.

Sur le laboratoire, le paramètre de transfert peut être activé temporairement avec :

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Pour conserver le paramètre après le redémarrage, configure une valeur persistante dans un fichier adapté de `/etc/sysctl.d/`, puis recharge les paramètres.

Exemple :

```text
net.ipv4.ip_forward = 1
```

L’activation du routage ne suffit pas, à elle seule, à garantir une architecture fonctionnelle. Les routes, les règles de pare-feu et le chemin retour des serveurs réels doivent être cohérents.

### 4.6 Exemple de configuration IPVS

Le bloc suivant illustre une configuration de service virtuel HTTP avec deux serveurs réels.

Il s'agit d'un exemple de laboratoire à intégrer dans une configuration Keepalived compatible, après avoir préparé les réseaux et la VIP.

```conf
virtual_server 192.168.70.100 80 {
    delay_loop 5
    lvs_sched wrr
    lvs_method NAT
    protocol TCP

    real_server 192.168.80.21 80 {
        weight 1

        TCP_CHECK {
            connect_timeout 3
            retry 2
            delay_before_retry 2
        }
    }

    real_server 192.168.80.22 80 {
        weight 1

        TCP_CHECK {
            connect_timeout 3
            retry 2
            delay_before_retry 2
        }
    }
}
```

Explications :

- `virtual_server` décrit le service virtuel et son port.
- `delay_loop` définit l’intervalle de contrôle du pool.
- `lvs_sched wrr` choisit une répartition pondérée.
- `lvs_method NAT` utilise le mode NAT.
- `protocol TCP` indique le protocole du service.
- `real_server` définit chaque backend.
- `weight` permet de pondérer les serveurs.
- `TCP_CHECK` vérifie la capacité d’établir une connexion TCP.

Un contrôle TCP ne prouve pas que l’application retourne une réponse correcte. Pour une application HTTP, un contrôle HTTP peut être plus représentatif de la santé applicative.

La configuration IPVS ne remplace pas la configuration VRRP qui doit assurer la haute disponibilité de la VIP de l’équilibreur.

Documentation : [Keepalived — Configuration et équilibrage](https://keepalived.org/documentation/user-guide/configuration-synopsis/).

### 4.7 Vérifier la configuration IPVS

Lorsque la configuration est chargée, les commandes suivantes peuvent aider :

```bash
sudo systemctl status keepalived
sudo journalctl -u keepalived --no-pager -n 100
```

Si `ipvsadm` est installé :

```bash
sudo ipvsadm -Ln
```

Cette commande présente les services virtuels IPVS et leurs serveurs réels.

Si la VIP n’est pas active ou si les serveurs réels ne sont pas présents, vérifie la configuration Keepalived, l’état de l’instance VRRP et les journaux.

### 4.8 Limites des contrôles IPVS

Un contrôle TCP vérifie l’ouverture d’une connexion sur le port cible.

Il ne valide pas nécessairement :

- Le contenu HTTP.
- L’authentification.
- L’accès à une base de données.
- La qualité des données renvoyées.
- La disponibilité de tous les modules applicatifs.

Le bon contrôle est celui qui détecte l’état important pour le service, sans ajouter une charge excessive ni créer des faux positifs.

## 5. HAProxy derrière une adresse virtuelle

### 5.1 Quand utiliser HAProxy ?

HAProxy est un équilibreur de charge et un proxy particulièrement adapté aux protocoles TCP et HTTP.

Il peut fournir des fonctions de niveau applicatif, telles que :

- La sélection d’un backend.
- Les contrôles de santé HTTP.
- La terminaison TLS selon la configuration.
- Les règles d’accès adaptées.
- Certaines stratégies de persistance.
- Des indicateurs et journaux de connexion.

IPVS travaille principalement au niveau transport ; HAProxy permet de prendre des décisions fondées sur des informations applicatives HTTP ou TCP.

Les deux technologies ne sont pas interchangeables dans tous les scénarios.

### 5.2 Architecture HAProxy hautement disponible

```text
                         CLIENTS
                            |
                            v
                     VIP 192.168.70.100
                            |
                 +----------+----------+
                 |                     |
                 v                     v
             +--------+            +--------+
             |  LB1   |            |  LB2   |
             | HAProxy|            | HAProxy|
             | actif  |            | secours|
             +--------+            +--------+
                 |                     |
                 +----------+----------+
                            |
                   Serveurs applicatifs
                      /           \
                     v             v
                   APP01         APP02
```

Dans cette architecture, Keepalived gère le point d’accès réseau, tandis que HAProxy distribue les requêtes.

La configuration des équilibreurs doit être cohérente.

### 5.3 Exemple de configuration HAProxy

L'exemple suivant est une base pédagogique pour un point d'entrée HTTP non chiffré dans un réseau de laboratoire.

Fichier typique :

`/etc/haproxy/haproxy.cfg`

```conf
global
    log /dev/log local0
    log /dev/log local1 notice
    maxconn 2000

defaults
    log global
    mode http
    option httplog
    timeout connect 5s
    timeout client 30s
    timeout server 30s

frontend http_in
    bind *:80
    default_backend web_servers

backend web_servers
    balance roundrobin
    option httpchk GET /healthz

    server app01 192.168.80.21:80 check
    server app02 192.168.80.22:80 check
```

Cet exemple suppose que les applications possèdent un endpoint `/healthz` adapté au contrôle.

Si cet endpoint n’existe pas, il faut utiliser une URL que l'application sait traiter correctement.

### 5.4 Comprendre les paramètres

`global` définit certains paramètres généraux du processus.

`defaults` fournit des paramètres communs aux sections suivantes.

`mode http` configure le traitement HTTP.

`timeout connect` définit le délai maximal de connexion au backend.

`timeout client` et `timeout server` définissent les délais applicables aux côtés client et serveur.

`frontend` décrit le point d'entrée.

`backend` contient les serveurs recevant les requêtes.

`balance roundrobin` distribue les nouvelles requêtes selon un algorithme circulaire, sous réserve des règles de fonctionnement et de santé.

`option httpchk GET /healthz` demande une vérification HTTP sur l'URL spécifiée.

`check` active les contrôles de santé pour le serveur concerné.

Les valeurs doivent être ajustées selon les applications et le volume réel de trafic. Les délais trop courts peuvent provoquer des erreurs sur des services normaux ; des délais trop longs peuvent ralentir la détection d'une panne.

### 5.5 Vérifier et recharger HAProxy

Avant de recharger une configuration, vérifie sa syntaxe.

Sur les versions de HAProxy qui prennent en charge ces options :

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
```

Si le résultat est valide, recharge le service :

```bash
sudo systemctl reload haproxy
```

Si le service ne prend pas en charge un rechargement dans l'environnement choisi, suis la procédure appropriée à la distribution.

Vérifie ensuite :

```bash
sudo systemctl status haproxy
```

Puis teste le point d'accès local et le point d'accès virtuel depuis un client approprié.

### 5.6 Le contrôle de santé et la disponibilité réelle

Le contrôle d'un endpoint HTTP est plus représentatif qu'un simple `ping`, mais il ne prouve pas forcément que toutes les fonctions du service sont disponibles.

Par exemple, si `/healthz` renvoie systématiquement `200 OK` même lorsque la base de données est inaccessible, HAProxy peut continuer à envoyer des requêtes à une application partiellement défaillante.

L'endpoint de santé doit être conçu avec une intention claire.

Il peut vérifier des dépendances importantes, mais une vérification trop lourde ou trop dépendante peut aussi éliminer inutilement plusieurs serveurs en même temps.

Documentation : [HAProxy — Contrôles de santé](https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/).

### 5.7 La disponibilité de l'équilibreur lui-même

Avoir deux serveurs applicatifs équilibrés ne protège pas automatiquement l'équilibreur.

C'est précisément l'intérêt de l'association entre Keepalived et HAProxy.

Le suivi de HAProxy peut influencer la priorité VRRP. Si le service d'équilibrage devient réellement indisponible sur LB1, la VIP peut basculer vers LB2 lorsque la politique de priorité le permet.

Il faut toutefois éviter un contrôle de santé qui se contente de vérifier que la VIP répond, car la VIP peut elle-même dépendre de l'état Keepalived.

### 5.8 Session utilisateur et état applicatif

HAProxy peut redistribuer les requêtes entre plusieurs serveurs. Cela ne signifie pas que les serveurs partagent automatiquement les sessions utilisateur.

Si une application conserve son état uniquement en mémoire locale, un utilisateur peut rencontrer un problème lorsque ses requêtes arrivent sur un autre backend.

Plusieurs approches sont possibles :

- Concevoir l'application pour être sans état côté serveur.
- Partager l'état dans un stockage adapté.
- Utiliser une persistance de session lorsque c'est justifié.
- Déployer une solution de session distribuée.
- Appliquer des règles d'architecture spécifiques à l'application.

La persistance sur un backend peut aider certains scénarios, mais elle ne remplace pas un mécanisme de réplication de l'état.

## 6. Architectures Keepalived et HAProxy à plusieurs couches

### 6.1 Séparer les responsabilités

Une infrastructure complète peut organiser les rôles ainsi :

```text
                      CLIENTS
                         |
                         v
                  VIP D'ENTRÉE
                         |
                 Keepalived / VRRP
                         |
                         v
                     HAProxy
                         |
                Contrôles HTTP actifs
                         |
              +----------+----------+
              |                     |
              v                     v
          Serveur A             Serveur B
              |                     |
              +----------+----------+
                         |
                         v
                 Base ou données
                 selon l'architecture
```

Dans une architecture où HAProxy est installé sur LB1 et LB2, la VIP peut se trouver sur l'équilibreur actif.

Les backends applicatifs conservent leurs propres adresses fixes.

### 6.2 Ne pas confondre la santé du backend et la santé de l’équilibreur

Trois niveaux de santé doivent être distingués :

1. **Santé de l’hôte** : le système fonctionne et peut communiquer.
2. **Santé de l’équilibreur** : le processus HAProxy fonctionne et accepte les connexions.
3. **Santé du backend** : l’application ciblée répond comme attendu.

Un contrôle efficace doit tenir compte du niveau qu'il cherche à protéger.

### 6.3 Effets d'une panne

| Incident | Réaction attendue selon la configuration |
|---|---|
| APP01 tombe en panne | HAProxy ou IPVS retire APP01 du pool après détection |
| LB1 tombe en panne | LB2 peut prendre la VIP |
| HAProxy s'arrête sur LB1 | Le contrôle peut réduire la priorité de LB1 |
| Un endpoint applicatif devient invalide | Le backend peut être retiré du pool |
| Le réseau applicatif tombe en panne | L'équilibreur peut rester joignable sans pouvoir traiter les requêtes |
| Tous les backends tombent en panne | Le point d'entrée peut rester en ligne alors que le service métier ne l'est plus |

Il faut déterminer la réaction souhaitée pour chaque incident et tester cette réaction.

## 7. Pacemaker : structurer une configuration de cluster

### 7.1 Rappel du fonctionnement

Pacemaker gère les ressources d'un cluster et peut les déplacer d'un nœud vers un autre selon leurs contraintes et les événements.

Corosync fournit la communication de cluster et les informations d'appartenance nécessaires.

`pcs` est un outil d'administration permettant de configurer les composants et les ressources.

```text
                    Administrateur
                          |
                          v
                         pcs
                          |
                          v
                      Pacemaker
                          |
                          v
                       Corosync
                          |
              +-----------+-----------+
              |                       |
              v                       v
            node1                   node2
              |                       |
              +-----------+-----------+
                          |
                          v
                 Ressources clusterisées
```

Le cluster doit être validé au niveau de la communication, du quorum, du fencing et des ressources avant d'héberger des services critiques.

### 7.2 Choisir la distribution

Sur Ubuntu Server, `pcs` est l'outil recommandé pour administrer les clusters Pacemaker depuis Ubuntu 23.04. Les versions antérieures et certaines distributions utilisent des procédures ou des outils différents.

Red Hat Enterprise Linux fournit également une documentation détaillée sur `pcs`, Pacemaker, Corosync et les mécanismes de fencing.

Il faut suivre la documentation de la distribution déployée, car les commandes disponibles et les politiques de support peuvent différer.

### 7.3 Installer les composants sur Ubuntu

Dans un laboratoire Ubuntu, les paquets usuels peuvent être installés ainsi :

```bash
sudo apt update

sudo apt install pacemaker corosync pcs resource-agents fence-agents
```

La disponibilité exacte des paquets et des agents dépend de la version et des dépôts de la distribution.

Vérifie le service d'administration :

```bash
sudo systemctl enable --now pcsd
sudo systemctl status pcsd
```

Chaque nœud doit disposer des composants compatibles nécessaires à l'infrastructure retenue.

### 7.4 Résolution DNS et noms des nœuds

Les nœuds doivent pouvoir résoudre les noms utilisés par l'administration.

Exemple de laboratoire :

```text
192.168.90.11 node1
192.168.90.12 node2
```

Cette résolution peut être fournie par le DNS ou, dans un environnement isolé, par `/etc/hosts`.

Vérifie :

```bash
getent hosts node1
getent hosts node2
```

La résolution doit être cohérente entre tous les nœuds et l'ordinateur d'administration.

### 7.5 Préparer l'authentification de `pcs`

Sur les installations qui utilisent `pcsd`, les procédures d'administration emploient habituellement le compte `hacluster`.

Il faut préparer son accès selon les recommandations de la distribution, protéger ses identifiants et éviter de partager inutilement les accès administratifs.

Sur les versions compatibles, l'authentification peut utiliser :

```bash
sudo pcs host auth node1 node2 -u hacluster
```

Si la commande n'est pas acceptée, consulte l'aide et la documentation correspondant à la version installée :

```bash
pcs host auth --help
```

Il ne faut pas copier une commande d'une ancienne version sans vérifier la syntaxe.

### 7.6 Créer le cluster

Après avoir préparé les nœuds, le réseau et l'authentification, la commande suivante illustre une création de cluster avec deux nœuds :

```bash
sudo pcs cluster setup app-cluster node1 node2 --start --enable
```

Cette syntaxe est utilisée par des versions modernes de `pcs`. Il faut vérifier les options disponibles sur le système installé.

La commande organise la configuration de Corosync et peut démarrer le cluster.

**Attention :** une création réussie ne signifie pas que le cluster est prêt pour la production. Il faut encore traiter le quorum, le fencing, les permissions, la sécurité et les ressources.

### 7.7 Vérifier l'état

```bash
sudo pcs status
```

Pour une vue plus détaillée, selon la version :

```bash
sudo pcs status --full
```

Pour consulter la configuration :

```bash
sudo pcs config
```

Les informations doivent permettre de vérifier :

- Les nœuds présents.
- L'état du cluster.
- Les ressources configurées.
- Les erreurs connues.
- Le comportement du quorum.
- Les opérations de récupération en cours.

Une fois les nœuds opérationnels, examine les journaux avant d'ajouter des ressources critiques.

## 8. Les contraintes Pacemaker

### 8.1 Pourquoi les contraintes sont importantes

Une application peut nécessiter plusieurs composants.

Exemple : une application métier a besoin d'un service de stockage, d'un service applicatif et d'une adresse virtuelle.

```text
Stockage disponible
        |
        v
Service applicatif actif
        |
        v
Adresse de service disponible
        |
        v
Accès des clients
```

Le cluster doit savoir :

- Quelles ressources doivent être actives.
- Dans quel ordre elles doivent démarrer.
- Sur quels nœuds elles peuvent fonctionner.
- Quelles ressources doivent rester ensemble.
- Comment traiter un échec.
- Quand une ressource peut être déplacée.

Pacemaker utilise des ressources, des groupes et des contraintes pour exprimer ces exigences.

### 8.2 Les contraintes de placement

Une contrainte de placement (*location constraint*) indique sur quels nœuds une ressource peut fonctionner ou quels nœuds sont préférés.

Exemple conceptuel :

```text
Application Web
|
+-- Préférence initiale : node1
|
+-- node1 indisponible :
       reprise possible sur node2
       si les autres conditions sont satisfaites
```

Sur un cluster opérationnel, une préférence peut être exprimée ainsi :

```bash
sudo pcs constraint location web-stack prefers node1=100
```

La préférence n'est pas nécessairement une interdiction absolue d'utiliser node2.

Il faut distinguer les scores positifs, les scores négatifs et les règles qui rendent un nœud inéligible.

### 8.3 Les contraintes d'ordre

Les contraintes d'ordre déterminent la séquence de démarrage et d'arrêt des ressources.

Exemple :

```text
Volume de données
       |
       v
Application métier
       |
       v
Adresse IP de service
```

La contrainte exacte doit correspondre aux dépendances réelles.

Si le service ne peut pas fonctionner sans son volume de données, ce volume doit être prêt avant le démarrage de l'application.

Il faut également anticiper l'ordre d'arrêt : une ressource dépendante ne doit pas rester active alors que sa dépendance critique a été retirée.

### 8.4 Les contraintes de colocation

La colocation indique que des ressources doivent fonctionner sur le même nœud ou respecter une relation de placement.

Exemple :

```text
node1
|
+-- Volume
+-- Application
+-- Adresse virtuelle
```

Si l'application utilise un système de fichiers local qui ne doit être monté que sur le nœud actif, l'application et la ressource de stockage doivent être coordonnées.

Une mauvaise colocation peut entraîner une application sur un nœud tandis que sa ressource de données reste indisponible ailleurs.

### 8.5 Les groupes de ressources

Un groupe permet de gérer plus simplement des ressources qui doivent être colocalisées et démarrer dans un ordre défini.

Exemple :

```text
Groupe web-stack
|
+-- Service Nginx
|
+-- Adresse virtuelle
```

Les ressources d'un groupe sont généralement colocalisées et démarrées dans l'ordre défini lors de leur ajout.

Elles sont arrêtées dans l'ordre inverse.

Le groupe est utile lorsque les ressources partagent réellement le même cycle de vie et le même besoin de placement.

Documentation : [Pacemaker — Groupes de ressources et contraintes](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/assembly_configuring-cluster-resources-configuring-and-managing-high-availability-clusters).

### 8.6 Exemple de création de ressources

Dans un cluster préparé et correctement protégé, une ressource d'adresse IP peut utiliser l'agent `IPaddr2`.

Exemple :

```bash
sudo pcs resource create web-vip \
    ocf:heartbeat:IPaddr2 \
    ip=192.168.90.100 \
    cidr_netmask=24 \
    nic=ens18 \
    op monitor interval=20s
```

Cette commande suppose que :

- L'adresse IP est libre.
- L'agent est disponible.
- L'interface existe sur les nœuds concernés.
- Le réseau est adapté.
- Le cluster dispose des mécanismes de sécurité et de fencing requis.

La ressource représente une adresse virtuelle gérée par Pacemaker.

### 8.7 Créer la ressource Nginx

Si l'agent systemd est disponible et adapté à la distribution :

```bash
sudo pcs resource create web-service \
    systemd:nginx \
    op monitor interval=30s
```

Le nom exact de l'unité et l'agent de ressource doivent être vérifiés sur les deux nœuds.

Cette ressource demande à Pacemaker de gérer Nginx. Il faut donc éviter de créer une deuxième méthode permanente et indépendante de gestion du même service.

### 8.8 Regrouper l'application et la VIP

Pour cet exemple, nous souhaitons que Nginx soit actif avant de rendre l'adresse de service accessible.

Le groupe est créé dans l'ordre suivant :

```bash
sudo pcs resource group add web-stack web-service web-vip
```

Dans ce groupe, Nginx démarre avant la VIP. Lors de l'arrêt du groupe, l'adresse est retirée avant l'arrêt du service.

Ce choix doit être adapté à l'application et testé. Dans certaines architectures, l'ordre correct peut être différent.

Vérifie la configuration :

```bash
sudo pcs resource config
sudo pcs status
```

### 8.9 Pourquoi la configuration doit être validée

Un groupe de ressources ne remplace pas la validation des prérequis.

Avant de l'utiliser en production, vérifie :

- Le fencing.
- Le quorum.
- Les nœuds disponibles.
- Les permissions.
- Les agents utilisés.
- Les chemins de stockage.
- Le comportement en cas d'échec.
- Les contraintes existantes.
- Les objectifs de reprise.

Un groupe syntaxiquement valide peut être opérationnellement inadapté si les dépendances sont mal conçues.

## 9. Gérer les erreurs et les récurrences de panne

### 9.1 Pourquoi Pacemaker conserve des informations d'échec

Pacemaker peut enregistrer des échecs d'opération et utiliser ces informations pour déterminer si une ressource doit être relancée, déplacée ou considérée comme temporairement indisponible.

Un échec ne doit pas être effacé aveuglément : il faut comprendre pourquoi il est arrivé.

Exemples :

- Le service a échoué au démarrage.
- Le contrôle de santé n'a pas répondu dans le délai.
- Le stockage n'était pas disponible.
- Un agent de ressource a échoué.
- La ressource ne pouvait pas être arrêtée.
- Le nœud n'était plus joignable.

### 9.2 Éviter les basculements répétitifs

Un service qui échoue fréquemment peut produire une succession de reprises et de déplacements.

Il faut examiner :

- La fréquence du contrôle de santé.
- Les seuils d'échec.
- La durée nécessaire au démarrage de l'application.
- Les dépendances.
- La stabilité du stockage.
- La charge du nœud.
- Les délais réseau.

Un contrôle trop strict peut signaler un incident temporaire comme une panne permanente.

Un contrôle trop permissif peut laisser une ressource défaillante active plus longtemps que prévu.

### 9.3 Examiner les états et les échecs

Commence par :

```bash
sudo pcs status --full
```

Selon la version, examine également l'état des ressources :

```bash
sudo pcs resource status
```

Les commandes de détail des échecs peuvent varier selon la version. Consulte l'aide de `pcs` pour la syntaxe disponible.

### 9.4 Nettoyer un état d'échec

Après correction de la cause, il peut être nécessaire de nettoyer l'état d'échec d'une ressource afin que le cluster puisse réévaluer son état.

Exemple :

```bash
sudo pcs resource cleanup web-service
```

Cette action peut permettre une nouvelle évaluation de la ressource. Elle ne corrige pas à elle seule la panne initiale.

Ne l'utilise pas comme une méthode de traitement automatique de tous les incidents sans consulter les journaux et l'état réel du service.

### 9.5 Redémarrage ou déplacement ?

Lorsqu'une ressource échoue, plusieurs actions sont possibles selon les contraintes et la politique de récupération :

- Réessayer sur le nœud actuel.
- Déplacer la ressource vers un autre nœud.
- Arrêter la ressource si les conditions ne sont pas réunies.
- Isoler un nœud si son état ne permet pas de garantir la sécurité des données.

Il faut définir le comportement en fonction du service et de ses données.

Un déplacement vers un autre nœud n'est pas toujours une bonne solution si le défaut provient d'une dépendance commune, comme un stockage hors service.

## 10. Quorum et fencing à un niveau intermédiaire

### 10.1 Rôle du quorum

Le quorum permet au cluster de déterminer si les membres en communication disposent des votes requis pour continuer à gérer les ressources.

Il est important notamment lorsqu'un réseau de communication tombe en panne sans que les serveurs eux-mêmes soient arrêtés.

```text
Avant l'incident

node1 <------ communication ------> node2


Après une partition réseau

node1                            node2
  |                                |
  |          communication perdue  |
  |                                |
  +----------X---------------------+
```

Les deux serveurs peuvent encore fonctionner localement. Le cluster doit néanmoins décider quelle partie peut continuer à exploiter les ressources partagées.

### 10.2 Pourquoi un cluster à deux nœuds demande une attention particulière

Avec seulement deux nœuds, la perte de communication entre eux pose un problème plus délicat qu'avec plusieurs membres et une majorité évidente.

Il faut concevoir une politique adaptée au nombre de votes et au scénario de panne.

Un mécanisme témoin peut contribuer à l'arbitrage selon la configuration du cluster.

Le témoin doit être disponible et indépendant des ressources qui pourraient tomber en panne simultanément avec le cluster.

### 10.3 Corosync QDevice

Corosync QDevice permet d'ajouter un mécanisme d'arbitrage externe à certaines architectures de cluster.

Le dispositif de quorum QDevice peut communiquer avec les nœuds et participer à la décision selon l'algorithme configuré.

Il peut être utile pour certains clusters comportant un nombre pair de membres, mais il ne doit pas être considéré comme un remplacement universel du fencing.

Le service QDevice doit être placé et dimensionné de manière réfléchie pour limiter les défaillances communes.

### 10.4 Le fencing protège les données

Le fencing, également appelé STONITH dans les environnements Pacemaker, permet d'isoler un nœud qui ne doit plus accéder aux ressources du cluster.

Le terme STONITH provient de *Shoot The Other Node In The Head*.

Il ne s'agit pas simplement de déclarer qu'un nœud est hors ligne dans une interface d'administration. Le mécanisme doit pouvoir l'isoler de manière fiable.

Exemples selon l'infrastructure :

- Arrêter ou redémarrer un serveur à travers son interface de gestion matérielle.
- Isoler un nœud via une API d'hyperviseur appropriée.
- Utiliser un mécanisme de fencing du stockage pris en charge.

### 10.5 La configuration de fencing est spécifique à l'environnement

Il n'existe pas une commande de fencing universelle valable pour tous les serveurs.

Le bon agent dépend notamment du matériel, du contrôleur d'alimentation et des mécanismes disponibles.

Avant de configurer une ressource de fencing, il faut vérifier :

- L'identité du nœud ciblé.
- La connectivité du dispositif.
- Les permissions utilisées.
- Le comportement de l'action demandée.
- Les journaux du dispositif.
- La possibilité de réussir l'isolation pendant un incident.
- Le retour à l'état normal après la reprise.

Les identifiants de gestion doivent être protégés. Ils ne doivent pas être exposés dans les historiques de terminal, les journaux partagés ou des scripts non protégés.

**Ne désactive pas le fencing sur un cluster de production pour contourner une erreur de configuration.** Sans isolation fiable, le cluster peut laisser deux nœuds utiliser simultanément des ressources incompatibles.

Documentation : [Ubuntu Server — Fencing des clusters Pacemaker](https://ubuntu.com/server/docs/explanation/high-availability/pacemaker-fence-agents/).

## 11. DRBD : réplication de stockage par blocs

### 11.1 Le problème du stockage

Jusqu'ici, nous avons surtout déplacé des rôles et des adresses réseau.

Mais une application a souvent besoin de données persistantes : documents, fichiers, journaux, bases de données ou fichiers de configuration.

Si les données sont stockées uniquement sur le disque local du nœud actif, le serveur de secours peut démarrer sans disposer des données attendues.

DRBD permet de répliquer des périphériques de stockage par blocs entre plusieurs hôtes Linux.

### 11.2 Principe de fonctionnement

```text
             NODE1
               |
          Volume local A
               |
               v
             DRBD
               |
      Réplication réseau
               |
               v
             DRBD
               |
          Volume local B
               |
             NODE2
```

DRBD peut présenter un périphérique bloc répliqué aux applications et au système de fichiers.

La réplication peut être utilisée avec un gestionnaire de cluster tel que Pacemaker pour coordonner le rôle actif, le montage du système de fichiers et le démarrage de l'application.

### 11.3 Single-primary

En mode single-primary, une seule instance est autorisée à être Primary à un instant donné dans les conditions normales de fonctionnement du mécanisme.

C'est une configuration courante lorsque l'application utilise un système de fichiers traditionnel qui ne prend pas en charge les accès concurrents simultanés depuis deux nœuds.

```text
NODE1
  |
  +-- DRBD Primary
  +-- Système de fichiers monté
  +-- Application active

NODE2
  |
  +-- DRBD Secondary
  +-- Système de fichiers non monté en écriture
  +-- Application inactive
```

Cette disposition permet au cluster de coordonner le transfert du rôle et l'accès aux données.

### 11.4 La réplication n'est pas synonyme de sauvegarde

Une suppression ou une corruption logique effectuée sur le nœud actif peut être répliquée vers le nœud secondaire.

DRBD réplique les blocs selon sa configuration, mais ne constitue pas à lui seul un historique de sauvegardes.

Il faut donc une stratégie de sauvegarde indépendante, avec des points de restauration conservés et des tests de récupération.

### 11.5 Les modes de réplication

DRBD propose différents protocoles et modes de réplication, selon les capacités de la version et les objectifs de l'infrastructure.

Le mode synchrone attend que l'écriture soit confirmée selon le protocole de réplication choisi.

Les modes asynchrones peuvent diminuer la latence de certaines opérations, mais ils présentent des compromis différents en matière de perte de données après incident.

Le choix dépend :

- De la latence réseau.
- De la bande passante.
- Du besoin de cohérence.
- De la capacité de stockage.
- Du RPO cible.
- Des performances de l'application.
- Du scénario de panne.

Il ne faut pas choisir un protocole uniquement parce qu'il est plus rapide dans un test isolé.

### 11.6 Préparer un volume DRBD

Le processus de préparation comprend généralement :

1. Créer des espaces de stockage adaptés sur les deux nœuds.
2. Vérifier que les périphériques choisis sont dédiés à DRBD.
3. Installer les outils DRBD compatibles avec la distribution et le noyau.
4. Préparer la connectivité réseau de réplication.
5. Définir la configuration du ressource DRBD.
6. Initialiser les métadonnées selon les instructions du projet.
7. Connecter les nœuds.
8. Vérifier l'état de synchronisation.
9. Confirmer la cohérence avant de monter le système de fichiers.
10. Intégrer la ressource au gestionnaire de cluster.

Le détail dépend de la version de DRBD, du noyau et des paquets installés.

### 11.7 Les commandes de diagnostic

Les outils DRBD comprennent notamment `drbdadm`.

Pour afficher l'état d'une ressource configurée :

```bash
sudo drbdadm status
```

Pour examiner une ressource spécifique, utilise le nom défini dans la configuration :

```bash
sudo drbdadm status r0
```

Ces commandes ne créent pas les volumes et ne corrigent pas une réplication défaillante. Elles permettent d'examiner l'état actuel.

### 11.8 Attention aux commandes d'initialisation

Les commandes qui initialisent les métadonnées ou créent des périphériques DRBD doivent être exécutées avec une grande prudence.

Une erreur sur le périphérique cible peut rendre des données inaccessibles ou détruire des informations existantes.

Avant une initialisation :

- Vérifie le nom du nœud.
- Vérifie le périphérique physique ou logique.
- Vérifie la capacité.
- Vérifie que le volume ne contient pas de données à conserver.
- Sauvegarde les informations nécessaires.
- Suis la procédure correspondant à la version de DRBD.
- Réalise d'abord l'opération en laboratoire.

Ne copie pas une commande destructive en remplaçant simplement le nom du volume par intuition.

### 11.9 Intégration de DRBD avec Pacemaker

Dans une architecture où Pacemaker gère DRBD, les transitions Primary/Secondary doivent normalement être contrôlées par l'agent de ressource prévu pour cette intégration.

L'application ne doit pas promouvoir ou rétrograder manuellement le stockage indépendamment du cluster en fonctionnement normal.

Le modèle de dépendances peut être :

```text
DRBD prêt et promu
        |
        v
Système de fichiers monté
        |
        v
Service applicatif démarré
        |
        v
Adresse virtuelle activée
```

Les opérations de démontage et d'arrêt doivent respecter les dépendances inverses.

### 11.10 Le système de fichiers doit correspondre au modèle d'accès

Un système de fichiers classique tel qu'ext4 ou XFS ne doit pas être monté simultanément en lecture-écriture sur deux nœuds indépendants sur le même périphérique partagé, à moins qu'une architecture spécialement prévue et prise en charge garantisse la coordination nécessaire.

Le mode DRBD single-primary convient à de nombreux scénarios de système de fichiers monté sur un seul nœud à la fois.

Les scénarios multi-nœuds nécessitent un système de fichiers conçu pour les accès concurrents et un mécanisme de verrouillage adapté.

Documentation : [Ubuntu Server — DRBD](https://ubuntu.com/server/docs/how-to/high-availability/install-drbd/) et [Guide utilisateur DRBD de LINBIT](https://linbit.com/drbd-user-guide/drbd-guide-9_0-en/).

## 12. Stockage partagé, réplication et cohérence applicative

### 12.1 Trois modèles à distinguer

**Stockage partagé**

Les nœuds accèdent au même stockage par une infrastructure commune.

**Réplication par blocs**

Les données d'un périphérique sont répliquées vers un autre périphérique sur un second nœud, comme dans certains scénarios DRBD.

**Réplication applicative**

L'application ou le moteur de données réplique lui-même son état et ses transactions.

Chaque modèle a ses propres exigences de cohérence.

### 12.2 Exemple avec une base de données

Une base de données ne devient pas hautement disponible simplement parce que son disque est répliqué.

Il faut également considérer :

- Le moteur de base de données.
- Les transactions en cours.
- Les journaux.
- Le verrouillage.
- Le démarrage et l'arrêt du service.
- Les procédures de récupération.
- Les connexions des clients.
- Les mécanismes de réplication natifs du moteur.

Un stockage répliqué doit être utilisé selon les exigences du logiciel hébergé.

### 12.3 Pourquoi le fencing et le stockage sont liés

Si un ancien nœud conserve un accès au stockage pendant que le cluster tente d'activer la même ressource sur un autre nœud, les conséquences peuvent être graves.

Le fencing contribue à garantir l'isolation du nœud qui n'est plus autorisé à exploiter la ressource.

Le quorum, le fencing, la réplication et les règles de montage doivent donc être conçus ensemble plutôt que configurés séparément.

## 13. Maintenance et mises à jour d'un cluster

### 13.1 Pourquoi les mises à jour demandent une procédure

Une mise à jour peut nécessiter un redémarrage, modifier le noyau, remplacer un pilote, changer le comportement d'un service ou introduire une incompatibilité.

Dans un cluster, la mise à jour d'un nœud peut également modifier le nombre de membres disponibles et affecter le quorum.

Une procédure de maintenance doit protéger les rôles actifs et conserver une capacité suffisante.

### 13.2 Mise en maintenance d'un nœud Pacemaker

Sur un cluster correctement préparé, un nœud peut être placé en mode standby pour que les ressources quittent ce nœud selon les contraintes et les conditions du cluster.

Exemple :

```bash
sudo pcs node standby node1
```

Après avoir vérifié que le nœud est dans l'état prévu et que ses ressources ont été déplacées, tu peux effectuer les opérations planifiées.

Pour réintégrer le nœud :

```bash
sudo pcs node unstandby node1
```

Ces opérations doivent être adaptées à l'état du cluster et aux dépendances des ressources.

Ne les exécute pas aveuglément si le cluster a perdu le quorum ou si une ressource est en situation d'échec.

### 13.3 Procédure de maintenance recommandée

```text
Préparation
    |
    v
Vérification du quorum
    |
    v
Vérification du fencing
    |
    v
Vérification des ressources
    |
    v
Mise en standby du nœud
    |
    v
Contrôle du déplacement des ressources
    |
    v
Maintenance et redémarrage
    |
    v
Contrôle des services et du cluster
    |
    v
Réintégration du nœud
    |
    v
Vérification finale
```

Le nœud restant doit disposer des ressources suffisantes pour accueillir les services déplacés.

### 13.4 Ne pas mettre tous les nœuds à jour en même temps

Dans un cluster de deux nœuds, arrêter simultanément les deux membres supprime la capacité de reprise locale.

La maintenance doit être séquentielle, sauf si le scénario impose une opération différente et qu'un plan de reprise spécifique existe.

Avant chaque étape, vérifie que le cluster est revenu à l'état attendu.

### 13.5 Mode maintenance de Pacemaker

Le mode de maintenance modifie la manière dont Pacemaker gère les ressources.

Il peut être utile pendant certaines interventions contrôlées, mais il ne doit pas être confondu avec le mode standby d'un nœud.

En mode maintenance, le cluster peut cesser d'effectuer certaines actions de gestion automatique sur les ressources, selon la configuration.

Cela peut empêcher une récupération automatique attendue pendant la période d'intervention.

Le mode de maintenance doit avoir une justification, une durée prévue et une procédure de sortie.

## 14. Supervision d'un cluster

### 14.1 État des nœuds

Il faut surveiller :

- L'appartenance des nœuds.
- Le nombre de votes disponibles.
- Le quorum.
- Le réseau de communication.
- Les journaux Corosync.
- L'état des services de cluster.
- Les ressources en échec.
- Les événements de fencing.

Un nœud qui répond à `ping` n'est pas nécessairement opérationnel pour le cluster.

### 14.2 État des ressources

Pour chaque ressource critique, la supervision doit connaître :

- Son état.
- Son emplacement.
- Son dernier échec.
- Sa durée de démarrage.
- Ses changements de rôle.
- Son comportement en cas de perte d'une dépendance.

Exemple :

```text
Cluster app-cluster
|
+-- node1 : Online
|
+-- node2 : Online
|
+-- web-service : Started
|
+-- web-vip : Started
|
+-- Quorum : présent
|
+-- Fencing : configuré et vérifié
```

Ce schéma décrit un état souhaité, pas une sortie réelle de commande.

### 14.3 Contrôles fonctionnels

La supervision ne doit pas se limiter aux composants d'infrastructure.

Un contrôle utile vérifie que le service est réellement accessible par le chemin utilisé par les clients.

Exemples :

- Requête HTTP sur une URL dédiée.
- Vérification d'une réponse applicative.
- Test de lecture d'un fichier de contrôle.
- Mesure de latence.
- Test de connectivité vers une dépendance.
- Vérification d'un traitement transactionnel non destructif.

Les tests doivent être adaptés à l'application et ne pas provoquer une charge excessive.

### 14.4 Alertes

Les alertes peuvent signaler :

- La perte de quorum.
- Un nœud hors ligne.
- L'échec du fencing.
- Une ressource qui ne démarre pas.
- Une réplication en retard.
- Un disque presque plein.
- La perte de plusieurs backends.
- Une indisponibilité de la VIP.
- Des basculements répétés.

L'objectif n'est pas de générer le plus grand nombre d'alertes, mais d'identifier les événements qui exigent une action.

### 14.5 Conservation des journaux

Les journaux du cluster sont essentiels pour comprendre la chronologie d'un incident.

Ils doivent être conservés selon une politique adaptée, accessibles aux personnes autorisées et horodatés de manière cohérente.

Une plateforme de journalisation centralisée peut aider lorsque les nœuds deviennent inaccessibles ou qu'un incident touche plusieurs machines.

## 15. Sécuriser l'architecture

### 15.1 Sécuriser les réseaux de communication

Les réseaux utilisés pour la gestion, la communication du cluster, le stockage et les services applicatifs doivent être définis clairement.

La séparation physique ou logique doit correspondre aux risques et au trafic réel.

Il faut notamment :

- Limiter les sources autorisées.
- Restreindre l'accès aux interfaces de gestion.
- Contrôler les ports nécessaires.
- Protéger les identifiants et secrets.
- Surveiller les changements de configuration.
- Documenter les dépendances réseau.

### 15.2 Protéger Keepalived

Le processus Keepalived doit disposer des permissions nécessaires sans exposer ses fichiers de configuration et ses scripts à des modifications non autorisées.

Les échanges VRRP doivent être autorisés entre les participants prévus.

Une ancienne option d'authentification VRRP ne doit pas être considérée comme une protection cryptographique complète.

### 15.3 Protéger Pacemaker

Le contrôle du cluster donne potentiellement la capacité de démarrer ou d'arrêter des applications et de manipuler des ressources critiques.

Les accès à `pcs`, les comptes d'administration et les mécanismes de fencing doivent donc être protégés.

Il faut appliquer le principe du moindre privilège et éviter d'utiliser des comptes administrateurs partagés sans contrôle.

### 15.4 Protéger les données

Les fichiers de configuration, les clés, les certificats, les bases de données et les sauvegardes doivent être protégés contre les suppressions et modifications non autorisées.

La haute disponibilité n'empêche pas les actions malveillantes ou les erreurs de configuration d'affecter plusieurs nœuds.

Une copie indépendante et protégée demeure nécessaire pour restaurer les données après un incident grave.

### 15.5 Gérer les secrets

Ne place pas les secrets d'administration dans des scripts accessibles à tous les utilisateurs.

Les secrets utilisés par le fencing, la réplication, les bases de données ou les solutions de sauvegarde doivent être protégés par des mécanismes adaptés.

Lorsqu'une commande nécessite un secret, évite de l'exposer dans l'historique du shell ou dans des journaux partagés.

## 16. Dépannage avancé de Keepalived et IPVS

### 16.1 Symptôme : la VIP est absente

Vérifie :

1. L'état du service Keepalived.
2. Le contenu de la configuration.
3. Le nom de l'interface.
4. Le VRID.
5. Les adresses sources et les pairs unicast.
6. Les règles de pare-feu.
7. Les journaux VRRP.
8. La disponibilité de l'adresse.
9. La présence d'autres instances utilisant le même identifiant.
10. L'état de la priorité après contrôle de santé.

Commandes utiles :

```bash
sudo systemctl status keepalived
sudo journalctl -u keepalived --no-pager -n 100
ip -br address
ip route
```

Ne modifie pas plusieurs paramètres à la fois. Identifie d'abord la cause.

### 16.2 Symptôme : la VIP existe sur deux nœuds

C'est une situation anormale dans l'architecture à détenteur unique présentée ici.

Vérifie la communication des pairs, les identifiants VRRP, les adresses sources, les priorités et les journaux.

Il peut s'agir d'une partition réseau ou de deux instances qui ne se voient pas.

Si les deux serveurs continuent à recevoir le trafic, les clients peuvent connaître des comportements incohérents.

### 16.3 Symptôme : VIP active, aucun backend accessible

Vérifie :

- L'état des serveurs réels.
- Le contrôle TCP ou HTTP.
- Les routes.
- Le transfert IP si nécessaire.
- Les règles de pare-feu.
- Le chemin retour des paquets.
- L'état IPVS.
- Les interfaces physiques.
- L'état des applications.

Dans un mode NAT, les serveurs réels doivent disposer d'un chemin retour cohérent avec les traductions effectuées.

### 16.4 Symptôme : un backend sain est retiré du pool

Le contrôle de santé peut être trop strict ou mal configuré.

Vérifie les délais, les seuils et le protocole utilisé.

Un service peut refuser certaines requêtes de contrôle tout en restant fonctionnel pour les vraies requêtes clients. Il faut donc tester l'endpoint réellement configuré.

### 16.5 Symptôme : seules les connexions existantes échouent après basculement

Une migration de VIP ne garantit pas que toutes les connexions en cours restent intactes.

Les clients peuvent devoir se reconnecter. L'état des connexions et celui des sessions applicatives ne sont pas nécessairement transférés.

Pour un service critique, il faut examiner la manière dont l'application traite les reconnexions et les transactions interrompues.

## 17. Dépannage Pacemaker, Corosync et DRBD

### 17.1 Vérifier l'état du cluster

```bash
sudo pcs status
sudo pcs status --full
```

Examine également la configuration :

```bash
sudo pcs config
```

Si une ressource reste en échec, il faut examiner ses paramètres, ses dépendances et les messages des agents.

### 17.2 Examiner les journaux

Sur les systèmes qui utilisent les unités correspondantes :

```bash
sudo journalctl -u pacemaker --no-pager -n 100
sudo journalctl -u corosync --no-pager -n 100
sudo journalctl -u pcsd --no-pager -n 100
```

Les journaux doivent être interprétés dans l'ordre chronologique.

Recherche notamment ce qui a changé juste avant la panne : déconnexion réseau, perte de quorum, erreur d'agent, manque de stockage ou opération administrative.

### 17.3 Vérifier le quorum

Lorsque l'outil est disponible :

```bash
sudo corosync-quorumtool -s
```

Si le cluster a perdu le quorum, n'essaie pas de forcer le démarrage des ressources sans connaître l'origine de la perte de communication et les risques liés aux ressources partagées.

### 17.4 Ressource refusée ou bloquée

Une ressource peut être en échec parce que :

- L'agent n'existe pas.
- Le service est mal configuré.
- Une dépendance est absente.
- L'adresse IP est déjà utilisée.
- Le montage de stockage ne peut pas aboutir.
- Une opération précédente a échoué.
- Le nœud n'est pas autorisé à gérer la ressource.
- Le cluster ne dispose pas du quorum.

La première étape est la collecte des informations, pas la suppression de la ressource.

### 17.5 DRBD en état de synchronisation ou de déconnexion

Vérifie :

- L'état du lien réseau.
- Les paramètres de la ressource.
- Le nom du nœud.
- Les périphériques définis.
- La disponibilité du stockage local.
- L'état des données répliquées.
- Les journaux.
- Le comportement de Pacemaker.

Ne promeus pas une ressource DRBD à l'aveugle pour forcer le service à démarrer. Une promotion incorrecte peut créer une situation de données divergentes.

Avant toute procédure de récupération DRBD, consulte les indications de la version et les recommandations du fournisseur pour ne pas écraser la copie contenant les données valides.

## 18. Sauvegarde et reprise après sinistre

### 18.1 Le cluster ne protège pas contre toutes les pertes

Une infrastructure redondante peut continuer à fonctionner après la panne d'un nœud, mais elle peut toujours être affectée par :

- Une suppression accidentelle.
- Une corruption logique.
- Une mauvaise configuration répliquée.
- Une attaque touchant plusieurs serveurs.
- Une panne de stockage commune.
- La destruction du site.
- Une erreur lors d'une opération d'administration.

La sauvegarde doit être pensée comme un mécanisme distinct.

### 18.2 Définir une stratégie de sauvegarde

Une stratégie de sauvegarde doit préciser :

- Les services protégés.
- La fréquence des copies.
- La durée de rétention.
- La localisation des copies.
- La protection contre les suppressions.
- Le chiffrement éventuel.
- Les permissions d'accès.
- Les objectifs de restauration.
- Les procédures de test.

Il faut vérifier la restauration complète d'une application et de ses dépendances, et pas seulement constater que des fichiers de sauvegarde existent.

### 18.3 La sauvegarde doit être indépendante du cluster

Conserver toutes les sauvegardes sur le stockage que le cluster utilise pour ses services peut créer un risque commun.

Lorsqu'une sauvegarde dépend du même espace susceptible d'être corrompu ou détruit que les données originales, elle peut disparaître avec elles.

Il est préférable d'utiliser une architecture de sauvegarde protégée et suffisamment indépendante du domaine de panne principal.

### 18.4 Préparer un plan de reprise après sinistre

Un plan de reprise doit décrire :

1. Qui déclare le sinistre.
2. Quelles applications doivent être récupérées en priorité.
3. Quelles ressources et données sont nécessaires.
4. Dans quel ordre les services doivent démarrer.
5. Comment les utilisateurs accèdent aux services.
6. Comment vérifier la cohérence des données.
7. Qui valide la reprise.
8. Comment le service revient à l'état nominal.
9. Comment les événements sont documentés.

Un cluster local ne remplace pas nécessairement une stratégie de reprise intersite.

## 19. Travaux pratiques guidés

Tous les tests ci-dessous doivent être réalisés dans un laboratoire. Les commandes qui créent des ressources de cluster, modifient le stockage ou affectent le quorum peuvent interrompre des services ; ne les exécute pas sur une infrastructure de production sans procédure approuvée.

### TP 1 — Configurer un suivi de santé Keepalived

**Objectif :** détecter l'arrêt d'un service applicatif.

Étapes :

1. Vérifier l'état de Keepalived sur les deux serveurs.
2. Vérifier le détenteur actuel de la VIP.
3. Créer un script de contrôle Nginx ou HAProxy.
4. Protéger le script avec des permissions adaptées.
5. Le tester manuellement.
6. Ajouter `vrrp_script`.
7. Associer le contrôle à l'instance VRRP.
8. Vérifier les journaux.
9. Arrêter le service dans le laboratoire.
10. Observer la modification de priorité et le basculement.

**Résultat attendu :** un compte rendu qui explique comment le contrôle de santé influence l'instance VRRP.

### TP 2 — Ajouter IPVS à Keepalived

**Objectif :** répartir le trafic vers deux serveurs réels.

Prérequis :

- Deux serveurs applicatifs.
- Un équilibreur de laboratoire.
- Une VIP libre.
- Les réseaux et routes nécessaires.

Étapes :

1. Vérifier l'accès HTTP aux deux backends.
2. Préparer le réseau du service virtuel.
3. Configurer le bloc `virtual_server`.
4. Choisir un algorithme adapté.
5. Configurer les contrôles de santé.
6. Activer le routage IPv4 si le scénario NAT le demande.
7. Charger la configuration.
8. Examiner les serveurs réels dans IPVS.
9. Arrêter un backend dans le laboratoire.
10. Observer son retrait du pool.
11. Vérifier le service depuis un client.

**Résultat attendu :** un service de laboratoire qui reste accessible tant qu'au moins un backend sain est disponible et que l'équilibreur fonctionne.

### TP 3 — Configurer HAProxy

**Objectif :** comprendre la répartition de requêtes HTTP.

Étapes :

1. Installer HAProxy sur le serveur de laboratoire.
2. Configurer deux backends.
3. Définir un endpoint de contrôle de santé.
4. Valider la syntaxe.
5. Recharger le service.
6. Vérifier les journaux.
7. Arrêter un backend.
8. Vérifier le comportement des requêtes.
9. Restaurer le backend.
10. Documenter les résultats.

**Résultat attendu :** une configuration vérifiée et un compte rendu expliquant la différence entre la santé du backend et celle de l'équilibreur.

### TP 4 — Créer un cluster Pacemaker

**Objectif :** comprendre la préparation et la validation du cluster.

Étapes :

1. Préparer deux nœuds de laboratoire.
2. Installer Corosync, Pacemaker et `pcs`.
3. Vérifier les noms et les adresses.
4. Préparer l'authentification.
5. Créer le cluster.
6. Vérifier son état.
7. Examiner le quorum.
8. Définir le mécanisme de fencing approprié à l'environnement de laboratoire.
9. Vérifier les mécanismes de reprise.
10. Documenter les tests.

**Important :** ne désactive pas le fencing pour simplement obtenir un résultat visuellement réussi. Le cluster ne doit pas être considéré comme prêt pour la production tant que le fencing et le quorum n'ont pas été vérifiés.

### TP 5 — Créer un groupe de ressources

**Objectif :** organiser le service et l'adresse de service.

Étapes :

1. Vérifier que le cluster est sain et correctement protégé.
2. Préparer Nginx sur les deux nœuds.
3. Vérifier l'agent de service disponible.
4. Créer la ressource du service.
5. Créer la ressource d'adresse IP.
6. Ajouter les ressources au groupe dans l'ordre choisi.
7. Vérifier le résultat.
8. Effectuer un test de placement contrôlé.
9. Vérifier le service depuis un client.
10. Documenter l'ordre de démarrage et d'arrêt.

**Résultat attendu :** des ressources gérées par Pacemaker dont le comportement est cohérent avec la dépendance attendue.

### TP 6 — Concevoir une architecture DRBD

**Objectif :** comprendre comment la disponibilité d'une application dépend de la réplication des données.

Étapes :

1. Identifier les périphériques de stockage destinés au laboratoire.
2. Définir le réseau de réplication.
3. Choisir le protocole de réplication correspondant au besoin.
4. Préparer la configuration DRBD selon la documentation de la version.
5. Initialiser les métadonnées uniquement sur des volumes de laboratoire dédiés.
6. Vérifier la synchronisation.
7. Définir le mécanisme de gestion du rôle actif.
8. Prévoir le montage et le démontage du système de fichiers.
9. Définir les dépendances Pacemaker.
10. Définir le fencing et le quorum.
11. Tester le basculement.
12. Vérifier l'intégrité des données.

**Résultat attendu :** un plan de configuration documenté, comprenant le mécanisme de réplication et la procédure de reprise.

## 20. Exercices d'application avec corrigés

### Exercice 1 — Keepalived et HAProxy

LB1 possède la VIP, mais HAProxy est arrêté. Le serveur Linux répond encore au réseau.

**Question :** pourquoi un contrôle de la seule disponibilité de l'hôte est-il insuffisant ?

**Corrigé :** le système et son interface peuvent fonctionner alors que le service d'équilibrage est indisponible. Le suivi doit contrôler le service lui-même ou un endpoint local adapté, puis influencer la priorité VRRP selon la politique choisie.

### Exercice 2 — Un backend est retiré du pool

Un backend est fonctionnel, mais le contrôle HTTP échoue.

**Question :** que faut-il examiner ?

**Corrigé :** vérifier l'URL de contrôle, le code HTTP attendu, les délais, les permissions, le routage et le comportement de l'application. Un simple test TCP peut être insuffisant ; inversement, un endpoint HTTP mal conçu peut créer de faux échecs.

### Exercice 3 — IPVS avec NAT

Les clients peuvent atteindre la VIP, mais les réponses des serveurs applicatifs ne reviennent pas correctement.

**Question :** quelles causes examiner ?

**Corrigé :** vérifier le transfert IP, la traduction NAT, les routes, le chemin retour, les règles de pare-feu et la configuration des interfaces. Les serveurs réels doivent répondre par un chemin compatible avec la méthode NAT retenue.

### Exercice 4 — Deux ressources doivent rester ensemble

Un service applicatif doit fonctionner sur le même nœud que son volume de données.

**Question :** quel mécanisme Pacemaker permet d'exprimer cette relation ?

**Corrigé :** une contrainte de colocation ou un groupe adapté peut permettre de maintenir les ressources ensemble. Le choix dépend du cycle de vie de l'application et des dépendances réelles.

### Exercice 5 — Le service démarre avant le montage

Pacemaker démarre une application qui dépend d'un volume, mais le volume n'est pas encore monté.

**Question :** quel type de configuration faut-il examiner ?

**Corrigé :** examiner les contraintes d'ordre, les contraintes de colocation et l'agent de stockage. L'application ne doit pas commencer tant que sa dépendance n'est pas correctement disponible.

### Exercice 6 — Un nœud a perdu la communication réseau

Les deux nœuds restent allumés mais ne communiquent plus entre eux.

**Question :** pourquoi le cluster ne doit-il pas simplement démarrer les ressources sur les deux côtés ?

**Corrigé :** cela pourrait créer un split-brain. Le quorum et le fencing participent à empêcher plusieurs membres de gérer simultanément les mêmes ressources de manière incohérente.

### Exercice 7 — Une ressource est en échec

Après un redémarrage manuel du service, Pacemaker continue à afficher une ressource en échec.

**Question :** pourquoi ne faut-il pas immédiatement supprimer la ressource ?

**Corrigé :** le cluster peut avoir conservé des informations d'échec ou attendre une nouvelle évaluation. Il faut consulter les journaux, corriger la cause, puis utiliser les mécanismes adaptés de nettoyage et de réévaluation. Supprimer la ressource peut retirer des protections et des dépendances importantes.

### Exercice 8 — DRBD et système de fichiers

Une équipe veut monter le même système de fichiers ext4 en lecture-écriture sur les deux nœuds DRBD.

**Question :** pourquoi cette approche est-elle dangereuse dans un scénario single-primary classique ?

**Corrigé :** un système de fichiers traditionnel comme ext4 n'est pas conçu pour un accès concurrent en écriture depuis deux nœuds indépendants au même périphérique bloc. Le montage doit être coordonné par le cluster, ou l'architecture doit utiliser un système de fichiers adapté à un accès partagé concurrent.

### Exercice 9 — Cluster et sauvegarde

L'équipe possède deux serveurs avec DRBD et estime qu'une sauvegarde est inutile.

**Question :** pourquoi ce raisonnement est-il incorrect ?

**Corrigé :** la réplication maintient une copie des blocs selon la configuration, mais peut aussi répliquer une corruption ou une suppression. Il faut conserver des sauvegardes indépendantes et tester leur restauration.

### Exercice 10 — Maintenance d'un nœud

Un administrateur veut redémarrer node1 pour installer des mises à jour.

**Question :** quelles vérifications doit-il effectuer avant le redémarrage ?

**Corrigé :** vérifier le quorum, le fencing, l'état des ressources, la capacité restante, les dépendances de stockage et la procédure de drainage. Il faut ensuite vérifier le rétablissement de la santé du cluster avant de passer au nœud suivant.

## 21. Projet de synthèse : plateforme Linux hautement disponible

### 21.1 Contexte

Une entreprise possède un site Web interne utilisé par plusieurs équipes.

Elle veut protéger le point d'entrée contre la panne d'un équilibreur, répartir les requêtes entre deux serveurs applicatifs et garantir que l'application puisse être reprise après certains incidents.

Une seconde application, plus complexe, nécessite un service de stockage et un ordre de démarrage particulier.

### 21.2 Architecture cible

```text
                         CLIENTS
                            |
                            v
                    VIP D'ENTRÉE WEB
                            |
                   Keepalived / VRRP
                            |
                 +----------+----------+
                 |                     |
                 v                     v
              +------+              +------+
              | LB1  |              | LB2  |
              |      |              |      |
              | IPVS |              | IPVS |
              | ou   |              | ou   |
              | HAProxy             | HAProxy
              +------+              +------+
                 |                     |
                 +----------+----------+
                            |
                     Pool applicatif
                       /        \
                      v          v
                    APP01      APP02


              APPLICATION AVEC DONNÉES
                            |
                            v
                    Pacemaker / Corosync
                            |
                 +----------+----------+
                 |                     |
                 v                     v
               node1                 node2
                 |                     |
                 +----------+----------+
                            |
                       Stockage DRBD
                  et ressource applicative
```

Ce schéma représente deux familles de services. Il ne faut pas les considérer comme un même cluster si leurs responsabilités et leurs dépendances sont différentes.

### 21.3 Travaux demandés

Le dossier doit comprendre :

1. Le schéma logique de l'architecture.
2. Les plages IP et les interfaces utilisées.
3. Les règles de filtrage réseau.
4. Le mécanisme Keepalived retenu.
5. Le mécanisme de répartition de charge.
6. Le choix entre IPVS et HAProxy pour le service Web.
7. Les contrôles de santé.
8. Les ressources Pacemaker.
9. Les contraintes d'ordre et de placement.
10. Le mécanisme de quorum.
11. La méthode de fencing.
12. Le modèle de stockage ou de réplication.
13. Les procédures de sauvegarde et de restauration.
14. La procédure de mise à jour.
15. Les tests de panne et les résultats observés.
16. Les commandes utiles à l'exploitation.
17. La documentation de retour arrière.

### 21.4 Critères de réussite

Le projet est réussi si :

- La VIP reste portée par un seul détenteur dans le scénario prévu.
- Les backends défaillants sont retirés du trafic selon les tests.
- Le service Web reste accessible lorsque les conditions de disponibilité sont satisfaites.
- Les ressources Pacemaker respectent les dépendances définies.
- Le quorum est compris et documenté.
- Le fencing a été préparé et testé.
- Le stockage est utilisé selon un modèle cohérent.
- Les procédures de reprise sont reproductibles.
- Les sauvegardes sont distinctes du mécanisme de réplication.
- Les tests sont documentés et mesurés.

## 22. Défi final : industrialiser un cluster Linux

Une organisation utilise :

- Deux équilibreurs.
- Trois serveurs applicatifs.
- Une application basée sur des données persistantes.
- Deux nœuds pour un cluster de ressources.
- Un réseau de gestion distinct du réseau applicatif.

Elle veut maintenir un accès stable aux services et limiter les interruptions pendant la maintenance.

Tu dois proposer une architecture expliquant :

### Partie A — Point d'accès

Définis :

- La VIP.
- Les priorités VRRP.
- Les contrôles de santé.
- La stratégie de préemption.
- Les règles de sécurité réseau.
- Le comportement attendu lors d'une panne de l'équilibreur.

### Partie B — Équilibrage de charge

Compare IPVS et HAProxy pour le besoin.

Justifie le choix à partir de :

- La nature du trafic.
- La couche de protocole.
- Le contrôle de santé.
- La configuration des backends.
- Les besoins de persistance.
- Les contraintes de performance.
- La capacité de supervision.

### Partie C — Cluster de ressources

Définis :

- Les ressources à gérer.
- Les contraintes d'ordre.
- Les contraintes de colocation.
- Le quorum.
- Le fencing.
- Le modèle de stockage.
- Les procédures de récupération.

### Partie D — Reprise et sécurité

Prépare :

- Une stratégie de sauvegarde.
- Une procédure de restauration.
- Une politique de maintenance.
- Un plan de reprise après sinistre.
- Un système de journalisation.
- Une politique d'accès administratif.
- Un plan de tests de panne.

### Partie E — Validation opérationnelle

Définis les résultats attendus et les preuves à collecter.

Le dossier doit démontrer que l'infrastructure a été testée et que ses mécanismes de récupération fonctionnent dans les scénarios retenus.

## 23. Fiche de référence opérationnelle

| Besoin | Outil ou mécanisme |
|---|---|
| Voir les interfaces réseau | `ip -br address` |
| Contrôler la table de routage | `ip route` |
| Vérifier Keepalived | `systemctl status keepalived` |
| Lire les événements Keepalived | `journalctl -u keepalived` |
| Vérifier la VIP | `ip address show ens18` |
| Examiner les services IPVS | `ipvsadm -Ln` |
| Vérifier HAProxy | `systemctl status haproxy` |
| Valider la configuration HAProxy | `haproxy -c -f /etc/haproxy/haproxy.cfg` |
| Consulter l'état Pacemaker | `pcs status` |
| Examiner la configuration Pacemaker | `pcs config` |
| Examiner les ressources | `pcs resource status` |
| Examiner le quorum Corosync | `corosync-quorumtool -s` |
| Consulter les journaux du cluster | `journalctl -u pacemaker` et `journalctl -u corosync` |
| Mettre un nœud en standby | `pcs node standby node1` |
| Réintégrer un nœud | `pcs node unstandby node1` |
| Nettoyer l'état d'échec d'une ressource après correction | `pcs resource cleanup web-service` |
| Examiner l'état DRBD | `drbdadm status` |

La disponibilité de certaines commandes et leur syntaxe dépendent de la version et des paquets installés.

## 24. Bonnes pratiques à retenir

### Architecture

- Identifie les points uniques de défaillance avant de choisir les outils.
- Définis les objectifs RTO et RPO.
- Sépare clairement le point d'entrée, l'équilibrage, les applications et les données.
- Ne considère pas deux serveurs comme une architecture hautement disponible sans mécanisme de coordination adapté.
- Vérifie la cohérence des données sur tous les nœuds susceptibles d'héberger un service.

### Keepalived et IPVS

- Surveille les fonctions réellement nécessaires à l'application.
- Vérifie les priorités et les règles de préemption.
- Protège les scripts de contrôle.
- Valide les routes et les chemins retour.
- Mesure les effets du basculement sur les clients.
- Distingue le contrôle TCP d'un contrôle applicatif.
- Vérifie que la VIP ne peut pas être gérée indépendamment par deux mécanismes.

### HAProxy

- Valide la syntaxe avant de recharger une configuration.
- Utilise des contrôles de santé adaptés au protocole.
- Évite les délais trop courts ou trop longs sans mesure.
- Prévoyez un comportement pour les cas où tous les backends sont indisponibles.
- Conçois correctement la gestion des sessions applicatives.
- Surveille l'équilibreur et les serveurs réels séparément.

### Pacemaker et Corosync

- Vérifie le quorum avant les opérations de maintenance.
- Configure et teste le fencing avant la production.
- Utilise les groupes et contraintes pour représenter les dépendances réelles.
- Ne lance pas manuellement un service de façon indépendante lorsqu'il est géré par Pacemaker.
- Examine les journaux avant de nettoyer les échecs.
- Évite les changements simultanés sur plusieurs nœuds.

### DRBD et stockage

- Vérifie les périphériques avant les opérations d'initialisation.
- Ne monte pas simultanément un système de fichiers non conçu pour l'accès concurrent en écriture.
- Coordonne le montage et l'arrêt des ressources avec le cluster.
- Surveille la synchronisation et l'état des copies.
- Maintiens une sauvegarde indépendante.
- Teste les procédures de récupération.

### Exploitation

- Documente les changements.
- Journalise les basculements.
- Mesure les temps de reprise.
- Teste périodiquement les scénarios de panne.
- Protège les informations d'administration.
- Vérifie les services applicatifs, pas seulement les hôtes.
- Prévois une procédure de retour arrière.

## 25. Glossaire intermédiaire

**VIP — Virtual IP Address :** adresse IP virtuelle utilisée comme point d'accès à un service.

**VRRP :** protocole permettant de coordonner la responsabilité d'une adresse virtuelle.

**Keepalived :** logiciel Linux qui fournit notamment la gestion VRRP et des fonctions d'équilibrage IPVS.

**IPVS :** fonction Linux Virtual Server utilisée pour répartir le trafic IP vers des serveurs réels.

**Backend :** serveur ou service qui reçoit le trafic transmis par un équilibreur.

**NAT :** traduction d'adresses et de ports réseau, utilisée notamment pour transmettre le trafic vers des réseaux privés.

**Direct Routing :** méthode IPVS dans laquelle le serveur réel peut retourner directement les réponses au client selon la conception réseau.

**Tunneling :** méthode qui transmet les paquets vers les serveurs réels au moyen de tunnels réseau.

**HAProxy :** logiciel d'équilibrage de charge et de proxy pour des services TCP et HTTP.

**Pacemaker :** gestionnaire de ressources de cluster.

**Corosync :** composant de communication et d'appartenance au cluster.

**pcs :** outil d'administration pour les clusters Pacemaker/Corosync.

**Ressource :** élément que Pacemaker peut gérer par l'intermédiaire d'un agent.

**Contrainte de placement :** règle définissant les nœuds autorisés ou préférés pour une ressource.

**Contrainte d'ordre :** règle définissant l'ordre de démarrage ou d'arrêt de ressources.

**Colocation :** règle permettant de placer plusieurs ressources ensemble selon une politique donnée.

**Quorum :** mécanisme déterminant si le cluster possède les votes requis pour continuer à gérer ses ressources.

**QDevice :** mécanisme externe d'arbitrage de quorum disponible pour certaines architectures Corosync.

**Fencing / STONITH :** isolation fiable d'un nœud qui ne doit plus accéder aux ressources du cluster.

**DRBD :** mécanisme de réplication de périphériques de stockage par blocs.

**Single-primary :** mode dans lequel une seule instance DRBD est primaire selon la configuration normale retenue.

**Split-brain :** situation dans laquelle plusieurs parties isolées d'un cluster peuvent essayer de gérer simultanément les mêmes ressources.

**RTO :** délai maximal ciblé pour rétablir un service après incident.

**RPO :** quantité de données qu'une organisation accepte de perdre, exprimée en durée.

## 26. Documentation officielle

### Keepalived et IPVS

- [Guide utilisateur Keepalived](https://keepalived.org/documentation/user-guide/)
- [Présentation de Keepalived](https://keepalived.org/documentation/user-guide/introduction/)
- [Vue d'ensemble de la configuration](https://keepalived.org/documentation/user-guide/configuration-synopsis/)
- [Techniques d'équilibrage de charge](https://www.keepalived.org/documentation/user-guide/load-balancing-techniques/)
- [Algorithmes de répartition IPVS](https://www.keepalived.org/documentation/user-guide/scheduling-algorithms/)
- [Guide de démarrage rapide](https://keepalived.org/documentation/user-guide/quick-start/)

### HAProxy

- [Contrôles de santé HAProxy](https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/)
- [Documentation de configuration HAProxy](https://docs.haproxy.org/)

### Pacemaker et Corosync

- [Documentation haute disponibilité Ubuntu Server](https://ubuntu.com/server/docs/reference/high-availability/)
- [Introduction à la haute disponibilité Ubuntu Server](https://ubuntu.com/server/docs/explanation/intro-to/high-availability/)
- [Agents de fencing Pacemaker sur Ubuntu](https://ubuntu.com/server/docs/explanation/high-availability/pacemaker-fence-agents/)
- [Agents de ressources Pacemaker](https://ubuntu.com/server/docs/explanation/high-availability/pacemaker-resource-agents/)
- [Clusters haute disponibilité RHEL 9](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/)
- [Créer et gérer des ressources Pacemaker](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/assembly_configuring-cluster-resources-configuring-and-managing-high-availability-clusters)

### DRBD

- [Installer et configurer DRBD avec Ubuntu Server](https://ubuntu.com/server/docs/how-to/high-availability/install-drbd/)
- [Guide utilisateur DRBD de LINBIT](https://linbit.com/drbd-user-guide/drbd-guide-9_0-en/)

## Conclusion

Un cluster Linux intermédiaire combine plusieurs mécanismes qui ont des responsabilités différentes.

Keepalived et VRRP peuvent fournir un point d'accès réseau stable. IPVS et HAProxy peuvent répartir le trafic entre des serveurs applicatifs. Pacemaker et Corosync gèrent les ressources et les transitions de rôle, tandis que DRBD peut contribuer à rendre les données disponibles sur plusieurs nœuds.

Cependant, aucune de ces technologies ne suffit à elle seule à garantir la cohérence des données et la disponibilité de toute une application.

Une conception robuste nécessite une stratégie de quorum, un fencing fiable, des contrôles de santé pertinents, une gestion rigoureuse des dépendances, des sauvegardes indépendantes et des tests de basculement documentés.

La règle fondamentale du niveau intermédiaire est donc la suivante : **chaque ressource doit avoir un propriétaire clairement défini, chaque dépendance doit être prise en compte et chaque scénario de panne doit être validé par un test contrôlé.**