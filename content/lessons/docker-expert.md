# Sécurité des conteneurs

## 1. Présentation du cours

La conteneurisation permet de déployer des applications de manière reproductible, mais elle introduit également des enjeux de sécurité spécifiques.

Une application conteneurisée peut être compromise à cause d'une vulnérabilité dans son code, d'une dépendance obsolète, d'une image malveillante, d'un secret exposé, d'une configuration trop permissive ou d'une mauvaise protection du moteur Docker.

Le conteneur ne constitue pas une frontière de sécurité absolue. Les conteneurs Linux partagent le noyau de leur environnement d'exécution. Une vulnérabilité du noyau, une mauvaise configuration des permissions ou une exposition dangereuse du daemon Docker peut avoir des conséquences dépassant le seul conteneur.

La sécurité doit donc être considérée comme une chaîne complète :

```text
Code source
    |
    v
Dépendances applicatives
    |
    v
Dockerfile et environnement de build
    |
    v
Image construite
    |
    v
Registre d'images
    |
    v
Configuration de déploiement
    |
    v
Moteur Docker et système hôte
    |
    v
Exécution du conteneur
    |
    v
Surveillance et réponse aux incidents
```

Un conteneur correctement configuré ne compense pas automatiquement une image compromise. De même, une image sans vulnérabilité connue peut être dangereuse si elle reçoit des privilèges excessifs ou accède à des fichiers sensibles de l'hôte.

Ce cours approfondit la sécurité des conteneurs Docker en abordant les mécanismes d'isolation, la réduction des privilèges, la sécurité des images, la chaîne d'approvisionnement logicielle, les secrets, les réseaux, les limites de ressources, la surveillance et la réponse aux incidents.

Le contenu s'appuie notamment sur le guide NIST SP 800-190, les recommandations officielles Docker, le CIS Docker Benchmark et les travaux OWASP consacrés à la sécurité des conteneurs.

### 1.1. Objectifs pédagogiques

À la fin de ce cours, vous devrez savoir :

- Construire un modèle de menace pour une infrastructure conteneurisée.
- Identifier les principales surfaces d'attaque de Docker.
- Comprendre les namespaces, les cgroups, les capabilities Linux et les profils de sécurité.
- Distinguer l'utilisateur `root` du conteneur de l'utilisateur `root` de l'hôte.
- Réduire les privilèges d'un conteneur.
- Utiliser les options `--cap-drop`, `--read-only`, `--security-opt` et les limites de ressources.
- Sécuriser les Dockerfiles et les images de base.
- Réduire la surface d'attaque des images.
- Détecter les vulnérabilités des dépendances et des paquets système.
- Produire un inventaire logiciel, ou SBOM, et exploiter les informations de provenance.
- Protéger les secrets pendant la construction et l'exécution.
- Sécuriser les registres d'images et l'authentification.
- Comprendre les risques liés au socket Docker et au mode privilégié.
- Configurer des réseaux de conteneurs avec des accès minimaux.
- Protéger le système de fichiers et les données persistantes.
- Mettre en place des vérifications de sécurité dans CI/CD.
- Analyser des configurations dangereuses.
- Détecter des comportements anormaux et organiser une réponse aux incidents.
- Construire une checklist d'audit et de mise en production.

### 1.2. Prérequis

Il est recommandé de maîtriser :

- Les images et les conteneurs Docker.
- Les Dockerfiles.
- Docker Compose.
- Les volumes et les réseaux.
- Les registres d'images.
- Les commandes de diagnostic Docker.
- Les bases de Linux et des permissions Unix.
- Les notions d'utilisateur, de groupe, de processus et de port réseau.
- Les notions de CI/CD, de dépendances et de gestion des versions.

Les exemples utilisent Linux et Docker Engine lorsque les mécanismes dépendent du noyau Linux. Certaines options sont également présentées avec Docker Compose.

Sur Docker Desktop, les conteneurs Linux s'exécutent généralement dans un environnement Linux virtualisé ou intégré. Les comportements liés au noyau, aux permissions et aux mécanismes de confinement doivent être vérifiés dans l'environnement réellement utilisé.

### 1.3. Principe fondamental

La sécurité d'un conteneur repose sur plusieurs couches complémentaires :

1. La sécurité du code et des dépendances.
2. L'intégrité de l'image.
3. La sécurité du processus de construction.
4. Le contrôle de l'accès au registre.
5. La configuration des privilèges.
6. L'isolation réseau et système.
7. La limitation des ressources.
8. La protection des données et des secrets.
9. La sécurité du moteur et de l'hôte.
10. La surveillance et la réponse aux incidents.

Aucune de ces couches ne doit être considérée comme suffisante à elle seule.

## 2. Modèle de menace des conteneurs

Avant de choisir des options de sécurité, il faut identifier les ressources à protéger, les acteurs susceptibles de les compromettre et les conséquences possibles.

### 2.1. Les ressources à protéger

Dans une infrastructure Docker, les ressources sensibles comprennent notamment :

- Le système d'exploitation hôte.
- Le daemon Docker.
- Les fichiers du système hôte.
- Les données applicatives.
- Les volumes persistants.
- Les bases de données.
- Les clés privées et les jetons d'accès.
- Les identifiants des registres.
- Les images publiées.
- Les pipelines de construction.
- Les réseaux internes.
- Les journaux et les traces d'exécution.
- Les machines et services accessibles depuis les conteneurs.

Une compromission peut concerner une seule application ou s'étendre à plusieurs composants lorsque les autorisations et les réseaux sont insuffisamment segmentés.

### 2.2. Les principaux scénarios de menace

| Menace | Exemple | Conséquence possible |
|---|---|---|
| Image malveillante | Une image inconnue exécute du code non attendu. | Vol de secrets, exfiltration ou activité malveillante. |
| Dépendance vulnérable | Une bibliothèque contient une faille exploitable. | Compromission de l'application. |
| Conteneur trop privilégié | Un service fonctionne avec des permissions inutiles. | Augmentation de l'impact d'une compromission. |
| Accès excessif à l'hôte | Le conteneur monte des répertoires sensibles en écriture. | Modification ou destruction de fichiers hôtes. |
| Socket Docker exposé | Un conteneur accède à `/var/run/docker.sock`. | Contrôle potentiellement étendu de l'environnement Docker. |
| Secret exposé | Un jeton est incorporé dans une image. | Accès non autorisé à des services. |
| Réseau mal segmenté | Un conteneur compromis peut atteindre des bases de données sensibles. | Mouvement latéral et exfiltration. |
| Déni de service | Un processus consomme excessivement le CPU ou la mémoire. | Dégradation des autres services. |
| Fuite de données | Des données sensibles sont écrites dans les journaux. | Exposition d'informations confidentielles. |
| Compromission du registre | Un acteur remplace une image par un contenu malveillant. | Déploiement d'une version compromise. |

### 2.3. Exemple de propagation d'une attaque

Imaginons qu'une API soit compromise à la suite d'une vulnérabilité applicative.

Si le conteneur possède des privilèges limités, un système de fichiers en lecture seule et un accès réseau restreint, l'impact peut être contenu.

En revanche, si le conteneur :

- fonctionne avec des privilèges excessifs ;
- monte le système de fichiers hôte ;
- possède le socket Docker ;
- peut joindre toutes les bases de données ;
- dispose de secrets globaux ;

la compromission initiale peut devenir beaucoup plus grave.

```text
Vulnérabilité applicative
          |
          v
Compromission de l'API
          |
          v
Tentative d'exploitation
          |
     +----+----+
     |         |
     v         v
Isolation    Privilèges excessifs
correcte      et accès étendus
     |         |
     v         v
Impact       Accès possible à
limité       d'autres ressources
               |
               v
         Extension de l'incident
```

L'objectif d'une architecture sécurisée est de limiter la probabilité de compromission, puis de réduire l'impact si une couche de protection échoue.

### 2.4. Définir un périmètre de sécurité

Avant de déployer une application, documentez :

- Les données qu'elle traite.
- Les services auxquels elle doit accéder.
- Les ports réellement nécessaires.
- Les fichiers qu'elle doit lire ou modifier.
- Les secrets qui lui sont destinés.
- Les permissions système nécessaires.
- Les ressources maximales qu'elle peut consommer.
- Les événements qui doivent déclencher une alerte.
- Les conditions dans lesquelles le conteneur doit être arrêté ou remplacé.

Cette définition constitue une base pour les contrôles du Dockerfile, de Compose et du moteur.

## 3. Comprendre les mécanismes d'isolation Linux

Docker utilise plusieurs mécanismes du système d'exploitation pour isoler les processus et contrôler leurs ressources.

### 3.1. Les namespaces

Les namespaces Linux permettent de fournir des vues isolées de certaines ressources du système.

Ils contribuent notamment à séparer :

- Les identifiants de processus.
- Les interfaces et paramètres réseau.
- Les points de montage.
- Les noms d'hôte.
- Les identifiants d'utilisateurs et de groupes.
- Certaines ressources interprocessus.

Un processus dans un conteneur peut ainsi voir une vue différente du système par rapport aux processus de l'hôte.

Les namespaces ne constituent toutefois pas une virtualisation complète du noyau. Ils reposent sur les mécanismes du noyau hôte.

### 3.2. Les cgroups

Les *control groups*, ou cgroups, permettent notamment d'organiser et de contrôler l'utilisation de certaines ressources par les groupes de processus.

Ils sont utilisés pour des besoins tels que :

- Le contrôle de la mémoire.
- Les limites et priorités CPU.
- Le suivi de certaines consommations.
- La gestion de certaines ressources du système.

Un conteneur sans limites adaptées peut consommer des ressources importantes et affecter d'autres services.

Les cgroups aident à limiter les effets d'un processus trop gourmand, mais ne remplacent pas la surveillance et le dimensionnement.

### 3.3. Les capabilities Linux

Linux divise certains privilèges historiquement regroupés dans le compte `root` en capacités distinctes, appelées *capabilities*.

Exemples :

- `NET_BIND_SERVICE` : autorise certaines opérations de liaison à des ports privilégiés.
- `NET_ADMIN` : autorise certaines opérations d'administration réseau.
- `SYS_ADMIN` : capacité très étendue liée à de nombreuses opérations d'administration système.
- `NET_RAW` : autorise notamment certaines opérations utilisant des sockets bruts.
- `CHOWN` : autorise certains changements de propriétaire de fichiers.

Un conteneur ne devrait pas recevoir toutes les capabilities sans justification.

### 3.4. Seccomp

Seccomp est un mécanisme du noyau Linux permettant de restreindre les appels système disponibles.

Docker utilise normalement un profil seccomp par défaut qui bloque certains appels jugés dangereux ou inutiles dans la configuration standard.

Un profil personnalisé peut restreindre davantage les appels système, mais il doit être conçu et testé avec soin.

Une restriction incorrecte peut empêcher une application légitime de fonctionner.

### 3.5. AppArmor et SELinux

AppArmor et SELinux sont des mécanismes de contrôle d'accès obligatoires, ou MAC, qui permettent d'appliquer des politiques de sécurité supplémentaires.

Selon le système hôte et sa configuration, ils peuvent limiter les opérations qu'un processus est autorisé à réaliser.

Docker peut utiliser des profils de sécurité associés à ces mécanismes.

Il faut éviter de désactiver AppArmor ou SELinux pour faire fonctionner rapidement un conteneur sans déterminer d'abord la cause du refus d'accès.

### 3.6. Défense en profondeur

```text
+--------------------------------------+
| Application et dépendances           |
+--------------------------------------+
| Utilisateur non privilégié           |
+--------------------------------------+
| Capabilities limitées                |
+--------------------------------------+
| Seccomp et profil MAC                |
+--------------------------------------+
| Namespaces et cgroups                |
+--------------------------------------+
| Noyau et système hôte                |
+--------------------------------------+
| Contrôle physique ou cloud de l'hôte |
+--------------------------------------+
```

Chaque mécanisme apporte une protection différente.

Les conteneurs doivent être configurés pour utiliser les protections disponibles, en tenant compte de leurs besoins réels.

## 4. Conteneur, root et privilèges de l'hôte

### 4.1. Pourquoi l'utilisateur root du conteneur est-il important ?

Dans de nombreuses images, le processus principal démarre par défaut en tant qu'utilisateur `root` à l'intérieur du conteneur.

Cet utilisateur dispose de privilèges importants dans l'espace de noms du conteneur, même si certaines capacités sont limitées par Docker et par le noyau.

L'isolation réduit les conséquences de ces privilèges, mais elle ne justifie pas de les accorder sans nécessité.

