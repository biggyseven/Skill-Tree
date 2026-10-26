# Fibre optique & DWDM — Intermédiaire

> **Mise en contexte**
> Une liaison optique de 80 km transporte correctement le signal le matin, mais les erreurs augmentent après l’ajout de plusieurs canaux. Le lien reste actif : il faut relier les mesures de puissance, les pertes, l’amplification et la qualité optique au service transporté.

## Objectifs d’apprentissage
À la fin du cours, vous saurez construire un budget optique, expliquer le rôle d’un MUX/DEMUX et d’un EDFA, décrire le plan de canaux DWDM, interpréter la puissance reçue et l’OSNR et diagnostiquer une dégradation à partir de mesures.

## Prérequis
Connaître les grandeurs dB et dBm, les bases de la fibre monomode et les composants d’une liaison optique. Le niveau débutant du parcours Fibre optique & DWDM constitue le point de départ.

## 1. De WDM à DWDM
Le multiplexage en longueur d’onde transporte plusieurs signaux optiques à des longueurs d’onde différentes sur une même fibre. Chaque canal peut porter un service indépendant, sous réserve de compatibilité des transpondeurs, de la grille, des puissances et du système de transmission.

- **WDM** est le principe général du partage d’une fibre par longueurs d’onde.
- **CWDM** utilise généralement un espacement spectral plus large et convient à certaines distances et capacités métropolitaines.
- **DWDM** rapproche davantage les canaux et augmente la capacité agrégée, au prix d’une ingénierie plus stricte.

    Transpondeurs → MUX → fibre / amplificateurs → DEMUX → transpondeurs
                       λ1  λ2  λ3  λ4

Le multiplexeur combine les canaux en émission ; le démultiplexeur les sépare à la réception. Ces fonctions passives ne corrigent pas un signal dégradé et ne garantissent pas, à elles seules, la compatibilité entre équipements.

## 2. Grille de fréquences et plan de canaux
Les systèmes DWDM sont habituellement planifiés à partir d’une grille de fréquences. Un canal est identifié par sa fréquence centrale ; sa longueur d’onde correspondante dépend de la fréquence. L’espacement doit être compatible avec le système, la largeur du signal modulé et les équipements.

Un espacement plus faible ne signifie pas automatiquement une capacité utile plus importante : il faut considérer la modulation, le débit symbolique, la bande passante optique, le filtrage et les performances du récepteur.

Avant d’ajouter un canal, vérifier la fréquence centrale, la grille autorisée, les filtres, la plage des transpondeurs, les limites de puissance, la capacité des amplificateurs et les marges prévues.

## 3. Budget optique : calculer avant de déployer
Le budget estime si la puissance disponible peut traverser les pertes tout en restant dans les limites du récepteur.

\[
P_{Rx}=P_{Tx}-L_{fibre}-L_{connecteurs}-L_{épissures}-L_{autres}
\]

Les pertes sont exprimées en dB ; les puissances absolues en dBm. Les gains d’amplification doivent être ajoutés avec leur valeur et leur emplacement réels, sans oublier le bruit du système.

**Exemple pédagogique :** puissance Tx +2 dBm ; fibre de 60 km à 0,22 dB/km (13,2 dB) ; quatre connexions à 0,25 dB (1,0 dB) ; dix épissures à 0,1 dB (1,0 dB). La perte estimée vaut 15,2 dB, donc la puissance Rx sans amplification est +2 − 15,2 = −13,2 dBm.

Il faut comparer cette valeur à la plage du récepteur et à la marge d’ingénierie exigée. Les pertes unitaires sont des hypothèses pédagogiques ; un projet réel se base sur les spécifications et les mesures du trajet.

Une puissance Rx conforme ne prouve pas une qualité optique suffisante. Une puissance trop forte peut aussi saturer un récepteur ou un étage optique : plus de puissance n’est pas toujours mieux.

## 4. EDFA, gain et bruit
Un amplificateur EDFA augmente la puissance optique dans une bande compatible avec son fonctionnement. Dans une liaison DWDM, il amplifie généralement plusieurs canaux simultanément. Il faut respecter les limites de puissance totale et par canal, les plages de gain et de sortie, l’équilibre entre canaux, les objectifs de qualité et les alarmes constructeur.

