# Introduction aux SIEM

> **Mise en contexte**

Une organisation connectée génère des événements dans de nombreux endroits : contrôleurs de domaine, postes Windows, serveurs Linux, applications, pare-feu, DNS, VPN, proxys et plateformes Cloud. Un incident laisse rarement une histoire complète dans un seul journal. Le rôle d'un SIEM est de rassembler les traces, de les rendre comparables, de les analyser dans leur contexte et de présenter des alertes que des analystes peuvent investiguer. Il ne prouve pas automatiquement qu'un système est compromis : il produit des signaux et des hypothèses qui doivent être vérifiés.

Ce cours suit le module de sécurité Active Directory. Il apprend à mettre en place une collecte fiable, comprendre les champs, concevoir des règles, réduire les faux positifs, examiner une alerte, reconstruire une chronologie et documenter une conclusion. Les exercices emploient des événements fictifs ou des commandes de lecture. Effectue les manipulations sur un laboratoire ou un système que tu es autorisé à administrer. Ne provoque pas des tentatives de connexion ou des changements privilégiés sur une production pour déclencher une règle sans procédure approuvée.

**Objectifs :** décrire l'architecture d'un SIEM ; choisir les journaux Windows, Linux, réseau et Cloud utiles ; distinguer l'heure de l'événement et l'heure de réception ; normaliser des champs ; construire des détections simples ; corréler plusieurs sources ; interpréter le résultat avec prudence ; surveiller l'état du pipeline ; estimer volume, rétention et risques de confidentialité.

## 1. Rôle et limites d'un SIEM

SIEM signifie **Security Information and Event Management**, ou gestion des informations et événements de sécurité. Il rassemble des événements, les stocke et les rend consultables, applique des règles ou des analyses et génère des alertes. Les cas d'usage typiques sont les échecs d'authentification répétés, les changements de groupes privilégiés, l'exécution d'un processus inhabituel, une sortie réseau anormale ou l'arrêt des journaux d'un actif critique.

La gestion centralisée des logs peut simplement fournir stockage et recherche. Le SIEM ajoute typiquement une logique de détection et une présentation des résultats centrée sur l'investigation. Un EDR collecte une télémétrie plus détaillée des terminaux et peut bloquer ou isoler selon sa configuration. Un XDR corrèle les signaux de domaines tels que terminaux, identité, messagerie et réseau. Un SOAR orchestre des procédures et des actions automatiques, comme enrichir une alerte ou ouvrir un ticket. Ces catégories peuvent se recouvrir selon le produit ; évalue les fonctions disponibles au lieu de conclure à partir du nom commercial.

~~~text
Poste / serveur / réseau / Cloud
          │ événements et télémétrie
          ▼
Collecteur et transport
          │
          ▼
Parsing + normalisation + enrichissement
          │
          ▼
Stockage et recherche
          │
          ▼
Règles / corrélations / analyse
          │
          ▼
Alerte ──► triage humain ──► escalade ou clôture documentée
                      │
                      └──► SOAR : tâches approuvées et réversibles
~~~

Un SIEM n'est ni un mécanisme de prévention universel ni un substitut à la réponse à incident. La qualité de la détection dépend des sources présentes, de la précision temporelle, du parsing, du mapping des champs, de la logique de règle et de la compétence de l'analyste. Une alerte de sévérité élevée peut être un faux positif ; une absence d'alerte peut signifier que l'événement n'a jamais été collecté. Les règles doivent donc décrire leurs limites et les contrôles du pipeline doivent être considérés comme un cas de sécurité à part entière.

## 2. Architecture et parcours des données

Les fonctions principales sont la source, l'agent ou connecteur de collecte, le transport, le parsing, la normalisation, l'enrichissement, le stockage, le moteur de recherche et de détection, puis l'alerte et l'investigation. Distinguer ces étapes aide à rechercher la panne : un champ manquant peut provenir de la source, d'un filtre, du transport ou du parseur, et non de la règle de détection.

~~~text
[Windows] [Linux] [Firewall] [DNS] [VPN] [Cloud]
     │        │        │        │      │      │
     └────────┴────────┴────────┴──────┴──────┘
                         │
                 agents / connecteurs
                         │
                 files / transport protégé
                         │
                  messages bruts reçus
                         │
                 parsing et normalisation
                         │
                enrichissement contrôlé
                         │
                  stockage / indexation
                         │
                 règles et recherches
                         │
                   alerte documentée
~~~

Un agent peut lire les journaux locaux et tamponner des événements pendant une courte interruption. Il exige toutefois mises à jour, permissions contrôlées, surveillance de service et configuration versionnée. Un transport sans agent peut s'appuyer sur Syslog, une API ou un service de transfert. Il faut alors vérifier les identifiants de connexion, certificats, quotas, erreurs d'API et délais. Le chiffrement en transit et la limitation des privilèges évitent que le pipeline devienne un chemin d'accès abusif.

Une file tampon absorbe une pointe de volume mais ne garantit pas une livraison sans perte : elle peut être saturée ou manquer d'espace. La livraison « au moins une fois » peut générer des doublons après une reprise ; « au plus une fois » peut perdre des événements. Les règles par comptage doivent en tenir compte. Ne déduplique pas uniquement parce que deux textes sont identiques : deux actions légitimes peuvent avoir produit le même message.

~~~text
Source ─► agent ─► file persistante ─► collecteur ─► SIEM
   │          │            │               │
   └─ compteur└─ état      └─ âge / taille  └─ erreurs
      local      service      de la file       parsing
Ces contrôles doivent être suivis séparément de l'absence d'alertes métier.
~~~

Un choix d'architecture doit préciser les sources et leurs propriétaires, les flux autorisés, les zones réseau, la méthode de transport, les garanties de reprise, les formats, les champs normalisés, la rétention, les droits d'accès, le volume de pointe et les procédures de dépannage. Deux collecteurs ne garantissent pas à eux seuls une haute disponibilité : vérifie la redondance des chemins, la répartition de charge, les certificats et le comportement des sources lors d'une panne.

## 3. Horloges, parsing et normalisation

La corrélation temporelle n'est fiable que si les horloges et fuseaux sont compris. Un poste peut écrire une heure locale et une source Cloud un timestamp UTC. Une source peut également envoyer l'événement longtemps après l'action. Conserve autant que possible l'heure de l'événement et l'heure de réception, et documente le fuseau ou l'incertitude quand il manque.

~~~text
Action source        Envoi / transport        Ingestion          Alerte
t0                   t0 + 3 s                 t0 + 8 s           t0 + 12 s
  │                        │                       │                  │
  └── event_time ──────────┴── retard ────────────┴── alert_time ────┘
event_time : instant déclaré par la source
ingest_time : réception par le collecteur ou la plateforme
alert_time : résultat produit par la règle
~~~

Synchronise les systèmes avec une source de temps maîtrisée. Sous Linux, chrony ou systemd-timesyncd peuvent être présents selon la distribution ; sous Windows, le service de temps suit l'architecture du domaine. Vérifie la configuration réelle. Ne convertis pas une heure sans fuseau en UTC sur la base d'une supposition : une conversion erronée peut inverser l'ordre des événements.

Le parsing extrait les champs du message brut. La normalisation traduit des formats différents vers des champs communs, par exemple event.category, event.action, event.outcome, event_time, ingest_time, host.name, user.name, source.ip, destination.ip, process.name et event.code. Le nom précis dépend du schéma utilisé par la plateforme. L'exemple suivant est conceptuel :

~~~text
event.category = authentication
event.action   = logon-failure
event.outcome  = failure
event_time     = 2026-10-26T21:42:10Z
host.name      = DC01.corp.example
user.name      = compte_test
source.ip      = 192.0.2.44
event.code     = 4625
raw_event      = événement d'origine préservé selon la politique
~~~

