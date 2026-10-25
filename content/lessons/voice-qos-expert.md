---
node_id: voice-qos-expert
title: QoS pour la Voix et Vidéo
---

# QoS Voix et Vidéo — Niveau expert

## Objectifs
Concevoir et valider une politique QoS de bout en bout pour la voix et la visioconférence, dimensionner les files, contrôler la gigue et la perte, et diagnostiquer les défauts dans un WAN congestionné.

## 1. Pourquoi la QoS est nécessaire
La QoS ne crée pas de bande passante : elle décide comment traiter les paquets lorsqu'il existe une contention. Les flux temps réel sont sensibles à la latence, à la variation de délai (gigue) et à la perte. La qualité dépend de tous les segments : accès, campus, WAN, tunnel, opérateur et réseau distant.

## 2. Marquage et classes

| Usage | DSCP courant | Traitement attendu |
|---|---:|---|
| Voix RTP contrôlée | EF 46 | file à faible latence avec limite |
| Signalisation voix | CS3 ou AF31 selon politique | classe prioritaire de contrôle, distincte du média |
| Vidéo interactive | AF41/AF42/AF43 selon politique | classe garantie/pondérée adaptée au débit |
| Applications critiques | AF/CS selon politique | traitement défini par besoin |
| Best effort | 0 | traitement par défaut |

Le marquage doit être accepté seulement depuis des sources de confiance. À l'accès, classifier et éventuellement remarquer ; ne pas faire confiance aveuglément au DSCP fourni par un poste utilisateur.

## 3. Pipeline QoS

```text
Entrée
  -> classification (port, VLAN, ACL, application)
  -> marquage DSCP/CoS
  -> policing ou shaping selon rôle
  -> files et ordonnanceur
  -> lien congestionné
  -> contrôle/validation des compteurs
```

- **Classification** : identifier les flux.
- **Marquage** : attribuer une classe.
- **Policing** : mesurer et supprimer ou remarquer le trafic au-delà du profil.
- **Shaping** : mettre en tampon et lisser le débit.
- **LLQ** : file à faible latence, généralement réservée à la voix avec un plafond.
- **WRED/AQM** : gestion préventive de congestion pour certaines classes, pas un remplacement de la bonne conception.

## 4. Calculs de bande passante

Pour un codec à débit (R), le débit IP réel inclut les en-têtes et la fréquence des paquets. Exemple simplifié : G.711 transporte 160 octets de charge utile par paquet à 20 ms, soit 50 paquets/s. Le seul payload est 64 kbit/s. Avec 40 octets d'en-têtes IPv4/UDP/RTP par paquet, l'overhead ajoute 16 kbit/s avant couche 2, tunnel, chiffrement et encapsulation. Le débit réel sur le lien est donc supérieur à 64 kbit/s par appel.

Pour dimensionner une file LLQ, additionner le débit de tous les appels simultanés, les en-têtes et la marge ; inclure l'encapsulation réellement présente. Ne pas allouer une file illimitée : une priorité non bornée peut affamer les autres classes.

## 5. Conception multi-sites

- Marquer à l'entrée, puis vérifier que le DSCP est préservé sur chaque saut.
- Appliquer des politiques cohérentes au campus, aux tunnels et au WAN.
- Aligner shaping du routeur sur le débit réellement disponible du circuit.
- Réserver la LLQ à la voix temps réel et définir un plafond adapté.
- Prévoir la signalisation séparément du média.
- Vérifier le comportement du fournisseur WAN et le mapping DSCP/CoS.
- Contrôler les MTU et la fragmentation, surtout dans les tunnels IPsec/SD-WAN.
- Sur Wi-Fi, intégrer WMM/AC_VO et la contention radio ; DSCP seul ne garantit pas la priorité.

## 6. Mesures et diagnostic

Mesurer délai aller-retour et, si possible, délai unidirectionnel, gigue, perte, utilisation, drops par classe, profondeur de file et taux de policing. RTCP et les outils de supervision peuvent compléter les compteurs d'interface. Une mesure moyenne peut masquer des pics ; examiner les percentiles et les périodes de congestion.

Symptômes :
- voix robotique : perte, gigue ou paquetisation ;
- délai excessif : chemin trop long, files ou traitement ;
- vidéo figée : débit insuffisant, perte, adaptation de débit ;
- voix dégradée uniquement à l'heure de pointe : congestion ou shaping mal aligné ;
- DSCP EF sans effet : marquage effacé, classe non appliquée ou congestion sur un segment non contrôlé.

## 7. Validation en laboratoire
1. Générer un flux RTP et un flux de données saturant un lien simulé.
2. Mesurer perte/gigue sans QoS.
3. Appliquer classification, marquage et LLQ bornée.
4. Refaire le test et comparer les compteurs.
5. Tester un marquage EF abusif depuis un poste non fiable et vérifier le remarking/policing.

## Exercices corrigés
1. **QoS augmente-t-elle la capacité ?** Non, elle gère la contention.
2. **Pourquoi plafonner LLQ ?** Pour éviter que le trafic prioritaire affame les autres classes.
3. **EF 46 sans amélioration :** vérifier confiance, conservation du marquage, classification, files et chaque segment du chemin.
4. **Pourquoi G.711 dépasse 64 kbit/s sur le lien ?** En-têtes RTP/UDP/IP, couche 2, tunnels et sécurité ajoutent de l'overhead.

## Défi final corrigé
Sur un WAN 20 Mbit/s, les appels sont bons hors pointe et dégradés pendant les sauvegardes. Mesurer drops et files ; classifier voix par une source fiable, marquer EF, appliquer LLQ limitée, façonner juste sous le débit effectif du circuit et placer les sauvegardes dans une classe moins prioritaire. Tester aussi le mapping DSCP chez le fournisseur et les effets des tunnels. Comparer avant/après sur gigue, perte et compteurs.

## Références
- RFC 4594 — Guidelines for DiffServ Service Classes : https://www.rfc-editor.org/rfc/rfc4594
- RFC 3246 — Expedited Forwarding PHB : https://www.rfc-editor.org/rfc/rfc3246
- Cisco QoS Design Guides : https://www.cisco.com/
