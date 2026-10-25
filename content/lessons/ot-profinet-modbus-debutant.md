# Protocoles industriels Modbus & PROFINET — Débutant

## Mise en contexte : comment un automate échange-t-il avec le terrain ?

Dans une installation industrielle, un automate programmable (API/PLC) reçoit des mesures de capteurs, exécute un programme de commande et pilote des actionneurs : moteurs, vannes, pompes, convoyeurs ou îlots d’entrées/sorties déportées. Les équipements doivent échanger des valeurs et des états de manière suffisamment fiable pour que le procédé fonctionne comme prévu.

Deux technologies très répandues remplissent des rôles qui se recoupent parfois, mais qui ne sont pas identiques : **Modbus** et **PROFINET**. Modbus est d’abord un protocole applicatif d’échange de données, historiquement utilisé sur des liaisons série puis sur TCP/IP. PROFINET est une technologie d’Ethernet industriel avec une architecture de contrôleur et de périphériques, des échanges d’E/S cycliques, des services acycliques et des mécanismes de temps réel adaptés à différentes applications.

> **Encadré de mise en contexte.** Modbus et PROFINET ne sont pas deux noms pour la même chose. Modbus décrit surtout la façon de demander et de retourner des données. PROFINET décrit aussi une architecture d’automatisation, la configuration des équipements et des échanges d’E/S cycliques avec des classes de communication adaptées aux besoins de temps réel. Le choix dépend du procédé, des équipements, du temps de cycle, du diagnostic requis, de l’architecture et des compétences disponibles.

Ce cours constitue le premier niveau d’un parcours progressif. Il vise à permettre de lire une architecture, reconnaître les composants et comprendre les échanges sans supposer que l’apprenant connaît déjà l’automatisme industriel.

## Objectifs pédagogiques

À la fin du cours, tu devras pouvoir :

- décrire le chemin d’une donnée entre capteur, module d’E/S, automate, IHM et supervision ;
- expliquer le rôle de Modbus RTU, Modbus TCP et PROFINET ;
- différencier client/serveur Modbus des rôles contrôleur/périphérique PROFINET ;
- reconnaître les principales familles d’objets Modbus ;
- comprendre la différence entre une communication cyclique et une lecture à la demande ;
- lire un schéma réseau industriel simple et relever les informations manquantes ;
- préparer un laboratoire simulé et interpréter une transaction de lecture ;
- appliquer les précautions élémentaires de sécurité à un réseau OT.

## 1. Les fondamentaux de l’automatisme industriel

### 1.1 Les composants d’une cellule automatisée

Un **capteur** mesure une grandeur physique : température, pression, niveau, présence, vitesse ou position. Un **actionneur** produit une action : ouvrir une vanne, déplacer un moteur, activer un relais ou faire avancer une pièce. L’API/PLC exécute une logique de commande et relie les mesures aux décisions. L’IHM donne à l’opérateur une représentation de l’installation. La supervision (SCADA) collecte des données, présente des alarmes et peut historiser les mesures.

```text
             ENVIRONNEMENT PHYSIQUE / PROCÉDÉ
  Température, pression, niveau, position, vitesse
                       │
                       ▼
                 Capteurs terrain
                       │ signal / données
                       ▼
          ┌──────────────────────────┐
          │ API / PLC                │
          │ logique de commande      │
          │ interverrouillages       │
          └──────────────────────────┘
                       │ sorties
                       ▼
             Variateurs, vannes,
              contacteurs, robots
                       │
                       ▼
                    Procédé

       IHM / SCADA ─── données et commandes autorisées
```

Les protocoles ne remplacent pas la logique de commande. Ils transportent des informations entre équipements. Le comportement sûr de la machine dépend aussi du programme, de la conception électrique, des fonctions de sécurité, des procédures d’exploitation et de la validation du système complet.

### 1.2 Quelques notions réseau indispensables

- **Adresse MAC :** identifiant de couche Ethernet utilisé pour livrer une trame sur un segment local.
- **Adresse IP :** identifie une interface dans un réseau IP et sert au routage entre sous-réseaux.
- **Port TCP/UDP :** identifie un service de transport sur une machine. Modbus TCP utilise habituellement TCP/502.
- **Commutateur industriel :** relie des équipements Ethernet ; selon le modèle, il peut offrir VLAN, QoS, supervision, redondance et diagnostics.
- **Sous-réseau :** groupe d’adresses IP défini par un préfixe, par exemple `192.168.10.0/24`.
- **Passerelle :** équipement qui achemine le trafic vers un autre sous-réseau. Toutes les communications industrielles n’ont pas besoin d’une passerelle.

```text
 API/PLC                  Commutateur                   E/S déportées
192.168.10.10  ────────  [ ETH 1 | ETH 2 ]  ─────────  192.168.10.20
                                 │
                                 ├────────────── IHM 192.168.10.30
                                 │
                                 └────────────── Station d’ingénierie

Exemple pédagogique : toutes les interfaces sont dans 192.168.10.0/24.
Les adresses sont fictives et doivent être adaptées au laboratoire.
```

