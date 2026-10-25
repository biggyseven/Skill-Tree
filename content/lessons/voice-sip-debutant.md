# Protocole SIP & Dial Peers — Débutant

## Mise en contexte

Une entreprise possède des téléphones IP, un système de téléphonie et une liaison vers le réseau téléphonique public (PSTN). Un utilisateur compose un numéro, mais la voix ne peut pas simplement « partir vers Internet » : il faut décider où envoyer l'appel, négocier les paramètres audio et transporter les médias jusqu'au correspondant.

Deux notions sont au centre de ce cours :

- **SIP (Session Initiation Protocol)** signale l'établissement, la modification et la fin d'une session de communication.
- **Les dial peers Cisco** sont des règles de routage d'appels sur une passerelle voix Cisco IOS/IOS XE. Ils aident à reconnaître un appel entrant et à choisir sa destination pour l'appel sortant.

SIP ne transporte généralement pas la voix elle-même. Dans une communication classique, le média audio est transporté séparément par RTP, après négociation des paramètres avec SDP.

> **Objectif du niveau débutant :** comprendre le parcours d'un appel et savoir lire puis construire une configuration très simple de dial peers VoIP. Les exemples utilisent des adresses de documentation et des extensions fictives. La syntaxe exacte varie selon la version IOS/IOS XE, la plateforme et le modèle de déploiement.

## 1. Objectifs pédagogiques

À la fin du cours, tu sauras :

- distinguer signalisation SIP et flux audio RTP ;
- reconnaître les principales méthodes et réponses SIP ;
- expliquer le rôle de SDP, des codecs et du DTMF ;
- distinguer un dial peer POTS d'un dial peer VoIP ;
- différencier le choix d'un dial peer entrant et sortant ;
- lire `destination-pattern`, `incoming called-number` et `session target` ;
- construire une maquette simple entre deux passerelles ;
- dépanner les cas fréquents : appel non routé, audio absent et DTMF non transmis.

## 2. Prérequis

Il est utile de connaître l'adressage IP, les sous-réseaux, UDP/TCP, les ports réseau et le fonctionnement général d'un téléphone IP. Les bases de Cisco IOS (modes EXEC, configuration globale, sauvegarde) sont recommandées.

## 3. Le parcours d'un appel de bout en bout

### 3.1 Signalisation et média sont deux chemins différents

```text
Téléphone A         Passerelle A             Passerelle B         Téléphone B
    |                    |                        |                    |
    |---- SIP INVITE --->|                        |                    |
    |                    |---- SIP INVITE ------->|                    |
    |                    |<--- 100/180/200 OK ----|                    |
    |<--- réponses SIP --|                        |                    |
    |---- ACK ---------->|---- ACK -------------->|                    |
    |                    |                        |                    |
    |<====================== RTP audio ================================>|
    |                    |                        |                    |
    |---- BYE ---------->|---- BYE -------------->|                    |
```

Ce dessin est volontairement simplifié. Selon l'architecture, le téléphone peut échanger directement les médias avec l'autre téléphone ou passer par un relais, une passerelle, un SBC ou une ressource média. La signalisation et le média ne suivent donc pas nécessairement le même trajet.

### 3.2 Les composants essentiels

- **User Agent (UA)** : terminal ou application SIP qui émet ou reçoit des requêtes.
- **Proxy SIP** : relaie des requêtes SIP selon sa politique.
- **Registrar** : accepte les enregistrements des utilisateurs et leurs coordonnées de contact.
- **Passerelle voix** : relie des domaines de téléphonie différents, par exemple IP et PSTN.
- **SBC (Session Border Controller)** : contrôle la frontière entre domaines SIP, applique des politiques et peut ancrer les médias.
- **RTP** : transporte les paquets audio en temps réel.

Une passerelle Cisco qui utilise des dial peers ne remplace pas nécessairement un PBX ou un registrar. Son rôle dépend de son architecture et de sa configuration.

## 4. SIP : les bases

### 4.1 Qu'est-ce que SIP ?

SIP est un protocole de signalisation défini par l'IETF. Il peut utiliser UDP, TCP ou TLS suivant les équipements et la configuration. Le port 5060 est couramment associé à SIP non chiffré et le port 5061 à SIP sur TLS, mais il faut vérifier le port réellement configuré : ce ne sont pas des valeurs universelles imposées à toute installation.

