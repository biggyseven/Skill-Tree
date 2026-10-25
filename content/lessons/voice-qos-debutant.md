# QoS Voix et Vidéo — Débutant

## Mise en contexte : pourquoi une visioconférence peut-elle se dégrader alors que le réseau fonctionne ?

Une personne téléphone depuis un bureau pendant qu'un collègue télécharge un fichier volumineux et qu'une salle participe à une visioconférence. Le lien réseau est actif et les applications restent connectées, mais la voix devient saccadée, l'image se fige et les interlocuteurs se coupent la parole.

Ce n'est pas nécessairement une panne complète. Quand plusieurs flux se disputent un lien congestionné, les paquets n'ont pas tous les mêmes exigences. Un paquet vocal qui arrive trop tard peut être inutilisable, alors qu'un paquet d'un téléchargement peut généralement attendre un peu plus longtemps.

La **qualité de service (QoS, Quality of Service)** regroupe les mécanismes qui identifient les flux, les marquent et organisent leur traitement afin de mieux respecter les besoins des applications. La QoS ne crée pas de bande passante supplémentaire et ne répare pas une liaison défectueuse : elle gère les ressources disponibles, surtout en situation de congestion.

> **Idée essentielle :** la voix et la vidéo de temps réel ont besoin d'un traitement cohérent de bout en bout. Marquer quelques paquets sans configurer les files d'attente, les liens WAN et les limites de confiance ne suffit pas.

## 1. Objectifs pédagogiques

À la fin du cours, tu sauras :

- expliquer pourquoi la voix et la vidéo sont sensibles au délai, à la gigue et aux pertes ;
- distinguer bande passante, latence, gigue et perte de paquets ;
- comprendre les notions de classification, marquage, mise en file, policing et shaping ;
- reconnaître DSCP EF, AF41, CS3/CS5 et CoS 802.1p sans les confondre ;
- décrire le rôle d'un VLAN voix et les limites de cette séparation ;
- suivre un flux RTP et signaler les points de contrôle QoS sur le chemin ;
- effectuer un calcul simple de bande passante pour des appels ;
- interpréter des symptômes courants et suivre une checklist de dépannage.

## 2. Prérequis

Connaître les bases Ethernet, VLAN, IPv4, UDP/TCP, téléphonie IP, SIP et RTP. Le cours rappelle les concepts nécessaires.

# Partie I — Les besoins de la voix et de la vidéo

## 3. Voix et vidéo : des flux temps réel

Une application temps réel émet des paquets qui doivent arriver assez vite pour être présentés au bon moment. Le récepteur dispose souvent d'un tampon de lecture limité. Un paquet qui arrive après sa date de lecture peut être abandonné, même si le réseau finit par le livrer.

- **Voix :** petit flux continu, généralement à débit relativement stable. Une perte brève peut provoquer un clic, une syllabe manquante ou une coupure.
- **Vidéo interactive :** débit plus variable, souvent beaucoup plus élevé. Une perte peut créer des artefacts, réduire la résolution ou provoquer un gel de l'image.
- **Signalisation :** établit, modifie et termine l'appel. Elle est importante, mais ses paquets ne sont pas le même flux que les paquets audio/vidéo.
- **Données classiques :** courriel, téléchargement, sauvegarde ou navigation. Selon l'application, un délai plus élevé est souvent tolérable.

Schéma de principe :

```text
Téléphone A ===== audio RTP =====> réseau ===== audio RTP =====> Téléphone B
     |                                                       |
     +--- signalisation SIP pour établir/terminer l'appel ---+

RTP transporte les médias. SIP contrôle généralement la session.
La QoS doit traiter séparément les classes correspondant à ces besoins.
```

## 4. Les quatre indicateurs fondamentaux

### 4.1 Bande passante et débit disponible

La bande passante d'un lien représente sa capacité. Le débit utilisé est la quantité de données qui le traverse par unité de temps. Quand la demande cumulée dépasse régulièrement la capacité, les files d'attente grandissent et des paquets peuvent être retardés ou supprimés.

