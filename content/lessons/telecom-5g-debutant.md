## Encadré de mise en contexte

Un téléphone connecté en 4G ou en 5G ne communique pas seulement avec une antenne. Il s'appuie sur une chaîne de composants radio, de transport et de cœur de réseau qui authentifient l'abonné, gèrent sa mobilité, transportent ses données et le relient à Internet ou aux services de l'opérateur.

Ce cours explique cette chaîne depuis les fondamentaux. L'objectif n'est pas de mémoriser des sigles isolés, mais de comprendre comment une connexion mobile fonctionne, pourquoi les performances varient et comment diagnostiquer les problèmes les plus courants.

# Réseaux Mobiles (4G/5G) — Débutant

## 1. Objectifs pédagogiques

À la fin du cours, tu devras être capable de :

- distinguer les principales générations de réseaux mobiles et leurs objectifs ;
- décrire l'architecture générale d'un réseau mobile ;
- expliquer les rôles de l'UE, de la station de base et du cœur de réseau ;
- reconnaître les principales fonctions de l'architecture 4G LTE/EPC et 5G/5GC ;
- différencier la 5G NSA de la 5G SA ;
- comprendre les notions de cellule, bande de fréquences, largeur de bande, duplexage, MIMO et handover ;
- interpréter les indicateurs radio élémentaires ;
- comprendre les notions d'APN, de DNN, de bearer, de QoS et de réseau cœur ;
- réaliser des observations simples sur un téléphone et mesurer les performances d'une connexion ;
- analyser des incidents de couverture, de capacité et de connectivité ;
- expliquer les principaux enjeux de sécurité et d'évolution des réseaux mobiles.

## 2. Prérequis et matériel conseillé

Les bases de l'adressage IP, des sous-réseaux, du routage et de TCP/IP sont utiles. Aucun équipement radio professionnel n'est indispensable pour suivre ce cours.

Pour le parcours pratique, prévois si possible :

- un téléphone compatible 4G et/ou 5G avec une carte SIM active ;
- un ordinateur connecté à Internet ;
- un navigateur Web ;
- un outil de mesure de débit ou les outils réseau fournis par ton système d'exploitation ;
- un tableau pour noter les observations.

Les menus d'information radio dépendent du modèle de téléphone, de la version du système et de l'opérateur. Il n'existe donc pas un chemin de menu universel.

## 3. Les générations mobiles en un coup d'œil

Les générations se sont succédé en ajoutant des capacités. Les déploiements réels peuvent toutefois conserver plusieurs générations en parallèle et varier selon les pays, les opérateurs et les bandes de fréquences autorisées.

| Génération | Orientation générale | Exemples de capacités | Limites à connaître |
|---|---|---|---|
| 2G (GSM) | Voix numérique et SMS ; données lentes avec les évolutions GPRS/EDGE | Appels classiques, SMS, données à faible débit | Faible capacité de données par rapport aux générations suivantes |
| 3G (UMTS/HSPA) | Internet mobile et services de données plus développés | Navigation Web, appels et données simultanés selon l'architecture | Capacité et efficacité généralement inférieures à LTE |
| 4G (LTE) | Réseau mobile orienté paquets IP | Haut débit mobile, LTE avancé, VoLTE avec IMS | Dépend du spectre, de la couverture, de la charge et du cœur de réseau |
| 5G (NR) | Radio plus flexible et évolution du cœur de réseau | Débits élevés, meilleure capacité dans de bonnes conditions, usages IoT et services spécialisés | Les gains ne sont pas automatiques ; ils dépendent du spectre, du déploiement et du terminal |

La 4G LTE a fortement généralisé une architecture mobile orientée IP. La 5G introduit une nouvelle interface radio, appelée NR (*New Radio*), ainsi qu'un cœur de réseau conçu pour davantage de flexibilité, notamment en mode Standalone.

**À retenir :** l'étiquette 4G ou 5G ne garantit pas à elle seule un débit, une couverture ou une latence précise. Les conditions radio, la largeur de bande disponible, la charge de la cellule, le terminal, le transport et le cœur de réseau influencent tous le résultat.

## 4. Vue d'ensemble d'une connexion mobile

Quatre éléments sont utiles pour comprendre le parcours d'une donnée :

1. **UE (*User Equipment*)** : le téléphone, une tablette, un routeur 4G/5G ou un modem cellulaire.
2. **RAN (*Radio Access Network*)** : le réseau d'accès radio qui relie le terminal au réseau de l'opérateur.
3. **Cœur de réseau (*Core Network*)** : les fonctions d'authentification, de mobilité, de gestion de session et d'acheminement des données.
4. **Réseau de destination** : Internet, un réseau d'entreprise, un serveur privé ou un service de l'opérateur.

```text
+--------------------+
| Téléphone / UE     |
+---------+----------+
          |
          | Liaison radio 4G LTE ou 5G NR
          v
+--------------------+
| Station de base    |
| eNodeB (4G)        |
| gNodeB (5G)        |
+---------+----------+
          |
          | Réseau de transport de l'opérateur
          v
+--------------------+
| Cœur de réseau     |
| EPC (4G) ou 5GC    |
| (5G Standalone)    |
+---------+----------+
          |
          v
+--------------------+
| Internet / services|
+--------------------+
```

Ce schéma est logique et simplifié. Dans un réseau réel, ces fonctions sont réparties sur de nombreux équipements, sites et liens. Certaines fonctions du cœur peuvent aussi être virtualisées ou exécutées sur une infrastructure cloud.

## 5. La carte SIM et l'identité de l'abonné

La carte SIM, ou une eSIM intégrée, contient des éléments permettant au terminal de s'authentifier sur le réseau mobile. Elle ne constitue pas, à elle seule, le téléphone ni le service Internet : le réseau doit reconnaître l'abonnement et appliquer le profil de service correspondant.

Quelques notions importantes :

- **IMSI** : identifiant international d'abonné utilisé dans les architectures mobiles antérieures et encore pertinent pour certaines procédures d'interfonctionnement.
- **SUPI** : identifiant permanent d'abonné utilisé dans l'architecture 5G.
- **SUCI** : représentation protégée du SUPI utilisée dans certains mécanismes 5G pour limiter l'exposition de l'identité permanente sur l'interface radio.
- **IMEI** : identifiant de l'équipement mobile, distinct de l'identité de l'abonné.
- **PLMN** : réseau mobile public identifié par les codes MCC et MNC, correspondant respectivement au pays et au réseau mobile.

L'identité de l'équipement et l'identité de l'abonnement sont donc deux choses différentes. Un téléphone peut être techniquement compatible avec un réseau sans que sa SIM ou son forfait autorise tous les services proposés.

# Partie I — La 4G LTE

## 6. Architecture générale de la 4G

La 4G LTE s'appuie sur un réseau d'accès appelé **E-UTRAN** et un cœur de réseau appelé **EPC** (*Evolved Packet Core*).

```text
                   E-UTRAN
        +---------------------------+
        |                           |
   +----+-----+                +----+-----+
   | eNodeB A |------ X2 ------| eNodeB B |
   +----+-----+                +----+-----+
        |                           |
        +-------------+-------------+
                      | S1
                      v
             +----------------+
             |      EPC       |
             |                |
             | MME            |
             | S-GW            |
             | P-GW            |
             | HSS / PCRF      |
             +--------+-------+
                      |
                      v
                  Internet
```

La représentation rassemble plusieurs fonctions dans un même bloc pour simplifier la lecture. Dans le réseau réel, elles peuvent être hébergées sur des équipements différents.

