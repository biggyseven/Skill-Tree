# NTP & Syslog - Expert

**Niveau :** Expert

La synchronisation temporelle et la journalisation centralisée sont deux services transversaux du système d'information. NTP (Network Time Protocol) permet à des systèmes distribués d'approcher une même référence temporelle, malgré la dérive des oscillateurs, la variabilité des délais réseau et les différences d'implémentation des horloges. Syslog normalise le transport et la représentation d'événements produits par des équipements et des applications. Pris séparément, ces services sont souvent considérés comme des fonctions d'exploitation. Pris ensemble, ils deviennent une infrastructure critique : sans temps cohérent, l'interprétation chronologique des journaux, la corrélation SIEM, l'analyse d'incident et l'audit sont fortement dégradés.

Les déploiements contemporains doivent concilier exactitude, résilience, traçabilité, sécurité et capacité opérationnelle. Il ne suffit pas de configurer une adresse de serveur NTP ou une destination Syslog. Il faut définir les sources de confiance, les domaines de temps, les limites de dérive tolérées, les chemins réseau, les politiques de filtrage, la rétention, les files d'attente, la gestion des certificats et les procédures de continuité. Un serveur NTP en stratum faible n'est pas automatiquement exact, pas plus qu'un collecteur Syslog joignable ne garantit que les événements y sont arrivés, correctement horodatés, conservés et indexés.

NTPv4 est décrit principalement dans la RFC 5905 et les RFC qui l'ont mise à jour. Le protocole estime l'écart entre une horloge locale et une référence à partir d'échanges horodatés, puis utilise des mécanismes de sélection, de filtrage et de discipline de l'horloge. La sécurité cryptographique de NTP a été complétée par des mécanismes tels que Network Time Security (NTS), défini par la RFC 8915. NTS sépare l'établissement des clés, effectué sur TLS, de l'authentification des paquets NTP. Cette approche est différente de la simple accessibilité UDP/123 et ne doit pas être confondue avec l'authentification symétrique historique disponible sur certains équipements réseau.

Syslog possède plusieurs générations et modes de transport. Le format historique souvent appelé BSD Syslog diffère du format structuré défini par la RFC 5424. Le transport UDP est simple mais ne garantit ni livraison ni ordre. Le transport TLS défini par la RFC 5425 protège le canal et utilise normalement le port TCP 6514. Le choix du transport doit prendre en compte les capacités réelles des émetteurs, les contraintes de réseau, le volume d'événements et les objectifs de preuve. Les équipements réseau peuvent proposer des sous-ensembles différents de ces fonctions : la validation de la version du système d'exploitation et de la plateforme est donc indispensable avant tout déploiement.

> **Analogie** : Considère le temps comme l'échelle commune d'un réseau ferroviaire national, et Syslog comme le registre officiel de chaque gare. Si chaque gare utilise une horloge différente, deux rapports d'incident peuvent sembler inversés : une panne paraît avoir précédé la coupure qui l'a provoquée, ou un événement observé sur un pare-feu semble survenir après la connexion qu'il a bloquée. NTP fournit un mécanisme de comparaison des horloges avec des références, de rejet des sources incohérentes et de correction graduelle des écarts. Syslog transporte les rapports des gares vers un centre d'archives. Mais une ligne de communication saturée peut perdre les rapports, un émetteur mal configuré peut inscrire un horaire local dans un format mal interprété, et un adversaire peut tenter d'injecter de faux événements. Une architecture professionnelle doit donc traiter l'heure, l'identité de la source, le transport, l'intégrité, la capacité de collecte et la conservation comme des maillons d'une même chaîne de confiance.


## 1. La théorie et les algorithmes

### 1.1. Temps civil, temps système et précision réellement obtenue

Il faut distinguer plusieurs notions qui sont souvent confondues :

- **UTC** est l'échelle de temps de référence utilisée pour exprimer l'heure civile mondiale.
- **L'heure système** est la valeur maintenue par le noyau et exposée aux applications. Elle peut être corrigée par un service de temps.
- **L'horloge monotone** mesure une durée qui ne doit pas reculer lors d'une correction de l'heure civile. Les applications de mesure de délais doivent généralement l'utiliser au lieu de soustraire deux horodatages civils.
- **La fréquence de l'oscillateur** détermine la vitesse à laquelle l'horloge locale avance. Elle dérive avec la température, l'âge du composant, l'alimentation et les caractéristiques du matériel.
- **L'exactitude** indique la proximité de la valeur obtenue par rapport à la référence ; la **précision** décrit la dispersion ou la finesse des mesures. Une horloge affichant des millisecondes n'est pas nécessairement exacte à la milliseconde.

La synchronisation d'horloge ne supprime pas les limites physiques. Le délai de propagation, les files d'attente, l'asymétrie aller-retour, les interruptions, la virtualisation et la charge CPU affectent la mesure. Un réseau local bien maîtrisé peut obtenir une synchronisation bien meilleure qu'un chemin Internet congestionné, mais les chiffres exacts dépendent du matériel, du logiciel et de la topologie.

Il faut également différencier le réglage de l'heure et le réglage de la fréquence. Une correction brutale, appelée souvent *step*, change directement l'heure système. Une correction progressive, souvent désignée par *slew*, ajuste le rythme de l'horloge afin de réduire l'écart sans saut apparent. Un saut peut être pertinent au démarrage si l'écart est très grand ; il est dangereux pour les applications qui supposent un temps monotone, les bases de données, les systèmes de fichiers, les transactions et les mécanismes d'authentification temporelle.

### 1.2. Architecture NTP et rôles des serveurs

NTP organise les relations de synchronisation en une hiérarchie logique. Une source de stratum 1 est directement raccordée à une référence de temps, par exemple un récepteur GNSS, une horloge atomique ou une autre référence dédiée. Un serveur synchronisé sur une source de stratum 1 peut fonctionner au stratum 2 ; ses clients peuvent devenir stratum 3, et ainsi de suite. Le stratum exprime une distance logique par rapport à une référence, pas une mesure complète de la qualité ni une certification d'exactitude.

Un serveur au stratum 2 dont la référence est stable et bien surveillée peut fournir de meilleurs résultats qu'un serveur au stratum 1 mal installé ou perturbé. Le choix des sources ne doit donc pas reposer uniquement sur le plus petit numéro de stratum. Les informations d'incertitude, de délai, de dispersion, de stabilité, de cohérence des sources et la politique locale doivent être considérées.

Les architectures courantes comprennent :

1. **Client simple** : un hôte interroge une ou plusieurs sources amont et ne sert pas d'autres clients.
2. **Serveur secondaire interne** : il se synchronise sur plusieurs sources amont et distribue le temps à un domaine local.
3. **Sources de référence indépendantes** : plusieurs serveurs internes récupèrent le temps par des chemins ou technologies différents, puis alimentent les équipements réseau et les serveurs.
4. **Hiérarchie isolée** : un domaine restreint utilise ses propres références, sans dépendance permanente à l'Internet public.
5. **Horloge de référence locale** : un équipement peut être configuré pour annoncer une heure locale de secours, mais une horloge locale déclarée autoritaire sans véritable référence n'est pas une source UTC fiable. Cette fonction doit rester un choix explicite de continuité ou de laboratoire, jamais une solution de secours masquant la perte de synchronisation.

```text
                   Références de temps indépendantes
                 +----------------+  +----------------+
                 | Source A       |  | Source B       |
                 | GNSS / amont   |  | amont distinct |
                 +-------+--------+  +--------+-------+
                         \                  /
                          \                /
                   +-------v--------------v-------+
                   | NTP interne A / B             |
                   | sélection, surveillance      |
                   +---------------+---------------+
                                   |
                +------------------+------------------+
                |                  |                  |
           +----v----+        +----v----+        +----v----+
           | Routeur |        | Serveur |        | Pare-feu|
           +---------+        +---------+        +---------+
```

La redondance doit être réelle. Deux noms DNS pointant vers le même serveur ou deux serveurs dépendant du même lien, de la même alimentation et de la même source GNSS n'offrent pas deux domaines de panne indépendants. Une architecture bien conçue documente la dépendance de chaque source et définit ce qui se produit lorsqu'une, plusieurs ou toutes les références disparaissent.

