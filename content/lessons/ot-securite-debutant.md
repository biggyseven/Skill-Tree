# Cybersécurité OT — Débutant

## Mise en contexte : protéger un système qui agit sur le monde physique

Dans une usine, une station de pompage, un réseau électrique ou un système de traitement d'eau, des équipements informatiques ne servent pas seulement à stocker des fichiers. Ils surveillent et commandent un procédé physique : température, pression, vitesse d'un moteur, position d'une vanne, niveau d'une cuve ou état d'un convoyeur.

La **technologie opérationnelle (OT, Operational Technology)** regroupe les systèmes numériques qui surveillent ou commandent des équipements physiques. La cybersécurité OT vise donc à réduire le risque cyber tout en préservant la sécurité des personnes, l'environnement, la qualité du produit et la continuité du procédé.

> **Principe essentiel :** une action acceptable sur un serveur bureautique peut être dangereuse dans un système industriel. Avant toute modification, tout test ou toute réponse à incident, il faut comprendre le procédé, les conséquences physiques possibles et les procédures d'exploitation sûres.

## 1. Objectifs pédagogiques

À la fin du cours, tu sauras :

- distinguer IT, OT, ICS, SCADA, DCS, PLC/API et IHM/HMI ;
- expliquer pourquoi la disponibilité, l'intégrité du procédé et la sûreté sont prioritaires en OT ;
- reconnaître les menaces et vulnérabilités OT courantes ;
- lire un schéma simple inspiré du modèle Purdue ;
- comprendre les principes de segmentation, de moindre privilège et d'accès distant contrôlé ;
- préparer un inventaire d'actifs et une première matrice de flux ;
- proposer une réponse prudente à un incident sans mettre en danger le procédé.

## 2. IT, OT et systèmes de contrôle industriel

### 2.1 Différences de priorités

| Dimension | Environnement IT courant | Environnement OT |
|---|---|---|
| Objectif dominant | Traiter et protéger l'information | Surveiller ou contrôler un procédé physique |
| Critères typiques | Confidentialité, intégrité, disponibilité | Sécurité des personnes, disponibilité, intégrité du contrôle, qualité et environnement |
| Fenêtre de maintenance | Souvent planifiable fréquemment | Parfois limitée à un arrêt industriel planifié |
| Durée de vie | Renouvellement relativement fréquent | Équipements parfois exploités pendant de nombreuses années |
| Effet d'une interruption | Perte de service ou de données | Arrêt de production, dommage matériel, risque humain ou environnemental |
| Tolérance aux changements | Variable | Changement potentiellement très contraint par la validation du procédé |

La confidentialité reste importante en OT, par exemple pour les recettes, les paramètres de production ou les plans. Mais elle ne doit pas conduire à sacrifier la sûreté ou la disponibilité sans analyse de risque.

### 2.2 Les principaux composants

- **Capteur :** mesure une grandeur physique, par exemple la pression.
- **Actionneur :** produit une action physique, par exemple ouvrir une vanne.
- **PLC/API :** contrôleur logique programmable exécutant une logique de commande.
- **RTU :** unité terminale distante souvent utilisée dans des sites distribués.
- **IHM/HMI :** interface permettant à un opérateur de visualiser l'état et d'effectuer des commandes autorisées.
- **SCADA :** système de supervision et d'acquisition de données reliant souvent plusieurs sites ou unités.
- **DCS :** système de contrôle distribué employé notamment dans les procédés continus.
- **Historian :** collecte et conserve des données de procédé dans le temps.
- **Station d'ingénierie :** poste utilisé pour programmer, diagnostiquer ou maintenir les contrôleurs.
- **SIS :** système instrumenté de sécurité, lorsqu'il existe, conçu pour réduire certains risques de procédé et soumis à des exigences spécifiques.

Le système de contrôle et le système de sécurité instrumenté ne doivent pas être confondus. Un SIS n'est pas simplement une fonction logicielle de cybersécurité ; il relève de l'ingénierie de sûreté et doit être protégé selon sa conception certifiée et les procédures du site.

## 3. Schéma d'une installation industrielle

