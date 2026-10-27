# Gestion des vulnérabilités

> **Mise en contexte**

Une organisation peut disposer d’un pare-feu, d’un antivirus, d’un SIEM et de règles de sécurité bien rédigées tout en restant vulnérable à une faiblesse connue qui n’a jamais été corrigée. Un serveur oublié, une bibliothèque logicielle incorporée dans une application, un équipement réseau en fin de support ou une interface d’administration exposée peut devenir la porte d’entrée d’un incident. La gestion des vulnérabilités transforme cette réalité en un processus suivi : découvrir les actifs, identifier les faiblesses, évaluer le risque dans le contexte réel, décider des actions, corriger ou réduire l’exposition, vérifier le résultat et conserver des preuves.

Il ne s’agit pas de courir après le plus grand nombre de scores élevés. Il s’agit de réduire, de manière démontrable, les chemins d’attaque les plus dangereux pour le service métier. Un score technique ne dit pas à lui seul si un actif est exposé, s’il contient des données sensibles, s’il est exploité activement ou si sa mise à jour est sûre. Un programme efficace combine les informations techniques, la réalité de l’inventaire, le renseignement sur les menaces, les contraintes opérationnelles et la responsabilité métier.

Ce cours prolonge la sécurité des protocoles de routage par une approche transversale qui s’applique aux serveurs, applications, postes de travail, équipements réseau, conteneurs, environnements cloud et dépendances logicielles. Les exemples de systèmes et de résultats sont fictifs. Les travaux pratiques se déroulent sur des ressources que vous possédez ou êtes autorisé à tester.

## Objectifs pédagogiques

À la fin du cours, vous saurez mettre en place un cycle complet de gestion des vulnérabilités, définir une source de vérité pour les actifs, organiser la collecte des résultats, comprendre les identifiants CVE et les faiblesses CWE, interpréter le CVSS v4, utiliser prudemment EPSS et le catalogue CISA KEV, prioriser un backlog selon le risque contextualisé, planifier les correctifs, choisir une mesure compensatoire, gérer les exceptions et vérifier la remédiation. Vous saurez aussi distinguer une vulnérabilité, une exposition, un incident et un faux positif, puis construire un tableau de bord utile sans le transformer en concours de volumes.

Le programme est cumulatif : la découverte des actifs précède la mesure ; la qualité des données conditionne la priorité ; le choix de remédiation dépend du contexte ; et la clôture exige une preuve de correction. Si un actif ne figure dans aucun inventaire ou n’est interrogé par aucun outil, le meilleur score de risque ne pourra pas être calculé. Si le correctif est installé mais jamais vérifié, le dossier ne peut pas être considéré comme terminé.

## 1. Comprendre les notions fondamentales

### 1.1 Qu’est-ce qu’une vulnérabilité ?

Une vulnérabilité est une faiblesse d’un produit, d’un composant, d’une configuration ou d’un processus qui peut être exploitée dans certaines conditions et produire un effet de sécurité. Les causes peuvent inclure une erreur de conception, une erreur d’implémentation, un contrôle insuffisant, une configuration trop permissive, un composant non maintenu, un secret exposé ou un défaut de mise à jour. Toutes les faiblesses ne sont pas des vulnérabilités exploitables de la même façon : il faut préciser les préconditions, l’attaque réalisable et les effets possibles.

Une vulnérabilité connue est documentée ou reconnue par une source compétente. Une vulnérabilité zero-day désigne souvent une faiblesse exploitée avant qu’un correctif soit disponible au défenseur, mais l’usage exact du terme varie selon le contexte. Une vulnérabilité non corrigée n’est pas nécessairement zero-day : un correctif peut exister depuis des mois. À l’inverse, l’absence d’un numéro CVE ne prouve pas qu’une faiblesse est inexistante.

### 1.2 Vulnérabilité, menace, exposition et risque

Ces notions doivent rester distinctes. La vulnérabilité est la faiblesse. La menace décrit une cause potentielle de dommage ou un acteur capable d’en provoquer un. L’exposition décrit dans quelles conditions un actif ou un service peut être atteint ou utilisé. Le risque combine la possibilité d’un événement dommageable et la gravité de ses conséquences dans un contexte donné. Un service vulnérable directement accessible depuis Internet n’a pas forcément le même risque qu’un équipement similaire isolé, mais la segmentation ne supprime pas nécessairement le risque : un attaquant interne ou un poste compromis peut encore fournir un chemin.

~~~text
Vulnérabilité : défaut technique ou configuration faible
          |
          v
Conditions d'exploitation
          |
          +------ exposition réseau et accès disponibles
          |
          +------ exploit connu ou activité observée
          |
          v
Effet possible sur l'actif et les systèmes liés
          |
          v
Impact métier + probabilité + contrôles existants
          |
          v
Risque contextualisé et décision de traitement
~~~

Un risque n’est pas calculé de manière fiable en multipliant mécaniquement deux nombres choisis sans méthode. Certaines organisations utilisent une échelle qualitative ; d’autres combinent des données quantitatives et des hypothèses. Dans tous les cas, documentez les critères, l’incertitude, le propriétaire de la décision et la date de réévaluation.

### 1.3 La gestion des vulnérabilités est un cycle

La gestion des vulnérabilités comprend davantage que le scan et l’installation de correctifs. Elle commence par la préparation : périmètre, inventaire, responsabilité, règles d’autorisation et critères de priorité. Elle se poursuit par la découverte, la validation, l’évaluation, la planification, la remédiation et la vérification. Les résultats sont ensuite utilisés pour améliorer les contrôles et prévenir les répétitions.

~~~text
Préparer le périmètre et les responsabilités
                    |
                    v
Découvrir actifs et composants
                    |
                    v
Détecter et valider les faiblesses
                    |
                    v
Enrichir avec exposition, menace et impact
                    |
                    v
Prioriser et attribuer un propriétaire
                    |
                    v
Corriger / atténuer / accepter temporairement
                    |
                    v
Vérifier par une nouvelle mesure
                    |
                    v
Clôturer avec preuve et mesurer l'efficacité
                    |
                    +-----------> nouvelle itération
~~~

Le processus est continu parce que les actifs, logiciels, versions, menaces et configurations changent. Une photographie annuelle ne permet pas de maîtriser une flotte dont le cloud s’agrandit chaque semaine ou dans laquelle de nouvelles dépendances sont publiées à chaque version.

## 2. Gouvernance et responsabilités

### 2.1 Définir le périmètre

Le périmètre doit inclure les éléments que l’organisation possède, exploite, administre ou a contractuellement la responsabilité de sécuriser. Il peut contenir des adresses IP publiques et privées, équipements de réseau, VM, hôtes physiques, postes, applications, API, conteneurs, images, fonctions serverless, systèmes embarqués, bases de données, bibliothèques, dépendances de construction et services externalisés. Les actifs non traditionnels doivent être pris en compte : environnements de test connectés à la production, comptes cloud temporaires, appliances sous contrat et équipements en fin de vie.

Il faut également préciser ce qui ne peut pas être scanné directement et pourquoi. Certains environnements industriels, dispositifs médicaux, contrôleurs ou systèmes temps réel exigent des fenêtres, des méthodes passives ou un laboratoire de validation. Un actif exclu du scan ne doit pas disparaître du programme : il doit avoir une méthode d’évaluation alternative et une justification revue périodiquement.

### 2.2 RACI et propriétaires

Chaque étape doit avoir un responsable. L’équipe sécurité définit la méthode et aide à prioriser ; l’équipe d’exploitation applique les correctifs ; le propriétaire métier évalue l’impact et valide les fenêtres ; l’équipe de développement corrige le code et les dépendances ; l’architecture vérifie les mesures structurelles ; l’audit vérifie les preuves et la conformité. Dans une petite organisation, une personne peut porter plusieurs rôles, mais les décisions importantes doivent rester traçables et les conflits d’intérêt identifiés.

~~~text
Activité                    Sécurité   Exploitation   Métier   Dev
Inventaire / politique      pilote     contribue      valide   contribue
Validation d'un résultat    pilote     contribue      informé  contribue
Priorité de traitement      conseille  contribue      décide*  contribue
Déploiement du correctif    contrôle   exécute        approuve exécute code
Acceptation du risque       conseille  contribue      autorise contribue
Vérification / clôture      contrôle   fournit preuve informé  fournit preuve

* Selon le modèle de gouvernance et la délégation d'autorité.
~~~

Le propriétaire d’un actif est une personne ou une fonction qui peut décider de son usage, de sa disponibilité, de son importance et de son plan de traitement. Une boîte mail collective n’est pas un propriétaire efficace si personne ne reçoit et n’assume les décisions. Un outil doit permettre d’identifier le propriétaire, son suppléant, le service métier et la voie d’escalade.

### 2.3 Politique et objectifs de service

La politique doit définir les types d’actifs couverts, les sources d’information, la fréquence de détection, la méthode de priorisation, les délais cibles, les rôles, la gestion des exceptions, la preuve exigée et les procédures d’urgence. Les délais sont adaptés à l’organisation, au cadre réglementaire applicable, à la disponibilité des correctifs et à la criticité des services. Il ne faut pas recopier aveuglément un délai réglementaire ou une cible d’une autre juridiction sans vérifier son applicabilité.