Un lien de 10 Mbit/s peut être suffisant pour quelques dizaines d'appels et devenir problématique si une sauvegarde sature simultanément le même chemin. La capacité nominale n'indique donc pas à elle seule la qualité perçue.

### 4.2 Latence (délai)

La latence est le temps mis par un paquet pour aller d'un point à un autre. Elle comprend notamment :

- le délai de propagation sur le support ;
- le délai de sérialisation pour placer les bits sur le lien ;
- le traitement des équipements ;
- l'attente dans les files d'attente.

Pour une conversation, le délai aller-retour influence le rythme des échanges. Une voix peut être intelligible tout en paraissant désagréable si les interlocuteurs s'interrompent à cause du délai.

### 4.3 Gigue (jitter)

La gigue désigne la variation du délai entre les paquets. Le récepteur peut utiliser un tampon de gigue pour lisser les variations, mais un tampon plus grand augmente le délai global.

```text
Arrivée régulière :  |---20 ms---|---20 ms---|---20 ms---|
Arrivée irrégulière: |--8 ms--|------34 ms------|--12 ms--|
                         variation = gigue
```

La définition exacte de la gigue mesurée dépend de la métrique et de l'outil. Comparer deux valeurs suppose de vérifier qu'elles sont calculées de la même manière.

### 4.4 Perte de paquets

La perte survient quand un paquet est supprimé, arrive trop tard ou n'est pas reçu. Elle peut être causée par la congestion, une erreur physique, une interface saturée, une mauvaise configuration ou un équipement qui abandonne des paquets selon une politique de policing.

La QoS peut réduire les pertes dues à la congestion en donnant un traitement adapté aux flux prioritaires. Elle ne corrige pas les erreurs physiques, et ne doit pas permettre à un flux prioritaire incontrôlé de consommer toutes les ressources.

## 5. Symptômes et causes possibles

| Symptôme observé | Causes à examiner en priorité |
|---|---|
| Voix hachée dans les deux sens | pertes, congestion, gigue, CPU ou média surchargé |
| Un seul interlocuteur entend mal | chemin asymétrique, perte sur un seul sens, problème d'interface ou de média |
| Appels bons à faible charge, mauvais à l'heure de pointe | saturation et files d'attente inadéquates |
| Signalisation correcte mais média mauvais | chemin RTP/UDP, QoS du WAN, NAT/firewall, perte ou gigue |
| Vidéo qui se fige alors que l'audio reste acceptable | débit vidéo insuffisant, pertes, congestion de la classe vidéo ou capacité Wi-Fi |
| Appel impossible à établir | signalisation, routage, admission, configuration ou sécurité ; ce n'est pas automatiquement un problème QoS |

# Partie II — Les marquages de QoS

## 6. Classification et marquage

La **classification** consiste à reconnaître un paquet ou un flux, par exemple grâce à l'adresse, au protocole, au port, à une ACL ou à une information fournie par l'application.

Le **marquage** écrit une valeur dans un champ utilisé par les équipements suivants pour appliquer une politique. Le marquage ne réserve pas automatiquement une capacité : il sert de signal aux politiques QoS configurées dans le réseau.

### 6.1 DSCP : champ de couche 3

DSCP (Differentiated Services Code Point) occupe les six bits de poids fort du champ DS de l'en-tête IP. Une valeur DSCP n'est utile que si les équipements du chemin l'interprètent de manière cohérente.

| Usage courant | Marquage souvent rencontré | Valeur décimale | Remarque |
|---|---|---:|---|
| Audio voix interactif | EF | 46 | Classe courante pour le média vocal RTP |
| Signalisation téléphonique | CS3 ou CS5 | 24 ou 40 | Le choix dépend de la politique du système et de l'entreprise |
| Vidéo de conférence | AF41 | 34 | Recommandation fréquente, à confirmer dans la politique locale |
| Vidéo temps réel / collaboration spécialisée | CS4 dans certains environnements | 32 | Peut être utilisé pour certains équipements ou architectures |
| Trafic classique non différencié | DF / CS0 | 0 | Traitement par défaut |

