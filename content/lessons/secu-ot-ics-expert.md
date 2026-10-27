# Architecture de sécurité sur les réseaux OT/ICS

> **Mise en contexte**

Un système industriel ne se comporte pas comme un serveur bureautique. Un serveur informatique peut souvent être redémarré pendant une fenêtre de maintenance ; un automate de procédé peut piloter une pompe, une ligne de production, une station de traitement d’eau, une sous-station électrique ou un dispositif de transport. Une modification de configuration, une interruption réseau ou un faux ordre de commande peut affecter la disponibilité du procédé, la qualité du produit, l’environnement ou la sécurité des personnes. Protéger un environnement OT/ICS signifie donc réduire le risque cyber sans dégrader la sûreté, la stabilité, la capacité de supervision ou les délais de réponse attendus par les équipements.

L’OT (Operational Technology, technologie opérationnelle) désigne les systèmes programmables qui surveillent ou influencent le monde physique. Les ICS (Industrial Control Systems, systèmes de contrôle industriels) en sont une famille majeure, avec notamment les systèmes SCADA, les systèmes de contrôle distribués DCS, les automates PLC, les unités distantes RTU et les interfaces opérateur HMI. Ces environnements comprennent aussi les serveurs d’historisation, postes d’ingénierie, relais de protection, équipements de terrain, réseaux de communication, dispositifs de sécurité fonctionnelle et services de maintenance.

Ce cours reprend les principes de gestion des risques, de sécurité des protocoles de routage et de sécurité de la supply chain pour concevoir une architecture défensive complète. La cible n’est pas une « usine sans réseau », mais un système où les flux sont connus, les zones ont une fonction claire, les chemins d’administration sont limités, les changements sont testés, les événements sont surveillés et le retour à un état sûr est préparé. Tous les travaux pratiques sont à effectuer dans un laboratoire isolé, sur des maquettes ou des équipements que vous êtes expressément autorisé à administrer.

## Objectifs pédagogiques

À la fin du cours, vous saurez distinguer OT, ICS, SCADA, DCS, PLC, RTU, HMI et SIS ; expliquer les contraintes de sûreté et de disponibilité ; construire un inventaire fiable ; cartographier les flux ; segmenter l’architecture en zones et conduits ; concevoir une zone démilitarisée industrielle ; réduire l’accès distant ; protéger les postes d’ingénierie et les comptes privilégiés ; planifier les mises à jour et sauvegardes ; choisir des méthodes de surveillance adaptées ; construire un plan de réponse à incident qui implique les exploitants ; et démontrer la qualité des contrôles par des tests et des preuves.

Le principe directeur est que la cybersécurité industrielle doit soutenir un fonctionnement sûr et maîtrisé. Avant d’appliquer une mesure sur un système réel, il faut comprendre le procédé, identifier les responsables opérationnels, évaluer les effets possibles sur les fonctions de contrôle et de protection, tester dans un environnement représentatif et suivre la procédure de gestion du changement. Un scan actif, une réinitialisation, un redémarrage ou une modification d’ACL apparemment banale peut avoir un impact sérieux si le procédé et ses dépendances ne sont pas connus.

## 1. Comprendre l’OT et les ICS

### 1.1 IT et OT : objectifs différents, même besoin de sécurité

Les environnements IT servent principalement au traitement de l’information, à la collaboration et aux services numériques. Les environnements OT observent le monde physique, commandent des équipements et contribuent à la continuité d’un procédé. La confidentialité est importante dans les deux domaines, mais l’OT donne souvent un poids particulier à la disponibilité, à l’intégrité des commandes, à la précision temporelle, à la fiabilité et à la sûreté fonctionnelle. Une panne de la supervision ou une commande erronée peut entraîner des effets physiques.

Il ne faut pas opposer ces environnements comme s’ils étaient toujours isolés. Les systèmes industriels modernes échangent des données avec la planification, la maintenance, les systèmes qualité, l’analyse de production, les fournisseurs et parfois le cloud. Les points de convergence apportent de la valeur, mais aussi des chemins d’attaque. Il faut donc définir les données réellement nécessaires, les flux autorisés et les responsabilités de bout en bout.

~~~text
IT / systèmes d'entreprise
ERP | messagerie | identité | analytique
             |
             | flux métier explicitement autorisés
             v
Zone d'échange industrielle contrôlée
passerelles | relais | dépôts de fichiers approuvés
             |
             | conduits limités et surveillés
             v
OT / contrôle de procédé
SCADA | HMI | PLC | RTU | DCS | capteurs/actionneurs
             |
             v
Procédé physique et fonctions de protection
~~~

### 1.2 SCADA, DCS, PLC, RTU et HMI

Un système SCADA (Supervisory Control and Data Acquisition) supervise des équipements souvent répartis géographiquement. Il collecte des mesures, présente les états, enregistre des événements et permet des actions de contrôle selon les autorisations. Un DCS (Distributed Control System) coordonne généralement un procédé industriel dans une installation, avec des contrôleurs, réseaux, stations opérateur et systèmes d’ingénierie distribués. Ces descriptions sont générales : l’architecture exacte varie selon l’industrie et les générations d’équipements.

Un PLC (Programmable Logic Controller, automate programmable industriel) exécute une logique de commande. Un RTU (Remote Terminal Unit, unité terminale distante) collecte et transmet des mesures ou pilote des équipements distants. Une HMI (Human-Machine Interface, interface homme-machine) permet à l’opérateur de visualiser des états et d’interagir avec le procédé. Des capteurs mesurent la température, la pression, le débit, la position ou d’autres grandeurs ; des actionneurs influencent le procédé, par exemple en commandant un moteur ou une vanne.

~~~text
Capteurs ------> PLC / RTU <------ commandes autorisées
   |                |
   | mesures        | sorties de commande
   v                v
SCADA / DCS <---- réseau de contrôle ----> HMI opérateur
   |                                      |
   v                                      v
Historisation                         opérateur autorisé
   |
   v
Rapports, maintenance et analyse approuvée
~~~

La sécurité ne repose pas uniquement sur le réseau. Les droits du poste d’ingénierie, la possibilité de modifier une logique, les supports amovibles, les comptes fournisseur, la sauvegarde de programme et les procédures d’approbation ont une influence directe sur la sûreté du système. L’architecture doit rendre ces chemins visibles et limiter qui peut les utiliser.

### 1.3 Sûreté fonctionnelle et cybersécurité

La sûreté fonctionnelle vise à réduire les risques inacceptables liés au procédé en atteignant un état sûr selon la conception de l’installation. Des systèmes instrumentés de sécurité (SIS), relais de protection, interverrouillages ou dispositifs indépendants peuvent contribuer à cette fonction. La cybersécurité cherche notamment à prévenir ou détecter les actions non autorisées susceptibles d’affecter le contrôle ou la protection. Les deux disciplines se recoupent, mais ne sont pas interchangeables.

Un contrôle de sécurité mal conçu peut compromettre la sûreté : une règle réseau trop stricte peut interrompre une communication nécessaire, un agent endpoint peut consommer des ressources, et un correctif peut changer le comportement d’un système certifié. Il faut donc faire travailler ensemble automatisme, exploitation, sécurité OT, cybersécurité IT, maintenance et responsables sûreté. Aucun administrateur réseau ne doit improviser une modification sur un procédé dont il ne connaît pas les conséquences.

~~~text
Sûreté du procédé
   |-- analyse de danger
   |-- interverrouillages / protection indépendante
   |-- procédures opérateur
   |
   +------ échange d'exigences ------+
                                     |
Cybersécurité OT                     |
   |-- identité / accès              |
   |-- segmentation / surveillance   |
   |-- intégrité des programmes      |
   |-- réponse à incident            |
                                     v
                    Etat sûr et exploitation maîtrisée
~~~

### 1.4 Les critères qui distinguent l’OT

Les contraintes fréquentes sont la durée de vie longue, la disponibilité continue, la compatibilité avec des systèmes anciens, les fenêtres de maintenance rares, les protocoles propriétaires ou historiques, la faible puissance de certains équipements, les exigences temps réel, les dépendances entre systèmes et la nécessité de préserver un état sûr. Ces facteurs ne sont pas universels, et ils ne justifient pas l’absence de sécurité ; ils indiquent comment sélectionner des mesures sûres et proportionnées.

Un équipement ancien peut ne pas supporter le chiffrement moderne ou l’authentification forte. Dans ce cas, le contrôle peut être placé autour de lui : limiter la portée réseau, isoler l’administration, filtrer les flux, surveiller les accès, empêcher les connexions directes depuis les postes utilisateurs et utiliser des passerelles adaptées. Toute compensation doit être testée, documentée et revue ; le mot « legacy » ne suffit pas comme justification permanente.

## 2. Définir le périmètre et l’inventaire

### 2.1 L’inventaire industriel

Un inventaire OT doit identifier les actifs, leur rôle, leur emplacement, leur propriétaire, leurs dépendances, leur version, les méthodes de gestion, les chemins réseau, leur statut de support et les conséquences possibles d’une indisponibilité. Il doit aussi identifier les équipements qui jouent un rôle de protection ou de sécurité fonctionnelle. Les actifs cachés dans une baie, les postes portables de maintenance, les modems, les accès fournisseurs, les équipements de test et les systèmes de reprise sont souvent des angles morts.

Les adresses IP et les noms d’hôte sont utiles, mais ne suffisent pas comme identifiants durables. Ajoutez les numéros de série, références matérielles, versions de firmware, identifiants de configuration et références d’actifs de l’organisation. Pour des équipements embarqués ou isolés, les données peuvent être collectées à partir d’une documentation de conception, d’une inspection physique et des outils natifs utilisés par un technicien autorisé. La méthode d’inventaire ne doit pas perturber le procédé.

~~~text
Pour chaque actif OT, consigner :
  ID stable / fabricant / modèle / série
  fonction dans le procédé / zone / criticité
  firmware / logiciel / date de support
  interfaces et flux attendus
  responsable opérationnel et responsable technique
  accès de maintenance / fournisseur / compte
  dépendances et fonctions de protection liées
  sauvegarde / méthode de restauration / dernière preuve
~~~

### 2.2 Découverte passive et limites des scans actifs

