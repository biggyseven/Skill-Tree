# NTP & Syslog - Intermédiaire

**Niveau :** Intermédiaire

Dans un réseau d’entreprise, la synchronisation de l’heure et la centralisation des journaux sont deux fonctions d’exploitation essentielles. NTP (*Network Time Protocol*) permet aux équipements de maintenir une heure cohérente malgré les dérives des horloges matérielles, les redémarrages et les variations de délai sur le réseau. Syslog permet de transmettre et de centraliser les événements produits par les routeurs, commutateurs, pare-feu, serveurs et équipements de sécurité. Pris séparément, ces mécanismes répondent à des besoins distincts ; utilisés ensemble, ils permettent de reconstituer une chronologie fiable des événements.

Une heure incohérente rend difficile la corrélation d’événements qui se produisent sur plusieurs équipements. Par exemple, un routeur peut enregistrer une perte de voisinage à 10:03:12, tandis qu’un commutateur indique une interface descendue à 09:58:12 parce que son horloge a cinq minutes de retard. Sans synchronisation, l’administrateur risque d’inverser l’ordre apparent des événements. Les systèmes d’authentification, les certificats, les journaux d’audit, les outils SIEM et certains protocoles de sécurité dépendent également d’une gestion correcte du temps.

NTP est spécifié notamment par la RFC 5905 pour NTPv4, avec des mises à jour publiées ensuite. Il utilise généralement UDP, port 123, et organise les sources de temps selon une hiérarchie de stratum. Syslog possède une architecture et un format décrits dans la RFC 5424 ; ses transports usuels comprennent UDP selon la RFC 5426 et TLS selon la RFC 5425. Il faut différencier les formats standards des variantes historiques et des commandes propres à chaque constructeur. Un équipement peut produire des messages Syslog au format historique Cisco sans implémenter exactement tous les éléments du format RFC 5424.

Ce cours se concentre sur le déploiement intermédiaire en environnement Cisco IOS/IOS XE : architecture NTP, choix des sources, calcul du décalage, hiérarchie de stratum, niveaux de gravité Syslog, sélection du transport, centralisation, filtrage, dépannage et sécurité. Les commandes proposées sont représentatives de Cisco IOS/IOS XE ; leur disponibilité et leur syntaxe exacte doivent être contrôlées sur la plateforme et la version logicielle utilisées.

> **Analogie** : Imagine une entreprise dans laquelle chaque équipe tient son propre journal de bord. Si l’horloge de l’équipe réseau avance de trois minutes, celle du serveur de sécurité retarde de deux minutes et celle du centre de données est à l’heure exacte, il devient presque impossible de reconstituer la séquence d’un incident à partir des journaux bruts. NTP joue le rôle d’un service de référence horaire partagé : les horloges se comparent à une ou plusieurs références et corrigent progressivement leur dérive. Syslog joue le rôle d’un registre central dans lequel les différentes équipes déposent leurs événements, accompagnés de l’heure et de métadonnées qui permettent de les classer. Une bonne architecture exige donc à la fois une référence de temps fiable et un circuit d’acheminement des journaux sûr. Le registre central ne doit pas être considéré comme infaillible : les messages UDP peuvent être perdus, une source peut être compromise, et des événements peuvent être supprimés localement avant leur transmission. C’est pourquoi la synchronisation, la collecte, la protection et la rétention doivent être conçues ensemble.


## 1. La théorie et les algorithmes

### 1.1. Pourquoi NTP et Syslog sont complémentaires

NTP répond à la question : « À quel moment cet événement s’est-il produit ? » Syslog répond plutôt à : « Quel événement l’équipement a-t-il observé et comment l’acheminer vers une plateforme d’analyse ? »

| Besoin opérationnel | Contribution de NTP | Contribution de Syslog |
|---|---|---|
| Dépannage réseau | Horodatage cohérent des changements | Événements de lien, voisinage, routage et interface |
| Investigation de sécurité | Corrélation temporelle entre équipements | Centralisation des alertes et événements d’audit |
| Disponibilité des services | Référence horaire partagée | Indices de panne et de récupération |
| Gestion des changements | Chronologie cohérente des interventions | Trace des changements et erreurs |
| Conformité | Réduction des écarts d’horloge | Conservation et recherche des événements |

Les deux fonctions ne garantissent pas, seules, la fiabilité complète d’une investigation. Les journaux peuvent être incomplets, certains messages peuvent être supprimés à cause de limites de mémoire, et une horloge synchronisée peut être réglée par une source erronée. Il faut compléter NTP et Syslog par le contrôle d’accès, la supervision, la conservation des journaux, une stratégie de sauvegarde et une validation régulière du fonctionnement.

### 1.2. Architecture NTP : sources et stratum

NTP organise les sources de temps en niveaux hiérarchiques appelés *strata* (singulier : *stratum*). Le stratum indique la distance logique par rapport à une référence de temps, et non une note absolue de qualité.

- **Stratum 0** : référence de temps physique ou source de référence, par exemple une horloge GPS, une horloge atomique ou une autre source spécialisée. Dans l’architecture NTP classique, un équipement de stratum 0 n’est pas un serveur réseau NTP ordinaire ; il fournit la référence à un serveur de stratum 1.
- **Stratum 1** : serveur NTP synchronisé directement sur une référence de stratum 0.
- **Stratum 2** : serveur synchronisé sur une ou plusieurs sources de stratum 1.
- **Stratum 3 et suivants** : niveaux successifs de serveurs qui apprennent l’heure d’autres sources NTP.
- **Stratum 16** : valeur utilisée pour signaler un état non synchronisé dans les représentations NTP habituelles.

Le stratum ne suffit pas à déterminer le meilleur serveur. Un serveur de stratum 2 stable, accessible et bien caractérisé peut être préférable à un serveur de stratum 1 joignable par un chemin réseau instable. La qualité dépend notamment du délai, de la dispersion, du bruit, de la stabilité de la source et de la cohérence entre sources.

```text
              Référence horaire physique
              GPS / horloge de référence
                         |
                    +---------+
                    | Stratum |
                    |    1    |
                    +---------+
                         |
                 Réseau d'entreprise
                         |
                    +---------+
                    | Stratum |
                    |    2    |
                    +---------+
                     /       \
                    /         \
              +---------+  +---------+
              | Stratum |  | Stratum |
              |    3    |  |    3    |
              +---------+  +---------+
                 |              |
             Clients NTP     Clients NTP
```

Un serveur peut à la fois être client d’une source amont et fournir l’heure à des clients en aval. Dans une architecture d’entreprise, il est courant de déployer plusieurs serveurs internes qui se synchronisent sur des sources approuvées, puis de demander aux routeurs, commutateurs, serveurs et équipements de sécurité d’utiliser seulement ces serveurs internes.

### 1.3. UDP/123 et échange client-serveur