Si une vulnérabilité permet à un attaquant de contrôler le processus applicatif, ses permissions déterminent les actions que l'attaquant peut tenter d'effectuer.

### 4.2. Créer un utilisateur applicatif dans le Dockerfile

Exemple :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser app.py .

USER appuser

CMD ["python", "app.py"]
```

L'instruction `USER` indique que le processus principal est lancé avec l'utilisateur `appuser`, sous réserve des options et de la configuration d'exécution.

L'utilisateur et le groupe doivent disposer des permissions nécessaires aux fichiers de l'application.

### 4.3. Vérifier l'utilisateur utilisé

Après le démarrage :

```bash
docker inspect --format '{{.Config.User}}' mon-conteneur
```

Cette commande affiche l'utilisateur défini dans la configuration du conteneur.

Si la valeur est vide, cela peut indiquer qu'aucun utilisateur explicite n'a été défini dans la configuration du conteneur. Le comportement réel dépend alors notamment de l'image et de son processus de démarrage.

Pour vérifier l'utilisateur du processus en cours dans un conteneur contenant les outils nécessaires :

```bash
docker exec mon-conteneur id
```

Vérifiez le résultat réel plutôt que de supposer qu'un Dockerfile utilise toujours un utilisateur non privilégié.

### 4.4. Attention aux permissions des fichiers

Passer de `root` à un utilisateur non privilégié peut révéler des problèmes de permissions.

Par exemple, un dossier créé par `root` peut empêcher l'application d'écrire les fichiers dont elle a besoin.

Une solution consiste à attribuer les fichiers au bon utilisateur pendant la construction :

```dockerfile
COPY --chown=appuser:appuser app.py .
```

Il est préférable de corriger les permissions attendues plutôt que de lancer toute l'application avec des privilèges plus élevés.

### 4.5. Ne pas confondre root dans le conteneur et root sur l'hôte

La relation entre l'identité du conteneur et les identifiants de l'hôte dépend notamment des namespaces utilisateurs et de la configuration de l'environnement.

Sans remappage particulier, le compte `root` dans un conteneur classique peut correspondre à l'identifiant utilisateur zéro de l'hôte dans certains contextes. Les mécanismes de confinement limitent toutefois les permissions et les ressources accessibles.

La distinction ne doit donc pas être interprétée comme une garantie d'absence de risque.

La réduction des privilèges et, lorsque c'est approprié, le mode rootless ou le remappage des namespaces utilisateurs améliorent la défense.

## 5. Rootless, userns-remap et sécurité du daemon

### 5.1. Le mode rootless

Le mode rootless permet d'exécuter le daemon Docker et les conteneurs sans que le daemon ait besoin de fonctionner avec les privilèges root classiques de l'hôte.

Cela réduit certaines possibilités d'impact en cas de vulnérabilité du daemon ou du runtime.

Le mode rootless nécessite une configuration compatible et possède des limites opérationnelles qui doivent être évaluées selon l'application et l'environnement.

Documentation officielle :

https://docs.docker.com/engine/security/rootless/

### 5.2. Vérifier les options de sécurité

```bash
docker info
```

Selon la configuration, les informations affichées peuvent inclure des options de sécurité comme le mode rootless ou les mécanismes de confinement disponibles.

Pour n'examiner que les options de sécurité retournées par le moteur :

```bash
docker info --format '{{json .SecurityOptions}}'
```

Interprétez la sortie selon la version du moteur et les paramètres réellement activés.

### 5.3. Le remappage des namespaces utilisateurs

L'option `userns-remap` permet de remapper les identifiants utilisateurs et groupes des conteneurs vers des identifiants moins privilégiés sur l'hôte.

Cela peut réduire l'impact de certaines actions réalisées en tant que root à l'intérieur du conteneur.

Le remappage nécessite une configuration correcte des plages UID et GID et peut compliquer la gestion des bind mounts ou de certains volumes.

Documentation officielle :

https://docs.docker.com/engine/security/userns-remap/

### 5.4. Rootless et userns-remap : différence

| Mécanisme | Objectif principal |
|---|---|
| Rootless | Exécuter le daemon et les conteneurs sans privilèges root classiques sur l'hôte. |
| `userns-remap` | Mapper les identifiants des utilisateurs du conteneur vers des identifiants non privilégiés de l'hôte, tandis que le daemon peut rester privilégié. |

Le choix dépend du support de l'environnement et des contraintes de fonctionnement.

Ces mécanismes complètent les bonnes pratiques de configuration des conteneurs ; ils ne dispensent pas de contrôler les capacités, les montages et le réseau.

## 6. Protéger le daemon Docker

### 6.1. Pourquoi le daemon est-il sensible ?

Le daemon Docker contrôle la création et l'exécution des conteneurs.

Il peut également gérer les montages de fichiers hôtes, les réseaux, les volumes et d'autres opérations importantes.

Un utilisateur qui peut contrôler le daemon peut potentiellement demander des opérations qui compromettent l'isolation prévue.

L'accès au daemon doit donc être traité comme un accès privilégié à l'infrastructure, et non comme une permission ordinaire.

### 6.2. Le socket Docker

Sur de nombreuses installations Linux, la CLI communique avec le daemon à travers le socket :

```text
/var/run/docker.sock
```

Donner ce socket à un conteneur signifie lui donner un accès à l'API du daemon, selon les permissions et les règles d'autorisation.

Le montage du socket est souvent dangereux :

```bash
docker run \
  -v /var/run/docker.sock:/var/run/docker.sock \
  image-inconnue
```

Il ne faut pas utiliser ce montage sans connaître le besoin exact.

Un conteneur disposant d'un accès étendu au daemon peut être capable de demander la création d'autres conteneurs, de monter des répertoires de l'hôte ou de lancer des processus avec des privilèges importants.

### 6.3. Éviter le socket Docker dans les conteneurs applicatifs

Une application web ordinaire n'a généralement pas besoin d'accéder au socket Docker.

Si un outil de déploiement doit contrôler Docker, étudiez plutôt :

- Un processus de déploiement séparé.
- Un compte dédié avec des droits limités.
- Un environnement de construction isolé.
- Un endpoint d'administration protégé.
- Un accès distant sécurisé avec SSH ou TLS selon le modèle retenu.

La meilleure protection est souvent de ne pas exposer le socket au conteneur lorsque cette dépendance n'est pas nécessaire.

### 6.4. Sécuriser l'accès distant au daemon

Évitez d'exposer directement le daemon Docker sur un endpoint réseau non protégé.

La documentation Docker décrit notamment l'utilisation de SSH et de TLS pour protéger les communications avec le daemon distant :

https://docs.docker.com/engine/security/protect-access/

Les certificats et les clés privées associés à cet accès doivent être protégés avec le même soin que les identifiants administratifs.

Le chiffrement des communications ne suffit pas à lui seul : les clients autorisés peuvent demander des opérations très puissantes.

### 6.5. Contrôler les utilisateurs autorisés

Sur Linux, l'accès au socket Docker est souvent associé à un groupe dédié.

L'appartenance à ce groupe peut donner des possibilités comparables à un accès très privilégié au système, selon la configuration.

Ne considérez donc pas l'ajout d'un utilisateur à ce groupe comme une simple permission d'utilisation d'un outil.

Documentez les autorisations, limitez les membres et privilégiez des environnements d'exécution moins privilégiés lorsque cela est possible.

## 7. Modes privilégiés et capabilities

### 7.1. Éviter `--privileged`

L'option :

```bash
docker run --privileged image
```

accorde des capacités supplémentaires très importantes au conteneur et modifie plusieurs protections usuelles.

Elle peut notamment donner accès à des ressources ou à des périphériques normalement restreints.

Un conteneur privilégié ne doit pas être considéré comme un conteneur applicatif ordinaire avec une petite permission supplémentaire.

**Bonne pratique : évitez `--privileged` en production, sauf besoin exceptionnel documenté et évalué.**

### 7.2. Pourquoi `--privileged` est-il dangereux ?

Une compromission dans un conteneur privilégié peut avoir un impact plus élevé.

Selon les autres paramètres, le conteneur peut disposer d'un accès étendu aux périphériques, aux opérations système ou à des interfaces qui ne sont normalement pas disponibles.

Les protections par namespaces et capabilities sont alors réduites pour certaines catégories d'opérations.

### 7.3. Retirer des capabilities

Exemple :

```bash
docker run --rm \
  --cap-drop ALL \
  alpine:3.22 \
  sh -c 'id; echo "Test"'
```

Cette commande illustre le retrait des capabilities Linux du conteneur.

Selon l'application, certaines capabilities peuvent être nécessaires. Il faut donc tester la configuration avant de la déployer.

### 7.4. Ajouter une capability uniquement si nécessaire

Supposons qu'un composant de diagnostic doive administrer une interface réseau.

Une capability comme `NET_ADMIN` peut être nécessaire, mais elle doit être attribuée uniquement au service concerné, avec un objectif documenté.

```bash
docker run --rm \
  --cap-add NET_ADMIN \
  image-de-diagnostic
```

L'exemple ne signifie pas que `NET_ADMIN` doit être accordée aux conteneurs applicatifs ordinaires.

Ne remplacez pas une analyse de permission par l'ajout systématique de capabilities.

### 7.5. Exemple de configuration de sécurité Compose

```yaml
services:
  api:
    image: exemple-api:1.0

    user: "10001:10001"

    cap_drop:
      - ALL

    security_opt:
      - no-new-privileges:true

    read_only: true

    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m

    pids_limit: 100

    mem_limit: 256m

    cpus: 1.0
```

Cette configuration illustre plusieurs protections :

- `user` définit une identité non privilégiée.
- `cap_drop` retire les capabilities.
- `no-new-privileges` empêche le processus d'acquérir de nouveaux privilèges par certains mécanismes.
- `read_only` rend le système de fichiers racine du conteneur en lecture seule.
- `tmpfs` fournit un espace temporaire destiné aux fichiers qui doivent être écrits.
- `pids_limit` limite le nombre de processus ou de tâches.
- `mem_limit` définit une limite de mémoire.
- `cpus` définit une limite de CPU selon la prise en charge de l'environnement Compose utilisé.

Cette configuration doit être adaptée et testée avant déploiement : un service qui écrit dans des répertoires non prévus par la configuration peut ne plus démarrer.

### 7.6. Interdiction d'escalade de privilèges

La commande suivante utilise l'option `no-new-privileges` :

```bash
docker run --rm \
  --security-opt no-new-privileges=true \
  alpine:3.22 \
  sh -c 'id'
```

Cette option empêche certains mécanismes d'acquisition de nouveaux privilèges, notamment par des exécutables setuid ou des mécanismes similaires.

Elle ne remplace pas les autres protections d'accès.

### 7.7. Retrait de capabilities et compatibilité

Retirer toutes les capabilities est un objectif de durcissement utile lorsque l'application n'en a besoin d'aucune.

Il ne faut cependant pas supposer que toutes les applications fonctionneront dans cette configuration.

Certaines applications réseau, outils système ou agents d'infrastructure peuvent requérir une capacité précise.

Procédure recommandée :

1. Tester l'application avec les capabilities retirées.
2. Analyser les opérations refusées.
3. Identifier la capacité réellement nécessaire.
4. Ajouter uniquement cette capacité si le besoin est justifié.
5. Documenter l'exception.
6. Vérifier que les autres protections restent actives.

## 8. Seccomp, AppArmor et SELinux

### 8.1. Seccomp par défaut

Docker utilise normalement un profil seccomp par défaut lorsque le système prend en charge ce mécanisme.

Ce profil restreint certains appels système et participe à la réduction de la surface d'attaque.

Documentation :

https://docs.docker.com/engine/security/seccomp/

Évitez de désactiver seccomp uniquement pour résoudre un problème de compatibilité sans comprendre la fonction concernée.

### 8.2. Profil seccomp personnalisé

Un profil personnalisé peut être utilisé lorsque l'application a besoin d'une politique plus restrictive.

Exemple de forme de commande :

```bash
docker run --rm \
  --security-opt seccomp=/chemin/vers/profil-seccomp.json \
  mon-image:1.0
