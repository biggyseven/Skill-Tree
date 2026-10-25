# Protocoles industriels : Modbus et PROFINET — Niveau intermédiaire

## Mise en contexte : passer de la lecture du protocole à la conception d’un réseau fiable

Au niveau débutant, tu as identifié les composants d’une cellule industrielle, reconnu les rôles Modbus et PROFINET, et lu quelques échanges simples. Le niveau intermédiaire prend le point de vue de la personne qui doit intégrer des équipements hétérogènes, documenter les données, mettre en service une cellule, diagnostiquer des défauts intermittents et limiter les risques sans interrompre la production.

Le défi n’est pas uniquement de « faire communiquer » deux appareils. Une intégration réussie doit garantir que les données sont correctes, à jour, interprétées dans les bonnes unités, livrées dans un délai approprié et contrôlées par des flux réseau prévisibles. Une valeur erronée peut être plus dangereuse qu’une communication totalement interrompue, car elle peut paraître crédible à l’opérateur ou au programme automate.

> **Encadré de mise en contexte.** Aucun protocole ne garantit, à lui seul, la sécurité du procédé. La fiabilité dépend du matériel, du câblage, de l’architecture, des paramètres, de la logique de commande, des délais, des alarmes, de la conception des fonctions de sécurité et des procédures d’exploitation. Les essais de ce cours se déroulent en simulation ou sur un banc autorisé, jamais par exploration spontanée d’un réseau OT de production.

## Objectifs pédagogiques

À l’issue de cette formation, tu devras être capable de :

- analyser l’architecture et les dépendances d’une intégration Modbus/PROFINET ;
- décoder les champs principaux d’une transaction Modbus TCP et comprendre le format d’une trame RTU ;
- résoudre les erreurs d’offset, de fonction, de quantité, d’échelle, de signe et d’ordre des mots ;
- expliquer la différence entre un défaut de transport, une exception applicative et une donnée incohérente ;
- estimer l’effet du polling, des délais et du nombre d’équipements sur la charge d’un client Modbus ;
- préparer une intégration d’E/S PROFINET à partir d’un GSDML et d’un projet d’ingénierie ;
- distinguer données cycliques, paramètres acycliques, diagnostics et découverte de topologie ;
- construire une matrice de flux et un plan de diagnostic reproductible ;
- recommander des mesures de défense adaptées à des équipements anciens et récents.

## 1. Modbus en profondeur : du registre à la donnée d’ingénierie

### 1.1 Une table de registres est un contrat d’intégration

La carte Modbus fournie par le constructeur représente le contrat entre le système qui demande les données et le dispositif qui y répond. Il ne suffit pas de connaître « le registre 12 ». Il faut savoir quelle famille de données est utilisée, si l’adresse est un offset ou une référence documentaire, si l’accès est en lecture ou en écriture, combien de mots sont nécessaires, quelle unité représente la valeur, comment le signe est encodé et quelle valeur indique un défaut ou une donnée invalide.

Une fiche de données devrait contenir au minimum :

| Champ | Question à résoudre |
|---|---|
| Équipement et révision | Quelle documentation correspond exactement au modèle installé ? |
| Réseau | Adresse IP ou identifiant série, port, unité/gateway et paramètres de ligne |
| Fonction Modbus | Quel code de fonction est pris en charge ? |
| Famille et adresse | Coil, Discrete Input, Input Register ou Holding Register ? Offset ou notation de référence ? |
| Taille | Combien de bits ou de registres composent la donnée ? |
| Type numérique | Entier non signé, entier signé, valeur 32 bits, flottant, bitfield ? |
| Ordre des octets/mots | Quelle convention d’encodage le fabricant définit-il ? |
| Échelle et unité | Facteur, offset et unité physique ? |
| Qualité/validité | Existe-t-il un bit d’état, un code défaut ou un indicateur de donnée périmée ? |
| Accès autorisé | Lecture seule, écriture contrôlée, accès protégé ou interdit ? |
| Temporalité | Quelle fréquence de lecture est réellement nécessaire ? |

Sans ces informations, l’intégration repose sur des suppositions. Une valeur qui « ressemble à quelque chose » ne constitue pas une validation.

### 1.2 Cartographie des adresses et pièges d’offset

Les tables utilisent souvent la convention traditionnelle de références `00001`, `10001`, `30001` et `40001` pour différencier les familles de données. Ces préfixes ne sont pas nécessairement transmis dans la PDU. Les requêtes contiennent un code de fonction et un champ d’adresse sur 16 bits. Pour certaines API, l’adresse `40001` dans la documentation correspond à l’offset `0` dans la requête de lecture des Holding Registers ; d’autres bibliothèques exposent un modèle différent.

**Procédure à respecter :**

