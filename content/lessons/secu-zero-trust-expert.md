# Architecture Zero Trust

> **Mise en contexte**
>
> Un réseau d’entreprise n’est plus un château fort dont le pare-feu extérieur sépare une zone interne digne de confiance d’un Internet hostile. Les collaborateurs se connectent depuis des bureaux, des domiciles et des appareils mobiles ; les applications s’exécutent dans plusieurs clouds ; les services communiquent entre eux ; les partenaires et les chaînes d’automatisation accèdent aux données. Un compte interne peut être compromis, un poste conforme peut devenir vulnérable, et un service légitime peut être détourné. L’architecture Zero Trust répond à cette réalité : aucune confiance implicite ne doit découler uniquement de l’emplacement réseau, de la propriété d’un appareil ou de la présence d’une session déjà ouverte. L’accès se décide explicitement, selon la ressource, l’identité, le contexte, le risque et une politique vérifiable.

## Objectifs pédagogiques et fil conducteur

Ce cours expert vous apprend à concevoir, déployer et mesurer une architecture Zero Trust (ZTA). Vous apprendrez à distinguer un principe d’architecture d’un produit commercial, à cartographier les ressources et les flux, à concevoir un moteur de décision, à intégrer l’identité des personnes et des machines, à évaluer la posture des appareils, à protéger les applications et les données, à appliquer la microsegmentation, à gérer l’accès privilégié juste-à-temps, à organiser la télémétrie et à conduire une migration sans interrompre l’activité.

Le fil conducteur est une organisation fictive, **Atlas Formation**. Elle possède un annuaire d’entreprise, un portail pédagogique, une API, une base de données, des administrateurs, des intervenants externes, une infrastructure cloud et quelques serveurs internes historiques. Le réseau historique place ces systèmes derrière un pare-feu et accorde un accès large aux utilisateurs du VPN. L’objectif n’est pas de remplacer toutes les technologies d’un seul coup : il s’agit de réduire la confiance implicite, de placer des décisions de politique aux bons endroits, d’améliorer l’observabilité et de prouver que les accès sont contrôlés de bout en bout.

Les travaux pratiques sont à réaliser dans un environnement de test que vous administrez ou pour lequel vous avez une autorisation explicite. Les exercices de conception n’exigent aucun service payant : les politiques, matrices d’accès, diagrammes et plans de test peuvent être réalisés avec des fichiers texte et les outils déjà disponibles.

## 1. Du périmètre réseau à la protection de la ressource

### 1.1 Pourquoi le modèle périmétrique ne suffit plus

Dans un modèle traditionnel, un pare-feu sépare une zone externe et une zone interne. Après connexion au VPN, un utilisateur peut parfois atteindre de nombreuses adresses internes. Ce modèle reste utile pour contrôler des flux réseau, mais il crée un raccourci de confiance : « connecté au réseau » peut être confondu avec « autorisé à utiliser l’application ». Or les comptes, les postes, les services et les réseaux internes ne sont pas infaillibles.

~~~text
Modèle périmétrique classique

Internet ---> [Pare-feu/VPN] ---> [Réseau interne de confiance]
                                      |          |
                                  [Portail]   [Base de données]
                                      |
                           L'accès réseau devient
                           parfois l'unique preuve
~~~

Les conséquences sont importantes. Un poste compromis peut explorer des services qui ne lui sont pas utiles. Un compte VPN volé peut permettre des déplacements latéraux. Une application peut accorder une permission trop large, car la segmentation n’a pas été conçue autour de ses fonctions réelles. Les journaux peuvent montrer une connexion VPN réussie sans révéler quelle ressource a ensuite été consultée.

### 1.2 Le principe fondamental de Zero Trust

Zero Trust ne signifie pas « ne jamais faire confiance à personne » dans le sens courant, ni demander une nouvelle authentification pour chaque clic sans discernement. Il s’agit d’une architecture qui n’accorde pas de confiance implicite fondée sur la localisation réseau ou la propriété. Elle prend une décision explicite et contextualisée avant l’accès à une ressource, puis applique et réévalue les politiques pendant la durée et dans le périmètre appropriés.

Une décision peut intégrer l’identité, les facteurs d’authentification, le rôle, la ressource visée, la sensibilité de la donnée, la posture du terminal, l’heure, la localisation estimée, le niveau de risque et les signaux de menace. Tous ces facteurs ne sont pas nécessairement disponibles ou fiables ; il faut évaluer leur qualité, leur fraîcheur et les conséquences d’une absence de signal.

~~~text
Accès à une ressource
       |
       v
[Identité connue ?]
       |
       v
[Authentification suffisante ?]
       |
       v
[Appareil / service conforme ?]
       |
       v
[Action permise sur cette ressource ?]
       |
       v
[Conditions de risque satisfaites ?]
       |
       v
[Accorder un accès limité et observable]
       |
       +----> réévaluer lors d'un changement pertinent
~~~

### 1.3 Ce que Zero Trust n’est pas

Zero Trust n’est ni un produit unique, ni un synonyme de VPN, ni le remplacement de tous les pare-feu. Un produit d’accès distant peut contribuer à une architecture Zero Trust, mais il ne la garantit pas automatiquement. Une segmentation réseau sans identité applicative n’est pas à elle seule une architecture complète. Un fournisseur d’identité qui applique le MFA ne prouve pas que les autorisations au niveau des objets métier sont correctes. Un tableau de bord avec beaucoup de journaux ne compense pas une politique mal conçue.

Le terme ne doit pas non plus devenir un simple slogan d’achat. Une organisation doit identifier quels actifs elle protège, quelles décisions sont prises, quels composants les appliquent, comment les exceptions sont gérées, et quelles preuves démontrent que les contrôles fonctionnent. Le succès se mesure par la réduction des accès excessifs et des chemins de mouvement latéral, pas par le nombre de licences achetées.

### 1.4 Une politique porte sur une action et une ressource

La règle « les employés peuvent accéder au réseau interne » est trop large. Une politique utile répond à des questions concrètes : qui demande l’accès ? À quelle ressource ? Pour quelle action ? Dans quelles conditions ? Pour quelle durée ? Quelle donnée peut être lue ou modifiée ? Quel événement est enregistré ? Que se passe-t-il lorsque le contexte change ?

~~~text
Règle trop générale
Groupe Employés -> Réseau interne -> Autoriser

Règle contextualisée
Employé actif
  + MFA récent
  + appareil géré et conforme
  + relation métier avec le portail
  + action autorisée par le rôle
  + niveau de risque acceptable
    -> accès HTTPS au portail, sans accès direct à la base
~~~

Le niveau de précision dépend du risque. Une application publique de consultation peut demander une politique moins stricte qu’un coffre-fort de secrets ou qu’une console d’administration. Évitez toutefois de créer des exceptions invisibles ou des règles tellement complexes que personne ne peut les tester.

## 2. Concepts et principes de conception

### 2.1 Protéger les ressources plutôt que les segments seulement

La ressource peut être un dossier, une ligne de base de données, une API, un compte cloud, un processus d’administration, une identité machine ou une charge de travail. Protéger la ressource signifie qu’un chemin réseau valide ne donne pas automatiquement le droit à son contenu. La couche réseau limite les chemins possibles ; l’identité et l’application appliquent des permissions adaptées.

### 2.2 Authentification et autorisation séparées

L’authentification établit le principal qui fait la demande. L’autorisation décide si cette identité peut exécuter l’action sur la ressource dans le contexte courant. Pour une personne, on peut vérifier un fournisseur d’identité, un MFA et l’état du compte. Pour un service, on doit vérifier l’identité de charge de travail, le certificat ou le jeton et la politique d’accès machine-à-machine. Dans les deux cas, la décision porte sur une action précise.

~~~text
[Authentification]
Qui fait la demande ? Quel mécanisme prouve l'identité ?
              |
              v
[Autorisation]
Peut-il faire cette action sur cet objet maintenant ?
              |
              v
[Application]
La ressource applique effectivement la décision ?
~~~

### 2.3 Moindre privilège

Le moindre privilège accorde uniquement les droits nécessaires, à la bonne portée et pendant le temps nécessaire. Il s’applique aux personnes, aux comptes de service, aux jetons, aux rôles cloud, aux bases de données, aux équipes d’exploitation et aux outils d’automatisation. Il ne suffit pas de donner un rôle « lecture seule » si ce rôle permet d’exporter l’ensemble de la base contenant des données sensibles.

Le modèle doit différencier la consultation, la création, la modification, la suppression, l’export, la configuration et l’administration. Il doit inclure le contexte métier : un formateur peut consulter les résultats de ses groupes, mais pas forcément tous les dossiers de l’organisation. Les comptes privilégiés doivent être distincts des comptes ordinaires et leur élévation limitée dans le temps.

### 2.4 Vérifier explicitement

Vérifier explicitement signifie prendre une décision à partir de signaux définis et disponibles, au lieu de supposer qu’une ancienne connexion ou une adresse interne suffit. Cela ne signifie pas nécessairement déclencher une authentification interactive à chaque requête. Une session courte et bien contrôlée peut rester valide, à condition d’avoir des limites, une révocation et une politique de réévaluation lorsque des signaux importants évoluent.

### 2.5 Supposer la compromission possible

