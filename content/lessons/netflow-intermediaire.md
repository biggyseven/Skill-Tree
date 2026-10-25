# IP SLA & NetFlow — Niveau Intermédiaire

**Fichier :** `netflow-intermediaire.md`  
**Parcours :** Réseaux Cisco — Niveau intermédiaire  
**Prérequis :** cours `netflow-debutant.md`, adressage IPv4, routage, ACL, interfaces Cisco IOS/IOS XE et commandes `show` de base.  
**Environnement :** principalement Cisco IOS XE avec Flexible NetFlow. Certaines commandes, options de cache, champs disponibles, formats d’export et fonctions IP SLA varient selon la plateforme, la version et la licence. Les exemples sont des modèles à valider en laboratoire avant production.

> **Objectif du niveau intermédiaire** — Concevoir un enregistrement de flux répondant à une question opérationnelle, déployer Flexible NetFlow de façon cohérente, comprendre l’export v9/IPFIX, interpréter les compteurs sans double comptage, et exploiter IP SLA au-delà d’une simple sonde ICMP. Le cours approfondit le niveau débutant au lieu de reprendre toute son introduction.

## Plan

1. Positionner le niveau intermédiaire
2. Concevoir un record utile : `match` et `collect`
3. Construire une chaîne Flexible NetFlow complète
4. Choisir interface et direction : éviter les biais d’observation
5. Comprendre cache, expirations et flux de longue durée
6. Export NetFlow v9 et IPFIX : templates, transport et collecteur
7. Échantillonnage, précision et dimensionnement
8. Lire les statistiques et expliquer les top talkers
9. IP SLA intermédiaire : qualité, seuils et notifications
10. Corréler IP SLA, NetFlow et compteurs d’interface
11. Laboratoire guidé de bout en bout
12. Dépannage systématique
13. Exercices corrigés, quiz et fiche de référence
14. Sources et précautions de compatibilité


## 1. Positionner le niveau intermédiaire

Au niveau débutant, on a établi la différence fondamentale : IP SLA produit des mesures actives vers une cible choisie ; NetFlow décrit les conversations vues par un équipement. Le niveau intermédiaire consiste à passer de « j’ai activé une fonction » à « j’ai une mesure fiable qui répond à une question précise ».

Par exemple, « connaître le trafic » est trop vague. Des questions exploitables sont :

- Quels sous-réseaux utilisent le plus de bande passante sur le lien WAN durant les heures de pointe ?
- Quel service ou protocole explique l’augmentation des octets sortants ?
- Le délai vers une cible augmente-t-il au même moment que les compteurs d’interface et les volumes de certains flux ?
- La collecte est-elle incomplète à cause de la configuration, du réseau de transport, des templates ou du collecteur ?
- Les sondes IP SLA mesurent-elles réellement le chemin que l’on souhaite surveiller ?

Il faut séparer quatre plans : **trafic utilisateur**, **mesure**, **export**, **analyse**. Un routeur peut acheminer les paquets correctement tout en exportant mal les flux. Inversement, un collecteur vide ne prouve pas que le trafic utilisateur est interrompu.

**Schéma 1 — Chaîne de traitement Flexible NetFlow**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" width="960" height="390" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Chaîne de traitement Flexible NetFlow</text><rect x="32" y="80" width="188" height="112" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="126" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">1 · Paquets</text><text x="126" y="135" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Entrée / sortie</text><text x="126" y="160" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Interface observée</text><rect x="260" y="80" width="188" height="112" rx="12" fill="#1b2b3a" stroke="#60a5fa" stroke-width="2"/><text x="354" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">2 · Record</text><text x="354" y="135" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Clés + champs</text><text x="354" y="160" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Définit le flux</text><rect x="488" y="80" width="188" height="112" rx="12" fill="#243024" stroke="#4ade80" stroke-width="2"/><text x="582" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">3 · Cache</text><text x="582" y="135" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Compteurs agrégés</text><text x="582" y="160" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Durée · octets · paquets</text><rect x="716" y="80" width="212" height="112" rx="12" fill="#30251d" stroke="#fbbf24" stroke-width="2"/><text x="822" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">4 · Export / collecte</text><text x="822" y="135" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">NetFlow v9 / IPFIX</text><text x="822" y="160" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Collecteur → analyse</text><path d="M220 136 H250" stroke="#38bdf8" stroke-width="2.5"/><path d="M448 136 H478" stroke="#9fb5d0" stroke-width="2.5"/><path d="M676 136 H706" stroke="#9fb5d0" stroke-width="2.5"/><rect x="90" y="230" width="780" height="95" rx="12" fill="#101c2b" stroke="#334a66"/><text x="480" y="258" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">À retenir : les compteurs sont construits sur l’équipement exportateur</text><text x="480" y="284" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Le collecteur reçoit des enregistrements, pas nécessairement chaque paquet.</text><text x="480" y="306" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Une perte d’export n’implique pas forcément une perte de trafic utilisateur.</text></svg>

*Lecture du schéma : Des paquets observés sur une interface sont classés par un record, agrégés dans un cache, exportés puis analysés par un collecteur.*

### 1.1 Ce que NetFlow ne garantit pas

NetFlow n’est pas une capture complète de paquets. Dans le cas habituel, l’équipement construit des entrées de flux et exporte des statistiques. Il ne fournit donc pas automatiquement le contenu détaillé de chaque conversation, ni une preuve que l’application a répondu correctement. Les compteurs exportés peuvent également différer d’une mesure faite sur un autre point du réseau, particulièrement si l’on observe le trafic à plusieurs interfaces, utilise l’échantillonnage ou compare des périodes différentes.

IP SLA ne garantit pas non plus une expérience applicative parfaite. Une sonde ICMP peut réussir pendant qu’un serveur HTTP est en panne ; elle peut échouer si l’ICMP est filtré alors que l’application fonctionne. Le type de sonde et la cible doivent correspondre au besoin à mesurer.

### 1.2 Une fiche de mesure avant la configuration

Avant chaque déploiement, écris une fiche courte :

| Question | Exemple de choix | Pourquoi c’est important |
|---|---|---|
| Quel problème doit-on voir ? | Congestion WAN en sortie | Oriente les champs, l’interface et la fréquence d’analyse. |
| Où observer le trafic ? | Interface WAN, en sortie | Fixe le périmètre de mesure. |
| Quel niveau de détail ? | Sous-réseaux, protocole, ports | Des clés trop détaillées multiplient les entrées ; trop simples masquent la distinction. |
| Quels champs collecter ? | Octets, paquets, temps premier/dernier | Permet de calculer volumes et débits. |
| Où envoyer les données ? | Collecteur `192.0.2.200:2055/UDP` | Nécessite une route, une ACL et une configuration cohérente. |
| Quelle sonde de santé ? | IP SLA vers un service représentatif | Évite d’assimiler un ping à la disponibilité métier. |
| Quel résultat est acceptable ? | RTT stable et export reçu | Donne un critère de validation observable. |

## 2. Concevoir un record utile : `match` et `collect`

Un Flexible NetFlow record décrit **l’identité logique d’un flux** et **les informations à mesurer**. Dans une configuration personnalisée, les commandes `match` définissent les clés du flux ; les commandes `collect` ajoutent des compteurs et des champs d’information. Un record bien conçu répond à la question de départ sans créer inutilement des millions d’entrées.

