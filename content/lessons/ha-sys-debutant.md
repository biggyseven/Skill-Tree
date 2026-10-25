# Haute disponibilité sous Linux : Keepalived et Pacemaker
## Cours débutant — VIP, basculement automatique, surveillance des services et introduction aux clusters

## 1. Présentation du cours

### 1.1 Objectif général

Dans une infrastructure informatique, un serveur peut fonctionner parfaitement pendant plusieurs semaines puis devenir indisponible à la suite d'une panne matérielle, d'une erreur de configuration, d'un incident réseau ou d'un problème logiciel.

Lorsqu'un service est important, il ne suffit pas de savoir le redémarrer manuellement. Il faut réfléchir à la manière dont il pourra continuer à fonctionner si un composant tombe en panne.

C'est l'objectif de la **haute disponibilité**, généralement abrégée en HA (*High Availability*).

Ce cours présente deux technologies Linux complémentaires :

- **Keepalived** : permet notamment de déplacer automatiquement une adresse IP virtuelle entre plusieurs machines à l'aide du protocole VRRP. Il peut aussi servir à effectuer des contrôles de santé et à gérer certains scénarios d'équilibrage de charge.
- **Pacemaker** : gestionnaire de ressources de cluster qui peut démarrer, surveiller, arrêter et déplacer des services entre plusieurs nœuds selon des règles définies par l'administrateur.

Ces outils peuvent être employés séparément ou dans des architectures plus complexes. Ils ne répondent cependant pas exactement au même besoin.

Keepalived peut convenir pour rendre disponible une adresse IP utilisée par un service réseau. Pacemaker peut gérer un ensemble de ressources et leurs dépendances, notamment une adresse IP, un service, un système de fichiers ou d'autres composants pris en charge.

### 1.2 Ce que tu vas apprendre

À la fin de ce cours, tu devras être capable de :

- Comprendre les objectifs et les limites de la haute disponibilité.
- Distinguer une adresse IP physique d'une adresse IP virtuelle.
- Comprendre le fonctionnement général de VRRP.
- Installer Keepalived sur deux serveurs Linux.
- Configurer une adresse IP virtuelle avec Keepalived.
- Comprendre la différence entre un serveur principal et un serveur de secours.
- Contrôler l'état d'un service et surveiller les journaux.
- Déclencher et observer un basculement dans un laboratoire.
- Comprendre le rôle de Pacemaker et de Corosync.
- Identifier les notions de nœud, ressource, quorum et fencing.
- Comprendre pourquoi le fencing est indispensable dans un cluster de production.
- Découvrir l'administration d'un cluster avec `pcs`.
- Diagnostiquer les problèmes courants.
- Comprendre pourquoi la haute disponibilité ne remplace pas la sauvegarde.
- Concevoir une architecture simple et sécurisée pour un service Web.

### 1.3 Prérequis

Il est préférable de connaître les bases de Linux :

- Navigation dans le système de fichiers.
- Utilisation du terminal.
- Édition d'un fichier de configuration.
- Gestion des utilisateurs et des permissions.
- Utilisation de `systemctl`.
- Configuration des adresses IP.
- Résolution DNS.
- Notions de TCP, UDP et ports réseau.
- Installation de paquets.

Les commandes seront présentées principalement pour Ubuntu Server. Certaines commandes sont communes à Debian, Ubuntu et aux distributions de la famille Red Hat, mais les noms de paquets, les pare-feu et les procédures d'administration peuvent différer.

### 1.4 Environnement de laboratoire

Nous allons utiliser deux serveurs Linux.

| Élément | Serveur 1 | Serveur 2 |
|---|---|---|
| Nom | `ha1` | `ha2` |
| Adresse IP de gestion | `192.168.50.11` | `192.168.50.12` |
| Interface du laboratoire | `ens18` | `ens18` |
| Fonction initiale | Principal préféré | Secours |
| Service Web | Nginx | Nginx |

L'adresse IP virtuelle utilisée pour le laboratoire sera :

`192.168.50.100/24`

Cette adresse n'est attribuée en permanence à aucun des deux serveurs. Elle sera portée par celui qui assume le rôle actif.

Les adresses sont fictives. Il faut les adapter à un réseau de laboratoire qui t'appartient ou pour lequel tu es autorisé à effectuer des tests.

Les deux serveurs doivent être placés sur un réseau compatible avec le fonctionnement de VRRP. Pour le laboratoire, nous supposerons qu'ils partagent le même segment réseau de niveau 2, ou un réseau correctement configuré pour les annonces VRRP en unicast.

**Important :** ne configure pas l'adresse IP virtuelle sur un autre équipement du réseau. Une adresse déjà utilisée provoquerait un conflit IP.

## 2. Comprendre la haute disponibilité

### 2.1 Le problème du serveur unique

Prenons une entreprise qui héberge son site Web sur un seul serveur Linux.

```text
                 UTILISATEURS
                      |
                      v
              +---------------+
              | Serveur WEB01 |
              |               |
              | Nginx         |
              | Site Web       |
              +---------------+
```

Tant que le serveur fonctionne, le site est accessible.

Mais que se passe-t-il si :

- Le serveur s'arrête ?
- Le système d'exploitation se bloque ?
- Le service Nginx tombe en panne ?
- La carte réseau devient inutilisable ?
- Une mise à jour nécessite un redémarrage ?
- Le serveur perd sa connectivité réseau ?

Si aucune solution de secours n'est prévue, les utilisateurs ne peuvent plus accéder au service jusqu'à sa remise en état.

### 2.2 Ajouter un serveur de secours

Une première amélioration consiste à préparer un second serveur, capable de prendre le relais.

```text
                    UTILISATEURS
                         |
                         v
                 Adresse de service
                         |
                  +------+------+
                  |             |
                  v             v
             +---------+   +---------+
             |   ha1   |   |   ha2   |
             | Principal|  | Secours |
             +---------+   +---------+
                  |             |
                  +------+------+
                         |
                 Réseau commun
```

Cependant, deux serveurs ne constituent pas automatiquement une infrastructure hautement disponible.

Il faut déterminer :

- Comment les utilisateurs rejoignent le service.
- Comment le serveur de secours détecte une panne.
- Comment il sait qu'il peut prendre le relais en toute sécurité.
- Comment l'adresse du service est transférée.
- Comment les données sont rendues accessibles.
- Comment éviter que les deux machines deviennent actives simultanément alors qu'elles ne devraient pas l'être.

Keepalived et Pacemaker répondent à différentes parties de ces questions.

### 2.3 Haute disponibilité et équilibrage de charge

Ces deux notions ne sont pas équivalentes.

**Haute disponibilité**

L'objectif est de réduire la durée d'indisponibilité en prenant le relais lorsqu'un élément tombe en panne.

**Équilibrage de charge**

L'objectif est de répartir le trafic entre plusieurs serveurs afin de mieux utiliser les ressources, de supporter davantage de connexions ou d'améliorer les performances.

Une architecture peut combiner les deux.

Exemple d'équilibrage de charge :

```text
                UTILISATEURS
                     |
                     v
             +----------------+
             | Point d'entrée |
             | de trafic      |
             +----------------+
                     |
               +-----+-----+
               |           |
               v           v
          +---------+  +---------+
          | WEB01   |  | WEB02   |
          +---------+  +---------+
```

Le point d'entrée peut, lui aussi, nécessiter une protection contre les pannes.

Keepalived peut être utilisé avec VRRP pour fournir une adresse virtuelle d'accès. Il dispose également de fonctions d'équilibrage de charge reposant notamment sur IPVS, qui constituent un sujet plus avancé que le simple transfert d'adresse virtuelle.

### 2.4 Haute disponibilité et sauvegarde

La haute disponibilité permet de poursuivre ou de rétablir un service après certains incidents.

La sauvegarde sert à récupérer des données à partir de copies conservées.

Ces mécanismes répondent à des risques différents.

| Situation | Haute disponibilité | Sauvegarde |
|---|---|---|
| Arrêt brutal du serveur principal | Peut permettre le basculement | Peut permettre une restauration si nécessaire |
| Suppression accidentelle d'un fichier | Ne garantit pas sa récupération | Permet une récupération si le fichier a été sauvegardé |
| Corruption de données répliquée | Peut propager le problème selon l'architecture | Peut fournir une version antérieure saine |
| Destruction du site principal | Un cluster local peut être perdu | Une sauvegarde indépendante peut permettre la reprise |
| Panne d'un processus Web | Peut redémarrer ou transférer le service selon la configuration | Généralement pas le mécanisme principal de traitement |

Un environnement hautement disponible a toujours besoin d'une stratégie de sauvegarde et de restauration.

## 3. Les indicateurs essentiels : RTO et RPO

### 3.1 RTO : délai de rétablissement

Le RTO (*Recovery Time Objective*) est le délai maximal ciblé pour rétablir un service après un incident.

Exemple :

Le site Web doit redevenir accessible dans les deux minutes suivant une panne détectable.

Le RTO cible est de deux minutes.

Le temps réel dépend toutefois de la détection, du mécanisme de basculement, de la disponibilité du service, du réseau et du comportement des clients.

### 3.2 RPO : perte de données acceptable

Le RPO (*Recovery Point Objective*) exprime la perte de données qu'une organisation accepte, en durée.

Pour un simple site Web statique, le RPO peut être facile à satisfaire lorsque son contenu est identique sur les deux serveurs.

Pour une application qui enregistre des commandes ou des paiements, le problème est différent : les données enregistrées doivent être protégées par une architecture applicative et de stockage adaptée.

Déplacer une adresse IP ne synchronise pas une base de données.

### 3.3 Exemple de besoins

| Service | RTO cible | RPO cible |
|---|---:|---:|
| Site Web statique interne | 2 minutes | Selon la méthode de publication du contenu |
| Application métier | 5 minutes | 1 minute |
| Base de données transactionnelle | Selon le besoin métier | Selon la stratégie de réplication |
| Serveur de test | 1 journée | 1 journée |

Ce sont des exemples pédagogiques, pas des garanties offertes par Keepalived ou Pacemaker.

## 4. Comprendre l'adresse IP virtuelle

