# Introduction aux Réseaux OT / ICS — Expert

## Mise en contexte

Le niveau expert traite l’environnement OT comme un système cyberphysique dont les composants réseau, les logiciels de contrôle, l’ingénierie, les opérateurs et les fonctions de sûreté sont interdépendants. L’objectif n’est pas d’appliquer mécaniquement des contrôles IT : il s’agit de concevoir une architecture défendable, de mesurer le risque sur le procédé, de détecter les comportements anormaux, de répondre aux incidents sans aggraver la situation et de restaurer le service de façon maîtrisée.

Les recommandations ci-dessous s’adressent aux architectes, responsables OT, ingénieurs de contrôle, spécialistes de cybersécurité industrielle et responsables de réponse aux incidents. Toute action active sur un équipement réel doit être autorisée et évaluée par les propriétaires opérationnels concernés.

## 1. Objectifs du niveau expert

À la fin de ce cours, tu devras pouvoir :

- conduire une analyse de risque cyberphysique fondée sur les conséquences ;
- concevoir des zones, conduits et frontières de confiance ;
- définir une architecture OT défendable intégrant DMZ, administration, supervision et accès tiers ;
- interpréter les principes de sécurité OT et les relier à un programme d’amélioration ;
- concevoir une stratégie de détection basée sur les comportements et les processus ;
- préparer des scénarios de réponse aux incidents et une reprise ordonnée ;
- traiter les contraintes de disponibilité, redondance et synchronisation ;
- gérer les risques des fournisseurs, de l’ingénierie et de la chaîne d’approvisionnement ;
- mesurer la maturité à l’aide d’indicateurs utiles, sans confondre conformité et réduction réelle du risque.

## 2. Concevoir à partir des conséquences

### 2.1 Dépasser la gravité informatique

Une même compromission technique peut produire des conséquences très différentes selon le procédé. La compromission d’une station d’ingénierie peut menacer l’intégrité d’un programme de contrôle ; l’indisponibilité d’un historien peut dégrader l’analyse sans interrompre la boucle locale ; la perte d’une IHM peut laisser le contrôle local fonctionner tout en supprimant la visibilité opérateur. Une action de confinement peut elle-même interrompre un chemin de contrôle ou supprimer une capacité de supervision.

L’analyse doit donc établir une chaîne causale :

```text
Menace ou défaillance
        |
        v
Actif ou fonction touchée
        |
        v
Capacité perdue ou altérée
(mesure, commande, supervision, ingénierie)
        |
        v
Effet sur le procédé
        |
        v
Conséquence sécurité / environnement /
production / service essentiel / conformité
        |
        v
Mesures de prévention, détection,
confinement et reprise
```

### 2.2 Atelier de menace cyberphysique

Pour chaque scénario, documenter : acteur ou cause, accès initial plausible, actifs concernés, privilèges nécessaires, mécanisme technique, effet sur les fonctions de contrôle, conditions de détection, conséquences opérationnelles, mesures existantes, hypothèses et incertitudes.

Une matrice de risque doit expliquer ses critères, ses seuils et son propriétaire. Les scores servent à comparer et prioriser, pas à donner une fausse précision lorsqu’on manque de données. Les scénarios doivent être validés par des personnes qui connaissent le procédé et les modes dégradés.

## 3. Architecture défendable et zones/conduits

### 3.1 Définir le périmètre

Décrire le système considéré, les frontières organisationnelles et techniques, les liens avec les fournisseurs, les flux de données, les dépendances essentielles et les interfaces physiques. Une architecture de référence doit représenter aussi les chemins d’administration et de maintenance, pas seulement le trafic applicatif.

### 3.2 Découpage logique

Créer des zones selon les besoins de sécurité et la conséquence d’une compromission : contrôle d’une cellule, supervision d’une ligne, ingénierie, systèmes de sécurité, historiens, services communs, DMZ, accès tiers et infrastructure réseau. Le découpage doit rester cohérent avec les contraintes fonctionnelles, la disponibilité et l’exploitation.

### 3.3 Conduits et politiques

