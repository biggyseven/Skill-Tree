# Gestion d’incident (ITIL et RCA) — Niveau Expert

**Niveau :** Expert  
**Public cible :** responsables de gestion des services, Incident Commanders, Problem Managers, SRE, responsables d’exploitation, équipes NOC/SOC, propriétaires de services et responsables de continuité.  
**Prérequis :** maîtriser le cycle d’incident, la priorisation, l’escalade, les principes de RCA et la rédaction d’un post-incident review.  
**Objectif :** bâtir et piloter un système de réponse aux incidents qui limite l’impact métier, accélère le rétablissement, conserve les preuves et transforme l’événement en améliorations vérifiables.

<style>
@keyframes incidentFlow { to { stroke-dashoffset: -36; } }
svg .flow-animated { stroke-dasharray: 9 9; animation: incidentFlow 1.8s linear infinite; }
@media (prefers-reduced-motion: reduce) { svg .flow-animated { animation: none; } }
</style>

> **Principe directeur.** Le traitement de l’incident vise d’abord à protéger les personnes, les données et le service, puis à restaurer une situation acceptable. L’analyse causale vise ensuite à expliquer les mécanismes et les conditions qui ont rendu l’incident possible, puis à vérifier que les actions réduisent réellement le risque. Une RCA n’est ni une chasse au coupable ni une simple liste de tâches.

## Objectifs d’apprentissage

À la fin de ce cours, l’apprenant saura :

- concevoir un modèle d’incident majeur avec autorité de décision explicite et rôles séparés ;
- définir une sévérité à partir de l’impact métier, de l’étendue, de la durée, des obligations et du risque ;
- coordonner plusieurs équipes techniques et parties prenantes sous pression ;
- décider entre rollback, failover, limitation de trafic, mode dégradé et restauration ;
- construire une chronologie distinguant événements observés, actions, inférences et inconnues ;
- conduire une RCA multicause avec hypothèses falsifiables et niveaux de confiance ;
- produire des actions préventives, détectives et atténuantes, priorisées et testables ;
- mesurer la santé du processus sans encourager le masquage des incidents ;
- intégrer les incidents de sécurité, les fournisseurs, la continuité et la communication de crise ;
- auditer la maturité du dispositif et organiser des exercices réalistes.

## 1. Le modèle mental expert : service, incident, problème et risque

Un **incident** est un événement non planifié qui entraîne ou peut entraîner une interruption ou une dégradation d’un service. Le but opérationnel est de minimiser son impact et de rétablir le service dans un délai acceptable. Un **problème** correspond à la cause, ou aux causes potentielles, d’un ou de plusieurs incidents ; sa gestion cherche à réduire la probabilité et l’impact des récidives. Une **erreur connue** est un problème qui a été analysé mais pas nécessairement résolu, associé à une solution de contournement si disponible. Un **changement** modifie un service ou son environnement et peut être une action corrective, mais doit lui-même être gouverné par une évaluation de risque adaptée.

Il faut éviter trois raccourcis :

1. **Incident résolu ≠ problème résolu.** Un redémarrage peut restaurer la disponibilité sans enlever la cause de la saturation.
2. **Cause technique ≠ explication complète.** « La base de données a ralenti » décrit souvent un mécanisme proche, pas les conditions de conception, de capacité, de détection ou de contrôle qui ont permis l’impact.
3. **RCA achevée ≠ risque réduit.** La qualité se juge aussi aux actions livrées, à leur validation et aux récidives, pas seulement à la qualité du document.

### 1.1 Le modèle en couches de causalité

Une enquête robuste examine au moins cinq couches :

- **Déclencheur :** événement proche du début de l’incident (déploiement, expiration d’un certificat, pic de trafic, panne fournisseur).
- **Mécanisme de défaillance :** ce qui a techniquement transformé le déclencheur en panne (pool épuisé, route retirée, verrou, quota atteint).
- **Conditions latentes :** caractéristiques préexistantes (couplage, limites par défaut, capacité insuffisante, dépendance non résiliente).
- **Contrôles :** garde-fous qui auraient pu prévenir, limiter, détecter ou accélérer la récupération (tests, canary, alertes, limites de débit, rollback éprouvé).
- **Facteurs d’impact :** pourquoi une défaillance localisée s’est propagée (absence d’isolation, retries synchronisés, absence de mode dégradé, blast radius trop grand).

Une RCA experte ne force pas systématiquement une cause unique. Les incidents complexes résultent souvent de plusieurs conditions nécessaires ou contributives qui se rencontrent.

## 2. Gouvernance opérationnelle et modèle de responsabilité

### 2.1 Séparer les responsabilités pendant une crise

L’Incident Commander (IC) pilote l’événement ; il n’est pas automatiquement le spécialiste technique le plus senior. Il définit l’objectif de rétablissement, assigne les tâches, résout les conflits de priorité et veille à ce que les décisions soient consignées. Le lead technique organise le diagnostic et les actions techniques. Le responsable communication rédige et diffuse des messages cohérents. Le scribe tient la chronologie, les décisions, les hypothèses et les changements d’état. Selon l’organisation, un représentant métier, un responsable sécurité ou un liaison fournisseur complète l’équipe.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 520" width="100%" role="img" aria-label="Pilotage d’un incident majeur">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="1080" height="520" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Pilotage d’un incident majeur</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Séparer commandement, exécution technique, communication et consignation.</text>
<path d="M 199.7,220.0 L 269.8,185.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="234.7" y="194.5" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">déclarer</text>
<path d="M 455.0,141.9 L 520.0,143.1" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="487.5" y="134.5" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">déléguer</text>
<path d="M 455.0,182.8 L 520.0,212.2" fill="none" stroke="#ffbd59" stroke-width="3" marker-end="url(#arrowAmber)" class="flow-animated"/>
<text x="487.5" y="189.5" text-anchor="middle" fill="#ffbd59" font-size="13" font-weight="600">informer</text>
<path d="M 409.9,185.0 L 565.1,325.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="487.5" y="247.0" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">consigner</text>
<path d="M 710.0,143.3 Q 749.7,127.7 790.0,141.8" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="749.7" y="120.7" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">mitiger</text>
<path d="M 890.0,185.0 Q 877.6,255.0 890.0,325.0" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="877.6" y="248.0" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">apprendre</text>
<path d="M 710.0,370.0 L 790.0,370.0" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="750.0" y="362.0" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">chronologie</text>
<rect x="35" y="220" width="165" height="82" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="117.5" y="261.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Signal / alerte</text>
<rect x="265" y="95" width="190" height="90" rx="13" fill="#1b2844" stroke="#48b9ff" stroke-width="2"/>
<text x="360.0" y="130.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Incident Commander</text>
<text x="360.0" y="151.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">priorités &amp; décisions</text>
<rect x="520" y="100" width="190" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="615.0" y="135.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Lead technique</text>
<text x="615.0" y="156.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">diagnostic &amp; mitigation</text>
<rect x="520" y="210" width="190" height="90" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="615.0" y="245.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Communication Lead</text>
<text x="615.0" y="266.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">messages &amp; audience</text>
<rect x="520" y="325" width="190" height="90" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="615.0" y="360.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Scribe / timeline</text>
<text x="615.0" y="381.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">faits &amp; décisions</text>
<rect x="790" y="95" width="200" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="890.0" y="130.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Rétablissement</text>
<text x="890.0" y="151.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">tests &amp; stabilité</text>
<rect x="790" y="325" width="200" height="90" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="890.0" y="360.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Revue post-incident</text>
<text x="890.0" y="381.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">RCA &amp; actions</text>
</svg>

**Règle de taille :** pendant un incident majeur, une personne ne devrait pas simultanément commander, diagnostiquer un système complexe, rédiger les communications et prendre des notes exhaustives. Si l’effectif est réduit, attribuer explicitement les rôles cumulés et transférer l’autorité au fur et à mesure.

### 2.2 Matrice de responsabilité indicative

| Activité | Incident Commander | Lead technique | Communication | Scribe | Propriétaire métier |
|---|---|---|---|---|---|
| Déclarer la sévérité | A/R | C | I | I | C |
| Fixer l’objectif de rétablissement | A | R/C | I | C | C |
| Exécuter une mitigation | A pour l’arbitrage | R | I | C | C selon risque |
| Publier une mise à jour | A pour l’approbation | C | R | C | C |
| Tenir la chronologie | C | C | C | R/A | I |
| Confirmer l’impact métier | C | C | I | C | R/A |
| Approuver la clôture opérationnelle | A | R pour la preuve technique | C | C | C/A selon politique |
| Conduire la RCA | C | C | I | C | C ; Problem Manager A/R selon gouvernance |

**A** = accountable/autorité finale ; **R** = réalise ; **C** = consulté ; **I** = informé. Adaptez cette matrice à la taille et aux contraintes réglementaires de l’organisation. Il n’existe pas de matrice universelle qui remplace les responsabilités formellement établies.

### 2.3 Autorité et garde-fous

L’IC doit connaître les décisions qu’il peut prendre sans approbation supplémentaire, et les seuils qui exigent une validation métier, sécurité, conformité ou direction. Par exemple : couper une fonctionnalité non critique peut être préautorisé ; supprimer des données, restaurer un backup susceptible d’écraser des transactions récentes ou isoler un site complet peut requérir une autorité supérieure. Une matrice d’autorité est utile seulement si elle est accessible, comprise et répétée lors des exercices.

Documenter les éléments suivants avant une crise :

- services critiques, propriétaires et dépendances principales ;
- niveaux de sévérité et critères mesurables ;
- personnes d’astreinte et mécanisme de remplacement ;
- canaux de coordination et canal de secours si l’outil principal tombe ;
- actions préautorisées, seuils d’approbation et opérations interdites ;
- chemin de communication avec clients, direction, juridique, sécurité et fournisseurs ;
- politique de collecte, de conservation et d’accès aux éléments probants.

