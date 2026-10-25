# Téléphonie IP CUCM — Intermédiaire

## Mise en contexte : passer d'une téléphonie qui fonctionne à une téléphonie bien conçue

Au niveau débutant, tu as découvert l'architecture Cisco Unified Communications Manager (CUCM), l'enregistrement des téléphones IP, le plan de numérotation, les notions SIP/RTP, la QoS et les premiers contrôles de dépannage.

Le niveau intermédiaire s'intéresse à ce qui rend une plateforme de téléphonie exploitable à l'échelle d'une entreprise : un plan de numérotation lisible, des routes sortantes maîtrisées, des trunks SIP robustes, des règles de transformation cohérentes, une qualité vocale contrôlée par site, une continuité de service en cas de coupure WAN et une méthode de diagnostic fondée sur les traces.

Ce cours utilise une entreprise fictive appelée **Atlas Services**. Elle possède un siège à Douala et une agence à Yaoundé. Les extensions, adresses IP et numéros présentés sont des exemples réservés au laboratoire. Ils doivent être adaptés à l'environnement réel avant toute mise en production.

> **Objectif opérationnel :** être capable de concevoir et de dépanner un scénario CUCM multi-sites avec routage entrant et sortant, redondance de chemins, règles de numérotation, QoS, contrôle de bande passante et survivabilité locale.

## 1. Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- concevoir des partitions et des Calling Search Spaces (CSS) à partir d'une matrice de droits d'appel ;
- distinguer un route pattern, un translation pattern et un transformation pattern ;
- construire la chaîne route pattern → route list → route group ;
- organiser les trunks et les passerelles pour obtenir une stratégie de routage résiliente ;
- comprendre les rôles des device pools, régions, locations et codecs ;
- identifier l'action des ressources médias telles que MTP, transcoder, conférence et Music on Hold ;
- intégrer un trunk SIP en tenant compte de la sécurité et de l'interopérabilité ;
- expliquer l'intérêt et les limites de SRST ;
- diagnostiquer un appel qui échoue, un appel établi sans audio ou une qualité vocale dégradée ;
- produire un plan de validation et un compte rendu de changement.

## 2. Prérequis et règles du laboratoire

Il faut connaître les bases de CUCM, des téléphones IP, du protocole SIP, du RTP, des adresses IP, des VLAN voix et du routage IP.

Le cours ne suppose pas l'accès à un cluster CUCM réel. Les procédures peuvent être étudiées sur papier ou reproduites dans un environnement de formation autorisé. Les chemins de menus et certains noms de champs peuvent varier selon la version de CUCM, le type de périphérique, les fonctions activées et les droits de l'administrateur. Vérifie toujours la documentation correspondant à la version installée.

### Topologie d'étude

```text
                    Réseau opérateur / PSTN
                             |
                     Trunk SIP opérateur
                             |
                    +------------------+
                    | CUCM / cluster   |
                    | Atlas Services   |
                    +------------------+
                       /           \
                      /             \
             LAN siège             WAN privé
             Douala                    |
          10.10.10.0/24                |
          +----------------+      +----------------+
          | Téléphones IP  |      | Agence Yaoundé |
          | 1001, 1002     |      | 2001, 2002     |
          +----------------+      +----------------+
                                      10.20.20.0/24
                                      Routeur avec SRST
```

Exemple de conventions :

| Élément | Valeur de laboratoire |
|---|---|
| Siège, Douala | Site A |
| Agence, Yaoundé | Site B |
| Extensions du siège | 1XXX |
| Extensions de l'agence | 2XXX |
| Standard général | 1000 |
| Partition utilisateurs | `PT-INTERNAL` |
| Partition appels nationaux | `PT-LOCAL-NATIONAL` |
| Partition appels internationaux | `PT-INTERNATIONAL` |
| Partition services | `PT-SERVICES` |
| CSS employés | `CSS-EMPLOYEE` |
| CSS support | `CSS-SUPPORT` |
| CSS administrateurs | `CSS-ADMIN` |

Ces valeurs sont fictives et ne représentent aucune configuration réelle d'Atlas Services.

# Partie I — Concevoir le plan de numérotation

## 3. Partitions et Calling Search Spaces : appliquer les droits d'appel

Une partition regroupe logiquement des destinations du plan de routage CUCM : Directory Numbers (DN), route patterns, translation patterns, URI et autres objets pris en charge.

Un Calling Search Space (CSS) est une liste ordonnée de partitions qu'un appelant peut consulter pour trouver une destination. Le DN et le téléphone peuvent posséder chacun un CSS ; CUCM combine les CSS applicables selon la configuration du périphérique et du numéro appelé. Il faut donc vérifier les deux affectations lorsqu'un appel est autorisé ou bloqué de façon inattendue.

### 3.1 Principe d'accès

```text
Téléphone 1001
    |
    | CSS-EMPLOYEE
    v
Partitions accessibles :
  PT-INTERNAL
  PT-LOCAL-NATIONAL
  PT-SERVICES
    |
    +--> Appels internes : autorisés
    +--> Appels nationaux : autorisés
    +--> Services internes : autorisés
    +--> Appels internationaux : non accessibles
```

Si un route pattern international appartient uniquement à `PT-INTERNATIONAL` et que cette partition ne figure dans aucun CSS effectif du téléphone, l'appel ne doit pas pouvoir utiliser ce pattern. À l'inverse, ajouter une partition trop large à un CSS peut ouvrir des destinations non souhaitées.

### 3.2 Concevoir une matrice de droits avant de configurer

| Profil | Interne | National | International | Services sensibles |
|---|---:|---:|---:|---:|
| Employé | Oui | Oui | Non | Selon politique |
| Support | Oui | Oui | Selon autorisation | Oui |
| Direction | Oui | Oui | Oui | Oui |
| Téléphone de salle | Oui | Restreint | Non | Restreint |

La matrice doit être validée par le responsable de la téléphonie et le responsable de la sécurité. Un CSS n'est pas à lui seul une solution complète contre la fraude : il doit être associé à des restrictions opérateur, des profils de sécurité, une supervision des appels et des procédures de changement.

### 3.3 Bonnes pratiques