### 6.1 UE — User Equipment

L'UE est le terminal mobile : téléphone, modem, routeur cellulaire ou autre équipement compatible LTE. Il doit prendre en charge les bandes de fréquences et les fonctionnalités utilisées par le réseau pour pouvoir en tirer pleinement parti.

### 6.2 eNodeB — station de base LTE

L'eNodeB est la station de base 4G. Il gère notamment :

- la communication radio avec les terminaux ;
- la planification des ressources radio ;
- une partie du contrôle de la liaison radio ;
- les mesures radio et la mobilité entre cellules ;
- l'échange de données avec le cœur de réseau.

Une station de base peut desservir plusieurs cellules ou secteurs. Le mot « antenne » est souvent utilisé dans le langage courant, mais l'antenne physique, la cellule logique et l'ensemble de la station de base ne sont pas strictement synonymes.

### 6.3 MME — Mobility Management Entity

Le MME est une fonction de contrôle du cœur EPC. Parmi ses responsabilités figurent la gestion de la mobilité et de l'état de connexion, la signalisation de contrôle ainsi que des procédures liées à l'authentification et à la sécurité.

Il ne transporte pas normalement le trafic utilisateur de la même manière que le plan utilisateur. Il participe principalement au **plan de contrôle**.

### 6.4 S-GW — Serving Gateway

Le S-GW sert de point d'ancrage et de transfert pour une partie du trafic utilisateur entre le réseau d'accès LTE et les autres fonctions de l'EPC. Il participe aussi à certaines procédures de mobilité.

### 6.5 P-GW — PDN Gateway

Le P-GW fournit la connectivité vers un réseau de données externe, par exemple Internet ou un réseau privé. Selon le déploiement, il participe à l'allocation d'adresse IP du terminal, au filtrage et à l'application de politiques de service.

### 6.6 HSS — Home Subscriber Server

Le HSS contient des données d'abonnement et des informations nécessaires à l'authentification et à l'autorisation des services. Il contribue à déterminer si un utilisateur est autorisé à s'enregistrer et à accéder aux services mobiles.

### 6.7 PCRF — Policy and Charging Rules Function

Le PCRF participe à la décision des politiques de qualité de service et de taxation dans l'architecture EPC. Les règles effectivement appliquées dépendent du profil de l'abonné, des services souscrits et de la configuration de l'opérateur.

### 6.8 APN — Access Point Name

L'APN désigne le point d'accès logique utilisé pour établir la connectivité vers un réseau de données. Un opérateur peut, par exemple, proposer des APN distincts pour Internet public, des services privés ou certaines offres d'entreprise.

Un APN mal configuré, non autorisé ou associé à un mauvais profil peut empêcher l'accès aux données même lorsque le terminal capte correctement le réseau radio.

## 7. Comment une session de données 4G est-elle établie ?

Le détail des procédures est complexe, mais le parcours peut se comprendre en grandes étapes :

1. Le terminal détecte une cellule LTE convenable et tente de s'y connecter.
2. Il établit une connexion de signalisation radio avec l'eNodeB.
3. Le réseau traite les procédures de contrôle et d'authentification nécessaires.
4. Le cœur de réseau vérifie l'abonnement et met en place la connectivité appropriée.
5. Un contexte de données et un bearer sont établis selon le service et la politique de l'opérateur.
6. Le terminal peut échanger des paquets IP via l'eNodeB, l'EPC et le réseau de destination.

```text
Téléphone       eNodeB             EPC                 Internet
    |               |                |                     |
    |-- recherche cellule ---------->|                     |
    |-- signalisation radio -------> |                     |
    |               |-- contrôle --->|                     |
    |               |                |-- vérifications     |
    |               |                |-- session données   |
    |<-------------- connexion établie --------------------|
    |               |                |                     |
    |================ paquets IP =========================>|
```

Ce déroulé ne représente pas tous les messages de signalisation et ne doit pas être interprété comme une séquence complète de messages normalisés. Il sert à comprendre la séparation entre accès radio, contrôle réseau et transport de données.

## 8. Les appels vocaux en 4G : VoLTE et IMS

LTE est principalement conçue autour du transport de paquets. Pour fournir de la voix sur LTE, les opérateurs utilisent généralement **VoLTE** (*Voice over LTE*), qui s'appuie sur l'**IMS** (*IP Multimedia Subsystem*).

IMS est une architecture de services multimédias IP qui peut servir à la voix, à la vidéo et à d'autres services de communication. Dans un déploiement VoLTE, le réseau mobile doit être configuré pour la voix, et le terminal comme l'abonnement doivent être compatibles.

Le simple fait qu'un téléphone affiche « 4G » ne garantit pas que tous les appels passent en VoLTE. Selon le réseau et le terminal, d'autres mécanismes peuvent être utilisés, notamment le repli vers une technologie plus ancienne lorsque celle-ci est encore disponible.

# Partie II — La 5G

## 9. Qu'est-ce que la 5G NR ?

La 5G NR (*New Radio*) est l'interface radio de la cinquième génération. Elle permet des configurations radio plus flexibles et une évolution des performances, en fonction de la bande de fréquences, du spectre attribué, des antennes, du terminal et de l'architecture du réseau.

La 5G n'est pas uniquement une radio plus rapide. Elle est également conçue pour mieux adapter les ressources et les fonctions réseau à des services présentant des besoins différents.

L'UIT présente trois grandes familles de scénarios d'usage de l'IMT-2020 :

- **eMBB — enhanced Mobile Broadband** : haut débit mobile, par exemple pour le streaming et l'accès rapide aux services en ligne.
- **URLLC — Ultra-Reliable Low-Latency Communications** : services visant une fiabilité élevée et une faible latence dans des conditions précisément définies.
- **mMTC — massive Machine-Type Communications** : prise en charge d'un grand nombre d'équipements connectés, comme certains capteurs IoT.

Ces catégories décrivent des objectifs et des familles d'usage. Elles ne signifient pas que toute connexion 5G commerciale garantit automatiquement une latence d'une milliseconde, une fiabilité déterminée ou un million d'équipements opérationnels par kilomètre carré.

## 10. Architecture de la 5G Standalone

La 5G Standalone, ou **5G SA**, utilise un accès radio 5G NR associé à un cœur de réseau 5G appelé **5GC** (*5G Core*).

```text
+-------------------+
| Téléphone / UE 5G |
+---------+---------+
          |
          | 5G NR
          v
+-------------------+
| gNodeB (gNB)      |
| Réseau d'accès 5G |
+---------+---------+
          |
          | Réseau de transport
          v
+--------------------------------+
|             5G Core             |
|                                |
| AMF  - accès et mobilité       |
| SMF  - gestion des sessions    |
| UPF  - transfert des données   |
| UDM  - données d'abonnement    |
| AUSF - authentification        |
| PCF  - politiques réseau       |
+----------------+---------------+
                 |
                 v
        Internet / services privés
```

### 10.1 gNodeB (gNB)

Le gNB est la station de base 5G NR. Il fournit l'accès radio 5G au terminal et échange les données et la signalisation avec le cœur 5G. L'architecture radio peut varier selon le déploiement et le découpage fonctionnel retenu.

### 10.2 AMF — Access and Mobility Management Function

L'AMF gère notamment l'enregistrement du terminal, des aspects de mobilité et une partie de la signalisation de contrôle entre l'UE et le cœur 5G.

### 10.3 SMF — Session Management Function

Le SMF gère les sessions de données, notamment leur établissement et leur modification, et contrôle les éléments du plan utilisateur nécessaires à ces sessions.

