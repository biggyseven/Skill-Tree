# Pipelines DevSecOps et sécurité de la chaîne logicielle — Intermédiaire

> **Mise en contexte.** Une équipe dispose déjà de tests et de scanners, mais les alertes sont nombreuses, les images ne sont pas reliées au commit source et un jeton de déploiement est accessible à trop de workflows. Le niveau intermédiaire consiste à intégrer les contrôles dans un processus de livraison réellement exploitable, avec critères de décision et responsabilités.

## Objectifs d’apprentissage

Tu apprendras à concevoir les étapes d’un pipeline DevSecOps, hiérarchiser les alertes, sécuriser la construction des artefacts, comprendre le rôle d’une SBOM, analyser l’IaC, protéger les identités CI/CD et définir les critères d’acceptation d’une livraison.

## Prérequis

Connaître Git, les Pull Requests, les pipelines CI/CD, les tests, les images de conteneur et les familles SAST, SCA, DAST et recherche de secrets. Ce cours prolonge les fondamentaux DevSecOps ; il ne remplace pas la formation de base.

## 1. Organiser le pipeline selon le risque

Un scanner exécuté au mauvais moment peut être inutile, et une étape trop stricte sans processus de correction pousse les équipes à contourner le système. Définis pour chaque contrôle l’objet inspecté, le moment d’exécution, le seuil de blocage, le responsable du tri et la preuve conservée.

~~~text
Pull request
  -> format + tests + SAST + secrets + SCA
  -> revue du changement
Commit accepté
  -> construction déterministe
  -> analyse d'image + SBOM + provenance
Staging
  -> DAST + tests de configuration + smoke tests
Production
  -> approbation, déploiement progressif, observation
~~~

Toutes les alertes n’ont pas nécessairement le même seuil. Une clé privée exposée ou un contrôle d’accès critique mérite une réponse immédiate ; une vulnérabilité dans une dépendance non utilisée peut exiger une investigation, un contournement temporaire et une correction planifiée. La décision doit rester traçable.

## 2. SAST, SCA, DAST et IaC : combiner les preuves

Le SAST analyse le code source ou une représentation dérivée. Le SCA compare les composants aux données de vulnérabilité, identifie les dépendances transitives et peut contribuer à la génération d’une SBOM. Le DAST recherche des problèmes dans une application démarrée. Les scanners IaC analysent les déclarations d’infrastructure, par exemple des règles de pare-feu trop ouvertes ou des stockages publics.

Le pipeline doit conserver le nom de l’outil, sa version, la configuration appliquée, la version du code, les résultats et la décision de tri. Sans contexte de version, il devient difficile de savoir si un rapport correspond à l’artefact en production.

## 3. SBOM, provenance et intégrité des artefacts

Une SBOM (Software Bill of Materials) est un inventaire de composants présents dans un logiciel. Elle permet de répondre plus vite à la question « cette version contient-elle la bibliothèque concernée ? ». Elle ne certifie pas qu’un logiciel est sûr, et une SBOM doit correspondre à l’artefact effectivement livré.

La provenance décrit des éléments de la construction : source, paramètres, outils et identité du processus. Les signatures d’artefacts permettent de vérifier qu’un artefact provient d’une identité attendue et n’a pas été modifié de façon inattendue. Leur valeur dépend de la protection des identités, des clés et des systèmes de build.

Contrôles recommandés :
- construire à partir d’une révision source identifiée ;
- épingler les dépendances et les images de base ;
- conserver les rapports et la SBOM avec la version d’artefact ;
- restreindre l’écriture dans le registre ;
- vérifier l’origine et la signature avant déploiement lorsque l’environnement le permet.

## 4. Identités et permissions des workflows

Les jetons CI/CD sont souvent des chemins d’accès très puissants. Un pipeline de tests n’a normalement pas besoin des mêmes permissions qu’un job qui publie un artefact, et un déploiement staging ne doit pas disposer par défaut de toutes les permissions de production.

Applique une séparation claire :
- exécuter les tests avec permissions de lecture ;
- réserver la publication à une étape dédiée et protégée ;
- utiliser des identités de courte durée lorsque la plateforme le permet ;
- exiger une approbation pour les environnements sensibles ;
- séparer les secrets par application et environnement ;
- protéger les workflows qui exécutent du contenu fourni par un tiers.

Un workflow qui traite une Pull Request non fiable ne doit pas recevoir automatiquement les secrets de production. Évalue également les actions tierces, les scripts de build, les dépendances de pipeline et le risque d’exécution de code sur l’agent.

## 5. Gestion de secrets et réponse à l’incident

