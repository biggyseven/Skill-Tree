# Gestion de parc (GLPI, OCS)

> **Mise en contexte**
>
> Un ordinateur est déplacé dans un autre service, un portable est remplacé et un serveur est réinstallé. Pourtant, l'inventaire indique encore l'ancien utilisateur, la mauvaise adresse réseau et une garantie expirée depuis deux ans. Un parc mal documenté ralentit le support, complique les audits et crée des risques de sécurité. La gestion de parc consiste à maintenir une vue fiable des actifs tout au long de leur cycle de vie.

## Objectifs du cours

À la fin du cours, tu sauras structurer un inventaire d'actifs, distinguer découverte technique et gestion de cycle de vie, comprendre les rôles complémentaires de GLPI et OCS Inventory, réconcilier les doublons et protéger les données collectées.

## 1. Qu'est-ce qu'un actif informatique ?

Un actif est un équipement, un logiciel, un service ou une ressource que l'organisation doit gérer. Pour chaque actif matériel, l'inventaire peut associer un identifiant interne, le type, le fabricant, le modèle, le numéro de série, l'état, l'emplacement, le responsable, la date d'acquisition, la garantie, la configuration réseau, le système, le niveau de criticité et les tickets liés.

Ne collecte que les attributs nécessaires. Un inventaire destiné au support n'a généralement pas besoin du contenu personnel des utilisateurs. Les champs qui identifient un utilisateur ou sa machine doivent respecter la politique de confidentialité de l'organisation.

## 2. Découverte technique et gestion d'actifs

La **découverte** identifie les équipements visibles sur le réseau ou rapporte des caractéristiques techniques depuis un agent. Un outil d'inventaire comme **OCS Inventory NG** collecte des informations de parc selon sa configuration. Un outil de gestion des services et des actifs comme **GLPI** peut centraliser les fiches, les affectations, les contrats, les tickets, les changements et les calendriers.

La collecte technique ne suffit pas à établir la vérité métier. Un agent peut rapporter un nom d'hôte et une mémoire installée, mais il ne sait pas nécessairement si le PC est attribué au bon service, couvert par un contrat ou en attente de réforme. Ces informations nécessitent une source et un processus de validation.

~~~mermaid
flowchart TD
    A[Agent ou découverte réseau] --> B[Inventaire technique]
    C[Achat, affectation et contrat] --> D[Référentiel des actifs]
    B --> D
    D --> E[Comparaison et contrôle]
    E --> F[Mise à jour validée]
    F --> G[Support, reporting et audit]
~~~

Le référentiel doit indiquer l'origine, la date et le statut de confiance des données. Une donnée découverte récemment peut être plus actuelle qu'une saisie ancienne, mais une valeur inattendue doit être contrôlée avant de remplacer une donnée validée.

## 3. Organiser le cycle de vie

Un cycle de vie simple comprend l'acquisition, l'enregistrement, la préparation, l'affectation, l'exploitation, la maintenance, le transfert, la réparation, puis la sortie du parc. Chaque étape doit posséder un responsable et une preuve adaptée : bon de réception, fiche d'actif, ticket d'affectation, rapport de réparation ou procès-verbal de sortie.

Au moment de la réception, vérifie l'identifiant matériel et le numéro de série. À l'affectation, enregistre le lieu et le responsable selon les règles de l'organisation. Lors d'un transfert, mets à jour l'emplacement et les relations avec le service. Avant la réforme, assure la récupération des données qui doivent être conservées, la révocation des accès et l'effacement sécurisé conforme à la politique applicable.

Un équipement retiré ne doit pas être simplement supprimé de l'inventaire : conserve un statut historique cohérent pour les audits, les garanties et les tickets anciens. La durée de conservation doit être définie par la politique et les obligations applicables.

## 4. Construire un inventaire fiable

Les données doivent être normalisées : mêmes conventions de nommage, mêmes catégories, unités cohérentes et identifiants stables. Le nom d'hôte et l'adresse IP peuvent changer ; le numéro de série ou l'identifiant interne a un rôle différent. Aucun champ isolé ne devrait être utilisé comme identifiant universel sans vérifier les cas de doublons et de réinstallation.

Contrôles réguliers :
- actifs sans responsable ou sans emplacement ;
- doublons de numéros de série ou d'identifiants internes ;
- actifs découverts mais absents du référentiel ;
- actifs enregistrés mais non vus depuis longtemps ;
- équipements hors support ou avec une garantie proche de l'expiration ;
- logiciels ou systèmes qui ne respectent plus la politique approuvée ;
- actifs réformés qui apparaissent toujours actifs dans la supervision.

Un poste absent depuis trente jours ne doit pas être automatiquement déclaré perdu : il peut être éteint, hors site ou réinstallé. Utilise les seuils comme signaux de vérification et documente la décision.

## 5. Collecter des informations techniques

Sur un poste Linux, ces commandes consultent des caractéristiques générales :

~~~bash
hostnamectl
ip -brief address
lscpu
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
~~~