1. Copier littéralement la table officielle du modèle installé.
2. Identifier l’outil ou la bibliothèque et vérifier s’il attend un offset à base zéro ou une référence documentaire.
3. Utiliser une variable de test non critique sur un simulateur.
4. Lire un point de référence connu, puis confirmer la correspondance avec le logiciel d’ingénierie.
5. Faire relire et valider le mapping par une seconde personne avant l’intégration.
6. Enregistrer la convention retenue dans le dossier d’exploitation.

```text
Table constructeur                       Requête Modbus (exemple)
Holding Register 40001  ───────────────► offset 0, fonction 03
Holding Register 40002  ───────────────► offset 1, fonction 03
Input Register 30001    ───────────────► offset 0, fonction 04

Le numéro de référence et l’offset transporté ne sont pas synonymes.
La correspondance ci-dessus est illustrative : le manuel et l’API décident.
```

### 1.3 Taille des valeurs et représentation numérique

Un registre Modbus transporte 16 bits. Pour une valeur multi-registres, le dispositif doit définir comment les mots se combinent. Deux appareils peuvent transmettre chacun deux registres mais utiliser un ordre des mots différent. Les termes courants « ABCD », « CDAB », « BADC » ou « DCBA » décrivent certains agencements d’octets/mots, mais les conventions de nommage varient selon les outils.

Exemple : une valeur entière non signée de 32 bits `100000` est stockée dans deux mots. Si le client inverse les mots, il combine les bits dans un ordre incorrect et affiche un nombre très grand ou très petit. Pour un flottant IEEE 754, une inversion peut produire un nombre apparemment valide mais physiquement impossible.

```text
Valeur 32 bits (exemple pédagogique) : 0x0001 0x86A0
                mot haut   mot bas

Ordre attendu : [0x0001] [0x86A0]
Ordre inversé : [0x86A0] [0x0001]

Même séquence de deux registres, interprétation différente si le client
reconstruit la valeur avec le mauvais ordre de mots.
```

Autres points importants :

- **Signe :** la suite binaire `0xFFFF` vaut 65535 en non signé, mais -1 en entier signé sur 16 bits.
- **Échelle :** 253 peut signifier 25,3 °C, 253 kPa ou une valeur sans unité selon le contrat de données.
- **Offset :** certaines variables utilisent une formule `valeur_physique = brut × facteur + offset`.
- **Bits d’état :** un mot peut contenir plusieurs drapeaux qui exigent un masque binaire, non une conversion décimale naïve.
- **Valeur périmée :** le dernier nombre reçu peut rester affiché même après la perte de communication ; la qualité et l’horodatage doivent aussi être évalués.

### 1.4 Codes de fonction et exceptions

Les codes de fonction déterminent le type d’opération. Les fonctions 01 à 04 servent aux lectures les plus courantes ; 05, 06, 15/`0x0F` et 16/`0x10` couvrent des écritures individuelles ou multiples. Les implémentations ne supportent pas nécessairement toutes les fonctions. Une exception est un retour applicatif structuré, différent d’une absence totale de réponse.

| Situation | Signification possible | Ce qu’il faut vérifier |
|---|---|---|
| Fonction non prise en charge | Code non implémenté par l’appareil | Manuel, famille d’objet et modèle exact |
| Adresse non valide | L’offset ou l’étendue dépasse la carte | Base d’adressage, famille, nombre de registres |
| Valeur invalide | Paramètre refusé par la logique de l’appareil | Plage autorisée, état opérationnel, droits |
| Délai dépassé | Aucune réponse dans le temps attendu | Transport, charge, serveur, route, timeout |
| Réponse tronquée ou mal formée | Défaut d’implémentation, équipement ou intermédiaire | Capture autorisée, firmware, passerelle et client |
| Valeur incohérente sans erreur | Mapping, signe, échelle, ordre des mots ou qualité | Contrat de données et référence de terrain |

Une réponse d’exception n’indique pas forcément un défaut réseau ; elle peut signifier que la requête est arrivée jusqu’à l’application, qui l’a rejetée. À l’inverse, une absence de réponse peut résulter d’un filtrage réseau, d’une connexion défaillante, d’un serveur occupé ou de paramètres de délai trop stricts.

### 1.5 Structure d’une trame Modbus TCP

Une ADU Modbus TCP contient l’en-tête MBAP de 7 octets et la PDU. Le champ Transaction ID aide le client à associer la réponse à la requête correspondante. Protocol ID est zéro dans le profil usuel. Length indique la longueur restante associée au champ Unit ID et à la PDU. Le code de fonction et les données suivent.

```text
Offset octets (indicatif)
0–1     Transaction Identifier
2–3     Protocol Identifier (0 pour Modbus TCP usuel)
4–5     Length
6       Unit Identifier
7       Function Code
8…      Data (adresse, quantité, valeur, etc.)

┌──────────────────────────── MBAP ────────────────────────────┐
│ Transaction ID │ Protocol ID │ Length │ Unit ID              │
└───────────────────────────────────────────────────────────────┘
┌──────────────────────── PDU Modbus ──────────────────────────┐
│ Function Code │ Data                                         │
└───────────────────────────────────────────────────────────────┘
```

