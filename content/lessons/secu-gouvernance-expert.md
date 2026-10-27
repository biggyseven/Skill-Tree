# Gouvernance et Conformité

> **Mise en contexte**

Une organisation peut disposer de pare-feu, d'un outil EDR, de sauvegardes et d'une équipe technique compétente tout en étant incapable de répondre à des questions essentielles : qui accepte les risques, qui valide les exceptions, quelles exigences contractuelles s'appliquent à un fournisseur, et comment démontrer qu'une politique est suivie ? Cette situation révèle un problème de gouvernance. La cybersécurité ne se limite pas à l'achat d'outils : elle exige des responsabilités, des décisions justifiées, des contrôles vérifiables et une amélioration continue.

La gouvernance organise la manière dont une organisation décide, finance, applique et surveille ses mesures de sécurité. La conformité consiste à évaluer les exigences applicables et à démontrer, avec des preuves, comment elles sont prises en compte. Les deux sont complémentaires, mais ne sont pas synonymes. Des documents conformes en apparence peuvent coexister avec des risques mal maîtrisés ; une mesure technique efficace ne suffit pas non plus à démontrer qu'une obligation juridique ou contractuelle a été satisfaite.

Ce cours propose une démarche pratique indépendante d'un secteur ou d'un pays. Les lois, délais de notification, exigences de certification et obligations de conservation dépendent du contexte réel. Toute interprétation juridique doit être validée par les responsables compétents et, si nécessaire, un conseil qualifié. Les exercices reposent sur des scénarios fictifs.

## 1. Objectifs et compétences visées

À la fin du cours, vous saurez expliquer les rôles de la gouvernance et de la conformité, établir le périmètre d'un programme de gestion des risques, identifier les parties prenantes, construire un registre des obligations, tenir un registre des risques, sélectionner des contrôles, attribuer des propriétaires, produire des preuves d'exécution, organiser une revue de direction et construire un plan d'amélioration. Vous saurez distinguer une politique, une norme interne, une procédure, une ligne directrice, une preuve et un résultat de contrôle.

La compétence avancée consiste à relier les enjeux métiers aux décisions de sécurité. Il faut pouvoir expliquer pourquoi un risque est acceptable ou non, quelles options existent, qui dispose de l'autorité pour décider et comment vérifier que la décision reste valable. Les risques ne peuvent pas tous être éliminés ; ils doivent être identifiés, évalués, traités et acceptés au niveau approprié, en respectant les obligations applicables.

Le cours s'appuie sur plusieurs référentiels reconnus. Le NIST Cybersecurity Framework (CSF) 2.0 décrit des résultats qui structurent la gestion du risque cyber. ISO/IEC 27001:2022 définit des exigences pour un système de management de la sécurité de l'information. NIST SP 800-53 propose un catalogue de contrôles de sécurité et de protection de la vie privée. Ces ressources n'ont pas exactement la même finalité : aucune n'est automatiquement une loi pour toute organisation et aucune ne garantit, à elle seule, la sécurité.

~~~text
Stratégie métier
      |
      v
Objectifs et tolérance au risque
      |
      v
Politiques + responsabilités + contrôles
      |
      v
Exécution opérationnelle et preuves
      |
      v
Mesures, audit et revue de direction
      |
      v
Décisions et amélioration continue
~~~

## 2. Gouvernance, gestion et opérations

La gouvernance fixe la direction, l'appétence au risque, les responsabilités et les mécanismes de surveillance. La gestion transforme cette direction en plans, budgets, ressources et priorités. L'opérationnel exécute les contrôles au quotidien : gestion des accès, correctifs, sauvegardes, revue des alertes, tests de restauration, inventaires et traitement des incidents. Un programme solide relie ces trois niveaux et s'assure que les décisions produisent des résultats mesurables.

La direction porte la responsabilité de l'orientation et de la surveillance selon la structure de l'organisation. Le responsable sécurité coordonne le programme et présente les risques. Les responsables métiers définissent la criticité des services et les conséquences acceptables. Les équipes techniques mettent en œuvre les contrôles. Les fonctions juridique, conformité, audit, achats, ressources humaines et protection des données apportent leurs expertises. Les fournisseurs peuvent exécuter certaines activités, mais la délégation technique n'efface pas automatiquement les responsabilités du client.

Ne confondez pas séparation des rôles et transfert de responsabilité. Un fournisseur cloud peut assurer la sécurité physique de ses centres de données tout en laissant au client la responsabilité des identités, des données, de certaines configurations et des règles d'accès. La répartition dépend du service, du contrat et du modèle de déploiement. Elle doit être documentée et vérifiée.

~~~text
Direction : objectifs, arbitrages, surveillance
                    |
                    v
Gestion : budget, risques, priorités, indicateurs
                    |
                    v
Opérations : contrôles, journaux, correction
                    |
                    v
Preuves et résultats mesurés
                    |
                    +------> revue de direction
~~~

### 2.1 Autorité et responsabilité

Pour chaque décision importante, identifiez une personne ou une fonction redevable. Plusieurs équipes peuvent réaliser une tâche, mais l'approbation ne doit pas rester ambiguë. Une matrice RACI clarifie qui réalise (R), qui est redevable ou approuve (A), qui est consulté (C) et qui est informé (I). Évitez d'attribuer l'approbation à plusieurs fonctions lorsque cela crée un conflit ; définissez une règle d'arbitrage.

Une responsabilité utile est observable. « L'équipe sécurité gère la conformité » est trop vague. Préférez : « le propriétaire du contrôle d'accès valide la revue trimestrielle des comptes privilégiés, suit les écarts et conserve la preuve d'approbation ». Cette formulation indique un responsable, une fréquence, une action, un résultat attendu et un emplacement de preuve.

## 3. NIST CSF 2.0 et la fonction Govern

Le NIST CSF 2.0 a été publié en février 2024 et s'adresse à des organisations de tailles et de secteurs variés. Il organise les résultats cyber autour de six fonctions : Govern, Identify, Protect, Detect, Respond et Recover. La fonction Govern rend explicites la stratégie de risque, le contexte organisationnel, les responsabilités, les politiques, la surveillance et la gestion du risque fournisseur. Elle n'est pas une étape unique que l'on termine avant les autres fonctions ; elle les oriente en continu.

Le CSF décrit des résultats souhaités plutôt qu'un processus technique obligatoire. Une organisation peut atteindre un résultat par des moyens différents selon son contexte, sa taille, ses dépendances et sa maturité. Les profils organisationnels servent à comparer l'état actuel et l'état cible. Ils doivent être construits autour des priorités métiers, et non par sélection mécanique de toutes les catégories.

Le CSF n'est pas une certification générale délivrée par NIST. C'est un cadre flexible pour organiser la gestion du risque, expliquer les choix à la direction et communiquer avec les partenaires. Il ne remplace ni le jugement métier ni l'analyse des exigences applicables.

~~~text
CSF 2.0
  |
  +--> GOVERN  : stratégie, rôles, politiques, fournisseurs
  +--> IDENTIFY: actifs, contexte, risques
  +--> PROTECT : mesures de protection
  +--> DETECT  : événements et analyse
  +--> RESPOND : réponse aux incidents
  +--> RECOVER : restauration et résilience
  |
  v
Profil actuel -> écarts prioritaires -> profil cible
~~~

### 3.1 Profil actuel et profil cible

Le profil actuel décrit les résultats observés à partir de preuves disponibles. Il ne doit pas reposer uniquement sur les affirmations des responsables. « Les accès privilégiés sont revus » doit être corroboré par un calendrier, un export, une validation, les exceptions et les preuves de correction. Si la revue est seulement planifiée, le profil doit le signaler.

