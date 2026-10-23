---
node_id: ntp-syslog-debutant
title: NTP & Syslog - Débutant
---

# NTP & Syslog - Débutant

**Niveau :** Débutant

La gestion d’un réseau ne consiste pas seulement à faire circuler les paquets. Un administrateur doit également pouvoir dater les événements avec précision, comprendre ce qui s’est produit avant une panne, corréler les incidents sur plusieurs équipements et conserver des traces utilisables après un redémarrage. Deux services contribuent directement à cet objectif : le Network Time Protocol (NTP) et Syslog. NTP maintient l’horloge des équipements alignée sur une source de temps de référence ; Syslog transporte des messages d’événements vers une destination de collecte afin qu’ils puissent être consultés, filtrés et conservés.

Sans synchronisation horaire, les journaux d’un routeur, d’un commutateur, d’un pare-feu et d’un serveur peuvent afficher des heures divergentes. Une alerte enregistrée à 10 h 02 sur un équipement peut apparaître à 10 h 07 sur un autre, même si les deux événements ont été provoqués par la même action. Il devient alors difficile de déterminer l’ordre réel des événements. Une heure correctement synchronisée ne garantit pas à elle seule un diagnostic juste, mais elle constitue une condition importante pour établir une chronologie fiable.

NTP est un protocole réseau spécialisé dans la synchronisation des horloges. Les clients échangent des messages avec un ou plusieurs serveurs et utilisent des mesures temporelles pour estimer le décalage de leur horloge et ajuster son comportement. Les concepts de strate (*stratum*), de source de référence, de décalage (*offset*), de délai et de dispersion aident à évaluer la qualité de la synchronisation. Dans un réseau d’entreprise, il est courant de désigner une source de temps approuvée, de synchroniser les équipements d’infrastructure sur cette source et de vérifier régulièrement leur état.

Syslog est un mécanisme normalisé de transmission de messages d’événements. Un équipement peut produire des événements concernant les interfaces, le routage, l’authentification, l’alimentation, les changements de configuration ou les relations avec ses voisins. Syslog permet de diriger ces messages vers un collecteur central. Le format et le transport doivent être distingués : la RFC 5424 décrit un format de message Syslog standardisé et une architecture en couches ; des transports comme UDP ou TLS font l’objet de spécifications séparées. Les équipements Cisco proposent également des paramètres locaux de journalisation, indépendamment de l’envoi distant.

> **Analogie** : Imagine une équipe de maintenance qui travaille dans plusieurs bâtiments. Chaque technicien porte une montre et tient un carnet d’intervention. Si les montres ne sont pas à l’heure, les carnets racontent une histoire incohérente : le technicien du bâtiment A croit qu’une panne a commencé après l’arrivée du technicien B, alors que l’ordre réel est inverse. NTP joue le rôle du service qui remet régulièrement les montres à l’heure d’une référence commune. Il n’oblige pas tous les techniciens à utiliser exactement la même montre physique ; il maintient leurs horloges cohérentes avec une référence de temps.
>
> Syslog représente le processus qui centralise les carnets. Chaque technicien consigne ce qui s’est passé, puis envoie les informations utiles au bureau de maintenance. Le bureau peut rechercher tous les événements d’une période, repérer des erreurs répétées et comparer les rapports de plusieurs bâtiments. Les carnets locaux restent utiles, mais ils peuvent être effacés ou disparaître si l’équipement est réinitialisé. Une collecte centralisée ajoute une copie exploitable ailleurs.
>
> Une nuance importante : le service qui synchronise les montres ne tient pas le carnet à la place des techniciens. NTP ne collecte pas les événements, et Syslog ne synchronise pas l’heure. Les deux fonctions se complètent. Une politique efficace doit donc configurer et vérifier séparément la synchronisation horaire, la journalisation locale, l’envoi distant, la conservation des messages et la protection des accès.

---

## 1. La théorie et les algorithmes

### 1.1. Pourquoi synchroniser l’heure d’un équipement réseau ?

Chaque routeur, commutateur, pare-feu ou serveur possède une horloge système. Cette horloge sert à afficher les dates, à produire des journaux, à dater des événements de sécurité et à coordonner certaines opérations. Les horloges matérielles et logicielles ne sont pas parfaites : elles peuvent avancer ou retarder, dériver avec la température, être mal configurées ou être remises à zéro après une coupure d’alimentation.

Le temps doit être suffisamment cohérent entre les équipements pour permettre la corrélation d’événements. Les journaux peuvent par exemple révéler la séquence suivante :

1. Un port de commutateur passe à l’état down.
2. Le voisinage de routage disparaît.
3. Une route est retirée de la table.
4. Une alarme de surveillance constate une perte de connectivité.
5. Un administrateur se connecte pour intervenir.

Si les équipements utilisent des horloges très différentes, ces événements peuvent sembler dans le mauvais ordre. La synchronisation réduit cette ambiguïté. Elle est également utile pour l’analyse des incidents de cybersécurité, les audits, les certificats, les systèmes distribués et les mécanismes qui dépendent d’horodatages.

NTP ne garantit pas que toutes les machines afficheront exactement la même heure à la microseconde près. La précision dépend de la source, du réseau, de la qualité de l’horloge, du logiciel et des mécanismes de correction. L’objectif opérationnel consiste à disposer d’une heure cohérente, traçable et assez précise pour les besoins de l’organisation.

### 1.2. Temps système, UTC et fuseau horaire

Il faut distinguer l’instant de référence, le temps système et la manière dont l’heure est affichée.

- **UTC (Temps universel coordonné)** fournit une référence de temps commune.
- **L’horloge système** représente le temps maintenu par l’équipement.
- **Le fuseau horaire** détermine la conversion utilisée pour présenter cette heure dans une région.
- **L’heure d’été**, lorsqu’elle est applicable, est une règle de présentation et de calendrier, non une source de synchronisation.

Deux routeurs peuvent afficher des heures locales différentes tout en étant correctement synchronisés sur la même référence UTC, si leurs fuseaux horaires sont configurés différemment. Inversement, deux routeurs qui affichent la même heure locale ne sont pas nécessairement synchronisés : leur horloge peut simplement être réglée manuellement sur la même valeur.

Pour corréler des journaux provenant de systèmes différents, il est souvent préférable de conserver un horodatage cohérent et de documenter le fuseau utilisé par chaque collecteur. Les systèmes de collecte modernes peuvent normaliser les heures en UTC tout en affichant les résultats dans le fuseau de l’opérateur.

### 1.3. Présentation de NTP

Le Network Time Protocol permet à des systèmes d’échanger des informations de temps sur un réseau IP. NTPv4 est décrit notamment dans la RFC 5905, complétée et mise à jour par plusieurs RFC ultérieures. NTP utilise UDP et le port de destination 123 dans son fonctionnement réseau courant.

Dans une architecture typique, un équipement client envoie des requêtes à un serveur NTP. Le serveur répond en fournissant des horodatages qui permettent au client d’estimer le décalage temporel et le délai du chemin. Les implémentations NTP utilisent plusieurs mesures et des algorithmes de filtrage afin d’éviter de corriger l’horloge à partir d’une mesure isolée trop perturbée.

