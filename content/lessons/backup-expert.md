# Tests de restauration et PRA

## Niveau expert

## 1. Présentation générale

Au niveau débutant, nous avons appris à sauvegarder et restaurer des fichiers, à utiliser des outils comme `tar`, `rsync` et Restic, et à vérifier des copies simples.

Au niveau intermédiaire, nous avons étudié les solutions de sauvegarde d'entreprise, les dépôts centralisés, les politiques de rétention, la protection des machines virtuelles et les copies indépendantes.

Le niveau expert répond à une question fondamentale :

**Comment démontrer qu'une organisation peut réellement reprendre ses activités lorsque ses systèmes, ses données ou son site principal deviennent indisponibles ?**

Disposer d'une sauvegarde ne suffit pas. Il faut démontrer que les bonnes données sont récupérables, que les dépendances sont disponibles, que les systèmes peuvent redémarrer dans le bon ordre, que les applications fonctionnent et que les délais respectent les objectifs métier.

Cette démonstration repose sur trois domaines complémentaires :

- **Les tests de restauration** : vérifier qu'une sauvegarde permet effectivement de récupérer des données, des systèmes et des applications.
- **Le PRA — Plan de reprise d'activité informatique** : organiser le rétablissement des services après un sinistre.
- **Le PCA — Plan de continuité d'activité** : organiser le maintien des activités essentielles pendant une perturbation.

Nous aborderons également la gestion de crise, la reprise après rançongiciel, les environnements de récupération isolés, le basculement vers un site secondaire, le retour vers le site principal et la mesure des résultats.

Le cours adopte une approche pratique : chaque scénario doit aboutir à des preuves, des résultats mesurés, des responsabilités explicites et des actions d'amélioration.

## 2. Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit pouvoir :

1. Construire une stratégie de tests de restauration fondée sur les risques.
2. Distinguer un contrôle d'intégrité, un test technique et une validation métier.
3. Concevoir un programme annuel d'exercices PRA.
4. Définir des scénarios de perte de données, de panne d'infrastructure et de cyberattaque.
5. Mesurer les RPO et RTO réellement obtenus.
6. Construire une analyse d'impact métier, ou BIA.
7. Déterminer les dépendances critiques d'un système.
8. Organiser un ordre de reprise cohérent.
9. Restaurer des fichiers, des bases de données, des machines virtuelles et des services complets.
10. Préparer un environnement de récupération isolé.
11. Organiser une reprise après rançongiciel sans réintroduire la menace.
12. Définir des critères de validation technique et métier.
13. Concevoir des procédures de crise et des runbooks de restauration.
14. Organiser un exercice sur table, un test technique et un exercice de reprise.
15. Documenter les résultats et corriger les faiblesses identifiées.
16. Organiser le retour vers l'infrastructure normale après une reprise.
17. Définir les responsabilités des équipes techniques, métier, sécurité et direction.
18. Démontrer qu'un plan de reprise peut être exécuté dans les conditions prévues.

## 3. Les notions fondamentales : sauvegarde, restauration, reprise et continuité

### 3.1 Sauvegarder n'est pas restaurer

Une sauvegarde est une opération de protection. Une restauration est une opération de récupération.

Une sauvegarde peut être déclarée réussie alors qu'une restauration demeure impossible pour plusieurs raisons :

- Le fichier de sauvegarde est incomplet ou corrompu.
- La clé de chiffrement a été perdue.
- Le catalogue ou les métadonnées sont indisponibles.
- Le système de destination ne dispose pas de suffisamment d'espace.
- Les versions des logiciels sont incompatibles.
- Les dépendances réseau ne sont pas disponibles.
- Les données sont récupérées, mais l'application ne peut pas démarrer.
- Les identifiants nécessaires à la reprise sont indisponibles.
- La procédure n'a jamais été testée.
- La restauration prend beaucoup plus de temps que prévu.

La réussite d'une tâche de sauvegarde ne doit donc pas être utilisée comme seul indicateur de préparation à un sinistre.

### 3.2 Les quatre étapes de la récupération

```text
PROTEGER LES DONNEES
        |
        v
CONSERVER DES POINTS DE RESTAURATION
        |
        v
RESTAURER LES DONNEES ET LES SYSTEMES
        |
        v
VALIDER LES SERVICES ET LES DONNEES
        |
        v
REPRENDRE LES ACTIVITES
```

La restauration des données est une étape du processus. La reprise opérationnelle exige également des tests, des décisions et une validation par les responsables concernés.

### 3.3 PRA et PCA

Le PRA et le PCA sont complémentaires.

**PRA : Plan de reprise d'activité informatique**

Il définit comment rétablir les systèmes, les données, les applications et les services après une interruption majeure.

**PCA : Plan de continuité d'activité**

Il définit comment maintenir les activités essentielles pendant une perturbation, éventuellement avec des procédures manuelles, des équipes alternatives ou des moyens de fonctionnement dégradés.

Exemple :

```text
SINISTRE DU SITE PRINCIPAL
          |
          v
Les équipes métier peuvent-elles
continuer à travailler ?
          |
    +-----+------+
    |            |
   OUI           NON
    |            |
    v            v
Activer les   Activer les mesures
mesures de    de continuité métier
reprise       et les procédures
informatique  de secours
    |            |
    +------+-----+
           |
           v
    Services prioritaires
           |
           v
    Reprise contrôlée
```

Le PCA peut permettre de continuer certaines activités manuellement pendant que l'infrastructure est restaurée.

Le PRA vise à remettre en service les moyens informatiques nécessaires.

### 3.4 Gestion de crise et réponse à incident

La gestion de crise coordonne la décision, les responsabilités, les communications et les priorités pendant un événement majeur.

La réponse à incident de sécurité vise notamment à identifier, contenir, analyser et éliminer une menace.

Ces processus doivent être coordonnés avec le PRA, mais ne sont pas identiques.

Lors d'une attaque informatique, il peut être dangereux de démarrer immédiatement les restaurations sans avoir déterminé si les comptes, les systèmes ou les sauvegardes sont encore compromis.

## 4. Pourquoi tester les restaurations ?

### 4.1 La sauvegarde n'est qu'une hypothèse tant qu'elle n'est pas testée

Une opération de sauvegarde indique que le mécanisme a effectué un travail selon les contrôles prévus.

Le test de restauration apporte une preuve supplémentaire : il montre que les données peuvent être récupérées dans un environnement donné.

La validation applicative va encore plus loin : elle montre que le service récupéré répond aux besoins opérationnels.

```text
NIVEAU 1 : JOB REUSSI
  La sauvegarde a été exécutée
            |
            v
NIVEAU 2 : CONTROLE D'INTEGRITE
  Les contrôles techniques réussissent
            |
            v
NIVEAU 3 : TEST DE RESTAURATION
  Les données sont récupérées
            |
            v
NIVEAU 4 : TEST TECHNIQUE
  Le système ou service démarre
            |
            v
NIVEAU 5 : VALIDATION METIER
  Les fonctions attendues sont opérationnelles
```

Ces niveaux de vérification sont complémentaires. La réussite d'un niveau ne garantit pas automatiquement tous les niveaux suivants.

### 4.2 Ce que doit démontrer un test

Un test bien conçu doit permettre de répondre à ces questions :

- La bonne sauvegarde a-t-elle été sélectionnée ?
- Le point de restauration est-il disponible ?
- Les données sont-elles lisibles ?
- Les permissions nécessaires sont-elles présentes ?
- Les clés et secrets sont-ils disponibles ?
- Les dépendances sont-elles accessibles ?
- Le système peut-il démarrer ?
- L'application fonctionne-t-elle ?
- Le propriétaire métier confirme-t-il le résultat ?
- Le délai obtenu respecte-t-il l'objectif ?
- La procédure est-elle suffisamment claire pour être exécutée par une autre personne ?

### 4.3 Les tests révèlent les dépendances cachées

Un serveur applicatif peut être sauvegardé correctement sans que l'entreprise sache comment restaurer :

- Son service d'authentification.
- Ses certificats.
- Sa configuration DNS.
- Ses secrets de connexion.
- Ses règles réseau.
- Sa base de données.
- Ses fichiers de configuration.
- Son ordonnanceur de tâches.
- Ses fichiers de licence.
- Ses services externes.

Un test de reprise doit vérifier les dépendances nécessaires au fonctionnement réel, et pas seulement la présence des fichiers.

## 5. Distinguer les types de tests

### 5.1 Vérification d'intégrité

Ce test cherche à détecter certaines erreurs dans les données ou les structures de sauvegarde.

Il peut vérifier :

- La cohérence des métadonnées.
- L'intégrité des blocs.
- Les fichiers de sauvegarde.
- Les sommes de contrôle.
- Les objets stockés.
- La cohérence des références internes.

Exemples de mécanismes : vérification d'un dépôt Restic, tâches de vérification Proxmox Backup Server ou contrôles d'intégrité d'une solution d'entreprise.

Une vérification d'intégrité ne démontre pas que l'application peut fonctionner après une restauration.

### 5.2 Test de restauration de fichier

Il consiste à récupérer un ou plusieurs fichiers dans un emplacement de test.

Il vérifie notamment :

- La disponibilité du dépôt.
- La sélection du point de restauration.
- La récupération des données.
- La lisibilité des fichiers.
- Les permissions attendues.
- La durée de l'opération.

Ce test est simple, mais il ne suffit pas pour valider une reprise de base de données ou d'application.

### 5.3 Test de restauration de système

Le test peut concerner une machine virtuelle, un serveur physique ou un système d'exploitation.

Il doit vérifier :

- La récupération de la configuration.
- La présence des disques nécessaires.
- Le démarrage.
- Les interfaces réseau.
- Les services système.
- Les comptes et permissions.
- L'accès aux dépendances.

Le système peut démarrer sans que son application soit fonctionnelle.

### 5.4 Test applicatif

Il consiste à valider des fonctions pertinentes du service restauré.

Exemples :