Une politique doit préciser ce qu’il se passe si un délai est dépassé. Le résultat ne doit pas être simplement une alerte oubliée. Il faut une escalade vers le propriétaire, un plan de réduction d’exposition, une date de décision et une autorité capable d’accepter le risque résiduel si une correction immédiate est impossible.

### 2.4 Exceptions et acceptation du risque

Une exception n’est pas une disparition du risque. Elle autorise temporairement une dérogation à une règle de traitement en échange d’une décision explicite et d’un ensemble de contrôles. Le dossier doit comporter la vulnérabilité, l’actif, le service métier, la justification, les raisons empêchant la correction, les mesures compensatoires, les risques résiduels, le propriétaire, l’autorité d’approbation, l’échéance et le plan de sortie.

~~~text
Demande d'exception
       |
       v
Risque documenté + preuves
       |
       v
Analyse des alternatives et compensations
       |
       v
Approbation par l'autorité compétente
       |
       v
Échéance + propriétaire + contrôles de suivi
       |
       +--> correction vérifiée : clôture
       |
       +--> date atteinte / contexte changé : réévaluation
~~~

Une acceptation permanente et non révisée est dangereuse lorsque les menaces ou l’exposition évoluent. Une exception doit expirer ou obliger à une nouvelle décision. Il faut vérifier qu’une mesure compensatoire est réellement appliquée ; « placé derrière le pare-feu » n’est pas une preuve si la règle autorise plusieurs réseaux ou si l’administration est exposée par un autre chemin.

## 3. Construire un inventaire fiable

### 3.1 L’inventaire est la base de la couverture

Un scanner ne peut trouver une vulnérabilité que sur un actif qu’il peut découvrir et examiner. Un inventaire fiable combine plusieurs sources : CMDB, MDM, EDR, gestion cloud, DNS, DHCP, gestion de réseau, inventaire logiciel, outils de déploiement, registre de conteneurs, pipelines CI/CD, achats et contrats. Aucune source unique ne contient nécessairement tous les éléments ni n’est toujours à jour.

Le rapprochement doit utiliser des identifiants stables autant que possible : ID cloud, UUID d’agent, numéro de série, adresse MAC, nom d’instance et identifiants du système de gestion. Une adresse IP est une donnée utile mais pas un identifiant unique durable : elle peut changer ou être réutilisée. Le nom d’hôte n’est pas toujours stable, et une image de machine peut contenir un identifiant cloné si la préparation a été incorrecte.

~~~text
CMDB -----\
Cloud -----\
EDR --------> Rapprochement et déduplication ---> Inventaire de référence
MDM -------/                                      |
DNS/DHCP --/                                       +--> propriétaire
Achats ----/                                       +--> criticité métier
                                                  +--> exposition
                                                  +--> versions
~~~

Pour chaque actif, collectez seulement les informations utiles et légitimes : identifiant, type, propriétaire, environnement, service métier, criticité, emplacement logique, exposition, OS ou firmware, applications, version, support fournisseur, méthode de scan, dernière observation et statut opérationnel. Les secrets, données personnelles non nécessaires et configurations sensibles doivent être protégés.

### 3.2 Découverte des actifs inconnus

Comparez régulièrement les actifs trouvés par les capteurs avec l’inventaire officiel. Toute différence doit donner lieu à une investigation : appareil autorisé mais non enregistré, adresse réaffectée, environnement de test oublié, service externalisé ou actif non autorisé. Il est dangereux de supprimer automatiquement un actif inconnu de la liste simplement parce que le propriétaire est difficile à trouver.

La couverture peut être calculée selon une définition précise, par exemple le nombre d’actifs éligibles récemment évalués divisé par le nombre d’actifs éligibles connus. Cette mesure n’inclut pas automatiquement les actifs inconnus ; il faut donc aussi mesurer le nombre d’actifs découverts hors inventaire et le délai de traitement des écarts. Sinon, le tableau de bord peut annoncer une couverture parfaite sur une liste incomplète.

~~~text
Inventaire de référence : 1 000 actifs éligibles
Actifs évalués dans la fenêtre : 920
Couverture de la mesure : 920 / 1 000 = 92 %
Actifs inconnus détectés en parallèle : 35

Le 92 % ne prouve pas que les 35 actifs inconnus sont maîtrisés.
Il faut enquêter sur la complétude des deux sources.
~~~

### 3.3 Logiciels, bibliothèques et dépendances

L’actif n’est pas seulement la machine. Une application contient des dépendances directes et transitives ; une bibliothèque peut être embarquée dans un binaire, une image de conteneur ou un paquet livré. Les équipes doivent savoir quelles versions et quelles dépendances sont présentes dans chaque artefact réellement déployé. Le fichier de dépendances du code source ne prouve pas toujours ce qui tourne en production si l’image a été construite différemment ou si un composant est chargé dynamiquement.

Un inventaire logiciel utile associe le produit, la version, l’origine, la licence si pertinente, le propriétaire du composant, le mode de déploiement et les actifs qui l’embarquent. Un SBOM (Software Bill of Materials) peut aider à décrire les composants d’un produit. Il doit être relié à un artefact précis, généré et mis à jour pendant la construction, stocké avec sa provenance et comparé à la version effectivement déployée. Un SBOM ne remplace ni un scan de vulnérabilités ni une vérification de configuration.

## 4. Comprendre les identifiants et les sources

### 4.1 CVE, CWE et avis éditeur

Un CVE est un identifiant commun attribué à une vulnérabilité divulguée publiquement afin que les personnes et outils puissent référencer le même problème. Le CVE n’est pas un score de risque, une preuve de compromission ni un correctif. Sa description peut être incomplète ou évoluer ; il faut consulter les avis des éditeurs et les versions affectées, ainsi que les données techniques récentes.

CWE (Common Weakness Enumeration) décrit des catégories de faiblesses, telles que le contrôle d’accès insuffisant, la validation inadéquate des entrées ou la gestion incorrecte de la mémoire. Une CWE est une classe de problème, pas nécessairement l’identifiant d’une instance de vulnérabilité. Un même type de faiblesse peut apparaître dans de nombreux produits et plusieurs CVE.

Les avis éditeur indiquent souvent les versions touchées, les versions corrigées, les conditions d’exploitation, les contournements et les dépendances. Les informations doivent être comparées avec la version exacte et l’architecture. Une dénomination de produit proche n’est pas une preuve que le produit est affecté : les éditions, versions, options compilées et plateformes peuvent différer.

### 4.2 NVD et autres bases de données

La National Vulnerability Database (NVD) enrichit les données CVE par des informations normalisées, qui peuvent comprendre des métriques techniques. D’autres bases, avis éditeurs, CERT nationaux et fournisseurs de renseignement peuvent ajouter des détails utiles. Les délais de publication et de mise à jour varient : ne considérez pas qu’un champ vide prouve l’absence d’impact ou qu’un score provisoire est définitif.

Chaque dossier important devrait conserver les références consultées, la version de l’avis, l’heure de consultation et la conclusion. Les données externes peuvent diverger temporairement. Les sources originales de l’éditeur et le contexte du déploiement doivent être examinés lorsqu’une décision va entraîner une interruption ou un changement important.

~~~text
CVE / avis initial
       |
       v
Avis de l'éditeur et versions affectées
       |
       +--> NVD / métriques normalisées
       +--> KEV / preuve d'exploitation connue
       +--> EPSS / estimation probabiliste
       +--> bulletin CERT / renseignement
       |
       v
Comparaison à l'inventaire réel
       |
       v
Décision locale documentée
~~~

### 4.3 Sources à hiérarchiser

Les sources ne répondent pas toutes à la même question. L’avis éditeur sert à confirmer l’implémentation et la version affectées. CVSS décrit des caractéristiques de gravité technique. EPSS estime la probabilité que l’exploitation soit observée dans la nature dans une période donnée. Le catalogue KEV recense des CVE pour lesquelles l’exploitation est connue et constitue un signal d’urgence important. La télémétrie locale indique si l’actif est présent et exposé, et si des signes d’exploitation sont observés.

Ces sources se complètent. Un indicateur de menace élevé ne corrige pas un inventaire imprécis. Un score CVSS bas ne doit pas neutraliser une preuve d’exploitation active contre un actif critique. Un résultat KEV ne prouve pas que votre instance est compromise : il impose de déterminer l’exposition, de corriger ou atténuer et d’évaluer la possibilité d’une exploitation.

## 5. Détecter les vulnérabilités

### 5.1 Scans réseau authentifiés et non authentifiés

Un scan non authentifié observe principalement ce qu’un point de vue externe peut déduire : services exposés, versions visibles, certificats, protocoles et signatures accessibles. Il aide à comprendre la surface d’attaque réelle. Ses conclusions peuvent rester limitées si les bannières sont masquées, les services sont derrière un proxy ou l’équipement est conçu pour peu divulguer.

Un scan authentifié utilise des identifiants autorisés pour interroger le système plus profondément : paquets installés, versions, correctifs, configurations et paramètres. Il peut réduire les angles morts, mais les identifiants doivent être limités, protégés, renouvelés et audités. Un scanner qui exige un compte administrateur global sans justification crée lui-même un risque.