### 10.4 UPF — User Plane Function

L'UPF assure le transfert des paquets utilisateur entre le réseau d'accès, les autres fonctions pertinentes et les réseaux de données. Son emplacement peut avoir une influence sur les chemins empruntés et la latence.

### 10.5 UDM — Unified Data Management

L'UDM gère des données liées aux abonnés et aux profils de service. Il contribue aux mécanismes permettant au réseau de connaître les droits et les caractéristiques d'un abonnement.

### 10.6 AUSF — Authentication Server Function

L'AUSF participe aux procédures d'authentification. Il travaille avec les autres fonctions concernées pour vérifier l'identité et les éléments d'authentification de l'abonné.

### 10.7 PCF — Policy Control Function

Le PCF contribue à la gestion des politiques, notamment celles qui déterminent les traitements et règles de service applicables aux sessions.

### 10.8 NSSF et NRF

- **NSSF — Network Slice Selection Function** : contribue à la sélection de tranche réseau lorsque les mécanismes de slicing sont utilisés.
- **NRF — Network Repository Function** : aide les fonctions du réseau à découvrir les autres fonctions de réseau disponibles dans l'architecture 5G.

Le 5GC comporte d'autres fonctions. Cette liste présente les plus utiles pour comprendre les bases et n'est pas un inventaire exhaustif.

## 11. 5G NSA et 5G SA : une différence essentielle

Deux expressions reviennent souvent : NSA et SA.

### 11.1 5G NSA — Non-Standalone

Dans une architecture NSA courante, la radio LTE et la radio 5G NR peuvent fonctionner ensemble, tandis que le réseau reste raccordé au cœur 4G EPC selon l'option de déploiement retenue.

Cette approche a permis à des opérateurs de déployer la 5G radio en réutilisant une partie importante de leur infrastructure 4G existante.

```text
                    Terminal compatible
                      /           \
                     /             \
                  LTE               NR
                   |                 |
                 eNodeB ------------ gNodeB
                   |      liaison    |
                   +-----------------+
                           |
                           v
                         EPC 4G
                           |
                           v
                        Internet
```

Le schéma est simplifié : l'organisation exacte de la double connectivité dépend de l'option NSA et de l'implémentation retenue.

### 11.2 5G SA — Standalone

En SA, le terminal peut se connecter en 5G NR à un cœur 5G, sans dépendre d'un cœur EPC 4G pour la connexion 5G principale.

```text
              Terminal compatible 5G
                       |
                     5G NR
                       |
                     gNodeB
                       |
                     5G Core
                       |
             +---------+---------+
             |                   |
          Internet          Réseau privé
```

### 11.3 Comparaison

| Critère | 5G NSA | 5G SA |
|---|---|---|
| Accès radio | LTE et NR peuvent être utilisés ensemble | Accès 5G NR vers le 5GC dans l'architecture SA |
| Cœur principal dans le déploiement type | EPC 4G | 5GC |
| Réutilisation de l'infrastructure LTE/EPC | Importante dans le modèle courant | Le 5GC doit être déployé et exploité |
| Services fondés sur les fonctions natives du 5GC | Limités par l'architecture NSA utilisée | Architecture prévue pour ces fonctions |
| Network slicing de bout en bout | Dépend fortement de l'architecture et des fonctions disponibles | Peut s'appuyer sur les fonctions natives du 5GC si elles sont déployées et configurées |

Il ne faut pas considérer SA comme systématiquement plus rapide que NSA dans chaque situation. Le résultat dépend du spectre, de la couverture, de la charge radio, du cœur, du transport, du terminal et de la politique de service.

## 12. APN en 4G et DNN en 5G

L'APN est couramment utilisé pour désigner le point d'accès logique d'une session de données 4G. En 5G, la notion correspondante est le **DNN** (*Data Network Name*).

Ces paramètres orientent la connectivité vers un réseau de données déterminé, selon la configuration de l'opérateur.

Exemples illustratifs :

- accès à Internet public ;
- accès à un réseau privé d'entreprise ;
- accès à un service géré par l'opérateur.

Un réseau privé mobile peut être configuré pour donner accès à certaines applications d'entreprise sans offrir le même chemin vers Internet public. Les détails dépendent des politiques et de l'architecture déployées.

## 13. Le slicing réseau

Le **network slicing** est une approche qui permet de construire plusieurs tranches logiques de réseau adaptées à différents besoins à partir d'une infrastructure partagée.

```text
                 Infrastructure mobile partagée
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
        Tranche A        Tranche B        Tranche C
        Haut débit       IoT              Industrie
        mobile           massif           spécialisée
```

Chaque tranche peut avoir des caractéristiques et des politiques différentes, dans la limite des ressources réellement déployées et disponibles.

Le slicing n'implique pas nécessairement un réseau physique entièrement séparé pour chaque service. Il ne supprime pas non plus les contraintes de radio, de transport, de calcul ou de capacité. Il faut distinguer la possibilité prévue par les normes et le service effectivement déployé par un opérateur.

# Partie III — La radio mobile

## 14. Cellules, sites et secteurs

Un réseau mobile est généralement organisé en cellules. Une cellule est une zone de couverture logique desservie par une configuration radio donnée.

Un site peut héberger plusieurs antennes, secteurs et bandes. Une carte de couverture est donc une représentation simplifiée d'un environnement radio variable.

Le terminal peut changer de cellule en se déplaçant ou lorsque les conditions radio évoluent. Cette opération s'inscrit dans la gestion de mobilité.

### 14.1 Pourquoi les cellules sont-elles nécessaires ?

Une seule station de base ne pourrait pas fournir efficacement le service à tous les utilisateurs d'un pays. Les opérateurs déploient de nombreux sites afin de répartir la couverture et la capacité.

- En zone rurale, une cellule peut devoir couvrir une zone géographique étendue.
- En zone urbaine dense, de petites cellules peuvent être nécessaires pour absorber la demande.
- Dans les bâtiments, la pénétration des signaux peut réduire la couverture.
- Dans les stades, gares et centres commerciaux, la capacité peut devenir aussi importante que la couverture.

**Couverture** signifie qu'un signal utilisable est disponible. **Capacité** désigne la quantité de trafic que le réseau peut supporter dans les conditions considérées. Une zone peut être bien couverte mais saturée.

## 15. Spectre et bandes de fréquences

Les réseaux mobiles utilisent des bandes de fréquences attribuées et réglementées. Un opérateur ne peut pas simplement choisir librement n'importe quelle fréquence pour son réseau public.

Les propriétés radio varient avec la fréquence, la puissance, les obstacles, les antennes et l'environnement.

### 15.1 Comparaison qualitative

| Type de bande | Atouts courants | Contraintes courantes | Usages fréquents |
|---|---|---|---|
| Fréquences basses | Bonne portée et meilleure pénétration à couverture comparable | Quantité de spectre parfois limitée, donc capacité par cellule potentiellement plus faible | Couverture étendue, zones rurales et intérieur des bâtiments |
| Fréquences moyennes | Équilibre intéressant entre portée et capacité | Portée et pénétration variables selon la fréquence et l'environnement | Couverture urbaine et capacité 4G/5G |
| Fréquences très élevées, notamment certaines bandes millimétriques | Possibilité de disposer de larges canaux | Atténuation plus importante, sensibilité aux obstacles et couverture souvent plus localisée | Hotspots, zones à forte capacité et certains déploiements spécialisés |

Ce tableau donne des tendances générales, pas une loi absolue. La puissance, la hauteur des sites, le type de bâtiment, les antennes et la topographie influencent fortement le résultat.

