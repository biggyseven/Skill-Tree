# Red Team vs Blue Team vs Purple Team

> **Mise en contexte**
>
> Une organisation peut posséder un pare-feu, un EDR, un SIEM et des procédures de crise tout en restant incapable de détecter un comportement discret, d’en comprendre la portée ou de rétablir rapidement un service. La Red Team met à l’épreuve les hypothèses de défense, la Blue Team observe et traite les signaux, et la Purple Team relie les deux démarches par des preuves, des corrections et des retests. Cet ensemble n’est utile que si l’objectif est clair, l’autorisation explicite et les effets de l’exercice maîtrisés.
>
> Ce cours poursuit le parcours de cybersécurité après la gouvernance, la gestion des vulnérabilités, la supply chain et les réseaux OT/ICS. Il vous apprend à concevoir une campagne limitée, à la rapprocher de MITRE ATT&CK, à mesurer une détection et à présenter des conclusions vérifiables. Les travaux pratiques sont conçus pour des laboratoires, des événements synthétiques et des systèmes expressément autorisés. Une compétence technique ne donne jamais le droit de tester un système sans mandat.

## Objectifs du cours

Vous apprendrez à différencier Red Team, Blue Team, Purple Team et White Team, puis à choisir un format adapté à une question métier. Vous saurez rédiger des règles d’engagement, identifier les propriétaires d’actifs, définir une fenêtre, établir les critères d’arrêt et faire la différence entre un résultat négatif, un résultat non concluant et un contrôle réellement défaillant. Vous saurez aussi spécifier les traces attendues, suivre un événement depuis sa source jusqu’à l’analyste, et produire des actions correctives qui ont un propriétaire, une échéance et un critère d’acceptation.

La compétence n’est pas mesurée par le nombre d’outils utilisés ou de techniques ATT&CK coloriées. Elle repose sur la capacité à démontrer ce qui a été testé, dans quelles conditions, avec quelle preuve, quelle limite et quel niveau de confiance. Une bonne évaluation produit des décisions, évite les dommages inutiles et donne aux équipes une manière reproductible de vérifier les progrès.

## 1. Red Team : éprouver une hypothèse de défense

La Red Team adopte une perspective adversaire pour vérifier comment un système et ses équipes résistent à des comportements définis. Elle peut étudier la visibilité sur les identités, l’administration à distance, la segmentation, la détection d’un changement de privilège ou la coordination entre les opérations et le SOC. L’objectif n’est pas de remporter une compétition ni d’exécuter la chaîne la plus longue possible. Il s’agit de déterminer si une hypothèse de risque tient face à une simulation proportionnée, encadrée et documentée.

La préparation commence par la question métier, puis identifie les actifs, les préconditions, les actions permises, les résultats attendus et les méthodes de preuve. Les actions sont choisies en tenant compte du niveau de risque. Un événement synthétique peut valider un pipeline de détection sans toucher à un actif sensible. Une maquette peut suffire à tester la procédure d’escalade. La méthode la moins intrusive qui répond à la question doit être privilégiée.

L’équipe note chaque étape, l’heure, le compte de test, la source de preuve et le résultat. Elle distingue un fait d’une interprétation. « Aucun événement correspondant n’apparaît dans la recherche prévue » est vérifiable ; « le SOC ne détecte jamais ce comportement » ne l’est pas à partir d’un seul essai. Les limites, les préconditions manquantes et les branches non testées figurent dans le rapport. La preuve doit être suffisante et minimisée, afin de ne pas exposer des données inutiles.

~~~text
Objectif métier
     |
Hypothèse précise
     |
Périmètre et règles d'engagement
     |
Comportement de test autorisé
     |
Preuves collectées et limites
     |
Conclusion liée aux faits
~~~

## 2. Blue Team : de la télémétrie à la réponse

La Blue Team représente les capacités opérationnelles de défense : analystes SOC, ingénierie de détection, responsables EDR, réseau, identité, systèmes et réponse à incident. Elle collecte des événements, les normalise, les corrèle, qualifie les signaux, investigue les alertes et décide d’une réponse selon les procédures. Un produit installé ne garantit pas à lui seul cette capacité. Il faut une configuration pertinente, des événements fiables, des alertes exploitables, des personnes capables de les examiner et un mécanisme d’escalade.

Un signal utile doit apporter le contexte nécessaire pour répondre à plusieurs questions : quelle identité a agi, sur quelle ressource, à quelle heure, quel résultat a été enregistré, quelle source soutient la conclusion et pourquoi l’activité mérite une investigation ? Une alerte sans identifiant d’actif peut techniquement exister mais rester difficile à traiter. Une bonne détection ne se contente donc pas de déclencher ; elle facilite une décision proportionnée.

La Blue Team ne doit pas être blâmée lorsqu’une source ne collecte pas les données attendues. Il faut déterminer si l’écart vient de l’événement source, du collecteur, de l’ingestion, du mapping des champs, de la règle, de l’interface ou du processus humain. Le rôle défensif consiste aussi à reconnaître l’incertitude : si l’information nécessaire n’existe pas, l’analyse doit indiquer une visibilité insuffisante au lieu de conclure qu’aucune action n’a eu lieu.

~~~text
Événement source
      |
Collecte et ingestion
      |
Normalisation et enrichissement
      |
Règle / corrélation
      |
Alerte visible au SOC
      |
Triage et investigation
      |
Décision, réponse et compte rendu
~~~

## 3. Purple Team : la boucle de collaboration

La Purple Team est une pratique de collaboration structurée. Elle peut être portée par un groupe dédié ou organisée sous forme de sessions communes entre les opérateurs offensifs et les défenseurs. Elle transforme une observation en question exploitable : quel comportement a été représenté, quelles données auraient dû le rendre visible, quelle alerte est apparue, l’analyste disposait-il du contexte nécessaire et quelle modification permettra de corriger l’écart ?

Une session efficace est fondée sur une preuve partagée. L’équipe confirme les préconditions, réalise une action contrôlée, recherche l’événement dans les sources convenues puis compare le résultat à l’attendu. Si le journal n’existe pas, le problème se situe en amont de la règle. Si le journal existe mais que le champ a été renommé, il faut examiner le schéma ou le mapping. Si l’alerte apparaît mais n’est pas prise en charge, le problème peut concerner le triage, la priorité ou le contexte. Il faut corriger la cause réelle plutôt que d’ajouter des règles au hasard.

La session n’est pas une compétition de réputation. L’absence d’alerte n’est pas nécessairement une faute individuelle ; elle peut résulter d’un manque de collecte, d’un pipeline mal configuré, d’une règle absente ou d’une procédure impraticable. Une correction n’est validée qu’après un retest avec critères définis. Le registre partagé doit contenir l’hypothèse, la version du scénario, l’écart, le propriétaire, l’échéance, les preuves et la date du retest.