Chaque conduit doit avoir une finalité, des extrémités, des services, un sens d’initiation, des exigences de disponibilité, une méthode de surveillance, un propriétaire et un processus de modification. Un flux « quelconque » ou un accès d’administration large ne peut être accepté uniquement parce que le fournisseur en demande la commodité.

### 3.4 Exemple cible

```text
       Services d'entreprise / SOC
                  |
           Frontière IT/OT
                  |
  +------------------------------------+
  | DMZ industrielle                   |
  | - bastion d'administration         |
  | - relais de transfert contrôlé     |
  | - collecteur / réplication de logs |
  | - dépôt de mises à jour vérifiées  |
  +------------------------------------+
                  |
            Frontière OT/DMZ
                  |
  +------------------------------------+
  | Services OT du site                |
  | - historien répliqué               |
  | - supervision et gestion           |
  | - services communs approuvés       |
  +------------------------------------+
                  |
       frontières de cellules contrôlées
          /             |             \
  +------------+ +------------+ +------------+
  | Cellule A  | | Cellule B  | | Ingénierie |
  | IHM / PLC  | | IHM / PLC  | | station    |
  +------------+ +------------+ +------------+
                  |
     fonctions de sécurité séparées
     selon l'analyse et la conception
```

Ce schéma n’est pas universel. Le placement de l’historien, les chemins de télémétrie, les contrôleurs redondants et le réseau de sûreté dépendent de l’ingénierie du site. Les fonctions SIS doivent être analysées selon les exigences de sûreté et ne doivent pas être considérées comme protégées par le seul fait d’être dessinées dans une zone séparée.

### 3.5 Contrôle des flux applicatifs

Pour chaque règle, préciser si l’on contrôle une session réseau, une commande applicative, une identité ou une action d’ingénierie. Le filtrage IP/port ne comprend pas nécessairement le sens opérationnel d’une commande. Les passerelles de protocole ou dispositifs d’inspection peuvent apporter du contexte, mais leur compatibilité, leur comportement de panne, leur latence et leurs effets sur le déterminisme doivent être testés.

La règle la plus stricte n’est pas toujours celle qui offre la meilleure sécurité totale : une interruption inattendue peut avoir un impact de sûreté. Toute politique doit être validée avec les personnes responsables du procédé.

## 4. Principes Zero Trust adaptés à l’OT

Les principes de vérification explicite, de moindre privilège et de limitation de l’exposition peuvent améliorer la protection OT. Leur mise en œuvre doit néanmoins respecter les équipements anciens, les protocoles à faible capacité d’authentification, les flux déterministes, les fonctions de sécurité et les capacités de fonctionnement local.

Une approche pratique peut inclure :

- inventorier les actifs, les identités, les applications et les flux ;
- vérifier chaque accès d’administration et sa justification ;
- privilégier les identités individuelles et supprimer les comptes partagés lorsque cela est réalisable ;
- limiter les privilèges et la durée des autorisations ;
- contrôler les postes et outils de maintenance ;
- placer les points d’administration derrière des frontières dédiées ;
- journaliser les décisions et actions compatibles avec le système ;
- prévoir un mode de défaillance sûr et des procédures locales ;
- éviter d’introduire des agents ou des mécanismes interactifs dans les PLC sans validation du fabricant et de l’ingénierie.

Zero Trust ne signifie pas nécessairement installer un agent sur chaque PLC ni intercepter chaque échange de terrain. Dans certains environnements, les contrôles les plus pertinents se situent aux frontières, sur les accès d’ingénierie, les postes de maintenance et les flux inter-zones. Les recommandations récentes consacrées à l’OT soulignent la nécessité d’adapter les principes aux contraintes particulières de ces systèmes.

## 5. Visibilité, détection et renseignement opérationnel

### 5.1 Inventaire et référence comportementale

L’inventaire et la cartographie des communications sont des prérequis à la détection. Le système de détection doit comprendre quels actifs sont autorisés, à quoi ils communiquent, quand les opérations de maintenance sont prévues et quelles actions sont critiques.

