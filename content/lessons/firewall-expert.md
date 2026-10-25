# Pare-feu & NGFW - Expert

**Niveau :** EXPERT

Un pare-feu moderne n’est pas seulement une liste de ports autorisés ou refusés. Il est un point de décision de sécurité placé dans un chemin réseau, qui combine contexte de connexion, identité, application, réputation, état du terminal, zone de confiance, stratégie métier et signaux de détection. Dans une architecture bien conçue, il applique une politique explicite, cohérente avec le modèle de menace, et produit des événements suffisamment riches pour permettre l’investigation, la mesure d’efficacité et l’amélioration continue.

Le niveau expert exige de raisonner en termes de chemins de données et de plans de contrôle, de dépendances entre routage, NAT, inspection et politiques, et de conséquences opérationnelles. Une règle isolée peut sembler correcte tout en étant contournée par un chemin secondaire, une famille IP non filtrée, un tunnel, un réseau d’administration, une exception temporaire oubliée ou une asymétrie de routage. La sécurité réelle se mesure donc à partir du trafic effectivement possible, pas seulement à partir d’un écran de configuration.

Ce cours aborde les pare-feu stateful, les pare-feu de nouvelle génération (NGFW), les architectures en zones, l’identification applicative, la prévention d’intrusion, le déchiffrement TLS, le filtrage DNS et URL, la segmentation, le NAT, IPv6, la haute disponibilité, le dimensionnement, la journalisation et l’automatisation. Les commandes présentées sont des exemples d’orientation : la syntaxe, les capacités et l’ordre d’évaluation varient selon les familles de produits et les versions. Une configuration de production doit être vérifiée dans la documentation du constructeur et dans un laboratoire correspondant au matériel réellement déployé.

L’objectif n’est pas d’empiler un maximum de fonctions. Il est de construire une politique vérifiable, compréhensible, performante et exploitable, puis de prouver que les flux attendus passent tandis que les flux interdits échouent, y compris en situation de panne, de changement de route, de mise à jour des signatures ou d’investigation d’incident.

> **Analogie** : imaginez un poste frontière doté d’un registre de voyageurs, d’un contrôle des bagages, d’un système d’identification et d’une caméra. Le pare-feu stateful suit le dossier d’une connexion ; le NGFW enrichit ce dossier avec l’application, l’identité et les menaces détectées. Mais si une route secondaire contourne le poste frontière, même le contrôle le plus avancé devient inutile. L’architecture complète compte autant que le moteur d’inspection.


## 1. La théorie et les algorithmes

### 1.1 Modèle de décision : du paquet au flux autorisé

Un paquet traverse une chaîne de traitements qui dépend de la plate-forme : réception sur une interface, validation de couche 2 ou 3, classification de zone, recherche de route, traitement NAT, recherche d’une session, évaluation de politique, inspection de sécurité, application de QoS éventuelle, puis transmission. Certains équipements effectuent une partie de ces étapes dans un autre ordre, ou reclassent le trafic après une traduction d’adresse. Il faut donc éviter de réciter un ordre universel : l’ordre réel doit être établi à partir de la documentation du produit et de tests contrôlés.

La décision peut être représentée par un tuple enrichi :

- **Réseau** : famille IP, adresse source et destination, protocole, ports, indicateurs TCP, ICMP ou ICMPv6.
- **Chemin** : interface d’entrée, zone source, interface et zone de sortie, route choisie, VRF ou contexte virtuel.
- **Session** : nouvelle connexion ou trafic appartenant à une session existante, état TCP suivi, délai d’expiration et compteurs.
- **Identité et application** : utilisateur ou groupe, appareil, application détectée, fonction applicative et méthode d’identification.
- **Contexte de menace** : réputation, catégorie URL, verdict IPS, fichier, anomalie de protocole et renseignement de menace disponible.
- **Action** : autoriser, refuser, réinitialiser, rediriger, mettre en quarantaine, journaliser ou appliquer une inspection complémentaire.

Ces dimensions ne sont pas toujours toutes disponibles au début du traitement. Une règle peut autoriser une connexion sur la base du tuple IP/port, puis une inspection applicative plus tardive peut détecter une application non souhaitée. L’architecture doit préciser si cette détection ferme la session, bloque seulement certaines transactions, ou génère uniquement une alerte. « Autorisé par la politique réseau » ne signifie donc pas nécessairement « toute opération applicative autorisée ».

### 1.2 Pare-feu sans état, stateful et proxy

Un filtre **stateless** décide paquet par paquet selon des champs visibles. Il ne conserve pas de contexte de connexion : autoriser un paquet TCP entrant selon son port source et ses drapeaux n’équivaut pas à confirmer qu’il appartient à une session légitime. Ce mode reste utile pour les filtres simples, les ACL d’interface, les listes de contrôle de plan de contrôle et les protections anti-usurpation, mais il peut exiger des règles de retour plus complexes.

Un pare-feu **stateful** crée une entrée de session lors de l’autorisation d’un flux et associe ensuite les paquets compatibles à cette session. Il mémorise par exemple le tuple de départ, les adresses et ports traduits, l’état TCP observé, les délais et parfois des éléments d’inspection applicative. Le retour est admis lorsque la plate-forme estime qu’il appartient à une session existante autorisée. Cela réduit le besoin d’écrire des ouvertures explicites pour chaque paquet de retour, mais ne remplace pas les contrôles de protocole, la validation des séquences TCP ni les règles qui encadrent l’établissement de nouvelles sessions.

Un **proxy applicatif** termine la connexion côté client puis ouvre éventuellement une seconde connexion côté serveur. Cette architecture permet une inspection riche et la normalisation du protocole, mais introduit un coût de traitement, des exigences de compatibilité et parfois une modification des certificats ou des mécanismes d’authentification. Un NGFW n’est pas nécessairement un proxy complet : certaines fonctions sont intégrées au chemin de données, d’autres utilisent des mécanismes hybrides.

| Propriété | Statless / ACL | Stateful | Proxy applicatif / inspection approfondie |
|---|---|---|---|
| Mémoire de session | Aucune ou minimale | Table de sessions | Contexte applicatif et connexions terminées selon l’architecture |
| Contrôle du retour | Règles explicites souvent nécessaires | Associé à une session reconnue | Trafic relayé et inspecté dans un contexte applicatif |
| Visibilité applicative | Limitée aux champs disponibles | Variable | Souvent élevée pour les protocoles pris en charge |
| Coût par flux | Généralement faible | Moyen, lié à la table d’état | Plus élevé et dépendant de l’inspection |
| Limite majeure | Ne comprend pas le contexte du flux | Peut faire confiance à une classification insuffisante | Latence, compatibilité, capacité et portée d’inspection |

### 1.3 Le moteur de politique et la logique de première correspondance

Les règles sont généralement évaluées dans un ordre défini. Dans une liste séquentielle classique, la première règle correspondant au trafic produit la décision, sauf mécanisme spécifique de la plate-forme. Une règle générique d’autorisation placée avant une règle de blocage peut donc rendre cette dernière inopérante. Certains NGFW utilisent des couches distinctes — pré-règles, règles locales, règles post-règles, règles de déchiffrement et profils de sécurité — dont l’ordre doit être compris séparément.

Une politique experte doit décrire explicitement :

