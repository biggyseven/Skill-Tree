# VXLAN — Niveau intermédiaire

## Configuration de l'underlay, création des VTEP, apprentissage MAC et dépannage


# PRÉSENTATION DU COURS

Le niveau intermédiaire constitue la suite directe de `vxlan-debutant.md`.

Dans le cours précédent, l'apprenant a découvert les principes fondamentaux de VXLAN, la différence entre underlay et overlay, le rôle du VTEP, le VNI et le mécanisme d'encapsulation Ethernet dans UDP/IP.

Ces notions constituent la base théorique. Il faut maintenant les utiliser pour comprendre comment construire une architecture VXLAN fonctionnelle, comment vérifier les associations entre les réseaux locaux et les segments virtuels, et comment diagnostiquer les problèmes qui apparaissent lorsque plusieurs équipements participent au même overlay.

Le niveau intermédiaire passe donc de la compréhension du mécanisme à l'étude de son fonctionnement opérationnel.

L'objectif n'est pas d'accumuler des commandes. Il faut comprendre ce que chaque composant doit accomplir, quelles informations il doit connaître et comment démontrer qu'une communication fonctionne réellement.

Le laboratoire principal repose sur deux points de terminaison VXLAN, appelés VTEP-A et VTEP-B, reliés par un réseau IP de transport.

Une machine est raccordée de chaque côté. Les deux machines appartiennent au même réseau logique VXLAN, bien qu'elles soient raccordées à des points de terminaison différents.

Pour rendre les notions concrètes, un laboratoire Linux utilisant les espaces de noms réseau, les interfaces virtuelles, les ponts Ethernet et les interfaces VXLAN sera construit progressivement. Les commandes Linux servent à expérimenter les mécanismes fondamentaux ; elles ne remplacent pas les procédures propres aux commutateurs d'entreprise.

## Positionnement dans le parcours

```text
NIVEAU DÉBUTANT — vxlan-debutant.md
        |
        v
Concepts de VXLAN
Underlay et overlay
VNI et VTEP
Encapsulation Ethernet / UDP / IP
Parcours d'une trame
        |
        v
NIVEAU INTERMÉDIAIRE — CE COURS
        |
        v
Connectivité IP entre les VTEP
Création des interfaces VXLAN
Association des segments locaux
Apprentissage MAC
Découverte et réplication
Contrôle de la MTU
Tests et dépannage
        |
        v
NIVEAU EXPERT — vxlan-expert.md
        |
        v
EVPN et BGP
Routes MAC/IP
VNI de couche 2 et de couche 3
Anycast Gateway
Routage inter-VNI
Multihoming et convergence
Architecture de centre de données
```

**Continuité pédagogique :** le cours intermédiaire reprend les notions du niveau débutant et les met en pratique. Le niveau expert devra ensuite utiliser les mêmes concepts pour introduire le plan de contrôle EVPN et les architectures VXLAN plus avancées.


# OBJECTIFS PÉDAGOGIQUES

À la fin de ce cours, l'apprenant devra pouvoir :

1. Expliquer les conditions nécessaires au fonctionnement de l'underlay.
2. Vérifier la connectivité entre les adresses IP des VTEP.
3. Comprendre la création et le rôle d'une interface VXLAN.
4. Distinguer les paramètres locaux du VTEP des informations de transport.
5. Expliquer l'association entre un segment local et un VNI.
6. Comprendre le rôle du pont Ethernet dans une architecture VXLAN.
7. Expliquer comment les adresses MAC sont apprises et utilisées.
8. Distinguer le trafic unicast connu du trafic de diffusion et des destinations inconnues.
9. Comparer l'utilisation de destinations distantes statiques, de la réplication et du multicast.
10. Comprendre les contraintes de MTU et de transport UDP.
11. Réaliser un laboratoire VXLAN élémentaire sous Linux.
12. Vérifier les résultats avec les outils de diagnostic disponibles.
13. Identifier les causes courantes d'une panne VXLAN.
14. Préparer une architecture et un ensemble de contrôles qui serviront au niveau expert.

## Prérequis

L'apprenant doit connaître :

- Les notions de VLAN et de sous-réseau.
- Les adresses MAC et IP.
- Le rôle d'un commutateur de couche 2.
- Le routage IP.
- ARP et les communications Ethernet.
- Les principes d'encapsulation.
- Les notions d'adresse source, d'adresse destination et de MTU.
- Le fonctionnement général de VXLAN expliqué au niveau débutant.

Une connaissance élémentaire de Linux facilite les travaux pratiques.

## Environnement du laboratoire

Le laboratoire pratique repose sur Linux et nécessite notamment :

- Un noyau prenant en charge VXLAN et les espaces de noms réseau.
- `iproute2`.
- Les outils `ip` et `bridge`.
- Un accès administrateur permettant de créer des interfaces et des espaces de noms.
- Facultativement, `tcpdump` pour analyser le trafic.
- Facultativement, `ethtool` pour examiner certaines capacités des interfaces.

Les commandes de création et de suppression des interfaces modifient la configuration réseau du système Linux. Elles doivent être exécutées dans un environnement de laboratoire isolé, et non sur un poste de production sans préparation.


# PARTIE 1 — REPRENDRE LES FONDAMENTAUX ET COMPRENDRE LE FONCTIONNEMENT OPÉRATIONNEL

## 1. Ce que le niveau débutant nous a appris

VXLAN transporte des trames Ethernet à travers une infrastructure IP en les encapsulant dans des paquets UDP/IP.

Le VTEP joue le rôle de point de terminaison du tunnel. Lorsqu'une trame doit être transmise à travers l'overlay, le point de terminaison prépare l'encapsulation. À l'arrivée, le VTEP distant traite l'en-tête VXLAN, récupère la trame et la remet au segment local approprié.

Le VNI identifie le segment logique auquel appartient le trafic encapsulé.

Ces mécanismes sont simples à représenter, mais un déploiement réel nécessite plusieurs paramètres cohérents. Les points de terminaison doivent pouvoir communiquer par IP, utiliser le bon identifiant de segment et disposer d'informations suffisantes pour acheminer les trames vers les destinations appropriées.

Une erreur sur un seul de ces éléments peut empêcher les machines de communiquer, même si les autres composants sont correctement configurés.

## 2. De la théorie au fonctionnement réel

Reprenons la topologie de démonstration :

- Hôte A possède l'adresse IP `192.168.10.11`.
- Hôte B possède l'adresse IP `192.168.10.12`.
- VTEP-A utilise l'adresse de transport `10.0.0.1`.
- VTEP-B utilise l'adresse de transport `10.0.0.2`.
- Le segment VXLAN utilise le VNI `10010`.

Les hôtes appartiennent au même sous-réseau logique. L'underlay possède son propre adressage IP et transporte les paquets entre les points de terminaison.

```text
HÔTE A                                             HÔTE B
192.168.10.11                                      192.168.10.12
     |                                                   |
     v                                                   v
  VTEP-A                                               VTEP-B
10.0.0.1                                              10.0.0.2
     |                                                   |
     +---------------- RÉSEAU IP -------------------------+
                     UNDERLAY

             Segment VXLAN : VNI 10010
```

Le point important est que les hôtes ne doivent pas nécessairement être placés dans un même domaine Ethernet physique. VXLAN fournit la connectivité logique entre les segments concernés.