Modbus RTU a une structure différente : adresse de station, code de fonction, données et CRC16. Il ne faut pas interpréter l’ADU TCP comme une simple trame RTU placée dans TCP. Une passerelle peut devoir convertir la transaction, traiter l’identifiant d’unité et gérer les contraintes de la liaison série.

### 1.6 Modbus RTU sur RS-485 : ce que le protocole applicatif ne remplace pas

Le protocole ne corrige pas un mauvais câblage. Les réseaux RS-485 exigent de respecter la topologie et les recommandations du fabricant : câble adapté, polarité cohérente, limitation des dérivations, terminaison aux extrémités électriques requises, référence de potentiel selon les règles du constructeur, blindage et mise à la terre conformément à la conception du site. Le débit, la parité et le nombre de bits d’arrêt doivent correspondre sur tous les appareils.

```text
[Maître / client série]───[Esclave 1]───[Esclave 2]───[Esclave 3]
      termin.                                     termin.

Schéma de principe d’une ligne ; les résistances de terminaison se placent
selon les caractéristiques de la ligne et les recommandations fabricant.
Éviter de traiter une ligne RS-485 comme un bus Ethernet en étoile.
```

Diagnostic de base : vérifier les paramètres de série, le numéro de station, la continuité, la polarité, la terminaison et les compteurs d’erreurs. Ne pas modifier un bus actif à l’aveugle ; une intervention physique doit être planifiée et isolée selon la procédure de maintenance.

### 1.7 Polling, délais et charge

Dans beaucoup d’architectures Modbus, un client interroge une série de serveurs selon un calendrier. Si chaque requête attend une réponse avant de passer à la suivante, le temps nécessaire au cycle total augmente avec le nombre de requêtes, les délais, les retards des équipements et les retransmissions éventuelles.

Un modèle simplifié permet de réfléchir à la charge, sans prédire exactement les performances :

`Temps de cycle ≈ somme(des temps de réponse + délais de traitement + temps de transport) pour les requêtes séquentielles`.

Exemple : 20 lectures prennent chacune en moyenne 30 ms, hors traitement additionnel. Le temps agrégé est approximativement `20 × 30 ms = 600 ms`. Si le système doit afficher une mesure toutes les 100 ms, cette stratégie est inadéquate. Il faut revoir la fréquence requise, grouper des registres contigus lorsque c’est compatible, réduire les lectures redondantes, distribuer les tâches ou choisir une architecture appropriée.

Ne fusionne pas des registres simplement pour réduire le nombre de requêtes si la table n’autorise pas la plage, si des registres ont des effets de lecture, si les valeurs sont incohérentes dans le temps ou si la lecture d’un bloc trop large crée un risque de surcharge. La carte et la documentation du constructeur restent prioritaires.

## 2. PROFINET : engineering, E/S et diagnostic approfondis

### 2.1 Le projet d’ingénierie comme source de vérité

Une relation PROFINET correctement configurée dépend du modèle exact, des modules et sous-modules, du GSDML, du nom de station, des paramètres, des capacités réseau et des attentes du contrôleur. Le projet décrit ce que le contrôleur croit devoir trouver. Si le matériel installé diffère du projet, la relation peut être refusée ou un diagnostic de configuration peut être généré.

```text
                     Projet d’ingénierie
       ┌─────────────────────────────────────────────┐
       │ IO Controller                               │
       │   ├── Device A : module DI + module DO       │
       │   ├── Device B : variateur                  │
       │   └── paramètres/cycle/nom/topologie         │
       └──────────────────────┬──────────────────────┘
                              │ compile et charge
                              ▼
                      Réseau PROFINET
                              │
               comparaison configuration attendue/réelle
                              ▼
                   État de la relation d’E/S
```

Avant une mise en service, vérifier : référence du matériel, version du firmware, GSDML exact, ordre des modules, adresses ou identifiants, nom de station, options de synchronisation, taille des données process, valeurs de substitution et paramètres de diagnostic.

### 2.2 GSDML : usage, version et gouvernance

Le fichier GSDML aide l’outil d’ingénierie à représenter les capacités d’un IO Device. Il ne constitue ni le programme automate ni une preuve que la configuration fonctionne. Le bon fichier doit correspondre à la gamme et aux capacités du périphérique. Les versions obsolètes, un modèle proche mais différent ou une bibliothèque modifiée peuvent aboutir à des options de modules incompatibles.

Bonnes pratiques : récupérer les fichiers sur le site officiel du fabricant ; consigner la version et l’origine ; garder une copie de référence avec le projet ; valider le projet hors ligne ; conserver le rapport de compilation ; ne pas importer un fichier reçu par courriel sans contrôle ; organiser la gestion de versions des projets d’ingénierie.

