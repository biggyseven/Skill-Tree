# Introduction aux Réseaux OT / ICS — Intermédiaire

## Mise en contexte

Au niveau débutant, tu as appris à reconnaître les composants d’un environnement industriel et à dessiner une architecture simple. Le niveau intermédiaire passe de la compréhension à la conception et à l’exploitation : établir un inventaire fiable, définir les zones et conduits, documenter les flux, appliquer des règles de segmentation, analyser des communications sans perturber le procédé et préparer des opérations de maintenance ou de réponse aux incidents.

Ce cours adopte une approche défensive. Les analyses de trafic et les exercices utilisent des maquettes, des journaux ou des captures approuvées. Une production réelle ne doit pas être testée sans autorisation, validation opérationnelle, analyse de risque et procédure de changement.

## 1. Objectifs

À la fin de ce niveau, tu sauras :

- construire un inventaire OT avec criticité et dépendances ;
- découper un système en zones de sécurité et conduits de communication ;
- concevoir une DMZ industrielle et limiter les flux entre IT et OT ;
- rédiger une matrice de règles de pare-feu avec justification et propriétaire ;
- connaître les usages et limites des protocoles industriels courants ;
- organiser la visibilité réseau passive et la gestion des journaux ;
- planifier l’accès distant de tiers, les sauvegardes et la maintenance ;
- préparer un processus de gestion des vulnérabilités compatible avec les opérations ;
- traiter un incident OT en coordination avec les opérateurs et les responsables de sûreté.

## 2. Modèle de risque OT

En environnement OT, la gravité d’un incident dépend de ses effets sur le procédé, et non seulement de l’actif informatique touché. Un serveur de supervision peut être critique parce qu’il masque les alarmes ou empêche l’opérateur de connaître l’état du système, même si la logique du PLC continue localement. À l’inverse, une interruption d’un service IT non essentiel peut n’avoir qu’un impact limité sur la production.

Pour chaque actif, décrire :

- sa fonction et le procédé concerné ;
- sa criticité en matière de sécurité, d’environnement, de production et de conformité ;
- ses dépendances réseau, électriques, temporelles et applicatives ;
- les modes dégradés disponibles ;
- les conséquences d’une perte de confidentialité, d’intégrité ou de disponibilité ;
- le temps de rétablissement requis et les exigences de sauvegarde ;
- le propriétaire opérationnel et l’équipe autorisée à intervenir.

Une évaluation de risque doit associer automatisme, exploitation, maintenance, IT, cybersécurité et sûreté. Une classification technique seule ne suffit pas à décider des mesures.

## 3. Inventaire exploitable et cartographie des flux

### 3.1 Champs recommandés

Un inventaire intermédiaire peut contenir : identifiant stable, fabricant, modèle, version firmware, système d’exploitation, adresse(s), sous-réseau, VLAN, zone, fonction, propriétaire, criticité, accès physique, accès distant, protocoles, dépendances, sauvegarde, état de support, dernière vérification et source de l’information.

Les champs doivent distinguer une donnée confirmée, une donnée estimée et une donnée inconnue. Les changements d’adresse ou de rôle sont à tracer, sans effacer l’historique nécessaire au diagnostic.

### 3.2 Cartographie de flux

Pour chaque flux connu, enregistrer :

| Champ | Question à résoudre |
|---|---|
| Source et destination | Quels systèmes précis communiquent ? |
| Sens initiateur | Quel système ouvre la session ? Y a-t-il des flux retour nécessaires ? |
| Protocole et service | Quelles fonctions applicatives sont utilisées ? |
| Port | Est-il confirmé, configurable ou seulement supposé ? |
| Besoin métier | Quelle fonction du procédé dépend de ce flux ? |
| Fréquence et volume | Communication périodique, événementielle, transfert de fichier ? |
| Criticité | Quel est l’effet de la perte ou de l’altération ? |
| Propriétaire | Qui valide le besoin et la règle ? |
| Preuve | Document de conception, configuration, journal ou capture ? |

