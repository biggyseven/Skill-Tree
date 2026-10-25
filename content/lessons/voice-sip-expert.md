# Protocole SIP & Dial Peers — Expert

## Mise en contexte

Le niveau expert ne consiste pas à accumuler des commandes. Il consiste à concevoir un service voix prévisible, sécurisé et observable même lorsque plusieurs PBX, SBC, opérateurs SIP, réseaux IP, plans de numérotation et politiques de média interagissent.

Ce cours couvre l'ingénierie du routage sur les passerelles Cisco IOS/IOS XE, les architectures multi-trunks, les subtilités de sélection SIP, les conversions de signalisation, la sécurité et la méthodologie d'analyse d'incident. Les exemples sont pédagogiques et doivent être adaptés à la version, aux fonctions et au contexte réglementaire réels.

## 1. Objectifs experts

À l'issue du cours, tu devras pouvoir :

- modéliser une architecture à plusieurs jambes SIP et identifier les points de terminaison ;
- concevoir une stratégie de dial-peer matching explicite, sans dépendre d'un défaut implicite ;
- structurer une normalisation E.164 et des transformations par frontière ;
- raisonner sur Request-URI, `From`, `To`, `Contact`, `Diversion`, `History-Info` et `P-Asserted-Identity` ;
- analyser Early Offer, Delayed Offer, Early Media, UPDATE, re-INVITE, transfert et renvoi ;
- construire une route primaire/secours et éviter boucles et bascules dangereuses ;
- diagnostiquer les erreurs interopérabilité SIP/SDP/RTP/DTMF ;
- limiter les risques de fraude, usurpation d'identité et épuisement de ressources ;
- définir des tests de charge, de panne, de régression et une procédure de rollback ;
- conduire un incident avec des preuves corrélées et des hypothèses falsifiables.

## 2. Architecture multi-domaines et modèle d'appel

### 2.1 Un appel n'est pas toujours une unique session

```text
Téléphone / CUCM
       |
       | Jambe SIP A
       v
+---------------------+
| Passerelle / SBC A  |  Termine ou adapte la jambe A
+---------------------+
       |
       | Jambe SIP B, numéros ou SDP éventuellement réécrits
       v
+---------------------+
| SBC / opérateur     |
+---------------------+
       |
       | Jambe SIP C éventuelle
       v
Réseau distant / PSTN
```

Un équipement de type B2BUA peut agir comme point de terminaison d'une jambe et créer une autre session. Les Call-ID, tags, numéros, URI, en-têtes, offres SDP et ports RTP peuvent différer entre les jambes. Pour reconstruire le parcours, il faut corréler les traces par temps, adresses, numéros et journaux de l'équipement, pas uniquement par un seul Call-ID.

### 2.2 Séparer les plans

- **Plan de signalisation** : SIP, routage des requêtes, transactions et dialogues.
- **Plan média** : RTP/RTCP, codecs, ports, traduction d'adresse, ancrage et QoS.
- **Plan de contrôle** : politiques de numérotation, autorisation, capacités, supervision et admission.
- **Plan d'administration** : SSH/HTTPS, AAA, journalisation, sauvegardes et contrôle de changement.

Une panne peut affecter un plan sans affecter les autres. Par exemple, SIP peut établir un appel alors que le chemin RTP est bloqué ; ou RTP peut être audible tandis que le transfert échoue en raison d'une méthode SIP non prise en charge.

## 3. Ingénierie du dial-peer matching

### 3.1 Conception : une intention par règle

Un dial peer doit avoir une intention claire : source entrante, classe d'appel autorisée, normalisation, destination et caractéristiques média. Les règles trop larges rendent le comportement imprévisible, augmentent le risque de transit non souhaité et compliquent les diagnostics.

Pour chaque dial peer important, documenter :

- tag et description ;
- interface/tenant/VRF lorsque ces mécanismes sont utilisés ;
- critère de sélection entrante (URI, numéro appelé, numéro appelant ou autre) ;
- format de numéro supposé à l'entrée ;
- translation profile entrant/sortant ;
- destination-pattern, URI de destination ou groupe de serveurs ;
- codecs et mécanisme DTMF ;
- politique TLS/SRTP et confiance ;
- préférences, hunting et comportement de secours ;
- classe d'appel autorisée et tests de sécurité associés.

