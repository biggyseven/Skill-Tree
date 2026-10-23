# Gestion d’incident (ITIL et RCA) — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Public :** techniciens support N1/N2, administrateurs systèmes et réseaux, service desk, responsables applicatifs, coordinateurs IT et futurs Incident Managers.  
**Prérequis :** savoir enregistrer un ticket, reconnaître un incident, recueillir des informations techniques et comprendre les bases de la priorité, de l’escalade et de la documentation.  
**Objectif général :** organiser une réponse cohérente aux incidents complexes, limiter leur impact métier, garder une chronologie fiable et conduire une analyse des causes (RCA) qui aboutit à des actions correctives mesurables.

> **Principe directeur :** pendant l’incident, rétablir le service et contrôler le risque. Après stabilisation, comprendre pourquoi les défenses n’ont pas suffi et améliorer le système. La RCA ne doit pas retarder une mesure de mitigation sûre.

## 1. Résultats d’apprentissage

À la fin du cours, tu dois pouvoir :

- distinguer incident, problème, événement, demande, erreur connue et changement ;
- qualifier impact, urgence, portée, gravité et priorité sans confondre ces notions ;
- déclencher et coordonner une réponse de type incident majeur ;
- répartir les responsabilités entre commandement, opérations, communication et documentation ;
- formuler des hypothèses, collecter des preuves et conserver une chronologie exploitable ;
- construire une RCA qui distingue déclencheur, cause immédiate, facteurs contributifs et causes systémiques ;
- utiliser les 5 pourquoi, Ishikawa, arbre causal et comparaison avant/après sans conclure trop vite ;
- produire un post-incident review et un plan d’actions assortis de propriétaires, d’échéances et de critères de succès ;
- mesurer la qualité de la réponse et suivre les actions jusqu’à leur validation.

## 2. ITIL : le vocabulaire opérationnel

ITIL est un ensemble de bonnes pratiques de gestion des services. Ce cours s’inspire de la pratique **Incident Management** d’ITIL 4, mais les délais, niveaux P1–P4, rôles et seuils proposés ici sont des exemples de conception : chaque organisation doit les adapter à ses contrats, à ses services et à ses risques. Les termes peuvent différer selon les outils ITSM et les éditions de référence.

### 2.1 Incident, problème, demande et changement

- **Incident :** interruption non planifiée d’un service, ou dégradation de sa qualité. Un serveur qui ne répond plus, une application lente ou des utilisateurs qui ne peuvent plus imprimer peuvent déclencher un incident.
- **Problème :** cause réelle ou potentielle d’un ou de plusieurs incidents. Plusieurs erreurs DNS peuvent être des incidents distincts reliés à un même problème de configuration.
- **Demande de service :** requête convenue, par exemple créer un compte, installer un logiciel autorisé ou ajouter un utilisateur à un groupe.
- **Changement :** ajout, modification ou retrait pouvant affecter un service. Une modification réseau mal contrôlée peut déclencher un incident.
- **Événement :** changement d’état détecté ou notifié par un système. Une alerte CPU est un événement ; elle devient un incident lorsqu’elle signale une interruption ou une dégradation qui exige une réponse.
- **Erreur connue :** problème analysé et documenté dont la cause ou une solution de contournement est connue. Elle facilite les diagnostics futurs, mais elle n’implique pas que le risque soit éliminé.
- **Solution de contournement (workaround) :** mesure temporaire qui réduit ou supprime l’impact sans nécessairement corriger la cause. Exemple : désactiver temporairement une fonction fautive.
- **Rétablissement / résolution :** retour du service à un état acceptable selon des critères convenus. Il ne signifie pas forcément que la cause profonde est définitivement corrigée.

### 2.2 Pourquoi séparer gestion des incidents et gestion des problèmes ?

Pendant une panne, le besoin métier immédiat est de récupérer un service fiable. La recherche exhaustive de la cause peut nécessiter des journaux, des spécialistes, une reproduction en environnement de test ou des vérifications longues. Si une action de mitigation réversible peut réduire rapidement l’impact, elle passe généralement avant l’enquête complète.

La gestion des problèmes prend ensuite en charge l’investigation, la prévention de la récurrence et la documentation des erreurs connues. Les deux pratiques se relient via les identifiants, les chronologies, les changements et les actions de suivi. Elles ne doivent pas devenir deux équipes qui se transmettent un ticket sans conserver le contexte.

### 2.3 Impact, urgence, priorité et sévérité

Ces champs répondent à des questions différentes :

- **Impact :** quel périmètre métier est affecté ? Combien d’utilisateurs, de sites, de transactions ou de fonctions essentielles ?
- **Urgence :** combien de temps peut-on attendre avant qu’un dommage important apparaisse ? Existe-t-il une échéance métier, un risque de perte de données ou une obligation de conformité ?
- **Priorité :** quel ordre de traitement faut-il donner, compte tenu de l’impact, de l’urgence et des règles de service ?
- **Sévérité :** dans certains environnements, niveau technique ou métier de gravité (SEV1, SEV2…). Sa définition doit être écrite et cohérente avec la priorité ITSM.

Ne choisis pas une priorité sur la base du statut hiérarchique du demandeur ou de la pression du canal de discussion. Un ticket très bruyant peut avoir un impact limité ; un service silencieusement défaillant peut affecter toutes les transactions.

### 2.4 Matrice de priorité indicative

Le schéma ci-dessous fournit un exemple pédagogique, pas une norme universelle. Remplace les étiquettes par les niveaux réellement définis dans ton organisation. Une matrice 3 × 3 peut être plus facile à appliquer qu’un calcul mathématique complexe, à condition que ses définitions soient explicites.

<div class="lesson-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" role="img" aria-labelledby="svgtitle-1 svdesc-1" width="960" height="380" style="max-width:100%;height:auto;display:block"><title id="svgtitle-1">Matrice impact urgence</title><desc id="svdesc-1">Matrice indicative pour qualifier la priorité de service.</desc><defs><marker id="arrow-1" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62d6ff"/></marker><marker id="arrowGreen-1" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62e6a7"/></marker><marker id="arrowAmber-1" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#ffc56b"/></marker><style>@keyframes dash{to{stroke-dashoffset:-30}}.flow,.flowg,.flowa{animation:dash 2.2s linear infinite}@media (prefers-reduced-motion: reduce){.flow,.flowg,.flowa{animation:none;stroke-dasharray:none}}</style></defs><rect fill="#090e16" x="0" y="0" width="960" height="380" rx="16"/><text x="28" y="30" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">La priorité vient de l’impact métier et de l’urgence — pas du volume de messages</text><text x="32" y="85" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Impact</text><text x="32" y="108" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Élevé</text><text x="32" y="284" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Faible</text><text x="440" y="360" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Urgence croissante →</text><rect x="155" y="58" width="208" height="70" rx="9" fill="#351d25" stroke="#ff8293" stroke-width="1.6"/><text x="259" y="87" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P1</text><text x="259" y="107" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Critique</text><rect x="380" y="58" width="208" height="70" rx="9" fill="#351d25" stroke="#ff8293" stroke-width="1.6"/><text x="484" y="87" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P1</text><text x="484" y="107" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Majeure</text><rect x="605" y="58" width="208" height="70" rx="9" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="709" y="87" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P2</text><text x="709" y="107" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Importante</text><rect x="155" y="146" width="208" height="70" rx="9" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="259" y="175" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P1/P2</text><text x="259" y="195" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Élevée</text><rect x="380" y="146" width="208" height="70" rx="9" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="484" y="175" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P2</text><text x="484" y="195" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Modérée</text><rect x="605" y="146" width="208" height="70" rx="9" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="709" y="175" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P3</text><text x="709" y="195" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Limitée</text><rect x="155" y="234" width="208" height="70" rx="9" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="259" y="263" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P2</text><text x="259" y="283" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">À évaluer</text><rect x="380" y="234" width="208" height="70" rx="9" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="484" y="263" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P3</text><text x="484" y="283" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Faible</text><rect x="605" y="234" width="208" height="70" rx="9" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="709" y="263" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">P3/P4</text><text x="709" y="283" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Faible</text><text x="259" y="331" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Urgence faible</text><text x="694" y="331" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Urgence forte</text><text x="825" y="82" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Exemples à</text><text x="825" y="98" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">adapter localement</text></svg>
</div>

**Exemple de définitions locales possibles :**

| Niveau | Exemple de critère | Réponse attendue |
|---|---|---|
| P1 / majeur | Service critique indisponible pour une large population, sécurité ou intégrité des données menacée | Déclaration immédiate, mobilisation de l’astreinte, coordination dédiée, communication régulière |
| P2 / élevé | Fonction métier importante dégradée, contournement partiel disponible | Priorité forte, propriétaire de service mobilisé, cadence de mise à jour définie |
| P3 / normal | Impact limité, groupe restreint, contournement raisonnable | File de traitement standard avec échéance selon SLA |
| P4 / faible | Question ou impact mineur non bloquant | Traitement planifié selon les règles du service |

Il doit être possible de **rehausser ou abaisser** le niveau à mesure que les preuves évoluent. Une panne localisée peut devenir majeure si elle menace un site critique ; inversement, une alerte initiale très inquiétante peut être déclassée si le service et les données sont confirmés sains. Toute réévaluation importante doit être horodatée et expliquée.

