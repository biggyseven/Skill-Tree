# Protocole SIP & Dial Peers — Intermédiaire

## Mise en contexte

Au niveau débutant, tu as appris à lire un échange SIP, à distinguer la signalisation du média et à construire des dial peers simples. En production, le défi est moins d'écrire un `destination-pattern` que de maîtriser la sélection entrante, la normalisation des numéros, la négociation SDP, les routes de secours, les politiques de sécurité et l'analyse des échecs.

Ce niveau approfondit l'exploitation d'une passerelle Cisco IOS/IOS XE interconnectée à un PBX, à CUCM, à un opérateur SIP ou à une autre passerelle. Les syntaxes et fonctions disponibles varient par version, plateforme et licences : valider les commandes dans la documentation correspondante avant déploiement.

## 1. Compétences visées

À la fin du cours, tu sauras :

- expliquer la sélection du dial peer entrant selon les critères SIP et l'information disponible ;
- construire un plan de numérotation avec règles de traduction entrantes et sortantes ;
- utiliser les notions de préférence et de route de secours sans créer de boucles ;
- interpréter les codes SIP, les en-têtes importants et les corps SDP ;
- analyser codecs, DTMF, Early Offer/Delayed Offer et Early Media ;
- concevoir une stratégie de dépannage structurée ;
- sécuriser l'accès SIP et limiter les appels à risque ;
- documenter et tester une modification de dial plan.

## 2. Rappel d'architecture

```text
Téléphones / CUCM ---- SIP trunk ---- Passerelle IOS-XE ---- SIP trunk / PSTN
       |                                     |                       |
       | signalisation                       | signalisation          |
       +-------------- RTP direct, relayé ou ancré selon l'architecture --------+
```

Les appels peuvent comporter plusieurs jambes. Un `INVITE` entrant côté passerelle peut conduire à un nouvel `INVITE` sortant qui possède ses propres Call-ID, tags, SDP et états de transaction. Une passerelle B2BUA ou un SBC peut terminer une jambe SIP et en créer une autre. Ne suppose donc pas qu'un identifiant ou un en-tête reste identique de bout en bout.

## 3. Comprendre le choix des dial peers

### 3.1 Entrant contre sortant

Le routage des appels est généralement un processus en deux étapes :

1. **Sélection entrante** : associer l'appel reçu à un contexte d'entrée à partir des informations disponibles (URI SIP, numéro appelé, numéro appelant, etc.).
2. **Sélection sortante** : chercher un dial peer adapté au numéro appelé / à la destination, puis choisir une session cible ou un port.

La règle `destination-pattern` n'a pas une signification unique dans toutes les situations. Pour la sélection sortante, elle correspond au numéro appelé. Pour certaines étapes de sélection entrante, elle peut aussi être utilisée comme critère secondaire de numéro appelant, selon le protocole et la plate-forme. La sélection SIP IOS/IOS XE peut tenir compte de l'URI dans les en-têtes `Via`, Request-URI, `To` ou `From`, selon les commandes configurées. Le processus exact dépend de la version et des caractéristiques d'appel.

### 3.2 Critères entrants fréquemment utilisés

| Critère | Utilité habituelle | Risque d'erreur courant |
|---|---|---|
| `incoming uri request` | Sélection par URI de requête SIP. | Le Request-URI diffère de la valeur supposée par l'administrateur. |
| `incoming uri from` | Sélection basée sur l'identité URI de l'émetteur. | L'en-tête `From` n'est pas une identité authentifiée à lui seul. |
| `incoming called-number` | Sélection via le numéro appelé. | Le numéro est normalisé différemment ou absent. |
| `answer-address` | Sélection basée sur le numéro appelant. | Le CLI présenté est masqué ou change selon le trunk. |
| `destination-pattern` | Sert principalement à la sélection sortante ; peut participer à la sélection entrante dans certains contextes. | Supposer que le même motif est évalué de façon identique à l'entrée et à la sortie. |

Un appel entrant sans dial peer explicite peut, selon la plateforme, être associé au dial peer 0 ou à un mécanisme par défaut. Le comportement de repli peut avoir des capacités et une politique différentes du dial peer attendu. Il ne faut pas s'appuyer sur ce comportement comme politique de sécurité.

### 3.3 Examiner la sélection sans deviner

Pour chaque appel de test, consigner :