- Organiser les partitions selon les droits d'accès et la fonction des destinations, pas uniquement selon la localisation physique.
- Nommer clairement les objets, par exemple `PT-INTERNAL` ou `CSS-EMPLOYEE`.
- Éviter les CSS très génériques ou partagés sans justification.
- Documenter les CSS au niveau du téléphone, du DN, des trunks et des passerelles.
- Après chaque modification, tester un appel autorisé et un appel qui doit rester interdit.
- Vérifier les combinaisons de CSS effectives plutôt que de regarder seulement un champ isolé.

## 4. Route pattern, translation pattern et transformation pattern

Ces objets sont proches par leur nom, mais leur rôle est différent.

### 4.1 Route pattern

Le route pattern sélectionne un chemin de sortie ou bloque une plage de numéros. Il peut pointer vers une passerelle ou un trunk, mais une conception évolutive utilise généralement une route list et des route groups.

Exemple conceptuel :

```text
Route Pattern : 0.2XXXXXXX
Partition    : PT-LOCAL-NATIONAL
Route List   : RL-PSTN-LOCAL
Objectif     : router les appels nationaux vers le chemin téléphonique prévu
```

Le motif exact dépend du plan national et de la politique de numérotation. Ne copie pas cet exemple tel quel dans un système réel.

### 4.2 Translation pattern

Un translation pattern intercepte une chaîne de chiffres, réalise une transformation, puis relance la recherche d'une route selon le CSS associé au pattern. Il est souvent employé pour convertir un numéro composé dans une forme canonique ou pour adapter un préfixe.

Exemple de laboratoire : l'utilisateur compose `82001` pour joindre l'extension `2001`. Un translation pattern peut retirer le préfixe `8`, puis réévaluer le numéro `2001` à travers un CSS qui contient la partition interne.

```text
Numéro composé : 82001
        |
        v
Translation Pattern 8.XXXX
        |
        | suppression du premier chiffre (préfixe 8)
        v
Numéro traduit : 2001
        |
        v
Nouvelle recherche dans le CSS du translation pattern
        |
        v
DN 2001 dans PT-INTERNAL
```

Cette illustration décrit la logique, pas les valeurs exactes de tous les champs CUCM. Les options de suppression, de préfixe, de masque et le CSS doivent être vérifiés dans la configuration de la version utilisée.

### 4.3 Transformation pattern

Un transformation pattern modifie la présentation ou le format d'un numéro appelant ou appelé, par exemple pour adapter le format envoyé à un opérateur ou afficher un numéro public plutôt qu'une extension interne.

Il faut distinguer :

- **Called-party transformation** : adapte le numéro de destination.
- **Calling-party transformation** : adapte le numéro ou le nom présenté comme appelant.

Exemple : le poste interne `1001` peut présenter un numéro public professionnel lors d'un appel sortant, si la politique de l'entreprise et les règles de l'opérateur l'autorisent.

### 4.4 Comparaison

| Objet | Fonction principale | Résultat attendu |
|---|---|---|
| Route pattern | Choisir, bloquer ou acheminer l'appel | Un chemin de routage ou un rejet |
| Translation pattern | Traduire la chaîne puis refaire une recherche | Un numéro réévalué par le plan de routage |
| Transformation pattern | Adapter le format du numéro appelant ou appelé | Un numéro transformé au point prévu du routage |

Une erreur fréquente consiste à employer un translation pattern pour une simple présentation d'identité, ou à supposer qu'une transformation de numéro rend automatiquement une destination accessible. La transformation et les droits de routage sont deux sujets distincts.

## 5. Route groups, route lists et route patterns

La stratégie de routage sortant CUCM est généralement structurée en trois niveaux :

1. **Route pattern** : reconnaît la chaîne composée par l'utilisateur.
2. **Route list** : définit une liste ordonnée de chemins possibles.
3. **Route group** : regroupe les passerelles ou trunks utilisables selon une politique de sélection.

### 5.1 Exemple de routage avec secours

```text
L'utilisateur compose un numéro externe
                |
                v
        Route Pattern (RP)
                |
                v
        Route List (RL-PSTN)
                |
         +------+------+
         |             |
         v             v
    Route Group 1  Route Group 2
    Trunk opérateur Trunk de secours
         |             |
         v             v
     Fournisseur A  Fournisseur B
```

La présence de deux groupes n'assure pas automatiquement le basculement dans toutes les situations. Le comportement dépend de l'état des périphériques, des conditions d'échec, des timers, des réponses SIP, de la configuration et du type d'incident. Il faut tester le scénario de panne visé.

### 5.2 Plan de mise en œuvre

1. Inventorier les gateways et trunks réellement disponibles.
2. Définir les critères du chemin principal et du chemin de secours.
3. Créer les route groups et y placer les périphériques appropriés.
4. Créer la route list et ordonner les groupes.
5. Créer le route pattern et l'associer à la route list.
6. Affecter la partition adéquate au route pattern.
7. Inclure cette partition uniquement dans les CSS autorisés.
8. Tester appel normal, indisponibilité du chemin principal, restauration et interdiction d'appel.

Dans un environnement multi-sites, les Local Route Groups peuvent permettre de réutiliser des route patterns communs tout en choisissant la sortie locale en fonction du device pool et du site appelant. Cette approche doit être conçue et testée selon la topologie réelle.

## 6. Numérotation canonique et normalisation

Une stratégie de numérotation robuste sépare le format présenté par l'utilisateur du format interne de référence. Dans une entreprise multi-sites, une extension courte peut coexister avec un numéro canonique plus complet.

Exemple fictif :

| Élément | Numéro |
|---|---|
| Extension courte du siège | 1001 |
| Extension courte de l'agence | 2001 |
| Forme interne complète de l'agence | 8820001 |
| Numéro public de démonstration | +237 2XX XXX XXX |

Les numéros publics de cet exemple sont volontairement non complets et ne doivent pas être composés.

### 6.1 Principes de normalisation

- Établir un format de référence pour les numéros internes et publics.
- Savoir à quel point du parcours les préfixes sont ajoutés ou supprimés.
- Ne pas transformer deux fois un même numéro.
- Séparer l'identité interne de l'identité autorisée à être présentée au réseau public.
- Vérifier les appels internes, entrants, sortants, transférés et renvoyés.
- Documenter la chaîne de transformations de chaque classe d'appel.