1. les zones et les chemins que la règle couvre ;
2. les objets réseau utilisés et leur provenance ;
3. les utilisateurs, applications et services attendus ;
4. l’action réseau et les profils d’inspection attachés ;
5. les exigences de journalisation, la justification et le propriétaire ;
6. la date de révision ou d’expiration lorsqu’il s’agit d’une exception.

Les objets et groupes facilitent la maintenance, à condition qu’ils soient maîtrisés. Un groupe partagé peut être modifié pour une nouvelle application et ouvrir involontairement un flux dans plusieurs politiques. Les objets imbriqués, les groupes trop larges et les alias peu explicites compliquent l’analyse. Les noms comme `SRC_USERS_SUPPORT`, `DST_DNS_APPROVED` ou `APP_FINANCE_PORTAL` rendent les règles plus lisibles que `NET_12` ou `TEMP_ALLOW_4`.

### 1.4 Algorithme d’évaluation : raisonnement reproductible

Un modèle conceptuel de décision peut être décrit en pseudocode. Il ne reproduit pas l’implémentation interne d’un constructeur ; il sert de méthode d’analyse :

```text
recevoir(paquet)
valider_entete_et_protocole(paquet)
identifier_contexte(paquet, interface, zone, vrf)
si paquet correspond à une session valide :
    appliquer contrôles propres à la session
    exécuter inspection nécessaire
    transmettre ou bloquer selon résultat
sinon :
    déterminer chemin et contexte NAT selon la plate-forme
    rechercher première politique applicable
    si aucune politique n'autorise le nouveau flux :
        refuser et journaliser selon la politique de logs
    sinon :
        créer état de session si le moteur le permet
        exécuter profils IPS, application, URL, fichiers ou TLS requis
        transmettre uniquement si les contrôles requis réussissent
```

Les étapes peuvent être réordonnées par le produit. Une session existante peut aussi être réévaluée après un changement de politique, ou continuer avec l’ancienne décision jusqu’à expiration, selon le système. Après une modification critique, il peut être nécessaire de fermer des sessions existantes pour que la nouvelle politique soit immédiatement appliquée. Cette opération doit être soigneusement planifiée, car elle peut interrompre des applications sensibles.

> **Piège :** ne déduisez pas l’ordre de traitement à partir du seul numéro de règle affiché. L’ordre de NAT, le routage, les règles de déchiffrement, les profils de sécurité et les exceptions locales peuvent être traités dans des phases distinctes. Consultez le diagramme de traitement de la version exacte du produit et confirmez-le par des tests.

### 1.5 Politique fondée sur les zones et architecture de confiance

Les zones représentent des domaines présentant un niveau de confiance, des fonctions ou des exigences similaires : Internet, DMZ publique, utilisateurs, serveurs métier, administration, sauvegarde, OT/industriel, invités et services partagés. Le principe est de contrôler les transitions entre zones, pas seulement les sous-réseaux. Les interfaces qui partagent un même segment logique peuvent être regroupées dans une zone, mais le regroupement doit être justifié par des exigences de sécurité compatibles.

Le modèle doit couvrir les flux **nord-sud** (entre réseaux internes et Internet) et **est-ouest** (entre sous-réseaux internes). Un pare-feu de périmètre bien configuré ne compense pas une architecture interne dans laquelle tous les serveurs peuvent communiquer librement. La microsegmentation peut s’appuyer sur des pare-feu physiques, virtuels, distribués ou des contrôles d’hôtes, selon la topologie.

```text
                        INTERNET
                           |
                    [ Pare-feu NGFW ]
                      /           \
                  [DMZ]           [VPN]
                   |                |
             Web / reverse proxy   Utilisateurs distants
                   |
             [Zone applicative]
                   |
              [Zone données]
                   |
          [Zone sauvegarde isolée]

 [Zone administration] ---> gestion contrôlée des équipements
```

Les flèches illustrent des relations possibles, pas des autorisations implicites. Par exemple, un serveur Web en DMZ peut recevoir HTTPS depuis Internet, mais l’accès à la base de données doit être limité aux ports et destinations réellement nécessaires. Les serveurs de sauvegarde ne devraient pas accepter des connexions administratives depuis chaque segment. La gestion doit être séparée du trafic utilisateur, et les chemins de dépannage d’urgence doivent eux aussi être contrôlés.

### 1.6 NGFW : identification des applications et limites du DPI

Un NGFW combine généralement des capacités réseau stateful avec certaines fonctions telles que l’identification des applications, l’IPS, le filtrage URL/DNS, la réputation, l’analyse de fichiers, le contrôle d’identité et la détection de comportements. Le nom « NGFW » n’établit pas que toutes ces fonctions sont présentes, activées, licenciées ou efficaces dans chaque contexte. Il faut vérifier le modèle, les licences, les limites de débit avec inspection, la couverture protocolaire et la qualité des mises à jour.

L’identification applicative peut exploiter plusieurs signaux : ports, signatures de protocole, séquences d’échange, métadonnées, certificats, noms de serveur, négociation TLS, comportement et déchiffrement autorisé. Les ports ne suffisent pas : des applications peuvent utiliser HTTPS sur TCP/443, QUIC sur UDP/443, des ports dynamiques ou des tunnels. À l’inverse, un port connu n’atteste pas que le service légitime s’y trouve.

L’inspection approfondie des paquets (DPI) analyse certains contenus ou motifs au-delà de l’en-tête réseau. Elle est limitée par le chiffrement, la fragmentation, les formats propriétaires, les protocoles encapsulés, la compression, la version de protocole et la charge de traitement. Un bon NGFW indique le niveau de visibilité réel : application reconnue avec confiance élevée, application probable, session chiffrée non inspectée, ou trafic inconnu.

L’identification doit conduire à des décisions proportionnées. Bloquer une application métier entière parce qu’elle partage une signature avec une fonction interdite peut casser la productivité. Une règle peut autoriser un service et interdire certaines fonctions, comme le partage de fichiers ou l’administration à distance, si la plate-forme supporte cette granularité et si le trafic est suffisamment visible.

### 1.7 IPS, signatures et prévention des menaces

Un système de prévention d’intrusion (IPS) compare le trafic à des signatures, des règles de protocole et parfois des modèles comportementaux. Il peut détecter des tentatives d’exploitation, des anomalies, des scans ou des protocoles malformés. Ses actions typiques sont l’alerte, le blocage, la réinitialisation ou la mise en quarantaine. Une signature est un indicateur technique, pas une preuve parfaite : elle peut générer un faux positif, manquer une variante ou ne pas reconnaître un protocole chiffré.

La stratégie doit différencier les catégories de menace, la criticité des actifs, le risque métier et la qualité de validation. En phase pilote, certaines familles de signatures peuvent être en alerte afin d’observer le comportement. Les règles à fort niveau de confiance et les protections indispensables peuvent être mises en blocage après validation. Il ne faut pas laisser indéfiniment l’ensemble de l’IPS en alerte pour éviter les exceptions : cette situation donne un sentiment de protection sans blocage effectif.

Les exceptions doivent être limitées par source, destination, service, signature, durée et justification. Une exclusion globale de l’IPS pour un serveur critique est une dette de sécurité majeure. Lorsqu’une application déclenche un faux positif, collectez l’événement, la version de signature, le flux, la requête ou le protocole concerné, puis validez auprès du propriétaire métier et du fournisseur avant de créer une exception minimale.

