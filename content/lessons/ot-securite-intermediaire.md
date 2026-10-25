# Cybersécurité OT — Intermédiaire

## Mise en contexte : passer des bonnes pratiques à une architecture défendable

Au niveau débutant, tu as appris à identifier les actifs OT, reconnaître les risques et appliquer les principes de base. Le niveau intermédiaire consiste à transformer ces principes en une architecture exploitable : zones de sécurité, conduits maîtrisés, accès fournisseurs contrôlés, journalisation, gestion des vulnérabilités et préparation des incidents.

L'objectif n'est pas de reproduire mécaniquement une architecture IT. L'objectif est de réduire les chemins d'attaque tout en préservant la disponibilité du contrôle, les fonctions de sûreté et les exigences de production.

> **Règle de travail :** aucun changement de segmentation, de filtrage, de compte, d'agent de sécurité ou de version sur un système OT ne doit être appliqué sans propriétaire métier, évaluation d'impact, validation, fenêtre approuvée et procédure de retour arrière.

## 1. Objectifs et prérequis

À l'issue de ce cours, tu sauras :

- concevoir une segmentation inspirée de Purdue et fondée sur les zones/conduits ;
- décrire une DMZ industrielle et ses flux autorisés ;
- construire une matrice de communication vérifiable ;
- organiser les accès distants de fournisseurs et les privilèges des techniciens ;
- planifier une gestion des vulnérabilités compatible avec la production ;
- déployer une collecte de journaux et une surveillance OT adaptées ;
- préparer des scénarios de réponse à incident et de reprise ;
- mesurer le niveau de maîtrise de façon concrète.

Prérequis : bases OT/ICS, segmentation réseau, pare-feu, inventaire d'actifs, notions de sauvegarde et gestion de changement.

## 2. Modèle de menace et analyse de risque

### 2.1 Décrire le procédé avant l'actif

Pour une fonction industrielle, documenter :

1. la fonction physique rendue ;
2. les équipements qui la contrôlent ou la surveillent ;
3. les dépendances réseau, électriques, temps, identité et ingénierie ;
4. les conséquences d'une perte, d'un retard ou d'une commande incorrecte ;
5. les conditions d'un état sûr et la manière de le vérifier ;
6. les moyens de restauration et les personnes habilitées.

On peut utiliser une échelle qualitative vraisemblance × gravité, mais le score ne doit pas donner une fausse précision. Les conséquences de sûreté, d'environnement et de production peuvent être non linéaires et doivent être examinées par des spécialistes métier.

### 2.2 Exemple d'analyse

| Scénario | Faiblesse | Conséquence possible | Contrôles prioritaires |
|---|---|---|---|
| Compte fournisseur compromis | Accès permanent et large | Modification non autorisée ou interruption | Accès temporaire, MFA, bastion, approbation, journalisation |
| Ransomware atteint une station d'ingénierie | Partage et privilèges trop larges | Perte d'ingénierie et restauration complexe | Segmentation, sauvegardes indépendantes, privilèges limités, plan de reprise |
| Poste IT communique directement avec les PLC | Réseau plat | Mouvement latéral vers le contrôle | Zones/conduits, règles allowlist, supervision passive |
| Mise à jour non testée | Changement sans validation OT | Incompatibilité ou arrêt | Gestion de changement, test, fenêtre de maintenance, retour arrière |
| Nouvelle passerelle oubliée | Inventaire incomplet | Chemin réseau non maîtrisé | Découverte passive, revue des schémas et changements, propriétaires désignés |

## 3. Segmentation par zones et conduits

La série ISA/IEC 62443 utilise la notion de **zone** pour regrouper des actifs ayant des besoins de sécurité communs et celle de **conduit** pour décrire les communications entre zones. Les exigences doivent être définies selon le risque ; le modèle Purdue aide à situer les fonctions, mais les zones ne correspondent pas toujours une à une aux niveaux Purdue.

### 3.1 Architecture exemple

