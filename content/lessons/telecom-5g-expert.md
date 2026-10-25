# Réseaux mobiles 4G/5G — Expert

## Mise en contexte : concevoir, optimiser et exploiter un réseau mobile de bout en bout

Au niveau débutant, tu as découvert les principes radio, l'architecture LTE/EPC, la 5G NSA et SA ainsi que les principaux éléments du réseau. Au niveau intermédiaire, tu as étudié les procédures d'accès, les sessions de données, la mobilité, la QoS et le diagnostic des incidents.

Ce niveau expert fait passer de la compréhension des composants à l'ingénierie de bout en bout. Il s'agit désormais de relier les contraintes radio aux décisions du cœur de réseau, de dimensionner des capacités, d'analyser des procédures, de comprendre les compromis d'architecture et de bâtir une méthode de diagnostic fondée sur des mesures corrélées.

> **Principe directeur :** une bonne performance 4G/5G ne dépend jamais d'un seul indicateur. Elle résulte de la cohérence entre couverture radio, capacité, mobilité, transport, cœur de réseau, politiques QoS, services applicatifs, sécurité et exploitation.

Les exemples chiffrés et les identifiants de réseau de ce cours sont fictifs et servent à l'apprentissage. Les paramètres exacts et les commandes d'exploitation varient selon le fournisseur, la version logicielle, la bande de fréquences et la réglementation nationale.

## Objectifs pédagogiques

À la fin du cours, tu sauras :

- analyser une architecture 4G/5G SA/NSA et justifier des choix d'évolution ;
- relier les paramètres NR, le budget de liaison, la charge et le débit utilisateur ;
- diagnostiquer les problèmes de mobilité, de handover et de continuité de session ;
- expliquer les fonctions du 5G Core et les interactions entre AMF, SMF, UPF, PCF, UDM, AUSF, NSSF et NRF ;
- concevoir une politique QoS cohérente et interpréter 5QI, QFI, GBR, ARP, GFBR et MFBR ;
- concevoir un scénario de network slicing sans confondre séparation logique et isolation garantie ;
- raisonner sur MEC, ancrage UPF, routage local et chemin de données ;
- structurer une analyse de sécurité et de résilience ;
- corréler compteurs radio, traces de signalisation, métriques du cœur et mesures applicatives ;
- proposer un plan d'optimisation mesurable, réversible et vérifiable.

## Prérequis

Il faut maîtriser les bases LTE/NR, EPC/5GC, adressage IP, routage, QoS et signalisation NAS/RRC. Il est aussi utile de savoir lire des journaux, des captures réseau et des tableaux de KPI. Si ces notions ne sont pas encore solides, consolide d'abord les niveaux débutant et intermédiaire.

# Partie I — Architecture avancée et décisions d'ingénierie

## 1. Comparer LTE, 5G NSA et 5G SA au-delà des slogans

LTE s'appuie sur E-UTRAN et l'Evolved Packet Core (EPC). La 5G NSA ajoute une radio NR tout en conservant une dépendance à une architecture LTE/EPC, dans les variantes où LTE joue le rôle de nœud maître. La 5G SA utilise une NG-RAN et un 5G Core natif.

```text
LTE classique
UE ── LTE/eNB ── EPC (MME, S-GW, P-GW, HSS, PCRF) ── DN/Internet

5G NSA, variante EN-DC courante
UE ── LTE/eNB (nœud maître) ── EPC
          ╲
           ╲── NR en-gNB (nœud secondaire)

5G SA
UE ── NR/gNB ── 5G Core (AMF, SMF, UPF, UDM, AUSF, PCF...) ── DN/Internet
```

Le terme NSA recouvre plusieurs options de déploiement. Le schéma illustre le mode EN-DC fréquent, mais il ne faut pas déduire que toutes les architectures NSA sont identiques.

| Dimension | LTE/EPC | 5G NSA | 5G SA |
|---|---|---|---|
| Accès radio | LTE | LTE et NR selon l'option | NR avec NG-RAN |
| Cœur de réseau | EPC | EPC dans le scénario représenté | 5G Core |
| Dépendance à LTE pour le contrôle | Non, LTE est l'accès lui-même | Souvent oui dans EN-DC | Non dans l'architecture SA |
| Fonctions 5GC natives | Non | Pas dans le scénario EPC indiqué | Oui |
| Slicing 5GC de bout en bout | Non sous sa forme native 5GC | Pas avec le seul EPC illustré | Architecture adaptée, sous réserve de mise en œuvre complète |
| Services et mobilité | Écosystème LTE | Coexistence et interfonctionnement LTE/NR | Fonctions 5GS et interfonctionnement avec EPS si déployé |

Le choix n'est pas seulement technique. Il dépend des fréquences disponibles, du parc de terminaux, de la couverture, du coût de migration, des services prioritaires, de l'interconnexion IMS, de la capacité du transport et de la maturité opérationnelle.

**Erreur fréquente :** conclure qu'un téléphone affiche « 5G » donc que la session utilise obligatoirement un 5G Core. L'indicateur affiché par le terminal ne suffit pas à déterminer l'architecture de contrôle réellement utilisée.

## 2. 5G Core : fonctions, responsabilités et dépendances

Le 5GC est conçu autour d'une architecture orientée services (*Service-Based Architecture*, SBA) pour une partie importante des interactions du plan de contrôle. Les fonctions réseau fournissent et consomment des services. Cela ne signifie pas que toutes les interfaces sont identiques ni que les fonctions peuvent être remplacées sans contraintes d'interopérabilité.

| Fonction | Rôle principal | Exemple de question d'exploitation |
|---|---|---|
| AMF | Enregistrement, mobilité et gestion de l'accès du terminal | L'UE s'enregistre-t-il et reste-t-il joignable ? |
| SMF | Contrôle des sessions PDU et sélection/contrôle des UPF | La session est-elle créée avec le bon DNN et le bon UPF ? |
| UPF | Acheminement du plan utilisateur, application de règles et ancrage de session | Les paquets traversent-ils le bon chemin de données ? |
| UDM | Données d'abonnement et fonctions de gestion des données utilisateur | L'abonnement autorise-t-il le service demandé ? |
| AUSF | Fonction d'authentification | L'authentification se termine-t-elle correctement ? |
| PCF | Décisions de politique et de contrôle QoS/facturation selon l'architecture | Les règles appliquées correspondent-elles au service ? |
| NRF | Découverte et enregistrement des fonctions réseau | Le consommateur trouve-t-il une fonction compatible et disponible ? |
| NSSF | Assistance à la sélection de slice et aux informations de slicing | Le réseau autorise-t-il et sélectionne-t-il la slice attendue ? |
| NEF | Exposition contrôlée de capacités réseau à des applications autorisées | Une application est-elle autorisée à demander une capacité réseau ? |
| AF | Fonction applicative qui peut interagir avec la politique réseau | Les exigences de l'application sont-elles traduites en politique autorisée ? |
| CHF | Fonction de collecte de données de taxation/facturation | Les événements de consommation sont-ils enregistrés ? |
| UDR | Dépôt de données utilisé par certaines fonctions du cœur | Les données de politique ou d'abonnement sont-elles cohérentes ? |
| SCP | Proxy de communication des services, lorsqu'il est utilisé | Les appels entre fonctions sont-ils routés et observables correctement ? |

Les fonctions exactes présentes, leur découpage en microservices, leur redondance et leur mode d'interconnexion dépendent du déploiement. Il faut distinguer la fonction logique normalisée de son implémentation commerciale.

### 2.1 Plan de contrôle et plan utilisateur

Le plan de contrôle établit les contextes, décide les politiques et pilote les sessions. Le plan utilisateur transporte les paquets de l'abonné.

```text
                  PLAN DE CONTRÔLE
UE ── NAS ── gNB ── AMF ── SMF ── PCF / UDM / AUSF / NRF / NSSF
                         │
                         └── contrôle et sélection du chemin UPF

                  PLAN UTILISATEUR
UE ── radio NR ── gNB ── N3/GTP-U ── UPF ── N6/IP ── réseau de données
```

Dans le modèle courant, l'interface N2 relie le NG-RAN à l'AMF pour le contrôle d'accès, tandis que N3 transporte le trafic utilisateur entre le NG-RAN et l'UPF. N6 relie l'UPF au réseau de données (*Data Network*, DN). D'autres interfaces et fonctions interviennent selon la procédure et le scénario.

Le découplage rend possibles différentes architectures de données, mais il introduit aussi des dépendances : une session peut échouer parce que le contrôle fonctionne mal, ou bien être établie alors que le chemin utilisateur, le routage externe ou la politique de filtrage est incorrect.

### 2.2 Les sessions PDU et leur cycle de vie

Une session PDU est le contexte logique permettant au terminal d'accéder à un réseau de données. Elle est associée notamment à un type de session (IPv4, IPv6, IPv4v6, Ethernet ou autres formes prises en charge), un DNN et des règles QoS. Les options effectivement autorisées dépendent de l'abonnement, du terminal et du réseau.

Séquence logique simplifiée :