### 1.8 Inspection TLS et déchiffrement

Le chiffrement TLS protège la confidentialité et l’intégrité, mais réduit la visibilité d’un dispositif qui ne déchiffre pas le flux. Selon la plate-forme, le NGFW peut exploiter les éléments visibles de la négociation, le certificat, le nom de serveur et la réputation. Cela n’équivaut pas à inspecter le contenu applicatif. La visibilité réelle dépend de la version TLS, de la négociation, d’ECH lorsqu’il est utilisé, de QUIC, des applications épinglant leurs certificats et des contraintes des terminaux.

L’inspection TLS intermédiaire consiste généralement à terminer une session TLS côté client puis à établir une autre session vers le serveur. Le système présente au client un certificat signé par une autorité interne approuvée sur les postes gérés. Il faut protéger la clé privée de cette autorité, gérer le cycle de vie des certificats et définir clairement les catégories exemptées. Un défaut de confiance sur les terminaux provoque des erreurs de certificat ; une mauvaise gestion de clé peut transformer le dispositif d’inspection en risque majeur.

Les exceptions peuvent être nécessaires pour les applications utilisant le *certificate pinning*, certaines applications financières, les services médicaux, les systèmes OT, les appareils non gérés et les contraintes réglementaires ou contractuelles. Elles doivent être documentées, réduites au minimum et surveillées. Le déchiffrement augmente la charge CPU, la latence et le volume de données à analyser ; la capacité d’un équipement annoncée sans déchiffrement ne doit pas être assimilée à sa capacité en inspection TLS complète.

> **Astuce :** distinguez toujours trois états dans vos tableaux de bord : trafic chiffré observé sans déchiffrement, trafic effectivement déchiffré et inspecté, et trafic exempté. Un compteur « HTTPS autorisé » ne permet pas de mesurer la couverture réelle de l’inspection de contenu.

### 1.9 NAT, routage et politiques : dépendances critiques

Le NAT modifie des adresses et parfois des ports. Le pare-feu peut évaluer la règle en utilisant l’adresse originale, l’adresse traduite, ou des objets adaptés à une phase précise du traitement. Le comportement dépend du constructeur. Une publication de serveur peut exiger une translation destination (DNAT) et une politique de sécurité qui autorise le flux vers l’objet approprié. Une règle NAT seule ne prouve pas que le flux est autorisé ; une règle de sécurité seule ne garantit pas que la translation et le routage fonctionnent.

Pour une connexion entrante, vérifiez la route vers l’interface publique, l’objet NAT, le destinataire après traduction, la politique de sécurité et la route retour. Pour une connexion sortante, vérifiez l’adresse source après traduction, l’interface de sortie et la route de retour. Dans les environnements à plusieurs opérateurs, la réponse peut sortir par un autre lien, déclenchant un rejet par le suivi d’état ou par les équipements amont.

La traduction peut aussi interagir avec les ACL, le routage basé sur la politique (PBR), les VPN et les sélecteurs de trafic IPsec. Les exceptions NAT sont souvent nécessaires pour que le trafic entre deux sous-réseaux privés utilisant le même équipement ne soit pas traduit à tort. Une analyse experte documente le tuple avant NAT, le tuple après NAT, la règle de sécurité utilisée et la route retenue pour chaque étape.

### 1.10 Routage asymétrique et synchronisation d’état

Un pare-feu stateful s’attend souvent à voir les deux directions d’une session, même si quelques mécanismes prennent en charge l’asymétrie. Si le trafic aller traverse le pare-feu A et le retour le pare-feu B, chaque nœud peut ne voir qu’une partie de la connexion. Le résultat peut être un échec intermittent, des réinitialisations TCP ou des compteurs indiquant une session incomplète.

La synchronisation d’état en haute disponibilité peut partager certaines informations entre les nœuds, mais elle ne supprime pas toutes les limites : différences de chemin, sessions non synchronisées, délais de convergence, NAT dépendant du nœud, connexions UDP, inspection applicative non transférable et versions différentes. Les concepteurs doivent s’assurer que le routage, les règles, les tables NAT et les mécanismes HA sont cohérents, puis tester les pannes réelles.

```text
             Aller : client ---> [FW-A] ---> serveur
             Retour : client <--- [FW-B] <--- serveur

 Risque : FW-A et FW-B ne disposent pas du même état de session.
 Solution possible : chemin symétrique, cluster compatible et état synchronisé,
                     ou architecture explicitement conçue pour l'asymétrie.
```

Ne désactivez pas l’inspection stateful comme correction générique à un problème de routage asymétrique. Cela affaiblirait la sécurité sans traiter la cause racine. Commencez par les tables de routage, les annonces dynamiques, la PBR, les liens redondants, les ECMP et les chemins VPN.

### 1.11 IPv6 et politique double pile

IPv6 doit disposer d’une politique de sécurité explicite. Une configuration IPv4 stricte ne protège pas automatiquement IPv6. Les réseaux à double pile doivent disposer d’un inventaire des sous-réseaux, d’une stratégie de routage et de filtrage IPv6, d’une journalisation cohérente et de tests couvrant les deux familles. Il faut également examiner les tunnels IPv6, les mécanismes de transition et les chemins créés par les réseaux invités ou les services cloud.

ICMPv6 est essentiel à des fonctions comme la découverte de voisins et la découverte MTU du chemin. Le bloquer complètement peut casser la connectivité ou produire des symptômes difficiles à diagnostiquer. Il faut contrôler les messages selon le contexte et les recommandations du système, plutôt que copier mécaniquement la politique ICMPv4. La découverte des routeurs, les annonces de préfixes et la protection contre les annonces frauduleuses peuvent nécessiter des contrôles complémentaires aux frontières de couche 2.

Les adresses temporaires, la découverte de voisins, les groupes multicast et l’absence de NAT systématique en IPv6 modifient la manière de lire les journaux. La sécurité doit s’appuyer sur la politique, la segmentation et les identités, non sur l’hypothèse que des adresses privées sont forcément invisibles.

### 1.12 Haute disponibilité et continuité de service

Les architectures HA incluent typiquement un mode actif/passif, actif/actif ou une répartition en clusters selon la plate-forme. Les éléments de conception comprennent le suivi de liens, les sondes de santé, le quorum ou mécanisme d’arbitrage, la synchronisation de configuration, les tables de sessions, les licences, les versions logicielles et les chemins de gestion. La redondance doit éviter le partage d’une même cause de panne, comme un seul commutateur, une seule alimentation, un seul opérateur ou une dépendance commune à un DNS indisponible.

Le basculement doit être testé pour plusieurs cas : perte d’interface, panne du nœud actif, perte de la liaison de synchronisation, partition réseau entre membres, redémarrage après mise à jour et perte d’une route critique. Selon la plate-forme, les nouvelles connexions peuvent être rétablies alors que les sessions existantes sont interrompues. Le plan de continuité doit décrire les attentes exactes, les seuils de détection, les procédures de retour au nœud nominal et les risques de basculement répété (*flapping*).