Ne remplis pas un champ en devinant. Si la source ne donne pas l'adresse IP, laisse le champ vide ou indique explicitement qu'il est inconnu ; n'inscris pas l'adresse du collecteur dans le champ de l'hôte source. Si le parseur ne parvient pas à déterminer l'action, garde le message brut et marque le parsing comme incomplet. Les événements malformés doivent être visibles dans une file de quarantaine au lieu de disparaître silencieusement.

L'enrichissement peut ajouter le propriétaire de l'actif, son environnement, sa criticité, le rôle du compte, la plage réseau ou une fenêtre de maintenance. Le référentiel doit avoir un propriétaire et une date de mise à jour : un propriétaire obsolète peut provoquer une mauvaise escalade ou cacher une activité inhabituelle. Conserve l'origine des données enrichies et, si possible, leur période de validité.

~~~text
Message brut ─► parseur versionné ─► champs normalisés
     │                 │                   │
     └── préservé      └── tests de parsing└── règles validées
                          │
                          └── anomalie visible si champ critique manquant
~~~

Mesure la qualité : taux de parsing réussi, événements sans timestamp, champs critiques manquants, doublons, retard médian et retard au 95e percentile. Segmente les métriques par source. Un gros volume Windows ne doit pas masquer la panne du collecteur DNS. Après une mise à jour de source ou de parseur, rejoue un échantillon, compare les champs et vérifie que les règles produisent toujours les résultats attendus.

## 4. Journaux Windows, Active Directory, PowerShell et Sysmon

Les journaux Windows sont répartis entre Security, System, Application et les journaux spécialisés Applications and Services. Security contient des événements d'audit selon les stratégies activées. Sysmon ajoute une télémétrie détaillée si le service est installé et configuré. Ne collecte pas tout au niveau maximal sans raison : le volume peut devenir excessif, et les événements peuvent exposer des informations sensibles.

Événements qu'un analyste doit savoir reconnaître :
- **4624** : ouverture de session réussie.
- **4625** : échec d'ouverture de session.
- **4688** : création d'un processus lorsque l'audit correspondant est activé.
- **4720** : création de compte utilisateur.
- **4728** et événements apparentés : ajout d'un membre à certaines familles de groupes, selon leur portée.
- **4719** : modification de la stratégie d'audit.
- **1102** : effacement du journal Security.
- **PowerShell 4104** : souvent associé à la journalisation des blocs de script, si elle est activée.
- **Sysmon ID 1** : création de processus ; **ID 3** : connexion réseau ; **ID 22** : requête DNS, lorsqu'ils sont activés par la configuration.

Les identifiants ne remplacent pas l'analyse du contexte. Pour 4625, examine le compte, l'hôte, le type de connexion, les codes d'état, l'adresse source si disponible et les événements voisins. Une série d'échecs depuis une seule source contre plusieurs comptes peut être un signal d'essai de mots de passe ; une rafale sur un compte technique peut venir d'un secret obsolète ou d'un service mal configuré. Une réussite juste après des échecs mérite d'être examinée, mais ne prouve pas une compromission.

~~~text
Poste ou serveur Windows
  ├─ Security : authentifications et audit
  ├─ System : services et état du système
  ├─ Application : événements applicatifs
  ├─ PowerShell Operational : script et activités selon stratégie
  └─ Sysmon Operational : processus, réseau, fichiers, registre
                           │
                           ▼
                 collecte puis parsing SIEM
~~~

Un compte ajouté à un groupe sensible exige l'identité de l'acteur, le membre, le groupe, le contrôleur de domaine, l'heure et une recherche de changement approuvé. L'acteur peut être administrateur tout en réalisant une opération non prévue. Ne crée pas une exclusion globale sur le compte d'administration. Cible les groupes à surveiller et documente les différences entre groupes globaux, locaux ou universels.

PowerShell est un outil d'administration légitime. Les termes « téléchargement », « encodage » ou « exécution dynamique » dans une ligne de commande sont des indices, pas une preuve. Corrèle le processus parent, l'identité, l'hôte, l'heure, le chemin, la signature quand elle est disponible, la destination réseau et les actions suivantes. Des scripts de déploiement approuvés peuvent partager des motifs identiques.

Sysmon consigne des observations ; il n'établit pas à lui seul qu'un processus est malveillant et ne bloque pas l'activité. Les événements deviennent plus utiles quand ils sont corrélés :

~~~text
21:03:01  processus lancé sur WS-17
21:03:03  requête DNS par ce processus
21:03:05  connexion vers une destination inhabituelle
21:03:08  fichier créé dans un répertoire temporaire
   │
   └── associer hôte + Process GUID + période et vérifier le contexte
~~~

Commande de lecture pour les échecs récents sur une machine Windows de laboratoire :

~~~powershell
Get-WinEvent -FilterHashtable @{
  LogName = 'Security'
  Id = 4625
  StartTime = (Get-Date).AddHours(-4)
} -ErrorAction SilentlyContinue |
  Select-Object -First 20 TimeCreated, MachineName, Id, Message |
  Format-List
~~~

La commande interroge le journal local sur quatre heures. Un résultat vide peut signifier qu'aucun événement ne correspond, que l'audit n'est pas activé, que le journal a été purgé, que l'hôte est incorrect ou que l'utilisateur n'a pas la permission de lecture. Le message aide à comprendre l'événement ; une collecte de production devrait s'appuyer sur des champs structurés plutôt que sur un texte localisé.

Pour examiner des événements PowerShell 4104 déjà collectés :

~~~powershell
Get-WinEvent -FilterHashtable @{
  LogName = 'Microsoft-Windows-PowerShell/Operational'
  Id = 4104
  StartTime = (Get-Date).AddHours(-2)
} -ErrorAction SilentlyContinue |
  Select-Object TimeCreated, Id, MachineName, Message
~~~

Ces commandes sont en lecture seule. Elles ne configurent pas l'audit et ne génèrent pas de télémétrie. Toute modification de stratégie d'audit doit être testée et approuvée avant de déployer en production.

## 5. Journaux Linux : journald, auditd, SSH et sudo

Linux peut utiliser systemd-journald, des fichiers traditionnels de syslog, le journal du noyau et des journaux propres aux applications. L'authentification est souvent enregistrée dans /var/log/auth.log sur certaines distributions et /var/log/secure sur d'autres. Les chemins et le nom des unités varient ; vérifie la distribution réelle avant d'automatiser la collecte.

**journald** rassemble des événements de services et du système. La persistance, les quotas et les droits dépendent de la configuration. **auditd** et Linux Audit peuvent enregistrer des actions ciblées sur les appels système, les identités ou les fichiers. Les règles d'audit doivent être adaptées au rôle du serveur ; des règles trop larges peuvent produire un gros volume et affecter les performances. Les journaux SSH montrent les sessions et échecs distants ; sudo peut fournir des traces des usages de privilèges.

~~~text
Linux
  ├── journald / journalctl : services et système
  ├── auth.log ou secure : authentification selon la distribution
  ├── auditd / ausearch : événements d'audit activés
  ├── SSH : connexions distantes
  ├── sudo : commandes élevées selon la configuration
  └── applications : accès, erreurs, opérations métier
                     │
                     ▼
              agent / Syslog
                     │
                     ▼
            parsing et corrélation
~~~

Lecture des événements SSH via journald :

~~~bash
sudo journalctl -u ssh --since "2 hours ago" --no-pager
~~~

Sur certaines distributions, le service s'appelle sshd. Si aucune ligne n'apparaît, vérifie le nom de l'unité, le filtre temporel, les permissions et le mécanisme de journalisation. Exemple de recherche dans un fichier d'authentification lorsqu'il existe :

