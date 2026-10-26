# Service Mesh (Istio, Linkerd) — Débutant

> **Mise en contexte.** Une application répartie sur plusieurs microservices doit chiffrer les échanges internes, mesurer les appels et gérer les délais d’attente. Ajouter les mêmes fonctions dans chaque application rend la maintenance coûteuse. Un Service Mesh propose une couche dédiée à la communication entre services, généralement autour d’un cluster Kubernetes.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois expliquer la place d’un Service Mesh, distinguer plan de contrôle et plan de données, comprendre le rôle des proxys, décrire mTLS, observer un flux et identifier les situations où un mesh est utile ou trop complexe.

## Prérequis

Connaître les bases des conteneurs, des pods et des services Kubernetes, les adresses IP, les ports TCP, DNS et TLS. Les exemples sont conceptuels et n’exigent pas d’installer un mesh sur un cluster de production.

## 1. Pourquoi parler de Service Mesh ?

Dans une architecture à microservices, le service A appelle le service B, qui appelle C. Chaque service doit gérer la découverte des destinations, les délais d’attente, les erreurs, la télémétrie et parfois la sécurité du transport. Les implémentations indépendantes finissent par diverger.

Un Service Mesh déplace une partie de ces fonctions dans l’infrastructure de communication. Il ne remplace ni le code métier ni l’API de l’application. Il ajoute des composants, des politiques, des certificats et un besoin d’exploitation.

~~~text
Service A -> proxy A ==== réseau ==== proxy B -> Service B
                      \             /
                       politiques, TLS,
                       métriques et traces

Plan de contrôle : distribue la configuration et gère les identités
Plan de données   : traite les flux réels des applications
~~~

Le motif du proxy adjacent à chaque workload, appelé souvent sidecar, est courant. D’autres architectures existent, notamment des modes sans sidecar ; le modèle exact dépend de la solution et de sa version.

## 2. Ce que fait un Service Mesh

- **Découverte et routage** : choisir une destination selon la configuration et les règles.
- **Sécurité du transport** : authentifier les workloads et chiffrer les connexions avec mTLS.
- **Gestion du trafic** : appliquer des délais d’attente, des limites, des répartitions et des politiques de reprise.
- **Observabilité** : produire des métriques, des journaux et parfois des traces associées aux appels.
- **Politique d’accès** : limiter les communications entre services selon l’identité et le contexte.

Toutes les fonctions ne sont pas activées par défaut. Les règles de reprise peuvent amplifier une surcharge si elles sont mal configurées ; mTLS exige une gestion des certificats et une politique d’identité cohérente.

## 3. Plan de contrôle et plan de données

Le plan de contrôle calcule ou distribue la configuration, gère la découverte et les identités. Le plan de données transporte les flux. Il peut être constitué de proxys qui interceptent les communications des applications.

Une panne du plan de contrôle ne signifie pas toujours que tous les flux existants s’arrêtent immédiatement ; cela dépend du comportement des composants et de la configuration déjà distribuée. Cependant, les changements de politique ou la découverte de nouveaux endpoints peuvent être affectés. L’équipe doit comprendre ce qui reste en fonctionnement quand les composants de gestion deviennent indisponibles.

## 4. mTLS et identité des services

TLS chiffre le transport et authentifie le serveur selon les certificats et la configuration du client. Le mTLS demande également un certificat au client, afin que les deux extrémités prouvent leur identité. Dans un mesh, les workloads peuvent recevoir des identités temporaires et des certificats gérés par le système.

Ce mécanisme est utile pour réduire les connexions non authentifiées, mais n’est pas une solution complète à tous les problèmes de sécurité. Il faut aussi limiter les autorisations, vérifier les identités attendues, protéger le plan de contrôle et comprendre les chemins de flux. Le chiffrement ne garantit pas que le service appelé est autorisé à exécuter l’action métier demandée.

## 5. Routage et résilience

La configuration du mesh peut répartir le trafic vers différentes versions, imposer des délais d’attente ou limiter le nombre de connexions simultanées. Une stratégie de retries doit tenir compte du caractère idempotent des opérations et du délai global. Répéter une requête de paiement sans idempotence peut créer un dommage métier.

Une configuration sûre prévoit :
- un délai total cohérent avec le contrat applicatif ;
- des retries bornés, avec backoff ;
- des limites de concurrence adaptées ;
- des métriques de rejet et de latence ;
- une procédure pour revenir à la règle précédente.