Dans un réseau IT classique, le scan actif est souvent un outil habituel d’inventaire. En OT, envoyer des requêtes inattendues à un contrôleur, un relais, un équipement ancien ou un appareil sensible peut provoquer des délais, un comportement inattendu ou une panne. Il faut d’abord consulter le fabricant, les responsables du procédé et les règles d’exploitation. La découverte passive à partir des communications observées, des commutateurs, des journaux, des configurations existantes et de l’inventaire technique peut être préférable dans de nombreux environnements.

La découverte passive n’est pas parfaite : elle ne voit que les actifs qui communiquent pendant la fenêtre d’observation et peut manquer les chemins rarement utilisés ou les équipements isolés. Il faut trianguler les sources et documenter les limites. Lorsqu’un scan actif est nécessaire, l’analyse de risque, le périmètre, la méthode, l’approbation et la fenêtre doivent être explicites ; une maquette ou un laboratoire peut servir à valider le comportement de l’outil avant tout essai autorisé.

### 2.3 Prioriser l’inventaire par le risque

Tous les actifs n’ont pas le même impact. Les actifs essentiels au contrôle du procédé, aux fonctions de sécurité, à la supervision opérateur, à la synchronisation, à l’alimentation ou aux communications peuvent exiger un niveau d’inventaire et de contrôle supérieur. Il faut considérer les effets en cascade, pas seulement la valeur commerciale de l’appareil. Un commutateur qui relie plusieurs contrôleurs ou une station d’ingénierie qui peut modifier plusieurs automates peut représenter un point de concentration du risque.

~~~text
Actif découvert
      |
      v
Fonction et propriétaire identifiés ?
      |
      +-- non --> isoler l'incertitude / investiguer avec l'exploitant
      |
      +-- oui
           |
           v
Effet potentiel sur procédé et sûreté
           |
           v
Chemins de commande / accès / dépendances
           |
           v
Priorité d'inventaire et de protection
~~~

### 2.4 Documents de référence

L’inventaire doit être relié à des documents techniques : diagrammes réseau, matrice de communication, liste des automates et programmes, architecture des postes d’ingénierie, comptes de maintenance, dépendances du système de contrôle, procédures de changement, sauvegardes et plans de continuité. Le diagramme doit distinguer ce qui est approuvé de ce qui a été observé. Les écarts entre architecture de référence et réseau réel sont eux-mêmes des résultats de sécurité.

Les documents doivent être contrôlés comme des actifs sensibles. Des schémas détaillés peuvent révéler les équipements prioritaires ou les chemins d’accès. Conservez les versions, propriétaires, dates de validation et niveaux d’accès. Un diagramme ancien qui continue d’être utilisé comme vérité peut être plus dangereux que l’absence de diagramme, car il encourage une décision fondée sur de faux prémisses.

## 3. Architecture par niveaux, zones et conduits

### 3.1 Niveaux fonctionnels : repères, pas loi universelle

Une architecture souvent présentée par niveaux décrit le procédé et les équipements de terrain en bas, le contrôle local au-dessus, la supervision ensuite, puis les services d’exploitation et d’entreprise. Ce repère fonctionnel aide à raisonner sur les flux, mais les installations réelles sont parfois plus distribuées, redondantes ou spécialisées. Il ne faut pas attribuer une sécurité garantie à un niveau simplement parce qu’il se trouve au « niveau 3 » ou au « niveau 4 ».

Les principales questions sont : quel système doit parler à quel autre, pour quelle raison, dans quelle direction, avec quelle identité, à quelle fréquence et avec quelle conséquence en cas de perte ? Chaque connexion est un conduit potentiel de propagation. Les communications vers l’IT doivent être limitées à la nécessité opérationnelle et traverser les frontières de sécurité définies.

~~~text
Niveau entreprise / IT
Services métiers, identité, analyse
             |
             v
Frontière IT/OT et zone d'échange industrielle
relais contrôlés, transferts approuvés, bastion
             |
             v
Supervision et opérations industrielles
SCADA / historien / serveurs d'application
             |
             v
Contrôle local
PLC / RTU / DCS / stations d'ingénierie
             |
             v
Processus / capteurs / actionneurs
             |
             v
Fonctions de protection et état physique
~~~

La séparation des fonctions compte davantage que les étiquettes du dessin. Si un serveur historique doit transmettre des données au système d’entreprise, privilégiez un flux défini plutôt qu’une connexion générale entre les réseaux. Si un serveur d’ingénierie doit télécharger un programme, ce privilège ne doit pas être accordé au même réseau qu’un ordinateur bureautique ordinaire sans contrôles renforcés.

### 3.2 Modèle de zones et conduits IEC 62443

Le modèle de zones et conduits de la série IEC 62443 permet de regrouper les actifs qui partagent des exigences de sécurité et de définir les communications contrôlées entre groupes. Une zone peut être, par exemple, la supervision, l’ingénierie, les contrôleurs d’une cellule, les équipements de protection ou les services d’échange. Un conduit regroupe les communications entre zones et définit les exigences associées. La segmentation doit être basée sur le risque et la fonction du procédé, non uniquement sur le sous-réseau IP.

Pour chaque zone, documentez les actifs, les fonctions, les conséquences de compromission, les exigences de disponibilité et d’accès, les données qui circulent et la stratégie de surveillance. Pour chaque conduit, décrivez source, destination, sens, protocole, port si applicable, propriétaire, justification, méthode de protection et comportement attendu en cas de panne. Une règle large « OT vers IT autorisé » est rarement une politique suffisamment précise.

~~~text
+-------------------+     conduit     +-------------------+
| Zone supervision  | <-------------->| Zone historien    |
| HMI / SCADA       |                 | collecte / relais |
+-------------------+                 +-------------------+
          |
          | conduit limité et autorisé
          v
+-------------------+     conduit     +-------------------+
| Zone ingénierie   | --------------> | Zone contrôleurs  |
| poste maîtrisé    |   changement    | PLC / RTU         |
+-------------------+   approuvé      +-------------------+

Aucune connexion directe non justifiée depuis IT utilisateur
~~~

### 3.3 Zone démilitarisée industrielle (IDMZ)

Une IDMZ (Industrial Demilitarized Zone) crée une zone intermédiaire entre les réseaux d’entreprise et les réseaux de contrôle. Elle peut héberger des relais d’accès distant, des passerelles, des serveurs de transfert, des proxies, des services de mise à jour inspectés ou des copies d’historisation. L’objectif est d’éviter que les postes de l’entreprise se connectent directement aux contrôleurs et aux systèmes critiques.

Une IDMZ n’est pas un espace fiable par défaut : c’est une frontière conçue et surveillée. Les systèmes qui s’y trouvent doivent être durcis, maintenus, segmentés et dotés de journaux. Une machine compromise dans la zone intermédiaire ne doit pas pouvoir se connecter librement à tous les réseaux OT. Les flux doivent être explicitement autorisés, et les comptes ne doivent pas être partagés à travers toutes les zones.

~~~text
Réseau IT
    |
[pare-feu IT/DMZ]
    |
+----------------------------------+
| IDMZ industrielle                |
| bastion | transfert | relais      |
| mise à jour inspectée | journal   |
+----------------------------------+
    |
[pare-feu OT / règles minimales]
    |
Réseau de supervision
    |
Réseau de contrôle et équipements
~~~

### 3.4 Limiter les flux et les protocoles

Les communications doivent suivre le besoin du procédé. Une matrice de flux décrit les communications nécessaires avant la création des règles. Évitez les règles qui autorisent une plage entière d’adresses vers tout le réseau industriel simplement parce qu’un fournisseur demande un accès. Précisez les systèmes sources, destinations, protocoles, directions, fenêtres, comptes, validation et propriétaire.

Les protocoles industriels peuvent être anciens et ne pas offrir d’authentification ou de chiffrement robustes. Une frontière réseau ne transforme pas ces protocoles en mécanismes sûrs ; elle réduit les personnes et systèmes capables d’envoyer ou de recevoir les messages. Les passerelles ou proxys peuvent aider si elles comprennent le protocole et sont validés, mais elles ne doivent pas être ajoutées sans test : elles peuvent introduire latence, perte de données ou compatibilité imprévue.

### 3.5 Redondance et frontières de sécurité

La haute disponibilité OT utilise parfois des chemins réseau redondants et des contrôleurs en paire. La sécurité doit respecter les mécanismes de redondance : une règle ou un dispositif qui bloque un chemin peut mettre hors service la communication de secours ou empêcher la synchronisation. Les changements doivent être testés avec les scénarios de bascule et le retour au chemin nominal, pas seulement avec les conditions normales.

La redondance n’est pas un substitut aux contrôles : deux systèmes configurés de la même façon avec le même secret et accessibles par le même chemin peuvent être compromis ensemble. Il faut considérer les dépendances communes, les identités, l’alimentation, les commutateurs, les services de gestion et les sauvegardes. La diversité peut réduire certains risques mais augmente la complexité d’exploitation et nécessite une validation spécifique.

## 4. Accès distant et maintenance fournisseur

### 4.1 Pas de connexion fournisseur permanente par défaut

Les connexions distantes sont un chemin fréquent entre le monde extérieur et un système industriel. Elles peuvent servir au diagnostic, au support éditeur, à une mise à jour ou à l’intervention d’un intégrateur. L’architecture devrait privilégier un accès temporaire, attribué à une personne, justifié par un ticket, approuvé par un responsable OT, protégé par une authentification forte, limité à une cible et observé pendant la session.

Les accès permanents et les tunnels toujours actifs accroissent le rayon d’impact d’une compromission du fournisseur ou de ses identifiants. Lorsqu’une connexion persistante est réellement nécessaire, justifiez-la explicitement, restreignez ses flux et son temps d’usage, surveillez-la et testez sa révocation. L’accès doit pouvoir être interrompu par une personne autorisée sans créer un risque incontrôlé pour le procédé.

~~~text
Demande de maintenance
        |
        v
Ticket / identité / cible / plage horaire
        |
        v
Approbation de l'exploitant OT
        |
        v
MFA + bastion + autorisation temporaire
        |
        v
Session enregistrée / actions observées
        |
        v
Fin de session -> révocation -> compte rendu
~~~

### 4.2 Bastion et poste intermédiaire

Un bastion (jump server) offre un point d’accès contrôlé entre un réseau d’administration et les systèmes cibles. Il doit être dédié, durci, patché selon une procédure adaptée, surveillé et limité à des usages précis. Le compte d’un fournisseur ne doit pas bénéficier d’un accès réseau général depuis le bastion ; l’autorisation doit viser une cible et des fonctions approuvées.

