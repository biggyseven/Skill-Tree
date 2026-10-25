# Introduction aux Réseaux OT / ICS — Débutant

## Mise en contexte : le réseau qui contrôle le monde physique

Quand on parle de réseau informatique, on pense souvent à des ordinateurs, des serveurs, au cloud et aux applications bureautiques. Les réseaux OT (*Operational Technology*, ou technologies opérationnelles) ont une mission différente : ils transportent les données qui permettent de surveiller et de piloter des équipements physiques. On les trouve dans les usines, les réseaux électriques, les stations de traitement d’eau, les bâtiments, les infrastructures de transport et les installations pétrolières ou gazières.

Un incident OT peut dépasser la perte de données. Il peut interrompre une production, endommager une machine, dégrader un service essentiel ou créer un risque pour les personnes et l’environnement. La sécurité OT doit donc préserver la cybersécurité tout en respectant la disponibilité, le comportement déterministe, la continuité de production et la sûreté industrielle.

> **Principe central :** avant de modifier, scanner, isoler ou redémarrer un équipement industriel, comprendre son rôle dans le procédé, les conséquences possibles et les procédures d’autorisation. Une bonne action de sécurité informatique peut devenir dangereuse si elle est appliquée sans analyse opérationnelle.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu devras pouvoir :

- expliquer la différence entre IT, OT, ICS et SCADA ;
- identifier capteurs, actionneurs, automates, IHM, serveurs SCADA et systèmes de contrôle distribués ;
- lire une architecture OT simple ;
- comprendre le rôle des switches, VLAN, routeurs, pare-feu et passerelles industrielles ;
- reconnaître quelques familles de protocoles industriels ;
- comprendre pourquoi la disponibilité, la latence et la sûreté sont critiques ;
- identifier des risques courants et proposer des protections de base ;
- réaliser un inventaire simple et une matrice de flux dans un laboratoire simulé ;
- suivre une procédure de diagnostic sans perturber un équipement réel.

## 2. IT, OT, ICS et SCADA : les notions fondamentales

### 2.1 IT : Information Technology

L’IT désigne les technologies de l’information classiques : postes utilisateurs, services d’identité, messagerie, bases de données, serveurs d’entreprise, applications métier et réseau bureautique. Les opérations IT privilégient souvent la confidentialité, l’intégrité et la disponibilité des informations, avec des changements réguliers lorsque ceux-ci sont validés.

### 2.2 OT : Operational Technology

L’OT regroupe les systèmes qui surveillent ou modifient l’état du monde physique, ainsi que les technologies qui les prennent en charge. Il peut s’agir de capteurs de température, de variateurs, de contrôleurs de machines, de systèmes de supervision, de réseaux d’automates ou de contrôle d’accès physique.

### 2.3 ICS : Industrial Control Systems

ICS est un terme générique pour les systèmes de contrôle industriels. Le SCADA, les DCS et les systèmes de contrôle associés aux automates peuvent appartenir à cet ensemble.

### 2.4 SCADA, DCS et PLC

- **SCADA** (*Supervisory Control and Data Acquisition*) : supervision de processus parfois géographiquement dispersés. Il collecte des mesures, présente des alarmes et permet des commandes autorisées.
- **DCS** (*Distributed Control System*) : système de contrôle distribué souvent utilisé pour piloter un processus industriel complexe à partir de contrôleurs et de stations intégrés.
- **PLC / API** (*Programmable Logic Controller / Automate programmable industriel*) : contrôleur exécutant une logique de commande, par exemple démarrer une pompe si certaines conditions sont réunies.
- **RTU** (*Remote Terminal Unit*) : équipement de terrain utilisé notamment dans les infrastructures étendues pour acquérir des données et commander des équipements distants.
- **IHM / HMI** (*Interface Homme-Machine*) : écran permettant à l’opérateur de visualiser les mesures, alarmes, états et commandes autorisées.

Ces termes ne sont pas interchangeables. Un SCADA peut communiquer avec des RTU ou des PLC ; un DCS peut intégrer plusieurs contrôleurs, stations opérateur et serveurs d’ingénierie.