```text
                 Internet / prestataires
                           |
                  [Passerelle d'accès distant]
                           |
Réseau IT ---- [Pare-feu IT/DMZ] ---- [DMZ industrielle]
                                       |  Bastion OT
                                       |  Relais de fichiers
                                       |  Collecteur / Historian répliqué
                           [Pare-feu DMZ/OT]
                                       |
                           [Zone de supervision]
                                       |
                      +----------------+----------------+
                      |                                 |
               [Cellule A]                       [Cellule B]
               IHM / PLC                         IHM / PLC
```

La DMZ industrielle ne devrait pas être un simple VLAN de passage. Chaque service qui y réside doit avoir une fonction claire, des flux documentés, une identité et un cycle de mise à jour. Les données transférées vers IT peuvent être répliquées ou relayées selon l'architecture, sans autoriser pour autant des connexions générales dans les deux sens.

### 3.2 Matrice de flux

Pour chaque flux, enregistrer : source, destination, protocole/service, sens d'initiation, besoin opérationnel, propriétaire, criticité, justification, méthode de test et date de révision.

| Source | Destination | Fonction | Politique cible | Validation |
|---|---|---|---|---|
| IHM cellule A | PLC cellule A | Supervision/commande autorisée | Autoriser uniquement les communications requises | Essai fonctionnel avec opérateur |
| PLC cellule A | Historian OT | Remontée de données | Autoriser uniquement le chemin prévu | Vérifier les valeurs et la charge |
| Historian OT | Relais DMZ | Export des mesures approuvées | Flux contrôlé et limité | Vérifier la fraîcheur des données |
| Bastion DMZ | Station d'ingénierie | Maintenance temporaire | Autorisation nominative et horaire | Session observée puis clôturée |
| IT utilisateur | PLC | Aucun besoin direct documenté | Refuser | Vérifier qu'aucun processus légitime ne dépend du flux avant activation |
| Internet | Automate | Aucun besoin direct | Refuser | Vérifier la topologie et les règles existantes |

Ne pas inventer les ports ou supposer qu'un protocole est à sens unique uniquement parce que son usage paraît le suggérer. La direction d'initiation, les réponses de session et les dépendances doivent être établies à partir de la documentation fournisseur et du comportement validé du système.

### 3.3 Déploiement progressif d'une règle

1. Recueillir les flux observés sur une période représentative du procédé.
2. Comparer les observations avec les schémas et la documentation.
3. Faire confirmer chaque flux par le propriétaire de l'application ou de l'automatisme.
4. Identifier les flux rares : démarrage, maintenance, synchronisation, sauvegarde, reprise après panne.
5. Construire les règles les plus précises possibles.
6. Simuler ou tester dans un environnement représentatif, si disponible.
7. Prévoir un retour arrière, une surveillance et des critères d'arrêt.
8. Déployer par étapes, vérifier le procédé et documenter les exceptions.

Les périodes d'observation doivent couvrir les régimes de fonctionnement pertinents ; quelques minutes de capture ne prouvent pas qu'un flux n'est jamais nécessaire.

## 4. DMZ industrielle et accès distant

### 4.1 Services possibles dans la DMZ

Selon l'architecture : bastion d'administration, relais de transfert de fichiers, collecteur de journaux, réplica de l'historian, dépôt de mises à jour contrôlées, serveur d'accès distant ou passerelle de médiation. Un service ne doit être placé dans la DMZ que si les dépendances, les flux et les responsabilités sont explicités.

### 4.2 Schéma d'accès fournisseur

```text
Fournisseur
    |
Identité nominative + MFA + autorisation ponctuelle
    |
Passerelle d'accès distant
    |
Bastion en DMZ industrielle -- journalisation de session
    |
Cible approuvée (et uniquement celle-ci)
    |
Procédure de changement / validation du responsable OT
```

Principes recommandés :

- accès fermé par défaut et ouvert sur demande approuvée ;
- cible, horaire et motif explicitement définis ;
- authentification forte et identité individuelle ;
- poste du prestataire évalué selon la politique du site ;
- droits temporaires et séparation des tâches ;
- blocage ou contrôle des transferts de fichiers ;
- enregistrement des actions, dans le respect des règles de confidentialité ;
- clôture de la session, révocation et revue après intervention ;
- moyen de coupure maîtrisé sans interrompre une fonction critique.