### 3.2 Sélection entrante SIP

IOS/IOS XE peut sélectionner un dial peer entrant à partir de plusieurs catégories de critères. Les préférences et les commandes disponibles varient selon le protocole et la version. Les critères SIP peuvent inclure l'URI de Via, Request-URI, To, From, le numéro appelé (`incoming called-number` ou pattern map), le numéro appelant (`answer-address` ou pattern map) et, dans certains contextes, des critères de destination-pattern. Des fonctions tenant/VRF peuvent ajouter d'autres contraintes.

Méthode correcte :

1. relever les valeurs exactes du message reçu ;
2. déterminer le premier critère de matching applicable pour la version utilisée ;
3. vérifier quel dial peer est réellement choisi dans une trace ;
4. éliminer les règles qui peuvent capturer involontairement le trafic ;
5. ajouter un cas de test pour chaque changement.

Ne pas reprendre une liste de priorité d'une ancienne version comme une loi universelle. Utiliser la documentation de la version IOS/IOS XE et les résultats observés sur la plateforme.

### 3.3 Dial peer 0 et chemins par défaut

Le dial peer 0 ou tout mécanisme de repli peut être activé lorsque le routage explicite n'identifie aucun pair entrant. Sa capacité codec, DTMF, marquage et autres comportements peut différer du contexte souhaité. Un design de production doit prévoir le cas « aucune règle ne correspond » et vérifier qu'il ne crée ni transit ouvert, ni chemin de facturation imprévu, ni négociation média dégradée.

### 3.4 Prévenir les collisions de motifs

Un plan complexe peut contenir :

- des motifs de postes internes ;
- des codes de service ;
- des préfixes de sortie ;
- des destinations internationales ;
- des appels d'urgence ;
- des numéros courts opérateur ;
- des URI SIP pour partenaires ;
- des règles de renvoi et de transfert.

Construire une matrice de décision plutôt qu'une série de motifs ad hoc :

| Classe | Exemple fictif | Autorisation | Route | Transformation |
|---|---|---|---|---|
| Extension interne | `2xxx` | Utilisateurs internes | PBX/cluster interne | Normalisation interne |
| National | préfixe national défini | Groupe téléphonie autorisé | Trunk opérateur | Préfixe/format opérateur validé |
| International | format E.164 hors pays | Liste d'autorisations | Trunk approuvé | E.164 sans ambiguïté |
| Numéro d'urgence | numéro officiel local | Tous les profils concernés selon règle locale | Route d'urgence dédiée | Règles réglementaires locales |
| Surtaxé / haut risque | plages définies localement | Refus ou approbation | Aucune route par défaut | Blocage explicite |

Les numéros et règles d'urgence dépendent du pays et de l'opérateur. Les exemples ne doivent pas être utilisés comme définition réglementaire.

## 4. Normalisation et transformations E.164

### 4.1 Modèle en couches

Une stratégie maîtrisable distingue :

1. **Format de présentation** : ce que l'utilisateur compose.
2. **Format canonique interne** : représentation stable utilisée par le routage.
3. **Format de sortie par trunk** : format attendu par le PBX/opérateur de destination.
4. **Identité appelante** : numéro présenté et identité affirmée, soumis à une politique différente du numéro appelé.

Ne pas utiliser une même translation pour des usages différents sans vérifier les conséquences sur `called`, `calling`, `redirect-called` et les autres champs pris en charge.

### 4.2 Règles de traduction et ordre de traitement

Les voice translation rules Cisco fonctionnent avec des règles de correspondance et de modification. L'ordre est important : une règle correspondante antérieure peut empêcher l'application d'une règle ultérieure. Une translation profile applique les translations à un champ précis et peut être associé à une direction du dial peer ou à un autre point de configuration supporté.

Exemple de laboratoire : retirer le préfixe 9 d'un numéro à huit chiffres. La longueur est fictive et doit être adaptée :

```text
voice translation-rule 10
 rule 1 /^9\(........\)$/ /\1/
!
voice translation-profile NORMALIZE-LOCAL
 translate called 10
```

Avant tout usage, tester au minimum :

