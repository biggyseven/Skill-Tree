# Fibre optique & DWDM — Expert

> **Mise en contexte**
> Un opérateur veut ajouter des canaux 400G sur une liaison longue distance déjà chargée. La puissance totale reste nominale, mais les marges varient selon les canaux et le service le plus exigeant devient instable. L’ingénieur doit prouver la faisabilité, identifier les contraintes partagées et définir une mise en service mesurable et réversible.

## Objectifs d’apprentissage
À la fin du cours, vous saurez établir une méthode d’ingénierie de capacité, analyser puissance, OSNR et marges, expliquer l’impact de la dispersion et des non-linéarités, distinguer dimensionnement et acceptation et produire un plan d’extension avec retour arrière.

## Prérequis
Maîtriser le budget optique, dB/dBm, MUX/DEMUX, EDFA et OSNR. La modulation cohérente, les transpondeurs modernes et les métriques d’erreur sont des notions utiles.

## 1. Ingénierie d’une liaison cohérente
Un système cohérent exploite des propriétés de l’onde optique et un traitement numérique du signal au récepteur. Selon l’équipement, ce traitement compense une grande partie de la dispersion chromatique et certains effets de propagation. Il ne supprime pas toutes les limites physiques : OSNR, dispersion de polarisation, non-linéarités, bande passante et marges restent à considérer.

Le débit maximal d’une fiche technique ne suffit pas à prouver qu’un profil fonctionnera sur le chemin réel. Un dossier d’ingénierie doit documenter :
- inventaire des fibres, spans, connecteurs, épissures et équipements ;
- plan de fréquences, largeur de canal et capacités des transpondeurs ;
- pertes mesurées ou hypothèses justifiées par span ;
- modèle d’amplification et limites de puissance ;
- référence et objectifs OSNR / qualité pour chaque canal ;
- profils de transmission, portée et marges selon la documentation constructeur ;
- scénarios de panne, capacité de protection et critères d’acceptation.

## 2. Spectre, canaux et capacité
Le spectre disponible est fini. Le nombre de canaux dépend de la bande optique, de la grille, de la largeur occupée par chaque signal, des marges spectrales et des filtres. Une grille flexible peut adapter les allocations à différents profils, mais elle ne rend pas le spectre illimité.

La capacité agrégée ne se déduit pas uniquement du nombre de canaux multiplié par un débit commercial. Il faut confirmer capacité nette utile, FEC, encapsulation, compatibilité des composants et chemin de bout en bout.

Pour préparer une extension : établir l’inventaire actuel ; déterminer les canaux et profils visés ; vérifier les composants partagés ; modéliser puissance, OSNR et risques de saturation ; mesurer l’état de référence ; puis mettre en service progressivement selon le plan approuvé.

## 3. Amplification en cascade et OSNR
Un EDFA compense la perte d’un span, mais introduit du bruit. Le résultat d’une longue chaîne dépend de tous les spans et amplificateurs, pas du dernier niveau Rx isolé. Un niveau élevé à la réception peut coexister avec une marge OSNR insuffisante ou une dégradation des canaux voisins.

Documenter les puissances d’entrée et de sortie, le gain demandé et mesuré, la puissance totale et par canal, l’OSNR et sa méthode de mesure, les alarmes et les métriques numériques du transpondeur. Chaque mesure doit avoir une unité, un point de mesure et un horodatage. Des méthodes différentes ne doivent pas être comparées comme équivalentes sans vérification.

## 4. Dispersion et non-linéarités
La dispersion chromatique étale les composantes d’un signal selon leur longueur d’onde. Les systèmes cohérents compensent souvent une grande partie de cet effet par traitement numérique, dans les limites de leur conception.

Les effets non linéaires peuvent devenir significatifs à forte puissance ou avec une forte densité spectrale. Leur importance dépend notamment de la puissance par canal, du nombre de canaux, du spectre et des propriétés de la fibre. Le choix d’une puissance optimale est un compromis entre OSNR et pénalités non linéaires.

Deux raisonnements sont à éviter :
- **« Plus de puissance résout toujours les erreurs »** : un excès peut accroître certaines pénalités.
- **« L’OSNR suffit à valider le système »** : les erreurs, les marges, les alarmes et le service doivent aussi être vérifiés.