Une mise à jour ne doit pas être lancée simultanément sur tous les membres sans procédure supportée. La séquence de mise à niveau, la compatibilité des versions, la possibilité de retour arrière, l’impact sur les signatures et les éventuels changements du moteur de politique doivent être validés dans les notes de version et le laboratoire.

### 1.13 Dimensionnement et performances

La capacité nominale d’un pare-feu varie selon les conditions de mesure. Les chiffres de débit « pare-feu » ne sont pas interchangeables avec le débit en IPS, antivirus, contrôle applicatif, déchiffrement TLS ou journalisation détaillée. Les métriques utiles comprennent :

- débit réel selon la taille des paquets et le profil d’inspection ;
- nouvelles connexions par seconde et taux d’établissement TCP ;
- nombre de sessions simultanées et répartition TCP/UDP ;
- latence ajoutée, pertes, retransmissions et gigue ;
- utilisation CPU, accélérateurs, mémoire et files d’attente ;
- taux de déchiffrement TLS, taux d’échec et coût des certificats ;
- volume de journaux, capacité locale et débit de transfert au SIEM.

Le nombre d’objets et la longueur d’une liste de règles ne suffisent pas à prédire les performances. Certains moteurs compilent les politiques en structures optimisées ; d’autres opérations sont plus coûteuses, notamment certaines recherches d’identité, classifications d’application, validations de certificat ou traitements de contenu. Il faut mesurer un profil représentatif du trafic réel, incluant les pics, les mises à jour et les opérations de sauvegarde.

Une marge de capacité est nécessaire pour absorber les pointes et les pannes d’un membre du cluster. En actif/passif, le nœud survivant doit pouvoir supporter la charge complète en mode dégradé. En actif/actif, la redistribution de flux lors d’une panne peut concentrer les sessions sur un nœud restant. Un dimensionnement fondé seulement sur la moyenne journalière est fragile.

### 1.14 Journalisation, observabilité et SIEM

Les journaux doivent permettre de répondre à des questions opérationnelles : quel flux a été refusé, par quelle règle, depuis quel actif, à quelle heure, avec quelle application, quel utilisateur connu et quel verdict de sécurité ? Les événements utiles incluent les autorisations importantes, les refus pertinents, les alertes IPS, les événements de déchiffrement, les changements de politique, les authentifications administratives, les mises à jour de signatures et les changements d’état HA.

Un journal ne doit pas enregistrer aveuglément chaque paquet sans étude de volumétrie. Une journalisation exhaustive peut saturer le stockage, augmenter la latence ou masquer les incidents importants dans le bruit. Définissez des règles de log cohérentes, un taux d’échantillonnage lorsque cela est approprié, des seuils d’alerte et une politique de rétention. Les refus répétés provenant d’une source inconnue peuvent être agrégés ; les événements de changement administratif doivent conserver une traçabilité détaillée.

La synchronisation horaire est indispensable aux corrélations. Les sources doivent utiliser une référence de temps fiable et être surveillées en cas de dérive. Les événements exportés vers le SIEM doivent conserver l’identifiant stable de l’équipement, l’interface ou le contexte virtuel, le fuseau horaire ou l’horodatage normalisé, l’identifiant de règle et un schéma de champs cohérent. Les secrets, données personnelles et charges applicatives sensibles ne doivent pas être collectés inutilement.

### 1.15 Automatisation, API et infrastructure as code

Une politique conçue manuellement peut être transformée en changements déclaratifs, contrôlés par revue de code et tests. L’automatisation réduit les erreurs répétitives mais accélère aussi les erreurs systématiques. Un pipeline prudent comprend un inventaire de l’état actuel, la validation de syntaxe, le contrôle des références d’objets, l’analyse des différences (*diff*), la détection de règles trop larges ou redondantes, des tests automatisés, une approbation, un déploiement progressif et une vérification post-changement.

Les secrets d’API doivent être stockés dans un gestionnaire de secrets, et non dans des dépôts Git ou des fichiers de variables en clair. Utilisez des comptes de service à privilèges minimaux, des jetons à durée limitée lorsque c’est possible, des restrictions de réseau et une journalisation des appels. La séparation des environnements laboratoire, préproduction et production limite l’impact d’une erreur. Les sauvegardes de configuration doivent être chiffrées, testées et accompagnées d’une procédure de restauration.

La validation automatisée peut rechercher les motifs dangereux : source `any` vers destination `any`, service `any`, règles temporaires non expirées, absence de propriétaire, journalisation absente sur un flux critique, règle masquée par une règle précédente, objet non référencé ou exception IPS trop large. Ces contrôles ne remplacent pas l’analyse métier ; ils repèrent les erreurs que l’outillage peut définir objectivement.

### 1.16 Gouvernance des règles et réduction de la surface d’attaque

La base de règles évolue généralement par ajouts successifs. Sans revue périodique, elle accumule les doublons, les objets obsolètes, les exceptions provisoires et les règles dont le besoin n’est plus connu. Une règle inutilisée n’est pas automatiquement inutile : certains processus sont saisonniers, rares ou activés lors de reprises après sinistre. Les compteurs d’usage doivent donc être analysés sur une période représentative et avec les propriétaires d’application.

Une bonne règle répond à une demande traçable, a un propriétaire, un motif commercial, un périmètre précis et une stratégie de revue. Les règles temporaires comportent une date d’expiration et un processus de renouvellement. Les modifications sont enregistrées dans un journal de changement, avec auteur, ticket, approbateur, comparaison avant/après, tests attendus et plan de retour arrière.

La réduction des règles ne consiste pas à fusionner toutes les autorisations similaires. Une agrégation peut élargir la portée réelle. Par exemple, réunir dix sous-réseaux d’utilisateurs dans un seul super-réseau peut autoriser des segments qui n’étaient pas concernés. Toute optimisation doit être accompagnée d’une comparaison sémantique : les flux autorisés avant et après sont-ils exactement les mêmes ?

### 1.17 Menaces courantes et limites de la défense périmétrique

Un pare-feu n’élimine pas à lui seul les menaces liées aux identifiants volés, aux terminaux compromis, aux applications vulnérables, aux erreurs d’administration ou aux abus internes. Un flux HTTPS légitime peut transporter une activité malveillante si les identifiants sont valides et si la détection applicative ne reconnaît pas le comportement. Un attaquant peut aussi passer par des services cloud autorisés, DNS chiffré ou des outils d’administration à distance.

La stratégie doit superposer les contrôles : gestion des identités et authentification forte, segmentation, protection des terminaux, correctifs, sauvegardes isolées, filtrage DNS, inspection adaptée, surveillance centralisée et réponse à incident. Les politiques egress sont particulièrement importantes : limiter les sorties aux services requis réduit l’utilisation de canaux de commande et de contrôle, sans prétendre rendre impossible toute communication malveillante.

Un filtrage egress ne devrait pas se limiter à « autoriser tout HTTPS ». Selon le risque, l’organisation peut restreindre les destinations, appliquer un proxy explicite, contrôler les applications, imposer une résolution DNS approuvée et alerter sur les connexions inhabituelles. Ces mesures peuvent être complexes dans des environnements modernes utilisant des CDN, des services cloud dynamiques ou des applications mobiles ; elles doivent être conçues avec des tests de compatibilité.

### 1.18 Méthode d’analyse d’un flux de bout en bout