## 3. Cycle de vie d’un incident intermédiaire

Le flux représenté ci-dessous sépare la boucle d’intervention de la boucle d’apprentissage. La RCA n’a pas vocation à bloquer le retour au service.

<div class="lesson-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" role="img" aria-labelledby="svgtitle-2 svdesc-2" width="960" height="380" style="max-width:100%;height:auto;display:block"><title id="svgtitle-2">Cycle incident et RCA</title><desc id="svdesc-2">Cycle de gestion opérationnelle, puis boucle d’apprentissage après rétablissement.</desc><defs><marker id="arrow-2" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62d6ff"/></marker><marker id="arrowGreen-2" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62e6a7"/></marker><marker id="arrowAmber-2" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#ffc56b"/></marker><style>@keyframes dash{to{stroke-dashoffset:-30}}.flow,.flowg,.flowa{animation:dash 2.2s linear infinite}@media (prefers-reduced-motion: reduce){.flow,.flowg,.flowa{animation:none;stroke-dasharray:none}}</style></defs><rect fill="#090e16" x="0" y="0" width="960" height="380" rx="16"/><text x="28" y="30" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Du signal à l’apprentissage : deux boucles distinctes</text><rect x="26" y="75" width="148" height="76" rx="12" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="100.0" y="102" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Détection</text><text x="100.0" y="124" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Alerte / utilisateur</text><rect x="216" y="75" width="148" height="76" rx="12" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="290.0" y="102" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Qualification</text><text x="290.0" y="124" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Impact + urgence</text><rect x="406" y="75" width="148" height="76" rx="12" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="480.0" y="102" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Coordination</text><text x="480.0" y="124" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Rôles + hypothèses</text><rect x="596" y="75" width="148" height="76" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="670.0" y="102" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Rétablissement</text><text x="670.0" y="124" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Mitigation contrôlée</text><rect x="786" y="75" width="148" height="76" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="860.0" y="102" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Validation</text><text x="860.0" y="124" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Service fiable ?</text><path d="M174 113 H206" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-2)" class="flow"/><path d="M364 113 H396" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-2)" class="flow"/><path d="M554 113 H586" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-2)" class="flow"/><path d="M744 113 H776" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-2)" class="flow"/><rect x="626" y="213" width="250" height="68" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="751.0" y="240" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Incident résolu</text><text x="751.0" y="262" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Impact terminé et contrôlé</text><rect x="302" y="213" width="250" height="68" rx="12" fill="#261f3a" stroke="#b7a0ff" stroke-width="1.6"/><text x="427.0" y="240" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Revue / RCA</text><text x="427.0" y="262" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Seulement après stabilisation</text><path d="M860 151 V184 H751 V203" fill="none" stroke="#62e6a7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowGreen-2)" class="flowg"/><path d="M626 247 H562" fill="none" stroke="#62e6a7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowGreen-2)" class="flowg"/><path d="M302 247 H100 V161" fill="none" stroke="#ffc56b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowAmber-2)" class="flowa"/><text x="29" y="330" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Boucle opérationnelle : protéger les utilisateurs, restaurer le service, communiquer.</text><text x="29" y="353" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Boucle d’apprentissage : expliquer les conditions, assigner des actions et vérifier leur efficacité.</text></svg>
</div>

### 3.1 Détection et création d’un enregistrement

Les sources possibles sont la supervision, un centre de service, un utilisateur, un fournisseur, une alerte de sécurité ou une équipe technique. Quel que soit le canal d’entrée, l’objectif est de converger vers un enregistrement de référence qui contient au minimum :

1. identifiant unique et heure de détection ;
2. service ou CI concerné, environnement et localisation ;
3. symptôme observable, message d’erreur et fréquence ;
4. population ou fonctions affectées ;
5. heure de début estimée et niveau de confiance ;
6. changements récents, dépendances et événements associés ;
7. priorité initiale, propriétaire et canal de communication.

Un rapport tel que « le réseau est cassé » n’est pas exploitable. Reformule : « depuis 09 h 12, 18 utilisateurs du site B ne peuvent plus atteindre l’application RH via HTTPS ; DNS résout le nom, mais les connexions TCP expirent ; le site A fonctionne ». La deuxième version permet de choisir des tests ciblés.

Ne suppose pas que l’heure du ticket est l’heure de début de la panne. Inscris séparément l’heure du premier symptôme connu, celle de détection, celle du signalement et celle de création du ticket.

### 3.2 Qualification et regroupement

Vérifie si plusieurs tickets décrivent le même incident. Le regroupement aide à voir l’étendue de la panne et à éviter que plusieurs équipes exécutent des changements incompatibles. Conserve les tickets enfants ou les références originales pour respecter la traçabilité.

Regroupe lorsque les symptômes, le périmètre, la fenêtre temporelle et les preuves suggèrent un événement commun. Ne fusionne pas mécaniquement tous les tickets qui mentionnent « lenteur » : plusieurs causes sans lien peuvent coexister.

Questions de triage :

- Quel service métier est réellement impacté ?
- Le problème touche-t-il un site, un VLAN, un groupe d’utilisateurs, une région ou tous les clients ?
- Le service est-il indisponible, lent, instable ou incorrect ?
- Des transactions sont-elles perdues, dupliquées ou retardées ?
- Une question de confidentialité, d’intégrité ou de sécurité est-elle plausible ?
- Le symptôme suit-il un déploiement, une modification, une expiration de certificat ou une panne de dépendance ?
- Existe-t-il un contournement sûr et autorisé ?

### 3.3 Diagnostic guidé par hypothèses

Une bonne investigation ne consiste pas à exécuter toutes les commandes disponibles. Elle consiste à formuler une hypothèse falsifiable, choisir une observation qui la confirme ou la réfute et conserver le résultat.

**Format de travail utile :**

- Hypothèse : « Les nouvelles connexions échouent car le pool SQL est épuisé. »
- Indice attendu : connexions actives au plafond, erreurs de pool et attente au niveau applicatif.
- Test : consulter les métriques du pool et les journaux sur la fenêtre correspondante.
- Résultat : « plafond atteint de 09 h 04 à 09 h 13 ; les erreurs augmentent avec les demandes ». 
- Conclusion provisoire : « hypothèse renforcée, mais il reste à déterminer pourquoi les connexions ne sont pas libérées ». 
- Prochaine étape : vérifier le cycle de vie des connexions et les changements du déploiement.

Évite le biais de confirmation. Une alerte CPU à 95 % peut être la conséquence d’une boucle de retry déclenchée par une dépendance en panne, plutôt que la cause initiale. Il faut reconstituer la chaîne temporelle.

### 3.4 Mitigation, rétablissement et résolution

Distingue les notions suivantes dans les tickets et les communications :

- **Mitigation :** action destinée à stopper la propagation ou réduire immédiatement l’impact.
- **Contournement :** solution alternative temporaire pour fournir un service acceptable.
- **Rétablissement :** service redevenu utilisable selon les critères retenus.
- **Correction définitive :** modification qui supprime ou réduit la cause et a été vérifiée.
- **Clôture administrative :** enregistrement terminé après les vérifications et validations requises.

Une mitigation doit tenir compte du risque de changement. Avant une action, indique la portée, la personne qui l’exécute, le bénéfice attendu, les risques, les critères de succès et la condition de rollback. Pendant une panne majeure, il faut parfois agir rapidement, mais cela ne signifie pas agir sans contrôle.

Exemple : revenir à la version applicative précédente peut rétablir le service. Il faut encore vérifier les transactions en attente, surveiller les erreurs, notifier les utilisateurs et ouvrir une analyse pour comprendre pourquoi la version fautive a passé les validations.

### 3.5 Vérification après rétablissement

Un seul test réussi n’établit pas que le service est stable. Utilise plusieurs signaux adaptés au service :

- tests synthétiques ou transaction métier de bout en bout ;
- taux de succès et latence ;
- journaux d’erreur et files de traitement ;
- métriques des dépendances ;
- confirmation d’un utilisateur ou d’un représentant métier ;
- absence de réapparition pendant une fenêtre définie.

Définis cette fenêtre selon le rythme du service. Un système de facturation utilisé seulement à certaines heures ne peut pas être validé exactement comme une API à fort trafic. Notifie que le service est rétabli, mais précise lorsqu’une enquête ou une surveillance renforcée continue.

## 4. Gestion d’incident majeur

Un incident majeur se caractérise par un impact ou un risque qui justifie une coordination spéciale : disponibilité critique, propagation entre services, menace sur les données, forte visibilité ou capacité de réponse ordinaire insuffisante. Le seuil exact est local. N’attends pas une certitude technique complète pour déclarer un incident majeur si l’impact et l’incertitude rendent la réponse normale inadaptée.

### 4.1 Déclencheurs de déclaration

Écris des critères préalables, par exemple :

- service essentiel totalement indisponible ;
- plusieurs services ou sites affectés ;
- risque de perte, corruption ou divulgation de données ;
- impact client ou financier au-dessus d’un seuil défini ;
- absence de contournement sûr ;
- incident qui continue à s’étendre ;
- réponse normale incapable de coordonner les équipes dans le délai attendu.

