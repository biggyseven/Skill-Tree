# Protocoles industriels Modbus & PROFINET — Expert

## Mise en contexte : concevoir un système dont les données restent fiables sous contrainte

Au niveau expert, l’objectif n’est plus simplement d’activer une communication. Il faut concevoir, vérifier et exploiter une architecture où les échanges restent déterministes au regard du besoin fonctionnel, où les erreurs sont détectables, où les conséquences d’une panne sont connues et où les changements peuvent être réalisés sans introduire un risque inacceptable pour le procédé.

Modbus et PROFINET occupent des positions différentes dans cette architecture. Modbus fournit un modèle applicatif relativement simple fondé sur des requêtes, des réponses, des codes de fonction et une carte de données. PROFINET organise des relations d’E/S, l’ingénierie des périphériques, les données cycliques, les services acycliques, les diagnostics et plusieurs classes de communication temps réel. Les intégrer dans un même système impose donc de maîtriser simultanément la signification métier des données, la temporalité, les contraintes des équipements, l’architecture réseau et la gouvernance des changements.

> **Encadré de mise en contexte.** Une communication peut être « en ligne » tout en étant impropre au procédé : registre interprété avec le mauvais signe, donnée vieille mais encore affichée, cycle qui ne respecte plus le besoin, écriture non autorisée, périphérique de remplacement mal identifié ou passerelle qui traduit les requêtes avec des délais excessifs. L’expert doit définir les critères de bon fonctionnement avant la mise en service et recueillir des preuves vérifiables pendant les essais.

Les scénarios pratiques de ce cours sont destinés à la simulation, à un banc isolé ou à un périmètre explicitement autorisé. Ils ne recommandent pas de tester des écritures, du fuzzing, des scans actifs ni des perturbations sur un système industriel en production sans procédure d’autorisation et d’analyse de risque.

## Objectifs pédagogiques

À la fin de ce niveau, tu seras capable de :

- concevoir une architecture combinant E/S PROFINET, dispositifs Modbus et supervision ;
- formaliser un contrat de données et démontrer la cohérence du mapping ;
- analyser la structure et la chronologie d’une transaction Modbus TCP, RTU ou passant par une passerelle ;
- dimensionner un budget de polling et identifier les goulots d’étranglement ;
- évaluer le compromis entre cycle, charge, redondance et disponibilité pour PROFINET ;
- diagnostiquer des problèmes de topologie, de relation d’E/S, de qualité et de temps de communication ;
- élaborer une stratégie d’observabilité et un plan de capture non intrusif ;
- appliquer la défense en profondeur, le moindre privilège et la gestion de changement à un réseau de contrôle ;
- rédiger un plan de test, des critères d’acceptation et un retour arrière ;
- justifier les choix d’architecture par des exigences mesurables plutôt que par des préférences de marque.

## 1. Partir des exigences du procédé

### 1.1 Les questions à résoudre avant de choisir un mécanisme

Une architecture de communication industrielle doit répondre à des questions fonctionnelles et temporelles :

- Quelle variable est transférée, par qui est-elle produite et qui l’utilise ?
- Quelle est sa conséquence physique si elle est périmée, fausse, perdue ou répétée ?
- Quelle fraîcheur de donnée est nécessaire ? Quelle durée d’interruption est acceptable ?
- Quelle est la réaction correcte à la perte de communication : maintien contrôlé, repli, arrêt maîtrisé, alarme ou autre comportement défini par l’analyse de risque ?
- Les commandes à distance sont-elles nécessaires ? Quelles identités, plages, états et autorisations les limitent ?
- Quelle configuration et quel firmware sont qualifiés ?
- Quelles preuves permettront de conclure que le système satisfait ses exigences ?

La réponse varie selon le cas. Un compteur d’énergie lu toutes les quelques secondes ne doit pas automatiquement partager les paramètres d’une boucle de commande rapide. Une valeur utilisée dans une fonction de protection ne doit pas être traitée comme une simple statistique de supervision. Les fonctions de sécurité instrumentées doivent suivre leur propre cycle de vie et leurs exigences de conception : la présence de PROFINET ou de Modbus ne rend pas, par elle-même, une fonction conforme à une exigence de sécurité fonctionnelle.

### 1.2 Classer les données par criticité et temporalité

| Classe illustrative | Exemples | Besoin dominant | Précaution de conception |
|---|---|---|---|
| A — Commande/retour cyclique | E/S d’une machine, états de commande | Cycle et comportement à la perte déterminés | Utiliser la technologie et le matériel adaptés au temps de cycle requis |
| B — Paramètre de procédé | Consigne autorisée, mode de fonctionnement | Cohérence, autorisation, journalisation et validation | Restreindre les écritures et contrôler leur effet physique |
| C — Mesure de supervision | Pression, énergie, température historisée | Exactitude, qualité, âge de la donnée | Documenter échelle, unité, horodatage et qualité |
| D — Diagnostic/maintenance | Codes défaut, version, compteurs | Disponibilité à la demande | Privilégier la collecte approuvée, limiter la charge et garder les traces |
| E — Donnée de sécurité | Informations utilisées par une fonction de sécurité | Exigences propres à l’analyse de risque et au système qualifié | Ne pas remplacer une fonction de sécurité par un simple échange standard non qualifié |

Cette classification guide le choix du mécanisme, les règles de flux, la priorité des diagnostics et l’acceptation des pannes.

## 2. Concevoir un contrat de données Modbus robuste

### 2.1 Le mapping comme interface versionnée

Dans une intégration durable, la table Modbus doit être gérée comme un artefact d’ingénierie versionné, pas comme une feuille personnelle. Elle doit indiquer le modèle de l’équipement, la révision documentaire, les fonctions autorisées, les adresses de référence, les offsets attendus par le client, les types numériques, le format des registres, les unités, les limites, la fréquence demandée, la qualité et le comportement en défaut.