### 2.3 Données cycliques, paramètres et alarmes

Les échanges cycliques véhiculent les données process à une cadence configurée. Les services acycliques servent à consulter ou modifier des paramètres, lire des enregistrements et obtenir des diagnostics. Les alarmes et états détaillés permettent au contrôleur ou à l’outil d’ingénierie d’identifier des événements dans le périphérique.

Les temps de cycle doivent être déterminés à partir de l’application. Une machine de convoyage, une mesure lente de température et un entraînement synchronisé n’ont pas les mêmes contraintes. Les capacités du CPU, le nombre de périphériques, la taille des données, la topologie, le commutateur, la synchronisation et la charge doivent être pris en compte.

```text
                  CPU / IO Controller
              ┌────────────────────────┐
 Cycle n      │ Sorties calculées       │────► IO Device
              │ Entrées mises à jour   │◄──── IO Device
              └────────────────────────┘
                        │
                        ├── service acyclique : lecture paramètre
                        ├── alarme/diagnostic : module absent ou défaut
                        └── observation d’état : relation d’E/S
```

Une donnée process qui ne se met plus à jour ne doit pas être présentée sans indicateur de qualité ou de fraîcheur. Une application IHM/SCADA doit distinguer, lorsque les données le permettent, valeur valide, communication interrompue, valeur périmée, valeur de substitution et état de défaut. L’absence de mise à jour ne doit pas silencieusement devenir une valeur normale.

### 2.4 RT, IRT et déterminisme

PROFINET RT convient à de nombreux échanges d’E/S industriels. IRT vise des exigences de synchronisation et de déterminisme plus strictes, notamment dans certaines applications de mouvement. IRT dépend d’un ensemble compatible : contrôleur, périphérique, matériel réseau et paramètres d’ingénierie. Il ne suffit pas d’activer une case dans un projet pour créer une architecture déterministe.

Pour un projet demandant une forte synchronisation, recueillir les spécifications de temps de cycle, le temps de mise à jour requis, la tolérance de gigue, les contraintes de synchronisation, le type de trafic coexistant, les topologies supportées et les limites du matériel. Valider dans l’outil d’ingénierie et au banc selon le plan d’acceptation.

### 2.5 DCP, nom de station et IP

La découverte et la configuration PROFINET utilisent notamment des mécanismes de couche Ethernet. Le nom de station identifie logiquement le périphérique attendu dans le projet ; l’adresse IP sert à la communication IP des services qui l’utilisent. Les deux doivent être correctement définis, mais ils n’ont pas le même rôle.

Symptômes fréquents : lien actif mais périphérique non associé ; équipement visible dans l’outil mais nom incorrect ; nom dupliqué ; IP en dehors du plan ; contrôleur attendant un modèle différent ; projet et matériel qui ne correspondent pas. Une vérification doit confirmer le nom exact, la présence d’un seul équipement portant ce nom, l’adresse, le VLAN/port où le périphérique se trouve et les diagnostics du contrôleur.

### 2.6 LLDP, topologie et MRP

LLDP expose des informations de voisinage entre équipements compatibles. Les outils d’ingénierie peuvent exploiter ces informations pour aider à vérifier que les ports et les liaisons correspondent au plan. Un port mal branché, un remplacement de commutateur ou un équipement déplacé peut modifier la topologie et affecter la redondance ou le temps de convergence.

MRP permet la récupération de communication sur certains anneaux Ethernet industriels compatibles. Il faut vérifier le rôle de gestionnaire, les capacités des commutateurs et périphériques, le temps de récupération attendu et les effets des ruptures. La redondance n’est utile que si elle est conçue, configurée, testée et documentée.

## 3. Comparer les deux technologies au niveau intégration

| Dimension | Modbus RTU/TCP | PROFINET |
|---|---|---|
| Modèle de données | Table explicite d’objets et de registres | Données d’E/S associées aux modules, paramètres et diagnostics |
| Interaction | Requête/réponse | Échanges cycliques contrôlés, services acycliques et alarmes |
| Configuration principale | Adresse, fonction, offset, encodage, paramètres de transport | Projet d’ingénierie, GSDML, nom, modules, cycle et topologie |
| Diagnostic applicatif | Réponse, exception, timeout, valeurs et registres | Relation d’E/S, état de périphérique/module, alarme, qualité de données |
| Charge | Fréquence des requêtes, nombre de points, temps de réponse | Cycle d’actualisation, données process, nombre d’équipements, paramètres temps réel |
| Intégration d’un appareil tiers | Souvent réalisable à partir d’une table publiée | Dépend du GSDML, du profil et des fonctions supportées |
| Risque fréquent | Mauvais mapping, écriture non voulue ou polling excessif | Projet désynchronisé, nom incorrect, module ou temps de cycle mal défini |

Les protocoles peuvent coexister : un PLC peut échanger des E/S PROFINET avec des modules et lire des mesures Modbus sur TCP ou via une passerelle série. Cette coexistence ne signifie pas que toutes les zones réseau doivent être fusionnées.

