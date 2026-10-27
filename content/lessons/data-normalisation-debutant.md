# Normalisation (1NF, 2NF, 3NF) — Débutant

> **Mise en contexte.** Une plateforme de formation conserve des apprenants, des cours, des formateurs, des inscriptions et des résultats. Au début du projet, une seule table semble pratique : chaque inscription reprend le nom de l'apprenant, le titre du cours et le nom du formateur. Après quelques mois, les mêmes titres sont recopiés dans des dizaines de lignes. Quand un formateur change de nom, certaines lignes sont corrigées et d'autres non. Lorsqu'un cours n'a encore aucun inscrit, il est difficile de le créer sans inventer une inscription. Quand on supprime la dernière inscription, des informations sur le cours risquent de disparaître avec elle. Ces anomalies viennent moins de SQL que d'une mauvaise organisation des faits. La normalisation aide à placer chaque information à l'endroit où elle dépend réellement, à réduire les contradictions et à rendre les règles vérifiables.

## 1. Objectifs pédagogiques

Les cours précédents ont présenté les tables, les clés, les requêtes SQL, les jointures et les agrégations. La normalisation pousse le raisonnement un cran plus loin : au lieu de simplement interroger les tables existantes, vous allez évaluer si leur structure représente correctement les faits et les dépendances du métier.

La normalisation est une méthode de conception relationnelle. Elle aide à répartir les attributs dans des relations appropriées en tenant compte des clés et des dépendances entre les valeurs. Son objectif pratique est de réduire les redondances inutiles, les mises à jour contradictoires et les anomalies d'insertion ou de suppression. Elle ne signifie pas créer le plus grand nombre possible de tables ; elle consiste à représenter les faits selon des règles compréhensibles et à éviter que le même fait soit conservé plusieurs fois sans raison.

À la fin de la leçon, vous devrez savoir expliquer ce qu'est une dépendance fonctionnelle, reconnaître une clé candidate et une clé composée, comprendre la première forme normale (1NF), la deuxième forme normale (2NF) et la troisième forme normale (3NF), repérer les anomalies liées à la redondance, décomposer une grande relation en tables plus précises, identifier les clés primaires et étrangères de la décomposition, et vérifier que les données peuvent être reconstruites sans perdre les associations prévues.

Vous apprendrez également à reconnaître les limites de la normalisation. Une structure normalisée ne garantit pas à elle seule la qualité des données, les autorisations, la performance ou la bonne interprétation métier. Un modèle normalisé doit être accompagné de contraintes, de tests, de conventions de données et d'une stratégie d'exploitation. Dans certains contextes, une duplication contrôlée peut être utile pour la lecture ou le reporting, mais elle doit être volontaire, documentée et justifiée par des mesures, pas introduite par hasard.

Objectifs opérationnels :

- expliquer une dépendance fonctionnelle avec un exemple ;
- distinguer un identifiant d'une dépendance et d'une simple corrélation ;
- comprendre pourquoi une clé composée peut révéler des dépendances partielles ;
- détecter les colonnes qui répètent les mêmes faits dans plusieurs lignes ;
- appliquer les idées centrales de 1NF, 2NF et 3NF ;
- transformer une relation mal conçue en plusieurs relations cohérentes ;
- définir les clés primaires et les clés étrangères de la nouvelle structure ;
- vérifier qu'une décomposition conserve les faits sans créer de combinaisons inventées ;
- savoir quand une règle métier supplémentaire doit être imposée par une contrainte ou par le programme ;
- expliquer pourquoi la normalisation ne signifie pas forcément « une table par mot » ni « aucune redondance dans tout le système ».

## 2. Prérequis et environnement

Le prérequis du parcours est **data-sql-2-debutant — Jointures et agrégations SQL**. Vous devez connaître les tables, les clés primaires et étrangères, les jointures et la notion de granularité. Vous devez également pouvoir lire un petit jeu de données et expliquer ce que chaque ligne représente.

Les exemples utilisent une plateforme pédagogique. Nous devons suivre les apprenants, les cours, les formateurs, les inscriptions et les résultats. Le cas sera suffisamment petit pour être compris à la main, mais il reproduira des problèmes typiques rencontrés dans les applications métier.

Pour la pratique, utilisez une base isolée et des données fictives. Vous pouvez travailler avec SQLite, PostgreSQL ou MySQL ; les concepts relationnels restent communs, mais les types, les syntaxes d'identifiant et certaines options varient. Le cours ne dépend pas d'un dialecte SQL unique. Les scripts sont illustratifs et doivent être testés sur le moteur réel avant de réutiliser des décisions dans un environnement de production.

Avant de commencer, notez la version du moteur, le compte et la base utilisés, ainsi que la méthode de réinitialisation du laboratoire. Une décomposition de table en production peut nécessiter une migration, une copie contrôlée des données et des validations de cohérence. Ne réalisez pas de modifications structurelles sur une base réelle à partir d'un exemple de cours sans sauvegarde, plan de migration et revue.

## 3. Comprendre le problème : une grande table qui répète les faits

Imaginez une table appelée INSCRIPTIONS_DETAIL qui rassemble toutes les informations suivantes :

| apprenant_id | nom_apprenant | cours_id | titre_cours | formateur_id | nom_formateur | date_inscription | note |
|---:|---|---:|---|---:|---|---|---:|
| 10 | Amina | 100 | SQL débutant | 7 | Jules | 2026-09-01 | 82 |
| 11 | Samuel | 100 | SQL débutant | 7 | Jules | 2026-09-02 | 75 |
| 10 | Amina | 200 | Modélisation | 8 | Nadège | 2026-09-05 | 91 |
| 12 | Nadia | 100 | SQL débutant | 7 | Jules | 2026-09-06 | 88 |

Supposons que chaque ligne représente une inscription d'un apprenant à un cours. Dans cette version du modèle, on admet qu'un apprenant ne peut avoir qu'une seule inscription par cours ; l'identifiant composé (apprenant_id, cours_id) peut donc identifier la ligne. Si les réinscriptions, les sessions multiples ou les tentatives sont permises, cette hypothèse devra changer : nous y reviendrons.

La table contient plusieurs familles de faits. Le nom d'Amina décrit l'apprenant 10 ; le titre « SQL débutant » décrit le cours 100 ; le nom « Jules » décrit le formateur 7 ; la date et la note décrivent l'inscription du couple apprenant-cours. Ces faits ne dépendent pas tous de la même chose.

La table répète certains faits. Le titre du cours 100 apparaît dans chacune de ses inscriptions. Le nom de Jules est répété pour chaque inscription au cours 100. Amina apparaît à la fois pour SQL débutant et pour Modélisation. Répéter une valeur n'est pas toujours mauvais ; le problème est que plusieurs lignes prétendent conserver le même fait, et qu'il n'existe pas de garantie que toutes les copies restent identiques lorsque le fait évolue.

### 3.1 Trois anomalies classiques

**Anomalie de mise à jour.** Le cours 100 est renommé « SQL — Fondamentaux ». Si seulement deux des trois inscriptions sont mises à jour, le même cours possède deux titres dans la table. Le système ne sait plus quelle valeur fait autorité.

**Anomalie d'insertion.** L'équipe veut enregistrer le cours 300 « Administration PostgreSQL », attribué au formateur 9, avant qu'un apprenant ne s'y inscrive. La table exige un ensemble de colonnes qui décrit une inscription ; il faut soit inventer une ligne sans apprenant, soit attendre, soit utiliser des valeurs artificielles. Le modèle mélange le cours et l'inscription.

**Anomalie de suppression.** Si la dernière inscription au cours 200 est supprimée, la seule ligne où apparaissent son titre et le formateur 8 disparaît. La suppression d'une inscription a alors effacé accidentellement des informations sur le cours et le formateur.

Ces anomalies montrent que la table réunit plusieurs concepts dont les cycles de vie sont différents. Le nom d'un apprenant peut exister indépendamment d'une inscription ; le cours peut être planifié avant d'avoir des inscrits ; l'inscription peut être annulée sans supprimer le cours. Une conception robuste sépare ces faits puis les relie par des identifiants.