Le principe « assume breach » demande de concevoir les contrôles en considérant qu’un compte, un terminal ou une zone peut être compromis. Il faut limiter les accès transverses, isoler les plans d’administration, surveiller les comportements anormaux, protéger les sauvegardes et prévoir la révocation des identités. Cela ne signifie pas que l’on cesse de prévenir les incidents ; cela évite de faire reposer toute la sécurité sur l’hypothèse qu’aucune première barrière ne sera franchie.

~~~text
Si un poste est compromis
   |
   +--> il ne possède pas automatiquement les identifiants
   +--> il ne peut pas atteindre toutes les applications
   +--> il ne peut pas modifier les politiques
   +--> les sessions et jetons peuvent être révoqués
   +--> les événements permettent de reconstruire les accès
~~~

### 2.6 Continuité et expérience utilisateur

Une architecture sûre doit rester exploitable. Une réauthentification permanente pousse les utilisateurs vers des contournements, par exemple des comptes partagés ou des copies locales de données. Définissez des sessions adaptées au risque, des parcours de récupération et des mécanismes d’accès d’urgence encadrés. Le but n’est pas de multiplier la friction, mais de demander une preuve plus forte quand la ressource ou l’action le justifie.

## 3. Composants logiques de référence selon le NIST

Le NIST SP 800-207 formalise une architecture de référence qui distingue notamment le plan de décision et le plan d’application de la politique. Les noms sont des rôles logiques : ils peuvent être implémentés par un service, plusieurs produits ou des composants intégrés. Le choix de fournisseur ne dispense pas de définir le comportement attendu.

### 3.1 Policy Engine (PE)

Le Policy Engine évalue les demandes et décide d’accorder, refuser ou éventuellement interrompre l’accès selon la politique et les signaux disponibles. Il peut consulter les attributs d’identité, la posture d’un appareil, la classification d’une ressource, le risque, l’état du compte et des règles métier. Une décision doit être explicable : quel principal, quelle ressource, quel attribut et quelle règle ont conduit au résultat ?

Le moteur ne devrait pas deviner une permission en se fondant sur un seul indicateur arbitraire. Par exemple, une connexion depuis un bureau ne doit pas suffire à accorder l’accès administrateur. Un signal de posture manquant ne doit pas automatiquement être interprété comme une conformité parfaite. La politique doit prévoir le refus ou un accès de repli limité lorsque les éléments sont insuffisants.

### 3.2 Policy Administrator (PA)

Le Policy Administrator coordonne la mise en place ou la fin d’un chemin d’accès selon la décision. Selon l’implémentation, il peut ordonner l’établissement d’un tunnel, fournir un jeton de courte durée, configurer un point d’application ou publier un état de décision. Il ne doit pas créer une permission qui contredit celle du moteur.

### 3.3 Policy Enforcement Point (PEP)

Le Policy Enforcement Point applique la décision là où la demande entre dans le périmètre protégé ou là où le flux doit être contrôlé. Il peut être une passerelle, un proxy d’application, un agent sur un terminal, un contrôle d’accès API, un composant de service mesh ou un mécanisme intégré à l’application. Le point d’application doit échouer de manière sûre, vérifier l’authenticité et la fraîcheur de la décision et empêcher qu’une autre route contourne le contrôle.

~~~text
Demandeur -> PEP -> ressource protégée
             |
             | demande de décision / contexte
             v
      [Policy Engine]
             |
             | autoriser / refuser + conditions
             v
      [Policy Administrator]
             |
             | configuration / jeton / session limitée
             v
            PEP
             |
             +--> autorise le chemin conforme
             +--> bloque ou termine le chemin non conforme
~~~

Le schéma représente les fonctions logiques et non une séquence réseau obligatoire pour chaque requête. Les architectures varient. Certaines applications prennent des décisions directement dans le middleware ; d’autres s’appuient sur une passerelle et un service de politiques. L’exigence clé est de savoir qui décide et quel composant applique réellement la décision.

### 3.4 Sources d’information et de politique

La décision a besoin de données fiables. On peut retrouver l’annuaire et le fournisseur d’identité, la gestion des terminaux, l’inventaire des ressources, les informations de menace, la classification des données, les règles de conformité, les journaux et le système de tickets pour une élévation temporaire. La qualité dépend de la fraîcheur, de l’intégrité et de la disponibilité de ces sources.

~~~text
Identité / MFA ---------+
Posture de l'appareil --+
Sensibilité ressource --+--> Policy Engine --> décision
Risque / télémétrie ----+
Rôle / contrat ---------+
                          |
                          v
                    PEP : application
                          |
                          v
                    Journaux / métriques
~~~

Une source de posture qui n’a pas communiqué depuis plusieurs jours ne doit pas forcément être traitée comme si elle venait de vérifier l’appareil à l’instant. Les données peuvent être indisponibles, retardées ou erronées. La politique doit définir les seuils de fraîcheur et ce que l’on fait quand un système d’identité ou de posture tombe en panne.

### 3.5 Disponibilité et mode de défaillance

Le moteur de décision et le point d’application peuvent devenir des dépendances critiques. Une architecture doit définir ce qui se passe lors d’une panne : refuser l’accès sensible, autoriser un accès minimal préalablement établi, utiliser une décision en cache pendant une durée bornée ou basculer vers une instance redondante. Le choix dépend de la ressource et de l’impact métier ; il ne doit pas être improvisé pendant l’incident.

Pour les accès à fort impact, une politique « fail open » incontrôlée peut transformer une panne du moteur en ouverture générale. Pour des usages où une interruption met en danger la sécurité physique, un refus universel peut aussi être inacceptable. Il faut définir une procédure d’urgence spécifique, limitée, contrôlée, testée et journalisée.

## 4. Les cinq piliers du modèle de maturité CISA

Le modèle de maturité Zero Trust de la CISA décrit cinq piliers et des capacités transverses. Il s’agit d’un cadre de progression, pas d’une architecture technique unique à copier. Les piliers se renforcent mutuellement ; les progrès purement réseau ne compensent pas une identité machine faible ou des données sans classification.

### 4.1 Identité

Le pilier identité couvre les utilisateurs, les groupes, les comptes privilégiés, les comptes de service, les identités externes, les informations d’authentification et les cycles de vie. Une identité doit être créée avec un propriétaire, une justification, une portée et une date de revue. Lorsqu’une personne quitte l’organisation, ses accès doivent être retirés de manière cohérente. Un compte dormant ou orphelin constitue une dette de sécurité.

Les rôles permanents devraient être réduits. Utilisez des permissions spécifiques, une séparation des tâches et une élévation temporaire pour les opérations d’administration. Le MFA est important, mais tous les facteurs n’ont pas la même résistance au phishing. Pour les comptes à fort impact, privilégiez des moyens résistants au phishing lorsque l’organisation peut les prendre en charge.

### 4.2 Appareils

Le pilier appareils porte sur l’inventaire, l’identité du terminal, sa gestion, sa configuration, les mises à jour, le chiffrement, les mécanismes de protection et la télémétrie. Un appareil n’est pas conforme uniquement parce qu’il s’est enregistré une fois. Il faut préciser quels signaux sont contrôlés et à quelle fréquence : version prise en charge, protection active, chiffrement, état de conformité et statut de gestion.

La posture ne doit pas être traitée comme une vérité absolue. Un appareil conforme peut être compromis entre deux évaluations. Les signaux doivent alimenter une décision contextualisée, avec des actions comme autoriser, demander une preuve supplémentaire, limiter à des ressources non sensibles ou bloquer. Les appareils personnels et non gérés demandent souvent des politiques différentes.

### 4.3 Réseau et environnement

Le pilier réseau couvre la segmentation, l’accès distant, les contrôles de chemin, la résolution des flux et la réduction de la portée du mouvement latéral. Il ne consiste pas uniquement à ajouter des sous-réseaux. Une règle de microsegmentation devrait correspondre à un besoin métier et à un flux légitime : service A vers API B sur un port et une direction définis. Les règles doivent être observables, maintenues et testées.

~~~text
Avant
VPN --> réseau général --> serveurs multiples

Après
Utilisateur / terminal évalué
    |
    +--> application autorisée via un point d'accès
    |
    X--> base de données non exposée au poste
    X--> interface d'administration non nécessaire
    |
Service applicatif identifié
    |
    +--> base de données sur un flux spécifique
~~~

### 4.4 Applications et charges de travail

Les services, applications, conteneurs, fonctions serverless, automatisations et processus doivent avoir une identité propre. Évitez les secrets partagés à longue durée de vie entre plusieurs services. Une application devrait disposer seulement des permissions nécessaires et communiquer avec les services explicitement autorisés. Les identités de charge de travail sont souvent plus adaptées qu’un mot de passe d’utilisateur réutilisé par un script.

L’architecture doit réduire la confiance implicite entre microservices. Le fait que deux conteneurs partagent un cluster ou un réseau virtuel n’implique pas qu’ils doivent pouvoir se joindre. Un service mesh ou une couche d’identité de service peut aider à appliquer des communications chiffrées et des politiques cohérentes, mais il faut encore contrôler les routes, les autorisations métier et la gestion des certificats.

### 4.5 Données

