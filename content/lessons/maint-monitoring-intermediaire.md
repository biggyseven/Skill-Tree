# Supervision réseau (Nagios, Zabbix)

> **Mise en contexte**
>
> Tu assures l'exploitation d'un petit réseau d'entreprise. Les utilisateurs signalent des lenteurs, mais personne ne sait si le problème vient du lien Internet, d'un serveur saturé ou d'un service arrêté. Une supervision bien conçue transforme ces impressions en signaux vérifiables : elle mesure l'état des services, conserve un historique et prévient l'équipe avant qu'une dégradation ne devienne une panne majeure.

## Objectifs du cours

À la fin de ce cours, tu sauras définir ce qu'il faut surveiller, distinguer disponibilité et performance, organiser des contrôles Nagios ou Zabbix, régler des seuils utiles et traiter une alerte jusqu'à sa clôture. Tu dois aussi pouvoir expliquer pourquoi un tableau de bord « tout vert » ne garantit pas que les utilisateurs travaillent normalement.

## 1. Ce que la supervision mesure réellement

La supervision repose sur trois questions complémentaires :

- **Disponibilité :** le service répond-il au moment du contrôle ?
- **Performance :** répond-il assez vite et avec une qualité acceptable ?
- **Capacité et tendance :** les ressources risquent-elles d'être saturées prochainement ?

Un contrôle isolé ne permet pas d'établir une tendance. Il faut conserver des mesures horodatées, leur contexte et l'état du service pendant une période suffisante. Les indicateurs courants comprennent la latence, la perte de paquets, le débit, les erreurs d'interface, l'utilisation CPU, la mémoire disponible, l'espace disque, les certificats qui approchent de leur expiration et la disponibilité d'un service métier.

Une métrique doit avoir un sens opérationnel. L'utilisation CPU à 90 % peut être normale pendant une opération de calcul ; un disque qui atteint 90 % peut annoncer une panne imminente si sa croissance est rapide. Le seuil doit donc être interprété avec la durée, le rôle de la machine et les conséquences sur le service.

## 2. Architecture d'une supervision

~~~mermaid
flowchart TD
    A[Equipements et services] --> B[Agents, SNMP ou sondes]
    B --> C[Serveur de supervision]
    C --> D[Historique des mesures]
    C --> E[Evaluation des seuils]
    E --> F[Tableau de bord et notification]
    F --> G[Diagnostic puis intervention]
~~~

Les composants ont des rôles distincts :

- **Équipement surveillé :** routeur, commutateur, serveur, application, lien ou service.
- **Sonde ou agent :** fournit des mesures, exécute un contrôle ou expose des compteurs. SNMP sert notamment à interroger des équipements réseau ; un agent fournit des informations locales plus détaillées.
- **Serveur de supervision :** planifie les contrôles, collecte les résultats et détermine l'état courant.
- **Historique :** permet de comparer les périodes, reconnaître une tendance et préparer un rapport.
- **Notification :** transmet une alerte utile à une personne capable d'agir.

Le protocole doit être choisi selon le besoin. ICMP permet de tester une réponse IP, mais ne prouve pas qu'une application fonctionne. SNMP peut exposer l'état d'une interface et ses compteurs, mais ne remplace pas un test métier. Un contrôle HTTP peut confirmer qu'une page répond, sans garantir que l'utilisateur peut se connecter ou effectuer une transaction.

## 3. Contrôles actifs et passifs

Un **contrôle actif** est déclenché par la plateforme : ping, requête HTTP, test d'un port ou interrogation d'un agent. Il est utile pour vérifier régulièrement un résultat défini.

Un **contrôle passif** reçoit un événement ou un résultat envoyé par un équipement ou un autre système. Il est utile pour les journaux, les traps SNMP et certaines alertes d'application.