Un bastion compromis est un point d’appui majeur. Il faut protéger son OS, limiter les transferts de fichiers, gérer le presse-papiers et les disques partagés selon le risque, enregistrer les sessions conformément aux obligations de confidentialité et de droit du travail, surveiller les commandes privilégiées quand la plateforme le permet et conserver des journaux inaltérables. Les enregistrements doivent être accessibles uniquement aux personnes autorisées et conservés selon une politique définie.

### 4.3 Accès d'urgence et perte de connectivité

Une procédure « break-glass » doit permettre de répondre à un incident lorsque l’identité centrale ou l’accès normal est indisponible. Elle ne doit pas devenir un compte partagé permanent. Définissez qui peut autoriser l’accès, comment le secret est protégé, quelles actions doivent être journalisées, comment la session est contrôlée et comment le compte est réinitialisé après utilisation.

Le plan doit couvrir la perte du VPN, du fournisseur d’identité, d’un bastion ou du lien vers l’entreprise. L’équipe locale doit conserver les capacités nécessaires pour maintenir l’état sûr et le contrôle du procédé. Les chemins de secours doivent être testés périodiquement et protégés physiquement, car un chemin « toujours ouvert » utilisé seulement en urgence est souvent oublié.

### 4.4 Transfert de fichiers et supports amovibles

Les fichiers de projet, correctifs, configurations, scripts et programmes d’automate peuvent transporter des logiciels malveillants ou des modifications non approuvées. Les transferts doivent utiliser une zone contrôlée, une source identifiée, une vérification d’intégrité, une analyse par un outil adapté au contexte, une approbation et une traçabilité. L’analyse antivirus dans l’OT peut exiger des signatures et une méthode de déploiement testées, notamment lorsque les systèmes sont sensibles.

Les clés USB et disques amovibles doivent être soumis à une politique : supports autorisés, étiquetage, contrôle d’entrée et de sortie, poste d’inspection dédié et registre d’usage. L’interdiction totale peut être difficile à tenir dans certains sites de maintenance ; dans ce cas, définissez un processus contrôlé plutôt que de compter sur une règle théorique que les équipes contournent en silence.

## 5. Protéger les comptes, les postes d’ingénierie et les contrôleurs

### 5.1 Identités et privilèges

Les comptes doivent être individuels, attribués à une fonction, limités au besoin et révisés. Les comptes partagés rendent l’attribution des actions difficile et compliquent la révocation. Lorsque l’équipement ancien ne permet pas des identités individuelles, compensez avec un bastion, une gestion de session, une autorisation de maintenance, un registre d’accès et la rotation du secret après les interventions pertinentes.

La gestion des privilèges doit différencier opérateur, ingénieur, administrateur OT, support fournisseur et compte de service. Un compte capable de modifier une logique de contrôleur ne doit pas être utilisé pour la messagerie ou la navigation générale. Les comptes de service doivent être inventoriés, leurs secrets protégés et leurs privilèges vérifiés. Les changements de rôle ou les départs doivent déclencher une révocation rapide.

### 5.2 MFA dans les environnements industriels

L’authentification multifacteur est très utile pour les accès distants, les consoles d’administration et les systèmes modernes. Cependant, certains HMIs, contrôleurs ou équipements anciens ne peuvent pas intégrer directement MFA. Placez alors la MFA à la frontière d’administration ou au bastion, tout en maintenant un chemin local de secours sécurisé si le procédé l’exige. Il faut tester la disponibilité du mécanisme et le comportement de secours.

La MFA ne remplace pas la segmentation et l’autorisation. Un utilisateur authentifié peut encore disposer de privilèges excessifs, et un appareil compromis peut réutiliser une session active. Combinez l’identité avec la cible, le rôle, le contexte, la durée, le ticket et la journalisation. Définissez aussi les procédures en cas de téléphone perdu, d’identité compromise ou d’indisponibilité du fournisseur MFA.

### 5.3 Stations d'ingénierie

La station d’ingénierie peut charger des projets, modifier des paramètres, compiler ou télécharger des programmes. Elle constitue donc un actif hautement privilégié. Elle doit être dédiée, segmentée, contrôlée par des listes d’applications lorsque cela est supporté, maintenue avec une méthode approuvée, protégée contre l’accès non autorisé et conservée avec une configuration connue. Les outils de programmation, licences, fichiers de projet et pilotes doivent être inventoriés.

Évitez l’usage de la station d’ingénierie comme poste bureautique ou accès Internet général. Lorsque les outils nécessitent des mises à jour ou téléchargements, utilisez un flux d’acquisition approuvé et une zone d’inspection. Toute modification du projet doit être associée à une personne, un changement, une sauvegarde, un test et une approbation. Conservez le programme de référence et les empreintes ou mécanismes de comparaison disponibles.

~~~text
Station d'ingénierie dédiée
   |
   +--> comptes nominaux / privilèges temporaires
   +--> outils et versions autorisés
   +--> projet de référence protégé
   +--> transfert contrôlé des fichiers
   +--> journaux / approbation de changement
   |
   v
Accès aux contrôleurs uniquement dans le périmètre autorisé
~~~

### 5.4 Automates et contrôleurs

Un PLC/RTU ou un contrôleur de procédé doit être protégé par le réseau, les accès de programmation, l’intégrité du projet, la protection physique et les contrôles d’opération. N’exposez pas ses interfaces de gestion à des réseaux non nécessaires. Définissez comment vérifier le mode opérationnel, qui peut changer le programme, comment les modifications sont autorisées et comment la version approuvée est restaurée.

Il faut éviter les changements non planifiés sur un contrôleur réel, même à des fins de test de sécurité. Les expériences doivent se faire sur des maquettes ou en laboratoire. Les vérifications de configuration peuvent s’appuyer sur les outils et procédures du fabricant, la comparaison des projets et les journaux disponibles. Si l’équipement ne supporte pas une protection technique, réduire les voies d’accès et renforcer la surveillance autour de lui.

### 5.5 Fonctions de sécurité et indépendance

Les SIS, relais de protection et autres systèmes de sécurité fonctionnelle doivent être traités selon leur conception et leurs exigences de sûreté. Une architecture peut isoler les systèmes de protection des systèmes de contrôle et limiter les flux. Ne raccordez pas un réseau de sécurité à un réseau bureautique sans un processus d’analyse de danger, une évaluation technique et des approbations appropriées.

Un système de sécurité indépendant peut contribuer à limiter les conséquences d’une défaillance, mais il n’est pas une autorisation de négliger le contrôle. La séparation physique ou logique, les comptes, les procédures, le mode de maintenance et les essais périodiques doivent suivre la conception de sécurité. Une modification de cybersécurité qui affecte la fonction de protection doit être revue par les responsables sûreté et automatisme.

## 6. Protocoles industriels et protection des communications

### 6.1 Protocoles et limites de sécurité

Les environnements OT utilisent de nombreux protocoles, notamment Modbus, DNP3, OPC UA, Profinet, EtherNet/IP, protocoles de fabricant et mécanismes dédiés à la synchronisation ou à la protection. Les fonctionnalités de sécurité varient selon le protocole, le profil, la version et l’implémentation. Certains protocoles historiques ne disposent pas nativement d’une authentification robuste ou d’un chiffrement ; d’autres offrent des mécanismes de sécurité qui doivent être configurés et vérifiés.

Il ne faut pas supposer que la présence d’un protocole industriel est en soi une vulnérabilité. Le risque dépend des capacités, des fonctions utilisées, des chemins réseau et des personnes qui peuvent envoyer des messages. Les contrôles incluent le filtrage de flux, la limitation des sources, les architectures de passerelle, les fonctions de sécurité du protocole quand elles sont supportées, la surveillance passive et des procédures de changement adaptées.

### 6.2 Cartographie des flux connus

Créez une matrice qui décrit source, destination, protocole, port ou fonction, fréquence, raison métier, propriétaire et sens de communication. Toute connexion non justifiée doit être examinée. Les flux observés ne sont pas automatiquement légitimes : ils doivent être comparés à la documentation et validés par l’équipe de contrôle de procédé. De même, un flux non observé pendant une courte période peut rester nécessaire lors d’une phase particulière.

~~~text
Source             Destination        Usage                Décision
HMI opérateur      serveur SCADA      supervision           autorisé
SCADA              PLC ciblé          contrôle approuvé     restreint
Historien          zone d'échange     données process       flux défini
Bastion maintenance poste ingénierie  accès temporaire      ticket + MFA
IT utilisateur     PLC / RTU          aucun besoin général   refus
Fournisseur        réseau OT entier   trop large             refus / redesign
~~~

### 6.3 Passerelles et inspection de protocole

Une passerelle de protocole peut limiter les commandes, traduire des formats et créer une frontière entre zones. Mais elle doit comprendre les scénarios réels d’utilisation et ne pas bloquer une transaction nécessaire au procédé. Les fonctions d’inspection profonde peuvent dépendre des versions et des profils exacts ; elles doivent être testées sur une maquette, avec les cas normaux, les états de panne et les scénarios de reprise.

L’inspection ne doit pas introduire de latence incompatible ou devenir un point unique de défaillance sans mécanisme de continuité. Prévoyez une architecture validée par l’exploitant et une méthode de contournement approuvée en cas de panne du dispositif, si ce contournement ne crée pas un risque plus élevé. Le contournement ne doit pas être une règle permanente inconnue de l’équipe de sécurité.

### 6.4 Chiffrement et authenticité

Le chiffrement protège la confidentialité et peut contribuer à l’intégrité, mais il doit être pris en charge par les équipements et correctement configuré. Sur les communications industrielles sensibles au temps, la latence et la charge doivent être mesurées. Si le chiffrement de bout en bout n’est pas disponible, les frontières, chemins physiques, accès et contrôles compensatoires peuvent réduire l’exposition sans fournir une garantie équivalente.

L’authentification des commandes et des opérateurs est distincte de la simple connectivité. Un réseau segmenté peut encore subir l’action d’un compte privilégié compromis. Vérifiez les identités, les rôles et les conditions de modification. Lorsqu’une fonction critique n’est pas authentifiée au niveau protocole, l’accès doit être limité à un nombre très réduit de systèmes et surveillé avec des méthodes adaptées.

## 7. Gestion des vulnérabilités et patch management OT