### 6.2 Exemple de tableau de test

| Appel | Entrée | Résultat attendu |
|---|---|---|
| Interne siège | 1001 → 1002 | Sonnerie du 1002 |
| Inter-site | 1001 → 2001 | Sonnerie du 2001 via le routage interne prévu |
| Sortant autorisé | 1001 → numéro national de test | Appel sortant et CLI conforme à la politique |
| Sortant non autorisé | Employé → motif international | Refus prévu |
| Entrant public | Numéro DID → DN interne | Appel vers la destination publiée |
| Retour d'appel | Historique d'un appel entrant | Numéro rappelable et correctement normalisé |

# Partie II — Trunks SIP, interopérabilité et sécurité

## 7. Trunk SIP : paramètres à contrôler

Un trunk SIP relie CUCM à un système externe : opérateur SIP, passerelle, autre cluster, proxy ou plateforme de collaboration. Une configuration fonctionnelle nécessite plus qu'une adresse IP de destination.

Selon l'interconnexion, il faut examiner :

- destination ou adresses de destination ;
- port et transport de signalisation ;
- SIP Profile ;
- SIP Trunk Security Profile ;
- authentification, si elle est requise ;
- certificats et noms attendus en mode TLS ;
- règles de routage et formats des numéros ;
- codec et paramètres SDP ;
- DTMF ;
- early offer/delayed offer selon l'interopérabilité ;
- ressources médias nécessaires ;
- options SIP, timers, keepalives et supervision selon la solution interconnectée.

Les paramètres disponibles varient selon le type de trunk, la version de CUCM et les exigences du correspondant. Il faut éviter de modifier plusieurs options simultanément sans preuve dans les traces.

### 7.1 Signalisation et média sont deux chemins distincts

```text
                    SIGNALISATION SIP
          +-----------------------------------+
          |                                   |
      Téléphone A -------- CUCM -------- Trunk SIP
          |                                   |
          +-----------------------------------+

                       MÉDIA RTP/SRTP
          +-----------------------------------+
          |                                   |
      Téléphone A ===================== Téléphone B
                flux audio, selon la négociation
```

CUCM est généralement le contrôleur d'appel ; le média peut aller directement entre les terminaux ou passer par une ressource média selon la topologie et les paramètres négociés. Une session SIP qui réussit ne prouve donc pas que le chemin RTP fonctionne.

## 8. Sécuriser les trunks et les appels

### 8.1 Signalisation TLS

TLS peut protéger la signalisation SIP entre deux équipements qui le prennent en charge et dont les certificats et paramètres sont correctement configurés. Pour l'activer, il faut notamment vérifier le mode de sécurité, le transport entrant/sortant, le port, la chaîne de confiance, les noms des certificats et les exigences du correspondant.

Le port 5061 est couramment utilisé pour SIP sur TLS, mais le port réel dépend de la configuration. Ne présume jamais que changer le port rend le trunk sécurisé.

### 8.2 Chiffrement du média

SRTP protège le flux média selon le mécanisme de clés et les algorithmes négociés. La prise en charge du SRTP doit être cohérente de bout en bout ou à travers les ressources média compatibles. Un trunk dont la signalisation est chiffrée ne garantit pas, à lui seul, que le média est chiffré.

### 8.3 Contrôles de sécurité recommandés

- Autoriser uniquement les adresses, ports et transports nécessaires au niveau réseau.
- Ne pas exposer l'interface d'administration CUCM directement à Internet.
- Employer TLS/SRTP lorsque la solution, les terminaux et le correspondant les prennent en charge et qu'ils sont correctement configurés.
- Protéger les comptes d'administration et les accès aux interfaces de gestion.
- Limiter les appels internationaux, surtaxés et autres destinations sensibles selon la politique de l'entreprise.
- Contrôler les numéros présentés au réseau public et les règles de transfert d'appel.
- Surveiller les volumes d'appels anormaux, les échecs répétés et les changements de configuration.
- Vérifier la validité des certificats, leur expiration et la synchronisation horaire.
- Réaliser des sauvegardes et tester la restauration dans un environnement maîtrisé.

## 9. SIP interopérable : SDP, codecs, DTMF et MTP

Le protocole SDP décrit notamment les capacités média, les codecs, les adresses, les ports et les modes de transport proposés ou acceptés. Une incompatibilité SDP peut empêcher l'établissement média même quand la signalisation progresse.

### 9.1 Codecs

Un codec transforme la voix en données numériques et influe sur la bande passante, la charge de traitement et parfois la qualité perçue.

| Codec | Caractéristique générale | Point d'attention |
|---|---|---|
| G.711 | Débit audio nominal de 64 kbit/s par direction, hors surcharge IP | Consomme davantage de bande passante réseau que les codecs compressés |
| G.729 | Codec historique à faible débit nominal, lorsqu'il est pris en charge et licencié selon la plate-forme | Peut imposer des contraintes de licences, de compatibilité et de qualité |
| Opus | Codec adaptatif courant dans plusieurs systèmes de communication modernes | Ne pas supposer que tous les trunks ou terminaux CUCM le prennent en charge |

Le débit réel sur le réseau comprend RTP, UDP, IP, les en-têtes de couche 2 et parfois des tunnels. Un appel G.711 n'utilise donc pas seulement 64 kbit/s sur le lien IP.

### 9.2 DTMF

Les chiffres d'un clavier téléphonique peuvent être transportés par différents mécanismes, selon les équipements : événements RTP de type telephone-event, signalisation SIP ou transmission audio dans la bande. Si l'utilisateur entend correctement la voix mais que le serveur vocal interactif ne reconnaît pas les chiffres, il faut vérifier le mode DTMF négocié et la compatibilité de bout en bout.

### 9.3 Quand un MTP est-il pertinent ?

Un Media Termination Point peut être requis dans certains scénarios d'interopérabilité ou de traitement média. Il ne faut pas l'activer systématiquement pour tous les appels : une ressource ajoutée inutilement consomme de la capacité et peut modifier le chemin média.

Avant d'imposer un MTP, déterminer précisément le problème : négociation SDP, mode d'offre, DTMF, protocole, besoin de relais ou contrainte d'un système tiers. Puis tester l'appel avec et sans la ressource, selon une procédure de changement approuvée.