Les contrôles doivent couvrir des couches différentes. Pour un serveur web, une vérification raisonnable peut inclure la présence réseau, le port TCP, la réponse HTTP, le certificat TLS puis un test fonctionnel disponible. Si le ping réussit mais que le port applicatif est fermé, l'état réseau est sain tandis que le service est défaillant.

## 4. Nagios et Zabbix : principes d'utilisation

**Nagios** est organisé autour d'hôtes, de services, de contrôles et de plugins. Les plugins exécutent des vérifications et renvoient un état ainsi qu'un code de sortie : généralement OK, WARNING, CRITICAL ou UNKNOWN. Les seuils doivent être définis selon le contrat de service. Un plugin inconnu ou mal configuré ne doit pas être interprété comme un service sain.

**Zabbix** utilise des hôtes, des items qui collectent les valeurs, des triggers qui évaluent des expressions, des actions et des modèles. Un template permet de réutiliser la configuration. Les agents actifs initient leurs échanges depuis l'hôte surveillé ; les contrôles passifs sont sollicités par le serveur ou le proxy, selon la configuration. Il faut autoriser uniquement les flux réseau nécessaires et protéger les identifiants d'administration.

Ces outils ne dispensent pas de concevoir correctement la supervision. Avant de créer une règle, documente le service, sa criticité, l'indicateur choisi, le seuil, la fréquence de contrôle, la personne destinataire et l'action attendue.

## 5. Construire des seuils utiles

Un seuil trop permissif détecte la panne trop tard. Un seuil trop strict crée du bruit et encourage les équipes à ignorer les alertes.

1. Mesure le comportement normal à plusieurs moments de la journée.
2. Définis un seuil d'avertissement et un seuil critique selon l'impact.
3. Ajoute, lorsque c'est pertinent, une durée ou plusieurs échantillons avant déclenchement.
4. Distingue les symptômes dépendants : la panne d'un routeur ne doit pas générer vingt alertes indépendantes pour tous les serveurs derrière lui.
5. Vérifie les horaires de maintenance et les règles d'acquittement.
6. Revois les seuils après les incidents et les changements d'architecture.

Les états doivent avoir un sens commun à toute l'équipe. WARNING demande une vérification ou une action planifiée ; CRITICAL indique un risque ou un impact qui exige une réponse rapide ; UNKNOWN signifie que la supervision ne peut pas conclure. UNKNOWN n'est pas équivalent à OK.

## 6. Lire les signaux sans conclure trop vite

Quelques commandes en lecture seule aident à confirmer une alerte sur un hôte Linux :

~~~bash
ping -c 4 192.0.2.10
ip -s link
ss -lnt
df -h
free -h
systemctl --failed
journalctl -p warning --since "1 hour ago"
~~~

Remplace l'adresse d'exemple par une cible autorisée. Une perte de ping peut être due au filtrage ICMP ; vérifie également le service attendu. La commande ss affiche les sockets TCP en écoute, pas la santé complète de l'application. df montre l'espace des systèmes de fichiers, tandis que journalctl aide à repérer des messages récents. Les permissions et la disponibilité des journaux dépendent du système.

Pour tester un agent Zabbix installé et autorisé, cette commande interroge une clé courante sur l'hôte local :

~~~bash
zabbix_get -s 127.0.0.1 -k system.uptime
~~~

Elle nécessite le client zabbix_get, un agent compatible et une configuration autorisant cette requête. N'ouvre pas le port de l'agent à tout Internet : utilise une liste d'adresses autorisées et, quand c'est possible, les mécanismes d'authentification et de chiffrement pris en charge.

## 7. Traiter une alerte de bout en bout

Une alerte utile contient au minimum l'hôte, le service, l'heure, le résultat observé, le seuil, la durée, la criticité et un lien vers la procédure de diagnostic. À réception :

