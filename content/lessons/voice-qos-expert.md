# QoS Voix et Vidéo — Expert

## Mise en contexte : garantir le comportement temps réel dans une architecture complexe

Une architecture de collaboration d'entreprise peut traverser des commutateurs d'accès, un réseau de campus, le Wi-Fi, des tunnels VPN, des liens WAN opérateur, des réseaux MPLS ou SD-WAN, des SBC et plusieurs plateformes de collaboration. Chaque domaine peut interpréter, modifier ou ignorer les marquages QoS. La congestion peut se produire sur un seul sens, à un seul saut ou seulement pendant quelques millisecondes, ce qui rend les moyennes globales insuffisantes.

Le niveau expert vise à concevoir, mesurer, sécuriser et dépanner le comportement QoS complet. Il faut comprendre non seulement les marquages, mais aussi les limites du matériel, les files et leurs buffers, l'encapsulation, les contrats opérateur, les mécanismes Wi-Fi, les effets de microburst et les interactions entre politiques.

> **Principe d'ingénierie :** définir des objectifs par classe et par domaine, maîtriser les frontières de confiance et la congestion, puis vérifier les comportements réellement appliqués par les équipements et les fournisseurs.

## 1. Compétences visées

À la fin de ce cours, tu sauras :

- concevoir une architecture QoS de bout en bout sur LAN, WLAN, VPN, WAN, MPLS et SD-WAN ;
- définir une taxonomie DSCP et ses mappings vers CoS/PCP, WMM et classes opérateur ;
- dimensionner une file à faible latence et analyser les risques de surallocation ;
- différencier limites de shaping, policing, remarking et comportement des files ;
- analyser les effets des encapsulations, du MTU, des microbursts et de la sérialisation ;
- établir une stratégie de mesure corrélant RTP, captures, queues et SLA ;
- diagnostiquer les incidents multi-domaines et asymétriques ;
- sécuriser les marquages face aux terminaux non fiables et à la fraude ;
- rédiger un plan de mise en production, de tests, de retour arrière et d'amélioration continue.

# Partie I — Modèle de service et objectifs quantifiés

## 2. Définir des SLO par classe

Avant de configurer QoS, définir des objectifs observables et associés à des conditions précises :