Le profil cible fixe les résultats à atteindre dans un horizon réaliste. Les écarts sont classés selon l'impact, la probabilité, les obligations, le coût, les dépendances et les ressources. Une feuille de route peut donner la priorité à la journalisation des actifs critiques, à la gestion des identités, aux sauvegardes restaurables, à la réponse à incident et aux fournisseurs critiques avant des optimisations moins importantes.

~~~text
État actuel : contrôles observés et preuves
                         |
                         v
Analyse des écarts et risques
                         |
                         v
État cible : résultats priorisés et datés
                         |
                         v
Plan : propriétaire + budget + échéance + indicateur
                         |
                         v
Revue périodique des résultats
~~~

## 4. Système de management de la sécurité de l'information

Un système de management de la sécurité de l'information (SMSI) établit le cadre pour définir, mettre en œuvre, maintenir et améliorer la sécurité. ISO/IEC 27001:2022 spécifie des exigences relatives au contexte, au leadership, à la planification, au soutien, aux opérations, à l'évaluation de la performance et à l'amélioration. La version officielle et ses amendements doivent être consultés pour connaître le texte exact ; ce cours n'en reproduit pas le contenu intégral.

Le SMSI commence par une compréhension de l'organisation : activités, parties intéressées, dépendances, besoins, exigences et périmètre. Un périmètre trop vague rend les responsabilités et l'audit difficiles. Un périmètre artificiellement étroit peut masquer des services indispensables ou des données importantes. Décrivez les activités, sites, équipes, systèmes, données, fournisseurs et interfaces inclus, ainsi que les exclusions justifiées.

Le SMSI est un cycle, pas un classeur de politiques. Il relie le contexte aux risques, aux objectifs, aux ressources, à l'exécution des contrôles, aux preuves, à l'audit interne, à la revue de direction et aux actions correctives.

~~~text
Contexte et périmètre
       |
       v
Leadership et politique
       |
       v
Risques et objectifs
       |
       v
Contrôles en fonctionnement
       |
       v
Mesure, audit et revue
       |
       v
Correction et amélioration
       +----------------------> retour au contexte
~~~

### 4.1 Politique, procédure et preuve

La politique exprime les principes, exigences et responsabilités de haut niveau. Une norme interne formalise une règle plus précise, par exemple les conditions d'approbation d'une exception. Une procédure détaille les étapes d'une activité. Un guide propose des conseils sans nécessairement créer la même obligation. Le statut de chaque document doit être clair.

Les documents possèdent un propriétaire, une version, une date d'approbation, une date de révision, un périmètre et une audience. L'organisation communique les règles applicables et vérifie leur mise en œuvre. Une signature prouve qu'une personne a approuvé un document, mais ne prouve pas que le contrôle est exécuté.

La preuve d'exécution peut être un rapport de revue, un export horodaté, un ticket de correction, une trace de test, une configuration vérifiée ou un procès-verbal. Elle doit être suffisamment complète pour démontrer le fonctionnement, tout en étant protégée contre les modifications. Les preuves peuvent contenir des données sensibles : appliquez la minimisation et des droits d'accès limités.

## 5. Exigences juridiques, réglementaires et contractuelles

Les exigences peuvent venir des lois, réglementations sectorielles, contrats, engagements clients, règles internes, conditions d'assurance, licences et clauses de fournisseurs. Chaque obligation est liée à un acteur, un contexte, une donnée, un système, une activité ou une géographie. Il faut donc identifier où l'organisation opère, quelles données elle traite, quels services elle fournit, quels accords elle a signés et quelles autorités peuvent être compétentes.

Ne confondez pas norme volontaire, certification, contrat et loi. Un référentiel peut soutenir une démarche de contrôle mais ne remplace pas une obligation juridique applicable. Une certification peut porter sur un périmètre précis et une période donnée ; elle ne signifie pas que tous les systèmes ont été audités. Un contrat peut imposer des délais, des niveaux de service, des audits ou des notifications propres à ce client.

Créez un registre des exigences avec la source officielle, l'exigence précise, l'applicabilité, le propriétaire, le contrôle associé, les preuves attendues, la fréquence de revue, la date de dernière vérification et les changements à surveiller. Pour un texte juridique, faites valider l'interprétation par une fonction compétente. Le registre doit être mis à jour lors d'un changement d'activité, d'un nouveau pays, d'un nouveau type de données, d'une acquisition, d'un contrat important ou d'une modification réglementaire.

~~~text
Source d'exigence
    |
    v
Applicabilité confirmée ?
    |
    +--> non : justification documentée et revue planifiée
    |
    +--> oui
          |
          v
Contrôle + propriétaire identifiés
          |
          v
Preuve attendue + fréquence de vérification
          |
          v
Écart ? -> action corrective, échéance, responsable
~~~

### 5.1 Veille et gestion du changement

La veille ne consiste pas à accumuler des liens. Un processus de veille précise les sources, la fréquence, les responsables, les critères d'impact et la façon de modifier les documents ou contrôles concernés. Lorsqu'une nouvelle version d'un référentiel ou une nouvelle règle apparaît, évaluez son effet sur le périmètre, les contrats, les contrôles, les preuves ou les échéances.

Une fiche d'impact peut comporter : changement détecté, source et date, exigences concernées, systèmes et équipes touchés, analyse juridique ou contractuelle nécessaire, actions, responsable, échéance et preuve de clôture. Les exceptions doivent être datées et réévaluées. Conserver une ancienne version de politique sans savoir si elle s'applique est une faiblesse de gouvernance.

## 6. Registre et traitement des risques

Le risque cyber associe un scénario d'événement, les actifs ou objectifs concernés, les facteurs facilitants, la vraisemblance et les conséquences. Il ne se réduit pas à une note produite par un scanner. Une vulnérabilité technique est un facteur de risque ; le risque métier dépend aussi de l'exposition, des contrôles existants, des privilèges, des dépendances, des données, de la capacité de détection et du temps de récupération.

Décrivez le scénario de manière compréhensible. « Risque serveur élevé » manque de précision. « Une compromission de l'identité d'administration du service de paiement pourrait permettre une modification non autorisée des données et interrompre les transactions » décrit un événement, une ressource et des conséquences. Cette formulation aide à choisir des contrôles pertinents et à expliquer la priorité.

Le registre comporte un identifiant, un scénario, les actifs concernés, le propriétaire du risque, les contrôles existants, les éléments disponibles, la vraisemblance, l'impact, le niveau initial, les options de traitement, le niveau résiduel, la décision d'acceptation, les échéances et la date de revue. Les scores aident à comparer, mais les hypothèses et incertitudes doivent rester visibles.

~~~text
Actif et objectif métier
        |
        v
Scénario crédible et facteurs de risque
        |
        v
Vraisemblance + impact + contrôles existants
        |
        v
Niveau de risque initial
        |
        v
Traitement -> risque résiduel -> décision autorisée
        |
        v
Surveillance et réévaluation
~~~

### 6.1 Risque inhérent, actuel et résiduel

Le risque inhérent décrit le scénario avant de considérer les contrôles, selon la méthode retenue. Le risque actuel ou net tient compte des contrôles réellement en place et de leur efficacité démontrée. Le risque résiduel est celui qui subsiste après les mesures de traitement envisagées ou réalisées, selon la définition utilisée. Documentez la terminologie, car les méthodes diffèrent.

