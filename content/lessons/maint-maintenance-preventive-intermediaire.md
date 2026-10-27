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


## 8. Construire un programme de maintenance fondé sur les risques

La périodicité d'une tâche doit avoir une justification : recommandation constructeur, exigence interne, mesure de dégradation, historique des incidents, obligation applicable ou analyse de risque. Évite la formule « on l'a toujours fait ainsi » comme unique raison. Une tâche peut être déplacée, renforcée ou allégée si les données changent, mais toute modification de la politique doit être approuvée et documentée.

Pour chaque actif, réunis la criticité du service, les modes de défaillance plausibles, les signes précurseurs observables, la probabilité estimée, l'impact, la redondance testée et le temps nécessaire à l'intervention. N'ajoute pas une précision artificielle aux évaluations : si la probabilité est inconnue, indique l'incertitude au lieu de produire un score au centième. Les catégories « critique », « élevée », « modérée » et « faible » peuvent servir de base si les définitions sont écrites et partagées.

~~~mermaid
flowchart TD
    A[Actif identifié] --> B[Service et impact métier]
    B --> C[Modes de défaillance]
    C --> D[Signes précurseurs et données]
    D --> E[Mesures et périodicité]
    E --> F[Validation du propriétaire]
    F --> G[Plan, checklist et prochaine revue]
~~~

Un actif est souvent impliqué dans plusieurs chaînes de service. La maintenance d'un DNS, d'un annuaire, d'un routeur de distribution ou d'un stockage partagé peut perturber un grand nombre d'applications. Dans ces cas, la criticité dépend du rôle et des dépendances, pas seulement du coût de remplacement de l'équipement. L'inventaire doit relier les actifs aux services qu'ils supportent et aux équipes qui pourront valider le résultat.

La priorité doit tenir compte des tâches en retard et du risque accumulé. Si un contrôle obligatoire n'a pas été effectué, indique l'écart, la raison, les mesures temporaires et la date de nouvelle décision. Une tâche marquée « reportée » n'est pas terminée. Le responsable de service doit comprendre l'effet du report et accepter explicitement le risque lorsque la politique le permet.

## 9. Planifier la charge et les ressources

Le calendrier doit être réaliste. Pour chaque tâche, estime la préparation, l'intervention, la validation, la communication, la documentation et une marge pour les imprévus. Les durées doivent être révisées avec les temps réels. Si l'équipe ne dispose pas de la compétence ou d'une pièce compatible, la tâche ne doit pas être planifiée comme si le prérequis était satisfait.

Un plan trimestriel peut combiner les fenêtres régulières, les périodes d'activité métier, les expirations de garantie ou de certificat, les avis de sécurité et les résultats de supervision. Évite de programmer simultanément les opérations sur deux composants redondants si cela peut supprimer la continuité. La séquence doit tenir compte des dépendances, du temps nécessaire aux tests et du délai pour obtenir une décision du responsable.

Une planification robuste comporte trois niveaux : un calendrier de référence, un backlog priorisé des tâches non planifiées ou en retard, et une procédure de replanification. Le calendrier ne doit pas masquer les urgences ; le backlog ne doit pas devenir un espace où les tâches critiques restent sans échéance. Chaque élément doit posséder un responsable, une priorité expliquée, une date cible et une condition de clôture.

## 10. Fenêtre et points de décision

Une fenêtre de maintenance décrit ce qui peut être modifié, où, quand, par qui et selon quelles conditions. Elle précise la durée maximale, les services touchés, les utilisateurs à informer, les contacts d'escalade, la méthode de retour et les critères d'annulation. Une fenêtre approuvée n'est pas une autorisation d'improviser des actions supplémentaires au milieu de l'intervention.

~~~mermaid
sequenceDiagram
    participant O as Opérateur
    participant R as Responsable
    participant M as Monitoring
    participant U as Utilisateur métier
    O->>R: Confirme les prérequis et le plan
    R-->>O: Autorisation et points d'arrêt
    O->>M: Place les objets prévus en maintenance
    O->>O: Exécute une étape à la fois
    M-->>O: Mesures et alertes après action
    O->>U: Demande de validation fonctionnelle
    U-->>R: Résultat et écarts
    R-->>O: Clôture ou retour autorisé
~~~

Un point d'arrêt est une décision préparée à l'avance. Exemple : si une interface redondante ne revient pas au niveau attendu dans le délai prévu, arrêter la suite et contacter le responsable. La définition du délai doit venir des caractéristiques du service et du plan approuvé. Il ne faut pas choisir une durée arbitraire pendant une panne.

Les changements simultanés doivent être évités lorsqu'ils rendent le diagnostic impossible. Si plusieurs actifs doivent être mis à jour, applique une stratégie progressive : un équipement pilote, vérification, puis vague suivante. Note les versions, les fichiers et les heures. Si le résultat est différent du scénario, ne poursuis pas simplement parce que le calendrier est serré.

## 11. Retour arrière, preuve et clôture

Une stratégie de retour arrière doit être réaliste. « Remettre comme avant » n'est pas une procédure : indique le mécanisme, le responsable, le temps estimé, les risques, les étapes et le test. Pour un routeur, cela peut inclure une configuration exportée et un accès de secours ; pour un serveur, une méthode de restauration ou une version connue ; pour une base, une protection particulière des transactions créées depuis la dernière sauvegarde. Certains changements peuvent être irréversibles, ce qui doit être compris avant l'intervention.