### 15.2 FR1 et FR2 en 5G NR

Dans les spécifications 3GPP citées dans les références de ce cours, les plages de fréquences NR sont définies notamment comme suit :

- **FR1** : 410 MHz à 7 125 MHz.
- **FR2** : 24,25 GHz à 52,6 GHz pour les plages couvertes par les spécifications correspondantes.

Les bandes effectivement utilisées dépendent des normes applicables, du pays, de l'attribution du spectre, des autorisations réglementaires et du matériel de l'opérateur. Les bornes de fréquence peuvent évoluer selon la version des spécifications et les bandes concernées.

Il ne faut donc pas déduire la couverture d'un réseau du seul mot « 5G ». Il faut aussi connaître la bande utilisée, la largeur du canal, les caractéristiques des antennes et la disponibilité du spectre.

## 16. Uplink, downlink et duplexage

Les communications mobiles comprennent deux sens :

- **Downlink (DL)** : de la station de base vers le terminal.
- **Uplink (UL)** : du terminal vers la station de base.

Le terminal ne dispose pas forcément des mêmes ressources ni de la même puissance d'émission que la station de base. C'est une raison pour laquelle les débits montants et descendants peuvent être différents.

Deux modes de duplexage sont fréquents :

- **FDD (*Frequency Division Duplex*)** : l'émission et la réception utilisent des bandes de fréquences distinctes appariées.
- **TDD (*Time Division Duplex*)** : émission et réception utilisent la même bande mais à des instants distincts selon une configuration temporelle.

Le mode et la répartition des ressources ont une influence sur les capacités en montée et en descente.

## 17. Largeur de bande et débit

La largeur de bande disponible est l'un des facteurs importants du débit maximal possible. Un canal plus large permet généralement de transporter plus de données dans des conditions radio équivalentes, sans pour autant garantir un débit supérieur dans toutes les situations.

Le débit réel dépend entre autres :

- de la largeur de bande et du spectre utilisé ;
- du rapport signal/bruit et des interférences ;
- de la modulation et du codage retenus ;
- du nombre de couches spatiales exploitables ;
- du partage des ressources entre utilisateurs ;
- de la capacité du transport et du cœur de réseau ;
- de la capacité du terminal et du serveur de destination.

Une annonce commerciale de débit de pointe décrit une condition de référence ou un maximum théorique ou de laboratoire. Elle ne garantit pas le débit obtenu par un utilisateur donné.

## 18. OFDM, ressources radio et modulation

LTE et NR s'appuient sur des formes d'onde de la famille OFDM. De façon simplifiée, plusieurs sous-porteuses orthogonales transportent de l'information parallèlement dans un canal radio.

```text
Largeur de bande radio
+----------------------------------------------------+
| sous-porteuse | sous-porteuse | sous-porteuse | ... |
+----------------------------------------------------+
             Ressources attribuées dans le temps
```

La station de base planifie les ressources disponibles pour les terminaux, en prenant en compte des éléments comme les conditions radio et les besoins de service.

La modulation représente la manière dont les informations sont codées dans les symboles transmis. Des modulations plus denses peuvent transmettre davantage de bits par symbole, mais exigent généralement de meilleures conditions radio pour conserver une qualité acceptable.

L'OFDM n'explique pas à lui seul toute la 4G ou la 5G. Les deux générations diffèrent aussi dans la structure des trames, la gestion des ressources, les options radio et le fonctionnement du réseau.

## 19. MIMO et beamforming

### 19.1 MIMO

Le MIMO (*Multiple Input, Multiple Output*) utilise plusieurs antennes d'émission et/ou de réception pour améliorer les performances radio.

Selon les conditions, le système peut utiliser la diversité spatiale pour renforcer la robustesse ou plusieurs couches spatiales pour augmenter le débit.

### 19.2 Beamforming

Le beamforming consiste à ajuster la manière dont plusieurs éléments d'antenne émettent ou reçoivent afin de favoriser certaines directions.

```text
          Groupe d'antennes
             \\\ | ///
              \\ | //
                \|/
                 |
                 v
         Zone de réception visée
```

Le dessin est illustratif et ne représente pas précisément un diagramme de rayonnement réel. Le beamforming peut aider à utiliser le signal radio plus efficacement, mais les résultats dépendent du matériel, de l'environnement et des conditions de propagation.

## 20. Agrégation de porteuses

L'agrégation de porteuses (*Carrier Aggregation*) permet de combiner plusieurs porteuses radio lorsque le réseau et le terminal prennent en charge la combinaison utilisée.

Par exemple, un terminal peut utiliser une porteuse d'une bande et une autre porteuse d'une bande différente afin d'augmenter la largeur de bande totale disponible.

Cela ne signifie pas que toutes les bandes sont toujours utilisées simultanément, ni que tout terminal prend en charge toutes les combinaisons possibles.

## 21. Mesures radio utiles

Les téléphones et les outils de mesure peuvent afficher différentes valeurs. Les plus communes comprennent :

| Indicateur | Signification simplifiée | Unité | Comment l'interpréter |
|---|---|---|---|
| RSRP | Puissance reçue des signaux de référence LTE/NR, selon la mesure concernée | dBm | Plus la valeur est proche de zéro, plus le niveau reçu est généralement fort |
| RSRQ | Qualité de réception tenant compte notamment du niveau reçu et de l'énergie observée | dB | Une valeur plus élevée est généralement préférable, mais le contexte de mesure compte |
| SINR | Rapport signal utile / interférences et bruit | dB | Plus il est élevé, meilleures sont généralement les conditions pour des débits radio élevés |
| RSSI | Puissance totale reçue dans la bande de mesure | dBm | Inclut notamment signal, interférences et bruit selon la définition de la mesure |

Les seuils pratiques dépendent de la bande, de la technologie, du matériel et du contexte. Les plages ci-dessous sont donc des repères pédagogiques approximatifs, pas des seuils normatifs universels.

| Exemple RSRP | Lecture indicative |
|---|---|
| Environ -80 dBm | Signal souvent fort |
| Environ -95 dBm | Signal moyen ou acceptable selon le contexte |
| Environ -110 dBm | Signal faible dans de nombreux scénarios |

Pour les valeurs négatives, **-80 dBm est plus fort que -110 dBm** : le nombre est plus proche de zéro.

Un signal fort ne garantit pas une connexion rapide. Si la cellule est saturée ou si le SINR est mauvais, le débit peut rester faible.

# Partie IV — Mobilité, qualité de service et performances

## 22. Handover : passer d'une cellule à une autre

Lorsqu'un utilisateur se déplace, le terminal peut quitter une cellule et en rejoindre une autre. Cette transition est appelée **handover**.

Le réseau s'appuie sur des mesures radio, des paramètres de mobilité, la configuration de l'opérateur et des messages de signalisation pour décider et coordonner la transition.

```text
              déplacement du terminal
                     -------->

        Cellule A                    Cellule B
     +-------------+              +-------------+
     |             |              |             |
     |      UE ----+------------->|             |
     |             |              |             |
     +-------------+              +-------------+
                 Handover
```

Le dessin est conceptuel. Le handover n'est pas toujours déclenché uniquement parce que le terminal se rapproche d'une autre antenne. La qualité radio, les seuils, les temporisations, la charge et les stratégies réseau peuvent intervenir.

Un handover réussi vise à préserver la continuité du service. En cas de problème, l'utilisateur peut constater une interruption, une coupure d'appel, une perte momentanée de données ou un retour vers une autre technologie.

## 23. Itinérance ou roaming