### 4.1 Adresse physique et adresse virtuelle

Chaque serveur possède sa propre adresse IP, utilisée notamment pour son administration.

Par exemple :

- `ha1` : `192.168.50.11`
- `ha2` : `192.168.50.12`

L'adresse de service est :

- VIP : `192.168.50.100`

Une VIP (*Virtual IP Address*) est une adresse utilisée par le service. Selon la configuration, elle peut être portée par un seul serveur actif à la fois.

```text
SERVEUR ha1
|
+-- IP physique : 192.168.50.11
|
+-- VIP : 192.168.50.100  <-- si ha1 est actif


SERVEUR ha2
|
+-- IP physique : 192.168.50.12
|
+-- VIP absente            <-- si ha2 est en secours
```

Lorsque le serveur actif n'est plus capable d'assurer le rôle, l'adresse virtuelle peut être transférée vers le serveur de secours.

### 4.2 Pourquoi utiliser une VIP ?

Sans adresse virtuelle, les utilisateurs doivent connaître l'adresse du serveur utilisé.

Si le service se déplace, il faudrait alors modifier la configuration des clients ou le point d'accès au service.

Avec une VIP, les utilisateurs conservent la même adresse de destination.

```text
AVANT LA PANNE

Client
  |
  v
192.168.50.100
  |
  v
ha1 : service actif


APRÈS LE BASCULEMENT

Client
  |
  v
192.168.50.100
  |
  v
ha2 : service actif
```

Les utilisateurs peuvent continuer à utiliser le même point d'accès, sous réserve du temps de détection, de la mise à jour des informations réseau et du comportement des connexions en cours.

### 4.3 La VIP ne transporte pas les données à elle seule

L'adresse virtuelle représente un point d'accès. Elle ne copie pas les fichiers du serveur principal vers le serveur de secours.

Si le site Web utilise un contenu différent sur chaque machine, le changement de serveur peut afficher un contenu incorrect.

Il faut donc prévoir une méthode de distribution des données, par exemple :

- Déploiement identique des fichiers sur les deux serveurs.
- Gestion de configuration.
- Synchronisation adaptée aux besoins.
- Stockage partagé lorsque l'architecture le justifie.
- Réplication propre à l'application pour les données dynamiques.

Une VIP ne remplace ni le stockage, ni la réplication des données.

## 5. Keepalived : présentation

### 5.1 À quoi sert Keepalived ?

Keepalived est un logiciel Linux de haute disponibilité.

Dans le scénario étudié, son rôle principal est de gérer l'adresse IP virtuelle en s'appuyant sur **VRRP** (*Virtual Router Redundancy Protocol*).

Chaque serveur exécute Keepalived. Les instances échangent des annonces permettant de déterminer quelle machine porte la VIP.

Keepalived permet également de surveiller certains états locaux, notamment au moyen de scripts de vérification.

Documentation officielle : https://keepalived.org/documentation/user-guide/

### 5.2 Les rôles MASTER et BACKUP

Dans une configuration VRRP classique, les instances Keepalived peuvent avoir des rôles initiaux différents.

- `MASTER` : rôle initial privilégié dans la configuration.
- `BACKUP` : instance de secours.
- `priority` : priorité utilisée pour déterminer quelle instance devrait être active.

La priorité la plus élevée l'emporte normalement lorsque les conditions VRRP et les politiques de préemption le permettent.

Exemple :

```text
ha1
  IP : 192.168.50.11
  Priorité : 110
  État habituel : MASTER
  VIP : 192.168.50.100


ha2
  IP : 192.168.50.12
  Priorité : 100
  État habituel : BACKUP
  VIP : absente
```

Si ha1 devient indisponible, ha2 peut devenir le nouveau détenteur de la VIP.

### 5.3 Fonctionnement simplifié de VRRP

VRRP permet à plusieurs équipements de participer à la gestion d'une adresse virtuelle.

Les instances échangent des annonces. Une instance active annonce son état et permet aux autres de détecter la disparition des annonces attendues.

Le protocole contribue à organiser le basculement de l'adresse.

```text
              RÉSEAU COMMUN
                    |
          +---------+---------+
          |                   |
          v                   v
     +---------+         +---------+
     |   ha1   |         |   ha2   |
     | Priorité|         | Priorité|
     |   110   |         |   100   |
     +---------+         +---------+
          |                   |
          +------ VRRP -------+
                    |
                    v
           Élection du détenteur
              de la VIP
```

Une panne de serveur est un exemple de condition détectable. Une panne du processus applicatif est différente : le serveur peut rester en ligne alors que Nginx ne répond plus.

C'est pourquoi la surveillance de l'application est importante.

### 5.4 La VIP et le réseau

La VIP doit être compatible avec le réseau dans lequel l'instance la porte.

Dans le laboratoire, les serveurs partagent le réseau `192.168.50.0/24`.

Cela signifie que :

- L'adresse doit être disponible.
- Les clients doivent pouvoir atteindre le réseau.
- Les interfaces doivent être correctement configurées.
- Les échanges VRRP doivent être autorisés.
- Le réseau doit permettre la mise à jour des informations de voisinage, notamment ARP en IPv4.

Si les serveurs sont séparés par un réseau qui ne permet pas le fonctionnement du protocole tel qu'il est configuré, le basculement peut échouer.

### 5.5 VRRP et pare-feu

VRRP utilise le protocole IP numéro 112. Ce n'est pas un port TCP ou UDP classique.

Le réseau et les règles de filtrage doivent autoriser les annonces VRRP selon le mode utilisé :

- Multicast, lorsque l'environnement le permet.
- Unicast, lorsque les pairs sont explicitement configurés et que l'architecture le prend en charge.

Certains environnements virtualisés ou réseaux cloud filtrent le multicast ou imposent des règles particulières. Une configuration adaptée peut donc être nécessaire.

### 5.6 Une VIP ne garantit pas une session sans interruption

Lors d'un basculement, l'adresse IP peut réapparaître sur un autre serveur.

Cela ne signifie pas que toutes les connexions TCP déjà établies continueront forcément sans interruption.

Les clients peuvent devoir réessayer leurs connexions. L'application doit gérer correctement les reconnexions et les erreurs temporaires.

Pour une application critique, il faut mesurer le comportement réel et ne pas promettre une continuité absolue à partir de la seule présence de Keepalived.

## 6. Installer Keepalived sur Ubuntu Server

### 6.1 Vérifier les adresses et les interfaces

Sur chaque serveur, exécute :

```bash
hostname
```

Puis :

```bash
ip -br address
```

La sortie doit permettre d'identifier l'interface qui porte l'adresse utilisée pour le réseau du laboratoire.

Exemple conceptuel :

```text
ha1
ens18    UP    192.168.50.11/24

ha2
ens18    UP    192.168.50.12/24
```

Le nom `ens18` est un exemple. Ton interface peut s'appeler `ens33`, `enp0s3`, `eth0` ou autrement.

N'utilise pas le nom d'interface d'un exemple sans vérifier celui qui existe sur tes machines.

### 6.2 Mettre à jour les listes de paquets

Sur les deux serveurs :

```bash
sudo apt update
```

L'installation des mises à jour doit suivre la politique de maintenance de ton système. Dans un environnement de production, évite d'effectuer de grandes opérations de mise à jour sur les deux serveurs en même temps.

### 6.3 Installer Keepalived et Nginx

Sur ha1 et ha2 :

```bash
sudo apt install keepalived nginx curl
```

Dans ce laboratoire :

- Keepalived gère l'adresse virtuelle.
- Nginx fournit le service Web.
- `curl` permet de vérifier que le service répond.

Vérifie les versions installées :

```bash
keepalived --version
nginx -v
```

Les options disponibles peuvent varier selon la version fournie par la distribution.

### 6.4 Vérifier Nginx

Sur chaque serveur :

```bash
sudo systemctl status nginx
```

Puis :

```bash
curl http://127.0.0.1/
```

Si Nginx fonctionne, la requête locale doit renvoyer une réponse HTTP.

Pour personnaliser la page du laboratoire :

```bash
echo "Service Web actif sur $(hostname)" |
    sudo tee /var/www/html/index.html
```

Vérifie à nouveau le résultat :

```bash
curl http://127.0.0.1/
```

Les pages peuvent différer entre les deux serveurs ; cette différence sera utile pour observer le basculement.

Avant de passer à Keepalived, assure-toi que Nginx fonctionne sur les deux machines.

## 7. Configurer Keepalived

### 7.1 Le fichier de configuration

Le fichier de configuration conventionnel est :

`/etc/keepalived/keepalived.conf`

Il décrit notamment les paramètres VRRP et, selon les besoins, les vérifications de santé et les adresses virtuelles.

Avant de modifier un fichier système, il est conseillé d'en conserver une copie :

```bash
sudo cp /etc/keepalived/keepalived.conf \
    /etc/keepalived/keepalived.conf.bak
```

### 7.2 Configurer le serveur ha1

Sur ha1, ouvre le fichier :

```bash
sudo nano /etc/keepalived/keepalived.conf
```

Pour ce laboratoire, utilise une configuration de type unicast afin de désigner explicitement l'autre nœud. Le réseau doit toujours autoriser le protocole VRRP.

```conf
global_defs {
    router_id HA1
}

vrrp_script chk_nginx {
    script "/usr/local/sbin/check_nginx.sh"
    interval 2
    timeout 2
    fall 2
    rise 2
    weight -20
}

vrrp_instance VI_WEB {
    state MASTER
    interface ens18
    virtual_router_id 51
    priority 110
    advert_int 1

    unicast_src_ip 192.168.50.11

    unicast_peer {
        192.168.50.12
    }

    virtual_ipaddress {
        192.168.50.100/24 dev ens18
    }

    track_script {
        chk_nginx
    }
}
```

Vérifie attentivement :

- `interface` correspond à l'interface réelle.
- `unicast_src_ip` correspond à l'adresse fixe de ha1.
- `unicast_peer` correspond à l'adresse fixe de ha2.
- L'adresse virtuelle est libre.
- `virtual_router_id` sera identique sur les deux nœuds.
- `priority` est supérieure à celle de ha2.