La détection au commit n’est qu’une couche. En cas de fuite :
1. révoque ou fais tourner le secret ;
2. identifie les systèmes et opérations qu’il autorisait ;
3. recherche une activité anormale dans les journaux ;
4. limite les permissions et remplace les valeurs ;
5. examine l’historique et les copies éventuelles ;
6. ajoute des garde-fous et documente la cause racine.

Un nettoyage de l’historique peut être nécessaire dans certains cas, mais il ne remplace jamais la révocation. La correction doit couvrir les copies, les logs, les caches d’artefacts et les environnements où le secret a pu être utilisé.

## 6. Politique de blocage et exceptions

Établis un seuil de blocage compréhensible. Un exemple de politique peut bloquer un secret confirmé ou une vulnérabilité critique exploitable, alors que les résultats moins graves sont enregistrés et affectés à un propriétaire avec une échéance. Les seuils exacts doivent tenir compte du produit, du risque métier et de la capacité de réponse.

Une exception doit contenir le résultat concerné, la raison, l’impact, les mesures compensatoires, le propriétaire, la date de révision et la date d’expiration. Ne transforme pas une suppression de règles en politique permanente. Les équipes doivent pouvoir corriger le signalement et faire lever l’exception.

## 7. Analyse de configuration et infrastructure as code

Les contrôles IaC recherchent des paramètres dangereux dans des fichiers déclaratifs : stockage accessible publiquement, ports ouverts trop largement, chiffrement absent, journalisation insuffisante ou permissions excessives. Le scan doit fonctionner sur les Pull Requests et être rapproché de l’état réel de l’infrastructure.

Un résultat statique ne décrit pas toujours le contexte complet. Une règle réseau ouverte à toutes les sources a un risque différent selon qu’elle protège un service public prévu ou une base de données privée. La bonne démarche combine politique standard, contexte de l’architecture, approbation et validation après déploiement.

## 8. TP guidé : sécuriser une publication d’image

**Situation :** le dépôt produit une image de conteneur et la déploie en staging.

1. Déclenche tests, SAST et SCA lors de la Pull Request.
2. Vérifie que les secrets ne sont ni dans les fichiers suivis ni imprimés dans les logs.
3. Construis une image liée au commit exact.
4. Exécute un scan sur l’image finale et génère une SBOM correspondant à cette image.
5. Publie l’artefact seulement depuis un workflow protégé.
6. En staging, exécute un DAST et un test de santé.
7. Enregistre les versions et les résultats.
8. Simule une alerte élevée et démontre son affectation, sa décision et son délai.

**Critères de réussite :** un artefact traçable, une SBOM attachée à la version, des permissions minimales, une alerte traitée et une séparation entre tests et publication.

## 9. Diagnostic des faux positifs et des alertes non applicables

Ne ferme pas une alerte simplement parce que son exploitation semble improbable. Vérifie la version affectée, le chemin de dépendance, la présence effective dans l’image, l’entrée contrôlée par un utilisateur et les conditions nécessaires à l’exploitation. Conserve le raisonnement et la version du scanner. Une mise à jour du scanner peut changer le résultat ; l’historique de tri doit permettre d’expliquer pourquoi.

## Exercices corrigés

**1. Pourquoi une SBOM n’est-elle pas une preuve de sécurité ?**  
Elle décrit les composants identifiés, mais n’élimine pas les vulnérabilités ni les erreurs de conception. Elle facilite l’analyse d’impact et doit correspondre à l’artefact livré.

**2. Pourquoi séparer le job de test du job de publication ?**  
Le job de test traite plus souvent des contributions non fiables. Lui donner des droits de publication permettrait à une modification malveillante de remplacer un artefact ou d’accéder aux environnements.

**3. Que faire en premier après la découverte d’un secret exposé ?**  
Le révoquer ou le faire tourner, puis examiner les usages passés. Supprimer la chaîne du dernier commit ne suffit pas.

**4. Pourquoi un scanner IaC peut-il avoir besoin d’un arbitrage humain ?**  
Il peut identifier une configuration risquée sans connaître la totalité du contexte architectural. L’arbitrage doit vérifier le contexte sans supprimer les contrôles génériques.

## Défi final corrigé

Conçois une chaîne qui refuse une image non analysée, associe SBOM et provenance au commit, réserve la publication à une identité protégée, déploie en staging et documente les exceptions de sécurité.

**Correction :** la Pull Request passe les tests et scans ; la construction est liée à une révision identifiée ; l’image est analysée ; les rapports et la SBOM sont archivés ; la publication exige les permissions minimales ; la promotion vérifie l’identité de l’artefact ; les alertes bloquantes doivent être corrigées ou faire l’objet d’une exception temporaire approuvée.

## Synthèse

Un pipeline DevSecOps intermédiaire ne se contente pas de lancer des scanners. Il relie les résultats à une version précise, contrôle les identités et les permissions, définit des seuils de décision et produit une chaîne d’artefacts traçables.