Ces valeurs sont des conventions fréquentes, pas une vérité universelle pour tous les produits et toutes les architectures. Avant d'imposer des règles, consulter la documentation du système de collaboration, la stratégie de l'entreprise et les spécifications du fournisseur.

### 6.2 EF, AF et CS : ne pas les confondre

- **EF (Expedited Forwarding)** est fréquemment associé à l'audio de téléphonie interactif. Il doit être protégé par une politique de priorité avec une limite de débit appropriée ; il ne faut pas laisser n'importe quel trafic réclamer EF.
- **AF (Assured Forwarding)** définit des classes avec des niveaux de précédence d'abandon. AF41, AF42 et AF43 peuvent être utilisés pour différencier plusieurs traitements de trafic vidéo selon la politique retenue.
- **CS (Class Selector)** fournit des classes simples, par exemple CS0, CS3, CS5 ou CS6.

Le nombre DSCP correspond à un code, pas directement à un pourcentage de bande passante. EF 46 ne signifie pas « 46 % de priorité ».

### 6.3 CoS 802.1p : priorité de couche 2

Dans une trame Ethernet taguée 802.1Q, le champ PCP (souvent appelé CoS) utilise trois bits et peut prendre les valeurs 0 à 7. CoS est visible sur le segment Ethernet tagué, tandis que DSCP est porté par le paquet IP.

| CoS (PCP) | Interprétation courante, selon politique locale |
|---:|---|
| 0 | meilleur effort |
| 3 | signalisation ou traitement intermédiaire dans certains plans |
| 4 | vidéo dans certaines politiques |
| 5 | voix dans de nombreuses politiques d'entreprise |
| 6–7 | classes de contrôle ou réservées à une politique spécifique ; éviter leur attribution arbitraire |

CoS et DSCP ne sont pas le même champ. Lorsqu'un paquet traverse un lien routé, le tag Ethernet est retiré et recréé à chaque saut ; le DSCP peut rester dans l'en-tête IP, à moins qu'une politique le modifie.

## 7. Les mécanismes QoS à connaître

### 7.1 Files d'attente et ordonnancement

Lorsque plusieurs paquets veulent sortir d'une interface plus vite que le lien ne peut les transmettre, ils attendent dans des files. L'ordonnancement décide quelle file est servie en premier ou quelle part de capacité chaque classe reçoit.

- Une **file prioritaire** peut servir rapidement le trafic temps réel.
- Une politique de type **LLQ (Low Latency Queuing)** combine souvent une file strictement prioritaire et des classes à bande passante garantie.
- Une file prioritaire doit être plafonnée ou surveillée : sinon elle peut priver les autres classes de capacité.

### 7.2 Policing et shaping

Le **policing** mesure le débit et peut marquer ou supprimer les paquets qui dépassent le profil autorisé. Il ne met pas les paquets en attente pour lisser le débit.

Le **shaping** retarde les paquets afin de lisser un flux vers un débit cible. Il est particulièrement utile pour faire correspondre le débit envoyé à la capacité réelle d'un circuit WAN.

```text
Policing : trafic excessif ---> [mesure] ---> conforme : transmis
                                      +----> excès : remarqué ou supprimé

Shaping  : trafic en rafale ---> [tampon d'attente] ---> sortie régulée
```

### 7.3 Pourquoi marquer ne suffit pas

Un paquet DSCP EF traversant un switch sans politique de files d'attente peut être traité comme les autres paquets. Un autre équipement peut aussi réécrire son DSCP. Il faut donc vérifier le comportement réel à chaque frontière : classification, confiance accordée au marquage, mapping, queues, compteurs et capacité du lien.

# Partie III — Architecture et chemin des médias

## 8. VLAN voix : utile, mais distinct de la QoS

Un port de bureau peut connecter un téléphone IP et un ordinateur derrière ce téléphone. Le téléphone envoie sa voix dans un VLAN voix tandis que le PC utilise un VLAN de données.

```text
                 +--------------------+
PC de l'employé--| port PC du téléphone|
                 |   Téléphone IP     |---- trames taguées VLAN voix
                 +--------------------+              |
                                                     v
                                               Switch d'accès
                                              /             \
                                      VLAN données       VLAN voix
                                          |                  |
                                          v                  v
                                      Réseau PC         CUCM / média
```