~~~bash
sudo grep -i "failed password" /var/log/auth.log
~~~

Cette recherche textuelle est limitée : les fichiers peuvent avoir tourné, être absents ou utiliser un format différent. Pour une investigation automatisée, préfère les champs structurés. Tu peux aussi consulter journald en JSON :

~~~bash
sudo journalctl --since "2026-10-26 18:00:00" --until "2026-10-26 20:00:00" -o json
~~~

Pour interroger des événements Linux Audit déjà collectés, un exemple à vérifier sur la distribution est :

~~~bash
sudo ausearch -ts today -m USER_LOGIN
~~~

Le type d'événement et la disponibilité dépendent des règles d'audit. Une sortie vide ne prouve pas que personne n'a tenté de se connecter ; elle peut indiquer que la catégorie n'est pas collectée, que le journal est vide ou que la période ne contient aucun résultat.

Un changement de fichier critique ne doit pas être interprété sans le chemin, l'opération, l'utilisateur, le processus, l'heure et la fenêtre de maintenance. Un hash permet de constater qu'un fichier a changé, mais n'indique pas qui l'a modifié et si le changement était malveillant. Si un acteur peut modifier également la référence d'empreinte, la comparaison locale seule ne garantit pas l'intégrité.

## 6. Sources réseau, applications et Cloud

Les pare-feu peuvent journaliser l'autorisation ou le refus d'une connexion, ses adresses et ports, son protocole et son interface. Vérifie si une ligne représente un paquet, une session ou un résumé de flux. Ne mélange pas les types d'événements pour compter les connexions. Les équipements peuvent aussi enregistrer l'accès administratif et les changements de configuration ; ces traces doivent être envoyées vers une destination séparée du dispositif surveillé.

Le DNS fournit noms demandés, clients, réponses et timestamps selon la source. Un nom long ou peu courant est un signal à examiner, pas automatiquement une preuve d'activité malveillante. Les journaux de proxy peuvent contenir domaine, URL, statut HTTP, utilisateur et volume ; les URL complètes peuvent inclure des jetons ou paramètres sensibles. Collecte seulement les champs nécessaires et masque les secrets. Les journaux VPN peuvent inclure identité, IP source, adresse attribuée, MFA, heures de session et volume. Une IP publique peut être partagée par un NAT ou VPN, il ne faut pas l'utiliser seule pour attribuer une action.

~~~text
Identité / MFA ─► VPN ─► poste ─► DNS / proxy ─► ressource Cloud
       │             │       │          │                │
       └─────────────┴───────┴──────────┴────────────────┘
              corrélation SIEM par identité, hôte,
                adresse, temps et activité observée
~~~

Les journaux Cloud couvrent le plan de contrôle, authentifications, changements de privilèges, création de clés, modifications de politiques et réglages de journalisation. Vérifie les comptes, régions et environnements couverts par l'export ; certains journaux doivent être activés ou transférés explicitement. Les applications métier fournissent du contexte sur les transactions, résultats et approbations, mais peuvent exposer des données personnelles. La collecte doit correspondre à une finalité documentée.

Pour chaque source, consigne le propriétaire, la criticité, la méthode de collecte, les événements attendus, le mapping, la rétention, les champs sensibles, les droits, les objectifs de retard et le contrôle de santé. Teste la source avec des événements contrôlés et compare les journaux locaux au résultat reçu. Une source absente du catalogue ne peut pas fournir une couverture de détection fiable.

## 7. Construire des détections utiles

Commence par une question concrète, pas par un motif de texte : « un compte a-t-il accumulé un nombre anormal d'échecs dans une fenêtre ? », « un membre a-t-il été ajouté à un groupe sensible ? », « un hôte critique a-t-il cessé de transmettre ses événements ? ». Définis les sources, les champs, les seuils, les exclusions justifiées, les tests et l'action attendue pour l'analyste.

Une règle événementielle signale une action précise. Un seuil agrège des événements dans une fenêtre temporelle. Une séquence exige un ordre logique. Une corrélation multi-sources relie plusieurs systèmes. Une détection comportementale compare l'activité à une base de référence. Une fenêtre fixe découpe le temps en périodes prédéfinies ; une fenêtre glissante examine la période avant chaque évaluation. Les fenêtres doivent tenir compte des retards et des doublons.

~~~text
Événement unique : changement de configuration critique
Seuil :            10 échecs / compte / cinq minutes
Séquence :         plusieurs échecs puis réussite
Multi-source :     VPN + identité + poste + proxy
Comportement :     écart au profil normal, à vérifier
~~~

Exemple de logique pseudo-SQL :

~~~text
SELECT user.name, source.ip, COUNT(*) AS failures
FROM events
WHERE event.category = 'authentication'
  AND event.outcome = 'failure'
  AND event_time >= NOW() - 5 minutes
GROUP BY user.name, source.ip
HAVING COUNT(*) >= 10
~~~

Le seuil est un exemple de laboratoire, pas une valeur universelle. Les utilisateurs peuvent saisir leur mot de passe de manière incorrecte et les services peuvent utiliser un ancien secret. Une attaque distribuée peut répartir les échecs sur plusieurs adresses. Affiche les événements bruts, les timestamps, les hôtes et les résultats proches. Les règles de production doivent être testées avec des données représentatives et des résultats positifs et négatifs.

Pour un ajout à un groupe sensible, cible les groupes critiques et récupère acteur, membre, hôte, heure et approbation. Pour une exécution suspecte, corrèle processus parent/enfant, compte, hôte, ligne de commande, signature et activité réseau. Pour une exfiltration potentielle, compare volume, destination, heure, rôle du serveur et activité d'accès aux fichiers. Pour un changement de configuration critique, surveille acteur, état avant/après, ticket et effets sur la collecte.

~~~text
Poste
  ├─ lecture de fichiers sensibles
  ├─ requêtes DNS inhabituelles
  └─ transfert sortant plus important que la baseline
           │
           ▼
Corrélation SIEM par hôte + utilisateur + période
           │
           ▼
Alerte « transfert potentiellement anormal »
           │
           └── valider destination, contexte métier et preuves
~~~

Une règle Sigma décrit une logique de détection en YAML et peut être convertie vers différents backends compatibles. La validation YAML ne garantit pas que la règle fonctionnera : le backend, les champs, les valeurs, la fenêtre temporelle et les capacités du moteur doivent être vérifiés. Les sélections de champs ne réalisent pas automatiquement un seuil ou une séquence complexe. Versionne la règle, ajoute des tests et note les champs requis.

~~~text
Scénario ► sources ► règle versionnée ► tests positifs/négatifs
                               │
                               ▼
                    conversion/backend cible
                               │
                               ▼
                     validation sur l'échantillon
                               │
                               ▼
                    déploiement + suivi + revue
~~~

MITRE ATT&CK fournit un vocabulaire de tactiques et techniques adverses. Le mapping d'une règle vers ATT&CK décrit ce qu'elle cherche à couvrir, mais ne signifie pas que toute utilisation d'une technique sera détectée. Documente les sources, la portée, les conditions et les lacunes ; ne coche pas des techniques pour embellir une matrice de couverture.

~~~text
Couverture de détection
  ├── scénario et impact
  ├── actifs et sources disponibles
  ├── règle et champs nécessaires
  ├── résultat des tests
  └── lacunes + responsable du plan d'action
~~~

## 8. Faux positifs, faux négatifs et cycle de vie des règles

Un faux positif survient lorsque la règle s'active sans que l'activité corresponde au scénario inquiétant visé. Un faux négatif survient lorsqu'une activité préoccupante n'est pas détectée. Les deux comptent : trop d'alertes inutiles fatiguent l'équipe ; des règles insensibles créent une confiance trompeuse.

