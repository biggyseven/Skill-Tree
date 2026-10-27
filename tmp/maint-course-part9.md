## 12. Atelier pratique : petite infrastructure de laboratoire

### 12.1 Topologie

Utiliser un réseau de laboratoire réservé comprenant une machine de supervision, un serveur Linux, un serveur Web de test, un client et un commutateur administrable ou simulateur SNMP si disponible. Les adresses et comptes sont fictifs. N'exécute pas de scans sur des réseaux tiers et ne modifie pas un équipement de production pour réaliser ces exercices.

~~~mermaid
flowchart LR
  A[Poste apprenant] --> B[Switch de laboratoire]
  B --> C[Serveur Web test]
  B --> D[Serveur Linux test]
  B --> E[Routeur ou simulateur SNMP]
  B --> F[Nagios ou Zabbix]
  F --> C
  F --> D
  F --> E
~~~

### 12.2 Définir la matrice de contrôle avant de configurer

Pour chaque cible, noter le but, le signal, la fréquence, le résultat attendu et l'action en cas d'écart.

| Cible | Signal | Ce que le test prouve | Ce qu'il ne prouve pas |
|---|---|---|---|
| Routeur | ICMP | Réponse depuis le point de collecte | Santé de toutes les interfaces ou routage de bout en bout |
| Routeur | SNMP interface | Valeur exposée pour l'interface visée | Exactitude de tous les compteurs sans validation |
| Serveur Linux | Agent | Données système autorisées disponibles | Fonctionnement complet d'une application |
| Serveur Web | HTTP | Réponse au test configuré | Toutes les transactions métier |
| API | Requête fonctionnelle | Réponse conforme au contrat de test | Absence de tous les défauts possibles |

Cette matrice empêche de confondre un signal technique simple avec l'expérience de l'utilisateur. Elle rend aussi les seuils et résultats attendus vérifiables par un autre technicien.

### 12.3 Atelier Nagios

1. Vérifier la présence des plugins requis et lire leur aide.
2. Lancer les checks manuellement sur les cibles de laboratoire et consigner code de retour, sortie, durée et arguments.
3. Créer un hôte et un service avec des noms explicites et le modèle adapté à l'installation.
4. Définir intervalles, tentatives et options de notification selon le but du test.
5. Valider la configuration avant de la recharger.
6. Déclencher un échec contrôlé, par exemple en arrêtant le serveur Web de test ou en filtrant son port dans le laboratoire.
7. Observer l'état, les tentatives, la notification et la récupération.
8. Restaurer le service et vérifier que le check redevient nominal.

Ne coupe jamais un lien de production pour créer un scénario de panne. Le moyen de restauration doit être préparé avant de démarrer un test qui modifie l'état d'un système.

### 12.4 Atelier Zabbix

1. Créer un hôte avec un nom stable et l'interface adaptée.
2. Lier un template approprié au rôle, sans ajouter d'items inutiles.
3. Vérifier la configuration agent active/passive ou SNMP, y compris les règles de pare-feu.
4. Contrôler la fraîcheur des dernières valeurs et la cohérence des unités.
5. Créer ou utiliser un trigger avec un seuil et une persistance justifiés.
6. Configurer une action et un média ; valider la réception d'un test.
7. Simuler une panne contrôlée, observer l'événement puis vérifier la récupération.
8. Archiver les captures utiles, les résultats de tests et les limites de chaque mesure.

~~~mermaid
flowchart TD
  A[Créer un hôte pilote] --> B[Lier le template]
  B --> C[Contrôler valeurs fraîches]
  C --> D[Tester le trigger]
  D --> E[Tester action et média]
  E --> F[Simuler panne]
  F --> G[Valider récupération]
~~~

### 12.5 Étudier quatre pannes de base

- **Panne de service seul** : l'hôte répond, mais le port ou la transaction échoue. L'alerte doit cibler le service.
- **Perte de connectivité** : la cible devient inaccessible ; les contrôles dépendants peuvent générer plusieurs symptômes.
- **Perte de collecte** : l'agent ou le proxy est inaccessible alors que le service peut continuer de fonctionner.
- **Notification défaillante** : l'événement existe, mais le canal d'acheminement ne délivre rien.

Les quatre cas doivent aboutir à des diagnostics différents. Si un seul contrôle sert à les distinguer, le modèle de supervision est trop pauvre.

### 12.6 Livrable du laboratoire

Le rapport doit comporter la topologie, les versions, la liste des contrôles, les fréquences, les seuils, les résultats attendus, les tests de panne et de récupération, les preuves d'alerte et les actions restantes. Ne pas inclure les secrets SNMP, les mots de passe, les clés privées ou les tokens dans les captures diffusées. Pour chaque test, préciser ce qu'il prouve réellement et ce qui n'a pas été vérifié.

### 12.7 Critères d'acceptation

Le laboratoire est réussi lorsque les contrôles sont reproductibles, la cible et le service sont distingués, les données sont fraîches, les alertes ont le bon propriétaire, le canal de notification a été testé et le rétablissement est confirmé. L'apprenant doit pouvoir simuler une panne sans dégrader la production, revenir à l'état initial et expliquer pourquoi chaque alerte a été générée. Un écran vert seul n'est pas une preuve suffisante de validation.