Le scan authentifié n’est pas toujours possible sur des équipements fragiles, systèmes industriels, appliances ou services SaaS. Il faut prévoir des méthodes adaptées : interrogation API, inventaire par agent, analyse de version, preuves du fournisseur ou évaluation manuelle. Les limitations doivent apparaître dans le tableau de bord ; « scan réussi » ne doit pas être interprété comme « couverture complète ».

~~~text
Scan externe non authentifié
  -> surface visible de l'extérieur
  -> services exposés et configurations accessibles

Scan authentifié
  -> paquets / paramètres / niveau de correctif
  -> meilleure précision sur l'état local

Les deux sont complémentaires :
une faiblesse interne peut être invisible depuis l'extérieur,
et une exposition externe peut échapper au scan local.
~~~

### 5.2 SAST, DAST, SCA et IaC

Les outils ont des périmètres différents :

- SAST (Static Application Security Testing) inspecte le code source ou une représentation compilée sans exécuter l’application, selon l’outil.
- DAST (Dynamic Application Security Testing) teste une application en fonctionnement par ses interfaces observables.
- SCA (Software Composition Analysis) identifie des dépendances et compare leurs versions à des informations de vulnérabilité et parfois de licence.
- Le scan IaC analyse des modèles de configuration d’infrastructure, par exemple les règles d’accès ou les paramètres de stockage.
- L’analyse d’images et de conteneurs examine les paquets et couches connus de l’artefact.
- Le scan de configuration compare les paramètres à une référence attendue.
- Les tests de pénétration évaluent des scénarios plus ciblés et ne remplacent pas la surveillance continue.

Aucun outil ne couvre tous les défauts. Une analyse statique peut créer des faux positifs et manquer des problèmes liés à l’exécution. Une analyse dynamique ne prouve pas qu’une branche de code non testée est sûre. SCA peut identifier une bibliothèque vulnérable qui n’est pas réellement utilisée dans le chemin affecté ; il faut cependant vérifier l’analyse avant de conclure qu’il n’y a aucun risque.

### 5.3 Fréquence et déclencheurs

La fréquence de scan dépend du type d’actif, de son exposition, de sa criticité et du rythme de changement. Les équipements exposés et les actifs critiques peuvent nécessiter une surveillance plus rapprochée que des systèmes isolés. Les nouvelles mises en production, les changements de réseau, l’ajout de dépendances, les alertes critiques et les vulnérabilités activement exploitées doivent déclencher des évaluations ciblées.

Ne vous contentez pas d’un calendrier. Un scan hebdomadaire ne découvre pas un nouveau service immédiatement après sa création si la prochaine exécution est plusieurs jours plus tard. Les mécanismes d’inventaire et de scan événementiel complètent le programme périodique. Les fenêtres doivent aussi prendre en compte les équipements dont le scan peut perturber la disponibilité.

### 5.4 Faux positifs, doublons et données manquantes

Un faux positif se produit lorsqu’un outil signale une vulnérabilité qui ne s’applique pas à l’actif, par exemple parce que la version détectée est incorrecte, un correctif rétroporté est présent ou la condition requise n’existe pas. Il doit être confirmé à l’aide de preuves, pas simplement supprimé parce qu’il gêne la métrique.

Un doublon correspond à plusieurs résultats liés au même problème sur le même actif ou à la même cause. La déduplication doit préserver les détails nécessaires : emplacements, composants, preuves, dates, identifiants de scanner et références. Une vulnérabilité de dépendance qui touche plusieurs applications peut nécessiter une action centrale sur la bibliothèque, mais il faut conserver le lien vers chaque artefact affecté.

Un résultat « inconnu » n’est pas équivalent à « non vulnérable ». L’absence d’information peut révéler un scan échoué, un identifiant insuffisant, une version inconnue ou une source périmée. Il faut distinguer l’état de l’actif, l’état du scan et l’état de la vulnérabilité afin d’éviter de transformer une panne de collecte en statut sain.

## 6. Évaluer et prioriser le risque

### 6.1 Comprendre CVSS v4

CVSS est un cadre ouvert pour décrire les caractéristiques d’une vulnérabilité et communiquer sa gravité. CVSS v4 distingue plusieurs groupes de métriques : Base, Threat, Environmental et Supplemental. Les métriques Base décrivent des caractéristiques intrinsèques ; Threat permet de prendre en compte des éléments changeants comme la maturité de l’exploitation ; Environmental affine l’évaluation à l’environnement concerné ; Supplemental ajoute des informations qui ne modifient pas directement le score final.

Le score Base est utile pour comparer la sévérité technique, mais il n’est pas votre risque métier complet. Pour une décision locale, il faut ajouter l’exposition, la criticité, les données, la présence d’exploit, la preuve d’exploitation connue, les contrôles compensatoires et la possibilité d’une interruption de service. La chaîne de métriques doit être conservée avec le score pour comprendre la conclusion. Ne communiquez pas un nombre sans indiquer la version CVSS et, lorsque disponible, le vecteur.

~~~text
CVSS Base
  -> caractéristiques techniques intrinsèques
Threat
  -> maturité / contexte d'exploitation
Environmental
  -> sensibilité et configuration locale
Supplemental
  -> informations complémentaires

Décision de remédiation = CVSS + menace + contexte actif
                               + impact métier + contraintes
~~~

### 6.2 EPSS : probabilité et limites

EPSS (Exploit Prediction Scoring System) fournit un score probabiliste, compris entre 0 et 1, qui estime la probabilité qu’une exploitation associée à un CVE soit observée dans la nature au cours des 30 prochains jours. Les scores sont actualisés quotidiennement. Une probabilité de 0,20 ne signifie pas que l’actif local a 20 % de chances d’être compromis : le score concerne la probabilité d’observation d’activité exploitante pour la vulnérabilité à l’échelle des données du modèle, et il ne connaît pas votre déploiement particulier.

EPSS est une aide à la priorisation, pas une décision autonome. Combinez-le avec la présence réelle de la vulnérabilité, la criticité de l’actif, la possibilité d’exploitation et les autres signaux. Le percentile classe un score par rapport aux autres vulnérabilités ; il ne doit pas être confondu avec la probabilité absolue. La FAQ officielle de FIRST précise également qu’une preuve d’exploitation active et une présence dans KEV doivent primer sur un score EPSS qui semblerait faible.

### 6.3 KEV : exploitation connue

Le catalogue Known Exploited Vulnerabilities (KEV) de CISA est une source de CVE pour lesquelles une exploitation dans la nature est connue. Il représente un signal fort de priorisation. Sa portée juridique dépend de l’organisation et de la juridiction : des délais spécifiques peuvent s’appliquer à certaines entités, tandis que d’autres organisations peuvent l’adopter comme pratique de gestion du risque sans être directement soumises aux mêmes directives.

Lorsqu’une vulnérabilité présente sur un actif figure dans KEV, il faut immédiatement vérifier la présence réelle, l’exposition et la version affectée, planifier la correction ou la mitigation prioritaire, puis rechercher des signes d’exploitation si le scénario le justifie. L’absence d’un CVE dans KEV ne prouve pas l’absence d’exploitation, car le catalogue est sélectif et les informations évoluent.

### 6.4 Un modèle de risque contextualisé

Un modèle local peut utiliser des catégories telles que : preuve d’exploitation connue, exploit public, accessibilité Internet, privilèges nécessaires, importance de l’actif, sensibilité des données, périmètre de propagation, facilité de correction et efficacité des contrôles compensatoires. Il doit être reproductible et permettre d’expliquer pourquoi un item est classé comme urgent.

Évitez les pondérations arbitraires qui masquent un signal critique. Par exemple, un point de bonus lié à une faible exposition ne doit pas compenser mécaniquement une preuve d’exploitation active contre un serveur exposé qui protège des données majeures. Utilisez des règles de priorité minimales : KEV présent et actif exposé peut imposer une voie accélérée ; les autres facteurs affinent ensuite l’ordre, sans empêcher l’escalade.

~~~text
1. La vulnérabilité est-elle réellement présente ?
               |
               v
2. L'actif est-il accessible ou critique ?
               |
               v
3. Exploitation connue, preuve locale ou forte menace ?
               |
               v
4. Quel est le dommage métier plausible ?
               |
               v
5. Quel contrôle réduit réellement le chemin d'attaque ?
               |
               v
Priorité + délai + propriétaire + preuve attendue
~~~

### 6.5 Exemple de matrice de triage

La matrice suivante est une proposition d’exercice, pas une règle universelle ou un barème légal. Chaque organisation doit définir ses seuils avec le métier, les équipes techniques et les exigences applicables.

~~~text
Niveau Urgence       Signaux possibles
P0     immédiate     Exploitation en cours / actif critique fortement exposé
P1     urgente      KEV présent sur actif exposé ou voie d'attaque crédible
P2     élevée       Gravité élevée et exposition ou impact significatif
P3     planifiée    Risque modéré avec contrôles efficaces et échéance suivie
P4     backlog      Faible risque contextualisé, mais action/documentation requise

Toutes les classes gardent :
propriétaire | date cible | justification | statut | preuve
~~~

Le niveau ne doit pas être déterminé uniquement par le score CVSS. Une vulnérabilité de sévérité technique moyenne peut mériter un traitement très rapide si elle est exploitée, présente sur une passerelle Internet ou permet de contourner un contrôle crucial. Une vulnérabilité techniquement sévère sur un composant non affecté par la condition d’exploitation peut être moins urgente, mais la conclusion doit être justifiée par des preuves vérifiables.

