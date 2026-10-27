# Sécurité de la supply chain

> **Mise en contexte**

Une application en production n’est presque jamais le produit d’une seule équipe qui écrit tout son code depuis zéro. Elle assemble des bibliothèques open source, des images de base, des outils de compilation, des actions d’intégration continue, des services cloud, des composants fournis par des partenaires et parfois du firmware ou des logiciels préinstallés. Chaque dépendance ajoute des fonctionnalités, mais aussi une relation de confiance. Une faiblesse dans un composant, un compte mainteneur compromis, un pipeline qui fuit des secrets ou un artefact remplacé après sa construction peut compromettre le produit final sans que le code métier principal ait changé.

La sécurité de la supply chain consiste à maîtriser ces relations depuis l’acquisition et le développement jusqu’à la construction, la livraison, le déploiement, l’exploitation et la fin de vie. Elle exige de connaître les fournisseurs et les composants, de protéger les environnements de production logicielle, de vérifier l’identité et la provenance des artefacts, de réduire les privilèges, de documenter les preuves et de planifier une réponse aux incidents impliquant des dépendances. Il ne suffit pas de scanner des bibliothèques ou de signer des fichiers : les contrôles doivent se compléter.

Ce cours prolonge la gestion des vulnérabilités. Il s’adresse aux équipes sécurité, développement, exploitation, achats et architecture qui doivent établir des garanties vérifiables sur les logiciels, matériels et services dont elles dépendent. Les exemples sont fictifs et les travaux pratiques se font sur un laboratoire isolé ou des ressources que vous êtes autorisé à administrer.

## Objectifs pédagogiques

À la fin du cours, vous saurez cartographier les relations de confiance d’une chaîne d’approvisionnement logicielle, évaluer le risque fournisseur, distinguer un SBOM d’une attestation de provenance, comprendre les formats SPDX et CycloneDX, durcir le dépôt source et les pipelines CI/CD, sécuriser les secrets et les runners, signer et vérifier des artefacts, comprendre SLSA 1.2, produire des preuves de construction, gérer les dépendances et leurs mises à jour, intégrer les contrôles aux achats et aux contrats, réagir à une compromission de dépendance et mesurer l’efficacité du programme.

Le principe directeur est simple : ne faites pas confiance à un artefact uniquement parce qu’il porte un nom connu ou qu’il se trouve dans un registre attendu. Vérifiez qu’il correspond à la source approuvée, qu’il a été construit par un processus autorisé, que ses composants et sa provenance sont documentés et que le produit déployé est bien celui qui a été contrôlé. Toutes les vérifications doivent être proportionnées au risque, automatisables lorsque c’est pertinent et compréhensibles par les équipes qui prennent les décisions.

## 1. Modéliser la supply chain

### 1.1 Une chaîne de relations, pas une liste de fournisseurs

La chaîne d’approvisionnement peut inclure les fournisseurs directs, les sous-traitants, les mainteneurs open source, les registres de paquets, les plateformes de construction, les services de signature, les fournisseurs cloud, les services SaaS, les fabricants de composants matériels et les opérateurs de distribution. Une dépendance peut elle-même dépendre de nombreuses autres. Le produit livré est donc le résultat d’un graphe de composants, d’acteurs, de processus et de systèmes.

~~~text
Organisation
   |
   +--> Dépôt source et mainteneurs
   |        |
   |        +--> dépendances directes et transitives
   |
   +--> Outils CI/CD et runners
   |        |
   |        +--> compilateurs, actions, images de build
   |
   +--> Registre et service de signature
   |
   +--> Fournisseur cloud / SaaS
   |
   v
Artefact livré --> déploiement --> service métier
~~~

Chaque relation apporte un type de confiance différent. Un contrat peut définir les obligations de notification d’un fournisseur, mais ne prouve pas qu’un paquet précis a été construit à partir du code attendu. Une signature peut vérifier l’intégrité d’un artefact et l’identité de la clé ou de l’identité signataire, mais elle ne prouve pas que le code est exempt de vulnérabilité. Un SBOM décrit des composants déclarés, mais ne garantit pas que chacun est sûr. Il faut associer les garanties à des questions précises.

### 1.2 Les principaux objectifs de sécurité

La supply chain sécurisée doit préserver l’intégrité des sources et des artefacts, contrôler les identités qui peuvent modifier ou publier, limiter l’accès aux secrets, vérifier la provenance, maîtriser les dépendances, détecter les vulnérabilités, réduire les possibilités de substitution et assurer la disponibilité du processus de livraison. La traçabilité permet d’identifier le commit, l’environnement de construction, les paramètres significatifs et l’artefact réellement diffusé.

La disponibilité est également une dimension de sécurité. Une bibliothèque devenue indisponible, un compte mainteneur verrouillé, une registry compromise ou une licence incompatible peut bloquer un service ou empêcher une version corrective. Une chaîne résiliente prévoit les miroirs autorisés, la sauvegarde des composants nécessaires, les procédures de retrait, les reconstructions et une stratégie de migration. Il faut cependant éviter de recopier aveuglément des paquets publics dans un miroir interne : le miroir doit préserver la provenance et les règles de validation.

### 1.3 Construire un modèle de confiance

Commencez par les actifs et les résultats attendus, puis identifiez les personnes, systèmes et tiers qui peuvent modifier chaque élément. Il faut savoir qui peut pousser du code, approuver une pull request, modifier un workflow, publier un paquet, changer les paramètres du runner, utiliser les clés de signature et déployer l’artefact. Une matrice de confiance révèle les accès trop larges ou les chemins où une seule identité peut modifier et valider le même résultat.

~~~text
Question : qui peut modifier le résultat livré ?
       |
       +--> code source
       +--> dépendance / lockfile
       +--> workflow CI
       +--> runner / image de construction
       +--> paramètres de publication
       +--> clé ou identité de signature
       +--> promotion vers production
       |
       v
Pour chaque chemin : identité, permission, preuve, contrôle indépendant
~~~

La séparation des tâches est particulièrement importante. Si une seule identité peut modifier le code, changer le pipeline, supprimer les tests et publier l’artefact, la chaîne peut être compromise en une étape. Les approbations, environnements protégés, signatures générées par le service de construction et contrôles indépendants rendent cette compromission plus difficile et plus visible.

## 2. Menaces sur la chaîne d’approvisionnement

### 2.1 Dépendance malveillante ou compromise

Une dépendance peut être malveillante dès sa publication, compromise après la prise de contrôle du compte du mainteneur, ou modifiée à la suite d’un incident sur l’infrastructure de distribution. Le code malveillant peut s’exécuter pendant la construction, au premier lancement ou seulement dans certaines conditions. Il peut tenter d’exfiltrer des secrets accessibles au processus, ouvrir un canal réseau, installer une charge différée, manipuler les artefacts ou désactiver les contrôles.

Le risque ne se limite pas aux paquets déclarés directement dans le projet. Une dépendance transitive peut ajouter d’autres composants, et un plugin du système de build peut exécuter du code avec des droits très élevés. La réponse consiste à maîtriser les sources autorisées, verrouiller les versions, analyser la composition, séparer les secrets, réduire les droits d’exécution et vérifier la provenance des artefacts.

### 2.2 Typosquatting et confusion de dépendances

Le typosquatting consiste à publier un paquet dont le nom ressemble à celui d’un paquet légitime ou contient une variation facile à confondre. La confusion de dépendances survient notamment lorsqu’un outil choisit un paquet public alors qu’un paquet interne de même nom était attendu, selon les règles de résolution et la configuration des registres. Ces scénarios sont facilités par des noms mal vérifiés, des dépôts sans propriétaire clair et des configurations ambiguës.

~~~text
Projet attend : bibliotheque-interne
              |
              v
Configuration du registre ambiguë
              |
       +------+------+
       |             |
       v             v
Registre privé    Registre public
paquet attendu    nom similaire / package inattendu
       |             |
       +------?------+
              |
              v
Risque : résolution vers une source non approuvée
~~~

Pour réduire ce risque, définissez les registres de confiance, les espaces de noms internes, les règles de priorité, les propriétaires des paquets et les versions verrouillées. Vérifiez les métadonnées de publication. Les noms seuls ne constituent pas une preuve : le projet source, le mainteneur, le hash, la signature et la provenance peuvent fournir des signaux complémentaires.

### 2.3 Compromission du dépôt source

Un attaquant qui compromet un compte mainteneur, un jeton d’accès ou une clé SSH peut modifier le code, la configuration de construction, le fichier des dépendances ou les workflows. La modification peut être discrète : ajout d’une action tierce, désactivation d’un test, changement de source du paquet ou permission trop large. Même si la branche principale est protégée, un workflow qui utilise des références mouvantes peut évoluer sans revue adéquate.

Il faut protéger les comptes avec MFA ou passkeys, restreindre les permissions des jetons, examiner les règles de branches, exiger des revues pour les chemins sensibles, surveiller les changements de workflow et utiliser des règles d’approbation adaptées au niveau de risque. Les changements d’infrastructure de livraison et ceux du code produit ne doivent pas nécessairement suivre la même politique : les fichiers qui définissent la confiance méritent une revue spécifique.

### 2.4 Compromission de la CI/CD

Le pipeline a souvent accès au code, aux dépendances, aux jetons de publication et parfois aux secrets de production. Un runner compromis peut altérer l’artefact tout en produisant des tests apparemment normaux. Un workflow non fiable peut recevoir les secrets d’un environnement protégé si les règles d’événement ou de permission sont mal définies. Les caches de dépendances et les répertoires persistants peuvent aussi transporter des éléments inattendus entre jobs.

~~~text
Commit / pull request
        |
        v
Workflow autorisé ?
        |
        v