- protocole et interface d'entrée ;
- Request-URI, `From`, `To`, numéro appelé et numéro appelant reçus ;
- dial peer entrant réellement sélectionné ;
- transformations appliquées ;
- chiffres finaux envoyés à la recherche sortante ;
- dial peer sortant et session target sélectionnés ;
- réponse SIP et paramètres SDP.

Les traces `debug` changent selon les images. Tester d'abord sur un équipement de laboratoire, activer la trace au minimum utile et désactiver toute trace immédiatement après le test.

## 4. Normalisation du plan de numérotation

### 4.1 Séparer reconnaissance et transformation

Une architecture robuste sépare généralement trois décisions :

1. **Quel appel est-ce ?** Sélectionner le contexte entrant.
2. **Quel numéro logique doit-on utiliser ?** Normaliser vers un format interne cohérent, par exemple E.164 lorsque c'est adapté.
3. **Où acheminer cet appel ?** Sélectionner le dial peer sortant, puis appliquer la transformation finale requise par le réseau de destination.

Exemple conceptuel :

```text
Numéro reçu :     9 61234567
          |
          v  retirer le préfixe d'accès national 9
Numéro interne :  61234567
          |
          v  normaliser selon la politique d'entreprise
Format logique :  +23761234567
          |
          v  route externe, après contrôle d'autorisation
Destination :     opérateur SIP approuvé
```

Il s'agit d'une illustration ; la numérotation réelle et les règles nationales doivent être vérifiées pour le pays et l'opérateur. N'applique pas une règle globale qui retire ou ajoute des chiffres sans tests de toutes les plages concernées.

### 4.2 Exemple de translation rule

Les exemples ci-dessous illustrent une syntaxe classique IOS/IOS XE. Le motif suppose un préfixe d'accès `9` suivi de huit chiffres. Adapter les longueurs et valider la regex sur la plateforme :

```text
voice translation-rule 10
 rule 1 /^9\(........\)$/ /\1/
!
voice translation-profile PSTN-OUT
 translate called 10
!
dial-peer voice 300 voip
 description Vers-operateur-SIP
 destination-pattern 0T
 translation-profile outgoing PSTN-OUT
 session protocol sipv2
 session target ipv4:192.0.2.30
 dtmf-relay rtp-nte
 codec g711alaw
```

Cette illustration doit être adaptée : la ligne `destination-pattern 0T` ne couvre pas nécessairement tous les plans de numérotation, et la translation ci-dessus ne décrit qu'un cas de numérotation précis. Tester les chiffres avant et après transformation avec des exemples valides, invalides, limites, numéros d'urgence et numéros à accès restreint. Ne jamais modifier le routage des numéros d'urgence sans procédure et validation réglementaire locale.

### 4.3 Ordre de préférence et routes alternatives

Les dial peers peuvent être associés à une préférence ou à d'autres mécanismes de sélection pour proposer une route principale et une route de secours. La préférence ne doit pas être confondue avec une preuve de disponibilité réelle : le comportement de sélection, les causes d'échec qui déclenchent une nouvelle tentative et le mécanisme de hunting dépendent de l'implémentation.

Exemple de conception logique :

```text
Appels autorisés vers l'extérieur
              |
              v
       Route principale
       opérateur SIP A
              |
       échec admissible ?
          /       \
        non        oui
        |           |
       fin     route de secours
               opérateur SIP B
```

Planifier les tests de panne et vérifier qu'un appel ne reboucle pas entre opérateurs. Les routes alternatives ne doivent pas contourner les restrictions de numérotation.

## 5. Lire correctement SIP en production

### 5.1 En-têtes utiles

| Élément | Rôle diagnostique |
|---|---|
| `Call-ID` | Identifie une session ou transaction logique selon l'architecture ; utile pour corréler les messages d'une même jambe. |
| `Via` | Décrit les éléments de transport traversés et le chemin de réponse de la transaction. |
| `From` / `To` | Identités logiques présentées dans le dialogue ; elles ne sont pas en elles-mêmes une preuve d'authentification. |
| `Contact` | Indique une adresse de contact, utilisée notamment pour les requêtes futures dans le dialogue. |
| `Route` / `Record-Route` | Participent au routage des requêtes dans un dialogue via des proxys. |
| `CSeq` | Associe une séquence et une méthode aux requêtes. |
| `Max-Forwards` | Limite le nombre de relais SIP pour prévenir les boucles. |
| `P-Asserted-Identity` | Identité affirmée dans un domaine de confiance lorsqu'il est utilisé conformément à la politique ; ne doit pas être accepté aveuglément de sources inconnues. |
| `Diversion` / `History-Info` | Peuvent renseigner sur renvois ou historique, selon la plateforme et l'usage. |