```

Le fichier doit être présent à l'endroit attendu par la CLI, et le format du profil doit être compatible avec l'environnement utilisé.

Un profil trop restrictif peut empêcher une application de fonctionner correctement. Un profil trop permissif peut offrir peu de protection supplémentaire.

### 8.3. Ne pas utiliser `seccomp=unconfined` par facilité

Désactiver le profil seccomp peut supprimer une couche de protection.

Avant de le faire, identifiez précisément l'appel système refusé et déterminez s'il peut être autorisé de manière ciblée dans un profil approprié.

La configuration par défaut constitue généralement un meilleur point de départ qu'une politique entièrement désactivée.

### 8.4. AppArmor

Sur les systèmes compatibles, Docker peut utiliser un profil AppArmor par défaut pour les conteneurs.

La configuration et les profils doivent être examinés lorsqu'une application a besoin d'un accès inhabituel.

Documentation :

https://docs.docker.com/engine/security/apparmor/

Évitez de définir un profil non confiné sans justification.

### 8.5. SELinux

Sur les systèmes utilisant SELinux, les politiques peuvent restreindre les accès aux fichiers, aux processus et à certains objets du système.

Les bind mounts et les volumes peuvent nécessiter une configuration de contexte compatible.

Un refus SELinux ne signifie pas automatiquement qu'il faut désactiver SELinux. Il faut identifier l'accès refusé et corriger les permissions ou la politique conformément aux exigences de sécurité.

### 8.6. Défense en profondeur

Les mécanismes suivants sont complémentaires :

```text
Utilisateur non privilégié
          |
          v
Capabilities minimales
          |
          v
no-new-privileges
          |
          v
Seccomp
          |
          v
AppArmor ou SELinux
          |
          v
Namespaces et cgroups
          |
          v
Noyau maintenu à jour
```

Une configuration de sécurité efficace combine plusieurs protections au lieu de dépendre d'une seule.

## 9. Sécuriser le système de fichiers

### 9.1. Pourquoi le système de fichiers est-il important ?

Un attaquant ayant pris le contrôle d'un processus applicatif peut essayer de modifier des fichiers, d'installer des outils, de persister ou de collecter des informations sensibles.

Le système de fichiers doit être aussi restrictif que possible.

### 9.2. Rendre le système de fichiers racine en lecture seule

Avec Docker :

```bash
docker run --rm \
  --read-only \
  mon-image:1.0
```

Cette option rend le système de fichiers racine du conteneur en lecture seule.

Elle ne rend pas automatiquement les volumes ou les systèmes temporaires en lecture seule. Il faut examiner les montages additionnels.

### 9.3. Prévoir les espaces temporaires

Certaines applications doivent écrire dans `/tmp`.

Un système de fichiers racine en lecture seule peut être combiné avec un montage temporaire en mémoire :

```bash
docker run --rm \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  mon-image:1.0
```

Cette configuration est un exemple de départ et doit être testée avec l'application réelle.

Les options de montage doivent être adaptées au système et aux besoins du processus.

### 9.4. Écriture dans les répertoires applicatifs

Si l'application doit écrire dans un dossier de travail, il faut déterminer si cette écriture est réellement nécessaire.

Options possibles :

- Utiliser un volume dédié.
- Monter un répertoire en lecture seule lorsque seules des lectures sont nécessaires.
- Prévoir un répertoire temporaire limité.
- Modifier l'application afin qu'elle écrive les journaux sur la sortie standard.
- Séparer les données persistantes du code applicatif.

Évitez d'autoriser l'écriture dans tout le système de fichiers uniquement parce qu'un composant écrit actuellement à plusieurs endroits.

### 9.5. Vérifier la configuration en lecture seule

Après démarrage :

```bash
docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' mon-conteneur
```

Cette commande affiche la valeur associée au paramètre de système de fichiers racine en lecture seule.

Vérifiez également les montages :

```bash
docker inspect --format '{{json .Mounts}}' mon-conteneur
```

La sortie permet d'examiner les volumes et les chemins montés dans le conteneur.

### 9.6. Éviter les montages sensibles

Évitez de monter inutilement des chemins tels que :

```text
/
/etc
/root
/var/run
/var/run/docker.sock
```

Le risque exact dépend du chemin, du mode de montage, de l'utilisateur et des permissions, mais ces ressources peuvent donner accès à des informations ou à des capacités importantes de l'hôte.

Un montage doit être justifié par un besoin réel.

### 9.7. Montage en lecture seule

Exemple :

```bash
docker run --rm \
  --mount type=bind,source=/srv/config-app,target=/app/config,readonly \
  mon-image:1.0
```

Cette forme monte le répertoire indiqué en lecture seule.

Le chemin source doit exister et le processus doit disposer des droits de lecture appropriés.

La syntaxe de chemin est à adapter au système hôte.

### 9.8. Attention aux volumes persistants

Un volume conserve potentiellement des données après la suppression du conteneur.

Cela signifie que les fichiers sensibles qu'il contient peuvent aussi survivre à la fin de vie du conteneur.

Il faut donc gérer :

- Les permissions du volume.
- Les sauvegardes.
- Le chiffrement lorsque nécessaire.
- Les procédures de suppression.
- Les droits d'accès des différents services.
- Les données présentes dans les snapshots et les sauvegardes.

La persistance facilite la disponibilité des données, mais elle crée également des responsabilités de sécurité supplémentaires.

## 10. Limiter les ressources et prévenir les dénis de service

### 10.1. Pourquoi fixer des limites ?

Un conteneur compromis ou mal conçu peut consommer excessivement du CPU, de la mémoire ou des processus.

Dans un environnement partagé, cette consommation peut affecter les autres services.

Les limites de ressources réduisent certains risques de dégradation, sans remplacer l'analyse de la charge et de la capacité.

### 10.2. Limite de mémoire

Exemple :

```bash
docker run --rm \
  --memory=256m \
  mon-image:1.0
```

Cette option définit une limite de mémoire pour le conteneur.

Le comportement précis en cas de dépassement dépend des mécanismes du noyau et de la configuration. Un dépassement peut entraîner l'arrêt d'un processus par le mécanisme OOM du système.

Il faut donc dimensionner la limite en fonction des besoins réels et surveiller les événements de dépassement.

### 10.3. Limite CPU

Exemple :

```bash
docker run --rm \
  --cpus=1.0 \
  mon-image:1.0
```

Cette configuration limite la consommation CPU du conteneur selon la politique du moteur.

Une limite trop faible peut rendre l'application lente et produire des délais d'attente.

### 10.4. Limite du nombre de processus

```bash
docker run --rm \
  --pids-limit=100 \
  mon-image:1.0
```

Cette option limite le nombre de processus ou tâches dans le conteneur.

Elle peut aider à contenir certains scénarios de création excessive de processus.

La valeur doit être adaptée à l'application, notamment si elle utilise de nombreux workers ou des traitements parallèles.

### 10.5. Limites d'entrées-sorties et limites complémentaires

Selon l'environnement et le stockage utilisé, d'autres contrôles de ressources peuvent être pertinents.

Le dimensionnement peut inclure :

- Le nombre de processus.
- Le CPU.
- La mémoire.
- L'espace disque.
- Les opérations d'entrée-sortie.
- Le nombre de connexions.
- Les files d'attente applicatives.

Toutes les limites disponibles ne sont pas prises en charge de la même manière sur tous les systèmes et pilotes de stockage.

### 10.6. Exemple Compose avec des limites

```yaml
services:
  api:
    image: exemple-api:1.0
    mem_limit: 256m
    cpus: 1.0
    pids_limit: 100
```

Cette configuration doit être vérifiée avec la version de Docker Compose et le moteur utilisés.

Les besoins des applications varient. Une limite arbitraire très faible peut provoquer des pannes ; une limite trop élevée peut ne pas contenir efficacement l'impact d'un processus défectueux.

### 10.7. Surveiller les consommations

```bash
docker stats
```

Pour un conteneur particulier :

```bash
docker stats mon-conteneur
```

Les informations de consommation doivent être interprétées avec les métriques du système hôte et les indicateurs de fonctionnement de l'application.

Une consommation inhabituelle doit déclencher une investigation lorsqu'elle s'écarte du comportement attendu.

## 11. Sécuriser les images de conteneurs

La sécurité d'une image commence avant le lancement du conteneur.

Une image peut contenir des dépendances vulnérables, des outils inutiles, des secrets ou des fichiers qui facilitent une attaque.

### 11.1. Utiliser une image de base fiable

Avant de choisir une image de base, vérifiez :

- Son origine.
- Son propriétaire.
- Sa documentation.
- Son cycle de maintenance.
- Les versions de paquets qu'elle contient.
- Sa compatibilité avec le projet.
- Les mises à jour de sécurité.
- Les architectures prises en charge.

Évitez de construire la production à partir d'une image inconnue dont la provenance n'est pas vérifiable.

### 11.2. Éviter les images inutilement volumineuses

Une image contenant de nombreux outils et paquets peut élargir la surface d'attaque.

Une image allégée peut réduire les composants installés et simplifier certains contrôles.

Cette optimisation doit cependant préserver la compatibilité, la maintenance et les possibilités de diagnostic nécessaires.

### 11.3. Utiliser des constructions multi-stage

Les constructions multi-stage permettent de séparer les outils de construction des fichiers nécessaires à l'exécution.

Exemple conceptuel :

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/* \
    && useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser app.py .

USER appuser

CMD ["python", "app.py"]
```

Cette illustration suppose que `requirements.txt` contient les dépendances appropriées et que celles-ci peuvent être construites ou téléchargées dans l'environnement choisi.

Dans le stage final, seuls les éléments nécessaires à l'exécution sont copiés depuis le stage de construction.

Selon les besoins, il peut être nécessaire d'ajuster la compilation, les paquets système et les dépendances natives.

Documentation Docker :

https://docs.docker.com/build/building/multi-stage/

### 11.4. Éviter les outils inutiles dans l'image finale

Les compilateurs, outils de diagnostic temporaires et composants exclusivement nécessaires au build peuvent être conservés uniquement dans le stage de construction lorsque l'architecture le permet.

Cela peut réduire la surface d'attaque de l'image finale.

Il ne faut toutefois pas supprimer aveuglément les éléments nécessaires au fonctionnement, à la maintenance ou à l'observation du service.

### 11.5. Contrôler les paquets installés

Une image peut contenir des bibliothèques vulnérables même si l'application ne les utilise pas directement.

Il faut prendre en compte :

- Les dépendances déclarées.
- Les dépendances transitives.
- Les paquets système.
- Les bibliothèques natives.
- Les composants de construction conservés dans l'image finale.

Un scan de vulnérabilités peut aider à identifier les composants à corriger.

### 11.6. Ne pas utiliser systématiquement `latest`

Exemple à éviter pour une base de production non contrôlée :

```dockerfile
FROM python:latest
```

Préférez une référence explicitement choisie et maintenue :

```dockerfile
FROM python:3.12-slim
```

Pour un environnement nécessitant une provenance et une identité strictes, une référence par digest peut être utilisée.

Exemple de forme :

```dockerfile
FROM python:3.12-slim@sha256:DIGEST_COMPLET
```

Le digest doit être obtenu à partir d'une source fiable et correspondre à l'image attendue.

Une référence par digest favorise l'identification exacte du contenu, mais elle ne dispense pas d'un processus de mise à jour : un digest ancien peut toujours correspondre à une image vulnérable.

### 11.7. Politique de mise à jour

Une image doit être reconstruite et réévaluée lorsque :

- Une vulnérabilité importante est détectée.
- Une version de dépendance atteint sa fin de support.
- Une nouvelle image de base corrigée est disponible.
- Une exigence de conformité évolue.
- Le composant utilisé n'est plus adapté à l'usage prévu.

Une image qui fonctionne ne doit pas être considérée comme définitivement sûre.

## 12. Gérer les vulnérabilités et les dépendances

### 12.1. Comprendre un scan de vulnérabilités

Un scanner compare les composants détectés dans une image à des informations de vulnérabilités connues.

Il peut identifier :

- Des vulnérabilités dans des bibliothèques.
- Des paquets système obsolètes.
- Des versions exposées à des CVE.
- Certaines erreurs de configuration.
- Des composants dont l'identification est incertaine.

Le résultat dépend notamment des données disponibles, de la capacité d'identification des paquets et de la date de l'analyse.

### 12.2. Les limites d'un scan

Un scan sans vulnérabilité connue ne prouve pas qu'une image est sûre.

Il ne garantit pas :

- L'absence de vulnérabilités inconnues.
- L'absence de code malveillant.
- La sécurité des permissions du conteneur.
- L'absence de secrets exposés.
- La sécurité des services externes.
- La bonne configuration du réseau.
- La qualité du code applicatif.

Le scan est donc un contrôle complémentaire.

### 12.3. Exemple avec Docker Scout

Docker Scout peut analyser la composition d'une image et identifier des vulnérabilités connues dans les composants détectés.