**Schéma 2 — Un record sépare clés et mesures**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" width="960" height="390" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Un record sépare clés et mesures</text><rect x="35" y="75" width="400" height="252" rx="14" fill="#13263a" stroke="#38bdf8" stroke-width="2"/><text x="235" y="105" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">MATCH = identité de la clé</text><text x="65" y="142" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Adresse source</text><rect x="240" y="123" width="160" height="28" rx="6" fill="#1d3b55"/><text x="320" y="142" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#7dd3fc">10.10.1.20</text><text x="65" y="181" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Adresse destination</text><rect x="240" y="162" width="160" height="28" rx="6" fill="#1d3b55"/><text x="320" y="181" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#7dd3fc">10.20.1.80</text><text x="65" y="220" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Protocole / ports</text><rect x="240" y="201" width="160" height="28" rx="6" fill="#1d3b55"/><text x="320" y="220" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#7dd3fc">TCP · 51514 → 443</text><text x="235" y="285" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Les clés définissent les conversations distinctes.</text><rect x="525" y="75" width="400" height="252" rx="14" fill="#172b21" stroke="#4ade80" stroke-width="2"/><text x="725" y="105" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">COLLECT = mesures / contexte</text><text x="565" y="143" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Compteur octets</text><rect x="750" y="124" width="145" height="28" rx="6" fill="#244b32"/><text x="822" y="143" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#86efac">1 840 000</text><text x="565" y="182" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Compteur paquets</text><rect x="750" y="163" width="145" height="28" rx="6" fill="#244b32"/><text x="822" y="182" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#86efac">1 240</text><text x="565" y="221" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Temps premier / dernier</text><rect x="750" y="202" width="145" height="28" rx="6" fill="#244b32"/><text x="822" y="221" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#86efac">Horodatages</text><text x="725" y="285" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Les champs collectés décrivent le flux sans le redéfinir.</text><text x="480" y="362" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Un champ utile pour l’analyse n’est pas toujours une clé : limiter les clés évite de fragmenter excessivement le cache.</text></svg>

*Lecture du schéma : La partie MATCH identifie les flux distincts ; la partie COLLECT collecte les compteurs ou informations utiles.*

### 2.1 Les clés : trouver le bon niveau d’agrégation

Un record IPv4 courant peut utiliser les adresses source et destination, le protocole et les ports de transport. Chaque combinaison distincte des clés peut devenir une entrée distincte dans le cache. Ajouter des clés signifie généralement plus de granularité, mais aussi davantage d’entrées et potentiellement davantage de consommation mémoire et CPU.

Trois profils illustrent le compromis :

| Profil | Clés représentatives | Question à laquelle il répond | Limite |
|---|---|---|---|
| Agrégé par hôte | IP source, IP destination, protocole | Quels hôtes échangent le trafic ? | Les services TCP/UDP ne sont pas distingués par port. |
| Conversation applicative | IP source/destination, protocole, ports source/destination | Quelles conversations et quels ports sont actifs ? | Grand nombre d’entrées possibles, surtout sur un réseau très actif. |
| Analyse d’un segment | Conversation + interface d’entrée ou champs de contexte | Par quel point le trafic est-il observé ? | Les mêmes paquets peuvent apparaître dans plusieurs séries si l’observation est répétée. |

Il n’existe pas un record optimal universel. Un bilan de capacité peut nécessiter uniquement des adresses, des protocoles et des compteurs ; une enquête sur un service peut exiger les ports. Commence avec l’ensemble le plus simple qui répond à la question, puis ajoute des champs lorsque leur valeur opérationnelle est claire.

### 2.2 Les compteurs et horodatages

Les compteurs d’octets et de paquets permettent de comparer le volume d’un flux. Les timestamps de premier et dernier paquet permettent de comprendre la durée et d’estimer un débit moyen, si l’outil de collecte dispose de valeurs cohérentes et si la sémantique exacte des champs est connue. Attention : le compteur d’octets NetFlow est celui rapporté par l’exportateur ; il ne faut pas supposer sans vérification qu’il correspond exactement à tous les octets de couche 2 sur une interface physique.

Une estimation de débit moyen à partir des données d’un flux est :

\[
\text{débit moyen (bit/s)} \approx \frac{8 \times \text{octets observés}}{\text{durée en secondes}}
\]

**Exemple :** si un enregistrement contient 12 000 000 octets pendant 30 secondes, l’estimation moyenne est :

\[
\frac{8 \times 12\,000\,000}{30}=3\,200\,000\text{ bit/s}=3{,}2\text{ Mbit/s}
\]

Ce calcul n’est qu’une moyenne sur la période de l’enregistrement. Il ne montre pas les pointes instantanées. Pour évaluer une interface, compare aussi les compteurs d’interface et les intervalles de mesure alignés.

### 2.3 Champs de transport : précautions

Les ports source et destination s’appliquent aux protocoles qui utilisent les champs correspondants, comme TCP et UDP. Les autres protocoles IP n’ont pas les mêmes champs. En conséquence, les données d’un flux ICMP, d’un fragment IP ou de paquets atypiques peuvent ne pas contenir de valeur de port au sens attendu. Le comportement exact des champs dépend du type de record et de la plateforme.

### 2.4 Éviter le record « fourre-tout »

Un record qui contient toutes les clés disponibles peut surcharger le cache et complexifier l’analyse sans valeur supplémentaire. On doit pouvoir répondre à deux questions avant de créer un champ : « Quelle décision ce champ m’aidera-t-il à prendre ? » et « Quel est le coût de l’ajouter à la clé ou à la collecte ? » Les champs `collect` ne sont pas interchangeables avec les clés `match` : collecter un compteur ne crée pas une nouvelle classe de flux, tandis qu’ajouter une clé peut fractionner les conversations en entrées séparées.

## 3. Construire une chaîne Flexible NetFlow complète

La structure opérationnelle fréquente de Flexible NetFlow est la suivante :

- **Record** : définit les clés et les champs collectés.
- **Exporter** : définit le collecteur de destination, l’adresse source, le protocole d’export et le port UDP.
- **Monitor** : associe le record à un cache et à un ou plusieurs exportateurs.
- **Attachement à l’interface** : active le monitor, souvent en entrée ou en sortie.
- **Collecteur** : reçoit et décode les enregistrements, puis les stocke et les présente.

La syntaxe illustrative ci-dessous vise des versions Cisco IOS XE disposant des commandes Flexible NetFlow correspondantes. Certains champs, choix d’export, directions d’application et options sont spécifiques à la plateforme. Utilise `?`, les commandes de vérification locales et le guide de configuration de la version avant de déployer.

### 3.1 Topologie de laboratoire

- R1 observe le trafic sur `GigabitEthernet1/0/1`.
- Le collecteur se trouve à `192.0.2.200/24` et écoute sur UDP/2055.
- Loopback0 de R1 fournit une adresse source stable, par exemple `198.51.100.1`.
- Une route active entre R1 et le collecteur doit exister. Si l’exportateur utilise une VRF, la destination, l’interface source et la route doivent être cohérentes dans cette VRF.

Les préfixes `192.0.2.0/24` et `198.51.100.0/24` sont réservés à la documentation et doivent être remplacés dans un réseau réel.

### 3.2 Exemple de record personnalisé

```text
R1(config)# flow record NF-INTERMEDIATE-IPv4
R1(config-flow-record)# description IPv4 conversations with counters and timestamps
R1(config-flow-record)# match ipv4 source address
R1(config-flow-record)# match ipv4 destination address
R1(config-flow-record)# match ipv4 protocol
R1(config-flow-record)# match transport source-port
R1(config-flow-record)# match transport destination-port
R1(config-flow-record)# collect counter bytes long
R1(config-flow-record)# collect counter packets long
R1(config-flow-record)# collect timestamp sys-uptime first
R1(config-flow-record)# collect timestamp sys-uptime last
R1(config-flow-record)# exit
```

**Interprétation :** les cinq `match` définissent la conversation IPv4 classée. Les compteurs octets/paquets mesurent son volume et les timestamps first/last décrivent la fenêtre d’observation selon les informations exposées par la plateforme. Des variantes matérielles peuvent employer un modèle de record prédéfini ou ne pas accepter chaque champ proposé.

### 3.3 Exemple d’exportateur

```text
R1(config)# flow exporter NF-COLLECTOR
R1(config-flow-exporter)# description Export to monitoring server
R1(config-flow-exporter)# destination 192.0.2.200
R1(config-flow-exporter)# source Loopback0
R1(config-flow-exporter)# transport udp 2055
R1(config-flow-exporter)# export-protocol netflow-v9
R1(config-flow-exporter)# template data timeout 60
R1(config-flow-exporter)# exit
```

NetFlow v9 utilise des **templates** pour décrire la structure des enregistrements exportés. Le collecteur doit recevoir le template approprié avant de pouvoir correctement décoder les données correspondantes. Le délai `template data timeout 60` est illustratif et dépend de la syntaxe prise en charge. IPFIX peut être une alternative si l’équipement et le collecteur le supportent tous deux ; changer le protocole d’export demande de vérifier la compatibilité des champs et de la version.