Une communication qui fonctionne au niveau IP n’est pas nécessairement une communication applicative fonctionnelle. Un `ping` peut réussir tandis qu’un équipement refuse le service Modbus, qu’un registre est mal interprété ou qu’un contrôleur PROFINET n’établit pas ses relations d’E/S.

## 2. Comprendre Modbus

### 2.1 Qu’est-ce que Modbus ?

Modbus est un protocole applicatif défini pour échanger des données entre équipements d’automatisation. Une transaction typique consiste en une requête et une réponse. La requête précise une fonction, une adresse ou un ensemble de valeurs ; la réponse retourne les données demandées ou indique une exception.

Dans le modèle historique, on parle de **maître/esclave**. Dans la terminologie plus courante du Modbus TCP moderne, les rôles sont souvent décrits comme **client/serveur** : le client initie une requête et le serveur la traite. Ces termes décrivent les rôles de communication, pas la valeur hiérarchique des équipements.

```text
Client Modbus (souvent PLC, IHM ou passerelle)
        │
        │ 1. Requête : lire les registres 100 à 103
        ▼
Serveur Modbus (compteur, variateur, PLC, passerelle)
        │
        │ 2. Réponse : valeurs demandées ou code d’exception
        ▼
Client Modbus
```

Modbus ne fixe pas à lui seul le support physique. On le rencontre notamment en **Modbus RTU sur ligne série**, en **Modbus TCP sur Ethernet/IP**, et dans des architectures de conversion au moyen de passerelles série/Ethernet.

### 2.2 Modbus RTU, Modbus TCP et passerelles

| Variante | Transport courant | Caractéristiques à retenir | Point de vigilance |
|---|---|---|---|
| Modbus RTU | RS-485 ou RS-232 selon l’installation | Trames série, adresse de station et contrôle CRC | Câblage, polarité, terminaison, débit et format série |
| Modbus TCP | TCP/IP sur Ethernet, port TCP 502 par défaut | En-tête MBAP et PDU Modbus ; pas de CRC Modbus RTU dans l’ADU TCP | Réseau IP, ports autorisés, délais, gestion des connexions |
| Passerelle RTU/TCP | Série d’un côté, Ethernet/IP de l’autre | Traduit/achemine les transactions entre deux domaines | Mapping des unités, délais, conversions et diagnostic de chaque côté |
| Modbus Security | Modbus encapsulé dans TLS, certificats X.509 | Variante conçue pour ajouter authentification et intégrité du transport | Disponibilité et compatibilité réelles sur les équipements concernés ; port 802 spécifié par l’organisation Modbus |

Il ne faut pas supposer qu’un équipement utilisant Modbus TCP prend automatiquement en charge Modbus Security. C’est une capacité distincte qui doit être confirmée dans la documentation du produit.

### 2.3 Les quatre familles de données Modbus

Les cartes de mémoire classiques sont souvent présentées au moyen de quatre familles. Les noms et la documentation des fabricants peuvent différer ; il faut suivre la table d’adressage publiée pour le modèle exact.

| Famille courante | Type | Accès habituel | Exemple d’usage |
|---|---|---|---|
| Coils | Bits | Lecture et écriture selon fonction et droits | Commande binaire, drapeau logique |
| Discrete Inputs | Bits | Lecture | État d’une entrée logique |
| Input Registers | Mots de 16 bits | Lecture | Mesure analogique ou valeur d’état |
| Holding Registers | Mots de 16 bits | Lecture et, si autorisé, écriture | Consigne, compteur, paramètre ou valeur mesurée |

Un registre Modbus fait **16 bits**. Une mesure sur 32 bits peut utiliser deux registres ; un flottant peut aussi occuper deux registres. L’ordre des octets et l’ordre des mots ne sont pas uniformes dans tous les produits. Un nombre incohérent peut donc être la conséquence d’une convention d’encodage mal comprise plutôt qu’une panne réseau.

```text
Exemple fictif de table d’un variateur
+----------------------+----------------------+--------------------------+
| Élément              | Adresse documentée   | Interprétation           |
+----------------------+----------------------+--------------------------+
| État du moteur       | Discrete Input 0     | 0 = arrêté, 1 = en marche|
| Fréquence mesurée    | Input Register 10    | Valeur brute / 10 = Hz   |
| Consigne fréquence   | Holding Register 20  | Écriture autorisée       |
| Défaut présent       | Coil 4               | 0 = aucun, 1 = défaut    |
+----------------------+----------------------+--------------------------+

Toutes les adresses et mises à l’échelle de cet exemple sont fictives.
Elles ne doivent pas être réutilisées sur un équipement réel sans sa notice.
```

### 2.4 Les codes de fonction les plus connus