Selon l'environnement et l'installation, des commandes peuvent inclure :

```bash
docker scout quickview mon-image:1.0
```

Pour examiner les vulnérabilités :

```bash
docker scout cves mon-image:1.0
```

Pour générer ou consulter un inventaire logiciel :

```bash
docker scout sbom mon-image:1.0
```

Ces commandes supposent que Docker Scout est disponible dans l'environnement.

Documentation officielle :

https://docs.docker.com/scout/

### 12.4. Prioriser les corrections

Toutes les vulnérabilités ne présentent pas le même risque opérationnel.

Pour prioriser, examinez notamment :

- La sévérité publiée.
- L'exploitabilité dans le contexte réel.
- L'exposition du service.
- Les privilèges du conteneur.
- Les données accessibles.
- L'existence d'un correctif.
- La disponibilité d'une mesure compensatoire.
- Le rôle de la dépendance dans l'application.

Il est utile de définir des objectifs de correction selon le niveau de risque plutôt que d'utiliser un seuil unique sans analyse.

### 12.5. Mettre à jour sans casser l'application

Une mise à jour de base ou de dépendance peut introduire un changement de comportement.

Le processus devrait inclure :

1. Identification de la vulnérabilité.
2. Sélection d'une version corrigée.
3. Mise à jour du Dockerfile ou du fichier de dépendances.
4. Reconstruction.
5. Exécution des tests.
6. Scan de la nouvelle image.
7. Publication.
8. Déploiement contrôlé.
9. Surveillance après déploiement.

Pour les vulnérabilités exploitées activement ou critiques, le processus doit être accéléré selon une procédure de réponse définie.

### 12.6. Ne pas simplement supprimer un paquet signalé

Si un scanner détecte un composant vulnérable, il faut déterminer :

- S'il est réellement présent dans l'image finale.
- Quelle version est utilisée.
- Quelle fonction remplit le composant.
- Si une version corrigée existe.
- Si le composant peut être retiré sans casser l'application.
- Si la vulnérabilité est exploitable dans le contexte du service.

La réponse correcte est une réduction documentée du risque, et non simplement un rapport de scan affichant moins de résultats.

## 13. SBOM et provenance de construction

La sécurité de la chaîne d'approvisionnement logicielle ne se limite pas à scanner les vulnérabilités.

Il faut également pouvoir répondre à deux questions :

1. Que contient exactement l'image ?
2. Comment cette image a-t-elle été construite ?

### 13.1. Qu'est-ce qu'un SBOM ?

Un SBOM, ou *Software Bill of Materials*, est un inventaire des composants logiciels présents dans un produit ou un artefact.

Il peut notamment contenir :

- Les noms des composants.
- Les versions.
- Les relations entre composants.
- Certaines informations de licence.
- Des informations utiles à la gestion des dépendances.

Un SBOM facilite l'identification des images qui contiennent un composant affecté lorsqu'une vulnérabilité est annoncée.

Il est particulièrement utile lorsque plusieurs applications partagent la même image de base ou les mêmes bibliothèques.

### 13.2. Générer un SBOM

Les outils et les formats disponibles dépendent de la méthode de construction.

Avec BuildKit et Docker Buildx, des attestations SBOM peuvent être produites lors de la construction.

Exemple :

```bash
docker buildx build \
  --tag MON_IDENTIFIANT/mon-image:1.0 \
  --sbom=true \
  --push .
```

Remplacez la référence par celle de votre registre.

Cette commande illustre le principe de génération du SBOM et de publication. Le builder doit prendre en charge les attestations, et le registre doit permettre la conservation des métadonnées produites.

Documentation :

https://docs.docker.com/build/metadata/attestations/sbom/

### 13.3. Qu'est-ce que la provenance ?

La provenance décrit les éléments qui permettent de comprendre comment un artefact a été produit.

Selon le mécanisme utilisé, elle peut inclure des informations sur :

- La source.
- Le processus de construction.
- Les paramètres de build.
- Les matériaux utilisés.
- L'identité ou le contexte du processus de publication.

Une attestation de provenance peut aider à vérifier qu'une image provient du processus attendu.

Elle n'est pas une preuve automatique d'absence de malveillance. Il faut aussi vérifier la fiabilité de la source, du processus et des identités signataires.

### 13.4. Produire des attestations de construction

Exemple avec Buildx :

```bash
docker buildx build \
  --tag MON_IDENTIFIANT/mon-image:1.0 \
  --provenance=true \
  --sbom=true \
  --push .
```

Les options exactes et le niveau de provenance disponible dépendent de la version de Buildx, du builder et de la méthode de publication.

Lorsque les attestations sont attachées au résultat de construction, il faut s'assurer que le registre et les outils utilisés les conservent et permettent de les vérifier.

Documentation :

https://docs.docker.com/build/metadata/attestations/

### 13.5. Attention aux secrets pendant le build

Les métadonnées de provenance peuvent inclure des informations sur les paramètres utilisés lors de la construction.

Ne transmettez pas de secrets par des arguments de build ou des variables d'environnement qui peuvent apparaître dans l'image ou dans les attestations.

Docker documente les mécanismes de montage temporaire de secrets destinés au build :

https://docs.docker.com/build/building/secrets/

Un secret doit être mis à disposition uniquement de l'étape qui en a besoin et ne doit pas être incorporé au contenu final.

### 13.6. Relier l'image au commit source

Pour une livraison traçable, conservez un ensemble d'informations cohérent :

```text
Commit source
     |
     v
Pipeline de construction
     |
     v
Image identifiée
     |
     +--> SBOM
     |
     +--> Provenance
     |
     +--> Résultats de tests
     |
     +--> Résultats de scan
     |
     v
Artefact publié
     |
     v
Déploiement identifié
```

Ce modèle facilite les investigations lorsque l'on doit retrouver rapidement les composants présents dans une image ou identifier les applications affectées par une nouvelle vulnérabilité.

## 14. Sécuriser les secrets

### 14.1. Qu'est-ce qu'un secret ?

Un secret est une information sensible qui ne doit être accessible qu'aux personnes ou processus autorisés.

Exemples :

- Mot de passe d'une base de données.
- Clé API.
- Jeton d'accès à un registre.
- Clé privée SSH.
- Certificat client associé à une clé privée.
- Identifiant d'accès à un service cloud.
- Clé de chiffrement.
- Secret de signature.

### 14.2. Mauvaise pratique : secret dans le Dockerfile

Évitez :

```dockerfile
FROM python:3.12-slim

ENV API_TOKEN="secret-tres-sensible"

CMD ["python", "app.py"]
```

Le secret peut être visible dans les métadonnées de l'image ou les informations de configuration.

Il ne doit pas être inscrit directement dans le Dockerfile.

### 14.3. Mauvaise pratique : utiliser un build argument comme secret

Exemple à éviter :

```dockerfile
ARG PRIVATE_TOKEN
RUN commande-utilisant-le-token
```

Si le jeton est transmis au build comme argument, il peut être exposé dans des informations liées à la construction selon la façon dont il est utilisé et enregistré.

Un argument de build sert à configurer une construction, pas à stocker un secret de manière sécurisée.

### 14.4. Utiliser les secrets BuildKit

Lorsque la construction doit accéder à un dépôt privé, Docker permet de fournir un secret à une instruction de build de manière temporaire.

Exemple de Dockerfile :

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=secret,id=pip_conf,target=/etc/pip.conf \
    pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

Dans cet exemple, l'étape de build peut accéder à un fichier de configuration temporaire appelé `pip_conf`.

La construction peut être lancée avec :

```bash
docker build \
  --secret id=pip_conf,src=/chemin/vers/pip.conf \
  -t mon-api:1.0 .
```

Le fichier doit être accessible au processus de construction.

Le secret doit être utilisé uniquement pendant l'étape prévue et ne doit pas être copié ailleurs dans les couches de l'image.

### 14.5. Les secrets d'exécution

Les secrets nécessaires lorsque le conteneur fonctionne doivent être fournis par un mécanisme adapté au runtime et à la plateforme.

Selon l'environnement, cela peut inclure :

- Un gestionnaire de secrets.
- Des secrets montés comme fichiers.
- Des identités de service.
- Des mécanismes de distribution de certificats.
- Des variables d'environnement fournies à partir d'un stockage sécurisé lorsque ce modèle est adapté.

Les variables d'environnement ne sont pas automatiquement inappropriées, mais elles peuvent être visibles dans certaines interfaces d'administration, certains diagnostics ou certains journaux.

Le modèle choisi doit tenir compte de la sensibilité du secret et des personnes ou processus capables de lire la configuration du conteneur.

### 14.6. Secrets dans Docker Compose

Compose permet de déclarer des secrets et de les associer à certains services.

Exemple :

```yaml
services:
  api:
    image: exemple-api:1.0
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

Le service reçoit le secret selon le mécanisme prévu par Compose pour le contexte d'exécution utilisé.

Dans les installations Compose locales, un secret basé sur un fichier hôte n'est pas automatiquement équivalent à un secret chiffré et administré par un gestionnaire centralisé.

Il faut protéger le fichier source, ses permissions, sa distribution et les sauvegardes qui le contiennent.

Ne commitez pas le fichier `secrets/db_password.txt`.

### 14.7. Rotation des secrets

Si un secret a été exposé, sa suppression du fichier ne suffit pas.

Il faut généralement :

1. Révoquer ou renouveler le secret.
2. Identifier les systèmes qui lui faisaient confiance.
3. Contrôler les accès potentiellement réalisés.
4. Mettre à jour les services concernés.
5. Rechercher les copies et les journaux susceptibles de contenir la valeur.
6. Nettoyer l'historique si nécessaire.
7. Documenter l'incident.

### 14.8. Séparer les secrets de développement et de production

Un pipeline de test ne devrait pas disposer d'un jeton global capable de modifier toutes les ressources de production.

Utilisez des secrets dédiés à chaque environnement et limitez les permissions à l'opération nécessaire.

Cette séparation réduit les conséquences d'une compromission du dépôt, du runner ou d'une dépendance.

## 15. Sécuriser les réseaux de conteneurs

### 15.1. Pourquoi segmenter les réseaux ?

Les services d'une application n'ont pas tous besoin de communiquer directement entre eux.

Une API peut devoir joindre une base de données, tandis que le frontal web n'a pas besoin d'accéder directement à cette base.

Un réseau trop permissif facilite certains mouvements latéraux après la compromission d'un service.

### 15.2. Séparer frontal et données

Exemple Compose :

```yaml
services:
  frontend:
    image: exemple-frontend:1.0
    ports:
      - "127.0.0.1:8080:80"
    networks:
      - front_net

  api:
    image: exemple-api:1.0
    networks:
      - front_net
      - data_net

  database:
    image: postgres:18
    networks:
      - data_net

networks:
  front_net:
  data_net:
```

Dans ce modèle :

- Le frontal est connecté à `front_net`.
- L'API est connectée aux deux réseaux.
- La base de données n'est connectée qu'à `data_net`.

Cela limite les chemins de communication directs.

Dans une architecture de production, il faudra également définir une configuration de stockage, des identifiants et des règles d'exposition appropriés pour la base de données.

### 15.3. Ne pas publier inutilement les ports internes

Un service qui doit uniquement être accessible depuis le réseau Compose ne nécessite généralement pas de mapping `ports` sur l'hôte.

Par exemple, si PostgreSQL n'est utilisé que par l'API, sa section `ports` peut être omise.

Les services partagés peuvent communiquer via leur nom de service et le port interne approprié.

### 15.4. Différence entre `ports` et `expose`

La publication des ports avec `ports` crée une configuration d'accès entre l'hôte et le service.

L'attribut `expose` peut documenter les ports internes d'un service, mais ne publie pas automatiquement ces ports sur les interfaces de l'hôte.

Les services d'un même réseau Compose peuvent déjà communiquer selon la configuration du réseau, sans qu'il soit nécessaire de publier leurs ports sur l'hôte.

### 15.5. Limiter les réseaux sensibles

Les services d'administration, les bases de données et les composants contenant des secrets peuvent nécessiter des réseaux séparés et des permissions spécifiques.

Cette segmentation doit être conçue en fonction des communications requises, et non uniquement du nom des services.

Évitez d'utiliser un réseau partagé très large si plusieurs applications indépendantes peuvent être séparées.

### 15.6. Surveillance des connexions

La sécurité réseau nécessite également de contrôler les flux inattendus.

Selon l'environnement, surveillez :

- Les ports publiés.
- Les connexions vers les services de données.
- Les requêtes DNS.
- Les communications sortantes.
- Les connexions administratives.
- Les volumes inhabituels de données.
- Les tentatives de connexion échouées.

Docker fournit des informations réseau et des statistiques, mais une visibilité approfondie peut nécessiter des contrôles supplémentaires au niveau de l'hôte ou de l'infrastructure.

## 16. Contrôler l'accès aux ressources et aux périphériques

### 16.1. Les périphériques

Un conteneur n'a pas besoin d'accéder à tous les périphériques de l'hôte.

L'accès à des interfaces, à des périphériques ou à des composants du système doit être explicitement justifié.

Évitez d'utiliser le mode privilégié simplement parce qu'une application a besoin d'un périphérique spécifique.

### 16.2. Ajouter un accès ciblé

Docker permet notamment de préciser des périphériques avec des options dédiées.

Les autorisations nécessaires dépendent de l'interface et de l'environnement.

Avant d'accorder un accès, identifiez :

- Le périphérique exact.
- Les opérations requises.
- L'utilisateur qui y accède.
- La possibilité de restreindre les permissions.
- Les conséquences d'une compromission du conteneur.

### 16.3. Partage du namespace PID de l'hôte

Partager le namespace des processus de l'hôte peut exposer davantage d'informations ou d'interactions entre les processus.

Exemple :

```bash
docker run --pid=host image
```

Cette option ne doit pas être accordée à une application ordinaire sans besoin documenté.

### 16.4. Partage du namespace réseau de l'hôte

De même :

```bash
docker run --network=host image
```

peut modifier les hypothèses de séparation réseau et faire perdre l'isolation habituelle du réseau du conteneur.

Les comportements précis diffèrent selon le système et le moteur.

L'accès à l'espace réseau de l'hôte doit être évalué comme un privilège important.

## 17. Les conteneurs et la chaîne d'approvisionnement logicielle

### 17.1. Une image peut être compromise avant son exécution

Les risques ne viennent pas uniquement du code applicatif.

Ils peuvent apparaître dans :

- Le dépôt source.
- Une dépendance externe.
- Une action CI/CD.
- Un outil de construction.
- Une image de base.
- Un registre compromis.
- Un pipeline utilisant des permissions trop larges.
- Un processus de publication non vérifié.

La sécurité doit couvrir toute la chaîne, depuis la source jusqu'à la version déployée.

### 17.2. Vérifier l'origine des images

Avant d'utiliser une image :

- Identifiez l'éditeur.
- Consultez les informations de maintenance.
- Évaluez la source de téléchargement.
- Vérifiez la politique de publication.
- Contrôlez le contenu des images.
- Conservez les informations de provenance lorsque cela est disponible.

Ne supposez pas que le nom d'une image garantit son authenticité.

### 17.3. Protéger les registres

Pour les images privées :

- Exigez l'authentification.
- Limitez les permissions de téléchargement et de publication.
- Séparez les rôles de lecture et d'écriture.
- Utilisez des identifiants adaptés aux pipelines.
- Protégez les clés et les jetons.
- Contrôlez les journaux d'accès.
- Définissez une politique de conservation.
- Prévoyez le retrait ou la dépréciation des versions obsolètes.

Un registre centralisé facilite la gouvernance, mais il doit lui-même être protégé.

### 17.4. Réduire les droits de publication

Le pipeline de publication n'a généralement pas besoin de droits administratifs complets sur toute l'organisation.

Accordez uniquement les droits nécessaires au dépôt d'image concerné.

Séparez, lorsque cela est pertinent :

- Les droits de lecture.
- Les droits de construction.
- Les droits de publication.
- Les droits de suppression.
- Les droits d'administration du registre.

### 17.5. Signatures d'images

La signature d'une image peut aider à vérifier qu'un contenu correspond à une identité ou à une chaîne de confiance attendue.

Une signature valide n'indique pas automatiquement que l'image est sûre : elle indique surtout que le contenu correspond à la signature et à la clé vérifiées, selon le mécanisme utilisé.

La politique doit préciser :

- Qui peut signer.
- Quels artefacts doivent être signés.
- Comment les clés ou identités sont protégées.
- Où les signatures sont conservées.
- Comment les signatures sont vérifiées avant déploiement.
- Comment les clés compromises sont révoquées ou remplacées.

### 17.6. Vérifier avant déploiement

Un déploiement sensible devrait être conditionné par les contrôles définis dans la politique de livraison.

Exemple conceptuel :

```text
Image téléchargée
       |
       v
Vérification de l'origine
       |
       v
Vérification de la signature
       |
       v
Validation du digest
       |
       v
Contrôle du SBOM et des vulnérabilités
       |
       v
Application des règles de sécurité
       |
       v
Autorisation de déploiement
```

La politique exacte dépend des outils, du registre et du niveau d'assurance recherché.

## 18. Vérifier les configurations Docker dangereuses

Cette section fournit des commandes d'audit initial. Elles aident à repérer certaines configurations, mais elles ne constituent pas un audit exhaustif du système.

### 18.1. Lister les conteneurs

```bash
docker ps -a
```

Identifiez les conteneurs actifs, arrêtés, inconnus ou inutilisés.

Les conteneurs anciens peuvent conserver des configurations, des fichiers ou des références d'images qui méritent une revue.

### 18.2. Examiner les privilèges d'un conteneur

```bash
docker inspect --format '{{.HostConfig.Privileged}}' NOM_DU_CONTENEUR
```

Si la sortie indique `true`, le conteneur est configuré en mode privilégié.

Examinez également :

```bash
docker inspect --format '{{json .HostConfig.CapAdd}}' NOM_DU_CONTENEUR
```

Puis :

```bash
docker inspect --format '{{json .HostConfig.CapDrop}}' NOM_DU_CONTENEUR
```

Ces commandes permettent de voir les capabilities ajoutées et supprimées dans la configuration du conteneur.

### 18.3. Examiner les montages

```bash
docker inspect --format '{{json .Mounts}}' NOM_DU_CONTENEUR
```

Recherchez les montages qui exposent :

- Le système de fichiers hôte.
- Le socket Docker.
- Des répertoires système.
- Des fichiers de secrets.
- Des répertoires en écriture qui ne sont pas nécessaires.

Un montage n'est pas dangereux par nature. Le risque dépend de la ressource, des permissions et du besoin applicatif.

### 18.4. Examiner le réseau

```bash
docker inspect --format '{{json .NetworkSettings.Networks}}' NOM_DU_CONTENEUR
```

Examinez également les ports publiés :

```bash
docker port NOM_DU_CONTENEUR
```

Un service interne ne devrait pas nécessairement être accessible depuis toutes les interfaces de l'hôte.

### 18.5. Examiner l'utilisateur

```bash
docker inspect --format '{{.Config.User}}' NOM_DU_CONTENEUR
```

Une valeur vide peut indiquer que l'image n'explicite pas l'utilisateur dans la configuration inspectée.

Vérifiez le Dockerfile et le processus réellement exécuté avant de conclure.

### 18.6. Examiner le système de fichiers en lecture seule

```bash
docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' NOM_DU_CONTENEUR
```

Cette valeur peut aider à identifier les conteneurs dont le système de fichiers racine est ou n'est pas configuré en lecture seule.

La lecture seule n'est pas toujours compatible avec tous les services, mais elle doit être étudiée pour les applications qui n'ont pas besoin d'écrire dans leur système de fichiers racine.

### 18.7. Examiner les ressources

```bash
docker stats --no-stream
```

Cette commande fournit un instantané des consommations de ressources.

Pour connaître la configuration d'un conteneur :

```bash
docker inspect NOM_DU_CONTENEUR
```

Examinez les limites mémoire, CPU et processus selon les options et la version du moteur.

### 18.8. Limites des inspections

Les commandes `docker inspect` décrivent la configuration exposée par le moteur. Elles ne remplacent pas :

- L'audit du système hôte.
- La vérification des règles de pare-feu.
- L'analyse des dépendances.
- Le contrôle des fichiers et des secrets.
- L'inspection des politiques AppArmor ou SELinux.
- L'analyse de la provenance des images.
- La vérification des événements de sécurité.
- Les tests de l'application.

Utilisez ces commandes comme point de départ d'une investigation structurée.

## 19. Exemple de conteneur durci

L'objectif de cette section est de combiner plusieurs protections dans un lancement concret.

### 19.1. Conditions préalables

Supposons que l'image `exemple-api:1.0` :

- Dispose d'un utilisateur non privilégié.
- Écoute sur le port 8000.
- N'a pas besoin d'écrire dans le système de fichiers racine.
- Peut utiliser `/tmp` pour les fichiers temporaires.
- N'a pas besoin de capabilities supplémentaires.

Les options doivent être adaptées si ces conditions ne sont pas vraies.

### 19.2. Exemple de lancement

```bash
docker run -d \
  --name api-durcie \
  --user 10001:10001 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges=true \
  --pids-limit 100 \
  --memory 256m \
  --cpus 1.0 \
  -p 127.0.0.1:8080:8000 \
  exemple-api:1.0
```

Cette commande illustre un profil de sécurité de base, pas une configuration universelle.

Elle combine :

- Un utilisateur non privilégié.
- Un système de fichiers racine en lecture seule.
- Un système de fichiers temporaire limité.
- Le retrait des capabilities.
- L'interdiction d'acquérir de nouveaux privilèges.
- Une limite de processus.
- Une limite mémoire.
- Une limite CPU.
- Une publication du port limitée à la boucle locale.

### 19.3. Vérifier le démarrage

```bash
docker ps -a
```

Puis :

```bash
docker logs api-durcie
```

Si l'application échoue, identifiez l'opération refusée avant de retirer une protection.

Elle peut avoir besoin d'un répertoire temporaire supplémentaire, d'une permission sur un fichier ou d'une capacité précise.

### 19.4. Tester les protections

Vérifiez les paramètres :

```bash
docker inspect api-durcie
```

Examinez notamment :

- L'utilisateur.
- Le mode privilégié.
- Les capabilities.
- La valeur `ReadonlyRootfs`.
- Les limites de ressources.
- Les montages.
- Les ports publiés.

### 19.5. Vérifier la compatibilité

Testez :

- Le démarrage normal.
- Le comportement des principales routes.
- Les erreurs applicatives.
- Les dépendances externes.
- Les écritures temporaires.
- Les redémarrages.
- Les limites mémoire et CPU.
- La journalisation.
- L'arrêt propre.

Une configuration qui empêche l'application de fonctionner n'est pas nécessairement une configuration de sécurité réussie.

L'objectif est de définir les permissions minimales nécessaires, puis de vérifier que les protections fonctionnent comme prévu.

## 20. Sécuriser une application avec Docker Compose

Un fichier Compose de production doit intégrer les protections de l'application et de ses dépendances.

### 20.1. Exemple de configuration durcie

```yaml
name: api-securisee

services:
  api:
    image: registre.exemple/organisation/api:1.0.0

    user: "10001:10001"

    read_only: true

    cap_drop:
      - ALL

    security_opt:
      - no-new-privileges:true

    tmpfs:
      - /tmp:rw,noexec,nosuid,size=64m

    pids_limit: 100

    mem_limit: 256m

    cpus: 1.0

    ports:
      - "127.0.0.1:8080:8000"

    restart: unless-stopped

    networks:
      - front_net

networks:
  front_net:
```

Cette configuration illustre une politique de réduction des privilèges et d'exposition.

L'image, le port, l'utilisateur et les limites doivent être adaptés à l'application réelle.

Le réseau `front_net` est créé par Compose. Dans une architecture plus complète, vous pouvez prévoir des réseaux distincts pour les composants applicatifs et les données.

### 20.2. Valider le fichier

```bash
docker compose config --quiet
```

Cette commande vérifie la syntaxe et la résolution de la configuration.

Elle ne démontre pas que toutes les protections sont effectives ni que les paramètres sont compatibles avec le logiciel.

### 20.3. Examiner les paramètres résolus

```bash
docker compose config
```

Examinez les valeurs résultantes avant le déploiement.

Évitez de partager la sortie sans vérifier qu'elle ne contient pas de données sensibles.

### 20.4. Contrôler les conteneurs après lancement

```bash
docker compose up -d
docker compose ps
docker compose logs
```

Puis utilisez les commandes d'inspection pour vérifier les protections attendues.

Dans un environnement professionnel, ces contrôles peuvent être automatisés dans la validation de déploiement.

## 21. Sécuriser les ports et les communications

### 21.1. N'exposer que les ports nécessaires

Une application peut avoir besoin d'un port HTTP public, mais pas nécessairement de publier directement sa base de données.

Exemple :

```yaml
services:
  api:
    ports:
      - "127.0.0.1:8080:8000"

  database:
    image: postgres:18