Runner isolé + identité à privilèges limités
        |
        +--> installation contrôlée des dépendances
        +--> tests et scans
        +--> build reproductible ou traçable
        |
        v
Artefact + provenance + signature
        |
        v
Vérification indépendante avant promotion
~~~

Un pipeline sûr sépare le code non fiable des secrets et environnements sensibles. Il utilise des runners éphémères ou régulièrement reconstruits, limite la persistance, épingle les actions et images à des références vérifiées, restreint les permissions de jetons et garde les secrets hors des logs. La vérification du workflow doit être systématique, pas seulement celle du code applicatif.

### 2.5 Substitution de l’artefact

Un paquet peut être correctement construit puis remplacé avant son téléchargement ou son déploiement. Cela peut arriver à la suite d’une compromission de registre, d’un jeton de publication, d’un cache partagé ou d’un chemin de promotion trop permissif. L’intégrité de l’artefact doit être liée à un digest cryptographique, et la provenance doit indiquer comment l’objet a été produit.

Le digest confirme que deux objets ont le même contenu selon la fonction de hachage utilisée ; il ne dit pas à lui seul si le contenu est légitime. Il faut vérifier le digest par rapport à une source fiable, examiner une signature et contrôler les attentes de provenance. Si la source de confiance elle-même est compromise, la signature peut confirmer un artefact qui ne devrait jamais avoir été publié.

### 2.6 Attaques sur le matériel et le firmware

La supply chain inclut le matériel physique : composants contrefaits, provenance incertaine, firmware modifié, versions non supportées, appareils reconditionnés de manière opaque ou pièces remplacées sans traçabilité. Ces risques sont particulièrement importants pour les équipements réseau, les systèmes industriels, les dispositifs embarqués et les appliances de sécurité.

La prévention comprend des fournisseurs approuvés, des contrôles à la réception, le suivi des numéros de série, des empreintes ou signatures du firmware lorsque le fabricant les fournit, une gestion des mises à jour, un démarrage sécurisé quand il existe et un processus de retrait des composants suspects. Une signature de firmware est utile seulement si la chaîne de clés et la méthode de vérification sont fiables et si l’appareil applique réellement cette vérification.

### 2.7 Dépendance au service externe et au mainteneur

Un mainteneur peut abandonner un projet, perdre l’accès au compte, subir une pression, ou ne plus pouvoir corriger les failles. Un fournisseur SaaS peut modifier son architecture, ses sous-traitants, ses mécanismes de support ou sa politique de notification. Ces risques affectent aussi la capacité à comprendre et traiter un incident.

Le plan de continuité doit considérer la disponibilité du source, la possibilité de reconstruire, la portabilité des données, les alternatives de remplacement, la procédure d’escalade et les obligations contractuelles. Pour les composants critiques, l’organisation doit savoir si elle dépend d’une seule personne ou d’un service qui n’offre aucune solution de sortie.

## 3. Gouvernance du risque fournisseur

### 3.1 Classer les fournisseurs selon leur criticité

Une évaluation efficace ne soumet pas tous les fournisseurs au même questionnaire. Le niveau de contrôle dépend du rôle de la solution, de la sensibilité des données, de l’accès au réseau, du privilège technique, de la continuité métier, du degré de dépendance et de la capacité à remplacer le service. Un prestataire qui construit un artefact signé pour un produit critique peut nécessiter plus de garanties qu’un fournisseur d’un outil sans accès à des systèmes sensibles.

~~~text
Critères de criticité fournisseur
  |-- impact sur le service métier
  |-- accès aux données / secrets
  |-- privilèges réseau et système
  |-- dépendance technologique et délai de sortie
  |-- visibilité sur sous-traitants
  |-- maturité de sécurité et incidents connus
  |-- capacité de notification et de correction
              |
              v
Niveau de risque -> exigences -> preuve -> réévaluation
~~~

La classification doit être justifiée et révisée lors des changements de contexte. Un service initialement non critique peut devenir central après une migration. Un fournisseur peut accéder à de nouvelles données ou recevoir un jeton de déploiement. Les équipes d’achats doivent être informées de ces changements, car le contrat et l’évaluation peuvent devoir être adaptés.

### 3.2 Questionnaire et preuves vérifiables

Un questionnaire fournisseur permet de recueillir les pratiques déclarées, mais une réponse positive ne vaut pas une preuve de fonctionnement. Les questions doivent être liées au risque : comment le fournisseur gère-t-il les comptes privilégiés, les vulnérabilités, les incidents, les dépendances, les versions de firmware, les SBOM, les accès de support et la fin de vie ? Quelles preuves peut-il fournir ? Quel est le périmètre de l’attestation ou de l’audit ? Quelle est sa date ?

Les preuves possibles incluent des rapports d’audit, attestations de certification, description des contrôles, engagements contractuels, SBOM, attestations de provenance, avis de sécurité, statistiques de correction et rapports de tests. Vérifiez la période couverte, les exclusions et les écarts. Un certificat ne prouve pas que chaque produit ou chaque sous-traitant est couvert par le même périmètre.

### 3.3 Exigences contractuelles

Les clauses de sécurité devraient être adaptées au service et à la juridiction. Elles peuvent traiter des notifications d’incidents, délais de correction, vulnérabilités critiques, accès privilégiés, chiffrement, sous-traitance, conservation et suppression des données, droit d’audit, mise à jour de firmware, gestion de fin de support, SBOM, intégrité des artefacts, continuité et assistance à la sortie. Les clauses ne sont utiles que si les rôles et délais sont définis et si l’organisation peut les suivre.

Ne transformez pas toutes les bonnes pratiques en exigences absolues sans considérer la faisabilité, le risque et le contexte réglementaire. Une clause impossible à vérifier ne garantit rien. Il faut désigner le propriétaire contractuel, conserver les preuves, établir des contacts d’escalade et programmer une revue périodique. Pour un incident critique, le fournisseur doit savoir comment joindre l’organisation et quelles informations fournir sans exposer davantage ses autres clients.

### 3.4 Sous-traitants et dépendances indirectes

Une entreprise peut acheter un service à un fournisseur direct qui utilise lui-même un hébergeur, une société de support, un registre ou un sous-traitant spécialisé. La visibilité peut s’arrêter au premier niveau. Le programme doit identifier les sous-traitants importants, les dépendances technologiques communes et les possibilités de propagation d’un incident. Il n’est généralement pas réaliste d’exiger le même détail sur chaque acteur indirect ; on cible ceux qui peuvent accéder aux actifs critiques ou interrompre le service.

Une dépendance commune à plusieurs fournisseurs peut créer un risque de concentration. Si plusieurs applications reposent sur le même registre, la même identité cloud ou la même bibliothèque, un incident unique peut affecter plusieurs produits. Les analyses doivent tenir compte de ces points partagés et prévoir des plans de continuité compatibles avec le service métier.

## 4. SBOM : connaître la composition du logiciel

### 4.1 Définition et limites

Un SBOM (Software Bill of Materials) est un inventaire formel des composants logiciels associés à un produit ou à un artefact. Il peut identifier des paquets, versions, relations de dépendance, fournisseurs, auteurs, licences et informations de provenance du document. Il sert à répondre à des questions pratiques : quelle application contient telle bibliothèque ? quelles versions sont concernées par un CVE ? quelle partie faut-il reconstruire ? quelles licences doivent être examinées ?

Un SBOM est une vue de la composition, pas une certification de sécurité. Sa qualité dépend de son exhaustivité, sa fraîcheur, la méthode de génération et le lien à un artefact concret. Un SBOM généré depuis le dépôt source peut ne pas correspondre au conteneur final s’il existe des dépendances embarquées, des paquets injectés au build, des modules compilés ou des composants ajoutés au déploiement.

~~~text
Source et manifestes
       |
       v
Résolution des dépendances
       |
       v
Construction de l'artefact
       |
       v
SBOM associé au digest précis
       |
       v
Inventaire et corrélation avec les CVE
       |
       +--> composant affecté : localiser les produits
       +--> pas de composant : conserver la preuve et la méthode
~~~

### 4.2 Génération au bon moment

Produisez un SBOM au moment où les versions sont résolues ou le produit est construit, puis associez-le à l’artefact final. Conservez le nom et la version du produit, l’identifiant ou digest, l’auteur ou l’outil de génération, le contexte de génération, la date et les composants. Pour les logiciels déployés, le SBOM doit être relié à l’image ou au paquet qui fonctionne réellement.

Le document doit être signé ou distribué dans un mécanisme qui permet de vérifier son origine lorsque le risque l’exige. Une signature sur un SBOM ne garantit pas que l’inventaire soit complet : elle protège surtout l’intégrité et la provenance du document signé. Il faut encore faire confiance au producteur et à son processus de génération, puis tester la couverture contre l’artefact.

### 4.3 Éléments minimums en évolution

Les exigences et recommandations SBOM évoluent pour améliorer l’interopérabilité et la possibilité d’automatisation. La guidance CISA et partenaires publiée en 2026 a ajouté ou renforcé des éléments comme le hash du composant, la licence, le nom de l’outil SBOM et le contexte de génération, ainsi que des recommandations de partage et de traitement machine. Les organisations doivent consulter la version actuelle de la spécification et les obligations applicables avant de définir leurs exigences contractuelles. Il ne suffit pas de produire un fichier JSON sans confirmer qu’il contient les métadonnées nécessaires.

Les éléments d’identité du composant doivent éviter les noms ambigus. Les identifiants, la version, le fournisseur, les empreintes et les relations de dépendance facilitent le rapprochement. Lorsque l’information est inconnue, ne l’inventez pas : utilisez les champs prévus, indiquez la limite et évaluez les conséquences sur l’analyse de risque.

