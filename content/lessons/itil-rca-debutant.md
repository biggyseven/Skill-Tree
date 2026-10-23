# Gestion d’incident (ITIL et RCA) — Niveau Débutant

**Niveau :** Débutant  
**Public :** techniciens helpdesk, administrateurs systèmes et réseaux débutants, équipes de support et personnes qui découvrent la gestion des services IT.  
**Objectif :** apprendre à enregistrer, qualifier, prioriser, traiter et clôturer un incident, puis à rechercher ses causes avec une analyse des causes racines (RCA, *Root Cause Analysis*).

> **Fil conducteur :** pendant un incident, la priorité immédiate est de limiter l’impact et de rétablir le service de manière contrôlée. L’analyse approfondie des causes peut continuer après le rétablissement. Il ne faut ni confondre ces deux objectifs, ni laisser l’un faire oublier l’autre.

Ce cours présente les pratiques de manière pédagogique, en s’inspirant des concepts ITIL 4 et des méthodes courantes d’analyse post-incident. Il ne remplace pas une formation ou une certification officielle. Les noms de statuts, les délais et les règles de priorité proposés sont des exemples à adapter aux procédures de chaque organisation.

---

## 1. Les objectifs d’apprentissage

À la fin du cours, tu devrais pouvoir :

- expliquer ce qu’est un incident et le distinguer d’une demande de service, d’un problème et d’un changement ;
- décrire le cycle de vie d’un incident, de la détection à la clôture ;
- recueillir les informations essentielles sans retarder inutilement la prise en charge ;
- évaluer l’impact et l’urgence, puis attribuer une priorité cohérente ;
- communiquer clairement avec les utilisateurs et escalader au bon moment ;
- appliquer une solution de contournement sans la présenter comme une correction définitive ;
- utiliser les **5 pourquoi**, le diagramme d’Ishikawa et une chronologie pour explorer les causes ;
- distinguer fait, hypothèse, cause directe, facteur contributif et cause racine ;
- rédiger un compte rendu post-incident avec des actions vérifiables ;
- mesurer quelques indicateurs sans encourager des comportements qui dégradent le service.

## 2. Comprendre la gestion des services IT

Une équipe informatique ne se contente pas de faire fonctionner des ordinateurs. Elle fournit des services qui aident les utilisateurs à accomplir leur travail : accès au courrier électronique, réseau, application métier, authentification, stockage de fichiers, téléphonie, plateforme de paiement ou encore sauvegarde.

Un **service IT** combine généralement des personnes, des processus, des informations, des applications, des infrastructures et des fournisseurs. L’utilisateur juge surtout le résultat : peut-il travailler correctement ? Un serveur peut être « en ligne » alors que le service reste indisponible parce que le DNS, l’authentification, le réseau ou la base de données ne fonctionne plus.

La gestion des services IT (*IT Service Management*, ITSM) regroupe les pratiques qui permettent de concevoir, fournir, soutenir et améliorer ces services. ITIL est un référentiel de bonnes pratiques de gestion des services. Il propose des concepts et des recommandations ; il ne faut pas le considérer comme une procédure unique identique pour toutes les organisations.

### 2.1 Une analogie simple

Imagine une compagnie d’électricité :

- un **incident** est une panne qui prive des clients d’électricité ou réduit la qualité de l’alimentation ;
- la **gestion de l’incident** vise à rétablir le courant en sécurité le plus rapidement possible ;
- la **gestion du problème** cherche pourquoi la panne s’est produite et comment empêcher qu’elle se reproduise ;
- un **changement** est une modification contrôlée du réseau, par exemple remplacer un équipement ou modifier un réglage.

Dans l’informatique, on applique la même logique. Réinitialiser un service peut rétablir une application, mais cela n’explique pas forcément pourquoi elle s’est bloquée. Un bon support gère la panne immédiate **et** apprend de ce qui s’est passé.

## 3. Les notions à ne pas confondre

### 3.1 Incident

Un incident est une interruption non planifiée d’un service, ou une baisse de sa qualité. Un défaut d’un composant qui n’affecte pas encore les utilisateurs peut aussi être suivi comme incident selon les règles internes de l’organisation.

Exemples :

- plusieurs utilisateurs ne peuvent plus ouvrir leur session ;
- le Wi-Fi fonctionne, mais les connexions coupent régulièrement ;
- l’application comptable répond en 40 secondes au lieu de quelques secondes ;
- les imprimantes d’un étage sont inaccessibles ;
- un disque est dégradé et menace la disponibilité du stockage.

### 3.2 Demande de service

Une demande de service est une sollicitation habituelle, prédéfinie et autorisée : créer un compte, installer un logiciel approuvé, demander un accès ou obtenir un équipement. Elle n’indique pas nécessairement qu’un service est défaillant.

**Question utile :** l’utilisateur demande-t-il quelque chose qui n’existait pas encore, ou signale-t-il que quelque chose qui devrait fonctionner ne fonctionne plus ? Dans le premier cas, il peut s’agir d’une demande ; dans le second, probablement d’un incident.

### 3.3 Problème

Un problème est une cause, ou une cause potentielle, d’un ou de plusieurs incidents. La gestion des problèmes cherche à réduire la probabilité et l’impact des incidents en comprenant les causes, en proposant des solutions de contournement et en suivant les corrections durables.

Un incident peut être résolu avant que sa cause soit connue. Il peut donc être clôturé selon la procédure de l’organisation tandis que le problème associé continue d’être investigué. Certains environnements imposent toutefois de conserver l’incident ouvert jusqu’à la validation de certaines conditions : il faut suivre la politique locale.

### 3.4 Erreur connue

Une **erreur connue** (*known error*) est un problème analysé dont la cause ou une méthode de réduction de l’impact est suffisamment documentée pour être réutilisée. Elle peut comporter une solution de contournement et des limites connues. Elle n’est pas nécessairement corrigée définitivement.

### 3.5 Changement

Un changement est l’ajout, la modification ou la suppression de quelque chose qui peut avoir un effet direct ou indirect sur un service. Le changement peut être nécessaire pour appliquer une correction permanente : mise à jour, modification de configuration, remplacement de matériel ou ajustement d’une règle réseau.

Une correction technique risquée ne doit pas être improvisée uniquement parce qu’un incident est urgent. Le processus d’urgence prévu par l’organisation doit permettre une décision rapide tout en gardant l’autorisation, les tests, le plan de retour arrière et la traçabilité nécessaires.

### 3.6 Tableau de comparaison

| Notion | Question centrale | Exemple | Résultat attendu |
|---|---|---|---|
| Incident | Qu’est-ce qui ne fonctionne pas ? | Le portail de paiement ne répond plus. | Rétablir le service et limiter l’impact. |
| Demande | Quel service standard est demandé ? | Créer un compte pour un nouvel employé. | Livrer la demande autorisée. |
| Problème | Pourquoi des incidents se produisent-ils ? | Les pannes du portail reviennent après les pics de charge. | Comprendre les causes et réduire les récidives. |
| Erreur connue | Que sait-on déjà du problème ? | Une fuite de connexions est identifiée ; redémarrer rétablit temporairement le service. | Partager le diagnostic et le contournement connus. |
| Changement | Quelle modification contrôlée doit être effectuée ? | Corriger le pool de connexions et déployer une nouvelle version. | Modifier le service de manière maîtrisée. |

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 900 330" role="img" aria-label="Différence entre gestion de l’incident, gestion du problème et changement"><defs><marker id="ir1-cyan" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#38bdf8"/></marker><marker id="ir1-green" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#34d399"/></marker><marker id="ir1-amber" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#fbbf24"/></marker><style>@keyframes ir1Flow{to{stroke-dashoffset:-20}}.flow-line{stroke-dasharray:8 7;animation:ir1Flow 1.5s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="898" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="28" y="35" fill="#e5eefb" font-size="19" font-weight="700">Trois objectifs complémentaires</text><rect x="28" y="65" width="245" height="105" rx="12" fill="#11283c" stroke="#38bdf8" stroke-width="1.5"/><text x="150" y="91" fill="#7dd3fc" text-anchor="middle" font-size="15" font-weight="700">INCIDENT</text><text x="150" y="117" fill="#edf6ff" text-anchor="middle" font-size="14">Rétablir le service</text><text x="150" y="139" fill="#a9bdcf" text-anchor="middle" font-size="12">Réduire l’impact immédiat</text><rect x="328" y="65" width="245" height="105" rx="12" fill="#102b27" stroke="#34d399" stroke-width="1.5"/><text x="450" y="91" fill="#6ee7b7" text-anchor="middle" font-size="15" font-weight="700">PROBLÈME / RCA</text><text x="450" y="117" fill="#edf6ff" text-anchor="middle" font-size="14">Comprendre les causes</text><text x="450" y="139" fill="#a9bdcf" text-anchor="middle" font-size="12">Réduire les récidives</text><rect x="628" y="65" width="245" height="105" rx="12" fill="#302817" stroke="#fbbf24" stroke-width="1.5"/><text x="750" y="91" fill="#fcd34d" text-anchor="middle" font-size="15" font-weight="700">CHANGEMENT</text><text x="750" y="117" fill="#edf6ff" text-anchor="middle" font-size="14">Modifier avec contrôle</text><text x="750" y="139" fill="#c9bda7" text-anchor="middle" font-size="12">Tester et réduire le risque</text><path class="flow-line" d="M273 119 H320" fill="none" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#ir1-cyan)"/><path class="flow-line" d="M573 119 H620" fill="none" stroke="#34d399" stroke-width="2.5" marker-end="url(#ir1-green)"/><path class="flow-line" d="M750 170 V218 H450 V178" fill="none" stroke="#fbbf24" stroke-width="2" marker-end="url(#ir1-amber)"/><rect x="70" y="228" width="760" height="69" rx="12" fill="#111d2e" stroke="#334155"/><text x="450" y="253" fill="#e5eefb" text-anchor="middle" font-size="14" font-weight="700">Boucle d’amélioration</text><text x="450" y="276" fill="#afc1d3" text-anchor="middle" font-size="13">Rétablir → enquêter → corriger durablement → vérifier → apprendre</text></svg></div>