### 4.2 Rôles à déléguer

<div class="lesson-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" role="img" aria-labelledby="svgtitle-3 svdesc-3" width="960" height="380" style="max-width:100%;height:auto;display:block"><title id="svgtitle-3">Rôles de réponse incident</title><desc id="svdesc-3">Schéma des rôles de coordination, opérations, communication et documentation.</desc><defs><marker id="arrow-3" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62d6ff"/></marker><marker id="arrowGreen-3" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62e6a7"/></marker><marker id="arrowAmber-3" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#ffc56b"/></marker><style>@keyframes dash{to{stroke-dashoffset:-30}}.flow,.flowg,.flowa{animation:dash 2.2s linear infinite}@media (prefers-reduced-motion: reduce){.flow,.flowg,.flowa{animation:none;stroke-dasharray:none}}</style></defs><rect fill="#090e16" x="0" y="0" width="960" height="380" rx="16"/><text x="28" y="30" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Une coordination centralisée, une exécution technique déléguée</text><rect x="352" y="57" width="256" height="72" rx="12" fill="#261f3a" stroke="#b7a0ff" stroke-width="1.6"/><text x="480.0" y="84" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Incident Commander</text><text x="480.0" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Priorités, décision, délégation</text><rect x="47" y="184" width="250" height="83" rx="12" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="172.0" y="211" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Lead opérations</text><text x="172.0" y="233" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Diagnostic et changements contrôlés</text><text x="172.0" y="255" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Une équipe modifie la production</text><rect x="355" y="184" width="250" height="83" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="480.0" y="211" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Lead communication</text><text x="480.0" y="233" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Utilisateurs, direction, statut</text><text x="480.0" y="255" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Messages à cadence définie</text><rect x="663" y="184" width="250" height="83" rx="12" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="788.0" y="211" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Scribe / planning</text><text x="788.0" y="233" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Chronologie, actions, dépendances</text><text x="788.0" y="255" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Préparer le relais et le suivi</text><path d="M480 129 V151 H172 V174" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-3)" class="flow"/><path d="M480 151 V174" fill="none" stroke="#62e6a7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowGreen-3)" class="flowg"/><path d="M480 151 H788 V174" fill="none" stroke="#ffc56b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowAmber-3)" class="flowa"/><rect x="80" y="302" width="800" height="48" rx="10" fill="#111b29" stroke="#2a4058" stroke-width="1.5"/><text x="480" y="322" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Experts techniques et propriétaires de service apportent preuves et options.</text><text x="480" y="339" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Le Commandant conserve la vue globale ; les rôles peuvent être cumulés si l’équipe est petite.</text></svg>
</div>

Dans une petite équipe, une personne peut tenir plusieurs rôles. Lorsqu’un incident devient majeur, séparer les fonctions réduit la charge cognitive et évite que le responsable technique passe tout son temps à répondre aux messages au lieu de résoudre le problème.

**Incident Commander / coordinateur :** tient la vue d’ensemble, fixe les priorités, assigne les rôles, arbitre les options et s’assure que les décisions sont consignées. Il n’est pas nécessairement le meilleur expert technique.

**Lead opérations :** dirige le diagnostic et les interventions. Il veille à ce qu’une seule équipe ou un ensemble coordonné de personnes modifie la production, selon les règles du service, afin d’éviter des changements contradictoires.

**Lead communication :** prépare les mises à jour internes et externes, vérifie que les messages correspondent aux faits et tient une cadence. Il ne publie pas de cause non confirmée comme si elle était établie.

**Scribe / planning :** conserve la chronologie, les décisions, les hypothèses, les actions et les dépendances ; prépare le relais et suit les tâches différées.

**Experts et propriétaires de service :** fournissent des preuves et proposent des options techniques. Ils doivent expliciter les risques et les critères de réussite, pas seulement recommander « redémarrer ».

### 4.3 Règles de fonctionnement d’une cellule incident

1. Déclarer le canal ou le pont principal, et interdire les investigations parallèles non coordonnées sur la production.
2. Attribuer les rôles et publier l’identifiant du ticket maître.
3. Énoncer l’impact connu, les inconnues et l’objectif immédiat.
4. Maintenir une liste courte des hypothèses, chacune avec un propriétaire et un test.
5. Annoncer les décisions à l’équipe entière et les consigner.
6. Exiger une fenêtre de test et un critère de succès avant les changements risqués.
7. Fixer une cadence de mise à jour et respecter l’heure annoncée, même pour dire qu’il n’y a pas de changement significatif.
8. Préparer le transfert de commandement si le coordinateur doit être remplacé.
9. Quand l’impact baisse, réévaluer la sévérité et réduire progressivement la cellule.
10. Après stabilisation, préserver les preuves et organiser la revue.

### 4.4 Communication de crise

Une communication utile répond à cinq questions : que se passe-t-il, qui est affecté, quel est l’impact connu, que fait l’équipe, quand aura lieu la prochaine mise à jour ?

**Exemple de message initial :**

> **Incident INC-204 — Portail client dégradé**  
> Depuis 10 h 14, certains utilisateurs rencontrent des erreurs lors de la connexion. L’équipe technique est mobilisée. La cause n’est pas confirmée à ce stade. Une mise à jour sera publiée à 10 h 30, ou plus tôt si la situation évolue.

**Exemple de mise à jour :**

> Le trafic a été basculé vers les instances saines à 10 h 24. Le taux de succès remonte, mais nous poursuivons la vérification des sessions et transactions en attente. Prochaine mise à jour à 10 h 45.

**Exemple de rétablissement :**

> Le portail répond normalement depuis 10 h 41 et les tests de connexion et de consultation réussissent. La surveillance renforcée se poursuit. Une revue technique sera menée afin d’identifier les facteurs contributifs et les actions préventives.

N’annonce pas « tout est réparé » si seul un test technique est positif. N’affiche pas de secrets, données personnelles, détails d’exploitation sensibles ou informations de sécurité qui faciliteraient une attaque. Pour un incident de cybersécurité, applique les procédures dédiées et la chaîne de signalement adaptée.

### 4.5 Transfert de commandement

Un transfert doit être explicite, pas une simple déconnexion. Le nouveau responsable reçoit : état et impact actuels, sévérité, rôles, actions actives, hypothèses non testées, décisions prises et raisons, principaux risques, prochaines échéances, messages déjà diffusés et critères de rétablissement. Le cédant demande au repreneur de reformuler les points critiques pour confirmer la compréhension.

## 5. SLA, SLO et indicateurs

Un **SLA** est un engagement de service établi avec un client ou un utilisateur. Un **SLO** est un objectif de fiabilité défini pour mesurer un service. Les **OLA** ou accords opérationnels internes peuvent préciser comment les équipes se soutiennent. Ces notions ne sont pas interchangeables et les définitions exactes dépendent du contrat.

### 5.1 Définir les horloges correctement

Un indicateur de délai doit préciser son point de départ, son point d’arrivée, les pauses autorisées et le calendrier d’application. « Réponse en 30 minutes » peut signifier première réponse humaine, prise en charge par un groupe qualifié, ou début d’une action de mitigation : ces événements ne sont pas identiques.

Mesure séparément :

- **MTTD** (Mean Time to Detect) : délai moyen entre le début estimé et la détection ;
- **MTTA** (Mean Time to Acknowledge) : délai moyen entre l’alerte et son accusé de prise en charge ;
- **MTTR** : acronyme ambigu selon l’organisation — il peut désigner le temps de réparation, de rétablissement ou de résolution. Définis-le explicitement dans le tableau de bord ;
- **Temps de mitigation** : délai jusqu’à la mesure qui réduit l’impact ;
- **Temps de rétablissement** : délai jusqu’au retour vérifié du service ;
- **Récurrence** : nombre d’incidents similaires durant une période définie ;
- **Taux de réouverture** : tickets rouverts après clôture / tickets clôturés sur le périmètre choisi ;
- **Âge des actions RCA** : temps écoulé depuis la création d’une action sans preuve de validation.

La moyenne peut masquer de très longues pannes. Complète-la avec médiane, 90e/95e percentile, distribution par priorité et impact métier. Précise toujours la période, la population et le nombre de tickets inclus.

### 5.2 Éviter les indicateurs qui donnent de mauvaises incitations

Un objectif tel que « fermer un maximum de tickets » peut pousser à fermer trop tôt ou à fragmenter les incidents. Un MTTR faible obtenu en classant prématurément des tickets comme rétablis n’est pas une amélioration. Associe les métriques de vitesse à des mesures de qualité : réouverture, récurrence, confirmation utilisateur, intégrité des données et efficacité des actions correctives.

Ne compare pas deux équipes sans normaliser le contexte : criticité des services, horaires, volume de tickets, complexité, couverture d’astreinte et outils. Les indicateurs servent d’abord à améliorer le système, pas à désigner des coupables.

## 6. Préparer une RCA rigoureuse

La **Root Cause Analysis (RCA)** cherche à identifier les causes et conditions qui ont rendu l’incident possible, puis à sélectionner des actions qui réduisent la probabilité de répétition ou son impact. Une RCA est une argumentation fondée sur des preuves, pas un récit qui choisit après coup un coupable ou une explication séduisante.

