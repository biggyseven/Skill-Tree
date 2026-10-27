# Automatiser les tâches (scripts, Ansible)

> **Mise en contexte**
>
> Une équipe doit vérifier quotidiennement l'espace disque, contrôler les services, sauvegarder les configurations réseau, préparer des rapports et appliquer des changements répétitifs à plusieurs serveurs. Chaque technicien exécute les mêmes commandes manuellement, avec des variations et des oublis. Un script improvisé lancé en production supprime un répertoire trop large ; un playbook rejoué plusieurs fois redémarre inutilement des services. L'automatisation réduit certaines erreurs et accélère les tâches, mais elle peut aussi multiplier rapidement une erreur sur des dizaines de machines.
>
> Une automatisation fiable n'est pas une commande placée dans un planificateur. Elle possède un objectif, un périmètre, des entrées validées, des droits limités, un comportement répétable, des journaux, une gestion d'erreur, un contrôle avant exécution et une procédure d'arrêt ou de retour. Le technicien doit pouvoir expliquer ce que le programme fera, sur quelles cibles, quelles modifications sont attendues et comment vérifier son résultat.
>
> Ce cours présente les scripts de maintenance, les bases de l'ordonnancement, la gestion de configuration avec Ansible et les contrôles nécessaires avant une exécution. Les exemples sont destinés à un laboratoire ou à des environnements autorisés. Les commandes qui modifient des systèmes doivent être testées et approuvées avant de viser la production.

## 1. Objectifs pédagogiques

À la fin du cours, tu dois pouvoir identifier les tâches adaptées à l'automatisation, concevoir un script sûr et observable, choisir une méthode d'ordonnancement, écrire un playbook Ansible lisible, comprendre l'idempotence, contrôler la portée d'un déploiement, utiliser le mode vérification lorsqu'il est pris en charge, protéger les secrets et documenter les résultats.

Tu dois notamment savoir :

- décomposer une tâche manuelle en entrées, étapes, résultats et exceptions ;
- choisir entre un script simple, un outil spécialisé ou un playbook Ansible ;
- vérifier et normaliser les paramètres ;
- utiliser des codes de retour et gérer les échecs ;
- écrire des journaux utiles sans divulguer de secrets ;
- éviter les exécutions concurrentes et les répétitions dangereuses ;
- concevoir des tâches idempotentes lorsque c'est approprié ;
- structurer inventaires, groupes, variables, playbooks, rôles et handlers ;
- tester en mode vérification et sur un petit groupe avant un déploiement large ;
- respecter le processus de changement, la traçabilité et le principe du moindre privilège.

## 2. Décider si une tâche doit être automatisée

Une bonne candidate est répétitive, possède des entrées prévisibles, une procédure stable, des critères de réussite vérifiables et un risque maîtrisable. Exemples : contrôler la présence d'un fichier, collecter une version, générer un rapport à partir d'une source autorisée, vérifier un certificat, déployer un fichier de configuration approuvé ou contrôler un service après maintenance.

Une tâche n'est pas prête à être automatisée si les étapes sont mal comprises, si les exceptions ne sont pas connues, si le résultat dépend d'un jugement humain non formalisé ou si personne ne sait comment revenir à l'état précédent. Commence par standardiser le processus. Automatiser un processus mal défini accélère souvent les erreurs au lieu de les supprimer.

Évalue l'automatisation selon sa fréquence, le temps consommé, la variabilité, le taux d'erreur, l'impact de l'action, l'étendue des cibles, les droits nécessaires, l'observabilité, les coûts de maintenance et la capacité de test. Le gain de temps ne doit pas être le seul critère : un script de suppression qui économise quelques minutes peut créer un incident majeur s'il n'a pas de garde-fous.

~~~mermaid
flowchart TD
    A[Tâche manuelle] --> B[Étapes et exceptions documentées ?]
    B -->|Non| C[Standardiser et tester le processus]
    C --> B
    B -->|Oui| D[Évaluer risque et répétition]
    D --> E{Automatisation adaptée ?}
    E -->|Non| F[Procédure manuelle contrôlée]
    E -->|Oui| G[Prototype et tests en laboratoire]
    G --> H[Validation et déploiement progressif]
~~~

Pour les interventions à fort impact, l'automatisation peut préparer les données et réduire les oublis, mais conserver une validation humaine au point de décision. Par exemple, un script peut lister les serveurs qui approchent d'un seuil ; l'extension du stockage ou la suppression de données exige une décision et une procédure approuvée.

