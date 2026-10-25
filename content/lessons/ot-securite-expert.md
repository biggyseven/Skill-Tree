# Cybersécurité OT et Purdue Model — Niveau expert

## Mise en contexte : de la segmentation à la résilience cyberphysique

Au niveau expert, la cybersécurité OT ne se réduit ni à la pose de pare-feu ni à l'installation d'un outil de détection. Elle consiste à concevoir, exploiter et améliorer une architecture qui résiste aux erreurs, aux compromissions et aux pannes, tout en gardant la maîtrise du procédé physique.

Ce cours traite de l'architecture Purdue et de ses limites, des zones et conduits, de la modélisation du risque cyberphysique, de la confiance et des accès, de la détection orientée procédé, de la réponse coordonnée, de la résilience et de la gouvernance. Les exemples sont défensifs et conçus pour des environnements de formation, de conception ou d'évaluation autorisée.

> **Principe expert :** la mesure qui réduit le risque cyber mais crée un risque de procédé plus élevé n'est pas une bonne mesure. Toute décision doit être évaluée sur la sécurité des personnes, l'état sûr, la continuité essentielle, la récupération et la qualité des preuves.

## 1. Compétences visées

À la fin du cours, tu sauras :

- évaluer une architecture OT en combinant Purdue, zones/conduits et analyse de risque ;
- définir des exigences de sécurité mesurables par zone et par fonction ;
- construire une architecture de connectivité maîtrisée pour l'administration, les données et les fournisseurs ;
- concevoir des cas de détection basés sur les actifs, les flux, les actions d'ingénierie et les événements procédé ;
- interpréter des comportements ATT&CK for ICS dans une logique de détection et de réduction du risque ;
- élaborer une stratégie de réponse aux incidents qui préserve la sûreté ;
- définir des objectifs de récupération et tester la résilience ;
- établir une feuille de route avec indicateurs, responsables et preuves de contrôle.

## 2. Purdue Model : valeur et limites

### 2.1 Utiliser Purdue comme modèle fonctionnel

Une représentation courante place le procédé et les capteurs au niveau 0, les contrôleurs au niveau 1, la supervision locale au niveau 2, les opérations de site au niveau 3, les services IT au niveau 4 et les services d'entreprise ou externes au niveau 5. Une DMZ industrielle, souvent représentée autour du niveau 3.5, sert de frontière d'échange.

```text
 Services externes / entreprise                 Niveau 5
        | besoins strictement définis
 Services IT et applications d'entreprise       Niveau 4
        |
 +-------------------------------------------------------+
 | DMZ industrielle : relais, bastion, réplication, logs |  ~3.5
 +-------------------------------------------------------+
        |
 Opérations et supervision de site             Niveau 3
        |
 Supervision locale / cellules                 Niveau 2
        |
 PLC/API, RTU, contrôleurs                     Niveau 1
        |
 Capteurs, actionneurs, procédé                Niveau 0
```

Cette représentation doit être adaptée aux architectures distribuées, à l'edge, au cloud industriel, aux réseaux sans fil, aux fonctions de sécurité et aux systèmes du constructeur. Certains composants peuvent traverser plusieurs niveaux du point de vue logique ; le diagramme fonctionnel ne décrit pas automatiquement la topologie réelle.

### 2.2 Erreurs d'interprétation courantes

- considérer qu'un équipement est sûr simplement parce qu'il se trouve à un niveau inférieur ;
- supposer qu'un seul pare-feu entre niveaux suffit ;
- autoriser tout le trafic entre deux réseaux d'un même niveau ;
- confondre une DMZ avec un simple VLAN ;
- appliquer les mêmes exigences à une cellule de contrôle de processus et à un poste de reporting ;
- considérer qu'un trafic sortant d'une zone OT est toujours sans risque ;
- traiter chaque équipement d'une même couche comme s'il avait la même criticité et les mêmes privilèges.

### 2.3 Compléter Purdue par les zones et conduits