# Partie III — Architecture et qualité de service

## 10. Device pools, régions et locations

Ces objets remplissent des fonctions différentes et sont souvent confondus.

### 10.1 Device pool

Le device pool applique un ensemble de paramètres communs aux périphériques d'un site ou d'un groupe logique, par exemple une région, une location, un groupe de ressources médias et d'autres réglages selon le déploiement.

### 10.2 Region

Les régions servent notamment à définir des paramètres de codec et de débit média entre les groupes concernés. Une relation de région peut ainsi limiter les codecs ou le débit maximal utilisé pour un type de session.

### 10.3 Location et contrôle d'admission d'appels

Les locations modélisent la capacité disponible entre sites ou sur des liaisons WAN. Le Call Admission Control (CAC) peut empêcher l'établissement d'appels supplémentaires lorsque le budget de bande passante déclaré est épuisé.

```text
Douala (Location A) ===== WAN 2 Mbit/s ===== Yaoundé (Location B)
        |                                         |
    Téléphones                                Téléphones
        |                                         |
        +---- appels inter-sites contrôlés -------+
```

L'exemple illustre le principe ; les valeurs sont fictives. Le CAC ne remplace pas la QoS des routeurs. Il faut que la bande passante configurée dans CUCM reflète correctement les ressources réelles et la politique d'allocation, sans quoi les appels peuvent être autorisés à tort ou refusés inutilement.

### 10.4 Méthode de dimensionnement de départ

1. Mesurer la bande passante réellement disponible pour la voix sur le WAN.
2. Choisir les codecs et la taille des paquets selon la politique d'entreprise.
3. Calculer le débit approximatif d'un appel, avec les surcharges IP et de couche 2.
4. Définir la part de capacité réservée à la voix et une marge opérationnelle.
5. Définir le nombre maximal d'appels simultanés dans chaque sens et sur les chemins concernés.
6. Configurer les régions et les locations en cohérence avec ce modèle.
7. Vérifier le comportement à la limite : admission, refus ou chemin alternatif prévu.
8. Comparer les données CUCM à la supervision réseau réelle.

Pour un dimensionnement de production, ne déduis pas un nombre d'appels à partir du seul débit nominal du codec. Prends en compte la taille de paquet, les en-têtes, les tunnels, la signalisation, les flux vidéo, le trafic concurrent et les mécanismes de redondance.

## 11. QoS de bout en bout

La qualité audio dépend de l'ensemble du chemin : téléphone, commutateur d'accès, agrégation, WAN, routeur de site distant et chemin vers le correspondant. Un marquage DSCP ne garantit rien si un équipement l'efface ou si la file prioritaire est mal dimensionnée.

Les phénomènes importants sont :

- **Latence** : délai de bout en bout ; trop élevée, elle rend la conversation difficile.
- **Gigue** : variation du délai d'arrivée des paquets ; elle met à l'épreuve le tampon de gigue du terminal.
- **Perte de paquets** : paquets audio perdus, pouvant causer coupures ou dégradation.
- **Congestion** : surcharge d'un lien ou d'une file qui augmente les retards et les pertes.

Dans de nombreux designs d'entreprise, le média RTP vocal est marqué DSCP EF (valeur décimale 46), alors que la signalisation peut être marquée différemment selon le modèle QoS de l'organisation. Ce ne sont pas des règles universelles : respecter la politique validée, le guide de conception du réseau et les pratiques de l'opérateur WAN.

### 11.1 Vérifications QoS

- Le port d'accès du téléphone applique la politique attendue au VLAN voix.
- Le téléphone marque le trafic comme prévu et le réseau fait confiance à cette marque uniquement sur les ports autorisés.
- Les commutateurs et routeurs conservent ou réécrivent le DSCP conformément à la politique.
- Les files de sortie donnent la priorité au trafic voix sans permettre à une classe prioritaire de monopoliser le lien.
- Le WAN possède un traitement cohérent dans les deux sens.
- Les compteurs de pertes, de drops et d'utilisation des files sont collectés pendant un appel de test.

# Partie IV — Ressources média et continuité de service

## 12. Ressources média CUCM

Les ressources média sont des composants qui fournissent des fonctions que les terminaux ne peuvent pas toujours accomplir seuls.

| Ressource | Fonction | Point de vigilance |
|---|---|---|
| MTP | Terminaison/relais média pour certains scénarios | Peut consommer des ressources et modifier le chemin média |
| Transcoder | Convertit entre codecs compatibles lorsque nécessaire | Vérifier la capacité et la compatibilité des codecs |
| Conference Bridge | Mélange ou gère les médias d'une conférence | Vérifier le type de ressource, la capacité et l'affectation |
| Music on Hold (MoH) | Fournit de la musique lorsqu'un appel est mis en attente | Vérifier le flux média et la portée réseau |
| Annunciator | Fournit certaines annonces audio | Vérifier son accessibilité et son association aux groupes de ressources |

La disponibilité d'une ressource dépend de la configuration, du type de ressource et du chemin de sélection. La bonne pratique est de diagnostiquer un besoin réel avant de changer son affectation.

## 13. SRST : maintenir un service local en cas de perte WAN

Sur un site distant dépendant de CUCM centralisé, Survivable Remote Site Telephony (SRST) permet au routeur/gateway local de fournir un service téléphonique limité lorsque les téléphones perdent leur connectivité avec les serveurs CUCM associés.

```text
Fonctionnement normal :
Téléphone distant ---> WAN ---> CUCM central
        |                         |
        +-------------------------+

Perte de WAN :
Téléphone distant ---> Routeur local en mode SRST
                              |
                              +--> appels locaux et fonctions prises en charge
```

Le périmètre exact dépend du routeur, de la version logicielle, du type d'enregistrement et des fonctionnalités configurées. SRST ne reproduit pas toutes les fonctions du cluster central : les services de collaboration avancés, certains transferts, les répertoires et les fonctions dépendantes de CUCM peuvent être limités.

### 13.1 Points de configuration et de validation