~~~text
RED : comportement contrôlé
          |
          v
BLUE : collecte, alerte et analyse
          |
          v
PURPLE : preuve partagée et diagnostic
          |
          v
Correction avec propriétaire
          |
          v
Retest positif + tests négatifs
          |
          v
Écart fermé ou risque explicitement accepté
~~~

## 4. White Team et séparation des rôles

La White Team contrôle l’exercice et garde une vue d’ensemble sur les conditions de sécurité. Elle vérifie les règles d’engagement, tient la chronologie de référence, coordonne les contacts, applique les règles d’arrêt et arbitre les demandes d’extension. Dans un exercice à connaissance limitée, elle peut être l’interlocuteur que les responsables de service contactent lorsqu’ils suspectent un incident. Elle ne doit pas manipuler les résultats pour favoriser une équipe.

Les rôles doivent être annoncés et compris avant la première action. La personne qui mène un test ne peut pas être l’unique autorité capable de dire si le test est encore sûr. Les propriétaires d’actifs doivent pouvoir déclarer un risque métier. Le responsable de sûreté doit pouvoir intervenir dans un environnement industriel. Le sponsor accepte les objectifs et le risque résiduel selon la gouvernance de l’organisation.

La séparation protège également l’intégrité du rapport. Une équipe peut constater qu’un objectif n’a pas été atteint, mais la conclusion doit reposer sur les événements disponibles et la définition de succès. Les interprétations et les faits doivent être séparés. Quand une observation est contestée, la réponse utile consiste à examiner les horodatages, le périmètre, la règle et la preuve, puis à rejouer le test si nécessaire.

~~~text
Sponsor / propriétaire du risque
              |
       Autorité désignée
              |
          White Team
         /    |     \
      Red    Blue   Opérations
         \    |     /
         Purple Team
              |
      Rapport et actions suivies
~~~

## 5. Distinguer les formats d’évaluation

Un test d’intrusion cherche à identifier et démontrer des faiblesses dans un périmètre donné, souvent une application, une API, un réseau ou une configuration. Un exercice Red Team s’intéresse davantage à des objectifs et à des chemins plausibles, et peut mesurer la coordination des équipes. Il n’a pas nécessairement pour mission de dresser l’inventaire complet de toutes les vulnérabilités. Une validation de contrôle vérifie qu’une protection ou une règle produit le résultat attendu. Un exercice sur table vérifie les décisions et la coopération à partir d’un scénario narratif. Un exercice de réponse à incident teste la qualification, la communication, le confinement et la reprise.

Ces formats se complètent, mais leurs conclusions ne sont pas interchangeables. Une absence de vulnérabilité dans le rapport d’un test d’intrusion ne prouve pas que les alertes sont bien traitées. Une simulation sur table ne prouve pas que l’événement est collecté par le SIEM. Un test technique positif ne garantit pas que l’équipe de garde prendra la bonne décision. Il faut préciser quelle capacité a été mesurée, dans quelles conditions et quelles autres capacités n’ont pas été testées.

Le bon format dépend de la question. Si l’objectif est de vérifier un champ manquant, un essai de détection ciblé est probablement plus rapide et moins risqué qu’une campagne Red Team étendue. Si l’objectif est d’évaluer un chemin entre plusieurs systèmes, un exercice plus large peut être justifié. Le choix doit considérer la valeur attendue, le coût, le risque de perturbation, le niveau d’autorisation et la capacité à interpréter les observations.

~~~text
Format                 Question principale
---------------------  -----------------------------------------
Test d'intrusion       Quelles faiblesses sont démontrables ?
Red Team               Un scénario atteint-il un objectif défini ?
Blue Team              Le signal est-il détecté et traité ?
Purple Team            Quelle correction et quel retest ?
Exercice sur table     Les décisions et responsabilités sont-elles claires ?
Validation de contrôle Le mécanisme répond-il au résultat attendu ?
~~~

## 6. Autorisation et règles d’engagement

L’autorisation n’est jamais un simple « vas-y » informel. Elle définit les systèmes, comptes, environnements et périodes approuvés, l’autorité qui peut élargir le périmètre, les méthodes permises et les actions interdites. Elle nomme les propriétaires d’actifs, le contrôleur, les contacts d’urgence et les personnes habilitées à décider d’un arrêt ou d’une reprise. Elle traite aussi des données personnelles, de la confidentialité, de la conservation des preuves et de la participation éventuelle de fournisseurs.

Les règles d’engagement (Rules of Engagement ou RoE) doivent être opérationnelles. Les exécutants doivent savoir quelles actions peuvent être réalisées, à quel moment, avec quels comptes et sur quels actifs. Les limites incluent les effets possibles sur la disponibilité, la charge, les flux réseau, la sécurité physique, la collecte de données et la communication avec des tiers. Toute découverte d’un système hors périmètre doit déclencher une pause et une demande d’avis, pas une extension improvisée.

Les critères d’arrêt doivent être concrets : service instable, donnée réelle découverte, système non prévu touché, contact d’urgence indisponible, perte de visibilité sur l’impact ou signal de sûreté inattendu. L’opérateur cesse l’action, enregistre les faits essentiels et avertit le contrôleur selon la procédure. La reprise requiert l’autorité prévue dans le mandat. Le fait qu’une action soit techniquement réversible ne la rend pas automatiquement acceptable.

~~~text
MANDAT
  |-- actifs inclus et exclus
  |-- fenêtre et méthodes autorisées
  |-- contacts de secours
  |-- données et preuves protégées
  |-- critères d'arrêt et de reprise
  v
BRIEF SÉCURITÉ
  v
ACTION AUTORISÉE -> OBSERVATION -> ARRÊT SI ÉCART
~~~

## 7. Construire une hypothèse testable

Une campagne commence par une question métier et non par un outil. Par exemple : « Un changement de privilège sur un compte de laboratoire est-il enregistré et présenté avec suffisamment de contexte pour déclencher une investigation ? » L’hypothèse contient un comportement, une précondition, un résultat attendu, une source de preuve et un critère de décision. Elle peut être confirmée, réfutée ou rester non concluante selon la qualité des données.

Il faut identifier l’actif de valeur, les dépendances et les contrôles supposés. Les tests doivent suivre une progression du moins risqué au plus risqué. Une revue de configuration, un événement synthétique ou une simulation peut suffire à valider l’audit. Une maquette est préférable quand l’action pourrait affecter un service réel. Les actions plus intrusives ne sont justifiées que si la question l’exige, que les autorisations le permettent et que les garde-fous sont adaptés.

Le scénario doit indiquer les éléments volontairement non testés. Cette transparence évite d’exagérer la conclusion. Si un scénario ne passe pas sa précondition, le test n’a pas mesuré les contrôles postérieurs à cette précondition. Le résultat doit donc être classé selon ce qui a réellement été observé. Une conclusion négative n’est pas automatiquement une preuve de vulnérabilité, et un résultat positif isolé ne prouve pas une sécurité générale.

