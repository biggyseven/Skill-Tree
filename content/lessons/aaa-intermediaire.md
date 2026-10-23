---
node_id: aaa-intermediaire
title: Authentification réseau (AAA) - Intermédiaire
---

# Authentification réseau (AAA) - Intermédiaire

**Niveau :** INTERMÉDIAIRE

À mesure qu’un réseau grandit, le contrôle des accès ne peut plus reposer sur des comptes locaux copiés à la main sur chaque routeur, commutateur, pare-feu et passerelle VPN. L’équipe doit être capable de retirer rapidement les droits d’un collaborateur, de limiter les actions des techniciens, de vérifier qui a effectué un changement et de maintenir un accès d’urgence lorsque le serveur central est indisponible. Le modèle AAA fournit une architecture pour organiser ces besoins, mais sa qualité dépend de la conception des politiques, du transport, de la disponibilité et des procédures d’exploitation.

Ce cours intermédiaire traite AAA comme un service de production. Il approfondit les listes de méthodes Cisco IOS/IOS XE, les différences opérationnelles entre RADIUS et TACACS+, l’autorisation EXEC et des commandes, l’accounting, les mécanismes de secours, l’intégration à un annuaire, 802.1X, les attributs d’autorisation, la haute disponibilité et le dépannage fondé sur les preuves. Les exemples restent des modèles de laboratoire : la prise en charge exacte des commandes varie selon le matériel, la version logicielle, le type de serveur et la fonctionnalité AAA concernée.

Une architecture AAA doit être évaluée sur trois plans. Le plan **identité** répond à la question « qui ou quel appareil se connecte ? ». Le plan **politique** décide quels services, commandes, VLAN ou profils sont autorisés. Le plan **preuve et exploitation** garde des traces fiables et permet de maintenir le service en cas de panne. Une authentification correcte ne suffit pas si tous les comptes obtiennent le même privilège, et un journal très détaillé n’est pas utile s’il n’est pas horodaté, protégé ou corrélé à une identité unique.

> **Analogie** : AAA ressemble à un système de contrôle d’accès dans un centre de données. Le badge vérifie l’identité, le profil du badge détermine les salles et les équipements accessibles, et le registre conserve les passages. Une panne du service central ne doit pas obliger à laisser toutes les portes ouvertes : il faut une procédure d’urgence limitée, prévue et auditée, ainsi qu’une manière sûre de revenir au contrôle normal.

---

## 1. La théorie et les algorithmes

### 1.1. Passer du modèle AAA à une politique exploitable

AAA est la combinaison de trois fonctions : **Authentication** (authentification), **Authorization** (autorisation) et **Accounting** (traçabilité ou comptabilisation). En exploitation, il faut les configurer et les tester séparément. Une demande réussie dans une fonction n’implique pas automatiquement le succès des deux autres.

| Fonction | Question opérationnelle | Exemple | Preuve attendue |
|---|---|---|---|
| Authentication | Quelle identité présente une preuve valide ? | Un administrateur se connecte en SSH. | Succès ou rejet avec méthode utilisée. |
| Authorization | Quelles opérations cette identité peut-elle réaliser ? | Un opérateur peut afficher l’état, mais pas modifier les routes. | Rôle, privilège ou décision par commande. |
| Accounting | Quelles sessions et opérations ont eu lieu ? | Une session démarre, une commande de configuration est exécutée puis la session se termine. | Événements horodatés attribuables à un compte. |

Dans une organisation mature, ces fonctions sont traduites en règles vérifiables. Par exemple : « les administrateurs réseau nominatifs peuvent ouvrir une session SSH depuis le réseau de gestion ; les opérateurs de supervision sont en lecture seule ; les commandes de changement de configuration sont autorisées uniquement au groupe réseau ; toutes les sessions et commandes prises en charge sont journalisées ; un compte d’urgence distinct est stocké et utilisé selon une procédure de secours ». Cette phrase contient identité, contexte, autorisation, accounting et gestion des exceptions.

Une politique AAA peut être centralisée dans un serveur, mais le point d’application reste généralement l’équipement : routeur, commutateur, contrôleur Wi-Fi, concentrateur VPN ou pare-feu. Le serveur décide et renvoie des attributs ou une réponse ; l’équipement doit comprendre cette réponse et appliquer le comportement attendu. Il faut donc vérifier de bout en bout le serveur, la communication, la compatibilité des attributs et les capacités du client AAA.

### 1.2. Architecture : supplicant, authenticator, client AAA et serveur

Ces termes changent de sens selon le scénario. En administration d’équipements, le routeur est le client AAA et l’administrateur est l’utilisateur. Dans 802.1X, le terminal est couramment appelé **supplicant**, le commutateur ou point d’accès est l’**authenticator**, et l’authenticator relaie les échanges vers le serveur d’authentification, souvent à l’aide de RADIUS.

```text
ADMINISTRATION D'UN EQUIPEMENT

 Administrateur --SSH--> Routeur / Switch (client AAA)
                                  |
                                  | RADIUS ou TACACS+
                                  v
                            Serveur AAA
                              |      |
                         Annuaire   Journaux/SIEM

CONTROLE D'ACCES 802.1X

 Terminal (supplicant) --EAPOL--> Switch (authenticator)
                                       |
                                       | EAP encapsulé dans RADIUS
                                       v
                                  Serveur RADIUS
                                       |
                                  Annuaire / PKI
```

Il faut distinguer **EAPOL** (EAP over LAN, utilisé entre terminal et authenticator), **EAP** (cadre d’échange des méthodes d’authentification) et **RADIUS** (protocole de transport entre l’équipement d’accès et le serveur AAA, dans le déploiement classique). Un terminal 802.1X ne parle donc pas forcément directement à RADIUS. Cette distinction aide à isoler les pannes : un problème EAPOL local ne se diagnostique pas de la même manière qu’un secret RADIUS incorrect ou une règle de serveur qui rejette le certificat.

### 1.3. RADIUS et TACACS+ : choisir selon le scénario

**RADIUS** est courant pour l’accès au réseau, le Wi-Fi d’entreprise, 802.1X, certains VPN et l’attribution de profils. Historiquement, RADIUS transporte des messages sur UDP avec les ports habituels 1812 pour l’authentification/autorisation et 1813 pour l’accounting. Les attributs normalisés et spécifiques au constructeur transportent des informations d’identité, de session et de politique. Les détails du comportement d’un attribut doivent être vérifiés dans les documentations du client et du serveur, car une valeur renvoyée mais ignorée par l’équipement ne produit pas le résultat recherché.

**TACACS+** est largement utilisé pour l’administration des équipements. Il sépare les échanges d’authentification, d’autorisation et d’accounting et peut permettre l’autorisation des commandes CLI une par une, si le client et le serveur la prennent en charge. Cette granularité est utile pour séparer les opérateurs en lecture seule des administrateurs capables de modifier la configuration. Le port historique est TCP/49.

| Critère | RADIUS | TACACS+ |
|---|---|---|
| Usage courant | 802.1X, Wi-Fi, VPN, NAC, accès réseau | Administration des équipements réseau |
| Transport classique | UDP, avec ports distincts selon les fonctions | TCP, port historique 49 |
| Séparation des fonctions AAA | Intégrées dans les échanges et attributs RADIUS | Authentification, autorisation et accounting ont des échanges distincts |
| Autorisation d’une commande CLI | Dépend de l’équipement et de l’implémentation ; moins typique | Fonction fréquente dans l’administration des équipements compatibles |
| Données de politique | Attributs normalisés et attributs constructeur | Attributs et arguments adaptés à l’administration d’équipements |
| Chiffrement historique du protocole | Le modèle UDP classique ne chiffre pas le paquet intégral | L’obfuscation historique du corps ne doit pas être considérée comme un chiffrement moderne |
| Transport sécurisé | Options TLS/DTLS ou protection réseau selon prise en charge | TACACS+ sur TLS 1.3 est spécifié par RFC 9887 ; la prise en charge produit doit être confirmée |

Il ne faut pas conclure qu’un protocole est « toujours plus sécurisé » en regardant uniquement son nom. Le résultat dépend de la version, du transport, de la validation des certificats, des secrets, de la protection du réseau de gestion et de la politique. Un service RADIUS classique accessible depuis un réseau non fiable n’équivaut pas à un déploiement correctement protégé par TLS ou un réseau de confiance. De même, TACACS+ historique ne fournit pas à lui seul les garanties d’un canal TLS moderne.

### 1.4. Transport et protection des échanges

Le secret partagé historique de RADIUS permet au client et au serveur de vérifier certaines données du protocole et sert à protéger quelques attributs sensibles selon les mécanismes classiques. Cela ne signifie pas que l’ensemble du paquet RADIUS est chiffré. Les attributs de politique, les identifiants et les métadonnées peuvent exposer des informations selon le scénario et les extensions utilisées. Le contrôle de l’adresse source du client, le secret unique par client, le filtrage des flux et la protection de la voie de gestion restent importants.