Établir des références pour :

- les actifs et relations réseau ;
- les protocoles et fonctions utilisées ;
- les sessions d’administration ;
- les opérations de téléchargement ou de modification de programme ;
- les changements de firmware et de configuration ;
- les alarmes et événements de contrôle ;
- les fenêtres de maintenance et les basculements ;
- les volumes, périodes et retards de communication.

### 5.2 Détection multi-sources

Une architecture de détection peut combiner télémétrie réseau passive, journaux d’identité, accès distant, pare-feu, poste d’ingénierie, environnement SCADA, événements des contrôleurs et changements approuvés. La disponibilité des journaux dépend des matériels, des versions et des licences.

Exemples de cas d’usage :

1. nouveau poste qui communique avec une cellule de contrôle ;
2. session d’ingénierie en dehors d’une fenêtre de maintenance ;
3. transfert de programme non associé à un changement approuvé ;
4. nouvel équipement utilisant une fonction d’écriture ;
5. modification soudaine des relations entre actifs ;
6. échecs d’authentification suivis d’une session réussie ;
7. écarts d’horloge qui empêchent une corrélation fiable ;
8. perte d’un capteur de supervision ou d’un point de collecte ;
9. hausse de trafic ou d’erreurs affectant une communication critique.

Les alertes doivent comprendre la preuve, la confiance, le contexte et l’action suggérée. Elles ne doivent pas déclencher automatiquement une coupure de réseau sans évaluation de conséquence et autorité explicite.

### 5.3 MITRE ATT&CK for ICS

La matrice MITRE ATT&CK for ICS peut aider à structurer les hypothèses de comportement adversaire, à identifier les opportunités de détection et à organiser des exercices. Elle ne remplace pas une analyse de risque du procédé. Les techniques doivent être étudiées pour construire des contrôles défensifs, des hypothèses de chasse et des procédures de réponse, et non comme une checklist qui garantirait la sécurité.

## 6. Gestion avancée des vulnérabilités

### 6.1 Prioriser selon l’exposition et les conséquences

Ne pas classer les vulnérabilités uniquement par un score technique générique. Croiser : exploitabilité, présence du service concerné, accessibilité réseau, exposition par un fournisseur, privilèges nécessaires, conséquence sur le procédé, disponibilité du correctif, compatibilité, avis du fabricant et possibilités de contrôle compensatoire.

### 6.2 Processus

1. confirmer l’actif, la version et la configuration ;
2. valider l’avis auprès du fabricant et des sources de référence ;
3. identifier les fonctions affectées et les chemins d’accès ;
4. faire analyser l’impact par l’équipe OT ;
5. décider du patch ou d’une mesure compensatoire temporaire ;
6. tester en laboratoire représentatif ;
7. préparer la sauvegarde, le plan de retour arrière et les critères d’acceptation ;
8. planifier la fenêtre et les autorisations ;
9. exécuter le changement et vérifier le procédé ;
10. documenter l’exception éventuelle, son propriétaire et la date de réexamen.

Une exception permanente sans propriétaire est une dette de risque non maîtrisée. Les contrôles compensatoires doivent être évalués pour vérifier qu’ils ne créent pas de nouvelles dépendances ou points uniques de défaillance.

## 7. Résilience réseau et contraintes temporelles

Les réseaux OT peuvent nécessiter une latence faible, des délais bornés, une disponibilité élevée ou une synchronisation précise. Les exigences diffèrent selon que l’on parle d’une IHM, d’une supervision, d’une commande cyclique de mouvement ou d’un réseau de capteurs.

### 7.1 Redondance

Les mécanismes possibles incluent des chemins réseau redondants, des anneaux industriels, des protocoles de redondance, des contrôleurs et serveurs en haute disponibilité ou des services répliqués. Les mécanismes tels que RSTP, MRP, PRP, HSR ou des solutions propriétaires ne sont pas équivalents et ne sont pas interchangeables dans tous les cas. Il faut confirmer la prise en charge exacte par les équipements, les temps de convergence, le comportement en défaut et les recommandations du fabricant.