~~~text
Risque métier
     |
Hypothèse testable
     |
Préconditions + périmètre
     |
Méthode proportionnée
     |
Résultat attendu / résultat observé
     |
Conclusion, limites et action
~~~

## 8. Utiliser MITRE ATT&CK correctement

MITRE ATT&CK fournit un vocabulaire structuré pour parler des tactiques, techniques et sous-techniques observées dans des activités adverses. Une tactique représente un objectif général ; une technique décrit une manière de l’atteindre. ATT&CK permet de relier le renseignement sur la menace, les scénarios d’émulation et les idées de détection. Ce n’est pas une certification, une liste obligatoire de tests ni une preuve qu’une capacité fonctionne.

Les scénarios doivent correspondre au contexte : actifs concernés, menace pertinente, exposition et conséquence métier. Une organisation n’a pas besoin de tester toutes les entrées de la matrice. Elle peut choisir un ensemble restreint lié à l’abus d’identité, à l’accès distant, à l’audit des changements privilégiés ou à la visibilité des échanges entre zones, selon ses risques. Les exclusions doivent aussi être notées et justifiées.

Il faut vérifier les descriptions et versions actuelles des techniques ainsi que les limites des sources publiques. Les plans d’émulation publiés par MITRE et le Center for Threat-Informed Defense peuvent soutenir la préparation. Ils ne doivent pas être copiés sans adaptation, car l’architecture, les contrôles, les droits et les contraintes de l’organisation ne sont pas identiques. Une technique ne doit être mappée que si le comportement représenté correspond réellement à sa définition. Si la correspondance est incertaine, le rapport doit le dire.

~~~text
Renseignement et contexte de menace
              |
Choix d'une technique pertinente
              |
Comportement sûr et autorisé
              |
Sources de données et détection attendue
              |
Preuve + date + version ATT&CK
              |
Retest et mise à jour de la couverture
~~~

## 9. Vérifier la qualité de la télémétrie

Avant de tester une règle, vérifiez que les sources produisent les événements nécessaires. Les horloges doivent être synchronisées ou leurs écarts documentés. Le pipeline doit préserver les identités, les actifs, la date, l’action et le résultat si ces champs existent. Les conventions de nommage doivent être cohérentes entre systèmes. L’accès de l’analyste aux champs doit être suffisant pour appliquer la procédure prévue.

Un échec de détection peut être localisé à plusieurs endroits : l’événement n’a pas été généré, la source n’a pas journalisé l’action, le collecteur ne l’a pas envoyé, l’ingestion a échoué, le schéma a été transformé, la règle n’a pas correspondu, l’alerte a été supprimée ou l’interface a omis le contexte. Chacun de ces cas demande une correction différente. Ajouter une règle supplémentaire n’aide pas si la donnée n’existe jamais.

La préparation comporte une ligne de base. L’équipe exécute une requête connue sur des données de laboratoire, vérifie les résultats attendus et conserve la version du schéma. Le retest répète cette vérification après une modification. Les tests positifs doivent être complétés par des cas négatifs proches du comportement recherché afin d’examiner les faux positifs et les régressions.

~~~text
L'événement est-il créé ?
  non -> vérifier précondition et audit
  oui
    |
Le collecteur l'ingère-t-il ?
  non -> diagnostiquer source et transport
  oui
    |
Les champs sont-ils corrects ?
  non -> corriger mapping / schéma
  oui
    |
La règle et l'alerte fonctionnent-elles ?
  non -> corriger détection et workflow
  oui -> valider triage et réponse
~~~

## 10. Construire une détection utile

Une règle durable s’appuie sur des comportements, des relations et des séquences plutôt que sur un seul indicateur statique. Les indicateurs ont une utilité, mais un nom, une adresse ou un hash peut rapidement devenir périmé. Chaque règle doit avoir une hypothèse, une source, une logique, une version, un responsable, une documentation, un test positif et des tests négatifs. Les faux positifs et les faux négatifs doivent être interprétés dans le contexte du jeu de test.

La qualité se mesure au-delà du déclenchement. Une alerte peut être rapide mais ne contenir ni acteur ni actif. Une autre peut arriver plus tard mais permettre une investigation complète. Il faut choisir les objectifs selon l’impact et les engagements de service, sans ignorer le besoin de détection rapide. Le résultat attendu décrit la qualité minimale du contexte et les décisions à prendre.

Le déploiement d’une règle est un changement opérationnel. Il faut tester la logique, examiner les effets sur les événements proches, déployer selon le processus de changement et surveiller les résultats. Une exception temporaire doit avoir un propriétaire et une échéance. Exclure en permanence un compte de test peut créer un angle mort si ce compte devient utilisable par une personne non autorisée ou si son rôle change.

~~~text
Hypothèse de détection
        |
Source et champs requis
        |
Test positif -> alerte attendue
        |
Tests négatifs -> absence d'alerte incorrecte
        |
Revue, approbation et déploiement
        |
Mesure après déploiement
~~~

## 11. Concevoir la boucle Purple

La session commence par un objectif limité, des préconditions documentées et des critères de sûreté. Les participants vérifient l’état des données avant le test afin d’éviter de confondre un défaut préexistant avec une régression. Une seule action contrôlée est exécutée à la fois. L’heure, l’identité de test, la version des règles et les résultats doivent être consignés avec précision.

Les équipes analysent ensemble ce qui s’est passé, puis formulent des hypothèses sur les écarts. Un champ manquant, un retard d’ingestion et une règle mal écrite ne se corrigent pas de la même façon. La cause retenue doit être appuyée par une observation. Si plusieurs causes demeurent possibles, le dossier indique ce qui est inconnu et propose un test supplémentaire, au lieu de prétendre à une certitude.

La correction est décrite comme une action vérifiable. « Améliorer la visibilité » est vague ; « faire apparaître l’identifiant de l’actif dans la vue de triage, vérifier la normalisation sur trois événements synthétiques et rejouer le test positif et deux tests négatifs » constitue une action contrôlable. Le responsable et l’échéance sont assignés selon la gouvernance. Le résultat n’est pas fermé avant un retest, sauf décision explicite d’accepter le risque résiduel par l’autorité habilitée.

~~~text
1. Sélectionner une hypothèse
2. Confirmer environnement et journaux
3. Exécuter un seul comportement contrôlé
4. Rechercher la preuve
5. Identifier le maillon défaillant
6. Définir la correction et son propriétaire
7. Rejouer le positif et les négatifs
8. Consigner le résultat, la version et la date
~~~

## 12. Mesures : délais, précision et couverture