NTP utilise typiquement UDP sur le port 123. Le client envoie une requête et le serveur retourne un message qui contient des horodatages permettant d’estimer le décalage et le délai. Comme UDP ne fournit pas de session fiable comparable à TCP, la qualité de synchronisation dépend des mécanismes NTP, de la répétition des échanges et du filtrage statistique effectué par l’implémentation.

Le mode client-serveur est le mode le plus courant pour les équipements d’entreprise. NTP supporte également d’autres modes, mais il n’est pas nécessaire de les activer pour un déploiement classique composé de serveurs internes et de clients réseau.

Les règles réseau doivent autoriser les échanges requis. Un client doit pouvoir envoyer des requêtes à la source horaire et recevoir les réponses associées. Une ACL qui autorise le trafic dans un seul sens sans tenir compte du fonctionnement stateful ou stateless du chemin peut bloquer la synchronisation. Il faut aussi vérifier les routes retour, le NAT éventuel et les politiques de sécurité intermédiaires.

NTP n’utilise normalement pas TCP/123. Une règle qui n’ouvre que TCP/123 ne permet pas le fonctionnement NTP classique. De même, Syslog UDP/514 et NTP UDP/123 remplissent des rôles différents : ils ne doivent pas être confondus dans une politique de pare-feu.

### 1.4. Les quatre horodatages NTP

L’échange NTP client-serveur classique emploie quatre horodatages, souvent notés T1, T2, T3 et T4 :

- **T1** : moment où le client transmet la requête ;
- **T2** : moment où le serveur reçoit la requête ;
- **T3** : moment où le serveur transmet la réponse ;
- **T4** : moment où le client reçoit la réponse.

À partir de ces valeurs, on estime le décalage (offset) entre les horloges et le délai aller-retour (round-trip delay). Dans le modèle simplifié, les équations sont :

\[
\text{offset} = \theta = \frac{(T2-T1)+(T3-T4)}{2}
\]

\[
\text{delay} = \delta = (T4-T1)-(T3-T2)
\]

L’offset estime l’écart entre l’horloge du client et celle du serveur. Un offset positif ou négatif doit être interprété selon la convention de signe de la commande ou de l’outil utilisé. Le délai estime le temps aller-retour mesuré, diminué du temps passé par le serveur à traiter la requête.

Ces équations reposent sur une hypothèse approximative de symétrie des délais aller et retour. Si la congestion, le routage asymétrique ou le traitement créent de fortes différences, l’estimation peut être biaisée. NTP atténue les effets du bruit au moyen d’échantillons successifs, de filtres, de sélections de sources et d’algorithmes de discipline de l’horloge. Il ne suffit donc pas de calculer un offset sur un seul paquet pour déterminer la précision durable d’un système.

### 1.5. Offset, delay, jitter et dispersion

Les outils NTP présentent différents paramètres qui ne doivent pas être confondus.

| Paramètre | Signification générale | Comment l’interpréter |
|---|---|---|
| Offset | Décalage estimé entre horloges | Une valeur élevée indique une correction potentiellement importante |
| Delay | Délai de communication mesuré | Un délai variable ou élevé peut augmenter l’incertitude |
| Jitter | Variation statistique des mesures d’offset ou de délai selon l’outil | Une valeur basse traduit généralement des mesures plus stables |
| Dispersion | Estimation de l’incertitude qui s’accumule dans les mesures | Une valeur croissante peut signaler une source moins fiable ou ancienne |
| Stratum | Distance logique à la référence | Ne constitue pas seul un score de précision |

Les noms exacts et le calcul des champs affichés diffèrent selon le système d’exploitation et la plateforme. Pour diagnostiquer, il faut établir une tendance au fil du temps plutôt que réagir à une mesure isolée. Une source qui alterne rapidement entre synchronisée et non synchronisée, un offset qui dérive et un jitter qui augmente constituent des signaux plus utiles qu’un unique résultat ponctuel.

### 1.6. Dérive de l’horloge et discipline temporelle

Les horloges matérielles ne restent pas parfaitement stables. Leur fréquence varie avec la température, le vieillissement, les caractéristiques du composant et la qualité de l’oscillateur. Une horloge locale peut ainsi gagner ou perdre une petite fraction de seconde par jour.

NTP n’agit pas simplement comme un mécanisme qui remplace l’heure locale à chaque réponse. L’implémentation suit des échantillons, estime la dérive et ajuste progressivement l’horloge afin d’éviter des sauts intempestifs qui rendraient les applications instables. Pour une différence très importante, certains systèmes ou certaines configurations peuvent effectuer une correction brusque lors de l’initialisation ; le comportement dépend de l’implémentation et des paramètres.

Un changement brusque du temps système peut avoir un impact sur les ordonnancements, les journaux, les certificats, les bases de données et les applications qui supposent que les horodatages progressent normalement. Les déploiements doivent donc éviter de modifier manuellement et fréquemment l’heure d’un équipement qui devrait être synchronisé par NTP.

Il faut distinguer l’heure UTC de la présentation locale. L’heure de référence devrait être maintenue de manière cohérente ; le fuseau horaire sert à afficher une heure locale aux opérateurs. Deux appareils peuvent être synchronisés sur le même instant UTC tout en affichant des heures locales différentes si leurs fuseaux sont configurés différemment.

### 1.7. Sélection et redondance des sources NTP

Il est recommandé de configurer plusieurs sources de temps approuvées lorsque la plateforme le permet et que la politique de l’organisation l’exige. La redondance permet de résister à la panne d’une source et aide le mécanisme de sélection à repérer une source aberrante.

Une politique de temps d’entreprise typique peut comporter :

1. plusieurs serveurs internes de temps ;
2. des sources amont choisies et documentées ;
3. une connectivité contrôlée vers ces sources ;
4. une surveillance du stratum, de l’offset et de l’état de synchronisation ;
5. une restriction des clients autorisés à interroger les serveurs internes ;
6. une procédure de remplacement et de validation des sources.

Configurer quatre sources publiques quelconques ne garantit pas automatiquement une meilleure précision. Les sources doivent être fiables, indépendantes autant que possible et compatibles avec la politique de sécurité. Une seule source interne mal synchronisée peut distribuer une heure fausse à des dizaines ou des centaines d’équipements.

Le paramètre `prefer` disponible sur certaines plateformes Cisco permet d’indiquer une source préférée. Il ne faut pas interpréter ce mot comme une garantie absolue que la source restera sélectionnée si elle est jugée invalide ou inaccessible. Les règles de sélection dépendent de la qualité et de l’état des associations NTP.

### 1.8. Configurer NTP côté client, serveur et équipement Cisco

Dans l’architecture d’entreprise la plus fréquente, un routeur ou un commutateur Cisco est client NTP et interroge un ou plusieurs serveurs internes. Certains modèles et versions peuvent également fournir l’heure à d’autres clients, mais cette capacité et la configuration associée doivent être vérifiées.