SIP peut établir une session audio, vidéo ou autre. Il ne garantit pas à lui seul la qualité de la voix et ne transporte pas à lui seul les échantillons audio de l'appel.

### 4.2 Les principales méthodes SIP

| Méthode | Rôle général |
|---|---|
| `INVITE` | Invite un correspondant à rejoindre une session. |
| `ACK` | Confirme la réception d'une réponse finale à un `INVITE` dans le mécanisme prévu par SIP. |
| `BYE` | Met fin à une session établie. |
| `CANCEL` | Annule une requête en cours, par exemple un appel qui sonne encore. |
| `REGISTER` | Enregistre une association entre une identité et un contact auprès d'un registrar. |
| `OPTIONS` | Interroge les capacités ou vérifie qu'un élément répond, selon l'usage. |
| `REFER` | Demande généralement à un UA d'initier une nouvelle requête, souvent utilisé pour le transfert. |
| `UPDATE` | Met à jour certains paramètres de session lorsqu'il est applicable. |

Attention : `CANCEL` et `BYE` ne sont pas interchangeables. `CANCEL` vise une transaction d'établissement encore en cours ; `BYE` termine une session déjà établie.

### 4.3 Réponses SIP fréquentes

| Code | Signification courante | Interprétation opérationnelle |
|---|---|---|
| `100 Trying` | La requête est en cours de traitement. | L'appel a été pris en charge par un élément SIP. |
| `180 Ringing` | Le correspondant est alerté. | Une sonnerie distante est signalée. |
| `183 Session Progress` | Progression de l'appel. | Peut s'accompagner d'un SDP et d'une tonalité précoce. |
| `200 OK` | Requête réussie. | Pour un INVITE, la session est généralement acceptée ; il faut ensuite l'ACK. |
| `301/302` | Redirection permanente/temporaire. | Le client peut devoir suivre un contact différent. |
| `400 Bad Request` | Requête invalide. | Vérifier la syntaxe ou la compatibilité du message. |
| `401/407` | Authentification requise. | Défi d'authentification au niveau UA/proxy. |
| `403 Forbidden` | Requête refusée. | La politique ou les autorisations bloquent l'appel. |
| `404 Not Found` | Destination inconnue. | Numéro ou URI non reconnu, selon le système. |
| `408 Request Timeout` | Délai dépassé. | Pas de réponse attendue dans le délai. |
| `480 Temporarily Unavailable` | Destination momentanément indisponible. | Téléphone hors service ou utilisateur indisponible, selon le contexte. |
| `486 Busy Here` | Occupé. | Le correspondant refuse car occupé. |
| `488 Not Acceptable Here` | Paramètres média non acceptables. | Codec, média ou paramètres SDP potentiellement incompatibles. |
| `500 Server Internal Error` | Erreur interne du serveur. | Chercher les journaux côté serveur. |
| `503 Service Unavailable` | Service indisponible. | Ressource indisponible ou surcharge possible. |

Un code de réponse n'est pas une preuve suffisante de la cause racine. Il faut lire la trace complète, les en-têtes, le SDP et les journaux de chaque équipement.

### 4.4 Lire un échange SIP simple

```text
A -> B : INVITE sip:2002@192.0.2.20 SIP/2.0
B -> A : SIP/2.0 100 Trying
B -> A : SIP/2.0 180 Ringing
B -> A : SIP/2.0 200 OK
A -> B : ACK sip:2002@192.0.2.20 SIP/2.0
     ... communication audio via RTP ...
A -> B : BYE sip:2002@192.0.2.20 SIP/2.0
B -> A : SIP/2.0 200 OK
```

Les adresses et messages ci-dessus sont illustratifs. Un appel réel peut contenir des messages provisoires supplémentaires, plusieurs jambes SIP et des échanges de mise à jour de session.

## 5. SDP, codecs, RTP et DTMF

### 5.1 À quoi sert SDP ?

SDP (*Session Description Protocol*) décrit les paramètres du média : type de média, adresse IP, port, formats et attributs. Il est souvent transporté dans le corps d'un message SIP, mais SDP n'est pas en lui-même un protocole de transport.

Extrait SDP simplifié :