## 7. Planifier la remédiation

### 7.1 Corriger, atténuer ou accepter temporairement

La correction élimine la faiblesse par l’installation d’un correctif, la mise à niveau, la modification du code, la mise à jour d’une dépendance ou la correction d’une configuration. La mitigation réduit la possibilité d’exploitation ou son impact sans nécessairement supprimer la cause. L’acceptation du risque conserve l’exposition et exige une décision formelle. Ces trois états ne doivent pas être confondus dans un tableau de bord.

La mitigation peut être un pare-feu applicatif, une règle de filtrage, la désactivation d’une fonctionnalité vulnérable, la restriction d’un port de gestion, une segmentation, un contrôle d’accès renforcé ou une configuration temporaire recommandée par l’éditeur. Elle doit être testée face au chemin d’exploitation connu. Une mitigation générique non validée peut produire un sentiment de sécurité sans réduire le risque.

### 7.2 Vérifier les correctifs et leurs prérequis

Avant de déployer un correctif, lire les notes de version, les prérequis, les dépendances, les problèmes connus, les éventuels changements de schéma, les exigences de redémarrage et les effets sur la compatibilité. Établir une sauvegarde ou un mécanisme de retour arrière lorsque c’est possible, choisir un groupe pilote et définir les tests fonctionnels et de sécurité.

La rapidité compte, mais installer un correctif sans valider les dépendances peut provoquer une indisponibilité métier. Il ne faut pas utiliser ce risque comme prétexte pour reporter indéfiniment l’action. Préparer les tests, le responsable, la fenêtre et le rollback permet d’accélérer de manière contrôlée. Pour un patch d’urgence, certains contrôles peuvent être accélérés mais doivent rester proportionnés à l’impact du changement.

~~~text
Avis éditeur + version affectée
             |
             v
Confirmer présence dans l'inventaire
             |
             v
Choisir correctif / mise à niveau / mitigation
             |
             v
Tester en environnement représentatif
             |
             v
Déployer par groupe avec surveillance
             |
             v
Vérifier version, service et sécurité
             |
             +--> succès : preuve et clôture
             |
             +--> échec : rollback, mitigation, enquête
~~~

### 7.3 Gestion des urgences

Une vulnérabilité exploitée peut exiger une réponse avant le prochain cycle habituel. Une procédure d’urgence doit préciser qui décide, qui est appelé en dehors des horaires, les actifs de périmètre, la façon de vérifier la version, la fenêtre de changement, la communication métier, le choix d’une mitigation provisoire et les critères de clôture. Sans cette procédure, les équipes se retrouvent à prendre des décisions à haut impact dans des canaux non traçables.

Une alerte ne justifie pas automatiquement de déployer partout un paquet non vérifié. La décision tient compte de la disponibilité du correctif, de sa source, des conditions d’exploitation, du risque de panne, de la possibilité d’isoler temporairement l’actif et de la probabilité d’exploitation locale. Pour les systèmes critiques, une mesure de confinement réversible peut être adoptée en parallèle à la préparation de la correction permanente.

### 7.4 Actifs hors support

Un système hors support ne reçoit plus les correctifs habituels du fournisseur. Les scans peuvent encore détecter les faiblesses, mais une solution durable implique généralement une mise à niveau, un remplacement, un isolement contrôlé ou un contrat de support explicite. La simple fermeture d’un ticket de vulnérabilité ne rend pas le système maintenable.

Pour les environnements hérités, le plan doit décrire la dépendance métier, les contraintes techniques, les mesures de segmentation et d’accès, la surveillance renforcée, les sauvegardes, le calendrier de remplacement et le financement. Toute mitigation doit avoir un responsable et des critères de révision. La présence d’un équipement ancien dans une zone isolée n’est pas une acceptation automatique ; le risque de mouvement latéral et l’accès de maintenance doivent également être étudiés.

### 7.5 Dépendances de la chaîne logicielle

Une vulnérabilité peut être corrigée à la source mais persister dans une image, une branche maintenue, un paquet interne, un cache de construction ou un service qui n’a pas été redéployé. Le processus doit suivre la dépendance du code jusqu’à l’artefact et l’instance de production. Une mise à jour déclarée dans le fichier de dépendances ne prouve pas que l’ancienne version a disparu de tous les environnements.

Les contrôles de pipeline doivent détecter les dépendances connues, enregistrer les versions résolues, signer ou attester les artefacts lorsque l’architecture le permet, conserver un SBOM et lier la version construite à son déploiement. Les exceptions de pipeline doivent avoir une échéance et un propriétaire. Un blocage automatique peut prévenir la mise en production d’un composant à risque, mais son seuil doit être conçu de façon à gérer les urgences et les faux positifs sans pousser les équipes à contourner l’outil.

## 8. Vérifier que le problème est réellement résolu

### 8.1 La clôture exige une preuve

Une tâche ne doit pas être clôturée parce que quelqu’un a déclaré « patch appliqué ». La preuve peut inclure la version installée, la configuration corrigée, le résultat du scan de confirmation, la sortie de l’outil de gestion de correctifs, une vérification du paquet et des tests applicatifs. L’élément de preuve doit être daté, associé à l’actif et conservé dans le système de suivi.

Une revalidation doit être appropriée à la vulnérabilité. Si l’outil ne détecte plus l’ancienne signature mais que la version reste vulnérable, le résultat peut être trompeur. Pour une bibliothèque embarquée, il faut contrôler l’artefact reconstruit et l’application réellement déployée, pas seulement l’environnement du développeur. Pour une mauvaise configuration, il faut vérifier l’état effectif, y compris si une autre règle réintroduit l’exposition.

~~~text
Ticket de vulnérabilité
       |
       v
Correctif déclaré installé
       |
       v
Vérifier version / configuration / artefact
       |
       v
Rescan ciblé ou test de confirmation
       |
       +--> vulnérabilité absente : clôture avec preuve
       |
       +--> vulnérabilité toujours présente : rouvrir
       |
       +--> résultat ambigu : investigation complémentaire
~~~

### 8.2 Faux sentiment de correction

Les erreurs de clôture courantes incluent : scanner le mauvais hôte, prendre un scan antérieur pour une preuve récente, confondre un paquet installé et un service redémarré, mettre à jour le code source sans reconstruire le conteneur, corriger un serveur tout en laissant un clone vulnérable et accepter une exception expirée sans réévaluation.

Il faut contrôler l’identifiant de l’actif, l’heure de mesure, la version réellement active, les réplications, les clusters, les images, les environnements de reprise et les ressources cloud éphémères. Un cas qui se reproduit doit être rouvert et analysé ; il ne doit pas être supprimé de la file d’attente pour améliorer les statistiques.

### 8.3 Rechercher une exploitation passée

La correction technique ne remplace pas une investigation lorsque des signes d’exploitation existent. Pour un actif potentiellement compromis, rechercher les indicateurs connus, les connexions inhabituelles, les processus et tâches anormaux, les modifications de fichiers, les comptes créés, les mouvements latéraux et les événements SIEM pertinents. Si des éléments indiquent une compromission, appliquer le processus de réponse à incident et préserver les preuves avant toute réinstallation qui pourrait détruire des données utiles.

Les états peuvent être distingués en « non affecté », « affecté sans signe d’exploitation connu », « possiblement compromis » et « compromis confirmé », selon la taxonomie adoptée. Ces catégories exigent une définition précise, car « absence de détection » ne signifie pas preuve d’absence. Le niveau de confiance, les sources observées, la période d’analyse et les angles morts doivent être consignés.

## 9. Intégrer la gestion des vulnérabilités au développement et au cloud

### 9.1 Shift left sans oublier la production

Détecter tôt une dépendance vulnérable ou une erreur de code coûte souvent moins cher qu’une correction après déploiement. Mais « shift left » ne signifie pas se limiter aux pipelines. Une application vulnérable peut se retrouver dans des versions anciennes toujours déployées, dans un service managé mal configuré ou dans une image qui n’a pas été reconstruite. Il faut relier les résultats de développement, le registre des artefacts et l’inventaire de production.

Les règles CI peuvent distinguer les nouvelles vulnérabilités des vulnérabilités déjà connues. Elles doivent empêcher la croissance du risque tout en gardant une voie d’urgence contrôlée. Il est utile de rendre le résultat compréhensible : composant, version, CVE, chemin de dépendance, version corrigée connue, contexte de présence et propriétaire du code. Une liste brute de milliers de résultats sans contexte encourage l’ignorance ou le contournement.

### 9.2 Conteneurs et images

Les images de conteneurs incorporent des couches et des bibliothèques. Une image immuable permet de relier les scans à un digest précis, mais il faut construire et redéployer l’image corrigée. Modifier un conteneur en fonctionnement sans reconstruire l’image produit une divergence difficile à reproduire et peut ne pas survivre au redémarrage.

Le programme doit scanner l’image de base, les paquets et les dépendances applicatives, suivre les images de production, reconstruire lorsque les bases sont mises à jour et nettoyer les images obsolètes lorsque les règles opérationnelles le permettent. Les registres doivent distinguer les images de test des artefacts promus en production et conserver la provenance nécessaire à l’investigation.