Un contrôle écrit mais non exécuté ne doit pas réduire fortement le niveau de risque. Une sauvegarde annoncée mais jamais restaurée, une revue d'accès prévue mais non réalisée ou un correctif déployé sur une partie seulement des systèmes n'apportent pas la même assurance qu'un contrôle testé et mesuré. Évaluez l'efficacité à partir des preuves et du périmètre réellement couvert.

### 6.2 Options de traitement

Les options typiques sont la réduction du risque par des contrôles, l'évitement de l'activité, le transfert ou le partage de certaines conséquences, et l'acceptation documentée. Le transfert contractuel ou par assurance ne fait pas disparaître toutes les responsabilités ni les conséquences opérationnelles. L'acceptation ne doit pas servir à contourner une obligation juridique ou contractuelle.

Une décision d'acceptation précise le scénario, le niveau résiduel, la justification, les conséquences, les compensations, la durée, les conditions de réexamen et la personne redevable. Une acceptation indéfinie sans revue devient souvent une exception permanente.

~~~text
Options de traitement
    |
    +--> Réduire : ajouter ou améliorer des contrôles
    +--> Éviter : arrêter ou modifier l'activité risquée
    +--> Partager : répartir certaines conséquences
    +--> Accepter : décision autorisée, explicite et révisable
~~~

## 7. Appétence, tolérance et escalade

L'appétence au risque exprime le niveau et le type de risque que l'organisation est disposée à poursuivre pour atteindre ses objectifs. La tolérance définit des limites plus opérationnelles, par exemple la durée d'indisponibilité acceptable ou l'exposition maximale d'une catégorie de données. Les termes doivent être définis dans la politique de risque et reliés aux objectifs métiers.

Définissez des seuils d'escalade : risque au-dessus du niveau convenu, obligation non satisfaite, exposition de données sensibles, contrôle essentiel inopérant, fournisseur critique non évalué, ou risque dépassant la délégation d'un responsable. L'escalade présente le scénario, les options, le coût, les délais, le risque résiduel et la décision attendue. Une alerte peut la déclencher, mais l'acceptation doit rester sous l'autorité prévue.

La tolérance au risque ne doit pas être confondue avec un seuil arbitraire de conformité. Une organisation ne peut pas justifier le non-respect d'une obligation impérative par une appréciation interne « faible ». Les exigences contraignantes et les risques discrétionnaires doivent être gérés séparément, même s'ils sont présentés ensemble à la direction.

## 8. Inventaire, données et dépendances

La gouvernance exige une connaissance suffisante des actifs : systèmes, comptes, services, données, interfaces, fournisseurs et dépendances. Un inventaire incomplet fausse les analyses de risques, les contrôles d'accès, les plans de continuité et la preuve de conformité. Les actifs ont un propriétaire métier et, si nécessaire, un propriétaire technique. Les données sont classifiées selon leur sensibilité et les impacts en cas de perte, d'altération ou de divulgation.

Un inventaire utile contient un identifiant unique, un nom, un type, un propriétaire, une criticité, l'environnement, la localisation, la classification des données, les dépendances, le service métier, l'exposition, la source de vérité, la date de mise à jour et l'état du cycle de vie. Ne conservez pas inutilement des secrets dans l'inventaire ; référencez un coffre approuvé au lieu de copier une valeur confidentielle.

Une cartographie de dépendances répond à des questions telles que : quels services dépendent de ce fournisseur ? Quels systèmes utilisent ce compte de service ? Quels processus métier sont affectés si le réseau, DNS ou l'identité est indisponible ? Cette information facilite l'analyse d'impact, le confinement et les priorités de récupération.

~~~text
Processus métier
      |
      +--> Application
      |      +--> Base de données
      |      +--> Identité et accès
      |      +--> Réseau et DNS
      |
      +--> Fournisseur critique
      |
      v
Données, propriétaires, criticité et objectifs de service
~~~

## 9. Sélection des contrôles et déclaration d'applicabilité

Les contrôles doivent être choisis à partir des risques, objectifs, exigences applicables et contraintes de l'environnement. Une liste de contrôles n'est pas un plan d'action. Pour chaque contrôle sélectionné, indiquez l'objectif, le propriétaire, le périmètre, la méthode d'exécution, la fréquence, les preuves, le critère de réussite, les dépendances, les exceptions et les actions en cas d'échec.

Dans un SMSI aligné sur ISO/IEC 27001, la déclaration d'applicabilité (Statement of Applicability, SoA) documente les contrôles retenus, leur état de mise en œuvre et les justifications d'inclusion ou d'exclusion conformément à la norme et au contexte. Ne copiez pas un catalogue complet sans analyse. Les contrôles sont pertinents parce qu'ils traitent des risques ou répondent à des exigences applicables, non parce qu'ils apparaissent dans une liste générique.

Un catalogue comme NIST SP 800-53 aide à structurer des contrôles et des familles. Il faut sélectionner et adapter les contrôles au contexte. Les versions et mises à jour doivent être vérifiées : NIST a annoncé la version 5.2.0 de SP 800-53 en août 2025 avec certaines nouvelles améliorations et modifications. Identifiez précisément la version de référence utilisée par l'organisation.

~~~text
Risque / exigence
       |
       v
Contrôle adapté et objectif mesurable
       |
       v
Propriétaire + périmètre + fréquence
       |
       v
Preuve et critère de réussite
       |
       v
Test d'efficacité et traitement de l'écart
~~~

### 9.1 Contrôles préventifs, détectifs et correctifs

Les contrôles préventifs visent à empêcher une action non autorisée, par exemple des privilèges minimaux ou une segmentation adaptée. Les contrôles détectifs révèlent une activité ou un écart, par exemple une alerte ou une revue de configuration. Les contrôles correctifs limitent l'impact ou rétablissent un état attendu, par exemple une restauration testée ou une procédure de remédiation.

Plusieurs couches réduisent la dépendance à un contrôle unique. Toutefois, empiler des outils similaires sans tester leur efficacité n'offre pas automatiquement une meilleure assurance. Examinez la couverture réelle, les scénarios non détectés, les erreurs, la capacité opérationnelle et les preuves. Pour chaque contrôle, demandez-vous comment une défaillance serait repérée et corrigée.

## 10. Mesurer l'efficacité des contrôles

La présence d'un outil ou d'une politique est une entrée, pas nécessairement un résultat. Une mesure d'efficacité doit être liée à un objectif et à un critère d'acceptation. « Sauvegardes activées » décrit une configuration ; le taux de succès des sauvegardes critiques et les résultats de tests de restauration dans le délai cible renseignent davantage sur le résultat opérationnel. Un indicateur doit posséder une définition, un périmètre, une source, une fréquence, un responsable et un seuil d'escalade.

Distinguez indicateurs d'activité, de résultat et de risque. Le nombre de formations achevées est une activité ; le résultat d'un exercice peut éclairer la compréhension ; le taux d'incidents issus d'un vecteur particulier peut informer la gestion du risque si les données sont fiables. Aucune métrique n'est parfaite : une baisse des alertes peut signaler une amélioration ou une panne de collecte. Interprétez les tendances avec le contexte et des sources complémentaires.

Évitez les indicateurs qui favorisent les mauvais comportements. Récompenser uniquement le nombre de tickets fermés peut encourager des clôtures prématurées. Mesurer la conformité à partir de déclarations auto-rapportées sans preuve peut rendre les écarts invisibles. Une bonne mesure incite à vérifier le résultat, pas à optimiser le chiffre à la place de l'objectif.

~~~text
Objectif du contrôle
       |
       v
