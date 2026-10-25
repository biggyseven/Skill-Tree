# Audit des contrats HTTP — Skill Tree

**Sources analysées :** le contenu partagé de `static/index.html` (environ 2 992 lignes) et de `app/api.py` (environ 1 089 lignes). Cet audit porte sur ces deux instantanés fournis; il ne signifie pas que le dépôt local a été modifié.

## Résumé

La majorité des appels UI possède une route correspondante. Les écarts qui bloquent des fonctionnalités sont surtout concentrés sur le quiz de cours, l'examen sur mesure et le rechargement de topologie. Une incohérence de payload empêche également les défis de topologie de récupérer leur topology attendue.

| Méthode | Appel de `static/index.html` | `app/api.py` fourni | Impact |
|---|---|---|---|
| GET | `/api/node/{node_id}/quiz` | **Absent**; seul `POST` existe | `startExercise()` essaie de lire `quiz.questions`; le chargement du quiz échoue (généralement HTTP 405). |
| POST | `/api/exam/build` | **Absent** | L'interface retombe sur `/api/exam/start`. Cette route de secours ne lit que `category`, prélève jusqu'à 20 questions et utilise la durée fixe; elle ne respecte donc pas le périmètre, le compte et la durée configurés. |
| POST | `/api/exam/submit` | **Absent** | La soumission serveur échoue. Comme les réponses sont volontairement absentes des questions reçues, la correction locale peut aussi être impossible. |
| GET | `/api/topology` | **Absent**; seul `POST` existe | L'interface sauvegarde au serveur, mais ne peut pas récupérer la dernière topologie enregistrée. |
| GET | `/api/node/{node_id}` — objet `challenge` | Route présente, mais le JSON retourné ne comprend que `prompt` et `time_limit` | Le code UI attend aussi `challenge.expected_topology`; `startChallenge()` rejette donc le défi faute de topologie attendue. |
| Résultat d'examen | L'UI utilise `PASS_SCORE = 70` et annonce « 70 % requis »; l'API fixe `EXAM_PASS_SCORE = 85` | Seuils divergents | Un score de 70–84 % est affiché comme non validé par l'API alors que l'interface le décrit comme suffisant. Le patch aligne la constante API sur la valeur UI. |
| GET | `/api/certificate` | Route présente, mais renvoie les octets littéraux `PDF EXEMPLE` | Le chemin HTTP existe, mais le résultat n'est pas un vrai PDF. Non modifié pour ne pas inventer la logique de génération de certificat. |
| GET | `/api/diagnostics/{diag_id}` | Route présente | Le scénario doit exister sous `content/diagnostics/{diag_id}.json`; son existence n'est pas vérifiable avec les deux fichiers partagés. |

## Routes qui correspondent

Les appels front-end repérés pour `/api/tree`, `/api/stats`, `/api/user-stats`, `/api/streak`, `/api/daily-plan`, `/api/flashcards`, `/api/node/{id}`, `/api/node/{id}/lesson`, `/api/node/{id}/submit-answer`, `/api/lab/start`, `/api/lab/exec`, `/api/lab/validate`, `/api/exam/start`, `/api/tutor`, `POST /api/topology`, `/api/shop`, `/api/shop/buy`, `/api/certificate`, `/api/trigger-update` et WebSocket `/api/ws` ont une route correspondante dans le fichier API partagé. Les formats JSON de ces chemins ne sont pas tous testables sans exécuter l'application et disposer de la base SQLite, des contenus et de la configuration réels.

## Décisions du correctif

1. **Ne pas réécrire `static/index.html`.** Ajouter les routes attendues au backend est le changement le moins intrusif : les appels front-end et les fonctions existantes sont conservés.
2. **Ne jamais envoyer les réponses avant la correction.** `GET /api/node/{node_id}/quiz` ne renvoie que l'énoncé, le type, l'identifiant et les choix.
3. **Faire l'examen sur mesure sur le périmètre de nœuds envoyé par le client.** Le backend contrôle les identifiants, borne le nombre de questions et la durée, et conserve l'association exacte nœud/question en JSON dans le champ `question_ids` déjà existant. Aucune colonne existante n'est modifiée.
4. **Corriger l'examen côté serveur.** La nouvelle table `exam_submissions` sert uniquement à conserver le résultat d'une session déjà soumise, éviter qu'un double clic donne deux corrections différentes et permettre une réponse idempotente. Elle est créée à la demande.
5. **Conserver les anciennes sessions si elles sont résolubles.** La soumission comprend le format existant (`question_ids` comme liste d'IDs) et le nouveau format explicite. Une ancienne session ambiguë est refusée proprement et doit être relancée.
6. **Unifier le seuil d'examen.** `EXAM_PASS_SCORE` est ajusté vers `PASS_SCORE` lu dynamiquement dans le HTML fourni (70 % dans cet instantané), au lieu de maintenir 85 % en contradiction avec l'interface.
7. **Mise à jour du profil sans réécrire la progression.** Les examens terminés sont conservés dans la nouvelle table `exam_submissions`; le champ `exams_passed` du profil additionne ces réussites au compteur historique `attempts` existant. La table `attempts` n'est pas modifiée.
8. **Rendre le défi utilisable.** Le champ `expected_topology` est inclus dans le payload de `/api/node/{node_id}` et décodé en JSON si la base le stocke sous forme de chaîne.
9. **Ajouter uniquement la lecture de la dernière topologie.** Le `POST` existant reste en place; la politique actuelle qui insère une nouvelle ligne à chaque sauvegarde n'est pas changée, faute de schéma complet de la table. La lecture départage deux sauvegardes ayant le même horodatage à la seconde avec `rowid`.

## Contrôles effectués sur le paquet

- Compilation syntaxique des fichiers du patch avec `py_compile`.
- Cinq tests automatisés du script de patch : application sur un fixture contrôlé, syntaxe Python après patch, compatibilité LF/CRLF, absence de double application et vérification que le mode simulation ne modifie rien.
- Le script de patch vérifie ses ancres avant toute écriture, valide le résultat avec `ast.parse`, exige la présence des routes ajoutées, crée une sauvegarde de `app/api.py` et `static/index.html`, puis revalide après écriture. Si la validation post-écriture échoue, il restaure `app/api.py`.

**Important :** les tests utilisent un fixture représentatif pour éprouver le mécanisme de modification. Le vrai projet local, sa base SQLite et ses contenus n'étaient pas fournis comme checkout exécutable; un test HTTP d'intégration sur ce projet n'a donc pas été exécuté ici.