```text
UE             gNB             AMF             SMF             UPF
 |              |               |               |               |
 |-- demande de session PDU ---->|               |               |
 |              |---------------|-- sélection --|               |
 |              |               |               |-- préparation->|
 |              |<------ ressources radio / tunnel / règles -----|
 |<------------- acceptation et paramètres de session ------------|
 |================ trafic utilisateur via UPF ===================>|
```

Cette séquence est fonctionnelle et non une trace exhaustive des messages normalisés. Les procédures détaillées peuvent comprendre la découverte de fonctions, l'autorisation d'abonnement, la négociation des paramètres, la mise en place des tunnels, les règles de politique et plusieurs messages NAS, NGAP et PFCP.

Pour diagnostiquer une session, ne vérifie pas seulement qu'une adresse IP a été attribuée. Contrôle aussi le DNN, la sélection SMF/UPF, l'état N3, les règles de transfert UPF, le routage sur N6, le DNS, les politiques de sécurité et la QoS réellement appliquée.

## 3. Choisir le bon ancrage UPF et placer le trafic

Un UPF central peut simplifier l'exploitation et concentrer les fonctions de sécurité, mais rallonger le chemin vers une application proche de l'utilisateur. Un UPF en périphérie peut diminuer la distance de transport pour certains services, au prix d'une architecture distribuée plus complexe.

```text
Sans sortie locale
UE ─ gNB ─ transport régional ─ UPF central ─ réseau applicatif local
       <---------- détour de transport ---------->

Avec sortie locale adaptée
UE ─ gNB ─ UPF de périphérie ─ application/MEC
       <--- chemin réduit --->
```

Un déploiement peut utiliser un UPF de type PDU Session Anchor (PSA) et, selon les besoins, des fonctions telles que l'UL Classifier (UL CL) ou le Branching Point pour orienter certains flux. Le choix doit préserver la cohérence des politiques, le routage retour, l'adressage, la sécurité et la continuité de session.

**Attention :** déplacer un UPF vers la périphérie ne garantit pas à lui seul une latence faible. La radio, les files d'attente, le transport, le traitement applicatif, les retransmissions et la charge de l'application comptent également.

# Partie II — Ingénierie radio NR avancée

## 4. Numérologie NR, trames et bande passante

NR utilise plusieurs espacements de sous-porteuses. Pour la numérologie courante, l'espacement est lié à l'indice μ selon :

\[
\Delta f = 15 \times 2^{\mu}\ \text{kHz}
\]

| μ | Espacement de sous-porteuses | Durée nominale d'un slot normal-CP |
|---:|---:|---:|
| 0 | 15 kHz | 1 ms |
| 1 | 30 kHz | 0,5 ms |
| 2 | 60 kHz | 0,25 ms |
| 3 | 120 kHz | 0,125 ms |
| 4 | 240 kHz | 0,0625 ms, pour les cas où ce paramètre est prévu |

Ce tableau illustre les relations nominales. Les formats de slot, le préfixe cyclique, les canaux et les configurations prises en charge dépendent de la bande et du profil NR. Il ne faut pas confondre durée de slot, temps de transmission d'un paquet, délai applicatif et délai aller-retour.

Le nombre de blocs de ressources (RB) utilisables dépend de la largeur de canal, de l'espacement des sous-porteuses et des règles de configuration NR. Ne déduis pas directement le nombre de RB du seul nombre de MHz sans consulter les tables de la spécification correspondante.

### 4.1 TDD, UL/DL et capacité réelle

Dans une bande TDD, la même bande de fréquences est partagée dans le temps entre liaison descendante et liaison montante. Une configuration plus favorable au DL peut améliorer les téléchargements dans certains scénarios, mais réduire les occasions de transmission UL. Les réseaux voisins doivent également gérer les risques d'interférence entre cellules lorsque leurs motifs temporels ne sont pas coordonnés.

Les décisions de configuration TDD doivent être guidées par :

- la répartition observée du trafic DL/UL ;
- les besoins de services montants comme la vidéo, la télémétrie ou le transfert de fichiers ;
- les contraintes réglementaires et la coordination avec les opérateurs voisins ;
- la synchronisation temporelle et l'interférence intercellulaire ;
- la continuité aux frontières de cellules et pendant la mobilité.

### 4.2 Débit : du spectre au débit utilisateur

Une approximation de premier ordre est :

\[
R \approx B \times \eta \times N_{\text{couches}} \times \alpha
\]

avec :

- \(R\) : débit théorique approximatif en bit/s ;
- \(B\) : largeur de bande exprimée en Hz ;
- \(\eta\) : efficacité spectrale moyenne par couche en bit/s/Hz ;
- \(N_{\text{couches}}\) : nombre de couches spatiales utiles ;
- \(\alpha\) : facteur global représentant notamment les ressources de contrôle, les références radio, les créneaux UL/DL, les erreurs, les retransmissions et les autres surcharges.

Exemple purement illustratif : une bande de 100 MHz, une efficacité spectrale moyenne de 3 bit/s/Hz, deux couches spatiales et un facteur global de 0,7 donnent :

\[
100\times10^6 \times 3 \times 2 \times 0{,}7 = 420\ \text{Mbit/s}
\]

Ce chiffre n'est pas une promesse commerciale ni une prévision précise. Le débit d'un abonné dépend de la qualité radio, de la planification, de la charge de cellule, de la modulation et du codage, du nombre de couches, des allocations de ressources, du terminal, du transport, du cœur et du serveur distant.

Il faut toujours préciser si un débit annoncé est un débit physique, un débit MAC, un débit IP, un débit applicatif, un débit instantané, un débit moyen ou un débit de percentile.

## 5. Couverture radio, propagation et budget de liaison

Un budget de liaison organise les gains et les pertes entre l'émetteur et le récepteur. Une forme simplifiée s'écrit :

\[
P_{RX}=P_{TX}+G_{TX}+G_{RX}-L_{câbles}-L_{propagation}-L_{divers}
\]

Toutes les quantités sont exprimées en dB ou dBm de façon cohérente. Des calculs plus complets incluent les pertes de pénétration, les pertes liées au corps humain, les pertes de polarisation, les marges d'évanouissement et les effets de l'implémentation.

Le dimensionnement doit considérer les deux sens de transmission. Une cellule peut être entendue par le terminal alors que le terminal ne parvient pas à transmettre avec une qualité suffisante vers la station de base. C'est particulièrement important lorsque le budget UL est plus contraignant.

### 5.1 FR1, FR2 et propagation

Les bandes FR1 et FR2 couvrent des plages de fréquences définies par les spécifications NR. En règle générale, des fréquences plus élevées subissent une atténuation de propagation plus forte à distance égale, une pénétration souvent plus difficile dans les bâtiments et une sensibilité accrue à certaines obstructions. Elles peuvent toutefois exploiter de grandes largeurs de bande et des réseaux d'antennes à faisceaux étroits.

Il faut éviter les simplifications comme « la 5G haute fréquence traverse toujours moins bien les murs de la même manière » : le résultat dépend de la fréquence, du matériau, de l'angle, de la polarisation, des ouvertures, de l'environnement et de la géométrie des antennes.

### 5.2 SINR et interférences

Le SINR (Signal-to-Interference-plus-Noise Ratio) compare la puissance du signal utile à la somme de l'interférence et du bruit. Une puissance de signal élevée n'implique pas nécessairement un SINR élevé : des cellules voisines ou des réflexions peuvent dégrader la qualité.

Lors d'une optimisation, analyse au minimum un ensemble de mesures : RSRP, RSRQ, SINR, BLER, taux de retransmission, modulation/codage, débit, utilisation des ressources, distribution des mesures et localisation. Les définitions exactes et les noms de compteurs dépendent de la technologie et du fournisseur.

## 6. Massive MIMO, beamforming et mobilité de faisceau

Le massive MIMO utilise de nombreux éléments d'antenne pour exploiter la dimension spatiale. Le beamforming concentre l'énergie vers une direction ou un ensemble de directions. Le multiplexage spatial peut servir plusieurs flux lorsque le canal et le terminal le permettent.

Bénéfices possibles :

- amélioration du rapport signal/interférence dans des conditions adaptées ;
- augmentation de la capacité par réutilisation spatiale ;
- meilleure maîtrise du rayonnement et du gain de lien ;
- adaptation du faisceau aux conditions radio et à la mobilité.

Limites et contraintes :

- qualité et rapidité des mesures de canal ;
- calibration, synchronisation et implémentation de l'antenne ;
- couverture UL par rapport au DL ;
- vitesse et direction de déplacement du terminal ;
- obstacles, mobilité du corps et environnement radio ;
- consommation énergétique et échauffement ;
- complexité de planification et de diagnostic.

Dans NR, les signaux de synchronisation et de mesure de faisceau, ainsi que les procédures RRC associées, jouent un rôle dans l'accès et le suivi radio. Les paramètres concrets de balayage, de périodicité, de mesure et de sélection sont spécifiques à la configuration.

**Méthode experte :** ne conclue pas à un mauvais beamforming uniquement à partir d'un débit faible. Vérifie la couverture, le SINR, la charge PRB, la configuration du terminal, l'UL, les retransmissions, l'agrégation de porteuses, la capacité du transport et les éventuelles limitations de forfait ou de politique.

## 7. CA, EN-DC, double connectivité et agrégation

