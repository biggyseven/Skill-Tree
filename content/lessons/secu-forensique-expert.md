# Forensique réseau et système

> **Mise en contexte**

Un serveur génère une alerte de connexion inhabituelle. Dans le même intervalle, un compte de service change de comportement, un processus nouveau apparaît et le trafic réseau augmente. L'équipe doit comprendre ce qui s'est produit, sur quels systèmes, à quel moment et avec quel degré de certitude. La forensique numérique fournit une méthode structurée pour préserver, examiner et corréler les traces d'un système et d'un réseau sans confondre les faits, les hypothèses et les décisions.

Ce cours est orienté vers l'investigation défensive et autorisée. Les travaux pratiques utilisent des journaux synthétiques, des fichiers créés pour l'exercice et des captures réseau pédagogiques. Ne collectez pas les données d'un tiers sans autorisation, ne modifiez pas les preuves originales et ne lancez pas d'outils d'acquisition sur une infrastructure réelle sans plan validé. Les règles applicables à la vie privée, aux données personnelles et à la conservation varient selon la juridiction et l'organisation ; faites valider le périmètre et les méthodes par les responsables compétents.

## 1. Objectifs et compétences visées

À la fin du cours, vous saurez définir le périmètre d'une investigation, établir un plan de collecte, prioriser les éléments volatils, préserver l'intégrité, documenter une chaîne de conservation, examiner des journaux système et réseau, construire une chronologie, formuler des hypothèses vérifiables et rédiger un rapport reproductible. Vous comprendrez les différences entre capture de paquets, journaux de flux, journaux de pare-feu, télémétrie endpoint, mémoire vive, journaux applicatifs et image de stockage.

L'objectif n'est pas de produire une certitude artificielle. Une analyse peut conclure qu'un événement est confirmé, probable, possible ou non démontré avec les sources disponibles. Elle doit décrire ce que les preuves montrent, ce qu'elles ne montrent pas, ce qui manque et quel prochain contrôle autorisé réduirait l'incertitude. L'absence de trace n'est pas automatiquement une preuve d'absence : un capteur peut être désactivé, l'heure erronée, la rétention expirée ou l'événement hors de la fenêtre étudiée.

La forensique diffère d'une simple recherche dans un SIEM par son attention portée à la préservation, à la provenance, à la reproductibilité et aux relations entre éléments. Les requêtes rapides restent utiles, mais leurs résultats doivent pouvoir être expliqués et vérifiés. Le but final est d'aider à prendre des décisions proportionnées : contenir un incident, retrouver son étendue, améliorer une détection ou établir une chronologie fiable.

~~~text
Signal initial
     |
     v
Autorisation et périmètre
     |
     v
Préservation et chaîne de conservation
     |
     v
Collecte des sources pertinentes
     |
     v
Validation et normalisation
     |
     v
Examen puis corrélation
     |
     v
Hypothèses testées et limites explicites
     |
     v
Rapport, décisions et actions de suivi
~~~

## 2. Principes fondamentaux de la preuve numérique

Une preuve numérique est une donnée utile à une question d'investigation : fichier, journal, valeur de configuration, capture réseau, événement d'authentification, métadonnée, artefact mémoire ou image de stockage. Sa valeur dépend de sa provenance, de son intégrité, de sa pertinence, de sa complétude et du contexte dans lequel elle a été obtenue. Un fichier isolé ne raconte souvent qu'une petite partie de l'histoire.

Il faut distinguer l'original, la copie de préservation, la copie de travail, les exports d'outils et les notes d'analyse. L'original doit être protégé selon la procédure applicable. Les opérations analytiques sont réalisées sur une copie de travail. Chaque transformation — extraction, conversion, décompression, normalisation, filtrage ou export — doit être notée, car elle peut modifier le contenu ou réduire des informations.

Une empreinte cryptographique telle que SHA-256 aide à vérifier qu'une copie contient les mêmes octets qu'une autre. Elle ne prouve pas que les données étaient authentiques avant leur collecte, que l'horloge du système était juste ou que le fichier fourni représente intégralement l'incident. L'intégrité et l'authenticité sont deux questions différentes.

### 2.1 Les cinq questions à poser

- **Provenance :** quelle source a produit cette donnée, sur quel équipement, avec quel compte et par quelle méthode ?
- **Intégrité :** une empreinte, un contrôle d'export ou un autre mécanisme permet-il de détecter une modification depuis la collecte ?
- **Pertinence :** quel lien cette donnée possède-t-elle avec l'hypothèse et la fenêtre étudiées ?
- **Complétude :** quels événements ou champs sont absents, filtrés, perdus ou hors rétention ?
- **Reproductibilité :** un autre analyste peut-il refaire la recherche avec les mêmes entrées et paramètres ?

~~~text
              Qualité d'une preuve
                     |
     +---------------+---------------+
     |               |               |
  Provenance       Intégrité       Pertinence
     |               |               |
     +---------------+---------------+
                     |
              Complétude + contexte
                     |
                     v
          Conclusion proportionnée
~~~

## 3. Autorisation, périmètre et règles d'arrêt

Définissez les systèmes, comptes, réseaux, dates, fuseaux horaires, types de données et questions que l'investigation doit couvrir. Notez qui a autorisé le travail, qui prend les décisions et quelles actions sont permises. Une autorisation d'examiner un serveur ne signifie pas automatiquement qu'il est permis de collecter les boîtes mail des utilisateurs, d'interroger un service tiers, d'accéder à un équipement personnel ou de conserver indéfiniment des données sensibles.

Définissez des règles d'arrêt avant la collecte : exposition de données personnelles inattendues, perte d'intégrité, risque pour la disponibilité, découverte d'un système hors périmètre, nécessité d'obtenir une autorisation supplémentaire ou effet imprévu d'une action. Lorsqu'une limite est atteinte, arrêtez l'opération concernée, consignez le motif et demandez une décision au responsable approprié. Ne continuez pas au seul motif que le nouvel élément semble intéressant.

Les interventions doivent être proportionnées au risque. La collecte de données volatiles sur un serveur critique peut avoir un effet opérationnel. Une isolation réseau peut limiter une propagation, mais couper un lien peut aussi rendre impossible la collecte distante et interrompre une activité métier. Il faut arbitrer avec l'équipe de réponse à incident, les responsables du service et, lorsque nécessaire, les équipes juridiques et de protection des données.

~~~text
Question d'investigation
        |
        v
Système / données dans le périmètre ?
        |
   +----+----+
   |         |
  non       oui
   |         |
Arrêter      v
et demander  Action minimisée et autorisée
une décision       |
                   v
           Journaliser l'action
~~~

## 4. Préparer le dossier et la chaîne de conservation

Attribuez un identifiant de dossier stable. Enregistrez le demandeur, l'autorité, la finalité, la portée, les dates, les personnes autorisées, les dispositifs collectés et le lieu de conservation. Chaque élément reçoit son propre identifiant et une description factuelle : type, hôte, chemin ou interface, date et heure de collecte, fuseau horaire, outil, version, opérateur, méthode, empreinte et emplacement de stockage.

La chaîne de conservation trace les transferts et les accès. Pour chaque transfert, consignez l'expéditeur, le destinataire, l'heure, le support et le contrôle d'intégrité effectué. Les permissions doivent empêcher toute modification accidentelle ; le stockage doit être protégé contre les accès non autorisés et les suppressions prématurées. Des journaux d'accès et une rétention définie facilitent l'audit.

Évitez les descriptions subjectives dans la fiche de preuve. « Export de journaux collecté sur LAB-07 à 14:32 UTC » est plus précis que « virus retrouvé ». La qualification de malware est une conclusion analytique distincte. Les notes doivent distinguer l'observation brute de l'interprétation, les étapes automatiques des actions manuelles, et les erreurs ou limites de l'acquisition.