### 3.4 Exemple de monitor et cache

```text
R1(config)# flow monitor NF-MONITOR
R1(config-flow-monitor)# description WAN traffic visibility
R1(config-flow-monitor)# record NF-INTERMEDIATE-IPv4
R1(config-flow-monitor)# exporter NF-COLLECTOR
R1(config-flow-monitor)# cache timeout inactive 60
R1(config-flow-monitor)# cache timeout active 180
R1(config-flow-monitor)# exit
```

Les valeurs ci-dessus sont des choix d’exemple, pas des valeurs universelles. Un `inactive` de 60 secondes peut faire expirer les flux qui n’ont pas vu de nouveau paquet depuis ce délai, selon le comportement de la plateforme. Un `active` de 180 secondes cherche à exporter périodiquement les flux longs sans attendre leur inactivité, lorsque cette option est disponible.

### 3.5 Attacher le monitor à une interface

```text
R1(config)# interface GigabitEthernet1/0/1
R1(config-if)# ip flow monitor NF-MONITOR input
R1(config-if)# end
```

`input` signifie que le monitor observe les paquets à leur entrée sur cette interface. La forme exacte de la commande peut varier. Ne pas oublier l’attachement : avoir un record, un exporter et un monitor en configuration ne garantit pas qu’un trafic est observé tant que le monitor n’est pas attaché au bon point d’observation.

### 3.6 Ordre de déploiement recommandé

1. Vérifier que le collecteur est joignable depuis l’adresse source prévue.
2. Créer le record, puis valider les champs acceptés par la plateforme.
3. Créer l’exportateur et vérifier son état.
4. Créer le monitor et associer record/exportateur.
5. Attacher le monitor à une seule interface du laboratoire dans la direction voulue.
6. Générer quelques conversations identifiables.
7. Examiner le cache local, les statistiques de l’exportateur et l’arrivée des données au collecteur.
8. Étendre le périmètre après validation et documenter l’impact sur les ressources.

## 4. Choisir l’interface et la direction

Un des pièges classiques de l’analyse de flux est de comparer des nombres qui ne décrivent pas la même chose. Le trafic entre LAN A et LAN B peut être observé à l’entrée d’une interface, à la sortie d’une autre, ou à plusieurs points intermédiaires. Un flux logique peut donc être représenté dans plusieurs caches. Cela peut être correct pour une analyse par lien, mais trompeur si l’on additionne toutes les observations pour estimer le volume global.

**Schéma 3 — Direction de mesure et risque de double comptage**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 395" width="960" height="395" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="393" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Direction de mesure et risque de double comptage</text><rect x="45" y="85" width="190" height="86" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="140" y="116" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">LAN A</text><text x="140" y="143" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">10.10.0.0/16</text><rect x="386" y="85" width="188" height="86" rx="12" fill="#25263b" stroke="#a5b4fc" stroke-width="2"/><text x="480" y="116" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Routeur R1</text><text x="480" y="143" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">G0/0 · G0/1</text><rect x="725" y="85" width="190" height="86" rx="12" fill="#183126" stroke="#4ade80" stroke-width="2"/><text x="820" y="116" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">WAN / LAN B</text><text x="820" y="143" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">10.20.0.0/16</text><path d="M235 106 H376" stroke="#38bdf8" stroke-width="3"/><text x="304" y="95" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#7dd3fc">Entrée G0/0</text><path d="M584 106 H715" stroke="#4ade80" stroke-width="3"/><text x="650" y="95" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#86efac">Sortie G0/1</text><path d="M715 153 H584" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="7 5"/><text x="650" y="190" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#fcd34d">Retour : autre direction / autre observation</text><path d="M376 153 H235" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="7 5"/><text x="304" y="190" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#fcd34d">Retour vers LAN A</text><rect x="70" y="228" width="390" height="103" rx="12" fill="#142b3e" stroke="#38bdf8"/><text x="265" y="255" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Mesure en entrée</text><text x="265" y="280" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Observe quand le paquet arrive sur G0/0.</text><text x="265" y="305" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Pratique pour attribuer le trafic à une interface source.</text><rect x="500" y="228" width="390" height="103" rx="12" fill="#2f2819" stroke="#fbbf24"/><text x="695" y="255" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Mesure en sortie</text><text x="695" y="280" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Observe quand le paquet quitte l’interface.</text><text x="695" y="305" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Ne pas additionner les deux sans définir la question.</text><text x="480" y="366" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">L’observation à plusieurs interfaces peut compter deux fois le même trafic logique lors d’une synthèse globale.</text></svg>

*Lecture du schéma : Le même échange peut être observé sur plusieurs interfaces et directions ; choisir un périmètre explicite évite de surestimer le volume.*

### 4.1 Questions à poser avant d’attacher un monitor

- Veux-tu expliquer l’utilisation du lien WAN sortant, ou attribuer les conversations à leur réseau d’origine ?
- Le trafic doit-il être observé en entrée, en sortie, ou dans les deux directions ?
- Le collecteur doit-il différencier l’interface d’observation ?
- Les données de plusieurs routeurs vont-elles être additionnées ? Si oui, quelles observations sont réellement disjointes ?
- Le sens aller et le sens retour empruntent-ils le même chemin ?

La bonne configuration dépend de la question. Un monitor en entrée sur un LAN est utile pour identifier la source des communications vues depuis ce segment ; un monitor en sortie sur l’interface WAN peut mieux correspondre à une question sur le trafic quittant le routeur. Il faut toutefois vérifier les champs de direction disponibles et la signification exacte des compteurs exportés.

### 4.2 Pourquoi les compteurs NetFlow peuvent différer des compteurs d’interface

Les compteurs d’interface mesurent le trafic selon les règles de comptage du matériel et de l’interface. Les records NetFlow comptent les paquets qui correspondent au monitor, après prise en compte des fonctions prises en charge et de la position dans le pipeline de traitement. Des écarts peuvent venir du point d’observation, de l’échantillonnage, des paquets non classés, des pertes d’export, des variations de fenêtre temporelle, ou de la différence entre octets de couche 3 et compteurs de couche 2. Il faut comparer des mesures équivalentes plutôt que rechercher une égalité parfaite sans connaître la sémantique des deux sources.

## 5. Cache, temporisations et flux longs

L’exportateur ne transmet pas nécessairement un enregistrement complet après chaque paquet. L’équipement conserve des entrées dans un cache et actualise leurs compteurs pendant que les paquets continuent d’arriver. Les règles d’expiration contrôlent quand ces entrées sont exportées et/ou supprimées.

**Schéma 4 — Cycle de vie d’une entrée dans le cache**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" width="960" height="380" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Cycle de vie d’une entrée dans le cache</text><line x1="105" y1="152" x2="856" y2="152" stroke="#506784" stroke-width="3"/><circle cx="150" cy="152" r="14" fill="#38bdf8"/><circle cx="385" cy="152" r="14" fill="#60a5fa"/><circle cx="620" cy="152" r="14" fill="#4ade80"/><circle cx="830" cy="152" r="14" fill="#fbbf24"/><rect x="55" y="70" width="190" height="63" rx="10" fill="#152b42" stroke="#38bdf8"/><text x="150" y="95" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Premier paquet</text><text x="150" y="116" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Création d’un cache</text><rect x="290" y="190" width="190" height="68" rx="10" fill="#172c43" stroke="#60a5fa"/><text x="385" y="215" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Paquets suivants</text><text x="385" y="237" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Compteurs incrémentés</text><rect x="525" y="70" width="190" height="63" rx="10" fill="#193026" stroke="#4ade80"/><text x="620" y="95" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Fin d’inactivité</text><text x="620" y="116" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Timeout inactive</text><rect x="735" y="190" width="180" height="68" rx="10" fill="#30271b" stroke="#fbbf24"/><text x="825" y="215" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Export / expiration</text><text x="825" y="237" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Selon les règles du cache</text><path d="M150 138 V133" stroke="#38bdf8" stroke-width="2"/><path d="M385 166 V190" stroke="#60a5fa" stroke-width="2"/><path d="M620 138 V133" stroke="#4ade80" stroke-width="2"/><path d="M830 166 V190" stroke="#fbbf24" stroke-width="2"/><text x="480" y="302" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Inactive timeout : flux qui ne génère plus de paquets.</text><text x="480" y="326" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Active timeout : export périodique des flux longs sans attendre leur inactivité.</text><text x="480" y="354" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Les règles exactes d’export et d’expiration dépendent de la plateforme et du type de cache.</text></svg>

