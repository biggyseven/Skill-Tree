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
