# Réseaux mobiles 4G/5G — Intermédiaire

## Mise en contexte : de la couverture radio au service IP

Un abonné connecté en 4G ou en 5G ne communique pas uniquement avec une antenne. Son trafic traverse une chaîne composée d'un terminal, d'un réseau d'accès radio, d'un réseau de transport et d'un cœur mobile. Des fonctions d'authentification, de mobilité, de politique, de qualité de service et d'acheminement doivent coopérer pour que l'abonné puisse accéder à Internet ou à un service privé.

Au niveau débutant, tu as découvert les architectures LTE/EPC et 5G Core, la différence NSA/SA et les principaux équipements. Ce niveau intermédiaire approfondit le fonctionnement opérationnel : établissement des connexions, mobilité, QoS, mesures radio, découpage du réseau, voix sur IP et diagnostic d'incidents.

> **Encadré de mise en contexte** — Une icône « 5G » sur un téléphone ne garantit pas à elle seule un débit élevé, une latence faible ou une connexion au cœur 5G autonome. Le résultat dépend notamment de la bande de fréquences, de la largeur de bande, de la charge de la cellule, de la qualité radio, du déploiement NSA ou SA, du transport, du cœur mobile et de la politique appliquée à l'abonné.

## Objectifs pédagogiques

À la fin de ce cours, tu devras pouvoir :

- décrire les fonctions principales du réseau d'accès et du cœur mobile LTE et 5G ;
- reconstituer les grandes étapes d'un enregistrement LTE ou 5G et d'une session de données ;
- différencier les plans de contrôle et utilisateur, ainsi que les interfaces majeures ;
- expliquer NSA, SA, double connectivité, agrégation de porteuses et mobilité inter-RAT ;
- interpréter les indicateurs radio RSRP, RSRQ, SINR, CQI et MCS avec prudence ;
- comparer les mécanismes QoS LTE et 5G ;
- expliquer les bases du slicing, de VoLTE, de VoNR et de l'IMS ;
- organiser un diagnostic selon les couches radio, transport, cœur, politique et service ;
- appliquer une démarche de dépannage à des scénarios d'exploitation réalistes.

## Parcours pratique du niveau intermédiaire

1. Reconstituer les architectures LTE et 5G et les chemins du trafic.
2. Étudier un établissement de session et une panne d'accès aux données.
3. Lire des indicateurs radio et distinguer un problème de couverture d'un problème de capacité.
4. Examiner QoS, mobilité et voix.
5. Résoudre les travaux pratiques et le défi final à partir de symptômes, de compteurs et de traces fictives.

## Prérequis et conventions

Les notions suivantes sont supposées connues : IPv4/IPv6, CIDR, VLAN, routage IP, TCP/UDP, antenne, cellule, eNB, gNB, EPC et 5GC.

Les adresses, abonnés, identifiants, mesures et extraits de traces qui suivent sont fictifs et servent uniquement à l'apprentissage. Les valeurs radio sont indicatives : les seuils opérationnels dépendent de la bande, de la technologie, du terminal, du constructeur, de la configuration et de la méthode de mesure. Les exemples de commandes opérateur sont génériques ; les commandes exactes varient selon le fournisseur et la version logicielle.

# 1. Architecture LTE/EPC : approfondissement

## 1.1 Les blocs principaux

En LTE, le réseau d'accès radio s'appelle E-UTRAN et le cœur de paquet s'appelle EPC (*Evolved Packet Core*).

```text
                          PLAN DE CONTRÔLE
                  +--------------------------------+
                  | MME                            |
                  | mobilité, signalisation, NAS   |
                  +---------------+----------------+
                                  |
                 S1-MME           | S11
UE == radio == eNodeB             +---------+---------+
                 |                          |         |
                 | S1-U                     v         |
                 +----------------------> S-GW        |
                                            |         |
                                            | S5/S8   v
                                            +------> P-GW ---- SGi ---- Internet
                                                       |
                                         HSS : données d'abonnement
                                         PCRF : politiques et règles QoS

                 PLAN UTILISATEUR : UE -> eNodeB -> S-GW -> P-GW -> réseau externe
```

Le schéma est simplifié. Les interfaces exactes et les fonctions mobilisées dépendent du scénario, notamment lors du roaming, de la mobilité et de l'utilisation de variantes d'architecture.

### 1.2 Fonctions EPC à connaître

**eNodeB (eNB)** — Station de base LTE. Elle assure la couche radio, l'ordonnancement des ressources, la gestion de nombreuses procédures radio et la signalisation vers le cœur.

**MME (*Mobility Management Entity*)** — Fonction du plan de contrôle. Elle traite notamment la signalisation NAS, la gestion de mobilité, une partie de la sécurité et la coordination de l'établissement des connexions. Le MME ne transporte pas directement les paquets IP de l'abonné.

**S-GW (*Serving Gateway*)** — Nœud du plan utilisateur qui achemine les paquets entre le réseau d'accès et le reste de l'EPC. Il peut également servir de point d'ancrage pour le plan utilisateur pendant certaines procédures de mobilité.

**P-GW (*PDN Gateway*)** — Fournit la connectivité vers un réseau de données externe, applique certaines fonctions d'acheminement et participe à l'allocation et à la gestion de l'adresse IP de l'abonné. Les fonctions exactes de politique et de taxation dépendent de l'architecture.

**HSS (*Home Subscriber Server*)** — Base de données contenant les informations d'abonnement et les données nécessaires aux fonctions d'authentification.

**PCRF (*Policy and Charging Rules Function*)** — Fonction de contrôle de politique et de taxation dans l'architecture EPC classique. Elle peut contribuer à définir le traitement QoS des flux.

### 1.3 Interfaces LTE importantes

| Interface | Extrémités typiques | Rôle principal |
|---|---|---|
| Uu | UE – eNB | Interface radio LTE |
| S1-MME | eNB – MME | Signalisation du plan de contrôle |
| S1-U | eNB – S-GW | Transport utilisateur, typiquement GTP-U |
| S11 | MME – S-GW | Signalisation de contrôle des tunnels de service |
| S5/S8 | S-GW – P-GW | Contrôle et transport utilisateur entre passerelles ; S8 est associé au roaming inter-PLMN dans les architectures classiques |
| SGi | P-GW – réseau IP externe | Connectivité vers Internet ou un réseau de données privé |
| S6a | MME – HSS | Échanges liés à l'abonnement et à l'authentification |
| Gx | PCRF – P-GW/PCEF | Contrôle des politiques, selon l'architecture |

### 1.4 Plan de contrôle et plan utilisateur

Le **plan de contrôle** transmet les messages qui organisent le service : authentification, gestion de mobilité, création ou modification d'une session, configuration QoS et établissement des tunnels.

Le **plan utilisateur** transporte les données effectives : navigation Web, vidéo, messagerie, voix sur IP et trafic applicatif.

```text
PLAN DE CONTRÔLE
UE -- NAS/RRC --> eNB -- S1-MME --> MME -- contrôle --> passerelles

PLAN UTILISATEUR
Application UE --> radio --> eNB == GTP-U == S-GW == S5/S8 == P-GW --> IP
```

Une session peut donc échouer alors que la radio fonctionne : l'authentification peut être refusée, le profil d'abonné peut manquer, la création du tunnel peut échouer ou le routage externe peut être incorrect.

## 1.5 Bearers LTE et QoS

Dans LTE, un *EPS bearer* représente un chemin logique auquel sont associés des paramètres de traitement du trafic. Les bearers permettent de différencier les flux qui ne doivent pas nécessairement recevoir le même traitement.

Un contexte de données LTE classique comprend notamment :

- un bearer par défaut qui fournit la connectivité générale associée à la connexion PDN ;
- éventuellement des bearers dédiés pour certains services ou besoins QoS.