### 4.4 SPDX et CycloneDX

SPDX est un standard ouvert utilisé notamment pour décrire des composants logiciels, licences et relations. Sa spécification actuelle indiquée par le site officiel est SPDX 3.0, standardisée comme ISO/IEC 5962:2021. CycloneDX est une spécification de nomenclature logicielle et de chaîne d’approvisionnement qui peut représenter des composants, services, dépendances et d’autres types d’actifs ; le site officiel présente la version 1.7 comme version courante. Les capacités précises diffèrent et doivent être comparées avec les besoins d’outillage.

Ne choisissez pas un format uniquement parce qu’un outil le produit par défaut. Vérifiez que les consommables savent le lire, que les relations et identifiants sont conservés, que les champs requis sont disponibles et que les données peuvent être intégrées au suivi des vulnérabilités. Le format ne garantit pas la qualité ; l’exactitude et le lien à l’artefact sont essentiels.

### 4.5 Consommer un SBOM en exploitation

Un SBOM devient utile lorsqu’il est intégré à un inventaire et corrélé avec les avis de vulnérabilité. Le processus doit retrouver les produits qui contiennent le composant, vérifier si la version est concernée, identifier les propriétaires, déterminer l’exposition et créer une action de remédiation. Les versions antérieures du SBOM doivent rester disponibles pour les enquêtes : savoir ce qui était déployé à une date donnée aide à évaluer une vulnérabilité divulguée après coup.

La correspondance des noms peut être imparfaite entre les écosystèmes. Utilisez les identifiants normalisés disponibles et vérifiez les cas ambigus. Un résultat « aucun composant touché » n’est fiable que si le SBOM couvre le bon artefact et la méthode de génération. Un document incomplet ne doit pas servir à déclarer un produit non affecté.

## 5. Provenance, signatures et attestations

### 5.1 Distinguer SBOM, digest, signature et provenance

Le digest cryptographique identifie le contenu d’un artefact de manière compacte. La signature permet d’établir que le contenu signé ou référencé n’a pas été modifié depuis la signature et de vérifier l’identité liée à la clé ou au mécanisme de signature. La provenance décrit comment l’artefact a été construit : source, processus de build, builder et paramètres ou entrées pertinents. Une attestation relie un sujet à une déclaration vérifiable produite par une identité ou un système.

Ces mécanismes répondent à des questions différentes. Le SBOM répond « de quels composants le produit est-il constitué ? ». Le digest répond « quel objet précis est-ce ? ». La signature répond « quelle identité a signé cet objet ou cette déclaration ? ». La provenance répond « comment cet objet a-t-il été produit ? ». Aucun ne prouve seul que le logiciel est sans défaut, et aucun ne remplace les tests, l’analyse de code et la surveillance.

~~~text
Artefact final
   |
   +--> digest : identité exacte du contenu
   |
   +--> signature : identité / intégrité de l'objet signé
   |
   +--> provenance : source et processus de construction
   |
   +--> SBOM : inventaire des composants
   |
   +--> résultats de tests : contrôles et constats observés
   |
   v
Décision de promotion selon des règles vérifiées
~~~

### 5.2 Qu'est-ce que la provenance ?

Une provenance de build fiable décrit de manière claire l’artefact produit, le code source ou l’entrée principale, la plateforme de construction et le processus exécuté. Les champs exacts dépendent du format et du niveau de garantie, mais l’objectif est d’établir si un artefact correspond à un build autorisé. La provenance doit être générée par un système dont l’intégrité est protégée, plutôt que par un script libre que l’attaquant pourrait modifier avec le code qu’il construit.

Le consommateur doit définir les attentes : dépôt canonique, branche ou commit autorisé, builder accepté, procédure de build, identités attendues et artefact. Il vérifie ensuite que les déclarations correspondent à ces attentes. La simple présence d’un fichier de provenance n’est pas suffisante si un acteur non fiable peut le fabriquer ou si le vérificateur ne contrôle aucune propriété pertinente.

### 5.3 SLSA et niveau de garantie

SLSA est un cadre d’amélioration progressive des garanties de la chaîne logicielle. La version 1.2 est la version actuelle sur le site officiel consulté pour ce cours ; elle comprend les tracks Build et Source. Dans le track Build, les niveaux L1 à L3 progressent de la présence d’une provenance jusqu’à une provenance signée produite par une plateforme hébergée, puis à un environnement de build renforcé avec des protections supplémentaires. Il faut toujours préciser la version et le track, car les anciens contenus SLSA peuvent utiliser des termes ou niveaux différents.

Un niveau n’est pas un score universel de sécurité du produit. Il décrit des garanties dans un périmètre précis. Le bon objectif est d’identifier quelles attaques le niveau choisi cherche à réduire, quelles exigences sont réellement remplies et quelle partie de la chaîne reste hors garantie. Par exemple, une provenance de build robuste ne prouve pas que les dépendances sont sans vulnérabilité ou que les comptes des mainteneurs sont inviolables.

~~~text
SLSA Build L1 : provenance présente
          |
          v
SLSA Build L2 : provenance générée et signée
par une plateforme de build hébergée
          |
          v
SLSA Build L3 : plateforme renforcée, isolation
et protections accrues contre l'altération du build

L'implémentation et la vérification réelles déterminent le niveau.
~~~

### 5.4 Attestations et vérification au déploiement

Une attestation est une déclaration structurée qui relie un sujet, souvent un artefact identifié par digest, à un type de déclaration. Une politique de déploiement peut exiger une provenance conforme, une signature provenant d’une identité attendue, un SBOM valide et des tests passés. Le vérificateur doit refuser les artefacts lorsque les conditions requises ne sont pas satisfaites, ou suivre une voie d’exception contrôlée et enregistrée.

Les règles ne doivent pas être ambiguës. Si l’identité signataire, le dépôt, le workflow et la référence source sont connus, vérifiez-les explicitement. Évitez les politiques qui acceptent une signature de n’importe quelle identité d’un domaine large, ou qui ignorent les champs absents. Une attestation valide mais issue d’un dépôt non approuvé ne doit pas suffire pour déployer un paquet en production.

### 5.5 Rotation des clés et identités de signature

Les clés ou identités qui signent les artefacts sont des actifs de haute valeur. Leur gestion prévoit la création, la protection, la rotation, la révocation, la vérification des signatures historiques et la réponse à une compromission. Il faut séparer l’identité qui construit, celle qui autorise la publication et celle qui approuve le déploiement lorsque le risque le justifie.

Les systèmes de signature sans clé peuvent réduire la dépendance à des secrets durables en utilisant des identités de workload et une infrastructure de transparence, mais ils restent dépendants de l’identité, des règles de confiance, de la configuration du pipeline et du service de vérification. La technologie choisie doit être évaluée dans le contexte opérationnel. La signature n’est pas un remède à un build compromis si l’attaquant peut faire signer son artefact par l’identité légitime au cours d’une exécution autorisée.

## 6. Sécuriser le code source et les dépôts

### 6.1 Protéger les identités de développeur et de mainteneur

Les dépôts source et les comptes de mainteneur contrôlent l’entrée du processus de construction. Utilisez une authentification forte, des comptes individuels, un accès minimal, une revue des membres, la révocation rapide des accès sortants et une séparation des comptes personnels et techniques. Les jetons doivent être limités à un dépôt ou à une action lorsque c’est possible, associés à une durée et surveillés.

Les clés SSH, jetons d’accès personnel et identifiants de registry ne doivent pas être copiés dans le code, les issues, les logs ou des exemples pédagogiques. Un secret publié doit être considéré compromis : révoquez-le, cherchez son usage, évaluez les artefacts affectés et examinez les journaux. Effacer un secret du dernier commit ne retire pas les copies historiques ou les clones.

### 6.2 Revue des changements sensibles

Protégez les branches principales, exigez des approbations, contrôles CI et règles de résolution des discussions pour les changements à risque. Les workflows, fichiers de dépendance, scripts de release, fichiers de configuration du registre et politiques de publication méritent une attention renforcée car ils peuvent changer les garanties de tous les builds suivants. Les exceptions à la revue doivent être limitées et journalisées.

L’approbateur doit comprendre le changement. Un clic mécanique sur une approbation ne garantit rien si la revue ne porte pas sur le diff et les conséquences. Les changements de dépendances doivent montrer la nouvelle version, la source, l’avis de sécurité, l’effet sur l’API et les tests. Les changements de workflows doivent être analysés comme du code d’infrastructure privilégié.

### 6.3 Protéger le contenu non fiable

Une pull request provenant d’un fork ou d’un contributeur inconnu peut exécuter du code dans le pipeline. Ne lui fournissez pas automatiquement des secrets de publication ou d’environnement. Séparez les jobs de validation des contributions non fiables des jobs de release. Les événements de workflow et les permissions réelles doivent être relus avec soin : une combinaison incorrecte d’événements peut permettre à un code non approuvé d’accéder à un jeton privilégié.

~~~text
Pull request non fiable
       |
       v
Tests isolés, sans secrets de release
       |
       v
Revue + vérifications requises
       |
       v
Merge autorisé dans la branche protégée
       |
       v
Build/release de confiance sur plateforme protégée
       |
       v
Signature et provenance
~~~

Le principe est d’éviter qu’une exécution contrôlée par l’auteur de la pull request puisse influencer une publication de confiance. Les caches, les artefacts entre jobs et les runners persistants doivent être pris en compte. Si un build non fiable écrit dans un cache consommé par la release, la séparation apparente des jobs peut ne rien protéger.

## 7. Durcir la CI/CD et les runners

### 7.1 Moindre privilège des jetons