### 7.1 Prioriser selon l’exposition et l’impact physique

Les correctifs d’OT doivent être planifiés avec prudence parce qu’un redémarrage ou une régression peut perturber le contrôle. Cela ne signifie pas qu’il faut accepter indéfiniment les vulnérabilités. La priorisation combine la présence réelle de la faiblesse, la possibilité d’exploitation, les chemins d’accès, la criticité de l’actif, les conséquences sur le procédé, l’existence d’un correctif, la compatibilité, le statut de support et les mesures compensatoires.

Une vulnérabilité sur un poste d’ingénierie connecté à plusieurs cellules peut avoir un rayon d’impact élevé. Une faiblesse sur un actif isolé mais essentiel à la protection peut être critique même s’il n’est pas directement accessible. La priorité doit être discutée avec l’exploitant, l’automatisme et la sécurité. Les équipes doivent documenter les hypothèses au lieu de classer tout le matériel sur le seul score du scanner.

### 7.2 Tester hors ligne ou dans une maquette

Avant d’appliquer un correctif à une production industrielle, vérifiez les notes de version, les prérequis, la compatibilité avec les versions du PLC, du SCADA, des pilotes et des outils d’ingénierie. Testez sur une maquette, un environnement hors ligne ou un système représentatif lorsque cela est possible. Confirmez les fonctions essentielles, la redondance, les alarmes, l’historisation et le comportement de récupération.

Les fournisseurs peuvent fournir des matrices de compatibilité ou des procédures d’upgrade. Ces ressources doivent être conservées et comparées à l’installation exacte. Si aucune maquette identique n’existe, la décision doit reconnaître l’incertitude et mettre en place les mesures compensatoires et le plan de restauration. Une intervention d’urgence doit avoir des rôles, une fenêtre et des critères d’arrêt clairs.

~~~text
Avis de vulnérabilité
       |
       v
Applicabilité confirmée sur l'actif ?
       |
       v
Conséquence procédé / sûreté et exposition
       |
       v
Correctif ou mitigation proposée
       |
       v
Test sur maquette / hors ligne / fournisseur
       |
       v
Approbation changement + sauvegarde vérifiée
       |
       v
Déploiement contrôlé et validation du procédé
~~~

### 7.3 Fenêtres de maintenance

La fenêtre doit être coordonnée avec l’exploitation, la maintenance, les fournisseurs et la personne responsable de la sûreté. Définissez les étapes, les conditions préalables, les points de contrôle, les critères d’arrêt et le chemin de rollback. Si le procédé ne peut pas être interrompu, évaluez une mitigation qui réduit l’exposition et un plan de correction pendant une période où le risque est acceptable.

Une fenêtre planifiée n’est pas une garantie qu’on pourra corriger le problème. Le système peut ne pas revenir correctement, ou un équipement redondant peut ne pas basculer comme prévu. Le plan doit inclure les capacités locales, une communication claire, les pièces nécessaires, une sauvegarde disponible et les conditions pour suspendre l’intervention sans pression à « forcer » un déploiement dangereux.

### 7.4 Actifs sans correctif et équipements hors support

Si aucun correctif n’est disponible, ou si l’équipement n’est plus supporté, il faut réduire les voies d’exploitation : restreindre l’accès, limiter les protocoles et commandes, isoler la zone, supprimer les connexions inutiles, surveiller les événements et préparer le remplacement. Ces mesures ne font pas disparaître la faiblesse. Elles modifient les conditions d’exploitation et doivent être testées pour éviter d’interrompre une communication nécessaire.

Le plan doit comporter propriétaire, date cible, risque résiduel, mesures de compensation, décision d’acceptation, échéance de revue et plan de sortie. Les exceptions sans date ni responsable deviennent des décisions invisibles. Le niveau de risque doit être réévalué si les menaces changent, si l’actif devient plus exposé ou si le procédé est modifié.

## 8. Sauvegardes et restauration

### 8.1 Que faut-il sauvegarder ?

La sauvegarde OT peut inclure les programmes des automates, projets d’ingénierie, configurations réseau, images de stations, fichiers de configuration, bases de données d’historisation, règles de pare-feu, fichiers de licences, documents de conception et outils nécessaires à la restauration. Il faut savoir quelle version est approuvée, à quel système elle correspond et quelles dépendances sont nécessaires pour la réutiliser.

Une sauvegarde d’un programme sans la version du logiciel d’ingénierie ou les données de référence peut être difficile à restaurer. Les licences, pilotes, certificats, configurations et procédures de téléchargement font partie du plan. La récupération doit être testée avec les techniciens responsables et sur un équipement compatible. Ne réalisez pas de restauration sur le procédé réel sans procédure approuvée.

### 8.2 Intégrité et stockage

Protégez les sauvegardes contre la modification non autorisée, le chiffrement malveillant et l’effacement. Utilisez des copies hors ligne ou immuables quand cela est adapté, des comptes séparés, des contrôles d’accès et des vérifications d’intégrité. La copie accessible en permanence par le même compte administrateur que la production peut être compromise au même moment que le système.

~~~text
Configuration approuvée
        |
        v
Copie contrôlée et versionnée
        |
        +--> dépôt restreint en ligne
        |
        +--> copie séparée / immuable / hors ligne
        |
        v
Test de restauration sur environnement approuvé
        |
        v
Rapport : durée, état restauré, dépendances, écarts
~~~

Les sommes de contrôle ou digests permettent de vérifier que les fichiers n’ont pas changé entre deux mesures, mais la référence de comparaison doit elle-même être protégée. Une image signée par un compte compromis ne suffit pas. Conservez des logs, la date, l’identité qui a créé la sauvegarde, le système source et les changements associés.

### 8.3 Tester le retour au service

La restauration doit être testée selon un calendrier et après des changements importants. Évaluez le temps nécessaire pour remettre le service à un état acceptable, les compétences nécessaires, les dépendances fournisseurs, les médias de démarrage et la compatibilité des versions. Définissez les critères opérationnels de validation : les mesures affichées sont cohérentes, les alarmes sont attendues, les communications sont rétablies et les fonctions de protection sont conformes aux procédures du site.

Ne considérez pas la copie de sauvegarde comme valide uniquement parce que le job a annoncé « success ». Une sauvegarde peut être incomplète, corrompue, obsolète ou impossible à restaurer sur le matériel disponible. Les tests et les résultats documentés donnent une preuve plus solide que le statut d’un outil.

## 9. Surveillance et détection adaptées à l’OT

### 9.1 Surveillance passive

La surveillance passive observe les communications ou événements existants sans envoyer de sondes actives à tous les équipements. Elle peut détecter des nouveaux actifs, changements de flux, protocoles inattendus, transferts de fichiers, connexions fournisseur hors fenêtre ou communications entre zones qui ne sont pas dans la matrice. Cette approche limite le risque d’interaction directe avec des équipements fragiles, mais doit être déployée de manière à ne pas perturber le réseau ni introduire un point de défaillance.

Les capteurs doivent être placés à des points qui offrent une visibilité pertinente. Un seul capteur sur le réseau d’entreprise ne révèle pas nécessairement les communications entre contrôleurs. Les ports miroir, TAP, compteurs et journaux de commutateurs peuvent fournir des éléments, mais les limites de visibilité doivent être documentées. Toute perte de capture peut se traduire par une période aveugle et doit être surveillée.

### 9.2 Définir une ligne de base

Établissez le comportement normal du procédé et des communications : actifs habituels, protocoles, pairs, horaires de maintenance, volumes, versions, changements planifiés et commandes administratives attendues. La période de base doit inclure les différents modes pertinents de fonctionnement, sans supposer que tous les modes sont présents dans un court échantillon. Les alertes doivent distinguer un changement autorisé, une opération rare mais légitime et un comportement incohérent à examiner.

Un changement de communication peut être dû à une mise à jour, une maintenance ou un nouvel équipement, et pas forcément à une attaque. Le processus doit relier la détection au registre des changements. À l’inverse, l’absence d’alerte ne signifie pas que les commandes sont légitimes si le capteur ne peut pas interpréter le protocole ou si le trafic n’est pas visible.

~~~text
Comportement de référence
  |-- actifs et communications attendus
  |-- profils de maintenance
  |-- volumes et périodes
  |-- commandes d'administration autorisées
          |
          v
Nouvelle observation
          |
          +--> correspond à un changement approuvé : valider
          |
          +--> sans justification : enquêter avec l'exploitant
          |
          v
Enrichissement + décision + preuve
~~~

### 9.3 Journalisation

Les sources utiles incluent les connexions au bastion, changements de configuration, accès aux stations d’ingénierie, modifications de programme, événements d’authentification, règles de pare-feu, alertes des capteurs, accès physique et événements des services d’entreprise qui atteignent l’OT. Les horloges doivent être synchronisées de façon sûre et les effets d’une perte de synchronisation connus. Certains équipements disposent de capacités limitées : la stratégie doit les prendre en compte et ne pas saturer le système avec trop de logs.

Les logs doivent être centralisés lorsque la conception le permet, avec contrôle d’accès et protection contre l’altération. Ne changez pas la méthode de collecte sans test si elle risque de consommer des ressources. Définissez les périodes de conservation et les utilisateurs autorisés à consulter les détails de procédé. Les données industrielles peuvent être sensibles commercialement et révéler l’architecture physique de l’installation.

### 9.4 Utiliser MITRE ATT&CK for ICS avec prudence

MITRE ATT&CK for ICS décrit des tactiques et techniques associées aux adversaires dans les environnements industriels, y compris l’accès initial, la découverte, le mouvement latéral, l’inhibition des fonctions de réponse, l’altération du contrôle du procédé et les impacts physiques. Le cadre peut aider à construire des scénarios de détection, tester la couverture et organiser les procédures de réponse. Il ne doit pas être transformé en catalogue de tests intrusifs à exécuter sans autorisation sur une installation réelle.

Associez chaque scénario à des sources de télémétrie, un responsable, une procédure de triage et un critère d’escalade. Si une technique ne peut pas être testée en production en sécurité, utilisez une simulation, une table d’exercices ou un environnement laboratoire. Le but est de vérifier la capacité de détection et de réaction sans mettre le procédé en danger.

## 10. Répondre aux incidents sans compromettre la sûreté

### 10.1 Procédure coordonnée