```text
              Réseau d'entreprise (IT)
                       |
             Zone d'échange contrôlée
                       |
              DMZ industrielle (IDMZ)
            collecte / relais / bastion
                       |
            Pare-feu et flux autorisés
                       |
            Supervision et SCADA (OT)
                       |
          Réseau de contrôle / automate
                       |
             PLC/API et E/S déportées
                       |
                Capteurs / actionneurs
                       |
                  Procédé physique
```

Ce schéma est une représentation pédagogique, pas une architecture universelle. Les couches exactes dépendent du secteur, du fabricant, des contraintes de disponibilité et de l'analyse de risque. Une séparation dessinée sur un diagramme n'apporte de sécurité que si elle est appliquée réellement par des contrôles techniques et opérationnels.

## 4. Le modèle Purdue : une carte, pas une règle absolue

Le modèle Purdue est couramment utilisé pour parler des niveaux d'un environnement industriel :

```text
Niveau 5 : services d'entreprise / accès externes
Niveau 4 : systèmes IT d'entreprise
        | séparation IT/OT et zone tampon
Niveau 3.5 : DMZ industrielle (IDMZ)
Niveau 3 : opérations de site, supervision, historian
Niveau 2 : supervision locale, IHM, contrôle de cellule
Niveau 1 : contrôleurs, PLC/API, RTU
Niveau 0 : procédé physique, capteurs, actionneurs
```

Certaines représentations ajoutent des sous-niveaux ou modifient l'organisation. Les architectures modernes peuvent être distribuées, virtualisées ou organisées en cellules. Il ne faut donc pas attribuer automatiquement un niveau à un produit sans examiner sa fonction et ses communications.

Le Purdue Model aide à identifier les frontières, mais ne remplace pas une analyse par **zones et conduits**. Deux machines de niveau 3 peuvent avoir des fonctions, des risques et des droits de communication différents.

## 5. Menaces et vulnérabilités courantes

### 5.1 Menace, vulnérabilité et risque

- **Menace :** événement ou acteur susceptible de causer un dommage.
- **Vulnérabilité :** faiblesse exploitable ou susceptible d'être utilisée.
- **Conséquence :** effet sur les personnes, la production, l'environnement, les équipements ou les données.
- **Risque :** combinaison de la vraisemblance et de la gravité des conséquences, compte tenu des contrôles existants.

Un exemple : une station d'ingénierie encore active avec un compte partagé et un accès distant permanent présente une exposition. Le risque exact dépend notamment des privilèges, des chemins réseau, de l'état du procédé et des conséquences d'une commande incorrecte.

### 5.2 Exemples fréquents

1. Accès distant fournisseur permanent ou mal contrôlé.
2. Comptes partagés, mots de passe par défaut ou privilèges trop élevés.
3. Réseau plat où les postes bureautiques peuvent communiquer directement avec les automates.
4. Support USB non contrôlé utilisé pour transférer des fichiers.
5. Stations d'ingénierie obsolètes ou insuffisamment protégées.
6. Sauvegardes connectées en permanence au même environnement que les systèmes de production.
7. Actifs inconnus, adresses et propriétaires non documentés.
8. Modifications de configuration réalisées sans validation ni journal de changement.
9. Protocoles industriels conçus à l'origine pour des réseaux de confiance et ne fournissant pas toujours authentification ou chiffrement.
10. Mauvaise séparation entre l'environnement OT, les services IT et les prestataires externes.

L'absence de chiffrement ne signifie pas qu'il faut remplacer immédiatement un équipement. Dans certains cas, une segmentation stricte, une limitation des accès et une surveillance passive permettent de réduire le risque sans introduire un changement risqué dans le contrôleur.

## 6. Protocoles industriels : connaître les risques sans les confondre

On peut rencontrer Modbus TCP, EtherNet/IP, PROFINET, OPC UA, DNP3, BACnet ou des protocoles propriétaires. Ils n'ont ni les mêmes fonctions ni les mêmes mécanismes de sécurité.