Le VLAN voix facilite la séparation logique, les politiques de sécurité et l'application de QoS. Mais il ne garantit pas automatiquement une faible latence. Le trafic vocal doit être pris en charge dans les files et sur les liens montants, les routeurs WAN et, si nécessaire, le réseau sans fil.

Sur des commutateurs Cisco, CDP ou LLDP-MED peut participer à la découverte de paramètres voix par le téléphone. La configuration exacte du VLAN voix et des mécanismes QoS dépend du modèle et de la version logicielle du switch.

## 9. Chemin du média et de la signalisation

Exemple simplifié d'un appel entre deux sites :

```text
Téléphone A -- Switch A -- routeur / WAN -- routeur -- Switch B -- Téléphone B
     |                                                           |
     +------------ SIP / signalisation ---------------------------+
     +=============== RTP / audio ou vidéo =======================+
```

La signalisation peut suivre un chemin logique différent de celui du média. Le média RTP peut aussi traverser des composants de traversée de pare-feu, SBC, passerelles ou relais médias. Une capture SIP réussie ne prouve donc pas que le chemin RTP fonctionne correctement.

Pour chaque sens, vérifier :

1. le marquage à la source ;
2. la classification et le trust boundary du switch d'accès ;
3. les interfaces de sortie en congestion ;
4. le mapping DSCP/CoS sur les liaisons de couche 2 ;
5. le traitement QoS du WAN, du Wi-Fi et des tunnels ;
6. le marquage observé à destination et les statistiques de réception RTP.

# Partie IV — Calculs fondamentaux

## 10. Estimer la bande passante d'un appel

Le débit d'un codec ne représente pas tout le débit réseau. Chaque paquet ajoute des en-têtes RTP, UDP, IP, Ethernet et éventuellement VLAN, tunnel, chiffrement ou encapsulation WAN.

### 10.1 Exemple avec G.711 et une période de paquetisation de 20 ms

Hypothèses pédagogiques :

- débit audio G.711 : 64 kbit/s ;
- durée audio par paquet : 20 ms ;
- charge utile audio : 64 000 bit/s × 0,020 s = 1 280 bits = 160 octets ;
- fréquence : 1 / 0,020 = 50 paquets par seconde ;
- en-têtes RTP + UDP + IPv4 : 12 + 8 + 20 = 40 octets, sans options IP ;
- taille au niveau IP : 160 + 40 = 200 octets par paquet.

Débit IP estimé dans un sens :

`200 octets × 8 bits × 50 paquets/s = 80 000 bit/s = 80 kbit/s`

Le débit réellement consommé sur le support est supérieur après ajout des en-têtes Ethernet, du tag VLAN, du préambule, de l'intervalle inter-trame et de l'encapsulation WAN. Une estimation autour de 90 à 100 kbit/s par sens est souvent utilisée pour illustrer G.711 avec 20 ms, mais il faut recalculer selon la couche mesurée et le transport réel.

### 10.2 Nombre d'appels et dimensionnement initial

Si une classe voix doit supporter 30 appels simultanés et qu'on retient une hypothèse prudente de 100 kbit/s par appel et par sens :

`30 × 100 kbit/s = 3 000 kbit/s`, soit environ 3 Mbit/s dans chaque sens.

On ajoute une marge pour les pointes, les en-têtes réels, la signalisation, les autres flux prioritaires et l'évolution du trafic. Le calcul exact doit préciser s'il s'agit de débit applicatif, IP ou sur le fil.

## 11. Les codecs changent le profil de trafic

| Codec | Débit audio nominal indicatif | Conséquence QoS |
|---|---:|---|
| G.711 | 64 kbit/s de charge audio | bonne qualité courante, débit réseau total nettement supérieur à 64 kbit/s |
| G.729 | 8 kbit/s de charge audio | débit inférieur, mais les en-têtes sont proportionnellement plus importants |
| Opus | débit variable selon configuration | dimensionner selon le profil réel et l'adaptation du codec |