- Créer ou sélectionner la SRST Reference adaptée au site.
- Associer cette référence au device pool pertinent.
- Vérifier la configuration du routeur de branche et sa capacité à gérer les téléphones.
- Valider l'accessibilité IP et les paramètres de secours des téléphones.
- Tester la perte de liaison vers CUCM selon un plan approuvé.
- Vérifier l'indicateur de mode dégradé sur les téléphones.
- Tester les appels locaux et les appels externes via les ressources disponibles.
- Restaurer le WAN, observer le retour à CUCM puis confirmer les services normaux.

Ne jamais simuler une panne sur un site de production sans autorisation, plan de retour arrière et validation des conséquences sur les appels en cours.

# Partie V — Dépannage structuré

## 14. Une méthode commune pour tout incident d'appel

Le dépannage doit partir du symptôme et suivre le parcours d'un appel. Éviter de modifier plusieurs réglages à la fois.

### Étape 1 : cadrer l'incident

Noter : heure et fuseau, appelant, appelé, site, téléphone, direction de l'appel, fréquence, message affiché, état du trunk, type de média et périmètre des utilisateurs touchés. Utiliser des données de test autorisées et protéger les numéros personnels présents dans les traces.

### Étape 2 : déterminer la catégorie

- **Échec de composition** : le numéro n'est pas reconnu ou le pattern est inaccessible.
- **Échec d'établissement** : problème de routage, de trunk, de passerelle, de réponse SIP ou de ressources.
- **Appel établi sans audio** : chemin RTP, SDP, ACL, NAT, firewall, ressource média ou mauvais adressage média.
- **Audio unidirectionnel** : vérifier séparément le flux dans chaque direction.
- **Mauvaise qualité** : mesurer latence, gigue, pertes, congestion et compteurs de QoS.
- **DTMF défaillant** : contrôler le mode négocié et le chemin média.
- **Incident limité à un site** : vérifier WAN, CAC, device pool, région/location et routeur local.

### Étape 3 : remonter la chaîne de signalisation

```text
Poste appelant
   |
   v
DN / CSS / Partition
   |
   v
Translation éventuelle
   |
   v
Route Pattern
   |
   v
Route List / Route Group
   |
   v
Trunk SIP ou Gateway
   |
   v
Réseau distant / opérateur
```

Selon le sens de l'appel, l'ordre réel de parcours diffère. Pour un appel entrant, commencer par la signalisation reçue, les transformations du numéro appelé, les routes entrantes configurées et le DN de destination.

### Étape 4 : utiliser les traces correctement

Dans Cisco Unified Serviceability, les traces peuvent être configurées pour les services concernés. Les traces SDI et SDL servent au diagnostic des services CUCM ; RTMT fournit des fonctions de collecte, de recherche et de consultation de données et de traces.

Les procédures et menus exacts dépendent de la version. Les traces peuvent contenir des informations sensibles sur les communications et les numéros : limiter l'accès, la durée de conservation et le partage.

Bonnes pratiques :

1. Synchroniser les horloges de CUCM, passerelles et équipements réseau.
2. Reproduire un seul cas de test avec heure précise et numéros connus.
3. Activer temporairement le niveau de trace utile, dans une fenêtre approuvée.
4. Capturer les journaux et, si nécessaire, les paquets au point approprié.
5. Corréler les messages SIP avec l'identifiant d'appel et les données de chaque équipement.
6. Relier la signalisation au SDP et au chemin média.
7. Restaurer le niveau de trace normal après investigation.
8. Documenter la preuve, la cause racine, le changement et le test de non-régression.

Un niveau de trace détaillé peut impacter les performances et produire beaucoup de données. Ne le laisse pas activé sans nécessité.

## 15. Tableau de dépannage rapide

| Symptôme | Première zone à vérifier | Indices complémentaires |
|---|---|---|
| L'appel interne échoue | DN, partition, CSS effectif | Contrôler les CSS du périphérique et du DN |
| Le numéro externe est rejeté immédiatement | Route pattern et CSS | Vérifier le motif composé et les transformations |
| Seuls les appels internationaux échouent | Partition internationale et restrictions | Confirmer la politique d'autorisation et les motifs |
| Le trunk apparaît indisponible | Connectivité, port, transport et paramètres trunk | Vérifier les réponses SIP, les options et les journaux du correspondant |
| Appel établi sans audio | SDP et chemin RTP | Vérifier adresses/ports annoncés, ACL et routage des deux sens |
| Audio dans un seul sens | Retour média | Tester chaque sens et observer les compteurs firewall/NAT |
| Mauvais numéro affiché à l'extérieur | Calling Party Transformation | Comparer DN interne, numéro canonique et CLI envoyé |
| DTMF non reconnu | Négociation DTMF | Comparer le mode attendu côté CUCM, passerelle et IVR |
| Voix coupée aux heures chargées | QoS et congestion WAN | Mesurer drops, gigue, pertes et utilisation des files |
| Le site distant perd les fonctions lors d'une coupure | SRST Reference et routeur local | Vérifier la capacité et les fonctions disponibles en secours |

# Partie VI — Travaux pratiques corrigés

Tous les TP sont conçus comme des exercices de conception ou d'administration sur un système de test. Ils ne demandent pas de modifier une plateforme de production sans autorisation.

## TP 1 — Construire une matrice CSS/Partition

### Objectif
Autoriser les appels internes à tous, les appels nationaux aux employés et les appels internationaux uniquement à la direction.

### Situation
Partitions disponibles : `PT-INTERNAL`, `PT-NATIONAL`, `PT-INTERNATIONAL`, `PT-SERVICES`.

### Travail demandé
1. Définir les CSS des employés et de la direction.
2. Définir les partitions où placer les motifs de routage.
3. Expliquer comment vérifier qu'un employé ne peut pas joindre un motif international.
4. Proposer un test négatif et un test positif.

### Correction
Une conception de départ possible est :

```text
CSS-EMPLOYEE:
  PT-INTERNAL
  PT-NATIONAL
  PT-SERVICES

CSS-MANAGEMENT:
  PT-INTERNAL
  PT-NATIONAL
  PT-INTERNATIONAL
  PT-SERVICES
```

Les route patterns nationaux et internationaux sont placés dans les partitions correspondantes. Les profils effectifs des téléphones et des DN sont examinés pour éviter qu'un autre CSS ne donne accidentellement accès à la partition internationale.