## 3. Définir une sévérité exploitable

La sévérité décrit le niveau d’attention et de mobilisation requis. La priorité de traitement dépend également de l’urgence, des obligations de service et du contexte métier. Ces concepts ne doivent pas être confondus mécaniquement avec la priorité d’un ticket isolé.

### 3.1 Axes de sévérité

Évaluer au minimum :

1. **Impact fonctionnel :** indisponibilité totale, dégradation, perte de données, erreur de transaction, intégrité compromise.
2. **Étendue :** un utilisateur, un segment, une région, tous les clients, un système interne ou un service inter-entreprises.
3. **Criticité métier :** revenu, sécurité, opérations essentielles, obligations contractuelles ou échéances non déplaçables.
4. **Durée et tendance :** panne stable, dégradation qui s’étend, backlog qui croît, capacité résiduelle qui s’épuise.
5. **Contournement :** fiable et acceptable, coûteux, partiel, ou absent.
6. **Risque de sécurité :** suspicion de compromission, exposition de données ou altération non expliquée.
7. **Incertitude :** si l’étendue n’est pas connue, le manque d’information peut justifier un classement temporairement plus élevé.

### 3.2 Exemple de grille locale

Cette grille est un **exemple à adapter**, et non une norme ITIL imposant ces niveaux.

| Niveau | Indices typiques | Mobilisation | Fréquence indicative des mises à jour |
|---|---|---|---|
| SEV-1 / Critique | Service vital indisponible, intégrité ou sécurité possiblement compromise, impact multi-région ou nombre important de clients | IC, lead technique, communication, métier et sécurité selon contexte | 15–30 min ou selon politique |
| SEV-2 / Majeur | Fonction importante fortement dégradée, contournement limité, impact métier significatif | Équipe de réponse dédiée et propriétaire de service | 30–60 min |
| SEV-3 / Modéré | Impact circonscrit, contournement disponible, pas de risque immédiat de propagation | Équipe de support propriétaire avec escalade si tendance défavorable | Selon SLA et évolution |
| SEV-4 / Faible | Incident localisé avec faible effet métier | File habituelle | Selon politique |

Les minutes sont des exemples. Le contrat de service ou le plan de crise peut exiger d’autres cadences.

### 3.3 Reclassification sans débat improductif

Au début, il est préférable de choisir une sévérité provisoire et de la réévaluer à partir de nouveaux éléments. Chaque changement de niveau doit avoir un motif et une heure consignés. L’équipe ne doit pas attendre d’avoir identifié la cause pour reconnaître un incident majeur. À l’inverse, la baisse de sévérité doit être justifiée par des indicateurs objectifs : erreur revenue à son niveau de référence, débit de backlog stable, transactions de test réussies, absence de nouvelles erreurs sur une fenêtre définie.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1060 420" width="100%" role="img" aria-label="Prioriser par impact et urgence">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="1060" height="420" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Prioriser par impact et urgence</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Une étiquette P1/P2 est une politique locale : documenter les seuils et les exceptions.</text>
<path d="M 270.0,145.0 L 370.0,145.0" fill="none" stroke="#ff717e" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="320.0" y="137.0" text-anchor="middle" fill="#ff717e" font-size="13" font-weight="600">croiser</text>
<path d="M 270.0,290.0 L 370.0,290.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="320.0" y="282.0" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">croiser</text>
<path d="M 590.0,145.0 L 720.0,145.0" fill="none" stroke="#ff717e" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="655.0" y="137.0" text-anchor="middle" fill="#ff717e" font-size="13" font-weight="600">escalade</text>
<path d="M 590.0,290.0 L 720.0,290.0" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="655.0" y="282.0" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">traiter</text>
<rect x="40" y="100" width="230" height="90" rx="13" fill="#42252b" stroke="#ff717e" stroke-width="2"/>
<text x="155.0" y="135.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Impact fort</text>
<text x="155.0" y="156.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">multi-clients / revenu</text>
<rect x="40" y="245" width="230" height="90" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="155.0" y="280.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Impact modéré</text>
<text x="155.0" y="301.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">contournement possible</text>
<rect x="370" y="100" width="220" height="90" rx="13" fill="#42252b" stroke="#ff717e" stroke-width="2"/>
<text x="480.0" y="135.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Urgence forte</text>
<text x="480.0" y="156.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">service critique arrêté</text>
<rect x="370" y="245" width="220" height="90" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="480.0" y="280.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Urgence basse</text>
<text x="480.0" y="301.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">impact contenu</text>
<rect x="720" y="100" width="275" height="90" rx="13" fill="#42252b" stroke="#ff717e" stroke-width="2"/>
<text x="857.5" y="135.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Priorité haute</text>
<text x="857.5" y="156.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">mobiliser / commander</text>
<rect x="720" y="245" width="275" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="857.5" y="280.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Priorité normale</text>
<text x="857.5" y="301.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">file &amp; SLA</text>
</svg>

## 4. Commandement et communication pendant un incident majeur

### 4.1 Le briefing initial (premières minutes)

Le briefing doit être court, factuel et orienté action. À la première synchronisation, l’IC devrait confirmer :

- ce qui est connu et ce qui ne l’est pas encore ;
- impact observé et estimation provisoire de l’étendue ;
- objectif immédiat (ex. arrêter la propagation, restaurer le chemin de paiement) ;
- actions en cours, leur propriétaire et leur critère de réussite ;
- prochaine mise à jour et canal faisant autorité ;
- risques de changement, de perte de données et de sécurité.

Éviter les longues discussions libres. Les enquêtes parallèles doivent avoir une hypothèse ou une question précise, une personne responsable et un délai de retour. Les nouvelles informations passent par le canal central pour éviter que plusieurs équipes exécutent simultanément des changements contradictoires.

### 4.2 Modèle de message interne initial

```text
[INCIDENT SEV-1] Paiements — dégradation régionale
Détecté à : 14:06 UTC (heure affichée explicitement)
État : en investigation ; l’impact exact est encore en cours d’évaluation
Impact connu : taux d’échec des autorisations supérieur au seuil ; portée à confirmer
Objectif immédiat : stopper la hausse des échecs et préserver l’intégrité des transactions
IC : [rôle / contact] ; lead technique : [rôle]
Actions en cours : [action — responsable — critère de réussite]
Décisions / risques : aucune suppression de données ; changements de production coordonnés par l’IC
Prochaine mise à jour : 14:25 UTC, ou plus tôt si changement matériel
Canal de référence : [lien / canal]
```

Ne pas inclure de secret, jeton, adresse personnelle, données de paiement ou détails exploitables qui n’ont pas à être largement distribués. Pour une communication publique, préciser l’impact réellement observé, éviter les causes prématurées et indiquer quand une nouvelle mise à jour est prévue.

### 4.3 Fréquence de communication et charge cognitive

Une mise à jour peut dire « l’investigation continue » à condition d’apporter une information utile : impact réévalué, test terminé, mitigation écartée, risque découvert ou prochaine décision. Il n’est pas nécessaire d’inventer un progrès à chaque cycle. Des messages cohérents, horodatés et publiés dans un canal de référence limitent les contradictions. Chaque message doit distinguer clairement : **confirmé**, **probable**, **non confirmé** et **inconnu**.

### 4.4 Journal de décision

| Heure | Décision | Alternatives considérées | Preuve / motif | Décideur | Risque accepté | Résultat observé |
|---|---|---|---|---|---|---|
| 14:12 | Limiter le trafic vers le nœud B | Redémarrage ; rollback | Erreurs concentrées sur B ; autres nœuds sains | IC + lead | Hausse de latence possible | Erreurs en baisse à 14:16 |
| 14:21 | Geler le déploiement | Poursuivre le lot | Corrélation de version à confirmer | IC | Correctifs différés | Aucun nouveau lot lancé |

Le tableau ci-dessus est un exemple pédagogique. En situation réelle, consigner les identifiants de changement et les liens vers les preuves.

## 5. Stratégie de rétablissement sous incertitude

Le but n’est pas de prouver la cause en temps réel ; il est de choisir une action réversible et sûre qui réduit l’impact tout en gardant la capacité d’enquêter.

### 5.1 Arbre de décision pratique

- **Y a-t-il un risque pour la sécurité des personnes, l’intégrité des données ou une compromission ?** Appliquer immédiatement les procédures spécialisées et obtenir l’autorité adéquate ; ne pas sacrifier les preuves à une restauration précipitée.
- **Un changement récent est-il fortement associé au début du problème ?** Envisager rollback ou désactivation d’un feature flag si le mécanisme est compris, la procédure est éprouvée et les risques de migration de données sont évalués.
- **La capacité restante permet-elle de fonctionner en mode dégradé ?** Limiter les fonctionnalités, appliquer du load shedding ou des limites de débit, avec validation métier.
- **Une dépendance est-elle indisponible ?** Réduire les retries, mettre en file les opérations si c’est sûr, activer une dépendance secondaire selon runbook, ou interrompre les actions qui aggravent la saturation.
- **La cause est-elle inconnue ?** Choisir la mitigation à plus faible risque et la plus facile à annuler ; définir une fenêtre d’observation et un indicateur de retour arrière.

### 5.2 Critères d’une mitigation sûre

Chaque action doit préciser :

- l’hypothèse qu’elle cherche à tester ou l’impact qu’elle doit réduire ;
- le périmètre exact et le blast radius potentiel ;
- le propriétaire qui exécute et celui qui approuve ;
- les préconditions et dépendances ;
- le critère de réussite mesurable ;
- le critère d’arrêt ou de rollback ;
- les effets secondaires possibles et le plan de surveillance ;
- la manière de préserver logs, snapshots ou événements requis pour la RCA.

