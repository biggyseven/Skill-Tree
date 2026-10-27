# Stratégies de sauvegarde (3-2-1)

> **Mise en contexte**
>
> Une entreprise perd un dossier partagé après une erreur de manipulation. L'équipe affirme qu'une sauvegarde s'exécute toutes les nuits, mais personne n'a testé la restauration depuis plusieurs mois. Une sauvegarde dont on ne peut pas prouver la lisibilité et la restauration ne constitue pas une garantie suffisante. L'objectif est de réduire la perte de données et de remettre un service en fonctionnement dans un délai connu.

## Objectifs du cours

Tu vas apprendre à concevoir une stratégie 3-2-1, fixer un RPO et un RTO, choisir des méthodes de sauvegarde, protéger les copies et organiser des tests de restauration documentés.

## 1. Le principe 3-2-1

La règle classique recommande de conserver **3 copies des données**, sur **2 types de supports** ou domaines de stockage différents, dont **1 copie hors site**. Une copie supplémentaire immuable ou hors ligne et des contrôles d'intégrité renforcent la stratégie ; ils ne remplacent pas les trois principes de base.

~~~mermaid
flowchart TD
    A[Données de production] --> B[Copie locale contrôlée]
    A --> C[Copie sur un second support]
    A --> D[Copie hors site]
    B --> E[Test de restauration]
    C --> E
    D --> E
    E --> F[Preuve et compte rendu]
~~~

Trois répertoires sur le même disque ne sont pas trois copies indépendantes. Un ransomware, un défaut matériel, un compte compromis ou une erreur de suppression peut toucher toutes les copies accessibles depuis le même poste. Une copie hors site doit être protégée par des identifiants séparés, des droits limités et une politique de rétention vérifiable.

## 2. Définir RPO et RTO

- **RPO (Recovery Point Objective)** : quantité de données que l'organisation accepte de perdre, exprimée généralement en durée. Un RPO de quatre heures implique que les points de restauration disponibles ne doivent pas laisser un intervalle de perte supérieur à cet objectif.
- **RTO (Recovery Time Objective)** : durée cible pour remettre le service en fonctionnement après l'incident.
- **Rétention** : durée pendant laquelle on conserve les points de restauration.
- **Point de restauration** : ensemble cohérent de données et, selon le système, des journaux ou métadonnées indispensables à la reprise.

Un objectif n'est pas réaliste sans mesurer la taille des données, le débit disponible, le temps de vérification, les dépendances et les étapes de remise en service. Il faut distinguer les données qui peuvent être reconstruites de celles qui doivent absolument être restaurées.

## 3. Choisir la méthode adaptée

| Méthode | Principe | Avantage | Point d'attention |
|---|---|---|---|
| Complète | Copie le périmètre entier | Restauration plus simple | Durée et stockage plus importants |
| Incrémentale | Copie les changements depuis le dernier point prévu | Rapide et économe | La chaîne des incréments doit rester disponible |
| Différentielle | Copie les changements depuis la dernière complète | Restauration souvent plus simple qu'une longue chaîne incrémentale | Les volumes augmentent avant la prochaine complète |
| Instantané cohérent | Capture un état à un instant donné | Utile pour certaines plateformes | Ne remplace pas automatiquement une copie indépendante |

Un instantané stocké sur le même système n'est pas une sauvegarde indépendante. Pour une base de données ou une application à forte activité, une simple copie de fichiers peut être incohérente. Utilise le mécanisme de sauvegarde natif, une mise en cohérence ou une procédure validée par l'éditeur.

## 4. Planifier, protéger et surveiller

Pour chaque service, note le propriétaire, le périmètre, le RPO, le RTO, la fréquence, la rétention, l'emplacement, le chiffrement, les personnes autorisées et le mode de restauration. Définis également les alertes en cas d'échec, de volume anormal, de copie manquante ou de durée excessive.

Les protections essentielles sont :
- des comptes de sauvegarde distincts des comptes de production ;
- des permissions minimales, avec contrôle des accès administratifs ;
- un chiffrement en transit et au repos lorsque le risque le justifie ;
- une copie hors site et, pour les données critiques, une copie immuable ou hors ligne ;
- une surveillance du résultat, et pas uniquement de la fin d'un processus ;
- une rétention validée par les obligations métier, contractuelles et légales ;
- un accès documenté aux clés de chiffrement, avec procédure de récupération sécurisée.