Exemple de modèle de fiche :

| Champ | Exemple fictif | Validation exigée |
|---|---|---|
| Tag métier | `PUMP_01_SPEED_FB` | Nom unique et propriétaire fonctionnel |
| Source | Variateur VFD-01, firmware spécifié | Confirmer modèle/révision |
| Fonction | 04 — Input Registers | Vérifier la fonction supportée |
| Adresse documentée | Référence `30021` dans la notice | Vérifier la convention de référence |
| Offset client | `20` si base zéro | Valider par lecture de référence en environnement de test |
| Taille/type | Entier non signé 16 bits | Vérifier la représentation du fabricant |
| Conversion | `brut × 0,1 = tr/min` | Vérifier unité, plage et facteur |
| Qualité | Bit de statut séparé / timeout | Définir le comportement en défaut |
| Période | 500 ms dans le scénario de test | Justifier par la fraîcheur attendue et la charge |
| Écriture | Interdite depuis la supervision | Vérifier les capacités, règles de flux et séparation fonctionnelle |

La référence constructeur et l’offset dans le client doivent apparaître séparément. Cette simple discipline évite une catégorie fréquente d’erreurs : appliquer un décalage deux fois, ou ne l’appliquer nulle part.

### 2.2 Modbus TCP : analyse de transaction et corrélation

La séquence suivante est le modèle de base d’une requête de lecture :

```text
Client Modbus TCP                      Serveur Modbus TCP
        │                                      │
        │ TCP session/flux                     │
        │                                      │
        │ MBAP: Transaction ID = 0x0042         │
        │ Unit ID, FC=03, offset=0x0010, qty=2  │
        ├─────────────────────────────────────►│
        │                                      │ traite la requête
        │ MBAP: Transaction ID = 0x0042         │
        │ FC=03, byte count=4, deux registres   │
        ◄─────────────────────────────────────┤
        │                                      │
```

La corrélation par Transaction ID aide le client à associer une réponse à une requête, surtout lorsque l’implémentation permet plusieurs transactions en vol. Il ne faut toutefois pas conclure qu’un serveur accepte une concurrence illimitée. Les limites de connexions, la gestion des requêtes en attente, la charge CPU, le délai de réponse et le comportement de l’équipement sont spécifiques au modèle.

Une analyse de capture doit examiner la séquence temporelle, les requêtes sans réponse, les réponses tardives, les réutilisations de connexion, les identifiants de transaction, les codes de fonction, les quantités demandées, les exceptions et les éventuels resets TCP. L’absence de réponse dans une capture ne prouve pas à elle seule que le serveur a ignoré la requête : la capture peut avoir été prise au mauvais endroit, le trafic peut être asymétrique ou un filtre peut l’avoir exclu.

### 2.3 Modbus RTU : contraintes de trame et de bus

Sur une liaison série, le diagnostic porte aussi sur les paramètres et la qualité électrique : débit, parité, bits d’arrêt, adresse de station, temporisation inter-caractères, trame complète, CRC, blindage, terminaison, dérivations et référence de potentiel. Un CRC incorrect ou des délais irréguliers peuvent provenir de plusieurs causes et ne se résolvent pas en changeant aléatoirement le débit.

Un expert doit distinguer les erreurs d’application des erreurs de ligne et documenter les paramètres imposés par chaque constructeur. Les valeurs de terminaison, le nombre maximal de nœuds, les longueurs de câble et la vitesse admissible dépendent de la configuration électrique exacte ; il n’existe pas une recette unique valable pour toutes les installations RS-485.

### 2.4 Passerelles : traduire sans masquer l’échec

Une passerelle Modbus TCP/RTU ajoute un point de dépendance. Elle doit traiter les connexions IP, l’identifiant d’unité, le séquencement des transactions, l’arbitrage sur la ligne série, les délais, les réponses d’exception, la distribution de données et parfois les tables de conversion. Une passerelle peut fonctionner côté TCP tandis qu’un instrument série est inaccessible.

```text
Client SCADA / PLC
       │ Modbus TCP (Ethernet/IP)
       ▼
┌─────────────────────────┐
│ Passerelle TCP ↔ RTU    │
│ - mapping Unit ID        │
│ - file de requêtes       │
│ - délai série            │
│ - journaux/diagnostics   │
└───────────┬─────────────┘
            │ Modbus RTU / RS-485
            ├──────── Instrument A
            ├──────── Instrument B
            └──────── Instrument C

Un état TCP « joignable » ne prouve pas que l’instrument série répond.
```

Le plan de test doit examiner les deux côtés et la traduction : ID d’unité, limites de requêtes en attente, temps d’attente, récupération après perte de la ligne série, traitement d’instrument indisponible et journaux. Pour les données utilisées par le procédé, il faut aussi définir comment la passerelle signale une donnée invalide ou périmée.

## 3. Budget de performance Modbus

### 3.1 Calculer un budget au lieu de choisir une fréquence arbitraire

Le temps de cycle d’un client dépend du nombre de requêtes, du temps moyen et maximal de réponse, du nombre de retries, des délais, de la manière dont les transactions sont séquencées et des équipements partagés. Le modèle simple `N × temps moyen` est utile pour un premier calcul, mais il sous-estime souvent les queues de distribution, les incidents et les délais de timeout.

Considère un scénario de laboratoire :

- 16 appareils ;
- 3 requêtes par appareil ;
- durée nominale requête-réponse de 18 ms ;
- traitement client et journalisation estimés à 4 ms par requête ;
- modèle séquentiel, sans retry.

