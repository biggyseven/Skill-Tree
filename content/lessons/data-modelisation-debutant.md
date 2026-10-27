# Modélisation et diagrammes (MCD/MLD) — Débutant

> **Mise en contexte.** Une application de formation commence avec quelques pages : des apprenants, des cours, des inscriptions et des résultats de quiz. Au début, l'équipe stocke tout dans un tableur ou dans quelques tables improvisées. Puis une personne suit plusieurs cours, un cours change de nom, une nouvelle session est ouverte, certains apprenants abandonnent et d'autres reprennent leur formation. Les mêmes informations se retrouvent copiées à plusieurs endroits. Personne ne sait exactement si une inscription représente un apprenant, une session, un cours ou une tentative. La solution ne consiste pas à ajouter des colonnes au hasard. Il faut d'abord comprendre les règles du métier, représenter les objets et leurs relations, puis traduire ce modèle en structures relationnelles cohérentes. C'est le rôle de la modélisation.

## 1. Objectifs pédagogiques

La modélisation est une étape de conception : elle transforme les besoins exprimés par les utilisateurs en une représentation structurée que l'équipe peut examiner avant de créer les tables. Ce cours présente la démarche dans l'esprit de MERISE, très utilisée dans les enseignements francophones : modèle conceptuel des données (MCD), puis modèle logique des données (MLD), avant d'aborder plus tard le modèle physique (MPD). Les outils et notations varient d'un environnement à l'autre, mais la distinction entre le sens métier, la structure relationnelle et les détails propres au SGBD reste utile.

À la fin de cette leçon, vous devrez être capable de distinguer une entité d'un attribut, reconnaître une association, expliquer une cardinalité minimale et maximale, repérer les identifiants, modéliser des relations un-à-plusieurs et plusieurs-à-plusieurs, transformer un MCD en MLD relationnel, choisir une clé primaire, représenter une association porteuse d'attributs et vérifier que le modèle couvre les règles métier énoncées. Vous apprendrez également à documenter les hypothèses et à éviter de représenter comme une entité chaque nom qui apparaît dans une phrase.

Le cours utilise comme fil conducteur une plateforme de formation. Les entités principales sont les apprenants, les cours, les sessions et les inscriptions. Nous ajouterons ensuite des évaluations et des résultats pour comprendre la différence entre le fait de suivre un cours et le fait de réussir une tentative. Le modèle sera volontairement limité : il doit être assez riche pour illustrer les concepts, sans prétendre décrire toute l'architecture d'une plateforme de production.

Vous devez déjà comprendre les tables, les clés et les requêtes SQL simples, notions étudiées dans les deux cours précédents. Ici, la priorité n'est pas d'écrire beaucoup de SQL. Il s'agit plutôt de décider quelles informations conserver, comment les relier et quelles règles doivent rester vraies. Une bonne modélisation réduit les ambiguïtés avant qu'elles ne deviennent des défauts dans le code ou dans les données.

Objectifs opérationnels :