L'agrégation de porteuses (Carrier Aggregation, CA) permet à un terminal compatible d'utiliser plusieurs porteuses selon la configuration du réseau. La double connectivité permet au terminal d'être connecté à plusieurs nœuds radio logiques selon l'architecture et de répartir certaines ressources.

En NSA EN-DC, LTE et NR peuvent participer au service utilisateur sous contrôle d'une architecture ancrée dans LTE/EPC. En SA, les procédures et options de connectivité s'appuient sur la NG-RAN et le 5GC. Les mécanismes exacts de gestion des bearers, des flux et des rôles de nœud dépendent de la variante déployée.

Pour analyser une agrégation décevante, vérifie que le terminal et la bande sont compatibles, que la combinaison de bandes est autorisée, que la cellule secondaire est ajoutée, que les qualités radio sont suffisantes et que la charge de cellule permet réellement un gain. La présence de plusieurs porteuses ne garantit pas un débit multiplié par leur nombre.

# Partie III — Mobilité et continuité des services

## 8. Handover : du déclenchement au résultat utilisateur

Le handover change le point d'accès radio utilisé par le terminal. Selon la procédure, il implique des mesures UE, une décision côté réseau, une préparation de la cellule cible, une reconfiguration radio, le transfert de contexte et éventuellement la modification de chemin dans le cœur.

```text
UE             Source gNB             Cible gNB            AMF/UPF
 | mesure radio     |                     |                   |
 |----------------->|                     |                   |
 |                  |-- préparation ----->|                   |
 |                  |<-- admission -------|                   |
 |<-- commande HO --|                     |                   |
 |------------------------------ accès cible ---------------->|
 |                  |<----- finalisation / mise à jour --------|
```

Ce schéma représente les grandes étapes, non le détail exact d'une procédure donnée. Les messages, responsabilités et mises à jour varient notamment selon qu'un handover est fondé sur Xn ou N2, qu'il s'effectue en intra-gNB, inter-gNB ou entre technologies.

### 8.1 Handover Xn et N2

- **Handover via Xn :** une interface entre nœuds NG-RAN est utilisée pour les fonctions de préparation et de transfert prévues par cette procédure. Elle peut réduire la dépendance directe au cœur pour certaines étapes.
- **Handover via N2 :** le cœur, notamment l'AMF, participe à la procédure de mobilité entre NG-RAN selon le scénario.

Le choix entre ces mécanismes dépend de l'architecture, des relations entre nœuds, des capacités de la cible et de la situation de mobilité. Ne suppose pas qu'un handover Xn est toujours possible ou toujours préférable.

### 8.2 Mesures et déclencheurs

Le réseau configure les mesures radio via RRC. Les événements de mesure, les seuils, l'hystérésis, les offsets et les temporisations contribuent à décider quand préparer ou déclencher une mobilité.

Un paramétrage trop agressif peut provoquer des handovers fréquents, des retours vers la cellule source (*ping-pong*) et une signalisation supplémentaire. Un paramétrage trop conservateur peut provoquer une dégradation radio avant le changement de cellule, voire des échecs.

La mobilité doit être évaluée avec plusieurs indicateurs : taux de succès de préparation, taux de succès d'exécution, interruption perçue, pertes de paquets, échecs de rétablissement, durée de séjour, taux de ping-pong et qualité après handover.

### 8.3 Diagnostic d'un échec de mobilité

| Symptôme | Hypothèses à examiner | Vérifications |
|---|---|---|
| Handover rejeté | Admission refusée, cellule cible saturée, contexte invalide | Cause de rejet, charge cible, ressources et capacités déclarées |
| Handover préparé mais non exécuté | Radio cible insuffisante, synchronisation ou configuration incorrecte | Mesures UE, chronologie RRC, accès aléatoire et radio cible |
| Coupure de données à la transition | Mise à jour de chemin ou transfert de paquets incomplet | Traces NGAP, tunnel GTP-U, UPF, compteurs de pertes |
| Ping-pong | Hystérésis ou temporisations inadaptées, couverture chevauchante | Historique des cellules, mesures et paramètres de mobilité |
| Voix coupée mais data stable | Problème IMS/QoS, continuité de voix ou interfonctionnement | Traces SIP, QoS de voix, procédures EPS fallback ou mobilité IMS concernées |
| Échecs limités à une frontière de technologie | Interfonctionnement ou voisinage incomplet | Relations de voisinage, bandes et configurations inter-RAT |

Ne corrige pas un problème de mobilité en modifiant immédiatement plusieurs paramètres. Construis d'abord une chronologie, isole une hypothèse et prépare une comparaison avant/après avec possibilité de retour arrière.

## 9. Mobilité entre 5GS et EPS

Les opérateurs peuvent devoir maintenir la connectivité lorsque le terminal passe entre 5G SA et LTE/EPC. Les mécanismes disponibles dépendent du support terminal et réseau, des options d'interfonctionnement, de l'abonnement, de la configuration de l'IMS et des versions prises en charge.

Il faut distinguer :

- le passage radio d'une technologie à une autre ;
- la continuité de la session de données ;
- la continuité d'une session IMS/voix ;
- la réutilisation ou la création d'un contexte dans le cœur correspondant.

Le N26 entre AMF et MME peut contribuer à certaines procédures de mobilité inter-systèmes lorsqu'il est déployé. Son absence ne signifie pas automatiquement qu'aucune mobilité n'est possible, mais peut modifier les procédures, les délais ou le niveau de continuité.

### 9.1 EPS fallback, VoLTE et VoNR

VoLTE utilise IMS au-dessus d'un accès LTE et des mécanismes QoS associés à l'EPC. VoNR fournit la voix IMS au-dessus de 5G SA lorsqu'elle est prise en charge et configurée. EPS fallback peut amener un terminal 5G SA vers LTE pour un service vocal dans les réseaux qui suivent cette stratégie.

Le choix dépend de la couverture SA, du support VoNR, de l'état de déploiement IMS, de la disponibilité LTE et de la politique opérateur. Un logo 5G ne permet pas de conclure que l'appel vocal restera en NR.

Pour diagnostiquer une expérience vocale, corrèle les événements radio, l'établissement de session, l'affectation des ressources QoS, les messages SIP/IMS autorisés à l'analyse, les transitions EPS/5GS et les statistiques de pertes/jitter. Respecte les règles de confidentialité et masque les identifiants abonnés dans les exports.

# Partie IV — QoS, slicing et services différenciés

## 10. Modèle QoS du 5GS

Dans le 5GS, les flux QoS sont identifiés notamment par un QFI (QoS Flow Identifier) au sein d'une session PDU. Le 5QI caractérise un ensemble de comportements QoS, comme le type de ressource, la priorité, un budget de délai de paquet et un taux de perte de paquet selon la définition applicable. La manière exacte de transporter les caractéristiques vers la radio dépend de l'architecture et du flux.

| Notion | À quoi elle sert | Ce qu'elle ne garantit pas à elle seule |
|---|---|---|
| 5QI | Référence de caractéristiques QoS | Un délai garanti de bout en bout sans capacité et politique adéquates |
| QFI | Identifie un flux QoS dans une session PDU | Une priorité globale indépendante des politiques du réseau |
| GBR | Flux avec débit garanti défini selon les paramètres applicables | Une capacité physique illimitée en cas de congestion massive |
| GFBR / MFBR | Débit garanti et débit maximal de flux lorsque ces paramètres s'appliquent | Le débit réellement observé par l'application à tout instant |
| ARP | Priorité de rétention/admission et règles de préemption prévues | La priorité de chaque paquet utilisateur en temps réel |
| DNN | Identifie le réseau de données demandé | Une segmentation de sécurité suffisante à lui seul |
| S-NSSAI | Identifie une slice au moyen du SST et éventuellement du SD | Une isolation complète de toutes les ressources physiques |

La priorité ARP concerne principalement les décisions d'admission et de rétention de ressources ; elle ne doit pas être confondue avec une règle de priorité paquet appliquée en permanence. Les paramètres QoS doivent être interprétés dans leur contexte normatif et leur configuration opérationnelle.

### 10.1 Concevoir une politique pour plusieurs services

Imaginons trois catégories :

1. Téléphonie interactive : priorité à la continuité, au délai et aux pertes très limitées.
2. Vidéo à la demande : besoin de débit soutenu, mais une mise en mémoire tampon peut absorber certaines variations.
3. Télémétrie industrielle : petits volumes, potentiellement contraintes strictes de disponibilité et de délai, selon l'application réelle.

On ne peut pas attribuer une politique QoS uniquement en fonction du nom du service. Il faut recueillir les objectifs métier, les caractéristiques du trafic, la criticité, la tolérance à la perte et au délai, les modèles d'appareils, la localisation et les exigences de sécurité.

Le chemin de décision peut être représenté ainsi :

```text
Exigence applicative
        |
        v
Authentification et autorisation de l'abonné / de l'application
        |
        v
Politique PCF et contrôle de session SMF
        |
        v
Paramètres de flux QoS dans la session PDU
        |
        v
Admission et configuration du RAN + règles de transfert UPF
        |
        v
Mesure du comportement réellement observé
```