Un workflow doit recevoir uniquement les permissions nécessaires. Les jetons à portée globale, les secrets permanents et les identifiants partagés entre projets augmentent le rayon d’impact d’une compromission. Les permissions d’écriture doivent être réservées aux jobs qui publient réellement. L’authentification temporaire ou les identités de workload peuvent être préférables lorsque la plateforme les supporte et que la configuration est vérifiée.

Les secrets doivent être injectés seulement dans le job et l’étape qui en ont besoin. Un test de code tiers ne devrait pas recevoir un jeton de publication. La valeur des secrets peut apparaître dans les fichiers temporaires ou être accessible au processus ; le masquage des logs n’est pas une frontière de sécurité suffisante. Nettoyez l’environnement et limitez l’accès réseau des tâches de build.

### 7.2 Runners éphémères et isolation

Un runner persistant peut conserver des fichiers, caches, processus ou identifiants entre exécutions. Si un code non fiable partage l’environnement avec un job privilégié, une contamination peut traverser les étapes. Les runners éphémères, l’isolation des jobs, les images de build maintenues, la limitation des accès réseau et la destruction de l’environnement après usage réduisent ces risques.

Pour un runner auto-hébergé, l’organisation est responsable de l’OS, du réseau, de l’accès administrateur, des mises à jour, des journaux et de la gestion du cycle de vie. Il ne faut pas placer un runner capable de publier des artefacts sensibles dans un réseau plat avec des bases de données ou des systèmes de production accessibles sans contrôle. Les workloads de construction doivent avoir la connectivité nécessaire, pas un accès illimité.

### 7.3 Épingler les actions et images

Référencer une action par une branche mouvante ou une étiquette de version qui peut être réaffectée facilite les mises à jour, mais ne garantit pas que le code exécuté soit resté identique. Épingler à un commit ou un digest approuvé et gérer explicitement les mises à jour réduit le risque de remplacement silencieux. La procédure doit inclure la vérification de la source, la revue du changement, les tests et une mise à jour planifiée des références.

L’épinglage seul n’est pas une garantie absolue. Un commit peut contenir du code malveillant ou vulnérable ; une référence épinglée peut devenir obsolète. Il faut combiner la revue des dépendances d’action, le suivi de vulnérabilités, la provenance et un calendrier de mise à jour. Les exceptions doivent être justifiées par un risque connu, pas par la commodité.

### 7.4 Caches et artefacts intermédiaires

Les caches accélèrent les builds mais deviennent une source de confiance si leur contenu est réutilisé. Séparez les caches selon le niveau de confiance, la branche ou la plateforme lorsque cela est nécessaire. N’acceptez pas un artefact intermédiaire provenant d’une source non fiable dans une release protégée sans validation. Utilisez des clés de cache fondées sur les inputs pertinents et prévoyez leur invalidation après une compromission.

Les artefacts de build doivent avoir une durée de conservation et un contrôle d’accès adaptés. Le pipeline ne doit pas télécharger un fichier de release simplement parce qu’il se trouve dans le bon répertoire ; le fichier doit être relié à une exécution connue et validé. Pour une enquête, conservez les manifestes, digest, attestations et logs essentiels dans une zone qui n’est pas modifiable par la même identité que celle qui publie.

## 8. Dépendances, versions et registres

### 8.1 Verrouillage des dépendances

Un fichier de manifeste exprime souvent des plages de versions, tandis qu’un lockfile enregistre les versions résolues et parfois les hashes. Le verrouillage stabilise le build et limite les résolutions inattendues, mais il n’assure pas que les dépendances soient sûres. Il faut générer et examiner le lockfile avec les outils de l’écosystème, vérifier les sources et prévoir des mises à jour contrôlées.

Une chaîne reproductible enregistre la version du compilateur, les dépendances directes et transitives, les paramètres de build et l’identité de la source. Reproductibilité signifie que des entrées et un processus définis permettent d’obtenir le même résultat ou un résultat comparably vérifiable, selon les contraintes. Certaines constructions incluent des horodatages ou éléments non déterministes ; il faut alors expliquer la limite et utiliser d’autres preuves de provenance.

### 8.2 Registres et miroirs internes

Les registres privés peuvent appliquer des politiques, mettre en cache des paquets, conserver des artefacts et limiter les accès aux dépôts autorisés. Ils doivent toutefois être protégés comme tout système critique : MFA, rôles, séparation de publication et téléchargement, journalisation, sauvegardes, gestion des jetons, validation des paquets entrants et procédure de retrait.

Un miroir ne doit pas absorber silencieusement n’importe quel paquet public dans les builds de production. Il peut nécessiter une étape de validation, une politique de namespace, des scans et une attestation d’origine. Pour les paquets essentiels, conservez assez de données pour reproduire un build ou migrer vers une source de secours lorsque le registre d’origine est indisponible ou compromis.

### 8.3 Mises à jour et maintenance

Les dépendances doivent être mises à jour de façon régulière, avec des mécanismes automatiques de proposition, de test, de revue et de fusion. Les mises à jour de sécurité peuvent suivre une voie accélérée lorsqu’un risque est urgent. Les versions abandonnées doivent déclencher une décision : migrer, forker sous gouvernance explicite, remplacer ou accepter un risque résiduel avec une date de sortie.

Le verrouillage ne doit pas devenir une excuse pour ne jamais mettre à jour. La chaîne doit permettre de renouveler les versions tout en conservant des preuves et en limitant les régressions. Les mises à jour doivent être attribuées à un propriétaire, tester les fonctionnalités critiques et inclure le déploiement réel. Le backlog des dépendances anciennes doit être visible dans le tableau de bord.

## 9. Sécurité des artefacts et du déploiement

### 9.1 Promouvoir le même artefact

Un principe important consiste à construire une fois un artefact identifié, le vérifier et promouvoir ce même artefact entre les environnements. Recompiler séparément pour la recette et pour la production crée des écarts possibles : une dépendance a pu changer, une variable ou un script a pu être modifié, ou un environnement a pu utiliser une autre image de base. Si la reconstruction est nécessaire, les nouvelles sorties doivent être revalidées et reliées à leur provenance.

~~~text
Commit approuvé
      |
      v
Build -> digest + SBOM + provenance + tests
      |
      v
Vérification indépendante des attentes
      |
      v
Promotion du même digest vers recette
      |
      v
Validation fonctionnelle et sécurité
      |
      v
Promotion du même digest vers production
      |
      v
Inventaire du déploiement réel et surveillance
~~~

La promotion par digest réduit l’ambiguïté d’une étiquette mutable comme latest. L’inventaire de production doit conserver l’identifiant exact de l’artefact. Si une étiquette est utilisée, il faut pouvoir résoudre à quel digest elle correspond au moment du déploiement. Une fois déployé, surveillez les dérives et assurez-vous que les nœuds ou régions exécutent la version attendue.

### 9.2 Politique d’admission

Une politique d’admission peut refuser un artefact si des conditions définies ne sont pas satisfaites : provenance absente ou invalide, signature inattendue, SBOM manquant, vulnérabilité au-delà d’un seuil, licence non approuvée ou version interdite. Les règles doivent être documentées et tester les scénarios d’échec. Elles doivent également prévoir un mécanisme d’urgence contrôlé pour éviter que les équipes contournent la politique de manière cachée en cas d’incident.

L’outil qui vérifie doit être distinct de la partie non fiable quand c’est possible. Une attestation qui peut être réécrite par le même job que l’artefact perd une partie de sa valeur. De même, le scanner ne doit pas être autorisé à modifier la conclusion après une validation humaine sans trace. Les exceptions d’admission doivent être ciblées, temporaires et visibles.

### 9.3 Déploiement, configuration et secrets

La sécurité supply chain continue après la publication : un artefact validé peut être déployé dans un mauvais environnement, avec des permissions excessives ou des secrets incorrects. Les configurations doivent être versionnées, les secrets injectés par une méthode appropriée et les changements de production audités. Le système de déploiement doit limiter les identités capables de substituer un artefact et préserver une trace de la version appliquée.

Les secrets n’ont pas besoin d’être incorporés dans l’image. Ils doivent être fournis au runtime, avec des permissions limitées et une rotation. Une fuite du processus de build peut nécessiter la rotation de tous les secrets accessibles pendant l’exécution, pas seulement le mot de passe associé au dépôt. Conservez une cartographie des secrets, des permissions et des jobs qui les consomment.

## 10. Open source, mainteneurs et confiance communautaire

### 10.1 Évaluer le risque d’une dépendance open source

Une dépendance open source peut être excellente, largement auditée et très utile, mais son statut public ne garantit pas qu’elle soit activement maintenue ou protégée. Examinez la source canonique, les mainteneurs, le rythme de publication, la politique de sécurité, les avis et corrections, les tests, les dépendances transitives, les permissions de publication et les mécanismes de provenance.

Le nombre d’étoiles ou de téléchargements n’est pas une preuve de sécurité. Il indique au mieux une forme d’adoption ou de visibilité. Un projet peu connu peut être maintenu correctement ; un projet très populaire peut devenir une cible prioritaire. Les indicateurs d’hygiène comme OpenSSF Scorecard peuvent aider à identifier les points à examiner, mais un score ne remplace pas une évaluation contextualisée.

### 10.2 Sponsoring, bus factor et succession

Les composants critiques maintenus par une seule personne présentent un risque de continuité et de succession. Cela ne signifie pas qu’ils sont malveillants, mais qu’un départ, une perte de compte ou une indisponibilité peut retarder la correction. Le programme peut financer la maintenance, contribuer des tests, soutenir plusieurs mainteneurs ou planifier une alternative. Il doit éviter de transformer un logiciel libre en dépendance invisible sans ressource ni responsable interne.