Métrique et définition
       |
       v
Source + périmètre + fréquence
       |
       v
Seuil et propriétaire
       |
       v
Tendance et explication
       |
       v
Action d'amélioration si écart
~~~

## 11. Audit interne, externe et assurance

Un audit évalue des critères établis à partir d'éléments probants selon un périmètre et une méthode définis. L'audit interne contribue à l'amélioration et à l'assurance ; l'audit externe peut être contractuel, réglementaire ou lié à une certification. L'audit ne doit pas être confondu avec une revue opérationnelle quotidienne, un scan automatisé ou un simple inventaire de documents. Les activités se complètent, mais leurs objectifs, leur indépendance et leurs conclusions diffèrent.

La planification identifie les critères, le périmètre, la période, les compétences, les échantillons, les sources, les contacts, les risques d'interruption et les règles de confidentialité. Un échantillon doit être pertinent et justifié. La preuve doit être appropriée et vérifiable : un document peut prouver l'existence d'une procédure sans prouver son exécution.

Les constats doivent être rattachés aux critères et aux preuves. Distinguez non-conformité, observation, opportunité d'amélioration et risque opérationnel selon la méthode applicable. Le rapport explique l'impact, la portée et la solidité des éléments. Le suivi vérifie les actions correctives et leurs preuves de clôture.

~~~text
Critère d'audit
     |
     v
Collecte d'éléments probants
     |
     v
Évaluation contre le critère
     |
     +--> Conforme avec preuve
     +--> Écart ou non-conformité
     +--> Point à clarifier
     |
     v
Constat + responsable de réponse + suivi
~~~

### 11.1 Préparer des preuves sans fabriquer une vitrine

Une préparation d'audit efficace consiste à savoir où se trouvent les preuves, qui les produit, quel contrôle elles démontrent et comment elles ont été validées. Ne créez pas de journaux, de signatures ou de procès-verbaux rétroactifs pour faire apparaître un contrôle comme exécuté. Si une preuve manque, indiquez-le, analysez l'écart et mettez en place une correction réelle.

Conservez les documents avec leur version et leur contexte. Une capture d'écran peut être utile, mais ne remplace pas toujours l'export source ou une trace horodatée. Les preuves sont protégées contre les modifications, avec un accès limité et une durée de conservation définie. Appliquez la minimisation des données, surtout lorsque les preuves contiennent des informations personnelles ou des secrets.

## 12. Non-conformités et actions correctives

Une non-conformité est un écart par rapport à une exigence applicable ou à un critère défini. La correction traite l'écart visible ; l'action corrective traite sa cause afin de réduire la probabilité de réapparition. Rétablir un compte correctement configuré corrige un cas ; améliorer le processus d'approbation et ajouter une détection peut prévenir la répétition.

Le plan d'action précise le constat, le critère, la preuve, l'impact, la cause analysée, la correction immédiate, l'action corrective, le responsable, le budget, l'échéance, les dépendances, le risque temporaire et la méthode de vérification. Les dates doivent être réalistes ; les reports sont justifiés et approuvés. Un plan qui indique seulement « sensibiliser les équipes » ne montre ni la cause traitée ni le résultat attendu.

La vérification de clôture confirme que l'action a été réalisée et qu'elle fonctionne. Une procédure mise à jour doit être communiquée et appliquée. Un script déployé doit être testé sur le périmètre concerné. Une règle doit être évaluée sur des cas positifs et négatifs. Les risques résiduels doivent être réévalués plutôt que supposés nuls après la clôture d'un ticket.

~~~text
Écart constaté
     |
     v
Correction immédiate
     |
     v
Analyse de cause et facteurs contributifs
     |
     v
Action corrective avec responsable et échéance
     |
     v
Vérification d'efficacité
     |
     +--> échec : reprendre l'analyse
     |
     +--> succès : clôture et preuve
~~~

## 13. Exceptions et dérogations

Une exception autorise temporairement une situation qui s'écarte d'une règle interne, lorsque le cadre applicable le permet. Elle ne doit pas être utilisée pour contourner une obligation juridique impérative. La demande décrit la règle, le motif, le périmètre, la durée, les risques, les compensations, le responsable, l'autorité d'approbation, la date d'expiration et les critères de retrait.

Les mesures compensatoires doivent réduire le risque. Si un contrôle ne peut pas être appliqué immédiatement, une mesure alternative peut restreindre les accès, limiter le réseau, réduire la durée d'exposition ou augmenter la surveillance. La pertinence dépend du scénario. Une exception sans mesure compensatoire, sans échéance ni revue n'est pas une gestion de risque rigoureuse.

Centralisez les exceptions, classez-les par criticité et examinez-les régulièrement. Avant expiration, le propriétaire doit mettre le système en conformité ou demander une nouvelle décision justifiée. Les exceptions anciennes peuvent révéler une faiblesse structurelle : outil inadéquat, manque de budget, procédure irréaliste ou dette technique. La gouvernance doit faire remonter ces tendances à la direction.

~~~text
Demande d'exception
       |
       v
Obligation impérative ou règle interne ?
       |
       v
Motif + risque + mesures compensatoires
       |
       v
Approbation par autorité compétente
       |
       v
Expiration + revue + retrait ou renouvellement motivé
~~~

## 14. Fournisseurs et chaîne d'approvisionnement

Les fournisseurs peuvent accéder aux données, réseaux, identités, logiciels ou fonctions essentielles. La gouvernance évalue les fournisseurs selon leur criticité, leurs accès, les données traitées, les dépendances, le niveau de service, la concentration de risque et les conséquences d'une interruption. Une évaluation peut être légère pour un service peu critique et plus approfondie pour un fournisseur qui traite des données sensibles ou opère une fonction essentielle.

Avant la signature, les achats et les équipes concernées précisent les exigences de sécurité, confidentialité, notification d'incident, gestion des sous-traitants, auditabilité, continuité, restitution ou suppression des données, gestion des accès et fin de contrat. Les déclarations commerciales du fournisseur ne remplacent pas la lecture des clauses ni l'évaluation de preuves adaptées.

Pendant le contrat, surveillez les changements importants, incidents notifiés, résultats d'assurance, disponibilité, sous-traitants critiques, comptes d'accès et dates de renouvellement. Prévoyez un plan de sortie pour les services essentiels : export des données, transfert, suppression vérifiable, révocation des accès et solution de remplacement. Le risque fournisseur est évolutif, pas limité à la validation initiale.

~~~text
Fournisseur proposé
       |
       v
Criticité + accès + données + dépendances
       |
       v
Évaluation proportionnée et exigences contractuelles
       |
       v
Approbation + mise en service contrôlée
       |
       v
Surveillance, revue et plan de sortie
~~~

### 14.1 Responsabilités dans le cloud

Le modèle de responsabilité partagée varie entre infrastructure, plateforme et logiciel en tant que service, et dépend de chaque offre. Le fournisseur assume certaines couches ; le client en conserve d'autres, notamment les identités, données, configurations, permissions et usages. Consultez les documents contractuels et la matrice de responsabilité du service précis.

Une revue cloud devrait examiner les rôles privilégiés, la journalisation, la configuration des ressources, les sauvegardes, le chiffrement pertinent, la localisation si exigée, l'intégration des alertes et les procédures d'export. Une certification du fournisseur peut fournir une assurance limitée au périmètre et à la période couverts ; elle ne prouve pas que la configuration du client est correcte.

## 15. Protection des données et vie privée