### 5.2 Transaction, dialogue et appel

Ces termes sont proches mais ne sont pas identiques :

- Une **transaction SIP** correspond à une requête et à ses réponses associées selon les règles SIP.
- Un **dialogue** est une relation SIP de plus longue durée, identifiée notamment par Call-ID et tags locaux/distants.
- Un **appel** est une notion utilisateur/opérationnelle qui peut comprendre plusieurs dialogues ou jambes SIP.

Cette distinction aide à comprendre les transferts, forks, B2BUA et scénarios multi-trunks.

### 5.3 Les codes SIP comme indices

| Réponse | Vérifications possibles |
|---|---|
| `401` / `407` | Défi d'authentification attendu ? Réponse avec `Authorization` / `Proxy-Authorization` ? Boucle de défi ? |
| `403` | Politique d'autorisation, identité appelante, restrictions de trunk ou filtrage de numéros. |
| `404` | URI appelée, plan de numérotation, route et format des chiffres. |
| `408` | Atteignabilité, pare-feu, transport, minuterie ou absence de réponse. |
| `484 Address Incomplete` | Numéro incomplet, longueur attendue ou collecte des chiffres. |
| `486` | Occupation réelle, supervision d'état ou logique de ligne. |
| `488` | Offre SDP, codecs, profils RTP ou paramètres média. |
| `491 Request Pending` | Requête de modification de session simultanée ou gestion du dialogue. |
| `500` / `503` | Erreur d'élément, surcharge, service distant indisponible ou erreur transitoire. |
| `603 Decline` | Refus explicite, à interpréter avec le contexte et la politique. |

Ne transforme pas automatiquement un code en diagnostic définitif. Examiner la première réponse qui change le résultat de l'appel et identifier l'équipement qui l'a émise.

## 6. SDP, offre/réponse et Early Media

### 6.1 Modèle offre/réponse

SIP transporte fréquemment une offre SDP et une réponse SDP. Ces descriptions permettent de négocier les codecs, adresses, ports, directions média et options compatibles. L'offre et la réponse peuvent se trouver dans différents messages selon le scénario : par exemple dans un `INVITE`, dans une réponse provisoire ou finale, ou dans une requête de modification de session.

### 6.2 Early Offer et Delayed Offer

- **Early Offer** : le premier `INVITE` contient déjà une offre SDP.
- **Delayed Offer** : le `INVITE` n'inclut pas d'offre SDP ; l'offre est présentée plus tard dans le flot de signalisation.

L'interopérabilité peut échouer lorsque deux équipements exigent des modes différents ou traitent différemment le SDP absent. Les mécanismes de conversion dépendent des capacités de la passerelle, du SBC et de la version logicielle. Ne force pas un mode dans un réseau de production sans analyser les équipements adjacents et les scénarios d'appel.

### 6.3 Early Media

Une réponse `183 Session Progress` peut contenir SDP et permettre un média avant réponse finale, par exemple tonalité distante ou annonce d'opérateur. Les politiques réseau, la passerelle et le PBX doivent être cohérents sur la gestion du média précoce et des messages provisoires.

### 6.4 Diagnostic d'un audio à sens unique

1. Comparer le SDP offert et accepté sur les deux jambes.
2. Vérifier les adresses `c=` et ports `m=` après chaque transformation de signalisation.
3. Vérifier le codec commun, les payload types et les paramètres associés.
4. Confirmer que le routage et les règles de pare-feu autorisent RTP/RTCP dans le sens nécessaire.
5. Vérifier NAT, adresse d'interface de média, SBC et ancrage média.
6. Capturer des paquets à la frontière appropriée pour confirmer l'émission et la réception.

## 7. DTMF, codec et qualité média

### 7.1 DTMF par événements RTP

