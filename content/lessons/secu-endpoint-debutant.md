# Sécurité des Endpoints

> **Encadré de mise en contexte**
>
> Tu es technicien informatique dans une entreprise qui utilise une plateforme de formation en ligne. Les employés travaillent sur des ordinateurs portables, les formateurs utilisent des postes fixes et les administrateurs se connectent à des serveurs pour gérer les applications et les comptes.
>
> Un lundi matin, un employé télécharge une archive reçue par courriel et lance un programme qu'il pense être un document. Quelques minutes plus tard, son ordinateur ralentit. Des fichiers changent de nom, une connexion réseau inconnue apparaît et le logiciel de sécurité affiche une alerte. Le service informatique découvre que le compte de l'employé disposait de droits locaux trop importants.
>
> Dans un autre cas, un ordinateur portable est perdu pendant un déplacement. Il contient des documents professionnels et des informations enregistrées dans le navigateur. Le disque n'était pas chiffré et personne ne sait précisément quelles données étaient présentes.
>
> Ces deux situations concernent la sécurité des endpoints, c'est-à-dire des appareils qui accèdent aux systèmes et aux données. La première exige de détecter et contenir une activité potentiellement malveillante. La seconde demande de protéger les données lorsque l'appareil sort du contrôle physique de l'organisation.
>
> Pour protéger efficacement un parc informatique, il ne suffit pas d'installer un antivirus. Il faut connaître les appareils, réduire leurs vulnérabilités, limiter les droits, contrôler les applications, surveiller les événements et préparer une procédure de réponse aux incidents.

## 1. Objectifs du cours

À la fin du cours, tu devras pouvoir :
- définir un endpoint et reconnaître les différents types d'appareils concernés ;
- identifier les menaces qui ciblent les postes de travail et les appareils mobiles ;
- expliquer pourquoi l'inventaire et la gestion du cycle de vie sont indispensables ;
- appliquer les principes de base du durcissement d'un poste ;
- comprendre la gestion des mises à jour et la priorisation des vulnérabilités ;
- distinguer antivirus, EDR et XDR ;
- appliquer le moindre privilège aux utilisateurs et aux administrateurs ;
- comprendre le rôle du pare-feu local, du chiffrement du disque et des sauvegardes ;
- repérer les risques liés aux applications, scripts, périphériques USB et accès distants ;
- examiner des indicateurs de sécurité sous Windows et Linux ;
- définir les premières actions lorsqu'un poste semble compromis ;
- établir un plan de protection adapté à une petite organisation.

Ce cours est une introduction pratique. Les commandes sont destinées à l'observation et au diagnostic sur un appareil que tu es autorisé à administrer. Les opérations de correction doivent suivre les procédures de ton environnement.

## 2. Comprendre la sécurité des endpoints

### 2.1. Qu'est-ce qu'un endpoint ?

Un endpoint, appelé aussi terminal ou point de terminaison, est un appareil qui communique avec un réseau ou un service informatique. Dans une entreprise, cela peut être un ordinateur de bureau, un ordinateur portable, un téléphone professionnel, une tablette, un serveur, un poste d'administration, une machine virtuelle ou un appareil spécialisé connecté au réseau.

Certains appareils ne sont pas des postes utilisateurs classiques, mais ils nécessitent eux aussi une protection. Un serveur accessible depuis un poste compromis peut devenir une cible de déplacement latéral. Un ordinateur portable perdu peut révéler des données si son stockage n'est pas protégé.

Les mesures doivent cependant être adaptées. Un serveur de production, un téléphone personnel utilisé pour le travail et un poste de formation n'ont ni les mêmes usages ni les mêmes contraintes.

### 2.2. Qu'est-ce que la sécurité des endpoints ?

La sécurité des endpoints regroupe les méthodes, technologies et procédures destinées à protéger les appareils qui accèdent aux données et aux services. Elle concerne le système d'exploitation, les applications, les comptes et privilèges, le stockage, les périphériques, les communications réseau, les mises à jour, la détection et le traitement des incidents.

Elle ne se limite pas à reconnaître des logiciels malveillants. Elle vise aussi à réduire les possibilités d'attaque et à limiter les conséquences d'une compromission.

### 2.3. Pourquoi un endpoint est-il une cible importante ?

Un ordinateur de travail peut contenir une session de messagerie, un navigateur connecté à plusieurs applications, des documents professionnels, des clés d'accès ou des informations de configuration.

Si un attaquant prend le contrôle de l'appareil, il peut chercher à récupérer les informations accessibles à l'utilisateur, voler des sessions, installer un programme malveillant, désactiver des protections, rechercher d'autres appareils ou exploiter les droits disponibles pour atteindre des ressources supplémentaires.

Le poste est donc à la fois une cible et parfois un point de départ pour attaquer le reste du réseau.

### 2.4. Endpoint, réseau et serveur

La sécurité des endpoints ne remplace pas celle du réseau ou des serveurs. Un pare-feu réseau peut limiter les communications entre segments. Un pare-feu local contrôle certaines communications de l'appareil. Un EDR observe des activités sur le terminal. Un serveur d'identité applique des règles aux comptes.

Ces contrôles se complètent :

    Utilisateur
       |
       v
    Endpoint protégé
    - Mises à jour
    - Comptes limités
    - Protection locale
    - Surveillance
       |
       v
    Réseau contrôlé
    - Segmentation
    - Filtrage
    - Journalisation
       |
       v
    Services protégés
    - Contrôle d'accès
    - Correctifs
    - Sauvegardes

Si un poste est compromis, un réseau segmenté peut limiter la propagation. Si une attaque passe malgré les contrôles réseau, la protection locale peut aider à la détecter. Si un rançongiciel chiffre des fichiers, des sauvegardes isolées et testées peuvent faciliter la restauration.

### 2.5. Relier les endpoints à la triade CIA

La confidentialité concerne l'accès non autorisé aux documents, secrets, sessions et données personnelles. L'intégrité concerne les modifications non autorisées des fichiers, paramètres, logiciels et données. La disponibilité concerne le maintien de l'appareil et des services ou leur restauration rapide après incident.

Un ordinateur volé dont le disque est chiffré peut réduire le risque de divulgation des fichiers locaux. Un logiciel malveillant qui modifie les configurations touche l'intégrité. Un rançongiciel qui empêche d'ouvrir les données peut compromettre la disponibilité, parfois en même temps que la confidentialité.

## 3. Les principales menaces contre les endpoints

### 3.1. Les logiciels malveillants

Un logiciel malveillant, ou malware, est un programme conçu pour mener des actions nuisibles ou non autorisées. Les catégories courantes comprennent les virus, les vers, les chevaux de Troie, les rançongiciels, les logiciels espions, les voleurs d'informations, les portes dérobées et les outils de contrôle à distance détournés.

Un virus peut être associé à un fichier ou un programme ; un ver peut se propager entre des systèmes dans certaines conditions ; un cheval de Troie semble légitime mais dissimule un comportement malveillant ; un rançongiciel chiffre ou bloque des données ; un voleur d'informations recherche par exemple des identifiants ou des cookies.

Un seul outil de détection ne peut garantir que tous les programmes malveillants seront bloqués. Prévention, détection et réaction doivent fonctionner ensemble.

### 3.2. Phishing et pièces jointes

Un utilisateur peut recevoir un message qui semble provenir d'un collègue, d'un fournisseur ou d'un service de livraison. Le message lui demande d'ouvrir une pièce jointe ou d'installer un logiciel. Le lien peut conduire vers une fausse page de connexion, télécharger un programme ou exploiter une vulnérabilité du navigateur.

Il faut vérifier la source, utiliser les protections de messagerie, maintenir les applications à jour et signaler les messages suspects. Un message ne devient pas fiable simplement parce qu'il semble venir d'une personne connue : son compte peut être compromis.

