# Sauvegarde et restauration

## Niveau débutant

## 1. Présentation générale du cours

Les données représentent souvent l'un des éléments les plus importants d'un système informatique. Il peut s'agir de documents, de bases de données, de fichiers applicatifs, de configurations de serveurs, de machines virtuelles ou encore de données métier.

Une panne matérielle, une erreur de manipulation, une suppression accidentelle, un logiciel malveillant, une corruption de données ou un sinistre physique peuvent rendre ces informations inutilisables.

La sauvegarde permet de conserver des copies récupérables des données afin de pouvoir les restaurer après un incident.

Cependant, posséder une copie ne suffit pas. Une sauvegarde doit être correctement réalisée, protégée, conservée et testée. Il faut également savoir restaurer les données dans un délai compatible avec les besoins du service.

Ce cours présente les principes essentiels de la sauvegarde et de la restauration, puis met en pratique plusieurs outils sous Linux et Windows.

Nous utiliserons notamment :

- `tar` pour créer et extraire des archives.
- `rsync` pour copier des fichiers et des répertoires.
- Restic pour réaliser des sauvegardes versionnées et chiffrées.
- `sha256sum` pour vérifier l'intégrité de fichiers.
- `wbadmin` et les outils Windows pour sauvegarder et restaurer des données.
- Des scripts simples pour automatiser une sauvegarde.
- Des procédures de test pour vérifier que les données peuvent être récupérées.

Les exemples utilisent un environnement de laboratoire. Les chemins, comptes et noms de machines devront être adaptés avant toute utilisation sur un système réel.

## 2. Objectifs pédagogiques

À la fin de ce cours, l'apprenant doit être capable de :

1. Expliquer pourquoi une sauvegarde est nécessaire.
2. Distinguer une sauvegarde d'une simple copie ou synchronisation.
3. Comprendre les sauvegardes complètes, incrémentales et différentielles.
4. Comprendre les principes de conservation et de rétention.
5. Définir les notions de RPO et de RTO.
6. Appliquer la règle de sauvegarde 3-2-1.
7. Créer une archive sous Linux avec `tar`.
8. Copier des données avec `rsync`.
9. Créer un dépôt Restic et réaliser une sauvegarde chiffrée.
10. Consulter les versions disponibles et restaurer des fichiers.
11. Vérifier l'intégrité des sauvegardes.
12. Comprendre les possibilités de sauvegarde et de récupération sous Windows.
13. Automatiser une sauvegarde à l'aide d'un script simple.
14. Protéger les sauvegardes contre les accès non autorisés et les rançongiciels.
15. Tester une restauration sans écraser les données originales.
16. Documenter une procédure de sauvegarde et de reprise.

## 3. Les risques de perte de données

Une perte de données peut survenir de plusieurs manières.

| Risque | Exemple | Protection adaptée |
|---|---|---|
| Erreur humaine | Suppression d'un dossier important | Sauvegarde versionnée |
| Panne de disque | Disque devenu illisible | Copie indépendante sur un autre support |
| Corruption | Fichier ou base de données endommagé | Version antérieure et restauration testée |
| Rançongiciel | Fichiers chiffrés par un logiciel malveillant | Copie isolée, immuable ou hors ligne |
| Vol de matériel | Serveur ou ordinateur volé | Copie hors site et chiffrement |
| Incendie ou dégât des eaux | Destruction du local informatique | Sauvegarde dans un autre emplacement |
| Erreur logicielle | Une application efface ou modifie des données | Historique de sauvegardes |
| Mauvaise mise à jour | Fichiers inutilisables après une migration | Copie préalable et procédure de retour arrière |
| Compromission d'un compte privilégié | Suppression des données et des sauvegardes accessibles | Identités séparées et protection des dépôts |
| Erreur de configuration | Suppression d'un volume ou d'un répertoire | Sauvegarde de configuration et des données |

Une bonne stratégie ne doit pas dépendre d'un unique type de protection.

Par exemple, un RAID peut améliorer la disponibilité des données après certaines pannes de disques, mais il ne remplace pas une sauvegarde. Si un fichier est supprimé ou chiffré par un rançongiciel, la suppression ou la corruption peut se retrouver sur l'ensemble des membres du RAID.

## 4. Qu'est-ce qu'une sauvegarde ?

Une sauvegarde est une copie de données conservée dans le but de permettre leur récupération ultérieure.

Prenons l'exemple d'un dossier contenant des documents importants.

```text
DOSSIER ORIGINAL
/home/administrateur/documents
                |
                v
       OPERATION DE SAUVEGARDE
                |
                v
COPIE DE SAUVEGARDE
/mnt/backup/documents
                |
                v
        INCIDENT EVENTUEL
                |
                v
          RESTAURATION
                |
                v
COPIE RECUPEREE DANS UN DOSSIER DE TEST
/tmp/restore/documents
```

La copie de sauvegarde doit pouvoir être retrouvée même si le dossier original a été supprimé ou endommagé.

Pour cela, la sauvegarde devrait être placée sur un support ou un système distinct, avec des autorisations et un cycle de vie adaptés.

### 4.1 Les opérations de sauvegarde et de restauration

La sauvegarde consiste à créer une copie à partir des données sources.

La restauration consiste à récupérer cette copie pour retrouver les données.

Ces deux opérations doivent être conçues ensemble.

Une sauvegarde qui ne peut pas être restaurée à cause d'un mot de passe perdu, d'une archive corrompue ou d'une dépendance manquante ne remplit pas son objectif.

### 4.2 Ce qu'une sauvegarde doit permettre

Une solution de sauvegarde doit généralement répondre aux questions suivantes :

- Quelles données sont protégées ?
- À quel moment la copie est-elle réalisée ?
- Où est-elle conservée ?
- Qui peut la consulter ?
- Qui peut la supprimer ?
- Combien de temps doit-elle être conservée ?
- Comment vérifier son intégrité ?
- Comment restaurer les données ?
- Combien de temps faut-il pour les récupérer ?
- Quelle perte de données est acceptable ?

Il faut documenter les réponses avant de choisir un outil.

## 5. Sauvegarde, synchronisation, réplication et snapshot

Ces mécanismes sont complémentaires, mais ne sont pas équivalents.

### 5.1 La copie simple

Une copie reproduit des fichiers à un autre emplacement.

Exemple :

```bash
cp -a documents /mnt/backup/
```

Cette commande copie le répertoire dans la destination indiquée, sous réserve des permissions et de l'espace disponible.

Elle ne gère pas nécessairement l'historique des versions, la rétention ou les contrôles réguliers d'intégrité d'un système de sauvegarde dédié.

### 5.2 La synchronisation

Une synchronisation rapproche le contenu de deux emplacements.

Exemple :

```bash
rsync -a /home/alice/Documents/ /mnt/backup/Documents/
```

Cette commande copie les fichiers et répertoires nécessaires pour rapprocher la destination de la source selon le comportement de `rsync`.

Mais si un fichier important a été modifié par erreur, la version modifiée peut aussi être synchronisée.

La synchronisation ne fournit donc pas automatiquement un historique des versions.

### 5.3 La réplication

La réplication maintient des copies de données sur plusieurs systèmes.

Elle sert notamment à la disponibilité et à la continuité de service.

Cependant, si une modification incorrecte est répliquée, elle peut affecter les copies répliquées elles aussi.

### 5.4 Le snapshot

Un snapshot représente un état d'un volume, d'un système de fichiers ou d'une machine virtuelle à un moment donné, selon le mécanisme employé.

Il facilite notamment certaines opérations de retour à un état antérieur.

Mais un snapshot conservé sur le même système de stockage peut disparaître lors d'une panne complète du support. Il peut également être supprimé par un compte compromis disposant des permissions nécessaires.

Un snapshot ne doit donc pas être considéré automatiquement comme une sauvegarde indépendante.

### 5.5 Comparaison

| Mécanisme | Objectif principal | Limite importante |
|---|---|---|
| Copie | Dupliquer des données | Pas nécessairement d'historique |
| Synchronisation | Aligner deux emplacements | Peut propager les modifications indésirables |
| Réplication | Disponibilité et duplication continue | Peut propager une suppression ou une corruption |
| Snapshot | Capturer un état | Peut partager les mêmes risques que le système source |
| Sauvegarde versionnée | Conserver des états récupérables | Nécessite stockage, rétention et tests |

Le choix dépend du risque à couvrir. Un service important peut utiliser simultanément snapshots, réplication et sauvegardes versionnées.

## 6. Les types de sauvegardes

### 6.1 Sauvegarde complète

Une sauvegarde complète copie l'ensemble des données sélectionnées selon le périmètre défini.

Exemple :

```text
LUNDI
  Données sélectionnées : 100 Go
  Sauvegarde : 100 Go

MARDI
  Données sélectionnées : 100 Go
  Sauvegarde : 100 Go

MERCREDI
  Données sélectionnées : 100 Go
  Sauvegarde : 100 Go
```

Dans cet exemple, chaque opération copie à nouveau la totalité des données sélectionnées. Ce schéma ne représente pas le comportement de tous les outils de sauvegarde.

Avantages :

- Compréhension simple.
- Ensemble de données complet dans chaque copie.
- Restauration généralement plus directe.

Inconvénients :

- Durée potentiellement importante.
- Volume de données élevé.
- Bande passante et stockage nécessaires.

### 6.2 Sauvegarde incrémentale

Une sauvegarde incrémentale conserve les données modifiées depuis le point de référence prévu par la méthode utilisée, souvent depuis la sauvegarde précédente.

Exemple :