- L'utilisateur peut s'authentifier.
- Une page s'affiche.
- Une recherche fonctionne.
- Une transaction de test réussit.
- Une donnée peut être lue.
- Une sauvegarde applicative complémentaire peut être restaurée.
- Les journaux ne signalent pas une erreur bloquante.

Le propriétaire applicatif doit définir les critères de réussite.

### 5.5 Test de reprise complète

Ce test vérifie un scénario plus large, comme la perte du site principal ou la reconstruction d'un environnement critique.

Il peut inclure :

- La déclaration du sinistre.
- L'activation de la cellule de crise.
- L'accès aux procédures.
- La récupération des identités.
- La restauration des données.
- Le démarrage des services dans l'ordre.
- La validation des applications.
- La communication avec les utilisateurs.
- Le retour vers l'environnement normal.

Un test complet implique généralement davantage de risques, de ressources et de coordination qu'un test de fichier.

## 6. Les différents formats d'exercice PRA

### 6.1 Revue documentaire

La revue documentaire vérifie que les procédures, contacts et informations sont présents, compréhensibles et à jour.

Questions à vérifier :

- Les contacts d'urgence existent-ils ?
- Les responsabilités sont-elles explicites ?
- Les coordonnées sont-elles encore valides ?
- Les dernières versions des procédures sont-elles accessibles ?
- Les dépendances sont-elles documentées ?
- Les sauvegardes attendues existent-elles ?
- Les secrets nécessaires sont-ils récupérables ?
- Les critères de reprise sont-ils définis ?

Cette revue peut révéler des lacunes sans interrompre les services.

### 6.2 Exercice sur table

L'exercice sur table consiste à simuler un scénario et à demander aux participants de décrire leurs décisions et actions.

Aucune destruction réelle ni interruption de production n'est nécessaire.

Exemple :

```text
SCENARIO
Le site informatique principal devient indisponible.

QUESTION 1
Qui déclare le sinistre ?

QUESTION 2
Quel service doit être rétabli en premier ?

QUESTION 3
Où se trouvent les copies de sauvegarde ?

QUESTION 4
Comment récupérer les identités et les accès ?

QUESTION 5
Qui valide le retour au fonctionnement normal ?
```

L'exercice doit révéler les problèmes de coordination, les dépendances oubliées et les décisions qui ne sont attribuées à personne.

### 6.3 Test technique ciblé

Il teste une opération bien définie, par exemple la restauration d'une base de données ou d'une VM.

Il doit préciser les prérequis, le point de restauration, l'environnement, le délai mesuré et les critères de réussite.

### 6.4 Exercice de récupération isolée

Les systèmes sont restaurés dans un environnement séparé qui empêche les conflits avec la production.

Cette approche est particulièrement utile pour tester :

- Le démarrage de VM.
- Les dépendances réseau.
- Les applications.
- La cohérence des données.
- Les procédures de reprise après compromission.

### 6.5 Test parallèle

Un environnement de reprise est activé sans interrompre le service de production, dans les limites du scénario.

L'objectif consiste à vérifier la capacité du site de secours à accueillir ou exécuter les services.

Il faut éviter que les deux environnements deviennent actifs simultanément lorsque cela risque de créer des conflits de données, d'identité ou de routage.

### 6.6 Test de basculement complet

Le service bascule réellement vers un environnement de reprise.

Ce test est plus exigeant, car il peut avoir un impact sur les utilisateurs. Il nécessite une fenêtre, des autorisations, des critères d'arrêt et un plan de retour arrière.

Il ne doit pas être exécuté sur une production critique sans préparation, validation des risques et coordination.

### 6.7 Choisir le bon niveau de test

| Type de test | Impact possible | Objectif |
|---|---|---|
| Revue documentaire | Très faible | Vérifier les procédures et les responsabilités |
| Exercice sur table | Faible | Vérifier les décisions et la coordination |
| Restauration de fichier | Faible à modéré | Vérifier une récupération ciblée |
| Restauration de VM isolée | Modéré | Vérifier le système et certains services |
| Test applicatif complet | Modéré | Vérifier les fonctions métier |
| Test parallèle | Variable | Vérifier l'environnement de reprise |
| Basculement complet | Élevé | Vérifier une reprise opérationnelle réelle |

Le niveau de test doit correspondre à la criticité et aux risques du service.

## 7. Analyse d'impact métier (BIA)

### 7.1 Pourquoi réaliser une BIA ?

L'analyse d'impact métier, ou *Business Impact Analysis*, permet d'identifier les activités essentielles et d'évaluer les conséquences d'une interruption.

Elle sert à déterminer les priorités de reprise et les objectifs attendus.

Sans BIA, les équipes peuvent consacrer beaucoup d'efforts à restaurer des systèmes secondaires alors que les services véritablement critiques restent indisponibles.

### 7.2 Questions à poser

Pour chaque activité métier :

- À quoi sert-elle ?
- Qui en est responsable ?
- Combien d'utilisateurs sont concernés ?
- Quel est l'impact après une heure d'interruption ?
- Quel est l'impact après huit heures ?
- Quel est l'impact après une journée ?
- Quelles obligations doivent être respectées ?
- Quelles données peuvent être perdues ?
- Quel délai maximal d'interruption est acceptable ?
- Existe-t-il un mode de fonctionnement manuel ?
- Quels systèmes sont indispensables ?

### 7.3 Exemple de BIA

| Activité | Impact après une heure | Impact après une journée | Priorité illustrative |
|---|---|---|---|
| Paiement et facturation | Transactions ralenties | Pertes financières et retards importants | Critique |
| Service d'identité | Accès perturbés | Blocage de nombreux services | Critique |
| Portail documentaire | Perturbation modérée | Retards de traitement | Élevée |
| Environnement de test | Faible | Retards de développement | Faible |
| Reporting secondaire | Peu d'impact immédiat | Analyse métier retardée | Moyenne |

Ce tableau est fictif. Chaque organisation doit effectuer sa propre analyse.

### 7.4 Relier la BIA aux systèmes

Une activité peut dépendre de plusieurs composants.

Exemple :

```text
ACTIVITE : FACTURATION
          |
          v
Application de facturation
          |
          +----------> Base de données
          |
          +----------> Service d'identité
          |
          +----------> DNS
          |
          +----------> Réseau
          |
          +----------> Certificats
          |
          +----------> Stockage
```

Le PRA doit tenir compte de ces dépendances.

La restauration de l'application seule ne suffit pas si elle ne peut pas contacter la base de données ou authentifier les utilisateurs.

## 8. RPO, RTO et autres mesures de reprise

### 8.1 RPO : Recovery Point Objective

Le RPO définit la perte maximale de données acceptable, exprimée en temps.

Exemple :

```text
Dernière version récupérable : 10 h 00
Incident :                    12 h 00

Perte potentielle :            2 heures
```

Si le RPO demandé est de trente minutes, ce point de restauration n'est pas suffisant à lui seul.

Le RPO doit être évalué à partir du dernier point réellement récupérable, et pas uniquement de l'heure du dernier job déclaré réussi.

### 8.2 RTO : Recovery Time Objective

Le RTO est le délai cible de rétablissement du service.

Il faut en définir le début et la fin de manière précise.

Exemple :

```text
Début de l'incident       : 10 h 00
Décision de reprise       : 10 h 20
Restauration terminée     : 11 h 00
Service validé            : 11 h 40
```

Si l'organisation mesure le RTO jusqu'à la validation complète du service, le délai est de 1 heure et 40 minutes.

Le temps de copie des données ne représente donc qu'une partie du temps de reprise.

### 8.3 Définir le début du RTO

La convention de mesure doit préciser si le calcul commence :

- À la détection de l'incident.
- À la déclaration officielle du sinistre.
- À la décision d'activer le PRA.
- À la première indisponibilité constatée.

La convention doit être connue des équipes et cohérente avec les engagements internes ou contractuels.

### 8.4 Définir la fin du RTO

La fin peut correspondre à différents événements :

- Démarrage du serveur.
- Disponibilité technique de l'application.
- Validation des tests.
- Autorisation de réouverture aux utilisateurs.
- Validation métier.

Pour un service critique, il est généralement préférable de définir une fin qui corresponde au retour opérationnel réel du service, et non au seul démarrage d'une VM.

### 8.5 RPO et RTO mesurés

Les objectifs sont des cibles. Les résultats des tests fournissent les mesures réellement obtenues.

| Indicateur | Cible fictive | Résultat du test | Conclusion |
|---|---:|---:|---|
| RPO | 30 min | 18 min de données perdues | Objectif respecté |
| RTO | 2 h | 2 h 25 min | Objectif dépassé |
| Validation applicative | 20 min après démarrage | 35 min | Amélioration nécessaire |

Il faut documenter les hypothèses, le scénario, l'environnement et les conditions du test pour interpréter les résultats correctement.

### 8.6 MTTR et autres métriques

Le terme MTTR peut être utilisé pour désigner le temps moyen de réparation ou de rétablissement selon le contexte.

Il est important de définir explicitement la mesure retenue, car le même sigle est utilisé avec plusieurs significations.

Autres indicateurs utiles :

- Âge du dernier point de restauration valide.
- Taux de réussite des tests.
- Taux de couverture des systèmes.
- Durée des restaurations.
- Nombre de dépendances non documentées.
- Nombre de procédures non testées.
- Nombre d'écarts PRA non corrigés.

## 9. Construire la matrice de criticité

### 9.1 Relier priorité métier et objectifs de reprise

La criticité doit guider les efforts de sauvegarde et de restauration.

| Classe | Niveau de criticité | Exemple de priorité |
|---|---|---|
| C1 | Critique | Service de paiement, identité centrale |
| C2 | Élevée | Application métier principale |
| C3 | Modérée | Partage documentaire courant |
| C4 | Faible | Environnement de test reconstructible |

Le nombre de classes et leurs définitions doivent être adaptés à l'organisation.

### 9.2 Exemple de matrice