### 1.3. Mesure des horodatages : le cœur du calcul NTP

Dans le mode client-serveur classique, un échange NTP utilise quatre horodatages :

- **T1** : instant où le client envoie la requête ;
- **T2** : instant où le serveur reçoit cette requête ;
- **T3** : instant où le serveur envoie la réponse ;
- **T4** : instant où le client reçoit la réponse.

En supposant que les délais aller et retour soient suffisamment symétriques, le décalage estimé entre l'horloge serveur et l'horloge client est calculé par :

\[
\theta = \frac{(T2-T1)+(T3-T4)}{2}
\]

Le délai réseau aller-retour estimé est :

\[
\delta = (T4-T1)-(T3-T2)
\]

Ces formules estiment le décalage et le délai à partir des horodatages échangés. Elles ne démontrent pas qu'un chemin est symétrique. Une asymétrie de propagation ou de file d'attente peut être interprétée comme un décalage d'horloge. C'est une limite importante lorsqu'on traverse des liaisons WAN, des tunnels, des files d'attente fortement variables ou des chemins dont les directions empruntent des itinéraires différents.

La qualité de l'horodatage compte également. Si T1 et T4 sont affectés par un ordonnancement logiciel imprécis, ou si le timestamp de réception est pris tardivement après une longue interruption, le résultat est contaminé. Les cartes réseau et systèmes capables d'horodatage matériel réduisent certaines sources d'incertitude, mais ils ne sont pas systématiquement utilisés par une configuration NTP ordinaire.

NTP maintient aussi des mesures de délai, de dispersion et de jitter. La dispersion reflète l'incertitude accumulée ou estimée autour de la source ; le jitter représente, dans le contexte NTP, la variabilité statistique des écarts de mesure ou des offsets filtrés, et ne doit pas être assimilé sans précaution à la gigue d'un flux RTP. L'interprétation des sorties dépend de l'implémentation.

### 1.4. Format temporel et limites de représentation

Le format NTP traditionnel utilise une représentation de timestamp en virgule fixe sur 64 bits, avec une partie entière de 32 bits exprimant les secondes et une partie fractionnaire de 32 bits. L'époque NTP commence le 1er janvier 1900, ce qui ne correspond pas à l'époque Unix du 1er janvier 1970.

Le champ de secondes sur 32 bits implique une question de cycle d'ère : la représentation classique revient à zéro après une période de l'ordre de 136 ans. Les implémentations doivent déterminer l'ère pertinente à partir du contexte et d'autres informations. Cette caractéristique importe pour les systèmes de longue durée, les logiciels embarqués ou les équipements restés sans mise à jour. Il ne s'agit pas du même problème que le rollover Unix de 2038, car les époques et les largeurs de représentation sont différentes.

NTP inclut également des indicateurs et champs tels que Leap Indicator, Version Number, Mode, Stratum, Poll, Precision, Root Delay, Root Dispersion, Reference ID et les timestamps d'origine, de réception, de transmission et de référence. Ils sont utiles lors de l'analyse des paquets, mais les valeurs doivent être interprétées dans le contexte du protocole et de l'implémentation. Une valeur affichée en stratum 16, par exemple, indique classiquement une source non synchronisée ; elle n'est pas une référence à utiliser pour distribuer une heure fiable.

### 1.5. Filtrage, sélection et discipline de l'horloge

Les paquets NTP peuvent être retardés, perdus ou perturbés. Une implémentation ne doit donc pas adopter aveuglément le dernier timestamp reçu. NTP utilise des algorithmes de filtrage et de sélection destinés à limiter l'influence des mesures aberrantes et à rechercher un ensemble de sources cohérentes.

Le processus conceptuel peut être décomposé en plusieurs étapes :

1. **Collecte** : l'hôte maintient des associations avec plusieurs sources et collecte leurs mesures.
2. **Filtrage par source** : les observations récentes sont conservées et évaluées afin de limiter l'influence d'échantillons de mauvaise qualité.
3. **Évaluation des distances** : les retards et incertitudes sont combinés pour estimer la plage probable dans laquelle se situe l'heure réelle.
4. **Sélection** : les sources incompatibles avec un groupe cohérent peuvent être écartées comme fausses ou aberrantes (*falsetickers* dans la terminologie classique NTP).
5. **Clustering et choix** : parmi les sources acceptables, l'algorithme recherche un sous-ensemble cohérent et une référence appropriée.
6. **Discipline** : le système ajuste la fréquence et, si nécessaire, l'heure, en respectant les limites et paramètres de l'implémentation.

Une seule source ne permet pas toujours de distinguer une véritable dérive d'horloge d'une source qui fournit systématiquement une heure erronée. Plusieurs sources indépendantes permettent une comparaison. Toutefois, trois noms de serveur ne signifient pas nécessairement trois sources indépendantes. Les organisations doivent analyser les dépendances de synchronisation, pas seulement compter les entrées de configuration.

Les mécanismes de boucle à verrouillage de phase et de fréquence (PLL/FLL), le modèle de dérive et les paramètres de discipline varient selon les implémentations. Les systèmes `ntpd`, `chronyd` et les services de temps des systèmes d'exploitation ne présentent pas exactement les mêmes sorties ni les mêmes options. Les commandes et seuils issus d'une implémentation ne doivent pas être transposés directement dans une autre.

### 1.6. Stratum, distance racine et choix de la source

Le stratum indique la distance logique à la référence de temps dans la hiérarchie NTP. Stratum 1 correspond traditionnellement à une source de référence directement connectée ; les stratum suivants représentent des niveaux de distribution. Un client qui n'est pas synchronisé est généralement signalé par un stratum 16 dans les implémentations NTP classiques.

La distance racine est une estimation de l'incertitude totale par rapport à la référence, intégrant notamment des composantes du délai racine et de la dispersion racine. Une source avec un meilleur stratum peut présenter une incertitude supérieure à une source de stratum plus élevé. Le déploiement doit donc examiner plusieurs informations : stratum, offset, root delay, root dispersion, jitter, état de sélection et stabilité sur la durée.

La distance racine n'est pas un certificat. Si une source est compromise et annonce des données trompeuses, des mesures plausibles peuvent être difficiles à distinguer d'une situation normale sans authentification et sans observations indépendantes. Les indicateurs de qualité permettent de détecter des problèmes accidentels, mais la confiance cryptographique exige des mécanismes adaptés.

### 1.7. NTP, SNTP, NTS et PTP : ne pas confondre leurs objectifs

**NTPv4** fournit une architecture complète de synchronisation, avec des algorithmes de sélection, de filtrage et de discipline. **SNTP** est un sous-ensemble simplifié qui ne fournit pas toute la sophistication de sélection et de discipline de NTP complet. Le fait qu'un appareil affiche « SNTP » n'implique pas qu'il soit inutilisable, mais ses garanties et son rôle doivent être considérés à partir de sa documentation.

**NTS** (Network Time Security) protège le mode client-serveur NTP par une négociation de clés TLS et des champs d'extension authentifiés. La RFC 8915 définit deux sous-protocoles : NTS-KE pour l'établissement initial et les extensions NTP qui assurent l'authentification et la protection cryptographique des échanges de synchronisation. Le port TCP par défaut de NTS-KE est 4460 ; les échanges NTP restent basés sur le transport NTP et son port usuel UDP/123. NTS n'est pas simplement « NTP sur TLS » pour chaque paquet.

**PTP** (Precision Time Protocol, IEEE 1588) vise notamment des précisions très élevées sur des réseaux compatibles, souvent avec horodatage matériel et mécanismes adaptés à la topologie. NTP reste très courant pour l'horodatage opérationnel, les journaux, les systèmes informatiques et les équipements réseau. PTP et NTP peuvent coexister, mais il faut documenter quelle discipline d'horloge fait autorité sur chaque équipement afin d'éviter que deux services ne tentent de corriger l'horloge de façon concurrente.

### 1.8. NTS : déroulement logique et conséquences opérationnelles

NTS utilise d'abord NTS Key Establishment, fondé sur TLS, pour authentifier le serveur et établir le matériel cryptographique. Le client reçoit notamment des cookies opaques qu'il utilise ensuite dans les requêtes NTP. Les paquets NTP comportent des champs d'extension protégés par une clé d'authentification et un algorithme AEAD négocié selon le protocole. Le serveur peut traiter les cookies sans conserver un état complet par client ; la plupart des états nécessaires aux requêtes sont portés par le client.