```text
DIMANCHE
  Sauvegarde complète : 100 Go

LUNDI
  Modifications : 5 Go

MARDI
  Modifications : 3 Go

MERCREDI
  Modifications : 7 Go
```

Dans un modèle incrémental classique, la restauration de mercredi peut nécessiter la sauvegarde complète ainsi que les incréments nécessaires jusqu'à mercredi.

Avantages :

- Volume de données transférées souvent réduit.
- Sauvegardes fréquentes possibles.
- Temps de copie inférieur si peu de données changent.

Inconvénients :

- Le plan de restauration dépend de plusieurs éléments.
- La perte ou la corruption d'un maillon peut compliquer la récupération, selon le format et le logiciel.
- La gestion et les vérifications demandent une attention particulière.

Certains logiciels utilisent des chaînes incrémentales, d'autres s'appuient sur des blocs dédupliqués ou des snapshots logiques. Il faut comprendre leur fonctionnement réel.

### 6.3 Sauvegarde différentielle

Dans un modèle différentiel classique, la sauvegarde contient les modifications depuis la dernière sauvegarde complète.

Exemple :

```text
DIMANCHE
  Sauvegarde complète : 100 Go

LUNDI
  Modifications depuis dimanche : 5 Go

MARDI
  Modifications depuis dimanche : 8 Go

MERCREDI
  Modifications depuis dimanche : 12 Go
```

Pour restaurer mercredi, il faut en principe la sauvegarde complète et la différentielle de mercredi.

Avantages :

- Restauration souvent plus simple qu'une longue chaîne incrémentale classique.
- Chaque différentielle dépend de la complète de référence.

Inconvénient :

- La taille des différentielles peut augmenter au fil du temps.

### 6.4 Comparaison des méthodes classiques

| Critère | Complète | Incrémentale | Différentielle |
|---|---|---|---|
| Volume à chaque opération | Élevé | Souvent faible | Variable |
| Durée de sauvegarde | Souvent élevée | Souvent faible | Croissante selon les changements |
| Éléments nécessaires à la restauration | Copie complète | Complète et incréments nécessaires dans le modèle classique | Complète et différentielle choisie |
| Complexité opérationnelle | Faible à moyenne | Dépend du logiciel | Faible à moyenne |
| Usage courant | Point de référence | Sauvegardes fréquentes | Compromis entre temps et volume |

Les outils modernes peuvent utiliser de la déduplication, des sauvegardes synthétiques et des architectures spécifiques qui ne correspondent pas exactement aux schémas simplifiés ci-dessus.

## 7. Définir les objectifs de sauvegarde

### 7.1 Le RPO

Le RPO, ou *Recovery Point Objective*, désigne la perte maximale de données acceptable, exprimée en temps.

Exemple :

```text
Dernière sauvegarde valide : 02 h 00
Incident :                  10 h 00
RPO cible :                 4 heures
```

Si aucune donnée n'est récupérable après la sauvegarde de 02 h 00, il est possible de perdre jusqu'à huit heures de modifications.

La politique ne satisfait donc pas nécessairement un RPO de quatre heures.

### 7.2 Le RTO

Le RTO, ou *Recovery Time Objective*, désigne le délai cible de rétablissement du service après une interruption.

Exemple :

```text
Début de l'incident : 10 h 00
Service rétabli :     11 h 30

Durée de reprise :    1 h 30
```

Si le RTO cible est de deux heures, ce scénario respecte l'objectif en durée, sous réserve de la méthode contractuelle de mesure.

### 7.3 Différence entre RPO et RTO

```text
DERNIER POINT RECUPERABLE           RETABLISSEMENT
          |                                |
          v                                v
----------+--------------------------------+-------->
       Données pouvant être perdues       Service rétabli

     <--- Perte de données potentielle --->
                                      <--->
                                  Temps de reprise
```

Le RPO mesure la perte de données acceptable.

Le RTO mesure la durée cible pour remettre le service en fonctionnement.

Une organisation peut accepter de perdre peu de données mais tolérer plusieurs heures de reprise, ou imposer un rétablissement très rapide avec une stratégie de protection plus coûteuse.

### 7.4 Exemple de politique

| Type de service | RPO illustratif | RTO illustratif |
|---|---|---|
| Documents internes standards | 24 heures | 8 heures |
| Application métier importante | 4 heures | 2 heures |
| Base transactionnelle critique | 15 minutes ou moins selon l'architecture | 1 heure |
| Environnement de test reconstructible | 24 heures ou davantage | 24 heures |

Ces valeurs sont des exemples pédagogiques. Les exigences doivent être définies avec les propriétaires métier et validées techniquement.

Une sauvegarde quotidienne ne garantit pas un RPO de quinze minutes. Il peut falloir des sauvegardes plus fréquentes, des journaux transactionnels ou d'autres mécanismes complémentaires.

## 8. La règle 3-2-1 et les protections supplémentaires

### 8.1 La règle 3-2-1

La règle 3-2-1 recommande généralement :

- Trois copies des données en comptant les données de production.
- Deux types de supports ou environnements de stockage distincts.
- Une copie conservée hors site.

Exemple :

```text
COPIE 1 : DONNEES DE PRODUCTION
                 |
                 v
COPIE 2 : DEPOT DE SAUVEGARDE LOCAL
                 |
                 v
COPIE 3 : SAUVEGARDE HORS SITE
```

Cette approche réduit le risque de perdre toutes les copies à cause d'un incident unique.

La règle doit être adaptée à la nature des données, au coût, au volume et au niveau de service attendu.

### 8.2 Ajouter l'isolation ou l'immutabilité

Une copie hors site n'est pas nécessairement protégée contre une suppression malveillante si les mêmes identifiants administratifs contrôlent les deux environnements.

Il peut être utile d'ajouter :

- Une copie hors ligne.
- Une copie immuable.
- Des identités séparées.
- Des droits de suppression limités.
- Un chiffrement.
- Une rétention protégée.
- Des vérifications régulières.
- Des restaurations périodiques.

On résume parfois ces principes par 3-2-1-1-0 : une copie supplémentaire est isolée ou immuable, et les restaurations sont vérifiées de manière à réduire le nombre d'erreurs non détectées.

Cette formule constitue un aide-mémoire de bonnes pratiques, pas une garantie mathématique de sécurité.

### 8.3 Schéma d'une stratégie renforcée

```text
             DONNEES DE PRODUCTION
                      |
                      v
              DEPOT DE SAUVEGARDE
               local et contrôlé
                      |
            +---------+---------+
            |                   |
            v                   v
      COPIE HORS SITE      COPIE ISOLEE
      accès restreint      ou immuable
            |                   |
            +---------+---------+
                      |
                      v
               TEST DE RESTAURATION
                      |
                      v
             VALIDATION DES DONNEES
```

L'isolement doit être réel. Si un attaquant peut utiliser un compte compromis pour détruire toutes les copies, la séparation n'est pas suffisante.

## 9. Choisir le bon périmètre de sauvegarde

Avant de sauvegarder, il faut savoir ce qui doit être protégé.

### 9.1 Données utilisateur

Exemples :

- Documents.
- Images.
- Fichiers de travail.
- Répertoires partagés.
- Fichiers personnels autorisés par la politique.

### 9.2 Configuration système

Exemples :

- Fichiers de configuration.
- Paramètres réseau.
- Configuration des services.
- Scripts d'automatisation.
- Liste des paquets.
- Paramètres de pare-feu.

Une sauvegarde de fichiers ne suffit pas toujours à reconstruire complètement un serveur. Il faut parfois conserver la documentation, les versions, les dépendances et les procédures d'installation.

### 9.3 Bases de données

Une base de données active peut être modifiée pendant la sauvegarde.

Copier simplement les fichiers d'une base en fonctionnement ne garantit pas toujours une sauvegarde cohérente.

Il faut utiliser une méthode adaptée au moteur :

- Export logique.
- Sauvegarde physique cohérente.
- Snapshot coordonné.
- Sauvegarde intégrée au moteur.
- Journaux transactionnels si nécessaire.

### 9.4 Machines virtuelles

Une sauvegarde de VM peut inclure le disque virtuel, la configuration et d'autres éléments selon l'outil.

Il faut vérifier si la sauvegarde est cohérente avec l'application et si elle couvre les disques et dépendances nécessaires.

Un snapshot d'une VM n'est pas automatiquement une sauvegarde indépendante. Pour récupérer après une perte complète du stockage, il faut disposer d'une copie récupérable ailleurs.

### 9.5 Dépendances souvent oubliées

Pour restaurer un service, il peut être nécessaire de retrouver :

- Les certificats.
- Les clés de chiffrement.
- Les configurations DNS.
- Les règles de pare-feu.
- Les paramètres réseau.
- Les fichiers d'installation.
- Les licences.
- Les secrets.
- Les procédures d'accès.
- Les données de configuration.
- Les informations nécessaires au démarrage.

Il faut protéger les secrets sans les mélanger à des copies ordinaires accessibles trop largement.

## 10. Préparer un laboratoire Linux

Nous allons créer un petit environnement fictif.

La source sera un dossier local contenant plusieurs fichiers. La destination initiale sera un répertoire de sauvegarde de test.

Attention : un répertoire placé sur le même disque que les données originales ne protège pas contre la panne physique de ce disque.

### 10.1 Créer les données de test

```bash
mkdir -p ~/backup-lab/source
mkdir -p ~/backup-lab/restore-test
```

Créer des fichiers :

```bash
echo "Document de test numéro 1" > ~/backup-lab/source/document1.txt
echo "Document de test numéro 2" > ~/backup-lab/source/document2.txt
echo "Configuration de test" > ~/backup-lab/source/config.txt
```

