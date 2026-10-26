# Service Mesh (Istio, Linkerd) — Intermédiaire

> **Mise en contexte.** Une plateforme Kubernetes possède plusieurs versions d’un service de paiement. L’équipe veut répartir progressivement les requêtes, authentifier les workloads, surveiller la latence et limiter les effets d’une panne. Le défi intermédiaire consiste à déployer des politiques contrôlées, testables et réversibles.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois savoir préparer une adoption de mesh, structurer le routage entre versions, concevoir des politiques mTLS et d’autorisation, configurer des délais d’attente et retries raisonnables, lire les métriques et construire une procédure de diagnostic.

## Prérequis

Maîtriser Kubernetes, les services et endpoints, TLS, les conteneurs, les concepts de plan de contrôle/plan de données et les principes d’identité des workloads. Ce cours s’appuie sur le niveau débutant.

## 1. Préparer l’introduction d’un mesh

Commence par un inventaire des flux : producteur, consommateur, protocole, port, sens de communication, niveau de disponibilité et données sensibles. Pour une migration, vérifie également les connexions qui contournent les services attendus, les appels externes et les dépendances au niveau réseau.

Une stratégie progressive peut comporter :
1. observation sans politiques restrictives ;
2. activation d’une identité et du chiffrement sur un périmètre limité ;
3. vérification des erreurs de certificat et des dépendances ;
4. politiques d’autorisation explicites ;
5. routage avancé et stratégies de résilience ;
6. automatisation et contrôle de dérive.

Ne passe pas simultanément toute l’application en mode strict. Un service qui appelle encore une destination non migrée peut être bloqué. Utilise un environnement de test et un plan de retour arrière avant de modifier des règles globales.

## 2. Routage par versions et déploiement progressif

Le routage par poids permet une migration canary : une petite portion du trafic arrive sur la nouvelle version, et la proportion peut évoluer selon les métriques. Les objets exacts dépendent de la solution et de l’API utilisée. Le principe opérationnel est de lier chaque progression à des critères de santé.

~~~text
Clients
  |
Route du mesh
  ├── 95 % -> service v1
  └──  5 % -> service v2 (canary)
          |
          +-- si erreurs/latence acceptables : augmenter progressivement
          +-- sinon : revenir à la distribution connue comme bonne
~~~

Choisis des métriques représentatives : taux d’erreur, latence p95/p99, saturation, résultats métier et dépendances. Une simple baisse de latence ne prouve pas que les réponses sont correctes. Les sessions collantes, les caches, les différences de schéma de données et les appels asynchrones peuvent compliquer une migration.

## 3. mTLS et modes de migration

Le chiffrement du transport et l’identité des workloads doivent être observables. Selon le mesh, il peut être possible de commencer par un mode permissif pour reconnaître les connexions non chiffrées, puis de durcir progressivement. Le mode permissif n’est pas le résultat de sécurité souhaité à long terme.

Avant la bascule :
- confirme les identités des workloads ;
- recense les flux légitimes ;
- vérifie les certificats, les expirations et la rotation ;
- vérifie les politiques de namespace et de workload ;
- teste les appels depuis et vers les services concernés ;
- garde des journaux et métriques d’échec TLS.

Ne confonds pas chiffrement et autorisation. Un client authentifié ne doit pas automatiquement pouvoir accéder à toutes les fonctions d’un serveur.

## 4. Autorisation par identité

Écris des politiques fondées sur des identités et des actions explicites. Le moindre privilège est plus fiable qu’une liste d’exceptions qui grandit au fil des incidents. Les règles d’autorisation doivent être versionnées et testées avec les identités réelles des workloads.

Un plan d’application réaliste :
1. observer les appels réels dans un environnement représentatif ;
2. définir une matrice source-destination ;
3. créer les règles minimales ;
4. tester les appels positifs et négatifs ;
5. surveiller les refus ;
6. déployer progressivement et garder une procédure de retour arrière.

Un test de refus est important : une politique n’est pas validée seulement parce qu’elle laisse passer le chemin attendu. Elle doit également démontrer que les flux non autorisés sont réellement bloqués.

## 5. Timeouts, retries, circuit breaking et saturation

Un timeout doit correspondre au budget de latence de bout en bout, et pas seulement à celui d’un proxy. Si chaque couche impose un délai trop long, la requête peut rester en attente plus longtemps que la limite de l’utilisateur. Des retries non bornés ou des reprises sur des opérations non idempotentes peuvent amplifier une panne.