Un équipement peut être client NTP, serveur pour d’autres clients, ou jouer les deux rôles. Par exemple, un serveur de temps interne peut se synchroniser sur une source de référence autorisée et distribuer ensuite l’heure aux routeurs et commutateurs du réseau. Les équipements d’accès n’ont alors pas besoin d’interroger directement de nombreux serveurs externes.

NTP est différent d’une simple commande manuelle permettant de régler l’heure. Le réglage manuel définit une valeur ponctuelle, tandis que NTP mesure régulièrement la relation entre l’horloge locale et une source distante, puis ajuste l’horloge au fil du temps.

### 1.4. Hiérarchie NTP et stratum

NTP représente l’organisation des sources de temps à l’aide d’une hiérarchie appelée *stratum* (strate).

| Stratum | Signification simplifiée |
|---|---|
| Stratum 0 | Référence de temps de haute qualité, par exemple certaines horloges atomiques ou certains récepteurs de référence. Ce n’est généralement pas un serveur NTP IP ordinaire. |
| Stratum 1 | Serveur directement synchronisé sur une référence de stratum 0. |
| Stratum 2 | Serveur synchronisé sur un serveur stratum 1. |
| Stratum 3 | Serveur synchronisé sur une source stratum 2, etc. |

La strate indique la distance hiérarchique depuis la référence déclarée, pas une note absolue de qualité. Un serveur de stratum 2 n’est pas systématiquement plus précis qu’un autre serveur stratum 2. La stabilité, le délai, la dispersion, le jitter, la qualité du chemin et la fiabilité de la source comptent aussi.

Une horloge peut être « non synchronisée » même si elle possède une configuration `ntp server`. La présence d’une commande dans la configuration indique seulement qu’une source a été déclarée ; il faut inspecter l’état opérationnel de la synchronisation.

#### Schéma de hiérarchie de temps

```text
          Référence de temps
       (GPS, radio ou horloge)
                  |
                  v
          +---------------+
          | Serveur NTP   |
          |   Stratum 1   |
          +---------------+
                  |
          v
          +---------------+
          | Serveur NTP   |
          |   Stratum 2   |
          +---------------+
             /          \
            v            v
      +----------+  +----------+
      | Routeur  |  | Switch   |
      | Client   |  | Client   |
      +----------+  +----------+

  La hiérarchie représente la relation de synchronisation,
  pas une hiérarchie de privilèges administratifs.
```

Dans un réseau d’entreprise, une conception habituelle consiste à disposer d’un ou de plusieurs serveurs internes approuvés, à les synchroniser sur une source fiable et à faire pointer les équipements réseau vers ces serveurs. L’organisation peut également prévoir des sources secondaires pour améliorer la disponibilité.

### 1.5. Les mesures temporelles essentielles

NTP manipule plusieurs grandeurs qui décrivent la qualité de la synchronisation. Pour un débutant, les principales sont les suivantes :

- **Offset** : différence estimée entre l’horloge locale et celle de la source distante.
- **Delay** : délai aller-retour associé à la mesure de temps.
- **Jitter** : variation statistique des mesures d’offset ou estimation de leur stabilité, selon le contexte de sortie.
- **Dispersion** : estimation de l’incertitude accumulée sur la mesure.
- **Stratum** : niveau hiérarchique de la source sélectionnée.

NTP utilise quatre horodatages dans son modèle client-serveur classique. Ils sont traditionnellement désignés T1, T2, T3 et T4 :

- T1 : instant auquel le client envoie la requête.
- T2 : instant auquel le serveur reçoit la requête.
- T3 : instant auquel le serveur envoie la réponse.
- T4 : instant auquel le client reçoit la réponse.

Sous les hypothèses habituelles du modèle, le client estime le délai aller-retour et le décalage temporel par des combinaisons de ces quatre valeurs. Une formule souvent enseignée pour le délai est :

\[
\delta = (T4 - T1) - (T3 - T2)
\]

L’offset peut être estimé par :

\[
\theta = \frac{(T2 - T1) + (T3 - T4)}{2}
\]

Ces formules expliquent le principe de mesure, mais elles ne décrivent pas à elles seules l’ensemble de l’algorithme NTP. Les implémentations gèrent les erreurs de mesure, les variations de délai et les données historiques à l’aide de filtres et de mécanismes de sélection.

Le trajet réseau n’est pas toujours symétrique. Si la requête et la réponse subissent des délais très différents, l’estimation de l’offset peut être affectée. C’est l’une des raisons pour lesquelles une bonne synchronisation dépend de la qualité des liens et de la qualité des sources, et pas uniquement de la présence d’un serveur dans la configuration.

### 1.6. NTP et SNTP

NTP et SNTP (*Simple Network Time Protocol*) ont des formats et des comportements apparentés, mais SNTP utilise une partie simplifiée des capacités de NTP. Il convient de vérifier les fonctionnalités réellement prises en charge par l’équipement.

De nombreux équipements réseau utilisent des clients NTP intégrés dont l’administrateur n’a pas à régler tous les paramètres de l’algorithme. Il suffit souvent de déclarer les serveurs et de contrôler l’état. D’autres systèmes peuvent fournir une interface de configuration plus avancée.

Dans une architecture de production, on ne doit pas supposer qu’une commande existe dans toutes les versions d’un système d’exploitation. Les exemples Cisco IOS ci-dessous sont représentatifs de nombreuses plateformes classiques, mais la syntaxe et les options exactes doivent être vérifiées sur le logiciel ciblé.

### 1.7. Présentation de Syslog

Syslog est un mécanisme de production, de transmission et de collecte de messages décrivant des événements. Il peut être mis en œuvre sur les routeurs, les commutateurs, les pare-feu, les serveurs, les systèmes d’exploitation et de nombreuses applications.

Un message Syslog contient généralement des informations sur l’événement : l’équipement source, le processus concerné, une indication de gravité, un horodatage éventuel et un texte expliquant ce qui s’est produit. La représentation exacte varie selon le format et l’implémentation.

La RFC 5424 spécifie le format standardisé moderne de messages Syslog. La RFC 3164 documentait un format historique souvent appelé BSD Syslog. En pratique, les équipements réseau peuvent continuer à produire des messages dans des formats classiques propriétaires ou traditionnels. Les collecteurs doivent donc être configurés pour interpréter les messages effectivement envoyés.

Syslog sépare conceptuellement le contenu du message et son transport. UDP est historiquement courant dans les environnements réseau, souvent sur le port destination 514, mais il ne fournit pas à lui seul la garantie qu’un message a été livré. D’autres transports peuvent apporter des mécanismes différents, et TLS peut être utilisé dans des architectures qui prennent en charge le transport Syslog sécurisé défini notamment par la RFC 5425.

La collecte centralisée permet de chercher des événements sur plusieurs équipements depuis un même système. Elle ne doit pas être considérée comme une sauvegarde parfaite : il faut contrôler les pertes, la rétention, les accès, les capacités de stockage et la qualité des horodatages.

