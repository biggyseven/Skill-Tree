# Téléphonie IP CUCM — Expert

## Mise en contexte : concevoir une plateforme voix qui reste exploitable en situation réelle

Dans une architecture d'entreprise, Cisco Unified Communications Manager (CUCM) n'est pas simplement un serveur qui associe un téléphone à une extension. Il participe à une chaîne de services comprenant l'identité de l'utilisateur, le plan de numérotation, les autorisations d'appel, la signalisation SIP, la négociation des médias, la qualité de service, la sécurité des terminaux, la connectivité au réseau téléphonique public et la continuité d'activité.

Au niveau expert, la difficulté n'est plus seulement de faire fonctionner un appel. Il faut savoir concevoir une architecture maintenable, anticiper les défaillances, diagnostiquer les appels à partir de preuves, mesurer l'impact d'une modification et limiter le risque de régression.

Ce cours prolonge les niveaux Débutant et Intermédiaire. Il prend comme fil conducteur une entreprise fictive, **NovaTel**, répartie sur plusieurs sites et utilisant CUCM, des téléphones IP, des passerelles ou un Cisco Unified Border Element (CUBE), un opérateur SIP, des trunks inter-clusters et des ressources média.

> **Principe d'exploitation :** toute modification de téléphonie doit être préparée, testée, documentée, surveillée et accompagnée d'une procédure de retour arrière. Une configuration qui fonctionne pendant un appel de test n'est pas encore une preuve suffisante de disponibilité, de sécurité ou de capacité.

## 1. Compétences visées

À la fin du cours, tu devras être capable de :

- concevoir une architecture CUCM multi-sites et multi-clusters ;
- choisir une stratégie de routage inter-clusters et d'accès au PSTN ;
- concevoir un dial plan fondé sur E.164, des transformations explicites et des contrôles d'accès vérifiables ;
- analyser un dialogue SIP et distinguer un problème de signalisation d'un problème média ;
- résoudre des problèmes d'interopérabilité au moyen des profils SIP, des scripts de normalisation et des profils de transparence SDP lorsque cela est justifié ;
- dimensionner et vérifier les ressources média, la bande passante et le Call Admission Control (CAC) ;
- concevoir une stratégie réaliste de résilience, de sauvegarde et de reprise ;
- renforcer la sécurité des terminaux, des trunks, des certificats et des accès d'administration ;
- diagnostiquer une panne avec RTMT, les traces SDI/SDL, les journaux, les CDR/CMR et des tests reproductibles ;
- préparer une maintenance ou une mise à niveau avec critères d'entrée, critères de sortie et plan de retour arrière.

## 2. Prérequis et périmètre

On suppose que tu maîtrises déjà : les extensions et téléphones IP, les Device Pools, les régions et locations, les partitions et Calling Search Spaces (CSS), les route patterns, les route lists et route groups, les trunks SIP, SRST, les codecs, RTP, QoS et les principes de TLS/SRTP.

Les noms de menus et les fonctions disponibles peuvent varier selon la version de CUCM, le type de terminal, les licences, la topologie et les options activées. Les chemins cités sont alignés principalement sur la documentation CUCM 15. Vérifie toujours la documentation exacte de la version déployée avant une modification en production.

Les configurations et numéros d'exemple de ce cours sont fictifs. Ne copie jamais une configuration de laboratoire vers la production sans revue d'architecture, validation des exigences réglementaires, tests et approbation de changement.

## 3. Architecture de référence de NovaTel

NovaTel utilise deux sites principaux et plusieurs agences. Le cluster CUCM central est composé d'un Publisher et de deux Subscribers de traitement des appels. Les téléphones de chaque site disposent d'une liste de serveurs de secours. Les appels vers le PSTN passent par deux chemins SIP distincts via des CUBE, avec des trunks inter-clusters pour les appels internes entre deux entités.

```text
                         Opérateur SIP A     Opérateur SIP B
                               |                   |
                              CUBE-A              CUBE-B
                                 \                 /
                                  \               /
                              +-----------------------+
                              | Cluster CUCM principal |
                              | Publisher              |
                              | Subscriber A           |
                              | Subscriber B           |
                              +-----------------------+
                                  |               |
                           Campus central     Agences WAN
                                  |               |
                         Téléphones IP       Téléphones IP
                                  |
                    Unity Connection / Expressway / CTI
                    (selon les services réellement déployés)
```

### 3.1 Rôle des composants

| Composant | Rôle principal | Point de vigilance expert |
|---|---|---|
| CUCM Publisher | Référence de configuration et de base de données du cluster selon l'architecture | Protéger l'accès administratif, surveiller la réplication et sauvegarder le cluster |
| CUCM Subscriber | Traitement des appels et services selon les rôles activés | Vérifier capacité, services actifs, redondance et affectation des terminaux |
| TFTP | Distribution de fichiers de configuration et de micrologiciels pris en charge | Vérifier DHCP option, adresses TFTP, certificats et accessibilité réseau |
| CUBE ou passerelle voix | Interconnexion SIP/PSTN, contrôle de bordure et médias selon la conception | Éviter les routes ouvertes, vérifier les codecs, les ACL, les certificats et les limites de sessions |
| Unity Connection | Messagerie vocale et fonctions associées | Vérifier ports de messagerie, MWI, intégration téléphonique et capacité |
| Expressway | Accès distant ou interconnexion de collaboration selon la solution | Vérifier certificats, zones, traversal et règles de sécurité spécifiques |
| Ressource média | Conférence, MTP, transcodage ou annonces selon la fonction | Ne pas supposer que CUCM transporte lui-même le flux RTP |
| RTMT | Surveillance et collecte de traces | Collecter des données ciblées, pendant une fenêtre définie, puis revenir au niveau de trace habituel |

### 3.2 Signalisation et médias : deux plans à séparer

La signalisation décrit l'établissement, la modification et la fin d'un appel. Le média transporte la voix ou la vidéo. Ils peuvent emprunter des chemins différents.

```text
Téléphone A ---- SIP ---- CUCM ---- SIP ---- Téléphone B
      \                                  /
       \--------------- RTP -------------/

Autre scénario :
Téléphone A ---- RTP ---- MTP / Transcoder ---- RTP ---- Téléphone B
```

Dans le premier scénario, CUCM contrôle l'appel mais les téléphones échangent directement le RTP si l'architecture et la négociation le permettent. Dans le second, une ressource média est insérée pour satisfaire une exigence, par exemple une incompatibilité de média ou un besoin d'ancrage. L'insertion d'une ressource peut changer la consommation de bande passante et les symptômes de dépannage.

**Conséquence opérationnelle :** un appel peut être connecté du point de vue SIP tout en n'ayant aucun son, un son unidirectionnel ou une qualité dégradée. Le diagnostic doit examiner séparément la signalisation, le SDP, le routage IP, les ACL, le NAT, le RTP/SRTP et la QoS.

## 4. Concevoir une architecture multi-cluster

Le choix du modèle multi-cluster découle du besoin métier, de la latence, du nombre de sites, de la gouvernance, de la tolérance aux pannes et des limites de capacité. Il ne doit pas être guidé uniquement par le nombre de téléphones.

### 4.1 Un cluster central ou plusieurs clusters

Un cluster central simplifie souvent la normalisation et l'administration, mais il concentre davantage les dépendances. Plusieurs clusters peuvent isoler les domaines de panne ou répondre à des contraintes géographiques et organisationnelles, au prix d'une complexité de routage, de certificats, de numérotation et de supervision plus élevée.

Avant de décider, documente :

