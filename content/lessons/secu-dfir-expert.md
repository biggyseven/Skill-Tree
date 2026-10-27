# Réponse à incident (DFIR)

> **Mise en contexte**

Une alerte signale une authentification inhabituelle, un poste commence à communiquer avec une destination inconnue et un serveur critique ralentit. Les équipes ne peuvent pas se contenter de supprimer un fichier ou de redémarrer la machine : elles doivent vérifier si un incident s'est produit, limiter les dommages, préserver les preuves, comprendre l'étendue, restaurer les services et empêcher une récidive. La réponse à incident et l'investigation numérique, souvent regroupées sous l'acronyme DFIR pour Digital Forensics and Incident Response, associent des décisions opérationnelles rapides à une analyse méthodique.

Ce cours est conçu pour la défense, la coordination d'équipes et les environnements autorisés. Les scénarios sont fictifs et les travaux pratiques utilisent des journaux synthétiques. Les actions de confinement, de collecte ou de restauration sur des systèmes réels doivent être approuvées et réalisées selon les procédures de l'organisation. Le meilleur choix technique dépend du risque, du périmètre, de la criticité métier, de l'état des preuves et de l'autorité de décision.

## 1. Objectifs et résultats attendus

À la fin du cours, vous saurez reconnaître les étapes d'une réponse structurée, organiser le triage d'une alerte, déclarer et qualifier un incident, tenir un journal des décisions, coordonner les équipes, protéger les actifs critiques, planifier la collecte et la conservation des preuves, contenir une activité malveillante, préparer l'éradication et vérifier une restauration. Vous saurez également produire un rapport post-incident, définir des indicateurs de suivi et transformer les enseignements en améliorations concrètes.

L'objectif n'est pas de mémoriser une suite fixe de commandes. Un incident de rançongiciel, une exposition de données, un compte compromis, une panne réseau et une compromission cloud n'ont ni les mêmes risques ni les mêmes priorités. La méthode offre un cadre commun, tandis que les décisions se personnalisent en fonction de l'impact, de l'incertitude et des contraintes métier.

Il faut distinguer quatre notions. Un **événement** est une activité observée. Une **alerte** est un signal émis par un outil ou une personne. Un **incident de sécurité** est un événement ou un ensemble d'événements qui répond aux critères internes de qualification et peut affecter la confidentialité, l'intégrité ou la disponibilité. Une **crise** exige une coordination élargie en raison de son ampleur, de son impact ou des obligations de communication. Une alerte n'est donc pas automatiquement un incident confirmé, mais une alerte crédible ne doit pas être ignorée au motif que toutes les preuves ne sont pas encore disponibles.

~~~text
Signal / déclaration
        |
        v
Triage et validation initiale
        |
        v
Qualification + priorité
        |
        v
Coordination et journal de décision
        |
        v
Confinement proportionné
        |
        v
Investigation et collecte en parallèle
        |
        v
Éradication puis récupération vérifiée
        |
        v
Clôture, retour d'expérience et améliorations
~~~

## 2. Gouvernance, rôles et autorité

La réponse est une activité d'équipe. La personne qui détecte un signal n'est pas nécessairement celle qui autorise l'isolation d'un système critique, la désactivation d'un compte privilégié ou la communication aux clients. Définissez les rôles avant la crise : responsable d'incident, analystes techniques, responsable du service, équipe réseau, identité, cloud, juridique, protection des données, communication, direction et fournisseurs concernés. Selon l'organisation, une seule personne peut cumuler des rôles, mais la décision et son approbation doivent rester explicites.

Le responsable d'incident maintient la vue d'ensemble, fixe les objectifs immédiats, arbitre les priorités selon les délégations reçues, organise les points de situation et suit les actions. Les analystes formulent les hypothèses et proposent des mesures. Les équipes opérationnelles exécutent les changements approuvés et évaluent leur impact sur la disponibilité. Les fonctions juridique et protection des données déterminent les obligations pertinentes avec les responsables compétents. Les communications externes sont coordonnées par les personnes désignées.

Une matrice RACI — responsable de réalisation, autorité redevable, consulté, informé — peut clarifier qui exécute et qui approuve. Il ne faut toutefois pas laisser la matrice ralentir une action urgente déjà prévue dans une procédure approuvée. Le plan doit définir à l'avance les actions automatiques autorisées, les seuils d'escalade et les personnes de garde.

~~~text
Responsable d'incident
     |
     +--> Investigation / DFIR
     +--> Réseau et infrastructure
     +--> Identités et postes
     +--> Services métier
     +--> Juridique / données / communication
     |
     v
Décisions enregistrées, propriétaires et échéances
~~~

## 3. Préparation avant l'incident

La réponse commence bien avant la première alerte. L'organisation doit connaître ses actifs, leurs propriétaires, les dépendances critiques, les méthodes d'accès d'urgence et les sauvegardes disponibles. Les journaux utiles doivent être activés, synchronisés, protégés contre les modifications et conservés assez longtemps pour couvrir la détection et l'investigation. Les contacts d'urgence doivent être joignables ; les accès hors bande doivent être testés, pas seulement décrits dans un document.

Préparez des modèles : fiche d'incident, chronologie, journal des décisions, matrice d'impact, demande de conservation de preuve, plan de communication, checklist de récupération et compte rendu. Documentez les critères de gravité et les seuils d'escalade. La préparation inclut aussi les capacités des fournisseurs, les procédures de déclaration, les contraintes réglementaires, les exigences contractuelles et la gestion des identifiants d'urgence.

Les exercices de table testent les décisions et la coordination sans toucher aux systèmes réels. Les exercices techniques doivent employer un environnement isolé, une autorisation claire et des critères de sécurité. Après chaque exercice, notez les blocages : manque de droits, contacts obsolètes, sauvegarde non testée, données de télémétrie absentes ou ambiguïté sur l'autorité de décision.

~~~text
Avant l'incident
    |
    +--> Inventaire et criticité des actifs
    +--> Journaux activés et heures synchronisées
    +--> Sauvegardes testées et accès d'urgence
    +--> Procédures, contacts et délégations
    +--> Exercices et plans de communication
    |
    v
Capacité de réponse prête à être mobilisée
~~~

## 4. Détection, signalement et triage

Le triage vise à déterminer rapidement ce qui est connu, ce qui est incertain et ce qui doit être protégé en premier. Recueillez la source de l'alerte, l'heure de détection, l'actif, l'identité, le comportement observé, la règle qui a déclenché le signal, les données associées et l'impact apparent. Évitez d'effacer ou de fermer une alerte avant de préserver les éléments pertinents. Vérifiez si plusieurs alertes correspondent au même événement ou si elles représentent des sources indépendantes.

Un triage défensif se concentre sur la criticité de l'actif, la probabilité d'une activité non autorisée, l'activité en cours, l'étendue possible et le dommage potentiel. Une alerte sur un système d'identité central peut mériter une priorité élevée même si les preuves initiales sont limitées. À l'inverse, un signal isolé sur un poste de test peut nécessiter une validation avant une isolation qui perturberait une activité critique.