## 3. Les qualités d'un script de maintenance

Un script robuste possède un nom explicite, un but, un propriétaire, des paramètres documentés, une validation d'entrée, un comportement défini en cas d'erreur, des journaux, une limite de durée, une gestion des répétitions et un résultat de sortie. Il ne doit pas considérer qu'une commande a réussi simplement parce qu'elle s'est terminée : il faut vérifier l'effet attendu.

### 3.1 Valider les entrées et réduire le périmètre

Valide les chemins, noms d'hôtes, options, périodes et listes de cibles avant l'action. Si le script reçoit une liste de serveurs, vérifie que les noms appartiennent au groupe autorisé. Évite de concaténer un texte fourni par l'utilisateur dans une commande shell. Préfère les arguments séparés et les bibliothèques conçues pour le protocole ciblé. Refuse explicitement les valeurs vides ou les paramètres qui pourraient élargir la portée.

Une liste de cibles doit venir d'une source approuvée. Le script doit afficher ou enregistrer les cibles prévues avant de modifier le système. Un paramètre de type « tous » doit être clairement encadré et ne doit pas devenir la valeur par défaut si cela est risqué. Pour les tâches destructives, prévois une confirmation ou une étape d'approbation séparée, ainsi qu'un mode de simulation utile.

### 3.2 Retourner un statut exploitable

Utilise des codes de sortie distincts lorsque c'est pertinent : réussite, entrée invalide, prérequis absent, délai dépassé, cible indisponible ou erreur inattendue. Si le script appelle d'autres commandes, vérifie leurs codes de retour et leur sortie. Ne supprime pas les erreurs silencieusement et n'utilise pas un code zéro si une étape essentielle a échoué.

Un planificateur ou une plateforme de supervision utilise souvent le code de retour pour qualifier le job. Un script peut imprimer « échec » puis terminer avec zéro ; le tableau de bord présente alors une réussite trompeuse. Teste le code final des chemins de succès et d'échec, y compris les erreurs de lecture, les timeouts et les entrées inconnues.

### 3.3 Journaux, timeout et répétition

Un journal peut inclure l'heure, le nom de la tâche, l'identifiant d'exécution, la cible, la durée, le résultat, le nombre d'objets traités et le message d'erreur. Évite les mots de passe, clés, jetons d'API et données personnelles inutiles. Les logs doivent être protégés contre la modification, leur rétention définie et leur taille contrôlée.

Définis un délai maximum par cible et par tâche. Une connexion qui ne répond pas ne doit pas bloquer indéfiniment tout le lot. Les tentatives répétées peuvent aider face à une erreur transitoire, mais elles doivent être limitées, espacées et réservées aux opérations que l'on peut répéter sans dommage. Ne répète pas aveuglément une opération financière, une suppression, une migration de schéma ou une action non idempotente.

### 3.4 Comprendre l'idempotence

L'idempotence signifie qu'appliquer plusieurs fois la même déclaration conduit au même état final qu'une seule application. « Assurer que ce paquet est installé à la version approuvée » est généralement plus robuste que « lancer l'installateur à chaque exécution ». L'idempotence ne signifie pas que toute action est sans effet : redémarrer un service ou envoyer un courriel plusieurs fois peut produire des effets répétés. La conception doit distinguer état souhaité et action ponctuelle.

~~~mermaid
flowchart TD
    A[Démarrage] --> B[Valider les paramètres]
    B --> C[Contrôler prérequis et portée]
    C --> D[Exécuter avec timeout]
    D --> E[Vérifier code et résultat]
    E --> F{Succès confirmé ?}
    F -->|Oui| G[Journaliser la preuve]
    F -->|Non| H[Journaliser erreur et arrêter ou escalader]
    G --> I[Résumé final et code de sortie]
    H --> I
~~~

## 4. Exemple de script Python prudent pour un contrôle en lecture seule

Le script ci-dessous illustre une collecte locale de capacité disque. Il ne supprime rien et ne modifie pas le système. Dans un environnement réel, adapte le chemin, l'identité d'exécution, le format de sortie et la politique de journalisation. Il vérifie les entrées, utilise une fonction adaptée du système et renvoie un statut non nul en cas d'erreur.

~~~python
from pathlib import Path
import json
import logging
import shutil
import sys
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def main() -> int:
    target = Path("/")
    if not target.exists():
        logging.error("Le chemin de contrôle n'existe pas")
        return 2

    try:
        usage = shutil.disk_usage(target)
        result = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "path": str(target),
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
            "free_percent": round((usage.free / usage.total) * 100, 2)
                if usage.total else None,
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except OSError:
        logging.exception("Échec du contrôle de capacité")
        return 1