```

Dans ce modèle, aucun port de base de données n'est publié explicitement sur l'hôte.

La communication interne doit être configurée au moyen du réseau approprié.

### 21.2. Utiliser un proxy inverse lorsque c'est adapté

Une architecture peut placer un proxy inverse devant plusieurs services.

Ce proxy peut assumer certaines responsabilités d'exposition, telles que la terminaison TLS, le routage et certains contrôles d'accès.

Cela ne signifie pas que le proxy remplace la sécurité applicative, l'authentification ou la segmentation interne.

### 21.3. Contrôler les communications sortantes

Il faut également considérer ce qu'un conteneur peut joindre.

Une application compromise peut tenter de contacter des serveurs externes ou des services internes.

Selon le niveau de risque, la politique réseau peut inclure :

- Des règles de sortie.
- Des restrictions DNS.
- Des contrôles de routage.
- Une segmentation des réseaux.
- Une journalisation des flux.
- Une surveillance des connexions inhabituelles.

Les réseaux Docker seuls ne constituent pas toujours une politique complète de filtrage des flux sortants.

### 21.4. Protéger les services de données

Les bases de données et les caches doivent être accessibles uniquement aux services qui en ont besoin.

Les contrôles comprennent notamment :

- L'authentification.
- Des droits propres à l'application.
- Des comptes différents pour les environnements.
- Le contrôle des ports.
- La segmentation réseau.
- La protection des sauvegardes.
- La gestion de la rotation des secrets.

Il est préférable de ne pas utiliser un compte administrateur global pour toutes les connexions applicatives.

## 22. Sécuriser les journaux et la surveillance

### 22.1. Les journaux peuvent contenir des secrets

Une application peut involontairement enregistrer :

- Des mots de passe.
- Des jetons.
- Des données personnelles.
- Des informations de requêtes.
- Des identifiants de sessions.
- Des chaînes de connexion.
- Des paramètres sensibles.

Ces informations peuvent être exposées si les journaux sont accessibles à un nombre trop important de personnes ou conservés trop longtemps.

### 22.2. Journaliser de manière utile

Les journaux devraient fournir des informations suffisantes pour diagnostiquer les problèmes sans révéler inutilement des données sensibles.

Par exemple, il est généralement préférable de journaliser un identifiant de requête et un code d'erreur plutôt que d'enregistrer l'intégralité d'une requête contenant des informations confidentielles.

### 22.3. Consulter les journaux Docker

```bash
docker logs NOM_DU_CONTENEUR
```

Pour suivre les messages :

```bash
docker logs -f NOM_DU_CONTENEUR
```

La politique de journalisation dépend du pilote utilisé, de la configuration du moteur et des services d'observabilité disponibles.

### 22.4. Protéger l'accès aux journaux

Contrôlez :

- Qui peut consulter les journaux.
- Qui peut modifier la configuration de journalisation.
- Combien de temps les données sont conservées.
- Si les journaux sont transmis à un service centralisé.
- Si les données sont chiffrées lorsque nécessaire.
- Comment les événements de sécurité sont protégés contre une altération.

### 22.5. Surveiller les signaux importants

Selon l'application, il peut être utile d'alerter sur :

- Des redémarrages fréquents.
- Des échecs répétés de healthchecks.
- Une consommation excessive de ressources.
- Des erreurs d'authentification.
- Des connexions inhabituelles.
- Des échecs de communication avec les dépendances.
- Des changements inattendus de configuration.
- Des tentatives de publication non autorisées.

Les alertes doivent être associées à une procédure d'investigation claire.

## 23. Réponse aux incidents impliquant des conteneurs

### 23.1. Reconnaître un incident

Un incident peut être suspecté lorsque :

- Un conteneur exécute un processus inattendu.
- Une image inconnue est apparue.
- Un secret a été exposé.
- Le socket Docker a été utilisé par un processus non prévu.
- Une consommation CPU ou réseau devient anormale.
- Une image publiée diffère de l'image approuvée.
- Des connexions sortantes inhabituelles sont observées.
- Des fichiers hôtes ont été modifiés.
- Des privilèges inattendus ont été accordés.

Un signal isolé peut être bénin. Il doit être examiné dans son contexte.

### 23.2. Première démarche

Lorsqu'un incident est suspecté :

1. Déterminer l'étendue possible de l'incident.
2. Protéger les services et ressources critiques.
3. Préserver les journaux et éléments nécessaires à l'investigation.
4. Éviter les manipulations qui détruisent les preuves.
5. Révoquer ou renouveler les secrets exposés.
6. Identifier l'image et la configuration réellement utilisées.
7. Contenir les communications ou accès nécessaires.
8. Établir une procédure de remise en service à partir d'artefacts fiables.

La priorité dépend de la nature de l'incident, des données concernées et des exigences de continuité.

### 23.3. Ne pas supprimer immédiatement toutes les traces

La suppression d'un conteneur peut faire disparaître sa couche inscriptible et compliquer l'analyse de son état.

Avant une opération de nettoyage, conservez les éléments nécessaires, lorsque cela est possible et conforme à la procédure d'incident :

- Les journaux.
- Les métadonnées du conteneur.
- L'identifiant de l'image.
- La configuration des montages.
- Les ports et réseaux.
- Les événements du système hôte.
- Les informations relatives au processus.
- Les artefacts de construction et de publication.

Les procédures doivent tenir compte des besoins juridiques, opérationnels et de confidentialité de l'organisation.

### 23.4. Inspecter un conteneur suspect

Commencez par :

```bash
docker ps -a
```

Puis :

```bash
docker inspect NOM_DU_CONTENEUR
```

Consultez les journaux :

```bash
docker logs NOM_DU_CONTENEUR
```

Examinez les processus si le conteneur fonctionne encore :

```bash
docker top NOM_DU_CONTENEUR
```

Ces commandes fournissent des éléments utiles, mais elles ne remplacent pas les outils de détection sur l'hôte ni l'analyse de l'ensemble de l'infrastructure.

### 23.5. Contenir l'incident

Selon le contexte, les mesures de confinement peuvent inclure :

- Le retrait du trafic vers le service.
- L'isolement réseau du conteneur.
- La suspension des identifiants compromis.
- La révocation des jetons de registre.
- L'arrêt de pipelines de publication suspects.
- La protection des autres systèmes qui utilisent la même image.
- Le remplacement du service par une version validée.

Il faut éviter de redémarrer simplement le même conteneur ou de republier la même image sans comprendre la cause.

### 23.6. Reconstruire à partir d'une source fiable

Après une compromission :

1. Vérifiez le code source.
2. Identifiez le point d'entrée de l'attaque.
3. Corrigez le défaut.
4. Recréez l'image dans un environnement de build fiable.
5. Vérifiez les dépendances et les secrets.
6. Effectuez les contrôles de sécurité.
7. Publiez une nouvelle version identifiée.
8. Déployez selon une procédure contrôlée.
9. Surveillez le service après remise en production.

Le remplacement d'un conteneur compromis n'est pas suffisant si l'image ou le pipeline qui l'a produit est lui-même compromis.

## 24. Audit de sécurité avec le CIS Docker Benchmark

### 24.1. Qu'est-ce que le CIS Docker Benchmark ?

Le CIS Docker Benchmark est un ensemble de recommandations de configuration sécurisée élaborées selon une démarche de consensus.

Il fournit des critères qui peuvent servir de base à un audit du moteur et de l'environnement Docker.

Documentation officielle :

https://www.cisecurity.org/benchmark/docker

### 24.2. Ce qu'un benchmark permet de faire

Un benchmark peut aider à :

- Identifier des configurations trop permissives.
- Vérifier certains paramètres du daemon.
- Examiner les permissions.
- Contrôler certaines pratiques de journalisation.
- Vérifier certains paramètres des conteneurs.
- Formaliser des exigences d'audit.

Il faut sélectionner la version correspondant au système et à l'environnement concernés.

### 24.3. Un résultat conforme ne garantit pas l'absence de risque

Une configuration peut respecter des contrôles définis tout en comportant une vulnérabilité non couverte par le benchmark.

Le contexte métier, l'exposition réseau, les données, les dépendances et les exigences réglementaires restent déterminants.

Les résultats doivent être interprétés en fonction du risque réel et des exceptions explicitement justifiées.

### 24.4. Documenter les exceptions

Certaines applications nécessitent des paramètres particuliers.

Lorsqu'une recommandation ne peut pas être appliquée, documentez :

- La raison de l'exception.
- Le risque associé.
- La durée de validité.
- Les mesures compensatoires.
- Le responsable de la décision.
- Les conditions de réévaluation.

Il vaut mieux documenter une exception maîtrisée que prétendre qu'une configuration est sécurisée sans examiner les écarts.

## 25. Exemple de pipeline CI/CD orienté sécurité

Un pipeline de sécurité doit intégrer les contrôles au processus normal de construction et de publication.

### 25.1. Étapes recommandées

```text
Pull request
     |
     v
Validation des fichiers
     |
     v
Tests applicatifs
     |
     v
Construction de l'image
     |
     v
Analyse des dépendances
     |
     v
Analyse des vulnérabilités
     |
     v
Génération du SBOM
     |
     v
Vérification des règles
     |
     v
Publication autorisée
     |
     v
Vérification de provenance
     |
     v
Déploiement contrôlé
```

Chaque contrôle doit avoir une fonction claire et une politique de résultat.

### 25.2. Les contrôles ne doivent pas être simplement décoratifs

Un pipeline peut exécuter un scan, mais être configuré pour continuer même si le résultat révèle une vulnérabilité critique.

Il faut définir :

- Quels résultats provoquent un échec.
- Quels résultats nécessitent une dérogation.
- Qui peut approuver une exception.
- Quelle durée est accordée à la correction.
- Comment les exceptions sont enregistrées.
- Quand une exception doit être réévaluée.

### 25.3. Exemple de validation du build

Un job de validation Docker peut commencer par :

```yaml
name: Validation image

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Récupérer le dépôt
        uses: actions/checkout@v7

      - name: Vérifier Docker
        run: docker version

      - name: Valider la configuration Compose
        run: docker compose config --quiet

      - name: Construire l'image
        run: docker compose build api
```

Cet exemple est un contrôle de construction minimal. Il ne constitue pas un pipeline complet de sécurité.

Les références de versions des actions et les fonctions disponibles doivent être vérifiées selon la plateforme et la politique de sécurité de l'organisation.

### 25.4. Ajouter les scans

Dans un pipeline réel, ajoutez des étapes dédiées à l'analyse de vulnérabilités et de secrets.

Il est préférable que les outils détectent :

- Les vulnérabilités des paquets.
- Les secrets intégrés à l'image.
- Les dépendances malveillantes ou inconnues selon les capacités disponibles.
- Les défauts de configuration.
- Les informations de provenance manquantes.

Les critères d'acceptation doivent être adaptés au risque et documentés.

### 25.5. Protéger les workflows privilégiés

Une pull request peut contenir du code qui n'a pas encore été approuvé.

Ne donnez pas automatiquement à tous les workflows l'accès aux secrets de publication ou de production.

Séparez les tâches de validation des tâches privilégiées de publication et de déploiement.

Les secrets doivent être disponibles uniquement pour les travaux et identités qui en ont besoin.

## 26. Projet pratique : durcir une application Docker

Ce projet met en œuvre les principales protections abordées dans le cours.

### 26.1. Contexte

Vous disposez d'une application HTTP dans une image Docker.

Le service doit être accessible localement pour le laboratoire, mais il ne doit pas disposer d'accès inutiles au système hôte.

L'objectif est de construire une image adaptée, de définir une configuration de runtime durcie, puis de vérifier les protections réellement appliquées.

### 26.2. Structure du projet

```text
application-securisee/
|
+-- app.py
+-- requirements.txt
+-- Dockerfile
+-- compose.yaml
+-- .dockerignore
+-- .gitignore
+-- README.md
```

### 26.3. Créer l'application

Dans `app.py` :

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        payload = {
            "service": "application-securisee",
            "status": "ok"
        }

        body = json.dumps(payload).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = HTTPServer(("0.0.0.0", 8000), Handler)

    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
```

Cette application ne dépend que de la bibliothèque standard Python.

Elle sert uniquement de démonstration des protections Docker. Le serveur HTTP intégré à Python n'est pas destiné à être utilisé tel quel pour une application de production.

