# Qualité de Service (QoS) - Débutant

**Niveau :** Débutant  
**Prérequis :** Notions de base en réseau (Modèle OSI, notions d'IP, TCP/UDP, paquets, commutateurs et routeurs).

Ce cours introduit les concepts fondamentaux de la **Qualité de Service (QoS)** dans les réseaux informatiques. Il explique les problèmes liés au trafic réseau (gigue, latence, perte de paquets) et montre comment la QoS permet de prioriser les flux critiques (comme la voix ou la vidéo) face au trafic ordinaire (web, téléchargements).

---

## 1. Qu'est-ce que la QoS et Pourquoi est-elle Nécessaire ?

### Le Problème du Modèle « Best Effort »

Par défaut, Internet et la plupart des réseaux locaux fonctionnent selon le modèle **Best Effort** (Meilleur Effort) :

* **Tous les paquets sont traités de manière égale.**
* Premier arrivé, premier servi (*FIFO - First In, First Out*).
* Aucune garantie de délai, de débit ou de livraison.

Lorsque la bande passante d'un lien (ex: un routeur d'accès WAN) est saturée, des files d'attente se forment et les paquets en trop sont supprimés.

```
                  SITUATION DE CONGESTION (Sans QoS)
                  
 [ Voix IP (Sensible) ]  ────┐
 [ Vidéo (Sensible)   ]  ────┼───> [ TAMPON / FILE ] ───> [ LIEN SATURÉ ]
 [ Téléchargement )   ]  ────┘     (Débordement : Paquets jetés au hasard)
```

Dans ce schéma, si un gros téléchargement remplit le tampon (*buffer*), un paquet de voix de quelques octets peut être retardé ou jeté, provoquant des coupures dans la communication téléphonique.

### La Solution : La Qualité de Service (QoS)

La **QoS** est un ensemble de technologies et de mécanismes permettant d'identifier le type de trafic et d'accorder un traitement privilégié aux paquets critiques ou sensibles au temps.

```
                   SITUATION AVEC QOS (Tri et Priorisation)

                         ┌──> [ File Prioritaire (Voix) ] ───┐
 [ Trafic Mélangé ] ──>  ├──> [ File Moyenne (Vidéo)   ] ───┼─> [ LIEN ]
 (Voix, Web, File)  (TRI)└──> [ File Standard (Web/FTP)] ───┘
```

---

## 2. Les Problèmes Réseau Résolus par la QoS

Pour comprendre la QoS, il faut connaître les quatre métriques clés qui dégradent l'expérience utilisateur :

| Métrique | Description | Impact en cas de dégradation |
| :--- | :--- | :--- |
| **Bande passante (Bandwidth)** | La capacité maximale de transfert du lien (ex: 100 Mbps). | Sensation de lenteur générale lors des transferts. |
| **Délai / Latence (Latency)** | Le temps mis par un paquet pour aller de la source à la destination. | Décalage dans les conversations voix/vidéo, latence dans les jeux en ligne. |
| **Gigue (Jitter)** | La variation du délai entre deux paquets successifs. | Voix hachée ou robotique, saccades vidéo. |
| **Perte de paquets (Packet Loss)** | Le pourcentage de paquets supprimés suite à la saturation des buffers. | Coupures audio, distorsions d'image, retransmissions TCP lentes. |

---

## 3. Le Processus QoS : Les Étape Clés

L'application de la QoS sur un équipement réseau (routeur ou switch) suit un cycle bien précis :

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 1. Classification  │ 2. Marquage  │ 3. Gestion des│ 4. Mise en   │
│   (Identifier)     │   (Étiqueter)│   Files (Queuing) │   Mise en forme
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
  Voix, Web,           Marquer DSCP         Placer en            Policing /
  Vidéo, SSH           EF ou CS3            File Priorité        Shaping
```

### Étape 1 : Classification & Marquage (Classification & Marking)

1. **Classification :** L'équipement inspecte le paquet pour déterminer son type (ex: en observant l'adresse IP, le port UDP/TCP 5060 pour SIP, etc.).
2. **Marquage :** On modifie un champ dans l'en-tête du paquet pour que les autres équipements du réseau reconnaissent immédiatement sa priorité sans devoir re-tester tout le paquet.

#### Champs de Marquage :
* **Au niveau Couche 2 (Ethernet) :** Champ **CoS (Class of Service)** / 802.1p (3 bits, valeurs de 0 à 7).
* **Au niveau Couche 3 (IP) :** Champ **DSCP (Differentiated Services Code Point)** (6 bits, valeurs de 0 à 63).

```
   EN-TÊTE IP (Champ ToS / DiffServ)
   ┌───────────────────┬──────────────┐
   │    DSCP (6 bits)  │ ECN (2 bits) │
   └───────────────────┴──────────────┘