## 4. Méthode de mise en service structurée

### 4.1 Avant le raccordement

Créer une fiche de mise en service avec : périmètre, responsable, fenêtre de travail, plan d’adressage, schéma physique, matrice de flux, versions des équipements, sauvegardes, configuration actuelle, essais prévus, critères de réussite, plan de retour arrière et personne autorisée à arrêter le procédé. Toute intervention sur une fonction de commande doit être examinée par l’exploitant et les responsables sécurité de la machine.

### 4.2 Validation par couches

```text
Étape 1 : ALIMENTATION / PHYSIQUE
  alimentation, câble, fibre, paire, vitesse/lien, blindage
                   │ OK
                   ▼
Étape 2 : LIAISON / TOPOLOGIE
  ports, VLAN, anneau, LLDP, erreurs de port, doublons
                   │ OK
                   ▼
Étape 3 : IP ET TRANSPORT (si applicable)
  IP/masque, routes, port/service, ACL, sessions et délais
                   │ OK
                   ▼
Étape 4 : PROTOCOLE ET CONFIGURATION
  Modbus : fonction, offset, registre, unit ID, timeout
  PROFINET : nom, GSDML, modules, relation d’E/S, diagnostic
                   │ OK
                   ▼
Étape 5 : SENS MÉTIER DE LA DONNÉE
  signe, échelle, unité, qualité, valeurs de référence, âge
```

Cette séquence évite de tenter de résoudre un mauvais offset quand le serveur n’est pas joignable, ou de modifier un projet PROFINET alors que le périphérique n’est pas correctement raccordé.

## 5. Laboratoire 1 — Diagnostic d’une valeur Modbus incorrecte

### Scénario

Un simulateur renvoie `0xFF9C` pour une mesure. La documentation fictive spécifie un entier signé 16 bits avec un facteur `0,1` et l’unité °C. Le logiciel affiche `6543,6 °C`.

### Travail

1. Calcule la valeur interprétée comme non signée.
2. Calcule la valeur interprétée comme signée en complément à deux.
3. Applique le facteur.
4. Explique pourquoi la valeur affichée est probablement erronée.
5. Décris les éléments à faire valider avant toute modification en production.

### Correction

`0xFF9C` vaut `65436` en non signé. Comme entier signé 16 bits en complément à deux, la valeur est `-100`. Après application du facteur `0,1`, la mesure est `-10,0 °C`. L’affichage `6543,6 °C` résulte vraisemblablement d’une interprétation non signée du mot. Il faut confirmer le type exact dans la notice, l’offset, le point de référence et la conversion dans un simulateur ou un environnement de test. Ne pas corriger la logique automate ou les paramètres d’un équipement actif sur la seule base d’une supposition.

## 6. Laboratoire 2 — Dépanner une absence de réponse Modbus TCP

### Scénario

Le poste de test est autorisé à accéder au simulateur `192.168.50.30`, mais une lecture Modbus expire. L’ICMP répond.

### Travail

Établis une séquence de diagnostic en évitant toute écriture. Distingue réseau IP, service TCP, transaction applicative et donnée.

### Correction attendue

1. Confirmer l’adresse, le masque et le chemin réseau documenté.
2. Vérifier les journaux et règles approuvées du pare-feu ou du simulateur pour TCP/502 ; le succès ICMP n’atteste pas l’ouverture du service applicatif.
3. Confirmer que le service Modbus est activé et écoute sur l’adresse/port attendus, uniquement sur le simulateur.
4. Examiner dans une capture autorisée la requête, le Transaction ID, la fonction, le Unit ID et l’existence d’une réponse.
5. Si une réponse est présente, interpréter le code de fonction et l’exception ; si elle est absente, examiner les délais, la charge, les connexions et les journaux côté serveur.
6. Ne pas réaliser de scan large ni de test de charge pour « voir si cela répond » sur un système réel.

## 7. Laboratoire 3 — Vérifier le mapping d’une table Modbus

### Scénario

Un simulateur expose : pression brute en Input Register offset 4, facteur `0,01 bar`; débit en Input Registers offsets 10–11, entier signé 32 bits, facteur `0,1 m³/h`; état alarme dans Discrete Input offset 2. Les informations sont fictives.

### Travail

Élabore une fiche de mapping et liste les incertitudes qui doivent être résolues.

### Correction proposée

| Tag SCADA | Fonction | Offset(s) | Type attendu | Conversion | Risque à vérifier |
|---|---:|---:|---|---|---|
| `P_LINE` | 04 | 4 | entier 16 bits à confirmer | brut × 0,01 bar | signe, plage, invalidité |
| `FLOW_LINE` | 04 | 10–11 | entier signé 32 bits | brut × 0,1 m³/h | ordre des mots, ordre des octets |
| `ALARM_ACTIVE` | 02 | 2 | bit | `0/1` | logique active-haut/bas, qualité |