### 3.3. Vulnérabilités non corrigées

Une vulnérabilité est une faiblesse qui peut permettre à un attaquant de compromettre un système ou de contourner une protection. Elle peut concerner le système d'exploitation, un navigateur, un lecteur PDF, un outil de visioconférence, une bibliothèque, un pilote ou un micrologiciel.

Un programme obsolète n'est pas nécessairement compromis, mais il peut exposer des faiblesses connues. La gestion des correctifs vise à réduire cette exposition.

### 3.4. Privilèges excessifs

Un utilisateur qui travaille en permanence comme administrateur possède plus de permissions que nécessaire pour beaucoup de tâches. Si un malware s'exécute dans ce contexte, il peut hériter d'une partie des privilèges et réaliser des changements beaucoup plus importants qu'avec un compte standard.

Le moindre privilège réduit l'impact potentiel d'une compromission.

### 3.5. Supports amovibles

Une clé USB peut contenir des fichiers infectés, des exécutables inconnus ou des documents conçus pour exploiter un logiciel vulnérable. Un périphérique inconnu peut aussi présenter un risque matériel. Il ne faut pas brancher un appareil trouvé dans un lieu public sur un poste professionnel.

Les supports amovibles doivent être utilisés selon une politique claire, avec un contrôle approprié et des restrictions adaptées aux besoins.

### 3.6. Accès distant mal configuré

Les logiciels de contrôle à distance sont utiles au support et à la maintenance. Ils deviennent risqués lorsqu'ils sont exposés sans contrôle, mal configurés ou utilisés avec des comptes faibles.

L'organisation doit inventorier les outils approuvés, limiter les accès, exiger une authentification appropriée et surveiller leur utilisation. Un outil d'administration à distance légitime peut être détourné par un attaquant ; sa présence seule ne prouve pas une attaque. Il faut examiner le compte, la source, les horaires et les actions réalisées.

### 3.7. Perte ou vol d'un appareil

Un appareil qui sort des locaux peut être perdu, volé ou utilisé par une autre personne. Le risque dépend des données présentes, du verrouillage, du chiffrement, des sessions ouvertes et de la possibilité de révoquer l'accès à distance.

Le chiffrement du disque rend les fichiers plus difficiles à exploiter lorsque l'appareil est éteint et que le déverrouillage fonctionne correctement. Il ne protège toutefois pas automatiquement les données si l'appareil est déjà déverrouillé et contrôlé par un attaquant.

### 3.8. Mauvaises configurations

Les erreurs fréquentes comprennent les comptes oubliés encore actifs, les services inutiles en écoute, un pare-feu désactivé sans justification, les logiciels installables librement, les macros non contrôlées, l'absence de chiffrement, les mises à jour reportées ou les sauvegardes accessibles depuis le poste compromis.

Une bonne configuration réduit la surface d'attaque avant même qu'un malware soit détecté.

## 4. Inventaire et cycle de vie des appareils

### 4.1. Connaître le parc

On ne peut pas protéger efficacement les appareils dont on ignore l'existence ou l'état. Un inventaire utile peut contenir l'identifiant unique, le type et modèle, le système et sa version, le propriétaire, l'emplacement ou le mode d'utilisation, les applications critiques, le niveau des correctifs, le statut du chiffrement, la solution de sécurité, la date de dernière connexion au système de gestion et le calendrier de remplacement.

Il n'est pas nécessaire de collecter toutes les informations possibles. L'inventaire doit rester proportionné aux besoins et respecter les règles concernant les données personnelles.

### 4.2. Les appareils inconnus

Un appareil personnel peut accéder aux applications professionnelles sans être correctement administré. Un ancien portable peut continuer à accéder au réseau après le départ d'un employé. Ces appareils créent des angles morts.

Une organisation peut utiliser la gestion centralisée des terminaux, un annuaire, une gestion des appareils mobiles ou un inventaire maintenu selon une procédure contrôlée. La technologie exacte dépend de la taille de l'environnement.

### 4.3. Enrôler un appareil

Lorsqu'un appareil rejoint le parc, il ne devrait pas recevoir immédiatement un accès complet sans vérification. Un processus d'enrôlement peut comprendre l'attribution d'un identifiant, l'installation du système depuis une source approuvée, l'application d'une configuration de référence, les mises à jour, l'activation du pare-feu et de la protection, le chiffrement nécessaire, l'inscription aux outils de gestion et la vérification des accès.

Cette méthode améliore la cohérence et évite les différences difficiles à expliquer entre les appareils.

### 4.4. Retirer un appareil

Lorsqu'un appareil est retiré du service, il faut éventuellement révoquer les certificats, jetons ou accès, sauvegarder les données professionnelles autorisées, retirer les secrets locaux, supprimer les données de manière adaptée avant réutilisation ou cession et mettre l'inventaire à jour.

Un effacement sommaire ne garantit pas toujours que les données soient irrécupérables. La procédure doit respecter les obligations de conservation et les exigences de protection des données.

## 5. Durcissement d'un endpoint

### 5.1. Définition

Le durcissement, ou hardening, consiste à configurer un appareil pour réduire sa surface d'attaque et limiter les possibilités d'abus. Il ne s'agit pas de désactiver arbitrairement toutes les fonctions, mais de conserver celles qui sont nécessaires tout en supprimant ou contrôlant celles qui ne le sont pas.

Le durcissement peut inclure la suppression des logiciels inutiles, la désactivation de services non nécessaires, la limitation des privilèges, l'activation du pare-feu, les mises à jour, la protection des comptes, le chiffrement, le contrôle de l'exécution des applications et la journalisation.

### 5.2. Configuration de référence

Une configuration de référence, ou baseline, décrit l'état attendu d'un appareil. Une baseline de poste de bureau peut préciser :
- une version prise en charge du système ;
- un navigateur maintenu ;
- un pare-feu actif ;
- une solution anti-malware opérationnelle ;
- un compte utilisateur sans privilèges administratifs permanents ;
- le chiffrement du disque lorsque nécessaire ;
- les mises à jour configurées ;
- un contrôle de l'installation des logiciels ;
- la journalisation des événements pertinents ;
- un verrouillage automatique après une période définie.

Les paramètres exacts doivent correspondre au système, aux contraintes métier et aux référentiels adoptés.

### 5.3. Documenter les changements

Changer plusieurs paramètres simultanément sans enregistrer ce qui a été modifié peut compliquer le diagnostic. Pour chaque changement important, documente l'objectif, la valeur initiale, la valeur attendue, les appareils concernés, le test effectué et la possibilité de revenir à une configuration connue si le changement provoque une panne.

La configuration de sécurité doit être maintenue et vérifiée, pas simplement appliquée une fois.

### 5.4. Désactiver ce qui n'est pas nécessaire

Un service inutile peut exposer un port, introduire une vulnérabilité ou créer une voie d'accès. Mais désactiver un service utilisé peut interrompre une activité légitime. Il faut identifier sa fonction, examiner les dépendances, effectuer un changement contrôlé et tester le résultat.

### 5.5. Démarrage sécurisé

Les mécanismes de démarrage sécurisé, lorsqu'ils sont pris en charge et correctement configurés, contribuent à protéger la chaîne de démarrage contre certains composants non approuvés. Ils ne remplacent pas les mises à jour, le chiffrement ou la protection en cours d'utilisation.

La configuration dépend du matériel, du micrologiciel et du système d'exploitation. Avant de modifier des paramètres de démarrage sur un appareil de production, il faut suivre les procédures du fabricant et vérifier les exigences de récupération.

## 6. Mises à jour et gestion des vulnérabilités

### 6.1. Pourquoi appliquer les correctifs ?

