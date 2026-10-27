# Threat Hunting avancé

> **Mise en contexte**
>
> Un SOC peut disposer d’un SIEM, d’un EDR et de nombreux tableaux de bord sans pour autant voir toutes les activités dangereuses. Certaines actions sont réalisées avec des outils légitimes, des comptes valides et des flux normalement autorisés. Une alerte peut ne jamais apparaître, être noyée dans le bruit ou manquer du contexte qui permet de la comprendre. Le Threat Hunting complète les détections existantes par une démarche proactive, structurée et reproductible : formuler une hypothèse, rechercher des preuves dans les données disponibles, examiner les explications alternatives et améliorer les contrôles.
>
> Ce cours vient après Red Team vs Blue Team vs Purple Team. Il met l’accent sur la recherche défensive, la qualité des journaux, l’analyse d’hypothèses, la détection des activités anormales, le suivi des résultats et l’apprentissage organisationnel. Les exercices utilisent des jeux de données synthétiques ou des environnements explicitement autorisés. Ils ne demandent ni accès à un système tiers, ni collecte de secrets réels, ni action intrusive.

## Objectifs et résultats attendus

À la fin du cours, vous saurez expliquer pourquoi le Threat Hunting n’est ni une simple recherche de mots-clés dans un SIEM ni un test d’intrusion déguisé. Vous pourrez concevoir une hypothèse de chasse liée à un risque métier, estimer la pertinence des données disponibles, construire une recherche de départ, mesurer ses limites et distinguer une absence de résultat d’une preuve d’absence d’activité. Vous saurez documenter la provenance des événements, contrôler les écarts d’horloge, examiner les explications bénignes, et transformer une découverte en détection réutilisable ou en action corrective.

Vous apprendrez à organiser un cycle de chasse, à choisir des sources selon les questions posées, à exploiter des concepts issus de MITRE ATT&CK sans confondre mapping et couverture réelle, à interpréter les anomalies comportementales et à tenir un registre des hypothèses testées. Vous saurez également définir les conditions d’arrêt, protéger les données, préserver les preuves nécessaires, communiquer les résultats et retester les améliorations.

Un hunt est réussi lorsqu’il produit une conclusion proportionnée aux preuves. Une chasse sans découverte peut être utile si la question était pertinente, les données disponibles, la recherche correcte et les limites explicitement notées. Inversement, une découverte spectaculaire mais non reproductible, mal attribuée ou obtenue hors du périmètre ne constitue pas un résultat de qualité.

## 1. Threat Hunting : définition et principes

Le Threat Hunting est une démarche proactive de recherche de comportements ou d’activités susceptibles d’indiquer un risque de sécurité. Le chasseur part d’une hypothèse, d’un renseignement, d’une observation ou d’un angle mort connu, puis interroge les données autorisées pour chercher des éléments qui la confirment ou la réfutent. Il ne remplace pas la détection automatisée. Il complète les règles existantes, explore les lacunes, aide à enrichir les signaux et améliore la compréhension du fonctionnement normal des systèmes.

La chasse se distingue de la surveillance continue. La surveillance traite les alertes et événements au fil de l’eau ; le Threat Hunting sélectionne une question particulière et organise une investigation limitée dans le temps. Les deux peuvent s’alimenter. Un hunt peut révéler un motif utile pour une règle de détection, tandis qu’une nouvelle alerte peut suggérer une question de chasse. La distinction reste utile pour planifier les ressources et mesurer les résultats.

La chasse n’est pas synonyme de recherche d’indicateurs connus. Une adresse IP, un hash ou un nom de fichier peut être utile, mais ces indicateurs vieillissent, changent et peuvent être partagés par plusieurs activités légitimes. Une recherche comportementale s’intéresse plutôt aux relations et au contexte : qui a effectué l’action, sur quel actif, à quelle heure, selon quelle séquence, avec quel niveau de privilège et avec quel résultat ? Le contexte réduit les conclusions hâtives.

Le Threat Hunting ne donne pas le droit d’examiner librement toutes les données d’une organisation. La mission est bornée par une autorisation, des objectifs, les règles de confidentialité et les accès de l’analyste. La recherche porte sur les sources nécessaires à l’hypothèse ; elle ne doit pas devenir une exploration générale des données privées. Les résultats doivent être conservés dans un espace contrôlé, avec une durée et un accès adaptés.

~~~text
Hypothèse de chasse
        |
Données autorisées et vérifiées
        |
Recherche initiale
        |
Contexte + explications alternatives
        |
Conclusion documentée
        |
Détection / correction / nouveau test
~~~

## 2. Différencier chasse, alerting, investigation et réponse à incident

Une alerte correspond à un signal produit par une règle, un modèle ou une détection. Le triage qualifie ce signal, enrichit le contexte et décide de la suite. L’investigation d’incident reconstruit ce qui a pu se passer, l’étendue, les actifs concernés et l’impact. Le Threat Hunting, lui, commence généralement par une question proactive, même en l’absence d’alerte. Il peut confirmer qu’une détection existante capte un comportement, mais il peut aussi viser une activité non couverte.

Ces activités sont complémentaires. Un hunt qui découvre une activité suspecte peut déclencher le processus d’incident. Ce processus doit ensuite prendre la direction opérationnelle de la réponse ; le chasseur ne doit pas improviser le confinement en dehors de son rôle. De la même manière, un incident déjà confirmé peut produire une leçon qui justifie un hunt plus large pour rechercher des traces semblables dans un périmètre autorisé.

Les frontières se définissent dans la procédure interne. Qui possède l’hypothèse ? Qui approuve l’accès aux sources ? Qui déclare un incident ? Qui autorise une mesure de confinement ? Qui a le droit de modifier une règle ou d’interroger une donnée sensible ? Ces réponses doivent être connues avant l’exercice. Le fait de découvrir un résultat inattendu ne transfère pas automatiquement ces responsabilités au chasseur.

~~~text
Alerte     : un signal doit être qualifié
Triage     : le signal est priorisé et enrichi
Hunt       : une hypothèse est recherchée proactivement
Incident   : l'événement est géré par les rôles prévus
Réponse    : les mesures sont décidées et suivies
Amélioration : détection et procédure sont revalidées
~~~

## 3. La boucle de chasse structurée

Une chasse solide suit un cycle. D’abord, le chasseur identifie une question importante et la formule en termes observables. Ensuite, il vérifie que les données nécessaires existent et que les conditions d’accès sont autorisées. Il établit une recherche initiale, examine le résultat, enrichit les événements et cherche des explications bénignes. Selon les preuves, il peut rejeter l’hypothèse, la renforcer, la reformuler ou déclarer le résultat non concluant.

La boucle doit être suffisamment petite pour être testable. Une question comme « sommes-nous compromis ? » est trop large. Une formulation telle que « des connexions interactives vers des serveurs critiques depuis des postes qui n’en administrent normalement aucun sont-elles visibles dans les événements de connexion de la dernière semaine ? » définit un domaine, une période et un type d’observation. Cette hypothèse demande encore une validation du contexte métier, mais elle est plus mesurable.

La recherche évolue après chaque résultat. La première requête peut servir à estimer le volume et la couverture. Une seconde ajoute des champs de contexte. Une troisième vérifie les exceptions autorisées et les faux positifs. Il faut conserver la version de chaque requête, les paramètres, la fenêtre temporelle, les filtres et les limites. Sans ces informations, un résultat ne peut être reproduit.

~~~text
1. Prioriser une question à risque
2. Formuler une hypothèse falsifiable
3. Vérifier l'autorisation et les sources
4. Établir la ligne de base
5. Chercher et enrichir les événements
6. Tester les explications alternatives
7. Conclure avec un niveau de confiance
8. Créer une action et retester
~~~