Une politique peut être correctement définie dans le cœur mais ne pas produire le résultat attendu si la radio manque de ressources, si le transport est congestionné ou si l'application elle-même est lente.

### 10.2 Mesurer le délai correctement

Un temps aller-retour (RTT) mesuré par une application n'est pas équivalent au délai radio unidirectionnel. Le RTT inclut le chemin aller et retour, les files d'attente, le traitement des équipements et le comportement du serveur de test. Pour analyser un objectif de latence, précise :

- le point de départ et le point d'arrivée ;
- le sens de mesure et la méthode de synchronisation temporelle ;
- la taille et la fréquence des paquets ;
- la charge de la cellule et du transport ;
- les percentiles retenus, et non uniquement la moyenne ;
- les pertes, retransmissions et périodes d'inactivité.

Une valeur de latence très basse annoncée pour un segment technique n'est pas une garantie de latence applicative de bout en bout.

## 11. Network slicing : modèle, sélection et isolation

Le slicing permet de concevoir plusieurs réseaux logiques sur une infrastructure commune, avec des caractéristiques, des fonctions et des politiques adaptées aux services. Une slice 5GS est identifiée par un S-NSSAI comprenant un Slice/Service Type (SST) et, lorsque nécessaire, un Slice Differentiator (SD).

Exemple pédagogique de trois slices :

```text
Infrastructure physique partagée
+------------------------------------------------+
| RAN | transport | 5GC | système de supervision |
+------------------------------------------------+
       |                |                 |
       v                v                 v
 Slice A           Slice B           Slice C
 Haut débit         IoT massif        Service critique
 DNN public         DNN capteurs      DNN industriel
 Politique QoS      Politique énergie Politique résilience
```

Ce dessin est conceptuel. Un déploiement réel peut partager certaines fonctions, réserver d'autres ressources, utiliser des UPF différents ou appliquer des mécanismes d'isolation variables. Une slice n'est pas automatiquement un réseau physiquement indépendant.

### 11.1 Concevoir une slice sérieusement

Une conception de slice doit décrire :

- les utilisateurs et équipements autorisés ;
- le S-NSSAI et les règles d'abonnement/présentation correspondantes ;
- les DNN et les sorties vers les réseaux de données ;
- les zones géographiques et conditions de mobilité ;
- les fonctions réseau utilisées et leurs critères de placement ;
- les budgets de capacité, les objectifs de performance et les métriques ;
- les frontières de sécurité, les accès d'administration et la journalisation ;
- les scénarios de panne, la capacité de secours et le comportement en surcharge ;
- le coût, les quotas, le cycle de vie et le déclassement.

### 11.2 Contrôler la sélection et le résultat

Le terminal peut présenter des informations de sélection de slice autorisées par son profil, mais le réseau effectue les vérifications et sélectionne les fonctions appropriées selon les règles et l'abonnement. Le NSSF participe aux mécanismes de sélection de slice et aux informations associées. Il ne remplace pas à lui seul les contrôles d'abonnement, le contrôle de session, le routage ni la configuration du RAN.

Pour valider une slice, teste au minimum :

1. un abonné autorisé ;
2. un abonné non autorisé ;
3. un terminal en mobilité vers une zone sans la même disponibilité ;
4. une congestion dans une ressource partagée ;
5. la perte d'une fonction du cœur ou d'un chemin transport ;
6. un accès à un DNN non attendu ;
7. les journaux et la visibilité des incidents sans fuite d'information inter-slice.

**Point de sécurité :** la séparation logique doit être appuyée par des politiques explicites, des contrôles d'accès, une validation du chemin de données et une surveillance des ressources partagées.

# Partie V — Sécurité, résilience et interconnexion

## 12. Sécurité 5G : examiner les frontières de confiance

La sécurité ne se réduit pas au chiffrement radio. Les risques couvrent le terminal, la carte d'abonné, le RAN, le cœur, les interfaces de service, le transport, les API d'administration, l'orchestration, les fournisseurs et les interconnexions avec d'autres réseaux.

Parmi les mécanismes normalisés figurent notamment les procédures d'authentification et de gestion des identités, la protection de la confidentialité de l'identité permanente au moyen de mécanismes associés à SUCI/SUPI, la sécurité des accès radio et NAS, ainsi que des protections pour différentes interfaces. Les déploiements doivent suivre la spécification et les recommandations de sécurité applicables à la version prise en charge.

### 12.1 Analyse par frontière

| Zone | Risques à examiner | Mesures à valider |
|---|---|---|
| Terminal et USIM | Terminal compromis, identité exposée, profil erroné | Sécurité du terminal, authentification, politique de mise à jour |
| RAN | Accès physique, mauvaise configuration, déni de service radio | Durcissement, contrôle d'accès, surveillance et procédures d'intervention |
| SBA du 5GC | Appel de service non autorisé, usurpation, exposition de données | Authentification mutuelle quand prévue, protection du transport, autorisations, certificats et segmentation |
| Plan utilisateur | Mauvais routage, abus de tunnel, fuite entre réseaux de données | Filtrage, validation de règles, segmentation, contrôle des chemins et télémétrie |
| OAM et orchestration | Privilèges excessifs, secret exposé, changement non approuvé | MFA, moindre privilège, gestion des secrets, journalisation et approbation de changement |
| Roaming/interconnexion | Usurpation ou abus d'interface, fuite de données | Contrôles interopérateurs, politiques, filtrage et mécanismes de sécurité adaptés comme SEPP lorsque requis |
| Chaîne logicielle | Composant vulnérable, image altérée, dépendance non suivie | Inventaire, provenance, correctifs, validation et séparation des environnements |

L'architecture SBA utilise des interactions entre fonctions réseau ; dans de nombreux déploiements, elles utilisent des API fondées sur HTTP/2 et des mécanismes d'identité/protection de transport selon les exigences et le modèle de confiance. Ne suppose pas que tout appel interne est automatiquement sûr parce qu'il est situé sur un réseau privé.

### 12.2 Identifiants et confidentialité

Une capture de signalisation peut contenir des identifiants, des informations de localisation, des données d'abonnement ou des informations de session. Les extraits utilisés dans les tickets doivent minimiser les données : pseudonymise les identifiants, limite l'accès, définit une durée de conservation et évite de publier des traces complètes dans des outils non approuvés.

L'utilisation de SUCI protège certains usages de l'identité permanente sur l'accès radio lorsque les mécanismes et configurations correspondants sont correctement déployés. Cela ne rend pas tous les métadonnées de signalisation invisibles et ne supprime pas la nécessité de protéger les données et journaux dans le cœur.

## 13. Résilience du cœur, haute disponibilité et reprise

La redondance nominale n'équivaut pas à la résilience. Un service peut rester indisponible malgré plusieurs instances si elles partagent une dépendance commune : réseau, stockage, zone, configuration, certificat, base de données ou plan de contrôle.

La conception doit considérer :

- la redondance géographique et les domaines de panne ;
- la découverte et le retrait d'une fonction indisponible ;
- les délais de détection, de bascule et de restauration ;
- la cohérence des données et des états de session ;
- le comportement des sessions déjà établies en cas de panne UPF ;
- la capacité restante sous charge pendant la panne ;
- les certificats, DNS, synchronisation horaire, PKI et accès OAM ;
- les procédures de restauration testées et la preuve de retour au service.

### 13.1 Définir les objectifs de reprise

Pour chaque service, définis un objectif de point de reprise (RPO) lorsqu'il s'applique, un objectif de temps de reprise (RTO), la perte de service acceptable, les fonctions prioritaires et le mode de dégradation. Les objectifs doivent correspondre à des tests et ne pas rester uniquement dans une documentation de conception.

Un exercice de résilience ne doit pas se limiter à couper une instance de test. Il faut observer si les consommateurs découvrent la fonction restante, si les sessions existantes continuent ou sont rétablies, si les alarmes sont pertinentes et si la capacité après bascule suffit.

# Partie VI — Transport, synchronisation et architecture distribuée

## 14. Le transport conditionne la performance mobile

Le transport relie les sites radio, l'agrégation, le cœur et les réseaux applicatifs. Les segments sont souvent distingués en fronthaul, midhaul et backhaul selon l'architecture de séparation des fonctions RAN. Ces termes ne correspondent pas à un découpage physique universel : leur usage dépend du niveau de centralisation et des interfaces réellement déployées.

Le transport doit être évalué pour :

- la capacité moyenne et la capacité de pointe ;
- la latence et la variation de délai ;
- la perte de paquets et la congestion ;
- la disponibilité et la convergence après panne ;
- la synchronisation de fréquence et de phase lorsque requise ;
- la MTU, le marquage QoS, les files d'attente et l'ingénierie de trafic ;
- la sécurité et l'isolation des services.

### 14.1 Synchronisation

Les réseaux TDD et certaines configurations radio avancées nécessitent une synchronisation rigoureuse en fréquence et en phase. Des erreurs de synchronisation peuvent provoquer une dégradation de performance ou des interférences, même si la connectivité IP semble saine.

PTP (Precision Time Protocol), SyncE et d'autres méthodes peuvent être utilisés selon les besoins et la conception. Leur présence ne garantit pas à elle seule la qualité : il faut mesurer l'erreur de temps, surveiller les sources et chemins de synchronisation, gérer les pertes de référence et tester le comportement de holdover.