Les critères de décision doivent être écrits. Par exemple : activité destructive en cours, propagation observée, accès privilégié suspect, données potentiellement exposées, impact sur plusieurs services, ou impossibilité de maintenir des contrôles de sécurité. Chaque organisation doit adapter les seuils à son contexte et les réviser à la lumière des incidents passés.

~~~text
Alerte reçue
    |
    v
Actif critique ou activité en cours ?
    |
  +--+--+
  |     |
 oui    non / inconnu
  |     |
Escalade rapide   Collecte initiale et validation
  |     |
  +-----+
    |
    v
Décision tracée : fermer, surveiller ou déclarer incident
~~~

### 4.1 Éviter les décisions hâtives

Une alerte peut être un faux positif, un comportement administratif légitime ou un indicateur incomplet. Mais attendre la certitude totale avant toute action peut permettre à un attaquant de poursuivre son activité. Adoptez une approche à deux voies : une qualification technique qui améliore progressivement les preuves, et des mesures de protection réversibles ou préapprouvées pour limiter les risques immédiats.

Distinguez l'observation du jugement. « Le fournisseur d'identité a enregistré cinq échecs puis une réussite » est une observation. « Le compte est compromis » est une hypothèse qui exige d'autres éléments. La réponse peut néanmoins appliquer une vérification renforcée ou suspendre temporairement une session si les règles approuvées le prévoient. Consignez la raison, les risques et les critères de retour arrière.

## 5. Classification, priorité et impact métier

Un modèle de sévérité peut combiner l'impact sur la confidentialité, l'intégrité et la disponibilité, la criticité des actifs, l'étendue, les privilèges touchés, la persistance éventuelle, l'activité actuelle, les obligations de déclaration et les dépendances métier. Une note unique facilite la coordination mais ne remplace pas un résumé de situation. Deux incidents classés « élevés » peuvent exiger des stratégies différentes : l'un peut menacer la disponibilité d'un service, l'autre l'exposition de données.

L'impact technique doit être traduit en conséquences compréhensibles : service interrompu, utilisateurs affectés, intégrité non garantie, perte de données, accès non autorisé potentiel, coûts de restauration, engagements clients ou risques réglementaires. Indiquez ce qui est confirmé, estimé et inconnu. Ne transformez pas une capacité théorique en impact réalisé sans preuve.

Réévaluez la sévérité quand les faits évoluent. Un incident limité peut devenir majeur après découverte d'un compte privilégié compromis ou d'un second site touché. À l'inverse, une alerte initialement critique peut être requalifiée après validation, sans effacer le raisonnement original. Conservez l'historique du niveau, du motif du changement et de la personne responsable.

~~~text
Impact métier
    +
Étendue observée
    +
Privilèges / persistance
    +
Activité en cours
    +
Données et obligations
    |
    v
Sévérité provisoire + justification + prochain réexamen
~~~

## 6. Déclarer l'incident et ouvrir un dossier

Lorsqu'un événement répond aux critères de déclaration, créez un identifiant unique et un dossier d'accès contrôlé. Enregistrez le déclarant, la première détection, la fenêtre connue, les systèmes potentiellement affectés, la description neutre, les décisions prises, les équipes impliquées et les questions ouvertes. Le dossier doit être mis à jour au fil de l'investigation. N'utilisez pas des noms accusatoires ou des conclusions définitives avant qu'elles ne soient étayées.

Le journal de décisions doit rendre la réponse compréhensible après coup : quelle décision a été prise, quand, par qui, sur quelles informations, avec quelle justification, quels risques ont été acceptés et quelles suites sont attendues. Une conversation dans un canal de discussion peut aider à coordonner l'équipe, mais les décisions significatives doivent être reportées dans le dossier de référence selon la politique de conservation.

Le statut peut suivre une liste cohérente, par exemple nouveau, en triage, déclaré, contenu, en éradication, en récupération, en surveillance, clôturé. Les transitions doivent avoir des critères. « Contenu » ne signifie pas que l'attaquant est éliminé ; « restauré » ne signifie pas que toutes les causes sont corrigées ; « clôturé » ne signifie pas qu'aucune amélioration ne soit requise.

~~~text
ID : IR-2026-042
Statut : déclaré / qualification en cours
Responsable : désigné
Périmètre initial : LAB-07 et services dépendants
Faits confirmés : selon les sources référencées
Actions en cours : propriétaire + échéance
Décisions : heure + auteur + justification
Inconnues : élément manquant + prochaine vérification
~~~

## 7. Communication et rythme de situation

Pendant un incident, la communication doit être fréquente, cohérente et limitée aux personnes qui en ont besoin. Définissez un canal de coordination, un format de mise à jour et une fréquence de situation. Une bonne mise à jour répond à six questions : que s'est-il passé, quels systèmes sont affectés, quel impact est confirmé, quelles actions sont engagées, quels risques restent ouverts et quelle décision est attendue ?

Évitez les messages différents envoyés par plusieurs équipes avec des gravités incompatibles. Le responsable d'incident conserve un résumé de référence avec l'heure de mise à jour et le niveau de confiance. Les informations sensibles, les données personnelles et les détails susceptibles d'aggraver le risque ne doivent pas être diffusés largement. Les communications clients, autorités, partenaires et médias suivent les délégations et obligations qui s'appliquent.

Dans les environnements distribués, tenez compte des fuseaux horaires et désignez les personnes qui prennent le relais. Un transfert entre équipes doit inclure l'état actuel, les actions déjà réalisées, les hypothèses, les preuves importantes, les risques et les prochaines échéances. Un relais oral sans mise à jour du dossier augmente le risque de répétition ou d'oubli.

~~~text
Point de situation
    |
    +--> Faits confirmés
    +--> Impact actuel et tendance
    +--> Actions / responsables / échéances
    +--> Risques et inconnues
    +--> Décisions attendues
    +--> Heure du prochain point
~~~

## 8. Préserver les preuves pendant la réponse

Une action de défense peut modifier des données utiles. Isoler un poste, arrêter un processus, désactiver un compte, redémarrer un serveur ou restaurer un fichier peut être nécessaire pour limiter l'impact, mais cela change potentiellement l'état du système. Le but n'est pas de préserver chaque donnée à tout prix : il faut choisir le compromis adapté, protéger d'abord les personnes et les services critiques, puis conserver les éléments nécessaires dans la mesure raisonnable.

Avant l'action, si le temps et le risque le permettent, relevez l'état, les alertes, les sessions, les connexions, les horodatages et les éléments volatils utiles. Prenez des empreintes des fichiers ou exports lorsque pertinent. Documentez l'heure et la raison de la mesure ainsi que ses effets attendus. Si l'urgence impose de contenir avant de collecter, consignez pourquoi et les données qui risquent d'avoir été perdues.

