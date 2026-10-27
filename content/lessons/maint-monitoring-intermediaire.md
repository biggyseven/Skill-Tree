# Supervision réseau (Nagios, Zabbix)

> **Mise en contexte**
>
> L'entreprise dans laquelle tu travailles utilise plusieurs commutateurs, routeurs, serveurs, points d'accès Wi-Fi et applications métier. À 8 h 20, les utilisateurs signalent que le logiciel de facturation est lent. À 8 h 27, un premier serveur ne répond plus. À 8 h 35, un collègue constate que l'espace disque du serveur de base de données est presque saturé. Si l'équipe attend les appels téléphoniques pour découvrir chaque difficulté, elle subit les incidents au lieu de les anticiper.
>
> La supervision rassemble des mesures régulières, des contrôles de disponibilité, des seuils, des événements, des notifications et des tableaux de bord. Elle permet de repérer les dérives avant qu'elles ne deviennent des interruptions importantes, de vérifier un service après une intervention et de fournir des faits utiles au diagnostic. Elle ne remplace ni les sauvegardes, ni les procédures, ni les compétences de l'équipe : elle donne des signaux sur lesquels des personnes doivent prendre des décisions.
>
> Ce cours fait passer d'une surveillance « un ping de temps en temps » à une supervision organisée. Tu apprendras à modéliser un périmètre, à comparer Nagios Core et Zabbix, à définir des indicateurs pertinents, à construire des alertes utiles, à protéger la plateforme de supervision, à traiter les faux positifs et à mesurer la qualité du dispositif. Les exemples sont pédagogiques ; adapte toujours les commandes, versions, seuils, règles de notification et autorisations à ton environnement.

## 1. Objectifs pédagogiques et périmètre

À la fin du cours, tu dois pouvoir concevoir un petit dispositif de supervision pour un réseau d'entreprise, justifier les contrôles retenus, lire une alerte, réduire les notifications inutiles et expliquer les limites des mesures. Tu dois aussi savoir comment vérifier que la supervision elle-même fonctionne.

Les compétences visées sont les suivantes :

- distinguer supervision, observabilité, inventaire et journalisation ;
- reconnaître les mesures de disponibilité, de performance, de capacité et d'expérience utilisateur ;
- décrire la relation entre équipement, service contrôlé, mesure, seuil, événement et notification ;
- préparer un déploiement de Nagios Core ou Zabbix sans exposer inutilement les systèmes ;
- construire un tableau de bord adapté à une équipe de support ;
- écrire une règle d'alerte qui déclenche une action possible ;
- traiter les alertes, les dépendances, les maintenances planifiées et les faux positifs ;
- valider la couverture, la fraîcheur des données et la chaîne de notification ;
- réaliser un petit bilan de supervision exploitable dans le reporting mensuel.

La supervision doit avoir un périmètre explicite. Une équipe ne doit pas promettre de détecter « toutes les pannes ». Elle doit préciser les équipements observés, les services concernés, les périodes couvertes, la fréquence des contrôles, les seuils, les destinataires et les exclusions approuvées. Un service non instrumenté peut tomber en panne sans produire d'alerte. Le niveau de couverture doit être défini en termes de services et de risques, pas seulement de nombre d'équipements ajoutés dans l'outil.

## 2. Les quatre questions auxquelles répond la supervision

La première question est : **l'objet est-il joignable ?** Un test ICMP peut indiquer qu'une adresse répond, mais un serveur peut accepter le ping alors que son application est bloquée. Inversement, un pare-feu peut bloquer ICMP alors que le service HTTP est pleinement opérationnel. Il faut donc éviter de confondre joignabilité réseau et disponibilité métier.

La deuxième question est : **le service répond-il correctement ?** On peut vérifier l'établissement d'une connexion TCP, le code de réponse HTTP, la validité d'un certificat, la présence d'un texte attendu ou la durée d'une requête. Ce contrôle est plus proche du besoin utilisateur, mais il doit être conçu sans générer de charge excessive ni exposer de données sensibles. Une sonde de transaction doit utiliser un compte de test limité, des données synthétiques et un parcours qui ne déclenche pas d'opération financière ou destructive.

La troisième question est : **les ressources se dégradent-elles ?** L'utilisation du processeur, la mémoire disponible, l'espace disque, les erreurs d'interface, la température, les connexions actives ou la longueur d'une file peuvent révéler un risque. Une valeur isolée est rarement suffisante : une utilisation CPU de 90 % pendant vingt secondes peut être normale, alors qu'une saturation persistante accompagnée de délais élevés est plus préoccupante.

La quatrième question est : **la tendance devient-elle anormale ?** La croissance d'un volume disque, le taux d'erreurs d'une interface ou la hausse du temps de réponse peuvent être plus utiles qu'un seuil instantané. Un disque qui gagne 3 % d'occupation chaque jour peut être en danger même s'il reste aujourd'hui 30 % d'espace libre.

## 3. Architecture d'une chaîne de supervision

Les données suivent généralement une chaîne : cible, mécanisme de collecte, stockage, règle d'évaluation, notification et réaction. Selon la plateforme, certaines fonctions sont rassemblées dans un serveur central, réparties entre agents et serveurs, ou confiées à des relais. La topologie réelle dépend de la taille, de la segmentation réseau, de la sécurité et de la disponibilité demandée.

~~~mermaid
flowchart LR
    A[Équipements et services] --> B[Agent, SNMP ou contrôle distant]
    B --> C[Collecte et historique]
    C --> D[Seuils et corrélation]
    D --> E[Événement qualifié]
    E --> F[Notification ciblée]
    F --> G[Diagnostic et intervention]
    G --> H[Compte rendu et amélioration]
    H -. ajustement .-> D
~~~

