# Rédiger des procédures et checklists

> **Mise en contexte**
>
> Une intervention réussie par un technicien expérimenté échoue lorsqu'un collègue doit la répéter, car les étapes n'étaient connues que de la première personne. Une procédure partage la méthode, définit les limites d'autorisation et permet de vérifier le résultat. Elle ne doit pas être un simple texte à suivre aveuglément : elle doit aussi indiquer quand s'arrêter et comment revenir à un état sûr.

## Objectifs du cours

Tu apprendras à rédiger un runbook opérationnel, décrire les préconditions, structurer une checklist, ajouter les critères de réussite et de retour arrière, puis gérer la version et l'amélioration continue d'une procédure.

## 1. Procédure, checklist et runbook

Une **procédure** explique le but, le périmètre, les rôles, les règles et l'ordre des opérations. Une **checklist** rend visibles les vérifications qui ne doivent pas être oubliées. Un **runbook** associe généralement les étapes opérationnelles à des commandes ou des actions, à des résultats attendus et aux décisions en cas d'écart.

Ces documents sont complémentaires. Une checklist ne décrit pas forcément comment résoudre une erreur complexe ; un runbook ne remplace pas l'approbation ou l'analyse de risque requise avant une modification.

## 2. Le contenu minimal d'un document utilisable

Tout document opérationnel doit contenir :

- **But et périmètre :** service visé, environnement, version, exclusions et résultat attendu.
- **Responsabilités :** exécutant, valideur, contact métier, personne à joindre en cas d'incident.
- **Conditions préalables :** autorisation, accès, sauvegarde vérifiée, dépendances, fenêtre et matériel.
- **Risques :** impact possible, seuil d'arrêt et mesures de réduction.
- **Étapes :** ordre précis, action, résultat attendu et point de décision.
- **Validation :** contrôles après intervention, preuve attendue et critère de réussite.
- **Retour arrière :** condition de déclenchement, action et point de contrôle.
- **Traçabilité :** identifiant de changement ou de ticket, version du document, date et approbateur.

Le niveau de détail doit correspondre au public. Une procédure de rétablissement utilisée en astreinte doit être concise et sans ambiguïté ; un guide de conception peut expliquer davantage les choix. Chaque commande doit préciser l'hôte, les droits requis, l'effet prévu et la manière de vérifier le résultat.

## 3. Cycle de vie d'une procédure

~~~mermaid
flowchart TD
    A[Besoin ou incident récurrent] --> B[Définir portée et risques]
    B --> C[Rédiger les étapes et contrôles]
    C --> D[Relecture par un pair]
    D --> E[Test dans un environnement sûr]
    E --> F{Résultat conforme ?}
    F -->|Non| C
    F -->|Oui| G[Validation et publication]
    G --> H[Utilisation et retour terrain]
    H --> I[Revue périodique ou après incident]
    I --> C
~~~

Un document ne doit pas être publié uniquement parce qu'il est bien écrit. Un pair doit relire les étapes, puis un test doit démontrer que les instructions fonctionnent dans le périmètre annoncé. Les approbations attendues dépendent de la criticité du service et du processus de changement.

## 4. Écrire des étapes précises

Une étape utile comporte un verbe d'action, la cible, le résultat attendu et la décision si ce résultat n'est pas obtenu.

| Étape vague | Étape exploitable |
|---|---|
| Vérifier le serveur | Exécuter les contrôles de disponibilité définis sur l'hôte nommé dans le ticket et consigner l'heure et le résultat |
| Faire la sauvegarde | Identifier le point de restauration retenu, vérifier son statut, noter sa référence et vérifier que la restauration est possible selon la procédure |
| Redémarrer si besoin | Ne redémarrer que si la condition prévue est confirmée et l'autorisation obtenue ; en cas de dépendance non vérifiée, arrêter et escalader |
| Tout est bon | Exécuter les tests fonctionnels listés, comparer aux résultats attendus et joindre les preuves au ticket |

Évite les mots « normal », « rapidement », « éventuellement » ou « comme d'habitude » sans critère défini. Une instruction doit être compréhensible par un technicien qui n'a pas participé à sa rédaction.

## 5. Prévoir l'arrêt et le retour arrière