Le RADIUS classique utilise habituellement UDP/1812 pour les demandes d’authentification et UDP/1813 pour l’accounting. Des extensions et déploiements particuliers peuvent employer d’autres ports. Les solutions RADIUS sur TLS ou DTLS sont documentées par l’IETF, mais il faut vérifier leur disponibilité sur chaque serveur et client avant de les retenir pour un projet. RFC 9765 définit expérimentalement RADIUS/1.1 négocié avec ALPN afin de supprimer certains mécanismes MD5 de la variante de protocole concernée ; cette RFC est **expérimentale**, ce qui ne signifie pas qu’elle est activée ou largement prise en charge dans tous les produits.

Le RFC 9887, publié en décembre 2025, spécifie TACACS+ transporté par TLS 1.3 et met en évidence les limites du mécanisme historique d’obfuscation. Il est essentiel de ne pas supposer qu’un équipement existant prend cette variante en charge simplement parce que la spécification existe. Vérifie les versions, la configuration, le port attendu (300 par défaut pour cette variante TLS, contre 49 pour TACACS+ historique) et les exigences de certificats. Un client TLS ne doit pas basculer silencieusement vers un transport non-TLS si l’établissement TLS échoue.

> **Piège :** « le mot de passe est masqué dans une capture » ne prouve pas que le transport est chiffré de bout en bout. Une capture peut sembler peu lisible tout en révélant des attributs, des métadonnées ou une partie des échanges. Identifie précisément la variante du protocole, l’encapsulation et les garanties de confidentialité et d’intégrité avant de qualifier le canal de sécurisé.

### 1.5. Séquences d’échange et états possibles

Pour une demande d’administration classique, le déroulement logique peut être représenté ainsi :

1. L’utilisateur ouvre une session vers l’adresse de gestion du routeur ou du commutateur.
2. L’équipement demande un nom d’utilisateur et une preuve d’identité, selon la méthode d’accès.
3. Le client AAA construit une demande et la transmet au serveur configuré.
4. Le serveur vérifie le client réseau, l’identité, les règles, les groupes ou les facteurs requis.
5. Le serveur renvoie une réponse acceptée, rejetée ou parfois un challenge nécessitant une étape supplémentaire.
6. L’équipement applique la politique : ouverture de session, niveau de privilège, autorisation EXEC et, éventuellement, autorisation de commandes.
7. L’accounting enregistre les événements configurés.
8. À la fermeture ou à l’expiration de la session, les événements de fin sont envoyés, s’ils sont pris en charge et si la communication est disponible.

```text
Utilisateur        Equipement/client AAA        Serveur AAA
    |                       |                        |
    |---- demande SSH ----->|                        |
    |<--- demande login ----|                        |
    |---- identifiants ---->|                        |
    |                       |---- Access-Request --->|
    |                       |<--- Accept/Reject -----|
    |                       |                        |
    |       si accepté : appliquer autorisation      |
    |<--- session autorisée ou refusée --------------|
    |                       |---- accounting ------->|
```

Dans RADIUS, les réponses habituelles de la procédure d’accès incluent Access-Accept, Access-Reject et Access-Challenge. Un challenge peut faire partie d’un mécanisme à plusieurs étapes, par exemple lors d’un échange interactif. Le client doit gérer le déroulement attendu. Un **Access-Reject** est un refus explicite, alors qu’une **absence de réponse** indique plutôt une indisponibilité, un filtrage, une perte de paquet ou une erreur de transport. Cette différence influence la décision de secours.

Dans les équipements IOS/IOS XE, les listes de méthodes AAA déterminent les mécanismes essayés et l’ordre dans lequel ils le sont. Les comportements précis peuvent varier selon le type de liste et la version ; ils doivent être testés sur le matériel cible. En règle générale, une méthode de secours locale ne doit pas devenir un moyen de contourner un refus explicite du serveur central. Elle est destinée au scénario de défaillance défini par la politique, pas à permettre à un ancien compte local de passer après un rejet intentionnel.

### 1.6. Listes de méthodes Cisco : lecture et contrôle

Avec `aaa new-model`, IOS/IOS XE active le modèle AAA. Les méthodes sont ensuite configurées pour un type d’accès précis : connexion, autorisation EXEC, autorisation de commandes ou accounting. Une liste nommée peut être appliquée à certaines lignes ou interfaces, ce qui permet de distinguer les politiques de la console, de SSH, du VPN ou de 802.1X. Les exemples ci-dessous sont indicatifs : certains mots-clés ou comportements sont propres à une famille de produits.

Exemple de lecture :

```text
aaa authentication login VTY-LOGIN group ADMIN-TAC local
```

Cette liste indique que l’équipement essaie le groupe de serveurs TACACS+ `ADMIN-TAC`, puis peut utiliser la base locale dans les conditions de repli définies par l’implémentation. Elle n’équivaut pas à « accepter localement chaque demande rejetée par le serveur ». Un serveur peut répondre explicitement par un refus ; la manière dont la liste traite cette réponse doit être vérifiée dans la documentation et dans un test contrôlé.

Les mots-clés `default` et les noms de liste ne sont pas interchangeables. `default` définit le comportement par défaut pour un type AAA lorsqu’aucune liste plus spécifique n’est appliquée. Une liste nommée doit être liée à la ligne ou à l’interface concernée, sinon elle peut rester définie mais inutilisée. Une erreur fréquente consiste à écrire la liste correctement, puis à oublier `login authentication NOM-DE-LISTE` sur les lignes VTY.

Les listes distinctes aident à appliquer le principe du moindre privilège. Par exemple, on peut avoir une liste d’authentification des connexions SSH, une liste d’autorisation EXEC, une liste pour les commandes de niveau 15 et une liste d’accounting. Il faut toutefois veiller à ce que les noms restent cohérents, à ce que les services du serveur comprennent les demandes et à ce que les rôles ne soient pas confondus entre authentification et autorisation.

### 1.7. Autorisation EXEC et autorisation des commandes

Après authentification, l’équipement doit décider quel environnement d’exécution offrir. L’autorisation EXEC peut déterminer si l’utilisateur accède au shell ou au CLI et avec quels attributs de privilège selon les capacités de la plate-forme. Le niveau de privilège 15 de Cisco est souvent associé au mode privilégié, mais il ne constitue pas à lui seul une modélisation complète des rôles. Les menus, views, politiques par commande et mécanismes propres à certaines plateformes peuvent offrir une granularité supplémentaire.

**Autorisation par commande.** Sur les produits et serveurs qui la prennent en charge, un client peut transmettre une demande d’autorisation quand l’utilisateur essaie d’exécuter une commande. Le serveur décide d’autoriser ou de refuser. Le fonctionnement doit être testé pour les commandes simples, les commandes imbriquées et les commandes de configuration. Le contexte de commande peut être transmis sous forme d’arguments ou d’attributs ; les différences de parsing entre équipements peuvent produire des règles trop permissives ou trop restrictives.

Il faut définir les rôles à partir des tâches et non attribuer le niveau maximal à tous les comptes. Quelques rôles typiques :

| Rôle | Actions permises typiques | Actions à refuser ou limiter |
|---|---|---|
| Supervision | Consulter l’état, les compteurs, les voisins et les journaux non sensibles. | Modification de configuration, secrets, effacement des journaux. |
| Exploitation N1 | Vérifications guidées et commandes de diagnostic limitées. | Modifications de routage et d’authentification. |
| Réseau N2 | Changements approuvés selon le périmètre et la fenêtre. | Administration des comptes globaux sans autorisation spécifique. |
| Administrateur AAA | Gestion des méthodes, serveurs, rôles et audits AAA. | Usage quotidien non contrôlé des comptes d’urgence. |
| Compte d’urgence | Récupération strictement nécessaire lorsque la voie normale échoue. | Connexion permanente ou utilisation ordinaire non justifiée. |

Une politique qui autorise `show` mais refuse toutes les commandes de modification peut être appropriée pour la supervision, mais elle doit tenir compte des variantes de commandes et des commandes qui modifient indirectement l’état. Teste des exemples autorisés et interdits, y compris les alias, les sous-commandes, les commandes en mode configuration et les fonctions introduites par une nouvelle version logicielle.

### 1.8. Accounting : sessions, commandes et qualité des preuves

L’accounting peut enregistrer les débuts et fins de session, la durée, les paramètres d’accès, des volumes ou les commandes exécutées si les produits et la configuration le permettent. Les événements n’ont pas tous la même fiabilité : une commande de démarrage de session peut être enregistrée alors que l’événement de fin est perdu si l’équipement redémarre ou si le serveur est injoignable. Il faut donc éviter d’interpréter un événement manquant comme une preuve absolue que l’action n’a pas eu lieu.

Une bonne chaîne de preuve dépend de plusieurs conditions :

- les horloges des serveurs et équipements sont synchronisées par une source de temps fiable ;
- les identités sont nominatives, et les comptes partagés sont limités aux cas exceptionnels ;
- les journaux sont transmis de manière fiable, contrôlés contre les altérations et stockés avec des accès restreints ;
- les équipements et le serveur conservent des identifiants de session permettant de rapprocher les événements ;
- la durée de conservation est documentée et cohérente avec les obligations internes ou réglementaires ;
- les tests couvrent les pertes de connectivité, les redémarrages, les changements d’heure et les rotations de serveurs.