L'approche ISA/IEC 62443 consiste à regrouper les actifs dans des zones présentant des exigences de sécurité communes et à définir les conduits autorisés entre elles. La segmentation doit refléter les fonctions, les conséquences de compromission, les besoins de communication et les capacités réelles des équipements.

Exemple de zones : contrôle de cellule A, contrôle de cellule B, station d'ingénierie, supervision de site, services de données, zone de sécurité instrumentée, DMZ industrielle et accès distant. Une zone peut se trouver dans un niveau Purdue et être séparée en sous-zones si le risque le justifie.

## 3. Modélisation du risque cyberphysique

### 3.1 Partir des conséquences

L'analyse doit relier les chemins numériques au procédé :

```text
Actif / accès exposé
        |
Capacité ou privilège compromis
        |
Action possible dans le système de contrôle
        |
Effet sur les variables / séquences du procédé
        |
Conséquence : personne, environnement, équipement, production
```

Cette chaîne n'affirme pas que toute compromission donne un contrôle direct. Les interverrouillages, les limites physiques, les procédures et les systèmes instrumentés de sécurité peuvent modifier les scénarios. Ils doivent être analysés par les spécialistes compétents sans supposer qu'ils neutralisent tous les scénarios cyber.

### 3.2 Fiche de scénario

Pour chaque scénario, documenter : actif initial ; chemin réseau et identité ; préconditions ; fonction touchée ; effets plausibles ; barrières existantes ; hypothèses ; indice de détection ; méthode de confinement sûre ; dépendances de reprise ; propriétaire ; risque résiduel et date de révision.

### 3.3 Exemple de scénario

**Scénario :** compte d'un prestataire compromis puis utilisé pour une session de maintenance non planifiée.

- **Chemin :** accès distant → bastion → station d'ingénierie → zone de contrôle autorisée.
- **Conséquence possible :** changement non autorisé de configuration, interruption de supervision ou indisponibilité de maintenance.
- **Prévention :** compte nominatif, MFA, accès activé sur demande, cible unique, privilège limité, séparation entre administration et compte quotidien.
- **Détection :** connexion hors fenêtre, destination inhabituelle, transfert de fichier inattendu, changement de projet sans ordre de travail.
- **Réponse :** vérifier le procédé avec les opérateurs, stopper ou révoquer la session après évaluation de l'impact, préserver les journaux et comparer les configurations à la version approuvée.
- **Récupération :** restaurer seulement après validation d'une version connue et vérification fonctionnelle.

Le scénario doit être traité comme une hypothèse de risque, pas comme une recette d'attaque. Le travail de l'équipe est de fermer les chemins inutiles et de détecter les actions inattendues.

## 4. Architecture défendable

### 4.1 Architecture logique de référence

```text
        IT / identités d'entreprise / services partagés
                            |
                  Pare-feu IT vers DMZ
                            |
       +-----------------------------------------------+
       |                 DMZ industrielle              |
       | bastion | relais de fichiers | réplica data   |
       | collecteur de logs | accès distant contrôlé   |
       +-----------------------------------------------+
                            |
                  Pare-feu DMZ vers OT
                            |
               Services de supervision du site
                            |
             +--------------+--------------+
             |                             |
      Zone de contrôle A              Zone de contrôle B
      IHM / PLC / E/S                  IHM / PLC / E/S
             |                             |
       Procédé A                      Procédé B

   Zone SIS / sécurité instrumentée : séparation et exigences spécifiques
```

Ce schéma est une proposition de principe. La séparation et l'indépendance d'un SIS relèvent des exigences de sûreté du système et de la conception du fournisseur ; elles ne peuvent pas être garanties par un schéma cyber générique.

### 4.2 Exigences par conduit

Pour chaque conduit, définir :

- source et destination précises ;
- initiateur et direction des sessions ;
- services et commandes autorisés ;
- besoin et propriétaire fonctionnel ;
- exigences d'authentification, d'intégrité et de confidentialité ;
- contrôle de contenu ou médiation si applicable ;
- journalisation, alertes et rétention ;
- traitement d'une perte de liaison ;
- stratégie de test et de retour arrière ;
- date de révision et critères de retrait.