Le processus exige un certificat serveur valide, une chaîne de confiance appropriée, une résolution DNS correcte lorsqu'un nom est utilisé, une horloge initiale suffisamment plausible pour valider les certificats et un accès aux ports requis. Ce dernier point crée une dépendance de démarrage : sur une machine dont l'horloge est très fausse, la validation du certificat NTS-KE peut échouer parce que le certificat paraît expiré ou pas encore valide. Les systèmes critiques doivent prévoir une stratégie de bootstrap et de récupération documentée, sans désactiver durablement la validation TLS.

NTS ne résout pas tous les risques liés au temps. Il authentifie la source et protège les échanges contre certaines modifications et attaques de rejeu, mais ne garantit pas que l'opérateur de la source fournit une heure correcte, que le GNSS en amont est exact ou que l'hôte local n'est pas compromis. Le choix d'une source de confiance, la diversité des références, la surveillance des écarts et le durcissement de la machine restent nécessaires.

L'adoption de NTS dépend des capacités logicielles et matérielles. Les déploiements de systèmes Linux peuvent s'appuyer sur des implémentations qui prennent en charge NTS, tandis que de nombreux commutateurs ou routeurs peuvent ne proposer que les mécanismes NTP qu'ils documentent, parfois avec authentification symétrique historique. Il ne faut jamais supposer que la commande d'authentification d'un équipement réseau fournit automatiquement les mêmes garanties que NTS.

### 1.9. Menaces NTP et stratégies de défense

Les menaces comprennent la falsification de réponses, l'injection de fausses références, les attaques de rejeu, la manipulation de la route réseau, le déni de service et l'exploitation de services NTP exposés inutilement. Une heure fausse peut entraîner des effets en chaîne : certificats TLS refusés, sessions Kerberos invalides, jetons d'authentification expirés de façon incohérente, journaux mal ordonnés, erreurs de validation de signatures et confusion dans une enquête de sécurité.

Les mesures de défense doivent être adaptées au rôle de chaque serveur :

- limiter les clients autorisés à utiliser les serveurs NTP internes ;
- limiter les serveurs internes aux sources amont prévues ;
- filtrer UDP/123 aux frontières et éviter de transformer des équipements internes en serveurs publics ouverts ;
- employer NTS lorsque le parc et les objectifs le permettent ;
- conserver plusieurs sources réellement indépendantes ;
- surveiller les changements de source, les offsets anormaux, les stratum non synchronisés et les erreurs d'authentification ;
- protéger l'administration, les secrets et les clés ;
- mettre à jour les implémentations et désactiver les fonctions de contrôle inutiles.

Les anciennes configurations NTP ont parfois permis des fonctions de contrôle et d'information trop généreuses. Les options exactes diffèrent selon les implémentations, mais le principe reste de désactiver les services d'administration ou de diagnostic exposés aux réseaux non fiables et de n'autoriser que les requêtes nécessaires. Les règles de pare-feu doivent être validées pour le trafic client, les réponses établies, les opérations de maintenance et les mécanismes de sécurité utilisés.

### 1.10. Syslog : format, facility et sévérité

Syslog distingue le contenu du message et le transport qui l'achemine. La RFC 5424 définit le format structuré d'un message. Un message Syslog moderne comporte notamment une priorité (PRI), une version, un timestamp, un hostname, un nom d'application, un identifiant de processus, un identifiant de message, des données structurées optionnelles et un contenu de message.

Le champ PRI combine la *facility* et la sévérité :

\[
PRI = 8 \times Facility + Severity
\]

La facility identifie la catégorie fonctionnelle émettrice selon le registre applicable, tandis que la sévérité est un entier de 0 à 7.

| Valeur | Sévérité | Interprétation habituelle |
|---:|---|---|
| 0 | Emergency | Système inutilisable |
| 1 | Alert | Action immédiate requise |
| 2 | Critical | Condition critique |
| 3 | Error | Erreur |
| 4 | Warning | Avertissement |
| 5 | Notice | Événement normal mais significatif |
| 6 | Informational | Information opérationnelle |
| 7 | Debug | Diagnostic détaillé |

Dans de nombreuses interfaces Cisco, les niveaux de journalisation sont configurés avec des noms tels que `warnings`, `informational` ou `debugging`. Un seuil de gravité filtre le message selon sa sévérité : le seuil *warnings* sélectionne typiquement les niveaux 0 à 4, pas uniquement les messages portant exactement le niveau 4. Il faut vérifier l'interprétation de chaque système et documenter le seuil réellement voulu.

Le format historique BSD Syslog (souvent associé à la RFC 3164) n'est pas identique à la structure de la RFC 5424. Les collecteurs reçoivent parfois des messages en formats différents. Le parsing doit reconnaître le format ou utiliser des profils d'équipement ; un parseur trop strict peut rejeter des messages valides ou mal extraire leur timestamp.

### 1.11. Transports Syslog et sémantique de livraison

Les transports ne fournissent pas les mêmes garanties :

- **UDP/514** est très répandu et léger, mais ne garantit ni livraison, ni ordre, ni retransmission. La perte de paquets est possible sous charge ou lors d'une panne de collecteur.
- **TCP** fournit un flux fiable au niveau transport, mais un émetteur doit disposer d'un mécanisme d'encadrement de messages adapté. Une connexion TCP ne garantit pas que le collecteur a durablement écrit chaque événement dans son stockage.
- **TLS sur TCP/6514** protège le canal et permet l'authentification par certificats selon la RFC 5425. La gestion de la chaîne de confiance, de l'identité du serveur, de la rotation des certificats et de la révocation doit être opérationnelle.
- **Relais Syslog** permettent d'isoler les équipements du collecteur final, d'agréger les connexions, de mettre en tampon et de segmenter les flux.

La RFC 6587 décrit des méthodes d'encadrement pour Syslog sur TCP, notamment le comptage de longueur et le framing historique par délimitation. Le choix doit être compatible entre l'émetteur, le relais et le collecteur. Les plateformes d'équipement ne prennent pas toutes en charge le même sous-ensemble. Une option `transport tcp` sur un routeur ne signifie pas nécessairement que celui-ci prend en charge Syslog sur TLS, le format RFC 5424 ou toutes les méthodes de framing.

La fiabilité doit être définie de bout en bout. Un message accepté par le socket TCP peut encore être perdu si le relais tombe avant l'écriture persistante. Une file d'attente peut être saturée ; une politique de rotation ou de rétention peut supprimer des fichiers ; un collecteur peut recevoir le message mais échouer à l'indexer. Les exigences de preuve doivent préciser le niveau de livraison attendu : best effort, file locale persistante, acquittement d'application, stockage immuable ou chaîne de traitement surveillée.

### 1.12. Architecture Syslog à grande échelle

Un petit réseau peut envoyer ses messages directement à un collecteur central. Dans un environnement multi-sites, il est souvent préférable d'utiliser une architecture en couches : équipement → relais régional → ingestion centrale → stockage et indexation → SIEM ou plateforme d'analyse.

Le relais régional peut limiter l'exposition du collecteur, normaliser les sources, appliquer une stratégie de mise en file, compresser ou transmettre les événements selon les capacités de l'écosystème. Il doit cependant être considéré comme un composant critique. Il faut surveiller son occupation disque, la profondeur des files, les messages rejetés, la latence d'ingestion et la disponibilité de ses destinations amont.

```text
       Site A                         Centre de données
  +---------------+                  +---------------------+
  | Routeurs      | -- Syslog ------>| Relais / ingestion  |
  | Pare-feux     |                  | validation, parsing |
  | Serveurs      |                  +----------+----------+
  +---------------+                             |
                                                v
                                      +---------------------+
                                      | Stockage durable     |
                                      | indexation / SIEM    |
                                      +---------------------+
                                                |
                                                v
                                      +---------------------+
                                      | Alertes, enquêtes,   |
                                      | rapports d'audit     |
                                      +---------------------+
```