Un journal détaillé améliore les investigations, mais augmente le volume de données sensibles. Ne consigne pas les mots de passe, secrets partagés ou jetons MFA dans des messages de diagnostic. Définis qui peut chercher, exporter et supprimer les événements, et alerte sur les interruptions d’accounting plutôt que de supposer qu’elles sont sans conséquence.

### 1.9. Mécanismes de secours, panne et refus explicite

Il faut distinguer au moins quatre situations :

1. **Acceptation** : le serveur a reconnu l’identité et les règles d’autorisation permettent l’accès.
2. **Refus** : le serveur a reçu et traité la demande, mais la politique n’autorise pas l’accès.
3. **Absence de réponse** : les requêtes expirent, ce qui peut indiquer panne, perte ou filtrage réseau, client inconnu, mauvaise adresse, port fermé ou problème applicatif.
4. **Réponse invalide ou incohérente** : secret différent, certificat non approuvé, attribut inattendu, message mal formé, horloge/certificat expiré ou incompatibilité logicielle.

Le comportement d’une liste de méthodes en présence d’un refus n’est pas nécessairement celui d’une liste en présence d’une expiration. L’ordre des méthodes doit être choisi consciemment et vérifié avec des tests de panne et de refus. Si le comportement de repli n’est pas compris, une mauvaise configuration peut soit verrouiller l’administrateur dehors, soit autoriser un compte local après un refus qui devait rester définitif.

Le compte local de secours doit être nominatif ou géré dans un coffre de secrets, disposer du minimum de privilèges nécessaire, être utilisable uniquement depuis des chemins d’administration maîtrisés et déclencher un audit en cas d’usage. Il doit être testé périodiquement. Pour un parc critique, il est préférable de maintenir une console ou un réseau de gestion hors bande, si la conception le permet, au lieu de dépendre uniquement d’une authentification à travers le réseau en panne.

> **Astuce :** réalise une matrice de test avec quatre résultats — serveur accepte, serveur refuse, serveur ne répond pas, secret/certificat est incorrect. Pour chaque cas, note si l’équipement autorise la connexion, quelle méthode est utilisée, ce qui apparaît dans les journaux et comment récupérer le contrôle. Le test de « serveur inaccessible » ne remplace pas celui de « compte refusé ».

### 1.10. Haute disponibilité : redondance, préférence et cohérence

La présence de deux serveurs AAA configurés ne garantit pas automatiquement une haute disponibilité correcte. Les clients doivent pouvoir joindre les deux serveurs, ceux-ci doivent appliquer des politiques cohérentes, leurs bases d’identité et certificats doivent être maintenus, et les journaux doivent rester corrélables. Les délais d’attente et le nombre de tentatives influencent directement l’expérience utilisateur : un délai trop long rend une panne visible pendant plusieurs dizaines de secondes ; un délai trop court peut provoquer des basculements lors d’une simple congestion.

| Élément | Question de conception | Test opérationnel |
|---|---|---|
| Redondance réseau | Les équipements atteignent-ils chaque serveur depuis l’adresse source attendue ? | Tester la connectivité et les ports de service de chaque chemin. |
| Serveurs AAA | Le second serveur possède-t-il les mêmes utilisateurs, certificats, clients et politiques ? | Tester le même compte et les mêmes rôles sur chaque serveur. |
| Délais d’attente | La latence nominale reste-t-elle largement sous le timeout ? | Mesurer dans les périodes chargées et pendant une panne contrôlée. |
| Priorité des serveurs | Quel serveur reçoit les demandes en fonctionnement normal ? | Observer les journaux pour confirmer l’ordre effectif. |
| Accounting | Les événements sont-ils perdus pendant le basculement ? | Couper un chemin de façon contrôlée et vérifier la continuité. |
| Changement de secret | Tous les clients et serveurs ont-ils été modifiés dans le bon ordre ? | Tester chaque équipement avant de supprimer l’ancien secret. |

Deux serveurs actifs peuvent être une configuration valide ou un facteur de divergence selon l’architecture. Documente les règles de réplication, le délai de propagation et la source de vérité pour les groupes. Les comptes désactivés, certificats révoqués et rôles modifiés doivent être appliqués dans un délai acceptable. Ne suppose pas que la disponibilité est démontrée par un ping : la couche applicative, les méthodes d’identité et l’autorisation doivent elles aussi fonctionner.

### 1.11. 802.1X, EAP et décision d’accès au réseau

802.1X fournit le contrôle d’accès basé sur le port. Dans un déploiement filaire, le commutateur peut maintenir le port dans un état non autorisé avant l’authentification, avec seulement les échanges nécessaires pour le processus. En Wi-Fi d’entreprise, le point d’accès ou le contrôleur prend un rôle similaire. La décision AAA peut attribuer un VLAN, une ACL téléchargeable, une durée de session ou d’autres attributs selon les capacités de l’infrastructure.

**EAP** est un cadre pour plusieurs méthodes. EAP-TLS utilise des certificats et TLS pour authentifier les parties selon la configuration. Des méthodes basées sur un nom d’utilisateur et un mot de passe existent également, mais leurs garanties dépendent fortement du tunnel TLS, de la validation du certificat serveur et de la configuration du client. Un poste qui accepte un certificat serveur arbitraire pourrait envoyer ses informations d’authentification à un faux serveur.

802.1X n’est pas un substitut aux protections de couche 2 ou à la segmentation. Un port authentifié peut encore accéder à des ressources qui doivent être filtrées par les ACL, pare-feu et politiques de routage. L’identité du terminal, l’intégrité du certificat, l’état de l’appareil et le profil reçu peuvent faire partie d’une politique de contrôle d’accès réseau plus vaste.

### 1.12. RADIUS : attributs, VLAN et autorisation dynamique

RADIUS transporte une collection d’attributs. Selon le scénario, ces attributs peuvent désigner l’identité, l’adresse du NAS, la méthode utilisée, le VLAN, le délai de session ou des informations de comptabilisation. Pour assigner un VLAN dynamique, les valeurs renvoyées par le serveur doivent correspondre au format attendu par la plate-forme, et le VLAN doit exister ou être créé selon les possibilités du système. Une authentification réussie sans application de VLAN peut venir d’une politique absente, d’un attribut mal formé, d’une incompatibilité ou d’une fonction non activée côté commutateur.

Les extensions d’autorisation dynamique permettent dans certains déploiements de changer une session après l’authentification, par exemple pour demander une déconnexion ou réévaluer certaines autorisations. La famille décrite par RFC 5176 inclut notamment CoA (Change of Authorization) et Disconnect. Dans la pratique, vérifier les ports, la confiance du client d’autorisation, les secrets/certificats, les protections anti-rejeu et les conséquences d’une erreur de politique est indispensable. Une commande CoA mal ciblée peut déconnecter beaucoup d’utilisateurs ; un client non autorisé ne doit jamais pouvoir envoyer ces messages depuis un réseau non fiable.

### 1.13. Intégration à un annuaire, MFA et cycle de vie des identités

Un serveur AAA peut s’appuyer sur une base propre, un annuaire LDAP, Active Directory, un fournisseur d’identité ou une PKI. L’annuaire centralise les identités, mais les décisions de rôle doivent rester explicites. Être membre d’un groupe général « IT » ne devrait pas nécessairement autoriser chaque opération privilégiée sur tous les équipements.

Le cycle de vie des identités doit couvrir l’arrivée, le changement de poste, la suspension et le départ. Les droits doivent être accordés sur justification, réévalués lors d’un transfert et retirés rapidement à la fin du besoin. Les comptes de service ont un propriétaire, une finalité, une échéance ou une procédure de revue. Les certificats ont une chaîne de confiance, une date de validité et un processus de révocation ou de remplacement.

**MFA** renforce l’authentification en combinant des facteurs distincts, par exemple un facteur de connaissance et une clé de sécurité. Deux éléments équivalents du même type ne deviennent pas automatiquement une authentification multifacteur. Le MFA doit être particulièrement considéré pour les accès privilégiés, VPN d’administration et accès sensibles. Le choix d’une méthode dépend du risque, de la compatibilité des équipements, du besoin hors ligne et de la capacité à gérer les pertes d’appareil.

### 1.14. Modèle de décision : flux complet

```text
                DEMANDE D'ACCES
                      |
                      v
            Identité / appareil présenté
                      |
                      v
         Authentification (local ou central)
                      |
           +----------+----------+
           |                     |
        Rejet                  Succès
           |                     |
           v                     v
       Refus / log       Evaluation de la politique
                                 |
                       +---------+---------+
                       |                   |
                    Refus              Autorisé
                       |                   |
                       v                   v
                    Refus          Attributs/rôle/session
                                           |
                                           v
                                Accounting + supervision
```

Ce schéma représente la logique fonctionnelle, pas tous les échanges protocolaires. La décision réelle peut impliquer plusieurs étapes, un challenge MFA, un certificat, une autorisation EXEC puis des vérifications de commandes. L’accounting peut commencer avant certaines actions ou envoyer des événements de mise à jour ; le détail dépend du mécanisme et du produit.