Exemple de configuration de client NTP :

```cisco
ntp server 192.0.2.10 prefer
ntp server 192.0.2.11
clock timezone WAT 1 0
service timestamps log datetime msec localtime show-timezone
```

Les adresses `192.0.2.10` et `192.0.2.11` appartiennent à un bloc d’exemple documentaire. Elles doivent être remplacées par les adresses réelles des serveurs NTP internes. Le nom de fuseau `WAT` et le décalage d’une heure sont des exemples ; vérifie le fuseau et les règles locales avant de les appliquer. Sur les équipements où l’horodatage Syslog en UTC est préféré, ne configure pas `localtime` et documente cette décision.

La commande `service timestamps log datetime msec` ajoute une date et une heure à certains messages de journalisation, avec une précision d’affichage en millisecondes. Elle ne signifie pas que l’horloge elle-même est exacte à la milliseconde. La qualité de l’horodatage dépend de la synchronisation effective, du comportement de l’équipement et de la précision de sa source.

Pour examiner l’état temporel, Cisco IOS/IOS XE propose généralement des commandes telles que :

```cisco
show clock detail
show ntp status
show ntp associations
show ntp associations detail
```

La disponibilité exacte des commandes dépend du système logiciel. Il faut vérifier que l’horloge est effectivement synchronisée, qu’une association est valide, que le stratum n’indique pas un état non synchronisé et que l’offset reste dans la tolérance opérationnelle.

### 1.9. NTP et sécurité

NTP est un service critique mais souvent insuffisamment protégé. Si un attaquant peut faire accepter une référence horaire erronée, les conséquences peuvent dépasser un simple affichage incorrect. Des certificats peuvent sembler expirés ou pas encore valides, les journaux peuvent devenir difficiles à corréler et des systèmes d’authentification peuvent réagir de façon inattendue.

Les mesures utiles comprennent :

- autoriser les requêtes NTP uniquement vers les serveurs approuvés ;
- limiter les clients capables d’interroger un serveur interne ;
- réduire l’exposition des serveurs de temps à Internet ;
- maintenir le logiciel et les paramètres de sécurité à jour ;
- surveiller les changements de stratum, les écarts et les sources sélectionnées ;
- éviter de considérer une source comme fiable uniquement parce qu’elle répond ;
- utiliser un mécanisme d’authentification pris en charge lorsque le modèle de menace et l’architecture le justifient.

NTP traditionnel n’offre pas, dans sa configuration de base, les garanties cryptographiques d’un transport chiffré moderne. Network Time Security (NTS), défini notamment par la RFC 8915, prévoit une méthode de sécurisation de NTP qui utilise TLS pour l’établissement des paramètres de sécurité puis NTP pour les échanges de temps. Son support dépend des systèmes ; il ne faut pas supposer qu’un routeur Cisco donné l’implémente sans vérifier sa documentation.

### 1.10. Syslog : rôle et architecture

Syslog est un mécanisme de journalisation utilisé pour transporter des messages d’événement vers un collecteur. Un réseau bien conçu centralise les journaux sur un ou plusieurs serveurs afin de rendre possible la recherche, la corrélation, la conservation et l’analyse des événements.

Les principaux rôles sont :

- **Originator** : équipement ou application qui produit un message ;
- **Transport sender** : composant qui transmet le message ;
- **Relay** : intermédiaire qui reçoit puis relaie des messages ;
- **Collector/receiver** : système qui reçoit les événements pour les stocker ou les traiter.

```text
 +----------+       Syslog       +------------------+
 | Routeur  |-------------------->|                  |
 +----------+                     |                  |
                                  | Collecteur Syslog|
 +----------+       Syslog       | / SIEM           |
 | Switch   |-------------------->|                  |
 +----------+                     |                  |
                                  +--------+---------+
 +----------+       Syslog                |
 | Pare-feu |-----------------------------+
 +----------+                             |
                                          v
                               Recherche / corrélation
                               Alertes / conservation
```

Les sources envoient généralement leurs messages au collecteur via un réseau de gestion ou une interface source spécifiée. Le collecteur peut effectuer une normalisation, un enrichissement, un indexage et une conservation. Le flux ne garantit pas que tous les événements seront effectivement enregistrés : le transport, les files d’attente, la configuration de gravité, les limites de stockage et le traitement côté collecteur influencent le résultat.

### 1.11. Format des messages et niveau de gravité

La RFC 5424 définit un format structuré de Syslog comprenant notamment une priorité, une version, un horodatage, un nom d’hôte, une application, un identifiant de processus, un identifiant de message et des données structurées. Les implémentations historiques, y compris de nombreuses versions Cisco IOS, peuvent produire des messages différents ou simplifiés. En exploitation, il faut donc distinguer le format du message source de la manière dont le collecteur le parse et l’indexe.

La priorité (PRI) standard est dérivée de la facility et de la sévérité :

\[
PRI = 8 \times Facility + Severity
\]

Les sévérités Syslog habituelles sont :

| Valeur | Nom français courant | Nom Syslog | Interprétation |
|---:|---|---|---|
| 0 | Urgence | Emergency | Système inutilisable |
| 1 | Alerte | Alert | Action immédiate nécessaire |
| 2 | Critique | Critical | Condition critique |
| 3 | Erreur | Error | Erreur nécessitant une attention |
| 4 | Avertissement | Warning | Condition potentiellement problématique |
| 5 | Notification | Notice | Événement important mais non erroné |
| 6 | Informationnel | Informational | Message informatif normal |
| 7 | Débogage | Debugging | Informations détaillées de diagnostic |

**Plus la valeur numérique de sévérité est basse, plus le niveau est grave.** Une configuration demandant des messages jusqu’à `informational` transmet normalement les niveaux 0 à 6 ; elle ne doit pas être interprétée comme « seulement les messages dont la valeur est supérieure à 6 ».

Il faut aussi distinguer la sévérité Syslog du type de message. Un message d’interface ou de protocole peut être classé à différents niveaux selon l’implémentation. La gravité n’est pas une mesure universelle de l’impact métier ; le SIEM ou la politique d’exploitation peut avoir besoin d’une classification supplémentaire.

### 1.12. Facilities Syslog

La *facility* représente l’origine fonctionnelle du message dans l’architecture Syslog. Des valeurs historiques ont été associées à des sous-systèmes Unix ; des valeurs `local0` à `local7` sont souvent utilisées par les applications et équipements pour séparer les flux.

Sur les équipements Cisco, la commande `logging facility` permet, sur les plateformes qui la prennent en charge, de choisir la facility envoyée au collecteur. Elle peut être définie pour répondre à la politique du collecteur, par exemple pour différencier les journaux du réseau de ceux d’un serveur applicatif. La facility ne remplace pas le nom de l’équipement ni l’identification de la source.