- Un protocole de contrôle peut échanger des variables de procédé ou des commandes.
- Un protocole de supervision peut transporter des mesures, des alarmes ou des consignes.
- Certains protocoles modernes disposent de mécanismes de sécurité optionnels ou intégrés ; leur présence dépend des produits, des versions et de la configuration.
- Le port réseau seul ne prouve pas qu'un service est sûr, nécessaire ou correctement configuré.

**Bonne pratique :** documenter le couple source-destination, le service, le sens d'initiation, le besoin métier, le responsable et la méthode de validation. N'active jamais un service ou un mécanisme de sécurité sur un actif industriel en production sans vérifier la compatibilité fournisseur et la procédure de changement.

## 7. Les premières protections à mettre en place

### 7.1 Inventaire des actifs

Commencer par un inventaire utile à l'exploitation :

| Champ | Exemple fictif |
|---|---|
| Identifiant | PLC-POMPE-01 |
| Fonction | Contrôle de pompe P-101 |
| Adresse / segment | 10.20.10.11 / cellule pompage |
| Fabricant et modèle | Modèle déclaré par l'équipe maintenance |
| Version / firmware | Valeur vérifiée sans mise à niveau |
| Propriétaire | Responsable automatisme |
| Criticité | Élevée, selon l'analyse du procédé |
| Dépendances | IHM-POMPAGE-01, historian local |
| Accès distant | Aucun / contrôlé via bastion |
| Sauvegarde | Projet automate archivé et validé |

Ne fais pas d'inventaire en lançant directement un scan agressif sur des automates inconnus. Utilise d'abord les schémas, configurations réseau, exports d'équipements et observations passives approuvées. Tout test actif doit être autorisé et évalué avec les responsables OT.

### 7.2 Segmentation

La segmentation limite les communications entre groupes de systèmes. On peut séparer, selon le besoin :

- les postes bureautiques ;
- la DMZ industrielle ;
- la supervision ;
- les cellules d'automates ;
- les stations d'ingénierie ;
- les dispositifs de sécurité ;
- les accès prestataires.

Le principe directeur est **refuser par défaut, autoriser explicitement le strict nécessaire**, avec validation par le responsable du procédé et test avant mise en production.

### 7.3 Accès distant

Un accès distant acceptable comporte au minimum :

- un besoin métier précis et une autorisation nominative ;
- une authentification forte, idéalement multifacteur ;
- un point d'entrée contrôlé, par exemple un bastion dans la DMZ ;
- des droits limités à la cible et à la durée nécessaires ;
- une journalisation des connexions et actions ;
- une validation des outils et fichiers transférés ;
- une procédure de fermeture de session et de révocation ;
- un plan de fonctionnement local si la liaison distante tombe.

Éviter les connexions directes permanentes depuis Internet vers une IHM ou un automate. Un VPN seul ne remplace ni l'autorisation, ni la séparation des réseaux, ni la surveillance.

### 7.4 Comptes et mots de passe

Chaque personne devrait avoir un compte nominatif lorsque la technologie le permet. Réduire les privilèges permanents, désactiver les comptes inutilisés après validation, protéger les comptes de service et gérer les secrets selon une procédure sûre. Les exceptions des équipements anciens doivent être documentées et compensées par d'autres contrôles.

### 7.5 Sauvegardes et restauration

Sauvegarder ne suffit pas : il faut pouvoir restaurer dans des conditions maîtrisées.

- conserver les projets PLC/API, paramètres réseau et configurations système ;
- conserver plusieurs versions approuvées ;
- séparer les sauvegardes des systèmes de production ;
- protéger au moins une copie contre la modification ou la suppression ;
- documenter les licences, dépendances, firmwares et outils de restauration ;
- tester les restaurations dans un environnement approprié ;
- faire valider la cohérence fonctionnelle avant de reconnecter le système au procédé.

### 7.6 Surveillance prudente

La surveillance passive peut collecter les métadonnées de trafic via un port miroir ou une TAP adaptée, sans envoyer de requêtes aux équipements. Elle aide à repérer les nouveaux actifs, les conversations inattendues et les écarts au fonctionnement habituel. Elle doit être dimensionnée et testée : un dispositif mal inséré peut perturber la disponibilité.