### 7.3 Comprendre cette configuration

`global_defs` définit des paramètres généraux, notamment un identifiant local.

`vrrp_instance` définit l'instance qui gère l'adresse virtuelle.

`state MASTER` indique le rôle initial souhaité par cette configuration.

`interface ens18` définit l'interface utilisée.

`virtual_router_id 51` identifie le groupe VRRP. Cet identifiant doit être cohérent entre les pairs concernés et choisi pour éviter les conflits avec d'autres groupes sur le réseau.

`priority 110` indique une priorité supérieure à celle du serveur de secours.

`advert_int 1` définit l'intervalle normal des annonces VRRP, en secondes.

`unicast_src_ip` indique l'adresse source locale des communications VRRP en unicast.

`unicast_peer` identifie l'autre nœud.

`virtual_ipaddress` déclare l'adresse virtuelle gérée par l'instance.

`track_script` demande à Keepalived de tenir compte du résultat du script de contrôle.

### 7.4 Configurer le serveur ha2

Sur ha2, ouvre le même fichier :

```bash
sudo nano /etc/keepalived/keepalived.conf
```

Utilise cette configuration :

```conf
global_defs {
    router_id HA2
}

vrrp_script chk_nginx {
    script "/usr/local/sbin/check_nginx.sh"
    interval 2
    timeout 2
    fall 2
    rise 2
    weight -20
}

vrrp_instance VI_WEB {
    state BACKUP
    interface ens18
    virtual_router_id 51
    priority 100
    advert_int 1

    unicast_src_ip 192.168.50.12

    unicast_peer {
        192.168.50.11
    }

    virtual_ipaddress {
        192.168.50.100/24 dev ens18
    }

    track_script {
        chk_nginx
    }
}
```

La configuration est très semblable à celle de ha1.

Les principales différences sont :

| Paramètre | ha1 | ha2 |
|---|---|---|
| `router_id` | `HA1` | `HA2` |
| `state` | `MASTER` | `BACKUP` |
| `priority` | `110` | `100` |
| `unicast_src_ip` | `192.168.50.11` | `192.168.50.12` |
| `unicast_peer` | `192.168.50.12` | `192.168.50.11` |

Les deux configurations doivent utiliser le même identifiant VRRP, la même VIP et des paramètres VRRP compatibles.

### 7.5 Pourquoi ne pas ajouter une authentification VRRP ancienne au hasard ?

Certaines configurations historiques de Keepalived utilisent un bloc `authentication` avec `auth_type PASS` et un mot de passe.

Cette méthode ne doit pas être considérée comme une protection cryptographique forte : elle est historique et n'offre pas une protection complète contre un acteur malveillant présent sur le réseau.

Il ne faut donc pas ajouter cette configuration en supposant qu'elle sécurise fortement les échanges.

Dans un environnement sensible, protège le réseau VRRP, restreins les pairs autorisés et applique les mécanismes de sécurité adaptés au contexte.

La documentation officielle Keepalived décrit les options disponibles et leurs limites : https://keepalived.org/documentation/keepalived.conf/

## 8. Vérifier l'état du service avec un script

### 8.1 Pourquoi surveiller Nginx ?

Keepalived peut observer l'état de l'interface et l'état du service par l'intermédiaire d'un script.

Considérons cette situation :

```text
Serveur ha1
|
+-- Linux : fonctionne
|
+-- Interface réseau : fonctionne
|
+-- Keepalived : fonctionne
|
+-- Nginx : ARRÊTÉ
```

Le serveur n'est pas en panne, mais le site Web ne répond pas.

Un test qui vérifie seulement l'existence de la machine ne détectera pas correctement cette défaillance applicative.

### 8.2 Créer le script de contrôle

Sur les deux serveurs, crée le fichier :

`/usr/local/sbin/check_nginx.sh`

Commande :

```bash
sudo nano /usr/local/sbin/check_nginx.sh
```

Contenu :

```bash
#!/bin/sh

systemctl is-active --quiet nginx || exit 1

curl --fail \
     --silent \
     --show-error \
     --max-time 2 \
     http://127.0.0.1/ \
     >/dev/null 2>&1 || exit 1

exit 0
```

Ce script effectue deux vérifications :

1. Il vérifie que le service Nginx est actif.
2. Il vérifie qu'une requête HTTP locale aboutit.

Si une vérification échoue, il renvoie un code d'erreur. Si tout fonctionne, il renvoie le code `0`.

### 8.3 Protéger le script

Le script sera exécuté par un service système privilégié. Il doit être accessible en lecture et exécution par le contexte prévu, sans devenir modifiable par des utilisateurs non autorisés.

Sur chaque serveur :

```bash
sudo chown root:root /usr/local/sbin/check_nginx.sh
sudo chmod 750 /usr/local/sbin/check_nginx.sh
```

Teste-le :

```bash
sudo /usr/local/sbin/check_nginx.sh
echo $?
```

Résultat attendu :

- `0` si Nginx fonctionne et renvoie une réponse HTTP valide.
- Une valeur différente de `0` si le contrôle échoue.

### 8.4 Comprendre `fall`, `rise` et `weight`

Dans notre configuration :

```conf
vrrp_script chk_nginx {
    script "/usr/local/sbin/check_nginx.sh"
    interval 2
    timeout 2
    fall 2
    rise 2
    weight -20
}
```

`interval 2` demande une vérification périodique toutes les deux secondes.

`timeout 2` limite le temps d'exécution du contrôle selon la configuration.

`fall 2` demande deux échecs consécutifs avant de considérer le contrôle comme en échec.

`rise 2` demande deux réussites consécutives pour considérer le contrôle comme rétabli.

`weight -20` réduit la priorité effective de l'instance lorsque le script est considéré comme en échec, selon les règles de suivi de Keepalived.

Dans notre exemple, la priorité initiale de ha1 est de 110. Si son contrôle échoue et que sa priorité devient inférieure à celle de ha2, ce dernier peut prendre la VIP.

Ce comportement dépend de l'état de VRRP, des priorités et des politiques de préemption. Il faut toujours le vérifier pendant les tests.

## 9. Démarrer et vérifier Keepalived

### 9.1 Démarrer le service

Sur les deux serveurs :

```bash
sudo systemctl enable --now keepalived
```

Cette commande active le service au démarrage et le lance immédiatement.

Vérifie son état :

```bash
sudo systemctl status keepalived
```

Si le service échoue au démarrage, lis d'abord le message d'erreur et les journaux avant d'effectuer des modifications supplémentaires.

### 9.2 Vérifier les journaux

Pour examiner les journaux récents :

```bash
sudo journalctl -u keepalived --no-pager -n 100
```

Pour suivre les événements en direct :

```bash
sudo journalctl -u keepalived -f
```

Les journaux permettent notamment de rechercher les erreurs de syntaxe, les changements de rôle et certains problèmes liés aux scripts.

### 9.3 Vérifier la VIP

Sur ha1 :

```bash
ip address show ens18
```

Sur ha2 :

```bash
ip address show ens18
```

Dans la situation nominale prévue, la VIP `192.168.50.100` doit être portée par le nœud actif.

Schéma :

```text
ha1
|
+-- 192.168.50.11
+-- 192.168.50.100   <- VIP


ha2
|
+-- 192.168.50.12
+-- pas de VIP
```

Le détenteur réel de la VIP doit être vérifié, et non supposé à partir du mot `MASTER` dans le fichier de configuration.

### 9.4 Tester le service par la VIP

Depuis une machine ayant accès au réseau :

```bash
curl http://192.168.50.100/
```

Si la page attendue apparaît, l'adresse virtuelle est joignable et le service répond.

Sur le serveur actif :

```bash
ip -br address
```

Cette commande fournit une vue rapide des adresses présentes sur les interfaces.

Si la VIP n'apparaît sur aucun serveur, vérifie l'état de Keepalived, les configurations, le réseau et les journaux.

## 10. Simuler un basculement Keepalived

### 10.1 Premier test : arrêt de Keepalived sur le principal

Ce test doit être réalisé dans le laboratoire.

Sur ha1 :

```bash
sudo systemctl stop keepalived
```

Puis, sur ha2 :

```bash
ip address show ens18
```

Si les conditions de VRRP sont satisfaites, ha2 devrait prendre en charge l'adresse virtuelle après la détection de la disparition du rôle actif.

Vérifie l'accès au service :

```bash
curl http://192.168.50.100/
```

Le contenu affiché peut maintenant provenir de ha2.

### 10.2 Observer le nouveau détenteur

Sur ha1 :

```bash
ip address show ens18
```

Sur ha2 :

```bash
ip address show ens18
```

Le résultat attendu est :

```text
Avant le test
VIP sur ha1

Après l'arrêt de Keepalived sur ha1
VIP sur ha2
```

Le délai observé dépend de la détection, des annonces VRRP et de la configuration réseau.

### 10.3 Revenir à l'état nominal

Sur ha1 :

```bash
sudo systemctl start keepalived
```

Dans notre configuration, ha1 possède une priorité supérieure à ha2. Le comportement par défaut de préemption peut donc lui permettre de récupérer la VIP après son retour, lorsque les conditions nécessaires sont réunies.

Vérifie les journaux et l'emplacement de l'adresse.

### 10.4 Deuxième test : panne de Nginx

Le serveur physique et Keepalived peuvent fonctionner alors que Nginx est arrêté.

Pour tester ce scénario, vérifie d'abord que ha1 est le détenteur de la VIP.

Puis, sur ha1 :

```bash
sudo systemctl stop nginx
```

Observe les journaux :

```bash
sudo journalctl -u keepalived -f
```

La surveillance doit détecter l'échec de Nginx et affecter la priorité. Le serveur ha2 peut alors prendre la VIP.

Teste ensuite :

```bash
curl http://192.168.50.100/
```

Le but est de confirmer que la VIP est transférée lorsque le service Web n'est plus capable de répondre, même si le système Linux reste actif.

### 10.5 Attention au redémarrage automatique de Nginx

Dans ce laboratoire Keepalived, Nginx est un service système indépendant. Le script contrôle son état, mais Keepalived ne possède pas automatiquement toutes les capacités d'un gestionnaire de ressources comme Pacemaker.