Le **QCI (*QoS Class Identifier*)** référence des caractéristiques de traitement, notamment la priorité, le budget de délai de paquets et le taux d'erreur de paquets selon la classe normalisée ou configurée.

L'**ARP (*Allocation and Retention Priority*)** participe aux décisions d'admission et de préemption lorsqu'elles sont prises en charge et autorisées par les politiques. Il ne remplace pas le QCI et ne signifie pas que chaque paquet de cet abonné sera systématiquement prioritaire dans tous les contextes.

Le **GBR (*Guaranteed Bit Rate*)** concerne les bearers pour lesquels un débit garanti est défini selon les règles du service. Un bearer non-GBR ne bénéficie pas de cette même garantie de débit.

Le débit observé dépend toujours des ressources radio disponibles et des autres éléments de la chaîne. Une classe QoS n'est pas une promesse universelle de débit de bout en bout.

# 2. Architecture 5G : 5G Core et interfaces

## 2.1 Vue générale du 5GC

La 5G autonome (SA) s'appuie sur le 5G Core, conçu autour de fonctions réseau spécialisées et d'interfaces de services entre les fonctions du plan de contrôle.

```text
                        PLAN DE CONTRÔLE 5G CORE

 UE ==== NR ==== gNB ---- N2 ---- AMF -------- AUSF
                     |              |             |
                     |              +----------- UDM
                     |              |
                     |              +----------- SMF ---- PCF
                     |                            |
                     | N3                         | N4
                     v                            v
                    UPF ======================== UPF
                     |
                     +---- N6 ---- Internet / réseau d'entreprise

       NRF : découverte des fonctions réseau
       NSSF : sélection des tranches réseau, selon le scénario
       NEF : exposition contrôlée de capacités et d'informations
```

L'illustration met en évidence les fonctions, mais toutes les fonctions ne dialoguent pas entre elles dans chaque procédure. Les relations, interfaces et messages sont définis par les spécifications 3GPP.

## 2.2 Fonctions du 5G Core

**gNB** — Station de base 5G NR. Elle gère le réseau d'accès radio et communique avec le cœur 5G via les interfaces prévues par l'architecture.

**AMF (*Access and Mobility Management Function*)** — Gère notamment l'enregistrement de l'UE, la signalisation NAS, les aspects de mobilité et la coordination de certaines procédures d'accès.

**SMF (*Session Management Function*)** — Gère l'établissement et la modification des sessions PDU, sélectionne et contrôle les fonctions du plan utilisateur et participe à la gestion des règles de session.

**UPF (*User Plane Function*)** — Transporte le trafic utilisateur. Il applique notamment des règles de traitement des paquets et assure la connectivité vers les réseaux de données. Plusieurs UPF peuvent exister selon la topologie.

**UDM (*Unified Data Management*)** — Fonction de gestion des données d'abonnement et des données nécessaires à plusieurs procédures du cœur.

**AUSF (*Authentication Server Function*)** — Participe aux procédures d'authentification.

**PCF (*Policy Control Function*)** — Fournit les règles de politique applicables aux sessions et services selon le contexte.

**NRF (*Network Repository Function*)** — Permet aux fonctions réseau de publier et de découvrir les fonctions disponibles selon le mécanisme de découverte défini.

**NSSF (*Network Slice Selection Function*)** — Contribue à la sélection des tranches réseau adaptées au contexte et aux informations d'abonnement.

**NEF (*Network Exposure Function*)** — Offre des mécanismes contrôlés d'exposition de capacités du réseau vers des applications ou fonctions autorisées.

La présence et le déploiement de certaines fonctions varient selon les services, l'architecture et les capacités implémentées.

## 2.3 Interfaces 5G à retenir

| Interface | Extrémités typiques | Fonction générale |
|---|---|---|
| Uu | UE – gNB | Interface radio NR |
| N1 | UE – AMF, via la signalisation d'accès | Messages NAS entre UE et cœur |
| N2 | gNB – AMF | Signalisation du plan de contrôle |
| N3 | gNB – UPF | Transport du plan utilisateur, généralement avec GTP-U |
| N4 | SMF – UPF | Contrôle du plan utilisateur et installation des règles |
| N6 | UPF – réseau de données | Connectivité vers Internet, entreprise ou service |
| N9 | UPF – UPF | Transport utilisateur entre UPF, selon la topologie |
| N11 | AMF – SMF | Coordination entre gestion d'accès/mobilité et gestion de session |

### 2.4 Architecture à services

Le cœur 5G met l'accent sur une architecture à services (*Service-Based Architecture*, SBA) pour de nombreuses interactions de contrôle. Les fonctions peuvent exposer et consommer des services via des interfaces définies par les spécifications. Les interfaces de service utilisent notamment HTTP/2 et des mécanismes de sécurité adaptés à l'architecture.

Cela ne signifie pas que tout le trafic du réseau mobile est transporté sous forme d'API HTTP. Le plan utilisateur continue d'utiliser des mécanismes de transport adaptés, par exemple GTP-U entre les points d'extrémité concernés.

## 2.5 Session PDU et connectivité IP

En 5G, une **session PDU** représente une association permettant à l'UE d'échanger des données avec un réseau de données. Elle peut fournir une connectivité IPv4, IPv6, IPv4v6, Ethernet ou d'autres types pris en charge par l'architecture.

Le **DNN (*Data Network Name*)** identifie le réseau de données auquel l'UE demande à se connecter. Il joue un rôle analogue, sans être strictement identique dans tous les aspects, à celui de l'APN dans LTE.

Exemples de DNN fictifs :

```text
internet
entreprise
ims
```

La disponibilité d'un DNN dépend de la configuration réseau et du profil d'abonnement.

# 3. Enregistrement et établissement de données

## 3.1 Séparer les étapes

Il est important de distinguer plusieurs états qui sont parfois confondus pendant un dépannage :

1. Le terminal détecte et sélectionne un réseau mobile.
2. Il effectue l'accès radio et échange de la signalisation.
3. Il s'enregistre auprès du réseau et est authentifié selon les procédures applicables.
4. Une session de données est établie.
5. Le plan utilisateur est configuré et l'accès au réseau de données est disponible.
6. Les paquets peuvent être acheminés au-delà du réseau mobile.

L'enregistrement réussi n'implique donc pas automatiquement que toutes les connexions de données fonctionneront.

## 3.2 Vue simplifiée d'une connexion LTE

Le vocabulaire exact et les variantes de procédure dépendent du mode de fonctionnement. Dans un scénario LTE classique, le déroulement général comprend :

```text
UE          eNodeB         MME         HSS       S-GW / P-GW
 |              |            |           |              |
 |-- accès radio/connexion -->|           |              |
 |-- demande d'attachement -->|---------->|              |
 |              |            |-- auth./données ------->|
 |              |            |<-- résultat/données -----|
 |<------------- authentification et sécurité ----------|
 |              |            |-- création contexte ---->|
 |              |            |<-- paramètres/session ---|
 |<---------- acceptation et configuration -------------|
 |              |            |           |              |
 |================ trafic utilisateur =================>|
```

Ce diagramme est pédagogique, pas une capture détaillée de tous les messages NAS, RRC, S1AP et GTP. Les messages peuvent être combinés, omis ou ordonnés différemment selon le contexte.

Lorsqu'un problème survient, il faut identifier l'étape réellement atteinte : échec radio, rejet d'attachement, échec de sécurité, création de bearer ou perte de connectivité externe.

## 3.3 Vue simplifiée d'un enregistrement 5G SA

En 5G SA, le terminal effectue une procédure d'enregistrement avant de demander une session PDU selon les besoins.