Le pilier données commence par l’inventaire et la classification. Les données peuvent être publiques, internes, confidentielles ou hautement sensibles selon la politique de l’organisation. La classification détermine où elles peuvent être stockées, qui peut les lire, comment elles sont partagées, chiffrées, sauvegardées, conservées et supprimées. Sans classement, la politique est forcée de traiter toutes les données de la même manière.

~~~text
Catalogue de données
    |
    +--> classe de sensibilité
    +--> propriétaire métier
    +--> emplacement / copies
    +--> lecteurs et écrivains autorisés
    +--> clés et mécanismes de chiffrement
    +--> conservation et suppression
    +--> journaux d'accès et alertes
~~~

Un accès à une application ne signifie pas que toutes les données qu’elle contient sont visibles. Les autorisations doivent descendre au niveau des fonctions, objets et opérations lorsqu’il est nécessaire. Des exports, caches, copies de sauvegarde, fichiers temporaires et index de recherche peuvent exposer les mêmes informations que la base principale. La protection doit suivre les copies.

### 4.6 Capacités transverses

La CISA décrit trois capacités transverses qui soutiennent les piliers : **visibilité et analytique**, **automatisation et orchestration**, et **gouvernance**. Elles assurent que les décisions s’appuient sur les bons signaux, que les réponses ne dépendent pas uniquement d’actions manuelles et que les politiques restent compatibles avec les obligations et les risques.

~~~text
                    [Gouvernance]
                         |
[Identité] [Appareils] [Réseau] [Applications] [Données]
      \         |        |         |          /
       \--------+--------+---------+---------/
                         |
              [Visibilité et analytique]
                         |
             [Automatisation / orchestration]
                         |
                 réponse et amélioration
~~~

La visibilité n’est pas la collecte indiscriminée de tout ce qui est techniquement possible. Les événements doivent être utiles, proportionnés, protégés et conservés selon les règles applicables. L’automatisation ne doit pas pouvoir accorder des privilèges sans garde-fous. La gouvernance doit identifier les responsables, les exceptions, les risques acceptés, les exigences de confidentialité et les preuves de contrôle.

## 5. Identité utilisateur et authentification forte

### 5.1 Fournisseur d’identité et fédération

Un fournisseur d’identité (IdP) centralise une partie des preuves d’identité et peut émettre des assertions ou jetons pour des applications. La fédération permet à une application de s’appuyer sur une identité établie par un fournisseur de confiance. Les protocoles tels que SAML ou OpenID Connect servent à différents modèles de fédération. La configuration, la validation des audiences, des signatures, des émetteurs, des délais et des redirections doit être correcte.

La centralisation améliore la cohérence, mais augmente l’impact potentiel d’une compromission de l’IdP. Protégez les comptes administratifs, appliquez une authentification forte, limitez les permissions, surveillez les modifications de configuration et préparez un processus de récupération. Les applications doivent refuser des assertions invalides ou destinées à une autre audience. Un jeton signé n’est pas automatiquement autorisé pour toutes les ressources.

### 5.2 MFA résistant au phishing

Le MFA réduit le risque qu’un mot de passe volé suffise à ouvrir une session. Un code à usage unique peut améliorer la sécurité mais peut rester vulnérable à des techniques de phishing en temps réel. Les authentifications liées au domaine de confiance et les clés cryptographiques modernes peuvent offrir une résistance supérieure. La méthode doit être adaptée aux capacités, à l’accessibilité et aux scénarios de secours.

Une exception MFA doit être visible, limitée et revue. Évitez de créer un compte de secours permanent qui ignore tous les contrôles. Les procédures de récupération doivent vérifier l’identité de manière adaptée au risque et prévenir la réinitialisation frauduleuse d’un facteur. Les changements d’authentificateur et les nouvelles sessions privilégiées méritent une surveillance particulière.

### 5.3 Accès privilégié et JIT

La gestion des accès privilégiés (PAM) réduit la présence de secrets et de permissions d’administration permanentes. L’accès juste-à-temps (JIT) accorde une élévation pour une fenêtre courte lorsque le besoin est justifié. L’accès juste-suffisant (JEA) limite les commandes ou opérations disponibles à la tâche. Ces idées sont complémentaires : un accès temporaire peut rester trop puissant s’il donne tous les droits d’administrateur sur tous les systèmes.

~~~text
Demande d'élévation
       |
       v
Identité et MFA vérifiés
       |
       v
Ticket / motif / ressource / durée
       |
       v
Approbation selon le risque
       |
       v
Droit ciblé et temporaire
       |
       v
Session surveillée et journalisée
       |
       v
Expiration / révocation automatique
~~~

Les secrets privilégiés doivent être protégés, renouvelés et attribués à une tâche ou une personne identifiée. Les comptes administrateurs doivent être séparés des comptes de travail ordinaires. Les opérations d’urgence doivent se faire selon un modèle « break glass » : accès rare, protection renforcée, durée limitée, alertes immédiates, revue a posteriori et test régulier de la procédure.

## 6. Identités machines, applications et services

### 6.1 Pourquoi les comptes de service sont critiques

Les scripts et applications utilisent parfois un mot de passe d’utilisateur, un jeton permanent ou une clé partagée. Ces secrets peuvent finir dans un dépôt, un journal, une image de conteneur ou un fichier de configuration. Il faut préférer une identité de charge de travail attribuée à un service précis, des certificats gérés ou des jetons à durée de vie limitée, selon l’environnement.

~~~text
Pipeline de déploiement
       |
       | identité dédiée au pipeline
       v
Registre de conteneurs
       |
       | identité de charge de travail
       v
Service pédagogique
       |
       | droit SELECT limité / API autorisée
       v
Base de données des cours
~~~

Ne donnez pas au pipeline la capacité d’administrer tous les comptes cloud si son rôle est de publier une seule application. Ne réutilisez pas le même secret dans le test et la production. Les identités machine doivent avoir un propriétaire, une audience, des permissions, une durée, un mécanisme de rotation et une procédure de révocation.

### 6.2 mTLS et identité de service

Le TLS mutuel (mTLS) permet aux deux extrémités d’un canal TLS de présenter et vérifier des certificats. Il peut aider un service à authentifier son interlocuteur, notamment dans les communications machine-à-machine. Il ne remplace pas nécessairement l’autorisation applicative : un service connu peut demander une action qui dépasse sa permission. Les certificats exigent une gestion du cycle de vie, des autorités de confiance, des identités cohérentes, une révocation ou expiration et une surveillance des erreurs.

~~~text
Service A -- certificat client --> Proxy / Service B
    |                                  |
    | vérifie l'identité du serveur    | vérifie l'identité du client
    |                                  |
    +---------- canal TLS -------------+
                     |
                     v
        politique A -> B : action limitée
~~~

Un service mesh peut automatiser une partie de l’identité de service, du chiffrement et des politiques réseau. Il ne doit cependant pas être décrit comme une solution magique. Une mauvaise configuration du maillage, une autorité compromise, des permissions globales ou des composants hors du mesh peuvent maintenir des chemins non contrôlés. La couverture doit être documentée.

### 6.3 Secrets, jetons et rotation

Les jetons doivent être limités par audience, permission et durée. Les jetons de rafraîchissement demandent une protection spécifique et des règles de rotation. Les clés doivent vivre dans un gestionnaire de secrets ou un mécanisme de confiance équivalent, jamais dans les images publiques ou les dépôts. Les secrets partagés et leur inventaire doivent être réduits progressivement.

Le retrait d’un secret exige plus que l’effacement du fichier. Il faut le révoquer, remplacer les consommateurs, examiner les journaux pour détecter un usage suspect et vérifier les copies et sauvegardes. Les rotations doivent être testées pour éviter de bloquer toute l’application si un fournisseur ou un service dépend encore d’une ancienne clé.

## 7. Posture des appareils et accès adaptatif

### 7.1 Évaluer le terminal

Une décision peut tenir compte de la gestion du terminal, du niveau de correctif, de la protection endpoint, du chiffrement disque, de l’état de la configuration et de l’intégrité de l’identité machine. Définissez une politique par catégorie de ressource. Pour consulter une documentation publique, un appareil personnel peut suffire ; pour administrer une plateforme de données, un poste géré et contrôlé peut être obligatoire.

~~~text
Signal de posture
     |
     +--> frais et valide ?
     +--> appareil connu et attribué ?
     +--> mises à jour prises en charge ?
     +--> protection active ?
     +--> niveau de risque acceptable ?
     |
     v
Décision : autoriser / limiter / renforcer / refuser
~~~

### 7.2 Éviter la fausse précision

Un score de risque n’est pas une vérité universelle. Les signaux doivent être mesurés et expliqués. Si la posture d’un appareil est inconnue, la politique peut demander une vérification, limiter l’accès ou refuser une action sensible. Il serait dangereux de donner un score faible par défaut parce que le service de posture ne répond pas.

Les politiques adaptatives doivent être testées pour les faux positifs. Si chaque déplacement ou changement d’adresse IP invalide les sessions, les utilisateurs chercheront des contournements. Les changements significatifs incluent plutôt l’apparition de signaux de compromission, un nouvel appareil non géré, une révocation, une géolocalisation impossible à expliquer ou une demande qui sort nettement du comportement attendu.

### 7.3 Évaluer en continu de façon proportionnée