### 6.1 Quand lancer une RCA formelle ?

Définis les critères à l’avance. Exemples : incident majeur, interruption dépassant le seuil défini, perte ou corruption de données, intervention d’urgence, incident répété, détection tardive, contournement risqué ou demande d’une partie prenante. Les incidents mineurs peuvent être suivis par une analyse légère ; le niveau d’effort devrait être proportionnel au risque et à l’apprentissage attendu.

### 6.2 Les termes d’une chaîne causale

- **Symptôme :** observation visible, par exemple HTTP 503.
- **Déclencheur :** événement qui démarre la séquence, par exemple un déploiement ou une coupure électrique.
- **Cause immédiate :** mécanisme direct, par exemple le pool de connexions atteint son plafond.
- **Facteur contributif :** condition qui rend l’incident plus probable ou plus grave, par exemple des délais de retry trop longs.
- **Cause systémique/actionnable :** défaut dans l’architecture, le processus, la validation, la supervision ou les contrôles, qu’une action peut modifier pour prévenir la classe d’incidents.
- **Facteur d’amplification :** élément qui augmente l’impact, par exemple l’absence de limite de concurrence ou un retry synchronisé.
- **Défense manquante :** test, alerte, garde-fou, redondance ou procédure qui aurait pu empêcher, détecter ou limiter l’incident.

Il existe parfois plusieurs causes nécessaires. Un déclencheur isolé n’explique pas pourquoi le système n’a pas résisté, pourquoi la détection a tardé et pourquoi le rétablissement a duré aussi longtemps.

<div class="lesson-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="svgtitle-4 svdesc-4" width="960" height="350" style="max-width:100%;height:auto;display:block"><title id="svgtitle-4">Chaîne causale RCA</title><desc id="svdesc-4">Exemple illustratif de chaîne causale et de questions de validation.</desc><defs><marker id="arrow-4" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62d6ff"/></marker><marker id="arrowGreen-4" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62e6a7"/></marker><marker id="arrowAmber-4" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#ffc56b"/></marker><style>@keyframes dash{to{stroke-dashoffset:-30}}.flow,.flowg,.flowa{animation:dash 2.2s linear infinite}@media (prefers-reduced-motion: reduce){.flow,.flowg,.flowa{animation:none;stroke-dasharray:none}}</style></defs><rect fill="#090e16" x="0" y="0" width="960" height="350" rx="16"/><text x="28" y="30" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Distinguer symptôme, mécanisme immédiat et cause actionnable</text><rect x="32" y="72" width="155" height="78" rx="12" fill="#351d25" stroke="#ff8293" stroke-width="1.6"/><text x="109.5" y="99" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Symptôme</text><text x="109.5" y="121" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Portail indisponible</text><rect x="223" y="72" width="155" height="78" rx="12" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="300.5" y="99" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Mécanisme</text><text x="300.5" y="121" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Pool épuisé</text><rect x="414" y="72" width="155" height="78" rx="12" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="491.5" y="99" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Condition</text><text x="491.5" y="121" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Retry sans limite</text><rect x="605" y="72" width="155" height="78" rx="12" fill="#261f3a" stroke="#b7a0ff" stroke-width="1.6"/><text x="682.5" y="99" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Défense absente</text><text x="682.5" y="121" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Pas de budget de retry</text><rect x="796" y="72" width="155" height="78" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="873.5" y="99" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Action système</text><text x="873.5" y="121" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Timeout + plafond + test</text><path d="M187 111 H215" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-4)" class="flow"/><path d="M378 111 H406" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-4)" class="flow"/><path d="M569 111 H597" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-4)" class="flow"/><path d="M760 111 H788" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-4)" class="flow"/><rect x="40" y="205" width="880" height="106" rx="14" fill="#111b29" stroke="#2a4058" stroke-width="1.5"/><text x="64" y="231" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">À chaque « pourquoi ? »</text><text x="64" y="255" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">• Quelle preuve soutient le lien causal ?</text><text x="64" y="276" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">• Quelle autre explication est plausible ?</text><text x="520" y="255" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">• Où agir pour réduire une classe d’incidents ?</text><text x="520" y="276" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">• Comment tester que l’action fonctionne ?</text></svg>
</div>

### 6.3 Construire une chronologie probante

<div class="lesson-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="svgtitle-5 svdesc-5" width="960" height="360" style="max-width:100%;height:auto;display:block"><title id="svgtitle-5">Chronologie incident</title><desc id="svdesc-5">Chronologie illustrative avec preuves, actions et rétablissement.</desc><defs><marker id="arrow-5" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62d6ff"/></marker><marker id="arrowGreen-5" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62e6a7"/></marker><marker id="arrowAmber-5" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#ffc56b"/></marker><style>@keyframes dash{to{stroke-dashoffset:-30}}.flow,.flowg,.flowa{animation:dash 2.2s linear infinite}@media (prefers-reduced-motion: reduce){.flow,.flowg,.flowa{animation:none;stroke-dasharray:none}}</style></defs><rect fill="#090e16" x="0" y="0" width="960" height="360" rx="16"/><text x="28" y="30" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Une chronologie sépare les faits confirmés des hypothèses</text><path d="M70 130 H894" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-5)" class="flow"/><circle cx="90" cy="130" r="7" fill="#62d6ff"/><rect x="18" y="163" width="144" height="84" rx="10" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="90" y="185" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">09:02</text><text x="90" y="207" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Déploiement</text><text x="90" y="226" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Fait : version v42</text><circle cx="286" cy="130" r="7" fill="#62d6ff"/><rect x="214" y="163" width="144" height="84" rx="10" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="286" y="185" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">09:04</text><text x="286" y="207" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Latence ↑</text><text x="286" y="226" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Métrique &gt; seuil</text><circle cx="482" cy="130" r="7" fill="#62d6ff"/><rect x="410" y="163" width="144" height="84" rx="10" fill="#351d25" stroke="#ff8293" stroke-width="1.6"/><text x="482" y="185" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">09:06</text><text x="482" y="207" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Alerte</text><text x="482" y="226" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Premiers tickets</text><circle cx="678" cy="130" r="7" fill="#62d6ff"/><rect x="606" y="163" width="144" height="84" rx="10" fill="#261f3a" stroke="#b7a0ff" stroke-width="1.6"/><text x="678" y="185" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">09:10</text><text x="678" y="207" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Rollback</text><text x="678" y="226" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Début mitigation</text><circle cx="875" cy="130" r="7" fill="#62d6ff"/><rect x="803" y="163" width="144" height="84" rx="10" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="875" y="185" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">09:16</text><text x="875" y="207" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Retour normal</text><text x="875" y="226" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Mesures stables</text><rect x="60" y="283" width="840" height="48" rx="10" fill="#111b29" stroke="#2a4058" stroke-width="1.5"/><text x="480" y="303" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Une corrélation temporelle oriente l’enquête ; elle ne prouve pas seule la causalité.</text><text x="480" y="320" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#9db2c8">Conserver horaires, fuseaux, source, incertitude et lien vers la preuve.</text></svg>
</div>

La chronologie aide à séparer les faits et les suppositions. Pour chaque entrée, note l’heure, le fuseau, la source, l’auteur ou le système, l’observation, la décision qui en découle et le degré de confiance. Un événement observé dans les journaux n’est pas forcément l’heure de la cause : les horloges peuvent être décalées, les métriques agrégées et les alertes retardées.

**Bon format :** « 09:04:12 UTC+1 — métrique du pool atteint 100 % sur deux instances (tableau de bord X, lien Y). »  
**Format faible :** « vers 9 h, la base était probablement saturée ».

Préserve les journaux avant rotation, les identifiants de requête, versions de configuration, commits et changements. Respecte la politique de conservation, les accès nécessaires, la confidentialité et, en cas d’incident de sécurité, les exigences de préservation de preuves. Ne copie pas de données personnelles ou secrets dans un rapport largement partagé.

### 6.4 Technique des 5 pourquoi

Commence par un effet vérifiable et demande pourquoi il s’est produit. Chaque réponse doit être étayée et ouvrir une question plus précise. Cinq n’est pas un nombre magique : il faut arrêter lorsque la chaîne devient suffisamment actionnable, ou signaler explicitement l’incertitude.

**Exemple : service de rapports indisponible après une hausse du trafic**

1. Pourquoi la génération échoue-t-elle ? Parce que les workers n’obtiennent plus de connexion à la base.
2. Pourquoi le pool est-il épuisé ? Parce que les connexions actives atteignent le plafond pendant les pics.
3. Pourquoi restent-elles occupées trop longtemps ? Parce que certaines requêtes analytiques dépassent le délai attendu et que les tentatives supplémentaires gardent des ressources.
4. Pourquoi les retries amplifient-ils la pression ? Parce qu’ils n’ont pas de budget global, de backoff adéquat ni de limite de concurrence.
5. Pourquoi ces contrôles manquent-ils ? Parce que le modèle de charge et les tests de panne n’étaient pas intégrés aux critères de mise en production.

Les niveaux 4 et 5 sont des hypothèses à confirmer par le code, la configuration et les pratiques de livraison. Il serait incorrect de déclarer la RCA terminée simplement parce que cinq questions ont été écrites.

