# DevSecOps

> **Mise en contexte**

Une équipe publie une nouvelle version chaque semaine. Les tests passent et le déploiement paraît réussi, pourtant un jeton a été écrit dans les journaux, une dépendance vulnérable a été incluse et un workflow permet à une branche non approuvée de demander des droits de production. Le logiciel fonctionne, mais la chaîne qui le fabrique constitue elle-même une surface d’attaque. Une compromission de la chaîne peut contourner de nombreux contrôles placés uniquement dans l’application.

Le DevSecOps intègre la sécurité à la conception, au développement, à la construction, à la livraison et à l’exploitation. Il ne se résume ni à ajouter un scanner partout, ni à ralentir chaque livraison par une approbation manuelle. Le but est de rendre les contrôles reproductibles, compréhensibles et proportionnés au risque, tout en conservant la capacité de livrer fréquemment.

Ce cours approfondit le modèle de menace CI/CD, la gouvernance du code, les permissions des workflows, les identités temporaires, l’isolation des runners, les analyses SAST/SCA/DAST, les secrets, l’infrastructure as code, les SBOM, la provenance, les signatures, les politiques de déploiement et la réponse aux incidents. Les exemples sont pédagogiques et doivent être adaptés à la plateforme et à la politique de l’organisation.

## 1. Objectifs et vocabulaire opérationnel

À la fin du cours, vous devrez pouvoir dessiner un pipeline, identifier ses actifs sensibles et ses frontières de confiance, distinguer les catégories d’analyse, définir des règles de blocage justifiées, réduire les permissions des jobs, vérifier l’origine d’un artefact et retrouver les services affectés par une vulnérabilité nouvellement découverte.

La CI, ou intégration continue, automatise la compilation, les tests et les autres contrôles répétables à chaque changement. La livraison continue prépare régulièrement une version prête à être publiée. Le déploiement continu automatise également la mise en production lorsque les conditions prévues sont satisfaites. DevSecOps reprend ces pratiques et fait de la sécurité une responsabilité partagée : les développeurs comprennent les risques de leur code, la plateforme fournit des chemins sûrs, la sécurité aide à définir les politiques et l’exploitation alimente le processus par les retours de production.

Trois propriétés structurent le travail. La confidentialité exige que les secrets, les données de test et le code privé ne soient accessibles qu’aux composants autorisés. L’intégrité exige de savoir quels composants ont été construits, quels contrôles ont réussi et si l’artefact déployé correspond à celui qui a été vérifié. La disponibilité exige que la chaîne résiste aux abus, à l’épuisement de ressources et aux pannes de services essentiels. Un jeton cloud divulgué peut compromettre les trois propriétés : révéler des données, modifier l’infrastructure et interrompre des services.

~~~text
                 DEVSECOPS : RESPONSABILITÉ PARTAGÉE
+---------------------+   +----------------------+   +----------------------+
| Développement       |<->| Plateforme / Ops     |<->| Sécurité             |
| Code et corrections |   | CI, build, release   |   | Risques et politiques|
+---------------------+   +----------------------+   +----------------------+
            \                     |                         /
             \                    |                        /
              +-------------------+-----------------------+
                                  |
                       Livraison vérifiable
                                  |
                        Produit maintenable
~~~

L’objectif n’est pas d’atteindre une sécurité abstraite et absolue. Il est de rendre le risque visible, de réduire les chemins d’attaque les plus probables, de détecter les échecs et d’organiser la correction. La sécurité est un processus de décision documenté, soutenu par des contrôles techniques et une capacité de réponse.

## 2. Cartographier le pipeline et ses menaces

Un pipeline est un système distribué. Ses composants incluent le dépôt source, les branches et pull requests, l’orchestrateur CI, les runners, les actions ou plugins, les gestionnaires de paquets, les caches, les secrets, l’identité cloud, les registres d’artefacts, les environnements de test, le cluster et les journaux. Une cartographie limitée au fichier YAML oublie souvent les permissions de la machine, les accès réseau et les composants téléchargés à l’exécution.

Les menaces fréquentes comprennent l’exécution de code non fiable dans un runner privilégié, l’exfiltration de secrets, le remplacement d’une action externe, l’empoisonnement d’un cache, la dépendance compromise, la substitution d’un artefact, l’abus d’un jeton de publication, le contournement des approbations et la modification discrète d’un workflow. Les risques de configuration comprennent les runners persistants partagés, les permissions globales excessives, les environnements sans contrôle et les journaux qui divulguent des variables.

~~~text
Entrée non fiable
       |
       v
[Pull request] --> [Runner CI] --> [Artefact] --> [Registre]
                       |                 |              |
                       v                 v              v
                    [Secrets]        [Signature]   [Déploiement]
                       |                 |              |
                       +-----------------+--------------+
                                         |
                               [Identité de production]
~~~

Inventoriez les actifs et leur valeur. Pour chaque actif, demandez qui peut le lire, l’écrire, l’exécuter ou le remplacer. Définissez les frontières de confiance : une pull request venant d’un fork n’est pas équivalente à un commit fusionné sur une branche protégée ; un test est différent d’un job de publication ; un registre de test n’est pas le registre de production.

Un modèle de menace exploitable peut être une table avec l’actif, la menace, la précondition, l’impact, la prévention, la détection, le propriétaire et le risque résiduel. Actualisez-le lors de l’ajout d’un runner, d’un rôle cloud, d’une action externe ou d’un chemin de déploiement. L’exercice utile consiste à identifier les transferts de données et de privilèges qui pourraient transformer un défaut mineur en compromission globale.

~~~text
Actif          Menace                  Contrôle prioritaire
-------------  ----------------------  -----------------------------------
Jeton cloud    Vol ou réutilisation     OIDC et rôle minimal
Runner         Persistance d'attaque    Isolation et environnement éphémère
Dépendance     Version compromise       Verrouillage, SCA et revue
Image          Substitution             Digest, signature et provenance
Production     Déploiement non autorisé Environnement protégé
Logs           Fuite de secret           Minimisation et accès contrôlé
~~~

Examinez les liens autant que les composants. Une signature n’a de valeur que si l’identité de signature est protégée. Une branche protégée ne suffit pas si un autre événement permet à du code non fiable d’obtenir des secrets. Une SBOM est peu utile si elle n’est pas liée à l’artefact exécuté. Les contrôles doivent former une chaîne de preuves cohérente.

## 3. Gouvernance du développement sécurisé

Le NIST Secure Software Development Framework (SSDF) donne un cadre de pratiques pour réduire le risque de vulnérabilités. NIST SP 800-204D traite de l’intégration de la sécurité de la supply chain dans les pipelines CI/CD. Ces références aident à structurer un programme, mais il ne suffit pas de cocher des cases : chaque contrôle doit être lié à un risque, une preuve et une responsabilité.

L’équipe produit répond du comportement attendu, de la maintenance du code et de la correction des défauts. La plateforme construit des workflows et environnements communs, maintenus et limités. La sécurité aide pour les modèles de menace, les politiques et les cas complexes. L’exploitation détecte les comportements anormaux et communique les contraintes de production. Les rôles varient selon l’organisation ; l’important est qu’aucune anomalie ne soit abandonnée parce qu’elle touche plusieurs équipes.

~~~text
Conception et exigences
        |
        v
Développement + tests + analyse locale
        |
        v
Pull request + revue + contrôles automatisés
        |
        v
Construction isolée + SBOM + provenance
        |
        v
Signature / vérification / décision de promotion
        |
        v
Déploiement contrôlé + observabilité
        |
        +------> Retours de production vers tests et règles
~~~