Lister le contenu :

```bash
find ~/backup-lab/source -maxdepth 1 -type f -print
```

Examiner les tailles :

```bash
du -sh ~/backup-lab/source
```

### 10.2 Pourquoi commencer par un dossier de test ?

La restauration peut écraser des fichiers, remplacer des versions ou réintroduire des données indésirables.

Il est donc préférable de travailler d'abord dans un environnement de test, puis de valider les résultats avant de restaurer dans l'emplacement de production.

## 11. Créer une archive avec tar

### 11.1 Qu'est-ce que tar ?

`tar` est un outil permettant de regrouper des fichiers et des répertoires dans une archive.

Il peut également être utilisé avec une compression telle que gzip.

Une archive facilite le transport et la conservation d'un ensemble de fichiers.

Mais une archive tar ne fournit pas automatiquement un historique, une gestion de rétention, une sauvegarde incrémentale optimisée ou un chiffrement.

### 11.2 Créer le répertoire de sauvegarde

Dans le laboratoire :

```bash
mkdir -p ~/backup-lab/archives
```

### 11.3 Créer une archive compressée

```bash
tar -czf ~/backup-lab/archives/source-$(date +%F).tar.gz \
  -C ~/backup-lab source
```

Explication :

- `-c` crée une archive.
- `-z` utilise gzip.
- `-f` indique le fichier de sortie.
- `$(date +%F)` insère la date au format année-mois-jour.
- `-C` change le répertoire de référence avant l'ajout.
- `source` est le répertoire à sauvegarder.

Exemple de résultat :

```text
backup-lab/
  |
  +-- source/
  |    +-- document1.txt
  |    +-- document2.txt
  |    +-- config.txt
  |
  +-- archives/
       +-- source-2026-10-24.tar.gz
```

La date d'exemple correspond au jour de création indiqué. Le nom réel dépend de la date et de l'heure de l'exécution.

### 11.4 Vérifier qu'une archive est lisible

Lister les fichiers contenus :

```bash
tar -tzf ~/backup-lab/archives/source-$(date +%F).tar.gz
```

Cette commande montre la liste des membres de l'archive. Elle ne constitue pas à elle seule un test exhaustif de restauration.

### 11.5 Examiner la taille

```bash
ls -lh ~/backup-lab/archives/
```

Une archive compressée peut être plus petite que les fichiers d'origine, mais le niveau de réduction dépend du contenu. Les fichiers déjà compressés ne diminuent généralement pas beaucoup.

## 12. Restaurer une archive tar

### 12.1 Préparer la destination

```bash
mkdir -p ~/backup-lab/restore-test
```

### 12.2 Extraire dans un emplacement séparé

```bash
tar -xzf ~/backup-lab/archives/source-$(date +%F).tar.gz \
  -C ~/backup-lab/restore-test
```

Explication :

- `-x` extrait le contenu.
- `-z` décompresse gzip.
- `-f` indique le fichier d'archive.
- `-C` définit le répertoire de destination.

Après extraction, le répertoire restauré doit se trouver sous `~/backup-lab/restore-test/source`.

### 12.3 Vérifier les fichiers

```bash
find ~/backup-lab/restore-test -maxdepth 2 -type f -print
```

Comparer les contenus :

```bash
diff -r ~/backup-lab/source \
  ~/backup-lab/restore-test/source
```

Si la commande `diff` ne signale aucune différence, les contenus comparés sont identiques selon cette comparaison.

### 12.4 Pourquoi restaurer dans un autre dossier ?

La restauration dans un répertoire séparé permet de vérifier les données sans écraser la source.

Cela évite de confondre un test technique avec une restauration réelle. C'est également une bonne manière d'apprendre à inspecter une copie avant de la remettre en production.

## 13. Comprendre rsync

### 13.1 Le rôle de rsync

`rsync` est un outil de copie et de synchronisation efficace entre répertoires locaux ou entre machines.

Il peut éviter de retransférer inutilement des données lorsque la destination contient déjà une copie similaire.

Il est souvent utilisé pour :

- Copier des fichiers vers un disque de sauvegarde.
- Transférer des données sur un autre serveur.
- Synchroniser des répertoires.
- Déplacer des données.
- Préparer une copie avant une opération de maintenance.

`rsync` ne constitue pas automatiquement un système de sauvegarde versionnée.

### 13.2 Copier un répertoire

```bash
mkdir -p ~/backup-lab/rsync-copy
```

Puis :

```bash
rsync -a --human-readable \
  ~/backup-lab/source/ \
  ~/backup-lab/rsync-copy/
```

Le slash final sur la source signifie que le contenu de `source` est copié dans le répertoire de destination.

Sans ce slash final, la structure créée peut différer.

### 13.3 Comprendre les options

| Option | Fonction |
|---|---|
| `-a` | Mode archive, conservant notamment l'arborescence et plusieurs attributs |
| `--human-readable` | Affichage des tailles sous une forme plus lisible |
| `--info=progress2` | Affichage d'une progression globale lorsque cette option est disponible |
| `--dry-run` | Simulation des opérations sans les exécuter |
| `-v` | Mode bavard |

Le mode archive n'est pas une garantie de préservation de tous les attributs possibles dans tous les contextes. Les permissions, ACL, attributs étendus et propriétés spécifiques peuvent demander des options ou permissions supplémentaires.

### 13.4 Simuler une copie avant de l'exécuter

```bash
rsync -a --dry-run --itemize-changes \
  ~/backup-lab/source/ \
  ~/backup-lab/rsync-copy/
```

Le mode simulation permet d'examiner les opérations prévues.

Pour une commande qui pourrait remplacer ou supprimer de nombreux fichiers, examiner le résultat avant de procéder.

### 13.5 Le piège de `--delete`

L'option `--delete` permet de retirer de la destination les fichiers absents de la source.

Elle est utile dans certains scénarios de miroir, mais elle peut aussi effacer des données que l'on souhaitait conserver.

Exemple à ne pas exécuter sans analyse :

```bash
rsync -a --delete source/ destination/
```

Si un fichier est accidentellement supprimé dans la source, une synchronisation avec `--delete` peut également le supprimer de la destination.

Pour une sauvegarde qui doit préserver les anciennes versions, utiliser un outil de sauvegarde versionnée ou des répertoires datés avec une politique de rétention maîtrisée.

### 13.6 Copier vers un autre serveur

Exemple de copie vers un serveur de sauvegarde accessible par SSH :

```bash
rsync -a --human-readable \
  ~/backup-lab/source/ \
  backupuser@backup01:/srv/backups/backup-lab/
```

Les noms sont fictifs et doivent être adaptés.

Avant le transfert, il faut vérifier :

- L'accès SSH.
- Les droits du compte distant.
- L'espace disponible.
- La connectivité.
- Le comportement de la copie.
- La protection des données sur la destination.

Une copie sur un serveur distant ne constitue pas une protection suffisante si le même compte peut supprimer toutes les versions sans contrôle.

## 14. Créer des sommes de contrôle

### 14.1 Pourquoi vérifier l'intégrité ?

Une sauvegarde peut être présente sans être exploitable.

Les données peuvent être altérées pendant le transfert, mal écrites ou corrompues après leur création.

Une somme de contrôle permet de comparer le contenu d'un fichier à un condensat calculé par un algorithme.

### 14.2 Calculer une somme SHA-256

```bash
sha256sum ~/backup-lab/archives/source-$(date +%F).tar.gz
```

Résultat illustratif :

```text
fictif...  source-2026-10-24.tar.gz
```

La valeur réelle est calculée par la commande. Il ne faut pas remplacer une valeur manquante par un condensat inventé.

### 14.3 Enregistrer une somme de contrôle

```bash
cd ~/backup-lab/archives
sha256sum source-$(date +%F).tar.gz > SHA256SUMS.txt
```

Vérifier le fichier :

```bash
sha256sum -c SHA256SUMS.txt
```

Cette commande vérifie que le condensat du fichier correspond au condensat enregistré.

### 14.4 Limite importante

Une somme de contrôle stockée à côté de l'archive ne protège pas contre un attaquant qui peut modifier à la fois l'archive et le fichier de sommes de contrôle.

Pour renforcer la protection, conserver les preuves d'intégrité dans un emplacement et un périmètre d'accès distincts lorsque le risque le justifie.

Le condensat ne remplace pas non plus un test de restauration. Un fichier peut être intact tout en étant inutilisable si le logiciel nécessaire, les clés ou les dépendances manquent.

## 15. Découvrir Restic

### 15.1 À quoi sert Restic ?

Restic est un logiciel de sauvegarde qui conserve des snapshots de fichiers dans un dépôt. Il prend notamment en charge le chiffrement du dépôt et la sauvegarde de différentes sources.

Il permet notamment :

- D'initialiser un dépôt.
- De créer une sauvegarde.
- De lister les snapshots.
- D'examiner des versions.
- De restaurer des données.
- De vérifier le dépôt.
- De gérer la rétention.

Restic ne planifie pas automatiquement tous les travaux à lui seul. La programmation périodique peut être réalisée avec des mécanismes comme `cron`, systemd ou un ordonnanceur adapté.

Documentation officielle : https://restic.readthedocs.io/

### 15.2 Pourquoi utiliser un outil de sauvegarde dédié ?

Contrairement à une simple archive, un système comme Restic est conçu pour gérer plusieurs versions et réduire les duplications de données selon son fonctionnement.

Il offre également des mécanismes de vérification du dépôt et de restauration.

La manière de stocker les données, de gérer les clés et de configurer les sauvegardes dépend de l'outil et de la version utilisés. Les principes de protection et de tests restent indispensables.