### 1.8. La gravité Syslog

Les événements Syslog sont couramment associés à huit niveaux de sévérité, numérotés de 0 à 7. Le nombre le plus bas indique le niveau de gravité le plus élevé.

| Niveau | Nom | Interprétation générale |
|---:|---|---|
| 0 | emergencies | Le système est inutilisable. |
| 1 | alerts | Une action immédiate est nécessaire. |
| 2 | critical | Événement critique. |
| 3 | errors | Condition d’erreur. |
| 4 | warnings | Avertissement. |
| 5 | notifications | Événement notable, mais non nécessairement problématique. |
| 6 | informational | Information de fonctionnement. |
| 7 | debugging | Informations de débogage détaillées. |

La valeur de sévérité ne doit pas être confondue avec la catégorie fonctionnelle de l’événement. Un message informatif peut être important pour l’investigation même s’il n’indique pas une panne. À l’inverse, un événement de niveau élevé peut nécessiter une vérification immédiate.

Dans Cisco IOS, les commandes de journalisation permettent généralement de définir un seuil. Par exemple, `logging trap warnings` autorise l’envoi des événements de gravité *warnings* et plus critiques, c’est-à-dire les niveaux 0 à 4. Le paramètre est un seuil et non une liste restrictive d’un seul niveau.

### 1.9. Facility, sévérité et message

La *facility* est une catégorie utilisée par certaines implémentations Syslog pour identifier une source ou un type de service. La sévérité indique quant à elle le niveau d’importance du message. Les deux concepts répondent à des besoins différents.

Le contenu d’un message peut inclure un identifiant de processus, un identifiant d’événement, un nom de composant ou des champs structurés. Un collecteur peut employer ces informations pour classer les messages par équipement, interface, application, catégorie ou gravité.

Un administrateur ne doit pas supposer que tous les équipements prennent en charge exactement la même liste de facilities ou qu’ils émettent un format identique. Lors de la mise en service d’un collecteur, il faut vérifier le parsing des messages et le mapping des niveaux utilisés par chaque famille d’équipements.

### 1.10. Syslog local et Syslog distant

Les équipements réseau proposent souvent plusieurs destinations de journalisation :

- La console locale, utile pendant la configuration ou le dépannage.
- Les lignes de terminal virtuel, selon la configuration.
- La mémoire tampon interne, dont la capacité est limitée.
- Un serveur Syslog distant, qui peut conserver les événements en dehors de l’équipement.

Le journal local est pratique pour un diagnostic immédiat, mais son contenu peut être perdu lors d’un redémarrage ou lorsqu’il est remplacé par de nouveaux messages. Le Syslog distant permet de conserver les événements au-delà de la durée de vie de la mémoire locale, à condition que l’envoi, la réception et la rétention soient opérationnels.

#### Schéma de collecte centralisée

```text
    +------------+        Syslog         +-------------------+
    | Routeur R1 |--------------------->|                   |
    +------------+                      |                   |
                                        | Collecteur Syslog |
    +------------+        Syslog         |                   |
    | Switch S1  |--------------------->| Recherche, filtre,|
    +------------+                      | alertes, rétention|
                                        |                   |
    +------------+        Syslog         |                   |
    | Pare-feu   |--------------------->|                   |
    +------------+                      +-------------------+

       Horloge NTP cohérente sur les équipements
       et le collecteur pour corréler les événements.
```

### 1.11. Pourquoi NTP et Syslog doivent être configurés ensemble

NTP et Syslog se complètent. Un collecteur central peut réunir les événements de centaines d’équipements, mais l’analyse temporelle devient fragile si les horloges sont incorrectes.

Supposons qu’un routeur signale une perte de voisinage à 09:15:02, qu’un commutateur signale un changement de port à 09:15:04 et qu’un serveur de supervision déclare une indisponibilité à 09:15:01. Si ces horodatages reposent sur des horloges désynchronisées, la séquence peut être inversée ou faussement rapprochée.

La bonne pratique consiste à :

1. établir une source horaire approuvée ;
2. synchroniser les équipements et le collecteur sur une hiérarchie cohérente ;
3. configurer Syslog local et distant ;
4. vérifier que les messages sont réellement reçus ;
5. contrôler les fuseaux horaires et la précision des horodatages ;
6. définir la rétention, les accès et les alertes.

Il ne suffit pas de déclarer une adresse NTP et une adresse Syslog dans la configuration. Les états opérationnels des deux services doivent être contrôlés séparément.

### 1.12. Limites du transport Syslog

Le transport Syslog historique sur UDP est simple et léger, mais il ne garantit pas la livraison de chaque message. Un paquet peut être perdu à cause d’une congestion, d’un filtrage, d’une erreur de routage ou d’un problème du collecteur. UDP ne fournit pas, par lui-même, une confirmation de réception.

Cela ne signifie pas que Syslog est inutile ou intrinsèquement non fiable dans tous les environnements. Pour les événements courants, le transport UDP peut être suffisant si les exigences sont adaptées, que les pertes sont surveillées et que l’équipement conserve également des messages localement. Pour des exigences de sécurité ou de conformité plus élevées, il faut étudier des transports offrant une protection de transport et des garanties adaptées.

La RFC 5424 définit la structure du message Syslog, mais elle n’impose pas un unique transport dans toutes les situations. La RFC 5426 décrit le transport de Syslog sur UDP et la RFC 5425 spécifie Syslog sur TLS. La compatibilité et la syntaxe disponibles dépendent des équipements concernés.

### 1.13. Fuseaux horaires et horodatages Cisco

Une configuration Cisco peut définir le fuseau local et le format des horodatages de journalisation. Une configuration représentative est :

```cisco
clock timezone WAT 1 0
service timestamps log datetime msec localtime show-timezone year
```

Dans cet exemple, le fuseau `WAT` est configuré avec un décalage de +1 heure par rapport à UTC. Les règles spécifiques doivent toujours correspondre au lieu et à la politique de l’organisation. Il faut éviter de supposer que la même ligne de fuseau convient à tous les sites.

La commande `service timestamps log datetime msec localtime show-timezone year` demande à IOS d’inclure une date et une heure avec millisecondes, de présenter l’heure locale, d’afficher l’indication de fuseau et l’année. Certaines options ou formes de commande peuvent différer selon la version IOS/IOS XE.

Une fois l’horloge NTP synchronisée, l’heure de journalisation doit être vérifiée dans les messages réellement produits. Le fait qu’une commande soit dans la configuration ne prouve pas qu’un horodatage précis et correct apparaît dans tous les journaux.

### 1.14. Source d’envoi Syslog

Un routeur peut posséder plusieurs interfaces et donc plusieurs adresses IP. Lorsqu’il envoie des messages Syslog à un collecteur, il est généralement utile de choisir explicitement une adresse source stable. Cette adresse permet au collecteur d’identifier l’équipement de manière prévisible.

Sous Cisco IOS, une configuration courante est :