Les secrets ne doivent pas être écrits dans un script en clair ni enregistrés dans les journaux. La politique de rétention doit tenir compte des besoins de restauration, des données sensibles et des règles applicables.

## 5. Créer une archive et vérifier son contenu

Pour un exemple de laboratoire, on sauvegarde deux fichiers de configuration dans une archive datée. La commande tar doit être exécutée avec les autorisations appropriées :

~~~bash
mkdir -p "$HOME/backup-lab"
tar -czf "$HOME/backup-lab/configuration.tar.gz" -C /etc hostname hosts
tar -tzf "$HOME/backup-lab/configuration.tar.gz"
sha256sum "$HOME/backup-lab/configuration.tar.gz" > "$HOME/backup-lab/configuration.tar.gz.sha256"
sha256sum -c "$HOME/backup-lab/configuration.tar.gz.sha256"
~~~

L'archive contient uniquement les fichiers indiqués. La vérification de la somme de contrôle détecte une altération par rapport à la somme enregistrée ; elle ne prouve pas à elle seule que tous les fichiers nécessaires à l'application ont été sauvegardés. La liste de l'archive permet de vérifier son contenu avant toute restauration.

Pour simuler une copie avec rsync vers un répertoire de laboratoire, commence par un mode à blanc :

~~~bash
rsync -a --dry-run "$HOME/documents-lab/" "$HOME/backup-lab/documents-lab/"
~~~

Si la source et la destination ont été vérifiées, retire --dry-run pour exécuter la copie. Évite l'option --delete dans un exercice : une mauvaise inversion de source et de destination pourrait supprimer des fichiers. Une copie locale n'est qu'une étape du dispositif 3-2-1.

## 6. Exemple de script de sauvegarde de laboratoire

Ce script produit une archive, vérifie que l'archive peut être listée, puis calcule son empreinte. Modifie les chemins uniquement pour un dossier de test que tu es autorisé à sauvegarder.

~~~bash
#!/usr/bin/env bash
set -Eeuo pipefail

SRC="/srv/donnees-lab"
DEST="/var/backups/donnees-lab"
STAMP="$(date +%Y%m%d-%H%M%S)"

if [ ! -d "$SRC" ]; then
  printf 'Source absente : %s\n' "$SRC" >&2
  exit 1
fi

mkdir -p "$DEST"
ARCHIVE="$DEST/donnees-$STAMP.tar.gz"
tar -czf "$ARCHIVE" -C "$(dirname "$SRC")" "$(basename "$SRC")"
tar -tzf "$ARCHIVE" >/dev/null
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"
printf 'Archive créée et lisible : %s\n' "$ARCHIVE"
~~~

Le script ne chiffre pas l'archive, n'envoie pas de copie hors site et ne supprime rien. Avant un usage réel, il faut ajouter une gestion des secrets, un stockage de destination approprié, la supervision du résultat, la politique de rétention et des tests de restauration. Une exécution sans erreur ne remplace pas ces vérifications.

## 7. Restaurer et prouver la reprise

Une restauration doit être préparée comme une opération contrôlée :

1. Choisir le point correspondant à l'heure nécessaire.
2. Vérifier la présence de toutes les parties de sauvegarde et les sommes de contrôle disponibles.
3. Restaurer d'abord dans un emplacement de test isolé.
4. Vérifier les permissions, propriétaires, dates et cohérence des données.
5. Tester l'ouverture du fichier ou le démarrage de l'application de manière adaptée.
6. Mesurer la durée et comparer le résultat au RTO.
7. Documenter les écarts, puis seulement préparer une bascule réelle si elle est autorisée.

Extraire une archive de test dans un répertoire séparé :

~~~bash
mkdir -p "$HOME/restore-test"
tar -xzf "$HOME/backup-lab/configuration.tar.gz" -C "$HOME/restore-test"
find "$HOME/restore-test" -maxdepth 2 -type f -print
~~~

Ne restaure pas directement sur le système de production sans valider le périmètre, les permissions, les impacts et le plan de retour arrière.

## Mise en pratique

### Laboratoire : tester une sauvegarde vérifiable