Les exigences doivent être compréhensibles. Pour une API exposée qui traite des données sensibles, l’organisation peut exiger une analyse des dépendances, des secrets, d’IaC et de l’image. Pour un prototype interne, certaines étapes lourdes peuvent être adaptées, mais la fuite d’un secret ou l’accès non autorisé à un environnement réel ne doit pas être banalisé. Le niveau de contrôle doit être justifié par le risque.

Prévoyez une gestion des exceptions. Toute exception indique l’actif, le risque, le périmètre, les mesures compensatoires, le propriétaire, l’approbateur, la date de révision et les critères de sortie. Une exception permanente sans justification se transforme en défaut de politique. Les exceptions critiques doivent être rares et visibles dans les revues.

## 4. Protéger le dépôt, les branches et les revues

Le dépôt source est un actif privilégié : la personne qui peut modifier un workflow peut parfois changer les contrôles, accéder à des identifiants ou influencer les artefacts. Protégez les branches principales, exigez une revue adaptée, rendez les contrôles obligatoires et interdisez les poussées directes lorsque c’est approprié. Les fichiers de workflows, d’infrastructure et de politique sont sensibles et doivent être examinés par des personnes capables d’évaluer leur impact.

Les approbations doivent porter sur le contenu effectivement fusionné. Si le code ou les fichiers sensibles changent après les contrôles, exigez de nouveaux contrôles. Une validation ancienne ne prouve rien sur un commit différent. Les statuts requis doivent être précis et ne pas pouvoir être neutralisés par la modification du même code qu’ils sont censés contrôler.

~~~text
BRANCHE CIBLE PROTÉGÉE
+------------------------------------------+
| Revue obligatoire                        |
| Tests attendus                           |
| Analyses de sécurité exigées             |
| Contrôles à jour sur le commit fusionné  |
| Dérogations visibles et traçables        |
+------------------------------------------+
                   |
                   v
          Fusion autorisée ou bloquée
~~~

Les contributions venant de forks sont des entrées non fiables. Exécutez leurs tests sans secrets de production et avec des permissions minimales. Séparez la validation du code proposé de la publication de l’artefact. La publication devrait intervenir depuis un contexte approuvé, lié à une branche ou une version protégée, et recevoir uniquement les droits nécessaires.

Une revue humaine doit examiner le changement de comportement, les dépendances, les nouveaux accès, la modification des tests et la raison des exceptions. Les tests automatisés détectent certaines faiblesses connues ; les reviewers évaluent les intentions et les scénarios qui ne sont pas encodés dans les règles. Ces contrôles sont complémentaires.

## 5. Sécuriser les workflows et les actions externes

Les workflows exécutent des scripts, installent des paquets, accèdent aux environnements et obtiennent des jetons. Examinez les actions ou plugins externes comme des dépendances exécutables. Étudiez leur source, les données transmises, les permissions, la maintenance et les comportements de publication. N’installez pas un composant uniquement parce qu’il est populaire.

Lorsque la plateforme le permet, référencez une action par un SHA de commit complet plutôt qu’un tag mutable. Une référence immuable réduit le risque qu’un tag soit déplacé vers un autre code, mais ne prouve pas que ce code est sûr. Surveillez les mises à jour, examinez les changements et mettez à niveau les références vulnérables. Limitez le nombre d’actions externes.

Déclarez explicitement les permissions de chaque job. Un test unitaire a généralement besoin d’une lecture du dépôt, pas du droit de publier des paquets ou de modifier la production. Évitez de donner à chaque étape le même jeton étendu. Séparez les jobs de vérification, de publication et de déploiement si cela réduit les privilèges.

~~~text
CONTRIBUTION NON FIABLE
       |
       v
[Job de test : lecture seule, aucun secret de production]
       |
       v
Résultats de tests et artefacts temporaires
       |
       | fusion approuvée et contrôles réussis
       v
[Job de publication avec droits ciblés]
       |
       v
[Déploiement dans un environnement protégé]
~~~

Un risque majeur est l’injection de commandes. Un nom de branche, un titre de pull request, un commentaire ou un champ utilisateur peut contenir des caractères interprétés par un shell si la valeur est insérée directement dans une commande. Traitez toute donnée d’événement comme non fiable. Préférez les variables d’environnement, les arguments distincts et la validation stricte du format. Évitez les interprétations secondaires par un autre shell ou moteur de template.

Un modèle prudent transmet une chaîne contrôlée par un utilisateur dans une variable d’environnement dédiée, puis la traite comme du texte ; il évite de construire un script autour de cette chaîne. La protection exacte dépend du shell et de la plateforme. Il faut également éviter de réinjecter la valeur dans une autre commande et tester les entrées contenant espaces, guillemets, caractères spéciaux et retours à la ligne.

Comprenez les événements précis du fournisseur CI. Selon l’événement, le code exécuté peut venir de la branche proposée ou de la branche cible, et les secrets disponibles peuvent différer. Ne changez pas de déclencheur pour contourner un secret inaccessible. Testez une pull request de fork, une branche non protégée, un test en échec et une tentative de publication non autorisée.

## 6. Identités, jetons et secrets

Un secret est une capacité d’accès, pas seulement une valeur de configuration. Un jeton long terme à privilèges administratifs reste dangereux même s’il est chiffré au repos : le pipeline doit l’utiliser, et une étape compromise peut le récupérer. Préférez des identités fédérées et des jetons de courte durée lorsque cela est possible. Limitez leur portée à une ressource, une action et un environnement.

Avec OIDC, un workflow prouve son identité auprès d’un fournisseur qui peut émettre ou autoriser une session selon des conditions de confiance. Cela peut éviter de conserver une clé cloud durable dans le dépôt. Toutefois, limitez l’émetteur, l’audience, le dépôt, la branche, l’environnement et les permissions du rôle. Une politique trop large pourrait permettre à un autre workflow d’obtenir la même identité.

~~~text
Workflow approuvé
       |
       | preuve OIDC : identité, branche, environnement, audience
       v
Fournisseur d'identité
       |
       | conditions de confiance validées
       v
Rôle cloud à privilèges limités
       |
       | jeton temporaire
       v
Action autorisée
~~~

Stockez les secrets dans le gestionnaire prévu, accordez les accès au niveau le plus étroit et révoquez ou remplacez les valeurs après une exposition présumée. Un secret de production ne doit pas être accessible à toutes les branches. Le droit d’utiliser un secret peut être aussi important que le droit de le lire. Enregistrez qui peut le créer, l’utiliser, le renouveler et le révoquer.

Le masquage automatique dans les logs n’est pas une garantie absolue. Une valeur encodée, fragmentée ou transformée peut ne pas être reconnue comme le secret d’origine. Ne testez jamais le masquage en affichant une vraie clé. Évitez la sortie complète de variables d’environnement, désactivez le traçage excessif et ne journalisez que les informations utiles.

N’intégrez pas les secrets au dépôt, aux couches de conteneur, au cache ou aux artefacts. Pendant la construction, utilisez un mécanisme dédié afin que la valeur ne persiste pas dans les couches finales. Si une clé a été exposée, retirez les copies pour limiter la propagation, mais priorisez la révocation : supprimer le texte du dernier commit ne neutralise pas les copies existantes.

~~~text
Alerte de fuite
      |
      v
Identifier la portée et le propriétaire
      |
      v
Révoquer / remplacer le secret
      |
      v
Examiner journaux et usages possibles
      |
      v
Nettoyer les copies et corriger la cause
      |
      v
Tester le contrôle préventif
~~~

La procédure d’incident doit indiquer qui peut suspendre les publications, révoquer les identités et examiner les accès. Recherchez les usages anormaux, identifiez les artefacts et environnements concernés, puis vérifiez les permissions qui ont permis l’exposition. Le secret compromis est à traiter comme un incident potentiel, même si aucun usage malveillant n’est visible immédiatement.

## 7. Runners, caches et environnements de construction