MFA, VPN ou bastion ne sont pas interchangeables. Un VPN chiffre un transport ; il ne donne pas, à lui seul, une autorisation appropriée à chaque cible et à chaque action.

### 4.3 Comptes privilégiés

Séparer les comptes bureautiques et d'administration ; employer des comptes nominatifs ; limiter les droits permanents ; protéger les comptes de service ; gérer les secrets ; réviser les accès ; désactiver les comptes obsolètes selon une procédure validée. Quand un ancien contrôleur ne prend pas en charge les identités modernes, compenser par une segmentation, des accès médiés, des restrictions physiques et une journalisation adaptée.

## 5. Gestion des vulnérabilités en OT

### 5.1 Pourquoi la méthode IT classique ne suffit pas toujours

Un scan actif, un agent, un redémarrage ou une mise à jour peut affecter un équipement ancien ou une fonction en temps réel. Le fait qu'un correctif soit disponible ne veut pas dire qu'il peut être déployé immédiatement dans tous les sites.

### 5.2 Processus recommandé

1. Détecter ou recevoir l'information de vulnérabilité.
2. Confirmer les actifs et versions concernés.
3. Évaluer l'exposition réelle : chemins d'accès, privilèges, services et contrôles compensatoires.
4. Évaluer la conséquence pour le procédé et la sûreté avec l'équipe OT.
5. Chercher une mise à jour, une mesure compensatoire ou une restriction temporaire auprès du constructeur.
6. Tester dans un environnement représentatif, quand cela est possible.
7. Planifier avec l'exploitation et la maintenance.
8. Sauvegarder, appliquer, vérifier et documenter.
9. Réévaluer le risque résiduel et la date de prochaine action.

Les scans actifs et tests intrusifs ne doivent être exécutés que sur autorisation explicite, avec portée, fenêtre, sauvegarde, procédure d'arrêt et validation constructeur si nécessaire. Une analyse de vulnérabilité passive ne démontre pas à elle seule l'absence de vulnérabilités.

### 5.3 Mesures compensatoires

Lorsqu'un correctif ne peut pas être appliqué : réduire l'exposition réseau, désactiver les services non requis si c'est supporté et validé, limiter l'accès distant, utiliser une liste d'applications autorisées sur les hôtes compatibles, surveiller les comportements pertinents, renforcer les sauvegardes et documenter l'exception avec échéance et responsable.

## 6. Durcissement des postes et systèmes

Pour les postes Windows ou Linux qui soutiennent l'OT, définir un socle de configuration compatible avec les applications industrielles :

- comptes et privilèges minimaux ;
- services et ports non nécessaires désactivés après validation ;
- politiques de verrouillage de session et de gestion des secrets ;
- contrôle des logiciels installés ;
- protection antimalware/EDR uniquement après tests de compatibilité et de performance ;
- gestion des supports amovibles ;
- horodatage cohérent et journaux protégés ;
- sauvegardes des configurations, projets et dépendances ;
- gestion du cycle de vie et des systèmes non supportés.

Ne pas activer un contrôle qui met en quarantaine automatiquement un équipement de contrôle critique sans scénario de validation et de reprise. L'action doit être conçue en fonction de la fonction du poste et du procédé.

## 7. Surveillance et détection OT

### 7.1 Ce qu'il faut observer

- actifs nouveaux ou disparus ;
- communications entre zones inhabituelles ;
- accès distants en dehors des fenêtres approuvées ;
- changements de configuration ou de programme ;
- nouveaux services, équipements ou comptes ;
- trafic d'ingénierie à des périodes inattendues ;
- écarts importants du volume ou de la fréquence des communications ;
- erreurs d'authentification et événements de sécurité système ;
- changements qui coïncident avec un changement de procédé.

L'anomalie doit être mise en contexte. Une activité de programmation peut être légitime pendant une maintenance. Le même événement en pleine production sans ordre de travail peut justifier une enquête, mais ne constitue pas à lui seul une preuve de compromission.

### 7.2 Collecte prudente

Utiliser des TAP ou ports SPAN dimensionnés, des capteurs passifs et les journaux des équipements. Vérifier la capacité, la synchronisation horaire, la protection de la plateforme de collecte et la qualité de la rétention. Un collecteur ne doit pas ajouter de chemin de commande vers les contrôleurs si seul un besoin d'observation existe.