- format valide et longueurs limites ;
- format trop court et trop long ;
- numéro avec `+` ou code pays ;
- numéro privé, anonyme ou absent ;
- numéros de service, urgence et haut risque ;
- appel transféré ou renvoyé ;
- identité appelante et numéro appelé séparément.

Les translation rules manipulent des champs numériques d'appel pris en charge. La modification d'URI non numérique dans des en-têtes SIP peut exiger des fonctions distinctes, telles que des SIP profiles, et relève d'une analyse différente. Ne pas tenter de changer n'importe quel texte SIP avec une règle de numérotation.

### 4.3 Prévenir les boucles et les doubles transformations

Une passerelle A peut ajouter un préfixe, B le supprimer, puis A le rajouter après un renvoi : la même destination se retrouve transformée plusieurs fois. Pour prévenir cela :

- définir le format canonique à chaque frontière ;
- documenter où la transformation se fait ;
- éviter d'appliquer la même normalisation à l'entrée et à la sortie sans raison ;
- tester les transferts et renvois en plus des appels simples ;
- limiter les possibilités de renvoi vers le trunk d'origine ;
- conserver des exemples de numéros avant/après chaque frontière.

## 5. SIP avancé et interopérabilité

### 5.1 Transaction, dialogue, fork et B2BUA

Un `INVITE` peut être relayé à plusieurs destinations (forking) ; plusieurs réponses provisoires et finales peuvent apparaître. Les réponses `200 OK` à plusieurs branches doivent être traitées avec les mécanismes SIP appropriés, dont ACK et éventuellement BYE pour les dialogues non retenus. Un B2BUA peut modifier la structure et l'identification de ces échanges. Lors du dépannage, ne pas supposer qu'une seule réponse `180` ou qu'un seul Call-ID décrit toute la tentative.

### 5.2 En-têtes et identité

- `From` : identité de présentation dans le message ; non authentifiée en soi.
- `P-Asserted-Identity` : identité affirmée au sein d'un domaine de confiance selon les règles du service.
- `Remote-Party-ID` : en-tête historique encore rencontré, avec un statut et une interopérabilité dépendant de l'écosystème.
- `Diversion` et `History-Info` : informations de renvoi ou d'historique selon les implémentations.
- `Contact` : adresse utilisée pour atteindre un UA dans certaines requêtes ultérieures.
- `Record-Route` / `Route` : mécanismes de routage au sein des dialogues.

La politique doit déterminer quelle entité est autorisée à définir l'identité appelante. Ne pas faire confiance à une identité reçue d'un trunk public sans validation. Vérifier aussi la cohérence entre numéro présenté, autorisations et politique opérateur.

### 5.3 Re-INVITE et UPDATE

Les messages `re-INVITE` ou `UPDATE` peuvent modifier des paramètres de session, y compris des aspects du média et du SDP. Des équipements intermédiaires peuvent les filtrer, les transformer ou les rejeter. Les problèmes apparaissent souvent lors du hold/resume, de la mise en attente, du transfert, du changement de média ou de la réoptimisation du chemin RTP.

Lors de l'analyse, tracer l'état avant/après la modification : méthodes, CSeq, SDP, direction média (`sendrecv`, `sendonly`, `recvonly`, `inactive`), réponses et état RTP. Vérifier les temporisations et les rôles offerer/answerer.

### 5.4 Transfert et renvoi

Le transfert peut utiliser `REFER`, un nouveau dialogue, un transfert piloté par PBX ou une logique propriétaire. `302 Moved Temporarily`, `Diversion`, `History-Info` et d'autres éléments peuvent apparaître dans les scénarios de renvoi. Le comportement dépend du terminal, du PBX, du SBC et de l'opérateur. Documenter les scénarios : transfert annoncé, transfert aveugle, renvoi inconditionnel, sur occupation et sur non-réponse.

Vérifier, pour chaque scénario :

- quelle entité prend la décision de renvoyer ;
- quels numéros et identités sont transmis ;
- si la route de sortie autorise la destination ;
- si le média reste ancré ou est réoptimisé ;
- si les compteurs d'appel et la facturation sont corrects ;
- si une boucle de renvoi est possible.

## 6. SDP et média à un niveau avancé

### 6.1 Offre/réponse et compatibilité