## 5. Protection et risque de panne commune
Une capacité de secours n’est utile que si le chemin de protection dispose des ressources nécessaires et évite les points de défaillance communs pertinents. Deux chemins logiques distincts peuvent partager une fibre, un conduit, un site d’amplification ou une alimentation.

Distinguer la capacité nominale, la capacité utile en fonctionnement normal, la capacité après perte d’un équipement ou d’un span, la capacité disponible après bascule et les marges réservées à la croissance et à la maintenance. Une bascule configurée ne prouve pas la résilience sans test contrôlé et autorisé.

## 6. Atelier d’analyse d’une liaison
**Situation :** une route de six spans transporte 40 canaux. Le projet veut en ajouter huit. Après une mise à jour, l’OSNR baisse sur les canaux proches d’une extrémité de bande et un transpondeur passe sous sa marge cible.

1. Geler les modifications et sauvegarder l’état observé.
2. Comparer les mesures à la référence, avec la même méthode.
3. Vérifier inventaire, fréquences, largeur de canal et filtres.
4. Examiner puissance par canal, puissance totale et amplificateurs des spans concernés.
5. Contrôler alarmes et métriques numériques.
6. Formuler plusieurs hypothèses et choisir des tests qui les départagent.
7. Tester une correction limitée dans une fenêtre approuvée.
8. Revalider les canaux existants autant que les nouveaux.

| Observation | Hypothèses | Preuve utile |
|---|---|---|
| Tous les canaux d’un span baissent | Perte, connectique, span ou amplificateur | Mesures intermédiaires, puissance d’entrée/sortie |
| Quelques canaux se dégradent | Filtrage, puissance inégale, fréquence, transpondeur | Spectre, inventaire, mesure par canal |
| Puissance stable, erreurs en hausse | OSNR, non-linéarités, transpondeur, changement récent | OSNR, métriques récepteur, historique |
| Protection non conforme | Capacité résiduelle, chemin partagé, politique de bascule | Essai contrôlé, mesure après bascule, carte physique |

## 7. TP guidé : dossier d’augmentation de capacité
Préparer un dossier pour ajouter des canaux à une route optique existante. Les mesures et seuils doivent être fournis par le scénario ou le constructeur, pas inventés.

1. Dessiner les spans et les points de mesure.
2. Lister fréquences, transpondeurs et profils proposés.
3. Calculer le budget de chaque span à partir des pertes documentées.
4. Comparer avant/après puissance, OSNR et indicateurs numériques.
5. Définir les conditions qui déclenchent l’arrêt du changement.
6. Décrire le retour arrière et les critères de retour au service.
7. Vérifier la capacité résiduelle après perte d’un span ou d’un site critique.

**Livrables :** schéma, calculs avec unités, registre d’hypothèses, mesures, décision Go/No-Go, procédure de changement et de restauration.

## Exercices corrigés
**1.** Après ajout, la puissance Rx reste conforme mais l’OSNR diminue. Que conclure ?  
**Correction :** la puissance ne suffit pas. Examiner bruit, équilibre spectral, cascade d’amplification, limites et performances du récepteur.

**2.** Deux routes logiques de protection sont distinctes. Quelle question reste indispensable ?  
**Correction :** vérifier la diversité physique et les dépendances partagées : conduits, sites, alimentation, amplificateurs et autres équipements communs.

**3.** Pourquoi re-tester les canaux déjà en service ?  
**Correction :** l’ajout peut modifier puissance, spectre et marges des canaux existants ; la recette doit couvrir tout le périmètre affecté.

## Défi final corrigé
**Scénario :** le projet veut doubler la capacité d’une route chargée ; le budget après bascule est inconnu.

**Correction attendue :** ne pas autoriser le changement sur la seule base de la capacité nominale. Obtenir mesures et paramètres vérifiables, modéliser les marges des canaux et les pires cas de panne, confirmer l’indépendance physique de la protection et effectuer les essais contrôlés. Définir les seuils d’arrêt et de retour arrière avant la mise en service. Sans preuve sur les marges ou la capacité de secours, la décision reste No-Go.

## À retenir
L’ingénierie DWDM combine spectre, bilan de puissance, bruit, transpondeurs, effets de propagation et résilience. L’expertise se démontre par un dossier de mesures, une décision argumentée et une validation de bout en bout.