```cisco
logging source-interface Loopback0
```

Si la plateforme prend en charge cette commande et si la Loopback0 est configurée et routable depuis le collecteur, Syslog utilise cette interface comme source selon le comportement de la plateforme. Il faut s’assurer que le réseau de collecte dispose d’une route de retour et que les ACL ou pare-feu autorisent le trafic correspondant.

La loopback doit être documentée et ne doit pas être choisie arbitrairement. Dans les architectures à VRF, le contexte de routage utilisé pour le Syslog distant doit également être validé.

### 1.15. Perte de messages et capacité du collecteur

La centralisation des journaux ne supprime pas les contraintes de volume. Un commutateur peut produire peu d’événements en fonctionnement stable, mais générer un flux important de messages si une interface oscille, si un protocole se reconverge souvent ou si le débogage est activé.

Un collecteur doit disposer d’une capacité suffisante pour recevoir, indexer et conserver le volume attendu. Une politique de rétention doit équilibrer le coût de stockage, les exigences d’investigation et les exigences réglementaires éventuelles.

Il faut également maîtriser les niveaux d’émission. Transmettre continuellement des messages de débogage peut saturer le collecteur, augmenter le trafic et rendre les événements importants plus difficiles à distinguer. Il est préférable de sélectionner un seuil adapté à l’exploitation et de n’activer le débogage que temporairement lorsque cela est nécessaire.

La bonne conception consiste à prévoir les limites de volume, les événements de sécurité prioritaires, les alertes en cas d’absence de messages attendus et une protection de l’accès aux journaux.

### 1.16. Syslog et sécurité

Un message Syslog peut contenir des informations sensibles : adresses IP internes, noms d’utilisateurs, identifiants de sessions, noms de systèmes ou détails de configuration. L’accès aux journaux doit donc être limité aux personnes et services autorisés.

Lorsque les messages traversent un réseau partagé ou non fiable, un transport non chiffré peut exposer leur contenu à l’observation ou à la modification par un acteur capable d’intercepter le trafic. Les mécanismes de transport sécurisé, notamment Syslog sur TLS lorsque pris en charge, peuvent contribuer à protéger la confidentialité et l’intégrité des transmissions.

La protection du collecteur est aussi importante que celle de l’équipement source. Il faut sécuriser les comptes, restreindre les interfaces d’administration, synchroniser l’heure, définir la rétention et surveiller les changements de configuration. Si un attaquant obtient la capacité d’effacer ou d’altérer les journaux centraux, l’investigation après incident peut devenir difficile.

### 1.17. Pièges de débutant

Plusieurs erreurs sont fréquentes lors de la mise en œuvre de NTP et Syslog.

- Confondre le fuseau horaire avec la synchronisation NTP. Régler le fuseau n’aligne pas l’horloge sur une source fiable.
- Déduire que NTP fonctionne simplement parce qu’une commande `ntp server` est présente.
- Confondre la sévérité Syslog et une facility.
- Croire que le niveau Syslog `warnings` signifie uniquement que les messages de niveau 4 sont envoyés. C’est un seuil qui inclut généralement les niveaux plus critiques.
- Considérer que Syslog sur UDP garantit la réception de tous les messages.
- Envoyer tous les journaux de débogage en permanence vers le collecteur.
- Ne pas prévoir de route de retour, de règle de pare-feu ou d’ACL autorisant les échanges vers le serveur.
- Oublier de vérifier la synchronisation du serveur de collecte lui-même.

> **Piège :** Une ligne `ntp server 192.0.2.10` signifie que l’équipement a été configuré pour utiliser cette adresse comme source NTP ; elle ne prouve pas que l’horloge est synchronisée. De même, une ligne `logging host 192.0.2.20` ne prouve pas que le collecteur reçoit des messages. Il faut confirmer séparément l’état NTP, le routage, les règles de filtrage, les journaux locaux et la réception sur le collecteur.

```text
       CONFIGURATION                     ÉTAT OPÉRATIONNEL
       -------------                     ------------------
       ntp server ...  ------------->    show ntp status
       logging host ... ------------>    show logging + collecteur
       timezone ...     ------------>    vérifier l'heure affichée

       La configuration exprime l'intention ;
       les commandes d'état et les tests confirment le résultat.
```

---

## 2. Configuration et Pratique

### 2.1. Objectif du laboratoire

Le laboratoire met en place une architecture où un routeur de gestion synchronise son horloge avec un serveur NTP et transmet ses messages à un collecteur Syslog. L’objectif est de comprendre comment configurer les deux services, comment vérifier leur fonctionnement et comment isoler les pannes.

Les adresses du laboratoire utilisent les plages de documentation réservées. Elles sont des exemples et ne doivent pas être utilisées comme adresses publiques de production.

| Équipement | Adresse de gestion | Rôle |
|---|---|---|
| R1 | 192.0.2.1/24 | Routeur Cisco à surveiller |
| Serveur NTP | 192.0.2.10/24 | Source de temps approuvée du laboratoire |
| Collecteur Syslog | 192.0.2.20/24 | Réception et stockage des journaux |
| Passerelle de gestion | 192.0.2.254/24 | Sortie éventuelle du segment de gestion |

Pour que les tests réussissent, les serveurs doivent être réellement configurés pour le rôle annoncé, les interfaces doivent être opérationnelles et les politiques réseau doivent autoriser les échanges nécessaires. Une adresse dans le tableau ne crée pas automatiquement un service NTP ou un collecteur Syslog.

#### Schéma du laboratoire

```text
              VLAN / réseau de gestion
                    192.0.2.0/24

     +----------+     NTP UDP/123     +---------------+
     | Serveur  |<--------------------|               |
     | NTP      |                     |      R1       |
     | .10      |                     |    .1         |
     +----------+                     |               |
                                      +-------+-------+
                                              |
                                              | Syslog
                                              | (port/transport
                                              | configurés)
                                              v
                                      +---------------+
                                      | Collecteur    |
                                      | Syslog .20    |
                                      +---------------+
```

### 2.2. Vérifier la connectivité IP avant de configurer les services

Le service NTP et le transport Syslog reposent sur une connectivité IP fonctionnelle. Avant de modifier la configuration des services, vérifie les interfaces et le routage.

```cisco
show ip interface brief
show ip route
ping 192.0.2.10
ping 192.0.2.20
```

Les adresses doivent correspondre au plan d’adressage. Si les serveurs sont sur le même sous-réseau, l’équipement doit résoudre leur adresse de couche 2 pour transmettre les paquets Ethernet. Si les destinations sont distantes, le routeur doit disposer d’une route valide vers elles et les chemins de retour doivent exister.

Un ping réussi constitue un test utile, mais il ne prouve pas que UDP/123 ou le transport Syslog est autorisé. Un pare-feu peut autoriser ICMP tout en bloquant NTP ou Syslog. Il faut donc tester et inspecter les services eux-mêmes.

### 2.3. Configurer le nom, l’heure locale et les horodatages

Un nom d’équipement explicite facilite l’identification des événements dans le collecteur. Le fuseau horaire et le format des horodatages doivent respecter la convention de l’organisation.