Le contrôle continu peut être événementiel ou périodique. Il peut reconsidérer l’accès après une alerte endpoint, une révocation d’identité, une élévation de privilège ou un changement de sensibilité de la ressource. Certaines sessions nécessitent une durée courte ; d’autres peuvent rester actives tant que les conditions restent vérifiées. La politique doit documenter sa fréquence et la latence maximale acceptable entre le signal et l’action.

## 8. Réseau, segmentation et accès distant

### 8.1 La microsegmentation

La microsegmentation réduit les flux permis entre applications ou charges de travail en appliquant des règles granulaires. Elle peut s’appuyer sur des pare-feu hôte, des contrôles cloud, des groupes de sécurité, des politiques d’orchestrateur ou des couches d’identité et de proxy. La granularité est utile seulement si l’inventaire est assez précis pour comprendre les flux et leurs propriétaires.

~~~text
Zone de services Web
  Frontend ----HTTPS----> API
                             |
                             | SQL/TLS : flux explicite
                             v
                       Base de données
                             X
                             X pas d'accès direct depuis le poste utilisateur

Plan d'administration
  Poste privilégié --> bastion / accès administré --> serveur ciblé
~~~

La première étape consiste à observer les flux existants, classer ceux qui sont légitimes et identifier les propriétaires. Bloquer immédiatement tous les flux inconnus peut interrompre des traitements critiques ou des sauvegardes. La stratégie doit inclure un mode d’observation, des essais, des exceptions temporaires, un calendrier de retrait et un mécanisme de retour arrière.

### 8.2 VPN traditionnel, ZTNA, SSE et SASE

Un VPN peut créer un tunnel chiffré vers un réseau ou une passerelle. Une solution ZTNA cherche généralement à donner accès à des applications spécifiques selon l’identité et la politique, plutôt qu’à ouvrir un accès réseau large. SSE regroupe des contrôles de sécurité livrés comme services cloud ; SASE associe ces fonctions à des capacités réseau de type SD-WAN. Les offres commerciales varient : il faut comparer les fonctions réelles au besoin au lieu de se fier à l’étiquette marketing.

Le VPN n’est pas intrinsèquement incompatible avec Zero Trust. Il peut rester une couche de transport, mais les ressources doivent appliquer des politiques explicites et les chemins doivent rester limités. Un tunnel ne devrait pas permettre de joindre une base de données directement si seul le portail a besoin de cette donnée. À l’inverse, une solution ZTNA n’offre aucune garantie si toutes les applications publiées sont accessibles à tous les utilisateurs.

### 8.3 Éviter les chemins parallèles

Quand une nouvelle passerelle est déployée, l’ancienne route peut rester accessible : adresse publique, port ouvert, règle de pare-feu héritée, interface d’administration oubliée ou accès par le VPN. Une architecture Zero Trust doit inventorier tous les chemins, pas uniquement le chemin « recommandé ». Une politique centrale ne sert à rien si un autre point d’entrée atteint la même ressource sans la consulter.

~~~text
Route officielle : Utilisateur -> ZTNA -> application
Route oubliée :   VPN ancien -> réseau interne -> application
Route oubliée :   URL publique directe -> serveur
Route oubliée :   poste admin -> protocole d'administration exposé
                  |
                  v
Audit : inventorier, tester, fermer ou contrôler chaque chemin
~~~

### 8.4 Contrôle des flux de sortie

La sécurité ne porte pas seulement sur le trafic entrant. Une charge de travail compromise peut essayer d’envoyer des données, de récupérer des outils ou de contacter des services de commande. Limitez les destinations sortantes selon le rôle, utilisez des résolveurs DNS et des proxys adaptés, contrôlez les flux nécessaires et surveillez les écarts. La liste doit rester maintenable pour les mises à jour et les dépendances légitimes.

## 9. Architecture applicative et autorisation de bout en bout

### 9.1 Passerelle n’est pas synonyme d’autorisation complète

Une passerelle peut vérifier l’identité, appliquer une politique d’accès initiale et journaliser les requêtes. Une fois le trafic transmis à l’application, celle-ci doit encore appliquer ses règles métier au niveau des fonctions et des objets. L’accès au portail ne signifie pas l’accès à chaque cours, dossier, export ou opération d’administration.

~~~text
Utilisateur -> IdP / MFA -> Passerelle d'accès
                                  |
                                  v
                                API
                                  |
                     identité + permission objet
                                  |
                                  v
                      service métier / base de données
                                  |
                                  v
                  réponse minimale et événement d'audit
~~~

Une politique peut se baser sur un groupe « formateurs » ; l’application vérifie ensuite que la personne peut modifier le cours et le groupe concernés. Cette défense en profondeur évite qu’une erreur de publication de groupe transforme toute l’organisation en administrateurs. L’autorisation doit être testée dans les routes d’API directes, exports, téléchargements et traitements asynchrones.

### 9.2 Jetons d’accès entre services

Un jeton signé ne constitue pas une autorisation universelle. Les services doivent valider l’émetteur, l’audience, l’expiration, la signature selon la configuration attendue et les droits. Il faut limiter les audiences pour qu’un jeton destiné à un service ne soit pas automatiquement valide partout. Le jeton doit porter assez de contexte pour la décision requise, sans embarquer de secrets ni trop de données personnelles.

Les autorisations doivent être actualisables. Si un utilisateur est retiré d’un rôle, une session longue ou un jeton valide pendant plusieurs heures peut conserver un droit dépassé. Une architecture doit choisir entre des jetons courts, introspection, révocation, vérification périodique ou contrôles dans le service. La latence et la disponibilité font partie du compromis.

### 9.3 Modes de déploiement et points d’application

Un point d’application peut être intégré à l’application, placé dans une passerelle devant les applications, installé auprès des charges de travail ou distribué dans une couche de service. Aucun modèle unique n’est adapté à toutes les contraintes. Les systèmes anciens peuvent ne pas prendre en charge une identité moderne ; un proxy ou un bastion peut constituer un contrôle intermédiaire, en attendant une modernisation.

~~~text
Application moderne :   IdP --> Proxy --> API avec autorisation métier
Service machine :       identité workload --> mTLS --> service ciblé
Système ancien :        utilisateur --> bastion contrôlé --> accès limité
Cloud :                 identité de workload --> politique cloud --> ressource
~~~

Un système historique derrière un proxy n’est pas automatiquement Zero Trust. Le proxy peut vérifier l’identité de l’utilisateur, mais si le serveur interne demeure accessible depuis un autre chemin ou utilise un compte partagé, il conserve une faiblesse. Les contrôles temporaires doivent inclure un plan de modernisation et une preuve que les chemins parallèles sont fermés.

## 10. Données et classification dans la décision

### 10.1 Classifier avant de contrôler

La classification doit être utilisable par les politiques. Une étiquette « confidentiel » ne doit pas être seulement un champ documentaire : elle doit influencer les droits, le partage, le chiffrement, le téléchargement et l’audit. Les propriétaires métier définissent la sensibilité ; les responsables de sécurité définissent les contrôles associés ; les équipes techniques les appliquent.

~~~text
Public        -> accès large avec contrôle d'intégrité
Interne       -> identité organisationnelle et usage métier
Confidentiel  -> autorisation par rôle/objet et audit
Très sensible -> MFA renforcé, accès limité, export restreint,
                 privilèges temporaires et alertes dédiées
~~~

Les classes doivent être simples à comprendre et leur usage vérifiable. Un système contenant des données de classes différentes peut appliquer la politique au niveau des lignes, fichiers ou opérations. Si la plateforme ne sait appliquer qu’une permission globale, il peut être nécessaire de séparer les ressources afin d’éviter une exposition excessive.

### 10.2 Protection pendant le cycle de vie

Une donnée est vulnérable durant la collecte, le traitement, le transport, le stockage, la sauvegarde, le partage et la suppression. Le chiffrement au repos et en transit est important, mais ne remplace pas la gestion des accès aux clés, la classification ou la suppression des copies. Les exports et les sauvegardes nécessitent des contrôles au même titre que les systèmes principaux.

Les clés sont des actifs à protéger séparément des données chiffrées. Limitez qui peut les utiliser, qui peut modifier la politique et qui peut restaurer une sauvegarde. Une personne qui contrôle à la fois les données, la clé et les journaux peut compromettre la valeur de séparation ; la séparation des tâches et les preuves indépendantes sont importantes pour les actifs critiques.

## 11. Visibilité, analytique et réponse

### 11.1 Quoi journaliser

Les événements utiles comprennent les décisions d’accès, les changements de politique, les changements de posture, les élévations temporaires, les échecs répétés, les révocations, les tentatives d’accès à des ressources sensibles, les accès machine-à-machine et les changements d’inventaire. Les événements devraient inclure une heure fiable, un identifiant de corrélation, le principal, la ressource, l’action, la décision, la règle correspondante et les informations de contexte nécessaires.

Évitez de journaliser les mots de passe, les cookies, les jetons complets, les clés privées ou les corps confidentiels sans justification et protection explicites. La centralisation augmente la valeur des journaux mais aussi l’impact d’une exposition. Contrôlez l’accès, l’intégrité, la conservation, les exports et la suppression.

### 11.2 Corrélation et signaux