Selon la configuration locale de systemd, un service peut être relancé automatiquement par d'autres mécanismes. Il faut donc observer les journaux et ne pas supposer qu'un simple arrêt manuel constitue toujours une panne persistante.

### 10.6 Ce que ce test prouve réellement

Un test réussi démontre que le mécanisme prévu réagit dans les conditions qui ont été testées.

Il ne prouve pas que tous les scénarios de panne seront traités correctement.

Il faut encore tester ou examiner :

- Une perte de connectivité entre les nœuds.
- Une panne de l'interface réseau.
- Un problème du réseau de niveau 2.
- Un conflit d'adresse IP.
- Une erreur de configuration.
- Un service qui répond localement mais n'est pas accessible aux clients.
- La cohérence du contenu des deux serveurs.
- Le comportement des connexions des utilisateurs.

La haute disponibilité se valide par des scénarios de test reproductibles.

## 11. Limites de Keepalived

### 11.1 Keepalived ne synchronise pas automatiquement les fichiers

Les fichiers présents sur ha1 ne sont pas copiés automatiquement sur ha2 simplement parce que la VIP est gérée par Keepalived.

Si le site Web est mis à jour sur un seul serveur, il faut distribuer le contenu de manière cohérente.

Une solution simple consiste à publier la même version du site sur les deux machines avec le même processus de déploiement.

### 11.2 Keepalived ne remplace pas une base de données répliquée

Si une application utilise une base de données, déplacer la VIP ne garantit pas que la base de données soit disponible sur le deuxième serveur.

Il faut concevoir la protection de la base séparément, avec une méthode adaptée à la technologie employée.

### 11.3 Un test local ne garantit pas l'accessibilité externe

Le script de notre laboratoire teste :

`http://127.0.0.1/`

Cette vérification confirme que Nginx répond localement.

Elle ne prouve pas que les clients peuvent accéder au serveur depuis leur réseau.

Une panne du commutateur externe, une règle de pare-feu ou une erreur de routage peut empêcher l'accès des clients alors que le test local reste réussi.

Pour un environnement professionnel, il faut adapter les contrôles à la véritable architecture.

### 11.4 Keepalived ne doit pas être utilisé seul pour chaque problème de haute disponibilité

Si une application utilise plusieurs ressources dépendantes, un stockage partagé et des règles de démarrage ou d'arrêt complexes, un gestionnaire de ressources de cluster peut être nécessaire.

C'est là que Pacemaker apporte des mécanismes complémentaires.

## 12. Pacemaker : présentation

### 12.1 À quoi sert Pacemaker ?

Pacemaker est un gestionnaire de ressources de cluster.

Il observe l'état des nœuds et des ressources, applique les règles définies par l'administrateur et peut démarrer, arrêter, surveiller ou déplacer des ressources selon les conditions du cluster.

Une ressource peut être, par exemple :

- Une adresse IP.
- Un service Web.
- Un service de base de données.
- Un système de fichiers.
- Un montage de volume.
- Un service applicatif.
- Un mécanisme de stockage pris en charge.

Contrairement au scénario Keepalived centré sur l'adresse virtuelle, Pacemaker peut gérer un ensemble de ressources interdépendantes.

### 12.2 Architecture de Pacemaker

Une architecture Pacemaker comprend généralement plusieurs composants.

```text
              ADMINISTRATEUR
                    |
                    v
                   pcs
                    |
                    v
              CONFIGURATION
                    |
                    v
                PACEMAKER
          Gestionnaire de ressources
                    |
                    v
                COROSYNC
        Communication et appartenance
              au cluster
                    |
          +---------+---------+
          |                   |
          v                   v
       +------+            +------+
       | ha1  |            | ha2  |
       +------+            +------+
          |                   |
          +---------+---------+
                    |
                    v
           Ressources gérées
           par le cluster
```

Ce schéma montre les rôles fonctionnels et non tous les détails internes du logiciel.

### 12.3 Rôle des composants

**Pacemaker**

Décide quelles ressources doivent être actives, sur quel nœud et selon quelles contraintes.

**Corosync**

Fournit des mécanismes de communication et de gestion de l'appartenance au cluster. Il participe aussi aux informations de quorum utilisées dans l'architecture.

**pcs**

Outil d'administration qui permet de configurer et de contrôler un cluster Pacemaker/Corosync.

**Agents de ressources**

Programmes qui définissent comment démarrer, arrêter et contrôler une ressource donnée.

**Fencing**

Mécanisme permettant d'isoler de manière fiable un nœud qui ne doit plus accéder aux ressources gérées.

Le fencing est particulièrement important pour préserver l'intégrité des données.

Documentation générale Ubuntu : https://ubuntu.com/server/docs/reference/high-availability/

### 12.4 Différence entre Pacemaker et Corosync

Corosync ne remplace pas Pacemaker.

Corosync contribue aux communications et à la connaissance des membres du cluster.

Pacemaker utilise ces informations pour prendre des décisions sur l'emplacement et l'état des ressources.

Une communication correcte entre les nœuds est donc essentielle, mais elle ne suffit pas à définir la stratégie de gestion des applications.

### 12.5 Qu'est-ce qu'une ressource ?

Une ressource est un élément que le cluster sait gérer à travers un agent approprié.

Exemple :

```text
Cluster Pacemaker
|
+-- Ressource VIP
|     |
|     +-- Adresse IP de service
|
+-- Ressource Nginx
|     |
|     +-- Démarrage du service
|     +-- Arrêt du service
|     +-- Vérification du fonctionnement
|
+-- Ressource de stockage, si nécessaire
      |
      +-- Montage contrôlé du système de fichiers
```

Pacemaker peut configurer des contraintes qui définissent les relations entre ces ressources.

Par exemple, le service Web et l'adresse virtuelle peuvent être regroupés pour fonctionner sur le même nœud.

### 12.6 Ressources et dépendances

Supposons que l'application Web ait besoin :

1. D'un stockage monté.
2. D'un service applicatif.
3. D'une adresse IP accessible aux clients.

Dans ce cas, l'ordre de démarrage et les dépendances peuvent être importants.

```text
Stockage disponible
        |
        v
Service applicatif démarré
        |
        v
Adresse de service activée
        |
        v
Accès client
```

L'ordre exact dépend de l'application. Certaines ressources doivent être activées avant les autres ; d'autres doivent être arrêtées dans l'ordre inverse.

Pacemaker permet de définir ces contraintes dans une configuration appropriée.

## 13. Le quorum et le fencing

Cette partie est essentielle. Il ne faut pas apprendre Pacemaker comme un simple outil de redémarrage des services : un cluster doit aussi protéger l'intégrité de ses ressources.

### 13.1 Le problème du split-brain

Imaginons un cluster à deux nœuds qui perd sa communication interne.

Chaque nœud reste en fonctionnement, mais ils ne peuvent plus communiquer entre eux.

```text
           AVANT LA PANNE

             +-------+
             | ha1   |
             +-------+
                 |
             Communication
                 |
             +-------+
             | ha2   |
             +-------+


           APRÈS LA PANNE

          +-------+       +-------+
          | ha1   |       | ha2   |
          +-------+       +-------+
              X               X
              Pas de communication
```

Si chaque nœud décide indépendamment qu'il peut exploiter la même ressource, ils peuvent entrer en conflit.

Dans le cas d'une ressource de stockage ou d'une base de données, ce comportement pourrait provoquer une corruption ou une perte de données.

Ce problème est appelé *split-brain*.

### 13.2 Qu'est-ce que le quorum ?

Le quorum est un mécanisme de décision qui détermine si le cluster dispose du nombre de votes requis pour continuer à fonctionner selon sa politique.

Dans une configuration classique à plusieurs nœuds, une majorité de votes est nécessaire. Les règles exactes dépendent de la configuration du cluster, du nombre de nœuds et des mécanismes de quorum retenus.

Exemple conceptuel avec trois nœuds :

```text
ha1 : 1 vote
ha2 : 1 vote
ha3 : 1 vote

Total : 3 votes
Majorité : 2 votes
```

Si ha1 devient indisponible, ha2 et ha3 peuvent conserver la majorité.

Dans un cluster à deux nœuds, la situation est plus délicate. Il faut concevoir explicitement le scénario de perte d'un membre et la protection contre un état incohérent.

### 13.3 Le quorum ne remplace pas le fencing

Le quorum et le fencing sont liés, mais remplissent des fonctions différentes.

Le quorum aide le cluster à décider quelle partie a le droit de continuer à gérer les ressources.

Le fencing permet d'isoler le nœud dont la situation ne garantit plus qu'il a réellement cessé d'utiliser une ressource.

Il peut s'agir, selon l'architecture, d'une action sur l'alimentation, l'hyperviseur ou un mécanisme pris en charge capable d'interrompre de manière fiable le nœud concerné.

### 13.4 Pourquoi le fencing est-il important ?

Supposons que ha1 ne réponde plus au réseau du cluster, mais qu'il continue à fonctionner et à écrire sur un stockage partagé.

Si ha2 démarre ensuite la même ressource sans s'assurer que ha1 a réellement cessé de l'utiliser, les deux nœuds risquent de modifier simultanément les mêmes données.

Le fencing sert à rendre la situation suffisamment sûre avant que le cluster réattribue la ressource.

Il peut impliquer un redémarrage forcé ou une isolation du nœud selon le périphérique de fencing disponible.

**En production, ne désactive pas le fencing pour faire disparaître une erreur de cluster.** Une configuration qui prétend qu'un nœud est isolé sans disposer d'un mécanisme d'isolation fiable peut compromettre l'intégrité des données.

### 13.5 Les équipements de fencing

Le mécanisme à configurer dépend de l'infrastructure.

Il peut s'agir notamment de :

- Contrôleurs de gestion matérielle compatibles.
- Interfaces de gestion d'alimentation prises en charge.
- API d'hyperviseur ou d'infrastructure virtuelle.
- Dispositifs d'isolation du stockage selon une architecture supportée.

Il ne faut pas inventer une commande universelle de fencing : les paramètres et agents dépendent de l'équipement et de la plateforme.