Un fork interne exige lui-même un processus de maintenance : suivi de l’amont, corrections, revue, tests, provenance des builds et gestion de licence. Un fork abandonné peut créer une dette plus coûteuse que le remplacement. Il faut définir les critères de sortie avant de créer une branche privée permanente.

### 10.3 Gouvernance des licences

La chaîne d’approvisionnement implique aussi les obligations de licence. Les obligations dépendent de la licence, du mode de distribution, de la manière dont le composant est lié ou modifié et du contexte juridique. Un SBOM aide à inventorier les composants, mais ne suffit pas à déterminer toutes les obligations. Les équipes juridiques ou spécialisées doivent interpréter les cas qui le nécessitent.

Ne supprimez pas un composant uniquement sur la base d’un champ licence incomplet. Confirmez la licence exacte et la source. Les règles d’approbation doivent distinguer les licences autorisées, les licences qui requièrent une analyse et les éléments dont l’information est inconnue. Les risques de sécurité et de licence peuvent toucher les mêmes dépendances mais doivent rester traçables séparément.

## 11. Firmware, matériel et logiciels embarqués

### 11.1 Cycle de vie matériel

Pour les équipements physiques, reliez le fournisseur, le modèle, le numéro de série, la révision matérielle, la version firmware, la date de mise en service, la garantie et le statut de support. Lors de la réception, vérifiez la commande, les références, les scellés ou informations de provenance appropriées, et les identifiants attendus. Les écarts doivent être examinés avant raccordement au réseau de confiance.

Les appareils en fin de vie doivent être identifiés, isolés lorsque nécessaire, surveillés et remplacés selon un plan. Une appliance critique avec un firmware non maintenu peut être une dépendance centrale. Le risque ne peut pas être réduit à la présence d’un numéro de version : il faut connaître l’exposition, les privilèges, les voies de gestion et la possibilité de mise à jour ou de remplacement.

### 11.2 Mises à jour signées et retour arrière

Un firmware signé peut permettre à un appareil de vérifier qu’une mise à jour provient d’une chaîne de confiance. La vérification doit être activée et testée ; il faut comprendre comment la clé du fabricant est approuvée, comment la révocation fonctionne et comment le retour à une version antérieure est contrôlé. Une fonction de rollback non authentifiée peut réintroduire des vulnérabilités déjà corrigées.

N’installez pas un firmware trouvé sur un site tiers uniquement parce que son nom ressemble au fichier du fabricant. Obtenez la mise à jour par une source officielle, vérifiez les sommes de contrôle et signatures selon le procédé supporté, testez dans un périmètre représentatif et prévoyez un plan de secours. Pour un équipement réseau, conserver une voie de gestion hors bande peut être critique.

### 11.3 Pièces et composants contrefaits

Les achats doivent identifier les canaux autorisés, les fournisseurs de rechange et les procédures d’inspection. Les contrefaçons ou pièces non conformes peuvent affecter la sécurité, la fiabilité ou la durée de vie d’un appareil. Les éléments de traçabilité, numéros de série et documents d’origine sont utiles lors de réception et d’incidents. Les achats urgents auprès d’une source non vérifiée exigent une évaluation documentée.

## 12. Intelligence artificielle et services cloud

### 12.1 Composants d'un système IA

Un produit qui utilise un modèle d’IA peut intégrer des poids du modèle, tokenizer, bibliothèques, jeux de données, code d’entraînement, conteneurs, plugins, outils d’inférence, API tierces et éléments de configuration. La supply chain s’étend aux artefacts téléchargés, aux dépôts de modèles et aux données utilisées. Les risques comprennent les modèles falsifiés, les paquets de téléchargement malveillants, les dépendances vulnérables, les licences incompatibles et les preuves de provenance insuffisantes.

Un SBOM de logiciel classique ne décrit pas nécessairement toutes les dépendances spécifiques à l’IA. Le guide CISA et partenaires sur les éléments minimums de SBOM pour l’IA publié en 2026 complète la guidance générale et encourage la description d’éléments propres aux systèmes IA. Les équipes doivent relier les modèles, versions, sources, empreintes et conditions d’utilisation au produit déployé, et vérifier les exigences actuelles en fonction de leur architecture.

### 12.2 Services cloud et responsabilité partagée

Un service cloud peut fournir une infrastructure sécurisée mais ne gère pas toutes les configurations et identités du client. La responsabilité partagée dépend du modèle IaaS, PaaS, SaaS ou service managé. La chaîne inclut l’identité cloud, les images de base, les providers IaC, les actions CI, les registres, les clés de signature et les intégrations. Un seul jeton trop privilégié peut permettre de modifier plusieurs produits.

La stratégie doit évaluer les accès API, la résidence et la sauvegarde des artefacts, la gestion des sous-traitants, la disponibilité des journaux et la capacité d’export. La possibilité de reconstruire un service sans dépendre d’une seule personne ou d’un compte unique renforce la résilience. L’inventaire doit identifier quels composants et services sont indispensables au build et lesquels sont nécessaires au runtime.

## 13. Détecter et répondre à un incident supply chain

### 13.1 Signaux d'alerte

Les signaux peuvent inclure une nouvelle version inattendue d’une dépendance, une signature ou une provenance qui ne correspond plus, un changement de mainteneur ou de permission, un commit de workflow suspect, un jeton utilisé depuis un contexte anormal, un paquet retiré, une hausse de connexions sortantes dans le build, un changement d’empreinte d’artefact ou un avis de compromission du fournisseur. Aucun signal n’est nécessairement une preuve définitive ; il déclenche un triage proportionné.

Les journaux utiles comprennent les changements de code, approbations, événements d’identité, exécutions CI, téléchargements et publications d’artefacts, signatures, promotions, déploiements et appels de secrets. Synchronisez les horloges et conservez les données dans un espace non modifiable par l’identité mise en cause. Sans logs de build, il peut être impossible de déterminer quels artefacts ont été produits par une exécution donnée.

### 13.2 Contenir sans détruire la preuve

Lorsqu’une dépendance est soupçonnée compromise, suspendre les nouvelles publications concernées peut empêcher la propagation. Il faut identifier les commits, builds, digests, images et déploiements possiblement affectés. Préserver les attestations et logs, révoquer les identifiants compromis, mettre en quarantaine les artefacts et communiquer avec le fournisseur ou mainteneur par un canal vérifié. Le confinement ne doit pas supprimer silencieusement les preuves nécessaires à l’enquête.

~~~text
Signal de compromission
       |
       v
Suspendre / bloquer les promotions concernées
       |
       v
Préserver logs, commits, digests, attestations
       |
       v
Identifier artefacts, environnements et consommateurs
       |
       v
Révoquer secrets / corriger source / reconstruire
       |
       v
Revalider provenance, SBOM, signatures et tests
       |
       v
Redéployer, surveiller et documenter les leçons
~~~

Il est important de distinguer l’artefact compromis, l’artefact potentiellement affecté et l’artefact non concerné avec preuve. Si le système de build lui-même est compromis, une nouvelle construction sur le même environnement ne suffit pas. Il faut restaurer ou reconstruire la confiance dans l’environnement, la configuration et les identités avant de signer un nouveau produit.

### 13.3 Gestion des consommateurs en aval

Une compromission peut concerner des clients ou des équipes qui ont intégré une version. Le producteur doit savoir qui a reçu quel digest, quelle version et quelle provenance. Les notifications doivent donner l’identifiant de produit, les versions affectées, les indicateurs utiles, les actions recommandées et le canal de mise à jour, sans exposer inutilement des secrets ou les données des autres clients.

Une organisation consommatrice doit pouvoir interroger son inventaire et SBOM pour localiser les composants affectés. Les équipes doivent tester les mécanismes de notification, de retrait, de reconstruction et de retour arrière. Pour les services SaaS, la correction se fait parfois chez le fournisseur ; le client doit connaître l’état, l’impact sur ses données et les actions nécessaires sur ses intégrations.

### 13.4 Retour d'expérience

Après l’incident, analyser la cause initiale, les chemins de confiance concernés, l’efficacité des détecteurs, les délais, la qualité de l’inventaire et la capacité de retirer un artefact. Les actions doivent avoir un propriétaire, une date et une preuve. Les enseignements peuvent conduire à modifier les permissions, renforcer les règles de publication, ajouter une validation de provenance, améliorer les SBOM ou diversifier une dépendance critique.

## 14. Mesurer la maturité supply chain

### 14.1 Indicateurs opérationnels

Les métriques pertinentes incluent la proportion d’artefacts de production dotés d’un SBOM relié au digest, la proportion des releases avec provenance vérifiable, les dépôts qui appliquent des protections de branche, les jobs disposant de permissions minimales, les dépendances critiques sans propriétaire, les exceptions actives, les délais de retrait d’un artefact et la part des fournisseurs critiques évalués avec des preuves récentes.

Mesurez également la qualité : SBOM non parsables, composants sans identifiant, attestations invalides, artefacts sans source canonique, images non supportées, secrets détectés et écarts entre inventaire et runtime. Une valeur élevée de couverture peut cacher des documents incomplets. Le tableau de bord doit définir chaque indicateur, son dénominateur, sa fréquence et son propriétaire.

~~~text
Pilotage de la supply chain
  |-- composants et fournisseurs inventoriés
  |-- SBOM liés aux digests de production
  |-- releases avec provenance vérifiée
  |-- signatures conformes aux identités autorisées
  |-- dépôts et workflows protégés
  |-- secrets et permissions excessives
  |-- dépendances critiques obsolètes
  |-- délais de réaction et de reconstruction
  |-- exceptions et risques résiduels
~~~

### 14.2 Éviter les scores de conformité trompeurs