Pour régler une règle, examine un échantillon représentatif d'événements légitimes et de tests contrôlés. Identifie la cause racine : seuil trop bas, mauvaise normalisation, référentiel périmé, doublons, source mal configurée, filtre trop large ou activité métier non documentée. Modifie une variable à la fois et rejoue le même jeu de données pour vérifier que les faux positifs diminuent sans effacer les vrais scénarios. Une exclusion basée seulement sur un utilisateur ou une IP « bruyante » peut créer une zone aveugle.

~~~text
Hypothèse ► sources/champs ► règle et jeux de tests
     │
     ▼
Mode observation et calibration
     │
     ▼
Déploiement versionné + propriétaire + procédure
     │
     ▼
Mesure du volume, de la qualité et de la couverture
     │
     └──► ajuster, documenter ou retirer avec contrôle
~~~

Les exclusions doivent être étroites, documentées, attribuées à un propriétaire, justifiées et révisées à une date définie. Une tâche approuvée peut nécessiter du contexte ou une priorité adaptée plutôt qu'une exclusion permanente. L'événement de modification d'une stratégie d'audit ne doit pas devenir invisible au motif que l'auteur est un administrateur.

La priorité dépend de la criticité de l'actif, du rôle de l'identité, de l'impact potentiel, de la qualité du signal et des événements convergents. Une seule modification de journalisation sur un contrôleur de domaine peut être plus importante que de nombreux échecs sur un serveur de test. Chaque règle doit avoir un nom clair, les sources requises, les champs, les tests, un propriétaire, une version et un playbook de triage.

## 9. Investigation, chronologie et preuves

Commence par vérifier que la règle s'est déclenchée sur les données attendues. Consulte le message brut, les champs normalisés, la version du parseur et la fenêtre temporelle. Enrichis l'alerte avec le rôle du compte, le propriétaire de l'hôte, la criticité, les adresses et la zone réseau. Cherche les événements avant et après l'alerte et confirme si les sources sont complètes.

~~~text
Alerte reçue
   │
   ▼
Valider source brute, parsing et temps
   │
   ▼
Enrichir identité / hôte / actif / changement
   │
   ▼
Chronologie et requêtes multi-sources
   │
   ├── preuve insuffisante ─► rechercher / documenter les limites
   ├── activité expliquée ──► clôturer avec raison vérifiable
   └── risque significatif ─► escalade selon procédure approuvée
~~~

Une chronologie doit conserver l'heure source, le fuseau, l'heure d'ingestion et l'incertitude. Exemple fictif :

~~~text
09:14:03Z  échec d'authentification (compte A)
09:14:21Z  nouvel échec depuis la même source
09:14:37Z  authentification réussie
09:15:02Z  accès à une ressource inhabituelle
09:16:11Z  processus administratif sur le poste
           │
           ▼
Hypothèse à tester : compte compromis ou changement légitime ?
~~~

La séquence ne suffit pas à conclure à une compromission. Vérifie si les échecs sont dus à un service, si la réussite correspond à une activité attendue, si l'accès à la ressource est approuvé et si des événements indépendants corroborent l'hypothèse.

Préserve les événements bruts, identifiants source, requêtes, période, heure d'extraction, version du parseur et identité de l'analyste. Documente toute transformation et tout export. Une empreinte cryptographique peut vérifier qu'une copie n'a pas été modifiée pendant un transfert, mais ne garantit pas que le journal source soit exact ou complet.

~~~text
Source d'origine ─► export contrôlé + paramètres
                          │
                          ▼
                 copie préservée / manifeste
                          │
                          ▼
                 copie de travail analytique
                          │
                          ▼
                 note reproductible
~~~

Sépare les faits observés des hypothèses. Une note peut dire « le journal indique une connexion réussie depuis cette adresse » ; elle ne doit pas affirmer « l'attaquant a compromis le compte » sans preuves suffisantes. Escalade quand l'impact, les privilèges, l'étendue ou l'incertitude dépassent le mandat de l'analyste. Les actions de confinement ou de suppression doivent suivre la procédure et être documentées.

## 10. Rétention, coût, confidentialité et intégrité

Le volume brut par jour peut être estimé par :

~~~text
Volume brut/jour = EPS moyen × taille moyenne en octets × 86 400

Exemple :
750 événements/s × 900 octets × 86 400
≈ 58,3 GB décimaux par jour avant compression, index et réplication
~~~

Cette estimation n'inclut ni indexation, ni copies, ni sauvegardes, ni pics. Mesure des échantillons représentatifs et ajoute de la capacité pour les pointes. Choisis la rétention en fonction des scénarios d'enquête, des obligations applicables, des risques et des coûts. Le stockage chaud peut permettre une recherche rapide sur les données récentes ; une archive froide peut être moins coûteuse mais doit rester protégée et récupérable dans un délai connu.

Ne réduis pas les coûts en supprimant aveuglément les événements de niveau informatif. Certains sont essentiels à la chronologie, et certains événements de niveau élevé sont fréquents sans constituer une attaque. Si le filtrage se produit avant le SIEM, surveille les compteurs supprimés et versionne la configuration. Définis aussi la suppression des données en fin de rétention.

Les logs peuvent exposer identifiants, noms, adresses, URL ou informations clients. Applique le moindre privilège, sépare les rôles de lecture, administration des règles et suppression, journalise les accès privilégiés et protège les archives contre l'altération. Utilise un transport protégé, une gestion contrôlée des secrets et une durée de conservation documentée.

## 11. Surveiller la santé du pipeline

Une source qui cesse d'envoyer des journaux peut être en panne, perdre sa connectivité, saturer son stockage ou avoir été désactivée. La santé est donc une détection de sécurité à part entière. Mesure la dernière réception, le retard, le volume attendu, les erreurs de transport, la profondeur des files et le taux de parsing.

~~~text
Agent actif ? ─► transport disponible ? ─► collecteur reçoit ?
      │                     │                     │
      ▼                     ▼                     ▼
    heartbeat            retard / file         parsing
                                                   │
                                                   ▼
                                             index consultable
                                                   │
                                                   ▼
                                              règle de santé
~~~

Ne fixe pas une limite « aucune donnée depuis dix minutes » sans connaître la fréquence habituelle. Un serveur de développement peut être silencieux pendant des heures ; un contrôleur de domaine doit émettre des événements plus fréquemment. Définis un profil selon le rôle de l'actif et détecte l'écart avec cette attente.

Si une alerte n'apparaît pas, ne commence pas immédiatement par assouplir le seuil. Vérifie l'événement source, l'agent, le transport, la file, le collecteur, les erreurs d'authentification, le parsing, l'index et enfin la règle. Le heartbeat ne prouve pas que toutes les catégories sont collectées : complète-le avec des événements de contrôle ciblés.

~~~text
Pas d'alerte attendue
     │
     ├── l'événement existe-t-il localement ?
     ├── l'agent/export est-il actif ?
     ├── le collecteur a-t-il reçu le message ?
     ├── les champs nécessaires sont-ils parsés ?
     ├── l'événement est-il indexé et recherchable ?
     └── la règle couvre-t-elle le champ et la fenêtre ?
~~~

Les outils de laboratoire peuvent inclure PowerShell et Observateur d'événements sur Windows, journalctl et auditd sous Linux, Sigma pour décrire des règles et une solution libre de collecte/recherche si le matériel le permet. Wazuh et OpenSearch disposent de documentation officielle, mais leur configuration et leur coût d'exploitation doivent être vérifiés pour la version utilisée. Il n'est pas nécessaire de souscrire à un service payant pour réaliser les exercices ci-dessous.

## 12. TP 1 — Lire une chronologie d'authentification JSONL