~~~text
Dossier IR-2026-042
    |
    +--> E-001 : export de journaux
    |      source, fenêtre, SHA-256, opérateur
    |
    +--> E-002 : capture PCAP
    |      interface, filtre, durée, SHA-256
    |
    +--> E-003 : image de travail
    |      origine, méthode, vérification
    |
    +--> N-001 : notes et décisions horodatées
           auteur, contexte, référence à la preuve
~~~

### 4.1 Empreintes et copies

Sur un fichier autorisé et présent dans le laboratoire, calculez une empreinte avant et après copie, puis documentez les valeurs :

~~~text
Linux :
sha256sum journaux-labo.txt

macOS :
shasum -a 256 journaux-labo.txt

Windows PowerShell :
Get-FileHash .\journaux-labo.txt -Algorithm SHA256
~~~

Une concordance entre les empreintes indique que les octets correspondent, avec la confiance pratique apportée par la fonction choisie. Elle ne confirme pas que la collecte était complète. Si les empreintes diffèrent, ne remplacez pas silencieusement la valeur ; vérifiez les opérations, identifiez la copie concernée et documentez la résolution.

## 5. Ordre de volatilité et acquisition

Les données ne disparaissent pas toutes à la même vitesse. Les connexions réseau actives, les processus, la mémoire vive, les sessions, les caches et certaines informations temporaires peuvent changer ou disparaître après redémarrage. Les fichiers persistants et les images de stockage peuvent survivre plus longtemps, mais les journaux tournent, sont purgés ou sont remplacés. Il n'existe pas un ordre universel applicable à tous les systèmes ; l'ordre doit être adapté à la question et au coût opérationnel.

Avant d'acquérir une source, demandez-vous si elle est volatile, si sa collecte peut changer l'état, si la méthode est approuvée, si le système est critique et si l'équipe possède un chemin de gestion fiable. Une capture mémoire ou une collecte live peut être utile pour un incident actif, mais elle utilise des ressources et ajoute des processus ou fichiers. Une acquisition à froid peut préserver davantage l'état du stockage après arrêt, mais l'arrêt détruit des données en mémoire et peut déclencher du chiffrement, des tâches de nettoyage ou des changements d'état.

La bonne décision documente les compromis. Notez l'état du système avant l'intervention, l'heure précise, les commandes ou outils autorisés, les erreurs, les effets connus et les éléments non collectés. Si une acquisition spécialisée est nécessaire, faites-la exécuter par une personne formée selon une procédure validée, plutôt que d'improviser en production.

~~~text
Question : qu'est-ce qui disparaît le plus vite ?
        |
        +--> connexions / sessions actives
        |
        +--> processus / mémoire / caches
        |
        +--> journaux temporaires et files
        |
        +--> journaux persistants et fichiers
        |
        +--> sauvegardes / archives disponibles
        |
        v
Ordre adapté au risque, à la question et aux outils
~~~

### 5.1 Collecte live ou hors ligne

La collecte live se déroule pendant que le système fonctionne ; elle est utile pour les sessions actives, la mémoire, les connexions et les processus. Elle peut cependant modifier l'état et consommer des ressources. La collecte hors ligne examine un support ou une image déjà acquise, ce qui réduit le changement induit pendant l'analyse, mais dépend de la qualité de l'acquisition initiale et peut ne pas révéler des données qui n'ont jamais été persistées.

Avant de décider, consultez les équipes propriétaires et les règles de réponse. Dans une situation à fort impact, la priorité peut être de confiner rapidement plutôt que de collecter toutes les données volatiles. À l'inverse, lorsque la preuve volatile est essentielle et que le risque est maîtrisé, une acquisition autorisée peut être prioritaire. Toute action doit être justifiée par le but de l'investigation.

## 6. Sources forensiques système

Les systèmes d'exploitation et les applications enregistrent des événements différents selon leur configuration. Parmi les sources possibles figurent les journaux d'authentification, de sécurité, de services, de tâches planifiées, de création de processus, de modifications de configuration, de mises à jour, d'applications, de pare-feu local, les journaux EDR, les journaux de fichiers et les informations d'inventaire. Les champs et la disponibilité dépendent de l'OS, des agents et des politiques de collecte.

Un journal doit être interprété avec son schéma, sa politique de rétention et son contexte. Un identifiant d'événement a une signification précise dans une version donnée ; ne recopiez pas un numéro trouvé en ligne sans vérifier la documentation de la source. Le nom d'un processus peut être usurpé. Un compte peut être utilisé par plusieurs services. Les journaux peuvent être incomplets ou avoir été altérés par une action légitime ou malveillante.

La collecte doit préserver le format natif lorsque cela est possible, mais des exports structurés peuvent être nécessaires pour l'analyse. Conservez une copie originale et notez les transformations. Si le système exporte des journaux en CSV ou JSON, gardez le fichier initial, les paramètres de filtre, la période et les erreurs d'export. Si une interface graphique est utilisée, documentez les recherches et les critères appliqués.

~~~text
Poste / serveur
    |
    +--> Authentification et comptes
    |
    +--> Processus et services
    |
    +--> Fichiers et configuration
    |
    +--> Applications / tâches planifiées
    |
    +--> EDR / pare-feu local
    |
    v
Collecte horodatée et documentée
~~~

### 6.1 Artefacts et fichiers système

Les fichiers de configuration, métadonnées d'accès, journaux, raccourcis, historiques d'application, tâches programmées, services et éléments de démarrage peuvent éclairer la séquence d'une activité. La pertinence dépend du système étudié. Un chemin de fichier ou un artefact de navigation ne garantit pas qu'un utilisateur ait lu le contenu ; un horodatage d'accès peut provenir d'un service, d'un indexeur ou d'une sauvegarde.

L'analyse du système de fichiers examine les noms, chemins, tailles, dates, attributs, propriétaires et empreintes. Les dates de création, de modification, d'accès ou de changement de métadonnées ne sont pas interchangeables. Certains systèmes modifient l'heure d'accès ou la désactivent pour des raisons de performance. Les copies et migrations peuvent préserver, remplacer ou recalculer les métadonnées. Il faut connaître le système de fichiers et le processus de collecte avant de donner un sens aux heures.

La récupération de fichiers supprimés ou de fragments peut être utile, mais son succès dépend du support, de l'espace réutilisé, du chiffrement et de la méthode. Une récupération partielle ne garantit pas que tout le fichier soit reconstitué correctement. Conservez les limites et évitez d'inférer le contenu absent.

### 6.2 Registres, services et comptes

Sur Windows, certaines configurations et informations de fonctionnement sont présentes dans le registre, les journaux d'événements et des artefacts système. Sur Linux, des éléments pertinents peuvent se trouver dans journald, syslog, les configurations de services, les journaux d'authentification, les tâches planifiées et les outils de gestion des paquets. Les emplacements varient selon les distributions et versions. Ne supposez pas que le même chemin soit présent partout.

Pour un changement de service ou de compte, recherchez les événements de création, modification, suppression, le compte initiateur, l'heure, le processus responsable et l'effet observé. Comparez avec le système de gestion de configuration et les changements approuvés. Un nouveau service peut correspondre à une mise à jour ; son absence dans un référentiel d'inventaire est un motif de vérification, non une preuve automatique de malveillance.

~~~text
Changement observé
       |
       v
Quel compte / quel processus ?
       |
       v
Existe-t-il un changement approuvé ?
       |
   +---+---+
   |       |
  oui     non / inconnu
   |       |
Comparer   Rechercher la provenance
à la plage et les événements associés
approuvée       |
   +-----------+
         |
         v
Conclusion documentée avec niveau de confiance
~~~

## 7. Mémoire vive et données volatiles

La mémoire peut contenir des processus actifs, des connexions, des modules chargés, des objets en mémoire, des fragments de commandes et des données qui ne sont pas encore écrites sur disque. Son analyse peut aider à comprendre un incident actif ou un état qui disparaîtrait après un redémarrage. Elle est toutefois complexe : la capture peut être partielle, l'OS peut changer pendant l'acquisition, les profils ou symboles peuvent être incompatibles et certains résultats peuvent être ambigus.