Ne déduis pas la totalité d’un flux depuis un numéro de port. Les ports par défaut sont des indices ; les équipements et intégrateurs peuvent modifier les services ou employer des communications complémentaires.

## 4. Segmentation : zones et conduits

L’approche par zones et conduits, présentée notamment dans la série ISA/IEC 62443, regroupe les actifs selon leurs exigences de sécurité et contrôle les communications qui relient ces groupes.

- **Zone :** ensemble d’actifs soumis à des exigences de sécurité similaires.
- **Conduit :** ensemble de communications entre zones, soumis à des exigences documentées.
- **Système considéré (SUC) :** périmètre du système étudié pour une analyse donnée.
- **Niveau de sécurité cible :** résultat de l’analyse de risque dans le cadre des normes applicables ; il ne doit pas être choisi arbitrairement ni confondu avec un score de maturité général.

Une zone peut être définie par fonction (contrôle d’une cellule, supervision d’une ligne, ingénierie) plutôt que seulement par emplacement physique. Deux équipements sur le même switch peuvent nécessiter une séparation logique et des contrôles de flux.

### 4.1 Exemple d’architecture

```text
Réseau entreprise
      |
[FW IT/DMZ]  Règles explicites et journalisées
      |
+-------------------------------+
| DMZ industrielle              |
| - bastion de maintenance      |
| - relais de transfert         |
| - collecteur de journaux      |
| - dépôt de fichiers contrôlé  |
+-------------------------------+
      |
[FW DMZ/OT]  Flux limités par besoin
      |
+-------------------------------+
| Zone supervision site         |
| SCADA / historien / alarmes   |
+-------------------------------+
      |
[Frontière contrôlée]
      |
+-------------------------------+
| Zone cellule                  |
| IHM / PLC / équipements       |
+-------------------------------+
```

Ce schéma est conceptuel. L’emplacement, les fonctions redondantes et les flux requis varient selon l’installation. Certains protocoles industriels établissent des sessions ou échanges secondaires qui exigent une validation spécifique de la règle de filtrage.

### 4.2 De la règle « tout autoriser » à une règle justifiée

Partir d’une politique restrictive, puis documenter les communications nécessaires. Il faut éviter deux erreurs opposées : ouvrir une zone entière pour faciliter le dépannage, ou bloquer sans comprendre les effets sur les alarmes et les opérations.

Exemple de matrice fictive :

| Source | Destination | Service | Décision proposée | Conditions |
|---|---|---|---|---|
| IHM cellule A | PLC cellule A | protocole du constructeur validé | autoriser | uniquement entre actifs identifiés |
| PLC cellule A | serveur de supervision | télémétrie documentée | autoriser si nécessaire | sens et paramètres vérifiés |
| Poste bureautique | PLC | accès d’administration | refuser par défaut | exception uniquement après analyse et approbation |
| Fournisseur | bastion DMZ | accès distant | autoriser sous contrôle | identité individuelle, MFA adapté, durée limitée, journalisation |
| Bastion | actif industriel ciblé | outil/service nécessaire | autoriser pour la fenêtre approuvée | destination et port précis, approbation locale |
| Internet | PLC ou IHM | interface directe | refuser | ne pas publier les interfaces OT |

La journalisation des refus comme des autorisations peut aider, mais doit être dimensionnée pour éviter de saturer les équipements ou les collecteurs. Les règles temporaires doivent avoir une date d’expiration et un propriétaire.

## 5. Protocoles industriels : fonctionnement et limites

### 5.1 Modbus TCP

Modbus TCP transporte des requêtes et réponses de lecture ou d’écriture de registres et de bobines. Il est couramment associé au port TCP 502. La sécurité du protocole classique ne doit pas être confondue avec celle d’un tunnel ou d’une architecture qui l’entoure. Les lectures, écritures et accès aux registres n’ont pas le même impact potentiel.

Le registre n’est pas toujours auto-descriptif : son échelle, son unité, son signe et sa signification dépendent de la documentation du fabricant. Une valeur brute sans carte de registres peut conduire à une interprétation fausse.

### 5.2 OPC UA