Un tableau de bord vert ne prouve pas que la chaîne est invulnérable. Il indique que les contrôles définis semblent présents selon les mesures collectées. Il faut conserver des tests de contrôle, examiner les échecs, revoir les exceptions et tester périodiquement le processus de réponse. Un test peut volontairement vérifier qu’un artefact avec provenance non conforme est refusé, ou qu’une publication par une identité non autorisée échoue dans un laboratoire.

Les objectifs doivent favoriser la résilience, pas la suppression de résultats. Si les équipes sont évaluées seulement sur le nombre de contrôles activés, elles peuvent produire des attestations sans vérifier leur usage. Mesurez plutôt la proportion de releases effectivement bloquées en cas d’échec de vérification, la capacité de retrouver tous les consommateurs d’un digest et le temps entre une alerte et le confinement.

## 15. Travaux pratiques guidés

Les travaux pratiques se font dans des dépôts et registres que vous contrôlez. Utilisez des comptes de test, des artefacts non sensibles et des clés éphémères ou dédiées. Ne tentez pas de compromettre une dépendance publique, d’injecter un paquet dans un registre tiers ou de tester des secrets d’un fournisseur réel sans autorisation.

### TP 1 — Cartographier la chaîne et le risque fournisseur

**Scénario :** l’équipe fictive KivuLab développe une application web, construit des images de conteneur, dépend de cinq paquets open source, utilise une action CI tierce, publie dans une registry et déploie sur un service cloud. Un fournisseur externe assure le support de l’identité.

**Étapes :**
1. Dessiner le graphe source, dépendances, CI, registry, signature, déploiement et fournisseur.
2. Pour chaque nœud, identifier le propriétaire, l’identité de confiance, le privilège et les données auxquelles il accède.
3. Classer les fournisseurs par impact métier, accès aux secrets, criticité, dépendance et capacité de remplacement.
4. Identifier les points de défaillance uniques et les chemins où une seule identité peut modifier puis approuver le même artefact.
5. Définir les preuves attendues du fournisseur d’identité et du service de construction.
6. Écrire un plan de traitement pour une dépendance critique sans mainteneur actif.
7. Fixer une fréquence de réévaluation et des événements qui déclenchent une mise à jour.

**Correction de référence :** la cartographie doit distinguer les composants du produit, les outils qui le construisent et les services qui le livrent. L’action tierce et le runner sont des éléments de confiance à part entière. Les fournisseurs qui peuvent atteindre les secrets ou changer une release doivent recevoir des contrôles plus forts que les services sans privilège. Pour une dépendance sans mainteneur, prévoir une migration ou un plan de continuité avec un propriétaire, et ne pas considérer sa présence dans un registre public comme une garantie.

**Livrable :** graphe annoté, matrice fournisseur, risques priorisés et plan de traitement.

### TP 2 — Générer et valider un SBOM

**Scénario :** une petite application est construite en image de conteneur. L’équipe souhaite pouvoir retrouver rapidement les versions des composants en cas d’avis de vulnérabilité. Le laboratoire dispose d’un outil compatible SPDX ou CycloneDX.

**Étapes :**
1. Construire une version identifiée de l’application et noter son digest.
2. Générer un SBOM depuis l’artefact final ou la méthode la plus proche de l’artefact effectivement livré.
3. Vérifier la présence du produit, de ses composants, versions, relations et métadonnées requises.
4. Vérifier le format et les champs contre la spécification retenue et les besoins organisationnels.
5. Lier le SBOM au digest de l’image et archiver la méthode de génération.
6. Introduire une dépendance mise à jour dans le laboratoire, reconstruire et comparer les SBOM.
7. Simuler un avis affectant une version et retrouver tous les artefacts qui la contiennent.
8. Documenter les limites, les composants non identifiés et le processus de mise à jour.

**Correction de référence :** le SBOM doit correspondre à l’artefact identifié, pas seulement à la branche source. La différence entre deux SBOM montre si le composant est apparu, a disparu ou a changé de version. Si le composant ne peut pas être identifié, le résultat est une limite de visibilité, pas une preuve qu’il est absent. Le dossier doit conserver le digest, la version du générateur, la date et le contexte de construction.

**Livrable :** SBOM validé, digest, comparaison des composants et note de qualité.

### TP 3 — Vérifier la provenance avant promotion

**Scénario :** une pipeline produit une image et publie une attestation de provenance. L’équipe de déploiement doit vérifier que le résultat vient du dépôt, du commit et du workflow attendus. Une deuxième attestation du laboratoire utilise volontairement une identité incorrecte.

**Étapes :**
1. Définir les attentes autorisées : dépôt canonique, référence source, identité du builder et artefact attendu.
2. Construire un artefact et associer un digest.
3. Générer ou récupérer l’attestation de provenance selon la plateforme de lab.
4. Vérifier signature, identité et champs de provenance selon les outils disponibles.
5. Soumettre une attestation dont l’identité ou la source ne correspond pas à la politique.
6. Confirmer que la règle refuse l’artefact non conforme et conserve un journal exploitable.
7. Documenter les exceptions possibles et leur mécanisme d’approbation.
8. Relier la vérification au déploiement pour qu’un artefact différent ne puisse pas être promu par simple changement d’étiquette.

**Correction de référence :** la présence d’une attestation ne suffit pas. La vérification compare l’identité, la source et le processus aux attentes de l’organisation. La deuxième attestation doit être rejetée si elle ne correspond pas. Le digest de l’objet vérifié doit être le même que celui déployé. Si le pipeline n’offre pas de provenance vérifiable, documenter le niveau réellement atteint et le plan d’amélioration, sans déclarer une garantie inexistante.

**Livrable :** règle d’admission, traces de validation positive et négative, digests et procédure de déploiement.

### TP 4 — Simuler une compromission de dépendance

**Scénario :** un avis confirme qu’une version fictive de la bibliothèque Kivu-Parser a été publiée avec un code malveillant. Votre inventaire permet de rechercher les composants et digest de production. Vous devez empêcher de nouvelles livraisons, identifier les usages et préparer un artefact propre.

**Étapes :**
1. Geler dans le lab la promotion des versions concernées et préserver les journaux de publication.
2. Interroger le SBOM et l’inventaire pour identifier les artefacts qui contiennent la version.
3. Vérifier les builds et déploiements qui ont utilisé la version, y compris les clones et environnements de reprise.
4. Révoquer dans le lab les identifiants de test exposés, et examiner les jobs qui avaient accès à ces secrets.
5. Remplacer la dépendance par une version approuvée ou une alternative, puis reconstruire dans un environnement digne de confiance.
6. Vérifier la provenance, le digest, le SBOM et les tests avant le redéploiement.
7. Préparer une notification pour les équipes consommatrices et une synthèse des indicateurs d’impact.
8. Écrire un retour d’expérience avec les contrôles manquants et propriétaires des actions.

**Correction de référence :** la réponse commence par empêcher de nouvelles promotions, conserver les preuves et inventorier les artefacts qui ont consommé la dépendance. Si le runner ou le processus de publication est aussi suspect, il faut restaurer la confiance dans cet environnement avant de produire un nouvel artefact. La reconstruction utilise une source approuvée et un processus contrôlé. Tous les déploiements qui exécutent l’ancien digest doivent être traités, pas seulement la branche principale.

**Livrable :** liste d’artefacts et consommateurs, chronologie, plan de correction, preuve de build propre et actions post-incident.

## 16. Exercices corrigés

### Exercice 1 — Signature et sécurité

Un artefact possède une signature valide. Peut-on conclure qu’il ne contient aucune vulnérabilité ?

**Correction :** non. La signature aide à vérifier l’intégrité et l’identité qui a signé, mais elle ne prouve pas l’absence de défaut. Il faut aussi examiner le code, les dépendances, les tests et la provenance.

### Exercice 2 — SBOM sans digest

Un SBOM répertorie tous les composants mais n’est relié à aucun artefact précis. Quelle est sa limite majeure ?

**Correction :** l’équipe ne peut pas confirmer quel build il décrit ni le relier avec certitude au logiciel déployé. Il faut associer le SBOM à une version et à un digest de l’artefact.

### Exercice 3 — Dépendance transitive

Une application ne déclare pas directement une bibliothèque vulnérable, mais une dépendance de second niveau l’utilise. L’application peut-elle être concernée ?

**Correction :** oui. Les dépendances transitives doivent être prises en compte et le chemin du composant doit être retrouvé. Il faut vérifier si la version affectée se trouve dans l’artefact et quelle action la supprime.

### Exercice 4 — Mainteneur connu

Un paquet est très populaire et provient d’un mainteneur connu. Suffit-il de lui accorder une confiance illimitée ?

**Correction :** non. La popularité est un signal d’adoption, pas une garantie d’intégrité. Les versions, signatures, provenance, politiques de publication et dépendances doivent être évaluées.

### Exercice 5 — Workflow de pull request

Un workflow exécuté pour une contribution externe reçoit le jeton de publication. Quel est le risque ?

**Correction :** le code non fiable peut potentiellement accéder au jeton ou influencer le processus de release. Il faut isoler les tests des contributions des tâches privilégiées et limiter permissions et secrets.

### Exercice 6 — Registre interne

Un registre privé met en miroir tous les paquets publics automatiquement. Quelle mesure complémentaire est utile ?

**Correction :** appliquer des namespaces et des sources approuvées, analyser les paquets entrants, conserver la provenance et limiter les droits de publication. Un registre privé peut aussi distribuer un paquet malveillant.

### Exercice 7 — Provenance présente

Une provenance décrit un dépôt, un commit et un builder. Est-elle automatiquement fiable ?