1. le nombre de terminaux, de sessions et de sites ;
2. les délais de signalisation acceptables et les liaisons inter-sites ;
3. les objectifs RTO et RPO définis par l'entreprise ;
4. les fonctions devant survivre à une panne WAN ;
5. le plan de numérotation, les numéros d'urgence et les politiques d'appel ;
6. la capacité des serveurs, licences et ressources médias ;
7. la stratégie d'exploitation, de sauvegarde, de mise à niveau et de reprise.

### 4.2 Intercluster SIP, ILS et Global Dial Plan Replication

Un trunk SIP inter-cluster permet de transporter la signalisation entre des clusters. Intercluster Lookup Service (ILS) et Global Dial Plan Replication (GDPR), lorsqu'ils sont pertinents et pris en charge par la conception, peuvent faciliter l'échange de destinations et de numéros globalisés. Ils ne remplacent ni les politiques de routage, ni les CSS/partitions, ni les contrôles de sécurité.

Principes de conception :

- définir une autorité claire pour les plages de numéros ;
- utiliser une représentation globale cohérente, généralement basée sur E.164, tout en conservant les besoins locaux ;
- éviter que plusieurs clusters annoncent de manière ambiguë la même destination ;
- prévoir les transformations nécessaires à l'entrée et à la sortie de chaque domaine ;
- contrôler les CSS associées aux trunks et les partitions des patterns appris ou créés ;
- mesurer le nombre de sessions et le comportement en cas de perte d'un trunk ;
- décider explicitement si les appels doivent être hairpinés par un cluster central ou sortir localement.

### 4.3 Session Management Edition

Cisco Unified Communications Manager Session Management Edition (SME) peut servir de couche centrale de contrôle des appels pour relier des clusters régionaux ou des domaines de téléphonie. Une telle architecture peut centraliser certaines politiques, mais augmente l'importance de la capacité, de la haute disponibilité, du routage alternatif et de la maîtrise des dépendances.

Ne déploie pas SME comme simple raccourci pour éviter de concevoir le dial plan. Il faut d'abord définir les domaines de numérotation, les trunks, les transformations, les classes d'appels, le contrôle des sessions et les scénarios de panne.

## 5. Dial plan expert : normalisation, autorisation et routage

Un dial plan robuste sépare trois questions : **quel numéro a été composé**, **cet appel est-il autorisé**, et **par quel chemin doit-il sortir**. Mélanger ces responsabilités dans des transformations multiples et implicites rend le dépannage difficile.

### 5.1 Stratégie de numérotation normalisée

Exemple de plan fictif :

| Domaine | Extensions locales | Présentation globale fictive |
|---|---|---|
| Siège | 2XXX | +237 22 00 2XXX |
| Agence Nord | 3XXX | +237 22 00 3XXX |
| Agence Sud | 4XXX | +237 22 00 4XXX |
| Service client | 5XXX | +237 22 00 5000 |

Les préfixes et numéros de cet exemple sont pédagogiques et ne décrivent pas un plan de numérotation réel à utiliser sans vérification. Les règles nationales, les numéros d'urgence et les obligations de présentation d'identité doivent être validés localement.

L'approche recommandée est de définir une représentation interne canonique, souvent E.164, puis d'appliquer des transformations aux frontières où une autre représentation est nécessaire. Les numéros doivent être testés dans les deux sens : appelé et appelant.

### 5.2 CSS et partitions : reconstruire le chemin de décision

Le Calling Search Space (CSS) détermine les partitions accessibles par le dispositif ou l'objet de routage. Une partition donne un domaine logique aux patterns. Le fait qu'un pattern existe ne signifie donc pas que chaque téléphone peut l'utiliser.

Pour diagnostiquer un appel, reconstruis cette chaîne dans l'ordre :

1. numéro composé et chiffres effectivement reçus ;
2. objet qui fait la première correspondance : route pattern, translation pattern, directory number ou autre mécanisme applicable ;
3. partition de cet objet ;
4. CSS effectivement utilisé à ce point du parcours ;
5. éventuelle transformation des chiffres ;
6. nouvel aiguillage et nouvelle décision de routage ;
7. route list, route group, trunk ou passerelle sélectionné ;
8. transformation de l'identité appelante et règles d'opérateur.

Une translation pattern peut modifier le numéro puis faire effectuer une nouvelle recherche de route avec le CSS configuré sur la translation. Ne traite donc pas un CSS comme une permission globale qui s'appliquerait automatiquement à chaque étape.

### 5.3 Exemple de classes d'appel

```text
Téléphone de bureau
   CSS_EMPLOYEE
      ├── PT_INTERNAL      : appels internes autorisés
      ├── PT_LOCAL         : appels locaux autorisés
      └── PT_EMERGENCY     : route d'urgence selon la politique locale

Téléphone invité
   CSS_GUEST
      └── PT_INTERNAL_LIMITED
          (aucune route internationale ni route opérateur générale)
```

Ce schéma est conceptuel. Les numéros d'urgence ne doivent pas être bloqués par une classe d'appel générique et doivent être conçus selon la réglementation, l'emplacement réel et les solutions d'acheminement d'urgence en place.

### 5.4 Patterns concurrents et sélection de route

Des patterns qui se recouvrent peuvent créer des comportements inattendus, notamment lorsque la temporisation interchiffres, les indicateurs de pattern urgent, les transformations ou l'ordre des partitions sont mal compris. Construis une matrice de tests, plutôt que de déduire le résultat à partir du seul texte visible du pattern.

| Numéro composé | Résultat attendu | Test négatif à prévoir |
|---|---|---|
| Extension connue | Appel interne | Extension inexistante |
| Numéro public autorisé | Route opérateur approuvée | Numéro public interdit |
| Numéro international autorisé | Route internationale dédiée | Classe d'appel sans droit international |
| Numéro d'urgence local | Routage conforme au site et à la réglementation | Téléphone déplacé ou télétravail |
| Numéro d'une autre entité | Route intercluster appropriée | Trunk intercluster indisponible |

### 5.5 Réduire le risque de toll fraud

Une mauvaise règle de routage peut autoriser une fraude téléphonique coûteuse. Applique les contrôles suivants :

- CSS du moindre privilège ;
- destinations internationales et numéros surtaxés séparés par classes d'appel ;
- interdiction de routes génériques ouvertes aux terminaux non maîtrisés ;
- restrictions sur les appels entrants capables de provoquer une nouvelle sortie PSTN ;
- authentification, ACL et politiques de sessions sur les trunks et passerelles ;
- alertes sur les volumes, destinations inhabituelles et appels hors horaires ;
- journalisation, CDR et procédures de gel de comptes ou de routes en cas d'incident.

Un test positif n'est pas suffisant : vérifie également qu'un téléphone invité, un téléphone compromis et un trunk externe ne peuvent pas contourner les restrictions.

## 6. SIP avancé et interopérabilité

### 6.1 Lire le dialogue SIP comme une machine à états

Un dialogue typique peut ressembler à ceci :

```text
A                 CUCM / interconnexion                 B
|------ INVITE + SDP ------------------------------->   |
|<----- 100 Trying ---------------------------------   |
|<----- 180 Ringing (ou 183 avec SDP) --------------   |
|<----- 200 OK + SDP -------------------------------   |
|------ ACK ---------------------------------------->   |
|                   RTP / SRTP                       |
|------ BYE ---------------------------------------->   |
|<----- 200 OK -------------------------------------   |
```

Les messages visibles et leur ordre dépendent du scénario. Un appel peut utiliser un SDP précoce ou retardé, une réponse 183 avec annonce de progression, un ancrage média ou des messages supplémentaires dus au transfert, à la conférence ou à l'interopérabilité.