La chaîne de conservation identifie l'origine, le collecteur, les outils et versions, les heures, les transformations, les emplacements et les accès. Les journaux et captures peuvent contenir des informations sensibles. Stockez-les avec des permissions restrictives, une rétention définie et un accès auditable. Une copie de travail doit être séparée de l'original selon les procédures applicables.

~~~text
Action défensive proposée
       |
       v
Risque immédiat de dommage ?
       |
  +----+----+
  |         |
oui        maîtrisé
  |         |
Contenir selon   Préserver si utile et autorisé
procédure        avant l'action
  |         |
  +----+----+
       |
       v
Documenter heure, décideur, effet et preuves restantes
~~~

## 9. Confinement : objectif, options et arbitrages

Le confinement vise à empêcher l'incident de s'étendre ou de continuer à causer des dommages. Les options peuvent inclure l'isolation d'un endpoint, le blocage d'une destination confirmée, la révocation d'une session, la désactivation temporaire d'un compte, la restriction d'un rôle cloud, l'arrêt d'un accès distant, la séparation d'un segment ou l'activation d'une règle de protection. La méthode doit correspondre au scénario et au périmètre autorisé.

Il n'existe pas de bouton universel « contenir ». Isoler un serveur peut interrompre une chaîne de production ; désactiver un compte de service peut arrêter des intégrations ; bloquer une adresse d'hébergement partagé peut affecter des services légitimes. Évaluez l'effet métier, les dépendances, les moyens d'accès d'urgence, les exceptions approuvées et le plan de retour arrière. Dans une crise importante, le responsable d'incident coordonne les décisions avec les propriétaires métier et l'autorité désignée.

Le confinement doit être vérifiable. Après l'action, contrôlez que l'état attendu a été appliqué, recherchez des signes de continuation et consignez les exceptions. Une règle sur un seul indicateur peut être contournée si d'autres chemins existent. Un compte désactivé peut conserver des sessions actives dans certains services. La vérification porte donc sur l'objectif atteint et non sur la seule réussite de la commande.

~~~text
Hypothèse de propagation
       |
       v
Choisir un contrôle adapté
       |
       v
Évaluer impact et dépendances
       |
       v
Approbation selon la procédure
       |
       v
Appliquer + vérifier + consigner
       |
       v
Surveillance des voies alternatives
~~~

### 9.1 Confinement court terme et long terme

Le confinement court terme réduit rapidement le dommage, parfois au prix d'une perturbation importante ou d'une solution temporaire. Le confinement long terme construit une position stable qui protège le réseau et permet de poursuivre l'investigation : segmentation renforcée, accès conditionnel, limitation des privilèges, filtrage ciblé, renforcement de la journalisation et validation des chemins d'administration.

Toute mesure temporaire doit porter un propriétaire, une date d'expiration ou une condition de retrait, des tests et une méthode de retour arrière. Sinon, une exception d'urgence peut devenir un contrôle permanent mal documenté. Les changements de confinement doivent être suivis comme des changements de production.

## 10. Identités et accès pendant l'incident

De nombreux incidents impliquent une identité, une session, un jeton, un secret technique ou un rôle excessif. Les actions de réponse peuvent inclure révocation de sessions, rotation de secrets, suspension d'un compte, contrôle MFA renforcé, réduction des privilèges et vérification des connexions. Ces actions doivent s'appuyer sur la procédure d'identité et sur une évaluation des dépendances ; la révocation indiscriminée peut bloquer des services critiques ou compliquer l'accès d'urgence.

Différenciez le compte humain, le compte de service, le principal d'application, la clé d'accès et le jeton de session. Un changement du mot de passe ne révoque pas forcément toutes les sessions ou les secrets non interactifs. Recherchez les moyens d'accès associés selon les journaux disponibles, puis planifiez la rotation dans un ordre qui ne casse pas les services sans contrôle. Les secrets exposés ne doivent pas être copiés dans le dossier d'incident ; consignez leur identifiant, leur emplacement logique et l'action de rotation.

Après le changement, vérifiez les journaux d'authentification, les échecs attendus, les applications dépendantes et la réapparition d'activité suspecte. Si un compte privilégié est en cause, vérifiez les accès de secours, la séparation des rôles et les actions effectuées durant la fenêtre. Documentez ce qui a été révoqué, ce qui reste en circulation et comment le confirmer.

~~~text
Compte ou session suspecte
       |
       v
Identifier type, privilèges et dépendances
       |
       v
Choisir révocation / suspension / rotation
       |
       v
Appliquer selon l'autorité définie
       |
       v
Vérifier sessions résiduelles et usages de service
~~~

## 11. Investigation technique en parallèle

Le confinement et l'investigation peuvent progresser en parallèle. L'équipe DFIR cherche la chronologie, le vecteur initial possible, les identités touchées, les hôtes impliqués, les actions observées et les preuves d'impact. L'équipe d'exploitation applique les mesures de protection. Le responsable d'incident synchronise les deux voies et s'assure que les conclusions utilisées pour une action sont suffisamment solides.

Définissez pour chaque hypothèse la source qui permettrait de la tester. Pour un accès suspect : journaux d'authentification, MFA, adresse source, appareil, méthode d'accès et événements de session. Pour un processus suspect : arbre de processus, chemin, hash, signature, compte et événements endpoint. Pour une exposition réseau : DNS, proxy, pare-feu, flux et capture selon disponibilité. Pour un impact cloud : audit API, changements de rôle, ressources et journaux de contrôle.

Ne collectez pas sans limite. Définissez la fenêtre de temps, les systèmes, les champs et le motif. Conservez les requêtes de recherche, les résultats bruts pertinents et les limites. Si une source manque, écrivez-le et demandez une autre source. Distinguez les faits confirmés, les inférences et les hypothèses ; ne forcez pas une attribution si les preuves restent insuffisantes.

~~~text
Hypothèse H1 : compte utilisé sans autorisation
        |
        +--> Journaux IAM / MFA / appareil
        |
Hypothèse H2 : poste impliqué
        |
        +--> EDR / processus / fichiers
        |
Hypothèse H3 : communication sortante
        |
        +--> DNS / proxy / pare-feu / flux
        |
        v
Chronologie + preuves + alternatives + incertitudes
~~~

## 12. Éradication : supprimer les causes et les accès persistants

L'éradication vise à éliminer les composants de compromission identifiés et les conditions qui permettraient à l'incident de se reproduire. Selon le scénario, cela peut exiger une reconstruction, la suppression contrôlée d'un composant, une correction de configuration, la fermeture d'un accès, la rotation d'identifiants ou l'application d'un correctif. La suppression d'un fichier observé ne suffit pas si des comptes, tâches, clés ou chemins d'accès persistants sont encore présents.

