# QoS Voix et Vidéo — Intermédiaire

## Mise en contexte : concevoir une politique QoS qui tient sous charge

Au niveau débutant, tu as découvert les marquages, les files d'attente et les métriques de qualité. Au niveau intermédiaire, le défi consiste à faire fonctionner ces éléments ensemble : plusieurs sites, téléphones, visioconférences, accès Wi-Fi, tunnels, WAN opérateur et applications métiers se partagent la même infrastructure.

Une stratégie correcte ne consiste pas à marquer tout le trafic de collaboration en priorité maximale. Elle définit des classes, établit une limite de confiance, réserve ou répartit la capacité de façon contrôlée, traite les pointes et vérifie les résultats avec des compteurs et des mesures de bout en bout.

> **Règle de conception :** classifier de manière fiable, marquer de façon cohérente, protéger les classes temps réel, maîtriser la congestion et prouver le comportement sur le chemin réel.

## 1. Compétences visées et prérequis

Ce niveau suppose la compréhension de DSCP/CoS, EF, AF, SIP/RTP, VLAN voix, délai, gigue et perte. À la fin, tu sauras :

- concevoir une matrice de classes voix, signalisation, vidéo et données ;
- établir des limites de confiance et reclasser les sources non fiables ;
- concevoir des politiques de files avec priorité limitée, bande passante garantie et meilleur effort ;
- différencier shaping, policing, LLQ, CBWFQ et mécanismes de gestion de congestion ;
- dimensionner une classe à partir du nombre de sessions et du débit réel ;
- analyser DSCP, CoS, drops de files et statistiques RTP ;
- comprendre les interactions avec Wi-Fi, VPN et WAN ;
- documenter une politique, ses tests et ses critères d'acceptation.

# Partie I — Construire une stratégie de classification

## 2. De l'application à la file de sortie

Une QoS de bout en bout comprend plusieurs opérations qui sont souvent confondues :

1. **Identifier/classifier** : reconnaître le trafic par classe d'application, média, signalisation, adresse, protocole, port, ACL ou marquage contrôlé.
2. **Marquer** : attribuer DSCP et, lorsque pertinent, CoS/PCP.
3. **Contrôler le débit** : appliquer policing ou shaping au point adapté.
4. **Mettre en file et ordonnancer** : attribuer la classe à une file et choisir comment le lien est partagé.
5. **Surveiller** : mesurer les débits, les drops, la latence, la gigue et le comportement réel des applications.

```text
Source -> classification -> validation du marquage -> DSCP/CoS
                                                   |
                                                   v
                           sortie congestionnée -> files/ordonnancement
                                                   |
                                                   v
                                          mesures et compteurs
```

Le marquage exprime une intention. La file d'attente applique un traitement. Les compteurs confirment ce qui se passe réellement.

## 3. Élaborer une matrice de classes

La matrice suivante illustre un plan d'entreprise. Elle doit être adaptée à la plateforme de collaboration et aux exigences de l'organisation.

| Classe | Exemple de trafic | Marquage fréquent | Traitement envisagé |
|---|---|---|---|
| Audio temps réel | RTP voix interactive | EF (46) | file faible latence, débit prioritaire plafonné |
| Signalisation | SIP ou signalisation de collaboration | CS3 (24) ou CS5 (40), selon politique | débit assuré, faible risque de perte, pas nécessairement même priorité que l'audio |
| Vidéo interactive | flux vidéo de conférence | AF41 (34) ou marquage défini par le fournisseur | capacité réservée/pondérée, gestion de congestion selon plateforme |
| Collaboration spécialisée | certains systèmes immersifs/TelePresence | parfois CS4 (32) | classe définie explicitement et dimensionnée |
| Applications transactionnelles | applications métier interactives | classe AF/CS définie localement | débit et délai adaptés à la criticité |
| Données générales | web, mises à jour, transferts | CS0 (0), par défaut | meilleur effort et partage équitable |
| Contrôle réseau | protocoles de routage/gestion selon politique | valeurs spécifiques, souvent CS6 pour certains contrôles | réservé au trafic réellement autorisé |