### 7.2 Temps et synchronisation

NTP peut convenir à de nombreux besoins de journalisation ; certaines applications de contrôle exigent une synchronisation plus précise, par exemple avec PTP selon le profil et la conception. La perte de la source de temps, un chemin de synchronisation incorrect ou une dérive peuvent nuire au diagnostic et aux fonctions qui utilisent des horodatages. La stratégie de temps doit inclure des sources de référence, des chemins redondants lorsque nécessaire, une surveillance et un comportement documenté en cas de perte.

### 7.3 Qualité de service et congestion

Prioriser un trafic critique peut aider lorsque les files d’attente et les frontières sont conçues correctement, mais une marque DSCP ne réserve pas à elle seule de la bande passante sur tout le chemin. Les commutateurs, routeurs, tunnels et fournisseurs doivent appliquer une politique cohérente. Toute modification de QoS doit être testée avec les profils de trafic réels et les exigences de temps.

## 8. Accès d’ingénierie et chaîne d’approvisionnement

Le poste d’ingénierie est souvent un actif à fort impact, car il peut modifier la logique ou la configuration des contrôleurs. Il doit être traité comme un actif critique : accès limité, logiciels approuvés, configuration de référence, sauvegardes, journalisation, contrôle des médias amovibles et procédure de modification.

Pour les fournisseurs :

- tenir une liste des connexions et services supportés ;
- interdire les accès permanents non justifiés ;
- exiger une demande, un responsable et une durée ;
- contrôler l’identité, le poste et les privilèges ;
- approuver les fichiers et mises à jour avant transfert ;
- enregistrer les sessions quand c’est possible ;
- retirer les autorisations dès la fin ;
- vérifier la configuration après l’intervention ;
- prévoir les obligations contractuelles d’avis de vulnérabilité et d’assistance en incident.

Une signature numérique aide à vérifier l’origine et l’intégrité d’un fichier lorsque la chaîne de confiance est correcte ; elle ne prouve pas à elle seule que le fichier est compatible ou sans risque.

## 9. Réponse aux incidents OT : scénarios et décisions

### 9.1 Ransomware sur un poste d’ingénierie

**Objectif :** empêcher la propagation sans perdre une capacité essentielle de contrôle.

- informer l’autorité opérationnelle et le responsable d’incident ;
- déterminer si le poste est connecté à des cellules ou à des contrôleurs ;
- préserver les journaux et les éléments utiles ;
- utiliser une isolation approuvée si les conséquences sur le procédé ont été comprises ;
- empêcher les connexions d’administration non nécessaires ;
- vérifier l’intégrité des sauvegardes depuis un environnement réputé sain ;
- reconstruire le poste à partir d’une référence validée ;
- vérifier les projets et configurations avant réutilisation.

### 9.2 Écriture anormale vers un contrôleur

**Objectif :** protéger l’intégrité de la logique et la stabilité du procédé.

- confirmer la fonction du contrôleur et les effets potentiels ;
- rechercher une fenêtre de maintenance ou une tâche d’ingénierie autorisée ;
- préserver les traces disponibles, les versions et les journaux d’accès ;
- faire intervenir le personnel de contrôle pour vérifier la logique et l’état du procédé ;
- ne pas télécharger une copie de programme supposée bonne sans validation ;
- restaurer uniquement selon une procédure approuvée et avec validation fonctionnelle.

### 9.3 Fournisseur compromis

- suspendre ou réduire l’accès selon le plan approuvé ;
- identifier les autres chemins, comptes, certificats ou postes associés ;
- vérifier les sessions et changements récents ;
- remplacer les secrets concernés en tenant compte des dépendances ;
- ne pas révoquer aveuglément un certificat ou compte si cela peut arrêter un service essentiel sans plan de remplacement ;
- rétablir l’accès selon une procédure renforcée et temporaire.

### 9.4 Perte de supervision