```cisco
hostname R1

clock timezone WAT 1 0
service timestamps log datetime msec localtime show-timezone year
```

Dans cet exemple, `WAT` désigne un libellé de fuseau configuré avec un décalage de +1 heure par rapport à UTC. Il faut vérifier que ce paramètre correspond au fuseau réellement utilisé dans le site. Les options de `service timestamps` peuvent différer selon les versions ; il est nécessaire de consulter l’aide de la plateforme si une option n’est pas acceptée.

Le fuseau horaire détermine l’affichage local de la date et de l’heure. Il ne synchronise pas automatiquement l’horloge et ne remplace pas NTP.

### 2.4. Configurer NTP client

Dans le laboratoire, R1 utilise le serveur NTP `192.0.2.10`. La commande Cisco IOS classique est :

```cisco
ntp server 192.0.2.10
```

Pour spécifier une source NTP supplémentaire en redondance :

```cisco
ntp server 192.0.2.11
```

Les adresses doivent correspondre à des serveurs réellement disponibles et approuvés. Il n’est pas conseillé d’ajouter arbitrairement de nombreuses sources : il faut suivre la politique de temps de l’organisation et utiliser des sources de bonne qualité.

Sur les plateformes compatibles, une commande de source d’interface peut être utilisée pour stabiliser l’adresse source des requêtes NTP :

```cisco
ntp source Loopback0
```

Cette configuration suppose que `Loopback0` existe, que son adressage est correct et que la route aller-retour fonctionne depuis le serveur NTP. L’utilisation d’une loopback peut simplifier l’identification des équipements mais exige une conception de routage appropriée.

NTP utilise couramment UDP destination 123. Les pare-feu et ACL intermédiaires doivent autoriser les flux NTP nécessaires, sans ouvrir inutilement des accès vers des réseaux non concernés.

### 2.5. Contrôler l’état NTP

Après la configuration, la synchronisation doit être vérifiée à l’aide des commandes disponibles sur la version utilisée.

```cisco
show ntp status
show ntp associations
show clock detail
```

`show ntp status` fournit l’état global de synchronisation lorsqu’il est disponible. `show ntp associations` donne des informations sur les associations NTP connues, leur état et la source qui peut être sélectionnée selon la plateforme. `show clock detail` montre l’heure système et des informations complémentaires sur la source ou les paramètres de l’horloge, selon le logiciel.

Les états et symboles exacts varient selon la version IOS/IOS XE. Il faut interpréter la sortie de la plateforme et ne pas s’appuyer uniquement sur un code vu dans une documentation d’une autre version.

Si l’horloge n’est pas synchronisée, vérifie dans cet ordre :

1. connectivité IP vers le serveur ;
2. route de retour ;
3. autorisation d’UDP/123 ;
4. disponibilité du service NTP sur le serveur ;
5. compatibilité de la configuration et des mécanismes d’authentification éventuels ;
6. cohérence de l’heure et de l’état affiché sur le client.

Une réponse ICMP à un ping ne garantit pas la réponse NTP. Il faut aussi tenir compte des politiques de sécurité, de l’état du serveur et d’éventuelles restrictions de source.

### 2.6. Configurer Syslog distant

Dans le laboratoire, le collecteur Syslog possède l’adresse `192.0.2.20`. Une configuration Cisco IOS classique peut utiliser :

```cisco
logging on
logging host 192.0.2.20
logging trap informational
logging source-interface Loopback0
```

La syntaxe d’adresse du collecteur et les options exactes varient selon IOS/IOS XE. Certaines versions acceptent également des options de transport ou de VRF. La configuration doit être adaptée à la plateforme et au transport pris en charge.

- `logging on` active la journalisation selon les capacités de la plateforme.
- `logging host` indique la destination distante.
- `logging trap informational` définit un seuil de gravité, qui inclut généralement les niveaux 0 à 6.
- `logging source-interface Loopback0` choisit une source IP stable si l’interface existe et est adaptée au routage vers le collecteur.

Le fait de définir le niveau `informational` peut générer un volume important de messages. Dans un réseau de production, le seuil doit être défini en fonction des besoins opérationnels, de la capacité du collecteur et de la politique de rétention.

### 2.7. Comprendre les niveaux Syslog dans Cisco IOS

Les huit niveaux de sévérité sont souvent présentés comme suit :

| Niveau | Nom | Signification générale |
|---:|---|---|
| 0 | emergencies | Système inutilisable |
| 1 | alerts | Une action immédiate est nécessaire |
| 2 | critical | Condition critique |
| 3 | errors | Erreur |
| 4 | warnings | Avertissement |
| 5 | notifications | Événement notable |
| 6 | informational | Information de fonctionnement |
| 7 | debugging | Information détaillée de débogage |

Le seuil choisi autorise les messages de ce niveau et les niveaux plus graves, c’est-à-dire ceux qui possèdent un numéro inférieur ou égal au seuil. Ainsi, `logging trap warnings` inclut normalement les niveaux 0, 1, 2, 3 et 4, et non uniquement le niveau 4.

Le seuil Syslog distant n’est pas nécessairement identique au niveau de journalisation conservé dans la mémoire tampon locale. La configuration de chaque destination doit être vérifiée, car un équipement peut conserver certains messages localement et en envoyer un sous-ensemble au collecteur.

### 2.8. Configurer la mémoire tampon locale

Un journal local constitue un complément utile à la collecte distante. Une configuration classique peut définir une mémoire tampon de journalisation :

```cisco
logging buffered 16384 informational
```

La valeur de taille, les options et le comportement exact sont dépendants de la plateforme. Il faut vérifier la capacité mémoire disponible et la syntaxe de la version concernée avant d’appliquer cette valeur à un appareil particulier.

La mémoire tampon est généralement limitée. Lorsque de nouveaux messages arrivent, les plus anciens peuvent être remplacés. Elle n’est donc pas équivalente à un système de conservation à long terme. Pour les investigations importantes, le collecteur distant reste nécessaire, avec une politique de rétention appropriée.

La commande de consultation courante est :

```cisco
show logging
```

Elle permet de vérifier l’état du mécanisme de journalisation, certains paramètres, la mémoire tampon et des informations sur les destinations distantes. Elle ne remplace pas la validation côté collecteur, où il faut confirmer que les messages arrivent et sont correctement horodatés.

### 2.9. Générer et vérifier un événement

Pour vérifier Syslog, on peut observer des événements ordinaires comme un changement d’état d’interface dans un environnement de laboratoire. Évite de modifier une interface de production uniquement pour générer un message de test.

Il est possible de produire un message de journalisation de test sur certaines plateformes Cisco à l’aide d’une commande telle que :

```cisco
send log 6 TEST-SYSLOG message-de-verification
```

Cette commande et sa syntaxe ne sont pas disponibles partout et doivent être vérifiées avec l’aide de la plateforme. Si elle n’est pas prise en charge, utilise un événement de test approuvé ou une fonction de test documentée par le constructeur.