Ne calcule jamais la capacité d'une liaison uniquement à partir du débit nominal du codec.

## 12. La vidéo : débit variable

Le débit vidéo dépend de la résolution, de la fréquence d'image, du codec, du contenu, de la scène, du partage d'écran et de la politique de l'application. Un partage d'écran statique et une vidéo en mouvement peuvent avoir des profils très différents.

Pour la QoS, utiliser les profils et statistiques fournis par la plateforme de collaboration, puis valider les mesures sur le réseau. Il n'existe pas de valeur universelle de débit par participant adaptée à toutes les réunions.

# Partie V — Laboratoire guidé

## 13. TP 1 — Identifier la QoS dans une capture réseau

### Objectif

Observer les marquages DSCP d'un flux RTP et distinguer média et signalisation.

### Matériel

Deux terminaux de téléphonie IP ou une maquette de collaboration, Wireshark ou un outil de capture autorisé. Une capture préenregistrée est acceptable si le laboratoire ne dispose pas de téléphones.

### Étapes

1. Capturer le trafic pendant un appel de test autorisé.
2. Identifier l'établissement d'appel (par exemple SIP si cette technologie est utilisée).
3. Identifier les flux média RTP/UDP à partir des ports négociés ou des fonctions de décodage de l'outil.
4. Examiner le champ DSCP de plusieurs paquets IP.
5. Comparer la valeur observée avec la politique interne. Ne suppose pas EF uniquement parce que le flux transporte de la voix.
6. Répéter, si possible, la capture sur un autre point du chemin.

### Résultat attendu

Une fiche indique les adresses, le protocole, les ports, les DSCP observés, l'emplacement de la capture et toute différence entre les points de capture.

### Correction et interprétation

- Un flux audio souvent marqué EF (46) est cohérent avec une politique courante, mais la valeur attendue doit être confirmée localement.
- Une valeur DSCP différente à deux points peut indiquer une réécriture, un tunnel, un équipement qui ne préserve pas le marquage ou une différence entre média et signalisation.
- Une capture unique ne permet pas toujours de déterminer à quel saut le changement s'est produit.

## 14. TP 2 — Vérifier un port d'accès voix sur un commutateur Cisco

> Les commandes et leur emplacement exact changent suivant la famille de commutateur et la version IOS/IOS XE. Exécute-les uniquement dans une maquette ou après validation de la configuration cible.

Exemple illustratif d'un port avec PC et téléphone :

```text
interface GigabitEthernet1/0/10
 description Poste-utilisateur-avec-telephone
 switchport mode access
 switchport access vlan 20
 switchport voice vlan 30
 spanning-tree portfast
```

Ce fragment illustre la séparation logique. Il ne configure pas à lui seul une stratégie QoS de bout en bout.

Vérifications possibles selon plateforme :

```text
show interfaces GigabitEthernet1/0/10 switchport
show vlan brief
show interfaces GigabitEthernet1/0/10 counters errors
show running-config interface GigabitEthernet1/0/10
```

### Questions à résoudre

1. Quel VLAN porte le trafic du PC ?
2. Quel VLAN est destiné au téléphone ?
3. Le port a-t-il des erreurs physiques ou des rejets ?
4. Où se trouve la politique qui fait confiance aux marquages du téléphone ?
5. Que faut-il inspecter sur le lien montant ?

### Correction

Dans l'exemple, le VLAN de données est 20 et le VLAN voix est 30. Il faut ensuite vérifier les politiques de marquage/confiance, les files de sortie et les liens montants. La seule présence de `switchport voice vlan 30` ne garantit pas que les paquets audio obtiennent un traitement prioritaire.

## 15. TP 3 — Observer l'effet d'une congestion

### Objectif

Comprendre pourquoi les problèmes apparaissent sous charge.

### Procédure

1. Mesurer latence, gigue et pertes avec le lien peu chargé.
2. Générer ensuite une charge contrôlée dans un environnement de test, sans perturber une production.
3. Relever les compteurs des files d'attente et des interfaces.
4. Si une politique QoS de laboratoire existe, comparer les résultats avec et sans cette politique.
5. Vérifier que la classe voix reste protégée et que les autres classes continuent à progresser.