Avant l'éradication, vérifiez que l'activité est suffisamment contenue, que les éléments nécessaires ont été préservés et que l'étendue est assez bien comprise pour planifier la correction. Définissez les critères de réussite, les responsables, l'ordre des systèmes, les dépendances et un plan de retour arrière. Une action précipitée peut supprimer des preuves, détruire une configuration utile ou laisser la cause initiale intacte.

Après la mesure, effectuez des contrôles indépendants. Vérifiez les actifs concernés, les identités, les règles, les services et les sources de télémétrie. Recherchez des signes de retour, notamment via des chemins d'accès alternatifs ou des systèmes qui n'étaient pas encore inclus dans la fenêtre. Si une nouvelle activité est détectée, revenez à l'investigation et réévaluez l'étendue au lieu de déclarer l'incident terminé.

~~~text
Activité contenue
       |
       v
Éléments critiques préservés ?
       |
       v
Étendue et cause assez comprises ?
       |
       v
Plan d'éradication approuvé
       |
       v
Retirer composants / accès / vulnérabilités
       |
       v
Vérification indépendante et surveillance
~~~

## 13. Récupération et retour en service

La récupération remet les systèmes et services en fonctionnement selon un plan vérifié. Elle peut inclure reconstruction à partir d'une image de confiance, restauration de données, réapplication de correctifs, rotation de secrets, rétablissement de configurations, tests métier et reconnexion progressive au réseau. Une sauvegarde n'est utile que si elle est intègre, exploitable et antérieure à la compromission ; le point de restauration doit être choisi en évaluant le risque de remettre en service des composants compromis.

La restauration doit se faire par étapes, avec des critères de passage : état de sécurité vérifié, comptes et secrets corrigés, vulnérabilité initiale traitée, journaux disponibles, contrôles de détection actifs et tests fonctionnels réussis. Une reconnexion complète sans surveillance peut permettre à l'incident de reprendre. Un retour progressif limite l'impact et donne la possibilité de détecter rapidement une anomalie.

N'oubliez pas l'intégrité des données et la communication aux utilisateurs. Certains services peuvent redémarrer mais afficher des données incohérentes. Les tests doivent couvrir la fonction métier, la sécurité et les dépendances. Documentez les versions reconstruites, les jeux de données restaurés, les validations effectuées et les exceptions qui restent ouvertes.

~~~text
Source de restauration vérifiée
        |
        v
Reconstruction / restauration contrôlée
        |
        v
Correctifs + rotation de secrets + durcissement
        |
        v
Tests techniques et métier
        |
        v
Reconnexion progressive
        |
        v
Surveillance renforcée + approbation du propriétaire
~~~

### 13.1 Sauvegardes et preuve de récupération

Vérifiez les sauvegardes avant d'en dépendre : date, intégrité, couverture, isolation, contrôle d'accès et tests de restauration. Les sauvegardes connectées avec les mêmes privilèges que la production peuvent être exposées au même incident. La restauration d'une sauvegarde doit s'accompagner d'une vérification que le vecteur initial et les accès compromis ont été corrigés.

Les tests de récupération doivent mesurer le délai de remise en service et la perte de données tolérable, conformément aux objectifs définis par les métiers. Les objectifs RTO et RPO doivent être réalistes et testés. Consignez les écarts entre les objectifs déclarés et le résultat réellement obtenu.

## 14. Scénarios de réponse et priorités spécifiques

### 14.1 Rançongiciel ou chiffrement massif

Priorité : protéger les services et réduire la propagation. Activez le plan de crise, identifiez les systèmes affectés et les dépendances, protégez les sauvegardes, vérifiez les voies d'accès distantes et coordonnez l'isolation avec les responsables métier. Préservez les preuves accessibles quand cela est compatible avec la protection urgente. Évitez de reconnecter les systèmes ou de restaurer avant que les conditions de compromission soient suffisamment comprises.

Ne promettez pas qu'une sauvegarde est saine avant de l'avoir vérifiée. L'absence d'un fichier de rançon sur un hôte n'exclut pas un impact ailleurs. Organisez l'inventaire des services, les priorités de récupération, les mises à jour de situation et les critères de retour en production. Les décisions de paiement, de communication et de notification relèvent des personnes autorisées et des cadres juridiques applicables.

### 14.2 Compromission d'identité

Priorité : stopper les sessions et accès non autorisés sans couper aveuglément les services essentiels. Identifiez les comptes, rôles, jetons, clés et systèmes qui peuvent être affectés. Révoquez ou faites tourner les secrets selon un plan qui inclut les comptes de service. Examinez les actions privilégiées, les changements de règles et les nouveaux accès. Vérifiez ensuite que l'activité ne se poursuit pas par une autre identité ou un jeton résiduel.

### 14.3 Exposition potentielle de données

Priorité : confirmer quelles données, quelle période, quels utilisateurs et quels systèmes sont réellement concernés. Préservez les logs d'accès et les preuves de transfert, évitez d'élargir inutilement la copie de données personnelles et impliquez les responsables juridique et protection des données. Ne qualifiez pas une exposition comme une exfiltration si les sources ne permettent pas de le démontrer.

### 14.4 Compromission cloud

Priorité : garder le contrôle de l'identité, des journaux d'audit, des clés et des ressources. Les actions incluent parfois la restriction d'un rôle, la désactivation d'une clé, le blocage d'un chemin ou la restauration d'une configuration, mais elles doivent être coordonnées avec les propriétaires des workloads. Dans le cloud, un changement de configuration peut être réappliqué par l'automatisation ; vérifiez les pipelines, l'état désiré, les journaux d'audit et les dépendances avant de conclure à l'éradication.

~~~text
Type d'incident      Priorité immédiate
-----------------    ------------------------------------
Rançongiciel         Limiter l'impact et protéger les sauvegardes
Identité compromise  Révoquer les accès et valider les sessions
Données exposées     Déterminer l'étendue, préserver et coordonner
Cloud                Contrôler les identités, clés et changements
Panne / DDoS         Maintenir le service et analyser la cause
~~~

## 15. Communication externe, conformité et partenaires

Les obligations de notification dépendent du pays, du secteur, des contrats, du type de données et de l'impact confirmé. N'appliquez pas une règle générique sans vérifier le contexte : certains délais sont définis par un texte ou un contrat, d'autres par une politique interne. Le responsable désigné doit obtenir rapidement les faits nécessaires et travailler avec les fonctions juridiques et protection des données.

Une communication externe doit éviter les spéculations, les détails techniques qui créent un risque supplémentaire et les engagements impossibles à tenir. Elle doit distinguer ce qui est connu, les mesures engagées, les conséquences confirmées et la date de la prochaine mise à jour. Conservez la version, l'approbateur, le canal et l'heure de publication. Pour un fournisseur ou partenaire, identifiez les obligations contractuelles, les accès qu'il gère et les données qu'il conserve.