### 1.15. Risques classiques à ce niveau

Les erreurs les plus dangereuses proviennent souvent de l’interaction entre mécanismes pourtant corrects isolément :

- le serveur autorise l’utilisateur, mais renvoie un attribut de privilège trop élevé ;
- l’équipement est client AAA, mais son IP source n’est pas celle autorisée par le serveur ;
- le réseau laisse passer les requêtes d’authentification, mais bloque l’accounting ou le retour dynamique ;
- le serveur secondaire possède des règles plus permissives que le principal ;
- une politique EAP valide le compte sans vérifier correctement l’identité du serveur TLS ;
- les journaux sont présents, mais l’heure diverge et les événements ne peuvent être corrélés ;
- le mécanisme local de secours est documenté, mais n’a pas été testé depuis des mois ;
- la journalisation des commandes est activée alors que les administrateurs partagent un seul identifiant ;
- une migration de transport laisse une voie de repli en clair qui contourne la nouvelle protection.

> **Piège :** une règle AAA centrale ne suffit pas si la configuration du client utilise une autre liste, un autre serveur, un autre groupe ou un compte local qui n’a pas été retiré. Cartographie séparément les règles côté serveur et côté équipement. Les deux extrémités font partie de la politique effective.

---

## 2. Configuration et pratique

### 2.1. Objectifs du laboratoire

Le laboratoire vise à séparer les étapes de configuration, à appliquer une méthode d’authentification nommée aux accès SSH, à configurer un groupe TACACS+ ou RADIUS selon le cas, à ajouter l’autorisation et l’accounting lorsque le matériel le permet, puis à tester les pannes sans perdre l’administration. Les adresses du document appartiennent aux plages réservées à la documentation et doivent être remplacées dans un véritable laboratoire.

Objectifs vérifiables :

1. se connecter par SSH avec un compte local avant de toucher AAA ;
2. configurer le serveur central et vérifier la connectivité depuis l’adresse source réellement utilisée ;
3. créer et appliquer une liste de méthodes au bon type d’accès ;
4. tester acceptation, rejet, absence de réponse et secret incorrect ;
5. vérifier l’autorisation EXEC/commandes et l’accounting séparément ;
6. prouver qu’un mécanisme de secours fonctionne comme prévu ;
7. documenter la procédure de retour arrière.

### 2.2. Topologie et plan d’adressage

```text
                    Réseau d'administration

 Poste admin
 192.0.2.50
      |
      | SSH
      v
+---------------------+       Réseau de gestion       +--------------------+
| SW-ADMIN / R1       |------------------------------>| Serveur AAA        |
| 192.0.2.1           |                               | 192.0.2.10         |
| client AAA          |                               | TACACS+ / RADIUS   |
+---------------------+                               +--------------------+
      |
      +---- console / accès hors bande pour récupération
```

| Élément | Adresse d’exemple | Rôle |
|---|---|---|
| Équipement géré | `192.0.2.1` | Routeur ou commutateur Cisco IOS/IOS XE. |
| Serveur AAA | `192.0.2.10` | Serveur TACACS+ pour l’administration ou RADIUS pour NAC. |
| Poste de gestion | `192.0.2.50` | Client SSH autorisé. |
| Réseau de gestion | `192.0.2.0/24` | Réseau isolé ou filtré pour l’administration. |

Les adresses `192.0.2.0/24` sont réservées aux exemples de documentation. Elles ne doivent pas être copiées comme adresses de production. Pour un déploiement réel, choisis des plages appropriées, une route de retour vers le client et des ACL qui n’autorisent que les sources nécessaires.

### 2.3. Étape zéro : sauvegarde et accès de secours

Avant d’activer AAA, confirme qu’au moins un accès de récupération indépendant est disponible, généralement une console locale ou une voie de gestion hors bande. Crée un utilisateur local de secours avec un secret robuste stocké dans un coffre approuvé. N’inscris pas ce secret dans un ticket ou dans le fichier de configuration partagé. Vérifie également que SSH fonctionne et qu’une session de test peut être ouverte depuis le poste autorisé.

```text
! Exemple IOS/IOS XE : syntaxe à valider sur la plateforme
hostname SW-ADMIN
ip domain-name lab.example
username secours privilege 15 secret <SECRET-ROBUSTE-UNIQUE>
crypto key generate rsa modulus 2048
ip ssh version 2

! Restreindre les sources de gestion selon la stratégie du laboratoire
ip access-list standard MGMT-SOURCES
 permit 192.0.2.50
 deny any log

line vty 0 15
 access-class MGMT-SOURCES in
 transport input ssh
 login local
```

La commande de création de clé peut demander une confirmation ou dépendre des capacités cryptographiques de la version. Dans un réseau réel, utilise les tailles et algorithmes recommandés par la politique de sécurité applicable, ainsi que les possibilités actuelles de la plateforme. Une ACL VTY doit être testée avec une seconde session : une erreur de réseau ou de masque peut bloquer le poste qui devait administrer l’appareil.

**Ne ferme pas la session initiale** durant la transition AAA. Garde une autre session ouverte après chaque modification. Si l’accès console est disponible, vérifie qu’il fonctionne indépendamment de la méthode appliquée aux lignes VTY.

### 2.4. Configurer un groupe TACACS+ pour l’administration

Le serveur TACACS+ doit déclarer l’équipement comme client connu, associer le bon secret ou la bonne identité de transport, reconnaître l’adresse source utilisée et appliquer les politiques des administrateurs. Sur l’équipement, le nom du serveur et le groupe doivent correspondre aux objets référencés dans les listes AAA.

```text
! Exemple classique, sans transport TLS : vérifier la syntaxe prise en charge
configure terminal
aaa new-model

username secours privilege 15 secret <SECRET-ROBUSTE-UNIQUE>

tacacs server TAC1
 address ipv4 192.0.2.10
 key <SECRET-PARTAGE-UNIQUE>
 timeout 5
!

aaa group server tacacs+ ADMIN-TAC
 server name TAC1
!
end
```

Ne réutilise pas littéralement le même secret pour tous les clients de l’infrastructure si la solution permet des secrets distincts. Stocke et distribue la valeur par un canal protégé. Le secret doit être identique côté serveur et client, mais ne doit pas être exposé dans des captures, scripts non protégés ou sauvegardes accessibles à tous.

Le bloc ci-dessus illustre le modèle TACACS+ historique. Il ne configure pas automatiquement TACACS+ over TLS. Si le matériel et le serveur prennent en charge la variante TLS 1.3 définie par RFC 9887, suis les instructions spécifiques du constructeur pour les certificats, le port et les paramètres du transport. Ne transforme pas arbitrairement un port 49 en port TLS et ne suppose pas qu’une simple ligne `key` remplace la validation de certificats.

### 2.5. Créer et appliquer des listes AAA nommées

Une approche plus sûre consiste à configurer les listes, puis à les appliquer aux lignes VTY uniquement après avoir vérifié le serveur et l’accès local. La configuration ci-dessous représente un exemple courant ; les commandes exactes et le comportement de secours dépendent de la plate-forme et de la version.

```text
configure terminal

aaa authentication login VTY-LOGIN group ADMIN-TAC local
aaa authorization exec VTY-EXEC group ADMIN-TAC local
aaa accounting exec VTY-EXEC start-stop group ADMIN-TAC

line vty 0 15
 login authentication VTY-LOGIN
 authorization exec VTY-EXEC
 accounting exec VTY-EXEC
 transport input ssh
 access-class MGMT-SOURCES in
end
```

La liste `VTY-LOGIN` traite l’authentification des connexions. `VTY-EXEC` sert ici à l’autorisation EXEC et à l’accounting EXEC, si la version prend en charge ces associations. N’active pas l’autorisation des commandes immédiatement sur un routeur distant critique : commence avec un équipement de test, valide chaque commande nécessaire au diagnostic puis élargis les règles selon la procédure de changement.

Si l’équipement ne supporte pas la même syntaxe ou si une fonction d’autorisation échoue, consulte le guide de configuration de la version exacte. Une commande refusée par le serveur peut être interprétée différemment d’un serveur indisponible. Ne traite pas le mot-clé `local` comme une garantie universelle de repli après n’importe quel type d’échec.

### 2.6. Ajouter l’autorisation des commandes avec prudence

L’autorisation des commandes peut être utile pour différencier l’exploitation en lecture seule de l’administration. Elle introduit aussi un risque opérationnel : si le serveur ne connaît pas une commande requise pour réparer le réseau, l’administrateur peut être authentifié mais incapable d’agir. Sur certains équipements, une partie des commandes est interprétée localement ou regroupe les sous-commandes d’une manière inattendue. Les règles doivent donc être testées sur le CLI exact.

Exemple conceptuel à adapter :

```text
! Syntaxe représentative, à vérifier selon la version IOS/IOS XE
configure terminal
aaa authorization commands 15 VTY-COMMANDS group ADMIN-TAC local
aaa accounting commands 15 VTY-COMMANDS start-stop group ADMIN-TAC
!
line vty 0 15
 authorization commands 15 VTY-COMMANDS
 accounting commands 15 VTY-COMMANDS
end
```