*Lecture du schéma : Les paquets sont agrégés dans une entrée de flux puis exportés selon les règles de timeout configurées et prises en charge.*

### 5.1 Inactive timeout

Une entrée peut être considérée inactive lorsque plus aucun paquet correspondant n’a été observé pendant un délai. L’expiration permet d’exporter les flux qui ont terminé leur activité. Un timeout trop long peut retarder l’apparition de certains flux dans le collecteur ; un timeout trop court peut augmenter le nombre d’enregistrements exportés pour une même activité qui reprend par intermittence.

### 5.2 Active timeout

Un flux de longue durée peut continuer à générer du trafic. Un active timeout permet, lorsque supporté, d’exporter périodiquement un enregistrement partiel ou une mise à jour pour cette entrée au lieu d’attendre sa fin. Le collecteur doit gérer correctement les mises à jour/segments successifs afin de calculer les volumes et débits sans les additionner deux fois de manière incorrecte.

### 5.3 Pression sur le cache

Un grand nombre de conversations simultanées consomme de la mémoire. Un record trop détaillé, un attaquant qui génère de nombreuses clés distinctes ou une forte variation des ports peut faire augmenter rapidement le nombre d’entrées. Vérifie les statistiques de cache et les compteurs de ressources propres à la plateforme. Une saturation peut entraîner des pertes de visibilité, même si le routage utilisateur fonctionne encore.

### 5.4 Temporisations et qualité des séries

Un seul enregistrement n’est pas nécessairement une tranche fixe de 60 secondes. Le temps premier/dernier, le moment d’export, les mises à jour actives et l’intervalle de consolidation du collecteur doivent être distingués. Lorsque tu compares des données par minute, documente si la plateforme exporte un flux inactif, une mise à jour de flux long ou un agrégat déjà traité par le collecteur.

## 6. NetFlow v9 et IPFIX : templates et transport

NetFlow v9 et IPFIX reposent sur une description structurée des données exportées. Les templates indiquent comment interpréter les champs dans les enregistrements de données. Si le collecteur n’a pas le template correspondant, il peut recevoir des datagrammes sans pouvoir les décoder correctement. Les templates sont renvoyés périodiquement pour aider à récupérer après des pertes ou une reprise de collecteur.

**Schéma 5 — Export NetFlow v9 / IPFIX : données et templates**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" width="960" height="380" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Export NetFlow v9 / IPFIX : données et templates</text><rect x="42" y="80" width="230" height="122" rx="12" fill="#182b42" stroke="#38bdf8" stroke-width="2"/><text x="157" y="111" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Exportateur</text><text x="157" y="139" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Données + template</text><text x="157" y="166" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">UDP / v9 ou IPFIX</text><rect x="366" y="80" width="230" height="122" rx="12" fill="#30251a" stroke="#fbbf24" stroke-width="2"/><text x="481" y="111" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Réseau de transport</text><text x="481" y="139" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Routage · ACL · VRF</text><text x="481" y="166" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Datagrammes parfois perdus</text><rect x="690" y="80" width="230" height="122" rx="12" fill="#193026" stroke="#4ade80" stroke-width="2"/><text x="805" y="111" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Collecteur</text><text x="805" y="139" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Mémorise le template</text><text x="805" y="166" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Décode les enregistrements</text><path d="M272 141 H356" stroke="#38bdf8" stroke-width="2.5"/><path d="M596 141 H680" stroke="#9fb5d0" stroke-width="2.5"/><path d="M805 202 V242 H157 V202" fill="none" stroke="#a5b4fc" stroke-width="2" stroke-dasharray="7 5"/><text x="480" y="236" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Les templates doivent être reçus à nouveau périodiquement.</text><rect x="105" y="276" width="750" height="67" rx="10" fill="#101c2b" stroke="#334a66"/><text x="480" y="302" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Symptôme fréquent : paquets exportés, mais aucun flux visible dans l’interface de collecte.</text><text x="480" y="325" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Vérifier destination/port/source, reachability, VRF/ACL et réception des templates v9/IPFIX.</text></svg>

*Lecture du schéma : L’exporteur envoie des datagrammes et des informations de template ; le collecteur doit connaître le template pour décoder les données.*

### 6.1 Contrôles côté exportateur

Vérifie les points suivants :

- L’adresse IP de destination du collecteur est correcte.
- Le port UDP attendu correspond à la configuration du collecteur.
- L’interface source est configurée, active et routable depuis l’espace de routage utilisé.
- Le protocole v9 ou IPFIX est compatible avec le collecteur.
- Le bon exporter est associé au monitor et celui-ci est attaché à l’interface active.
- Les règles ACL/firewall laissent passer les datagrammes d’export.
- En contexte VRF, l’exportateur utilise la bonne VRF et la route vers la destination s’y trouve.

L’exemple suivant donne des commandes de consultation que la plateforme peut proposer. Les noms et options varient selon les versions :

```text
show flow exporter NF-COLLECTOR
show flow monitor NF-MONITOR
show flow monitor NF-MONITOR cache
show running-config | section flow exporter
show running-config | section flow monitor
show running-config | section flow record
show ip route 192.0.2.200
ping 192.0.2.200 source Loopback0
```

Pour un exporteur configuré en VRF, réalise les tests de reachability dans cette VRF avec la syntaxe propre à la plateforme. Un ping qui réussit dans la table de routage globale ne prouve pas que le trafic UDP d’export utilise le même contexte.

### 6.2 Ce que UDP implique

L’export NetFlow s’effectue généralement avec UDP dans les exemples considérés ici. UDP ne garantit ni livraison, ni ordre, ni retransmission des datagrammes. Des pertes de paquets d’export peuvent donc créer une collecte incomplète sans interrompre le trafic observé. Il est important de surveiller séparément l’état de l’exportateur, la reachability du collecteur, les pertes du réseau de transport et l’état de réception des templates.

### 6.3 Le port ne révèle pas à lui seul le protocole

Le port UDP 2055 est utilisé dans cet exemple, mais ce n’est pas une exigence universelle. Un collecteur peut écouter sur un autre port. Le port configuré côté exportateur doit correspondre au port de réception côté collecteur, et le flux UDP doit être permis à travers les filtrages intermédiaires.

### 6.4 Une méthode de validation à deux points

Pour séparer émission et réception :

1. Sur l’équipement, vérifie les statistiques de l’exportateur et la route vers la destination.
2. Sur le réseau ou sur le collecteur, capture les datagrammes UDP si tu disposes d’un accès autorisé.
3. Si les datagrammes sont absents à la sortie de l’équipement, reviens à la configuration, au monitor ou à la route.
4. S’ils quittent l’équipement mais n’arrivent pas au serveur, vérifie le chemin, les ACL et le pare-feu.
5. S’ils arrivent mais ne sont pas interprétés, vérifie le port d’écoute, le format sélectionné, les templates et les champs que le collecteur accepte.

## 7. Échantillonnage, précision et dimensionnement

L’échantillonnage observe une partie du trafic au lieu de chaque paquet, afin de réduire les coûts de traitement sur certaines plateformes. Il peut être utile sur les liens très actifs, mais il faut traiter les compteurs comme des estimations si les valeurs ont été extrapolées ou calculées à partir d’un sous-ensemble.