## 3. Du capteur à l’actionneur

Un procédé physique est observé par des capteurs, traité par un contrôleur, puis influencé au moyen d’actionneurs.

```text
     Procédé physique
            |
            v
   Capteur / transmetteur
   (température, pression)
            |
            v
    Entrées de l'automate
            |
            v
    Logique de contrôle
       dans le PLC
            |
            v
    Sorties de l'automate
            |
            v
  Actionneur (vanne, moteur)
            |
            v
     Procédé physique
```

Exemple : un capteur mesure la température d’une cuve. L’automate compare cette mesure à une consigne, applique une logique de contrôle et peut commander une vanne ou un dispositif de refroidissement. Le réseau transporte les mesures, commandes, alarmes ou paramètres, mais il ne remplace pas la logique de contrôle locale.

### 3.1 Pourquoi la sûreté est-elle différente de la cybersécurité ?

- **Cybersécurité** : limiter les accès non autorisés, préserver l’intégrité des données et maintenir la disponibilité.
- **Sûreté fonctionnelle** (*functional safety*) : réduire le risque qu’un système provoque un état dangereux, au moyen de fonctions de sécurité conçues et validées.

Un système instrumenté de sécurité (SIS) peut être séparé du système de contrôle de procédé. Cette séparation et son niveau d’indépendance dépendent de l’analyse de risques et de la conception. Un pare-feu ou un antivirus ne remplace pas une fonction de sécurité conçue conformément aux exigences applicables.

## 4. Architecture OT : niveaux et zones

Un modèle de référence souvent utilisé pour communiquer sur l’architecture industrielle est le modèle Purdue. Il distingue des niveaux fonctionnels, depuis le procédé et les équipements de terrain jusqu’aux systèmes de gestion de l’entreprise. Ce modèle aide à réfléchir, mais une installation réelle ne correspond pas toujours exactement à ses niveaux. Il ne constitue pas à lui seul une architecture de sécurité.

```text
Niveau entreprise
  ERP, bureautique, messagerie, SI métier
                  |
          Zone de frontière IT/OT
                  |
Niveau 3.5 : DMZ industrielle
  relais, transfert de fichiers contrôlé,
  bastion d'accès distant, collecte de journaux
                  |
Niveau 3 : opérations du site
  historiens, supervision de production,
  serveurs SCADA, gestion des opérations
                  |
Niveau 2 : supervision locale
  IHM, stations opérateur, serveurs locaux
                  |
Niveau 1 : contrôle
  PLC/API, contrôleurs, équipements intelligents
                  |
Niveau 0 : procédé
  capteurs, vannes, moteurs, pompes
```

La DMZ industrielle (*Industrial DMZ*) est une zone intermédiaire contrôlée. Elle évite d’autoriser automatiquement des connexions directes entre le réseau bureautique et les contrôleurs. Les données peuvent être transmises par des relais ou des services dédiés, avec des flux explicitement autorisés.

### 4.1 Composants réseau

- **Switch industriel** : relie des équipements Ethernet. Les modèles industriels peuvent être conçus pour résister aux contraintes physiques du site.
- **VLAN** : sépare logiquement des domaines de niveau 2. Un VLAN ne suffit pas à contrôler à lui seul les communications routées entre sous-réseaux.
- **Routeur** : transfère des paquets entre réseaux IP.
- **Pare-feu** : applique des règles aux communications qui le traversent ; un filtrage efficace exige de connaître les flux nécessaires au procédé.
- **Passerelle de protocole** : relie des systèmes qui utilisent des protocoles ou modèles de données différents.
- **Bastion** : point d’accès administré et journalisé pour les sessions d’administration.
- **TAP ou port SPAN** : méthode de copie de trafic pour l’observation, sous réserve d’une conception correcte.

## 5. Protocoles industriels : aperçu

Les protocoles sont choisis selon les équipements, les contraintes temps réel, les fonctions et les exigences du secteur. Il ne faut pas supposer qu’un protocole a les mêmes propriétés de sécurité dans toutes ses versions ou configurations.

