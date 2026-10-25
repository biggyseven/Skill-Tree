---
node_id: voice-sip-intermediaire
title: Protocole SIP & Dial Peers
---

# Protocole SIP et Dial Peers — Niveau intermédiaire

## Objectifs et prérequis
Lire un échange SIP, distinguer signalisation et média, comprendre SDP, les codes de réponse, les dial peers Cisco IOS et les premières causes d'échec. Prérequis : téléphonie IP et routage de base.

## 1. SIP et RTP

SIP (Session Initiation Protocol) établit, modifie et termine les sessions. SDP décrit les paramètres média négociés. RTP transporte généralement la voix ; RTCP fournit des informations de contrôle/qualité. SIP n'est pas le protocole qui transporte les échantillons audio.

```text
Téléphone A / CUBE ---------------- Téléphone B / opérateur
      |                                    |
      | INVITE + SDP                       |
      |----------------------------------->|
      | 100 Trying / 180 Ringing            |
      |<-----------------------------------|
      | 200 OK + SDP                        |
      |<-----------------------------------|
      | ACK                                 |
      |----------------------------------->|
      |========== RTP / RTCP ===============|
      | BYE / réponse 200 pour terminer     |
```

Les échanges exacts varient selon les services, les proxies et la présence d'un SBC/CUBE. Un INVITE peut être suivi de réponses provisoires, d'une réponse finale et d'un ACK. CANCEL annule une tentative en cours ; BYE termine une session établie.

## 2. Codes SIP à connaître

- **100 Trying** : la requête est traitée.
- **180 Ringing** : la destination sonne.
- **183 Session Progress** : progression, parfois avec média précoce.
- **200 OK** : succès pour la méthode concernée.
- **401/407** : authentification demandée.
- **403 Forbidden** : requête refusée.
- **404 Not Found** : destination introuvable.
- **408 Request Timeout** : délai expiré.
- **486 Busy Here** : occupé.
- **488 Not Acceptable Here** : paramètres de session non acceptables.
- **503 Service Unavailable** : service temporairement indisponible.

Un code seul ne suffit pas : corréler le message, le Call-ID, les en-têtes, le SDP et les journaux des deux côtés.

## 3. SDP et négociation média

SDP peut annoncer l'adresse IP, le port UDP, le type de média et les codecs acceptés. Les erreurs courantes sont une adresse privée annoncée vers un réseau distant, des ports bloqués, des codecs incompatibles ou une mauvaise gestion du NAT. L'audio unidirectionnel est souvent un problème de chemin média, pas de routage de l'appel.

## 4. Dial peers Cisco IOS

Les dial peers définissent comment traiter et acheminer les appels. Les dial peers **POTS** relient typiquement le plan de numérotation à une interface téléphonique ou à une passerelle circuit ; les dial peers **VoIP** acheminent les appels sur IP, souvent via SIP.

Exemple pédagogique (adapter les interfaces, numéros et politiques à la maquette) :

```text
! Appels vers les extensions 2xxx par SIP vers un serveur de test
dial-peer voice 200 voip
 description Vers-PBX-laboratoire
 destination-pattern 2...
 session protocol sipv2
 session target ipv4:192.0.2.20
 codec g711ulaw
 dtmf-relay rtp-nte
 no vad
```

Le code ci-dessus est un exemple de syntaxe IOS et ne doit pas être copié en production sans validation. Vérifier la version IOS/IOS XE, le contexte de configuration, les codecs autorisés et la stratégie de sécurité.

Les critères de sélection peuvent inclure destination-pattern, incoming called-number, ports/URI selon la plate-forme et la configuration dial-peer. Éviter les motifs trop larges qui capturent involontairement des appels.

## 5. Dépannage structuré

1. Confirmer la route de numérotation et le dial peer sélectionné.
2. Vérifier la connectivité IP, le routage et les ACL.
3. Lire les messages SIP dans l'ordre, en corrélant Call-ID et horodatages.
4. Contrôler l'authentification, les en-têtes et les réponses finales.
5. Comparer les offres/réponses SDP, codecs et ports.
6. Vérifier RTP dans les deux sens et la présence d'un SBC/CUBE/NAT.
7. Capturer des traces de laboratoire ; activer les débogages avec prudence en production.

Commandes de vérification possibles selon plateforme et version : `show dial-peer voice summary`, `show voice call summary`, `show sip-ua status`. Les commandes de debug SIP peuvent produire beaucoup de données et révéler des numéros ; limiter la durée et protéger les captures.

## 6. TP et exercices corrigés

**TP :** créer un dial peer VoIP de laboratoire vers un PBX simulé, appeler une extension 2xxx, capturer SIP et RTP, puis tester un codec incompatible et une ACL RTP bloquante.

1. **INVITE transporte-t-il la voix ?** Non, il initie la session ; RTP transporte généralement l'audio.
2. **488 indique quoi ?** Les paramètres de session ne sont pas acceptables, souvent à examiner dans SDP/codecs.
3. **Appel sonne mais aucun audio :** comparer SDP, NAT, ACL et flux RTP bidirectionnels.
4. **Quel rôle du dial peer ?** Sélectionner le traitement et la destination d'un appel selon les critères configurés.

## Défi final corrigé
Les appels sortants reçoivent 404. Vérifier le numéro composé, le pattern de destination, le dial peer sélectionné, la normalisation du numéro et la réponse de la destination. Si la session reçoit 200 OK mais aucun son, basculer l'investigation sur SDP et RTP plutôt que modifier le plan de numérotation.

## Glossaire et références
SIP, SDP, RTP, RTCP, INVITE, ACK, BYE, dial peer, CUBE.
- RFC 3261 — SIP : https://www.rfc-editor.org/rfc/rfc3261
- RFC 4566 — SDP : https://www.rfc-editor.org/rfc/rfc4566
- Cisco IOS Voice Configuration : https://www.cisco.com/