~~~text
Code + dépendances verrouillées
              |
              v
Construction reproductible de l'image
              |
              v
SBOM + scan de vulnérabilités
              |
              v
Contrôles d'admission et approbation
              |
              v
Promotion de l'artefact par digest
              |
              v
Déploiement et inventaire réel
              |
              v
Nouvelles alertes -> reconstruire et redéployer
~~~

### 9.3 Infrastructure as Code et cloud

Les environnements cloud changent vite. Les vérifications doivent inclure les images système, les services managés, les API d’administration, les groupes de sécurité, les identités, les chemins réseau, le chiffrement, les fonctions et les configurations d’exposition. Une vulnérabilité de composant et une erreur de configuration peuvent créer ensemble un chemin d’attaque plus grave que chacune prise isolément.

Les modèles IaC permettent de détecter les erreurs avant déploiement, tandis que la surveillance du cloud vérifie l’état réel. Les deux sont nécessaires : un environnement créé à la main peut contourner le modèle, et une modification manuelle postérieure peut provoquer une dérive. Le propriétaire du service doit connaître les ressources dynamiques qui appartiennent au même périmètre et la façon de confirmer leur remédiation.

### 9.4 SaaS et fournisseurs

L’organisation n’a pas toujours accès à un scan technique direct pour un SaaS. Elle peut utiliser les avis du fournisseur, les preuves d’audit, les notifications de sécurité, les engagements de correction, les versions ou régions affectées et les mécanismes contractuels d’escalade. La responsabilité partagée doit être écrite : le fournisseur corrige certaines couches, tandis que le client doit corriger les configurations, identités et intégrations qu’il maîtrise.

Une absence de visibilité n’est pas un motif pour classer un service comme sans risque. Documentez la dépendance, la criticité, les engagements contractuels, les contacts, les délais de notification et les options de contournement ou de sortie. Pour les composants critiques, exiger une voie de communication et un délai de traitement des vulnérabilités fait partie de la gestion des risques fournisseurs.

## 10. Divulgation responsable et coordination

### 10.1 Recevoir un rapport de vulnérabilité

Un rapport externe peut venir d’un chercheur, d’un client, d’un employé ou d’un partenaire. Le processus de divulgation doit fournir un canal clair, expliquer les informations attendues et interdire les actions dangereuses ou non autorisées dans les limites définies. L’équipe doit accuser réception, confirmer le périmètre, reproduire de façon contrôlée, évaluer l’impact, coordonner avec les développeurs et informer le déclarant du suivi raisonnablement possible.

La validation doit être conduite sur des systèmes autorisés. Ne demandez pas à un chercheur de démontrer une exfiltration de données réelles ou une perturbation de service lorsque la reproduction minimale suffit. Conservez le rapport, les horodatages, les preuves et les échanges nécessaires, tout en limitant l’accès aux données personnelles et aux informations sensibles.

### 10.2 Publication et coordination avec les éditeurs

Une divulgation peut demander une coordination entre le déclarant, le mainteneur, le fournisseur, un coordinateur et les personnes affectées. La chronologie dépend de la nature de la faille, de la disponibilité d’un correctif, des signes d’exploitation, des engagements et des règles applicables. Une publication prématurée de détails exploitables peut accroître les risques ; une absence de réponse du fournisseur nécessite une procédure d’escalade définie.

Le programme CVE facilite l’emploi d’identifiants communs pour les vulnérabilités divulguées publiquement. Une référence CVE améliore la coordination, mais ne dispense pas de publier des détails exploitables pour les défenseurs, des versions affectées et une solution lorsque cela est approprié. Les équipes de réponse doivent distinguer la confidentialité temporaire d’un rapport et l’obligation de fournir des informations suffisantes pour protéger les utilisateurs.

~~~text
Rapport reçu
    |
    v
Accusé de réception + périmètre autorisé
    |
    v
Triage et reproduction contrôlée
    |
    v
Évaluation de l'impact + notification interne
    |
    v
Correction / mitigation + tests
    |
    v
Coordination de publication si nécessaire
    |
    v
Conseils aux utilisateurs + clôture documentée
~~~

## 11. Mesurer l'efficacité du programme

### 11.1 Mesures de délai

Le délai de correction (time to remediate) peut être mesuré entre la date de détection validée et la date à laquelle la remédiation est vérifiée. Documentez le point de départ et la définition du point de fin. Si l’organisation mesure du « temps jusqu’à correctif déclaré » et l’appelle temps de correction vérifiée, la métrique surestime l’efficacité.

Mesurez des percentiles et des distributions, pas seulement une moyenne. Quelques vulnérabilités anciennes peuvent augmenter la moyenne ; une majorité de cas urgents peut être masquée par une longue file de faibles risques. Segmentez par niveau, famille d’actifs, propriétaire, exposition et source. Les délais de détection, d’affectation, de décision, d’atténuation et de vérification donnent des diagnostics plus précis que le seul temps total.

### 11.2 Couverture, dette et récurrence

Les indicateurs de couverture peuvent inclure la part des actifs éligibles évalués dans la fenêtre, le taux de scans authentifiés quand ils sont pertinents, la part des actifs avec propriétaire, les dépendances de production inventoriées et les écarts entre actifs découverts et actifs officiels. La dette de vulnérabilité peut être définie comme le nombre ou le risque pondéré des problèmes ouverts, mais la formule doit rester stable et explicitée.

La récurrence indique qu’un problème revient après correction : image de base jamais mise à jour, même mauvaise configuration répétée, patch non intégré à l’automatisation ou exception devenue permanente. L’indicateur de récurrence doit conduire à une action de cause racine, par exemple corriger le modèle IaC, la bibliothèque partagée, la norme d’image ou le processus d’approbation.

~~~text
Tableau de bord opérationnel
  |-- actifs inconnus et couverture de scan
  |-- vulnérabilités critiques et KEV présentes
  |-- âge du backlog par niveau
  |-- délai médian et percentile de correction vérifiée
  |-- exceptions actives et échéances expirées
  |-- taux de faux positifs confirmés
  |-- récurrence des causes techniques
  |-- résultats de validation après déploiement
~~~

### 11.3 Éviter la mauvaise incitation

Un objectif fondé uniquement sur le nombre de vulnérabilités fermées peut inciter à fermer les cas les plus simples, à multiplier les doublons ou à déclarer des mitigations non vérifiées. Le tableau de bord doit mesurer la réduction réelle d’exposition et la qualité de la preuve. La quantité peut rester un indicateur secondaire, mais le résultat métier et le risque résiduel doivent rester au centre.

Chaque indicateur a une définition de données, un propriétaire, une fréquence, un périmètre, une cible et des limites. Une variation peut venir d’une meilleure détection plutôt que d’une détérioration du système ; une baisse peut provenir d’un scan qui a échoué. Les indicateurs doivent donc être interprétés avec la couverture, la qualité de la collecte et le contexte des changements.

## 12. Automatisation, intégrations et qualité des données

### 12.1 Relier scanner, ticketing et déploiement

Le flux automatisé doit transférer le résultat utile : identifiant stable de l’actif, vulnérabilité, preuve, source, première et dernière observation, priorité, propriétaire, échéance, statut et lien vers l’avis. Il doit éviter de générer un ticket distinct à chaque scan pour la même vulnérabilité sur le même actif. La corrélation doit être stable, mais conserver la possibilité de distinguer des occurrences différentes.

Une intégration sûre valide les permissions, journalise les actions, gère les erreurs, limite les données sensibles et rend visible l’échec de synchronisation. Si l’outil de ticketing est inaccessible, le résultat critique ne doit pas disparaître silencieusement. Un mécanisme de reprise ou une file d’attente permet de synchroniser après le retour du service. Les automations qui modifient directement les systèmes doivent être limitées et auditées.

### 12.2 Règles de déduplication

La clé de corrélation peut combiner l’identifiant d’actif, le CVE ou l’identifiant du scanner, le composant, la version affectée et la famille de détection. Une correspondance uniquement sur le titre du problème peut fusionner deux failles différentes. À l’inverse, une clé trop stricte crée des milliers de tickets pour le même défaut.

Les résultats doivent garder leurs sources d’origine et les transformations opérées. Lorsqu’un scanner change son format ou qu’un actif est renommé, il faut une migration contrôlée pour ne pas réinitialiser l’âge du backlog. Les tickets clôturés réouverts doivent refléter la nouvelle observation, et les exceptions ne doivent pas masquer automatiquement toutes les nouvelles versions de la même vulnérabilité.

### 12.3 Accès et secrets des scanners

Les comptes d’analyse, clés API et secrets d’intégration sont des éléments sensibles. Ils doivent disposer du minimum de permissions, avoir une rotation, être stockés dans un coffre approprié et ne pas apparaître dans les commandes, journaux ou résultats de scan. Les comptes de scan ne doivent pas servir à l’administration quotidienne. Surveiller leurs usages permet de détecter les erreurs et les abus.

L’exécution d’un outil sur le mauvais périmètre peut provoquer une charge ou une perturbation. Utilisez des listes d’autorisation, des limites de débit, des fenêtres, un mécanisme d’arrêt et des tests sur un groupe pilote. Les scans actifs sur des systèmes fragiles nécessitent une analyse de risque et une approbation de l’exploitant.