Le circuit breaking et les limites de connexion cherchent à empêcher une surcharge de s’étendre. Ils ne créent pas de capacité supplémentaire. Définis des limites adaptées au profil de trafic, surveille les rejets et distingue une surcharge temporaire d’un défaut applicatif.

~~~text
Budget client : 2 s
  service A : 500 ms
  service B : 700 ms
  service C : 400 ms
  marge réseau et traitement : 400 ms

Les délais et retries des couches doivent rester cohérents avec ce budget.
~~~

Les valeurs ci-dessus illustrent une démarche de répartition du budget, pas des seuils universels à copier en production.

## 6. Observabilité du mesh

Mesure le taux de requêtes, le taux d’erreurs, la durée et la saturation. Examine les dimensions source, destination, version, réponse et statut TLS. Les noms des métriques varient selon la solution et les versions ; vérifie leur définition avant de créer des alertes.

Une explosion de cardinalité peut rendre la supervision coûteuse. Évite d’utiliser des identifiants uniques d’utilisateur ou de requête comme labels à haute cardinalité. Utilise les traces pour suivre un appel à travers plusieurs services et les journaux pour analyser un événement précis. Une corrélation cohérente entre les trois réduit le temps de diagnostic.

## 7. Méthode de diagnostic

Lors d’un échec :
1. confirme que le pod cible est prêt et que les endpoints sont corrects ;
2. vérifie la résolution de nom et la connectivité ;
3. examine les erreurs TLS et les identités ;
4. recherche un refus d’autorisation ;
5. inspecte la route, le poids de version et les timeouts ;
6. compare les métriques par version ;
7. vérifie la santé de l’application et de ses dépendances.

Évite d’appliquer immédiatement une règle globale permissive. Elle peut rétablir un appel en masquant le véritable défaut et en élargissant les accès. Utilise des tests ciblés et documente chaque changement.

## 8. TP guidé : canary et politique d’accès

**Situation :** un service catalogue existe en v1 et v2 ; seul frontend doit l’appeler et le mesh doit fournir une mesure claire du trafic.

1. Représente la route et les identités concernées.
2. Définis une distribution initiale prudente entre v1 et v2.
3. Choisis les métriques de succès et les critères d’arrêt.
4. Écris une politique qui autorise frontend et refuse un client de test non autorisé.
5. Prépare un scénario de timeout et un service temporairement indisponible.
6. Vérifie le comportement sur staging puis effectue une bascule progressive.
7. Simule une hausse d’erreurs et démontre le retour à la distribution précédente.

**Réussite :** le flux autorisé fonctionne, le flux interdit est bloqué, les erreurs sont visibles, les retries sont bornés et le changement peut être annulé rapidement.

## Exercices corrigés

**1. Pourquoi ne pas commencer par le mode d’autorisation le plus strict partout ?**  
Parce que les flux non cartographiés peuvent être bloqués. Il faut inventorier, observer, tester les flux autorisés et non autorisés, puis durcir par périmètre.

**2. Un canary à 5 % réussit. Peut-on immédiatement passer à 100 % ?**  
Pas sans vérifier des métriques et des critères représentatifs, notamment les erreurs, la latence, la saturation et la correction métier. Les effets liés au volume ou à la cohérence des données peuvent n’apparaître qu’à plus grande échelle.

**3. Pourquoi mTLS ne remplace-t-il pas les politiques d’autorisation ?**  
mTLS apporte un mécanisme d’identité et de protection du transport. Il ne définit pas automatiquement quelles opérations une identité est autorisée à effectuer.

**4. Pourquoi éviter les retries illimités ?**  
Ils peuvent multiplier la charge sur un service déjà en panne et prolonger la saturation. Les reprises doivent être limitées et compatibles avec l’idempotence.

## Défi final corrigé

Planifie la migration progressive d’une application de quatre services vers un mesh, avec chiffrement, autorisation minimale et routage canary.

**Correction attendue :** cartographie des flux ; activation d’observabilité ; tests TLS ; identité des workloads ; règles d’autorisation positives et négatives ; canary contrôlé par métriques ; limites de timeout/retry ; arrêt sur seuil d’erreur ; procédure de retour arrière ; documentation des politiques. La réussite se juge à la preuve de sécurité et de disponibilité, pas à la seule installation des composants.

## Synthèse

Un Service Mesh intermédiaire nécessite une migration graduelle, des politiques testées, une observabilité pertinente et des protections contre la surcharge. Le mesh doit rendre les échanges contrôlables sans substituer des règles complexes à la compréhension du réseau d’application.