La perte d’une IHM ou d’un serveur SCADA ne signifie pas nécessairement que le PLC a cessé d’exécuter sa logique. Mais elle peut supprimer des alarmes ou la visibilité de l’opérateur. Appliquer le mode opératoire local, confirmer l’état du procédé par les moyens approuvés, mobiliser l’automatisme et rétablir la supervision dans l’ordre de dépendances documenté.

## 10. Reprise après incident et stratégie de sauvegarde

### 10.1 Objectifs de reprise

Définir les objectifs de temps de reprise (RTO) et les objectifs de point de reprise (RPO) pour les fonctions concernées. Dans l’OT, ces objectifs ne doivent pas être uniquement déterminés par l’IT : ils doivent être confrontés au procédé, aux modes manuels, à la durée de sûreté, aux exigences de qualité et aux conséquences d’une indisponibilité.

### 10.2 Ordre de restauration

L’ordre dépend de l’installation, mais une procédure doit expliciter les dépendances telles que : alimentation et réseau de base, services de temps et d’identité, configuration des équipements réseau, postes de maintenance, services de supervision, historiques, IHM et contrôleurs. Ne jamais imposer un ordre universel sans vérifier le design.

### 10.3 Sauvegardes vérifiables

- maintenir des versions approuvées des projets PLC, HMI, SCADA et des équipements réseau ;
- stocker des copies séparées et contrôler les accès de modification ;
- associer aux sauvegardes les versions et dépendances nécessaires ;
- vérifier la cohérence, l’intégrité et la provenance ;
- tester la restauration dans un environnement de test ou une fenêtre approuvée ;
- documenter les écarts entre projet sauvegardé et configuration réellement déployée ;
- protéger les clés, certificats et licences nécessaires à la reprise.

## 11. Gouvernance et indicateurs de sécurité OT

La gouvernance doit inclure les propriétaires d’actifs, les responsables de procédés, les automatismes, la maintenance, le réseau, la cybersécurité et la sûreté. Les objectifs mesurables doivent encourager le progrès sans pousser à des changements risqués uniquement pour améliorer un indicateur.

Exemples d’indicateurs utiles :

- proportion d’actifs critiques inventoriés et attribués ;
- proportion de flux inter-zones documentés et approuvés ;
- nombre de règles de pare-feu sans propriétaire ;
- nombre d’accès distants tiers permanents ;
- proportion des sauvegardes critiques dont une restauration a été testée ;
- proportion de postes d’ingénierie avec référence de configuration ;
- délai de détection d’un changement non planifié ;
- délai de correction des chemins réseau non nécessaires ;
- nombre d’exceptions de vulnérabilité sans date de réexamen ;
- taux de participation à des exercices inter-équipes.

La conformité à une norme ou à une checklist ne prouve pas à elle seule que le risque est correctement réduit. La preuve doit inclure des tests, des exercices, des résultats de restauration et la validation par les responsables opérationnels.

## 12. Travaux pratiques experts avec corrigés

### TP 1 — Analyse de risque d’une cellule de procédé

**Scénario fictif :** une cellule de pompage comporte deux PLC, une IHM, un variateur communicant et un poste d’ingénierie. Une compromission du poste d’ingénierie pourrait modifier les projets. Une panne de l’IHM rendrait les données locales moins visibles.

**Travail demandé :** décrire trois scénarios de risque, leurs conséquences, les actifs et protections, les détections possibles et les conditions de restauration.

**Correction indicative :**

1. **Modification non autorisée du programme PLC :** impact possible sur la logique ; contrôles : accès d’ingénierie limité, comparaison de projet, sauvegarde validée, fenêtre et double approbation ; détection : changement de programme, session anormale, différence de checksum si la méthode est supportée.
2. **Perte de l’IHM :** perte de visibilité, sans déduire automatiquement l’arrêt du contrôle ; contrôles : référence de configuration, redondance selon les besoins, procédure locale, surveillance de service ; reprise : restaurer la station validée et confirmer alarmes et états.
3. **Perte du réseau entre cellule et supervision :** impact sur historisation ou supervision ; contrôles : architecture redondante si exigée, alarmes de perte de communication, documentation des modes dégradés ; diagnostic : états de lien, logs, compteurs et observation passive.