if __name__ == "__main__":
    sys.exit(main())
~~~

Ce script n'est qu'un exemple. Pour un audit de plusieurs systèmes, ne copie pas le script et ne l'exécute pas sous un compte d'administration global sans besoin. Prévois une identité en lecture seule, un mécanisme de connexion approuvé et des contrôles de délai. Ajoute si nécessaire un seuil d'avertissement, mais garde la règle métier séparée du simple calcul de la valeur. Un résultat de 8,5 % d'espace libre peut déclencher une analyse selon le service, pas nécessairement une suppression.

Le script doit être testé sur des situations connues : espace normal, espace bas, chemin inexistant et erreur de permission. Une collecte en lecture seule est une première étape utile parce qu'elle limite le risque, mais elle doit quand même être supervisée et avoir un code de retour correct.

## 5. Planifier les tâches sans créer de concurrence ni de silence

Cron, un ordonnanceur système, un pipeline CI ou un service de planification peuvent lancer des tâches à intervalles. Le choix dépend du système, des droits, de la gestion des dépendances, des journaux, des notifications et de la reprise après redémarrage. Le fichier de planification ne doit pas être le seul document qui explique le but de la tâche.

Une tâche planifiée doit préciser l'utilisateur d'exécution, l'environnement, le chemin des programmes et fichiers, les journaux, le verrouillage, les codes d'erreur, les délais, les tentatives, les notifications, les secrets, le test après modification du calendrier et le propriétaire qui reçoit les rapports d'échec.

Une tâche exécutée toutes les cinq minutes peut rester en cours plus longtemps que prévu et démarrer une seconde fois. Cela risque de consommer deux fois les ressources ou d'écraser un fichier. Utilise un mécanisme de verrouillage adapté au système, vérifie les exécutions pendantes et décide quoi faire si une précédente exécution est toujours active. Évite de masquer les erreurs par une redirection générale vers un puits silencieux.

Une vérification doit détecter la tâche qui ne s'exécute plus. Superviser uniquement ses erreurs ne suffit pas si le programme est silencieux ou ne démarre jamais. Le reporting peut comparer l'heure du dernier résultat valide à la périodicité attendue, puis générer une alerte si la preuve est trop ancienne. Distingue « aucune anomalie mesurée » de « aucune mesure reçue ».

## 6. Pourquoi utiliser Ansible ?

Ansible automatise la configuration et les tâches sur un ensemble de systèmes à partir d'inventaires et de playbooks. Un playbook décrit un état ou une suite d'opérations, généralement structurée en plays et tâches. Les modules gèrent des objets comme les paquets, fichiers, services et utilisateurs. Les variables adaptent le résultat aux groupes ou environnements ; les templates produisent des fichiers de configuration ; les handlers peuvent exécuter une action après un changement pertinent.

Ansible utilise généralement SSH pour de nombreux systèmes Linux, mais les méthodes et prérequis varient selon la cible. Un inventaire identifie les hôtes et groupes. Un playbook peut cibler un groupe précis, appliquer des variables, appeler des modules et vérifier le résultat. Le but est de remplacer des étapes manuelles répétées par une définition versionnée, relisible et testable.

Documentation officielle :
- Playbooks : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html
- Modes check et diff : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html
- Ansible Vault : https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html

~~~mermaid
flowchart LR
    A[Inventaire et variables] --> B[Playbook]
    B --> C[Modules et rôles]
    C --> D[Cibles autorisées]
    D --> E[État déclaré]
    E --> F[Résultat et journaux]
    F --> G[Validation et rapport]
~~~

## 7. Inventaire, groupes et limites de ciblage

L'inventaire peut être statique ou dynamique. Les groupes permettent de regrouper les systèmes par fonction, site, environnement ou responsabilité. Un nom tel que « production » ne suffit pas à garantir que la cible est correcte : examine l'inventaire résolu, les groupes imbriqués, les variables et les exclusions avant d'exécuter. Un changement de nom ou d'appartenance peut élargir l'ensemble des hôtes ciblés.

Exemple fictif d'inventaire INI :

~~~ini
[lab_web]
web-lab-01 ansible_host=192.0.2.31
web-lab-02 ansible_host=192.0.2.32

[lab_web:vars]
ansible_user=automation
~~~