Les valeurs de signalisation et de vidéo diffèrent parfois selon les référentiels, produits et versions. RFC 4594 et les guides constructeurs fournissent des recommandations, mais la politique de l'entreprise doit choisir une seule convention cohérente. Ne mélange pas CS3 et CS5 au hasard, et n'accorde pas CS6/CS7 à des applications utilisateur.

### 3.1 Audio et vidéo d'un même appel

Audio et vidéo n'ont pas forcément le même débit ni le même besoin de file. Dans de nombreuses politiques, l'audio reçoit EF tandis que la vidéo de conférence reçoit AF41 ou une classe vidéo définie. Les maintenir dans une seule classe illimitée peut laisser la vidéo consommer la capacité destinée à l'audio.

### 3.2 Signalisation et média

La signalisation SIP produit généralement moins de trafic que le média RTP. Elle doit rester fiable, mais il n'est pas toujours judicieux de lui donner le même traitement de priorité stricte que l'audio. Une politique doit aussi prendre en compte les appels en rafale après une panne ou un redémarrage.

## 4. DSCP : préserver, traduire ou réécrire ?

Le DSCP se trouve dans l'en-tête IP. Un routeur peut le préserver, le réécrire ou s'en servir pour sélectionner une classe. Dans les réseaux administrés, la frontière de confiance doit être explicite.

- **Sources fiables** : téléphone géré, équipement de visioconférence administré, switch ou routeur du domaine maîtrisé. Le marquage peut être accepté après validation.
- **Sources non fiables** : PC utilisateur, invité, IoT ou terminal qui peut choisir librement ses marquages. Classifier selon une politique et réécrire les valeurs non autorisées.
- **Frontière de domaine** : entrée du WAN, VPN, réseau opérateur ou interconnexion. Définir ce qui est préservé et ce qui est remappé.

Un utilisateur peut marquer un téléchargement en EF pour tenter de lui faire obtenir un traitement prioritaire. C'est pourquoi la confiance ne doit pas être accordée simplement parce que la valeur DSCP est élevée.

### 4.1 Relation entre DSCP et CoS

CoS/PCP existe sur une trame taguée de couche 2. DSCP existe dans le paquet IP. Lorsque le trafic passe d'un domaine L2 à un domaine routé ou à un tunnel, les équipements peuvent devoir convertir les valeurs selon une table de mapping. Le mapping doit être documenté et vérifié sur les liens montants, les trunks et les points de terminaison des tunnels.

# Partie II — Files, congestion et contrôle de débit

## 5. LLQ et CBWFQ

**CBWFQ (Class-Based Weighted Fair Queuing)** répartit la capacité entre des classes configurées. **LLQ (Low Latency Queuing)** ajoute généralement une file à priorité stricte pour le trafic temps réel, souvent à l'intérieur d'une politique CBWFQ.

La priorité stricte aide à réduire le délai d'attente, mais elle doit être contrôlée. Le trafic qui dépasse l'enveloppe configurée peut être abandonné ou traité selon le comportement de la plateforme. Il ne faut pas supposer que toute politique LLQ fonctionne de manière identique sur routeur, switch, contrôleur Wi-Fi ou SD-WAN.

Une classe vidéo peut recevoir une part de capacité garantie sans être dans la file stricte audio. Les données classiques utilisent le reste selon l'algorithme et les paramètres de l'équipement.

## 6. Policing : appliquer une enveloppe

Le policing mesure un débit, généralement à l'aide d'un profil de débit et d'une tolérance de rafale. Le trafic conforme est transmis ; le trafic excédentaire peut être marqué vers une classe moins prioritaire, supprimé ou traité selon la configuration.

Le policing est utile à l'entrée d'un domaine pour empêcher une source de consommer des ressources au-delà du profil autorisé. Cependant, policer à l'aveugle l'audio réel peut introduire de la perte et dégrader l'appel. Il faut choisir le point, le profil et l'action avec soin.

## 7. Shaping : lisser avant la congestion

Le shaping met temporairement en tampon les paquets afin de limiter le débit envoyé vers un lien. Il est souvent utilisé lorsque le débit logique d'une interface est supérieur au débit réel du circuit opérateur, ou pour organiser les classes à l'intérieur d'un débit parent.