### 14.2 MTU et tunnels

Le plan utilisateur peut transporter GTP-U sur IP/UDP, auquel s'ajoutent les en-têtes de l'IP sous-jacent, du transport et potentiellement d'autres mécanismes. Une MTU insuffisante peut provoquer fragmentation, pertes ou comportements difficiles à reproduire, tandis qu'une MTU trop élevée peut entraîner des paquets rejetés sur un segment plus étroit.

Lors d'un diagnostic : vérifie la MTU sur l'ensemble du chemin, les compteurs d'erreurs, la fragmentation, les messages ICMP utiles, les politiques de filtrage et les différences de comportement selon la taille des paquets. Ne modifie pas la MTU sans cartographier les segments et prévoir une validation de bout en bout.

# Partie VII — Virtualisation, O-RAN et automatisation

## 15. RAN désagrégé et O-RAN

Une architecture RAN désagrégée sépare certaines fonctions radio afin de permettre un placement, une évolutivité et éventuellement une interopérabilité plus flexibles. Dans une architecture NR, la gNB peut être répartie en CU et DU ; la radio peut être identifiée comme RU dans certains modèles O-RAN. L'architecture et les interfaces exactes dépendent du déploiement.

Le vocabulaire O-RAN inclut notamment :

- **O-RU** : unité radio ;
- **O-DU** : unité distribuée ;
- **O-CU-CP** : plan de contrôle de l'unité centrale ;
- **O-CU-UP** : plan utilisateur de l'unité centrale ;
- **Near-RT RIC** : contrôleur RAN intelligent en temps quasi réel ;
- **Non-RT RIC** : fonctions d'optimisation et d'orchestration à des échelles de temps plus longues.

Les rApps et xApps sont des applications associées aux cadres Non-RT RIC et Near-RT RIC selon leur rôle et les spécifications applicables. Elles ne doivent pas être confondues avec les fonctions de base obligatoires de chaque gNB.

### 15.1 Avantages et coûts de l'ouverture

Avantages potentiels : choix élargi de composants, automatisation, innovation, visibilité via des interfaces définies et évolution plus modulaire.

Risques et coûts : intégration multivendeur, gestion des versions, synchronisation, latence des interfaces, cohérence des fonctions, sécurité de la chaîne d'approvisionnement, tests de conformité, responsabilité partagée et diagnostic plus complexe.

Une interface dite « ouverte » n'assure pas automatiquement l'interopérabilité de toutes les combinaisons de matériels et de logiciels. Il faut vérifier les profils pris en charge, les versions, les tests de conformité et l'intégration système.

## 16. Cloud-native et orchestration du cœur

Les fonctions réseau peuvent être fournies sous forme d'applications virtualisées, de conteneurs ou de solutions hybrides. Le choix influe sur la densité, les cycles de mise à jour, l'observabilité et les domaines de panne.

Les principales exigences d'exploitation comprennent :

- capacité CPU, mémoire, accélération réseau et ressources de paquets ;
- placement et affinité tenant compte de la latence et de la résilience ;
- réseau de cluster, politiques d'accès et gestion des certificats ;
- gestion des configurations et des secrets ;
- mises à jour progressives, canaris et retour arrière ;
- supervision de l'application et de la plateforme ;
- limites explicites de ressources et tests sous charge ;
- inventaire des versions et analyse des vulnérabilités.

La virtualisation peut améliorer la flexibilité, mais les charges de traitement de paquets, le temps réel et la synchronisation peuvent imposer des exigences particulières de placement, de CPU, de NIC et de configuration système.

## 17. Automatisation sûre des opérations

L'automatisation devient indispensable lorsque le nombre de cellules, de paramètres et de sites augmente. Elle doit cependant limiter l'impact des erreurs de configuration à grande échelle.

Un pipeline de changement réseau devrait comporter :

1. collecte d'état et validation de la source de vérité ;
2. génération d'un changement versionné ;
3. validation syntaxique et contrôle des valeurs autorisées ;
4. comparaison de l'état attendu et de l'état réel ;
5. simulation ou validation en environnement pilote ;
6. déploiement progressif par groupe de sites ;
7. contrôle automatisé des KPI et alarmes ;
8. arrêt ou retour arrière si les seuils de sécurité sont dépassés ;
9. archivage de l'état précédent, du résultat et de l'approbation.

Exemple de logique en pseudocode :

```python
# Pseudocode pédagogique : à adapter à l'API et aux garde-fous du fournisseur.

change = load_change_request("nr-cell-profile-042")
assert change.approved
assert validate_schema(change)
assert all(value in allowed_ranges for value in change.parameters)

before = collect_kpis(change.target_sites, window="baseline")
apply_to_canary(change)

if not health_checks_pass(change.target_sites):
    rollback(change)
else:
    after = collect_kpis(change.target_sites, window="post-change")
    if regression_detected(before, after):
        rollback(change)
    else:
        expand_gradually(change)
```

Ce pseudocode ne se connecte pas à un équipement et ne doit pas être exécuté tel quel. Il décrit une méthode. Les seuils de non-régression doivent être spécifiques au service et tenir compte de la variabilité statistique.

# Partie VIII — Observabilité et optimisation experte

## 18. Concevoir une chaîne d'observabilité de bout en bout

Un tableau de bord expert doit relier les niveaux suivants :

```text
Expérience utilisateur
  ├─ délai applicatif, débit utile, échecs, qualité vocale
  ↓
Session et cœur
  ├─ enregistrement, sessions PDU, QFI, UPF, pertes, erreurs de politique
  ↓
Transport
  ├─ capacité, files, MTU, latence, synchronisation, erreurs interfaces
  ↓
RAN
  ├─ RSRP/RSRQ/SINR, BLER, PRB, MCS, MIMO, accès et handover
  ↓
Infrastructure et exploitation
  ├─ CPU, mémoire, NIC, certificats, API, orchestration, alarmes
```

L'objectif est de rendre possible une corrélation temporelle et géographique. Un débit bas sur l'application peut provenir du serveur distant ; une hausse de latence peut venir d'une file de transport ; un échec de session peut provenir de l'autorisation d'abonnement ou d'une fonction de contrôle. La corrélation ne prouve pas la cause, mais permet de réduire l'espace de recherche.

### 18.1 KPI et formules de base

Les définitions exactes de KPI opérateur dépendent des normes, du fournisseur, de la collecte et de la politique de calcul. Les formules ci-dessous sont des définitions génériques illustratives.

**Taux de succès d'établissement de session**

\[
SR = \frac{N_{\text{établissements réussis}}}{N_{\text{tentatives valides}}}\times100\%
\]

**Taux de succès de handover**

\[
HOSR = \frac{N_{\text{handovers réussis}}}{N_{\text{tentatives de handover éligibles}}}\times100\%
\]

**Taux de perte de paquets**

\[
PLR = \frac{N_{\text{paquets perdus}}}{N_{\text{paquets transmis}}}\times100\%
\]

**Disponibilité sur une fenêtre**

\[
A = \frac{T_{\text{fenêtre}}-T_{\text{indisponibilité définie}}}{T_{\text{fenêtre}}}\times100\%
\]

Chaque calcul nécessite une définition claire du dénominateur, de la fenêtre, des événements comptabilisés, de l'exclusion des données incomplètes et du niveau d'agrégation. Une hausse d'un taux peut résulter d'une modification de la collecte et non d'une amélioration réelle.

### 18.2 Moyennes, percentiles et pièges d'agrégation

Une moyenne peut masquer une mauvaise expérience pour un groupe restreint d'utilisateurs. Pour un délai, un débit ou une durée de procédure, examine les percentiles (par exemple P50, P90, P95 et P99), les distributions, les zones et les types de terminal. Évite de mélanger des échantillons obtenus avec des méthodes de mesure différentes.

Pour les événements rares, les petites fenêtres peuvent être trompeuses. Pour les incidents géographiques, une moyenne nationale peut noyer une zone affectée. Pour les services critiques, complète les métriques globales par des objectifs localisés et des tests synthétiques.

## 19. Méthode de diagnostic en cinq étapes

### Étape 1 — Définir le symptôme

Précise qui est affecté, où, quand, sur quel service, avec quel modèle de terminal, sur quelle bande et dans quel état de mobilité. Distingue un incident global d'un problème localisé ou d'une seule application.

### Étape 2 — Construire une chronologie

Synchronise autant que possible l'heure des événements : tentative d'accès, mesure radio, signalisation NAS/RRC, mise en place de session, tunnel UPF, bascule de cellule, mesure applicative et début de la dégradation.

### Étape 3 — Localiser la frontière défaillante

Découpe la chaîne en domaines : terminal, RAN, transport, contrôle 5GC, plan utilisateur, interconnexion, DNS, serveur et application. Vérifie quelle frontière a cessé de satisfaire l'objectif en premier.

### Étape 4 — Tester une hypothèse

Formule une hypothèse falsifiable, identifie une métrique discriminante et compare les terminaux ou sites témoins. Une hypothèse comme « la 5G est lente » est trop large ; « la perte augmente après l'UPF local lorsque le trafic dépasse un seuil de charge » est testable.