### 7.3 De l'alerte à l'action

Chaque règle de détection devrait préciser : événement, sources de données, contexte attendu, niveau de confiance, impact potentiel, propriétaire, méthode de triage et actions autorisées. Éviter les réponses automatisées génériques qui coupent une liaison ou isolent un contrôleur sans vérification de l'impact sur le procédé.

## 8. Sauvegarde, reprise et continuité

Les sauvegardes devraient inclure les projets PLC/API, paramètres, recettes, configurations de commutateurs et pare-feu, configurations IHM/SCADA, scripts d'intégration, certificats et clés récupérables selon une procédure sécurisée, licences, versions installables et documentation des dépendances.

Établir, pour chaque fonction critique :

- **RTO :** durée cible de rétablissement ;
- **RPO :** perte de données acceptable ;
- séquence de restauration ;
- personne habilitée à valider le résultat ;
- matériel de remplacement ou procédure de reconstruction ;
- test hors production ;
- critères de reconnexion et de retour à l'exploitation.

Une sauvegarde du programme automate ne prouve pas que le procédé peut repartir en sécurité. La remise en service peut nécessiter la validation des E/S, capteurs, actionneurs, séquences, paramètres, interverrouillages et procédures opératoires.

## 9. Réponse à incident OT

### 9.1 Phases

1. **Préparation :** rôles, contacts, scénarios, inventaire, accès d'urgence, sauvegardes et exercices.
2. **Détection et analyse :** confirmer les signaux et déterminer le périmètre avec les opérateurs.
3. **Maîtrise :** choisir les mesures qui réduisent le dommage sans créer un risque supplémentaire pour la sûreté.
4. **Éradication :** traiter la cause après stabilisation et validation technique.
5. **Récupération :** restaurer, tester, vérifier les fonctions et rétablir progressivement.
6. **Retour d'expérience :** chronologie, cause, écarts de procédure et actions de réduction du risque.

### 9.2 Ordre de décision

Les mesures de réponse doivent être organisées avec une priorité explicite : sécurité des personnes et état sûr du procédé ; maintien ou rétablissement des fonctions essentielles ; confinement cyber compatible avec la sécurité ; préservation des éléments d'enquête ; reprise validée. L'ordre exact dépend du scénario et du plan de sûreté du site.

### 9.3 Indices d'incident

Un chiffrement visible, des comptes d'ingénierie inattendus, des changements de logique non autorisés, des flux inhabituels ou une perte de visibilité peuvent être des indices. Ne pas conclure à une attaque uniquement à partir d'une seule alarme. Corréler les journaux, les ordres de travail, les événements procédé et les observations du personnel.

## 10. Travaux pratiques guidés

### TP 1 — Construire une matrice de flux défendable

**Contexte :** une cellule industrielle utilise une IHM, deux PLC, un historian, une station d'ingénierie et un bastion dans la DMZ.

**Tâche :** définir les champs de la matrice, demander les confirmations nécessaires et proposer les règles cibles sans inventer les ports.

**Correction :** décrire chaque flux avec source, cible, besoin, sens d'initiation, service confirmé, propriétaire, fenêtre, criticité et test de validation. Les flux inconnus restent en attente de clarification ; ils ne doivent pas être autorisés indéfiniment par commodité. Toute règle restrictive se teste sur un environnement représentatif ou une fenêtre de maintenance approuvée.

### TP 2 — Reconcevoir l'accès fournisseur

**Situation initiale :** un VPN donne accès à tout le sous-réseau OT et les sessions ne sont pas enregistrées.

**Correction :** authentification forte, compte nominatif, demande et approbation, cible précise, accès temporaire, bastion, transferts contrôlés, logs, fermeture de session et revue. Le routage réseau doit empêcher l'accès latéral aux actifs non autorisés.

### TP 3 — Traiter une vulnérabilité sur une station d'ingénierie

**Tâche :** créer un plan d'évaluation et de correction.