## 4. Qu’est-ce que la RCA ?

La **RCA** (*Root Cause Analysis*, analyse des causes racines) désigne une démarche structurée pour comprendre pourquoi un événement indésirable s’est produit, comment il a pu atteindre le service et quelles actions peuvent empêcher une récidive ou réduire son impact.

Une RCA sérieuse ne se contente pas de donner un nom au composant qui a échoué. « Le serveur a planté » décrit un événement observé, mais n’explique pas pourquoi il a planté. « Un technicien a redémarré le service » décrit une action de rétablissement, pas la cause initiale. Il faut chercher les mécanismes et les conditions qui ont permis à l’incident d’apparaître et de durer.

### 4.1 Des niveaux de causalité différents

- **Symptôme :** ce que l’utilisateur ou le système observe — par exemple, les pages restent en chargement.
- **Événement déclencheur :** ce qui précède immédiatement l’incident — par exemple, le nombre de connexions augmente brusquement.
- **Cause directe ou cause proximale :** mécanisme qui provoque directement la défaillance — par exemple, le pool de connexions atteint sa limite.
- **Facteur contributif :** condition qui augmente la probabilité ou l’impact — par exemple, le délai d’attente est trop élevé ou les alertes arrivent tard.
- **Cause racine/actionnable :** condition plus profonde sur laquelle une action peut agir et dont la correction réduit la probabilité de répétition — par exemple, une gestion des connexions qui ne libère pas les ressources dans un scénario d’erreur, combinée à l’absence de test de charge et de surveillance dédiée.

Le terme « cause racine » ne signifie pas toujours qu’il existe une seule cause ultime. Les incidents complexes sont souvent le résultat de plusieurs facteurs techniques et organisationnels. L’objectif n’est pas de trouver un coupable, mais d’identifier des explications suffisamment étayées pour orienter des actions efficaces.

### 4.2 Incident, rétablissement et RCA : trois temps

1. **Réponse immédiate :** protéger les personnes, les données et le service ; contenir l’impact ; coordonner les intervenants.
2. **Rétablissement :** appliquer un contournement ou une correction maîtrisée ; vérifier que le service est de nouveau acceptable.
3. **Apprentissage :** collecter les preuves, établir la chronologie, tester les hypothèses, identifier les actions correctives et vérifier leur efficacité.

Ces étapes peuvent se chevaucher. Dès le début, il faut préserver les journaux, les métriques et les informations utiles sans ralentir un rétablissement urgent. Si un incident de sécurité est possible, ne pas supprimer les traces ni redémarrer aveuglément : appliquer la procédure de sécurité et de préservation des preuves de l’organisation.

## 5. Le cycle de vie d’un incident

Les outils et équipes peuvent utiliser des statuts différents. Le cycle suivant est un modèle de base, à adapter localement.

1. **Détecter / signaler.** Un utilisateur, un outil de supervision ou une équipe constate un dysfonctionnement.
2. **Enregistrer.** Créer un ticket ou une fiche unique avec un identifiant et les faits connus.
3. **Catégoriser.** Choisir une catégorie utile : réseau, poste de travail, application, accès, sécurité, base de données, fournisseur, etc.
4. **Évaluer l’impact et l’urgence.** Déterminer la priorité selon des critères partagés.
5. **Diagnostiquer initialement.** Vérifier les symptômes, chercher les incidents similaires et consulter la base de connaissances.
6. **Escalader si nécessaire.** Transférer à une équipe compétente avec le contexte et les tests déjà réalisés.
7. **Contenir / contourner.** Réduire l’impact si la correction définitive n’est pas immédiatement sûre ou disponible.
8. **Rétablir et valider.** Appliquer la solution prévue et confirmer le fonctionnement du point de vue technique et utilisateur.
9. **Documenter et clôturer.** Résumer le résultat, le temps d’indisponibilité, les confirmations et les liens vers les problèmes ou changements associés.
10. **Déclencher la RCA si nécessaire.** Investiguer les incidents récurrents, majeurs, à fort risque ou dont la cause n’est pas claire, selon les règles de l’organisation.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 1000 330" role="img" aria-label="Cycle de vie d’un incident en dix grandes étapes"><defs><marker id="ir2-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#38bdf8"/></marker><marker id="ir2-green" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#34d399"/></marker><style>@keyframes ir2Flow{to{stroke-dashoffset:-18}}.flow-line{stroke-dasharray:8 6;animation:ir2Flow 1.4s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="998" height="328" rx="18" fill="#0b1220" stroke="#263449"/><text x="26" y="34" fill="#e5eefb" font-size="19" font-weight="700">Cycle de vie de l’incident</text><g font-family="Arial, sans-serif" text-anchor="middle"><rect x="28" y="67" width="150" height="68" rx="10" fill="#11283c" stroke="#38bdf8"/><text x="103" y="93" fill="#7dd3fc" font-size="14" font-weight="700">1. Détecter</text><text x="103" y="115" fill="#dbeafe" font-size="12">Signalement</text><rect x="200" y="67" width="150" height="68" rx="10" fill="#11283c" stroke="#38bdf8"/><text x="275" y="93" fill="#7dd3fc" font-size="14" font-weight="700">2. Enregistrer</text><text x="275" y="115" fill="#dbeafe" font-size="12">Ticket et faits</text><rect x="372" y="67" width="150" height="68" rx="10" fill="#11283c" stroke="#38bdf8"/><text x="447" y="93" fill="#7dd3fc" font-size="14" font-weight="700">3. Qualifier</text><text x="447" y="115" fill="#dbeafe" font-size="12">Catégorie / priorité</text><rect x="544" y="67" width="150" height="68" rx="10" fill="#152338" stroke="#60a5fa"/><text x="619" y="93" fill="#93c5fd" font-size="14" font-weight="700">4. Diagnostiquer</text><text x="619" y="115" fill="#dbeafe" font-size="12">Tests / historique</text><rect x="716" y="67" width="150" height="68" rx="10" fill="#302817" stroke="#fbbf24"/><text x="791" y="93" fill="#fcd34d" font-size="14" font-weight="700">5. Escalader</text><text x="791" y="115" fill="#fef3c7" font-size="12">Si nécessaire</text><path class="flow-line" d="M178 101 H194 M350 101 H366 M522 101 H538 M694 101 H710" stroke="#38bdf8" stroke-width="2.3" fill="none" marker-end="url(#ir2-arrow)"/><rect x="112" y="190" width="170" height="68" rx="10" fill="#302817" stroke="#fbbf24"/><text x="197" y="216" fill="#fcd34d" font-size="14" font-weight="700">6. Contourner</text><text x="197" y="238" fill="#fef3c7" font-size="12">Réduire l’impact</text><rect x="318" y="190" width="170" height="68" rx="10" fill="#102b27" stroke="#34d399"/><text x="403" y="216" fill="#6ee7b7" font-size="14" font-weight="700">7. Rétablir</text><text x="403" y="238" fill="#d1fae5" font-size="12">Tester le service</text><rect x="524" y="190" width="170" height="68" rx="10" fill="#102b27" stroke="#34d399"/><text x="609" y="216" fill="#6ee7b7" font-size="14" font-weight="700">8. Clôturer</text><text x="609" y="238" fill="#d1fae5" font-size="12">Résumé / validation</text><rect x="730" y="190" width="170" height="68" rx="10" fill="#241c36" stroke="#c084fc"/><text x="815" y="216" fill="#d8b4fe" font-size="14" font-weight="700">9. RCA si utile</text><text x="815" y="238" fill="#f3e8ff" font-size="12">Prévenir la récidive</text><path class="flow-line" d="M791 135 V164 H197 V184 M282 224 H312 M488 224 H518 M694 224 H724" stroke="#38bdf8" stroke-width="2.3" fill="none" marker-end="url(#ir2-arrow)"/><text x="500" y="294" fill="#94a3b8" text-anchor="middle" font-size="12">Le rétablissement est validé avant la clôture selon les règles locales.</text></g></svg></div>

### 5.1 Les informations minimales du ticket

Un ticket utile permet à une autre personne de reprendre le travail sans recommencer toute l’enquête. Enregistre au minimum :

- identifiant du ticket, date et heure, personne ou système à l’origine du signalement ;
- service concerné, site, utilisateurs ou groupe affecté ;
- description factuelle des symptômes et heure de début si connue ;
- portée et impact métier connu ;
- priorité et justification ;
- message d’erreur exact, captures ou identifiants de journaux si pertinents ;
- tests effectués, résultats observés et actions déjà tentées ;
- état actuel, contournement, équipe responsable et prochaine mise à jour annoncée.

Ne demande pas de mots de passe, de jetons d’accès ou de données personnelles inutiles dans le ticket. Les captures et extraits de journaux peuvent contenir des informations sensibles : applique les règles d’accès, de rétention et de masquage de l’organisation.

### 5.2 Écrire un bon titre et une bonne description

**Titre vague :** « Le réseau est nul ».  
**Titre plus utile :** « Les utilisateurs du 2e étage perdent l’accès au serveur de fichiers depuis 09 h 20 ».

**Description factuelle :** « Depuis 09 h 20, 12 utilisateurs du 2e étage indiquent que le lecteur réseau `S:` se déconnecte. L’accès Internet semble fonctionner. Deux postes ont été testés ; la résolution DNS du serveur répond. Aucun changement connu n’a encore été confirmé. »

