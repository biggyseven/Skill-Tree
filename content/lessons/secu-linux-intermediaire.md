# Sécurité des systèmes Linux

> **Mise en contexte**
>
> Un serveur Linux peut héberger une API, une base de données, un dépôt de code, un service DNS, une passerelle ou un outil de supervision. Sa sécurité ne repose pas uniquement sur un mot de passe fort ou un pare-feu : elle dépend aussi des permissions, des privilèges des processus, des paquets installés, des services actifs, des mises à jour, de SSH, de la journalisation, des sauvegardes et des changements d'exploitation.
>
> Ce cours présente une méthode défensive pour inventorier un serveur, réduire sa surface d'attaque, gérer les comptes et sudo, protéger SSH, contrôler les ports, corriger les logiciels, auditer les fichiers et permissions, comprendre AppArmor ou SELinux, renforcer les services systemd, centraliser les journaux et préparer une réponse à incident. Les commandes varient selon la distribution ; toute modification distante doit rester testée, tracée et réversible.

## 1. Objectifs et méthode de travail

À la fin du cours, tu dois pouvoir produire un inventaire de sécurité, expliquer les permissions Unix et les ACL, examiner les comptes et les privilèges, sécuriser un accès SSH sans te verrouiller à distance, identifier les ports en écoute, réduire les services inutiles, traiter les mises à jour, lire les journaux, contrôler le confinement des applications, protéger les sauvegardes et recueillir des preuves utiles à une investigation.

Le durcissement est une démarche par risque, pas une liste de commandes universelles. Un serveur Web exposé, un bastion, un serveur de sauvegarde et une machine de développement n'ont pas les mêmes besoins. Une règle correcte pour un rôle peut rendre un autre rôle indisponible. Avant de changer une configuration, il faut documenter le besoin, la valeur initiale, le résultat attendu, les effets secondaires possibles, la validation et le retour arrière.

~~~text
                 DEFENSE EN PROFONDEUR LINUX
+---------------------------------------------------------+
| Inventaire, proprietaire, criticite et baseline         |
+---------------------------------------------------------+
| Identite : comptes nominatifs, MFA, sudo, cle SSH       |
+---------------------------------------------------------+
| Systeme : mises a jour, services et noyau               |
+---------------------------------------------------------+
| Acces : permissions, ACL, capabilities, MAC             |
+---------------------------------------------------------+
| Reseau : ecoute, pare-feu, segmentation, administration  |
+---------------------------------------------------------+
| Donnees : secrets, chiffrement, sauvegardes              |
+---------------------------------------------------------+
| Detection : journaux, audit, alertes et reponse           |
+---------------------------------------------------------+
~~~

## 2. Identifier le serveur avant de le modifier

Commence par déterminer la distribution, sa version, le noyau, l'architecture, le rôle de la machine, son exposition et sa méthode de gestion. Les outils et fichiers de configuration diffèrent entre Debian/Ubuntu, RHEL, Rocky Linux, AlmaLinux, SUSE et les images minimales. Les hôtes conteneurisés ou immuables ont également des contraintes particulières.

~~~bash
cat /etc/os-release
uname -a
hostnamectl
id
uptime
findmnt
lsblk -f
~~~

Ces commandes renseignent sur le système, le noyau, l'identité, les groupes, l'état général, les montages et les périphériques de stockage. Vérifie ensuite les systèmes d'identité, les dépôts logiciels, les services activés et les canaux d'administration. Les comptes peuvent provenir d'un annuaire via NSS/SSSD et ne pas apparaître comme des comptes locaux ordinaires dans /etc/passwd.

Une baseline est un état de référence approuvé : comptes et groupes privilégiés, paquets, services et sockets, règles de pare-feu, tâches planifiées, clés SSH autorisées, configurations critiques et versions. Une comparaison régulière aide à repérer une dérive, mais toute différence n'est pas automatiquement une attaque : les mises à jour ou déploiements légitimes doivent également laisser des traces.

~~~text
[Identification du serveur]
          |
          v
[Distribution + version + role + criticite]
          |
          v
[Inventaire comptes / paquets / services / ports]
          |
          v
[Comparaison a la baseline approuvee]
          |
          v
[Changement teste + preuve + rollback]
~~~

## 3. Modèle de menace et surface d'attaque

La surface d'attaque regroupe les services réseau, interfaces d'administration, applications, paquets, comptes, tâches planifiées, fichiers exécutables privilégiés et chemins de déploiement. Même un service non exposé à Internet peut être atteint depuis un réseau interne compromis, un compte de service, un pipeline CI/CD ou une autre machine.

Le modèle de menace identifie les actifs, les attaquants possibles, les chemins d'accès, les conséquences et les contrôles. Une vulnérabilité Web peut permettre l'exécution de code sous l'identité de l'application ; si ce compte peut lire les secrets ou écrire dans les tâches root, l'impact peut devenir bien plus large. Le contrôle adapté dépend de cette chaîne.

~~~text
[Source non fiable]
       |
       v
[Service expose ou application vulnerable]
       |
       v
[Compte applicatif trop privilegie]
       |
       v
[Secrets / fichiers / socket accessibles]
       |
       v
[Persistance ou mouvement lateral]

Controles : surface minimale, moindre privilege, confinement et logs.
~~~

Désactiver un service inutile réduit la surface d'attaque, mais identifier correctement un service est indispensable avant de le couper. Un composant qui semble secondaire peut assurer l'identité, le stockage, la supervision ou la haute disponibilité. La réduction de surface doit être fondée sur l'inventaire et la validation des dépendances.

## 4. Comptes, groupes et identité

Les comptes nominatifs facilitent l'attribution des actions. Les comptes partagés rendent difficile l'identification de l'auteur d'une commande, compliquent la révocation des accès et encouragent le partage de clés ou de mots de passe. Privilégie un compte personnel par administrateur, des groupes dont la fonction est claire et des autorisations limitées.

~~~bash
getent passwd
getent group
id utilisateur
last
lastlog
sudo -l
~~~

Les commandes affichent les comptes résolus, groupes, connexions et droits sudo, selon les outils et la politique de la machine. Vérifie les comptes issus d'un annuaire central et les comptes techniques. Ne te contente pas de chercher les UID locaux : un compte distant peut avoir des droits importants sans ligne locale.

Le compte root dispose de privilèges très étendus. Il ne devrait pas servir aux tâches quotidiennes. sudo permet d'autoriser certaines opérations et d'en enregistrer l'usage, si la politique et les journaux sont convenablement configurés. Un compte de service devrait être non interactif lorsqu'il n'a pas besoin de session, éviter les groupes privilégiés et posséder seulement les droits sur ses données, sockets et fichiers.

~~~text
Compte nominatif
     |
     +--> authentification individuelle
     |
     +--> droits normaux minimaux
     |
     +--> action admin via sudo selon une politique
     |
     +--> journalisation / attribution
     |
     +--> retrait de l'acces lors du depart

Compte service --> acces machine precis, aucune session interactive inutile
~~~

Lorsqu'un collaborateur quitte l'équipe, retire ses accès locaux et centraux, révoque les clés, jetons et sessions, et examine les secrets partagés dont il disposait. Supprimer un compte local ne révoque pas les clés copiées ailleurs ni les jetons API. Associe chaque compte technique à un propriétaire, une application et une procédure de rotation.

## 5. Authentification, PAM, MFA et récupération

La politique d'authentification doit prendre en compte les comptes locaux, l'annuaire, les clés SSH, la MFA, les comptes de secours et les identités de service. Les mots de passe doivent être traités par les mécanismes de la distribution ; leurs empreintes ne doivent pas être copiées dans des journaux ou tickets. Favorise des secrets longs et uniques, et évite leur réutilisation.