Test positif : un employé appelle une extension interne et un numéro national de test autorisé. Test négatif : le même téléphone tente un numéro correspondant au motif international et l'appel est refusé. Réaliser ensuite les tests en tant que direction et vérifier que l'appel international est autorisé uniquement si les autres conditions de routage sont satisfaites.

Ce schéma est une proposition logique : les règles réelles doivent aussi prendre en compte les numéros d'urgence, les services locaux, les règles opérateur et les obligations applicables.

## TP 2 — Concevoir une route list avec secours

### Objectif
Préparer une route sortante utilisant un opérateur principal et un second chemin.

### Travail demandé
1. Inventorier deux trunks de laboratoire.
2. Créer `RG-PSTN-PRIMARY` et `RG-PSTN-BACKUP`.
3. Créer `RL-PSTN-OUT` avec le groupe principal en priorité.
4. Associer le route pattern de test à cette route list.
5. Définir les cas de validation.

### Correction
```text
Route Pattern de test
        |
        v
RL-PSTN-OUT
   1. RG-PSTN-PRIMARY
   2. RG-PSTN-BACKUP
```

Configurer les trunks et profils en fonction du laboratoire, puis valider un appel normal. Simuler ensuite, avec autorisation, l'indisponibilité du chemin principal et observer le comportement. Le fait qu'un chemin de secours figure en second ne suffit pas à prouver le basculement : vérifier que CUCM considère bien le premier chemin indisponible dans le scénario testé et que le deuxième est correctement configuré.

Cas de test à inclure : appel normal, perte de la connectivité principale, réponse d'erreur du fournisseur, restauration, appel non autorisé, et vérification du numéro appelant présenté.

## TP 3 — Diagnostiquer un trunk SIP

### Symptôme
Les postes peuvent appeler en interne, mais les appels sortants par le trunk échouent.

### Démarche
1. Reproduire l'échec une fois et relever l'heure exacte.
2. Vérifier si le motif externe correspond au plan de numérotation.
3. Vérifier la partition et le CSS effectif.
4. Vérifier la route list, le route group et le statut du trunk.
5. Contrôler adresse de destination, port, transport et SIP Security Profile.
6. Lire les traces CUCM et la réponse SIP correspondante.
7. Comparer l'appelant et l'appelé effectivement envoyés au correspondant.

### Correction attendue
Ne pas conclure immédiatement à une panne du fournisseur. Un rejet peut provenir d'un motif inaccessible, d'une transformation incorrecte, d'un trunk désactivé, d'une erreur de transport, d'une politique d'authentification ou d'une réponse du correspondant. La cause doit être prouvée par le point de rupture observé.

Exemple d'interprétation générale :

- Une requête SIP n'est jamais émise par CUCM : rechercher le plan de numérotation, le CSS et la sélection du chemin.
- Une requête est envoyée mais aucune réponse ne revient : examiner connectivité, firewall, chemin de retour et disponibilité du correspondant.
- Une réponse SIP d'erreur est reçue : en interpréter le code et le contexte avant de changer la configuration.
- L'appel est établi mais n'a pas d'audio : quitter le diagnostic purement signalisation et examiner le SDP et RTP/SRTP.

## TP 4 — Appel sans audio ou audio unidirectionnel

### Objectif
Séparer la signalisation de la connectivité média.

### Démarche
1. Confirmer que l'appel atteint l'état établi.
2. Collecter les adresses et ports annoncés dans les SDP pertinents.
3. Identifier les adresses réelles des deux terminaux et les éventuelles ressources médias.
4. Vérifier les règles ACL/firewall et les routes retour dans chaque sens.
5. Observer les flux RTP/SRTP au point de capture autorisé.
6. Examiner les compteurs d'interface et les règles QoS.

### Correction
Si SIP s'établit mais qu'aucun flux média n'arrive, vérifier le chemin média indépendamment du chemin de signalisation. Un flux qui sort d'un côté mais ne revient pas oriente l'enquête vers le routage retour, un filtrage, un problème NAT ou une adresse/port annoncés incorrects. Ne désactive pas globalement le firewall pour tester : crée une observation ou une règle de test limitée et autorisée, puis retire-la après validation.

## TP 5 — Préparer la continuité SRST d'une agence

### Objectif
Rédiger un plan de test de survivabilité sans interrompre un site réel.

### Travail demandé
- Identifier les téléphones et les fonctions indispensables.
- Associer une SRST Reference au site et au device pool, selon la conception.
- Vérifier le rôle du routeur local, ses interfaces et ses ressources.
- Définir les appels qui doivent rester possibles pendant une coupure WAN.
- Définir la procédure de retour au fonctionnement normal.

### Correction
Le plan de test doit préciser les préconditions, l'autorisation de coupure, le début et la durée de la fenêtre, la méthode de simulation, les tests d'appels locaux et externes, les fonctions explicitement limitées, les critères de retour arrière et la validation du réenregistrement CUCM après restauration. SRST fournit un service de secours limité, pas une copie intégrale de CUCM.

# Partie VII — Exercices corrigés

## Exercice 1 — CSS et accès

Un employé peut appeler le national, mais il peut également joindre un motif international que la politique devrait lui interdire. Donne trois hypothèses de vérification.

**Correction :**
1. La partition internationale figure dans le CSS effectif du téléphone ou du DN.
2. Un autre CSS appliqué au périphérique ou au DN ajoute l'accès à cette partition.
3. Un motif plus large ou une autre route accessible permet d'atteindre la même destination. Il faut examiner le plan de numérotation complet et tester le chemin réellement sélectionné.

## Exercice 2 — Route pattern ou translation pattern ?

Un préfixe de sortie doit être retiré avant de rechercher une extension interne. Quel objet correspond le mieux à cette logique ?

**Correction :** Un translation pattern peut correspondre, car CUCM traduit les chiffres puis relance la recherche de route selon le CSS configuré sur cet objet. Un route pattern, en revanche, sélectionne un chemin de sortie ou une action de routage.

## Exercice 3 — Route list

Pourquoi choisir une route list et des route groups plutôt que de lier chaque route pattern directement à un trunk ?