| Code décimal | Nom courant | Fonction générale |
|---:|---|---|
| 01 | Read Coils | Lire des bits de type coil |
| 02 | Read Discrete Inputs | Lire des entrées discrètes |
| 03 | Read Holding Registers | Lire des registres de maintien |
| 04 | Read Input Registers | Lire des registres d’entrée |
| 05 | Write Single Coil | Écrire un seul coil |
| 06 | Write Single Register | Écrire un registre |
| 15 (`0x0F`) | Write Multiple Coils | Écrire plusieurs coils |
| 16 (`0x10`) | Write Multiple Registers | Écrire plusieurs registres |

Une réponse d’exception utilise le code de fonction avec le bit de poids fort activé. Par exemple, une exception liée à la fonction 03 utilise `0x83` comme code de fonction de réponse. Le code d’exception explique la catégorie du problème, comme une fonction non acceptée, une adresse invalide ou une valeur non valide, selon la spécification et l’implémentation.

**Important :** les opérations d’écriture peuvent modifier le procédé ou un paramètre critique. Dans les ateliers de débutant, on se limite à la lecture sur un serveur simulé. Toute écriture sur un équipement réel exige une autorisation explicite, une validation fonctionnelle et un plan de retour arrière.

### 2.5 Adressage : pourquoi deux notices peuvent sembler se contredire

La notation traditionnelle `40001`, `30001`, etc. est souvent une convention documentaire qui identifie une famille de données et une position. Le champ d’adresse transporté dans la PDU Modbus est généralement un offset commençant à zéro. Des bibliothèques, API et notices peuvent exposer l’offset brut ou une adresse de référence décalée.

Exemple pédagogique : si la notice déclare « Holding Register 40001 », elle peut correspondre à l’offset PDU `0`. Un outil qui attend l’offset peut donc demander `0`, et non `40001`. Il faut vérifier l’outil, le fabricant et l’exemple de lecture associé.

```text
Notation dans une notice               Adresse d’offset dans la requête
40001  ──────────────────────────────► 0
40002  ──────────────────────────────► 1
40003  ──────────────────────────────► 2

Correspondance illustrative, pas une règle universelle de toutes les API.
Toujours vérifier comment le logiciel représente les adresses.
```

### 2.6 Anatomie d’une transaction Modbus TCP

Une requête Modbus TCP comprend un en-tête **MBAP** puis une **PDU Modbus**. L’en-tête MBAP contient notamment l’identifiant de transaction, l’identifiant de protocole, la longueur et l’identifiant d’unité. L’identifiant d’unité est particulièrement utile avec certaines passerelles ou architectures multi-équipements.

```text
Modbus TCP ADU
┌──────────────────────────────────────────────────────────┐
│ MBAP Header (7 octets)                                   │
│ Transaction ID | Protocol ID | Length | Unit ID           │
├──────────────────────────────────────────────────────────┤
│ PDU Modbus                                                │
│ Function Code | Data (adresse, quantité, valeurs, etc.)  │
└──────────────────────────────────────────────────────────┘

Exemple de lecture : FC=03, adresse de départ=0, quantité=2.
Le serveur retourne un nombre d’octets puis les deux registres.
```

Le champ Protocol ID vaut zéro dans le profil Modbus TCP usuel. Contrairement à une trame RTU, l’ADU Modbus TCP n’ajoute pas le CRC16 RTU : la longueur de l’ADU est portée par MBAP et le transport TCP assure ses contrôles propres. Cela ne signifie pas que la communication est chiffrée ou authentifiée.

## 3. Comprendre PROFINET

### 3.1 Qu’est-ce que PROFINET ?

PROFINET est une technologie d’Ethernet industriel développée au sein de l’écosystème PROFIBUS & PROFINET International (PI). Elle sert notamment à relier des automates, des îlots d’E/S déportées, des variateurs, des robots et des systèmes d’ingénierie. Elle prend en charge des échanges de données cycliques et des services acycliques, ainsi que des mécanismes de communication adaptés aux besoins de temps réel.

Le mot « Ethernet » ne signifie pas que toutes les trames PROFINET sont des paquets TCP/IP. Certaines communications PROFINET RT et IRT utilisent des mécanismes Ethernet temps réel spécifiques. Les services d’ingénierie, de configuration et d’autres fonctions peuvent utiliser différents protocoles selon leur rôle.

### 3.2 Les trois rôles de base

| Rôle | Fonction | Exemple |
|---|---|---|
| IO Controller | Contrôle les échanges d’E/S et exploite le périphérique dans le programme | Automate PLC |
| IO Device | Expose des modules ou données d’E/S au contrôleur | Bloc d’E/S déportées, variateur, équipement de terrain |
| IO Supervisor | Sert à l’ingénierie, au diagnostic et à la mise en service | PC d’ingénierie ou outil de maintenance |

Ces rôles sont fonctionnels. Ils ne sont pas les mêmes que les rôles client/serveur d’une transaction Modbus.