**Schéma 6 — Échantillonnage : économie contre précision**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" width="960" height="370" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Échantillonnage : économie contre précision</text><rect x="35" y="78" width="240" height="140" rx="12" fill="#172b42" stroke="#38bdf8" stroke-width="2"/><text x="155" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Trafic réel</text><text x="155" y="137" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">1 000 000 paquets</text><text x="155" y="165" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Population complète</text><text x="155" y="190" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Volume de référence</text><path d="M275 148 H353" stroke="#9fb5d0" stroke-width="2.5"/><rect x="363" y="78" width="234" height="140" rx="12" fill="#30271b" stroke="#fbbf24" stroke-width="2"/><text x="480" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Échantillonnage</text><text x="480" y="137" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">1 paquet sur 100</text><text x="480" y="165" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">10 000 paquets observés</text><text x="480" y="190" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Gain de ressources possible</text><path d="M597 148 H675" stroke="#9fb5d0" stroke-width="2.5"/><rect x="685" y="78" width="240" height="140" rx="12" fill="#193026" stroke="#4ade80" stroke-width="2"/><text x="805" y="108" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Estimation</text><text x="805" y="137" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Extrapolation possible</text><text x="805" y="165" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Pas une valeur exacte</text><text x="805" y="190" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Biais selon le trafic</text><rect x="73" y="254" width="814" height="80" rx="12" fill="#101c2b" stroke="#334a66"/><text x="480" y="282" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Échantillonner réduit le coût, mais réduit la précision de l’observation.</text><text x="480" y="307" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Le taux réel, la méthode d’échantillonnage et les champs exportés influencent l’interprétation.</text></svg>

*Lecture du schéma : L’échantillonnage observe seulement une partie des paquets et les compteurs peuvent être extrapolés par les outils, avec incertitude.*

### 7.1 Quand l’échantillonnage est-il approprié ?

Il peut convenir à des tendances de capacité, à des top talkers indicatifs ou à l’observation à grande échelle où le coût de chaque paquet serait trop important. Il est moins adapté lorsqu’il faut reconstituer exactement un petit échange, quantifier précisément un faible volume ou fournir une preuve forensique complète. Le caractère aléatoire ou déterministe de l’échantillonnage et les modalités d’extrapolation influencent aussi le biais potentiel.

### 7.2 Une valeur estimée reste une estimation

Supposons que l’outil observe un paquet sur cent et extrapole un volume global à partir des paquets retenus. Le résultat est utile à grande échelle, mais la taille des paquets et la nature du trafic peuvent faire varier l’écart entre échantillon et population réelle. N’écris pas « le trafic était exactement de 800 Mbit/s » si la plateforme fournit une estimation à partir d’un échantillon : documente la méthode et la période.

### 7.3 Planifier le déploiement

Le coût de collecte dépend du nombre de flux uniques, des clés sélectionnées, de la vitesse de création de nouvelles entrées, des timeouts, de la fréquence d’export, de l’échantillonnage et des capacités du matériel. Il dépend également du nombre de monitors appliqués à différentes interfaces. Commence sur un point contrôlé, observe les ressources et étends par étapes. Une haute granularité est un choix de capacité, pas uniquement un choix d’analyse.

## 8. Lire les statistiques et expliquer les top talkers

Un top talker est un hôte, une conversation, un protocole ou une application qui représente un volume élevé dans la série analysée. Pour interpréter correctement une liste, vérifie d’abord :

- Le périmètre exact : routeur, interface, direction, VRF et période.
- L’unité : octets, bits/s, paquets, nombre d’enregistrements ou estimation extrapolée.
- La façon dont le collecteur traite les mises à jour de flux actifs.
- La présence d’échantillonnage ou de filtres.
- La comparabilité avec les compteurs d’interface et la période IP SLA.

### 8.1 Calculer un débit à partir d’un volume

Si un volume mesuré de 150 000 000 octets traverse le point observé sur 60 secondes, le débit moyen estimé est :

\[
\frac{150\,000\,000\times 8}{60}=20\,000\,000\text{ bit/s}=20\text{ Mbit/s}
\]

C’est une moyenne. Une conversation peut envoyer des rafales beaucoup plus importantes sur quelques secondes. Pour la capacité d’un lien de 100 Mbit/s, une moyenne de 20 Mbit/s ne permet donc pas d’exclure une saturation brève. Pour investiguer les pointes, compare les séries d’interface à des intervalles suffisamment fins et consulte les drops, la latence et les files de QoS si ces compteurs existent.

### 8.2 Les volumes peuvent masquer une application lente

Un flux avec peu d’octets peut être sensible au délai. Les appels de signalisation, les transactions courtes ou les applications interactives ne sont pas nécessairement les top talkers. L’observation NetFlow doit être accompagnée de mesures de performance quand l’objectif porte sur l’expérience utilisateur.

### 8.3 Les ports ne suffisent pas à identifier toutes les applications

Un port standard peut être utilisé par différents services, certains usages peuvent employer des ports dynamiques, et le chiffrement masque le contenu. NetFlow peut aider à établir les pairs, protocoles, ports et volumes, mais il ne doit pas être présenté comme une identification applicative certaine dans tous les environnements.

### 8.4 Un exemple d’enquête sur un lien WAN

Supposons qu’un lien WAN de 100 Mbit/s connaisse des ralentissements entre 10 h 00 et 10 h 10. Les données NetFlow indiquent qu’un ensemble de flux augmente fortement pendant cette période. L’interface signale des drops de sortie et IP SLA montre une hausse du RTT vers une cible distante.

Cette combinaison rend la congestion plausible mais ne suffit pas encore à conclure qu’un flux précis est la cause. Vérifie que les trois mesures couvrent le même chemin et la même fenêtre temporelle ; contrôle les files d’attente, les politiques QoS, les changements de route et les symptômes côté serveur. Identifie ensuite si l’augmentation est légitime, anormale ou liée à une mauvaise configuration.

## 9. IP SLA intermédiaire : qualité, seuils et réactions

Au niveau débutant, une opération ICMP Echo servait à déterminer si une cible répondait et à lire son temps aller-retour. Le niveau intermédiaire demande de choisir une sonde qui correspond au service, d’interpréter une série temporelle et d’activer des alertes sans transformer chaque fluctuation en incident.

### 9.1 Choisir le type de sonde en fonction du service

| Besoin | Type de mesure possible | Précaution |
|---|---|---|
| Joignabilité IP vers une cible | ICMP Echo | N’évalue pas directement l’application. |
| Délai d’établissement d’une connexion vers un port | TCP Connect, si pris en charge | Un port ouvert ne garantit pas un traitement applicatif sain. |
| Gigue et pertes sur un échange UDP | UDP Jitter, selon le support et le répondant | Vérifier les prérequis côté source et côté répondant. |
| Résolution de nom | Opération DNS prise en charge | Tester le résolveur réellement utilisé par les clients. |
| Réponse d’un service | Opération applicative adaptée à la version | Valider les capacités exactes de la plateforme. |

La cible doit représenter le service ou le chemin que l’on veut surveiller. Une sonde vers la passerelle locale peut rester bonne alors que le WAN est en panne. Une sonde vers un service distant teste davantage de segments, mais son échec peut avoir plusieurs causes : réseau, ACL, serveur, route retour ou filtrage ICMP/TCP.

### 9.2 Seuils de performance

Un seuil permet de signaler qu’une mesure dépasse un niveau défini, par exemple un RTT trop élevé ou un événement de perte de connectivité. Les paramètres et les types de réaction pris en charge varient selon les opérations IP SLA et la version. Certaines plateformes permettent d’émettre des notifications syslog/SNMP ou de déclencher une opération complémentaire. Ces actions ne doivent pas être supposées disponibles sans vérification.

**Schéma 7 — IP SLA : seuils et stabilisation des alertes**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380" width="960" height="380" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">IP SLA : seuils et stabilisation des alertes</text><rect x="45" y="70" width="270" height="105" rx="12" fill="#152b42" stroke="#38bdf8" stroke-width="2"/><text x="180" y="100" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">IP SLA probe</text><text x="180" y="127" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">RTT / gigue / perte</text><text x="180" y="151" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Séries de mesures</text><rect x="345" y="70" width="270" height="105" rx="12" fill="#30271b" stroke="#fbbf24" stroke-width="2"/><text x="480" y="100" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Seuils + hystérésis</text><text x="480" y="127" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Seuil haut / seuil bas</text><text x="480" y="151" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Évite les alarmes répétitives</text><rect x="645" y="70" width="270" height="105" rx="12" fill="#193026" stroke="#4ade80" stroke-width="2"/><text x="780" y="100" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Réaction</text><text x="780" y="127" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Trap / syslog / action supportée</text><text x="780" y="151" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Selon plate-forme</text><path d="M315 123 H335" stroke="#9fb5d0" stroke-width="2.5"/><path d="M615 123 H635" stroke="#9fb5d0" stroke-width="2.5"/><line x1="100" y1="267" x2="870" y2="267" stroke="#526985" stroke-width="1.5"/><line x1="100" y1="220" x2="870" y2="220" stroke="#fb923c" stroke-width="2" stroke-dasharray="7 5"/><text x="861" y="211" text-anchor="end" fill="#9fb2c9" font-size="12px" font-family="Inter,Arial,sans-serif">Seuil haut (alarme)</text><line x1="100" y1="300" x2="870" y2="300" stroke="#4ade80" stroke-width="2" stroke-dasharray="7 5"/><text x="861" y="319" text-anchor="end" fill="#9fb2c9" font-size="12px" font-family="Inter,Arial,sans-serif">Seuil bas (retour à la normale)</text><polyline points="115,286 170,272 225,246 280,216 335,208 390,236 445,251 500,271 555,288 610,294 665,267 720,232 775,212 830,215" fill="none" stroke="#60a5fa" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><text x="480" y="352" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Exemple schématique : un événement n’est pas nécessairement renvoyé à chaque mesure hors seuil.</text></svg>