La règle la plus sûre est la règle la plus précise qui répond au besoin, mais une politique restrictive doit être vérifiée contre toutes les séquences normales du procédé, y compris démarrage, arrêt, maintenance, bascule et reprise après incident.

### 4.3 Flux de données et flux de commande

Distinguer les besoins de remontée de données, les flux d'ingénierie et les flux de commande. La séparation logique peut être renforcée par des relais, des passerelles de médiation et, lorsque c'est adapté au besoin et évalué par les équipes OT, des architectures de transfert unidirectionnel. Le sens du flux ne doit jamais être supposé à partir du nom d'un service : les sessions et dépendances sont à vérifier.

### 4.4 Accès distant à haute assurance

Une architecture mature définit les identités, l'approbation, la durée, la cible, le contexte de travail, le point de médiation, la journalisation, le transfert de fichiers, le contrôle des privilèges et la révocation. Les accès d'urgence doivent eux aussi être documentés, testés et audités ; « urgence » ne doit pas devenir un accès permanent non contrôlé.

L'accès fournisseur ne devrait pas disposer d'une route générale vers toute la zone OT. Les tiers doivent être rattachés à une cible, une tâche, un créneau et une responsabilité. Les sessions privilégiées peuvent être enregistrées selon la politique, la réglementation et les obligations de confidentialité applicables.

## 5. Identité, confiance et cycle de vie des accès

### 5.1 Zero Trust adapté à l'OT

Les principes de vérification explicite, de moindre privilège et de réduction de la confiance implicite sont utiles, mais ne se traduisent pas par l'installation de contrôles qui rompent un protocole industriel critique. Les décisions de confiance doivent prendre en compte l'identité, la fonction de l'actif, la zone, le contexte de maintenance, l'état de la connexion et les exigences de disponibilité.

### 5.2 Comptes privilégiés et exceptions legacy

Une cible robuste peut inclure : comptes individuels, MFA à la frontière d'accès, séparation des comptes, gestion contrôlée des secrets, élévation temporaire, droits par rôle, suppression des comptes abandonnés, journalisation des sessions et inventaire des dépendances. Les appareils incapables de prendre en charge ces fonctions nécessitent des compensations explicites : accès médié, restriction des chemins, contrôle physique, surveillance et plan de remplacement.

### 5.3 Gestion des secrets

Ne pas intégrer des secrets permanents dans des scripts, documents partagés ou configurations accessibles largement. Prévoir stockage contrôlé, rotation compatible avec les équipements, procédures d'urgence, protection des clés et certificats, inventaire des dépendances et révocation testée. La rotation non planifiée d'un secret partagé par plusieurs fonctions peut interrompre une opération ; elle doit être conduite selon le plan de changement.

## 6. Détection orientée OT

### 6.1 Construire une référence de fonctionnement

La référence devrait couvrir plusieurs modes : production normale, démarrage, arrêt, maintenance, bascule, sauvegarde et reprise. Elle associe les actifs, les communications, les utilisateurs, les horaires et, lorsque les données sont disponibles, les événements de procédé. Une référence réduite à une journée de fonctionnement peut manquer des opérations rares mais légitimes.

### 6.2 Exemples de cas de détection

| Cas de détection | Signal | Contexte de validation | Réponse initiale sûre |
|---|---|---|---|
| Maintenance non planifiée | Session d'ingénierie hors fenêtre | Ordre de travail, identité, cible | Contacter l'exploitation ; vérifier l'action avant toute coupure |
| Nouveau chemin IT→contrôleur | Flux entre zones non documenté | Changement réseau, service nécessaire | Préserver les événements et faire évaluer le flux |
| Changement de projet | Empreinte ou version différente | Historique de téléchargement et validation | Mettre en comparaison avec la version approuvée |
| Nouveau compte privilégié | Création ou élévation inattendue | Ticket de changement et propriétaire | Révoquer seulement selon procédure et après vérification des dépendances |
| Perte simultanée de visibilité | Historian/IHM ne reçoit plus les données | État réseau, matériel, procédé | Déterminer si le contrôle local continue et si la sûreté est affectée |
| Connexion fournisseur inhabituelle | Source, durée ou cible inattendue | Approbation et journal de session | Coordonner avec le responsable et contrôler l'accès |