Évite de mettre la cause présumée dans le titre avant de l’avoir prouvée. « Switch en panne » est une hypothèse ; « Perte d’accès au serveur de fichiers depuis le 2e étage » décrit le symptôme.

## 6. Prioriser : impact, urgence et priorité

La priorité aide l’équipe à décider dans quel ordre traiter les incidents. Elle ne doit pas dépendre uniquement de la personne qui insiste le plus ou de la facilité technique du ticket.

- **Impact :** ampleur des conséquences — combien de personnes, de sites ou de processus critiques sont affectés ?
- **Urgence :** combien de temps peut-on attendre avant que l’impact devienne inacceptable ou augmente fortement ?
- **Priorité :** ordre et rythme de traitement décidés à partir de critères partagés, souvent fondés sur impact et urgence, avec des règles spécifiques aux incidents majeurs et de sécurité.

Une petite panne affectant une fonction vitale peut être plus urgente qu’une panne plus visible sur un service secondaire. De même, un seul compte compromis peut représenter un risque élevé pour la sécurité et ne doit pas être sous-priorisé parce qu’un seul utilisateur est touché.

### 6.1 Exemple de matrice de priorité

La matrice ci-dessous est illustrative. Chaque organisation doit adapter ses niveaux, délais cibles, définitions d’impact et règles de sécurité.

| Impact \ Urgence | Faible | Moyenne | Élevée |
|---|---:|---:|---:|
| **Élevé** | P2 | P1 | P1 |
| **Moyen** | P3 | P2 | P1 ou P2 selon contexte |
| **Faible** | P4 | P3 | P2 si la fenêtre d’action est courte |

P1 signifie ici « priorité la plus élevée ». D’autres organisations utilisent P0 ou des noms différents. Il faut définir chaque niveau concrètement au lieu de retenir uniquement un chiffre.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 900 385" role="img" aria-label="Matrice exemple de priorité en fonction de l’impact et de l’urgence"><defs><style>@keyframes ir3Pulse{to{stroke-dashoffset:-16}}.flow-line{stroke-dasharray:7 6;animation:ir3Pulse 1.6s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="898" height="383" rx="18" fill="#0b1220" stroke="#263449"/><text x="26" y="34" fill="#e5eefb" font-size="19" font-weight="700">Matrice de priorité — exemple à adapter</text><text x="42" y="218" fill="#cbd5e1" font-size="13" transform="rotate(-90 42 218)" text-anchor="middle">Impact</text><text x="525" y="355" fill="#cbd5e1" font-size="13" text-anchor="middle">Urgence →</text><g font-family="Arial, sans-serif" text-anchor="middle"><text x="151" y="77" fill="#94a3b8" font-size="12">Urgence faible</text><text x="363" y="77" fill="#94a3b8" font-size="12">Urgence moyenne</text><text x="575" y="77" fill="#94a3b8" font-size="12">Urgence élevée</text><text x="83" y="125" fill="#e2e8f0" font-size="12">Impact élevé</text><text x="83" y="205" fill="#e2e8f0" font-size="12">Impact moyen</text><text x="83" y="285" fill="#e2e8f0" font-size="12">Impact faible</text><rect x="118" y="90" width="205" height="67" rx="8" fill="#513224" stroke="#fb923c"/><text x="220" y="118" fill="#fed7aa" font-size="18" font-weight="700">P2</text><text x="220" y="139" fill="#ffedd5" font-size="11">Plan d’action rapide</text><rect x="330" y="90" width="205" height="67" rx="8" fill="#4a2026" stroke="#fb7185"/><text x="432" y="118" fill="#fecdd3" font-size="18" font-weight="700">P1</text><text x="432" y="139" fill="#ffe4e6" font-size="11">Impact élevé et pressant</text><rect x="542" y="90" width="205" height="67" rx="8" fill="#4a2026" stroke="#fb7185"/><text x="644" y="118" fill="#fecdd3" font-size="18" font-weight="700">P1</text><text x="644" y="139" fill="#ffe4e6" font-size="11">Traiter en priorité</text><rect x="118" y="170" width="205" height="67" rx="8" fill="#1e293b" stroke="#64748b"/><text x="220" y="198" fill="#cbd5e1" font-size="18" font-weight="700">P3</text><text x="220" y="219" fill="#e2e8f0" font-size="11">Traitement planifié</text><rect x="330" y="170" width="205" height="67" rx="8" fill="#513224" stroke="#fb923c"/><text x="432" y="198" fill="#fed7aa" font-size="18" font-weight="700">P2</text><text x="432" y="219" fill="#ffedd5" font-size="11">Surveillance et action</text><rect x="542" y="170" width="205" height="67" rx="8" fill="#4a2026" stroke="#fb7185"/><text x="644" y="198" fill="#fecdd3" font-size="18" font-weight="700">P1/P2</text><text x="644" y="219" fill="#ffe4e6" font-size="11">Selon le risque métier</text><rect x="118" y="250" width="205" height="67" rx="8" fill="#142b2a" stroke="#34d399"/><text x="220" y="278" fill="#a7f3d0" font-size="18" font-weight="700">P4</text><text x="220" y="299" fill="#d1fae5" font-size="11">Faible impact, attente possible</text><rect x="330" y="250" width="205" height="67" rx="8" fill="#1e293b" stroke="#64748b"/><text x="432" y="278" fill="#cbd5e1" font-size="18" font-weight="700">P3</text><text x="432" y="299" fill="#e2e8f0" font-size="11">Planifier</text><rect x="542" y="250" width="205" height="67" rx="8" fill="#513224" stroke="#fb923c"/><text x="644" y="278" fill="#fed7aa" font-size="18" font-weight="700">P2*</text><text x="644" y="299" fill="#ffedd5" font-size="11">*Si fenêtre courte</text></g><text x="450" y="337" fill="#94a3b8" text-anchor="middle" font-size="10">Exemple pédagogique : sécurité, conformité et criticité peuvent modifier la priorité.</text></svg></div>

### 6.2 Quand déclarer un incident majeur ?

Un incident majeur est un incident qui, selon les critères locaux, exige une coordination et une communication renforcées : impact étendu, service critique indisponible, risque sur la sécurité ou la conformité, perte de données ou durée déjà trop longue. Il faut définir à l’avance :

- qui peut déclarer un incident majeur et à partir de quels critères ;
- qui coordonne l’intervention et qui prend les décisions ;
- comment rassembler les équipes techniques et les responsables métier ;
- à quelle fréquence publier les mises à jour ;
- comment valider le rétablissement et organiser la revue après incident.

La déclaration d’un incident majeur ne signifie pas que la cause est connue. Elle signifie que l’impact ou le risque justifie une réponse coordonnée.

## 7. Diagnostic et escalade

Le diagnostic consiste à recueillir et tester des faits pour réduire le nombre d’hypothèses plausibles. Il faut éviter de lancer au hasard de nombreuses commandes ou modifications, car on risque de perdre des indices et de rendre le problème plus difficile à reproduire.

### 7.1 Une méthode de diagnostic débutant

1. **Confirmer le symptôme.** Que voit exactement l’utilisateur ? Quel message ? Depuis quand ? Toujours ou par intermittence ?
2. **Définir la portée.** Un utilisateur, une équipe, un site, tous les clients ou un seul appareil ?
3. **Déterminer ce qui fonctionne encore.** L’utilisateur peut-il ouvrir d’autres services ? Le problème touche-t-il un réseau, un compte ou une application précise ?
4. **Chercher les changements récents.** Déploiement, mise à jour, modification réseau, renouvellement de certificat, changement d’accès ou incident fournisseur.
5. **Consulter les données.** Journaux, métriques, alertes, historique des changements, incidents similaires et base de connaissances.
6. **Tester une hypothèse à la fois.** Note le test, l’heure, le résultat attendu et le résultat observé.
7. **Définir une limite d’escalade.** Si le risque augmente, si l’incident est critique ou si les compétences nécessaires dépassent ton rôle, appelle l’équipe compétente immédiatement.

### 7.2 Escalade fonctionnelle et hiérarchique

- **Escalade fonctionnelle :** transfert vers une équipe disposant de la compétence nécessaire — réseau, systèmes, application, sécurité, fournisseur.
- **Escalade hiérarchique :** alerte d’un responsable afin d’obtenir une décision, des ressources ou une coordination adaptée.

Les deux peuvent être nécessaires en même temps. Escalader n’est pas « abandonner » le ticket. La personne qui transfère doit apporter une synthèse claire : impact, début, portée, priorité, symptômes, tests, résultats, hypothèses et actions déjà réalisées.

### 7.3 Exemple de note de transfert

> **Service :** application de gestion des commandes. **Impact :** 35 utilisateurs ne peuvent plus valider une commande depuis 10 h 12 ; consultation des commandes existantes encore possible. **Tests :** connectivité vers le frontal OK ; plusieurs réponses HTTP 502 ; erreurs similaires sur trois postes. **Changement récent :** nouvelle version applicative déployée à 10 h 05, à confirmer comme facteur causal. **Action :** équipe applicative sollicitée pour corréler les journaux du frontal et du service backend. **Prochaine mise à jour :** 10 h 30.

Cette note sépare l’observation de l’hypothèse et permet à l’équipe suivante de commencer utilement.

## 8. Contournement et rétablissement du service

Une **solution de contournement** réduit temporairement les effets d’un incident sans nécessairement supprimer sa cause. Exemples : basculer vers un serveur secondaire, utiliser un canal de secours approuvé, désactiver temporairement une fonction fautive ou redémarrer un service selon une procédure validée.

Une solution de contournement doit être évaluée selon :