## 4. Formuler une bonne hypothèse

Une bonne hypothèse annonce ce qu’on s’attend à observer si le scénario est vrai, et ce qui pourrait la contredire. Elle indique l’actif ou la population, la période, le comportement, la source et les limites. Elle peut être conçue à partir du renseignement sur la menace, d’une faiblesse de journalisation, d’un signal faible, d’une nouvelle architecture ou d’une découverte en réponse à incident.

Exemple : « Pendant les sept derniers jours, les comptes de service qui ont ouvert des sessions interactives sur des serveurs de laboratoire sont-ils différents des comptes et plages horaires établis dans la ligne de base ? » Cette question n’accuse personne. Elle demande de comparer des événements et de comprendre les exceptions. Avant de rechercher, il faut identifier les comptes concernés et les opérations administratives légitimes prévues.

Un mauvais exemple serait « trouver les comptes suspects ». Il manque une définition du suspect, une période, une population, un champ et une règle d’interprétation. Un autre mauvais exemple serait « rechercher une menace avancée ». L’expression ne précise pas le comportement ni la preuve attendue. L’hypothèse doit pouvoir être raffinée sans perdre la question initiale.

L’hypothèse est accompagnée d’une justification : quel risque métier la rend prioritaire, quel événement serait observé, quelles sources sont nécessaires et quelle décision pourrait changer selon le résultat. Une chasse sans conséquence possible pour la décision de sécurité devient une collecte coûteuse. Il est acceptable de lancer un travail exploratoire, mais il faut annoncer ce statut et éviter de lui attribuer une conclusion forte.

~~~text
Hypothèse : événement + population + période + contexte
                |
                v
Prédiction observable
                |
                v
Source nécessaire et niveau de confiance
                |
                v
Décision qui changera selon le résultat
~~~

## 5. Prioriser les chasses par le risque

Toutes les hypothèses ne méritent pas la même priorité. Il faut considérer l’impact potentiel, l’exposition, la vraisemblance, les actifs concernés, les contrôles connus, le niveau de confiance du renseignement et la faisabilité de la recherche. Une question peut être critique même si les signaux attendus sont rares. À l’inverse, une anomalie très fréquente peut avoir un intérêt faible si elle ne débouche sur aucune décision utile.

La disponibilité des données fait partie de la priorité. Si le comportement exige une télémétrie absente, le travail initial peut être un projet de collecte plutôt qu’une chasse directe. Le registre indique cette dépendance. Ne pas voir un événement dans une source qui ne l’enregistre pas ne constitue pas une preuve rassurante. Il faut distinguer le risque, la capacité de l’observer et la capacité de le traiter.

Le chasseur peut définir une liste de sujets selon les risques prioritaires : comptes privilégiés, changements inhabituels sur les mécanismes d’audit, connexions à distance, accès à des partages sensibles, communications rares entre zones, comportement anormal d’une identité de service ou changements de configuration cloud. Le choix concret dépend des actifs, des contraintes, des journaux et des risques métier. Il ne s’agit pas de lancer toutes ces recherches simultanément.

Une matrice de priorisation est un outil de discussion et non une vérité mathématique. Les scores doivent être expliqués et revus avec les propriétaires de risque. Quand un scénario peut avoir des conséquences opérationnelles, comme dans l’OT/ICS, le risque de la chasse elle-même doit être pris en compte. La méthode la moins intrusive capable de répondre à la question est préférable.

~~~text
Priorité d'une chasse
  = importance métier
  + pertinence du renseignement
  + exposition et lacune de détection
  + capacité de collecter une preuve
  - coût et risque opérationnel
~~~

## 6. Préparer les données avant toute recherche

Les journaux ne sont utiles que si leur origine, leur couverture et leur qualité sont comprises. Le chasseur doit savoir quel système les produit, quels événements sont enregistrés, si la collecte est complète, comment les champs sont normalisés, quel fuseau ou référentiel temporel est appliqué, combien de temps les données sont conservées et qui peut y accéder. Les sources peuvent inclure des journaux d’identité, d’endpoint, réseau, DNS, proxy, pare-feu, service cloud, application, système industriel ou gestion de changement.

La collecte et la recherche sont deux choses différentes. Un SIEM peut afficher beaucoup de données tout en manquant les événements utiles. Une source peut avoir une période de rétention trop courte pour l’hypothèse. Certains champs peuvent être présents dans un système mais supprimés lors de l’ingestion. Des horloges différentes peuvent inverser l’ordre apparent de deux événements. Le chasseur documente ces limites avant d’interpréter les résultats.

Un inventaire des données doit associer chaque source à des événements, champs, période de disponibilité, taux d’ingestion, propriétaire, sensibilité et limites. Une mesure de qualité peut comparer les événements attendus avec les événements reçus sur une population de référence. Le volume brut n’est pas une mesure suffisante : il peut augmenter sans améliorer l’observabilité.

La source et le pipeline doivent être traités comme des composants de sécurité. Les journaux utiles à l’investigation doivent être protégés contre l’altération et la suppression non autorisées, avec des accès et une durée de conservation adaptés. Les mécanismes d’intégrité, les contrôles d’accès et la séparation de l’administration des journaux aident à préserver la confiance dans les preuves. Le niveau de protection varie selon le risque, les obligations et les capacités.

~~~text
Source -> Agent/collecteur -> Transport -> Normalisation -> Stockage
  |             |               |              |              |
Couverture    pertes          délai          schéma        rétention
  \______________ qualité et provenance des données __________/
                              |
                              v
                    Recherche reproductible
~~~

## 7. Les champs et le contexte nécessaires

Une recherche se construit autour de champs réellement disponibles. Les éléments habituels peuvent inclure l’horodatage, l’acteur, le compte, l’appareil, le processus, l’action, la ressource, l’adresse source, la destination, le protocole, le résultat et l’origine du journal. Tous les systèmes n’ont pas tous ces champs ; certains identifiants changent selon les plateformes. Le chasseur décrit les correspondances de normalisation plutôt que de supposer qu’un même nom signifie partout la même chose.

Le contexte peut provenir de sources auxiliaires : inventaire des actifs, gestion des identités, registre des changements, horaires de maintenance, CMDB, gestion des tickets, correspondance des comptes de service et niveaux de criticité. Ce contexte est souvent essentiel pour distinguer une activité rare mais autorisée d’une activité véritablement anormale. La date de mise à jour de la référence doit être connue ; une CMDB ancienne peut créer beaucoup de conclusions erronées.

Les identités doivent être interprétées correctement. Un compte technique peut représenter un service, une tâche planifiée, un utilisateur ou une intégration tierce. L’acteur visible dans un journal peut être le compte délégué plutôt que l’utilisateur initial. Les champs d’impersonation, d’initiateur ou de délégation doivent être préservés quand la plateforme les fournit. Le rapport précise les limites d’attribution lorsqu’un identifiant ne permet pas d’identifier une personne.

Les données sensibles sont filtrées et utilisées avec parcimonie. Une chasse ne nécessite pas nécessairement le contenu des communications, les documents de l’utilisateur ou les secrets d’authentification. Un identifiant d’événement, une heure, une ressource et un résultat peuvent suffire. Le principe de minimisation protège les employés, les clients et l’organisation, tout en rendant le dossier plus facile à partager avec les personnes habilitées.

## 8. Ligne de base et activité normale

Une anomalie n’est pas automatiquement malveillante. Elle indique une différence par rapport à une référence. Pour interpréter cette différence, il faut comprendre la saisonnalité, les heures de travail, les fenêtres de maintenance, les changements de service, les tâches planifiées, les tests, les migrations et les opérations exceptionnelles. Une ligne de base peut être statistique, descriptive, historique ou définie par une politique.