| Service | Classe | RPO cible | RTO cible | Ordre de reprise |
|---|---|---|---|---:|
| Identité centrale | C1 | 15 min | 1 h | 1 |
| DNS et services essentiels | C1 | Selon la charge | 1 h | 2 |
| Base transactionnelle | C1 | 15 min | 1 h 30 | 3 |
| API métier | C1 | Selon les données | 2 h | 4 |
| Partage documentaire | C2 | 4 h | 4 h | 5 |
| Reporting non critique | C3 | 24 h | 24 h | 6 |
| Laboratoire de test | C4 | 24 h ou davantage | 48 h | 7 |

Ces objectifs sont illustratifs. Une activité peut demander des valeurs différentes après analyse.

### 9.3 Priorité ne signifie pas indépendance

Il ne suffit pas de classer les services du plus important au moins important.

Certains composants moins visibles peuvent conditionner le rétablissement des services prioritaires.

Par exemple, le service DNS ou le système d'identité peut ne pas être perçu comme une application métier, mais il peut être indispensable à plusieurs applications critiques.

La priorité de reprise doit donc tenir compte de la criticité et des dépendances.

## 10. Cartographier les dépendances

### 10.1 Pourquoi documenter les dépendances ?

La reprise peut échouer si une application est restaurée avant ses services indispensables.

Les dépendances peuvent être :

- Techniques.
- Réseau.
- Identité.
- Données.
- DNS.
- Sécurité.
- Licences.
- Externes.
- Organisationnelles.

### 10.2 Exemple d'arbre de dépendances

```text
SERVICE METIER
      |
      v
APPLICATION
      |
      +----------> BASE DE DONNEES
      |
      +----------> AUTHENTIFICATION
      |
      +----------> DNS
      |
      +----------> CERTIFICATS
      |
      +----------> STOCKAGE
      |
      +----------> RESEAU
```

La restauration d'une application suppose que tous les composants nécessaires soient accessibles ou que des procédures de remplacement temporaires existent.

### 10.3 Dépendances cycliques

Certains environnements comportent des dépendances croisées.

Par exemple, le système d'administration des sauvegardes peut dépendre du service d'identité du site principal, alors que ce service d'identité doit lui-même être restauré depuis les sauvegardes.

Il faut prévoir un accès de secours contrôlé, des comptes d'urgence, une documentation disponible hors ligne et des procédures permettant de récupérer les composants fondamentaux.

Ces mécanismes doivent être protégés afin de ne pas devenir une porte d'entrée incontrôlée vers l'infrastructure.

### 10.4 Construire un graphe de dépendances

Un inventaire exploitable peut contenir :

```text
Composant :
Service dépendant :
Nature de la dépendance :
Adresse ou référence :
Responsable :
Criticité :
Ordre de reprise :
Solution de secours :
Méthode de validation :
```

Ce graphe doit être mis à jour lorsque les architectures évoluent.

Il peut être tenu dans une CMDB, un dépôt documentaire versionné ou un outil de gestion de configuration.

## 11. Définir un ordre de reprise

### 11.1 Pourquoi l'ordre compte-t-il ?

Restaurer les systèmes dans un ordre incorrect peut provoquer des échecs ou compliquer les diagnostics.

Exemple : une application est démarrée avant sa base de données. Elle échoue au démarrage et doit être redémarrée ultérieurement.

### 11.2 Exemple d'ordre de reprise

```text
PHASE 1 : PREPARATION
  |
  +--> Déclaration du sinistre
  +--> Accès aux procédures
  +--> Vérification des dépôts
  +--> Sécurisation de l'environnement
  |
  v
PHASE 2 : INFRASTRUCTURE
  |
  +--> Réseau
  +--> Stockage
  +--> Virtualisation
  +--> Services fondamentaux
  |
  v
PHASE 3 : DONNEES
  |
  +--> Base de données
  +--> Fichiers critiques
  +--> Dépendances métier
  |
  v
PHASE 4 : APPLICATIONS
  |
  +--> API
  +--> Services intermédiaires
  +--> Frontends
  |
  v
PHASE 5 : VALIDATION
  |
  +--> Tests techniques
  +--> Tests métier
  +--> Autorisation de reprise
  |
  v
PHASE 6 : COMMUNICATION
      |
      +--> Notification aux équipes
      +--> Retour au fonctionnement normal
```

Cet ordre représente un modèle générique. Il faut le personnaliser en fonction des dépendances réelles.

### 11.3 Les groupes de reprise

Il peut être utile de définir des groupes de services qui seront restaurés ensemble.

Exemple :

- Groupe A : accès et infrastructure essentielle.
- Groupe B : données et bases.
- Groupe C : services applicatifs.
- Groupe D : accès utilisateurs.
- Groupe E : services secondaires.

Cela permet de piloter le rétablissement en fonction des dépendances et de mesurer les objectifs de chaque groupe.

## 12. Préparer un plan de reprise exploitable

### 12.1 Le contenu minimum

Un PRA doit être suffisamment précis pour être exécuté pendant une situation stressante.

Il devrait inclure :

- Objet et périmètre.
- Scénarios couverts.
- Critères de déclenchement.
- Rôles et responsabilités.
- Contacts d'urgence.
- Liste des services.
- RPO et RTO cibles.
- Dépendances.
- Emplacements de sauvegarde.
- Identités et accès de secours.
- Procédures de restauration.
- Ordre de démarrage.
- Critères de validation.
- Consignes de communication.
- Conditions de retour à la normale.
- Procédures de nettoyage.
- Emplacement des preuves et des comptes rendus.

### 12.2 Fiche de synthèse d'un service

```text
SERVICE :
PROPRIETAIRE METIER :
RESPONSABLE TECHNIQUE :
NIVEAU DE CRITICITE :

RPO CIBLE :
RTO CIBLE :

DEPENDANCES :
- Réseau :
- Identité :
- DNS :
- Stockage :
- Base de données :
- Services externes :

DERNIER POINT DE RESTAURATION VALIDE :
EMPLACEMENT DE LA COPIE :
METHODE DE RESTAURATION :
PROCEDURE DE DEMARRAGE :
TESTS TECHNIQUES :
TESTS METIER :
CRITERE DE REPRISE :

RESPONSABLE DE VALIDATION :
PROCEDURE DE RETOUR ARRIERE :
```

Cette fiche doit être accessible même lorsque les principaux outils de documentation du site principal sont indisponibles.

### 12.3 Documents hors ligne

Une procédure de reprise ne doit pas être disponible uniquement sur le système susceptible d'être perdu.

Prévoir des copies sécurisées accessibles en cas de panne majeure, dans le respect des règles de confidentialité.

Les secrets doivent être protégés séparément et leur récupération doit suivre une procédure formelle.

### 12.4 Contrôle des accès de secours

Les comptes d'urgence doivent :

- Être documentés.
- Avoir un périmètre défini.
- Être protégés.
- Être surveillés.
- Disposer d'une procédure de rotation.
- Être testés sans compromettre la production.
- Faire l'objet d'une revue après chaque utilisation.

Un compte d'urgence ne doit pas être confondu avec un compte partagé dont personne ne contrôle l'utilisation.

## 13. Organiser les tests de restauration

### 13.1 Définir un programme de tests

Une entreprise doit déterminer ce qui sera testé, à quelle fréquence, par qui et avec quels critères de réussite.

Un exemple de programme :

| Test | Fréquence illustrative | Responsable |
|---|---|---|
| Restauration de fichier | Mensuelle | Équipe de sauvegarde |
| Restauration de VM isolée | Trimestrielle | Équipe systèmes |
| Restauration de base | Trimestrielle ou selon criticité | Équipe base de données |
| Reprise d'une application critique | Semestrielle | Équipe applicative et exploitation |
| Exercice sur table PRA | Semestrielle | Coordination de crise |
| Reprise du site secondaire | Annuelle ou selon le risque | Équipes infrastructure et métier |
| Restauration après compromission | Selon le risque et le programme de sécurité | Sécurité et exploitation |

Les fréquences doivent être définies par l'organisation en fonction de la criticité, des risques, des obligations et des capacités d'exploitation.

### 13.2 Un test doit commencer par un périmètre clair

Avant le test, préciser :

- Les systèmes concernés.
- Le point de restauration.
- L'environnement cible.
- Les ressources disponibles.
- Les risques.
- Les personnes impliquées.
- Les étapes prévues.
- Les critères d'arrêt.
- Les critères de réussite.
- Les données interdites d'exposition.
- Les procédures de nettoyage.

Un test sans périmètre clair peut produire des données inutilisables ou affecter la production.

### 13.3 Définir un test reproductible

Un test doit contenir assez d'informations pour être répété.

Exemple :

```text
ID TEST : RESTORE-VM-001

Objectif :
  Restaurer une VM depuis une sauvegarde.

Source :
  VM de laboratoire.

Point de restauration :
  Dernière sauvegarde validée avant la modification.

Cible :
  Réseau isolé de test.

Contrôles :
  - VM restaurée.
  - Système démarré.
  - Fichier connu présent.
  - Service attendu actif.
  - Accès réseau contrôlé.

Critère de succès :
  Tous les contrôles réussissent dans le RTO prévu.
```

Les informations d'identification, les secrets et les données sensibles ne doivent pas être inscrits en clair dans un document partagé.

## 14. Tests automatiques de restauration

### 14.1 Pourquoi automatiser les tests ?

Les restaurations manuelles sont nécessaires pour les opérations complexes, mais elles sont coûteuses à répéter.

L'automatisation peut réduire la charge et augmenter la fréquence des contrôles.

Elle peut inclure :

- Le démarrage isolé d'une VM restaurée.
- La vérification de l'état du système.
- Un test de connectivité.
- Une requête applicative.
- Une comparaison de données.
- Une capture du résultat.
- La génération d'un rapport.

L'automatisation doit être adaptée aux limites de la plateforme. Elle ne remplace pas les validations métier difficiles à automatiser.

### 14.2 Exemple avec Veeam SureBackup

Veeam propose SureBackup pour vérifier la récupérabilité de sauvegardes selon les fonctionnalités disponibles dans la version et la licence utilisées.