La capture de mémoire doit suivre une procédure approuvée et être réalisée avec un outil adapté à l'OS et à la version. Notez la source, la date, l'heure, l'outil, la version, les paramètres, les privilèges employés, la destination et l'empreinte du fichier obtenu. Stockez la capture comme une preuve sensible : elle peut contenir des jetons, des identifiants, des données personnelles et des secrets applicatifs. Restreignez son accès et définissez sa conservation.

L'analyse de mémoire utilise des vues différentes : inventaire des processus, connexions déclarées, modules, descripteurs, lignes de commande disponibles et structures propres à l'OS. Un résultat absent peut signifier que la structure n'a pas été reconnue, que la capture est incomplète, ou que l'artefact n'existait pas. Toute conclusion importante doit être recoupée avec des journaux ou des sources indépendantes.

~~~text
Capture mémoire autorisée
       |
       v
Empreinte + métadonnées de capture
       |
       v
Validation OS / version / symboles
       |
       v
Vue processus + connexions + modules
       |
       v
Comparaison avec journaux EDR et système
       |
       v
Rapport avec artefacts et limites
~~~

### 7.1 Processus et connexions

Un processus doit être identifié par plus que son nom. Relevez si disponibles le PID, l'heure de création, le processus parent, l'utilisateur, le chemin de l'exécutable, la signature, la ligne de commande, les modules chargés et les connexions associées. Les PID sont réutilisés ; un PID identique à deux moments différents ne suffit pas à affirmer qu'il s'agit du même processus.

Une connexion peut être associée à un processus par la télémétrie endpoint, par une capture appropriée ou par les tables d'état au moment de la collecte. Le lien peut manquer si la connexion a déjà fermé, si les données ont été tronquées ou si la source ne conserve pas cette association. La présence d'une connexion ne révèle pas automatiquement le contenu transféré, particulièrement si l'application utilise le chiffrement.

### 7.2 Valeur et limites de la mémoire

La mémoire ne remplace pas les journaux réseau ou la preuve sur disque. Certaines données ne sont pas résidentes, ont été paginées, chiffrées ou réutilisées ; les structures changent selon la version de l'OS. Les outils peuvent produire des faux positifs lorsque leur profil ne correspond pas au système. Présentez les résultats d'analyse comme des observations de l'outil, puis expliquez ce qui a été corroboré.

## 8. Forensique réseau : ce que les traces prouvent

L'investigation réseau peut s'appuyer sur des captures de paquets (PCAP), des journaux de pare-feu, des résolveurs DNS, des proxys, des équilibreurs de charge, des flux NetFlow/IPFIX, des journaux d'authentification réseau, des IDS/IPS et des métadonnées cloud. Chaque source répond à des questions différentes. Une capture de paquets peut contenir des détails protocolaires, mais elle est limitée aux interfaces, à la durée et aux paquets effectivement capturés. Un journal de flux résume plutôt des échanges et peut ne pas contenir le contenu applicatif.

Un DNS observé démontre une requête vue par le résolveur, pas nécessairement une connexion au serveur. Un SYN TCP peut démontrer une tentative de début de connexion sans prouver qu'un échange applicatif a abouti. Une connexion établie peut ne pas révéler le contenu chiffré. Un volume élevé peut correspondre à une sauvegarde, un téléchargement légitime, une mise à jour ou une exfiltration ; le contexte décide quelles hypothèses sont plausibles.

Avant l'analyse, vérifiez l'interface, l'heure, le filtre de capture, les pertes de paquets, le point d'observation et les limites de rétention. Une capture prise sur le serveur peut ne pas montrer le trafic bloqué plus en amont ; un port miroir configuré de manière incorrecte peut omettre certains paquets. Notez les zones que la preuve ne couvre pas.

~~~text
Question : quelle activité réseau est documentée ?
       |
       +--> DNS : demande / réponse / code de résultat
       |
       +--> Pare-feu : règle et décision
       |
       +--> Flux : source, destination, volume, durée
       |
       +--> PCAP : paquets capturés et protocoles
       |
       +--> Proxy : requête, réponse, identité si disponible
       |
       v
Croiser les sources au lieu de surinterpréter une seule
~~~

## 9. Wireshark : capture, filtres et bonnes pratiques

Wireshark est un analyseur de protocoles qui permet d'examiner les paquets capturés. Un filtre de capture est appliqué avant ou pendant la capture pour limiter ce qui est enregistré ; un filtre d'affichage réduit les paquets visibles dans la liste après ouverture du fichier. Ces deux syntaxes sont différentes. Un filtre d'affichage ne supprime pas les paquets du fichier source, et un filtre de capture peut empêcher de recueillir des informations utiles si le périmètre est mal compris.

Exemples de filtres d'affichage dans un PCAP pédagogique :

~~~text
Afficher le trafic TCP :
tcp

Afficher les requêtes DNS :
dns

Afficher les paquets HTTP :
http

Filtrer une adresse IP source :
ip.src == 192.0.2.25

Filtrer les connexions vers un port TCP :
tcp.dstport == 443

Chercher les flux vers une IP de documentation :
ip.addr == 198.51.100.20
~~~

Les plages 192.0.2.0/24 et 198.51.100.0/24 sont utilisées à titre documentaire. Dans un réseau réel, remplacez les valeurs uniquement par celles dont l'examen est autorisé. Les filtres ci-dessus sont des exemples de syntaxe ; les champs disponibles dépendent du protocole et de la version de Wireshark.

Un filtre de capture compatible libpcap peut par exemple se limiter à un hôte ou à un sous-réseau ; sa syntaxe n'est pas celle des filtres d'affichage. Testez le filtre sur une petite capture autorisée, vérifiez les compteurs de perte et conservez la valeur exacte utilisée. Ne filtrez pas trop tôt si la question dépend d'un protocole inattendu ou d'une relation entre flux différents.

~~~text
Source autorisée
     |
     v
Capture contrôlée + heure de début/fin
     |
     v
Vérifier pertes / interface / taille
     |
     v
Calculer l'empreinte du PCAP original
     |
     v
Filtre d'affichage pour l'analyse
     |
     v
Exporter uniquement les résultats nécessaires
~~~

### 9.1 Interpréter une poignée de main TCP

Une séquence TCP typique commence par SYN, puis SYN-ACK, puis ACK. Un SYN observé seul peut correspondre à une tentative, un paquet retransmis ou une capture incomplète. Un SYN-ACK indique que la destination a répondu à la tentative ; l'analyse complète doit vérifier si la poignée de main a été achevée et si des données applicatives ont suivi. Les réinitialisations, retransmissions et délais d'attente doivent être interprétés selon la topologie et les pertes de capture.

~~~text
Client                         Serveur
  |                               |
  |---------- SYN --------------->|
  |<-------- SYN-ACK -------------|
  |---------- ACK --------------->|
  |<====== échange éventuel =====>|
  |                               |
  +-- absence de réponse : vérifier route,
      filtrage, capture et disponibilité
~~~

### 9.2 DNS, HTTP et TLS

Les métadonnées DNS peuvent révéler un nom demandé, un type de requête, une réponse et un code de résultat, si le point de capture voit ces paquets. Le DNS chiffré et les caches peuvent limiter ce qui apparaît. Une requête DNS n'est pas équivalente à un accès applicatif. Pour les protocoles HTTP non chiffrés, la capture peut contenir des champs lisibles sensibles ; leur conservation et leur diffusion doivent être restreintes. TLS protège le contenu, mais des métadonnées telles que les adresses, durées, tailles et certaines informations de négociation peuvent rester visibles selon la version et le contexte.