Le temps de détection (TTD) doit être défini avec un point de départ et un point d’arrivée précis. L’heure de l’action, celle de l’ingestion, celle de création de l’alerte et celle de sa prise en charge sont différentes. Les comparer sans définition produit des chiffres trompeurs. Les délais peuvent être mesurés séparément : événement vers ingestion, ingestion vers alerte, alerte vers triage, triage vers escalade, décision vers confinement et confinement vers reprise.

Le terme MTTR peut représenter des phases très différentes. Le rapport doit déclarer ce qu’il mesure et ne pas mélanger le temps de qualification et le temps de récupération. Les mesures incluent la source, la fenêtre, les conditions, le fuseau et les éventuelles incertitudes d’horloge. Les objectifs sont fixés avant le test selon le niveau de risque et les attentes métiers.

La précision se mesure sur un jeu de test défini. Un petit nombre de tests positifs réussis ne garantit pas une capacité universelle. La couverture ATT&CK doit distinguer collecte disponible, règle testée, alerte visible, traitement vérifié et réponse exercée. Une case non testée est inconnue, non automatiquement protégée ou vulnérable. Les tableaux de bord doivent afficher la date de dernière preuve et les limites d’interprétation.

~~~text
Mesure                Départ -> Arrivée
--------------------  ----------------------------------------
Collecte               événement -> donnée ingérée
Détection              événement -> alerte pertinente
Triage                 alerte -> qualification initiale
Escalade               qualification -> rôle compétent
Confinement            décision -> effet vérifié
Récupération           début de reprise -> service validé
Couverture opérationnelle collecte + règle + traitement testés
~~~

## 13. Renseignement sur la menace et priorisation

Le renseignement fournit du contexte, pas une suite d’actions à reproduire mécaniquement. Les informations documentées, les inférences et les inconnues doivent être séparées. Les sources ont une date, une provenance et un niveau de confiance. Une procédure ancienne peut rester intéressante pour illustrer un comportement stable, mais sa pertinence actuelle doit être vérifiée avant qu’elle devienne un objectif de test.

La sélection des scénarios repose sur la vraisemblance, l’impact métier, la surface d’exposition, les actifs de valeur, les contrôles disponibles et le risque de l’exercice lui-même. Une technique fréquente mais peu pertinente peut être secondaire. À l’inverse, une faiblesse de journalisation sur un accès privilégié peut être prioritaire si les conséquences sont importantes. La priorisation doit être expliquée et relue avec les propriétaires du risque.

La fiche du scénario décrit l’hypothèse, les sources utilisées, les actifs, les comportements autorisés, les journaux attendus, le succès, les exclusions, le calendrier et les limites. Elle peut être reprise et améliorée au fil des exercices. Une hypothèse ne devient pas une vérité permanente parce qu’elle a été testée une fois ; les configurations, les menaces et les personnes changent.

## 14. Identité, cloud et fournisseurs

Les environnements cloud possèdent des frontières administratives et techniques complexes : comptes, abonnements, rôles, clés, services managés, outils d’administration, journaux d’audit et fournisseurs. Le droit de tester un compte client ne donne pas automatiquement l’autorisation d’évaluer les services partagés du fournisseur. La préparation doit vérifier les conditions applicables, les contacts et les limites exactes du périmètre.

Les scénarios d’identité doivent employer des comptes dédiés, des permissions minimales et des ressources de laboratoire. Il est possible de vérifier l’attribution d’une action privilégiée, la journalisation d’une décision d’accès ou la révocation d’un compte sans collecter des secrets réels. Les clés de test doivent avoir une portée réduite, une expiration courte et une procédure de rotation ou de suppression connue.

Les journaux doivent permettre de distinguer une action humaine, une identité de service et une automatisation. Il faut conserver l’acteur, la ressource, l’heure, l’origine et le résultat lorsque ces champs sont disponibles. Pour les tiers, la procédure inclut l’approbation, les fenêtres, la notification, la confidentialité et le partage du rapport. Toute action ambiguë est suspendue jusqu’à clarification.

~~~text
Compte de test à permissions minimales
         |
Action synthétique autorisée
         |
Audit d'identité et journal cloud
         |
Normalisation et corrélation
         |
Alerte contextualisée
         |
Validation SOC et révocation du compte
~~~

## 15. Environnements OT/ICS et sûreté

Les systèmes OT/ICS commandent ou surveillent des procédés et peuvent être soumis à des contraintes de disponibilité et de sûreté. Les automates, IHM, SCADA, systèmes de contrôle distribué et systèmes instrumentés de sécurité ne doivent pas être traités comme des postes informatiques ordinaires. Une action de test peut affecter la visibilité, la communication ou le procédé. Les responsables d’exploitation, de procédé et de sûreté doivent participer à la préparation.

Les méthodes commencent par une revue documentaire ou une observation passive quand elle répond à la question. Une maquette, des événements synthétiques ou un environnement de développement permettent de valider des journaux, une escalade ou une procédure sans perturber un procédé réel. Une action susceptible de modifier une consigne de production ou d’affecter un mécanisme de sécurité est exclue d’un exercice ordinaire sans analyse de risques et approbation formelle spécifiques.

Les critères d’arrêt OT doivent être alignés avec les responsables habilités : perte de visibilité, alarme inattendue, performance dégradée, incertitude sur l’effet d’une action ou contact de supervision indisponible. Les critères de reprise sont décidés par les mêmes autorités. Le rapport distingue cybersécurité, sécurité physique et sûreté fonctionnelle ; ces domaines se recoupent mais ne sont pas identiques.

~~~text
SOC / IT
   |
   | journaux validés
   v
Zone de supervision
   |
   | accès approuvé et contrôlé
   v
Maquette OT de test
   |-- événements synthétiques
   |-- opérateur d'exercice
   |-- responsable procédé
   |-- responsable sûreté
   |
Arrêt immédiat si risque pour le procédé
~~~

## 16. Réponse à incident et confinement

Un exercice peut mesurer si l’alerte devient une investigation, si l’investigation est qualifiée comme incident et si les équipes suivent les responsabilités prévues. Les participants doivent connaître le rôle du responsable d’incident, les niveaux de gravité, les contacts et les règles de préservation. Une White Team peut introduire les informations progressivement, en notant chaque injection et son heure, pour observer la coordination sans confondre les événements.

Le confinement peut avoir un impact métier important. Couper un compte, isoler un endpoint ou bloquer un segment doit respecter les autorisations, les procédures et les conséquences. Le testeur ne doit pas improviser une action réelle sur un système critique uniquement pour démontrer qu’une réponse est possible. Une simulation sur table ou un actif désigné peut valider la prise de décision et le workflow.

La preuve doit avoir une provenance et un horodatage. Si le contexte exige une chaîne de possession, elle doit être conservée conformément aux procédures internes. Les données synthétiques et les faits réels doivent être distingués. Après le scénario, il faut vérifier que les services fonctionnent, que les mesures temporaires sont retirées, que les comptes sont désactivés et que le propriétaire confirme l’état final.