Après l’envoi, vérifie `show logging` puis recherche le message attendu sur le collecteur distant. Un message visible dans la mémoire tampon locale mais absent sur le collecteur indique que le problème peut se situer sur la source, le transport, le routage, le filtrage ou le collecteur.

### 2.10. Tester NTP et Syslog séparément

Les services doivent être testés séparément, car ils utilisent des protocoles et des chemins logiques différents.

Pour NTP, confirme l’état de synchronisation et l’association réellement sélectionnée. Vérifie également que l’horloge se stabilise et que l’offset n’est pas anormalement élevé. Pour Syslog, confirme l’émission des messages, leur arrivée sur le collecteur, l’identification de la source, le format de l’horodatage et la présence des niveaux attendus.

Le ping est utile pour vérifier la connectivité IP, mais ne prouve pas que le service fonctionne. Si le ping vers un collecteur répond, il peut néanmoins y avoir un blocage du transport Syslog. De même, la présence d’une route vers un serveur NTP ne garantit pas que le port UDP nécessaire soit autorisé ou que le service réponde.

Une procédure de validation opérationnelle doit inclure au minimum :

- état de synchronisation NTP ;
- source NTP sélectionnée ;
- horloge affichée et fuseau horaire ;
- état du système de journalisation ;
- messages locaux visibles ;
- réception des événements sur le collecteur ;
- présence d’une route et du chemin retour ;
- règles d’ACL et de pare-feu ;
- politique de rétention et d’accès au collecteur.

### 2.11. Exemple de configuration consolidée

La configuration suivante rassemble les éléments principaux du laboratoire. Les interfaces et les adresses doivent être adaptées au réseau utilisé.

```cisco
hostname R1
!
clock timezone WAT 1 0
service timestamps log datetime msec localtime show-timezone year
!
ntp server 192.0.2.10
ntp source Loopback0
!
logging on
logging buffered 16384 informational
logging host 192.0.2.20
logging trap informational
logging source-interface Loopback0
!
interface Loopback0
 description IDENTITE_DE_GESTION
 ip address 198.51.100.1 255.255.255.255
!
```

Les blocs ci-dessus sont illustratifs. L’adresse `198.51.100.1/32` appartient à une plage réservée à la documentation : il s’agit d’un exemple à remplacer dans un réseau réel. Il faut aussi configurer le routage nécessaire vers les serveurs, vérifier que la syntaxe est acceptée sur l’équipement et contrôler que les serveurs acceptent les sources attendues.

La loopback n’est utile que si sa route est présente et annoncée ou configurée comme il convient. Un collecteur ou un serveur NTP qui ne possède pas de chemin de retour vers la source choisie ne pourra pas communiquer normalement avec l’équipement.

### 2.12. Sécuriser la collecte et limiter l’exposition

L’heure et les journaux sont importants pour les opérations et la sécurité. Leur protection doit faire partie du plan d’exploitation.

Les mesures recommandées comprennent :

- utiliser des sources NTP approuvées et limiter les accès NTP aux réseaux nécessaires ;
- empêcher des hôtes non autorisés de devenir des sources de temps pour l’infrastructure ;
- protéger les accès administratifs aux équipements et au collecteur ;
- limiter les niveaux de journalisation à ceux nécessaires en fonctionnement normal ;
- éviter d’exposer des détails sensibles dans les messages lorsque cela peut être contrôlé ;
- protéger l’accès au stockage des journaux ;
- employer un transport Syslog sécurisé lorsque la plateforme et l’architecture le permettent ;
- surveiller l’absence anormale de messages, la dérive temporelle et l’épuisement du stockage ;
- conserver une configuration de référence et une procédure de retour arrière.

L’authentification NTP et les capacités de sécurisation peuvent varier selon l’implémentation. Le transport Syslog sécurisé n’est pas automatiquement activé simplement parce que l’équipement envoie des messages à un serveur distant. La capacité du serveur, le certificat, le transport et la compatibilité du client doivent être vérifiés.

### 2.13. Dépannage : NTP non synchronisé

Si NTP n’est pas synchronisé, commence par relever l’état de l’horloge et les associations :

```cisco
show ntp status
show ntp associations
show clock detail
show ip route 192.0.2.10
```

Puis vérifie la connectivité, la route retour et les politiques de filtrage. Si le serveur est accessible par ping mais que NTP échoue, confirme que le service NTP fonctionne réellement et qu’il autorise l’équipement client. Si la plateforme utilise une source IP spécifique, vérifie que l’adresse source est routable et autorisée par le serveur.

Des décalages extrêmes de l’horloge ou une horloge initialisée à une date très ancienne peuvent affecter certains mécanismes. Il faut suivre les procédures d’initialisation de l’équipement plutôt que d’effectuer des corrections manuelles arbitraires en production.

NTP peut aussi être affecté par des retards, de la perte de paquets ou des chemins réseau asymétriques. Des mesures ponctuelles doivent être comparées à l’état général de l’association et aux sources alternatives éventuelles.

### 2.14. Dépannage : Syslog absent du collecteur

Si les messages sont visibles localement mais ne parviennent pas au collecteur, procède par étapes :

1. vérifie l’adresse IP du collecteur et le transport attendu ;
2. confirme que la destination est configurée sur l’équipement ;
3. vérifie la source d’envoi utilisée ;
4. confirme le routage aller et retour ;
5. vérifie les ACL et les pare-feu entre la source et le collecteur ;
6. confirme que le service Syslog écoute sur l’adresse, le port et le transport configurés ;
7. inspecte une capture réseau ou les compteurs du collecteur si nécessaire ;
8. vérifie les filtres et seuils de sévérité ;
9. recherche les erreurs de parsing, d’horodatage ou de classement dans le collecteur.

La configuration locale peut être correcte tandis que le service destinataire est arrêté. À l’inverse, le collecteur peut recevoir des paquets sans les classer correctement si son parseur ou son mapping de sources est mal configuré.

### 2.15. Diagnostic par capture de paquets

Une capture réseau permet de déterminer si l’équipement envoie réellement des paquets NTP ou Syslog, quelle adresse source est utilisée et si des réponses sont observées. Elle aide à séparer un problème de configuration locale d’un problème de réseau intermédiaire ou de serveur.

Pour NTP, recherche des échanges UDP avec le port concerné, vérifie les adresses source et destination et observe si les réponses reviennent. Pour Syslog, vérifie le protocole et le port réellement utilisés, car l’architecture peut employer des transports différents.

Une capture ne prouve pas à elle seule que le contenu d’un journal a été stocké de façon durable. Elle démontre seulement que le paquet était visible au point de capture. Il faut ensuite vérifier la réception, l’indexation, les règles de rétention et la disponibilité des données dans le collecteur.

Lorsqu’une capture contient des données sensibles, sa collecte, son stockage et sa transmission doivent suivre la politique de sécurité de l’organisation.

### 2.16. Surveillance et bonnes pratiques opérationnelles

Une configuration réussie au moment du déploiement n’est pas suffisante. Les services NTP et Syslog doivent être surveillés dans le temps.