Un runner exécute le code de la chaîne. Un runner compromis peut lire des jetons accessibles, modifier un artefact, exfiltrer des fichiers ou empoisonner un cache. Sécurisez-le en fonction de la confiance du code exécuté. Favorisez l’isolation des jobs, des images de base maintenues, un environnement éphémère ou réinitialisé et des permissions système minimales.

Évitez qu’un runner autohébergé permanent exécute indistinctement des contributions externes et des déploiements privilégiés. Séparez les pools par niveau de confiance. N’exposez pas inutilement le socket du moteur de conteneurs, les métadonnées cloud, le réseau interne ni les identifiants d’autres projets. Restreignez les sorties réseau et surveillez les connexions inattendues.

~~~text
POOL A : CODE NON FIABLE
- Aucun secret de production
- Réseau contrôlé
- Permissions de lecture
- État éphémère ou réinitialisé

POOL B : CONSTRUCTION APPROUVÉE
- Dépendances verrouillées
- Sorties traçables
- Droits limités au registre de test

POOL C : DÉPLOIEMENT
- Déclencheur protégé
- Identité temporaire
- Approbation selon la politique
- Journaux d'audit
~~~

Les caches accélèrent les builds mais peuvent transférer des fichiers entre jobs. Leurs clés et leur portée doivent empêcher un job non fiable d’écrire des exécutables ensuite consommés par un job privilégié. Vérifiez les artefacts importés ou reconstruisez-les lorsque nécessaire. Ne sauvegardez pas des fichiers contenant des secrets, jetons ou configurations sensibles.

L’image du runner est une dépendance. Réduisez les logiciels préinstallés, appliquez les mises à jour, inventoriez les outils et retirez ceux qui ne servent plus. Les environnements de construction ne doivent pas recevoir l’accès au cluster de production par défaut. Le moindre privilège concerne aussi le réseau : si un test n’a pas besoin de joindre une base réelle, cette route ne devrait pas lui être accessible.

## 8. SAST : analyser le code statiquement

L’analyse statique, ou SAST, recherche dans le code ou sa représentation des motifs associés à des vulnérabilités. Elle peut détecter des entrées non validées, des requêtes construites de façon dangereuse, certaines erreurs d’authentification, des usages cryptographiques inadaptés et des configurations risquées. La couverture varie selon le langage, les règles et la capacité à suivre les données.

Un finding est un signal à examiner. Vérifiez la source de l’entrée, son contrôle éventuel par un utilisateur, le chemin de données, le contexte d’exécution et les protections existantes. Un faux positif doit être caractérisé et justifié plutôt que simplement ignoré. Une analyse sans résultat ne prouve pas l’absence de faille : le code peut être hors couverture, la règle absente ou le défaut invisible à l’outil.

~~~text
Code source
    |
    v
[SAST sur la pull request]
    |                  \
    | findings          \ aucun finding
    v                    v
[Triage et correction] [Poursuite des contrôles]
    |                          |
    v                          v
[Test de non-régression] [Analyse complète selon le risque]
~~~

L’analyse est plus utile lorsqu’elle se produit près du changement. Des retours rapides aident le développeur à comprendre le contexte. Une analyse plus complète peut être exécutée dans un job séparé. La politique précise les catégories bloquantes, la gestion des exceptions et la façon de lier un résultat à la correction.

SAST ne remplace pas les tests fonctionnels, les tests d’intégration ou les tests dynamiques. Les tests fonctionnels valident les comportements attendus ; SAST examine certaines constructions du code ; DAST observe l’application active. Une application peut réussir ses tests fonctionnels tout en contenant un défaut d’autorisation, ou présenter un finding statique non exploitable dans la configuration déployée.

## 9. SCA : composants et dépendances

L’analyse de composition logicielle, ou SCA, identifie bibliothèques, paquets et dépendances transitives pour les comparer aux avis de vulnérabilité, aux règles de licence et parfois aux signaux de maintenance. Une dépendance transitive est incluse parce qu’un autre paquet l’utilise. Elle peut donc faire partie du logiciel livré sans apparaître directement dans le manifeste principal.

Un fichier de verrouillage stabilise les versions et favorise des constructions répétables. Il ne prouve pas qu’une version est sûre. L’équipe doit surveiller les vulnérabilités, mettre à jour les paquets, tester la compatibilité et éviter les versions flottantes en production. Une mise à jour aveugle sans test peut corriger un risque tout en provoquant une régression.

~~~text
Application
   |
   +-- Bibliothèque A
   |       |
   |       +-- Bibliothèque C  <--- vulnérabilité connue
   |
   +-- Bibliothèque B
           |
           +-- Bibliothèque D

L'inventaire couvre les dépendances transitives et relie
leurs versions aux artefacts livrés.
~~~

Un finding doit être évalué selon la version, le code vulnérable, l’exposition, les privilèges et le correctif disponible. L’absence d’appel connu peut réduire la priorité, mais ne constitue pas une acceptation permanente sans réévaluation. Le contexte de déploiement évolue et de nouvelles voies de code peuvent apparaître.

Les registres privés et proxys centralisent les téléchargements et améliorent la traçabilité, mais ne rendent pas automatiquement tout paquet digne de confiance. Contrôlez les sources, versions, signatures disponibles et provenance. La licence compte également : un paquet sans vulnérabilité peut être incompatible avec les obligations de distribution.

## 10. Détection des secrets

Le secret scanning détecte des formats de clés, jetons et mots de passe dans le code, parfois dans l’historique ou les dépôts. Un contrôle local ou à la création d’une pull request permet une réaction rapide ; une surveillance du dépôt reste utile pour trouver des ajouts passés inaperçus.

Un faux positif peut se produire quand une chaîne de test ressemble à un secret. Utilisez des valeurs fictives documentées et des exceptions ciblées. Ne commitez pas une vraie clé pour démontrer qu’un outil la détecte. Vérifiez que le mécanisme ne peut pas être désactivé silencieusement par la modification qu’il doit contrôler.

Quand un secret actif est détecté, révoquez ou remplacez la valeur, recherchez son usage, évaluez les permissions associées et nettoyez les copies. Le retrait du dernier fichier ne garantit pas que la valeur est absente de l’historique, des clones, des journaux ou des caches. Les logs doivent eux-mêmes être protégés, avoir une durée de conservation définie et limiter les accès.

## 11. DAST et tests dynamiques

Le DAST teste une application en fonctionnement. Il peut trouver certains problèmes visibles depuis l’extérieur : contrôle d’accès insuffisant, paramètres mal traités, configuration faible ou fuite d’information. Il ne connaît pas toujours le code exécuté et ne couvre pas toutes les branches. Son efficacité dépend de la portée, de l’authentification, des données de test et des fonctionnalités atteintes.

~~~text
[Déploiement de test]
       |
       v
[Données synthétiques]
       |
       v
[DAST authentifié et limité]
       |
       +--> Surface et configuration
       +--> Contrôles d'accès
       +--> Entrées et erreurs
       |
       v
[Triage, reproduction et correction]
       |
       v
[Nouveau test]
~~~

Exécutez le scanner dans un environnement autorisé, avec une portée claire et des données synthétiques. Un outil actif peut créer des ressources, modifier l’état ou générer une charge. Ne le dirigez pas vers la production sans autorisation explicite, limites et plan de retour arrière. Les tests d’API doivent vérifier l’autorisation réelle : un utilisateur ne doit pas lire les ressources d’un autre en modifiant un identifiant, même si l’interface masque le lien.

Le fuzzing explore des entrées variées pour trouver des crashs ou des violations d’invariants. Un test d’intrusion examine des scénarios complexes et des failles de conception. Ces activités ont une valeur différente des analyses continues ; elles les complètent plutôt que de les remplacer.

## 12. Infrastructure as Code et politiques

