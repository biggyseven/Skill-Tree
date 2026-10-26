# GitOps et Argo CD — Expert

> **Mise en contexte.** Une plateforme Kubernetes gère plusieurs environnements et équipes. La CI construit une image valide, mais des modifications manuelles créent une dérive dans le cluster, la version exécutée n’est pas toujours reliée à son commit source et les retours arrière sont improvisés. Au niveau expert, l’enjeu consiste à concevoir un modèle de livraison déclaratif, gouverné, vérifiable et observable.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois pouvoir concevoir une architecture GitOps, séparer correctement CI et CD, organiser les dépôts et la promotion des environnements, définir les politiques de synchronisation Argo CD, gouverner les secrets et permissions, diagnostiquer les écarts et préparer un retour arrière cohérent avec l’historique Git.

## Prérequis

Maîtriser Git, les pipelines CI/CD, Kubernetes, les manifests déclaratifs, les namespaces, les permissions RBAC et les bases du déploiement de conteneurs. Les exemples YAML sont des modèles à adapter à la version d’Argo CD et aux APIs de la plateforme cible.

## 1. GitOps : déclarer, versionner et réconcilier

GitOps consiste à décrire l’état attendu d’un système de manière déclarative, conserver cette description sous contrôle de version et utiliser un agent qui observe l’état voulu puis le réconcilie avec l’état réel. Git n’est pas un simple stockage de YAML : le dépôt devient une source de vérité, les changements ont un historique, les revues exposent le diff et le contrôleur détecte les écarts.

La CI valide le code et produit un artefact identifiable. La promotion modifie ensuite une référence dans le dépôt de configuration. Argo CD lit les manifests approuvés et les applique au cluster cible. La CI n’a ainsi pas besoin de posséder par défaut un accès administrateur au cluster de production.

~~~text
Code applicatif -> tests -> image versionnée -> registre
                                      |
Dépôt de configuration <--- promotion approuvée de la version
          |
          v
      Argo CD
          |
          v
Cluster Kubernetes <--- détection et réconciliation de la dérive
~~~

Le modèle repose sur quatre idées : état déclaratif, historique de versions protégé, récupération automatisée de cet état et réconciliation continue. Il ne remplace pas les contrôles d’accès à Git, les tests, la validation des artefacts ou le plan de gestion d’incident.

## 2. CI, artefacts et promotion

La CI doit produire une image associée à une révision source. Un tag mutable comme « latest » rend l’audit ambigu si le même tag pointe successivement vers plusieurs images. Utilise un identifiant de version ou un digest, et conserve le lien vers le commit, les tests et les informations de construction.

La promotion vers staging ou production doit porter sur un artefact déjà construit, au lieu de reconstruire une image différente pour chaque environnement. La configuration propre à l’environnement peut changer, mais l’identité de l’artefact doit rester traçable.

~~~text
Pull request du code
  -> tests et analyse
  -> construction d'une image identifiable
  -> publication dans un registre contrôlé
  -> promotion d'un digest dans le dépôt GitOps
  -> revue du diff
  -> réconciliation par Argo CD
  -> vérifications de santé
~~~

Pour les environnements sensibles, ajoute les approbations, les propriétaires de code et des protections de branche. Un workflow de test ne doit pas recevoir les mêmes secrets ou permissions qu’un workflow autorisé à publier ou promouvoir une version en production.

## 3. Architecture Argo CD et ressource Application

Argo CD suit des sources, génère ou récupère les manifests et compare l’état désiré aux ressources observées. Une ressource Application précise typiquement la source, la révision, le chemin ou chart, la destination et la politique de synchronisation. Les permissions peuvent être limitées avec les projets Argo CD et le RBAC.

~~~yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: catalogue-staging
  namespace: argocd
spec:
  project: staging
  source:
    repoURL: https://github.com/example/platform-config.git
    targetRevision: main
    path: apps/catalogue/overlays/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: catalogue
  syncPolicy:
    automated:
      prune: false
      selfHeal: true