Une réponse à incident OT doit impliquer l’exploitation, la sûreté, l’automatisme, la cybersécurité, le réseau, la maintenance, les fournisseurs et la direction selon l’impact. Une action informatique qui serait simple ailleurs — débrancher une interface, arrêter un service, redémarrer un serveur ou bloquer un protocole — peut affecter la supervision ou l’état physique du procédé. Les premiers gestes doivent se baser sur des procédures préparées à l’avance et le commandement doit être clair.

L’équipe cyber qualifie les signaux et protège les preuves ; l’exploitant du procédé décide des contraintes de conduite et de sécurité physique ; l’autorité de gestion d’incident coordonne les objectifs. Lorsque les indications sont ambiguës, il faut préserver la capacité de contrôler le procédé et se conformer au plan d’urgence du site. L’objectif n’est pas de préserver un réseau au détriment des personnes.

### 10.2 Détection, confinement, continuité

L’ordre des opérations dépend du risque. Il peut être nécessaire de limiter un accès distant, bloquer une promotion logicielle, isoler un poste d’ingénierie ou suspendre une interconnexion. Mais l’isolement doit être ciblé et validé par l’exploitant, surtout si l’actif assure une communication nécessaire au contrôle. La perte de télémétrie peut elle-même constituer un danger si l’opérateur ne voit plus l’état du procédé.

~~~text
Signal / suspicion
       |
       v
Alerter le responsable incident et l'exploitant OT
       |
       v
Préserver les données sans perturber le procédé
       |
       v
Qualifier l'impact technique et physique
       |
       v
Choisir un confinement approuvé par le commandement
       |
       v
Rétablir depuis une configuration connue
       |
       v
Valider l'état sûr, puis documenter les preuves
~~~

### 10.3 Conservation des preuves

Avant de redémarrer ou réinitialiser un système, évaluer la nécessité de préserver les journaux, images, configurations, projets d’automates, fichiers de programme, événements réseau et données de support. La collecte peut avoir des contraintes particulières sur les systèmes OT ; utilisez les méthodes acceptées par le site et les équipes spécialisées. Il faut éviter les manipulations non nécessaires qui changeraient l’état ou écraseraient les traces.

La chaîne de conservation doit enregistrer la source, l’heure, le responsable, la méthode, le hash lorsqu’il est adapté et l’emplacement sécurisé. Les secrets et données sensibles de procédé doivent être protégés. Une enquête ne doit pas retarder une mesure urgente nécessaire pour préserver la sûreté des personnes : les procédures doivent prévoir comment gérer ces deux impératifs.

### 10.4 Reprise et validation

La reprise doit vérifier plus que l’accès réseau. Confirmez que les programmes, paramètres, alarmes, communications, historiques et protections attendus sont présents ; le responsable opérationnel doit valider le comportement du procédé selon les procédures du site. Une connectivité rétablie ne suffit pas à prouver que le système est sûr. Les versions et configurations doivent être comparées à la référence approuvée.

Après le rétablissement, surveillez les signaux de réapparition, contrôlez les identifiants utilisés pendant l’incident, corrigez les voies d’accès, restaurez les sauvegardes fiables et actualisez la matrice de flux. Les actions post-incident doivent avoir un propriétaire et une échéance. Un rapport utile explique comment l’attaque ou l’erreur a traversé les frontières de confiance et comment on empêchera ou détectera un scénario similaire.

## 11. Gestion des changements

### 11.1 Tout changement doit avoir une justification

Une modification réseau ou de contrôle peut affecter la disponibilité et la sécurité. Chaque changement doit définir la raison, le périmètre, les actifs concernés, les dépendances, le risque, le responsable, la fenêtre, le test, les critères de succès et le plan de retour arrière. Le changement d’une règle firewall, la mise à jour d’un firmware, la modification d’un compte, l’ajout d’un flux cloud ou le téléchargement d’un programme sur un automate exige une procédure adaptée à son impact.

Les approbations doivent venir des personnes compétentes. Une validation de cybersécurité seule ne remplace pas l’approbation d’exploitation, d’automatisme ou de sûreté lorsque le procédé est concerné. De même, un fournisseur ne doit pas exécuter un changement critique sans responsable interne qui connaît l’impact et peut confirmer le résultat.

### 11.2 Gérer les changements d'urgence

Une urgence peut exiger un changement en dehors du cycle normal, par exemple pour couper un accès fournisseur suspect ou appliquer une mitigation contre une vulnérabilité exploitée. La voie d’urgence doit être définie : qui est autorisé à décider, comment vérifier l’impact, quels journaux sont conservés, quel niveau d’approbation est nécessaire et comment effectuer la revue après l’action.

Le changement d’urgence ne doit pas devenir une voie permanente sans documentation. Après stabilisation, réalisez une revue qui confirme ce qui a été appliqué, les risques résiduels, les écarts et les actions complémentaires. Documentez les changements manuels pour éviter qu’une configuration non enregistrée reste en place.

### 11.3 Tests sur maquette et jumeau numérique

Une maquette ou un jumeau numérique peut permettre de tester une règle, un correctif, une mise à jour de contrôleur, un changement de version ou un scénario de récupération. Sa valeur dépend de sa fidélité : une maquette qui n’a pas le même firmware, les mêmes dépendances ou la même topologie peut manquer une régression importante. Il faut documenter les différences et ne pas considérer le succès du test comme une garantie parfaite en production.

Les simulations de réponse à incident sont également importantes. Elles peuvent vérifier les décisions, les responsabilités, les voies d’escalade, l’accès aux sauvegardes et les communications sans altérer de matériel actif. Les essais d’attaque sur un procédé réel nécessitent un cadre de test distinct, autorisé, coordonné et conçu pour ne pas créer de conditions dangereuses.

## 12. Continuité, résilience et dépendances

### 12.1 Identifier les fonctions critiques

Le plan de continuité doit identifier les fonctions qui doivent rester disponibles, les états opérationnels acceptables, les dépendances, les procédures manuelles autorisées et les priorités de restauration. Les objectifs de reprise doivent être déterminés par le métier et les risques physiques. Un délai de reprise acceptable pour un système de reporting peut être inacceptable pour une fonction de commande ou de protection.

Une architecture redondante n’élimine pas tous les risques : une identité commune compromise, une mauvaise configuration répliquée ou un firmware vulnérable identique peut affecter plusieurs systèmes. La segmentation et la séparation des accès doivent couvrir les deux côtés de la redondance. Les scénarios de panne du service de temps, du DNS, de l’identité, de l’archivage et du lien d’entreprise doivent être envisagés si ces éléments sont des dépendances de l’OT.

### 12.2 Procédures manuelles et état sûr

Les procédures manuelles ne sont pas une solution improvisée après une attaque. Elles doivent être rédigées, formées, validées et maintenues avec les responsables de procédé et de sécurité. Certaines actions manuelles peuvent elles-mêmes créer des risques ; elles doivent être limitées à ce que le personnel compétent est autorisé à réaliser. La décision de mise à l’arrêt ou de passage à un mode sûr appartient aux procédures de sûreté et au commandement opérationnel.

Le plan doit préciser les conditions de transition, les rôles, les communications de secours et le niveau de vérification requis pour revenir au mode normal. La restauration d’un serveur ou d’un lien réseau ne doit pas automatiquement déclencher des commandes sur le procédé. Il faut vérifier les états et reprendre la conduite conformément aux procédures validées.

### 12.3 Contrats et support fournisseur

Le support fournisseur peut nécessiter un accès distant, des mises à jour, des fichiers de configuration et des interventions sur les systèmes. Les contrats doivent définir la notification d’incident, les délais, l’identité des intervenants, la portée de l’accès, la gestion des sous-traitants, le support des versions, les correctifs, les sauvegardes et la fin de vie. Le fournisseur ne doit pas conserver des comptes actifs ou des tunnels permanents sans décision et suivi.

Les logiciels et pièces de remplacement doivent être obtenus par une source autorisée, être compatibles avec l’installation et faire l’objet d’une vérification avant intégration. Conservez les versions, sommes de contrôle et signatures disponibles. Les composants de rechange et médias d’installation font partie de la continuité, car une intervention d’urgence peut nécessiter de reconstruire une station sans accès à la source du fournisseur.

## 13. Sûreté physique et environnements particuliers

### 13.1 Accès physique

Une personne ayant accès à une baie, un port de maintenance ou une station locale peut contourner certaines frontières logiques. Contrôlez les accès aux salles, armoires, postes d’ingénierie, ports console et équipements portables. Les badges, journaux de visite, accompagnement des fournisseurs et procédures de gestion des supports doivent être adaptés au risque et à la réalité du site.

Les contrôles physiques doivent être coordonnés avec les opérations : une porte verrouillée ne doit pas retarder une intervention de sécurité autorisée, mais les accès d’urgence doivent être consignés. Les modifications de câblage, connexions nouvelles, changements d’alimentation et ouvertures d’armoire peuvent être des événements à surveiller.

### 13.2 Réseaux radio, télémaintenance et capteurs sans fil

Les environnements peuvent inclure des réseaux Wi-Fi industriels, radios privées, liaisons cellulaires, passerelles IIoT et capteurs sans fil. Ces technologies apportent mobilité et couverture mais augmentent le nombre de canaux à inventorier. Définissez les identités de dispositif, la rotation des clés, les profils de connexion, la segmentation, la gestion du firmware et le comportement en cas de perte de signal.

Ne supposez pas qu’un appareil radio isolé est sans risque : une passerelle peut relier un capteur à un système de supervision et devenir un nouveau chemin d’accès. Les liaisons temporaires d’intervention doivent être autorisées, vérifiées et retirées après usage. Les tests de radio ou de pénétration doivent se dérouler dans des plages autorisées et coordonnées pour ne pas interférer avec les systèmes de production.

### 13.3 Cloud et accès de données industrielles

Les données d’historisation, d’analyse et de maintenance peuvent être traitées dans le cloud ou par des services distants. Séparez les flux de télémétrie des flux de commande. Lorsqu’un service cloud ne fait que recevoir des mesures, il ne doit pas automatiquement disposer d’une voie de commande vers les contrôleurs. Les comptes et clés d’API doivent être limités à la fonction, surveillés et révoqués en cas de besoin.

Toute convergence cloud-OT doit être examinée selon la latence, la disponibilité du lien, la résidence des données, les accès du fournisseur, le comportement en cas de coupure et le risque de propagation. Une coupure de l’accès cloud ne doit pas provoquer de manière imprévue l’arrêt du contrôle local, sauf si cette dépendance fait partie de la conception de sûreté évaluée.