| Réponse ou événement | Lecture opérationnelle habituelle | Vérifications prioritaires |
|---|---|---|
| 100 Trying | La requête est en cours de traitement | Délai de réponse ultérieur, routage et disponibilité de la destination |
| 180 Ringing | La destination signale la sonnerie | État du terminal et progression de l'appel |
| 183 Session Progress | Progression de l'appel, éventuellement avec SDP | Early media, chemin RTP, codec et compatibilité SDP |
| 200 OK | Requête acceptée ; pour INVITE, session établie après la séquence appropriée | SDP, ACK, adresse/port média, RTP/SRTP |
| 403 Forbidden | Refus lié à une politique ou à une autorisation | Configuration de l'appel, autorisations, politique du pair |
| 404 Not Found | Ressource ou destination non reconnue par le serveur répondant | Numéro transmis, routage, URI et contexte de domaine |
| 408 Request Timeout | Expiration d'une attente | Reachability, pare-feu, délai du pair ou chemin réseau |
| 481 Call/Transaction Does Not Exist | Dialogue ou transaction non reconnu | Incohérence de dialogue, état du pair, ALG/SBC ou interopérabilité |
| 488 Not Acceptable Here | Paramètres de session non acceptables | SDP, codecs, média, SRTP, capacités des terminaux |
| 491 Request Pending | Requête concurrente ou état provisoire selon le contexte | Séquence de re-INVITE, transfert ou modification média |
| 503 Service Unavailable | Service indisponible ou surcharge côté répondant | Capacité, santé du serveur, politique de débordement et temporisation |

Ces interprétations sont des points de départ. Le code seul ne donne pas la cause racine. Il faut identifier qui l'a émis, pour quelle requête, dans quel sens et après quel état de dialogue.

### 6.2 SDP, codec et négociation média

Le Session Description Protocol (SDP) décrit notamment les médias proposés, les codecs, les ports, les adresses et les attributs de session. Il est transporté dans les messages SIP concernés.

Extrait pédagogique simplifié :

```text
v=0
c=IN IP4 192.0.2.20
m=audio 18000 RTP/AVP 0 8 9 18
```

Dans cet exemple fictif, les numéros de payload indiquent une liste de formats RTP proposés selon les associations définies par les profils RTP correspondants. Ne déduis pas la compatibilité de deux extrémités uniquement d'une liste de codecs : il faut comparer les directions, les formats réellement négociés, les fréquences d'échantillonnage, les paramètres spécifiques et, le cas échéant, le SRTP.

### 6.3 Early Offer et Delayed Offer

Avec l'**Early Offer**, l'INVITE initial contient un SDP. Avec le **Delayed Offer**, l'offre média peut arriver plus tard dans la transaction, selon le scénario SIP. Les politiques des opérateurs, des SBC, des passerelles et des terminaux peuvent exiger une forme précise.

Méthode de diagnostic :

1. comparer un appel réussi et un appel échoué ;
2. repérer le premier message qui diffère ;
3. relever l'offre et la réponse SDP sans exposer de données sensibles ;
4. vérifier codec, adresse, port, direction média et profil de sécurité ;
5. contrôler si CUCM ou un équipement de bordure modifie ou ancre le SDP ;
6. faire un changement isolé, puis revalider l'appel dans les deux sens.

### 6.4 Profils SIP, Normalization Scripts et SDP Transparency Profiles

Un SIP Profile applique des paramètres communs aux terminaux ou trunks qui lui sont associés. Une normalization script peut modifier certains éléments SIP pour adapter des comportements d'interopérabilité. Un SDP Transparency Profile peut aider dans certains scénarios où les attributs SDP doivent être préservés ou traités d'une manière spécifique.

Règles de prudence :

- identifier d'abord le comportement standard attendu par les deux pairs ;
- préférer un paramétrage natif lorsque cela résout le problème ;
- ne pas ajouter une script de normalisation « au cas où » ;
- documenter chaque modification, son périmètre et la version testée ;
- valider appel entrant, sortant, transfert, mise en attente, reprise, conférence et fax ou média spécialisé s'ils sont utilisés ;
- contrôler les traces après mise à niveau, car le comportement des versions et les fonctions disponibles peuvent évoluer.

Une transformation de signalisation peut corriger un interfonctionnement, mais aussi masquer une mauvaise conception ou rendre le comportement plus difficile à maintenir.

## 7. Contrôle des médias et ressources

### 7.1 Quand insérer une ressource média ?

Les ressources sont consommées pour des fonctions différentes :

- **MTP (Media Termination Point)** : terminaison et traitement de flux média dans des scénarios qui le requièrent ;
- **Transcoder** : conversion entre formats compatibles avec les deux extrémités ;
- **Conference Bridge** : mixage ou traitement d'une conférence ;
- **Annunciator** : annonces audio ;
- **Music on Hold** : musique d'attente, selon le mode et la conception.

Une ressource n'est pas une solution universelle à tout problème de média. L'insertion forcée d'un MTP peut augmenter la charge, imposer un chemin média différent ou affecter certaines capacités. Il faut identifier l'exigence exacte avant de sélectionner une ressource.

### 7.2 Symptômes média et hypothèses à tester

| Symptôme | Hypothèses prioritaires | Preuve à rechercher |
|---|---|---|
| Aucun son dans les deux sens | RTP bloqué, mauvais SDP, mauvaise adresse annoncée, ressource indisponible | SDP négocié, chemin IP, compteurs de flux, capture réseau autorisée |
| Son dans un seul sens | ACL asymétrique, NAT, mauvaise route de retour, adresse/port erroné | Vérifier chaque sens séparément |
| Appel connecté puis coupé | Expiration SIP, perte du dialogue, BYE distant, temporisation réseau ou SBC | Chronologie SIP et identité de l'émetteur du BYE |
| Voix hachée | Perte, gigue, congestion, CPU ou radio/Wi-Fi dégradé | Mesures de perte, jitter, DSCP, interfaces et qualité terminal |
| Aucun codec commun | Politiques de région, capacités des terminaux, paramètres SDP | Comparaison exacte des SDP et des régions |
| Conférence échouée | Ressource indisponible ou incompatible, capacité atteinte | État de la ressource, type de conférence, traces et appels simultanés |

Ne conclus jamais « problème CUCM » uniquement parce que CUCM apparaît dans la chaîne de signalisation. La cause peut se trouver sur le réseau, le terminal, la passerelle, l'opérateur ou une ressource média.

## 8. Qualité de service et contrôle d'admission

### 8.1 Régions et locations ne répondent pas à la même question

Dans CUCM, les **Regions** contribuent notamment à contrôler les codecs et les limites de bande passante pour les appels entre groupes de terminaux. Les **Locations** modélisent la bande passante globale disponible entre sites ou segments pour des appels simultanés. Enhanced Locations Call Admission Control (Enhanced Locations CAC) ajoute un modèle des liens, des poids et du réseau inter-sites, lorsque la fonctionnalité est déployée.

```text
Région HQ  ---- WAN 1 ---- Région AGENCE
    |                           |
  Location HQ                Location AGENCE
    |                           |
  Téléphones                  Téléphones

Regions : caractéristiques média autorisées par appel
Locations/Links : capacité cumulée des appels sur les liens
```

Le CAC peut refuser un appel lorsqu'il ne reste pas assez de bande passante réservée dans le modèle configuré. Ce refus peut être souhaitable : accepter tous les appels tout en saturant le WAN dégrade la qualité de tous les utilisateurs.

### 8.2 Calcul d'ingénierie simplifié

Supposons un lien voix qui réserve 1 024 kbit/s au média et une estimation d'ingénierie de 80 kbit/s par appel G.711 dans chaque sens pour le modèle étudié. La capacité arithmétique est :