SDP décrit les formats et adresses média ; le modèle offre/réponse définit comment les paramètres sont proposés et acceptés. Les incompatibilités peuvent venir d'un ensemble de codecs vide, d'un payload type mal géré, d'attributs incompatibles, de la direction média, d'un port ou d'une adresse incorrecte ou de différences d'implémentation.

Éviter les conclusions trop rapides : un `488` peut être causé par plusieurs paramètres, et deux offres affichant « G.711 » peuvent encore différer sur la loi A/µ, les paquets, les événements téléphoniques ou des paramètres de sécurité.

### 6.2 Early Offer, Delayed Offer et Early Media

Pour chaque interface SIP, documenter le mode d'offre attendu, le traitement des réponses provisoires, la gestion du SDP et les mécanismes de conversion réellement pris en charge. Une passerelle peut agir comme B2BUA et réécrire le SDP, mais les fonctions spécifiques dépendent du modèle et de l'image logicielle.

L'absence de sonnerie distante peut être due à l'absence d'Early Media, alors que le téléphone génère une sonnerie locale. Inversement, du média peut commencer avant la réponse finale, ce qui demande de maîtriser l'ouverture et la fermeture des chemins RTP.

### 6.3 RTP, RTCP, DTMF et qualité

RTP utilise des numéros de séquence, horodatages et types de charge utile. RTCP peut signaler des pertes, de la gigue et des éléments de synchronisation. Ils ne garantissent pas une livraison à temps et ne réservent pas la capacité réseau.

Pour la DTMF, analyser les méthodes négociées sur chaque jambe : événements RTP type `telephone-event` (`rtp-nte` dans la terminologie Cisco), messages SIP compatibles ou audio en bande. Une passerelle peut devoir convertir entre les méthodes, si elle supporte cette fonction. Comparer les payload types et les traces des deux côtés.

### 6.4 Calcul de capacité média

Un codec à 64 kbit/s ne signifie pas que l'appel consomme exactement 64 kbit/s sur le réseau IP. Un flux avec paquets de 20 ms émet typiquement 50 paquets par seconde et ajoute en-têtes RTP/UDP/IP et de couche 2. La surcharge dépend de IPv4/IPv6, VLAN, tunnel, sécurité, encapsulation et paquetisation.

Méthode de dimensionnement :

1. établir le codec et l'intervalle de paquetisation ;
2. calculer le nombre de paquets par seconde ;
3. ajouter les en-têtes de chaque couche du chemin ;
4. calculer dans les deux sens ;
5. tenir compte des appels simultanés, du silence éventuel, de SRTP et des tunnels ;
6. réserver de la marge pour les pics et autres applications.

Un calcul théorique ne remplace pas une mesure de trafic réel et le dimensionnement des files QoS.

## 7. Architecture de routes primaires et secours

### 7.1 Les questions de conception

- Quel type d'échec déclenche le secours : absence de réponse, rejet explicite, panne de next-hop, saturation, ou autre ?
- Une route secondaire est-elle réellement indépendante (fournisseur, lien, alimentation, route IP) ?
- Les deux opérateurs acceptent-ils le même format et la même identité appelante ?
- Les règles de sécurité s'appliquent-elles à la route de secours ?
- La bascule risque-t-elle une boucle ou une double tentative de facturation ?
- Comment la route est-elle surveillée et testée périodiquement ?

### 7.2 Logique de routage

```text
Appel normalisé et autorisé
             |
             v
       Route principale
             |
      résultat d'appel
       /          \
  succès        échec admissible
    |                |
  fin          route de secours
                     |
             résultat contrôlé
```

La préférence d'un dial peer, le hunting et la sélection par groupe de serveurs ne sont pas équivalents. La configuration exacte dépend des fonctions IOS/IOS XE disponibles. Les règles de bascule doivent être documentées et testées avec chaque code de réponse pertinent.

### 7.3 Test de défaillance

En laboratoire ou pendant une fenêtre approuvée :

1. noter la route utilisée lorsque tout est normal ;
2. simuler une panne supportée sans provoquer de trafic incontrôlé ;
3. observer le dial peer sélectionné et la cause de bascule ;
4. vérifier les numéros transmis au trunk secondaire ;
5. vérifier la réponse finale et l'audio ;
6. restaurer la route principale ;
7. vérifier le retour au chemin nominal et les journaux ;
8. conserver les résultats comme preuve de test.