## 8. Exemple de matrice de flux minimale

Site fictif :

| Source | Destination | Besoin | Décision de conception |
|---|---|---|---|
| IHM-01 | PLC-01 | Lecture et commande opérateur documentées | Autoriser uniquement le service requis, après validation fournisseur |
| Historian-01 | Collecteur DMZ | Export de données de procédé | Flux unidirectionnel si l'architecture le permet ; sinon règles strictes |
| Bastion-DMZ | Station d'ingénierie | Maintenance approuvée | Accès nominatif, temporaire et journalisé |
| Réseau bureautique | PLC-01 | Aucun besoin direct identifié | Refuser |
| Internet | IHM-01 | Aucun besoin direct | Refuser |

Les noms de services et ports ne sont pas universels ; ils doivent être confirmés à partir de la documentation de la version réellement installée et d'une capture autorisée du trafic.

## 9. Procédure de changement sûre

Avant un changement cyber ou réseau :

1. Décrire le problème et le résultat attendu.
2. Identifier les équipements, les flux et les dépendances concernés.
3. Faire évaluer l'effet sur la sûreté, la disponibilité et le contrôle.
4. Obtenir l'autorisation du responsable OT et, si nécessaire, du responsable sécurité/sûreté.
5. Sauvegarder la configuration avant changement.
6. Tester en laboratoire ou hors production lorsque c'est possible.
7. Définir un plan de retour arrière et des critères d'arrêt.
8. Appliquer pendant une fenêtre approuvée.
9. Vérifier les fonctions de contrôle et les alarmes avec les opérateurs.
10. Documenter le résultat, la configuration finale et les écarts.

Un changement de pare-feu peut bloquer un paquet essentiel à une fonction de contrôle. Un redémarrage de poste peut interrompre la supervision. Il faut considérer les dépendances avant d'agir.

## 10. Que faire en cas d'incident ?

Si tu observes un comportement inhabituel :

- avertir immédiatement le responsable d'exploitation et suivre le plan incident du site ;
- ne pas arrêter un automate ou un processus à l'aveugle ;
- ne pas lancer de scan, de nettoyage ou de mise à jour improvisée ;
- conserver les heures, alarmes, journaux et observations utiles ;
- protéger les personnes en priorité et appliquer les procédures de sécurité du procédé ;
- limiter les communications suspectes uniquement selon une décision autorisée, en évaluant les effets sur le contrôle ;
- maintenir une chaîne de conservation des preuves adaptée ;
- faire coordonner les équipes OT, IT, cybersécurité, maintenance et sûreté.

L'objectif n'est pas de préserver un serveur à tout prix, mais de maîtriser les conséquences pour le procédé et de rétablir un état sûr.

## 11. Travaux pratiques guidés

### TP 1 — Construire un inventaire initial

**Contexte :** une petite unité possède un PLC de pompage, une IHM, un historian et une station d'ingénierie. Les schémas sont incomplets.

**Travail demandé :** créer les champs d'inventaire de la section 7.1 et dresser les questions à poser avant toute intervention.

**Correction attendue :** chaque actif reçoit un identifiant, une fonction, un propriétaire, une criticité provisoire, ses dépendances, sa version connue et son statut de sauvegarde. Les valeurs inconnues restent marquées « à vérifier » : on ne les invente pas. Le responsable automatisme valide le fonctionnement et les dépendances ; l'équipe réseau confirme les segments et les chemins de communication.

### TP 2 — Repérer les frontières de confiance

**Topologie initiale :** le réseau bureautique et les automates partagent un même VLAN ; le fournisseur dispose d'un accès VPN vers une station d'ingénierie.

**Travail demandé :** dessiner une architecture cible logique et expliquer les changements.

**Correction attendue :** séparer les zones IT et OT, créer une DMZ industrielle pour les services d'échange, positionner un point d'accès distant contrôlé, limiter les flux vers la station d'ingénierie, journaliser les sessions et supprimer l'accès direct inutile. Le plan de migration doit prévoir des tests, une fenêtre de maintenance et un retour arrière.

### TP 3 — Examiner une demande fournisseur