Cependant, cette connectivité n'est pas créée par la seule présence du VNI. Il faut aussi que l'underlay transporte les paquets externes et que les VTEP disposent des associations de segments et des informations de destination nécessaires.

## 3. Les trois problèmes à résoudre

Pour établir une communication, l'architecture doit répondre à trois questions.

**Première question : comment atteindre le VTEP distant ?**

Cette fonction relève de l'underlay. Les adresses IP des points de terminaison doivent être joignables selon la topologie et le plan de routage utilisés.

**Deuxième question : à quel segment VXLAN appartient la trame ?**

Le VTEP doit associer la trame reçue au bon VNI. Cette association dépend de la configuration locale, par exemple d'un VLAN, d'un pont Ethernet ou d'une interface virtuelle.

**Troisième question : où faut-il envoyer la trame ?**

Le point de terminaison doit disposer d'une information de forwarding permettant de déterminer la destination. Cette information peut provenir d'un apprentissage MAC, d'une destination statique ou d'un plan de contrôle tel qu'EVPN.

Une architecture ne peut pas être considérée comme fonctionnelle si l'un de ces trois mécanismes est absent ou incohérent.


# PARTIE 2 — CONSTRUIRE UN UNDERLAY FIABLE

## 4. Pourquoi l'underlay est-il prioritaire ?

Un overlay VXLAN dépend du réseau IP qui transporte ses paquets.

Si un VTEP utilise l'adresse `10.0.0.1` et doit transmettre des paquets vers `10.0.0.2`, le système de transport doit savoir comment joindre cette destination.

Cette connectivité peut être obtenue par un réseau directement connecté, des routes statiques ou un protocole de routage dynamique. Le choix dépend de la taille du réseau, de la redondance souhaitée et de l'architecture de l'infrastructure.

Dans un petit laboratoire, les deux VTEP peuvent être raccordés au même sous-réseau de transport. Dans un centre de données plus important, les VTEP peuvent être distribués entre plusieurs racks et atteindre leurs adresses par une infrastructure de couche 3.

Le mécanisme VXLAN n'impose pas un protocole de routage unique pour construire l'underlay.

## 5. Adresses de transport et adresses applicatives

Il est important de ne pas confondre l'adresse IP du serveur avec celle du VTEP.

Dans notre exemple, `192.168.10.11` identifie Hôte A dans son réseau logique. `10.0.0.1` identifie VTEP-A dans le réseau de transport.

Lorsque le VTEP encapsule une trame, l'adresse IP externe sert au transport du tunnel. L'adresse IP intérieure, si la trame contient un paquet IP, reste celle de la communication entre les hôtes.

Cette distinction permet de diagnostiquer le problème au bon niveau. Une erreur sur l'adresse intérieure concerne généralement le réseau logique ou l'hôte. Une erreur sur l'adresse extérieure peut empêcher le paquet VXLAN d'atteindre le VTEP distant.

## 6. Vérifier la connectivité des VTEP

Avant de configurer les segments VXLAN, il faut vérifier que le réseau de transport est opérationnel.

La première vérification porte sur l'adressage et l'état des interfaces. Il faut ensuite contrôler la table de routage et tester la connectivité vers l'adresse distante.

Dans un environnement Linux, les commandes suivantes permettent d'inspecter les interfaces et les routes :

```bash
ip addr show
ip route show
ip link show
```

Pour tester la connectivité depuis un espace de noms réseau, la commande `ping` peut être utilisée lorsque l'outil est disponible et que les politiques de filtrage l'autorisent.

Par exemple, dans le laboratoire de ce cours :

```bash
ip netns exec vtepA ping -c 3 10.0.0.2
```

Cette commande teste la connectivité IP entre VTEP-A et VTEP-B.

Un résultat positif démontre que le mécanisme de test atteint la destination par le réseau IP. Il ne prouve pas encore que VXLAN fonctionne, car l'interface VXLAN, le VNI et les associations de segments peuvent être mal configurés.

## 7. Vérifier le chemin complet

Dans une infrastructure réelle, les adresses de transport peuvent être séparées par plusieurs routeurs.

Une vérification approfondie comprend :

- L'état administratif des interfaces.
- La présence d'adresses correctes.
- La cohérence du masque et des routes.
- L'accessibilité des adresses des VTEP.
- Les règles de filtrage.
- La MTU des interfaces du chemin.
- La capacité de l'underlay à transporter le trafic VXLAN.

Le test de connectivité IP est une étape essentielle, mais il reste un test du transport. Les contrôles propres à l'overlay doivent être réalisés séparément.

## 8. Que se passe-t-il si les VTEP ne sont pas joignables ?

Lorsque la connectivité IP entre les VTEP est interrompue, le trafic encapsulé ne peut généralement pas être transporté vers son destinataire.

La cause peut être une route absente, une interface arrêtée, une adresse incorrecte ou un filtrage du trafic.

Dans cette situation, modifier le VNI ne résout pas le problème d'underlay.

La méthode correcte consiste à rétablir d'abord la connectivité de transport, puis à vérifier les composants VXLAN.


# PARTIE 3 — COMPRENDRE LES INTERFACES VXLAN

## 9. À quoi correspond une interface VXLAN ?

Une interface VXLAN représente un point d'accès local au mécanisme d'encapsulation.

Sous Linux, l'outil `iproute2` permet de créer une interface virtuelle de type VXLAN. Cette interface possède notamment un identifiant de segment, ainsi que des paramètres relatifs au transport.

Selon le scénario, elle peut également utiliser une adresse locale, une destination distante ou un groupe de multicast.

Les paramètres disponibles dépendent du système et de l'implémentation. Le mécanisme général reste le même : l'interface fournit au système un point de traitement des trames qui doivent être transportées par VXLAN.

## 10. Les paramètres principaux

Dans une configuration Linux, les paramètres courants comprennent :

| Paramètre | Fonction |
|---|---|
| `id` | Identifie le VNI utilisé par l'interface |
| `local` | Définit l'adresse IP source locale du tunnel |
| `remote` | Définit une destination distante de transport dans un scénario unicast statique |
| `group` | Définit un groupe multicast dans un scénario qui utilise ce mécanisme |
| `dev` | Désigne l'interface de transport utilisée |
| `dstport` | Définit le port UDP de destination |
| `nolearning` | Désactive certains mécanismes d'apprentissage intégrés à l'interface VXLAN |

La syntaxe de Linux ne doit pas être confondue avec celle d'un commutateur d'entreprise. Un commutateur peut utiliser une interface NVE, une interface logique VXLAN ou une autre structure propre à son système d'exploitation.

## 11. Le rôle du VNI

Le VNI sélectionne le segment VXLAN concerné.

Si deux interfaces sont associées à des segments logiques différents, leur trafic ne doit pas être traité comme s'il appartenait automatiquement à un seul domaine Ethernet.

L'identifiant participe donc à la segmentation de l'overlay.

Dans une topologie simple, l'association entre un VLAN local et un VNI peut être représentée conceptuellement de la manière suivante :

```text
VLAN LOCAL 10
      |
      v
Association sur VTEP-A
      |
      v
VNI 10010
      |
      v
Transport VXLAN
      |
      v
VNI 10010 sur VTEP-B
      |
      v
Segment local distant
```

Cette représentation est conceptuelle et ne constitue pas une syntaxe de configuration universelle. Le niveau expert étudiera également les architectures dans lesquelles les VNI de couche 2 et de couche 3 jouent des rôles distincts.

## 12. Le choix de l'adresse locale