1. Crée un dossier avec deux fichiers non sensibles dans $HOME/backup-lab/source.
2. Archive ce dossier avec une date explicite dans le nom.
3. Liste le contenu de l'archive.
4. Crée et vérifie une somme de contrôle.
5. Restaure l'archive dans un second répertoire vide.
6. Compare les fichiers restaurés avec les originaux.
7. Complète une fiche de test : heure de début, heure de fin, point restauré, fichiers attendus, fichiers retrouvés, erreur éventuelle et durée.

**Critère de réussite :** le test est réussi uniquement si les fichiers attendus sont présents et lisibles dans l'emplacement de test. L'existence du fichier archive ne suffit pas.

## Exercices corrigés

**1. Trois sauvegardes sont conservées dans trois dossiers du même disque. La règle 3-2-1 est-elle satisfaite ?**

Correction : non. Les copies partagent un même domaine de défaillance et il n'y a pas de copie hors site démontrée. Il faut des copies indépendantes sur des supports ou domaines différents, dont une hors site.

**2. Quelle différence entre RPO et RTO ?**

Correction : le RPO porte sur la perte de données acceptable ; le RTO porte sur la durée cible pour rétablir le service. Une sauvegarde fréquente aide le RPO mais ne garantit pas une restauration rapide.

**3. Une tâche de sauvegarde termine avec le code de succès, mais personne ne restaure jamais les données. Quel risque reste-t-il ?**

Correction : l'archive peut être incomplète, incohérente, illisible ou inutilisable faute de clés, de dépendances ou de procédure. Une restauration périodique et documentée est nécessaire.

**4. Pourquoi utiliser un compte et des droits spécifiques pour les sauvegardes ?**

Correction : limiter l'impact d'un compte de production compromis et réduire les possibilités de modifier ou détruire toutes les copies depuis le même contexte d'accès.

## Défi final corrigé

Le partage de fichiers a un RPO de quatre heures et un RTO de deux heures. La sauvegarde quotidienne est conservée uniquement sur le serveur de production. Propose un plan d'amélioration.

**Correction attendue :** mettre en place des points de sauvegarde dont la fréquence et la réussite démontrent le RPO de quatre heures ; conserver au moins une copie indépendante hors site et protéger les copies contre la suppression ; définir la rétention, le chiffrement et les droits d'accès ; alerter sur les échecs et les volumes inattendus ; documenter les étapes de restauration ; enfin, réaliser un test chronométré dans un environnement isolé. Si la restauration dépasse deux heures, il faut revoir la méthode, le débit, la capacité ou les objectifs avec le responsable métier plutôt que prétendre que le RTO est respecté.


## 8. Modéliser les dépendances d'une reprise

Une liste de fichiers ne suffit pas à représenter un service. Une application peut dépendre d'une base, de l'annuaire, du DNS, d'un certificat, de paramètres de connexion, d'un partage, d'une clé de chiffrement et d'un service externe. Si ces éléments sont récupérés à des dates incompatibles, le service peut démarrer sans produire de données cohérentes. La stratégie doit donc décrire les dépendances et l'ordre de rétablissement.

~~~mermaid
flowchart TD
    A[Plateforme restaurée] --> B[Identité et DNS]
    B --> C[Base de données cohérente]
    C --> D[Fichiers et pièces jointes]
    D --> E[Configuration et certificats]
    E --> F[Application]
    F --> G[Test métier et autorisation de reprise]
~~~

Cette séquence est illustrative : l'ordre réel dépend du produit et de l'architecture. Certains services exigent que l'identité et le réseau soient disponibles avant tout accès ; d'autres peuvent restaurer les données dans un environnement isolé sans contacter la production. La procédure doit indiquer les dépendances en amont, les versions compatibles, l'ordre de restauration, les comptes autorisés et le test final.

Le plan de reprise doit aussi distinguer les données indispensables à la remise en service de celles qui peuvent être reconstituées ensuite. Pour un portail, il peut être prioritaire de rétablir les transactions et l'authentification avant des rapports anciens. Cette priorisation doit être acceptée par le propriétaire métier. Elle évite de consommer tout le temps disponible à restaurer des données secondaires pendant que les fonctions essentielles demeurent indisponibles.

Un runbook de reprise doit comporter un déclencheur, un décideur, une liste d'actifs concernés, un lieu sûr de restauration, les accès d'urgence, les étapes de validation, le plan de communication, le point où l'on décide de revenir à la production et une procédure d'échec. Un document qui ne peut être trouvé en cas d'incident, ou qui exige un accès au serveur perdu pour être consulté, n'est pas une procédure de reprise suffisante. Conserve une copie contrôlée du runbook dans un espace disponible indépendamment du système qui doit être restauré.