### 6.5 Diagramme d’Ishikawa / causes contributives

Le diagramme de cause à effet aide à organiser les pistes. Catégories possibles : personnes/compétences, processus, technologie, données/mesure, dépendances externes, environnement et gouvernance. Ce sont des familles de recherche, pas des conclusions. La présence de « personnes » dans le diagramme ne doit pas servir de raccourci vers une faute individuelle.

Exemple, incident DHCP dans une agence :

- **Technologie :** portée IP presque épuisée, relay mal configuré, service indisponible ;
- **Processus :** croissance des appareils non anticipée, revue de changement incomplète ;
- **Détection :** seuil d’alerte absent sur le taux d’utilisation de la portée ;
- **Dépendances :** liaison WAN instable vers le serveur central ;
- **Environnement :** nouveau réseau Wi-Fi invité ou nouveau lot d’appareils ;
- **Procédure :** runbook incomplet pour distinguer une panne DHCP d’une panne DNS.

Ensuite, relie chaque cause potentielle à une preuve ou un test. Les catégories sans preuve doivent rester des pistes à investiguer.

### 6.6 Arbre causal et causes multiples

Un incident peut se produire parce que plusieurs conditions se rencontrent : un déploiement introduit un défaut, la supervision ne détecte pas rapidement la dégradation et la redondance ne prend pas le relais. Un arbre causal permet de représenter des conditions nécessaires conjointement ou des chemins alternatifs. Évite les explications monocausales lorsque les preuves décrivent un système complexe.

Formule les liens explicitement : « La saturation du pool a provoqué des erreurs de connexion » est une relation testable. « L’équipe n’a pas été assez attentive » n’est ni précise, ni mesurable, ni une correction système.

### 6.7 Hypothèses, preuves et confiance

Pour chaque hypothèse, conserve :

| Champ | Exemple |
|---|---|
| Hypothèse | Un changement de configuration a réduit la capacité du pool |
| Prédiction | Le plafond effectif diffère de la valeur précédente |
| Preuve recherchée | Diff de configuration, historique de déploiement, métriques |
| Résultat | Plafond passé de 120 à 40 connexions à 09:01 |
| Alternatives | Hausse de charge, fuite de connexions, panne de la dépendance |
| Conclusion | Facteur fortement étayé ; vérifier le rôle du volume de requêtes |
| Action associée | Test automatique de capacité et validation du paramètre |

Utilise des niveaux qualitatifs (« confirmé », « fortement étayé », « plausible », « non confirmé ») uniquement si leurs critères sont expliqués. N’invente pas de pourcentage de confiance précis sans modèle approprié.

## 7. Preuves, journaux et sécurité de l’investigation

Une RCA robuste combine plusieurs sources : télémétrie, journaux applicatifs, traces distribuées, métriques d’infrastructure, événements de changement, retours des utilisateurs, journaux du fournisseur et captures réseau. Aucune source n’est parfaite. Vérifie la synchronisation horaire, les échantillonnages, l’échantillonnage de traces, la rétention, les trous de données et les différences d’environnement.

### 7.1 Collecter sans détruire la preuve

- Exporter ou figer les plages de logs avant expiration si cela est autorisé.
- Conserver la version de configuration et le commit précis en cause.
- Noter les commandes exécutées, l’identité du compte opérationnel et l’heure.
- Éviter les redémarrages ou nettoyages qui effacent l’état diagnostique tant que la conservation n’est pas jugée nécessaire ou que le risque de continuer est supérieur.
- Pour une situation de cybersécurité, suivre les procédures de sécurité et de conservation des preuves, limiter les accès et ne pas mener d’expérimentation improvisée sur un système potentiellement compromis.
- Masquer les identifiants, tokens, secrets, données personnelles et contenus clients dans les documents de revue.

### 7.2 Changement récent : indice, pas verdict

Le fait qu’un incident survienne juste après un changement fournit une piste forte, pas une preuve absolue. Vérifie le lien technique : différence de configuration, chemin de requête, version, métriques avant/après, test contrôlé si possible et comportement après rollback. Un changement peut exposer une faiblesse préexistante plutôt que la créer de zéro.

### 7.3 Problèmes de dépendances

Lorsqu’un fournisseur ou service interne est impliqué, documente le contrat et les attentes raisonnables : disponibilité, latence, limites, délais, modes dégradés et alertes. Si la dépendance fonctionne dans ses objectifs mais que ton service échoue, la résilience du service consommateur doit être étudiée. Si la dépendance dépasse ses limites annoncées ou convenues, le problème d’intégration, de contrat et de gestion du fournisseur doit aussi être traité. Ne réduis pas automatiquement la RCA à « le fournisseur est tombé ».

## 8. Plan d’actions correctives et préventives (CAPA)

Une RCA n’a de valeur opérationnelle que si les enseignements sont traduits en changements vérifiables. Un rapport sans action, propriétaire et suivi ne réduit pas le risque de manière fiable.

<div class="lesson-diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 350" role="img" aria-labelledby="svgtitle-6 svdesc-6" width="960" height="350" style="max-width:100%;height:auto;display:block"><title id="svgtitle-6">Actions RCA et efficacité</title><desc id="svdesc-6">Cycle de suivi des actions de mitigation, prévention et détection.</desc><defs><marker id="arrow-6" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62d6ff"/></marker><marker id="arrowGreen-6" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#62e6a7"/></marker><marker id="arrowAmber-6" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#ffc56b"/></marker><style>@keyframes dash{to{stroke-dashoffset:-30}}.flow,.flowg,.flowa{animation:dash 2.2s linear infinite}@media (prefers-reduced-motion: reduce){.flow,.flowg,.flowa{animation:none;stroke-dasharray:none}}</style></defs><rect fill="#090e16" x="0" y="0" width="960" height="350" rx="16"/><text x="28" y="30" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Une RCA utile se termine par des actions suivies et vérifiables</text><rect x="52" y="76" width="240" height="70" rx="12" fill="#351d25" stroke="#ff8293" stroke-width="1.6"/><text x="172.0" y="103" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Réduire l’exposition</text><text x="172.0" y="125" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Rollback, feature flag, limitation</text><rect x="360" y="76" width="240" height="70" rx="12" fill="#302517" stroke="#ffc56b" stroke-width="1.6"/><text x="480.0" y="103" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Réduire la récurrence</text><text x="480.0" y="125" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Fix, test, garde-fou technique</text><rect x="668" y="76" width="240" height="70" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="788.0" y="103" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Réduire l’impact</text><text x="788.0" y="125" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Détection, runbook, résilience</text><rect x="52" y="207" width="240" height="75" rx="12" fill="#102b3d" stroke="#62d6ff" stroke-width="1.6"/><text x="172.0" y="234" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Propriétaire + échéance</text><text x="172.0" y="256" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Une personne accountable</text><rect x="360" y="207" width="240" height="75" rx="12" fill="#261f3a" stroke="#b7a0ff" stroke-width="1.6"/><text x="480.0" y="234" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Preuve de complétion</text><text x="480.0" y="256" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Test, métrique, revue de code</text><rect x="668" y="207" width="240" height="75" rx="12" fill="#102d28" stroke="#62e6a7" stroke-width="1.6"/><text x="788.0" y="234" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f2f7ff">Validation d’efficacité</text><text x="788.0" y="256" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">Mesure avant / après</text><path d="M172 146 V194" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-6)" class="flow"/><path d="M480 146 V194" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-6)" class="flow"/><path d="M788 146 V194" fill="none" stroke="#62e6a7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowGreen-6)" class="flowg"/><path d="M292 244 H348" fill="none" stroke="#62d6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrow-6)" class="flow"/><path d="M600 244 H656" fill="none" stroke="#62e6a7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="7 8" marker-end="url(#arrowGreen-6)" class="flowg"/><text x="480" y="324" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#c5d4e5">« Fermer le ticket » n’est pas la même chose que « supprimer le risque de répétition ».</text></svg>
</div>

### 8.1 Types d’action

- **Correction :** supprimer ou modifier le défaut technique identifié.
- **Prévention :** empêcher cette classe de défaut de se reproduire (tests, garde-fous, limites, validations, revue de changement).
- **Détection :** réduire le délai entre l’apparition du problème et son signalement exact.
- **Mitigation / résilience :** limiter la portée ou la durée (redondance, isolation, dégradation gracieuse, rollback).
- **Récupération :** accélérer le retour à un état cohérent (restauration testée, procédures, contrôle d’intégrité).
- **Amélioration organisationnelle :** clarifier ownership, runbook, couverture d’astreinte, procédures fournisseurs ou formation.

Une bonne liste couvre les protections complémentaires. Si le correctif prend trois mois, une alerte plus rapide ou un contournement documenté peut réduire le risque entre-temps.

### 8.2 Formuler une action SMART et testable

Évite : « améliorer la supervision ». Préfère : « avant le 15 décembre, l’équipe Plateforme ajoute une alerte sur l’occupation du pool au-dessus de 85 % pendant cinq minutes, la teste sur l’environnement de préproduction et vérifie que l’astreinte reçoit l’alerte en moins de deux minutes ». L’exemple de date est fictif et doit être adapté.

Chaque action devrait préciser :