| Technologie | Utilisation courante | Point de vigilance |
|---|---|---|
| Modbus RTU | Communication série entre équipements | Les protections dépendent de l’installation et de l’environnement ; protocole historique simple |
| Modbus TCP | Échanges Modbus sur TCP/IP | La variante classique ne fournit pas à elle seule chiffrement et authentification modernes |
| PROFINET | Automatisation industrielle Ethernet | Les exigences et mécanismes dépendent du profil et de la mise en œuvre |
| EtherNet/IP | Automatisation utilisant CIP sur Ethernet/IP | Identifier les flux nécessaires aux services et aux équipements réellement utilisés |
| OPC UA | Échange de données entre applications industrielles | Peut fournir authentification, intégrité et chiffrement lorsque les certificats et politiques sont correctement configurés |
| DNP3 | Téléconduite et infrastructures comme l’énergie | Les extensions de sécurité doivent être prises en charge et configurées ; ne pas présumer qu’elles sont actives |
| BACnet | Automatisation des bâtiments | Les services exposés et les capacités de sécurité varient selon les produits |

Le port TCP 502 est couramment associé à Modbus TCP, le port TCP 4840 à OPC UA et le port TCP 20000 à DNP3/IP. Ce sont des valeurs par défaut fréquentes, pas des preuves qu’un service est présent : les ports peuvent être modifiés et le contexte doit être confirmé par l’inventaire et l’administrateur.

### 5.1 Données de supervision et commandes

Une communication peut servir à lire une mesure, recevoir une alarme, synchroniser l’heure, transférer une recette, changer un paramètre ou télécharger un programme. Ces actions n’ont pas toutes le même niveau de risque. Lire une température n’équivaut pas à écrire une consigne ou à modifier la logique d’un automate.

## 6. Pourquoi les priorités OT diffèrent de l’IT

Les systèmes OT peuvent rester en service pendant de longues périodes, utiliser des systèmes anciens et être difficiles à redémarrer. Une mise à jour testée sur un poste bureautique peut affecter un pilote, une carte de communication ou un logiciel industriel particulier.

Les contraintes à prendre en compte comprennent :

- la disponibilité et la continuité de la production ;
- la sûreté des opérateurs et du public ;
- le temps de réponse et le comportement temporel ;
- la compatibilité avec les équipements anciens ;
- les fenêtres de maintenance limitées ;
- les exigences réglementaires et de validation ;
- les dépendances entre contrôleurs, IHM, serveurs, réseaux et procédés.

La bonne décision est donc fondée sur le risque et coordonnée entre OT, IT, maintenance, automatisme, ingénierie et responsables de sûreté.

## 7. Menaces et faiblesses courantes

Les principaux risques ne se limitent pas aux attaques sophistiquées. Ils comprennent aussi les erreurs de configuration et les accès oubliés.

1. **Connexion directe à Internet** : service de supervision ou interface d’administration exposés involontairement.
2. **Mots de passe partagés ou par défaut** : absence de traçabilité et difficulté à révoquer un accès.
3. **Réseau plat** : une compromission bureautique peut offrir une voie vers plusieurs zones industrielles.
4. **Accès distant non maîtrisé** : accès fournisseur permanent, compte non révoqué ou session non journalisée.
5. **Système non maintenu** : vulnérabilité connue, mais mise à jour impossible à court terme.
6. **Sauvegardes non testées** : fichiers présents, mais restauration incomplète ou inutilisable.
7. **USB et ordinateurs de maintenance** : transfert de logiciels malveillants ou de configurations erronées.
8. **Inventaire incomplet** : équipement inconnu, adresse non documentée ou service non autorisé.
9. **Surveillance inadaptée** : sondes actives susceptibles de perturber les équipements sensibles.

## 8. Les premières protections à mettre en place

### 8.1 Connaître les actifs