```text
v=0
s=Appel voix
c=IN IP4 192.0.2.10
t=0 0
m=audio 20000 RTP/AVP 0 101
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-16
```

Dans cet exemple, `c=` indique une adresse média et `m=` annonce un flux audio sur le port 20000 avec certains types de charge utile. L'exemple est pédagogique, non une configuration complète à recopier telle quelle. L'espacement exact et la négociation dépendent des implémentations.

### 5.2 Les codecs

Un codec représente et compresse (ou non) l'audio :

- **G.711 mu-law (PCMU)** : courant en Amérique du Nord et dans de nombreux environnements IP ; débit audio de 64 kbit/s.
- **G.711 A-law (PCMA)** : courant dans de nombreux autres pays ; débit audio de 64 kbit/s.
- **G.729** : codec à débit réduit, soumis à des considérations de licence et de compatibilité selon la plateforme.
- **Opus** : codec à débit adaptable dans certains clients et plateformes, mais pas universellement disponible sur toutes les passerelles traditionnelles.

Le débit du codec ne représente pas le débit IP total. Il faut ajouter les en-têtes RTP, UDP, IP et de couche 2, ainsi que tenir compte de la périodicité des paquets.

### 5.3 RTP et RTCP

RTP transporte la voix. Il fournit notamment des numéros de séquence, des horodatages et l'identification du type de charge utile. RTCP peut fournir des statistiques de réception et des informations de contrôle.

**RTP n'assure pas à lui seul la livraison à temps, ne réserve pas la bande passante et ne garantit pas la QoS.** Le réseau doit être conçu pour limiter latence, gigue et pertes.

### 5.4 DTMF

Les touches du téléphone peuvent être transportées de plusieurs façons :

- dans la bande audio, méthode historique sensible à la compression ;
- sous forme d'événements RTP, souvent appelé `rtp-nte` sur Cisco IOS/IOS XE ;
- par des messages SIP tels que `INFO`, si les équipements l'acceptent.

Il faut que les deux extrémités et les équipements intermédiaires utilisent un mécanisme compatible. Le fait qu'un appel audio fonctionne ne prouve pas que les touches IVR fonctionneront.

## 6. Dial peers Cisco : principe

Un **dial peer** est une entrée de configuration qui décrit comment reconnaître ou acheminer une jambe d'appel. Sur une passerelle Cisco, on rencontre généralement :

- **dial peer POTS** : connecté à un port voix traditionnel (FXS, FXO, T1/E1 selon le matériel et les cartes) ;
- **dial peer VoIP** : achemine la signalisation et les médias à travers un réseau de paquets, par exemple SIP.

La disponibilité de chaque type dépend du matériel et de la version logicielle. Une passerelle purement logicielle ou une plateforme cloud peut présenter des modèles différents.

### 6.1 Comment se fait le routage ?

```text
Appel entrant
     |
     v
Identification du dial peer entrant
     |
     v
Traitement des chiffres / règles de traduction
     |
     v
Recherche du dial peer sortant selon la destination
     |
     v
Sélection de session cible ou port voix
     |
     v
Signalisation SIP / média RTP
```

Il est important de distinguer **le dial peer entrant** et **le dial peer sortant**. Le premier donne au routeur un contexte pour traiter l'appel reçu. Le second détermine vers où envoyer l'appel. Les critères précis de sélection dépendent du protocole, des champs présents dans le signal d'appel, des fonctions configurées et de la version IOS/IOS XE.

### 6.2 Attributs à connaître

| Commande / attribut | Rôle courant |
|---|---|
| `dial-peer voice 100 voip` | Crée un dial peer VoIP avec le tag 100. |
| `destination-pattern` | Définit le motif utilisé pour sélectionner un dial peer sortant ; sa fonction dans la sélection entrante est différente. |
| `incoming called-number` | Associe un appel entrant au numéro appelé (DNIS) correspondant. |
| `answer-address` | Peut faire correspondre le numéro appelant (ANI) pour sélectionner un dial peer entrant. |
| `session protocol sipv2` | Définit SIP version 2 comme protocole de session pour le dial peer. |
| `session target ipv4:192.0.2.20` | Indique la cible IP de la session sortante. |
| `port 0/0/0` | Associe un dial peer POTS à un port voix, si la plateforme le prend en charge. |
| `dtmf-relay rtp-nte` | Configure le relais des événements DTMF dans des paquets RTP. |
| `codec g711ulaw` | Sélectionne un codec pour le dial peer sur les plateformes qui prennent en charge cette syntaxe. |
| `no vad` | Désactive la détection d'activité vocale pour le contexte concerné. À ne pas copier sans comprendre l'impact. |