~~~mermaid
flowchart TD
    A["Table unique avec faits mélangés"] --> B["Redondance du nom et du titre"]
    B --> C["Anomalie de mise à jour"]
    A --> D["Impossible d'enregistrer certains faits seuls"]
    D --> E["Anomalie d'insertion"]
    A --> F["Suppression d'une ligne qui emporte d'autres faits"]
    F --> G["Anomalie de suppression"]
    C --> H["Décomposer les faits selon leurs dépendances"]
    E --> H
    G --> H
~~~

La normalisation offre un cadre pour décider comment répartir les colonnes en relations. Pour y parvenir, nous devons d'abord comprendre les clés et les dépendances fonctionnelles.

## 4. Clés, clés candidates et dépendances fonctionnelles

### 4.1 Une clé identifie une occurrence

Une clé est un attribut ou un ensemble d'attributs qui permet de distinguer une ligne des autres selon les règles du modèle. Dans notre table d'inscriptions, supposons que chaque apprenant ne puisse être inscrit qu'une fois à chaque cours. Le couple (apprenant_id, cours_id) constitue alors un identifiant possible.

Ni apprenant_id seul ni cours_id seul ne convient : un apprenant peut suivre plusieurs cours, et un cours peut avoir plusieurs apprenants. Le couple complet est nécessaire pour identifier l'inscription. On parle de clé composée parce qu'elle réunit plusieurs attributs.

Une **superclé** est un ensemble d'attributs qui identifie les lignes de manière unique, éventuellement avec des attributs supplémentaires inutiles. Une **clé candidate** est une superclé minimale : aucun de ses attributs ne peut être retiré sans perdre l'unicité. Une table peut posséder plusieurs clés candidates. Une **clé primaire** est la clé candidate choisie comme identifiant principal dans le modèle. Les autres clés candidates peuvent être protégées par des contraintes UNIQUE si le besoin l'exige.

L'unicité doit être fondée sur une règle métier confirmée, et pas uniquement sur l'état du petit jeu de test. Si Amina peut suivre SQL plusieurs fois lors de sessions différentes, le couple (apprenant_id, cours_id) n'est plus suffisant pour identifier une inscription. Il faudra inclure session_id, un numéro d'occurrence ou un identifiant distinct, selon les règles retenues.

### 4.2 Dépendance fonctionnelle