## 16. Installer et préparer Restic

La méthode d'installation dépend du système d'exploitation et de la distribution.

Consulter la documentation officielle :

https://restic.readthedocs.io/en/stable/020_installation.html

Après l'installation, vérifier la disponibilité de la commande :

```bash
restic version
```

Le résultat doit indiquer la version installée.

### 16.1 Créer un dépôt local de laboratoire

Dans cet exemple, le dépôt est local :

```bash
mkdir -p ~/backup-lab/restic-repository
```

Cette méthode convient à un exercice. En production, le dépôt devrait généralement être placé sur un stockage indépendant et protégé selon la stratégie de sauvegarde.

### 16.2 Créer un fichier de mot de passe protégé

Restic utilise un mot de passe pour chiffrer les données du dépôt.

Créer un emplacement de configuration :

```bash
mkdir -p ~/.config/restic
chmod 700 ~/.config/restic
```

Générer un mot de passe aléatoire :

```bash
umask 077
openssl rand -base64 32 > ~/.config/restic/password
chmod 600 ~/.config/restic/password
```

Cette méthode nécessite OpenSSL.

Le fichier contient un secret indispensable à l'accès au dépôt. Le protéger soigneusement et en conserver une copie sécurisée dans un système de gestion des secrets adapté.

Si le mot de passe est perdu et qu'aucune copie exploitable n'existe, les données chiffrées peuvent devenir irrécupérables.

### 16.3 Définir les variables d'environnement

Dans le terminal de laboratoire :

```bash
export RESTIC_REPOSITORY="$HOME/backup-lab/restic-repository"
export RESTIC_PASSWORD_FILE="$HOME/.config/restic/password"
```

Ces variables indiquent à Restic le dépôt utilisé et le fichier contenant le secret.

Pour consulter leur valeur sans exposer le contenu du secret :

```bash
printf 'Dépôt : %s\n' "$RESTIC_REPOSITORY"
printf 'Fichier de mot de passe : %s\n' "$RESTIC_PASSWORD_FILE"
```

Éviter de placer le mot de passe directement dans une commande ou un script partagé. Les variables d'environnement ne sont pas non plus une solution universelle de gestion des secrets ; leur usage doit être adapté au contexte.

### 16.4 Initialiser le dépôt

```bash
restic init
```

Cette commande initialise le dépôt. Elle doit normalement être exécutée une seule fois par dépôt nouvellement créé.

Ne pas réinitialiser un dépôt existant sans comprendre ce que l'opération implique.

## 17. Réaliser une sauvegarde avec Restic

### 17.1 Sauvegarder les données de test

```bash
restic backup "$HOME/backup-lab/source"
```

Restic parcourt les fichiers sélectionnés et enregistre un snapshot.

Pour identifier le contenu et le contexte de la sauvegarde, on peut utiliser des tags :

```bash
restic backup \
  --tag labo \
  --tag documents \
  "$HOME/backup-lab/source"
```

Les tags facilitent l'identification et certaines opérations ultérieures de gestion des snapshots.

### 17.2 Lire le résultat

Après une sauvegarde, examiner les informations de l'opération :

- Nombre de fichiers examinés.
- Volume ajouté.
- Volume traité.
- Nombre d'erreurs éventuelles.
- Identifiant du snapshot.
- Répertoire ou périmètre sauvegardé.

Ne pas considérer uniquement le code de retour comme une preuve suffisante de récupérabilité. Il faut également surveiller les erreurs, l'espace restant et les résultats des vérifications.

### 17.3 Lister les snapshots

```bash
restic snapshots
```

La sortie permet de consulter les versions disponibles dans le dépôt.

Une sauvegarde récente doit correspondre au bon hôte, au bon chemin et au périmètre attendu.

### 17.4 Examiner le contenu d'un snapshot

Pour voir les fichiers d'un snapshot donné :

```bash
restic ls latest
```

La référence `latest` sélectionne le snapshot le plus récent correspondant au contexte de sélection de Restic.

Dans un dépôt partagé par plusieurs machines, il faut tenir compte des hôtes, chemins et tags selon les critères de regroupement utilisés. Vérifier que le snapshot sélectionné est bien celui que l'on souhaite restaurer.

### 17.5 Effectuer plusieurs versions

Modifier un fichier de test :

```bash
echo "Modification du fichier" >> ~/backup-lab/source/document1.txt
```

Puis créer une nouvelle sauvegarde :

```bash
restic backup "$HOME/backup-lab/source"
```

Lister les snapshots :

```bash
restic snapshots
```

On peut maintenant constater que plusieurs états successifs ont été conservés.

C'est un avantage fondamental par rapport à une simple synchronisation : il est possible de rechercher une version antérieure même si le fichier source a changé depuis.

## 18. Restaurer des données avec Restic

### 18.1 Ne pas restaurer directement sur les fichiers d'origine au premier essai

Une restauration mal ciblée peut remplacer des fichiers actuels. Pour un premier test, restaurer dans un nouveau répertoire.

Créer une destination :

```bash
mkdir -p ~/backup-lab/restic-restore
```

Restaurer le snapshot le plus récent :

```bash
restic restore latest \
  --target "$HOME/backup-lab/restic-restore"
```

La commande extrait dans le répertoire cible les chemins appartenant au snapshot selon la structure gérée par Restic.

Le répertoire restauré peut reproduire une partie de l'arborescence d'origine. Il faut examiner la sortie et localiser les fichiers restaurés avant de poursuivre.

### 18.2 Restaurer un snapshot précis

Lister les snapshots :

```bash
restic snapshots
```

Choisir l'identifiant du snapshot désiré, puis exécuter :

```bash
restic restore IDENTIFIANT_DU_SNAPSHOT \
  --target "$HOME/backup-lab/restic-restore"
```

Remplacer `IDENTIFIANT_DU_SNAPSHOT` par un identifiant réel obtenu avec `restic snapshots`.

Cette commande ne doit pas être exécutée avec un identifiant fictif.

### 18.3 Vérifier les fichiers restaurés

Examiner l'arborescence :

```bash
find ~/backup-lab/restic-restore -type f -print
```

Comparer les contenus restaurés aux fichiers attendus, en tenant compte du chemin de destination.

Pour les restaurations de production, vérifier également les permissions, les propriétaires, les attributs nécessaires et les dépendances des applications.

### 18.4 Récupérer un fichier particulier

Restic permet aussi de rechercher et de restaurer des fichiers individuels. La sélection dépend du chemin tel qu'il apparaît dans le snapshot et de la syntaxe prise en charge par la version installée.

Avant de restaurer un fichier de production :

1. Identifier le snapshot.
2. Localiser le chemin exact dans celui-ci.
3. Sélectionner un répertoire de test.
4. Vérifier le contenu récupéré.
5. Décider ensuite de la procédure de remplacement du fichier en production.

## 19. Vérifier l'intégrité d'un dépôt Restic

### 19.1 Vérification du dépôt

```bash
restic check
```

Cette commande vérifie la cohérence des structures internes du dépôt selon les contrôles réalisés par Restic.

Elle ne remplace pas un test applicatif de restauration.

### 19.2 Vérifier les données stockées

Pour une vérification plus approfondie des données :

```bash
restic check --read-data
```

Cette commande lit les données du dépôt pour en vérifier l'intégrité. Elle peut être plus longue et solliciter davantage le stockage et le réseau que la vérification de base.

Planifier les vérifications en tenant compte des performances, du volume de données et des fenêtres d'exploitation.

### 19.3 La différence entre trois contrôles

| Contrôle | Ce qu'il permet d'examiner |
|---|---|
| Succès du travail de sauvegarde | Résultat de l'opération selon le logiciel |
| Vérification du dépôt | Cohérence de certaines structures internes |
| Test de restauration | Capacité réelle à récupérer les données et à les utiliser |

Une stratégie sérieuse utilise ces contrôles de manière complémentaire.

## 20. Comprendre la rétention des sauvegardes

### 20.1 Pourquoi faut-il supprimer certaines anciennes versions ?

Les données occupent de l'espace. Si l'on conserve toutes les versions pour toujours, le dépôt peut finir par manquer de capacité.

La rétention détermine quelles versions doivent être conservées et lesquelles peuvent être retirées.

Exemple de politique :

```text
Dernières sauvegardes quotidiennes : 7
Dernières sauvegardes hebdomadaires : 4
Dernières sauvegardes mensuelles : 6
```

Ces valeurs sont un exemple, pas une politique universelle.

Il faut tenir compte des besoins métier, des coûts, des exigences de conservation et du risque de suppression prématurée.

### 20.2 Politique de rétention avec Restic

Un exemple de gestion de rétention :

```bash
restic forget \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 6 \
  --prune
```

Cette commande peut supprimer les snapshots qui ne correspondent plus à la politique spécifiée et effectuer ensuite le nettoyage des données qui ne sont plus référencées.

Il s'agit d'une opération destructive pour l'historique qui n'est plus retenu. Elle doit être testée et approuvée avant utilisation sur un dépôt important.

### 20.3 Pourquoi séparer sauvegarde et rétention ?

Les tâches de sauvegarde créent de nouveaux points de restauration.

La rétention supprime certains points qui ne doivent plus être conservés.

Les deux opérations n'ont pas le même objectif et ne devraient pas être exécutées sans contrôle.

Avant toute purge :

- Vérifier la politique.
- Vérifier les snapshots conservés.
- Vérifier les versions qui seront retirées.
- Contrôler les exigences métier.
- Préserver les preuves nécessaires.
- S'assurer que les nouvelles sauvegardes fonctionnent.