### 6.3 Exemple d'un dial peer VoIP sortant

```text
dial-peer voice 100 voip
 description Appels vers le site B
 destination-pattern 2...
 session protocol sipv2
 session target ipv4:192.0.2.20
 dtmf-relay rtp-nte
 codec g711ulaw
 no vad
```

Dans cet exemple pédagogique, les extensions commençant par `2` et comportant quatre chiffres peuvent correspondre au motif `2...` selon la sémantique de motifs de la plateforme. `session target` dirige la session vers l'adresse de l'autre passerelle. L'option DTMF et le codec doivent être cohérents avec l'équipement distant.

### 6.4 Exemple d'un dial peer entrant SIP

```text
dial-peer voice 200 voip
 description Appels SIP entrants pour les extensions du site A
 session protocol sipv2
 incoming called-number 1...
 dtmf-relay rtp-nte
 codec g711ulaw
```

Cet exemple montre un critère de numéro appelé. Dans une configuration de production, il faut également traiter explicitement les appels non reconnus, les appels provenant de pairs autorisés et la politique de sécurité. Un dial peer qui ne correspond pas peut aboutir au dial peer par défaut ou à un autre comportement de la plateforme ; cela doit être vérifié, jamais supposé.

## 7. Atelier guidé : relier deux passerelles SIP

### 7.1 Topologie du laboratoire

```text
Téléphones / PBX A                                  Téléphones / PBX B
extensions 1xxx                                      extensions 2xxx
      |                                                   |
      v                                                   v
+-------------------+       IP 192.0.2.0/24       +-------------------+
| GW-A              |-----------------------------| GW-B              |
| 192.0.2.10        |                             | 192.0.2.20        |
| dial peer vers 2xxx|                             | dial peer vers 1xxx|
+-------------------+                             +-------------------+
```

Le préfixe `192.0.2.0/24` est réservé à la documentation. Il faut le remplacer par un réseau de laboratoire effectivement isolé. Les exemples ne sont pas destinés à un réseau téléphonique public sans adaptation et revue de sécurité.

### 7.2 Configuration illustrative de GW-A

```text
configure terminal
!
voice service voip
 allow-connections sip to sip
!
dial-peer voice 120 voip
 description Vers-GW-B-extensions-2xxx
 destination-pattern 2...
 session protocol sipv2
 session target ipv4:192.0.2.20
 dtmf-relay rtp-nte
 codec g711ulaw
 no vad
end
```

La commande `allow-connections sip to sip` est nécessaire dans certains scénarios de transit SIP sur IOS/IOS XE, mais son utilité et sa prise en charge dépendent du rôle de la passerelle. Elle ne doit pas être ajoutée automatiquement à chaque équipement. Certaines versions utilisent des commandes ou des fonctions supplémentaires pour contrôler les connexions SIP.

### 7.3 Configuration illustrative de GW-B

```text
configure terminal
!
voice service voip
 allow-connections sip to sip
!
dial-peer voice 110 voip
 description Vers-GW-A-extensions-1xxx
 destination-pattern 1...
 session protocol sipv2
 session target ipv4:192.0.2.10
 dtmf-relay rtp-nte
 codec g711ulaw
 no vad
end
```

Ces extraits se concentrent sur le choix d'une destination. Une configuration complète dépend des interfaces, du routage IP, des règles d'entrée, du contrôle d'accès, des paramètres SIP globaux, de la politique de numérotation et des codecs réellement supportés.

### 7.4 Validation avant les tests

1. Vérifier que GW-A et GW-B peuvent joindre leurs adresses IP respectives.
2. Vérifier les routes IP et les ACL / pare-feu entre les passerelles.
3. Confirmer que les dial peers sont présents et correspondent aux numéros composés.
4. Effectuer un appel de test entre une extension `1xxx` et une extension `2xxx`.
5. Vérifier le retour audio dans les deux sens.
6. Tester les touches DTMF sur un IVR ou un service de test.
7. Arrêter l'appel normalement et examiner les journaux si le résultat diffère de l'attendu.