```

#### Valeurs DSCP Standard Recommandées :
* **EF (Expedited Forwarding - DSCP 46) :** Priorité maximale pour la Voix sur IP (VoIP).
* **AF (Assured Forwarding - ex: AF41, AF31) :** Pour les flux interactifs et la vidéo.
* **BE (Best Effort - DSCP 0) :** Pour le trafic ordinaire (Web, mail).

---

### Étape 2 : Gestion des Files d'Attente (Queuing & Scheduling)

Une fois les paquets marqués, ils sont placés dans des files d'attente distinctes avant d'être transmis sur l'interface de sortie.

```
                           SCHÉMA DE MISE EN FILE (QUEUING)

                           ┌─────────────────────────┐
                   ┌─────> │ File Prioritaire (EF)   │ ───┐
                   │       └─────────────────────────┘    │  Ordre de
                   │       ┌─────────────────────────┐    │  sortie :
 [ Paquets Marqués]├─────> │ File Vidéo (AF41)       │ ───┼──>  1. EF
                   │       └─────────────────────────┘    │     2. AF41
                   │       ┌─────────────────────────┐    │     3. BE
                   └─────> │ File Best Effort (BE)   │ ───┘
                           └─────────────────────────┘
```

* **Strict Priority Queuing (PQ) :** La file prioritaire est *toujours* servie en premier. Tant qu'il y a un paquet dans cette file, les autres attendent.
* **Weighted Fair Queuing (CBWFQ / LLQ) :** Répartit la bande passante de manière équitable tout en garantissant une file prioritaire dédiée pour la voix.

---

### Étape 3 : Gestion de la Congestion et Lissage (Policing & Shaping)

Si le débit injecté dépasse la capacité de l'interface, on utilise deux mécanismes :

```
                  POLICING (Dropping) vs SHAPING (Buffering)

  Débit entrant > Limite
 
  POLICING :  [ Paquets autorisés ] ──> Passer
              [ Paquets en trop   ] ──> [ JETÉS (Drop) ]
              
  SHAPING  :  [ Paquets autorisés ] ──> Passer
              [ Paquets en trop   ] ──> [ Stockés en mémoire ] ──> Envoyés plus tard
```

* **Traffic Policing :** Tranche brutalement le trafic excédentaire (idéal à l'entrée d'un réseau).
* **Traffic Shaping :** Lisse le trafic en retenant temporairement les paquets en mémoire (idéal en sortie vers un lien WAN).

---

## 4. Exemple Concret d'une Configuration de Base (Cisco IOS)

Voici un exemple simple illustrant le marquage et la priorité de la Voix sur un routeur Cisco via le modèle **MQC (Modular QoS CLI)**.

```text
! 1. CLASSIFICATION (Class-Map)
class-map match-all CLASSE_VOIX
 match access-group name ACL_VOIX

! 2. MARQUAGE ET ALLOCATION DE BANDE PASSANTE (Policy-Map)
policy-map POLITIQUE_QOS
 class CLASSE_VOIX
  set dscp ef
  priority percent 20   ! Réserve 20% de la bande passante avec priorité stricte
 class class-default
  fair-queue             ! Trafic standard

! 3. APPLICATION SUR L'INTERFACE DE SORTIE
interface GigabitEthernet0/0/1
 service-policy output POLITIQUE_QOS
```

---

## 5. Résumé des Modèles QoS

1. **Best Effort :** Pas de QoS. Tout le monde est à égalité.
2. **IntServ (Integrated Services) :** Réservation explicite de ressources via le protocole RSVP. Très lourd, peu utilisé à grande échelle.
3. **DiffServ (Differentiated Services) :** Le modèle moderne le plus utilisé. Chaque paquet est marqué (DSCP) et chaque routeur applique un traitement par saut (*Per-Hop Behavior - PHB*).

---

## Points à Retenir

* La QoS est essentielle lorsque **la bande passante est saturée** ou lorsque des flux **sensibles au temps (VoIP, visioconférence)** coexistent avec du trafic lourd.
* **Voix IP (VoIP) :** Nécessite une latence < 150 ms, une gigue < 30 ms et une perte de paquets < 1%.
* Le champ **DSCP (6 bits)** au niveau IP est le standard le plus répandu pour classifier le trafic.
* La valeur **DSCP EF (46)** est systématiquement réservée à la Voix.