Préparez aussi la communication interne : quels utilisateurs doivent changer une action, quel service est indisponible, quel canal utiliser et où vérifier les mises à jour fiables. Le silence laisse place aux rumeurs, mais une communication non vérifiée peut nuire à la confiance. Le bon rythme dépend de l'impact et des informations réellement confirmées.

## 16. Clôture et retour d'expérience

La clôture exige des critères vérifiables : activité malveillante non observée pendant la fenêtre définie, mesures de correction terminées, services validés par leurs propriétaires, surveillance active, risques résiduels acceptés par la bonne autorité et actions restantes confiées à des responsables. Une date de clôture ne doit pas masquer des inconnues importantes. Certains dossiers peuvent passer en surveillance prolongée tout en gardant des tâches ouvertes.

Le retour d'expérience cherche à améliorer les contrôles, pas à blâmer une personne. Examinez les causes techniques et organisationnelles : actifs non inventoriés, privilèges excessifs, journaux absents, alerte non traitée, sauvegarde non testée, ambiguïté d'autorité, dépendances inconnues ou communication tardive. Une explication causale doit être soutenue par des éléments ; évitez les résumés tels que « erreur humaine » sans examiner les conditions qui ont permis l'erreur.

Chaque action d'amélioration doit être mesurable : responsable, échéance, priorité, preuve de réalisation et méthode de vérification. Si une règle de détection est modifiée, testez-la sur des cas positifs et négatifs. Si un accès est réduit, vérifiez les rôles effectifs. Si la procédure change, réalisez un exercice qui prouve qu'elle est comprise et applicable.

~~~text
Clôture
  |
  +--> Incidence contenue et causes traitées ?
  +--> Services validés par les propriétaires ?
  +--> Surveillance et critères de sortie définis ?
  +--> Risques résiduels acceptés ?
  +--> Actions restantes attribuées ?
  |
  v
Revue post-incident
  |
  v
Améliorations testées puis vérifiées
~~~

## 17. Mesures de performance et indicateurs

Les métriques peuvent aider à améliorer la qualité de la réponse. Mesurez par exemple le délai de triage, le délai de qualification, le temps avant confinement, le temps de récupération, le taux de réouverture, la disponibilité des journaux, le succès des exercices et le pourcentage d'actions post-incident terminées. Interprétez-les selon la criticité et la nature de l'incident : un temps moyen faible peut masquer quelques crises très longues.

Évitez de récompenser la fermeture rapide des dossiers sans considérer la qualité, les incidents réouverts et les risques résiduels. Un délai de réponse ne doit pas encourager à déclarer un incident clos prématurément. Combinez les métriques quantitatives avec des revues qualitatives et les commentaires des équipes opérationnelles.

Les indicateurs doivent servir à améliorer le système. Si la détection est trop lente, vérifiez l'instrumentation et les responsabilités ; si le confinement tarde, examinez les délégations et les accès ; si la récupération dépasse l'objectif, examinez les sauvegardes, dépendances et tests. Chaque métrique doit avoir une définition, une source de données, une fréquence et un responsable.

~~~text
Détection --> Triage --> Confinement --> Récupération
     |          |            |               |
     v          v            v               v
  Couverture   Délai       Réduction       RTO / RPO
  journaux     qualité     de l'impact      réellement observés
     \          |            |               /
      +---------+------------+--------------+
                         |
                         v
                Programme d'amélioration
~~~

## 18. Automatisation sûre et orchestration

L'automatisation peut enrichir des alertes, ouvrir un dossier, collecter des métadonnées, faire des recherches dans des journaux, signaler les équipes de garde et suivre des tâches. Elle réduit les délais et la répétition, mais peut amplifier une erreur. Les actions destructives ou impactantes — isolation, désactivation de compte, rotation de secret, suppression, restauration — nécessitent des permissions, des seuils et des contrôles adaptés à leur risque.

Concevez les workflows pour être explicables et idempotents autant que possible : un événement déclenché deux fois ne doit pas créer deux actions incohérentes. Chaque étape enregistre les entrées, la version de la règle, le résultat, les erreurs et l'identifiant du dossier. Prévoyez un chemin de refus sûr si le contexte est incomplet ou si une dépendance n'est pas disponible.

Testez sur des événements simulés et des environnements de validation. Les secrets d'intégration doivent être minimisés et protégés ; la permission d'une automatisation doit correspondre à ses responsabilités. Les exceptions et décisions humaines doivent rester visibles. Ne laissez pas un workflow interpréter seul une preuve ambiguë et déployer un confinement global sans mécanisme d'approbation adapté.

~~~text
Alerte
  |
  v
Enrichissement automatique et contrôles
  |
  v
Score / règles / dossier créé
  |
  v
Décision : automatisation préapprouvée ou revue humaine
  |
  v
Action contrôlée et journalisée
  |
  v
Vérification du résultat et suivi
~~~

## 19. Modèle de rapport d'incident

Un rapport d'incident utile commence par un résumé exécutif : quoi, quand, où, quel impact confirmé et quelles décisions sont requises. Le corps décrit le périmètre, la détection, la chronologie, les preuves, les hypothèses, les actions de confinement, l'éradication, la récupération, les risques résiduels et les recommandations. Les annexes contiennent les références techniques, requêtes, empreintes, éléments d'horodatage et limites de collecte.

Ne mettez pas des secrets, des mots de passe, des jetons ou des captures complètes contenant des données personnelles dans la version destinée à tous les destinataires. Produisez des versions adaptées aux audiences lorsque cela est nécessaire : résumé de direction, rapport opérationnel et annexe technique restreinte. Chaque version doit rester cohérente quant aux faits et à la gravité.

Une conclusion doit indiquer ce qui est établi et ce qui ne l'est pas. Exemple : « Les journaux confirment une session inhabituelle et une tentative sortante bloquée ; les sources disponibles ne démontrent pas de transfert de données réussi. » Ce type de formulation est précis et utile, même si l'attribution ou la cause initiale reste ouverte.

~~~text
1. Résumé et décision attendue
2. Périmètre / actifs / fenêtre temporelle
3. Détection et qualification
4. Chronologie sourcée
5. Faits confirmés / hypothèses
6. Impact et étendue
7. Confinement / éradication
8. Récupération et validation métier
9. Risques résiduels et limites
10. Actions, responsables, échéances
~~~

## 20. Travaux pratiques guidés

Les quatre travaux pratiques utilisent un dossier fictif, des événements synthétiques et des données créées pour le cours. N'utilisez pas de systèmes de production ni de données réelles sensibles. Les corrections illustrent le raisonnement attendu ; elles ne remplacent pas les procédures d'une organisation.

### TP 1 — Triage et déclaration d'incident

**Objectif.** Transformer un signal brut en dossier de triage exploitable.

**Données.** Une alerte EDR signale un processus enfant inhabituel sur le poste pédagogique LAB-07 à 09:15 UTC. Un événement IAM indique cinq échecs puis une réussite d'authentification du même compte de test. Le propriétaire confirme qu'une maintenance est prévue le matin, mais ne fournit pas encore le numéro de changement.

