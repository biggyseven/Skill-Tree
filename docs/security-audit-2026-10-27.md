# Audit de sécurité Skill-Tree — 27 octobre 2026

## Périmètre et limite

Analyse statique du code de `feature/lab-workspace`, des workflows GitHub Actions et des métadonnées Render disponibles en lecture seule. Le service Render de production pointe sur cette branche et déploie automatiquement les commits qui y arrivent. Les tests HTTP externes directs n'ont pas pu être réalisés depuis l'environnement d'audit : ce document ne constitue donc pas un test d'intrusion ni une certification de sécurité.

## Corrections incluses dans la PR de base

- **CORS :** suppression de l'origine universelle et des identifiants CORS. La liste `SKILLTREE_CORS_ORIGINS` est vide par défaut (l'interface hébergée sur la même origine continue de fonctionner), n'accepte que des origines HTTP(S) explicites et ne prend pas en charge `*`. Les méthodes et en-têtes CORS sont limités.
- **En-têtes HTTP :** ajout de `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` et `Permissions-Policy`. La CSP n'est pas imposée dans cette PR : l'interface actuelle repose sur des scripts inline et une politique trop stricte pourrait casser le site. Une CSP avec nonces ou hashes doit être planifiée séparément.
- **GitHub Actions :** les vérifications Python et frontend des PR utilisent maintenant un jeton en lecture seule. La publication du bundle statique est déplacée dans un workflow distinct déclenché uniquement par un push sur `feature/lab-workspace`; le droit d'écriture est limité au job de publication.
- **Ancien moteur Docker :** les trois endpoints legacy qui démarrent/exécutent/valident un shell de laboratoire renvoient désormais 503 tant que `SKILLTREE_ENABLE_LEGACY_DOCKER_LABS` n'est pas explicitement activé. L'option est documentée comme réservée aux environnements de confiance.
- **Dépendances :** ajout d'un audit automatisé avec `pip-audit` et de mises à jour Dependabot hebdomadaires pour Python et GitHub Actions.
- **Authentification propriétaire unique :** une PR empilée ajoute une page de connexion et un cookie de session signé qui verrouillent les pages et routes `/api/*` sur Render. Elle reste distincte de cette PR de base et doit être fusionnée après configuration des deux secrets Render. Cette mesure ne crée pas encore de comptes séparés ni d'isolation multi-utilisateur ; voir `docs/site-authentication.md`.
- **Fichiers de base de données :** les copies SQLite de test/sauvegarde ne doivent pas faire partie du dépôt public. Cette PR les retire de l'arbre courant et renforce `.gitignore`. Cette suppression ne les efface pas des commits historiques.

## Constats nécessitant un chantier dédié

### Élevé — aucune isolation d'identité pour les données de progression

La plupart des routes d'écriture et de lecture ne portent pas d'identité utilisateur authentifiée. Les topologies sauvegardées, tentatives, séries, récompenses et statistiques peuvent donc être partagées dans le stockage applicatif au lieu d'être rattachées à un propriétaire. CORS n'est pas un mécanisme d'authentification et ne règle pas ce problème.

**Suite recommandée :** choisir un vrai mécanisme de connexion/identité, puis rattacher chaque session d'examen, tentative, topologie, inventaire et profil à l'identifiant utilisateur côté serveur. Ajouter des tests d'accès croisé entre deux utilisateurs avant de rendre le parcours multi-utilisateur fiable.

### Élevé si le moteur legacy est explicitement activé — endpoints de shell Docker

Cette PR désactive par défaut les routes `/api/lab/start`, `/api/lab/exec` et `/api/lab/validate` ; chacune refuse la requête avant de lancer le runner tant que `SKILLTREE_ENABLE_LEGACY_DOCKER_LABS` n'est pas explicitement activé. Si cette option est activée, le code historique peut encore démarrer un conteneur en mode `--privileged` et exécuter une commande fournie par le client. Sur un hôte disposant d'un démon Docker accessible, cela reste un risque important d'abus de ressources et d'escalade vers l'hôte.

**Suite recommandée :** ne pas activer l'option sur un site public ; pour les usages locaux de confiance, supprimer `--privileged` au profit de capacités minimales, plafonner les sessions et tester les scénarios réseau avant de réactiver ce moteur. La disponibilité de Docker sur le service Render actuel n'est pas prouvée par le code seul.

### Élevé — absence de limite de débit sur les fonctionnalités coûteuses

Le tuteur IA (`/api/tutor`) et la synthèse vocale (`/api/tts`) déclenchent des appels externes et n'ont pas de limitation de débit visible dans le code audité. Ils peuvent être abusés pour provoquer des coûts, saturer les quotas ou dégrader la disponibilité.

**Suite recommandée :** ajouter des limites côté serveur (par adresse et, après mise en place de l'identité, par utilisateur), des plafonds de concurrence et une gestion des quotas.

### Moyen — rendu de contenu HTML

Le lecteur transforme le Markdown de cours en HTML via `marked.parse`, puis l'insère dans le DOM. Le contenu actuel est chargé depuis les ressources du dépôt, mais tout contenu non fiable introduit à l'avenir doit être assaini avec une liste blanche de balises/attributs et des tests XSS avant affichage.

### Moyen — dépendances non verrouillées

`requirements.txt` fixe principalement des versions minimales. Les mises à jour de dépendances et l'audit automatisé réduisent le risque, mais la version réellement installée peut varier d'un build à l'autre. Il faut enregistrer et auditer les versions résolues à chaque release ou introduire un lockfile compatible avec le mode de déploiement.

## À faire avant de déclarer l'application sécurisée

1. Décider et implémenter l'identité utilisateur et les contrôles d'accès par ressource.
2. Neutraliser ou sécuriser les endpoints Docker historiques et tester leur isolation.
3. Ajouter des limites de débit pour les endpoints qui déclenchent des appels externes.
4. Vérifier si les fichiers SQLite supprimés contenaient des données personnelles ou de production. S'ils en contenaient, une suppression de l'arbre courant ne suffit pas : il faut évaluer un nettoyage contrôlé de l'historique Git et la rotation de tout secret éventuellement exposé.
5. Compléter par des tests HTTP en environnement de validation pour les en-têtes, CORS, les méthodes inattendues, les erreurs et les chemins d'accès.