Ne tentez pas de contourner le chiffrement ni d'intercepter des communications d'utilisateurs hors autorisation. Pour l'apprentissage, utilisez une capture synthétique ou un service local conçu pour la formation. Si un contenu sensible apparaît accidentellement, suivez la procédure de minimisation et de protection des données ; ne le reproduisez pas dans un rapport général.

## 10. Corréler réseau et système

La corrélation sert à relier les événements provenant de sources distinctes. Un événement endpoint peut identifier un PID ; une capture réseau donne une connexion à une heure donnée ; le proxy peut relier une requête à un utilisateur ; DNS peut montrer la résolution ; un journal d'authentification peut contextualiser la session. La relation ne doit être acceptée que si les horodatages, identifiants et chemins sont compatibles.

Normalisez les heures en UTC lorsque cela est adapté, en gardant la valeur originale et le fuseau source. Consignez la dérive estimée de l'horloge, la latence d'ingestion et les zones sans données. Pour un lien processus-connexion, vérifiez la source qui effectue cette association : un simple rapprochement à la minute près est moins solide qu'un identifiant endpoint explicite.

Un analyste doit aussi chercher les explications alternatives : sauvegarde planifiée, outil de déploiement, vérification de santé, scanner de sécurité, système de mise à jour ou usage normal inhabituel. Une activité atypique n'est pas toujours un incident. Le rapport doit expliquer pourquoi une hypothèse est retenue plutôt qu'une alternative, ou déclarer que les éléments ne permettent pas de trancher.

~~~text
Journal endpoint          DNS             Proxy / pare-feu
     |                     |                    |
     v                     v                    v
création processus      requête nom          tentative / décision
     |                     |                    |
     +----------- horodatage normalisé --------+
                           |
                           v
               Chronologie corrélée
                           |
                           v
          Hypothèse avec preuve et alternatives
~~~

## 11. Construire une chronologie fiable

La chronologie est souvent le cœur du dossier. Pour chaque événement, enregistrez au minimum : identifiant, date et heure source, fuseau, heure normalisée, source, hôte, compte, action, résultat, identifiants de corrélation, référence à la preuve et niveau de confiance. Ne modifiez pas l'heure originale ; ajoutez un champ normalisé séparé et documentez la conversion.

Distinguez l'heure à laquelle l'événement s'est produit, l'heure à laquelle il a été enregistré et l'heure à laquelle il est arrivé dans le SIEM. Une ingestion retardée peut inverser l'ordre apparent. Les dates de fichiers peuvent indiquer la dernière modification plutôt que la date de présence initiale. Les horloges de plusieurs appareils peuvent dériver. Ces effets doivent être pris en compte avant de déduire une séquence causale.

Une chronologie ne doit pas cacher les trous. Marquez les fenêtres sans télémétrie et les sources qui ne couvrent qu'une partie des systèmes. Lorsque deux sources semblent contradictoires, vérifiez les définitions et les horloges avant de choisir l'une des versions.

~~~text
14:02:11 UTC  Authentification inhabituelle (IAM)
14:02:16 UTC  Création de processus (endpoint)
14:02:22 UTC  Requête DNS (résolveur)
14:02:25 UTC  Connexion refusée (pare-feu)
14:07:40 UTC  Alerte générée (EDR)
14:09:03 UTC  Événement reçu par le SIEM
       |
       v
Événement != heure d'ingestion
~~~

Les horaires sont fictifs et illustrent des sources distinctes. Dans un dossier réel, l'analyste doit confirmer les identifiants de machine, l'identité de la source, les horloges et la couverture avant d'attribuer un lien causal. L'alerte émise à 14:07 n'indique pas nécessairement que le comportement a commencé à 14:07.

## 12. Analyse de flux, volumes et comportements réseau

Les journaux de flux peuvent fournir les adresses source et destination, les ports, le protocole, la durée, le nombre d'octets et les flags TCP selon l'exporteur. Ils sont utiles pour comprendre les volumes, les conversations longues, les destinations rares ou les changements de comportement. Ils ne donnent pas toujours les URLs, les noms de processus ou le contenu des échanges ; ils ne doivent pas être traités comme un PCAP complet.

Un comportement réseau doit être défini par rapport à une base de référence : serveur qui parle normalement à ses mises à jour, poste qui communique vers des services cloud, équipement qui envoie des sauvegardes nocturnes ou contrôleur qui échange périodiquement avec ses capteurs. La rareté d'une destination est un indice à qualifier, pas une conclusion. Les adresses hébergées sur des infrastructures partagées peuvent desservir de nombreux services légitimes.

Comparez les volumes, périodes, destinations, protocoles et identités. Examinez les changements de fenêtres temporelles et les sources qui les confirment. Une hausse soudaine peut être un incident, une tâche planifiée, une erreur applicative ou une panne produisant des répétitions. Documentez les hypothèses et vérifiez par une source différente chaque fois que c'est possible.

~~~text
Flux A : volume ordinaire, destination habituelle
Flux B : volume inhabituel, destination nouvelle
Flux C : retries répétés, réponse absente
        |
        v
Comparer à la base de référence
        |
        +--> fenêtre de maintenance ?
        +--> changement applicatif connu ?
        +--> décision pare-feu / proxy ?
        +--> processus ou compte à l'origine ?
        |
        v
Escalade selon preuve, portée et impact
~~~

## 13. Images disque et systèmes de fichiers

Une image disque est une représentation acquise d'un support ou d'un volume. Les méthodes d'acquisition varient selon l'OS, le stockage, le chiffrement, le système de fichiers et le niveau d'intervention autorisé. Une image peut être physique ou logique ; ces termes ne sont pas interchangeables. Une collecte logique se limite souvent aux éléments visibles ou sélectionnés, tandis qu'une acquisition plus complète peut inclure des zones qui ne sont pas exposées par le système de fichiers actif.

Le choix de la méthode dépend de la question, de l'impact et de l'autorisation. N'improvisez pas une copie brute sur un système critique : une erreur de périphérique ou de sens source-destination peut détruire des données. Utilisez un environnement contrôlé, des procédures validées, un stockage suffisant et une vérification après acquisition. Dans les exercices de ce cours, travaillez avec une image pédagogique déjà fournie ou un dossier de fichiers créé pour l'étude.

Les outils d'analyse de systèmes de fichiers comme The Sleuth Kit et son interface graphique Autopsy peuvent aider à examiner des métadonnées, fichiers, chronologies et empreintes. L'outil ne remplace pas la validation de la source. Un résultat d'indexation ou de recherche doit être relié à l'image, au chemin, à la méthode et aux limites de la récupération.

~~~text
Support autorisé
      |
      v
Méthode d'acquisition validée
      |
      v
Image / export + journal d'opérations
      |
      v
Empreinte et contrôle post-acquisition
      |
      v
Copie de travail en lecture seule si possible
      |
      v
Examen du système de fichiers
~~~

### 13.1 Fichiers supprimés, espace non alloué et limites

La suppression d'un fichier peut retirer une référence au fichier sans effacer immédiatement tous ses octets. Une récupération dépend toutefois des écritures ultérieures, du système de fichiers, de l'allocation, du chiffrement et des mécanismes de nettoyage. Les SSD peuvent appliquer des commandes de récupération d'espace ou des mécanismes internes qui réduisent les chances de récupération. Un résultat partiel doit être décrit comme partiel.

L'absence d'un fichier dans une image logique ne prouve pas qu'il n'a jamais existé. À l'inverse, un nom de fichier retrouvé dans une entrée supprimée ne prouve pas que le contenu soit intact ni que le fichier ait été ouvert. Expliquez la portée de l'acquisition et utilisez des sources complémentaires comme les journaux, les sauvegardes et la télémétrie endpoint.

## 14. Hashes, filtrage et identification d'artefacts