Constituer un inventaire approuvé : fabricant, modèle, fonction, emplacement, adresse IP, système d’exploitation ou firmware si connu, propriétaire, criticité, dépendances, modes d’accès et date de dernière vérification. Les informations inconnues doivent rester marquées « à confirmer » plutôt que d’être devinées.

### 8.2 Documenter les flux

Pour chaque échange, noter la source, la destination, le protocole, le sens, la justification métier, le propriétaire et la criticité. Autoriser les communications nécessaires plutôt que d’ouvrir une zone entière « au cas où ».

### 8.3 Segmenter le réseau

Séparer au minimum les fonctions qui n’ont pas besoin de communiquer directement. Utiliser des pare-feux ou des contrôles de frontière lorsque cela convient à la conception. Appliquer des règles strictes entre la DMZ industrielle et les zones de contrôle. Un VLAN seul n’est pas une frontière de sécurité suffisante si le routage autorise tout.

### 8.4 Maîtriser l’accès distant

L’accès fournisseur doit être approuvé, limité dans le temps, soumis à une identité individuelle, protégé par une authentification forte adaptée et enregistré. L’accès doit passer par un point de contrôle désigné ; ne pas exposer directement l’interface d’un PLC à Internet.

### 8.5 Sauvegarder et préparer la reprise

Sauvegarder les configurations réseau, les projets PLC, les programmes IHM, les configurations SCADA et les certificats nécessaires. Protéger les copies contre la modification non autorisée, conserver les versions, documenter les dépendances et vérifier périodiquement la restauration dans un environnement approprié.

### 8.6 Surveiller sans perturber

Privilégier les journaux disponibles, les fonctions de supervision approuvées, les ports SPAN ou des TAP conçus pour le besoin. Les scans actifs, tests de charge et sondes industrielles doivent être autorisés, évalués et testés avant utilisation. L’absence d’alerte n’est pas la preuve qu’un réseau est sûr.

## 9. Méthode de diagnostic sûre

Quand une IHM ne reçoit plus les données d’un automate, ne commence pas par redémarrer le contrôleur.

1. Noter l’heure, le symptôme, les alarmes et le périmètre touché.
2. Confirmer auprès de l’opérateur si le procédé est stable et si une procédure particulière s’applique.
3. Vérifier les changements récents : maintenance, câble, configuration, alimentation, adresse ou pare-feu.
4. Consulter les indicateurs déjà disponibles : état du lien, compteurs d’erreurs, journaux, état des services.
5. Comparer la situation à une référence connue et à la documentation réseau.
6. Toute action de correction doit être autorisée, réversible lorsque possible et coordonnée avec les responsables du procédé.
7. Après résolution, documenter la cause, la mesure, les tests et les actions préventives.

Un ping réussi vérifie seulement une partie de la connectivité IP ; il ne prouve pas que le protocole applicatif fonctionne ni que le système de contrôle est sain.

## 10. Travaux pratiques en environnement simulé

Tous les exercices ci-dessous utilisent des adresses fictives et des maquettes ou simulateurs. Ne les transpose pas sur une usine réelle sans autorisation formelle, analyse de risque et procédure de changement.

### TP 1 — Dessiner une petite architecture

**Contexte :** une station de traitement d’eau simulée comporte un PLC, une IHM, un serveur d’historisation et un poste bureautique.

Proposition de plan d’adressage fictif :

| Zone | Sous-réseau d’exemple | Actifs |
|---|---|---|
| Cellule de contrôle | `192.0.2.0/24` | PLC et IHM de laboratoire |
| Supervision site | `198.51.100.0/24` | Historien et supervision simulés |
| DMZ industrielle | `203.0.113.0/24` | Relais de transfert simulé |
| Réseau entreprise | autre réseau de laboratoire | Poste IT de démonstration |

Ces plages sont réservées à la documentation et aux exemples ; elles ne doivent pas servir à identifier des équipements de production.

**Travail demandé :** dessiner les zones, indiquer les fonctions, puis tracer les flux métier requis.