```text
UE              gNB              AMF              AUSF / UDM
 |                |                |                    |
 |-- accès radio->|                |                    |
 |-- Registration Request -------> |                    |
 |                |-- NAS relay -->|                    |
 |                |                |-- authentification ->|
 |                |                |<-- données/résultat --|
 |<---------- sécurité et acceptation de l'enregistrement -|
 |                |                |                    |
 |-- PDU Session Establishment Request ------------------|
 |                |                |---- SMF ------------|
 |                |                |                    |
 |                |                |       UPF préparé par le SMF
 |<-------------- acceptation de session et paramètres --|
 |==================== trafic via gNB / UPF =============>|
```

Le schéma omet certains échanges entre AMF, SMF, PCF, UPF et autres fonctions. Il ne doit pas être interprété comme une chronologie exhaustive.

### Point opérationnel

Si un terminal est enregistré en 5G SA mais n'accède pas à Internet, il faut examiner au minimum :

- le DNN demandé et autorisé ;
- le profil et les droits de l'abonné ;
- l'établissement de la session PDU ;
- la sélection de l'UPF et les règles de transfert ;
- l'adressage IP et les routes ;
- le pare-feu, le NAT si utilisé et la connectivité du réseau de données.

# 4. NSA, SA et options de déploiement

## 4.1 5G NSA

NSA signifie *Non-Standalone*. Dans un déploiement 5G NSA fréquent, la LTE et l'EPC restent au centre de l'architecture d'ancrage, tandis que la NR vient compléter les ressources radio LTE, par exemple avec la double connectivité LTE-NR.

```text
                  EPC (cœur LTE)
                       |
                      eNB ------------- gNB NR
                       |                  |
                       +---- UE ----------+

       Exemple de déploiement NSA de type EN-DC
```

Cette architecture permet à un opérateur de déployer la NR sans devoir immédiatement migrer l'ensemble de son cœur vers le 5GC. Les capacités et options exactes dépendent du scénario 3GPP utilisé.

## 4.2 5G SA

SA signifie *Standalone*. Dans une architecture 5G SA, le gNB est connecté au 5G Core. Les fonctions du cœur permettent notamment de gérer les sessions PDU, les QoS flows et les mécanismes propres au système 5G.

```text
UE ===== NR ===== gNB ===== N2/N3 ===== 5G Core
                                            |
                                      UPF ===== réseau IP
```

Le déploiement SA rend possibles des capacités du 5GC qui ne sont pas équivalentes à la simple présence d'une porteuse NR dans une architecture NSA. Le fait qu'un réseau soit SA ne garantit toutefois pas à lui seul une latence précise, une QoS particulière ou une tranche dédiée.

## 4.3 Comparaison

| Élément | NSA fréquent (EN-DC) | SA |
|---|---|---|
| Accès radio | LTE et NR en double connectivité | NR, selon les capacités du réseau |
| Ancrage principal | LTE/EPC dans l'architecture considérée | 5G Core |
| Cœur mobile | EPC | 5GC |
| Sessions | Modèle EPC/EPS dans l'architecture ancrée LTE | Sessions PDU et QoS flows 5G |
| Slicing 5GC natif | Non apporté par le seul ajout de NR à EPC | Capacités 5GC de slicing disponibles si configurées et déployées |
| Dépendances LTE | Importantes dans EN-DC | Pas nécessairement dans le plan d'accès 5G SA |

Le terme NSA recouvre plusieurs options de déploiement. Le tableau décrit une architecture NSA très répandue ; il ne prétend pas couvrir toutes les options 3GPP.

## 4.4 Double connectivité et agrégation de porteuses

Ces deux notions sont différentes.

**Agrégation de porteuses (*Carrier Aggregation*, CA)** : le terminal peut utiliser plusieurs porteuses radio associées pour augmenter la capacité disponible, sous réserve des capacités du terminal, du réseau et des conditions radio.

**Double connectivité (*Dual Connectivity*, DC)** : le terminal peut être connecté à deux nœuds d'accès, par exemple un nœud maître LTE et un nœud secondaire NR dans EN-DC.

Une architecture peut combiner ces mécanismes. Il ne faut pas conclure à partir de l'icône 5G affichée sur un smartphone que toutes les porteuses ou toutes les fonctionnalités possibles sont activées.

# 5. Radio : mesures, capacité et qualité de service perçue

## 5.1 Couverture et qualité ne sont pas synonymes

Une cellule peut être détectable tout en fournissant une expérience médiocre. La qualité d'un service dépend notamment du niveau du signal utile, des interférences, de la configuration de la cellule, de la charge et de la capacité de transport.

### Indicateurs LTE et NR

**RSRP (*Reference Signal Received Power*)** — Mesure de la puissance reçue des signaux de référence. C'est l'un des indicateurs de couverture utilisés en LTE ; des mesures de référence spécifiques existent aussi en NR.

**RSRQ (*Reference Signal Received Quality*)** — Mesure de qualité combinant la puissance reçue de référence et l'énergie reçue totale selon la définition applicable. Elle peut aider à comprendre une situation où la puissance seule ne suffit pas.

**SINR (*Signal-to-Interference-plus-Noise Ratio*)** — Rapport entre le signal utile et la somme des interférences et du bruit. Un SINR plus élevé permet généralement l'utilisation de schémas radio plus efficaces, si les autres conditions sont favorables.

**CQI (*Channel Quality Indicator*)** — Retour de qualité du canal transmis par le terminal selon les règles radio. Le réseau peut s'en servir pour adapter le traitement radio.

**MCS (*Modulation and Coding Scheme*)** — Combinaison de modulation et de codage utilisée pour transmettre les données. Un MCS plus efficace peut transporter davantage de bits par ressource, mais il nécessite des conditions radio appropriées.

**PRB (*Physical Resource Block*)** — Unité de ressources radio utilisée par l'ordonnanceur, définie selon la technologie et la numérologie. La capacité disponible dépend notamment de la bande passante, de la configuration et des autres utilisateurs.

### 5.2 Interpréter les mesures avec prudence

Les plages ci-dessous sont des repères pédagogiques approximatifs pour le RSRP en LTE, et non des seuils universels d'acceptation ou de déclenchement de handover.

| RSRP approximatif | Lecture pédagogique possible |
|---:|---|
| supérieur à -80 dBm | Signal fort dans de nombreuses situations |
| de -80 à -95 dBm | Signal souvent bon |
| de -95 à -105 dBm | Signal moyen selon l'environnement |
| de -105 à -115 dBm | Signal faible, marge réduite possible |
| inférieur à -115 dBm | Signal très faible dans de nombreuses situations |

Un seul indicateur ne suffit pas. Un signal de -85 dBm avec un SINR très faible peut être moins performant qu'un signal plus faible mais nettement moins perturbé.

Les seuils et la comparaison de mesures en NR doivent également tenir compte de la bande, du type de signal mesuré et de la méthode de mesure utilisée.

## 5.3 Couverture, capacité ou transport : comment distinguer les pannes ?

**Hypothèse A : mauvaise couverture.** Le signal est faible, les déconnexions se multiplient en bordure de cellule et les performances peuvent s'améliorer près du site radio.

**Hypothèse B : interférences.** Le niveau radio peut sembler raisonnable, mais le SINR ou le RSRQ est mauvais. Les débits fluctuent et les retransmissions peuvent augmenter.

**Hypothèse C : cellule congestionnée.** Le niveau radio est correct, mais de nombreux utilisateurs partagent des ressources limitées. Les débits chutent surtout aux heures chargées.

**Hypothèse D : problème de transport ou de cœur.** Les indicateurs radio sont bons, mais la latence, la perte de paquets ou l'accès à certains réseaux sont dégradés. Il faut examiner le backhaul, le routage, les UPF ou passerelles, ainsi que les services externes.