## 8. Commandes de vérification et de dépannage

Les commandes disponibles varient selon l'image IOS/IOS XE, les licences et la plateforme. L'aide contextuelle `?` reste utile.

```text
show dial-peer voice summary
show dial-peer voice 120
show running-config | section dial-peer
show running-config | section voice service voip
show ip interface brief
show ip route
```

Certaines plateformes prennent en charge des commandes de diagnostic telles que `debug ccsip messages`, `debug voip dialpeer` ou d'autres commandes VoIP. **Les commandes `debug` peuvent générer beaucoup de sortie et affecter un système chargé.** Les utiliser d'abord dans un laboratoire, ou en production pendant une fenêtre encadrée, avec une procédure de désactivation (`undebug all`) et une collecte conforme à la politique d'exploitation.

### 8.1 Problème : l'appel ne se route pas

Pistes de diagnostic :

- Le numéro réellement reçu est-il identique au motif attendu ?
- Un chiffre de sortie (préfixe) doit-il être ajouté ou retiré ?
- Le dial peer entrant est-il bien sélectionné ?
- Un autre dial peer correspond-il avant celui attendu selon les règles de sélection de la plateforme ?
- La cible `session target` est-elle correcte et routable ?
- Les ports et transports SIP sont-ils autorisés dans les deux sens ?
- L'autre côté accepte-t-il l'URI ou le numéro envoyé ?

### 8.2 Problème : l'appel aboutit, mais aucun son n'est entendu

Un appel SIP qui aboutit ne prouve pas que RTP circule. Vérifier :

- l'adresse et le port indiqués dans SDP (`c=` et `m=`) ;
- le routage IP dans les deux sens ;
- les pare-feu et ACL UDP sur la plage média configurée ;
- les adresses privées annoncées vers un réseau non routable ;
- la compatibilité du codec ;
- les fonctions NAT, SBC ou média qui peuvent modifier le chemin.

### 8.3 Problème : les touches DTMF ne fonctionnent pas

Vérifier que le téléphone, la passerelle et le service distant négocient un mécanisme commun. Inspecter le SDP, la configuration `dtmf-relay`, les journaux SIP et la présence d'événements RTP. Ne pas conclure que le DTMF est correctement transporté uniquement parce que la voix est audible.

## 9. Sécurité élémentaire

- Restreindre les flux SIP aux pairs autorisés et aux ports effectivement utilisés.
- Ne pas exposer directement une passerelle voix de laboratoire à Internet.
- Protéger les plans d'administration ; utiliser les mécanismes d'authentification et de chiffrement supportés.
- Contrôler les numéros accessibles : international, surtaxé et renvoi d'appel peuvent générer des coûts importants.
- Mettre en place une politique d'accès et un suivi des journaux.
- Masquer les numéros de téléphone, URI, adresses publiques et identifiants dans les captures partagées.

SIP sur TLS protège la signalisation en transit entre les points où TLS est effectivement établi. SRTP protège le média lorsqu'il est négocié et supporté. Le chiffrement ne dispense pas du contrôle d'accès ni d'une conception correcte de la confiance entre passerelles.

## 10. Exercices corrigés

### Exercice 1 — Signalisation ou média ?

Un `INVITE` est suivi d'un `200 OK` puis d'un `ACK`, mais les interlocuteurs ne s'entendent pas. Quelle famille de flux faut-il vérifier en priorité ?

**Correction :** le média RTP et les paramètres SDP, tout en vérifiant aussi les éventuelles erreurs de codec. La signalisation a apparemment progressé jusqu'à l'établissement de la session, mais cela ne prouve pas que les paquets audio circulent.

### Exercice 2 — Choisir la destination

Un utilisateur compose `2345`. Quel dial peer sortant de l'exemple débutant peut correspondre à ce numéro ?

**Correction :** le motif `2...` est conçu pour correspondre à un numéro à quatre chiffres commençant par 2. Il faut toutefois confirmer la sémantique et les autres dial peers configurés sur la passerelle.

### Exercice 3 — `CANCEL` ou `BYE` ?

Le téléphone de l'appelé sonne encore, mais l'appelant raccroche avant la réponse. Quelle méthode SIP est couramment utilisée pour annuler l'établissement ?