Une convention cohérente est indispensable. Si chaque site utilise des facilities différentes sans documentation, les filtres et tableaux de bord deviennent plus difficiles à maintenir. Il faut harmoniser les noms, les adresses de source, les fuseaux horaires, les niveaux de gravité et les règles de classification.

### 1.13. Transports Syslog : UDP, TCP et TLS

Les déploiements historiques emploient souvent UDP/514. Ce transport est léger et largement supporté, mais il ne fournit pas de garantie de livraison : les messages peuvent être perdus lors d’une congestion, d’un filtrage, d’une panne de chemin ou d’une saturation du collecteur. UDP ne garantit pas non plus l’authenticité ni la confidentialité des messages.

La RFC 5426 décrit le transport Syslog sur UDP et rappelle que ses propriétés de fiabilité et de sécurité sont limitées. La RFC 5425 définit Syslog sur TLS et utilise le port TCP 6514 comme port par défaut. TLS peut apporter confidentialité, intégrité et authentification des pairs si les certificats et la validation sont correctement configurés.

| Transport | Port conventionnel | Avantages | Limites |
|---|---:|---|---|
| UDP | 514 | Simple, faible surcharge, très répandu | Perte possible, pas de chiffrement ni authentification intégrée |
| TCP | Dépend de l’implémentation/configuration | Livraison en flux, meilleure gestion de congestion qu’UDP dans de nombreux scénarios | Un flux TCP seul ne garantit ni chiffrement ni authentification applicative |
| TLS sur TCP | 6514 par défaut selon RFC 5425 | Confidentialité et intégrité du transport, authentification par certificats si configurée | Support variable, gestion des certificats et des versions nécessaire |

Ne présume pas qu’une commande IOS générique supporte Syslog TLS simplement parce que la RFC existe. Le support dépend du modèle, de la version et de la licence éventuelle. Vérifie les capacités exactes du collecteur et de la plateforme avant de concevoir le transport. Si un équipement ne supporte que UDP/514, isole le trafic Syslog sur un réseau de gestion protégé et évalue un relais sécurisé comme point de transition, selon l’architecture.

### 1.14. Journalisation locale, console, mémoire tampon et serveur distant

Sur Cisco IOS/IOS XE, les messages peuvent être envoyés vers plusieurs destinations :

- la console ;
- les sessions VTY ou terminal monitor ;
- la mémoire tampon locale ;
- le collecteur Syslog distant.

Les commandes qui activent une destination ne sont pas nécessairement équivalentes. Par exemple, `logging buffered` active une mémoire tampon locale, tandis que `logging host` configure une destination distante. Les messages qui apparaissent à l’écran pendant une session SSH ne sont pas automatiquement une preuve de livraison au collecteur central.

La taille du tampon et le niveau de gravité déterminent le nombre de messages conservés et la quantité de détails disponibles. Un niveau très verbeux, notamment debugging, peut générer un volume élevé et affecter les ressources de l’équipement. Il faut employer le niveau adapté et augmenter temporairement le détail pendant une intervention si nécessaire.

Les journaux locaux peuvent disparaître après un redémarrage ou être écrasés lorsque le tampon se remplit. La centralisation réduit ce risque, mais seulement si le transport fonctionne et si le collecteur conserve effectivement les messages. Les systèmes à forte exigence de sécurité devraient conserver les journaux sur un serveur avec contrôle d’accès, horodatage cohérent, rétention définie et sauvegarde.

### 1.15. Filtrage et seuils de sévérité Cisco

La commande représentative suivante configure le niveau de journalisation transmis à un serveur distant :

```cisco
logging trap informational
```

Sur les plateformes IOS classiques, `logging trap` détermine le seuil des messages envoyés au serveur Syslog. Un seuil `informational` comprend en général les sévérités 0 à 6 ; les messages de débogage de niveau 7 ne sont pas inclus. La commande exacte et ses effets doivent être confirmés dans la documentation de la plateforme.

Un seuil trop restrictif peut éliminer des événements nécessaires à l’investigation. Un seuil trop permissif peut saturer la bande passante, les disques ou l’indexation, particulièrement lorsque des traces de débogage sont émises. Il est recommandé de définir un profil initial raisonnable, de vérifier l’impact sur le collecteur et d’ajuster en fonction du risque et des besoins.

Les filtres ne doivent pas être choisis uniquement en fonction du volume. Les événements de modification de configuration, d’authentification, d’échec de liaison, de changements de voisinage et de sécurité peuvent être prioritaires. L’importance dépend toutefois de la fonction de l’équipement et des objectifs de surveillance.

### 1.16. Horodatage des journaux et fuseaux horaires

Un message centralisé n’est utile pour la corrélation que si son horodatage est compréhensible et cohérent. Il faut décider si l’organisation utilise UTC ou une représentation locale, puis appliquer cette convention partout où c’est possible.

Sur IOS/IOS XE, des commandes représentatives sont :

```cisco
service timestamps log datetime msec localtime show-timezone
clock timezone WAT 1 0
```

La première active des horodatages de journal avec date, millisecondes, heure locale et indication de fuseau lorsque le logiciel le permet. La seconde illustre un fuseau horaire ; remplace-la selon la politique réelle. Si le collecteur convertit tous les messages vers UTC, la convention doit être documentée afin d’éviter les doubles conversions ou des erreurs d’interprétation.

Ne confonds pas l’affichage du fuseau et l’état de synchronisation NTP. Une horloge peut être exacte en UTC mais présenter un fuseau incorrect. Inversement, un fuseau correct ne prouve pas que l’horloge est synchronisée.

Pour un système de supervision réparti sur plusieurs pays, UTC est souvent plus simple pour les recherches et la corrélation. Une interface de consultation peut ensuite convertir les horodatages vers le fuseau local de l’analyste sans altérer la valeur de référence stockée.

### 1.17. Syslog fiable, disponibilité et rétention

Il faut considérer Syslog comme une chaîne de traitement plutôt que comme une seule commande : émission, transport, réception, parsing, indexation, alerte, stockage et rétention. Un message peut quitter le routeur et ne jamais apparaître dans le tableau de bord si le collecteur écoute sur le mauvais port, si le format est mal interprété ou si une règle d’ingestion le rejette.

Une architecture robuste prévoit :

- un ou plusieurs collecteurs dimensionnés pour le volume attendu ;
- une surveillance de l’ingestion et de la dernière réception par source ;
- une vérification de la capacité de stockage ;
- des politiques de rétention et de rotation ;
- un contrôle d’accès aux journaux ;
- une stratégie de sauvegarde et une protection contre la suppression non autorisée ;
- une procédure de test qui génère un événement connu et vérifie sa présence dans le collecteur.

Lorsque les événements sont critiques, il faut choisir un transport offrant des garanties adaptées et vérifier les limites du produit. Une connexion TCP ou TLS améliore certaines propriétés, mais ne remplace pas le contrôle de capacité, la gestion des erreurs, les sauvegardes et la détection des périodes où aucune donnée n’est reçue.