## 5.4 FDD, TDD et bandes de fréquences

En **FDD (*Frequency Division Duplex*)**, les transmissions montantes et descendantes utilisent des bandes de fréquences séparées.

En **TDD (*Time Division Duplex*)**, les transmissions montantes et descendantes partagent une même bande, mais utilisent des ressources temporelles différentes selon une configuration définie.

Le choix entre FDD et TDD influence notamment la capacité montante et descendante, la synchronisation entre cellules et les possibilités de planification radio.

Les bandes basses offrent généralement une meilleure propagation et une couverture plus étendue, alors que des bandes plus élevées peuvent fournir davantage de bande passante mais présenter une portée plus limitée, à puissance et environnement comparables. Ces tendances ne dispensent pas d'une analyse radio réelle.

## 5.5 Handover et reselection

La **reselection de cellule** concerne principalement le choix de cellule par un terminal en mode veille ou inactif, selon les règles applicables.

Le **handover** transfère une connexion active vers une autre cellule ou un autre nœud d'accès. Dans un cas LTE classique, le réseau peut préparer la cellule cible et coordonner le transfert de la connexion.

```text
Cellule A                         Cellule B
   |                                  |
   |<------ terminal en mobilité ---->|
   |                                  |
   |-- mesures et décision réseau ----|
   |                                  |
   +---- préparation du handover ---->|
   |                                  |
   |       transfert de connexion    |
   |                                  |
   |              UE attaché à B      |
```

Un handover raté peut provenir de mesures erronées, d'une mauvaise couverture de la cellule cible, d'un problème de signalisation, de ressources insuffisantes, d'un transport défaillant ou d'une incompatibilité de configuration.

La mobilité inter-RAT, par exemple entre LTE et NR, implique des procédures et des conditions spécifiques selon l'architecture et les capacités déployées.

# 6. QoS : bearer LTE et QoS flow 5G

## 6.1 Pourquoi différencier les flux ?

Un utilisateur peut simultanément naviguer sur Internet, passer un appel, écouter de la musique et utiliser une application professionnelle. Ces services ne sont pas nécessairement sensibles aux mêmes paramètres.

La QoS permet au réseau de classer et de traiter les flux selon des règles. Elle peut prendre en compte la priorité, le débit, le délai, les pertes et les règles d'admission, sous réserve de la politique et des ressources réellement disponibles.

La QoS radio est une composante d'une chaîne plus large. Une bonne configuration au niveau radio ne garantit pas la même performance à travers un transport saturé ou un serveur distant lent.

## 6.2 QoS en LTE

Les notions principales sont :

- **EPS bearer** : chemin logique auquel une classe et des paramètres QoS sont associés ;
- **QCI** : référence à des caractéristiques de traitement ;
- **ARP** : priorité liée à l'allocation et à la rétention des ressources ;
- **GBR / non-GBR** : distinction entre des bearers avec débit garanti et des bearers sans cette garantie ;
- **AMBR** : limite de débit agrégée applicable à des groupes de connexions selon le contexte LTE.

Le nombre de bearers et leur traitement dépendent du service et de l'architecture. Il ne faut pas supposer que chaque application correspond systématiquement à un bearer distinct.

## 6.3 QoS en 5G

Le modèle de QoS 5G repose sur les **QoS flows** à l'intérieur d'une session PDU.

Principaux éléments :

**QFI (*QoS Flow Identifier*)** — Identifie un QoS flow dans une session PDU.

**5QI (*5G QoS Identifier*)** — Référence des caractéristiques de traitement QoS, notamment la priorité, le budget de délai et les caractéristiques de pertes selon la définition applicable.

**GBR / non-GBR** — Les QoS flows peuvent être de type GBR ou non-GBR selon leur profil.

**GFBR (*Guaranteed Flow Bit Rate*)** — Débit garanti associé à un QoS flow GBR dans les directions concernées.

**MFBR (*Maximum Flow Bit Rate*)** — Débit maximal défini pour le QoS flow selon le profil.

**ARP** — Paramètre relatif à l'allocation et à la rétention de ressources dans les contextes où il s'applique.

**AMBR** — Paramètre de débit agrégé, utilisé selon le contexte d'abonnement ou de session.

Le SMF gère les aspects de session et coordonne la mise en œuvre des règles du plan utilisateur. Le gNB applique les mécanismes radio pertinents et l'UPF traite les paquets selon les règles installées.

## 6.4 Comparaison de concepts

| LTE/EPC | 5G Core | Attention |
|---|---|---|
| PDN connection | PDU session | Concepts proches dans leur rôle général, mais pas identiques |
| EPS bearer | QoS flow | Modèles de QoS différents ; ne pas les assimiler strictement |
| QCI | 5QI | Identifiants de caractéristiques QoS propres à chaque système |
| APN | DNN | Identifie la connectivité vers un réseau de données selon l'architecture |
| MME | AMF pour l'accès/mobilité, avec d'autres fonctions 5GC | La séparation fonctionnelle 5G est différente |
| S-GW/P-GW | UPF et SMF, entre autres fonctions 5GC | La correspondance n'est pas terme à terme |

## 6.5 Exemple pédagogique

Un opérateur gère trois catégories de trafic :

1. Navigation Internet classique.
2. Voix sur IP avec exigences de délai et de pertes plus sensibles.
3. Vidéo avec un débit élevé et un profil adapté au service.

L'opérateur peut utiliser des règles de politique et de QoS pour différencier le traitement de ces flux. Cela ne signifie pas qu'une classe donnée évitera systématiquement la congestion, ni qu'une application pourra exiger une priorité sans autorisation du réseau.

# 7. Network slicing et services différenciés

## 7.1 Notion de tranche réseau

Le *network slicing* permet de fournir des réseaux logiques adaptés à des besoins distincts au sein d'une infrastructure mobile commune. Une tranche peut s'appuyer sur des ressources, fonctions et politiques configurées pour un service ou un groupe de clients.

Exemples de catégories de besoins :

- large bande mobile ;
- communications industrielles nécessitant des caractéristiques contrôlées ;
- objets connectés en grand nombre ;
- réseaux privés ou services professionnels spécialisés.

Ces catégories décrivent des objectifs possibles, et non des garanties automatiquement fournies par la simple création d'une tranche.

## 7.2 S-NSSAI

En 5G, un *Single Network Slice Selection Assistance Information* (S-NSSAI) identifie une tranche de réseau.

Il est généralement composé de :

- **SST (*Slice/Service Type*)** : type de service associé à la tranche ;
- **SD (*Slice Differentiator*)** : valeur facultative permettant de différencier plusieurs tranches partageant un même SST.

La sélection réelle dépend de plusieurs éléments, notamment les informations d'abonnement, les tranches prises en charge, la demande de l'UE et les politiques du réseau.

## 7.3 Un slice n'est pas nécessairement une infrastructure physique isolée

Deux tranches peuvent partager une partie de l'infrastructure tout en bénéficiant de politiques et de fonctions distinctes. Selon le déploiement, l'isolation, les ressources réservées et les mécanismes de sécurité peuvent varier.

Pour analyser un service annoncé comme « dédié », il convient de vérifier ce qui est réellement isolé ou garanti : cœur, UPF, ressources radio, transport, politiques d'admission, supervision et accords de service.

# 8. VoLTE, VoNR et IMS

## 8.1 L'IMS, en quelques mots

L'*IP Multimedia Subsystem* (IMS) est une architecture de services permettant notamment de fournir la voix et des services multimédias sur IP. Il comprend des fonctions de contrôle de session et s'intègre aux mécanismes d'authentification, de politique et de transport du réseau mobile.