- le bénéfice attendu et la rapidité de rétablissement ;
- le risque de perte ou de corruption de données ;
- les conséquences sur la sécurité, les performances et les autres services ;
- l’autorisation nécessaire et la possibilité de revenir en arrière ;
- les vérifications à faire après son application ;
- le suivi nécessaire pour retirer le contournement une fois la correction durable appliquée.

Un redémarrage peut être un contournement efficace, mais il peut détruire des preuves volatiles ou masquer une défaillance. Sur un système critique, consulte la procédure et le responsable approprié avant d’agir. En cas de suspicion de compromission, suis le processus de réponse aux incidents de sécurité.

### 8.1 Définir ce que signifie « rétabli »

Un service n’est pas forcément rétabli parce qu’un serveur répond au ping. Établis des critères concrets :

- l’utilisateur peut accomplir l’action métier critique ;
- les erreurs ne progressent plus et la latence revient dans une plage acceptable ;
- les composants dépendants répondent ;
- les données sont cohérentes et les transactions en attente sont traitées ;
- la supervision est revenue à un état normal, sans simplement masquer l’alerte ;
- un utilisateur ou un représentant métier confirme le résultat quand cela est pertinent.

Le rétablissement peut être partiel. Le ticket doit alors décrire précisément ce qui est revenu, ce qui reste dégradé, les risques résiduels et la prochaine action.

## 9. Communication pendant l’incident

La communication fait partie de la gestion de l’incident. Une bonne intervention technique peut être perçue comme mauvaise si personne ne sait ce qui se passe, qui pilote la situation ou quand une nouvelle information sera donnée.

Une mise à jour utile répond à quatre questions :

1. **Que sait-on ?** Faits vérifiés et périmètre affecté.
2. **Que fait-on ?** Actions en cours et équipes impliquées.
3. **Que doit faire l’utilisateur ?** Attendre, utiliser un contournement approuvé, éviter une action particulière ou signaler un impact spécifique.
4. **Quand aura lieu la prochaine mise à jour ?** Donner une heure ou un intervalle, même si la cause n’est pas encore connue.

Exemple : « Nous investiguons une indisponibilité du portail de commandes qui affecte plusieurs utilisateurs depuis 10 h 12. L’équipe applicative compare les journaux avant et après le dernier déploiement. Aucune cause n’est confirmée à ce stade. Prochaine mise à jour à 10 h 45. »

Évite d’annoncer une heure de retour non vérifiée, de publier des données sensibles ou de spéculer sur un fournisseur ou un collègue. Dire « nous ne connaissons pas encore la cause, voici les vérifications en cours » est plus fiable qu’une explication inventée.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 900 270" role="img" aria-label="Chronologie illustrant détection, communication, contournement, rétablissement et revue RCA"><defs><marker id="ir4-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#38bdf8"/></marker><style>@keyframes ir4Flow{to{stroke-dashoffset:-16}}.flow-line{stroke-dasharray:7 6;animation:ir4Flow 1.3s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="898" height="268" rx="18" fill="#0b1220" stroke="#263449"/><text x="26" y="34" fill="#e5eefb" font-size="19" font-weight="700">Chronologie fictive d’un incident</text><path class="flow-line" d="M76 126 H826" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#ir4-arrow)"/><g font-family="Arial, sans-serif" text-anchor="middle"><circle cx="110" cy="126" r="8" fill="#38bdf8"/><text x="110" y="70" fill="#7dd3fc" font-size="13" font-weight="700">09:10</text><text x="110" y="88" fill="#e5eefb" font-size="12">Détection</text><text x="110" y="165" fill="#a9bdcf" font-size="11">Signal reçu</text><text x="110" y="181" fill="#a9bdcf" font-size="11">ticket créé</text><circle cx="280" cy="126" r="8" fill="#fbbf24"/><text x="280" y="70" fill="#fcd34d" font-size="13" font-weight="700">09:18</text><text x="280" y="88" fill="#e5eefb" font-size="12">Coordination</text><text x="280" y="165" fill="#a9bdcf" font-size="11">Équipe affectée</text><text x="280" y="181" fill="#a9bdcf" font-size="11">mise à jour publiée</text><circle cx="450" cy="126" r="8" fill="#fbbf24"/><text x="450" y="70" fill="#fcd34d" font-size="13" font-weight="700">09:32</text><text x="450" y="88" fill="#e5eefb" font-size="12">Contournement</text><text x="450" y="165" fill="#a9bdcf" font-size="11">Test et validation</text><text x="450" y="181" fill="#a9bdcf" font-size="11">du risque</text><circle cx="620" cy="126" r="8" fill="#34d399"/><text x="620" y="70" fill="#6ee7b7" font-size="13" font-weight="700">09:44</text><text x="620" y="88" fill="#e5eefb" font-size="12">Rétablissement</text><text x="620" y="165" fill="#a9bdcf" font-size="11">Tests métier OK</text><text x="620" y="181" fill="#a9bdcf" font-size="11">surveillance active</text><circle cx="790" cy="126" r="8" fill="#c084fc"/><text x="790" y="70" fill="#d8b4fe" font-size="13" font-weight="700">10:30+</text><text x="790" y="88" fill="#e5eefb" font-size="12">Revue RCA</text><text x="790" y="165" fill="#a9bdcf" font-size="11">Chronologie, causes</text><text x="790" y="181" fill="#a9bdcf" font-size="11">et actions durables</text></g><text x="450" y="232" fill="#94a3b8" text-anchor="middle" font-size="12">Les horaires sont fictifs. La RCA débute souvent après le rétablissement, à partir des preuves préservées.</text></svg></div>

## 10. Préparer une RCA sans perdre les preuves

La qualité de l’analyse dépend de la qualité des éléments disponibles. Après un incident, les journaux peuvent tourner, les compteurs se réinitialiser et les souvenirs diverger. Il est utile de conserver rapidement, selon les règles de sécurité et de confidentialité :

- les horodatages et événements de supervision ;
- les journaux applicatifs, système, réseau ou base de données pertinents ;
- les métriques avant, pendant et après l’incident ;
- les changements, déploiements et opérations de maintenance proches de l’heure de début ;
- les messages d’erreur exacts, identifiants de requêtes et exemples de transactions ;
- les actions d’intervention, leurs horaires et les résultats observés ;
- les témoignages des utilisateurs, séparés des faits observés par les systèmes.

Ne collecte pas « tout au cas où » sans limite. Détermine les sources utiles, les autorisations, la durée de conservation et le mode de partage. Masque les mots de passe, jetons, informations personnelles et données métier non nécessaires. Lorsqu’une enquête de sécurité ou une obligation réglementaire est possible, respecte les exigences de chaîne de conservation des preuves et d’accès restreint.

## 11. Méthode des 5 pourquoi

Les **5 pourquoi** consistent à poser plusieurs fois la question « pourquoi ? » afin de remonter la chaîne causale. Le nombre cinq est un repère, pas une règle mathématique : une bonne analyse peut nécessiter moins ou plus de questions. Arrête-toi lorsque l’explication est étayée et qu’une action réaliste peut agir sur la cause, pas simplement parce que tu as posé cinq questions.

### 11.1 Exemple : le portail interne devient indisponible

**Problème formulé :** le portail de commandes est indisponible pendant 12 minutes, avec un impact sur 35 utilisateurs.

1. **Pourquoi le portail n’a-t-il pas traité les requêtes ?** Le service applicatif n’obtenait plus de connexion à la base de données.
2. **Pourquoi n’obtenait-il plus de connexion ?** Toutes les connexions du pool étaient occupées et de nouvelles demandes attendaient jusqu’au timeout.
3. **Pourquoi le pool restait-il saturé ?** Dans un chemin d’erreur, certaines connexions n’étaient pas libérées correctement.
4. **Pourquoi ce chemin n’a-t-il pas été détecté avant le déploiement ?** Les tests couvraient les réponses normales mais pas les erreurs répétées et la charge simultanée.
5. **Pourquoi ce type de test manquait-il ?** La définition des critères de mise en production ne précisait pas de test du cycle de vie des connexions sous erreur et sous charge.

