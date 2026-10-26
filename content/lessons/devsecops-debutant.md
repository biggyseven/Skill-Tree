# DevSecOps : intégrer la sécurité au développement — Débutant

> **Mise en contexte.** Une équipe découvre une clé API publiée dans un dépôt et une bibliothèque vulnérable dans une application. Corriger ces problèmes juste avant la production coûte cher. DevSecOps consiste à intégrer des contrôles de sécurité au cycle de développement, le plus tôt possible et de façon répétable, sans attendre une revue finale isolée.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois pouvoir expliquer DevSecOps, distinguer les principales familles d’outils, identifier les secrets dans un pipeline, comprendre les résultats d’un scanner et proposer un flux simple qui vérifie le code avant publication.

## Prérequis

Connaître les bases de Git, des dépôts, des pipelines CI/CD et des composants logiciels. Les exercices peuvent être réalisés dans un dépôt de démonstration sans envoyer de code sensible ni de secret réel.

## 1. Qu’est-ce que DevSecOps ?

DevSecOps associe les pratiques de développement, d’exploitation et de sécurité. Il ne signifie pas qu’un outil scanner garantit que l’application est sûre ni que tous les développeurs deviennent des experts en sécurité. Il vise plutôt à rendre les contrôles compréhensibles, automatiques et intégrés au travail quotidien.

Les principes fondamentaux sont :
- tester tôt plutôt que découvrir les vulnérabilités à la dernière minute ;
- définir des règles versionnées et reproductibles ;
- limiter les privilèges des comptes et des jobs ;
- conserver des preuves utiles sans exposer de données sensibles ;
- traiter les alertes selon leur contexte, leur exploitabilité et l’impact ;
- maintenir des mécanismes de correction et de dérogation documentés.

## 2. Où placer les contrôles ?

~~~text
Code / Pull request
   ├── format et tests
   ├── analyse statique du code (SAST)
   ├── recherche de secrets
   ├── analyse des dépendances (SCA)
   └── revue et décision
          |
        Build
          ├── analyse d'image
          ├── génération de métadonnées / SBOM
          └── artefact identifiable
                 |
             déploiement staging
                 ├── tests dynamiques (DAST)
                 ├── vérifications de configuration
                 └── approbation selon le risque
~~~

Les étapes exactes dépendent du langage et du type de projet. Une bibliothèque cliente n’a pas les mêmes contrôles qu’un serveur exposé à Internet ou qu’un contrôleur industriel.

## 3. Les principales familles d’outils

| Contrôle | Ce qu’il examine | Limite importante |
|---|---|---|
| SAST | Code source et motifs de vulnérabilité | Peut produire des faux positifs et manquer des chemins complexes |
| SCA | Dépendances directes et transitives | Une vulnérabilité nécessite une analyse de version, de fonction et d’exposition |
| Recherche de secrets | Clés, jetons et mots de passe potentiellement publiés | Ne remplace pas l’inventaire et la rotation des secrets |
| Analyse d’image | Paquets et couches d’une image de conteneur | Une image sans alerte n’assure pas une configuration sûre à l’exécution |
| DAST | Application en fonctionnement | Couverture limitée aux surfaces testées |
| Scan IaC | Fichiers d’infrastructure déclarative | Les résultats doivent être rapprochés de l’architecture et de la politique |
| SBOM | Inventaire des composants livrés | L’inventaire n’est pas un correctif ; il doit être maintenu à jour |

Un bon pipeline combine plusieurs preuves. Un scan statique est utile avant le déploiement, tandis qu’un test dynamique exige un environnement où l’application peut être sollicitée.

## 4. Secrets : prévenir, détecter et répondre

Les secrets comprennent les jetons d’accès, clés privées, mots de passe, identifiants cloud et clés de signature. Ils ne doivent pas être écrits directement dans le code ou les journaux.

Mauvaises pratiques :
- ajouter un fichier d’environnement de production dans Git ;
- imprimer toutes les variables d’environnement pour déboguer ;
- partager un token entre tous les environnements ;
- croire que supprimer une clé dans le dernier commit la retire de l’historique.

Bonnes pratiques :
1. Utiliser un gestionnaire de secrets ou le mécanisme prévu par la plateforme CI.
2. Donner à chaque job et environnement uniquement les droits nécessaires.
3. Masquer les valeurs sensibles dans les logs, sans compter uniquement sur le masquage automatique.
4. En cas de fuite, révoquer ou faire tourner le secret, examiner l’usage passé et réévaluer les permissions.
5. Ajouter la prévention à l’outillage local et au pipeline pour réduire les récidives.

Un secret publié doit être considéré comme compromis jusqu’à preuve contraire. Le supprimer du dépôt ne suffit pas.

## 5. Dépendances et versions