~~~text
Signal
  |
Triage et enrichissement
  |
Qualification par le rôle prévu
  |
Décision de réponse autorisée
  |-- confinement contrôlé
  |-- préservation des preuves
  |-- communication métier
  v
Récupération validée par le propriétaire
  |
Retour d'expérience et retest
~~~

## 17. Construire un rapport actionnable

Un rapport contient le but, le périmètre, les règles d’engagement, la période, les méthodes, les preuves, les résultats, les limites et les recommandations. Il doit dire ce qui n’a pas été exécuté et pourquoi. Une absence de preuve, un test interrompu et un résultat négatif sont des états différents. Un rapport sérieux ne transforme pas une incertitude en conclusion pour présenter un résultat plus spectaculaire.

Chaque constat peut inclure un identifiant, le titre, l’actif, le risque métier, le fait observé, les préconditions, la preuve minimale, l’impact, la cause probable, le niveau de confiance, une recommandation, un propriétaire, une échéance et la méthode de retest. Les preuves doivent être suffisantes et minimisées. Une capture d’écran sans heure ni contexte est faible ; un export complet de logs peut exposer des informations inutiles. Un extrait documenté, associé à une source et à un stockage restreint, est souvent préférable.

Les actions doivent être spécifiques. « Améliorer les alertes » ne permet pas de savoir quand fermer le ticket. Une action peut viser un champ de normalisation, une règle, un panneau de triage ou une procédure d’escalade. Le critère d’acceptation exprime ce qui sera observé après correction et les tests négatifs qui doivent continuer à réussir. Les priorités considèrent l’impact, l’exposition, la faisabilité et les mesures compensatoires.

~~~text
Constat RT-01
Fait observé : alerte sans contexte d'actif
Impact : qualification plus lente que l'objectif convenu
Cause à confirmer : mapping ou panneau de triage
Action : corriger le champ et vérifier trois cas de test
Propriétaire : ingénierie de détection
Acceptation : positif réussi, négatifs maîtrisés
Retest : date, version, requête et preuve enregistrées
~~~

## 18. Débriefing et culture d’amélioration

Le débriefing compare les chronologies de la Red Team, de la Blue Team et du contrôleur. Les participants identifient les écarts entre attente et observation, les signaux utiles, les données manquantes et les décisions difficiles. Il faut se concentrer sur les faits et les systèmes, pas sur les humiliations. « L’alerte est restée sans prise en charge jusqu’au dépassement du seuil, car la file ne montrait pas l’actif » permet de concevoir une amélioration ; « l’analyste a échoué » n’explique pas la cause.

Les réussites doivent être documentées aussi. Une alerte pertinente, une escalade rapide, une action correctement arrêtée ou une reprise validée représentent des capacités à conserver. Le rapport doit préciser les limites du test afin de ne pas généraliser une réussite à un contexte qui n’a pas été observé. Le bilan attribue des actions et établit un point de suivi.

Une équipe mature sait discuter d’un résultat non concluant. Si l’horloge est désynchronisée, si les journaux sont incomplets ou si la précondition ne s’est pas produite, la bonne réponse consiste à corriger les conditions et rejouer le scénario. La transparence sur l’incertitude est une force opérationnelle. Les erreurs doivent aider à améliorer les procédures et la visibilité, pas encourager à cacher les difficultés.

## 19. Programme récurrent et automatisation

Un programme Red/Blue/Purple pérenne établit un calendrier proportionné aux risques, une bibliothèque de scénarios versionnés, des critères communs, un processus de revue et des retests. Les changements d’identité, de réseau, de cloud, d’outil de collecte ou de règle de détection peuvent justifier une validation ciblée. Des exercices plus larges évaluent la coordination entre les équipes et les dépendances. Ces formats se complètent.

L’automatisation améliore la répétabilité, mais elle peut aussi produire une charge, créer des objets ou déclencher des réponses. Un test planifié doit s’identifier clairement, limiter les actifs, respecter la fenêtre et avoir un mécanisme d’arrêt. Les exclusions et exceptions doivent être limitées dans le temps et réexaminées. Une automatisation ne doit jamais être programmée contre des actifs non autorisés ou avec des données réelles non nécessaires.

Les tableaux de bord sont utiles quand ils exposent la définition des indicateurs, la qualité des données, les versions et les dates de dernière preuve. Ils sont trompeurs s’ils réduisent la couverture à des cases colorées. Une technique peut avoir été collectée mais pas testée ; une règle peut avoir déclenché mais l’alerte n’a pas été traitée ; un test positif peut réussir mais les faux positifs augmentent. Les niveaux sont séparés pour conserver une image honnête de la capacité.

~~~text
Planification selon le risque
       |
Bibliothèque de scénarios versionnés
       |
Test ciblé ou exercice coordonné
       |
Correction affectée à un propriétaire
       |
Retest et vérification des effets secondaires
       |
Revue de couverture et nouveau cycle
~~~

## 20. Erreurs fréquentes

Première erreur : démarrer sans question métier ni critères mesurables. L’activité devient une démonstration d’outil et le rapport ne peut pas dire si le risque a changé. Deuxième erreur : considérer les règles d’engagement comme une formalité. Elles constituent un mécanisme de sécurité opérationnelle, et les exécutants doivent pouvoir les appliquer sans interprétation hasardeuse.

Troisième erreur : affirmer qu’un contrôle fonctionne parce qu’il est installé. La configuration doit être testée avec une entrée pertinente et une preuve. Quatrième erreur : conclure que la détection est absente parce qu’une alerte n’est pas visible. Il faut vérifier la chaîne source, transport, normalisation, règle et traitement. Cinquième erreur : fermer le constat après le déploiement d’une correction sans retest ni preuve.

Sixième erreur : mesurer la couverture par le nombre de cases ATT&CK cochées. La collecte, le déclenchement, le contexte, le triage et la réponse sont des niveaux différents. Septième erreur : traiter la Purple Team comme une réunion ponctuelle. Le processus inclut le test, la cause, la correction et la revalidation. Huitième erreur : conserver un scénario immuable pendant des années. Il faut comparer les versions, prendre en compte les changements d’architecture et actualiser les hypothèses.

## 21. Méthode opérationnelle de conception

Rédigez d’abord une phrase qui décrit la capacité à vérifier. Décrivez ensuite l’état initial, les systèmes de laboratoire, les comptes autorisés et le résultat attendu. Listez les dépendances, les données qui pourraient être sensibles, les effets secondaires possibles et les personnes décisionnaires. Si vous ne pouvez pas expliquer comment interrompre l’essai et remettre l’environnement dans son état prévu, le test n’est pas prêt.

Découpez le scénario en étapes courtes. Chaque étape possède un identifiant, une précondition, un comportement synthétique, une source de données, un résultat attendu et un critère d’arrêt. Les tests positifs démontrent que le signal attendu est produit. Les tests négatifs examinent des événements légitimes similaires et doivent éviter une alerte erronée. Les entrées et sorties sont versionnées pour que les résultats puissent être répétés.