La ligne de base doit être contextualisée et datée. Les habitudes changent lorsqu’une équipe migre vers le cloud, qu’un compte de service est remplacé ou qu’une application se met à jour. Une référence figée peut qualifier une activité légitime de suspecte, tandis qu’un apprentissage automatique non surveillé pourrait intégrer un comportement indésirable dans la norme. Les changements importants doivent être documentés et validés, pas absorbés silencieusement.

Il existe des distributions normales, des exceptions récurrentes et des événements rares attendus. Une connexion d’un administrateur à une heure inhabituelle peut être approuvée dans un ticket de maintenance. Un processus rarement observé peut être un déploiement logiciel légitime. Une activité habituelle n’est cependant pas forcément sûre : un abus peut imiter un comportement normal. Il faut examiner les relations et les changements de contexte plutôt que de s’appuyer uniquement sur la fréquence.

Les tests synthétiques aident à vérifier la ligne de base sans collecter de vraies données sensibles. Ils doivent être clairement étiquetés pour ne pas polluer les métriques de production. L’équipe conserve les règles de filtrage, les populations et la date de calcul. Quand une recherche ne produit aucun résultat, la qualité de la ligne de base et la couverture des sources doivent être vérifiées avant de conclure.

~~~text
Événements observés
      |
Contexte métier + calendrier + changements
      |
Ligne de base datée
      |
Écarts
  |          |
attendus   inexpliqués
  |          |
documenter  enrichir puis investiguer
~~~

## 9. Requêtes de chasse : principes de construction

Une requête doit être lisible, limitée à un intervalle de temps et testée d’abord sur un volume gérable. Commencez par un filtre large pour vérifier la disponibilité des champs et le volume, puis ajoutez une condition à la fois. Si la recherche s’appuie sur une jointure, vérifiez que les identifiants ont le même sens et que les relations temporelles sont cohérentes. Les résultats doivent être triés selon une clé qui facilite l’examen des séquences.

La logique peut être décrite en pseudo-SQL sur des événements synthétiques. Exemple conceptuel : sélectionner les événements de connexion où le type d’acteur est « compte de service », l’accès est interactif et la cible est un serveur de laboratoire ; joindre ensuite le registre des exceptions approuvées. Il s’agit ici d’une illustration de pensée analytique, pas d’une requête universelle. Les champs, fonctions et formats doivent être adaptés au moteur réel et validés avec l’équipe qui en assure l’exploitation.

Une recherche peut comprendre des agrégations : nombre d’identités distinctes par hôte, fréquence par fenêtre horaire, destinations jamais observées dans la période de référence, ou séquence de changements rapprochés. Il faut toujours contrôler les biais de population. Si un hôte envoie beaucoup plus de logs que les autres, le volume peut dominer l’analyse. Si un événement est réémis plusieurs fois, le comptage peut surestimer l’activité. Le dédoublonnage doit respecter le modèle de données et ne pas supprimer des événements qui témoignent de répétitions utiles.

Les requêtes sont du code opérationnel : versionnez-les, revoyez les droits d’accès, expliquez les coûts, définissez les paramètres et documentez les limites. Une requête coûteuse peut affecter l’outil ou le service d’analytique. Définissez une fenêtre et une limite avant d’élargir la recherche, surtout dans de grands environnements. Les optimisations doivent préserver la sémantique ; réduire le temps d’exécution en omettant la moitié des événements peut produire une conclusion fausse.

~~~text
Étape A : compter les événements dans la période
Étape B : vérifier les champs obligatoires et les valeurs nulles
Étape C : appliquer la condition comportementale
Étape D : ajouter le contexte métier et les exceptions
Étape E : examiner les échantillons représentatifs
Étape F : vérifier les faux positifs et les angles morts
~~~

## 10. Corrélation temporelle et reconstruction des séquences

La corrélation recherche des relations entre événements. Une ouverture de session, un changement de rôle et un accès à une ressource peuvent être normaux chacun pris isolément ; leur association dans une courte fenêtre temporelle peut mériter une analyse. Il ne faut toutefois pas supposer une causalité uniquement parce que deux événements sont proches. Les identifiants, les actifs, les relations d’identité et les dépendances d’application doivent soutenir le lien.

Pour reconstruire une séquence, commencez par normaliser les timestamps. Notez le fuseau et l’écart des sources si les systèmes ne sont pas synchronisés. Conservez une chronologie brute puis créez une chronologie analytique où les événements sont classés et reliés avec des références à leur source. Les événements qui ont une heure incertaine doivent être marqués comme tels. Il ne faut pas réécrire l’heure source pour que la séquence semble cohérente.

Une séquence utile inclut le déclencheur possible, l’identité, l’hôte, la ressource, l’activité intermédiaire et les résultats. Les chaînes d’événements doivent être justifiées par des relations vérifiables : identifiant de session, compte, identifiant de processus, jeton de corrélation ou réseau source. Si le lien est seulement probable, le rapport le qualifie comme tel.

Les agrégations de séquence peuvent révéler des motifs : une identité qui accède à plusieurs hôtes dans un ordre rare, une série de changements d’accès en dehors des fenêtres habituelles ou une activité réseau inhabituelle après une connexion. Les motifs servent à orienter l’enquête, pas à affirmer automatiquement une compromission. Il faut chercher les tickets, déploiements, opérations légitimes et dépendances susceptibles d’expliquer le résultat.

~~~text
10:01:02 Authentification réussie (compte A)
       |
10:02:14 Changement de rôle dans le service
       |
10:04:40 Accès à la ressource laboratoire
       |
10:05:10 Export d'audit associé
       |
       v
Vérifier acteur, session, ticket et résultat de chaque événement
~~~

## 11. Enrichissement, triage et hypothèses alternatives

Un résultat inhabituel doit être enrichi avant d’être qualifié. Les éléments de contexte incluent la criticité de l’actif, le rôle du compte, le ticket de changement, la fenêtre de maintenance, l’emplacement réseau, la version du système, l’historique et la relation avec d’autres événements. Le but est d’augmenter la qualité de la décision sans collecter des données non nécessaires.

Les hypothèses alternatives sont essentielles. Une tâche planifiée, un déploiement, une mise à jour, un audit, une intervention de support et une automatisation peuvent expliquer un comportement rare. La présence d’une explication plausible ne signifie pas qu’elle est vraie ; il faut la confirmer par un ticket, une fenêtre approuvée, un propriétaire ou une trace. De même, l’absence de ticket ne prouve pas en soi une activité malveillante : les procédures peuvent être incomplètes.

Les conclusions peuvent être classées avec des états explicites : confirmé par preuve, probable mais incomplet, expliqué par un changement autorisé, non concluant faute de données, ou réfuté par une preuve contraire. Une simple couleur dans un tableau de bord ne doit pas masquer le niveau de certitude. Le degré de confiance dépend de la qualité de la source, de la cohérence des identifiants, de la couverture temporelle et des explications alternatives vérifiées.

La chasse doit s’arrêter ou être transmise lorsque le résultat dépasse le mandat, révèle un incident possible ou nécessite des actions opérationnelles que le chasseur n’est pas autorisé à entreprendre. Le processus d’incident prend alors le relais. La chasse conserve les références utiles, sans perturber les systèmes ni multiplier les accès non nécessaires.

~~~text
Résultat inhabituel
      |
Enrichir l'actif, l'identité et le changement
      |
Lister au moins une explication alternative
      |
Vérifier les preuves pour / contre
      |
+----------------------+-----------------------+
| confirmé / probable  | expliqué / non concluant |
| transmettre selon    | documenter les limites   |
| procédure d'incident | et améliorer les sources |
+----------------------+-----------------------+
~~~