**Correction indicative :** le PLC communique avec l’IHM selon le protocole prévu par le constructeur ; l’historien reçoit les données via un chemin documenté ; le poste entreprise ne dispose pas d’accès direct au PLC ; les échanges entre entreprise et OT passent par des services explicitement autorisés dans la DMZ. La direction exacte des connexions doit être vérifiée dans la conception réelle.

### TP 2 — Créer un inventaire

Compléter les champs suivants pour cinq actifs simulés : identifiant, zone, adresse, rôle, propriétaire, protocole, criticité, accès d’administration, sauvegarde disponible, incertitudes.

**Correction attendue :** aucun champ critique ne doit être inventé. Les valeurs inconnues sont marquées « à confirmer » et associées à une action, un responsable et une échéance.

### TP 3 — Première matrice de flux

Élaborer une matrice comportant source, destination, service, sens, justification et propriétaire.

| Source | Destination | Service | Justification | Décision initiale |
|---|---|---|---|---|
| IHM de laboratoire | PLC simulé | protocole du banc | visualisation et commande simulées | autoriser seulement le flux documenté |
| Historien | serveur de données simulé | service approuvé | collecte des mesures | autoriser selon l’architecture validée |
| Poste bureautique | PLC | tout service | aucune justification fournie | refuser par défaut, puis analyser le besoin |
| Fournisseur externe | PLC | accès direct | pratique non maîtrisée | ne pas autoriser ; concevoir un accès contrôlé |

### TP 4 — Diagnostic d’une perte de communication

**Scénario :** l’IHM affiche des valeurs figées ; le PLC continue de fonctionner localement selon l’opérateur.

**Démarche de correction :** confirmer l’état du procédé, contrôler les alarmes et horodatages, vérifier les changements récents, examiner l’état du lien et les compteurs du switch, vérifier l’adressage et la route, puis analyser les logs ou une capture passive approuvée. Ne pas provoquer de redémarrage du PLC et ne pas modifier la logique de contrôle pour résoudre un problème réseau non compris.

## 11. Exercices corrigés

### Exercice 1
**Question :** quelle différence entre OT et IT ?

**Correction :** l’IT gère principalement les données et services d’information ; l’OT surveille ou influence un procédé physique. Les deux se recoupent, mais les changements OT doivent intégrer les conséquences sur le procédé, la disponibilité et la sûreté.

### Exercice 2
**Question :** un PLC et une IHM sont-ils la même chose ?

**Correction :** non. Le PLC exécute la logique de commande ; l’IHM présente des informations à l’opérateur et transmet des actions autorisées.

### Exercice 3
**Question :** une DMZ industrielle est-elle juste un VLAN ?

**Correction :** non. C’est une zone d’architecture avec des systèmes intermédiaires et des règles de communication contrôlées. Un VLAN peut contribuer à sa mise en œuvre, mais ne suffit pas à garantir la protection.

### Exercice 4
**Question :** pourquoi éviter de scanner un PLC de production sans préparation ?

**Correction :** certains équipements anciens ou sensibles peuvent réagir de manière inattendue à des volumes ou séquences de requêtes non prévus. Il faut une autorisation, une analyse d’impact, des tests et une procédure de retour arrière.

### Exercice 5
**Question :** Modbus TCP utilise-t-il toujours le port 502 ?

**Correction :** c’est le port par défaut courant, mais la configuration peut varier. Le port seul ne prouve pas la nature du service ; il faut confirmer avec l’inventaire et l’administrateur.

### Exercice 6
**Question :** une sauvegarde est-elle valide dès que le fichier existe ?

**Correction :** non. Elle doit être protégée, cohérente, documentée et testée par une restauration dans un cadre approprié.

### Exercice 7
**Question :** le ping prouve-t-il qu’une communication SCADA fonctionne ?

**Correction :** non. Il vérifie au mieux la connectivité IP ICMP entre deux points. Le service applicatif, les sessions, les droits et les données peuvent toujours être en panne.

### Exercice 8
**Question :** pourquoi ne pas laisser un fournisseur connecté en permanence ?

**Correction :** cela augmente la surface d’exposition, complique la révocation et réduit la traçabilité. L’accès doit être approuvé, limité dans le temps, individuel et journalisé.