```text
              IO Supervisor
           (ingénierie/diagnostic)
                     │
                     ▼
               Ethernet industriel
        ┌────────────┴────────────┐
        ▼                         ▼
  IO Controller              IO Device
  (API / PLC)            (E/S déportées)
        │                         │
        │ programme               ├─ Entrées : capteurs
        │ de commande             └─ Sorties : actionneurs
        └──────── échange cyclique d’E/S ────────┘
```

### 3.3 Échanges cycliques et acycliques

Les données **cycliques** sont échangées de façon répétée selon un cycle configuré : état d’entrées, valeurs de sortie, mesures et consignes. Elles servent au fonctionnement régulier de l’automatisation. Les services **acycliques** sont utilisés à la demande pour des opérations comme la lecture ou l’écriture de paramètres, des diagnostics et certaines informations d’identification.

```text
Temps ───────────────────────────────────────────────────────────►

Cycle 1       Cycle 2       Cycle 3       Cycle 4
[Entrées][Sorties] [Entrées][Sorties] [Entrées][Sorties] [Entrées][Sorties]
   │                │              │               │
   └────────────── échange cyclique ───────────────┘

En parallèle, une requête acyclique peut lire un diagnostic ou un paramètre.
Elle ne remplace pas le flux cyclique d’E/S.
```

Un cycle rapide n’est pas automatiquement meilleur. Il faut respecter les capacités de l’automate, du périphérique, du réseau et les contraintes du procédé. Le temps de cycle, la gigue admissible, les options de synchronisation et les limites du matériel doivent être vérifiés dans le projet d’ingénierie.

### 3.4 RT et IRT : le temps réel selon le besoin

- **PROFINET RT (Real Time)** fournit une communication temps réel adaptée à de nombreuses tâches d’automatisation industrielle. Il s’appuie sur des mécanismes optimisés pour les échanges de données cycliques.
- **PROFINET IRT (Isochronous Real Time)** vise des applications demandant une synchronisation et un déterminisme plus stricts, comme certaines applications de mouvement. Il exige des équipements et une planification compatibles.
- **TSN (Time-Sensitive Networking)** est une famille de standards Ethernet qui peut être intégrée à des architectures industrielles. Ne suppose pas qu’un équipement PROFINET quelconque prend en charge toutes les fonctions TSN : la compatibilité doit être vérifiée.

Il ne faut pas résumer la distinction par « RT est lent, IRT est rapide ». Le bon choix dépend de l’application, du cycle, de la précision temporelle nécessaire et des capacités des composants.

### 3.5 GSDML, nom de station et découverte

Le fichier **GSDML** (General Station Description Markup Language) décrit les caractéristiques d’un périphérique : modules disponibles, paramètres, identifiants, options et diagnostics. L’outil d’ingénierie l’utilise pour configurer le périphérique dans le projet.

Le **nom PROFINET de l’équipement** et son adresse IP sont deux éléments différents. Pendant la mise en service, des mécanismes de découverte et de configuration de couche 2, notamment DCP, peuvent permettre de retrouver un équipement et de lui affecter son nom ou ses paramètres IP. Un nom incorrect, dupliqué ou absent peut empêcher l’établissement correct de la relation d’E/S, même si le câble et le commutateur fonctionnent.

```text
Outil d’ingénierie
      │ importe GSDML
      ▼
Projet : contrôleur + périphériques + modules + paramètres
      │ téléchargement / mise en service
      ▼
Réseau PROFINET ─── découverte/configuration ─── IO Device
      │                                           │
      └──── nom, adresse, configuration attendue ─┘
```

### 3.6 Topologie, LLDP et redondance

Les équipements et commutateurs compatibles peuvent utiliser LLDP pour échanger des informations de voisinage. Les outils d’ingénierie peuvent comparer la topologie attendue à la topologie détectée et aider à repérer un mauvais câblage, un port inattendu ou un périphérique déplacé.

Dans certaines architectures, le **Media Redundancy Protocol (MRP)** permet de construire un anneau Ethernet avec un mécanisme de récupération adapté aux équipements compatibles. La redondance de média ne rend pas automatiquement toute l’installation redondante : alimentation, contrôleur, commutateurs, câbles, configuration et comportement applicatif doivent aussi être analysés.

## 4. Comparer Modbus et PROFINET sans les confondre