Exemple : « retirer le nœud API-03 du load balancer » est incomplet. Une instruction experte précise le motif, l’autorité, le nombre de requêtes en cours, les contrôles de santé, la capacité restante, le seuil d’erreur attendu, la durée d’observation et les conditions de réintégration.

### 5.3 Rollback, roll-forward, failover et mode dégradé

| Option | Quand elle peut convenir | Risques à traiter |
|---|---|---|
| Rollback | Régression liée à une version ou configuration, retour arrière disponible et sûr | Migration de schéma non réversible, incompatibilité API, données déjà écrites |
| Roll-forward | Correctif ciblé bien compris, rollback plus risqué | Un deuxième changement peut étendre la panne ou masquer la preuve |
| Failover | Réplique ou site sain, procédure testée, capacité disponible | Split-brain, réplication en retard, dépendance commune, incohérence de données |
| Mode dégradé | Fonctions non essentielles peuvent être coupées sans violer les règles métier | Confusion utilisateur, files d’attente, reprise de charge brutale |
| Limitation / load shedding | Surcharge qui s’auto-amplifie ; certaines requêtes peuvent être rejetées proprement | Perte d’opérations si l’idempotence et la gestion des erreurs sont mal conçues |
| Restauration backup | Corruption ou perte de données, point de restauration adapté | RPO/RTO, opérations postérieures au backup, intégrité, tests de restauration |

Ne jamais traiter le retour d’un statut « vert » sur une seule sonde comme preuve suffisante. Valider le parcours métier, les données, les erreurs, la latence, le backlog et la stabilité sous charge réaliste.

## 6. Clôture opérationnelle et période de stabilisation

La fermeture d’un incident est une décision de gestion, pas seulement la fin d’une commande technique. Avant de le déclarer résolu, vérifier :

1. le service et les parcours critiques fonctionnent selon les critères convenus ;
2. l’impact est revenu sous les seuils acceptables sur une fenêtre d’observation spécifiée ;
3. les files et traitements différés sont récupérés ou disposent d’un plan explicite ;
4. la cohérence des données et le rapprochement des transactions sont confirmés lorsque nécessaire ;
5. les équipes et utilisateurs concernés ont reçu une information de statut ;
6. la configuration temporaire et les contournements sont documentés ;
7. un propriétaire et une échéance sont définis pour le suivi post-incident ;
8. les preuves et les journaux utiles sont conservés de manière sûre.

La durée d’observation doit correspondre au comportement du service : une simple requête de santé ne suffit pas à prouver la stabilité d’un traitement batch nocturne. Si le service est de nouveau disponible mais que des actions de suivi restent ouvertes, le dossier peut être opérationnellement résolu tout en conservant un problème relié et un plan de suivi, selon la politique interne.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 470" width="100%" role="img" aria-label="Cycle de réponse et apprentissage">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="980" height="470" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Cycle de réponse et apprentissage</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Le rétablissement est prioritaire pendant l’événement ; la RCA suit avec des preuves conservées.</text>
<path d="M 210.0,195.8 L 260.0,179.2" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="235.0" y="179.5" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">capacité</text>
<path d="M 435.0,150.0 L 500.0,150.0" fill="none" stroke="#ffbd59" stroke-width="3" marker-end="url(#arrowAmber)" class="flow-animated"/>
<text x="467.5" y="142.0" text-anchor="middle" fill="#ffbd59" font-size="13" font-weight="600">déclarer</text>
<path d="M 675.0,150.0 L 740.0,150.0" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="707.5" y="142.0" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">mitigation</text>
<path d="M 827.5,195.0 L 827.5,310.0" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="827.5" y="244.5" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">après stabilité</text>
<path d="M 740.0,355.0 L 675.0,355.0" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="707.5" y="347.0" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">prioriser</text>
<path d="M 500.0,355.0 L 435.0,355.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="467.5" y="347.0" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">livrer</text>
<path d="M 269.6,310.0 Q 240.8,279.9 200.4,270.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="240.8" y="272.9" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">amélioration</text>
<rect x="35" y="180" width="175" height="90" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="122.5" y="215.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Préparer</text>
<text x="122.5" y="236.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">rôles, runbooks</text>
<rect x="260" y="105" width="175" height="90" rx="13" fill="#1b2844" stroke="#48b9ff" stroke-width="2"/>
<text x="347.5" y="140.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Détecter &amp;</text>
<text x="347.5" y="161.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">qualifier</text>
<rect x="500" y="105" width="175" height="90" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="587.5" y="140.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Répondre</text>
<text x="587.5" y="161.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">commander, agir</text>
<rect x="740" y="105" width="175" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="827.5" y="140.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Rétablir</text>
<text x="827.5" y="161.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">valider le service</text>
<rect x="740" y="310" width="175" height="90" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="827.5" y="345.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Revue / RCA</text>
<text x="827.5" y="366.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">faits &amp; facteurs</text>
<rect x="500" y="310" width="175" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="587.5" y="345.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Actions suivies</text>
<text x="587.5" y="366.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">prévenir, détecter</text>
<rect x="260" y="310" width="175" height="90" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="347.5" y="345.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Vérifier</text>
<text x="347.5" y="366.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">efficacité mesurée</text>
</svg>

## 7. Construire une chronologie fiable

Une chronologie est une série d’événements horodatés, liée à des sources. Elle ne doit pas être un récit reconstruit de mémoire sans distinguer ce qui est certain.

### 7.1 Champs d’une entrée

| Champ | Pourquoi il existe |
|---|---|
| Heure avec fuseau | Évite les ambiguïtés entre UTC, heures locales et fuseaux des journaux |
| Événement observé | Mesure, alerte, requête échouée, déploiement ou action confirmée |
| Source | ID d’alerte, log, ticket, trace, message, audit de changement |
| Statut de preuve | Confirmé, déduit, rapporté, estimé ou inconnu |
| Acteur / système | Équipe ou composant responsable de l’événement, pas forcément fautif |
| Confiance | Élevée, moyenne, faible, accompagnée de la raison |

### 7.2 Synchronisation des horloges et précision trompeuse

Les systèmes peuvent utiliser des horloges décalées, des collecteurs qui tamponnent les logs ou des interfaces affichant une heure locale. Conserver l’horodatage brut et la source, noter la correction appliquée et ne pas fabriquer de précision. Lors de la corrélation de plusieurs sources, vérifier les décalages NTP/PTP, la latence d’ingestion et le format du fuseau. Une séquence « A avant B » n’est fiable que si l’incertitude temporelle est suffisamment petite pour établir cet ordre.

### 7.3 Modèle de chronologie

```text
| Heure UTC | Type | Événement | Source / lien | Confiance | Note / conséquence |
|-----------|------|-----------|---------------|-----------|--------------------|
| 14:06:12  | Signal | Taux 5xx dépasse 8 % | Alert API-184 | élevée | Début détecté ; heure réelle possible antérieure |
| 14:08:30  | Contexte | Version v2026.10.22.3 déployée sur 20 % des nœuds | audit CI/CD | élevée | Corrélation temporelle, causalité non confirmée |
| 14:12:00  | Décision | Déploiement suspendu | journal IC | élevée | Aucun nouveau lot |
| 14:18:44  | Test | Retrait du nœud canari réduit les erreurs | métrique LB | moyenne | Contrôle complémentaire requis |
```

## 8. RCA avancée : du symptôme au mécanisme causal

La RCA (Root Cause Analysis) est un ensemble de méthodes d’enquête. La technique doit être choisie selon la nature de l’événement. Un diagramme des 5 pourquoi peut suffire à une panne simple ; une défaillance multi-service peut demander une chronologie distribuée, un arbre de défaillance, un graphe causal, l’analyse de changement et une revue des contrôles. Une causalité forte demande plus qu’une succession temporelle.

### 8.1 La qualité d’une affirmation causale

Pour chaque affirmation, demander :

- Quelle observation la soutient ?
- Quelle autre explication est compatible avec les mêmes données ?
- Quelle prédiction devrait être vraie si l’hypothèse est correcte ?
- Quel test pourrait la réfuter ?
- La relation causale est-elle directe, contributive ou simplement corrélée ?
- Quelle intervention aurait évité l’impact, ou au moins réduit sa durée ou son étendue ?

### 8.2 Les 5 pourquoi : utiles mais limités

Les « 5 pourquoi » aident à remonter de l’effet vers des conditions plus profondes, mais le nombre cinq n’est pas une règle scientifique. Éviter de s’arrêter à une explication humaine telle que « quelqu’un a oublié », « l’ingénieur n’a pas vérifié » ou « l’opérateur a mal cliqué ». Ces formulations n’expliquent pas pourquoi le système permettait cette action, pourquoi le contrôle a échoué ou pourquoi la récupération était difficile.

Exemple de chaîne plus utile :

1. Pourquoi les paiements ont-ils échoué ? Le service d’autorisation n’obtenait plus de connexions à la base.
2. Pourquoi le pool était-il épuisé ? Les requêtes lentes retenaient les connexions et les retries augmentaient le nombre de demandes.
3. Pourquoi la charge s’est-elle auto-amplifiée ? Les retries étaient synchronisés et n’avaient pas de budget global.
4. Pourquoi le comportement n’a-t-il pas été détecté plus tôt ? Les alertes suivaient surtout CPU et disponibilité de l’instance, pas l’attente du pool ni la proportion de retries.
5. Pourquoi ces contrôles étaient-ils absents ? Les critères de mise en production ne définissaient pas d’enveloppe de charge, de SLO ni de signaux de saturation du pool.