La sécurité de l'information et la protection de la vie privée se recoupent, mais ne couvrent pas les mêmes questions. La sécurité préserve la confidentialité, l'intégrité et la disponibilité ; la protection de la vie privée examine aussi la manière dont les données relatives aux personnes sont collectées, utilisées, partagées, conservées et expliquées. Un traitement peut être techniquement sécurisé et néanmoins disproportionné ou incompatible avec les exigences applicables.

Cartographiez les catégories de données, les finalités, les acteurs, les destinataires, les transferts, les durées de conservation, les droits d'accès et les opérations à risque. Ne collectez pas plus de données que nécessaire pour l'objectif. Les données de test devraient être synthétiques ou anonymisées de manière appropriée. La pseudonymisation réduit certains risques mais n'est pas identique à une anonymisation irréversible.

La gouvernance prévoit la gestion des demandes des personnes, la réponse aux incidents de données, la suppression lorsque requise, les contrats de traitement et les évaluations de risque adaptées. Les obligations précises dépendent des lois et du contexte ; la fonction juridique ou protection des données doit confirmer les exigences. Ne copiez pas des données personnelles dans des outils d'analyse publics sans autorisation.

~~~text
Objectif métier
      |
      v
Données nécessaires à cette finalité ?
      |
      v
Base et obligations applicables validées
      |
      v
Minimisation + accès + conservation
      |
      v
Transparence, droits, sécurité et suivi
~~~

## 16. Conservation documentaire et preuves

Les preuves et enregistrements ont besoin d'une durée de conservation justifiée. Trop courte, elle peut empêcher une investigation ou l'audit d'un contrôle ; trop longue, elle augmente les coûts et les risques de confidentialité. Les règles dépendent des obligations, des contrats, du risque, du type de preuve et de la finalité. La politique précise ce qui est conservé, pourquoi, où, combien de temps, qui y accède et comment la suppression est vérifiée.

La gestion documentaire inclut le contrôle des versions, l'approbation, les droits, la classification, la revue périodique, la disponibilité et l'archivage. Les documents obsolètes doivent être remplacés ou retirés des espaces de travail pour éviter qu'une équipe applique une mauvaise version. Gardez l'historique lorsque nécessaire, mais marquez clairement la version courante.

Pour les éléments pouvant servir de preuve, la traçabilité et l'intégrité comptent particulièrement. Distinguez l'enregistrement natif, l'export, la transformation et le résumé. Les preuves générées automatiquement doivent comporter une source et des horodatages fiables. Si une donnée est supprimée selon une politique, conservez si approprié la preuve de l'exécution de la suppression sans garder inutilement le contenu qui devait être effacé.

## 17. Continuité d'activité et résilience

La gouvernance de sécurité doit être reliée à la continuité d'activité et à la reprise après sinistre. Une analyse d'impact métier identifie les fonctions essentielles, les dépendances, les impacts d'une interruption et les délais acceptables. RTO désigne généralement l'objectif de délai de rétablissement ; RPO représente l'objectif de perte de données acceptable exprimé dans le temps. Ces objectifs sont approuvés par le métier et testés, non seulement déclarés.

La continuité ne se limite pas aux sauvegardes. Elle inclut les personnes, procédures, accès d'urgence, dépendances fournisseurs, sites, réseau, DNS, identité, clés de chiffrement, documentation et capacité d'exploitation. Une sauvegarde récente mais non restaurable n'est pas une stratégie fiable. Un plan de continuité doit être exercé dans des conditions représentatives et ses résultats consignés.

Les tests mesurent le temps de restauration, l'intégrité, les dépendances oubliées, la qualité des données et les étapes manuelles. Après un exercice, mettez à jour les plans, responsabilités et priorités de financement. Les objectifs irréalistes doivent être renégociés ou accompagnés d'investissements.

~~~text
Fonction métier critique
       |
       v
Dépendances et impact d'interruption
       |
       v
RTO / RPO approuvés
       |
       v
Stratégie : redondance, sauvegarde, procédure alternative
       |
       v
Test réel + mesure + correction
~~~

## 18. Formation, culture et responsabilisation

La formation doit correspondre aux rôles. Une personne qui accepte des risques doit comprendre l'appétence, les responsabilités et les conséquences métier. Un administrateur doit connaître les exigences opérationnelles, la journalisation et la gestion des changements. Un acheteur doit identifier les clauses de sécurité et les points d'escalade fournisseur. Les utilisateurs ont besoin de consignes accessibles sur la protection des informations et le signalement des incidents.

Une formation achevée ne prouve pas nécessairement une compétence. Selon le risque, mesurez la compréhension, la capacité à appliquer une procédure, les résultats d'exercices et les erreurs récurrentes. Évitez d'utiliser un seul indicateur pour sanctionner automatiquement les personnes ; considérez aussi la clarté des règles, la charge, les outils disponibles et l'accompagnement.

Une culture de sécurité favorise le signalement rapide, la transparence des erreurs et l'apprentissage. Les équipes doivent savoir comment signaler une erreur ou une suspicion sans la dissimuler par crainte d'une sanction. La responsabilisation exige des attentes claires et une réponse cohérente, pas seulement des affiches ou un module annuel.

## 19. Gouvernance des changements et des projets

La sécurité doit être intégrée aux changements, acquisitions, projets et développements quand les choix de conception et de budget peuvent encore modifier le risque. Les critères de changement comprennent l'impact sur les données, les accès, les journaux, les fournisseurs, la continuité, les dépendances et les obligations. Les exceptions suivent le processus approuvé ; les changements urgents exigent une revue a posteriori lorsque la procédure le prévoit.

Les projets identifient qui accepte le risque, qui vérifie les exigences et quelles preuves seront produites avant la mise en production. Une revue de sécurité tardive peut découvrir des défauts coûteux à corriger. L'intégration précoce évite de traiter la conformité comme une phase documentaire après réalisation.

Pour chaque changement significatif, notez l'objectif, le périmètre, les risques, les tests, l'approbation, le plan de retour arrière, les résultats et les contrôles post-déploiement. Vérifiez que l'inventaire, les procédures, les contrats et la documentation sont mis à jour. Un système livré sans propriétaire ni budget de maintien crée une dette de gouvernance.

~~~text
Demande de changement
        |
        v
Impact sur risque, données, contrôles et contrats
        |
        v
Tests + approbation + plan de retour arrière
        |
        v
Mise en œuvre contrôlée
        |
        v
Vérification et mise à jour des preuves
~~~

## 20. Tableaux de bord à destination de la direction

Un tableau de bord exécutif aide à décider, il ne reproduit pas tout le détail des outils. Il présente les risques majeurs, les tendances, les écarts aux objectifs, les incidents significatifs, les fournisseurs critiques, les exceptions échues, la progression des actions correctives et les décisions attendues. Chaque métrique doit avoir une définition stable et un périmètre connu ; les comparaisons entre périodes ne sont utiles que si les méthodes restent cohérentes.

Le tableau de bord explique ce qui a changé et pourquoi. Un taux de conformité élevé peut masquer des exclusions importantes ou une absence de preuve. Une baisse des incidents peut refléter une collecte défaillante. Une liste de vulnérabilités ouvertes ne distingue pas nécessairement l'exposition réelle, l'actif critique et les contrôles compensatoires. Associez les chiffres à une interprétation, au niveau de confiance et à l'action proposée.

La direction a besoin d'une vue qui montre les arbitrages : budget nécessaire, risque accepté, impact attendu et date de révision. Les indicateurs techniques détaillés restent accessibles aux équipes opérationnelles. Un bon tableau de bord met en évidence les décisions qui ne peuvent pas être prises par les seules équipes techniques.