## 21. Automatiser une sauvegarde Restic

### 21.1 Principe

Une sauvegarde automatique doit être reproductible, journalisée et contrôlée.

```text
Déclenchement planifié
         |
         v
Vérification des prérequis
         |
         v
Exécution de Restic
         |
         v
Contrôle du code de retour
         |
         v
Journalisation du résultat
         |
         v
Alerte en cas d'échec
         |
         v
Vérification périodique et test de restauration
```

Une tâche qui ne s'exécute jamais ou qui échoue sans notification peut donner une fausse impression de sécurité.

### 21.2 Créer un script de laboratoire

Créer `~/backup-lab/backup-restic.sh` :

```bash
#!/usr/bin/env bash

set -Eeuo pipefail

REPOSITORY="$HOME/backup-lab/restic-repository"
PASSWORD_FILE="$HOME/.config/restic/password"
SOURCE="$HOME/backup-lab/source"
LOG_DIR="$HOME/backup-lab/logs"

mkdir -p "$LOG_DIR"

TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
LOG_FILE="$LOG_DIR/restic-$TIMESTAMP.log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "Début de la sauvegarde : $(date --iso-8601=seconds)"

if ! command -v restic >/dev/null 2>&1; then
    echo "ERREUR : Restic n'est pas installé."
    exit 1
fi

if [[ ! -d "$SOURCE" ]]; then
    echo "ERREUR : le répertoire source n'existe pas."
    exit 1
fi

if [[ ! -r "$PASSWORD_FILE" ]]; then
    echo "ERREUR : le fichier de mot de passe est absent ou illisible."
    exit 1
fi

if [[ ! -d "$REPOSITORY" ]]; then
    echo "ERREUR : le dépôt n'existe pas."
    exit 1
fi

export RESTIC_REPOSITORY="$REPOSITORY"
export RESTIC_PASSWORD_FILE="$PASSWORD_FILE"

restic snapshots

restic backup \
    --tag automatic \
    "$SOURCE"

echo "Vérification du dépôt"
restic check

echo "Fin de la sauvegarde : $(date --iso-8601=seconds)"
```

Ce script correspond au laboratoire local présenté dans les sections précédentes.

Pour un autre environnement, adapter le chemin de dépôt, la source, le fichier de secret et la méthode de notification.

### 21.3 Rendre le script exécutable

```bash
chmod 700 ~/backup-lab/backup-restic.sh
```

Puis l'exécuter :

```bash
~/backup-lab/backup-restic.sh
```

La sortie est conservée dans un fichier horodaté et également affichée dans le terminal.

### 21.4 Limites du script

Ce script illustre une automatisation simple. Il ne remplace pas une solution de sauvegarde d'entreprise.

Il faut encore réfléchir à :

- La gestion des exécutions concurrentes.
- Les délais et les erreurs de stockage.
- Les notifications.
- Les limites de durée.
- Le réseau.
- Le dépôt distant.
- Les sauvegardes de secrets.
- Les restaurations de test.
- La supervision de la tâche.
- La stratégie de rétention.

Le script peut notamment nécessiter un mécanisme de verrouillage pour empêcher plusieurs exécutions de se chevaucher.

## 22. Planifier une sauvegarde sous Linux

### 22.1 Le rôle de cron

`cron` permet d'exécuter des commandes à des horaires définis.

Pour ouvrir le crontab de l'utilisateur :

```bash
crontab -e
```

Exemple :

```cron
0 2 * * * /home/alice/backup-lab/backup-restic.sh
```

Cette entrée demande une exécution tous les jours à 02 h 00 selon la configuration temporelle du système et du service cron.

Remplacer `/home/alice` par le répertoire réel.

### 22.2 Ce qu'il faut vérifier

Avant de planifier la tâche :

- Le script s'exécute manuellement.
- Les chemins sont explicites.
- Les permissions sont correctes.
- Le fichier de mot de passe est accessible.
- La destination dispose d'assez d'espace.
- L'environnement d'exécution est connu.
- Les erreurs sont enregistrées.
- Une notification existe en cas d'échec.
- Les horaires ne se chevauchent pas avec d'autres travaux lourds.

Une tâche cron peut s'exécuter dans un environnement différent de celui du terminal interactif. Il faut notamment éviter de dépendre de variables qui ne seront pas définies.

### 22.3 Vérifier l'exécution

Le répertoire suivant contient les journaux produits par le script de laboratoire :

```bash
ls -lah ~/backup-lab/logs
```

Examiner le dernier fichier :

```bash
tail -n 100 "$(ls -1t ~/backup-lab/logs/*.log | head -n 1)"
```

Il faut aussi contrôler que la sauvegarde est visible dans le dépôt :

```bash
export RESTIC_REPOSITORY="$HOME/backup-lab/restic-repository"
export RESTIC_PASSWORD_FILE="$HOME/.config/restic/password"

restic snapshots
```

La présence d'un fichier de journal ne suffit pas : le résultat de la sauvegarde doit être confirmé.

## 23. Sauvegarder des fichiers sous Windows

Windows dispose de plusieurs possibilités de sauvegarde et de restauration. Le choix dépend notamment du système d'exploitation, du type de données et du besoin de reprise.

Les solutions possibles incluent :

- Historique des fichiers lorsqu'il est disponible et adapté.
- Sauvegarde Windows Server.
- `wbadmin`.
- Des outils de sauvegarde tiers.
- Des sauvegardes applicatives spécifiques.
- Des solutions de protection de postes et de données d'entreprise.

La disponibilité des fonctionnalités et les conditions d'utilisation varient selon la version de Windows.

### 23.1 Préparer un dossier de test

Dans PowerShell :

```powershell
New-Item -ItemType Directory -Force -Path "C:\BackupLab\Source"
New-Item -ItemType Directory -Force -Path "C:\BackupLab\Restore"
```

Créer des fichiers :

```powershell
Set-Content -Path "C:\BackupLab\Source\document1.txt" -Value "Document de test 1"
Set-Content -Path "C:\BackupLab\Source\document2.txt" -Value "Document de test 2"
```

### 23.2 Copier les données vers un emplacement de test

```powershell
Copy-Item `
    -Path "C:\BackupLab\Source\*" `
    -Destination "C:\BackupLab\Restore" `
    -Recurse
```

Cette commande effectue une copie. Elle n'offre pas à elle seule un historique de versions ni la protection complète d'une solution de sauvegarde.

Elle sert ici à comprendre le processus de copie et à préparer un premier test de vérification.

### 23.3 Comparer le contenu

```powershell
Get-ChildItem "C:\BackupLab\Source" -Recurse
Get-ChildItem "C:\BackupLab\Restore" -Recurse
```

Pour comparer un contenu précis :

```powershell
Get-Content "C:\BackupLab\Source\document1.txt"
Get-Content "C:\BackupLab\Restore\document1.txt"
```

Dans le laboratoire, les contenus doivent correspondre.

## 24. Windows Server Backup et wbadmin

### 24.1 Qu'est-ce que wbadmin ?

`wbadmin` est un outil en ligne de commande permettant de réaliser certaines opérations de sauvegarde et de restauration sur les versions Windows prises en charge.

Ses possibilités comprennent notamment :

- Sauvegarder des volumes et fichiers.
- Réaliser certaines sauvegardes du système.
- Examiner les versions disponibles.
- Consulter l'état d'une opération.
- Restaurer des données selon les paramètres autorisés.

Il faut utiliser une version compatible avec le serveur et respecter les permissions requises.

Documentation officielle :

https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin

### 24.2 Vérifier la présence de la fonctionnalité

Selon la version et la configuration du serveur, Windows Server Backup peut nécessiter l'installation de la fonctionnalité correspondante.

Vérifier son état dans la gestion des rôles et fonctionnalités du serveur.

Ne pas supposer que toutes les commandes fonctionneront sur chaque édition ou installation de Windows.

### 24.3 Examiner les disques disponibles

Dans une console administrateur adaptée :

```powershell
wbadmin get disks
```

Cette commande affiche les disques détectés par l'outil, selon le contexte d'exécution.

Il faut vérifier soigneusement le support de sauvegarde cible avant toute opération.

### 24.4 Lancer une sauvegarde

Pour réaliser une sauvegarde planifiée ou ponctuelle, la configuration dépend du périmètre, des volumes, du support de destination et des options disponibles.

Exemple conceptuel de sauvegarde ciblant un volume de sauvegarde :

```powershell
wbadmin start backup -backupTarget:E: -allCritical -quiet
```

**Attention :** cette commande est un exemple. Il faut vérifier le support cible, les capacités disponibles, les volumes critiques et la procédure adaptée à la version du système. Ne pas la lancer sans avoir validé que `E:` correspond réellement à la destination souhaitée.

Pour un travail de sauvegarde réel, il est préférable de commencer par examiner la documentation des paramètres et de tester le résultat dans un environnement contrôlé.

### 24.5 Vérifier l'état du travail

```powershell
wbadmin get status
```

Cette commande permet de consulter l'état d'une opération en cours, lorsqu'il y en a une.

Pour consulter les versions disponibles :

```powershell
wbadmin get versions
```

Ces commandes aident à vérifier l'existence de points de restauration.

### 24.6 Pourquoi ne pas utiliser une commande de restauration sans vérifier le périmètre ?

Une restauration peut écraser ou remplacer des éléments existants selon les options utilisées.

Avant d'exécuter une restauration, il faut déterminer :

- La version à restaurer.
- Le type d'élément.
- Le chemin ou volume de destination.
- Les conséquences sur les données actuelles.
- Les permissions.
- Les dépendances du service.
- La procédure de retour arrière.

La documentation officielle de `wbadmin` décrit les paramètres de restauration :

https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-recovery

### 24.7 Restaurer à l'aide des outils Windows

Pour restaurer une sauvegarde, on peut utiliser l'interface Windows Server Backup ou la commande appropriée avec les identifiants exacts de la sauvegarde et les paramètres de destination nécessaires.

Avant de restaurer sur le système de production, effectuer si possible une restauration de test vers un emplacement distinct.

Cela permet de vérifier que les fichiers existent et sont lisibles sans écraser immédiatement les données actuelles.

## 25. Sauvegarder une base de données

Une base de données n'est pas simplement un répertoire contenant des fichiers ordinaires. Elle peut être active et modifier ses données pendant la sauvegarde.

Une copie brute effectuée au mauvais moment peut être incohérente.

### 25.1 Sauvegarde logique

Une sauvegarde logique exporte les objets et données selon le format proposé par le moteur.

Pour PostgreSQL, `pg_dump` est un outil courant d'export logique.

Exemple :

```bash
pg_dump -Fc -d NOM_DE_BASE -f sauvegarde.dump
```

Remplacer `NOM_DE_BASE` par le nom réel de la base.

L'accès à la base peut nécessiter des paramètres d'authentification adaptés. Éviter de mettre les mots de passe en clair dans les commandes et dans les scripts.

### 25.2 Vérifier la sauvegarde

L'existence du fichier ne prouve pas que l'export sera restauré correctement.

Vérifier :

- Le code de retour de l'outil.
- La taille du fichier.
- Les journaux de l'opération.
- La disponibilité des identifiants nécessaires à la restauration.
- L'espace disponible.
- La possibilité de lire ou d'inspecter l'archive.
- La capacité à restaurer dans un environnement de test.

### 25.3 Restaurer dans une base de test

Avec PostgreSQL, `pg_restore` permet de restaurer un export compatible, par exemple :

```bash
pg_restore -d BASE_DE_TEST sauvegarde.dump
```

Il faut créer et configurer la base cible selon le scénario de restauration. La commande peut échouer si les objets, rôles, extensions ou dépendances ne sont pas disponibles.

Ne pas utiliser une base de production comme destination d'un exercice.

### 25.4 Cohérence et sauvegarde des bases

Selon la taille de la base, le RPO et le RTO, il peut être nécessaire d'utiliser :

- Des sauvegardes logiques.
- Des sauvegardes physiques.
- Des sauvegardes à chaud.
- Des mécanismes de snapshots cohérents.
- Des journaux de transactions.
- Une réplication adaptée.
- Des tests de restauration réguliers.

Les bases transactionnelles critiques exigent un niveau de planification supérieur à une simple copie de fichiers.

## 26. Vérifier réellement une restauration

### 26.1 Pourquoi ce test est-il indispensable ?

Un compte rendu indiquant « sauvegarde terminée » ne prouve pas que les données pourront être récupérées après un sinistre.

Il peut manquer :

- Le mot de passe.
- La clé de chiffrement.
- Un catalogue.
- Un volume.
- Un fichier de configuration.
- Une dépendance logicielle.
- Une permission.
- Un identifiant de base de données.
- Une copie complète des données.

Il faut donc tester périodiquement la restauration.

### 26.2 Procédure de test

```text
1. Choisir une sauvegarde connue
             |
             v