## 12. MITRE ATT&CK et modèles défensifs actuels

MITRE ATT&CK peut organiser les hypothèses et relier les comportements aux stratégies de détection. Le choix d’une technique doit être fondé sur la description actuelle et sur une correspondance réelle avec le comportement étudié. Il ne suffit pas qu’un nom ressemble à celui d’une activité observée. Le rapport note la version de la matrice ou la date de consultation, car les techniques, les objets et les recommandations évoluent.

ATT&CK v18, publié en octobre 2025, a apporté des changements importants à la partie défensive : les anciennes pages Data Sources ont été dépréciées et les Detection Strategies, Analytics et Data Components jouent un rôle plus central dans la description de la détection. Il faut donc éviter de bâtir un programme neuf uniquement sur l’ancienne liste de sources. Consultez le modèle de données, les stratégies de détection et les composants pertinents dans la version en vigueur, puis documentez la façon dont les événements de l’organisation satisfont réellement les besoins.

ATT&CK est un vocabulaire, pas un moteur automatique de chasse. Une stratégie de détection peut suggérer les événements et la logique à examiner, mais la capacité réelle dépend des journaux disponibles, de leur schéma, de l’architecture, des règles locales et du niveau de traitement opérationnel. Un mapping n’est pas une preuve qu’une technique est détectée. Une preuve exige un essai, une observation et des conditions explicites.

Utilisez le framework pour prioriser, expliquer et communiquer. Ne forcez pas tous les résultats à entrer dans une technique. Certaines anomalies résultent d’une erreur d’administration, d’une dérive de configuration ou d’un défaut d’instrumentation. Le rapport peut indiquer une relation à ATT&CK si elle est justifiée, tout en précisant que la conclusion porte sur les événements observés et non sur l’activité d’un groupe particulier.

~~~text
Risque + hypothèse
       |
Technique / sous-technique pertinente
       |
Stratégie de détection et composantes requises
       |
Sources réellement disponibles
       |
Test, résultat et niveau de preuve
       |
Recommandation et date de revalidation
~~~

## 13. Chasse sur les identités et les accès

Les identités constituent un contexte central de la plupart des environnements modernes. Une chasse peut étudier des sessions inhabituelles, des changements de groupe, des comptes de service utilisés de manière interactive, des erreurs d’authentification récurrentes ou une activité privilégiée hors des fenêtres habituelles. Ces comportements doivent être interprétés avec soin : les tâches d’automatisation, les astreintes et les changements validés produisent aussi des événements atypiques.

Commencez par identifier la population de comptes et les rôles. Une comparaison n’a de sens que si le rôle attendu est correctement renseigné. Les comptes techniques partagés rendent parfois l’attribution difficile ; le résultat doit noter cette limite et proposer une amélioration de la traçabilité. Les champs d’initiateur, de délégation et de cible doivent être examinés lorsque le système les fournit.

Exemple de chasse : examiner les événements d’attribution de rôle durant une période donnée, joindre les demandes de changement approuvées et isoler les événements pour lesquels le rôle, l’acteur ou la fenêtre ne correspondent pas au dossier. Ce n’est qu’un signal d’investigation. Il faut vérifier l’approbation, le propriétaire de l’application, la source de l’action et la validité du ticket. Une anomalie peut refléter un processus de changement insuffisant plutôt qu’un adversaire.

Une chasse d’identité doit respecter les droits d’accès et la confidentialité. Elle ne doit pas extraire les secrets des comptes, collecter le contenu des communications ou surveiller un employé en dehors des politiques et autorisations applicables. Si une enquête exige des données sensibles, les rôles autorisés et la finalité doivent être clarifiés avant de poursuivre.

## 14. Chasse endpoint et comportement des processus

Les journaux endpoint peuvent inclure le démarrage des processus, leur parent, l’utilisateur, la signature, le chemin, les paramètres d’exécution, les événements de sécurité et la santé de l’agent. Leur qualité varie selon les plateformes et les configurations. Il faut savoir quels champs sont collectés, s’ils sont disponibles partout, combien de temps ils sont conservés et si les agents transmettent les données attendues.

Une chasse comportementale peut chercher des relations inhabituelles entre un parent et un enfant, un binaire rarement utilisé par une équipe donnée, une tâche administrative lancée depuis un compte utilisateur standard ou un changement de politique de sécurité hors d’une fenêtre approuvée. Le rare n’est pas automatiquement malveillant. Le chasseur compare les rôles, le contexte de l’hôte, le processus de changement et le comportement des systèmes similaires.

Une ligne de base d’exécutables légitimes doit tenir compte des mises à jour, des tâches planifiées, des outils de support et des changements du parc. Il faut éviter les listes d’autorisation éternelles qui font disparaître la visibilité. Les exclusions sont liées à une raison, une portée, une échéance et un propriétaire. Le but est de préserver l’observabilité plutôt que de faire disparaître les événements bruyants.

Les exemples de requêtes restent des modèles conceptuels adaptés aux champs synthétiques. Une recherche de processus ne doit pas se transformer en instructions pour exécuter une charge ou contourner un contrôle. Les tests utilisent un événement témoin autorisé ou des enregistrements artificiels, puis vérifient la source, le mapping, la détection et la qualité du triage.

~~~text
Processus observé
   |
Parent + utilisateur + hôte + heure
   |
Contexte du rôle et de l'installation
   |
Ticket de changement et ligne de base
   |
Évaluation des explications alternatives
   |
Détection, documentation ou clôture justifiée
~~~

## 15. Chasse réseau et DNS

La télémétrie réseau peut comprendre des métadonnées de flux, des journaux de pare-feu, DNS, proxy, VPN, passerelles cloud et capteurs spécialisés. Elle ne donne pas nécessairement le contenu des communications et ce n’est pas un défaut si les métadonnées suffisent à répondre à la question. La collecte de contenu peut accroître les risques de confidentialité et de stockage ; elle doit être justifiée et autorisée séparément lorsque c’est nécessaire.

Les questions utiles concernent des relations inhabituelles : un poste de laboratoire qui communique avec une destination rare, une série de connexions à des hôtes auxquels l’actif n’accède normalement pas, des volumes inattendus au regard du rôle, ou un changement soudain du profil DNS. Les signaux sont contextualisés avec le rôle de l’actif, son logiciel, la maintenance, les destinations approuvées et les changements récents. Un domaine rare peut être un service légitime nouvellement déployé.

Les analyses de fréquence doivent traiter les biais. La popularité d’un nom de domaine dépend de la taille de l’organisation, des caches, des appareils et de la durée de référence. Les résolutions négatives, le cache local, les clients qui ne passent pas par le résolveur central et les flux chiffrés peuvent limiter la visibilité. Le rapport indique ces angles morts plutôt que de déduire une absence d’activité à partir d’une source incomplète.

Pour les environnements OT/ICS, une chasse réseau doit être coordonnée avec les ingénieurs du procédé. Les relations entre équipements et les communications prévues doivent être documentées. Les scans actifs ou les changements de configuration ne sont pas nécessaires à une chasse basée sur les journaux et peuvent être dangereux. La méthode privilégie l’observation passive autorisée, la maquette et les changements contrôlés.

~~~text
Flux / DNS / pare-feu
        |
Source, destination, protocole, heure, volume
        |
Profil normal de l'actif
        |
Destination ou séquence atypique
        |
Vérifier changement, service tiers et inventaire
        |
Hypothèse confirmée, réfutée ou non concluante
~~~

## 16. Chasse cloud, SaaS et conteneurs

Les environnements cloud comportent des événements de plan de contrôle, d’accès, de configuration, de stockage, de réseau et d’orchestration. Les journaux doivent être activés selon le risque et acheminés vers un espace de surveillance dont l’administration est suffisamment séparée de celle des ressources observées. Une chasse sur les changements d’accès ou la modification de la journalisation n’est efficace que si les événements correspondants existent et ne peuvent pas être effacés sans trace.