## 13. Travaux pratiques guidés

Les travaux pratiques utilisent des actifs fictifs ou un laboratoire que vous contrôlez. Ne scannez pas un réseau tiers sans autorisation écrite et un périmètre précis. Les sorties de résultats ci-dessous sont des données pédagogiques, pas des indications sur l’état réel d’un logiciel ou d’un service public.

### TP 1 — Construire et vérifier un inventaire

**Scénario :** l’organisation fictive KivuLab possède des serveurs Linux et Windows, deux équipements réseau, une application de gestion, des postes administrés, plusieurs instances cloud et une application avec des dépendances tierces. Les données de la CMDB et de l’EDR divergent.

**Travail demandé :**
1. Construire une table des actifs avec identifiant stable, type, propriétaire, environnement, exposition, criticité et dernière observation.
2. Repérer les doublons et les actifs présents dans une source mais absents de l’autre.
3. Choisir une méthode de rapprochement qui n’utilise pas uniquement l’adresse IP.
4. Définir des règles d’éligibilité et des actifs nécessitant une méthode alternative.
5. Calculer la couverture de mesure sur un ensemble connu, puis écrire pourquoi ce chiffre ne prouve pas la complétude de l’inventaire.
6. Définir une procédure de traitement des actifs inconnus avec un propriétaire et une échéance.
7. Présenter les champs sensibles et les permissions d’accès à l’inventaire.

**Correction de référence :** la table de référence doit identifier un actif indépendamment de son adresse temporaire ; elle peut associer ID cloud, numéro de série, UUID d’agent et nom courant. Une entrée vue dans l’EDR mais pas dans la CMDB devient une anomalie à attribuer, pas un objet à supprimer. Les actifs impossibles à scanner directement obtiennent une méthode de vérification alternative. La couverture se calcule sur un dénominateur explicitement défini, tandis que les actifs inconnus sont mesurés séparément.

**Livrable :** inventaire de démonstration, règles de déduplication, calcul de couverture, registre des écarts et plan de rattrapage.

### TP 2 — Prioriser un backlog avec CVSS, EPSS et KEV

**Scénario :** vous recevez les observations suivantes, dont toutes les données sont fictives :

- Faille A : CVSS élevé, pas d’exploitation connue dans les sources consultées, serveur de test isolé.
- Faille B : CVSS moyen, entrée dans KEV, application Internet exposée et service critique.
- Faille C : score EPSS élevé, mais le composant n’existe pas dans votre inventaire après validation.
- Faille D : CVSS critique dans une bibliothèque du produit, mais la version déployée est encore incertaine.
- Faille E : CVSS élevé, système hors support avec un correctif impossible à installer avant remplacement.

**Travail demandé :**
1. Définir les données supplémentaires nécessaires pour chaque cas.
2. Classer la priorité de traitement et justifier les facteurs utilisés.
3. Distinguer une vulnérabilité confirmée, une exposition probable et un cas incertain.
4. Préciser les mesures immédiates, l’action définitive, le responsable et la preuve de clôture.
5. Définir quand il faut déclencher une investigation de compromission.
6. Expliquer comment vous éviterez qu’un score EPSS ou CVSS décide seul.

**Correction de référence :** la faille B passe en voie d’urgence à cause de l’exploitation connue et de l’exposition d’un service critique, sans attendre qu’un score isolé confirme la priorité. La faille A mérite d’être traitée dans le délai défini mais son contexte peut réduire l’urgence relative. La faille C est d’abord un problème de qualité de données ou de périmètre ; si l’absence est confirmée, documenter la décision sans prétendre qu’un actif vulnérable existe. Pour D, confirmer le composant et l’artefact réellement déployé. Pour E, formaliser un plan avec contrôle compensatoire, propriétaire, échéance de remplacement et autorité qui accepte le risque résiduel.

**Livrable :** registre trié, rationales, échéances, mesures de réduction de risque et conditions de réévaluation.

### TP 3 — Déployer et vérifier un correctif en sécurité

**Scénario :** une application de test utilise une bibliothèque vulnérable. Une version corrigée est disponible, mais le produit utilise des images de conteneur et une pipeline de construction. L’application ne doit pas être mise à jour directement en production sans vérification.

**Travail demandé :**
1. Confirmer la présence de la bibliothèque et les versions affectées dans le manifeste et l’artefact.
2. Identifier la version corrigée recommandée dans la source éditeur et les prérequis.
3. Modifier la dépendance, reconstruire l’artefact et créer ou mettre à jour le SBOM.
4. Exécuter les tests fonctionnels et l’analyse de dépendances.
5. Promouvoir l’artefact identifié par un digest stable vers un environnement pilote.
6. Vérifier que la production exécute réellement l’artefact corrigé.
7. Réexécuter le scan ou un contrôle de confirmation, conserver la preuve et fermer le ticket uniquement si la faiblesse n’est plus détectée et que les tests sont acceptés.
8. Définir le rollback et les actions si le correctif casse une fonction.

**Correction de référence :** le changement de fichier de dépendances n’est que la première étape. Le nouveau build doit contenir la version corrigée, être testé, et c’est ce même artefact qui doit être promu. Le contrôle de production doit correspondre au digest, à la version ou à l’identifiant effectivement déployé. Si l’ancien conteneur subsiste dans un cluster ou un environnement de reprise, le ticket reste ouvert pour ces instances. Si la correction provoque une régression, revenir au build approuvé et appliquer une mitigation validée pendant la correction du problème, sans perdre la trace du risque résiduel.

**Livrable :** diff de dépendance, résultats de build et de tests, SBOM, preuve de déploiement, résultat du scan et procédure de retour arrière.

### TP 4 — Gérer une exception sur un actif hors support

**Scénario :** un équipement réseau essentiel ne reçoit plus de correctifs de sécurité. Son remplacement prendra plusieurs mois. Une vulnérabilité à risque élevé a été identifiée ; l’équipement possède une interface d’administration et communique avec des segments utilisateurs.

**Travail demandé :**
1. Confirmer le modèle, la version, le statut de support et la vulnérabilité applicable.
2. Décrire les chemins d’accès à l’équipement et l’impact d’une exploitation.
3. Comparer remplacement, mise à niveau, isolement, filtrage de gestion et restrictions de fonctionnalités.
4. Construire une demande d’exception avec risques résiduels, propriétaire, autorité, échéance et plan de sortie.
5. Définir des contrôles de détection et des vérifications périodiques.
6. Préparer une procédure d’urgence si une exploitation est observée.
7. Définir la preuve qui permettra de fermer l’exception après remplacement.

**Correction de référence :** une exception doit être proportionnée et temporaire. La solution durable consiste à migrer vers une plateforme supportée. Jusqu’à ce que cela soit possible, limiter l’accès de gestion aux postes et réseaux d’administration, supprimer les services inutiles si le constructeur le recommande, réduire les chemins réseau, renforcer les journaux et tester la sauvegarde de configuration. L’approbation doit venir de l’autorité responsable du risque métier, pas uniquement de l’équipe qui exploite l’équipement. Une date de fin et une revue périodique sont obligatoires.

**Livrable :** fiche de risque, plan de mitigation, demande d’exception, calendrier et critères de sortie.

## 14. Exercices corrigés

### Exercice 1 — CVE et correctif

Un ticket contient un identifiant CVE, mais aucune version corrigée n’est indiquée. Peut-on conclure que le problème ne peut pas être traité ?

**Correction :** non. Il faut consulter l’avis de l’éditeur, les versions affectées, les mises à jour disponibles et les mitigations recommandées. L’absence d’un champ dans une base ne signifie pas l’absence de solution.

### Exercice 2 — CVSS élevé sur un actif isolé

Une vulnérabilité a un score CVSS Base élevé, mais l’actif est isolé et contient peu de données. Peut-on classer automatiquement le cas en dernier ?

**Correction :** non. L’isolement et l’impact local modifient le contexte, mais il faut vérifier les chemins d’administration, le mouvement latéral, les usages et les contrôles. La priorité doit suivre une méthode documentée, pas une règle unique.

### Exercice 3 — KEV et EPSS divergent

Une vulnérabilité figure dans KEV, mais EPSS est faible. Quel signal faut-il privilégier ?

**Correction :** la présence dans KEV représente une exploitation connue et doit être traitée comme un signal fort. EPSS prédit une probabilité d’observation future et n’est pas un historique complet de l’exploitation active. Il faut confirmer si le produit est affecté et répondre rapidement.

### Exercice 4 — EPSS élevé sur une technologie absente

EPSS indique une probabilité élevée, mais vous avez validé que le composant n’est déployé nulle part. Quelle action est correcte ?

**Correction :** documenter les sources d’inventaire vérifiées, enregistrer la non-applicabilité avec preuve et surveiller les nouvelles versions de l’inventaire. Il ne faut pas créer une remédiation fictive ni conclure à un risque local sans actif affecté. Il faut cependant s’assurer que l’inventaire couvre les dépendances, images et services externalisés.

### Exercice 5 — Couverture de scan

L’inventaire contient 600 actifs éligibles et 510 ont un scan valide dans la fenêtre. Quel est le taux de couverture ?

**Correction :** 510 ÷ 600 = 0,85, soit 85 %. Ce résultat ne mesure que la couverture par rapport au dénominateur connu ; les actifs inconnus et les limites de profondeur de scan doivent être suivis séparément.