### TP 2 — Revue de frontière IT/OT

**Scénario :** une règle autorise un réseau bureautique complet vers un sous-réseau de contrôle pour un ancien outil de reporting.

**Travail demandé :** mener la revue sans interrompre l’outil avant de comprendre ses dépendances.

**Correction :** identifier les hôtes, l’application, les sens de session et les horaires ; confirmer le besoin avec le propriétaire ; examiner les journaux et les flux autorisés ; rechercher une solution par réplication, relais ou service DMZ ; tester le changement ; limiter la règle aux extrémités et services requis ; définir un retour arrière et documenter l’acceptation.

### TP 3 — Concevoir un cas de détection

**Cas :** une station d’ingénierie initie une communication vers un PLC en dehors des fenêtres enregistrées.

**Travail demandé :** créer la logique de triage sans déclencher automatiquement un blocage.

**Correction :** enrichir l’alerte avec l’identité du poste, la zone, l’actif cible, le protocole, l’heure, les changements approuvés, le compte utilisé et la criticité du contrôleur ; demander validation à l’équipe OT ; préserver les journaux ; décider d’un confinement avec l’autorité opérationnelle ; utiliser le résultat pour affiner la baseline.

### TP 4 — Exercice de réponse à incident

**Scénario :** le poste d’ingénierie montre des signes de compromission pendant une production active.

**Correction indicative :** contacter immédiatement le responsable du procédé ; déterminer les connexions et la fonction actuelle du poste ; ne pas supposer qu’une coupure physique est sans risque ; conserver les éléments utiles ; appliquer la procédure d’isolement décidée ; vérifier si les contrôleurs et le réseau restent sains ; utiliser une référence de reconstruction validée ; vérifier les programmes et configurations avant reprise ; documenter les décisions et les délais.

### TP 5 — Plan de reprise

Définir les priorités de restauration pour une cellule comprenant réseau, PLC, IHM, historian et service d’identité.

**Correction attendue :** construire un ordre basé sur les dépendances réelles, attribuer un propriétaire à chaque étape, préciser les prérequis, les critères d’acceptation, les points de contrôle de sûreté et les procédures de retour arrière. Tester le plan dans un environnement approuvé et enregistrer les écarts.

## 13. Exercices corrigés

### Exercice 1 — Pourquoi un score CVSS élevé ne suffit-il pas à établir la priorité OT ?
**Correction :** il faut prendre en compte la présence réelle de la fonction, l’exposition, l’accès nécessaire, les conséquences sur le procédé, la compatibilité des correctifs et les mesures compensatoires. Le score technique est une donnée, pas une décision complète.

### Exercice 2 — Une DMZ industrielle rend-elle tous les flux sûrs ?
**Correction :** non. Une DMZ mal configurée, dotée de doubles connexions incontrôlées ou de règles larges peut devenir un pont. Elle doit avoir des fonctions définies, des conduits restrictifs, une surveillance et un processus de changement.

### Exercice 3 — Faut-il bloquer automatiquement tout trafic inconnu détecté par une sonde OT ?
**Correction :** non. Un blocage peut interrompre une communication de contrôle ou un mode dégradé. L’alerte doit être contextualisée et toute mesure active doit suivre une procédure décidée avec les responsables opérationnels.

### Exercice 4 — Zero Trust impose-t-il un agent sur chaque automate ?
**Correction :** non. Les principes peuvent se matérialiser par la segmentation, le contrôle d’accès, l’identité, le moindre privilège, les bastions et la surveillance aux frontières. Les capacités des automates et les contraintes du procédé déterminent les contrôles possibles.

### Exercice 5 — Quelle différence entre redondance et résilience ?
**Correction :** la redondance fournit des composants ou chemins alternatifs ; la résilience inclut aussi la détection, le basculement, les procédures, les personnes, les sauvegardes et la capacité de restaurer le service après une défaillance.