Il faut confirmer la convention de l’offset dans la bibliothèque, la façon dont les deux mots sont combinés, la fréquence de lecture, le comportement au timeout et la valeur de qualité en cas de perte de communication. La table ne permet pas d’inférer toutes ces propriétés.

## 8. Laboratoire 4 — Diagnostic d’un périphérique PROFINET

### Scénario

Un îlot d’E/S a un lien Ethernet actif. L’outil d’ingénierie voit un périphérique, mais le contrôleur signale une différence de configuration.

### Travail

Propose un ordre de vérification et précise les preuves à collecter.

### Correction proposée

1. Relever le code et le texte exact du diagnostic côté contrôleur et périphérique.
2. Confirmer le modèle, la révision et le firmware ; comparer au matériel déclaré dans le projet.
3. Vérifier le GSDML utilisé, les modules et sous-modules, leur ordre et les tailles d’E/S.
4. Vérifier le nom PROFINET, son unicité, l’adresse IP si applicable et l’emplacement réseau.
5. Examiner le port du commutateur, le câblage, le VLAN, les informations LLDP et le chemin de la topologie.
6. Comparer le projet téléchargé à la version de référence, en respectant la procédure de gestion de changement.
7. Sauvegarder le diagnostic et les changements ; ne pas remplacer ou redémarrer des composants en production sans évaluation des conséquences.

Preuves : capture d’écran ou export de diagnostic, version projet, GSDML, identifiant matériel, nom de station, adresses, schéma de ports et horodatage.

## 9. Laboratoire 5 — Calcul simple de polling

### Scénario

Un client interroge 12 équipements en série. Le temps moyen requête-réponse prévu est de 25 ms par équipement. On ajoute 5 ms de traitement dans le client par équipement.

### Travail

Calcule le temps de cycle approximatif et explique si une actualisation toutes les 100 ms est réaliste.

### Correction

Temps par équipement simplifié : `25 ms + 5 ms = 30 ms`. Pour 12 équipements, le cycle agrégé estimé est `12 × 30 = 360 ms`, hors variations, retransmissions et autres traitements. Une actualisation garantie toutes les 100 ms ne peut donc pas être assurée par cette stratégie séquentielle selon les hypothèses du problème. Il faut réviser les exigences, réduire ou regrouper les lectures lorsque c’est permis, optimiser l’architecture ou sélectionner un mécanisme de communication adapté. Ce calcul est un modèle de réflexion, pas une garantie de performance réelle.

## 10. Conception réseau et sécurité

### 10.1 Segmentation et matrice de flux

Une zone OT doit être définie par les besoins du procédé et les risques, non uniquement par la facilité de câblage. Les flux entre SCADA, PLC, passerelles, stations d’ingénierie et équipements doivent être documentés. Par défaut, les flux non nécessaires ne sont pas ouverts.

```text
ZONE SUPERVISION                 ZONE CELLULE
┌──────────────────┐            ┌─────────────────────┐
│ SCADA / historian│──flux prévus│ PLC / contrôleurs   │
└──────────────────┘            │ PROFINET IO         │
            │                   │ passerelle Modbus   │
            │                   └─────────────────────┘
     [Pare-feu industriel]
            │
ZONE ENTREPRISE / ACCÈS DISTANT — aucune route implicite vers les PLC
```

Une matrice minimale consigne source, destination, service/protocole, direction, justification, propriétaire, durée, méthode de journalisation et méthode de vérification. Un port TCP/502 autorisé entre deux sous-réseaux ne signifie pas que les opérations d’écriture sont sûres ; il faut également tenir compte des fonctions applicatives, du rôle de l’utilisateur et de la conception du système.

### 10.2 Modbus Security et sécurité PROFINET

La spécification Modbus Security associe TLS au protocole traditionnel et utilise des certificats X.509 pour l’authentification du client et du serveur ; l’organisation Modbus décrit le port 802 pour cette variante. La présence de cette spécification ne garantit pas que les équipements installés la supportent.

Pour PROFINET, les fonctions et options de sécurité varient selon les éditions, les classes, le matériel et les mises en œuvre. Vérifier la documentation de chaque appareil et l’architecture complète. Aucun protocole de terrain ne dispense des contrôles d’accès, de la segmentation, du suivi des configurations, des sauvegardes et de la surveillance.

Mesures prioritaires :

- inventaire versionné des équipements, services et connexions ;
- accès d’ingénierie temporaires et authentifiés ;
- filtrage des flux selon le besoin documenté ;
- observation passive et journaux centralisés quand cela est compatible ;
- contrôle de changement avant modification d’une table de registres ou d’un projet ;
- sauvegarde testée du programme PLC, du projet d’ingénierie et des paramètres ;
- validation préalable des mises à jour et des nouveaux composants ;
- procédure de secours expliquant le comportement attendu à la perte de communication.