Selon le serveur, l’autorisation d’une commande peut reposer sur les attributs de commande reçus, sur un rôle ou sur un profil. Définis d’abord une matrice d’opérations ; ne démarre pas par une expression complexe qui tente de couvrir tous les cas. Documente les commandes d’observation, les commandes de modification et les commandes interdites par rôle.

| Test | Exemple | Résultat attendu à définir |
|---|---|---|
| Lecture simple | `show interfaces status` ou équivalent plateforme | Autorisé pour supervision. |
| Lecture de routage | `show ip route` | Autorisé uniquement aux rôles qui en ont besoin. |
| Mode configuration | `configure terminal` | Refusé pour supervision, autorisé pour réseau N2/N3 selon rôle. |
| Changement de production | Modification d’une route ou ACL en laboratoire | Refusé si le compte n’a pas le rôle adéquat. |
| Commande rare de dépannage | Commande prévue par le runbook | Autorisée au rôle d’intervention concerné. |

Les exemples sont volontairement indicatifs, car les commandes varient selon les produits. N’utilise pas un laboratoire de commande pour tester directement sur une infrastructure de production sans fenêtre de changement, validation et retour arrière.

### 2.7. Tester le repli local et les états du serveur

Avant de finaliser la configuration, exécute une matrice de tests. Les résultats doivent être observés dans le CLI et dans le journal du serveur. Il ne suffit pas que la connexion réussisse : il faut savoir quelle méthode a accepté l’identité.

| Scénario | Préparation | Observation à capturer | Contrôle attendu |
|---|---|---|---|
| Compte central valide | Serveur accessible, compte autorisé | Demande côté serveur, rôle renvoyé, session ouverte | Connexion autorisée et journalisée. |
| Compte central rejeté | Utilisateur désactivé ou refus de politique | Réponse explicite du serveur | Refus conforme à la politique, sans contournement non voulu. |
| Serveur indisponible | Coupure de laboratoire du chemin AAA | Timeouts, tentatives, voie utilisée | Repli uniquement selon le design documenté. |
| Secret incorrect | Valeur temporairement incorrecte en laboratoire | Erreur d’intégrité ou absence de service selon produit | Pas de bascule silencieuse vers une méthode moins sûre. |
| Second serveur actif | Premier serveur arrêté de manière contrôlée | Demande reçue par le secondaire | Politique équivalente et délais acceptables. |
| Accounting interrompu | Flux comptable filtré en laboratoire | Session active, événement absent ou retardé | Alerte et preuve de l’impact. |

Ne provoque pas de panne de serveur AAA dans un réseau de production sans plan approuvé. Une erreur de test peut affecter l’administration de plusieurs équipements. Sauvegarde la configuration, maintiens la console disponible et consigne l’état initial et final.

### 2.8. Configurer RADIUS pour un scénario 802.1X

Ce deuxième exemple est séparé de TACACS+ : il illustre le rôle de RADIUS lors de l’accès réseau d’un terminal. Le serveur doit disposer du commutateur comme client RADIUS, avec l’adresse source correcte, et d’une politique d’identité. Le terminal doit être configuré en supplicant 802.1X avec une méthode EAP compatible. Le commutateur doit posséder les VLAN requis et avoir une configuration d’accès adaptée.

```text
! Exemple de structure Catalyst IOS/IOS XE : vérifier le guide exact
radius server NAC1
 address ipv4 192.0.2.10 auth-port 1812 acct-port 1813
 key <SECRET-RADIUS-UNIQUE>
!
aaa group server radius NAC-GROUP
 server name NAC1
!
aaa authentication dot1x default group NAC-GROUP
aaa authorization network default group NAC-GROUP
aaa accounting dot1x default start-stop group NAC-GROUP
!
dot1x system-auth-control
```

Sur une interface de bordure, une configuration type peut inclure un port d’accès, l’authenticator 802.1X et une politique de contrôle de port. La syntaxe exacte change selon les familles de commutateurs, notamment pour l’authentification multi-hôte, les appareils téléphoniques, le comportement MAB et les VLAN de quarantaine. N’applique pas un exemple générique sans lire le guide de la plateforme.

```text
interface GigabitEthernet1/0/10
 description Poste-utilisateur-laboratoire
 switchport mode access
 authentication port-control auto
 dot1x pae authenticator
 spanning-tree portfast
```

Le bloc de port est illustratif et ne contient pas l’ensemble des réglages qu’une production peut nécessiter. En particulier, la décision d’autoriser une méthode de secours MAC Authentication Bypass (MAB) ne doit pas être prise par défaut : l’adresse MAC est usurpable et n’est pas une preuve forte d’identité humaine. Si MAB est indispensable pour un appareil sans supplicant, isole l’appareil dans un profil restreint et contrôle les flux autorisés.

### 2.9. Vérifier la politique et les attributs RADIUS

Les commandes de vérification disponibles dépendent de la plate-forme. Sur les équipements Cisco, on trouve souvent des commandes `show aaa`, des vues sur les serveurs RADIUS/TACACS+, des statistiques, des sessions 802.1X ou des commandes de diagnostic spécifiques à la version. Les syntaxes ci-dessous sont des familles de commandes à confirmer dans le guide du produit :

```text
show running-config | section aaa
show running-config | section radius
show running-config | section tacacs
show aaa servers
show radius statistics
show tacacs
show dot1x all
show authentication sessions
```

Une commande non disponible ne veut pas forcément dire que le service ne fonctionne pas ; le nom change selon la gamme et la version. Si les commandes sont prises en charge, relève les compteurs avant et après une tentative pour repérer si une requête est envoyée, si elle reçoit une réponse et si elle est acceptée ou rejetée.

Pour un VLAN dynamique, vérifie en particulier :

1. l’identité que le serveur a réellement traitée ;
2. le profil de politique choisi et ses attributs ;
3. le format et les valeurs exactes de l’attribut VLAN attendu ;
4. la présence du VLAN sur le commutateur ou sa création dynamique autorisée ;
5. la table d’affectation de la session et les journaux de changement d’autorisation ;
6. la connectivité après affectation, notamment DHCP, passerelle et DNS.

### 2.10. Accounting et journalisation centralisée

L’accounting de session ne remplace ni les journaux système ni une collecte centralisée. Il apporte des événements propres au protocole AAA, tandis que Syslog peut enregistrer les changements de configuration, l’état des interfaces ou les échecs d’accès. Un SIEM peut rapprocher ces données si les horloges sont synchronisées et si l’identité de l’utilisateur est cohérente entre les sources.

Une configuration de production doit prévoir :

- une source de temps fiable et le contrôle du décalage ;
- des destinations de journaux clairement identifiées ;
- une protection de transport adaptée à la sensibilité des événements ;
- le filtrage des données inutiles ou trop sensibles ;
- la surveillance des pertes de journal, des files saturées et des erreurs d’envoi ;
- une rétention documentée, des contrôles d’accès et une procédure d’export pour investigation.

Ne partage pas les sorties de commande qui contiennent secrets, clés, jetons ou attributs sensibles dans des canaux ouverts. Une capture de dépannage doit être limitée au besoin, protégée au repos, puis supprimée conformément à la procédure de conservation.

### 2.11. Segmentation de gestion et filtrage réseau

Les flux AAA doivent être autorisés uniquement entre les équipements qui en ont besoin et les serveurs déclarés. Dans un modèle classique, RADIUS emploie généralement UDP/1812 et UDP/1813 ; TACACS+ historique emploie TCP/49. Les variantes TLS/DTLS utilisent leurs ports définis et dépendent de l’implémentation. Les ports exacts de l’environnement sont à confirmer dans les paramètres du serveur et de chaque client.

L’ACL ou le pare-feu devrait prendre en compte le sens du flux, l’adresse source observée sur le serveur, les réponses, la haute disponibilité, l’accounting et, le cas échéant, les messages d’autorisation dynamique. N’ouvre pas « tous les ports entre le réseau de gestion et le serveur AAA » simplement pour faire disparaître un timeout. Commence par un test précis et réduis la règle aux sources, destinations et services nécessaires.

### 2.12. Rotation des secrets et migration vers un transport protégé

Les secrets RADIUS ou TACACS+ partagés doivent être uniques autant que possible, suffisamment robustes, conservés dans un coffre et remplacés selon une procédure contrôlée. Une rotation réussie exige que le serveur et le client disposent de valeurs compatibles pendant la transition. Selon le produit, il est possible de créer temporairement un deuxième objet serveur ou un second profil ; dans d’autres cas, il faut une fenêtre de changement dédiée.

Procédure de rotation générique :

1. inventorier les clients, leurs adresses source et les serveurs concernés ;
2. vérifier si chaque client supporte plusieurs serveurs, clés ou certificats et quelle est la limite ;
3. générer un secret par client ou un certificat selon le mécanisme recommandé ;
4. mettre à jour les côtés selon un ordre compatible, en conservant une voie de récupération ;
5. vérifier l’authentification, l’autorisation et l’accounting sur chaque client ;
6. retirer les anciennes valeurs, mettre à jour le coffre et consigner la date ;
7. rechercher des erreurs de secret, des clients oubliés et des connexions qui utilisent encore l’ancien chemin.

