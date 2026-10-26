# Observabilité — Débutant : comprendre métriques, journaux et traces

> **Mise en contexte.** Une application devient lente. Le service est-il indisponible ? La base de données est-elle saturée ? Une nouvelle version a-t-elle introduit une régression ? L’observabilité aide à comprendre ce que fait un système à partir de signaux accessibles aux équipes, au lieu de se limiter à constater qu’il est en panne.

## Objectifs d’apprentissage

Tu vas apprendre à distinguer supervision et observabilité, expliquer métriques, journaux et traces, comprendre le rôle de Prometheus et Grafana, choisir des indicateurs simples et construire une démarche de diagnostic.

## Prérequis

Connaître les bases de Linux, les services, les adresses IP, DNS, les ports et les notions d’application et de base de données. Aucun environnement Prometheus réel n’est requis pour les schémas et exercices initiaux.

## 1. Supervision et observabilité

La supervision surveille des indicateurs et alerte lorsqu’une condition est remplie. L’observabilité aide à investiguer des comportements qui n’ont pas forcément été prévus au moment de concevoir les tableaux de bord. Les deux sont complémentaires : des alertes utiles détectent les symptômes, tandis que les signaux détaillés aident à expliquer les causes.

Trois familles de signaux sont courantes :

| Signal | Question principale | Exemple |
|---|---|---|
| Métrique | Combien, à quelle vitesse, quelle évolution ? | requêtes par seconde, mémoire utilisée |
| Journal (log) | Quel événement s’est produit ? | erreur de connexion à la base |
| Trace | Où le temps a-t-il été consommé dans une requête ? | appel lent entre deux services |

Aucun signal ne suffit seul. Une métrique peut montrer que les erreurs augmentent, les journaux expliquer un événement et une trace mettre en évidence un service lent sur le chemin d’une requête.

## 2. Prometheus en termes simples

Prometheus collecte des séries temporelles : une valeur numérique associée à un nom de métrique, à un moment donné et à des labels. Il peut interroger périodiquement des cibles qui exposent des métriques, puis stocker les valeurs pour les requêtes et les alertes.

~~~text
Application / Exporter
       |
       | endpoint de métriques
       v
   Prometheus  ----> règles d'alerte
       |
       v
   requêtes PromQL
       |
       v
    Grafana ----> tableaux de bord
~~~

Un exporter traduit des informations d’un système en métriques exposées. Par exemple, l’exporter d’un hôte peut exposer CPU, mémoire, disque et réseau. L’application doit aussi fournir des métriques métier lorsque c’est nécessaire.

## 3. Mesures, séries temporelles et labels

Une métrique doit exprimer une quantité ou un événement mesurable. Les noms et types exacts dépendent de l’application, mais on trouve souvent compteurs de requêtes, histogrammes de durée et jauges d’état.

Les labels permettent de distinguer des dimensions comme le service, la méthode HTTP ou le code de réponse. Évite d’ajouter un identifiant unique d’utilisateur ou de requête à chaque série : cela peut créer une cardinalité très élevée et augmenter le coût de stockage et de calcul.

Une métrique n’est pas un journal. Ne transforme pas un message de log complet en label. Utilise les métriques pour les tendances et les alertes, et les logs pour les détails événementiels.

## 4. Grafana et les tableaux de bord

Grafana permet de créer des tableaux de bord à partir de Prometheus et d’autres sources. Un bon tableau de bord répond à une question opérationnelle précise. Évite les panneaux ajoutés simplement parce qu’une métrique est disponible.

Un tableau de bord initial peut montrer :
- le taux de requêtes ;
- la proportion d’erreurs ;
- la latence ;
- la saturation CPU, mémoire et disque ;
- la disponibilité et les dépendances importantes.

Les couleurs doivent aider à comprendre les écarts sans masquer les unités ou les périodes. Tout panneau doit avoir une description, une unité correcte et une plage temporelle pertinente.

## 5. Les quatre signaux d’un service web

Pour un service HTTP, on peut suivre :
- trafic : nombre ou taux de requêtes ;
- erreurs : requêtes échouées ou réponses inattendues ;
- durée : distribution des temps de réponse ;
- saturation : ressources proches de leur limite.

La moyenne de latence peut cacher une minorité de requêtes extrêmement lentes. Les percentiles p95 ou p99 aident à observer cette queue de distribution, à condition que la métrique soit collectée correctement et que la fenêtre soit suffisamment représentative.