PAM permet de composer des contrôles d'authentification et de compte, mais une erreur de configuration peut empêcher les connexions. Avant de modifier PAM, la configuration de l'annuaire ou la politique de mots de passe, garde une session administrative ouverte, prévois une console de récupération et teste avec un compte de validation.

~~~text
[Utilisateur]
     |
     v
[Authentification : cle / mot de passe / MFA / annuaire]
     |
     v
[Controle du compte et de la politique]
     |
     v
[Autorisation : shell, groupes, sudo, ressources]
     |
     v
[Logs + revue des acces]
~~~

Les administrateurs devraient utiliser une authentification renforcée adaptée au contexte. Pour SSH, une clé privée protégée par une phrase secrète est préférable à une clé non protégée ; une MFA peut ajouter un facteur de possession ou un autre facteur selon la plateforme. Toutefois, une politique forte doit prévoir récupération et révocation des facteurs perdus.

Évite les scripts maison de gestion de secrets et les politiques de verrouillage irréfléchies. Un seuil trop strict peut permettre à un attaquant de bloquer le compte d'un administrateur par une rafale d'échecs. Le contrôle de débit, la surveillance et les mécanismes de récupération doivent être conçus ensemble. Pour les comptes centralisés, applique la politique au point réellement autoritaire.

## 6. Permissions Unix et umask

Le modèle classique distingue propriétaire, groupe et autres, avec les droits de lecture, d'écriture et d'exécution. Sur un fichier, l'exécution permet de lancer le programme ; sur un répertoire, le droit x autorise sa traversée. Lire un répertoire permet d'en lister les entrées, tandis que le droit d'écriture peut permettre de créer ou renommer des entrées selon les autres permissions.

~~~bash
ls -l /etc/ssh/sshd_config
stat /etc/ssh/sshd_config
namei -l /var/www/site/index.html
umask
getfacl /srv/application
~~~

Le mode octal 640 signifie que le propriétaire peut lire et écrire, que le groupe peut lire et que les autres n'ont aucun droit. Cela peut être adapté à certains fichiers de configuration, mais pas à tous les exécutables et répertoires. Les fichiers d'un service doivent appartenir au compte prévu et être lisibles par les processus autorisés, pas par tous les utilisateurs.

~~~text
Fichier mode 640
+-- proprietaire : rw-  lecture / ecriture
+-- groupe       : r--  lecture
+-- autres       : ---  aucun droit

Repertoire mode 750
+-- proprietaire : rwx
+-- groupe       : r-x
+-- autres       : ---
~~~

chmod modifie les permissions, chown le propriétaire et le groupe, chgrp le groupe. Une opération récursive sur une arborescence peut casser les droits d'un serveur entier. Évite le réflexe de chmod 777 : il élargit les possibilités de modification et masque souvent le problème original. Utilise namei pour inspecter chaque composant du chemin et stat pour vérifier le propriétaire réel.

umask retire des permissions par défaut lors de la création d'éléments. Elle ne remplace ni les permissions explicites, ni les ACL, ni les politiques d'une application. Vérifie l'identité et l'environnement effectif du processus : shell interactif, unité systemd, tâche cron, conteneur ou pipeline de déploiement.

## 7. ACL et fichiers privilégiés

Les ACL offrent des autorisations plus précises que le trio propriétaire/groupe/autres. Elles sont utiles lorsque plusieurs équipes doivent accéder à un dossier partagé. Elles peuvent cependant surprendre par leur masque et leur héritage ; la sortie de getfacl doit être comprise et les droits effectifs testés sous l'identité concernée.

~~~bash
getfacl /srv/application
setfacl -m u:lecteur:r-- /srv/application/rapport.txt
setfacl -m d:g:auditeurs:rx /srv/application/rapports
getfacl /srv/application/rapport.txt
~~~

Teste les exemples dans un répertoire de laboratoire, jamais sur des données de production sans validation. Le premier exemple ajoute un accès utilisateur à un fichier ; le second définit une ACL par défaut pour les nouveaux éléments d'un répertoire. Le système de fichiers et ses options doivent prendre en charge ces mécanismes.

Les bits setuid et setgid changent le contexte de privilèges ou de groupe de certains exécutables ; le sticky bit a un rôle particulier sur des répertoires partagés. Certains binaires privilégiés sont légitimes. Un fichier privilégié inconnu ou nouvellement apparu demande une investigation, mais pas nécessairement une suppression immédiate.

~~~bash
find / -xdev -type f -perm -4000 -print 2>/dev/null
find / -xdev -type f -perm -2000 -print 2>/dev/null
find / -xdev -type f -perm -0002 -print 2>/dev/null
~~~

Ces recherches peuvent être coûteuses et ne couvrent que les systèmes de fichiers inclus. Compare les résultats à une référence de la distribution, aux paquets installés et à l'historique des changements. Un fichier inscriptible par tous mérite une revue du propriétaire, du rôle et du chemin parent.

## 8. sudo et moindre privilège

Les règles sudo doivent être gérées via visudo ou un outil de configuration qui valide leur syntaxe. Une règle qui semble autoriser une seule commande peut donner de facto un accès root si cette commande permet d'invoquer un interpréteur, d'exécuter du code arbitraire ou d'écrire un fichier privilégié.

~~~bash
sudo -l
sudo visudo
sudo visudo -f /etc/sudoers.d/equipe-operations
~~~

Avant d'écrire une règle, formule le besoin : commande, arguments, ressources, identité et durée. L'autorisation d'un éditeur, d'un interpréteur ou d'un utilitaire capable de lancer des programmes peut contourner l'intention initiale. Préfère des interfaces administratives étroites, des scripts appartenant à root et non modifiables par les utilisateurs, ou un outil de gestion des changements.

~~~text
[Compte]
   |
   v
[Politique sudo]
   |
   +--> commande et arguments autorises
   |
   +--> autres commandes refusees
   |
   v