L’Infrastructure as Code décrit les ressources dans des fichiers versionnés, revus et exécutés de manière contrôlée. Une analyse avant application peut détecter un stockage public, des permissions IAM excessives, l’absence de chiffrement, des règles réseau trop larges ou des journaux désactivés. Le plan de changement doit être revu pour son impact et ses opérations destructives.

~~~text
Pull request IaC
      |
      v
Format + validation syntaxique
      |
      v
Analyse de configuration et dépendances
      |
      v
Plan de changement
      |
      v
Politique as code ---- échec critique ----> blocage
      |
      v
Revue et approbation
      |
      v
Application avec identité limitée
      |
      v
Contrôle de dérive et audit
~~~

Le plan n’est pas une garantie absolue : il dépend de variables, d’état distant, de modules et de permissions réelles. Contrôlez la provenance des modules et leurs versions, protégez l’état IaC et n’affichez pas les valeurs sensibles. Séparez les droits qui lisent l’état, planifient et appliquent. Un job d’analyse ne doit pas disposer de droits de modification en production.

Une politique as code traduit des invariants en décisions reproductibles : empêcher le stockage public, exiger le chiffrement, limiter un rôle aux actions nécessaires ou imposer des tags de responsabilité. Les règles doivent expliquer comment corriger la ressource. Testez les cas conformes, interdits et inconnus. Une règle incompréhensible incite à chercher un contournement.

La détection de dérive compare l’état réel à la déclaration. Elle peut identifier un port ouvert manuellement ou une ressource non gérée. Une correction automatique peut interrompre un service si elle est mal conçue. Définissez quand appliquer une réparation et quand demander une revue, et conservez une preuve du changement.

## 13. Construire une image de conteneur sûre

La sécurité de l’image commence par le choix d’une base maintenue, l’installation des seuls paquets nécessaires, l’exécution sous un utilisateur non privilégié quand cela est possible et la séparation des étapes de construction de l’image finale. Les compilateurs, caches et fichiers temporaires n’ont pas nécessairement leur place dans l’image d’exécution. Évitez d’inclure des fichiers secrets dans le contexte de build.

Les instructions de construction sont du code. Un script qui télécharge une dépendance sans contrôle, un dépôt ajouté sans vérification ou un tag mutable peut introduire des changements inattendus. Contrôlez les versions et les sources. Une image minimale réduit la surface d’attaque, mais une image abandonnée peut être plus risquée qu’une image maintenue comportant quelques paquets de plus.

~~~text
Code + dépendances verrouillées
             |
             v
Construction isolée et contrôlée
             |
             v
Image finale minimale
             |
             v
Scan des composants et de la configuration
             |
             v
SBOM + provenance + signature
             |
             v
Déploiement par digest validé
~~~

Scannez les images avant promotion et examinez les findings selon la version affectée, le composant présent, l’exploitabilité, l’exposition et la disponibilité d’un correctif. Après correction, reconstruisez et testez l’image. Ne modifiez pas manuellement un conteneur en production sans représenter le changement dans la source de vérité.

Un tag tel que latest est mutable et n’identifie pas de façon stable l’image testée. Le digest identifie le contenu exact, mais ne prouve pas qui a construit l’image ni si les contrôles ont réussi. Il doit être lié à la provenance, aux signatures et aux résultats de validation.

## 14. SBOM, provenance et traçabilité

Une SBOM est une nomenclature logicielle qui inventorie les composants présents dans un logiciel ou un artefact. SPDX et CycloneDX sont des formats courants. Une SBOM bien produite indique les paquets et versions observés et facilite la recherche de vulnérabilités ou l’analyse des licences. Elle doit correspondre à l’artefact final, pas seulement au répertoire de développement : le contenu peut changer entre la source, le build et l’image livrée.

La SBOM n’est pas une certification de sécurité. Sa précision dépend de l’outil, de l’écosystème et des composants observables. Reliez-la au digest, à la version, à la source et à la construction. Quand un avis est publié, l’équipe doit trouver les artefacts concernés puis les environnements où ils tournent.

La provenance décrit la fabrication : source, workflow, étapes et paramètres utiles. Une attestation est une déclaration structurée à propos d’un artefact ou d’un processus. L’intégrité du document et la confiance dans son émetteur doivent toutes deux être vérifiées. Une attestation émise par un workflow contrôlé par une pull request non fiable ne prouve pas que l’artefact est approuvé.

~~~text
Commit approuvé
      |
      v
Workflow de confiance
      |
      v
Build isolé
      |
      +------------------+
      v                  v
Image + digest          SBOM
      \                  /
       \                /
        v              v
       Provenance et attestations
                  |
                  v
          Politique de promotion
~~~

SLSA fournit un cadre de garanties de la supply chain logicielle, notamment autour de la construction et de la provenance. Ne traitez pas un niveau comme un badge ; examinez les exigences et vérifiez que votre chaîne les satisfait. La traçabilité doit répondre à ces questions : quel code a créé cet artefact, quel workflow l’a construit, quelles dépendances ont été incluses et quel digest est déployé ? Si la réponse dépend de journaux éphémères ou d’un tag mutable, la preuve est insuffisante.

## 15. Signer et vérifier les artefacts

Une signature numérique permet de détecter une modification et d’associer un artefact à une clé ou une identité selon un mécanisme défini. Elle ne garantit pas que le logiciel est exempt de vulnérabilités. La politique doit identifier les signataires autorisés, l’émetteur de confiance, le digest exact et les attestations exigées.

Sigstore et Cosign fournissent des mécanismes de signature et de vérification des artefacts. Dans une configuration keyless, une identité OIDC peut être associée à un certificat à courte durée. Vérifiez l’identité exacte et l’émetteur attendu. Ne vous contentez pas d’accepter n’importe quelle signature valide ou d’utiliser un motif d’identité excessivement large.

~~~text
Image par digest
      |
      v
Signature valide ?
  | non --> REFUS
  v oui
Identité de signature autorisée ?
  | non --> REFUS
  v oui
Provenance et SBOM attendues ?
  | non --> QUARANTAINE / REVUE
  v oui
Promotion autorisée par politique
~~~

Le contrôle doit avoir lieu à un endroit qu’un déploiement alternatif ne peut pas contourner. Une image vérifiée en CI ne suffit pas si une autre référence peut être déployée ensuite. Une politique d’admission Kubernetes peut, selon l’architecture, imposer les exigences au moment où une charge est créée.

Définissez la rotation et la révocation des identités, la protection des droits de signature et les responsabilités. Les flux keyless déplacent une partie de la gestion vers les identités et les certificats de courte durée ; ils ne suppriment pas la nécessité d’une politique de confiance.

## 16. Priorisation et seuils de blocage

Les outils peuvent émettre beaucoup de findings. Deux extrêmes sont à éviter : tout bloquer sans hiérarchiser ou ignorer toutes les alertes. Tenez compte de la gravité, de l’exposition, des privilèges, des données concernées, de l’exploitation connue, de la disponibilité d’un correctif et des contrôles compensatoires. Le score technique aide, mais ne résume pas le risque local.

~~~text
DÉCISION SUR UN FINDING
                       Exposition
                   Faible        Élevée
Gravité faible     Planifier     Analyser le contexte
Gravité élevée     Évaluer       Blocage / correction rapide

Autres facteurs :
- exploitation connue ou probable
- privilèges et données touchées
- disponibilité du correctif
- mesure compensatoire
- propriétaire et échéance
~~~

Une fuite certaine d’un secret actif exige une réponse immédiate. Une vulnérabilité critique exploitable dans un composant exposé peut bloquer une publication. Un résultat moyen dont l’exploitation est peu probable peut être planifié si un propriétaire et une date sont définis. Ce sont des exemples, pas des seuils universels : l’organisation doit les formaliser.