### 26.4. Créer le Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser app.py .

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
```

Ce Dockerfile :

- Utilise une image de base Python.
- Désactive l'écriture habituelle des fichiers bytecode.
- Rend les journaux Python plus directement visibles.
- Crée un utilisateur non privilégié.
- Copie l'application avec une propriété adaptée.
- Configure l'utilisateur d'exécution.
- Documente le port du service.
- Définit le processus principal.

Avant une utilisation professionnelle, vérifiez la version de Python, l'image de base, les vulnérabilités connues et la politique de maintenance.

### 26.5. Créer `.dockerignore`

```dockerignore
.git/
.venv/
venv/
__pycache__/
*.py[cod]
*.log
.env
.env.*
```

Cela réduit le contexte de construction et évite d'inclure certains fichiers temporaires et locaux.

### 26.6. Créer `compose.yaml`

```yaml
name: application-securisee

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile

    image: application-securisee:1.0

    user: "10001:10001"

    read_only: true

    cap_drop:
      - ALL

    security_opt:
      - no-new-privileges:true

    tmpfs:
      - /tmp:rw,noexec,nosuid,size=32m

    pids_limit: 50

    mem_limit: 128m

    cpus: 0.5

    ports:
      - "127.0.0.1:8080:8000"

    restart: unless-stopped
```

### 26.7. Comprendre le profil appliqué

Le conteneur :

- Utilise un utilisateur non privilégié.
- N'a pas besoin de capabilities supplémentaires dans ce cas de démonstration.
- Ne peut pas écrire dans le système de fichiers racine.
- Dispose d'un espace temporaire restreint.
- Ne peut pas acquérir certains nouveaux privilèges.
- Dispose de limites de ressources.
- N'expose le service que sur la boucle locale de l'hôte.

Cette configuration doit être testée avec la version de Docker Compose utilisée.

### 26.8. Valider la configuration

```bash
docker compose config --quiet
```

Si la commande réussit, examinez aussi la configuration résolue :

```bash
docker compose config
```

Vérifiez que le port, l'image et les paramètres de sécurité sont conformes au besoin.

### 26.9. Construire et démarrer

```bash
docker compose up --build -d
```

Puis :

```bash
docker compose ps
```

### 26.10. Tester l'application

```bash
curl http://127.0.0.1:8080/
```

Réponse attendue :

```json
{
  "service": "application-securisee",
  "status": "ok"
}
```

### 26.11. Vérifier les paramètres de sécurité

Récupérez le nom du conteneur :

```bash
docker compose ps
```

Inspectez ensuite les paramètres importants :

```bash
docker inspect NOM_DU_CONTENEUR
```

Contrôlez notamment :

- L'utilisateur effectif.
- La configuration du système de fichiers.
- Les capabilities.
- Les options de sécurité.
- Les montages.
- Les ports publiés.
- Les limites de ressources.

### 26.12. Tester le comportement en lecture seule

Essayez d'écrire dans un répertoire qui n'est pas monté en écriture, à condition que l'image contienne un outil permettant le test.

L'opération doit échouer lorsque le chemin appartient au système de fichiers racine rendu en lecture seule.

Une écriture dans `/tmp` peut en revanche réussir grâce au montage temporaire défini.

Cette différence permet de vérifier que le système de fichiers et les exceptions sont configurés de manière cohérente.

### 26.13. Consulter les journaux

```bash
docker compose logs api
```

Vérifiez que les informations utiles sont disponibles et qu'aucun secret n'est écrit.

### 26.14. Nettoyer le laboratoire

```bash
docker compose down
```

Ce projet ne définit pas de volume persistant, mais dans une application réelle les données doivent être examinées avant tout nettoyage.

## 27. Audit de sécurité d'une configuration volontairement faible

Considérez le Dockerfile suivant :

```dockerfile
FROM ubuntu:latest

ENV DB_PASSWORD="mot-de-passe-en-clair"

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    curl \
    vim \
    netcat-openbsd