La documentation distingue notamment les tests complets de récupérabilité dans un environnement isolé et les modes de vérification de sauvegarde ou d'analyse de contenu.

La validation peut inclure le démarrage de machines depuis les sauvegardes et des tests applicatifs.

Documentation officielle :

https://helpcenter.veeam.com/docs/vbr/userguide/recovery_verification_surebackup_job.html

https://helpcenter.veeam.com/docs/vbr/userguide/surebackup_hiw.html

Avant d'utiliser cette fonctionnalité, vérifier les prérequis, les composants requis et les conditions de licence de l'environnement.

### 14.3 Exemple avec Proxmox Backup Server

Proxmox Backup Server propose des tâches de vérification de sauvegardes permettant de contrôler l'intégrité des données stockées.

Il est conseillé d'organiser les vérifications périodiques selon la documentation et le volume des sauvegardes.

Cependant, une vérification d'intégrité ne remplace pas une restauration testée d'une VM avec validation applicative.

Documentation officielle :

https://pbs.proxmox.com/docs/maintenance.html

### 14.4 Distinguer les résultats

Un rapport d'automatisation doit distinguer :

```text
BackupIntegrity = PASS
RestoreTest     = PASS
SystemBoot      = PASS
ApplicationTest = FAIL
BusinessTest    = NOT RUN
```

Dans cet exemple, les données sont considérées comme intègres et le système démarre, mais le test applicatif échoue.

Il ne faut pas déclarer la reprise réussie sur la base du seul résultat d'intégrité.

## 15. Restaurer une machine virtuelle dans un environnement isolé

### 15.1 Pourquoi isoler ?

Restaurer une VM dans le même réseau que sa production peut créer des conflits :

- Adresse IP dupliquée.
- Nom DNS identique.
- Nom de machine en conflit.
- Double démarrage de tâches planifiées.
- Connexions à une base de production.
- Traitement de messages en double.
- Réplication involontaire.
- Envoi de courriels aux utilisateurs.
- Déclenchement d'opérations financières.

Une VM restaurée pour un test ne doit pas être autorisée à modifier les systèmes de production.

### 15.2 Architecture de laboratoire

```text
                 PRODUCTION
                     |
                     v
             DEPOT DE SAUVEGARDE
                     |
                     v
              POINT RESTAURABLE
                     |
                     v
             ENVIRONNEMENT ISOLE
                     |
             +-------+-------+
             |               |
             v               v
         VM restauree    Réseau de test
             |
             v
      Tests sans impact métier
```

L'environnement de test doit être suffisamment réaliste pour valider les services, mais séparé de la production.

### 15.3 Contrôler le réseau de test

Avant le démarrage, définir :

- Les réseaux disponibles.
- Les routes autorisées.
- Les communications interdites.
- Les règles DNS.
- Les éventuels accès sortants.
- Les accès d'administration.
- La politique d'isolement.
- Les conditions de destruction de l'environnement.

Les exceptions réseau doivent être temporaires, documentées et supprimées après le test.

### 15.4 Tests à effectuer sur la VM

Une recette peut inclure :

1. Vérifier le nombre de disques attendus.
2. Vérifier la configuration matérielle virtuelle.
3. Démarrer la VM.
4. Attendre la disponibilité du système d'exploitation.
5. Contrôler les journaux de démarrage.
6. Vérifier les interfaces.
7. Vérifier l'état des services.
8. Lire un fichier de référence.
9. Effectuer un test applicatif.
10. Enregistrer le résultat.
11. Arrêter puis supprimer l'environnement de test selon la procédure.

La suppression doit être effectuée uniquement après la collecte des preuves et la confirmation que le test est terminé.

## 16. Tests de restauration d'une base de données

### 16.1 Pourquoi le test doit-il être spécifique à la base ?

Une base de données peut être constituée de plusieurs fichiers, journaux et structures internes.

Il faut garantir une restauration cohérente et vérifier la capacité à lire les données après récupération.

Le système peut démarrer tout en présentant des erreurs logiques, des extensions manquantes ou des données incompatibles avec la version applicative.

### 16.2 Plan de test

```text
Sauvegarde de référence
         |
         v
Préparer une base de test
         |
         v
Restaurer les données
         |
         v
Vérifier la cohérence du moteur
         |
         v
Exécuter des requêtes de contrôle
         |
         v
Valider les données attendues
         |
         v
Démarrer l'application liée
         |
         v
Valider les opérations métier
```

### 16.3 Définir des contrôles fonctionnels

Les contrôles doivent être liés à l'application.

Exemples :

- La base accepte une connexion.
- Les objets attendus existent.
- Le nombre de lignes se situe dans la plage attendue.
- Des identifiants de référence sont présents.
- Les relations entre tables sont cohérentes.
- Une requête métier renvoie le résultat attendu.
- Les données les plus récentes sont compatibles avec le RPO.
- Les utilisateurs et permissions requis sont disponibles.

Un simple contrôle `SELECT 1` confirme seulement qu'une requête de base peut être exécutée. Il ne garantit pas la cohérence complète de la base métier.

### 16.4 PostgreSQL : contrôle après restauration

Après une restauration d'un export compatible, des vérifications peuvent être exécutées avec `psql`.

Exemple :

```sql
SELECT current_database();
SELECT count(*) FROM table_de_reference;
```

`table_de_reference` est un nom fictif à remplacer par une table réellement pertinente.

Il faut comparer le résultat à une attente connue. Un nombre de lignes peut varier normalement si le service est actif ; il faut donc choisir un critère adapté à l'instant de sauvegarde.

### 16.5 Ne jamais restaurer un test directement sur la base de production

Un test de restauration doit utiliser une destination isolée, sauf procédure de reprise autorisée et explicitement planifiée.

Une restauration directe peut écraser des données plus récentes ou provoquer des incohérences avec d'autres systèmes.

## 17. Tests de restauration des services d'identité

Les services d'identité sont souvent des dépendances fondamentales du système d'information.

Un environnement peut avoir besoin d'Active Directory, de DNS, de NTP, de certificats, de comptes de service et de mécanismes d'authentification pour restaurer ses autres systèmes.

### 17.1 Pourquoi tester ces services séparément ?

Sans une stratégie d'identité et d'accès de secours, les équipes peuvent ne pas parvenir à administrer le système de sauvegarde ou à restaurer les composants fondamentaux.

Il faut étudier :

- Les comptes d'urgence.
- L'accès administrateur hors bande.
- Les dépendances DNS.
- Les paramètres horaires.
- Les certificats.
- Les secrets nécessaires.
- Les politiques de restauration du service d'identité.
- Les procédures de validation.
- Les risques de restauration d'un ancien état.

### 17.2 Exemple de chaîne de dépendance

```text
Accès à la console
        |
        v
Compte d'administration de secours
        |
        v
Réseau de récupération
        |
        v
DNS / NTP / Identité
        |
        v
Administration des serveurs
        |
        v
Restauration des applications
```

Cette architecture est conceptuelle. L'ordre de récupération précis doit suivre les procédures officielles du produit d'identité concerné.

### 17.3 Risques de restauration d'un service d'identité

Une restauration incorrecte d'un service d'identité peut provoquer des incohérences de réplication, des problèmes de confiance ou des erreurs d'authentification.

Il ne faut pas appliquer une procédure générique de restauration à tous les contrôleurs de domaine ou composants d'identité. Respecter les procédures officielles correspondant au service et à sa version.

## 18. Préparer la reprise après rançongiciel

### 18.1 Pourquoi le scénario cyber est différent

Une panne matérielle rend généralement un composant indisponible. Un rançongiciel peut compromettre plusieurs systèmes et chercher à détruire les sauvegardes.

La reprise comporte alors deux objectifs :

1. Éliminer ou contenir la menace.
2. Rétablir les systèmes à partir de données propres et de procédures fiables.

Restaurer des machines sans maîtriser l'incident peut réintroduire des systèmes compromis.

### 18.2 Chaîne de reprise cyber

```text
SUSPICION D'ATTAQUE
        |
        v
DECLARATION ET COORDINATION
        |
        v
CONFINEMENT
        |
        v
COLLECTE DES ELEMENTS NECESSAIRES
        |
        v
EVALUATION DES SYSTEMES COMPROMIS
        |
        v
VERIFICATION DES SAUVEGARDES
        |
        v
ENVIRONNEMENT DE RECUPERATION PROPRE
        |
        v
RESTAURATION PRIORISEE
        |
        v
PATCH / ROTATION DES SECRETS / CONTROLES
        |
        v
VALIDATION TECHNIQUE ET METIER
        |
        v
RECONNEXION PROGRESSIVE
```

L'ordre exact dépend de l'incident, des obligations de conservation de preuves et de l'expertise mobilisée.

### 18.3 Ne pas restaurer immédiatement après la détection

Avant de restaurer :

- Identifier le périmètre compromis.
- Préserver les preuves utiles.
- Contenir les systèmes touchés.
- Vérifier que les comptes d'administration ne sont pas compromis.
- Déterminer quelles sauvegardes précèdent l'intrusion.
- Vérifier l'intégrité et la provenance des copies.
- Construire un environnement propre.
- Examiner les risques de réinfection.

Les décisions de réponse à incident doivent être prises avec l'équipe sécurité et selon les exigences de l'organisation.

### 18.4 Le point de restauration sain

La sauvegarde la plus récente n'est pas nécessairement la meilleure.

Un point de restauration peut contenir une configuration malveillante ou une charge compromise si l'incident est resté indétecté pendant plusieurs jours ou semaines.

La sélection du point de restauration doit donc considérer :

- La chronologie de l'intrusion.
- Les alertes et indicateurs de compromission.
- Les modifications suspectes.
- Les journaux.
- Les résultats d'analyse des sauvegardes.
- Les versions antérieures disponibles.
- Les exigences de récupération des données.

Le choix doit s'appuyer sur des preuves, pas uniquement sur la date la plus récente.

### 18.5 Contrôles avant la remise en service