Les adresses de la plage 192.0.2.0/24 sont réservées à la documentation ; remplace-les dans un laboratoire autorisé. N'inscris pas de mot de passe dans l'inventaire. Utilise les mécanismes de clés et de secrets approuvés. Les variables d'inventaire peuvent provenir de plusieurs emplacements ; en cas de conflit, vérifie la priorité d'Ansible plutôt que de supposer quelle valeur est appliquée.

Avant une exécution, affiche les cibles ou utilise une limite explicite au groupe de test. Commence par un hôte canari puis une petite vague, avant d'élargir. Une commande appliquée à 200 serveurs à la fois peut transformer une erreur de syntaxe en incident majeur. L'étendue doit être un choix réfléchi, et la sortie d'Ansible doit être conservée selon les règles de l'organisation.

## 8. Lire et écrire un playbook simple

Un playbook YAML doit être indenté proprement et nommer ses tâches clairement. Utilise les modules spécialisés plutôt que des commandes shell lorsqu'un module idempotent couvre le besoin. Les noms de tâches servent de documentation et facilitent l'interprétation de la sortie. Déclare explicitement les systèmes et les privilèges nécessaires.

~~~yaml
---
- name: Vérifier un service dans le laboratoire
  hosts: lab_web
  gather_facts: false
  tasks:
    - name: Collecter les faits de service
      ansible.builtin.service_facts:

    - name: Afficher que le contrôle a été effectué
      ansible.builtin.debug:
        msg: "Contrôle des faits du service terminé"
~~~

Ce playbook illustre la structure, pas un contrôle complet de disponibilité HTTP. Les faits de service peuvent dépendre de la plateforme et des privilèges ; la tâche de debug ne vérifie pas que les utilisateurs peuvent accéder à l'application. Il faut ajouter un test d'application distinct, avec un point de contrôle autorisé, un code de réponse ou un résultat attendu, et traiter les échecs.

Exemple d'état souhaité : maintenir un paquet installé. Le module ansible.builtin.package peut déclarer le paquet et son état, tandis que ansible.builtin.service peut déclarer si un service doit être activé ou démarré. Le nom du paquet et du service varient selon les distributions et versions. Vérifie les noms pris en charge et teste sur l'environnement cible.

~~~yaml
---
- name: Déclarer un paquet dans le laboratoire
  hosts: lab_web
  become: true
  tasks:
    - name: S'assurer que le paquet exemple est présent
      ansible.builtin.package:
        name: paquet-exemple
        state: present
~~~

Le nom « paquet-exemple » est un substitut documentaire : ce playbook ne doit pas être lancé tel quel sur des hôtes réels. Remplace le paquet par un nom vérifié, valide l'environnement, utilise une cible laboratoire et vérifie le diff. Le choix de devenir un utilisateur privilégié implique une élévation de droits ; ne l'ajoute pas si la tâche ne la nécessite pas et si l'autorisation ne l'accorde pas.

## 9. Idempotence, handlers, rôles et réutilisation

L'idempotence est un avantage important des modules Ansible, mais elle dépend du module et de la tâche. Une commande shell qui redémarre un processus à chaque fois n'est pas idempotente. Un module déclarant qu'un fichier doit contenir une ligne donnée peut ne modifier le fichier que lorsque cette ligne manque. Avant de répéter un playbook, vérifie son comportement et les effets secondaires.

Un handler permet d'effectuer une action, souvent un redémarrage ou un rechargement, seulement si une tâche qui le notifie a produit un changement. Ce mécanisme limite les redémarrages inutiles. Mais un redémarrage reste un effet opérationnel qui peut interrompre un service ; il doit être soumis à une validation si l'environnement l'exige.

~~~mermaid
flowchart TD
    A[Tâche de configuration] --> B{Fichier réellement modifié ?}
    B -->|Non| C[Aucun redémarrage requis]
    B -->|Oui| D[Notifier le handler]
    D --> E[Recharger selon procédure]
    E --> F[Test de service et preuve]
~~~

Un rôle organise des tâches, variables, fichiers et templates afin de réutiliser la même logique. Un rôle bien conçu expose les paramètres qui doivent varier et garde par défaut des valeurs prudentes. Évite de rendre un rôle aussi général qu'il devient impossible de savoir quels systèmes il peut modifier. Les dépendances doivent être versionnées et vérifiées.