Un VTEP doit utiliser une adresse source adaptée à la topologie de transport.

Dans un réseau de centres de données, il est courant de s'appuyer sur une adresse de loopback stable, atteignable à travers l'underlay. Cela évite de dépendre directement de l'adresse d'un lien physique particulier, lorsque l'architecture est conçue pour utiliser cette méthode.

Dans le laboratoire Linux de ce cours, les adresses des interfaces de transport sont utilisées directement. Cette solution est suffisante pour un scénario simple où les deux points de terminaison se trouvent sur le même réseau de transport.

Dans une architecture plus complexe, le choix des adresses de VTEP, leur stabilité et leur distribution dans le réseau doivent être définis dans la conception de l'underlay.


# PARTIE 4 — COMPRENDRE LE BRIDGE ET L'ASSOCIATION AU SEGMENT

## 13. Pourquoi utiliser un pont Ethernet ?

Le VTEP ne fonctionne pas de manière isolée du réseau local. Il doit être associé à un segment Ethernet où les trames peuvent être reçues et transmises.

Sous Linux, un pont Ethernet permet de relier plusieurs interfaces dans un même domaine de couche 2.

Une interface VXLAN peut être ajoutée au pont avec l'interface d'accès d'un hôte. Le pont traite alors les trames locales et dirige le trafic vers l'interface appropriée.

Dans un commutateur d'entreprise, la fonction équivalente peut être réalisée par un VLAN, une instance de commutation ou une structure différente selon le système d'exploitation.

## 14. Association du segment local et du VNI

Considérons un hôte qui envoie une trame au VTEP-A. Le VTEP-A doit déterminer quel segment local a reçu cette trame.

Dans un exemple simple, le pont Linux relie l'interface de l'hôte et l'interface VXLAN au même domaine Ethernet. Le VNI de l'interface VXLAN détermine le segment virtuel transporté.

Dans un équipement qui utilise des VLAN, il peut être nécessaire d'associer un VLAN local à un VNI spécifique.

La cohérence de cette association est fondamentale. Si le VLAN 10 est associé au VNI 10010 sur un équipement et que l'architecture s'attend à une association différente sur l'autre équipement, le trafic risque d'être remis au mauvais segment ou de ne pas atteindre sa destination prévue.

## 15. Pourquoi les VLAN locaux peuvent-ils être différents des VNI ?

Un VLAN et un VNI n'appartiennent pas au même champ d'encapsulation.

Le VLAN est un identifiant utilisé dans le contexte de la commutation Ethernet locale. Le VNI identifie le segment VXLAN dans l'en-tête du tunnel.

Une architecture peut choisir une correspondance simple, par exemple VLAN 10 vers VNI 10010, afin de faciliter l'administration.

Ce n'est pas une relation arithmétique obligatoire. Le VNI est attribué selon le plan d'adressage de l'overlay.

Dans une architecture répartie, cette relation doit être documentée, validée et cohérente avec le service réseau attendu.

## 16. Pourquoi séparer les responsabilités ?

Une panne peut provenir du port local, du pont Ethernet, de l'association VLAN-VNI ou du transport VXLAN.

Si la configuration est organisée de façon à distinguer ces composants, le dépannage devient plus clair.

L'administrateur peut d'abord vérifier le port local, puis l'association au segment, ensuite l'interface VXLAN et enfin le transport IP.

Cette séparation permet aussi d'éviter de corriger une couche qui fonctionne déjà correctement.


# PARTIE 5 — COMPRENDRE L'APPRENTISSAGE MAC ET LE FORWARDING

## 17. Pourquoi le VTEP doit-il connaître les destinations MAC ?

VXLAN transporte des trames Ethernet. Le VTEP doit donc disposer d'un mécanisme permettant de déterminer où envoyer la trame correspondant à une adresse MAC de destination.

L'information recherchée peut être une association entre une adresse MAC et un VTEP distant, ou une information équivalente disponible dans l'implémentation.

Dans un pont Ethernet classique, le commutateur apprend les adresses MAC source à partir des trames reçues sur ses ports. Il peut ensuite utiliser sa table MAC pour transmettre les trames destinées aux adresses connues.

Dans VXLAN, le mécanisme doit aussi tenir compte de la séparation entre les segments locaux et les VTEP distants.

## 18. Exemple d'apprentissage

Supposons qu'Hôte A envoie une trame dont l'adresse MAC source est `AA:AA:AA:AA:AA:AA`.

VTEP-A peut apprendre que cette adresse est accessible localement dans le segment concerné.

Lorsque la trame provenant d'Hôte B arrive depuis VTEP-B, les mécanismes de forwarding peuvent apprendre ou mettre à jour les informations correspondant à la MAC distante.

Ce processus est soumis au fonctionnement de l'implémentation et au mode d'apprentissage utilisé.

L'apprentissage ne doit pas être considéré comme une base de données globale automatiquement synchronisée en permanence entre tous les VTEP.

## 19. Table MAC locale et destinations distantes

Il faut distinguer les informations de forwarding du pont Ethernet et les informations de forwarding VXLAN.

La table du pont peut associer une MAC à une interface locale. L'interface VXLAN possède également des informations permettant de déterminer vers quels points de terminaison distants les paquets doivent être envoyés.

La relation entre ces tables dépend du système utilisé.

Cette séparation est importante lorsque la communication échoue : une MAC peut être connue localement sans que le VTEP dispose d'une destination distante correcte.

## 20. Destinations connues et inconnues

Lorsque le VTEP connaît la destination, il peut envoyer le trafic vers le point de terminaison approprié selon son état de forwarding.

Lorsque la destination est inconnue, l'architecture doit décider quoi faire du trafic. Le comportement peut inclure une diffusion, une réplication vers plusieurs VTEP ou un traitement propre au système.

Le flooding peut permettre de découvrir des destinations, mais il augmente le volume de trafic et ne constitue pas toujours la méthode la plus efficace dans les grands réseaux.

Dans les architectures de production, les mécanismes de contrôle et de distribution des informations de reachability deviennent donc importants.

## 21. Le trafic BUM

BUM signifie Broadcast, Unknown unicast et Multicast.

Ces catégories regroupent différents types de trafic qui peuvent nécessiter une réplication dans un overlay.

- **Broadcast** : trame destinée à tous les équipements concernés du domaine Ethernet.
- **Unknown unicast** : trame unicast dont le destinataire n'est pas connu du mécanisme de forwarding.
- **Multicast** : trafic destiné à un groupe de destinataires.

Le traitement BUM dépend de la conception de l'overlay et des capacités de la plateforme.

Une architecture VXLAN peut utiliser le multicast de l'underlay ou la réplication de tête, également appelée *head-end replication*. Le choix a des conséquences en matière de configuration, de charge et d'exploitation.

## 22. Réplication de tête

Avec la réplication de tête, le VTEP d'origine crée une copie du trafic à transmettre à chacun des VTEP participants au segment, selon les règles de l'architecture.

Cette méthode évite d'exiger un groupe multicast du réseau underlay dans les scénarios qui l'utilisent.

En revanche, le nombre de copies générées par le VTEP source peut croître avec le nombre de destinations.

Dans un réseau de grande taille, la réplication de tête doit être dimensionnée et associée à une méthode fiable permettant de connaître les VTEP participants.

## 23. Multicast de l'underlay

Dans une architecture qui utilise le multicast, les VTEP peuvent s'appuyer sur des groupes multicast du réseau de transport pour diffuser certains paquets.