Les mises à jour peuvent corriger des vulnérabilités, des défauts de fonctionnement et des problèmes de sécurité. Un système non corrigé peut rester exposé à des faiblesses connues. Le processus de gestion des correctifs doit identifier les actifs concernés, prioriser les mises à jour, les acquérir depuis une source fiable, les déployer et vérifier qu'elles sont installées.

Le processus concerne le système d'exploitation, les applications, les navigateurs, les pilotes et parfois le micrologiciel.

### 6.2. Une gestion organisée

Dans une petite organisation, l'activation des mises à jour automatiques est souvent un point de départ raisonnable. Les environnements professionnels peuvent nécessiter une gestion plus structurée pour limiter les interruptions et vérifier la compatibilité.

Une procédure peut inclure :
1. inventorier les logiciels et versions ;
2. identifier les mises à jour disponibles ;
3. évaluer gravité et exposition ;
4. tester sur un groupe pilote lorsque nécessaire ;
5. déployer selon une priorité définie ;
6. suivre les échecs d'installation ;
7. vérifier les appareils concernés ;
8. documenter les exceptions et mesures temporaires.

### 6.3. Prioriser les corrections

Toutes les mises à jour n'ont pas la même urgence. Il faut tenir compte de la gravité, de l'exploitation connue, de l'exposition, des privilèges de l'application, des données sensibles, des mesures compensatoires et des conséquences d'une interruption.

Une vulnérabilité très exposée et exploitée peut exiger une action rapide. Un correctif peut néanmoins nécessiter un test ciblé si l'interruption serait grave. La priorisation doit être documentée et ne doit pas servir d'excuse pour reporter indéfiniment les correctifs.

### 6.4. Logiciels en fin de support

Lorsqu'un système ou une application n'est plus maintenu, de nouvelles vulnérabilités peuvent ne pas être corrigées. Il faut planifier la migration vers une version prise en charge ou remplacer le produit.

Si une migration immédiate est impossible, des mesures compensatoires temporaires peuvent limiter l'exposition, contrôler les accès et renforcer la surveillance. Elles ne rendent pas un système obsolète durablement sûr.

### 6.5. Sources fiables et vérification

Un faux installateur peut se faire passer pour une mise à jour. Utilise les fonctions du système, les dépôts officiels ou les sites des éditeurs approuvés. Dans un environnement professionnel, le déploiement peut être centralisé.

Les fichiers reçus par messagerie ou depuis un site inconnu ne doivent pas être installés simplement parce qu'ils promettent une correction urgente.

### 6.6. Vérifier les résultats

Un panneau indiquant que les mises à jour automatiques sont activées ne prouve pas que tous les appareils ont installé les correctifs attendus. Il faut examiner les versions installées, l'état du déploiement, les appareils en échec et les exceptions.

Un appareil qui n'a pas communiqué depuis longtemps doit être identifié : il peut constituer un angle mort.

## 7. Comptes et moindre privilège

### 7.1. Compte standard et administrateur

Un compte standard dispose de permissions limitées pour les tâches courantes. Un compte administrateur peut effectuer des opérations plus sensibles, comme installer des logiciels ou modifier les paramètres système.

Travailler en permanence comme administrateur augmente l'impact potentiel d'un programme malveillant ou d'une erreur. Les tâches ordinaires devraient être réalisées avec des droits standards ; les privilèges élevés doivent être utilisés uniquement lorsque nécessaire et selon une procédure contrôlée.

### 7.2. Comptes locaux et centralisés

Un appareil peut avoir des comptes locaux indépendants ou utiliser des identités gérées par un annuaire. Il faut éviter les comptes inutiles et les secrets partagés lorsqu'une identité individuelle est nécessaire à la traçabilité.

L'entreprise doit connaître les comptes d'administration présents sur ses appareils, vérifier qu'ils sont nécessaires et restreindre leur usage.

### 7.3. Comptes locaux privilégiés partagés

Lorsque plusieurs techniciens utilisent le même compte administrateur local, il devient difficile d'attribuer une action. La compromission du secret partagé peut également toucher plusieurs appareils.

Une organisation peut utiliser des comptes individuels, un mécanisme approuvé de gestion des mots de passe administrateur locaux et des droits temporaires lorsque les outils le permettent.

### 7.4. Retrait des droits inutiles

Lorsqu'un employé change de fonction ou quitte l'entreprise, ses permissions doivent être revues. Les comptes temporaires, comptes de prestataires et anciens comptes locaux doivent aussi être contrôlés.

Il faut éviter de supprimer un compte sans vérifier s'il est lié à un service ou à une application, mais une dépendance ne justifie pas de conserver indéfiniment des droits excessifs sans plan de correction.

### 7.5. Élévation de privilèges sous Windows

Le contrôle de compte d'utilisateur (UAC) participe à la gestion des opérations exigeant des privilèges élevés. Une demande d'élévation ne doit pas être approuvée automatiquement. L'utilisateur ou l'administrateur doit vérifier quel programme demande les privilèges et pourquoi.

Si un logiciel inconnu demande des droits administrateur pour afficher un document ordinaire, cette demande mérite une vérification. L'UAC ne constitue pas une protection complète contre tous les malwares ; il fait partie d'une stratégie plus large.

## 8. Antivirus, EDR et XDR

### 8.1. Antivirus

Un antivirus cherche à détecter et bloquer des logiciels malveillants à l'aide de techniques qui peuvent comprendre des signatures, l'analyse comportementale et d'autres mécanismes. Les capacités varient selon le produit et sa configuration.

Un antivirus à jour contribue à prévenir de nombreuses infections, mais aucun outil ne détecte nécessairement toutes les menaces. Il doit être correctement configuré, actualisé et surveillé. Une alerte ignorée ou un agent désactivé sans suivi réduit l'efficacité du dispositif.

### 8.2. Protection intégrée au système

Des systèmes modernes proposent des mécanismes intégrés. Sous Windows, Microsoft Defender Antivirus peut fournir une protection anti-malware si le produit et la configuration le permettent. L'état réel peut varier selon l'édition, les politiques et les produits gérés par l'organisation.

Il faut vérifier le statut réel plutôt que supposer qu'une protection est active uniquement parce qu'elle est incluse.

### 8.3. EDR

EDR signifie Endpoint Detection and Response, soit détection et réponse sur les terminaux. Un EDR peut collecter des événements relatifs aux processus, fichiers, connexions, comptes et autres activités du terminal. Il aide à reconstituer des séquences et peut permettre certaines actions de réponse, comme isoler un appareil, selon le produit.

L'équipe peut examiner un processus inhabituel, une modification suspecte, une tentative de désactivation des protections ou une connexion réseau inattendue. Un EDR ne dispense pas d'une analyse humaine, d'un réglage des alertes et d'une procédure d'incident ; il peut produire de faux positifs.

### 8.4. XDR

XDR signifie Extended Detection and Response. L'idée est de corréler plusieurs sources de sécurité au-delà d'un terminal, selon les fonctions du produit. Une solution peut intégrer des signaux issus des endpoints, de la messagerie, des identités, du réseau ou du cloud.

Elle peut relier des événements qui sembleraient anodins isolément. Le terme XDR varie selon les fournisseurs : il faut comparer les fonctions réelles plutôt que se fier à l'étiquette commerciale.

### 8.5. Comparaison des outils

| Solution | Rôle principal | Limite |
|---|---|---|
| Antivirus | Détecter ou bloquer des menaces sur l'appareil | Ne couvre pas tous les scénarios |
| EDR | Observer les événements du terminal et soutenir l'investigation | Requiert une configuration et une réponse |
| XDR | Corréler des événements issus de plusieurs domaines | Les intégrations varient selon le produit |
| SIEM | Centraliser et corréler les journaux collectés | La collecte ne garantit pas la détection ni le traitement |