Le mesh ne répare pas une base de données saturée ni un code qui bloque indéfiniment. Il expose et encadre les échanges, mais la capacité de l’application reste essentielle.

## 6. Istio et Linkerd

Istio et Linkerd sont des solutions de Service Mesh pour les environnements cloud-native, mais elles diffèrent par leur architecture, l’étendue de leurs fonctions, leur complexité opérationnelle et leur modèle de configuration. Le bon choix ne se résume pas à une liste de fonctionnalités : il dépend de la topologie, des compétences de l’équipe, des exigences de sécurité et du coût d’exploitation.

Avant d’adopter un mesh, pose des questions :
- Le besoin existe-t-il déjà dans l’ingress, la bibliothèque cliente ou la plateforme ?
- Faut-il une identité forte entre workloads ?
- Quelle équipe maintiendra les certificats et les politiques ?
- Quelles métriques sont nécessaires pour détecter une panne ?
- Le parc de services et le volume de trafic justifient-ils cette couche ?

Pour un petit projet, des contrôles Kubernetes et une configuration TLS directe peuvent être suffisants. Un Service Mesh devient intéressant quand le besoin est transversal et qu’une équipe peut maintenir sa complexité.

## 7. Observer un appel

Pour diagnostiquer un flux, identifie d’abord l’origine, la destination, le protocole, le port et le résultat attendu. Compare ensuite le comportement de l’application, les logs du proxy, les métriques de succès/erreur et la latence.

~~~text
Appel échoué
  1. DNS et endpoint corrects ?
  2. Pod et service disponibles ?
  3. Connexion TCP et certificat acceptés ?
  4. Politique d'autorisation compatible ?
  5. Route, timeout ou retry en cause ?
  6. Service métier en bonne santé ?
~~~

Ne commence pas par modifier simultanément plusieurs politiques. Une modification à la fois permet de savoir si le diagnostic était correct et d’éviter d’élargir accidentellement les accès.

## 8. TP guidé : cartographier les échanges

Dans un cluster de test ou un schéma, représente trois services A, B et C. Identifie les appels, les ports et les identités. Pour chaque appel, note si le besoin porte sur TLS, authentification mutuelle, restrictions d’accès, délais ou métriques.

1. Dessine le flux A vers B et B vers C.
2. Indique l’endroit où se trouveraient les proxys dans un modèle sidecar.
3. Identifie ce que gère le plan de contrôle.
4. Définis une métrique de succès, une métrique de latence et un journal utile.
5. Décris le comportement attendu si B devient indisponible.
6. Explique pourquoi multiplier les retries peut aggraver une surcharge.

**Réussite :** chaque flux a une destination, une identité attendue, des contrôles et une stratégie de diagnostic.

## Exercices corrigés

**1. Le Service Mesh remplace-t-il le service métier ?**  
Non. Il encadre la communication entre workloads et fournit des fonctions transversales, sans implémenter les règles métier.

**2. Que signifie mTLS ?**  
TLS mutuel : les deux extrémités authentifient l’autre à l’aide de certificats, tout en protégeant le transport selon la configuration TLS.

**3. Un mesh garantit-il qu’un service est invulnérable ?**  
Non. Il peut renforcer l’identité et les échanges, mais les applications, leurs données, les politiques d’autorisation et le plan de contrôle doivent toujours être sécurisés.

**4. Pourquoi limiter les retries ?**  
Ils peuvent amplifier la charge pendant une panne et répéter une opération non idempotente. Il faut des limites, un backoff et un délai global cohérent.

## Défi final corrigé

Pour une plateforme de trois microservices, propose une politique de communication qui chiffre les flux, donne une identité aux workloads, refuse par défaut les appels non nécessaires et permet de détecter une hausse d’erreurs.

**Solution :** cartographier les appels légitimes ; activer et vérifier mTLS dans un environnement de test ; définir des règles d’autorisation minimales ; instrumenter les erreurs et la latence ; borner les timeouts et retries ; tester un service indisponible ; documenter la procédure de retour arrière. Une politique de sécurité ne doit pas être appliquée à l’ensemble du cluster sans test d’impact.

## À retenir

Le Service Mesh est une couche de communication qui peut centraliser identité, sécurité du transport, routage et observabilité. Il apporte de la valeur lorsque le besoin est réel et que l’équipe peut en exploiter les composants sans masquer la complexité.