- Réinitialiser les comptes compromis.
- Révoquer les sessions et secrets concernés.
- Appliquer les correctifs nécessaires.
- Vérifier les configurations système.
- Examiner les tâches planifiées.
- Contrôler les mécanismes de démarrage.
- Vérifier les services exposés.
- Contrôler les règles réseau.
- Scanner les systèmes selon la procédure retenue.
- Valider les applications.
- Réintroduire les systèmes progressivement.

L'équipe sécurité doit valider que le risque de réinfection est acceptable avant la reconnexion de systèmes sensibles.

Les recommandations de la CISA mettent notamment l'accent sur des sauvegardes hors ligne et chiffrées, des tests réguliers de restauration et la protection contre la suppression des copies.

Documentation officielle : https://www.cisa.gov/stopransomware/ransomware-guide

## 19. Définir un environnement de récupération propre

### 19.1 Qu'est-ce qu'un environnement de récupération ?

C'est un environnement préparé pour restaurer et contrôler les systèmes sans dépendre totalement de l'infrastructure potentiellement compromise.

Il peut nécessiter :

- Des hôtes physiques ou virtuels.
- Un réseau isolé.
- Un accès d'administration dédié.
- Un DNS de récupération.
- Un système de sauvegarde accessible.
- Les images de référence.
- Les installations logicielles.
- Les certificats et secrets nécessaires.
- Les outils de diagnostic.
- La documentation du PRA.

### 19.2 Exemple d'architecture

```text
             ENVIRONNEMENT COMPROMIS
                       |
                 Accès restreint
                       |
                       X
                       |
                       v
              DEPOT DE SAUVEGARDE
                       |
                       v
             ENVIRONNEMENT DE RECUPERATION
                       |
              +--------+--------+
              |                 |
              v                 v
        Infrastructure       Accès sécurisé
        propre               de secours
              |
              v
        Systèmes restaurés
              |
              v
        Contrôles de sécurité
              |
              v
        Validation applicative
              |
              v
        Autorisation de reprise
```

L'accès au dépôt doit être contrôlé et isolé autant que possible. Une simple séparation logique ne suffit pas nécessairement si les identités ou les droits d'administration restent compromis.

### 19.3 Images de référence

Les images de référence permettent de reconstruire certains systèmes de manière reproductible.

Elles doivent :

- Être maintenues.
- Être identifiées par une version.
- Être vérifiées.
- Être protégées contre les modifications non autorisées.
- Être conservées dans un emplacement récupérable.
- Être dépourvues de secrets permanents non nécessaires.
- Être compatibles avec les procédures de reprise.

Une image ancienne peut contenir des vulnérabilités. Le PRA doit préciser si les correctifs seront appliqués avant ou après le démarrage, selon le risque.

## 20. Scénarios PRA à préparer

Un plan de reprise robuste ne doit pas couvrir uniquement la panne d'un serveur.

### 20.1 Panne d'un disque

Objectif :

- Vérifier la disponibilité des données.
- Remplacer le composant défaillant selon le plan.
- Contrôler l'intégrité.
- Vérifier le fonctionnement du stockage.
- Vérifier les sauvegardes supplémentaires si nécessaire.

### 20.2 Perte d'un hyperviseur

Objectif :

- Vérifier que les charges concernées disposent de points de restauration.
- Vérifier la capacité de l'environnement de reprise.
- Restaurer les VM prioritaires.
- Contrôler le réseau et les disques.
- Valider les applications.
- Mesurer le RTO.

### 20.3 Perte du stockage principal

Objectif :

- Accéder à un dépôt indépendant.
- Retrouver les points de restauration.
- Disposer d'une capacité de stockage cible.
- Restaurer les données ou les machines.
- Valider leur intégrité.
- Mesurer les délais.

### 20.4 Perte du site principal

Objectif :

- Déclarer le sinistre.
- Activer les procédures de communication.
- Accéder au site secondaire.
- Récupérer les systèmes fondamentaux.
- Restaurer les services selon leurs priorités.
- Valider la disponibilité métier.
- Organiser la continuité des opérations.

### 20.5 Compromission des identités

Objectif :

- Bloquer les accès compromis selon les procédures.
- Utiliser les mécanismes d'administration de secours.
- Préserver les accès indispensables aux dépôts.
- Réinitialiser les secrets concernés.
- Contrôler les autorisations.
- Reprendre les opérations à partir d'un environnement propre.

### 20.6 Compromission du système de sauvegarde

Objectif :

- Isoler le serveur de gestion affecté.
- Vérifier l'état des dépôts.
- Conserver les preuves nécessaires.
- Accéder à une copie indépendante.
- Reconstruire le plan de contrôle si nécessaire.
- Restaurer la gestion des sauvegardes.
- Vérifier les autorisations.
- Lancer des tests de récupération.

### 20.7 Perte d'une application critique

Objectif :

- Retrouver la version de données appropriée.
- Restaurer les dépendances.
- Recréer ou récupérer les systèmes.
- Vérifier les opérations métier.
- Valider l'intégrité des données.
- Mesurer le RPO et le RTO.
- Documenter les écarts.

## 21. Organiser une cellule de crise

### 21.1 Pourquoi une structure de décision est nécessaire

En situation de crise, plusieurs équipes peuvent intervenir en même temps.

Sans organisation, elles risquent de réaliser des actions contradictoires, d'ignorer des dépendances ou de perdre du temps à déterminer qui doit approuver une décision.

### 21.2 Rôles possibles

| Rôle | Responsabilité principale |
|---|---|
| Responsable de crise | Coordonne les décisions |
| Responsable technique | Suit la reprise des systèmes |
| Responsable sécurité | Évalue la compromission et les risques cyber |
| Responsable sauvegarde | Localise les points de restauration |
| Responsable applicatif | Valide les fonctions du service |
| Responsable métier | Confirme le besoin et la priorité |
| Responsable communication | Organise les messages aux parties concernées |
| Responsable documentation | Conserve la chronologie et les décisions |

Dans une petite organisation, une même personne peut assumer plusieurs rôles. Les responsabilités doivent toutefois être clairement définies.

### 21.3 Matrice RACI

RACI signifie :

- Responsible : réalise l'action.
- Accountable : porte la responsabilité finale.
- Consulted : est consulté.
- Informed : est informé.

Exemple :

| Activité | Crise | Systèmes | Sécurité | Application | Métier |
|---|---|---|---|---|---|
| Déclarer le sinistre | A | C | C | I | I |
| Identifier les sauvegardes | I | R | C | C | I |
| Valider le point de restauration | A | R | C | C | C |
| Restaurer l'infrastructure | I | A/R | C | C | I |
| Contrôler une compromission | I | C | A/R | C | I |
| Valider l'application | I | C | C | R | A |
| Autoriser la reprise métier | C | C | C | R | A |
| Communiquer aux utilisateurs | A/R | I | C | C | C |

La matrice doit être ajustée à l'organisation et aux contrats. Les activités critiques doivent posséder un responsable final clairement identifié.

## 22. Communication pendant la reprise

### 22.1 Les informations à communiquer

Une communication de crise doit préciser :

- Ce qui est connu.
- Le périmètre impacté.
- Les services indisponibles.
- Les mesures en cours.
- Les décisions prises.
- Les risques identifiés.
- La prochaine étape.
- L'heure de la prochaine mise à jour.

Il faut distinguer les faits confirmés des hypothèses.

### 22.2 Exemple de communication initiale

```text
Incident :
Indisponibilité du site informatique principal

Détection :
10 h 15

Impact confirmé :
Plusieurs services internes sont indisponibles.

Actions en cours :
Les équipes évaluent les systèmes affectés et
vérifient la disponibilité des copies de sauvegarde.

Décisions :
Aucune reconnexion des systèmes compromis
n'est autorisée avant validation de sécurité.

Prochaine mise à jour :
Selon la cadence fixée par la cellule de crise.

Responsable de communication :
Rôle désigné dans le dispositif de crise.
```

Les heures de cet exemple sont fictives.

### 22.3 Eviter les annonces non vérifiées

Ne pas annoncer un RTO respecté avant la validation du service.

Ne pas déclarer un incident résolu parce qu'une VM a démarré.

Ne pas annoncer une restauration complète si les données métier n'ont pas été vérifiées.

Les messages doivent correspondre aux preuves disponibles.

## 23. Runbook de reprise après sinistre

### 23.1 Définition

Un runbook décrit une suite d'actions concrètes permettant de gérer une opération récurrente.

Un runbook PRA doit être assez précis pour être utilisé par une équipe qui n'a pas participé à sa rédaction.

### 23.2 Structure d'un runbook

```text
ID DU RUNBOOK
Nom du service :
Version :
Propriétaire :
Dernière validation :

OBJECTIF
Conditions de déclenchement :
Prérequis :
Contacts :
Accès de secours :
Dépendances :
Points de restauration attendus :

ETAPES
1. Préparer l'environnement
2. Vérifier les sauvegardes
3. Restaurer les données
4. Démarrer les services
5. Contrôler les dépendances
6. Exécuter les tests
7. Obtenir la validation
8. Communiquer le résultat

CRITERES D'ARRET
Risques :
Plan de retour arrière :
Nettoyage :
Preuves à conserver :
```

### 23.3 Les commandes doivent être vérifiées

Les runbooks peuvent contenir des commandes de restauration, mais elles doivent être adaptées à l'outil et aux chemins réels.

Éviter de copier une commande destructive sans vérifier :

- Le nom du serveur.
- La destination.
- Le point de restauration.
- Les permissions.
- Les dépendances.
- Les conséquences sur les données actuelles.

Une procédure de reprise doit être testée avec les versions réelles du logiciel.

## 24. Mesurer précisément les résultats

### 24.1 Chronologie de reprise

Pendant un exercice, enregistrer les étapes importantes.

Exemple :

| Événement | Heure fictive | Heure cumulée |
|---|---|---:|
| Déclaration du sinistre | 09:00 | 0 min |
| Accès au dépôt | 09:20 | 20 min |
| Début de restauration | 09:30 | 30 min |
| Fin de restauration des données | 10:20 | 80 min |
| Démarrage du système | 10:40 | 100 min |
| Tests techniques terminés | 11:00 | 120 min |
| Validation métier | 11:15 | 135 min |