Ces solutions peuvent être combinées. Une petite organisation peut commencer avec une protection correctement administrée, des mises à jour, des sauvegardes et une bonne gestion des comptes avant de déployer une plateforme plus complexe.

### 8.6. Liste d'applications autorisées

L'application allowlisting limite l'exécution aux programmes approuvés selon des règles définies. Elle se distingue d'une approche qui tente uniquement de bloquer une liste connue d'applications malveillantes.

Elle peut réduire l'exécution de logiciels inconnus, mais exige une gestion des exceptions, des logiciels légitimes et des mises à jour. Une politique trop restrictive peut interrompre le travail ; une politique trop permissive peut réduire son bénéfice.

## 9. Applications, navigateurs, scripts et macros

### 9.1. Réduire les applications installées

Un logiciel inutile ajoute des composants, services ou bibliothèques à maintenir. Avant d'installer une application, vérifie qu'elle est nécessaire, provient d'une source fiable et dispose d'un processus de maintenance. Les applications non prises en charge doivent être retirées ou remplacées.

### 9.2. Protéger le navigateur

Le navigateur est central pour les applications de formation, la messagerie, les consoles cloud et les services professionnels. Il doit être maintenu à jour et configuré selon les besoins de l'organisation. Les extensions doivent être limitées aux besoins réels, car elles peuvent accéder à des informations selon leurs permissions.

Évite les extensions dont la réputation et les permissions ne sont pas comprises, même si elles promettent d'améliorer la productivité.

### 9.3. Téléchargements

Les utilisateurs doivent distinguer un téléchargement d'un éditeur officiel d'un fichier obtenu sur un site inconnu ou dans un message non vérifié. Pour les programmes sensibles, l'organisation peut exiger une vérification de la signature, de la source et de la version.

Une extension de fichier ne prouve pas la sécurité. Un nom trompeur peut masquer la nature d'un fichier, notamment si l'affichage des extensions est désactivé.

### 9.4. Macros et documents

Certains documents peuvent exécuter des macros ou déclencher des actions. Une macro peut être légitime, mais aussi devenir un vecteur d'attaque. Il faut appliquer la politique relative aux macros et aux documents venant d'Internet. Un utilisateur ne devrait pas activer un contenu simplement parce qu'un message lui demande de le faire pour afficher un document inattendu.

L'organisation peut utiliser des contrôles centralisés pour limiter l'exécution des macros non approuvées.

### 9.5. Scripts d'administration

PowerShell, Bash et d'autres langages de script sont utiles à l'administration, mais peuvent être détournés. Interdire tous les scripts sans analyse serait peu réaliste. Il est plus utile de contrôler qui peut les exécuter, d'où ils proviennent, quels privilèges ils utilisent et quelles activités sont enregistrées.

Les scripts d'administration devraient être versionnés, examinés et conservés dans des emplacements maîtrisés. Les secrets ne doivent pas être intégrés en clair dans le code.

### 9.6. Téléassistance

Une application approuvée peut faciliter le support. Des outils équivalents peuvent aussi être détournés. L'organisation doit inventorier les logiciels autorisés, contrôler les comptes, limiter les accès réseau et examiner les journaux. L'utilisation en dehors des horaires habituels n'est pas forcément malveillante, mais peut justifier une vérification selon le contexte.

## 10. Pare-feu local, réseau et accès distant

### 10.1. Le rôle du pare-feu local

Le pare-feu local contrôle certaines communications entrantes et sortantes selon les règles définies. Il peut limiter l'exposition des services qui ne doivent pas être accessibles depuis le réseau.

La politique correcte ne consiste pas à désactiver le pare-feu parce qu'une application ne fonctionne pas. Il faut identifier le protocole, la destination, la direction et le besoin avant de créer une exception appropriée.

### 10.2. Services en écoute

Un service en écoute attend des connexions sur un port. Tous les ports ouverts ne sont pas malveillants : ils peuvent correspondre à des fonctions légitimes. Il faut cependant identifier les services exposés et comprendre pourquoi ils le sont.

Un service qui n'est pas nécessaire devrait être désactivé selon une procédure maîtrisée. Un service d'administration ne devrait pas être exposé sans contrôle approprié.

### 10.3. Poste hors du réseau de l'entreprise

Un ordinateur portable peut être utilisé depuis un domicile, un hôtel ou un réseau public. Certaines protections du réseau local ne sont alors plus présentes. L'endpoint doit conserver ses propres contrôles : pare-feu, mises à jour, protection des comptes et accès distant adapté.

Un VPN ou un accès contrôlé peut contribuer à protéger les communications, mais ne rend pas automatiquement sûr un appareil compromis.

### 10.4. Bureau à distance

RDP et d'autres outils peuvent être utiles à l'administration, mais présentent des risques lorsqu'ils sont mal configurés ou exposés directement. Les mesures possibles comprennent la restriction des sources d'accès, une authentification robuste, la limitation des comptes autorisés, la journalisation et la surveillance.

L'accès direct depuis Internet ne devrait pas être activé par défaut. Un accès distant requis doit passer par une architecture contrôlée et documentée.

### 10.5. Segmentation

Les appareils n'ont pas tous besoin de communiquer avec les mêmes ressources. Un poste d'apprenant n'a pas besoin d'accéder directement à tous les serveurs d'administration. La segmentation limite les communications entre zones et réduit les possibilités de déplacement latéral.

Elle doit être cohérente avec les flux nécessaires et accompagnée d'une revue des règles. Des exceptions accumulées ou des appareils non fiables connectés aux différents segments peuvent réduire son efficacité.

## 11. Chiffrement, données et sauvegardes

### 11.1. Chiffrement du disque

Le chiffrement du disque protège les données stockées localement en les rendant inaccessibles sans le mécanisme de déverrouillage approprié. Selon la plateforme, on peut rencontrer BitLocker sous Windows, FileVault sous macOS ou LUKS sous Linux.

Il est particulièrement important pour les appareils portables susceptibles d'être perdus ou volés.

### 11.2. Limites du chiffrement

Le chiffrement du disque ne résout pas tous les risques. Si l'appareil est déverrouillé et qu'un attaquant contrôle la session active, certaines données peuvent rester accessibles via les applications ou les permissions de l'utilisateur.

Le chiffrement ne remplace pas l'authentification, les mises à jour ou la protection anti-malware. Il faut aussi conserver les moyens de récupération : une mauvaise gestion de la clé de récupération peut empêcher la restauration après une panne ou un changement de configuration.

### 11.3. Données locales

Un endpoint peut contenir des fichiers téléchargés, des caches, des pièces jointes et des données de session. L'organisation doit déterminer quelles données peuvent être stockées localement, qui peut y accéder et combien de temps elles sont conservées.

Pour des données sensibles, un espace de stockage géré peut être préférable à une conservation dispersée sur les postes. Les utilisateurs doivent connaître le traitement attendu des fichiers temporaires et des exports.

### 11.4. Sauvegardes

Les sauvegardes contribuent à la disponibilité et à la récupération. Mais une sauvegarde accessible en écriture depuis le poste compromis peut être chiffrée ou supprimée par un attaquant qui contrôle ce poste.

Il faut considérer l'isolement, la protection des accès, le chiffrement et la rétention des sauvegardes. Les copies hors ligne ou autrement protégées contre la suppression constituent une défense utile contre certains rançongiciels.

Une sauvegarde non testée n'est pas une garantie de restauration. Les procédures de récupération doivent être testées et documentées.

### 11.5. Planifier la restauration

Détermine quelles données sont critiques, quelle perte est tolérable, combien de temps le service peut rester indisponible, qui peut supprimer les sauvegardes, comment elles sont protégées et comment une restauration est vérifiée.

Ces décisions relient la sécurité des endpoints à la continuité d'activité.

## 12. Appareils mobiles et usages personnels

### 12.1. Les mobiles sont des endpoints

