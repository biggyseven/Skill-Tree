# Supervision réseau (Nagios, Zabbix)

> **Mise en contexte** — Un réseau d'entreprise comprend routeurs, commutateurs, pare-feu, liens opérateur, DNS, systèmes d'authentification, serveurs, API et applications métiers. Une panne peut venir d'un composant, d'une dépendance, d'une saturation lente, d'un certificat expiré ou de la collecte qui ne reçoit plus les données. La supervision doit permettre de distinguer ces situations et d'agir avant que les utilisateurs ne découvrent le problème.

> **Idée directrice** — Une bonne supervision ne cherche pas à afficher le plus de voyants verts. Elle collecte les bons signaux, explique ce qu'ils prouvent, détecte les anomalies significatives, limite les fausses alertes, protège les accès de gestion et conserve les traces nécessaires à la reconstruction d'un incident. Nagios Core et Zabbix peuvent servir ces objectifs, mais reposent sur des modèles différents.

## 1. Objectifs pédagogiques

Tu dois pouvoir concevoir un pilote avec Nagios et Zabbix, créer des contrôles cohérents, comprendre pourquoi une alerte apparaît et expliquer les résultats à une équipe technique. Cela demande de distinguer hôte, service, item, métrique, trigger, événement, état et notification ; comprendre les plugins et codes de retour Nagios ; expliquer la logique SOFT/HARD et les dépendances ; décrire les composants Zabbix, ses agents, proxys, templates, items, triggers et actions ; distinguer collecte active, passive, SNMP, traps et contrôles applicatifs ; définir des seuils adaptés ; sécuriser les flux et diagnostiquer une collecte manquante.

Les exemples sont illustratifs : chemins, options, noms de services et clés d'items varient selon la version et la distribution. Toute configuration de production doit être adaptée, testée en laboratoire et révisée avant application.

## 2. Ce que l'on mesure

### 2.1 Hôte, service, métrique et événement

Un **hôte** est un élément supervisé : routeur, commutateur, serveur, VM, imprimante, point d'accès ou système applicatif. Un hôte est un objet logique et ne doit pas forcément correspondre à une machine physique.

Un **service Nagios** représente une vérification associée à un hôte. Le terme peut désigner HTTP, DNS, espace disque, latence, état d'interface ou nombre de connexions. Dans Zabbix, un **item** collecte ou reçoit une valeur, tandis qu'un **trigger** évalue une expression pour décider si un problème doit être signalé.

Une **métrique** doit être définie avec une unité, une cible, un intervalle et une méthode de collecte : latence en millisecondes, perte en pourcentage, débit en bits par seconde, mémoire disponible en octets ou âge du dernier point de sauvegarde. Un **événement** représente une occurrence significative ; une **notification** transmet une information à une personne ou à un autre système. Toutes les valeurs ne doivent pas déclencher des notifications.

~~~mermaid
flowchart LR
  A[Équipement] --> B[Mesure]
  B --> C[Évaluation]
  C --> D{Anomalie significative ?}
  D -->|Non| E[Historique]
  D -->|Oui| F[Événement]
  F --> G[Priorisation]
  G --> H[Notification]
~~~

### 2.2 Pourquoi le ping ne suffit pas

ICMP Echo vérifie si une cible répond à une requête réseau. Il ne prouve pas que l'application fonctionne. Un serveur Web peut répondre au ping mais avoir son processus HTTP arrêté ; une API peut accepter TCP et renvoyer une erreur de base de données ; un hôte peut bloquer ICMP tout en servant correctement HTTPS.

Pour un service Web important, combiner selon le besoin réponse ICMP, port TCP, code HTTP, contenu attendu, validité TLS et test d'une transaction. Pour un commutateur, surveiller l'accès de gestion, les états des interfaces, les erreurs, les discards, les débits, la température et les alimentations lorsque les données existent.

~~~mermaid
flowchart TD
  A[Serveur Web] --> B[ICMP]
  A --> C[TCP]
  A --> D[HTTP]
  A --> E[TLS]
  A --> F[Transaction métier]
  B --> G[Diagnostic]
  C --> G
  D --> G
  E --> G
  F --> G
~~~

Le point de mesure compte également : un test du poste d'un technicien ne traverse pas nécessairement les mêmes routes, ACL ou pare-feu que le serveur de supervision. Pour diagnostiquer la collecte, reproduire le check depuis le bon endroit.

### 2.3 Zéro et absence de donnée

Zéro peut être valide : aucune erreur mesurée, aucune perte ou aucun utilisateur actif. L'absence de valeur peut provenir d'un agent arrêté, d'un pare-feu, d'un problème SNMP, d'un proxy hors ligne ou d'un délai de traitement. Ne transforme jamais silencieusement une valeur absente en zéro : tu pourrais afficher un système comme sain alors qu'il n'est plus observé.

### 2.4 Pull et push

En collecte interrogée (pull ou polling), le serveur ou le proxy contacte la cible. Dans une collecte émise (push), l'agent ou un collecteur initie la connexion et transmet les résultats ; les checks actifs Zabbix utilisent ce modèle. Nagios peut aussi recevoir des résultats passifs.

~~~mermaid
flowchart LR
  A[Serveur] -->|Requête| B[Cible]
  B -->|Réponse| A
  C[Collecteur distant] -->|Résultat envoyé| D[Récepteur]
  D --> E[Évaluation]
~~~

Le choix dépend des routes, du pare-feu, du volume de collecte, de l'autonomie en cas de coupure et du modèle de sécurité. Tout déploiement hybride doit documenter ses flux.