| Critère | Modbus RTU/TCP | PROFINET |
|---|---|---|
| Nature | Protocole applicatif d’échange de données | Technologie Ethernet industriel avec architecture d’E/S |
| Modèle courant | Requête/réponse, client/serveur | IO Controller, IO Device, IO Supervisor |
| Données | Coils, entrées discrètes, registres de 16 bits, blocs de données | Modules d’E/S, données cycliques, paramètres et diagnostics acycliques |
| Transport | Série pour RTU ; TCP/IP pour Modbus TCP | Ethernet industriel ; mécanismes temps réel spécifiques et services complémentaires |
| Temps réel déterministe | À évaluer au niveau de l’ensemble du système ; Modbus TCP standard ne fournit pas à lui seul un ordonnancement IRT | Classes RT/IRT, selon les équipements et la conception |
| Configuration | Table Modbus, paramètres et adresses du dispositif | Projet d’ingénierie, GSDML, nom de station et paramètres de périphérique |
| Diagnostic | Exceptions, délais, erreurs série, valeurs et registres | État de relation d’E/S, alarmes, diagnostics de modules, topologie et état réseau |
| Sécurité | Les versions classiques n’apportent pas toujours authentification/chiffrement ; Modbus Security est une option distincte | Les capacités de sécurité dépendent de la génération, des profils, du produit et de l’architecture |

**Règle pratique :** il ne faut pas décider qu’un protocole est « meilleur » sans connaître la fonction requise. Modbus est souvent adapté aux lectures de mesures, à l’intégration d’instruments et aux échanges simples avec une table de données bien documentée. PROFINET est fréquemment employé pour des E/S cycliques et des architectures d’automatisation Ethernet intégrées. Certaines installations utilisent les deux.

## 5. Exemple d’architecture mixte

```text
                           Réseau de supervision
                         ┌────────────────────────┐
                         │ SCADA / Historien      │
                         │ poste opérateur        │
                         └───────────┬────────────┘
                                     │ flux autorisés
                              [Pare-feu / L3]
                                     │
                 Réseau cellule / réseau automate
        ┌────────────────────────────┴──────────────────────────┐
        │                                                       │
        ▼                                                       ▼
   [API/PLC] ── PROFINET ── [E/S déportées]               [Passerelle]
        │                                                       │
        │                                                       └─ Modbus RTU/RS-485
        │                                                            │
        ▼                                                            ▼
    IHM locale                                                 Compteur d’énergie

Exemple de conception : les flux entre zones doivent être explicitement définis.
La passerelle n’est pas une permission automatique de connecter les réseaux.
```

Dans une architecture réelle, l’emplacement d’un pare-feu, d’une passerelle ou d’un serveur dépend de l’analyse de risque. Une connexion SCADA vers une passerelle Modbus peut être autorisée uniquement depuis un poste précis et pour les fonctions nécessaires. Il faut éviter d’exposer directement les automates au réseau bureautique ou à Internet.

## 6. Lire et diagnostiquer une communication Modbus

### 6.1 Méthode simple en cinq étapes

1. Vérifier le câblage ou le lien Ethernet, les LEDs et la vitesse négociée.
2. Confirmer l’adresse IP, le masque, le routage nécessaire et l’absence de conflit d’adresse.
3. Confirmer que le service Modbus est activé et que le client contacte la bonne adresse et le bon port.
4. Vérifier la table de registres, la fonction, l’offset, la quantité et le format de valeur.
5. Comparer la valeur lue à une mesure de référence et examiner les journaux ou exceptions.

### 6.2 Tableau de dépannage

| Symptôme | Causes possibles | Vérifications non intrusives |
|---|---|---|
| Aucun lien Ethernet | Câble, alimentation, port, module défaillant | LEDs, lien côté commutateur, documentation du port |
| Ping impossible | IP/masque incorrect, VLAN, route, ACL, équipement arrêté | Plan d’adressage, état du port, table ARP avec autorisation |
| TCP/502 inaccessible | Service désactivé, ACL, adresse ou port incorrect | Journaux du pare-feu, configuration approuvée et test autorisé |
| Exception Modbus | Fonction non supportée, adresse/quantité incorrecte, valeur invalide | Table officielle du fabricant et code d’exception |
| Valeur plausible mais erronée | Mauvais offset, échelle, signe, ordre des mots | Registre de référence, format et unité documentés |
| Valeurs qui se figent | Polling interrompu, délai, connexion fermée, appareil saturé | Horodatages, compteurs d’erreur, fréquence de scrutation |

N’effectue pas de balayage de ports, de test de charge, de fuzzing ou d’écritures de registres sur un réseau de production sans autorisation documentée. Certains équipements industriels anciens ne tolèrent pas les sondes agressives.

## 7. Atelier pratique 1 — Lire une table Modbus fictive

### Objectif

Savoir passer d’une documentation de registre à une interprétation correcte de la donnée.

### Scénario

Un serveur simulé représente un compteur. La table pédagogique indique :

| Donnée | Famille | Offset PDU | Taille | Décodage |
|---|---|---:|---:|---|
| Tension | Input Register | 0 | 1 registre | valeur brute / 10 = V |
| Courant | Input Register | 1 | 1 registre | valeur brute / 100 = A |
| Énergie | Input Register | 10–11 | 2 registres | entier 32 bits, ordre documenté par le simulateur |
| Consigne de relais | Coil | 0 | 1 bit | **Ne pas écrire dans ce TP** |