Chaque étage d’amplification ajoute du bruit optique. La cascade des amplificateurs peut donc dégrader l’OSNR même si la puissance reçue paraît suffisante. Augmenter le gain sans localiser la perte peut masquer le symptôme ou créer d’autres problèmes.

## 5. Comprendre l’OSNR
L’OSNR (Optical Signal-to-Noise Ratio) compare la puissance du signal optique à celle du bruit optique dans une bande de référence. Les méthodes et conditions de référence doivent être documentées pour comparer des résultats.

Distinguer :
- **puissance Rx** : niveau optique reçu ;
- **OSNR** : qualité du signal par rapport au bruit optique ;
- **BER / erreurs** : résultat numérique observable ;
- **disponibilité** : capacité à respecter les critères convenus du service.

Une baisse d’OSNR peut venir du bruit des amplificateurs, de niveaux de signal inadéquats, d’un mauvais équilibre des canaux ou de la conception du chemin. Croiser les mesures est préférable à une conclusion fondée sur une seule valeur.

## 6. Diagnostic structuré

| Symptôme | Vérifications initiales | Précaution |
|---|---|---|
| Puissance Rx trop faible | Connecteurs, épissures, courbures, pertes par span et mesures | Ne pas augmenter le gain avant de localiser la perte |
| Puissance dans la plage mais erreurs en hausse | OSNR, alarmes, compteurs, canaux et changements récents | Le niveau Rx ne prouve pas la qualité |
| Un seul canal est affecté | Transpondeur, fréquence, filtre MUX/DEMUX et puissance du canal | Comparer aux canaux voisins |
| Plusieurs canaux se dégradent après un changement | Équilibre des puissances, EDFA, saturation et inventaire des canaux | Modifier un paramètre à la fois |
| Calcul et mesure divergent | Hypothèses de pertes, instruments et unités | Vérifier la méthode et l’étalonnage |

## 7. TP guidé : réception en marge insuffisante
**Situation :** après un raccordement, la puissance reçue baisse de 2,5 dB sur un côté et les erreurs augmentent sur un seul canal.

1. Relever et horodater Tx/Rx, OSNR, compteurs d’erreurs et alarmes.
2. Comparer les valeurs au référentiel antérieur et aux canaux voisins.
3. Vérifier le raccordement, la propreté des connecteurs et le chemin selon les procédures du site.
4. Répéter les mesures après toute action corrective autorisée.
5. Valider le canal et le service de bout en bout.

**Livrables :** tableau avant/après avec unités, hypothèse prioritaire, preuves qui la confirment ou l’écartent et critère de réussite.

## Exercices corrigés
**1.** Une fibre présente 9 dB de perte et les éléments de raccordement ajoutent 2 dB. Quelle est la perte passive ?  
**Correction :** 9 + 2 = 11 dB. Sans autre gain, Rx estimée = Tx − 11 dB.

**2.** Rx reste dans la plage, mais OSNR baisse après ajout de canaux. La liaison est-elle forcément bonne ?  
**Correction :** non. Contrôler qualité optique, erreurs, équilibre des canaux, limites d’amplification et changements récents.

**3.** Un canal est dégradé et ses voisins sont stables. Quelle piste vérifier en premier ?  
**Correction :** la chaîne propre au canal — transpondeur, fréquence et filtrage — tout en confirmant l’hypothèse avec des mesures.

## Défi final corrigé
**Scénario :** après l’ajout de deux canaux, l’OSNR baisse et les erreurs augmentent sur le canal le plus sensible.

**Correction attendue :** figer l’état initial, comparer puissance par canal et OSNR, contrôler limites d’amplification, équilibre spectral, filtres et changements récents. Tester une hypothèse à la fois dans une fenêtre autorisée ; ne pas augmenter arbitrairement la puissance. Valider ensuite les critères optiques et numériques du chemin et la stabilité des canaux ajoutés comme des canaux existants.

## À retenir
Le budget estime les pertes ; l’EDFA compense une partie des pertes mais ajoute du bruit ; l’OSNR renseigne sur la qualité optique. Un diagnostic fiable associe calcul, mesures, historique et validation du service de bout en bout.