### Exercice 6 — Scan non authentifié

Un scanner externe ne signale aucune vulnérabilité sur un serveur. Peut-on le déclarer sûr ?

**Correction :** non. Le scan peut ne voir que la surface réseau et manquer les paquets, correctifs ou paramètres internes. Il faut une méthode authentifiée ou une source alternative appropriée et une preuve de couverture.

### Exercice 7 — Faux positif

Un scanner signale un paquet affecté, mais le fournisseur a rétroporté un correctif sans changer le numéro de version visible. Que faire ?

**Correction :** vérifier l’avis du fournisseur et la preuve locale du correctif. Documenter la conclusion, conserver l’identifiant de scan et le raisonnement, puis ajouter une règle de validation si le cas est récurrent. Ne pas supprimer le signal sans preuve.

### Exercice 8 — Dépendance transitive

Le fichier de dépendances directes ne mentionne pas une bibliothèque vulnérable, mais le scanner SCA la trouve dans le build. Pourquoi ?

**Correction :** elle peut être introduite par une dépendance transitive ou embarquée dans un autre composant. Il faut identifier le chemin de dépendance et corriger à la source appropriée, puis reconstruire l’artefact.

### Exercice 9 — Correctif annoncé installé

Le ticket indique « patch appliqué », mais le scan de confirmation retrouve la même vulnérabilité. Peut-on fermer le ticket comme succès ?

**Correction :** non. Il faut vérifier la bonne machine, la version réellement active, le redémarrage requis, les réplications et la signature du scanner. Le ticket reste ouvert jusqu’à une preuve valide ou une exception approuvée.

### Exercice 10 — Actif hors support

Une appliance hors support est considérée « faible risque » parce qu’elle n’a pas d’accès Internet direct. Quels autres éléments faut-il examiner ?

**Correction :** les chemins d’administration, réseaux d’accès, partenaires, mouvement latéral, vulnérabilités connues, comptes, sauvegardes, exposition indirecte et possibilités de remplacement. L’absence d’accès direct n’annule pas le risque.

### Exercice 11 — Mitigation

La désactivation d’une fonctionnalité vulnérable est proposée. Quelle preuve faut-il demander ?

**Correction :** confirmer que la fonctionnalité est effectivement désactivée sur l’instance en service, que les chemins alternatifs sont contrôlés et que le test correspondant échoue comme prévu. Documenter l’impact métier, la durée et le plan de correction définitive.

### Exercice 12 — Délai dépassé

Une vulnérabilité dépasse le délai cible mais le propriétaire n’a pas répondu. Que faire ?

**Correction :** déclencher l’escalade prévue, identifier un suppléant ou une autorité, appliquer des mesures de réduction de risque si elles sont justifiées et enregistrer le blocage. Le silence ne vaut ni acceptation du risque ni clôture.

### Exercice 13 — Priorité et criticité

Deux vulnérabilités ont le même score. L’une touche un système exposé qui traite des données sensibles, l’autre un système de test isolé. Doivent-elles nécessairement avoir la même échéance ?

**Correction :** non. L’exposition, le rôle métier, l’impact et les signaux de menace différencient le risque contextualisé. Le modèle local doit expliquer comment ces dimensions modifient la priorité.

### Exercice 14 — Qualité de l’inventaire

Le taux de couverture est passé de 90 % à 98 % après que le périmètre a été réduit. Est-ce forcément une amélioration ?

**Correction :** non. Une exclusion non justifiée peut artificiellement améliorer l’indicateur. Il faut tracer les modifications du périmètre et les exclusions, et surveiller les actifs inconnus.

### Exercice 15 — SBOM

Un SBOM a été généré pendant le développement. Suffit-il à prouver ce qui fonctionne en production ?

**Correction :** non. Il faut l’associer à l’artefact exact et à son digest ou identifiant, puis vérifier que cet artefact a été déployé. Un build différent ou une image plus ancienne peut encore contenir la dépendance vulnérable.

### Exercice 16 — Scan d’un environnement sensible

Le scan actif risque de perturber un équipement industriel. Quelle approche est la plus appropriée ?

**Correction :** évaluer le risque avec l’exploitant et choisir une méthode approuvée : collecte passive, informations de version, contrôle fournisseur, scan en laboratoire, fenêtre contrôlée ou autre méthode alternative. L’actif reste dans le programme et la limite de visibilité est documentée.

### Exercice 17 — Nombre de tickets

Une équipe ferme 500 tickets de vulnérabilité en un mois. Peut-on conclure que le risque a fortement diminué ?

**Correction :** pas uniquement. Il faut contrôler la qualité de la clôture, le niveau de risque, la présence d’actifs exposés, les tickets réouverts et les preuves de correction. Le volume fermé est un indicateur d’activité, pas une mesure suffisante du résultat.

### Exercice 18 — Exploitation suspectée

Une vulnérabilité KEV est identifiée sur un serveur, et les logs indiquent des requêtes anormales. Que faut-il ajouter à la remédiation ?

**Correction :** déclencher une investigation selon le processus d’incident, rechercher des indicateurs et des comportements anormaux, préserver les preuves, déterminer si l’actif est compromis et coordonner le confinement. L’installation du correctif n’efface pas une compromission préalable.

### Exercice 19 — Exception expirée

Une exception a dépassé sa date, mais le service fonctionne sans incident connu. Que faire ?

**Correction :** réévaluer le risque, vérifier l’état de la mitigation et escalader pour renouvellement formel ou correction. L’absence d’incident observé n’est pas une preuve que la vulnérabilité n’a pas été exploitée.

### Exercice 20 — Automatisation défaillante

Le scanner continue de fonctionner, mais la synchronisation avec l’outil de ticketing est interrompue. Pourquoi est-ce un incident de processus ?

**Correction :** les vulnérabilités peuvent être détectées mais rester sans propriétaire, échéance ou suivi. L’intégration doit alerter sur les erreurs, conserver une file de reprise et synchroniser les résultats après rétablissement.

## 15. Défi final — Piloter une campagne prioritaire

**Scénario :** KivuLab exploite une application métier dans le cloud, un cluster de conteneurs, un parc de postes, deux serveurs historiques et un équipement réseau en fin de support. Le scanner a détecté 420 résultats. Plusieurs sont des doublons, certains actifs n’ont pas de propriétaire et une dépendance vulnérable figure dans l’image de production. Une autre vulnérabilité est listée dans KEV sur une passerelle exposée. L’équipe doit réduire le risque sans interrompre les services essentiels.

Toutes les données sont fictives ; l’objectif est de construire un processus reproductible, pas de viser un produit particulier.

### Livrables obligatoires

1. **Inventaire :** dresser la liste des actifs concernés, identifier les inconnus, attribuer propriétaires et criticité métier.
2. **Qualité :** dédupliquer les résultats, valider les faux positifs avec une preuve et signaler les données manquantes.
3. **Priorité :** combiner applicabilité, exposition, CVSS, EPSS, KEV, impact métier et contrôles existants ; justifier chaque priorité.
4. **Plan de remédiation :** définir l’action, le responsable, l’échéance, les prérequis, le test et la preuve attendue.
5. **Urgence KEV :** organiser la réponse à la passerelle exposée et établir si une investigation de compromission est nécessaire.
6. **Dépendance :** mettre à jour, reconstruire, tester et promouvoir un artefact corrigé en reliant le résultat au déploiement.
7. **Actif hors support :** préparer une exception encadrée et un plan de sortie réaliste.
8. **Mesure :** définir couverture, délai de correction vérifiée, vieillissement du backlog, exceptions et récurrence.
9. **Gouvernance :** fournir un tableau de bord et une synthèse destinée à la direction.

### Correction de référence

Commencez par vérifier le périmètre et la qualité des données. Le nombre brut de 420 résultats n’est pas le nombre de vulnérabilités uniques ni le niveau de risque. Utilisez un identifiant stable pour l’actif, reliez le CVE ou la signature à la version, fusionnez les doublons sans perdre les détails de source, et conservez les cas incertains dans une file de validation. Tout actif inconnu doit avoir un processus d’attribution au lieu d’être supprimé du périmètre.

La passerelle exposée avec une vulnérabilité KEV est la priorité de réponse. Vérifiez immédiatement l’applicabilité, l’avis fournisseur, la version, le correctif et les mitigations disponibles. Appliquez une correction validée ou une restriction temporaire coordonnée avec l’exploitant, puis vérifiez la version active. Les requêtes anormales éventuelles doivent être examinées pour déterminer s’il existe des signes de compromission. Ne concluez pas « non compromis » uniquement parce qu’aucune alerte n’est présente.

Pour la dépendance vulnérable, identifiez le chemin de dépendance et l’image de production exacte. Mettez à jour la source, reconstruisez, exécutez les tests, générez ou actualisez le SBOM, puis déployez l’artefact identifié. Contrôlez tous les réplicas et environnements de reprise. Un correctif dans la branche principale ne prouve pas que le cluster n’exécute plus l’image précédente.

Pour l’actif hors support, comparez remplacement, mise à niveau, isolement et contrôle d’accès. Formalisez le risque résiduel, l’autorité d’approbation, les responsables, la date de sortie et les contrôles compensatoires. L’exception ne doit pas effacer la vulnérabilité des mesures : elle doit rester visible et être réévaluée.