Un dépôt d'automatisation devrait contenir la structure, les rôles, les templates, les tests et la documentation, mais pas les secrets en clair. Les changements de playbook doivent être relus comme du code : portée, privilèges, effets secondaires, gestion de l'erreur, retour arrière et sortie attendue. Le versionnement permet de retrouver le changement appliqué et de comparer les versions.

## 10. Tester avant de modifier les systèmes

Ansible propose un mode vérification avec l'option --check et un mode différence avec --diff. Le check mode simule les tâches qui le prennent en charge et ne modifie normalement pas les systèmes ; certaines tâches, modules ou conditions ne peuvent pas produire un résultat complet dans ce mode. Le diff montre avant/après pour les tâches compatibles, mais peut révéler des secrets dans les fichiers de configuration. La documentation officielle présente les limites : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html.

Séquence prudente :
1. vérifier la syntaxe ;
2. examiner les cibles exactes et les variables ;
3. lancer les contrôles de qualité du dépôt ;
4. exécuter sur un groupe de laboratoire ;
5. utiliser check mode et diff lorsque cela est pris en charge ;
6. relire les changements prévus et toute donnée sensible exposée ;
7. lancer sur une cible pilote avec autorisation ;
8. vérifier le résultat et les effets secondaires ;
9. augmenter progressivement la portée ;
10. documenter la version et les preuves.

~~~mermaid
flowchart TD
    A[Modifier le playbook] --> B[Contrôle syntaxe et revue]
    B --> C[Inventaire limité au laboratoire]
    C --> D[Test fonctionnel]
    D --> E[Check et diff si compatibles]
    E --> F{Diff compris et validé ?}
    F -->|Non| G[Corriger le playbook]
    G --> B
    F -->|Oui| H[Approbation et pilote]
    H --> I[Vérification post-exécution]
    I --> J[Déploiement progressif et compte rendu]
~~~

Le mode check n'est pas une preuve absolue que l'exécution réelle sera sans risque. Les modules qui ne prennent pas le mode en charge, les conditions dépendant de résultats précédents et les différences entre environnement de test et production peuvent modifier le résultat. Il faut examiner la documentation du module et tester les comportements critiques dans une zone contrôlée.

Le diff peut afficher des valeurs sensibles avant/après. Désactive l'affichage du diff pour les tâches contenant des secrets lorsque nécessaire, utilise no_log pour éviter les fuites dans la sortie quand c'est approprié, et vérifie les journaux du pipeline. Même si un fichier est chiffré dans le dépôt, les secrets sont déchiffrés pendant l'exécution et peuvent être exposés par un debug mal conçu.

## 11. Protéger les secrets avec Ansible Vault

Les playbooks peuvent nécessiter des mots de passe techniques, clés API ou paramètres privés. N'écris pas ces valeurs en clair dans un inventaire, un template, un ticket ou un dépôt. Ansible Vault permet de chiffrer des variables ou fichiers ; les éléments restent chiffrés au repos, puis sont déchiffrés pendant l'exécution. Il faut donc encore protéger la sortie, l'environnement d'exécution, les permissions et les mécanismes d'accès. Documentation : https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html.

Un fichier Vault ne se protège pas lui-même contre un accès trop large au mot de passe de Vault. La séparation des droits doit distinguer qui peut modifier le playbook, qui peut récupérer le secret et qui peut exécuter le déploiement. Le processus de rotation des secrets, la révocation et la réponse à une fuite doivent être documentés. Dans un pipeline, ne place pas le secret en ligne de commande si cela peut l'exposer au journal ou à la liste des processus ; utilise le mécanisme approuvé.

Ne confonds pas chiffrement du fichier et absence de fuite. Une tâche peut imprimer une variable secrète, une erreur peut inclure un paramètre ou un diff peut montrer une configuration complète. La revue doit comprendre le chemin complet de la donnée : stockage, déchiffrement, utilisation, journaux et destination.

## 12. Gestion des erreurs, reprise et retour arrière

Une automation peut échouer sur une partie seulement de ses cibles. Le rapport doit identifier les hôtes réussis, en erreur, inaccessibles et non exécutés. Relancer globalement sans comprendre l'état partiel peut répéter les actions sur les hôtes réussis ou aggraver ceux qui ont échoué. Les tâches doivent être conçues pour détecter l'état actuel et reprendre sans action destructive, lorsque c'est possible.

Le retour arrière dépend de l'action. Pour un fichier de configuration, conserver la version précédente, valider la syntaxe avant rechargement et tester l'application peut fournir un chemin. Pour une mise à jour de paquet, revenir à la version précédente peut être impossible ou risqué. Pour une migration de base de données, le retour peut nécessiter une stratégie particulière. Les limites doivent être comprises avant l'exécution.