## 11. Arbre de diagnostic réutilisable

```text
PROBLÈME OBSERVÉ
      │
      ├─ Pas de lien ? ─► alimentation, câble, fibre, port, erreurs physiques
      │
      └─ Lien présent
             │
             ├─ IP/TCP indisponible (si utilisé) ?
             │      └─► adressage, VLAN, route, ACL, port/service
             │
             └─ Transport disponible
                    │
                    ├─ Modbus : aucune réponse ?
                    │      └─► service, timeout, transaction, charge, passerelle
                    │
                    ├─ Modbus : exception ?
                    │      └─► fonction, offset, quantité, plage/paramètre
                    │
                    ├─ PROFINET : relation d’E/S absente ?
                    │      └─► nom, projet/GSDML, modules, état du contrôleur
                    │
                    └─ Communication active mais valeur fausse ?
                           └─► type, signe, ordre mots, échelle, unité, qualité
```

La démarche doit être reproductible : noter l’heure, la version, le point exact, la valeur attendue et observée, les hypothèses, les contrôles réalisés et le résultat. Cette discipline permet de distinguer les faits des suppositions et de transmettre le diagnostic à un collègue sans perdre l’historique.

## 12. Exercices corrigés

### Exercice 1 — Interprétation d’un registre signé

Une valeur `0xFF38` est interprétée comme entier signé 16 bits. Sa mise à l’échelle est `brut × 0,01`. Quelle valeur obtient-on ?

**Correction :** `0xFF38` vaut 65336 en non signé. En signé 16 bits, on soustrait 65536 : `65336 − 65536 = −200`. Après mise à l’échelle, la valeur vaut `−2,00` dans l’unité documentée.

### Exercice 2 — Transport ouvert, application en échec

Le poste atteint l’adresse IP du serveur et établit TCP/502, mais le serveur retourne une exception de fonction.

**Correction :** la connectivité IP/TCP fonctionne suffisamment pour la transaction. Il faut examiner la fonction demandée, la capacité du serveur, la table de données et le code d’exception. Il serait inapproprié de commencer par modifier le VLAN ou le routage sans autre indice.

### Exercice 3 — Donnée 32 bits incohérente

Deux registres sont lus sans erreur ; leur interprétation dépasse de plusieurs ordres de grandeur la plage physique.

**Correction :** vérifier l’ordre des mots et des octets, le type (signé, non signé ou flottant), l’offset, le facteur et l’unité. Une réponse protocolée valide n’implique pas une interprétation métier correcte.

### Exercice 4 — Pourquoi éviter un polling trop fréquent ?

**Correction :** cela peut accroître la charge des appareils, créer des files d’attente et des délais, rendre les valeurs plus anciennes en pratique et perturber d’autres opérations. La fréquence doit répondre au besoin réel du procédé et aux limites de l’équipement.

### Exercice 5 — GSDML différent du matériel

Un projet utilise un fichier de description d’une variante proche du périphérique réellement installé.

**Correction :** identifier le modèle et la révision exacts, récupérer le GSDML officiel correspondant, comparer les modules/sous-modules et mettre à jour le projet sous contrôle de changement. Ne pas télécharger un projet en production avant validation.

### Exercice 6 — Nom PROFINET dupliqué

Deux équipements partagent le même nom de station.

**Correction :** la configuration logique devient ambiguë. Identifier les deux périphériques par la méthode de découverte autorisée, confirmer le plan de noms, attribuer des noms uniques conformément au processus de mise en service et vérifier le retour à un état de communication correct.

### Exercice 7 — Capture sans paquet Modbus

Une capture réalisée sur un port access ordinaire ne montre pas de trafic Modbus échangé entre deux autres ports.

**Correction :** un commutateur ne copie pas nécessairement le trafic unicast des autres ports vers le poste de capture. Utiliser un port miroir ou un TAP configuré et autorisé, sans changer la topologie de production de façon improvisée.

### Exercice 8 — Ring MRP et panne d’un lien

Après une rupture d’anneau, une partie des données s’interrompt plus longtemps que prévu.

**Correction :** vérifier la conception de l’anneau, la configuration du rôle gestionnaire, la compatibilité des équipements, le temps de récupération spécifié, la topologie réelle, l’état des ports et les événements d’alarme. Ne pas supposer que la seule présence d’un anneau garantit une récupération conforme.

### Exercice 9 — Supervision et écritures

Le SCADA n’a besoin que d’afficher des mesures mais le pare-feu permet un accès large de la supervision au PLC et à la passerelle.

**Correction :** revoir l’analyse de besoin, séparer les flux, restreindre origines/destinations/services, vérifier si l’architecture applicative permet de limiter les fonctions d’écriture et tester le comportement sans production. Le filtrage réseau est une couche de défense ; il ne remplace pas le contrôle métier.

### Exercice 10 — Valeur figée après perte de liaison