Préparez le plan de rapport avant l’exécution. Les indicateurs, les niveaux de preuve, les critères de clôture et l’autorité qui accepte le risque résiduel sont définis à l’avance. Après la correction, refaites les mêmes tests, ajoutez si nécessaire des cas négatifs, documentez les effets secondaires et faites valider la clôture. Cette méthode évite de choisir après coup les mesures qui favorisent le résultat observé.

~~~text
ID       Précondition     Test              Critère
RT-01    compte labo      événement témoin    audit complet
RT-02    log ingéré       recherche SOC       requête reproductible
RT-03    règle active     rejeu contrôlé      alerte attendue
RT-04    alerte visible   triage analyste     décision tracée
RT-05    correction faite retest             preuve de fermeture
~~~

## 22. Travaux pratiques guidés

Tous les travaux pratiques utilisent des événements synthétiques, un laboratoire ou une maquette. Ils n’exigent aucun accès non autorisé, aucune collecte de données réelles et aucune action destructrice.

### TP 1 — Rédiger des règles d’engagement

**Situation :** une équipe veut vérifier qu’un changement de rôle sur un compte de laboratoire produit un journal complet et une alerte dans la vue du SOC. L’application et le compte sont fictifs. Le but est de valider l’audit et la qualité du triage, pas de contourner des privilèges.

**À réaliser :** rédigez le sponsor, le propriétaire, le périmètre inclus et exclu, la fenêtre, les comptes de test, les contacts, les méthodes permises, les données protégées, les critères d’arrêt, les conditions de reprise et le nettoyage. Définissez le succès à partir de l’identité, de l’actif, de l’heure, de l’action et du résultat. Précisez qui peut arrêter l’exercice.

**Correction :** le mandat inclut uniquement l’instance de démonstration et le compte indiqué. Les systèmes de production, comptes personnels, fournisseurs et données réelles sont exclus. Avant l’essai, le contrôleur vérifie que le compte correspond bien à l’identifiant de laboratoire. Un service instable, une donnée réelle découverte, un périmètre incertain ou un contact d’urgence injoignable déclenche l’arrêt. La reprise demande l’accord du rôle désigné. Le succès exige un événement d’audit complet et une alerte contextualisée dans le délai préétabli. La clôture vérifie que le compte et les objets de test sont désactivés ou supprimés.

**Barème sur 20 :** périmètre (4), rôles et contacts (4), critères d’arrêt et de reprise (4), résultat mesurable (4), nettoyage et protection des données (4).

### TP 2 — Mapper un comportement à une preuve ATT&CK

**Situation :** l’organisation souhaite vérifier la traçabilité d’une action d’administration représentée par un événement synthétique. Les défenseurs veulent utiliser ATT&CK pour communiquer le type de comportement, sans confondre le mapping avec une preuve de détection.

**À réaliser :** créez une fiche avec l’hypothèse, la pertinence métier, le mapping retenu, la version de la matrice, la source, les champs nécessaires, la règle, le résultat attendu et les limites. Distinguez les niveaux « source disponible », « règle testée », « alerte visible » et « traitement vérifié ». Expliquez comment noter un test non concluant.

**Correction :** le mapping n’est retenu que si le comportement correspond à la description actuelle de la technique. L’événement contient acteur, ressource, heure et résultat. Le scénario décrit la source, la requête et la version de règle. Si la source manque, le statut est « visibilité insuffisante, test non concluant » ; la conclusion n’affirme pas automatiquement qu’une technique est non détectée. La fiche indique ce qui est connu, ce qui doit être réparé, le propriétaire et la date de retest. La matrice n’est pas présentée comme un certificat de couverture générale.

**Barème sur 20 :** hypothèse et risque (4), source et champs (4), mapping justifié (4), statuts exacts (4), version et limites (4).

### TP 3 — Diagnostiquer une alerte absente

**Données du laboratoire :** un événement synthétique se produit à 10:00:00. Le collecteur le reçoit à 10:00:02. La plateforme le normalise à 10:00:05, mais change le champ user_id en actor_name. La règle recherche toujours user_id. À 10:00:07 aucune alerte n’est créée, et l’analyste ne trouve rien à 10:12.

**À réaliser :** localisez le premier écart visible, proposez une correction, un test positif et deux tests négatifs, puis définissez les critères de clôture. Expliquez pourquoi une nouvelle règle générique peut masquer le défaut au lieu de le corriger.

**Correction :** les événements existent et sont ingérés ; le mapping de schéma constitue le premier écart. L’équipe compare le message avant et après normalisation, vérifie la convention de champs, puis corrige le mapping ou la règle selon le schéma approuvé. Le test positif utilise un acteur et une action synthétiques. Les négatifs peuvent être un changement légitime ne remplissant pas la condition de risque et un événement de laboratoire sans le champ déclencheur. La clôture exige un événement normalisé, une alerte contextualisée dans le délai cible et l’absence de faux positifs sur les cas négatifs définis. Les versions et preuves sont enregistrées.

**Barème sur 20 :** diagnostic (5), causes alternatives (4), tests positifs et négatifs (4), critères de fermeture (4), explication des limites (3).

### TP 4 — Produire un bilan Purple Team

**Situation :** une alerte de laboratoire apparaît en 24 secondes, mais il faut neuf minutes pour identifier le bon actif. Le triage final est correct. Le nom d’actif est disponible dans les données brutes, mais absent du premier panneau d’alerte.

**À réaliser :** rédigez une conclusion factuelle, une action corrective, un propriétaire, une échéance, une métrique de retest et un contrôle des effets secondaires. Évitez tout jugement individuel sur l’analyste.

**Correction :** le signal a été créé rapidement, mais le contexte nécessaire au triage n’est pas visible dans la première vue. L’action consiste à corriger l’enrichissement ou l’affichage du champ d’actif, puis à vérifier plusieurs événements synthétiques. Le SOC valide que la vue est exploitable ; l’équipe d’ingénierie de détection possède la correction. Le retest mesure alerte-vers-qualification, contrôle le champ sur plusieurs actifs fictifs et rejoue les cas négatifs. Le résultat est fermé après vérification de la règle et de l’absence de régression. L’échéance suit la gravité et la capacité d’ingénierie.

**Barème sur 20 :** constat factuel (4), action précise (4), métrique (4), propriétaire et échéance (4), retest et régression (4).

## 23. Exercices corrigés

1. **Choisir l’approche.** Le SOC doit-il détecter et traiter un changement de privilège simulé.  
   **Correction :** un cycle Purple Team est adapté, car il met en relation la production du signal, son traitement et le retest.

2. **Définir l’objectif.** Pourquoi « faites un test réaliste » est-il insuffisant ?  
   **Correction :** il manque le risque métier, le périmètre, les préconditions, la preuve et les critères de réussite.