Les valeurs et adresses sont inventées et servent seulement à apprendre la démarche.

### Procédure

1. Utiliser un simulateur Modbus local, sur une machine isolée, ou un environnement pédagogique fourni par l’enseignant.
2. Déclarer le serveur et son port selon la documentation du simulateur.
3. Lire deux Input Registers à partir de l’offset 0 avec la fonction 04.
4. Noter les valeurs brutes, puis appliquer les échelles indiquées.
5. Lire les offsets 10 et 11, sans inventer l’ordre des mots : suivre la convention explicitement fournie par le simulateur.
6. Comparer les résultats à la valeur de référence générée par le laboratoire.

### Correction attendue

- Deux registres à partir de l’offset 0 doivent renvoyer les valeurs de tension et de courant dans cet exemple.
- Une valeur brute de `2301` signifie `230,1 V` avec l’échelle définie, et non `2301 V`.
- Une valeur brute de `1542` pour le courant donne `15,42 A` si la mise à l’échelle est `/100`.
- Pour la donnée 32 bits, il est impossible de déduire la valeur exacte sans connaître l’ordre des mots et le type numérique choisi. Identifier cette incertitude fait partie de la correction.
- Aucun coil n’est écrit : le laboratoire est en lecture seule.

## 8. Atelier pratique 2 — Construire un plan d’adressage de cellule

### Objectif

Dessiner une architecture Ethernet simple et cohérente avant de raccorder les équipements.

### Énoncé

Une cellule simulée contient un PLC, une IHM, un équipement Modbus TCP et un poste d’ingénierie temporaire. Propose un plan d’adressage dans `192.168.40.0/24`.

### Correction possible

| Équipement | Adresse d’exemple | Rôle |
|---|---|---|
| PLC | `192.168.40.10/24` | Contrôle de la cellule |
| IHM | `192.168.40.20/24` | Interface opérateur |
| Serveur Modbus simulé | `192.168.40.30/24` | Données de mesure |
| Station d’ingénierie | `192.168.40.50/24` | Maintenance contrôlée |

```text
             VLAN_CELLULE (exemple pédagogique)
  ┌──────────────┐      ┌─────────────────┐
  │ PLC          │──────│                 │───── IHM
  │ .40.10       │      │ Commutateur     │      .40.20
  └──────────────┘      │ industriel      │
                        │                 │───── Simulateur Modbus
                        └─────────────────┘      .40.30
                                │
                                └─ Port temporaire contrôlé : .40.50
```

Dans une vraie installation, l’adresse de réseau et le masque ne sont pas choisis uniquement par commodité. Ils doivent s’intégrer au plan OT global, aux zones, aux routes, aux règles de pare-feu et aux exigences du fournisseur. Le poste d’ingénierie ne doit pas rester connecté sans nécessité.

## 9. Atelier pratique 3 — Préparer un projet PROFINET

### Objectif

Comprendre les étapes d’ingénierie sans se connecter à un automate réel.

### Procédure

1. Ouvrir un environnement de formation ou un projet hors ligne.
2. Relever le modèle et la version des équipements de la maquette.
3. Télécharger le fichier GSDML du modèle exact depuis le fournisseur officiel, après vérification de la signature ou de l’intégrité lorsque cette option existe.
4. Importer le périphérique dans le projet d’ingénierie.
5. Ajouter les modules d’E/S correspondant à la configuration réelle de la maquette.
6. Définir une topologie, un nom de station unique et les paramètres réseau attendus.
7. Vérifier la cohérence des modules, la longueur des données d’E/S et les diagnostics du projet.
8. En simulation ou hors ligne, documenter les étapes nécessaires à la mise en service ; ne pas télécharger le projet sur un système en production.

### Correction attendue

Un bon dossier doit mentionner le modèle exact, la révision matérielle/logicielle, le GSDML utilisé, le nom de station, l’adresse IP prévue, les modules dans l’ordre requis, les paramètres importants et une méthode de retour à la configuration précédente. L’apprenant doit savoir expliquer que le nom PROFINET et l’adresse IP sont deux éléments distincts.

## 10. Atelier pratique 4 — Lire une capture réseau en laboratoire

### Objectif

Distinguer une transaction Modbus TCP d’un échange PROFINET.

### Procédure

1. Capturer du trafic provenant uniquement d’un simulateur ou d’une maquette autorisée.
2. Filtrer sur `tcp.port == 502` pour rechercher du Modbus TCP.
3. Examiner l’identifiant de transaction, le code de fonction, l’adresse demandée et la réponse.
4. Pour une capture PROFINET, utiliser les décodeurs disponibles dans la version de Wireshark et identifier les paquets de découverte, diagnostics ou E/S si le trafic est présent.
5. Enregistrer la capture anonymisée avec l’heure, l’équipement simulé et le scénario.

Les noms de filtres et le décodage exact peuvent varier avec la version de l’outil et les protocoles présents. Une capture faite sur un port commuté ordinaire ne montre pas automatiquement le trafic unicast des autres ports ; un port miroir ou un TAP approuvé peut être nécessaire.