Les points d'observation doivent être choisis selon le risque. Pour un routeur, on peut vérifier la joignabilité, l'état des interfaces, l'utilisation, les erreurs et la température si les données sont disponibles. Pour une application web, on contrôle plutôt le code HTTP, le délai de réponse, la disponibilité du certificat et, si c'est autorisé, un parcours synthétique. Pour une sauvegarde, il faut observer non seulement la disponibilité du serveur de sauvegarde, mais aussi la fin des tâches, leur durée, les erreurs et la possibilité de restauration.

Le serveur de supervision constitue lui-même un service critique. Si sa base de données est saturée, si ses sondes sont arrêtées ou si son canal de notification ne fonctionne plus, l'équipe peut croire à tort que le réseau est calme. Le plan de supervision doit donc inclure l'espace disque, l'état des processus, les retards de collecte, la file de traitement, l'âge du dernier point reçu et un test contrôlé du chemin d'alerte.

Une sonde doit posséder une identité claire. Les noms d'hôtes dupliqués, les adresses modifiées sans mise à jour ou les équipements retirés qui restent suivis rendent les tableaux de bord peu fiables. À l'ajout d'une cible, consigne son propriétaire, sa fonction, le service métier dépendant, sa criticité, sa localisation, sa source d'inventaire, son groupe de notification et les règles appliquées. Un inventaire fiable évite que la supervision ne devienne une liste d'adresses sans contexte.

## 4. Nagios Core : objets, contrôles et alertes

Nagios Core est un système de supervision qui contrôle des hôtes et des services définis. Les contrôles s'appuient couramment sur des plugins qui exécutent une vérification et renvoient un état ainsi qu'un texte explicatif. La configuration décrit les hôtes, services, périodes, contacts, commandes et relations nécessaires. La documentation officielle explique les objets et les contrôles des services publics ; consulte-la avant de reprendre un extrait dans une installation réelle :

- https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/about.html
- https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/configobject.html
- https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/monitoring-publicservices.html

Un **hôte** représente habituellement un équipement ou un système identifiable. Un **service** représente un contrôle associé à cet hôte : état d'un service système, réponse d'un site web, espace disque, disponibilité SSH ou niveau d'erreurs. Un **plugin** réalise le contrôle. Une **commande** donne à Nagios la manière de lancer ce plugin avec les paramètres adéquats. Les **contacts** et groupes de contacts déterminent les personnes qui peuvent recevoir des notifications.

Il faut séparer le résultat technique d'une commande du niveau de gravité communiqué à l'organisation. Les états de service habituels dans Nagios Core sont OK, WARNING, CRITICAL et UNKNOWN. OK indique que le contrôle respecte ses critères. WARNING correspond à une dégradation ou à un seuil d'avertissement. CRITICAL traduit un état déclaré critique par le contrôle. UNKNOWN indique que la vérification n'a pas pu conclure correctement, par exemple à cause d'une erreur de plugin ou de paramétrage. Un UNKNOWN ne doit pas être interprété automatiquement comme un serveur en panne : il faut aussi diagnostiquer le mécanisme de contrôle.

Un plugin comme check_http vérifie un service web ; check_ping peut tester une réponse ICMP ; d'autres plugins contrôlent les disques, les charges et les services. La présence exacte des plugins et leurs paramètres dépendent de l'installation. N'exécute pas une commande copiée depuis un tutoriel sans vérifier le nom du plugin, la version installée, les options, l'utilisateur qui lance le contrôle et les droits nécessaires.

Exemple de configuration conceptuelle — ce fragment illustre des objets Nagios, il ne constitue pas à lui seul une configuration prête pour la production :

~~~text
define host {
    use         linux-server
    host_name   serveur-intranet
    alias       Serveur intranet
    address     192.0.2.20
}

define service {
    use                  generic-service
    host_name            serveur-intranet
    service_description  HTTP intranet
    check_command        check_http
}
~~~

Avant le déploiement, vérifie que les modèles référencés existent, que la commande check_http est définie dans les fichiers de commande et que le plugin fonctionne dans le contexte de l'utilisateur de supervision. Les adresses de la plage 192.0.2.0/24 sont réservées aux exemples documentaires ; remplace-les dans ton laboratoire par une cible que tu es autorisé à tester.

La documentation peut aussi décrire les relations parent/enfant entre hôtes. Elles aident à différencier un équipement réellement indisponible d'une cible inaccessible parce qu'un parent réseau ne répond plus. Sans dépendances, une panne de routeur peut produire des dizaines d'alertes d'équipements en aval ; une conception correcte limite le bruit tout en conservant les informations utiles.

Les contrôles actifs sont exécutés à intervalles définis. Leur fréquence doit être assez courte pour détecter les problèmes dans le délai requis, mais pas au point de surcharger la cible ou le réseau. Des contrôles passifs peuvent être utiles lorsqu'un système externe fournit un résultat. Quel que soit le mécanisme, la supervision doit distinguer la date d'exécution de la date de réception : un résultat ancien reçu tardivement ne doit pas être présenté comme un état actuel.

## 5. Zabbix : hôtes, items, triggers, événements et modèles

Zabbix organise la supervision autour des hôtes surveillés, des **items** qui recueillent des valeurs, des **triggers** qui évaluent les conditions, des événements et des actions. Il peut utiliser des agents, des contrôles réseau, SNMP et d'autres méthodes de collecte. Les modèles permettent de réutiliser les mêmes éléments pour des équipements comparables ; les tableaux de bord présentent ensuite les problèmes, valeurs et tendances utiles.

La documentation actuelle est disponible à l'adresse https://www.zabbix.com/documentation/current/en/manual/. La version de documentation consultée est susceptible de changer ; vérifie toujours la version déployée par ton organisation avant d'appliquer un réglage ou une expression.

~~~mermaid
flowchart TD
    A[Hôte : commutateur] --> B[Items : interface, erreurs, charge]
    B --> C[Historique des valeurs]
    C --> D[Trigger : erreurs au-dessus du seuil]
    D --> E{Condition confirmée ?}
    E -->|Oui| F[Événement de problème]
    E -->|Non| G[Pas de problème déclaré]
    F --> H[Action et notification]
    H --> I[Accusé de prise en charge]