## 9. Cohérence applicative et choix du point de restauration

Les fichiers ouverts, les transactions de base de données et les applications en mémoire peuvent changer pendant une copie. Un cliché obtenu sans coordination peut représenter un état où certains fichiers sont anciens et d'autres déjà mis à jour. Le degré de cohérence requis dépend du système : une archive de documents peut tolérer une différence de quelques secondes entre fichiers ; une base transactionnelle exige souvent un mécanisme pris en charge par son moteur.

Pour les bases de données, utilise les outils et méthodes recommandés par l'éditeur. Vérifie si le mode de sauvegarde exige des journaux, une phase de préparation, un checkpoint, un verrouillage ou une coordination entre composants. Ne lance pas une copie brute du répertoire de données d'une base active en supposant qu'elle est forcément exploitable. Si le produit permet la restauration à un instant précis, teste aussi la disponibilité et la continuité des journaux nécessaires.

La sélection du point doit prendre en compte l'heure de l'incident, l'heure de la dernière transaction confirmée, les copies disponibles, les rétentions, la présence éventuelle d'une corruption antérieure et le risque que l'attaquant ait déjà compromis le point de sauvegarde. Lors d'un incident de sécurité, le point le plus récent n'est pas toujours le plus sûr. L'équipe de réponse doit aider à sélectionner un point propre avant la réintégration dans le réseau.

~~~mermaid
flowchart TD
    A[Incident détecté] --> B[Estimer heure de début et périmètre]
    B --> C[Identifier points récupérables]
    C --> D[Évaluer cohérence et intégrité]
    D --> E{Point acceptable ?}
    E -->|Non| F[Examiner une génération antérieure]
    E -->|Oui| G[Restaurer isolément]
    F --> D
    G --> H[Validation technique et métier]
~~~

Une restauration doit respecter les autorisations. Restaurer une ancienne version d'un dossier partagé peut écraser des modifications utiles faites après cette version. Préfère un emplacement temporaire lorsque c'est possible, compare le contenu et fais valider le remplacement par le propriétaire. Avant une restauration de base, assure-toi que l'application est arrêtée ou placée dans l'état prévu par le guide du fournisseur.

## 10. Garantir l'indépendance et la sécurité des copies

La séparation des copies couvre plusieurs dimensions. La séparation physique protège contre un incendie ou une perte du local. La séparation logique limite la possibilité pour un attaquant d'accéder à toutes les copies avec une seule identité. L'immuabilité protège pendant une durée définie contre des modifications ou suppressions. L'accès hors ligne réduit l'exposition au réseau, mais demande une procédure opérationnelle de connexion, de contrôle et de retrait.

Un dépôt objet, une cible dédiée ou un média amovible peuvent répondre à différents besoins, mais aucun choix ne doit être considéré comme sûr par son seul nom. Vérifie les droits de suppression, les identités de service, les possibilités de raccourcir la rétention, les journaux d'administration, les méthodes de chiffrement, les règles de verrouillage et le mécanisme de récupération des clés. Fais valider ces points par l'équipe responsable de la sécurité.

Les comptes de sauvegarde doivent être séparés des comptes d'administration générale lorsque l'architecture le permet. Les droits de copie, de consultation, de restauration et de suppression peuvent être différents. Un opérateur qui doit restaurer un fichier ne devrait pas nécessairement pouvoir supprimer des mois de points. Les opérations privilégiées doivent être journalisées et revues.

Ne place pas un fichier contenant des mots de passe, des clés privées, des jetons d'API ou des codes de récupération dans un partage accessible à toute l'équipe. Le plan doit expliquer où se trouvent les secrets, qui peut les utiliser, comment une personne autorisée peut les obtenir pendant une crise et comment leur usage sera audité. La clé de chiffrement ne doit pas dépendre uniquement de l'environnement qui a été perdu.

L'intégrité se vérifie à différents moments : après transfert, au dépôt, pendant les tests et après restauration. Une somme de contrôle peut détecter des altérations d'un fichier, mais ne prouve pas qu'une application complète fonctionnera. Combine la vérification technique avec un contrôle de structure, de cohérence et de fonction. Les journaux du système de sauvegarde doivent être protégés suffisamment pour que le rapport d'une restauration puisse être considéré comme fiable.