**Étapes.** Créez l'identifiant IR-LAB-001. Notez les sources, heures, actifs et observations exactes. Distinguez les faits des hypothèses. Proposez une priorité provisoire, les deux premières vérifications, les actions qui pourraient être préapprouvées et l'autorité de décision. Ne fermez pas l'alerte en vous appuyant uniquement sur l'existence de la maintenance.

**Livrable.** Fiche d'incident, chronologie initiale et liste des questions ouvertes.

**Correction attendue.** Les deux sources constituent des observations distinctes, mais leur lien n'est pas encore établi. La maintenance est une explication possible à vérifier par le ticket, le compte, le processus et les horaires. La priorité dépend de la criticité du poste, des privilèges du compte et de l'activité qui se poursuit. Les actions immédiates peuvent inclure le contrôle des sessions et la collecte des détails EDR, selon les procédures autorisées.

**Critères de réussite.** Dossier identifié, vocabulaire factuel, priorité justifiée, propriétaire des prochaines actions et absence de conclusion prématurée.

### TP 2 — Choisir et vérifier le confinement

**Objectif.** Comparer les options de confinement sans oublier l'impact métier.

**Données.** Le poste LAB-07 héberge un outil de production important. Le réseau signale une tentative de communication vers une destination documentaire bloquée par un contrôle. Le responsable de service indique que l'isolation totale arrêterait une tâche métier. Le plan approuvé permet de mettre temporairement le poste en quarantaine réseau, avec un chemin de gestion restreint.

**Étapes.** Comparez trois options : ne rien faire, isoler entièrement, appliquer le confinement approuvé avec gestion restreinte. Pour chacune, décrivez le risque pour le métier, le risque de propagation, la préservation des preuves, la personne qui autorise et la manière de vérifier le résultat. Sélectionnez une option et définissez un critère de réévaluation.

**Livrable.** Matrice de décision, journal de décision et étapes de vérification après action.

**Correction attendue.** Ne rien faire peut laisser persister un risque crédible. L'isolation totale réduit potentiellement la propagation mais peut interrompre le service et empêcher la gestion. La quarantaine approuvée peut être proportionnée si elle réduit le risque tout en conservant un accès contrôlé ; elle doit être vérifiée sur le plan réseau et surveillée. La décision dépend de l'activité en cours et doit être prise selon l'autorité, pas par supposition de l'apprenant.

**Critères de réussite.** Risques et dépendances explicités, décision rattachée à la procédure, contrôle d'efficacité prévu et retour arrière défini.

### TP 3 — Construire un plan d'éradication et de récupération

**Objectif.** Concevoir une restauration contrôlée à partir d'un scénario de compromission fictif.

**Données.** Un serveur applicatif de test a été isolé. L'analyse indique un compte de service exposé, une configuration ancienne et une sauvegarde de la veille. La validation d'intégrité de cette sauvegarde est en cours ; la source exacte de l'exposition n'est pas encore confirmée.

**Étapes.** Définissez les contrôles nécessaires avant restauration, le plan de rotation du secret, la correction de configuration, les tests fonctionnels et de sécurité, les critères de reconnexion et le plan de retour arrière. Identifiez les preuves qui doivent être conservées avant toute réinitialisation ou reconstruction. Ne supposez pas que la sauvegarde soit saine parce qu'elle est récente.

**Livrable.** Plan par étapes avec responsable, critère de passage, risque et preuve de validation.

**Correction attendue.** Il faut valider la sauvegarde, préserver les journaux nécessaires, corriger le secret exposé et sa portée, traiter la configuration vulnérable et vérifier l'étendue de l'accès. La restauration passe par des tests techniques et métier, une reconnexion progressive, une surveillance renforcée et une acceptation explicite du propriétaire. Si l'origine reste inconnue, cette limite doit conduire à des vérifications supplémentaires avant la clôture.

**Critères de réussite.** Aucune restauration aveugle, critères objectifs de retour en service, dépendances identifiées et risques résiduels attribués.

### TP 4 — Rapport et retour d'expérience

**Objectif.** Rédiger un compte rendu qui sépare les faits établis des questions encore ouvertes.

**Données.** Dans un dossier fictif, le journal IAM confirme une connexion inhabituelle ; l'EDR montre un processus inattendu ; le pare-feu enregistre une tentative sortante bloquée ; aucun transfert de données réussi n'est démontré. Le service a été restauré après rotation des identifiants et vérification des sauvegardes. Deux lacunes restent ouvertes : fenêtre de journalisation incomplète et inventaire du compte de service.

**Étapes.** Rédigez un résumé exécutif, une chronologie, l'impact confirmé, les actions prises, les inconnues et cinq améliorations. Pour chaque amélioration, indiquez un responsable, une échéance, une preuve de réalisation et une méthode de test.

**Livrable.** Rapport court et tableau d'actions post-incident.

**Correction attendue.** Le rapport confirme la connexion inhabituelle, l'alerte endpoint et la tentative bloquée, mais ne prétend pas qu'une exfiltration a eu lieu. Il indique les actions de récupération et les limites des journaux. Les améliorations devraient inclure la couverture des logs, la gestion du compte de service, la mise à jour de l'inventaire, un exercice de confinement et un contrôle périodique des sauvegardes.

**Critères de réussite.** Conclusion fidèle aux preuves, actions attribuées, limites visibles et critères de clôture vérifiables.

## 21. Exercices corrigés

### Exercice 1 — Une alerte devient-elle automatiquement un incident ?
Un outil signale un comportement inhabituel sur un poste.

**Correction.** Non. L'alerte doit être triée, contextualisée et qualifiée selon les critères internes. Une alerte crédible peut toutefois justifier des protections préapprouvées avant la certitude complète.

### Exercice 2 — Qui doit autoriser l'isolation d'un serveur critique ?
L'analyste dispose d'un indice crédible mais le serveur soutient un service métier.

**Correction.** La décision relève de l'autorité désignée dans la procédure, en coordination avec le responsable d'incident et le propriétaire du service. Des actions d'urgence prédéfinies peuvent avoir une autorisation anticipée ; il faut respecter les délégations existantes.

### Exercice 3 — Quelles informations inclure dans une première mise à jour ?
L'impact exact reste inconnu.

**Correction.** Décrivez les faits confirmés, les systèmes potentiellement touchés, l'impact connu et inconnu, les mesures en cours, les décisions nécessaires et l'heure de mise à jour suivante. Ne remplissez pas les lacunes par des suppositions.

### Exercice 4 — Le compte de service a été désactivé. L'incident est-il contenu ?
**Correction.** Pas nécessairement. Il faut vérifier les sessions, les secrets, les autres identités, les chemins d'accès alternatifs et les ressources dépendantes. Le contrôle doit porter sur l'objectif de confinement, pas uniquement sur la réussite de la commande.

