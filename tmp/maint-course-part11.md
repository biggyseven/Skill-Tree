## 15. Checklist d'exploitation avant production

- [ ] Tous les actifs critiques ont un nom stable, un propriétaire, une criticité et des dépendances documentées.
- [ ] Chaque check possède une définition, une unité, une fréquence et un résultat attendu.
- [ ] Les plugins Nagios ont été testés et leurs codes de retour sont compris.
- [ ] Les objets, macros, intervalles, tentatives et dépendances Nagios sont validés avant rechargement.
- [ ] Les items Zabbix existent et fournissent des valeurs récentes.
- [ ] Les templates et règles de découverte ne créent pas des milliers d'items sans usage.
- [ ] Les triggers et leurs conditions de récupération ont été testés.
- [ ] Les actions, médias, utilisateurs et canaux d'escalade sont testés de bout en bout.
- [ ] Les flux de gestion sont limités aux sources autorisées et utilisent le chiffrement disponible.
- [ ] Les identifiants sensibles sont absents des fichiers versionnés, rapports diffusés et captures.
- [ ] Le serveur, la base, les proxies, les agents et les canaux de notification sont eux-mêmes supervisés.
- [ ] Les configurations et la base sont sauvegardées et une restauration a été testée.
- [ ] Les fenêtres de maintenance ont une fin explicite et la reprise de la collecte est vérifiée.
- [ ] Les faux positifs, alertes dupliquées et données périmées sont revus périodiquement.
- [ ] Les incidents significatifs peuvent être reconstruits à partir de mesures, journaux, horodatages et changements.

## 16. Glossaire

| Terme | Définition |
|---|---|
| Agent | Composant installé sur une cible qui expose ou transmet des données. |
| Check actif Nagios | Contrôle planifié et lancé par Nagios à partir d'une commande. |
| Résultat passif Nagios | Résultat produit ailleurs puis soumis au moteur pour être évalué. |
| Check passif Zabbix | Le serveur ou proxy demande une donnée à l'agent. |
| Check actif Zabbix | L'agent demande sa configuration et transmet des valeurs au serveur ou proxy. |
| Plugin Nagios | Programme ou script qui renvoie un code et une sortie selon le contrat du plugin. |
| Item | Objet Zabbix qui définit une donnée collectée, reçue ou calculée. |
| Trigger | Expression Zabbix qui évalue des valeurs pour signaler un problème. |
| Template | Ensemble réutilisable d'items, triggers et autres objets liés aux hôtes. |
| LLD | Découverte de bas niveau qui détecte des entités et génère des objets à partir de prototypes. |
| MIB | Description des objets qu'un équipement expose pour la gestion SNMP. |
| OID | Identifiant d'un objet dans la hiérarchie SNMP. |
| Polling | Interrogation régulière d'une cible pour obtenir un état ou une mesure. |
| Trap SNMP | Message envoyé par un équipement lors d'un événement configuré. |
| Proxy Zabbix | Collecteur intermédiaire pour un groupe d'hôtes ou un site. |
| SOFT/HARD | États Nagios qui distinguent un résultat transitoire d'un état confirmé. |
| Prétraitement | Transformation ou validation d'une valeur avant son stockage ou usage dans Zabbix. |
| Historique | Valeurs individuelles conservées selon la rétention. |
| Tendance | Agrégat temporel de métriques numériques utile sur des périodes longues. |
| Fraîcheur | Ancienneté d'une donnée par rapport au moment attendu de collecte. |
| Faux positif | Alerte ne correspondant pas à une condition actionnable selon les critères fixés. |
| Dépendance | Relation entre un service supervisé et un composant dont il dépend. |
| Fatigue d'alerte | Réduction de l'attention liée à un trop grand nombre de notifications peu utiles. |
| RCA | Analyse d'un incident visant à expliquer ses mécanismes et vérifier des actions préventives. |

## 17. Références officielles

Les options, syntaxes et fonctions évoluent selon les versions. Consulter la documentation correspondant à la version réellement installée avant tout déploiement.

- [Nagios Core — définitions d'objets](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/objectdefinitions.html)
- [Nagios Core — contrat et codes de retour des plugins](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/pluginapi.html)
- [Nagios Core — dépendances hôtes et services](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/dependencies.html)
- [Zabbix — manuel officiel courant](https://www.zabbix.com/documentation/current/en/manual)
- [Zabbix — agents](https://www.zabbix.com/documentation/current/en/manual/concepts/agent)
- [Zabbix — notifications et actions](https://www.zabbix.com/documentation/current/en/manual/config/notifications)
- [Zabbix — types de médias](https://www.zabbix.com/documentation/current/en/manual/config/notifications/media)

La compétence essentielle est de relier un signal à ce qu'il démontre, aux limites de sa mesure et à la décision qu'il doit déclencher. Nagios apporte un modèle de checks, plugins et états ; Zabbix apporte un modèle de collecte, données, triggers et templates. Dans les deux cas, la qualité dépend de la méthode de mesure, de la sécurité, des tests, de la fraîcheur de l'information et de la capacité de l'équipe à interpréter les événements.