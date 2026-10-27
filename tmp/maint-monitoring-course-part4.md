## 5. Les objets Zabbix : hôtes, items, triggers et templates

### 5.1 Hôtes et interfaces

Un hôte Zabbix représente l'objet suivi. Son nom doit être stable et cohérent avec l'identité utilisée par les agents pour les contrôles actifs. Une interface indique le chemin de communication quand l'item en a besoin : agent, SNMP, IPMI ou JMX selon la configuration. Un check simple, un item calculé ou certains types de données peuvent ne pas nécessiter une interface classique.

Une convention de nommage peut combiner site, rôle et identifiant : **DOU-AGENCE01-RTR01**, **DC1-SW-CORE01** ou **DC1-LNX-APP01**. Évite d'incorporer dans le nom une propriété qui change souvent, comme le propriétaire ou l'adresse IP, si elle peut être gérée par des champs séparés. L'identité doit aider les recherches, le rapprochement avec l'inventaire et la déduplication d'événements.

### 5.2 Items : définir une donnée sans ambiguïté

Un **item** définit la donnée à collecter ou recevoir, le type de collecte, la clé ou la requête, l'intervalle, l'unité, le type d'information, la rétention et éventuellement le prétraitement. Les types et clés disponibles dépendent de la version et du composant.

| Famille | Exemple | Contrôle essentiel |
|---|---|---|
| Agent | CPU, mémoire, système de fichiers, processus | Clé disponible, permission et mode actif/passif. |
| SNMP | Statut d'interface, trafic, erreurs, température | OID, droits, unité et type de compteur. |
| ICMP ou check simple | Reachability, perte, latence | Portée du test et utilitaires disponibles. |
| HTTP ou API | Code HTTP, temps, réponse JSON | Authentification, certificat et contenu attendu. |
| Trap ou sender | Événement externe transmis | Récepteur, schéma et provenance. |
| Item dépendant ou calculé | Valeur dérivée d'une autre mesure | Prétraitement, unité et fraîcheur. |

Une valeur en octets ne doit pas être comparée directement à un seuil exprimé en pourcentage. Les noms doivent décrire la mesure et pas seulement répéter le nom du périphérique. La fréquence doit correspondre au besoin : trop courte, elle augmente le stockage ; trop longue, elle peut manquer un événement bref. Il faut fixer un délai de détection, évaluer la volatilité de la mesure et mesurer le coût de collecte.

### 5.3 Triggers et expressions temporelles

Un **trigger** transforme les données en état significatif. Il peut comparer une valeur à un seuil, rechercher l'absence de données ou détecter une évolution anormale. La durée fait partie de la logique : « CPU au-dessus de 90 % pendant cinq minutes » n'a pas la même signification qu'un seul échantillon. La persistance filtre certains pics, mais peut augmenter le délai de détection.

Exemples d'expressions modernes à adapter et à tester : le nom d'hôte et les clés d'items doivent réellement exister.

~~~text
max(/ROUTEUR-WAN01/icmpping,3m)=0
min(/SERVEUR-LINUX01/agent.ping,5m)=0
~~~

La seconde expression n'est pertinente que si la clé **agent.ping** existe dans la configuration de cet hôte et si sa sémantique correspond à l'intention. Vérifie la clé réelle, le type d'information, l'unité, la période et les valeurs reçues avant de copier une expression.

Un trigger doit avoir une gravité, une description et une condition de récupération compréhensibles. « Warning » doit appeler une action de vigilance ou de planification ; une gravité élevée doit correspondre à un impact supérieur. Des triggers qui se recouvrent peuvent créer plusieurs problèmes sur un même signal : contrôler les tags, la corrélation, les dépendances et les règles de récupération.

~~~mermaid
flowchart TD
  A[Valeurs de l'item] --> B[Expression du trigger]
  B --> C{Condition vraie ?}
  C -->|Non| D[Pas de problème]
  C -->|Oui| E[Événement]
  E --> F[Action ciblée]
  F --> G[Notification]
  B --> H[Condition de récupération]
  H --> I[Événement de récupération]
~~~

### 5.4 Templates, macros et héritage

Un template regroupe des items, triggers, graphes, règles de découverte et éléments réutilisables. Le rattacher à plusieurs hôtes compatibles évite de reproduire des configurations manuelles. On peut créer un modèle Linux commun, puis des modèles spécialisés pour les bases de données, serveurs Web, applications ou équipements SNMP.

~~~mermaid
flowchart TD
  A[Template Linux commun] --> B[Serveur Linux 01]
  A --> C[Serveur Linux 02]
  D[Template switch SNMP] --> E[Switch accès 01]
  D --> F[Switch accès 02]
  G[Macros globales] --> A
  H[Macros spécifiques] --> B
  H --> C
~~~

Les macros réutilisent des paramètres comme les seuils ou identifiants de site. Les valeurs sensibles nécessitent un mécanisme de secret et des permissions adaptés : une macro masquée dans l'interface ne garantit pas qu'elle est absente de tous les exports ou journaux.

L'héritage doit rester lisible. Un template universel qui comporte des contrôles inapplicables à beaucoup d'hôtes génère du bruit et augmente la charge. Crée des modèles par rôle, ajoute une spécialisation lorsque les matériels diffèrent et teste sur un hôte pilote avant de lier le template à toute la flotte.