Une migration vers TLS ne consiste pas simplement à changer un port. Elle implique les certificats, l’identité de chaque pair, la confiance de la CA, la version TLS requise, le port, le transport et la gestion du cas où le canal sécurisé échoue. Évite toute stratégie de repli silencieux vers un canal moins protégé.

### 2.13. Étude de cas : séparer supervision, exploitation et administration

Une entreprise possède quinze commutateurs, cinq routeurs et deux pare-feu administrés à distance. Trois équipes interviennent : supervision (N1), exploitation (N2) et ingénierie (N3). La supervision doit consulter les états et les compteurs, N2 peut appliquer des changements approuvés sur certains équipements et N3 détient les droits d’administration avancés. Tous les changements sont attribuables à une identité nominative.

**Conception proposée :** TACACS+ pour l’administration des équipements compatibles ; groupes d’identité séparés pour N1, N2 et N3 ; listes de méthodes nommées sur les accès SSH ; autorisation de commandes activée progressivement après étude du CLI ; accounting de session et de commandes lorsque la plateforme et le serveur le permettent ; logs exportés vers un collecteur protégé ; compte de secours limité et alerté.

**Tests d’acceptation :** N1 ouvre une session et peut exécuter les commandes d’observation approuvées mais ne peut pas modifier la configuration ; N2 effectue un changement prévu pendant la fenêtre et l’événement apparaît dans les journaux ; N3 peut réparer un service selon la politique ; un compte désactivé est rejeté ; un serveur secondaire fournit les mêmes décisions ; une panne contrôlée ne verrouille pas tous les accès ; le compte d’urgence fait l’objet d’une alerte et d’une revue.

**Critère de réussite :** ce n’est pas seulement « tous les utilisateurs peuvent se connecter ». Le système doit démontrer que chaque rôle peut accomplir son travail légitime et échoue lorsqu’il tente une action non autorisée, sans supprimer la capacité de récupération.

### 2.14. Exercices pratiques avec corrigés indicatifs

**Exercice 1 — authentification centrale qui échoue.** L’équipement tente de contacter le serveur, mais aucune demande n’apparaît dans ses journaux. Cite quatre vérifications dans l’ordre.

**Corrigé indicatif :** vérifier l’adresse et le port du serveur ; confirmer l’adresse source réellement utilisée et la route de retour ; examiner ACL/pare-feu et les compteurs ; vérifier le service d’écoute et les journaux du serveur. Si le serveur n’a reçu aucune demande, il est trop tôt pour changer les règles d’identité.

**Exercice 2 — rejet d’un compte connu.** Le compte fonctionne sur un équipement, mais est rejeté sur un autre.

**Corrigé indicatif :** comparer l’identité client/NAS, le groupe ou la politique sélectionnée, la source de la requête, la version ou le type de service, les attributs et les restrictions de groupe. Confirmer également que les équipements appliquent la même liste de méthodes et utilisent le même serveur logique. Ne présume pas que le seul mot de passe explique la différence.

**Exercice 3 — connexion autorisée mais privilège incorrect.** Le compte se connecte en mode utilisateur alors que son rôle doit accéder à l’EXEC privilégié.

**Corrigé indicatif :** inspecter la réponse d’autorisation, les attributs de privilège, l’autorisation EXEC appliquée, le profil du serveur et les capacités de l’équipement. Authentification et autorisation sont deux décisions différentes ; ne résous pas ce problème en donnant automatiquement le privilège 15 à tous les comptes.

**Exercice 4 — VLAN dynamique absent.** L’utilisateur est authentifié, mais son poste arrive dans le VLAN par défaut.

**Corrigé indicatif :** vérifier les attributs renvoyés, la cohérence du nom/numéro de VLAN, la configuration du port, les journaux du serveur et la prise en charge de la fonctionnalité par le commutateur. Puis vérifier si le VLAN et le DHCP sont disponibles. Distingue l’affectation du VLAN du fonctionnement IP après affectation.

**Exercice 5 — perte de serveur secondaire.** Le serveur principal tombe en panne et les connexions mettent 30 secondes à aboutir.

**Corrigé indicatif :** examiner le délai d’attente par tentative, le nombre de tentatives, l’ordre des serveurs et les intervalles de réessai. Mesurer la latence normale et vérifier la disponibilité applicative du secondaire. Ajuster après test, sans raccourcir aveuglément les délais au point de provoquer des basculements pendant une congestion.

**Exercice 6 — audit de commandes incomplet.** Les sessions s’ouvrent et se ferment dans les journaux, mais les modifications ne sont pas attribuables.

**Corrigé indicatif :** vérifier si l’accounting des commandes est pris en charge, activé et relié à la ligne ou à la liste correcte ; examiner la politique du serveur et la livraison vers le collecteur ; vérifier les identités nominatives, la synchronisation NTP et les journaux locaux en cas de perte du serveur.

### 2.15. Checklist de validation

- [ ] Accès console ou hors bande testé et disponible.
- [ ] Configuration initiale sauvegardée et procédure de retour arrière écrite.
- [ ] Accès SSH limité aux sources de gestion prévues.
- [ ] Serveur AAA déclaré avec la bonne adresse source et le bon secret/certificat.
- [ ] Authentification, autorisation et accounting testés séparément.
- [ ] Acceptation, refus explicite, timeout et erreur de secret testés.
- [ ] Compte local de secours testé et usage surveillé.
- [ ] Second serveur et basculement testés.
- [ ] Rôles et commandes interdits validés par des essais négatifs.
- [ ] Horloge, journaux et corrélation SIEM vérifiés.
- [ ] Flux réseau limités aux services nécessaires.
- [ ] Documentation, propriétaire de politique et date de revue consignés.

> **Astuce :** conserve une session d’administration valide pendant le déploiement et ouvre une deuxième session pour tester la nouvelle politique. Ne retire l’ancienne voie qu’après avoir confirmé les scénarios positifs et négatifs, la journalisation et le retour arrière. Pour les équipements critiques, exécute les changements par petits lots, pas simultanément sur tout le parc.

---

## 3. Dépannage et sécurité

### 3.1. Diagnostiquer à partir d’une hypothèse testable

Le dépannage AAA doit distinguer le symptôme de la cause. « SSH ne marche pas » ne précise pas si la connexion TCP échoue, si SSH refuse la clé ou la version, si le serveur demande des identifiants, si AAA rejette le compte ou si l’utilisateur ne reçoit pas l’autorisation attendue. Divise le problème en étapes, collecte les preuves et ne change qu’un élément à la fois.

Ordre de diagnostic recommandé :

1. vérifier que l’interface de gestion est active et que la route existe ;
2. vérifier que la connexion administrative atteint bien le service prévu ;
3. confirmer l’adresse source et les règles d’accès VTY ;
4. inspecter la liste AAA appliquée et le serveur/groupe choisi ;
5. observer si une requête arrive au serveur, puis la réponse exacte ;
6. vérifier identité, état du compte, groupe, certificat et politique ;
7. inspecter l’autorisation EXEC ou l’attribution de rôle ;
8. contrôler l’accounting, l’horloge, la livraison des logs et les alertes ;
9. comparer avec un équipement fonctionnel, sans copier aveuglément sa configuration.

### 3.2. Lire les symptômes sans tirer de conclusion trop tôt

| Symptôme | Hypothèses possibles | Première preuve à rechercher |
|---|---|---|
| Aucun journal côté serveur | Mauvaise adresse, route, filtrage, source inattendue, service arrêté | Compteurs/réseau et journaux système du serveur. |
| Requête reçue mais rejetée | Compte désactivé, secret utilisateur, groupe, règle ou méthode incorrecte | Motif de rejet et règle sélectionnée. |
| Timeout intermittent | Perte de paquets, surcharge, latence, serveur instable, filtrage d’un sens | Latence, compteurs, journaux des deux côtés. |
| Connexion réussie mais privilège faible | Attribut de rôle ou autorisation EXEC absente | Réponse du serveur et liste d’autorisation appliquée. |
| Commandes refusées en série | Politique de commande trop restrictive ou contexte mal interprété | Demande d’autorisation par commande et arguments reçus. |
| 802.1X en échec avant RADIUS | Supplicant, EAPOL, port, certificat côté terminal | Journaux client et authenticator. |
| EAP/TLS échoue | Date/CA/SAN du certificat, méthode incompatible, chaîne incomplète | Détails de validation TLS et de méthode EAP. |
| Accounting incomplet | Liste non appliquée, serveur indisponible, reboot, file saturée | Compteurs de comptabilisation et journaux. |
| VLAN attendu absent | Attribut invalide ou ignoré, VLAN manquant, configuration d’accès | Attribut d’acceptation et état de session. |
| Compte de secours accepté après un rejet | Liste ou comportement différent de la politique attendue | Test de refus explicite et documentation du produit. |