Si l'accès opérateur est de 20 Mbit/s mais que le routeur envoie plus rapidement que cette valeur, la file du fournisseur peut accumuler des paquets sans appliquer la même politique QoS. Un shaping légèrement inférieur au débit réellement disponible peut permettre au routeur de contrôler la file, à condition que l'overhead et le contrat soient correctement pris en compte.

```text
Rafales applicatives --> [shaper au bord client] --> débit maîtrisé --> WAN
                                      |
                                      +-- les files locales décident qui attend
```

Il n'existe pas une marge de shaping valable pour tous les circuits : valider la couche de mesure, l'encapsulation, le débit du contrat, les mécanismes de burst et la façon dont le fournisseur mesure le service.

## 8. WRED/AQM et trafic temps réel

Les mécanismes de gestion active de files (AQM), dont certaines formes de WRED, peuvent réduire certaines congestions en abandonnant ou marquant des paquets avant que la file soit pleine. Ils sont parfois utiles pour des classes de données ou de vidéo adaptative.

Ils ne doivent pas être appliqués indistinctement à l'audio prioritaire. La compatibilité et le comportement exact varient selon l'équipement et sa version ; vérifier la documentation de la plateforme.

## 9. Fragmentation et liens à faible débit

Sur un lien très lent, la transmission d'un grand paquet de données peut bloquer momentanément un petit paquet vocal : c'est le délai de sérialisation. Des techniques de fragmentation et d'entrelacement de liens, ou une optimisation adaptée au transport, ont historiquement aidé sur certains liens étroits.

Sur les réseaux modernes à haut débit, l'intérêt peut être faible ou les mécanismes peuvent ne plus être disponibles. Ne pas activer une fonction ancienne sans vérifier le type de circuit, la plateforme et l'impact sur le chemin.

# Partie III — Dimensionnement voix et vidéo

## 10. Calculer la capacité à partir des flux

La méthode doit annoncer clairement les hypothèses : nombre de sessions simultanées, codec, paquetisation, IPv4/IPv6, RTP/UDP, Ethernet/VLAN, tunnel, SRTP, encapsulation WAN et direction du trafic.

Exemple de référence pour G.711, 20 ms, IPv4 sans options :

- charge audio : 64 kbit/s, soit 160 octets par paquet de 20 ms ;
- RTP/UDP/IPv4 : 12 + 8 + 20 = 40 octets ;
- charge totale IP : 200 octets par paquet ;
- fréquence : 50 paquets/s ;
- débit IP : 200 × 8 × 50 = 80 kbit/s par sens.

Le débit sur le support sera plus élevé avec les en-têtes de couche 2, l'encapsulation WAN et les tunnels. Pour un dimensionnement préliminaire, un facteur simplifié peut aider, mais la mise en production nécessite les détails de la liaison.

### 10.1 Exemple de capacité audio

Un site prévoit 45 appels G.711 simultanés. On retient, à titre pédagogique seulement, 100 kbit/s par appel et par sens pour inclure les surcharges usuelles :

`45 × 100 kbit/s = 4,5 Mbit/s par sens`

Si l'on ajoute une marge de dimensionnement de 20 % :

`4,5 × 1,20 = 5,4 Mbit/s par sens`

Ce budget ne comprend pas automatiquement la vidéo, la signalisation, les autres classes ou les surcharges propres au transport. La marge doit être justifiée par des mesures, et non utilisée comme remplacement d'une analyse de trafic.

### 10.2 Calculer une classe prioritaire

Une classe prioritaire doit être dimensionnée pour la simultanéité attendue et le profil réel, avec une marge contrôlée. Si le nombre d'appels dépasse la capacité de la classe, des pertes peuvent apparaître même si le reste du lien est peu utilisé. Il faut envisager une capacité adéquate, le contrôle d'admission d'appels lorsque disponible, ou une réduction du trafic concurrent.

## 11. QoS vidéo interactive

La vidéo a un débit plus variable que l'audio. Il faut connaître la plateforme, les résolutions, la fréquence d'image, le codec, le partage d'écran, les fonctions de caméra et le nombre maximal de participants par site.