Un dispositif de fencing doit être testé avant d'héberger des ressources critiques.

Documentation : https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/

## 14. Comparer Keepalived et Pacemaker

### 14.1 Comparaison générale

| Critère | Keepalived | Pacemaker |
|---|---|---|
| Objectif fréquent | VIP, VRRP et certains scénarios d'équilibrage | Gestion de ressources de cluster |
| Basculement d'une VIP | Oui | Oui, avec une ressource adaptée |
| Surveillance d'un service | Oui, notamment par scripts de suivi | Oui, par agents de ressources |
| Gestion de plusieurs ressources dépendantes | Plus limitée dans le rôle VRRP | Fonction centrale |
| Gestion de contraintes d'ordre et de placement | Pas l'objectif principal de VRRP | Oui |
| Gestion du quorum | Ne remplace pas un gestionnaire de quorum de cluster | Intégrée à l'architecture avec Corosync |
| Fencing de nœuds | Ne remplace pas le fencing de Pacemaker | Mécanisme de sécurité essentiel en cluster |
| Complexité d'exploitation | Relativement simple pour une VIP | Plus exigeante |
| Exemple courant | VIP devant des serveurs Web | VIP et service coordonnés, stockage, applications |

### 14.2 Quand choisir Keepalived ?

Keepalived est un choix raisonnable lorsque le besoin consiste principalement à :

- Fournir une adresse virtuelle sur un réseau.
- Faire basculer cette adresse entre deux serveurs.
- Surveiller un processus ou un service simple.
- Construire un point d'accès réseau résilient.
- Utiliser certaines fonctions d'équilibrage de charge prises en charge.

Il convient notamment à un laboratoire de haute disponibilité réseau.

### 14.3 Quand choisir Pacemaker ?

Pacemaker est pertinent lorsque le besoin nécessite de gérer les ressources de manière coordonnée :

- Une adresse virtuelle.
- Un service applicatif.
- Un système de fichiers.
- Des dépendances de démarrage.
- Des contraintes de placement.
- Des politiques de reprise.
- Des ressources nécessitant une isolation contrôlée des nœuds.

Cela ne signifie pas que chaque application doit être mise dans Pacemaker. Il faut évaluer sa compatibilité, ses agents de ressources et son modèle de données.

### 14.4 Peut-on utiliser les deux ?

Oui, une architecture peut employer Keepalived et Pacemaker à des niveaux distincts si leurs rôles sont clairement définis.

Par exemple, une infrastructure de grande taille pourrait employer Keepalived pour une fonction réseau spécifique et Pacemaker pour d'autres ressources.

Toutefois, **ne configure pas simultanément Keepalived et Pacemaker pour gérer indépendamment la même adresse virtuelle sur les mêmes nœuds**.

Cela créerait deux gestionnaires susceptibles de prendre des décisions contradictoires sur l'adresse IP.

Il faut choisir quel mécanisme possède la responsabilité de chaque ressource.

## 15. Découvrir `pcs` pour administrer Pacemaker

### 15.1 Qu'est-ce que `pcs` ?

`pcs` est un outil d'administration utilisé pour configurer et contrôler les clusters Pacemaker/Corosync.

Il permet notamment de :

- Préparer un cluster.
- Authentifier les hôtes pour les opérations administratives.
- Démarrer ou arrêter le cluster.
- Consulter son état.
- Créer des ressources.
- Configurer certaines propriétés.
- Examiner les ressources et leurs contraintes.

Sur les versions modernes d'Ubuntu Server, la documentation Ubuntu recommande `pcs` pour l'administration des clusters de haute disponibilité basés sur Pacemaker.

### 15.2 Installer les composants sur Ubuntu

Pour étudier le cluster dans un laboratoire, les paquets usuels comprennent :

```bash
sudo apt update

sudo apt install pacemaker corosync pcs resource-agents fence-agents
```

La disponibilité exacte des paquets et des agents dépend de la version de la distribution et des dépôts activés.

Démarrer le service d'administration :

```bash
sudo systemctl enable --now pcsd
```

Vérifier son état :

```bash
sudo systemctl status pcsd
```

Dans certains environnements, des composants supplémentaires seront nécessaires pour la surveillance ou le fencing.

### 15.3 Préparer les noms des serveurs

Les deux nœuds doivent pouvoir résoudre les noms utilisés par le cluster.

Par exemple :

```text
192.168.60.11  ha1
192.168.60.12  ha2
```

Ces entrées peuvent être fournies par le DNS ou par un fichier `/etc/hosts` dans un laboratoire isolé.

Vérifie :

```bash
getent hosts ha1
getent hosts ha2
```

Une résolution cohérente des noms simplifie l'administration et les diagnostics.

### 15.4 Configurer le compte `hacluster`

Les procédures d'installation de `pcs` créent habituellement un compte d'administration de cluster nommé `hacluster`.

Dans un environnement de laboratoire, le mot de passe de ce compte doit être configuré selon les instructions de la distribution et protégé comme un secret d'administration.

Il ne faut pas réutiliser un mot de passe faible ou partager ce compte sans contrôle entre les administrateurs.

### 15.5 Authentifier les hôtes

La commande de gestion d'authentification dépend de la version installée. Sur les versions qui prennent en charge cette syntaxe, l'administrateur peut effectuer l'authentification des nœuds avec `pcs host auth`.

Exemple à adapter :

```bash
sudo pcs host auth ha1 ha2 -u hacluster
```

Le mot de passe du compte sera demandé selon le comportement de la version.

Si la commande est refusée, vérifie l'aide intégrée et la documentation correspondant à la version de `pcs` :

```bash
pcs host auth --help
```

Il est préférable d'adapter la procédure à l'environnement que de copier aveuglément une syntaxe provenant d'une autre version.

### 15.6 Créer un cluster Pacemaker

Après avoir vérifié le réseau, les nœuds, l'authentification et les prérequis de sécurité, la commande de création sur les versions qui utilisent la syntaxe moderne peut ressembler à ceci :

```bash
sudo pcs cluster setup ha-web ha1 ha2 --start --enable
```

Cette commande représente un exemple pédagogique. Vérifie d'abord la syntaxe prise en charge et les conditions attendues par la version de `pcs` de ton environnement.

La création d'un cluster ne suffit pas à obtenir une infrastructure de production prête à héberger des données critiques. Il faut notamment préparer le quorum, le fencing, les ressources, les droits, les réseaux et les tests.

### 15.7 Vérifier l'état du cluster

```bash
sudo pcs status
```

Pour examiner la configuration :

```bash
sudo pcs cluster config
```

Si la version offre une option détaillée :

```bash
sudo pcs status --full
```

La sortie permet de vérifier l'état des nœuds et des ressources, les informations de cluster et certains problèmes de fonctionnement.

Si le cluster n'est pas sain, corrige les erreurs de configuration avant d'ajouter des ressources critiques.

### 15.8 Pourquoi nous ne désactivons pas le fencing dans ce cours

Certains tutoriels d'introduction désactivent le fencing afin d'afficher plus rapidement les commandes de gestion des ressources.

Cette facilité pédagogique n'est pas une méthode de déploiement de production.

Le fencing permet notamment de garantir qu'un ancien détenteur d'une ressource ne continue pas à utiliser cette ressource lorsque le cluster prend une décision de reprise.

Dans ce cours, la règle est donc simple : **ne déploie pas de ressources de production sur un cluster Pacemaker tant que son mécanisme de fencing et son quorum n'ont pas été correctement conçus et validés.**

## 16. Première ressource Pacemaker : comprendre la VIP et Nginx

Cette section présente la configuration logique d'un service Web géré par Pacemaker.

Les commandes de création des ressources ne doivent être exécutées qu'après avoir préparé un cluster dont le quorum, le fencing et la sécurité sont correctement configurés. Les noms d'interfaces, les agents disponibles et les paramètres exacts doivent être vérifiés sur la distribution utilisée.

### 16.1 Installer Nginx sur les deux nœuds

Sur ha1 et ha2 :

```bash
sudo apt update
sudo apt install nginx
```

Vérifie que le service peut être exécuté localement :

```bash
curl http://127.0.0.1/
```

Avant d'utiliser Pacemaker pour gérer ce service, vérifie la configuration Nginx sur les deux nœuds.

### 16.2 Un service contrôlé par Pacemaker ne doit pas être géré indépendamment

Lorsque Pacemaker devient propriétaire de la gestion d'un service, il faut éviter qu'un autre mécanisme lance ou arrête simultanément ce service sans tenir compte de l'état du cluster.

Sinon, Pacemaker peut croire qu'une ressource est arrêtée alors qu'un service a été lancé manuellement, ou inversement.

La configuration de démarrage automatique et le contrôle manuel du service doivent donc être adaptés à la procédure de gestion du cluster.

Ne fais pas de `systemctl enable` ou de `systemctl start` une seconde méthode permanente d'administration du service géré par Pacemaker.

### 16.3 Définir la ressource d'adresse IP

Une ressource utilisant l'agent `IPaddr2` peut gérer une adresse virtuelle.

Exemple de commande sur un cluster prêt à gérer des ressources :

```bash
sudo pcs resource create WebVIP \
    ocf:heartbeat:IPaddr2 \
    ip=192.168.60.110 \
    cidr_netmask=24 \
    nic=ens18 \
    op monitor interval=30s
```

Les informations suivantes doivent être adaptées :

- `ip` : adresse virtuelle libre.
- `cidr_netmask` : préfixe du réseau.
- `nic` : interface concernée.
- `interval` : intervalle de vérification de la ressource.

Le nom de l'agent doit être disponible sur les nœuds. La commande `pcs resource describe` permet d'examiner les propriétés d'un agent pris en charge.

Exemple :

```bash
sudo pcs resource describe ocf:heartbeat:IPaddr2
```

### 16.4 Définir la ressource Nginx

Selon les agents disponibles, la ressource du service peut utiliser l'agent `systemd`.

Exemple :

```bash
sudo pcs resource create WebService \
    systemd:nginx \
    op monitor interval=30s
```

Cette commande indique au cluster de gérer le service Nginx à l'aide de son unité systemd.