### 1.18. Modèle intégré NTP + Syslog

```text
                 Sources de temps approuvées
                    +-------------+
                    | NTP amont   |
                    +------+------+ 
                           |
                  UDP/123  |
                           v
                  +----------------+
                  | NTP interne    |
                  | A / B          |
                  +-------+--------+
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
          +-------+   +--------+   +--------+
          | Routeur|  | Switch |   | Pare-feu|
          +---+---+   +---+----+   +---+----+
              |           |            |
              +-----------+------------+
                   Syslog (514 ou
                transport sécurisé)
                          |
                          v
                 +------------------+
                 | Collecteur / SIEM|
                 +--------+---------+
                          |
                 Corrélation / alerte
                 Rétention / recherche
```

Tous les équipements doivent atteindre les serveurs NTP approuvés et les collecteurs Syslog par des chemins contrôlés. Une interface source dédiée, par exemple une Loopback ou une interface de gestion selon l’architecture, peut stabiliser l’identité IP de la source et simplifier les règles du collecteur. Cette sélection doit être cohérente avec le routage, la VRF utilisée et la politique d’accès.

> **Piège :** Une heure affichée avec des millisecondes n’est pas nécessairement exacte à la milliseconde. La précision de l’affichage, l’état de synchronisation NTP, la qualité de la source et les délais du réseau sont des notions différentes. De la même manière, une commande qui configure un serveur Syslog ne prouve pas que le serveur reçoit les messages. Il faut valider le chemin complet avec les commandes d’état et un événement de test observé côté collecteur.


## 2. Configuration et Pratique

### 2.1. Objectif du laboratoire

Le laboratoire présente un routeur Cisco IOS/IOS XE et un commutateur administrable qui utilisent des serveurs internes de temps et un collecteur Syslog. Les adresses utilisées appartiennent à des plages de documentation ; remplace-les avant tout déploiement réel.

| Élément | Adresse de documentation | Fonction |
|---|---|---|
| Serveur NTP-A | 192.0.2.10 | Source de temps principale |
| Serveur NTP-B | 192.0.2.11 | Source de temps secondaire |
| Collecteur Syslog | 198.51.100.50 | Réception des journaux |
| Loopback du routeur | 198.51.100.1/32 | Adresse source stable d’administration |
| VLAN de gestion | 198.51.100.0/24 | Segment logique d’administration, exemple uniquement |

Les réseaux `192.0.2.0/24` et `198.51.100.0/24` sont réservés à la documentation. Ils ne doivent pas être utilisés comme plan d’adressage de production sans contexte de laboratoire approprié.

### 2.2. Configuration horaire complète du routeur

```cisco
hostname R1
!
clock timezone WAT 1 0
!
service timestamps log datetime msec localtime show-timezone
!
ntp server 192.0.2.10 prefer
ntp server 192.0.2.11
!
interface Loopback0
 description SOURCE_STABLE_ADMINISTRATION
 ip address 198.51.100.1 255.255.255.255
!
```

Explications :

- `hostname` définit l’identifiant de l’équipement ; il est important que le nom envoyé dans les journaux soit documenté.
- `clock timezone` configure la présentation locale de l’heure ; adapte le fuseau à la convention de l’entreprise.
- `service timestamps log datetime msec ...` permet aux journaux locaux d’afficher une date et une heure plus précises que l’absence d’horodatage.
- `ntp server` déclare une source de synchronisation. La commande `prefer` marque une source préférée lorsque les autres conditions de sélection sont compatibles.
- `Loopback0` représente une source d’adresse stable pour les messages d’administration. Si cette interface n’existe pas ou ne correspond pas à la conception, choisis une interface de gestion existante.

Dans un environnement réel, assure-toi que la loopback est joignable depuis le serveur NTP et le collecteur Syslog, et que les ACL permettent les échanges attendus. Une adresse source stable ne sert à rien si le chemin retour est absent.

### 2.3. Vérifier la synchronisation NTP

Exécute les commandes de diagnostic disponibles sur la plateforme :

```cisco
show clock detail
show ntp status
show ntp associations
show ntp associations detail
show running-config | include ntp|clock timezone|service timestamps
```

Interprétation générale :

- La date et l’heure doivent être plausibles et suivre la convention de fuseau retenue.
- L’état NTP doit indiquer une synchronisation valide, lorsque la plateforme présente ce champ.
- Une association doit être accessible et exploitable ; une simple présence dans la configuration ne suffit pas.
- Le stratum ne doit pas signaler un état non synchronisé.
- L’offset et les valeurs de qualité doivent se stabiliser selon les objectifs de l’organisation.

Si l’horloge n’est pas synchronisée, vérifie d’abord la résolution IP et le routage vers les serveurs, puis les ACL/pare-feu, la disponibilité des serveurs et enfin les paramètres NTP. Évite de modifier simultanément le fuseau, les serveurs et les filtres : la démarche doit isoler la cause.

### 2.4. Configuration Syslog centralisée

Exemple de base :

```cisco
service timestamps log datetime msec localtime show-timezone
logging host 198.51.100.50
logging trap informational
logging buffered 64000 informational
logging source-interface Loopback0
!
```

Les éléments principaux :

- `logging host` déclare le collecteur Syslog distant.
- `logging trap informational` définit le seuil de gravité des messages transmis au collecteur sur les plateformes IOS usuelles.
- `logging buffered` conserve une copie locale en mémoire tampon. La taille et le seuil doivent être ajustés à la mémoire disponible et aux besoins.
- `logging source-interface` fixe l’interface utilisée comme adresse source pour les messages distants, si la plateforme et la configuration le permettent.

Il est possible que les commandes `logging host`, `logging trap` ou `logging source-interface` diffèrent selon les versions. Dans certaines interfaces de configuration, plusieurs destinations peuvent être définies séparément. Vérifie `show logging` et la documentation de la version avant de réutiliser un exemple sur un équipement de production.

Le seuil `informational` comprend en principe les niveaux de sévérité 0 à 6 et exclut le niveau 7 (debug). Pour réduire le volume, un niveau plus restrictif peut être retenu, mais cette décision doit être testée au regard des événements nécessaires aux investigations.

### 2.5. Configuration du niveau console et VTY

Le comportement d’affichage console et terminal peut être contrôlé séparément. Dans un laboratoire, les commandes suivantes sont des exemples dont la prise en charge dépend de la plateforme :

```cisco
logging console warnings
logging monitor informational
```

`logging console` définit les messages envoyés à la console physique ; `logging monitor` s’applique à l’affichage des messages vers les sessions de terminal qui ont activé le suivi des journaux. Il ne faut pas confondre l’affichage dans une session SSH et la transmission au collecteur distant.

Des messages nombreux pendant une intervention peuvent perturber une session de configuration. En environnement de production, limite le niveau de console et active l’affichage terminal uniquement lorsque cela est utile. Privilégie le serveur central et la mémoire tampon pour les événements persistants.