2. Identifier les données attendues
             |
             v
3. Préparer un environnement isolé
             |
             v
4. Restaurer dans une destination de test
             |
             v
5. Vérifier les fichiers et permissions
             |
             v
6. Ouvrir les données ou démarrer l'application
             |
             v
7. Comparer avec les attentes
             |
             v
8. Mesurer le délai de restauration
             |
             v
9. Documenter le résultat
```

### 26.3 Vérifications à effectuer

Un test de restauration doit pouvoir vérifier :

- La présence des données.
- La cohérence des fichiers.
- L'intégrité des archives.
- Les permissions et propriétaires nécessaires.
- La disponibilité des secrets et dépendances.
- Le fonctionnement de l'application.
- La durée de restauration.
- La quantité de données perdues, lorsqu'elle peut être mesurée.
- La capacité à respecter le RPO et le RTO.

Le test doit être répété selon la criticité du service et les risques.

## 27. Sécuriser les sauvegardes contre les rançongiciels

### 27.1 Pourquoi les sauvegardes sont-elles ciblées ?

Un rançongiciel peut chercher à chiffrer les fichiers de production et à supprimer les sauvegardes accessibles.

Si le même compte privilégié peut modifier les données et supprimer les dépôts de sauvegarde, une compromission peut affecter les deux.

La stratégie doit séparer les responsabilités et réduire les possibilités de suppression.

### 27.2 Mesures de protection

- Garder une copie hors ligne ou isolée.
- Utiliser une copie immuable lorsque c'est adapté.
- Chiffrer les sauvegardes.
- Séparer les comptes d'administration.
- Appliquer le moindre privilège.
- Protéger les clés et mots de passe de chiffrement.
- Limiter les droits de suppression.
- Contrôler les connexions aux dépôts.
- Surveiller les échecs et les suppressions inhabituelles.
- Tester la restauration dans un environnement propre.

Ces mesures sont cohérentes avec les recommandations de préparation à la reprise après rançongiciel publiées par la CISA.

Documentation :

https://www.cisa.gov/stopransomware/ransomware-guide

### 27.3 Ne pas reconnecter aveuglément une sauvegarde

Si un système est compromis, il faut évaluer le risque avant de reconnecter les dépôts de sauvegarde à l'environnement affecté.

La restauration doit être effectuée dans un environnement propre ou contrôlé. Sinon, les systèmes récupérés peuvent être à nouveau compromis.

La procédure de reprise doit inclure l'analyse de l'incident, le contrôle des comptes, la vérification des systèmes restaurés et des mesures adaptées à la menace identifiée.

## 28. Scripts de sauvegarde : bonnes pratiques

### 28.1 Contrôler les erreurs

Un script doit distinguer une sauvegarde réussie d'une sauvegarde partiellement réussie ou échouée.

Sous Bash :

```bash
#!/usr/bin/env bash

set -Eeuo pipefail

echo "Début de la sauvegarde"

# Exécuter ici la commande de sauvegarde adaptée.

echo "Sauvegarde terminée"
```

Cette base améliore le traitement de certains échecs, mais elle n'envoie pas automatiquement une notification et ne valide pas l'intégrité des données.

### 28.2 Utiliser des chemins explicites

Éviter de dépendre d'un répertoire courant imprévisible.

Préférer :

```bash
SOURCE="/srv/application/data"
DESTINATION="/mnt/backup/application"
```

puis vérifier que les chemins existent et que la destination est bien le support attendu.

### 28.3 Éviter les exécutions concurrentes

Si une sauvegarde dure plus longtemps que prévu, la tâche suivante peut démarrer pendant que la précédente fonctionne encore.

Selon l'outil et le système, utiliser un verrouillage ou un mécanisme d'ordonnancement permettant d'éviter les chevauchements.

### 28.4 Enregistrer des informations utiles

Les journaux de sauvegarde doivent contenir notamment :

- L'heure de début.
- L'heure de fin.
- Le périmètre.
- Le résultat.
- L'identifiant du snapshot lorsque disponible.
- Les erreurs.
- Les opérations de vérification.
- Les éventuelles notifications.

Ils ne doivent pas contenir les secrets nécessaires au déchiffrement.

## 29. Capacité, durée et planification

### 29.1 Estimer le volume

Supposons que les données sources représentent 200 Go.

Si une sauvegarde complète copie l'ensemble des données, le volume logique de la copie peut être proche de 200 Go, en fonction du format utilisé et de la compression.

Si les modifications quotidiennes sont de 8 Go et que le mécanisme d'incrémentation ne conserve que les blocs modifiés, le volume transféré chaque jour peut être sensiblement inférieur.

Il ne faut pas supposer que tous les logiciels calculent la taille de la même façon.

### 29.2 Durée de transfert

Une estimation simple peut être faite à partir du débit effectif.

Exemple :

```text
Volume à transférer : 100 Go
Débit effectif      : 50 Mo/s
```

En utilisant 100 Go comme 100 000 Mo :

```text
Durée approximative :
100 000 / 50 = 2 000 secondes
```

Soit environ 33 minutes et 20 secondes dans ce calcul simplifié.

La durée réelle dépend de la charge, du protocole, de la compression, du nombre de petits fichiers, du stockage, de la latence et des autres traitements.

### 29.3 Prévoir une marge

La fenêtre de sauvegarde doit tenir compte :

- Du volume actuel.
- De la croissance.
- Des pics de charge.
- Du réseau disponible.
- Des tâches concurrentes.
- Du chiffrement.
- De la compression.
- De la vérification.
- Des éventuelles copies hors site.

Il ne faut pas planifier un travail exactement à la limite de la fenêtre disponible sans prévoir de marge.

## 30. Restaurer après une suppression accidentelle

Imaginons qu'un administrateur supprime un document important.

Une démarche prudente consiste à :

1. Arrêter si possible les opérations qui pourraient écraser l'historique.
2. Identifier le chemin supprimé.
3. Déterminer la date de la dernière version correcte.
4. Sélectionner le snapshot approprié.
5. Restaurer dans un emplacement temporaire.
6. Vérifier le contenu.
7. Vérifier les permissions et attributs.
8. Confirmer le besoin avec le propriétaire des données.
9. Remettre le fichier à l'emplacement prévu.
10. Documenter l'intervention.

Ne pas restaurer une ancienne version complète du système pour un simple document, lorsque la récupération ciblée du fichier est possible.

## 31. Exercice guidé : réaliser puis restaurer une sauvegarde

### Objectif

Mettre en œuvre un cycle complet sur des données de laboratoire.

### Étape 1 — Créer les données

```bash
mkdir -p ~/backup-lab/exercice-source