Un événement isolé peut être normal. Une succession de décisions — authentification inhabituelle, appareil soudain non conforme, augmentation des refus d’accès, demande d’élévation puis export massif — peut révéler un risque élevé. La corrélation exige des identités stables, une horloge synchronisée et des schémas d’événement cohérents.

~~~text
Signal IdP : nouvelle connexion à risque élevé
             |
Signal appareil : conformité perdue
             |
Signal API : accès à des objets hors du profil habituel
             |
             v
Moteur de détection : corrélation et seuil adapté
             |
             v
Action : réauthentifier, réduire ou révoquer l'accès
             |
             v
Ticket d'incident + preuves + revue
~~~

L’analytique ne doit pas entraîner de décisions opaques ou injustifiables. Définissez ce qui déclenche une action automatique, ce qui exige une validation humaine et comment corriger les faux positifs. Un blocage de compte automatisé mal contrôlé peut provoquer un déni de service ou bloquer les équipes de réponse pendant un incident.

### 11.3 Réponse automatisée

Une automatisation peut révoquer un jeton, isoler un terminal, réduire une permission, désactiver une identité machine ou ouvrir un ticket. Les actions à fort impact doivent comporter des limites : approbation, conditions d’exécution, journalisation, procédure de retour arrière et identité propre à l’automatisation. L’automatisation doit elle-même être protégée avec le moindre privilège.

### 11.4 Horodatage, corrélation et confidentialité

Les systèmes doivent partager une référence temporelle fiable. Un décalage important rend difficile la reconstruction d’un incident. Utilisez des identifiants de corrélation qui suivent une opération à travers les couches sans incorporer de secrets. Les adresses IP et les identifiants de compte peuvent être des données personnelles selon le contexte ; la collecte et l’usage doivent respecter la politique de confidentialité et les obligations applicables.

## 12. Gouvernance, risques et indicateurs de maturité

### 12.1 Gouvernance

La gouvernance définit qui est propriétaire des ressources, qui peut approuver une exception, comment un risque est accepté, quand les droits sont revus et comment les politiques évoluent. Une exception sans date d’expiration devient souvent une règle permanente. Chaque exception doit documenter la raison métier, la ressource, le propriétaire, les compensations, le risque accepté, la date de revue et la date de fin.

Une politique générale doit rester cohérente avec la réalité. Si une équipe ne peut jamais utiliser le dispositif prévu, elle peut créer un compte partagé ou un tunnel parallèle. Mesurez les points de friction, simplifiez les parcours légitimes et traitez les cas hérités avec un plan et une date plutôt qu’avec une exemption éternelle.

### 12.2 Mesurer la progression

Utilisez des indicateurs qui reflètent une réduction de risque : proportion des ressources inventoriées et classifiées, comptes privilégiés sans MFA fort, pourcentage des accès sensibles avec décision explicite, durée moyenne de retrait des accès après départ, couverture des identités machine, délais de révocation, flux interdits détectés, accès de secours testés et proportion des exceptions arrivées à échéance.

~~~text
Indicateur                      Exemple d'objectif mesurable
Inventaire                      95 % des actifs critiques avec propriétaire
Comptes privilégiés             100 % avec MFA adapté
Accès permanents                baisse trimestrielle des droits superflus
Révocation                      délai maximal défini par la criticité
Flux applicatifs                flux critiques documentés et testés
Exceptions                     100 % avec propriétaire et expiration
Journaux                        événements critiques reçus et corrélés
Reprise                         test périodique du chemin d'urgence
~~~

Ces pourcentages sont des exemples de planification, pas des seuils universels imposés par le NIST ou la CISA. L’organisation doit sélectionner ses cibles selon la criticité, la réglementation, les ressources et le risque accepté. Un indicateur doit préciser son dénominateur, sa source de données, sa fréquence, son responsable et les cas exclus.

### 12.3 Modèle de maturité

Les modèles de maturité décrivent une progression allant de contrôles manuels et cloisonnés vers des politiques plus coordonnées, automatisées et adaptatives. Il ne faut pas chercher à atteindre le niveau le plus automatisé partout avant de sécuriser les actifs critiques. Une progression pragmatique commence souvent par les comptes privilégiés, les applications majeures, les données sensibles et les chemins d’accès les plus risqués.

~~~text
Étape 1 : inventaire et visibilité
       |
       v
Étape 2 : identité forte et moindre privilège
       |
       v
Étape 3 : points d'application sur les ressources critiques
       |
       v
Étape 4 : segmentation et politiques inter-services
       |
       v
Étape 5 : corrélation, révocation et automatisation contrôlée
       |
       v
Amélioration continue mesurée et réévaluée
~~~

La maturité n’est pas une ligne parfaitement uniforme. Une organisation peut disposer d’un excellent contrôle d’identité mais d’une visibilité réseau faible. Évaluez les piliers séparément, puis les capacités transverses, et fixez des priorités selon les chemins d’attaque et l’impact métier.

## 13. Stratégie de migration par étapes

### 13.1 Inventorier le réel

L’inventaire initial doit couvrir les applications, données, terminaux, identités, comptes de service, flux, réseaux, interfaces de gestion, fournisseurs et dépendances. Les diagrammes d’architecture sont utiles, mais ils doivent être confrontés aux flux observés, aux règles de pare-feu, aux DNS, aux configurations cloud et aux journaux. Un service oublié ne sera pas protégé par une politique qui ne le connaît pas.

### 13.2 Choisir un premier périmètre

Choisissez une application métier qui possède un propriétaire engagé, des utilisateurs identifiables, une architecture compréhensible et un risque significatif, mais où le retour arrière est possible. Définissez les critères de réussite avant le déploiement : routes couvertes, rôles, accès non autorisés refusés, latence acceptable, logs disponibles et procédure de secours testée.

~~~text
Pilote
  |
  +--> inventaire des utilisateurs et terminaux
  +--> cartographie des ressources et dépendances
  +--> matrice d'accès par rôle et action
  +--> définition des exceptions nécessaires
  +--> mode observation / test
  +--> application graduelle
  +--> mesure, correction et décision d'extension
~~~

### 13.3 Observer avant de bloquer

Le mode observation permet d’identifier les flux et usages légitimes avant de passer à l’application stricte. Il faut néanmoins fixer une date de sortie du mode observation ; sinon il devient une exception permanente. Les observations doivent être examinées avec les propriétaires métier, en distinguant les besoins réels des habitudes historiques et des flux inutiles.

### 13.4 Déploiement progressif et retour arrière

Introduisez la politique par groupes, applications ou environnements. Mesurez les refus inattendus, les incidents opérationnels et l’expérience utilisateur. Gardez les mécanismes existants qui restent nécessaires, mais évitez le double chemin non contrôlé. Le retour arrière doit restaurer une version définie, pas rouvrir tous les accès. Les commandes et procédures de restauration doivent être testées à l’avance.

### 13.5 Moderniser les systèmes hérités

Certains systèmes anciens ne comprennent ni fédération moderne, ni MFA, ni identité de charge de travail. On peut parfois placer un proxy, un bastion ou une passerelle devant eux, réduire les origines autorisées et imposer une identité en amont. Cela reste une solution de transition : le propriétaire doit documenter la portée résiduelle, les flux, le plan de modernisation et la date de revue.

## 14. Modèles de politiques et tests vérifiables

### 14.1 Une politique testable

Une politique devrait être exprimée sous une forme que l’équipe peut lire, versionner et tester. Les attributs peuvent inclure principal, rôle, ressource, action, posture, niveau de risque et durée. Les politiques doivent être déterministes autant que possible : même entrée de contexte, même décision, sauf si un signal explicite change.

~~~text
POLITIQUE : lecture du portail de cours
Principal : apprenant actif
Ressource : API de lecture des cours auxquels il est inscrit
Action    : GET /cours/{id}
Conditions :
  - identité vérifiée par l'IdP
  - MFA conforme au niveau de risque
  - session non expirée
  - inscription valide au cours demandé
  - risque inférieur au seuil défini
Décision :
  - autoriser la lecture des champs permis
  - refuser tout objet hors inscription
Journal :
  - principal, cours, action, décision, règle, correlation_id
~~~

### 14.2 Tester les cas positifs et négatifs

Pour chaque règle, testez au moins un cas autorisé, un cas refusé pour identité invalide, un cas refusé pour mauvaise ressource, un cas avec posture inconnue, un cas de révocation et un cas de panne d’une source de décision. Testez aussi les chemins secondaires : export, téléchargement, API administrative, tâches asynchrones, console cloud et accès de secours. Les règles doivent être revalidées après chaque changement d’application ou de rôle.

~~~text
Identité   Ressource           Posture    Attendu
Amina      son cours inscrit   conforme   autoriser lecture
Amina      cours non inscrit   conforme   refuser
Anonyme    cours privé         conforme   refuser
Admin      console admin       conforme   JIT + MFA + audit
Service X  API Y non prévue    conforme   refuser
Terminal   ressource critique inconnue   limiter ou refuser
~~~

### 14.3 Éviter les règles contradictoires

Un moteur de politique doit définir comment il traite les priorités, exceptions, règles de refus et permissions héritées. Une règle large qui autorise un groupe entier peut contredire une règle spécifique de refus si l’ordre d’évaluation est mal compris. Évitez de dépendre d’un ordre caché. Versionnez les politiques, faites une revue à deux personnes pour les droits critiques et gardez des tests qui documentent le comportement attendu.