### 2.6. Transport sécurisé et limites de plateforme

Lorsque la plateforme supporte Syslog sur TLS ou un transport fiable, configure-le conformément à la documentation de la version et au mécanisme accepté par le collecteur. La RFC 5425 désigne le port TCP 6514 comme port par défaut de Syslog sur TLS, mais cela ne signifie pas que toutes les versions Cisco IOS/IOS XE disposent d’une commande universelle pour ce transport.

Avant d’imposer TLS, vérifie :

1. que le routeur ou commutateur supporte le transport demandé ;
2. que le collecteur écoute sur le port prévu ;
3. que les certificats et leur validation sont configurés correctement ;
4. que la date NTP est correcte pour la validation des certificats ;
5. que les ACL et le routage autorisent le flux ;
6. que l’ingestion côté collecteur confirme la réception.

Si le transport disponible est UDP, limite les sources et destinations aux équipements attendus, transporte le flux sur un segment de gestion contrôlé et protège le collecteur. Ne présente pas UDP comme un transport chiffré ou garanti : il peut perdre des messages et n’assure pas intrinsèquement l’identité de l’émetteur.

### 2.7. Protéger le service NTP

La protection de NTP doit être mise en œuvre sur les équipements qui fournissent le temps et sur les équipements qui le consomment. Les règles suivantes décrivent la politique, mais leur syntaxe exacte doit être adaptée à l’architecture :

- autoriser les clients internes prévus à interroger les serveurs NTP internes ;
- limiter les sources NTP configurées sur les équipements ;
- éviter d’exposer publiquement un serveur de temps d’entreprise sans raison ;
- filtrer le trafic UDP/123 à la frontière ;
- surveiller les sources sélectionnées et les changements de stratum ;
- documenter la source primaire, la source de secours et la procédure de remplacement.

Si le routeur fournit lui-même un service NTP, la commande exacte pour restreindre les clients dépend du mode, de l’IOS et de la configuration d’accès. Il ne faut pas recopier une ACL générique sans vérifier si elle contrôle les requêtes client, les paquets reçus ou d’autres fonctions. Utilise les mécanismes de limitation et d’authentification documentés pour le rôle précis du routeur.

### 2.8. Tester l’arrivée des journaux

La procédure de validation doit comprendre un événement connu, par exemple un changement contrôlé de l’état d’une interface de laboratoire ou une opération de configuration qui est journalisée. Sur un équipement de production, ne fais pas tomber une interface simplement pour tester sans approbation : utilise un événement sans impact ou un environnement de test.

Vérifie ensuite :

1. que le message apparaît dans `show logging` ou dans la mémoire tampon locale ;
2. que la destination Syslog et le niveau de gravité sont configurés ;
3. que la source IP observée au collecteur correspond à l’identité attendue ;
4. que le collecteur reçoit le message sur le transport et le port prévus ;
5. que l’horodatage est correct et correctement converti ;
6. que le message est indexé et consultable dans l’interface du collecteur/SIEM.

Cette méthode isole les pannes par étape. Si le message n’existe pas localement, le problème est probablement au niveau de la génération ou du seuil. S’il existe localement mais pas au collecteur, examine le transport et le chemin réseau. S’il est reçu mais absent des recherches, examine le parser, les règles d’ingestion et les champs indexés.

### 2.9. Commandes opérationnelles Syslog

Les commandes suivantes sont couramment disponibles sous une forme proche sur Cisco IOS/IOS XE :

```cisco
show logging
show running-config | include logging|service timestamps
show interfaces
show ip route 198.51.100.50
ping 198.51.100.50 source Loopback0
```

`show logging` indique notamment des paramètres du système de journalisation, l’état du tampon et des messages mémorisés. La sortie exacte dépend de la version. La commande de ping avec source permet de tester la connectivité en utilisant la source configurée, si la syntaxe est prise en charge. Un ping réussi ne prouve pas que Syslog est autorisé, car ICMP et UDP/514 sont des flux différents.

Il est utile de vérifier les compteurs d’interface, la route vers le collecteur et les ACL sur chaque segment traversé. Si une VRF est utilisée pour l’administration, assure-toi que les commandes NTP/Syslog et les mécanismes de source-interface utilisent la VRF correcte ; les syntaxes sont différentes selon les plateformes et les versions.

### 2.10. Procédure de dépannage NTP

**Symptôme : l’horloge n’est pas synchronisée.**

Commence par afficher la date et l’état NTP. Vérifie ensuite l’adresse configurée, la connectivité et la route retour. Un serveur NTP peut être joignable par ICMP tout en refusant ou en ne recevant pas le trafic UDP/123.

**Symptôme : la source apparaît mais n’est pas sélectionnée.**

Vérifie l’état de l’association, le stratum, l’offset, la dispersion et les statistiques disponibles. Une entrée de configuration valide n’est pas une preuve de synchronisation. Contrôle aussi si une autre source est sélectionnée et si la politique de sécurité bloque certaines réponses.

**Symptôme : l’heure est décalée d’un nombre fixe d’heures.**

Vérifie le fuseau horaire et la convention d’affichage avant de conclure que NTP est en panne. Une erreur de fuseau peut produire un décalage constant alors que le temps UTC est correct.

**Symptôme : l’heure saute ou dérive.**

Examine l’indépendance et la stabilité des sources, la qualité du chemin réseau, les événements de redémarrage et les modifications manuelles. Ne change pas immédiatement de serveur vers une source publique inconnue ; confirme d’abord le problème et compare plusieurs sources approuvées.

### 2.11. Procédure de dépannage Syslog

**Symptôme : aucun message distant.**

Vérifie le seuil de gravité, la destination, la source IP, le routage et les ACL. Confirme que le collecteur écoute réellement sur le protocole et le port configurés. La présence de messages dans le tampon local démontre qu’ils ont été générés, mais ne prouve pas leur livraison distante.

**Symptôme : seuls certains messages arrivent.**

Contrôle les seuils et le volume d’événements. Vérifie si des messages ont été filtrés par l’équipement, perdus par UDP, supprimés par une file d’attente, rejetés par une règle de parsing ou exclus de l’indexation. Compare les journaux bruts reçus avec les recherches du SIEM.

**Symptôme : l’identité de la source est incorrecte.**

Vérifie l’interface source, le routage et les éventuelles traductions d’adresses. Si l’équipement a plusieurs interfaces, la source utilisée peut ne pas être celle attendue. La normalisation au collecteur doit tenir compte de cette configuration.

**Symptôme : les messages sont décalés dans le temps.**

Vérifie NTP, le fuseau horaire, la présence du champ d’heure dans le message et les conversions effectuées à l’ingestion. Le serveur Syslog peut stocker en UTC tandis que la console affiche une heure locale ; la politique de normalisation doit être documentée.