echo "Version 1" > ~/backup-lab/exercice-source/fichier.txt
echo "Données complémentaires" > ~/backup-lab/exercice-source/donnees.txt
```

### Étape 2 — Créer une sauvegarde

Avec tar :

```bash
mkdir -p ~/backup-lab/exercice-backups

tar -czf ~/backup-lab/exercice-backups/exercice.tar.gz \
  -C ~/backup-lab exercice-source
```

### Étape 3 — Vérifier l'archive

```bash
tar -tzf ~/backup-lab/exercice-backups/exercice.tar.gz
```

### Étape 4 — Modifier le fichier source

```bash
echo "Version 2" > ~/backup-lab/exercice-source/fichier.txt
```

### Étape 5 — Restaurer l'archive

```bash
mkdir -p ~/backup-lab/exercice-restore

tar -xzf ~/backup-lab/exercice-backups/exercice.tar.gz \
  -C ~/backup-lab/exercice-restore
```

### Étape 6 — Vérifier le résultat

```bash
cat ~/backup-lab/exercice-source/fichier.txt
cat ~/backup-lab/exercice-restore/exercice-source/fichier.txt
```

Résultat attendu :

```text
Fichier source :
Version 2

Fichier restauré :
Version 1
```

Cet exercice démontre l'intérêt de conserver une version antérieure. Il ne teste pas encore la protection contre la perte du disque qui contient simultanément la source et la sauvegarde.

## 32. Travaux pratiques

### TP 1 — Créer une archive de documents

**Objectif :** créer et extraire une archive tar.

Réaliser les étapes suivantes :

1. Créer un répertoire de laboratoire.
2. Générer plusieurs fichiers.
3. Créer une archive gzip.
4. Lister le contenu de l'archive.
5. Calculer une somme SHA-256.
6. Restaurer dans un nouveau répertoire.
7. Comparer les fichiers originaux et restaurés.
8. Rédiger les commandes utilisées.

Livrable : une procédure accompagnée des résultats de vérification.

### TP 2 — Comparer copie et sauvegarde versionnée

**Objectif :** comprendre la différence entre une copie et un historique.

1. Copier un dossier avec `rsync`.
2. Modifier un fichier source.
3. Refaire la copie.
4. Observer le contenu de la destination.
5. Réaliser une sauvegarde Restic.
6. Modifier le fichier.
7. Créer un nouveau snapshot.
8. Restaurer l'ancienne version de test.
9. Comparer les résultats.

Livrable : un tableau indiquant les avantages et les limites de chaque méthode.

### TP 3 — Restaurer avec Restic

**Objectif :** récupérer des données depuis un snapshot.

1. Créer le dépôt.
2. Initialiser le dépôt.
3. Créer une sauvegarde.
4. Modifier les fichiers.
5. Créer une seconde sauvegarde.
6. Lister les snapshots.
7. Restaurer un état antérieur.
8. Vérifier le contenu.
9. Exécuter `restic check`.
10. Consigner les résultats.

Livrable : la procédure de sauvegarde et de restauration avec les identifiants des snapshots réellement créés.

### TP 4 — Sauvegarder un dossier Windows

**Objectif :** copier et vérifier des données sous Windows.

1. Créer un dossier de test.
2. Créer plusieurs fichiers.
3. Copier les données vers une destination distincte.
4. Modifier un fichier original.
5. Comparer les versions.
6. Créer un second jeu de fichiers sauvegardés.
7. Restaurer dans une autre destination.
8. Vérifier le contenu.
9. Documenter les limites de la méthode utilisée.

Livrable : un rapport expliquant ce que la copie permet et ne permet pas.

### TP 5 — Définir une politique de sauvegarde

**Objectif :** construire une politique adaptée aux besoins d'un service.

Pour chaque type de données, préciser :

- Le propriétaire.
- La criticité.
- La fréquence.
- Le type de sauvegarde.
- La destination.
- La rétention.
- Le chiffrement.
- Les contrôles d'intégrité.
- Le RPO.
- Le RTO.
- La fréquence des tests de restauration.

Livrable : un tableau validé et suffisamment clair pour être utilisé par une équipe d'exploitation.

### TP 6 — Tester une restauration complète

**Objectif :** déterminer si la méthode retenue permet de récupérer les données.

1. Créer un jeu de données connu.
2. Le sauvegarder.
3. Simuler la perte de la copie de travail dans le laboratoire.
4. Restaurer dans un emplacement distinct.
5. Vérifier le contenu.
6. Mesurer la durée.
7. Comparer le résultat aux objectifs.
8. Documenter les écarts.

Livrable : un compte rendu de test de restauration.

## 33. Exercices d'application avec corrections

### Exercice 1 — Sauvegarde ou synchronisation ?

Un administrateur synchronise chaque soir le dossier source vers un disque externe. Un fichier est supprimé accidentellement avant la synchronisation suivante.

La destination peut-elle conserver une version antérieure du fichier ?

**Correction :**

Cela dépend de l'outil et de sa configuration. Une simple synchronisation peut supprimer ou remplacer la copie du fichier. Elle ne garantit pas un historique de versions.

Une solution versionnée, ou une stratégie qui conserve explicitement plusieurs états, est nécessaire pour protéger les anciennes versions.

### Exercice 2 — RPO

Une entreprise effectue une sauvegarde complète chaque soir à 23 h 00. Une perte de données survient le lendemain à 17 h 00.

Si aucune autre information n'est récupérable, quelle quantité de données temporelles peut être perdue ?

**Correction :**

La perte potentielle peut atteindre 18 heures de données, entre la dernière sauvegarde de 23 h 00 et l'incident survenu à 17 h 00 le lendemain.

Cette valeur représente la durée de données potentiellement perdues. La quantité réelle dépend des modifications effectuées et des autres mécanismes de récupération disponibles.

### Exercice 3 — RTO

Un service doit être rétabli dans un délai de trois heures. La restauration prend deux heures, les tests applicatifs 45 minutes et la remise en service 30 minutes.

L'objectif est-il respecté ?

**Correction :**

```text
Restauration :        2 h 00
Tests :               0 h 45
Remise en service :   0 h 30