~~~text
Tableau exécutif
    |
    +--> Risques prioritaires et tendance
    +--> Écarts et obligations à échéance
    +--> Incidents et impacts majeurs
    +--> Contrôles critiques et preuves
    +--> Fournisseurs et continuité
    +--> Actions en retard / décisions requises
    |
    v
Arbitrage, propriétaire et prochaine revue
~~~

## 21. Erreurs fréquentes

**Erreur 1 : traiter la conformité comme une pile de documents.** Les documents doivent se traduire en contrôles, preuves et résultats. Si la procédure existe mais n'est pas exécutée, le risque demeure.

**Erreur 2 : considérer une certification comme une garantie générale.** Vérifiez le périmètre, les exclusions, la période, les réserves et le type d'assurance. Une attestation fournisseur ne vérifie pas toutes les configurations du client.

**Erreur 3 : multiplier les contrôles sans priorisation.** Un catalogue exhaustif peut surcharger les équipes et détourner les ressources des risques critiques. Sélectionnez les contrôles selon le contexte, les obligations et l'impact.

**Erreur 4 : laisser des exceptions sans expiration.** Une dérogation doit être approuvée, limitée, compensée et réévaluée.

**Erreur 5 : réduire le risque à une note.** La note peut masquer les hypothèses et l'incertitude. Conservez le scénario, les éléments, le propriétaire, les options et le risque résiduel.

**Erreur 6 : demander une preuve sans la protéger.** Les exports peuvent contenir des secrets ou des données personnelles. Minimisez, classez, limitez l'accès et définissez la rétention.

**Erreur 7 : traiter la responsabilité fournisseur comme un transfert total.** L'organisation doit comprendre les responsabilités conservées et vérifier les configurations qui lui incombent.

**Erreur 8 : mesurer seulement les activités.** Le nombre de formations, tickets ou scans ne démontre pas toujours un résultat. Mesurez l'efficacité et le risque.

~~~text
Document sans exécution       -> vérifier les preuves
Certification sans périmètre  -> lire les exclusions
Exception sans échéance       -> autorité, durée, revue
Score sans scénario           -> risque décrit et justifié
Métrique d'activité seule     -> résultat mesurable
Responsabilité floue          -> propriétaire et décideur
~~~

## 22. Travaux pratiques guidés

Les travaux pratiques utilisent l'organisation fictive Atelier Numérique. Aucun élément ne représente une organisation réelle. Chaque exercice produit des livrables concrets : registre, matrice, justification, preuve et action de suivi.

### TP 1 — Construire un registre des risques

**Objectif.** Évaluer et traiter un risque de gouvernance de manière structurée.

**Scénario.** Atelier Numérique fournit un portail client. Trois administrateurs disposent de privilèges élevés, mais la revue d'accès prévue tous les trimestres n'a pas été réalisée depuis neuf mois. Les journaux d'authentification sont activés et une procédure de récupération existe, mais le test de restauration date de plus d'un an.

**Étapes.** Rédigez deux scénarios de risque distincts : accès privilégié inapproprié et capacité de récupération incertaine. Décrivez les actifs et conséquences métier, les contrôles existants, les lacunes de preuve, le niveau provisoire et les options de traitement. Attribuez un propriétaire de risque et une date de revue. Distinguez le contrôle prévu du contrôle démontré.

**Livrable.** Registre contenant identifiant, scénario, impact, vraisemblance, contrôles, niveau, action, responsable, échéance et preuve de clôture.

**Correction attendue.** Le registre explique pourquoi les privilèges élevés et la revue en retard augmentent le risque sans affirmer qu'un compte est compromis. L'action immédiate peut inclure une revue d'accès approuvée, la réduction des privilèges inutiles et un test de restauration planifié. La priorité dépend de la criticité réelle du portail, de l'exposition et des objectifs de récupération.

**Critères de réussite.** Scénarios précis, hypothèses visibles, action mesurable, responsable nommé et preuve de réalisation prévue.

### TP 2 — Registre des obligations et des preuves

**Objectif.** Relier une exigence à un contrôle et à une preuve.

**Scénario.** Le contrat d'un client demande une notification des incidents selon un délai contractuel précis. La politique interne exige une revue trimestrielle des comptes privilégiés. L'organisation possède un guide de réponse à incident, mais aucun exercice récent n'est documenté.

**Étapes.** Créez trois entrées distinctes : exigence contractuelle, politique interne et préparation de réponse à incident. Notez la source, l'applicabilité, l'interprétation à valider, le propriétaire, la preuve attendue, la fréquence, les écarts et les actions. Ne supposez pas qu'un délai générique s'applique au contrat réel : indiquez que le délai exact doit être vérifié dans la version signée.

**Livrable.** Registre d'exigences, table de correspondance exigence-contrôle-preuve et liste des points à confirmer.

**Correction attendue.** Chaque entrée pointe vers une source identifiable et une personne responsable. La clause de notification exige le contrat signé et une validation juridique si sa portée est incertaine. La revue d'accès doit être prouvée par une liste de comptes, une approbation et le suivi des écarts. L'exercice doit être planifié puis appuyé par des résultats et des actions.

**Critères de réussite.** Distinction entre source juridique ou contractuelle et règle interne, preuves concrètes et aucun délai inventé.

### TP 3 — Mini-revue d'audit

**Objectif.** Établir un programme d'audit ciblé sur un contrôle important.

**Scénario.** L'organisation déclare que toutes les sauvegardes critiques sont testées régulièrement. L'auditeur doit vérifier cette affirmation sur trois systèmes sélectionnés, sans perturber la production.

**Étapes.** Définissez le critère, le périmètre, les systèmes échantillonnés, les preuves attendues, la période, les personnes à consulter et les limites. Demandez les résultats de sauvegarde et de restauration, la date du test, les erreurs, l'intégrité des données restaurées et l'approbation du propriétaire. Séparez la preuve qu'une sauvegarde a réussi de la preuve qu'une restauration est possible.

**Livrable.** Plan de test, demandes de preuves, grille de résultats et exemple de constat.

**Correction attendue.** La présence d'un journal de sauvegarde ne démontre pas qu'une restauration réussit. Le programme examine les preuves pour les systèmes échantillonnés et documente tout élément manquant. Si un test échoue, le constat identifie le critère non atteint, le risque et les actions sans généraliser au-delà de l'échantillon.

**Critères de réussite.** Critère mesurable, source traçable, échantillon justifié, impact métier considéré et constat rattaché aux preuves.

### TP 4 — Gouverner une exception et préparer la revue de direction

**Objectif.** Évaluer une exception et formuler une décision de direction.

**Scénario.** Un ancien système ne peut pas appliquer immédiatement un contrôle de chiffrement prévu par la norme interne. Il doit rester en service huit semaines à cause d'une dépendance métier. Il est segmenté du réseau utilisateur et accessible à un groupe limité, mais sa surveillance n'a pas été revue depuis deux mois.

**Étapes.** Documentez la règle, le motif, l'actif, le risque résiduel, les compensations, leur efficacité et les lacunes. Proposez une durée limitée, une autorité d'approbation, une surveillance renforcée et un plan de retrait ou de mise à niveau. Préparez une synthèse qui expose les options, les coûts, les risques et les décisions attendues.

**Livrable.** Fiche d'exception, plan de réduction du risque et une page de revue de direction.