- le résultat attendu et le risque visé ;
- un responsable unique, même si plusieurs contributeurs participent ;
- une échéance réaliste ;
- la priorité et les dépendances ;
- un critère de complétion ;
- une méthode de validation d’efficacité ;
- le lien vers l’incident, la RCA et le système de suivi.

**Complétion n’est pas efficacité.** Le déploiement d’une alerte démontre que le changement a été livré ; un test d’alerte prouve qu’elle fonctionne ; les données d’incidents futurs aident à voir si elle améliore réellement la détection. Ces trois résultats sont distincts.

### 8.3 Prioriser le plan d’action

Classe les actions d’après le risque réduit, la fréquence des incidents, leur impact, le coût, la complexité et les dépendances. Une action simple et immédiate peut apporter une réduction de risque importante ; une refonte complète peut être nécessaire mais doit être planifiée et découpée.

| Action | Catégorie | Exemple de preuve de complétion |
|---|---|---|
| Limiter les retries | Prévention | Test de charge et de dépendance en panne réussi |
| Alerter sur l’épuisement du pool | Détection | Alerte testée de bout en bout |
| Activer une limitation de concurrence | Mitigation | Test de charge avec plafond confirmé |
| Améliorer le rollback | Récupération | Exercice chronométré avec validation métier |
| Ajouter un test de non-régression | Prévention | Test dans le pipeline, échec reproduit avant correctif et réussite après |

### 8.4 Gestion du backlog RCA

Revois régulièrement les actions ouvertes et les actions en retard. Si une action est bloquée, le propriétaire doit expliquer le blocage, proposer un plan alternatif et faire arbitrer le risque résiduel. Ne marque pas une action comme terminée simplement parce que la date est dépassée ou qu’un ticket lié a été fermé.

Les actions de RCA peuvent être liées à un backlog produit, une demande de changement ou un projet de fiabilité. Garde cependant un lien direct vers la RCA d’origine pour comprendre pourquoi l’action existe et quel résultat elle est censée produire.

## 9. Post-incident review et culture sans blâme

La revue post-incident (postmortem ou PIR selon l’organisation) vise à expliquer ce qui s’est passé, évaluer la réponse et convenir des actions. Elle doit être factuelle, respectueuse et orientée vers l’amélioration du système. « Sans blâme » ne signifie pas ignorer les responsabilités, les contrôles ou la conformité : cela signifie éviter d’expliquer une défaillance complexe par l’accusation d’une personne et rechercher les conditions qui ont influencé les décisions.

### 9.1 Agenda de revue (45 à 60 minutes, à adapter)

1. Rappeler l’objectif et l’absence de recherche de coupable.
2. Confirmer le périmètre d’impact et les données disponibles.
3. Parcourir la chronologie sans commencer par débattre des personnes.
4. Identifier le déclencheur, les causes immédiates et les facteurs contributifs étayés.
5. Étudier ce qui a bien fonctionné, ce qui a ralenti la détection ou le rétablissement et les circonstances favorables.
6. Décider des actions, des propriétaires, des échéances et des critères d’efficacité.
7. Déterminer les lecteurs autorisés et les informations qui doivent être masquées.
8. Publier la revue et inscrire les actions dans le système de suivi.

### 9.2 Questions productives

- Quelles informations l’équipe avait-elle au moment de prendre cette décision ?
- Quels signaux étaient disponibles et lesquels étaient invisibles ?
- Quels contrôles étaient en place ? Lesquels ont échoué ou n’existaient pas ?
- Qu’est-ce qui a permis au service de se rétablir ?
- Qu’aurait-on pu détecter plus tôt ?
- Qu’est-ce qui a étendu ou limité l’impact ?
- Quelle amélioration est susceptible d’empêcher la classe d’incidents plutôt que le seul cas exact ?

Évite « Pourquoi la personne a-t-elle fait une erreur ? » au profit de « Quelles informations et contraintes ont conduit à cette décision, et quel contrôle rendrait la bonne action plus probable ? »

### 9.3 Exemple de formulation neutre

- Accusatrice : « L’administrateur a oublié la vérification. »
- Factuelle et actionnable : « Le runbook de changement ne comporte pas de vérification automatisée de la résolution DNS après déploiement ; l’étape n’apparaît pas dans le pipeline et il n’existe pas d’alerte sur les échecs de résolution. »

La deuxième formulation n’efface pas l’action humaine ; elle décrit des facteurs qu’on peut examiner et modifier.

## 10. Cas pratique complet : application métier inaccessible

### Contexte

Une application de gestion des commandes devient inaccessible pour une partie des utilisateurs après un déploiement. Les premières remontées parlent d’une « panne réseau », mais les équipes n’ont pas encore établi la cause. Les exemples d’horaires ci-dessous sont fictifs.

### 10.1 Triage initial

- 09:02 : un déploiement applicatif commence.
- 09:05 : le taux d’erreur HTTP passe de 0,3 % à 18 %.
- 09:07 : le centre de service reçoit les premiers appels.
- 09:09 : la supervision signale une hausse de latence.
- 09:12 : le propriétaire du service confirme qu’un flux de commande critique échoue.

L’équipe ouvre un incident maître, collecte les identifiants des tickets similaires, évalue l’impact, vérifie s’il existe un risque sur l’intégrité des commandes et mobilise le propriétaire applicatif. En l’absence de preuve d’une panne réseau, elle ne désactive pas immédiatement tous les contrôles réseau ni ne redémarre tous les serveurs.

### 10.2 Hypothèses initiales

| Hypothèse | Test rapide | Résultat fictif | Suite |
|---|---|---|---|
| Résolution DNS défaillante | Résoudre le nom depuis plusieurs réseaux et vérifier les erreurs DNS | Résolution cohérente | Réduire la priorité de cette piste sans l’exclure partout |
| Filtrage réseau | Tester la connectivité et consulter les journaux de flux | Connexions TCP établies | Le réseau n’est pas totalement innocenté, mais le chemin de base fonctionne |
| Défaut dans la nouvelle version | Comparer taux d’erreur avant/après et vérifier logs applicatifs | Erreurs apparues juste après le déploiement | Hypothèse renforcée, recherche d’un mécanisme précis |
| Pool de base saturé | Examiner les métriques de connexion et attente SQL | Occupation à 100 %, erreurs de timeout | Indice fort d’un mécanisme immédiat |

### 10.3 Mitigation

L’équipe compare les risques d’un rollback, d’une limitation de trafic et d’un redémarrage. Le rollback est choisi car il est connu, réversible et cohérent avec la temporalité observée. Le lead opérations l’exécute selon la procédure de changement d’urgence. Le scribe note l’heure, la version, les métriques initiales et les résultats.

Après retour à la version précédente, les erreurs diminuent. L’équipe valide les transactions de bout en bout, vérifie les files en attente et surveille la latence pendant la fenêtre définie. Une communication indique le rétablissement et précise que l’analyse se poursuit.

### 10.4 RCA après stabilisation

L’analyse montre, dans cet exemple, que la nouvelle version a introduit des retries applicatifs plus agressifs. La baisse momentanée de réponses de la base a entraîné davantage de tentatives, accru la durée d’occupation des connexions et épuisé le pool. Les alertes signalaient les erreurs utilisateurs mais pas l’épuisement imminent du pool. Les tests de préproduction n’incluaient pas une dépendance volontairement lente ni la validation du comportement de retry.

**Conclusion causale étayée :** la version a modifié le comportement de retry ; sous une dépendance lente, cette logique a augmenté la concurrence et maintenu le pool à son plafond. L’absence de test de panne et de seuil d’alerte a augmenté respectivement la probabilité de livraison et le temps de détection. Le rapport évite de déclarer que « la base est la cause racine » : la base peut avoir subi une lenteur initiale, mais le mécanisme d’amplification et les défenses manquantes ont également contribué.

### 10.5 Actions de suivi

1. Ajouter un budget global de retry, un backoff avec jitter et une limite de concurrence — propriétaire : équipe applicative — succès : test de défaillance de la base sans épuisement du pool.
2. Ajouter une alerte sur l’occupation du pool et le temps d’attente — propriétaire : équipe plateforme — succès : alerte testée sur seuil et livraison à l’astreinte.
3. Étendre les tests de préproduction avec dépendance lente ou intermittente — propriétaire : QA/Dev — succès : pipeline échoue sur la version fautive et passe après correction.
4. Définir une procédure de rollback — propriétaire : service owner — succès : exercice mesuré et vérification du flux métier.
5. Revoir les métriques de succès — propriétaire : SRE/ops — succès : tableau de bord corrélé entre taux d’erreur, pool, retries et latence.

Ces actions couvrent prévention, détection et rétablissement. Leur clôture exige des preuves liées à chaque action, pas seulement une déclaration de leur propriétaire.

## 11. Modèle de ticket d’incident intermédiaire

Copie ce modèle dans ton outil ITSM et adapte les champs à ton service.