Les cas d’usage peuvent porter sur des rôles privilégiés nouveaux, des changements de règles d’accès, la modification d’un service de collecte, l’accès à un stockage depuis une identité inattendue ou une dérive de configuration Kubernetes. Le chasseur compare les événements au registre de changement, aux pipelines de déploiement et aux responsables de service. Une automatisation d’infrastructure peut faire plusieurs changements à la suite ; le contexte du pipeline est nécessaire pour interpréter correctement la séquence.

La collecte doit distinguer les événements du plan de contrôle et ceux de la charge de travail. Une API cloud peut enregistrer la création d’une ressource alors qu’un agent sur la machine enregistre son activité locale. Les deux sources répondent à des questions différentes. Le chasseur documente la couverture de chaque source et n’infère pas l’absence de comportement local à partir d’un audit du plan de contrôle seul.

Les conteneurs et clusters demandent des références temporelles et des identifiants stables. Les pods peuvent être éphémères ; il faut relier le nom, l’identifiant, le nœud, l’image, le déploiement et le compte de service. Si une ressource a été supprimée, un journal d’audit ou un inventaire peut être la seule trace. Les recherches doivent respecter les capacités de la plateforme et ne pas entraîner une collecte imprévue de données de production.

## 17. Living off the Land et activité légitime détournée

Les activités Living off the Land (LOTL) tirent parti d’outils ou fonctions légitimes du système. Elles rendent l’analyse difficile, car les mêmes composants sont utilisés par les administrateurs et les applications normales. Les recommandations conjointes de CISA et d’autres agences soulignent l’importance de journaux détaillés, de données centralisées, de lignes de base comportementales et de corrélation. La collecte doit rendre observables des comportements pertinents sans se résumer à une liste statique d’outils.

La chasse commence par un contexte : quelles équipes utilisent ces outils, sur quels hôtes, à quelles heures et dans quelles procédures ? Ensuite, elle recherche des différences significatives : utilisateur inhabituel, hôte qui n’a normalement pas ce rôle, argument inattendu, séquence rare, destination inhabituelle ou action suivie d’un changement sensible. Aucune caractéristique seule ne prouve une activité malveillante. Une conclusion crédible assemble plusieurs pièces et vérifie les explications alternatives.

La qualité des journaux est déterminante. Les configurations par défaut peuvent ne pas inclure les détails nécessaires. Il faut prioriser les événements selon le risque et s’assurer qu’ils sont centralisés, protégés et conservés assez longtemps. La collecte détaillée peut accroître le coût et le volume ; le choix doit mettre en balance le risque, la valeur de détection, la confidentialité, la capacité de stockage et la faculté d’enquêter.

Le chasseur évite de transformer la chasse en recherche aveugle de commandes. Un exécutable légitime utilisé par un administrateur dans un contexte prévu peut être parfaitement normal. Une recherche doit comparer l’acteur, la ressource, la séquence et la fenêtre de changement. Lorsqu’un comportement suspect est découvert, l’équipe documente les faits et transmet au processus d’incident selon la procédure.

~~~text
Outil système légitime
        |
Contexte normalement autorisé
        |
Acteur / hôte / séquence / destination
        |
Écart par rapport à la ligne de base
        |
Ticket, changement et preuve corroborante
        |
Hunt approfondi ou décision de clôture
~~~

## 18. Hypothèses statistiques et biais analytiques

La rareté est une propriété statistique, pas un jugement de sécurité. Un événement qui apparaît une fois peut être parfaitement légitime ; un événement fréquent peut être préoccupant s’il est devenu habituel à la suite d’une compromission. Les mesures de fréquence doivent être interprétées avec le volume, la population, la période, la saisonnalité et les changements de service.

Les biais peuvent venir des sources elles-mêmes. Si seulement certains serveurs envoient leurs journaux, la chasse donne une vision incomplète. Si un outil de collecte a changé de version, les champs et le volume peuvent changer. Si l’analyste choisit uniquement la fenêtre où le résultat paraît significatif, il risque de confirmer l’hypothèse sans chercher à la réfuter. Le rapport décrit le choix de la période, les exclusions et les contrôles de qualité.

Les hypothèses alternatives doivent être formulées explicitement. Le chasseur cherche des éléments qui contredisent l’explication initiale, pas seulement des signes qui lui donnent raison. Si la recherche trouve une connexion rare, vérifier une maintenance, un déploiement, une nouvelle dépendance, une automatisation et une attribution d’identité est essentiel. Il ne faut pas sélectionner arbitrairement une seule explication parce qu’elle convient au récit.

Les modèles statistiques et les approches de détection par anomalie peuvent réduire le travail manuel, mais ils dépendent des données et des paramètres. Les seuils doivent être testés, suivis et réévalués. Un modèle qui se met à apprendre sans gouvernance peut normaliser une activité indésirable ou déclencher trop d’alertes après un changement bénin. La décision finale repose sur des preuves et un contexte compris, pas sur le score seul.

~~~text
Signal statistique
      |
Qualité des données
      |
Population et période comparables ?
      |
Changements légitimes vérifiés ?
      |
Preuves pour et contre l'hypothèse
      |
Conclusion avec limites et confiance
~~~

## 19. Protéger les preuves et les données

Une chasse peut toucher des informations sensibles : identifiants, adresses, journaux d’accès, noms d’utilisateur, métadonnées de clients, architecture et événements métiers. Les données doivent être limitées à la finalité autorisée. L’analyste doit éviter d’exporter des dossiers complets si quelques champs suffisent, et il ne doit pas extraire de secrets ou de contenus personnels sans justification et autorisation spécifique.

Les résultats doivent porter des métadonnées minimales : identifiant de chasse, auteur, période, requête versionnée, sources, filtres, date d’extraction et destination sécurisée. Si l’intégrité est nécessaire, le processus peut enregistrer un hash ou un mécanisme de stockage immuable selon les moyens de l’organisation. Un hash seul ne garantit pas la provenance ; il faut aussi documenter la source et le traitement.

L’accès aux données et aux exports doit suivre le principe du moindre privilège. Les autorisations de recherche sont approuvées selon le rôle, et la durée de rétention correspond à la finalité et aux obligations. Les rapports partagés doivent distinguer le résumé exécutif de la preuve technique restreinte. La suppression des résultats temporaires suit une procédure connue, et les exceptions de conservation sont justifiées.

Si le chasseur identifie un incident possible, il conserve les références nécessaires pour la passation et respecte le processus de réponse. Il évite de modifier les systèmes ou les journaux pour « vérifier » un comportement. Les actions susceptibles de détruire une preuve sont décidées par les responsables habilités, avec une attention particulière à la continuité métier.

## 20. Rendre le résultat exploitable

Chaque hunt doit se terminer par un état, une justification et une action éventuelle. Les états peuvent inclure hypothèse confirmée, hypothèse réfutée, piste expliquée par un changement approuvé, résultat non concluant faute de données, ou anomalie nécessitant une investigation d’incident. Une chasse sans découverte peut produire un résultat utile si les données couvrent réellement la question et que la requête est correcte.

Le rapport succinct décrit la question, la priorité, le périmètre, les sources, les versions, la période, les requêtes, les résultats, les exemples pertinents, les explications alternatives, les limites et les recommandations. Il distingue le constat de l’interprétation. Une affirmation sur une identité ou un hôte doit être soutenue par les champs et relations vérifiés ; si l’attribution est incertaine, elle doit rester qualifiée.