### 6.3 Utiliser MITRE ATT&CK for ICS avec discernement

ATT&CK for ICS fournit une taxonomie de comportements adverses observés. Elle peut aider à transformer une hypothèse de menace en exigences de journalisation, mesures préventives et cas de détection. Une technique listée ne signifie pas que l'actif est vulnérable ou qu'un incident est présent ; il faut adapter les scénarios aux systèmes, versions et fonctions du site.

Pour chaque scénario retenu, définir : données disponibles, conditions normales, signal attendu, faux positifs, niveau de confiance, escalade et actions autorisées. L'objectif est d'augmenter la visibilité et de réduire l'impact, pas de cocher mécaniquement une liste de techniques.

### 6.4 Détection passive et qualité des données

Les capteurs passifs doivent être insérés sans créer de chemin de commande non nécessaire. Vérifier la saturation des ports SPAN, les pertes de paquets, la synchronisation horaire, la rétention et la protection du collecteur. Les données manquantes ou les horloges non alignées peuvent rendre une chronologie trompeuse.

## 7. Gestion du changement et des vulnérabilités à maturité élevée

Un programme mature classe les actifs selon la criticité et les possibilités de maintenance ; suit les annonces du constructeur ; évalue l'exposition réelle ; associe propriétaire et date cible ; documente les compensations ; teste en laboratoire ou sur une plateforme représentative ; applique les changements dans une fenêtre autorisée ; vérifie les résultats ; conserve les preuves.

Pour les actifs non supportés, l'acceptation du risque doit être explicite, limitée dans le temps et accompagnée d'une feuille de route. Les mesures compensatoires incluent la réduction des communications, un accès médié, un contrôle renforcé des modifications, une surveillance dédiée, une sauvegarde vérifiée et un plan de remplacement.

## 8. Réponse à incident et coordination cyberphysique

### 8.1 Structure de gouvernance

Prévoir au minimum les rôles suivants, qui peuvent être combinés selon la taille du site :

- responsable d'exploitation / procédé ;
- responsable OT / automatisme ;
- responsable cybersécurité et coordination incident ;
- équipe réseau et systèmes ;
- maintenance et constructeur/intégrateur ;
- responsable sûreté, sécurité industrielle ou HSE ;
- direction de site et communication de crise, selon le scénario.

La cybersécurité ne décide pas seule d'une action pouvant modifier l'état physique. L'exploitation et les spécialistes de sûreté participent aux décisions de confinement et de reprise.

### 8.2 Séquence de décision

1. Évaluer immédiatement la sécurité des personnes et l'état du procédé.
2. Confirmer les signaux avec les opérateurs sans détruire les données.
3. Définir le périmètre connu et les incertitudes.
4. Choisir les mesures de confinement les moins perturbatrices compatibles avec le risque.
5. Documenter qui a décidé, quand, sur quelle base et avec quels critères d'arrêt.
6. Préserver les journaux, configurations et horodatages pertinents.
7. Traiter la cause après stabilisation et validation du procédé.
8. Restaurer dans un ordre connu, tester les fonctions et obtenir l'approbation de remise en service.
9. Réaliser un retour d'expérience sans blâme, avec actions mesurables.

### 8.3 Ransomware : scénarios distincts

Un ransomware peut toucher les systèmes d'entreprise sans affecter directement le contrôle local ; il peut aussi atteindre une station d'ingénierie, un serveur de supervision ou les sauvegardes. Les réponses ne sont pas identiques.