**Correction attendue.** La segmentation et les accès restreints sont des compensations possibles, mais leur fonctionnement doit être testé. La surveillance en retard doit être corrigée. L'exception est limitée à la durée nécessaire, approuvée par une autorité adaptée et assortie d'une échéance, d'une revue et d'un plan de sortie. Si une obligation impérative s'applique, le processus interne ne peut pas la neutraliser.

**Critères de réussite.** Aucune acceptation non autorisée, date d'expiration, critères de retrait, propriétaire et décision clairement formulée.

## 23. Exercices corrigés

### Exercice 1 — Politique approuvée mais non suivie
Une politique est signée, mais aucune preuve d'exécution du contrôle n'existe.

**Correction.** L'approbation démontre l'existence de la règle, pas son fonctionnement. Vérifiez l'exécution, identifiez l'écart et mettez en place une preuve régulière ainsi qu'une action corrective.

### Exercice 2 — Certification fournisseur
Un fournisseur présente une attestation.

**Correction.** Vérifiez la validité, le périmètre, les exclusions, la période, les réserves et les services couverts. Évaluez aussi les responsabilités et configurations qui restent à la charge du client.

### Exercice 3 — Risque noté 9 sur 10
Un registre indique un score élevé sans scénario précis.

**Correction.** Reformulez le risque en événement, actifs et conséquences ; documentez les hypothèses de vraisemblance et d'impact ; associez les contrôles, le propriétaire et le traitement. Le score seul ne suffit pas.

### Exercice 4 — Exception sans échéance
Un système déroge à une règle depuis plusieurs années.

**Correction.** Revoyez l'applicabilité, le risque, les compensations et l'autorité d'approbation. Fixez une date de réexamen, un responsable et une stratégie de retrait. Une exception ne doit pas se prolonger sans décision révisée.

### Exercice 5 — Beaucoup de formations
La direction considère la sécurité efficace parce que 98 % des utilisateurs ont suivi la formation.

**Correction.** La participation est un indicateur d'activité. Complétez-la par des mesures de compréhension et des exercices adaptés, en tenant compte des limites de ces mesures.

### Exercice 6 — Obligation contractuelle incertaine
Une équipe ne connaît pas le délai de notification d'incident.

**Correction.** Consultez la version signée et le responsable contractuel, puis obtenez la validation juridique nécessaire. N'inventez pas une valeur ni n'appliquez automatiquement le délai d'un autre client.

### Exercice 7 — Revue d'accès annoncée
Le propriétaire dit que les accès sont revus mais ne dispose d'aucun résultat signé.

**Correction.** Demandez l'export, les critères, le réviseur, la date, les écarts et les tickets de correction. Si la preuve manque, enregistrez la limite et réalisez la revue réelle.

### Exercice 8 — Sauvegarde réussie
Les journaux disent que la tâche s'est terminée avec succès.

**Correction.** Cela démontre que la tâche a déclaré réussir selon sa source. Vérifiez aussi la couverture, l'intégrité et la capacité de restauration des systèmes critiques.

### Exercice 9 — Catalogue de contrôles copié
Une organisation copie toute une liste sans analyse.

**Correction.** Choisissez et adaptez les contrôles selon les risques, obligations, périmètre et résultats souhaités. Documentez les décisions d'applicabilité et leurs justifications.

### Exercice 10 — Contrôle absent jugé peu risqué
Un contrôle manque, mais les responsables estiment le risque faible.

**Correction.** Déterminez si le contrôle est une obligation impérative, contractuelle ou interne. Une appréciation du risque ne permet pas de supprimer à elle seule une obligation contraignante.

### Exercice 11 — Non-conformité répétée
Le même écart apparaît lors de trois audits.

**Correction.** Traitez les causes systémiques, les ressources, outils, formation et responsabilités, puis vérifiez l'efficacité de l'action corrective.

### Exercice 12 — Collecte d'audit trop large
L'auditeur demande tous les journaux de tous les systèmes sans expliquer la finalité.

**Correction.** Définissez le critère, le risque, la période et un échantillon pertinent. Appliquez la minimisation et ajustez la collecte à la question d'audit.

### Exercice 13 — Application cloud certifiée
Un fournisseur cloud possède une certification.

**Correction.** Examinez la portée de l'assurance et la répartition des responsabilités. Vérifiez la configuration client, les accès, les journaux et les options activées.

### Exercice 14 — RTO et RPO non testés
L'organisation annonce des objectifs sans exercice récent.

**Correction.** Réalisez un test autorisé qui mesure les résultats réels, note les dépendances et les écarts, puis ajustez la stratégie ou les objectifs approuvés.

### Exercice 15 — Données de test réelles
Une équipe copie des données de production vers un environnement de formation.

**Correction.** Vérifiez si l'usage est nécessaire et autorisé. Préférez des données synthétiques ou anonymisées, protégez les copies, limitez les accès et appliquez la rétention.

### Exercice 16 — Risque accepté par la mauvaise personne
Un administrateur accepte un risque majeur pour éviter un délai.

**Correction.** Vérifiez sa délégation et escaladez vers l'autorité adaptée. L'urgence ne remplace pas le processus d'acceptation, sauf procédure d'urgence préapprouvée et documentée.

### Exercice 17 — Fournisseur secondaire non évalué
Un fournisseur peut accéder à une base contenant des données sensibles.

**Correction.** Réévaluez la criticité selon l'accès et les données, définissez les contrôles et clauses adaptés, examinez les sous-traitants et vérifiez le processus d'accès et de sortie.

### Exercice 18 — Tableau de bord rassurant
Le nombre d'incidents baisse après une modification de collecte.

**Correction.** Vérifiez que les sources et règles fonctionnent toujours. La baisse pourrait refléter une perte de visibilité plutôt qu'une amélioration du risque.

### Exercice 19 — Preuve contenant des secrets
Un export de configuration contient des clés et jetons.

**Correction.** Protégez l'export, expurgez les secrets des copies de travail selon la procédure, limitez l'accès et ne partagez que les éléments nécessaires.

### Exercice 20 — Action corrective sans test
Une action est marquée terminée, mais aucun test n'a été réalisé.

**Correction.** La clôture est prématurée si l'efficacité doit être démontrée. Effectuez un test adapté, conservez la preuve et rouvrez l'action si le résultat ne correspond pas au critère attendu.

## 24. Défi final — Préparer une revue de gouvernance

**Scénario fictif.** Atelier Numérique possède un portail client, des comptes privilégiés, un fournisseur cloud et une application héritée. Le registre contient trois risques élevés, dont un sans propriétaire. La revue d'accès privilégié est en retard. Le fournisseur présente une attestation dont le périmètre n'a pas été vérifié. L'application héritée bénéficie d'une exception sans échéance, et la dernière restauration testée ne respecte pas l'objectif de récupération fixé par le métier.

**Travail demandé.** Préparez une fiche de synthèse de direction. Distinguez les faits connus, les hypothèses et les informations manquantes. Proposez une priorité, un responsable et une échéance pour chaque écart. Indiquez les décisions à approuver, les preuves attendues et les risques qui ne peuvent pas être acceptés sans validation supplémentaire. Construisez une feuille de route sur 30, 60 et 90 jours avec des critères de réussite.

**Correction détaillée.**

