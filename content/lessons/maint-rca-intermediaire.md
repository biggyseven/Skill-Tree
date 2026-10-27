# Analyse de cause racine (5 Pourquoi, Ishikawa)

> **Mise en contexte**
>
> Tous les lundis matin, les utilisateurs signalent que l'application est lente. L'équipe redémarre le serveur et la situation s'améliore, puis le problème revient la semaine suivante. Dire « le serveur est lent » décrit un symptôme, pas une explication exploitable. L'analyse de cause racine cherche à identifier les conditions qui ont produit l'incident, à tester les hypothèses et à réduire le risque de répétition.

## Objectifs du cours

Tu apprendras à séparer les faits des hypothèses, construire une chronologie, utiliser les 5 Pourquoi et Ishikawa, tester des causes possibles, choisir des actions correctives proportionnées et vérifier leur efficacité sans rechercher un coupable.

## 1. Symptôme, cause contributive et cause racine

Un symptôme est ce que l'on observe : une requête échoue, un disque se remplit ou un service redémarre. Une cause contributive augmente la probabilité ou l'impact de l'incident. Une cause racine est une explication causale suffisamment étayée pour orienter une action durable dans le périmètre étudié.

La cause racine n'est pas forcément unique. Une panne peut résulter de plusieurs facteurs : seuils de supervision incomplets, capacité insuffisante, changement non vérifié et procédure de retour arrière inadéquate. Le but n'est pas d'inventer une réponse simple, mais de trouver les causes que les preuves permettent de soutenir.

Sépare toujours :
- **Faits :** mesures, journaux, horodatages, changement enregistré et résultats reproductibles.
- **Hypothèses :** explications possibles à confirmer.
- **Conclusions :** hypothèses appuyées par des preuves et confrontées aux alternatives.
- **Actions :** mesures immédiates, correction de fond et prévention de la récidive.

## 2. Préserver les éléments et construire une chronologie

Commence par définir le périmètre : service, période, utilisateurs affectés, impact et état actuel. Collecte les éléments nécessaires selon les autorisations et les règles de rétention : journaux applicatifs, métriques de supervision, changements récents, événements système, tickets similaires et mesures de capacité.

Une chronologie peut prendre cette forme :

| Heure | Fait observé | Source | Interprétation actuelle |
|---|---|---|---|
| 08 h 55 | Début de hausse de latence | Tableau de bord | À confirmer |
| 09 h 02 | Files de requêtes en hausse | Métrique applicative | Piste à explorer |
| 09 h 08 | Redémarrage du service enregistré | Journal de changement | A modifié l'état, pas nécessairement la cause |
| 09 h 12 | Latence redevenue normale | Sonde fonctionnelle | Rétablissement observé |

Les heures doivent provenir des sources et utiliser un fuseau cohérent. Vérifie les décalages d'horloge. Ne supprime pas les journaux et ne lance pas de modification susceptible d'écraser les preuves avant d'avoir évalué leur nécessité. La collecte doit rester proportionnée à l'incident.

## 3. La méthode des 5 Pourquoi

Les 5 Pourquoi consistent à demander pourquoi un résultat s'est produit, puis à poursuivre en utilisant les réponses comme pistes à vérifier. Le nombre cinq est indicatif, pas une obligation ; une chaîne peut être plus courte ou comporter plusieurs branches.

Exemple à examiner :
1. Pourquoi les utilisateurs voient-ils des erreurs ? Parce que les requêtes dépassent le délai.
2. Pourquoi les requêtes dépassent-elles le délai ? Parce que la file de traitement s'accumule.
3. Pourquoi la file s'accumule-t-elle ? Parce que les traitements prennent plus de temps que d'habitude.
4. Pourquoi prennent-ils plus de temps ? Une piste est la saturation d'une dépendance, à vérifier avec les métriques.
5. Pourquoi cette saturation n'a-t-elle pas été détectée plus tôt ? Une hypothèse est l'absence d'un indicateur ou d'un seuil adapté.

Chaque réponse doit être confrontée aux éléments. Une chaîne bien racontée mais non vérifiée n'est pas une analyse de cause racine.

## 4. Le diagramme d'Ishikawa

Ishikawa organise les hypothèses par grandes catégories pour réduire le risque de s'arrêter à la première explication. Dans un système informatique, on peut adapter les catégories aux personnes, aux procédures, à la technologie, aux données, à l'environnement et aux dépendances externes.

~~~mermaid
flowchart LR
    A[Incident observé] --> B[Personnes et compétences]
    A --> C[Procédures et changements]
    A --> D[Technologie et capacité]
    A --> E[Données et configuration]
    A --> F[Environnement et dépendances]
    B --> G[Hypothèses à tester]
    C --> G
    D --> G
    E --> G
    F --> G
    G --> H[Preuves et expériences]
    H --> I[Causes étayées et actions]
~~~

Le diagramme ne prouve aucune cause ; il aide à produire des hypothèses diverses. Évite les catégories qui blâment une personne. Analyse les conditions, les garde-fous, les informations disponibles et la conception du processus.

## 5. Tester les hypothèses

Pour chaque hypothèse, précise le fait qui la soutient, les éléments qui la contredisent, le test sûr qui permet de la vérifier et la décision selon le résultat. Les tests doivent être proportionnés et autorisés. Lorsque l'incident a un impact fort, privilégie la collecte non destructive, un environnement de reproduction ou une analyse par un spécialiste.