Les découvertes répétables peuvent devenir une règle de détection, un tableau d’observation, un playbook de triage ou une amélioration de collecte. Le nouveau contrôle doit être testé sur des cas positifs et négatifs, mis en revue, versionné et suivi après déploiement. Une découverte confirmée peut déclencher une réponse, mais la décision revient à l’autorité prévue dans le processus d’incident.

Le registre des chasses suit l’effort, le résultat et l’amélioration. Le volume d’alertes nouvelles n’est pas le seul indicateur. On peut mesurer le nombre d’hypothèses testées avec données suffisantes, le temps de préparation, la part des résultats reproductibles, les améliorations de couverture, le nombre d’actions fermées par preuve et le taux de régression des tests négatifs. Ces métriques doivent être définies avant la mesure.

~~~text
Résultat de chasse
   |-- hypothèse confirmée -> procédure d'incident si nécessaire
   |-- hypothèse réfutée -> documenter la preuve
   |-- signal légitime -> mise à jour de la ligne de base
   |-- donnée insuffisante -> action de collecte
   |-- motif reproductible -> règle ou playbook testé
                         |
                         v
                    Retest daté
~~~

## 21. Organiser un programme de Threat Hunting

Un programme durable combine priorités métier, demandes du SOC, renseignement, incidents passés, évolutions d’architecture et lacunes de télémétrie. Il doit établir une cadence adaptée aux risques plutôt que multiplier les chasses pour remplir un tableau de bord. Les sujets sont sélectionnés selon leur valeur, leur faisabilité, leur coût, les données disponibles et les actions qui pourraient en découler.

La bibliothèque de hunts contient les hypothèses, les requêtes, les paramètres, la version des sources, les champs requis, les résultats connus, les faux positifs, les cas de test et les limites. Elle est versionnée et revue comme du contenu opérationnel. Les changements de schéma, de plateforme, d’identité ou de politique doivent déclencher une vérification des recherches qui dépendent de ces données.

Les rôles doivent être explicites : sponsor ou propriétaire de risque, responsable du programme, chasseur, responsable des sources, analyste SOC, ingénierie de détection et gestion d’incident. L’analyste ne doit pas être seul responsable de la décision de risque. Une découverte importante suit les procédures d’escalade existantes et les résultats techniques restent accessibles aux personnes autorisées.

Le programme doit également suivre le temps consacré aux chasses, la disponibilité des sources, la dette de journalisation et le taux de retest. Une chasse abandonnée parce que la donnée manque n’est pas perdue si elle produit un plan clair d’amélioration de la collecte. Il faut séparer l’absence de résultat dû à l’hypothèse de celle due à l’observabilité.

~~~text
Backlog de risques
      |
Priorisation conjointe
      |
Bibliothèque de hunts versionnés
      |
Exécution, analyse et revue
      |
Détection ou collecte améliorée
      |
Retest et réévaluation du backlog
~~~

## 22. Travaux pratiques guidés

Tous les TP utilisent des données synthétiques et des systèmes de laboratoire explicitement autorisés. Les champs cités sont illustratifs et doivent être adaptés au schéma réel ; aucun test ne nécessite de scanner ou d’attaquer une cible.

### TP 1 — Formuler une hypothèse et vérifier les sources

**Situation.** Une équipe veut examiner si les comptes de service sont utilisés pour des sessions interactives sur des serveurs de laboratoire. Les données disponibles comprennent un journal de connexion synthétique, un inventaire d’actifs et un registre de changements autorisés.

**Travail demandé.** Formulez l’hypothèse, définissez la période, les champs nécessaires, les sources, les exceptions à vérifier et le critère de conclusion. Précisez comment éviter de considérer automatiquement chaque session inhabituelle comme un incident.

**Correction attendue.** L’hypothèse spécifie les comptes de service, les serveurs de laboratoire, une période précise et le type de session. Les champs sont l’acteur, le système, l’heure, le type de connexion, le résultat et l’origine du journal. L’inventaire précise les rôles, et le registre de changements permet de comparer l’activité avec une opération approuvée. Un écart est un point à investiguer, non une confirmation automatique de malveillance. La conclusion distingue les cas expliqués, les anomalies soutenues par une preuve, et les résultats non concluants dus à une source incomplète.

**Barème sur 20.** Hypothèse falsifiable : 4 points. Sources et champs : 4 points. Contexte et exceptions : 4 points. Critères d’interprétation : 4 points. Limites explicitement décrites : 4 points.

### TP 2 — Analyser une suite d’événements synthétiques

**Données.** À 09:12:00, un compte de service s’authentifie sur un serveur de laboratoire. À 09:14:10, un événement enregistre une modification de rôle. À 09:17:22, le même identifiant de session accède à une ressource de test. À 09:19:00, le journal d’audit confirme la lecture de la ressource. Le registre des changements contient une maintenance approuvée de 09:00 à 09:30, mais le compte responsable noté dans le ticket diffère du compte observé.

**Travail demandé.** Construisez une chronologie, listez au moins trois explications alternatives, identifiez la preuve supplémentaire qui serait la plus utile et choisissez un statut de résultat provisoire.

**Correction attendue.** La chronologie relie les événements par l’identifiant de session tout en conservant les timestamps source. Le ticket explique la fenêtre, mais la discordance entre le compte observé et le compte déclaré n’est pas résolue. Des hypothèses alternatives comprennent une tâche automatisée exécutée par un compte technique, une délégation non documentée ou une erreur d’attribution dans le registre. La preuve la plus utile est une trace d’exécution de la maintenance ou une validation du propriétaire de l’automatisation. Le statut provisoire est « anomalie à vérifier » ou « non concluant » selon les règles internes ; les données ne suffisent pas à attribuer l’action à un adversaire. Si le seuil d’incident est atteint, on transmet au processus prévu.

**Barème sur 20.** Chronologie exacte : 4 points. Relations vérifiées : 4 points. Alternatives : 4 points. Preuve complémentaire : 4 points. Conclusion prudente : 4 points.

### TP 3 — Vérifier une absence de résultat

**Situation.** Une recherche sur les modifications de rôles ne renvoie aucun événement sur sept jours. L’audit du fournisseur confirme que les événements sont activés depuis trois jours seulement, et que l’ingestion comporte une interruption de six heures.

**Travail demandé.** Déterminez si l’absence de résultat permet de réfuter l’hypothèse. Construisez une liste de vérifications et proposez un plan de correction. Définissez un critère de reprise de la chasse.

**Correction attendue.** Non : la période n’est pas couverte. L’absence d’événement ne prouve pas l’absence d’action. L’équipe vérifie la configuration de la source, les événements effectivement générés, les lacunes d’ingestion, les horloges, les droits de requête et la rétention. Elle crée une action de collecte avec propriétaire et date, puis teste sur une fenêtre connue ou un événement synthétique autorisé. La chasse reprend lorsque la couverture temporelle convenue et les champs requis sont confirmés. Le rapport conserve la limite observée et ne présente pas le résultat comme une confirmation de sécurité.

**Barème sur 20.** Conclusion non biaisée : 5 points. Diagnostic des sources : 5 points. Plan d’action : 4 points. Critère de reprise : 4 points. Documentation des limites : 2 points.

### TP 4 — Transformer un motif en détection

**Situation.** Une chasse sur des événements synthétiques révèle un motif reproductible : plusieurs changements de rôle rapprochés sur un compte de laboratoire, hors de la fenêtre de changement attendue. Après vérification, le motif mérite une alerte mais doit ignorer les opérations approuvées identifiées dans un registre versionné.

**Travail demandé.** Définissez la logique conceptuelle de détection, les sources et champs requis, le jeu de tests positif et négatif, la procédure de revue, les métriques et le retest après déploiement.