Cette approche demande que l'underlay et ses équipements prennent en charge le fonctionnement multicast nécessaire.

Il faut notamment prendre en compte l'adhésion aux groupes, le routage multicast lorsque nécessaire et la compatibilité des interfaces.

Le choix entre multicast et réplication de tête doit être fait à partir des capacités de l'infrastructure et du nombre de points de terminaison. Il ne faut pas supposer que l'un des mécanismes convient automatiquement à toutes les architectures.


# PARTIE 6 — CRÉER LE LABORATOIRE VXLAN SOUS LINUX

## 24. Objectif du laboratoire

Le laboratoire va créer deux points de terminaison VXLAN et deux hôtes Linux isolés dans des espaces de noms réseau.

Les deux VTEP communiqueront sur un réseau de transport Ethernet simple. Chaque VTEP disposera d'une interface VXLAN rattachée à un pont local.

Le scénario utilise un VNI unique et une destination distante statique. Il s'agit donc d'un laboratoire pédagogique limité à deux VTEP, et non d'une architecture EVPN multi-équipements.

La configuration est reproduite par les commandes Linux. Les interfaces et les namespaces ne correspondent pas à du matériel physique.

## 25. Plan d'adressage

| Élément | Interface logique | Adresse |
|---|---|---|
| VTEP-A | Interface underlay | `10.0.0.1/24` |
| VTEP-B | Interface underlay | `10.0.0.2/24` |
| Hôte A | Interface hôte | `192.168.10.11/24` |
| Hôte B | Interface hôte | `192.168.10.12/24` |
| Segment VXLAN | VNI | `10010` |
| Transport | UDP de destination | `4789` |

Les adresses sont réservées à la démonstration. Elles ne sont pas destinées à être utilisées comme des adresses de production.

## 26. Architecture du laboratoire

```text
Hôte A                                     Hôte B
192.168.10.11                             192.168.10.12
     |                                          |
  br-access-A                                br-access-B
     |                                          |
 vxlan10010-A                               vxlan10010-B
     |                                          |
 VTEP-A                                     VTEP-B
 10.0.0.1                                   10.0.0.2
     |                                          |
     +--------- bridge underlay Linux ----------+
                    Réseau IP
```

Le pont de transport situé dans l'espace de noms principal simule le réseau underlay.

Les espaces de noms `vtepA`, `vtepB`, `hostA` et `hostB` permettent d'isoler les interfaces et les tables réseau.

## 27. Vérifier les prérequis

Avant de commencer, vérifiez la disponibilité des commandes :

```bash
ip -Version
bridge -Version
ip netns list
```

Selon la distribution, certaines commandes peuvent être fournies par des paquets distincts d'`iproute2`.

Il faut aussi disposer des privilèges nécessaires pour créer des interfaces virtuelles et des espaces de noms.

Le laboratoire crée des interfaces et des ponts temporaires. Il est préférable d'utiliser une machine virtuelle Linux ou un environnement spécialement prévu pour les exercices.

## 28. Créer un script de laboratoire

Le script suivant construit l'environnement décrit précédemment.

Il doit être exécuté en tant qu'administrateur dans un système Linux compatible. Il vérifie d'abord la présence des principaux outils, puis crée les espaces de noms et les interfaces.

Le script est volontairement séparé de la configuration de production : il sert à reproduire un laboratoire isolé.

Créez un fichier `lab-vxlan.sh`.

```bash
#!/usr/bin/env bash

set -euo pipefail

# Laboratoire pédagogique VXLAN statique.
# À exécuter dans une machine Linux de laboratoire.
# Ne pas exécuter sur un système dont la configuration réseau
# doit être conservée sans vérification préalable.

if [ "$(id -u)" -ne 0 ]; then
    echo "Erreur : exécutez ce laboratoire avec les privilèges administrateur."
    exit 1
fi

for command_name in ip bridge; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Erreur : commande manquante : $command_name"
        exit 1
    fi
done

cleanup() {
    ip netns del hostA 2>/dev/null || true
    ip netns del hostB 2>/dev/null || true
    ip netns del vtepA 2>/dev/null || true
    ip netns del vtepB 2>/dev/null || true
    ip link del br-underlay 2>/dev/null || true
}

echo "Nettoyage d'une précédente instance du laboratoire..."
cleanup

echo "Création des espaces de noms..."
ip netns add hostA
ip netns add hostB
ip netns add vtepA
ip netns add vtepB

echo "Création du réseau underlay..."
ip link add br-underlay type bridge
ip link set br-underlay up

ip link add a-root type veth peer name eth-underlay
ip link set eth-underlay netns vtepA
ip link set a-root master br-underlay
ip link set a-root up

ip link add b-root type veth peer name eth-underlay
ip link set eth-underlay netns vtepB
ip link set b-root master br-underlay
ip link set b-root up

echo "Configuration des adresses de transport..."
ip -n vtepA link set lo up
ip -n vtepB link set lo up

ip -n vtepA addr add 10.0.0.1/24 dev eth-underlay
ip -n vtepB addr add 10.0.0.2/24 dev eth-underlay

ip -n vtepA link set eth-underlay up
ip -n vtepB link set eth-underlay up

echo "Création des interfaces d'accès..."
ip link add a-access type veth peer name hostA-eth0
ip link set hostA-eth0 netns hostA

ip link add b-access type veth peer name hostB-eth0
ip link set hostB-eth0 netns hostB

echo "Création des ponts locaux..."
ip -n vtepA link add br-access type bridge
ip -n vtepB link add br-access type bridge

ip link set a-access netns vtepA
ip link set b-access netns vtepB

ip -n vtepA link set a-access master br-access
ip -n vtepB link set b-access master br-access

ip -n vtepA link set a-access up
ip -n vtepB link set b-access up

echo "Création des interfaces VXLAN..."
ip -n vtepA link add vxlan10010 \
    type vxlan \
    id 10010 \
    local 10.0.0.1 \
    remote 10.0.0.2 \
    dev eth-underlay \
    dstport 4789

ip -n vtepB link add vxlan10010 \
    type vxlan \
    id 10010 \
    local 10.0.0.2 \
    remote 10.0.0.1 \
    dev eth-underlay \
    dstport 4789

echo "Rattachement des interfaces VXLAN aux ponts..."
ip -n vtepA link set vxlan10010 master br-access
ip -n vtepB link set vxlan10010 master br-access

ip -n vtepA link set vxlan10010 up
ip -n vtepB link set vxlan10010 up

ip -n vtepA link set br-access up
ip -n vtepB link set br-access up

echo "Configuration des hôtes..."
ip -n hostA link set lo up
ip -n hostB link set lo up

ip -n hostA addr add 192.168.10.11/24 dev hostA-eth0
ip -n hostB addr add 192.168.10.12/24 dev hostB-eth0

ip -n hostA link set hostA-eth0 up
ip -n hostB link set hostB-eth0 up

echo
echo "Laboratoire créé."
echo "Test underlay :"
echo "  ip netns exec vtepA ping -c 3 10.0.0.2"
echo
echo "Test overlay :"
echo "  ip netns exec hostA ping -c 3 192.168.10.12"
echo
echo "Inspection VXLAN :"
echo "  ip -n vtepA -d link show vxlan10010"
echo "  ip netns exec vtepA bridge fdb show dev vxlan10010"
```

Rendez le script exécutable :