## 14. Cadres, normes et références de sécurité OT

### 14.1 NIST SP 800-82

NIST SP 800-82 Rev. 3, publiée en septembre 2023, fournit une référence importante pour la sécurité OT avec une attention particulière aux exigences de performance, fiabilité et sûreté. Le 21 septembre 2026, NIST a également publié le premier projet public de Rev. 4. Ce projet élargit l’attention à plusieurs secteurs et technologies OT, restructure les recommandations autour du NIST Cybersecurity Framework 2.0 et développe notamment la gestion des actifs, la surveillance réseau, l’accès d’administration et les principes Zero Trust. Le projet n’est pas la version finale ; la page officielle indique une période de commentaires ouverte jusqu’au 30 novembre 2026.

Une organisation qui cite la Rev. 4 doit signaler qu’il s’agit d’un projet public et préciser la version consultée. Les exigences finales peuvent évoluer. Pour une procédure opérationnelle, s’appuyer sur la publication finale applicable et utiliser le draft comme information de préparation, sans le présenter à tort comme une obligation finale.

### 14.2 Série ISA/IEC 62443

La série ISA/IEC 62443 couvre le programme de sécurité des propriétaires d’actifs, les exigences des fournisseurs de services, les évaluations de risques, les zones et conduits, les exigences système et les pratiques de développement de produits. La partie 3-2 traite notamment de la définition du système considéré, de sa partition en zones et conduits, de l’évaluation du risque et de la définition des objectifs de sécurité. La partie 3-3 décrit des exigences de sécurité pour les systèmes. Les parties 4-1 et 4-2 concernent notamment le cycle de développement sécurisé et les exigences techniques des composants.

La norme ne donne pas une configuration réseau universelle adaptée à toutes les installations. Le système doit être défini, les risques évalués et les exigences choisies selon le contexte. Les niveaux de sécurité ne doivent pas être assignés de façon mécanique uniquement à partir d’un score ; il faut expliquer les capacités visées et la preuve attendue. Consultez la version et l’édition pertinentes dans le catalogue ISA/IEC.

### 14.3 ATT&CK for ICS et exercices défensifs

MITRE ATT&CK for ICS fournit un vocabulaire de tactiques et techniques qui peut aider à raisonner sur les chemins d’attaque et la couverture de détection. Certaines techniques décrivent des impacts particulièrement industriels, comme la perte de contrôle, la perte de visibilité ou l’altération de fonctions de protection. Ce modèle peut éclairer les analyses de scénario, les règles de détection, les exercices sur table et les plans d’amélioration.

Il ne remplace pas les normes d’architecture ni la procédure d’exploitation. L’équipe doit relier chaque scénario aux actifs, sources de télémétrie, impacts possibles, responsables et réponses approuvées. L’entraînement doit rester dans un environnement de test, avec des simulations adaptées, à moins qu’un essai réel soit spécialement autorisé et encadré par un protocole de sécurité.

## 15. Travaux pratiques guidés

Les travaux pratiques sont défensifs et doivent être exécutés sur maquettes, simulateurs ou environnements de laboratoire isolés. N’appliquez pas des scans, des règles, des mises à jour ou des commandes de test sur un procédé réel sans validation de l’exploitant, analyse de risque et autorisation documentée. Ne manipulez pas un automate actif pour démontrer une attaque.

### TP 1 — Construire une architecture zones/conduits

**Scénario :** une usine fictive possède un réseau d’entreprise, une zone de supervision, un historien, une station d’ingénierie, deux cellules de contrôle PLC et un SIS séparé. Un fournisseur doit faire une maintenance planifiée. Les flux réseau ont grandi sans matrice à jour.

**Étapes :**
1. Établir la liste des actifs, leurs fonctions et leurs propriétaires.
2. Identifier les communications nécessaires en fonctionnement normal, maintenance et reprise.
3. Regrouper les actifs en zones fondées sur la fonction et le risque.
4. Définir les conduits avec source, destination, protocole, sens, justification et propriétaire.
5. Proposer une IDMZ pour les transferts et l’accès distant.
6. Identifier les chemins qui permettraient à un poste IT ordinaire de joindre un contrôleur.
7. Décrire les risques de disponibilité et les tests nécessaires avant de modifier les flux.
8. Définir une méthode de revue et de validation de la matrice tous les six ou douze mois selon la politique locale.

**Correction de référence :** la matrice doit refléter les besoins du procédé et inclure les chemins de maintenance, pas seulement le trafic observé pendant une heure. L’accès fournisseur passe par une zone intermédiaire contrôlée et un bastion, avec approbation et durée limitée. La station d’ingénierie dispose d’un conduit dédié vers les contrôleurs nécessaires. Le SIS est isolé conformément à sa conception et à ses exigences de sûreté, sans supposer que la simple séparation VLAN suffit. Tout flux IT vers un contrôleur doit être justifié et les flux sans justification doivent être refusés après validation opérationnelle.

**Livrable :** diagramme d’architecture, matrice de flux, registre des écarts et plan de changement.

### TP 2 — Concevoir un accès distant temporaire

**Scénario :** un fournisseur doit diagnostiquer une anomalie sur un système SCADA. L’organisation possède un bastion dans l’IDMZ, une MFA, un système de tickets et une supervision de session. Une ancienne connexion VPN fournisseur reste active en permanence.

**Étapes :**
1. Décrire les informations obligatoires du ticket : identité, cible, motif, fenêtre, opérations et approbateur.
2. Définir les permissions minimales et les étapes d’activation temporaire.
3. Préciser comment la session sera surveillée et enregistrée.
4. Définir les règles de transfert de fichiers et de supports.
5. Écrire la procédure de révocation en fin de session.
6. Prévoir le chemin d’urgence si le bastion ou la MFA est indisponible.
7. Examiner le tunnel permanent et proposer un retrait ou une exception explicitement approuvée.
8. Tester le scénario dans le lab, notamment une demande rejetée et une session qui dépasse sa fenêtre.

**Correction de référence :** l’accès doit être nominatif, limité à un système précis et accordé pour une durée définie. La MFA se fait avant la session, mais l’autorisation doit encore restreindre la cible et le rôle. La session est journalisée dans les limites légales et opérationnelles. Le tunnel permanent doit être supprimé si aucun besoin vérifié ne l’impose ; si un maintien est indispensable, il doit avoir un propriétaire, une portée minimale, une détection et une revue. Le break-glass doit être protégé et réinitialisé après usage.

**Livrable :** procédure d’accès distant, modèle de ticket et preuve des tests du lab.

### TP 3 — Préparer une campagne de correctifs OT

**Scénario :** le fournisseur annonce un correctif pour une vulnérabilité touchant une version d’un serveur HMI et un composant de la station d’ingénierie. L’installation ne peut pas être interrompue à court terme. Les systèmes disposent d’une maquette partielle et d’une fenêtre d’arrêt prévue dans trois semaines.

**Étapes :**
1. Confirmer l’applicabilité de l’avis à la version réelle.
2. Déterminer les conséquences possibles sur le procédé et les dépendances.
3. Demander ou consulter les notes de compatibilité du fournisseur.
4. Créer un plan de test sur maquette et lister les tests fonctionnels et de sûreté requis.
5. Définir la mitigation temporaire, le responsable, l’échéance et le risque résiduel.
6. Préparer la sauvegarde, le rollback et la communication de changement.
7. Définir les critères de succès, les critères d’arrêt et la preuve de correction.
8. Décrire la validation opérationnelle avant le retour au mode normal.

**Correction de référence :** le correctif n’est pas déployé uniquement parce que le score de vulnérabilité est élevé. L’équipe confirme la version et le chemin d’exposition, puis évalue les risques de patch et les risques d’attente. Elle teste la version sur une maquette représentative, documente ses limites, applique une mitigation approuvée jusqu’à la fenêtre et prépare une sauvegarde restaurable. Après le déploiement, elle vérifie les fonctions essentielles, les communications, les alarmes et la version réellement active avant clôture.

**Livrable :** analyse de risque, plan de test, ticket de changement, rollback et preuve de revalidation.

### TP 4 — Exercice sur table d’un incident OT

**Scénario :** la supervision OT reçoit une alerte de connexion fournisseur hors fenêtre et le capteur réseau voit une nouvelle communication entre l’IDMZ et une station d’ingénierie. Le procédé est encore stable, mais l’équipe ne sait pas si un accès non autorisé a eu lieu. Aucun essai intrusif ne sera exécuté ; les faits sont injectés dans un exercice sur table.

**Étapes :**
1. Identifier les responsables qui dirigent l’incident et l’exploitation.
2. Définir les premières questions sans interrompre le procédé.
3. Choisir les journaux, données de session, tickets et changements à préserver.
4. Proposer des mesures de confinement autorisées qui ne provoquent pas une perte incontrôlée de visibilité.
5. Décider quand l’exploitant doit envisager une transition vers un état sûr selon les procédures du site.
6. Préparer un compte rendu à la direction et une communication avec le fournisseur.
7. Décrire la validation du système après restauration.
8. Établir des actions correctives avec propriétaire, date et preuve.

**Correction de référence :** le commandement doit impliquer l’exploitant OT, l’équipe cyber et les responsables de sûreté selon l’impact. Il faut préserver les logs du bastion, les événements réseau et les tickets, puis qualifier la session et la cible. Une révocation ciblée de l’accès distant peut être préférable à une coupure générale non analysée. Si un changement menace la visibilité ou le contrôle du procédé, il doit être validé selon la procédure opérationnelle. La restauration doit confirmer l’intégrité et le comportement, pas seulement l’état réseau.

**Livrable :** chronologie, décision de confinement justifiée, liste des preuves et plan de retour d’expérience.

## 16. Exercices corrigés

### Exercice 1 — Définition d'OT

Quelle est la caractéristique essentielle qui distingue l’OT de nombreux systèmes IT ?

**Correction :** l’OT surveille ou influence un procédé physique, de sorte que disponibilité, intégrité de commande, temps de réponse, fiabilité et sûreté peuvent avoir des conséquences matérielles directes. Les systèmes IT peuvent également être critiques, mais les contraintes opérationnelles doivent être évaluées selon le procédé.

### Exercice 2 — Interruption d'un réseau