**Correction attendue.** La règle regroupe des changements de rôle selon une fenêtre définie, en préservant l’acteur, la cible, le résultat et les horodatages. Le registre des opérations approuvées est utilisé comme contexte et son propriétaire doit maintenir les données à jour. Le test positif utilise un jeu synthétique qui correspond au motif ; les tests négatifs comprennent une opération de maintenance approuvée et un événement isolé ne dépassant pas la condition. La règle est versionnée et révisée. Le retest vérifie le déclenchement, la qualité de l’alerte et les effets sur les activités légitimes. Les exclusions doivent être limitées et auditées.

**Barème sur 20.** Logique traçable : 4 points. Sources et champs : 4 points. Tests positifs/négatifs : 4 points. Revue et versionnement : 4 points. Métriques et retest : 4 points.

## 23. Exercices corrigés

1. **Une chasse ne trouve aucun événement. Peut-on conclure qu’il n’y a pas eu d’activité ?**  
   **Correction :** seulement si les sources couvrent la période, l’événement attendu est journalisé, les champs sont disponibles et la requête a été validée. Sinon, la conclusion est non concluante.

2. **Quelle différence entre un hunt et une alerte ?**  
   **Correction :** l’alerte est un signal généré par une détection ; le hunt part d’une hypothèse et recherche proactivement des éléments dans les données.

3. **Pourquoi faut-il une hypothèse falsifiable ?**  
   **Correction :** elle permet de déterminer quelles observations la soutiendraient et quelles observations la contrediraient. Une question vague encourage les biais.

4. **Un compte de service se connecte à une heure inhabituelle. Est-ce malveillant ?**  
   **Correction :** pas automatiquement. Vérifier la tâche planifiée, la maintenance, le propriétaire, le compte réel et les sources corroborantes.

5. **La source n’enregistre pas les arguments du processus. Quelle conclusion tirer ?**  
   **Correction :** la visibilité est limitée sur cette propriété. On peut recommander d’améliorer l’audit, mais on ne peut pas déduire les arguments manquants.

6. **À quoi sert une ligne de base ?**  
   **Correction :** à contextualiser les écarts en fonction des rôles, systèmes et périodes. Elle doit être datée et mise à jour après les changements légitimes.

7. **Pourquoi vérifier les heures des sources ?**  
   **Correction :** des horloges désynchronisées peuvent produire une chronologie trompeuse ou masquer une relation entre événements.

8. **Quel est le rôle du contexte de changement ?**  
   **Correction :** expliquer les événements attendus comme un déploiement ou une maintenance, sans les considérer comme légitimes avant vérification.

9. **Une requête volumineuse ralentit le SIEM. Que faire ?**  
   **Correction :** réduire la fenêtre, optimiser les filtres, vérifier les coûts et faire approuver l’extension avant de lancer une recherche large.

10. **Pourquoi versionner une requête ?**  
    **Correction :** pour reproduire l’analyse, comparer les résultats et attribuer une différence à une modification précise.

11. **Comment gérer un résultat inattendu qui pourrait être un incident ?**  
    **Correction :** conserver les références utiles et transférer au processus de réponse selon les rôles définis. Ne pas improviser des actions de confinement.

12. **Pourquoi ne pas collecter tout le contenu réseau ?**  
    **Correction :** les métadonnées peuvent suffire et la collecte de contenu accroît les risques de confidentialité et de stockage. Toute collecte supplémentaire doit être justifiée et autorisée.

13. **Qu’est-ce qu’un faux négatif dans le jeu de test ?**  
    **Correction :** un cas qui devait satisfaire le critère de détection mais que la logique n’a pas signalé.

14. **Pourquoi tester des cas bénins ressemblants ?**  
    **Correction :** pour identifier les faux positifs et éviter qu’une nouvelle règle ne dégrade la qualité opérationnelle.

15. **Un mapping ATT&CK prouve-t-il que le contrôle fonctionne ?**  
    **Correction :** non. Le mapping organise le vocabulaire ; une preuve demande des données, un test et un résultat vérifié.

16. **Pourquoi la rétention importe-t-elle ?**  
    **Correction :** une période de conservation trop courte rend impossible une chasse couvrant la fenêtre souhaitée et limite l’investigation rétrospective.

17. **Comment présenter un résultat probable mais incomplet ?**  
    **Correction :** décrire les faits, les relations fiables, les éléments manquants et le niveau de confiance, sans le transformer en certitude.

18. **Pourquoi protéger les exports du hunt ?**  
    **Correction :** ils peuvent contenir des identifiants, l’architecture, des données personnelles et des informations sur les faiblesses du système.

19. **Qu’est-ce qu’un résultat utile sans découverte ?**  
    **Correction :** une hypothèse correctement testée sur des données suffisantes, qui n’est pas soutenue par les événements observés et dont les limites sont claires.

20. **Quand une chasse est-elle terminée ?**  
    **Correction :** quand les résultats sont documentés, les limites explicitées, les incidents éventuels transmis et les actions attribuées, avec des critères de retest convenus.

## 24. Défi final — Concevoir un programme de chasse sur quatre semaines

### Contexte

L’organisation fictive NovaFormation possède un annuaire d’identité, des serveurs applicatifs, un SIEM, une plateforme EDR et un environnement de laboratoire cloud. Une revue a montré que les journaux de changement de privilège sont incomplets pendant certaines périodes et que les analystes ont du mal à relier les événements d’identité aux tickets de changement. Aucun incident confirmé n’est associé à cette observation ; le programme vise à vérifier les hypothèses et améliorer les contrôles, pas à déclarer prématurément une compromission.

### Travail demandé

1. Définissez trois hypothèses classées par risque et expliquez leur valeur métier.
2. Identifiez les sources et champs requis ainsi que les limites de collecte.
3. Définissez le mandat, les accès, les personnes habilitées et les règles de confidentialité.
4. Planifiez les recherches et précisez les critères de conclusion.
5. Pour chaque hypothèse, listez des explications alternatives et les données qui permettraient de les vérifier.
6. Construisez un registre des découvertes, actions, propriétaires et échéances.
7. Transformez une découverte reproductible en détection testée.
8. Définissez les métriques de couverture, qualité et retest.
9. Présentez un résumé exécutif clair.
10. Précisez les critères qui déclencheraient une passation au processus d’incident.

### Exemple de correction

**Hypothèse A — Traçabilité des privilèges :** les changements de rôle sur les comptes de laboratoire doivent être enregistrés avec l’acteur, la cible, l’heure et le résultat, puis être rapprochés d’un ticket approuvé. Elle est prioritaire car une modification privilégiée non expliquée peut exposer des ressources importantes.

**Hypothèse B — Couverture temporelle :** les journaux sont disponibles sur toute la période de recherche définie. Elle vise à établir si l’absence de résultats est significative ou découle de lacunes de collecte. Les indicateurs sont les périodes couvertes, les erreurs d’ingestion et la présence des champs requis.

**Hypothèse C — Corrélation :** une séquence de changements de rôle peut être reliée à un acteur et un contexte de changement. Le test vérifie les identifiants de corrélation et la qualité des informations de triage ; il ne suppose pas que chaque séquence rapprochée est suspecte.

**Mandat et sources :** les recherches portent sur les journaux professionnels autorisés et les comptes de laboratoire. Les sources incluent l’audit d’identité, les événements de connexion, le registre des changements et les logs du SIEM. Les comptes personnels, les données non pertinentes et les systèmes de fournisseurs sont exclus. Les accès suivent le moindre privilège et la conservation suit les politiques de l’organisation.

**Calendrier :** semaine 1, valider les sources et établir la ligne de base ; semaine 2, exécuter les recherches et vérifier les alternatives ; semaine 3, corriger le mapping ou la couverture des événements ; semaine 4, retester et faire valider le rapport. Si la couverture initiale est insuffisante, la recherche de comportement est reportée et le travail porte d’abord sur la collecte.