Le plan doit déterminer : quels contrôles fonctionnent localement ; quelles fonctions dépendent des serveurs affectés ; quels liens peuvent être isolés sans déstabiliser le procédé ; où se trouvent les sauvegardes de confiance ; qui valide un arrêt ou un fonctionnement manuel ; quels indicateurs autorisent la reprise. Ne pas appliquer une règle générique d'extinction ou d'isolement à tous les équipements OT.

### 8.4 Preuves et chaîne de conservation

Conserver la chronologie, la source et l'heure d'extraction, les personnes ayant accédé aux données et les transformations éventuelles. Ne pas modifier les systèmes suspects à des fins d'enquête sans coordination. La collecte doit rester proportionnée aux impératifs de sûreté et aux capacités du site.

## 9. Résilience et reprise

### 9.1 La reprise est un processus de procédé

Restaurer un serveur ne signifie pas que l'installation est prête à repartir. Les fonctions de terrain, les programmes, les paramètres, les versions, les licences, les dépendances réseau, les interverrouillages, les instruments et les procédures opératoires doivent être vérifiés selon le système.

### 9.2 Plan de reprise par fonction

Pour chaque fonction critique, préciser : priorité, dépendances, RTO, RPO, source de sauvegarde approuvée, matériel de remplacement, prérequis, tests, responsables et autorité de remise en service. Les objectifs doivent être réalistes et testés ; une valeur RTO déclarée mais jamais exercée est une hypothèse, pas une capacité prouvée.

### 9.3 Stratégie de sauvegarde

Conserver les versions approuvées des projets et configurations ; protéger une copie indépendante contre la modification ; documenter les outils, licences, mots de passe de récupération et dépendances ; tester l'intégrité et la restauration dans un environnement adapté ; vérifier que les sauvegardes ne contiennent pas déjà une configuration non fiable.

### 9.4 Modes dégradés et autonomie locale

Comprendre ce qui se passe si la liaison à l'IT, l'historian, l'IHM ou la connectivité distante devient indisponible. L'architecture doit permettre, lorsque c'est prévu par la conception, de maintenir ou d'arrêter le procédé de façon sûre. Les modes manuels, les limites de commande et les responsabilités sont définis par l'ingénierie du procédé, non par une équipe cyber isolée.

## 10. Indicateurs de maturité

Éviter les métriques purement quantitatives sans contexte. Exemples utiles :

- part des actifs critiques avec propriétaire et dépendances connus ;
- part des flux interzones justifiés et révisés ;
- part des accès distants nominatifs, approuvés, temporaires et journalisés ;
- délai de révocation après fin d'une intervention ;
- proportion de sauvegardes de fonctions critiques restaurées en test ;
- part des changements OT avec validation procédé et retour arrière documenté ;
- couverture des événements de configuration pertinents ;
- durée de triage lors d'un exercice ;
- nombre d'exceptions de sécurité sans responsable ou sans date d'expiration ;
- délai de correction ou de mitigation selon le risque.

Chaque indicateur doit avoir une définition, une source de données, un propriétaire, une fréquence et une interprétation. Une baisse du nombre d'alertes n'est pas forcément un progrès : elle peut aussi signifier une perte de visibilité.

## 11. Travaux pratiques experts

### TP 1 — Revue d'une architecture Purdue

**Contexte :** un schéma montre IT, DMZ, supervision et automates, mais toutes les cellules partagent un réseau de contrôle et la station d'ingénierie dispose d'une route vers toutes les cellules.

**Tâche :** réaliser une revue de conception.

**Correction attendue :** cartographier les fonctions et dépendances ; proposer des zones selon les conséquences et besoins ; définir les conduits nécessaires ; isoler les cellules lorsque la conception le permet ; limiter la station d'ingénierie à des cibles approuvées ; expliquer les flux de maintenance, de sauvegarde, de synchronisation et de reprise ; prévoir des essais et un retour arrière. Ne pas décider de la topologie finale uniquement sur la base du modèle Purdue.

### TP 2 — Concevoir un cas de détection