```bash
chmod +x lab-vxlan.sh
```

Puis exécutez-le dans un environnement Linux de laboratoire :

```bash
sudo ./lab-vxlan.sh
```

Le script construit les espaces de noms et leurs interfaces. Les versions de Linux et d'`iproute2` doivent prendre en charge les paramètres VXLAN utilisés.

## 29. Comprendre ce que le script crée

Le script commence par supprimer les espaces de noms et le pont portant les noms utilisés par le laboratoire. Cette étape évite certaines collisions avec une précédente exécution, mais elle signifie aussi qu'il ne faut pas utiliser ces noms pour des ressources existantes à conserver.

Le pont `br-underlay` relie les interfaces de transport des deux VTEP. Il simule un réseau Ethernet de transport sur lequel les adresses IP `10.0.0.1` et `10.0.0.2` sont directement joignables.

Chaque VTEP possède également un pont `br-access`. Ce pont relie l'interface de l'hôte local à l'interface VXLAN.

L'interface VXLAN utilise le VNI `10010` et une destination distante statique correspondant à l'autre VTEP.

Cette approche est volontairement simple : elle permet d'observer le transport et la décapsulation sans introduire tout de suite EVPN ou un plan de contrôle distribué.

## 30. Vérifier d'abord l'underlay

Exécutez :

```bash
ip netns exec vtepA ping -c 3 10.0.0.2
```

Puis :

```bash
ip netns exec vtepB ping -c 3 10.0.0.1
```

Ces tests vérifient la connectivité IP entre les adresses de transport des VTEP.

Si les tests échouent, vérifiez les interfaces des deux espaces de noms, leur adressage et le pont underlay.

Il est inutile d'examiner les associations MAC du VXLAN tant que le transport IP de base ne fonctionne pas.

## 31. Vérifier l'interface VXLAN

Utilisez :

```bash
ip -n vtepA -d link show vxlan10010
```

Puis :

```bash
ip -n vtepB -d link show vxlan10010
```

L'option `-d` affiche des informations détaillées sur l'interface.

Vérifiez notamment le VNI, l'adresse locale, la destination distante, l'interface de transport et le port UDP.

Les détails de présentation peuvent varier selon la version de Linux et d'`iproute2`.

## 32. Tester l'overlay

Lancez :

```bash
ip netns exec hostA ping -c 3 192.168.10.12
```

Ce test cherche à vérifier que l'hôte A peut atteindre l'hôte B à travers le segment logique.

Dans ce laboratoire, le mécanisme de destination distante statique convient au scénario simple à deux VTEP. Ce n'est pas une architecture générique prête pour un grand nombre d'équipements.

Si le ping échoue, il faut suivre une séquence de diagnostic plutôt que modifier arbitrairement le VNI ou les adresses.

## 33. Examiner les tables de forwarding

Les outils Linux permettent d'observer les interfaces, les ponts et les entrées de forwarding.

Par exemple :

```bash
ip netns exec vtepA bridge link show
```

```bash
ip netns exec vtepA bridge fdb show
```

```bash
ip netns exec vtepA bridge fdb show dev vxlan10010
```

La table FDB peut contenir des entrées locales et distantes selon le mode d'apprentissage et les paquets échangés.

Il faut générer du trafic avant d'interpréter certaines informations, car une destination qui n'a pas encore été observée peut ne pas apparaître comme une destination apprise.

L'absence d'une entrée MAC n'est donc pas toujours une erreur de configuration. Il faut tenir compte de l'état du trafic et du mécanisme de forwarding utilisé.

## 34. Analyser le trafic VXLAN

Si `tcpdump` est installé, il est possible d'observer le trafic UDP utilisé par le tunnel.

Dans cet exemple :

```bash
ip netns exec vtepA tcpdump -ni eth-underlay udp port 4789
```

L'outil permet d'observer les paquets sur l'interface de transport.

Lorsque le trafic de test est généré, on doit pouvoir chercher des paquets dont les adresses extérieures correspondent aux VTEP, avec le port UDP de destination prévu.

Une capture confirme la présence de certains paquets, mais elle ne suffit pas à démontrer qu'ils ont été décapsulés et remis correctement à l'hôte distant.

Il faut également examiner la réception et le résultat de bout en bout.

## 35. Nettoyer le laboratoire

Lorsque les exercices sont terminés, exécutez le nettoyage prévu :

```bash
sudo ip netns del hostA
sudo ip netns del hostB
sudo ip netns del vtepA
sudo ip netns del vtepB
sudo ip link del br-underlay
```

Les interfaces associées aux espaces de noms supprimés sont supprimées avec eux.

La commande concernant `br-underlay` peut échouer si le pont a déjà été supprimé. Cela ne signifie pas nécessairement que le laboratoire est encore actif. Vérifiez l'état du système avec `ip link show` et `ip netns list`.


# PARTIE 7 — COMPRENDRE LES LIMITES DU LABORATOIRE STATIQUE

## 36. Pourquoi une destination distante statique ?

Le laboratoire utilise un paramètre `remote` pour indiquer l'adresse distante vers laquelle transporter le trafic VXLAN.

Cette approche est utile pour comprendre les fondamentaux, parce qu'elle rend explicite l'association entre le point de terminaison local et son homologue distant.

En revanche, elle ne constitue pas une solution de contrôle évolutive pour un overlay comportant un grand nombre de VTEP.

Lorsque plusieurs équipements participent au même segment, il faut un mécanisme fiable pour connaître les destinations, distribuer les informations et prendre en charge les changements de topologie.

Ce besoin explique l'intérêt de mécanismes de contrôle comme EVPN.

## 37. Ce que le laboratoire démontre

Le laboratoire permet d'observer :

- La connectivité IP entre les VTEP.
- La création d'une interface VXLAN.
- L'utilisation d'un VNI.
- L'association entre une interface VXLAN et un pont Ethernet.
- Le transport de trames sur UDP/IP.
- Le forwarding dans un petit segment.
- Les étapes de dépannage de base.

Il ne démontre pas une architecture complète de centre de données.

Il n'inclut notamment pas :

- BGP EVPN.
- Les routes MAC/IP EVPN.
- Le routage inter-VNI.
- L'Anycast Gateway.
- Le multihoming.
- Les mécanismes de convergence avancés.
- Une politique de sécurité complète.
- Une conception de production à grande échelle.

Ces sujets seront développés au niveau expert.

## 38. Quand faut-il passer à un plan de contrôle ?

Lorsque le nombre de VTEP augmente, la gestion manuelle des destinations et les mécanismes simples de réplication deviennent plus difficiles à maintenir.

Un plan de contrôle peut distribuer les informations de reachability et réduire la nécessité d'administrer chaque relation manuellement.

EVPN, généralement associé à BGP dans les architectures VXLAN de centres de données, apporte des procédures de distribution de routes et des mécanismes associés à l'apprentissage des adresses MAC/IP.

Le niveau expert abordera ces fonctions en expliquant les routes utilisées et leur rôle dans l'overlay.


# PARTIE 8 — LA MTU ET LES PROBLÈMES DE TRANSPORT

## 39. Pourquoi la MTU doit-elle être contrôlée ?

VXLAN ajoute des en-têtes au paquet d'origine.

Lorsque le paquet encapsulé traverse l'underlay, sa taille est supérieure à celle du paquet intérieur.

Si un lien du chemin possède une MTU insuffisante, certains paquets peuvent ne pas être transportés correctement.

