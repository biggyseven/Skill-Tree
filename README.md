# Correctif de compatibilité API — Skill Tree

Ce paquet contient un correctif **additif** pour aligner `app/api.py` avec les appels observés dans `static/index.html`. Il ne remplace pas le fichier API complet et ne modifie pas l'interface HTML.

## Écarts constatés dans les fichiers fournis

| Appel front-end | État dans `app/api.py` fourni | Conséquence |
|---|---|---|
| `GET /api/node/{node_id}/quiz` | Route absente; seul le `POST` existe | `startExercise()` reçoit typiquement HTTP 405 et ne peut pas charger les questions. |
| `POST /api/exam/build` | Route absente | L'interface bascule sur `/api/exam/start`; le périmètre des nœuds, le nombre de questions et la durée personnalisée ne sont pas respectés par l'ancien endpoint. |
| `POST /api/exam/submit` | Route absente | La correction serveur ne fonctionne pas; la correction locale ne peut pas calculer le score si les réponses ne sont pas incluses dans les questions renvoyées par l'API. |
| `GET /api/topology` | Route absente; seul le `POST` existe | La sauvegarde peut fonctionner, mais le chargement depuis le serveur ne fonctionne pas. |
| `GET /api/certificate` | Route présente, corps `PDF EXEMPLE` | L'URL répond, mais le contenu n'est pas un vrai PDF de certificat. Ce point est volontairement laissé intact dans ce patch. |
| `GET /api/diagnostics/{diag_id}` | Route présente | Le scénario `network_down.json` doit exister dans `content/diagnostics/`, sinon la route renvoie 404. |

Le correctif n'altère pas les parcours de cours/labs existants et n'ajoute pas de scripts côté client. Les appels `/api/tree`, `/api/stats`, `/api/user-stats`, `/api/streak`, `/api/daily-plan`, `/api/flashcards`, `/api/node/{id}`, `/api/node/{id}/lesson`, `/api/node/{id}/submit-answer`, `/api/lab/*`, `/api/tutor`, `/api/shop`, `/api/shop/buy`, le `POST /api/topology`, `/api/certificate`, `/api/trigger-update` et WebSocket `/api/ws` ont des routes correspondantes dans le fichier API partagé.

## Ce que le correctif ajoute

- `GET /api/node/{node_id}/quiz` : renvoie `id`, `type`, `prompt`, `choices`; **ne révèle pas les réponses avant soumission**.
- Payload `GET /api/node/{node_id}` : inclut la propriété `challenge.expected_topology` (décodée en JSON), nécessaire à `startChallenge()` dans Drawflow.
- Seuil d'examen : aligne `EXAM_PASS_SCORE` sur `PASS_SCORE` lu dans `static/index.html` (70 % dans les fichiers fournis), afin que le résultat serveur corresponde au message affiché.
- `POST /api/exam/build` : prend en charge `module`, `levels`, `count`, `node_ids` et `time_limit`, comme l'interface les envoie.
- `POST /api/exam/submit` : vérifie la session, note les réponses côté serveur, renvoie `score`, `passed`, `correct`, `total` et `details`; la soumission est idempotente via une petite table SQLite ajoutée sans modification des tables existantes. Le compteur `exams_passed` du profil ajoute les réussites enregistrées par cette route.
- `GET /api/topology` : renvoie la dernière topologie sauvegardée au format JSON utilisé par Drawflow.
- Les sessions d'examen démarrées par l'ancien endpoint stockent de manière non destructive une référence explicite `{node_id, question_id}`. Le nouveau `submit` comprend aussi l'ancien format des sessions précédentes lorsqu'il peut identifier chaque question sans ambiguïté.

`static/index.html` n'est pas modifié : le correctif répare l'API sous les contrats déjà utilisés par l'interface. Les résultats de ces sessions sont enregistrés dans `exam_submissions` et pris en compte par `exams_passed` dans le profil, sans inventer de colonnes dans `attempts`. L'historique détaillé visible de l'interface reste stocké côté navigateur.

## Application sûre

1. Place `apply_api_compat_patch.py` où tu veux, sans déplacer tes fichiers du projet.
2. Depuis Windows PowerShell ou un terminal, lance d'abord une simulation :

   ```powershell
   python .\apply_api_compat_patch.py --project-root "C:\chemin\vers\Skill-Tree"
   ```

3. Vérifie le résultat et garde un commit ou une copie de sécurité si tu en utilises déjà.
4. Applique ensuite :

   ```powershell
   python .\apply_api_compat_patch.py --project-root "C:\chemin\vers\Skill-Tree" --apply
   ```

Le mode simulation est le comportement par défaut. Le mode `--apply` crée avant l'écriture une sauvegarde horodatée des deux fichiers (`app/api.py` et `static/index.html`) sous `backups/api-compat-YYYYMMDD-HHMMSS/`; seul `app/api.py` est modifié. L'écriture du fichier API est atomique, vérifie la syntaxe avec `ast.parse`, vérifie les routes attendues et restaure automatiquement la sauvegarde de `app/api.py` si une vérification après écriture échoue.

## Vérifications après application

Depuis la racine du projet :

```powershell
python -m py_compile .\app\api.py
```

Puis démarre l'application comme d'habitude et vérifie :

- `GET http://127.0.0.1:8000/api/node/ID_D_UN_COURS/quiz` (200 pour un cours accessible avec quiz, 409 si verrouillé, 404 sans quiz)
- `POST http://127.0.0.1:8000/api/exam/build` avec le JSON `{ "module": "admin-reseaux", "levels": ["debutant"], "count": 10, "node_ids": ["ID_D_UN_COURS"], "time_limit": 900 }` (le nœud doit contenir des questions)
- Soumettre ensuite `POST /api/exam/submit` avec `{ "session_id": "ID_RETOURNE", "answers": [null, ...] }` (le nombre d'éléments doit égaler le nombre de questions retournées)
- Sauvegarder une topologie depuis l'interface, recharger la page, puis appeler `GET /api/topology`; le JSON doit inclure `drawflow` si une topologie a été sauvegardée.

Remplace les exemples `ID_D_UN_COURS` par un ID réel retourné par `/api/tree`. Ne colle pas une clé API, un mot de passe ou des captures réseau contenant des données sensibles dans un ticket de diagnostic.

## Limites et précautions

- Le paquet s'applique uniquement si les ancres des versions fournies existent exactement dans le véritable `app/api.py`. Sinon il refuse de modifier les fichiers et demande une adaptation manuelle; il n'écrase pas silencieusement un code divergent.
- `GET /api/topology` renvoie la sauvegarde la plus récente, alors que le `POST` actuel continue à ajouter une nouvelle ligne comme auparavant. Une migration en upsert est laissée de côté pour éviter de supposer une contrainte ou un identifiant de table non fourni.
- L'endpoint certificat est repéré mais pas retouché, car son remplacement nécessite la logique et les dépendances de génération de certificat du projet.