**Correction :** identifier la version et l'exposition, vérifier la notification constructeur, évaluer le risque procédé, isoler ou restreindre les chemins inutiles, tester le correctif et la compatibilité logicielle, planifier une fenêtre, sauvegarder, appliquer, vérifier et documenter. Si le correctif est différé, définir une mesure compensatoire, un responsable et une date de réexamen.

### TP 4 — Écrire une règle de détection

**Scénario :** une station d'ingénierie envoie du trafic de programmation vers un PLC en dehors d'une fenêtre de maintenance.

**Correction :** établir l'horaire de référence, identifier la source et la cible, corréler l'ordre de travail, alerter l'opérateur et le responsable OT, examiner les changements de projet et les journaux. Ne pas couper automatiquement le lien tant que l'effet sur le procédé n'a pas été évalué.

### TP 5 — Tester un plan de restauration

**Tâche :** préparer un exercice de restauration d'une IHM de test.

**Correction :** utiliser une plateforme isolée ou un laboratoire ; vérifier les versions, licences, certificats, dépendances, fichiers de projet et sources de données ; restaurer et tester les fonctions ; documenter le temps réel ; obtenir la validation technique ; ne pas reconnecter au procédé tant que la procédure de remise en service n'est pas approuvée.

## 11. Exercices corrigés

### Exercice 1
**Question :** quelle est la différence entre zone et conduit dans l'approche ISA/IEC 62443 ?

**Réponse :** une zone regroupe des actifs ayant des exigences de sécurité communes ; un conduit définit les communications entre zones et les contrôles qui les protègent. Le design doit partir des risques et besoins de communication, pas uniquement des sous-réseaux IP.

### Exercice 2
**Question :** pourquoi ne pas bloquer tous les flux inconnus dès le premier jour ?

**Réponse :** certains flux rares ou mal documentés peuvent soutenir le démarrage, la maintenance, la redondance ou la reprise. Il faut les caractériser, obtenir une validation et déployer le filtrage progressivement avec retour arrière.

### Exercice 3
**Question :** un VPN avec MFA suffit-il pour l'accès fournisseur ?

**Réponse :** non. Il faut limiter les cibles et privilèges, médiatiser l'accès, contrôler les transferts, journaliser, approuver les sessions, limiter leur durée et révoquer les accès.

### Exercice 4
**Question :** quelle est la valeur d'une capture réseau passive ?

**Réponse :** elle aide à établir une base de communications et détecter des changements sans solliciter directement les équipements. Elle ne détecte pas nécessairement les actifs silencieux et n'explique pas automatiquement la légitimité de chaque flux.

### Exercice 5
**Question :** que faire d'un correctif pour lequel le constructeur ne garantit pas la compatibilité ?

**Réponse :** ne pas l'appliquer directement en production. Évaluer l'exposition, rechercher un avis officiel, tester si possible et choisir avec l'exploitation une mesure compensatoire documentée jusqu'à une fenêtre validée.

### Exercice 6
**Question :** un système EDR isole une station d'ingénierie. Pourquoi faut-il un scénario validé ?

**Réponse :** l'isolement pourrait couper une liaison de contrôle, une fonction de supervision ou un accès d'urgence. La réponse automatisée doit être compatible avec la fonction de l'hôte et les procédures du site.

### Exercice 7
**Question :** pourquoi les sauvegardes de projets PLC doivent-elles être versionnées ?

**Réponse :** pour identifier une version approuvée, comparer les changements, revenir à une configuration connue et éviter de restaurer un fichier obsolète ou non validé.

### Exercice 8
**Question :** en quoi un RTO diffère-t-il d'un RPO ?

**Réponse :** le RTO est la durée cible de rétablissement ; le RPO définit la quantité de données ou l'ancienneté maximale acceptable du point restauré.

### Exercice 9
**Question :** un trafic de programmation inattendu prouve-t-il une attaque ?

**Réponse :** non. Il peut être lié à un changement approuvé ou à un événement technique. Il faut corréler la source, la fenêtre, l'ordre de travail, les journaux et les changements de projet.

### Exercice 10
**Question :** comment éviter qu'une DMZ devienne une zone de confiance excessive ?

**Réponse :** attribuer une fonction précise à chaque service, limiter les flux, maintenir les systèmes, gérer les identités, collecter les journaux, surveiller les transferts et éviter les routes générales entre IT et OT.