Pour NTP, l’exploitation peut vérifier régulièrement l’état de synchronisation, la source utilisée et les écarts temporels importants. L’absence de source sélectionnée ou une dérive inhabituelle doit produire une alerte adaptée.

Pour Syslog, la surveillance peut couvrir l’absence de messages d’un équipement, l’arrivée d’un volume soudainement élevé, la capacité du collecteur, les erreurs de parsing, les retards d’indexation et l’espace de stockage. Une absence de journal peut signifier que l’équipement est en panne, mais elle peut aussi indiquer une perte de transport ou un collecteur indisponible.

Les équipements critiques devraient disposer de sources de temps et de chemins réseau documentés. L’organisation doit savoir comment les systèmes se comportent lorsque le serveur NTP primaire est indisponible, lorsque le collecteur ne répond plus ou lorsque le réseau de gestion est isolé.

### 2.17. Résumé de la pratique

NTP synchronise les horloges ; Syslog centralise les événements. Les deux services reposent sur la connectivité IP, mais leur état opérationnel se vérifie avec des méthodes distinctes. Un ping réussi ne garantit pas que le service correspondant fonctionne et une commande de configuration ne garantit pas que le résultat attendu est atteint.

Pour exploiter ces services, il faut vérifier la source de temps, l’état de synchronisation, les horodatages, les destinations Syslog, le seuil de gravité, la source IP d’émission, le chemin réseau et la réception côté collecteur. Les journaux doivent être protégés et conservés selon les besoins opérationnels et de sécurité.

> **Astuce :** Pour tout incident, compare d’abord l’heure de `show clock` et l’état `show ntp status`, puis examine `show logging`. Si les messages sont présents localement mais absents du collecteur, concentre le diagnostic sur l’adresse source, les routes, les ACL, le transport et le service récepteur. Si tous les équipements affichent des heures incohérentes, résous d’abord NTP avant de tirer des conclusions à partir de l’ordre des événements.

---

## 3. Dépannage et Sécurité

### 3.1. Construire une méthode de diagnostic

Le dépannage doit partir d’une observation reproductible. Il faut relever l’heure affichée, l’état de synchronisation, la configuration des destinations Syslog et les messages réellement visibles. Modifier plusieurs paramètres en même temps peut masquer la cause du problème et rendre le retour arrière difficile.

Une démarche pratique suit quatre niveaux :

1. **Configuration** : les commandes indiquent-elles les serveurs, les seuils et les horodatages attendus ?
2. **Connectivité** : les adresses source et destination sont-elles routables ? Les ACL autorisent-elles le trafic ?
3. **État du service** : le client NTP est-il synchronisé ? Les messages Syslog sont-ils produits ?
4. **Collecte et exploitation** : le collecteur reçoit-il, interprète-t-il et conserve-t-il les messages ?

Il est important d’éviter l’amalgame entre une route valide et un service fonctionnel. Un routeur peut posséder une route vers un serveur mais ne recevoir aucune réponse parce que le service est arrêté ou filtré.

### 3.2. Panne NTP : la source n’est pas joignable

Si le client ne peut pas joindre le serveur, il faut contrôler l’état de l’interface, le routage et la connectivité. Une route spécifique manquante ou une route par défaut incorrecte peut empêcher les requêtes d’atteindre le serveur. Une mauvaise route retour peut empêcher les réponses de parvenir au client.

Commandes utiles :

```cisco
show ip interface brief
show ip route
show ip route 192.0.2.10
ping 192.0.2.10
traceroute 192.0.2.10
```

La syntaxe exacte du traçage peut varier. Le diagnostic doit tenir compte des filtres et du fait que les serveurs peuvent traiter différemment ICMP et UDP. Si un ping fonctionne, il reste nécessaire de vérifier UDP/123 et la disponibilité du service NTP.

### 3.3. Panne NTP : le serveur répond mais l’horloge n’est pas synchronisée

Une réponse réseau ne garantit pas que le client sélectionne la source. Le serveur peut ne pas être synchronisé lui-même, les mesures peuvent être jugées peu fiables, ou une configuration incorrecte peut empêcher l’association de devenir utilisable.

Examine les sorties suivantes :

```cisco
show ntp status
show ntp associations
show clock detail
show running-config | include ntp
```

La dernière commande de filtrage varie selon les environnements et peut ne pas être disponible partout. Il est acceptable d’inspecter la configuration complète si nécessaire.

Vérifie que l’adresse configurée est correcte, que le serveur est réellement une source NTP, que les paramètres requis sont compatibles et que la source de temps respecte la politique de l’organisation. Si plusieurs sources sont configurées, vérifie laquelle est sélectionnée et si les autres fournissent des informations cohérentes.

Il ne faut pas se contenter de réduire les intervalles de sondage ou d’ajouter de multiples serveurs inconnus. La qualité de la source et la cohérence de la hiérarchie sont plus importantes que le nombre de lignes `ntp server`.

### 3.4. Panne Syslog : aucun message n’est envoyé

Si aucune donnée n’arrive au collecteur, vérifie d’abord que Syslog est activé et que la destination est correcte. Examine ensuite le seuil choisi et la présence de messages locaux. Certains équipements n’enverront pas tous les types d’événements si le seuil est trop restrictif.

```cisco
show logging
show running-config | include logging
```

La commande de recherche dans la configuration est illustrative et dépend de la version. Sur certains systèmes, la syntaxe exacte peut différer.

Si des messages sont visibles localement mais n’atteignent pas le serveur, examine la source IP sélectionnée, les routes et les politiques de filtrage. Si les messages sont reçus mais introuvables dans l’interface du collecteur, contrôle les filtres, le nom de la source, la normalisation de l’horodatage et le parsing.

### 3.5. Problèmes d’horodatage

Un horodatage erroné peut provenir d’une absence de synchronisation, d’un fuseau configuré incorrectement, de l’absence d’année dans les messages, d’un parseur qui interprète mal le format ou d’une différence entre l’heure source et l’heure d’affichage du collecteur.

La première vérification est l’horloge du système et son état NTP. Ensuite, compare un message brut reçu sur le collecteur à la façon dont il apparaît dans l’interface d’analyse. Cette comparaison aide à savoir si le défaut existe sur l’équipement émetteur ou seulement dans le système de collecte.

La normalisation en UTC dans le collecteur peut simplifier la corrélation, mais l’équipe doit documenter le traitement des fuseaux horaires et les règles d’affichage. Un fuseau horaire configuré sur l’équipement ne remplace pas la synchronisation NTP.

### 3.6. Risques de sécurité liés à NTP

Une source de temps malveillante ou incorrecte peut faire afficher des dates erronées, compliquer une investigation, perturber certaines opérations sensibles aux dates et dégrader la confiance dans les journaux. Les mécanismes de sécurité NTP varient selon les implémentations et les versions logicielles ; il faut consulter les capacités de la plateforme et appliquer les méthodes prises en charge.

Les mesures recommandées sont :