Le problème peut être difficile à détecter lorsqu'il ne touche que les paquets les plus volumineux.

Par exemple, un ping de petite taille peut fonctionner, tandis qu'un transfert contenant des paquets plus grands échoue.

Il ne faut pas conclure que l'underlay est parfaitement adapté simplement parce qu'un petit ping réussit.

## 40. Calculer la surcharge

Pour VXLAN sur IPv4 classique, l'encapsulation ajoute notamment :

- L'en-tête IP extérieur.
- L'en-tête UDP.
- L'en-tête VXLAN.
- L'en-tête Ethernet extérieur sur le lien physique.

La surcharge communément citée est d'environ 50 octets en IPv4 et environ 70 octets en IPv6, selon la manière dont la taille est comptée et les champs présents.

Les options, les marquages VLAN et les conventions de calcul peuvent modifier le résultat précis.

Pour dimensionner le MTU, il faut partir du MTU intérieur voulu et calculer la taille réelle du paquet extérieur selon les en-têtes transportés.

Il ne faut pas augmenter la MTU de manière arbitraire sans vérifier les limites des interfaces et des équipements traversés.

## 41. Symptômes possibles d'une MTU inadéquate

Parmi les symptômes possibles :

- Des flux fonctionnent seulement pour certaines tailles de paquets.
- Les connexions semblent établir leur session mais échouent pendant des transferts.
- Certains chemins fonctionnent et d'autres non.
- Des pertes apparaissent lorsque des paquets plus grands sont utilisés.
- Les résultats varient selon le chemin ECMP.

Une MTU inadéquate n'est pas la seule cause possible de ces symptômes. Il faut examiner le chemin complet, les politiques de filtrage et les compteurs disponibles.

## 42. Méthode de diagnostic

Commencez par relever les MTU des interfaces physiques et logiques.

Ensuite, vérifiez la taille du paquet intérieur, la surcharge attendue et la MTU disponible sur le chemin de transport.

Il faut aussi tenir compte du comportement lié à la fragmentation et à la découverte de MTU, selon le protocole et les fonctions supportées.

Le diagnostic doit éviter de se limiter à une mesure réalisée sur un seul lien lorsque les paquets traversent plusieurs équipements.


# PARTIE 9 — SÉCURITÉ DU TRAFIC VXLAN

## 43. VXLAN ne chiffre pas automatiquement les données

L'encapsulation VXLAN permet le transport de trames Ethernet sur le réseau IP. Elle ne constitue pas à elle seule une protection cryptographique du contenu.

Le réseau de transport doit donc être conçu selon le niveau de confiance requis.

Dans certains environnements, le trafic des VTEP est limité à un réseau de transport contrôlé. Dans d'autres, des mécanismes supplémentaires de protection et de chiffrement peuvent être nécessaires.

Il faut également protéger les interfaces d'administration et contrôler qui peut modifier les associations entre les segments locaux et les VNI.

## 44. Principaux contrôles à prévoir

Un réseau VXLAN doit contrôler :

- Les adresses de VTEP autorisées.
- Les chemins de transport.
- Le trafic UDP utilisé par le tunnel.
- Les correspondances VLAN-VNI.
- Les associations MAC et les destinations distantes.
- Les règles de filtrage inter-segments.
- Les accès d'administration aux équipements.
- Les changements de configuration.
- Les événements de forwarding et les erreurs.

La sécurité ne découle pas uniquement du fait que deux hôtes possèdent des VNI différents.

Il reste nécessaire de définir les flux applicatifs autorisés et les mécanismes de contrôle qui s'appliquent au réseau logique.

## 45. Pourquoi protéger le réseau de transport ?

Le VTEP traite les paquets VXLAN qu'il reçoit conformément aux règles de la plateforme.

Une infrastructure qui accepte des paquets de tunnel provenant de sources non autorisées peut exposer des risques d'usurpation ou d'injection de trafic, en fonction de l'implémentation et de la configuration.

Il est donc important de restreindre le trafic VXLAN aux chemins et aux points de terminaison prévus.

Les mesures exactes doivent être adaptées à l'architecture. Un filtrage mal conçu peut aussi interrompre le fonctionnement légitime de l'overlay.


# PARTIE 10 — DÉPANNAGE MÉTHODIQUE

## 46. Pourquoi faut-il dépanner par couches ?

VXLAN combine un réseau de transport, un mécanisme d'encapsulation et une logique Ethernet. Une panne peut se produire à chacun de ces niveaux.

La méthode la plus efficace consiste à vérifier d'abord ce qui est nécessaire au fonctionnement de tout le reste.

Il faut donc commencer par la connectivité IP entre les VTEP. Ensuite, vérifier les paramètres VXLAN et les associations de segments. Enfin, étudier l'apprentissage MAC et la remise de la trame au segment local.

Cette méthode réduit le risque de modifier une configuration qui fonctionne déjà.

## 47. Panne de l'underlay

**Symptôme :** les hôtes ne communiquent plus et les adresses IP des VTEP ne sont pas joignables.

**Hypothèses à examiner :**

- Interface de transport arrêtée.
- Adresse IP incorrecte.
- Route absente.
- Problème de voisinage de couche 2 dans le réseau de transport.
- Politique de filtrage.
- Problème de MTU.
- Perte de connectivité sur un lien intermédiaire.

**Méthode :**

1. Vérifier les interfaces et les adresses.
2. Contrôler la table de routage.
3. Tester la connectivité entre les VTEP.
4. Examiner les compteurs et les journaux disponibles.
5. Vérifier le chemin et la MTU.

Il ne faut pas passer directement à la configuration de l'overlay si les points de terminaison ne peuvent pas se joindre dans l'underlay.

## 48. VNI incohérent

**Symptôme :** les VTEP communiquent par IP, mais le segment logique ne fonctionne pas.

**Hypothèses à examiner :**

- VNI incorrect.
- Interface VXLAN rattachée au mauvais pont.
- VLAN local associé au mauvais VNI.
- Association différente sur les extrémités.
- Paramètre de transport incompatible.

La correction doit s'appuyer sur le plan d'allocation des VNI du réseau, et non sur un changement choisi au hasard.

Dans une architecture de production, il faut également considérer les règles de service et les éventuelles correspondances particulières entre les segments.

## 49. Problème d'apprentissage MAC

**Symptôme :** les VTEP sont joignables, mais une destination MAC ne peut pas être atteinte.

**Hypothèses à examiner :**

- La machine distante n'a jamais émis de trafic.
- L'adresse MAC n'a pas été apprise.
- Une entrée de forwarding est incorrecte.
- Les mécanismes de réplication ne distribuent pas le trafic nécessaire.
- Une information de reachability est absente du plan de contrôle.
- Le trafic est associé au mauvais segment.

Il faut examiner les tables de forwarding et provoquer un trafic de test contrôlé avant de conclure que l'apprentissage ne fonctionne pas.

## 50. Problème de MTU

**Symptôme :** certains paquets passent et d'autres échouent.

**Hypothèses à examiner :**

- MTU underlay insuffisante.
- MTU incohérente entre les liens.
- Comportement de fragmentation.
- Problème de découverte de MTU.
- Limite propre à un chemin ou à un équipement.

La MTU doit être vérifiée de bout en bout.

## 51. Problème de remise locale

Même si le paquet arrive à VTEP-B, la communication peut échouer.