La voix mobile n'est pas simplement un flux audio envoyé vers Internet. Pour fournir un service téléphonique, il faut aussi gérer l'enregistrement de service, l'établissement des appels, la signalisation, la QoS pertinente et l'interconnexion avec d'autres réseaux.

## 8.2 VoLTE

VoLTE (*Voice over LTE*) fournit des services de voix sur le réseau LTE, généralement avec une intégration IMS. L'opérateur doit disposer d'un déploiement et d'un profil compatibles, et le terminal doit être autorisé et configuré.

Des problèmes VoLTE peuvent venir du profil d'abonnement, de l'enregistrement IMS, de la connectivité vers les fonctions IMS, des politiques QoS ou de la mobilité.

## 8.3 VoNR

VoNR (*Voice over New Radio*) permet la voix sur un accès NR en architecture 5G SA, avec une intégration aux fonctions IMS et au 5G Core selon le déploiement.

Le soutien de VoNR ne doit pas être déduit de la seule présence de 5G SA : les fonctions, le terminal, la couverture et les politiques doivent aussi être pris en charge.

## 8.4 Voix et mobilité

Si un réseau ne prend pas en charge la continuité de voix dans toutes les situations radio, un mécanisme de mobilité vers une technologie compatible peut être nécessaire. Les mécanismes possibles dépendent de l'architecture, des capacités du terminal et du réseau.

Lors du diagnostic d'un appel qui coupe pendant un déplacement, ne pas se limiter au signal radio. Vérifier aussi les événements de handover, les transitions LTE/NR, l'enregistrement IMS et les compteurs de succès/échec associés.

# 9. Transport, synchronisation et performance

## 9.1 Le réseau de transport mobile

Le transport relie les sites radio au cœur et interconnecte les fonctions réseau. Il peut inclure des liaisons Ethernet, de la fibre, des faisceaux hertziens et des réseaux IP/MPLS.

Un transport mal dimensionné ou mal configuré peut provoquer :

- de la congestion et des pertes ;
- une latence excessive ;
- une gigue nuisible à certains services temps réel ;
- la perte de connectivité entre une station et le cœur ;
- des problèmes de qualité liés à la synchronisation lorsque les exigences radio ne sont pas satisfaites.

## 9.2 Synchronisation

Les réseaux mobiles utilisent des mécanismes de synchronisation de fréquence et de temps selon la technologie et le déploiement. PTP, SyncE et le GNSS peuvent être employés dans certaines architectures.

Les exigences exactes varient avec la bande, le mode duplex, les fonctionnalités radio et la topologie. Un incident de synchronisation doit être analysé à partir des alarmes et mesures du matériel concerné, plutôt que d'appliquer un seuil générique sans contexte.

## 9.3 Latence de bout en bout

La latence perçue peut s'écrire de manière simplifiée :

```text
Latence totale = accès radio
               + transport vers le cœur
               + traitement du cœur
               + transport externe
               + traitement du serveur
               + éventuels retours et retransmissions
```

La formule est conceptuelle : les délais ne sont pas toujours strictement séparables et certains traitements peuvent se dérouler en parallèle.

Le choix d'un UPF plus proche de l'utilisateur peut réduire une partie du transport dans certains déploiements, mais il ne supprime ni les délais radio ni ceux de la destination distante.

# 10. Sécurité et protection du réseau mobile

## 10.1 Identité et authentification

Les réseaux mobiles utilisent des mécanismes d'authentification basés sur les données d'abonnement et des procédures cryptographiques normalisées. Le fonctionnement précis diffère entre EPS/LTE et 5G.

En 5G, le SUPI (*Subscription Permanent Identifier*) est l'identifiant permanent d'abonné au niveau du système. Le SUCI (*Subscription Concealed Identifier*) est une représentation protégée utilisée dans les contextes applicables afin de limiter l'exposition de l'identité permanente sur l'interface radio. La confidentialité effectivement obtenue dépend de la configuration et des mécanismes pris en charge.

Un opérateur doit protéger les données d'abonnement, sécuriser les interfaces, appliquer les contrôles d'accès et surveiller les anomalies d'enregistrement et d'authentification.

## 10.2 Sécurité des interfaces et du plan utilisateur

La présence de tunnels de transport comme GTP-U ne signifie pas que tout paquet est automatiquement protégé contre toute menace. La protection dépend notamment du réseau de transport, de la segmentation, des contrôles d'accès, des mécanismes cryptographiques éventuels, de la configuration et du modèle de menace.

Mesures à considérer :

- limiter l'accès aux interfaces de gestion et de contrôle ;
- filtrer les échanges entre segments et fonctions ;
- superviser les tunnels, les sessions et les anomalies ;
- maintenir les équipements et logiciels selon les procédures opérateur ;
- contrôler les changements de configuration ;
- protéger les identifiants et secrets d'abonnement ;
- valider les configurations de peering, de routage et de transport.

## 10.3 Risques de configuration

Une erreur de DNN/APN, une politique trop restrictive, une route manquante ou des règles de pare-feu incorrectes peuvent interrompre un service sans qu'il y ait de panne radio.

De même, une configuration de QoS ne doit pas être utilisée comme substitut à la sécurité : une priorité élevée ne rend pas un flux fiable ou autorisé par elle-même.

# 11. Démarche de diagnostic opérationnel

## 11.1 Toujours isoler le domaine en panne

Une méthode efficace consiste à progresser du terminal vers le réseau externe sans présumer de la cause.

```text
1. Terminal et SIM/eSIM
       |
       v
2. Couverture et accès radio
       |
       v
3. Enregistrement et authentification
       |
       v
4. Session de données / bearer
       |
       v
5. Tunnel et plan utilisateur
       |
       v
6. IP, routage, DNS et filtrage
       |
       v
7. Application et serveur distant
```

Ce parcours n'impose pas de toujours effectuer les étapes dans cet ordre. Les alarmes et les faits déjà établis peuvent permettre de cibler directement le bon domaine. Il sert surtout à éviter des modifications au hasard.

## 11.2 Questions de départ

1. Le problème touche-t-il un seul abonné, plusieurs abonnés, une cellule, un site ou une région ?
2. Est-il permanent ou intermittent ?
3. Affecte-t-il la voix, les données, le SMS, la mobilité ou tous les services ?
4. Se produit-il sur LTE, NR NSA, NR SA ou plusieurs modes ?
5. A-t-il commencé après un changement de configuration, une panne ou une hausse de charge ?
6. Les indicateurs radio sont-ils dégradés ?
7. L'enregistrement est-il réussi ? La session de données est-elle active ?
8. L'adresse IP, la route, le DNS et le chemin jusqu'à la destination sont-ils corrects ?

## 11.3 Outils génériques côté terminal ou serveur Linux

Les outils ci-dessous servent à diagnostiquer la connectivité IP lorsqu'un environnement de laboratoire ou un équipement de test permet d'y accéder. Ils ne remplacent pas les outils spécialisés de supervision RAN et cœur mobile.

Afficher les interfaces et adresses :

```bash
ip address show
```

Examiner les routes :

```bash
ip route show
ip -6 route show
```

Tester la connectivité IP :

```bash
ping -c 4 192.0.2.1
```

Tester la résolution DNS :

```bash
getent hosts example.com
```

Examiner le chemin vers une destination lorsque l'outil est installé et que les paquets sont autorisés :

```bash
traceroute 192.0.2.1
```

Observer le trafic sur une interface, avec les privilèges nécessaires :

```bash
sudo tcpdump -ni any 'icmp or port 53'
```

Les réseaux mobiles peuvent filtrer certains messages ICMP ou masquer des sauts intermédiaires. Un `ping` ou un `traceroute` en échec ne prouve donc pas toujours une panne générale du service.