### 14.4 Évaluer la fraîcheur des signaux

Une décision doit utiliser des informations suffisamment récentes. Un utilisateur désactivé dans l’annuaire mais encore présent dans un cache de plusieurs heures peut conserver un accès indésirable. Définissez les délais maximaux de propagation pour la révocation, les groupes, la posture et les attributs sensibles. Mesurez ces délais, car une garantie qui n’a jamais été testée peut être fausse en pratique.

## 15. Travaux pratiques corrigés

### TP 1 — Concevoir la politique d’accès d’Atlas Formation

**Objectif :** passer d’une règle réseau globale à des permissions contextualisées.

**Contexte de laboratoire :** Atlas Formation possède les rôles apprenant, formateur, support et administrateur. Les ressources sont le portail, l’API de cours, les résultats, l’administration de comptes et la base de données. Le VPN historique donne actuellement accès à plusieurs segments internes.

**Étape 1 : inventaire.** Listez les ressources, leurs propriétaires, leur sensibilité et les chemins d’accès existants. Ne considérez pas qu’un schéma réseau remplace un inventaire d’applications et de données. Marquez les ressources qui contiennent des résultats ou des données personnelles.

**Étape 2 : matrice des permissions.** Définissez les actions nécessaires par rôle et par ressource. Un apprenant peut consulter les cours auxquels il est inscrit et ses résultats ; il ne modifie pas les notes. Un formateur gère ses cours et les résultats de ses groupes. Le support peut diagnostiquer les problèmes sans lire toutes les données métier. L’administrateur accède aux opérations privilégiées par un parcours distinct et audité.

**Étape 3 : signaux contextuels.** Définissez l’identité, le MFA, la posture de l’appareil, le risque, l’état du compte et la durée de session requis pour chaque action. Un appareil inconnu peut accéder à une page publique, mais ne devrait pas automatiquement atteindre un panneau d’administration.

**Étape 4 : architecture et points d’application.** Identifiez le point de décision, le point d’application réseau ou proxy et les contrôles métier dans l’API. Supprimez l’accès direct du poste utilisateur à la base de données. Documentez les chemins historiques et la manière de les fermer.

~~~text
Matrice minimale
Apprenant : lire ses cours inscrits ; lire ses résultats
Formateur : lire et corriger les cours de ses groupes
Support   : diagnostiquer sans accès global aux données métier
Admin     : privilèges temporaires, MFA fort, audit et approbation
Service API : accès SQL limité au besoin applicatif
~~~

**Correction expliquée.** La politique ne doit pas autoriser « les utilisateurs du VPN » à atteindre toute l’infrastructure. Le VPN peut rester un moyen de transport, mais chaque ressource exige un contrôle adapté. Les permissions doivent couvrir actions et objets ; autrement, un apprenant pourrait modifier un identifiant de cours et lire les résultats d’un autre groupe. L’administration de comptes et l’accès aux données métier doivent être séparés pour éviter une élévation indirecte.

**Critères d’acceptation :** chaque ressource a un propriétaire et une classe de sensibilité ; la matrice couvre lecture, modification et administration ; chaque règle possède un test ; les chemins directs vers la base sont bloqués ou justifiés par un besoin documenté ; les exceptions sont datées.

### TP 2 — Définir les composants PE, PA et PEP

**Objectif :** dessiner le plan de décision et vérifier qu’une autorisation est effectivement appliquée.

**Étape 1 : choisir un cas.** Un formateur tente de publier une nouvelle version d’un cours depuis un terminal géré. Le moteur doit vérifier l’identité, le MFA, la relation du formateur au cours, l’état du compte et la posture. La publication est interdite depuis un terminal non conforme.

**Étape 2 : attribuer les responsabilités.** Le PE évalue la politique et les signaux. Le PA coordonne l’accès ou sa terminaison selon la décision. Le PEP bloque ou autorise le chemin. L’API reste responsable de l’autorisation métier sur le cours et de la validation des données.

**Étape 3 : prévoir les échecs.** Que se passe-t-il si le service de posture est indisponible, si la décision expire ou si l’API n’arrive plus à vérifier l’identité ? Pour la publication, qui modifie le contenu, la politique peut refuser l’action si les preuves essentielles manquent. Toute exception de continuité doit être limitée et journalisée.

**Étape 4 : tester les dérivations.** Envoyez la requête par le chemin officiel, puis essayez les routes directes connues. Le test doit confirmer que le serveur interne ne peut pas être atteint par une route qui saute le contrôle de politique.

~~~text
Formateur -> PEP -> PE
                     |
                     +--> vérifie IdP / MFA
                     +--> consulte posture
                     +--> vérifie rôle et ressource
                     |
                     v
               PA coordonne
                     |
                     v
          PEP applique la décision
                     |
                     v
             API vérifie encore
             l'autorisation métier
~~~

**Correction expliquée.** Les fonctions PE, PA et PEP peuvent être implémentées dans des produits différents ; elles doivent néanmoins former un ensemble cohérent. Le PEP doit appliquer la décision, pas seulement l’enregistrer. Si l’API peut être contactée directement en contournant la passerelle, le contrôle est incomplet. Si le service de posture est indisponible, l’organisation doit appliquer la règle prévue pour ce niveau de risque et ne pas convertir l’incertitude en autorisation illimitée.

**Critères d’acceptation :** les responsabilités sont assignées ; la décision indique les facteurs évalués ; l’application du refus est testée ; expiration et révocation sont testées ; panne et mode de secours sont documentés.

### TP 3 — Microsegmentation progressive d’une application

**Objectif :** réduire les flux réseau sans interrompre les dépendances nécessaires.

**Contexte :** une application possède un frontend, une API, une base de données, un système de sauvegarde et un serveur de supervision. Les postes de travail peuvent actuellement joindre certains serveurs sur un trop grand nombre de ports.

**Étape 1 : observer.** Recueillez les flux pendant une période représentative, puis consultez les journaux applicatifs et les propriétaires. Différenciez les flux permanents, les opérations de déploiement, les sauvegardes, les tests et l’administration ponctuelle.

**Étape 2 : modéliser les besoins.** Le navigateur ou le poste utilisateur doit rejoindre le point d’accès au frontend ; le frontend appelle l’API ; l’API accède à la base sur un port spécifique ; le service de sauvegarde utilise son propre rôle et ses créneaux prévus ; le système de supervision accède uniquement aux interfaces nécessaires.

**Étape 3 : définir et tester les règles.** Écrivez les règles de refus par défaut et les exceptions strictement nécessaires. Testez dans un environnement pilote. Surveillez les flux refusés inattendus, puis effectuez le basculement par groupe. Gardez une procédure de retour arrière qui restaure une version définie des règles et ne réouvre pas globalement le réseau.

~~~text
Poste utilisateur --> Frontend HTTPS
Frontend ----------> API HTTPS
API ---------------> Base de données : port documenté
Sauvegarde --------> Base : fenêtre et identité contrôlées
Supervision -------> métriques autorisées
Poste utilisateur -X-> Base de données
API ---------------X-> réseau d'administration général
~~~

**Correction expliquée.** La microsegmentation commence par comprendre les flux, pas par bloquer les connexions inconnues au hasard. Le chemin direct du poste à la base n’est pas nécessaire pour une utilisation normale ; il doit être supprimé. Les sauvegardes et la supervision possèdent des besoins spécifiques, à limiter en source, destination, port et identité. Il faut surveiller les flux avant et après la mise en œuvre, car un flux peu fréquent peut correspondre à un traitement mensuel important.

**Critères d’acceptation :** chaque flux autorisé a un propriétaire et une raison ; les accès interdits sont effectivement bloqués ; les sauvegardes et la supervision continuent ; les règles sont versionnées ; le plan de retour arrière est essayé.

### TP 4 — Accès privilégié juste-à-temps et réponse automatisée

**Objectif :** diminuer les privilèges permanents et contrôler une élévation administrative.

**Étape 1 : séparer les identités.** L’administrateur possède un compte ordinaire pour le travail quotidien et un compte privilégié réservé aux tâches d’administration. L’authentification forte est exigée pour le compte privilégié. Les comptes partagés sont éliminés ou traités comme une exception transitoire très encadrée.

**Étape 2 : formaliser la demande.** Le demandeur précise la cible, l’action, le motif, le ticket, la durée et le niveau d’approbation requis. Le rôle temporaire donne uniquement les permissions nécessaires. Une demande pour redémarrer un service ne doit pas accorder automatiquement l’administration de tout le cloud.

**Étape 3 : activer et terminer.** Le mécanisme provisionne le droit, enregistre le début, surveille la session et retire le droit à l’expiration. La révocation doit aussi fonctionner lorsque le compte est désactivé ou qu’un signal de compromission est reçu.

**Étape 4 : réponse automatisée contrôlée.** Une alerte de risque peut révoquer un jeton ou suspendre une session selon une règle définie. L’automatisation a sa propre identité et ses propres permissions. Les actions graves nécessitent une approbation ou des conditions documentées, et chaque action est auditée.

~~~text
Besoin -> demande JIT -> vérification identité/MFA
      -> approbation et portée -> privilège temporaire
      -> session auditée -> expiration ou révocation
                                      |
                                      v
                        alerte / ticket / revue postérieure