~~~

Ce manifest est illustratif : le dépôt, la destination et les chemins doivent être remplacés et validés. Dans un environnement critique, assure-toi que le projet limite les dépôts autorisés, les clusters, les namespaces et les types de ressources. Une Application capable de synchroniser n’importe quelle ressource dans n’importe quel cluster constitue une frontière de privilèges trop large.

## 4. Organiser dépôts, bases et environnements

Il n’existe pas une seule structure optimale. Un dépôt applicatif distinct d’un dépôt de déploiement facilite la séparation entre développement et exploitation. Un mono-dépôt peut fonctionner si les permissions, la revue et la propriété des fichiers restent précises.

~~~text
platform-config/
  apps/
    catalogue/
      base/
      overlays/
        dev/
        staging/
        production/
    paiement/
      base/
      overlays/
        staging/
        production/
  platform/
    projects/
    policies/
~~~

Kustomize et Helm peuvent réutiliser des configurations. Maintiens un socle commun et des différences d’environnement explicites. Le rendu final doit être inspectable : une variable de production qui modifie un accès, une image ou une politique de sécurité ne doit pas se cacher dans une logique de template difficile à examiner.

Les secrets ne doivent pas être stockés en clair dans le dépôt suivi. Utilise une intégration de gestion des secrets adaptée ou une solution de chiffrement dont les clés sont gouvernées séparément. Protéger le dépôt ne suffit pas si les identifiants donnant accès au secret sont eux-mêmes versionnés.

## 5. Synchronisation, prune et self-heal

Une synchronisation applique l’état souhaité à la cible. L’auto-sync peut permettre au contrôleur de déployer après une modification approuvée dans Git, sans donner à la CI un accès direct au serveur Kubernetes.

Deux options nécessitent une attention particulière :

- **Prune** autorise le nettoyage des ressources gérées qui ont disparu de la configuration déclarative.
- **Self-heal** permet de corriger certaines dérives lorsque l’état réel est modifié en dehors de Git.

La suppression automatique est un choix de cycle de vie, pas une option esthétique. Un manifest supprimé peut entraîner la suppression d’une ressource réelle. Évalue l’impact sur les volumes, namespaces, ressources partagées et bases de données. Utilise des protections et une politique de validation avant d’activer prune à grande échelle.

~~~yaml
syncPolicy:
  automated:
    enabled: true
    prune: false
    selfHeal: true
~~~

La syntaxe exacte dépend de la version supportée ; confirme-la dans la documentation de la version déployée. En production, une stratégie prudente peut activer la correction de dérive mais garder les suppressions sous validation spécifique. Ne permets pas à l’automatisation de vider un ensemble de ressources sans une protection explicite.

## 6. Ordre de synchronisation, migrations et stratégies de livraison

GitOps ne rend pas automatiquement un déploiement sûr. Une mise à jour peut dépendre d’une CRD, d’un contrôleur, d’un secret, d’une migration de données ou d’une autre application. Définis les dépendances et les critères de réussite avant d’ordonner l’application.

Une livraison risquée peut être découpée en étapes : préparer les dépendances, appliquer la migration compatible, déployer une version sur un périmètre limité, vérifier la santé, puis augmenter la portée. Les hooks et les vagues de synchronisation d’Argo CD sont utiles pour certains ordres mais doivent rester idempotents, testés et compréhensibles.

Le canary et le blue/green exigent des mécanismes de routage et de mesure appropriés. Le seul fait de synchroniser une ressource Kubernetes ne garantit pas une répartition progressive du trafic. Mesure les erreurs, la latence, la saturation et les résultats métier, puis établis un seuil d’arrêt.

## 7. Sécurité du contrôleur et gouvernance

Argo CD est un système privilégié : il peut lire des dépôts et modifier des ressources de cluster. Sa sécurité concerne donc l’identité, les dépôts autorisés, les destinations, les droits de synchronisation, les secrets et la traçabilité.

