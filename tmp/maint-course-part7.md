## 8. Concevoir des seuils et des déclencheurs pertinents

### 8.1 Seuil absolu, relatif et temporel

Un seuil absolu compare une mesure à une limite : occupation disque au-dessus de 90 %, perte au-dessus d'un pourcentage défini ou température supérieure à une limite constructeur. Un seuil relatif compare une valeur à son comportement historique. Une condition temporelle exige que le dépassement persiste ; elle permet d'éviter qu'un pic fugace devienne un incident alors qu'il n'a pas d'effet réel.

Les seuils doivent être justifiés par la capacité, les marges de sécurité, les contraintes du service et la vitesse de dégradation. Une partition stable à 85 % n'a pas la même urgence qu'une partition à 75 % qui augmente rapidement et sera pleine avant la prochaine fenêtre d'intervention. Un lien WAN à forte utilisation peut fonctionner normalement ; pour reconnaître une saturation, il faut observer la perte, la latence, les files d'attente et les exigences de l'application.

~~~mermaid
flowchart TD
  A[Valeur hors norme] --> B[Confirmer dans le temps]
  B --> C[Comparer à la référence]
  C --> D{Impact ou risque établi ?}
  D -->|Non| E[Observer la tendance]
  D -->|Oui| F[Créer un événement]
  F --> G[Action et responsable]
~~~

### 8.2 Hystérésis et récupération

Un trigger qui s'active à 90 % et récupère à 89,9 % risque d'osciller si la valeur bouge autour de la limite. Une condition de récupération distincte, une temporisation, une moyenne ou un minimum/maximum sur une fenêtre peuvent stabiliser l'état. Les possibilités exactes diffèrent entre Nagios et Zabbix ; le principe est de supprimer les oscillations inutiles sans retarder une récupération réelle.

La disparition d'un seuil n'est pas toujours la suppression du risque. Si un disque repasse sous la limite parce que des fichiers temporaires ont été supprimés, mais que la croissance va reproduire le problème le lendemain, l'événement peut se résoudre alors qu'une action de capacité reste nécessaire. Les tendances et le suivi d'actions doivent compléter les événements.

### 8.3 Corrélation et gravité

Les alertes doivent être analysées selon la topologie, le service, le site, la fenêtre temporelle et les dépendances. Des alertes simultanées peuvent avoir une cause commune, mais le timing seul ne prouve pas la causalité. Les règles de dépendance et de corrélation doivent être explicites et testées avec des scénarios réels ou de laboratoire.

~~~mermaid
flowchart LR
  A[Alertes brutes] --> B[Normalisation]
  B --> C[Analyse des dépendances]
  C --> D[Regroupement de symptômes]
  D --> E[Incident parent possible]
  E --> F[Évaluation de gravité]
  F --> G[Équipe responsable]
~~~

Chaque gravité doit correspondre à une action concrète. Une information peut enrichir un graphe. Un avertissement peut créer une tâche de capacité. Une alerte critique peut déclencher une astreinte et une communication. Un signal sans propriétaire ou sans suite attendue n'est pas correctement conçu.

### 8.4 Fatigue d'alerte

La fatigue d'alerte est provoquée par les faux positifs, les duplications, les notifications répétées et les signaux qui ne conduisent jamais à une action. Elle pousse les équipes à ignorer les messages ou à désactiver des contrôles importants. Pour réduire ce risque, mesurer les alertes actionnables, les doublons, les événements non acquittés, les délais de traitement et les incidents détectés trop tard.

Revoir les règles qui n'apportent aucune action, mais ne pas les supprimer par réflexe. La cause peut être un seuil mal réglé, une donnée qui ne mesure pas la bonne fonction, l'absence de propriétaire ou une procédure de traitement impraticable. Une bonne alerte doit changer une décision ou accélérer une action pertinente.

## 9. Modéliser et sécuriser la supervision

### 9.1 Inventaire et criticité

Avant de créer des hôtes, disposer d'un inventaire comprenant identifiant stable, type d'actif, adresse de gestion, site, rôle, criticité, propriétaire, dépendances, fenêtre de maintenance, protocole de collecte et contact d'escalade. Identifier les actifs retirés, temporaires, redondants et inconnus. Sinon, la couverture annoncée peut inclure des équipements inactifs tandis que des actifs critiques manquent.

La criticité influence la fréquence, la profondeur des contrôles, le niveau de notification et la rétention. Une passerelle partagée ou un DNS central peut avoir un rayon d'impact supérieur à celui d'un serveur isolé. Cartographier les composants partagés avant de décider quels symptômes doivent être agrégés.

### 9.2 Nommage, groupes et tags

Employer des noms stables et compréhensibles pour les hôtes, services et templates. Dans Zabbix, les tags peuvent qualifier le site, l'équipe, l'environnement, l'application ou le niveau de service selon la version. Dans Nagios, les groupes, contacts et noms d'objets structurent une partie de la gouvernance.

Les tags ne remplacent pas la qualité de l'inventaire. Un hôte portant **site=DOU** doit réellement appartenir au site concerné. Les mécanismes d'auto-découverte ne doivent pas placer un hôte inconnu dans un groupe privilégié ni lui attribuer des actions d'administration sans validation.

### 9.3 Sécurité des flux

La plateforme de supervision est sensible, car elle communique avec de nombreux segments et expose des informations sur l'état du parc. Limiter les ports par source et destination, séparer lecture et administration, utiliser des comptes nominatifs, protéger les identifiants, sécuriser l'interface Web et conserver les journaux de changement. Utiliser le chiffrement lorsqu'il est pris en charge par les composants.

~~~mermaid
flowchart LR
  A[Administrateurs nominatifs] -->|HTTPS contrôlé| B[Frontend Web]
  B --> C[Moteur supervision]
  C -->|Flux autorisés| D[Agents]
  C -->|SNMPv3 lecture| E[Routeurs et switches]
  C -->|Sortie contrôlée| F[Relais notification]
~~~

Vérifier qui peut modifier les triggers, les commandes, les médias, les scripts ou les intégrations. Un utilisateur capable de remplacer une commande ou d'élargir les cibles de collecte peut compromettre la détection ou introduire un risque d'exécution. Les droits d'administration doivent être réservés, revus et audités.

### 9.4 Superviser la plateforme elle-même

Surveiller les processus, l'ordonnanceur, les files d'attente, la base, l'espace disque, les retards de collecte, les derniers contacts des proxys et le canal de notification. Si le canal d'envoi tombe, le système peut générer des événements sans que l'équipe les voie. Prévoir un canal indépendant pour les alertes portant sur la plateforme centrale.

~~~mermaid
flowchart TD
  A[Moteur] --> B[Collecte et ordonnanceur]
  A --> C[Base de données]
  A --> D[Agents et proxies]
  A --> E[Notifications]
  B --> F[Contrôles de santé]
  C --> F
  D --> F
  E --> F
  F --> G[Canal indépendant]
~~~

Sauvegarder les configurations Nagios, les plugins maison et les modèles. Pour Zabbix, protéger de façon cohérente la base et la configuration nécessaire à la reconstruction. Une sauvegarde non testée ne prouve pas qu'il sera possible de restaurer l'environnement dans le temps visé.