La séparation des rôles améliore l'évolutivité et le contrôle d'accès, mais ajoute des points de panne. La conception doit prévoir les files persistantes, les limites de taille, la reprise après interruption, la synchronisation de configuration et l'absence de boucle de relais. Les chemins Syslog doivent être documentés comme des flux réseau explicites avec ports, protocoles, interfaces source et politiques de filtrage.

### 1.13. Horodatage : temps de l'événement et temps de réception

Le timestamp contenu dans un message indique généralement le temps attribué par l'émetteur. Le collecteur connaît également le temps de réception. Ces deux valeurs doivent être conservées lorsqu'on réalise une corrélation avancée. Elles permettent de distinguer un événement survenu tardivement d'un événement transmis ou ingéré avec retard.

Si l'horloge du routeur est en retard de cinq minutes, un événement peut apparaître chronologiquement avant des événements qui l'ont réellement précédé. Si le collecteur utilise le fuseau local tandis que les équipements émettent en UTC, un parsing incorrect peut introduire un décalage supplémentaire. Les dates sans fuseau explicite ou issues du format historique sont particulièrement sensibles à l'interprétation du collecteur.

Une architecture robuste :

- synchronise les émetteurs avant de tirer des conclusions temporelles ;
- enregistre le timestamp original et le timestamp d'ingestion ;
- normalise les événements en UTC pour l'analyse, tout en conservant les métadonnées d'origine ;
- surveille les dérives de temps des équipements qui génèrent des événements de sécurité ;
- documente les comportements durant une perte de synchronisation ;
- n'interprète pas un timestamp comme une preuve indépendante de l'heure réelle sans considérer la confiance accordée à la source.

NTP et Syslog sont donc fortement couplés d'un point de vue opérationnel. La perte NTP peut ne pas affecter immédiatement le transfert des messages Syslog, mais elle détériore l'interprétation des événements. À l'inverse, les journaux Syslog sont une source importante pour diagnostiquer les changements de sources NTP, les redémarrages et les pertes de connectivité.

### 1.14. Files, débit, backpressure et pertes de journaux

La capacité de Syslog doit être dimensionnée selon le nombre d'équipements, le nombre moyen d'événements par seconde, les rafales pendant un incident, la taille moyenne des messages, le facteur de compression et la durée de rétention. Il faut prévoir des marges pour les situations où plusieurs équipements produisent simultanément des événements, par exemple lors d'une panne WAN, d'une attaque ou d'un changement de configuration généralisé.

Une simple moyenne quotidienne peut masquer les pointes. La capacité doit considérer le débit de pointe et la durée pendant laquelle le collecteur peut rester indisponible. Si 8 000 événements/s arrivent avec une taille moyenne de 600 octets, le flux brut représente environ 4,8 Mo/s avant les en-têtes et les surcoûts de stockage. Il faut ensuite multiplier par la durée de rétention et tenir compte de l'indexation, des répliques, des métadonnées et des marges de croissance.

Les files doivent être surveillées. Une file croissante indique que l'ingestion est plus lente que la production ; si la situation persiste, les tampons finiront par saturer. Selon le logiciel, la saturation entraîne une perte, un blocage de l'émetteur, une suppression selon priorité ou une interruption de réception. Chaque choix a des conséquences : bloquer les équipements réseau peut affecter d'autres traitements, tandis que perdre des logs en période d'incident peut réduire les preuves disponibles.

Les stratégies utiles comprennent les files persistantes sur les relais, des quotas de disque, le filtrage des événements trop verbeux, des seuils d'alerte sur les pertes et une procédure de reprise qui évite les boucles d'ingestion. Le filtrage doit être contrôlé : supprimer les messages de niveau debug en régime normal peut être raisonnable, mais il faut s'assurer que des événements de sécurité ne sont pas classés à tort dans une catégorie exclue.

### 1.15. Structure, identités et normalisation

Les événements Syslog doivent conserver l'identité de l'émetteur autant que possible. Le hostname déclaré dans le message peut être absent, dupliqué ou falsifié ; l'adresse IP source du transport peut correspondre à une interface de sortie ou à un relais plutôt qu'à l'équipement logique. Il est donc utile de conserver des champs séparés : adresse source observée, hostname original, identité TLS, interface source configurée et identifiant d'actif issu de l'inventaire.

La normalisation doit également conserver le message brut. Les parser rules peuvent être mises à jour, et les besoins d'investigation peuvent changer. Stocker uniquement une version normalisée risque de faire perdre des détails nécessaires à l'analyse. La bonne architecture conserve le message original, les champs extraits, les métadonnées de réception et la version du parseur utilisée.

Dans RFC 5424, le champ Structured Data permet de transporter des paramètres structurés selon des identifiants définis. Il ne faut pas supposer que tous les équipements l'emploient correctement. De nombreux équipements réseau utilisent encore des messages historiques ou propriétaires ; la normalisation doit donc accepter des formats hétérogènes tout en signalant les événements qui ne peuvent pas être interprétés fiablement.

### 1.16. Corrélation NTP/Syslog et investigation d'incident

Considère une perte de connectivité à 14:03:20 UTC. Le pare-feu signale un refus à 14:03:18, le routeur signale la perte du voisin à 14:03:22 et le serveur applicatif signale un timeout à 14:03:16. Cette séquence peut correspondre à un déclenchement unique, mais seulement si les horloges et les temps d'ingestion sont compris. Si l'un des équipements a un offset de +40 secondes, l'ordre apparent sera trompeur.

Une investigation de qualité doit suivre une chronologie en plusieurs colonnes : timestamp émis, timestamp reçu, offset connu de l'émetteur au moment de l'événement si disponible, source du message, identifiant d'actif, type d'événement, confiance dans le temps et hypothèse de causalité. La corrélation ne doit pas établir une causalité uniquement parce que deux événements sont proches dans le temps.

La synchronisation garantit une base de comparaison meilleure, mais n'élimine pas les autres sources d'incertitude : files d'attente, retransmissions, capture tardive, journaux mis en tampon, traitement asynchrone et différences sémantiques entre événements. Les procédures d'investigation doivent inclure un contrôle de la santé NTP et de la dérive des équipements touchés.

> **Piège :** Ne conclus pas que le système est bien synchronisé uniquement parce que `show clock` affiche une heure plausible. Cette commande indique une valeur d'horloge, pas nécessairement la source active, l'incertitude, la stabilité ou l'authenticité de la référence. Vérifie l'état NTP, les associations, le stratum, la source sélectionnée, les offsets et les journaux. De la même façon, la réception de messages Syslog ne prouve pas leur exhaustivité : il faut surveiller les pertes, la file d'attente, les erreurs de parsing et le stockage final.

```text
          PLAN TEMPOREL                    PIPELINE SYSLOG
  +------------------------+       +-----------------------------+
  | Source NTP A / B       |       | Émetteurs réseau et serveurs|
  | diversité / qualité    |       +--------------+--------------+
  +-----------+------------+                      |
              |                                   v
              v                         +-------------------------+
  +------------------------+             | Transport UDP/TCP/TLS   |
  | Horloge système locale |             +------------+------------+
  | offset / dérive / état |                          |
  +-----------+------------+                          v
              |                            +-------------------------+
              v                            | Collecte / tampon      |
  +------------------------+             +------------+------------+
  | Horodatage des events  |                          |
  +-----------+------------+                          v
              +-------------------------->+-------------------------+
                                           | Normalisation / stockage|
                                           | timestamp reçu + émis   |
                                           +-------------------------+
```


## 2. Configuration et Pratique

Les configurations ci-dessous illustrent les principes sur Cisco IOS/IOS XE et sur un collecteur Linux. Elles doivent être adaptées à la version exacte du logiciel, aux licences, à la plate-forme et aux fonctions réellement prises en charge. La présence d'une commande dans une documentation IOS XE récente ne garantit pas sa disponibilité sur tous les commutateurs ou routeurs.

### 2.1. Architecture de laboratoire expert

Le laboratoire utilise deux serveurs de temps internes et un collecteur Syslog. Les équipements réseau synchronisent leur horloge sur des sources internes plutôt que sur plusieurs serveurs Internet configurés directement dans chaque équipement. Les deux sources doivent si possible utiliser des chemins et références indépendants.