OPC UA fournit un modèle d’échange de données et peut utiliser des mécanismes de sécurité tels que les certificats, la signature et le chiffrement. Les garanties réelles dépendent de la version, du profil, des politiques configurées, de la confiance accordée aux certificats et de la gestion du cycle de vie des clés. Activer un serveur n’implique pas que l’authentification forte et le chiffrement soient correctement configurés.

### 5.3 DNP3, PROFINET, EtherNet/IP et BACnet

Ces familles répondent à des besoins et environnements différents. Il faut connaître le profil effectivement déployé, les modes de communication, les mécanismes d’authentification éventuellement disponibles, les équipements compatibles et les contraintes temporelles. Ne pas appliquer une recommandation générique sans la confronter à la documentation du produit.

### 5.4 Horodatage et synchronisation

Les événements industriels doivent être corrélés. Un service de temps maîtrisé est important pour la comparaison des alarmes, des journaux, des changements et des incidents. Une dérive temporelle peut donner l’impression que les systèmes ne sont pas d’accord sur l’ordre des événements. La source de temps, les chemins réseau et les dépendances doivent être documentés. Dans certains systèmes, des protocoles spécialisés comme PTP sont nécessaires à des exigences de précision supérieures.

## 6. Visibilité réseau sans perturber le procédé

### 6.1 Collecte passive

Une collecte passive observe les communications existantes au moyen d’un TAP, d’un port SPAN ou d’une fonction de télémétrie conçue pour l’installation. Avant de la déployer, vérifier l’impact sur les switches, le risque de perte de paquets, le volume, la redondance et le point de collecte. Une mauvaise configuration SPAN peut ne copier qu’une partie du trafic.

### 6.2 Baseline du comportement normal

Établir une référence par cellule ou fonction : actifs qui communiquent, relations initiateur/répondeur, services habituels, périodicité, volumes, fenêtres de maintenance et changements légitimes. Il est préférable d’expliquer un comportement attendu que de déclencher des alertes sur des ports isolés sans contexte.

Les signaux utiles peuvent inclure :

- un nouvel actif ou une adresse inconnue ;
- une communication d’un réseau bureautique vers une cellule ;
- une nouvelle relation d’administration ;
- un changement de programme ou de configuration d’ingénierie ;
- une hausse anormale des erreurs, retransmissions ou délais ;
- une modification des services disponibles ;
- un transfert de fichier en dehors des fenêtres prévues.

Une anomalie est un indice à examiner, pas une preuve automatique d’attaque. Les modifications planifiées, opérations de maintenance et basculements doivent être intégrés à la baseline.

### 6.3 Journaux à corréler

Selon les systèmes, les sources peuvent comprendre les pare-feux, switches, VPN, bastions, serveurs d’accès, serveurs SCADA, systèmes d’ingénierie, contrôleurs, plateformes d’authentification et inventaires de changements. Tous les automates ne produisent pas les mêmes journaux, et les capacités de journalisation doivent être vérifiées sur les versions concernées.

## 7. Accès distant des fournisseurs

Un modèle d’accès distant robuste comporte :

1. demande de service identifiée et approuvée ;
2. identité individuelle et authentification adaptée ;
3. poste de maintenance conforme et contrôlé ;
4. accès via une passerelle ou un bastion dans la zone adaptée ;
5. restriction de la destination, de la fonction et de la durée ;
6. journalisation de la session et des actions lorsque techniquement possible ;
7. présence ou validation du personnel OT lorsque le risque le nécessite ;
8. fermeture de la session et révocation des droits temporaires ;
9. compte rendu et conservation des preuves selon la politique.

Le MFA est une mesure importante, mais il ne suffit pas à rendre sûr un accès. Il faut aussi contrôler la portée des droits, la santé du poste, les chemins réseau, les fichiers échangés et la supervision des sessions.

## 8. Gestion des vulnérabilités et changements

La gestion des vulnérabilités OT doit associer exposition réelle, exploitabilité, conséquences sur le procédé, disponibilité d’un correctif, compatibilité constructeur, fenêtre de maintenance et moyens de compensation.