Le fournisseur demande un accès permanent à tous les contrôleurs « pour faciliter le support ».

**Travail demandé :** rédiger une décision et les conditions d'un accès temporaire.

**Correction attendue :** refuser l'accès générique et permanent. Définir la cible exacte, le motif, l'approbateur, la durée, le compte nominatif, l'authentification forte, le bastion, les transferts autorisés, la journalisation et la procédure de révocation. Toute commande de programmation nécessite une procédure de changement validée.

### TP 4 — Exercice de table en cas d'alerte

Un opérateur signale des alarmes inhabituelles et un poste IT affiche un message de rançon. Il est impossible de savoir si les réseaux sont liés.

**Travail demandé :** lister les cinq premières actions.

**Correction attendue :** protéger les personnes et le procédé ; alerter le responsable d'exploitation et l'équipe incident ; ne pas redémarrer les équipements OT ; préserver les journaux et heures ; examiner les chemins de communication avec l'équipe réseau ; prendre toute mesure d'isolement selon une décision coordonnée et fondée sur l'impact. Les restaurations ne commencent qu'avec une stratégie validée.

## 12. Exercices corrigés

### Exercice 1
**Question :** pourquoi un pare-feu OT ne doit-il pas être configuré uniquement selon les règles IT habituelles ?

**Réponse :** les flux de contrôle ont des exigences particulières de disponibilité, de temporisation et de compatibilité. Une règle trop large est dangereuse, mais une règle trop restrictive peut interrompre une fonction physique. Chaque flux doit être compris, documenté, testé et validé par l'exploitation.

### Exercice 2
**Question :** le modèle Purdue garantit-il à lui seul une architecture sécurisée ?

**Réponse :** non. Il aide à représenter les fonctions et frontières. La sécurité dépend de la segmentation réelle, des règles de flux, des identités, de la surveillance, des procédures et de la gestion des risques.

### Exercice 3
**Question :** une IHM n'est pas accessible depuis Internet. Est-elle forcément protégée ?

**Réponse :** non. Elle peut rester exposée à des comptes faibles, à un poste compromis, à un accès fournisseur ou à un réseau plat. Il faut étudier tous les chemins, pas seulement l'accès Internet direct.

### Exercice 4
**Question :** pourquoi privilégier l'observation passive lors d'un premier inventaire OT ?

**Réponse :** certains équipements anciens ou sensibles réagissent mal aux scans actifs ou à des requêtes inattendues. L'observation passive et la documentation réduisent le risque de perturbation, même si elles peuvent laisser des actifs silencieux non détectés.

### Exercice 5
**Question :** quelle est la différence entre sauvegarde et restauration validée ?

**Réponse :** une sauvegarde est une copie ; une restauration validée prouve que les fichiers, versions, licences, paramètres et dépendances permettent de rétablir la fonction sans créer de risque pour le procédé.

### Exercice 6
**Question :** à quoi sert la DMZ industrielle ?

**Réponse :** elle fournit une zone tampon contrôlée entre les réseaux d'entreprise et les systèmes OT, par exemple pour un relais de transfert, un bastion ou une collecte de données. Elle ne doit pas devenir un pont libre entre les zones.

### Exercice 7
**Question :** que signifie le moindre privilège pour un prestataire ?

**Réponse :** n'accorder que les droits, les systèmes et la durée strictement nécessaires à l'intervention approuvée, puis révoquer l'accès et vérifier la trace laissée.

### Exercice 8
**Question :** que faire avant de débrancher un câble suspect dans une installation ?

**Réponse :** évaluer la fonction du lien, les dépendances et les conséquences possibles avec l'exploitation. Appliquer ensuite le plan d'incident et la procédure autorisée ; ne pas improviser une coupure qui pourrait interrompre le contrôle ou un système de sécurité.

## 13. Défi final corrigé

### Situation

Une petite usine dispose du réseau bureautique `10.10.0.0/16`, d'une supervision `10.20.10.0/24`, d'une cellule de contrôleurs `10.20.20.0/24` et d'une station fournisseur accessible à distance. Les automates n'ont pas été inventoriés complètement, les sauvegardes sont conservées sur un partage accessible depuis le réseau bureautique et aucune matrice de flux n'existe.