## 11. Sécurité minimale pour Modbus et PROFINET

Les protocoles industriels transportent parfois des commandes ayant une conséquence physique. La sécurité ne doit donc pas être ramenée à la seule confidentialité des données.

Principes à retenir :

- inventorier les PLC, variateurs, passerelles, équipements d’E/S, versions et fonctions actives ;
- segmenter les réseaux de contrôle, d’ingénierie et de supervision selon les flux réels ;
- n’autoriser que les origines, destinations, services et directions nécessaires ;
- limiter et superviser les accès distants des fournisseurs ;
- conserver des sauvegardes de programmes, de projets d’ingénierie, de configurations et de tables de registres ;
- surveiller les changements de configuration, de nom de station, d’adresse et de comportement réseau ;
- valider les mises à jour dans un environnement de test et appliquer la gestion de changement ;
- ne pas réaliser de scans actifs ou d’écritures de registre sans accord de l’exploitant.

Les variantes classiques de Modbus n’offrent pas, à elles seules, une authentification ou un chiffrement universel. Modbus Security ajoute TLS et des certificats, mais la compatibilité doit être confirmée sur les clients, serveurs et passerelles. Les mécanismes disponibles dans PROFINET varient aussi selon la génération de spécification et les équipements : ne présume pas que tous les dispositifs historiques chiffrent ou authentifient toutes leurs communications.

## 12. Exercices corrigés

### Exercice 1 — Quel rôle initie une transaction Modbus ?

**Question :** un client Modbus demande au serveur de lire trois registres. Qui initie la transaction ?

**Correction :** le client initie la requête ; le serveur la traite et retourne une réponse ou une exception. Le client/serveur est le modèle de transaction, pas une description de la fonction physique de l’équipement.

### Exercice 2 — Quel transport utilise Modbus TCP ?

**Question :** un technicien indique que Modbus TCP est uniquement un protocole Ethernet de couche 2. Est-ce exact ?

**Correction :** non. Modbus TCP encapsule la PDU Modbus dans un message avec en-tête MBAP, transporté via TCP/IP sur Ethernet ou un autre réseau IP approprié. Le port TCP par défaut est 502.

### Exercice 3 — Interpréter une valeur mise à l’échelle

**Question :** la notice fictive déclare que la température vaut le registre brut divisé par 10. Le client lit 287. Quelle valeur afficher ?

**Correction :** `28,7` dans l’unité prescrite par la notice. La lecture brute et l’unité doivent rester documentées ; il ne faut pas supposer que l’unité est le degré Celsius si la table ne l’indique pas.

### Exercice 4 — Un offset semble incorrect

**Question :** une notice donne `40001`, mais l’outil attend un offset et la lecture réussit à l’adresse `0`. Pourquoi ?

**Correction :** la notation `40001` peut être un identifiant de référence traditionnel. L’offset transporté dans la requête commence généralement à zéro. Il faut suivre la convention documentée par la notice et l’outil.

### Exercice 5 — Les rôles PROFINET

**Question :** quel est le rôle d’un IO Controller et d’un IO Device ?

**Correction :** l’IO Controller contrôle les échanges d’E/S dans l’architecture PROFINET ; l’IO Device expose ses données d’E/S et diagnostics. Un PLC est fréquemment contrôleur, tandis qu’un module d’E/S déportées ou un variateur peut être périphérique.

### Exercice 6 — Cyclique contre acyclique

**Question :** une mesure remonte chaque cycle tandis qu’un technicien demande le diagnostic d’un module. Quelle différence ?

**Correction :** la valeur régulière appartient aux échanges cycliques d’E/S ; la lecture de diagnostic est typiquement un service acyclique. Les deux sont complémentaires.

### Exercice 7 — Pourquoi le périphérique n’est-il pas reconnu ?

**Question :** le lien Ethernet est actif mais le contrôleur signale que le périphérique PROFINET attendu est absent. Donne trois vérifications.

**Correction :** vérifier le nom de station et son unicité, le GSDML/modèle et les modules configurés, puis le port/VLAN/topologie et les diagnostics du contrôleur. Le fait que le lien physique soit actif ne prouve pas que la relation d’E/S est correctement établie.

### Exercice 8 — Sécurité d’un réseau Modbus

**Question :** pourquoi ne faut-il pas publier le port 502 d’un automate sur Internet ?

**Correction :** le service peut exposer des données et, selon les fonctions prises en charge, permettre des écritures. Les implémentations classiques ne fournissent pas automatiquement une authentification et un chiffrement forts. Il faut utiliser une architecture d’accès contrôlée, une segmentation et des mesures adaptées au risque.

## 13. Défi final corrigé — Petite cellule de production

### Situation