### Étape 5 — Corriger, observer et documenter

Applique un changement limité, surveille les métriques avant/après, confirme l'absence de régression et conserve les preuves. Si le résultat n'est pas concluant, reviens à l'état précédent et poursuis le diagnostic.

## 20. Procédure pratique d'analyse d'un flux utilisateur

Le laboratoire ci-dessous est un exercice d'analyse. Les commandes exactes sur un équipement mobile dépendent du fournisseur et ne sont pas universelles.

1. Identifier le terminal de test et la session concernée sans exposer d'identifiant abonné dans le rapport.
2. Relever la cellule, la bande, le mode SA/NSA et les mesures radio disponibles.
3. Confirmer l'enregistrement du terminal et le type de session PDU.
4. Vérifier le DNN, la famille d'adresses et la sélection SMF/UPF attendue.
5. Confirmer que les règles de transfert UPF existent dans les deux sens nécessaires.
6. Examiner l'état du tunnel N3 et les compteurs du chemin vers N6.
7. Vérifier le routage, la résolution DNS et les politiques réseau de destination.
8. Mesurer le débit applicatif, le RTT, la perte et les percentiles avec un serveur de test connu.
9. Répéter le test sous différentes charges et, si possible, avec un terminal ou une cellule témoin.
10. Consigner les hypothèses rejetées et les observations reproductibles.

Exemples de commandes Linux génériques pouvant aider sur une machine de test ou un serveur autorisé :

```bash
# Adresses et routes de la machine de test
ip address show
ip route show
ip -6 route show

# Vérifier la résolution DNS
getent ahosts example.net

# Mesure de latence IP : la destination doit autoriser ICMP
ping -c 20 example.net

# Chemin réseau : utiliser l'outil présent sur le système
tracepath example.net
# ou, si installé et autorisé :
traceroute example.net

# Observer les interfaces et compteurs
ip -s link

# Capturer uniquement sur une interface que l'on est autorisé à observer
sudo tcpdump -ni eth0 -c 200 'host 192.0.2.10'
```

`example.net` et `192.0.2.10` sont des exemples de documentation ; remplace-les par des valeurs de laboratoire autorisées. Une capture côté serveur ne remplace pas une trace N3/N6 du réseau mobile. Il faut aussi respecter la confidentialité, les règles internes et le périmètre d'autorisation.

# Partie IX — Études de cas guidées

## 21. Étude de cas A : débit DL faible dans une cellule 5G SA

### Contexte

Une cellule NR de 100 MHz dessert plusieurs centaines de terminaux. Les utilisateurs signalent un débit faible en soirée. Le signal RSRP est généralement bon, mais le débit P95 chute lors des heures chargées.

### Hypothèses possibles

- capacité radio saturée ;
- SINR dégradé par l'interférence ;
- faible nombre de couches MIMO effectivement utilisé ;
- configuration TDD défavorable à la charge DL ;
- transport congestionné ;
- limitation du serveur ou du chemin externe ;
- politique QoS ou limitation d'abonné ;
- terminal incompatible avec la combinaison de porteuses attendue.

### Plan d'analyse

1. Comparer débit, PRB DL, SINR, BLER, MCS et nombre de couches MIMO.
2. Segmenter les mesures par zone, terminal et heure.
3. Vérifier le débit au niveau du transport en parallèle du débit applicatif.
4. Répéter avec un serveur local connu puis avec une destination Internet.
5. Comparer une période de faible charge à une période de pointe.
6. N'envisager un changement de TDD, d'antenne ou de porteuses qu'après avoir identifié le goulot dominant.

### Conclusion possible

Si la cellule est saturée alors que le SINR est bon, optimiser la radio seule peut ne pas suffire : l'ajout de capacité, la réorganisation de la charge ou une amélioration de l'efficacité spectrale peut être nécessaire. Si le débit baisse en même temps que la capacité du transport s'épuise, l'action prioritaire se situe ailleurs.

## 22. Étude de cas B : session PDU acceptée, mais aucun accès applicatif

### Symptôme

Le terminal s'enregistre, crée une session PDU et reçoit une configuration IP, mais ne peut joindre aucune application externe.

### Arbre de diagnostic

```text
Adresse IP attribuée ?
  ├─ Non : vérifier procédure session, abonnement, DNN, SMF, pool d'adresses
  └─ Oui
      |
      v
Règles de transfert UPF actives ?
  ├─ Non : inspecter programmation de session et règles PFCP
  └─ Oui
      |
      v
Paquets présents sur N3 ?
  ├─ Non : vérifier RAN, bearer/flux, tunnel et compteurs radio
  └─ Oui
      |
      v
Paquets visibles en sortie N6 ?
  ├─ Non : vérifier règles UPF, routage, ACL, MTU, filtrage
  └─ Oui
      |
      v
Destination joignable par IP ?
  ├─ Non : vérifier route retour, pare-feu et réseau de données
  └─ Oui : vérifier DNS, TLS, proxy, application et politiques L7
```

Cette séquence est un guide de triage, non une garantie que tous les environnements suivent exactement ce chemin. Des mécanismes NAT, des règles de sécurité, des tunnels additionnels ou des architectures de sortie locale peuvent modifier les points d'observation.

## 23. Étude de cas C : voix 5G instable lors de déplacements

### Symptôme

Les données restent utilisables, mais les appels se coupent à certains endroits pendant le déplacement.

### Pistes à vérifier

- état IMS/VoNR et compatibilité du terminal ;
- bascule EPS fallback ou mobilité entre 5GS/EPS ;
- qualité radio et continuité pendant le handover ;
- admission et maintien des ressources QoS vocales ;
- messages de signalisation IMS corrélés aux événements radio ;
- couverture LTE de secours, si cette stratégie est utilisée ;
- latence, pertes et jitter sur le chemin voix ;
- configuration des voisins et transitions inter-RAT.

### Mesure de résolution

Un incident est considéré résolu seulement après une campagne de tests répétée sur le trajet concerné, avec plusieurs terminaux si possible, et une confirmation que le taux de coupure et la qualité vocale s'améliorent sans dégrader les autres services.

# Partie X — Travaux pratiques

## TP 1 — Calcul de capacité et identification d'un goulot

### Objectif

Comparer la capacité radio théorique simplifiée au débit utilisateur mesuré et proposer une analyse argumentée.

### Données

Une cellule dispose de :

- bande passante configurée : 80 MHz ;
- efficacité spectrale moyenne estimée par couche : 2,5 bit/s/Hz ;
- nombre moyen de couches utiles : 2 ;
- facteur global estimé pour overhead et partage de ressources : 0,65 ;
- débit applicatif DL observé en période de pointe : 110 Mbit/s pour le terminal de test.

### Travail demandé

1. Calculer le débit approximatif selon le modèle présenté plus haut.
2. Calculer le rapport entre débit observé et estimation théorique.
3. Lister au moins cinq explications possibles de cet écart.
4. Proposer trois mesures qui permettraient de différencier les hypothèses.

### Correction

Capacité approximative :

\[
80\times10^6 \times 2{,}5 \times 2 \times 0{,}65 = 260\ \text{Mbit/s}
\]

Rapport débit observé/approximation :

\[
110/260 \approx 0{,}423 \quad \text{soit environ }42{,}3\%
\]

Ce ratio n'est pas directement une « efficacité radio réelle » car l'estimation et le débit mesuré ne représentent pas nécessairement la même couche de protocole ou la même période. Les écarts peuvent provenir de la charge, d'un SINR faible, d'une planification de ressources limitée, d'un mauvais usage des couches MIMO, du TDD, de retransmissions, du transport, d'un serveur lent ou d'une limitation du profil de service.

Mesures utiles : corréler PRB/SINR/BLER/MCS et couches MIMO ; comparer mesure sur serveur local et Internet ; regarder la capacité du transport et les percentiles par heure. L'action corrective dépend des résultats.

## TP 2 — Diagnostiquer une mobilité défaillante

### Données fictives

Sur une route, 1 000 tentatives de handover éligibles sont observées. 940 se terminent avec succès. Les événements montrent une concentration d'échecs lors de l'entrée dans deux cellules cibles ; certains handovers réussis sont suivis d'un retour vers la cellule source en moins de quelques secondes.

### Travail demandé

1. Calculer le taux de succès global.
2. Identifier pourquoi la moyenne globale est insuffisante.
3. Dresser une liste des traces à corréler.
4. Proposer un plan de test qui distingue problème radio, admission cible et paramètres de mobilité.

### Correction

\[
HOSR = \frac{940}{1000}\times100\% = 94\%
\]

Le résultat ne décrit ni la distribution par cellule, ni la cause des 60 échecs, ni la part des ping-pong. Il faut segmenter par cellule source/cible, bande, terminal, heure, cause de rejet et type de handover.

Corréler les mesures UE/RRC, la préparation de cible, les causes de rejet, les ressources disponibles, le résultat d'accès radio à la cible et l'évolution du chemin utilisateur. Un test contrôlé compare plusieurs terminaux et trajets, puis ne change qu'un paramètre de mobilité ou d'admission à la fois, avec mesures avant/après et procédure de retour arrière.

## TP 3 — Concevoir une QoS pour un service industriel

### Scénario