Le retour arrière doit être préparé avant l'action risquée. Il faut définir ce qui déclenche l'arrêt : perte d'un lien redondant, test métier échoué, dépassement de durée, absence de sauvegarde, erreur inattendue ou perte de supervision.

Le plan de retour arrière identifie les étapes de restauration, la personne autorisée, le temps estimé et les vérifications de rétablissement. Il doit être réaliste : si le retour arrière est impossible ou plus risqué que le changement, la décision doit être prise par les responsables concernés avant l'intervention.

Les commandes qui écrivent, suppriment ou modifient les configurations ne doivent pas apparaître sans contexte. Fournis une variante en lecture seule lorsque c'est possible, un environnement de test et une confirmation explicite avant toute action à effet de bord.

## 6. Exemple de fiche de procédure

### Contrôle initial d'un serveur Linux

**But :** collecter les faits avant de lancer une action corrective.

**Préconditions :** accès autorisé, identifiant de ticket disponible, serveur exact confirmé, périmètre de production ou de laboratoire documenté.

**Étapes :**

1. Consigner l'heure et le nom de l'hôte avec date -Is et hostnamectl.
2. Relever la charge et la durée de fonctionnement avec uptime.
3. Vérifier l'espace disponible avec df -h.
4. Consulter les unités en échec avec systemctl --failed.
5. Lire les avertissements récents avec journalctl -p warning --since "1 hour ago".
6. Comparer les résultats à la référence connue et aux seuils définis.
7. Joindre les sorties pertinentes au ticket en retirant les secrets ou données personnelles non nécessaires.

**Critère de réussite :** les mesures sont horodatées, attribuées au bon hôte et disponibles dans le dossier de l'intervention.

**Limite :** cette fiche ne répare pas un service. Si les résultats montrent une panne, ouvrir la procédure de diagnostic correspondante ou escalader. N'exécute pas un redémarrage ou une modification à partir de cette seule collecte.

## 7. Versionner et maintenir la documentation

Chaque document doit avoir une version, une date d'entrée en vigueur, un propriétaire et une prochaine date de revue. Une modification doit expliquer ce qui change et pourquoi. Les procédures périmées doivent être retirées du chemin opérationnel mais conservées selon les règles d'historique.

Déclenche une revue après une panne significative, un changement d'architecture, une évolution logicielle, une modification de politique ou un retour terrain répété. Mesure aussi la qualité : étapes échouées, appels à l'aide, écarts entre la procédure et la réalité et temps de réalisation. Une checklist fréquemment contournée est souvent un signal d'inadéquation à corriger.

## Mise en pratique

### Laboratoire : rédiger et tester une checklist de maintenance

Choisis un service de laboratoire, par exemple un site web local ou un service non critique. Rédige une procédure contenant but, périmètre, rôles, préconditions, risques, étapes numérotées, résultats attendus, critères d'arrêt, retour arrière, test final et traçabilité.

Fais relire le document par une autre personne, puis réalise uniquement les contrôles en lecture seule prévus. Note les différences entre la procédure et le résultat réel. Corrige le document, change sa version et conserve la trace du test. Ne teste pas une commande de modification sur la production.

**Critères d'acceptation :** une personne tierce peut identifier la bonne cible, comprendre chaque action, savoir ce qui doit être observé et reconnaître le moment où elle doit arrêter ou appeler un responsable.

## Exercices corrigés

**1. Une procédure dit « redémarrer si le serveur semble bloqué ». Quel est le défaut ?**

Correction : « semble bloqué » ne définit pas un critère observable, ne précise pas l'impact ni l'autorisation et ne décrit pas le retour arrière. Il faut des symptômes vérifiables, des préconditions et un test de validation.

**2. Pourquoi tester le document dans un environnement sûr ?**

Correction : pour déceler les étapes ambiguës, les dépendances oubliées et les résultats impossibles à atteindre avant que l'exécution affecte un vrai service.

**3. À quel moment faut-il déclencher un retour arrière ?**

Correction : lorsque les conditions d'arrêt prévues sont atteintes, par exemple un test fonctionnel échoué ou un impact dépassant le seuil accepté. La procédure doit définir l'autorité et les étapes avant le début du changement.

**4. Une procédure ancienne fonctionne encore. Peut-on la laisser sans date de revue ?**

Correction : non. L'environnement et les dépendances évoluent. Le propriétaire, la version et la revue permettent de savoir si elle reste valide.