1. **Risque sans propriétaire.** Nommer un responsable métier et une autorité de décision. Clarifier le scénario, l'impact, les contrôles et le niveau résiduel avant toute acceptation.
2. **Revue d'accès en retard.** Prioriser les comptes à privilèges, vérifier le périmètre, faire approuver la liste et suivre les suppressions ou corrections. La preuve finale doit montrer la revue et la résolution des exceptions.
3. **Attestation du fournisseur.** Vérifier la validité, le périmètre, les exclusions, les responsabilités partagées et les risques non traités. Une certification n'est pas une preuve générale de configuration correcte.
4. **Exception sans échéance.** Examiner sa validité, l'obligation liée, les mesures compensatoires et l'autorité. Si elle est permise, fixer une durée, une revue et un plan de sortie. Si une exigence impérative s'applique, escalader sans supposer qu'une exception interne suffit.
5. **Récupération hors objectif.** Analyser le délai réel, les dépendances et la cause, puis obtenir une décision du propriétaire métier sur la stratégie et le budget. Refaire un test représentatif et conserver les résultats.
6. **Feuille de route.** Dans les 30 jours, assigner les propriétaires, lancer la revue d'accès et clarifier l'exception. Dans les 60 jours, achever l'évaluation du fournisseur, corriger les écarts prioritaires et documenter le plan de récupération. Dans les 90 jours, réaliser les tests, mesurer les résultats, réviser les risques et faire approuver les risques résiduels.
7. **Tableau de bord.** Afficher l'écart, le risque, le propriétaire, l'échéance, la preuve attendue, les dépendances et la décision demandée. Ne déclarez pas les actions terminées avant vérification d'efficacité.

**Barème sur 100 points.** Clarté des risques : 15. Responsabilités et autorités : 15. Analyse de la preuve : 15. Traitement des exigences : 15. Priorisation et échéances : 15. Mesures de récupération : 10. Tableau de bord et critères de succès : 15.

## 25. Liste de contrôle opérationnelle

Avant une revue, définissez les objectifs, le périmètre, les parties prenantes et les exigences applicables. Vérifiez les versions de politiques, dates de révision, responsables, exceptions et preuves. Pour chaque risque important, assurez-vous que le scénario, le propriétaire, les contrôles, le niveau résiduel et la décision sont documentés. Reliez les obligations contractuelles et juridiques à des sources précises et à des responsables.

Pendant la mise en œuvre, associez chaque contrôle à un critère de réussite, une fréquence, une source de preuve, un propriétaire et une procédure d'escalade. Protégez les preuves, minimisez les données sensibles et évitez les exports inutiles. Les constats d'audit ont une action corrective, un responsable, une échéance et une vérification de résultat. Les exceptions ont une justification, une autorité, une expiration et des mesures compensatoires.

Après la revue, mettez à jour le profil de risque, le tableau de bord et le plan d'amélioration. Remontez les arbitrages qui dépassent la délégation du gestionnaire. Vérifiez la réalisation des décisions antérieures. Une gouvernance utile rend visibles les risques importants, aide à choisir les priorités et démontre les résultats, pas seulement la production de documents.

~~~text
[ ] Périmètre et exigences applicables confirmés
[ ] Politiques, versions et propriétaires à jour
[ ] Registre des risques et décisions actualisés
[ ] Contrôles associés à des preuves vérifiables
[ ] Exceptions datées, approuvées et réexaminées
[ ] Fournisseurs critiques évalués
[ ] Audit et actions correctives suivis
[ ] Indicateurs interprétés et sources contrôlées
[ ] RTO / RPO testés selon les priorités
[ ] Revue de direction et décisions consignées
~~~

## 26. Glossaire

**Appétence au risque.** Niveau et type de risque qu'une organisation est disposée à poursuivre pour atteindre ses objectifs.

**Audit.** Évaluation structurée par rapport à des critères définis à partir d'éléments probants.

**Contrôle.** Mesure, processus ou mécanisme conçu pour modifier le risque ou obtenir un résultat attendu.

**Conformité.** Respect et démonstration des exigences applicables, juridiques, réglementaires, contractuelles ou internes.

**Déclaration d'applicabilité (SoA).** Document du SMSI recensant les contrôles pertinents, leur statut et les justifications requises.

**Exception.** Dérogation limitée à une règle interne, si le cadre applicable le permet, avec autorité, compensation et réexamen.

**KPI.** Indicateur de performance mesurant un résultat ou une activité par rapport à un objectif.

**KRI.** Indicateur servant à surveiller le niveau ou l'évolution d'un risque.

**ISO/IEC 27001.** Norme définissant les exigences d'un système de management de la sécurité de l'information.

**NIST CSF 2.0.** Cadre de résultats pour comprendre, prioriser et communiquer la gestion des risques cyber.

**NIST SP 800-53.** Catalogue adaptable de contrôles de sécurité et de protection de la vie privée.

**Non-conformité.** Écart par rapport à une exigence ou un critère applicable.

**Risque inhérent.** Risque évalué avant prise en compte des contrôles, selon la méthode adoptée.

**Risque résiduel.** Risque qui subsiste après les mesures de traitement retenues.

**RACI.** Matrice clarifiant les rôles de réalisation, d'approbation, de consultation et d'information.

**RPO.** Objectif de perte de données acceptable mesuré dans le temps.

**RTO.** Objectif de délai de rétablissement après interruption.

**SMSI.** Système de management de la sécurité de l'information.

**Preuve.** Élément vérifiable soutenant une affirmation sur l'exécution ou l'efficacité d'un contrôle.

**Propriétaire du risque.** Personne ou fonction redevable de la surveillance et des décisions relatives à un risque.

## 27. Références officielles

- NIST Cybersecurity Framework 2.0 : https://www.nist.gov/cyberframework
- NIST, FAQ du CSF et précisions sur Govern, les profils et l'usage du cadre : https://www.nist.gov/cyberframework/faqs
- NIST CSF 2.0, document de référence : https://doi.org/10.6028/NIST.CSWP.29
- NIST SP 800-53 Rev. 5, catalogue des contrôles et mises à jour : https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- NIST SP 800-37 Rev. 2, Risk Management Framework : https://csrc.nist.gov/pubs/sp/800/37/r2/final
- ISO/IEC 27001:2022, exigences du SMSI : https://www.iso.org/standard/27001
- NIST Privacy Framework : https://www.nist.gov/privacy-framework
- NIST CSF 2.0 Implementation Examples : https://www.nist.gov/document/csf-20-implementations-pdf

Les référentiels évoluent. Consultez les pages officielles pour confirmer les versions, errata, amendements et ressources disponibles. Un référentiel ne remplace pas l'analyse des lois et contrats qui s'appliquent à une organisation particulière. Ce cours fournit une méthode d'étude ; il ne constitue ni un avis juridique ni une déclaration de conformité.

## 28. Synthèse finale

La gouvernance et la conformité donnent une structure de décision à la cybersécurité. Elles relient les objectifs métier, la tolérance au risque, les rôles, les exigences applicables, les contrôles, les preuves et l'amélioration continue. Le risque est décrit comme un scénario concret, confié à un propriétaire, traité par des mesures adaptées et réévalué à partir de preuves.

Le CSF 2.0 aide à organiser les résultats attendus ; ISO/IEC 27001 structure un SMSI ; les catalogues tels que NIST SP 800-53 soutiennent la sélection de contrôles. Ces ressources doivent être appliquées avec discernement et reliées au contexte réel. La conformité n'est ni un nombre de documents ni une certification universelle : elle repose sur les exigences réellement applicables et sur des preuves fiables.

Enfin, une gouvernance efficace sait dire qui décide, pourquoi, sur quelles informations, avec quel risque résiduel et à quel moment la décision sera réexaminée. Elle ne cache pas les écarts ; elle les rend visibles, attribue des actions correctives et vérifie leur efficacité. Cette discipline transforme la cybersécurité en capacité durable de l'organisation.

Fin du cours.