Pour un flux qui ne fonctionne pas, collectez un tuple précis : source, destination, protocole, ports, heure, interface ou zone de départ, application attendue, identité et résultat observé. Confirmez d’abord que les adresses sont correctes, puis examinez la route aller et la route retour, le NAT, la règle correspondante, la session, les profils d’inspection et enfin l’application. Cette méthode évite de modifier des règles au hasard.

Pour un flux autorisé mais dangereux, posez les questions inverses : pourquoi existe-t-il ? Quelle règle le permet ? L’identité ou l’application a-t-elle été identifiée correctement ? Existe-t-il une route alternative, un VPN ou une interface non couverte ? Le trafic IPv6 est-il soumis aux mêmes exigences ? Les journaux montrent-ils le même chemin que la topologie théorique ? L’accès d’administration est-il séparé ?

```text
1. Définir précisément le flux attendu
2. Vérifier interface, zone et route aller
3. Vérifier NAT et tuple avant/après traduction
4. Identifier la règle réellement correspondante
5. Vérifier session et route retour
6. Examiner IPS, application, TLS et autres profils
7. Corréler journaux, compteurs et captures autorisées
8. Corriger la cause, rejouer les tests, documenter le résultat
```

La collecte doit respecter les règles de confidentialité. Évitez de capturer le contenu de communications sans autorisation. Les captures peuvent contenir des identifiants, des jetons, des données métier ou des informations personnelles. Préférez les métadonnées nécessaires, limitez la durée de conservation et protégez les fichiers d’analyse.


## 2. Configuration et pratique

### 2.1 Principes de laboratoire avant production

Les exemples suivants servent à comprendre les mécanismes, et non à copier une configuration sans adaptation. Les commandes Cisco IOS ou IOS XE diffèrent selon la plate-forme, le rôle de l’équipement, le logiciel et les licences. Les pare-feu dédiés Cisco Secure Firewall, ASA, les produits d’autres constructeurs et les pare-feu cloud possèdent leurs propres moteurs de politique. Une ACL de routeur n’équivaut pas à une politique NGFW applicative.

Avant chaque expérience, préparez un diagramme, un tableau des flux, les adresses utilisées, le résultat attendu, une méthode de mesure et un plan de retour arrière. Conservez une session d’administration secondaire ou un accès console hors bande pour éviter de vous enfermer hors de l’équipement. Ne testez jamais un refus de trafic d’administration à distance sans accès de secours vérifié.

Exemple de laboratoire :

| Élément | Réseau ou adresse | Rôle |
|---|---|---|
| Client interne | `192.168.10.10/24` | Génère des requêtes de test |
| Passerelle interne | `192.168.10.1` | Routeur ou interface de pare-feu |
| Serveur Web en DMZ | `192.168.20.10/24` | Service HTTPS de test |
| Interface DMZ | `192.168.20.1` | Passerelle de la DMZ |
| Réseau de gestion | `192.168.99.0/24` | Administration limitée |
| Poste d’administration | `192.168.99.10` | SSH et supervision |

Les adresses sont réservées à un laboratoire isolé. Adaptez-les aux segments réellement disponibles. N’utilisez pas d’adresses publiques ou d’identifiants réels pour ces exercices.

### 2.2 Sauvegarde et collecte de l’état initial

Sur un routeur Cisco IOS/IOS XE utilisé comme filtre de laboratoire, commencez par collecter l’état :

```text
enable
terminal length 0
show running-config
show ip interface brief
show ip route
show access-lists
show logging
show users
show version
```

Les commandes disponibles dépendent de la version. Sauvegardez la configuration selon la procédure locale et vérifiez que la sauvegarde peut être lue et restaurée. Une copie non testée n’est pas une garantie de récupération. Notez les compteurs initiaux des ACL afin de différencier les tests et les flux de fond.

### 2.3 ACL étendue : autoriser seulement HTTPS vers la DMZ

Une ACL de routeur peut limiter l’accès vers le serveur Web. Dans cet exemple pédagogique, l’interface et le sens d’application doivent être adaptés à la topologie :

```text
ip access-list extended DMZ-IN
 remark HTTPS autorise depuis le reseau client de test
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 remark ICMP restreint pour tests de diagnostic si requis
 permit icmp 192.168.10.0 0.0.0.255 host 192.168.20.10 echo
 remark Refus explicite des autres flux vers le serveur publie
 deny ip any host 192.168.20.10 log
 remark Ne pas oublier les autres flux necessaires a l'architecture
 permit ip any any
!
interface GigabitEthernet0/1
 description Vers-reseau-DMZ
 ip access-group DMZ-IN out
```

Cette configuration illustre la syntaxe, mais comporte un choix important : `permit ip any any` laisse passer les autres flux non ciblés par la liste. Dans une politique de production, il faut définir ce qui doit être autorisé sur l’interface entière ; la dernière règle ne doit pas être ajoutée mécaniquement. Une ACL appliquée en sortie de l’interface DMZ ne traite que les paquets qui sortent par cette interface. Vérifiez la route réelle et les conséquences de la règle `deny` pour le trafic légitime.

Le serveur peut également nécessiter des flux d’administration depuis le réseau de gestion, des contrôles de santé, DNS, NTP ou supervision. Plutôt que d’ouvrir ces services à tous, ajoutez des autorisations ciblées avant le refus concerné. Les compteurs et les journaux doivent confirmer quelle ACE a correspondu.

> **Astuce :** après chaque modification d’ACL, testez une connexion autorisée, une connexion interdite, un flux légitime non directement visé et un chemin de gestion. Le test des seuls cas « attendus » ne révèle pas les blocages collatéraux.

### 2.4 Wildcard masks et vérification du périmètre

Cisco IOS emploie souvent des masques génériques dans les ACL. Un wildcard `0.0.0.255` correspond à un masque réseau `/24` dans le cas courant, car les huit derniers bits ne sont pas comparés. Un wildcard `0.0.0.0` correspond à une adresse unique. Une erreur sur un seul octet peut élargir fortement la portée de la règle.

| Réseau | Préfixe | Wildcard Cisco courante |
|---|---:|---|
| `192.168.10.0` | `/24` | `0.0.0.255` |
| `192.168.10.0` | `/25` | `0.0.0.127` |
| `10.20.0.0` | `/16` | `0.0.255.255` |
| Hôte `192.168.10.10` | `/32` | `0.0.0.0` ou mot-clé `host` |

Vérifiez les plages avec un calcul indépendant avant la mise en production. Les ACL non contiguës ou les wildcards non conventionnels sont difficiles à relire et doivent être évités sauf besoin documenté.

### 2.5 Limiter l’accès SSH d’administration

L’accès de gestion doit être isolé des réseaux utilisateurs et limité aux sources autorisées. Exemple Cisco IOS :

```text
ip access-list standard MGMT-SSH-SOURCES
 permit 192.168.99.10
 deny any log
!
line vty 0 4
 access-class MGMT-SSH-SOURCES in
 transport input ssh
 login local
```

Cette configuration ne remplace pas une stratégie de comptes robustes, une authentification centralisée, MFA lorsque disponible, la protection de la console ni la journalisation. Certains équipements n’acceptent pas toutes les options exactement sous cette forme. Avant de l’appliquer à distance, vérifiez le chemin de gestion et gardez un accès hors bande fonctionnel.