~~~

Un **item** définit ce qui est collecté, comment, à quelle fréquence et sous quel format. Un **trigger** transforme une série de mesures en état exploitable. Il faut comprendre la fenêtre temporelle de l'expression : un seuil dépassé une seule fois ne signifie pas nécessairement la même chose qu'un seuil dépassé pendant cinq minutes. Des dépendances de triggers peuvent réduire les alertes en cascade. Les règles de découverte et les modèles facilitent l'extension du périmètre, mais la découverte automatique doit être contrôlée afin de ne pas intégrer des équipements inconnus sans validation.

Un modèle doit refléter la fonction d'un type d'équipement, pas uniquement le nom d'un fabricant. Un modèle pour serveur Linux peut suivre le CPU, la mémoire, les systèmes de fichiers et des services essentiels. Un modèle pour commutateur peut suivre la disponibilité, l'état et les compteurs des interfaces, l'alimentation et la température si les OID correspondants sont pris en charge. La collecte doit rester adaptée à l'environnement : une interrogation trop fréquente ou trop large augmente la charge, le volume d'historique et les risques de bruit.

Les items numériques, textuels et calculés n'ont pas les mêmes contraintes. Une valeur brute collectée peut être transformée ou agrégée, mais chaque transformation doit rester compréhensible. Si le temps de réponse est enregistré en millisecondes et le seuil exprimé en secondes, une erreur d'unité peut produire de nombreuses alertes ou masquer une dégradation. Ajoute les unités, les périodes et les méthodes dans la documentation de la règle.

Nagios Core et Zabbix répondent à des besoins de supervision, mais leur configuration et leur modèle de données ne sont pas identiques. Ne mélange pas des exemples de syntaxe entre les outils et ne suppose pas que les mêmes seuils sont automatiquement pertinents. Choisis selon les compétences de l'équipe, la complexité des modèles, les besoins d'historique, la distribution des sondes, la capacité de notification, les contraintes d'exploitation et les exigences de support.

## 6. Choisir les bons indicateurs : disponibilité, performance et capacité

Un indicateur utile relie une mesure à un risque ou un objectif opérationnel. Il doit avoir une unité, une source, une fréquence, un périmètre et une méthode d'interprétation. Si deux personnes calculent la même mesure avec des fenêtres différentes, elles peuvent obtenir des conclusions contradictoires.

| Besoin | Mesure indicative | Interprétation prudente |
|---|---|---|
| Disponibilité | Réponses positives / contrôles valides | Préciser l'emplacement de la sonde et les exclusions |
| Temps de réponse | Millisecondes par requête | Analyser médiane, percentiles et erreurs, pas seulement la moyenne |
| Utilisation CPU | Pourcentage dans une fenêtre | Relier la durée élevée à la charge et à la dégradation observable |
| Espace disque | Libre en octets et pourcentage | Estimer le temps avant saturation à partir de la tendance |
| Interface réseau | Erreurs, pertes, débit, état | Corréler les compteurs avec les changements et la charge |
| Sauvegarde | Dernière exécution, résultat, durée | Vérifier la réussite réelle et le test de restauration |
| Expérience utilisateur | Parcours ou transaction synthétique | Utiliser un compte non privilégié et éviter d'extraire des données réelles |

Pour estimer le temps restant avant saturation, on peut utiliser une approximation : espace libre courant divisé par consommation moyenne par jour. Si un volume dispose de 120 Go libres et consomme en moyenne 8 Go par jour, l'estimation simple est de 15 jours. Mais la projection n'est fiable que si le rythme de croissance demeure proche de la moyenne. Un import exceptionnel, une rétention qui change ou un fichier journal qui grossit soudainement invalide l'estimation. Dans une vraie exploitation, il faut conserver une marge de sécurité et faire traiter l'alerte avant l'échéance estimée.

La disponibilité doit être définie : un ping réussi ne garantit pas qu'une transaction peut aboutir. Une sonde depuis le même réseau que le serveur peut aussi manquer une panne de routage vécue par les utilisateurs d'un site distant. Pour un service important, combine des contrôles locaux de composants et des contrôles de synthèse depuis un point représentatif des utilisateurs.

Les statistiques agrégées demandent une lecture soigneuse. Une disponibilité de 99,9 % ne décrit pas à elle seule la répartition des interruptions, les heures où elles se produisent, le nombre de personnes affectées, les dégradations partielles ni les exclusions du calcul. Deux mois ayant le même pourcentage peuvent représenter des expériences très différentes.

Définis les métriques en évitant les comparaisons trompeuses. Un débit en bits par seconde n'est pas un volume total transféré. Un compteur d'erreurs cumulatif n'est pas directement un taux d'erreur : il faut comparer son évolution sur une période et tenir compte des remises à zéro. Un taux de disponibilité ne peut être calculé que si le nombre de contrôles attendus et les fenêtres exclues sont bien définis. La donnée sans contexte peut inciter à une mauvaise décision.

## 7. Concevoir des alertes actionnables et réduire les faux positifs

Une bonne alerte répond à six questions : quel objet est concerné, quel symptôme a été observé, depuis quand, quel est l'impact possible, qui doit agir et quelle est la prochaine action attendue ? Si le destinataire ne sait pas quoi faire, la notification ressemble à un bruit plutôt qu'à un outil d'exploitation.

Une alerte doit nommer l'équipement et le service, indiquer une valeur et un seuil compréhensibles, ajouter le lien vers le tableau de bord ou le ticket, rappeler la gravité et préciser la procédure attendue. Évite les titres tels que « problème important » ou « alerte système » qui ne permettent pas de trier rapidement plusieurs notifications.