### 2.12. Exploitation et contrôle du changement

Toute modification des sources NTP, des transports Syslog ou des seuils de gravité doit être documentée. La procédure de changement devrait préciser l’objectif, la configuration avant intervention, le résultat attendu, le test de validation, les risques et la procédure de retour arrière.

Avant une modification :

- collecte l’état NTP et Syslog actuel ;
- sauvegarde la configuration ;
- vérifie la connectivité vers les serveurs ;
- confirme les adresses, ports et règles de sécurité ;
- identifie une manière de générer un événement de test ;
- évite d’effectuer simultanément plusieurs changements non liés.

Après la modification, contrôle l’état NTP, la stabilité de l’offset, la réception d’un message Syslog connu, l’horodatage, l’adresse source et l’indexation côté collecteur. Le changement n’est pas terminé uniquement parce que le routeur a accepté les commandes.

> **Astuce :** Pour isoler rapidement un problème, traite séparément le plan de contrôle NTP et le pipeline Syslog. Contrôle d’abord `show ntp status` et `show ntp associations`, puis vérifie les messages locaux avec `show logging`, la configuration avec `show running-config` et enfin la réception côté collecteur. Un ping vers le serveur ne teste ni UDP/123 ni UDP/514. Pour Syslog, l’ultime preuve est l’apparition d’un événement de test connu dans le collecteur avec l’identité et l’horodatage attendus.


## 3. Dépannage et Sécurité

### 3.1. Construire un plan de diagnostic reproductible

Un plan de diagnostic efficace doit distinguer la génération du message, son transport, sa réception, son traitement et sa conservation. Pour NTP, il faut distinguer l’accessibilité réseau du serveur, la validité de l’association et la synchronisation effective de l’horloge. Les observations doivent être recueillies avant d’apporter des modifications.

Pour chaque équipement, enregistre au minimum :

- date et heure affichées ;
- fuseau horaire ;
- état NTP et source sélectionnée ;
- stratum, offset et paramètres de qualité exposés ;
- liste des serveurs NTP configurés ;
- configuration Syslog et seuil de gravité ;
- source IP Syslog et transport utilisé ;
- dernier message reçu côté collecteur ;
- erreurs de transport, de parsing ou d’indexation signalées.

Ces informations permettent d’établir une référence avant incident. Il est difficile de diagnostiquer une dérive ou une disparition de journaux si aucune valeur normale n’a été documentée.

### 3.2. Séparer les problèmes de temps des problèmes de fuseau

Une erreur constante d’une ou plusieurs heures suggère souvent un mauvais fuseau, un changement saisonnier mal géré ou une conversion en double. Une dérive progressive suggère plutôt un problème de synchronisation ou d’oscillateur. Un décalage qui change de façon irrégulière peut venir d’une source instable, d’un changement de source ou de délais réseau variables.

Le diagnostic doit comparer la date système, la référence UTC et les horodatages effectivement reçus au collecteur. La sortie de `show clock detail` peut fournir des informations utiles sur certaines plateformes Cisco. Pour les systèmes qui exportent un horodatage au format Syslog, vérifie si le message comporte un fuseau explicite ou si le collecteur l’interprète selon une hypothèse de configuration.

Ne tente pas de corriger un décalage en configurant arbitrairement le fuseau pour compenser une mauvaise source NTP : cela masque la cause réelle et peut faire diverger les applications qui attendent une heure système cohérente.

### 3.3. Protéger l’intégrité des journaux

Les journaux sont une source de preuve pour les incidents réseau et de sécurité. Un attaquant qui peut injecter des événements, modifier les paramètres d’heure, supprimer des fichiers ou désactiver l’expédition peut compliquer l’investigation.

Les contrôles essentiels sont :

- limiter l’administration du collecteur aux comptes autorisés ;
- utiliser des comptes nominatifs ou une gestion d’identité adaptée ;
- synchroniser le collecteur et les équipements sur des sources approuvées ;
- séparer le réseau de gestion du réseau utilisateur lorsque c’est possible ;
- limiter les hôtes autorisés à envoyer des messages vers les collecteurs ;
- protéger le transport par TLS lorsque les équipements le supportent ;
- restreindre la suppression et la modification des journaux ;
- centraliser les événements d’accès et de configuration ;
- surveiller la disparition soudaine des messages d’un équipement ;
- définir une rétention et une sauvegarde compatibles avec les obligations de l’organisation.

Le collecteur doit être traité comme une infrastructure critique. Si tous les routeurs envoient leurs journaux vers un seul serveur sans redondance, panne ou saturation du collecteur peut rendre les événements indisponibles au moment d’un incident. L’architecture doit prévoir une capacité suffisante, une supervision de l’ingestion et une procédure de restauration.

### 3.4. Risques liés à UDP Syslog

UDP Syslog est simple, mais il ne garantit pas la livraison. Une congestion peut entraîner la perte d’événements, et il n’intègre pas de chiffrement ni d’authentification de l’émetteur. Si un collecteur accepte des messages depuis n’importe quelle source, il peut recevoir des événements falsifiés ou être exposé à un volume excessif.

La mitigation comprend le filtrage de source et de destination, la limitation du réseau d’administration, la séparation des flux, la protection du collecteur et, lorsque possible, un transport sécurisé. Les événements critiques doivent être sauvegardés sur un système dont les contrôles d’accès et la rétention sont indépendants de ceux de l’équipement source.

Un mécanisme de transport fiable ne garantit pas à lui seul que l’événement soit conservé dans l’index : il faut encore contrôler les files, les erreurs de réception et la capacité de stockage. La fiabilité doit être évaluée de bout en bout.

### 3.5. Risques liés à une source NTP compromise

Une source NTP erronée ou manipulée peut provoquer une dérive d’heure qui compromet l’analyse chronologique. L’impact peut concerner la validation de certificats, les jetons qui ont une durée de validité, les systèmes de journalisation, les tâches planifiées ou les mécanismes de détection d’incident.

Ne configure pas automatiquement des serveurs externes non approuvés pour compenser la panne d’une source interne. Une stratégie de secours documentée doit indiquer les serveurs approuvés et la façon dont ils seront validés. La surveillance doit détecter les sources qui passent soudainement à un stratum inattendu, dont l’offset devient anormal ou qui cessent d’être sélectionnées.

La redondance fonctionne seulement si les sources ne dépendent pas toutes du même élément fragile. Deux serveurs internes qui se synchronisent sur le même serveur amont en panne ne constituent pas une indépendance complète. L’architecture des dépendances doit être connue et documentée.

### 3.6. NTP, authentification et NTS

Les implémentations peuvent proposer des mécanismes d’authentification NTP historiques ou des fonctions plus modernes ; les détails diffèrent selon les logiciels. Il faut vérifier quel mécanisme est réellement supporté et éviter de considérer une option de configuration comme une preuve de sécurité sans vérifier les associations établies et les journaux du système.