Le roaming permet à un abonné d'utiliser un réseau mobile visité en dehors du réseau auquel son abonnement est normalement rattaché, sous réserve des accords et des politiques applicables.

Le réseau visité fournit l'accès radio et collabore avec d'autres éléments du système pour appliquer les procédures autorisées. Selon l'architecture, certains traitements peuvent être gérés par le réseau d'origine ou par le réseau visité.

Le roaming dépend notamment :

- des accords entre opérateurs ;
- des technologies et bandes compatibles ;
- du forfait et des services autorisés ;
- des paramètres de l'abonnement ;
- des règles tarifaires et réglementaires.

Avoir un téléphone compatible avec la 5G ne signifie donc pas que la 5G sera nécessairement accessible lors d'un déplacement à l'étranger.

## 24. QoS : les ressources adaptées au service

La qualité de service (*Quality of Service*, QoS) regroupe les mécanismes qui permettent de traiter différents flux selon des caractéristiques et des politiques définies.

Les exigences peuvent porter sur le débit, le délai, la variation du délai, le taux de perte ou la priorité de traitement. La manière dont ces exigences sont exprimées et appliquées dépend de la génération, du service et du réseau.

En LTE, les bearers et des indicateurs comme le QCI font partie de la logique QoS. En 5G, les flux QoS et les 5QI sont des éléments importants du modèle de service.

La QoS ne crée pas une capacité infinie. Si une cellule est congestionnée ou si une liaison de transport est saturée, les ressources restent limitées. Les règles de politique et d'abonnement déterminent également le traitement effectivement accordé.

## 25. Débit, latence, gigue et pertes

Ces indicateurs ne mesurent pas la même chose :

- **Débit** : quantité de données transférées par unité de temps, par exemple en Mbit/s.
- **Latence** : délai nécessaire à un paquet pour atteindre une destination ou effectuer un aller-retour, selon la mesure.
- **Gigue** : variation du délai des paquets.
- **Perte de paquets** : part des paquets envoyés qui n'arrivent pas à destination selon la mesure considérée.

Une connexion peut afficher un débit élevé tout en présentant une latence instable. À l'inverse, une connexion de débit modéré peut convenir à une application interactive si la latence et les pertes sont faibles.

La latence mesurée jusqu'à un serveur distant inclut plusieurs segments : accès radio, transport de l'opérateur, cœur de réseau, interconnexions et réseau de destination. Elle ne mesure donc pas uniquement la radio.

## 26. VoLTE et VoNR

VoLTE désigne la voix sur LTE, généralement basée sur IMS. **VoNR** désigne la voix sur NR dans une architecture adaptée, notamment 5G SA, avec le support nécessaire du terminal, du cœur et des services de l'opérateur.

Un opérateur peut aussi conserver des solutions d'interfonctionnement avec LTE pour la voix pendant la transition vers SA. Le comportement exact varie selon le déploiement et le terminal.

Les symptômes « Internet mobile fonctionne, mais les appels échouent » ou « l'appel entraîne un changement de technologie » ne désignent donc pas nécessairement une panne de la radio 5G : les services voix, IMS, l'abonnement et les mécanismes de repli doivent être considérés.

# Partie V — Sécurité et exploitation

## 27. Principes de sécurité mobile

Les réseaux 4G et 5G utilisent des mécanismes normalisés d'authentification et de protection des communications. Ces mécanismes sont importants, mais la sécurité globale dépend aussi des configurations, des mises à jour, des interfaces, des systèmes d'administration et des équipements déployés.

Il faut distinguer plusieurs objectifs :

- **Authentification** : vérifier que l'abonné ou l'équipement satisfait aux mécanismes d'identification attendus.
- **Confidentialité** : limiter la possibilité qu'une personne non autorisée lise les données protégées.
- **Intégrité** : détecter certaines modifications non autorisées des messages protégés.
- **Contrôle d'accès** : décider quels services et ressources peuvent être utilisés.
- **Résilience** : continuer à fournir un service acceptable malgré certaines pannes ou perturbations.

En 5G, des mécanismes comme SUCI contribuent à protéger l'identité permanente de l'abonné pendant certaines procédures. Cela ne rend pas l'utilisateur anonyme vis-à-vis de son opérateur et ne supprime pas tous les risques de suivi ou d'attaque.

### 27.1 Risques et mesures de réduction

| Risque | Exemple | Mesures possibles |
|---|---|---|
| Mauvaise configuration | APN/DNN incorrect, politique inadaptée | Gestion des changements, tests et revue de configuration |
| Panne radio | Équipement ou liaison radio indisponible | Supervision, redondance et maintenance |
| Saturation de cellule | Trop de trafic pour les ressources disponibles | Mesure de charge, optimisation et augmentation de capacité |
| Attaque ou abus de signalisation | Tentatives excessives ou exploitation d'une vulnérabilité | Mises à jour, contrôles d'accès, supervision et procédures de sécurité |
| Exposition d'une interface d'administration | Accès de gestion ouvert ou mal protégé | Segmentation, authentification forte et filtrage |
| Défaillance d'alimentation ou de transport | Site radio isolé | Alimentation secourue, redondance et supervision des liens |

Les mesures exactes relèvent de la politique de sécurité et de l'architecture de chaque opérateur. Il ne faut pas tester un réseau mobile public contre ses politiques ou autorisations : les expérimentations de ce cours doivent rester non intrusives et autorisées.

## 28. Les indicateurs d'exploitation (KPI)

Les opérateurs surveillent un ensemble d'indicateurs pour mesurer la qualité et la disponibilité. Les KPI exacts varient selon les outils, le fournisseur et la définition retenue.

Exemples fréquents :

- taux de réussite des enregistrements ou connexions ;
- taux d'établissement et de maintien des appels ;
- taux de réussite des handovers ;
- débit moyen et distribution des débits utilisateurs ;
- latence et pertes ;
- charge des cellules et utilisation des ressources radio ;
- disponibilité des sites et des fonctions du cœur ;
- taux d'échec de sessions de données.

Un KPI isolé est rarement suffisant. Un opérateur doit corréler les mesures radio, les événements du cœur, les alarmes de transport, les incidents d'alimentation et l'expérience utilisateur.

# Partie VI — Parcours pratique du débutant

## 29. TP 1 — Observer la connexion de son téléphone

**Objectif :** observer les informations de connexion et apprendre à distinguer couverture, qualité et performance.

### Étape 1 — Relever l'état de la connexion

Sur ton téléphone :

1. Ouvre les paramètres du réseau mobile ou les informations relatives à la SIM.
2. Note la technologie affichée : LTE/4G, NR/5G ou autre.
3. Note si les données mobiles et l'itinérance sont activées.
4. Si le téléphone fournit des informations radio détaillées, relève RSRP, RSRQ et SINR.
5. Note l'endroit général où tu réalises le test : intérieur, extérieur, quartier dense ou zone peu habitée.

Les menus et informations disponibles varient selon le terminal. N'utilise pas de code de diagnostic trouvé au hasard et ne modifie pas de paramètres radio avancés sans en comprendre les conséquences.

### Étape 2 — Mesurer les performances

Utilise un outil de mesure de débit reconnu ou les outils réseau de ton système. Effectue plusieurs mesures en notant :

- technologie affichée ;
- débit descendant ;
- débit montant ;
- latence affichée par l'outil ;
- heure et emplacement général ;
- si tu étais immobile ou en déplacement.

Ne manipule pas le téléphone en conduisant. N'effectue les mesures qu'à l'arrêt, dans un lieu où tu peux utiliser ton appareil en sécurité.