\[
N = \left\lfloor \frac{1024}{80} \right\rfloor = 12\text{ appels}
\]

Ce résultat est une estimation simplifiée, non une valeur universelle : l'overhead de couche 2/3, le mode de calcul de CUCM, le type de média, les réserves, la vidéo, la signalisation et la capacité réelle du lien doivent être pris en compte. Les valeurs de régions et locations doivent correspondre au modèle de bande passante retenu par l'exploitation.

### 8.3 DSCP et politique réseau

La QoS fonctionne de bout en bout seulement si les marquages sont cohérents et que chaque équipement sur le chemin applique une politique compatible. Les classes habituelles distinguent le média voix, le média vidéo, la signalisation et les flux de données. Les valeurs DSCP, les files et les réserves doivent être alignées sur la politique de l'entreprise et les capacités réseau.

Points à vérifier :

- le marquage effectué par le téléphone et les ressources média ;
- la préservation ou la modification de DSCP sur les commutateurs, routeurs, VPN et WAN ;
- la classification d'un appel avant et après une passerelle ou un SBC ;
- les files de priorité et leurs limites ;
- l'absence de sur-priorisation qui affamerait les autres flux ;
- les mesures de perte, délai et gigue pendant la congestion.

Les seuils de délai, de gigue et de perte doivent être définis par le service et mesurés de bout en bout. Ne traite pas une valeur générique comme garantie universelle de qualité.

### 8.4 Enhanced Locations CAC : déploiement prudent

Avant d'activer cette fonction à grande échelle :

1. représenter les sites et liens WAN réels ;
2. confirmer les capacités voix/vidéo qui doivent être réservées ;
3. vérifier les poids et chemins possibles ;
4. activer et superviser Location Bandwidth Manager (LBM) selon la conception ;
5. tester les appels avec bande passante suffisante et les appels excédentaires ;
6. tester une panne de lien et une topologie dégradée ;
7. surveiller l'état de réplication inter-clusters si elle est utilisée.

Le modèle de CAC ne remplace pas la supervision du WAN : pendant une panne réseau, sa topologie peut ne pas refléter parfaitement les conditions réelles. Utilise des allocations conservatrices et une stratégie de test documentée.

## 9. Sécurité avancée

### 9.1 Protéger les plans de contrôle et de média

La sécurité doit couvrir les interfaces d'administration, les fichiers de configuration des téléphones, les certificats, la signalisation, le média et les interconnexions. TLS protège la signalisation SIP lorsqu'il est correctement configuré ; SRTP protège le média lorsqu'il est négocié et pris en charge par les deux extrémités. L'un ne garantit pas automatiquement l'autre.

Contrôles clés :

- comptes nominatifs et droits minimaux ;
- accès d'administration limité aux réseaux de gestion ;
- mots de passe et secrets uniques, rotation contrôlée et stockage sécurisé ;
- certificats non expirés, noms et chaînes de confiance cohérents ;
- profils de sécurité adaptés aux terminaux et trunks ;
- TLS/SRTP activés selon l'interopérabilité et le modèle de sécurité ;
- séparation des réseaux voix, données et gestion ;
- ACL strictes, contrôle des ports et supervision des accès ;
- collecte de journaux, horodatage NTP fiable et procédure d'incident ;
- tests de compatibilité avant le renouvellement de certificats ou un passage en mode de sécurité plus strict.

### 9.2 ITL, CTL, CAPF et certificats

Les téléphones Cisco peuvent s'appuyer sur des mécanismes de confiance tels que ITL, CTL et CAPF selon le mode de sécurité et la version. Les certificats des services CUCM et des trunks peuvent être impliqués dans l'authentification et le chiffrement. Une régénération mal planifiée peut perturber l'enregistrement des terminaux, l'intégration d'applications ou la confiance entre clusters.

Avant toute opération sur les certificats :

1. inventorier les certificats, usages, dates d'expiration et dépendances ;
2. vérifier les noms, SAN, autorités de certification et confiance des pairs ;
3. consulter le guide de sécurité de la version installée ;
4. planifier l'ordre des changements et les redémarrages requis ;
5. prévoir l'actualisation CTL/ITL ou la procédure de récupération pertinente ;
6. valider un petit groupe pilote avant le déploiement général ;
7. effectuer une sauvegarde DRS conforme avant et après la modification lorsque cela s'applique ;
8. vérifier l'enregistrement, les trunks, les applications et les appels chiffrés après le changement.

La régénération d'un certificat n'est pas une action de dépannage anodine. Ne la réalise pas au hasard pour résoudre un appel isolé.

### 9.3 TLS/SRTP et limites de confiance

Un trunk SIP chiffré protège le segment de signalisation couvert par la session TLS, mais ne signifie pas que tous les segments du parcours sont chiffrés. De même, SRTP ne protège pas un média qui quitte ensuite le périmètre sous une forme non chiffrée. Documente les frontières de confiance : CUCM vers CUBE, CUBE vers opérateur, intercluster, médias de conférence, télétravail et réseaux partenaires.

La validation doit confirmer le mode de sécurité négocié, la chaîne de certificats, les suites cryptographiques disponibles dans la version, l'état SRTP effectif et l'impact sur l'interopérabilité. Ne prétends pas qu'un appel est « chiffré de bout en bout » sans prouver chaque segment et chaque point d'ancrage média.

### 9.4 Réduire les risques d'abus d'appel

Revois périodiquement les CSS, les route patterns, les appels entrants pouvant ressortir vers le PSTN, les identités de présentation, les restrictions des gateways et les politiques des CUBE. Ajoute des alertes sur les volumes anormaux, les destinations inhabituelles, les appels longs hors horaires et les changements inattendus du plan de numérotation.

En cas de suspicion de fraude : préserver les preuves, limiter l'exposition en appliquant un contrôle ciblé, identifier les appels et les comptes concernés, rechercher le chemin de routage réel et documenter les changements. Évite les modifications massives qui effaceraient les indices ou provoqueraient une panne générale.

## 10. Haute disponibilité, continuité et reprise

### 10.1 Comprendre la portée de la redondance

Un cluster CUCM peut distribuer le traitement des appels sur plusieurs nœuds et fournir des chemins de repli aux terminaux. Cela ne signifie pas que chaque fonction est disponible sans interruption : les applications, passerelles, opérateurs SIP, ressources médias, DNS, NTP, WAN et services d'annuaire ont leurs propres dépendances.

Pour chaque composant, définis :

- le mode de redondance ;
- le comportement observé lors d'une panne ;
- le nombre d'appels existants qui restent actifs ou sont interrompus ;
- le délai avant retour au service ;
- les fonctions qui deviennent indisponibles ;
- les alarmes et la procédure d'escalade ;
- les critères de restauration à l'état nominal.

### 10.2 SRST et survivabilité du site distant

Sur un site distant, SRST peut permettre à des téléphones compatibles de conserver certaines fonctions d'appel lorsque la connexion au traitement central est perdue et que l'architecture a été préparée pour cela. La portée réelle dépend du modèle de téléphone, de la passerelle, de la version, des fonctions et de la configuration. Les transferts, conférences, messageries, numéros d'urgence et fonctions avancées peuvent se comporter différemment pendant la survivabilité.

Plan de test SRST :

1. vérifier les paramètres de repli du Device Pool et la connectivité à la passerelle ;
2. documenter les fonctions attendues en mode normal et en mode dégradé ;
3. simuler une perte WAN uniquement dans un environnement autorisé ;
4. tester appels internes locaux, sortants autorisés et appels d'urgence selon une procédure de test approuvée ;
5. vérifier les annonces, l'identité appelante et le routage des appels entrants disponibles ;
6. restaurer le lien et observer le retour des téléphones au mode normal ;
7. vérifier qu'aucune route temporaire ni règle de test n'est restée active.