~~~mermaid
flowchart TD
    A[Exécution terminée] --> B[Lire résultat par cible]
    B --> C{Toutes les cibles attendues ont réussi ?}
    C -->|Oui| D[Contrôle fonctionnel et clôture]
    C -->|Non| E[Isoler les cibles en échec]
    E --> F[Collecter logs et état actuel]
    F --> G{Relance sûre et autorisée ?}
    G -->|Oui| H[Relancer sur périmètre réduit]
    G -->|Non| I[Escalader ou appliquer retour approuvé]
    H --> J[Validation finale]
    I --> J
~~~

Ne traite pas les erreurs comme du bruit à ignorer. Les options qui ignorent les erreurs ou continuent après un échec doivent être justifiées. Une exécution « verte » n'a aucune valeur si les contrôles critiques ont été sautés. Le compte rendu doit expliquer quels systèmes ont été modifiés, lesquels n'ont pas changé, les effets observés, les limites et les actions restantes.

## 13. Automatiser la production d'un rapport

Un script peut extraire des données d'un helpdesk, calculer des totaux, créer un CSV et préparer un brouillon de reporting. Sépare l'extraction des transformations et de la présentation pour que chaque partie puisse être testée. La méthode de calcul doit rester versionnée avec le dictionnaire d'indicateurs. Les sorties doivent inclure la période et les métadonnées nécessaires à leur interprétation.

Les erreurs de date, les filtres et les doublons peuvent fausser le résultat. Ajoute des tests de données : le nombre de tickets d'un échantillon correspond-il à la source ? Les identifiants sont-ils uniques ? Les dates sont-elles dans la période ? Les valeurs absentes sont-elles signalées ? Un contrôle des écarts par rapport au mois précédent peut déclencher une revue, mais ne doit pas automatiquement déclarer la donnée fausse.

L'automatisation d'un rapport ne doit pas diffuser automatiquement les informations sensibles à tous les destinataires. Prépare un brouillon, donne les sources et définitions, puis fais approuver les chiffres et les conclusions. Le rapport est archivé avec la version du script et les paramètres d'extraction. Si le calcul change, conserve la trace qui permet de comprendre pourquoi le chiffre du mois actuel n'est pas strictement comparable à celui du mois précédent.

## 14. Travaux pratiques guidés

### TP 1 — Automatiser un contrôle sans effet de bord

Écris un programme qui lit un fichier contenant des noms de services et produit un rapport d'état. Il doit valider les noms, utiliser une source autorisée, enregistrer heure et résultat, gérer les délais, séparer erreur et indisponibilité et ne modifier aucun service.

**Correction attendue :** les entrées invalides sont refusées ; chaque vérification produit un statut déterminé ; les échecs sont journalisés ; le programme se termine avec un code non nul si une vérification obligatoire échoue. Le rapport ne contient aucun secret. Les tests couvrent au moins une cible disponible, une cible indisponible, une entrée invalide et un timeout.

### TP 2 — Déployer dans Ansible un fichier fictif

Crée un inventaire de laboratoire, puis un playbook qui garantit qu'un fichier de test existe avec une ligne attendue. Lance d'abord la vérification syntaxique, puis check mode et diff lorsque les modules le prennent en charge. Teste deux exécutions successives.

**Correction attendue :** la première exécution indique un changement si le fichier diffère ; la seconde ne devrait plus produire de changement lorsque l'état souhaité est atteint. Les cibles sont limitées au laboratoire. Le résultat est vérifié sur la cible et la preuve conservée. Ne lance pas un playbook qui modifie un fichier réel de production pour réaliser l'exercice.

### TP 3 — Ajouter une gestion d'erreur

Simule un hôte inaccessible dans un groupe de trois cibles. Propose le traitement du résultat partiel.

**Correction attendue :** rapporter les deux succès et l'échec sans le masquer. Conserver la cible et le message d'erreur, vérifier la cause, et relancer uniquement si l'action est sûre et le périmètre autorisé. Ne pas exécuter un changement plus large pour « essayer ».

### TP 4 — Protéger un secret

Décris comment conserver une variable sensible utilisée par un playbook.

**Correction attendue :** utiliser le mécanisme Vault approuvé ou un gestionnaire de secrets, limiter l'accès aux personnes nécessaires, éviter de l'imprimer, protéger la sortie de tâches et définir une rotation. Vérifier que les permissions, journaux et pipelines ne révèlent pas la valeur.