### Objectif

Analyser des événements fictifs, compter les échecs et formuler une hypothèse prudente. Crée un fichier **auth-lab.jsonl** avec une ligne JSON par événement :

~~~json
{"time":"2026-10-26T09:00:00Z","host":"WS-17","user":"amina","src":"192.0.2.20","event":"auth_failure"}
{"time":"2026-10-26T09:00:17Z","host":"WS-17","user":"amina","src":"192.0.2.20","event":"auth_failure"}
{"time":"2026-10-26T09:00:31Z","host":"WS-17","user":"amina","src":"192.0.2.20","event":"auth_failure"}
{"time":"2026-10-26T09:01:09Z","host":"WS-17","user":"amina","src":"192.0.2.20","event":"auth_success"}
{"time":"2026-10-26T09:02:20Z","host":"WS-17","user":"amina","src":"192.0.2.20","event":"file_access"}
{"time":"2026-10-26T09:04:00Z","host":"WS-21","user":"service-sync","src":"192.0.2.50","event":"auth_failure"}
{"time":"2026-10-26T09:04:05Z","host":"WS-21","user":"service-sync","src":"192.0.2.50","event":"auth_failure"}
~~~

Les adresses 192.0.2.0/24 sont réservées à la documentation. Le but est d'apprendre sur des données synthétiques, pas d'identifier un réseau réel.

### Étapes

1. Valide le JSON de chaque ligne et compte les événements.
2. Filtre les lignes auth_failure.
3. Regroupe par utilisateur et source.
4. Construis la chronologie de amina et repère les événements voisins.
5. Formule deux explications possibles et liste les données manquantes.
6. Explique pourquoi un compte de service peut générer des échecs légitimes.

### Correction Python

~~~python
import json
from collections import Counter
from datetime import datetime

path = "auth-lab.jsonl"
events = []
with open(path, encoding="utf-8") as stream:
    for number, line in enumerate(stream, start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Ligne {number} invalide : {exc}") from exc

failures = [e for e in events if e.get("event") == "auth_failure"]
counts = Counter((e.get("user"), e.get("src")) for e in failures)
print("Événements lus :", len(events))
print("Échecs :", len(failures))
for (user, src), count in counts.items():
    print(user, src, count)

timeline = [e for e in events if e.get("user") == "amina"]
timeline.sort(key=lambda e: datetime.fromisoformat(e["time"].replace("Z", "+00:00")))
for event in timeline:
    print(event["time"], event["event"], event["host"])
~~~

Le résultat attendu est sept événements, cinq échecs et trois échecs rapprochés pour amina, suivis d'une réussite puis d'un accès à un fichier. Cela mérite un examen, pas une conclusion automatique de compromission. Vérifie si l'utilisateur a saisi un mot de passe incorrect, si un client réessaie et si l'accès au fichier a un motif métier. Le service-sync n'a que deux échecs proches ; recherche son propriétaire et la configuration du service avant de régler une règle.

## 13. TP 2 — Lire des événements Windows

### Prérequis

Un poste Windows de laboratoire sur lequel tu as l'autorisation de consulter le journal Security. Cette recherche est en lecture seule.

~~~powershell
$since = (Get-Date).AddHours(-4)
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    Id = 4625
    StartTime = $since
} -ErrorAction SilentlyContinue |
    Select-Object -First 20 TimeCreated, MachineName, Id, Message |
    Format-List
~~~

Note le nombre d'événements retournés, l'hôte, la période et les champs utiles. Vérifie l'événement 4625 dans la documentation Microsoft. Si aucun résultat apparaît, ne fabrique pas de données : vérifie l'hôte, le journal, les permissions, les stratégies d'audit et la période. Si les journaux sont visibles localement mais absents du SIEM, compare réception, parsing, index et recherche.

### Correction

Une bonne correction indique que 4625 est un échec d'ouverture de session et cite les limites de la requête. Elle vérifie l'identité, l'hôte, le type de connexion, les champs source disponibles et les événements voisins. Elle ne déduit pas une attaque sur la seule présence d'échecs. Une validation de la chaîne SIEM doit permettre de retrouver un événement de laboratoire du journal local jusqu'à la recherche normalisée et à la règle concernée.

## 14. TP 3 — Examens des journaux Linux et du temps

Sur une VM Linux de test, commence par vérifier l'état temporel :

~~~bash
timedatectl status
~~~

Puis examine les événements SSH récents. Selon la distribution, remplace ssh par sshd :

~~~bash
sudo journalctl -u ssh --since "2 hours ago" --no-pager
~~~

Note le nom de l'unité, la période, la disponibilité des journaux et les champs d'authentification. Une réponse vide ne prouve pas l'absence d'activité : l'unité peut porter un autre nom, les logs peuvent être stockés dans un fichier, la période peut être vide ou les droits de lecture insuffisants. Compare ensuite l'événement local à sa représentation reçue dans le SIEM. Si les valeurs diffèrent, identifie si la cause est le fuseau, le parseur ou un enrichissement.

### Correction

Une correction valide comporte le nom du système, la source consultée, la période et les événements observés. Elle vérifie si l'heure est synchronisée et si les données sont arrivées dans la plateforme. En cas de perte, elle examine l'agent/export, le transport, la file du collecteur et le parsing. Elle ne présente pas la présence d'échecs SSH comme une preuve d'intrusion.

## 15. Douze exercices avec réponses expliquées

### Exercice 1 — SIEM et gestion de logs

**Question :** une plateforme stocke et recherche les logs, mais ne contient aucune détection de sécurité. Est-ce nécessairement un SIEM complet ?

**Réponse :** non. Elle fournit une base de centralisation. Le SIEM apporte typiquement des détections et des alertes investigables en plus du stockage. Il faut évaluer les fonctions réelles plutôt que le nom du produit.

### Exercice 2 — Aucun résultat 4625

**Question :** aucune occurrence 4625 n'est retournée par Get-WinEvent. Quelle conclusion est valide ?

**Réponse :** aucun événement correspondant n'a été retourné par cette requête, sur cet hôte et cette période avec cette configuration. Cela ne prouve pas qu'il n'y a eu aucun échec. Vérifie audit, journal, permissions, heure et hôte.

### Exercice 3 — Échecs suivis d'une réussite

**Question :** un compte a plusieurs échecs puis une réussite. Est-il compromis ?

**Réponse :** cela mérite une investigation. Examine la source, le type de connexion, l'état du compte, l'hôte et l'activité ultérieure. Une erreur de mot de passe corrigée est aussi possible.

### Exercice 4 — Timestamp sans fuseau

**Question :** une source fournit l'heure 09:00:00 sans fuseau. Peut-on l'insérer avec certitude dans une chronologie UTC ?

**Réponse :** non. Il faut connaître le fuseau et la convention de la source, ou conserver l'incertitude. Une conversion devinée peut inverser l'ordre des faits.

### Exercice 5 — Mauvais champ source.ip

**Question :** le SIEM remplit source.ip avec l'adresse du collecteur parce que l'événement source ne donne pas cette valeur. Quel est le problème ?

**Réponse :** le champ est trompeur. Une valeur inconnue doit rester inconnue. L'adresse du collecteur n'est pas nécessairement l'origine de l'action. Préserve le brut et corrige le mapping.

### Exercice 6 — Sysmon

**Question :** Sysmon journalise un processus et une connexion réseau. Cela prouve-t-il la malveillance ?

**Réponse :** non. Sysmon observe des activités. Il faut corréler processus parent, identité, ligne de commande, destination et événements associés avant de conclure.

### Exercice 7 — Ajout à un groupe privilégié

**Question :** l'acteur d'un ajout à un groupe privilégié est administrateur. Peut-on ignorer l'événement ?