*Lecture du schéma : Une mesure franchit le seuil haut, puis le retour sous un seuil bas réarme certaines réactions afin de limiter les alarmes répétées.*

### 9.3 Hystérésis et seuil haut / seuil bas

Si une alerte est déclenchée au-dessus de 150 ms et effacée dès que la mesure repasse à 149 ms, une valeur proche de la limite peut produire un grand nombre d’alertes et de rétablissements. Un seuil de retour inférieur, par exemple 100 ms à titre illustratif, crée une zone d’hystérésis. L’alarme se déclenche quand la mesure franchit le seuil haut et ne revient à l’état normal qu’après avoir franchi le seuil bas, selon la logique du mécanisme utilisé.

Les valeurs choisies doivent refléter les objectifs réels de service et la variabilité habituelle. Elles ne doivent pas être copiées aveuglément à partir de cet exemple. Vérifie également si le mécanisme demande plusieurs mesures consécutives ou applique une moyenne.

### 9.4 Exemple illustratif de configuration IP SLA

Les syntaxes IP SLA et reaction-configuration ne sont pas identiques sur toutes les plates-formes. Le bloc ci-dessous sert à illustrer l’intention : créer une sonde, l’exécuter et configurer une réaction aux seuils, si les commandes sont prises en charge par la version du matériel.

```text
! Exemple de base ; vérifier chaque commande avec la CLI locale
ip sla 10
 icmp-echo 192.0.2.10 source-interface GigabitEthernet1/0/1
 timeout 1000
 frequency 10
ip sla schedule 10 life forever start-time now
!
! La syntaxe de réaction ci-dessous est dépendante de la version.
! Vérifier les valeurs, le nom du monitored-element et action-type.
! ip sla reaction-configuration 10 react rtt threshold-type ...
```

Sur les plateformes disposant des réactions à seuils, la politique doit préciser le champ surveillé, le type de seuil, les valeurs hautes/basses et l’action attendue. Si le routeur ne prend pas en charge la réaction souhaitée, les statistiques peuvent toujours être interrogées par un système de supervision externe.

### 9.5 IP SLA, Track et bascule : éviter les fausses conclusions

IP SLA peut alimenter un objet `track` utilisé par une route statique conditionnelle. Cette chaîne peut participer à une bascule, mais la disponibilité de la sonde dépend du chemin de routage réellement emprunté. Si une sonde vers une adresse distante peut encore passer par la route de secours, elle ne prouve pas que le chemin principal est encore sain. Concevoir la source, la cible et le suivi pour qu’ils mesurent l’événement voulu ; tester aussi l’échec et le retour à la normale.

### 9.6 Historique des mesures et alignement temporel

Lorsqu’on corrèle un incident, utilise la même zone horaire, vérifie la synchronisation NTP, note la fréquence de sonde et compare des fenêtres équivalentes. IP SLA peut produire une mesure chaque dizaine de secondes alors que le collecteur agrège NetFlow sur une minute. On peut comparer les tendances, mais il faut éviter de prétendre qu’un pic à 10:03:17 est exactement causé par une entrée NetFlow agrégée sur 10:03–10:04 sans données plus fines.

## 10. Corréler IP SLA, NetFlow et compteurs d’interface

La corrélation n’est pas une simple juxtaposition de graphes. Il faut examiner si les données correspondent au même trajet, à la même période et à des unités comparables. IP SLA répond à la question « comment se comporte le chemin vers cette cible ? » ; NetFlow aide à « quelles conversations sont observées et quel volume représentent-elles ? » ; les compteurs d’interface aident à « le lien ou les files montrent-ils des pertes ou des erreurs ? »

**Schéma 8 — Méthode de corrélation IP SLA + NetFlow**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 390" width="960" height="390" preserveAspectRatio="xMidYMid meet"><rect x="1" y="1" width="958" height="388" rx="18" fill="#0b1422" stroke="#2b415d"/><text x="480.0" y="34" text-anchor="middle" font-weight="700" font-size="21px" font-family="Inter,Arial,sans-serif" fill="#f4f8ff">Méthode de corrélation IP SLA + NetFlow</text><rect x="36" y="74" width="888" height="58" rx="10" fill="#182b42" stroke="#38bdf8"/><text x="480" y="99" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Étape 1 · Valider le symptôme</text><text x="480" y="119" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">IP SLA : portée, RTT, pertes, tendance temporelle</text><path d="M480 132 V154" stroke="#9fb5d0" stroke-width="2.3"/><rect x="36" y="160" width="426" height="76" rx="10" fill="#193026" stroke="#4ade80"/><text x="249" y="188" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Étape 2 · Repérer le trafic</text><text x="249" y="212" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">NetFlow : interfaces, top talkers, volumes</text><rect x="498" y="160" width="426" height="76" rx="10" fill="#30271b" stroke="#fbbf24"/><text x="711" y="188" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Étape 3 · Contrôler l’équipement</text><text x="711" y="212" text-anchor="middle" font-size="14px" font-family="Inter,Arial,sans-serif" fill="#c3d2e5">Drops, erreurs, CPU, file d’attente, route</text><path d="M249 236 V255 H480 V270" fill="none" stroke="#9fb5d0" stroke-width="2.3"/><path d="M711 236 V255 H480" fill="none" stroke="#9fb5d0" stroke-width="2.3"/><rect x="170" y="275" width="620" height="65" rx="10" fill="#18243a" stroke="#a5b4fc"/><text x="480" y="301" text-anchor="middle" font-weight="600" font-size="16px" font-family="Inter,Arial,sans-serif" fill="#e6eef9">Étape 4 · Formuler une hypothèse vérifiable</text><text x="480" y="322" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">Comparer la même période, le même chemin et des mesures indépendantes.</text><text x="480" y="365" text-anchor="middle" font-size="12px" font-family="Inter,Arial,sans-serif" fill="#9fb2c9">La corrélation aide à prioriser l’enquête ; elle ne prouve pas automatiquement la causalité.</text></svg>

*Lecture du schéma : IP SLA, NetFlow et les compteurs d’équipement apportent des preuves complémentaires pour diagnostiquer un incident.*

### 10.1 Matrice d’interprétation

| IP SLA | NetFlow | Compteurs d’interface | Hypothèse à examiner en premier | Ce que cela ne prouve pas |
|---|---|---|---|---|
| RTT en hausse | Forte hausse de volume | Utilisation/drops en hausse | Congestion possible | Que le plus gros flux est nécessairement fautif. |
| RTT en hausse | Volumes stables | Erreurs physiques en hausse | Problème de lien possible | Que la cause est uniquement physique. |
| Sonde en échec | Aucune donnée visible | Interface up/up | Cible/route/ACL/monitor/export à vérifier | Que l’absence de NetFlow traduit une panne du trafic. |
| RTT stable | Gros flux détecté | Interface sans drops | Trafic important mais lien peut-être sain | Qu’une application est lente uniquement à cause du volume. |
| Sonde ICMP en échec | Conversation applicative visible | Aucun drop évident | Filtrage ICMP ou chemin retour à tester | Que l’application est forcément en panne. |

### 10.2 Étapes de raisonnement