Reliez les résultats entre exécutions et attribuez-les à un propriétaire. Sans déduplication, les mêmes alertes se répètent et la fatigue augmente. Conservez la date de première détection, le statut, la décision et la preuve du correctif. Une exception doit expirer ou être réévaluée. Un finding ne doit pas disparaître simplement parce que l’outil change son identifiant.

Définissez le comportement lorsque l’outil est indisponible. Pour une preuve critique, l’absence de résultat fiable peut justifier un blocage. Pour une analyse informative moins critique, le pipeline peut continuer avec une alerte et une procédure de rattrapage. L’erreur dangereuse consiste à convertir silencieusement une erreur technique en réussite.

## 17. Sécuriser le déploiement Kubernetes

Le déploiement ouvre une nouvelle frontière de confiance. Vérifiez que la version déployée correspond à l’artefact approuvé, que l’identité a uniquement les droits nécessaires et que les environnements sensibles ont les approbations requises. Le job de déploiement n’a pas besoin de droits administratifs complets du cluster pour mettre à jour une application.

Appliquez les contrôles Kubernetes pertinents : comptes de service distincts, RBAC minimal, restrictions de sécurité des pods, limites de ressources, gestion sûre des secrets, segmentation réseau et contrôle d’admission. Utilisez le digest d’image validé et empêchez le chemin de déploiement de substituer une autre référence. La vérification doit rechercher une identité de signature précise.

~~~text
Workflow approuvé
       |
       v
Identité temporaire et limitée
       |
       v
API Kubernetes
       |
       v
Admission : signature / provenance / politique
       |
       +---- non conforme ----> Refus + journal
       |
       v
Création du Pod
       |
       v
Contrôles réseau et runtime
~~~

Une politique d’admission mal testée peut interrompre un service. Commencez si nécessaire en mode audit, inventoriez les exceptions, testez les cas légitimes puis appliquez progressivement le blocage. La procédure d’urgence doit être étroite, surveillée, documentée et révocable, jamais un droit général qui désactive la politique.

Les contrôles de déploiement ne remplacent pas la sécurité au runtime. Un défaut inconnu peut subsister et la configuration du cluster peut évoluer. Les journaux, alertes runtime, politiques réseau et identités de service restent nécessaires. Les signaux de production alimentent les tests et les priorités de correction.

## 18. Promotion, canary et retour arrière

La promotion fait passer un artefact vérifié d’un environnement à un autre. Lorsque l’architecture le permet, promouvez le même artefact immuable au lieu de reconstruire un contenu différent à chaque étape. Si la reconstruction est nécessaire, conservez une preuve vérifiable du lien entre le contenu final et les contrôles antérieurs.

Un déploiement progressif, canary ou blue/green, limite la portée initiale d’une version et facilite l’observation. Définissez les signaux d’arrêt : taux d’erreurs, latence, comportements inattendus, incidents de sécurité ou régressions métier. Un retour arrière ne neutralise pas nécessairement les effets d’une migration de base ou d’une fuite de données ; prévoyez la compatibilité et la restauration.

~~~text
Version validée
      |
      v
Canary sur une partie du trafic
      |
      v
Mesures d'erreurs, latence et incidents
      |
      +---- seuil dépassé ----> Arrêt et retour maîtrisé
      |
      v
Promotion graduelle
      |
      v
Surveillance renforcée
      |
      v
Retour d'expérience
~~~

La séparation des tâches réduit le risque qu’une seule identité modifie le code, désactive les contrôles, signe l’artefact et le déploie. Cela peut être obtenu par des permissions, des environnements protégés, des approbations distinctes et des journaux. Une approbation n’a de valeur que si la personne voit le changement, les résultats de contrôle et les risques restant à traiter.

## 19. Observabilité et réponse à incident

Les journaux doivent permettre de savoir qui a déclenché un job, quel commit a été construit, quelles actions et dépendances ont été utilisées, quelle identité a accédé à une ressource, quel digest a été publié et pourquoi le déploiement a été autorisé. Collectez les événements essentiels avec horodatage et identifiants de corrélation, mais ne stockez pas des secrets ou des données personnelles sans nécessité.

Surveillez les changements inattendus de workflow, l’élargissement des permissions, l’utilisation anormale des jetons, les nouveaux téléchargements d’actions, les accès inhabituels au registre, la modification d’un artefact après validation et la désactivation d’un contrôle. Une alerte a besoin d’un niveau de gravité, d’un propriétaire et d’une procédure d’escalade.

~~~text
Signal suspect
      |
      v
Collecter acteur, commit, job et artefact
      |
      v
Corréler avec les politiques et l'historique
      |
      +--> Bruit : ajuster la détection
      |
      v
Incident confirmé ou plausible
      |
      v
Contenir, révoquer, isoler et préserver les preuves
      |
      v
Identifier les artefacts et reconstruire
      |
      v
Corriger la cause racine et tester les protections
~~~

Si un runner privilégié est suspect, interrompez la propagation, isolez-le, révoquez les identités qui ont pu être exposées et préservez les preuves utiles. Identifiez les artefacts produits pendant la période suspecte et les environnements dans lesquels ils ont été déployés. Une relance immédiate sans enquête peut répéter la compromission. Ne copiez pas les secrets dans des tickets ou rapports.

La réponse définit qui suspend la publication, qui contacte l’équipe cloud ou le registre, qui informe les propriétaires de services et qui valide la reprise. Après incident, transformez les enseignements en contrôles : réduction des permissions, isolation accrue, meilleure traçabilité ou tests de détection. L’objectif est de supprimer les conditions qui ont rendu l’incident possible.

## 20. Mesurer l’efficacité

Les métriques utiles comprennent le délai entre détection et correction, le temps de mise à jour d’une dépendance critique, la couverture des dépôts, la proportion de publications avec provenance vérifiable, le nombre d’exceptions expirées et le délai de révocation d’un secret. Chaque mesure a besoin d’une définition, d’une source, d’une fréquence, d’un propriétaire et d’une décision qu’elle permet de prendre.

~~~text
INDICATEUR                   QUESTION
---------------------------  ------------------------------------------
Délai de correction          Les risques diminuent-ils rapidement ?
Couverture des analyses      Quels dépôts sont oubliés ?
Provenance vérifiable        Peut-on expliquer la construction ?
Exceptions en retard         La dette de risque est-elle maîtrisée ?
Révocation de secrets        La réponse est-elle rapide ?
Déploiements refusés         Les politiques sont-elles cohérentes ?
~~~

Le nombre brut de vulnérabilités peut augmenter lorsque la couverture s’améliore. Une baisse ne prouve rien si des contrôles ont été désactivés. Complétez les compteurs par des échantillonnages, la vérification des politiques et l’analyse des incidents. Les métriques ne doivent pas encourager les équipes à cacher ou reclasser les risques.

Si un contrôle est trop lent, améliorez les outils, les caches sûrs, le parallélisme et la structure du workflow. Ne désactivez pas un contrôle critique parce qu’il est gênant. Placez les analyses rapides dans les pull requests et les travaux lourds à l’étape appropriée, tout en définissant les vérifications obligatoires avant promotion.

## 21. Exemple de pipeline défensif

Le schéma ci-dessous est volontairement conceptuel : les références d’actions et commandes doivent être remplacées par des valeurs réelles vérifiées et maintenues. Il illustre surtout la séparation des permissions. Ne copiez pas une référence fictive dans un dépôt de production.