Le VTEP distant doit correctement traiter le paquet VXLAN, retrouver le segment correspondant et remettre la trame sur la bonne interface locale.

Il faut donc vérifier :

- L'état de l'interface VXLAN.
- Le VNI.
- L'état du pont Ethernet.
- Les membres du pont.
- Les entrées MAC.
- Les compteurs d'erreurs.
- Les filtres locaux éventuels.

Cette étape est souvent négligée lorsque l'on se concentre uniquement sur l'encapsulation.


# PARTIE 11 — EXERCICES CORRIGÉS

## 52. Exercice 1 — Underlay et overlay

**Question :** les VTEP peuvent se joindre par IP, mais les deux hôtes ne communiquent pas. Quelles couches faut-il examiner ?

**Correction :**

Il faut vérifier les paramètres de l'overlay, en particulier le VNI, l'association du segment local, le forwarding MAC et la remise de la trame.

La connectivité IP confirme une partie du transport, mais elle ne prouve pas que le segment VXLAN est correctement configuré.

## 53. Exercice 2 — Destination inconnue

**Question :** que se passe-t-il lorsqu'un VTEP ne possède pas d'information de forwarding pour la destination MAC ?

**Correction :**

Le comportement dépend de l'architecture et de l'implémentation. Des mécanismes de diffusion, de réplication ou de découverte peuvent être employés.

Dans une architecture simple, une destination distante statique peut fournir une destination de transport par défaut pour certains trafics inconnus. Cette approche ne remplace pas un système complet de distribution des informations de reachability pour un overlay de grande taille.

## 54. Exercice 3 — Port UDP

**Question :** les VTEP sont joignables par IP, mais le trafic VXLAN ne traverse pas le réseau. Quel rôle le filtrage UDP peut-il jouer ?

**Correction :**

Le transport VXLAN utilise UDP, généralement avec le port de destination 4789.

Un filtrage qui bloque le trafic requis entre les adresses de transport peut empêcher le tunnel de fonctionner.

Il faut vérifier les ACL et les pare-feu sur le chemin sans désactiver indistinctement les politiques de filtrage.

## 55. Exercice 4 — Mauvaise association VLAN-VNI

**Question :** deux hôtes doivent appartenir au même segment logique, mais les associations du VLAN local au VNI ne correspondent pas au plan prévu. Pourquoi cela peut-il empêcher la communication ?

**Correction :**

Le VNI identifie le segment logique transporté dans l'en-tête VXLAN.

Si le trafic local est associé à un autre segment, le paquet peut être transporté dans un overlay différent de celui attendu. Le problème doit être corrigé en respectant le plan d'allocation et les associations de la plateforme.

## 56. Exercice 5 — Destination MAC distante

**Question :** pourquoi faut-il distinguer la table MAC du pont et les informations de forwarding VXLAN ?

**Correction :**

La table du pont peut indiquer sur quelle interface locale se trouve une MAC. Le mécanisme VXLAN doit également connaître la destination distante appropriée lorsque la trame doit être transportée vers un autre VTEP.

La relation entre ces informations dépend de l'implémentation. Une entrée locale valide ne prouve donc pas que la destination distante est disponible.

## 57. Exercice 6 — MTU

**Question :** un petit ping fonctionne entre deux hôtes, mais un transfert volumineux échoue. VXLAN peut-il être impliqué ?

**Correction :**

Oui, une MTU d'underlay insuffisante constitue une hypothèse possible, car l'encapsulation ajoute des en-têtes.

Il faut toutefois examiner le chemin complet et vérifier les autres causes possibles. Le petit ping ne suffit pas à démontrer que le transport peut prendre en charge toutes les tailles de paquets nécessaires.

## 58. Exercice 7 — Évolutivité

**Question :** pourquoi une configuration statique de destinations distantes peut-elle devenir difficile à maintenir dans un réseau comportant de nombreux VTEP ?

**Correction :**

À mesure que le nombre de VTEP et de segments augmente, la configuration des destinations et la gestion des changements deviennent plus complexes.

Un plan de contrôle tel qu'EVPN permet de distribuer les informations de reachability au moyen de mécanismes structurés. Les détails de ce fonctionnement appartiennent au niveau expert.


# PARTIE 12 — ERREURS FRÉQUENTES

## 59. Configurer le VXLAN avant de vérifier le réseau IP

Une configuration d'overlay ne peut pas fonctionner correctement si l'underlay est incapable de transporter les paquets entre les VTEP.

**Bonne pratique :** vérifier les adresses, les routes, les interfaces et la connectivité avant de diagnostiquer l'overlay.

## 60. Confondre l'adresse de l'hôte avec celle du VTEP

L'adresse applicative appartient au réseau intérieur, tandis que l'adresse de transport sert à acheminer le paquet encapsulé.

**Bonne pratique :** identifier clairement les adresses intérieures et extérieures lorsque l'on analyse un paquet ou un schéma.

## 61. Supposer que le VNI garantit la communication

Le VNI identifie un segment. Il ne garantit pas, à lui seul, que la destination MAC est connue, que le transport est fonctionnel ou que la trame sera remise au bon port local.

**Bonne pratique :** contrôler le segment, le forwarding, le transport et la remise locale.

## 62. Ignorer le trafic BUM

Le trafic de diffusion et les destinations inconnues peuvent nécessiter des mécanismes de réplication spécifiques.

**Bonne pratique :** comprendre le comportement de l'implémentation et la façon dont les VTEP participants sont connus.

## 63. Utiliser un laboratoire statique comme modèle de production

Le laboratoire à deux VTEP est utile pour apprendre l'encapsulation, mais il ne représente pas toute la gestion d'un overlay à grande échelle.

**Bonne pratique :** identifier explicitement les limites du scénario et introduire le plan de contrôle avant d'étendre l'architecture.

## 64. Négliger la MTU

VXLAN augmente la taille des paquets transportés.

**Bonne pratique :** vérifier la MTU de toutes les interfaces et l'effet des en-têtes supplémentaires sur le chemin complet.


# PARTIE 13 — GLOSSAIRE INTERMÉDIAIRE

**Underlay :** infrastructure IP qui assure l'acheminement entre les points de terminaison de l'overlay.

**Overlay :** réseau logique VXLAN construit au-dessus du réseau de transport.

**VTEP :** point qui réalise l'encapsulation et la décapsulation VXLAN.

**VNI :** identifiant de 24 bits d'un segment VXLAN.

**Interface VXLAN :** interface logique qui permet de transporter des trames Ethernet dans un tunnel VXLAN.

**Bridge :** mécanisme de couche 2 qui relie des interfaces dans un même domaine Ethernet.

**Association VLAN-VNI :** correspondance entre un segment local et un segment VXLAN.

**FDB :** *Forwarding Database*, table utilisée pour associer les destinations MAC à des interfaces ou à des chemins de forwarding.

**BUM :** Broadcast, Unknown unicast et Multicast ; catégories de trafic nécessitant des mécanismes spécifiques de diffusion ou de réplication.

**Réplication de tête :** méthode dans laquelle le VTEP source envoie des copies du trafic vers plusieurs VTEP distants.

**Multicast underlay :** utilisation du multicast dans le réseau de transport pour distribuer certains trafics overlay.

**MTU :** taille maximale d'unité de données prise en charge sur un lien ou une interface dans le contexte considéré.

**Plan de données :** mécanismes qui transportent et acheminent le trafic.