Les empreintes aident à identifier les mêmes octets et à comparer des copies. Le filtrage par hash peut réduire le volume de fichiers connus et légitimes, mais il dépend de la fiabilité et de la date du référentiel. Un fichier recompilé, modifié ou emballé différemment aura une empreinte différente. Une empreinte ne permet pas de conclure à elle seule que deux fichiers sont fonctionnellement identiques.

En forensique, chaque empreinte doit être liée au bon artefact, à la bonne acquisition et à l'outil utilisé. Évitez de mélanger l'empreinte du fichier original, celle d'une archive et celle d'un export extrait. Si un outil transforme un fichier ou normalise un journal, calculez une nouvelle empreinte et indiquez clairement qu'il s'agit d'une version transformée.

~~~text
E-015 original.txt   SHA-256 = H1
        |
        +--> copie conforme.txt   SHA-256 = H1
        |
        +--> version nettoyée.txt SHA-256 = H2
                                  |
                                  v
             Transformation documentée, pas substitution
~~~

Une liste de hashes connus doit être versionnée, sourcée et adaptée à l'environnement. Évitez la suppression automatique de preuves uniquement parce qu'un hash correspond à une liste « connue bonne » : les logiciels légitimes peuvent être compromis, et les listes peuvent avoir des lacunes. Gardez les éléments d'origine et expliquez toute décision de filtrage.

## 15. Distinguer faits, inférences et hypothèses

Un fait analytique est une observation directement soutenue par une source qualifiée : « le journal du proxy indique une requête à 14:02 UTC » ou « l'empreinte de deux copies est identique ». Une inférence est une interprétation fondée sur plusieurs faits : « les événements semblent être reliés à la même session ». Une hypothèse est une explication encore à tester : « le processus a pu initier la communication ». Une décision est une action prise par une autorité responsable à partir de ces éléments.

Le vocabulaire doit refléter ces différences. Utilisez « observé », « indiqué par la source », « cohérent avec », « suggère », « non confirmé » et « non démontré » avec précision. Évitez « prouve » lorsque la source ne peut soutenir qu'une partie de l'affirmation. Conservez les hypothèses alternatives et indiquez comment les tester.

~~~text
FAIT
"Le proxy rapporte une requête HTTP à 14:02."
     |
     v
INFÉRENCE
"La requête peut être liée à l'activité de LAB-07."
     |
     v
TEST
"Comparer identité, chemin de processus et horodatages."
     |
     v
CONCLUSION
"Relation confirmée / probable / non établie avec les sources disponibles."
~~~

Le niveau de confiance n'est pas une décoration. Expliquez les critères : qualité et indépendance des sources, intégrité, couverture, répétabilité, alternatives testées et cohérence temporelle. Plusieurs alertes provenant de la même source ne constituent pas forcément plusieurs preuves indépendantes. Une source secondaire copiée dans plusieurs tableaux de bord reste une seule origine.

## 16. Outils courants et choix raisonné

**Wireshark** permet d'inspecter des paquets et des protocoles. **tshark** fournit des fonctions en ligne de commande adaptées aux analyses reproductibles de captures. **The Sleuth Kit** et **Autopsy** permettent l'examen de systèmes de fichiers, des métadonnées et de chronologies. **Volatility** est une famille d'outils d'analyse de mémoire ; la compatibilité dépend de la capture et des symboles ou profils disponibles. Les journaux système, les outils EDR et le SIEM complètent ces outils en apportant du contexte opérationnel.

Chaque outil doit avoir une question, une entrée identifiée et un résultat attendu. Une sortie volumineuse n'est pas automatiquement une preuve pertinente. Enregistrez la version de l'outil, les options, les filtres, les fichiers d'entrée et les erreurs. Pour des analyses importantes, faites valider les résultats par un second analyste et vérifiez le comportement sur des données de test dont les propriétés sont connues.

Les outils évoluent ; vérifiez la documentation officielle avant de reprendre une commande ou une procédure. Les noms de champs, les plugins, les symboles, les formats et les filtres peuvent différer entre versions. Ne copiez pas une commande depuis un forum sans comprendre les paramètres, son effet et la portée de ses entrées.

~~~text
Question précise
      |
      v
Outil adapté et version identifiée
      |
      v
Entrée vérifiée + paramètres sauvegardés
      |
      v
Résultat contrôlé sur données connues
      |
      v
Sortie interprétée + limites documentées
~~~

## 17. Confidentialité et minimisation

Les preuves numériques peuvent contenir des mots de passe en mémoire, jetons de session, documents confidentiels, informations personnelles, historiques de navigation ou données médicales. Le fait qu'une donnée soit techniquement accessible ne signifie pas qu'elle soit nécessaire à l'investigation. Collectez ce qui est raisonnablement nécessaire pour répondre à la question, limitez les accès, utilisez un stockage contrôlé et définissez les règles de conservation et de suppression.

Les captures réseau sont particulièrement sensibles : une capture peut contenir des requêtes applicatives, des noms internes, des identifiants transmis sans protection ou des données personnelles. Le contenu ne doit pas être ajouté intégralement à un rapport si quelques métadonnées suffisent. Les exports destinés à partager un indicateur doivent être nettoyés, expurgés et vérifiés avant diffusion.

Prévoyez un traitement pour les découvertes incidentes : arrêter l'examen concerné si nécessaire, protéger les informations, avertir le responsable désigné et noter les actions. Ne déplacez pas les preuves sensibles vers un service de réputation externe sans autorisation. Les règles de l'organisation et les obligations légales doivent être examinées avant la collecte et le partage.

~~~text
Preuve collectée
      |
      v
Contient-elle des données sensibles ?
      |
   +--+--+
   |     |
  oui   non
   |     |
Minimiser,     Accès restreint
restreindre,  et conservation définie
expurger si besoin
   |     |
   +--+--+
      |
      v
Partager le strict nécessaire via canal approuvé
~~~

## 18. Analyse d'incident et chronologie multi-source

Les incidents combinent souvent plusieurs systèmes : endpoint, identité, réseau, cloud, application et ticketing. Chaque source a sa propre rétention et son schéma. Une chronologie centrale permet de visualiser la succession des événements, mais les événements doivent conserver leur provenance et leur référence originale. Ne copiez pas uniquement le texte visible dans un tableau si le lien vers la source peut être conservé.

Créez un dictionnaire des champs : hôte, identité, IP, nom DNS, PID, session, identifiant d'événement, heure source, heure UTC, action, résultat et provenance. Les noms ne sont pas toujours uniques ; un nom d'utilisateur peut être renommé, une adresse IP réattribuée et un PID réutilisé. Les clés de corrélation devraient être aussi précises que possible et leur portée doit être documentée.

La reconstruction doit expliquer le début plausible, l'activité confirmée, les limites d'étendue, les systèmes concernés, les mesures de réponse et les inconnues. N'attribuez pas automatiquement un acte à une personne parce qu'un compte est mentionné ; les comptes partagés, sessions volées et outils automatiques exigent une analyse spécifique.

~~~text
Identité / IAM       Endpoint            Réseau
     |                   |                 |
authentification     lancement          DNS / flux
     |                   |                 |
     +------ correspondance temporelle -----+
                          |
                          v
                  Étendue hypothétique
                          |
                          v
            Sources supplémentaires à vérifier
~~~

## 19. Erreurs et pièges d'interprétation

**Erreur 1 :** redémarrer une machine avant de considérer la volatilité. Le redémarrage peut détruire l'état de mémoire et des connexions. La décision doit correspondre à l'urgence de confinement et à la question d'analyse.

**Erreur 2 :** croire que le hash garantit l'authenticité. Il vérifie l'identité des octets entre deux moments ou copies, mais ne prouve pas que l'échantillon était la bonne preuve au départ.

**Erreur 3 :** assimiler événement DNS et connexion réseau. La résolution, la tentative TCP, la session établie et le transfert applicatif sont des états distincts qui demandent des sources différentes.