Une application dépend souvent de bibliothèques directes et transitives. Un scanner SCA compare les versions déclarées avec des bases de vulnérabilités et fournit des pistes d’investigation. Examine le paquet, la version, la dépendance qui l’introduit, la présence du composant dans l’artefact et les chemins qui exposent la fonction vulnérable.

Ne mets pas automatiquement à jour toutes les dépendances sans tests. Un correctif peut exiger une version majeure, modifier une API ou introduire une incompatibilité. Préfère une mise à jour ciblée, des tests de régression et une date de traitement associée au niveau de risque.

## 6. Construire un pipeline sûr

Exemple conceptuel pour un dépôt d’application :

~~~yaml
name: controles-securite
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Tests
        run: ./scripts/test.sh
      - name: Analyse SAST
        run: ./scripts/sast.sh
      - name: Verifier les dependances
        run: ./scripts/dependency-check.sh
~~~

Les noms sast.sh et dependency-check.sh sont des exemples de scripts à fournir par le projet ; ce YAML ne devient pas fonctionnel tant que ces scripts n’existent pas et que les outils retenus ne sont pas configurés. C’est un schéma de conception, pas une configuration directement exécutable.

Configure les permissions de jetons au minimum nécessaire. Évite d’exposer des secrets aux workflows qui traitent des contributions non fiables. Pour toute étape qui publie une image ou un paquet, sépare autant que possible la validation d’un artefact et la permission de le publier.

## 7. Tri des alertes et gestion des faux positifs

Une alerte ne doit pas être ignorée parce qu’elle gêne le pipeline. Il faut examiner :
- la gravité et la fiabilité du résultat ;
- l’exposition de la ressource ;
- l’existence d’un correctif ;
- la présence du composant dans la version déployée ;
- les mesures temporaires qui réduisent le risque ;
- la date et la personne responsables du suivi.

Une dérogation doit avoir une justification, un périmètre, un propriétaire et une expiration. Ne crée pas une suppression globale de règles pour faire passer une livraison.

## 8. TP guidé : sécuriser une Pull Request

Dans un dépôt de démonstration :
1. Ajoute un test automatisé qui échoue si le code ne respecte pas le contrat.
2. Ajoute un scanner de dépendances adapté à l’écosystème.
3. Active une recherche de secrets sans utiliser de véritable clé dans l’exercice.
4. Vérifie que la Pull Request ne reçoit que les permissions nécessaires.
5. Introduis une vulnérabilité factice ou une dépendance de test connue, puis observe le rapport.
6. Enregistre le résultat et explique comment une équipe devrait corriger ou documenter l’alerte.

**Réussite :** les contrôles s’exécutent automatiquement, le résultat est lisible, les secrets ne sont pas exposés et une alerte entraîne une décision plutôt qu’un contournement silencieux.

## Exercices corrigés

**1. Quelle différence entre SAST et DAST ?**  
SAST examine principalement le code ou ses représentations sans exiger que l’application cible fonctionne. DAST teste l’application en fonctionnement via ses interfaces. Ils détectent des classes de problèmes différentes.

**2. Une clé a été supprimée du dernier commit. Est-elle sûre ?**  
Non. Elle a pu rester dans l’historique ou être copiée ailleurs. Il faut la révoquer ou la faire tourner, analyser les utilisations et mettre en place une prévention.

**3. Pourquoi ne pas donner un jeton d’administration à chaque job ?**  
Parce qu’une compromission de job deviendrait une compromission de l’environnement entier. Les permissions doivent être réduites au besoin réel et séparées entre test et production.

**4. Une alerte SCA critique signifie-t-elle toujours qu’une application est exploitable ?**  
Pas automatiquement. Il faut confirmer la version, l’usage, le chemin d’exposition et les conditions d’exploitation. Cela ne justifie pas de l’ignorer : la décision et son délai doivent être documentés.

## Défi final corrigé

Une application web doit être livrée chaque semaine. Conçois une chaîne minimale qui bloque les erreurs de test, détecte les secrets et vulnérabilités de dépendances, protège les secrets de déploiement et exige une décision explicite pour une alerte critique.

**Correction attendue :** tests et scans à la Pull Request ; permissions minimales ; secrets injectés depuis un gestionnaire approuvé ; artefact versionné ; contrôles à nouveau avant production ; alertes assignées avec priorité, échéance et propriétaire ; aucune exception permanente sans justification. La chaîne doit conserver les rapports sans inclure les valeurs secrètes.

## À retenir

DevSecOps est une pratique de livraison, pas un produit unique. Le but est d’obtenir des contrôles précoces, une réponse responsable aux alertes, une gestion rigoureuse des secrets et des décisions auditables sans transformer le pipeline en boîte noire.