Cette chaîne suggère plusieurs actions possibles : corriger la libération des connexions, ajouter un test de non-régression sous charge, instrumenter l’utilisation du pool et revoir les critères de validation de la mise en production. Il faut toutefois vérifier les journaux, le code et les résultats de test : les « pourquoi » sont des hypothèses tant qu’ils ne sont pas confirmés.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 900 440" role="img" aria-label="Exemple des cinq pourquoi remontant du symptôme vers des causes actionnables"><defs><marker id="ir5-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#38bdf8"/></marker><style>@keyframes ir5Flow{to{stroke-dashoffset:-16}}.flow-line{stroke-dasharray:7 6;animation:ir5Flow 1.35s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="898" height="438" rx="18" fill="#0b1220" stroke="#263449"/><text x="25" y="34" fill="#e5eefb" font-size="19" font-weight="700">Les 5 pourquoi — exemple pédagogique</text><g font-family="Arial, sans-serif"><rect x="130" y="55" width="640" height="45" rx="9" fill="#3a2028" stroke="#fb7185"/><text x="450" y="73" text-anchor="middle" fill="#fecdd3" font-size="11" font-weight="700">SYMPTÔME</text><text x="450" y="90" text-anchor="middle" fill="#fff1f2" font-size="12">Le portail est indisponible</text><path class="flow-line" d="M450 100 V107" stroke="#38bdf8" stroke-width="2" fill="none" marker-end="url(#ir5-arrow)"/><rect x="130" y="108" width="640" height="45" rx="9" fill="#11283c" stroke="#38bdf8"/><text x="450" y="126" text-anchor="middle" fill="#7dd3fc" font-size="11" font-weight="700">POURQUOI 1</text><text x="450" y="143" text-anchor="middle" fill="#e0f2fe" font-size="12">Le service n’obtient plus de connexion à la base</text><path class="flow-line" d="M450 153 V160" stroke="#38bdf8" stroke-width="2" fill="none" marker-end="url(#ir5-arrow)"/><rect x="130" y="161" width="640" height="45" rx="9" fill="#11283c" stroke="#38bdf8"/><text x="450" y="179" text-anchor="middle" fill="#7dd3fc" font-size="11" font-weight="700">POURQUOI 2</text><text x="450" y="196" text-anchor="middle" fill="#e0f2fe" font-size="12">Le pool de connexions est saturé</text><path class="flow-line" d="M450 206 V213" stroke="#38bdf8" stroke-width="2" fill="none" marker-end="url(#ir5-arrow)"/><rect x="130" y="214" width="640" height="45" rx="9" fill="#302817" stroke="#fbbf24"/><text x="450" y="232" text-anchor="middle" fill="#fcd34d" font-size="11" font-weight="700">POURQUOI 3</text><text x="450" y="249" text-anchor="middle" fill="#fef3c7" font-size="12">Certaines connexions ne sont pas libérées sur un chemin d’erreur</text><path class="flow-line" d="M450 259 V266" stroke="#38bdf8" stroke-width="2" fill="none" marker-end="url(#ir5-arrow)"/><rect x="130" y="267" width="640" height="45" rx="9" fill="#302817" stroke="#fbbf24"/><text x="450" y="285" text-anchor="middle" fill="#fcd34d" font-size="11" font-weight="700">POURQUOI 4</text><text x="450" y="302" text-anchor="middle" fill="#fef3c7" font-size="12">Les tests ne couvrent pas les erreurs répétées sous charge</text><path class="flow-line" d="M450 312 V319" stroke="#38bdf8" stroke-width="2" fill="none" marker-end="url(#ir5-arrow)"/><rect x="130" y="320" width="640" height="45" rx="9" fill="#102b27" stroke="#34d399"/><text x="450" y="338" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="700">POURQUOI 5</text><text x="450" y="355" text-anchor="middle" fill="#d1fae5" font-size="12">Les critères de mise en production n’exigent pas ce scénario</text><text x="450" y="402" text-anchor="middle" fill="#94a3b8" font-size="12">Chaque réponse doit être vérifiée : d’autres branches causales peuvent coexister.</text></g></svg></div>

### 11.2 Les pièges des 5 pourquoi

- **Réponse non vérifiée :** « C’est sûrement le réseau » ne constitue pas une preuve.
- **Arrêt trop tôt :** « L’application s’est arrêtée car elle a planté » reformule le symptôme.
- **Blâme individuel :** « Parce qu’un technicien a fait une erreur » n’explique pas pourquoi le processus a permis cette erreur ni comment éviter qu’elle se reproduise.
- **Cause unique forcée :** plusieurs facteurs peuvent être nécessaires pour expliquer la panne.
- **Action qui ne correspond pas à la cause :** former les utilisateurs ne corrigera pas une fuite de connexions démontrée.

Une bonne chaîne causale reste testable. Si la cause proposée est vraie, quelles traces, mesures ou expériences devraient l’étayer ? Quelles observations la contrediraient ?

## 12. Diagramme d’Ishikawa (causes-effets)

Le diagramme d’Ishikawa, appelé aussi diagramme en arêtes de poisson, aide une équipe à organiser plusieurs familles de causes possibles. Il sert à produire et classer des hypothèses, pas à prouver que chacune est responsable.

Pour un incident IT, on peut utiliser des catégories adaptées :

- **Personnes et compétences :** manque de formation, astreinte indisponible, responsabilités ambiguës ;
- **Processus :** absence de revue de changement, tests incomplets, procédures obsolètes ;
- **Technologie :** bug logiciel, configuration erronée, ressource saturée ;
- **Données et configuration :** certificat expiré, seuil incorrect, inventaire incomplet ;
- **Dépendances :** fournisseur, DNS, identité, réseau, base de données ou API externe ;
- **Mesure et supervision :** métrique absente, alerte mal réglée, journaux insuffisants ;
- **Environnement :** alimentation, température, capacité réseau ou variation de charge.

Évite d’imposer mécaniquement des catégories qui ne conviennent pas au problème. Le but est d’explorer les pistes utiles puis de les confronter aux preuves.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 900 380" role="img" aria-label="Diagramme d’Ishikawa simplifié pour rechercher les causes d’un incident applicatif"><defs><marker id="ir6-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#38bdf8"/></marker><style>@keyframes ir6Flow{to{stroke-dashoffset:-18}}.flow-line{stroke-dasharray:7 6;animation:ir6Flow 1.45s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="898" height="378" rx="18" fill="#0b1220" stroke="#263449"/><text x="25" y="33" fill="#e5eefb" font-size="19" font-weight="700">Ishikawa — pistes possibles, à vérifier</text><path d="M75 202 H720" stroke="#38bdf8" stroke-width="3" fill="none"/><path class="flow-line" d="M720 202 H785" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#ir6-arrow)"/><rect x="785" y="165" width="94" height="74" rx="10" fill="#3a2028" stroke="#fb7185"/><text x="832" y="193" fill="#fecdd3" text-anchor="middle" font-size="12" font-weight="700">EFFET</text><text x="832" y="213" fill="#fff1f2" text-anchor="middle" font-size="11">Service</text><text x="832" y="228" fill="#fff1f2" text-anchor="middle" font-size="11">indisponible</text><g stroke-width="2.2" fill="none"><path d="M190 202 L135 112" stroke="#38bdf8"/><path d="M360 202 L305 112" stroke="#34d399"/><path d="M530 202 L475 112" stroke="#fbbf24"/><path d="M190 202 L135 292" stroke="#c084fc"/><path d="M360 202 L305 292" stroke="#60a5fa"/><path d="M530 202 L475 292" stroke="#fb923c"/></g><g font-family="Arial, sans-serif"><rect x="40" y="56" width="194" height="56" rx="8" fill="#11283c" stroke="#38bdf8"/><text x="137" y="77" fill="#7dd3fc" text-anchor="middle" font-size="13" font-weight="700">Technologie</text><text x="137" y="96" fill="#dbeafe" text-anchor="middle" font-size="11">Bug, saturation, configuration</text><rect x="210" y="56" width="194" height="56" rx="8" fill="#102b27" stroke="#34d399"/><text x="307" y="77" fill="#6ee7b7" text-anchor="middle" font-size="13" font-weight="700">Processus</text><text x="307" y="96" fill="#d1fae5" text-anchor="middle" font-size="11">Tests, validation, procédure</text><rect x="380" y="56" width="194" height="56" rx="8" fill="#302817" stroke="#fbbf24"/><text x="477" y="77" fill="#fcd34d" text-anchor="middle" font-size="13" font-weight="700">Supervision</text><text x="477" y="96" fill="#fef3c7" text-anchor="middle" font-size="11">Alertes, métriques, journaux</text><rect x="40" y="292" width="194" height="56" rx="8" fill="#241c36" stroke="#c084fc"/><text x="137" y="313" fill="#d8b4fe" text-anchor="middle" font-size="13" font-weight="700">Personnes</text><text x="137" y="332" fill="#f3e8ff" text-anchor="middle" font-size="11">Compétences, rôles, astreinte</text><rect x="210" y="292" width="194" height="56" rx="8" fill="#17283c" stroke="#60a5fa"/><text x="307" y="313" fill="#93c5fd" text-anchor="middle" font-size="13" font-weight="700">Dépendances</text><text x="307" y="332" fill="#dbeafe" text-anchor="middle" font-size="11">DNS, identité, fournisseur</text><rect x="380" y="292" width="194" height="56" rx="8" fill="#30241b" stroke="#fb923c"/><text x="477" y="313" fill="#fdba74" text-anchor="middle" font-size="13" font-weight="700">Environnement</text><text x="477" y="332" fill="#ffedd5" text-anchor="middle" font-size="11">Charge, énergie, réseau</text></g></svg></div>

### 12.1 Comment utiliser le diagramme

1. Écrire un effet précis à droite : « validation des commandes impossible de 09 h 10 à 09 h 44 ».
2. Inviter les participants à proposer des facteurs possibles sans les présenter comme des faits.
3. Classer les hypothèses dans des familles compréhensibles.
4. Pour chaque hypothèse importante, préciser la preuve nécessaire, la personne qui la recueillera et le délai.
5. Écarter ou confirmer les pistes à mesure que les éléments sont analysés.
6. Retenir les causes démontrées, les facteurs contributifs plausibles et les inconnues résiduelles.

## 13. Construire une chronologie fiable

Une chronologie place les événements sur une ligne temporelle commune. Elle aide à distinguer ce qui s’est passé avant, pendant et après l’incident. Elle est essentielle lorsque plusieurs équipes observent des éléments différents.

Exemple de questions :

- Quand le premier symptôme mesurable est-il apparu ?
- Quand la première alerte a-t-elle été déclenchée, et quand a-t-elle été reçue ?
- Quel changement a été effectué avant l’incident ? À quelle heure réelle ?
- Quand la première action de diagnostic a-t-elle commencé ?
- Quand un contournement a-t-il été tenté, et quel effet a-t-il eu ?
- Quand le service est-il revenu à un niveau acceptable ?
- Y a-t-il eu une récidive, une dégradation secondaire ou un risque qui persiste ?

Attention aux horloges désynchronisées entre serveurs, consoles et appareils. Note la source de chaque heure et, quand c’est nécessaire, l’écart de synchronisation connu. Ne déduis pas une causalité du seul fait que deux événements sont proches dans le temps : une modification récente est une piste importante, mais elle doit être reliée au mécanisme de panne par des éléments vérifiables.