Exemple de règle conceptuelle : « Si l'espace libre du volume de données reste inférieur à 15 % pendant 10 minutes et que le volume n'est pas en maintenance, créer un avertissement pour l'équipe systèmes. Si l'espace libre reste inférieur à 7 % ou si l'espace disponible est inférieur à une limite absolue validée, escalader selon la procédure. » Les valeurs 15 % et 7 % ne sont pas universelles : elles doivent être ajustées en fonction de la taille du volume, du rythme de croissance, des besoins de l'application et du temps d'intervention disponible.

Il faut distinguer seuil absolu, seuil relatif, durée et combinaison de symptômes. Un serveur avec 4 Go libres peut être critique si la base écrit rapidement, mais un volume de plusieurs téraoctets avec 4 Go libres peut également être critique pour une autre raison. Inversement, un CPU à 90 % pendant quelques secondes n'appelle pas nécessairement un appel nocturne si aucune qualité de service n'est affectée. Les seuils doivent être testés sur des données d'exploitation représentatives, quand elles sont disponibles et autorisées.

~~~mermaid
flowchart TD
    A[Mesure reçue] --> B[Comparer à la règle]
    B --> C{Durée et seuil satisfaits ?}
    C -->|Non| D[Conserver la tendance]
    C -->|Oui| E[Évaluer dépendances et maintenance]
    E --> F{Alerte utile et action possible ?}
    F -->|Non| G[Corriger la règle ou documenter l'exception]
    F -->|Oui| H[Notifier la bonne équipe]
    H --> I[Accuser réception et diagnostiquer]
~~~

Les faux positifs naissent souvent de seuils trop agressifs, d'un intervalle de collecte mal choisi, d'une maintenance oubliée, d'une cible mal identifiée ou d'une vérification fragile. Les faux négatifs apparaissent quand les seuils sont trop permissifs, les contrôles trop rares, les permissions insuffisantes ou le service métier non instrumenté. L'équipe doit analyser les deux catégories.

Une pratique efficace consiste à examiner régulièrement les alertes qui n'ont entraîné aucune action. Ne les supprime pas uniquement parce qu'elles sont gênantes : vérifie si elles signalent une dérive, si le niveau de gravité est mal défini, si une dépendance manque ou si un comportement normal n'a pas été modélisé. Pour toute règle modifiée, note l'ancien comportement, la modification, la raison, la personne qui a approuvé le changement et la façon de revenir à la règle précédente.

Une notification à haute gravité doit correspondre à une action possible à la période concernée. Une alerte qui demande une réparation immédiate mais qui s'adresse à un groupe non astreint au milieu de la nuit n'est pas exploitable. Il faut accorder le niveau de gravité, le calendrier, l'impact métier et le destinataire. Une sévérité graphique ne remplace pas cette décision opérationnelle.

## 8. Notifications, astreinte et responsabilités

Les notifications doivent correspondre aux responsabilités et aux horaires. Un problème d'information peut créer un ticket à traiter dans la journée ; une défaillance touchant un service critique peut nécessiter une alerte immédiate. Le choix doit être défini par la politique de service, non par la seule facilité du logiciel.

Définis les groupes qui reçoivent les alertes de réseau, de systèmes, de stockage ou d'applications. Chaque groupe doit avoir une procédure d'escalade, un responsable de relève et un mécanisme de vérification de la notification. Les adresses des personnes, numéros et secrets de notification ne doivent pas être dispersés dans des fichiers de test ou des captures publiques.

Les mécanismes de répétition peuvent être utiles si aucune prise en charge n'est enregistrée après une durée déterminée. Ils deviennent contre-productifs si la même alerte est renvoyée à l'infini sans information nouvelle. Un accusé de réception n'est pas une résolution : il indique que quelqu'un a assumé le traitement. Après rétablissement, il faut déterminer si un ticket, un rapport d'incident ou une analyse de cause racine est nécessaire.

Pour une panne d'un équipement parent, les notifications des équipements enfants doivent être maîtrisées. Les dépendances servent à réduire le nombre d'alertes en cascade, mais elles ne doivent pas faire disparaître les symptômes utiles. L'équipe doit pouvoir voir la panne initiale et les services affectés. En cas de défaillance commune, le ticket principal peut être lié aux symptômes individuels pour conserver les informations sans multiplier inutilement les incidents indépendants.

## 9. Maintenance planifiée et fenêtres de changement

La supervision doit connaître les fenêtres de maintenance autorisées pour limiter les notifications attendues pendant une mise à jour, un redémarrage ou une opération réseau. La fenêtre doit avoir un objet, un périmètre, un début et une fin, une personne responsable et un moyen de confirmation. Une fenêtre trop large peut cacher une vraie panne après la fin de l'intervention.

Ne supprime pas simplement l'historique au moment d'une maintenance : il peut être nécessaire pour comprendre les conséquences du changement. Les données et événements doivent être conservés selon les règles de rétention. À la fin de l'opération, retire la suppression temporaire des alertes et vérifie que la collecte a repris, que les services sont sains et qu'aucune alerte n'est restée silencieuse.

~~~mermaid
flowchart TD
    A[Changement approuvé] --> B[Définir objets et durée]
    B --> C[Prévenir équipe et propriétaire]
    C --> D[Appliquer la suppression ciblée]
    D --> E[Exécuter la maintenance]
    E --> F[Restaurer contrôles et notifications]
    F --> G[Test fonctionnel et preuve]
    G --> H[Clôturer et examiner les écarts]
~~~

Exemple de checklist de maintenance de supervision :
1. confirmer le périmètre et l'autorisation ;
2. vérifier que l'équipe sait quelles alertes seront supprimées ;
3. définir une durée raisonnable et un responsable ;
4. sauvegarder ou exporter la configuration de supervision si nécessaire ;
5. appliquer le changement prévu ;
6. restaurer les contrôles et notifications normaux ;
7. exécuter un test fonctionnel ;
8. noter les alertes attendues, les surprises et les actions restantes.

La suppression doit être la plus ciblée possible. Si un site fait l'objet d'une maintenance, n'exclus pas sans raison toute la plateforme de supervision ni tous les services de l'entreprise. Le mécanisme de maintenance doit aussi posséder un rappel ou une expiration automatique lorsque la plateforme le permet, avec une vérification au-delà de la période prévue.

## 10. Accès, secrets et sécurité du système de supervision

Une plateforme de supervision peut exposer des noms d'hôtes, des topologies, des versions de logiciels, des adresses, des horaires d'activité, des faiblesses de capacité et des événements de sécurité. Les informations de monitoring doivent donc être protégées en fonction de leur sensibilité. Un compte en lecture de tableau de bord n'a pas nécessairement besoin de modifier les commandes, les scripts ou les contacts.

Applique le moindre privilège : sépare les droits de lecture, de configuration et d'administration. Restreins l'accès réseau aux interfaces web et aux agents, utilise des canaux de communication protégés lorsque le système les prend en charge, mets à jour les composants et documente les exceptions. Ne donne pas au serveur de supervision des privilèges d'administration globaux sur chaque équipement pour simplifier la collecte.

Les secrets utilisés pour les agents, SNMPv3, SSH, API ou notifications doivent être conservés dans les mécanismes prévus. Évite les mots de passe en clair dans les scripts, les référentiels de cours ou les captures. Les comptes de test devraient être limités, surveillés et supprimés lorsqu'ils ne sont plus nécessaires. La supervision des événements de sécurité complète les outils de journalisation ; elle ne remplace pas un dispositif de détection et de réponse à incident dédié.

La sécurité s'applique également à la collecte. Un script personnalisé peut exécuter une commande avec des privilèges plus élevés que prévu, interpréter incorrectement une donnée ou être détourné. Vérifie les entrées, fixe des délais, protège les fichiers, limite les permissions, journalise les erreurs et teste les scripts avant de les intégrer au planificateur de supervision. Si l'outil prend en charge un compte lecture seule ou un niveau de privilège SNMP restreint, préfère-le à un accès global lorsque les données attendues le permettent.

## 11. Données, rétention, performance et évolution

Chaque collecte ajoute des valeurs, des événements ou des historiques. Une fréquence élevée et une grande cardinalité augmentent le volume stocké, la charge de la base et le temps nécessaire pour afficher les dashboards. Il faut déterminer quelles données sont indispensables au diagnostic immédiat, lesquelles servent aux tendances et combien de temps chacune doit être conservée.

Le choix de rétention doit être cohérent avec les usages. Une équipe peut garder un historique détaillé sur une période courte, puis conserver des tendances agrégées plus longtemps. Les règles dépendent de la capacité, de la conformité, de l'intérêt métier et des possibilités de la plateforme. Ne supprime pas arbitrairement les données utiles à un incident en cours ou à une obligation de conservation.

Les valeurs absentes ne signifient pas toujours zéro. Une donnée inexistante peut signaler une sonde en panne, un service indisponible, un problème d'authentification, un changement d'OID, une indisponibilité réseau ou une mauvaise configuration. Le dashboard doit différencier « zéro mesuré », « aucune valeur reçue » et « valeur périmée ».

La découverte automatique d'équipements peut élargir rapidement la couverture. Elle doit être accompagnée d'une validation : les équipements trouvés sont-ils autorisés, appartiennent-ils à la bonne entité, leurs noms sont-ils corrects, le modèle appliqué correspond-il à leur rôle, les paramètres de collecte sont-ils acceptables ? Un scan non autorisé ou une interrogation excessive peut perturber certains matériels anciens.

Avant d'ajouter des centaines de cibles, estime les effets : nombre d'items, fréquence de collecte, volume d'historique et débit réseau. Déploie un modèle pilote sur quelques équipements représentatifs, mesure la charge de collecte et du serveur, puis élargis progressivement. Si les intervalles sont très courts sur toutes les métriques, les volumes augmentent rapidement sans nécessairement améliorer la qualité de détection.

## 12. Tableau de bord pour le support et la maintenance

Un tableau de bord d'équipe doit servir à décider, pas seulement à décorer un écran. Il doit présenter les problèmes actifs par sévérité, les services métier concernés, les événements sans propriétaire, les alertes récurrentes, les tendances de capacité et l'état de la supervision elle-même. Les vues doivent être adaptées au public : une équipe réseau a besoin d'informations différentes du responsable de service.

Une bonne page d'accueil n'affiche pas toutes les métriques. Elle permet de repérer rapidement ce qui requiert une action, d'ouvrir le détail et de revenir à une vue d'ensemble. Organise les widgets selon la priorité opérationnelle et assure-toi que les couleurs ne constituent pas l'unique moyen de transmettre la gravité. Les noms des services doivent être compréhensibles par l'équipe, même lorsque la plateforme emploie des identifiants techniques.

Pour le reporting, capture les indicateurs de couverture, la disponibilité calculée avec sa méthode, le nombre d'événements par gravité, les alertes sans prise en charge, les faux positifs, les principaux risques de capacité et les actions décidées. Les captures d'écran peuvent compléter les données mais ne doivent pas être l'unique source des chiffres.

Un tableau de bord destiné à la direction doit éviter la liste des compteurs bruts. Il présentera plutôt la continuité du service, les interruptions significatives, les risques de capacité, le respect des engagements et les actions avec responsables et échéances. La vue technique reste disponible pour les personnes qui mènent les investigations. L'objectif est de réduire le temps nécessaire pour passer du signal à une décision, pas de masquer les détails.

## 13. Procédure d'investigation d'une alerte

Quand une alerte apparaît, commence par confirmer l'objet, l'heure et la fraîcheur des mesures. Lis le contrôle qui a déclenché l'événement et consulte les données sur la période utile. Vérifie les changements récents, les fenêtres de maintenance et les dépendances réseau ou applicatives. Ne redémarre pas automatiquement un serveur uniquement parce qu'un seuil a été franchi.

Une méthode reproductible :
- déterminer si l'alerte décrit l'hôte, le service ou le système de supervision ;
- vérifier si le symptôme est observable depuis un autre point autorisé ;
- examiner les séries temporelles et l'historique des événements ;
- vérifier si d'autres composants dépendants signalent le même symptôme ;
- recueillir les journaux et résultats de test autorisés ;
- estimer l'impact sur l'utilisateur et appliquer la priorité ;
- suivre la procédure de diagnostic ou transférer le dossier si nécessaire ;
- confirmer le résultat après la correction et documenter la clôture.

La corrélation temporelle n'est pas une preuve de causalité. Une hausse CPU et une lenteur peuvent apparaître au même moment sans que la première explique la seconde. Il faut formuler les hypothèses, choisir des contrôles qui les distinguent, conserver les résultats et ne conclure qu'au niveau permis par les preuves.

~~~mermaid
sequenceDiagram
    participant S as Supervision
    participant N as N1
    participant E as Équipe experte
    participant T as Ticket
    S->>N: Alerte avec métrique et contexte
    N->>T: Enregistre impact et heure
    N->>N: Contrôle l'état, l'historique et les changements
    alt Résolution selon procédure
        N->>T: Note actions, résultats et vérification
    else Expertise nécessaire
        N->>E: Transmet preuves et hypothèses
        E->>T: Ajoute diagnostic et action
    end
    T-->>S: Vérifier le retour à l'état normal
~~~

Le ticket lié à l'alerte doit contenir la source, le premier instant observé, l'impact, les vérifications réalisées, les résultats, les modifications et le critère de retour à la normale. Évite de copier un graphe sans indiquer l'intervalle temporel ou l'unité. Une capture d'écran doit permettre de retrouver la période et l'objet dans la plateforme.

## 14. Travaux pratiques guidés

### TP 1 — Construire une matrice de supervision

Dans un laboratoire autorisé, choisis un routeur simulé ou un hôte de test, un serveur web et un stockage fictif. Pour chaque cible, rédige une fiche avec le besoin surveillé, la méthode de collecte, la fréquence, les seuils, le responsable, l'action associée et la rétention des données. Ajoute une colonne « risque de faux positif » et explique ce qui pourrait déclencher une fausse alerte.

Correction attendue : le routeur doit être suivi au minimum pour la joignabilité et, si disponible, l'état des interfaces ; le serveur web doit être évalué via le service HTTP plutôt que par le ping seul ; le stockage doit avoir une métrique d'espace libre et une tendance de croissance. Les seuils ne doivent pas être inventés comme une règle universelle : ils doivent être reliés à un délai avant saturation acceptable et au niveau de service attendu.

### TP 2 — Maquetter une alerte actionnable

Rédige une alerte pour une interface réseau qui présente un taux d'erreurs supérieur à la normale. Le message doit contenir le nom du switch, l'interface, la période de mesure, le compteur observé, l'impact à vérifier, le groupe responsable et un lien vers la procédure. Simule ensuite un cas où le seuil est dépassé une seule fois puis revient à la normale.

Correction attendue : l'alerte doit préciser que le compteur a augmenté pendant la fenêtre observée, sans affirmer automatiquement que l'interface est défectueuse. La procédure commence par vérifier le câble, le port distant, les erreurs et les changements récents dans le périmètre autorisé. La règle doit inclure une durée ou une évolution du compteur adaptée au type d'erreur pour éviter de déclencher une notification sur chaque incrément isolé.

### TP 3 — Comparer les modèles de contrôle

Prépare une table de sélection pour Nagios Core et Zabbix. Compare les types de cibles, la collecte, les règles, les templates, les historiques, les notifications, la courbe d'apprentissage et les pratiques d'exploitation que tu maîtrises. N'utilise pas un classement absolu sans préciser le contexte.

Correction attendue : Nagios Core offre un modèle explicite de contrôles d'hôtes et de services avec des plugins ; Zabbix organise la collecte autour des items, triggers, templates, événements et actions. Aucun outil ne dispense l'équipe de définir les besoins, de sécuriser les accès, de calibrer les seuils et de tester les alertes. Le meilleur choix est celui dont l'organisation peut maintenir la configuration dans la durée.

### TP 4 — Tester la chaîne d'alerte

Utilise un hôte de test et une règle temporaire prévue pour le laboratoire. Provoque uniquement une condition contrôlée, vérifie l'événement, le destinataire et l'accusé de réception, puis restaure l'état normal. Si l'environnement ne permet pas de provoquer un événement en sécurité, simule le résultat dans une maquette plutôt que de désactiver un service de production.

Correction attendue : la preuve comprend l'heure du test, le nom de la cible, le résultat attendu et observé, la réception de la notification et le retour à l'état normal. Une alerte visible sur le tableau de bord mais jamais envoyée au destinataire révèle que la chaîne de notification n'est pas validée.

### TP 5 — Détecter la perte de données de supervision

Imagine que le serveur central affiche les derniers points d'une interface avec plusieurs heures de retard. Explique comment tu détermines s'il s'agit d'un incident sur l'interface, d'un problème de collecte ou d'un problème d'historique.

Correction attendue : vérifier d'abord l'heure et l'état du serveur de supervision, puis le statut de la source, le mécanisme de collecte, les permissions et les erreurs de communication. Comparer une mesure récente obtenue par un contrôle indépendant autorisé peut aider. Il ne faut pas interpréter l'absence de donnée comme une valeur nulle.

### TP 6 — Concevoir un contrôle de fraîcheur

Crée une règle qui signale qu'une métrique importante n'a pas été reçue depuis une durée supérieure à ce qui est acceptable. Définis les cas où l'absence de valeur est normale, comme pendant une maintenance planifiée, et les cas où elle constitue un incident de supervision.

Correction attendue : la règle doit posséder un intervalle toléré, identifier la métrique, vérifier l'état de la collecte et supprimer seulement les alertes attendues pendant une fenêtre approuvée. La remise en service doit être vérifiée après la maintenance. Une valeur périmée doit être clairement différenciée d'une mesure actuelle.

## 15. Exercices avec corrections

### Exercice 1 — Ping réussi, application indisponible

**Situation :** le ping d'un serveur répond, mais le portail web renvoie une erreur 503.

**Correction :** l'hôte est joignable au niveau ICMP, mais le service HTTP n'est pas nécessairement sain. Contrôler le port, la réponse HTTP, les journaux applicatifs, la dépendance à une base ou à un proxy et les événements récents. L'alerte doit porter sur le service et mentionner le statut observé. Ne marque pas le service comme disponible uniquement parce que le ping répond.

### Exercice 2 — CPU élevé pendant quinze secondes

**Situation :** un seuil CPU est dépassé un court instant, sans ralentissement observable.

**Correction :** vérifier la durée de la règle, l'historique et la charge normale de ce système. Si le comportement est attendu, ajuster la logique ou conserver un indicateur informatif. Ne supprime pas la règle sans validation : la même pointe peut devenir dangereuse si elle se prolonge ou coïncide avec une saturation de mémoire.

### Exercice 3 — Des dizaines d'alertes simultanées

**Situation :** un routeur de distribution tombe, puis les hôtes du site apparaissent comme indisponibles.

**Correction :** examiner les relations de dépendance et identifier l'équipement amont. Les alertes d'enfants peuvent être contextualisées ou suppressées pendant l'indisponibilité du parent selon les règles, mais le problème initial doit rester visible. Le compte rendu doit distinguer la panne de l'équipement réseau de ses conséquences.

### Exercice 4 — Disque à 88 % d'occupation

**Situation :** le disque est à 88 % depuis deux jours ; le seuil standard de l'équipe est fixé à 90 %.

**Correction :** analyser la tendance, la capacité, la vitesse de croissance et l'espace nécessaire à l'application. Un volume qui grandit rapidement peut exiger une action avant 90 %. Définir un seuil suffisamment précoce pour permettre une intervention, utiliser une marge absolue et conserver une alerte de progression si la plateforme le permet.

### Exercice 5 — Alertes envoyées au mauvais groupe

**Situation :** les alertes de stockage sont envoyées uniquement au groupe réseau.

**Correction :** corriger l'association entre règle, objet, gravité et groupe responsable selon le processus de changement. Tester la notification sur un objet non critique, documenter les destinataires attendus et confirmer la réception. Ne pas envoyer de véritables alertes critiques à grande échelle pour tester une liste de contacts.

### Exercice 6 — Surveillance de certificat

**Situation :** un site est disponible, mais le certificat TLS expire prochainement.

**Correction :** la disponibilité HTTP n'implique pas que le certificat restera valide. Ajouter un contrôle de date d'expiration et définir un délai d'anticipation compatible avec l'approvisionnement et l'installation du nouveau certificat. Vérifier également la chaîne de confiance avec un test autorisé.

### Exercice 7 — UNKNOWN dans Nagios Core

**Situation :** un service remonte UNKNOWN après une modification du plugin.

**Correction :** vérifier la configuration de commande, les paramètres, les permissions, la sortie du plugin et ses dépendances. UNKNOWN signale que le contrôle ne peut pas déterminer correctement l'état. Il faut distinguer la panne potentielle de la cible et la défaillance du contrôle.

### Exercice 8 — Item sans valeur récente dans Zabbix

**Situation :** la dernière valeur d'un item remonte à quatre heures.

**Correction :** vérifier l'agent ou le canal de collecte, les files d'attente, les permissions, l'état de l'hôte et la configuration de l'item. Créer si nécessaire un contrôle de fraîcheur des données pour détecter ce cas. Une valeur ancienne ne doit pas être présentée comme actuelle.

### Exercice 9 — Alerte de maintenance planifiée

**Situation :** une alerte de redémarrage apparaît pendant une fenêtre de maintenance prévue.

**Correction :** vérifier que la fenêtre couvre le bon objet et la bonne période, puis contrôler que la suppression des alertes s'arrête à la fin prévue. Après la maintenance, exécuter les contrôles et vérifier la reprise de collecte. Les événements doivent être conservés selon la politique de rétention.

### Exercice 10 — Tableau de bord surchargé

**Situation :** l'écran montre quarante graphiques mais l'astreinte manque les deux problèmes critiques.

**Correction :** réorganiser l'écran par priorité et par service, présenter les problèmes actifs et les alertes sans propriétaire en premier, puis conserver des vues détaillées accessibles. Valider l'écran avec les utilisateurs qui vont réellement s'en servir. Ajouter davantage de widgets ne garantit pas davantage de visibilité.

## 16. Défi final corrigé — Déployer une supervision minimale d'un petit site

### Situation

Un site comprend un routeur, deux commutateurs, un serveur applicatif, une base de données et un stockage de sauvegarde. Les utilisateurs signalent parfois de la lenteur. L'équipe n'a pas encore de règles homogènes. Tu dois proposer un premier lot de supervision pour améliorer la détection sans générer de notifications inutiles.

### Travail demandé

1. choisir au moins deux contrôles adaptés à chaque composant ;
2. décrire la fréquence et le seuil de chaque contrôle, avec une justification ;
3. définir les liens de dépendance évidents ;
4. créer trois niveaux d'escalade et leurs destinataires par rôle ;
5. prévoir une règle de maintenance planifiée ;
6. définir les contrôles du serveur de supervision lui-même ;
7. proposer cinq indicateurs pour le bilan du premier mois ;
8. décrire comment tester la chaîne d'alerte sans perturber les utilisateurs.

### Correction détaillée

**Routeur :** joignabilité depuis un point pertinent, état des interfaces, erreurs et éventuellement taux d'utilisation. Les seuils doivent prendre en compte la capacité de l'interface et les valeurs normales du site. Les interruptions d'un routeur de distribution peuvent déclencher une cascade d'alertes ; déclarer la dépendance permet de présenter la cause amont avec ses impacts.

**Commutateurs :** état et erreurs des ports critiques, disponibilité de gestion et alimentation/température si les capteurs sont pris en charge. Un port utilisateur et un lien d'interconnexion ne doivent pas nécessairement avoir le même niveau de criticité. Vérifier la nomenclature des ports et associer les alertes aux liens ou services concernés.

**Serveur applicatif :** contrôle de la réponse HTTP avec code attendu, temps de réponse et certificat si applicable ; contrôle des ressources et des processus nécessaires. Le ping peut compléter mais ne prouve pas le bon fonctionnement de l'application. Le test HTTP doit être léger et ne pas créer de transactions métier non autorisées.

**Base de données :** disponibilité d'une connexion de vérification non destructive, nombre de connexions ou file d'attente, stockage et état de réplication si ce dernier est utilisé. Les contrôles doivent utiliser une identité de lecture dédiée et ne jamais exposer de requêtes ou secrets sensibles dans la sortie des alertes.

**Sauvegarde :** résultat et durée de la dernière tâche, âge de la dernière sauvegarde vérifiée, capacité disponible et test de restauration selon un calendrier convenu. Un serveur de sauvegarde accessible n'est pas la preuve que les données sont récupérables.

**Escalade :** un avertissement non critique crée une tâche pour l'équipe de jour ; une dégradation importante affectant des utilisateurs notifie immédiatement le responsable opérationnel ; une interruption d'un service critique suit la procédure d'astreinte. Les délais et destinataires doivent être définis par la politique interne. L'alerte doit rester attribuée à un responsable, avec une trace de l'accusé de réception.

**Maintenance :** enregistrer la fenêtre et le périmètre, prévenir les équipes, supprimer uniquement les notifications attendues sur les objets concernés, garder l'historique, puis contrôler le rétablissement des règles et le bon fonctionnement du site. Toute extension de la fenêtre exige une décision explicite.

**Supervision elle-même :** suivre son espace disque, les retards de collecte, les processus, les erreurs de base et un chemin de notification. Si possible, prévoir une vérification externe ou un mécanisme indépendant pour détecter qu'elle est totalement arrêtée.

**Bilan mensuel :** couverture des équipements et services, taux de disponibilité défini par une méthode écrite, alertes par sévérité, délais de prise en charge, principaux faux positifs et risques de capacité. Les nombres doivent être calculés à partir des événements et historiques et ne pas être estimés à partir d'une capture d'écran. Chaque indicateur doit déclencher une décision ou éclairer une tendance.

**Validation :** créer un contrôle de test identifié, déclencher une condition inoffensive, confirmer l'apparition de l'événement et la livraison de la notification, vérifier l'accusé de réception puis restaurer l'état initial. Consigner les résultats. Ne jamais provoquer une panne de production uniquement pour démontrer qu'une alerte marche.

### Barème indicatif

- 20 % : couverture et pertinence des contrôles ;
- 15 % : choix des mesures et des seuils justifiés ;
- 15 % : alertes actionnables et escalade claire ;
- 15 % : prise en compte des dépendances ;
- 15 % : sécurité et limites des privilèges ;
- 10 % : procédure de maintenance et vérification de retour ;
- 10 % : indicateurs et preuves du test.

Une proposition qui énumère de nombreuses métriques sans expliquer la réaction attendue ne satisfait pas l'objectif. Le résultat attendu est une supervision que l'équipe peut exploiter, entretenir et améliorer.

## 17. Checklist d'exploitation et de validation

Avant de déclarer le système de supervision prêt, vérifie les points suivants :

- les cibles et services sont validés par leur propriétaire ;
- les règles couvrent les risques majeurs et chaque alerte possède une action ou une justification ;
- les seuils ont été documentés et ne sont pas traités comme des valeurs universelles ;
- les dépendances et fenêtres de maintenance ont été testées ;
- les comptes disposent du moindre privilège et les secrets sont protégés ;
- les données de test sont clairement distinguées de la production ;
- un test contrôlé confirme la collecte, l'événement, la notification et le retour à l'état normal ;
- le dispositif de supervision est lui-même surveillé ;
- le volume d'historique et la rétention sont adaptés à la capacité et aux besoins ;
- une procédure de diagnostic permet de reprendre une alerte sans dépendre d'une seule personne ;
- les règles changées ont une trace, un responsable et une possibilité de retour arrière ;
- une revue périodique analyse les faux positifs, les faux négatifs, les alertes sans action et les nouveaux risques.

## 18. Synthèse et ressources officielles

La supervision est utile lorsqu'elle relie les mesures à une décision. Nagios Core s'appuie sur des hôtes, des services, des commandes, des plugins et des contacts ; Zabbix organise les collectes avec des items, des triggers, des modèles, des événements et des actions. Dans les deux cas, un bon résultat dépend surtout de la clarté du périmètre, de la qualité des mesures, de seuils justifiés, de règles de notification exploitables et d'une validation régulière du système de supervision.

Garde trois réflexes : ne confonds pas un signal réseau avec un service métier opérationnel, n'interprète jamais une donnée absente comme un zéro, et n'active pas une notification sans avoir défini qui l'utilisera et quelle action elle doit déclencher. La meilleure supervision est celle qui donne un avertissement assez tôt, au bon interlocuteur, avec suffisamment de contexte pour prendre une décision.

Ressources à consulter :
- Nagios Core, présentation : https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/about.html
- Nagios Core, définition des objets : https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/configobject.html
- Nagios Core, supervision des services publics : https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/monitoring-publicservices.html
- Zabbix, manuel actuel : https://www.zabbix.com/documentation/current/en/manual/
- Zabbix, triggers et notifications : consulter les chapitres Triggers, Events, Actions et Notifications du manuel correspondant à la version installée.