`rtp-nte` est une forme courante de configuration Cisco pour relayer les touches sous forme d'événements RTP (souvent négociés via SDP avec `telephone-event`). Vérifier les types de charge utile et la compatibilité des équipements. Si une extrémité attend de l'audio en bande et l'autre des événements RTP, les touches peuvent échouer même si la voix fonctionne.

### 7.2 Choix de codec

Le choix d'un codec doit considérer :

- support sur chaque extrémité ;
- bande passante avec surcharge de paquetisation ;
- qualité subjective et durée de paquetisation ;
- transcodage nécessaire et ressources disponibles ;
- compatibilité avec les fonctions de conférence, enregistrement, fax ou IVR.

Éviter de forcer un codec dans un seul dial peer sans vérifier les régions média, préférences ou capacités de la plateforme complète.

### 7.3 Mesures qualité

- **Latence** : délai de transit. Un délai trop grand rend la conversation difficile.
- **Gigue** : variation de délai, gérée partiellement par le tampon de gigue du récepteur.
- **Perte de paquets** : paquets RTP perdus, particulièrement dommageables pour la voix.
- **MOS** : estimation de qualité perceptuelle ; la valeur dépend de la méthode et des mesures réellement utilisées.

RTP fournit les mécanismes de séquence et d'horodatage utiles au suivi, mais ne garantit pas une qualité de service. La qualité dépend aussi du réseau, des files d'attente, des codecs et des terminaux.

## 8. Sécuriser et contrôler les appels

### 8.1 Principe de moindre privilège

- Autoriser les appels entrants uniquement depuis des pairs connus.
- Restreindre les préfixes accessibles à chaque classe d'appelant.
- Bloquer les appels non nécessaires vers les destinations internationales, surtaxées ou à haut risque.
- Contrôler les renvois, transferts et identités présentées.
- Séparer le plan d'administration du plan voix.
- Contrôler les ports, transports SIP, interfaces de bind et plages média réellement utilisés.
- Garder IOS/IOS XE et les équipements SIP sur des versions supportées et appliquer la gestion des vulnérabilités.

### 8.2 TLS, SRTP et confiance

TLS protège la signalisation sur le segment où la session TLS est établie. SRTP protège les médias lorsque les mécanismes cryptographiques ont été négociés et sont supportés de bout en bout ou sur les jambes appropriées. Si une passerelle termine une session puis en crée une autre, le chiffrement peut s'arrêter à cette frontière et reprendre séparément : inspecter l'architecture, pas seulement l'icône « sécurisé » d'un téléphone.

Les en-têtes d'identité comme `From` ne sont pas une authentification en soi. Un domaine de confiance peut utiliser des en-têtes affirmés, mais ne doit pas accepter ces valeurs de n'importe quelle source.

## 9. Atelier 1 — Normalisation d'un numéro

### Objectif

Retirer un préfixe d'accès `9` d'un numéro local de huit chiffres et envoyer le numéro normalisé vers une route approuvée. Cette règle n'est qu'un exercice de laboratoire ; elle ne doit pas être employée comme règle générale pour les numéros d'urgence ni pour des plages de longueur variable.

```text
voice translation-rule 10
 rule 1 /^9\(........\)$/ /\1/
!
voice translation-profile REMOVE-ACCESS-CODE
 translate called 10
!
dial-peer voice 300 voip
 description LAB-SIP-TRUNK
 destination-pattern 9........
 translation-profile outgoing REMOVE-ACCESS-CODE
 session protocol sipv2
 session target ipv4:192.0.2.30
 dtmf-relay rtp-nte
 codec g711alaw
```

### Tests obligatoires

| Entrée composée | Résultat à vérifier |
|---|---|
| `961234567` | Huit chiffres sans le préfixe `9`, si la règle exacte est supportée telle quelle. |
| `96123456` | Ne doit pas être traité comme un numéro valide si la longueur attendue est neuf chiffres au total. |
| `991234567` | Vérifier qu'aucun chiffre autre que le préfixe prévu n'est supprimé. |
| numéro d'urgence | Doit suivre une route d'urgence explicitement conçue, jamais une règle générale aveugle. |

Après chaque essai, observer les chiffres avant/après traduction, le dial peer sélectionné et le numéro réellement envoyé à l'opérateur.

## 10. Atelier 2 — Deux routes SIP avec secours

### Architecture de laboratoire

```text
                  +-- Trunk primaire 192.0.2.30
Réseau interne ---|   opérateur A
                  +-- Trunk secondaire 192.0.2.31
                      opérateur B
```