- limiter les sources NTP à une liste approuvée ;
- éviter d’exposer inutilement un serveur NTP aux réseaux non concernés ;
- contrôler qui peut interroger ou administrer les serveurs ;
- surveiller les changements de source et les écarts temporels anormaux ;
- documenter l’origine de la référence horaire et les chemins de secours ;
- mettre à jour les systèmes et appliquer les recommandations de sécurité du constructeur.

Le filtrage des requêtes NTP et les règles d’accès doivent être adaptés au rôle du serveur. Un serveur interne qui distribue l’heure aux équipements d’entreprise n’a pas nécessairement besoin d’être accessible depuis Internet.

### 3.7. Risques de sécurité liés à Syslog

Les messages de journalisation peuvent exposer des informations opérationnelles utiles à un attaquant. Selon les applications et les configurations, ils peuvent contenir des adresses, des identifiants, des noms d’équipements, des détails de sessions ou des messages d’erreur détaillés.

Il faut limiter l’accès aux journaux, sécuriser les connexions d’administration du collecteur et prévoir une rétention cohérente. Les transmissions non chiffrées sur des réseaux non fiables peuvent exposer le contenu et faciliter certaines formes de manipulation pour un acteur ayant accès au chemin réseau.

Lorsque la plateforme le permet, Syslog sur TLS peut protéger la transmission en apportant un canal chiffré. Il reste nécessaire de vérifier le certificat, l’identité du serveur, la configuration du client et les mécanismes de rotation. Un TLS mal validé peut donner un faux sentiment de sécurité.

La protection doit également concerner la suppression, la modification et l’accès aux journaux déjà stockés. Les droits du collecteur doivent être limités, les modifications de politique consignées et les sauvegardes protégées.

### 3.8. Résilience du système de collecte

Un collecteur Syslog indisponible ne doit pas rendre aveugle toute l’exploitation. La résilience peut s’appuyer sur plusieurs collecteurs, des relais, un stockage local temporaire ou une architecture qui réplique les messages. Les capacités exactes dépendent des équipements sources et du logiciel de collecte.

Il faut évaluer les conséquences d’une interruption : certains équipements continueront à fonctionner et conserveront éventuellement des messages localement ; d’autres peuvent perdre les événements transmis pendant la panne du collecteur. UDP ne garantit pas la remise différée des messages manqués.

Pour les environnements critiques, la conception doit définir les objectifs de rétention, les comportements en cas de perte de collecteur, les capacités de stockage, les alertes et le processus de reprise. Une architecture à plusieurs collecteurs n’est utile que si leur indépendance, leur capacité et leurs règles de rétention sont vérifiées.

### 3.9. Accès, séparation des rôles et audit

La gestion de NTP et de Syslog implique des privilèges d’administration. Il faut limiter les changements à des comptes et rôles autorisés, séparer la gestion de l’infrastructure de l’analyse des journaux lorsque cela est pertinent, et conserver des traces des changements de configuration.

Le compte utilisé pour lire les événements n’a pas nécessairement besoin de pouvoir les supprimer ou modifier la politique de rétention. Les administrateurs de la plateforme de collecte peuvent être distincts des opérateurs qui consultent les journaux. Les droits minimaux réduisent les effets d’une erreur et les possibilités d’abus.

Les modifications de source NTP, de fuseau horaire, de niveaux Syslog, de destination, de transport et de rétention doivent être documentées. Toute modification susceptible de modifier la chronologie ou de réduire la visibilité d’un incident doit faire l’objet d’une revue appropriée.

### 3.10. Checklist de mise en production

Avant de considérer le service comme opérationnel, vérifie les points suivants :

- Le ou les serveurs NTP sont approuvés et accessibles depuis le réseau de gestion.
- L’état NTP indique une synchronisation effective et cohérente avec la politique de temps.
- L’heure et le fuseau affichés sont conformes à la convention du site.
- Le serveur Syslog est configuré, joignable et reçoit des événements de test.
- Les seuils Syslog couvrent les événements nécessaires sans générer un volume ingérable.
- Les messages contiennent ou permettent de retrouver l’équipement source et leur chronologie est exploitable.
- Le collecteur possède une capacité de stockage et une politique de rétention appropriées.
- Les accès de consultation et d’administration sont limités.
- Les transports et règles de filtrage respectent le besoin réel et les exigences de sécurité.
- Les procédures de panne, de reprise et de changement sont documentées.

### 3.11. Références et limites de l’exemple

La RFC 5905 décrit le protocole NTPv4 et ses algorithmes fondamentaux ; elle a été complétée ou mise à jour par plusieurs RFC, notamment celles portant sur l’authentification, les champs d’extension et la randomisation du port. Il est préférable de consulter la page de la RFC auprès de l’éditeur RFC pour suivre ses mises à jour.

La RFC 5424 décrit le format Syslog standardisé. La RFC 5426 spécifie un transport Syslog sur UDP et la RFC 5425 définit Syslog sur TLS. Les équipements réels peuvent aussi prendre en charge des comportements historiques ou propriétaires, et la configuration disponible dépend de leur système d’exploitation.

Les commandes de ce cours visent principalement Cisco IOS/IOS XE classique. Avant de les utiliser dans un réseau réel, vérifie la syntaxe et le comportement sur la version ciblée, l’impact opérationnel, la compatibilité du collecteur et les règles de sécurité de l’organisation.

> **Danger :** Une heure incorrecte et une collecte de journaux non vérifiée peuvent masquer ou déformer la chronologie d’un incident. Un message absent du collecteur ne prouve pas que l’événement ne s’est pas produit. À l’inverse, un horodatage précis ne garantit pas que l’événement décrit correctement la cause d’une panne. Maintiens des sources NTP approuvées, vérifie régulièrement la synchronisation, protège le transport et le stockage Syslog, et corrèle les journaux avec l’état des interfaces, les tables de routage et les autres données de supervision.

## Points à retenir

- **NTP synchronise l’heure ; Syslog collecte et transmet les événements.** Ce sont deux services distincts, complémentaires et à diagnostiquer séparément.
- **La configuration ne prouve pas le fonctionnement.** Vérifie l’état NTP, les associations, les horodatages, les messages locaux et la réception effective sur le collecteur.
- **La qualité de l’heure et la sécurité des journaux participent directement à la qualité du dépannage.** Utilise des sources approuvées, protège les accès, règle les niveaux de journalisation en fonction du besoin et définis une politique de conservation.

---

## Références techniques

- [RFC 5905 — Network Time Protocol Version 4: Protocol and Algorithms Specification](https://www.rfc-editor.org/rfc/rfc5905.html)
- [RFC 5424 — The Syslog Protocol](https://www.rfc-editor.org/rfc/rfc5424.html)
- [RFC 5425 — Transport Layer Security (TLS) Transport Mapping for Syslog](https://www.rfc-editor.org/rfc/rfc5425.html)
- [RFC 5426 — Transmission of Syslog Messages over UDP](https://www.rfc-editor.org/rfc/rfc5426.html)
- [Documentation Cisco IOS/IOS XE — NTP et logging](https://www.cisco.com/)