**Correction :** non. Il faut vérifier sa signature ou son authentification, l’identité du générateur, la fiabilité du builder et la correspondance aux attentes. Une provenance modifiable par le code qu’elle décrit peut être falsifiée.

### Exercice 8 — SLSA

Pourquoi préciser le track et la version de SLSA quand on annonce un niveau ?

**Correction :** les spécifications évoluent et les anciens niveaux ont changé de structure. Indiquer la version et le track rend les garanties comparables et évite de revendiquer un niveau sur la base d’une description obsolète.

### Exercice 9 — Lockfile

Le projet utilise un lockfile immuable depuis un an. Cela suffit-il à sécuriser les dépendances ?

**Correction :** non. Le verrouillage rend la résolution plus prévisible mais peut figer des versions vulnérables ou abandonnées. Il faut un processus de revue et de mise à jour, avec analyses et tests.

### Exercice 10 — Artefact promu

La recette et la production ont été construites séparément à partir du même commit. Pourquoi cela peut-il poser problème ?

**Correction :** les environnements de build, dépendances ou paramètres peuvent différer. Construire un artefact identifié, vérifier puis promouvoir le même digest réduit ces écarts.

### Exercice 11 — Questionnaire fournisseur

Un fournisseur répond oui à toutes les questions de sécurité. Peut-on fermer son évaluation ?

**Correction :** pas sans apprécier la portée et les preuves. Les réponses déclaratives doivent être vérifiées selon la criticité, notamment sur les accès, les incidents, les vulnérabilités, la provenance et la sous-traitance.

### Exercice 12 — Fournisseur SaaS

Le fournisseur corrige son logiciel, mais votre intégration utilise un jeton admin permanent. Le problème supply chain est-il entièrement traité ?

**Correction :** non. Le client reste responsable des identités, permissions et intégrations qu’il maîtrise. Il faut limiter le jeton, définir une rotation et vérifier les accès après incident.

### Exercice 13 — Dépendance sans mainteneur

Une bibliothèque importante n’a plus de mainteneur actif mais aucune vulnérabilité connue. Quel est le risque ?

**Correction :** risque de continuité et de délai de correction futur, plus difficulté à vérifier les évolutions. Il faut planifier une migration, un remplacement ou un fork gouverné selon l’impact, sans attendre nécessairement une faille.

### Exercice 14 — Firmware signé

Un fabricant publie un firmware signé. Que faut-il encore vérifier avant installation ?

**Correction :** l’origine officielle, le modèle et la version matérielle, la signature et la méthode de vérification, les notes de version, les prérequis, le test et le plan de retour arrière. La signature ne prouve pas que la mise à jour ne provoquera pas de régression.

### Exercice 15 — SBOM d’IA

Un logiciel utilise un modèle téléchargé et plusieurs bibliothèques. Un SBOM de paquets classiques peut-il couvrir tous les éléments importants ?

**Correction :** pas nécessairement. Il faut examiner les besoins spécifiques aux modèles, aux données, aux versions, aux empreintes et aux services d’inférence, puis compléter l’inventaire selon l’architecture et la guidance pertinente.

### Exercice 16 — Runner compromis

Une dépendance malveillante a été détectée dans un runner et le build a utilisé des secrets de publication. Que faire en priorité ?

**Correction :** suspendre les releases concernées, préserver les logs et artefacts, révoquer les secrets accessibles, reconstruire ou restaurer l’environnement de build, identifier les produits diffusés puis rétablir la chaîne de confiance avant de signer de nouveaux artefacts.

### Exercice 17 — Hash différent

Le digest téléchargé ne correspond pas au digest attendu, alors que le nom et la version sont identiques. Peut-on le déployer ?

**Correction :** non, pas sans investigation. Le digest définit le contenu exact. Vérifier la source, la publication et la provenance, et bloquer l’artefact tant que l’écart n’est pas expliqué.

### Exercice 18 — Score OpenSSF

Une dépendance obtient un bon score automatique de bonnes pratiques. Est-ce une garantie d’absence de compromission ?

**Correction :** non. Les scores donnent des indicateurs sur certaines pratiques observables. Ils ne garantissent pas que le code soit exempt de vulnérabilité ou qu’une publication précise soit légitime.

### Exercice 19 — Signature non conforme

La signature est valide mais son identité ne correspond pas au dépôt autorisé. Que doit faire la politique d’admission ?

**Correction :** rejeter l’artefact ou le placer dans une voie d’investigation contrôlée. La validité cryptographique ne suffit pas : la politique doit vérifier que le signataire et la source sont attendus.

### Exercice 20 — Incident après correction

Une version malveillante a été retirée et une nouvelle version publiée. Peut-on considérer l’incident terminé ?

**Correction :** seulement après avoir identifié les artefacts et consommateurs affectés, redéployé les versions propres, examiné les possibles compromissions et conservé la preuve. Il faut aussi fermer les causes systémiques et suivre les actions post-incident.

## 17. Défi final — Établir une chaîne logicielle vérifiable

**Scénario :** KivuLab fournit un service de gestion réseau. Le code est stocké dans un dépôt Git, construit par une pipeline CI, utilise des paquets open source, est publié en image de conteneur signée et déployé dans le cloud. Une dépendance de build a été mise à jour automatiquement, une action CI est référencée par une étiquette mouvante, le SBOM n’est pas lié au digest final, et la production accepte tout artefact provenant de la registry interne. Un fournisseur SaaS conserve des accès de support privilégiés sans revue récente.

Les identifiants sont fictifs. L’exercice se déroule sur une architecture de laboratoire ; aucune action sur un système tiers n’est requise.

### Livrables obligatoires

1. **Graphe de confiance :** représenter le dépôt, les identités, dépendances, runners, registry, signatures, provenance et production.
2. **Analyse des menaces :** expliquer au moins cinq chemins d’attaque, leur précondition, l’actif visé et le contrôle qui les réduit.
3. **Protection du dépôt et de CI/CD :** limiter permissions, secrets, actions tierces et runners ; préciser les revues exigées pour les fichiers sensibles.
4. **SBOM :** générer un document lié au digest exact, valider les champs, identifier les composants et indiquer les limites connues.
5. **Provenance et SLSA :** proposer un niveau d’amélioration réaliste, définir les attentes de build et la vérification indépendante.
6. **Politique d’admission :** refuser les artefacts dont le digest, la provenance ou l’identité signataire ne correspond pas aux règles.
7. **Fournisseur SaaS :** construire un plan de vérification, réduire les accès privilégiés et intégrer notification et sous-traitance.
8. **Réponse incident :** décrire la suspension des releases, la recherche des artefacts, la rotation des secrets et la restauration de la confiance.
9. **Indicateurs :** mesurer la couverture SBOM, les provenances vérifiées, les écarts d’identité et le délai de reconstruction fiable.

### Correction de référence

L’analyse doit commencer par le graphe de confiance. Les fichiers de pipeline et les dépendances sont des entrées du processus de build, tandis que le runner, la registry et l’identité de publication peuvent avoir des privilèges élevés. Une action CI à référence mouvante doit être épinglée à une référence approuvée avec un processus de mise à jour. Les contributions non fiables ne doivent pas accéder aux secrets de release. Les permissions de jeton et de compte doivent être limitées et revues.

Le build doit produire un artefact identifié par digest, un SBOM qui décrit sa composition et une provenance générée par une plateforme dont l’intégrité est protégée. Les contrôles de qualité, vulnérabilité et licence doivent être liés à la même version. Le vérificateur d’admission compare l’artefact à l’identité et au processus attendus ; il refuse une signature ou une provenance simplement « valide » si la source ou l’identité n’est pas autorisée. Une exception éventuelle est limitée, approuvée, datée et surveillée.

Le niveau SLSA choisi doit être revendiqué seulement si les exigences correspondantes sont satisfaites dans la version applicable. Un premier objectif réaliste est la génération d’une provenance vérifiable liée au digest et l’application de la vérification par le consommateur. Ensuite, renforcer l’isolation des builds, empêcher un job de contrôler les éléments de provenance, et réduire l’accès des secrets au processus de build. Un niveau annoncé doit être appuyé par des preuves, pas une simple configuration déclarative.

Pour le fournisseur SaaS, identifier les opérations de support, les rôles, les journaux, les sous-traitants, les délais de notification, la capacité à révoquer l’accès et le plan de sortie. Limiter les comptes permanents, utiliser des accès temporaires et supervisés lorsque c’est disponible, et tester la révocation. La responsabilité partagée doit être documentée.

Lors d’un incident, bloquer les nouvelles promotions, préserver les journaux, identifier les digests construits pendant la période suspecte, révoquer les secrets exposés, reconstruire depuis une source approuvée et un environnement rétabli, valider à nouveau les SBOM, signatures et attestations, puis déployer le digest propre. Vérifier les consommateurs et environnements de reprise. Le retour d’expérience doit modifier les contrôles qui ont permis l’incident.

### Barème sur 100 points

- Graphe de confiance et identification des actifs/identités : 10 points.
- Analyse de menaces et contrôles associés : 15 points.
- Protection des dépôts, secrets et CI/CD : 15 points.
- SBOM associé au digest et vérification de la composition : 10 points.
- Provenance, signatures et attentes SLSA justifiées : 15 points.
- Politique d’admission et gestion des exceptions : 10 points.
- Évaluation et contrôle du fournisseur SaaS : 10 points.
- Plan de réponse et restauration de la confiance : 10 points.
- Indicateurs et gouvernance du programme : 5 points.

La solution ne peut obtenir la totalité des points si elle se contente de signer l’image sans vérifier l’identité source, de générer un SBOM non relié au produit livré ou de donner à tous les jobs un accès permanent aux secrets.

## 18. Checklist opérationnelle