~~~

**Correction expliquée.** L’accès temporaire réduit la durée d’exposition, mais il ne suffit pas si la portée est trop large. Le mécanisme doit retirer les droits réellement attribués, pas seulement masquer le rôle dans l’interface. La réponse automatisée doit utiliser un compte séparé et ne disposer que des permissions nécessaires pour les opérations autorisées. Un accès d’urgence doit être testé et revu après chaque utilisation.

**Critères d’acceptation :** pas de privilège permanent sans justification ; approbation proportionnée au risque ; périmètre et durée déterminés ; journaux sans secrets ; expiration et révocation testées ; procédure d’urgence testée.

## 16. Exercices corrigés

### Exercice 1 — Définir Zero Trust

Une entreprise affirme avoir Zero Trust parce que tous ses utilisateurs passent par un VPN avec MFA.

**Correction :** le VPN et le MFA sont des composants utiles, mais ne suffisent pas. Il faut des décisions d’accès explicites à la ressource, des autorisations adaptées à l’action, une posture évaluée lorsque pertinente, des points d’application et une observabilité cohérente. Vérifiez également les chemins qui contournent le VPN.

### Exercice 2 — Le poste est sur le LAN

Un poste connecté au réseau de bureau reçoit automatiquement l’accès à toutes les applications internes.

**Correction :** la localisation interne n’est pas une preuve suffisante de confiance. La politique doit distinguer les ressources et actions ; les terminaux doivent être identifiés et évalués selon le risque. L’accès à une base doit être réservé aux services qui en ont besoin.

### Exercice 3 — Session déjà authentifiée

Un utilisateur a réussi le MFA hier ; l’application lui accorde aujourd’hui une opération privilégiée sans autre vérification.

**Correction :** le contexte et l’âge de la preuve comptent. Une opération à fort impact peut exiger une authentification récente, une élévation JIT, une posture conforme et une autorisation spécifique. Le MFA ne remplace pas la permission métier.

### Exercice 4 — Qui décide et qui applique ?

Une passerelle enregistre une décision « refuser » mais transmet tout de même la requête à l’application.

**Correction :** le point d’application ne respecte pas la décision. Il doit bloquer le chemin ou terminer l’accès selon la politique. Vérifiez les chemins directs pour éviter le contournement et ajoutez un test de refus effectif.

### Exercice 5 — Service mesh et autorisation

Tous les services possèdent un certificat mTLS, et l’équipe considère qu’ils peuvent s’appeler librement.

**Correction :** mTLS permet d’authentifier les extrémités du canal selon les certificats et la confiance configurée ; il n’accorde pas toutes les permissions. Il faut une politique service-à-service limitée, une autorisation métier et une gestion rigoureuse des certificats.

### Exercice 6 — Compte de service partagé

Trois applications utilisent la même clé à longue durée de vie parce que cela facilite le déploiement.

**Correction :** attribuez une identité à chaque charge de travail, limitez l’audience et les droits, réduisez la durée des jetons, gérez le secret et planifiez une rotation. Une compromission ne doit pas donner un accès indifférencié aux trois applications.

### Exercice 7 — Appareil inconnu

Le service de posture ne répond pas ; le moteur traite cette absence comme une conformité parfaite pour éviter les refus.

**Correction :** une absence de signal n’équivaut pas à une conformité. Définissez une politique par niveau de risque : refus pour les opérations critiques, limitation ou vérification supplémentaire pour d’autres usages, accès public sans privilège si justifié. Mesurez la disponibilité du service de posture.

### Exercice 8 — Microsegmentation par sous-réseau uniquement

Une équipe crée beaucoup de VLAN, mais tous les serveurs de ces VLAN peuvent communiquer librement.

**Correction :** la séparation logique peut aider, mais n’applique pas nécessairement la granularité attendue. Définissez les flux requis, appliquez des règles entre charges de travail et testez les chemins directs. La documentation de chaque flux est aussi importante que le nombre de sous-réseaux.

### Exercice 9 — Exceptions sans date de fin

Un fournisseur a besoin d’un accès temporaire et obtient une règle qui n’a jamais de date d’expiration.

**Correction :** l’exception doit avoir un propriétaire, une justification, une portée, des contrôles compensatoires, une approbation et une échéance. Elle doit être supprimée ou revue à la date prévue, avec une alerte avant expiration.

### Exercice 10 — Journalisation trop large

Le service de politique enregistre chaque jeton complet pour faciliter les investigations.

**Correction :** les journaux ne doivent pas devenir un dépôt de secrets. Utilisez un identifiant de corrélation, des claims non sensibles nécessaires au diagnostic, la décision, la ressource et la règle. Masquez ou excluez les jetons, cookies et clés, puis protégez l’accès et l’intégrité des événements.

### Exercice 11 — Décision en cache

Un point d’application met en cache une autorisation administrateur pendant une journée, même après révocation.

**Correction :** la durée de cache n’est pas compatible avec l’impact si une révocation doit être rapide. Réduisez la durée, introduisez un mécanisme de révocation ou d’invalidation, et testez le délai maximal entre révocation et refus effectif. Le délai acceptable doit être défini par la criticité.

### Exercice 12 — Règles contradictoires

Une règle autorise tous les employés à lire un portail ; une règle spécifique interdit l’accès aux dossiers confidentiels, mais le moteur ne définit pas les priorités.

**Correction :** la sémantique des règles doit être explicite. Définissez une politique de priorité ou un modèle qui évite les conflits. Écrivez un test qui prouve que le dossier confidentiel reste inaccessible au rôle général.

### Exercice 13 — Administrateur permanent

Un technicien dispose d’un rôle global permanent, car son équipe l’utilise rarement.

**Correction :** un usage rare justifie plutôt un accès temporaire. Limitez la ressource, l’action et la durée, exigez une authentification forte, une justification et un audit. Gardez un mécanisme d’urgence encadré plutôt qu’une permission permanente.

### Exercice 14 — Tout automatiser dès le départ

La direction exige que chaque décision de risque déclenche immédiatement une isolation automatique du terminal.

**Correction :** l’automatisation doit être introduite progressivement et évaluée contre les faux positifs. Commencez par des alertes et des actions réversibles ou à faible impact, mesurez la qualité, puis automatisez les actions plus graves avec des garde-fous, une approbation ou des seuils adaptés.

### Exercice 15 — Application ancienne derrière un proxy

Un ancien serveur ne prend pas en charge les identités modernes. Un proxy vérifie le MFA, mais le serveur reste accessible depuis le LAN.

**Correction :** le contrôle du proxy peut réduire l’exposition mais la route directe contourne la politique. Fermez ou limitez ce chemin, utilisez un bastion ou un proxy contrôlé, documentez la dette héritée et fixez un plan de modernisation.

### Exercice 16 — Ressource non inventoriée

Un serveur découvert dans les journaux n’a pas de propriétaire et n’apparaît pas dans le catalogue d’actifs.

**Correction :** attribuez un propriétaire, identifiez les données et dépendances, évaluez les risques puis restreignez l’accès jusqu’à clarification. L’absence d’inventaire empêche une politique cohérente. Ajoutez un processus de découverte et de revue périodique.

### Exercice 17 — Accès hors du profil habituel

Un utilisateur demande beaucoup de dossiers très sensibles à une heure inhabituelle ; son identité et son appareil sont pourtant valides.

**Correction :** le risque dépend de la combinaison des signaux et de l’action. Une demande anormale peut nécessiter une vérification renforcée, une limite de volume, une approbation ou un refus temporaire. Il faut documenter les seuils et conserver les événements utiles sans conclure automatiquement à une attaque.

### Exercice 18 — Migration totale en une nuit

Un projet prévoit d’activer des politiques de refus sur tous les réseaux et toutes les applications en une seule fenêtre.

**Correction :** ce plan crée un risque opérationnel important et ne permet pas d’observer les dépendances. Faites l’inventaire, choisissez un périmètre pilote, observez les flux, testez, déployez progressivement et préparez un retour arrière. Les services critiques nécessitent une validation métier et des fenêtres adaptées.

### Exercice 19 — KPI de licences

Un tableau de bord mesure le succès par le pourcentage d’utilisateurs couverts par le produit Zero Trust, sans mesurer les accès refusés ou les exceptions.

**Correction :** l’adoption d’un outil est un indicateur d’avancement, pas de sécurité réelle. Mesurez la couverture des ressources, les contrôles d’autorisation, la durée de révocation, les chemins non gérés, la qualité des journaux et les exceptions expirées. Définissez un dénominateur transparent et un responsable pour chaque métrique.

### Exercice 20 — Accès d’urgence

L’unique compte de secours n’a jamais été testé et son mot de passe est connu de toute l’équipe.

**Correction :** l’accès d’urgence doit être contrôlé comme une ressource critique. Séparez l’identité, protégez le secret, limitez l’accès, alertez à chaque utilisation, documentez la procédure et testez-la périodiquement. Une procédure non testée peut échouer au moment où elle est indispensable.

## 17. Défi final corrigé — transformer l’accès d’Atlas Formation

### Situation