| Hypothèse | Preuve attendue | Test raisonnable | Limite |
|---|---|---|---|
| Le stockage manque d'espace | Courbe d'espace et erreurs liées | Comparer l'historique et l'état du volume | L'espace faible peut être un symptôme d'une autre activité |
| Une modification récente déclenche les erreurs | Chronologie cohérente et différence de configuration | Comparer la version et reproduire en test si possible | Une succession temporelle ne prouve pas seule la causalité |
| Le réseau provoque la latence | Mesures de perte, délai ou erreurs sur le chemin concerné | Comparer plusieurs points de mesure | Un ping seul ne représente pas forcément la voie applicative |

Ne conclus pas à partir d'une seule coïncidence. Si les preuves sont insuffisantes, note la cause comme probable ou inconnue et définis ce qui permettrait de progresser. L'honnêteté sur l'incertitude vaut mieux qu'une certitude inventée.

## 6. Passer de la cause aux actions

Une bonne analyse ne s'arrête pas à une explication. Distingue :
- **Action immédiate :** rétablir ou limiter l'impact.
- **Correction :** éliminer la cause confirmée ou réduire directement sa présence.
- **Prévention :** améliorer la détection, la capacité, les tests, la procédure ou la conception.
- **Vérification :** mesurer si la modification a réduit la probabilité ou l'impact de récurrence.

Chaque action doit avoir un responsable, une échéance, un indicateur d'achèvement et un critère d'efficacité. « Surveiller davantage » est trop vague ; « créer une alerte sur la croissance du volume, vérifier le seuil en test et mesurer les alertes pertinentes pendant la période convenue » est plus vérifiable.

## 7. Mesurer l'efficacité et partager le résultat

Après la mise en œuvre, vérifie si les symptômes sont absents ou réduits pendant une période pertinente, si les contrôles déclenchent au bon moment et si le contournement est toujours nécessaire. L'absence immédiate de récidive ne garantit pas un succès définitif si le cycle naturel de l'incident est hebdomadaire.

Le rapport doit résumer l'impact, la chronologie, les causes étayées, les facteurs contributifs, les preuves, les actions et les incertitudes restantes. Il doit aider l'équipe à apprendre, sans exposer des données sensibles et sans transformer l'analyse en accusation personnelle.

## Mise en pratique

### Laboratoire : rechercher la cause d'une lenteur récurrente

Scénario fictif : une application est lente chaque lundi à 9 h. Le redémarrage la rétablit temporairement. Tu disposes d'un historique de latence, de l'utilisation CPU, de l'espace disque, de l'état d'une dépendance et d'un journal des changements.

1. Écris cinq faits observables sans interprétation.
2. Construis une chronologie avec la source de chaque heure.
3. Utilise les 5 Pourquoi pour formuler une chaîne d'hypothèses, sans prétendre que chaque réponse est vraie.
4. Construis un Ishikawa avec au moins quatre catégories pertinentes.
5. Choisis deux hypothèses et précise le test, la preuve attendue et ce qui invaliderait chaque hypothèse.
6. Rédige une action immédiate, une action de fond et un indicateur de vérification.
7. Présente une conclusion avec un niveau de confiance explicite et les inconnues restantes.

**Résultat attendu :** une analyse fondée sur les preuves, qui différencie clairement hypothèse et cause étayée. Ne réalise pas de changement destructif sur une production pour les besoins du laboratoire.

## Exercices corrigés

**1. Le service fonctionne après un redémarrage. Est-ce la preuve que le redémarrage était la cause de la panne ?**

Correction : non. Il a servi de contournement ou d'action de rétablissement, mais ne démontre pas pourquoi l'incident s'est produit. Il faut confronter plusieurs hypothèses à des éléments vérifiables.

**2. Quel est le risque d'utiliser les 5 Pourquoi sans vérifier les réponses ?**

Correction : la chaîne peut transformer des suppositions en récit cohérent mais faux. Chaque réponse doit devenir une hypothèse à tester avec des preuves.

**3. Pourquoi utiliser Ishikawa si une première piste semble évidente ?**

Correction : pour considérer d'autres facteurs et éviter de conclure prématurément. Le diagramme aide à structurer les pistes mais ne remplace pas les tests.

**4. Que faire si la cause racine ne peut pas encore être déterminée ?**

Correction : documenter les faits et les hypothèses, indiquer les limites de l'analyse, définir les preuves et tests nécessaires, puis suivre les actions de réduction de risque. Ne pas inventer de certitude.

## Défi final corrigé

Une erreur applicative revient chaque lundi. Les journaux montrent des délais d'attente, la latence réseau ne change pas sensiblement et le redémarrage résout temporairement le problème. L'équipe soupçonne une saturation de la base de données.

**Correction attendue :** enregistrer les faits et leurs sources, aligner les horloges, comparer les métriques de base de données et d'application autour des incidents, rechercher les changements et les tâches planifiées du lundi, puis tester la piste dans un environnement sûr ou avec l'équipe responsable. Si les preuves confirment une saturation, définir une correction mesurable et un contrôle préventif. Sinon, poursuivre l'analyse des hypothèses alternatives. Le rapport doit qualifier le niveau de confiance et la période de validation nécessaire.