Temps nominal approximatif : `16 × 3 × (18 + 4) ms = 1056 ms`, soit environ 1,06 s. Si la cible de fraîcheur est 250 ms, le profil séquentiel ne la satisfait pas. Il faut évaluer le regroupement des points compatibles, les besoins de fréquence, la possibilité d’un échange moins coûteux, la capacité du serveur, le parallélisme supporté et l’impact sur les autres tâches.

Le regroupement de registres n’est valide que si les adresses sont contiguës, la fonction est acceptée, les limites de taille sont respectées et les données peuvent être lues ensemble sans violer la sémantique du dispositif. Un accès groupé trop large peut être impossible ou moins sûr qu’une lecture ciblée.

### 3.2 Timeouts et retries

Un délai de réponse doit être adapté au comportement observé et aux exigences. Un timeout trop court augmente les fausses défaillances ; un timeout trop long retarde la détection. Les retries améliorent parfois la probabilité de lecture mais peuvent aussi augmenter la charge au mauvais moment. Il faut mesurer : temps nominal, percentile de latence, maximum observé dans des essais représentatifs, fréquence des exceptions, durée d’indisponibilité et réaction applicative.

Les systèmes doivent éviter les « tempêtes de reconnexion » où de nombreux clients tentent simultanément de retrouver un équipement ou répètent une requête agressivement. Un backoff contrôlé, des limites de charge et une stratégie de reprise approuvée peuvent réduire l’effet d’un défaut partagé.

### 3.3 Qualité, âge et cohérence de la donnée

Un client peut recevoir une donnée valide au moment de la lecture mais trop ancienne au moment où elle est consommée. Le système doit distinguer :

- validité protocolaire de la réponse ;
- validité du format et de l’encodage ;
- validité métier (plage, état, unité) ;
- fraîcheur (âge depuis la dernière mise à jour) ;
- état de communication ;
- statut de l’équipement source.

Une valeur de `0` peut être une mesure réelle, une valeur par défaut ou un résultat de substitution. Elle ne doit pas être employée comme indicateur universel de panne. Il est préférable de transporter ou calculer séparément une qualité et un horodatage lorsque l’architecture le permet.

## 4. Ingénierie PROFINET avancée

### 4.1 La relation d’E/S : modèle attendu et état réel

Le contrôleur et les périphériques doivent s’accorder sur l’identité, les modules, les paramètres, le format des données, le cycle et les comportements de diagnostic. Les symptômes de relation d’E/S défaillante peuvent venir d’un nom de station incorrect, d’un périphérique remplacé par une révision incompatible, d’un GSDML inadéquat, d’un module absent, d’une configuration d’entrées/sorties différente, d’un réseau segmenté de façon inattendue ou d’une capacité temporelle non respectée.

```text
      PROJET VALIDÉ                         INSTALLATION RÉELLE
┌────────────────────────────┐       ┌────────────────────────────┐
│ PLC/Controller attendu     │       │ PLC réel                   │
│ Device = IO-A              │       │ Device trouvé ?            │
│ Slot 1 = DI 16 voies       │       │ Nom station = IO-A ?       │
│ Slot 2 = DO 16 voies       │       │ Révision identique ?       │
│ Cycle configuré            │       │ Modules présents ?         │
└──────────────┬─────────────┘       └──────────────┬─────────────┘
               └──────── comparaison/diagnostic ────┘

Une relation d’E/S demande davantage que la seule présence du lien Ethernet.
```

La procédure de diagnostic doit commencer par collecter le diagnostic exact. Réinitialiser l’équipement ou changer le projet sans sauvegarder le contexte fait disparaître des indices essentiels et peut transformer un défaut diagnostiquable en panne intermittente difficile à reproduire.

### 4.2 Temps de cycle, watchdog et valeurs de substitution

Le temps de cycle doit être cohérent avec l’application et les limites des composants. Les paramètres de surveillance (watchdog) déterminent quand la perte d’échanges doit être signalée. Un watchdog n’est pas un substitut à une bonne conception ; son réglage doit correspondre aux caractéristiques temporelles et au comportement attendu en cas de défaillance.

Lorsqu’une relation d’E/S est perdue, l’application peut utiliser des valeurs de substitution, conserver certains états ou déclencher un comportement d’arrêt. Ce comportement doit être documenté dans le programme, dans la configuration du périphérique et dans la spécification de fonctionnement de la machine. L’expert vérifie que la valeur de substitution ne peut pas être confondue avec une mesure réelle par l’opérateur ou un système supérieur.

### 4.3 Choisir entre RT, IRT et les options temporelles

PROFINET RT convient à de nombreuses applications cycliques ; IRT répond à des besoins plus stricts de synchronisation et de déterminisme, avec un écosystème matériel et de configuration approprié. TSN est une famille de mécanismes Ethernet de gestion temporelle ; ses capacités ne doivent pas être extrapolées à des composants qui ne les déclarent pas.

Une conception doit consigner :

- le cycle requis et la tolérance de gigue ;
- les capacités déclarées du contrôleur, des périphériques et des commutateurs ;
- le nombre et la taille des échanges ;
- la topologie et les liaisons partagées ;
- les besoins de synchronisation et les fonctions utilisées ;
- les mécanismes de redondance, le temps de récupération et les conséquences d’une reconvergence ;
- les preuves de vérification dans le projet et au banc.

L’expert ne conclut pas qu’une architecture est déterministe sur la seule base d’une étiquette de protocole. Il vérifie la chaîne complète et la classe d’application.

### 4.4 Diagnostic par topologie : DCP, LLDP, compteurs et événements

Les informations de découverte et de voisinage peuvent aider à répondre à des questions concrètes : le périphérique se trouve-t-il sur le port attendu ? Une boucle ou une liaison inattendue existe-t-elle ? Le matériel de remplacement a-t-il été raccordé au bon endroit ? Les erreurs de port ou la perte de liens coïncident-elles avec l’apparition du diagnostic ?