CMD ["bash"]
```

Cette configuration présente plusieurs problèmes à examiner.

### 27.1. L'image de base

```dockerfile
FROM ubuntu:latest
```

Le tag `latest` peut évoluer. Il n'identifie pas de façon stricte une version particulière.

Il faut sélectionner une version explicitement maintenue et appliquer une politique de mise à jour adaptée.

### 27.2. Le secret dans l'image

```dockerfile
ENV DB_PASSWORD="mot-de-passe-en-clair"
```

Le mot de passe est intégré à la configuration de l'image.

Il doit être retiré du Dockerfile et fourni par un mécanisme de secrets approprié.

Si cette image a déjà été construite ou publiée avec un vrai secret, sa simple suppression du fichier ne suffit pas. Le secret doit être renouvelé, puis les copies et l'historique doivent être évalués.

### 27.3. Copie du contexte complet

```dockerfile
COPY . .
```

Cette instruction peut inclure des fichiers non nécessaires si le contexte n'est pas soigneusement contrôlé.

Elle peut notamment incorporer des fichiers locaux, des journaux ou des éléments sensibles si le contexte et `.dockerignore` ne sont pas correctement définis.

Il est préférable de copier explicitement les fichiers nécessaires.

### 27.4. Installation de paquets inutiles

```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    netcat-openbsd
```

Les outils de diagnostic ne sont pas toujours nécessaires dans l'image finale.

L'installation d'outils inutiles augmente la quantité de logiciels maintenus et peut élargir la surface d'attaque.

Il faut examiner le besoin réel et, lorsque c'est approprié, séparer les outils de construction ou de diagnostic de l'image d'exécution.

### 27.5. Processus principal

```dockerfile
CMD ["bash"]
```

Ce Dockerfile démarre un shell par défaut au lieu de décrire clairement le lancement de l'application attendue.

Pour une image applicative, définissez un processus principal correspondant à la fonction du service.

### 27.6. Autres contrôles manquants

La configuration ne montre pas :

- D'utilisateur non privilégié.
- De stratégie de permissions.
- De politique de dépendances.
- De réduction du contexte.
- De contrôle d'image.
- De provenance.
- De contrôle de ressources.
- De restrictions de runtime.

Ces absences doivent être évaluées en fonction de l'usage prévu, mais elles justifient une revue avant la mise en production.

### 27.7. Travail demandé

Réécrivez cette configuration en :

1. Choisissant une image de base appropriée.
2. Retirant le secret.
3. Créant un utilisateur non privilégié.
4. Copiant seulement les fichiers nécessaires.
5. Réduisant les paquets inutiles.
6. Définissant clairement le processus principal.
7. Ajoutant `.dockerignore`.
8. Prévoyant les contrôles de vulnérabilités.
9. Définissant les options de runtime adaptées.
10. Documentant la méthode de construction et de publication.

## 28. Exercices de compréhension

### Exercice 1 : privilèges

Une API fonctionne en tant que `root`, sans nécessiter d'accès au système hôte.

Expliquez pourquoi il est utile de passer à un utilisateur non privilégié et citez deux autres protections complémentaires.

### Exercice 2 : mode privilégié

Un développeur ajoute `--privileged` à un conteneur parce qu'une opération réseau échoue.

Pourquoi cette correction est-elle dangereuse ? Quelle démarche faut-il adopter avant d'accorder une capability ou un accès supplémentaire ?

### Exercice 3 : système de fichiers

Un conteneur doit uniquement lire son code et écrire des fichiers temporaires.

Quelle configuration peut réduire les possibilités de modification du système de fichiers ? Expliquez le rôle de `--read-only` et de `--tmpfs`.

### Exercice 4 : socket Docker

Un conteneur d'application possède un montage du socket Docker.

Expliquez les risques possibles et proposez des solutions pour éviter cette exposition.

### Exercice 5 : seccomp

Pourquoi est-il généralement préférable de conserver le profil seccomp par défaut plutôt que de le désactiver pour résoudre une erreur ?

### Exercice 6 : secrets

Un jeton d'accès est fourni avec `ARG TOKEN=...` dans un Dockerfile.

Pourquoi cette méthode est-elle inappropriée ? Quelle approche peut être utilisée si le secret est nécessaire durant la construction ?

### Exercice 7 : registre

Une image est publiée sous le tag `stable`.

Pourquoi est-il important de conserver un digest ou d'autres informations d'identification de l'image réellement déployée ?

### Exercice 8 : limites de ressources

Un conteneur peut consommer toute la mémoire de l'hôte.

Quelles protections Docker peuvent contribuer à limiter ce risque ? Quels sont leurs inconvénients potentiels ?

### Exercice 9 : réseau

Une API et une base de données sont sur le même réseau, mais le frontal web n'a pas besoin d'accéder à la base.

Comment organiser les réseaux pour limiter les communications directes ?

### Exercice 10 : réponse à un incident

Un conteneur semble avoir été compromis et contient des fichiers temporaires potentiellement utiles à l'investigation.

Pourquoi ne faut-il pas supprimer immédiatement le conteneur sans réfléchir à la conservation des preuves ?

### Exercice 11 : SBOM

À quoi sert un SBOM ? Quelle différence existe entre un SBOM et une attestation de provenance ?

### Exercice 12 : défense en profondeur

Une image ne présente aucune vulnérabilité connue lors du scan, mais le conteneur utilise `--privileged` et monte le système de fichiers hôte en écriture.

Pourquoi ne peut-on pas considérer cette configuration comme sûre ?

## 29. Corrigés des exercices

### Corrigé 1

Un utilisateur non privilégié réduit les permissions accessibles au processus applicatif en cas de compromission.

D'autres protections possibles comprennent :

- Le retrait des capabilities inutiles.
- Un système de fichiers racine en lecture seule.
- `no-new-privileges`.
- Les limites de ressources.
- Le profil seccomp par défaut.
- La restriction des réseaux et des montages.

### Corrigé 2

Le mode privilégié peut accorder des permissions très étendues et réduire l'isolation du conteneur.

Il faut identifier l'opération réseau refusée, comprendre la capability ou la ressource réellement nécessaire, puis accorder uniquement la permission ciblée si elle est justifiée.

### Corrigé 3

Une configuration possible est :

```bash
docker run --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  mon-image:1.0
```

`--read-only` protège le système de fichiers racine contre les écritures ordinaires.

`--tmpfs` fournit un espace temporaire en écriture qui ne dépend pas du système de fichiers racine.

### Corrigé 4

L'accès au socket peut permettre au conteneur d'envoyer des instructions puissantes au daemon, notamment de demander la création de conteneurs et certains montages hôtes.

Il faut éviter de monter le socket lorsque l'application n'en a pas besoin, isoler la fonction de déploiement et limiter les permissions d'accès au daemon.

### Corrigé 5

Le profil par défaut restreint certains appels système inutiles ou dangereux tout en conservant une compatibilité large.

Le désactiver réduit une couche de protection. Il est préférable d'identifier les appels système concernés et d'ajuster les règles de manière ciblée lorsque cela est nécessaire.

### Corrigé 6

Les arguments de build ne sont pas conçus pour protéger les secrets et peuvent laisser des informations dans les métadonnées ou le processus de construction.

Les secrets BuildKit et les montages temporaires permettent de rendre le secret disponible uniquement pendant l'étape nécessaire, sans le copier volontairement dans l'image finale.

### Corrigé 7

Le tag `stable` peut être réaffecté à une autre image.

Conserver le digest et les informations de publication aide à retrouver exactement le contenu déployé, ainsi que son lien avec le commit source et les validations réalisées.

### Corrigé 8

Les protections comprennent notamment :

- `--memory`.
- `--cpus`.
- `--pids-limit`.
- Des contrôles et alertes de consommation.

Des limites trop basses peuvent provoquer des lenteurs ou des erreurs applicatives. Elles doivent être choisies selon la charge attendue et surveillées en fonctionnement.

### Corrigé 9

Il est possible de créer un réseau frontal et un réseau de données, puis de connecter le frontal uniquement au réseau frontal, l'API aux deux réseaux et la base de données uniquement au réseau de données.

Cela réduit les possibilités de connexion directe du frontal vers la base.

### Corrigé 10

La suppression d'un conteneur peut faire disparaître sa couche inscriptible et compliquer l'investigation.

Il faut d'abord déterminer quels éléments doivent être préservés, capturer les informations nécessaires selon la procédure d'incident et limiter les manipulations susceptibles de détruire les preuves.

### Corrigé 11

Un SBOM inventorie les composants logiciels présents dans un artefact.

Une attestation de provenance décrit comment l'artefact a été construit et fournit des éléments sur son origine.

Les deux informations se complètent pour améliorer la traçabilité de la chaîne d'approvisionnement.

### Corrigé 12

L'absence de vulnérabilité connue dans le scan ne prouve pas qu'une image est sûre.

Le mode privilégié et le montage du système de fichiers hôte en écriture peuvent augmenter fortement les conséquences d'une compromission.

La sécurité dépend de l'image, du runtime, des privilèges, des montages, du réseau, du système hôte et du processus de livraison.

## 30. Projet de fin de niveau : sécuriser une chaîne de conteneurisation

### 30.1. Objectif

Concevoir et mettre en œuvre une chaîne sécurisée depuis le code source jusqu'au déploiement du conteneur.

Le projet doit démontrer que vous savez appliquer des protections techniques, produire des éléments de traçabilité et définir une procédure opérationnelle.

### 30.2. Contexte

Une organisation exploite une API conteneurisée avec une base de données.

Elle souhaite réduire les risques liés aux images vulnérables, aux privilèges trop élevés, aux secrets exposés et aux déploiements non traçables.

L'application doit être construite par un pipeline, publiée dans un registre puis déployée sur un environnement de test.

### 30.3. Travail demandé

1. Créer un dépôt Git contenant l'application et le Dockerfile.
2. Définir les dépendances applicatives.
3. Créer une image de base fiable et documentée.
4. Utiliser un utilisateur non privilégié.
5. Réduire les fichiers copiés dans l'image.
6. Ajouter `.dockerignore`.
7. Vérifier les permissions du système de fichiers.
8. Définir les capabilities nécessaires.
9. Ajouter des limites de ressources.
10. Protéger les secrets de construction et d'exécution.
11. Définir les réseaux et ports nécessaires.
12. Scanner l'image et traiter les vulnérabilités pertinentes.
13. Générer un SBOM lorsque l'outil le permet.
14. Produire ou collecter les informations de provenance disponibles.
15. Publier une image avec un tag de version.
16. Conserver le digest de l'image publiée.
17. Déployer l'image dans un environnement de test.
18. Vérifier les options de sécurité réellement actives.
19. Tester le fonctionnement et la persistance des données.
20. Documenter la procédure de mise à jour.
21. Définir une procédure de réponse en cas de compromission.
22. Présenter les résultats de l'audit.

### 30.4. Livrables attendus

Le projet doit contenir :

- Le code source.
- Le Dockerfile.
- Les fichiers Compose.
- Le fichier `.dockerignore`.
- La documentation de construction.
- Les résultats de validation.
- Les résultats d'analyse des vulnérabilités.
- Un SBOM ou une explication de sa génération.
- Les informations de provenance disponibles.
- Le digest de l'image publiée.
- Une checklist de sécurité.
- Une procédure de réponse aux incidents.
- Un registre des exceptions de sécurité.
- Un plan d'amélioration continue.

### 30.5. Critères de réussite

Le projet est réussi si :

- Le processus de construction est documenté et reproductible dans les conditions prévues.
- L'image ne contient pas de secrets en clair.
- Le processus applicatif n'utilise pas inutilement des privilèges élevés.
- Les capacités et montages sont limités au besoin.
- Les ports publiés correspondent aux communications nécessaires.
- Les limites de ressources sont définies et testées.
- Les données importantes utilisent un stockage adapté.
- Les contrôles de sécurité sont intégrés à la livraison.
- L'image publiée est reliée à une version identifiable du code.
- Le déploiement peut être vérifié et l'incident peut faire l'objet d'une investigation structurée.

## 31. Checklist de mise en production

Avant de mettre un conteneur en production, examinez les éléments suivants.

### Image et chaîne d'approvisionnement

- [ ] L'image de base provient d'une source fiable.
- [ ] Les versions des dépendances sont contrôlées.
- [ ] Les paquets inutiles sont retirés lorsque cela est approprié.
- [ ] Les vulnérabilités sont analysées et priorisées.
- [ ] Les secrets ne sont pas intégrés à l'image.
- [ ] La construction est liée à une version source identifiable.
- [ ] Le tag et le digest de l'image sont conservés.
- [ ] Un SBOM est produit ou sa disponibilité est évaluée.
- [ ] Les informations de provenance disponibles sont conservées et vérifiées selon la politique du projet.

### Privilèges et système de fichiers

- [ ] Le processus fonctionne avec un utilisateur non privilégié lorsque cela est possible.
- [ ] Les capabilities sont limitées au besoin.
- [ ] Le mode privilégié est évité.
- [ ] Le socket Docker n'est pas monté inutilement.
- [ ] Le système de fichiers racine est en lecture seule lorsque l'application le permet.
- [ ] Les fichiers temporaires utilisent des espaces prévus à cet effet.
- [ ] Les montages hôtes sont limités et documentés.
- [ ] Seccomp reste actif lorsque l'environnement le permet.
- [ ] AppArmor ou SELinux sont configurés selon la plateforme.
- [ ] Les mécanismes rootless ou de remappage sont évalués lorsque cela est approprié.

### Réseau et données

- [ ] Seuls les ports nécessaires sont publiés.
- [ ] Les services internes ne sont pas exposés sans raison.
- [ ] Les réseaux sont segmentés selon les besoins.
- [ ] Les secrets sont fournis par un mécanisme approprié.
- [ ] Les volumes persistants ont des permissions adaptées.
- [ ] Les sauvegardes des données importantes sont définies et testées.
- [ ] Les journaux ne contiennent pas de secrets inutiles.
- [ ] Les communications sensibles sont protégées.

### Ressources et exploitation

- [ ] Les limites CPU, mémoire et processus sont adaptées.
- [ ] Les contrôles de santé sont configurés lorsque cela est utile.
- [ ] Les journaux sont accessibles et protégés.
- [ ] Les redémarrages sont configurés selon le besoin.
- [ ] Les alertes pertinentes sont définies.
- [ ] La procédure de mise à jour est documentée.
- [ ] La procédure de retour arrière est connue.
- [ ] La procédure de réponse aux incidents est définie.
- [ ] Les exceptions de sécurité ont un propriétaire et une justification.
- [ ] Les paramètres réellement actifs ont été vérifiés après le déploiement.

## 32. Glossaire essentiel

**AppArmor :** mécanisme de contrôle d'accès permettant d'appliquer des profils de sécurité aux processus.

**Capability :** privilège Linux spécifique accordé à un processus.

**Cgroups :** mécanismes du noyau permettant notamment de contrôler et suivre certaines ressources utilisées par des groupes de processus.

**Conteneur privilégié :** conteneur lancé avec l'option `--privileged`, qui reçoit des autorisations étendues et présente un risque accru.

**Daemon Docker :** service qui gère les opérations du moteur Docker.

**Digest :** identifiant de contenu permettant de référencer précisément une image ou un manifeste.

**Défense en profondeur :** approche qui combine plusieurs contrôles de sécurité complémentaires.

**Least privilege, ou moindre privilège :** principe consistant à n'accorder que les permissions nécessaires.

**MAC :** contrôle d'accès obligatoire, généralement appliqué au moyen d'une politique système.

**Namespace :** mécanisme Linux qui fournit une vue isolée de certaines ressources du système.

**NIST SP 800-190 :** publication du NIST consacrée aux préoccupations de sécurité des conteneurs applicatifs.

**No-new-privileges :** option qui empêche certains mécanismes d'acquisition de nouveaux privilèges par un processus.

**Provenance :** informations décrivant notamment l'origine et le processus de construction d'un artefact.

**Rootless :** mode d'exécution du moteur Docker et des conteneurs sans privilèges root classiques sur l'hôte.

**SBOM :** inventaire des composants logiciels d'un artefact.

**Seccomp :** mécanisme Linux permettant de restreindre certains appels système.

**SELinux :** système de contrôle d'accès obligatoire fondé sur des politiques de sécurité.

**Socket Docker :** interface locale de communication avec le daemon Docker, qui doit être considérée comme une ressource sensible.

**Surface d'attaque :** ensemble des interfaces, composants et mécanismes susceptibles d'être exploités.

**Tag :** référence nommée d'une image, souvent utilisée pour identifier une version logique.

**User namespace :** namespace qui permet d'isoler ou de remapper les identifiants utilisateurs et groupes.

**Volume :** stockage permettant de conserver des données indépendamment du cycle de vie habituel du conteneur.

**Vulnérabilité :** défaut susceptible d'être exploité pour compromettre la confidentialité, l'intégrité ou la disponibilité d'un système.

## 33. Références officielles pour approfondir

### Docker : sécurité du moteur et du runtime

- Docker Engine Security : https://docs.docker.com/engine/security/
- Docker Rootless Mode : https://docs.docker.com/engine/security/rootless/
- User Namespace Remapping : https://docs.docker.com/engine/security/userns-remap/
- Protection de l'accès au daemon Docker : https://docs.docker.com/engine/security/protect-access/
- Docker Seccomp Profiles : https://docs.docker.com/engine/security/seccomp/
- Docker AppArmor : https://docs.docker.com/engine/security/apparmor/
- Docker Container Run : https://docs.docker.com/reference/cli/docker/container/run/

### Docker : images et chaîne d'approvisionnement

- Bonnes pratiques de construction : https://docs.docker.com/build/building/best-practices/
- Constructions multi-stage : https://docs.docker.com/build/building/multi-stage/
- Build Secrets : https://docs.docker.com/build/building/secrets/
- Build Attestations : https://docs.docker.com/build/metadata/attestations/
- Attestations SBOM : https://docs.docker.com/build/metadata/attestations/sbom/
- Docker Scout : https://docs.docker.com/scout/
- Analyse de vulnérabilités avec Docker Scout : https://docs.docker.com/scout/explore/analysis/

### Référentiels de sécurité

- NIST SP 800-190 — Application Container Security Guide : https://csrc.nist.gov/pubs/sp/800/190/final
- CIS Docker Benchmark : https://www.cisecurity.org/benchmark/docker
- OWASP Docker Top 10 : https://owasp.org/projects/docker-top-10

Les référentiels et documentations doivent être consultés dans leur version correspondant à la plateforme utilisée. Les contrôles pertinents varient selon le système hôte, le moteur de conteneurs et les contraintes de l'application.

## 34. Synthèse du niveau expert

La sécurité des conteneurs exige une approche globale qui couvre la construction, la distribution, la configuration et l'exécution.

Les points essentiels à retenir sont les suivants.

**L'isolation n'est pas absolue.** Les conteneurs Linux partagent le noyau de leur environnement d'exécution. La sécurité dépend également du moteur, des namespaces, des capabilities, des profils de confinement et des permissions accordées.

**Le moindre privilège réduit les conséquences d'une compromission.** Utilisez des utilisateurs non privilégiés, retirez les capabilities inutiles, évitez le mode privilégié et limitez les accès au système de fichiers.

**Le daemon Docker constitue une ressource sensible.** Le socket Docker et les accès administratifs au moteur ne doivent être exposés qu'aux processus et utilisateurs autorisés.

**L'image doit être sécurisée avant son lancement.** Il faut utiliser des sources fiables, contrôler les dépendances, maintenir les images de base et réduire les éléments inutiles de l'image finale.

**La chaîne d'approvisionnement doit être traçable.** Les résultats de scan, les SBOM, les informations de provenance et les digests aident à relier le code source à l'image effectivement déployée.

**Les secrets doivent rester hors des images.** Les mécanismes de gestion des secrets doivent protéger les valeurs pendant le build et pendant l'exécution. Un secret exposé doit être renouvelé ou révoqué, et pas seulement supprimé d'un fichier.

**Le réseau et le stockage doivent être limités au besoin.** Ne publiez que les ports nécessaires, segmentez les communications, limitez les montages et protégez les volumes persistants.

**Les ressources doivent être contrôlées.** Les limites de mémoire, de CPU et de processus réduisent certains risques de déni de service, tandis que les journaux et les métriques facilitent la détection des anomalies.

**Les contrôles doivent être appliqués dans le processus de livraison.** Les scans et les règles de sécurité doivent avoir des critères d'acceptation explicites. Un contrôle exécuté mais systématiquement ignoré ne protège pas réellement la chaîne.

Enfin, **la sécurité d'une image ne garantit pas la sécurité de son déploiement**. Une image correcte peut être exécutée avec des privilèges excessifs, exposée sur le mauvais réseau ou connectée à des données sensibles sans protection suffisante.

Une architecture de conteneurs robuste combine la sécurité du code, la confiance dans les images, la réduction des privilèges, l'isolation réseau et système, la protection des secrets, la surveillance et une procédure de réponse aux incidents testée.

La maturité se mesure à la capacité de prévenir les compromissions, de limiter leur impact, de détecter rapidement les anomalies et de remettre en service une version fiable avec des preuves de traçabilité suffisantes.