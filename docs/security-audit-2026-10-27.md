# Audit de sécurité Skill-Tree — 27 octobre 2026

## Périmètre et limite

Analyse statique du code de `feature/lab-workspace`, des workflows GitHub Actions et des métadonnées Render disponibles en lecture seule. Le service Render de production pointe sur cette branche et déploie automatiquement les commits qui y arrivent. Les tests HTTP externes directs n'ont pas pu être réalisés depuis l'environnement d'audit : ce document ne constitue donc pas un test d'intrusion ni une certification de sécurité.

## Corrections incluses dans cette PR

- **CORS :** suppression de l'origine universelle et des identifiants CORS. La liste `SKILLTREE_CORS_ORIGINS` est vide par défaut (l'interface hébergée sur la même origine continue de fonctionner), n'accepte que des origines HTTP(S) explicites et ne prend pas en charge `*`. Les méthodes et en-têtes CORS sont limités.
- **En-têtes HTTP :** ajout de `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` et `Permissions-Policy`. La CSP n'est pas imposée dans cette PR : l'interface actuelle repose sur des scripts inline et une politique trop stricte pourrait casser le site. Une CSP avec nonces ou hashes doit être planifiée séparément.
- **GitHub Actions :** les vérifications Python et frontend des PR utilisent maintenant un jeton en lecture seule. La publication du bundle statique est déplacée dans un workflow distinct déclenché uniquement par un push sur `feature/lab-workspace`; le droit d'écriture est limité au job de publication.
- **Dépendances :** ajout d'un audit automatisé avec `pip-audit` et de mises à jour Dependabot hebdomadaires pour Python et GitHub Actions.
- **Fichiers de base de données :** les copies SQLite de test/sauvegarde ne doivent pas faire partie du dépôt public. Cette PR les retire de l'arbre courant et renforce `.gitignore`. Cette suppression ne les efface pas des commits historiques.

## Constats nécessitant un chantier dédié

### Élevé — aucune isolation d'identité pour les données de progression

La plupart des routes d'écriture et de lecture ne portent pas d'identité utilisateur authentifiée. Les topologies sauvegardées, tentatives, séries, récompenses et statistiques peuvent donc être partagées dans le stockage applicatif au lieu d'être rattachées à un propriétaire. CORS n'est pas un mécanisme d'authentification et ne règle pas ce problème.

**Suite recommandée :** choisir un vrai mécanisme de connexion/identité, puis rattacher chaque session d'examen, tentative, topologie, inventaire et profil à l'identifiant utilisateur côté serveur. Ajouter des tests d'accès croisé entre deux utilisateurs avant de rendre le parcours multi-utilisateur fiable.

### Élevé si le runtime dispose de Docker — anciens endpoints de shell de laboratoire

Les routes historiques `/api/lab/start`, `/api/lab/exec` et `/api/lab/validate` n'ont pas de dépendance d'authentification. Le runner peut démarrer un conteneur en mode `--privileged` et exécuter une commande fournie par le client dans ce conteneur. Si un déploiement dispose d'un démon Docker accessible, cela expose un risque important d'abus de ressources et d'escalade vers l'hôte.

**Suite recommandée :** désactiver les routes legacy sur les déploiements publics ou les protéger par une authentification serveur, plafonner le nombre de sessions et leur durée, supprimer `--privileged` au profit de capacités minimales, et tester les scénarios réseau avant déploiement. Le code seul ne prouve pas que Docker est disponible sur le service Render actuel.

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