**Erreur 4 :** confondre filtres de capture et filtres d'affichage. Le premier limite les données enregistrées ; le second masque temporairement certains paquets à l'écran.

**Erreur 5 :** supposer qu'un horodatage de fichier indique l'heure de l'action malveillante. Le fichier peut être copié, extrait d'une archive, restauré ou modifié par un outil.

**Erreur 6 :** présenter une absence de journal comme une preuve d'absence. Il faut d'abord connaître l'état de la collecte, la rétention, les filtres, les pertes et les horloges.

**Erreur 7 :** faire une acquisition sans connaître sa source et sa destination. Une erreur de périphérique peut détruire les données que l'on voulait préserver. Utilisez un plan validé et un opérateur formé.

**Erreur 8 :** extraire tout un PCAP dans un rapport partagé. La capture peut contenir des secrets et des données personnelles. Partagez le strict nécessaire.

~~~text
Piège                     Réflexe rigoureux
-----                     ----------------
Redémarrage immédiat      Évaluer les données volatiles
Hash égal = preuve sûre   Distinguer intégrité et authenticité
DNS = connexion           Vérifier TCP / proxy / flux
Horodatage local seul     Conserver l'heure source et normaliser
Pas d'événement = rien    Vérifier couverture et rétention
PCAP entier diffusé       Minimiser et protéger les données
~~~

## 20. Travaux pratiques guidés

Les travaux pratiques utilisent des fichiers texte, des journaux synthétiques et une capture réseau préparée pour l'enseignement. Ils n'exigent aucun accès à un tiers, aucune capture du réseau d'une entreprise et aucune acquisition brute d'un disque de production. Préparez un répertoire de cours distinct, indiquez une heure de référence et conservez les sorties afin de permettre la correction.

### TP 1 — Fiche de preuve et vérification d'intégrité

**Objectif.** Créer une fiche d'élément de preuve et vérifier une copie d'un fichier inoffensif.

**Préparation.** Créez un fichier texte contenant quelques lignes fictives et nommez-le journal-labo.txt. Attribuez l'identifiant E-001. Notez l'origine, l'heure UTC, l'opérateur, le motif de collecte et l'emplacement du fichier original. Calculez son SHA-256 à l'aide de l'outil disponible.

**Étapes.** Copiez le fichier dans un dossier d'analyse, calculez l'empreinte de la copie, comparez les valeurs et consignez le résultat. Ne modifiez pas l'original. Faites ensuite une nouvelle copie de travail et ajoutez un caractère uniquement à celle-ci ; recalculez son empreinte pour observer la différence. Documentez cette modification comme transformation volontaire du TP.

**Livrable.** Fiche E-001, empreinte initiale, empreinte de la copie intacte, empreinte de la copie modifiée, heures et journal d'opérations.

**Correction attendue.** L'original et la copie intacte doivent produire la même empreinte. La copie modifiée doit produire une empreinte différente. La conclusion correcte concerne l'intégrité octet pour octet, pas la sûreté ou l'authenticité du contenu.

**Critères de réussite.** Les fichiers sont clairement distingués, les empreintes sont reliées à leur nom et l'opérateur ne remplace pas une valeur différente sans explication.

### TP 2 — Construire une chronologie système

**Objectif.** Corréler des événements fictifs sans transformer la proximité temporelle en causalité.

**Données.** Le jeu fourni indique : à 10:05:02 UTC, une connexion utilisateur réussit sur LAB-03 ; à 10:05:12, le journal endpoint mentionne un processus créé ; à 10:06:01, un service d'inventaire démarre ; à 10:06:14, l'EDR crée une alerte pour un enfant inattendu ; à 10:08:00, un ticket annonce une maintenance d'inventaire autorisée de 10:00 à 10:15.

**Étapes.** Créez une table avec l'heure source, la source, l'hôte, l'identité, l'événement, l'état de confirmation et l'hypothèse associée. Identifiez les données qui permettent de relier le processus à l'utilisateur ; si ces identifiants manquent, marquez le lien comme inconnu. Comparez ensuite l'événement au ticket de maintenance sans supposer que le ticket explique nécessairement tous les événements.

**Livrable.** Chronologie et bref commentaire comprenant deux faits confirmés, deux hypothèses et une requête de vérification supplémentaire.

**Correction attendue.** Les journaux rapportés montrent les événements aux heures indiquées et le ticket décrit une plage de maintenance. Le ticket rend une explication légitime plausible mais ne prouve pas que l'alerte est bénigne. Il faut vérifier le compte de service, le processus parent, la version de l'outil d'inventaire et les détails de l'alerte.

**Critères de réussite.** Les heures restent en UTC, les observations sont séparées des hypothèses et les données manquantes sont nommées.

### TP 3 — Examiner un PCAP pédagogique

**Objectif.** Distinguer requête DNS, tentative de connexion, réponse du serveur et transfert de données à partir d'un PCAP fourni par le formateur.

**Préparation.** Utilisez une capture pédagogique qui ne contient pas de communications réelles sensibles. Consignez le nom du fichier, la taille, l'empreinte, la période couverte et la provenance. Ouvrez le fichier dans Wireshark sans démarrer une capture live.

**Étapes.** Appliquez le filtre d'affichage dns, puis tcp. Relevez les heures, adresses documentaires, ports, flags et réponses. Trouvez un exemple de requête DNS bloquée ou sans réponse et un exemple de poignée de main TCP complète, si le jeu de données les contient. Si l'exemple demandé n'existe pas, écrivez qu'il n'est pas présent dans la capture au lieu de l'inventer.

**Livrable.** Tableau avec numéro de paquet ou référence de flux, filtre utilisé, observation exacte, interprétation possible et limite de preuve.

**Correction attendue.** Le filtre d'affichage sélectionne les paquets visibles mais ne modifie pas le PCAP. Une requête DNS ne prouve pas une connexion. Un SYN sans réponse prouve seulement que le paquet SYN est présent dans la capture ; il ne suffit pas à déterminer pourquoi aucune réponse n'apparaît. Une poignée de main complète permet d'établir qu'un échange TCP a été initié, sans démontrer à elle seule un contenu applicatif précis.

**Critères de réussite.** Les filtres sont notés, les sources et limites sont explicites et aucune donnée réelle hors périmètre n'est recherchée.

### TP 4 — Rapport multi-source et recommandations

**Objectif.** Rédiger un rapport court à partir d'événements système et réseau synthétiques.

**Données.** Un jeu de journaux montre qu'à 15:10 UTC une connexion est établie par un poste pédagogique vers l'adresse documentaire 198.51.100.20, que le proxy enregistre ensuite une réponse HTTP et que l'EDR détecte un processus non habituel. Le propriétaire de l'application indique qu'une maintenance est prévue le même jour, mais le dossier ne contient pas encore le numéro de changement ni l'identité du compte ayant lancé le processus.

**Étapes.** Séparez les faits par source. Construisez la chronologie, notez les éléments concordants, précisez les lacunes et proposez les vérifications supplémentaires. Formulez une recommandation proportionnée au risque et indiquez quelle autorité doit décider d'une isolation. N'inventez ni contenu HTTP ni volume transféré si la donnée n'existe pas dans le jeu.

**Livrable.** Rapport avec résumé exécutif, périmètre, preuves, faits, hypothèses, niveau de confiance, actions recommandées et limites.

**Correction attendue.** Les sources données indiquent une connexion établie, une réponse proxy et une alerte endpoint dans une même fenêtre ; le lien exact entre le processus et la connexion doit être corroboré. La maintenance est une explication possible mais demande le ticket, le compte et les métadonnées de processus. Les données fournies ne démontrent pas à elles seules une exfiltration. L'équipe doit examiner la télémétrie endpoint, les détails proxy et le changement autorisé, puis décider des mesures en fonction de l'activité actuelle et du risque.

**Critères de réussite.** Le rapport est factuel, compréhensible et reproductible ; il n'affirme pas plus que ce que les sources permettent d'établir.