LLDP expose le voisinage entre équipements compatibles ; DCP permet des opérations de découverte/configuration PROFINET ; les compteurs de commutateur donnent des indices sur les erreurs physiques, les rejets ou les changements de lien. Aucun de ces éléments ne suffit isolément. Les informations doivent être corrélées à des horodatages, au journal du PLC et au comportement process.

### 4.5 Redondance média et redondance système

MRP prend en charge la récupération sur certains anneaux compatibles. Des architectures peuvent également offrir différents niveaux de redondance de contrôleur ou de périphérique selon le produit, la configuration et la classe supportée. Les concepts de redondance système (par exemple les fonctions S2/R1, lorsque le matériel et la version les supportent) ne sont pas interchangeables avec la simple redondance de média.

La conception doit préciser le défaut couvert : rupture de câble, défaillance de commutateur, arrêt du contrôleur, perte d’alimentation, panne de périphérique, défaillance de l’outil d’ingénierie ou erreur de configuration. Chaque classe demande une stratégie, des composants compatibles et des essais distincts. Un anneau réseau ne protège pas contre la panne de l’automate unique qui gère le procédé.

## 5. Architecture combinée et intégration au système de supervision

```text
                         ENTREPRISE / IT
                               │
                       [Frontière contrôlée]
                               │ flux spécifiques
                    ┌──────────▼──────────┐
                    │ Pare-feu / DMZ OT   │
                    │ relais / collecteur │
                    └──────────┬──────────┘
                               │ flux documentés seulement
                ┌──────────────▼────────────────┐
                │ Zone supervision / historique │
                │ SCADA, historien, stations    │
                └──────────────┬────────────────┘
                               │
                         [Pare-feu cellule]
                               │
          ┌────────────────────▼─────────────────────┐
          │ Réseau de contrôle de cellule             │
          │                                           │
          │ PLC/Controller ─ PROFINET ─ IO Devices    │
          │     │                                     │
          │     └──── Modbus TCP ─ Compteur / drive   │
          │                    │                      │
          │               passerelle RTU              │
          └───────────────────────────────────────────┘

La séparation doit refléter les flux fonctionnels et les risques du site.
Un schéma conceptuel ne remplace pas une matrice de flux validée.
```

La collecte ne doit pas créer une voie d’écriture implicite vers le système de commande. Quand c’est possible, distinguer les services nécessaires à l’historisation des fonctions de programmation, de téléchargement ou de contrôle. Les capacités de séparation applicative dépendent du produit ; un pare-feu ne voit pas toujours la sémantique complète des registres écrits, donc une stratégie de sécurité doit combiner zones, règles de flux, authentification, configuration de service, supervision et procédures.

## 6. Observabilité et analyse de captures

### 6.1 Construire un jeu de preuves

Un dossier de diagnostic expert doit contenir, si disponibles :

- heure synchronisée et fuseau horaire ;
- version de projet et de firmware ;
- topologie et ports impliqués ;
- texte/code exact du diagnostic ;
- paires valeur attendue/valeur observée ;
- capture ou compteurs recueillis par méthode approuvée ;
- changement récent et périmètre affecté ;
- hypothèses testées et résultats ;
- procédure de rétablissement, décision et responsable.

Pour PROFINET, combiner diagnostic contrôleur/périphérique, état des modules, topologie, événements de port et captures autorisées. Pour Modbus, associer la séquence de requête/réponse, le code de fonction, la donnée décodée, le tableau de mapping, le timeout et les journaux du client/serveur.

### 6.2 Capture non intrusive

Une capture réseau sur une installation commutée n’a pas nécessairement une visibilité complète du trafic. Utiliser, selon la politique locale, un port miroir configuré par l’administrateur ou un TAP approprié. Enregistrer la durée et le point exact d’observation. Les filtres de Wireshark évoluent selon les versions ; les noms de protocoles et les champs disponibles doivent être vérifiés dans la version utilisée.

Exemples de filtres utiles pour un **laboratoire autorisé** :

```text
tcp.port == 502               # Modbus TCP standard
ip.addr == 192.168.60.30      # Trafic IP impliquant un serveur de test
tcp.analysis.retransmission   # Retransmissions TCP détectées par Wireshark
```

Ces filtres sont des outils d’observation, pas une preuve automatique de causalité. Le filtrage sur le port 502 ne verra pas forcément les échanges Modbus Security sur le port 802 ni le Modbus RTU sur une interface série capturée autrement. PROFINET temps réel peut utiliser des trames Ethernet spécifiques qui ne sont pas de simples sessions TCP/UDP ; une capture uniquement filtrée sur IP risque donc d’ignorer une partie des communications pertinentes.

### 6.3 Corréler les couches sans conclure trop vite

- Une retransmission TCP peut indiquer une perte ou un retard, mais pas identifier à elle seule l’emplacement de la perte.
- Une exception Modbus est une réponse applicative, pas une erreur de transport.
- Un `ping` réussi ne garantit pas que TCP/502 soit autorisé ni que la transaction soit valide.
- Une relation PROFINET absente ne prouve pas que le câble soit coupé.
- Une valeur impossible peut provenir d’un mapping ou d’une unité incorrecte plutôt que d’un défaut du réseau.
- Une alarme apparue après un changement de réseau peut avoir une cause applicative, temporelle ou matérielle : les journaux doivent être corrélés.

## 7. Cybersécurité : commandes, configuration et chaîne de confiance

### 7.1 Modèle de menace

Les risques comprennent l’accès non autorisé aux commandes, la modification de paramètres, la fausse donnée, la perte de disponibilité, l’usurpation d’un équipement, le remplacement d’un fichier d’ingénierie, l’accès distant laissé ouvert et la propagation depuis le réseau de l’entreprise. Les conséquences peuvent aller de l’erreur de suivi énergétique à une perturbation physique du procédé.

