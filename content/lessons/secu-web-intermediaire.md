# Sécurité Web de base

## Introduction

Une application Web reçoit des données non fiables depuis navigateurs, API et systèmes tiers. Une validation insuffisante ou un contrôle d’accès mal placé peut entraîner une injection, une fuite de données ou une action non autorisée ; la sécurité doit être intégrée au développement.

Les risques courants comprennent l’injection SQL, les scripts intersites (XSS), la falsification de requêtes intersites (CSRF), les sessions fragiles et les permissions vérifiées seulement dans l’interface. Requêtes paramétrées, encodage contextuel, protection CSRF et contrôle côté serveur réduisent ces risques.

La production nécessite aussi TLS moderne, cookies de session adaptés, en-têtes de sécurité, gestion sûre des secrets et journaux ne divulguant pas d’informations sensibles. Les tests doivent inclure des entrées invalides et des tentatives d’accès non autorisées.

## Concepts clés

- **Injection SQL** : utiliser des requêtes paramétrées.
- **XSS** : encoder la sortie selon son contexte.
- **CSRF** : protéger les actions sensibles basées sur la session.
- **Autorisation** : vérifier les permissions côté serveur pour chaque opération.
- **Sessions / TLS** : HTTPS, cookies adaptés et secrets protégés.

## Méthode pratique

1. Identifie les entrées non fiables et les frontières de confiance.
2. Paramètre les requêtes et encode la sortie.
3. Teste les permissions avec plusieurs identités.
4. Vérifie TLS, cookies, en-têtes et absence de secrets dans le dépôt.
5. Ajoute des tests de sécurité au pipeline d’intégration.

## À retenir

La sécurité Web combine validation, encodage, autorisation, sessions sûres et tests continus.