**Correction :** Cette architecture sépare la logique de numérotation de la sélection des chemins, facilite la priorisation des trunks, le secours et la réutilisation de la configuration. Le comportement de basculement doit cependant être vérifié selon les conditions d'échec réelles.

## Exercice 4 — TLS et SRTP

Un administrateur affirme qu'un trunk SIP configuré avec TLS chiffre forcément la voix. Est-ce exact ?

**Correction :** Non. TLS protège la signalisation sur le lien concerné. Le média nécessite une protection adaptée, par exemple SRTP, négociée et prise en charge de bout en bout ou par les équipements intermédiaires prévus.

## Exercice 5 — Qualité vocale

La qualité se dégrade pendant les heures de pointe, mais le nombre d'échecs d'établissement reste faible. Quelles mesures faut-il relever ?

**Correction :** Latence, gigue, perte de paquets, utilisation des liens, drops et compteurs de files QoS, ainsi que le DSCP observé à différents points du chemin. Vérifier aussi si la congestion se situe dans le LAN, le WAN ou le réseau de l'opérateur.

## Exercice 6 — Regions et Locations

Quel est le rôle distinct des régions et des locations ?

**Correction :** Les régions servent notamment à définir des contraintes de codec et de débit média entre groupes. Les locations modélisent des capacités réseau et servent au contrôle d'admission d'appels sur les liaisons déclarées. Elles ne remplacent pas le traitement QoS du réseau IP.

## Exercice 7 — Pas d'audio

L'appel SIP s'établit, mais les interlocuteurs ne s'entendent pas. Quelle est la prochaine étape logique ?

**Correction :** Examiner le SDP et vérifier le chemin RTP/SRTP dans les deux sens : adresses, ports, routage, ACL/firewall, NAT éventuel, ressources média et compteurs réseau. Il serait prématuré de modifier les partitions ou le CSS sans indice reliant le problème au routage de l'appel.

## Exercice 8 — SRST

Lorsqu'un site perd son accès au cluster central, SRST maintient-il toutes les fonctions de collaboration ?

**Correction :** Non. SRST peut fournir des fonctions téléphoniques locales limitées, selon le routeur et la configuration. Les services qui dépendent du cluster ou de systèmes externes peuvent être indisponibles ou limités pendant la panne.

## Exercice 9 — Traces

Pourquoi faut-il limiter le niveau de trace détaillé dans le temps ?

**Correction :** Les traces détaillées peuvent augmenter la charge, consommer de l'espace et collecter des données sensibles. Elles doivent être activées pour une investigation ciblée, puis ramenées à leur niveau normal après collecte.

## Exercice 10 — Numéro appelant incorrect

Un appel sortant aboutit, mais le destinataire voit l'extension interne au lieu du numéro public attendu. Que vérifier ?

**Correction :** Vérifier la forme du numéro dans CUCM, les calling-party transformations appliquées, les paramètres du trunk ou de la route list et les exigences de présentation de l'opérateur. Confirmer quel numéro est effectivement émis dans la signalisation plutôt que de supposer que le DN interne doit toujours être affiché.

# Partie VIII — Défi final corrigé

## 16. Scénario : concevoir la téléphonie multi-sites d'Atlas Services

Atlas Services possède un siège à Douala et une agence à Yaoundé. Tous les employés peuvent appeler les extensions internes. Les employés peuvent faire des appels nationaux. Seule la direction peut effectuer des appels internationaux. Les appels sortants doivent utiliser un chemin principal et un chemin de secours. L'agence doit conserver une capacité téléphonique locale limitée lorsque le WAN vers CUCM est indisponible. Les appels inter-sites doivent respecter la capacité de bande passante WAN.

### Travail demandé

1. Proposer les partitions et CSS.
2. Décrire la chaîne de routage sortant.
3. Proposer une stratégie de numérotation inter-sites.
4. Identifier les paramètres CUCM utiles pour le contrôle de la bande passante.
5. Décrire la stratégie de sécurité du trunk.
6. Définir le plan de test SRST.
7. Définir les contrôles de qualité vocale et les éléments à collecter lors d'un incident.

### Correction détaillée

#### 16.1 Modèle de partitions et de CSS

```text
Partitions :
  PT-INTERNAL
  PT-NATIONAL
  PT-INTERNATIONAL
  PT-SERVICES

CSS-EMPLOYEE :
  PT-INTERNAL
  PT-NATIONAL
  PT-SERVICES

CSS-MANAGEMENT :
  PT-INTERNAL
  PT-NATIONAL
  PT-INTERNATIONAL
  PT-SERVICES
```

Le plan réel doit prévoir les numéros d'urgence et les exigences locales. Les CSS effectifs du téléphone et du DN doivent être vérifiés ensemble. Une revue périodique du plan de numérotation permet de rechercher les chemins alternatifs qui contourneraient les restrictions voulues.

#### 16.2 Routage sortant

```text
RP-NATIONAL / RP-INTERNATIONAL
                 |
                 v
             RL-PSTN-OUT
                 |
        +--------+---------+
        |                  |
        v                  v
 RG-PSTN-PRIMARY     RG-PSTN-BACKUP
        |                  |
     Trunk A             Trunk B
```

Les partitions et CSS déterminent quels profils ont accès à chaque motif. Les route patterns sont associés à la route list appropriée. Les tests doivent couvrir le fonctionnement normal, l'indisponibilité du premier chemin, le retour du service, les numéros non autorisés et la présentation du numéro appelant. Un échec spécifique à un opérateur doit être corrélé avec les réponses SIP et la configuration du trunk.

#### 16.3 Stratégie de numérotation

Conserver une forme canonique documentée pour les destinations internes et les numéros publics. Définir les règles qui traduisent l'extension courte vers la forme inter-sites ou qui normalisent les appels entrants. Utiliser des transformations distinctes lorsque l'objectif est d'adapter le numéro présenté ou celui envoyé au trunk.

Chaque règle doit être accompagnée d'exemples d'entrée/sortie. Tester les appels entrants, sortants, transférés, renvoyés et les rappels depuis l'historique.

#### 16.4 Bande passante et qualité