~~~yaml
name: verification-securisee
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  verification:
    runs-on: runner-isole
    permissions:
      contents: read
    steps:
      - name: Checkout
        uses: fournisseur/action@SHA_COMPLET_A_VERIFIER
      - name: Tests
        run: commande-de-tests-du-projet
      - name: Analyse statique
        run: commande-sast-configuree
      - name: Analyse dependances
        run: commande-sca-configuree
      - name: Detection secrets
        run: commande-secret-scanning

  publication:
    if: branche-protegee-et-controles-valides
    needs: verification
    runs-on: runner-publication-isole
    permissions:
      contents: read
      id-token: write
      packages: write
    environment: publication-protegee
    steps:
      - name: Produire les preuves
        run: build-sbom-provenance-signature
~~~

Cet exemple n’est pas directement exécutable : les noms sont des marqueurs d’architecture. Le workflow réel dépend du fournisseur CI, du langage, du registre et du cloud. Le principe est de donner un accès en lecture au job de vérification et de réserver les permissions de publication à un job déclenché depuis un contexte approuvé. L’identité de publication doit être liée au dépôt et à l’environnement attendu.

Testez les événements exacts, les pull requests de forks, les branches non protégées et les échecs de contrôle. Vérifiez que le job de publication n’est pas activable depuis un contexte non fiable et qu’aucun autre workflow n’offre les mêmes droits. Conservez une stratégie de mise à jour des actions épinglées et des images de runner.

Le job de publication doit vérifier que les tests attendus ont réussi sur la bonne révision, que les preuves sont présentes et que le digest est enregistré. L’état du workflow doit correspondre à l’artefact réellement publié. Une coche verte d’une ancienne exécution ou d’un autre commit ne constitue pas une preuve.

## 22. Tester les politiques elles-mêmes

Les règles de sécurité sont du code et peuvent contenir des erreurs. Ajoutez des tests pour les entrées acceptées et refusées. Un test précise sa configuration, le résultat attendu et sa justification. Quand une politique change, examinez les ressources bloquées ou nouvellement autorisées et l’impact sur les exceptions existantes.

~~~text
Entrée conforme      --> ACCEPTÉ
Entrée interdite     --> REFUSÉ
Valeur inconnue      --> Résultat explicitement défini
Scanner indisponible --> Comportement documenté
Exception expirée    --> Refus ou nouvelle approbation
~~~

Utilisez des données synthétiques pour les tests négatifs. Ne créez pas de ressource de production vulnérable pour vérifier le scanner. Une politique de stockage privé peut être testée avec une configuration fictive demandant l’accès public ; un contrôle de signature peut utiliser une image de test non signée.

Prévoyez les pannes : source d’avis indisponible, fournisseur d’identité en erreur, registre inaccessible ou signature révoquée. La politique doit distinguer résultat négatif, résultat positif, preuve manquante et indisponibilité. Exercez ces scénarios en équipe ; les réponses doivent être suffisamment précises pour éviter d’inventer une procédure durant un incident.

## 23. Travaux pratiques guidés

### TP 1 — Auditer un workflow de pull request

**Situation :** le pipeline teste, publie un paquet et déploie sur chaque pull request. Un seul jeton dispose de droits de lecture, d’écriture et de déploiement. Les actions sont référencées par des tags et un titre de pull request est inséré directement dans une commande.

**Étape 1 : dessiner le flux.** Identifiez le déclencheur, le code exécuté, le runner, les secrets, le registre et la cible, y compris les scripts exécutés indirectement.

**Étape 2 : classer la confiance.** Une pull request de fork est non fiable. Elle peut exécuter les tests sans secrets de production et avec des permissions minimales. La validation du code proposé doit être séparée de la publication.

**Étape 3 : scinder les tâches.** Le job de test ne reçoit que les permissions nécessaires. Le job de publication dépend de la réussite des contrôles et n’est disponible qu’après fusion approuvée. Le déploiement utilise une identité distincte.

**Étape 4 : prévenir l’injection.** Les valeurs de titre et de branche sont transmises comme données, jamais incorporées directement dans une commande. Validez les formats attendus et évitez l’interprétation secondaire.

**Étape 5 : revoir les actions.** Inventoriez les propriétaires, les permissions, la source et les versions ; épinglez les références selon la politique et planifiez leur mise à jour.

**Étape 6 : tester les restrictions.** Une pull request de fork ne publie pas ; un test en échec bloque la publication ; une branche non protégée n’obtient pas d’identité cloud ; les modifications sensibles demandent une revue.

**Correction attendue :** le pipeline sépare les niveaux de confiance, minimise les permissions, protège les secrets et relie la publication au code approuvé. Les restrictions sont vérifiées par des tests et des protections de dépôt.

### TP 2 — Ajouter SAST, SCA et secret scanning

**Situation :** les tests unitaires passent mais le projet n’a pas d’inventaire des dépendances et les alertes ne sont attribuées à personne.

**Étape 1 : établir une référence.** Exécutez les outils sur une branche de travail. Examinez des échantillons, classez les résultats et relevez les limites de couverture.

**Étape 2 : placer les analyses.** Ajoutez des contrôles rapides aux pull requests et des analyses plus complètes aux étapes adaptées. Documentez le comportement en cas de panne d’un outil.

**Étape 3 : définir les blocages.** Précisez les cas qui empêchent la fusion, notamment les secrets actifs exposés et les catégories critiques retenues par la politique. Les cas non bloquants ont un propriétaire et une échéance.

**Étape 4 : rendre les alertes actionnables.** Pour une dépendance, indiquez le composant, la version, la chaîne transitive et le correctif possible. Pour SAST, documentez le chemin des données et les conditions d’exploitation.

**Étape 5 : tester le détecteur de secrets.** Utilisez des valeurs fictives et documentées. N’utilisez aucune vraie clé. Vérifiez que les exceptions ne désactivent pas toute la règle.

**Étape 6 : mesurer la qualité.** Suivez le délai de triage, la correction, la couverture et la proportion de résultats attribués. Le compteur brut de vulnérabilités n’est pas suffisant.

**Correction attendue :** les résultats sont dédupliqués et priorisés, chaque anomalie a un propriétaire et une échéance, les exceptions sont limitées et l’équipe distingue un résultat propre d’une analyse en échec.

### TP 3 — SBOM, provenance et signature d’image

**Situation :** plusieurs tags d’image sont disponibles dans le registre, et les déploiements n’enregistrent que le tag. Lorsqu’une vulnérabilité est annoncée, l’équipe ne sait pas où se trouve le composant.

**Étape 1 : enregistrer un digest.** Identifiez l’image finale par son digest, pas seulement par un tag mutable.

**Étape 2 : générer la SBOM.** Choisissez SPDX ou CycloneDX. Vérifiez qu’elle correspond à l’image livrée et documentez les limites de l’outil.

**Étape 3 : établir la provenance.** Reliez l’image au commit et au workflow. L’attestation doit provenir d’un processus de confiance.

**Étape 4 : signer et vérifier.** Configurez une identité autorisée. Avec Cosign, vérifiez la signature et l’émetteur attendu. Une expression d’identité trop permissive annulerait la valeur du contrôle.

**Étape 5 : imposer la politique.** Vérifiez l’image avant promotion et assurez-vous que le déploiement utilise le digest validé. Si possible, renforcez la règle par l’admission Kubernetes.

**Étape 6 : répondre à un avis.** Cherchez le composant dans la SBOM, identifiez les digests concernés et retrouvez les environnements correspondants. Reconstruisez une version corrigée et passez-la par les validations.

**Correction attendue :** chaque artefact possède une identité immuable, une SBOM, une provenance et une signature vérifiable liée à une identité autorisée. La signature seule ne prouve pas l’absence de vulnérabilité.

### TP 4 — Politique IaC et exception urgente

**Situation :** une pull request propose un stockage public et un rôle administrateur général pour le compte de service d’une application. Le scanner signale les deux points, mais la chaîne ne bloque rien.

**Étape 1 : analyser l’impact.** Identifiez les données exposées, l’environnement, les privilèges nécessaires et les chemins réseau.