**Réponse :** non. Vérifie le membre, le groupe, la portée, le ticket de changement, l'hôte et les activités suivantes. Les privilèges techniques de l'acteur ne prouvent pas que l'action est approuvée.

### Exercice 8 — Réduire des alertes de sauvegarde

**Question :** une tâche de sauvegarde génère des alertes de volume. Quelle démarche est la plus prudente ?

**Réponse :** caractériser la tâche, sa destination, son propriétaire, son calendrier et son volume normal. Une exception doit être étroite et révisable ; une exclusion globale peut masquer une future activité anormale.

### Exercice 9 — Sigma valide

**Question :** une règle Sigma est valide en YAML. Peut-on déployer sans autre test ?

**Réponse :** non. Vérifie mapping, backend, champs, valeurs, conversion et résultats sur des données positives et négatives. Une syntaxe valide ne prouve pas une détection correcte.

### Exercice 10 — Mapping ATT&CK

**Question :** une règle associée à une technique MITRE ATT&CK détecte-t-elle toutes les utilisations de cette technique ?

**Réponse :** non. Le mapping décrit le comportement visé, mais la couverture dépend des sources, des champs, des conditions et des tests. Les limites doivent être documentées.

### Exercice 11 — Logs absents

**Question :** un hôte cesse de transmettre ses journaux et aucune alerte métier n'apparaît. Est-ce rassurant ?

**Réponse :** non. La visibilité est dégradée. Vérifie l'agent, le réseau, le collecteur, les files, les règles de parsing et l'heure de dernière réception.

### Exercice 12 — Rétention illimitée

**Question :** pourquoi ne pas conserver indéfiniment tous les logs ?

**Réponse :** cela augmente coûts, accès abusifs et exposition des données personnelles. La rétention doit équilibrer besoins de réponse, audit, coûts et confidentialité, avec un processus de suppression vérifiable.

### Exercice 13 — Retard d'ingestion

**Question :** un événement arrive dix minutes après son heure source et la règle inspecte seulement deux minutes. Que vérifier ?

**Réponse :** le retard entre event_time et ingest_time, le tampon, les paramètres de fenêtre et la stratégie de rattrapage. La règle peut avoir manqué l'événement à cause de son retard.

### Exercice 14 — Volume sortant élevé

**Question :** le SIEM ne montre que le volume envoyé vers une destination. Quelles données manquent pour l'investigation ?

**Réponse :** l'identité, l'hôte, la destination, la fenêtre, la criticité, le contexte métier et les autres événements pertinents. Le volume seul ne prouve pas une exfiltration.

## 16. Défi final — Investigation multi-sources

### Situation

Dans un laboratoire fictif, le SIEM affiche les quatre événements suivants :

~~~json
{"time":"2026-10-26T08:40:00Z","source":"vpn","host":"VPN-GW-01","user":"nora","src":"198.51.100.28","event":"vpn_login_success","mfa":"passed"}
{"time":"2026-10-26T08:44:15Z","source":"windows-security","host":"DC-LAB-01","user":"nora","event_id":4728,"target_group":"Sensitive-Admins","actor":"ops-admin"}
{"time":"2026-10-26T08:49:50Z","source":"proxy","host":"PROXY-01","user":"nora","dst":"203.0.113.80","bytes_out":180000000,"domain":"upload.example.invalid"}
{"time":"2026-10-26T08:52:10Z","source":"pipeline-health","host":"WS-17","event":"last_seen_exceeded","minutes_without_logs":12}
~~~

Tous les identifiants et les adresses sont fictifs. Le premier indique une connexion VPN réussie avec MFA selon le jeu d'essai. Le deuxième est une représentation normalisée d'un changement de groupe, à confirmer par l'événement natif dans un vrai système. Le troisième indique un transfert à examiner ; le quatrième est une perte de visibilité. La proximité temporelle ne prouve pas qu'ils sont causalement liés.

### Travail demandé

1. Sépare faits, hypothèses et informations manquantes.
2. Établis la chronologie en UTC.
3. Liste les sources supplémentaires à interroger.
4. Évalue une priorité initiale sans conclure automatiquement à une compromission.
5. Décris la préservation des preuves et le contrôle de pipeline.
6. Propose une règle corrélée et une séquence négative de test.
7. Écris une note finale d'investigation en séparant faits et hypothèses.

### Correction pas à pas

**Étape 1 — Faits.** Le jeu contient une connexion VPN réussie pour nora avec MFA passé, un changement de groupe attribué à ops-admin, un volume sortant mesuré par le proxy et un événement de santé indiquant qu'un hôte n'envoie plus ses journaux. Il faut confirmer que les sources et identités sont correctement normalisées.

**Étape 2 — Hypothèses.** Une identité compromise pourrait avoir servi à une modification de privilège suivie d'un transfert. Une opération légitime pourrait aussi coïncider avec une panne de collecte. Les événements peuvent représenter plusieurs activités indépendantes. Les données initiales ne suffisent pas à trancher.

**Étape 3 — Sources.** Recherche les événements du fournisseur d'identité, les connexions et processus de l'endpoint, le détail natif du changement de groupe, le ticket d'approbation, les logs proxy et DNS, les événements d'accès aux fichiers et l'état de l'agent sur WS-17. Documente les sources manquantes.

**Étape 4 — Priorité.** Le groupe sensible, le transfert inhabituel et la perte de visibilité justifient un triage prioritaire dans ce scénario, mais le lien causal demeure à vérifier. La sévérité doit suivre la politique de l'organisation et les impacts potentiels.

**Étape 5 — Preuves.** Conserve événements bruts, IDs source, heures d'événement et d'ingestion, requêtes, versions du parseur et résultats d'enrichissement. N'efface aucun compte ou fichier avant les étapes de réponse prévues. Toute action de confinement doit être autorisée et documentée.

**Étape 6 — Détection.** Une règle candidate pourrait relier la session distante, le changement privilégié et le transfert inhabituel par identité, hôte et fenêtre. Elle doit inclure les événements qui justifient l'alerte. Teste un cas positif synthétique et un cas négatif où le transfert correspond à une sauvegarde approuvée.

**Étape 7 — Pipeline.** Vérifie l'agent, le transport, le dernier événement local, le réseau, les files et la configuration d'export de WS-17. Traite l'absence de journaux comme une incertitude de visibilité, pas comme une preuve que l'activité a cessé.

**Étape 8 — Note possible.** « Le SIEM a rapproché une connexion VPN réussie, un changement vers un groupe sensible, un volume sortant inhabituel et une perte de journaux sur un poste. Ces signaux méritent une investigation prioritaire. Le lien causal reste à établir. Il faut confirmer l'approbation du changement de groupe, examiner le compte et la destination, préserver les événements et rétablir la visibilité. Aucune compromission ne peut être déclarée uniquement à partir de ces quatre événements. »

Le défi est réussi si la note distingue faits et hypothèses, cite les données manquantes, préserve la preuve et propose une règle testable plutôt qu'une conclusion automatique.

## 17. Checklist opérationnelle

Avant d'activer une source :
- Le propriétaire, le cas d'usage et les événements attendus sont documentés.
- La collecte, l'authentification du connecteur et le transport sont protégés.
- Le fuseau et la synchronisation horaire sont compris.
- Les champs bruts et normalisés sont comparés sur un échantillon.
- Le volume de pointe, la rétention et les données sensibles sont estimés.
- Le contrôle de santé et la procédure de panne sont définis.
- Des tests positifs, négatifs et de retard sont disponibles.