Les commandes de diagnostic très verbeuses peuvent divulguer des attributs sensibles et surcharger la console ou le serveur. Active le débogage sur une courte durée, de préférence dans un laboratoire ou une fenêtre maîtrisée, puis désactive-le et protège les sorties produites. Vérifie la possibilité de masquer les secrets avant de partager un extrait.

### 3.3. Erreurs de client AAA et d’adresse source

Un serveur AAA identifie souvent ses clients à partir d’une adresse, d’un secret, d’un certificat ou d’une combinaison de paramètres. Si le routeur envoie la requête avec l’adresse d’une interface inattendue, le serveur peut traiter le client comme inconnu ou appliquer la mauvaise politique. Le problème apparaît souvent après un changement de route, d’interface de sortie, de VRF, de NAT ou de configuration du loopback source.

**Procédure :** confirmer dans le journal serveur l’adresse source réelle ; comparer avec l’objet client déclaré ; vérifier les routes aller et retour ; vérifier l’interface/VRF de gestion et l’adresse source configurée dans le client ; examiner les ACL et le firewall. Si une adresse source est volontairement fixée, documente l’interface et assure-toi que le routage la rend joignable depuis tous les serveurs.

Ne corrige pas automatiquement le problème en ouvrant le serveur aux requêtes depuis n’importe quelle adresse. La déclaration des clients doit rester restrictive, car un accès à l’API/protocole AAA par un client non autorisé peut permettre des tentatives ou des décisions d’accès non désirées.

### 3.4. Secrets partagés, certificats et horloge

Un secret différent entraîne généralement un échec d’intégrité ou une demande ignorée/rejetée selon le protocole et l’implémentation. La réponse visible côté client peut se présenter comme un timeout, ce qui ne prouve pas que le serveur est hors ligne. Vérifie la cohérence de la valeur côté deux pairs sans afficher les secrets dans les journaux ou les conversations d’exploitation.

Pour les transports TLS, vérifie en plus :

- la validité temporelle du certificat et l’horloge ;
- la chaîne complète jusqu’à une autorité approuvée ;
- le nom attendu (SAN) ou l’identité de pair comparée au certificat ;
- l’usage des certificats client et serveur attendu par le produit ;
- les suites cryptographiques et versions TLS prises en charge ;
- la révocation et le renouvellement ;
- l’absence de retour automatique vers un canal moins sécurisé après échec TLS.

Une CA inaccessible, un certificat expiré ou une date incorrecte peut casser une authentification mutuelle même si le routage et le port sont corrects. La solution n’est pas de désactiver durablement la validation du certificat : corrige la chaîne, la confiance ou l’horloge et teste le scénario de rotation.

### 3.5. 802.1X : localiser la panne par étape

Dans 802.1X, l’authentification peut échouer avant que le serveur RADIUS ne voie la demande. Le terminal doit envoyer EAPOL, le commutateur doit activer le port et la méthode doit être compatible. Un client qui ne démarre pas le supplicant ne peut pas être réparé uniquement en modifiant RADIUS.

Pour un échec EAP-TLS, examine le certificat client, la chaîne, son usage, les dates de validité, la politique de révocation et l’identité serveur validée par le poste. Pour une méthode avec tunnel TLS et mot de passe, vérifie la configuration de confiance du certificat serveur et refuse les avertissements ignorés par réflexe. Le nom extérieur présenté dans un échange EAP ne prouve pas à lui seul l’identité réelle ; RFC 9190 rappelle notamment que l’identité présentée dans l’échange EAP initial n’est pas authentifiée par le mécanisme EAP-TLS.

Le contrôle d’accès par port doit également gérer les appareils qui ne prennent pas en charge 802.1X. S’il existe une méthode de secours, comme MAB, elle doit attribuer des droits limités, ne pas confondre adresse MAC et identité forte, et être contrôlée par des filtres ou VLAN adaptés. Les ports d’imprimantes, téléphones, bornes et appareils IoT nécessitent des profils de politique spécifiques.

### 3.6. Protéger les comptes privilégiés

Les comptes administratifs sont des cibles de grande valeur. Applique des identités nominatives, une authentification renforcée pour les accès sensibles, des rôles limités, une revue des droits et une procédure de départ. Les comptes partagés rendent l’attribution individuelle plus difficile et doivent être réservés aux cas réellement nécessaires, comme certaines opérations de secours.

Pour le compte de secours :

- conserver les identifiants dans un coffre approuvé et limiter l’accès au coffre ;
- accorder le minimum de droits permettant la récupération ;
- restreindre l’origine de connexion et garder la console/hors bande sous contrôle ;
- générer une alerte à chaque usage et exiger un motif de changement ;
- effectuer une revue après usage et révoquer/rotater le secret selon la procédure ;
- tester la procédure à intervalles définis et vérifier que le compte n’est pas verrouillé ou expiré.

N’utilise pas un compte d’urgence comme solution quotidienne lorsque le serveur central est simplement pénible à maintenir. Chaque usage doit être visible et analysé, car un compte local de privilège élevé contourne généralement les politiques centrales et peut échapper à certains mécanismes d’autorisation de commande.

### 3.7. Protéger la voie réseau AAA

Le trafic d’authentification doit rester dans un réseau de gestion restreint ou utiliser un transport protégé pris en charge. Limite les clients, les serveurs et les protocoles aux équipements nécessaires. Évite d’exposer les ports AAA vers Internet ou un réseau utilisateur non fiable. Les règles doivent inclure le trafic d’accounting, la redondance et les extensions dynamiques si elles sont nécessaires, mais ne doivent pas autoriser des flux trop larges par facilité de dépannage.

Privilégie des secrets uniques et robustes, une gestion centralisée et une rotation testée. Si un secret est partagé avec un outil de supervision, un dépôt de code ou une ancienne sauvegarde, traite-le comme compromis possible et planifie son remplacement. Les comptes clients AAA côté serveur doivent être enregistrés explicitement ; évite les modes qui acceptent indistinctement des clients inconnus.

Pour un déploiement RADIUS classique, examine l’opportunité de transports sécurisés lorsque les versions des équipements le supportent. Pour TACACS+, évalue les options de transport et les recommandations de la version du produit. Les documents IETF récents comme RFC 9887 (TACACS+ sur TLS 1.3) et RFC 9765 (profil RADIUS/1.1 expérimental) méritent d’être évalués avec prudence : un document technique ne garantit ni le support du constructeur ni l’interopérabilité dans un environnement donné.

### 3.8. Protection des journaux et conformité

Les journaux AAA peuvent contenir des noms d’utilisateur, des adresses IP, des noms d’équipements, des commandes administratives et des données permettant de reconstituer les actions d’un opérateur. Ils doivent être protégés contre l’altération et l’accès abusif, sans empêcher les équipes autorisées de les consulter lors d’un incident.

Définis une matrice d’accès aux journaux : qui peut lire, rechercher, exporter, gérer la rétention et administrer le système ? Sépare si possible les droits d’administration de la politique AAA de ceux qui permettent d’effacer les preuves d’activité. Alimente les outils de détection avec des événements pertinents : connexions échouées répétées, connexions privilégiées hors horaire, usage du compte de secours, échecs de validation de certificats, basculement inhabituel vers un serveur secondaire et interruption de l’accounting.

La conservation n’est pas « tout garder indéfiniment ». Fixe les durées selon les besoins d’audit, les règles internes et la réglementation applicable. Limite les données d’authentification à ce qui est nécessaire et ne stocke jamais le mot de passe en clair comme solution de dépannage.

### 3.9. Haute disponibilité et test de continuité

Une procédure de haute disponibilité doit préciser le comportement prévu en cas de panne complète, de perte d’un serveur, d’un réseau isolé, de certificat expiré ou de réplication retardée. La politique « fail open » accorde éventuellement un accès lorsque le service ne répond pas, tandis que « fail closed » refuse l’accès ; le choix dépend du scénario, de la criticité et du produit. Pour l’administration d’équipements, un compte local ou une console indépendante est généralement plus contrôlable qu’une ouverture générale automatique.

Les tests doivent être organisés et limités. Vérifie séparément le principal, le secondaire, la perte du réseau, la rotation de secret, le renouvellement de certificat et le retour du service. Observe la latence du client et la cohérence des rôles ; deux serveurs accessibles n’assurent pas une politique cohérente si leurs groupes ou règles divergent.

### 3.10. Réponse à un incident AAA

Si les connexions administratives montrent un comportement inattendu, conserve d’abord un accès valide. Ne redémarre pas tous les équipements et ne supprime pas immédiatement les comptes, car cela peut rendre la récupération plus difficile. Identifie le périmètre : un équipement, un site, un serveur ou l’ensemble des clients ; compare l’heure de début avec les changements récents ; collecte les journaux des deux côtés.

Séquence de réponse :

1. protéger l’accès qui fonctionne et suspendre les changements non essentiels ;
2. déterminer si le problème est disponibilité, refus de politique, transport, certificat ou autorisation ;
3. comparer les demandes envoyées et reçues, sans exposer les secrets ;
4. restaurer le service ou appliquer le retour arrière approuvé ;
5. confirmer acceptation, rejet, secours et accounting après correction ;
6. revoir les comptes privilégiés, les changements et les journaux potentiellement affectés ;
7. documenter la cause racine et mettre à jour les tests de régression.

