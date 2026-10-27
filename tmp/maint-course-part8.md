## 10. Choisir entre Nagios et Zabbix

Les deux solutions peuvent superviser des hôtes, états, seuils et services, mais leur modèle diffère.

| Critère | Nagios Core | Zabbix |
|---|---|---|
| Modèle central | Hôtes, services, commandes et plugins | Hôtes, interfaces, items, triggers, templates et événements |
| Collecte | Plugins et commandes, checks actifs et résultats passifs | Agents, SNMP et types d'items variés selon version |
| Historique et graphes | Données de performance ; outils complémentaires possibles | Historique et tendances intégrés au modèle de données |
| Réutilisation | Templates d'objets, groupes, commandes et héritage | Templates, macros, prototypes et découverte |
| Extension | Plugins et intégrations externes | Types d'items, agents, proxies, prétraitement et intégrations |
| Compétence centrale | Commandes, plugins, états et notifications | Items, triggers, templates, rétention, proxies et actions |
| Point de vigilance | Organisation des configurations et composants associés | Complexité des modèles et volume de collecte |

Nagios est souvent naturel pour une équipe qui veut définir explicitement des contrôles spécialisés et dispose déjà de nombreux plugins. Zabbix convient lorsqu'on veut regrouper collecte, templates, historique, graphes, découverte et actions. Ce sont des tendances, pas une règle absolue : comparer les outils sur un échantillon représentatif du vrai parc.

~~~mermaid
flowchart TD
  A[Besoin et contraintes] --> B{Priorité dominante}
  B -->|Plugins et checks ciblés| C[Évaluer Nagios]
  B -->|Historique et templates| D[Évaluer Zabbix]
  C --> E[Pilote représentatif]
  D --> E
  E --> F[Mesurer qualité et coût]
  F --> G[Décision documentée]
~~~

Une coexistence ou une migration peut être pertinente, mais introduit des risques de doublons et de règles divergentes. Définir quel outil fait foi pour chaque service, où se trouve l'historique de référence et comment les événements sont corrélés.

## 11. Dépannage méthodique

### 11.1 Méthode commune

Lorsqu'une alerte apparaît, commencer par confirmer la cible, la période, le dernier résultat valide et la source de données. Déterminer ensuite si l'on est face à une panne réelle, une mesure absente, un seuil incorrect ou un problème de la plateforme. Ne pas redémarrer immédiatement un service sans recueillir les preuves disponibles : un redémarrage peut effacer des éléments utiles ou aggraver l'incident.

~~~mermaid
flowchart TD
  A[Alerte reçue] --> B[Confirmer cible et heure]
  B --> C{Valeur récente ?}
  C -->|Non| D[Diagnostiquer collecte]
  C -->|Oui| E[Comparer seuil et historique]
  D --> F[Agent réseau accès moteur]
  E --> G[Test indépendant]
  F --> H[Défaut de collecte possible]
  G --> I[Panne réelle ou faux positif]
  H --> J[Tracer résultat et action]
  I --> J
~~~

### 11.2 Diagnostiquer un check Nagios

Lire le statut, le texte complet du plugin, ses arguments, la tentative courante et les logs. Si le check est **UNKNOWN**, examiner en priorité la commande, les droits, la résolution DNS, les bibliothèques, l'authentification et le timeout. Si plusieurs services d'un hôte échouent simultanément, vérifier le contrôle d'hôte, la passerelle et le chemin de gestion. Si le service est disponible par un test indépendant mais le check échoue, le défaut est probablement dans la méthode de contrôle ou son chemin réseau.

~~~mermaid
flowchart TD
  A[Service Nagios non OK] --> B{Type de retour}
  B -->|UNKNOWN| C[Commande et exécution]
  B -->|WARNING ou CRITICAL| D[Mesure et seuil]
  B -->|Hôte inaccessible| E[Route et dépendance]
  C --> F[Arguments droits timeout]
  D --> G[Contre-test autorisé]
  E --> H[Passerelle ou lien]
  F --> I[Recontrôler]
  G --> I
  H --> I
~~~

### 11.3 Diagnostiquer une valeur Zabbix absente

Commencer par l'item et son horodatage : existe-t-il, l'interface est-elle correcte, quelle méthode utilise-t-il, quand la dernière valeur a-t-elle été reçue ? Ensuite vérifier l'agent ou le proxy, les routes, les ports, l'identité de l'hôte, le chiffrement et les logs. Si la valeur est visible mais que le trigger ne passe pas à problème, examiner l'expression, la clé, la fenêtre temporelle et l'historique requis.

~~~mermaid
flowchart TD
  A[Problème Zabbix] --> B[Dernière valeur item ?]
  B -->|Non| C[Agent SNMP proxy réseau]
  B -->|Oui| D[Expression du trigger]
  D --> E{Événement créé ?}
  E -->|Non| F[Seuil unité fenêtre]
  E -->|Oui| G[Action et opérations]
  G --> H[Média destinataire horaires]
  C --> I[Tester connectivité et accès]
  F --> J[Correction et retest]
  H --> J
  I --> J
~~~

### 11.4 Une notification n'est pas reçue

Si l'événement existe mais que le message n'arrive pas, le défaut peut être dans la chaîne de notification et non dans le trigger. Examiner les conditions de l'action, sévérité, tags, utilisateur, média, plage horaire, limitation de répétition, serveur SMTP ou webhook, puis les logs. Tester le média avec la fonction prévue par la version. Modifier le seuil n'aidera pas si le problème se trouve dans l'acheminement.

### 11.5 Files d'attente et charge

Un grand nombre d'alertes simultanées peut représenter une panne réelle, mais aussi un retard de collecte. Surveiller la durée des checks, les files d'attente, les processus de collecte, la base, le disque et l'écart entre la valeur attendue et le dernier échantillon reçu. Augmenter tous les intervalles sans diagnostic peut réduire la charge mais dégrader la détection. Identifier le goulot, vérifier la distribution des hôtes et comparer le volume aux objectifs.

### 11.6 Pourquoi tester depuis le collecteur

Un poste utilisateur et un serveur de supervision peuvent avoir des routes et permissions différentes. Le serveur peut résoudre un nom par un autre DNS ou se trouver derrière une ACL spécifique. Un test « depuis mon PC » ne prouve donc pas que le check configuré fonctionnera depuis Nagios ou le proxy Zabbix. Reproduire les tests depuis le vrai point de collecte et capturer la même destination, la même résolution et le résultat horodaté.

### 11.7 Corréler sans masquer

Une corrélation correcte simplifie une cascade de symptômes autour d'une cause commune. Elle ne doit pas supprimer les événements indépendants ou empêcher une équipe de voir une dégradation locale. Vérifier les dépendances sur plusieurs scénarios : panne du parent, panne d'un seul service, panne du collecteur et événements qui coïncident mais n'ont pas de cause commune.
