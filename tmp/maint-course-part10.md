## 13. Exercices avec corrigés détaillés

### Exercice 1 — Le ping est vert mais le site est inaccessible

**Situation.** Nagios indique que le serveur Web répond au ping ; les utilisateurs reçoivent une erreur HTTP.

**Corrigé.** Tester le port TCP, le code HTTP, le contenu attendu, le certificat TLS, le DNS et les dépendances applicatives depuis un point de collecte autorisé. Lire les journaux Web et applicatifs selon les permissions. Le ping démontre seulement la réponse au test ICMP ; il ne prouve pas que la transaction métier fonctionne.

### Exercice 2 — Un plugin retourne UNKNOWN

**Situation.** Un check affiche UNKNOWN et parle d'une erreur de résolution DNS.

**Corrigé.** Vérifier les arguments du plugin, reproduire la résolution depuis le serveur Nagios, examiner la configuration DNS, les droits et le réseau utilisé. UNKNOWN signifie que le plugin n'a pas produit un statut fiable ; le service peut être sain ou non. Réaliser un test indépendant avant de conclure.

### Exercice 3 — Zabbix collecte les données mais n'ouvre aucun problème

**Situation.** Les valeurs CPU sont visibles ; le dépassement prévu n'entraîne pas d'événement.

**Corrigé.** Vérifier le nom de l'hôte dans l'expression, la clé réelle de l'item, le type et l'unité, la fenêtre temporelle, l'historique requis et les conditions de récupération. Confirmer que les données dépassent réellement la condition exprimée. Une valeur présente ne garantit pas que le trigger examine la bonne valeur.

### Exercice 4 — Un événement existe mais aucun courriel n'arrive

**Corrigé.** Contrôler les conditions et opérations de l'action, le média de l'utilisateur, son adresse, les horaires, la sévérité, les règles de répétition et les logs du canal d'envoi. Tester le média par le mécanisme prévu. Ne pas changer le trigger si le problème se trouve dans l'acheminement.

### Exercice 5 — Une interface semble utiliser 115 % de sa capacité

**Corrigé.** Vérifier le type de compteur, le débit nominal configuré, l'unité, la durée entre échantillons, le redémarrage de l'équipement et le débordement d'un compteur. Calculer la différence sur une durée valide puis comparer à une autre mesure. Ne pas déclarer une saturation tant que la formule et le compteur n'ont pas été vérifiés.

### Exercice 6 — Cent alertes arrivent en même temps

**Corrigé.** Aligner les événements dans le temps, vérifier le périmètre du site, inspecter la passerelle et les dépendances communes. Déterminer s'il existe un incident parent qui explique une partie des symptômes. Ne pas supprimer toutes les alertes : une panne indépendante peut se produire en parallèle. Les dépendances doivent réduire le bruit tout en conservant l'information utile au diagnostic.

### Exercice 7 — L'agent Zabbix ne transmet plus après une règle de pare-feu

**Corrigé.** Identifier le mode de collecte. Pour un check passif, vérifier le chemin serveur/proxy vers l'agent et le filtrage TCP 10050. Pour un check actif, vérifier la connexion sortante de l'agent vers le serveur/proxy et le port généralement 10051. Vérifier aussi les paramètres Server, ServerActive, Hostname, le chiffrement, les routes et les logs. Ne pas ouvrir le port à toutes les sources.

### Exercice 8 — Une alerte CPU survient chaque nuit pendant une sauvegarde

**Corrigé.** Comparer les données aux horaires connus et déterminer si le pic affecte réellement le service. Examiner latence, files d'attente et taux d'erreur, pas seulement le CPU. Ajouter une fenêtre temporelle ou une règle plus appropriée si le comportement normal est documenté. Conserver l'alerte si une autre mesure montre que l'opération dégrade le service.

### Exercice 9 — Estimer le volume de collecte

**Situation.** On supervise 600 hôtes avec 80 items en moyenne, chacun toutes les 60 secondes.

