# Planifier la maintenance préventive

> **Mise en contexte**
>
> Un serveur tombe en panne un vendredi soir. L'équipe découvre que ses sauvegardes n'ont pas été contrôlées, que le disque approche de la saturation et que les mises à jour ont été reportées plusieurs mois sans décision formelle. Plusieurs de ces risques auraient pu être détectés par un plan préventif. La maintenance préventive cherche à réduire la probabilité d'une panne, sans introduire elle-même plus de risques que nécessaire.

## Objectifs du cours

Tu apprendras à créer un plan préventif basé sur la criticité, à organiser une fenêtre de maintenance, à rédiger une checklist, à conserver des preuves et à décider quand une anomalie doit être escaladée.

## 1. Distinguer les types d'intervention

La maintenance corrective intervient après un incident. La maintenance préventive réalise des tâches planifiées pour réduire un risque connu : contrôles d'état, mises à jour validées, tests de sauvegarde, nettoyage autorisé, vérification de capacité ou inspection physique. La maintenance conditionnelle déclenche une tâche lorsque des mesures dépassent un critère ; la maintenance prédictive exploite des tendances ou modèles pour estimer le risque de défaillance.

Une tâche préventive n'est pas « redémarrer toutes les machines le premier lundi du mois ». Elle doit répondre à un objectif précis, identifier les risques, préciser les préconditions et prévoir une vérification après intervention.

## 2. Hiérarchiser par criticité

Avant d'élaborer le calendrier, classe les actifs en fonction de leur impact métier, des dépendances et du temps de reprise disponible.

| Critère | Question à poser | Conséquence sur le plan |
|---|---|---|
| Impact métier | Combien d'utilisateurs ou de processus dépendent de l'actif ? | Priorité de traitement |
| Criticité technique | La panne affecte-t-elle d'autres services ? | Vérification des dépendances |
| Exposition au risque | Existe-t-il une vulnérabilité ou une usure détectée ? | Mesure de réduction du risque |
| Récupération | Une sauvegarde restaurable et un retour arrière existent-ils ? | Préconditions avant action |
| Fenêtre disponible | À quel moment l'impact est-il acceptable ? | Planification et communication |

La fréquence doit être justifiée. Les contrôles simples peuvent être quotidiens ou hebdomadaires, les inspections détaillées mensuelles, trimestrielles ou selon les recommandations applicables. Pour le matériel, respecte les consignes du constructeur et les règles de sécurité électrique. Ne fixe pas un intervalle universel pour des équipements différents.

## 3. Cycle d'une maintenance planifiée

~~~mermaid
flowchart TD
    A[Inventaire et criticité] --> B[Définir tâche et fréquence]
    B --> C[Evaluer le risque et annoncer la fenêtre]
    C --> D[Contrôles avant intervention]
    D --> E[Exécuter la tâche autorisée]
    E --> F[Contrôles après intervention]
    F --> G{Résultat conforme ?}
    G -->|Oui| H[Clore et mettre à jour le dossier]
    G -->|Non| I[Retour arrière ou escalade]
    I --> H
~~~

Le plan doit préciser l'actif, la raison, le responsable, les étapes, le temps prévu, les dépendances, les risques, le plan de retour arrière et les critères de réussite. Une tâche non exécutée doit être replanifiée avec une justification ; elle ne doit pas disparaître du registre.

## 4. Préparer une fenêtre de maintenance

Avant une tâche qui peut affecter un service :

1. Vérifie l'actif et son propriétaire dans l'inventaire.
2. Lis la procédure validée et les changements récents.
3. Vérifie les sauvegardes ou mécanismes de restauration requis.
4. Confirme les accès, dépendances et personnes de contact.
5. Définis l'impact prévu et informe les utilisateurs concernés.
6. Note les mesures avant intervention : état de santé, disponibilité, capacité et versions.
7. Définis un critère d'arrêt et un retour arrière réalisable.
8. Obtiens l'approbation prévue par le processus de changement.

Les mises à jour de sécurité peuvent être urgentes, mais elles ne doivent pas être improvisées : évalue le risque, vérifie l'origine des paquets, prépare la reprise et adapte le niveau d'approbation à l'urgence. Ne désactive pas les protections pour faire passer une tâche plus vite.

## 5. Exemples de contrôles techniques

Sur une machine Linux, les commandes suivantes aident à relever l'état avant et après intervention :

~~~bash
date -Is
hostnamectl
uptime
df -h
free -h
systemctl --failed
systemctl list-timers --all
journalctl -p warning --since "24 hours ago"
~~~

Pour les interfaces et les disques, selon le matériel et les outils installés :

~~~bash
ip -s link
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
~~~