| Élément | Adresse illustrative | Fonction |
|---|---|---|
| NTP-A | 192.0.2.10 | Source interne principale |
| NTP-B | 192.0.2.11 | Source interne secondaire |
| SYSLOG-1 | 192.0.2.20 | Collecteur central |
| R1 Loopback0 | 192.0.2.101/32 | Identité stable du routeur |
| R2 Loopback0 | 192.0.2.102/32 | Identité stable du routeur |

Le bloc `192.0.2.0/24` est réservé à la documentation et aux exemples ; il ne doit pas être utilisé tel quel pour des destinations de production sur Internet. Remplace-le par l'adressage réel de l'entreprise.

```text
                     Sources amont fiables
                         +----------+
                         | Référence|
                         +-----+----+
                               |
                   +-----------+-----------+
                   |                       |
             +-----v-----+           +-----v-----+
             | NTP-A     |           | NTP-B     |
             | interne   |           | interne   |
             +-----+-----+           +-----+-----+
                   \                       /
                    \                     /
                 +---v-------------------v---+
                 | Routeurs / pare-feux /    |
                 | serveurs applicatifs      |
                 +-------------+-------------+
                               |
                         Syslog TCP/TLS
                               |
                       +-------v-------+
                       | SYSLOG-1      |
                       | collecte      |
                       +---------------+
```

### 2.2. NTP sur Cisco IOS/IOS XE

Une configuration de base côté client peut ressembler à ceci :

```cisco
! Identité stable de gestion (exemple à adapter)
interface Loopback0
 description IDENTITE_MANAGEMENT
 ip address 192.0.2.101 255.255.255.255
!
! Référence NTP principale et secondaire
ntp server 192.0.2.10 prefer
ntp server 192.0.2.11
!
! Utiliser une interface source stable si le logiciel le permet
ntp source Loopback0
!
! Fuseau local du Cameroun : UTC+1, sans changement saisonnier
clock timezone WAT 1 0
!
! Horodatage détaillé pour la journalisation
service timestamps log datetime msec localtime show-timezone
```

Le mot-clé `prefer` exprime une préférence, pas une garantie absolue qu'une source défaillante ou incohérente restera utilisée. Le protocole et l'implémentation conservent leurs propres règles de sélection. La commande `ntp source` choisit l'adresse source utilisée pour les échanges lorsque la plateforme prend en charge cette syntaxe ; elle ne crée pas la route vers les serveurs et ne remplace pas les ACL.

Le fuseau horaire affecte l'affichage local, mais NTP synchronise une référence temporelle et ne « synchronise » pas le nom de fuseau. Pour l'analyse centralisée, privilégie des timestamps avec indication du fuseau ou une normalisation du collecteur en UTC. Si les journaux indiquent l'heure locale, configure la plateforme et le parseur de manière cohérente.

Sur les routeurs, les commandes de vérification courantes sont :

```cisco
show clock detail
show ntp status
show ntp associations
show ntp associations detail
show running-config | include ntp|clock timezone|service timestamps
```

Les commandes exactes peuvent différer par version. `show clock detail` permet de lire l'horloge et souvent la source ou les informations d'horloge de référence. `show ntp status` indique l'état de synchronisation selon la plateforme ; `show ntp associations detail` fournit davantage de détails sur les sources, offsets, délais et dispersion. Il faut étudier la source sélectionnée et la stabilité, pas seulement la présence d'une ligne `ntp server` dans la configuration.

### 2.3. Authentification NTP sur les équipements qui la prennent en charge

Certains équipements Cisco prennent en charge l'authentification symétrique NTP par clé partagée. La syntaxe exacte et les algorithmes autorisés varient selon la version. Un exemple de forme classique est :

```cisco
ntp authentication-key 10 md5 CLE_DE_DEMONSTRATION
ntp trusted-key 10
ntp authenticate
ntp server 192.0.2.10 key 10 prefer
```

Cet exemple illustre le mécanisme historique de clé partagée ; il ne doit pas être présenté comme équivalent à NTS. Utilise une clé longue et unique, protège sa gestion, limite les équipements autorisés et vérifie la prise en charge effective de l'algorithme sur tous les pairs. Le secret de démonstration ne doit pas être réutilisé en production.

NTS, spécifié par la RFC 8915, utilise TLS pour l'établissement des clés et protège les paquets NTP avec des champs d'extension authentifiés. De nombreux équipements réseau n'implémentent pas NTS ; il faut donc vérifier la documentation de la plateforme au lieu d'inventer une commande `ntp nts` ou de supposer que `ntp authenticate` active NTS. Lorsqu'un routeur ne prend pas en charge NTS, la sécurité doit être renforcée par l'architecture, le filtrage, la protection des sources, les limites d'accès et la surveillance de cohérence.

### 2.4. Contrôle d'accès au service NTP

Les serveurs NTP doivent répondre uniquement aux clients et aux types de requêtes nécessaires. Les possibilités exactes d'ACL NTP dépendent de la plateforme et du système serveur. Sur un réseau Cisco, une ACL IP, une fonction de contrôle NTP ou une politique de pare-feu peut limiter la source des requêtes. Il faut maintenir séparés le besoin de synchronisation des clients internes et les besoins d'administration du serveur.

Une politique réseau typique autorise :

- les clients approuvés vers les serveurs internes sur UDP/123 ;
- les serveurs internes vers les sources amont déclarées sur UDP/123 ;
- le trafic de réponse correspondant, conformément au modèle stateful/stateless du pare-feu ;
- le port TCP/4460 vers un serveur NTS-KE lorsqu'une implémentation NTS est utilisée et que le chemin l'exige.

Elle interdit les requêtes NTP inutiles en provenance d'Internet vers les équipements de réseau qui ne doivent pas fournir de service public. Il faut également empêcher un client de configurer une source de temps non approuvée par simple accès administratif excessif. Le filtrage ne dispense pas du contrôle cryptographique lorsque celui-ci est requis.

### 2.5. Configuration Syslog Cisco

Une configuration de journalisation centralisée de base peut être structurée ainsi :

```cisco
! Horodatage des événements
service timestamps log datetime msec localtime show-timezone
!
! Destination centrale (transport par défaut dépend de la plateforme)
logging host 192.0.2.20
!
! Exemple : ne transmettre que les messages de niveau warning et plus graves
logging trap warnings
!
! Tampon local pour diagnostic en cas de perte du collecteur
logging buffered 16384 informational
!
! Adresser les messages avec une identité d'interface stable
logging source-interface Loopback0
!
! Exemple de facility, si prise en charge par l'IOS utilisé
logging facility local6
```

La commande `logging host` transmet les messages à la destination spécifiée. Le transport par défaut est souvent UDP dans les configurations traditionnelles ; les versions modernes peuvent proposer des options de transport additionnelles. Vérifie l'aide contextuelle (`?`) de l'IOS/IOS XE, les commandes `show logging` et le guide de configuration de la version cible. Ne suppose pas qu'une plateforme prend en charge TLS simplement parce qu'elle prend en charge TCP.

`logging trap warnings` configure généralement un seuil : les événements de niveau 0 à 4 sont envoyés au serveur. Si le besoin est d'inclure les événements informatifs, il faut régler le seuil en conséquence et surveiller le volume. `logging buffered` concerne le tampon local du routeur, pas le stockage final du collecteur. La capacité et le comportement exacts du tampon dépendent de l'implémentation.

Après configuration, exécute :

```cisco
show logging
show clock detail
show running-config | include logging|service timestamps
```

Vérifie l'adresse de destination, le niveau de gravité, la source, les compteurs d'erreurs et les horodatages. Une configuration qui semble correcte n'assure pas que le collecteur reçoit les paquets. Il faut également confirmer le routage, les ACL, les ports en écoute, les files et l'espace de stockage côté collecteur.

### 2.6. Transport TCP et TLS : validation des capacités

Certains Cisco IOS/IOS XE proposent des variantes de configuration TCP, parfois avec port ou options de transport. La syntaxe dépend de la version. Sur les plateformes qui les prennent en charge, un exemple peut avoir la forme suivante :

```cisco
! Syntaxe indicative : valider avec l'aide contextuelle de la plateforme
logging host 192.0.2.20 transport tcp port 6514
```