## 12. Défi final corrigé

### Scénario

Une usine dispose de deux cellules de production, d'un historian, d'une station d'ingénierie partagée et d'un accès fournisseur via VPN. Les journaux sont locaux, la DMZ reçoit plusieurs flux non documentés et les sauvegardes ne sont jamais restaurées en test.

### Mission

Proposer un plan de sécurisation en trois phases : 30 jours, 90 jours, 180 jours. Les durées sont des exemples de planification et doivent être ajustées à la criticité et aux ressources.

### Correction détaillée

**Phase 1 — Comprendre et réduire l'exposition immédiate**

- nommer les responsables et définir le circuit d'approbation ;
- inventorier les actifs critiques et les chemins d'accès ;
- examiner le VPN fournisseur, les comptes partagés et les accès permanents ;
- collecter et préserver les journaux existants ;
- identifier les sauvegardes disponibles et sécuriser une copie indépendante ;
- interdire les nouveaux flux non autorisés, sans appliquer de blocage risqué avant analyse des dépendances.

**Phase 2 — Concevoir et tester les contrôles**

- définir zones/conduits et une DMZ industrielle avec fonctions explicites ;
- produire et valider la matrice de flux ;
- mettre en place un accès fournisseur temporaire, nominatif, MFA et journalisé ;
- tester les règles de filtrage sur un environnement représentatif ou par étapes ;
- créer un socle de durcissement compatible avec les logiciels industriels ;
- construire une première base de référence passive.

**Phase 3 — Améliorer la résilience et la détection**

- déployer les règles approuvées avec surveillance et retour arrière ;
- centraliser les journaux pertinents sans ajouter de chemin de commande inutile ;
- tester une restauration complète en environnement de test ;
- définir RTO/RPO et séquences de reprise pour chaque fonction ;
- exécuter un exercice de table sur accès fournisseur compromis et ransomware ;
- mesurer les progrès par les flux justifiés, les accès révisés, les restaurations réussies et les temps de triage.

**Critères de réussite :** chaque actif critique a un propriétaire ; les flux essentiels sont documentés ; l'accès distant est contrôlé et révoqué après usage ; les sauvegardes ont été restaurées en test ; les responsabilités d'incident sont connues ; les changements de sécurité ont été validés par l'exploitation.

## 13. Glossaire

- **Allowlist :** liste explicite des communications ou applications autorisées.
- **Bastion :** point contrôlé d'administration ou d'accès distant.
- **Conduit :** canal contrôlé de communication entre zones.
- **EDR :** détection et réponse sur les terminaux.
- **IDMZ :** DMZ industrielle.
- **MFA :** authentification multifacteur.
- **RPO :** objectif de point de reprise.
- **RTO :** objectif de délai de rétablissement.
- **TAP/SPAN :** moyens d'observer une copie du trafic.
- **Zone :** ensemble d'actifs soumis à des besoins de sécurité communs.

## 14. Références techniques

1. NIST SP 800-82 Rev. 3 — guide final OT : https://csrc.nist.gov/pubs/sp/800/82/r3/final
2. NIST SP 800-82 Rev. 4 — projet public initial publié en septembre 2026, non finalisé : https://csrc.nist.gov/pubs/sp/800/82/r4/ipd
3. ISA/IEC 62443 — série de normes de cybersécurité IACS : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
4. CISA — Cross-Sector Cybersecurity Performance Goals : https://www.cisa.gov/cross-sector-cybersecurity-performance-goals
5. CISA — recommandations de gestion de l'accès distant industriel : https://www.cisa.gov/sites/default/files/recommended_practices/RP_Managing_Remote_Access_S508NC.pdf
6. Australian Cyber Security Centre — *Secure connectivity principles for OT* (janvier 2026) : https://www.cyber.gov.au/publication/secure-connectivity-principles-for-operational-technology
7. MITRE ATT&CK for ICS : https://attack.mitre.org/matrices/ics/

Utiliser les textes de référence dans leur version applicable et vérifier les exigences légales ou sectorielles locales. Les configurations doivent être validées avec le constructeur et les responsables du procédé.