Les protocoles de base et les équipements anciens ne doivent pas être considérés comme authentifiés ou chiffrés par défaut. Modbus Security apporte une option basée sur TLS et certificats X.509, couramment spécifiée sur le port 802, mais la prise en charge doit être confirmée côté client, serveur, passerelle et outil. Les capacités PROFINET de sécurité dépendent de la spécification, du profil et de l’implémentation du produit. Dans les deux cas, la défense en profondeur reste nécessaire.

### 7.2 Liste de contrôle défensive

**Inventaire et configuration**

- maintenir une liste d’actifs, de versions, de fonctions actives, de propriétaires et de dépendances ;
- versionner les projets d’ingénierie, fichiers GSDML, cartes de registres, configurations de passerelle et règles réseau ;
- authentifier l’origine des fichiers ; contrôler les modifications et garder un exemplaire de référence ;
- conserver des sauvegardes hors ligne et tester la restauration dans un périmètre contrôlé.

**Accès et flux**

- isoler les zones de supervision, de contrôle, d’ingénierie et d’accès distant selon les besoins ;
- ouvrir uniquement les flux requis, avec source, destination, service, direction et propriétaire précis ;
- limiter la programmation et les écritures aux postes et comptes autorisés ;
- supprimer ou désactiver les accès temporaires après l’intervention ; journaliser les accès fournisseurs ;
- ne pas exposer directement un PLC ou une passerelle industrielle sur Internet.

**Surveillance et changement**

- surveiller les nouveaux appareils, adresses, noms de station, fonctions inhabituelles, volumes anormaux et échecs de communication ;
- planifier la maintenance et valider les mises à jour sur une architecture de test ;
- définir des critères de retour arrière et une chaîne d’escalade ;
- protéger les preuves et respecter les procédures de réponse aux incidents du site.

**Sûreté du procédé**

- avant tout test actif, faire valider l’impact par l’exploitant et l’ingénierie de contrôle ;
- ne pas effectuer d’écritures, de fuzzing, de tests de saturation ou de scans généraux sans autorisation formelle ;
- définir explicitement le comportement à la perte de communication ;
- vérifier que les alarmes signalent une valeur invalide ou périmée et ne masquent pas la perte de liaison.

## 8. Laboratoire expert 1 — Construire le budget Modbus

### Scénario

Une application de supervision lit 10 équipements. Chaque équipement nécessite deux requêtes séquentielles. Le temps nominal requête-réponse est de 22 ms ; le traitement et l’écriture historienne prennent 3 ms par requête. Un retry est prévu après un timeout de 120 ms. La cible d’actualisation est de 500 ms.

### Travail demandé

1. Calcule le temps nominal sans retry.
2. Calcule le temps supplémentaire d’un seul timeout et retry pour une requête, en indiquant l’hypothèse retenue.
3. Explique pourquoi le temps moyen nominal ne suffit pas comme critère d’acceptation.
4. Propose un plan de mesure.

### Correction

Temps nominal : `10 × 2 × (22 + 3) ms = 500 ms`. Le nominal atteint déjà toute la cible, sans marge pour les variations, la planification, les autres clients ni les traitements imprévus. Si une requête expire à 120 ms avant de réussir au retry, le surcoût par rapport à une transaction nominale peut être approximativement `120 ms + 25 ms`, soit 145 ms, selon la logique de timeout et le temps réel du retry. Le cycle total excéderait alors la cible.

L’acceptation doit examiner la distribution des latences, les timeouts, les périodes de pointe, la charge de l’historien, les équipements lents et le comportement au défaut. Il faut mesurer sur un simulateur ou un banc avec les mêmes profils et fixer une marge explicite. La fréquence, le regroupement des points et le nombre de requêtes doivent être réexaminés sans dépasser les limites officielles de chaque dispositif.

## 9. Laboratoire expert 2 — Analyse d’une capture Modbus TCP

### Scénario

Sur un simulateur, une lecture FC=03 part du client avec Transaction ID `0x002A`, offset `0x0010`, quantité 2. Une réponse revient avec le même Transaction ID, FC=03 et quatre octets de données. Une seconde requête n’obtient aucune réponse.

### Travail demandé

Décris ce que la première transaction prouve, ce qu’elle ne prouve pas, et les éléments à examiner pour la seconde.

### Correction

La première transaction montre qu’une requête et une réponse applicative ont été observées et qu’elles correspondent par l’identifiant de transaction. Elle ne prouve pas que les quatre octets soient interprétés avec le bon signe, l’ordre des mots, l’unité ou l’échelle ; il faut la carte officielle des registres. La seconde requête demande d’examiner l’horodatage, la session TCP, l’existence d’une retransmission ou d’un reset, l’éventuel code d’exception, le serveur et sa charge, le délai client, les règles réseau et l’emplacement de capture. Si la capture ne couvre qu’un segment du chemin, elle peut ne pas voir tous les événements.

## 10. Laboratoire expert 3 — Migration d’un appareil Modbus RTU derrière une passerelle

### Scénario

Un instrument RS-485 doit être lu depuis un client Modbus TCP. Le client atteint la passerelle, mais la lecture est intermittente.

### Plan d’analyse

1. Vérifier le contrat de données et le Unit ID utilisé par le client.
2. Vérifier si la passerelle mappe correctement le Unit ID vers l’adresse de station série.
3. Confirmer les paramètres série et la topologie RS-485 : débit, parité, bits d’arrêt, polarité, terminaison et câblage suivant la documentation.
4. Examiner les journaux de la passerelle, la file de requêtes, le délai série et le comportement en cas de réponse absente.
5. Tester sur simulateur ou banc et mesurer la latence nominale ainsi que les pires délais raisonnables.
6. Vérifier que le client ne lance pas plus de transactions que la passerelle ou le bus ne peut en traiter.
7. Documenter la réaction à une perte d’instrument, y compris qualité et âge de la valeur côté SCADA.