Cette ligne est un modèle de discussion, pas une commande universelle à copier sans vérification. Le port 6514 est le port par défaut de Syslog sur TLS défini par la RFC 5425 ; employer ce numéro ne transforme pas un flux TCP en TLS. Le client doit négocier TLS et vérifier l'identité du serveur pour que le canal bénéficie de ces garanties.

Quand les équipements ne prennent pas TLS en charge, un relais proche peut collecter en UDP ou TCP sur un segment contrôlé puis envoyer au collecteur central avec TLS. Cette solution protège le segment entre relais et centre, mais le segment local n'est pas chiffré ; il doit être isolé, filtré et dimensionné. Les journaux sensibles ne doivent pas être envoyés en clair sur un réseau partagé non fiable au seul motif qu'un relais utilise TLS en aval.

La RFC 5425 définit le transport Syslog sur TLS avec authentification par certificats et port TCP par défaut 6514. Il faut gérer la chaîne CA, les noms DNS, l'expiration, la rotation et la révocation des certificats. Dans une architecture où l'authentification mutuelle est exigée, assure-toi que les émetteurs et le collecteur la prennent tous en charge et que les certificats clients sont correctement autorisés.

### 2.7. Collecteur Linux : exemple de réception TLS

Les détails varient selon la distribution et la version de rsyslog, notamment le module TLS installé. Un exemple indicatif de configuration pour un collecteur est :

```text
# Exemple conceptuel rsyslog : vérifier le module TLS disponible
module(load="imtcp")

# Les paramètres exacts dépendent du pilote TLS installé
input(
  type="imtcp"
  port="6514"
  StreamDriver.Name="gtls"
  StreamDriver.Mode="1"
  StreamDriver.AuthMode="x509/name"
  PermittedPeer="r1.example.net"
)
```

Cet extrait illustre les paramètres usuels : port d'écoute, pilote TLS, mode d'authentification et identité distante autorisée. Il ne constitue pas une configuration prête à l'emploi pour toute version de rsyslog. Les chemins des certificats, les permissions, les options de validation et la syntaxe exacte doivent être configurés selon le paquet installé et testés avant production.

Un collecteur Syslog TLS doit être contrôlé à trois niveaux : établissement TLS, réception du flux Syslog et persistance du message. Une connexion TLS active ne démontre pas que les messages sont correctement parsés, qu'ils sont écrits dans les bons fichiers ni que le disque est suffisamment dimensionné. Le test doit envoyer un événement identifiable, vérifier sa réception, contrôler ses champs normalisés et confirmer sa présence dans le stockage ou l'index.

### 2.8. Concevoir les politiques d'horodatage

Définis une politique explicite pour l'ensemble du parc : référence UTC, fuseau d'affichage, précision attendue, source de temps principale et secondaire, état acceptable de synchronisation, seuils d'alerte et procédure en cas de perte d'amont.

Pour les systèmes Unix, `chronyc tracking`, `chronyc sources -v` ou des commandes équivalentes fournissent des informations de suivi ; la syntaxe dépend du démon utilisé. Pour `ntpq`/`ntpd`, les commandes d'association et d'état diffèrent. Il faut éviter de documenter une commande comme générique pour toutes les distributions.

Le suivi doit mettre l'accent sur les évolutions et les seuils adaptés à l'application : offset qui augmente, changement inattendu de source, stratum 16, source marquée comme rejetée, absence de réponse, dispersion excessive, dérive au redémarrage et synchronisation perdue après mise à jour. Les seuils doivent être calibrés, car un seuil universel en microsecondes ne convient pas à toutes les machines ou toutes les topologies.

Pour Syslog, utilise un format qui préserve le fuseau ou une représentation UTC, et normalise les messages avec leur source d'origine. Ne modifie pas les timestamps source de façon destructive. Conserve l'heure d'ingestion séparément, car elle permet d'identifier des retards de transmission et des équipements dont l'horloge n'est pas fiable.

### 2.9. Test de résilience : perte d'une source NTP

Un test planifié doit confirmer que la disparition d'une source NTP entraîne un basculement maîtrisé et une alerte visible. Désactive ou bloque une source dans un laboratoire, observe les associations, la sélection, l'offset, le jitter et l'évolution de la dispersion. Rétablis la source puis vérifie que la machine ne passe pas continuellement d'une référence à l'autre.

Le test ne doit pas se limiter à un ping. Un serveur peut répondre à ICMP tout en ne fournissant pas un temps acceptable, ou répondre en NTP mais annoncer un état non synchronisé. Inversement, une politique de filtrage ICMP peut empêcher le ping sans empêcher UDP/123. Le diagnostic doit vérifier le protocole réel, les états NTP et la qualité de la source sélectionnée.

Sur les routeurs, un test de perte peut être observé à travers les sorties `show ntp status` et `show ntp associations detail`, ainsi que les journaux horodatés. Les détails changent selon le logiciel. Le test doit être mené à faible impact et documenté avec état initial, action, temps de détection, comportement de l'horloge et retour à l'état normal.

### 2.10. Test de perte Syslog et mesure des écarts

Pour mesurer la capacité de Syslog, génère un événement de test identifiable depuis un équipement, puis vérifie la présence du message dans le tampon local, dans le relais et dans le collecteur final. Note le timestamp émis, le timestamp de réception et, si disponible, l'horodatage d'ingestion dans la plateforme d'analyse.

Un décalage entre ces valeurs peut représenter le retard réseau, une file d'attente, la congestion du collecteur, un retard de traitement ou une horloge source incorrecte. Les timestamps doivent être comparés dans un fuseau uniforme. Une correction du parseur peut être requise si le format du message ne transporte pas explicitement le fuseau horaire.

Un test de panne doit vérifier :

- l'accumulation éventuelle dans les files locales ou relais ;
- les compteurs de messages émis, reçus, rejetés et perdus ;
- le comportement lorsque le disque est proche de la saturation ;
- la reprise après restauration du collecteur ;
- l'absence de duplications ou de boucles de relais ;
- les alarmes déclenchées par le pipeline de supervision.

Un résultat de test acceptable n'est pas seulement « le message est arrivé ». Il faut établir combien de temps il a mis, si la chaîne a conservé son intégrité et si les objectifs de service sont satisfaits pendant une pointe ou une panne représentative.

> **Astuce :** Crée un événement synthétique par équipement, avec un identifiant unique et une heure UTC connue. Compare la valeur émise, la réception au relais et l'indexation centrale. Ce marqueur permet de mesurer un retard de pipeline et de distinguer l'absence d'un message de l'incapacité du parseur à le retrouver. Couple ce contrôle à l'état NTP de l'émetteur et du collecteur ; sinon, une différence de timestamp pourrait provenir d'une horloge divergente plutôt que du transport.


## 3. Dépannage et Sécurité

### 3.1. Méthode structurée pour diagnostiquer NTP

Le diagnostic doit séparer la connectivité réseau, le protocole NTP, la sélection de source, la discipline de l'horloge et la validation de l'heure par les applications.

**Étape 1 — Connectivité :** vérifier la route vers la source, les interfaces, les ACL et le trafic UDP/123. Un test ICMP est utile mais non suffisant.

**Étape 2 — Réponse NTP :** vérifier que la source répond au protocole et que le pare-feu ne bloque pas la réponse. Une capture doit confirmer que la requête part et qu'une réponse revient.

**Étape 3 — État de source :** examiner le stratum, l'identifiant de référence, le délai, le jitter, la dispersion et l'indication de source sélectionnée. Un serveur peut répondre sans être synchronisé.

**Étape 4 — Sélection :** vérifier qu'au moins une source est jugée acceptable et que les autres sources ne sont pas incohérentes. Rechercher une dérive ou un saut de source non attendu.

**Étape 5 — Discipline locale :** contrôler les offsets, la fréquence corrigée, le temps écoulé depuis la dernière synchronisation et le comportement au démarrage. Une horloge système peut rester incorrecte pendant un certain temps après rétablissement du réseau.

**Étape 6 — Chaîne de confiance :** si NTS ou une authentification est utilisée, examiner certificats, clés, identité du pair et erreurs d'authentification. Ne désactive pas la validation cryptographique pour « réparer » rapidement la synchronisation.

### 3.2. Stratum 16, falseticker et source rejetée