### Mission

Proposer les premières mesures de cybersécurité en donnant la priorité à la sûreté et à la continuité de production.

### Correction détaillée

1. **Établir la gouvernance :** nommer le responsable de procédé, le responsable OT et le coordinateur cybersécurité ; déterminer les personnes autorisées à approuver un changement.
2. **Créer un inventaire progressif :** utiliser les documents disponibles, les configurations et une observation passive autorisée. Marquer les données incertaines comme telles.
3. **Cartographier les flux :** documenter les communications entre IHM, PLC, historian, station d'ingénierie et services d'entreprise ; identifier les flux nécessaires et les flux inconnus.
4. **Protéger les accès distants :** suspendre les accès non nécessaires selon une procédure validée ; remplacer le modèle d'accès générique par un accès nominatif, temporaire, authentifié fortement, via une zone intermédiaire contrôlée.
5. **Concevoir la segmentation :** séparer IT, DMZ industrielle, supervision et cellules de contrôle. N'appliquer les règles qu'après validation des flux et plan de retour arrière.
6. **Sécuriser les sauvegardes :** établir une copie indépendante, protéger les accès en écriture et planifier un test de restauration hors production.
7. **Surveiller :** établir une base de référence passive et conserver des journaux centralisés, en vérifiant que la collecte n'affecte pas les équipements.
8. **Préparer l'incident :** rédiger une procédure de notification, d'analyse, de décision d'isolement, de restauration et de reprise sûre.
9. **Mesurer les progrès :** suivre le pourcentage d'actifs connus, les accès distants revus, les flux justifiés, les sauvegardes restaurées en test et les incidents simulés.

L'erreur à éviter serait de déployer immédiatement une série de blocages réseau sans connaître les communications indispensables. La priorité est d'obtenir une vision crédible du procédé et de ses flux, puis d'appliquer des contrôles progressifs et vérifiés.

## 14. Glossaire

- **API/PLC :** automate programmable industriel.
- **DCS :** système de contrôle distribué.
- **DMZ/IDMZ :** zone tampon entre domaines de confiance ; IDMZ désigne la DMZ industrielle.
- **ICS :** système de contrôle industriel.
- **IHM/HMI :** interface homme-machine.
- **Historian :** base spécialisée dans l'historique des données de procédé.
- **OT :** technologie opérationnelle.
- **Purdue Model :** modèle de référence pour organiser les fonctions d'une architecture industrielle.
- **RTU :** unité terminale distante.
- **SIS :** système instrumenté de sécurité.
- **TAP / SPAN :** méthodes de copie du trafic à des fins d'observation.
- **Zone et conduit :** regroupement d'actifs ayant des besoins de sécurité communs et chemin de communication contrôlé entre zones.

## 15. Références techniques

1. NIST, *SP 800-82 Rev. 3 — Guide to Operational Technology (OT) Security*, version finale publiée en septembre 2023 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
2. NIST, *SP 800-82 Rev. 4 — Initial Public Draft*, projet publié le 21 septembre 2026, non finalisé à la date de ce cours ; commentaires annoncés jusqu'au 30 novembre 2026 : https://csrc.nist.gov/pubs/sp/800/82/r4/ipd
3. ISA, série de normes ISA/IEC 62443 sur la cybersécurité des systèmes d'automatisation et de contrôle industriels : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
4. CISA, *Cross-Sector Cybersecurity Performance Goals* : https://www.cisa.gov/cross-sector-cybersecurity-performance-goals
5. MITRE, *ATT&CK for ICS* — base de connaissances sur les comportements adverses observés dans les environnements de contrôle industriel : https://attack.mitre.org/matrices/ics/
6. Australian Cyber Security Centre, *Secure connectivity principles for Operational Technology (OT)*, janvier 2026 : https://www.cyber.gov.au/publication/secure-connectivity-principles-for-operational-technology

Les références fournissent des principes de conception ; elles ne remplacent pas les procédures du site, les instructions du constructeur, la réglementation applicable ni une analyse de risque spécifique au procédé.