**Étape 2 : proposer une correction.** Limitez le stockage à la portée attendue, activez les protections nécessaires et réduisez le rôle aux actions indispensables.

**Étape 3 : écrire une politique testable.** Refusez par défaut le stockage public et les privilèges administratifs généraux pour un compte de service applicatif. Testez un cas conforme, interdit et inconnu.

**Étape 4 : traiter l’urgence.** Une exception indique l’actif, le risque, la justification, la mesure compensatoire, l’approbateur, le propriétaire et l’échéance. Elle ne supprime pas toute la politique.

**Étape 5 : séparer les permissions.** Le job d’analyse lit le plan mais n’applique pas de modification. Seul un job approuvé reçoit les droits nécessaires.

**Étape 6 : vérifier l’état réel.** Après application, examinez la configuration réelle et la journalisation. Le fichier déclaré ne prouve pas que l’environnement est resté conforme.

**Correction attendue :** les configurations dangereuses sont bloquées avant application, les permissions de modification sont réservées à l’étape approuvée et les exceptions sont limitées dans le temps.

## 24. Vingt exercices corrigés

### Exercice 1 — Pourquoi adopter DevSecOps ?
**Correction :** intégrer la sécurité au processus permet de détecter plus tôt les défauts, de rendre les contrôles reproductibles et de réduire les validations manuelles. Cela ne supprime pas l’expertise spécialisée.

### Exercice 2 — Un fork peut-il déployer en production ?
**Correction :** une pull request de fork doit être traitée comme non fiable et ne doit pas recevoir des secrets de production. Elle peut exécuter des tests isolés ; la publication intervient depuis un contexte approuvé.

### Exercice 3 — Faut-il donner un droit d’écriture au job de test ?
**Correction :** généralement non. Il reçoit les permissions nécessaires pour récupérer le code et produire ses résultats. Les permissions d’écriture appartiennent aux jobs qui en ont besoin.

### Exercice 4 — Que garantit un SHA complet pour une action ?
**Correction :** il fixe précisément le code référencé et réduit le risque d’un tag déplacé. Il ne garantit pas l’absence de vulnérabilité et doit être accompagné d’un audit et de mises à jour.

### Exercice 5 — Comment réduire l’injection shell ?
**Correction :** traitez les champs d’événement comme des données, transmettez-les dans un contexte sûr, validez-les et évitez l’interprétation secondaire. Testez avec des entrées contenant des caractères spéciaux.

### Exercice 6 — Supprimer une clé d’un commit suffit-il ?
**Correction :** non. Révoquez-la, recherchez les usages possibles et les copies dans l’historique, les logs et les artefacts, puis corrigez la cause de fuite.

### Exercice 7 — OIDC élimine-t-il la politique de confiance ?
**Correction :** non. Il peut éviter les clés longues durées, mais l’émetteur, l’audience, le dépôt, la branche et l’environnement doivent être restreints.

### Exercice 8 — Pourquoi isoler les runners ?
**Correction :** un job non fiable peut tenter de persister, lire des fichiers résiduels ou empoisonner un cache. Des pools séparés et des environnements réinitialisés réduisent ces possibilités.

### Exercice 9 — Un finding SAST prouve-t-il une exploitation ?
**Correction :** il signale un motif suspect. Il faut vérifier les données contrôlables, le chemin d’exécution, le contexte et les protections.

### Exercice 10 — Pourquoi inventorier les dépendances transitives ?
**Correction :** elles peuvent faire partie du logiciel livré et contenir des vulnérabilités même si elles ne sont pas déclarées directement. L’inventaire doit refléter les composants réellement livrés.

### Exercice 11 — SCA remplace-t-elle les tests ?
**Correction :** non. SCA analyse les composants et leurs risques connus ; elle ne teste pas tous les comportements et défauts de conception.

### Exercice 12 — Que teste DAST ?
**Correction :** DAST observe une application en fonctionnement. Il doit être limité à un environnement autorisé et n’offre pas une couverture totale du code.

### Exercice 13 — Une SBOM certifie-t-elle la sécurité ?
**Correction :** non. Elle rend les composants visibles et facilite l’analyse ; sa qualité dépend du processus et elle doit correspondre à l’artefact final.

### Exercice 14 — Pourquoi utiliser un digest ?
**Correction :** le digest identifie le contenu précis de l’image, alors qu’un tag peut changer. Il faut le relier aux preuves de provenance et de vérification.

### Exercice 15 — Que vérifier en plus d’une signature valide ?
**Correction :** le signataire doit être autorisé, l’émetteur attendu et le digest identique à l’artefact demandé. La signature ne garantit pas l’absence de vulnérabilités.

### Exercice 16 — Tous les findings moyens doivent-ils bloquer ?
**Correction :** la décision dépend du contexte, de l’exposition, de l’exploitabilité, des privilèges et des compensations. Les règles doivent être documentées et cohérentes.

### Exercice 17 — Pourquoi analyser l’IaC avant application ?
**Correction :** les erreurs de configuration peuvent être détectées avant impact. Le plan, l’état réel et les permissions doivent toujours être contrôlés.

### Exercice 18 — Que faire après la compromission d’un runner ?
**Correction :** contenir, isoler, révoquer les identités concernées, préserver les preuves, identifier les artefacts touchés et reconstruire depuis une source saine.

### Exercice 19 — Le nombre de vulnérabilités doit-il toujours baisser ?
**Correction :** non. Une meilleure couverture peut augmenter le nombre détecté. Suivez aussi le délai de correction, la couverture et les exceptions expirées.

### Exercice 20 — Que documenter dans une exception ?
**Correction :** l’actif, le périmètre, le risque, la justification, les mesures compensatoires, le propriétaire, l’approbateur, l’échéance et les critères de réévaluation.

## 25. Défi final : concevoir une livraison vérifiable

**Scénario :** une API conteneurisée est déployée sur Kubernetes. Le code réside dans un dépôt Git ; les dépendances viennent d’un registre ; l’infrastructure est décrite en IaC ; les déploiements sont automatisés. L’équipe veut réduire les risques sans rendre chaque livraison manuelle.

**A. Entrée du code.** Définissez les protections de branches, les reviewers des modifications sensibles, le traitement des pull requests externes et la prévention de neutralisation des contrôles. Les statuts doivent correspondre au commit fusionné.

**B. Vérifications.** Placez les tests unitaires, SAST, SCA, secret scanning et analyse IaC aux étapes adaptées. Distinguez les résultats bloquants, ceux à trier et l’indisponibilité d’un outil. Chaque exception doit être attribuée et expirée.

**C. Construction.** Utilisez des bases maintenues, des dépendances contrôlées, un runner isolé et un mécanisme empêchant les secrets de persister. Générez une image par digest et une SBOM correspondant à cet artefact.

**D. Preuves.** Reliez la provenance au commit et au workflow. Limitez les identités qui peuvent signer ; vérifiez la signature et l’émetteur attendus. Expliquez pourquoi une signature valide n’indique pas l’absence de vulnérabilité.

**E. Déploiement.** Séparez les permissions de test, de publication et de déploiement. Utilisez une identité temporaire lorsque possible. Vérifiez le digest validé et imposez la politique à la promotion et, si l’architecture le permet, à l’admission Kubernetes.

**F. Opérations.** Conservez les informations de traçabilité, surveillez les usages anormaux et définissez les procédures de fuite de secret, de runner compromis et de vulnérabilité annoncée après déploiement. Mesurez la couverture, le délai de correction et les exceptions expirées.

### Correction détaillée

Une bonne conception sépare les niveaux de confiance. Les contributions non fiables s’exécutent sans secrets de production et avec des permissions minimales. Les branches protégées imposent les revues et contrôles nécessaires. Les workflows et fichiers d’infrastructure sont traités comme des changements sensibles et les résultats s’appliquent à la version qui sera réellement fusionnée.