## 8. Sécurité expert

### 8.1 Modèle de menace

Les risques incluent :

- appels frauduleux à destinations coûteuses ;
- falsification des numéros ou URI présentés ;
- transit SIP non autorisé ;
- en-têtes malformés ou tentatives de déni de service ;
- balayage de numéros et d'interfaces d'administration ;
- fuite de métadonnées sensibles dans des traces ;
- mauvaise séparation entre plan d'administration et plan de voix ;
- politiques TLS/SRTP incohérentes entre les jambes.

### 8.2 Défenses en couches

1. **Filtrage réseau** : autoriser seulement les adresses et ports requis pour les peers légitimes ; définir précisément les plages média.
2. **Contrôle de routage** : aucune destination externe sans politique explicite ; deny par défaut pour les préfixes dangereux ; routes d'urgence distinctes et validées.
3. **Identité et confiance** : ne faire confiance aux en-têtes affirmés qu'à partir de pairs/domaines autorisés ; appliquer une politique de numéros présentés.
4. **Transport** : TLS et SRTP lorsque supportés et requis, avec gestion correcte des certificats, algorithmes et échéances.
5. **Administration** : AAA, SSH/HTTPS, comptes nominatifs, sauvegardes protégées, accès via réseau de gestion.
6. **Surveillance** : taux d'appels, refus, échecs, destinations inhabituelles, tentatives répétées, utilisation CPU/mémoire et événements de sécurité.
7. **Cycle de vie** : versions supportées, analyse des vulnérabilités, sauvegarde et tests de restauration.

TLS protège une connexion de signalisation ; il ne chiffre pas automatiquement le RTP. SRTP doit être réellement négocié sur les segments pertinents. Un SBC ou une passerelle qui termine une session peut créer une nouvelle frontière de confiance.

## 9. Observabilité et méthodologie d'incident

### 9.1 Jeu minimal de preuves

Pour un appel affecté, recueillir (en accord avec la politique de confidentialité) :

- horodatage avec fuseau et synchronisation NTP ;
- identifiant d'appel local, adresses IP et sens de l'appel ;
- numéros d'origine/destination masqués lorsque requis ;
- dial peers entrant et sortant réellement sélectionnés ;
- captures SIP expurgées des secrets ;
- SDP avant/après la passerelle ;
- traces RTP/RTCP ou statistiques qualité ;
- réponses SIP et élément qui les émet ;
- état du trunk, interfaces, ACL, CPU et ressources média ;
- résultat attendu, résultat observé et tests comparatifs.

Ne partage jamais des traces contenant des mots de passe, tokens, identifiants personnels ou données d'abonné sans autorisation et expurgation. Les traces voix peuvent constituer des données sensibles.

### 9.2 Arbre de diagnostic

```text
L'appel n'aboutit pas ou n'est pas utilisable
             |
             +-- SIP INVITE sort-il du bon équipement ?
             |       +-- non : sélection entrante, autorisation, dial peer de sortie
             |       +-- oui : vérifier transport, routage IP et réponse distante
             |
             +-- réponse finale reçue ?
             |       +-- non : reachability, filtrage, timer, transport, retour
             |       +-- oui, échec : code, en-têtes, politique, chiffres, SDP
             |
             +-- appel établi mais audio absent ?
             |       +-- SDP, adresses, ports, RTP, ACL/NAT, codec, ancrage média
             |
             +-- audio correct mais DTMF/transfer échoue ?
                     +-- négociation DTMF, REFER/re-INVITE, politique PBX/trunk
```

La méthode doit produire une hypothèse testable, puis une observation qui peut la confirmer ou la réfuter. Éviter la modification simultanée de plusieurs composants : elle empêche d'isoler la cause.

## 10. Atelier expert 1 — Matrice de dial plan et test de non-régression

### Situation fictive

Une entreprise utilise :

- extensions `1xxx` et `2xxx` ;
- un préfixe de sortie `9` ;
- un trunk principal vers `192.0.2.30` ;
- un trunk de secours vers `192.0.2.31` ;
- une politique interdisant certains appels internationaux.

Ces adresses et numéros sont réservés à l'exemple ; le plan d'accès international est volontairement laissé à la politique locale approuvée.