Cela produit plusieurs actions possibles : capacité et timeouts, budgets de retry avec backoff/jitter, métriques de pool, tests de charge et critères de lancement. Il reste à confirmer les relations avec les traces et métriques de l’incident réel.

### 8.3 Diagramme d’Ishikawa et familles de facteurs

Pour éviter une enquête trop centrée sur le code, examiner : **architecture**, **logiciel**, **configuration**, **données**, **dépendances**, **capacité**, **observabilité**, **processus de changement**, **compétences et organisation**, **fournisseur**, **charge métier**. Ce sont des catégories d’exploration, pas des conclusions. Ne cochez pas toutes les catégories par principe ; documentez celles qui ont une preuve ou une hypothèse testable.

### 8.4 Arbre de défaillance et analyse de barrières

Un arbre de défaillance part de l’événement indésirable et décompose les conditions selon des relations logiques. Une porte **ET** indique que plusieurs conditions sont requises ensemble ; une porte **OU** signifie qu’une seule branche peut déclencher l’événement. Éviter de traiter ces symboles comme une quantification probabiliste en l’absence de données. Une analyse de barrières se demande quelles protections auraient pu prévenir l’événement, empêcher sa propagation, le détecter, ou permettre la récupération.

### 8.5 Graphes causaux et interventions

Un graphe causal explicite les relations proposées : « retries sans backoff → charge amplifiée → pool saturé → taux d’erreur → files en croissance ». Les flèches représentent des hypothèses à confirmer, non une vérité automatique. Le test le plus utile ne se limite pas à voir si deux métriques montent ensemble ; il examine si la relation prédit le comportement et si une intervention contrôlée modifie le résultat. En production, les interventions doivent être autorisées et sûres ; les expériences risquées se font en environnement de test ou en exercice.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 480" width="100%" role="img" aria-label="Construire une chaîne causale défendable">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="1100" height="480" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Construire une chaîne causale défendable</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Une RCA utile relie conditions, mécanisme, impact et contrôles manquants sans réduire l’analyse à une personne.</text>
<path d="M 240.0,168.0 L 310.0,168.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="275.0" y="160.0" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">permet</text>
<path d="M 515.0,168.0 L 585.0,168.0" fill="none" stroke="#ffbd59" stroke-width="3" marker-end="url(#arrowAmber)" class="flow-animated"/>
<text x="550.0" y="160.0" text-anchor="middle" fill="#ffbd59" font-size="13" font-weight="600">active</text>
<path d="M 790.0,168.0 L 860.0,168.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="825.0" y="160.0" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">produit</text>
<path d="M 471.6,325.0 Q 560.8,282.9 628.4,211.0" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="560.8" y="275.9" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">n’empêche pas</text>
<path d="M 746.6,325.0 Q 814.2,253.2 903.4,211.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="814.2" y="246.2" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">retarde la réponse</text>
<rect x="35" y="125" width="205" height="86" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="137.5" y="158.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Conditions latentes</text>
<text x="137.5" y="179.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">charge, dette, dépendance</text>
<rect x="310" y="125" width="205" height="86" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="412.5" y="158.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Déclencheur</text>
<text x="412.5" y="179.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">changement ou pic</text>
<rect x="585" y="125" width="205" height="86" rx="13" fill="#1b2844" stroke="#48b9ff" stroke-width="2"/>
<text x="687.5" y="158.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Mécanisme de défaillance</text>
<text x="687.5" y="179.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">pool saturé</text>
<rect x="860" y="125" width="205" height="86" rx="13" fill="#42252b" stroke="#ff717e" stroke-width="2"/>
<text x="962.5" y="158.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Impact observé</text>
<text x="962.5" y="179.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">transactions en échec</text>
<rect x="310" y="325" width="205" height="86" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="412.5" y="358.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Contrôle absent/faible</text>
<text x="412.5" y="379.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">garde-fou / limite</text>
<rect x="585" y="325" width="205" height="86" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="687.5" y="358.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Détection tardive</text>
<text x="687.5" y="379.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">alerte orientée infra</text>
</svg>

### 8.6 Hypothèses concurrentes, réfutation et niveaux de confiance

Ne choisissez pas la première explication plausible. Créez une liste de deux à cinq hypothèses significatives, surtout lorsque les données sont incomplètes. Pour chacune, noter : éléments favorables, éléments contradictoires, données manquantes, test discriminant, risque de test, responsable et résultat. Une hypothèse devrait pouvoir être rejetée.

| Hypothèse | Prédiction si vraie | Test prudent | Critère de réfutation |
|---|---|---|---|
| Régression de version | Erreurs concentrées sur les instances de la nouvelle version | Comparer canari et ancienne version avec même charge | Ancienne version montre le même taux d’erreur et le même mécanisme |
| Saturation d’une dépendance | Latence et erreurs augmentent en aval avant l’erreur API | Corréler traces, pool et métriques DB | Dépendance reste saine pendant l’impact et ne montre pas de contention pertinente |
| Épuisement de capacité | Attente ou saturation s’aligne avec charge et limite configurée | Examiner taux d’occupation, files et historique de capacité | Ressources restent sous les limites et aucun signal d’attente n’est présent |

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 400" width="100%" role="img" aria-label="Gérer les hypothèses avec niveau de preuve">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="1100" height="400" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Gérer les hypothèses avec niveau de preuve</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Ne pas confondre corrélation temporelle, hypothèse plausible et cause confirmée.</text>
<path d="M 225.0,161.9 L 300.0,145.3" fill="none" stroke="#ffbd59" stroke-width="3" marker-end="url(#arrowAmber)" class="flow-animated"/>
<text x="262.5" y="145.6" text-anchor="middle" fill="#ffbd59" font-size="13" font-weight="600">à examiner</text>
<path d="M 225.0,213.3 L 300.0,238.3" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="262.5" y="217.8" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">à examiner</text>
<path d="M 505.0,143.9 Q 545.3,163.1 590.0,161.6" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="545.3" y="156.1" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">prédiction testable</text>
<path d="M 505.0,240.4 Q 544.3,216.8 590.0,213.8" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="544.3" y="209.8" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">prédiction testable</text>
<path d="M 790.0,182.5 L 880.0,182.5" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="835.0" y="174.5" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">preuve</text>
<rect x="40" y="140" width="185" height="85" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="132.5" y="172.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Signal</text>
<text x="132.5" y="193.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">erreur 5xx ↑</text>
<rect x="300" y="80" width="205" height="85" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="402.5" y="112.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Hypothèse A</text>
<text x="402.5" y="133.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">release récente</text>
<rect x="300" y="230" width="205" height="85" rx="13" fill="#1b2844" stroke="#48b9ff" stroke-width="2"/>
<text x="402.5" y="262.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Hypothèse B</text>
<text x="402.5" y="283.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">dépendance DB</text>
<rect x="590" y="140" width="200" height="85" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="690.0" y="172.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Test discriminant</text>
<text x="690.0" y="193.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">logs, métriques, diff</text>
<rect x="880" y="140" width="190" height="85" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="975.0" y="172.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Résultat</text>
<text x="975.0" y="193.5" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">confirmé / rejeté</text>
</svg>

### 8.7 Causes multiples et facteur déterminant

Dans un système complexe, il est souvent trompeur de dire « la cause racine est X » au singulier. Documenter :

- **cause directe ou mécanisme proche** qui a déclenché l’impact ;
- **conditions contributives** qui ont accru sa probabilité ou son ampleur ;
- **défaillance de contrôle** qui a laissé la panne passer ou se propager ;
- **défaut de détection ou de récupération** qui a prolongé l’impact ;
- **facteur d’échappement** qui explique pourquoi les contrôles habituels n’ont pas bloqué la mise en production.

Une conclusion doit indiquer ce qui est confirmé, ce qui reste incertain et les limites des preuves. Un champ « cause inconnue » accompagné d’un plan d’amélioration de l’observabilité est préférable à une certitude inventée.

## 9. RCA sans blâme, sans complaisance

« Sans blâme » ne signifie pas « sans responsabilité ». Cela signifie que l’enquête cherche à comprendre les conditions de travail, les informations disponibles et la conception du système, plutôt que de conclure au défaut moral d’une personne. La responsabilité opérationnelle existe : les décisions, contrôles et engagements doivent être améliorés, attribués et vérifiés. Les politiques de conduite ou de sécurité éventuellement applicables suivent une voie de gouvernance distincte et ne doivent pas polluer l’analyse technique.

Questions utiles :

- Qu’est-ce que l’opérateur pensait se passer au moment de la décision ?
- Quelles informations et quelles options étaient disponibles à cet instant ?
- Le runbook était-il exact, accessible et testé ?
- Les signaux ont-ils différencié une panne réelle d’un bruit courant ?
- Les systèmes rendaient-ils l’action sûre et facile, ou l’erreur probable ?
- Le mécanisme de validation était-il adapté au risque ?
- Une autre équipe raisonnable, avec les mêmes informations et pressions, aurait-elle fait un choix différent ?

Éviter les expressions « erreur humaine » comme conclusion finale. Il est possible de consigner qu’une commande incorrecte a été exécutée ; l’analyse ne s’arrête pas là. Explorer la validation, les permissions, la visibilité de l’environnement cible, l’ergonomie, les revues, la possibilité de simulation et le garde-fou qui aurait empêché un périmètre involontaire.

## 10. Incident IT, incident cyber et préservation des preuves