[Action privilegiee + trace d'audit]

Attention : une commande autorisee peut offrir un shell root indirect.
~~~

Les règles doivent être revues à chaque changement de rôle et lors du départ d'un administrateur. Contrôle les groupes utilisés dans sudoers, les fichiers inclus et leurs permissions. Évite les règles générales qui accordent sudo sans mot de passe ou tous les droits sans besoin démontré.

## 9. OpenSSH : accès distant sécurisé

SSH fournit un canal chiffré pour l'administration et les transferts. Sa sécurité dépend de la version du serveur, des méthodes d'authentification, des clés, des autorisations, des contrôles réseau et de la surveillance. Les services historiques comme Telnet ne doivent pas servir à l'administration lorsque des alternatives chiffrées sont disponibles.

~~~bash
ssh-keygen -t ed25519
ssh-copy-id utilisateur@serveur-exemple
ssh -v utilisateur@serveur-exemple
~~~

La clé privée demeure sur le poste client et ne doit jamais être copiée dans authorized_keys. Seule la clé publique est distribuée. Protège le fichier privé et le compte client ; ajoute une phrase secrète lorsque c'est possible et gère le retrait des clés lors du départ d'une personne.

Avant de modifier SSH, confirme un accès console ou de récupération et conserve la session actuelle ouverte. Sauvegarde la configuration, examine les fragments inclus et vérifie les valeurs effectives. Certaines distributions gèrent des snippets dans sshd_config.d, et les options Match peuvent rendre la politique différente d'un compte à l'autre.

~~~text
Session existante (ne pas fermer)
           |
           v
Sauvegarde de la configuration
           |
           v
Modification limitée
           |
           v
sshd -t : syntaxe valide ?
    | oui           | non
    v                v
Reload prudent    Corriger / restaurer
    |
    v
Tester une 2e session
    |
    v
Fermer l'ancienne session seulement apres validation
~~~

~~~bash
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.backup-avant-durcissement
sudo sshd -t
sudo sshd -T | grep -E 'permitrootlogin|passwordauthentication|pubkeyauthentication'
sudo systemctl reload ssh
~~~

Le nom d'unité est souvent ssh sur Debian/Ubuntu et sshd sur certaines autres distributions. Vérifie son état avant l'opération. Ne recharge pas le service si sshd -t échoue. Les options PermitRootLogin, PasswordAuthentication, PubkeyAuthentication, AllowUsers et AllowGroups doivent être adaptées au besoin. N'interdis pas les mots de passe avant d'avoir confirmé que toutes les identités nécessaires disposent d'un autre accès opérationnel.

Restreindre SSH au réseau d'administration réduit l'exposition mais ne remplace pas l'authentification. Surveille les échecs répétés, les connexions réussies inhabituelles, les nouvelles clés et les changements de configuration. Les journaux doivent contenir assez de contexte pour une investigation sans révéler des secrets.

## 10. Services actifs et ports

Un service installé n'est pas forcément actif ; un service actif n'écoute pas forcément sur le réseau. Un programme peut aussi ouvrir un socket indépendamment d'une unité évidente, ou être publié via un conteneur. Il faut rapprocher les services, processus, sockets et usages métier.

~~~bash
systemctl --type=service --state=running
systemctl --type=socket --state=running
ss -lntup
ps -eo user,pid,ppid,comm,args --sort=user
~~~

ss affiche les sockets et, avec les privilèges nécessaires, les processus. Un service attaché à 127.0.0.1 n'a pas la même exposition qu'un service lié à toutes les interfaces, mais tunnels et proxys peuvent fournir un accès indirect. Examine les interfaces, routes, NAT, conteneurs et règles de filtrage pour connaître le chemin réel.

~~~text
Processus
  +--> service sans socket reseau
  +--> ecoute localhost
  +--> ecoute sur interface privee
  +--> ecoute sur toutes les interfaces
                       |
                       v
      Bind + pare-feu + routage + besoin metier
~~~

Désactive un service seulement après avoir identifié ses dépendances et prévu un retour arrière. Pour chaque port, documente le processus, le propriétaire, l'interface, les clients autorisés, le besoin, la mise à jour et les journaux. Un service inconnu doit être attribué à un propriétaire avant une décision, et non simplement tué par PID.

## 11. Pare-feu hôte et trafic réseau

Le pare-feu hôte complète la segmentation réseau en limitant les connexions reçues et, selon la politique, les connexions sortantes. Un serveur Web peut nécessiter HTTPS ; une base de données doit généralement recevoir uniquement les flux attendus depuis les serveurs applicatifs ; un bastion doit être atteignable depuis les sources d'administration approuvées.

Sur Ubuntu, UFW est une interface de gestion courante. Selon la distribution, firewalld ou nftables peuvent être les outils privilégiés. N'alterne pas plusieurs gestionnaires qui risquent de modifier ou de contredire les règles les uns des autres.

~~~bash
sudo ufw status verbose
sudo ufw allow from 192.0.2.10 to any port 22 proto tcp
sudo ufw allow 443/tcp
sudo ufw status numbered
~~~

Les adresses en exemple sont réservées à la documentation ; remplace-les par celles de ton environnement de laboratoire. Avant d'activer un pare-feu restrictif à distance, assure-toi que la source d'administration est la bonne et qu'un accès de secours existe. Une politique mal préparée peut couper toutes les sessions.

~~~text
Source admin approuvee ---> SSH autorise
Clients Web -------------> HTTPS autorise
Autres sources ----------> SSH refuse
Internet ----------------> Base de donnees refusee
Sorties serveur ----------> destination necessaire si politique definie
~~~

Teste depuis une source autorisée et une source qui doit être bloquée. Vérifie les règles actives et les journaux. Le pare-feu ne corrige pas une application vulnérable ni un compte trop privilégié ; il doit être combiné avec les mises à jour, l'identité et le confinement du processus.

## 12. Mises à jour et chaîne logicielle

Les mises à jour corrigent vulnérabilités et défauts, mais doivent être déployées selon un processus maîtrisé. Inventorie les paquets, leur provenance, le support de la distribution, les correctifs disponibles, les services qui doivent redémarrer et les dépendances applicatives. Une version amont ancienne peut avoir reçu des correctifs rétroportés par le fournisseur ; ne juge pas uniquement par le numéro de version sans consulter les avis officiels.

~~~bash
# Debian / Ubuntu
sudo apt update
apt list --upgradable
sudo apt upgrade

# Famille RHEL, selon la version
sudo dnf check-update
sudo dnf upgrade
~~~

Adapte les commandes au gestionnaire de paquets et au processus de changement. Sur un serveur critique, teste dans une préproduction, prépare une sauvegarde ou un snapshot cohérent si approprié, applique dans une fenêtre approuvée puis vérifie les services, journaux et tests métier. Les mises à jour de noyau ou de bibliothèques peuvent nécessiter un redémarrage ou le redémarrage des processus.

~~~text
Avis de securite
       |
       v
Evaluation exposition / criticite / correctif
       |
       v
Test + sauvegarde + changement approuve
       |
       v
Deploiement controle
       |
       v
Version + service + tests + journaux
       |
       v
Preuve et cloture, ou rollback documente
~~~

Utilise des dépôts de confiance et vérifie signatures et clés selon les pratiques de la distribution. Évite d'exécuter en root un script d'installation distant sans vérifier sa provenance et son contenu. Les secrets d'accès aux dépôts et pipelines font partie de la chaîne logicielle ; limite leur portée et tourne-les lorsqu'ils sont exposés.

## 13. Noyau, paramètres et montages

Le durcissement du noyau peut inclure des paramètres sysctl, des restrictions de modules, et des options de montage telles que nosuid, nodev ou noexec. Leur utilité dépend du rôle du serveur : un routeur doit transférer les paquets, une plateforme de conteneurs peut nécessiter des fonctions spécifiques, et un serveur applicatif n'a pas forcément besoin des mêmes options.

~~~bash
sysctl -a 2>/dev/null | less
sysctl net.ipv4.ip_forward
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
cat /proc/cmdline
~~~

Ne colle pas une liste générique de valeurs sysctl sans comprendre leurs effets. Des réglages peuvent casser le routage, la virtualisation, les conteneurs, les mécanismes de haute disponibilité ou certains outils de supervision. Documente la valeur initiale, la valeur approuvée et le test de validation. Les options de montage doivent correspondre à l'usage de la partition et au modèle de maintenance.

Les contrôles modernes ciblés sur un service peuvent être préférables à une restriction globale. Par exemple, réduire les capabilities d'une seule unité systemd limite la portée de cette application sans casser les autres services de la machine. La configuration doit toutefois être testée sur un environnement représentatif.

## 14. AppArmor et SELinux

Les permissions Unix classiques constituent un contrôle discrétionnaire. AppArmor et SELinux ajoutent un contrôle d'accès obligatoire qui peut limiter les actions d'un processus au-delà de ses permissions traditionnelles. AppArmor associe des profils aux programmes ; SELinux s'appuie notamment sur des étiquettes et des politiques. Les distributions n'activent pas toutes les mêmes mécanismes.

~~~bash
# AppArmor si present
sudo aa-status

# SELinux si present
getenforce
sestatus
ls -Z /var/www
~~~

Un mode permissif ou d'apprentissage peut signaler des violations sans les bloquer ; le mode enforcing applique la politique. Les modalités varient. Ne désactive pas un mécanisme de sécurité juste parce qu'une application échoue : un refus peut indiquer un chemin de fichier ou un accès réseau non prévu. Analyse les journaux, vérifie le contexte et ajuste uniquement la règle ou le profil requis.

~~~text
[Processus lance]
       |
       v
Permissions Unix suffisantes ?
       |
       v
Politique MAC autorise ?
   | oui           | non
   v                v
Controle suivant    Refus / evenement journalise

DAC et MAC se completent ; chmod permissif ne contourne pas proprement
un profil obligatoire et n'est pas une correction de fond.
~~~

Un contexte SELinux erroné après copie de fichier peut empêcher un service d'accéder à ses données. Vérifie les étiquettes et utilise les outils prévus pour restaurer les contextes attendus. Pour AppArmor, examine le profil réellement chargé, reproduis l'accès en test, puis active une politique restrictive progressivement avec validation métier.

## 15. systemd et confinement de services

systemd gère de nombreux services Linux. Les unités peuvent définir l'utilisateur d'exécution, les capacités, les répertoires accessibles, les limites de ressources et plusieurs protections de confinement. La sécurité dépend autant du code que de l'environnement dans lequel il s'exécute.

~~~bash
systemctl cat mon-service
systemctl show mon-service
systemd-analyze security mon-service
journalctl -u mon-service --since today
~~~

Remplace le nom d'exemple par une unité réelle. systemd-analyze security donne une évaluation indicative de certaines protections, pas une certification de sécurité. Les options disponibles et leur efficacité dépendent de systemd, du noyau et de l'environnement.

Selon le besoin, on peut étudier NoNewPrivileges, ProtectSystem, ProtectHome, PrivateTmp, ProtectKernelTunables, ProtectKernelModules, RestrictSUIDSGID, RestrictAddressFamilies et CapabilityBoundingSet. Ne les active pas toutes automatiquement : un service de mise à jour a des droits d'écriture différents d'une API qui ne devrait écrire que dans un répertoire de données.

~~~text
[Service systemd]
      |
      +--> compte non privilegie
      +--> chemins accessibles limites
      +--> capabilities reduites
      +--> interfaces noyau non necessaires restreintes
      +--> journaux et ressources surveilles
~~~

Sauvegarde l'unité locale et inspecte les drop-ins avant le changement. Après rechargement de la configuration du gestionnaire lorsque nécessaire, vérifie que le service démarre, que ses dépendances fonctionnent, que les journaux ne montrent pas de refus et que le test métier passe. Un processus peut être actif tout en échouant sur certaines requêtes.

## 16. Capabilities Linux

Les capabilities divisent certains pouvoirs historiquement liés à root. Elles peuvent donner un droit précis à un processus plutôt qu'un privilège administratif complet. La capacité nécessaire dépend de l'opération et de l'implémentation ; il faut consulter la documentation plutôt que distribuer une capacité parce qu'elle fait disparaître une erreur.

~~~bash
getcap -r /usr /opt 2>/dev/null
getpcaps PID
capsh --print
~~~

Les outils ne sont pas forcément installés. Compare les résultats à la baseline, identifie le paquet qui possède le binaire et documente pourquoi une capability a été attribuée. Ne les supprime pas toutes en bloc : certains services en ont besoin. L'objectif est d'enlever les droits inutiles sans casser le rôle.

Le moindre privilège s'applique aussi aux conteneurs et applications. Un serveur Web lancé en root augmente l'impact d'une vulnérabilité. Préfère un compte dédié, des accès fichiers minimaux, des capacités limitées et une politique de confinement compatible avec les besoins de l'application.

## 17. Secrets et clés

Les secrets comprennent les mots de passe de base de données, clés privées SSH/TLS, jetons API, clés de chiffrement et identifiants de déploiement. Leur protection exige des permissions, une rotation, un inventaire des usages et une voie de révocation. Un secret dans un dépôt privé peut être exposé à trop de personnes ou copié dans les journaux et caches.

~~~text
Secret cree
    |
    v
Stockage de confiance et permissions strictes
    |
    v
Injection au processus qui en a besoin
    |
    v
Utilisation limitee, logs sans valeur secrete
    |
    v
Rotation, expiration ou revocation si necessaire
~~~

Évite d'inscrire un mot de passe ou jeton dans l'historique du shell, les arguments visibles de processus, les logs ou les scripts versionnés. Utilise un coffre ou le mécanisme recommandé par la plateforme. Si un secret a été exposé, le retirer du fichier courant ne suffit pas : historique Git, caches, logs et copies peuvent le contenir. Il faut l'invalider et remplacer toutes les références.

Les clés privées doivent être lisibles uniquement par le propriétaire prévu. Pour les certificats, distingue la clé privée, le certificat, la chaîne de confiance, le nom et la date d'expiration. Planifie la rotation afin de ne pas interrompre tous les clients lors d'un renouvellement.

## 18. Chiffrement et sauvegardes

Le chiffrement au repos protège les données dans certains scénarios de perte ou d'accès hors ligne. LUKS est fréquemment utilisé sous Linux. Il faut aussi gérer les clés, les procédures de déverrouillage, les métadonnées nécessaires et les scénarios de récupération. Une clé accessible en clair à un attaquant sur le même support réduit la valeur du chiffrement.

La sauvegarde doit être protégée contre la lecture, l'altération et la suppression par un compte compromis. Des copies isolées ou immuables peuvent réduire le risque de destruction simultanée, mais il faut également protéger les comptes de sauvegarde et l'administration du stockage.

~~~text
Serveur production
       |
       v
Sauvegarde chiffree
       |
       v
Compte et stockage distincts
       |
       +--> copie isolee / immuable
       |
       v
Test de restauration periodique
       |
       v
Preuve de recuperation et temps mesure
~~~

Une sauvegarde n'est validée qu'après une restauration représentative. Vérifie l'intégrité, les droits restaurés, les clés, les dépendances applicatives et le temps de rétablissement. Prévois aussi comment restaurer si le système d'identité ou le gestionnaire de secrets est indisponible.

## 19. Journaux, journalctl et audit

La journalisation doit couvrir les authentifications, sudo, événements de service, erreurs applicatives, changements de configuration et événements de sécurité. La rétention, la synchronisation horaire, le stockage et le contrôle d'accès aux journaux font partie du contrôle de sécurité.

~~~bash
journalctl -b
journalctl -p warning..alert
journalctl -u ssh --since "1 hour ago"
journalctl _COMM=sudo
last
~~~

Les noms d'unités et les destinations de logs varient selon les systèmes. Certains utilisent /var/log/auth.log, d'autres /var/log/secure, le journal systemd ou des fichiers d'application. Vérifie la configuration réelle et la collecte distante ; n'assume pas qu'une commande montre tous les événements.

~~~text
[SSH / sudo / systemd / application / noyau]
                    |
                    v
              [Journal local]
                    |
                    v
           [Collecteur distant protege]
                    |
                    v
          [Correlation / alertes / revue]
                    |
                    v
              [Investigation]
~~~

Les journaux critiques doivent être envoyés vers une destination que l'administrateur du serveur surveillé ne peut pas facilement effacer. Synchronise l'heure et évite les secrets dans les logs. auditd peut collecter les événements définis par le sous-système Linux Audit ; il faut configurer des règles adaptées au risque.

~~~bash
sudo systemctl status auditd
sudo auditctl -s
sudo ausearch -m USER_AUTH,USER_LOGIN --start today
sudo aureport --summary
~~~

Les commandes supposent que les outils existent. Les règles temporaires et persistantes ne se gèrent pas de la même manière selon la distribution. Teste un événement contrôlé, vérifie sa collecte puis confirme la transmission distante. Trop peu d'événements crée des angles morts, alors qu'une collecte excessivement bruyante peut rendre les alertes inutilisables.

## 20. Intégrité, tâches planifiées et persistance

Les changements inattendus de binaires, unités systemd, tâches cron, clés SSH, scripts root ou fichiers de configuration sont des indicateurs à examiner. Un indicateur n'est pas une preuve définitive : une mise à jour ou un déploiement peut être légitime. Corrèle avec les tickets de changement, les paquets, la signature et l'historique des journaux.

~~~bash
crontab -l
sudo ls -la /etc/cron.d /etc/cron.daily /etc/cron.hourly
systemctl list-unit-files --state=enabled
sudo find /root /home -path '*/.ssh/authorized_keys' -type f -print 2>/dev/null
~~~

Pour les tâches root, vérifie le propriétaire et les permissions des scripts et de tous les fichiers qu'ils appellent. Un script root modifiable par un compte ordinaire est une voie d'élévation de privilèges. Les tâches doivent avoir un objectif, un propriétaire et une surveillance.

Les outils d'intégrité comparent les fichiers à une référence. Leur efficacité dépend de la protection de la baseline et de la manière dont les mises à jour légitimes sont intégrées. Une copie distante et des journaux centralisés augmentent la valeur de la preuve, car un attaquant qui contrôle l'hôte peut tenter de modifier les traces locales.

## 21. Limitation des tentatives et abus d'authentification

Les échecs répétés peuvent être traités par la surveillance, une limite de débit, une politique d'identité, un pare-feu ou un outil comme fail2ban. Ces mécanismes ne remplacent ni les mises à jour ni l'authentification robuste. Ils doivent être configurés avec des seuils et un processus de récupération qui évitent de bloquer les administrateurs légitimes.

~~~text
Connexions entrantes
        |
        v
Authentification / limite de debit
        |
        v
Journaux de succes et echecs
        |
        v
Detection / blocage proportionne
        |
        v
Alerte / investigation / ajustement
~~~

Vérifie les sources, les comptes ciblés et les connexions réussies associées. Les attaques distribuées peuvent venir de nombreuses adresses ; un simple blocage IP a des limites. Un seuil trop strict peut également créer un déni de service sur un compte. La politique doit traiter ces risques avec la journalisation, les contrôles d'identité et les procédures d'assistance.

## 22. Changements de configuration

Une configuration est un actif opérationnel. Le suivi versionné permet de comparer les changements et de restaurer une version, mais ne doit pas contenir de secrets. Les fichiers gérés par les paquets ou les snippets doivent être modifiés selon les recommandations de la distribution afin que les mises à jour n'écrasent pas silencieusement les adaptations locales.

~~~text
Demande de changement
        |
        v
Validation du besoin et des dependances
        |
        v
Sauvegarde / diff / rollback
        |
        v
Test dans un environnement representatif
        |
        v
Deploiement progressif
        |
        v
Preuve de validation et documentation
~~~

Avant le changement, définis le résultat attendu, l'impact potentiel, les commandes de vérification et le critère de retour arrière. Pour l'accès distant, préserve un canal de récupération. Pour les permissions, inspecte les chemins et fichiers impactés. Pour les mises à jour, vérifie la compatibilité et les tests de service après déploiement.

## 23. Première réponse à un incident

Un incident peut être signalé par une nouvelle clé SSH, un compte privilégié inconnu, un processus inattendu, un pic de trafic, une modification d'un binaire ou l'absence soudaine des journaux. Commence par cadrer l'heure, l'hôte, l'utilisateur, la source et l'impact. Préserve les preuves requises avant d'effacer ou redémarrer le système.

~~~text
Alerte
  |
  v
Verifier heure, hote, compte, source et impact
  |
  v
Preserver logs / snapshots / preuves autorisees
  |
  v
Contenir selon un plan approuve
  |
  v
Examiner acces, processus, persistance et donnees
  |
  v
Eradiquer, restaurer, tourner les secrets
  |
  v
Verifier et documenter les lecons apprises
~~~

Selon le scénario, collecte l'état des connexions, processus, services, sockets, tâches et logs. Évite de réinstaller ou supprimer des fichiers avant d'avoir évalué ce qui doit être préservé. Pour une machine critique, suis le plan de réponse à incident de l'organisation.

Après une compromission, la rotation doit couvrir les clés SSH, comptes techniques, jetons API et accès aux sauvegardes. Une restauration n'est sûre que si l'image et les dépendances sont fiables, les secrets compromis révoqués et le vecteur initial corrigé.

## 24. TP 1 — Audit initial sans modification

**Contexte :** tu reçois un serveur de test hébergeant une application interne. Tu dois documenter son état sans effectuer de changement.

~~~bash
cat /etc/os-release
id
getent passwd
systemctl --type=service --state=running
ss -lntup
findmnt
stat /srv/application
journalctl -p warning..alert --since today
~~~

**Travail demandé :** collecte la distribution, comptes et groupes privilégiés, services, ports, permissions de l'application et journaux récents. Distingue les faits des hypothèses et identifie les éléments dont le besoin métier doit être confirmé.

**Correction attendue :** produis un tableau avec l'élément, la commande, le résultat observé, l'état attendu, l'écart, le propriétaire et l'action proposée. Ne désactive aucun service pendant l'audit initial. Chaque port doit être attribué à un processus et à un usage.

**Critère de réussite :** une autre personne peut reproduire l'audit, comprendre les écarts et identifier les actions qui nécessitent l'approbation du propriétaire de service.

## 25. TP 2 — Durcir SSH en conservant un accès de secours

**Contexte :** un serveur de laboratoire accepte l'administration distante. Tu souhaites renforcer l'authentification et limiter les sources.

**Travail demandé :** confirme la console ou l'accès de récupération, vérifie la clé d'administration, sauvegarde la configuration, vérifie les snippets, contrôle la syntaxe et teste une nouvelle session après le rechargement.

**Correction attendue :** conserve la session initiale ouverte ; n'exécute pas le rechargement si sshd -t échoue. Vérifie les valeurs effectives et le bon nom de service. Une fois les changements appliqués, ouvre une seconde session et vérifie un accès légitime ainsi qu'un refus attendu avant de terminer.

**Critère de réussite :** les administrateurs autorisés ont un chemin opérationnel, les sources non autorisées sont bloquées par la politique prévue et un accès de récupération est documenté.

## 26. TP 3 — Corriger les permissions d'une application

**Contexte :** les permissions d'un répertoire applicatif ont été rendues très larges pour résoudre une erreur. Le dossier comprend une configuration, des données et des logs.

**Travail demandé :** identifie les propriétaires, groupes, permissions et processus qui doivent accéder à chaque type de fichier. Propose un mode par répertoire et fichier, teste dans un répertoire de laboratoire puis compare le comportement avant/après.

**Correction attendue :** inspecte chaque composant du chemin avec namei, vérifie stat et getfacl et identifie l'utilisateur effectif du service. Donne les droits nécessaires à cet utilisateur ou à un groupe dédié, protège les secrets plus strictement et teste le service après changement. N'applique pas chmod -R sans analyse.

**Critère de réussite :** le service légitime fonctionne, les autres comptes ne reçoivent pas d'accès excessif et les modifications sont justifiées et réversibles.

## 27. Exercices corrigés

### Exercice 1 — Un port inconnu est à l'écoute

**Question :** faut-il le fermer immédiatement ?

**Correction :** identifie le PID, le propriétaire, l'unité, l'interface d'écoute et le besoin métier. Compare la référence de configuration, puis planifie un blocage ou un arrêt si le service est confirmé comme inutile. Fermer un service critique sans comprendre son rôle peut provoquer une interruption.

### Exercice 2 — Un secret est lisible par tous

**Question :** chmod suffit-il ?

**Correction :** il réduit l'exposition future, mais ne prouve pas que le secret n'a pas été copié. Restreins les droits, identifie le propriétaire, recherche les usages, évalue l'exposition passée puis tourne le secret si nécessaire. Les copies dans les logs et dépôts doivent aussi être examinées.

### Exercice 3 — chmod 777 résout une erreur applicative

**Correction :** ce n'est pas une correction durable. Utilise namei, stat et getfacl pour trouver le droit manquant, identifie l'utilisateur du processus et accorde l'accès précis nécessaire. Teste ensuite les accès légitimes et les refus attendus.

### Exercice 4 — sshd -t retourne une erreur

**Correction :** ne recharge pas le service. Corrige la directive, inspecte les fragments inclus ou restaure la sauvegarde. Relance le test syntaxique et vérifie les valeurs effectives. Garde la session initiale et un accès de récupération jusqu'à la validation d'une seconde connexion.

### Exercice 5 — SELinux bloque une application

**Correction :** inspecte le journal de refus, le contexte des fichiers et les règles attendues. Corrige l'étiquette ou la règle ciblée et teste. Désactiver globalement SELinux enlève une couche de sécurité et peut masquer la véritable cause du problème.

### Exercice 6 — Un compte de service appartient au groupe sudo

**Correction :** vérifie le besoin, les dépendances et le propriétaire de l'application. Retire les privilèges interactifs inutiles et utilise un accès plus étroit. Teste la fonctionnalité après retrait : il est fréquent qu'une application n'ait besoin que d'un accès précis aux données ou sockets.

### Exercice 7 — Les mises à jour sont ignorées depuis un an

**Correction :** inventorie la distribution, son support, les paquets, les dépôts et les avis de sécurité. Priorise selon exposition et criticité, teste dans un environnement représentatif et déploie avec sauvegarde, fenêtre et validation. Les exceptions doivent avoir un propriétaire et une échéance.

### Exercice 8 — Une clé SSH apparaît sans justification

**Correction :** vérifie le compte concerné, les connexions, l'historique de configuration et le propriétaire de la clé. S'il s'agit d'un accès non autorisé, révoque-le selon la procédure et vérifie les clés sur les autres hôtes. Préserve les preuves et ne suppose pas qu'une seule clé est concernée.

### Exercice 9 — Les journaux locaux ont disparu

**Correction :** examine les collecteurs distants, alertes de santé du logging, sauvegardes et autres sources datées. Vérifie l'accès au stockage et les modifications de rétention. L'absence de journal ne prouve pas l'absence d'activité ; elle peut elle-même être un événement à enquêter.

### Exercice 10 — Le service échoue après un durcissement systemd

**Correction :** inspecte l'unité effective, ses drop-ins, les journaux, les chemins fichiers et interfaces réseau. Isole l'option concernée dans un test contrôlé et ajoute une exception ciblée si elle est justifiée. Ne supprime pas tout le confinement pour faire fonctionner l'application.

### Exercice 11 — Beaucoup d'échecs SSH sont observés

**Correction :** vérifie les sources, les comptes ciblés et les connexions réussies associées. Réduis l'exposition réseau, utilise une authentification forte et des versions maintenues. Une limitation de débit ou un outil de blocage peut compléter ces contrôles, mais ne remplace pas la surveillance ni l'identité.

### Exercice 12 — La sauvegarde est présente mais ne restaure pas

**Correction :** elle n'est pas fiable tant qu'une restauration représentative n'a pas réussi. Vérifie l'intégrité, les clés, les permissions, les dépendances et le temps de reprise. Corrige les procédures et répète le test documenté.

## 28. Défi final — sécuriser un serveur d'API

### Contexte

Un serveur Linux héberge une API utilisée par un service Web. SSH est nécessaire depuis un poste d'administration. L'application doit lire sa configuration, écrire dans son répertoire de données et joindre une base située sur un autre segment. Les journaux doivent être conservés, les mises à jour gérées et les sauvegardes restaurables.

**Étape 1 — Inventorier.** Confirme la distribution, le rôle, les comptes, groupes, paquets, services, ports, routes, propriétaires et dépendances. Conserve une référence avant tout changement.

**Étape 2 — Réduire les privilèges.** Utilise des comptes nominatifs, limite sudo et exécute l'API sous un compte de service non privilégié. Retire les comptes et droits inutiles et protège les secrets par une méthode de gestion dédiée.

**Étape 3 — Sécuriser SSH.** Vérifie les clés, sauvegarde la configuration, contrôle les fragments et valeurs effectives, teste la syntaxe et conserve un accès de récupération. Valide une deuxième session avant de fermer la première.

**Étape 4 — Contrôler le réseau.** Identifie les ports actifs, limite l'exposition, applique un pare-feu hôte en cohérence avec la segmentation inter-zones et teste depuis des sources autorisées et refusées. N'autorise vers la base que la communication nécessaire.

**Étape 5 — Corriger les logiciels.** Évalue les versions, dépôts et avis de sécurité, teste les mises à jour en préproduction puis vérifie les services, versions et journaux après déploiement.

**Étape 6 — Protéger le processus.** Restreins les fichiers, utilise AppArmor ou SELinux selon la distribution et examine le confinement systemd sans activer aveuglément toutes les options. Les erreurs doivent être résolues avec des droits ciblés.

**Étape 7 — Superviser.** Collecte les authentifications, usages sudo, événements du service et changements de configuration. Synchronise l'heure et envoie les journaux sensibles vers une destination distante protégée. Évite d'enregistrer les secrets.

**Étape 8 — Sauvegarder.** Protège les copies avec des identifiants et stockages distincts, teste une restauration et vérifie permissions, secrets et dépendances. Prévois la rotation des secrets dans un scénario d'incident.

**Étape 9 — Valider.** Teste accès SSH légitime, refus de sources non autorisées, connectivité API-vers-base, refus sur les fichiers sensibles, collecte des logs et comportement applicatif. Conserve les preuves des contrôles positifs et négatifs.

**Étape 10 — Documenter.** Chaque mesure doit avoir un propriétaire, un motif, une valeur de configuration, une commande de validation, une date de revue et un retour arrière. Une sécurité efficace doit survivre au changement d'équipe et aux mises à jour.

Le défi est réussi lorsque les privilèges sont maîtrisés, les ports correspondent au besoin, SSH reste accessible par le chemin approuvé, l'application ne possède que les droits nécessaires, les journaux sont disponibles et une restauration a été prouvée.

## 29. Checklist de durcissement

- La distribution, le rôle, la criticité et les propriétaires sont documentés.
- Les comptes nominatifs sont favorisés et les comptes orphelins traités.
- Les comptes de service ne possèdent pas de droits sudo ou interactifs inutiles.
- Les règles sudo sont limitées et validées avec visudo.
- Les permissions et ACL des fichiers sensibles sont vérifiées.
- Les exécutables privilégiés et capabilities inhabituelles ont une justification.
- SSH est sauvegardé, testé et validé depuis une seconde session.
- Chaque port et service possède un besoin et un propriétaire.
- Le pare-feu correspond aux flux nécessaires et les refus sont testés.
- Les dépôts sont de confiance et les mises à jour suivent un processus contrôlé.
- AppArmor ou SELinux n'est pas désactivé pour contourner un refus sans analyse.
- Les services systemd fonctionnent avec un accès minimal.
- Les secrets ne sont pas exposés dans les dépôts, logs ou scripts.
- Les journaux sont horodatés, conservés et transmis de façon protégée.
- Les tâches planifiées et changements de fichiers sont comparés à une référence.
- Les sauvegardes sont protégées et une restauration a été testée.
- La réponse à incident protège les preuves et comprend la rotation des secrets.
- Chaque modification possède une validation et un rollback.

## 30. Glossaire

**DAC :** contrôle d'accès discrétionnaire fondé notamment sur les propriétaires et permissions.

**MAC :** contrôle d'accès obligatoire qui peut restreindre un processus indépendamment des permissions Unix traditionnelles.

**PAM :** architecture modulaire pour les contrôles d'authentification et de compte.

**sudo :** mécanisme d'exécution de commandes avec les privilèges accordés par une politique.

**SSH :** protocole chiffré de connexion et transfert à distance.

**ACL :** liste de permissions plus détaillée que le modèle propriétaire/groupe/autres.

**umask :** masque qui retire des permissions lors de la création de fichiers ou répertoires.

**setuid/setgid :** bits de permission ayant un effet particulier sur l'identité effective ou le groupe à l'exécution.

**Capability :** pouvoir précis du noyau pouvant être accordé à un processus.

**AppArmor :** mécanisme de confinement des applications par profils.

**SELinux :** architecture de contrôle d'accès qui utilise notamment étiquettes et politiques.

**systemd :** système de gestion des services et unités présent sur de nombreuses distributions.

**auditd :** composant utilisateur lié à la collecte d'événements du sous-système Linux Audit.

**Surface d'attaque :** ensemble des composants, interfaces et chemins potentiellement utilisables pour compromettre un système.

**Baseline :** état de référence approuvé permettant de détecter les dérives.

**Secret :** valeur privée comme un mot de passe, jeton ou clé dont la divulgation compromettrait une identité ou un système.

## 31. Références officielles

- Ubuntu Server — Security : https://ubuntu.com/server/docs/how-to/security/ — gestion des utilisateurs, pare-feu, AppArmor, console et chiffrement.
- Ubuntu Server — OpenSSH server : https://ubuntu.com/server/docs/how-to/security/openssh-server/ — configuration SSH, clés et précautions pour les changements.
- Ubuntu Server — AppArmor : https://ubuntu.com/server/docs/security-apparmor/ — profils, modes de fonctionnement et commandes.
- Ubuntu Server — Security suggestions : https://ubuntu.com/server/docs/explanation/security/security_suggestions/ — moindre privilège, pare-feu, SSH et mises à jour.
- Linux man-pages — capabilities(7) : https://man7.org/linux/man-pages/man7/capabilities.7.html — capacités du noyau Linux.
- systemd.exec : https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html — options de protection des chemins, capacités et confinement des services.

Les commandes et options varient selon les distributions, versions, politiques et composants installés. Consulte la documentation de ton système et teste le résultat réel avant d'appliquer un durcissement sur une machine critique.

## 32. Cas de dépannage détaillés — 30 situations

### Cas 1 — La connexion SSH échoue après un changement

**Analyse et démarche.** Une directive, un fragment inclus ou une règle de réseau peut bloquer la connexion. Garde la session active, exécute sshd -t, vérifie les snippets et les journaux. Corrige la syntaxe ou restaure le fichier, puis teste une nouvelle connexion avant de fermer l'ancienne. Confirme le nom du service de ta distribution. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne ferme pas ta seule session administrative et ne redémarre pas SSH à l'aveugle. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 2 — Une application reçoit un refus d'accès fichier

**Analyse et démarche.** Propriétaire, groupe, ACL ou politique MAC peut bloquer un accès nécessaire. Utilise namei, stat et getfacl, puis identifie l'utilisateur effectif du processus. Examine AppArmor ou SELinux si présent. Corrige seulement le droit ou label requis et valide l'accès sous l'identité de service. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne remplace pas le diagnostic par chmod 777 ou par la désactivation globale du MAC. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 3 — Un port inconnu écoute sur le réseau

**Analyse et démarche.** Un service non documenté ou un processus lancé manuellement peut exposer une nouvelle surface. Associe le socket à son PID, vérifie l'unité, l'exécutable, le propriétaire, le paquet et les logs. Compare à la baseline, confirme le besoin et organise l'arrêt ou le filtrage s'il est inutile. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne tue pas un processus sans savoir s'il porte une fonction métier ou des preuves utiles. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 4 — Un compte de service a sudo complet

**Analyse et démarche.** Une faille applicative pourrait devenir une compromission root. Examine les groupes, règles sudo et dépendances. Remplace le privilège global par les droits strictement nécessaires, teste le service et vérifie les journaux des changements. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne considère pas un nom technique comme une raison suffisante de donner root. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 5 — Une clé privée est lisible par tous

**Analyse et démarche.** D'autres comptes locaux peuvent copier le secret et tenter de l'utiliser ailleurs. Restreins les droits, identifie les usages et examine les copies potentielles dans les dépôts, logs et pipelines. Évalue la révocation ou rotation de clé, puis vérifie les accès utilisant l'ancienne clé. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne suppose pas que chmod efface une copie déjà exfiltrée. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 6 — Les mises à jour sont absentes depuis un an

**Analyse et démarche.** Le serveur peut utiliser des paquets vulnérables ou un système qui n'est plus supporté. Vérifie la version, les dépôts, les avis de sécurité et les dépendances. Priorise selon l'exposition, teste en préproduction et déploie avec sauvegarde et validation des services. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne lance pas une mise à niveau majeure en production sans plan de compatibilité et rollback. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 7 — AppArmor bloque un accès

**Analyse et démarche.** Le profil peut manquer un chemin réellement requis ou l'application viser un chemin incorrect. Examine le refus, le profil chargé et les permissions classiques. Reproduis l'accès en test et ajuste la règle précise après validation du propriétaire applicatif. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne désactive pas tous les profils pour résoudre un seul refus. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 8 — SELinux est permissif sans approbation

**Analyse et démarche.** La politique peut enregistrer les violations sans les bloquer. Confirme le mode attendu, examine les journaux, les labels et les règles. Corrige les causes, puis planifie le retour à enforcing avec des tests représentatifs. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne change pas le mode global sans examiner les blocages possibles. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 9 — Un cron root appelle un script modifiable par un utilisateur

**Analyse et démarche.** Le script peut être modifié puis exécuté avec privilèges. Inspecte les permissions du script, répertoires parents, fichiers inclus et commandes appelées. Place les éléments de confiance sous contrôle administratif et teste l'exécution planifiée. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne vérifie pas uniquement le fichier principal en ignorant les chemins qu'il utilise. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 10 — Les journaux locaux ont disparu

**Analyse et démarche.** Ils peuvent avoir été purgés, mal configurés ou supprimés suite à un incident. Vérifie le collecteur distant, les alertes de santé, les sauvegardes et les sources datées alternatives. Examine qui peut gérer la rétention et protège les preuves restantes. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne conclus pas qu'aucune activité n'a eu lieu parce que les logs sont absents. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 11 — Le pare-feu a coupé SSH

**Analyse et démarche.** La règle de gestion peut être absente ou la source d'administration erronée. Utilise la console de récupération, inspecte la politique et restaure une règle minimale pour la source attendue. Valide l'accès admin ainsi que les refus des autres sources. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne désactive pas durablement le pare-feu comme solution. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 12 — Un service systemd échoue après durcissement

**Analyse et démarche.** Une option de confinement, un chemin ou une dépendance peut avoir été restreint. Vérifie l'unité effective, ses overrides, les logs, chemins d'accès et interfaces. Teste une correction ciblée puis valide le service et son test métier. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne supprime pas toutes les protections systemd avant d'avoir identifié l'option responsable. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 13 — Des processus inconnus consomment beaucoup de ressources

**Analyse et démarche.** Il peut s'agir d'un bug applicatif, d'une tâche normale ou d'une activité malveillante. Collecte processus, sockets, services, tâches planifiées et logs avec horodatage. Compare à la baseline et préserve les éléments utiles si une compromission est plausible. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne tue pas tous les processus gourmands sans vérifier leurs dépendances. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 14 — La sauvegarde échoue sur des permissions

**Analyse et démarche.** Le compte de sauvegarde ou l'accès aux données peut ne pas correspondre au besoin. Identifie le compte effectif et la ressource, examine les logs et ajoute un accès ciblé. Lance un test de sauvegarde puis surtout une restauration représentative. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne donne pas au compte un accès général à tous les secrets. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 15 — Le système chiffré ne se déverrouille plus

**Analyse et démarche.** La récupération, les clés ou les métadonnées peuvent être incomplètes. Suis la procédure approuvée, vérifie les copies sécurisées de clés et métadonnées et teste le mécanisme de récupération sur un système non critique. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne conserve pas l'unique clé de récupération sur le disque chiffré lui-même. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 16 — Une nouvelle clé apparaît dans authorized_keys

**Analyse et démarche.** Elle peut provenir d'un changement autorisé ou d'un accès illégitime. Identifie le propriétaire et le compte, vérifie les logs de connexion et l'historique de configuration. Révoque un accès non autorisé puis examine les autres hôtes où la clé pourrait exister. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne retire pas une clé de production sans vérifier le chemin de remplacement, sauf procédure d'urgence applicable. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 17 — Une commande sudo permet d'obtenir un shell root

**Analyse et démarche.** Le programme autorisé ou ses arguments peuvent exécuter du code arbitraire. Analyse le comportement de la commande et remplace la règle par une interface administrative plus étroite, arguments contrôlés et fichiers protégés. Teste les voies indirectes d'escalade. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne juge pas le risque uniquement d'après le nom de commande dans sudoers. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 18 — Une capability inattendue est attribuée à un binaire

**Analyse et démarche.** Un exécutable peut détenir un pouvoir du noyau dont il n'a pas besoin. Compare getcap à la baseline, identifie le paquet propriétaire et le besoin du processus, puis révoque seulement après validation fonctionnelle. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne retire pas toutes les capabilities de la machine sans analyser chaque rôle. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 19 — Un service systemd écrit dans un répertoire système

**Analyse et démarche.** Le confinement peut être insuffisant ou l'application mal conçue. Inspecte les chemins requis, droits et unité effective. Limite les écritures au répertoire de données nécessaire dans un environnement de test. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** N'active pas ProtectSystem=strict sans analyser les besoins et le retour arrière. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 20 — L'événement audit attendu manque

**Analyse et démarche.** La règle peut être absente, temporaire, filtrée ou non transmise. Contrôle l'état d'audit, les règles chargées et persistantes, les filtres et les journaux distants. Reproduis un événement contrôlé et valide sa réception de bout en bout. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne suppose pas qu'auditd actif implique que toute action sensible est journalisée. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 21 — L'administration se fait depuis le poste de développement quotidien

**Analyse et démarche.** Les outils et contenus plus risqués peuvent exposer les identifiants privilégiés. Sépare les rôles si possible, utilise comptes et postes dédiés, protège les clés, limite sudo et journalise les opérations d'administration. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne considère pas tout le poste comme fiable parce qu'il appartient à l'équipe IT. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 22 — Un paquet vient d'un dépôt inconnu

**Analyse et démarche.** La provenance et la chaîne de confiance sont incertaines. Identifie le paquet, sa source et ses signatures, inspecte l'historique et les fichiers concernés, puis évalue le besoin de retrait ou de restauration depuis une source fiable. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne considère pas qu'une installation réussie est une preuve d'authenticité. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 23 — Un service écoute sur toutes les interfaces alors qu'il devrait être interne

**Analyse et démarche.** La configuration de bind ou le filtrage peut être trop permissif. Vérifie ss, la configuration de l'application, les routes et les règles de pare-feu. Restreins l'exposition et teste depuis un segment autorisé et un segment refusé. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne confonds pas l'adresse d'écoute avec la garantie de filtrage du chemin réel. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 24 — De nombreux fichiers ont des permissions trop ouvertes

**Analyse et démarche.** Une opération récursive ou un déploiement a pu modifier les droits. Compare les fichiers avec la baseline et la provenance du paquet. Restaure les propriétaires et modes attendus par type de fichier, puis identifie le changement d'origine. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne remplace pas tous les droits de /etc, /var ou /opt avec une même valeur. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 25 — Un compte retiré conserve un accès

**Analyse et démarche.** La clé peut exister dans un autre compte ou l'identité être centralisée. Inspecte comptes, clés autorisées, groupes d'annuaire, bastions, jetons et automatisations. Révoque au point autoritaire et vérifie les hôtes concernés. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne te limite pas à /etc/passwd si l'identité est gérée par un annuaire. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 26 — Un secret applicatif a pu être lu

**Analyse et démarche.** Le changement de permissions ne restaure pas la confidentialité d'un secret déjà exposé. Révoque ou renouvelle le secret, identifie les applications consommatrices et recherche des usages anormaux. Vérifie dépôts, caches, pipelines, logs et copies sauvegardées. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne réutilise pas le même secret après simple correction du mode fichier. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 27 — Le disque plein interrompt les logs

**Analyse et démarche.** Rotation, rétention ou capacité peut être inadaptée. Contrôle df, du, rotation et santé du collecteur. Préserve les événements requis, libère l'espace selon la politique et vérifie la collecte après correction. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne supprime pas manuellement les journaux à préserver pour l'enquête. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 28 — PAM empêche des comptes légitimes de se connecter

**Analyse et démarche.** Une règle ou dépendance d'authentification peut être erronée. Utilise la console de secours, compare avec la configuration sauvegardée et vérifie les modules. Teste un compte non privilégié avant de rétablir le service de connexion. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne modifie pas plusieurs modules PAM à la fois sur le seul accès distant. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 29 — Un nouveau binaire setuid apparaît

**Analyse et démarche.** Il peut être légitime après mise à jour ou avoir été implanté. Vérifie paquet propriétaire, provenance, signature, permissions et baseline. Si son origine reste inexpliquée, préserve les preuves et escalade selon le plan d'incident. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne supprime pas immédiatement le fichier sans recueillir l'information nécessaire. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 30 — Le confinement casse le déploiement d'une application

**Analyse et démarche.** Le processus a peut-être besoin d'un accès jusque-là non documenté. Examine les refus et l'unité effective, identifie le chemin ou capability nécessaire et teste une exception ciblée avec le propriétaire applicatif. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne retire pas définitivement tout le confinement pour accélérer la mise en production. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

### Cas 31 — Une restauration copie les fichiers mais l'application ne démarre pas

**Analyse et démarche.** Permissions, contexte MAC, secrets ou dépendances peuvent manquer. Vérifie intégrité, droits, labels, versions, clés et logs de démarrage. Documente et reteste une procédure complète de restauration. Note l'heure, le système, l'utilisateur, le service, la configuration effective et les journaux associés. Compare l'état observé à la baseline et distingue la cause confirmée des hypothèses. Après un changement, vérifie la fonction métier et les preuves de sécurité.

**Erreur à éviter.** Ne considère pas la copie des fichiers comme preuve d'une reprise opérationnelle réussie. Conserve le ticket, le propriétaire, la modification, le test et le retour arrière si nécessaire.

Fin du cours.