Avant de déployer une règle :
- Le scénario et l'impact sont décrits.
- Les sources et champs requis existent réellement.
- Fenêtres, agrégations et exclusions sont testées.
- Le résultat contient le contexte nécessaire au triage.
- Le mapping ATT&CK est justifié et ses limites documentées.
- Le propriétaire, la version, les tests et la date de revue sont définis.
- Toute réponse automatique à fort impact est approuvée et réversible.

Lors d'une investigation :
- Les événements bruts, timestamps, IDs et requêtes sont préservés.
- Les horloges, retards et sources absentes sont documentés.
- Les faits sont distincts des hypothèses.
- Les actions, approbations et changements de règle sont traçables.
- La conclusion reflète le niveau de confiance disponible.

## 18. Glossaire

**Agent de collecte :** composant qui lit les événements d'un système et les transmet à une plateforme.

**Alerte :** résultat d'une règle ou d'une analyse qui nécessite une évaluation.

**Baseline :** description du comportement attendu d'une entité sur une période de référence.

**Corrélation :** rapprochement d'événements par champs communs, fenêtres temporelles ou séquences logiques.

**EDR :** fonction de détection et réponse centrée sur les terminaux.

**Enrichissement :** ajout d'un contexte contrôlé, tel que propriétaire ou criticité.

**Event time :** moment auquel la source affirme que l'événement a eu lieu.

**Faux négatif :** activité pertinente non détectée par la règle.

**Faux positif :** alerte qui ne correspond pas au scénario inquiétant visé.

**Ingestion time :** moment où le collecteur ou le SIEM reçoit l'événement.

**Journal brut :** représentation d'origine de l'événement, conservée avant ou parallèlement à sa normalisation.

**MITRE ATT&CK :** base de connaissances des tactiques et techniques adverses.

**Normalisation :** traduction des données de plusieurs sources vers un ensemble de champs cohérent.

**Parsing :** extraction des champs depuis un message ou document structuré.

**Playbook :** procédure documentée d'investigation ou de réponse.

**Rétention :** durée de conservation et de disponibilité des journaux.

**SIEM :** plateforme de gestion, recherche, analyse et détection des événements de sécurité.

**SOAR :** orchestration, automatisation et réponse aux incidents.

**Sigma :** format de description de règles de détection, converti vers un backend compatible.

**Syslog :** famille de formats et mécanismes de transport de messages de journalisation.

**Triage :** première phase d'analyse visant à établir nature, urgence et prochaine action.

**XDR :** approche de détection corrélant la télémétrie de plusieurs domaines.

## 19. Références officielles

- Microsoft Learn, référence des événements Windows envoyés vers Sentinel : https://learn.microsoft.com/en-us/azure/sentinel/windows-security-event-id-reference
- Microsoft Learn, audit des ouvertures de session : https://learn.microsoft.com/windows/security/threat-protection/auditing/basic-audit-logon-events
- Microsoft Learn, événement 4625 : https://learn.microsoft.com/fr-fr/windows/security/threat-protection/auditing/event-4625
- Microsoft Learn, événements Sysmon : https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/sysmon-events
- Microsoft Learn, lire et régler les événements Sysmon : https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/read-tune-sysmon-events
- Microsoft Learn, activer et configurer Sysmon : https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/how-to-enable-sysmon
- Microsoft Learn, connecteurs de sources de données Sentinel : https://learn.microsoft.com/en-us/azure/sentinel/configure-data-connector
- systemd, documentation de journald : https://www.freedesktop.org/software/systemd/man/latest/journald.html
- systemd, documentation de journalctl : https://www.freedesktop.org/software/systemd/man/latest/journalctl.html
- Linux Audit, projet et documentation : https://github.com/linux-audit/audit-userspace
- Sigma, dépôt officiel : https://github.com/SigmaHQ/sigma
- MITRE ATT&CK Enterprise : https://attack.mitre.org/tactics/enterprise/
- Wazuh, documentation officielle : https://documentation.wazuh.com/current/
- OpenSearch, documentation officielle : https://opensearch.org/docs/latest/

Les formats, versions et conditions de licence peuvent évoluer. Consulte la documentation correspondant à la version installée, valide les exemples sur des données de laboratoire et vérifie les prérequis avant usage opérationnel. Les liens sont des points de départ ; ils ne garantissent pas qu'un événement ou champ soit activé dans un environnement donné.

## 20. Conclusion

Un SIEM devient utile lorsque les événements sont fiables, le temps est compris, les champs sont normalisés, les sources sont surveillées et les règles répondent à des scénarios précis. Une détection doit rendre visibles ses raisons et ses limites. L'investigation relie les faits sans confondre signal et preuve ; le réglage des faux positifs doit préserver la couverture des risques.

Commence par des sources critiques, mesure leur fiabilité, teste les règles avec des événements contrôlés et améliore la plateforme à partir des enquêtes. Le pipeline et sa santé font partie de la sécurité tout autant que les alertes métier.

Fin du cours.

## 21. Scénarios complémentaires de dépannage et de tuning

Chaque scénario doit se conclure par une hypothèse documentée, les données manquantes et un test de régression. L'objectif est de pratiquer une investigation défendable, pas de transformer automatiquement chaque anomalie en incident confirmé.


### Rotation de mot de passe

Après une réinitialisation, des clients peuvent continuer à utiliser l'ancien secret et provoquer des échecs légitimes. Rapproche le changement de mot de passe, les échecs et la prochaine réussite. Si le bruit cesse après la mise à jour, documente cette explication et ajuste la règle de façon étroite. Ne transforme pas une explication valable pour un compte en exclusion permanente de tous les événements de cette identité.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Nouveau collecteur

L'arrivée d'un collecteur peut modifier le volume, les champs et les timestamps. Valide son identité, ses permissions, ses certificats, sa latence, ses erreurs et son comportement en cas de panne. Compare des événements bruts avant et après le changement et recherche les doublons. Documente quel collecteur est la source de référence pour chaque type de journal.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### GPO modifiée

Une stratégie de groupe peut modifier l'audit, les paramètres de sécurité ou des scripts. Vérifie l'acteur, le contrôleur de domaine, la portée, la configuration avant/après et le ticket de changement. Une stratégie attendue peut être modifiée accidentellement ; une règle doit surveiller la réduction de visibilité et pas simplement rechercher un nom de GPO.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Dérive de parsing

Un champ utilisateur devient vide après une mise à jour même si les messages continuent d'arriver. Compare les messages bruts, le parseur versionné et les champs extraits. Ajoute un test qui échoue si un champ critique disparaît. Corriger le parseur est préférable à l'exclusion des événements que la règle ne comprend plus.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Compte d'urgence

Le compte d'urgence doit rester surveillé même s'il est utilisé exceptionnellement. Relie activation, connexion, actions privilégiées et désactivation avec une approbation. Une procédure d'urgence autorisée peut réduire l'urgence d'une alerte, mais ne justifie pas de rendre ses opérations invisibles.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Logs Cloud désactivés

Un changement de configuration Cloud peut réduire l'export des journaux. Surveille les modifications de paramètres, erreurs du connecteur et absences de données. Le silence d'une table ne suffit pas : contrôle les journaux du plan de contrôle et le statut d'export. Une voie de santé indépendante est utile lorsque le connecteur lui-même est touché.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Rotation de certificat

Un certificat expiré ou renouvelé peut interrompre la collecte. Vérifie le propriétaire, les dates, l'identité du connecteur, les erreurs de transport et le débit avant/après. La règle de santé doit nommer les sources impactées et l'heure de dernière réception afin d'accélérer la résolution.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Transfert SaaS

Un transfert vers un fournisseur SaaS peut être attendu, mais il faut vérifier le compte, le domaine, l'application, le volume et l'approbation. Un référentiel de destinations doit avoir un propriétaire et une date de revue. Évite l'exclusion universelle d'un fournisseur, car la légitimité peut dépendre de l'identité ou de la ressource.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Création de compte puis privilège