3. **Actif inconnu.** Une ressource hors périmètre est découverte.  
   **Correction :** interrompre l’action concernée, informer le contrôleur et attendre une autorisation explicite.

4. **Pas de journal.** L’analyste ne voit aucune donnée et la source n’a pas été vérifiée.  
   **Correction :** le résultat est non concluant ; examiner la source et le pipeline avant de juger la détection.

5. **Alerte sans contexte.** Un événement est détecté mais l’actif est absent.  
   **Correction :** la détection est partielle ; améliorer l’enrichissement et mesurer le temps de qualification.

6. **Couverture ancienne.** Un test a réussi il y a deux ans.  
   **Correction :** présenter la date de preuve et revalider le contrôle dans l’environnement actuel.

7. **Test négatif.** Pourquoi vérifier des événements légitimes similaires ?  
   **Correction :** pour repérer les faux positifs et les régressions de précision après modification de la règle.

8. **Débriefing.** Quelle formulation est la plus utile que « le SOC a échoué » ?  
   **Correction :** décrire ce qui s’est passé, à quelle heure, quel contexte manquait et quel délai a été dépassé.

9. **Fournisseur cloud.** Un test peut toucher une plateforme partagée.  
   **Correction :** vérifier l’autorisation et les conditions du fournisseur, puis utiliser une simulation si le périmètre n’est pas permis.

10. **OT/ICS.** Une action peut perturber un procédé.  
    **Correction :** préférer une maquette ou une simulation et obtenir l’approbation des responsables de procédé et de sûreté.

11. **Temps de détection.** L’horodatage source est antérieur à l’ingestion.  
    **Correction :** distinguer événement-vers-ingestion et ingestion-vers-alerte ; ne pas masquer le délai total.

12. **Confinement.** L’isolation d’un serveur critique pourrait arrêter un service.  
    **Correction :** ne jamais la lancer sans autorisation explicite ; simuler la décision si nécessaire.

13. **Preuve volumineuse.** Pourquoi ne pas partager l’export complet ?  
    **Correction :** il pourrait exposer des données non nécessaires ; fournir un extrait protégé et contextualisé.

14. **Action vague.** « Améliorer la supervision » est inscrit au suivi.  
    **Correction :** définir le champ, la règle ou le workflow à changer, un responsable et le test d’acceptation.

15. **Champ absent.** La règle ne reçoit jamais la donnée.  
    **Correction :** traiter la collecte ou le schéma avant de qualifier cela de faux négatif de la règle.

16. **Arrêt indépendant.** Pourquoi la White Team est-elle habilitée à arrêter ?  
    **Correction :** afin que la sûreté prime sur l’achèvement du scénario et que la décision soit indépendante.

17. **Succès mesurable.** Quelle est la meilleure formulation ?  
    **Correction :** le positif déclenche une alerte contextualisée et les négatifs restent dans le seuil accepté.

18. **Précondition manquante.** Le compte laboratoire était désactivé.  
    **Correction :** le test ne mesure pas la détection visée et doit être répété si la précondition est corrigée.

19. **Versionnement.** Pourquoi stocker le scénario, la règle et les horodatages ?  
    **Correction :** pour que le résultat soit reproductible, comparable et attribuable à une version donnée.

20. **Clôture.** La correction est déployée mais non retestée.  
    **Correction :** noter le déploiement, mais conserver le constat ouvert ou en attente de vérification, sauf acceptation formelle du risque par l’autorité compétente.

## 24. Défi final — Concevoir un mini-programme Purple Team

### Contexte

NovaFormation possède un portail d’administration, un annuaire d’identité, un SIEM et un réseau de maquette OT isolé. Un précédent exercice a montré qu’un changement de rôle était enregistré dans une source, mais que la vue d’alerte ne présentait pas toujours l’actif. Le responsable veut un programme de quatre semaines sans interruption des services.

### Travail demandé

1. Formuler deux hypothèses mesurables et les relier aux risques métiers.
2. Définir la portée, les exclusions, les personnes autorisées et les règles d’engagement.
3. Choisir deux comportements synthétiques et les sources requises.
4. Définir les résultats attendus à la source, dans la règle, dans le triage et durant le nettoyage.
5. Ajouter un test positif et au moins deux tests négatifs par détection.
6. Définir les indicateurs et leurs horodatages.
7. Attribuer les actions, propriétaires, échéances et critères d’acceptation.
8. Rédiger une communication exécutive factuelle.
9. Établir les critères d’arrêt et la procédure de reprise.
10. Décrire les preuves minimales qui permettront de fermer les constats.

### Correction proposée

**Hypothèse A :** un changement de rôle sur le compte de laboratoire produit un événement d’audit contenant l’acteur, la ressource, l’heure et le résultat, puis une alerte visible dans la file désignée. Le risque est une modification privilégiée non détectée.

**Hypothèse B :** une alerte synthétique associée à un actif fictif entraîne une qualification et une escalade vers le rôle compétent dans le délai accepté. Le risque est une décision tardive ou une responsabilité ambiguë.

Le périmètre comprend l’application de démonstration, le compte dédié et les données synthétiques. La production, les comptes personnels, les fournisseurs et les systèmes partagés sont exclus. Le sponsor et les propriétaires approuvent l’exercice. La White Team coordonne la chronologie et peut arrêter l’opération. Les responsables d’OT et de sûreté approuvent toute utilisation de la maquette industrielle.

Les comportements choisis sont une simulation de changement de rôle et un événement d’accès inhabituel fictif. Les techniques ATT&CK ne sont assignées qu’après vérification de leur adéquation. Les sources comprennent les journaux de l’application, l’audit d’identité, le pipeline de normalisation, la règle SIEM et la vue d’analyste.

Les métriques séparent événement-vers-ingestion, ingestion-vers-alerte, alerte-vers-prise en charge, prise en charge-vers-qualification et qualification-vers-escalade. Les cibles sont définies avant l’essai. Les tests négatifs couvrent des événements légitimes proches et des événements ne satisfaisant pas le critère de risque. Les résultats sont limités au jeu de test et ne doivent pas être présentés comme une couverture globale.

La semaine 1 sert à obtenir les autorisations, inventer les actifs de laboratoire, vérifier les journaux et enregistrer la ligne de base. La semaine 2 exécute les tests contrôlés et rassemble les preuves. La semaine 3 corrige le schéma ou la vue de triage et vérifie les effets secondaires. La semaine 4 rejoue les scénarios, tient le débriefing et fait approuver les résultats. Le planning doit être adapté aux fenêtres de changement réelles.

L’équipe d’ingénierie de détection possède la correction d’affichage. Le SOC valide l’utilité du contexte. Le propriétaire de l’application confirme la sémantique du champ. La clôture exige un test positif, les tests négatifs, les horodatages, les versions de règle et la preuve de triage. Les comptes et objets de laboratoire sont désactivés à la fin.