## 11. Plan de tests et couverture

Une stratégie de test doit couvrir plusieurs niveaux, pas seulement l'extraction d'un fichier. Les tests unitaires peuvent vérifier qu'un document ou une configuration est restaurable. Les tests applicatifs vérifient des fonctions importantes sur un environnement représentatif. Les exercices de reprise mesurent le temps pour rétablir un service et coordonner les équipes. Une simulation de perte du site teste aussi les procédures d'accès et les dépendances externes.

~~~mermaid
flowchart LR
    A[Test d'un fichier] --> B[Test d'un jeu de données]
    B --> C[Test applicatif isolé]
    C --> D[Exercice de reprise]
    D --> E[Écart RPO/RTO]
    E --> F[Plan d'amélioration et nouveau test]
~~~

La fréquence des tests dépend de la criticité et du changement. Une modification de format, de version, de clés, de dépôt ou de procédure peut invalider un ancien résultat. Les systèmes les plus critiques exigent une preuve récente et suffisamment complète. Si un test n'a pas pu être effectué, il faut le rapporter comme non réalisé, préciser la raison, le risque et la date prévue. Ne remplace pas un test manquant par une case cochée « OK ».

Le protocole de test doit préciser le scénario, la source, le point sélectionné, la destination, les responsables, les critères de réussite, les données de test, la durée et l'arrêt d'urgence. Il doit préciser comment éviter que l'environnement restauré envoie des courriels réels, traite des paiements, déclenche des automations ou écrase la production. Un environnement isolé et des comptes limités réduisent les risques.

Après le test, note le temps écoulé par étape : sélection du point, préparation, transfert, restauration, démarrage, validation et décision métier. Le résultat total explique l'écart au RTO. Un test rapide qui omet la validation métier ne mesure pas le rétablissement complet du service. Les tests doivent être reproductibles, mais ils ne doivent pas laisser des données d'essai exposées après leur fin.

## 12. Interpréter les erreurs et éviter les reprises dangereuses

Un job qui échoue peut indiquer une source inaccessible, un espace insuffisant, un accès expiré, un verrou de fichier, une erreur de catalogue, un problème de réseau ou une altération de donnée. Le premier réflexe n'est pas toujours de relancer immédiatement. Si l'erreur est systématique, la répétition peut saturer la cible et retarder la résolution. Si une tâche complète réécrit un dépôt, il faut connaître son impact sur les autres points avant de recommencer.

Conserve le code d'erreur, les heures, l'objet affecté, la version du logiciel, la quantité traitée, les exclusions, la dernière copie valide et les changements récents. Si l'échec est partiel, identifie les fichiers ou objets manquants. Un rapport qui dit « 98 % terminé » peut signifier que les 2 % restants sont précisément les données critiques ; la couverture doit être vérifiée par le périmètre, pas seulement par un pourcentage.

Si les copies sont chiffrées ou si un accès anormal est détecté, préserve les traces selon la procédure de sécurité. Ne détruis pas un dépôt qui peut contenir des preuves. Ne connecte pas immédiatement une copie hors ligne à un système suspect sans avoir évalué le risque. En cas de doute, implique l'équipe responsable de la réponse à incident.

## 13. Laboratoire de conception — feuille de calcul et test de restauration

Prépare une matrice comportant une ligne par service. Les colonnes doivent comprendre : propriétaire, données, criticité, RPO, RTO, méthode, fréquence, rétention, copie hors site, protection contre suppression, clé, dernière exécution, dernier point vérifié, dernier test, résultat, durée mesurée, écart et action suivante. Les valeurs d'exemple doivent être signalées comme telles. La matrice est un outil de décision, pas une preuve en soi.

Travail demandé :

1. choisir deux services de criticité différente ;
2. demander ou proposer des RPO/RTO puis marquer explicitement les valeurs à faire valider ;
3. décrire deux domaines de panne et vérifier l'indépendance des copies ;
4. définir les événements qui doivent produire une alerte ;
5. prévoir une restauration d'un fichier non sensible et un test applicatif isolé ;
6. enregistrer les preuves et les limites ;
7. rédiger trois actions correctives triées par risque.

Correction attendue : la matrice doit distinguer le dernier job du dernier point récupérable. Le RPO détermine la fraîcheur nécessaire ; le RTO demande une mesure du processus complet. Les copies doivent survivre au scénario qui les menace, et la stratégie doit comporter une récupération des clés et de la configuration. Les résultats sont documentés avec le point, la date, le périmètre et le critère validé. Toute valeur non confirmée par le propriétaire reste une proposition.

## 14. Exercices avancés avec corrections

### Exercice 9 — Dépôt distant dans le même domaine de compte

**Énoncé :** une copie hors site est stockée dans le cloud, mais le compte de production peut supprimer toutes les générations.

**Correction :** la distance ne garantit pas l'indépendance. Il faut examiner les rôles, l'immutabilité, le verrouillage de rétention, les journaux et les comptes de récupération. Le risque doit être traité avec une séparation d'identités ou une protection approuvée.

### Exercice 10 — Restauration de sauvegarde incomplète

**Énoncé :** tous les fichiers sont présents mais l'application ne démarre pas car une configuration et un certificat manquent.

**Correction :** le périmètre de sauvegarde était incomplet ou les dépendances n'étaient pas documentées. Ajouter ces éléments à la stratégie après identification de leur sensibilité, tester une restauration complète et vérifier l'accès aux secrets avec le processus autorisé.

### Exercice 11 — Point le plus récent corrompu

**Énoncé :** le dernier point date de dix minutes, mais l'application contenait déjà une corruption introduite depuis la veille.

**Correction :** le point le plus récent ne convient pas automatiquement. Sélectionner un point antérieur propre selon l'analyse, estimer la perte de données possible, obtenir les validations et documenter la décision. Renforcer la détection des corruptions et la conservation de générations plus anciennes.

### Exercice 12 — Copie de serveur virtuel

**Énoncé :** le serveur virtuel est sauvegardé par snapshot, mais aucun test de lancement n'a été fait.

**Correction :** la présence d'un snapshot ne prouve pas que l'environnement se lancera sur un autre hôte ou que ses dépendances seront disponibles. Tester le démarrage isolé, les réseaux, les disques, les identités, l'application et la durée de remise en service selon le périmètre convenu.

### Exercice 13 — Clé de déchiffrement accessible uniquement depuis le serveur perdu

**Énoncé :** la procédure suppose que le serveur de gestion des secrets soit disponible, mais il a disparu avec le site.

**Correction :** le plan de secours possède une dépendance circulaire. Prévoir un moyen de récupération autorisé des clés, stocké et contrôlé indépendamment, et tester le processus sans exposer les secrets aux opérateurs non autorisés.

### Exercice 14 — Test planifié annulé trois fois

**Énoncé :** le test de restauration est annulé pour manque de temps depuis trois trimestres.

**Correction :** le risque n'est pas supprimé par le report. Enregistre le test comme non réalisé, informe le propriétaire, propose une durée et un environnement adaptés, puis fais décider le niveau d'acceptation du risque. Le reporting doit exposer le retard et sa conséquence.

## 15. Défi final complémentaire — Plan de reprise mesuré

Complète le défi final précédent en écrivant une procédure qui permet à une équipe différente de réaliser l'exercice. Ajoute une chronologie réaliste, les rôles, les points de décision, les critères de succès, la méthode de preuve, la protection des secrets et la manière de redémarrer les tâches de sauvegarde après reprise.

Correction : le document doit pouvoir être lu depuis un emplacement indépendant de l'infrastructure perdue. Il doit indiquer ce qui déclenche le plan, qui l'autorise, qui communique avec les utilisateurs, qui restaure les données, qui vérifie l'application et qui accepte le retour en service. Une fois la reprise réalisée, l'équipe doit vérifier que les sauvegardes régulières reprennent et créer un nouveau point valide. La restauration d'un point ancien ne protège pas les nouvelles transactions produites après la reprise ; le processus de sauvegarde doit revenir à son rythme conforme.

Le rapport doit distinguer la réussite technique et l'acceptation métier. Les conclusions incluent les temps mesurés, la quantité de données restaurées, le point temporel, les écarts, les limites et les actions. Si le RTO a été dépassé, le test reste utile : il révèle l'amélioration nécessaire. Il serait incorrect de modifier le RTO uniquement pour faire disparaître l'écart sans validation métier.