Si le RTO est mesuré jusqu'à la validation métier, le résultat est de 2 h 15.

### 24.2 Mesurer la perte de données

Pour calculer le RPO réellement obtenu, il faut connaître le dernier point de données récupérable et le moment de l'interruption.

Exemple :

```text
Dernier état récupérable :
10 h 00

Interruption :
10 h 18

Perte de données potentielle :
18 minutes
```

Le résultat est inférieur à une cible de trente minutes dans cet exemple.

Il faut toutefois considérer la cohérence des données et l'heure réelle du dernier état validé. Un fichier portant un horodatage récent ne prouve pas à lui seul que la transaction est cohérente.

### 24.3 Définir des critères objectifs

Les critères ne doivent pas être formulés de manière vague.

Formulation peu vérifiable :

```text
L'application fonctionne.
```

Formulation plus précise :

```text
- Le service HTTP répond.
- L'authentification fonctionne.
- Une requête de lecture renvoie le résultat attendu.
- Une transaction de test peut être créée.
- Les données de référence sont présentes.
- Les journaux ne présentent pas d'erreur bloquante.
- Le responsable métier confirme le test.
```

Les tests doivent être adaptés à la fonction réelle du service.

## 25. Test de restauration automatisé : exemple de vérification de fichiers

Le script suivant illustre une vérification simple d'un jeu de fichiers après restauration.

Il ne remplace pas un outil de sauvegarde, ni un test de base de données ou d'application.

### 25.1 Préparer les données de référence

Dans un laboratoire Linux, créer un dossier :

```bash
mkdir -p ~/pra-lab/source
mkdir -p ~/pra-lab/restore
```

Créer des fichiers :

```bash
printf 'Commande de test\n' > ~/pra-lab/source/commande.txt
printf 'Client de démonstration\n' > ~/pra-lab/source/client.txt
```

Créer des sommes de contrôle :

```bash
cd ~/pra-lab/source
sha256sum commande.txt client.txt > SHA256SUMS.txt
```

### 25.2 Sauvegarder le jeu de données

```bash
tar -czf ~/pra-lab/sauvegarde.tar.gz \
  -C ~/pra-lab source
```

### 25.3 Restaurer dans une destination de test

```bash
tar -xzf ~/pra-lab/sauvegarde.tar.gz \
  -C ~/pra-lab/restore
```

La restauration doit produire les fichiers dans `~/pra-lab/restore/source`.

### 25.4 Vérifier les sommes de contrôle

```bash
cd ~/pra-lab/restore/source
sha256sum -c SHA256SUMS.txt
```

Si les fichiers correspondent aux sommes enregistrées, les vérifications concernées passent.

Ce test ne garantit pas la sécurité du dépôt si les fichiers de référence ont pu être modifiés en même temps que les données. Il ne vérifie pas non plus le fonctionnement applicatif.

### 25.5 Étendre le test

Pour une procédure plus complète, ajouter :

- Une comparaison des chemins attendus.
- Un contrôle des permissions.
- Un contrôle du nombre de fichiers.
- Une vérification de l'espace disponible.
- Un journal du résultat.
- Une mesure de la durée.
- Une alerte en cas d'échec.

Le script ou l'outil de test doit éviter de supprimer les fichiers restaurés avant que le résultat ait été collecté.

## 26. Stratégie de test pour Proxmox Backup Server

### 26.1 Vérification et restauration sont complémentaires

Proxmox Backup Server propose des mécanismes de vérification des sauvegardes.

Une vérification réussie indique que les données ont passé les contrôles prévus par le mécanisme de vérification.

La restauration d'une VM dans un environnement isolé vérifie un autre ensemble de propriétés : récupération, démarrage, dépendances et fonctions applicatives.

Documentation officielle :

https://pbs.proxmox.com/docs/maintenance.html

### 26.2 Exemple de cycle de test

```text
Datastore PBS
    |
    v
Sélection d'un snapshot
    |
    v
Vérification d'intégrité
    |
    v
Restauration d'une VM de test
    |
    v
Démarrage en réseau isolé
    |
    v
Tests système
    |
    v
Tests applicatifs
    |
    v
Rapport et nettoyage contrôlé
```

### 26.3 Points à examiner

- L'intégrité du snapshot.
- La configuration de la VM.
- Le nombre de disques.
- L'espace cible.
- Les permissions.
- Les paramètres de chiffrement.
- Les clés nécessaires.
- La compatibilité de l'environnement de reprise.
- La connectivité.
- Le délai.
- La validation applicative.

Si le chiffrement côté client est utilisé, la récupération doit également disposer des clés nécessaires. La perte des clés peut rendre des données techniquement présentes mais inutilisables.

## 27. Stratégie de test pour Veeam

### 27.1 Vérification automatisée de récupérabilité

Veeam documente des mécanismes permettant de tester la récupérabilité de machines virtuelles à partir de sauvegardes ou de réplicas dans les environnements pris en charge.

SureBackup permet notamment d'exécuter des machines dans un environnement isolé et de réaliser des tests de récupération, selon la configuration et les capacités disponibles.

Documentation officielle :

https://helpcenter.veeam.com/docs/vbr/userguide/recovery_verification_overview.html

### 27.2 Ce qu'un test automatisé peut contrôler

Selon les capacités et la configuration :

- Le démarrage d'une VM restaurée.
- La présence d'un service.
- La connectivité.
- Certains contrôles applicatifs.
- Des tests d'intégrité.
- Les résultats de vérification.
- Les rapports d'exécution.

### 27.3 Ce qui doit rester validé par les équipes

Même si le démarrage d'une VM et les tests automatisés réussissent, il peut encore être nécessaire de vérifier :

- La cohérence de la base.
- Les fonctions métier.
- Les autorisations.
- Le traitement des transactions.
- Les flux inter-applications.
- La conformité de l'environnement restauré.

Un test automatisé doit donc être complété selon la criticité du service.

## 28. Test de restauration d'une base de données avec critères métier

Une base restaurée peut s'ouvrir tout en contenant des données incorrectes ou incomplètes.

Le test doit combiner des contrôles techniques et des contrôles métier.

### 28.1 Exemple de fiche de validation

```text
BASE :
VERSION :
POINT DE RESTAURATION :
HEURE DE LA SAUVEGARDE :

CONTROLES TECHNIQUES
- La base s'ouvre.
- Le moteur ne signale pas d'erreur bloquante.
- Les objets attendus existent.
- Les rôles et permissions nécessaires sont présents.

CONTROLES DES DONNEES
- Les tables de référence existent.
- Les enregistrements attendus sont présents.
- Les relations principales sont cohérentes.
- Les données récupérées correspondent au point de restauration.

CONTROLES APPLICATIFS
- L'application se connecte.
- Une requête métier de lecture réussit.
- Une transaction de test réussit si cela est prévu.
- Les résultats sont validés par le responsable applicatif.

MESURES
- Début de restauration :
- Fin de restauration :
- Début des tests :
- Fin des tests :
- Perte de données estimée :
- Conclusion :
```

### 28.2 Éviter les effets métier involontaires

Les tests doivent être réalisés dans une base de test ou un environnement isolé.

Une application restaurée peut envoyer des notifications, appeler un fournisseur de paiement, publier des messages ou lancer des tâches planifiées.

Ces comportements doivent être désactivés ou contrôlés dans le cadre du test afin d'éviter des opérations réelles non désirées.

## 29. Le retour au site principal : failback

### 29.1 Pourquoi le retour est-il une opération à part entière ?

Après un sinistre, une organisation peut faire fonctionner ses services dans un environnement de reprise.

Le retour au site principal est appelé *failback* dans de nombreux contextes techniques.

Cette opération n'est pas simplement un redémarrage de l'ancien serveur. Les données ont pu évoluer pendant que le système fonctionnait sur le site secondaire.

Il faut organiser la synchronisation finale, les décisions de bascule et les validations.

### 29.2 Cycle de failback

```text
SITE PRINCIPAL INDISPONIBLE
             |
             v
REPRISE SUR SITE SECONDAIRE
             |
             v
SERVICE OPERATIONNEL
             |
             v
REPARATION DU SITE PRINCIPAL
             |
             v
VALIDATION DE L'INFRASTRUCTURE
             |
             v
SYNCHRONISATION DES DONNEES
             |
             v
PREPARATION DE LA BASCULE
             |
             v
BASCULE CONTROLEE VERS LE PRINCIPAL
             |
             v
TESTS TECHNIQUES ET METIER
             |
             v
RETOUR CONFIRME
```

Le détail des étapes dépend du mécanisme employé, des bases de données, de la réplication et de l'architecture de l'application.

### 29.3 Les risques de split-brain

Le *split-brain* survient lorsque deux environnements agissent simultanément comme s'ils étaient tous deux la référence pour les mêmes données ou services.

Cela peut provoquer des conflits d'écriture et des incohérences.

La procédure doit définir quel environnement est autorisé à accepter les écritures, à quel moment et selon quel mécanisme.

### 29.4 Critères de retour au site principal

Avant un failback, vérifier :

- L'intégrité de l'environnement principal.
- Les correctifs nécessaires.
- Les règles réseau.
- Les dépendances.
- L'état du stockage.
- La synchronisation des données.
- La capacité.
- La disponibilité du plan de contrôle.
- Les procédures de retour arrière.
- L'approbation des responsables.

Un retour ne doit pas être décidé uniquement parce que le site principal répond de nouveau au ping.

## 30. Gérer la capacité pendant une reprise

### 30.1 Le site de secours doit être dimensionné

Un site de reprise qui dispose de quelques serveurs ne pourra peut-être pas héberger toutes les charges du site principal.

Il faut définir les ressources nécessaires pour les services prioritaires :

- CPU.
- Mémoire.
- Stockage.
- Débit réseau.
- Capacité des bases.
- Licences.
- Adresses IP.
- Accès réseau.
- Capacité des composants de sécurité.