Les téléphones et tablettes peuvent contenir des courriels, documents, sessions et applications professionnelles. Le fait qu'un appareil soit mobile ou utilise une boutique d'applications officielle ne garantit pas sa protection.

Les contrôles doivent tenir compte du système, de sa version, du verrouillage, du chiffrement, des mises à jour et des permissions des applications.

### 12.2. Verrouillage et maintenance

Un téléphone professionnel doit utiliser un mécanisme de verrouillage adapté. La durée de verrouillage automatique et les conditions de déverrouillage doivent correspondre au risque. Il faut installer les mises à jour, éviter les appareils non maintenus et retirer les applications qui n'ont plus de justification.

### 12.3. BYOD

BYOD signifie Bring Your Own Device : l'utilisateur emploie son propre appareil pour des activités professionnelles. Cela peut apporter de la souplesse, mais soulève des questions de séparation des données, de vie privée et de gestion.

Une politique BYOD précise les appareils autorisés, les données pouvant être stockées, les protections minimales, les applications ou conteneurs obligatoires, les limites d'inspection et d'effacement et le retrait des accès au départ d'un employé.

L'organisation ne doit pas prétendre gérer un appareil personnel comme si elle en était propriétaire sans définir les règles, les permissions et les limites applicables.

### 12.4. Appareil perdu

Le propriétaire doit signaler rapidement la perte. L'équipe peut devoir révoquer les sessions, bloquer l'accès, localiser ou effacer l'appareil selon les fonctions disponibles et la politique. L'effacement à distance doit être utilisé avec prudence car il peut détruire des données utiles ; les procédures doivent prévoir les appareils qui ne sont pas connectés.

## 13. Journalisation et surveillance

### 13.1. Pourquoi les journaux sont-ils importants ?

Les journaux rendent visibles des événements : connexions, changements de configuration, échecs de mise à jour, alertes, processus et opérations d'administration. Lors d'un incident, ils aident à reconstruire la chronologie, identifier les appareils concernés et estimer les conséquences.

Un journal n'est utile que si ses données sont pertinentes, conservées assez longtemps, protégées et examinées selon une procédure réaliste.

### 13.2. Événements intéressants

Selon les outils, on peut surveiller les alertes anti-malware, les désactivations inhabituelles de protections, l'installation de logiciels sensibles, les connexions privilégiées, les modifications du pare-feu, les échecs répétés d'authentification, l'apparition de mécanismes de démarrage, les modifications d'accès aux sauvegardes ou les connexions depuis des appareils inattendus.

Un seul événement ne prouve pas nécessairement une attaque. Il faut examiner le contexte et, lorsque possible, corréler plusieurs sources.

### 13.3. Alertes et faux positifs

Une alerte peut être déclenchée par une activité légitime. Un outil administratif peut accomplir des opérations ressemblant à certaines actions malveillantes. L'équipe doit définir comment valider une alerte, qui en est responsable, quelles informations préserver et quelles actions peuvent être automatisées.

Ne désactive pas une détection simplement parce qu'elle génère des alertes sans examiner si la règle peut être ajustée.

### 13.4. Centralisation des journaux

Les journaux conservés uniquement sur un poste compromis peuvent être supprimés ou modifiés par un attaquant suffisamment privilégié. La centralisation améliore la résilience et facilite les investigations. Elle exige des permissions appropriées, une politique de rétention et un contrôle d'accès aux données.

Évite de journaliser des secrets tels que mots de passe, codes de validation réutilisables ou clés privées.

## 14. Réagir à un endpoint potentiellement compromis

### 14.1. Signes possibles

Les signes à examiner comprennent une alerte de sécurité, une activité réseau inhabituelle, des fichiers modifiés de manière inattendue, un processus inconnu, la désactivation d'une protection, des connexions anormales ou des messages de rançongiciel.

Un signe isolé ne suffit pas toujours à conclure. Il faut éviter de transformer un soupçon en certitude sans examiner les éléments disponibles.

### 14.2. Limiter la propagation

Lorsque la compromission est crédible, il peut être nécessaire d'isoler l'appareil du réseau selon la procédure. Cela peut consister à désactiver la connexion Wi-Fi ou débrancher le câble réseau. L'objectif est de limiter les communications avec d'autres appareils et services, pas de détruire les preuves.

Dans un environnement critique, une isolation improvisée peut perturber une activité essentielle. La procédure doit définir qui décide et quelles sont les priorités.

### 14.3. Préserver les informations

Transmets rapidement l'incident à l'équipe de réponse si elle existe. Les informations utiles peuvent inclure l'heure, le nom de l'appareil, l'utilisateur, les alertes, les fichiers concernés et les actions déjà entreprises.

Évite les investigations improvisées qui suppriment des preuves, ainsi que le transfert de fichiers suspects vers d'autres postes ordinaires.

### 14.4. Sécuriser les comptes associés

Si les identifiants ou sessions ont pu être exposés, il peut être nécessaire de révoquer des sessions, changer les secrets concernés et examiner les activités du compte. Vérifie aussi les méthodes de récupération, les authentificateurs ajoutés, les jetons persistants et les permissions.

Changer le mot de passe ne suffit pas toujours. La séquence d'action doit correspondre aux recommandations de réponse à incident et à la portée probable de la compromission.

### 14.5. Éradiquer et restaurer

La restauration doit partir d'une source connue et maîtrisée. Si l'appareil a été fortement compromis, reconstruire à partir d'une image approuvée peut être préférable si la confiance dans l'intégrité ne peut être rétablie.

La procédure peut inclure l'analyse de l'incident, la correction des vulnérabilités, la réinstallation, la restauration de données saines et la vérification avant remise en service.

### 14.6. Apprendre de l'incident

Après l'incident, l'équipe doit identifier les causes, les contrôles manquants et les éléments qui ont facilité la détection. Les mesures correctives peuvent porter sur les mises à jour, les droits, la détection, la segmentation, la formation et les procédures d'installation.

L'objectif n'est pas seulement de remettre l'ordinateur en service, mais aussi de réduire la probabilité et l'impact d'un incident similaire.

## 15. TP : examiner un poste Windows

Ces commandes affichent des informations système. Exécute-les uniquement sur un appareil que tu es autorisé à examiner. Les résultats peuvent varier selon la version de Windows, les droits et les produits de sécurité installés.

### 15.1. Identifier la version

    Get-CimInstance Win32_OperatingSystem |
        Select-Object Caption, Version, BuildNumber

Cette commande affiche le nom, la version et le numéro de build. Ce numéro ne suffit pas à prouver que tous les correctifs sont installés ; consulte aussi l'état des mises à jour et la politique de support.

### 15.2. Examiner quelques correctifs enregistrés

    Get-HotFix |
        Sort-Object InstalledOn -Descending |
        Select-Object -First 10 HotFixID, Description, InstalledOn

La commande affiche certains correctifs connus du système. Elle ne constitue pas un inventaire universel : certaines mises à jour de composants, pilotes ou applications peuvent être représentées différemment. Utilise le résultat comme un indice et vérifie l'état global dans les outils officiels.

### 15.3. Examiner les profils du pare-feu

    Get-NetFirewallProfile |
        Select-Object Name, Enabled

La commande affiche l'état des profils disponibles. Un profil désactivé mérite une vérification, mais il faut comprendre la politique avant de modifier la configuration. Sur un appareil géré, des règles peuvent être définies centralement.

### 15.4. Examiner Microsoft Defender Antivirus

    Get-MpComputerStatus |
        Select-Object AMServiceEnabled,
                      AntivirusEnabled,
                      RealTimeProtectionEnabled,
                      AntivirusSignatureLastUpdated