### Exercice 5 — La sauvegarde est récente.
Peut-on la restaurer immédiatement ?

**Correction.** Non, pas sans vérifier son intégrité, sa couverture et la possibilité qu'elle soit antérieure à la compromission. Il faut corriger la cause et valider la restauration avant reconnexion.

### Exercice 6 — Une connexion a été bloquée.
Peut-on conclure à une exfiltration ?

**Correction.** Non. La source montre une tentative bloquée dans sa portée. Il faut d'autres preuves pour établir une connexion réussie, un transfert et la nature des données.

### Exercice 7 — L'analyste doit préserver toutes les données avant le confinement.
Est-ce toujours vrai ?

**Correction.** Non. La protection des personnes, des services et des données peut exiger une action urgente. Préservez les éléments utiles lorsque le temps et le risque le permettent, puis documentez toute perte potentielle de données volatiles.

### Exercice 8 — Plusieurs alertes dans plusieurs tableaux de bord.
Cela représente-t-il forcément plusieurs preuves indépendantes ?

**Correction.** Non. Plusieurs tableaux peuvent afficher le même événement source. Il faut vérifier la provenance et l'indépendance des sources avant de renforcer le niveau de confiance.

### Exercice 9 — Comment suivre la rotation des secrets ?
**Correction.** Identifiez les secrets affectés sans copier leur valeur dans le dossier, planifiez l'ordre, attribuez un propriétaire, exécutez selon la procédure et vérifiez les usages résiduels ainsi que les dépendances.

### Exercice 10 — Le service redémarre après restauration.
Cela suffit-il pour le retour en production ?

**Correction.** Non. Les validations de sécurité, d'intégrité des données, des dépendances, des journaux et des tests métier doivent aussi réussir. La reconnexion doit être progressive lorsque le risque le justifie.

### Exercice 11 — Une cause initiale est inconnue.
Peut-on clore le dossier ?

**Correction.** Cela dépend des critères de clôture et du risque résiduel accepté. La cause inconnue doit être explicitement documentée, les risques analysés et les tâches restantes attribuées. Ne clôturez pas simplement pour améliorer une métrique.

### Exercice 12 — Un service dépend du compte compromis.
Quel est le risque d'une désactivation brutale ?

**Correction.** Une indisponibilité métier peut en résulter. Évaluez les dépendances et les voies d'accès, puis coordonnez une révocation ou rotation qui réduit le risque tout en conservant un plan de continuité approuvé.

### Exercice 13 — Qui peut communiquer aux clients ?
**Correction.** Les personnes désignées par le plan de crise et les règles applicables. Les équipes techniques fournissent des faits vérifiés, mais ne doivent pas improviser des communications externes ni promettre des résultats non validés.

### Exercice 14 — Les journaux sont incomplets.
Quelle conclusion est adéquate ?

**Correction.** Les conclusions sont limitées par la fenêtre et les sources disponibles. Il faut identifier les lacunes, rechercher d'autres sources autorisées et ne pas interpréter le silence comme preuve d'inactivité.

### Exercice 15 — Après éradication, une nouvelle alerte apparaît.
**Correction.** Réouvrez l'investigation, vérifiez si le périmètre ou les moyens de persistance ont été sous-estimés, appliquez les mesures de confinement nécessaires et révisez le plan. Ne supposez pas qu'il s'agit d'un faux positif sans analyse.

### Exercice 16 — Une automatisation bloque un compte à privilèges.
Que doit-on vérifier ?

**Correction.** La portée du compte, les dépendances et l'autorisation de l'action, puis les journaux de workflow, l'état réellement appliqué, les sessions résiduelles et les effets métier. Une automatisation ne supprime pas le besoin de vérification.

### Exercice 17 — Comment qualifier une exposition de données ?
**Correction.** Déterminez quelles données, quels systèmes, quelle fenêtre et quels utilisateurs sont concernés avec des preuves identifiées. Les obligations de notification doivent être évaluées avec les responsables juridique et protection des données selon le contexte.

### Exercice 18 — Qu'est-ce qu'un bon critère de récupération ?
**Correction.** Un critère mesurable : intégrité vérifiée, correctif appliqué, secrets tournés, tests techniques et métier réussis, journaux opérationnels et propriétaire ayant approuvé la reconnexion. « Le système semble normal » est trop vague.

### Exercice 19 — Le retour d'expérience attribue l'incident à une erreur humaine.
Est-ce suffisant ?

**Correction.** Non. Il faut analyser les facteurs systémiques : permissions, procédures, interfaces, charge, formation, contrôles et outils. Chaque recommandation doit être vérifiable et posséder un responsable.

### Exercice 20 — Quelle est la meilleure conclusion quand la preuve ne démontre pas l'exfiltration ?
**Correction.** Écrire que les sources disponibles ne démontrent pas de transfert réussi, décrire ce qui a été observé et lister les sources manquantes. Ne pas affirmer une exfiltration ni conclure à l'absence absolue de transfert.

## 22. Défi final — Répondre à un incident multi-système

**Scénario fictif.** Un compte de test affiche une connexion inhabituelle. Un poste LAB-12 déclenche une alerte endpoint. Le pare-feu rapporte une tentative de communication bloquée. Le serveur métier a une sauvegarde récente, mais la restauration n'a pas été testée depuis plusieurs mois. Un responsable signale que ce serveur est nécessaire à la facturation. Les journaux couvrent les dernières 24 heures, mais l'horloge du poste a un décalage non encore quantifié.

**Travail demandé.** Créez un dossier d'incident, définissez une priorité provisoire, attribuez les rôles et rédigez une mise à jour initiale. Définissez une stratégie de collecte et de confinement, ainsi que les contrôles requis avant toute rotation ou isolation. Proposez un plan d'éradication et de récupération, un critère de clôture et six actions de retour d'expérience. Séparez les faits des hypothèses et expliquez les incertitudes temporelles.

**Correction détaillée.**