1. Décrire le symptôme exact et l’intervalle temporel.
2. Vérifier que l’opération IP SLA cible un point de service significatif.
3. Valider que le monitor NetFlow est attaché au point d’observation attendu.
4. Contrôler si les volumes sont instantanés, moyens, échantillonnés ou agrégés.
5. Comparer les compteurs d’interface et les drops du même segment.
6. Formuler une hypothèse testable et rechercher une donnée indépendante pour la confirmer.
7. Documenter la conclusion avec ses limites et les prochaines vérifications.

### 10.3 Exemple concret

**Symptôme :** les utilisateurs signalent que les transferts vers un serveur distant sont lents de 14 h 00 à 14 h 15.

**Données :** IP SLA vers le réseau du service montre une augmentation du RTT ; NetFlow signale plusieurs flux volumineux à travers le WAN ; les compteurs de sortie montrent un taux élevé et des drops sur une file.

**Hypothèse :** congestion de sortie possible, éventuellement exacerbée par une classe de trafic qui n’est pas correctement mise en file d’attente.

**Vérifications :** comparer le débit d’interface et les flux sur la même fenêtre ; examiner la politique QoS et ses compteurs ; vérifier que les paquets IP SLA suivent la même route ; contrôler l’état du serveur et le chemin retour.

**Conclusion correcte :** les observations sont cohérentes avec une congestion de sortie. La causalité d’un flux précis reste à confirmer par l’analyse de la politique, des séries temporelles et, si nécessaire, une capture ou un test contrôlé.

## 11. Laboratoire guidé de bout en bout

### 11.1 Objectif

Configurer une collecte Flexible NetFlow de conversations IPv4 sur une interface, vérifier l’export vers un collecteur et créer une opération IP SLA qui mesure une cible représentative. Enfin, provoquer des tests simples puis expliquer ce qu’ils prouvent et ce qu’ils ne prouvent pas.

### 11.2 Schéma logique

```text
PC-A ---- G1/0/1  R1  G1/0/2 ---- WAN / R2 ---- Serveur de test
                  |
                Lo0: 198.51.100.1
                  |
             réseau de supervision
                  |
        Collecteur: 192.0.2.200:2055/UDP
```

Les adresses sont réservées à la documentation. Remplace-les par le plan d’adressage de ton laboratoire. Le collecteur doit écouter avec le même protocole et le même port que l’exportateur.

### 11.3 Précontrôles

1. Vérifie les interfaces et les routes vers la cible IP SLA et vers le collecteur.
2. Vérifie que les ACL permettent le trafic de test et l’UDP d’export entre les points appropriés.
3. Note la version IOS/IOS XE et confirme les commandes Flexible NetFlow acceptées.
4. Assure-toi que tu peux générer des conversations connues (par exemple ping, DNS ou HTTP d’un serveur de laboratoire autorisé).
5. Capture ou note les compteurs d’interface avant de commencer pour disposer d’une référence.

### 11.4 Déploiement

Applique les blocs de record, exporter et monitor des sections 3.2 à 3.4, adaptés à l’équipement. Attache le monitor en entrée sur l’interface où le trafic doit être observé. Configure IP SLA avec une cible et une interface source réelles du laboratoire.

**Ne colle pas tous les blocs aveuglément en production.** Vérifie d’abord chaque sous-commande dans le CLI de l’équipement, car les modes, noms d’interfaces, types de record et protocoles d’export varient.

### 11.5 Générer du trafic de test

Depuis PC-A, établis plusieurs conversations différentes :

- ping vers une cible du laboratoire, si ICMP est permis ;
- connexion TCP vers un port de test ouvert ;
- transfert de quelques fichiers de test, si autorisé ;
- conversations de destinations différentes pour vérifier que les clés distinguent les flux.

Dans le collecteur, recherche les adresses et ports correspondants. Si le collecteur agrège les données, note l’intervalle temporel et la définition de chaque compteur. Ne t’attends pas nécessairement à voir chaque paquet comme une ligne séparée.

### 11.6 Résultats attendus

- Le monitor et le cache indiquent des entrées correspondant aux conversations générées.
- L’exportateur indique une configuration cohérente avec le collecteur.
- Le collecteur reçoit les datagrammes et les décode avec le template attendu.
- IP SLA indique que l’opération est planifiée et fournit des mesures, ou un état d’échec interprétable.
- Les volumes NetFlow peuvent différer des compteurs d’interface ; l’écart s’explique par le point de mesure, la définition des octets, les fenêtres ou l’échantillonnage.

### 11.7 Variantes à tester

1. **Mauvais port d’écoute :** change temporairement le port côté collecteur uniquement dans un environnement contrôlé. Observe que la réception échoue sans que le trafic utilisateur doive échouer.
2. **Route source différente :** si le laboratoire le permet, modifie la source d’export ou son routage et constate l’effet sur l’acheminement des datagrammes.
3. **Mauvaise direction :** attache le monitor à une autre direction, puis compare les champs et volumes ; ne mélange pas les résultats sans documenter le périmètre.
4. **Sonde filtrée :** bloque temporairement ICMP dans une ACL de laboratoire tout en gardant un port de service accessible. Observe la limite du test ICMP.
5. **Flux long :** maintiens un transfert durant plusieurs minutes et observe comment les timeouts actifs et les agrégations du collecteur influencent les enregistrements.

## 12. Dépannage systématique

Le dépannage doit distinguer les pannes de configuration, d’observation, d’export et d’analyse. Il est inutile de commencer par modifier tous les timeouts si la route vers le collecteur est absente ; il est inutile d’accuser l’ACL si le monitor n’est attaché à aucune interface.

### 12.1 Arbre de décision

| Symptôme | Contrôles prioritaires | Causes possibles |
|---|---|---|
| Aucun flux dans le cache local | Interface, direction, trafic généré, monitor, record accepté | Mauvais point d’observation, monitor non attaché, trafic de test absent, champs non supportés. |
| Cache local non vide, collecteur vide | Exporter, source, destination, route, port, VRF, ACL/firewall | UDP bloqué, mauvais port, mauvais espace de routage, collecteur inaccessible. |
| Datagrams reçus, données illisibles | Format NetFlow v9/IPFIX, templates, version du collecteur, champs | Template non reçu, format incompatible, parser inadapté. |
| Données apparaissent en retard | Active/inactive timeout, agrégation du collecteur, fréquence des templates | Entrée encore active, agrégation différée, fenêtre d’export. |
| Volumes plus élevés que prévu | Interfaces/ directions observées, clé de flux, mises à jour actives | Double comptage logique, agrégation ou interprétation erronée. |
| IP SLA en échec, mais application accessible | Filtrage de la sonde, source, route retour, type de sonde | ICMP bloqué, cible non représentative, opération inadaptée. |
| IP SLA stable, utilisateurs lents | Type de sonde, destination, files QoS, service applicatif | La sonde ne reproduit pas le trafic applicatif. |

### 12.2 Séquence de commandes de contrôle

Selon le système, les commandes ci-dessous peuvent être disponibles sous des variantes. Utilise la complétion CLI et la documentation de la version :

```text
show flow exporter NF-COLLECTOR
show flow monitor NF-MONITOR
show flow monitor NF-MONITOR cache
show flow record NF-INTERMEDIATE-IPv4
show running-config | section flow
show interfaces GigabitEthernet1/0/1
show ip route 192.0.2.200
show ip sla configuration
show ip sla statistics
show track
```

La première question n’est pas « quelle commande inconnue puis-je essayer ? », mais « quel maillon de la chaîne est le premier qui ne fonctionne pas ? » Vérifie l’observation locale, puis l’export, puis la réception et le décodage.

## 13. Exercices corrigés

### Exercice 1 — Choisir les clés

**Situation :** tu dois identifier les hôtes qui consomment le WAN par protocole, mais tu n’as pas besoin de distinguer chaque session TCP.

**Réponse :** commencer par les adresses source/destination et le protocole, plus les compteurs utiles. Les ports source/destination peuvent être ajoutés si la distinction par conversation applicative devient nécessaire. Ce choix limite l’explosion des entrées par rapport à un cinq-tuple complet, tout en gardant un niveau d’attribution par hôte et protocole.

### Exercice 2 — Exporteur silencieux

**Situation :** le cache du monitor contient des entrées, mais le collecteur ne reçoit rien.