Évitez Telnet pour la gestion, car les informations circulent sans chiffrement. Désactivez les services non utilisés et limitez les privilèges. Une ACL sur les lignes VTY contrôle les sources IP mais n’apporte pas à elle seule une authentification forte.

### 2.6 Démonstration du fonctionnement stateful

Dans un laboratoire, créez une session TCP depuis le client vers un service autorisé, observez son établissement, puis observez les paquets de retour. Sur une plate-forme qui expose la table d’état, recherchez la session avec les commandes adaptées à la version. Selon le produit Cisco, les commandes de diagnostic peuvent inclure `show conn`, `show conn detail`, des commandes de suivi de session ou des commandes spécifiques au moteur utilisé.

Le but est d’identifier le tuple avant traduction, le tuple après traduction si NAT est actif, l’interface d’entrée, l’interface de sortie, l’état TCP et les compteurs. Comparez cette observation à une connexion vers un service non autorisé. Le comportement attendu est que la session interdite n’obtienne pas un état autorisé, et qu’un journal de refus soit généré si le logging a été configuré.

N’utilisez pas le simple ping comme preuve que toutes les couches fonctionnent. ICMP peut être filtré indépendamment de TCP, et une connexion HTTPS peut échouer au niveau TLS ou applicatif même si TCP s’établit. Utilisez des outils adaptés : `ping`, `traceroute`/`tracert`, `nslookup` ou `dig`, `curl`, `nc`/`Test-NetConnection`, navigateur, journaux et capture de paquets autorisée.

### 2.7 Exemple conceptuel de politique NGFW en zones

Dans un NGFW, une règle peut porter sur la zone source, la zone destination, les objets, l’utilisateur, l’application, le service, l’action, les profils de sécurité et le logging. La logique attendue pour un portail public pourrait se résumer ainsi :

| Priorité logique | Source | Destination | Application/service | Action | Profils |
|---|---|---|---|---|---|
| 1 | Internet | DMZ-Web | HTTPS/portail approuvé | Autoriser | IPS, réputation, logs |
| 2 | Internet | DMZ-Web | Toute autre application | Refuser | Journaliser selon politique |
| 3 | Admin-VPN | Équipements gérés | SSH/HTTPS de gestion | Autoriser ciblé | MFA/identité, logs |
| 4 | Utilisateurs | Zone données | Accès direct non requis | Refuser | Logs adaptés |
| 5 | Applications | Zone données | Port DB spécifié | Autoriser ciblé | IPS, logs |

Il s’agit d’un modèle, pas d’une syntaxe importable. Certaines solutions exécutent les règles de déchiffrement séparément des règles de sécurité ; d’autres déterminent d’abord le NAT ou le routage. Il faut reproduire ces intentions dans le moteur du produit, puis vérifier les règles compilées et les journaux de décision.

### 2.8 Publication sécurisée d’un service dans une DMZ

Pour publier un serveur, il faut distinguer la traduction d’adresse, la politique de sécurité et la protection applicative. Un schéma courant comporte un reverse proxy ou un répartiteur en DMZ qui accepte HTTPS puis transmet à un serveur applicatif sur un port et une destination précis. La base de données n’accepte que le flux issu de l’application. L’administration est effectuée par un chemin séparé.

```text
Internet
   |
[IP publique / DNAT]
   |
[NGFW : règle HTTPS + profils]
   |
[Reverse proxy DMZ : TCP/443]
   |
[Serveur applicatif : port nécessaire]
   |
[Base de données : port DB depuis application seulement]

Gestion : bastion ---> interfaces d'administration autorisées
```

Une publication ne devrait pas permettre au serveur DMZ d’initier librement des connexions vers l’ensemble du réseau interne. Définissez aussi les sorties nécessaires aux mises à jour, DNS, NTP et supervision, avec des destinations et services explicites. Prévoyez des limites de connexion, protections contre les abus et alertes, sans faire du pare-feu un substitut aux contrôles de sécurité de l’application.

### 2.9 Journalisation et analyse des règles

Configurez des journaux pour les décisions importantes, les refus pertinents, les alertes IPS, les changements administratifs et les transitions HA. N’activez pas une journalisation exhaustive sans évaluer le volume, le coût de stockage et l’impact sur les performances. Un événement doit être interprétable : horodatage fiable, identifiant du dispositif, règle, zones, tuple, action et raison lorsque ces champs sont disponibles.

Sur Cisco IOS, `show access-lists` peut permettre d’observer les compteurs d’ACE ; les options et le niveau de détail varient. Sur un NGFW, utilisez les journaux de trafic, les logs de menace, les logs système et la recherche de session. Filtrez par source, destination, port, période et règle. La présence d’un journal de refus confirme qu’un paquet a été vu par ce point de contrôle, mais n’établit pas à elle seule le chemin complet du trafic.

### 2.10 Méthode de changement contrôlé

Chaque changement doit comprendre :

1. l’objectif et le propriétaire du flux ;
2. les sources, destinations et services exacts ;
3. les zones et équipements concernés ;
4. la règle proposée et sa position ;
5. la durée de validité si l’ouverture est temporaire ;
6. les tests positifs et négatifs ;
7. le plan de retour arrière ;
8. les éléments de preuve après changement.

Appliquez d’abord en laboratoire ou en préproduction. En production, limitez le périmètre du changement, utilisez une fenêtre adaptée et gardez un accès de secours. Après déploiement, confirmez que l’application fonctionne, que le trafic interdit est toujours bloqué, que les journaux sont présents et qu’aucun service collatéral n’a été interrompu.

### 2.11 Exercices pratiques

**Exercice A — Port HTTPS uniquement.** Le client `192.168.10.10` doit atteindre `192.168.20.10` en TCP/443, mais pas en TCP/22. Configurez une ACL de laboratoire, vérifiez les compteurs, puis expliquez ce que votre règle laisse passer pour les autres destinations.

**Exercice B — Gestion séparée.** Seul `192.168.99.10` doit ouvrir une session SSH d’administration. Vérifiez la règle de filtrage des sources, le mécanisme d’authentification et la procédure de secours si l’ACL est incorrecte.

**Exercice C — Échec intermittent.** Une application fonctionne depuis un sous-réseau, mais échoue depuis un autre. Comparez la route aller, le NAT, les zones, la règle correspondante, le profil de sécurité et le chemin retour. N’élargissez pas l’autorisation avant d’avoir identifié la différence.

**Exercice D — Session persistante.** Après la modification d’une règle, un flux déjà établi continue de fonctionner. Déterminez si le moteur conserve la décision jusqu’à expiration de la session. Expliquez comment effectuer une réévaluation contrôlée sans fermer des sessions de production de manière imprévisible.

**Exercice E — Visibilité TLS.** Un tableau de bord affiche beaucoup de trafic HTTPS mais très peu de sessions déchiffrées. Distinguez la classification de métadonnées, le déchiffrement réel et les exceptions. Proposez des indicateurs permettant de mesurer la couverture d’inspection sans collecter de contenu inutile.


## 3. Dépannage et sécurité

### 3.1 Symptôme : une connexion autorisée échoue

Ne commencez pas par créer une règle `permit any`. Établissez le résultat précis attendu et le point de test. Vérifiez ensuite les éléments suivants :