### TP 5 — Orchestrer une tâche planifiée

Prépare une fiche de tâche quotidienne qui contrôle l'âge de la dernière sauvegarde valide et crée une alerte si le délai autorisé est dépassé.

**Correction attendue :** l'entrée est la source officielle du dernier point vérifié, pas simplement l'heure de démarrage du job. Le script vérifie la fraîcheur, trace les données, respecte un timeout, empêche les exécutions concurrentes et remonte un statut exploitable. Une tâche qui ne s'exécute plus doit également être détectée.

### TP 6 — Plan d'automatisation progressive

Choisis une tâche de maintenance du parc et prépare une progression du manuel au pilote, puis à une petite vague et enfin à un déploiement.

**Correction attendue :** formaliser la procédure manuelle, définir les critères de réussite, créer une version de test, obtenir l'autorisation, limiter le pilote, analyser les journaux, confirmer le retour arrière, élargir progressivement et suivre les exceptions. Chaque étape produit une preuve.

## 15. Exercices avec corrections

### Exercice 1 — Script qui retourne toujours zéro

Le script affiche un message d'erreur mais termine avec le code de sortie zéro.

**Correction :** corriger le chemin de l'erreur afin qu'un échec obligatoire produise un code non nul. Le système d'ordonnancement et la supervision utilisent souvent ce code pour déterminer le résultat ; un journal d'erreur sans statut peut laisser la tâche marquée comme réussie.

### Exercice 2 — Cron envoie deux rapports

Le rapport quotidien prend huit minutes, mais la planification lance une nouvelle exécution toutes les cinq minutes.

**Correction :** définir une période compatible, un verrou ou un mécanisme de non-concurrence, et une politique si une exécution précédente est toujours active. Vérifier la durée réelle et signaler les exécutions qui dépassent leur budget.

### Exercice 3 — Playbook cible trop de serveurs

Une faute de variable cible un groupe de production au lieu du laboratoire.

**Correction :** arrêter et examiner l'étendue, ne pas relancer pour « réparer » au hasard, collecter l'état et les changements déjà appliqués, puis appliquer le processus d'incident ou de changement approprié. Prévenir les responsables, vérifier les services et corriger les gardes de portée. Le pilote et le contrôle de l'inventaire auraient dû détecter la mauvaise cible.

### Exercice 4 — Check mode sans résultat

Le playbook réussit en mode check mais échoue lors de l'exécution réelle.

**Correction :** le mode check est une simulation et certains modules ou conditions dépendent de résultats qui ne sont pas produits en check mode. Examiner les limites de la tâche, tester sur un environnement représentatif, contrôler les entrées et ne pas interpréter check mode comme une garantie de succès.

### Exercice 5 — Secret affiché dans les logs

Un playbook échoue et la sortie contient un jeton d'API.

**Correction :** traiter cela comme une exposition potentielle : restreindre les journaux selon la procédure, révoquer ou renouveler le secret selon la décision de l'équipe responsable, corriger les tâches pour supprimer les fuites et vérifier les artefacts du pipeline. Le chiffrement Vault au repos n'empêche pas une fuite pendant l'exécution.

### Exercice 6 — Répétition d'une commande destructive

Un script supprime un répertoire et est lancé deux fois automatiquement.

**Correction :** arrêter les exécutions suivantes, vérifier les effets et les sauvegardes, préserver les éléments nécessaires puis suivre le plan de récupération. La tâche doit être redessinée avec une validation de chemin, un mode de simulation, une limite de cible et un contrôle d'état avant suppression. Certaines actions ne doivent pas être répétées automatiquement.

### Exercice 7 — Déploiement partiel

Un playbook réussit sur 18 hôtes et échoue sur 2.

**Correction :** consigner les cibles et états distincts, examiner les erreurs des deux hôtes, vérifier si l'état final des 18 hôtes est conforme, puis corriger et relancer uniquement la partie non réussie si le comportement est sûr. Il faut faire un test post-déploiement à l'échelle du service.

### Exercice 8 — Rapport automatique incohérent

Le script affiche zéro incident, alors que le système source contient plusieurs incidents.

**Correction :** vérifier la période, le fuseau, le statut filtré, la pagination/API, les droits et le mapping de catégories. Échantillonner quelques identifiants, ajouter une alerte de données vide inattendue et ne pas publier un zéro tant que la requête n'est pas validée.