AF41 est souvent utilisé pour des flux de conférence, mais ce n'est pas une obligation universelle. Certains environnements utilisent d'autres classes définies par le constructeur. Il faut éviter que tout le trafic vidéo se retrouve dans une classe audio prioritaire, et vérifier que les systèmes interprètent le même DSCP de bout en bout.

Les sessions adaptatives peuvent réduire le débit ou la résolution face à la perte. Une vidéo qui se dégrade peut donc indiquer une congestion même lorsque le flux continue à fonctionner.

## 12. QoS et Call Admission Control (CAC)

La QoS détermine comment les paquets présents sont traités. Le CAC décide si une nouvelle session peut être admise en fonction des ressources ou des règles. Ce sont deux mécanismes complémentaires.

Une politique QoS ne garantit pas qu'il n'y aura jamais trop d'appels. Le CAC peut réduire le risque de dépasser un budget prévu ; la QoS traite ensuite les paquets admis, particulièrement en cas de concurrence ou de congestion.

# Partie IV — Wi-Fi, VPN et WAN

## 13. Voix sur Wi-Fi

Wi-Fi ajoute un médium partagé, des retransmissions, de la contention radio, des changements de point d'accès et parfois des clients à faible débit. Le DSCP IP peut être mappé en catégorie d'accès Wi-Fi WMM : voix, vidéo, meilleur effort ou arrière-plan. Ce mapping dépend du contrôleur, du point d'accès et de la configuration.

À vérifier :

- couverture et rapport signal/bruit ;
- utilisation du canal et contention ;
- pertes et retransmissions ;
- mapping DSCP vers WMM/UP ;
- roaming et délais de transition ;
- politiques d'admission et capacité radio ;
- coexistence de terminaux anciens et récents.

Un paquet marqué EF côté IP ne garantit pas une transmission radio dans une catégorie voix si le mapping ou les règles de confiance ne le permettent pas.

## 14. QoS à travers les VPN et les tunnels

Un tunnel ajoute un en-tête externe et peut masquer le paquet intérieur. Il faut savoir si le DSCP interne est copié dans l'en-tête externe, s'il est réécrit au point de sortie et si le réseau intermédiaire respecte ce marquage.

Ne présume pas que la QoS intérieure traverse automatiquement le tunnel. Vérifier le comportement du VPN, les règles de copie DSCP, les files du sous-réseau et la manière dont le point distant restaure ou traite les classes.

## 15. Interconnexion avec un fournisseur WAN

La politique QoS du client peut être remappée par l'opérateur en classes de service contractuelles. La table de mapping et le contrat (CIR, classes, limites, mesure du débit) doivent être documentés.

Exemple conceptuel :

```text
Client: EF / AF41 / CS0
       |
       v
[frontière client : validation + shaping]
       |
       v
[réseau opérateur : mapping vers classes du service]
       |
       v
[site distant : mapping vérifié + files de sortie]
```

Un marquage correct côté campus ne protège pas le flux si le fournisseur le traite en best effort, si la classe dépasse ses limites ou si les mêmes règles ne sont pas appliquées sur le chemin retour.

# Partie V — Atelier de configuration conceptuelle Cisco IOS/IOS XE

## 16. Avant d'écrire les commandes

Le fragment suivant est un exemple pédagogique de politique par classes sur un routeur. La syntaxe précise, les capacités de nesting, les pourcentages autorisés, la prise en charge du matériel et les commandes de vérification changent selon IOS/IOS XE et la plateforme. Valider le modèle dans la documentation correspondant à l'équipement ; ne pas le coller dans un réseau de production sans revue.

Exemple conceptuel de classification :

```text
class-map match-any REALTIME-VOICE
 match ip dscp ef
!
class-map match-any VIDEO-CONFERENCE
 match ip dscp af41
!
class-map match-any CALL-SIGNALING
 match ip dscp cs3
 match ip dscp cs5
!
```

Cette classification accepte CS3 et CS5 pour illustrer une migration ou une politique mixte. Dans une politique de production, choisir la convention réellement utilisée plutôt que conserver inutilement les deux.

Exemple conceptuel de politique enfant :