- L’adresse source réelle correspond-elle à ce qui est inscrit dans la demande ? Un NAT côté client ou un VPN peut modifier l’adresse visible.
- La destination résout-elle vers l’adresse attendue ? Le DNS peut renvoyer une IP différente ou une adresse IPv6 non couverte par la politique.
- Le paquet entre-t-il dans l’interface et la zone prévues ? Un chemin de routage alternatif peut contourner le pare-feu attendu.
- Quelle route le dispositif choisit-il ? Existe-t-il une route plus spécifique, une PBR ou un tunnel ?
- Quelle règle correspond réellement ? Examinez l’identifiant et les compteurs plutôt que de supposer que la règle visible est utilisée.
- Une règle NAT s’applique-t-elle ? Comparez les tuples avant et après translation.
- Le retour emprunte-t-il le même chemin ? Cherchez l’asymétrie et la synchronisation d’état.
- Une inspection IPS, TLS ou applicative bloque-t-elle après l’autorisation réseau ? Examinez le journal de menace ou le verdict de déchiffrement.
- La connexion atteint-elle le serveur ? Confirmez l’écoute du service, le pare-feu local de l’hôte et les journaux applicatifs.

Le résultat de chaque étape doit être consigné. Si la capture sur l’interface d’entrée montre le paquet, mais que la sortie ne le montre pas, le problème se trouve probablement dans une étape de traitement du pare-feu ou dans son choix de route. Si le paquet sort du pare-feu mais n’atteint pas le serveur, étendez l’analyse au chemin suivant.

### 3.2 Symptôme : une connexion interdite fonctionne

Une connexion interdite qui réussit constitue un problème plus grave qu’un simple blocage légitime. Vérifiez d’abord que le test emploie les bons endpoints, ports et familles IP. Ensuite, identifiez toutes les interfaces et tous les chemins possibles : Wi-Fi invité, second lien WAN, VPN, routage interne, IPv6, proxy explicite, tunnel ou connexion initiée depuis le réseau de destination.

Examinez les règles plus générales situées avant la règle de refus, les règles partagées à plusieurs zones, les objets imbriqués, les groupes dynamiques, les exceptions temporaires et les flux appartenant à une session déjà établie. Une politique modifiée peut ne pas réévaluer les sessions existantes. Vérifiez également si le trafic passe réellement par l’équipement que vous analysez.

Ne concluez pas à un contournement de sécurité avant d’avoir éliminé une erreur de mesure, mais traitez le cas comme un incident potentiel. Capturez les preuves nécessaires, limitez le périmètre d’accès de façon sûre et documentez toute action de confinement. Une règle de blocage supplémentaire peut être appropriée comme mesure temporaire, mais le problème de chemin ou de politique sous-jacent doit être corrigé.

### 3.3 Lire les compteurs et les journaux avec prudence

Les compteurs d’ACL peuvent inclure du trafic de fond et ne permettent pas toujours d’attribuer une décision à une application particulière. Un compteur qui augmente démontre qu’au moins un paquet correspond à l’entrée concernée, pas forcément qu’une session complète s’est établie. Les logs peuvent être échantillonnés, limités par un seuil, envoyés de façon asynchrone ou affectés par une panne du collecteur.

Comparez plusieurs sources : journaux de sécurité, table de sessions, statistiques d’interface, captures sur plusieurs points et logs du serveur. Normalisez les horodatages. Tenez compte de la différence entre heure locale, UTC et fuseau d’affichage. Une dérive NTP peut donner l’impression que les événements sont dans le mauvais ordre.

### 3.4 Distinguer routage, pare-feu et application

Un ping qui échoue ne signifie pas automatiquement que le pare-feu bloque le flux applicatif. ICMP peut être refusé alors que TCP/443 passe, ou le serveur peut ne pas répondre aux requêtes echo. De la même manière, une connexion TCP établie n’atteste pas que TLS, l’authentification ou la requête HTTP fonctionnent.

Utilisez des tests par couche : résolution DNS, reachability IP selon les politiques autorisées, établissement TCP vers le port exact, négociation TLS, réponse HTTP et enfin transaction métier. Chaque test a ses limites. `traceroute` peut être incomplet lorsque les messages ICMP sont filtrés ; il fournit une indication de chemin, pas une carte exhaustive. Les captures doivent être analysées en considérant les retransmissions, le MSS, la MTU, les segments et les mécanismes de chiffrement.

### 3.5 MTU, MSS et fragmentation

Une session peut s’établir puis se bloquer lorsque des paquets plus volumineux sont envoyés. Les tunnels VPN, encapsulations, liens PPPoE et chemins hétérogènes réduisent parfois la MTU utile. Si les messages ICMP nécessaires à la découverte MTU sont bloqués, certains flux peuvent échouer sans qu’un simple test de petit paquet ne le révèle.

Diagnostiquez ce scénario en comparant les tailles de paquets, les retransmissions et les réponses ICMP nécessaires, sans désactiver aveuglément les protections. Sur TCP, un ajustement MSS peut être un contournement adapté dans une architecture connue, mais il doit être justifié par les caractéristiques du chemin et validé sur les flux concernés. En IPv6, la découverte MTU du chemin repose sur ICMPv6 ; son blocage intégral est particulièrement risqué.

### 3.6 Déchiffrement TLS : erreurs et exceptions

Les erreurs TLS peuvent venir d’un certificat expiré, d’une chaîne de confiance incorrecte, d’un nom de serveur discordant, d’une application utilisant l’épinglage de certificat, d’un protocole non supporté ou d’une incompatibilité de version. Déterminez si le pare-feu bloque le flux, échoue à le déchiffrer ou le transmet sans inspection. Ces résultats n’ont pas la même signification.

Avant de créer une exception, identifiez l’application, le groupe d’utilisateurs, la destination, l’empreinte de l’événement et la raison de l’échec. Limitez l’exemption au minimum nécessaire et consignez le risque accepté. Ne désactivez pas le déchiffrement à l’échelle globale pour résoudre un problème isolé.

### 3.7 IPS : faux positifs et faux négatifs

Un faux positif survient lorsque le moteur identifie à tort une activité malveillante ; un faux négatif lorsqu’une activité malveillante n’est pas détectée. Le taux dépend du contexte, des signatures, du chiffrement, de la normalisation, de la version du logiciel et des techniques adverses. Aucun moteur ne fournit une garantie d’identification totale.

Pour enquêter, collectez l’identifiant de la signature, la sévérité, la version du moteur, le tuple, l’application identifiée, le sens du flux et la réponse du dispositif. Comparez le comportement avec la documentation du fournisseur. Si une exception est nécessaire, créez-la avec un scope minimal et une date de révision. Gardez les protections à forte confiance actives lorsque cela est possible et appliquez des tests de régression après la modification.

### 3.8 HA : split-brain et instabilité de basculement

Un problème HA peut apparaître comme un problème de session ou de routage. Recherchez les événements de changement de rôle, pertes de heartbeat, alarmes d’interface, erreurs de synchronisation, différences de configuration et divergences de version. Le split-brain — lorsque plusieurs membres se comportent comme actifs sans coordination correcte — peut entraîner des conflits d’adresse ou des chemins incohérents.