### 30.2 Exemple de capacité dégradée

```text
Capacité nominale du site principal
                |
                v
     Inventaire des services
                |
                v
     Classement par criticité
                |
                v
      Capacité disponible en secours
                |
      +---------+----------+
      |                    |
      v                    v
Services prioritaires   Services différés
      |                    |
      v                    v
Restauration rapide     Reprise ultérieure
```

Il peut être nécessaire de restaurer d'abord les services critiques et de différer certains systèmes secondaires.

Les décisions doivent respecter la BIA et les engagements de service.

### 30.3 Mesurer la performance de récupération

Les restaurations peuvent solliciter intensément le réseau, le stockage et les processeurs.

Un scénario de sinistre doit vérifier que le site de reprise peut restaurer plusieurs systèmes en même temps.

Il faut notamment mesurer :

- Le débit de transfert.
- Le temps de lecture des dépôts.
- Les temps de création des VM.
- Les performances des bases.
- La disponibilité du réseau.
- Les conflits de ressources.
- Les temps de validation.

## 31. Gouvernance des tests PRA

### 31.1 Qui décide qu'un test est réussi ?

Les critères de réussite doivent être définis avant le test.

La réussite peut exiger plusieurs validations :

- Équipe sauvegarde : données récupérées.
- Équipe système : OS et services démarrés.
- Équipe sécurité : environnement acceptable.
- Équipe applicative : fonctions correctes.
- Responsable métier : activité utilisable.
- Direction ou responsable désigné : autorisation de clôture du sinistre simulé.

Un test ne doit pas être déclaré réussi uniquement par la personne qui a exécuté la commande de restauration.

### 31.2 Gérer les écarts

Un test peut réussir techniquement tout en échouant à respecter le RTO.

Il faut alors :

1. Enregistrer le résultat.
2. Identifier la cause de l'écart.
3. Évaluer son impact.
4. Définir les actions correctives.
5. Attribuer un responsable.
6. Fixer une échéance.
7. Retester après correction.

Les écarts non corrigés doivent être visibles dans le registre des risques et dans le reporting adapté.

### 31.3 Cycle d'amélioration continue

```text
PLANIFIER
    |
    v
PREPARER LE TEST
    |
    v
EXECUTER
    |
    v
MESURER
    |
    v
ANALYSER LES ECARTS
    |
    v
CORRIGER
    |
    v
RETTESTER
    |
    v
METTRE A JOUR LE PRA
```

Le test n'est pas une simple formalité. Il doit améliorer la capacité de récupération.

## 32. Modèle de rapport de test de restauration

Le rapport suivant peut être adapté aux différents types de tests.

```text
RAPPORT DE TEST DE RESTAURATION

1. INFORMATIONS GENERALES

ID du test :
Nom du service :
Date :
Responsable :
Participants :
Version de la procédure :
Environnement :

2. OBJECTIF

Objectif du test :
Scénario :
Criticité :
RPO cible :
RTO cible :

3. PERIMETRE

Systèmes concernés :
Données concernées :
Point de restauration :
Dépôt utilisé :
Dépendances :

4. PREPARATION

Accès validés :
Capacité disponible :
Réseau de test :
Risques identifiés :
Plan de retour arrière :

5. EXECUTION

Heure de début :
Heure d'accès aux sauvegardes :
Heure de début de restauration :
Heure de fin de restauration :
Heure de démarrage :
Heure de fin des tests techniques :
Heure de validation métier :

6. RESULTATS

Intégrité :
Données présentes :
Système démarré :
Application fonctionnelle :
Tests métier réussis :
Durée totale :
RPO mesuré :
RTO mesuré :

7. ECARTS

Ecart observé :
Impact :
Cause connue ou hypothèse :
Action corrective :
Responsable :
Echéance :

8. CONCLUSION

Résultat :
Objectif respecté :
Risque résiduel :
Autorisation de clôture :
Date de prochaine vérification :
```

Les valeurs doivent être mesurées et les hypothèses clairement identifiées. Le rapport ne doit pas présenter une estimation comme une mesure réelle.

## 33. Exemple de rapport rempli

Les valeurs ci-dessous sont fictives.

```text
ID du test : PRA-RESTORE-DB-003
Service : Base de données métier
Date : 2026-10-24

Objectif :
  Restaurer une sauvegarde dans un environnement isolé.

RPO cible :
  30 minutes

RTO cible :
  2 heures

Résultats :
  Début du test : 09:00
  Accès au dépôt : 09:12
  Début de restauration : 09:20
  Fin de restauration : 10:05
  Tests techniques terminés : 10:25
  Validation métier : 10:40

RTO mesuré :
  1 heure et 40 minutes

RPO mesuré :
  18 minutes de données perdues dans le scénario testé

Conclusion :
  Les objectifs sont respectés dans ce test isolé.

Limites :
  Le test n'inclut pas le basculement réseau du site secondaire.
  Le test ne valide pas une perte complète du site principal.

Action :
  Préparer un exercice de reprise intersite.
```

Ce résultat ne prouve pas que toutes les situations de sinistre respecteront le même RTO. Il s'applique au scénario, au périmètre et aux conditions testés.

## 34. Construire un programme annuel de tests

### 34.1 Exemple de calendrier

| Période | Test | Objectif |
|---|---|---|
| Janvier | Revue documentaire du PRA | Contrôler les contacts et procédures |
| Février | Restauration de fichiers | Vérifier une récupération ciblée |
| Mars | Restauration de VM isolée | Vérifier démarrage et configuration |
| Avril | Restauration de base de données | Contrôler cohérence et données |
| Mai | Exercice sur table | Vérifier décisions et responsabilités |
| Juin | Test de copie distante | Contrôler l'accès à une copie indépendante |
| Juillet | Test de reprise applicative | Vérifier les dépendances métier |
| Août | Revue des comptes de secours | Vérifier les accès d'urgence |
| Septembre | Exercice cyber isolé | Tester le processus de récupération propre |
| Octobre | Test de restauration de VM prioritaire | Mesurer RTO et qualité des contrôles |
| Novembre | Exercice de reprise de site | Tester l'organisation du PRA |
| Décembre | Bilan et mise à jour | Corriger les écarts et planifier l'année suivante |

Cette programmation est un exemple de gouvernance. Les fréquences réelles dépendent des risques, des ressources et des obligations de l'organisation.

### 34.2 Prioriser les tests

Le programme doit être adapté aux changements :

- Nouvelle application.
- Nouveau dépôt.
- Migration de stockage.
- Mise à niveau du logiciel de sauvegarde.
- Changement de fournisseur.
- Nouvelle politique de rétention.
- Modification du système d'identité.
- Changement de site.
- Modification des responsabilités.
- Incident majeur.

Une modification importante peut justifier un test ciblé sans attendre le prochain exercice annuel.

## 35. Scénario de crise complet : perte du site principal

### 35.1 Situation initiale

Une entreprise héberge plusieurs services sur son site principal.

Un sinistre rend le site indisponible. Les applications, les hyperviseurs et une partie du réseau ne peuvent plus être utilisés.

Le site secondaire possède des ressources de reprise et une copie de sauvegarde.

### 35.2 Mission

L'équipe doit :

1. Confirmer l'impact.
2. Déclarer le sinistre selon le processus.
3. Activer la cellule de crise.
4. Vérifier la disponibilité du site secondaire.
5. Confirmer la disponibilité des sauvegardes.
6. Récupérer les services fondamentaux.
7. Restaurer les données prioritaires.
8. Restaurer les applications dans l'ordre.
9. Exécuter les tests techniques.
10. Obtenir les validations métier.
11. Communiquer les services rétablis.
12. Mesurer le RPO et le RTO.
13. Documenter les écarts.
14. Préparer le retour à l'infrastructure normale.

### 35.3 Critères de succès

- Les responsables sont identifiés.
- La déclaration est réalisée selon la procédure.
- Les copies de sauvegarde sont accessibles.
- Les services critiques sont restaurés.
- Les données respectent les critères de cohérence.
- Les accès sont contrôlés.
- Les utilisateurs peuvent exécuter les opérations prioritaires.
- Les objectifs sont mesurés.
- Le retour au site normal dispose d'une procédure.
- Les risques résiduels sont documentés.

### 35.4 Critères d'arrêt

Un exercice doit prévoir des conditions d'arrêt.

Exemples :

- Risque d'impact sur la production.
- Conflit de données entre deux environnements.
- Perte de contrôle du réseau de test.
- Données sensibles exposées.
- Sauvegarde potentiellement compromise.
- Risque d'effacer un point de restauration nécessaire.
- Dépendance à un système réel qui ne doit pas être touché.

L'équipe doit interrompre le test si la sécurité ou l'intégrité de la production est menacée.

## 36. Défi expert : reprise après rançongiciel

### 36.1 Scénario

Plusieurs serveurs présentent des fichiers chiffrés et les comptes administrateurs semblent compromis.

Certaines sauvegardes sont encore disponibles sur un site distant. La date de début de l'attaque n'est pas connue avec certitude.

Le serveur de gestion de sauvegarde n'est pas considéré comme fiable tant que son intégrité n'a pas été vérifiée.

### 36.2 Mission

Construire une stratégie de reprise qui répond aux questions suivantes :

1. Qui décide d'activer le processus de crise ?
2. Comment l'attaque est-elle contenue ?
3. Quelles preuves doivent être préservées ?
4. Comment contrôler les identités et accès de sauvegarde ?
5. Comment déterminer les points de restauration candidats ?
6. Comment évaluer la présence de traces de compromission dans ces points ?
7. Où construire l'environnement de récupération ?
8. Comment protéger le dépôt pendant les opérations ?
9. Dans quel ordre restaurer les services ?
10. Comment révoquer les secrets compromis ?
11. Comment valider les systèmes avant reconnexion ?
12. Comment communiquer les résultats ?
13. Quel mécanisme permet de revenir à la normale ?
14. Quelles mesures réduisent le risque de répétition ?

### 36.3 Résultat attendu

Fournir un dossier comportant :