Mesures de base :
- séparer lecture, synchronisation et administration ;
- protéger l’authentification et utiliser une identité centralisée lorsque disponible ;
- limiter les dépôts, namespaces, clusters et types de ressources ;
- protéger les branches et exiger la revue des modifications de configuration ;
- restreindre les identifiants de dépôts et faire tourner les secrets ;
- journaliser les opérations et l’identité du changement ;
- auditer régulièrement les permissions et les applications orphelines ;
- tester les politiques avec des appels autorisés et interdits.

Un développeur capable de modifier la branche suivie ou la ressource Application peut influencer la production. Les protections Git et les droits Argo CD font partie du périmètre de sécurité, et non de la seule organisation de l’équipe.

## 8. Diagnostiquer OutOfSync et Degraded

L’état Sync et l’état Health ne sont pas interchangeables. Une application peut être synchronisée alors qu’un pod est dégradé. Elle peut également être saine au sens Kubernetes mais OutOfSync parce qu’une ressource réelle diffère de la source déclarée.

Commandes utiles de la CLI Argo CD :

~~~bash
argocd app list
argocd app get catalogue-staging
argocd app diff catalogue-staging
argocd app history catalogue-staging
argocd app sync catalogue-staging
~~~

La commande sync applique des changements et n’est pas une simple commande d’observation. Commence par get et diff, vérifie le dépôt suivi, la révision et le cluster, puis exécute une action de synchronisation uniquement si elle est attendue et autorisée.

Démarche d’investigation :
1. confirmer la révision source attendue ;
2. inspecter le diff et les manifests rendus ;
3. lire les erreurs du contrôleur et vérifier les permissions ;
4. consulter les événements, pods, endpoints et logs Kubernetes ;
5. vérifier les hooks et les dépendances ;
6. identifier si l’écart vient d’une modification manuelle, du rendu, du manifeste ou d’un contrôleur ;
7. corriger la source ou la cause puis réexaminer le diff.

Une exception ignore-differences globale peut cacher une dérive dangereuse. Si une comparaison doit être ignorée, limite précisément la ressource et le champ, documente la raison et crée une procédure de révision.

## 9. Retour arrière durable

Le retour arrière GitOps le plus traçable consiste généralement à rétablir une configuration versionnée connue comme bonne, puis à laisser le contrôleur la réconcilier. Vérifie les contraintes de la version d’Argo CD avant d’utiliser un rollback applicatif, notamment si la synchronisation automatique est activée.

Avant le retour, identifie l’image et son digest, évalue la compatibilité avec les données et vérifie les migrations exécutées. Revenir à une ancienne image ne restaure pas automatiquement les données transformées par une migration irréversible.

Après le changement :
- contrôle que la révision attendue est suivie ;
- vérifie Sync et Health ;
- lance des tests fonctionnels ;
- observe le taux d’erreurs et la latence ;
- consigne le résultat et la décision finale.

Ne confonds pas la réussite de la réconciliation avec la restauration fonctionnelle du service. La preuve de succès doit inclure les critères d’exploitation.

## 10. TP guidé : promouvoir une version en GitOps

**Situation :** une application en staging doit recevoir une nouvelle image testée.

1. Construis un artefact lié à un commit connu.
2. Modifie uniquement la référence d’image dans le dépôt de configuration.
3. Ouvre une Pull Request contenant le diff, les tests et l’identifiant de l’artefact.
4. Fais vérifier la destination, le namespace, les permissions et les secrets.
5. Fusionne selon la procédure d’approbation.
6. Vérifie dans Argo CD la révision suivie, Sync et Health.
7. Dans un cluster jetable, simule une dérive et vérifie le comportement prévu.
8. Reviens à la référence précédente via le dépôt de configuration.
9. Vérifie le service et documente le retour arrière.

**Critères de réussite :** la version exécutée est traçable, la CI n’a pas besoin de privilèges inutiles, le diff est revu, la dérive est comprise et le retour arrière reste enregistré dans Git.

## Exercices corrigés