L’IHM continue à afficher `74,2` après une coupure de communication.

**Correction :** vérifier si le logiciel conserve la dernière valeur ; afficher un état de qualité et l’âge de la mesure ; définir un comportement explicite en cas de perte de données ; vérifier que les décisions critiques ne s’appuient pas aveuglément sur une valeur périmée.

## 13. Défi final corrigé — Intégrer un compteur Modbus et un îlot PROFINET

### Situation

Une machine fictive utilise un PLC avec des E/S PROFINET. Un compteur d’énergie communique en Modbus TCP. Les mesures doivent être historisées. L’ingénierie doit diagnostiquer les périphériques sans exposer les PLC au réseau bureautique. Une valeur de courant semble parfois dix fois trop grande.

### Livrables attendus

1. Schéma d’architecture logique et physique.
2. Fiche de mapping du compteur.
3. Plan de mise en service PROFINET.
4. Hypothèses et vérifications pour la mesure de courant.
5. Matrice de flux et procédure de diagnostic.

### Correction proposée

```text
               Zone supervision / historisation
         ┌─────────────────────────────────────┐
         │ SCADA / historien                   │
         └──────────────────┬──────────────────┘
                            │ flux limités à la collecte requise
                     [Pare-feu / L3]
                            │
         ┌──────────────────┴─────────────────────────┐
         │ Zone cellule                               │
         │ PLC ───── PROFINET ───── IO Device          │
         │  │                                         │
         │  └──────── Modbus TCP ───── Compteur        │
         │                                             │
         │ Accès d’ingénierie : poste approuvé,       │
         │ authentifié, limité dans le temps           │
         └─────────────────────────────────────────────┘
```

Pour la valeur de courant : comparer la table officielle au mapping ; vérifier si le facteur est `/10`, `/100` ou un autre facteur ; examiner l’unité et l’offset ; confirmer le type numérique, le signe et l’ordre des mots ; comparer à un instrument de référence ; tester sur un simulateur avec valeur connue ; ne corriger qu’après revue et validation. L’erreur d’un facteur dix suggère une échelle ou une unité incorrecte, mais le diagnostic doit le démontrer.

Pour PROFINET : faire correspondre le matériel et le GSDML, vérifier modules et tailles d’E/S, nom de station et topologie, cycle et diagnostics, puis effectuer les essais d’E/S dans le cadre accepté. Pour la sécurité : autoriser seulement les flux collectés, limiter le poste d’ingénierie, journaliser les changements, sauvegarder le projet et préparer le retour arrière. Pour le diagnostic : séparer les couches physique, réseau, transport, protocole, configuration et sémantique.

## 14. Glossaire

- **ADU :** unité de données transportée par un protocole ; l’ADU Modbus TCP contient MBAP et PDU.
- **Acyclique :** échange déclenché à la demande, par exemple lecture de paramètre ou diagnostic.
- **Base zéro :** convention d’adresse commençant à l’offset 0.
- **CRC16 :** contrôle d’intégrité de trame utilisé par Modbus RTU.
- **DCP :** mécanisme PROFINET de découverte/configuration de base.
- **GSDML :** description XML d’un périphérique PROFINET.
- **Holding Register :** registre Modbus de 16 bits ; l’écriture dépend du modèle et des droits.
- **IRT :** mode PROFINET isochrone temps réel.
- **LLDP :** protocole de découverte des voisins réseau, utilisé par les équipements compatibles.
- **MBAP :** en-tête Modbus TCP.
- **MRP :** mécanisme de redondance de média en anneau pour équipements compatibles.
- **Offset :** position réelle utilisée dans une requête ou une API, à distinguer d’une référence documentaire.
- **PDU :** code de fonction et données Modbus.
- **Polling :** lecture périodique des données par requêtes successives.
- **PROFINET RT :** communication PROFINET temps réel.
- **Qualité de donnée :** indicateur permettant de distinguer valeur valide, défaut ou valeur périmée.
- **Signe/encodage :** règle permettant d’interpréter les bits comme un type numérique.

## 15. Références techniques

1. Modbus Organization — Spécifications et guides : https://www.modbus.org/modbus-specifications
2. Modbus Application Protocol Specification V1.1b3 : https://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
3. Modbus Organization — Introduction : https://www.modbus.org/introduction-to-modbus
4. PROFIBUS & PROFINET International — Spécifications et standards : https://www.profibus.com/download/specifications-standards
5. PROFIBUS & PROFINET International — PROFINET Security Guideline : https://www.profibus.com/download/profinet-security-guideline
6. CISA — ICS Recommended Practices : https://www.cisa.gov/resources-tools/resources/ics-recommended-practices

Les détails d’implémentation changent selon les fabricants et les versions. Les exemples d’adresses et de valeurs de ce cours sont fictifs. La documentation spécifique du modèle, les exigences du procédé et les procédures du site priment toujours.