## 16. Défi final corrigé — Automatiser une maintenance répétitive

Une entreprise gère 25 serveurs Linux et plusieurs équipements réseau. L'équipe doit vérifier les versions, sauvegarder les configurations, surveiller le dernier point de sauvegarde et générer un tableau mensuel. Propose une automatisation sans risque disproportionné.

### Travail demandé

1. choisir les tâches adaptées et celles qui restent soumises à décision humaine ;
2. définir les inventaires et périmètres ;
3. écrire un script de vérification en lecture seule ;
4. proposer un playbook Ansible à état souhaité dans un laboratoire ;
5. prévoir check/diff, pilote, autorisations, journaux et retour ;
6. protéger les secrets et contrôler les privilèges ;
7. définir les codes de sortie et la gestion des cibles en échec ;
8. produire un reporting avec preuve et propriétaire.

### Correction détaillée

**Découpage :** commencer par la collecte en lecture seule des versions, de la capacité, de l'état du service et du dernier point de sauvegarde vérifié. Une modification de configuration est séparée de la collecte. Un déploiement de correctif reste un changement planifié, pas une conséquence automatique d'un seuil.

**Portée :** l'inventaire utilise des groupes explicites et les hôtes de laboratoire. La commande de contrôle montre les cibles avant l'exécution. Le premier essai se fait sur un hôte représentatif et la vague augmente seulement après validation.

**Playbook :** déclarer les états attendus avec les modules adaptés, versionner le fichier, vérifier la syntaxe, utiliser check/diff lorsqu'ils sont pris en charge et examiner les effets. Les secrets sont fournis par Vault ou le mécanisme approuvé. Les tâches qui exposent une donnée sensible évitent la diffusion de valeurs dans la sortie.

**Erreur et reprise :** la sortie distingue les succès, les erreurs et les hôtes inaccessibles. Un job planifié doit signaler les exécutions manquantes, les délais dépassés et les résultats périmés. Les relances sont limitées à un périmètre sûr et à une action qui peut être répétée. Un retour arrière est défini pour les changements qui en nécessitent un.

**Reporting :** un export structuré indique l'heure, la version, les hôtes, le résultat, les exceptions et les liens vers les preuves. Le rapport mensuel compare l'état actuel avec le mois précédent, indique les données manquantes et attribue les actions. Une personne valide les résultats et le changement avant diffusion.

### Barème indicatif

- 15 % : choix pertinent des tâches ;
- 15 % : contrôle de la portée et des entrées ;
- 15 % : qualité et idempotence du script/playbook ;
- 15 % : sécurité et gestion des secrets ;
- 15 % : tests, check mode et pilote ;
- 10 % : journalisation, erreurs et reprise ;
- 15 % : preuve, reporting et suivi.

## 17. Checklist avant exécution en environnement réel

- objectif, propriétaire et périmètre documentés ;
- inventaire et cibles affichés et validés ;
- entrées contrôlées et variables explicites ;
- privilèges limités au besoin ;
- secrets protégés dans stockage, exécution et journaux ;
- script ou playbook versionné et relu ;
- tests automatisés et environnement laboratoire disponibles ;
- check mode/diff utilisé lorsque compatible et limites connues ;
- pilote et fenêtre approuvés pour toute modification ;
- timeout, non-concurrence, codes de sortie et reprise définis ;
- effet final vérifié après exécution ;
- résultats par cible conservés avec les erreurs et exclusions ;
- retour arrière ou procédure d'arrêt connus ;
- rapport et actions restantes attribués.

## 18. Synthèse et documentation officielle

Une automatisation fiable s'appuie sur un processus compris, une cible maîtrisée, une validation d'entrée, des droits limités, une gestion d'erreur, des journaux, des tests et une preuve finale. Les scripts conviennent aux contrôles ciblés et aux traitements structurés ; Ansible permet d'exprimer des états et tâches sur un ensemble d'hôtes, à condition de contrôler l'inventaire, l'idempotence et les effets de chaque module.

Le mode check et le mode diff aident à inspecter les changements prévus, mais ne garantissent pas le comportement de toutes les tâches. Ansible Vault protège les valeurs chiffrées au repos ; il faut encore éviter de divulguer les secrets pendant l'exécution. La meilleure automatisation est celle que l'équipe peut expliquer, auditer, reprendre et arrêter sans aggraver une panne.

Sources officielles :
- Ansible Playbooks : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html
- Ansible check mode et diff mode : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html
- Ansible Vault : https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html