Il faut vérifier que cet agent est disponible et qu'il possède le comportement attendu pour la version de la distribution.

### 16.5 Regrouper les ressources

Les ressources du groupe sont normalement placées ensemble sur le même nœud. Elles sont démarrées dans l'ordre du groupe et arrêtées dans l'ordre inverse.

Exemple :

```bash
sudo pcs resource group add web-stack WebVIP WebService
```

Il faut vérifier que la version de `pcs` prend en charge cette syntaxe.

La configuration finale doit être contrôlée avec les commandes d'état et de configuration des ressources.

### 16.6 Examiner la ressource

```bash
sudo pcs resource status
```

Pour examiner les paramètres :

```bash
sudo pcs resource config
```

Le groupe doit être actif sur un nœud conformément aux contraintes et aux ressources définies.

### 16.7 Ce que Pacemaker ne fait pas automatiquement

Créer une ressource Nginx et une VIP ne copie pas automatiquement le contenu du site entre les nœuds.

La configuration de Nginx, les fichiers Web, les certificats, les secrets et les données nécessaires doivent être disponibles sur chaque nœud susceptible d'héberger le service.

De même, si le service dépend d'une base de données ou d'un montage de fichiers, il faut concevoir et gérer ces dépendances explicitement.

Une ressource Pacemaker n'est pas une solution universelle de réplication des données.

## 17. Comprendre l'organisation des ressources Pacemaker

### 17.1 Le groupe de ressources

Un groupe de ressources permet d'organiser des ressources qui doivent fonctionner ensemble.

Exemple :

```text
Groupe : web-stack
|
+-- WebVIP
|
+-- WebService
```

L'objectif est que les ressources du groupe soient colocées sur le même nœud.

Cet exemple suppose que les paramètres et les agents utilisés sont compatibles avec l'application.

### 17.2 Contraintes de placement

Une contrainte de placement permet d'exprimer une préférence ou une exigence concernant le nœud sur lequel une ressource peut fonctionner.

Exemple conceptuel :

```text
WebService
    |
    +-- Préférence : ha1
    |
    +-- Si ha1 devient indisponible :
           possibilité de reprise sur ha2,
           selon la configuration du cluster
```

Il faut distinguer une préférence et une règle qui interdit absolument un nœud.

Une contrainte trop stricte peut empêcher la reprise si aucun nœud ne satisfait les conditions.

### 17.3 Contraintes d'ordre

Les contraintes d'ordre définissent la séquence dans laquelle les ressources doivent être démarrées ou arrêtées.

Exemple :

```text
Stockage
    |
    v
Application
    |
    v
Adresse de service
```

L'ordre correct dépend du comportement du service. Dans certains cas, rendre une adresse disponible avant le démarrage de l'application peut permettre à des clients de tenter une connexion prématurée. Dans d'autres cas, l'ordre inverse peut être préférable.

Les contraintes doivent refléter le véritable besoin de l'application.

### 17.4 Surveiller les ressources

Une ressource doit pouvoir être contrôlée périodiquement pour déterminer si elle est réellement opérationnelle.

La surveillance n'est utile que si le test correspond à un état significatif pour l'application.

Par exemple :

- Vérifier qu'un processus existe.
- Vérifier qu'un port répond.
- Vérifier qu'une application renvoie une réponse valide.
- Vérifier qu'un système de fichiers est monté.
- Vérifier qu'une ressource de stockage est disponible.

Un test trop superficiel risque de laisser passer des pannes applicatives. Un test trop agressif peut provoquer des basculements inutiles.

## 18. Le service géré et l'accès réseau

### 18.1 Une interface réseau peut fonctionner alors que l'application est en panne

La disponibilité de l'interface réseau est un état différent de celui de l'application.

```text
Serveur
|
+-- Carte réseau : UP
|
+-- Adresse IP : présente
|
+-- Route réseau : valide
|
+-- Nginx : en erreur
|
+-- Service Web : indisponible
```

Il faut donc distinguer la santé de l'hôte, la santé du réseau et la santé du service.

### 18.2 Différents niveaux de contrôle

Un contrôle peut examiner :

1. L'état physique ou logique de l'interface.
2. La connectivité entre les nœuds.
3. La présence d'une adresse IP.
4. L'état du processus.
5. La réponse d'une requête HTTP.
6. Le fonctionnement de la dépendance applicative.
7. Le résultat visible depuis un client.

Ces contrôles ne sont pas interchangeables.

Un `ping` réussi ne démontre pas que le serveur Web est fonctionnel. Un test local réussi ne démontre pas que le réseau des clients est accessible.

### 18.3 Le choix des contrôles doit être proportionné au risque

Pour un petit site de laboratoire, un test HTTP local peut suffire.

Pour une application métier critique, il peut être nécessaire d'effectuer des contrôles fonctionnels, de vérifier les dépendances et de définir un comportement explicite en cas de perte d'accès aux données.

Le mécanisme de haute disponibilité doit être adapté au besoin réel et non à la seule simplicité du script.

## 19. Sécurité des mécanismes de haute disponibilité

### 19.1 Protéger les accès d'administration

Keepalived et Pacemaker ne remplacent pas une politique de sécurité Linux.

Il faut :

- Limiter les comptes ayant des droits `sudo`.
- Protéger les clés SSH.
- Sécuriser les accès aux fichiers de configuration.
- Protéger les scripts exécutés par les services.
- Appliquer les mises à jour selon une politique définie.
- Contrôler les connexions administratives.
- Surveiller les journaux.
- Limiter l'accès aux réseaux de gestion.

### 19.2 Protéger les fichiers Keepalived

Le fichier de configuration peut définir les adresses virtuelles, les identifiants VRRP, les scripts et les paramètres du service.

Un utilisateur non autorisé ne doit pas pouvoir le modifier.

Vérifie notamment :

```bash
sudo ls -l /etc/keepalived/keepalived.conf
```

Le niveau de permissions doit être adapté à la distribution et à la politique de sécurité.

### 19.3 Protéger les scripts de contrôle

Un script exécuté par un service privilégié ne doit pas être modifiable par un utilisateur qui n'a pas le droit de contrôler le service.

Dans le cas contraire, un acteur pourrait remplacer le script par une commande malveillante.

L'utilisation d'un propriétaire approprié et de permissions restrictives est donc une exigence de sécurité, et non une simple préférence de style.

### 19.4 Séparer les réseaux si nécessaire

Dans un environnement critique, les réseaux de gestion et de service peuvent être séparés selon les exigences de l'architecture.

Les communications de cluster et VRRP doivent uniquement être autorisées là où elles sont nécessaires.

Les règles réseau doivent être cohérentes avec les interfaces, les adresses et les protocoles utilisés.

### 19.5 Ne pas ignorer les erreurs de fencing

Dans un cluster Pacemaker de production, une erreur de fencing est un problème majeur.

Ne supprime pas une ressource de fencing simplement parce qu'elle affiche un état inattendu.

Il faut comprendre si le dispositif peut réellement isoler le nœud, si les permissions sont valides et si le réseau ou l'équipement de gestion est accessible.

La sécurité des données dépend de la qualité de ce mécanisme.

## 20. Diagnostic des problèmes Keepalived

### 20.1 La VIP n'apparaît sur aucun serveur

Vérifie dans l'ordre :

1. Keepalived est-il en fonctionnement sur les deux nœuds ?
2. Le fichier de configuration est-il correct ?
3. L'interface réseau existe-t-elle ?
4. Les adresses IP physiques sont-elles correctes ?
5. Les nœuds utilisent-ils le même `virtual_router_id` ?
6. Les priorités et les états sont-ils cohérents ?
7. Les échanges VRRP passent-ils entre les nœuds ?
8. L'adresse virtuelle est-elle libre ?
9. Le réseau permet-il le mode de communication utilisé ?
10. Les journaux indiquent-ils une erreur ?

Commandes utiles :

```bash
sudo systemctl status keepalived
sudo journalctl -u keepalived --no-pager -n 100
ip -br address
ip route
```

### 20.2 La VIP apparaît sur les deux serveurs

Cette situation est anormale pour le scénario de VIP unique étudié.

Les causes possibles comprennent :

- Une communication VRRP bloquée.
- Une mauvaise configuration des pairs unicast.
- Des `virtual_router_id` différents.
- Un conflit de configuration.
- Une séparation réseau qui empêche les instances de se détecter.
- Un service Keepalived exécuté avec des paramètres différents.

Ne corrige pas simplement le problème en arrêtant un nœud sans comprendre pourquoi les deux instances pensent devoir posséder la VIP.

Vérifie les configurations, les journaux et les échanges réseau.

### 20.3 La VIP est présente, mais le site Web est inaccessible

Le problème peut concerner :

- Nginx.
- Le pare-feu.
- Le routage.
- Le port HTTP.
- Le réseau virtuel.
- Le contenu du site.
- Une erreur de configuration applicative.
- Le service qui répond localement mais pas depuis le réseau client.

Tests :

```bash
curl http://127.0.0.1/
curl http://192.168.50.100/
```

Le premier vérifie le service local. Le second vérifie l'accès via la VIP.

Il faut effectuer ces tests depuis les machines appropriées et interpréter les résultats selon le réseau.

### 20.4 Le basculement ne se produit pas lorsque Nginx s'arrête

Vérifie :

- Que le script existe.
- Qu'il est exécutable.
- Qu'il renvoie un code d'échec lorsque Nginx est arrêté.
- Que le nom du script est correct dans la configuration.
- Que `track_script` référence le bon contrôle.
- Que la priorité après échec devient inférieure à celle du secours.
- Que Keepalived a rechargé la configuration.
- Que la communication VRRP fonctionne.

Lance directement le script :

```bash
sudo /usr/local/sbin/check_nginx.sh
echo $?
```

Il doit renvoyer un code non nul si Nginx ne répond pas selon le contrôle défini.

### 20.5 Le basculement fonctionne, mais revient trop souvent

Un basculement répétitif peut être provoqué par un contrôle instable ou des problèmes réseau intermittents.

Examine :