## 14. Le rapport post-incident

Le rapport post-incident (souvent appelé revue post-incident ou *postmortem*) documente ce qui s’est passé, l’impact, les mesures de rétablissement, les causes soutenues par les preuves et les actions d’amélioration.

Un bon rapport est orienté vers l’apprentissage. Il évite l’humiliation publique, les accusations et les conclusions non démontrées. Une culture sans blâme n’empêche pas la responsabilité : elle permet d’examiner les décisions, les contraintes, les outils et les processus qui ont rendu l’événement possible, puis de décider ce qui doit changer.

### 14.1 Structure recommandée

1. **Résumé exécutif :** une ou deux phrases compréhensibles par un lecteur non technique.
2. **Impact :** services, utilisateurs, transactions, sites, durée et éventuelles conséquences sur les données ou la sécurité.
3. **Chronologie :** détection, décisions, actions, escalades, contournement et rétablissement.
4. **Détection :** comment l’incident a été constaté, et si la supervision a bien fonctionné.
5. **Rétablissement :** action qui a ramené le service à un niveau acceptable et critères de validation.
6. **Causes et facteurs contributifs :** ce qui est démontré, ce qui reste probable et les incertitudes.
7. **Ce qui a bien fonctionné :** collaboration, alertes utiles, documentation, contournement sûr.
8. **Ce qui doit être amélioré :** délais, visibilité, procédures, tests ou capacité.
9. **Actions :** responsable, échéance, priorité, critère de réussite et preuve de vérification.
10. **Liens :** tickets d’incident, problème, changement, tableaux de bord et documents de suivi accessibles aux personnes autorisées.

### 14.2 Exemple de résumé

> Le 22 octobre, entre 09 h 10 et 09 h 44, le portail de commandes a refusé une partie des nouvelles transactions. Environ 35 utilisateurs ont été affectés ; aucun élément disponible ne signale une perte de données, point confirmé par une vérification post-rétablissement. Un contournement a rétabli le service. L’analyse a identifié une saturation du pool de connexions dans un chemin d’erreur, tandis que les tests de mise en production ne couvraient pas ce scénario sous charge. Les actions retenues portent sur la correction du code, les tests de non-régression, la supervision du pool et les critères de déploiement.

Cet exemple est fictif. Dans un rapport réel, les chiffres, conclusions et assertions relatives aux données doivent être soutenus par les preuves disponibles.

## 15. Transformer la RCA en actions efficaces

Une RCA n’a de valeur que si elle débouche sur des actions concrètes, suivies et vérifiées. Les actions ne doivent pas se limiter à « faire attention », « surveiller davantage » ou « former l’équipe » sans préciser le résultat attendu.

Une bonne action contient :

- **un verbe précis :** ajouter, corriger, automatiser, limiter, mesurer, tester, documenter ;
- **un responsable identifié :** une personne ou une équipe qui accepte le suivi ;
- **une échéance réaliste :** date prévue et dépendances ;
- **un critère de réussite :** ce qui devra être observé lorsque l’action sera achevée ;
- **une preuve :** test automatisé, capture de tableau de bord, résultat de simulation, revue validée ou lien vers le changement ;
- **une évaluation du risque :** effet potentiel de l’action et plan de retour arrière si nécessaire.

| Action vague | Action plus vérifiable |
|---|---|
| Améliorer la supervision. | Ajouter une alerte sur l’utilisation du pool de connexions à 80 % pendant 5 minutes et tester son déclenchement en préproduction avant le 15 novembre. |
| Faire plus de tests. | Ajouter un test automatisé simulant une erreur après acquisition d’une connexion et vérifier que la connexion est libérée dans tous les cas. |
| Former l’équipe. | Mettre à jour la procédure de mise en production, faire une session pratique et faire valider la checklist par l’équipe avant le prochain déploiement. |
| Éviter que cela se reproduise. | Corriger le chemin d’erreur, déployer selon le processus de changement, puis observer le taux d’erreur et le nombre de connexions actives durant une période définie. |

Il est souvent préférable de répartir les actions entre plusieurs couches : éliminer la cause technique, améliorer la détection, réduire l’impact, rendre la réponse plus rapide et améliorer le processus qui permet de déployer en sécurité.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 900 325" role="img" aria-label="Démarche RCA : preuves, hypothèses, tests, actions puis vérification"><defs><marker id="ir7-arrow" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#38bdf8"/></marker><marker id="ir7-green" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 Z" fill="#34d399"/></marker><style>@keyframes ir7Flow{to{stroke-dashoffset:-18}}.flow-line{stroke-dasharray:8 6;animation:ir7Flow 1.4s linear infinite}@media(prefers-reduced-motion:reduce){.flow-line{animation:none}}</style></defs><rect x="1" y="1" width="898" height="323" rx="18" fill="#0b1220" stroke="#263449"/><text x="25" y="34" fill="#e5eefb" font-size="19" font-weight="700">Une RCA n’est pas terminée avant la vérification</text><g font-family="Arial, sans-serif" text-anchor="middle"><rect x="28" y="82" width="145" height="82" rx="11" fill="#11283c" stroke="#38bdf8"/><text x="100" y="108" fill="#7dd3fc" font-size="14" font-weight="700">1. Preuves</text><text x="100" y="130" fill="#dbeafe" font-size="12">Journaux, mesures</text><text x="100" y="147" fill="#dbeafe" font-size="12">chronologie</text><rect x="198" y="82" width="145" height="82" rx="11" fill="#152338" stroke="#60a5fa"/><text x="270" y="108" fill="#93c5fd" font-size="14" font-weight="700">2. Hypothèses</text><text x="270" y="130" fill="#dbeafe" font-size="12">Cause proposée</text><text x="270" y="147" fill="#dbeafe" font-size="12">et facteurs</text><rect x="368" y="82" width="145" height="82" rx="11" fill="#302817" stroke="#fbbf24"/><text x="440" y="108" fill="#fcd34d" font-size="14" font-weight="700">3. Tester</text><text x="440" y="130" fill="#fef3c7" font-size="12">Confirmer ou</text><text x="440" y="147" fill="#fef3c7" font-size="12">rejeter</text><rect x="538" y="82" width="145" height="82" rx="11" fill="#241c36" stroke="#c084fc"/><text x="610" y="108" fill="#d8b4fe" font-size="14" font-weight="700">4. Agir</text><text x="610" y="130" fill="#f3e8ff" font-size="12">Correction, détection</text><text x="610" y="147" fill="#f3e8ff" font-size="12">et réduction d’impact</text><rect x="708" y="82" width="164" height="82" rx="11" fill="#102b27" stroke="#34d399"/><text x="790" y="108" fill="#6ee7b7" font-size="14" font-weight="700">5. Vérifier</text><text x="790" y="130" fill="#d1fae5" font-size="12">Critère mesurable</text><text x="790" y="147" fill="#d1fae5" font-size="12">et preuve conservée</text><path class="flow-line" d="M173 123 H192 M343 123 H362 M513 123 H532 M683 123 H702" stroke="#38bdf8" stroke-width="2.3" fill="none" marker-end="url(#ir7-arrow)"/><path class="flow-line" d="M790 164 V222 H440 V172" stroke="#34d399" stroke-width="2.2" fill="none" marker-end="url(#ir7-green)"/><rect x="92" y="235" width="716" height="58" rx="10" fill="#111d2e" stroke="#334155"/><text x="450" y="258" fill="#e5eefb" text-anchor="middle" font-size="14" font-weight="700">Si le test échoue, on réévalue les hypothèses</text><text x="450" y="278" fill="#afc1d3" text-anchor="middle" font-size="12">Si les actions réussissent, on observe le service pour vérifier l’effet dans le temps.</text></g></svg></div>

## 16. Erreurs fréquentes à éviter

1. **Clôturer sans vérifier le résultat.** Le service doit être testé selon des critères définis, pas seulement après l’exécution d’une commande.
2. **Confondre restauration et suppression de la cause.** Un service redémarré peut rester vulnérable à la même panne.
3. **Écrire une cause avant de recueillir les preuves.** Une hypothèse n’est pas une conclusion.
4. **Blâmer une personne trop vite.** Les erreurs humaines se produisent dans un contexte de conception, d’outils, de charge et de procédures.
5. **Omettre les horaires.** Sans chronologie, on ne peut pas mesurer les délais ni comparer les versions des événements.
6. **Changer plusieurs choses en même temps.** Cela complique l’identification de la modification qui a eu un effet.
7. **Faire une RCA sans actions suivies.** Une réunion sans responsable, échéance et critère de réussite produit peu d’amélioration.
8. **Surveiller uniquement la disponibilité technique.** Un serveur actif n’assure pas nécessairement que le service métier fonctionne.
9. **Masquer une alerte plutôt que corriger le problème.** La suppression du signal peut faire disparaître la visibilité sans réduire le risque.
10. **Traiter chaque ticket comme un événement isolé.** Les incidents récurrents doivent être corrélés et reliés à une investigation de problème.

## 17. Mesures utiles pour progresser

Les mesures aident à comprendre la performance et les faiblesses du processus. Elles doivent être interprétées ensemble : un indicateur isolé peut donner une image trompeuse.

- **Volume d’incidents :** combien d’incidents ont été déclarés par service, catégorie, site ou période ?
- **Temps de première réponse :** délai entre le signalement et une première prise en charge utile. Une réponse automatique seule n’est pas toujours une réponse opérationnelle.
- **Temps de rétablissement :** délai entre le début de l’impact et le retour du service au niveau accepté. Il faut définir précisément les horodatages utilisés.
- **Taux de récurrence :** fréquence de réapparition de symptômes ou de causes similaires.
- **Incidents majeurs :** nombre, durée, impact et tendances.
- **Qualité de la détection :** temps écoulé entre le début réel et la détection ; proportion d’incidents découverts par les utilisateurs plutôt que par la supervision.
- **Actions RCA à temps :** proportion d’actions achevées à échéance et validées selon les critères prévus.
- **Réouvertures :** incidents déclarés résolus puis rouverts parce que le problème persistait ou que la validation était insuffisante.