Une cellule fictive comporte un PLC, des E/S PROFINET, un compteur d’énergie Modbus TCP, une IHM et un serveur SCADA. Le SCADA doit afficher l’énergie et les alarmes ; il ne doit pas pouvoir modifier directement les sorties de commande du PLC. Le poste d’ingénierie doit être autorisé uniquement pendant les interventions.

### Travail demandé

1. Dessiner l’architecture et nommer les flux.
2. Proposer les informations d’inventaire à collecter.
3. Définir une démarche de mise en service PROFINET.
4. Définir la démarche de lecture Modbus.
5. Décrire trois mesures de sécurité et une méthode de diagnostic.

### Correction proposée

```text
                 Zone supervision
          ┌──────────────────────────┐
          │ SCADA : affichage/alarme │
          └────────────┬─────────────┘
                       │ lecture des seules données prévues
                 [Pare-feu / ACL]
                       │ flux explicitement autorisés
          ┌────────────┴────────────────────┐
          │ Zone cellule                    │
          │                                 │
          │ PLC ── PROFINET ── E/S          │
          │  │                              │
          │  └──── accès Modbus autorisé ─ Compteur
          │                                 │
          │ IHM locale                      │
          └─────────────────────────────────┘

  Station d’ingénierie : accès contrôlé et temporaire, journalisé.
```

Inventaire à collecter : fabricant, modèle, version, rôle, emplacement, adresses IP/MAC, nom de station PROFINET, GSDML et version, table de registres Modbus, fonctions d’écriture disponibles, dépendances, sauvegarde et responsable métier.

Mise en service PROFINET : confirmer modèle et GSDML, configurer les modules et le temps de cycle adapté, définir un nom unique, vérifier les paramètres réseau, valider diagnostics et topologie, puis tester les E/S en environnement contrôlé avant toute exploitation.

Lecture Modbus : identifier le serveur réel, le port et les fonctions prises en charge ; confirmer l’offset, la quantité, l’échelle et l’encodage ; tester en lecture seule sur simulateur ; comparer à la source de référence ; documenter les délais et la réaction en cas de perte de communication.

Sécurité : segmenter supervision et contrôle, limiter les flux par liste d’autorisation et tenir les accès d’ingénierie fermés hors intervention. Diagnostic : vérifier d’abord la couche physique, ensuite la connectivité IP et les règles de flux, puis le protocole et enfin la signification des données. Ne jamais écrire sur des sorties ou consignes dans le cadre de ce scénario sans procédure formelle.

## 14. Glossaire

- **API/PLC :** automate programmable industriel.
- **ADU :** unité complète de données du protocole transporté ; Modbus TCP comprend l’en-tête MBAP et la PDU.
- **Coil :** donnée binaire Modbus généralement lisible et écrivable selon l’implémentation.
- **DCP :** mécanisme PROFINET de découverte et de configuration de base au niveau Ethernet.
- **GSDML :** fichier XML décrivant les caractéristiques d’un périphérique PROFINET.
- **Holding Register :** registre Modbus de 16 bits souvent accessible en lecture et écriture selon la fonction autorisée.
- **IHM/HMI :** interface homme-machine.
- **IO Controller :** composant qui contrôle les échanges cycliques d’E/S PROFINET.
- **IO Device :** périphérique d’E/S ou équipement de terrain intégré à une relation PROFINET.
- **IRT :** communication PROFINET isochrone temps réel.
- **MBAP :** en-tête Modbus Application Protocol utilisé notamment par Modbus TCP.
- **Modbus RTU :** mode Modbus série utilisant des trames binaires et un CRC.
- **Modbus TCP :** Modbus transporté par TCP/IP, habituellement sur le port TCP 502.
- **MRP :** protocole de redondance de média pour certaines topologies en anneau compatibles.
- **PDU :** unité de données protocolaire, ici code de fonction Modbus et données.
- **PROFINET RT :** communication PROFINET temps réel.
- **SCADA :** système de supervision, de contrôle et d’acquisition de données.
- **Gigue :** variation du délai de livraison des paquets ou données.

## 15. Références techniques et approfondissement

1. Modbus Organization, **Specifications and Implementation Guides** : https://www.modbus.org/modbus-specifications
2. Modbus Organization, **An Introduction to Modbus** : https://www.modbus.org/introduction-to-modbus
3. Modbus Organization, **Modbus Application Protocol Specification V1.1b3** : https://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
4. PROFIBUS & PROFINET International, **Specifications & Standards / PI Downloads** : https://www.profibus.com/download/specifications-standards
5. PROFIBUS & PROFINET International, **PROFINET Security Guideline** : https://www.profibus.com/download/profinet-security-guideline
6. CISA, **ICS Recommended Practices** : https://www.cisa.gov/resources-tools/resources/ics-recommended-practices

Les spécifications officielles et les manuels des fabricants priment toujours sur les exemples de ce cours. Les capacités, menus d’ingénierie et fonctions prises en charge varient selon les modèles, les versions logicielles et les licences.