- La stabilité de Nginx.
- Les résultats successifs du script.
- Les délais de vérification.
- Les pertes de paquets.
- Les messages du journal.
- La différence de priorité.
- Les événements de redémarrage.

Une vérification trop sensible peut provoquer des changements de détenteur répétés. Le contrôle doit refléter la santé réelle du service.

## 21. Diagnostic Pacemaker et Corosync

### 21.1 Consulter l'état du cluster

```bash
sudo pcs status
```

Utilise aussi, selon la version :

```bash
sudo pcs status --full
```

La sortie aide à déterminer si :

- Les nœuds sont présents.
- Le cluster a un quorum.
- Les ressources sont actives.
- Des ressources sont en échec.
- Des opérations sont en attente.

### 21.2 Examiner les journaux

Pour examiner les événements des composants :

```bash
sudo journalctl -u pacemaker --no-pager -n 100
sudo journalctl -u corosync --no-pager -n 100
sudo journalctl -u pcsd --no-pager -n 100
```

Les unités et la disponibilité des journaux dépendent de la distribution et de la version installées.

Il faut corréler les messages avec l'heure de l'incident et les opérations effectuées.

### 21.3 Vérifier le quorum

Dans un environnement Corosync où la commande est disponible :

```bash
sudo corosync-quorumtool -s
```

Cette commande fournit des informations sur le quorum et les votes selon la configuration.

Si le cluster n'a plus le quorum, ne tente pas de forcer le démarrage des ressources sans comprendre la cause.

Il faut examiner l'état des nœuds, les communications, le vote et le fencing.

### 21.4 Comprendre une ressource en échec

Une ressource peut échouer à démarrer ou à répondre au contrôle.

Les causes possibles incluent :

- Un paquet manquant.
- Un mauvais nom de service.
- Une configuration incorrecte.
- Des permissions insuffisantes.
- Une adresse IP déjà utilisée.
- Un stockage indisponible.
- Une dépendance non satisfaite.
- Un agent de ressource absent.
- Une erreur du fencing.

Commence par examiner la sortie de `pcs status`, la configuration de la ressource et les journaux.

Ne supprime pas une ressource simplement pour faire disparaître son état d'échec.

### 21.5 Une ressource ne doit pas être corrigée par un lancement manuel permanent

Si Pacemaker doit gérer Nginx, ne transforme pas les interventions manuelles sur Nginx en méthode habituelle d'exploitation.

Une intervention manuelle peut être nécessaire pour diagnostiquer le service dans une procédure contrôlée, mais le fonctionnement normal doit rester cohérent avec la gestion du cluster.

La configuration doit garantir qu'un seul mécanisme possède la responsabilité des opérations de démarrage, d'arrêt et de basculement.

## 22. Travaux pratiques

Les travaux pratiques sont destinés à un environnement de laboratoire. Avant de les exécuter, vérifie les adresses IP, les interfaces et les permissions.

### TP 1 — Installer Keepalived

**Objectif :** installer le service sur deux machines.

Étapes :

1. Préparer les serveurs ha1 et ha2.
2. Configurer les adresses IP.
3. Vérifier le nom des interfaces.
4. Installer Keepalived et Nginx.
5. Vérifier que Nginx répond localement.
6. Lire le fichier de configuration Keepalived.
7. Sauvegarder les configurations avant modification.

Commandes de vérification :

```bash
hostname
ip -br address
sudo systemctl status nginx
sudo systemctl status keepalived
```

Résultat attendu : les deux serveurs sont joignables et les services sont installés.

### TP 2 — Configurer une VIP avec VRRP

**Objectif :** mettre en place un serveur principal et un serveur de secours.

Étapes :

1. Configurer ha1 avec la priorité 110.
2. Configurer ha2 avec la priorité 100.
3. Utiliser un identifiant VRRP identique sur les deux nœuds.
4. Vérifier les adresses des pairs unicast.
5. Vérifier que la VIP est libre.
6. Démarrer Keepalived.
7. Identifier le détenteur de la VIP.
8. Tester une requête HTTP via la VIP.

Résultat attendu : la VIP est portée par un seul des deux serveurs et le service Web est joignable.

### TP 3 — Surveiller Nginx

**Objectif :** détecter une panne applicative.

Étapes :

1. Créer le script de contrôle.
2. Définir ses permissions.
3. Tester son résultat lorsque Nginx est actif.
4. Arrêter Nginx sur le détenteur de la VIP.
5. Examiner les journaux Keepalived.
6. Observer le changement de priorité.
7. Vérifier si la VIP bascule vers le secours.
8. Redémarrer le service.
9. Vérifier le retour au fonctionnement normal.

Résultat attendu : la configuration de suivi est comprise et son comportement a été observé.

### TP 4 — Observer les journaux

**Objectif :** apprendre à diagnostiquer un basculement.

Étapes :

1. Suivre le journal Keepalived.
2. Déclencher un basculement dans le laboratoire.
3. Relever les messages de transition.
4. Vérifier les adresses IP.
5. Enregistrer l'heure de l'incident.
6. Mesurer le délai observé.
7. Écrire une synthèse des événements.

Commandes :

```bash
sudo journalctl -u keepalived -f
```

Puis :

```bash
ip -br address
```

Résultat attendu : un compte rendu montrant la cause du basculement, son déroulement et le résultat.

### TP 5 — Découvrir Pacemaker

**Objectif :** comprendre la structure d'un cluster Pacemaker.

Étapes :

1. Préparer deux serveurs de laboratoire.
2. Installer les paquets Pacemaker, Corosync et `pcs`.
3. Vérifier que les nœuds se résolvent correctement.
4. Consulter l'aide de `pcs`.
5. Étudier les exigences du quorum.
6. Identifier un mécanisme de fencing adapté au matériel ou à l'environnement virtuel.
7. Consulter les commandes d'état du cluster.
8. Documenter les différences entre une ressource et un service système.

Ne déploie pas de ressources de production tant que le fencing n'a pas été correctement configuré et testé.

### TP 6 — Concevoir un service Web géré par Pacemaker

**Objectif :** comprendre le modèle de ressources.

Prépare un schéma décrivant :

- L'adresse virtuelle.
- Le service Web.
- Le groupe de ressources.
- Les contrôles de santé.
- Le quorum.
- Le fencing.
- Les fichiers Web disponibles sur les deux nœuds.

Écris ensuite la séquence de démarrage et d'arrêt attendue.

Résultat attendu : un schéma cohérent montrant les dépendances et la responsabilité de chaque composant.

### TP 7 — Tester la reprise en environnement contrôlé

**Objectif :** comparer le comportement attendu et celui qui est réellement observé.

Prépare un test contrôlé comprenant :

1. Un état initial fonctionnel.
2. Une panne simulée appropriée au laboratoire.
3. Une collecte des journaux.
4. Une mesure du temps de détection.
5. Une mesure du temps de reprise.
6. Une vérification fonctionnelle du service.
7. Une vérification des ressources.
8. Un compte rendu des résultats.

Le test ne doit pas être exécuté sur un système de production sans procédure de changement, contrôle des risques et possibilité de retour arrière.

## 23. Exercices avec corrigés

### Exercice 1 — Comprendre la VIP

Deux serveurs possèdent respectivement les adresses `192.168.50.11` et `192.168.50.12`. L'adresse de service est `192.168.50.100`.

**Question :** pourquoi les clients utilisent-ils l'adresse virtuelle plutôt que l'adresse du serveur principal ?

**Corrigé :** l'adresse virtuelle constitue un point d'accès stable. Si le service passe sur le serveur de secours, les clients peuvent conserver la même adresse de destination, sous réserve du temps de convergence et du bon fonctionnement de l'application.

### Exercice 2 — Deux serveurs possèdent la VIP

Les administrateurs constatent que la VIP est présente sur ha1 et ha2 en même temps.

**Question :** est-ce le comportement attendu ?

**Corrigé :** non, pas dans le scénario étudié où une seule instance doit être active. Il faut vérifier la communication VRRP, les identifiants, les adresses des pairs, les priorités et les journaux. La présence de la VIP sur deux nœuds peut indiquer une configuration incohérente ou une séparation réseau.

### Exercice 3 — Nginx est arrêté, mais la VIP ne bouge pas

**Question :** quelles sont les principales vérifications ?

**Corrigé :** il faut vérifier le script, ses permissions, son code de sortie, la directive `track_script`, les paramètres `fall`, `rise` et `weight`, ainsi que la priorité effective par rapport au serveur de secours.

### Exercice 4 — La VIP fonctionne, mais les données sont différentes

ha1 contient une version récente du site. ha2 contient une version ancienne.

**Question :** pourquoi le basculement n'est-il pas suffisant ?

**Corrigé :** le déplacement de l'adresse ne synchronise pas les fichiers. Il faut déployer un contenu cohérent sur les deux serveurs ou utiliser une solution de gestion ou de partage des données adaptée.

### Exercice 5 — Pacemaker et la VIP

Un administrateur décide de faire gérer la même VIP par Keepalived et par Pacemaker.

**Question :** pourquoi est-ce une mauvaise idée ?

**Corrigé :** les deux logiciels peuvent essayer de contrôler indépendamment la même adresse, provoquer des conflits et rendre le comportement difficile à prévoir. Un mécanisme doit être responsable de la ressource concernée.

### Exercice 6 — Quorum et panne réseau

Deux nœuds Pacemaker ne peuvent plus communiquer, mais ils sont tous les deux encore allumés.

**Question :** pourquoi faut-il vérifier le quorum et le fencing ?

**Corrigé :** une partition réseau peut empêcher le cluster de savoir si l'autre nœud fonctionne encore. Le quorum participe à la décision de continuer à gérer les ressources, tandis que le fencing sert à isoler de manière fiable un nœud qui pourrait encore utiliser les ressources.

### Exercice 7 — Haute disponibilité et sauvegarde

Un site Web est hébergé derrière une VIP. L'administrateur affirme qu'aucune sauvegarde n'est nécessaire.

**Question :** pourquoi est-ce incorrect ?

**Corrigé :** la VIP améliore la disponibilité du point d'accès. Elle ne garantit pas la récupération des fichiers supprimés, des données corrompues ou des systèmes détruits. Une stratégie de sauvegarde distincte reste nécessaire.