**Corrigé.** L'ordre de grandeur est de 600 × 80 / 60, soit environ 800 valeurs par seconde. Ce chiffre n'est pas un calcul exact de capacité de base de données : les types d'items, prétraitements, triggers, pics, valeurs dépendantes, événements et durées de rétention changent la charge réelle. Tester un pilote et mesurer la latence, les files d'attente et la croissance de base.

### Exercice 10 — Le dashboard annonce 99,95 % mais les utilisateurs signalent des erreurs

**Corrigé.** Vérifier le périmètre et le point de mesure de la disponibilité. Un ping ou une simple réponse HTTP peut être nominale alors que les transactions métier échouent. Ajouter un contrôle synthétique représentatif ou une mesure de résultat utilisateur, documenter le changement de méthode et ne pas comparer les séries sans signaler les différences de définition.

### Exercice 11 — Réviser un seuil d'interface

**Situation.** Un lien est régulièrement à 85 % de charge, sans perte ni latence supplémentaire, alors que l'équipe reçoit une alerte critique.

**Corrigé.** Confirmer la capacité nominale, l'horaire, la stabilité de la tendance, les erreurs et les besoins de service. Si le seuil est trop sensible, réviser la gravité ou la persistance et documenter les raisons. Ne pas ignorer une tendance de croissance : une mesure qui ne déclenche pas d'incident immédiatement peut tout de même justifier une action de capacité.

### Exercice 12 — Distinguer panne de la cible et panne de collecte

**Situation.** Les dernières mesures d'un serveur ont vingt minutes alors que l'application semble disponible.

**Corrigé.** Vérifier le mode d'agent, le chemin réseau depuis la plateforme, le dernier succès, le pare-feu et le statut du serveur. Exécuter un test de service indépendant. Présenter séparément la disponibilité du service et la fraîcheur de la collecte. Le fait que l'application réponde ne signifie pas que la supervision collecte correctement.

## 14. Défi final : construire une supervision défendable

Une application métier est utilisée dans plusieurs agences. Elle dépend d'un lien WAN, d'un routeur central, d'un DNS, d'une API interne et d'une base de données. L'équipe veut déterminer si le problème signalé est une perte de connectivité, une saturation, une panne applicative ou une absence de collecte. Elle veut aussi limiter les alertes en cascade et produire un rapport de cause racine.

**Travail demandé**

1. Dessiner la topologie et indiquer le point de collecte de chaque check.
2. Définir quatre signaux distincts : reachability, service applicatif, capacité et fraîcheur des données.
3. Décrire les hôtes et services Nagios, les plugins nécessaires et l'interprétation de leurs codes de retour.
4. Décrire les hôtes, items, templates, triggers, tags et actions Zabbix du même scénario.
5. Justifier fréquence, seuils, confirmation temporelle, récupération et gravité.
6. Définir des dépendances qui regroupent les symptômes de la perte WAN sans masquer une panne indépendante.
7. Décrire les flux, ports, protocoles et mesures de sécurité.
8. Tester panne et récupération en laboratoire.
9. Préparer le message de notification et la séquence d'escalade.
10. Définir les preuves pour la RCA et trois indicateurs de qualité de supervision.

**Correction attendue**

La topologie fait apparaître les dépendances réseau et applicatives ; les tests de disponibilité ne sont pas confondus avec la disponibilité métier. Les plugins Nagios sont testés, les arguments documentés et la logique SOFT/HARD comprise. Les items Zabbix existent réellement, leurs valeurs sont fraîches, les triggers utilisent une unité et une fenêtre correctes, et les notifications sont testées de bout en bout. Les flux de gestion sont limités et les identifiants protégés. La panne WAN peut produire un incident parent avec des symptômes corrélés, tout en conservant des contrôles indépendants. Les tests couvrent la panne, la récupération et la fraîcheur. Le compte rendu indique ce qui est établi, ce qui reste incertain et qui doit suivre les actions.