```text
policy-map WAN-CHILD
 class REALTIME-VOICE
  priority percent 15
 class VIDEO-CONFERENCE
  bandwidth percent 25
 class CALL-SIGNALING
  bandwidth percent 5
 class class-default
  fair-queue
```

Les valeurs 15/25/5 sont fictives et ne constituent pas une recommandation de dimensionnement. La classe voix nécessite un plafond adapté au matériel et au nombre d'appels. Sur de nombreuses plateformes, `priority` implique un traitement et une action sur l'excès dont les détails sont spécifiques à la version.

Pour un parent shaper, un modèle possible sur les plateformes compatibles est :

```text
policy-map WAN-PARENT
 class class-default
  shape average <debit-cible-en-bit-par-seconde>
  service-policy WAN-CHILD
```

`<debit-cible-en-bit-par-seconde>` est un placeholder à remplacer par une valeur validée ; ce fragment ne se copie pas tel quel. Certaines plateformes utilisent une syntaxe ou des contraintes différentes.

### 16.1 Vérifier la politique

Commandes de consultation usuelles, à confirmer sur la plateforme :

```text
show policy-map interface
show interfaces <interface>
show interfaces counters errors
show class-map
show policy-map
```

Examiner les paquets par classe, octets, drops, débit, actions de police, shaping et compteurs de file. La présence d'une politique dans la configuration n'est pas la preuve qu'elle s'applique à la bonne interface et dans la bonne direction.

# Partie VI — Laboratoires guidés

## 17. TP 1 — Écrire la matrice QoS d'une entreprise

### Scénario

Trois sites partagent un WAN. Ils utilisent téléphones IP, visioconférences et applications de gestion. Le service réseau reçoit des plaintes pendant les sauvegardes nocturnes.

### Travail demandé

1. Définir 5 à 7 classes utiles au maximum.
2. Proposer les marquages selon une seule politique cohérente.
3. Identifier les sources fiables et non fiables.
4. Décrire le traitement attendu sur une interface de sortie WAN congestionnée.
5. Définir trois mesures d'acceptation.

### Correction possible

- Audio : EF, classe temps réel plafonnée.
- Signalisation : CS3 ou CS5 selon la politique retenue, capacité assurée sans priorité audio stricte.
- Vidéo interactive : AF41 ou classe documentée par la plateforme, capacité pondérée.
- Applications métier : classes selon criticité mesurée.
- Données générales : CS0, partage du reste.
- Gestion réseau : classe spécifique uniquement pour le trafic autorisé.

Placer la frontière de confiance sur les ports et équipements gérés. Reclassifier les terminaux non fiables. Mesurer les pertes/gigue RTP, les drops par classe et la continuité des applications métier pendant les charges représentatives.

## 18. TP 2 — Vérifier la confiance et le mapping DSCP/CoS

### Procédure

1. Capturer ou générer un flux audio dans un laboratoire autorisé.
2. Lire DSCP au terminal.
3. Lire DSCP ou CoS après le switch d'accès.
4. Lire le marquage sur le lien routé suivant.
5. Comparer avec le mapping documenté.
6. Répéter avec un paquet d'un terminal non fiable marqué artificiellement EF.

### Questions

- Le marquage est-il préservé ?
- Où se trouve la limite de confiance ?
- Un terminal non géré peut-il imposer sa propre priorité ?
- Quel équipement modifie la valeur éventuelle ?

### Correction attendue

Le système doit préserver les classes autorisées provenant des sources fiables et reclassifier ou limiter les sources non fiables. Si la valeur change, isoler l'étape en comparant des captures et des compteurs à proximité des frontières. Une simple valeur EF dans une capture n'est pas une preuve d'un traitement prioritaire.

## 19. TP 3 — Calculer et dimensionner une classe voix

Une interface WAN a un débit réel de 15 Mbit/s dans chaque sens. L'entreprise prévoit jusqu'à 35 appels G.711 simultanés, et retient 100 kbit/s par appel et par sens pour un budget préliminaire.

1. Calculer le budget des appels.
2. Calculer le budget avec 20 % de marge.
3. Expliquer les autres données à prendre en compte avant de fixer le plafond LLQ.

### Correction