## 21. Exercices corrigés

### Exercice 1 — Preuve numérique
Vous recevez un export de journaux sans indication de l'hôte source. Peut-il être directement traité comme une preuve complète ?

**Correction.** Non. Il faut retrouver la provenance, le système, la période, le fuseau, les filtres et l'opérateur. Sans ces informations, le résultat est difficile à interpréter et à reproduire. Notez la lacune et demandez un nouvel export ou des métadonnées vérifiables.

### Exercice 2 — Hash identique
Deux copies ont la même empreinte SHA-256. Qu'est-ce que cela établit ?

**Correction.** Les octets correspondent avec une forte assurance pratique selon l'algorithme utilisé. Cela n'établit ni l'authenticité de l'origine, ni la complétude de la collecte, ni l'absence de comportement dangereux.

### Exercice 3 — Hash différent
L'empreinte de la copie de travail ne correspond pas à l'original.

**Correction.** Ne masquez pas l'écart. Vérifiez les fichiers, transferts et transformations, identifiez la copie modifiée et documentez la résolution. Recalculez les empreintes à partir des bons éléments et préservez la preuve originale.

### Exercice 4 — Machine suspecte en fonctionnement
Un serveur affiche un comportement anormal et pourrait contenir des données mémoire importantes.

**Correction.** Évaluez l'urgence, la criticité, l'autorisation et les risques d'une collecte live. Coordonnez-vous avec la réponse à incident ; préservez les données volatiles si cela est justifié et sûr, ou confinez d'abord si la propagation impose cette priorité. Documentez les compromis.

### Exercice 5 — Redémarrage
Pourquoi ne pas redémarrer immédiatement un serveur suspect ?

**Correction.** Le redémarrage peut faire disparaître la mémoire, les processus et les connexions actives. Il peut néanmoins être nécessaire pour protéger l'organisation. Le choix dépend du risque et doit être décidé, justifié et consigné.

### Exercice 6 — Requête DNS
Une capture contient une requête DNS vers un nom rare.

**Correction.** Cela montre que la requête a été capturée, selon la source disponible. Il faut rechercher la réponse, le processus, le proxy, le pare-feu et le trafic correspondant. La rareté ne prouve pas l'intention.

### Exercice 7 — SYN seul
Le PCAP montre un SYN sortant sans réponse.

**Correction.** Il confirme la présence du paquet SYN dans la capture. La destination peut être indisponible, le trafic bloqué ou la capture incomplète. On ne peut pas conclure à une connexion établie.

### Exercice 8 — TCP établi
La poignée de main TCP est complète.

**Correction.** La connexion TCP a été initiée avec succès selon les paquets observés. Cela ne prouve pas la nature des données applicatives ni une exfiltration.

### Exercice 9 — Filtre Wireshark
Pourquoi la syntaxe tcp.port == 443 ne doit-elle pas être utilisée comme un filtre de capture libpcap ?

**Correction.** C'est une syntaxe de filtre d'affichage Wireshark. Les filtres de capture utilisent une syntaxe distincte, par exemple tcp port 443. Vérifiez le type de filtre avant de l'appliquer.

### Exercice 10 — Journaux absents
Un SIEM n'affiche rien pendant dix minutes.

**Correction.** Vérifiez l'agent, la rétention, les filtres, le transport, les erreurs d'ingestion, les horloges et la couverture. L'absence de résultat n'établit pas que le système n'a eu aucune activité.

### Exercice 11 — Heures contradictoires
Un événement endpoint semble postérieur à l'événement réseau alors que la logique attend l'inverse.

**Correction.** Conservez les heures originales, normalisez en UTC et examinez la dérive ainsi que la latence d'ingestion. Ne choisissez pas une séquence avant d'avoir compris les horloges.

### Exercice 12 — Fichier supprimé
Un nom de fichier est retrouvé dans les métadonnées d'une image disque, mais pas son contenu.

**Correction.** Le nom peut indiquer une entrée de fichier supprimée, mais le contenu n'est pas disponible ou récupérable dans l'image. Ne concluez pas que le contenu est intact ou qu'il a été ouvert.

### Exercice 13 — Service nouveau
Un service a été créé récemment sur un serveur.

**Correction.** Comparez avec les changements autorisés, identifiez le compte créateur, la cible, la signature et les événements de processus. Un service nouveau est un indice, pas une preuve unique.

### Exercice 14 — Processus inconnu
Un processus porte un nom identique à celui d'un composant système.

**Correction.** Examinez chemin, empreinte, signature, PID, parent, compte, métadonnées et télémétrie. Le nom seul peut être usurpé ou légitime dans plusieurs contextes.

### Exercice 15 — PCAP volumineux
Une capture de plusieurs gigaoctets doit être partagée avec une autre équipe.

**Correction.** Vérifiez la nécessité du partage, la classification, le canal autorisé et les données sensibles. Partagez plutôt les paquets, métadonnées ou exports strictement nécessaires si cela répond à la question, en conservant la preuve originale sous contrôle.

### Exercice 16 — Connexion et alerte endpoint
Une connexion et une alerte apparaissent à quelques secondes d'écart.

**Correction.** La proximité temporelle ne prouve pas le lien. Recherchez l'association processus-connexion, les identifiants de session, la ligne de commande si collectée et les sources réseau correspondantes.

### Exercice 17 — Ticket de changement
Une opération anormale survient pendant une fenêtre de maintenance.

**Correction.** Le ticket rend une explication légitime plausible, mais doit être rapproché des systèmes, comptes, horaires et processus. L'analyste doit vérifier que le changement couvre réellement l'opération observée.

### Exercice 18 — Mémoire et secrets
Une capture mémoire peut contenir des jetons ou mots de passe.

**Correction.** Traitez-la comme une preuve très sensible, limitez les accès, protégez le stockage, partagez le strict nécessaire et appliquez les règles de conservation. Ne copiez pas les secrets dans un rapport non restreint.

### Exercice 19 — Résultat d'outil
Un outil forensique signale un artefact suspect.

**Correction.** Vérifiez la compatibilité de l'outil, la source, la version, les paramètres, les erreurs et les faux positifs. Corroborez par une source indépendante avant de formuler une conclusion importante.

### Exercice 20 — Rapport sans conclusion ferme
Les preuves permettent de confirmer certains événements mais pas la cause.

**Correction.** Le rapport doit décrire les faits établis, les hypothèses possibles, les limites et les prochaines vérifications. Une conclusion « cause non déterminée avec les données disponibles » est correcte lorsque les preuves sont insuffisantes.

## 22. Défi final — Reconstituer un incident sans surinterpréter

**Scénario fictif.** Le poste LAB-21 déclenche une alerte endpoint à 16:21 UTC. Un journal système indique la création d'un processus à 16:20:52. Le résolveur enregistre une requête DNS à 16:21:01 et le pare-feu journalise une tentative sortante bloquée à 16:21:03. Une capture prise sur une autre interface ne contient pas le flux correspondant. Le poste a redémarré à 16:24 selon le système de gestion. L'inventaire ne couvre pas les événements de 16:10 à 16:18.

**Travail demandé.** Préparez une fiche de preuve pour chaque source, normalisez la chronologie, séparez faits et hypothèses, identifiez les lacunes, expliquez pourquoi la capture peut ne pas montrer la tentative et proposez les collectes supplémentaires. Établissez un plan de réponse proportionné qui tient compte du redémarrage déjà intervenu, sans supposer que les données mémoire ont été préservées.

**Correction détaillée.**