N'effectue jamais un test d'appel d'urgence réel sans coordination avec les responsables et autorités concernés. Utilise les procédures de test officiellement prévues dans la zone concernée.

### 10.3 DRS, RTO et RPO

Le Disaster Recovery System (DRS) réalise des sauvegardes du cluster selon les fonctions et composants pris en charge. Les sauvegardes sont chiffrées et doivent être restaurées par le mécanisme prévu, pas manipulées comme de simples fichiers de configuration.

- **RTO (Recovery Time Objective)** : durée maximale visée pour rétablir le service.
- **RPO (Recovery Point Objective)** : perte maximale de données acceptable, exprimée en durée.

La réussite d'une sauvegarde n'est pas la preuve que l'on peut restaurer rapidement. Il faut tester le processus de restauration dans un environnement contrôlé, respecter les conditions de version et de plateforme documentées par Cisco, et vérifier après restauration la réplication, les certificats, les trunks, les terminaux, les applications et les licences.

### 10.4 Plan de reprise vérifiable

Un plan de reprise expert contient :

1. inventaire des serveurs, versions, dépendances et certificats ;
2. procédures et contacts d'escalade ;
3. emplacement et protection des sauvegardes ;
4. conditions préalables à la restauration ;
5. ordre de restauration validé par la documentation officielle ;
6. tests fonctionnels par service ;
7. mesures RTO/RPO réellement observées ;
8. approbation de retour en production ;
9. compte rendu et actions d'amélioration.

## 11. Planification d'une maintenance et d'une mise à niveau

### 11.1 Préparation du changement

Avant une modification de dial plan, un renouvellement de certificats ou une mise à niveau, prépare un dossier de changement contenant :

- objectif et périmètre ;
- version source et version cible, matrice de compatibilité et prérequis ;
- sauvegarde DRS vérifiée ;
- état de santé initial du cluster ;
- liste des services et intégrations concernés ;
- scénario de validation, résultats attendus et personnes responsables ;
- risques, fenêtre de maintenance, plan de communication ;
- procédure d'arrêt ou de retour arrière autorisée ;
- critères mesurables de succès et de retour arrière.

### 11.2 Vérifications avant intervention

Exemples de contrôles de santé à réaliser dans la version et la topologie concernées :

- synchronisation NTP et résolution DNS ;
- état de réplication de base de données ;
- état des services CallManager, TFTP et autres services nécessaires ;
- capacité CPU, mémoire, disque et alertes système ;
- enregistrement des terminaux et statut des trunks ;
- appels entrants, sortants, internes, transferts, conférences et messagerie ;
- disponibilité des gateways, CUBE et opérateurs ;
- dates d'expiration des certificats ;
- état des sauvegardes et disponibilité des procédures de restauration.

### 11.3 Validation après intervention

Ne te contente pas d'un ping ou de l'accès à l'interface web. Vérifie :

- l'état des nœuds et de la réplication ;
- le statut des services et les alarmes ;
- l'enregistrement de téléphones représentatifs de chaque modèle et site ;
- appels internes, PSTN entrants/sortants, transferts, mise en attente, conférence et messagerie ;
- présentation et normalisation du numéro appelant ;
- média bidirectionnel, tonalités, DTMF, codecs, SRTP lorsque requis ;
- fonctionnement des sites de secours et des chemins alternatifs conformément au plan de test ;
- CDR et traces pour confirmer que les appels ont emprunté la route attendue.

Si une validation échoue, stoppe l'élargissement du changement, conserve les traces et applique le plan de décision convenu. Ne fais pas plusieurs corrections indépendantes en même temps : cela détruit la capacité à identifier le facteur causal.

## 12. Dépannage avancé fondé sur des preuves

### 12.1 Une méthode reproductible

Pour chaque incident, consigne :

1. heure exacte avec fuseau et source NTP ;
2. appelant, appelé, site, terminal et version ;
3. sens de l'appel et numéro composé ;
4. étape d'échec observable ;
5. fréquence et périmètre du problème ;
6. dernier changement connu ;
7. résultat attendu et résultat mesuré ;
8. identifiants et traces associés, en masquant les données sensibles.

Utilise ensuite une séquence de diagnostic qui réduit progressivement le périmètre : terminal, plan de numérotation, traitement CUCM, trunk/gateway, réseau, pair distant et média.

### 12.2 Outils de vérification

Selon la version et les permissions, les outils suivants peuvent être utilisés. Les commandes CLI doivent être exécutées avec un accès autorisé et uniquement en lecture lorsqu'elles servent au diagnostic. Vérifie la syntaxe prise en charge dans la version installée.

| Outil ou commande | Utilisation | Précaution |
|---|---|---|
| `show status` | État synthétique de la plateforme | Comparer avec les alertes et mesures historiques |
| `show network cluster` | Informations réseau et membres du cluster selon version | Vérifier les IP, noms et cohérence DNS |
| `utils ntp status` | État de synchronisation horaire | Les horodatages incohérents compliquent la corrélation |
| `utils dbreplication runtimestate` | État courant de la réplication DB | Examiner tous les nœuds et la stabilité, pas un seul instantané |
| `utils dbreplication status` | Vérification détaillée de la réplication | Peut solliciter le système ; suivre les recommandations de la version |
| `utils service list` | Services et états | Le service requis varie selon la fonction examinée |
| RTMT / Trace and Log Central | Collecte des traces SDI/SDL et journaux pris en charge | Activer les traces détaillées uniquement pendant une fenêtre nécessaire |
| CDR Analysis and Reporting (CAR) | Analyse des enregistrements d'appels selon configuration | Contrôler les droits d'accès et la conservation des données |

Les commandes exactes, leur portée et les opérations potentiellement consommatrices de ressources varient. N'exécute pas de commande destructive ou de remise à zéro de réplication uniquement parce qu'un guide de laboratoire la mentionne : lis d'abord la procédure officielle correspondant à la version et collecte l'état initial.

### 12.3 Traces SDI et SDL

Les traces peuvent aider à reconstruire le chemin de signalisation et le traitement de l'appel. RTMT permet de configurer et collecter différents types de traces, dont SDI et SDL pour les services CUCM concernés. Un niveau de trace élevé peut dégrader les performances ou produire un volume important de données : active-le pour une investigation limitée, avec une heure de début et de fin connue.

Méthode recommandée :

1. reproduire un seul appel identifié ;
2. collecter les traces sur les nœuds qui ont traité l'appel ;
3. aligner les horodatages grâce à NTP ;
4. chercher la première divergence par rapport à un appel réussi ;
5. suivre les identifiants de transaction et de dialogue pertinents ;
6. corréler avec la trace du trunk ou de la passerelle ;
7. réduire le diagnostic à une hypothèse vérifiable ;
8. désactiver les traces temporaires et archiver les résultats selon la politique de l'entreprise.

Ne partage pas des traces sans contrôle : elles peuvent contenir des numéros, des adresses IP, des identifiants et des informations opérationnelles sensibles.

### 12.4 CDR/CMR et qualité d'appel

CDR décrit les informations d'enregistrement d'un appel et CMR peut apporter des informations de mesure liées au média selon les terminaux, la configuration et la collecte activée. Ces données contribuent à l'analyse de tendances et à la corrélation avec les incidents, mais n'offrent pas nécessairement la totalité des mesures réseau ni une preuve complète de la cause racine.

Exemples d'analyse :

- comparer les appels affectés à ceux qui réussissent ;
- rechercher une corrélation avec un site, un codec, un trunk ou une plage horaire ;
- mesurer le taux de succès, la durée et les motifs de fin d'appel ;
- vérifier les modifications de configuration et les changements de route ;
- croiser avec les métriques WAN et les événements des passerelles.