Si des indicateurs suggèrent un secret compromis, ne le publie pas dans un canal d’incident ouvert. Restreins les clients concernés, remplace les secrets/certificats selon une séquence contrôlée, vérifie les connexions et recherche les accès suspects à partir d’une fenêtre de temps cohérente.

### 3.11. Mini-cas : authentification réussie, commande refusée

**Contexte.** Un opérateur peut ouvrir une session sur un routeur. La lecture des interfaces fonctionne mais la commande de configuration nécessaire à une modification approuvée est rejetée. Le mot de passe est correct et le serveur AAA répond.

**Hypothèse 1 :** le compte est membre du mauvais groupe. Vérifie la règle appliquée et les attributs de rôle renvoyés.

**Hypothèse 2 :** l’authentification est centrale mais l’autorisation des commandes est locale ou associée à une autre liste. Inspecte la configuration AAA effective, pas seulement la présence de lignes `aaa`.

**Hypothèse 3 :** la règle du serveur ne reconnaît pas la forme exacte de la commande ou de ses arguments. Compare la demande d’autorisation avec la règle, en protégeant les données sensibles.

**Hypothèse 4 :** la plateforme ne prend pas en charge la granularité attendue ou la commande passe par un mode d’autorisation différent. Consulte la documentation de la version.

La correction n’est pas nécessairement d’élever le compte au niveau maximal. Adapte le rôle ou l’exception la plus étroite, effectue les tests positifs et négatifs, puis vérifie l’apparition de l’événement d’accounting.

### 3.12. Mini-cas : le serveur refuse le certificat d’un terminal

**Contexte.** Des postes récemment renouvelés ne rejoignent plus le Wi-Fi d’entreprise via EAP-TLS. Les anciens postes continuent à fonctionner.

Vérifie la date de validité, la chaîne de CA, la présence du nom attendu et les usages de certificat. Les anciens postes peuvent conserver un certificat différent, une chaîne mise en cache ou un profil EAP qui n’a pas été actualisé. Examine aussi la révocation et la politique de sélection du certificat. Ne désactive pas la validation TLS comme correctif global : cela supprimerait une protection essentielle contre les faux serveurs.

Le déploiement de certificats doit être accompagné d’une gestion du cycle de vie : émission, renouvellement automatique lorsque possible, révocation, remplacement de CA et suivi des appareils qui n’ont pas reçu leur nouveau profil. Des tests sur plusieurs systèmes clients sont nécessaires avant de remplacer la chaîne de confiance à grande échelle.

### 3.13. Audit périodique et indicateurs utiles

Les indicateurs AAA doivent servir à mesurer la qualité du contrôle d’accès, pas seulement à produire des graphiques. Quelques métriques utiles :

- taux de succès et de rejet par service et par site, avec la prudence nécessaire pour distinguer une erreur utilisateur d’une attaque ;
- taux de timeout et latence par serveur ;
- disponibilité et taux d’utilisation du serveur secondaire ;
- proportion des équipements utilisant encore un transport historique non chiffré ;
- comptes inactifs, comptes partagés et comptes privilégiés non revus ;
- nombre d’échecs ou d’alertes liés au compte de secours ;
- interruptions de l’accounting et événements difficiles à corréler ;
- certificats proches de l’expiration et échecs de validation ;
- différences de politiques entre serveurs redondants ;
- délais de révocation après un départ ou un changement de rôle.

Une hausse des refus peut signaler une attaque, mais aussi un changement de configuration ou l’expiration d’un certificat. Les alertes doivent donc inclure du contexte et des runbooks. Les métriques doivent être vérifiées contre les journaux bruts pour éviter qu’un tableau de bord masque une perte de données.

### 3.14. Procédure de changement recommandée

Avant le changement : documente l’objectif, le périmètre, les prérequis, les dépendances, les risques, l’accès de secours, les tests, le responsable et la fenêtre. Prépare la configuration candidate et vérifie la syntaxe dans un environnement de test. Assure-toi que les administrateurs concernés savent quelle commande ou quel rôle doit être disponible après le changement.

Pendant : applique le changement sur un petit lot, conserve une session existante, observe les requêtes AAA et teste les connexions depuis un second terminal. Vérifie une identité de chaque rôle, une identité rejetée, l’accounting et le serveur secondaire. Si un test obligatoire échoue, arrête le déploiement et déclenche le retour arrière prévu plutôt que d’ajouter des exceptions improvisées.

Après : valide la cohérence des journaux, la source d’autorité, les sauvegardes, la liste des exceptions et le retrait des anciennes configurations. Mets à jour la documentation et les alertes. Planifie un contrôle différé pour confirmer que le serveur secondaire, la révocation et le compte de secours restent fonctionnels.

> **Danger :** n’applique pas une nouvelle politique AAA simultanément à l’ensemble d’un parc distant sans moyen de récupération indépendant. Une politique correcte sur le serveur peut devenir inaccessible à cause d’un défaut de routage, d’un secret divergent ou d’une autorisation trop stricte. Le plan de secours fait partie du changement et doit être testé avant la bascule.

---

## Points à retenir

1. AAA regroupe trois fonctions distinctes : authentifier, autoriser et enregistrer. Les trois doivent être testées séparément.
2. RADIUS est très courant pour 802.1X, le Wi-Fi, le NAC et certains VPN ; TACACS+ est souvent employé pour administrer les équipements réseau.
3. Une liste de méthodes doit être appliquée au bon service ou à la bonne ligne. Une liste présente dans la configuration n’est pas nécessairement utilisée.
4. Un refus explicite et un timeout ne sont pas équivalents. Le mécanisme de secours doit respecter cette distinction et être testé.
5. Les rôles et l’autorisation EXEC/commande réduisent le risque qu’un compte authentifié puisse tout modifier.
6. Les journaux d’accounting sont plus utiles quand les identités sont nominatives, les horloges synchronisées et les événements centralisés et protégés.
7. 802.1X, EAP et RADIUS sont des éléments différents d’une architecture d’accès réseau ; un échec peut se produire avant que RADIUS reçoive une demande.
8. Les attributs RADIUS tels que le VLAN dynamique doivent être reconnus par le client et testés du serveur jusqu’à la connectivité IP finale.
9. Les secrets, certificats, groupes, clients déclarés et règles du serveur doivent rester cohérents et faire l’objet d’une rotation contrôlée.
10. Une haute disponibilité dépend de la cohérence des politiques, des délais et du routage, pas simplement de deux adresses de serveur.
11. Le transport historique RADIUS/TACACS+ ne doit pas être supposé équivalent à un transport TLS moderne. Vérifie les recommandations et la prise en charge réelle du produit.
12. Le compte de secours, la console ou la gestion hors bande, le retour arrière et les tests négatifs sont des exigences opérationnelles, pas des détails optionnels.

### Références techniques

- Cisco, *RADIUS Configuration Guide, Cisco IOS XE* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/sec-crypto/radius/radius-configuration-guide/radius.html
- Cisco, *TACACS+ Configuration Guide / AAA* : https://www.cisco.com/c/en/us/support/security/identity-services-engine/series.html (consulter également le guide correspondant à la plateforme IOS/IOS XE utilisée).
- RFC 2865, *Remote Authentication Dial In User Service (RADIUS)* : https://www.rfc-editor.org/rfc/rfc2865.html
- RFC 2866, *RADIUS Accounting* : https://www.rfc-editor.org/rfc/rfc2866.html
- RFC 3580, *IEEE 802.1X Remote Authentication Dial In User Service (RADIUS) Usage Guidelines* : https://www.rfc-editor.org/rfc/rfc3580.html
- RFC 5176, *Dynamic Authorization Extensions to RADIUS* : https://www.rfc-editor.org/rfc/rfc5176.html
- RFC 8907, *The Terminal Access Controller Access-Control System Plus (TACACS+) Protocol* : https://www.rfc-editor.org/rfc/rfc8907.html
- RFC 9887, *TACACS+ over TLS 1.3* (décembre 2025) : https://www.rfc-editor.org/rfc/rfc9887.html
- RFC 6614, *Transport Layer Security (TLS) Encryption for RADIUS* : https://www.rfc-editor.org/rfc/rfc6614.html
- RFC 7360, *DTLS as a Transport Layer for RADIUS* : https://www.rfc-editor.org/rfc/rfc7360.html
- RFC 9765, *RADIUS/1.1: Leveraging ALPN to Remove MD5* (spécification expérimentale) : https://www.rfc-editor.org/rfc/rfc9765.html
- RFC 9190, *EAP-TLS 1.3* : https://www.rfc-editor.org/rfc/rfc9190.html
- NIST SP 800-63B, *Digital Identity Guidelines: Authentication and Lifecycle Management* : https://pages.nist.gov/800-63-3/sp800-63b.html
- NIST SP 800-53, *Security and Privacy Controls for Information Systems and Organizations* : https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