Ces propriétés peuvent indiquer si le service et la protection en temps réel sont actifs et quand les signatures ont été actualisées. La commande peut ne pas fonctionner de la même manière sur toutes les éditions ou avec un autre produit. Un résultat isolé ne mesure pas toute la posture de sécurité.

### 15.5. Examiner les comptes locaux

    Get-LocalUser |
        Select-Object Name, Enabled, LastLogon

Cette commande affiche les comptes locaux et certaines informations disponibles. Repère les comptes à comprendre et à justifier. Ne désactive pas un compte uniquement parce que son nom paraît inhabituel : il peut être nécessaire au fonctionnement ou à l'administration.

### 15.6. Construire une fiche

Note la version du système, la date de vérification, les observations sur les correctifs, l'état des profils de pare-feu, l'état de protection anti-malware et les comptes à clarifier. Évite de publier des noms de compte ou des détails sensibles de configuration dans un espace public.

### 15.7. Interpréter

Même si le pare-feu est activé, qu'un produit anti-malware fonctionne et que plusieurs correctifs sont présents, l'appareil n'est pas nécessairement entièrement sécurisé. Il faut aussi examiner les versions prises en charge, les applications, les privilèges, le chiffrement, les sessions, la détection et la restauration.

## 16. TP : examiner un poste Linux

Les exemples suivants conviennent notamment à Debian ou Ubuntu pour les commandes utilisant apt et ufw. D'autres distributions emploient des outils différents.

### 16.1. Identifier le système

    cat /etc/os-release
    uname -r

La première commande affiche des informations sur la distribution, la seconde la version du noyau en cours d'exécution. Il faut connaître la distribution et son support avant de déterminer les mises à jour appropriées.

### 16.2. Examiner les services en échec

    systemctl --failed

Cette commande affiche les unités que systemd signale comme étant en échec. Un service en échec n'est pas automatiquement un problème de sécurité : il peut s'agir d'une erreur de configuration ou d'un service facultatif. Il faut consulter son rôle et les messages pertinents avant d'intervenir.

### 16.3. Examiner les services réseau en écoute

    sudo ss -tulpn

Selon les permissions et les options prises en charge, cette commande affiche les sockets en écoute et des informations sur les processus associés. Le but est de comprendre quels services attendent des connexions. Ne les arrête pas arbitrairement sur un serveur de production.

### 16.4. Examiner UFW

    sudo ufw status verbose

Cette commande affiche l'état d'UFW si cet outil est installé et utilisé. Si un autre mécanisme de filtrage est employé, l'absence d'UFW ne prouve pas qu'aucun pare-feu n'est présent.

### 16.5. Examiner les mises à jour

Sur un système utilisant apt :

    sudo apt update
    apt list --upgradable

La première commande actualise les index de paquets ; elle n'installe pas les mises à jour. La seconde affiche les mises à jour disponibles. N'applique pas automatiquement toutes les mises à jour d'un serveur de production sans suivre la procédure de maintenance, les fenêtres d'intervention et les contrôles appropriés.

### 16.6. Interpréter les résultats

Vérifie si la distribution est prise en charge, si les mises à jour pertinentes sont disponibles, si les services en écoute sont justifiés, si le pare-feu suit la politique, si les comptes privilégiés sont limités et si les données sont protégées et restaurables. Une commande n'est qu'un outil de diagnostic : le but est de comprendre l'état du système et de définir des actions utiles.

## 17. TP : créer une baseline simple

### 17.1. Objectif

Définis une configuration de référence pour un poste de formation qui consulte des cours, utilise un navigateur, télécharge des documents et réalise des exercices techniques. Le poste ne doit pas avoir besoin de privilèges administratifs permanents et les utilisateurs ne doivent pas pouvoir installer librement tous les programmes trouvés sur Internet.

### 17.2. Inventorier et définir les besoins

Documente le système, les applications nécessaires, l'utilisateur responsable, les données stockées localement, les accès réseau requis, les fonctions d'administration, la solution de protection et l'état des sauvegardes et du chiffrement.

Liste les tâches légitimes : consulter le contenu, ouvrir des documents, accéder à la plateforme et exécuter les outils explicitement prévus pour les TP. Cette liste permet de décider quels logiciels et services doivent rester disponibles.

### 17.3. Réduire la surface d'attaque

Examine les applications inutiles, les comptes locaux et les services réseau. Définis les restrictions nécessaires. Ne supprime pas un outil de diagnostic simplement parce qu'il est puissant : certains outils sont nécessaires aux cours techniques. Il est préférable de limiter leur accès, d'expliquer leur usage autorisé et de protéger les opérations privilégiées.

### 17.4. Appliquer les contrôles de base

La baseline devrait inclure, lorsque le système le permet, les mises à jour configurées, le pare-feu actif, une protection anti-malware opérationnelle, un compte standard, le chiffrement lorsque nécessaire, le verrouillage de l'appareil, les sauvegardes autorisées, des sources logicielles fiables, l'accès distant limité et une journalisation adaptée.

### 17.5. Vérifier et maintenir

Pour chaque contrôle, indique la valeur attendue, le moyen de vérification, le résultat observé, les exceptions, la personne responsable et la date du prochain contrôle. De nouvelles versions, applications et permissions peuvent faire diverger l'appareil de la baseline ; un contrôle périodique aide à détecter les écarts.

## 18. Étude de cas : incident sur un poste de NovaLearn

### 18.1. Situation initiale

NovaLearn utilise des portables pour ses formateurs. Un formateur ouvre une pièce jointe d'une adresse qui ressemble à celle d'un partenaire. Le document demande l'activation d'un contenu supplémentaire. Quelques minutes plus tard, l'ordinateur devient lent, le produit de sécurité déclenche des alertes et un utilisateur signale qu'il ne peut plus accéder à un répertoire partagé.

L'équipe informatique ne connaît pas encore l'étendue de l'incident.

### 18.2. Séparer faits et hypothèses

Les faits disponibles sont que le document a été ouvert, que des alertes sont apparues, que le comportement du poste a changé et qu'un répertoire partagé semble affecté. Les hypothèses peuvent inclure un malware, un défaut logiciel ou une autre cause technique. L'équipe doit recueillir les éléments sans annoncer prématurément une cause non confirmée.

### 18.3. Contenir le poste suspect

L'équipe évalue le risque et isole le poste selon sa procédure. Si plusieurs systèmes semblent affectés, elle peut devoir protéger le segment concerné plutôt que traiter chaque appareil indépendamment. Elle évite de brancher des supports inconnus ou de copier des fichiers suspects sur des postes ordinaires.

### 18.4. Examiner les alertes

Les techniciens consultent les journaux et les informations de sécurité, recherchent les autres appareils concernés et identifient les comptes utilisés pendant la période. Ils vérifient également si des identifiants ou sessions ont pu être exposés et si le poste avait des droits excessifs.

### 18.5. Évaluer la portée

Il faut déterminer si l'activité est restée limitée au poste, si des comptes ont été utilisés anormalement et si d'autres appareils ou ressources ont été atteints. L'absence de symptômes sur un autre ordinateur ne prouve pas qu'il est sain ; l'enquête doit s'appuyer sur des observations adaptées.

### 18.6. Éradiquer et restaurer

Si l'appareil est compromis, l'équipe suit la procédure de nettoyage ou de reconstruction. Une restauration à partir d'une image approuvée peut être préférable si la confiance dans l'intégrité du système ne peut pas être rétablie. Les données ne sont restaurées qu'après avoir évalué leur état et le risque de réintroduire l'incident.

### 18.7. Corriger et prévenir

L'analyse révèle que le poste utilisait un compte administrateur local, que certaines applications étaient obsolètes et que trop d'utilisateurs pouvaient modifier le répertoire partagé. Les corrections comprennent le retrait des privilèges inutiles, la mise à jour des logiciels, la révision des permissions, l'amélioration de la détection et de la procédure de signalement, ainsi que la vérification des sauvegardes.