Ordre de travail conseillé :

1. confirmer l’actif et sa version ;
2. vérifier la vulnérabilité dans une source fiable et les avis du fabricant ;
3. déterminer si le composant et la fonctionnalité concernés sont réellement présents ;
4. évaluer l’exposition réseau et les conséquences ;
5. consulter l’équipe d’automatisme et le fournisseur si nécessaire ;
6. tester le correctif en laboratoire représentatif ;
7. préparer sauvegarde, validation, fenêtre et retour arrière ;
8. appliquer le changement selon l’autorisation ;
9. vérifier le comportement du procédé et le fonctionnement des communications ;
10. documenter le résultat et mettre à jour l’inventaire.

Lorsque le patch ne peut pas être posé immédiatement, les mesures compensatoires peuvent inclure la suppression d’un chemin réseau inutile, une règle de filtrage précise, la limitation de l’accès distant, une surveillance accrue ou une désactivation de service approuvée. Une mesure compensatoire doit avoir un responsable et une date de réévaluation.

## 9. Sauvegarde et reprise

Une stratégie de sauvegarde OT doit couvrir les projets des automates, les configurations IHM/SCADA, les configurations réseau et de sécurité, les certificats, les licences, les paramètres des équipements et les procédures de reconstruction. Il faut vérifier l’intégrité, le contrôle d’accès et la séparation des copies.

Une sauvegarde n’est utile que si la restauration est réalisable. Les tests doivent se faire dans un environnement de validation ou selon une procédure approuvée, pas en restaurant directement sur un contrôleur actif au hasard.

Documenter les dépendances de reprise : identité, DNS, temps, serveurs de licences, stations d’ingénierie, clés, configurations de switch, fichiers projet, versions de firmware et disponibilité des pièces de rechange.

## 10. Réponse à un incident OT

### 10.1 Principes

- préserver la sûreté et la stabilité du procédé ;
- mobiliser l’équipe opérationnelle avant une isolation qui peut interrompre les contrôles ;
- conserver les preuves et les journaux ;
- limiter les changements improvisés ;
- décider des actions selon les conséquences, pas uniquement selon la gravité cyber ;
- définir un décideur opérationnel pour les actions qui affectent le contrôle.

### 10.2 Séquence indicative

1. détecter et consigner les symptômes ;
2. informer le responsable opérationnel et le dispositif d’incident ;
3. déterminer le périmètre et les systèmes potentiellement touchés ;
4. préserver les journaux, configurations et traces disponibles ;
5. évaluer si une mesure de confinement risque de modifier le procédé ;
6. appliquer le confinement approuvé le moins perturbateur ;
7. vérifier la stabilité, les alarmes et la capacité de reprise ;
8. restaurer selon un ordre de dépendances validé ;
9. confirmer les fonctions de contrôle et la qualité des données ;
10. examiner la cause racine et mettre à jour les protections.

Il ne faut pas présumer qu’éteindre ou déconnecter un contrôleur est la bonne réponse. Le choix peut être différent selon le système, le mode manuel disponible, le SIS et les procédures de site.

## 11. Travaux pratiques corrigés

### TP 1 — Conception d’une segmentation

**Scénario simulé :** une ligne de production comprend deux cellules de PLC, des IHM, un historien partagé, un poste d’ingénierie et un accès fournisseur.

**Travail demandé :** créer les zones, préciser les flux autorisés, localiser la DMZ et identifier ce qui doit être refusé par défaut.

**Correction indicative :** séparer les cellules si leurs fonctions et conséquences de risque le justifient ; placer les services de transfert et d’accès distant dans la DMZ industrielle ; limiter les communications de l’historien aux sources nécessaires ; rendre l’accès d’ingénierie contrôlé et journalisé ; refuser l’accès direct du réseau bureautique et d’Internet aux PLC ; documenter tous les flux nécessaires au fonctionnement et aux opérations validées.

### TP 2 — Évaluer une règle de pare-feu