### Résultat attendu

Le rapport doit séparer les faits TCP du chemin série, présenter le mapping de l’unité, les paramètres confirmés et une chronologie de transactions. Aucune modification du câblage ou des paramètres du bus de production ne doit être réalisée sans autorisation et plan de maintenance.

## 11. Laboratoire expert 4 — Diagnostiquer une relation PROFINET défaillante

### Scénario

Après remplacement d’un îlot d’E/S, le contrôleur signale un défaut de périphérique. Le lien est actif ; l’outil d’ingénierie voit un équipement.

### Procédure attendue

1. Sauvegarder le diagnostic exact et les horodatages avant de changer quoi que ce soit.
2. Confirmer le numéro de produit, la révision et le firmware de l’équipement installé.
3. Vérifier le GSDML utilisé et les modules configurés, leur ordre et les tailles de données.
4. Vérifier l’identité attendue, le nom PROFINET, son unicité et la configuration IP pertinente.
5. Utiliser les diagnostics du contrôleur, la topologie, les données LLDP et les états du port pour vérifier la localisation physique.
6. Comparer la configuration du projet et la configuration réelle ; déterminer si le remplacement exige une modification validée du projet.
7. Tester au banc lorsque possible, puis établir une fenêtre d’intervention et des critères de retour arrière.

### Critères d’acceptation

- relation d’E/S établie sans diagnostic non résolu ;
- données des modules cohérentes et valeurs de qualité confirmées ;
- temps de cycle et surveillance conformes à l’exigence ;
- documentation et sauvegarde à jour ;
- état de défaut à la perte de communication connu ;
- aucune alarme supprimée pour masquer le symptôme.

## 12. Laboratoire expert 5 — Revue d’architecture et matrice de flux

### Scénario

Le SCADA doit lire des mesures d’un compteur Modbus TCP et afficher les états d’un PLC PROFINET. Un poste d’ingénierie doit pouvoir accéder au PLC pendant une fenêtre de maintenance. Le réseau bureautique ne doit pas communiquer directement avec les équipements de commande.

### Travail demandé

Définis les zones, les flux nécessaires et les preuves à conserver.

### Correction possible

```text
              Zone entreprise / bureautique
                           │
                aucune session directe vers PLC
                           │
               [Pare-feu / DMZ OT approuvée]
                           │ flux définis
                Zone supervision / SCADA
                           │
                   [Frontière cellule]
                           │
        ┌──────────────────┴─────────────────────┐
        │ Zone de contrôle                       │
        │ PLC ── PROFINET ── IO Devices           │
        │  └──── Modbus TCP ─── compteur         │
        │ accès ingénierie par poste autorisé    │
        └────────────────────────────────────────┘
```

Matrice illustrative :

| Source | Destination | Flux | Finalité | Contrôle |
|---|---|---|---|---|
| Collecteur/SCADA approuvé | Compteur | Modbus TCP selon besoin, généralement TCP/502 | Lire mesures identifiées | Adresse source fixe, destination précise, service limité, compte rendu de test |
| SCADA | PLC/serveur de données | Seulement les interfaces nécessaires à l’affichage | Supervision | Séparer les droits de lecture/commande lorsque le produit le permet |
| Station d’ingénierie | PLC/IO Device | Services officiels requis lors d’une fenêtre approuvée | Maintenance | Compte nominatif, accès temporisé, journalisation et sauvegarde |
| Réseau bureautique | PLC/IO Device | Aucun flux direct sauf exception évaluée | Non requis | Refus par défaut et journalisation appropriée |

Les flux PROFINET peuvent inclure des mécanismes Ethernet temps réel qui ne se résument pas au port TCP d’un service IP. Le plan de filtrage doit être conçu à partir des recommandations du fabricant, du modèle de commutateur/pare-feu et de la topologie exacte, puis validé par un test contrôlé. Il ne faut pas bloquer à l’aveugle un flux requis pour le fonctionnement cyclique.

## 13. Études de cas détaillées

### Cas A — Une valeur de température est dix fois trop grande

**Symptôme :** la supervision affiche `243,0` alors que la référence est proche de `24,3`.

**Hypothèses :** facteur d’échelle appliqué deux fois ou oublié ; changement de version de la table ; mauvaise unité ; mauvais offset pointant sur une autre donnée. Un problème d’encodage 16 bits est également possible, mais le facteur exactement dix est un indice, pas une preuve.

**Démarche :** comparer la table et la configuration actuelle ; vérifier les données brutes dans une capture ou un simulateur ; comparer à une source de référence ; vérifier la version du mapping ; revoir les transformations IHM/SCADA ; tester le correctif hors ligne. Ne pas modifier le PLC ou l’instrument avant d’avoir établi à quelle couche la transformation se produit.

### Cas B — L’alarme PROFINET apparaît après changement du commutateur

**Symptôme :** après remplacement d’un commutateur, un périphérique devient intermittent.

**Hypothèses :** port connecté à la mauvaise zone, configuration VLAN/filtrage modifiée, topologie d’anneau mal configurée, incompatibilité de fonctions temps réel, câble ou port défectueux, changement d’horloge/synchronisation selon l’architecture.

**Démarche :** sauvegarder les diagnostics ; comparer la configuration avant/après ; vérifier le câblage et les ports, les VLAN nécessaires, la topologie LLDP et les événements de lien ; confirmer la compatibilité du modèle de commutateur avec les fonctions temporelles et de redondance. Ne pas conclure qu’un commutateur « Ethernet » quelconque est équivalent à un modèle validé pour l’application.