Le tableau de bord final montre la couverture réelle de mesure, les vulnérabilités prioritaires ouvertes, les échéances en retard, les cas KEV, les exceptions actives, les délais de correction vérifiée et les résultats réouverts. La direction doit comprendre le risque résiduel, les dépendances nécessaires, les décisions attendues et l’effet des retards. Le rapport ne se limite pas au nombre de tickets fermés.

### Barème sur 100 points

- Qualité de l’inventaire et attribution des propriétaires : 15 points.
- Déduplication, validation et qualité des preuves : 10 points.
- Priorisation contextualisée et usage correct de KEV/EPSS/CVSS : 20 points.
- Traitement urgent de l’actif exposé et investigation appropriée : 15 points.
- Remédiation vérifiée de la dépendance : 10 points.
- Exception et plan de sortie de l’actif hors support : 10 points.
- Tableau de bord et indicateurs fiables : 10 points.
- Gouvernance, échéances et communication du risque : 10 points.

Une solution qui classe uniquement par CVSS, ferme sans revalidation ou exclut les actifs inconnus ne peut pas obtenir tous les points. La réussite exige une réduction démontrable de l’exposition et une traçabilité permettant de refaire la décision.

## 16. Checklist opérationnelle

Avant d’annoncer que le programme est opérationnel, vérifier les éléments suivants :

- Le périmètre couvre les actifs connus et définit une voie d’investigation pour les actifs inconnus.
- Les propriétaires, la criticité métier, l’exposition et le statut de support sont renseignés ou signalés comme données manquantes.
- Les sources de découverte et de scan sont identifiées, surveillées et rapprochées de l’inventaire.
- Les scans authentifiés et non authentifiés sont employés selon le risque et les limites sont documentées.
- Les composants logiciels, dépendances, images de conteneurs et artefacts de production sont reliés à des versions exactes.
- Les références CVE, les avis éditeurs et les sources de renseignement sont vérifiés avant une décision importante.
- CVSS n’est pas utilisé seul ; EPSS et KEV sont interprétés selon leur signification et leurs limites.
- Chaque vulnérabilité prioritaire possède un propriétaire, une échéance, une action et une preuve attendue.
- Les correctifs sont préparés, testés et déployés avec un plan de rollback proportionné.
- Les mesures compensatoires ont été testées et leurs échéances sont surveillées.
- Les exceptions sont approuvées par l’autorité compétente, expirent ou sont réévaluées et incluent un plan de sortie.
- Une nouvelle analyse ou un test de confirmation vérifie l’état réellement déployé.
- Les cas suspects sont transmis au processus de réponse à incident et les preuves sont préservées.
- Les intégrations ne perdent pas les résultats lors d’une panne et les secrets des scanners sont protégés.
- Les indicateurs distinguent couverture, activité, risque résiduel et qualité des preuves.
- Les tendances de récurrence sont analysées pour corriger les causes systémiques.

## 17. Glossaire

**Actif** : système, application, composant, service ou ressource dont l’organisation dépend et qu’elle doit inventorier et protéger.

**Avis éditeur** : document du fournisseur qui décrit les produits et versions affectés, les corrections et les mitigations.

**Backlog** : ensemble des vulnérabilités ouvertes et non encore vérifiées comme corrigées ou traitées.

**CISA KEV** : catalogue de vulnérabilités connues comme exploitées dans la nature, maintenu par la CISA.

**CVE** : identifiant commun associé à une vulnérabilité divulguée publiquement.

**CVSS** : Common Vulnerability Scoring System, cadre de communication de la gravité technique.

**CWE** : Common Weakness Enumeration, classification des catégories de faiblesses logicielles.

**DAST** : analyse dynamique d’une application en fonctionnement.

**EPSS** : modèle probabiliste qui estime la probabilité qu’une exploitation d’un CVE soit observée dans la nature au cours des 30 prochains jours.

**Faux positif** : détection qui ne s’applique pas réellement au produit ou à l’état de l’actif examiné.

**Faux négatif** : vulnérabilité réelle qui n’est pas détectée par la méthode utilisée.

**Mitigation** : mesure qui réduit l’exposition ou les conséquences sans nécessairement supprimer la cause technique.

**NVD** : National Vulnerability Database, base américaine qui fournit des enrichissements normalisés pour des vulnérabilités.

**Patch management** : processus de sélection, acquisition, installation et vérification des correctifs et mises à jour.

**Remédiation** : action qui corrige une vulnérabilité ou traite le risque selon la décision approuvée.

**Risque résiduel** : risque qui reste après la mise en œuvre des contrôles ou mitigations.

**SBOM** : Software Bill of Materials, inventaire des composants logiciels associés à un produit ou artefact donné.

**SCA** : analyse des dépendances logicielles et de leurs vulnérabilités connues.

**SLA/SLO de correction** : cible de délai, définie par la politique, pour traiter une catégorie de risque.

**SAST** : analyse statique du code ou d’un artefact sans exécution normale de l’application.

**DAST** : analyse des interfaces d’une application en fonctionnement.

**Exception** : dérogation documentée et approuvée, avec risque résiduel, échéance et plan de sortie.

**Falsification d’inventaire** : décision, volontaire ou accidentelle, qui masque des actifs ou fausse l’évaluation de la couverture.

**Remédiation vérifiée** : correction dont la réalisation et l’effet attendu ont été confirmés par des preuves appropriées.

## 18. Références officielles et lecture complémentaire

- NIST SP 800-40 Rev. 4 — Guide to Enterprise Patch Management Planning: Preventive Maintenance for Technology : https://csrc.nist.gov/pubs/sp/800/40/r4/final
- FIRST — CVSS v4.0 Specification Document : https://www.first.org/cvss/v4.0/specification-document
- FIRST — CVSS v4.0 User Guide : https://www.first.org/cvss/v4.0/user-guide
- FIRST — EPSS, présentation et accès aux données : https://www.first.org/epss/
- FIRST — EPSS FAQ, signification et limites des scores : https://www.first.org/epss/faq
- FIRST — Using EPSS, conseils de priorisation : https://www.first.org/epss/using-epss
- CISA — Known Exploited Vulnerabilities Catalog : https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- CISA — Federal Government Cybersecurity Incident and Vulnerability Response Playbooks : https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks
- NIST SP 800-216 — Recommendations for Federal Vulnerability Disclosure Guidelines : https://csrc.nist.gov/pubs/sp/800/216/final
- CVE Program — Overview : https://www.cve.org/About/Overview
- NVD — National Vulnerability Database : https://nvd.nist.gov/

Les guides NIST, CISA et les délais réglementaires peuvent viser des périmètres ou des juridictions précis. Il convient de distinguer une bonne pratique technique d’une obligation directement applicable à l’organisation. Vérifiez les versions courantes des avis et politiques au moment de prendre une décision de production.

## Schéma complémentaire A — Chaîne de preuve de remédiation

~~~text
Avis de sécurité + CVE
          |
          v
Actif + version exacte + preuve de présence
          |
          v
Action autorisée et approuvée
          |
          v
Version/configuration réellement déployée
          |
          v
Scan de confirmation + contrôle fonctionnel
          |
          v
Preuve datée attachée au ticket
          |
          v
Clôture vérifiable ou réouverture
~~~

La chaîne de preuve empêche de confondre l’intention, l’exécution et le résultat. La note de version indique ce que le correctif devrait changer ; le système déployé et le test de confirmation indiquent si ce changement a effectivement atteint l’actif. Cette distinction est particulièrement importante pour les clusters, les images et les composants partagés.

## Schéma complémentaire B — État de vie d'un constat

~~~text
Nouveau
  |
  v
À valider -----> Faux positif confirmé / preuve conservée
  |
  v
Confirmé et priorisé
  |
  v
Assigné + échéance
  |
  +--> Correction en cours
  |
  +--> Mitigation temporaire / exception approuvée
  |
  v
Vérification indépendante
  |
  +--> Réouvert si encore présent
  |
  +--> Clos si preuve suffisante
~~~

Un statut n’est utile que s’il représente une étape bien définie et qu’une personne sait comment le faire progresser. « En cours » ne doit pas durer indéfiniment sans prochaine action. « Clos » doit signifier que les conditions de clôture convenues sont remplies, et pas simplement que l’équipe a terminé une intervention.


## Conclusion

La gestion des vulnérabilités est un mécanisme de réduction du risque, pas une simple collecte de scores. Elle exige un inventaire crédible, une détection appropriée, une priorité contextualisée, des propriétaires responsables, une remédiation testée et une vérification de l’état réel. CVSS décrit la gravité technique, EPSS estime une probabilité d’exploitation future observée, et KEV signale des vulnérabilités connues comme exploitées : leur signification est complémentaire et aucune donnée isolée ne décrit tout le risque local.

Le programme devient fiable lorsque les exceptions restent visibles, les actifs inconnus sont investigués, les correctifs sont suivis jusqu’aux artefacts déployés et les résultats sont démontrés par des preuves. Il progresse enfin en utilisant les récurrences pour corriger les causes systémiques : images de base, dépendances, modèles IaC, inventaires, mécanismes d’approbation et responsabilités.

Fin du cours.