Règle existante : `source = any`, `destination = réseau PLC`, `service = any`, `action = allow`.

**Correction :** cette règle est trop large. Reconstituer les flux de fonctionnement, identifier chaque source précise et service validé, limiter les destinations, activer une journalisation appropriée, tester les communications critiques, puis procéder via un changement approuvé. Ne pas supprimer brutalement la règle sans connaître ses dépendances.

### TP 3 — Construire une baseline passive

Utiliser une capture fournie par un laboratoire ou un simulateur. Établir la liste des couples source/destination, protocoles, périodicités approximatives et changements pendant la maintenance simulée.

**Correction attendue :** séparer les communications habituelles des nouvelles relations, noter les limites de la capture (durée, point de collecte, pertes éventuelles) et valider les anomalies avec le propriétaire du système. Ne pas lancer de scan actif pour compléter la capture sans autorisation.

### TP 4 — Traiter une vulnérabilité d’un poste d’ingénierie

**Contexte :** un avis constructeur concerne une version utilisée par une station d’ingénierie, mais le correctif n’a pas encore été testé.

**Correction indicative :** confirmer version et exposition, demander l’avis du fabricant, analyser les conséquences, réduire les chemins d’accès inutiles, renforcer la supervision, tester le correctif sur un environnement représentatif, préparer la restauration et programmer la mise à jour dans une fenêtre approuvée. Documenter la mesure compensatoire et sa date d’expiration.

### TP 5 — Préparer une procédure d’accès fournisseur

Définir l’identité, l’approbation, la durée, la destination, les outils, la journalisation, l’accompagnement local, le transfert de fichiers et la révocation.

**Correction attendue :** aucune session permanente ni compte partagé ; chaque accès doit avoir un motif, une portée limitée, un responsable et un compte rendu. Les règles particulières dépendent de la criticité et des capacités de la plateforme.

## 12. Exercices corrigés

### Exercice 1 — Zone ou conduit ?
**Correction :** une zone regroupe des actifs aux exigences similaires ; un conduit définit les communications contrôlées entre zones.

### Exercice 2 — Les VLAN suffisent-ils à segmenter la sécurité ?
**Correction :** non. Les VLAN séparent des domaines de niveau 2, mais il faut maîtriser les routes, les communications inter-VLAN, les plans d’administration et les règles des équipements frontière.

### Exercice 3 — Une détection passive est-elle sans risque ?
**Correction :** elle est généralement moins intrusive qu’un scan actif, mais son point de collecte, la charge du switch, la perte de paquets et le câblage doivent être évalués.

### Exercice 4 — OPC UA est-il automatiquement sécurisé ?
**Correction :** non. Les garanties dépendent des politiques, certificats, modes de sécurité, autorisations et configurations effectivement activés.

### Exercice 5 — Faut-il patcher immédiatement tout système vulnérable ?
**Correction :** il faut traiter la vulnérabilité selon le risque et l’exposition, mais tester la compatibilité et planifier le changement avec les responsables OT. Un déploiement précipité peut créer une indisponibilité.

### Exercice 6 — Que faire d’une règle temporaire sans propriétaire ?
**Correction :** la documenter et la faire examiner ; ne pas la supprimer aveuglément. Trouver les dépendances, définir un responsable et une date de revue puis appliquer un changement approuvé.

### Exercice 7 — Le VPN rend-il l’accès fournisseur sûr ?
**Correction :** non à lui seul. Il faut aussi identité individuelle, MFA approprié, restriction des destinations et fonctions, bastion, supervision, transfert de fichiers maîtrisé et révocation.

### Exercice 8 — Pourquoi synchroniser les horloges ?
**Correction :** pour corréler événements, alarmes, journaux et changements. La source et la précision temporelle doivent correspondre aux exigences du système.

### Exercice 9 — Une alerte IDS prouve-t-elle une attaque ?
**Correction :** non. Elle doit être contextualisée avec la baseline, la maintenance planifiée, les journaux, le rôle des systèmes et la confirmation de l’équipe OT.