L'organisation met à jour la baseline, définit la procédure d'escalade et teste la restauration. Corriger uniquement le poste infecté laisserait les autres appareils avec la même configuration vulnérable.

## 19. Erreurs fréquentes à éviter

### Erreur 1 — Installer un antivirus suffit

Un antivirus contribue à la protection, mais ne remplace pas les mises à jour, la gestion des droits, les sauvegardes, le chiffrement et la surveillance.

**Correction :** construire plusieurs couches de défense et vérifier leur état réel.

### Erreur 2 — Tous les ports en écoute sont malveillants

Un port peut correspondre à un service légitime. Le risque dépend du service, de son exposition et de sa configuration.

**Correction :** identifier le processus et justifier le service avant de modifier la configuration.

### Erreur 3 — Un compte administrateur accélère toujours le travail

Un privilège permanent augmente l'impact potentiel d'une compromission.

**Correction :** effectuer les tâches ordinaires avec un compte standard et utiliser des privilèges élevés seulement lorsqu'ils sont nécessaires.

### Erreur 4 — Les mises à jour automatiques règlent tout

Un appareil peut échouer à installer un correctif ou utiliser une version hors support.

**Correction :** vérifier les versions et l'état du déploiement, puis traiter les exceptions.

### Erreur 5 — Le chiffrement protège toutes les données contre tous les scénarios

Le chiffrement du disque protège principalement les données stockées lorsque le mécanisme de déverrouillage n'est pas disponible ; il ne garantit pas la sécurité d'une session active compromise.

**Correction :** combiner chiffrement, contrôle d'accès, protection des sessions et surveillance.

### Erreur 6 — Une sauvegarde accessible depuis le poste suffit

Un attaquant qui contrôle le poste peut parfois accéder aux sauvegardes accessibles avec ses droits.

**Correction :** isoler ou protéger les copies, contrôler les permissions et tester la restauration.

### Erreur 7 — Une alerte est toujours une attaque confirmée

Les outils peuvent produire des faux positifs.

**Correction :** examiner le contexte et les éléments supplémentaires, sans ignorer les alertes.

### Erreur 8 — Désactiver une protection pour supprimer les alertes

Cela peut masquer le problème sans le résoudre.

**Correction :** analyser la cause, ajuster la règle selon une procédure contrôlée et documenter l'exception.

### Erreur 9 — Réinstaller immédiatement sans préserver les informations

L'effacement peut détruire des éléments utiles à la compréhension de l'incident.

**Correction :** suivre la procédure de réponse et préserver les informations nécessaires avant la reconstruction lorsque c'est approprié.

### Erreur 10 — Les portables hors du bureau sont protégés par le réseau d'entreprise

Un appareil à domicile ou sur un réseau public peut ne plus bénéficier des contrôles internes.

**Correction :** maintenir les protections locales, les mises à jour et une méthode d'accès distant contrôlée.

### Erreur 11 — Tous les appareils personnels peuvent être administrés comme les appareils de l'entreprise

Cela peut créer des problèmes de vie privée, de responsabilité et de conformité.

**Correction :** définir une politique BYOD qui explicite les contrôles, les données, les limites de gestion et le retrait des accès.

### Erreur 12 — Restaurer signifie nécessairement résoudre l'incident

Restaurer un système sans traiter la cause peut laisser la même vulnérabilité en place.

**Correction :** corriger la cause, valider l'état restauré et surveiller après la remise en service.

## 20. Exercices avec corrections

### Exercice 1 — Définir un endpoint

Lequel de ces éléments peut être un endpoint dans une organisation ?

A. Uniquement un portable  
B. Uniquement un serveur physique  
C. Un ordinateur, un téléphone ou un serveur connecté à des services informatiques  
D. Uniquement un routeur

**Correction : C.** Le terme recouvre différents types d'appareils. Les protections varient selon leur rôle.

### Exercice 2 — Durcissement

Quel est l'objectif principal du durcissement ?

A. Désactiver toutes les fonctions  
B. Réduire la surface d'attaque tout en gardant les besoins légitimes  
C. Installer le maximum de logiciels sans configuration  
D. Donner des droits administrateur à tous les utilisateurs

**Correction : B.** Le durcissement retire les fonctions inutiles et limite les possibilités d'abus tout en conservant la fonction attendue.

### Exercice 3 — Moindre privilège

Un employé consulte des cours et modifie ses documents, mais n'a pas besoin d'installer des pilotes. Quelle approche convient ?

A. Compte administrateur permanent  
B. Compte partagé avec l'équipe  
C. Compte standard pour les tâches courantes et élévation contrôlée si nécessaire  
D. Désactiver la protection du poste

**Correction : C.** Un compte standard limite l'impact potentiel d'une compromission dans le contexte utilisateur.

### Exercice 4 — Prioriser les correctifs

Un poste exposé contient une application vulnérable à une faille activement exploitée. Quelle réponse convient le mieux ?

A. Ignorer la faille jusqu'au remplacement du poste  
B. Prioriser l'évaluation et la correction selon le risque, avec des mesures temporaires si nécessaire  
C. Désactiver les mises à jour  
D. Réinstaller le navigateur sans analyse

**Correction : B.** La priorité dépend de l'exploitation, de l'exposition et de la gravité. Il faut vérifier la correction.

### Exercice 5 — EDR

Quelle affirmation décrit un EDR ?

A. Il chiffre systématiquement tous les fichiers  
B. Il remplace toujours les sauvegardes  
C. Il peut collecter et analyser des événements du terminal et aider à la détection et à la réponse  
D. Il empêche toute compromission

**Correction : C.** L'EDR améliore l'observation et certaines actions de réponse, mais sa valeur dépend de la configuration et de la capacité à traiter les alertes.

### Exercice 6 — Port en écoute

Un technicien observe un port en écoute. Quelle conclusion est justifiée ?

A. Le poste est forcément compromis  
B. Le service est nécessairement malveillant  
C. Il faut identifier le service, comprendre pourquoi il écoute et vérifier si son exposition est nécessaire  
D. Il faut immédiatement éteindre le poste

**Correction : C.** Un port en écoute peut être légitime. Il faut comprendre sa fonction, son exposition et sa justification.

### Exercice 7 — Ordinateur perdu

Un portable professionnel est perdu. Le disque était chiffré, mais des sessions étaient ouvertes. Que faut-il faire ?

A. Ne rien faire : le chiffrement résout tout  
B. Signaler l'incident, évaluer le risque et révoquer les accès nécessaires  
C. Communiquer les mots de passe au support  
D. Désactiver les sauvegardes

**Correction : B.** Le chiffrement réduit certains risques, mais les sessions et accès associés doivent aussi être évalués.

### Exercice 8 — Rançongiciel présumé

Des fichiers changent de nom et des alertes apparaissent. Quelle action est généralement appropriée ?

A. Continuer le travail jusqu'à la fin de journée  
B. Copier les fichiers inconnus sur tous les postes  
C. Appliquer la réponse à incident, isoler le système lorsque approprié et signaler l'événement  
D. Désactiver les alertes

**Correction : C.** Il faut limiter la propagation, préserver les éléments utiles et engager l'investigation.

### Exercice 9 — Sauvegardes

Pourquoi une sauvegarde accessible en écriture depuis le poste compromis peut-elle être insuffisante contre un rançongiciel ?

A. Parce qu'une sauvegarde ne contient jamais de fichiers  
B. Parce qu'un attaquant peut parfois chiffrer ou supprimer les copies accessibles avec les privilèges obtenus  
C. Parce que toutes les sauvegardes sont publiques  
D. Parce qu'une sauvegarde ne peut jamais être restaurée

**Correction : B.** Les copies doivent être protégées contre l'accès et la suppression non autorisés et la restauration doit être testée.