### Exercice 6 — À quoi sert une baseline industrielle ?
**Correction :** à comprendre les relations et comportements habituels, faciliter la détection des changements et réduire les faux positifs. Elle doit être actualisée et associée au calendrier de maintenance.

### Exercice 7 — Peut-on restaurer un programme PLC sauvegardé sans comparaison ni validation ?
**Correction :** non. Il faut confirmer la provenance, la version, la compatibilité et la relation avec le procédé, puis suivre une procédure approuvée avec des tests de fonctionnement.

### Exercice 8 — Pourquoi faut-il des règles d’exception datées ?
**Correction :** elles rendent visible le risque temporaire et permettent la réévaluation. Une exception sans propriétaire ni échéance tend à devenir permanente sans contrôle.

### Exercice 9 — Quel rôle joue l’équipe de sûreté dans une réponse cyber ?
**Correction :** elle évalue les conséquences sur le procédé et les fonctions de sécurité, participe à l’analyse des options de confinement et valide les conditions de remise en service selon les responsabilités du site.

### Exercice 10 — Comment mesurer une restauration réussie ?
**Correction :** par des critères prévus : versions cohérentes, communication fonctionnelle, données et alarmes correctes, validations du procédé, journaux et autorisation opérationnelle. Le simple démarrage d’un serveur ne suffit pas.

## 14. Défi final : architecture et plan de défense d’un site industriel

### Énoncé

Un site comprend quatre cellules de production, un serveur SCADA, un historien, deux stations d’ingénierie, une DMZ, un accès fournisseur et un réseau d’entreprise. Une revue a révélé des règles de pare-feu trop larges, des comptes de maintenance partagés, des sauvegardes non testées et une visibilité réseau incomplète. Le site ne peut pas interrompre la production pour une refonte massive.

Élaborer une feuille de route de défense sur plusieurs phases, avec risques prioritaires, contrôles, mesures de succès et conditions de déploiement.

### Correction détaillée

**Phase 1 — Gouvernance, inventaire et sécurité immédiate**

- nommer le propriétaire opérationnel de chaque actif critique ;
- réunir automatisme, exploitation, IT, cybersécurité, sûreté et fournisseurs ;
- confirmer les chemins d’administration et les dépendances ;
- réduire d’abord les expositions évidentes et non nécessaires selon un plan approuvé ;
- sauvegarder les configurations actuelles avant les changements ;
- conserver une trace des règles, comptes et exceptions.

**Phase 2 — Architecture cible**

- établir les zones et conduits par fonction et conséquences ;
- clarifier la frontière IT/OT et les fonctions de la DMZ ;
- définir le chemin d’accès distant via bastion ou solution contrôlée ;
- réduire les flux à des sources, destinations et services justifiés ;
- séparer les chemins d’administration des flux métier lorsque c’est approprié ;
- définir les contrôles et modes dégradés des fonctions de sûreté.

**Phase 3 — Identités et ingénierie**

- remplacer progressivement les comptes partagés par des identités individuelles lorsque les équipements le permettent ;
- documenter les comptes techniques qui ne peuvent être individualisés immédiatement ;
- limiter et dater les privilèges ;
- approuver les postes, outils et médias de maintenance ;
- établir une procédure de transfert de fichiers et une vérification des changements de programme.

**Phase 4 — Visibilité et détection**

- déployer l’observation passive à des points choisis après évaluation d’impact ;
- vérifier la couverture de collecte, les pertes et les angles morts ;
- corréler pare-feux, bastions, postes d’ingénierie, SCADA et changements ;
- prioriser quelques cas d’usage concrets : nouvel actif, accès distant hors fenêtre, écriture ou téléchargement non approuvé, communication IT-vers-OT inattendue ;
- définir le triage, l’escalade et les autorités décisionnelles.

**Phase 5 — Sauvegardes et reprise**

- identifier les projets et configurations nécessaires ;
- conserver les versions approuvées dans des dépôts à accès contrôlé ;
- tester la restauration hors production ;
- définir les dépendances, les priorités, les objectifs RTO/RPO et les preuves d’acceptation ;
- conduire un exercice de reprise et documenter les lacunes.