### Livrables demandés

1. Une matrice des classes d'appels et autorisations.
2. Un diagramme de sélection entrant/sortant.
3. Une liste de règles de traduction avec exemples avant/après.
4. Des cas positifs et négatifs, notamment numéros incomplets et préfixes interdits.
5. Un plan de rollback.

### Correction modèle

- Les appels intersites restent dans la classe de routage interne et ne sont pas envoyés au trunk PSTN.
- Les appels externes doivent passer par une classe explicitement autorisée.
- Les préfixes interdits sont bloqués avant la sélection d'une route de sortie, avec une règle de blocage vérifiable.
- La normalisation interne utilise un format canonique stable ; le format spécifique au fournisseur est appliqué uniquement à la frontière appropriée.
- Chaque règle a un ensemble de tests qui démontre qu'elle correspond au cas prévu et ne capture pas les numéros de sécurité, de service ou de longueur différente.
- Le secours doit respecter la même politique d'accès, les mêmes restrictions et les exigences de présentation d'identité.
- Le rollback restaure la configuration sauvegardée et confirme à nouveau les appels internes, urgences, appels nationaux autorisés et appels interdits.

## 11. Atelier expert 2 — Incompatibilité SDP

### Symptôme

L'INVITE atteint le SBC. L'appel reçoit `488 Not Acceptable Here`. Une autre route vers le même destinataire fonctionne.

### Analyse demandée

1. Comparer l'offre SDP entre route qui échoue et route qui fonctionne.
2. Identifier codecs, payload types, paramètres, directions média, adresse/port, profil RTP et exigences de chiffrement.
3. Déterminer où le `488` est émis.
4. Examiner les capacités de conversion de la passerelle et les changements de configuration récents.

### Correction attendue

Le code `488` seul ne suffit pas à identifier le paramètre refusé. Il faut comparer les offres et réponses SDP sur chaque jambe, examiner les codecs réellement communs, les paramètres RTP/DTMF et les exigences SRTP. La route qui fonctionne peut passer par un autre SBC ou profil de média ; comparer les chemins complets. Toute modification de codec ou de mode offre/réponse est testée sur les scénarios d'appels entrants, sortants, hold/resume, transfert, Early Media et DTMF.

## 12. Atelier expert 3 — Audio unidirectionnel à travers NAT

### Symptôme

L'établissement SIP est correct, mais seul l'appelant entend l'appelé.

### Méthode

1. Extraire le SDP de chaque jambe.
2. Comparer les adresses `c=` et ports `m=` à la topologie réelle.
3. Capturer RTP avant et après la frontière NAT/SBC si possible.
4. Confirmer les routes retour, les ACL et la plage UDP média autorisée.
5. Vérifier si la passerelle ancre les médias ou laisse un chemin direct.
6. Tester en laboratoire une correction isolée et confirmer les deux sens RTP.

### Correction attendue

Les causes fréquentes comprennent une adresse privée annoncée dans SDP, un port média non autorisé, un mapping NAT expiré, une route retour manquante ou une politique d'ancrage incohérente. La capture doit prouver quel équipement émet vers quel IP:port, plutôt que de supposer que le problème est nécessairement un « pare-feu SIP ».

## 13. Atelier expert 4 — Analyse de DTMF et transfert

### Scénario

Les appels et l'audio sont corrects, mais les touches d'un IVR ne fonctionnent pas et un transfert échoue.

### Correction attendue

Traiter les deux symptômes séparément :

- Pour DTMF, comparer `telephone-event` et les payload types SDP, la configuration `dtmf-relay`, les paquets RTP et toute conversion entre méthodes.
- Pour le transfert, examiner si le scénario emploie `REFER`, un nouveau `INVITE`, un re-INVITE ou une logique propriétaire ; suivre les codes de réponse, l'identité de la cible, les permissions de route et les changements de média.
- Vérifier que les règles de sécurité autorisent le transfert uniquement vers les destinations voulues.

La correction ne doit pas être de supprimer globalement les restrictions de trunk ou de permettre tout transfert sans contrôle.

## 14. Plan de mise en production

### Avant