Base : 35 × 100 kbit/s = 3,5 Mbit/s. Avec 20 % : 4,2 Mbit/s. C'est un budget préliminaire, pas automatiquement la valeur de la file prioritaire. Ajouter les autres flux audio, la façon dont le fournisseur mesure le débit, les en-têtes, la vidéo, le signalement, les pointes, le contrôle d'admission et le comportement lors d'une perte de lien. Vérifier aussi la capacité du matériel à traiter la classe.

## 20. TP 4 — Diagnostiquer une voix dégradée sur WAN

### Symptômes

Les appels internes d'un site sont bons. Les appels vers un autre site sont hachés seulement pendant les transferts de fichiers. Le DSCP EF est visible sur le téléphone source.

### Plan de diagnostic

1. Comparer RTP dans les deux sens et identifier où apparaissent pertes/gigue.
2. Examiner l'utilisation du WAN et les drops de sortie.
3. Vérifier que la politique est attachée au bon lien, dans la bonne direction.
4. Contrôler le DSCP à la sortie du routeur et au point distant.
5. Examiner shaping et policing, y compris la classe des transferts de fichiers.
6. Répéter lors d'une faible charge et documenter la différence.

### Correction attendue

Une cause plausible est que la congestion se produit dans la file de sortie ou chez le fournisseur, tandis que EF n'est pas traité comme attendu. Autres causes possibles : classe prioritaire sous-dimensionnée, DSCP remappé, shaping non aligné sur le débit réel ou chemin retour différent. La cause doit être prouvée par compteurs et captures, non déduite d'une seule observation.

## 21. TP 5 — Concevoir une validation avant mise en production

Établir une courte campagne de test : appel audio témoin, visioconférence, transfert de données, test pendant congestion contrôlée, test de panne de lien si autorisé. Consigner avant/après : latence, gigue, pertes, débit, drops, utilisation de file, DSCP, MOS si disponible, et impact sur les données.

**Critère de réussite :** les flux temps réel respectent les objectifs définis sous la charge attendue et les classes non prioritaires conservent une capacité acceptable.

# Partie VII — Méthode de troubleshooting intermédiaire

## 22. Lire correctement les compteurs

- **Drops de classe** : paquets supprimés par une file ou une action de police ; vérifier la période et les compteurs cumulés.
- **Drops d'interface** : congestion ou problème de ressources plus global ; corréler avec la classe.
- **Errors/CRC** : souvent couche physique, câblage, optique ou interface ; QoS n'est pas la première correction.
- **DSCP inattendu** : classification, trust boundary ou rewriting possible.
- **Utilisation moyenne faible avec plaintes** : examiner les pointes, la direction retour, le Wi-Fi, les microbursts et les composants hors du point de mesure.
- **Mesure RTP correcte mais perception mauvaise** : vérifier terminal, codec, suppression d'écho, buffers, jitter buffer, charge CPU et application de collaboration.

## 23. Arbre de décision

```text
Appel établi ?
  |-- NON --> signalisation, dial plan, admission, sécurité ; vérifier la QoS seulement si la congestion empêche l'établissement
  |
  +-- OUI --> média bon dans les deux sens ?
                |-- NON --> RTP/UDP, chemin asymétrique, pare-feu/NAT, ports et ressources média
                |
                +-- OUI au départ, mauvais sous charge --> pertes/gigue/drops, files, shaping, mapping DSCP/CoS
```

Cet arbre est un point de départ : un problème peut avoir plusieurs causes simultanées.

# Partie VIII — Exercices corrigés

## Exercice 1 — Classer audio et vidéo

**Question :** Pourquoi ne faut-il pas placer automatiquement audio et vidéo dans la même file prioritaire stricte ?

**Correction :** La vidéo consomme souvent un débit plus élevé et plus variable. Si elle partage une classe prioritaire illimitée ou mal plafonnée avec la voix, elle peut monopoliser la capacité. Une conception courante protège l'audio avec une classe contrôlée et attribue à la vidéo une classe distincte et dimensionnée.

## Exercice 2 — Marquage non fiable

**Question :** Un PC utilisateur émet un téléchargement marqué EF. Que faut-il faire ?