### Étape 3 — Interpréter

Si le débit change entre deux mesures, ne conclus pas immédiatement que la technologie est défectueuse. Vérifie notamment :

- si la cellule est chargée ;
- si les conditions radio ont changé ;
- si le serveur de test ou le transport est congestionné ;
- si le terminal a changé de bande ou de cellule ;
- si les mesures ont été réalisées au même endroit et à des horaires comparables.

### Fiche de résultats

| Mesure | Test A | Test B |
|---|---|---|
| Technologie affichée | À remplir | À remplir |
| RSRP (si disponible) | À remplir | À remplir |
| RSRQ (si disponible) | À remplir | À remplir |
| SINR (si disponible) | À remplir | À remplir |
| Débit descendant | À remplir | À remplir |
| Débit montant | À remplir | À remplir |
| Latence | À remplir | À remplir |
| Contexte | À remplir | À remplir |

**Résultat attendu :** produire une courte conclusion qui distingue les faits mesurés des hypothèses. Une mesure unique ne suffit pas à caractériser toute la qualité d'un réseau.

## 30. TP 2 — Tester la connectivité IP sur le réseau mobile

**Objectif :** séparer les problèmes de connectivité IP des problèmes de performance radio.

Sur un ordinateur connecté au partage de connexion du téléphone, ou directement sur un terminal disposant des outils nécessaires, tu peux réaliser les tests suivants. Les tests doivent être effectués vers des destinations publiques autorisées et peuvent être limités par le réseau ou le serveur distant.

### Sous Windows

```powershell
ping -n 20 1.1.1.1
tracert 1.1.1.1
```

### Sous Linux ou macOS

```bash
ping -c 20 1.1.1.1
traceroute 1.1.1.1
```

Les commandes supposent que les outils correspondants sont présents et que la destination répond aux sondes utilisées.

Interprétation :

- Si le ping échoue, cela ne prouve pas à lui seul que l'accès Internet est coupé : ICMP peut être filtré ou limité.
- Si les temps d'aller-retour varient fortement, il peut y avoir de la congestion, des variations radio ou d'autres délais sur le trajet.
- Si traceroute affiche des sauts sans réponse, cela peut simplement indiquer que certains routeurs ne répondent pas aux sondes.
- Si plusieurs applications ne fonctionnent pas alors que l'accès radio semble correct, vérifie également DNS, session de données, APN/DNN, routage et service distant.

Ne lance pas de scan massif ni de test de charge contre des réseaux tiers. Ces commandes simples suffisent pour observer une connectivité de base.

## 31. TP 3 — Cartographier une architecture 4G et 5G

**Objectif :** être capable de relier chaque fonction à son rôle.

### Scénario

Un utilisateur ouvre une application Web depuis son téléphone.

1. Identifie le terminal, la station de base et le cœur de réseau.
2. Dans le cas 4G, place les fonctions eNodeB, MME, S-GW et P-GW.
3. Dans le cas 5G SA, place gNB, AMF, SMF et UPF.
4. Trace le parcours des données utilisateur.
5. Trace séparément la signalisation de contrôle à un niveau conceptuel.
6. Indique quelle fonction gère la session et quelle fonction transfère les paquets utilisateur.

### Correction

En 4G, l'eNodeB fournit l'accès radio. Le MME participe au contrôle et à la mobilité ; le S-GW et le P-GW prennent part au transport des données entre l'accès LTE et le réseau de destination.

En 5G SA, le gNB fournit l'accès radio. L'AMF participe à l'accès et à la mobilité, le SMF gère les sessions et l'UPF transfère le trafic utilisateur vers le réseau de données.

Il s'agit d'un modèle fonctionnel. Il ne montre pas l'ensemble des interfaces, des fonctions d'authentification ni des procédures du protocole.

## 32. TP 4 — Simuler le diagnostic d'un problème mobile

**Objectif :** appliquer une méthode de diagnostic structurée.

### Cas A — Le téléphone affiche 5G, mais les pages Web ne s'ouvrent pas

Hypothèses possibles :

- les données mobiles sont désactivées ;
- la session de données n'est pas établie ;
- l'APN ou le profil d'abonnement est incorrect ;
- un problème DNS, de routage ou de service distant existe ;
- le terminal affiche une disponibilité radio 5G mais ne dispose pas d'une connectivité IP opérationnelle.

Démarche : vérifier l'état des données mobiles, l'abonnement et le profil de données ; tester une autre application ; vérifier la résolution DNS et la connectivité IP si les outils sont disponibles ; ensuite, isoler l'incident auprès de l'opérateur si nécessaire.

### Cas B — La connexion est bonne le matin, mais lente le soir

Hypothèse importante : la cellule ou un segment partagé du réseau est congestionné aux heures de pointe.

Démarche : comparer des mesures répétées à différents horaires et au même endroit ; observer le débit et la latence ; vérifier si le signal radio reste comparable ; éviter de conclure à une panne matérielle sans données supplémentaires.

### Cas C — Les appels coupent quand l'utilisateur se déplace

Hypothèses possibles : problème de handover, couverture insuffisante sur un segment du trajet, interférence, défaillance de cellule, ou problème de service voix/IMS.

Démarche : relever les lieux et heures de l'incident, voir s'il se reproduit sur le même trajet, déterminer si seules les voix ou également les données sont touchées, puis transmettre les observations à l'équipe réseau. Il faut des journaux et des mesures opérateur pour identifier la cause exacte.

# Partie VII — Exercices corrigés

## 33. Exercice 1 — Identifier les composants

Associe chaque élément à sa fonction :

1. UE
2. eNodeB
3. MME
4. P-GW
5. gNB
6. UPF
7. AMF
8. SMF

Fonctions :

A. Gestion des sessions de données en 5G.

B. Terminal mobile.

C. Accès radio 5G.

D. Contrôle de l'accès et de la mobilité en 5G.

E. Accès radio LTE.

F. Transfert du plan utilisateur en 5G.

G. Fonction de contrôle et de mobilité principale du cœur EPC.

H. Connectivité depuis le cœur EPC vers les réseaux de données.

### Correction

1-B ; 2-E ; 3-G ; 4-H ; 5-C ; 6-F ; 7-D ; 8-A.

## 34. Exercice 2 — Couverture ou capacité ?

Une zone affiche un RSRP de -82 dBm. Les utilisateurs observent un débit très faible à 19 h, mais un débit nettement supérieur à 6 h au même endroit. Le RSRP reste proche de la même valeur.

Quelle hypothèse est prioritaire ?

### Correction

La couverture en puissance semble relativement stable et plutôt bonne selon ce repère. La variation temporelle du débit suggère notamment une congestion de cellule ou de ressources partagées. Il faut vérifier le SINR, la charge radio, les conditions de transport et les mesures effectuées avant de conclure.

## 35. Exercice 3 — NSA ou SA ?

Un opérateur active la radio 5G NR, mais conserve un cœur EPC 4G pour le déploiement NSA envisagé.

1. S'agit-il d'un déploiement SA natif ?
2. Quel cœur est utilisé dans ce modèle ?
3. Quel est l'intérêt d'une telle approche ?

### Correction

1. Non, il s'agit d'un modèle 5G NSA.
2. Le cœur EPC 4G est utilisé dans le déploiement type décrit.
3. Il permet de lancer la radio 5G en réutilisant une partie importante de l'infrastructure 4G existante, sans devoir déployer immédiatement tous les éléments d'un 5GC.

## 36. Exercice 4 — Lire les mesures radio