Protège les enregistrements d'appels, limite leur consultation aux personnes habilitées et respecte la politique locale de conservation des données.

## 13. Cas de dépannage expert

### Cas A : appel établi mais silence dans les deux sens

Hypothèses possibles : adresse média incorrecte, flux RTP bloqué, ressources média mal sélectionnées, SRTP incompatible ou chemin de routage asymétrique.

Procédure : comparer le SDP aux deux extrémités ; confirmer adresse IP et port négociés ; vérifier la portée du pare-feu et les ACL ; confirmer si le média est direct ou ancré ; vérifier le codec et le mode SRTP ; comparer avec un appel réussi entre les mêmes réseaux.

**Ne pas faire :** forcer immédiatement un MTP sur tous les trunks. L'ancrage peut masquer le problème et ajouter une nouvelle dépendance.

### Cas B : seuls les appels internationaux échouent

Hypothèses : CSS ne donnant pas accès à la bonne partition, route pattern trop spécifique ou mal priorisé, transformation de chiffres incorrecte, restriction opérateur, identité appelante rejetée ou politique anti-fraude.

Procédure : relever le numéro composé ; reconstruire la suite des patterns et CSS ; vérifier les chiffres émis vers le CUBE/opérateur ; lire la réponse SIP exacte ; comparer un appel autorisé et un appel refusé ; faire un test négatif avec une classe d'appel qui ne doit pas autoriser l'international.

**Ne pas faire :** ajouter une route générique qui autorise toutes les destinations. La correction peut ouvrir une faille de toll fraud.

### Cas C : appel transféré échoué alors que les appels simples fonctionnent

Hypothèses : changement de dialogue SIP, nouveau routage après transfert, identité appelante ou URI transférée, interaction entre Early/Delayed Offer, média réinvité, ou comportement du pair distant.

Procédure : capturer l'appel simple et le transfert ; repérer REFER et/ou re-INVITE selon le scénario ; inspecter les codes de réponse ; vérifier les CSS utilisées lors de la nouvelle route et les règles de présentation ; reproduire avec un transfert interne puis externe.

### Cas D : téléphone incapable de s'enregistrer après changement de certificat

Hypothèses : chaîne de confiance ou certificat modifié, ITL/CTL, service TFTP, horloge, fichier de configuration, confiance du téléphone ou procédure de renouvellement incomplète.

Procédure : collecter le message exact du téléphone ; vérifier dates, chaîne et certificat du service ; contrôler la santé TFTP et les services associés ; vérifier la procédure officielle de mise à jour de confiance correspondant au modèle et au mode de sécurité ; tester un téléphone pilote. Ne pas effacer les fichiers de confiance ou régénérer plusieurs certificats à l'aveugle.

### Cas E : appels dégradés uniquement aux heures de pointe

Hypothèses : congestion WAN, queue de priorité surchargée, marquage DSCP perdu, Wi-Fi saturé, liens sous-dimensionnés, ressource média à capacité atteinte ou modèle CAC incorrect.

Procédure : corréler heures d'appel et métriques réseau ; comparer perte, gigue, délai et DSCP aux différents segments ; vérifier les files de sortie et les erreurs interface ; observer le nombre de sessions de ressources ; examiner le modèle Regions/Locations/CAC ; proposer une correction mesurée puis refaire le test sous charge.

## 14. Travaux pratiques guidés

Tous les noms, numéros, IP et valeurs suivants sont fictifs. Réalise les TP dans un environnement de laboratoire ou une maquette approuvée, pas en production. L'objectif est de vérifier le raisonnement, pas de recopier des valeurs sans comprendre leur portée.

### TP 1 — Revue de conception multi-sites

**Objectif :** proposer une architecture résiliente pour trois sites.

Données :
- Siège HQ : 300 téléphones ;
- Agence Nord : 80 téléphones sur WAN ;
- Agence Sud : 60 téléphones sur WAN ;
- deux chemins d'accès au PSTN au siège ;
- exigences : appels internes entre sites, appels PSTN, survivabilité limitée des agences.

**Travail demandé :**

1. dessiner les composants et les flux de signalisation/média ;
2. déterminer quels sites appartiennent au même cluster ou à des clusters différents, en justifiant ;
3. indiquer les chemins PSTN normaux et de secours ;
4. écrire les scénarios de panne : perte d'un Subscriber, perte WAN, perte d'un CUBE, perte d'un opérateur ;
5. définir les tests et les limites fonctionnelles en mode dégradé.

**Correction indicative :**

Il n'existe pas de réponse unique. Une bonne proposition explique les raisons du choix de cluster, le rôle des serveurs de traitement, le comportement des téléphones lors du basculement, la survivabilité locale, les chemins PSTN indépendants et les limites de la messagerie ou des fonctions avancées lorsque le WAN est perdu. Elle différencie les composants redondés des services qui restent des points uniques de défaillance. La conclusion doit inclure un plan de test mesurable plutôt qu'une simple mention « haute disponibilité ».

### TP 2 — Diagnostic d'une route internationale refusée

**Objectif :** isoler un problème de dial plan sans affaiblir la sécurité.

Contexte fictif : l'extension 2201 appelle les extensions internes et les numéros nationaux, mais l'appel international échoue. L'extension 2301, appartenant à un groupe différent, passe un appel international de test approuvé.

**Travail demandé :**

1. comparer les CSS des deux téléphones ;
2. identifier la partition du route pattern international ;
3. vérifier les transformations du numéro appelé et du numéro appelant ;
4. déterminer si CUCM sélectionne une route ou si le CUBE/opérateur rejette la session ;
5. proposer un test positif et deux tests négatifs.

**Correction :**

Commence par prouver que le CSS du téléphone 2201 ne permet pas l'accès à la partition requise, ou bien que la règle de transformation ne produit pas le format attendu. Si le routage parvient au CUBE, inspecte la réponse SIP et les chiffres envoyés à l'opérateur. Applique une correction limitée à la classe d'appel prévue. Les tests négatifs doivent confirmer qu'un utilisateur non autorisé reste bloqué et qu'un numéro malformé ne part pas vers une route générale.

### TP 3 — Appel connecté sans média

**Objectif :** séparer signalisation et médias.

Données fictives : SIP se termine par 200 OK et ACK, mais l'appelant n'entend pas le correspondant. Un appel interne dans le même site fonctionne.

**Travail demandé :**

1. analyser les messages SIP ;
2. comparer le SDP des deux extrémités ;
3. identifier si le RTP est direct ou passe par une ressource ;
4. vérifier ACL, routes et NAT éventuels ;
5. lister les preuves qui permettraient de confirmer la cause.

**Correction :**

Le 200 OK/ACK montre que la session de signalisation a progressé, pas que le média fonctionne. Relever les adresses et ports média annoncés et vérifier que chacun est joignable depuis l'autre côté. Si l'appel traverse un CUBE, examiner les flux de chaque jambe séparément. Vérifier SRTP et le codec en même temps que le routage IP. Une capture ou un compteur de flux, obtenus selon les procédures autorisées, apporte une preuve plus forte qu'une simple hypothèse sur le pare-feu.

### TP 4 — Réduire les risques avant un renouvellement de certificats

**Objectif :** préparer un changement de confiance sans interrompre les terminaux.

**Travail demandé :**

1. créer un inventaire des certificats, usages, expiration et systèmes pairs ;
2. définir le groupe pilote ;
3. établir les tests d'enregistrement, trunks TLS, SRTP et applications ;
4. prévoir sauvegarde et procédure de retour arrière autorisée ;
5. fixer les critères de succès et d'arrêt.