**Plan de contrôle :** mécanismes qui distribuent les informations de reachability et permettent de maintenir la connectivité logique.

**EVPN :** solution de contrôle qui peut distribuer des informations Ethernet et MAC/IP pour des réseaux overlay.


# PARTIE 14 — ÉVALUATION DE FIN DE NIVEAU

## 65. Questions théoriques

L'apprenant doit répondre aux questions suivantes sans consulter le cours.

1. Pourquoi l'underlay doit-il fonctionner avant le dépannage de l'overlay ?
2. Quelle est la différence entre une interface VXLAN et une interface de transport ?
3. Quel est le rôle du VNI ?
4. Quelle différence existe entre l'adresse IP du VTEP et celle de l'hôte ?
5. Pourquoi une association VLAN-VNI doit-elle être cohérente ?
6. Quel est le rôle d'un pont Ethernet dans le laboratoire Linux ?
7. Pourquoi la table MAC ne suffit-elle pas toujours à décrire le forwarding VXLAN ?
8. Que signifie BUM ?
9. Dans quel cas la réplication de tête peut-elle être utilisée ?
10. Quelle est la différence entre un mécanisme statique et un plan de contrôle distribué ?
11. Pourquoi une MTU insuffisante peut-elle provoquer des pannes partielles ?
12. Quelles informations peut-on observer avec `ip -d link show` ?
13. Que permet de vérifier `bridge fdb show` ?
14. Pourquoi un ping réussi ne démontre-t-il pas que tous les flux VXLAN fonctionnent ?
15. Quelles sont les limites d'un laboratoire VXLAN statique à deux VTEP ?
16. Pourquoi EVPN devient-il intéressant lorsque le nombre de VTEP augmente ?

## 66. Travaux pratiques

Réalisez les activités suivantes dans l'environnement Linux du laboratoire.

### Travail 1 — Créer l'underlay

Créez les deux espaces de noms VTEP et établissez la connectivité IP entre leurs adresses de transport.

Vérifiez les interfaces et les routes avant de poursuivre.

### Travail 2 — Créer les interfaces VXLAN

Créez une interface VXLAN de chaque côté avec le même VNI et les destinations distantes correspondant à la topologie.

Vérifiez les paramètres détaillés des interfaces.

### Travail 3 — Rattacher les hôtes

Créez les interfaces d'accès et les ponts Ethernet locaux.

Vérifiez que les interfaces concernées sont activées et associées aux bons ponts.

### Travail 4 — Tester la communication

Lancez un ping entre les deux hôtes.

Si le test échoue, consignez le résultat et vérifiez successivement le transport IP, les paramètres VXLAN, le forwarding et les interfaces locales.

### Travail 5 — Observer le trafic

Utilisez une capture lorsque l'outil est disponible.

Identifiez les paquets UDP correspondant au transport VXLAN et expliquez pourquoi leurs adresses IP extérieures diffèrent des adresses IP des hôtes.

### Travail 6 — Étudier les limites

Expliquez ce qui changerait si le laboratoire comportait plusieurs VTEP participant au même segment.

Décrivez pourquoi la découverte des destinations et le mécanisme de réplication deviendraient plus importants.


# PARTIE 15 — PRÉPARER LE NIVEAU EXPERT

## 67. Ce qui est maintenant acquis

Le cours intermédiaire a transformé les notions du niveau débutant en un laboratoire opérationnel.

L'apprenant sait maintenant distinguer les composants du transport et ceux de l'overlay, vérifier la connectivité entre les VTEP, créer des interfaces VXLAN, comprendre l'association au segment local et examiner les informations de forwarding.

Il a également étudié les limites d'une destination statique, le traitement du trafic BUM, les besoins de MTU et les étapes principales du dépannage.

La configuration statique est adaptée à un apprentissage contrôlé. Elle devient toutefois plus difficile à administrer lorsqu'il faut gérer un grand nombre de VTEP, de segments et de changements.

## 68. Progression vers le niveau expert

```text
NIVEAU DÉBUTANT
        |
        v
Comprendre l'encapsulation VXLAN
        |
        v
NIVEAU INTERMÉDIAIRE
        |
        v
Configurer un underlay fonctionnel
Créer les VTEP
Associer les segments
Comprendre le forwarding MAC
Dépanner le tunnel
        |
        v
NIVEAU EXPERT
        |
        v
Introduire EVPN et BGP
Distribuer les informations MAC/IP
Comprendre les types de routes EVPN
Mettre en œuvre le routage inter-VNI
Étudier l'Anycast Gateway
Aborder le multihoming et la convergence
Concevoir une architecture évolutive
```

## 69. Contenu attendu du cours expert

Le cours expert devra commencer par reprendre la topologie et les fonctions du laboratoire intermédiaire. Il devra expliquer ce qui devient difficile lorsque les destinations sont administrées manuellement et pourquoi un plan de contrôle distribué devient nécessaire.

Il approfondira ensuite :

- Le rôle de BGP dans la distribution des informations EVPN.
- Les routes EVPN et leur fonction.
- Les annonces de reachability MAC/IP.
- Les VNI de couche 2 et les VNI de couche 3.
- Le routage inter-VNI.
- L'Anycast Gateway.
- Les mécanismes de redondance.
- Le multihoming EVPN.
- La convergence après une panne.
- Les contrôles de sécurité et de conception.

Le niveau expert devra expliquer le raisonnement et les dépendances des mécanismes au lieu de présenter uniquement une liste de commandes propres à un constructeur.


# CONCLUSION GÉNÉRALE

Le niveau intermédiaire montre comment passer d'une compréhension théorique de VXLAN à un laboratoire fonctionnel.

L'apprenant a étudié le réseau IP de transport, les interfaces VXLAN, le VNI, les ponts Ethernet, l'apprentissage MAC et le forwarding. Il a également appris à vérifier les paramètres de l'interface, à observer le trafic UDP et à dépanner les problèmes de transport, d'association de segments, de forwarding et de MTU.

Le laboratoire statique à deux VTEP permet de comprendre les mécanismes essentiels sans confondre ce scénario pédagogique avec une architecture complète de production.

Pour aller plus loin, il faudra traiter la découverte des destinations, la distribution des informations de reachability, les réseaux logiques de grande taille et les mécanismes de redondance.

Le niveau expert prolongera donc ce travail avec EVPN, BGP, les routes MAC/IP, le routage inter-VNI et les architectures VXLAN distribuées.

**Principe final : vérifier d'abord le transport IP, puis l'interface VXLAN et le VNI, ensuite le forwarding MAC et la remise locale. Comprendre ces dépendances est indispensable avant d'aborder EVPN et les architectures VXLAN avancées.**


# RÉFÉRENCES TECHNIQUES

- RFC 7348 — *Virtual eXtensible LAN (VXLAN): A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks*  
  https://www.rfc-editor.org/rfc/rfc7348.html

- RFC 8365 — *A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)*  
  https://www.rfc-editor.org/rfc/rfc8365.html

- Documentation du noyau Linux — VXLAN  
  https://kernel.org/doc/html/latest/networking/vxlan.html

- Manuel Linux `ip-link` — paramètres des interfaces VXLAN  
  https://man7.org/linux/man-pages/man8/ip-link.8.html

Les commandes pratiques doivent être testées sur la version de Linux et d'`iproute2` effectivement installée. Pour un déploiement sur un commutateur physique, il faut utiliser la documentation du constructeur et tenir compte des fonctions réellement prises en charge.