**Correction :** `CANCEL`. `BYE` sert à terminer une session déjà établie.

### Exercice 4 — DTMF

L'audio fonctionne, mais le serveur vocal ne reçoit pas les touches. Donner deux vérifications.

**Correction :** vérifier le mécanisme commun de relais DTMF (`rtp-nte` ou une méthode SIP compatible) et examiner le SDP / les traces pour confirmer la négociation et la transmission des événements.

### Exercice 5 — `404` contre `488`

Quelle différence générale entre ces réponses ?

**Correction :** `404 Not Found` indique qu'une destination ou ressource n'a pas été trouvée dans le contexte SIP concerné. `488 Not Acceptable Here` indique généralement que la requête ou les paramètres de session ne sont pas acceptables pour ce destinataire, souvent à examiner via SDP et codecs.

## 11. Défi final corrigé : appel intersite

### Situation

Deux sites sont reliés par IP. Le site A utilise `1xxx`, le site B `2xxx`. La passerelle A peut joindre la passerelle B sur IP. Les appels `2xxx` échouent, mais les pings réussissent.

### Travail demandé

1. Décrire les étapes de dépannage dans l'ordre.
2. Identifier le rôle du dial peer de sortie.
3. Identifier les contrôles nécessaires après établissement de l'appel.
4. Proposer des critères de sécurité minimaux.

### Correction attendue

1. Vérifier le numéro exact reçu par la passerelle, puis le dial peer entrant, les éventuelles traductions, le dial peer sortant correspondant, le protocole SIP, la cible de session et les traces de signalisation. Un ping ne teste ni la logique de routage des appels ni les ports SIP/RTP.
2. Le dial peer sortant qui correspond au numéro appelé doit orienter l'appel vers la cible IP attendue ; par exemple, le motif `2...` vers `192.0.2.20` dans la maquette.
3. Examiner les réponses SIP, l'ACK, le SDP, le codec, le trafic RTP dans les deux sens et le DTMF.
4. Autoriser uniquement les pairs connus, limiter les destinations, protéger l'administration, éviter toute exposition directe non contrôlée à Internet, documenter les versions logicielles et surveiller les appels anormaux.

Une solution bien présentée distingue **la connectivité IP**, **le routage de l'appel**, **la négociation média** et **le transport RTP** au lieu de traiter l'appel comme un seul flux indivisible.

## 12. Glossaire

- **ANI** : Automatic Number Identification, numéro associé à l'appelant.
- **DNIS** : Dialed Number Identification Service, numéro composé / appelé.
- **Dial peer** : objet de configuration Cisco qui aide à reconnaître ou acheminer un appel.
- **DTMF** : tonalités correspondant aux touches d'un clavier téléphonique.
- **SDP** : format de description des paramètres de session média.
- **SIP** : protocole de signalisation pour les sessions multimédias.
- **SBC** : Session Border Controller, fonction de contrôle des frontières SIP.
- **RTP/RTCP** : transport média temps réel et contrôle/statistiques associés.
- **POTS** : interface ou réseau téléphonique traditionnel dans la terminologie des passerelles Cisco.
- **PSTN** : réseau téléphonique public commuté.

## 13. Références techniques

- [RFC 3261 — SIP: Session Initiation Protocol](https://www.rfc-editor.org/rfc/rfc3261)
- [RFC 3264 — An Offer/Answer Model with SDP](https://www.rfc-editor.org/rfc/rfc3264)
- [RFC 8866 — SDP: Session Description Protocol](https://www.rfc-editor.org/rfc/rfc8866)
- [RFC 3550 — RTP: A Transport Protocol for Real-Time Applications](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 4733 — RTP Payload for DTMF Digits, Telephony Tones, and Telephony Signals](https://www.rfc-editor.org/rfc/rfc4733)
- [Cisco — Understand Matching Inbound/Outbound Dial Peers on IOS](https://www.cisco.com/c/en/us/support/docs/voice/call-routing-dial-plans/14074-in-dial-peer-match.html)
- [Cisco DevNet — SIP Dial Peer Configurations for IOS XE](https://developer.cisco.com/docs/ios-xe-voip/sip-dial-peer-configurations/)

Les documents RFC décrivent les protocoles. Les commandes Cisco doivent être confirmées dans le guide de configuration de la version et de la plateforme utilisées.