**1. Pourquoi séparer CI et contrôleur de déploiement ?**  
La CI valide et construit l’artefact ; le contrôleur réconcilie la configuration approuvée avec le cluster. Cette séparation réduit les permissions de production exposées aux jobs de build.

**2. Quel risque introduit prune ?**  
Des ressources gérées qui ne sont plus déclarées peuvent être supprimées. Il faut vérifier le cycle de vie, les données et les protections avant de permettre les suppressions automatiques.

**3. Une application Synced est-elle forcément disponible ?**  
Non. Sync indique la concordance de l’état déclaré avec l’état observé. Health et les tests fonctionnels sont nécessaires pour évaluer le service.

**4. Pourquoi revenir par Git plutôt que modifier directement le cluster ?**  
Parce que Git reste la source déclarative. Un changement direct risquerait d’être annulé par la réconciliation et ferait perdre la traçabilité de la décision.

## Défi final corrigé

Conçois une plateforme GitOps multi-environnements avec promotion par Pull Request, synchro automatique en staging et contrôle renforcé en production.

**Correction attendue :** artefacts immuables, référence d’image explicite, dépôts et chemins gouvernés, AppProjects limitant destinations et ressources, RBAC minimal, secrets hors du dépôt en clair, revue du diff, approbations pour production, vérifications Health et procédure de retour via une révision Git approuvée.

## Synthèse

GitOps avec Argo CD fournit un modèle déclaratif et réconcilié. Sa fiabilité dépend toujours de la qualité des manifests, des permissions, de l’identité des artefacts, des politiques de suppression et des vérifications après déploiement.

## Liste de contrôle d’une livraison experte

Avant d’autoriser une promotion, examine l’ensemble du chemin de livraison plutôt qu’un seul indicateur :

- Le commit source et l’artefact publié sont-ils reliés par une référence stable ?
- Le scan de sécurité et les tests correspondent-ils à cet artefact précis ?
- Le dépôt GitOps pointe-t-il vers le bon digest et le bon environnement ?
- La Pull Request expose-t-elle les différences importantes de configuration ?
- L’identité du contrôleur possède-t-elle uniquement les permissions requises ?
- La configuration de synchronisation autorise-t-elle des suppressions imprévues ?
- Les secrets sont-ils injectés par un mécanisme sécurisé et renouvelable ?
- Le plan de déploiement a-t-il des seuils d’arrêt et des tests de santé ?
- Le retour arrière prend-il en compte les migrations et les données persistantes ?
- Les journaux permettent-ils de retrouver qui a promu la version et pourquoi ?

Une livraison est prête lorsque ces questions ont des réponses vérifiables et que les contrôles ont été exécutés sur un environnement représentatif. Une revue ne doit pas seulement cocher des cases : elle doit vérifier que chaque mesure correspond au risque de l’application.

## Étude de cas : l’application synchronisée mais inutilisable

Une équipe constate qu’Argo CD indique que les ressources sont synchronisées, mais les utilisateurs obtiennent des erreurs HTTP 503. Ne commence pas par resynchroniser sans examiner les symptômes. Vérifie d’abord la disponibilité des pods et des endpoints, puis les événements Kubernetes, le routage, les readiness probes et les journaux de l’application. Si une mise à jour vient d’être promue, compare la version et les paramètres de la révision précédente. Un manifeste appliqué peut être syntaxiquement correct alors que la configuration métier ou la dépendance externe est incorrecte.

La résolution doit être liée à une preuve. Si la nouvelle version a introduit le problème, rétablis la référence de configuration précédente selon le processus approuvé, laisse Argo CD réconcilier, puis vérifie la santé et les indicateurs utilisateurs. Enregistre ensuite la cause racine et les contrôles manquants pour éviter que l’incident ne se reproduise.

Cette étude illustre la différence entre convergence déclarative et disponibilité. L’état Sync est un indicateur important, mais il ne peut pas remplacer les contrôles fonctionnels, la télémétrie applicative et un processus de changement responsable.