```text
ID / incident maître :
Titre orienté symptôme :
Service / CI / environnement :
Détecté à (date, heure, fuseau) :
Début estimé et niveau de confiance :
Rapporté par / canal :
Impact métier et population affectée :
Urgence / priorité / justification :
Symptômes observés et messages exacts :
Changements et événements récents :
Dépendances concernées :
Hypothèses ouvertes + propriétaire + prochain test :
Actions exécutées (heure, personne/rôle, portée, résultat) :
Mitigation / rollback et risque résiduel :
Critères de rétablissement :
Résultats de validation et fenêtre de surveillance :
Communication publiée et prochaine mise à jour :
Liens vers preuves, logs, dashboards, changes et tickets enfants :
État, propriétaire actuel et prochaine action :
Lien RCA / problème associé :
```

## 12. Modèle de rapport RCA / post-incident review

```text
Titre :
Identifiant de l’incident et services touchés :
Date, durée d’impact, fuseau :
Résumé destiné au métier :
Sévérité et raison du classement :
Impact mesuré (utilisateurs, transactions, régions, durée) :
Ce qui a fonctionné / ce qui a moins bien fonctionné :
Chronologie factuelle avec sources :
Déclencheur identifié (ou statut inconnu) :
Cause immédiate :
Facteurs contributifs :
Défenses absentes ou inefficaces :
Hypothèses testées et preuves :
Incertitudes restantes :
Pourquoi la détection et la mitigation ont pris ce temps :
Mesures immédiates et risques résiduels :
Actions correctives/préventives : propriétaire, échéance, priorité,
critère de complétion et preuve d’efficacité pour chacune :
Leçons réutilisables et documentation mise à jour :
Approbation / lecteurs / restrictions de confidentialité :
Date de révision de l’efficacité des actions :
```

### Critères de qualité d’un rapport

Un lecteur absent de la crise doit comprendre ce qui était cassé, qui ou quoi a été affecté, comment l’équipe a réagi, quelle cause est soutenue par les preuves et quelles actions vont réduire le risque. Un rapport n’a pas besoin d’être long pour être bon, mais il doit être explicite sur les faits et les incertitudes.

## 13. Tableau de pilotage des incidents et RCA

Un tableau de bord intermédiaire peut inclure :

| Mesure | Définition à formaliser | Question d’amélioration |
|---|---|---|
| MTTD | Début estimé → détection | Quels incidents sont détectés par les utilisateurs avant la supervision ? |
| MTTA | Alerte → prise en charge reconnue | L’astreinte est-elle joignable et les alertes actionnables ? |
| Temps de rétablissement | Détection ou déclaration → validation du service, selon définition locale | Quelle phase prend le plus de temps ? |
| Incidents répétés | Incidents de même classe sur période donnée | Les actions précédentes sont-elles efficaces ? |
| RCA en retard | RCA non approuvées après l’échéance | Manque-t-il du temps, des preuves ou un responsable ? |
| Actions ouvertes/échues | État et âge des actions | Les risques restent-ils sans réduction ? |
| Taux de réouverture | Tickets rouverts selon une définition stable | La vérification de rétablissement est-elle suffisante ? |
| Qualité des données | Complétude des champs critiques et horodatages | Peut-on expliquer la chronologie sans conjecture ? |

Interprète les tendances et les cas importants, pas seulement le score global. Une amélioration de MTTD peut venir de meilleures alertes, mais aussi d’une modification de la méthode de mesure. Documente les changements de calcul pour préserver la comparabilité.

## 14. Gouvernance légère : responsabilités et décisions

Une matrice RACI (Responsible, Accountable, Consulted, Informed) clarifie les responsabilités, mais ne remplace pas une procédure d’urgence. Pour chaque activité, désigne qui exécute, qui rend compte du résultat, qui doit être consulté et qui doit être informé.

Exemple d’attribution :

| Activité | Service Desk | Incident Commander | Ops / spécialiste | Service Owner | Comms |
|---|---|---|---|---|---|
| Enregistrer / regrouper les tickets | R | A | C | I | I |
| Fixer la coordination d’un incident majeur | I | A/R | C | C | C |
| Exécuter un changement technique | I | C | R | A selon gouvernance | I |
| Valider le service métier | C | C | R technique | A/R métier | I |
| Publier la mise à jour | I | A | C | C | R |
| Piloter la RCA | C | C | R contributeur | A pour le service | I |
| Accepter le risque résiduel | I | C | C | A selon délégation | I |

Les rôles peuvent varier par entreprise. L’important est d’éviter les zones grises : qui autorise un changement, qui valide un flux métier, qui communique et qui accepte le risque résiduel.

### Contrôle des changements d’urgence

Un changement d’urgence reste un changement : il doit avoir un responsable, une raison, une portée, une méthode d’exécution, un contrôle de risque et une trace. Le processus peut être accéléré, mais les exigences essentielles ne disparaissent pas. Organise une revue rétrospective dès que possible et convertis les contrôles manuels répétés en tests automatisés lorsqu’ils sont adaptés.

## 15. Pièges fréquents à éviter

1. **Chercher la cause complète pendant que le service reste en panne.** Réduis d’abord l’impact avec une action sûre et réversible.
2. **Confondre corrélation et causalité.** Un déploiement juste avant la panne est un indice, pas une preuve complète.
3. **S’arrêter au composant qui a échoué.** Une base indisponible peut être un symptôme d’épuisement provoqué par les appels en amont.
4. **Trouver un responsable humain au lieu d’une explication systémique.** Étudie procédures, information disponible, contrôles, interfaces et pression temporelle.
5. **Créer trop d’actions vagues.** Mieux vaut quelques actions précises et testées que vingt recommandations sans propriétaire.
6. **Clôturer avant validation métier.** Distingue retour technique, intégrité des données et utilisabilité métier.
7. **Laisser la RCA sans suivi.** Chaque action doit avoir une échéance, un propriétaire et une preuve.
8. **Mesurer le MTTR sans définition.** Documente les bornes et la méthode de calcul.
9. **Oublier la confidentialité.** Masque tokens, données personnelles et détails exploitables dans les rapports partagés.
10. **Conserver uniquement le récit du plus expérimenté.** Croise les témoignages avec les logs, les métriques et les changements.
11. **Changer trop de choses à la fois.** Quand le risque le permet, une intervention isolée rend le résultat plus interprétable.
12. **Négliger les signaux d’absence.** L’absence de logs ou d’alertes peut révéler une lacune de détection, mais ne prouve pas que l’événement ne s’est pas produit.

## 16. Exercices pratiques

### Exercice 1 — Qualification

Un serveur de fichiers reste accessible, mais l’ouverture de documents dépasse 90 secondes pour 60 % du personnel d’un site pendant la période de clôture comptable. Un partage secondaire fonctionne, mais il est lent.

1. Quels renseignements faut-il recueillir pour qualifier l’impact et l’urgence ?
2. Quel niveau de priorité proposerais-tu et quelles règles locales vérifierais-tu ?
3. Quel message initial communiquerais-tu ?

### Exercice 2 — Coordination

Trois équipes veulent agir en même temps : réseau souhaite modifier les règles de pare-feu, système veut redémarrer les serveurs et applicatif propose un rollback. Personne n’est coordinateur.

1. Quelle mesure organisationnelle prendre immédiatement ?
2. Quelles informations demander à chaque équipe ?
3. Comment choisir l’action sans déclencher une guerre d’hypothèses ?

### Exercice 3 — Causalité

Une alerte disque apparaît à 14 h. Le service ralentit à 14 h 10. Une tâche de sauvegarde a démarré à 13 h 55. Le redémarrage résout le symptôme jusqu’au lendemain.

1. Pourquoi le redémarrage ne constitue-t-il pas une RCA ?
2. Quelles preuves vérifier ?
3. Quels facteurs contributifs pourraient expliquer la récurrence ?

### Exercice 4 — Actions

La RCA conclut que les certificats expirés provoquent plusieurs incidents par an. Propose une action de prévention, une action de détection et une action de récupération, chacune avec propriétaire et critère de réussite.

### Exercice 5 — Qualité du rapport

Critique la phrase : « La panne est due au manque de vigilance d’un technicien. Nous lui avons rappelé la procédure. » Réécris-la de façon factuelle et actionnable en indiquant au moins une preuve à rechercher.

### Exercice 6 — Indicateurs

Un tableau de bord annonce que le MTTR a diminué de 40 %, mais les tickets sont de plus en plus souvent rouverts. Donne trois explications possibles et propose deux indicateurs complémentaires.

### Exercice 7 — Incident majeur

Le système de paiement est partiellement indisponible et certains utilisateurs reçoivent une confirmation sans certitude que la transaction a été enregistrée. Décris l’ordre des priorités entre protection de l’intégrité, communication, mitigation et RCA.

## 17. Corrigés commentés

### Correction 1

Il faut préciser les fonctions touchées, la part d’utilisateurs, le calendrier métier, les erreurs, la latence, les changements récents, la capacité du partage secondaire, l’existence de pertes ou de corruptions et les autres sites. La priorité dépend de la matrice locale ; la clôture comptable augmente l’urgence, et le contournement partiel ne rend pas l’incident automatiquement mineur. Le message doit décrire le périmètre observé, les actions en cours, l’absence de cause confirmée et l’heure de la prochaine mise à jour.

### Correction 2