## Défi final corrigé

Un technicien veut publier une procédure de mise à jour d'un service. Le document contient des commandes, mais pas de sauvegarde vérifiée, de fenêtre, de test fonctionnel ni de retour arrière. Quelle est la décision correcte ?

**Correction attendue :** ne pas publier la procédure pour exécution. Définir le périmètre et les responsables, valider les préconditions, intégrer les preuves de sauvegarde nécessaires, préciser la fenêtre, tester les étapes dans un environnement sûr, définir des critères d'arrêt et un plan de retour arrière, établir les tests avant/après, puis faire relire et approuver le document. Une fois utilisé, recueillir les écarts et planifier sa revue.


## 8. Concevoir une procédure comme un contrat opérationnel

Une procédure indique quand l'action commence, qui est autorisé à l'exécuter, les conditions à réunir, la séquence, les résultats attendus, les contrôles, les exceptions et la preuve de clôture. Elle permet de reproduire une tâche sans dépendre uniquement de la mémoire d'un technicien expérimenté.

Un document exploitable précise le but, le périmètre, les rôles, les compétences requises, les accès, les outils, les prérequis, les étapes potentiellement irréversibles, le résultat attendu, le point d'arrêt, le plan de retour, les communications et l'emplacement de la preuve. Il indique aussi ce qu'il ne couvre pas. Une procédure de redémarrage simple ne doit pas être utilisée pour un cluster qui exige un ordre précis si cette configuration n'est pas incluse.

~~~mermaid
flowchart TD
    A[Besoin ou risque] --> B[Définir périmètre et acteurs]
    B --> C[Écrire prérequis et séquence]
    C --> D[Définir tests et exceptions]
    D --> E[Essai en environnement adapté]
    E --> F{Sûre et compréhensible ?}
    F -->|Non| C
    F -->|Oui| G[Approbation et publication]
    G --> H[Revue après retour terrain]
~~~

Le niveau de détail dépend du risque. Une tâche simple et réversible peut être courte ; une intervention de production, une mise à jour de firmware ou une restauration exige des contrôles et décisions explicites. Teste la procédure avec une personne qui n'a pas participé à la rédaction : les questions qu'elle pose révèlent les ambiguïtés. Une suite d'étapes qui n'est comprise que par son auteur n'est pas une procédure réutilisable.

## 9. Rédiger des étapes vérifiables

Privilégie les verbes d'action : identifier, sauvegarder, comparer, vérifier, enregistrer, valider. « Faire le nécessaire pour la sécurité » n'est pas vérifiable ; « confirmer que le compte utilisé possède uniquement les droits requis » est plus précis. Chaque étape critique doit préciser une action, un résultat attendu, un statut et la conduite à tenir en cas d'écart.

Une checklist peut contenir numéro et action, rôle responsable, prérequis, résultat attendu, résultat observé, preuve ou lien vers le ticket, statut « réussi », « échoué », « non réalisé » ou « bloqué », et décision attendue si le contrôle échoue.

~~~mermaid
flowchart LR
    A[Préconditions] --> B[Action précise]
    B --> C[Résultat attendu]
    C --> D{Conforme ?}
    D -->|Oui| E[Étape suivante]
    D -->|Non| F[Arrêt ou escalade]
    E --> G[Contrôle final]
    G --> H[Preuve et clôture]
~~~

Évite les valeurs qui nécessitent de deviner. Une procédure peut renvoyer à un catalogue de versions approuvées, une règle de rétention ou un numéro de changement, mais la référence doit être stable et accessible. Si un paramètre est variable, explique comment le récupérer et qui en valide la valeur. Les captures d'écran illustrent, mais ne remplacent pas le résultat ni la date de contrôle.

## 10. Versions, approbations et source de vérité

Une procédure doit identifier sa version, son propriétaire, son approbateur, sa date d'entrée en vigueur et sa prochaine revue. Une revue peut être déclenchée par le temps, mais aussi par un incident, une mise à jour de l'outil, un changement d'architecture, une vulnérabilité ou un écart constaté.