Un administrateur veut bloquer un flux inhabituel entre deux zones industrielles immédiatement. Que doit-il faire avant d'appliquer la règle ?

**Correction :** vérifier le flux avec l’inventaire, le responsable procédé et la matrice de communication, évaluer l’impact sur le contrôle et la sûreté, définir un plan de changement et un retour arrière. Si la menace est active, appliquer la procédure d’urgence et une mesure ciblée approuvée.

### Exercice 3 — Scan actif

Pourquoi ne faut-il pas lancer un scan agressif sur chaque PLC dès l’installation du scanner ?

**Correction :** certains équipements peuvent réagir de manière inattendue à des requêtes non prévues ou sensibles au temps. Il faut consulter le fabricant, utiliser une méthode passive ou une maquette quand c’est préférable, puis n’effectuer qu’un test actif autorisé et évalué.

### Exercice 4 — Zone et conduit

Un poste d’ingénierie et dix postes de bureau partagent le même réseau parce qu’ils utilisent tous Windows. Est-ce une bonne justification ?

**Correction :** non. Les zones doivent refléter les fonctions, les privilèges et le risque. Le poste d’ingénierie peut modifier des contrôleurs et nécessite une séparation, des accès minimaux et des flux ciblés.

### Exercice 5 — IDMZ

À quoi sert la zone démilitarisée industrielle ?

**Correction :** elle crée une zone intermédiaire contrôlée entre IT et OT pour les relais, transferts, accès distants ou services d’échange. Elle n’est pas automatiquement fiable et doit rester segmentée et surveillée.

### Exercice 6 — Accès fournisseur

Un fournisseur affirme qu’un tunnel permanent est nécessaire pour réduire les délais de support. Quelle est la bonne réponse ?

**Correction :** demander le besoin précis, évaluer le risque, rechercher une session temporaire et approuvée, puis justifier toute exception. Si un accès persistant est accepté, limiter les destinations, le privilège, la durée d’utilisation opérationnelle, la surveillance et la revue.

### Exercice 7 — MFA

Un contrôleur ancien ne supporte pas de MFA. Faut-il l’abandonner immédiatement ?

**Correction :** pas nécessairement. Placez la MFA à la frontière de l’accès distant ou au bastion, réduisez les chemins vers le contrôleur, limitez les comptes et surveillez les sessions, puis définissez une stratégie de remplacement ou une exception documentée.

### Exercice 8 — Patch urgent

Une vulnérabilité critique vient d’être annoncée mais aucun test de compatibilité n’a été effectué. Quelle action est correcte ?

**Correction :** confirmer l’applicabilité et le contexte, vérifier les recommandations du fournisseur, analyser les risques de déploiement et les mesures compensatoires. Préparer un test et une procédure accélérée sûre plutôt que d’installer sans évaluation ou de laisser le risque sans action.

### Exercice 9 — Sauvegarde

Un job de sauvegarde indique un succès, mais aucune restauration n’a été testée depuis deux ans. Est-ce suffisant ?

**Correction :** non. L’intégrité, l’exhaustivité, la compatibilité des versions et le temps de restauration restent incertains. Organisez un test sur un environnement approprié et documentez les résultats.

### Exercice 10 — HMI et programme PLC

Un opérateur peut visualiser les mesures. Cela signifie-t-il qu’il doit pouvoir télécharger un programme dans le PLC ?

**Correction :** non. La visualisation et la modification de logique sont des fonctions différentes. Les droits de programmation doivent être réservés aux identités autorisées, dans une procédure de changement et une fenêtre approuvée.

### Exercice 11 — Règle de pare-feu large

Le fournisseur demande l’accès TCP à toutes les adresses du réseau OT. Que faut-il faire ?

**Correction :** demander les cibles, services, protocoles, directions et fenêtres exacts. Définir un conduit minimal par bastion et refuser l’accès général tant qu’il n’est pas justifié par une analyse et une décision explicite.

### Exercice 12 — Protection indépendante

Une équipe pense que le SIS peut remplacer tous les contrôles de cybersécurité du réseau. Est-ce correct ?

**Correction :** non. Les systèmes de sécurité fonctionnelle servent à gérer des risques du procédé selon leur conception ; ils ne remplacent ni le contrôle d’accès ni la segmentation et doivent eux-mêmes être protégés et maintenus.

### Exercice 13 — Surveillance passive

Quelle est une limite importante de la surveillance passive ?

**Correction :** elle ne voit que les échanges observables pendant la période de capture et aux points de visibilité disponibles. Les actifs silencieux, les communications rares ou les segments non couverts peuvent rester inconnus.

### Exercice 14 — ATT&CK for ICS

À quoi sert ATT&CK for ICS dans le programme défensif ?

**Correction :** à organiser des scénarios de menace, des détections et des exercices. Il ne s’agit pas d’une autorisation d’exécuter des techniques intrusives sur une installation active.

### Exercice 15 — Perte de visibilité

Un pare-feu bloque un flux de télémétrie suspect et l’opérateur perd la vue d’un procédé. Pourquoi cela peut-il être un risque de sûreté ?

**Correction :** la perte d’information peut empêcher l’opérateur de détecter un changement physique ou de prendre une décision appropriée. Les règles doivent être évaluées avec l’exploitant, et le confinement doit préserver un état sûr.

### Exercice 16 — Programme d’automate modifié

Une comparaison révèle que le projet d’un PLC a changé sans ticket. Que faire ?

**Correction :** suivre le processus d’incident et de changement : préserver les informations disponibles, identifier les personnes et outils d’accès, évaluer l’effet sur le procédé avec l’automatisme, vérifier l’intégrité du programme et choisir une action approuvée. Ne pas téléverser automatiquement une ancienne version sans analyse du procédé.

### Exercice 17 — Système hors support

Une station de contrôle hors support est isolée d’Internet. Peut-on considérer que le risque est supprimé ?

**Correction :** non. Il faut évaluer les chemins de maintenance, le mouvement latéral, les médias, les dépendances et l’impact de l’actif. Une segmentation réduit l’exposition, mais l’exception doit avoir des contrôles et un plan de sortie.

### Exercice 18 — Changement d'urgence

Après une alerte, un ingénieur modifie une configuration à la hâte sans documenter le retour arrière. Que doit prévoir la procédure après l’urgence ?

**Correction :** enregistrer le changement, vérifier l’effet et l’état du procédé, documenter les risques résiduels, compléter la revue et attribuer les actions correctives. La procédure d’urgence ne doit pas devenir une voie d’administration permanente.

### Exercice 19 — Mise en service d'un équipement

Un automate neuf est livré et fonctionne. Peut-on le connecter directement au réseau de production ?

**Correction :** non sans les contrôles prévus : vérifier l’identité, la version, le firmware, la configuration, la provenance, les ports et services nécessaires, les accès par défaut, les sauvegardes et l’approbation de l’exploitant. Le test doit précéder la connexion au périmètre de confiance.

### Exercice 20 — NIST SP 800-82 Rev. 4

Comment faut-il référencer le draft SP 800-82 Rev. 4 publié le 21 septembre 2026 ?

**Correction :** comme un projet public initial, non comme une publication finale. NIST indique une période de commentaires jusqu’au 30 novembre 2026 ; les procédures doivent préciser la version consultée et s’appuyer sur les exigences finales applicables.

## 17. Défi final — Concevoir une architecture OT défensive

**Scénario :** KivuLab exploite une station de traitement d’eau fictive. Le réseau inclut les postes d’entreprise, une IDMZ, un serveur d’historisation, deux stations HMI, une station d’ingénierie, plusieurs PLC/RTU, une passerelle de télémaintenance et un système de protection indépendant. Les fournisseurs possèdent plusieurs comptes de support, certains non utilisés depuis longtemps. Les flux ont grandi de façon informelle, les sauvegardes ne sont pas toutes testées et l’équipe IT veut installer un scanner actif sur tout le réseau.

Toutes les activités se déroulent sur papier, en simulation ou en laboratoire isolé. Aucun changement de PLC ou de réseau réel ne doit être fait dans le cadre du défi.

### Livrables obligatoires

1. **Inventaire :** identifier les actifs, rôles, propriétaires, dépendances, versions et fonctions critiques.
2. **Analyse des risques :** construire au moins cinq scénarios qui combinent chemin cyber, impact sur le procédé, sûreté et disponibilité.
3. **Architecture :** produire un diagramme zones/conduits et définir l’IDMZ, les postes d’ingénierie et l’isolation des systèmes de protection.
4. **Matrice de flux :** source, destination, protocole, sens, justification, propriétaire, contrôles et réaction en cas d’échec.
5. **Accès distant :** proposer une authentification forte, une autorisation temporaire, un bastion, une surveillance et un mécanisme d’urgence.
6. **Gestion des changements :** définir tests sur maquette, sauvegarde, fenêtre, critères d’arrêt, rollback et validation du procédé.
7. **Détection :** élaborer une ligne de base passive, des alertes et une procédure de qualification avec l’exploitant.
8. **Résilience :** tester la restauration, retirer les comptes inutilisés et définir la continuité en cas de perte d’accès distant ou de service central.
9. **Gouvernance :** attribuer les rôles, définir les preuves et programmer une revue des risques et de l’inventaire.

### Correction de référence

L’inventaire doit inclure les chemins de maintenance et les systèmes de protection, pas uniquement les appareils visibles dans le réseau. L’architecture sépare IT utilisateur, IDMZ, supervision, ingénierie, contrôle local et systèmes de protection selon l’analyse de risque. Les zones et conduits décrivent les communications nécessaires ; les règles précisent les sources et destinations plutôt que d’autoriser des réseaux entiers. La frontière ne doit pas casser les flux essentiels, et toute modification doit être testée avec les équipes qui exploitent le procédé.

Le scanner actif ne doit pas être lancé sans analyse et autorisation. Commencez par la découverte passive et les sources de configuration, puis déterminez les équipements et méthodes pour lesquels un scan actif est sûr et nécessaire. Les contraintes et angles morts doivent être documentés. L’accès fournisseur se fait par un point contrôlé et temporaire, avec des identités nominatives, MFA, approbation et journaux ; les comptes et tunnels non utilisés sont révoqués selon un changement autorisé.