**Correction :**

Le plan doit inclure l'ordre des certificats dépendants, la compatibilité des pairs, les opérations de redémarrage exigées par la version, la mise à jour de la confiance des téléphones lorsque nécessaire et une sauvegarde valide. Le groupe pilote doit couvrir les modèles de terminaux et les fonctions réellement utilisés. Un certificat expiré n'est pas nécessairement la seule cause d'un échec TLS : le nom, la chaîne, l'horloge et le profil du trunk doivent aussi être vérifiés.

### TP 5 — Mesurer les effets d'une modification de CAC

**Objectif :** comprendre les effets d'un modèle de bande passante sur les appels.

Données : un lien WAN fictif dispose de 512 kbit/s alloués au modèle voix. La politique de laboratoire réserve 80 kbit/s par appel pour l'exercice. Le site veut aussi conserver une marge pour les variations et les autres médias.

**Travail demandé :**

1. calculer le maximum arithmétique théorique ;
2. proposer une limite opérationnelle plus prudente ;
3. préciser les tests nécessaires avant et après le changement ;
4. distinguer la capacité du CAC de la capacité physique du lien.

**Correction :**

Le quotient théorique est \(512/80 = 6,4\), donc au plus six appels selon cette hypothèse arithmétique. Une limite opérationnelle peut être inférieure si une réserve est exigée pour la signalisation, les autres flux ou l'incertitude du modèle. Ce calcul pédagogique ne remplace pas le dimensionnement réel : il faut intégrer l'overhead, les codec et paramètres effectivement utilisés, le mode d'allocation CUCM et les liens concurrents. Vérifie appels acceptés, appel supplémentaire refusé si attendu, chemins alternatifs et état du LBM.

## 15. Exercices corrigés

### Exercice 1 — Un trunk est-il un transport média ?

**Question :** un trunk SIP CUCM est établi ; peux-tu conclure que la voix passera par CUCM ?

**Correction :** non. Le trunk représente une interconnexion de signalisation et de routage d'appels. Le média peut emprunter un chemin direct entre terminaux, passer par un CUBE/gateway ou être ancré sur une ressource. Il faut examiner le SDP et la topologie réelle.

### Exercice 2 — Pourquoi séparer les transformations et les autorisations ?

**Question :** quel est l'intérêt de séparer la normalisation E.164 de la permission d'appeler ?

**Correction :** la normalisation vise une représentation cohérente des numéros ; l'autorisation limite les destinations accessibles ; le routage choisit le chemin. Cette séparation facilite les tests, réduit les règles ambiguës et limite les risques de fraude lors d'une transformation.

### Exercice 3 — SIP 488

**Question :** un pair retourne 488 Not Acceptable Here. Quelle est la première piste ?

**Correction :** comparer les paramètres SDP et les capacités réellement proposées et acceptées : codec, profil RTP, direction média, sécurité SRTP et attributs propres au scénario. Le code seul ne permet pas de conclure à une cause précise.

### Exercice 4 — Rôle du CAC

**Question :** pourquoi un appel peut-il être rejeté alors que l'interface WAN semble encore disponible ?

**Correction :** le CAC utilise un modèle logique de bande passante et de chemins configurés. Le modèle peut être plus conservateur que l'utilisation instantanée mesurée, ou être incohérent avec la topologie actuelle. Il faut comparer la configuration Locations/Links, les Regions et la situation réseau réelle.

### Exercice 5 — Sécurité du média

**Question :** un trunk TLS garantit-il que toute la conversation est chiffrée ?

**Correction :** non. TLS concerne la signalisation sur le segment concerné. La protection du média repose notamment sur SRTP et sur le comportement de chaque segment et point d'ancrage. Il faut prouver la protection de bout en bout avant de revendiquer cette propriété.

### Exercice 6 — Traces détaillées

**Question :** pourquoi ne faut-il pas conserver durablement toutes les traces en niveau détaillé ?

**Correction :** les traces élevées augmentent le volume de données et peuvent affecter les performances. Elles peuvent également contenir des informations sensibles. On utilise une collecte ciblée, limitée dans le temps, puis on restaure les niveaux habituels.

### Exercice 7 — Sauvegarde réussie

**Question :** une sauvegarde DRS terminée avec succès prouve-t-elle que le cluster peut être restauré dans le RTO ?

**Correction :** non. Seul un exercice de restauration contrôlé permet de mesurer la durée, révéler les dépendances et vérifier la validité de la procédure. Il faut également vérifier les versions, certificats, services, réplication et appels après restauration.

### Exercice 8 — Téléphone qui ne s'enregistre plus

**Question :** après une opération sur les certificats, plusieurs téléphones échouent à s'enregistrer. Quel est le bon premier réflexe ?

**Correction :** recueillir le message et l'heure exacts, vérifier les certificats et la chaîne de confiance, NTP, TFTP, ITL/CTL et les services concernés. Éviter les suppressions de confiance ou régénérations en chaîne sans procédure adaptée au modèle et à la version.

### Exercice 9 — Appels dégradés aux heures de pointe

**Question :** pourquoi un appel témoin effectué à faible charge ne suffit-il pas ?

**Correction :** il ne représente pas la congestion ni la saturation des ressources aux heures de pointe. Corrèle les mesures réseau, la QoS, les appels simultanés, la capacité des médias, les événements du site et le CAC aux périodes affectées.

### Exercice 10 — Choix multi-cluster

**Question :** quel argument suffit à justifier plusieurs clusters ?

**Correction :** aucun argument isolé ne suffit. La décision doit tenir compte de la résilience, de la géographie, de la gouvernance, de la capacité, de la latence, des contraintes de site, de la complexité opérationnelle et des coûts. Plusieurs clusters ajoutent des exigences de routage, de sécurité et de supervision.

## 16. Défi final : incident complexe sur NovaTel

### 16.1 Situation

NovaTel exploite un cluster CUCM central, deux CUBE vers des opérateurs SIP et trois sites reliés par WAN. Un changement a été déployé le soir précédent : modification d'une transformation de numéro, renouvellement d'un certificat de trunk et ajustement du modèle CAC. Le lendemain, plusieurs symptômes sont signalés :

- les appels internes du siège fonctionnent ;
- les appels internationaux de certains utilisateurs échouent ;
- quelques appels entre sites sont établis mais sans audio dans un sens ;
- des téléphones d'une agence se sont réenregistrés après un délai inhabituel ;
- les appels en visioconférence sont parfois refusés lorsque le WAN est chargé.

Tu es responsable de l'investigation. Tu dois limiter l'impact et préserver les preuves.

### 16.2 Travail demandé

1. établir une chronologie et une liste d'informations à collecter ;
2. définir un ordre de diagnostic qui évite les modifications simultanées ;
3. formuler au moins une hypothèse indépendante pour chaque symptôme ;
4. identifier les traces et mesures qui permettraient de confirmer ou d'infirmer chaque hypothèse ;
5. proposer des actions correctives avec contrôles de sécurité ;
6. préparer les critères de retour arrière et le rapport de clôture.

### 16.3 Correction détaillée

**Étape 1 : préserver l'état initial.** Enregistrer l'heure, la version, les changements exacts et leurs auteurs. Capturer l'état des trunks, services, réplication, enregistrement des téléphones, alarmes, NTP et métriques WAN. Ne pas commencer par modifier encore le dial plan ou les certificats.

**Étape 2 : séparer les symptômes.** Les appels internationaux concernent probablement le dial plan, les autorisations ou le comportement de l'opérateur. Le son unidirectionnel concerne probablement SDP/RTP, la connectivité ou un changement du chemin média. Le délai d'enregistrement oriente vers la confiance/certificats, TFTP, le réseau ou la disponibilité des services. Le refus vidéo sous charge oriente vers CAC, la disponibilité du chemin ou les ressources média. Ces pistes ne sont pas encore des conclusions.