## 11.4 Vérifications côté cœur mobile

Dans un environnement opérateur, les vérifications sont généralement réalisées par les outils de gestion, les compteurs, les traces de signalisation et les journaux des équipements. Selon la plateforme, il faut examiner :

- les taux de succès d'enregistrement et d'authentification ;
- les rejets de création de session ou de bearer ;
- la configuration de l'abonnement, de l'APN/DNN et des politiques ;
- la présence des tunnels et la cohérence de leurs extrémités ;
- les erreurs de transport et la perte de paquets ;
- les statistiques de l'UPF ou des passerelles EPC ;
- les routes vers les réseaux externes ;
- les compteurs de QoS, de congestion et de mobilité.

Les commandes propriétaires ne sont pas interchangeables entre fournisseurs. Il faut consulter la documentation correspondant au matériel, au logiciel et à la version réellement déployés.

# 12. Travaux pratiques

## TP 1 — Reconstituer une architecture LTE et 5G

### Objectif

Distinguer les fonctions qui gèrent l'accès, la mobilité, les sessions et le transport des données.

### Situation

Un terminal est connecté au réseau mobile. L'enregistrement est réussi mais la navigation Web échoue.

### Travail demandé

1. Dessine le chemin de signalisation d'une connexion LTE classique.
2. Dessine le chemin du trafic utilisateur en LTE.
3. Dessine le chemin du plan utilisateur en 5G SA.
4. Identifie les fonctions à examiner si la session existe mais qu'aucun paquet n'atteint Internet.

### Correction

En LTE, le MME gère la signalisation de mobilité et participe à la mise en place du contexte de données. Le trafic passe typiquement de l'eNB au S-GW puis au P-GW et au réseau externe. En 5G SA, le contrôle d'accès mobilise l'AMF ; la gestion de session passe notamment par le SMF, et le trafic utilisateur traverse le gNB puis l'UPF vers le réseau de données.

Si la session est établie mais la navigation échoue, les contrôles doivent inclure l'adresse IP, les règles de transfert de l'UPF ou des passerelles, les routes externes, le filtrage, le NAT s'il est utilisé et le DNS.

## TP 2 — Analyser des indicateurs radio

### Objectif

Distinguer un problème de couverture, d'interférences et de capacité.

### Données fictives

| Cas | RSRP | SINR | Charge cellule | Symptôme |
|---|---:|---:|---:|---|
| A | -118 dBm | 2 dB | 20 % | Déconnexions en bordure de zone |
| B | -88 dBm | -1 dB | 35 % | Débit très variable, retransmissions |
| C | -86 dBm | 18 dB | 95 % | Débit faible le soir, meilleur la nuit |
| D | -83 dBm | 17 dB | 30 % | Bon débit radio, accès à un serveur impossible |

### Travail demandé

Pour chaque cas, propose une hypothèse prioritaire et deux vérifications complémentaires.

### Correction

**Cas A : couverture probablement insuffisante.** Vérifier la couverture, les événements de mobilité, la cellule servante et les mesures autour du site. Le RSRP très faible est cohérent avec les déconnexions, mais il faut contrôler les conditions locales et les bandes utilisées.

**Cas B : interférences ou qualité radio dégradée.** Le RSRP est relativement élevé mais le SINR est très faible. Vérifier les interférences, les cellules voisines, les compteurs radio et les retransmissions. La charge doit également être examinée, même si elle n'est pas particulièrement élevée dans le tableau.

**Cas C : congestion probable.** Les indicateurs radio sont bons, mais la charge est très élevée et le problème varie avec l'heure. Vérifier l'utilisation des ressources radio, le nombre d'utilisateurs actifs, la capacité configurée et les compteurs de débit. Une hausse de charge n'est pas à elle seule une preuve, mais elle constitue une hypothèse cohérente.

**Cas D : domaine transport, cœur, routage ou serveur à examiner.** Les conditions radio et la charge indiquées semblent bonnes. Tester la connectivité IP par étapes, vérifier DNS, routes, filtrage et disponibilité du serveur. Les valeurs de radio ne garantissent pas la connectivité de bout en bout.

## TP 3 — Analyser un échec de session en 5G SA

### Situation fictive

Un abonné voit le réseau 5G SA et s'enregistre correctement. Le terminal affiche ensuite « pas d'accès Internet ».

Résultats des vérifications :

```text
Enregistrement 5G : réussi
Authentification : réussie
Demande de session PDU : rejetée
DNN demandé : entreprise
DNN autorisés dans le profil de test : internet
```

### Travail demandé

1. Quelle est l'hypothèse principale ?
2. Pourquoi ne faut-il pas commencer par modifier la radio ?
3. Quelles vérifications faut-il réaliser avant de relancer la session ?

### Correction

L'hypothèse principale est une incohérence entre le DNN demandé et les droits ou la configuration disponibles pour l'abonné. La radio et l'enregistrement fonctionnent, tandis que l'échec se produit à l'étape de session.

Il faut vérifier le DNN autorisé, le profil d'abonnement, les politiques, l'état des fonctions SMF/UPF et la cause précise du rejet. Si l'accès au DNN `entreprise` n'est pas autorisé, il faut appliquer la configuration approuvée et non contourner les contrôles. Le test doit ensuite être répété et le résultat documenté.

## TP 4 — Préparer une lecture d'incident de mobilité

### Situation fictive

Des utilisateurs perdent leur appel lors du passage d'une zone LTE à une zone NR. Le phénomène ne se produit pas lorsqu'ils restent immobiles.

### Travail demandé

Établir une liste de six vérifications pertinentes, sans conclure immédiatement à une panne radio.

### Correction attendue

Une démarche acceptable inclut :

1. comparer les événements d'appel coupé avec les événements de mobilité ;
2. contrôler les niveaux et la qualité radio de la cellule source et de la cellule cible ;
3. examiner les taux de succès et d'échec de handover ou de transition inter-RAT ;
4. vérifier les capacités du terminal et les modes LTE/NR pris en charge ;
5. contrôler la continuité du service IMS et les politiques de voix ;
6. comparer les résultats entre plusieurs terminaux, cellules et itinéraires.

Selon l'architecture, les mécanismes de continuité diffèrent. Il faut donc connaître le scénario NSA/SA et les procédures réellement déployées avant d'interpréter les traces.

# 13. Étude de cas intégrée

## 13.1 Scénario

Un opérateur déploie des cellules NR dans une ville. Les utilisateurs signalent trois problèmes :

- la navigation est lente dans un quartier commerçant en soirée ;
- certains abonnés SA s'enregistrent mais n'obtiennent pas de connectivité sur le DNN professionnel ;
- quelques appels se coupent lors des déplacements entre des zones LTE et NR.

Les premières mesures montrent :

- de bons niveaux RSRP dans le quartier commerçant ;
- une forte utilisation des ressources radio aux heures de pointe ;
- des rejets de session associés à certains profils DNN ;
- une corrélation entre les appels interrompus et des échecs de mobilité pour une partie des trajets.

## 13.2 Analyse attendue

Les trois problèmes peuvent relever de domaines différents. Il faut éviter de rechercher une cause unique avant d'avoir établi les faits.

**Problème 1 — Navigation lente.** La charge radio élevée est une hypothèse prioritaire. Vérifier les ressources radio, les compteurs d'ordonnancement, la configuration de bande passante et les performances du transport. Comparer les heures chargées et creuses avant de dimensionner la capacité.

**Problème 2 — DNN professionnel.** Les rejets de session orientent vers les droits de l'abonné, la configuration du DNN et les politiques de session. Examiner les causes de rejet, la sélection de SMF/UPF et le réseau de données associé. Ne pas assimiler un enregistrement réussi à une session professionnelle autorisée.