Affecter les device pools selon les sites, définir les relations de régions nécessaires aux codecs et débits, puis configurer les locations/CAC en cohérence avec les budgets WAN disponibles. Mettre en œuvre la QoS sur tous les équipements du chemin, avec le marquage et les files définis par la politique réseau. Vérifier les pertes, la gigue et la latence lors de tests en charge représentatifs.

#### 16.5 Sécurité du trunk

Utiliser le SIP Trunk Security Profile approprié au service. Lorsque le trunk et le fournisseur le permettent, mettre en œuvre TLS et vérifier les certificats ; utiliser SRTP lorsque le média chiffré est pris en charge et exigé. Limiter les flux réseau aux adresses et ports requis, contrôler les numéros autorisés et surveiller les anomalies. Le plan de sécurité doit préciser le renouvellement des certificats et la réponse à un incident.

#### 16.6 Continuité avec SRST

Associer une SRST Reference au device pool de Yaoundé et vérifier la configuration du routeur de branche. Tester les scénarios de perte et de restauration WAN pendant une fenêtre de maintenance autorisée. Pendant le mode dégradé, valider les appels locaux et les fonctions prévues par la conception ; documenter les services indisponibles. Après restauration, vérifier le retour à CUCM, la signalisation, les appels entrants/sortants et les fonctions normales.

#### 16.7 Plan de diagnostic

En cas d'échec, enregistrer l'heure, les numéros de test, le site et le résultat observé. Vérifier d'abord la portée de l'incident, puis le plan de numérotation, la route list, le trunk et les réponses SIP. Si l'appel est établi, inspecter le SDP et le média. Pour les problèmes de qualité, collecter les statistiques WAN/QoS et comparer les deux sens. Utiliser RTMT et les traces CUCM avec un niveau temporaire et ciblé, puis restaurer les paramètres de trace.

### Critères de réussite

- Les employés appellent les extensions et les numéros nationaux autorisés.
- Les appels internationaux des employés sont refusés, tandis que ceux de la direction sont autorisés selon la politique.
- Les appels externes empruntent le chemin prévu et la panne du chemin principal donne le comportement attendu.
- Les numéros présentés et les numéros appelés sont conformes aux règles établies.
- Les appels inter-sites respectent les contraintes de bande passante déclarées.
- Le scénario SRST est testé et ses limites sont documentées.
- Chaque incident peut être relié à une preuve technique et à une procédure de correction.

# 17. Glossaire

- **CAC — Call Admission Control :** mécanisme qui contrôle l'admission d'appels selon la capacité réseau déclarée.
- **CSS — Calling Search Space :** liste ordonnée de partitions accessibles pour la recherche de destinations.
- **CUCM :** plateforme Cisco de contrôle des appels et de gestion de la téléphonie collaborative.
- **DN — Directory Number :** numéro ou extension affecté à une destination téléphonique.
- **DTMF :** tonalités correspondant aux chiffres et touches d'un clavier téléphonique.
- **MTP — Media Termination Point :** ressource média utilisée dans certains scénarios de terminaison ou de relais.
- **MoH — Music on Hold :** musique diffusée pendant la mise en attente.
- **Partition :** groupe logique de destinations du plan de routage.
- **RTP :** protocole couramment utilisé pour transporter les médias temps réel.
- **RTMT :** outil Cisco de supervision, collecte et diagnostic en temps réel.
- **Route group :** groupe de gateways ou trunks utilisés comme chemins de sortie.
- **Route list :** liste ordonnée de route groups et/ou de local route groups.
- **Route pattern :** motif de numérotation qui sélectionne un chemin ou une action de routage.
- **SDI / SDL :** types de traces CUCM utilisés pour le diagnostic des services.
- **SDP :** description des capacités et paramètres média d'une session.
- **SRST :** fonction de survivabilité téléphonique locale lors de la perte de connectivité au système central.
- **SRTP :** protection du flux RTP par des mécanismes de sécurité adaptés.
- **TLS :** protocole de protection de la connexion de signalisation, lorsqu'il est pris en charge et correctement configuré.
- **Translation pattern :** motif qui transforme les chiffres et relance la recherche de routage.
- **Transformation pattern :** règle qui adapte le format du numéro appelant ou appelé à une étape donnée.

# 18. Références techniques

Les pages officielles ci-dessous servent à vérifier les menus, les champs et les procédures correspondant à la version de CUCM utilisée. La disponibilité exacte des fonctionnalités dépend de la version, des licences, des périphériques et de l'architecture déployée.

- [Cisco Unified Communications Manager — System Configuration Guide, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html) — partitions, CSS, routage, trunks, régions, locations et SRST.
- [Cisco Unified Communications Manager — Configure Partitions](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_010000.html) — modèle d'accès et CSS.
- [Cisco Unified Communications Manager — Configure Call Routing](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_010010.html) — route patterns, route lists, route groups et transformations.
- [Cisco Unified Communications Manager — Configure Trunks](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_01000.html) — profils SIP et trunks.
- [Cisco Unified Communications Manager — Security Guide, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/security/15_0/cucm_b_security-guide-release-15.html) — sécurité des trunks, profils et TLS.
- [Cisco Unified Communications Manager — Trace and Troubleshooting](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/adminGd/cucm_b_administration-guide-15/cucm_b_test-adminguide_chapter_011000.html) — configuration et collecte des traces.
- [Cisco Unified Real-Time Monitoring Tool — Administration Guide, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/service/15/rtmt/cucm_b_cisco-unified-rtmt-administration-15.html) — supervision et collecte.
- [Cisco Unified Communications Manager — Configure Enhanced Locations Call Admission Control](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_01101.html) — contrôle d'admission et topologie réseau.
- [Cisco Unified SRST Administration Guide](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cusrst/admin/sccp_sip_srst/configuration/guide/SCCP_and_SIP_SRST_Admin_Guide/srst_setting_up_the_network.html) — fonctionnement du secours téléphonique local.

## Conclusion

Le niveau intermédiaire consiste à raisonner au-delà du simple enregistrement d'un téléphone : droits de routage, transformations, chemins de secours, interopérabilité SIP, qualité vocale, ressources média et résilience locale doivent former un ensemble cohérent.

La méthode à retenir est simple : **définir la politique, cartographier le parcours de l'appel, modifier un élément à la fois, tester les scénarios nominaux et dégradés, puis documenter les preuves et le retour arrière.**