**Scénario :** un téléchargement de projet automate est détecté à une heure inhabituelle.

**Correction attendue :** corréler identité, poste source, cible, fenêtre, ordre de travail, empreinte de la version approuvée et événements procédé ; noter les incertitudes ; avertir l'exploitation ; vérifier les fonctions et les modifications par un moyen autorisé. Toute isolation ou restauration est décidée selon le plan du site.

### TP 3 — Plan d'accès distant à assurance élevée

**Tâche :** définir le processus d'accès d'un fournisseur pour une intervention urgente.

**Correction attendue :** identifiant unique, justification, approbation, MFA, contrôle du poste, bastion, cible unique, droits minimaux, durée, enregistrement approprié, transfert de fichier contrôlé, surveillance de la session, fermeture et révocation, revue post-intervention. Une procédure d'urgence est définie à l'avance et auditée ; elle ne doit pas devenir un compte partagé permanent.

### TP 4 — Exercice de ransomware affectant l'IT et l'OT

**Scénario :** l'IT perd plusieurs serveurs et la supervision signale des données vieillissantes. Le contrôle local semble encore fonctionner, mais la situation n'est pas confirmée.

**Correction attendue :** établir l'état du procédé avec les opérateurs ; déterminer quelles fonctions dépendent des serveurs indisponibles ; éviter l'arrêt ou l'isolement systématique ; protéger les copies de sauvegarde ; coordonner les équipes IT/OT/HSE ; décider des mesures de confinement selon la matrice d'impact ; restaurer d'abord les dépendances nécessaires en environnement contrôlé ; valider chaque étape avant reconnexion.

### TP 5 — Revue des capacités de reprise

**Tâche :** construire une fiche RTO/RPO pour la supervision, la station d'ingénierie et un contrôleur critique.

**Correction attendue :** définir pour chaque fonction la conséquence d'une interruption, le point de reprise acceptable, les versions et dépendances requises, le matériel, la séquence de restauration, les tests, le responsable et l'autorité de remise en service. Ne pas imposer un même RTO/RPO à tous les actifs : les objectifs découlent du risque métier et du procédé.

## 12. Exercices corrigés

### Exercice 1
**Question :** quelle est la différence entre Purdue et une architecture de zones/conduits ?

**Réponse :** Purdue fournit une représentation fonctionnelle en niveaux ; les zones/conduits définissent des regroupements de sécurité et leurs chemins de communication. Les deux approches se complètent, mais aucune ne remplace l'analyse de risque et la validation des flux.

### Exercice 2
**Question :** pourquoi « un seul pare-feu entre IT et OT » est-il une réponse insuffisante ?

**Réponse :** les menaces et les besoins diffèrent aussi entre cellules, stations d'ingénierie, supervision, services de données et accès tiers. Une frontière unique n'empêche pas nécessairement les mouvements latéraux internes ou les abus d'un accès autorisé.

### Exercice 3
**Question :** que doit contenir un cas de détection industrialisé ?

**Réponse :** scénario, sources, contexte normal, signal, seuil ou logique, faux positifs, niveau de confiance, procédure de triage, escalade, actions autorisées et indicateurs de qualité.

### Exercice 4
**Question :** faut-il automatiser le blocage d'un PLC dès qu'une anomalie est détectée ?

**Réponse :** pas sans étude. Le blocage peut interrompre une fonction physique ou dégrader un état sûr. L'automatisation doit être conçue et testée avec l'exploitation ; certaines actions doivent rester soumises à une décision humaine informée.

### Exercice 5
**Question :** comment intégrer ATT&CK for ICS dans un programme défensif ?

**Réponse :** sélectionner les comportements plausibles au regard des actifs et menaces, puis les traduire en mesures de prévention, données de détection et exercices. La taxonomie n'est pas un outil de preuve ni un substitut à l'analyse locale.

### Exercice 6
**Question :** pourquoi une sauvegarde non testée ne prouve-t-elle pas la résilience ?