Deux relevés sont disponibles :

| Indicateur | Site A | Site B |
|---|---:|---:|
| RSRP | -85 dBm | -103 dBm |
| SINR | 19 dB | 4 dB |

Quel site présente, selon ces seules mesures, les conditions radio les plus favorables ? Peut-on en déduire exactement le débit ?

### Correction

Le site A présente à la fois un RSRP plus fort et un SINR plus élevé ; ses conditions radio sont donc généralement plus favorables. En revanche, il est impossible d'en déduire un débit exact sans connaître la largeur de bande, la charge, la configuration radio, les capacités du terminal et les conditions du réseau de transport.

## 37. Exercice 5 — Identifier le bon domaine de panne

Le téléphone est bien enregistré sur LTE. Les mesures radio sont stables. Plusieurs sites Web ne fonctionnent pas, mais l'état de la connexion indique que les données mobiles sont activées.

Cite quatre éléments à vérifier avant de conclure à une panne radio.

### Correction

Exemples de réponses pertinentes :

- établissement de la session de données ;
- APN et profil d'abonnement ;
- résolution DNS ;
- connectivité IP et routage ;
- éventuel filtrage ou incident du cœur de réseau ;
- disponibilité des services distants.

Le fait d'être enregistré sur le réseau radio ne prouve pas, à lui seul, que la connectivité IP fonctionne de bout en bout.

## 38. Exercice 6 — Vrai ou faux

1. Un signal 5G fort garantit toujours un débit élevé.
2. Le gNB est la station de base 5G NR.
3. Un APN peut influencer la connectivité de données 4G.
4. NSA et SA désignent deux architectures identiques.
5. La capacité d'une cellule dépend entre autres du spectre et du nombre d'utilisateurs actifs.
6. Un test ping qui échoue prouve toujours que le réseau mobile est en panne.

### Correction

1. Faux. La charge, le SINR, la largeur de bande et d'autres facteurs influencent le débit.
2. Vrai.
3. Vrai.
4. Faux. Les architectures diffèrent notamment par le recours au cœur 4G EPC ou au cœur 5G selon les modèles considérés.
5. Vrai.
6. Faux. ICMP peut être filtré et un équipement peut ne pas répondre aux sondes.

# Partie VIII — Défi final corrigé

## 39. Défi : diagnostiquer et concevoir un service mobile

### Situation

Un opérateur fictif dessert trois environnements :

- **Zone A — zone rurale** : les habitants ont besoin d'une couverture étendue. Le débit est modeste, mais la stabilité est importante.
- **Zone B — centre-ville** : la couverture est bonne, mais les débits chutent à l'heure de pointe.
- **Zone C — parc industriel** : une entreprise souhaite connecter des capteurs, des terminaux mobiles et des applications nécessitant des performances prévisibles.

L'opérateur possède déjà un réseau LTE EPC et commence à déployer la 5G NR.

### Travail demandé

1. Proposer une approche de couverture pour la zone A.
2. Identifier les causes possibles de la baisse de débit en zone B.
3. Expliquer pourquoi le passage à la 5G ne résout pas automatiquement la congestion.
4. Comparer NSA et SA pour la future évolution du cœur de réseau.
5. Décrire les fonctions nécessaires pour fournir la connectivité 5G dans le parc industriel.
6. Proposer une démarche de mesure et de validation avant la mise en production.

## 40. Correction détaillée du défi

### 40.1 Zone rurale

Il faut privilégier une planification de couverture qui tient compte de la portée, de la topographie, des obstacles, des fréquences disponibles et de la capacité attendue. Des bandes plus basses peuvent offrir une couverture étendue dans certains contextes, mais il faut vérifier le spectre réellement attribué et les contraintes locales.

La conception doit inclure le transport, l'alimentation électrique, la disponibilité des sites, la capacité de la cellule et les mécanismes de supervision. Une bonne couverture radio sans liaison de transport disponible ne fournit pas un service complet.

### 40.2 Centre-ville

La baisse des débits pendant les heures de pointe peut provenir de la congestion radio, de la saturation du transport ou du cœur, d'un serveur de mesure saturé, ou d'une combinaison de ces facteurs.

La démarche consiste à mesurer à horaires comparables, examiner les indicateurs radio et la charge des cellules, comparer plusieurs terminaux et destinations, puis corréler les mesures avec la supervision des liens et des fonctions réseau.

### 40.3 Pourquoi la 5G n'est pas une solution magique

La 5G offre de nouvelles possibilités, mais les performances dépendent de la quantité de spectre, de la qualité radio, des antennes, des terminaux, de la charge et du transport. Si la capacité de transport est déjà insuffisante, une amélioration radio seule peut déplacer le point de congestion plutôt que le supprimer.

L'architecture et les réglages doivent donc être conçus de bout en bout. Il faut également différencier le débit de pointe d'une cellule de l'expérience réellement obtenue par chaque utilisateur.

### 40.4 Choix entre NSA et SA

NSA peut représenter une étape de transition permettant de réutiliser l'EPC 4G et une partie de l'infrastructure existante. SA fournit une architecture 5G avec le 5GC, qui permet de tirer parti des fonctions conçues autour du cœur 5G lorsque celles-ci sont effectivement déployées.

Le choix dépend notamment des investissements, des terminaux compatibles, des services à offrir, des exigences d'exploitation et de la stratégie de migration. Il ne faut pas choisir une architecture sur la seule base d'un slogan commercial.

### 40.5 Parc industriel

Il faut déterminer les besoins des applications, le nombre et le profil des équipements, la couverture intérieure et extérieure, le niveau de disponibilité attendu et les exigences de sécurité.

Une architecture 5G SA peut fournir une base pour des fonctions telles que la QoS avancée ou le slicing, si l'ensemble des éléments requis est réellement disponible et configuré. Un réseau privé ou une connectivité dédiée peut également être évalué selon les besoins.

Le dossier doit préciser les limites de performance, les mécanismes de gestion des abonnés et des terminaux, l'isolement des services, la supervision, la redondance et les procédures de rétablissement. Les besoins très critiques doivent être validés par des mesures et des tests adaptés ; il ne suffit pas de compter sur le nom « 5G ».

### 40.6 Plan de validation avant lancement

1. Cartographier la couverture radio et le transport.
2. Définir les KPI et les seuils d'acceptation du service.
3. Tester la mobilité et les changements de cellule.
4. Mesurer débit, latence, pertes et gigue dans des conditions représentatives.
5. Tester la charge et la capacité sans perturber les réseaux publics ni les autres utilisateurs.
6. Valider l'authentification, les droits d'accès et les politiques QoS.
7. Simuler des pannes de lien et de fonction lorsque l'environnement de test le permet.
8. Documenter les résultats, les limites connues, le plan de maintenance et les procédures de retour arrière.

**Conclusion du défi :** une architecture mobile performante résulte d'une conception de bout en bout. La radio, le cœur, le transport, les services et l'exploitation doivent être considérés ensemble.

# Partie IX — Méthode de diagnostic et mémorisation

## 41. Une méthode de diagnostic en six étapes

Lorsqu'un utilisateur indique que « la 4G/5G ne marche pas », évite de remplacer immédiatement un équipement ou d'accuser la couverture. Procède par étapes :