Une dépendance fonctionnelle, notée souvent \`X → Y\`, signifie que pour toute paire de lignes valides, si les valeurs de X sont identiques, les valeurs de Y doivent aussi être identiques. En langage courant : la valeur de X détermine la valeur de Y dans le domaine considéré.

Dans notre modèle, si apprenant_id identifie un apprenant, alors :

- apprenant_id → nom_apprenant
- apprenant_id → email_apprenant, si cet attribut est conservé dans le modèle

Si cours_id identifie un cours :

- cours_id → titre_cours
- cours_id → formateur_id, selon la règle que chaque cours possède un formateur responsable unique

Et si formateur_id identifie un formateur :

- formateur_id → nom_formateur

Enfin, si le couple (apprenant_id, cours_id) identifie une inscription :

- (apprenant_id, cours_id) → date_inscription
- (apprenant_id, cours_id) → note

Ces dernières dépendances expriment que la date et la note concernent l'inscription elle-même. Elles ne signifient pas nécessairement que la note est toujours connue ; si une note peut être absente, la règle doit définir le comportement attendu.

~~~mermaid
flowchart LR
    A["apprenant_id"] --> B["nom_apprenant"]
    A --> C["email_apprenant"]
    D["cours_id"] --> E["titre_cours"]
    D --> F["formateur_id"]
    F --> G["nom_formateur"]
    H["(apprenant_id, cours_id)"] --> I["date_inscription"]
    H --> J["note"]
~~~

La dépendance est une règle du domaine, pas un résultat statistique observé une fois. Si deux apprenants ont le même nom, le nom ne détermine pas l'identifiant. Si un formateur change de nom, son identifiant reste stable. Le fait que tous les noms soient différents dans les quatre lignes d'un exemple ne suffit pas à faire du nom une clé candidate.

### 4.3 Dépendance complète et dépendance partielle

Une dépendance \`X → Y\) est complète lorsque Y dépend de l'ensemble de la clé X et non d'une partie propre de cette clé. Elle est partielle lorsque certains attributs non-clés dépendent seulement d'une partie d'une clé composée.

Dans notre table d'inscription, la clé candidate est (apprenant_id, cours_id). La date_inscription dépend du couple complet : elle décrit cette inscription particulière. En revanche, nom_apprenant dépend uniquement d'apprenant_id. Le titre_cours dépend uniquement de cours_id. Ces deux derniers attributs ne dépendent donc que d'une partie de la clé composée.

Cette observation est capitale pour comprendre la deuxième forme normale. Quand une table possède une clé composée, examinez chaque attribut descriptif : dépend-il de la combinaison complète ou d'un seul composant ? S'il dépend d'une partie seulement, il est probablement placé au mauvais niveau.

### 4.4 Dépendance transitive

Une dépendance transitive se présente lorsque la clé détermine un attribut intermédiaire qui détermine à son tour un autre attribut. Dans l'exemple, cours_id détermine formateur_id et formateur_id détermine nom_formateur. On peut donc en déduire que cours_id détermine nom_formateur, mais cette dépendance passe par formateur_id.

Ce type de dépendance est lié au raisonnement de troisième forme normale. Le nom du formateur dépend de son identifiant, pas directement du fait qu'un apprenant s'inscrit à un cours. Si l'on conserve ce nom dans chaque ligne d'inscription, un changement du nom doit être propagé à toutes ces lignes.

Les dépendances fonctionnelles doivent toujours être interprétées dans un périmètre bien défini. Si chaque cours peut être confié à plusieurs formateurs, la règle cours_id → formateur_id ne tient plus. Une nouvelle relation entre cours et formateurs doit représenter cette multiplicité. La normalisation commence donc par la compréhension du métier ; on ne peut pas déduire toutes les règles du nom des colonnes.

## 5. Première forme normale (1NF) : des valeurs structurées correctement

La première forme normale est habituellement présentée au niveau débutant par deux idées pratiques : chaque cellule contient une valeur du domaine attendu, et les groupes répétitifs ou les listes de valeurs ne sont pas stockés dans une même colonne comme substitut à une structure relationnelle. La définition théorique repose sur les relations et les valeurs atomiques dans le modèle ; le mot « atomique » dépend du domaine et des opérations dont l'application a besoin.

Une table comme celle-ci pose un problème :

| apprenant_id | nom | cours_1 | cours_2 | cours_3 |
|---:|---|---|---|---|
| 10 | Amina | SQL | Modélisation | NULL |
| 11 | Samuel | SQL | NULL | NULL |

Les colonnes cours_1, cours_2 et cours_3 représentent un groupe répétitif. Que se passe-t-il lorsqu'un apprenant veut suivre dix cours ? Faut-il ajouter cours_4, cours_5 et cours_6 ? Comment rechercher tous les apprenants de Modélisation sans examiner chacune des colonnes ? Comment représenter la date ou le statut de chaque inscription ? Cette structure ajoute une limite arbitraire et rend les requêtes fragiles.

Une autre forme problématique consiste à placer des identifiants séparés par des virgules dans une seule cellule :

| apprenant_id | nom | cours_ids |
|---:|---|---|
| 10 | Amina | 100,200,300 |
| 11 | Samuel | 100 |

La colonne cours_ids représente plusieurs associations dans un champ texte. La base ne peut pas appliquer normalement une clé étrangère à chaque identifiant de cette liste. Les recherches par élément et la modification d'une seule association deviennent plus délicates. Il devient difficile de garantir qu'un cours référencé existe ou qu'un apprenant n'a pas deux fois le même cours.

La structure relationnelle normale consiste à représenter chaque inscription comme une ligne, avec une référence à l'apprenant et une référence au cours. Le nombre de cours n'est plus codé dans le nombre de colonnes ni dans une liste texte.

~~~mermaid
flowchart TD
    A["Colonnes répétées ou liste dans une cellule"] --> B["Difficile à filtrer et valider"]
    B --> C["Une ligne par association apprenant-cours"]
    C --> D["Colonnes simples : apprenant_id, cours_id, date, note"]
    D --> E["Clés et contraintes peuvent protéger les liens"]
~~~

La première forme normale ne signifie pas qu'il faut couper tous les textes en mots. Un nom complet peut rester un attribut si le système ne doit pas traiter séparément le prénom et le nom ; si la recherche ou le traitement exige une distinction, on peut envisager des attributs séparés. Une adresse peut être conservée en une seule valeur pour l'affichage, mais une application qui doit filtrer par pays, ville et code postal peut nécessiter une structure plus détaillée. L'atomicité se comprend en fonction de la sémantique métier et des opérations prévues.

### 5.1 Tester la 1NF par des questions pratiques

- Une cellule contient-elle une liste de valeurs indépendantes ?
- Existe-t-il des colonnes répétées numérotées comme cours_1, cours_2, cours_3 ?
- Est-il nécessaire de parser un texte pour retrouver une référence à une autre entité ?
- Peut-on ajouter une nouvelle occurrence du même type sans modifier la structure de la table ?
- Les valeurs sont-elles compréhensibles et manipulables selon le domaine prévu ?

Ces questions ne remplacent pas la définition théorique complète, mais elles servent à repérer les défauts les plus courants dans une conception débutante. Une fois la 1NF vérifiée, le travail continue : une table peut posséder des valeurs atomiques et néanmoins contenir de fortes redondances.

## 6. Deuxième forme normale (2NF) : éliminer les dépendances partielles

La deuxième forme normale concerne les dépendances entre les clés et les attributs non-clés. Une relation est en 2NF lorsqu'elle est en 1NF et qu'aucun attribut non-prime ne dépend d'une partie propre d'une clé candidate. Pour un premier apprentissage, cela signifie surtout : si la clé est composée de plusieurs colonnes, les attributs descriptifs de la table doivent dépendre de la clé complète, pas d'un seul de ses composants.

Dans notre table INSCRIPTIONS_DETAIL, nous supposons que la clé primaire est (apprenant_id, cours_id). Or :

- nom_apprenant dépend uniquement d'apprenant_id ;
- titre_cours dépend uniquement de cours_id ;
- formateur_id dépend uniquement de cours_id si chaque cours possède un formateur responsable ;
- date_inscription et note dépendent du couple apprenant_id, cours_id.

Les colonnes nom_apprenant, titre_cours et formateur_id sont partiellement dépendantes de la clé composée. Cette table n'est donc pas en 2NF selon les règles de ce modèle.

La correction consiste à séparer les faits selon ce qu'ils décrivent :

**APPRENANTS**
- apprenant_id
- nom_apprenant
- email_apprenant

**COURS**
- cours_id
- titre_cours
- formateur_id

**INSCRIPTIONS**
- apprenant_id
- cours_id
- date_inscription
- note

Dans INSCRIPTIONS, la clé composée (apprenant_id, cours_id) détermine la date et la note. Le nom de l'apprenant se trouve dans APPRENANTS et le titre du cours dans COURS. Chaque fait est conservé au niveau qui correspond à sa dépendance.

~~~mermaid
flowchart TD
    A["INSCRIPTIONS_DETAIL<br/>clé : apprenant_id + cours_id"] --> B["Nom de l'apprenant dépend de apprenant_id"]
    A --> C["Titre du cours dépend de cours_id"]
    A --> D["Date et note dépendent du couple"]
    B --> E["Table APPRENANTS"]
    C --> F["Table COURS"]
    D --> G["Table INSCRIPTIONS"]
~~~

La transformation réduit les copies du nom et du titre. Elle permet aussi de créer un apprenant sans inscription, ou un cours sans inscrit, si les règles du système le permettent. Le modèle reflète plus fidèlement le cycle de vie des faits.

### 6.1 Pourquoi la 2NF est-elle surtout liée aux clés composées ?

Si chaque clé candidate est constituée d'un seul attribut, aucun sous-ensemble propre non vide de cette clé n'existe. Dans ce cas, il n'y a pas de dépendance partielle de la forme examinée ici. Cela ne veut pas dire qu'une table avec une clé simple est automatiquement bien normalisée : des dépendances transitives ou d'autres anomalies peuvent encore exister, notamment si un attribut non-clé détermine un autre attribut non-clé.

La présence d'une clé technique simple peut masquer visuellement le problème d'une clé métier composée. Par exemple, si on ajoute inscription_id comme clé primaire mais que le système impose au maximum une inscription par couple apprenant-cours, le couple peut toujours être une clé candidate métier. Il faut conserver cette règle avec une contrainte UNIQUE si elle est requise. Ajouter un identifiant technique ne supprime pas magiquement les dépendances qui existent entre les données.

### 6.2 Exemple de dépendance partielle en dehors de la formation

Une table de lignes de commande pourrait contenir :
- commande_id
- produit_id
- date_commande
- nom_produit
- quantité
- prix_unitaire

Si la clé est (commande_id, produit_id), date_commande dépend normalement de commande_id seul et nom_produit dépend de produit_id seul. quantité peut dépendre du couple commande-produit. Le prix unitaire nécessite une règle métier plus précise : s'il représente le prix courant du produit, il dépend de produit_id ; s'il représente le prix effectivement vendu, il appartient à la ligne de commande et dépend du couple, éventuellement de la version de prix ou de l'offre appliquée.

La normalisation exige donc une lecture métier précise. Il serait incorrect de déplacer automatiquement prix_unitaire dans PRODUITS sans déterminer s'il décrit le prix catalogue ou le prix historique. La règle de dépendance vient du sens de la donnée, pas du fait que les valeurs se ressemblent dans un jeu de test.

## 7. Troisième forme normale (3NF) : éliminer certaines dépendances transitives

La troisième forme normale est une condition supplémentaire. Dans une explication simplifiée adaptée au débutant, une relation doit être en 2NF et ses attributs non-clés ne doivent pas dépendre transitivement de la clé par un autre attribut non-clé. La définition formelle s'exprime à travers les dépendances fonctionnelles et les attributs premiers ; ce cours utilise l'intuition pratique qui permet d'identifier les redondances courantes.

Après la décomposition liée à la 2NF, notre table COURS peut posséder :
- cours_id
- titre_cours
- formateur_id
- nom_formateur

Si la règle est \`cours_id → formateur_id\` et \`formateur_id → nom_formateur\`, le nom du formateur est dépendant transitivement de cours_id via formateur_id. Le nom du formateur devrait être enregistré dans une table FORMATEURS, identifiée par formateur_id. La table COURS conserve la référence vers ce formateur.

On obtient alors :

**FORMATEURS**
- formateur_id — clé primaire
- nom_formateur

**COURS**
- cours_id — clé primaire
- titre_cours
- formateur_id — clé étrangère

Le nom du formateur n'est plus copié dans chaque cours. Si le formateur modifie son nom d'affichage, une seule ligne de FORMATEURS est mise à jour. Tous les cours continuent de le référencer via formateur_id.

~~~mermaid
flowchart LR
    C["cours_id"] --> F["formateur_id"]
    F --> N["nom_formateur"]
    C -. "dépendance transitive" .-> N
    N --> T["Placer nom_formateur dans FORMATEURS"]
    T --> R["COURS conserve formateur_id"]
~~~

### 7.1 Pourquoi ne pas mettre le nom du formateur dans chaque cours ?

On pourrait recopier nom_formateur dans COURS parce que chaque cours possède un formateur responsable. Mais si le formateur intervient sur dix cours, le même nom serait stocké dix fois. Une correction aurait alors besoin d'être répercutée partout. Si une seule ligne reste ancienne, la base présente deux noms pour un même formateur.

Cela ne signifie pas qu'un nom ne peut jamais être enregistré dans une relation différente. Dans un modèle d'historique, une organisation peut conserver le nom du formateur tel qu'il apparaissait lors d'un événement passé. Il s'agit alors d'un instantané historique avec une règle différente, pas d'une copie accidentelle du nom courant. La justification de chaque duplication doit être explicite.

### 7.2 Une attention importante : dépendance métier versus coïncidence

Supposons que tous les cours du jeu de test aient un formateur nommé « Jules ». Il serait incorrect de conclure que cours_id détermine nom_formateur uniquement parce que les quatre lignes possèdent la même valeur. La règle métier doit dire comment les formateurs sont affectés. Les dépendances fonctionnelles ne se déduisent pas d'une coïncidence dans un échantillon minuscule.

De même, deux formateurs peuvent partager le même nom. Le nom ne détermine donc pas nécessairement formateur_id. Utiliser nom_formateur comme clé serait risqué si les homonymes, changements de nom ou variantes d'écriture sont possibles. L'identifiant sert à relier les occurrences, tandis que le nom les décrit.

## 8. MCD, MLD et normalisation : comment les concepts se complètent

La modélisation et la normalisation sont liées, mais répondent à des questions distinctes. Le MCD clarifie les entités, les associations, les attributs et les cardinalités selon le métier. Le MLD traduit ces concepts en relations, clés et références. La normalisation examine si les relations résultantes respectent certaines formes normales en tenant compte des dépendances fonctionnelles et des clés candidates.

Un MCD où les inscriptions, les cours et les apprenants sont mélangés en un seul concept n'exprime pas correctement les cycles de vie séparés. À l'inverse, un MCD correct peut être mal transformé en MLD si l'on copie les attributs du cours dans la table d'inscription ou si l'on crée un groupe de colonnes répétées. Les deux démarches se complètent : modéliser les concepts d'abord, vérifier ensuite les dépendances et la structure relationnelle.

~~~mermaid
flowchart TD
    A["Règles métier et dictionnaire"] --> B["MCD : concepts, liens, cardinalités"]
    B --> C["MLD : relations, clés, références"]
    C --> D["Analyser clés candidates et dépendances"]
    D --> E["Vérifier 1NF"]
    E --> F["Vérifier 2NF"]
    F --> G["Vérifier 3NF"]
    G --> H["Préparer le modèle physique"]
    H --> I["Implémenter et tester"]
~~~

Il faut rester attentif aux associations porteuses d'attributs. L'inscription a une date et une note ; elle possède un sens propre et devient une table de relation. Les attributs sont alors évalués selon la clé de cette relation. La normalisation ne consiste pas à déplacer chaque colonne vers la table la plus proche par son nom, mais à identifier le fait exact décrit par chaque valeur.

## 9. Décomposition : des tables plus petites mais reliées

Une décomposition transforme une relation en plusieurs relations plus petites. Une bonne décomposition devrait préserver le sens des données, permettre de reconstruire les associations prévues et éviter de créer des combinaisons qui n'existaient pas. Elle doit également préserver, autant que possible, les dépendances fonctionnelles utiles afin que les règles puissent être appliquées dans le schéma résultant.

Pour notre exemple, on passe de INSCRIPTIONS_DETAIL à quatre relations :

- APPRENANTS(apprenant_id, nom_apprenant, email_apprenant)
- FORMATEURS(formateur_id, nom_formateur)
- COURS(cours_id, titre_cours, formateur_id)
- INSCRIPTIONS(apprenant_id, cours_id, date_inscription, note)

Le MLD peut être représenté ainsi :

~~~mermaid
erDiagram
    FORMATEURS ||--o{ COURS : "responsable de"
    COURS ||--o{ INSCRIPTIONS : "recoit"
    APPRENANTS ||--o{ INSCRIPTIONS : "effectue"
    APPRENANTS {
        int apprenant_id PK
        string nom_apprenant
        string email_apprenant
    }
    FORMATEURS {
        int formateur_id PK
        string nom_formateur
    }
    COURS {
        int cours_id PK
        string titre_cours
        int formateur_id FK
    }
    INSCRIPTIONS {
        int apprenant_id PK, FK
        int cours_id PK, FK
        date date_inscription
        decimal note
    }
~~~

La clé primaire de INSCRIPTIONS est composée du couple apprenant_id, cours_id dans l'hypothèse qu'une seule inscription existe par apprenant et cours. Chaque table possède les attributs qui dépendent de l'identifiant de cette table. La relation est reliée par les clés étrangères. Les données ne sont pas dispersées au hasard : elles sont organisées autour de l'identité du fait qu'elles décrivent.

### 9.1 Décomposition sans perte

Une décomposition est sans perte lorsque la jointure des relations décomposées permet de retrouver exactement les associations prévues dans la relation initiale, sans perdre de tuples valides ni en fabriquer. Cette notion est essentielle : l'objectif de la normalisation n'est pas d'éliminer la redondance en détruisant l'information.

Dans notre modèle, chaque inscription référence un apprenant existant et un cours existant. En rejoignant INSCRIPTIONS à APPRENANTS par apprenant_id et à COURS par cours_id, on retrouve le nom de l'apprenant et le titre du cours associés à cette inscription. COURS référence à son tour FORMATEURS. Les clés doivent garantir les relations attendues et l'ensemble des jointures doit correspondre à la structure choisie.

La propriété sans perte dépend de la façon dont la décomposition est réalisée et des dépendances fonctionnelles qui justifient les relations. On ne peut pas décomposer une table au hasard puis espérer que les jointures reconstruisent la vérité. Les clés et les relations doivent être définies et vérifiées.

### 9.2 Préservation des dépendances

Une décomposition devrait aussi préserver les dépendances importantes de façon à permettre leur contrôle sans avoir à reconstruire un grand nombre de relations à chaque validation. Par exemple, apprenant_id détermine nom_apprenant dans APPRENANTS ; formateur_id détermine nom_formateur dans FORMATEURS ; cours_id détermine titre_cours et formateur_id dans COURS ; le couple apprenant_id-cours_id détermine les attributs de l'inscription.

Si une règle ne peut être vérifiée qu'en recroisant plusieurs tables, il faut comprendre si cela est nécessaire ou si une meilleure conception permet de la protéger plus simplement. Toutes les contraintes complexes ne peuvent pas être exprimées par une simple clé ou CHECK ; certaines demandent une logique applicative ou transactionnelle. La modélisation doit préciser où chaque règle est garantie.

## 10. Traduction SQL illustrative

Le schéma suivant montre une implémentation relationnelle possible. Adaptez les types et la génération des identifiants au moteur choisi.

~~~sql
CREATE TABLE formateurs (
    formateur_id INTEGER PRIMARY KEY,
    nom_formateur VARCHAR(120) NOT NULL
);

CREATE TABLE apprenants (
    apprenant_id INTEGER PRIMARY KEY,
    nom_apprenant VARCHAR(120) NOT NULL,
    email_apprenant VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE cours (
    cours_id INTEGER PRIMARY KEY,
    titre_cours VARCHAR(160) NOT NULL,
    formateur_id INTEGER NOT NULL,
    FOREIGN KEY (formateur_id)
        REFERENCES formateurs(formateur_id)
);

CREATE TABLE inscriptions (
    apprenant_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    note DECIMAL(5,2),
    PRIMARY KEY (apprenant_id, cours_id),
    FOREIGN KEY (apprenant_id)
        REFERENCES apprenants(apprenant_id),
    FOREIGN KEY (cours_id)
        REFERENCES cours(cours_id),
    CHECK (note IS NULL OR (note >= 0 AND note <= 100))
);
~~~

La clé composée de INSCRIPTIONS empêche le même apprenant d'être inscrit deux fois au même cours. Elle correspond à l'hypothèse du scénario. Si le système autorise plusieurs sessions ou tentatives, cette clé doit évoluer, par exemple en ajoutant session_id ou un identifiant d'inscription. Il ne faut pas appliquer le script sans vérifier que le métier respecte effectivement cette hypothèse.

La note est facultative dans cet exemple parce qu'un apprenant peut être inscrit avant d'avoir passé l'évaluation. CHECK autorise donc NULL ou un score entre zéro et cent. Cette contrainte valide une plage de valeur, mais elle ne garantit pas qu'un apprenant a réellement passé l'examen ni que le résultat a été calculé correctement. L'état métier de l'évaluation peut nécessiter une relation distincte.

Le champ email_apprenant est déclaré unique parce que le modèle suppose un email unique par compte. Si l'application permet plusieurs comptes partageant une adresse, cette règle doit être revue. Le fait qu'une contrainte apparaisse dans un script ne prouve pas qu'elle correspond aux besoins : il faut d'abord confirmer la règle, puis tester la contrainte sur le moteur réel.

## 11. Reconstruire une vue avec des jointures

Après normalisation, les données ne sont plus toutes dans une table unique. Pour afficher le nom d'un apprenant, le titre du cours et la note, il faut relier les tables.

~~~sql
SELECT
    a.apprenant_id,
    a.nom_apprenant,
    c.cours_id,
    c.titre_cours,
    f.nom_formateur,
    i.date_inscription,
    i.note
FROM inscriptions AS i
INNER JOIN apprenants AS a
    ON a.apprenant_id = i.apprenant_id
INNER JOIN cours AS c
    ON c.cours_id = i.cours_id
INNER JOIN formateurs AS f
    ON f.formateur_id = c.formateur_id
ORDER BY a.apprenant_id, c.cours_id;
~~~

Cette vue de lecture ressemble au contenu de l'ancienne table INSCRIPTIONS_DETAIL, mais les faits sont désormais conservés dans les relations qui leur correspondent. Le nom de l'apprenant provient d'APPRENANTS, le titre et le formateur sont récupérés depuis COURS et FORMATEURS, tandis que la date et la note proviennent d'INSCRIPTIONS.

La duplication peut encore être visible dans la sortie du rapport, car chaque inscription affiche le nom de l'apprenant et le titre du cours. Ce n'est pas une redondance de stockage : c'est une répétition dans le résultat construit pour répondre à une question. La normalisation concerne principalement l'organisation des relations stockées et les dépendances qui régissent ces données. Les rapports peuvent répéter volontairement des valeurs pour être lisibles.

Cette distinction est importante : si l'on juge la normalisation seulement à partir de l'affichage d'un rapport, on pourrait croire que le problème est toujours présent. La question porte sur l'endroit où la donnée est conservée et sur l'autorité qui fait foi, pas simplement sur le nombre de fois qu'une valeur apparaît dans un résultat.

## 12. Comprendre les trois formes normales par un résumé comparatif

| Forme normale | Idée pratique au niveau débutant | Problème typique détecté |
|---|---|---|
| 1NF | Valeurs structurées et absence de groupes répétitifs encodés dans des colonnes ou listes | cours_1, cours_2 ou liste d'IDs dans un champ |
| 2NF | En 1NF, chaque attribut non-clé dépend de la clé candidate complète, pas d'une partie propre d'une clé composée | nom_apprenant dépend seulement d'apprenant_id |
| 3NF | En 2NF, éviter les dépendances transitives inappropriées des attributs non-clés par d'autres attributs non-clés | nom_formateur dépend de formateur_id, lui-même déterminé par cours_id |

Ce tableau est une aide pédagogique, pas un substitut aux définitions formelles. Les définitions exactes s'appuient sur les clés candidates, les attributs premiers et les dépendances fonctionnelles. Le raisonnement pratique reste utile : identifier le fait, identifier sa clé, identifier les attributs qui en dépendent, puis placer les données dans des relations adaptées.

Une table peut satisfaire 1NF mais pas 2NF. Elle peut satisfaire 2NF mais pas 3NF. En revanche, atteindre 3NF implique les formes précédentes selon les définitions classiques. Ne passez pas directement à « trois tables parce qu'il y a trois formes normales » : le nombre de tables vient des dépendances et du domaine, pas du chiffre de la forme normale.

Il est également utile de connaître l'existence d'une forme normale plus stricte, la forme normale de Boyce-Codd (BCNF). Dans certains cas, une relation peut satisfaire 3NF mais rester problématique au regard de BCNF. Ce sujet demande une analyse plus formelle des déterminants et des clés candidates ; il sera étudié à un niveau ultérieur. Pour ce premier parcours, retenez que 3NF est une étape classique de conception et non une garantie absolue contre toutes les anomalies possibles.

## 13. Quand la normalisation ne suffit pas

La normalisation réduit certains types de redondance et clarifie les dépendances. Elle ne garantit pas que les règles de toutes les applications sont correctes. Une table normalisée peut accepter un prix négatif si aucune contrainte ne l'interdit. Une inscription peut référence un cours valide tout en dépassant la capacité d'une session si cette règle n'est pas contrôlée. Une base peut être normalisée et demeurer vulnérable si les droits sont trop larges ou si les secrets sont exposés.

Il faut donc associer la normalisation à d'autres garanties :
- contraintes de clé primaire, clé étrangère, unicité et validité ;
- validation des règles métier qui dépassent les contraintes simples ;
- transactions pour les opérations qui doivent être cohérentes ensemble ;
- gestion des permissions et des données sensibles ;
- sauvegardes et tests de restauration ;
- tests de migration lors des changements de structure ;
- surveillance et procédures de diagnostic.

Un autre sujet est la performance. Joindre plusieurs tables est parfois plus coûteux qu'une lecture dans une table dénormalisée, mais le coût doit être mesuré. Les SGBD modernes savent optimiser de nombreuses jointures. Une duplication peut parfois être introduite pour un rapport ou un cache, mais elle crée une obligation de synchronisation : il faut savoir quelle donnée fait autorité, comment la copie est rafraîchie et comment détecter un écart. Ne dénormalisez pas seulement parce que plusieurs tables vous semblent moins simples au premier abord.

## 14. Dénormalisation contrôlée : comprendre le compromis

La dénormalisation consiste à introduire volontairement une redondance ou à pré-calculer une information pour répondre à un besoin de lecture, d'analyse ou de performance. Elle peut prendre plusieurs formes : une vue matérialisée, une table de synthèse, un cache, un instantané historique ou une duplication de certains attributs. La dénormalisation n'est pas une excuse pour ignorer les formes normales au moment de la conception ; elle est une décision d'architecture qui doit être justifiée par un besoin mesuré.

Exemple : une table de reporting mensuel peut stocker le total des ventes par mois et par catégorie pour éviter de recalculer chaque agrégation sur un gros volume de lignes. Cette table est dérivée des transactions sources. Il faut définir comment et quand elle est recalculée, comment les retours et corrections sont pris en compte, et comment comparer ses valeurs aux données de référence. Si le job de rafraîchissement échoue, le tableau de bord peut afficher des chiffres obsolètes.

Il existe aussi une raison métier de conserver un instantané. Une inscription peut conserver le titre du cours ou la version des objectifs à la date où l'apprenant a commencé. Si l'historique doit refléter ce qui était présenté à ce moment, la duplication est intentionnelle et porte une sémantique historique. Elle doit être documentée comme telle et ne doit pas être écrasée par la modification du titre courant.

La règle pratique est donc : normaliser d'abord pour clarifier les faits et leurs dépendances ; mesurer ensuite les besoins de performance ou d'historique ; enfin, introduire uniquement les redondances qui ont une raison explicite et une stratégie de cohérence. Toute donnée dupliquée devrait répondre à la question : quelle source fait foi, et comment vérifier les copies ?

## 15. Atelier pratique guidé : corriger une table d'inscriptions

Cet atelier part de la relation illustrative INSCRIPTIONS_DETAIL du début de leçon. Le but est de repérer les dépendances partielles, de supprimer la dépendance transitive et de produire un MLD cohérent. Vous pouvez le réaliser sur papier avant de créer les tables.

### Étape 1 — Écrire les règles

Supposons les règles suivantes :
1. apprenant_id identifie un seul apprenant.
2. cours_id identifie un seul cours.
3. formateur_id identifie un seul formateur.
4. chaque cours a un formateur responsable unique pour le modèle initial.
5. un apprenant ne peut avoir qu'une seule inscription au même cours dans cette version.
6. la date d'inscription et la note concernent le couple apprenant-cours.
7. une note est comprise entre 0 et 100, ou NULL si l'évaluation n'a pas encore eu lieu.

Ces règles définissent les dépendances utilisées. Si le système autorise plusieurs sessions ou tentatives, nous devons revoir la règle 5 avant de choisir la clé d'inscription.

### Étape 2 — Établir les dépendances

À partir des règles :
- apprenant_id → nom_apprenant, email_apprenant
- cours_id → titre_cours, formateur_id
- formateur_id → nom_formateur
- (apprenant_id, cours_id) → date_inscription, note

La clé composée de la relation initiale est (apprenant_id, cours_id). Le nom de l'apprenant est déterminé par un seul composant de la clé. Le titre du cours et son formateur le sont par l'autre composant. Le nom du formateur dépend de formateur_id. Ces dépendances indiquent où les faits doivent être déplacés.

### Étape 3 — Décomposer le MLD

**APPRENANTS** (\`apprenant_id\` PK, nom_apprenant, email_apprenant)

**FORMATEURS** (\`formateur_id\` PK, nom_formateur)

**COURS** (\`cours_id\` PK, titre_cours, \`formateur_id\` FK)

**INSCRIPTIONS** (\`apprenant_id\` PK/FK, \`cours_id\` PK/FK, date_inscription, note)

Cette structure retire les dépendances partielles de la table d'inscription et place le nom du formateur dans la relation correspondant à son identifiant. Les clés étrangères préservent les relations entre les faits. Les contraintes de domaine et les règles de réinscription devront être contrôlées au niveau physique.

### Étape 4 — Créer les tables

~~~sql
CREATE TABLE apprenants (
    apprenant_id INTEGER PRIMARY KEY,
    nom_apprenant VARCHAR(120) NOT NULL,
    email_apprenant VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE formateurs (
    formateur_id INTEGER PRIMARY KEY,
    nom_formateur VARCHAR(120) NOT NULL
);

CREATE TABLE cours (
    cours_id INTEGER PRIMARY KEY,
    titre_cours VARCHAR(160) NOT NULL,
    formateur_id INTEGER NOT NULL,
    FOREIGN KEY (formateur_id)
        REFERENCES formateurs(formateur_id)
);

CREATE TABLE inscriptions (
    apprenant_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    date_inscription DATE NOT NULL,
    note DECIMAL(5,2),
    PRIMARY KEY (apprenant_id, cours_id),
    FOREIGN KEY (apprenant_id)
        REFERENCES apprenants(apprenant_id),
    FOREIGN KEY (cours_id)
        REFERENCES cours(cours_id),
    CHECK (note IS NULL OR (note >= 0 AND note <= 100))
);
~~~

La syntaxe des identifiants et des types doit être adaptée au moteur choisi. Ne supposez pas que tout comportement spécifique de SQLite, PostgreSQL et MySQL est identique. Le script illustre les relations logiques et les contraintes que le modèle veut exprimer.

### Étape 5 — Insérer des données synthétiques

~~~sql
INSERT INTO apprenants (apprenant_id, nom_apprenant, email_apprenant)
VALUES
    (10, 'Amina', 'amina@example.test'),
    (11, 'Samuel', 'samuel@example.test'),
    (12, 'Nadia', 'nadia@example.test');

INSERT INTO formateurs (formateur_id, nom_formateur)
VALUES
    (7, 'Jules'),
    (8, 'Nadège');

INSERT INTO cours (cours_id, titre_cours, formateur_id)
VALUES
    (100, 'SQL débutant', 7),
    (200, 'Modélisation', 8);

INSERT INTO inscriptions
    (apprenant_id, cours_id, date_inscription, note)
VALUES
    (10, 100, '2026-09-01', 82),
    (11, 100, '2026-09-02', 75),
    (10, 200, '2026-09-05', 91),
    (12, 100, '2026-09-06', 88);
~~~

Ces lignes reprennent les exemples de départ, mais les faits sont désormais placés dans les tables correspondantes. Amina est conservée une fois dans APPRENANTS et peut être reliée à plusieurs cours via INSCRIPTIONS. Le titre « SQL débutant » est conservé une fois dans COURS et les inscriptions réfèrent au cours par cours_id.

### Étape 6 — Reconstituer une vue lisible

~~~sql
SELECT
    a.apprenant_id,
    a.nom_apprenant,
    c.cours_id,
    c.titre_cours,
    f.nom_formateur,
    i.date_inscription,
    i.note
FROM inscriptions AS i
INNER JOIN apprenants AS a
    ON a.apprenant_id = i.apprenant_id
INNER JOIN cours AS c
    ON c.cours_id = i.cours_id
INNER JOIN formateurs AS f
    ON f.formateur_id = c.formateur_id
ORDER BY a.apprenant_id, c.cours_id;
~~~

Le résultat reconstitue les associations de l'ancienne relation, mais les faits sont conservés séparément. Vérifiez les quatre inscriptions prévues et les noms et titres associés. Le résultat de lecture répète des valeurs pour chaque inscription, ce qui est normal ; ces répétitions sont générées par la jointure et ne signifient pas que le nom est stocké plusieurs fois dans APPRENANTS.

### Étape 7 — Tester les règles

Essayez de créer une inscription qui référence un apprenant absent. La clé étrangère doit la rejeter. Essayez d'insérer une note égale à 150 : la contrainte CHECK doit la rejeter. Essayez d'ajouter deux fois le même couple apprenant-cours : la clé primaire composée doit empêcher la duplication dans l'hypothèse retenue.

Le test du couple en double révèle la limite de cette hypothèse. Si le métier accepte plusieurs tentatives ou sessions par cours, la contrainte est trop stricte. Il faudra ajouter l'identité de la session ou de la tentative dans la table et revoir les dépendances fonctionnelles. Une règle de normalisation correcte dépend d'une clé correcte ; un identifiant incomplet rend toutes les conclusions suivantes fragiles.

### Critères d'acceptation de l'atelier

Vous avez réussi si vous pouvez expliquer pourquoi le nom de l'apprenant dépend de apprenant_id, pourquoi le titre du cours dépend de cours_id, pourquoi le nom du formateur est conservé dans FORMATEURS, et pourquoi la date et la note dépendent du couple d'inscription. Vous devez aussi reconstituer les mêmes associations par jointure et montrer au moins une insertion valide et deux rejets conformes aux règles.

## 16. Exercices d'application avec corrigés

### Exercice 1 — Repérer une anomalie

Une table COMMANDE_DETAIL contient commande_id, date_commande, client_id, nom_client, produit_id, quantite. Le même client possède plusieurs commandes et le même nom client est répété. Donnez une anomalie possible et une correction.

**Corrigé.** Si le client change de nom et que certaines commandes ne sont pas corrigées, la table présente des valeurs contradictoires. Il faut séparer CLIENT et COMMANDE, puis référencer client_id dans COMMANDE. Si chaque commande contient plusieurs produits, une table LIGNE_COMMANDE porte la quantité et la référence produit. La décomposition dépend des règles de cardinalité mais évite de recopier l'identité du client dans chaque ligne.

### Exercice 2 — Identifier une dépendance fonctionnelle

Dans une table COURS(cours_id, titre, formateur_id), chaque cours a un seul titre courant et un seul formateur responsable. Quelle dépendance fonctionnelle exprime cette règle ?

**Corrigé.** cours_id → titre et cours_id → formateur_id. Le cours est identifié par cours_id ; les deux attributs sont déterminés par cet identifiant selon les règles du modèle. Si un cours a plusieurs formateurs, la seconde dépendance ne tient plus et le MCD doit représenter cette relation autrement.

### Exercice 3 — Dépendance partielle

Une table INSCRIPTION a pour clé composée (apprenant_id, cours_id), avec nom_apprenant, titre_cours, date_inscription et note. Quelles colonnes dépendent seulement d'une partie de la clé ?

**Corrigé.** nom_apprenant dépend seulement d'apprenant_id, tandis que titre_cours dépend seulement de cours_id. date_inscription et note sont supposées dépendre du couple complet. Les deux premiers attributs doivent être déplacés vers les relations APPRENANTS et COURS pour respecter l'objectif de 2NF dans ce modèle.

### Exercice 4 — Dépendance transitive

Dans COURS(cours_id, titre, formateur_id, nom_formateur), on sait que cours_id détermine formateur_id et que formateur_id détermine nom_formateur. Quel problème de 3NF apparaît ?

**Corrigé.** nom_formateur dépend transitivement de cours_id via formateur_id. Il doit être conservé dans FORMATEURS, identifiée par formateur_id, tandis que COURS garde la clé étrangère. Cela réduit la duplication du nom et les anomalies de mise à jour.

### Exercice 5 — Première forme normale

Une application stocke les cours d'un apprenant dans un champ texte « 100,200,300 ». Pourquoi cette solution est-elle fragile ?

**Corrigé.** Le champ contient plusieurs références au lieu d'une seule valeur relationnelle manipulable. La base ne peut pas facilement garantir une clé étrangère par identifiant ; les recherches, insertions et suppressions partielles demandent de parser le texte. Une table d'inscription avec une ligne par couple apprenant-cours rend les liens explicites et vérifiables.

### Exercice 6 — Une clé technique règle-t-elle tout ?

Une table ajoute inscription_id comme clé primaire, mais chaque apprenant ne doit pouvoir s'inscrire qu'une seule fois à chaque cours. Peut-on oublier la contrainte sur le couple apprenant_id-cours_id ?

**Corrigé.** Non. inscription_id garantit l'identité technique d'une ligne, mais deux lignes peuvent encore représenter le même couple apprenant-cours si rien ne l'interdit. Il faut une contrainte UNIQUE sur le couple si cette règle est confirmée. Si les réinscriptions sont permises, le modèle doit ajouter le contexte qui distingue les occurrences.

### Exercice 7 — Corriger une table de cours

Une table contient cours_id, titre, formateur_id et nom_formateur. Donnez une décomposition possible et les clés principales.

**Corrigé.** FORMATEURS(formateur_id PK, nom_formateur) et COURS(cours_id PK, titre, formateur_id FK). La dépendance formateur_id → nom_formateur est alors conservée dans une seule relation. La table COURS référence un formateur existant, si chaque cours doit obligatoirement avoir un formateur.

### Exercice 8 — Redondance ou historique ?

Une INSCRIPTION conserve le titre du cours tel qu'il apparaissait au moment de l'inscription, même si le titre courant du cours change. Cette duplication est-elle automatiquement une erreur ?

**Corrigé.** Non. Si le titre est un instantané historique avec une règle explicite — par exemple pour restituer exactement le contrat ou la version suivie — il représente un fait temporel distinct du titre courant. La duplication doit être documentée et gérée comme un historique, plutôt que propagée automatiquement. Une copie sans sémantique claire reste fragile.

### Exercice 9 — Relation plusieurs-à-plusieurs

Un apprenant suit plusieurs cours et chaque cours peut accueillir plusieurs apprenants. Pourquoi une colonne cours_id dans APPRENANTS ne suffit-elle pas ?

**Corrigé.** Une seule colonne ne peut référencer qu'un cours à la fois sans liste ou colonnes répétées. Le modèle doit représenter l'association avec une table INSCRIPTIONS contenant apprenant_id et cours_id, plus les attributs du lien. Cela permet plusieurs inscriptions et des contraintes référentielles.

### Exercice 10 — Vérifier une décomposition

Après normalisation, on joint INSCRIPTIONS à APPRENANTS par apprenant_id et à COURS par cours_id. Que vérifiez-vous pour confirmer que la décomposition préserve les associations ?

**Corrigé.** Comparez le résultat avec un jeu source de référence : chaque inscription initialement valide doit retrouver le bon apprenant et le bon cours, sans perdre d'association ni en inventer. Les clés et les références doivent être uniques et cohérentes. La comparaison doit porter sur l'identité et les valeurs attendues, pas seulement sur le nombre total de lignes.

### Exercice 11 — Une table déjà en 1NF est-elle correcte ?

Une table utilise des valeurs atomiques et ne possède pas de colonnes répétées, mais répète le nom d'un département pour chaque employé. Est-elle automatiquement en 3NF ?

**Corrigé.** Non. La 1NF ne garantit ni la 2NF ni la 3NF. Il faut analyser les clés et les dépendances. Si employe_id détermine departement_id et departement_id détermine nom_departement, le nom dépend transitivement de la clé de l'employé. Une table DEPARTEMENT peut être appropriée, et EMPLOYE référence le département.

### Exercice 12 — Reconnaître une dénormalisation

Un rapport mensuel conserve le total pré-calculé des ventes par mois pour accélérer l'affichage. Quels contrôles faut-il prévoir ?

**Corrigé.** Il faut identifier les tables sources faisant autorité, documenter la règle de calcul, le calendrier de rafraîchissement, la gestion des corrections et retours, les erreurs de job et les contrôles comparant le total pré-calculé aux sources. La redondance est volontaire mais impose une stratégie de cohérence et de surveillance.

## 17. Défi final corrigé — normaliser une gestion de formations

### Mission

Une organisation conserve une table unique appelée PARTICIPATION avec les colonnes apprenant_id, nom_apprenant, email_apprenant, cours_id, titre_cours, formateur_id, nom_formateur, date_debut, statut_inscription et score. Le métier confirme les règles suivantes :

- apprenant_id identifie un apprenant, et son nom et son courriel décrivent son compte ;
- cours_id identifie un cours, possède un titre courant et un formateur responsable unique dans cette version ;
- formateur_id identifie un formateur et détermine son nom ;
- un apprenant peut être inscrit à plusieurs cours et un cours peut avoir plusieurs apprenants ;
- date_debut, statut_inscription et score décrivent l'inscription à un cours ;
- un seul enregistrement d'inscription par couple apprenant-cours est autorisé dans la première version ;
- score peut être NULL avant l'évaluation, sinon il est compris entre zéro et cent.

Produisez le raisonnement de normalisation, le modèle logique, un diagramme et des critères de test.

### Étape A — Dépendances fonctionnelles

Les règles impliquent :
- apprenant_id → nom_apprenant, email_apprenant
- cours_id → titre_cours, formateur_id
- formateur_id → nom_formateur
- (apprenant_id, cours_id) → date_debut, statut_inscription, score

La clé candidate de PARTICIPATION est le couple apprenant_id-cours_id, selon l'hypothèse d'unicité. Le nom de l'apprenant et le courriel dépendent d'une partie de la clé, tout comme le titre et formateur_id. La dépendance formateur_id → nom_formateur crée une dépendance transitive à partir de cours_id.

### Étape B — Décomposition et MLD

**APPRENANTS** (\`apprenant_id\` PK, nom_apprenant, email_apprenant UNIQUE)

**FORMATEURS** (\`formateur_id\` PK, nom_formateur)

**COURS** (\`cours_id\` PK, titre_cours, \`formateur_id\` FK)

**INSCRIPTIONS** (\`apprenant_id\` PK/FK, \`cours_id\` PK/FK, date_debut, statut_inscription, score)

~~~mermaid
erDiagram
    APPRENANTS ||--o{ INSCRIPTIONS : "s'inscrit"
    COURS ||--o{ INSCRIPTIONS : "accueille"
    FORMATEURS ||--o{ COURS : "responsable"
    APPRENANTS {
        int apprenant_id PK
        string nom_apprenant
        string email_apprenant UK
    }
    FORMATEURS {
        int formateur_id PK
        string nom_formateur
    }
    COURS {
        int cours_id PK
        string titre_cours
        int formateur_id FK
    }
    INSCRIPTIONS {
        int apprenant_id PK, FK
        int cours_id PK, FK
        date date_debut
        string statut_inscription
        decimal score
    }
~~~

### Étape C — Vérifications de cohérence

Le modèle doit permettre un apprenant sans inscription, un cours sans apprenant et plusieurs inscriptions différentes. Une inscription doit référencer un apprenant et un cours existants. Un même couple apprenant-cours ne doit pas apparaître deux fois. Le score doit être absent ou compris entre zéro et cent. Le nom d'un formateur doit être conservé dans une seule relation courante, et plusieurs cours doivent pouvoir le référencer.

### Étape D — Vérifier les cas historiques

Si le métier permet plus tard à un apprenant de suivre plusieurs sessions du même cours, le couple apprenant-cours ne sera plus une clé suffisante. Il faudra ajouter session_id à INSCRIPTIONS et revoir les clés candidates. Il ne suffit pas de supprimer la contrainte UNIQUE sans décider comment distinguer les inscriptions, les dates, les scores et les tentatives.

Si un cours peut avoir plusieurs formateurs responsables en même temps, cours_id ne déterminera plus un unique formateur_id. Il faudra alors modéliser une association COURS_FORMATEUR, et décider si le rôle du formateur, sa date de début ou sa date de fin sont des attributs du lien.

Le modèle doit évoluer avec les règles métier. La normalisation n'est pas une opération mécanique qui se termine par une formule : c'est une manière de rendre explicites les dépendances et les identifiants. Dès qu'une règle change, les dépendances doivent être revues.

### Étape E — Critères d'acceptation

Le défi est réussi si vous pouvez expliquer chaque dépendance, justifier les quatre tables, indiquer les clés primaires et étrangères, montrer que les associations peuvent être reconstruites et tester les règles d'unicité et de validité. Vous devez également identifier les hypothèses de version : une inscription unique par cours et apprenant, un formateur principal unique par cours et un seul score courant par inscription.

Le but n'est pas de maximiser le nombre de tables. Il est de placer chaque fait à l'endroit où sa dépendance est comprise, afin qu'une mise à jour du nom d'un apprenant ou d'un formateur ne demande pas de modifier de nombreuses lignes sans relation avec le fait lui-même.

## 18. Parcours pratique du débutant

Pour ancrer les notions, travaillez en plusieurs séances.

**Séance 1 — Observer la redondance.** Reprenez la table PARTICIPATION et marquez chaque colonne. À quelle entité ou association appartient-elle ? Entourez les attributs recopiés plusieurs fois. Écrivez un scénario d'anomalie d'insertion, de mise à jour et de suppression.

**Séance 2 — Définir les clés.** Écrivez les clés candidates possibles à partir des règles. Vérifiez les attributs qui dépendent de l'ensemble de la clé et ceux qui dépendent d'un seul composant. Ne vous fiez pas seulement aux valeurs du petit jeu d'essai.

**Séance 3 — Appliquer la 1NF.** Remplacez tout groupe répétitif ou liste de références par une structure relationnelle. Expliquez pourquoi chaque ligne correspond à un fait au bon niveau.

**Séance 4 — Appliquer la 2NF.** Analysez les clés composées et les dépendances partielles. Déplacez les attributs descriptifs vers les tables des entités qu'ils décrivent. Vérifiez que les attributs de l'inscription restent liés à la clé complète de l'inscription.

**Séance 5 — Appliquer la 3NF.** Recherchez les attributs non-clés qui déterminent d'autres attributs non-clés. Dans notre exemple, séparez les formateurs des cours. Testez la règle en changeant un nom de formateur dans les données de laboratoire et vérifiez que le fait courant n'est conservé qu'à un seul endroit.

**Séance 6 — Reconstruire.** Joignez les tables et comparez le résultat au jeu de référence d'origine. Vérifiez chaque association, pas seulement le nombre de lignes. Distinguez la répétition visible dans un rapport de la redondance dans les tables stockées.

**Séance 7 — Documenter.** Écrivez les règles métier, les clés, les dépendances, les hypothèses et les limites. Préparez des tests qui vérifieront les contraintes dans un environnement isolé. Un autre apprenant doit pouvoir reproduire votre raisonnement.

## 19. Checklist de validation

Avant de considérer le modèle comme prêt à être implémenté, vérifiez les points suivants :

- Chaque table représente une entité ou une association clairement définie.
- La granularité de chaque relation est décrite en une phrase.
- Les clés candidates correspondent aux règles métier et ne sont pas supposées uniquement à partir d'un petit échantillon.
- Les dépendances fonctionnelles ont été listées et discutées.
- Les colonnes contenant des listes ou des groupes répétitifs ont été examinées.
- Les dépendances partielles sur une partie d'une clé composée sont traitées.
- Les dépendances transitives inappropriées sont traitées.
- Les clés primaires et étrangères reflètent la structure logique de la décomposition.
- Les associations plusieurs-à-plusieurs sont représentées par une table d'association.
- Les faits historiques éventuellement dupliqués ont une sémantique explicitement documentée.
- Les règles d'unicité correspondent aux sessions, réinscriptions et tentatives réelles.
- La décomposition permet de reconstruire les associations attendues.
- Les contraintes de domaine et les clés sont testées dans le moteur retenu.
- Les données existantes seraient contrôlées avant une migration de structure.
- Toute dénormalisation éventuelle est justifiée, mesurée et accompagnée d'une règle de synchronisation.

## 20. Synthèse finale

La normalisation aide à concevoir des relations cohérentes à partir des clés candidates et des dépendances fonctionnelles. Une dépendance X → Y signifie que X détermine Y dans le domaine considéré. Une clé composée peut révéler des dépendances partielles : certains attributs dépendent d'un seul composant de la clé plutôt que de la combinaison complète. Les dépendances transitives apparaissent lorsqu'un attribut non-clé est déterminé par un autre attribut non-clé.

La 1NF traite la représentation des valeurs et les groupes répétitifs. La 2NF ajoute l'élimination des dépendances partielles des attributs non-clés vis-à-vis des clés candidates. La 3NF traite les dépendances transitives inappropriées. Ces formes normales se comprennent en étudiant les règles du domaine, pas en appliquant une recette aveugle.

Décomposer une table ne doit pas détruire l'information. Les relations résultantes doivent posséder des clés et des références appropriées afin que les associations prévues puissent être reconstruites sans perte. Les contraintes, la validation métier, les tests et la stratégie de migration restent nécessaires. La normalisation ne garantit pas à elle seule sécurité, performance ou conformité ; elle établit une base plus claire pour les construire.

Une redondance peut être conservée volontairement lorsqu'elle représente un fait historique ou une structure dérivée qui répond à un besoin mesuré. Dans ce cas, la source de vérité et le mécanisme de synchronisation doivent être explicites. Le principe général est simple : chaque fait doit être conservé à l'endroit où ses règles de détermination sont comprises, et toute exception doit être justifiée.

## Références techniques

Ces ressources complètent la leçon sur la conception des tables et les contraintes. Les formes normales sont des concepts du modèle relationnel ; les détails d'implémentation dépendent du SGBD choisi.

- PostgreSQL 18, définition des contraintes : https://www.postgresql.org/docs/18/ddl-constraints.html
- PostgreSQL 18, création de tables : https://www.postgresql.org/docs/18/sql-createtable.html
- MySQL 8.4, clés étrangères InnoDB : https://dev.mysql.com/doc/refman/8.4/en/innodb-foreign-key-constraints.html
- SQLite, création des tables et contraintes : https://www.sqlite.org/lang_createtable.html

Consultez les versions correspondant à votre environnement avant d'appliquer un script. Une bonne modélisation se base sur les dépendances réelles et les règles métier, pas sur un dialecte SQL particulier.