Total :               3 h 15
```

Le délai total dépasse le RTO de 15 minutes. Il faut réduire le temps de reprise, revoir l'objectif avec les parties concernées ou améliorer la méthode de restauration.

### Exercice 4 — Pourquoi un RAID ne suffit-il pas ?

Un serveur contient quatre disques en RAID. Tous les fichiers sont accessibles après une panne d'un disque.

Est-il inutile de prévoir une sauvegarde ?

**Correction :**

Non. Le RAID peut améliorer la disponibilité face à certaines défaillances matérielles, mais il ne protège pas suffisamment contre les suppressions accidentelles, la corruption, les rançongiciels ou la destruction du serveur.

Une sauvegarde indépendante est nécessaire pour répondre à ces risques.

### Exercice 5 — Somme de contrôle

Un fichier d'archive possède le même nom que la veille. Sa taille n'a pas changé.

Peut-on conclure que son contenu est identique ?

**Correction :**

Non. Le nom et la taille ne prouvent pas l'identité du contenu. Un condensat tel que SHA-256 permet de comparer le fichier à une valeur de référence, dans les limites d'une procédure d'intégrité correcte.

### Exercice 6 — Mot de passe Restic perdu

Une organisation conserve un dépôt Restic chiffré, mais perd le secret nécessaire pour l'ouvrir.

La sauvegarde peut-elle être considérée comme récupérable ?

**Correction :**

Pas sans un autre mécanisme valide de récupération des clés ou du secret. Il faut prévoir la conservation sécurisée du secret et tester qu'il est disponible à partir de la procédure de reprise.

### Exercice 7 — Sauvegarde sur le même disque

Les données sont stockées dans `/srv/data` et la sauvegarde dans `/srv/data/backup`.

Cette solution protège-t-elle contre la panne physique du disque ?

**Correction :**

Non. Les données et la sauvegarde partagent le même disque physique. La perte de ce disque peut rendre les deux indisponibles.

### Exercice 8 — Sauvegarde réussie mais restauration échouée

Un outil indique que la sauvegarde s'est terminée avec succès, mais la restauration échoue à cause d'un fichier manquant.

Que faut-il améliorer ?

**Correction :**

Examiner les journaux, les erreurs de sauvegarde et la configuration du périmètre. Il faut ajouter des contrôles d'intégrité adaptés, des tests réguliers de restauration et des alertes sur les échecs ou les éléments manquants.

### Exercice 9 — Restauration d'un fichier

Un fichier important a été remplacé par une version incorrecte. Le reste du serveur fonctionne normalement.

Quelle stratégie est généralement préférable ?

**Correction :**

Si l'historique permet de récupérer le fichier seul, restaurer la version voulue dans un emplacement temporaire, vérifier son contenu, puis le remettre au bon endroit selon une procédure contrôlée.

La restauration complète du serveur serait inutilement risquée si seul un fichier est concerné.

### Exercice 10 — Protection contre les rançongiciels

Le compte utilisé par les serveurs de production peut supprimer les copies de sauvegarde.

Quelle mesure réduit ce risque ?

**Correction :**

Séparer les identités de sauvegarde et de production, limiter les privilèges de suppression, conserver une copie hors ligne ou immuable lorsque c'est adapté, protéger les secrets et tester régulièrement la restauration.

## 34. Projet de fin de niveau

### Concevoir une stratégie de sauvegarde pour une petite entreprise

L'entreprise fictive possède :

- Un serveur de fichiers Linux.
- Un serveur Windows contenant des documents.
- Une base de données métier.
- Une application interne.
- Un dépôt de sauvegarde local.
- Un stockage externe ou distant disponible pour une seconde copie.

Le but est de concevoir une stratégie adaptée aux besoins de récupération.

### Livrable A — Inventaire des données

Documenter pour chaque service :

- Les données protégées.
- Le propriétaire.
- La criticité.
- Les dépendances.
- La méthode de sauvegarde.
- Les besoins de conservation.
- Les risques principaux.

### Livrable B — Politique

Définir :

- La fréquence.
- Les types de sauvegarde.
- Les destinations.
- Le chiffrement.
- La séparation des identités.
- Le RPO.
- Le RTO.
- La rétention.
- La politique de suppression.
- La procédure de reprise.

### Livrable C — Mise en œuvre

Réaliser au moins :

- Une sauvegarde de fichiers avec tar.
- Une copie de laboratoire avec rsync.
- Une sauvegarde versionnée avec Restic.
- Une vérification d'intégrité.
- Une restauration dans un emplacement distinct.

Documenter les commandes réellement exécutées.

### Livrable D — Protection des sauvegardes

Expliquer :

- Comment les secrets sont conservés.
- Comment les copies sont protégées contre les suppressions.
- Comment les accès sont contrôlés.
- Comment une copie hors site est prévue.
- Comment les sauvegardes sont surveillées.
- Comment une restauration sera possible après une compromission.

### Livrable E — Test de reprise

Simuler une perte de fichier.

Le rapport devra contenir :

- Heure de début du test.
- Données concernées.
- Dernière version récupérable.
- Méthode de restauration.
- Durée mesurée.
- Résultat de la vérification.
- Écart par rapport aux objectifs.
- Action d'amélioration.

### Critères de réussite

Le projet est réussi lorsque l'apprenant démontre :

1. Qu'il sait choisir une méthode adaptée aux données.
2. Qu'il peut réaliser une sauvegarde.
3. Qu'il peut retrouver la bonne version.
4. Qu'il sait restaurer sans écraser les données originales pendant le test.
5. Qu'il vérifie le contenu récupéré.
6. Qu'il comprend les limites d'une copie sur le même support.
7. Qu'il sait protéger le secret de chiffrement.
8. Qu'il mesure la durée de restauration.
9. Qu'il documente les erreurs et les actions correctives.

## 35. Bonnes pratiques à retenir

### Préparation

- Identifier les données critiques.
- Définir les RPO et RTO.
- Choisir une fréquence adaptée.
- Prévoir la croissance du volume de données.
- Inclure les configurations et dépendances nécessaires.

### Exécution

- Vérifier les codes de retour.
- Lire les journaux des tâches.
- Surveiller la capacité du dépôt.
- Éviter les exécutions concurrentes.
- Tester les modifications de scripts.
- Contrôler les erreurs de lecture et d'écriture.

### Protection

- Séparer les sauvegardes de la production.
- Conserver une copie hors site.
- Envisager une copie hors ligne ou immuable.
- Chiffrer les données sensibles.
- Protéger les clés et mots de passe.
- Limiter les permissions de suppression.
- Contrôler les accès administratifs.

### Restauration

- Choisir la bonne version.
- Restaurer d'abord dans un emplacement de test si possible.
- Vérifier l'intégrité et le contenu.
- Contrôler les permissions nécessaires.
- Tester le fonctionnement applicatif.
- Mesurer la durée.
- Documenter les résultats.

### Amélioration continue

- Réaliser des tests régulièrement.
- Corriger les procédures défaillantes.
- Vérifier les contacts d'escalade.
- Contrôler les sauvegardes de configuration.
- Former les personnes responsables.
- Revoir périodiquement la politique de conservation.

## 36. Référence opérationnelle rapide

| Besoin | Commande |
|---|---|
| Créer une archive gzip | `tar -czf archive.tar.gz -C /source dossier` |
| Lister une archive | `tar -tzf archive.tar.gz` |
| Extraire une archive | `tar -xzf archive.tar.gz -C /destination` |
| Copier des fichiers | `rsync -a /source/ /destination/` |
| Simuler une synchronisation | `rsync -a --dry-run /source/ /destination/` |
| Calculer une somme SHA-256 | `sha256sum fichier` |
| Initialiser un dépôt Restic | `restic init` |
| Créer une sauvegarde Restic | `restic backup /chemin/source` |
| Lister les snapshots | `restic snapshots` |
| Examiner le contenu d'un snapshot | `restic ls latest` |
| Restaurer un snapshot | `restic restore latest --target /chemin/test` |
| Vérifier un dépôt Restic | `restic check` |
| Vérification approfondie des données | `restic check --read-data` |
| Lister les versions Windows | `wbadmin get versions` |
| Vérifier une opération Windows | `wbadmin get status` |
| Afficher le contenu d'un répertoire Linux | `find /chemin -type f -print` |

Les chemins et les identifiants doivent être adaptés au contexte. Les commandes de restauration et de suppression exigent une vérification particulière de leur cible.

## 37. Glossaire

**Archive :** ensemble de fichiers regroupés dans un seul fichier, éventuellement compressé.

**Copie :** duplication de données vers un autre emplacement.

**Chiffrement :** transformation des données pour qu'elles ne soient lisibles qu'avec les moyens de déchiffrement appropriés.

**Différentielle :** sauvegarde qui conserve les changements depuis une sauvegarde complète de référence dans le modèle classique.

**Incrémentale :** sauvegarde qui conserve les changements depuis un point de référence défini par le système employé.

**Immuabilité :** propriété d'une copie qui empêche sa modification ou sa suppression pendant une période définie, selon le mécanisme utilisé.

**Intégrité :** état dans lequel les données n'ont pas été modifiées de manière inattendue.

**Réplication :** maintien de copies de données sur plusieurs systèmes.

**Restauration :** opération de récupération de données à partir d'une sauvegarde.

**RPO :** objectif de point de récupération, exprimant la perte maximale de données acceptable en temps.

**RTO :** objectif de délai de reprise, exprimant le temps cible de rétablissement du service.

**Rétention :** durée et règles de conservation des versions de sauvegarde.

**Snapshot :** capture d'un état d'un volume, d'un système de fichiers ou d'une machine, selon le mécanisme employé.

**Somme de contrôle :** valeur calculée à partir du contenu d'un fichier pour permettre d'en vérifier l'intégrité par comparaison.

**Tar :** utilitaire de création et d'extraction d'archives.

**Restic :** outil de sauvegarde de fichiers disposant notamment de snapshots et de chiffrement.

**Rsync :** outil de copie et de synchronisation de fichiers.

**wbadmin :** outil en ligne de commande de sauvegarde et de récupération des versions Windows prises en charge.

## 38. Documentation officielle

### Restic

- Documentation principale : https://restic.readthedocs.io/
- Installation : https://restic.readthedocs.io/en/stable/020_installation.html
- Premiers pas : https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
- Création de sauvegardes : https://restic.readthedocs.io/en/stable/040_backup.html
- Restauration : https://restic.readthedocs.io/en/stable/050_restore.html
- Vérification du dépôt : https://restic.readthedocs.io/en/stable/045_working_with_repos.html
- Gestion des snapshots : https://restic.readthedocs.io/en/stable/060_forget.html

### Linux

- Manuel GNU tar : https://www.gnu.org/software/tar/manual/
- Manuel rsync : https://download.samba.org/pub/rsync/rsync.1
- Documentation cron du système : consulter les pages de manuel de la distribution.
- Manuel `sha256sum` : https://www.gnu.org/software/coreutils/manual/

### Windows

- Documentation générale de `wbadmin` : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin
- Commande de sauvegarde : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-backup
- Commande de restauration : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wbadmin-start-recovery
- Référence Windows Server Backup : https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-server-backup-command-reference

### Protection contre les rançongiciels

- Guide CISA StopRansomware : https://www.cisa.gov/stopransomware/ransomware-guide

Les procédures officielles évoluent. Avant de déployer une sauvegarde en production, vérifier les paramètres et les conditions correspondant au système d'exploitation, à la version de l'outil et à l'architecture utilisée.

## 39. Conclusion du niveau débutant

La sauvegarde est un mécanisme essentiel de protection des données, mais sa valeur dépend de la capacité réelle à restaurer les informations lorsqu'un problème survient.

Une copie simple peut convenir à certains usages, tandis qu'une sauvegarde versionnée est préférable pour conserver plusieurs états et récupérer des fichiers modifiés ou supprimés.

La stratégie doit également tenir compte des objectifs RPO et RTO, de la capacité de stockage, de la rétention, du chiffrement, des accès et des risques de destruction simultanée des données de production et des sauvegardes.

Les outils étudiés, comme tar, rsync, Restic et les mécanismes Windows, répondent à des besoins différents. Leur bonne utilisation demande de comprendre ce qu'ils sauvegardent réellement, les conditions de récupération et les limites de chaque méthode.

Le dernier principe est le plus important : **une sauvegarde n'est réellement utile que si les données peuvent être retrouvées, restaurées et vérifiées dans les conditions prévues.**

La suite du parcours approfondira les politiques de rétention avancées, la sauvegarde des bases de données, l'automatisation des tâches, les sauvegardes de machines virtuelles, la réplication, les dépôts distants, l'immuabilité et les stratégies de reprise après sinistre.