Évite de transformer ces mesures en objectifs rigides qui incitent à fermer trop vite les tickets, minimiser les priorités ou décourager les signalements. Le but est d’améliorer le service, pas d’optimiser artificiellement un tableau de bord.

### 17.1 MTTR : préciser le sens

Dans différentes équipes, l’acronyme MTTR peut désigner *Mean Time to Restore* (temps moyen de rétablissement), *Mean Time to Repair* (temps moyen de réparation), voire d’autres variantes. Dans un rapport, écris le terme complet et la définition utilisée. Précise le point de départ, le point d’arrivée, les tickets inclus et le traitement des incidents encore ouverts. Sans définition cohérente, comparer des chiffres entre équipes ou périodes peut être trompeur.

## 18. Atelier pratique complet

### Scénario

À 08 h 55, le centre de support reçoit des signalements indiquant que les utilisateurs ne peuvent plus accéder au partage de fichiers `\filesrv\commun`. L’accès Internet fonctionne encore. À 09 h 02, 18 utilisateurs et deux équipes métier sont concernés. La supervision signale une hausse des erreurs d’accès au serveur. Une modification du pare-feu a été réalisée la veille, mais aucun lien causal n’est confirmé. À 09 h 20, l’équipe réseau découvre des pertes de paquets entre un sous-réseau client et le serveur. Une route de secours permet de rétablir l’accès à 09 h 38. L’analyse doit se poursuivre.

### Étape A — Enregistrer

**Titre :** « Accès au partage `\\filesrv\commun` impossible pour plusieurs utilisateurs ».  
**Début connu :** 08 h 55.  
**Impact connu à 09 h 02 :** 18 utilisateurs, deux équipes.  
**Services encore fonctionnels :** accès Internet.  
**Priorité provisoire :** à déterminer selon la matrice locale, la criticité des fichiers, l’ampleur de l’impact et les délais métier.  
**Hypothèse non confirmée :** route ou règle réseau.  
**Prochaine étape :** tester la résolution de nom, la connectivité, les routes et les journaux en corrélant les résultats par sous-réseau.

### Étape B — Diagnostiquer sans sauter aux conclusions

Questions utiles :

- Le nom `filesrv` se résout-il vers l’adresse attendue ?
- Tous les utilisateurs sont-ils affectés, ou uniquement ceux d’un sous-réseau ?
- L’adresse du serveur répond-elle ? La réponse dépend-elle du protocole testé ?
- Observe-t-on des pertes, des délais ou des refus explicites ?
- Quel changement a été fait la veille, par qui, dans quel périmètre et avec quels résultats de validation ?
- La route de secours change-t-elle le chemin, le filtrage ou les deux ?

Le résultat d’un `ping` ne suffit pas à prouver que le partage SMB fonctionne. Il faut tester le service réellement concerné et suivre la procédure de diagnostic appropriée, avec les autorisations nécessaires.

### Étape C — Rétablir

À 09 h 38, la route de secours rend l’accès de nouveau possible. L’équipe doit valider le partage avec un compte autorisé, ouvrir un fichier de test, vérifier les erreurs et surveiller les métriques. Elle doit aussi préciser le risque résiduel : la route de secours est-elle durable, temporaire, moins performante ou moins sécurisée ? L’opération doit être documentée comme contournement tant que sa correction permanente n’est pas validée.

### Étape D — RCA après rétablissement

Hypothèses possibles :

- la modification du pare-feu a affecté le flux concerné ;
- une annonce ou une route a été modifiée ;
- une interface ou un lien présente des erreurs ;
- un équipement a changé de comportement ;
- un autre événement temporel est corrélé sans être causal.

Éléments à vérifier : configuration avant/après, journaux de pare-feu, tables de routage, compteurs d’interface, captures ou tests réseau autorisés, et comparaison entre le chemin normal et le chemin de secours. Si aucune preuve ne relie la modification du pare-feu aux pertes observées, elle ne doit pas être écrite comme cause confirmée.

### Étape E — Actions possibles si la cause est confirmée

- corriger la configuration fautive et l’appliquer selon la procédure de changement ;
- reproduire le scénario dans un environnement de test lorsque c’est possible ;
- ajouter un test de validation du partage depuis les sous-réseaux concernés ;
- alerter sur les pertes de paquets ou les erreurs d’interface pertinentes ;
- mettre à jour la documentation de routage et le plan de retour arrière ;
- surveiller le service après la correction et confirmer la fermeture du problème.

Ne choisis pas ces actions automatiquement : ne conserve que celles qui correspondent aux causes démontrées et aux risques réellement identifiés.

## 19. Modèles à réutiliser

### 19.1 Modèle de ticket d’incident

```text
ID / Référence :
Titre factuel :
Date et heure du début (avec fuseau si nécessaire) :
Date et heure du signalement :
Service / CI concerné :
Demandeur / contact autorisé :
Utilisateurs, sites ou processus affectés :
Description factuelle des symptômes :
Message d’erreur / preuve jointe :
Impact :
Urgence :
Priorité et justification :
Catégorie :
Changements récents à vérifier :
Tests effectués et résultats :
Hypothèses (non confirmées) :
Contournement et risques :
Équipe / responsable actuel :
Dernière mise à jour communiquée :
Prochaine mise à jour prévue :
Critères de rétablissement :
Heure de rétablissement et validation :
Solution appliquée :
Problème / changement lié :
Résultat final et motif de clôture :
```

### 19.2 Modèle de compte rendu RCA

```text
Titre de l’incident :
Résumé en langage simple :
Date, durée et période d’impact :
Services / utilisateurs / processus touchés :
Impact mesuré et conséquences connues :
Comment l’incident a-t-il été détecté ?
Chronologie avec sources des horodatages :
Actions de réponse et résultats :
Solution de contournement :
Critères utilisés pour confirmer le rétablissement :
Cause directe confirmée et preuves :
Cause(s) racine(s) actionnable(s) et preuves :
Facteurs contributifs :
Hypothèses rejetées :
Incertitudes restantes :
Ce qui a bien fonctionné :
Ce qui doit être amélioré :
Actions / responsable / échéance / priorité :
Critère de réussite pour chaque action :
Preuve de validation et date de revue :
Liens vers les tickets, problèmes et changements :
```

### 19.3 Tableau de suivi des actions

| ID | Action | Type | Responsable | Échéance | Critère de réussite | État |
|---|---|---|---|---|---|---|
| A1 | Corriger la fuite de connexions | Corrective | Équipe applicative | À définir | Test d’erreur et de charge réussi | À planifier |
| A2 | Ajouter une alerte de saturation | Détection | Équipe exploitation | À définir | Alerte testée et reçue par l’astreinte | À planifier |
| A3 | Réviser la checklist de déploiement | Prévention | Responsable de mise en production | À définir | Checklist adoptée et auditée | À planifier |

Ce tableau est un exemple. Dans un environnement réel, les responsables, délais, dépendances et critères doivent être convenus avec les équipes concernées.

## 20. Exercices de compréhension

### Exercice 1 — Classer les situations

Pour chaque situation, indique s’il s’agit principalement d’un incident, d’une demande de service, d’un problème ou d’un changement. Plusieurs enregistrements peuvent être liés.

A. Un nouvel employé demande un compte standard.  
B. La messagerie ne reçoit plus de messages.  
C. Trois interruptions de service similaires ont été constatées après les pics de charge ; l’équipe recherche une cause commune.  
D. L’équipe prévoit de modifier la configuration du proxy pour corriger la cause identifiée.

**Corrigé :** A = demande de service ; B = incident ; C = problème / investigation ; D = changement. Le changement peut être lié au problème et aux incidents d’origine.

### Exercice 2 — Symptôme ou cause ?

Classe les éléments suivants : « le navigateur affiche 502 », « le pool de connexions est saturé », « aucune alerte n’est configurée sur le pool », « redémarrer le service a restauré l’accès ».

**Corrigé indicatif :** « 502 » est un symptôme observable ; la saturation peut être une cause directe si les données le confirment ; l’absence d’alerte est un facteur contributif qui peut retarder la détection ; le redémarrage décrit une action de rétablissement, pas la cause racine.

### Exercice 3 — Priorité

Un service de paie devient indisponible une heure avant une échéance de traitement. Seulement deux personnes sont directement bloquées, mais elles ne peuvent pas terminer le processus critique. Comment choisir la priorité ?

**Corrigé :** ne pas se limiter au nombre d’utilisateurs. Évaluer la criticité du processus, le temps restant avant l’échéance, les solutions de secours et les conséquences d’un retard. Appliquer la matrice et les critères d’incident majeur locaux, puis documenter la justification.

### Exercice 4 — 5 pourquoi

Un ordinateur portable perd régulièrement l’accès au Wi-Fi. La réinstallation du pilote corrige le problème pendant deux jours, puis il revient. Propose trois questions « pourquoi » et au moins deux preuves à recueillir avant de conclure.

**Pistes de corrigé :** le problème survient-il sur un point d’accès ou tous ? L’événement correspond-il à une veille/réveil, à une mise à jour ou à un changement de signal ? Le journal WLAN montre-t-il une désassociation, une erreur d’authentification ou une coupure radio ? Vérifier les journaux, la version du pilote, les mises à jour, le comportement d’autres appareils, le signal et les heures exactes. La répétition après réinstallation ne prouve pas que le pilote est la cause profonde.