Un stratum 16 indique généralement que la source n'est pas synchronisée dans le contexte NTP classique. La présence d'une association ne prouve donc pas qu'elle doit être utilisée comme référence. Il faut rechercher en amont la cause de la perte de synchronisation : source de référence en panne, serveur amont inaccessible, mauvaise configuration, oscillateur non validé ou panne de distribution.

Une source déclarée falseticker ou rejetée par l'algorithme est en désaccord avec les autres sources ou ne répond pas aux critères de sélection. Cela peut être provoqué par un serveur mal configuré, un incident réseau, une source compromise ou une simple différence de qualité. Il ne faut pas augmenter arbitrairement sa priorité ; il faut comparer les mesures, les dépendances de source et l'état des autres associations.

Si tous les serveurs internes partagent le même amont fautif, la cohérence interne peut rester forte tout en étant incorrecte. La diversité doit porter sur les références et leurs chemins de dépendance, pas uniquement sur les adresses IP. Les événements Syslog, la surveillance du récepteur GNSS, les alertes d'offset et les contrôles hors bande peuvent fournir des éléments indépendants.

### 3.3. Offset important ou instabilité récurrente

Un offset important peut provenir d'un serveur qui annonce une heure erronée, d'une machine démarrée avec une horloge très fausse, d'une virtualisation qui suspend ou dérive, d'une connexion réseau à délai variable ou d'une correction manuelle concurrente. Il faut d'abord vérifier qu'un seul mécanisme est responsable de la discipline d'horloge.

Un hyperviseur peut synchroniser l'heure invitée tandis qu'un service NTP la discipline simultanément. Selon l'environnement, cette double correction peut engendrer de l'instabilité. La politique doit préciser si l'heure de l'invité est gouvernée par NTP, par l'hyperviseur ou par une stratégie documentée combinant les deux sans compétition.

La congestion, le routage asymétrique, les tunnels et les équipements qui traitent les paquets en CPU peuvent dégrader la mesure. Utilise des sources au plus près lorsque le design le permet et compare les chemins. Pour les applications qui exigent une précision élevée, étudie l'horodatage matériel, PTP et les caractéristiques de la carte réseau au lieu d'essayer de compenser un chemin inadapté uniquement par des paramètres NTP.

### 3.4. Dépannage NTS et certificats

Les erreurs NTS peuvent provenir de certificats expirés, d'un nom de serveur ne correspondant pas au certificat, d'une autorité de certification inconnue, de la résolution DNS, d'un port TCP/4460 bloqué, d'un service NTS-KE indisponible ou d'une incompatibilité d'algorithme. Les échanges de synchronisation peuvent ensuite échouer même si l'établissement initial a réussi, par exemple en raison de cookies invalides ou de clés mal gérées.

Il faut diagnostiquer séparément la négociation NTS-KE et le trafic NTP. Confirme la validation de la chaîne TLS, l'identité du serveur, la date de validité du certificat, le fonctionnement DNS et les règles réseau. Vérifie aussi que le client conserve et renouvelle correctement ses cookies selon son implémentation.

Il est dangereux de régler l'horloge manuellement à une valeur arbitraire afin de contourner l'expiration d'un certificat. Une procédure de bootstrap peut exister, mais elle doit être documentée, limitée, journalisée et suivie d'une resynchronisation fiable. Le contrôle du certificat ne doit pas être désactivé durablement.

### 3.5. Dépannage Syslog : absence de messages

Si le collecteur ne reçoit aucun message, le diagnostic suit la chaîne émetteur → réseau → relais → collecteur → parsing → stockage.

Sur l'émetteur, vérifie la destination, le seuil de gravité, l'interface source, l'horloge et les restrictions de journalisation. Sur le réseau, vérifie le routage, les ACL, le pare-feu, le NAT éventuel, le port et le transport. Sur le collecteur, vérifie l'écoute, la négociation TLS le cas échéant, les journaux du service, les permissions et l'état des disques.

Une capture réseau peut démontrer que les paquets arrivent au collecteur, mais pas nécessairement qu'ils sont écrits. Un message reçu au niveau socket peut être rejeté par un parseur, écrasé par une règle de routage ou non indexé. Il faut rechercher l'événement dans le stockage brut et dans les journaux internes du collecteur.

Les équipements réseau disposent parfois de plusieurs destinations et de tampons limités. La configuration du niveau de gravité doit être comparée au niveau de l'événement de test. Si le seuil est `warnings`, un événement `informational` ne sera normalement pas transmis par cette destination. Le premier test doit utiliser une sévérité incluse dans le seuil configuré.

### 3.6. Messages tronqués, mal parsés ou horodatés de façon incorrecte

Les formats Syslog hérités ne comportent pas toujours les champs nécessaires à un parseur moderne. La présence d'un hostname dans le corps ne garantit pas qu'il sera interprété comme hostname. Les relais peuvent réécrire certains champs, et les collecteurs peuvent déduire un timestamp incomplet à partir de l'heure de réception.

Pour résoudre ces problèmes :

1. conserver un échantillon brut du message reçu ;
2. identifier le format et l'encodage utilisés par l'émetteur ;
3. vérifier les règles de framing si TCP est employé ;
4. vérifier l'extraction du timestamp et du fuseau ;
5. comparer l'adresse source transportée et l'identité déclarée ;
6. tester avec une règle de parsing isolée avant la mise en production ;
7. conserver la version de la règle de parsing pour faciliter la reproduction des résultats.

Un message tronqué peut être dû à une limite de taille ou à une incompatibilité de framing, mais aussi à un champ de message contenant une séquence interprétée comme séparateur. Il faut vérifier le transport réellement utilisé et la manière dont chaque composant découpe les messages, plutôt que supposer que TCP préserve spontanément les frontières applicatives.

### 3.7. Fiabilité du stockage et intégrité des journaux

La collecte n'est qu'une étape de la conservation probante. Les journaux doivent être protégés contre la modification et la suppression non autorisées, et les contrôles d'accès doivent séparer les rôles d'administration du collecteur, d'analyse et d'administration des équipements source.

Des mécanismes possibles comprennent :

- stockage sur un domaine distinct des équipements surveillés ;
- files d'attente persistantes sur les relais ;
- contrôle des droits d'écriture et de suppression ;
- rétention alignée sur les obligations et le risque ;
- réplication vers un stockage indépendant ;
- immutabilité ou verrouillage de rétention lorsque les exigences l'imposent ;
- horodatage et journalisation des opérations d'administration ;
- contrôles de complétude à l'aide de marqueurs synthétiques et de compteurs d'ingestion.

Une simple sauvegarde n'est pas une garantie d'intégrité : un attaquant disposant d'un accès administratif peut tenter de modifier les originaux et les sauvegardes. Les exigences de preuve doivent définir les contrôles d'accès, la rétention, l'intégrité cryptographique, la séparation des responsabilités et les procédures d'extraction des journaux.

### 3.8. Défense contre l'injection et l'usurpation Syslog

Syslog traditionnel sur UDP ne prouve pas cryptographiquement l'identité de l'émetteur. Un acteur capable d'injecter du trafic vers un collecteur peut tenter de produire des événements falsifiés ou trompeurs. Un hostname déclaré n'est qu'une donnée du message et peut être imité. L'utilisation de TLS avec validation de certificat améliore l'authentification de la connexion, mais l'identité du certificat doit être associée à l'actif attendu et la configuration du collecteur doit refuser les pairs non autorisés.

Les systèmes doivent également traiter le contenu du message comme une donnée potentiellement hostile. Les applications doivent neutraliser ou échapper les retours à la ligne et caractères de contrôle dans les champs utilisateurs afin d'éviter la falsification de lignes ou la confusion des parsers. Les parseurs doivent être robustes face aux champs trop longs, aux formats inattendus et aux caractères non valides.

Ne place pas de mots de passe, jetons, clés privées ou secrets dans les messages de diagnostic. Les journaux peuvent être copiés et conservés sur plusieurs systèmes ; une information sensible journalisée dans une seule application peut ensuite être distribuée largement. Les politiques de minimisation doivent être intégrées au développement et à l'exploitation.

### 3.9. DDoS, amplification et exposition des ports