**Correction :** Ne pas faire confiance au marquage d'une source non autorisée. Classifier selon la politique d'accès et réécrire le DSCP ou appliquer un traitement approprié à la frontière de confiance. Vérifier la conséquence dans les files.

## Exercice 3 — Signification du shaping

**Question :** Le shaping supprime-t-il nécessairement les paquets excédentaires ?

**Correction :** Il met normalement les paquets en attente pour lisser le débit, jusqu'aux limites du tampon et du comportement de la plateforme. Un débordement peut néanmoins entraîner des pertes. Le policing, lui, peut marquer ou supprimer l'excès directement.

## Exercice 4 — Calcul d'une classe voix

**Question :** 50 appels × 100 kbit/s dans un sens. Quel budget avec 15 % de marge ?

**Correction :** 50 × 100 = 5 000 kbit/s = 5 Mbit/s. Avec 15 % : 5 × 1,15 = 5,75 Mbit/s dans un sens. Vérifier les hypothèses et autres trafics avant de fixer une politique.

## Exercice 5 — Le mapping L2/L3

**Question :** Un paquet a CoS 5, mais DSCP 0 après routage. Est-ce forcément une anomalie ?

**Correction :** Pas forcément : le mapping dépend de la stratégie réseau et le tag L2 peut être retiré/récréé lors du routage. Mais si la politique attend EF de bout en bout et que le DSCP devient CS0, il faut déterminer si la traduction est voulue ou constitue une erreur.

## Exercice 6 — Wi-Fi

**Question :** Pourquoi DSCP EF ne garantit-il pas la priorité radio ?

**Correction :** Le contrôleur ou le point d'accès doit mapper les valeurs IP vers les catégories WMM/UP et respecter la stratégie de confiance. Le partage radio, les retransmissions et le roaming continuent aussi d'influencer la qualité.

## Exercice 7 — QoS versus CAC

**Question :** Quelle différence entre QoS et contrôle d'admission d'appels ?

**Correction :** La QoS organise le traitement des paquets présents. Le CAC peut empêcher une session supplémentaire d'être admise lorsque les ressources ou la politique l'interdisent. Ils se complètent.

## Exercice 8 — Dégradation asymétrique

**Question :** L'utilisateur A entend B correctement, mais B entend A de façon hachée. Quelle démarche ?

**Correction :** Analyser séparément le média dans chaque direction, les chemins de routage, les drops et les marquages. Les politiques et congestions peuvent être asymétriques.

## Exercice 9 — Pourquoi une seule capture ne suffit-elle pas ?

**Correction :** Elle décrit le paquet au point de capture uniquement. Pour identifier une réécriture ou une perte, il faut comparer plusieurs points, horodatages, compteurs et flux dans le bon sens.

## Exercice 10 — Vidéo AF41

**Question :** AF41 est-il obligatoire pour toutes les vidéos d'entreprise ?

**Correction :** Non. C'est un marquage fréquent dans plusieurs recommandations, mais la plateforme et la politique locale peuvent définir d'autres marquages. La cohérence entre source, réseau et destination est essentielle.

# Partie IX — Défi final corrigé

## 24. Scénario

Une entreprise utilise un WAN de 15 Mbit/s par sens. Elle prévoit 35 appels voix simultanés, de la visioconférence et des transferts métier. Les appels sont bons en période calme mais perdent de la qualité sous charge. Les téléphones marquent EF, les terminaux vidéo AF41 et les données sont CS0. Le routeur d'accès applique une politique, mais les compteurs de sortie montrent des drops et l'opérateur ne confirme pas encore le mapping des classes.

### Missions

1. Calculer un budget voix provisoire avec une hypothèse de 100 kbit/s par appel et par sens et une marge de 20 %.
2. Rédiger une matrice de classes et le traitement prévu.
3. Définir une liste des éléments à obtenir du fournisseur WAN.
4. Proposer un plan de test avant et après correction.
5. Définir les conditions qui imposeraient une augmentation de capacité plutôt qu'un simple changement QoS.

## 25. Correction détaillée

### 1. Budget voix

35 × 100 kbit/s = 3,5 Mbit/s par sens. Avec 20 % : 4,2 Mbit/s par sens. C'est une première estimation ; elle ne fixe pas seule le plafond LLQ et n'inclut pas automatiquement les autres flux temps réel.