**Synthèse exécutive :** « L’exercice contrôlé confirme que l’événement de changement de rôle est enregistré. Le contexte d’actif manque cependant dans une partie de la vue de triage, ce qui retarde la qualification. La correction visera la normalisation ou l’affichage, puis sera vérifiée par un test positif et des tests négatifs. Aucun test sur la production ou sur des données réelles n’est prévu. Le risque résiduel ne sera réévalué qu’après le retest. »

### Barème sur 100

- Hypothèses et risques métiers : 10 points.
- Autorisation, portée et règles d’engagement : 15 points.
- Choix des comportements et usage justifié d’ATT&CK : 10 points.
- Sources et preuves attendues : 15 points.
- Tests positifs et négatifs : 10 points.
- Mesures interprétables : 10 points.
- Actions, responsabilités et échéances : 10 points.
- Arrêt, reprise et nettoyage : 10 points.
- Synthèse factuelle : 5 points.
- Limites et retest : 5 points.

Une note de 85/100 représente une bonne maîtrise si les exigences de sûreté sont respectées. Tout scénario autorisant une action hors périmètre ou ignorant un risque industriel doit être repris, même si le total numérique est élevé.

## 25. Checklist opérationnelle

**Avant :** vérifier le sponsor, les propriétaires, l’autorisation, les règles d’engagement, le périmètre, les comptes de laboratoire, les fenêtres, les horloges, la collecte, les contacts de secours et le retour arrière. Confirmer que la White Team peut déclencher un arrêt et que les critères de reprise sont clairs.

**Pendant :** consigner les actions et leurs heures, rester dans les limites, surveiller la santé du système, utiliser les identités dédiées, collecter la preuve minimale et signaler tout écart. Ne pas poursuivre un test uniquement pour obtenir un résultat plus spectaculaire. Une anomalie réelle peut exiger l’arrêt du scénario et le déclenchement du processus d’incident.

**Après :** rapprocher les chronologies, protéger les preuves, distinguer les faits des interprétations, attribuer les actions, désactiver les comptes et nettoyer les objets de laboratoire. Rejouer les tests après correction, vérifier les cas négatifs, surveiller les régressions et obtenir la validation du propriétaire du risque. Mettre à jour la version du scénario et la date de dernière preuve.

~~~text
AVANT    : mandat / portée / rôles / journaux / arrêt
PENDANT  : action limitée / chronologie / preuve / contrôle
APRÈS    : nettoyage / bilan / propriétaire / retest / approbation
TOUJOURS : autorisation, minimisation, traçabilité, coopération
~~~

## 26. Glossaire

- **Red Team :** équipe qui émule des comportements adverses autorisés pour éprouver les hypothèses de défense.
- **Blue Team :** équipes responsables de la prévention, de la détection, de l’investigation et de la réponse.
- **Purple Team :** collaboration structurée qui relie les essais et les améliorations défensives.
- **White Team :** fonction de contrôle et de coordination de l’exercice, notamment pour la sûreté.
- **Règles d’engagement :** limites, méthodes, horaires, rôles et critères d’arrêt et de reprise d’un test.
- **MITRE ATT&CK :** base de connaissances de tactiques et techniques associées à des comportements adverses.
- **Émulation :** reproduction contrôlée d’un comportement afin d’évaluer un contrôle ou une défense.
- **SIEM :** plateforme qui centralise et analyse des événements de sécurité.
- **EDR :** technologie de collecte et de réponse pour postes et serveurs, dépendante de sa configuration.
- **Télémétrie :** données produites par les systèmes et outils et utiles à l’observation.
- **Faux positif :** signal déclenché pour un événement qui ne répond pas à la condition recherchée.
- **Faux négatif :** cas pertinent du jeu de test non détecté selon le critère défini.
- **TTD :** délai entre un point de départ déclaré et une détection pertinente.
- **Triage :** qualification initiale d’un signal et décision sur les étapes suivantes.
- **Confinement :** limitation autorisée de la portée ou des conséquences d’un incident.
- **Preuve :** élément contextualisé et daté qui soutient un constat.
- **Critère d’acceptation :** condition mesurable qui permet de valider une correction.
- **Retest :** nouvelle exécution après correction pour vérifier le résultat et les effets secondaires.
- **Risque résiduel :** risque restant et traité par l’autorité compétente.
- **Sûreté fonctionnelle :** capacité à éviter des conditions dangereuses dans un procédé.
- **Couverture opérationnelle :** preuve que collecte, détection, traitement et réponse ont été vérifiés dans des conditions explicites.

## 27. Références officielles

- MITRE ATT&CK — Adversary Emulation and Red Teaming : https://attack.mitre.org/resources/get-started/adversary-emulation-and-red-teaming/
- MITRE ATT&CK — Adversary Emulation Plans : https://attack.mitre.org/resources/adversary-emulation-plans/
- MITRE Center for Threat-Informed Defense — Adversary Emulation Library : https://ctid.mitre.org/resources/adversary-emulation-library
- MITRE ATT&CK Evaluations : https://attackevals.mitre.org/
- NIST SP 800-115, Technical Guide to Information Security Testing and Assessment : https://csrc.nist.gov/pubs/sp/800/115/final
- NIST Cybersecurity Framework 2.0 : https://www.nist.gov/cyberframework
- NIST SP 800-61 Rev. 3, Incident Response Recommendations and Considerations for Cybersecurity Risk Management : https://csrc.nist.gov/pubs/sp/800/61/r3/final
- CISA, Cybersecurity Best Practices : https://www.cisa.gov/topics/cybersecurity-best-practices
- MITRE ATT&CK for ICS : https://attack.mitre.org/matrices/ics/
- CISA, Recommended Practices for Industrial Control Systems : https://www.cisa.gov/resources-tools/resources/ics-recommended-practices

Vérifiez toujours les versions actuelles des documents avant d’adopter une procédure en entreprise. Ces références décrivent des cadres et méthodes ; elles ne remplacent pas l’autorisation explicite d’un propriétaire de système.

## Conclusion

La Red Team éprouve une hypothèse de défense, la Blue Team transforme les événements en décisions, et la Purple Team relie les observations aux corrections. Un programme utile sait dire précisément ce qui a été testé, ce que les preuves démontrent, ce qui reste inconnu, qui porte l’action et comment le résultat sera vérifié. L’autorisation, la sûreté, la minimisation des données et la traçabilité sont des conditions de qualité, pas des obstacles à l’exercice.

La progression se mesure par des risques mieux compris, des contrôles testés, des alertes exploitables, une réponse maîtrisée et des améliorations confirmées. Le nombre d’outils, la taille de la matrice ou la sophistication apparente d’un scénario ne remplacent pas ces preuves.

Fin du cours.