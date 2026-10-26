# MPLS-TP & Métro Ethernet — Expert

> **Mise en contexte**
> Après une coupure, le chemin de secours apparaît actif, mais certaines trames sont perdues et les objectifs de restauration ne sont pas respectés. Il faut examiner la protection, l’OAM, le MTU, la QoS et la dépendance physique des chemins.

## Objectifs d’apprentissage
À la fin du cours, vous saurez concevoir travail et protection, distinguer les modes de bascule et de réversion, définir les contrôles OAM, examiner MTU/QoS et organiser une recette de transport reproductible.

## Prérequis
Maîtriser LSP, service Ethernet, VLAN, UNI/NNI, pseudowire et OAM, ainsi que les bases MPLS et le niveau intermédiaire de ce parcours.

## 1. Partir des exigences du service
Le transport doit respecter les contraintes contractuelles, pas seulement conserver un voyant au vert. Les exigences doivent être mesurables : disponibilité, délai, gigue, pertes, débit, taille de trame, délai de restauration et comportement de réversion.

Pour chaque service, documenter origine/destination et UNI, identifiant et VLAN, encapsulation, MTU, classe QoS, débit, chemin de travail, chemin de protection, OAM disponible, seuils et critères de retour arrière. Sans critères définis avant les essais, « ça fonctionne » ne prouve pas la conformité.

## 2. LSP, service et transport
Un LSP représente un chemin de transfert à labels dans le domaine MPLS ; un service Ethernet représente la connectivité fournie au client. Le service est associé à une fonction de transport selon la configuration retenue. Un état LSP positif n’exclut pas une panne de classification VLAN, d’encapsulation, de pseudowire, de MTU ou de QoS.

MPLS-TP adapte MPLS aux exigences d’exploitation des réseaux de transport, notamment par OAM et protection structurées. Les détails du plan de contrôle, de la gestion et de la configuration varient selon les équipements et les profils déployés.

## 3. Protection : plus que deux chemins dans un schéma
La protection peut utiliser des modes comme 1+1 ou 1:1 selon les mécanismes disponibles. Dans une approche 1+1, le trafic peut être transmis sur le chemin de travail et celui de protection, puis sélectionné à la réception. Dans une approche 1:1, la ressource de protection reprend le trafic lorsque les conditions sont remplies. Les comportements précis dépendent de l’implémentation et doivent être vérifiés.

Des LSP distincts peuvent partager une même fibre, un conduit, un nœud, un site, une alimentation, un système de refroidissement ou un équipement d’extrémité. Une carte logique ne démontre pas l’indépendance physique.

## 4. Bascule, réversion et restauration
Le plan doit préciser les événements déclencheurs, les temporisations, le comportement au retour du chemin de travail et les actions opérateur. En mode réversible, le trafic peut revenir au chemin initial lorsque les critères sont remplis ; en mode non réversible, il peut rester sur le chemin actif jusqu’à une action ou un nouvel événement selon la configuration.

Lors d’un essai autorisé :
1. enregistrer le défaut injecté et l’heure ;
2. vérifier la détection et la bascule ;
3. mesurer interruption, pertes, délai et gigue ;
4. vérifier capacité résiduelle et maintien des autres services ;
5. observer le retour du chemin principal ;
6. contrôler alarmes, journaux et état final.

Ne jamais provoquer une coupure de production sans autorisation, fenêtre, analyse d’impact et retour arrière approuvé.

## 5. OAM et localisation des défauts
OAM varie selon le niveau : interface, transport, chemin ou service. Une alarme ne couvre pas nécessairement l’ensemble de la chaîne ; interpréter le résultat selon le mécanisme, le point de mesure et le service surveillé.

| Observation | Piste |
|---|---|
| Port physique actif, service indisponible | VLAN, classification, MTU ou service aux extrémités |
| LSP actif, OAM de service en défaut | Association service/transport, extrémités, pseudowire et profil OAM |
| Plusieurs services tombent ensemble | Équipement/chemin partagé, ressource commune ou changement récent |
| Défaut uniquement après bascule | Capacité du secours, MTU différent, paramètres ou classification |
| Alarmes intermittentes | Compteurs, événements synchronisés, erreurs physiques, historique et seuils |

Corréler les horodatages des mesures client, UNI et transport améliore la fiabilité de la localisation.

## 6. MTU, encapsulation et QoS
La MTU doit être cohérente sur tout le chemin. Les encapsulations ajoutent des en-têtes et peuvent accroître la taille transportée ; vérifier la capacité de chaque segment. Des petits paquets qui passent alors que les grandes trames échouent orientent vers la MTU, sans constituer une preuve définitive.

La vitesse nominale d’un port ne garantit pas un débit réservé à chaque classe QoS. Classification, marquage, files d’attente, limites et congestion modifient le comportement. Pour la recette, tester des tailles de trames et profils de trafic pertinents, puis documenter durée, charge, directions, compteurs et seuils.

## 7. TP guidé : restauration non conforme
**Situation :** après la rupture du chemin de travail, l’OAM signale un défaut et le chemin de protection devient actif. Les petites trames passent, les grandes échouent et le délai dépasse l’objectif.

1. Enregistrer l’heure de panne, les alarmes et l’évolution des états.
2. Mesurer interruption et pertes selon la méthode contractuelle.
3. Comparer travail et secours : MTU, service, QoS, capacité et extrémités.
4. Contrôler association service/LSP et résultats OAM.
5. Vérifier la diversité physique avec des sources documentées.
6. Reproduire en laboratoire ou dans une fenêtre autorisée.
7. Définir les actions correctives, critères de réussite et retour arrière.
8. Rejouer le test dans les mêmes conditions et produire le rapport.

**Livrables :** chronologie horodatée, matrice des états, résultats, cause retenue et preuves, risques résiduels et plan préventif.

## Exercices corrigés
**1.** Le secours est un LSP différent mais partage le même conduit. Est-il indépendant ?  
**Correction :** non. Une coupure du conduit peut affecter les deux routes ; vérifier la diversité réelle et les autres points de panne commune.

**2.** Après bascule, les grandes trames échouent. Que vérifier ?  
**Correction :** MTU par segment, surcharge d’encapsulation et différences de configuration du chemin de secours. Les compteurs et un test de tailles progressives aident à confirmer.

**3.** Pourquoi contrôler les autres services pendant un test de protection ?  
**Correction :** le trafic déplacé peut saturer des ressources partagées ; vérifier capacité résiduelle, performances et absence de régression.

## Défi final corrigé
**Scénario :** après bascule, un service reste instable ; au retour du chemin principal, la transition ne respecte pas le délai contractuel.

**Correction attendue :** aligner la chronologie des alarmes et tests, comparer travail et secours pour MTU, QoS, capacité, extrémités et associations, puis vérifier les règles de réversion et la diversité physique. Définir les seuils à partir du contrat avant les essais. N’autoriser la mise en service qu’après validation des deux transitions, du service complet et des autres services affectés.

## À retenir
Une architecture robuste exige des chemins adaptés, des critères explicites, une OAM interprétable, MTU et QoS cohérents et des essais reproductibles. La conformité se démontre par des mesures, pas par le seul état « actif ».