- délai unidirectionnel ou aller-retour, en précisant la méthode de mesure ;
- gigue, en précisant la métrique utilisée ;
- perte de paquets, y compris les périodes de pic ;
- disponibilité et taux de réussite des sessions ;
- comportement sous charge normale, pointe et incident ;
- mesures de qualité applicative (par exemple MOS estimé, statistiques RTP, résolution/fréquence d'image) si disponibles.

Ne pas déclarer qu'un service respecte un SLA uniquement parce que la moyenne quotidienne est bonne. Les microbursts, la congestion localisée et les pertes courtes peuvent fortement dégrader l'expérience sans faire exploser une moyenne d'utilisation.

### 2.1 Distinguer KPI et cause

MOS, perte RTP ou gigue sont des indicateurs de résultat. Drops de file, drops de police, erreurs physiques, DSCP et utilisation sont des indices de cause. Une bonne investigation corrèle les deux avec le même intervalle de temps et le même sens de communication.

## 3. Construire une taxonomie de classes stable

La stratégie doit rester gérable à l'échelle de l'organisation. Trop de classes entraînent une complexité de mapping et des erreurs. Trop peu de classes fusionnent des trafics ayant des profils incompatibles.

Exemple de taxonomie de référence, à adapter :

| Nom logique | Marquage fréquemment utilisé | Objectif de traitement | Garde-fou |
|---|---|---|---|
| Voix interactive | EF (46) | faible latence et faible perte | admission/conformité, plafond strictement dimensionné |
| Signalisation de collaboration | CS3 ou CS5 selon convention | livraison fiable, débit suffisant | classer uniquement la signalisation autorisée |
| Vidéo de conférence | AF41 ou valeur du fournisseur | capacité pondérée, adaptation possible | limite et surveillance du débit par classe |
| Média immersif spécialisé | parfois CS4 | profil de temps réel documenté | ne pas fusionner sans analyse avec voix ou vidéo générale |
| Applications métier sensibles | classe AF/CS propre au domaine | objectifs selon SLO applicatif | approbation propriétaire de service |
| Données générales | CS0/DF | meilleur effort | évitement de famine, partage équitable |
| Contrôle réseau | marquages réservés par politique | protéger les fonctions réseau légitimes | filtrage strict de la source et des protocoles |

Cette matrice n'est pas une norme universelle. RFC 4594, les guides constructeurs et les plateformes de collaboration ne proposent pas toujours exactement les mêmes marquages pour la signalisation et la vidéo. Le concepteur doit choisir une convention par domaine, documenter toute traduction et tester le comportement après re-marking. Les trafics de contrôle réseau ne doivent jamais être confiés aux applications utilisateur.

# Partie II — Frontières de confiance et sécurité de la QoS

## 4. Marquage : accepter, normaliser ou réécrire

Le DSCP reçu doit être considéré comme une indication, pas comme une preuve d'autorisation. Tout terminal peut, dans certains environnements, émettre arbitrairement une valeur DSCP. Un attaquant ou un logiciel mal configuré pourrait essayer d'obtenir une priorité supérieure.

Un modèle de confiance explicite distingue :

1. **Port terminal géré** : confiance conditionnelle après identification de l'appareil, avec politique cohérente pour les paquets téléphone et PC derrière téléphone.
2. **Port utilisateur ou invité non fiable** : classifier par politique d'accès, réécrire le marquage ou limiter les classes autorisées.
3. **Trunk et uplink interne** : conserver seulement les classes prévues, vérifier la cohérence des mappings.
4. **Frontière WAN/VPN/opérateur** : valider les classes autorisées, les limites contractuelles et les opérations de remarking.
5. **Sortie vers l'Internet public** : ne pas présumer que les marquages seront conservés ou respectés au-delà du domaine administré.

### 4.1 Principe du moindre privilège QoS

- N'autoriser EF qu'aux flux audio conformes et identifiés.
- Contrôler la signalisation par source/destination/protocole selon la plateforme ; ne pas faire confiance à tous les paquets seulement parce qu'ils portent CS3/CS5.
- Éviter d'accorder des classes réseau critiques à des terminaux.
- Utiliser des compteurs et alertes lorsque la quantité de trafic dans une classe dépasse l'enveloppe attendue.
- Tester les cas où les marquages sont absents, erronés ou malveillants.

## 5. Concevoir le mapping inter-domaines

### 5.1 DSCP vers CoS/PCP

DSCP utilise six bits dans l'en-tête IP ; PCP/CoS utilise trois bits dans une trame VLAN 802.1Q. Une conversion est donc une décision de politique, pas une correspondance mathématique exacte. Un système doit savoir comment traiter les classes DSCP quand il recrée l'en-tête de couche 2 et comment réagir aux combinaisons incohérentes.

### 5.2 DSCP vers WMM/UP en Wi-Fi

Le réseau sans fil peut mapper DSCP ou priorité utilisateur en catégories d'accès WMM (voix, vidéo, meilleur effort, arrière-plan). Vérifier ce mapping ainsi que les règles de confiance côté contrôleur et point d'accès. La priorité radio améliore le traitement relatif, mais elle n'ajoute pas de capacité au canal et ne supprime pas les effets d'interférence, de retransmission ou de roaming.

### 5.3 DSCP dans les tunnels

Un paquet encapsulé possède un en-tête externe et un en-tête intérieur. Selon le type de tunnel, le DSCP externe peut être copié, fixé ou calculé à partir du paquet intérieur. La politique de sortie peut ensuite restaurer ou réécrire le DSCP interne.

Pour les VPN IPsec, GRE, VXLAN et les tunnels SD-WAN, documenter :

- quelle valeur est visible dans le sous-réseau underlay ;
- comment est effectuée la copie/propagation du DSCP ;
- si une politique applique le remarking au point d'encapsulation/décapsulation ;
- les surcharges MTU et effets possibles de fragmentation ;
- les files et compteurs applicables au paquet externe.

### 5.4 MPLS et classes opérateur

Les réseaux MPLS peuvent utiliser le champ Traffic Class (TC), historiquement appelé EXP, pour sélectionner un comportement de transfert dans le domaine du fournisseur. Le mapping entre DSCP IP et TC MPLS est propre à la politique et au service opérateur. Il ne faut pas supposer que EF IP est automatiquement transporté dans une classe prioritaire MPLS.

Exiger la documentation du fournisseur : classes, mapping, règles de police, débit garanti, enveloppe de rafale, objectifs de perte/délai et mesures disponibles. Vérifier aussi le marquage à la sortie du domaine opérateur.

# Partie III — Ingénierie des files et capacité

## 6. Concevoir la classe voix à faible latence

Une file stricte ou LLQ limite le délai d'attente du trafic de voix tant qu'elle reste dans son profil et que le comportement de l'équipement le permet. Sa limite doit être calculée avec la simultanéité prévue, le codec, le packetization time, les en-têtes réels et la direction du lien.

**Risques d'une priorité surdimensionnée :** la classe peut évincer les autres classes, masquer une mauvaise classification et créer une instabilité en cas de trafic EF anormal. **Risques d'une priorité sous-dimensionnée :** drops de la classe, perte audio et gigue lors des pointes.

Le calcul de débit n'est qu'une partie du dimensionnement. Vérifier :

- la capacité physique et le débit réellement disponible ;
- la granularité de configuration et les limites de la plateforme ;
- la façon dont le matériel compte les octets (IP ou sur le fil) ;
- les en-têtes L2, VLAN, MPLS, tunnels et sécurité ;
- les pointes synchronisées et microbursts ;
- les autres flux autorisés dans la même classe ;
- le comportement de l'excès (drop, remarking ou autre action documentée).

## 7. Calcul de référence : G.711

Hypothèses pédagogiques : 64 kbit/s audio, paquetisation 20 ms, charge audio de 160 octets, RTP/UDP/IPv4 de 40 octets, donc 200 octets IP par paquet et 50 paquets/s.

`200 × 8 × 50 = 80 000 bit/s = 80 kbit/s IP par sens`

La charge sur le lien est supérieure après Ethernet, VLAN, préambule, intervalle inter-trame, tunnels et encapsulations. Une estimation d'environ 90–100 kbit/s par appel et par sens est couramment employée pour illustrer un G.711/20 ms sur Ethernet, mais elle ne remplace pas le calcul lié au transport et à la méthode de comptage réels.

Pour N appels simultanés :

`Débit initial par sens ≈ N × débit estimé par appel`

Puis ajouter les autres flux temps réel, les marges justifiées, les surcharges et la stratégie de récupération en cas de panne. Ne pas fixer le plafond LLQ uniquement d'après un pourcentage de bande passante si le débit parent ou la taille du circuit est mal connue.

## 8. Shaping parent, classes enfants et contrat opérateur

Dans les architectures où le routeur peut façonner le trafic au débit réel du circuit, une politique hiérarchique peut utiliser :

- un shaper parent pour maîtriser le débit total de sortie ;
- des classes enfants qui distribuent la capacité entre voix, vidéo, signalisation et données ;
- une file prioritaire plafonnée pour la voix ;
- une classe vidéo pondérée ou garantie ;
- des politiques de policing/remarking aux entrées de domaines.

Le shaper doit être aligné avec le circuit réellement livré et la façon dont l'opérateur compte le débit. S'il est trop haut, les files peuvent se former chez le fournisseur, hors du contrôle du client. S'il est trop bas, il gaspille de la capacité. Les marges doivent être mesurées, pas choisies arbitrairement.

### 8.1 Policing et shaping ne sont pas interchangeables

Le policing mesure le profil et peut marquer ou supprimer l'excès. Le shaping met le trafic en tampon pour lisser la sortie, avec un risque de drop si le tampon déborde. Placer un policer agressif sur des paquets de média peut directement provoquer de la perte RTP. Placer un shaper sur un lien avec un tampon inadapté peut augmenter délai et gigue.

## 9. Congestion, microbursts et buffers

Une interface dont l'utilisation moyenne est de 20 % peut quand même connaître des pointes brèves assez fortes pour remplir une file. Les systèmes de supervision qui agrègent sur 1 ou 5 minutes peuvent masquer ces événements.

Examiner :

- les drops et les compteurs de file à un intervalle aussi fin que possible ;
- les buffers partagés et réservés, selon la plateforme ;
- les débits en rafale d'applications de sauvegarde et de stockage ;
- l'effet de l'oversubscription des ports d'accès/uplinks ;
- les changements de priorité lors de la traversée d'un ASIC ou d'un fabric ;
- l'écart entre compteurs matériel et compteurs logiciels.

Les détails de files, de partage de buffers et de comptage sont spécifiques au matériel. Ne transpose pas une intuition construite sur un routeur à un switch ASIC ou à un contrôleur sans vérifier la documentation.

## 10. Vidéo et autres flux adaptatifs

La vidéo interactive produit des débits variables ; les codecs adaptatifs peuvent ajuster la résolution, le débit ou la fréquence d'image en fonction de la perte et des estimations de capacité. Une classe vidéo pondérée peut être plus adaptée qu'une priorité stricte identique à celle de la voix.

La conception doit préciser si plusieurs profils vidéo coexistent, si le partage d'écran est séparé du média caméra, si la plateforme modifie ses marquages et comment les flux de médias sont identifiés. AF41 est fréquent dans plusieurs guides, mais la classe à retenir dépend de la politique et de la plateforme. Documenter tout usage de CS4 ou d'autres valeurs particulières.

# Partie IV — Wi-Fi et mobilité

## 11. La QoS Wi-Fi ne résout pas tous les problèmes radio

Le Wi-Fi est un médium partagé. Les catégories WMM influencent la contention, mais n'accordent pas une bande passante garantie indépendante de l'occupation du canal. Un client avec un mauvais signal peut occuper le médium plus longtemps, et un roaming peut interrompre brièvement les paquets temps réel.

Lors d'un incident de voix Wi-Fi, corréler :

- RSSI/SNR et taux de modulation ;
- occupation du canal et sources d'interférence ;
- retransmissions et taux de perte radio ;
- catégorie WMM et mapping DSCP/UP ;
- capacité/admission radio, itinérance et délais de transition ;
- congestion du réseau filaire en aval.

Ne pas corriger une dégradation radio uniquement en augmentant la priorité IP. La QoS et la conception radio se complètent.

# Partie V — Mesure, observabilité et corrélation

## 12. Sources de données

Une investigation de niveau expert combine plusieurs plans de mesure :

1. **Terminal/plateforme collaboration** : statistiques RTP, pertes, gigue, jitter buffer, codec, MOS estimé, adaptation vidéo, qualité par participant.
2. **Capture paquet** : DSCP, taille, intervalle inter-paquets, séquence RTP, pertes apparentes, chemin et ports.
3. **Switch/routeur** : utilisation, erreurs, drops, queues par classe, polices, shaping, compteurs matériels.
4. **Wi-Fi** : retransmissions, catégorie d'accès, qualité radio, roaming.
5. **Fournisseur WAN** : classes réellement appliquées, drops de police, métriques SLA et incidents.
6. **Application/session** : heure d'établissement, succès d'appel, site, direction, participant et changements de route.

Synchroniser les horloges quand c'est possible. Une corrélation n'est fiable que si les observations se rapportent au même intervalle, au même flux et au même sens.

## 13. Méthode de dépannage multi-domaine

### Étape 1 — Définir l'impact

Identifier utilisateurs, sites, appareils, heure, application, appel interne/externe, symptômes unidirectionnels/bidirectionnels et dépendance à la charge. Recueillir un appel témoin.

### Étape 2 — Séparer contrôle et média

Vérifier l'établissement de la session et analyser le flux RTP/UDP dans les deux sens. La réussite SIP ne prouve pas la réussite média. Examiner aussi pare-feu/NAT, SBC et ressources média si le flux est absent.

### Étape 3 — Déterminer où commence la dégradation

Comparer les statistiques du terminal avec les captures/compteurs aux frontières d'accès, de campus, de tunnel et de WAN. Si les paquets arrivent bien au bord mais sont perdus à la sortie d'un routeur, concentrer l'analyse sur cette sortie ; si la perte commence dans le Wi-Fi, investiguer le domaine radio.

### Étape 4 — Examiner les marquages

Vérifier DSCP de source à destination, remapping CoS, WMM/UP, propagation tunnel, mapping MPLS/SD-WAN, policies et actions de remarking. La valeur vue à un seul point ne prouve pas le traitement effectif.

### Étape 5 — Examiner les files et le débit

Relever drops de classe, drops d'interface, utilisation, burst, police, shaping, queues, MTU et erreurs physiques. Déterminer si la congestion est continue ou impulsionnelle. Séparer congestion et défaut de couche physique.

### Étape 6 — Formuler puis tester une hypothèse

Effectuer une seule modification contrôlée, si possible en laboratoire ou sur une fenêtre validée. Conserver un retour arrière, répéter les mesures identiques et vérifier aussi les autres classes. Une amélioration audio au prix de l'arrêt des applications métiers ne constitue pas automatiquement une bonne conception.

# Partie VI — Modèles de configuration à examiner

## 14. Exemple conceptuel de stratégie hiérarchique

Le fragment ci-dessous illustre les concepts Cisco IOS/IOS XE. Les noms, valeurs, nesting, commandes prises en charge et comportements d'excès sont spécifiques aux plateformes et aux versions. Il faut lire le guide QoS du modèle exact et tester les commandes avant utilisation.

```text
class-map match-any REALTIME-VOICE
 match ip dscp ef
!
class-map match-any VIDEO-CONFERENCE
 match ip dscp af41
!
class-map match-any COLLAB-SIGNALING
 match ip dscp cs3
 match ip dscp cs5
!
policy-map WAN-CHILD
 class REALTIME-VOICE
  priority percent <pourcentage-voix-valide>
 class VIDEO-CONFERENCE
  bandwidth percent <pourcentage-video-valide>
 class COLLAB-SIGNALING
  bandwidth percent <pourcentage-signalisation-valide>
 class class-default
  fair-queue
!
policy-map WAN-PARENT
 class class-default
  shape average <debit-reel-valide-en-bit-par-seconde>
  service-policy WAN-CHILD
```

Les valeurs entre chevrons sont des placeholders, pas des commandes prêtes à exécuter. Les plateformes ne prennent pas toutes en charge la même syntaxe, la même hiérarchie ou les mêmes unités. Dans le plan final, choisir une convention de signalisation au lieu de conserver CS3 et CS5 sans raison.

Avant de déployer, répondre à ces questions :

- Quelle interface et quelle direction sont concernées ?
- Le shaper correspond-il au débit réellement livré et au comptage opérateur ?
- Le débit prioritaire suffit-il au pic d'appels attendu ?
- Quelle action intervient lorsque la classe dépasse son plafond ?
- Le mapping des classes vidéo et signalisation est-il cohérent en entrée et sortie ?
- Où les compteurs matériels montrent-ils réellement les drops ?
- La configuration a-t-elle été testée sur le modèle et la version concernés ?

## 15. Vérifications sur équipement

Selon la plateforme, les commandes usuelles peuvent inclure :

```text
show policy-map interface
show policy-map
show class-map
show interfaces <interface>
show interfaces counters errors
show running-config interface <interface>
```

Utiliser uniquement les variantes disponibles sur le système. Vérifier l'incrément des compteurs pendant un test, plutôt que lire des compteurs cumulés sans connaître leur historique. Une classe définie mais sans compteurs peut indiquer que la politique n'est pas appliquée, que la classification ne correspond à aucun paquet ou que les compteurs consultés ne sont pas ceux du matériel concerné.

# Partie VII — Laboratoires experts

## 16. TP 1 — Cartographier la QoS de bout en bout

### Scénario

Une réunion vidéo traverse un switch campus, un point d'accès Wi-Fi sur le site A, un tunnel SD-WAN et un réseau opérateur avant d'atteindre le site B. La voix fonctionne correctement, mais la vidéo perd en résolution pendant les sauvegardes.

### Travail demandé

1. Dessiner les domaines et frontières de confiance.
2. Pour chaque segment, noter le marquage attendu et la classe/file correspondante.
3. Identifier où le DSCP externe est défini pour le tunnel.
4. Définir les compteurs nécessaires sur chaque domaine.
5. Établir un ordre de captures afin d'isoler le premier point de dégradation.

### Correction possible

Établir une matrice contenant point de mesure, DSCP interne, DSCP externe, CoS/UP éventuel, classe de sortie, drops, délai/gigue et source de données. Capturer près de la source, à l'entrée/sortie du tunnel et à l'arrivée. Vérifier la file vidéo ainsi que la voix, les retransmissions radio et les files WAN. Si la vidéo est remappée en best effort ou policée à la frontière, la correction se trouve dans le mapping ou le profil de service, pas seulement dans le switch d'accès.

## 17. TP 2 — Investiguer une classe EF qui droppe

### Scénario

Un routeur affiche des drops sur la classe voix sous charge. La voix utilise G.711 avec une paquetisation de 20 ms ; le pic prévu est de 60 appels par sens. Le WAN est nominalement à 20 Mbit/s, mais le débit livré et la méthode de comptage opérateur ne sont pas documentés.

### Travail demandé

1. Estimer le débit IP G.711 et un budget sur le fil indicatif.
2. Calculer 60 appels à 100 kbit/s par sens.
3. Lister les informations manquantes avant de relever le plafond.
4. Déterminer les compteurs supplémentaires à collecter.

### Correction

Débit IP de référence : 80 kbit/s par appel et par sens sous les hypothèses du cours. Budget préliminaire sur le fil à 100 kbit/s : 6 Mbit/s par sens. Ce chiffre doit être confirmé avec les en-têtes, encapsulation, débit réellement disponible, autres flux, limites de la plateforme et profil contractuel. Relever drops LLQ, trafic conforme/excédentaire, shaping parent, drops physiques, utilisation en rafale, mapping DSCP et statuts RTP. Ne pas simplement augmenter le plafond : si la classe reçoit du trafic non vocal marqué EF, le classifier et le limiter d'abord.

## 18. TP 3 — Vérifier un tunnel et la propagation DSCP

### Procédure

1. Générer un flux autorisé avec DSCP connu dans un environnement de test.
2. Capturer le paquet intérieur avant encapsulation.
3. Capturer le paquet externe dans l'underlay.
4. Examiner DSCP interne et externe après décapsulation.
5. Répéter avec plusieurs classes définies.
6. Corréler avec les compteurs de files du transport.

### Résultat attendu

Un tableau précise la valeur intérieure/extérieure à chaque point, la transformation attendue et la preuve observée. Si la valeur externe n'est pas celle attendue, examiner la politique de copie/remarking du tunnel. Ne pas conclure à une perte de QoS uniquement à partir du DSCP extérieur : vérifier aussi la classe de file du réseau sous-jacent et les drops associés.

## 19. TP 4 — Corréler qualité RTP et compteurs réseau

### Scénario

Entre 10 h 00 et 10 h 15, les utilisateurs signalent une voix dégradée. Les statistiques de la plateforme montrent une augmentation de perte RTP et de gigue pour plusieurs appels d'un site.

### Étapes

1. Établir une ligne temporelle précise à partir des sessions touchées.
2. Relever les statistiques RTP et le chemin réseau de chaque appel.
3. Aligner les horloges et consulter les compteurs de files sur les interfaces correspondantes.
4. Comparer l'utilisation moyenne avec les drops/microbursts.
5. Examiner le sens retour séparément.
6. Écarter erreurs physiques et problème de point d'accès avant de modifier la QoS WAN.

### Correction

La cause la plus probable ne peut pas être déduite de la seule gigue RTP. Une corrélation temporelle entre drops sur une interface et perte RTP sur le même chemin donne une preuve plus forte. Si l'utilisation moyenne est faible mais que les drops augmentent, rechercher microbursts ou limite de buffer. Si aucune file ne droppe, étendre l'analyse aux segments non observés, au Wi-Fi, aux endpoints et au chemin retour.

## 20. TP 5 — Plan de déploiement et rollback

Rédiger un plan qui contient : hypothèse, impact, prérequis, capture de l'état initial, changement précis, fenêtre, tests de non-régression, critères d'arrêt, retour arrière, personnes responsables et collecte des preuves. Tester la politique sur le modèle et la version visés. Aucun changement ne doit être validé uniquement parce que la commande est acceptée par le CLI.

# Partie VIII — Études de cas

## 21. Cas 1 : EF est respecté au campus mais pas sur le WAN

**Observations :** capture EF sur le LAN ; paquets marqués CS0 après l'entrée opérateur ; la vidéo se dégrade également.

**Hypothèses :** remarking à la frontière, absence de classe dédiée dans le contrat, classification WAN fondée sur une autre valeur, ou politique mal appliquée.

**Démarche :** comparer captures juste avant/après la frontière, consulter la politique de service et les compteurs du fournisseur, vérifier les drops et le shaping. Corriger le mapping ou le profil contractuel, puis valider dans les deux sens. Ne pas augmenter la priorité au campus si la perte de classe se produit dans le domaine opérateur.

## 22. Cas 2 : qualité variable sur Wi-Fi alors que le WAN est sain

**Observations :** les appels filaires sont bons ; les appels Wi-Fi sont affectés dans une zone spécifique ; les files WAN ne montrent aucun drop.

**Hypothèses :** couverture insuffisante, canal saturé, retransmissions, mauvais mapping WMM, roaming ou client défectueux.

**Démarche :** comparer les métriques radio et RTP, vérifier DSCP vers WMM, examiner utilisation de canal et événements de roaming, tester le même terminal dans une autre zone et un terminal différent au même endroit. Une priorité IP plus élevée ne corrige pas un problème de couverture.

## 23. Cas 3 : drops EF alors que la classe reçoit trop de trafic

**Observations :** le taux de trafic EF est supérieur à la capacité estimée pour le nombre d'appels ; certains postes et serveurs sont autorisés à marquer EF.

**Hypothèses :** frontière de confiance trop large, applications incorrectement marquées, classe qui mélange audio et données, ou plafond trop bas pour la vraie simultanéité.

**Démarche :** classifier les flux EF par source/protocole, retirer la confiance des sources non gérées, réécrire les marquages non conformes et comparer le trafic voix réel au budget prévu. Ajuster le plafond uniquement après validation de la demande légitime. Surveiller l'impact sur les autres classes.

# Partie IX — Exercices corrigés

## Exercice 1 — DSCP à travers un tunnel

**Question :** Le paquet intérieur porte EF mais le paquet externe porte CS0. Est-ce toujours une panne ?

**Correction :** Pas nécessairement. Tout dépend de la politique de propagation et du traitement du sous-réseau underlay. Si le service exige que le transport priorise le trafic vocal, il faut vérifier la politique du tunnel et le mapping externe ; le DSCP intérieur ne garantit pas automatiquement la priorité underlay.

## Exercice 2 — Compteurs de drops

**Question :** L'interface affiche peu d'utilisation moyenne, mais la classe audio présente des drops. Donne trois pistes.

**Correction :** Microbursts masqués par l'agrégation, trafic EF non conforme qui dépasse le plafond, ou limite/partage de buffer spécifique au matériel. Vérifier aussi les compteurs de police et les fenêtres de mesure.

## Exercice 3 — Priorité stricte

**Question :** Pourquoi ne pas donner une priorité stricte à toutes les classes de collaboration ?

**Correction :** Parce que la vidéo et les flux de collaboration peuvent être volumineux ou variables. Ils pourraient évincer l'audio et les classes métier. Définir une file voix contrôlée et attribuer aux autres flux un traitement compatible avec leur profil.

## Exercice 4 — Mapping CoS/DSCP

**Question :** Quel problème crée un mapping CoS vers DSCP différent entre deux switches ?

**Correction :** Les paquets peuvent changer de classe à chaque frontière, ce qui produit une QoS incohérente et difficile à dépanner. La matrice de mapping doit être documentée, appliquée et vérifiée sur chaque chemin.

## Exercice 5 — Shaping trop élevé

**Question :** Pourquoi un shaper client configuré à 100 % du débit nominal peut-il laisser la congestion se produire chez le fournisseur ?

**Correction :** Le débit réel disponible peut être inférieur à la valeur nominale ou calculé avec un overhead différent. Si le client envoie au-delà du profil reçu, la file peut se former en dehors de sa politique QoS. Utiliser les paramètres et mesures du circuit réel.

## Exercice 6 — Wi-Fi WMM

**Question :** La classe IP est EF, mais le flux utilise la catégorie WMM Best Effort. Que vérifier ?

**Correction :** Mapping DSCP/UP, trust policy du contrôleur/AP, comportement du client, tags à l'entrée, règles WLAN et éventuel remarking. Vérifier avec les traces et compteurs radio plutôt que supposer que le mapping est automatique.

## Exercice 7 — Différence entre QoS et CAC

**Correction :** QoS décide comment les paquets en attente sont traités ; CAC peut limiter l'admission de nouvelles sessions en fonction de la capacité/politique. Ils sont complémentaires, particulièrement quand le nombre d'appels peut dépasser le budget.

## Exercice 8 — Signalisation CS3 ou CS5

**Question :** Quelle valeur est toujours correcte pour SIP ?

**Correction :** Il n'existe pas une valeur unique valable pour toutes les politiques. CS3 ou CS5 apparaissent dans différentes recommandations et environnements. Choisir la convention du domaine, vérifier la documentation du fournisseur et assurer le mapping de bout en bout.

## Exercice 9 — Dépannage asymétrique

**Question :** Pourquoi deux captures, une dans chaque sens, sont-elles importantes ?

**Correction :** Les routes, congestions, classes, interfaces et politiques peuvent être asymétriques. Une mesure correcte dans un sens ne garantit rien pour le retour.

## Exercice 10 — Besoin de capacité

**Question :** Une classe voix est correctement dimensionnée et configurée, mais la qualité reste mauvaise quand la demande soutenue dépasse la capacité totale. Que faire ?

**Correction :** Augmenter ou redimensionner la capacité, réduire/adapter le trafic concurrent, utiliser le CAC si disponible, ajuster les profils d'application ou revoir l'architecture. La QoS ne peut pas créer de bande passante.

# Partie X — Défi final corrigé

## 24. Scénario de synthèse

Une organisation possède quatre sites connectés en SD-WAN. Les téléphones utilisent G.711, les salles font de la vidéo, les postes utilisent VPN pour le télétravail et l'entreprise a une classe métier sensible. Les appels sont bons dans le campus, mais certaines réunions sont dégradées lorsque le trafic de sauvegarde démarre. Les captures montrent EF au téléphone et AF41 pour la vidéo ; cependant, les paquets externes du tunnel sont tous marqués CS0. Le fournisseur indique que la classe voix est contractuelle, mais ne fournit pas encore le détail du mapping ni des drops.

### Travail demandé

1. Dessiner la matrice des classes et les frontières de confiance.
2. Estimer le budget d'une pointe de 50 appels voix par sens à 100 kbit/s par appel, avec 20 % de marge.
3. Expliquer pourquoi les captures intérieures EF ne prouvent pas une priorité dans l'underlay.
4. Préparer cinq questions précises au fournisseur.
5. Proposer un plan de diagnostic et de validation.
6. Décrire les risques d'une priorité voix trop élevée ou accordée à des sources non fiables.

## 25. Correction détaillée

### 1. Matrice et frontières

Définir audio EF, vidéo dans la classe conforme au fournisseur/plateforme (AF41 si le design le retient), signalisation CS3 ou CS5 selon la convention, classe métier justifiée par son propriétaire, et données générales CS0. Les ports d'utilisateurs/terminaux non gérés restent non fiables ; les téléphones et équipements médias sont autorisés selon l'identité et les politiques. Documenter la confiance au campus, sur le tunnel, à la frontière opérateur et à la sortie distante.

### 2. Budget voix

50 × 100 kbit/s = 5 Mbit/s par sens. Avec 20 % de marge : 6 Mbit/s par sens. C'est une hypothèse de dimensionnement, non la valeur LLQ finale. Vérifier la simultanéité, les autres flux prioritaires, les surcharges du transport et le débit réellement livré.

### 3. DSCP interne versus externe

Le DSCP du paquet intérieur appartient au paquet encapsulé. Le sous-réseau de transport classe le paquet externe, dont le DSCP peut être copié, réécrit ou fixé par la politique SD-WAN/VPN. Si ce champ reste CS0 et que l'underlay ne dispose pas d'une autre information, il peut être traité comme best effort. Capturer et vérifier le mapping réel, puis consulter les classes/fichiers d'attente du transport.

### 4. Questions au fournisseur

- Quelle valeur DSCP/TC mappe vers la classe voix contractuelle ?
- Comment sont traités EF, AF41 et CS0 dans chaque direction ?
- Quels sont le débit garanti, le débit de pointe, la tolérance de rafale et l'overhead de comptage ?
- Quels compteurs de police, d'abandon et d'utilisation sont disponibles ?
- Quelles règles de remarking appliquent les points d'entrée/sortie du service ?
- Quels objectifs de délai, gigue et perte sont couverts par le contrat et comment sont-ils mesurés ?

### 5. Plan de diagnostic

Synchroniser les horloges ; collecter les statistiques RTP et vidéo de sessions identifiées ; capturer intérieur/extérieur aux deux extrémités ; relever les queues et drops campus/WAN ; vérifier le shaping et le profil de la classe voix ; reproduire une charge de sauvegarde autorisée ; modifier le mapping ou le profil dans une fenêtre contrôlée ; répéter les mêmes mesures ; vérifier aussi la classe métier et les transferts de données.

### 6. Risques

Une priorité trop élevée peut affamer les autres classes et rendre le réseau instable en cas de flux EF non conforme. Une confiance excessive permettrait à un poste ou à un logiciel de marquer ses données prioritaires. La réponse consiste à limiter la classe, valider les sources, classifier et remapper le trafic, surveiller les anomalies et maintenir des critères de non-régression.

## 26. Critères de réussite

La correction est réussie si elle démontre le chemin réel du marquage, relie les métriques applicatives aux compteurs réseau, respecte le profil opérateur et améliore la qualité sans dégrader de façon inacceptable les autres services.

# Glossaire

- **AQM** : gestion active de file d'attente.
- **AF** : classes DiffServ avec niveaux de précédence d'abandon.
- **CBWFQ** : ordonnancement pondéré par classes.
- **CAC** : contrôle d'admission de sessions.
- **CoS/PCP** : priorité de couche 2 dans le tag 802.1Q.
- **DSCP** : six bits de code de différenciation dans l'en-tête IP.
- **EF** : Expedited Forwarding, comportement de transfert couramment utilisé pour la voix interactive.
- **LLQ** : mécanisme de file prioritaire à faible latence.
- **Microburst** : pointe de trafic très courte pouvant remplir une file sans se refléter dans les moyennes.
- **MPLS TC** : champ Traffic Class de l'étiquette MPLS, historiquement appelé EXP.
- **Policing** : contrôle de débit pouvant marquer ou supprimer l'excès.
- **SLO/SLA** : objectif de service / engagement contractuel de service.
- **Shaping** : régulation du débit par mise en attente de paquets.
- **WMM** : mécanismes QoS du Wi-Fi utilisant des catégories d'accès.

# Références techniques

- IETF, [RFC 4594 — Configuration Guidelines for DiffServ Service Classes](https://www.rfc-editor.org/rfc/rfc4594.html).
- IETF, [RFC 2474 — Definition of the Differentiated Services Field](https://www.rfc-editor.org/rfc/rfc2474.html).
- IETF, [RFC 3246 — An Expedited Forwarding PHB](https://www.rfc-editor.org/rfc/rfc3246.html).
- Cisco, [Quality of Service Configuration Guide — Catalyst 9400 IOS XE 17.15](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9400/software/release/17-15/configuration_guide/qos/b_1715_qos_9400_cg.pdf).
- Cisco, [Video Quality of Service Tutorial](https://www.cisco.com/c/en/us/support/docs/quality-of-service-qos/qos-video/212134-Video-Quality-of-Service-QOS-Tutorial.pdf).
- Cisco, [Configuring Voice VLANs — Catalyst 9300 IOS XE 17.17](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-17/configuration_guide/vlan/b_1717_vlan_9300_cg/configuring_voice_vlans.html).

Toujours vérifier la documentation de la version exacte, les limites matérielles et le contrat opérateur. Les configurations de ce cours sont des modèles pédagogiques, pas des prescriptions universelles de production.
