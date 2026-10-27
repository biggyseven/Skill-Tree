## 6. Agents Zabbix : contrôle actif et passif

### 6.1 Contrôle passif

En mode passif, le serveur Zabbix ou le proxy contacte l'agent et lui demande une donnée. L'agent écoute habituellement sur TCP 10050, sauf changement de configuration. Le collecteur doit pouvoir atteindre l'agent ; le pare-feu doit permettre ces connexions uniquement depuis les sources de supervision autorisées.

Le paramètre **Server** de l'agent limite les adresses autorisées à effectuer les contrôles passifs. Le laisser trop ouvert augmente la surface d'attaque. Vérifie aussi que le nom déclaré correspond à l'identité attendue, que l'agent peut lire les données et que les clés existent dans la version installée.

### 6.2 Contrôle actif

En mode actif, l'agent ouvre une connexion vers le serveur ou le proxy, récupère la liste des checks actifs qui lui sont attribués et envoie les valeurs. Le port du serveur Zabbix est habituellement TCP 10051. Ce mode est utile lorsque le réseau de la cible autorise les connexions sortantes vers la supervision mais interdit les connexions entrantes depuis le centre.

~~~mermaid
sequenceDiagram
  participant A as Agent actif
  participant Z as Serveur ou proxy
  participant DB as Base de données
  A->>Z: Demander configuration active
  Z-->>A: Items et paramètres
  A->>A: Collecter les valeurs
  A->>Z: Transmettre les mesures
  Z->>DB: Prétraiter et enregistrer
~~~

En passif, vérifier le chemin du serveur vers l'agent. En actif, vérifier la route sortante depuis l'agent vers le collecteur. Si les deux modes sont utilisés, documenter chaque flux et tester les items séparément.

### 6.3 Exemple de configuration agent

Voici des paramètres usuels à adapter au fichier et aux options de la version installée :

~~~ini
Server=192.0.2.20
ServerActive=192.0.2.20:10051
Hostname=SERVEUR-LINUX01
Timeout=5
~~~

**Server** désigne les sources autorisées pour les checks passifs. **ServerActive** désigne le serveur ou proxy auquel l'agent se connecte pour les checks actifs. **Hostname** doit correspondre au nom configuré côté Zabbix pour les checks actifs usuels. Le timeout doit être approprié aux contrôles autorisés. L'exemple ne montre pas toutes les options, notamment celles relatives au chiffrement, aux logs, aux modules ou scripts spécifiques.

Le protocole et les options varient selon les versions de l'agent. Agent et Agent 2 partagent une base de protocole unifiée dans les versions modernes, mais leurs fonctions et plugins doivent être vérifiés dans la documentation. Ne déploie pas une configuration identique sur un parc hétérogène sans essai pilote.

~~~mermaid
flowchart LR
  A[Agent et paramètres] --> B{Mode du check}
  B -->|Passif| C[Serveur vers agent TCP 10050]
  B -->|Actif| D[Agent vers serveur TCP 10051]
  C --> E[ACL et pare-feu]
  D --> E
  E --> F[Valeurs récentes]
~~~

### 6.4 Sécuriser les agents

Les données de supervision révèlent versions, chemins, processus et caractéristiques du système. Certains mécanismes peuvent aussi permettre des actions sensibles lorsqu'ils sont activés. Appliquer le moindre privilège, le filtrage réseau, le chiffrement disponible et la séparation des comptes. Désactiver les commandes distantes non nécessaires et examiner les modules externes avant leur déploiement.

Ne place jamais de secret réel dans un cours, un ticket largement partagé, un script commité ou une capture d'écran. Si un secret a été enregistré dans Git, le supprimer du fichier courant ne suffit pas : il faut le révoquer ou le renouveler, contrôler son utilisation et traiter l'historique exposé selon les procédures de sécurité.