## 12. Défi final corrigé

### Énoncé

Une petite usine possède deux automates, une IHM, un historien et un réseau bureautique. Un intervenant souhaite accéder depuis Internet au PLC pour accélérer les opérations de maintenance. L’équipe ignore si les sauvegardes des automates sont récentes et ne possède pas de diagramme de flux fiable.

Proposer un plan d’action initial sans interrompre la production.

### Correction détaillée

**Étape 1 — Stabiliser et comprendre.** Identifier le propriétaire opérationnel, le responsable automatisme et le référent sûreté. Confirmer le fonctionnement du procédé et les fenêtres de maintenance. Ne pas modifier la connectivité existante à l’aveugle.

**Étape 2 — Créer une vue fiable.** Inventorier automates, IHM, historien, switches, routeurs, pare-feu, comptes, protocoles et chemins d’administration. Reconstituer les flux à partir de la documentation, des configurations disponibles et d’une observation passive autorisée.

**Étape 3 — Évaluer les sauvegardes.** Vérifier quand et comment les projets PLC, configurations HMI et configurations réseau ont été sauvegardés. Organiser une validation de restauration dans un environnement de test ou selon une procédure approuvée.

**Étape 4 — Refuser l’exposition directe.** Ne pas publier l’interface d’administration du PLC sur Internet. Concevoir un accès distant via une zone intermédiaire ou un bastion contrôlé, avec identité individuelle, MFA si compatible, autorisation limitée dans le temps, journalisation et supervision par le personnel local.

**Étape 5 — Définir les règles de flux.** N’autoriser que les communications justifiées entre zones. Documenter chaque règle, son propriétaire et son mécanisme de revue.

**Étape 6 — Tester et maintenir.** Tester le parcours d’accès dans une maquette ou une fenêtre approuvée, définir une procédure de retour arrière, informer l’équipe opérationnelle et conserver les traces de changement.

**Étape 7 — Mesurer la progression.** Suivre le pourcentage d’actifs inventoriés, la couverture de sauvegarde testée, le nombre d’accès tiers permanents, le nombre de flux sans justification et les incidents liés aux changements.

La priorité n’est pas d’installer un outil rapidement : c’est de réduire le risque sans introduire une panne ou un état dangereux.

## 13. Glossaire

- **Actionneur :** équipement qui agit sur le procédé, par exemple une vanne ou un moteur.
- **API / PLC :** automate programmable industriel.
- **DCS :** système de contrôle distribué.
- **DMZ industrielle :** zone intermédiaire entre réseaux de niveaux de confiance différents.
- **HMI / IHM :** interface homme-machine.
- **ICS :** systèmes de contrôle industriels.
- **OT :** technologies opérationnelles.
- **RTU :** unité terminale distante.
- **SCADA :** supervision, acquisition de données et commande supervisée.
- **SIS :** système instrumenté de sécurité.
- **TAP / SPAN :** mécanismes de copie du trafic réseau pour observation.
- **VLAN :** réseau local virtuel ; mécanisme de segmentation de niveau 2.

## 14. Références techniques

1. NIST, *SP 800-82 Rev. 3 — Guide to Operational Technology (OT) Security* (publication finale, 2023) : https://csrc.nist.gov/pubs/sp/800/82/r3/final
2. ISA, *ISA/IEC 62443 Series of Standards* : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
3. CISA et partenaires, *Foundations for OT Cybersecurity: Asset Inventory Guidance* : https://www.cisa.gov/sites/default/files/2025-08/joint-guide-foundations-for-OT-cybersecurity-asset-inventory-guidance_508c.pdf
4. UK NCSC et partenaires, *Creating and maintaining a definitive view of your OT architecture* : https://www.ncsc.gov.uk/collection/operational-technology/definitive-architecture-view

Les références décrivent des orientations et des bonnes pratiques. Les contrôles précis doivent être adaptés à l’installation, aux exigences du secteur, aux contrats, aux normes applicables et à l’analyse de risques.