Le mécanisme de détection et d’arbitrage doit être conçu avec soin, notamment lorsque le lien de synchronisation traverse un commutateur partagé ou un réseau soumis à congestion. Les tests doivent inclure les pannes partielles, pas seulement l’arrêt complet d’un appareil. Ne forcez pas un retour de rôle en production sans comprendre les critères du cluster et l’impact sur les sessions.

### 3.9 Sécuriser le plan de gestion

Le plan de gestion doit être séparé du plan de données autant que possible. Utilisez un réseau d’administration dédié, un bastion, des comptes individuels, une authentification forte, des rôles à privilèges minimaux et une journalisation centralisée. Autorisez la gestion seulement depuis les sources qui en ont besoin. Supprimez les comptes et clés inutilisés et protégez les mécanismes de récupération.

L’accès d’urgence est nécessaire, mais ne doit pas devenir un compte partagé permanent dont les actions sont impossibles à attribuer. Protégez les sauvegardes, les clés, les certificats et les secrets d’API. Les consoles hors bande, ports série et réseaux d’administration doivent eux aussi être protégés physiquement et logiquement.

### 3.10 Réponse à incident impliquant un pare-feu

En présence d’un trafic suspect, définissez l’objectif immédiat : confirmer l’activité, limiter la propagation, protéger les preuves ou maintenir une fonction critique. Collectez le tuple, la fenêtre temporelle, la règle, la session, les logs de menace et les événements de gestion. Ne supprimez pas immédiatement toutes les traces et ne redémarrez pas l’équipement sans évaluer la perte de preuves et l’impact sur l’activité.

Le confinement peut comprendre le blocage d’une destination, la restriction d’un service, la suspension d’un compte, la segmentation d’un terminal ou le passage d’une règle d’alerte en blocage. Toute mesure doit être autorisée, documentée et évaluée au regard des effets de bord. La remédiation peut exiger une investigation des terminaux, identifiants, applications ou services cloud ; le pare-feu seul ne permet pas d’établir l’étendue complète d’une compromission.

Après l’incident, examinez la cause racine, le temps de détection, les règles qui ont permis ou limité le flux, la qualité des logs et les lacunes d’architecture. Convertissez les constats en tâches datées, avec un responsable et un test de vérification.

### 3.11 Liste de contrôle avant production

- Les zones reflètent-elles des exigences de confiance cohérentes ?
- Les flux nécessaires sont-ils documentés avec un propriétaire ?
- Les règles interdisent-elles par défaut les flux non requis ?
- Les règles les plus spécifiques précèdent-elles les règles générales correspondantes ?
- Les objets ont-ils des noms explicites et des périmètres vérifiés ?
- Le NAT et le routage aller/retour ont-ils été testés ?
- Les politiques IPv4 et IPv6 sont-elles cohérentes ?
- Les profils IPS, application, URL et TLS sont-ils activés comme prévu ?
- Les exceptions ont-elles une justification, une portée minimale et une date de revue ?
- L’administration est-elle séparée, authentifiée fortement et journalisée ?
- Les événements critiques arrivent-ils au collecteur avec une heure correcte ?
- Le cluster a-t-il été testé en perte de nœud, de lien et de synchronisation ?
- Le débit a-t-il été mesuré avec les fonctions d’inspection réellement utilisées ?
- Le plan de retour arrière et la sauvegarde ont-ils été vérifiés ?
- Les tests positifs, négatifs et de non-régression ont-ils été exécutés ?

> **Danger :** une règle de test large laissée en production, une interface de gestion exposée ou une exception TLS/IPS globale peut annuler les bénéfices du reste de la politique. Traitez chaque exception comme une modification de sécurité, avec une portée mesurée, un responsable et une révision planifiée.


## Points à retenir

1. Un pare-feu stateless filtre des paquets sans contexte complet de session ; un pare-feu stateful suit les flux ; un NGFW peut ajouter l’identification applicative, l’IPS, le contrôle d’identité et l’inspection TLS.
2. L’ordre effectif du traitement dépend du produit : routage, NAT, politique, état et inspection doivent être vérifiés sur la plate-forme réelle.
3. La sécurité doit se concevoir par zones et par flux métier, en incluant les chemins nord-sud, est-ouest, de gestion, VPN et IPv6.
4. Une autorisation réseau ne garantit pas que l’application est autorisée ; les profils de sécurité peuvent intervenir à des phases distinctes.
5. Le déchiffrement TLS apporte de la visibilité mais crée des obligations de performance, de gestion de certificats, de confidentialité et de compatibilité.
6. Une haute disponibilité correcte requiert une convergence testée, un routage cohérent et une synchronisation d’état appropriée ; elle ne se résume pas à deux boîtiers.
7. Les règles doivent être minimales, explicables, journalisées selon le besoin, rattachées à un propriétaire et révisées périodiquement.
8. Le diagnostic doit suivre une méthode reproductible : tuple, route, NAT, règle, session, profil de sécurité, retour et application.
9. Les chiffres commerciaux de débit doivent être vérifiés avec les fonctions d’inspection et les charges réellement utilisées.
10. La protection du pare-feu lui-même — gestion, secrets, mises à jour, sauvegardes, accès d’urgence et journaux — est une composante essentielle de la défense.

## Références techniques

- Cisco, documentation de configuration IOS/IOS XE : listes de contrôle d’accès IPv4/IPv6, Zone-Based Policy Firewall, NAT, routage, journalisation et sécurisation de l’accès d’administration. Vérifier la documentation correspondant à la version déployée.
- Cisco Secure Firewall et Cisco ASA : guides de configuration, guides de migration, matrice de fonctionnalités et notes de version adaptés à la génération du matériel et au logiciel.
- NIST SP 800-41 Rev. 1, *Guidelines on Firewalls and Firewall Policy* : architecture, politique et considérations de déploiement des pare-feu.
- NIST SP 800-207, *Zero Trust Architecture* : principes de contrôle d’accès, segmentation et absence de confiance implicite fondée uniquement sur la localisation réseau.
- NIST SP 800-53, *Security and Privacy Controls for Information Systems and Organizations* : contrôle des accès, audit, configuration, protection des communications et supervision.
- NIST SP 800-61 Rev. 2, *Computer Security Incident Handling Guide* : principes de préparation, détection, confinement et retour d’expérience en réponse à incident.
- RFC 791 et RFC 8200 : IPv4 et IPv6 ; RFC 4443 et RFC 4861 : ICMPv6 et découverte de voisins ; RFC 8446 : TLS 1.3.
- IETF RFC 1918 : allocation d’adresses IPv4 privées ; RFC 4632 : routage CIDR ; RFC 3022 : traduction traditionnelle d’adresses réseau IPv4.
- CIS Critical Security Controls : principes de gestion des actifs, configuration sécurisée, contrôle des accès et journalisation.
- Documentation du fournisseur concernant la couverture de signatures IPS, les capacités d’inspection TLS, les mécanismes de haute disponibilité, la compilation des politiques et les limites de performance.

Les standards et guides évoluent. Avant toute mise en production, vérifiez les versions récentes des références, les notes de version constructeur, les avis de sécurité et les recommandations applicables à votre contexte réglementaire et opérationnel.


*Fin du cours — Pare-feu & NGFW, niveau Expert.*