Les routes de secours peuvent être configurées au moyen de préférences, de groupes de destinations ou d'autres fonctions disponibles dans la version déployée. Le snippet exact varie selon la plateforme ; il est préférable de confirmer le modèle pris en charge avant de figer la configuration.

Travail demandé :

1. Définir la route principale et la route secondaire.
2. Déterminer quels codes d'échec doivent permettre une nouvelle tentative.
3. Vérifier si la passerelle peut basculer sur certains échecs, et dans quelles conditions.
4. Tester la panne du trunk principal en laboratoire.
5. Vérifier que les appels d'urgence et les destinations restreintes ne contournent pas la politique.
6. Détecter toute boucle de renvoi entre les trunks.

**Correction conceptuelle :** l'objectif n'est pas seulement d'avoir deux `session target`. Il faut maîtriser le mécanisme de sélection et de hunting réellement supporté, les causes déclenchant le secours, la limitation des tentatives et la cohérence des numéros envoyés aux deux opérateurs.

## 11. Atelier 3 — Analyse d'une trace SIP

Trace abrégée :

```text
GW-A -> SBC : INVITE sip:+23761234567@sbc.example
SBC  -> GW-A : 100 Trying
SBC  -> GW-A : 183 Session Progress (SDP)
SBC  -> GW-A : 488 Not Acceptable Here
```

### Analyse

Le `100 Trying` signifie que la requête est en cours de traitement, pas qu'un appel a été établi. Le `183` peut annoncer du progrès et, avec SDP, une description média précoce. Le `488` signale que la demande ou les paramètres de session ne sont pas acceptables pour le destinataire. Il faut comparer l'offre SDP initiale, les codecs, le type de charge utile, les attributs, le mode offre/réponse et les capacités du SBC. Il faut aussi vérifier quelle jambe a réellement émis le `488` et si une traduction média a eu lieu.

Ne pas conclure que « le codec G.711 ne marche pas » sans examiner le SDP et la configuration réels.

## 12. Méthode d'exploitation : changer sans casser

Avant modification :

1. Exporter et sauvegarder la configuration.
2. Relever les numéros concernés, la route actuelle et l'impact métier.
3. Écrire des cas de test positifs et négatifs.
4. Prévoir une fenêtre, un plan de rollback et une personne de validation.
5. Vérifier les dépendances entre dial peers, translations, classes de codec, SIP profiles, ACL et routes IP.

Après modification :

1. Exécuter les tests représentatifs et les tests de non-régression.
2. Confirmer le dial peer entrant et sortant réellement sélectionné.
3. Contrôler signalisation, média et DTMF.
4. Observer les journaux et compteurs pendant une période définie.
5. Documenter la version finale et le rollback réellement testé.

## 13. Exercices corrigés

### Exercice 1 — Le ping réussit, l'appel échoue

**Correction :** le ping confirme seulement une forme de connectivité IP ICMP entre les adresses. Il ne confirme ni la sélection du dial peer, ni le routage de numéros, ni l'accessibilité SIP, ni l'interopérabilité SDP/RTP. Examiner ces éléments séparément.

### Exercice 2 — Appel entrant associé au mauvais contexte

**Correction :** relever Request-URI, `From`, `To`, le numéro appelé et le numéro appelant réellement reçus. Examiner les critères entrants configurés (`incoming uri`, `incoming called-number`, `answer-address`, etc.) et l'ordre/priorité de sélection documenté pour cette version. Ne pas résoudre le problème en ajoutant des motifs très larges sans mesurer les effets.

### Exercice 3 — Appel sonne, mais la tonalité distante est absente

**Correction :** vérifier les réponses provisoires, le SDP présent ou absent dans `183`, le chemin média précoce, le traitement des alertes par la passerelle et la politique du PBX/opérateur. La sonnerie locale peut être générée par le terminal sans média distant.

### Exercice 4 — Une route de secours cause une boucle

**Correction :** identifier les numéros et en-têtes d'appel à chaque frontière, les transformations successives et les conditions de hunting. Ajouter une politique explicite pour que la route de secours n'envoie pas l'appel vers une passerelle qui le renvoie à la source. Tester les pannes et les codes de réponse en laboratoire.

### Exercice 5 — DTMF fonctionne dans un sens seulement