1. **Définir le symptôme** : aucun service, données lentes, appels coupés, latence élevée ou problème intermittent ?
2. **Délimiter le périmètre** : un terminal, plusieurs abonnés, une zone, une cellule ou plusieurs sites ?
3. **Vérifier la radio** : technologie, signal, qualité, mobilité et charge si les données sont disponibles.
4. **Vérifier l'accès et la session** : enregistrement, authentification, APN/DNN et établissement des services.
5. **Vérifier le transport et le cœur** : connectivité, routage, DNS, saturation, alarmes et disponibilité des fonctions.
6. **Valider l'hypothèse** : réaliser des mesures comparables, documenter les résultats et vérifier que le problème a réellement disparu.

Cette démarche aide à éviter les conclusions basées sur une seule mesure ou sur l'icône affichée par le téléphone.

## 42. Parcours pratique recommandé

Pour consolider les connaissances, suis cet ordre :

1. Dessiner de mémoire le trajet d'un paquet depuis le téléphone jusqu'à un serveur Internet.
2. Reproduire le schéma d'architecture LTE/EPC et expliquer la fonction de chaque élément.
3. Reproduire le schéma 5G SA et expliquer la différence entre AMF, SMF et UPF.
4. Comparer NSA et SA sans te limiter à la vitesse annoncée.
5. Relever des mesures de connexion à différents endroits, sans conduire pendant les tests.
6. Réaliser des tests simples de connectivité IP et noter leurs limites.
7. Résoudre les scénarios de diagnostic sans consulter la correction, puis vérifier tes réponses.
8. Refaire le défi final en justifiant chaque décision par un besoin mesurable.

## 43. Glossaire essentiel

| Terme | Définition |
|---|---|
| 4G | Génération mobile fondée sur LTE dans les déploiements courants |
| 5G | Génération mobile utilisant notamment l'interface NR et pouvant s'appuyer sur le 5GC en SA |
| AMF | Fonction 5G de gestion de l'accès et de la mobilité |
| APN | Point d'accès logique d'une session de données mobile, notamment en 4G |
| eMBB | Haut débit mobile amélioré |
| EPC | Cœur de réseau LTE/4G |
| eNodeB | Station de base LTE |
| eSIM | SIM intégrée et provisionnable selon les procédures prises en charge |
| FDD | Duplexage par séparation fréquentielle |
| gNB | Station de base 5G NR |
| Handover | Transfert de la connexion radio d'une cellule à une autre |
| HSS | Fonction de données d'abonné du cœur EPC |
| IMS | Architecture de services multimédias IP, utilisée notamment pour VoLTE |
| LTE | Long Term Evolution, technologie radio de la 4G courante |
| MIMO | Utilisation de plusieurs antennes pour améliorer robustesse ou capacité |
| mMTC | Communications avec un grand nombre d'équipements de type machine |
| MME | Fonction de contrôle et de mobilité du cœur EPC |
| NR | New Radio, interface radio 5G |
| NSA | Architecture 5G Non-Standalone, dans laquelle la radio 5G dépend d'une architecture combinée incluant LTE et un cœur 4G dans le modèle courant décrit ici |
| P-GW | Passerelle EPC vers les réseaux de données |
| PCF | Fonction de contrôle des politiques du 5GC |
| QoS | Qualité de service |
| RAN | Réseau d'accès radio |
| RSRP | Indicateur de puissance reçue des signaux de référence radio |
| RSRQ | Indicateur de qualité radio LTE/NR selon la mesure considérée |
| SA | Architecture 5G Standalone avec radio NR et cœur 5G dans le modèle SA |
| SINR | Rapport signal utile sur interférences et bruit |
| SMF | Fonction de gestion des sessions dans le 5GC |
| SUCI | Identité d'abonné protégée utilisée dans certains mécanismes 5G |
| TDD | Duplexage par séparation temporelle |
| UE | Équipement utilisateur mobile |
| UPF | Fonction de transfert du plan utilisateur dans le 5GC |
| URLLC | Communications à très faible latence et fiabilité élevée selon des exigences définies |
| VoLTE | Voix sur LTE, généralement avec IMS |
| VoNR | Voix sur NR dans une architecture compatible |

## 44. Vérification des acquis

Tu maîtrises les bases si tu peux répondre sans aide aux questions suivantes :

- Quelle différence existe entre le réseau d'accès radio et le cœur de réseau ?
- Quel est le rôle d'un eNodeB par rapport à celui d'un gNB ?
- À quoi servent MME, S-GW et P-GW en 4G ?
- À quoi servent AMF, SMF et UPF en 5G ?
- Quelle différence fondamentale existe entre NSA et SA ?
- Pourquoi le RSRP ne suffit-il pas à prédire le débit ?
- Pourquoi un téléphone peut-il afficher 5G alors qu'une application ne fonctionne pas ?
- Quelles sont les limites d'une mesure ping ?
- Comment distinguer une couverture insuffisante d'une congestion probable ?
- Pourquoi faut-il valider la QoS, la sécurité et la disponibilité avant de déployer un service industriel ?

## 45. Conclusion

Les réseaux mobiles associent la radio, le transport, le cœur de réseau, la gestion des abonnés et les services applicatifs. La 4G LTE repose sur l'E-UTRAN et l'EPC ; la 5G introduit NR et, dans l'architecture SA, le 5GC avec des fonctions comme AMF, SMF et UPF.

Pour diagnostiquer correctement un incident, il faut distinguer le signal radio, la qualité de réception, la charge, l'établissement de la session, le transport et le service distant. Pour concevoir un bon réseau, il faut définir les besoins, mesurer les performances, valider les limites et superviser l'ensemble de la chaîne.

La prochaine étape du parcours peut approfondir la planification radio, les interfaces du cœur EPC/5GC, la mobilité, la QoS, les réseaux privés 5G et l'exploitation des KPI avec davantage de calculs et de scénarios de configuration.

## Références techniques

Les documents ci-dessous permettent d'approfondir les notions du cours. Certaines spécifications sont longues et s'adressent aux ingénieurs réseau ; les pages d'introduction sont plus accessibles pour commencer.

1. **3GPP — Portail officiel des spécifications** : https://www.3gpp.org/specifications-technologies/specifications-by-series
2. **3GPP TS 23.501 — System architecture for the 5G System (5GS)**, spécification d'architecture du cœur 5G. Une version Release 18 est disponible sur le site ETSI : https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/18.10.00_60/ts_123501v181000p.pdf
3. **3GPP — Fiche de la spécification 23.501** : https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3144
4. **GSMA — 5G Standalone Networks** : https://www.gsma.com/solutions-and-impact/technologies/networks/5g-network-technologies-and-solutions/5g-standalone-networks/
5. **GSMA — 5G Implementation Guidelines** : https://www.gsma.com/solutions-and-impact/technologies/networks/wp-content/uploads/2019/03/5G-Implementation-Guideline-v2.0-July-2019.pdf
6. **ITU — IMT-2020 (5G)** : https://www.itu.int/en/ITU-R/study-groups/rsg5/rwp5d/imt-2020/pages/default.aspx
7. **ITU-R — Report M.2412, lignes directrices d'évaluation des technologies radio IMT-2020** : https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-M.2412-2017-PDF-E.pdf
8. **ETSI — Répertoire des spécifications E-UTRA/E-UTRAN, série 36.300** : https://www.etsi.org/deliver/etsi_ts/136300_136399/
9. **ETSI — Spécification 3GPP TS 38.101-2 relative aux fréquences NR FR2** : https://www.etsi.org/deliver/etsi_ts/138100_138199/13810102/16.11.00_60/ts_13810102v161100p.pdf

Les normes sont périodiquement révisées. Pour un déploiement réel, il faut consulter la version applicable des spécifications 3GPP/ETSI, les exigences réglementaires nationales et la documentation du fournisseur d'équipements.