La création suivie d'un ajout à un groupe et d'une connexion en peu de temps peut nécessiter un triage prioritaire. Vérifie les événements de création, activation, groupes et première connexion. Les workflows d'approvisionnement font parfois les étapes rapidement ; la règle doit distinguer l'automatisation connue d'un changement interactif inattendu.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Horloge en avance

Un serveur émet des événements plusieurs minutes dans le futur. Vérifie le service de temps et la source de référence. Conserve l'heure originale et documente la dérive plutôt que de corriger silencieusement la preuve. Ajuste les corrélations uniquement avec une limite connue et une procédure de retour à la normale.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### IP partagée

Plusieurs utilisateurs apparaissent derrière la même adresse à cause d'un NAT, proxy ou VPN. Corrèle l'identité, la session, l'adresse attribuée et l'heure. Ne déduis pas qu'un seul humain est responsable parce qu'une IP est identique. Si les journaux de passerelle manquent, indique la limite et recherche une autre clé fiable.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Secret dans un journal

Un journal contient accidentellement un jeton ou mot de passe. Restreins son accès, applique les procédures de rotation et corrige la source pour masquer les secrets. Une rédaction après ingestion n'efface pas les copies exportées. Examine les réplicas, tickets et archives selon la politique applicable.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Volume de source doublé

Un déploiement peut doubler le volume à cause d'une catégorie utile ou d'une boucle de journalisation. Compare événements par catégorie, retries et changement de verbosité. Mesure le retard et le coût. N'élimine pas en bloc les nouveaux événements avant d'avoir évalué s'ils couvrent un scénario de sécurité important.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Connexion nocturne

Une connexion hors des heures habituelles peut correspondre à une astreinte, un déploiement ou un autre fuseau horaire. Vérifie le calendrier, le rôle du compte, le poste, la ressource et l'approbation. L'heure seule est un contexte, pas une preuve d'attaque. Évite les exclusions permanentes pour des équipes qui travaillent en rotation.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Alerte répétée

La reprise de collecte peut recréer une alerte sur le même événement. Identifie une clé stable, la fenêtre de regroupement et les éléments qui justifient une réouverture. Un regroupement trop large peut fusionner plusieurs incidents ; trop étroit, il surcharge l'équipe. Garde les événements originaux accessibles.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### DNS peu courant

Un domaine rare ou un nom long peut être lié à une application normale, CDN ou mécanisme de télémétrie. Compare la fréquence, l'hôte, le processus et les connexions associées. Les listes de réputation vieillissent ; vérifie la date et la provenance. La requête DNS est un signal de triage, pas une preuve autonome.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Compte de service

Les comptes de service sont parfois bruyants, mais ne doivent pas être exclus de la détection. Documente propriétaire, but, hôtes attendus, droits, méthode d'authentification et rotation. Une connexion interactive ou depuis un nouvel hôte peut être plus significative que le nombre brut d'échecs. Vérifie si le secret a été changé récemment.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Pare-feu modifié

Une règle de pare-feu peut être approuvée ou ouvrir une exposition non voulue. Relie l'acteur, le poste source, l'état avant/après et le ticket. Si le journal ne décrit pas le diff, utilise une sauvegarde versionnée. Une modification qui réduit l'audit mérite aussi un contrôle de santé indépendant.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Événements hors ordre

Les événements peuvent être reçus après ceux qui leur sont postérieurs. Conserve event_time et ingest_time et mesure la latence par source. Une règle basée uniquement sur l'ordre d'arrivée peut manquer une séquence. Documente la tolérance de retard et les limites de rattrapage.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Indicateur ancien

Un domaine ou une IP d'un flux de renseignement peut être périmé, réattribué ou partagé. Vérifie provenance, confiance, date et contexte, puis examine la communication observée. Une correspondance est un signal à examiner, pas une confirmation automatique. Expire les indicateurs selon une procédure documentée.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Reprise après panne réseau

Après une interruption, la source peut retransmettre des événements, en perdre ou les envoyer en retard. Compare les compteurs source, les files et le débit reçu. Vérifie si les doublons ont gonflé les seuils. La politique de rattrapage doit être testée en laboratoire et documentée.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Application sans propriétaire

Une nouvelle application envoie des journaux sans personne responsable. Le flux peut contenir des données personnelles et les alertes ne sont assignées à aucune équipe. Attribue un propriétaire, une finalité, une rétention, les champs nécessaires et les droits d'accès avant d'élargir la collecte.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### PowerShell en maintenance

Une commande inhabituelle pendant une maintenance peut être justifiée mais doit être vérifiée. Examine ticket, compte, hôte, parent de processus, script et activité réseau. Une fenêtre autorisée n'est pas une exclusion totale ; une commande inhabituelle n'est pas toujours malveillante.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### API Cloud au format changé

Les appels API arrivent mais les champs d'action sont vides après un changement. Compare le schéma et le parseur, préserve des exemples sécurisés et ajoute un contrôle sur les champs manquants. Une règle qui ignore les événements incomplets peut manquer un changement d'accès sensible.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Rétention trop courte

Une activité lente ne peut plus être corrélée car les premières données ont été supprimées. Révise les scénarios de menace, les délais d'escalade et les exigences applicables, puis ajuste la rétention ciblée. Une archive doit être récupérable et protégée ; conserver indéfiniment tout le contenu n'est pas une bonne réponse automatique.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Règle sur un nom d'hôte

Une règle ciblant seulement DC01 cesse de fonctionner après renommage ou remplacement. Utilise un inventaire fiable des rôles d'actifs plutôt que le seul nom libre et vérifie les hôtes attendus. Une migration doit déclencher des tests de couverture pour les actifs critiques.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Exclusion expirée

Une exception pour une fenêtre de maintenance reste active après sa date de fin. Toute exception doit avoir propriétaire, justification, expiration et alerte de dépassement. Teste que la règle retrouve son comportement normal à la fin de la fenêtre.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Champ brut différent du champ normalisé

Le texte brut indique un compte humain mais le champ normalisé indique un compte de service. Vérifie le parseur, la provenance et l'enrichissement. Les règles doivent utiliser des champs validés. Ajoute un cas de test similaire pour prévenir la récidive.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### État différent entre contrôleurs

Deux contrôleurs consignent des événements proches ou des copies. Vérifie réplication, horloges, acteur et identifiant de l'objet pour éviter de compter deux fois la même opération. Ne fusionne pas automatiquement toutes les lignes proches : confirme leurs sémantiques dans la documentation du journal.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Disque de collecteur saturé

Le service reste actif mais le disque approche de la saturation. Surveille espace libre, débit, profondeur de file et âge des événements. Une alerte de capacité doit précéder les pertes. Corrige la cause ou augmente la capacité selon le processus, sans effacer des archives hors politique.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Messages malformés en quarantaine

Un lot d'événements échoue au parsing. Examine un échantillon protégé, classe la cause, corrige la source ou le parseur puis rejoue les données si possible. Garde un compteur de quarantaine et alerte sur les augmentations soudaines. Un événement malformé peut contenir la seule trace d'une action critique.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

### Migration d'identité

Un nouveau fournisseur d'identité change les IDs et attributs des utilisateurs. Mets à jour mappings, enrichissements et tests avant de généraliser. Une différence d'identifiant ne doit pas être automatiquement interprétée comme un nouvel utilisateur. Maintiens une correspondance versionnée quand elle est légitime.

**Contrôle de l'analyste :** confirme la source brute, l'heure et le champ de corrélation ; vérifie une explication légitime ; cite les données absentes ; décris un test positif et un test négatif ; limite toute exclusion au contexte démontré et prévois une date de revue.

Fin du cours.