1. **Faits observés.** Les journaux fournis mentionnent une création de processus à 16:20:52, une requête DNS à 16:21:01, une tentative bloquée à 16:21:03, une alerte à 16:21 et un redémarrage à 16:24. Les sources et la zone de temps doivent être conservées avec chaque observation.
2. **Chronologie.** Le processus précède de quelques secondes la requête DNS et le blocage selon les horodatages disponibles. Il faut vérifier la synchronisation et l'identité des événements avant d'affirmer une relation causale.
3. **Capture sans paquet correspondant.** L'interface peut ne pas voir le chemin concerné, le filtre de capture peut exclure le paquet, les paquets peuvent avoir été perdus, ou l'heure et la fenêtre ne sont pas alignées. Le PCAP n'infirme pas à lui seul le journal du pare-feu.
4. **Impact du redémarrage.** Il est probable que certaines données volatiles n'aient plus été accessibles après le redémarrage. Il faut chercher les journaux persistants, la télémétrie EDR, les événements de connexion et les sources réseau qui ont conservé l'état. Ne prétendez pas avoir acquis la mémoire pré-redémarrage.
5. **Lacunes.** L'inventaire absent entre 16:10 et 16:18 réduit la capacité à reconstruire une activité antérieure. Recherchez les logs de collecte, la rétention et d'éventuels exports complémentaires autorisés.
6. **Actions.** Préservez les données existantes, vérifiez l'activité actuelle et coordonnez une isolation ou une mesure de réponse selon la procédure et le risque. Cherchez d'autres systèmes avec les mêmes indicateurs dans une fenêtre justifiée, sans étendre le périmètre de manière automatique.
7. **Conclusion.** Une activité réseau suspecte a été signalée et une tentative est indiquée comme bloquée, mais les éléments ne démontrent ni une connexion réussie, ni le contenu transmis, ni la cause exacte. Le rapport doit expliciter ces limites et demander les sources nécessaires pour progresser.

**Barème sur 100 points.** Traçabilité et empreintes : 15. Chronologie et temps : 15. Distinction faits/hypothèses : 20. Lecture correcte des traces réseau : 15. Gestion des lacunes : 10. Plan défensif : 15. Qualité du rapport : 10.

## 23. Liste de contrôle opérationnelle

Avant la collecte, vérifiez l'autorisation, le périmètre, les règles d'arrêt, la criticité et les risques de confidentialité. Identifiez les sources et leur rétention, puis déterminez lesquelles sont volatiles. À la réception, enregistrez la provenance, l'heure et l'opérateur, calculez des empreintes lorsque cela est adapté et stockez les originaux de manière contrôlée. Pour chaque outil, notez la version, la source, les paramètres et les limites.

Pendant l'examen, gardez les données brutes séparées des exports transformés, conservez l'heure source en plus de l'heure normalisée, vérifiez la qualité de la collecte et reliez chaque conclusion à une preuve précise. Ne partagez pas un PCAP ou une capture mémoire entière si seules quelques métadonnées sont nécessaires. Toute action de confinement doit être décidée et journalisée selon la procédure de réponse.

Au moment de clore le dossier, vérifiez que les preuves peuvent être retrouvées, que la chaîne de conservation est cohérente, que les accès sont restreints et que la politique de rétention est appliquée. Le rapport doit indiquer les faits, les hypothèses, les limites, les décisions, les responsables et les prochaines actions. Une autre personne doit pouvoir comprendre et reproduire la logique.

~~~text
[ ] Autorisation et périmètre validés
[ ] Sources et rétention identifiées
[ ] Ordre de collecte justifié
[ ] Provenance et heures originales notées
[ ] Empreintes et copies vérifiées
[ ] PCAP et captures protégés
[ ] Fuseaux et dérive évalués
[ ] Faits distingués des hypothèses
[ ] Sources indépendantes recherchées
[ ] Données sensibles minimisées
[ ] Décisions et actions horodatées
[ ] Rapport relu et limites explicites
~~~

## 24. Glossaire

**Acquisition.** Collecte d'un support, fichier, export ou état d'un système par une méthode identifiée.

**Artefact.** Élément numérique utile à l'investigation : fichier, événement, métadonnée, entrée de configuration ou trace.

**Capture PCAP.** Fichier contenant les paquets réseau observés lors d'une capture.

**Chaîne de conservation.** Historique des transferts, accès, manipulations et lieux de stockage d'une preuve.

**Collecte live.** Collecte réalisée pendant que le système fonctionne, utile pour certaines données volatiles mais susceptible de modifier l'état.

**Données volatiles.** Données qui peuvent disparaître ou changer rapidement, comme les processus et connexions actives.

**Empreinte cryptographique.** Valeur calculée à partir des octets pour aider à comparer ou identifier un contenu.

**Forensique.** Méthode de préservation, d'examen et d'interprétation de traces afin de répondre à des questions documentées.

**Image disque.** Représentation acquise d'un support ou d'un volume, selon une méthode et un périmètre définis.

**Inférence.** Interprétation appuyée sur des faits, mais distincte d'une observation directe.

**IOC.** Indicateur de compromission ou élément observable utile à une recherche défensive.

**PCAP.** Format couramment utilisé pour stocker des paquets capturés.

**PID.** Identifiant numérique d'un processus dans un système ; il peut être réutilisé.

**Preuve originale.** Élément conservé dans l'état acquis, dont les copies de travail et transformations sont distinguées.

**SIEM.** Système qui collecte et corrèle des événements de plusieurs sources.

**Télémétrie endpoint.** Événements collectés sur les postes et serveurs, tels que processus, fichiers et connexions.

**Chronologie.** Présentation ordonnée d'événements avec leurs sources et horodatages.

**Faux positif.** Signal qui correspond au critère d'une détection sans relever du phénomène recherché.

**Faux négatif.** Événement recherché mais non détecté ou non visible dans la source considérée.

**Volatilité.** Capacité d'une donnée à disparaître ou à changer selon le temps et l'état du système.

## 25. Références officielles

- NIST SP 800-86, *Guide to Integrating Forensic Techniques into Incident Response* : https://csrc.nist.gov/pubs/sp/800/86/final
- NIST SP 800-101 Rev. 1, *Guidelines on Mobile Device Forensics* : https://csrc.nist.gov/pubs/sp/800/101/r1/final
- Guide utilisateur Wireshark : https://www.wireshark.org/docs/wsug_html/
- Référence des filtres Wireshark : https://www.wireshark.org/docs/man-pages/wireshark-filter.html
- Site officiel de The Sleuth Kit : https://www.sleuthkit.org/
- Site officiel d'Autopsy : https://www.autopsy.com/
- Documentation de Volatility : https://volatility3.readthedocs.io/
- Documentation de sécurité Microsoft : https://learn.microsoft.com/security/
- MITRE ATT&CK, base de connaissances des comportements adverses : https://attack.mitre.org/

Ces références apportent des bases méthodologiques et techniques. Les outils, systèmes et formats évoluent : vérifiez la documentation correspondant à la version réellement utilisée. Les guides techniques ne remplacent pas l'autorisation, la politique de protection des données ni les procédures internes.

## 26. Synthèse finale

La forensique réseau et système transforme un ensemble de traces en un récit vérifiable sans combler les lacunes par des suppositions. Son socle est l'autorisation, la préservation, la chaîne de conservation, la compréhension de la volatilité, la collecte adaptée, la normalisation du temps, la corrélation de sources distinctes et la documentation des limites.

Une capture réseau, un journal endpoint, une empreinte, une image disque et une capture mémoire n'ont ni la même portée ni les mêmes risques. Il faut les combiner selon une question précise et ne pas leur faire dire davantage que ce qu'elles montrent. L'analyste distingue toujours les faits observés, les inférences, les hypothèses et les décisions.

Le niveau expert se manifeste dans la qualité de la preuve et la prudence des conclusions : protéger les données sensibles, ne pas dépasser le périmètre, signaler les sources absentes, faire vérifier les résultats importants et rendre les actions reproductibles. Une conclusion rigoureuse peut laisser des questions ouvertes ; elle doit alors nommer clairement les éléments qui permettraient de les résoudre.

Fin du cours.