**Correction :** comparer la négociation et le trafic DTMF des deux jambes. Vérifier `telephone-event`, `rtp-nte`, les types de payload et la conversion éventuelle d'un mécanisme à un autre. Les événements peuvent être relayés ou terminés par une passerelle ; il faut analyser chaque jambe.

### Exercice 6 — TLS est activé, donc le média est chiffré

**Correction :** faux. TLS protège la signalisation sur le transport TLS. Le média a besoin de SRTP ou d'un autre mécanisme approprié, négocié et supporté. Vérifier chaque segment et chaque terminaison.

## 14. Défi final corrigé — Interconnexion d'entreprise

### Scénario

Une entreprise dispose de deux sites. Les extensions sont `1xxx` et `2xxx`. Les appels internes fonctionnent. Les appels externes passent par un trunk principal et doivent utiliser un trunk secondaire en cas d'indisponibilité. Certains préfixes internationaux sont interdits. Les appels vers le serveur vocal fonctionnent sans transfert DTMF fiable.

### Tâches

1. Définir une séquence de normalisation des numéros.
2. Décrire l'approche pour la route principale et le secours.
3. Donner les vérifications pour l'échec DTMF.
4. Proposer une politique de sécurité et de contrôle.
5. Décrire la preuve minimale à collecter avant mise en production.

### Correction détaillée

1. Définir un format interne canonique, distinguer préfixes locaux et formats E.164, puis créer des translations précises par classe de numéro. Éviter une règle générale qui s'applique aux numéros d'urgence ou à des longueurs non prévues. Tester tous les cas limites.
2. Configurer la route primaire et la route secondaire avec les fonctions de préférence/hunting supportées par la plateforme. Choisir les conditions d'échec de bascule, limiter les boucles et vérifier que le trunk secondaire applique la même politique d'autorisation.
3. Examiner la négociation SDP pour `telephone-event`, la configuration DTMF de chaque dial peer, les captures RTP et les conversions entre méthodes éventuelles. Vérifier si le DTMF fonctionne à l'entrée et à la sortie de la passerelle.
4. Restreindre les sources SIP, autoriser des numéros selon le rôle, interdire les préfixes risqués, protéger les trunks par les mécanismes de transport/authentification supportés, contrôler renvois et transferts, surveiller les volumes d'appel.
5. Collecter la configuration approuvée, le schéma du chemin d'appel, les traces SIP expurgées, la confirmation de sélection des dial peers, les résultats de tests média/DTMF, les tests négatifs, les statistiques de qualité et le plan de retour arrière.

## 15. Glossaire

- **B2BUA** : élément qui termine une jambe SIP et crée une autre jambe côté opposé.
- **Delayed Offer** : offre SDP présentée après le premier INVITE.
- **Dial peer entrant** : règle/contexte associé à l'appel reçu.
- **Dial peer sortant** : règle utilisée pour orienter l'appel vers la destination.
- **DNIS / ANI** : numéro composé / numéro associé à l'appelant.
- **Early Media** : média échangé avant la réponse finale de l'appel.
- **E.164** : plan de numérotation international public.
- **Hunting** : recherche d'une autre route ou destination selon les règles configurées.
- **SDP** : description des médias et des paramètres de session.
- **SBC** : contrôleur de frontière de sessions.

## 16. Références

- [RFC 3261 — SIP](https://www.rfc-editor.org/rfc/rfc3261)
- [RFC 3264 — Offer/Answer](https://www.rfc-editor.org/rfc/rfc3264)
- [RFC 8866 — SDP](https://www.rfc-editor.org/rfc/rfc8866)
- [RFC 3550 — RTP/RTCP](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 4733 — DTMF in RTP](https://www.rfc-editor.org/rfc/rfc4733)
- [Cisco — Matching inbound/outbound dial peers](https://www.cisco.com/c/en/us/support/docs/voice/call-routing-dial-plans/14074-in-dial-peer-match.html)
- [Cisco — In-depth explanation of IOS/IOS XE call routing](https://www.cisco.com/c/en/us/support/docs/voice/ip-telephony-voice-over-ip-voip/211306-In-Depth-Explanation-of-Cisco-IOS-and-IO.html)
- [Cisco DevNet — SIP dial peer configuration](https://developer.cisco.com/docs/ios-xe-voip/sip-dial-peer-configurations/)
