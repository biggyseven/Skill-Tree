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