Une alerte doit être liée à l’impact. Une utilisation CPU élevée n’est pas toujours une panne, mais une hausse simultanée de la latence, des erreurs et de la saturation mérite une investigation.

## 6. Lire et créer une alerte utile

Une alerte doit permettre de répondre rapidement à trois questions : que se passe-t-il, quel est l’impact et quelle action entreprendre ? Un avertissement non actionnable produit du bruit et finit par être ignoré.

Une bonne alerte inclut :
- la condition et la durée de dépassement ;
- le service ou environnement concerné ;
- le lien vers le tableau de bord et les runbooks ;
- un niveau de gravité ;
- le destinataire et l’action attendue.

Les seuils doivent être adaptés à la ligne de base, au SLO et aux objectifs métier. Ne copie pas un seuil universel sans mesurer le comportement normal du service.

## 7. Démarche de diagnostic

Quand une alerte apparaît, commence par définir l’impact : tous les utilisateurs ou une partie, toutes les opérations ou une méthode, depuis quelle heure et quelle région. Vérifie ensuite si le changement correspond à un déploiement, à un incident réseau ou à un événement de dépendance.

~~~text
Latence élevée
  -> erreurs également en hausse ?
  -> CPU ou mémoire saturés ?
  -> base de données lente ?
  -> une version précise est-elle concernée ?
  -> les traces montrent-elles un appel dominant ?
  -> un changement récent explique-t-il le début ?
~~~

L’objectif n’est pas de collecter tous les signaux possibles, mais d’utiliser des signaux cohérents qui permettent de réduire les hypothèses.

## 8. Sécurité et rétention

Les journaux peuvent contenir des noms, adresses, jetons ou paramètres sensibles. Définis ce qui peut être collecté, qui a accès aux données et combien de temps elles sont conservées. Masque les secrets avant expédition ; réduire l’accès après la collecte ne supprime pas le risque de les avoir stockés.

La supervision elle-même nécessite des comptes et des permissions. Une personne qui peut modifier les règles d’alerte ou les tableaux de bord peut influencer la détection d’incidents. Sépare les droits de lecture et d’administration et protège les identifiants des sources de données.

## 9. TP guidé : diagnostiquer un service lent

Utilise un jeu de données ou un scénario simulé :
1. Observe une métrique de trafic et une métrique d’erreur.
2. Compare la latence moyenne avec un percentile.
3. Observe le CPU et la mémoire pendant la même fenêtre.
4. Lis quelques logs autour de l’heure du problème.
5. Examine une trace si le système en fournit.
6. Énonce une hypothèse et les données qui la soutiennent.
7. Propose une vérification supplémentaire avant de déclarer la cause racine.

**Réussite :** tu différencies symptômes et causes, cites les signaux utilisés, notes l’incertitude et proposes la prochaine vérification.

## Exercices corrigés

**1. Quelle différence entre métrique et journal ?**  
Une métrique décrit une valeur quantitative dans le temps ; un journal enregistre des événements avec leurs détails. Les deux se complètent.

**2. Pourquoi limiter la cardinalité des labels ?**  
Chaque combinaison de labels peut créer une série distincte. Un identifiant unique par utilisateur ou requête peut créer un nombre de séries difficile à stocker et interroger.

**3. Pourquoi la moyenne peut-elle masquer un problème ?**  
Quelques réponses très lentes peuvent toucher une partie importante des utilisateurs tout en ayant peu d’effet sur la moyenne. Des percentiles et des distributions offrent une meilleure visibilité.

**4. Une alerte CPU à 90 % indique-t-elle toujours un incident ?**  
Non. Il faut rapprocher l’utilisation des erreurs, de la latence, de la saturation des autres ressources et de l’impact métier.

## Défi final corrigé

Un service répond lentement mais ne renvoie pas encore beaucoup d’erreurs. Propose un tableau de bord et une méthode de diagnostic.

**Correction attendue :** afficher trafic, latence p95, erreurs, CPU, mémoire et état de dépendance sur une fenêtre alignée ; explorer logs et traces ; comparer avant/après un changement ; vérifier si l’effet est concentré sur un endpoint ou une version ; documenter l’hypothèse et les preuves avant de modifier la production.

## Synthèse

L’observabilité s’appuie sur des métriques, des logs et des traces complémentaires. Prometheus collecte et interroge des séries temporelles, Grafana aide à les visualiser, mais l’essentiel est la qualité des indicateurs, la pertinence des alertes et la méthode d’investigation.