Avant de considérer la supply chain comme maîtrisée, vérifier les points suivants :

- Les actifs, fournisseurs, composants et sous-traitants critiques sont inventoriés avec un propriétaire.
- Les relations de confiance et les identités capables de modifier le code, le build, la signature et le déploiement sont documentées.
- Les comptes utilisent une authentification forte et les permissions sont minimales et révisées.
- Les modifications de dépôt, de dépendances et de workflow passent par une revue adaptée.
- Les tests de contributions non fiables n’accèdent pas aux secrets de publication.
- Les runners sont isolés et reconstruits ou nettoyés selon une politique explicite.
- Les actions, images et dépendances utilisent des références contrôlées, mises à jour après revue.
- Les registres et miroirs ont une politique de publication, d’accès, de provenance et de retrait.
- Les SBOM sont générés pour les artefacts concernés, validés et reliés à un digest exact.
- La provenance est générée et vérifiée selon des attentes explicites ; les niveaux SLSA sont revendiqués uniquement si démontrés.
- Les signatures sont vérifiées avec des identités attendues, pas seulement avec un constat cryptographique.
- Les artefacts promus en production sont les mêmes que ceux vérifiés ou sont revalidés après reconstruction.
- Les fournisseurs critiques fournissent des preuves et des engagements vérifiables en matière de vulnérabilité, incident et support.
- Les composants hors support et mainteneurs uniques ont un plan de traitement ou de sortie.
- Un incident supply chain peut être contenu, ses artefacts localisés et les consommateurs identifiés.
- Les secrets accessibles aux builds suspects peuvent être révoqués et remplacés.
- Les mesures de performance incluent la traçabilité et les résultats de vérification, pas seulement le volume de contrôles configurés.

## 19. Glossaire

**Attestation** : déclaration structurée sur un artefact ou un processus, vérifiable selon une identité et une politique de confiance.

**Build** : processus qui transforme une source et ses entrées en artefact logiciel.

**Chaîne de provenance** : éléments qui permettent de relier un artefact à sa source, son processus de construction et son identité de production.

**Composant transitif** : dépendance qui est introduite par une autre dépendance plutôt que déclarée directement par le projet principal.

**Digest** : empreinte cryptographique utilisée pour identifier le contenu précis d’un objet.

**Dépendance confusion** : situation dans laquelle le processus de résolution choisit un paquet issu d’une source inattendue ou non approuvée.

**Épinglage** : référence explicite et stable à une version, un commit ou un digest approuvé.

**Firmware** : logiciel embarqué qui contrôle le fonctionnement d’un équipement matériel.

**In-toto** : modèle et formats d’attestation destinés à décrire et vérifier des étapes d’une chaîne d’approvisionnement logicielle.

**OpenSSF Scorecard** : projet qui automatise certaines vérifications de pratiques de sécurité de projets open source.

**Provenance** : déclaration décrivant comment un artefact a été produit et quelles entrées ou plateformes l’ont généré.

**Registry / registre** : service qui stocke et distribue des paquets, images ou autres artefacts.

**SBOM** : inventaire formel des composants logiciels liés à un produit ou artefact.

**SLSA** : cadre de niveaux et exigences visant à renforcer les garanties de la supply chain logicielle.

**SPDX** : spécification ouverte pour représenter notamment des informations de composants, de licences et de relations logicielles.

**CycloneDX** : standard de nomenclature pouvant représenter composants, dépendances, services et informations connexes.

**Runner** : environnement d’exécution d’un job d’intégration ou de livraison continue.

**Typosquatting** : publication ou utilisation d’un nom ressemblant à celui d’un composant légitime pour induire une confusion.

**VEX** : échange structuré d’informations sur l’état d’applicabilité d’une vulnérabilité à un produit, avec un statut et une justification.

**SBOM de production** : SBOM associé à l’artefact réellement déployé et maintenu dans l’inventaire d’exploitation.

**Rayon d’impact** : ensemble des actifs, services ou clients affectés par la compromission d’un composant commun.

## 20. Références officielles

- NIST SP 800-161 Rev. 1, Update 1 — Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations : https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final
- NIST SP 800-218 — Secure Software Development Framework (SSDF) Version 1.1 : https://csrc.nist.gov/pubs/sp/800/218/final
- NIST SSDF Project — publications et profils complémentaires : https://csrc.nist.gov/projects/ssdf
- CISA et partenaires — 2026 Minimum Elements for a Software Bill of Materials : https://content.govdelivery.com/accounts/USDHSCISA/bulletins/422a7eb
- CISA — page sur le SBOM : https://www.cisa.gov/sbom
- SLSA — spécification officielle, version courante : https://slsa.dev/spec/v1.2/
- SLSA — Build Track Basics : https://slsa.dev/spec/v1.2/build-track-basics
- SPDX — spécifications officielles : https://spdx.dev/use/specifications/
- CycloneDX — aperçu officiel de la spécification : https://cyclonedx.org/specification/overview/
- OpenSSF Scorecard — projet et contrôles automatisés : https://openssf.org/scorecard/
- Sigstore — documentation de signature et de vérification : https://docs.sigstore.dev/
- in-toto — framework de chaîne d’approvisionnement : https://in-toto.io/

Les spécifications et recommandations évoluent. Les pages officielles doivent être consultées au moment d’implémenter un contrôle, notamment pour les versions des formats SBOM, les exigences de provenance et les champs minimaux applicables. Une norme décrit un cadre ; elle ne prouve pas que l’implémentation locale satisfait chaque exigence.

## Schéma complémentaire A — La chaîne de preuves

~~~text
Source contrôlée
   |
   v
Build autorisé
   |
   +--> SBOM associé au digest
   +--> provenance générée par le builder
   +--> signature / attestation
   |
   v
Vérification des attentes
   |
   v
Promotion du digest vérifié
~~~

Cette chaîne sert de fil conducteur lorsqu’une équipe doit expliquer pourquoi elle a confiance dans un artefact. Chaque preuve doit faire référence au bon produit et au bon identifiant. Un document valide mais rattaché à un autre build n’est pas une preuve suffisante.

## Schéma complémentaire B — Frontières de privilèges du pipeline

~~~text
Contribution externe
   |
   v
Job isolé sans secrets
   |
   v
Revue et merge approuvés
   |
   v
Build privilégié isolé
   |
   v
Identité de publication limitée
   |
   v
Promotion contrôlée
~~~

Le contrôle est efficace si aucun chemin indirect ne permet au job non fiable de réutiliser un cache, un fichier ou une identité privilégiée. Il faut examiner les transferts d’artefacts entre jobs, les permissions du token et la persistance du runner.

## Schéma complémentaire C — Gestion de version d'une dépendance

~~~text
Avis amont / nouvelle version
          |
          v
Vérifier source, mainteneur, hash et avis
          |
          v
Mettre à jour manifestes et lockfile
          |
          v
Scan + tests + revue
          |
          v
Build et SBOM mis à jour
          |
          v
Promotion et inventaire du digest
~~~

Le verrouillage stabilise les entrées, mais le processus de maintenance doit continuer. Une mise à jour urgente doit suivre une voie accélérée contrôlée, pas une voie sans revue ni preuve.

## Schéma complémentaire D — Évaluer un fournisseur

~~~text
Criticité métier
     |
     v
Données et privilèges
     |
     v
Preuves de contrôle et de provenance
     |
     v
Contrat, notification, support, sous-traitants
     |
     v
Décision, actions et réévaluation
~~~

Un questionnaire est seulement le début de l’évaluation. Les preuves doivent préciser le périmètre, la date, les exceptions et les systèmes réellement couverts. Les fournisseurs critiques doivent avoir des responsabilités et des voies d’escalade explicites.

## Schéma complémentaire E — Incident de dépendance

~~~text
Alerte fournisseur / paquet suspect
           |
           v
Blocage des promotions
           |
           v
Recherche des digests consommateurs
           |
           v
Préservation des logs et attestations
           |
           v
Correction des entrées + build fiable
           |
           v
Vérifier puis redéployer
           |
           v
Retour d'expérience et actions préventives
~~~

L’objectif est de limiter la propagation tout en préservant les éléments nécessaires à l’analyse. Si le builder est suspect, la confiance dans sa nouvelle production doit être restaurée avant de signer les artefacts suivants.

## Schéma complémentaire F — Contrôles de déploiement

~~~text
Artefact proposé
     |
     v
Digest attendu ?
     |
     v
Signature et identité conformes ?
     |
     v
Provenance conforme au dépôt et au builder ?
     |
     v
SBOM et contrôles requis présents ?
     |
     +--> Oui : admission et journalisation
     |
     +--> Non : refus ou exception approuvée
~~~

La politique d’admission doit être testée avec des cas positifs et négatifs. Les logs doivent permettre d’expliquer quel contrôle a refusé le déploiement sans dévoiler de secrets.


## Conclusion

La sécurité de la supply chain repose sur la réduction de la confiance implicite et la capacité à expliquer d’où vient chaque artefact, comment il a été construit, quels composants il contient, qui l’a autorisé et où il est déployé. Les SBOM, signatures, digests, attestations et niveaux SLSA offrent des garanties différentes et complémentaires. Ils doivent être intégrés à un processus qui protège les dépôts, les identités, les runners, les registres, les clés et la promotion en production.

La gouvernance des fournisseurs, la gestion des dépendances, les exigences de contrat, le suivi des versions et la réponse aux incidents apportent les éléments organisationnels nécessaires. Le résultat attendu n’est pas un tableau de bord artificiellement vert : c’est une chaîne observable, vérifiable, résiliente et capable de bloquer une release non conforme puis de reconstruire une version de confiance.

Fin du cours.