**Étape 3 : appels internationaux.** Prendre un appel réussi et un appel échoué avec le même préfixe, si possible. Comparer le numéro composé, les transformations et CSS, les chiffres envoyés au CUBE et la réponse SIP du pair. Si CUCM ne sélectionne aucun chemin, travailler sur la route et les autorisations. Si le CUBE émet l'appel puis reçoit un rejet, vérifier la politique de l'opérateur, l'identité appelante et le format demandé. Tester ensuite un cas autorisé et un cas qui doit rester bloqué.

**Étape 4 : audio unidirectionnel.** Lire le SDP dans les messages de chaque jambe de l'appel. Déterminer si la transformation modifiée a aussi changé un numéro ou une route média indirectement, puis contrôler le chemin IP du média, les ACL, le NAT éventuel, le SRTP et toute ressource ancrée. Comparer à un appel inter-site réussi. Vérifier les deux sens séparément et ne pas forcer MTP comme remède générique.

**Étape 5 : enregistrement des téléphones.** Corréler l'heure du problème avec le changement de certificat. Vérifier les dates et chaînes, les noms, le service TFTP, l'horloge, la confiance ITL/CTL et les messages exacts des modèles touchés. Examiner si le symptôme concerne un modèle, un site ou tous les téléphones. Appliquer seulement la procédure de confiance documentée pour la version, avec un pilote et un plan de retour arrière.

**Étape 6 : refus vidéo sous charge.** Comparer les appels refusés avec la capacité de lien, l'allocation média, les Regions, Locations/Links, le modèle CAC et l'état du LBM. Mesurer également la congestion physique du WAN et les pertes/gigue. Si le CAC rejette correctement une session excédentaire, il peut remplir son rôle ; il faut alors décider si la capacité ou l'allocation doit changer. Si le modèle ne correspond pas à la topologie réelle, le corriger de manière contrôlée et retester les scénarios de charge.

**Étape 7 : prioriser les actions.** Corriger d'abord une cause confirmée avec une modification aussi limitée que possible. Pour chaque modification, mesurer le résultat et réexécuter la matrice de tests. Si le changement de la veille est corrélé et que la procédure de retour arrière reste sûre, appliquer la décision approuvée plutôt que d'empiler des correctifs incertains.

**Étape 8 : valider et clôturer.** Tester les appels internes, PSTN entrants/sortants, internationaux autorisés/interdits, transferts, conférences, appels inter-sites, audio bidirectionnel, appels chiffrés et survivabilité dans le périmètre prévu. Vérifier que les téléphones sont enregistrés, que les trunks sont stables et que les alertes disparaissent. Documenter cause racine, preuves, changement réalisé, impact, résultats, risque résiduel et actions préventives.

## 17. Checklist d'exploitation experte

Avant un changement majeur :

- [ ] version et matrice de compatibilité vérifiées ;
- [ ] topologie, dépendances et impact documentés ;
- [ ] sauvegarde et procédure de restauration testées ou vérifiées selon le niveau de risque ;
- [ ] dial plan, CSS, partitions et routes testés positivement et négativement ;
- [ ] état de réplication, NTP, DNS, services et certificats contrôlé ;
- [ ] capacités médias, WAN et CAC vérifiées ;
- [ ] politique de sécurité et d'accès confirmée ;
- [ ] procédure de validation et retour arrière approuvée.

Après le changement :

- [ ] enregistrement des terminaux et état des trunks validés ;
- [ ] appels internes, entrants, sortants et inter-sites validés ;
- [ ] média bidirectionnel, codecs, DTMF, transfert, conférence et messagerie testés ;
- [ ] politique d'appel interdit testée ;
- [ ] métriques WAN, QoS, CAC et ressources média contrôlées ;
- [ ] alarmes et traces temporaires nettoyées ;
- [ ] documentation, sauvegarde et journal de changement mis à jour.

## 18. Glossaire expert

- **CAC** : Call Admission Control, contrôle d'admission des appels selon un modèle de ressources ou de bande passante.
- **CAR/CDR/CMR** : outils et données d'analyse de l'activité et de la qualité des appels selon la collecte configurée.
- **CUBE** : Cisco Unified Border Element, fonction de bordure pour interconnexion de sessions voix/vidéo.
- **CSS / Partition** : objets CUCM qui déterminent quelles destinations de routage sont accessibles.
- **DRS** : Disaster Recovery System, sauvegarde et restauration prises en charge du système.
- **E.164** : plan international de numérotation téléphonique.
- **ILS / GDPR** : mécanismes CUCM d'échange d'informations de recherche et de destinations globalisées, selon la conception.
- **ITL / CTL** : fichiers de confiance utilisés par les mécanismes de sécurité de CUCM et des terminaux selon le mode configuré.
- **LBM** : Location Bandwidth Manager, service utilisé par Enhanced Locations CAC.
- **MTP** : Media Termination Point.
- **RTMT** : Real-Time Monitoring Tool.
- **SDI / SDL** : familles de traces utilisées par les services et outils CUCM concernés.
- **SDP** : Session Description Protocol, description des paramètres média dans la signalisation.
- **SME** : Session Management Edition, architecture CUCM orientée gestion centralisée des sessions entre domaines.
- **SRST** : Survivable Remote Site Telephony.
- **SRTP / TLS** : mécanismes de protection du média et de la signalisation, respectivement, selon la configuration et les capacités des pairs.

## 19. Références techniques officielles

Consulte la documentation de la version réellement déployée avant toute intervention. Les liens suivants pointent vers les guides officiels Cisco disponibles lors de la préparation de ce cours.

1. **Cisco Unified Communications Manager 15 — System Configuration Guide** : architecture générale, trunks, gateways, plan de numérotation, routes, media resources, régions, locations et CAC.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html
2. **Configure Trunks — CUCM 15** : principes et configuration des trunks SIP et paramètres associés.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_01000.html
3. **Configure Call Routing — CUCM 15** : patterns, transformations et routage.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_010010.html
4. **Enhanced Locations Call Admission Control — CUCM 15** : topologie, bande passante, liens et Location Bandwidth Manager.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_01101.html
5. **Cisco Unified Communications Manager 15 — Security Guide** : sécurité des terminaux, certificats et modes sécurisés.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/security/15_0/cucm_b_security-guide-release-15.html
6. **CUCM 15 — Administration Guide, Trace** : configuration et collecte des traces via RTMT.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/adminGd/cucm_b_administration-guide-15/cucm_b_test-adminguide_chapter_011000.html
7. **CUCM 15 — Administration Guide, Back Up the System** : sauvegarde et planification DRS.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/adminGd/cucm_b_administration-guide-15.html
8. **Feature Configuration Guide for CUCM 15** : fonctions avancées, SIP interoperability, QoS et sécurité selon les fonctionnalités activées.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15.html

## Conclusion

Le niveau expert consiste à relier l'architecture, le plan de numérotation, SIP, les médias, la QoS, la sécurité et la reprise dans une méthode d'ingénierie cohérente. Pour chaque panne, une hypothèse doit produire une preuve vérifiable ; pour chaque changement, le résultat attendu et les limites de retour arrière doivent être explicites.

La compétence centrale n'est pas de mémoriser un grand nombre de champs CUCM. C'est de pouvoir expliquer pourquoi un appel suit un chemin donné, de prouver où il échoue, de corriger la cause sans ouvrir de nouvelle faille et de démontrer que le service reste fiable après le changement.