Un incident de service peut recouvrir une suspicion cyber : comptes privilégiés anormaux, mouvement latéral, exfiltration, altération de données, activité inconnue ou journaux supprimés. Dans ce cas, les équipes IT et sécurité coordonnent la disponibilité et la préservation des preuves. L’objectif de restauration immédiate ne doit pas détruire les journaux, écraser un système potentiellement compromis ou prévenir prématurément un attaquant d’une investigation.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 420" width="100%" role="img" aria-label="Réponse IT vs réponse cyber : recouvrement et priorité de preuve">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="1120" height="420" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Réponse IT vs réponse cyber : recouvrement et priorité de preuve</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Si compromission plausible, coordonner Service Management et équipe sécurité ; préserver les éléments probants.</text>
<path d="M 225.0,205.0 L 300.0,205.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="262.5" y="197.0" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">qualifier</text>
<path d="M 505.0,185.0 Q 549.3,159.1 600.0,166.5" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="549.3" y="152.1" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">impact service</text>
<path d="M 505.0,235.0 Q 547.6,265.5 600.0,262.8" fill="none" stroke="#ff717e" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="547.6" y="258.5" text-anchor="middle" fill="#ff717e" font-size="13" font-weight="600">suspicion cyber</text>
<path d="M 820.0,168.6 Q 863.2,162.0 900.0,185.7" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="863.2" y="155.0" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">arbitrer</text>
<path d="M 820.0,259.6 Q 864.9,261.9 900.0,233.9" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="864.9" y="254.9" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">gouverner</text>
<rect x="35" y="160" width="190" height="90" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="130.0" y="195.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Alerte / impact</text>
<text x="130.0" y="216.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">service dégradé</text>
<rect x="300" y="160" width="205" height="90" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="402.5" y="195.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Triage commun</text>
<text x="402.5" y="216.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">IT + sécurité</text>
<rect x="600" y="100" width="220" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="710.0" y="135.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Voie disponibilité</text>
<text x="710.0" y="156.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">restaurer en sécurité</text>
<rect x="600" y="250" width="220" height="90" rx="13" fill="#42252b" stroke="#ff717e" stroke-width="2"/>
<text x="710.0" y="285.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Voie cyber</text>
<text x="710.0" y="306.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">contenir &amp; préserver</text>
<rect x="900" y="160" width="180" height="90" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="990.0" y="195.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Décisions coordonnées</text>
<text x="990.0" y="216.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">preuve + service</text>
</svg>

### 10.1 Garde-fous spécifiques

- Suivre le plan de réponse à incident de sécurité et les autorités désignées.
- Préserver les journaux originaux, horodatages, images et métadonnées selon les procédures internes.
- Limiter l’accès et documenter qui a collecté, copié, transféré ou examiné une preuve.
- Préserver l’intégrité des fichiers (par exemple empreintes cryptographiques) lorsque le protocole de collecte l’exige.
- Éviter les commandes « nettoyage », réinstallation ou rotation qui supprimeraient les traces avant validation.
- Ne pas recueillir ni partager des secrets ou données personnelles sans nécessité et autorisation.
- Laisser la sécurité, le juridique et la conformité déterminer les exigences de notification applicables à la juridiction et au contrat concernés.

Cette section n’est pas un avis juridique. Les délais de déclaration, critères de violation de données et exigences de conservation dépendent du contexte réglementaire et contractuel.

## 11. Problèmes, erreurs connues et dette opérationnelle

Après la stabilisation, relier l’incident à un enregistrement de problème lorsqu’un mécanisme est inconnu, récurrent ou suffisamment risqué. Le Problem Manager ou le propriétaire de service décide comment regrouper les incidents, créer une erreur connue et publier une solution de contournement. Les contournements doivent présenter leurs limites et les risques acceptés, et ne deviennent pas une excuse pour reporter indéfiniment une correction.

**Critères pour ouvrir ou prioriser un problème :** récurrence, impact élevé, cause incertaine, risque de perte d’intégrité, vulnérabilité, contournement fragile, coût opérationnel récurrent ou forte probabilité de récidive. Une seule occurrence peut justifier un problème si son impact potentiel est important.

### 11.1 Relier les enregistrements

Un incident peut se relier à un problème, une change request, une release, un défaut logiciel, un fournisseur et plusieurs actions correctives. Garder des identifiants distincts et des relations explicites ; ne pas dupliquer la même vérité dans plusieurs tickets contradictoires. L’incident décrit l’événement et son traitement, le problème la compréhension et la réduction du risque, le changement l’action autorisée, et les items de travail suivent la livraison des mesures.

## 12. Post-incident review (PIR) : format de niveau expert

La revue doit se tenir assez tôt pour exploiter les faits, mais après que l’équipe a retrouvé une capacité d’analyse raisonnable. Le calendrier exact dépend de la criticité et des règles internes. Pour un incident majeur, préparer la revue dès le rétablissement, désigner un owner et définir l’échéance. Une réunion n’est pas obligatoire pour chaque incident ; le seuil doit être explicite.

### 12.1 Agenda suggéré (60–90 minutes)

1. **Cadre et sécurité psychologique (5 min) :** objectifs, périmètre, rappel sans blâme.
2. **Impact métier (10 min) :** utilisateurs, transactions, durée, conséquences et incertitudes.
3. **Chronologie (15 min) :** événements et sources, sans interprétation prématurée.
4. **Mécanisme causal (20 min) :** hypothèses confirmées/rejetées, facteurs et contrôles.
5. **Réponse opérationnelle (10 min) :** détection, décision, communication, restauration.
6. **Actions (15 min) :** prévention, détection, mitigation, résilience et apprentissage.
7. **Lecture finale (5 min) :** propriétaire de rapport, actions et date de validation.

### 12.2 Rapport post-incident : modèle complet

```markdown
# PIR — [ID incident] — [Service] — [Date]

## Résumé exécutif
- Service et capacité touchés :
- Période d’impact (avec fuseau) :
- Impact utilisateur/métier confirmé :
- Sévérité maximale et raison :
- État actuel / risques résiduels :

## Détection et portée
- Heure de début estimée :
- Heure de détection :
- Méthode de détection :
- Étendue confirmée / inconnue :
- Données ou transactions affectées :

## Chronologie sourcée
| Heure | Fait/action/décision | Source | Confiance |
|---|---|---|---|

## Mécanismes et causes
- Mécanisme direct :
- Conditions contributives :
- Contrôles absents ou inefficaces :
- Facteurs ayant prolongé l’impact :
- Hypothèses rejetées et pourquoi :
- Incertitudes restantes :

## Réponse
- Ce qui a réduit l’impact :
- Ce qui a aggravé ou prolongé l’incident :
- Les signaux qui ont aidé :
- Les signaux manquants :
- Décisions et risques acceptés :

## Actions
| ID | Catégorie | Résultat vérifiable | Responsable | Échéance | Priorité | Critère d’acceptation | Preuve |
|---|---|---|---|---|---|---|---|

## Validation et gouvernance
- Owner de la PIR :
- Relecteurs :
- Actions à risque élevé approuvées par :
- Date de publication / restrictions :
- Date de revue d’efficacité :
```

Ne pas publier de détails sensibles, données clients, secrets, vulnérabilités exploitables ou identifiants d’infrastructure sans revue d’accès et de sécurité.

## 13. Transformer les conclusions en actions qui réduisent le risque

Une action est faible si elle promet seulement « sensibiliser l’équipe », « faire plus attention » ou « améliorer la supervision ». Elle devient opérationnelle quand elle décrit un changement de système, une personne responsable, une échéance et une preuve observable.

### 13.1 Catégories d’actions

- **Préventive :** empêche le mécanisme ou réduit sa probabilité (validation de configuration, limite de débit, test, isolation).
- **Détective :** réduit le délai d’identification (mesure utilisateur, alerte sur saturation, synthèse des erreurs).
- **Atténuante :** réduit le blast radius ou rend le mode dégradé sûr (circuit breaker, canary, feature flag, failover testée).
- **Récupération :** réduit le temps de retour et le risque sur les données (restore testé, runbook, rapprochement des transactions).
- **Apprentissage :** améliore l’exactitude des investigations et du partage de connaissances.

Une RCA robuste comporte souvent un mélange, au lieu de s’appuyer uniquement sur la prévention. Toute prévention peut échouer un jour ; la détection, l’isolation et la récupération limitent alors les conséquences.

### 13.2 Qualité d’une action SMART

Une action doit être spécifique, mesurable, attribuée, réaliste et datée. Ajouter un **critère d’acceptation**, une **preuve de livraison**, un **test d’efficacité** et un **propriétaire du risque résiduel**. Le responsable est une personne nommée, pas seulement une équipe générique. Les actions dépendantes doivent expliciter leur ordre et leur blocage.