Conserve la trace des modifications : ce qui change, pourquoi, qui a demandé, qui a testé, qui a approuvé et depuis quand la nouvelle version s'applique. Lorsqu'une procédure est retirée, marque clairement l'ancienne comme obsolète et dirige vers la nouvelle. Des PDF envoyés par courriel peuvent continuer à circuler longtemps ; indique la source de vérité et remplace les liens directs vers les copies non contrôlées.

Les droits de lecture et d'édition doivent être adaptés. Les opérateurs ont besoin d'accéder à la procédure courante ; l'édition et l'approbation peuvent être restreintes. N'inscris pas de mots de passe, clés privées ou jetons dans la procédure : réfère-toi au mécanisme de gestion des secrets et décris comment une personne autorisée peut demander un accès.

## 11. Cas non couverts et arrêt sécurisé

Une procédure ne peut pas prévoir toutes les circonstances. L'environnement peut avoir changé, l'accès nécessaire peut manquer ou un résultat peut être inconnu. Le document doit indiquer comment arrêter en sécurité, conserver les faits, contacter le responsable et demander une décision. Une exception ne doit pas devenir une autorisation implicite d'improviser un changement en production.

~~~mermaid
flowchart TD
    A[Exécuter une étape] --> B{Résultat conforme ?}
    B -->|Oui| C[Enregistrer la preuve]
    B -->|Non| D[Arrêter les actions non prévues]
    D --> E[Évaluer impact et réversibilité]
    E --> F[Escalader au rôle défini]
    F --> G[Décision approuvée]
    G --> H[Retour, correction ou reprise contrôlée]
    H --> I[Revue de la procédure]
~~~

Lorsqu'une étape échoue, consigne la valeur observée, la cible, l'heure, les actions déjà réalisées et celles qui restent à faire. Précise si la procédure s'est arrêtée à un point sûr. Si un retour arrière a été appliqué, note les contrôles qui prouvent le retour au service. Ne copie pas de secrets dans les preuves.

Une revue après incident compare le déroulement réel à la procédure. Une erreur peut révéler une instruction ambiguë ; une défaillance peut révéler un prérequis manquant ; une réussite obtenue par une action non documentée peut signaler que la procédure est incomplète. L'objectif est d'améliorer la reproductibilité et la sécurité, pas de chercher automatiquement un responsable à blâmer.

## 12. Exemples concrets et travaux pratiques

Pour l'arrivée d'un collaborateur, la procédure peut demander de confirmer l'autorisation, attribuer le matériel, appliquer la configuration standard, tester l'accès et enregistrer la remise. Pour un départ, elle couvre la date, le retrait des accès, la récupération du matériel, le traitement des données, l'actualisation des licences et la preuve. Un courriel isolé ne suffit pas à accorder ou supprimer un privilège critique sans suivre le processus approuvé.

Pour une sauvegarde de configuration réseau, identifie l'équipement, contrôle l'autorisation, exporte vers un dépôt protégé, vérifie le résultat, enregistre la version et prévois un test périodique de restauration. Pour une mise à jour logicielle, distingue l'évaluation, le pilote, l'approbation, la communication, le déploiement, les tests, les échecs et le retour arrière. Une procédure ne donne pas l'autorisation de remplacer la version cible par une autre au milieu de l'opération.

### TP 6 — Transformer une connaissance orale en checklist

Un technicien dit : « Je redémarre le service, je regarde si ça marche, puis je ferme le ticket. » Transforme cette habitude en procédure.

**Correction attendue :** identifier la cible et le propriétaire ; vérifier l'autorisation, l'impact et les alertes ; examiner les dépendances ; annoncer l'action ; exécuter le redémarrage si la procédure l'autorise ; tester le service et la transaction métier ; observer les journaux ; informer les utilisateurs ; documenter les résultats. Si le service ne revient pas, arrêter les actions improvisées et escalader.

### TP 7 — Deux versions en circulation

Deux checklists différentes sont utilisées. Décris la migration.

**Correction :** nommer un propriétaire, comparer les différences, analyser les risques, faire approuver une version de référence, publier dans l'espace officiel et marquer l'ancienne comme obsolète. Remplacer les liens connus et informer l'équipe. La version courante doit être consultable pendant l'intervention.

### TP 8 — Prérequis manquant

La procédure demande une sauvegarde vérifiée, mais la sauvegarde a échoué.

**Correction :** arrêter avant l'action risquée. Évaluer si une autre méthode de retour est officiellement approuvée, obtenir une décision et documenter l'exception. Ne pas poursuivre en supposant que l'opération sera sans conséquence.