**Règle issue de la chasse :** un jeu synthétique définit un changement de rôle hors fenêtre approuvée. La règle est liée aux événements de changement, au registre de maintenance et aux champs d’acteur et de cible. Les tests positifs utilisent le cas défini ; les négatifs comprennent une maintenance approuvée et un changement isolé ne remplissant pas le seuil. Une revue vérifie les coûts, les exclusions et la qualité de l’alerte avant son déploiement.

**Critères de résultat :** chaque conclusion mentionne la période, la source, la version de requête, le nombre d’événements éligibles, les limites et la confiance. La correction de la collecte ne ferme la question qu’après que les événements témoins sont visibles et que la couverture de la période est adéquate. Les événements suspects qui satisfont les critères d’escalade sont transférés au processus d’incident, où les personnes habilitées déterminent les actions.

**Synthèse exécutive :** « Le programme évalue la couverture des journaux d’identité et la capacité à relier des changements privilégiés aux validations métier. Les recherches initiales montrent que la conclusion dépend de la disponibilité temporelle des événements. Une correction de collecte et de normalisation sera suivie de tests contrôlés et d’une validation de la règle. Aucun constat de compromission n’est établi sans preuve corroborante ; tout résultat répondant aux critères d’incident sera transmis au processus prévu. »

### Barème sur 100

- Hypothèses et priorisation du risque : 15 points.
- Sources, champs et qualité des données : 15 points.
- Mandat, confidentialité et rôles : 10 points.
- Recherche et explications alternatives : 15 points.
- Méthode de conclusion et niveau de confiance : 10 points.
- Détection issue d’un motif reproductible : 10 points.
- Tests positifs, négatifs et retest : 10 points.
- Actions, propriétaires et échéances : 5 points.
- Résumé exécutif et gestion des incidents : 10 points.

Tout plan qui transforme l’absence de données en preuve de sécurité, accède à des données sans autorisation ou contourne la procédure d’incident doit être repris, même avec une bonne note numérique.

## 25. Checklist opérationnelle

**Avant la chasse :** définir le risque, l’hypothèse, l’autorisation, le périmètre et les données nécessaires. Vérifier les sources, les champs, la synchronisation des horloges, la rétention, les droits et la sensibilité des données. Définir les critères de conclusion, la marche à suivre en cas de découverte et le propriétaire de chaque action.

**Pendant :** garder des recherches versionnées et limitées, examiner la qualité des données, enrichir les résultats avec le contexte métier, tester les explications alternatives et éviter les conclusions hâtives. Si une source est absente ou une période lacunaire, noter la limite. Si un événement répond aux critères d’incident, suivre la procédure de passation et ne pas improviser une réponse.

**Après :** publier le périmètre, les requêtes, les résultats, les éléments pour et contre, le niveau de confiance, les limitations et les actions. Protéger les preuves et limiter les exports. Corriger les sources ou règles nécessaires, tester les effets secondaires et planifier un retest. Mettre à jour le registre et la date de dernière validation.

~~~text
PRÉPARER : risque / hypothèse / autorisation / données
CHERCHER : requête / contexte / alternatives / preuve
CONCLURE : confirmé / réfuté / expliqué / non concluant
AMÉLIORER : collecte / détection / procédure / retest
TOUJOURS : minimisation, traçabilité et respect du périmètre
~~~

## 26. Glossaire

- **Threat Hunting :** recherche proactive et structurée d’éléments qui soutiennent ou réfutent une hypothèse de sécurité.
- **Hypothèse de chasse :** question falsifiable qui annonce une observation attendue et les sources nécessaires.
- **Ligne de base :** référence contextualisée de l’activité habituelle d’une population d’actifs.
- **Télémétrie :** événements et mesures générés par les systèmes et outils.
- **Normalisation :** transformation des champs vers un schéma cohérent.
- **Couverture temporelle :** période pendant laquelle une source possède réellement les événements nécessaires.
- **Faux positif :** signal qui ne satisfait pas le critère de risque recherché.
- **Faux négatif :** cas pertinent du jeu de test que le mécanisme n’a pas détecté.
- **Enrichissement :** ajout de contexte métier ou technique utile à l’interprétation.
- **Corrélation :** association d’événements à l’aide de champs, relations et fenêtres temporelles.
- **LOTL :** utilisation de fonctions ou outils légitimes dans un contexte potentiellement abusif.
- **ATT&CK :** base de connaissances qui organise les tactiques, techniques et mécanismes de détection.
- **Data Component :** propriété spécifique de données pertinente pour observer un comportement dans ATT&CK.
- **Détection opérationnelle :** détection dont la donnée, l’alerte, le contexte et le traitement ont été vérifiés.
- **Résultat non concluant :** résultat pour lequel les données ou conditions ne permettent pas de trancher l’hypothèse.
- **Provenance :** origine et transformations connues d’un événement ou d’une preuve.
- **Rétention :** durée pendant laquelle des données sont conservées et disponibles.
- **Minimisation :** limitation de la collecte et du partage aux informations nécessaires.
- **Retest :** répétition contrôlée après une correction pour vérifier l’amélioration et les effets secondaires.
- **Confiance analytique :** jugement explicite sur la qualité et la cohérence des éléments disponibles.
- **Passation d’incident :** transfert du résultat vers le processus et les rôles habilités à gérer un incident.

## 27. Références officielles et lectures complémentaires

- MITRE ATT&CK, stratégie d’émulation et Red Team : https://attack.mitre.org/resources/get-started/adversary-emulation-and-red-teaming/
- MITRE ATT&CK, Data Components : https://attack.mitre.org/datacomponents/
- MITRE ATT&CK, mises à jour d’octobre 2025 et évolution de la couverture défensive v18 : https://attack.mitre.org/resources/updates/updates-october-2025/
- CISA et partenaires, Identifying and Mitigating Living Off the Land Techniques : https://www.cisa.gov/sites/default/files/2024-02/Joint-Guidance-Identifying-and-Mitigating-LOTL_V3508c.pdf
- CISA/IC3 et partenaires, Best Practices for Event Logging and Threat Detection : https://www.ic3.gov/CSA/2024/240822.pdf
- NIST SP 800-61 Rev. 3, Incident Response Recommendations and Considerations for Cybersecurity Risk Management : https://csrc.nist.gov/pubs/sp/800/61/r3/final
- NIST Log Management project et état de SP 800-92 Rev. 1 : https://csrc.nist.gov/Projects/log-management
- NIST Cybersecurity Framework 2.0 : https://www.nist.gov/cyberframework

Les références doivent être revues avant leur intégration dans des procédures réelles. ATT&CK évolue, et la version 18 a notamment remplacé l’ancienne organisation des détections par des stratégies, analyses et composants de données plus détaillés. Consultez la version en vigueur pour les objets et définitions utilisés dans un nouveau hunt.

## Conclusion

Le Threat Hunting apporte une démarche proactive qui transforme une question de risque en une recherche vérifiable. La qualité dépend de la pertinence de l’hypothèse, de la couverture des sources, du contexte, des explications alternatives, de la protection des données et de l’honnêteté de la conclusion. Une absence de résultat n’est rassurante que lorsque l’observabilité est suffisante et la recherche correctement construite.

La maturité se mesure par la capacité à reproduire les analyses, améliorer la collecte et les détections, transmettre correctement les événements qui relèvent d’un incident et retester les corrections. La chasse ne doit jamais remplacer l’autorisation, la gouvernance ou la réponse à incident. Elle les renforce en produisant une preuve plus utile et une vision plus précise des angles morts.

Fin du cours.