### Correction attendue

Sans QoS appropriée, la congestion peut augmenter le délai et les pertes. Avec une politique correcte, les flux prioritaires peuvent mieux résister à la congestion, mais le résultat dépend de la capacité totale, des limites des classes et du chemin complet. Si le lien est saturé en permanence, l'ajout de capacité ou la réduction de la charge peut rester nécessaire.

## 16. TP 4 — Calculer la capacité d'une liaison voix

Un site doit transporter 24 appels simultanés G.711. Pour un premier dimensionnement, on retient 100 kbit/s par appel et par sens.

1. Calculer le débit voix approximatif dans un sens.
2. Proposer une marge de capacité de 25 %.
3. Expliquer pourquoi ce résultat n'est pas une preuve que le lien est suffisant.

### Correction

- Base : 24 × 100 kbit/s = 2,4 Mbit/s dans un sens.
- Avec 25 % de marge : 2,4 × 1,25 = 3,0 Mbit/s environ.
- Il faut encore inclure les autres flux temps réel, la signalisation, les en-têtes réellement utilisés, les pointes, le trafic de données et les débits garantis dans les deux sens. Il faut aussi tester les files d'attente et la capacité effective du lien.

# Partie VI — Méthode de dépannage

## 17. Checklist en cas de voix ou vidéo dégradée

Procéder par étapes, sans modifier plusieurs éléments à la fois.

1. **Définir le symptôme :** quel utilisateur, quelle heure, quel sens, quel site, appels internes ou externes, voix seule ou vidéo aussi ?
2. **Comparer avec un appel témoin :** même site, même appareil, même chemin ou même plateforme.
3. **Séparer signalisation et média :** l'appel s'établit-il correctement ? Le flux RTP arrive-t-il dans les deux sens ?
4. **Mesurer :** pertes, gigue, délai, débit, erreurs de ports, drops de files et utilisation des liens.
5. **Vérifier les marquages :** DSCP/CoS à la source, après le switch, sur le WAN et à destination.
6. **Examiner les limites de confiance :** les paquets du téléphone sont-ils traités selon la politique attendue ? Un PC branché derrière le téléphone peut-il imposer une priorité indue ?
7. **Inspecter la congestion :** compteurs de files, drops, shaping, policing, surallocation de la priorité.
8. **Tester les deux sens séparément :** les routes et politiques peuvent être asymétriques.
9. **Documenter le résultat :** horodatage, captures, compteurs avant/après, changement effectué et résultat.

## 18. Erreurs classiques à éviter

- Penser que le VLAN voix équivaut à la QoS.
- Croire que le marquage EF réserve automatiquement du débit.
- Faire confiance à tout paquet qui arrive avec DSCP EF, quelle que soit sa source.
- Mettre tout le trafic de collaboration dans une priorité stricte sans plafond.
- Vérifier seulement le chemin aller et oublier le retour.
- Supposer qu'un appel établi prouve que la qualité média est correcte.
- Calculer la capacité uniquement à partir du débit nominal du codec.
- Copier une configuration Auto-QoS sans vérifier sa compatibilité avec la plateforme et les téléphones vidéo utilisés.

# Partie VII — Exercices corrigés

## Exercice 1

**Question :** Quelle différence y a-t-il entre latence et gigue ?

**Correction :** La latence mesure le délai de livraison ; la gigue décrit la variation du délai entre les paquets. Une latence moyenne faible ne garantit pas une faible gigue.

## Exercice 2

**Question :** À quoi sert DSCP EF 46 dans une politique voix courante ?

**Correction :** À identifier un flux qui doit recevoir un traitement adapté à la téléphonie interactive, si le réseau a été configuré pour interpréter ce marquage. Le nombre 46 n'indique pas une quantité de bande passante.

## Exercice 3

**Question :** Quelle différence entre CoS et DSCP ?

**Correction :** CoS/PCP est un marquage de priorité à trois bits dans une trame Ethernet 802.1Q. DSCP est un marquage de six bits dans l'en-tête IP. Ils vivent à des couches différentes et nécessitent un mapping cohérent.