Une usine veut connecter des capteurs, des caméras de maintenance et un système de commande. Les flux de commande sont sensibles au délai et à la perte ; les caméras ont besoin d'un débit soutenu ; les capteurs envoient de petits messages périodiques.

### Travail demandé

1. Rédiger les questions à poser au client avant d'attribuer un 5QI.
2. Proposer une politique différenciée sans inventer de valeurs normalisées.
3. Définir les mesures de validation et la gestion d'une surcharge.
4. Expliquer pourquoi une QoS radio correcte ne suffit pas.

### Correction

Il faut obtenir la périodicité et la taille des messages, les délais acceptables, le taux de perte maximal, la criticité et les conséquences d'un retard, les débits agrégés, la mobilité, la couverture indoor, les exigences de sécurité et les objectifs de disponibilité.

Les flux de commande peuvent nécessiter une classe adaptée à leurs caractéristiques et une capacité admissionnée ; la vidéo peut être traitée selon une politique de débit soutenu ; les capteurs peuvent relever d'une catégorie de trafic de faible volume optimisée en coût/énergie. Le 5QI exact doit être choisi à partir des tables et de l'implémentation prises en charge, pas deviné à partir du nom du service.

Valider délai P95/P99, perte, jitter, taux d'établissement, débit, comportement sous surcharge et pendant la mobilité. Mesurer le chemin de bout en bout, y compris transport, UPF et application. Prévoir une hiérarchie de dégradation, une admission contrôlée et une supervision de la capacité restante.

## TP 4 — Vérifier la cohérence d'une slice

### Scénario

Une entreprise utilise une slice « industriel » et un DNN privé. Après une modification d'abonnement, certains terminaux sont dirigés vers le DNN public.

### Travail demandé

1. Identifier les domaines susceptibles d'expliquer le problème.
2. Préparer une liste de vérifications, de l'abonnement au plan utilisateur.
3. Définir des tests négatifs pour vérifier que l'accès non autorisé est refusé.
4. Lister les preuves à conserver dans le rapport d'incident.

### Correction

Examiner le profil d'abonnement et les S-NSSAI autorisés, les informations de sélection, le DNN demandé, les règles PCF/SMF, la sélection UPF, la programmation des règles de transfert et le routage en sortie. Vérifier les changements récents, les caches ou la cohérence des données de provisionnement.

Tester un terminal autorisé, un terminal non autorisé, un DNN erroné, une cellule de destination différente et un cas de perte d'une fonction. Le refus doit être explicite et observable. Conserver une chronologie, les paramètres de session pseudonymisés, les décisions pertinentes, les traces utiles, les versions de configuration et les résultats de tests. Ne joins pas de données personnelles inutiles.

## TP 5 — Construire un tableau de bord de diagnostic

### Objectif

Concevoir un tableau de bord qui rapproche expérience utilisateur, RAN, transport et 5GC.

### Travail demandé

Créer un tableau avec au moins les colonnes suivantes : KPI, définition, source, granularité, fréquence de collecte, seuil d'alerte, segment de population, responsable et action à lancer.

### Correction indicative

| KPI | Source | Granularité | Action si dégradation confirmée |
|---|---|---|---|
| Succès d'établissement PDU | Traces/statistiques SMF et AMF | Région, DNN, slice, fenêtre | Analyser cause de rejet et dépendances de fonction |
| Débit DL P95 | Mesures UE et test applicatif | Cellule, bande, terminal | Corréler charge, radio et transport |
| BLER DL/UL | Compteurs RAN | Cellule et période | Vérifier radio, interférences, mobilité et réglages |
| Succès de handover | RAN/NGAP selon mesure | Source/cible, type de mobilité | Décomposer préparation et exécution |
| Perte sur N3/N6 | Compteurs et mesures autorisés | UPF, interface, chemin | Vérifier tunnel, MTU, files et routage |
| Délai P95 applicatif | Sonde applicative | Service, zone et terminal | Comparer réseau, serveur et chemin externe |
| Disponibilité UPF | Supervision 5GC | Instance, pool, zone | Vérifier surcharge, dépendances et bascule |

Le tableau doit montrer les tendances et conserver suffisamment de contexte pour ne pas déclencher des alertes sur des données trop faibles ou non comparables. Les seuils sont définis à partir des objectifs de service et de la base de référence opérationnelle.

# Partie XI — Défi final corrigé

## 24. Défi : concevoir une stratégie d'amélioration 5G SA pour un campus industriel

### Contexte

Un opérateur déploie une couverture 5G SA sur un campus industriel et commercial. Trois catégories de service coexistent :

- employés : accès Internet et applications bureautiques ;
- maintenance : vidéo, assistance distante et transfert de fichiers ;
- commande industrielle : flux de contrôle sensibles à la perte et au délai.

Les sites radio disposent d'une capacité limitée et certains bâtiments ont une mauvaise couverture intérieure. Le cœur est centralisé, mais l'opérateur peut envisager un UPF en périphérie. Il faut proposer une stratégie sans promettre une latence ou une disponibilité qui n'a pas été mesurée.

### Tâches

1. Proposer une architecture logique 5G SA.
2. Définir une méthode de traitement différencié des trois catégories.
3. Expliquer quand une slice est utile et quelles garanties doivent l'accompagner.
4. Évaluer l'intérêt potentiel d'un UPF local/MEC.
5. Définir un plan de mesure radio et de mobilité.
6. Établir les contrôles de sécurité et de résilience.
7. Construire un plan de déploiement progressif et de retour arrière.
8. Définir cinq KPI prioritaires et la manière de les valider.

### Correction détaillée

#### 1. Architecture proposée

```text
Terminal industriel / employés
             |
             v
    Couverture NR SA (gNB)
             |
       N2 / N3 sur transport sécurisé et dimensionné
             |
      +------+------------------+
      |                         |
      v                         v
  5GC central             UPF local de campus (si justifié)
  AMF / SMF / PCF                 |
  UDM / AUSF / NRF / NSSF         +---- applications MEC
      |                           +---- DNN industriel
      +---- fonctions de politique
```

Le schéma est logique : l'emplacement réel des fonctions dépend de la capacité, des besoins de résilience, du modèle de confiance et des contraintes de transport. NSSF ne remplace pas la politique d'abonnement ; PCF et SMF contribuent au contrôle des règles ; UPF applique le transfert des paquets selon la session et la configuration.

#### 2. Traitement différencié

- **Employés :** accès Internet avec quotas et règles de sécurité standards de l'entreprise, sans réserver inutilement les ressources les plus critiques.
- **Maintenance vidéo :** objectifs de débit et de stabilité adaptés au besoin, avec priorité opérationnelle définie lors de congestion et politiques de sécurité vers les systèmes internes.
- **Commande industrielle :** exigences chiffrées définies par le fabricant du système et les responsables industriels avant toute configuration ; contrôle d'admission, chemin de données maîtrisé, redondance appropriée et surveillance dédiée.

Le réseau doit transformer les exigences applicatives en politiques de session et radio vérifiables. On ne choisit pas un 5QI uniquement parce qu'un service s'appelle « industriel ».

#### 3. Slice et isolation

Une ou plusieurs slices peuvent séparer la politique et les ressources logiques des services critiques, si l'abonnement, le terminal, le RAN et le cœur prennent en charge cette architecture. Le DNN sépare le réseau de données demandé, mais n'est pas à lui seul une frontière de sécurité complète. Les contrôles doivent couvrir le routage, les accès, l'administration, les ressources partagées et le comportement en panne.

Avant la mise en production, tester accès autorisés et interdits, surcharge, perte d'une fonction, mobilité vers une autre zone, isolation des journaux et capacité en mode dégradé.

#### 4. Intérêt d'un UPF local/MEC

Un UPF local peut raccourcir le chemin vers une application hébergée sur le campus et permettre des sorties locales. L'intérêt doit être démontré par les mesures du parcours de données. Il faut étudier le routage retour, la sécurité, l'adressage, le DNS, la disponibilité locale, les mises à jour de l'application et le plan de reprise si le site local tombe.

Si l'application reste hébergée dans un centre de données distant, ajouter un UPF local ne suffit pas forcément. Le choix se fait sur un test comparatif de bout en bout, en charge normale et dégradée.

#### 5. Radio et mobilité

Effectuer un relevé de couverture indoor/outdoor et de capacité, avec RSRP/RSRQ/SINR, tests UL et DL, mesures de charge, scénarios de déplacement et modèle de terminal. Analyser les échecs de handover, les zones de ping-pong, la couverture à la frontière des cellules et la transition entre zones couvertes par des technologies différentes. La couverture des systèmes industriels prioritaires doit être validée en conditions d'exploitation, pas seulement à vide.

#### 6. Sécurité et résilience

Utiliser le moindre privilège, des identités de service gérées, une protection adéquate des interfaces, une segmentation et des ACL validées, une gestion des secrets et certificats, une journalisation avec rétention contrôlée, ainsi qu'un processus de correctifs. Établir les dépendances de l'UPF local, du transport, de la synchronisation, des fonctions du cœur et de l'application.

Définir les objectifs de reprise, la capacité restante après panne et la procédure de retour au service. Tester des pannes réalistes dans une fenêtre autorisée avant d'annoncer des objectifs de disponibilité.