1. Acquitte l'alerte si le processus le prévoit ; cela signale qu'elle est prise en charge, pas qu'elle est résolue.
2. Confirme l'impact réel à l'aide d'une seconde mesure ou d'un test fonctionnel.
3. Consulte les événements récents et les changements survenus avant la panne.
4. Applique la procédure autorisée et conserve les preuves utiles.
5. Vérifie le retour du service depuis le point de vue pertinent.
6. Documente la cause, la correction et les améliorations de supervision nécessaires.

Une alerte qui revient souvent doit être analysée. Ne la désactive pas simplement pour faire disparaître le bruit : corrige le seuil, la dépendance, la sonde ou le problème sous-jacent.

## Mise en pratique

### Scénario de laboratoire

Tu disposes d'un serveur de test et d'une machine de supervision. Le serveur est joignable en ICMP, mais le site interne ne répond plus.

1. Note l'heure et l'identifiant de l'alerte.
2. Vérifie l'accès réseau vers le serveur.
3. Vérifie le port et le service visés ; ne te contente pas d'un ping positif.
4. Compare l'état du service avec ses journaux récents.
5. Vérifie si un déploiement, une modification de pare-feu ou une saturation précède la panne.
6. Après correction autorisée, valide à nouveau le service, observe au moins un cycle de contrôle et clôture l'alerte avec une cause documentée.

**Résultat attendu :** un compte rendu court qui sépare les faits, les hypothèses, le test de confirmation, l'action et la preuve de rétablissement. Le laboratoire doit être réalisé sur une cible de test ou une infrastructure pour laquelle tu as une autorisation.

### Fiche de seuils à remplir

| Signal | Valeur observée | Seuil Warning | Seuil Critical | Action associée |
|---|---:|---:|---:|---|
| Latence | À mesurer | À justifier | À justifier | Vérifier le chemin et la charge |
| Espace libre | À mesurer | À justifier | À justifier | Identifier la croissance avant nettoyage |
| Service applicatif | Réponse attendue | Dégradation définie | Indisponibilité | Tester le service et suivre la procédure |

Les valeurs ne doivent pas être copiées aveuglément depuis un autre environnement : justifie-les à partir d'une référence, d'un objectif de service et d'un historique.

## Exercices corrigés

**1. Le ping d'un serveur web réussit, mais les utilisateurs ne peuvent pas ouvrir le site. Que conclus-tu ?**

Correction : seule la connectivité ICMP est confirmée. Il faut tester le port, HTTP/TLS, les journaux et le parcours fonctionnel pertinent.

**2. Pourquoi conserver l'historique des métriques ?**

Correction : pour reconnaître une dérive, comparer la situation avant et après un changement, expliquer un incident et dimensionner les ressources à partir de tendances mesurées.

**3. Une dépendance réseau en panne déclenche des alertes sur dix serveurs. Que faut-il améliorer ?**

Correction : documenter la dépendance, construire une relation de dépendance ou une corrélation adaptée et garder une alerte principale claire sans masquer les symptômes utiles.

**4. Que signifie l'état UNKNOWN ?**

Correction : le système de supervision ne dispose pas d'un résultat suffisamment fiable. Il faut vérifier la sonde, les droits, le réseau et la configuration, sans le classer automatiquement comme OK.

## Défi final corrigé

Un outil signale une forte utilisation du disque sur un serveur de fichiers. Les utilisateurs se plaignent de lenteurs, mais aucune panne complète n'est confirmée. Prépare le traitement.

**Correction attendue :** acquitter l'alerte selon la procédure, confirmer l'espace libre avec df -h, vérifier l'évolution dans l'historique, déterminer les répertoires ou journaux responsables sans supprimer de données au hasard, examiner les événements récents, évaluer l'impact et informer le responsable. Si un nettoyage est autorisé, définir une sauvegarde ou une rétention vérifiée, faire valider l'action, l'exécuter dans la fenêtre prévue puis vérifier l'espace et le service. Enfin, documenter le résultat et ajuster la supervision si le seuil ou la tendance était mal interprété.