### 2. Matrice proposée

- Audio : EF, classe à faible latence et plafond déterminé par le nombre de sessions et la capacité réelle.
- Vidéo : AF41 ou classe validée par le fournisseur/plateforme, avec traitement pondéré et capacité vérifiée.
- Signalisation : CS3 ou CS5 selon la politique unique adoptée, débit assuré.
- Données : CS0 ou classes métier définies selon les besoins.
- Contrôle réseau : classes réservées aux protocoles réellement autorisés.

Reclassifier les sources non fiables et documenter le mapping d'entrée/sortie.

### 3. Questions au fournisseur

Obtenir le débit contractuel effectif, les profils de burst, la façon de compter les en-têtes, les classes disponibles, le mapping des DSCP, les règles de remarking/policing, les objectifs de SLA, les compteurs accessibles et les différences éventuelles entre sens aller et retour. Confirmer si le shaping client doit être placé sous le débit contractuel et selon quelle méthode.

### 4. Tests

Capturer RTP et DSCP aux frontières ; mesurer pertes, gigue et délai ; surveiller les drops par classe et par interface ; générer une charge contrôlée qui reproduit le scénario ; valider les appels et la vidéo ; mesurer l'impact sur les applications métier ; comparer dans les deux sens ; conserver les valeurs avant/après.

### 5. Quand augmenter la capacité ?

Si la charge soutenue dépasse la capacité réellement disponible, si la classe voix est correctement dimensionnée mais reste saturée à la simultanéité prévue, si le contrat WAN ne peut offrir les garanties nécessaires ou si les objectifs restent hors tolérance malgré une politique correcte, il faut envisager capacité supplémentaire, réduction de charge, adaptation des codecs/profils ou contrôle de sessions. La QoS ne crée pas de ressources.

## 26. Critères de réussite

Tu dois être capable de présenter une politique cohérente, justifier le plafond voix, identifier la frontière de confiance, demander les informations nécessaires au fournisseur et valider les changements avec des mesures objectives.

# Glossaire

- **AQM** : gestion active des files d'attente.
- **AF** : groupe de classes DiffServ avec différents niveaux de précédence d'abandon.
- **CBWFQ** : mise en file pondérée par classes.
- **CAC** : contrôle d'admission de nouvelles sessions.
- **DSCP** : code de classe dans le champ DiffServ de l'en-tête IP.
- **LLQ** : mécanisme de file prioritaire à faible latence.
- **PCP/CoS** : priorité de couche 2 dans le tag VLAN 802.1Q.
- **Policing** : mesure du débit avec action sur le dépassement.
- **Shaping** : lissage du trafic par tamponnage.
- **Trust boundary** : frontière où les marquages reçus sont acceptés, vérifiés ou réécrits.
- **WMM** : mécanismes de QoS du Wi-Fi basés sur des catégories d'accès.

# Références techniques

- IETF, [RFC 4594 — Configuration Guidelines for DiffServ Service Classes](https://www.rfc-editor.org/rfc/rfc4594.html).
- IETF, [RFC 2474 — Definition of the Differentiated Services Field](https://www.rfc-editor.org/rfc/rfc2474.html).
- IETF, [RFC 3246 — An Expedited Forwarding PHB](https://www.rfc-editor.org/rfc/rfc3246.html).
- Cisco, [Quality of Service Configuration Guide — Catalyst 9400 IOS XE 17.15](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9400/software/release/17-15/configuration_guide/qos/b_1715_qos_9400_cg.pdf).
- Cisco, [Video Quality of Service Tutorial](https://www.cisco.com/c/en/us/support/docs/quality-of-service-qos/qos-video/212134-Video-Quality-of-Service-QOS-Tutorial.pdf).
- Cisco, [Configuring Voice VLANs — Catalyst 9300 IOS XE 17.17](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-17/configuration_guide/vlan/b_1717_vlan_9300_cg/configuring_voice_vlans.html).

Les exemples de configuration sont illustratifs. Vérifie la documentation exacte de la plateforme et de la version, ainsi que les objectifs de service et la convention QoS de ton organisation, avant une mise en production.