Nommer un Incident Commander et ouvrir un canal de coordination. Chacune des équipes doit présenter les faits, l’hypothèse, le test attendu, les risques et les conditions de rollback. Le responsable des opérations coordonne l’exécution technique ; le coordinateur arbitre selon l’impact, l’invasivité, la réversibilité et la valeur diagnostique. Éviter plusieurs modifications simultanées rend les résultats plus faciles à interpréter, sauf urgence qui impose de réduire rapidement un risque.

### Correction 3

Un redémarrage retire peut-être temporairement des fichiers ou des processus ouverts mais ne démontre ni le lien avec la sauvegarde ni la raison de la saturation. Vérifier occupation et débit disque, files d’E/S, logs, calendrier de sauvegarde, limite de bande passante, croissance des données, changements et comportement sur plusieurs jours. Des facteurs contributifs possibles sont une sauvegarde non limitée, absence de capacité prévisionnelle, alerte tardive ou concurrence avec la charge métier. Il faut relier chaque piste à une preuve.

### Correction 4

- Prévention : renouvellement automatisé lorsque compatible, avec test de validité et validation après renouvellement ; propriétaire : équipe plateforme ; succès : test de renouvellement en préproduction sans interruption.
- Détection : alertes graduées à 30, 14 et 7 jours de l’expiration, plus contrôle de certificat réellement servi ; propriétaire : supervision ; succès : test d’alerte reçu par le bon groupe.
- Récupération : runbook de remplacement avec sauvegarde/retour arrière et vérification des chaînes ; propriétaire : service owner ; succès : exercice chronométré validant les clients représentatifs.

### Correction 5

Formulation possible : « La procédure de changement ne comporte pas de contrôle bloquant qui vérifie la configuration effective après intervention. Les journaux montrent une différence entre la configuration prévue et celle chargée en production. Ajouter une validation automatisée, rendre son résultat obligatoire dans la checklist et tester l’étape en environnement de préproduction. » Il faut encore recueillir le diff, les logs et le résultat du contrôle pour confirmer la relation causale.

### Correction 6

Explications possibles : l’horloge du MTTR a changé ; le ticket est déclaré rétabli avant validation complète ; le périmètre des tickets est devenu moins complexe ; ou les interruptions sont effectivement moins longues mais la solution reste fragile. Ajouter le taux de réouverture, la récurrence à 7/30 jours, le temps jusqu’à validation métier et les percentiles de durée. Comparer des populations et périodes comparables.

### Correction 7

La priorité immédiate est d’éviter les doublons, les pertes de cohérence ou les décisions dangereuses sur les transactions. Mobiliser le propriétaire du paiement et, si nécessaire, sécurité, finance et fournisseur. Communiquer que l’état des transactions est en cours de vérification, sans promettre une résolution non confirmée. Mitiger en protégeant les écritures, en contrôlant les retries et en utilisant une procédure approuvée. Préserver les journaux et faire la RCA après stabilisation de l’intégrité et de l’impact immédiat.

## 18. Quiz d’auto-évaluation

1. Un incident est-il nécessairement fermé lorsque l’utilisateur ne se plaint plus ?
2. Pourquoi impact et urgence doivent-ils être séparés ?
3. Quelle est la différence entre mitigation et correction définitive ?
4. Qui devrait modifier la production pendant une réponse majeure coordonnée ?
5. Une RCA doit-elle obligatoirement contenir exactement cinq « pourquoi » ?
6. Pourquoi un changement récent ne suffit-il pas à prouver une cause ?
7. Quelle différence existe entre compléter une action et prouver son efficacité ?
8. Pourquoi le MTTR doit-il être défini avant comparaison ?
9. Que doit contenir un transfert de commandement ?
10. Comment une approche sans blâme peut-elle améliorer la qualité de la RCA ?
11. Pourquoi la gestion des problèmes continue-t-elle après le rétablissement ?
12. Quels éléments doit contenir une action corrective utile ?

### Réponses

1. Non ; il faut valider le service selon des critères connus et documenter la décision.
2. Le périmètre touché et le délai avant dommage sont deux dimensions différentes qui peuvent conduire à des priorités différentes.
3. La mitigation limite l’impact ; la correction vise à supprimer ou réduire la cause de manière durable.
4. Les opérations coordonnées par le lead opérations, selon l’autorisation et la gouvernance de changement ; le coordinateur garde la vue d’ensemble.
5. Non ; c’est une technique de questionnement, pas une exigence numérique. Le raisonnement doit être étayé et actionnable.
6. La proximité temporelle est une corrélation à vérifier par des changements, métriques, logs et tests.
7. La complétion montre que le travail a été livré ; l’efficacité montre que le risque ciblé a réellement diminué.
8. Parce que l’expression peut mesurer des intervalles différents ; il faut des bornes homogènes pour comparer.
9. Impact, sévérité, état, rôles, actions, hypothèses, décisions, risques, communications, preuves et prochaines échéances.
10. Elle réduit la peur de signaler les problèmes et dirige l’attention vers les conditions, contrôles et améliorations plutôt que vers les accusations.
11. La cause, la prévention, les erreurs connues et les actions de réduction de récurrence restent à traiter même si le service fonctionne.
12. Résultat attendu, propriétaire, échéance, priorité, dépendances, critère de complétion et méthode de validation d’efficacité.

## 19. Checklist opérationnelle

### Au début

- [ ] Créer ou retrouver le ticket maître et ses liens.
- [ ] Décrire le symptôme observable et distinguer les heures.
- [ ] Évaluer impact, urgence, priorité et justification.
- [ ] Vérifier les risques sur l’intégrité, la sécurité et les données.
- [ ] Déclarer un incident majeur si les critères sont remplis.
- [ ] Attribuer les rôles et le canal de coordination.
- [ ] Fixer une cadence de communication et consigner les hypothèses.

### Pendant

- [ ] Réduire le périmètre de recherche avec des hypothèses testables.
- [ ] Préserver les preuves nécessaires et vérifier l’horodatage.
- [ ] Évaluer chaque changement pour sa portée, sa réversibilité et son risque.
- [ ] Documenter décision, exécution, résultat et prochaine action.
- [ ] Publier les mises à jour au rythme annoncé.
- [ ] Réévaluer régulièrement sévérité et impact.

### Après

- [ ] Valider service, transactions et intégrité métier.
- [ ] Communiquer le rétablissement et les incertitudes restantes.
- [ ] Ouvrir le problème / la RCA selon les critères locaux.
- [ ] Reconstituer une chronologie appuyée par des sources.
- [ ] Identifier cause immédiate, facteurs contributifs et défenses manquantes.
- [ ] Créer des actions précises avec propriétaire et échéance.
- [ ] Définir les preuves de complétion et d’efficacité.
- [ ] Publier un rapport adapté à son audience et respectueux de la confidentialité.
- [ ] Revoir les actions échues et mesurer la récurrence.

## 20. Glossaire

- **CAPA :** actions correctives et préventives.
- **CI (Configuration Item) :** élément de configuration suivi dans la gestion des services.
- **Incident Commander / Incident Manager :** personne qui coordonne la réponse, selon le modèle local.
- **ITSM :** gestion des services informatiques.
- **MTTA / MTTD / MTTR :** indicateurs de délai dont les bornes doivent être définies.
- **OLA :** accord opérationnel interne entre équipes.
- **PIR / postmortem :** revue post-incident.
- **RCA :** analyse des causes racines.
- **RACI :** matrice des rôles Responsible, Accountable, Consulted, Informed.
- **Runbook :** procédure opérationnelle reproductible.
- **SLA :** engagement de niveau de service.
- **SLO :** objectif de niveau de service.
- **SEV1/SEV2 :** niveaux de gravité internes, s’ils sont utilisés ; leur définition varie.
- **Workaround :** solution de contournement temporaire.

## 21. Références et lectures complémentaires

Les ressources suivantes complètent ce cours. Les procédures d’incident ITSM ne remplacent pas les obligations légales, contractuelles, de sécurité ou de notification applicables à une organisation.

1. **PeopleCert — ITIL 4 Practitioner: Incident Management.** Présentation de la pratique officielle et de son rôle dans la gestion des services : https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil4-practices-incident-management-3684
2. **Google Site Reliability Engineering — Managing Incidents.** Modèle de gestion coordonnée et rôles de réponse : https://sre.google/sre-book/managing-incidents/
3. **Google SRE Workbook — Incident Response.** Rôles, coordination et communication : https://sre.google/workbook/incident-response/
4. **Google SRE — Postmortem Culture: Learning from Failure.** Culture sans blâme, chronologie, actions et partage des apprentissages : https://sre.google/sre-book/postmortem-culture/
5. **Atlassian Incident Management Handbook — Postmortems.** Structure du rapport, facteurs contributifs et suivi des actions : https://www.atlassian.com/incident-management/handbook/postmortems
6. **NIST — Incident Response.** Pour la dimension spécifique des incidents de cybersécurité, consulter la page du projet et SP 800-61 Rev. 3 : https://csrc.nist.gov/projects/incident-response

---

**À retenir :** une réponse intermédiaire efficace combine triage discipliné, mitigation contrôlée, communication vérifiable, collecte de preuves, analyse causale sans accusation et actions suivies jusqu’à la preuve d’efficacité. Le service peut être rétabli avant que toutes les causes soient expliquées ; le risque, lui, ne doit pas être considéré comme traité tant que les améliorations convenues ne sont pas vérifiées.