## 13. Exercices corrigés

### Exercice 6 — Résultat attendu absent

La ligne dit « tester la connectivité » sans préciser la cible.

**Correction :** préciser la cible, le point de test, le contrôle autorisé, le résultat acceptable et la conduite à tenir sinon. Éviter les tests hors périmètre.

### Exercice 7 — Procédure obsolète

Un technicien retrouve une ancienne procédure dans ses favoris.

**Correction :** retrouver la source de vérité, contrôler la version et signaler le lien obsolète. Ne pas se fier au favori.

### Exercice 8 — Accès manquant

L'opérateur ne dispose pas de l'accès requis.

**Correction :** s'arrêter à un point sûr, noter ce qui a été effectué, demander l'accès par le processus autorisé et prévenir le responsable si la fenêtre est menacée. Ne pas emprunter les identifiants d'un collègue.

### Exercice 9 — Checklist terminée, service en panne

Toutes les cases sont cochées mais l'application échoue encore.

**Correction :** l'objectif fonctionnel n'est pas atteint. Ne clôture pas uniquement parce que la liste a été parcourue. Documente les symptômes, diagnostique ou escalade, puis révise la procédure si elle ne couvrait pas le contrôle nécessaire.

## 14. Défi final — Standardiser trois procédures

Crée des procédures pour l'arrivée d'un poste, une mise à jour logicielle et une restauration de configuration. Chacune doit définir le propriétaire, le périmètre, les prérequis, les étapes, la sécurité, les tests, les preuves, les exceptions, la version et l'approbation.

**Correction détaillée :** la structure est cohérente, mais les contrôles restent spécifiques à chaque tâche. La procédure d'arrivée vérifie l'autorisation, l'identité et les accès ; la mise à jour documente la cible et le retour arrière ; la restauration valide le point, la cohérence et le test de service. Teste chaque document avec un technicien différent de l'auteur et corrige les étapes qui nécessitent une explication orale.


## 15. Mesurer la qualité des procédures

Le nombre de pages ou de procédures publiées n'est pas une mesure de qualité. Pour évaluer un corpus, examine la couverture des tâches critiques, la proportion de documents revus dans les délais, les procédures sans propriétaire, les incidents liés à une instruction ambiguë, les écarts constatés lors des interventions et les résultats des essais effectués par des personnes différentes des auteurs.

L'indicateur de couverture doit avoir un dénominateur défini : tâches critiques identifiées dans le registre de risques, processus récurrents, actifs couverts ou opérations à autorisation obligatoire. Si la liste des tâches n'est pas complète, un taux de couverture peut être trompeur. Le rapport doit donc nommer la source du dénominateur et les catégories qui restent hors périmètre.

Un test de procédure se réalise en environnement adapté. Le testeur suit le document sans aide orale, note les ambiguïtés, les informations qu'il doit deviner, les liens morts, les prérequis indisponibles et les résultats impossibles à prouver. Pour les opérations risquées, la revue doit également vérifier que l'étape dangereuse est limitée, que le droit requis est identifié et que la procédure dispose d'un point d'arrêt.

~~~mermaid
flowchart TD
    A[Procédure publiée] --> B[Choisir un testeur indépendant]
    B --> C[Exécuter dans un cadre sûr]
    C --> D[Noter écarts et ambiguïtés]
    D --> E[Classer le risque]
    E --> F[Corriger et faire approuver]
    F --> G[Retester et archiver la preuve]
~~~

Un changement d'outil peut rendre une procédure obsolète sans modifier son titre. Lors d'une mise à niveau, identifie les documents liés à la version, teste les étapes concernées et marque les anciennes versions comme remplacées. Le responsable doit pouvoir retrouver la version en vigueur à une date donnée pour expliquer une intervention ou répondre à un audit.

Le catalogue de procédures doit aussi offrir une navigation simple. Utilise des titres parlants, des catégories, des mots-clés et des liens depuis les tickets ou l'inventaire lorsque cela est utile. Les documents sensibles doivent être accessibles aux rôles prévus sans exposer des identifiants dans les fichiers. Une procédure facile à trouver est plus probable d'être appliquée ; une procédure non retrouvable agit comme une procédure inexistante.