### Cas C — La passerelle est joignable mais les valeurs deviennent périmées

**Symptôme :** la session Modbus TCP s’établit, mais les lectures de certains instruments restent figées.

**Hypothèses :** bus série saturé ; instrument qui ne répond plus ; mauvais Unit ID ; gateway qui conserve la dernière valeur ; délai trop long ou politique de retry ; polling de plusieurs clients ; défaut de ligne.

**Démarche :** identifier le dernier horodatage valide ; comparer les points actifs ; consulter les journaux gateway ; vérifier l’activité du bus sans générer de trafic additionnel ; confirmer les paramètres de série ; analyser les requêtes par unité ; définir une qualité explicite. Le diagnostic doit éviter de traiter une valeur figée comme une mesure actuelle.

## 14. Exercices corrigés

### Exercice 1 — Signé et non signé

Le registre vaut `0x8000`. Interprète-le comme entier non signé 16 bits et comme entier signé en complément à deux.

**Correction :** non signé : 32768. Signé : -32768. La même séquence de bits produit des nombres différents selon le type déclaré ; le manuel détermine le format attendu.

### Exercice 2 — Temps nominal de polling

Huit appareils ont chacun quatre lectures séquentielles. Chaque transaction prend 15 ms en moyenne et 2 ms de traitement client. Quel est le temps nominal simplifié ?

**Correction :** `8 × 4 × (15 + 2) = 544 ms`. Le temps réel peut être plus élevé. Une cible inférieure à 544 ms ne peut pas être garantie par cette stratégie avec ces hypothèses.

### Exercice 3 — Réponse d’exception

Le serveur reçoit FC=03 mais renvoie FC=0x83 et un code d’exception.

**Correction :** il s’agit d’une réponse d’exception associée à la fonction de lecture 03. Il faut interpréter le code exact à l’aide de la spécification et de l’implémentation. Le retour prouve que la requête est parvenue à un traitement applicatif, mais pas que le registre demandé est valide.

### Exercice 4 — Modbus TCP ne répond plus après une segmentation

**Correction :** confirmer les flux nécessaires et l’ACL, la route, l’adresse et le port. Vérifier si les réponses sont autorisées dans le sens retour. Les tests restent limités à un flux connu et autorisé ; ne pas rouvrir tout le réseau pour résoudre un seul service.

### Exercice 5 — GSDML correct mais IO Device absent

**Correction :** le GSDML n’assure pas la présence du périphérique. Vérifier l’alimentation, le lien, le nom de station, le réseau, les ports, la compatibilité des modules, les diagnostics du contrôleur et l’état du périphérique.

### Exercice 6 — Valeur périmée, mais valeur dans la plage

**Correction :** la plage seule ne prouve pas la fraîcheur. Ajouter ou vérifier l’indicateur de qualité, l’âge depuis la dernière donnée, l’état de communication et l’action applicative à la perte de liaison.

### Exercice 7 — Anneau Ethernet présent, panne non récupérée

**Correction :** confirmer compatibilité et configuration MRP, rôle gestionnaire, état des ports, câblage, temps de récupération et éventuelles limitations des autres composants. L’anneau couvre une classe de défaillance et ne rend pas le système entier redondant.

### Exercice 8 — Lecture et écriture sur la même connexion

**Correction :** une connexion réseau ne donne pas à elle seule une autorisation fonctionnelle. Définir quelles fonctions de commande sont requises, qui peut les demander, dans quel état et comment les opérations sont validées/journalisées. Limiter l’exposition réseau en parallèle.

### Exercice 9 — Capturer le trafic PROFINET

**Correction :** s’assurer que le point de capture voit les ports concernés, utiliser un port miroir ou un TAP autorisé, inclure les protocoles Ethernet nécessaires plutôt que de filtrer uniquement l’IP, synchroniser les horodatages et respecter la politique de conservation des traces.

### Exercice 10 — Choix de RT ou IRT

**Correction :** établir d’abord les exigences du procédé, le cycle, la gigue, la synchronisation, les capacités de tous les composants et la topologie. RT convient à de nombreuses applications ; IRT s’utilise quand les besoins et l’équipement compatible l’exigent. Le choix n’est pas fait sur une préférence abstraite.

## 15. Défi final corrigé — Revue de conception d’une ligne de conditionnement

### Énoncé

Une ligne comprend un PLC, trois îlots d’E/S PROFINET, deux variateurs, un compteur Modbus TCP et une ancienne passerelle Modbus RTU. La supervision affiche énergie, vitesse et états. Après un changement, les états de deux périphériques deviennent intermittents, les valeurs du compteur parfois trop anciennes et une lecture de vitesse est dix fois trop élevée.

Prépare un plan expert : architecture, hypothèses, tests, sécurité, critères d’acceptation et retour arrière.

### Correction détaillée

**1. Préserver l’état initial et établir la chronologie.** Collecter l’heure des symptômes, les changements de commutateur/projet/mapping, les diagnostics PLC et IO Device, l’état des ports, les journaux de passerelle, la version du SCADA, les captures autorisées et les valeurs attendues/observées. Ne pas redémarrer ou reconfigurer les équipements avant d’avoir sauvegardé les informations utiles, sauf si l’exploitant juge nécessaire une action immédiate pour protéger le procédé.

**2. Séparer les trois symptômes.**

- Intermittence PROFINET : vérifier lien, ports et erreurs, topologie LLDP, configuration de commutateur, nom de station, GSDML, état de relation d’E/S, cycle et diagnostics. Établir si les deux périphériques partagent un segment ou un port qui a changé.
- Valeurs Modbus RTU/TCP périmées : vérifier les deux segments de la passerelle, les Unit IDs, l’état de la ligne série, les paramètres, les délais, la charge et la présence éventuelle de plusieurs clients. Mettre en évidence le dernier échantillon valide plutôt que conserver une valeur sans qualité.
- Vitesse dix fois trop élevée : vérifier le facteur d’échelle dans la carte de registres, la version du mapping, le signe, l’unité et les transformations IHM. Ne pas présumer que ce défaut provient du même changement réseau.