Atlas Formation veut moderniser l’accès à son portail, son API, sa base de résultats et son environnement cloud. Le VPN historique permet aux employés d’atteindre trop de serveurs. Certains comptes de service utilisent des secrets permanents, les administrateurs possèdent des rôles larges et plusieurs journaux ne sont pas corrélés. La direction demande une feuille de route Zero Trust sur six mois, sans interrompre les cours.

### Travail demandé

1. Définir les actifs prioritaires, les propriétaires et les frontières de confiance.
2. Décrire une architecture logique intégrant PE, PA et PEP et les sources de contexte.
3. Construire des politiques pour les apprenants, formateurs, services et administrateurs.
4. Définir la migration réseau et la stratégie pour les anciens accès.
5. Proposer des indicateurs, des tests et des conditions d’extension du pilote.

### Correction détaillée

**1. Actifs et priorités.** Les résultats, les identités, les secrets cloud, les consoles d’administration, les données personnelles et la base de résultats sont des actifs sensibles. Les propriétaires métier doivent être identifiés. Les flux essentiels comprennent le navigateur vers le portail, le portail vers l’API, l’API vers la base, les services de sauvegarde, le plan d’administration, le fournisseur d’identité et les outils de supervision. Les accès directs au stockage et à la base depuis les postes doivent être évalués puis restreints.

**2. Architecture de référence.** Le PE évalue l’identité, le MFA, la posture, le rôle, la ressource et le niveau de risque ; le PA coordonne l’accès ou sa terminaison ; le PEP applique la décision à l’entrée de la ressource. La passerelle et les contrôles applicatifs peuvent fournir plusieurs points d’application. L’API vérifie les droits métier au niveau de l’objet même après une autorisation d’accès initiale. L’IdP, l’inventaire, la gestion des terminaux, la classification des données et les journaux alimentent le contexte.

**3. Politiques.** Un apprenant ne consulte que ses cours inscrits et ses résultats. Un formateur ne gère que les cours de ses groupes. Le service API accède à la base avec une identité de charge de travail et des droits limités. L’administrateur utilise un compte séparé, MFA renforcé, élévation temporaire, ressource ciblée et audit. Un terminal inconnu ne reçoit pas les mêmes droits qu’un appareil conforme pour une opération critique.

**4. Migration.** Le premier mois sert à inventorier les actifs, propriétaires, comptes et flux. Le deuxième établit la matrice d’accès et les règles pour un pilote. Les mois suivants déploient l’identité forte, la protection de l’accès au portail, la microsegmentation entre frontend, API et base, puis la gestion JIT des privilèges. La télémétrie existante est corrélée. Les anciens chemins VPN sont restreints au fur et à mesure que les tests de remplacement passent. Les systèmes hérités qui ne peuvent pas être modernisés reçoivent un proxy ou un bastion, un inventaire des risques et un plan de retrait daté.

**5. Indicateurs et conditions d’extension.** Mesurez les ressources critiques avec un propriétaire, les accès directs à la base, les privilèges permanents, les comptes de service inventoriés, les délais de révocation, les flux non documentés et les exceptions sans échéance. Les tests de pilote incluent le cas autorisé, l’accès inter-utilisateur, la révocation, la posture inconnue, la panne d’une source de politique, les accès directs et l’expiration JIT. N’étendez le pilote que lorsque les refus sont réellement appliqués, les services fonctionnent, les journaux sont exploitables et le retour arrière est vérifié.

~~~text
Feuille de route illustrative
Mois 1 : inventaire, classification, propriétaires et flux
Mois 2 : politiques, identités fortes, sélection du pilote
Mois 3 : pilote portail/API et tests d'accès
Mois 4 : segmentation des flux et identités machines
Mois 5 : accès privilégié JIT, corrélation des événements
Mois 6 : audits, correction, indicateurs et décision d'extension

Porte de sortie pour chaque étape :
contrôles testés + impact connu + journaux utiles
+ propriétaire métier + retour arrière vérifié
~~~

Une architecture Zero Trust réussie n’est pas une case cochée à la fin du sixième mois. La feuille de route établit un système de contrôles qui s’améliore à partir des incidents, des changements d’actifs et de l’évolution des besoins. Les décisions et exceptions restent documentées, et les protections continuent d’être testées après l’ouverture du projet à de nouveaux périmètres.

## 18. Checklist de validation d’une architecture Zero Trust

- [ ] Les ressources critiques, les propriétaires, les flux et la classification sont connus.
- [ ] Aucun accès n’est accordé uniquement parce que le demandeur est sur un réseau interne ou un VPN.
- [ ] L’authentification est séparée de l’autorisation par ressource et par action.
- [ ] Les règles PE, le rôle PA et les responsabilités PEP sont documentés.
- [ ] Les points d’application bloquent réellement les accès refusés et les routes alternatives sont recensées.
- [ ] Les comptes privilégiés utilisent une authentification adaptée, des identités séparées et une élévation limitée.
- [ ] Les identités machines ont un propriétaire, une audience et des permissions minimales.
- [ ] Les certificats, jetons et secrets suivent un cycle de vie avec rotation et révocation.
- [ ] La posture des appareils est évaluée avec des seuils de fraîcheur et des règles en cas de signal inconnu.
- [ ] Les flux entre applications et services sont limités et testés.
- [ ] La classification des données contrôle aussi les exports, sauvegardes et copies.
- [ ] Les journaux couvrent les décisions, changements de politique, élévations et événements sensibles sans stocker les secrets.
- [ ] Les mécanismes d’automatisation sont eux-mêmes protégés et leurs actions réversibles lorsque possible.
- [ ] Les exceptions ont un propriétaire, une justification, un contrôle compensatoire et une échéance.
- [ ] La migration se fait par étapes, avec observation, tests métier et retour arrière.
- [ ] Les indicateurs ont une source, un dénominateur, une fréquence et un responsable.
- [ ] La procédure d’urgence a été testée et chaque utilisation déclenche une revue.
- [ ] Les exigences sont reliées à des preuves et les contrôles sont retestés après changement.

## 19. Glossaire

**Architecture Zero Trust (ZTA) :** architecture qui supprime la confiance implicite basée sur la seule localisation réseau et applique des décisions d’accès explicites aux ressources.  
**PE, Policy Engine :** composant logique qui évalue une demande et produit une décision selon la politique.  
**PA, Policy Administrator :** composant logique qui coordonne l’établissement, la modification ou la terminaison d’un accès.  
**PEP, Policy Enforcement Point :** composant qui applique effectivement la décision sur le chemin d’accès.  
**IdP :** fournisseur d’identité qui établit ou fédère les identités.  
**MFA :** authentification multifacteur.  
**PAM :** gestion des accès privilégiés.  
**JIT :** juste-à-temps, attribution d’un droit temporaire lorsque nécessaire.  
**JEA :** juste-suffisant, limitation du droit à l’action et aux commandes utiles.  
**ZTNA :** accès réseau Zero Trust centré sur l’accès à des applications ou ressources spécifiques.  
**SSE :** ensemble de services de sécurité livrés en mode service, souvent cloud.  
**SASE :** combinaison de fonctions réseau et de sécurité distribuées.  
**Microsegmentation :** contrôle fin des communications entre charges de travail ou ressources.  
**mTLS :** TLS mutuel où les deux extrémités peuvent s’authentifier par certificats.  
**Identité de charge de travail :** identité attribuée à un service, une application ou un processus automatisé.  
**Posture :** signaux décrivant l’état de sécurité et de gestion d’un appareil ou d’une charge de travail.  
**Mode d’urgence / break glass :** chemin d’accès exceptionnel, limité et surveillé pour rétablir une fonction critique.  
**Capacité transverse :** fonction comme la gouvernance, la visibilité ou l’automatisation qui soutient plusieurs piliers.  
**Mouvement latéral :** déplacement d’un acteur compromis d’une ressource à une autre.  
**Moindre privilège :** attribution des droits minimaux nécessaires, pour la bonne portée et la durée appropriée.

## 20. Références officielles

- NIST SP 800-207, *Zero Trust Architecture* : https://csrc.nist.gov/pubs/sp/800/207/final
- NIST SP 1800-35, *Implementing a Zero Trust Architecture* : https://csrc.nist.gov/pubs/sp/1800/35/final
- Documentation complète NIST SP 1800-35 et architectures de démonstration : https://pages.nist.gov/zero-trust-architecture/
- CISA, Zero Trust Maturity Model, version 2 : https://www.cisa.gov/resources-tools/resources/zero-trust
- CISA, *Microsegmentation in Zero Trust — Introduction and Planning* : https://www.cisa.gov/news-events/alerts/2025/07/29/cisa-releases-zero-trust-microsegmentation-guidance
- CISA et partenaires, *Modern Approaches to Network Access Security* : https://www.cisa.gov/news-events/alerts/2024/06/18/cisa-and-partners-release-guidance-modern-approaches-network-access-security
- NIST Cybersecurity Framework : https://www.nist.gov/cyberframework

Le NIST SP 800-207 donne les principes et les composants logiques de référence. Le SP 1800-35, publié en juin 2025, montre des implémentations de démonstration et des enseignements pratiques. Le modèle CISA aide à organiser la progression en piliers et capacités transverses. Aucun de ces documents ne remplace l’analyse de risque et les exigences propres à l’organisation : adaptez les modèles, documentez les choix et exigez des preuves de fonctionnement.

Fin du cours.