**Phase 6 — Changements progressifs**

Déployer les modifications par pilote et fenêtre de maintenance. Chaque changement doit avoir un propriétaire, une analyse d’impact, un plan de test, des critères d’arrêt, un retour arrière et l’approbation des acteurs concernés. Ne pas traiter une architecture OT comme un réseau bureautique que l’on peut redémarrer collectivement.

**Phase 7 — Gouvernance permanente**

Revoir les règles, comptes, accès fournisseurs, sauvegardes et exceptions selon une périodicité définie. Répéter les exercices, ajuster les scénarios de détection et intégrer les leçons des incidents et des changements.

**Indicateurs de succès :** baisse des flux IT-vers-OT non justifiés ; diminution des règles sans propriétaire ; réduction des comptes partagés et accès permanents ; couverture d’inventaire améliorée ; restauration testée pour les actifs critiques ; détection plus rapide des changements non planifiés ; réussite des exercices avec équipes OT et sûreté ; absence d’incident opérationnel introduit par les mesures.

## 15. Liste de contrôle d’architecture

Avant d’approuver une architecture OT, vérifier que :

- les actifs et leurs propriétaires sont connus ;
- les frontières et flux sont documentés ;
- les accès d’administration et de fournisseur sont identifiés ;
- les règles ont un besoin métier et une échéance de revue ;
- les fonctions de sûreté et les modes dégradés ont été évalués ;
- la collecte réseau ne perturbe pas les équipements ;
- les configurations et projets peuvent être restaurés ;
- les sources de temps et journaux sont cohérents ;
- les changements sont testés et réversibles ;
- les responsables OT participent aux décisions de confinement et de reprise.

## 16. Glossaire expert

- **ATT&CK for ICS :** matrice de comportements adverses utilisée pour structurer l’analyse et la défense des systèmes de contrôle industriels.
- **Conduit :** communications entre zones soumises à des exigences précises.
- **RPO :** quantité de données ou de changements que l’organisation accepte de perdre, exprimée par un objectif temporel.
- **RTO :** objectif de durée pour restaurer un service.
- **SIS :** système instrumenté de sécurité, destiné à mettre ou maintenir le procédé dans un état sûr selon sa conception.
- **Télémétrie passive :** observation de trafic ou d’événements sans envoyer de commandes de test aux équipements de contrôle.
- **Zero Trust :** principes de vérification explicite, moindre privilège et exposition réduite, adaptés ici aux contraintes OT.

## 17. Références techniques et statut des documents

1. **NIST SP 800-82 Rev. 3**, guide final de sécurité OT publié en septembre 2023 : https://csrc.nist.gov/pubs/sp/800/82/r3/final
2. **NIST SP 800-82 Rev. 4 — Initial Public Draft**, projet public publié le 21 septembre 2026 ; consultation annoncée jusqu’au 30 novembre 2026. Ce document est un projet et ne doit pas être présenté comme une révision finale : https://csrc.nist.gov/pubs/sp/800/82/r4/ipd
3. **ISA/IEC 62443**, série de normes de cybersécurité pour l’automatisation et les systèmes de contrôle industriels : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
4. **CISA et partenaires**, guide d’inventaire des actifs OT, publié en 2025 : https://www.cisa.gov/sites/default/files/2025-08/joint-guide-foundations-for-OT-cybersecurity-asset-inventory-guidance_508c.pdf
5. **CISA et partenaires**, guide 2026 sur l’adaptation des principes Zero Trust à l’OT : https://content.govdelivery.com/accounts/USDHSCISA/bulletins/4151784
6. **UK NCSC et partenaires**, création et maintenance d’une vue de référence de l’architecture OT : https://www.ncsc.gov.uk/collection/operational-technology/definitive-architecture-view
7. **MITRE ATT&CK for ICS** : https://attack.mitre.org/matrices/ics/

Les guides et standards ne remplacent pas l’analyse de risque propre au site. Les architectures et actions d’intervention doivent être validées avec les responsables des procédés, les ingénieurs de contrôle et les équipes de sûreté.