Les serveurs NTP et Syslog sont des services réseau à protéger. Un NTP mal exposé peut être utilisé dans des attaques par réflexion, tandis qu'un collecteur Syslog peut être saturé par des flux volumineux ou des tentatives de connexion TLS répétées. Les options exactes d'amplification et les vulnérabilités historiques varient avec la version, mais le principe de défense est stable : exposer le minimum, limiter les sources, surveiller les taux et maintenir les implémentations corrigées.

Pour NTP, n'autorise que les clients internes ou les pairs explicitement nécessaires. Désactive ou restreins les fonctions de contrôle et d'information lorsqu'elles ne sont pas requises. Applique des limites de débit adaptées, sans casser la synchronisation des clients légitimes. Sur un serveur public intentionnel, suis les recommandations de l'opérateur et de l'implémentation plutôt que d'exposer simplement UDP/123 par défaut.

Pour Syslog, protège le collecteur contre les connexions non attendues, fixe des limites de taille et de débit, surveille les files et définis les priorités de traitement. Une limite trop agressive peut éliminer les événements importants en période d'incident ; une limite inexistante peut entraîner une saturation et des pertes globales. Les seuils doivent être testés sous charge.

### 3.10. Cloisonnement, disponibilité et reprise

Le service NTP doit être disponible indépendamment du système de journalisation qu'il aide à dater. Sinon, une panne de collecte peut priver également le plan de temps de ses alertes et masquer son propre incident. À l'inverse, les serveurs NTP doivent envoyer leurs propres journaux à une destination qui n'est pas totalement dépendante de leur horloge locale pour organiser les événements.

Les deux services doivent être placés dans des segments et politiques de contrôle appropriés. Les clients n'ont généralement besoin que de rejoindre les serveurs NTP sur UDP/123. Les émetteurs Syslog n'ont besoin de joindre que les relais ou collecteurs autorisés et les ports définis. L'administration des serveurs doit se faire via un réseau de gestion distinct avec authentification forte et journalisation.

Les objectifs de disponibilité doivent être chiffrés : durée de perte NTP tolérée, offset maximum acceptable, taux de pertes Syslog, latence d'ingestion, durée de tamponnement hors ligne, RPO des journaux et temps de reprise. Un plan de reprise qui indique seulement « deux serveurs » sans définir les dépendances et les critères de basculement n'est pas suffisant.

### 3.11. Supervision et indicateurs d'exploitation

Pour NTP, mesure au minimum :

- état synchronisé ou non synchronisé ;
- source actuellement sélectionnée ;
- stratum et changements de source ;
- offset et évolution de l'offset ;
- dispersion et jitter selon l'implémentation ;
- disponibilité des sources amont ;
- dérive au redémarrage ;
- erreurs d'authentification ou de négociation NTS.

Pour Syslog, mesure :

- volume d'événements par seconde et par source ;
- messages rejetés ou perdus ;
- profondeur et âge des files ;
- latence entre timestamp source, réception et ingestion ;
- erreurs TLS et taux d'échec de connexion ;
- erreurs de parsing et champs manquants ;
- occupation disque, rétention, répliques et échecs d'indexation ;
- présence des événements synthétiques de contrôle.

Les alertes doivent être actionnables. Une alerte de « NTP down » devrait préciser l'équipement, la dernière source sélectionnée, l'offset observé, la durée de panne et les voisins affectés. Une alerte Syslog devrait identifier le point de la chaîne en panne : émission, transport, relais, ingestion ou stockage.

### 3.12. Procédure de changement et validation préproduction

Avant de modifier les serveurs NTP ou Syslog, sauvegarde la configuration, inventorie les dépendances et établis les critères de retour arrière. Les changements doivent être faits par étapes : quelques équipements pilotes, un site ou un segment, puis l'ensemble du parc. Vérifie les versions logicielles et les capacités du matériel avant d'appliquer des commandes issues d'une autre plateforme.

Pour un changement NTP, valide la synchronisation initiale, la bascule entre sources, les seuils d'offset, les conséquences de la perte d'amont et le comportement au retour de la source préférée. Pour Syslog, valide le transport, les certificats, l'intégrité du parsing, la persistance, le volume sous charge et la récupération après interruption du collecteur.

Le retour arrière doit lui aussi être testé. Une modification de source de temps peut introduire un saut de l'horloge ; un changement de transport Syslog peut interrompre les messages sans avertissement visible sur l'équipement source. Conserve une voie de diagnostic hors bande, une procédure d'accès administrative et des journaux indépendants qui permettent d'observer le changement.

> **Danger :** Une altération de l'heure peut avoir un effet systémique sans provoquer immédiatement de panne réseau visible. Des certificats peuvent paraître invalides, des mécanismes Kerberos ou des jetons expirer de manière incohérente, les transactions se retrouver mal ordonnées et les journaux perdre leur valeur chronologique. Inversement, une falsification de Syslog peut faire apparaître un faux événement, masquer une activité ou attribuer un message à un mauvais équipement. Protège donc les sources de temps et les journaux comme une infrastructure de sécurité : segmentation, contrôle d'identité, gestion des clés et certificats, surveillance de la dérive, rétention protégée et procédures d'incident documentées.

### 3.13. Matrice de diagnostic rapide

| Symptôme | Causes possibles | Contrôles prioritaires |
|---|---|---|
| NTP répond mais ne se synchronise pas | Source non valide, stratum 16, mesure incohérente | État NTP, associations détaillées, source amont |
| Offset qui augmente | Dérive, chemin variable, correction concurrente | Offset, jitter, charge, hyperviseur, source active |
| Certificat NTS refusé | Horloge initiale fausse, certificat expiré, nom incorrect | DNS, date du certificat, chaîne CA, port 4460/TCP |
| Aucun Syslog au collecteur | Niveau filtré, route/ACL, mauvais port, service inactif | Configuration source, capture, état d'écoute |
| Messages reçus mais absents du SIEM | Parsing, index, routage interne, quota | Message brut, logs du collecteur, files, stockage |
| Horodatage décalé | Fuseau mal interprété, horloge source erronée | Timestamp brut, temps d'ingestion, état NTP |
| Perte lors d'une panne du collecteur | UDP sans tampon, file pleine, relais indisponible | Compteurs, files persistantes, scénario de reprise |
| Identité de source douteuse | Hostname falsifié, relais, certificat mal associé | IP de transport, identité TLS, inventaire d'actifs |

## Points à retenir

- **NTP est un système de mesure, de sélection et de discipline temporelle, pas une simple requête à un serveur.** Le stratum ne suffit pas à classer la qualité ; l'offset, la dispersion, la diversité des sources, la stabilité et l'authenticité doivent être évalués. NTS, lorsqu'il est pris en charge, apporte une protection cryptographique au mode client-serveur, mais ne garantit pas que la source amont est exacte.
- **Syslog doit être conçu de bout en bout.** Le format du message, le transport, le framing, le TLS, la collecte, les files d'attente, le parsing et le stockage ont chacun des modes de panne distincts. UDP est best effort ; TCP ou TLS ne prouvent pas à eux seuls la persistance durable au collecteur.
- **L'intégrité de l'horodatage est essentielle à la valeur des journaux.** Conserve les timestamps source et ingestion, normalise les fuseaux, mesure les pertes et surveille la dérive. Protège NTP, Syslog, les secrets, les certificats et le stockage dans une architecture segmentée et redondante.

## Références techniques

- [RFC 5905 — Network Time Protocol Version 4: Protocol and Algorithms Specification](https://www.rfc-editor.org/rfc/rfc5905.html)
- [RFC 8915 — Network Time Security for the Network Time Protocol](https://www.rfc-editor.org/rfc/rfc8915.html)
- [RFC 5424 — The Syslog Protocol](https://www.rfc-editor.org/rfc/rfc5424.html)
- [RFC 5425 — TLS Transport Mapping for Syslog](https://www.rfc-editor.org/rfc/rfc5425.html)
- [RFC 5426 — UDP Transport Mapping for Syslog](https://www.rfc-editor.org/rfc/rfc5426.html)
- [RFC 6587 — Transmission of Syslog Messages over TCP](https://www.rfc-editor.org/rfc/rfc6587.html)
- Documentation Cisco IOS/IOS XE correspondant à la version et à la plateforme déployées.