| Mauvaise formulation | Reformulation opérationnelle |
|---|---|
| Améliorer les alertes | Ajouter une alerte sur l’attente du pool avec seuil fondé sur le SLO, vérifier le déclenchement lors d’un test de saturation et l’acheminement à l’astreinte avant la date convenue |
| Faire un test de charge | Définir le profil de charge attendu et les scénarios de pics, automatiser un test de 30 minutes au niveau de trafic prévu, publier les limites et faire bloquer le déploiement si le seuil d’erreur est dépassé |
| Mieux documenter | Créer un runbook versionné, assigner un owner, simuler le scénario, obtenir un opérateur non auteur qui réalise la procédure et corriger les étapes ambiguës |
| Éviter les erreurs humaines | Ajouter une validation de cible et une prévisualisation, interdire le changement global sans approbation, tester qu’une mauvaise cible est rejetée |

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 390" width="100%" role="img" aria-label="Cycle de vie des actions post-incident">
<defs><marker id="arrowBlue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48b9ff"/></marker><marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#48d597"/></marker><marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#ffbd59"/></marker></defs>
<rect x="0" y="0" width="1080" height="390" rx="20" fill="#090e17"/>
<text x="36" y="44" fill="#f4f8ff" font-size="25" font-weight="700">Cycle de vie des actions post-incident</text>
<text x="36" y="70" fill="#a8b9ce" font-size="15">Chaque action a un propriétaire, une échéance, un critère d’acceptation et une preuve de clôture.</text>
<path d="M 210.0,185.0 L 275.0,185.0" fill="none" stroke="#bba6ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="242.5" y="177.0" text-anchor="middle" fill="#bba6ff" font-size="13" font-weight="600">produire</text>
<path d="M 465.0,170.4 L 535.0,159.6" fill="none" stroke="#48d597" stroke-width="3" marker-end="url(#arrowGreen)" class="flow-animated"/>
<text x="500.0" y="157.0" text-anchor="middle" fill="#48d597" font-size="13" font-weight="600">assigner</text>
<path d="M 465.0,216.1 L 535.0,238.9" fill="none" stroke="#ffbd59" stroke-width="3" marker-end="url(#arrowAmber)" class="flow-animated"/>
<text x="500.0" y="219.5" text-anchor="middle" fill="#ffbd59" font-size="13" font-weight="600">planifier</text>
<path d="M 725.0,158.6 Q 764.7,148.8 800.0,169.3" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="764.7" y="141.8" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">livrer</text>
<path d="M 725.0,241.2 Q 767.1,244.9 800.0,218.4" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="767.1" y="237.9" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">prouver</text>
<path d="M 800.0,185.0 Q 505.0,142.5 210.0,185.0" fill="none" stroke="#48b9ff" stroke-width="3" marker-end="url(#arrowBlue)" class="flow-animated"/>
<text x="505.0" y="135.5" text-anchor="middle" fill="#48b9ff" font-size="13" font-weight="600">réviser si échec</text>
<rect x="35" y="140" width="175" height="90" rx="13" fill="#29233d" stroke="#bba6ff" stroke-width="2"/>
<text x="122.5" y="175.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Cause / risque</text>
<text x="122.5" y="196.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">documenté</text>
<rect x="275" y="140" width="190" height="90" rx="13" fill="#182b40" stroke="#48b9ff" stroke-width="2"/>
<text x="370.0" y="175.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Action SMART</text>
<text x="370.0" y="196.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">résultat vérifiable</text>
<rect x="535" y="100" width="190" height="90" rx="13" fill="#17372f" stroke="#48d597" stroke-width="2"/>
<text x="630.0" y="135.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Responsable</text>
<text x="630.0" y="156.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">une personne</text>
<rect x="535" y="225" width="190" height="90" rx="13" fill="#3d2d1b" stroke="#ffbd59" stroke-width="2"/>
<text x="630.0" y="260.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Échéance &amp; priorité</text>
<text x="630.0" y="281.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">risque / effort</text>
<rect x="800" y="140" width="220" height="90" rx="13" fill="#1b2844" stroke="#48b9ff" stroke-width="2"/>
<text x="910.0" y="175.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">Validation indépendante</text>
<text x="910.0" y="196.0" text-anchor="middle" dominant-baseline="middle" fill="#f4f8ff" font-size="15" font-weight="600">test / métrique</text>
</svg>

### 13.3 Priorisation des actions

Prioriser selon la baisse du risque attendu, le nombre de services protégés, le délai de livraison, la complexité, les dépendances et le risque introduit par le correctif. Les actions qui réduisent plusieurs modes de défaillance et le blast radius sont souvent plus fortes qu’une réparation étroite. Un exercice peut évaluer grossièrement le risque comme : **Risque = probabilité × impact**, mais ne pas attribuer de chiffres faussement précis sans données. Documenter les hypothèses et revoir le classement lorsqu’elles changent.

Ne pas fermer une action sur le seul statut « code fusionné ». La preuve de complétion peut être un déploiement, un test exécuté, une procédure simulée, une alerte reçue par l’astreinte ou une métrique observée en période réelle. Pour un contrôle de sécurité, exiger la validation appropriée.

## 14. Métriques : vitesse, qualité et effets indésirables

Les métriques aident à identifier les goulots d’étranglement, mais elles peuvent produire de mauvais comportements si elles sont utilisées comme objectifs isolés. Mesurer l’ensemble du parcours et segmenter par service, sévérité, heures d’astreinte, source de détection et famille causale.

### 14.1 Définitions à standardiser

- **MTTD (Mean Time to Detect)** : durée entre le début estimé de l’impact et sa détection. La qualité de l’heure de début est souvent incertaine.
- **MTTA (Mean Time to Acknowledge)** : délai entre l’alerte et sa prise en charge explicite.
- **Time to Mitigate** : délai jusqu’à une mesure qui réduit significativement l’impact, sans supposer que la résolution durable est terminée.
- **Time to Restore / MTTR** : terme ambigu. MTTR peut signifier repair, recovery, resolution ou restore time selon l’organisation. Définir précisément le début, la fin, le traitement des incidents récurrents et la méthode d’agrégation.
- **Temps de communication initiale** : délai jusqu’au premier message fiable aux parties prenantes concernées.
- **Taux de récidive** : incidents qui partagent un mécanisme causal sur une période définie, plutôt que simplement le même libellé.
- **Âge et taux de réalisation des actions** : mesure du suivi ; segmenter les retards critiques et les actions reportées.
- **Taux de détection externe** : part des incidents importants détectés d’abord par les utilisateurs ou clients.
- **Efficacité des exercices** : proportion de scénarios où l’équipe atteint les objectifs sans contournement dangereux.

### 14.2 Moyenne et percentiles

La moyenne peut masquer une longue traîne. Rapporter médiane et percentiles (p90/p95) lorsque le volume le permet, en précisant la période et le nombre d’événements. Un seul incident critique peut être plus important que des dizaines de tickets mineurs : ne pas agréger toutes les sévérités en un chiffre qui détruit le contexte.

### 14.3 Anti-patterns de métriques

- Récompenser un faible nombre de tickets peut pousser à ne pas déclarer les incidents.
- Viser un MTTR unique peut favoriser des fermetures prématurées ou la dissimulation des risques résiduels.
- Mesurer les heures de travail d’une équipe n’indique pas directement la fiabilité.
- Compter le nombre d’actions clôturées sans vérifier leur efficacité récompense les actions faciles.
- Classer les équipes selon la fréquence brute d’incidents pénalise parfois celles qui sont les plus transparentes.

Le tableau de bord doit servir à investir dans les contrôles, la capacité et la récupération, et non à faire porter la responsabilité individuelle des événements complexes.

## 15. Dépendances, fournisseurs et incidents à propagation multiple

Dans une architecture de services, un incident visible peut provenir d’une dépendance indirecte. Construire une carte des dépendances critiques incluant les chemins synchrones, les files, la résolution DNS, l’identité, les certificats, les quotas et les systèmes tiers. Une dépendance « disponible » peut rester la cause d’une dégradation si sa latence, son taux d’erreur ou sa capacité restent dans les limites nominales du fournisseur mais incompatibles avec le contrat du service appelant.

### 15.1 Questions à poser

- Quel composant a commencé à se dégrader en premier selon les horloges vérifiées ?
- Les erreurs se propagent-elles en cascade ou les services échouent-ils indépendamment ?
- Les retries, timeouts et files amplifient-ils la charge ?
- Existe-t-il un domaine de panne commun (DNS, identité, région, fournisseur) ?
- Les mécanismes de dégradation et de reprise sont-ils testés sous charge ?
- Le service dépendant a-t-il un SLO compatible avec l’objectif de son consommateur ?
- Qui possède les actions de part et d’autre du contrat fournisseur ?

### 15.2 Revue fournisseur

Demander des faits vérifiables : chronologie avec fuseau, régions et composants affectés, indicateurs d’impact, mitigation, mécanisme causal confirmé ou inconnu, limites de l’enquête, actions préventives et calendrier. Ne pas accepter un rapport qui dit seulement « incident réseau temporaire ». Comparer la preuve du fournisseur à ses engagements et aux observations locales, en gardant la possibilité que les deux systèmes aient contribué au résultat.

## 16. Risque, conformité et continuité d’activité

Les objectifs de continuité et de gestion d’incident doivent être cohérents :

- **RTO (Recovery Time Objective)** : délai cible de rétablissement d’une fonction après interruption ; il n’est pas automatiquement le délai de résolution de l’incident.
- **RPO (Recovery Point Objective)** : perte de données maximale tolérable exprimée comme point dans le temps.
- **SLO** : cible de fiabilité mesurée d’un service sur une fenêtre et une population définies.
- **SLA** : engagement de service, souvent contractuel, avec périmètre et conséquences spécifiques.
- **Error budget** : tolérance de non-fiabilité dérivée d’un SLO, lorsque cette approche est utilisée.

Un incident qui reste dans le RTO peut tout de même violer un SLA ou présenter une intégrité de données inacceptable. Un service techniquement disponible peut être incorrect du point de vue métier. Les décisions de continuité doivent tenir compte de la cohérence des données, des dépendances, des scénarios de reprise et du risque d’un basculement précipité.

Prévoir des exercices de restauration avec preuve d’intégrité, et non uniquement une documentation confirmant que les sauvegardes ont réussi. Vérifier les identifiants, clés, certificats, DNS, routage et accès nécessaires à la récupération. L’environnement de reprise ne doit pas dépendre exclusivement du plan de gestion qui vient de tomber.

## 17. Automatisation et outillage : aider sans masquer le jugement

L’automatisation peut corréler alertes, ouvrir l’incident, enrichir les services impactés, notifier l’astreinte, collecter des snapshots et créer une chronologie initiale. Elle peut aussi amplifier une panne si un automate lance des retries, redémarre simultanément toutes les instances ou déclenche un failover sur un signal bruité.