### Exercice 8 — Choix du mécanisme

Une application nécessite une VIP, un montage de stockage, une base de données et un service Web qui doivent suivre des règles d'ordre.

**Question :** quel outil peut être plus approprié pour coordonner ces ressources ?

**Corrigé :** Pacemaker peut être adapté parce qu'il sait gérer des ressources, des dépendances et des contraintes de placement. Il faut néanmoins vérifier la compatibilité de l'application, de ses données et des agents disponibles.

## 24. Projet pratique de synthèse

### 24.1 Contexte

Une petite entreprise héberge un site Web interne qui doit rester accessible malgré certaines pannes.

Elle dispose de deux serveurs Ubuntu :

- `ha1` : `192.168.50.11`
- `ha2` : `192.168.50.12`

Le service doit être accessible via la VIP `192.168.50.100`.

Les objectifs sont :

- Éviter qu'une panne de l'hôte principal entraîne une longue interruption.
- Détecter une panne du service Web.
- Bascule automatiquement l'adresse virtuelle dans les conditions prévues.
- Conserver une version cohérente du contenu sur les deux serveurs.
- Documenter et mesurer le comportement lors d'un incident.
- Préparer une stratégie de sauvegarde.

### 24.2 Schéma cible

```text
                       UTILISATEURS
                            |
                            v
                    VIP 192.168.50.100
                            |
                 +----------+----------+
                 |                     |
                 v                     v
            +---------+           +---------+
            |   ha1   |           |   ha2   |
            | Nginx   |           | Nginx   |
            | Keepalived           | Keepalived
            | Priorité 110         | Priorité 100
            +---------+           +---------+
                 |                     |
                 +----------+----------+
                            |
                       Réseau commun
                            |
                            v
                 Contenu Web cohérent
                 et sauvegarde séparée
```

### 24.3 Travail à réaliser

Tu dois remettre :

1. Une documentation des adresses IP et des interfaces.
2. Les fichiers Keepalived des deux serveurs.
3. Le script de surveillance.
4. Une vérification de l'état des deux Nginx.
5. Les commandes de contrôle.
6. Un rapport du test de basculement.
7. Une mesure du temps de reprise.
8. Un plan de mise à jour du contenu Web.
9. Une stratégie de sauvegarde.
10. Une procédure de diagnostic.
11. Une procédure de retour à l'état nominal.

### 24.4 Critères de réussite

Le projet est réussi si :

- La VIP est libre avant le déploiement.
- Une seule instance porte l'adresse virtuelle à l'état nominal.
- La VIP est accessible depuis un client autorisé.
- Le contrôle de santé produit le bon code de sortie.
- Le basculement est observé lors d'un test planifié.
- Le contenu affiché est cohérent sur les deux serveurs.
- Les journaux permettent d'expliquer le basculement.
- Les commandes de vérification sont documentées.
- La stratégie de sauvegarde est indépendante du mécanisme de VIP.
- Le résultat est reproductible.

## 25. Défi final — Concevoir une architecture de haute disponibilité

Une entreprise héberge une application utilisée par plusieurs dizaines de personnes.

Elle souhaite améliorer la disponibilité d'un serveur Web. Elle envisage également de protéger une application plus complexe qui utilise un système de fichiers et une base de données.

Tu dois proposer une architecture tenant compte de ces deux besoins.

### Partie A — Pour le service Web

Définis :

- Le nombre de serveurs.
- Les adresses physiques.
- L'adresse virtuelle.
- Les priorités.
- Le mécanisme de communication VRRP.
- Le contrôle de santé.
- Les règles du pare-feu.
- La méthode de distribution des fichiers.

### Partie B — Pour l'application complexe

Définis :

- Les ressources à gérer.
- Les dépendances.
- Les exigences de stockage.
- Les règles de démarrage.
- Le quorum.
- Le fencing.
- Les contrôles de santé.
- Le plan de maintenance.

### Partie C — Sécurité et exploitation

Documente :

- Les comptes autorisés.
- Les permissions.
- Les secrets.
- Les règles réseau.
- Les journaux.
- Les alertes.
- La sauvegarde.
- Les tests de reprise.
- Les procédures d'escalade.

### Partie D — Validation

Prépare un plan de test pour :

- L'arrêt du service.
- La perte d'un nœud.
- La perte d'une communication réseau.
- Le transfert de l'adresse virtuelle.
- Le démarrage sur le serveur de secours.
- La restauration des données.
- La vérification fonctionnelle de l'application.

Le but n'est pas de choisir Keepalived ou Pacemaker par habitude, mais de justifier la technologie qui correspond réellement au comportement attendu.

## 26. Fiche de révision rapide

| Besoin | Technologie ou commande |
|---|---|
| Afficher les interfaces réseau | `ip -br address` |
| Vérifier le routage | `ip route` |
| Tester une requête HTTP | `curl http://127.0.0.1/` |
| Vérifier Nginx | `systemctl status nginx` |
| Installer Keepalived sur Ubuntu | `sudo apt install keepalived` |
| Démarrer Keepalived | `sudo systemctl enable --now keepalived` |
| Examiner le journal Keepalived | `sudo journalctl -u keepalived` |
| Examiner l'adresse virtuelle | `ip address show ens18` |
| Administrer Pacemaker | `pcs` |
| Consulter l'état du cluster | `sudo pcs status` |
| Examiner les ressources | `sudo pcs resource status` |
| Examiner la configuration des ressources | `sudo pcs resource config` |
| Examiner le quorum Corosync | `sudo corosync-quorumtool -s` |
| Examiner les journaux Pacemaker | `sudo journalctl -u pacemaker` |
| Examiner les journaux Corosync | `sudo journalctl -u corosync` |

Ces commandes constituent un point de départ. Elles ne remplacent pas la documentation adaptée à la version de Linux et aux composants installés.

## 27. Glossaire

**Haute disponibilité (HA) :** approche visant à réduire l'indisponibilité d'un service après certains incidents.

**VIP (Virtual IP Address) :** adresse IP virtuelle utilisée comme point d'accès à un service.

**VRRP :** protocole permettant à plusieurs participants de gérer une adresse virtuelle selon une élection et des annonces.

**Keepalived :** logiciel Linux capable de gérer des instances VRRP, des contrôles de santé et des fonctions d'équilibrage de charge.

**MASTER :** état initial privilégié d'une instance VRRP dans certains scénarios.

**BACKUP :** état d'une instance qui peut prendre le rôle actif lorsque les conditions sont réunies.

**Priorité :** valeur utilisée par VRRP pour déterminer l'instance privilégiée, selon la configuration.

**Basculement (failover) :** transfert d'une responsabilité ou d'un service après une panne ou un changement d'état.

**Pacemaker :** gestionnaire de ressources de cluster.

**Corosync :** composant fournissant des mécanismes de communication et de gestion de l'appartenance du cluster.

**pcs :** outil d'administration de clusters Pacemaker/Corosync.

**Ressource :** service ou composant que Pacemaker sait gérer via un agent adapté.

**Agent de ressource :** programme qui définit les opérations de démarrage, d'arrêt et de surveillance d'une ressource.

**Quorum :** mécanisme de décision déterminant si le cluster possède les votes requis pour continuer à fonctionner.

**Fencing :** mécanisme permettant d'isoler de manière fiable un nœud qui ne doit plus accéder aux ressources gérées.

**Split-brain :** situation dans laquelle plusieurs parties d'un cluster peuvent penser qu'elles sont autorisées à gérer les mêmes ressources.

**RTO :** délai maximal ciblé pour rétablir un service après un incident.

**RPO :** quantité de données qu'une organisation accepte de perdre, exprimée en durée.

**Réplication :** mécanisme de maintien d'une copie de données ou d'état sur un autre système.

**Sauvegarde :** copie conservée pour permettre une restauration après perte ou corruption.

**Équilibrage de charge :** répartition du trafic entre plusieurs serveurs ou instances.

## 28. Documentation officielle

Pour approfondir le contenu, privilégie les documentations officielles des projets et de la distribution.

### Keepalived

- [Guide utilisateur Keepalived](https://keepalived.org/documentation/user-guide/)
- [Démarrage rapide : VIP et VRRP](https://keepalived.org/documentation/user-guide/quick-start/)
- [Syntaxe et configuration Keepalived](https://keepalived.org/documentation/keepalived.conf/)
- [Installer Keepalived](https://keepalived.org/documentation/user-guide/installing/)
- [Configuration des instances VRRP](https://keepalived.org/documentation/user-guide/configuration-synopsis/)

### Pacemaker et Corosync

- [Documentation haute disponibilité Ubuntu Server](https://ubuntu.com/server/docs/reference/high-availability/)
- [Présentation de la haute disponibilité Ubuntu Server](https://ubuntu.com/server/docs/explanation/high-availability/)
- [Documentation Pacemaker et clusters haute disponibilité — Red Hat](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/)
- [Création de ressources Pacemaker](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/assembly_configuring-cluster-resources-configuring-and-managing-high-availability-clusters)
- [Administration de ressources Pacemaker](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_high_availability_clusters/assembly_managing-cluster-resources-configuring-and-managing-high-availability-clusters)

Les commandes exactes doivent être vérifiées pour la version de la distribution, de Pacemaker, de Corosync et de Keepalived réellement utilisée.

## Conclusion

La haute disponibilité est une démarche d'architecture. Elle ne consiste pas simplement à installer deux serveurs et à démarrer un service identique sur chacun.

Keepalived est adapté à de nombreux scénarios de gestion d'une adresse virtuelle et de surveillance simple d'un service réseau. Pacemaker permet de gérer un ensemble de ressources et leurs dépendances dans une architecture de cluster plus complète.

Pour obtenir un fonctionnement réellement fiable, il faut aussi traiter la cohérence des données, le réseau, le contrôle de santé, le quorum, le fencing, la sécurité, les sauvegardes et les procédures d'exploitation.

La règle essentielle à retenir est la suivante : **un basculement doit être testé, mesuré et documenté. La présence de deux serveurs ne suffit pas à démontrer la haute disponibilité.**