La liste des interfaces et des disques peut révéler des informations sur l'environnement ; n'envoie les résultats que vers le référentiel approuvé. Sur Windows PowerShell, des commandes d'inventaire peuvent inclure :

~~~powershell
Get-CimInstance Win32_ComputerSystem | Select-Object Name, Manufacturer, Model
Get-CimInstance Win32_BIOS | Select-Object SerialNumber
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, LastBootUpTime
~~~

Exécute-les avec des droits appropriés et uniquement sur les machines autorisées. Certains champs peuvent être absents, modifiés par le fabricant ou répétés dans les environnements virtuels. Vérifie les résultats au lieu de considérer chaque valeur comme une preuve absolue.

## 6. Réconcilier les données

Une réconciliation fiable compare plusieurs sources : découverte technique, achats, affectation et tickets. Définis quelles sources font autorité pour chaque champ. Par exemple, le numéro de série vient normalement de l'étiquette ou d'une source constructeur vérifiée, le responsable vient du processus d'affectation et l'adresse IP vient de l'état réseau observé.

Lorsqu'une divergence est détectée :
1. conserve la valeur actuelle et sa date ;
2. consulte la source et l'heure de la nouvelle valeur ;
3. recherche un transfert, un remplacement ou une réinstallation ;
4. demande confirmation au propriétaire du processus si nécessaire ;
5. applique la correction avec une trace de qui l'a validée et pourquoi.

L'import automatique est utile, mais un script qui écrase toutes les données manuelles à chaque découverte peut effacer une information métier importante. Préfère des règles explicites par champ et une file de vérification pour les conflits.

## 7. Relier inventaire, tickets et décisions

L'inventaire devient utile quand le technicien peut retrouver l'actif depuis le ticket : historique des pannes, changements, pièces remplacées, garantie et contacts. Le ticket doit référencer un actif précis, pas seulement un nom générique tel que « ordinateur du bureau ». Cette relation permet ensuite de calculer les coûts, identifier un lot défectueux et prioriser les remplacements.

Un outil de gestion de parc n'élimine pas le besoin de gouvernance. Définis les profils d'accès, les champs obligatoires, les règles d'approbation, le traitement des doublons et une fréquence d'audit. Un compte d'inventaire ne doit pas recevoir des droits d'administration plus larges que nécessaire.

## Mise en pratique

### Laboratoire : créer puis réconcilier un mini-parc

Travaille avec des actifs fictifs ou un environnement explicitement autorisé. Crée quatre fiches : un poste fixe, un portable, un commutateur et un serveur de test. Pour chacun, renseigne un identifiant interne, le type, le fabricant/modèle si disponible, le numéro de série fictif, l'emplacement, le responsable métier, le statut, la date de dernière observation et les tickets associés.

Introduis ensuite trois écarts : un portable qui change d'utilisateur, un serveur dont le nom d'hôte a changé et une machine découverte mais absente du référentiel. Pour chaque cas, note la donnée détectée, la source faisant autorité, la décision de correction et la preuve conservée. Ne modifie pas automatiquement un champ si la source ne peut pas être vérifiée.

**Résultat attendu :** un inventaire cohérent, une liste de divergences traitées et un historique qui explique les changements. Le but n'est pas seulement d'avoir beaucoup d'enregistrements, mais de pouvoir justifier la fiabilité de chacun.

## Exercices corrigés

**1. OCS Inventory remonte le nom d'une machine, mais GLPI indique un autre responsable. Quelle action effectuer ?**

Correction : vérifier la fiche d'affectation, les tickets de transfert et l'horodatage des sources. La collecte technique ne constitue pas à elle seule une preuve de responsabilité métier. Corrige la fiche après validation et trace la modification.

**2. Pourquoi ne pas supprimer immédiatement un actif qui n'a pas été détecté depuis un mois ?**

Correction : il peut être hors site, éteint, en réparation ou réinstallé. Il faut lancer une vérification selon la procédure puis marquer un statut adapté en conservant l'historique.

**3. Le numéro de série est identique sur deux machines virtuelles. Quel enseignement en tirer ?**

Correction : le numéro peut être vide, générique ou cloné dans l'environnement. Il faut combiner plusieurs attributs, un identifiant interne stable et une règle de dédoublonnage adaptée.

**4. Quels risques crée un compte d'inventaire trop privilégié ?**

Correction : une compromission peut permettre d'administrer des machines ou de collecter trop de données. Applique le moindre privilège, sépare les rôles et contrôle les flux nécessaires.

## Défi final corrigé

Un audit révèle qu'un portable réformé apparaît encore comme actif, qu'un serveur récemment renommé est compté deux fois et qu'un nouveau commutateur n'a pas de responsable. Propose un traitement complet.

**Correction attendue :** vérifier les preuves de réforme et changer le statut du portable sans effacer son historique ; confirmer l'identité du serveur avec son identifiant stable, son numéro de série et ses relations, puis fusionner les fiches selon la procédure tout en préservant les tickets ; retrouver le propriétaire métier du commutateur et enregistrer l'affectation validée. Enfin, noter les causes des écarts, corriger la règle d'import ou la procédure de transfert qui les a provoqués et planifier une revue du parc.