Pour les correctifs, vérifier l’applicabilité, le fournisseur et les compatibilités, tester en maquette et définir les mesures compensatoires si le déploiement est différé. Les sauvegardes contiennent les programmes, configurations et dépendances nécessaires à la restauration ; elles doivent être protégées et testées. La remise en service exige une validation des fonctions et du procédé, pas uniquement un ping ou un état de service.

La détection combine la ligne de base réseau, l’accès distant, les changements de programme, les journaux de sécurité et les événements physiques pertinents. Une alerte est évaluée avec l’exploitant. Le confinement doit être ciblé et ne pas créer une perte incontrôlée de supervision. Le plan d’incident préserve les preuves, identifie les responsabilités, permet une communication coordonnée et prévoit le rétablissement depuis des configurations connues.

### Barème sur 100 points

- Inventaire complet et classification des actifs : 10 points.
- Analyse des risques cyber et physiques : 15 points.
- Architecture zones/conduits et IDMZ : 20 points.
- Matrice de flux et justification de chaque conduit : 10 points.
- Accès distant et gestion des privilèges : 10 points.
- Correctifs, changements, sauvegardes et restauration : 15 points.
- Surveillance, réponse à incident et préservation des preuves : 10 points.
- Gouvernance, responsabilités et mesures d'efficacité : 10 points.

Une solution qui se limite à installer un pare-feu, lancer un scan actif général ou couper toutes les liaisons sans analyser le procédé ne peut pas obtenir la totalité des points. La réussite est une architecture documentée, testable, exploitable et compatible avec la sûreté.

## 18. Checklist opérationnelle

Avant de déclarer l’architecture OT maîtrisée, vérifier les points suivants :

- Tous les actifs critiques, systèmes de protection, postes de maintenance et accès distants figurent dans l’inventaire.
- Les responsables d’exploitation, de cybersécurité, d’automatisme et de sûreté sont identifiés.
- Les documents réseau et de contrôle ont un propriétaire, une version et une date de validation.
- Les zones sont définies selon les fonctions et les risques ; les conduits sont justifiés par une matrice de flux.
- L’IDMZ est segmentée et aucun poste IT ordinaire n’accède directement aux contrôleurs sans besoin et contrôle documentés.
- Les connexions fournisseur sont temporaires quand c’est possible, nominatives, approuvées, surveillées et révoquées après usage.
- Les stations d’ingénierie sont dédiées, les privilèges sont limités et les programmes de référence sont protégés.
- Les systèmes de protection fonctionnelle sont sécurisés selon leur conception et les changements les concernant sont approuvés par les responsables compétents.
- Les scans actifs sont évalués et approuvés pour le matériel concerné ; des méthodes passives ou alternatives sont prévues.
- Les correctifs sont testés dans une maquette ou selon une méthode validée, avec sauvegarde et rollback.
- Les sauvegardes sont protégées, versionnées, accessibles en situation de crise et testées en restauration.
- Les comportements réseau normaux, les accès et les changements sont surveillés avec des sources adaptées.
- La réponse à incident comprend l’exploitant OT, la sûreté, les responsables cyber et les fournisseurs nécessaires.
- Les critères de confinement et de retour au service protègent l’état sûr et la visibilité opérateur.
- Les versions des standards et guides cités sont identifiées, en distinguant les documents finaux des projets publics.
- Les écarts, exceptions et contrôles compensatoires ont un propriétaire, une échéance et une preuve de revue.

## 19. Glossaire

**Automate PLC** : contrôleur programmable qui exécute une logique de commande d’un équipement ou d’une partie de procédé.

**Bastion** : système intermédiaire contrôlé pour l’accès administratif à des équipements d’une zone sensible.

**Conduit** : groupe de communications entre zones partageant des exigences de sécurité définies.

**DCS** : système de contrôle distribué qui supervise et coordonne un procédé au moyen de contrôleurs et stations répartis.

**HMI** : interface homme-machine permettant de visualiser et, selon les droits, commander un procédé.

**ICS** : systèmes de contrôle industriels qui surveillent ou commandent des processus industriels.

**IDMZ** : zone démilitarisée industrielle placée entre les réseaux d’entreprise et les réseaux de contrôle.

**Interverrouillage** : mécanisme qui empêche une action si certaines conditions de sécurité ou de fonctionnement ne sont pas réunies.

**OT** : technologie opérationnelle, systèmes qui détectent ou provoquent des changements dans le monde physique.

**RTU** : unité terminale distante, utilisée pour la collecte de mesure et le contrôle d’équipements éloignés.

**SCADA** : système de supervision, acquisition de données et commande de sites ou équipements souvent répartis.

**SIS** : système instrumenté de sécurité conçu pour contribuer à amener ou maintenir un procédé dans un état sûr.

**Zone** : regroupement d’actifs ayant des exigences de sécurité et fonctions communes.

**Matrice de flux** : document qui décrit les communications attendues entre systèmes, leur justification et les contrôles requis.

**Mode dégradé** : fonctionnement limité prévu par la conception et les procédures lorsque certaines capacités sont indisponibles.

**Découverte passive** : méthode d’inventaire qui observe les communications existantes au lieu de sonder activement les équipements.

**Gestion de changement** : processus d’approbation, test, déploiement, vérification et retour arrière d’une modification.

**Sûreté fonctionnelle** : partie de la sécurité liée aux fonctions de commande et de protection visant à prévenir les situations dangereuses ou à réduire leurs conséquences.

**Jumeau numérique** : représentation numérique d’un système physique, dont la fidélité doit être évaluée avant de s’en servir comme preuve de test.

**ATT&CK for ICS** : cadre de tactiques et techniques d’adversaires dans les environnements industriels, utile à la conception de scénarios défensifs.

## 20. Références officielles

- NIST SP 800-82 Rev. 3, Guide to Operational Technology (OT) Security, publication finale de septembre 2023 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
- NIST SP 800-82 Rev. 4, Initial Public Draft publié le 21 septembre 2026 ; période de commentaires jusqu’au 30 novembre 2026 : https://csrc.nist.gov/pubs/sp/800/82/r4/ipd
- Annonce NIST de la révision 4 : https://csrc.nist.gov/news/2026/draft-guide-to-ot-security
- Série ISA/IEC 62443, y compris programme de sécurité, zones/conduits et exigences systèmes : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
- IEC PAS 62443-2-2:2025, Security for industrial automation and control systems — IACS security protection scheme : https://webstore.iec.ch/en/publication/63886
- IEC PAS 62443-1-6:2025, application de la série 62443 à l’Industrial Internet of Things : https://webstore.iec.ch/en/publication/102885
- CISA, ICS Recommended Practices, défense en profondeur, accès distant, correctifs et intervention : https://www.cisa.gov/resources-tools/resources/ics-recommended-practices
- CISA, Cybersecurity Best Practices for Industrial Control Systems : https://www.cisa.gov/sites/default/files/publications/Cybersecurity_Best_Practices_for_Industrial_Control_Systems.pdf
- CISA, Configuring and Managing Remote Access for Industrial Control Systems : https://www.cisa.gov/sites/default/files/recommended_practices/RP_Managing_Remote_Access_S508NC.pdf
- CISA, Recommended Practice for Patch Management of Control Systems : https://www.cisa.gov/sites/default/files/recommended_practices/RP_Patch_Management_S508C.pdf
- MITRE ATT&CK for ICS, matrices, tactiques et techniques : https://attack.mitre.org/matrices/ics/
- MITRE ATT&CK for ICS, techniques : https://attack.mitre.org/techniques/ics/

Les documents de référence servent à concevoir et justifier les contrôles ; ils ne remplacent pas l’analyse de risque propre à l’installation, la documentation du fabricant ou les exigences réglementaires applicables. Vérifiez les versions des guides au moment de la mise en œuvre, et ne présentez pas un draft comme une norme finale.

## Schéma complémentaire A — Décision de changement OT

~~~text
Demande de changement
       |
       v
Analyse technique + analyse de danger
       |
       v
Validation exploitant / automatisme / sûreté
       |
       v
Test maquette + sauvegarde restaurable
       |
       v
Fenêtre + critères d'arrêt + rollback
       |
       v
Vérification du procédé avant clôture
~~~

Cette chaîne formalise le fait qu’un changement cybersécurité doit être évalué par rapport aux dépendances industrielles. Une règle réseau peut être correcte sur le plan logique et néanmoins interrompre un flux nécessaire au contrôle ; l’analyse opérationnelle et les essais sont donc indispensables.

## Schéma complémentaire B — Contrôler les accès fournisseur

~~~text
Identité nominative
       |
       v
Ticket avec cible et durée
       |
       v
Approbation locale OT
       |
       v
MFA + bastion + flux minimal
       |
       v
Journalisation de session
       |
       v
Révocation et revue de fin d'intervention
~~~

Un contrôle isolé ne suffit pas. MFA sans restriction de destination peut laisser un compte compromis atteindre trop d’équipements ; un bastion sans révocation peut laisser une session ouverte ; un ticket sans surveillance ne prouve pas ce qui a été fait. Les contrôles doivent se compléter.

## Schéma complémentaire C — Reprise après compromission

~~~text
Confinement approuvé
       |
       v
Etat de sécurité et preuves préservés
       |
       v
Configuration approuvée identifiée
       |
       v
Restauration sur équipement compatible
       |
       v
Vérification technique et opérationnelle
       |
       v
Validation du responsable du procédé
       |
       v
Surveillance renforcée et retour d'expérience
~~~

Une restauration réussie au niveau informatique ne démontre pas à elle seule que le procédé est prêt à repartir. Le responsable opérationnel doit confirmer les conditions selon les procédures du site, après les contrôles techniques et de sécurité requis.


## Conclusion

La sécurité OT/ICS est une discipline d’architecture et d’exploitation autant qu’une question de technologie. Elle dépend d’un inventaire fidèle, de zones et conduits documentés, d’une IDMZ contrôlée, d’accès distants limités, de postes d’ingénierie protégés, de programmes et configurations sauvegardés, de mises à jour testées, d’une surveillance adaptée et d’une réponse à incident qui respecte la sûreté. Le bon dispositif réduit les chemins d’attaque sans créer de panne ou de comportement dangereux.

La meilleure preuve de maturité est la capacité à expliquer quels flux sont nécessaires, qui peut effectuer une modification, comment la modification est testée, comment l’état approuvé est restauré et qui valide le retour au service. Une architecture industrielle défensive est celle qui reste compréhensible et réversible même pendant un incident.

Fin du cours.