- revue par pair ;
- sauvegarde de configuration et vérification de restauration ;
- matrice des dial peers, préfixes et routes ;
- tests couvrant les appels autorisés, interdits, urgences, transferts et DTMF ;
- dépendances de la version IOS/IOS XE et avis de sécurité vérifiés ;
- fenêtre et rollback approuvés.

### Pendant

- changement limité à un ensemble identifiable ;
- validation par étapes ;
- collecte de traces avec durée et volume contrôlés ;
- appels de contrôle représentatifs ;
- seuil clair d'abandon/rollback.

### Après

- tests de non-régression ;
- confirmation du routage primaire/secours ;
- suivi des taux d'échec, réponses SIP, qualité média et volumes ;
- documentation de configuration réellement déployée ;
- suppression des traces temporaires conformément à la politique de rétention.

## 15. Exercices corrigés

### Exercice 1 — Le Call-ID change entre deux frontières

**Question :** est-ce forcément une anomalie ?

**Correction :** non. Un B2BUA peut terminer une jambe SIP et en créer une autre, avec de nouveaux identifiants et en-têtes. Il faut corréler les jambes via les journaux, le temps, les adresses et les numéros.

### Exercice 2 — `P-Asserted-Identity` reçu d'un trunk inconnu

**Correction :** ne pas lui faire confiance automatiquement. Définir des domaines de confiance et accepter/propager l'identité selon la politique et l'authentification de la source.

### Exercice 3 — Un `488` est renvoyé

**Correction :** comparer les SDP offerts/répondus, codec, attributs, payload types, ports, profil RTP et sécurité média sur les deux jambes. Identifier l'élément qui produit la réponse. Le code seul ne désigne pas une cause unique.

### Exercice 4 — Les appels basculent vers le trunk secondaire, mais échouent là aussi

**Correction :** vérifier que le secondaire reçoit le bon format de numéro, que la route de secours est autorisée, que les identités présentées sont acceptées et que ses critères média sont compatibles. Le secours doit être testé indépendamment et en situation de panne.

### Exercice 5 — RTP circule dans un seul sens

**Correction :** comparer les adresses et ports SDP à ceux observés dans les captures, vérifier NAT, route retour, ACL, ancrage média et la présence réelle de RTP dans chaque sens.

### Exercice 6 — Tous les numéros peuvent sortir parce qu'un dial peer large est nécessaire

**Correction :** réduire le périmètre du motif, appliquer une politique d'autorisation explicite, séparer les classes d'appels et tester les destinations interdites. Une route large ne doit pas remplacer le contrôle d'accès.

## 16. Défi final corrigé — Réseau voix résilient multi-trunks

### Contexte

Une entreprise à deux sites utilise un PBX, une passerelle IOS XE et deux trunks SIP de fournisseurs différents. Les symptômes observés sont :

- certains appels internationaux passent par le fournisseur secondaire malgré une route primaire disponible ;
- les numéros appelants changent de format selon la route ;
- quelques appels ont une voix à sens unique ;
- les touches DTMF sont irrégulières sur les IVR ;
- le renvoi d'appel peut réintroduire un numéro dans le réseau de départ.

### Travail à effectuer

1. Concevoir la matrice de numérotation et d'autorisation.
2. Décrire l'analyse du choix de dial peer et du basculement.
3. Proposer une normalisation d'identité et de numéro appelé.
4. Établir une méthode de diagnostic RTP/SDP.
5. Définir les tests DTMF/transfert/renvoi.
6. Définir les mesures de sécurité et les critères de validation.

### Correction détaillée

**1. Plan de numérotation.** Définir un format canonique interne puis la conversion requise pour chaque trunk. Distinguer le numéro appelé et l'identité appelante. Décrire séparément les plages internes, les appels nationaux, internationaux, urgences, services et destinations interdites. Un appel non autorisé doit être refusé explicitement.

**2. Routage et secours.** Journaliser le dial peer entrant et sortant sélectionné, les numéros avant/après translation, le trunk choisi, la réponse SIP et la condition ayant déclenché le hunting. Vérifier la préférence et les conditions d'échec sur la version IOS XE exacte. Tester perte de connectivité, absence de réponse et différents rejets. Prévenir les boucles et garantir que le secours n'élargit pas les autorisations.