NTS (Network Time Security, RFC 8915) est conçu pour sécuriser les échanges NTP grâce à une phase d’établissement des clés qui s’appuie sur TLS, suivie d’extensions d’authentification pour NTP. Il ne faut pas assimiler NTS à « NTP chiffré sur TLS en permanence » : la négociation de sécurité et les échanges de temps utilisent des mécanismes distincts. Le support client/serveur doit être confirmé avant le choix d’architecture.

Pour les équipements réseau qui n’implémentent pas NTS, l’approche courante est de limiter les sources à des serveurs internes approuvés, de restreindre le trafic au niveau du réseau et de surveiller continuellement l’état temporel.

### 3.7. Gestion des volumes et conservation

Un seuil Syslog bas en gravité numérique signifie que seuls les événements les plus graves sont transmis ; un seuil allant jusqu’à informational produit beaucoup plus de messages. Les environnements peuvent avoir des profils distincts pour les routeurs de cœur, les commutateurs d’accès, les pare-feu et les équipements de laboratoire.

Le niveau de debug doit généralement être réservé aux interventions encadrées. Son volume peut être très important et peut affecter les performances de l’équipement ainsi que celles du collecteur. Une procédure doit préciser quand activer le debug, qui l’autorise, comment arrêter la collecte et comment archiver les éléments utiles.

La politique de rétention doit distinguer les événements opérationnels courants des journaux d’audit soumis à des exigences plus strictes. La durée nécessaire dépend du modèle d’exploitation, des obligations légales et de la capacité disponible. Il faut régulièrement tester la récupération des données sauvegardées et vérifier que les horodatages restent interprétables sur toute la période conservée.

### 3.8. Alertes de supervision recommandées

Un dispositif de supervision peut alerter sur :

- absence de synchronisation NTP ;
- hausse anormale de l’offset ou de l’incertitude estimée ;
- changement de source ou de stratum inattendu ;
- absence de messages Syslog pendant une période inhabituelle ;
- diminution de l’ingestion par rapport au volume normal ;
- erreurs de transport ou de parsing ;
- saturation de stockage ou file d’ingestion ;
- arrêt de service du collecteur ;
- changements non autorisés de configuration NTP ou Syslog.

L’absence de journal peut elle-même constituer un événement important. Un commutateur qui n’a envoyé aucun message depuis une durée inhabituelle est peut-être en panne, isolé du réseau de gestion, mal configuré ou compromis. La détection de silence doit tenir compte du profil normal de l’équipement : un équipement peu bavard ne doit pas générer de fausses alertes continues.

### 3.9. Sécurité de la configuration Cisco

Les commandes NTP et Syslog font partie de la configuration d’administration. Seuls les opérateurs autorisés devraient pouvoir modifier les serveurs de temps, les collecteurs, les niveaux de journalisation et les interfaces source. La gestion de configuration doit conserver l’historique des changements.

Les bonnes pratiques comprennent :

- limiter les lignes VTY et l’accès console selon la politique de l’organisation ;
- employer des mécanismes d’authentification d’administration robustes ;
- utiliser SSH plutôt que des accès en clair ;
- restreindre les connexions de gestion aux sous-réseaux approuvés ;
- sauvegarder régulièrement la configuration ;
- centraliser les journaux d’authentification et les modifications ;
- vérifier périodiquement que les sources NTP et Syslog sont toujours valides ;
- documenter les changements de fuseau horaire et d’adresse de collecteur.

La commande `show running-config` permet d’examiner une partie de la configuration, mais il faut aussi vérifier l’état opérationnel. Une ligne correcte dans la configuration ne prouve ni que le serveur est joignable ni que les messages sont réceptionnés.

### 3.10. Liste de contrôle avant mise en production

**NTP**

- Les sources de temps sont approuvées et documentées.
- Plusieurs sources sont utilisées lorsque c’est nécessaire et possible.
- L’état NTP confirme une synchronisation effective.
- Les valeurs de qualité restent dans les tolérances définies.
- Le fuseau et la présentation de l’heure sont cohérents.
- Les ACL n’autorisent que les échanges nécessaires.
- Le comportement en cas de perte des sources est documenté.

**Syslog**

- Le collecteur est opérationnel et écoute sur le transport attendu.
- Le niveau de gravité transmet les événements requis sans surcharge excessive.
- L’adresse source des messages est stable et connue.
- L’horodatage est cohérent et correctement interprété.
- Un événement de test apparaît dans le collecteur et dans les recherches.
- La capacité, les alertes, la rétention et les sauvegardes sont en place.
- Le transport est protégé selon les capacités des équipements.
- L’accès aux journaux et la suppression sont contrôlés.

> **Danger :** Une attaque ou une erreur de configuration qui fausse l’heure ou interrompt la journalisation peut dégrader simultanément la détection, la corrélation et la preuve d’un incident. Un équipement peut continuer à transférer les paquets alors que ses événements ne sont plus visibles au centre de supervision. Il faut donc surveiller activement l’état NTP et la présence des journaux, restreindre les sources et destinations, privilégier un transport protégé quand il est supporté, et protéger les journaux centralisés contre la modification et la suppression non autorisées.


## Points à retenir

- **NTP synchronise les horloges ; Syslog transporte les événements.** Leur intégration permet de corréler les incidents, mais une configuration présente ne prouve pas que l’heure est synchronisée ou que les journaux arrivent au collecteur.
- **Le stratum, l’offset, le délai et le jitter décrivent des aspects différents.** Le stratum ne suffit pas à évaluer la qualité d’une source. Les décalages doivent être analysés dans la durée, et les problèmes de fuseau doivent être distingués des problèmes de synchronisation.
- **Syslog est une chaîne de traitement de bout en bout.** Les seuils de gravité, l’adresse source, le transport, les ACL, le parsing, l’indexation, la rétention et la protection du collecteur doivent tous être vérifiés. UDP/514 est courant mais ne garantit ni la livraison ni la confidentialité ; TLS sur le port 6514 est défini par la RFC 5425 lorsque le support est disponible.

## Références techniques

- [RFC 5905 — Network Time Protocol Version 4 (NTPv4)](https://www.rfc-editor.org/rfc/rfc5905.html)
- [RFC 8915 — Network Time Security for the Network Time Protocol](https://www.rfc-editor.org/rfc/rfc8915.html)
- [RFC 5424 — The Syslog Protocol](https://www.rfc-editor.org/rfc/rfc5424.html)
- [RFC 5425 — Transport Layer Security (TLS) Transport Mapping for Syslog](https://www.rfc-editor.org/rfc/rfc5425.html)
- [RFC 5426 — Transmission of Syslog Messages over UDP](https://www.rfc-editor.org/rfc/rfc5426.html)
- [Documentation Cisco — Command Reference et Configuration Guides IOS/IOS XE](https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-software-releases-12-2-mainline/products-command-reference-list.html)