- Le schéma de l'environnement de récupération.
- La chronologie de crise.
- Les responsabilités.
- Les hypothèses.
- Les critères de sélection des sauvegardes.
- Les validations de sécurité.
- Les procédures de restauration.
- Les tests applicatifs.
- Les objectifs RPO/RTO.
- Le plan de communication.
- Les actions d'amélioration.

Le défi doit démontrer que la récupération ne se limite pas au redémarrage des machines. Il faut restaurer un environnement opérationnel et suffisamment fiable pour être réintroduit dans le système d'information.

## 37. Erreurs fréquentes à éviter

### Erreur 1 : confondre vérification et restauration

Un dépôt peut passer un contrôle d'intégrité sans que l'application ait été testée.

**Correction :** séparer clairement les tests d'intégrité, de récupération système et de validation applicative.

### Erreur 2 : tester uniquement les fichiers

La récupération de fichiers ne valide pas l'ensemble d'un service.

**Correction :** tester les systèmes, les bases, les dépendances et les fonctions métier selon la criticité.

### Erreur 3 : restaurer dans le réseau de production

Une VM de test peut entrer en conflit avec une machine active ou transmettre des données indésirables.

**Correction :** utiliser un environnement isolé et contrôler les communications.

### Erreur 4 : prendre la sauvegarde la plus récente sans vérifier la chronologie cyber

Une sauvegarde récente peut contenir une compromission déjà présente.

**Correction :** analyser la période de l'incident et sélectionner un point de restauration justifié par les preuves.

### Erreur 5 : ne pas tester les comptes de secours

Les secrets peuvent être perdus ou les accès peuvent dépendre d'un système indisponible.

**Correction :** tester périodiquement les mécanismes d'accès d'urgence selon une procédure sécurisée.

### Erreur 6 : mesurer uniquement le transfert des données

Le démarrage du système, la récupération des dépendances et les tests métier prennent aussi du temps.

**Correction :** mesurer la durée complète jusqu'à la validation définie du service.

### Erreur 7 : ne pas documenter les écarts

Un test échoue, puis la même procédure est réutilisée sans correction.

**Correction :** attribuer chaque action à un responsable et retester après correction.

### Erreur 8 : remettre trop tôt le service en production

Une VM démarre, mais l'application n'est pas validée.

**Correction :** définir des critères de reprise et obtenir la validation des responsables prévus.

### Erreur 9 : oublier le failback

Les services fonctionnent sur le site secondaire mais le retour vers le site principal n'est pas préparé.

**Correction :** prévoir la synchronisation, les décisions de bascule, les contrôles de cohérence et les conditions de retour.

### Erreur 10 : ne pas tester le plan de crise

Les contacts et procédures semblent corrects sur papier mais n'ont jamais été utilisés.

**Correction :** réaliser régulièrement des exercices documentés et améliorer les procédures.

## 38. Bonnes pratiques à retenir

### Stratégie

- Réaliser une analyse d'impact métier.
- Classer les services par criticité.
- Définir RPO et RTO.
- Cartographier les dépendances.
- Prévoir plusieurs scénarios de sinistre.
- Construire des objectifs de reprise mesurables.

### Tests

- Définir les critères avant l'exercice.
- Tester les fichiers, systèmes et applications.
- Restaurer dans un environnement isolé lorsque nécessaire.
- Tester la disponibilité des secrets et des comptes de secours.
- Mesurer le temps total de reprise.
- Vérifier la cohérence métier.
- Conserver les preuves.
- Retester après correction des écarts.

### Sécurité

- Vérifier les sauvegardes candidates après un incident cyber.
- Utiliser un environnement de récupération propre.
- Séparer les identités de production et de sauvegarde.
- Protéger les copies immuables.
- Contrôler les accès aux dépôts.
- Préserver les preuves nécessaires.
- Révoquer les secrets compromis avant la remise en service.

### Exploitation

- Maintenir des runbooks opérationnels.
- Garder les procédures disponibles en situation de panne.
- Définir les responsabilités.
- Préparer les communications.
- Documenter la chronologie.
- Gérer les critères d'arrêt.
- Mesurer les écarts entre objectifs et résultats.
- Mettre à jour les plans après chaque changement significatif.

### Gouvernance

- Programmer les tests.
- Attribuer un responsable à chaque service.
- Réviser les contacts.
- Suivre les actions correctives.
- Faire approuver les risques résiduels.
- Mesurer la progression de la préparation à la reprise.
- Vérifier la réversibilité des solutions et des prestataires.

## 39. Référence opérationnelle rapide

| Besoin | Mécanisme ou livrable |
|---|---|
| Définir les priorités de reprise | BIA |
| Définir les pertes et durées acceptables | RPO / RTO |
| Vérifier l'intégrité des données | Vérification de dépôt |
| Vérifier la récupération de fichiers | Test ciblé |
| Vérifier le démarrage d'une VM | Restauration isolée |
| Vérifier la récupération applicative | Tests techniques et métier |
| Tester un scénario sans toucher à la production | Exercice sur table |
| Préparer une reprise cyber | Environnement de récupération propre |
| Vérifier les machines virtuelles avec Veeam | SureBackup selon les capacités disponibles |
| Vérifier un datastore PBS | Tâches de vérification et tests de restauration |
| Organiser les étapes d'un sinistre | Runbook PRA |
| Mesurer le résultat d'un test | Chronologie de reprise |
| Documenter les écarts | Rapport de test et actions correctives |
| Gérer le retour vers le site principal | Plan de failback |
| Vérifier l'efficacité du plan | Programme régulier d'exercices |

## 40. Glossaire

**BIA — Business Impact Analysis :** analyse des conséquences d'une interruption et des priorités métier.

**Basculement :** transfert du service vers un autre environnement.

**Failback :** retour contrôlé à l'environnement principal après une période de fonctionnement sur un site ou environnement de reprise.

**Failover :** basculement d'un service vers un environnement alternatif.

**PCA — Plan de continuité d'activité :** organisation du maintien des activités essentielles pendant une perturbation.

**PRA — Plan de reprise d'activité :** procédures visant à restaurer les systèmes et services après un incident majeur.

**Restauration :** récupération de données à partir d'une sauvegarde.

**RPO — Recovery Point Objective :** perte maximale de données acceptable, exprimée en temps.

**RTO — Recovery Time Objective :** délai cible de rétablissement du service.

**MTTR :** mesure moyenne de temps de réparation ou de rétablissement, selon la définition retenue.

**Test de restauration :** opération vérifiant la capacité à récupérer des données ou des systèmes.

**Test applicatif :** ensemble de contrôles permettant de valider le fonctionnement d'une application récupérée.

**Exercice sur table :** simulation guidée d'un scénario dans laquelle les participants décrivent les décisions et actions attendues.

**Environnement de récupération propre :** environnement contrôlé destiné à restaurer et valider des systèmes sans dépendre d'une infrastructure potentiellement compromise.

**Runbook :** procédure opérationnelle structurée décrivant les actions à exécuter.

**Point de restauration :** état de données ou de système disponible pour une récupération.

**Immuabilité :** mécanisme qui empêche la modification ou la suppression de données pendant une durée définie, selon les protections activées.

**Split-brain :** situation dans laquelle plusieurs environnements se comportent simultanément comme la référence pour des données ou services qui devraient avoir une autorité unique.

**RACI :** matrice qui définit les responsabilités : Responsible, Accountable, Consulted et Informed.

## 41. Documentation officielle

### Continuité, reprise et gestion des risques

- NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems : https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final
- Publication NIST et guide de planification : https://doi.org/10.6028/NIST.SP.800-34r1
- CISA — StopRansomware Guide : https://www.cisa.gov/stopransomware/ransomware-guide

Le guide NIST présente notamment les grandes étapes de préparation, d'analyse d'impact, de choix des stratégies de reprise, de documentation et d'exercice des plans. Il s'agit d'un guide de référence ancien mais toujours utile pour structurer un programme de continuité ; vérifier les autres exigences et références applicables à son organisation.

### Veeam

- SureBackup : https://helpcenter.veeam.com/docs/vbr/userguide/recovery_verification_surebackup_job.html
- Fonctionnement de SureBackup : https://helpcenter.veeam.com/docs/vbr/userguide/surebackup_hiw.html
- Vérification de récupération VMware : https://helpcenter.veeam.com/docs/vbr/userguide/recovery_verification_overview.html

### Proxmox Backup Server

- Documentation générale : https://pbs.proxmox.com/docs/
- Maintenance et vérification : https://pbs.proxmox.com/docs/maintenance.html
- Documentation officielle et guides de versions : https://www.proxmox.com/en/downloads/proxmox-backup-server/documentation

### Microsoft

- Référence `wbadmin` : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin
- Sauvegarde de l'état système : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-systemstatebackup
- Restauration Windows Server : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-recovery

Les fonctionnalités de vérification, les possibilités de restauration automatisée et les prérequis varient selon les solutions, les versions et les licences. Il faut consulter la documentation correspondant à l'environnement réel.

## 42. Conclusion du niveau expert

La reprise après sinistre ne doit pas reposer sur une affirmation non démontrée selon laquelle « les sauvegardes existent ».

Elle doit reposer sur des preuves : points de restauration disponibles, données récupérées, systèmes démarrés, applications validées et objectifs mesurés.

Le PRA définit comment rétablir les services. Le PCA organise le maintien des activités essentielles. Les tests permettent de vérifier que les procédures fonctionnent et que les équipes savent les exécuter dans les conditions prévues.

La qualité de la reprise dépend également de l'analyse d'impact, des dépendances, de la capacité disponible, de la sécurité des copies, de la protection des comptes et de la préparation des environnements de récupération.

Un test doit être plus qu'une opération réussie : il doit produire un résultat mesurable, révéler les écarts et entraîner des améliorations.

**Le niveau expert est atteint lorsque l'organisation peut démontrer, par des exercices reproductibles et des restaurations validées, qu'elle sait récupérer ses données, remettre en service ses applications et reprendre ses activités dans les limites qu'elle a définies.**