### Exercice 5 — Action de prévention

RCA : les utilisateurs ne sont avertis qu’après avoir signalé eux-mêmes une indisponibilité de l’application. Propose une action mesurable.

**Corrigé possible :** définir un test synthétique qui exécute un parcours métier sans modifier de données sensibles, l’évaluer toutes les quelques minutes, puis vérifier en préproduction qu’une panne de test déclenche une alerte et qu’elle est reçue par le bon canal. Définir un seuil et un responsable. L’action finale doit correspondre à l’architecture et aux règles de sécurité.

## 21. Quiz final

Choisis la meilleure réponse pour chaque question.

1. Quel est l’objectif principal de la gestion des incidents ?  
   A. Trouver systématiquement la cause racine avant d’agir.  
   B. Minimiser l’impact en rétablissant le service aussi rapidement que possible.  
   C. Créer un rapport détaillé pour chaque demande standard.

2. Quelle affirmation est correcte ?  
   A. Un problème et un incident sont exactement la même chose.  
   B. Un incident peut être rétabli avant que sa cause racine soit connue.  
   C. Une erreur connue signifie que la correction définitive est déjà appliquée.

3. Qu’est-ce qu’une solution de contournement ?  
   A. Une mesure qui réduit temporairement l’impact sans nécessairement supprimer la cause.  
   B. Une suppression automatique du ticket.  
   C. Une preuve suffisante de la cause racine.

4. Pourquoi documenter les tests effectués ?  
   A. Pour rendre le ticket plus long.  
   B. Pour permettre la reprise, éviter les répétitions inutiles et conserver les résultats.  
   C. Pour éviter toute escalade.

5. Dans une RCA, que signifie « cause confirmée » ?  
   A. Une explication qui semble plausible à la personne la plus expérimentée.  
   B. Une hypothèse étayée par des preuves pertinentes et cohérentes.  
   C. Le premier changement récent trouvé.

6. Le diagramme d’Ishikawa sert principalement à :  
   A. Prouver automatiquement chaque cause.  
   B. Organiser des familles de causes possibles à vérifier.  
   C. Calculer la priorité du ticket.

7. Une bonne action post-incident doit inclure :  
   A. Seulement le nom de l’équipe.  
   B. Un résultat attendu, un responsable, une échéance et une preuve de vérification.  
   C. Une promesse générale de faire mieux.

8. Quand faut-il escalader ?  
   A. Seulement après avoir épuisé toutes les commandes possibles.  
   B. Lorsque les critères de risque, de priorité ou de compétence dépassent le cadre de prise en charge.  
   C. Jamais, si le ticket a déjà un propriétaire.

9. Un redémarrage rétablit le service. Cela prouve-t-il la cause racine ?  
   A. Oui, dans tous les cas.  
   B. Non, le redémarrage est une action ; il faut investiguer le mécanisme de la panne.  
   C. Oui, si l’application est disponible cinq minutes après.

10. Quel est le bon objectif d’une revue post-incident ?  
    A. Trouver une personne à sanctionner.  
    B. Apprendre, réduire les risques et décider d’actions suivies.  
    C. Éviter de parler de ce qui n’a pas fonctionné.

### Réponses du quiz

1. **B** — la gestion des incidents cherche à minimiser l’impact et à rétablir le service.  
2. **B** — le rétablissement peut précéder l’identification de la cause.  
3. **A** — le contournement atténue l’impact ; ce n’est pas nécessairement une correction durable.  
4. **B** — le contexte et les résultats doivent être réutilisables.  
5. **B** — une cause doit être étayée, pas simplement supposée.  
6. **B** — le diagramme aide à explorer et organiser des hypothèses.  
7. **B** — il faut rendre l’action suivable et vérifiable.  
8. **B** — ne pas attendre si le risque ou le niveau de compétence exige une prise en charge supérieure.  
9. **B** — le retour du service ne prouve pas la cause racine.  
10. **B** — la revue doit produire un apprentissage concret, dans un cadre sans blâme.

## 22. Glossaire

- **Incident :** interruption non planifiée ou dégradation d’un service.
- **ITSM :** gestion des services informatiques.
- **ITIL :** ensemble de bonnes pratiques de gestion des services IT.
- **RCA :** analyse des causes racines.
- **Problème :** cause ou cause potentielle d’un ou de plusieurs incidents.
- **Erreur connue :** problème analysé et documenté, avec cause connue ou solution de contournement disponible.
- **Contournement :** solution temporaire ou mesure qui réduit l’impact sans forcément supprimer la cause.
- **Escalade :** sollicitation d’une équipe plus spécialisée ou d’un niveau de décision adapté.
- **Impact :** ampleur des conséquences du dysfonctionnement.
- **Urgence :** délai avant lequel l’impact devient inacceptable ou augmente.
- **Priorité :** ordre de traitement déterminé selon les règles définies.
- **Incident majeur :** incident dont l’impact ou le risque exige une coordination renforcée selon les critères locaux.
- **Cause proximale :** facteur qui a directement déclenché l’événement observé.
- **Facteur contributif :** condition qui a rendu l’incident plus probable ou plus grave.
- **Postmortem / revue post-incident :** analyse structurée pour comprendre l’incident et planifier des améliorations.
- **SLA :** accord de niveau de service qui définit des objectifs et responsabilités convenus.
- **MTTR :** acronyme dont le sens doit être explicité selon la mesure utilisée.
- **Action corrective :** action qui supprime ou réduit une cause identifiée.
- **Action préventive :** action qui réduit le risque d’occurrence future.
- **Action de détection :** action qui améliore la rapidité ou la qualité de la détection.

## 23. Checklist rapide du technicien

### Pendant l’incident

- [ ] J’ai confirmé le symptôme et son début approximatif.
- [ ] J’ai évalué qui et quoi est affecté.
- [ ] J’ai enregistré des faits observables, pas une cause inventée.
- [ ] J’ai choisi la priorité avec les critères de l’organisation.
- [ ] J’ai conservé les éléments utiles sans exposer de données sensibles.
- [ ] J’ai exécuté des tests ciblés et noté leurs résultats.
- [ ] J’ai escaladé au bon moment.
- [ ] Toute action risquée a suivi la procédure d’autorisation applicable.
- [ ] J’ai communiqué l’état, l’action en cours et la prochaine mise à jour.
- [ ] Le service a été testé selon des critères d’acceptation concrets.

### Après le rétablissement

- [ ] Le ticket contient la chronologie, les actions et la solution appliquée.
- [ ] Le contournement et les risques résiduels sont documentés.
- [ ] Les incidents similaires ont été recherchés.
- [ ] Une RCA est déclenchée si les critères le justifient.
- [ ] Les causes sont séparées des hypothèses et soutenues par des preuves.
- [ ] Les actions ont des responsables, des échéances et des critères de réussite.
- [ ] Les actions terminées sont vérifiées et les résultats sont conservés.
- [ ] La connaissance acquise est rendue accessible aux personnes autorisées.

## 24. Références et lectures complémentaires

Les ressources suivantes aident à approfondir les notions présentées. Les guides officiels ITIL/PeopleCert peuvent être soumis à des conditions d’accès ou de licence ; ce cours est un support pédagogique indépendant et ne reproduit pas un guide officiel.

- **PeopleCert — ITIL 4 Practitioner: Incident Management :** [présentation officielle de la pratique Incident Management](https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil4-practices-incident-management-3684). Présente les compétences et activités associées à la gestion des incidents.
- **PeopleCert — ITIL 4 Practitioner: Problem Management :** [présentation officielle de la pratique Problem Management](https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil4-practices-problem-management-3688). Explique l’objectif de réduire la probabilité et l’impact des incidents en identifiant les causes et en gérant les contournements et erreurs connues.
- **AXELOS / ITIL 4 — Incident Management Practice Guide :** [document de référence disponible en ligne](https://s3.amazonaws.com/thinkific/file_uploads/381835/attachments/aba/2cf/226/Incident-management.pdf). Vérifier les droits et conditions d’utilisation associés à cette copie.
- **Atlassian — Root Cause Analysis :** [guide d’analyse des causes racines](https://www.atlassian.com/work-management/project-management/root-cause-analysis). Présentation de méthodes pour relier les symptômes à des causes actionnables.
- **Atlassian — Postmortems :** [guide de revue post-incident](https://www.atlassian.com/incident-management/handbook/postmortems). Conseils pour documenter une chronologie, utiliser les 5 pourquoi et suivre les actions après un incident.
- **Atlassian Team Playbook — 5 Whys Analysis :** [méthode des cinq pourquoi](https://www.atlassian.com/team-playbook/plays/5-whys). Rappelle que le nombre de questions n’est pas une limite absolue et qu’il faut valider la cause proposée.

### Pour continuer après ce niveau

Le niveau débutant apprend à exécuter le processus et à distinguer les concepts. Au niveau intermédiaire, tu pourras approfondir la gestion des incidents majeurs, les modèles de priorisation, la corrélation d’incidents, les erreurs connues, les SLA/SLO, les techniques de facilitation RCA et les indicateurs. Le niveau expert pourra aborder la gouvernance de la pratique, la résilience, l’analyse multi-factorielle, les chaînes de dépendance et la mesure de l’efficacité des actions sur plusieurs mois.

---

**À retenir :** un ticket correctement rempli facilite le diagnostic ; une priorité justifiée facilite la décision ; une communication régulière crée de la confiance ; une RCA fondée sur des preuves transforme une panne en opportunité d’amélioration. Le bon résultat n’est pas simplement que le service fonctionne de nouveau : c’est que l’organisation comprenne ce qui s’est passé, réduise le risque et puisse vérifier les progrès réalisés.
