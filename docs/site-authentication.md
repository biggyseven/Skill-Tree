# Authentification privée de Skill-Tree

## Ce que couvre cette étape

Cette première protection transforme le site actuel en application privée à propriétaire unique. Elle n'ajoute pas de comptes distincts et ne constitue donc pas encore une isolation multi-utilisateur. Les tables de progression historiques restent partagées, sous l'hypothèse qu'un seul propriétaire utilise le site. Ne communique pas le même mot de passe à d'autres apprenants.

Sur Render, l'authentification est activée automatiquement. Si les secrets ne sont pas configurés, les pages de l'application redirigent vers la connexion et les routes de données répondent avec une erreur explicite au lieu de rester ouvertes.

## Configuration de Render — à faire avant de fusionner cette PR

1. Dans un terminal à la racine du dépôt, exécute `python scripts/generate_auth_password_hash.py`. Saisis un mot de passe long (12 caractères minimum) ; le script ne l'écrit pas en clair et affiche son hash PBKDF2.
2. Génére un secret de session avec `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Dans le tableau de bord Render, ouvre le service **Skill-Tree**, puis **Environment**. Ajoute `SKILLTREE_AUTH_PASSWORD_HASH` avec le hash généré et `SKILLTREE_AUTH_SECRET` avec le secret aléatoire. Ne colle jamais ces valeurs dans Git, une issue ou un message public.
4. Enregistre les variables et confirme qu'elles sont disponibles sur le service avant de fusionner/déployer la PR. Le site public est fail-closed : sans ces deux valeurs, la connexion ne peut pas réussir et l'API de données reste indisponible.
5. Après le déploiement, ouvre le site, connecte-toi, recharge le tableau de bord et vérifie **Déconnexion**. Ferme la session après vérification.

Pour une installation locale, les variables peuvent être définies dans un fichier `.env` ignoré par Git. L'authentification s'active si `SKILLTREE_REQUIRE_AUTH=true` ou si l'une des variables d'authentification est renseignée. Sur Render, `RENDER_SERVICE_ID` active la protection même si la configuration est incomplète.

## Comportement technique

- Mot de passe : hash PBKDF2-HMAC-SHA256, 600 000 itérations et sel aléatoire.
- Session : jeton signé HMAC-SHA256, expiration absolue après 12 heures, cookie `HttpOnly`, `SameSite=Strict`, `Secure` sur Render.
- Échec de configuration : fermé par défaut sur Render ; aucune clé ou mot de passe de secours n'est intégré au code.
- Tentatives de connexion : cinq échecs dans une fenêtre de quinze minutes bloquent la nouvelle tentative depuis la même adresse pour la fenêtre en cours. Ce compteur est en mémoire du processus ; ce n'est pas une protection distribuée contre une attaque venant de plusieurs adresses.
- CSRF : vérification de l'en-tête `Origin` pour les mutations authentifiées quand il est fourni, plus cookie SameSite strict. Les WebSockets vérifient aussi l'origine et la session.
- API : les routes `/api/*` sont privées, sauf les trois routes de gestion de session et les documents de schéma OpenAPI/Swagger. `/login.html` reste public pour permettre la connexion.
- Frontend : une session expirée provoque une redirection vers la connexion ; un bouton explicite permet de se déconnecter.

## Limites et prochaine étape

C'est une barrière d'accès unique, pas un système d'identités multi-utilisateur. Les progrès, tentatives et inventaires restent stockés selon le schéma historique partagé. Avant d'ouvrir Skill-Tree à plusieurs apprenants, il faut créer un modèle `users`, attribuer un propriétaire aux sessions et ressources, migrer les données existantes et ajouter des tests d'accès croisé entre deux comptes. La limitation de débit devra également être stockée dans un service partagé et les routes coûteuses du tuteur IA/TTS doivent avoir leurs propres quotas.

Ne déploie pas cette étape sans avoir d'abord configuré les deux secrets d'environnement dans Render.