## Exercice 4

**Question :** Un appel s'établit, mais l'audio est haché. Quel plan d'investigation suivre ?

**Correction :** Examiner d'abord les flux RTP dans les deux sens, puis les pertes, la gigue, les compteurs d'interface et de files, le DSCP aux différentes frontières et la congestion du WAN. Ne pas se limiter à SIP.

## Exercice 5

**Question :** Un VLAN voix séparé garantit-il une bonne qualité d'appel ?

**Correction :** Non. Il facilite la séparation et l'application de politiques, mais la QoS doit encore être appliquée aux files et aux liaisons congestionnées sur l'ensemble du chemin.

## Exercice 6

**Question :** Pourquoi faut-il limiter le trafic en file prioritaire ?

**Correction :** Une file stricte non plafonnée peut monopoliser la capacité lorsqu'elle reçoit trop de trafic, au détriment des autres classes. La priorité doit être dimensionnée et surveillée.

## Exercice 7

**Question :** Calculer le débit IP approximatif d'un flux G.711 avec 20 ms de paquetisation et 200 octets IP par paquet.

**Correction :** 50 paquets/s × 200 octets × 8 = 80 000 bit/s, soit 80 kbit/s dans un sens, avant les surcharges de couche 2 et d'encapsulation.

## Exercice 8

**Question :** Que signifie un changement de DSCP entre deux captures ?

**Correction :** Un équipement ou une frontière de domaine a pu réécrire le marquage, ou la capture peut concerner un autre flux ou une autre encapsulation. Il faut capturer à plusieurs points pour isoler le saut responsable.

## Exercice 9

**Question :** Le téléphone porte CoS 5, mais la QoS WAN ne montre pas de priorité. Pourquoi ?

**Correction :** Le mapping CoS/DSCP peut être absent ou incorrect, le tag peut être retiré au routage, la politique WAN peut ignorer le marquage, ou la capture peut observer un paquet différent. Vérifier chaque étape.

## Exercice 10

**Question :** Quel est le rôle du shaping ?

**Correction :** Lisser un débit en mettant temporairement en attente les paquets pour respecter un débit de sortie cible. Le policing mesure le débit et peut marquer ou supprimer le trafic excédentaire.

# Partie VIII — Défi final corrigé

## 19. Scénario

Une entreprise possède deux sites reliés par un WAN de 10 Mbit/s. Les téléphones utilisent G.711 avec une paquetisation de 20 ms. À l'heure de pointe, les utilisateurs signalent une voix hachée pendant que les sauvegardes s'exécutent. Les appels s'établissent correctement. Une capture côté téléphone montre des paquets audio marqués EF, mais l'administrateur ne dispose pas encore de mesures au niveau WAN.

### Missions

1. Calculer un budget initial pour 20 appels simultanés avec une hypothèse de 100 kbit/s par appel et par sens.
2. Proposer un plan de mesure en cinq étapes minimum.
3. Décrire une politique QoS conceptuelle sans appliquer aveuglément une configuration constructeur.
4. Expliquer deux causes possibles pour lesquelles EF n'offre aucune amélioration.
5. Définir les preuves à collecter avant et après correction.

## 20. Correction détaillée

### Mission 1 — Budget initial

20 × 100 kbit/s = 2 Mbit/s par sens, hors marge et hors autres flux prioritaires. Une marge de 25 % porte l'hypothèse à 2,5 Mbit/s. Ce chiffre ne prouve pas que le lien suffit : il faut examiner le trafic vidéo, le débit réel du WAN, la direction congestionnée, l'encapsulation et la politique de files.

### Mission 2 — Mesures

- Horodater les plaintes et identifier les appels touchés.
- Mesurer pertes, gigue et délai du flux RTP dans les deux sens.
- Examiner les compteurs d'interface, drops de sortie, erreurs physiques et utilisation du lien WAN.
- Comparer DSCP à la source, avant l'entrée WAN et à la sortie WAN.
- Observer les statistiques de files et les éventuels drops de policing/shaping pendant la sauvegarde.
- Répéter avec un appel témoin lorsque le lien est peu chargé.