- extraire les règles métier d'un texte ou d'un entretien ;
- distinguer entités, attributs, identifiants, associations et cardinalités ;
- lire une cardinalité \`(min,max)\` et expliquer sa signification dans les deux sens ;
- représenter les relations un-à-un, un-à-plusieurs et plusieurs-à-plusieurs ;
- distinguer l'identité d'un objet de ses propriétés susceptibles de changer ;
- transformer un MCD en tables, clés primaires et clés étrangères ;
- décider quand une association doit devenir une table d'association ;
- vérifier le MLD avec des scénarios valides et invalides ;
- repérer les hypothèses qui doivent être confirmées avec le métier ;
- préparer une structure qui pourra être implémentée dans SQL sans dépendre trop tôt d'un moteur particulier.

## 2. Prérequis, vocabulaire et périmètre

Le prérequis du parcours est **data-sql-1-debutant — Requêtes SQL de base (SELECT, INSERT)**. Vous devez comprendre ce qu'est une table, une ligne, une colonne, une clé primaire et une clé étrangère. Si vous avez du mal à expliquer pourquoi une commande doit référencer un client existant, reprenez la première leçon Data : la modélisation donne précisément un sens à ces contraintes.

### 2.1 Les termes essentiels

**Donnée** : une valeur enregistrée, par exemple une date d'inscription.

**Règle métier** : une condition que l'organisation considère comme vraie, par exemple « une inscription correspond à un seul apprenant » ou « un cours publié possède un titre ».

**Entité** : une catégorie d'objets ou de faits que le système doit reconnaître et sur laquelle il conserve des informations. Exemples : APPRENANT, COURS, SESSION.

**Occurrence** : un élément particulier d'une entité. « Amina Njoya » est une occurrence de l'entité APPRENANT si l'identité et les règles du système permettent de la reconnaître comme telle.

**Attribut** : une propriété qui décrit une entité ou une association, comme le nom d'un apprenant ou la date d'inscription.

**Identifiant** : un attribut ou un groupe d'attributs qui permet de distinguer une occurrence des autres.

**Association** : un lien métier entre des entités, comme « un apprenant s'inscrit à une session ».

**Cardinalité** : une indication sur le nombre minimum et maximum de participations possibles d'une occurrence à une association.

**MCD** : modèle conceptuel des données. Il décrit les entités, leurs attributs, les identifiants, les associations et les cardinalités avec un vocabulaire métier, sans détailler encore les tables d'un SGBD particulier.

**MLD** : modèle logique des données. Dans le cadre de ce cours, il représente le modèle relationnel sous forme de relations/tables, colonnes, clés et contraintes logiques.

**MPD** : modèle physique des données. Il précise les choix d'implémentation liés au SGBD : types exacts, index, paramètres, stratégie de partitionnement éventuelle et autres décisions physiques.

**Dictionnaire de données** : document qui donne le nom, la signification, le type conceptuel, les règles et les exemples des données.

Ces termes ne sont pas de simples étiquettes. Ils servent à séparer des questions différentes. « Un apprenant peut-il avoir plusieurs inscriptions ? » est une question de cardinalité. « Comment identifier un apprenant sans ambiguïté ? » est une question d'identifiant. « Faut-il une colonne UUID ou un entier généré ? » est un choix logique ou physique qui intervient plus tard, après que le besoin d'identité a été compris.

### 2.2 Pourquoi modéliser avant de créer les tables ?

Créer les tables directement à partir d'un écran ou d'un fichier existant est tentant, mais cela copie souvent les limites de l'interface dans le stockage. Un formulaire peut afficher le nom d'un cours à côté de l'apprenant ; cela ne signifie pas que le nom doit être copié dans chaque inscription. Un écran peut présenter une date sous forme de texte ; cela ne signifie pas que la base doit stocker cette date comme un texte libre.

La modélisation rend les hypothèses visibles. Elle permet de demander aux personnes qui connaissent le métier si un cours peut être suivi plusieurs fois, si un apprenant peut s'inscrire à plusieurs sessions du même cours, si une session peut exister sans inscription et si un résultat appartient à une inscription ou à une tentative. Ces décisions affectent directement les tables et les contraintes.

~~~mermaid
flowchart TD
    A["Besoin métier formulé"] --> B["Clarifier les termes et règles"]
    B --> C["Construire le MCD"]
    C --> D["Vérifier entités, associations et cardinalités"]
    D --> E["Transformer en MLD relationnel"]
    E --> F["Vérifier clés et contraintes"]
    F --> G["Préparer le MPD et l'implémentation"]
    G --> H["Tester avec des données représentatives"]
    H -. "retour et correction contrôlée" .-> B
~~~

Ce processus est itératif. Il n'est pas nécessaire de connaître tous les détails dès le premier entretien, mais les inconnues doivent être écrites plutôt que remplacées par des suppositions silencieuses. Une bonne modélisation est compréhensible, discutée, révisable et vérifiable.

## 3. Partir du besoin métier, pas de la liste des colonnes

Considérez cette demande :

« Une plateforme permet à des apprenants de suivre des cours. Chaque cours possède un titre, un niveau et une durée estimée. Les apprenants créent un compte avec un nom et une adresse électronique. Pour organiser les formations en groupe, la plateforme propose des sessions avec une date de début. Un apprenant peut s'inscrire à une session. La plateforme enregistre la date d'inscription et son statut. Après la formation, une évaluation peut donner lieu à plusieurs tentatives. »

Il serait prématuré de transformer immédiatement chaque mot en colonne. La première étape consiste à souligner les noms qui semblent désigner des concepts, les verbes qui expriment des relations et les contraintes implicites. On identifie ensuite les ambiguïtés :

- Un apprenant peut-il participer à plusieurs sessions ? Le besoin le suggère, mais il faut le confirmer.
- Un cours peut-il être organisé en plusieurs sessions ? C'est courant, mais cela reste une règle à préciser.
- Une session est-elle obligatoirement rattachée à un cours ?
- Un cours peut-il exister sans session planifiée ?
- Le même apprenant peut-il suivre deux fois le même cours dans deux sessions différentes ?
- Une inscription peut-elle être annulée puis réactivée ?
- Une évaluation appartient-elle au cours, à la session ou à chaque apprenant ?
- Le résultat d'une tentative doit-il être conservé après qu'une nouvelle tentative est passée ?

Ces questions ne sont pas des détails secondaires. Elles définissent le sens des relations et de l'historique. Si la plateforme autorise plusieurs sessions pour un cours, alors session_id et cours_id ne sont pas interchangeables. Si un apprenant peut suivre plusieurs sessions, une simple colonne session_id dans la table APPRENANTS ne représente pas correctement le métier.

### 3.1 Écrire les règles en langage naturel

Avant de dessiner, formulez des règles numérotées et sans ambiguïté. Pour notre premier modèle :

1. Un apprenant est identifié de façon stable par un identifiant propre à la plateforme.
2. Une adresse électronique est nécessaire pour créer le compte dans cette version du système.
3. Un cours possède un titre, un niveau et une durée estimée.
4. Une session planifiée concerne un seul cours.
5. Un cours peut être proposé dans zéro, une ou plusieurs sessions.
6. Une session peut recevoir zéro ou plusieurs inscriptions tant qu'elle est ouverte.
7. Une inscription concerne exactement un apprenant et exactement une session.
8. Un apprenant peut avoir plusieurs inscriptions.
9. Le statut et la date d'inscription décrivent l'association entre apprenant et session, pas l'apprenant en général.
10. Un cours peut recevoir des évaluations ; chaque résultat d'évaluation doit être rattaché à la participation ou tentative qu'il représente, selon la règle décidée.
11. Le titre d'un cours peut changer sans que son identifiant change.
12. Les inscriptions et résultats historiques ne doivent pas être supprimés automatiquement lors d'une simple modification du profil d'un apprenant.

Les règles 1 à 10 sont suffisantes pour construire un modèle de base, mais la règle 10 demande un complément sur les tentatives. Cette limite sera explicitement traitée dans une extension. La modélisation n'exige pas de résoudre toute l'application en une seule page ; elle exige de savoir ce que le modèle couvre et ce qu'il ne couvre pas.

## 4. Identifier correctement les entités

### 4.1 Comment reconnaître une entité ?

Une entité représente quelque chose que le système doit reconnaître comme distinct et au sujet duquel il conserve plusieurs propriétés. Elle a généralement une identité, un cycle de vie ou des relations avec d'autres concepts. APPRENANT et COURS sont de bons candidats : on doit pouvoir retrouver un apprenant indépendamment du cours qu'il suit, et retrouver un cours même quand aucune session n'est planifiée.

En revanche, un simple libellé qui n'a pas d'identité ou de cycle de vie propre n'a pas toujours besoin d'être une entité. Le niveau d'un cours peut commencer comme un attribut si le vocabulaire est limité à débutant, intermédiaire et expert. Si les niveaux possèdent leur propre description, des règles, des prérequis et des traductions, une entité NIVEAU peut devenir justifiée. La conception dépend des besoins, pas de la longueur du mot.

Posez quatre questions lorsque vous hésitez :

- Le système doit-il reconnaître plusieurs occurrences de ce concept ?
- Chaque occurrence a-t-elle des propriétés propres ?
- Le concept a-t-il des liens avec d'autres concepts ?
- Faut-il le créer, le modifier, l'archiver ou le référencer indépendamment ?

Si la réponse est souvent oui, le concept mérite probablement une entité ou une association porteuse d'attributs. Si le mot est uniquement une qualification d'un autre objet, un attribut peut suffire.

### 4.2 Distinguer entité et attribut

Le nom d'un apprenant est un attribut de APPRENANT dans notre modèle initial. Il ne devient pas automatiquement une entité NOM. Le nom peut être modifié sans que l'identité de la personne change. Une date de création de compte est un attribut temporel du compte. En revanche, une session de formation a sa propre date de début, son état et potentiellement un formateur ; elle peut exister comme occurrence distincte, donc comme entité.

Une association peut également porter des attributs. La date d'inscription n'est pas une propriété générale de l'apprenant ni une propriété générale de la session. Elle décrit le fait que cet apprenant s'est inscrit à cette session. Il s'agit donc d'un attribut de l'inscription, qui deviendra une entité associative ou une table de liaison dans le modèle relationnel.

Cette distinction évite les erreurs classiques. Si date_inscription est placée dans APPRENANT, une seule date pourrait être conservée par apprenant alors qu'il suit plusieurs sessions. Si statut_inscription est placé dans SESSION, tous les participants partageraient le même statut alors qu'un participant peut être inscrit, un autre avoir abandonné et un autre avoir terminé. Les attributs doivent être attachés à l'objet ou au lien qu'ils décrivent réellement.

### 4.3 Construire le dictionnaire de données

Un dictionnaire de données documente les termes. Il est utile même pour une petite application, parce que les mêmes mots peuvent avoir des significations différentes selon les équipes.

| Nom conceptuel | Signification | Exemples | Questions à confirmer |
|---|---|---|---|
| Apprenant | personne ayant un compte sur la plateforme | Amina, Samuel | Peut-on fusionner deux comptes ? |
| Cours | contenu pédagogique suivi par un apprenant | SQL de base | Un cours peut-il avoir des versions ? |
| Session | occurrence planifiée d'un cours | session du mois d'octobre | Quelle est la règle de capacité ? |
| Inscription | lien entre un apprenant et une session | inscription confirmée | Peut-on se réinscrire après annulation ? |
| Tentative | exécution distincte d'une évaluation par un participant | tentative 1, tentative 2 | Combien de tentatives sont permises ? |
| Résultat | résultat enregistré pour une tentative | score et date | Peut-il être corrigé ou annulé ? |

Le dictionnaire doit distinguer le nom technique, le sens métier et les contraintes. Une colonne \`score\` peut représenter une note sur 100, une proportion de 0 à 1 ou un nombre de points. Sans unité ni plage, sa signification reste ambiguë.

## 5. Identifier les occurrences et choisir les identifiants

Un identifiant permet de reconnaître une occurrence sans confusion. Il doit être stable dans le temps et unique dans le périmètre défini. Dans le MCD, on souligne ou marque l'identifiant selon la notation employée. Dans le MLD, il devient généralement une clé primaire ou participe à une clé primaire composée.

Pour APPRENANT, on peut utiliser apprenant_id. Pour COURS, cours_id. Pour SESSION, session_id. L'adresse électronique peut être unique selon la règle de création de compte, mais elle n'est pas toujours un identifiant interne idéal : elle peut changer et peut parfois être partagée. Un identifiant technique stable permet de ne pas modifier toutes les références lorsque l'adresse évolue.

Un code métier peut être utilisé comme identifiant si sa stabilité et son unicité sont garanties. Il ne faut pas choisir une clé sur la seule observation de dix exemples. Un nom de cours peut être identique à celui d'un autre cours, ou changer avec une refonte pédagogique. Le titre est donc un attribut et non l'identifiant recommandé du cours.

~~~mermaid
flowchart TD
    A["Propriété envisagée comme identifiant"] --> B{"Unique pour toutes les occurrences ?"}
    B -->|Non| C["Ce n'est pas un identifiant suffisant"]
    B -->|Oui| D{"Stable dans le temps ?"}
    D -->|Non ou incertain| C
    D -->|Oui| E{"Non ambigu et utilisable dans le périmètre ?"}
    E -->|Non| C
    E -->|Oui| F["Candidat identifiant à documenter"]
    C --> G["Choisir une autre clé ou une combinaison"]
~~~

Il peut exister plusieurs clés candidates. Dans le MLD, l'une sera choisie comme clé primaire ; les autres pourront être déclarées uniques si la règle métier le justifie. L'identifiant ne doit pas être confondu avec une autorisation. Connaître apprenant_id ne doit pas donner automatiquement accès au compte ou aux résultats associés.

## 6. Comprendre les associations

Une association exprime un lien métier entre des entités. Le verbe choisi doit être lisible et précis. « APPRENANT s'inscrit à SESSION » décrit une relation plus parlante que « APPRENANT possède SESSION ». La formulation permet de vérifier si le lien correspond à la réalité et de définir le rôle de chaque entité.

Une association peut relier deux entités, comme APPRENANT et SESSION ; elle peut relier trois entités ou davantage dans certains modèles conceptuels. Les associations ternaires sont possibles, mais elles demandent une analyse attentive : les remplacer automatiquement par plusieurs associations binaires peut changer le sens. Pour un premier modèle, nous commencerons avec des associations binaires simples et examinerons une extension lorsque cela apportera une meilleure compréhension.

### 6.1 Association COURS — SESSION

La règle est : « une session planifiée concerne un seul cours ; un cours peut être proposé dans zéro, une ou plusieurs sessions ». La lecture doit se faire dans les deux sens. Un cours peut rester disponible dans le catalogue avant qu'une session soit planifiée. Une session, en revanche, n'a pas de sens si elle n'est associée à aucun cours.

### 6.2 Association APPRENANT — SESSION

La règle est : « un apprenant peut s'inscrire à plusieurs sessions ; une session ouverte peut recevoir plusieurs inscriptions ». La relation est plusieurs-à-plusieurs entre apprenants et sessions. Mais le lien possède ses propres attributs : date d'inscription, statut et éventuellement date d'achèvement. C'est une raison supplémentaire de faire apparaître l'association INSCRIPTION explicitement.

~~~mermaid
flowchart LR
    A["APPRENANT"] -->|"s'inscrit à"| S["SESSION"]
    S -->|"reçoit des inscriptions de"| A
    N["Attributs du lien : date, statut, achèvement"] -. "décrivent l'inscription" .-> I["INSCRIPTION"]
    A --- I
    S --- I
~~~

Le dessin est volontairement pédagogique : il montre que la date et le statut décrivent le lien, pas les deux entités prises séparément. Dans une notation MCD MERISE stricte, l'association peut être représentée directement entre les entités avec ses attributs ; pour la transformation relationnelle, une table d'association matérialisera ce lien.

### 6.3 Une association peut porter des attributs

Supposons que le statut d'un apprenant pour une session soit « en cours ». Cela ne signifie pas que l'apprenant est globalement « en cours » pour toute la plateforme. Il peut avoir terminé une session et être inscrit à une autre. Le statut est celui d'une inscription spécifique.

La même logique s'applique au rôle d'une personne dans un projet, à la quantité d'un produit dans une commande, au nombre d'heures d'un salarié sur une mission ou au résultat d'un étudiant à une évaluation. Si une propriété décrit le lien entre deux occurrences, la modélisation doit l'associer à la relation, pas arbitrairement à l'une des entités.

## 7. Lire les cardinalités (min,max)

La cardinalité précise le nombre minimum et maximum de fois qu'une occurrence d'entité peut participer à une association. Dans la notation MERISE fréquemment utilisée, on écrit un couple comme \`(0,N)\`, \`(1,1)\` ou \`(1,N)\`. Certaines représentations utilisent d'autres symboles, mais la question reste la même : la participation est-elle obligatoire et combien de liens sont autorisés ?

- \`(0,1)\` signifie zéro ou une participation : le lien est facultatif et au plus unique.
- \`(1,1)\` signifie exactement une participation : le lien est obligatoire et unique.
- \`(0,N)\` signifie zéro, une ou plusieurs participations : le lien est facultatif et répétable.
- \`(1,N)\` signifie une ou plusieurs participations : le lien est obligatoire et répétable.

Le N signifie un nombre multiple non fixé à une valeur précise par le modèle de base. Si une limite maximum existe, comme dix participants par session, cette règle peut nécessiter un attribut de capacité et une vérification métier supplémentaire ; la cardinalité \`N\` ne signifie pas que le nombre est illimité dans toutes les circonstances.

### 7.1 Le piège de la lecture dans le mauvais sens

Pour l'association entre COURS et SESSION, on écrit ici :

- COURS : \`(0,N)\` — un cours peut ne pas encore avoir de session ou en avoir plusieurs.
- SESSION : \`(1,1)\` — chaque session est rattachée à exactement un cours.

Il faut toujours nommer l'entité dont on mesure les occurrences. Dire seulement « la relation est 1,N » sans indiquer le sens peut prêter à confusion. Une phrase complète réduit le risque : « un cours peut avoir plusieurs sessions ; chaque session concerne un seul cours ».

Pour APPRENANT et SESSION, dans la relation réalisée par INSCRIPTION :

- APPRENANT : \`(0,N)\` — un apprenant peut n'avoir encore aucune inscription, ou en avoir plusieurs.
- SESSION : \`(0,N)\` — une session ouverte peut n'avoir aucune inscription, ou en avoir plusieurs.

Les deux extrémités indiquent ici des multiplicités multiples. Cette relation doit être représentée à l'aide d'une association identifiable, puisque chaque inscription porte une date et un statut.

~~~mermaid
flowchart TD
    C["COURS"] ---|"0..N sessions possibles"| S["SESSION"]
    S ---|"exactement 1 cours"| C
    A["APPRENANT"] ---|"0..N inscriptions"| I["INSCRIPTION"]
    I ---|"exactement 1 apprenant"| A
    I ---|"exactement 1 session"| S
~~~

Le diagramme Mermaid ci-dessus illustre les règles avec une notation simplifiée. Il ne remplace pas un MCD complet avec les cardinalités correctement placées aux extrémités, mais sert de support pour lire les règles. Lors de la réalisation d'un vrai modèle, utilisez une notation et une légende cohérentes, puis confirmez les relations en langage naturel.

### 7.2 Comment déterminer la cardinalité minimale ?

Posez la question : un enregistrement peut-il exister sans participer à cette relation ? Un cours peut-il exister sans session planifiée ? Oui, s'il est proposé au catalogue avant l'ouverture d'une session. Sa participation minimale à l'association COURS-SESSION peut donc être zéro. Une session peut-elle exister sans cours ? Non, selon notre règle. Sa participation à l'association est obligatoire et sa cardinalité minimale vaut un.

Attention : les règles de cycle de vie peuvent changer la réponse. Lorsqu'on crée une session en brouillon, on peut vouloir la sauvegarder avant de choisir le cours. Si le modèle autorise réellement cet état temporaire, la cardinalité minimale ne doit pas être déduite du fonctionnement final seulement. Il faut décider si le MCD décrit uniquement les états métier valides, ou si le système doit également stocker des objets provisoires. Le modèle doit être explicite sur ce périmètre.

### 7.3 Comment déterminer la cardinalité maximale ?

Posez la question : combien de liens distincts sont autorisés ? Une session a un seul cours dans notre modèle. Si un événement regroupe plusieurs cours dans le même créneau, la règle serait différente et l'entité SESSION devrait être redéfinie ou reliée à un ensemble de cours. Il ne suffit pas d'augmenter une limite à la base sans reconsidérer le besoin.

Les cardinalités doivent suivre les règles métier, pas la facilité de la mise en œuvre. Si une conception permet une chose interdite par le métier, elle est trop permissive. Si elle interdit une activité légitime, elle est trop restrictive. Une bonne revue vérifie les deux types de défauts.

## 8. Construire le MCD de la plateforme de formation

Un MCD simplifié pour notre besoin comprend APPRENANT, COURS, SESSION et l'association INSCRIPTION. On peut également représenter INSCRIPTION comme entité associative si l'outil utilisé et le cadre de modélisation le permettent. Cette représentation est particulièrement parlante lorsqu'elle possède plusieurs attributs ou un cycle de vie.

~~~mermaid
flowchart LR
    A["APPRENANT<br/>id_apprenant<br/>nom<br/>email"] ---|"0,N"| I(("INSCRIPTION<br/>date_inscription<br/>statut"))
    I ---|"1,1"| S["SESSION<br/>id_session<br/>date_debut"]
    C["COURS<br/>id_cours<br/>titre<br/>niveau<br/>duree_estimee"] ---|"0,N"| S
    S ---|"1,1"| C
~~~

Ce diagramme est une représentation conceptuelle simplifiée plutôt qu'une notation MERISE normalisée prête à être remise à un outil de modélisation. L'essentiel est de voir les entités, le lien porteur d'attributs et les cardinalités exprimées en cohérence avec les règles du scénario.

Les attributs de l'entité APPRENANT portent sur l'apprenant. Les attributs de COURS décrivent le cours. La date de début appartient à SESSION, car un même cours peut être planifié à des dates différentes. La date d'inscription et le statut appartiennent à INSCRIPTION, car ils varient pour chaque couple apprenant-session.

Le MCD doit rester indépendant de choix techniques tels que VARCHAR(120), SERIAL, AUTO_INCREMENT, UUID ou la syntaxe exacte des index. Il peut indiquer qu'un identifiant existe et qu'un courriel doit être unique, mais le choix technique et la manière de l'implémenter seront précisés dans les étapes suivantes. Cette séparation évite que le modèle métier soit prisonnier d'un moteur choisi trop tôt.

### 8.1 Vérifier le modèle par des histoires concrètes

Pour tester le modèle, racontez plusieurs situations :

- Amina possède un compte mais ne s'est inscrite à aucune session.
- Le cours « SQL de base » existe, mais aucune session n'est prévue.
- Une session du cours SQL commence le 20 octobre et accueille Amina et Samuel.
- Samuel abandonne la session, mais Amina la termine.
- Le titre du cours change après que des inscriptions ont été créées.
- Une seconde session du même cours est organisée le mois suivant.
- Amina s'inscrit aussi à cette seconde session.

Le modèle doit représenter toutes ces situations sans copier le cours dans chaque inscription ni obliger un apprenant à n'avoir qu'une inscription. Si l'une des histoires est impossible, vérifiez si la règle métier l'interdit réellement ou si le modèle est trop restrictif.

### 8.2 Distinguer l'inscription de la session

Une session est une occurrence planifiée du cours. Une inscription est le lien individuel d'un apprenant vers cette session. Elles ne sont pas interchangeables. Si on place apprenant_id dans SESSION, une session ne peut plus référencer plusieurs apprenants simplement à travers une colonne. Si on place session_id dans APPRENANT, un apprenant ne peut plus représenter naturellement plusieurs sessions sans stocker des colonnes répétées.

L'association INSCRIPTION est donc un concept clé du modèle. Elle porte sa propre date et son statut, et elle offre un emplacement naturel pour d'autres informations comme la source de l'inscription, la date d'annulation ou la remarque administrative, si le métier en a besoin.

## 9. Transformer le MCD en MLD relationnel

Le MLD traduit le modèle conceptuel en relations qui pourront devenir des tables. Dans un modèle relationnel courant, chaque entité forte devient une table et chaque attribut devient une colonne. L'identifiant devient une clé primaire. Les relations sont transformées selon leurs cardinalités : une relation un-à-plusieurs est généralement représentée par une clé étrangère du côté plusieurs ; une relation plusieurs-à-plusieurs devient une table d'association.

Pour notre plateforme, le modèle logique devient :

**APPRENANT**
- apprenant_id — clé primaire
- nom
- email

**COURS**
- cours_id — clé primaire
- titre
- niveau
- duree_estimee

**SESSION**
- session_id — clé primaire
- cours_id — clé étrangère vers COURS
- date_debut

**INSCRIPTION**
- inscription_id — clé primaire technique possible
- apprenant_id — clé étrangère vers APPRENANT
- session_id — clé étrangère vers SESSION
- date_inscription
- statut

~~~mermaid
flowchart TD
    A["MCD : APPRENANT -- INSCRIPTION -- SESSION -- COURS"] --> B["Entités transformées en tables"]
    B --> C["Identifiants transformés en clés primaires"]
    C --> D["Relation COURS-SESSION : FK cours_id dans SESSION"]
    D --> E["Relation APPRENANT-SESSION : table INSCRIPTION"]
    E --> F["Attributs de l'association dans INSCRIPTION"]
    F --> G["MLD relationnel obtenu"]
~~~

Pourquoi mettre cours_id dans SESSION plutôt que session_id dans COURS ? Parce que chaque session correspond à un cours, mais un cours peut être associé à plusieurs sessions. La clé étrangère est généralement placée dans la table côté plusieurs : SESSION. Une colonne session_id dans COURS ne suffirait pas à représenter naturellement plusieurs sessions pour un cours, sauf à créer une structure répétitive ou une liste de valeurs, ce qui serait une mauvaise traduction du modèle.

Pourquoi INSCRIPTION devient-elle une table ? Parce qu'elle représente une association plusieurs-à-plusieurs avec des attributs propres. Le MLD doit identifier les occurrences de cette relation. On peut retenir une clé composée \`(apprenant_id, session_id)\` si une seule inscription par apprenant et session est autorisée. On peut également utiliser \`inscription_id\` comme clé primaire technique et ajouter une contrainte UNIQUE sur \`(apprenant_id, session_id)\` pour empêcher les doublons. Si les réinscriptions sont permises, le modèle doit ajouter l'élément qui distingue les occurrences, par exemple une version d'inscription ou un identifiant de tentative ; sinon la contrainte unique contredit le besoin.

### 9.1 Exemple de MLD sous forme de diagramme relationnel

~~~mermaid
erDiagram
    APPRENANT ||--o{ INSCRIPTION : "possede"
    SESSION ||--o{ INSCRIPTION : "recoit"
    COURS ||--o{ SESSION : "organise"
    APPRENANT {
        int apprenant_id PK
        string nom
        string email UK
    }
    COURS {
        int cours_id PK
        string titre
        string niveau
        int duree_estimee
    }
    SESSION {
        int session_id PK
        int cours_id FK
        date date_debut
    }
    INSCRIPTION {
        int inscription_id PK
        int apprenant_id FK
        int session_id FK
        date date_inscription
        string statut
    }
~~~

Le diagramme Mermaid \`erDiagram\` est utile pour visualiser les tables et les clés, mais sa notation et sa sémantique ne sont pas identiques à toutes les notations MCD. Gardez la distinction conceptuelle : le MCD décrit d'abord les concepts et règles métier ; ce diagramme relationnel décrit déjà les relations, clés primaires et clés étrangères de l'implémentation logique.

### 9.2 Clé composée ou identifiant technique ?

Si une inscription ne peut apparaître qu'une fois par couple apprenant-session, le couple de références peut identifier la ligne. La clé composée reflète directement la règle. Dans d'autres cas, on choisit un identifiant technique pour simplifier les références vers l'inscription, puis une contrainte UNIQUE protège la règle métier.

Ces approches ne sont pas contradictoires. Une clé primaire identifie la ligne selon le modèle relationnel ; une contrainte UNIQUE peut protéger une autre combinaison de valeurs. Il faut éviter de confondre la facilité de lecture technique et le sens du métier. Un identifiant technique ne doit jamais servir à contourner la règle de non-duplication.

Voici une définition SQL indicative pour montrer la traduction logique :

~~~sql
CREATE TABLE cours (
    cours_id INTEGER PRIMARY KEY,
    titre VARCHAR(160) NOT NULL,
    niveau VARCHAR(20) NOT NULL,
    duree_estimee INTEGER NOT NULL CHECK (duree_estimee > 0)
);

CREATE TABLE apprenant (
    apprenant_id INTEGER PRIMARY KEY,
    nom VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE session_formation (
    session_id INTEGER PRIMARY KEY,
    cours_id INTEGER NOT NULL,
    date_debut DATE NOT NULL,
    FOREIGN KEY (cours_id) REFERENCES cours(cours_id)
);

CREATE TABLE inscription (
    inscription_id INTEGER PRIMARY KEY,
    apprenant_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    statut VARCHAR(20) NOT NULL
        CHECK (statut IN ('inscrit', 'en_cours', 'termine', 'abandonne', 'annule')),
    UNIQUE (apprenant_id, session_id),
    FOREIGN KEY (apprenant_id) REFERENCES apprenant(apprenant_id),
    FOREIGN KEY (session_id) REFERENCES session_formation(session_id)
);
~~~

Ce SQL est une illustration du MLD ; la syntaxe des identifiants, des types et des contraintes doit être testée sur le SGBD choisi. Le modèle métier devrait être utilisable même si le projet change de moteur. Le SQL physique peut évoluer sans changer le fait qu'une inscription appartient à un apprenant et à une session.

## 10. Un-à-un, un-à-plusieurs et plusieurs-à-plusieurs en pratique

### 10.1 Relation un-à-un

Considérons APPRENANT et PROFIL_CONFIDENTIEL. Si chaque apprenant peut posséder au plus un profil confidentiel et que chaque profil est rattaché à un seul apprenant, il s'agit d'un cas un-à-un. Dans le MLD, la clé étrangère peut être accompagnée d'une contrainte UNIQUE pour empêcher plusieurs profils du même apprenant. Une table séparée peut être justifiée par la différence de droits d'accès, de cycle de vie ou de nécessité fonctionnelle. Si les données sont toujours créées et utilisées ensemble, cette séparation doit être justifiée plutôt qu'automatique.

### 10.2 Relation un-à-plusieurs

Un cours peut avoir de nombreuses sessions. Chaque session appartient à un cours unique. Dans le MLD, cours_id se place normalement dans SESSION comme clé étrangère. Si cours_id était placé dans COURS, il ne permettrait pas de représenter une liste variable de sessions sans déformer la structure.

### 10.3 Relation plusieurs-à-plusieurs

Un apprenant peut suivre plusieurs sessions et une session peut accueillir plusieurs apprenants. INSCRIPTION représente ce lien. La table d'association est le lieu naturel pour les attributs qui caractérisent chaque participation. Elle permet aussi d'imposer une règle d'unicité sur la paire, si le métier l'exige.

~~~mermaid
flowchart LR
    subgraph "Côté apprenants"
      A1["Apprenant A"]
      A2["Apprenant B"]
    end
    subgraph "Association"
      I1["Inscription 1"]
      I2["Inscription 2"]
      I3["Inscription 3"]
    end
    subgraph "Côté sessions"
      S1["Session SQL"]
      S2["Session Réseaux"]
    end
    A1 --> I1
    S1 --> I1
    A1 --> I2
    S2 --> I2
    A2 --> I3
    S1 --> I3
~~~

Dans ce dessin, chaque inscription relie un apprenant et une session. Le statut peut être différent d'une inscription à l'autre. C'est exactement le genre de propriété que l'on ne doit pas placer dans l'une des deux entités parentes.

## 11. Règles d'intégrité et contraintes logiques

Un MLD bien conçu ne se limite pas à dessiner des clés. Il doit préciser les règles qui rendent les données cohérentes. Certaines règles peuvent s'exprimer dans le schéma : clé primaire unique, clé étrangère valide, champ obligatoire, valeur appartenant à une liste, durée supérieure à zéro. D'autres exigent une logique plus complexe : une session ne doit pas dépasser sa capacité, une date de début ne peut pas être postérieure à une date de fin, ou une inscription ne peut changer vers un état interdit après une fermeture de session.

Une règle qui doit toujours être vraie doit être imposée aussi près que possible de la donnée partagée. La contrainte évite qu'un import, une tâche automatisée ou une autre application produise des données qui contournent le formulaire. En revanche, une règle dépendant de plusieurs enregistrements ou de la concurrence peut nécessiter une transaction, une procédure centralisée ou d'autres mécanismes adaptés. Ne supposez pas qu'une simple contrainte de colonne valide toutes les règles de la plateforme.

Exemples de règles à documenter :

- un titre de cours ne peut pas être vide ;
- la durée estimée est strictement positive ;
- chaque session est liée à un cours existant ;
- chaque inscription est liée à un apprenant et à une session existants ;
- le statut d'inscription appartient à un vocabulaire contrôlé ;
- une seule inscription par apprenant et session est permise dans le modèle choisi ;
- une nouvelle tentative de quiz doit être reliée à l'inscription ou au participant concerné ;
- les résultats historiques ne doivent pas être effacés automatiquement lorsque le titre du cours change.

Il ne faut pas copier systématiquement le titre du cours dans SESSION ou INSCRIPTION pour simplifier un rapport. Une table qui référence cours_id peut retrouver le titre courant. Si l'on doit conserver le titre tel qu'il était lors d'une inscription historique, c'est une autre règle : elle peut nécessiter un instantané contrôlé ou une gestion de versions du cours. Il faut justifier la duplication et définir quand elle est mise à jour.

## 12. Évolution temporelle : statuts, tentatives et historique

Les premiers modèles simplifient souvent le temps. Une inscription possède un statut courant : inscrit, en cours, terminé ou abandonné. Cela suffit pour présenter l'état actuel. Mais si l'organisation veut connaître les changements successifs, il faut conserver un historique d'événements ou de statuts. Une simple colonne statut ne dit pas quand l'inscription est passée d'inscrit à en cours, ni qui a effectué la modification.

De même, un résultat de quiz peut représenter le meilleur score, le dernier score ou chaque tentative. Ce sont trois concepts différents. Si la plateforme permet plusieurs tentatives, une table TENTATIVE peut représenter une exécution particulière, avec une date, un score et un état. Elle sera reliée à l'inscription ou au participant selon la règle pédagogique. Avant d'ajouter un champ score à INSCRIPTION, il faut décider si un seul résultat suffit ou si l'historique compte.

~~~mermaid
flowchart TD
    I["INSCRIPTION"] --> T1["TENTATIVE 1"]
    I --> T2["TENTATIVE 2"]
    T1 --> R1["Résultat : 55/100"]
    T2 --> R2["Résultat : 82/100"]
    R2 --> B["Règle métier : meilleur score, dernier score ou validation ?"]
~~~

Le diagramme illustre pourquoi une unique colonne score dans l'inscription peut être insuffisante. Si l'on écrase le score 55 par 82, on conserve le résultat actuel mais on perd la trace du premier essai. Si le métier exige l'audit des tentatives, chaque tentative doit avoir une identité propre.

La temporalité touche aussi le cours. Une nouvelle version de contenu peut modifier les objectifs, les exercices ou le quiz. Les apprenants qui ont terminé une ancienne version doivent-ils rester validés ? Doivent-ils refaire le quiz ? Le modèle de données doit s'aligner sur une politique de versionnement explicite. Cela dépasse la première version de notre MCD, mais doit être noté comme évolution possible, pas caché sous un champ titre.

## 13. Le passage au modèle physique

Le MLD décrit les relations logiques, mais ne détermine pas tous les détails d'implémentation. Le modèle physique précise le SGBD et les choix techniques correspondants : types, identité générée, contraintes disponibles, index, conventions de schéma, stratégie de sauvegarde et besoins de performance. Le bon ordre consiste à clarifier le métier, à structurer logiquement les données, puis à choisir la traduction physique adaptée.

Par exemple, cours_id peut être un entier généré dans un moteur ou un UUID dans un autre projet. Ce détail ne change pas le fait qu'une session référence un cours. La durée estimée peut être exprimée en minutes comme entier ou sous une autre forme selon les exigences. Le statut peut être protégé par CHECK, un type dédié ou une table de référence ; ce choix varie avec les conventions du projet et la capacité à faire évoluer les états.

Les index ne remplacent pas les contraintes. Un index peut accélérer une recherche ; une clé étrangère ou une contrainte UNIQUE protège une règle de cohérence. Certaines définitions de clés créent des index automatiquement selon le moteur, mais la performance et l'intégrité restent deux questions à examiner séparément. Les index utiles seront étudiés plus tard dans le parcours.

Un schéma logique devrait être versionné. Une évolution réelle peut ajouter une table ou un attribut, modifier une règle d'unicité ou transformer le sens d'une relation. Cette évolution doit être traitée par une migration testée, avec un plan pour les données existantes et une stratégie de retour arrière. Modifier manuellement la base de production sans décrire le changement rend difficile la reproduction de l'environnement.

## 14. Démarche complète de modélisation

La démarche suivante convient à un projet débutant comme à une première analyse professionnelle.

### Étape 1 — Définir le périmètre

Écrivez ce que le système doit permettre et ce qui est hors périmètre. Pour une plateforme de formation, le périmètre peut couvrir les apprenants, cours, sessions et inscriptions, mais laisser la facturation, la messagerie et la délivrance des certificats à une phase suivante. Cette limite évite de concevoir une architecture complète à partir d'hypothèses non validées.

### Étape 2 — Recueillir les règles

Utilisez des exemples concrets : « Amina s'inscrit à la session du cours SQL le 20 octobre » ou « Samuel abandonne mais son historique reste conservé ». Demandez ce qui doit être possible, ce qui doit être interdit et quelles situations exceptionnelles existent. Consignez les hypothèses à confirmer.

### Étape 3 — Identifier les concepts

Relevez les entités candidates et les associations exprimées par les verbes. Vérifiez que chaque concept a un sens distinct et une identité ou des propriétés suffisantes. Ne transformez pas tous les mots d'un texte en entités.

### Étape 4 — Définir attributs et identifiants

Pour chaque entité, listez les attributs et leur signification. Définissez les identifiants candidats et vérifiez unicité, stabilité et portée. Déplacez les attributs des liens vers l'association correspondante quand ils ne décrivent pas une entité isolée.

### Étape 5 — Déterminer les cardinalités

Lisez chaque relation des deux côtés et écrivez les règles en phrases complètes. Posez les questions « zéro ou au moins un ? », « au plus un ou plusieurs ? ». Testez les réponses avec plusieurs scénarios.

### Étape 6 — Construire le MCD

Dessinez une représentation conceptuelle indépendante du SGBD. Utilisez une notation cohérente, une légende et des noms métier. Chaque association doit être nommée clairement et les cardinalités doivent correspondre aux règles écrites.

### Étape 7 — Vérifier le MCD avec le métier

Présentez le modèle à une personne qui connaît le processus. Demandez-lui de décrire des cas de la vie courante et des exceptions. Ne lui demandez pas seulement « le dessin est-il bon ? » ; demandez si chaque situation réelle peut être représentée sans contournement ambigu.

### Étape 8 — Transformer en MLD

Transformez les entités en tables, les identifiants en clés primaires, les relations un-à-plusieurs en clés étrangères, et les relations plusieurs-à-plusieurs en tables associatives. Définissez les règles de non-duplication et les attributs portés par les associations.

### Étape 9 — Vérifier les contraintes et cas limites

Créez un petit jeu de données logique sur papier, puis éventuellement en SQL. Testez les références absentes, les doublons et les valeurs invalides. Le modèle doit permettre les cas légitimes et interdire ceux qui violent les règles.

### Étape 10 — Documenter les décisions

Gardez le dictionnaire de données, les règles métier, les hypothèses, le MCD, le MLD et les décisions techniques à part. Une décision comme « une inscription par apprenant et session » doit être visible dans les documents et traduite par une contrainte ou une règle appropriée.

~~~mermaid
flowchart TD
    A["1. Périmètre"] --> B["2. Règles métier"]
    B --> C["3. Entités et associations candidates"]
    C --> D["4. Attributs et identifiants"]
    D --> E["5. Cardinalités"]
    E --> F["6. MCD"]
    F --> G["7. Revue métier"]
    G --> H["8. MLD : tables et clés"]
    H --> I["9. Tests d'intégrité"]
    I --> J["10. Documentation et évolution"]
    G -. "ambiguïté ou contradiction" .-> B
~~~

Cette méthode est volontairement simple, mais son efficacité dépend de la qualité des questions posées. Une erreur de cardinalité peut rendre toute la traduction relationnelle incorrecte. Une hypothèse de réinscription non clarifiée peut conduire à une contrainte unique qui bloque une activité légitime. Le dessin et le SQL doivent tous deux être relus à partir des règles de départ.

## 15. Pièges fréquents en modélisation

### Transformer chaque substantif en entité

Un texte métier peut contenir des dizaines de noms ; tous ne sont pas des entités. « Couleur » peut être un attribut d'un produit. Si la couleur possède un catalogue, un code, des traductions et un cycle de vie, elle peut devenir une entité référencée. La décision dépend des usages et des règles, pas uniquement de la grammaire.

### Confondre entité et association

L'inscription est un lien entre apprenant et session, mais elle porte date et statut et possède un cycle de vie. Il est souvent utile de la représenter explicitement. À l'inverse, une association qui ne porte aucun attribut ni aucune règle particulière peut devenir simplement une clé étrangère dans le MLD si elle est un-à-plusieurs.

### Oublier la cardinalité minimale

Dire qu'une session appartient à un cours répond à la cardinalité maximale côté session, mais il reste à savoir si la session peut exister sans cours. Dans la règle de notre modèle, non : la participation est obligatoire. La distinction peut être importante lors de la création d'un brouillon, et doit être confirmée plutôt que supposée.

### Inverser la lecture des cardinalités

Une notation \`1,N\` ne veut pas dire la même chose si l'on ne précise pas à quelle entité elle est rattachée. Écrivez la phrase en entier et testez les deux directions : « un cours peut avoir plusieurs sessions » et « chaque session appartient à un cours ».

### Placer le statut au mauvais endroit

Un statut d'inscription décrit le lien entre un apprenant et une session. Le placer sur l'apprenant produit un seul statut pour toutes ses inscriptions ; le placer sur la session impose un statut identique à tous les participants. L'attribut doit rester sur l'association ou l'entité qui représente le fait concerné.

### Utiliser le titre comme clé

Un titre peut changer, être traduit ou être partagé entre plusieurs versions. Un identifiant stable et une contrainte d'unicité métier éventuellement séparée sont généralement plus adaptés. Si un code métier stable existe, documentez sa portée et les conditions d'unicité.

### Représenter une relation plusieurs-à-plusieurs par une liste dans une colonne

Stocker des identifiants séparés par des virgules dans une seule colonne rend les références difficiles à valider et les requêtes plus fragiles. Une table associative permet de faire respecter les clés étrangères et de porter des attributs de relation.

### Oublier les règles de suppression et d'historique

Le modèle doit préciser ce qu'il advient des inscriptions lorsque le cours est archivé ou qu'un compte est désactivé. Les suppressions en cascade ne doivent pas être choisies par défaut pour faciliter l'effacement. Les données historiques peuvent avoir une valeur métier, légale ou d'audit.

### Trop dépendre du diagramme

Un beau diagramme ne compense pas des règles ambiguës. Les cardinalités, contraintes et hypothèses doivent être accompagnées de phrases compréhensibles, d'exemples et de tests. La notation sert à communiquer la logique, pas à la remplacer.

## 16. Atelier pratique guidé : modéliser une bibliothèque

Nous allons appliquer la démarche à une bibliothèque qui gère ses adhérents, ses ouvrages et les emprunts. Ce cas est différent de la plateforme de formation, ce qui permet de vérifier que vous comprenez les concepts plutôt que de mémoriser un seul diagramme.

### 16.1 Besoin

« La bibliothèque conserve une fiche pour chaque adhérent et un catalogue d'ouvrages. Un adhérent peut emprunter plusieurs ouvrages au fil du temps. Un ouvrage peut être emprunté par différents adhérents à des périodes différentes. Chaque emprunt possède une date de début, une date d'échéance et éventuellement une date de retour. La bibliothèque doit pouvoir retrouver l'historique des emprunts. Un ouvrage peut avoir plusieurs exemplaires physiques. »

La dernière phrase est importante : un ouvrage décrit une publication au niveau du catalogue ; un exemplaire décrit une copie physique pouvant être prêtée. Si on confond les deux, il devient impossible de distinguer deux copies du même livre ou de dire qu'une copie précise est actuellement empruntée.

### 16.2 Entités candidates

- ADHERENT : un membre de la bibliothèque.
- OUVRAGE : description bibliographique d'un livre ou d'une publication.
- EXEMPLAIRE : copie physique ou unité prêtée.
- EMPRUNT : événement reliant un adhérent à un exemplaire pendant une période.

Le lien EMPRUNT porte ses propres dates et son état. Il représente un fait historique, pas seulement un lien permanent entre adhérent et ouvrage. Un même exemplaire peut avoir plusieurs emprunts successifs dans le temps, mais il ne devrait pas avoir deux emprunts simultanés actifs si la règle métier l'interdit.

~~~mermaid
flowchart LR
    O["OUVRAGE"] ---|"0,N"| E["EXEMPLAIRE"]
    A["ADHERENT"] ---|"0,N"| P(("EMPRUNT"))
    E ---|"0,N dans le temps"| P
    P --- D["date_emprunt"]
    P --- R["date_echeance"]
    P --- T["date_retour facultative"]
~~~

La cardinalité temporelle demande de la précision. Un exemplaire peut être associé à de nombreux emprunts au cours de sa vie, donc \`0,N\` dans l'historique. Cependant, la règle « au maximum un emprunt actif à un instant donné » est une contrainte temporelle supplémentaire que la cardinalité simple ne suffit pas toujours à exprimer. Elle nécessite une stratégie de validation adaptée au SGBD et au fonctionnement concurrent.

### 16.3 Traduction logique

Une proposition de MLD :

**ADHERENT** (\`adherent_id\` PK, nom, email)

**OUVRAGE** (\`ouvrage_id\` PK, titre, auteur, isbn)

**EXEMPLAIRE** (\`exemplaire_id\` PK, \`ouvrage_id\` FK, code_inventaire UNIQUE, etat)

**EMPRUNT** (\`emprunt_id\` PK, \`adherent_id\` FK, \`exemplaire_id\` FK, date_emprunt, date_echeance, date_retour nullable)

Chaque exemplaire référence un ouvrage. Un emprunt référence un adhérent et un exemplaire. Les dates appartiennent à EMPRUNT. Un ouvrage peut exister sans exemplaire si le catalogue prépare une acquisition, selon les règles retenues. Un exemplaire doit référencer un ouvrage.

### 16.4 Questions de vérification

1. Où se trouve l'état d'un exemplaire : dans OUVRAGE ou dans EXEMPLAIRE ?
2. Pourquoi ne place-t-on pas date_retour directement dans ADHERENT ?
3. Comment représenter deux exemplaires du même ouvrage ?
4. Comment conserver les emprunts terminés ?
5. Quelle règle empêche deux emprunts actifs simultanés du même exemplaire ?

**Corrigé.** L'état physique appartient à EXEMPLAIRE, car deux copies du même ouvrage peuvent être dans des états différents. La date de retour appartient à EMPRUNT parce qu'elle décrit un événement déterminé. Plusieurs copies ont des identifiants d'exemplaire distincts et référencent le même ouvrage. L'historique est conservé en gardant les lignes d'EMPRUNT plutôt qu'en écrasant systématiquement l'ancien emprunt. Enfin, l'interdiction de deux emprunts actifs simultanés doit être explicitement modélisée et appliquée, potentiellement avec une contrainte ou un mécanisme adapté au SGBD ; une simple clé étrangère ne suffit pas.

### 16.5 Critères d'acceptation de l'atelier

L'atelier est réussi si vous savez distinguer un ouvrage d'un exemplaire, expliquer pourquoi EMPRUNT porte les dates, dessiner les relations dans les deux sens, transformer le modèle en tables et identifier la règle supplémentaire concernant les emprunts actifs simultanés. Notez aussi les décisions qui restent à confirmer, comme le nombre de prolongations, la politique de perte et la conservation de l'historique.

## 17. Exercices d'application avec corrigés

### Exercice 1 — Identifier les entités

Un service de livraison garde des clients, des commandes, des colis et des suivis de livraison. Une commande peut contenir plusieurs colis ; un colis peut produire plusieurs événements de suivi.

Quelles sont les entités candidates et quelles associations voyez-vous ?

**Corrigé.** CLIENT, COMMANDE, COLIS et EVENEMENT_SUIVI sont des entités candidates. Une commande peut regrouper plusieurs colis, selon une relation un-à-plusieurs si chaque colis appartient à une commande unique. Les événements de suivi appartiennent à un colis et sont multiples dans le temps. Le statut courant pourrait être obtenu à partir du dernier événement, mais il faut décider si on le conserve séparément pour faciliter l'accès et comment il reste cohérent avec l'historique.

### Exercice 2 — Distinguer entité et attribut

Un produit possède un nom, un prix et une couleur. La couleur doit-elle toujours être une entité ?

**Corrigé.** Non. Si la couleur est simplement une propriété textuelle du produit et qu'aucune règle spécifique n'est nécessaire, un attribut peut suffire. Si l'organisation doit gérer un catalogue de couleurs, des codes, des traductions ou des règles réutilisées, une entité COULEUR référencée par PRODUIT peut être justifiée. La décision dépend du besoin et de l'évolution prévue.

### Exercice 3 — Lire une cardinalité

Chaque session appartient à exactement un cours. Un cours peut avoir zéro ou plusieurs sessions. Donnez les cardinalités en nommant leur direction.

**Corrigé.** Pour la participation d'un cours à l'association, la cardinalité est \`(0,N)\) : un cours peut avoir aucune ou plusieurs sessions. Pour la participation d'une session à cette association, elle est \`(1,1)\) : chaque session doit appartenir à exactement un cours. Il faut toujours préciser l'entité dont on décrit la participation.

### Exercice 4 — Choisir où mettre un attribut

Une plateforme conserve le statut d'inscription, la date d'inscription et le nom du cours. Où placer chaque attribut ?

**Corrigé.** Le statut et la date d'inscription décrivent le lien entre apprenant et session ; ils appartiennent à INSCRIPTION. Le titre courant appartient à COURS. Si l'on doit conserver le titre qui était en vigueur au moment de l'inscription, il faut une règle d'historique ou de versionnement explicite. Copier le titre partout sans règle de mise à jour crée un risque d'incohérence.

### Exercice 5 — Transformer une relation un-à-plusieurs

Un département peut avoir plusieurs employés et chaque employé appartient à un seul département. Où placer la clé étrangère dans le MLD ?

**Corrigé.** On place généralement departement_id dans EMPLOYE, du côté plusieurs, comme clé étrangère vers DEPARTEMENT. Mettre une liste d'identifiants d'employés dans une seule colonne du département rendrait les références difficiles à valider et les requêtes plus fragiles.

### Exercice 6 — Transformer une relation plusieurs-à-plusieurs

Un apprenant peut suivre plusieurs modules et un module peut être suivi par plusieurs apprenants. L'association possède une date et un statut.

**Corrigé.** On crée une table associative INSCRIPTION contenant apprenant_id, module_id, date_inscription et statut. Les deux références sont des clés étrangères. Si une seule inscription par paire est autorisée, une clé composée ou une contrainte UNIQUE sur le couple protège la règle. Si plusieurs sessions ou tentatives sont possibles, le modèle doit inclure leur identifiant.

### Exercice 7 — Choisir un identifiant

Vous proposez le titre du cours comme clé primaire. Les cours peuvent être renommés et deux versions peuvent partager un titre proche. Quelle difficulté voyez-vous ?

**Corrigé.** Le titre n'est pas forcément unique et peut changer. Une mise à jour de titre risquerait de modifier toutes les références et pourrait créer des collisions. Utilisez un identifiant stable, et traitez le titre comme attribut. Une contrainte d'unicité sur un code métier peut être ajoutée si ce code est stable et la règle confirmée.

### Exercice 8 — Une cardinalité trop restrictive

Le modèle place un champ session_id dans APPRENANT. Plus tard, l'application doit permettre à un apprenant de suivre plusieurs sessions. Pourquoi ce modèle pose-t-il problème ?

**Corrigé.** Une seule colonne session_id permet de stocker au mieux une référence à la fois. Ajouter session_id_2, session_id_3 ou une liste texte crée une structure répétitive. Le lien plusieurs-à-plusieurs doit être représenté par une table d'association, comme INSCRIPTION, qui contient une ligne par participation.

### Exercice 9 — Préserver l'historique

Quand un apprenant quitte la plateforme, le responsable souhaite supprimer sa fiche. L'apprenant possède des résultats d'évaluation historiques. Que faut-il décider avant de supprimer ?

**Corrigé.** Il faut confirmer les règles de conservation, d'audit, de confidentialité et de suppression. Une suppression en cascade pourrait effacer les résultats ; ce n'est pas nécessairement acceptable. Selon le besoin, on peut désactiver le compte, anonymiser les données qui peuvent l'être ou conserver un historique minimal conformément aux règles applicables. La solution ne doit pas être choisie uniquement pour simplifier une suppression SQL.

### Exercice 10 — Repérer une association porteuse d'attributs

Dans une commande, la quantité et le prix appliqué au moment de la vente décrivent-ils le produit ou le lien entre la commande et le produit ?

**Corrigé.** Ils décrivent la ligne de commande, c'est-à-dire l'association entre commande et produit. Le prix catalogue courant peut évoluer ; le prix réellement appliqué dans la transaction doit souvent être conservé comme fait historique. La table d'association est donc nécessaire et porte ses propres attributs.

### Exercice 11 — Valider un MCD

Un diagramme indique que chaque cours possède exactement une session et chaque session appartient à un cours. Le besoin affirme que des cours peuvent être publiés avant l'ouverture de la première session et peuvent être organisés plusieurs fois. Identifiez l'erreur.

**Corrigé.** La cardinalité côté COURS est trop restrictive : elle devrait autoriser zéro session ou plusieurs sessions, donc \`(0,N)\) selon la notation choisie. La participation côté SESSION reste exactement un cours si telle est la règle. Le modèle doit être corrigé pour refléter le cycle de vie décrit par le métier.

### Exercice 12 — Tester une règle qui n'est pas une simple cardinalité

Une session ne doit pas avoir plus de 20 inscriptions confirmées. Une cardinalité \`(0,N)\) suffit-elle ?

**Corrigé.** Non. N exprime la multiplicité variable, pas la limite métier spécifique de 20. Il faut représenter la capacité de la session comme donnée et concevoir une validation qui empêche de dépasser la capacité, y compris lorsque plusieurs inscriptions arrivent simultanément. La solution peut demander une transaction ou un mécanisme central de réservation ; une simple clé étrangère ne suffit pas.

## 18. Défi final corrigé — modéliser une plateforme de mentorat

### Mission

Une plateforme relie des mentors à des apprenants. Un mentor peut accompagner plusieurs apprenants. Un apprenant peut bénéficier de plusieurs mentors, à des périodes différentes. Chaque accompagnement possède une date de début, un état et éventuellement une date de fin. Il faut conserver l'historique des accompagnements terminés. Vous devez produire les règles, le MCD, le MLD et des tests de cohérence.

### Étape A — Écrire les règles métier

1. Chaque mentor possède un identifiant stable et un nom d'affichage.
2. Chaque apprenant possède un identifiant stable et un nom d'affichage.
3. Un apprenant peut n'avoir aucun accompagnement ou en avoir plusieurs.
4. Un mentor peut n'accompagner personne ou accompagner plusieurs apprenants.
5. Un accompagnement relie exactement un mentor et exactement un apprenant.
6. Un accompagnement possède une date de début, un statut et éventuellement une date de fin.
7. Les accompagnements terminés restent dans l'historique.
8. Le modèle initial autorise plusieurs accompagnements au fil du temps entre un mentor et un apprenant ; les règles qui interdisent des périodes qui se chevauchent doivent être précisées séparément.

### Étape B — Construire le MCD

Les entités sont MENTOR et APPRENANT. L'association ACCOMPAGNEMENT porte des attributs et devient une entité associative pratique dans la traduction relationnelle.

~~~mermaid
flowchart LR
    M["MENTOR<br/>id_mentor<br/>nom"] ---|"0,N"| A(("ACCOMPAGNEMENT<br/>debut<br/>statut<br/>fin éventuelle"))
    A ---|"0,N dans l'historique"| P["APPRENANT<br/>id_apprenant<br/>nom"]
~~~

Le couple de cardinalités côté mentor et apprenant exprime que plusieurs accompagnements sont possibles dans le temps. Chaque occurrence d'ACCOMPAGNEMENT est reliée à un seul mentor et à un seul apprenant. Cette lecture évite de confondre la multiplicité des accompagnements historiques avec le nombre d'accompagnements actifs à un instant donné.

### Étape C — Traduire en MLD

**MENTOR** (\`mentor_id\` PK, nom)

**APPRENANT** (\`apprenant_id\` PK, nom)

**ACCOMPAGNEMENT** (\`accompagnement_id\` PK, \`mentor_id\` FK, \`apprenant_id\` FK, date_debut, statut, date_fin nullable)

~~~mermaid
erDiagram
    MENTOR ||--o{ ACCOMPAGNEMENT : "assure"
    APPRENANT ||--o{ ACCOMPAGNEMENT : "recoit"
    MENTOR {
        int mentor_id PK
        string nom
    }
    APPRENANT {
        int apprenant_id PK
        string nom
    }
    ACCOMPAGNEMENT {
        int accompagnement_id PK
        int mentor_id FK
        int apprenant_id FK
        date date_debut
        string statut
        date date_fin
    }
~~~

### Étape D — Établir des critères de vérification

Le modèle doit permettre un mentor sans accompagnement, un apprenant sans accompagnement, plusieurs apprenants pour un mentor et plusieurs mentors successifs pour un apprenant. Une référence à un mentor ou un apprenant inexistant doit être rejetée. Un accompagnement terminé doit rester consultable. Une date de fin, si elle est fournie, ne doit pas précéder la date de début.

Il faut également discuter une règle qui n'est pas spécifiée dans l'énoncé : un apprenant peut-il avoir plusieurs mentors actifs en même temps ? Un mentor peut-il accompagner au plus dix apprenants actifs ? Deux accompagnements du même couple peuvent-ils se chevaucher ? Ces questions ne sont pas résolues par le MCD minimal présenté. Il faut les confirmer avant d'ajouter des contraintes de capacité ou d'exclusivité.

### Étape E — Corrigé du raisonnement

L'association porte une date et un statut, donc elle ne peut pas se limiter à une référence unique dans MENTOR ou APPRENANT. Elle devient une table propre. Le fait qu'un accompagnement ait une date de fin facultative traduit la possibilité qu'il soit encore en cours, mais le statut doit rester cohérent avec cette absence. Si cette cohérence est indispensable, une contrainte adaptée ou une validation transactionnelle doit être ajoutée.

Le défi est réussi si vous expliquez les deux directions des cardinalités, justifiez l'entité associative, traduisez les références en clés étrangères et identifiez les règles temporelles encore ouvertes. Le but n'est pas de produire un diagramme qui paraît sophistiqué ; il est de rendre le besoin assez précis pour que l'implémentation et ses tests suivent naturellement.

## 19. Checklist avant de valider un modèle

Utilisez cette liste lors d'une revue. Chaque réponse doit pouvoir être justifiée par une règle ou un exemple :

- Le périmètre du modèle et ses limites sont écrits.
- Les concepts du métier sont définis dans un vocabulaire commun.
- Chaque entité candidate correspond à un concept qui doit être reconnu distinctement.
- Chaque attribut est rattaché à l'entité ou à l'association qu'il décrit réellement.
- Chaque identifiant est unique et suffisamment stable pour la règle métier.
- Chaque association est nommée avec un verbe ou une expression claire.
- Les cardinalités minimales et maximales sont définies dans les deux directions.
- Les scénarios autorisés et interdits ont été testés mentalement ou par écrit.
- Les associations porteuses d'attributs sont représentées explicitement.
- Les relations plusieurs-à-plusieurs sont traduites en tables associatives dans le MLD.
- Les clés étrangères sont placées du côté approprié pour les relations un-à-plusieurs.
- Les règles d'unicité et les contraintes sont cohérentes avec les réinscriptions et l'historique.
- Les règles de suppression, d'archivage et de conservation sont documentées.
- Le MLD ne dépend pas inutilement d'un dialecte SQL avant l'étape physique.
- Les choix de type, d'index et de moteur sont reportés au MPD lorsqu'ils relèvent de l'implémentation.
- Les inconnues sont consignées plutôt que remplacées par des hypothèses silencieuses.
- Le modèle a été relu par une personne qui connaît le métier.
- Une série de tests couvrira les cas valides, invalides et limites avant la mise en production.

## 20. Synthèse finale

La modélisation relie les règles du métier à la structure des données. On commence par définir le périmètre et le vocabulaire, puis on identifie les entités, les attributs, les identifiants et les associations. Les cardinalités donnent le nombre minimum et maximum de participations, et doivent être lues dans chaque direction. Le MCD représente le sens métier sans imposer les détails du SGBD. Le MLD traduit ce sens en tables, clés primaires, clés étrangères et associations relationnelles. Le MPD précise ensuite les détails d'implémentation.

Les relations un-à-un, un-à-plusieurs et plusieurs-à-plusieurs exigent des traductions différentes. Une clé étrangère placée du côté plusieurs représente généralement une relation un-à-plusieurs. Une relation plusieurs-à-plusieurs devient une table d'association, particulièrement lorsque le lien possède ses propres attributs comme une date, une quantité, un statut ou un score. Une association porteuse d'attributs est souvent un concept à part entière dans le modèle logique.

La cardinalité n'exprime pas toutes les règles métier. Une limite de vingt participants, l'absence de chevauchement entre deux dates ou une politique d'historique exige une règle complémentaire. Un diagramme valide doit être confirmé par des scénarios concrets, et un MLD bien conçu doit être testé avec des valeurs qui respectent ou violent les contraintes.

Ne dessinez pas pour remplir une page. Dessinez pour lever les ambiguïtés, organiser la discussion et rendre les règles vérifiables. Le meilleur modèle est celui que l'équipe peut expliquer, traduire, tester et faire évoluer sans perdre le sens des données.

## Références techniques

Ces ressources complètent la leçon. Les notations de modélisation peuvent dépendre du cursus et de l'outil utilisé ; le modèle doit donc inclure sa propre légende. Les références SQL officielles permettent de vérifier les contraintes lorsque le MLD sera implémenté.

- PostgreSQL 18, contraintes : https://www.postgresql.org/docs/18/ddl-constraints.html
- PostgreSQL 18, création de tables : https://www.postgresql.org/docs/18/sql-createtable.html
- MySQL 8.4, contraintes de clés étrangères : https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html
- SQLite, création de tables et contraintes : https://www.sqlite.org/lang_createtable.html

Consultez la documentation du moteur et de sa version avant de généraliser une commande. Le MCD et le MLD expriment des décisions de conception ; ils ne remplacent ni les tests, ni les règles métier ni la politique d'exploitation.