### Exercice 10 — Une sauvegarde d’automate doit-elle être testée ?
**Correction :** oui, dans un cadre validé. La disponibilité du fichier ne prouve ni sa cohérence ni la possibilité de restaurer le système.

## 13. Défi final corrigé

### Énoncé

Une usine possède un réseau bureautique, une DMZ existante mal documentée, un historien, quatre cellules industrielles et deux fournisseurs qui utilisent des accès VPN. Des communications non documentées sont observées entre le réseau bureautique et une cellule. Les configurations de pare-feu sont disponibles, mais personne ne connaît le propriétaire de certaines règles.

Construire un plan de remédiation progressif.

### Correction détaillée

**Phase 1 — Gouvernance et précautions.** Nommer les responsables métier et techniques, définir le périmètre, confirmer les contraintes de production et créer un processus d’autorisation des actions. Ne pas bloquer immédiatement un flux inconnu avant d’avoir vérifié son rôle.

**Phase 2 — Inventaire et preuve.** Consolider les actifs, les zones, les relations de flux et les règles. Comparer les configurations, journaux et observations passives. Marquer les hypothèses et les inconnues. Rechercher des sessions de maintenance ou dépendances oubliées.

**Phase 3 — Analyse de risque.** Prioriser les communications directes de l’entreprise vers le contrôle, les accès distants permanents, les règles « any-any », les actifs non inventoriés et les chemins non journalisés. Évaluer l’effet opérationnel de chaque correction.

**Phase 4 — Conception cible.** Définir une DMZ industrielle documentée, des zones par fonction, des conduits justifiés, un accès fournisseur via bastion, une collecte de journaux et des copies de sauvegardes vérifiées.

**Phase 5 — Pilote.** Tester les règles et procédures dans une maquette ou une cellule pilote. Pour les changements de production, créer une fenêtre, un plan de test, un retour arrière et une procédure d’escalade.

**Phase 6 — Déploiement et vérification.** Corriger les flux par lots, surveiller le fonctionnement, confirmer alarmes et collecte des données, puis faire signer l’acceptation opérationnelle.

**Phase 7 — Maintien.** Attribuer chaque règle à un propriétaire, fixer des dates de revue, supprimer les droits temporaires après intervention, réévaluer les vulnérabilités et tester périodiquement la reprise.

Indicateurs utiles : taux d’actifs inventoriés, pourcentage de règles avec propriétaire, nombre de communications IT-vers-OT non justifiées, sessions fournisseurs non journalisées, couverture de sauvegarde restaurable, délai de clôture des exceptions et nombre d’incidents induits par des changements.

## 14. Glossaire complémentaire

- **Baseline :** représentation documentée d’un comportement normal.
- **Bastion :** point de contrôle pour l’accès à des systèmes sensibles.
- **Conduit :** chemin de communication régi par des exigences de sécurité.
- **DMZ industrielle :** zone intermédiaire contrôlée entre des domaines de confiance.
- **MFA :** authentification multifacteur.
- **SUC :** système étudié dans une analyse de risque.
- **TAP/SPAN :** mécanismes d’observation du trafic réseau.
- **Gestion compensatoire :** mesure réduisant le risque lorsqu’un contrôle idéal ne peut être mis en place immédiatement.

## 15. Références

1. NIST SP 800-82 Rev. 3, guide final OT : https://csrc.nist.gov/pubs/sp/800/82/r3/final
2. ISA/IEC 62443, série de normes de cybersécurité pour l’automatisation industrielle : https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards
3. CISA et partenaires, guide d’inventaire des actifs OT : https://www.cisa.gov/sites/default/files/2025-08/joint-guide-foundations-for-OT-cybersecurity-asset-inventory-guidance_508c.pdf
4. UK NCSC et partenaires, vue d’architecture OT : https://www.ncsc.gov.uk/collection/operational-technology/definitive-architecture-view
5. NIST SP 800-82 Rev. 4, projet public initial publié en septembre 2026 ; il s’agit d’un projet en consultation, pas d’une publication finale : https://csrc.nist.gov/pubs/sp/800/82/r4/ipd