### Mission 3 — Politique conceptuelle

Classer le média vocal autorisé, vérifier son marquage et le traiter dans une classe temps réel à faible latence, avec une limite adaptée au nombre d'appels attendu. Donner une part définie à la vidéo de conférence selon le besoin métier et laisser une capacité suffisante aux données. Appliquer un shaping cohérent avec le débit réel du WAN si nécessaire. Mesurer, puis ajuster.

### Mission 4 — Pourquoi EF peut ne rien changer

1. Le WAN peut ne pas reconnaître EF ou ne pas avoir de file prioritaire correspondante.
2. Le marquage peut être réécrit ou supprimé à une frontière.
3. La classe prioritaire peut être mal dimensionnée ou déjà saturée.
4. Le problème peut venir de pertes physiques, d'un chemin asymétrique, du Wi-Fi ou d'un composant média plutôt que de la file WAN.

### Mission 5 — Preuves de validation

Comparer avant/après les mesures RTP, les drops par classe, les compteurs d'interface, l'utilisation du lien, les valeurs DSCP aux mêmes points, ainsi que les observations des utilisateurs. Vérifier aussi que les sauvegardes et les applications métiers restent utilisables. Conserver la configuration initiale et le plan de retour arrière.

## 21. Critères de réussite

Le défi est réussi si tu sais expliquer que la QoS ne crée pas de capacité, estimer un budget voix avec ses limites, suivre le marquage jusqu'au WAN, interpréter les compteurs de files et proposer une correction mesurable plutôt qu'une simple modification de DSCP.

# Glossaire

- **AF (Assured Forwarding)** : famille de classes DiffServ avec niveaux de précédence d'abandon.
- **CAC (Call Admission Control)** : mécanisme qui limite l'admission de nouvelles sessions selon les ressources ou la politique ; différent de la QoS des paquets.
- **CoS / PCP** : priorité de couche 2 portée par le tag 802.1Q.
- **DSCP** : code de différenciation des services dans l'en-tête IP.
- **EF** : Expedited Forwarding, comportement de transfert fréquemment utilisé pour l'audio interactif.
- **Gigue** : variation du délai de livraison des paquets.
- **LLQ** : mécanisme de file prioritaire à faible latence, souvent associé à d'autres classes garanties.
- **Policing** : contrôle d'un débit avec action sur l'excès (marquage, suppression, selon la politique).
- **RTP** : protocole de transport des médias temps réel.
- **Shaping** : lissage d'un débit par mise en attente des paquets.
- **SIP** : protocole de signalisation de session fréquemment utilisé en téléphonie IP.
- **VLAN voix** : VLAN logique destiné aux appareils ou flux de téléphonie ; distinct du mécanisme de files QoS.

# Références techniques

- IETF, [RFC 4594 — Configuration Guidelines for DiffServ Service Classes](https://www.rfc-editor.org/rfc/rfc4594.html) : classes de service et marquages recommandés.
- IETF, [RFC 2474 — Definition of the Differentiated Services Field](https://www.rfc-editor.org/rfc/rfc2474.html) : champ DiffServ/DSCP.
- IETF, [RFC 3246 — An Expedited Forwarding PHB](https://www.rfc-editor.org/rfc/rfc3246.html) : comportement EF.
- Cisco, [Configuring Voice VLANs — Catalyst 9300 IOS XE 17.17](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-17/configuration_guide/vlan/b_1717_vlan_9300_cg/configuring_voice_vlans.html) : VLAN voix, prérequis et fonctions de commutateur.
- Cisco, [Video Quality of Service Tutorial](https://www.cisco.com/c/en/us/support/docs/quality-of-service-qos/qos-video/212134-Video-Quality-of-Service-QOS-Tutorial.pdf) : repères de classification vidéo et QoS.

Les valeurs et commandes doivent être validées avec la politique de l'organisation, la plateforme et la version logicielle ciblées. Les exemples de ce cours servent à l'apprentissage et ne remplacent pas une revue de changement en production.