**Problème 3 — Appels interrompus.** La corrélation avec les échecs de mobilité conduit à examiner les mesures radio, la configuration des cellules voisines, les procédures inter-RAT, la compatibilité terminal et la continuité IMS. Il faut aussi confirmer si les pertes se produisent avant, pendant ou après le transfert.

## 13.3 Plan d'action professionnel

1. Établir une fenêtre temporelle et l'étendue de chaque incident.
2. Collecter les traces et compteurs associés aux abonnés et cellules de test en respectant les règles de protection des données.
3. Reproduire les symptômes dans un environnement maîtrisé lorsque c'est possible.
4. Définir une hypothèse par domaine avec des observations qui la confirmeraient ou l'infirmeraient.
5. Modifier une seule variable contrôlée à la fois, selon le processus de changement de l'opérateur.
6. Mesurer les résultats avant et après le changement.
7. Documenter la cause, la correction et le plan de retour arrière.

# 14. Exercices de consolidation corrigés

## Exercice 1 — Fonctions de cœur

**Question :** Quelle fonction est principalement responsable de la gestion de session en 5G SA : AMF, SMF ou UPF ?

**Correction :** Le SMF gère les aspects de session. L'AMF gère notamment l'enregistrement et la mobilité, tandis que l'UPF traite les paquets du plan utilisateur selon les règles configurées.

## Exercice 2 — NSA ou SA

**Question :** Un déploiement utilise LTE/EPC comme ancrage et ajoute une connectivité NR en double connectivité. À quel type de déploiement cela correspond-il typiquement ?

**Correction :** À un déploiement NSA de type EN-DC. Il faut néanmoins vérifier l'option d'architecture exacte avant d'appliquer ce terme à un réseau réel.

## Exercice 3 — Couverture et interférences

**Question :** Un utilisateur a un RSRP de -87 dBm et un SINR de -3 dB. Peut-on conclure que la couverture est bonne et qu'il n'existe aucun problème radio ?

**Correction :** Non. Le RSRP est relativement élevé, mais le SINR faible suggère une qualité radio dégradée. Il faut examiner les interférences, la configuration radio, les cellules voisines et les compteurs associés.

## Exercice 4 — Session et Internet

**Question :** L'enregistrement 5G est réussi, une session PDU est active et le terminal a une adresse IP. Quel domaine peut encore empêcher l'accès à une application ?

**Correction :** Plusieurs domaines restent possibles : règles UPF, route ou pare-feu, connectivité N6, NAT le cas échéant, DNS, serveur distant ou application. Il faut tester chaque étape plutôt que supposer que la session active garantit l'accès à tous les services.

## Exercice 5 — QoS

**Question :** Quelle différence générale existe entre 5QI et QFI ?

**Correction :** Le 5QI identifie des caractéristiques de traitement QoS. Le QFI identifie un QoS flow au sein d'une session PDU. Ils répondent à des besoins différents et ne sont pas interchangeables.

## Exercice 6 — Slicing

**Question :** Le fait qu'un service utilise un S-NSSAI prouve-t-il qu'il dispose d'une infrastructure physique totalement dédiée ?

**Correction :** Non. Une tranche est un réseau logique. L'isolation et les ressources réellement dédiées dépendent de l'architecture, du déploiement et des politiques.

## Exercice 7 — Handover

**Question :** Quelle est la différence entre reselection de cellule et handover ?

**Correction :** La reselection concerne principalement le choix de cellule en mode veille ou inactif. Le handover transfère une connexion active vers une autre cellule ou un autre nœud d'accès.

## Exercice 8 — Mauvais débit en heure de pointe

**Question :** Le RSRP et le SINR sont bons, mais le débit se dégrade systématiquement le soir. Quelle hypothèse vérifier en premier ?

**Correction :** La congestion est une hypothèse prioritaire. Il faut vérifier la charge et les ressources radio, tout en contrôlant le transport et le cœur pour exclure une saturation ailleurs.

# 15. Défi final — Diagnostiquer un incident multi-domaine

## 15.1 Contexte

Tu es technicien dans l'équipe d'exploitation d'un opérateur fictif. Trois clients transmettent des rapports distincts après une extension 5G.

**Client A :** le débit est mauvais de 18 h à 22 h dans une zone de forte affluence. Le signal indiqué est bon.

**Client B :** le terminal affiche 5G SA et indique « enregistré », mais les applications professionnelles ne fonctionnent pas. L'accès aux données publiques fonctionne.

**Client C :** les appels sont stables dans les zones LTE et NR, mais certains sont coupés à la frontière des deux zones.

### Données de diagnostic

| Élément observé | Client A | Client B | Client C |
|---|---|---|---|
| Enregistrement | Réussi | Réussi | Réussi avant l'appel |
| Radio | RSRP -86 dBm, SINR 17 dB | RSRP -91 dBm, SINR 13 dB | Variable près de la frontière |
| Charge radio locale | 96 % au pic | 42 % | 55 % |
| Service public IP | Fonctionne lentement | Fonctionne | Fonctionne hors transition |
| Service professionnel | Non testé | Échec | Sans objet |
| Mobilité | Sans anomalie rapportée | Sans objet | Échec corrélé à certains transferts LTE/NR |

## 15.2 Travail demandé

Pour chaque client :

1. Identifie le domaine probable de l'incident.
2. Cite deux preuves en faveur de l'hypothèse.
3. Propose trois vérifications supplémentaires.
4. Propose une action corrective possible, en précisant ce qui doit être confirmé avant de la déployer.
5. Donne un critère permettant de vérifier que la correction fonctionne.

## 15.3 Correction détaillée

### Client A — Dégradation du débit à l'heure de pointe

**Domaine probable :** capacité radio, avec vérification complémentaire du transport et du cœur.

**Éléments en faveur :** la charge locale atteint 96 % pendant la période de dégradation ; le RSRP et le SINR sont bons, ce qui rend une simple insuffisance de couverture moins probable.

**Vérifications :**

- examiner l'occupation des ressources radio et la distribution des utilisateurs actifs ;
- comparer le débit, les retransmissions et l'utilisation des ressources entre heures de pointe et heures creuses ;
- vérifier les compteurs de transport et du cœur pour s'assurer qu'une saturation simultanée ne contribue pas au problème.

**Action possible :** optimiser les paramètres radio ou augmenter la capacité si les mesures démontrent qu'elle est insuffisante. Toute modification doit tenir compte de la couverture, des cellules voisines et du spectre disponible.

**Critère de validation :** amélioration mesurable du débit et des percentiles de latence à l'heure de pointe, sans dégradation disproportionnée des cellules voisines.

### Client B — Accès public fonctionnel, services professionnels indisponibles

**Domaine probable :** DNN, profil d'abonnement, session, politiques ou réseau de données professionnel.

**Éléments en faveur :** l'enregistrement 5G est réussi et l'accès IP public fonctionne ; le problème est spécifique aux services professionnels.

**Vérifications :**

- confirmer le DNN demandé par l'application et celui autorisé dans le profil de l'abonné ;
- examiner la cause d'établissement ou de modification de session et les règles du SMF/UPF ;
- contrôler le routage, les ACL/pare-feu et les services DNS du réseau professionnel.

**Action possible :** corriger le profil, la politique ou la connectivité du DNN professionnel selon la cause démontrée. Ne pas supprimer les contrôles d'accès pour rétablir artificiellement le service.

**Critère de validation :** la session professionnelle est établie, les routes et politiques correspondent au profil prévu, et les tests d'accès autorisés réussissent sans ouvrir les destinations interdites.

### Client C — Appel coupé à la frontière LTE/NR

**Domaine probable :** mobilité inter-RAT et continuité du service voix, avec une possible contribution radio.