### 17.1 Principes de conception

- **Idempotence :** rejouer une action sans répéter un effet dangereux.
- **Limites et budgets :** empêcher les boucles d’escalade, les retries synchronisés et les cascades.
- **Périmètre explicite :** cible, région, version et environnement sont affichés et vérifiés avant exécution.
- **Circuit de validation :** approbation humaine selon l’impact potentiel, la réversibilité et la politique de sécurité.
- **Arrêt d’urgence :** mécanisme de désactivation testé et accessible.
- **Auditabilité :** entrées, versions, décisions, sorties et identité de l’exécutant sont conservées.
- **Observabilité :** l’automate émet des métriques, signale ses échecs et possède un owner.
- **Mode simulation :** quand c’est possible, afficher les changements prévus avant de les appliquer.

### 17.2 Runbook ou playbook ?

Un runbook décrit une procédure reproductible pour un événement connu ; un playbook coordonne plusieurs activités et décisions dans un scénario plus large. Tous deux doivent mentionner les prérequis, les commandes ou actions autorisées, les vérifications, l’interprétation des résultats, les étapes d’arrêt et l’escalade. Un document jamais testé est un risque, pas une garantie.

## 18. Exercices sur table et simulation technique

Un exercice valide le système humain autant que les outils. Ajouter progressivement des injects : alerte initiale imprécise, indisponibilité du canal de chat, contradiction entre dashboards, absence du propriétaire, risque de perte de données, fournisseur silencieux, ou action de rollback qui échoue.

### 18.1 Scénario de table (45–60 minutes)

**Situation :** le service de facturation répond lentement, les autorisations s’accumulent et des clients signalent des doublons. Une livraison a eu lieu 20 minutes auparavant. Les métriques CPU restent normales.

Questions à traiter :

1. Quelle est la sévérité provisoire et quels faits manquent ?
2. Qui devient IC et qui tient le journal de décision ?
3. Comment évaluer si les doublons sont de simples reprises d’affichage ou des transactions réelles ?
4. Quelle mitigation peut réduire la charge sans perdre les requêtes ?
5. Quelles preuves conserver avant une restauration ?
6. Quels messages peuvent être envoyés sans spéculer sur la cause ?
7. Quand baisse-t-on la sévérité et quand ferme-t-on l’incident ?
8. Quelles hypothèses RCA distinguent une régression logicielle d’un problème de verrouillage de base ?
9. Qui vérifie la récupération du backlog et le rapprochement financier ?

**Critères de réussite :** rôles attribués, décision horodatée, impact métier évalué, plan de protection de l’intégrité, mise à jour communiquée, hypothèses explicitement testables, clôture basée sur la preuve.

### 18.2 Critères pour évaluer l’exercice

Noter de 0 à 2 chaque item : 0 = absent ou dangereux ; 1 = partiel ; 2 = explicite et testé. Les critères comprennent activation de la réponse, qualité du commandement, hypothèses, gestion du risque, communication, précision de la chronologie, récupération, sécurité des preuves et suivi des actions. Utiliser les écarts pour améliorer les runbooks, rôles et systèmes, pas pour classer les personnes.

## 19. Étude de cas complète — API de paiement en saturation

> **Cas fictif pour apprentissage.** Les horaires, mesures et composants qui suivent sont inventés pour illustrer une analyse ; ils ne décrivent pas un incident réel.

### 19.1 Situation

À 14:06 UTC, la plateforme de paiement constate une hausse des réponses 5xx de 0,4 % à 11 %. La latence p95 passe de 280 ms à 4,8 s. Environ 35 % des demandes d’autorisation échouent ou expirent ; les clients voient des délais et le système de retry peut créer un risque de double soumission si l’idempotence est mal appliquée. Un déploiement d’une nouvelle version a commencé à 13:47 UTC sur 20 % des instances. La base de données semble globalement disponible, mais l’attente du pool n’est pas initialement visible dans le tableau de bord principal.

### 19.2 Réponse opérationnelle

- **14:08** — L’alerte est triée, l’impact métier est confirmé par l’équipe paiements. Sévérité élevée déclarée par précaution.
- **14:10** — IC nommé ; lead technique, communication et scribe attribués. Une seule source de statut est désignée.
- **14:13** — Le déploiement est suspendu. Le rollback est étudié, mais la compatibilité du schéma doit être confirmée.
- **14:17** — Les traces montrent une hausse des requêtes longues, en particulier sur le chemin d’autorisation. L’équipe n’affirme pas encore que la release est la cause.
- **14:22** — Une limitation temporaire des retries côté consommateur, déjà documentée et approuvée, est activée. Le taux de nouvelles demandes diminue ; l’équipe surveille le backlog et l’intégrité.
- **14:29** — Un canari permet une comparaison de versions à charge comparable ; la version récente montre un temps de rétention des connexions plus élevé.
- **14:36** — Un rollback contrôlé est validé avec le propriétaire de base de données. La restauration est effectuée par lots, les métriques sont surveillées.
- **14:48** — Le taux d’erreur approche le niveau de référence, mais la clôture est différée pendant la résorption du backlog et le rapprochement des transactions.
- **15:17** — Le parcours métier et les contrôles de transaction passent ; le backlog revient sous le seuil, les doublons suspects sont vérifiés. L’IC annonce le rétablissement avec suivi renforcé.

### 19.3 Analyse causale provisoire

**Faits observés :** corrélation entre version, hausse de la durée de certaines requêtes, occupation du pool et erreurs ; limitation des retries réduit l’amplification ; rollback suivi d’une amélioration. Ces faits rendent la régression plausible mais le mécanisme précis demande encore une comparaison de code et des traces.

**Mécanisme confirmé dans le cas fictif :** une modification d’accès aux données allonge la durée de rétention des connexions dans un chemin peu testé. Le pool est alors saturé lors d’un pic. Les retries sans jitter et sans budget de charge augmentent la pression. Le tableau de bord ne montre pas explicitement la saturation du pool ; la détection se fait à travers les erreurs utilisateur plutôt que le signal précurseur.

**Facteurs contributifs :** test de charge insuffisant pour le profil de pointe ; déploiement canari trop petit ou observé trop peu longtemps ; absence de SLO explicite pour la latence d’autorisation ; garde-fou de retry incomplet ; runbook de rapprochement des transactions pas suffisamment exercé.

**Limites :** le scénario n’établit pas qu’une seule action aurait empêché tous les impacts. Les tests et les traces doivent confirmer que la modification précise est nécessaire à la saturation et que le rollback ne fait pas que coïncider avec une baisse naturelle de trafic.

### 19.4 Plan d’action de l’étude

| ID | Type | Action | Critère d’acceptation | Responsable hypothétique |
|---|---|---|---|---|
| PAY-01 | Prévention | Ajouter un test de charge sur le chemin d’autorisation au profil de pointe | La version échoue au pipeline si p95 ou taux d’erreur dépasse le seuil convenu | Propriétaire service |
| PAY-02 | Détection | Instrumenter occupation, attente, timeouts et durée de rétention du pool | Un test de saturation déclenche l’alerte correcte et la notification d’astreinte | SRE / observabilité |
| PAY-03 | Atténuation | Introduire budget de retry, backoff et jitter validés | Test de panne simulée ne produit pas de croissance incontrôlée des retries | Équipe API |
| PAY-04 | Récupération | Tester rollback et compatibilité de schéma dans une répétition | Opérateur différent de l’auteur exécute le runbook et vérifie le retour arrière | Release engineering |
| PAY-05 | Intégrité | Automatiser le rapprochement et la détection des transactions ambiguës | Jeux d’essai avec retry/doublon sont rapprochés sans perte silencieuse | Équipe paiement |
| PAY-06 | Processus | Définir seuils de canari et fenêtre d’observation | La release est bloquée automatiquement à la violation d’un seuil | Responsable livraison |

### 19.5 Vérification à 30 jours

Un mois après la livraison, vérifier : le test de charge s’exécute à chaque release concernée ; le tableau de bord expose les signaux précurseurs ; l’alerte est reçue par l’astreinte ; le budget de retry est vérifié sous injection de panne ; le rollback a été exécuté par un autre opérateur ; le taux de récidive et la durée de mitigation sont surveillés. Si un seul livrable existe uniquement sous forme documentaire, l’action n’est pas entièrement validée.

## 20. Anti-patterns experts à éliminer

- **RCA prématurée :** annoncer une cause avant d’avoir examiné les hypothèses concurrentes.
- **RCA à cause unique :** ignorer les barrières défaillantes et les facteurs d’amplification.
- **Réunion sans propriétaire :** la discussion se termine sans action assignée ni date de validation.
- **Action « sensibiliser » :** transférer un risque systémique aux individus.
- **Fermeture à l’alerte verte :** oublier la file, les données ou les parcours métier.
- **Canal de crise unique :** perdre la coordination quand l’outil de messagerie ou d’identité est indisponible.
- **Réponse qui détruit la preuve :** redémarrer, purger ou restaurer sans considérer l’investigation cyber.
- **Métrique de vitesse seule :** raccourcir l’incident au prix d’une récupération fragile.
- **Runbook non testé :** supposer qu’une procédure est exécutable parce qu’elle est lisible.
- **Action sans critère de succès :** clôturer sur une opinion ou un état de ticket.
- **Blameless interprété comme absence de responsabilité :** ne pas corriger les contrôles ou les manquements de gouvernance.
- **Sévérité utilisée comme statut politique :** minimiser les incidents pour protéger des tableaux de bord.

## 21. Modèles opérationnels prêts à adapter

### 21.1 Brief de prise de commandement