### Exercice 10 — Posture de sécurité

Un ordinateur dispose d'un antivirus actif et d'un pare-feu activé. Est-il entièrement sécurisé ?

A. Oui, ces contrôles couvrent tous les risques  
B. Oui, si l'utilisateur connaît son mot de passe  
C. Non, il faut aussi examiner mises à jour, comptes, applications, stockage, sessions, surveillance et récupération  
D. Non, car un antivirus n'est jamais utile

**Correction : C.** La sécurité repose sur plusieurs couches complémentaires. Un outil opérationnel est utile, mais ne garantit pas l'absence de toutes les vulnérabilités.

## 21. Défi final — Sécuriser le parc informatique de Skill-Tree

### 21.1. Scénario

Une petite entreprise gère quinze portables de formateurs, dix postes fixes en salle de formation, trois serveurs, cinq téléphones professionnels, plusieurs comptes administrateurs et des sauvegardes. L'inventaire est incomplet. Certains utilisateurs disposent de droits administrateur, les mises à jour sont irrégulières, le chiffrement est absent sur certains portables et les alertes sont examinées seulement lorsqu'un utilisateur signale un problème.

### 21.2. Travail demandé

Prépare un plan comprenant l'inventaire des appareils et propriétaires, une baseline par catégorie, une stratégie de correctifs, une politique de comptes, une protection des endpoints et un suivi des alertes, la protection des données et sauvegardes, une procédure pour les appareils perdus et incidents ainsi que des indicateurs de progrès.

### 21.3. Correction détaillée

**Inventaire.** Chaque appareil doit avoir un identifiant, un responsable, une version du système, un statut de maintenance et des informations sur les accès. Les serveurs sont distingués des postes utilisateurs ; les appareils absents du système de gestion doivent être signalés.

**Baselines.** Un poste de formation n'a pas les mêmes besoins qu'un serveur. La configuration minimale de chaque catégorie doit définir les versions prises en charge, le pare-feu, les mises à jour, la protection, les comptes, le chiffrement lorsque nécessaire et les journaux pertinents.

**Correctifs.** L'équipe inventorie les systèmes, suit les mises à jour, priorise les risques élevés et vérifie l'installation. Les systèmes essentiels disposent d'une procédure de maintenance et de test sans reporter indéfiniment les correctifs urgents.

**Privilèges.** Les formateurs utilisent des comptes standards pour les tâches ordinaires. Les administrateurs ont des comptes individuels et limitent l'utilisation des privilèges. Les comptes obsolètes et accès partagés sont examinés.

**Protection et surveillance.** Les endpoints utilisent une solution de sécurité correctement gérée. Les alertes importantes sont dirigées vers une personne responsable, avec procédure de triage, d'escalade et d'isolation. L'état de l'outil doit être vérifié.

**Données.** Les portables qui stockent des données sensibles utilisent un chiffrement adapté et une récupération protégée. Les sauvegardes sont séparées des droits ordinaires, protégées contre la suppression et testées.

**Incident.** Les utilisateurs savent comment signaler et quelles manipulations éviter. L'équipe détermine quand isoler, comment préserver les éléments, quels comptes examiner et comment restaurer un système fiable.

**Mesure.** Indicateurs possibles : pourcentage d'appareils inventoriés, couverture de mise à jour, couverture de la protection, état du chiffrement, délai de correction des vulnérabilités prioritaires et taux de réussite des tests de restauration. Chaque indicateur doit être associé à une source vérifiable ; un tableau à 100 % ne prouve rien si les appareils absents de l'inventaire ne sont pas comptés.

### 21.4. Feuille de route

**Priorité 1 — Visibilité et risques critiques :** créer l'inventaire, identifier les appareils hors support, protéger les comptes administrateurs et vérifier que la protection fonctionne.

**Priorité 2 — Réduction des faiblesses :** organiser les correctifs, réduire les droits inutiles, activer le chiffrement nécessaire et revoir les services exposés.

**Priorité 3 — Résilience :** tester les sauvegardes, documenter l'isolation et les procédures de récupération.

**Priorité 4 — Amélioration continue :** centraliser les informations, analyser les alertes, revoir les baselines et mesurer la conformité.

### 21.5. Critères d'autoévaluation

Tu as réussi si tu peux expliquer pourquoi l'inventaire est nécessaire, comment le durcissement réduit la surface d'attaque, pourquoi les mises à jour demandent un suivi, les différences entre antivirus, EDR et XDR, la complémentarité des privilèges et du chiffrement, la réaction à un poste suspect, la protection des sauvegardes et la vérification de l'application des contrôles.

## 22. Glossaire

**Antivirus :** composant de sécurité destiné à détecter et bloquer des logiciels malveillants.

**Application allowlisting :** politique limitant l'exécution aux applications approuvées selon des règles définies.

**Baseline :** configuration de référence décrivant l'état de sécurité attendu d'un appareil.

**Chiffrement du disque :** protection cryptographique des données stockées, qui nécessite un mécanisme de déverrouillage approprié.

**Endpoint :** appareil qui communique avec un réseau ou un service informatique.

**EDR :** capacités de détection et de réponse sur les terminaux.

**Hardening :** durcissement d'un système pour réduire sa surface d'attaque.

**Inventaire des actifs :** liste maintenue des appareils et ressources à protéger, avec les informations nécessaires à leur gestion.

**Least privilege :** principe du moindre privilège limitant les permissions aux besoins légitimes.

**Malware :** logiciel malveillant destiné à mener des actions nuisibles ou non autorisées.

**Patch management :** processus d'identification, de priorisation, de déploiement et de vérification des correctifs.

**Pare-feu local :** mécanisme filtrant certaines communications réseau sur l'appareil.

**Rançongiciel :** logiciel malveillant qui chiffre ou bloque les données pour obtenir une rançon.

**Surface d'attaque :** ensemble des points, composants et configurations qu'un attaquant pourrait chercher à exploiter.

**XDR :** capacités corrélant des événements provenant de plusieurs domaines de sécurité, selon le produit.

## 23. Ressources pour approfondir

- **NIST — SP 800-40 Rev. 4, Guide to Enterprise Patch Management Planning :** planification, priorisation, déploiement et vérification des correctifs.  
  https://csrc.nist.gov/pubs/sp/800/40/r4/final

- **CISA — #StopRansomware Guide :** prévention et réponse aux incidents de rançongiciel, avec des recommandations sur sauvegardes, privilèges, détection et applications autorisées.  
  https://www.cisa.gov/stopransomware/ransomware-guide

- **CISA — Ransomware FAQs :** mesures de base telles que mises à jour, sauvegardes et restriction des privilèges.  
  https://www.cisa.gov/stopransomware/ransomware-faqs

- **NIST — SP 800-124 Rev. 2, Guidelines for Managing the Security of Mobile Devices in the Enterprise :** gestion de la sécurité des appareils mobiles en entreprise.  
  https://csrc.nist.gov/pubs/sp/800/124/r2/final

- **Microsoft Learn — Microsoft Defender Antivirus :** documentation sur la configuration et l'administration de la protection anti-malware sous Windows.  
  https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-antivirus

- **Microsoft Learn — Attack surface reduction rules :** documentation sur les règles de réduction de la surface d'attaque dans les environnements compatibles.  
  https://learn.microsoft.com/en-us/defender-endpoint/attack-surface-reduction

- **CIS — Center for Internet Security :** références de configuration sécurisée pour différents systèmes et logiciels.  
  https://www.cisecurity.org/cis-benchmarks

Relie toujours les recommandations à des contrôles vérifiables : quel appareil est concerné, quelle configuration est attendue, comment son état est mesuré, qui traite les écarts et comment la restauration est testée.

**Fin du cours : Sécurité des Endpoints.**