**Réponse :** les fichiers peuvent être incomplets, incompatibles, corrompus ou dépendre d'outils/licences indisponibles. Seule une restauration représentative, suivie d'une validation fonctionnelle, apporte une preuve de capacité.

### Exercice 7
**Question :** comment traiter un système legacy impossible à corriger ?

**Réponse :** évaluer l'exposition et les conséquences, restreindre ses communications, médiatiser les accès, surveiller les modifications, renforcer les sauvegardes, documenter l'exception et planifier un remplacement ou une mitigation avec échéance.

### Exercice 8
**Question :** pourquoi le plan d'incident doit-il inclure HSE et l'exploitation ?

**Réponse :** les décisions de confinement peuvent modifier l'état physique, les procédures manuelles et la sûreté. Les experts du procédé connaissent les conséquences qui ne sont pas visibles dans les journaux informatiques.

### Exercice 9
**Question :** quelle valeur apporte une architecture de transfert unidirectionnel ?

**Réponse :** lorsqu'elle convient au besoin, elle peut réduire le risque de commande entrante depuis une zone moins fiable. Elle doit être évaluée selon les flux réels, les besoins de maintenance et la capacité de reprise ; elle ne résout pas tous les risques de compromission interne.

### Exercice 10
**Question :** quel est le défaut d'un indicateur « nombre d'alertes par mois » utilisé seul ?

**Réponse :** le volume peut diminuer parce que le risque baisse, mais aussi parce que les capteurs ou journaux ne fonctionnent plus. Il faut combiner les alertes avec la couverture, la qualité des données, le délai de triage et les incidents simulés.

## 13. Défi final corrigé

### Scénario

Une station de traitement d'eau comporte trois zones de procédé. L'architecture est représentée par niveaux Purdue, mais les trois zones sont reliées à une même station d'ingénierie. Un accès fournisseur est toujours actif. Les journaux ne sont pas centralisés et les sauvegardes existent mais n'ont jamais été restaurées en exercice. Un incident touchant l'IT rend certains services de supervision indisponibles ; l'état du contrôle local est encore à confirmer.

### Mission

Élaborer un plan expert qui inclut : architecture cible, mesures immédiates, détection, réponse à incident, restauration et indicateurs.

### Correction détaillée

**A. Gestion de la situation présente**

1. Désigner le coordinateur incident et établir la communication avec l'exploitation, l'OT, la cybersécurité, le réseau, la maintenance et HSE.
2. Confirmer l'état physique et fonctionnel du procédé par les opérateurs et les moyens locaux autorisés ; ne pas supposer qu'une perte de supervision signifie nécessairement une perte de contrôle.
3. Identifier les dépendances des services IT touchés et les liaisons réellement établies vers l'OT.
4. Éviter les coupures ou redémarrages globaux ; appliquer les mesures de confinement prévues et évaluées par le responsable du procédé.
5. Préserver les journaux, changements réseau et configurations. Isoler les sauvegardes de confiance contre les modifications selon procédure.

**B. Architecture cible**

1. Définir des zones de contrôle par fonction et criticité, après analyse procédé.
2. Maintenir une DMZ industrielle avec services de transfert et de médiation explicitement définis.
3. Remplacer les routes générales de la station d'ingénierie par des chemins d'accès aux cellules approuvées, éventuellement médiatisés par un bastion ou des connexions activées à la demande.
4. Fermer l'accès fournisseur permanent et mettre en place identité nominative, MFA, approbation, fenêtre, journalisation et révocation.
5. Documenter tous les flux nécessaires y compris démarrage, maintenance, redondance, synchronisation et restauration, puis appliquer les règles par étapes.
6. Traiter les interfaces des systèmes de sécurité selon leurs exigences propres et l'ingénierie de sûreté ; ne pas les intégrer à une segmentation générique sans analyse.

**C. Détection et observabilité**