1. **Déclaration.** Ouvrir un identifiant, nommer un responsable et enregistrer la première détection, le compte, le poste et le service concerné. Maintenir le niveau de gravité provisoire tant que l'impact, les privilèges et l'activité en cours sont examinés.
2. **Rôles.** Le responsable coordonne ; DFIR établit la chronologie et préserve les données ; les équipes identité, endpoint, réseau et service métier fournissent les sources et exécutent les actions autorisées ; les fonctions juridique et protection des données sont sollicitées si des données potentiellement exposées le nécessitent.
3. **Faits et hypothèses.** Les connexions, l'alerte endpoint et la tentative bloquée sont des observations des sources décrites. Le lien entre compte, processus et trafic doit être vérifié. Aucun transfert réussi n'est démontré par le scénario.
4. **Collecte.** Préserver les journaux et détails de l'alerte, noter l'état du poste, vérifier les horloges et normaliser les heures sans écraser les valeurs sources. Demander les journaux IAM, EDR, pare-feu, proxy et les données pertinentes du serveur dans une fenêtre justifiée.
5. **Confinement.** Évaluer l'activité actuelle, les privilèges du compte et l'impact de l'isolation du serveur de facturation. Utiliser une mesure approuvée qui limite le risque tout en conservant un accès de gestion restreint si cela est permis. Vérifier l'état obtenu et surveiller les chemins alternatifs.
6. **Éradication.** Identifier le périmètre de compromission, traiter les accès concernés, corriger la cause identifiée et rechercher d'autres mécanismes d'accès. Ne pas supprimer aveuglément les éléments nécessaires à la preuve.
7. **Récupération.** Tester la restauration en environnement approprié, valider intégrité et tests métier, appliquer les corrections, activer les logs nécessaires et reconnecter progressivement après approbation du propriétaire.
8. **Clôture.** Exiger des preuves d'éradication, des tests de récupération réussis, un plan de surveillance, l'acceptation explicite des risques résiduels et des actions restantes attribuées.
9. **Amélioration.** Tester les sauvegardes, corriger la synchronisation des horloges, améliorer la couverture des journaux, formaliser les rôles d'urgence, revoir les accès des comptes de service et exercer le scénario d'isolation d'un service critique.

**Barème sur 100 points.** Déclaration et gouvernance : 10. Analyse de priorité : 15. Préservation et chronologie : 15. Confinement et arbitrage métier : 20. Éradication et récupération : 15. Communication : 10. Retour d'expérience mesurable : 15.

## 23. Liste de contrôle opérationnelle

Avant une crise, vérifiez que les actifs, les propriétaires, les journaux, les sauvegardes, les contacts et les délégations sont à jour. En triage, identifiez la source, l'horodatage, le système, l'identité, l'impact apparent et l'activité en cours. Déclarez l'incident selon les critères internes, attribuez un responsable et ouvrez un dossier.

Pendant la réponse, maintenez une chronologie, un journal de décision, une liste d'hypothèses et un tableau des actions. Préservez les preuves nécessaires lorsque cela est compatible avec la réduction du dommage. Évaluez l'effet métier de chaque confinement, vérifiez le résultat après action et suivez les exceptions temporaires. Coordonnez les communications et le relais entre équipes.

Pour la récupération, validez la source de restauration, traitez les causes et accès compromis, testez les fonctions techniques et métier et reconnectez par étapes. La clôture requiert des critères explicites, une surveillance définie, l'acceptation des risques résiduels et des améliorations attribuées.

~~~text
[ ] Rôles et autorité de décision confirmés
[ ] Périmètre et sévérité consignés
[ ] Dossier, chronologie et décisions ouverts
[ ] Sources et preuves préservées selon le risque
[ ] Confinement autorisé et efficacité vérifiée
[ ] Accès, secrets et causes traités
[ ] Sauvegarde et intégrité validées
[ ] Tests techniques et métier réussis
[ ] Reconnexion progressive approuvée
[ ] Surveillance et risques résiduels documentés
[ ] Actions post-incident attribuées et datées
~~~

## 24. Glossaire

**Alerte.** Signal d'un outil ou d'une personne indiquant une activité qui mérite une validation.

**Événement.** Action ou changement observé par une source donnée.

**Incident de sécurité.** Événement ou ensemble d'événements qui satisfait les critères de qualification définis et peut compromettre la confidentialité, l'intégrité ou la disponibilité.

**DFIR.** Association des pratiques d'investigation numérique et de réponse à incident.

**Triage.** Première évaluation visant à qualifier, prioriser et choisir les premières actions.

**Confinement.** Mesures destinées à empêcher l'incident de se poursuivre ou de s'étendre.

**Éradication.** Suppression contrôlée des composants et conditions de compromission identifiés.

**Récupération.** Remise en service vérifiée après correction et restauration.

**Chaîne de conservation.** Trace des transferts, accès, manipulations et lieux de stockage des preuves.

**RTO.** Objectif de délai de rétablissement d'un service après interruption.

**RPO.** Objectif de perte de données acceptable mesuré par rapport au temps.

**RACI.** Matrice clarifiant qui réalise, qui est redevable, qui est consulté et qui est informé.

**IOC.** Indicateur de compromission utilisé pour rechercher ou contextualiser une activité suspecte.

**Faux positif.** Alerte ou détection qui ne correspond pas au phénomène recherché.

**Risque résiduel.** Risque qui subsiste après les mesures de traitement.

**Retour d'expérience.** Analyse structurée d'un incident afin d'améliorer les contrôles et la préparation.

## 25. Références officielles

- NIST SP 800-61 Rev. 3, *Incident Response Recommendations and Considerations for Cybersecurity Risk Management* : https://csrc.nist.gov/pubs/sp/800/61/r3/final
- Projet NIST sur la réponse aux incidents : https://csrc.nist.gov/projects/incident-response
- CISA, Federal Government Cybersecurity Incident and Vulnerability Response Playbooks : https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks
- FIRST, CSIRT Services Framework : https://www.first.org/standards/frameworks/csirts/csirt_services_framework_v2.1
- NIST SP 800-86, *Guide to Integrating Forensic Techniques into Incident Response* : https://csrc.nist.gov/pubs/sp/800/86/final
- CISA, ressources et bonnes pratiques de cybersécurité : https://www.cisa.gov/topics/cybersecurity-best-practices

NIST SP 800-61 Rev. 3 est la révision publiée en avril 2025 et remplace la révision 2. Elle intègre la réponse dans la gestion globale du risque selon le Cybersecurity Framework 2.0. Les playbooks CISA présentent des procédures opérationnelles détaillées, initialement destinées aux systèmes fédéraux concernés, dont les pratiques générales peuvent servir de référence à d'autres organisations. Adaptez toujours ces ressources au droit, aux contrats, au secteur et aux procédures locales.

## 26. Synthèse finale

Une réponse à incident efficace est coordonnée, documentée et proportionnée. Elle débute par un triage et une qualification, établit une autorité de décision, préserve les preuves selon les risques, contient l'activité, investigue l'étendue, traite les accès et causes, puis restaure les services de façon vérifiable. La vitesse compte, mais la vitesse sans coordination peut aggraver les dommages ; la collecte exhaustive sans action peut aussi laisser un incident progresser.

Chaque action doit avoir un objectif, un responsable, une autorisation, un résultat attendu et un contrôle d'efficacité. Les faits, les hypothèses, les décisions et les risques résiduels doivent rester distincts. Les comptes, sessions, sauvegardes, journaux et dépendances doivent être traités dans leur contexte, et non par une commande universelle.

Le travail n'est pas achevé au simple redémarrage d'un service. La clôture repose sur l'éradication suffisamment validée, la récupération acceptée par les propriétaires, la surveillance et les risques résiduels documentés. Enfin, le retour d'expérience transforme les observations en améliorations mesurables, avec des responsables et des preuves de réalisation.

Fin du cours.