Sur une distribution Debian ou Ubuntu, une simulation de mise à jour permet de voir les changements proposés sans appliquer la mise à niveau :

~~~bash
sudo apt-get -s upgrade
~~~

La simulation doit être relue : elle ne valide ni la compatibilité applicative, ni le changement en production. Les résultats sont propres à la distribution, à ses dépôts et à la configuration. Toute opération d'écriture doit suivre la procédure approuvée.

## 6. Créer une checklist exploitable

Une checklist doit faire apparaître une action vérifiable, pas une instruction vague.

| Étape | Contrôle mesurable | Preuve attendue | En cas d'échec |
|---|---|---|---|
| Avant | Sauvegarde récente et résultat de contrôle disponibles | Référence du point de restauration | Reporter ou escalader |
| Avant | Fenêtre et contacts confirmés | Ticket ou validation | Ne pas démarrer |
| Pendant | Étape exécutée dans l'ordre approuvé | Journal d'intervention | Arrêter si le risque dépasse le seuil |
| Après | Service disponible et test fonctionnel réussi | Résultat horodaté | Retour arrière ou escalade |
| Clôture | Inventaire et historique mis à jour | Rapport final | Garder la tâche ouverte |

Évite les cases précochées et les mentions « OK » sans mesure ou référence. Si une étape ne s'applique pas, justifie le choix. Une checklist courte et spécifique à un service est généralement plus utile qu'une énorme liste identique pour tous les équipements.

## 7. Mesurer l'efficacité du plan

Un plan se pilote par des indicateurs : taux de tâches réalisées à la date prévue, nombre d'incidents liés à un contrôle manquant, taux de retour arrière, tâches reportées, durée réelle comparée à la durée prévue et anomalies répétitives. Un taux d'exécution de 100 % ne garantit pas l'efficacité si les tâches ne réduisent pas les pannes ou ne sont pas adaptées à la criticité.

Revois la fréquence lorsque les données le justifient, à la suite d'un incident, d'un changement majeur, d'une recommandation constructeur ou d'une dérive mesurée. Toute modification importante doit être documentée pour que l'équipe comprenne pourquoi la tâche a changé.

## Mise en pratique

### Laboratoire : construire un plan sur trois actifs fictifs

Prépare un plan pour un serveur de fichiers critique, un poste de travail standard et un commutateur d'accès utilisé par plusieurs équipes. Pour chaque actif, indique la criticité, les dépendances, la tâche préventive, la fréquence justifiée, le responsable, la fenêtre, les contrôles avant/après, les preuves et la réaction en cas d'échec. Utilise les commandes de diagnostic sur une machine de laboratoire, jamais sur un appareil sur lequel tu n'es pas autorisé à intervenir.

Ensuite, simule une tâche reportée parce que la sauvegarde n'est pas vérifiée. Le registre doit conserver le statut « bloquée » ou « reportée », la raison, le responsable et la prochaine date de décision. Ne transforme pas une précondition manquante en validation implicite.

## Exercices corrigés

**1. Pourquoi classer les actifs avant d'établir les fréquences ?**

Correction : parce que l'impact, les dépendances, le risque et le délai de reprise ne sont pas identiques. La fréquence doit suivre le risque et les recommandations applicables, pas une règle unique.

**2. La checklist indique « sauvegarde OK » sans date ni preuve. Est-ce suffisant ?**

Correction : non. Il faut identifier le point de sauvegarde, son résultat de contrôle et, lorsque le risque l'exige, la preuve d'un test de restauration.

**3. Une mise à jour a été installée, mais le test fonctionnel échoue. Quelle est la suite ?**

Correction : arrêter la clôture, suivre les critères d'arrêt et de retour arrière approuvés, informer les responsables, restaurer le service selon la procédure, puis consigner les résultats.

**4. Toutes les tâches sont réalisées à temps, mais le nombre d'incidents ne baisse pas. Que revoir ?**

Correction : la pertinence et la fréquence des tâches, la criticité, les preuves produites et la relation entre la maintenance et les incidents. Il faut mesurer l'efficacité, pas uniquement l'exécution.

## Défi final corrigé

Une maintenance préventive sur un commutateur d'accès est programmée. Le contrôle avant intervention révèle qu'un lien redondant est lui-même instable et que la sauvegarde de configuration est ancienne. Prépare la décision.

**Correction attendue :** ne pas exécuter immédiatement la tâche. Confirmer les faits et les dépendances, informer le responsable, remettre en état ou valider le lien redondant selon une procédure distincte, réaliser et vérifier une sauvegarde récente, confirmer le plan de retour arrière, puis demander une nouvelle fenêtre approuvée. Le report doit être inscrit dans le registre avec une raison et une date de réévaluation. La décision est traçable et vise à éviter qu'une intervention préventive provoque une panne.