1. Construire une base de référence passive pour les flux et modes de fonctionnement.
2. Collecter les journaux pertinents avec horodatage cohérent et stockage protégé.
3. Prioriser les événements d'accès distant, de programmation, de modification des comptes, de changement de flux et de perte de visibilité.
4. Pour chaque alerte, définir la validation avec l'exploitation et les critères d'action. Ne pas déclencher d'isolement automatique qui pourrait perturber le procédé sans validation spécifique.

**D. Reprise et exercice**

1. Établir des RTO/RPO par fonction ; identifier les sauvegardes approuvées, versions, licences, dépendances et matériel de remplacement.
2. Réaliser les premières restaurations en laboratoire ou en environnement isolé.
3. Définir la séquence de remise en service et les tests des contrôleurs, communications, alarmes, interverrouillages et interfaces.
4. Prévoir l'approbation par le responsable du procédé avant la reconnexion et la reprise.
5. Exécuter un exercice de table associant perte de supervision, accès fournisseur compromis et suspicion de ransomware.

**E. Indicateurs à suivre**

- couverture de l'inventaire des actifs critiques ;
- pourcentage de flux interzones avec justification et propriétaire ;
- durée maximale des accès fournisseur et taux de clôture vérifiée ;
- changements de programmes rapprochés d'une référence approuvée ;
- succès et durée des restaurations testées ;
- délai de confirmation de l'état du procédé en exercice ;
- temps de triage des alertes et qualité des données de collecte ;
- exceptions de sécurité avec propriétaire, échéance et mesure compensatoire.

**Conclusion :** la réussite n'est pas le nombre de dispositifs de sécurité déployés. Elle se mesure à la capacité démontrée de limiter les chemins d'accès, comprendre les communications, détecter un changement important, décider sans mettre le procédé en danger et rétablir une fonction fiable à partir d'une configuration approuvée.

## 14. Glossaire

- **ATT&CK for ICS :** base de connaissances des tactiques et techniques adverses touchant les systèmes de contrôle industriels.
- **Conduit :** communications contrôlées entre zones de sécurité.
- **IDMZ :** DMZ industrielle.
- **Purdue Model :** modèle fonctionnel d'organisation des systèmes industriels en niveaux.
- **RPO / RTO :** objectifs de point de reprise et de délai de rétablissement.
- **SIS :** système instrumenté de sécurité soumis à ses propres exigences de sûreté.
- **Zero Trust :** approche réduisant la confiance implicite et demandant une vérification explicite adaptée au contexte.
- **Zone :** groupe d'actifs aux exigences de sécurité communes.

## 15. Références techniques

1. NIST SP 800-82 Rev. 3, *Guide to Operational Technology (OT) Security*, version finale de septembre 2023 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
2. NIST SP 800-82 Rev. 4, *Initial Public Draft*, publié le 21 septembre 2026 et non finalisé à la date du cours : https://csrc.nist.gov/pubs/sp/800/82/r4/ipd
3. ISA/IEC 62443, série de normes pour la sécurité des systèmes d'automatisation et de contrôle industriels : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
4. MITRE ATT&CK for ICS : https://attack.mitre.org/matrices/ics/
5. CISA, *Cross-Sector Cybersecurity Performance Goals* : https://www.cisa.gov/cross-sector-cybersecurity-performance-goals
6. CISA, *Configuring and Managing Remote Access for Industrial Control Systems* : https://www.cisa.gov/sites/default/files/recommended_practices/RP_Managing_Remote_Access_S508NC.pdf
7. Australian Cyber Security Centre, *Secure connectivity principles for Operational Technology (OT)*, janvier 2026 : https://www.cyber.gov.au/publication/secure-connectivity-principles-for-operational-technology
8. CISA et partenaires, guide sur l'adaptation des principes Zero Trust aux environnements OT, annoncé en avril 2026 : https://content.govdelivery.com/accounts/USDHSCISA/bulletins/4151784

Les normes et guides peuvent être mis à jour. Vérifier la version officielle en vigueur, les exigences sectorielles locales et la documentation du constructeur. Toute architecture cible doit être validée avec les responsables OT, sûreté et exploitation avant sa mise en œuvre.