**Réponse :** vérifier l’adresse/port de destination et la source de l’exporteur, la route dans le contexte de routage pertinent, le monitor/exporter associé, les ACL et le port d’écoute du collecteur. Si les datagrammes atteignent le serveur mais n’apparaissent pas dans l’application, vérifier les templates, le format et la configuration du collecteur.

### Exercice 3 — Calculer le débit moyen

**Situation :** un enregistrement représente 48 Mo décimaux en 40 secondes. Estime le débit moyen en Mbit/s.

\[
\frac{48\,000\,000 \times 8}{40}=9\,600\,000\text{ bit/s}=9{,}6\text{ Mbit/s}
\]

**Réponse :** 9,6 Mbit/s en moyenne sur la durée considérée. Ce n’est pas une mesure de pic instantané.

### Exercice 4 — IP SLA échoue, HTTP répond

**Situation :** une opération ICMP Echo vers un serveur échoue, mais le navigateur atteint son service HTTPS.

**Réponse :** les faits ne sont pas nécessairement contradictoires. ICMP peut être filtré, la source de la sonde peut emprunter un chemin différent, ou la politique du serveur peut répondre à HTTPS sans répondre à ICMP. Tester la route, le retour, les ACL et une sonde adaptée au service avant de conclure.

### Exercice 5 — Top talker et saturation

**Situation :** NetFlow identifie un gros transfert durant un ralentissement. Les compteurs d’interface indiquent aussi des drops.

**Réponse :** la congestion est plausible, mais le top talker n’est pas automatiquement fautif. Vérifier si l’augmentation des octets, les drops et la hausse de RTT sont alignés dans le temps, examiner la QoS et l’impact sur les autres flux, puis établir si le transfert est attendu.

### Exercice 6 — Pourquoi les nombres diffèrent-ils ?

**Situation :** NetFlow totalise 75 Go alors que le compteur d’interface indique 68 Go pour la même heure.

**Réponse :** vérifier d’abord que la période, l’interface et la direction sont réellement identiques. Examiner l’observation à plusieurs endroits, l’échantillonnage, les mises à jour de flux actifs, les octets couche 2/couche 3, les filtres et la méthode d’agrégation du collecteur. Ne pas modifier arbitrairement un facteur pour faire coïncider les chiffres.

## 14. Quiz final

**1. À quoi sert principalement la partie `match` d’un record Flexible NetFlow ?**  
A. Définir l’adresse IP du collecteur.  
B. Définir les clés qui identifient les entrées de flux.  
C. Définir l’adresse source de la sonde IP SLA.  
D. Activer la route par défaut.

**2. Pourquoi les templates sont-ils importants en NetFlow v9/IPFIX ?**  
A. Ils remplacent les routes IP.  
B. Ils permettent au collecteur de connaître la structure des enregistrements.  
C. Ils garantissent la livraison UDP.  
D. Ils chiffrent les paquets exportés.

**3. Que peut provoquer un record excessivement détaillé ?**  
A. Toujours moins d’entrées.  
B. Une hausse du nombre d’entrées et du coût de collecte.  
C. La suppression automatique des ACL.  
D. Une mesure RTT plus précise.

**4. Un monitor en entrée sur une interface observe :**  
A. Tous les paquets partout dans le réseau.  
B. Les paquets observés à l’entrée de cette interface, selon les capacités du système.  
C. Seulement l’UDP de NetFlow.  
D. Seulement les réponses ICMP.

**5. IP SLA ICMP Echo prouve-t-il que HTTPS fonctionne ?**  
A. Oui, toujours.  
B. Non ; il mesure l’échange ICMP, pas directement le service HTTPS.  
C. Oui, si RTT < 100 ms.  
D. Oui, si NetFlow est activé.

**6. Que signifie une entrée de flux exportée périodiquement pendant une conversation longue ?**  
A. Forcément un nouveau flux utilisateur distinct.  
B. Cela peut être une mise à jour d’un flux actif, selon le cache et le collecteur.  
C. La session TCP est nécessairement interrompue.  
D. Le paquet a été retransmis par UDP.

**7. Pourquoi ne faut-il pas additionner sans réflexion les volumes de plusieurs monitors ?**  
A. Parce que NetFlow ne compte jamais les octets.  
B. Parce que la même conversation peut être observée à plusieurs points ou directions.  
C. Parce que les routeurs n’ont pas d’interface de sortie.  
D. Parce que IP SLA désactive NetFlow.

**8. Que faut-il contrôler quand le cache est actif mais le collecteur reste vide ?**  
A. Uniquement le modèle du PC client.  
B. Exporter, route/source/VRF, port, ACL, réception UDP et templates.  
C. Le DNS public seulement.  
D. Le masque du serveur sans vérifier sa route.

**9. Une moyenne de 20 Mbit/s sur un lien 100 Mbit/s exclut-elle une saturation brève ?**  
A. Oui.  
B. Non, la moyenne masque des rafales.  
C. Oui si le collecteur reçoit v9.  
D. Oui si les flux sont TCP.

**10. Quelle est la bonne méthode pour corréler IP SLA et NetFlow ?**  
A. Assumer qu’une hausse de trafic cause toujours la hausse du RTT.  
B. Comparer les mêmes périodes et chemins, puis confirmer l’hypothèse par des données complémentaires.  
C. Se baser sur le top talker seulement.  
D. Désactiver les compteurs d’interface.

### Corrigé du quiz

1. **B** — `match` définit les clés de flux.
2. **B** — Le template décrit la structure des données au collecteur.
3. **B** — Plus de clés peut multiplier les entrées et les coûts.
4. **B** — L’observation est liée au point et à la direction.
5. **B** — ICMP n’est pas un test HTTPS.
6. **B** — L’export périodique peut correspondre à la mise à jour d’un flux long.
7. **B** — Plusieurs points d’observation peuvent représenter le même trafic logique.
8. **B** — Il faut dépanner la chaîne d’export et de réception.
9. **B** — Le débit moyen ne décrit pas les pics.
10. **B** — Comparaison temporelle et chemin cohérents, puis confirmation indépendante.

## 15. Fiche de référence

### Flexible NetFlow

- `record` : définit clés `match` et champs `collect`.
- `exporter` : destination, source, port, protocole et paramètres d’export.
- `monitor` : associe record, cache et exporteur.
- Interface + direction : détermine le point d’observation réel.
- Cache : contrôle la conservation et l’export des entrées selon les règles disponibles.
- Collecteur : doit être compatible avec le protocole, recevoir les datagrammes et décoder les templates.

### IP SLA

- Le type de sonde fixe ce qui est mesuré.
- La source et la cible déterminent le chemin observé.
- Une cible représentative est plus utile qu’une simple cible facile à joindre.
- Les seuils doivent refléter un objectif opérationnel et tenir compte de la variabilité.
- Le suivi de route doit être testé dans les deux scénarios, panne puis récupération.

### Routine de dépannage

1. Définir symptôme, période et périmètre.
2. Vérifier les mesures et le point d’observation.
3. Examiner la route/source, l’exporteur et le collecteur.
4. Vérifier templates et format.
5. Comparer les unités et les fenêtres temporelles.
6. Confirmer l’hypothèse par une source complémentaire.

## 16. Sources et compatibilité

Les guides Cisco sont des références à consulter pour la syntaxe et les fonctionnalités exactes de la plateforme déployée. Les pages évoluent avec les versions ; la documentation correspondant au modèle et à la release installée doit primer sur cet exemple pédagogique.

- Cisco, **Flexible NetFlow Configuration Guide** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/fnf-avc/flexible-netflow-configuration-guide.html
- Cisco, **Troubleshoot NetFlow on IOS XE** : https://www.cisco.com/c/en/us/support/docs/quality-of-service-qos/netflow/226065-troubleshoot-netflow-on-ios-xe.html
- Cisco, **IP SLAs Reaction Threshold** : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr3-fwd/ip-slas/ip-slas-configuration-guide/ip-slas-reaction-threshold.html

> **Avertissement de production :** ce cours est un support pédagogique. Valide les commandes, les champs disponibles, les impacts sur les ressources, l’export et les seuils de réaction sur la plateforme réelle. Commence dans un laboratoire ; surveille le CPU/cache et la charge d’export avant une extension à grande échelle.