Les analyses produisent des résultats actionnables : dépendances verrouillées, alertes dédupliquées, secrets détectés, IaC contrôlée et seuils de blocage documentés. Une panne d’outil n’est pas automatiquement considérée comme un succès. Toute exception est limitée dans le temps et confiée à une personne qui doit confirmer son maintien ou sa suppression.

La construction est isolée, sans clé cloud durable inutile. Les runners et caches ne transmettent pas de privilèges entre jobs non fiables et privilégiés. L’image utilise une base maintenue et ne contient pas les secrets de build. La SBOM correspond à l’image finale ; la provenance relie l’artefact au commit et au processus de construction.

La signature est émise par une identité protégée et vérifiée selon une politique précise. Le déploiement utilise le digest validé et une identité aux droits limités. L’admission Kubernetes peut renforcer l’application de la politique. Les protections restantes du cluster incluent RBAC, comptes de service, sécurité des pods, segmentation réseau, gestion des secrets, limites de ressources et journalisation.

Lors d’un avis de vulnérabilité, la SBOM permet de trouver les composants concernés et les digests identifient les artefacts. Les logs les relient aux environnements déployés. L’équipe reconstruit une version corrigée, puis la fait passer par le même chemin de validation. En cas de fuite, elle révoque le secret, examine les usages, identifie les artefacts affectés et corrige la cause racine.

Le défi est réussi si l’organisation peut répondre de façon vérifiable : qui a approuvé le code ? Quelles dépendances ont servi à construire l’image ? Quelle identité a lancé le build et signé l’artefact ? Quel digest est exécuté ? Quels contrôles ont autorisé la promotion ? Comment identifier les instances affectées et révoquer une identité compromise ? Ces réponses ne doivent pas dépendre du souvenir d’un membre de l’équipe ou d’un tag changeant.

## 26. Checklist de mise en œuvre

### Dépôt et contributions
- Les branches principales et fichiers de workflow sensibles sont protégés.
- Les revues et contrôles obligatoires sont liés au commit exact.
- Les contributions non fiables n’ont pas accès aux secrets de production.
- Les exceptions sont traçables, limitées et expirables.

### CI et identités
- Les permissions des jobs sont explicitement minimales.
- Les actions externes sont auditables, épinglées selon la politique et mises à jour.
- Les runners et caches sont isolés par niveau de confiance.
- Les identités temporaires sont privilégiées aux clés persistantes lorsque possible.
- Les données d’événement ne sont pas insérées directement dans les commandes.

### Analyses
- Les tests, SAST, SCA, secret scanning et contrôles IaC couvrent les changements pertinents.
- Les résultats ont un propriétaire, une priorité et une échéance.
- Les outils en panne ne sont pas assimilés à un résultat conforme.
- Les tests dynamiques ciblent seulement un environnement autorisé.
- Les exceptions indiquent le risque résiduel.

### Artefacts et déploiement
- L’image repose sur des composants maintenus et ne contient pas de secrets.
- La SBOM correspond à l’artefact final.
- La provenance décrit la construction et la signature est vérifiée.
- Le déploiement utilise le digest validé et une identité limitée.
- Les politiques empêchent les voies de déploiement de contourner les contrôles.

### Opérations
- Les logs relient acteur, commit, workflow, artefact et environnement.
- Les procédures de fuite de secret et de runner compromis sont connues.
- Les alertes ont un propriétaire et une procédure de réponse.
- Les métriques suivent couverture, correction, provenance et exceptions.
- Les contrôles sont révisés après les incidents et changements majeurs.

## 27. Erreurs de conception fréquentes

**Ajouter des scanners sans processus de correction.** Les résultats deviennent du bruit si personne n’est responsable. Définissez seuils, attribution, échéance et exceptions avant d’ajouter de nouvelles alertes.

**Donner les mêmes permissions à tous les jobs.** Une étape de test compromise pourrait alors atteindre la production. Séparez identités, runners et opérations.

**Confondre absence d’alerte et absence de risque.** La couverture est limitée et évolue. Documentez les angles morts et combinez les contrôles.

**Signer sans contrôler l’identité.** La signature d’un workflow non fiable ne justifie pas une promotion. Protégez le signataire et vérifiez l’identité exacte.

**Déployer par tag mutable.** Le tag peut pointer ailleurs que vers le contenu vérifié. Enregistrez le digest et déployez cette référence.

**Conserver les exceptions indéfiniment.** Une exception sans échéance devient une politique parallèle non gouvernée. Surveillez les dates et réévaluez le risque.

**Partager un runner surpuissant.** Les jobs peuvent laisser des données ou atteindre des identités d’autres tâches. Isolez les niveaux de confiance et réduisez l’accès réseau.

**Désactiver un contrôle parce qu’il est lent.** Optimisez le processus, les caches, le parallélisme et la séparation des phases. Ne retirez pas un contrôle critique sans décision documentée.

## 28. Glossaire

- **CI** : intégration continue, contrôles automatisés sur les changements.
- **CD** : livraison ou déploiement continu selon le contexte.
- **DevSecOps** : intégration de la sécurité à la conception, au développement, à la livraison et à l’exploitation.
- **Runner** : environnement exécutant les étapes d’un pipeline.
- **SAST** : analyse statique du code.
- **SCA** : inventaire et analyse des dépendances.
- **DAST** : analyse dynamique d’une application active.
- **SBOM** : nomenclature des composants logiciels d’un artefact.
- **Provenance** : informations décrivant comment un artefact a été produit.
- **Attestation** : déclaration structurée à propos d’un artefact ou processus.
- **Digest** : empreinte identifiant le contenu exact d’un artefact.
- **Signature** : preuve cryptographique liant des données à une clé ou identité.
- **OIDC** : protocole d’identité permettant notamment la fédération.
- **SLSA** : cadre de garanties de la supply chain logicielle.
- **Policy as Code** : règles de conformité exprimées et testées comme du code.
- **Runner éphémère** : environnement détruit ou réinitialisé après une tâche.
- **Dépendance transitive** : composant inclus via une autre dépendance.
- **Faux positif** : résultat ne correspondant pas à une vulnérabilité réelle dans le contexte.
- **Risque résiduel** : risque persistant après les contrôles.
- **Contrôle compensatoire** : mesure réduisant temporairement un risque lorsque le contrôle principal ne peut pas s’appliquer.
- **Canary** : déploiement progressif sur une partie du trafic.
- **Dérive IaC** : différence entre l’infrastructure réelle et l’état déclaré.

## 29. Références officielles

- NIST SP 800-218, Secure Software Development Framework : https://csrc.nist.gov/pubs/sp/800/218/final
- NIST SP 800-204D, sécurité de la supply chain dans les pipelines CI/CD : https://csrc.nist.gov/pubs/sp/800/204/d/final
- OWASP CI/CD Security Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html
- GitHub Actions, documentation de sécurisation : https://docs.github.com/en/actions/reference/security/secure-use
- SLSA, cadre de garanties : https://slsa.dev/
- Sigstore Cosign, vérification des signatures : https://docs.sigstore.dev/cosign/verifying/verify/
- Sigstore, démarrage avec Cosign : https://docs.sigstore.dev/quickstart/quickstart-cosign/
- SPDX, SBOM et standard : https://spdx.dev/
- CycloneDX, standard SBOM : https://cyclonedx.org/

Ces documents évoluent et doivent être consultés dans leur version officielle lors de l’implémentation. Vérifiez les permissions réelles du fournisseur CI, les versions des outils et les exigences applicables. Les exemples illustrent une démarche et ne remplacent pas une revue adaptée à l’environnement.

Fin du cours.