**3. Architecture cible indicative.**

```text
               Zone supervision / historisation
       ┌────────────────────────────────────────┐
       │ SCADA + historien + qualité/horodatage │
       └─────────────────────┬──────────────────┘
                             │ flux nécessaires
                        [Pare-feu OT]
                             │
        ┌────────────────────▼────────────────────────────┐
        │ Zone de contrôle                                │
        │ PLC/Controller                                  │
        │  ├── PROFINET RT/IRT selon exigence ─ IO-1       │
        │  ├── PROFINET RT/IRT selon exigence ─ IO-2       │
        │  ├── PROFINET RT/IRT selon exigence ─ IO-3       │
        │  ├── PROFINET ─ variateurs                      │
        │  └── Modbus TCP ─ compteur                      │
        │                    └─ passerelle ─ RS-485/RTU   │
        └─────────────────────────────────────────────────┘

        Accès d’ingénierie : poste identifié, limité dans le temps,
        journalisé et autorisé par procédure de maintenance.
```

Le schéma ne fixe pas à lui seul la segmentation exacte. Les zones et les ports doivent être décidés avec le concepteur du procédé, les exigences des dispositifs, les règles des fournisseurs et l’analyse de risque. La ligne temps réel ne doit pas être placée derrière un filtre incompatible avec les échanges requis.

**4. Valider le mapping et la temporalité.** Pour la vitesse : documenter le registre et la fonction exacts, comparer la représentation brute à la notice, confirmer le facteur et l’unité, tester une valeur connue dans un simulateur puis vérifier la chaîne jusqu’à l’affichage. Pour le compteur : calculer le budget de polling, mesurer les pires latences raisonnables, définir les timeouts et retries, indiquer l’âge de la mesure et éviter de multiplier les clients qui demandent les mêmes points.

**5. Sécurité et gouvernance.** Limiter la supervision aux données nécessaires, réduire les écritures, contrôler les postes d’ingénierie, mettre à jour l’inventaire, versionner les cartes Modbus et le projet PROFINET, sauvegarder les configurations et garder les journaux. Confirmer le support réel de Modbus Security ou des options PROFINET de sécurité avant de considérer ces fonctions comme présentes.

**6. Critères d’acceptation.**

- les trois périphériques PROFINET sont dans l’état attendu, sans diagnostic non résolu ;
- les états/valeurs d’E/S se mettent à jour dans les limites définies ;
- les connexions Modbus et les lectures nécessaires sont stables dans la durée d’essai convenue ;
- les valeurs de compteur et vitesse correspondent à une référence connue ;
- les pertes de communication se traduisent par un état qualité/alarme approprié ;
- les chemins réseau et droits d’accès sont revus ;
- la sauvegarde et la procédure de retour arrière ont été vérifiées ;
- chaque modification est attribuée, documentée et approuvée.

**7. Retour arrière.** Conserver le projet précédent, la carte de registres précédente, la configuration des ports/commutateurs et la configuration de passerelle. Définir qui décide du rollback, le critère de déclenchement, le temps maximal de décision et comment vérifier que le procédé retrouve un état acceptable. Une restauration doit être testée et coordonnée avec l’exploitant, pas improvisée pendant la panne.

## 16. Glossaire avancé

- **Âge de donnée :** temps écoulé depuis la dernière mise à jour valide.
- **Backoff :** stratégie qui espace progressivement les nouvelles tentatives après une erreur.
- **Contrat de données :** document définissant adresse, type, unité, échelle, qualité, fréquence et droits.
- **DCP :** mécanisme de découverte et configuration PROFINET à couche Ethernet.
- **GSDML :** fichier de description d’un périphérique PROFINET.
- **IRT :** classe PROFINET isochrone temps réel destinée aux exigences de synchronisation avancées.
- **LLDP :** découverte de voisins sur le réseau Ethernet.
- **MBAP :** en-tête de Modbus TCP.
- **Modbus Security :** variante intégrant TLS et certificats X.509 ; support à vérifier dans chaque équipement.
- **MRP :** mécanisme de redondance média sur anneau pour composants compatibles.
- **PDU/ADU :** unité de données de protocole / unité de données applicative transportée.
- **Polling :** interrogation périodique d’équipements par un client.
- **Qualité de donnée :** statut qui distingue valeur valide, défaut, substitution ou donnée périmée.
- **RT :** communication PROFINET temps réel.
- **Temps de cycle :** période de mise à jour d’une tâche ou d’un échange cyclique.
- **Watchdog :** surveillance temporelle qui détecte l’absence d’échanges dans un délai configuré.

## 17. Références techniques

1. Modbus Organization — Spécifications et guides : https://www.modbus.org/modbus-specifications
2. Modbus Application Protocol Specification V1.1b3 : https://www.modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
3. Modbus Organization — Introduction to Modbus : https://www.modbus.org/introduction-to-modbus
4. PROFIBUS & PROFINET International — Specifications & Standards : https://www.profibus.com/download/specifications-standards
5. PROFIBUS & PROFINET International — PROFINET Security Guideline : https://www.profibus.com/download/profinet-security-guideline
6. CISA — ICS Recommended Practices : https://www.cisa.gov/resources-tools/resources/ics-recommended-practices

Les standards, outils et paramètres évoluent. Vérifier la version des spécifications, les manuels correspondant aux références installées, la compatibilité des firmwares et la documentation de conception approuvée. Les exemples de registres et de valeurs de ce cours sont fictifs et ne doivent pas être appliqués à un équipement réel sans validation.