```text
ID / Sévérité provisoire :
Service / capacité métier :
IC et heure d’activation :
Impact confirmé / estimé / inconnu :
Objectif de la prochaine période :
Actions actives (action, owner, réussite, rollback) :
Équipes mobilisées / dépendances :
Risques (données, sécurité, propagation, changement) :
Canal de référence / canal de secours :
Prochaine mise à jour :
Critères de baisse de sévérité / clôture :
```

### 21.2 Demande de changement d’urgence

```text
But / ID incident :
Changement exact, périmètre et environnement :
Preuve justifiant l’action :
Alternatives évaluées :
Risques, dépendances et impact possible :
Préconditions / sauvegarde / point de retour :
Exécutant / approbateur :
Indicateurs à surveiller :
Critère de réussite :
Critère d’arrêt / rollback :
Résultat horodaté et preuve :
Revue après action requise : oui/non — owner :
```

### 21.3 Mise à jour aux parties prenantes

```text
État actuel : confirmé / en mitigation / rétabli sous surveillance
Périmètre et impact confirmés :
Ce qui a changé depuis la dernière mise à jour :
Mesure appliquée et résultat mesuré :
Ce qui reste incertain :
Risques résiduels / action suivante :
Prochaine mise à jour :
```

### 21.4 Registre d’hypothèses RCA

```text
Hypothèse ID / formulation :
Pourquoi elle est plausible :
Observations favorables :
Observations contradictoires :
Prédiction testable :
Test discriminant et risque du test :
Source des preuves :
Résultat : confirmée / rejetée / indéterminée
Niveau de confiance et limites :
Prochaine action :
```

### 21.5 Tableau de suivi des actions

```text
ID action | Cause / risque lié | Type (prévention/détection/mitigation/récupération)
Résultat vérifiable | Responsable unique | Échéance | Priorité | Dépendances
Critère d’acceptation | Preuve de réalisation | Test d’efficacité / date de revue
Risque résiduel | Décision de clôture / approbateur
```

## 22. Mettre le dispositif en place en 90 jours

Le calendrier ci-dessous est une proposition d’amélioration progressive, à adapter au contexte, à la taille et aux risques de l’organisation.

### Jours 1–30 : établir les fondations

- sélectionner les services critiques et nommer leurs propriétaires ;
- documenter les seuils de sévérité, rôles, canaux, astreintes et autorité de décision ;
- créer un modèle de journal de décisions, de chronologie et de PIR ;
- choisir un incident majeur récent et évaluer la qualité du dossier ;
- identifier les dépendances, runbooks et principaux risques de récupération ;
- aligner les définitions MTTD, MTTA et MTTR et établir une ligne de base.

### Jours 31–60 : rendre la réponse reproductible

- exécuter un exercice sur table avec un scénario inattendu ;
- améliorer les alertes basées sur l’impact service et les signaux précurseurs ;
- tester les communications et le canal de secours ;
- définir les critères de post-incident review et les règles de conservation des preuves ;
- transformer les actions RCA en tâches traçables, avec un owner et des critères de réussite ;
- vérifier un runbook de rollback, de failover ou de restauration sur un environnement approprié.

### Jours 61–90 : mesurer l’efficacité

- exécuter un exercice technique contrôlé si le contexte l’autorise ;
- vérifier si les actions prioritaires ont changé les signaux ou les modes de défaillance ;
- analyser les récidives et les incidents détectés par les clients ;
- revoir les risques résiduels avec les propriétaires métier ;
- publier un tableau de bord qui montre les percentiles, la sévérité et les retards d’actions ;
- faire une revue de maturité et prioriser le prochain trimestre.

## 23. Évaluation finale — questions expertes

1. Pourquoi restaurer le service ne suffit-il pas à clore le problème sous-jacent ?
2. Quels faits permettent de justifier une reclassification SEV-2 vers SEV-1 ?
3. Quelle est la différence entre une cause directe, une condition contributive et une défaillance de contrôle ?
4. Comment tester une hypothèse sans transformer la production en laboratoire dangereux ?
5. Pourquoi une chronologie doit-elle conserver le fuseau et la source de chaque événement ?
6. Quelles limites un redémarrage peut-il créer pour l’investigation d’un incident cyber ?
7. En quoi un rollback est-il dangereux si une migration de données a eu lieu ?
8. Pourquoi « ajouter une alerte » ne constitue-t-il pas une action complète ?
9. Quels signaux permettent de confirmer que la stabilisation est durable ?
10. Comment éviter que MTTR ou le nombre d’incidents ne créent des incitations indésirables ?
11. Quand faut-il relier un incident à un problème même s’il n’y a pas de récidive ?
12. Quelles sont les exigences minimales d’une action corrective vérifiable ?
13. Comment traiter une dépendance fournisseur qui respecte son SLA mais provoque une dégradation chez le consommateur ?
14. Quelle différence entre RTO, RPO, SLO et SLA ?
15. Comment préserver la séparation entre analyse sans blâme et responsabilité de gouvernance ?

### Corrigé synthétique

1. La mitigation restaure un service mais peut laisser intactes les causes et les barrières défaillantes. 2. Extension du périmètre, criticité métier, risque sécurité/intégrité, absence de contournement ou propagation en hausse. 3. Le mécanisme produit l’effet immédiat ; les conditions augmentent la probabilité ou l’amplification ; le contrôle aurait dû prévenir, détecter ou limiter. 4. Définir une prédiction, un test autorisé, un périmètre limité et un plan d’arrêt ; privilégier tests/replays contrôlés si possible. 5. Les systèmes ont des horloges et des latences différentes ; les preuves sourcées permettent une causalité défendable. 6. Il peut supprimer des traces et écraser des éléments volatils ; coordonner sécurité et collecte. 7. Le retour de version peut être incompatible avec le schéma ou les données écrites. 8. Il faut un signal, seuil, destinataire, test, runbook et preuve de réception. 9. Parcours métier, taux d’erreur/latence, backlog, intégrité, durée d’observation et absence de récidive. 10. Mesurer plusieurs dimensions, segmenter et éviter la punition liée aux déclarations. 11. Lorsqu’un seul incident porte un risque majeur ou révèle un mécanisme inconnu et coûteux. 12. Résultat attendu, owner, date, critère d’acceptation, preuve et test d’efficacité. 13. Revoir l’attente de dépendance, le contrat entre services et la résilience du consommateur. 14. RTO = délai cible de reprise ; RPO = perte de données temporelle tolérable ; SLO = cible fiabilité mesurée ; SLA = engagement de service. 15. Comprendre les conditions sans pointer une personne, puis attribuer explicitement les actions et décisions de gouvernance.

## 24. Glossaire opérationnel

- **Incident Commander (IC) :** responsable de la coordination et des décisions d’ensemble pendant l’incident.
- **PIR / postmortem :** revue structurée après incident qui documente impact, chronologie, causes, réponse et actions.
- **RCA :** analyse des causes et facteurs qui ont permis l’événement ou son impact.
- **MTTD / MTTA / MTTR :** mesures temporelles à définir précisément dans chaque organisation.
- **SLA / SLO / SLI :** engagement, objectif et indicateur de niveau de service.
- **RTO / RPO :** objectifs de délai de reprise et de point de récupération des données.
- **Blast radius :** étendue potentielle d’impact d’une défaillance ou d’un changement.
- **Canary :** déploiement initial sur un périmètre limité pour observer les résultats avant généralisation.
- **Load shedding :** rejet contrôlé d’une partie de la charge pour éviter l’effondrement global.
- **Runbook :** procédure opérationnelle reproductible pour une tâche ou situation connue.
- **Problem record :** dossier de gestion d’un problème lié à un ou plusieurs incidents.
- **Erreur connue :** problème analysé pour lequel la cause ou le contournement est documenté, même si la correction durable reste en attente.
- **Action corrective :** travail ayant un résultat vérifiable qui réduit une cause ou un risque déterminé.
- **Sans blâme :** approche qui favorise l’analyse du système et des conditions plutôt que l’accusation personnelle.
- **Hypothèse falsifiable :** explication qui produit une prédiction pouvant être contredite par un test.
- **Erreur budgétaire / error budget :** tolérance de non-fiabilité résultant d’un objectif de fiabilité, si l’organisation emploie cette méthode.

## 25. Références et limites d’usage

Les pratiques et la terminologie peuvent varier selon l’édition, les guides sous licence, les contrats et les politiques de l’organisation. Le cours est une ressource pédagogique et ne remplace pas les publications officielles ni les procédures validées localement.

- **PeopleCert — ITIL 4 Practitioner: Incident Management** : https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil4-practices-incident-management-3684
- **PeopleCert — bibliothèque des guides ITIL** : https://www.peoplecert.org/peoplecert-library
- **Google SRE — Incident Management Guide** : https://sre.google/resources/practices-and-processes/incident-management-guide/
- **Google SRE — ressources sur les postmortems** : https://sre.google/sre-book/postmortem-culture/
- **Atlassian — Incident postmortems** : https://www.atlassian.com/incident-management/handbook/postmortems
- **Atlassian — modèle de postmortem** : https://www.atlassian.com/incident-management/postmortem/templates
- **CISA — Incident and Vulnerability Response Playbooks** : https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks
- **NIST — Incident Response Recommendations and Considerations for Cybersecurity Risk Management (SP 800-61 Rev. 3)** : https://csrc.nist.gov/pubs/sp/800/61/r3/final

Ces références éclairent des aspects complémentaires : gestion de la pratique ITIL, commandement des incidents, culture de postmortem et réponse cyber. Les processus cyber et les obligations légales nécessitent une adaptation à la juridiction, aux contrats et au contexte réel.


**Fin du cours — Gestion d’incident (ITIL et RCA), niveau Expert.**