#### 7. Déploiement progressif

1. Établir une référence de performance et une cartographie des risques.
2. Configurer un environnement de validation représentatif.
3. Déployer sur un petit groupe de cellules et de terminaux pilotes.
4. Comparer les KPI à la référence, y compris les services non ciblés.
5. Étendre par lots, avec arrêt automatique en cas de régression majeure.
6. Maintenir la configuration précédente pour le retour arrière.
7. Valider les opérations, la documentation et l'acceptation client.

Chaque changement doit inclure un propriétaire, une fenêtre, un risque, une preuve de validation et un plan de rollback. Le retour arrière doit être testé, et pas seulement documenté.

#### 8. KPI prioritaires

| KPI | Méthode de mesure | Usage |
|---|---|---|
| Succès d'établissement PDU | Tentatives et succès définis par le réseau | Détecter les problèmes d'accès, d'abonnement ou de cœur |
| Succès de handover | Mesure segmentée source/cible et type | Vérifier mobilité et continuité |
| Débit DL/UL P95 | Sondes et tests de référence | Vérifier expérience des employés et maintenance |
| Latence et perte P95/P99 | Mesure aux points de service définis | Valider les exigences industrielles de bout en bout |
| Disponibilité du service critique | Tests synthétiques et incidents confirmés | Vérifier résilience réelle plutôt que disponibilité d'un seul composant |

Les seuils doivent provenir des exigences validées avec le client et de la capacité réellement mesurée. Il n'est pas professionnel d'attribuer des valeurs arbitraires puis de déclarer le service conforme sans campagne de test.

# Partie XII — Exercices de synthèse corrigés

## Exercice 1 — Architecture

**Question :** une entreprise voit l'indicateur 5G sur ses terminaux. Peut-on conclure qu'elle utilise un 5G Core et qu'elle bénéficie d'une slice SA ?

**Correction :** non. L'affichage du terminal ne permet pas de déterminer à lui seul l'architecture exacte. Il faut vérifier le mode SA/NSA, la procédure d'accès, le cœur utilisé, le support de slicing et la configuration réellement provisionnée.

## Exercice 2 — Débit et radio

**Question :** le RSRP est bon mais le débit est bas. Quelles données faut-il vérifier avant de changer l'orientation de l'antenne ?

**Correction :** SINR/RSRQ, BLER, charge PRB, MCS, nombre de couches MIMO, bandes et CA, configuration TDD, charge du transport, serveur de test, profil de service et éventuelles limitations terminal. Le RSRP seul n'explique pas la performance.

## Exercice 3 — QoS

**Question :** quelle est la différence entre 5QI et ARP ?

**Correction :** le 5QI fait référence à des caractéristiques de traitement QoS d'un flux. L'ARP sert principalement aux décisions d'admission et de rétention de ressources avec les règles de préemption applicables. Ils répondent à des fonctions différentes.

## Exercice 4 — Slicing

**Question :** une slice dédiée est-elle forcément isolée physiquement des autres slices ?

**Correction :** non. Les slices peuvent partager des ressources physiques et certaines fonctions. Le niveau d'isolation dépend du design, de la configuration, des contrôles d'accès, de la gestion des ressources et des validations réalisées.

## Exercice 5 — UPF de périphérie

**Question :** un UPF local garantit-il une latence applicative basse ?

**Correction :** non. Il peut réduire une partie du chemin de transport si l'application est proche et le routage adéquat, mais la radio, la congestion, le traitement applicatif, le chemin retour et les retransmissions restent déterminants.

## Exercice 6 — Mobilité

**Question :** le taux de succès de handover est de 99 % au niveau national, mais une usine subit des coupures fréquentes. Quelle analyse faut-il mener ?

**Correction :** segmenter le KPI par zone, cellule source/cible, bande, terminal, direction de mobilité et service. Étudier les causes d'échec, le temps d'interruption et la qualité après handover. La moyenne nationale peut masquer un problème local.

## Exercice 7 — Sécurité

**Question :** le réseau SBA est privé et non exposé à Internet. Est-il inutile d'authentifier et d'autoriser les interactions de service ?

**Correction :** non. Les réseaux internes peuvent être compromis ou mal configurés. Les fonctions et API doivent appliquer les protections, identités, autorisations, mises à jour et mécanismes de journalisation adaptés au modèle de confiance.

## Exercice 8 — Observabilité

**Question :** quel indicateur faut-il utiliser pour conclure à une expérience utilisateur satisfaisante : moyenne, P95 ou disponibilité d'une fonction ?

**Correction :** aucun indicateur ne suffit seul. Combine les indicateurs adaptés à l'objectif : percentiles de délai et de débit, pertes, réussite des procédures, disponibilité du service de bout en bout et segmentation par population et géographie.

# Glossaire

- **5GC / 5G Core** : cœur de réseau 5G.
- **5QI** : identifiant de caractéristiques de QoS d'un flux.
- **AMF** : Access and Mobility Management Function.
- **AUSF** : Authentication Server Function.
- **ARP** : Allocation and Retention Priority.
- **CA** : Carrier Aggregation, agrégation de porteuses.
- **CU / DU** : Central Unit / Distributed Unit du RAN.
- **DNN** : Data Network Name.
- **EPC** : Evolved Packet Core.
- **EPS fallback** : procédure pouvant faire utiliser LTE/EPS à un terminal 5G pour certains services, notamment la voix, selon le déploiement.
- **FR1 / FR2** : plages de fréquences définies pour NR.
- **GBR / GFBR / MFBR** : notions de débit garanti ou maximal selon les paramètres QoS applicables.
- **gNB** : nœud de base NG-RAN pour NR.
- **Handover** : transfert de la connexion radio vers une autre cellule ou un autre nœud selon la procédure.
- **IMS** : IP Multimedia Subsystem.
- **MEC** : Multi-access Edge Computing.
- **MIMO** : Multiple Input Multiple Output.
- **N2 / N3 / N6** : interfaces de référence du 5GS entre NG-RAN et AMF, NG-RAN et UPF, puis UPF et réseau de données.
- **NAS / NGAP / RRC** : protocoles de signalisation à différents niveaux de l'architecture.
- **NSSF** : Network Slice Selection Function.
- **NR** : New Radio, interface d'accès radio 5G.
- **O-RAN** : cadre d'architecture et de spécifications pour des réseaux d'accès radio ouverts et désagrégés.
- **PCF** : Policy Control Function.
- **PDU Session** : session de connectivité vers un réseau de données dans le 5GS.
- **QFI** : QoS Flow Identifier.
- **RSRP / RSRQ / SINR** : mesures de puissance, de qualité et de rapport signal/interférence-bruit.
- **SBA** : Service-Based Architecture.
- **SMF** : Session Management Function.
- **S-NSSAI** : identifiant de sélection d'une slice comprenant SST et, éventuellement, SD.
- **TDD** : Time Division Duplex.
- **UPF** : User Plane Function.
- **UDM / UDR** : Unified Data Management / Unified Data Repository.
- **VoLTE / VoNR** : voix IMS sur LTE / NR.

# Références techniques pour approfondir

Les spécifications évoluent par versions et releases. Pour une implémentation réelle, consulte la version prise en charge par le réseau et par le fournisseur, puis vérifie les profils de conformité et les procédures d'exploitation.

1. **3GPP TS 23.501 — System architecture for the 5G System (5GS)** : architecture et fonctions du 5GC. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3144
2. **3GPP TS 23.502 — Procedures for the 5G System (5GS)** : procédures d'accès, de session et de mobilité. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3145
3. **3GPP TS 23.503 — Policy and charging control framework for the 5G System** : cadre de politique et de contrôle. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3334
4. **3GPP TS 38.300 — NR and NG-RAN Overall description** : description générale NR/NG-RAN. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3191
5. **3GPP TS 38.401 — NG-RAN; Architecture description** : architecture NG-RAN. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3219
6. **3GPP TS 38.331 — NR; Radio Resource Control (RRC)** : procédures et éléments de configuration RRC. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3197
7. **3GPP TS 33.501 — Security architecture and procedures for 5G System** : architecture et procédures de sécurité. https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3169
8. **O-RAN Alliance — Specifications** : documents d'architecture et d'interfaces O-RAN. https://www.o-ran.org/specifications
9. **GSMA — 5G Standalone Networks** : contexte de déploiement de la 5G SA. https://www.gsma.com/solutions-and-impact/technologies/networks/5g-network-technologies-and-solutions/5g-standalone-networks/
10. **ETSI — Publications 3GPP** : versions publiées et transpositions européennes de nombreuses spécifications. https://www.etsi.org/standards

## Conclusion

Le niveau expert consiste à relier architecture, radio, mobilité, QoS, slicing, sécurité, transport et exploitation à des observations mesurables. Les décisions efficaces sont fondées sur des exigences explicites, des données corrélées, des hypothèses testables, un déploiement progressif et un retour arrière validé.

La suite logique est de réaliser des projets intégrateurs : campagne de mesures NR, diagnostic de mobilité sur un trajet réel, conception de slice entreprise, étude de placement UPF/MEC et mise en place d'un tableau de bord de service de bout en bout.
