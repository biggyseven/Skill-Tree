# Utiliser PostgreSQL gratuit (Neon) avec Skill-Tree

Skill-Tree garde SQLite comme base locale par défaut. Sur Render, le système de fichiers d'un service Free n'est pas persistant, donc la progression ne doit pas rester dans `skilltree.db` pour un usage durable.

La migration utilise une base PostgreSQL avec `DATABASE_URL`. Le plan Neon Free est à 0 $ et, au moment de la rédaction (26 octobre 2026), inclut 1 Go de stockage par projet, 100 CU-heures de calcul par mois et 5 Go de transfert réseau public. Le calcul se met en veille après cinq minutes d'inactivité. Si le quota mensuel est atteint, le calcul peut être suspendu jusqu'à sa réinitialisation; les données restent stockées. Vérifier les limites courantes avant utilisation :
- Plans et quotas Neon : https://neon.com/docs/introduction/plans
- Quotas du plan gratuit : https://neon.com/docs/introduction/free-tier

## Ce que fait le code

- Si `DATABASE_URL` est absent, l'application continue d'utiliser SQLite localement.
- Si `DATABASE_URL` contient une URL PostgreSQL, les modules de l'application utilisent psycopg et le backend PostgreSQL.
- Au premier démarrage de la base Neon vide, le schéma est créé puis `content/nodes.json` et les fichiers de contenu versionnés alimentent le parcours.
- Les tables de progression et les tentatives sont ensuite conservées dans PostgreSQL au lieu du système de fichiers éphémère de Render.
- Le code de transition ne supprime ni ne réinitialise le fichier SQLite local.
- Le mot de passe PostgreSQL reste dans les variables secrètes Render; il ne doit jamais être commité dans GitHub ni envoyé dans un message.

## Activation sans terminal

### 1. Créer le projet Neon gratuit

1. Ouvrir https://console.neon.tech/ et créer un compte/projet sur le plan Free.
2. Choisir si possible une région européenne proche de Render (Render est actuellement hébergé à Francfort).
3. Dans **Connect**, sélectionner la base, puis copier la chaîne de connexion. Activer **Pooled connection** dans l'interface de Neon afin d'utiliser l'endpoint de pool.
4. Garder cette chaîne privée. Ne pas la coller dans GitHub, un ticket, ou cette conversation.

### 2. Ajouter le secret sur Render

1. Ouvrir la configuration du service Skill-Tree : https://dashboard.render.com/web/srv-dbf4kbu7bikc73c5qdr0/env
2. Ajouter une variable d'environnement nommée exactement `DATABASE_URL`.
3. Coller la chaîne PostgreSQL de Neon comme valeur et enregistrer.
4. Render redémarrera le service. Le premier démarrage créera les tables et rechargera le contenu pédagogique versionné.

Ne pas définir `SKILLTREE_DB` vers un ancien fichier local en pensant le rendre persistant : le code PostgreSQL s'active avec `DATABASE_URL`.

## À propos des anciennes données

Le diagnostic de production fourni le 26 octobre 2026 a signalé 0 tentative dans `attempts` et 0 dans `lab_attempts`. Il ne permet pas de récupérer d'éventuelles données auparavant perdues lorsque le service utilisait un stockage éphémère. Le changement vers Neon rend les nouvelles écritures persistantes; il ne peut pas reconstituer des tentatives déjà absentes.

Avant de saisir `DATABASE_URL` en production, la branche doit passer les tests et être intégrée dans `feature/lab-workspace`. Une fois le secret ajouté, vérifier immédiatement la page de diagnostic du Lab Workspace et effectuer un test non sensible : démarrer un cours et confirmer que sa progression survit à un redémarrage du service.

## Limites gratuites à prendre en compte

Neon Free n'est pas une garantie d'uptime ni un service illimité. Le projet a une limite de stockage, de temps de calcul et de transfert; le compute se met en veille et peut se suspendre si les quotas sont consommés. C'est néanmoins un stockage PostgreSQL persistant sans abonnement mensuel obligatoire, contrairement à un disque persistant Render ou à l'offre Render Postgres gratuite qui expire après 30 jours.