**3. Identité.** Définir quels numéros sont autorisés pour chaque trunk. Appliquer les transformations uniquement à la frontière nécessaire et selon une politique commune. Contrôler `From`, `P-Asserted-Identity` et les en-têtes de renvoi ; ne pas considérer l'en-tête reçu d'un trunk comme fiable par défaut.

**4. Audio.** Corréler SDP de chaque jambe, IP/ports annoncés, codec, payload types et état RTP réel. Capturer le trafic aux frontières clés. Vérifier route de retour, NAT, ACL, plage média et fonctions d'ancrage. Séparer panne de négociation d'une absence de transport.

**5. DTMF et renvoi.** Comparer `telephone-event` et la configuration DTMF sur chaque jambe, puis tester IVR avec plusieurs chiffres. Tracer le mécanisme de transfert et les numéros renvoyés ; appliquer une limite de renvoi et empêcher le retour vers le trunk d'origine lorsque cela crée une boucle.

**6. Contrôles.** Autoriser les pairs connus, segmenter le plan de gestion, utiliser TLS/SRTP lorsque nécessaires et supportés, surveiller les volumes et préfixes à risque, protéger les traces, sauvegarder la configuration et valider le rollback.

### Critères de réussite

- chaque classe de numéro a une route explicite et une politique d'autorisation ;
- le format numéro/identité est cohérent sur chaque fournisseur ;
- le basculement a un déclencheur documenté et aucune boucle ;
- appels bidirectionnels, DTMF, hold/resume, transfert et renvoi sont testés ;
- les preuves montrent SIP, SDP et RTP sur les points pertinents ;
- la procédure de rollback a été exécutée ou validée de manière démontrable.

## 17. Glossaire

- **B2BUA** : élément qui termine une jambe SIP et crée une autre jambe.
- **CAC** : contrôle d'admission d'appel, selon le contexte de l'architecture.
- **Delayed Offer / Early Offer** : modes de présentation de l'offre SDP.
- **Dial peer** : objet de routage d'appel Cisco IOS/IOS XE.
- **Early Media** : média avant réponse finale.
- **E.164** : plan international de numérotation publique.
- **Forking** : émission d'une requête vers plusieurs cibles potentielles.
- **Hunting** : tentative d'autres routes ou destinations selon la logique configurée.
- **P-Asserted-Identity** : identité affirmée dans un domaine de confiance.
- **SDP** : format de description des paramètres média.
- **SBC** : Session Border Controller.
- **SRTP** : profil sécurisé de transport RTP.

## 18. Références techniques

- [RFC 3261 — SIP: Session Initiation Protocol](https://www.rfc-editor.org/rfc/rfc3261)
- [RFC 3264 — An Offer/Answer Model with SDP](https://www.rfc-editor.org/rfc/rfc3264)
- [RFC 8866 — SDP: Session Description Protocol](https://www.rfc-editor.org/rfc/rfc8866) — remplace RFC 4566
- [RFC 3550 — RTP: A Transport Protocol for Real-Time Applications](https://www.rfc-editor.org/rfc/rfc3550)
- [RFC 4733 — RTP Payload for DTMF Digits, Telephony Tones, and Telephony Signals](https://www.rfc-editor.org/rfc/rfc4733)
- [RFC 3325 — Private Extensions for Asserted Identity within Trusted Networks](https://www.rfc-editor.org/rfc/rfc3325)
- [RFC 3323 — A Privacy Mechanism for SIP](https://www.rfc-editor.org/rfc/rfc3323)
- [Cisco — Understand Matching Inbound/Outbound Dial Peers](https://www.cisco.com/c/en/us/support/docs/voice/call-routing-dial-plans/14074-in-dial-peer-match.html)
- [Cisco — In-Depth Explanation of IOS and IOS XE Call Routing](https://www.cisco.com/c/en/us/support/docs/voice/ip-telephony-voice-over-ip-voip/211306-In-Depth-Explanation-of-Cisco-IOS-and-IO.html)
- [Cisco DevNet — SIP Dial Peer Configurations](https://developer.cisco.com/docs/ios-xe-voip/sip-dial-peer-configurations/)

Les commandes et le comportement de routage doivent être validés dans la documentation du train IOS/IOS XE réellement exploité. Les configurations d'exemple ne remplacent pas la revue du plan d'appel, la politique opérateur ni les procédures de changement du réseau.