~~~mermaid
flowchart TD
    A[Écart détecté] --> B[Conserver les faits et les heures]
    B --> C{Impact immédiat ?}
    C -->|Oui| D[Escalade et procédure d'urgence]
    C -->|Non| E[Diagnostic encadré]
    D --> F{Retour arrière prévu et autorisé ?}
    E --> F
    F -->|Oui| G[Retour et nouveaux tests]
    F -->|Non| H[Décision du responsable]
    G --> I[Compte rendu et actions restantes]
    H --> I
~~~

Une checklist de qualité doit spécifier le test, la valeur ou le résultat attendu, la source de vérité, le statut obtenu, la date, la personne et la conduite à tenir en cas d'écart. Distingue « réussi », « échoué », « non réalisé » et « bloqué ». Si un test n'a pas été fait, ne remplace pas le statut par « réussi parce que rien n'a été signalé ». Si la validation est partielle, décris le périmètre réellement couvert.

Les captures d'écran sont utiles mais ne doivent pas remplacer les résultats structurés. Un compte rendu peut référencer le ticket, les journaux, l'export de configuration ou le résultat d'une commande, tout en supprimant les secrets et données personnelles non nécessaires. Pour un contrôle automatisé, conserve le nom et la version de l'outil, les paramètres significatifs et l'heure. La méthode doit être reproductible, mais les mots de passe et clés ne doivent jamais figurer dans le rapport.

Après l'opération, confirme que toutes les suppressions de notifications temporaires sont retirées, que les services ont repris, que les sauvegardes sont exécutées conformément à leur calendrier et que les utilisateurs ont été informés. Les problèmes résiduels doivent avoir un propriétaire et une date de suivi. Une maintenance ne doit pas être clôturée uniquement parce que la fenêtre est terminée.

## 12. Exploiter les données pour améliorer le programme

La supervision indique les tendances, les seuils récurrents, les erreurs d'interface, la capacité, la température et l'état des services. Les tickets fournissent les symptômes et les impacts. Les fiches d'intervention indiquent les actions et les résultats. La revue périodique doit relier ces sources : quels défauts reviennent, quelles tâches ne détectent rien, quelles interventions créent des risques, quels actifs sont mal inventoriés, et quelles procédures manquent ?

Des indicateurs utiles comprennent la proportion des tâches critiques réalisées à temps, le backlog en retard par criticité, les écarts de validation, les incidents apparus après maintenance, les durées réelles, les changements nécessitant un retour arrière et la complétude des documents. Ne transforme pas le taux d'exécution en objectif isolé : les équipes pourraient choisir des tâches faciles et ignorer les travaux risqués. Présente à la fois la couverture, la qualité et le risque restant.

La périodicité peut être ajustée lorsque les recommandations, l'environnement ou les mesures évoluent. Toute décision doit documenter les raisons, les données utilisées, la personne qui a accepté le risque, la date de révision et les signes qui déclencheront une réévaluation. Les tâches qui n'ont pas trouvé de défaut restent utiles seulement si elles répondent à un risque ou à une exigence ; le nombre de contrôles exécutés ne prouve pas leur valeur.

## 13. Travaux pratiques avancés

### TP 6 — Revue d'un plan existant

Prends un plan fictif où chaque équipement est maintenu le premier samedi du mois. Pour cinq actifs de fonctions différentes, réévalue la périodicité à partir de la criticité, des recommandations disponibles, des incidents et des fenêtres métier.

**Correction attendue :** le calendrier doit être justifié actif par actif. La fréquence peut différer, certains contrôles peuvent être déclenchés par une mesure, et des tâches peuvent nécessiter une approbation. Les périodicités finales restent soumises à la validation du propriétaire et au manuel applicable.

### TP 7 — Préparer un changement à risque

Rédige la checklist pour une mise à jour d'un commutateur de distribution. Précise le périmètre, la sauvegarde de configuration, la compatibilité, l'accès de secours, les services dépendants, l'ordre, les tests, le point d'arrêt, la communication et le retour arrière.

**Correction attendue :** un nom d'actif unique et une version cible sont requis ; les deux équipements d'une paire ne doivent pas être modifiés simultanément sans justification et stratégie approuvée. Les tests portent sur la connectivité et les services métier, pas uniquement sur le démarrage de l'équipement.

### TP 8 — Proposer un indicateur équilibré

La direction demande un objectif de 100 % de tâches clôturées à la date prévue. Explique les risques d'un tel objectif et propose un tableau de bord complémentaire.

**Correction attendue :** l'indicateur peut masquer les tâches reportées, la qualité des contrôles et la mauvaise priorisation. Ajouter la couverture des actifs critiques, le backlog par niveau de risque, les tâches annulées, les écarts de validation, les incidents après maintenance et les preuves manquantes. Le but reste la réduction du risque, pas le nombre de cases cochées.

## 14. Défi final — Revue de programme

À partir du plan fictif du cours, prépare une revue trimestrielle avec les actifs en retard, les pannes récurrentes, les mesures de supervision, les fenêtres manquées et les tâches qui ont dépassé leur durée. Présente les trois risques prioritaires, les décisions à obtenir, les tâches proposées et les preuves qui permettront de confirmer l'amélioration.

**Correction :** le rapport commence par l'impact métier et l'état des risques. Il présente ensuite la couverture de la maintenance, les exceptions et leur justification, les écarts détectés, les actions avec responsables et échéances, puis la date de revue suivante. Toute donnée non disponible est indiquée comme non disponible au lieu d'être inventée. Le responsable accepte explicitement les risques résiduels.