**Éléments en faveur :** les appels fonctionnent dans chaque zone prise séparément ; les échecs sont corrélés à certains transferts LTE/NR et le signal varie à la frontière.

**Vérifications :**

- analyser les événements et causes d'échec de handover sur les itinéraires affectés ;
- vérifier la couverture de la cellule cible, les relations de voisinage et les paramètres de mobilité ;
- examiner l'IMS, les capacités du terminal, la politique de voix et les mécanismes de continuité applicables à l'architecture.

**Action possible :** corriger les relations de voisinage ou paramètres de mobilité si les traces le justifient, ou ajuster le plan radio après une étude contrôlée. Vérifier également les exigences de continuité de voix pour la combinaison de technologies concernée.

**Critère de validation :** réduction durable du taux d'échec des transferts et des appels coupés sur un ensemble représentatif de trajets, de terminaux et de conditions radio.

## 15.4 Livrable professionnel attendu

Rédige un rapport d'incident contenant :

- la description du symptôme et son périmètre ;
- les données collectées et la fenêtre temporelle ;
- les hypothèses classées par priorité ;
- les contrôles réalisés et leurs résultats ;
- la cause racine, une fois démontrée ;
- la correction et son plan de retour arrière ;
- les indicateurs comparés avant et après ;
- les actions de prévention ou de supervision supplémentaires.

Une bonne analyse distingue explicitement les faits, les hypothèses et les conclusions. Elle ne déduit pas une cause racine à partir d'une seule mesure.

# 16. Synthèse à retenir

- Internet est un ensemble de réseaux indépendants. Les réseaux mobiles s'insèrent dans cette architecture grâce à des mécanismes de transport et de routage IP.
- LTE utilise E-UTRAN et EPC. La 5G SA utilise NR et le 5G Core.
- Le plan de contrôle gère la signalisation et les décisions ; le plan utilisateur transporte les données.
- En LTE, le MME, les passerelles EPC, le HSS et la politique QoS jouent des rôles distincts.
- En 5GC, l'AMF gère notamment l'accès et la mobilité, le SMF les sessions, et l'UPF le trafic utilisateur.
- NSA et SA décrivent des architectures différentes. La présence de NR ne prouve pas que le terminal utilise un cœur 5G SA.
- Un bon RSRP ne garantit ni un bon SINR, ni l'absence de congestion, ni une bonne connectivité de bout en bout.
- Les bearers LTE et les QoS flows 5G permettent de différencier le traitement des flux, mais ne suppriment pas les limitations de capacité.
- Le slicing est une capacité logique ; les garanties et l'isolation dépendent du déploiement réel.
- VoLTE et VoNR s'appuient sur des architectures et des fonctions de service qui vont au-delà du signal radio.
- Un enregistrement réussi n'implique pas automatiquement qu'une session de données ou une application fonctionne.
- Pour dépanner efficacement, il faut corréler les symptômes aux mesures radio, à la signalisation, aux sessions, au transport et au réseau de données.

# 17. Glossaire

| Terme | Définition |
|---|---|
| 5GC | Cœur de réseau 5G |
| 5QI | Identifiant de caractéristiques de QoS en 5G |
| AMF | Fonction 5G de gestion de l'accès et de la mobilité |
| AMBR | Débit maximal agrégé selon le contexte concerné |
| ARP | Priorité d'allocation et de rétention de ressources |
| CA | Agrégation de porteuses radio |
| CQI | Indicateur de qualité du canal radio transmis par l'UE |
| DNN | Nom du réseau de données demandé en 5G |
| eNB | Station de base LTE |
| EPC | Cœur de paquet LTE |
| eMBB | Catégorie de service 5G orientée large bande mobile améliorée |
| EPS bearer | Bearer de service dans l'architecture LTE/EPC |
| FDD | Duplexage en fréquence |
| GBR | Débit garanti selon le profil applicable |
| gNB | Station de base NR |
| HSS | Base de données d'abonnés dans LTE/EPC |
| IMS | Sous-système multimédia IP, utilisé notamment pour la voix |
| iRAT / inter-RAT | Mobilité entre technologies d'accès radio différentes |
| MCS | Schéma de modulation et de codage |
| MME | Fonction de gestion de mobilité du cœur LTE |
| MFBR | Débit maximal d'un QoS flow concerné |
| NAS | Signalisation entre terminal et cœur mobile |
| NEF | Fonction d'exposition contrôlée de capacités du 5GC |
| NSSF | Fonction de sélection des tranches réseau 5G |
| NR | New Radio, accès radio 5G |
| NRF | Fonction de découverte des fonctions du 5GC |
| NSA | Architecture 5G non autonome, selon l'option déployée |
| PCF | Fonction de contrôle des politiques 5G |
| PCRF | Fonction de contrôle des politiques dans l'EPC classique |
| PDU session | Session de connectivité de données en 5G |
| P-GW | Passerelle PDN du cœur LTE |
| PRB | Bloc de ressources physiques radio |
| QoS | Qualité de service |
| QoS flow | Flux logique QoS dans une session PDU 5G |
| QCI | Identifiant de classe QoS LTE |
| QFI | Identifiant d'un QoS flow 5G |
| RAN | Réseau d'accès radio |
| RSRP | Puissance reçue des signaux de référence |
| RSRQ | Mesure de qualité du signal de référence selon la définition radio applicable |
| SA | Architecture autonome 5G avec 5G Core |
| S-GW | Passerelle de desserte du cœur LTE |
| SINR | Rapport signal / interférences et bruit |
| SMF | Fonction de gestion de session en 5G |
| SST / SD | Type de tranche / différenciateur de tranche |
| SUPI / SUCI | Identifiants d'abonné permanents et représentation protégée utilisée en 5G |
| TDD | Duplexage temporel |
| UE | Équipement utilisateur |
| UDM | Fonction de gestion des données d'abonné 5G |
| UPF | Fonction du plan utilisateur 5G |
| VoLTE | Voix sur LTE |
| VoNR | Voix sur New Radio, dans un contexte 5G approprié |

# 18. Références techniques

Les spécifications normatives sont la référence pour les procédures exactes et les détails d'interopérabilité. Les versions à consulter doivent correspondre aux fonctionnalités et à la Release réellement déployées.

- 3GPP TS 23.401 — *General Packet Radio Service (GPRS) enhancements for E-UTRAN access* : https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=849
- 3GPP TS 23.501 — *System architecture for the 5G System (5GS)* : https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3144
- 3GPP TS 23.502 — *Procedures for the 5G System (5GS)* : https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3169
- 3GPP TS 23.503 — *Policy and charging control framework for the 5G System (5GS)* : https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3167
- ETSI — versions publiées des spécifications 3GPP, dont TS 23.501 : https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/
- Open5GS — documentation du projet de cœur mobile 4G/5G open source : https://open5gs.org/open5gs/docs/
- UERANSIM — simulateur UE et RAN 5G NR utilisé dans certains laboratoires : https://github.com/aligungr/UERANSIM

Les outils Open5GS et UERANSIM peuvent faciliter l'expérimentation en laboratoire, mais ils ne remplacent pas un réseau radio commercial complet. Leur installation et leurs configurations évoluent ; il faut suivre la documentation de la version utilisée.

## Fin du cours

Tu dois désormais pouvoir expliquer comment un terminal passe de la couverture radio à une session de données, pourquoi l'architecture NSA diffère de SA, comment la QoS est organisée et comment commencer le diagnostic d'un incident mobile multi-domaine.

La suite logique est le niveau expert : ingénierie radio et capacité, mobilité avancée, dimensionnement et performance, optimisation QoS, architecture cœur distribuée, slicing opérationnel, haute disponibilité et analyse approfondie de traces.
