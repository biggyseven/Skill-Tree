# Authentification réseau (AAA) - Débutant

**Niveau :** DÉBUTANT

L’authentification réseau consiste à vérifier l’identité d’une personne, d’un équipement ou d’un service avant de lui accorder l’accès à une ressource. Dans une petite installation, un administrateur peut se connecter à un routeur avec un compte local. Dans une entreprise, plusieurs dizaines de commutateurs, routeurs, contrôleurs Wi-Fi, VPN et pare-feu doivent appliquer des règles cohérentes. Il devient alors utile de centraliser les identités, les autorisations et les traces d’activité.

Le modèle **AAA** signifie **Authentication, Authorization, Accounting**, soit **authentification, autorisation et traçabilité/comptabilisation**. Ces trois fonctions répondent à trois questions différentes : qui es-tu ? Que peux-tu faire ? Que s’est-il passé pendant ta session ? AAA est un modèle de contrôle d’accès, et non le nom d’un unique logiciel ou protocole. Des mécanismes tels que RADIUS, TACACS+, une base locale, un annuaire d’entreprise ou des méthodes EAP peuvent participer à son fonctionnement.

Dans ce cours, nous allons nous concentrer sur les bases utiles pour comprendre et sécuriser l’accès administratif aux équipements réseau, puis découvrir l’authentification des utilisateurs sur un réseau filaire ou Wi-Fi. Les exemples utilisent principalement la syntaxe de Cisco IOS/IOS XE et des adresses réservées à la documentation. Ils doivent être adaptés au matériel, à la version logicielle et au serveur AAA disponibles dans un laboratoire.

> **Analogie** : imagine un immeuble sécurisé. L’authentification correspond au contrôle de ton identité à l’entrée. L’autorisation correspond aux portes que ton badge permet d’ouvrir. L’accounting correspond au registre des entrées, sorties et actions importantes. Une seule de ces fonctions ne remplace pas les deux autres : vérifier ton identité ne signifie pas que tu peux accéder à toutes les pièces, et un registre ne décide pas à lui seul qui a le droit d’entrer.


## 1. La théorie et les algorithmes

### 1.1. Comprendre le modèle AAA

AAA est une architecture logique courante dans les réseaux. Ses trois lettres désignent des décisions et des fonctions distinctes, même si un même serveur peut les traiter toutes.

| Fonction | Question | Exemple réseau | Résultat attendu |
|---|---|---|---|
| Authentication (authentification) | Qui se connecte ? | Un technicien saisit son identifiant et son mot de passe SSH. | Identité acceptée ou rejetée. |
| Authorization (autorisation) | Que peut faire cette identité ? | Le technicien peut consulter l’état des interfaces, mais pas modifier le routage. | Privilèges, rôle, VLAN ou services permis. |
| Accounting (traçabilité/comptabilisation) | Que s’est-il passé ? | Le début et la fin d’une session sont enregistrés. | Journaux permettant audit et investigation. |

Les trois fonctions peuvent être activées séparément selon les possibilités de l’équipement. Un appareil peut authentifier les connexions sans enregistrer les sessions. Il peut aussi produire des journaux de connexion alors que l’autorisation des commandes demeure trop large. Une conception correcte vérifie donc chaque fonction au lieu de considérer « AAA activé » comme une garantie complète de sécurité.

**Authentification.** Le système compare une preuve présentée par l’utilisateur à une méthode connue. La preuve peut être un secret, un certificat, un code temporaire, une clé cryptographique ou une combinaison de facteurs. Un simple nom d’utilisateur n’est pas une preuve suffisante : il identifie le compte revendiqué, mais n’établit pas que la personne qui l’utilise est légitime.

**Autorisation.** Après l’authentification, une politique détermine les droits accordés. Elle peut s’appuyer sur le groupe de l’utilisateur, son rôle professionnel, le type d’équipement, le lieu de connexion, l’heure, la posture du terminal ou d’autres attributs. Dans un laboratoire débutant, cette autorisation peut se résumer au niveau de privilège CLI. Dans un réseau d’entreprise, elle peut décider du VLAN, d’une liste de contrôle, d’une durée de session ou d’un accès à un service précis.

**Accounting.** Le système enregistre des événements tels que le démarrage ou la fin d’une session, la durée de connexion, le point d’accès utilisé, des volumes de trafic ou les commandes administratives prises en charge par la plate-forme. Les détails exacts dépendent du protocole, du serveur et de l’équipement. Accounting ne veut pas dire espionner sans limite : les données collectées doivent être pertinentes, protégées, accessibles aux personnes autorisées et conservées pendant une durée définie.

### 1.2. Les acteurs d’une architecture AAA

Une architecture AAA courante comporte plusieurs rôles. Ils peuvent être réunis dans un seul appareil de laboratoire, mais ils sont souvent séparés dans une entreprise.

- **Utilisateur ou terminal (supplicant dans 802.1X)** : demande l’accès et présente des éléments d’authentification.
- **Équipement d’accès ou client AAA** : routeur, commutateur, contrôleur Wi-Fi, concentrateur VPN ou pare-feu. Il collecte la demande et communique avec le serveur AAA.
- **Serveur AAA** : reçoit la demande, vérifie l’identité via sa base ou un système externe, applique les règles d’autorisation et enregistre les événements.
- **Annuaire ou fournisseur d’identité** : source de comptes, de groupes ou de certificats, par exemple un annuaire d’entreprise.
- **Système de journalisation/SIEM** : centralise et corrèle les événements pour aider à détecter les comportements anormaux.

Le client AAA et le serveur AAA ne sont pas le même élément. Un commutateur peut être client RADIUS tout en servant de passerelle entre le terminal et le serveur d’authentification. Le terminal ne parle pas nécessairement directement au serveur : en 802.1X, il échange notamment des messages EAPOL avec le commutateur, puis le commutateur encapsule les échanges EAP dans des messages RADIUS vers le serveur.

```text
                    PLAN DE CONTRÔLE AAA

  Administrateur / poste
          |
          | SSH ou 802.1X
          v
  +---------------------+
  | Routeur / Switch /  |       messages RADIUS ou TACACS+
  | contrôleur Wi-Fi    | ----------------------------------+
  | client AAA          |                                  |
  +---------------------+                                  v
                                                 +--------------------+
                                                 | Serveur AAA        |
                                                 | identité / règles  |
                                                 +--------------------+
                                                   |              |
                                                   v              v
                                             Annuaire /       Journaux /
                                             identité         SIEM
```

### 1.3. Où rencontre-t-on AAA ?

Il faut distinguer plusieurs usages, car les mêmes acronymes recouvrent des scénarios différents.

**Administration des équipements.** Un administrateur ouvre une session SSH sur un routeur ou un commutateur. Le système vérifie son identité, peut autoriser l’accès au mode privilégié ou à certaines commandes, puis enregistre la session. Pour ce scénario, RADIUS et surtout TACACS+ sont courants dans les infrastructures d’entreprise. Une base locale reste utile comme mécanisme de secours maîtrisé.

**Contrôle d’accès au réseau (NAC).** Un ordinateur ou un téléphone tente de rejoindre un réseau filaire ou Wi-Fi. L’authentification peut déterminer si le terminal obtient l’accès, quel VLAN lui est attribué, quelles politiques s’appliquent et éventuellement quand réévaluer sa session. 802.1X est une famille de mécanismes couramment utilisée pour ce contrôle.

**Accès distant ou VPN.** Une passerelle VPN valide l’identité d’un utilisateur ou d’un appareil, peut exiger plusieurs facteurs et attribue des ressources accessibles. AAA peut être relié à un annuaire et à un service MFA. Il faut protéger les comptes privilégiés et éviter qu’un simple compte utilisateur permette d’atteindre le réseau entier.

**Réseaux Wi-Fi d’entreprise.** Le point d’accès ou le contrôleur utilise souvent RADIUS pour transmettre les décisions d’authentification et récupérer des attributs, par exemple un VLAN ou une politique. L’authentification du serveur par certificat est essentielle avec les méthodes EAP qui s’appuient sur TLS ; accepter aveuglément tout certificat peut exposer les identifiants.

### 1.4. Base locale et authentification centralisée

Une base locale stocke les comptes directement sur l’équipement. Elle est simple à installer et ne nécessite pas de serveur externe disponible au moment de la connexion. En revanche, chaque équipement a sa propre base, les modifications doivent être répétées et la révocation d’un compte peut être oubliée sur certains appareils.

Une solution centralisée conserve les identités et les politiques dans un service commun. Elle facilite la création et la révocation des comptes, la séparation des rôles et l’audit. Mais elle dépend de la connectivité, du DNS, de l’heure, du serveur, des secrets partagés ou certificats, et des règles de pare-feu. Il faut donc prévoir la disponibilité et un mécanisme de secours adapté au risque.

| Critère | Base locale | Serveur AAA centralisé |
|---|---|---|
| Mise en place initiale | Généralement simple. | Demande un serveur et une intégration. |
| Gestion de nombreux équipements | Répétitive. | Centralisée et plus cohérente. |
| Fonctionnement si le serveur est inaccessible | Peut rester disponible localement. | Dépend de la politique de secours configurée. |
| Révocation d’un compte | À appliquer sur chaque équipement. | Généralement centralisée, sous réserve de propagation. |
| Granularité des politiques | Variable et souvent limitée. | Peut intégrer groupes, attributs et facteurs supplémentaires. |
| Risque principal | Comptes oubliés et politiques divergentes. | Dépendance au service central et erreurs de politique à grande échelle. |

Le choix n’est pas « local ou centralisé pour toujours ». Un design fréquent associe l’AAA centralisé à un compte d’urgence local, fortement protégé et surveillé. Ce compte de secours ne doit pas devenir le moyen quotidien de contourner les contrôles centraux.

### 1.5. Les protocoles : RADIUS et TACACS+

**RADIUS** signifie *Remote Authentication Dial-In User Service*. Il est largement utilisé pour l’accès réseau, notamment 802.1X, Wi-Fi d’entreprise, VPN et authentification de certains accès administratifs. Dans son modèle classique, il utilise UDP, généralement le port 1812 pour l’authentification et le port 1813 pour l’accounting. Les implémentations peuvent proposer d’autres transports ou ports selon la plateforme et les options configurées.

RADIUS échange des paquets formés d’attributs. Une demande d’accès peut contenir le nom de l’utilisateur, l’identifiant du NAS, le type de port ou des informations de méthode d’authentification. Une réponse peut accepter, rejeter ou demander un nouvel échange. Pour l’accès réseau, les attributs peuvent porter des informations d’autorisation telles qu’un VLAN ou une politique, à condition que les deux côtés comprennent leur signification.

RADIUS classique ne chiffre pas indistinctement tout le paquet. Historiquement, le champ de mot de passe utilisateur utilise un mécanisme spécifique de masquage, mais cela ne doit pas être interprété comme un chiffrement moderne et complet de tout le trafic AAA. Il faut isoler les échanges sur un réseau de confiance, restreindre les sources et destinations, protéger les secrets et préférer les modes sécurisés comme RADIUS sur TLS lorsque la plateforme les prend correctement en charge. Le secret partagé sert à identifier la relation entre client et serveur ; il ne doit jamais être faible, réutilisé partout ou placé dans un document accessible.

**TACACS+** est particulièrement répandu pour l’administration des équipements réseau. Il permet de séparer les échanges d’authentification, d’autorisation et d’accounting et facilite, selon la plateforme, un contrôle détaillé des commandes CLI. Le port TCP historiquement utilisé est 49. Le protocole est documenté par le RFC 8907, qui décrit un protocole déployé mais ne le classe pas comme standard IETF de la même manière qu’un standard sur la voie normative.

| Point de comparaison | RADIUS | TACACS+ |
|---|---|---|
| Usages courants | Accès réseau, Wi-Fi, VPN, 802.1X. | Administration des routeurs, commutateurs et appareils réseau. |
| Transport classique | UDP 1812/1813. | TCP 49. |
| Échanges | Authentification et attributs d’autorisation ; accounting selon service. | Authentification, autorisation et accounting conçus comme services distincts. |
| Autorisation de commandes CLI | Dépend de la plateforme et des attributs pris en charge. | Souvent mieux adapté au contrôle détaillé des commandes d’administration. |
| Confidentialité du transport | Le RADIUS classique ne chiffre pas tout le paquet ; options TLS/DTLS possibles selon déploiement. | Obfuscation historique du corps, qui ne doit pas être assimilée automatiquement à un chiffrement moderne global ; protéger le transport et suivre les recommandations actuelles. |
| Décision de conception | Choisir selon le cas d’usage et les capacités certifiées de la solution. | Même principe : vérifier interopérabilité, sécurité et capacité d’audit. |

### 1.6. Déroulement d’une authentification RADIUS

Le client AAA envoie une demande au serveur avec les informations nécessaires. Le serveur traite la demande selon ses règles et renvoie une décision. Le résultat réel dépend aussi de la réaction du client : une réponse positive peut ne pas suffire si un attribut d’autorisation obligatoire est absent ou incompatible.

```text
Équipement client AAA                         Serveur RADIUS
        |                                             |
        | -------- Access-Request ------------------> |
        |                                             | vérifie identité,
        |                                             | règles et contexte
        | <------- Access-Challenge ----------------- | (si échange requis)
        | -------- nouvelle réponse / demande ------> |
        |                                             |
        | <------- Access-Accept ou Reject ---------- |
        |                                             |
        | ------ Accounting-Start (si configuré) ---> |
        | <----- Accounting-Response --------------- |
        |                                             |
        |      session active puis terminée           |
        | ------ Accounting-Stop -------------------> |
```

Les messages courants du cycle d’accès sont :

- **Access-Request** : demande d’authentification ou d’accès ; le nom exact et les attributs transmis varient selon le mécanisme.
- **Access-Accept** : le serveur accepte l’accès et peut joindre des attributs d’autorisation.
- **Access-Reject** : le serveur refuse l’accès.
- **Access-Challenge** : le serveur demande une étape supplémentaire, par exemple dans un échange interactif ou EAP.
- **Accounting-Request / Accounting-Response** : échange de traces de session selon le service, notamment démarrage, mises à jour éventuelles et arrêt.

Un **rejet** et une **absence de réponse** ne sont pas équivalents. Un rejet indique que le serveur a reçu et traité la demande puis refusé l’accès. Un délai dépassé peut indiquer un problème réseau, une règle de pare-feu, un secret partagé incorrect, une mauvaise adresse source ou un serveur indisponible. Le comportement de secours doit distinguer autant que possible ces situations.

### 1.7. Autorisation : le principe du moindre privilège

Une fois la personne authentifiée, son compte ne doit recevoir que les droits utiles à sa mission. C’est le principe du **moindre privilège**. Un technicien de support qui consulte l’état des ports n’a pas nécessairement besoin de modifier une route par défaut ou de supprimer les journaux. Un administrateur réseau peut avoir des droits étendus, mais ceux-ci doivent être nominatifs, limités et enregistrés.

Les modèles simples utilisent des niveaux de privilège ou des rôles prédéfinis. Les modèles plus avancés appliquent un contrôle basé sur les rôles (RBAC) ou sur des attributs contextuels (ABAC). Un rôle peut correspondre à « lecture seule », « exploitation », « sécurité » ou « administration complète ». L’autorisation doit être appliquée côté équipement ou service, pas seulement affichée dans une interface graphique.

Une authentification réussie ne doit pas être interprétée comme une autorisation totale. De même, l’appartenance à un groupe d’annuaire n’est pertinente que si une règle la mappe explicitement à un rôle. Il faut éviter d’utiliser un groupe trop large, mal nommé ou hérité par accident.

### 1.8. Accounting, journaux et audit

L’accounting fournit une trace structurée des sessions et de certaines actions. Selon le type de client et de service, on peut enregistrer le nom de compte, le point d’accès, l’adresse réseau, l’heure, la durée, le résultat ou des commandes exécutées. Les journaux AAA complètent les logs système, les journaux du serveur d’identité et les informations de pare-feu ; ils ne les remplacent pas.

Un journal utile doit permettre de répondre à des questions concrètes : quel compte s’est connecté ? Sur quel équipement ? Quand ? La connexion a-t-elle réussi ? Quel privilège a été attribué ? L’équipement a-t-il reçu une commande de déconnexion ou de fin de session ? Si l’horloge de l’équipement diffère de plusieurs minutes, la corrélation devient difficile. NTP, fuseau horaire clair, horodatage et centralisation sont donc des prérequis opérationnels importants.

L’accounting peut manquer un événement lorsque le réseau ou le serveur est indisponible. Il ne faut pas supposer que tous les journaux sont garantis ou parfaitement synchronisés. Pour des opérations sensibles, combinez les traces AAA avec les journaux système et les systèmes de surveillance, et documentez les limites de rétention ou de perte possible.

Les journaux doivent être protégés en transit et au repos, avec des droits de lecture limités. Ils ne devraient pas exposer de secrets, de mots de passe en clair ou de données personnelles superflues. Définissez les durées de conservation selon les exigences métier et légales applicables.

### 1.9. Accès administratif local, distant et comptes de secours

Avant de mettre en place AAA centralisé, il faut comprendre comment l’équipement accepte déjà les connexions. Le modèle peut inclure une base locale, des mots de passe de ligne historiques ou une méthode d’authentification centralisée. Une migration mal planifiée peut désactiver l’accès ou laisser un chemin administratif plus faible que prévu.

Un compte local de secours est utile si le serveur AAA est en panne ou si la liaison vers lui est coupée. Ce compte doit avoir un mot de passe robuste, être limité aux personnes autorisées, être conservé de manière sûre et son usage doit générer une alerte. Lorsque cela est possible, utilisez une procédure de coffre-fort de secrets, une rotation après usage et des essais réguliers de la procédure de secours.

Ne laissez pas Telnet activer une administration distante non chiffrée. Préférez SSHv2, désactivez les services de gestion inutiles et limitez les connexions aux réseaux d’administration. La commande de configuration d’un serveur AAA ne remplace pas la sécurisation de chaque service administratif, par exemple HTTP/HTTPS, console, ligne VTY ou API de gestion.

### 1.10. Ordre des méthodes et différence entre échec et indisponibilité

Sur de nombreux équipements, les listes de méthodes AAA permettent de spécifier un serveur central puis une base locale. L’idée est de continuer vers la méthode suivante lorsque la précédente **ne répond pas** ou ne peut pas être utilisée, selon les règles exactes de la plateforme. En revanche, si le serveur répond explicitement par un rejet, l’équipement ne doit généralement pas contourner la décision en essayant le compte local. Cette distinction empêche un utilisateur rejeté par la politique centrale de se connecter avec un compte local différent pour contourner la règle.

La syntaxe de la liste et les conditions de repli varient selon le système. Il faut lire la documentation correspondant à la version exacte et tester les scénarios de refus et d’indisponibilité séparément. Une mauvaise hypothèse sur le fallback est une source fréquente de défaut de sécurité.

```text
                    Demande de connexion
                            |
                            v
                    Serveur AAA central
                       /          \
             répond et accepte   ne répond pas
                    |                |
                    v                v
              accès selon       méthode de secours
                politique        (si configurée)
                    |
             répond et rejette
                    |
                    v
               accès refusé
```

La politique « fail-open » accorde un accès lorsqu’un système de décision ne peut pas être joint ; « fail-closed » refuse par défaut. Aucune option n’est universellement correcte. Une porte réseau invitée et un accès d’administration privilégié n’ont pas le même risque. La règle doit être décidée par zone, type de service et niveau de privilège, puis documentée et testée.

### 1.11. Accès réseau avec 802.1X

IEEE 802.1X définit un contrôle d’accès au réseau basé sur le port. Les rôles usuels sont :

- **Supplicant** : logiciel sur le terminal qui demande l’accès et participe à l’authentification.
- **Authenticator** : commutateur ou point d’accès qui contrôle le port et relaie des échanges.
- **Serveur d’authentification** : généralement un service RADIUS qui vérifie la méthode présentée et retourne la décision.

Sur un port filaire, le commutateur peut autoriser uniquement les échanges nécessaires à l’authentification tant que la session n’est pas établie. Après acceptation, il applique une politique au port ou à la session. Les détails peuvent inclure un VLAN, une ACL téléchargeable ou des attributs spécifiques à la solution. La possibilité, la syntaxe et l’ordre d’application de ces politiques dépendent du constructeur et de la version.

Sur le Wi-Fi d’entreprise, les échanges EAP sont souvent transportés vers RADIUS. Le point important pour le débutant est que 802.1X n’est pas, à lui seul, une méthode de chiffrement Wi-Fi : il fournit une structure d’authentification et de contrôle d’accès intégrée à une architecture de sécurité plus large.

### 1.12. EAP et certificats : première vue

EAP (*Extensible Authentication Protocol*) est un cadre qui permet différents mécanismes d’authentification. Certains s’appuient sur des identifiants et secrets ; d’autres reposent sur TLS et des certificats. EAP-TLS est une méthode basée sur des certificats côté client et serveur, lorsqu’elle est mise en œuvre avec les chaînes de confiance et contrôles attendus.

Les certificats reposent sur une PKI : autorité de certification, certificat, clé privée, date de validité et noms d’identité. Le terminal doit vérifier qu’il parle au serveur prévu, que le certificat est valide, que son nom correspond aux attentes et que la chaîne remonte à une autorité de confiance. Ignorer les avertissements ou accepter n’importe quel certificat peut autoriser un faux serveur à collecter des identifiants.

Les mots de passe restent sensibles au phishing et au partage. Les certificats déplacent une partie de la confiance vers les clés et la gestion du cycle de vie. Ils exigent une procédure de déploiement, renouvellement et révocation, mais peuvent fortement améliorer l’authentification de terminaux administrés.

### 1.13. MFA, facteurs et identité

L’authentification multifacteur (MFA) combine des facteurs de catégories différentes : quelque chose que l’utilisateur connaît, possède ou est. Deux mots de passe ne représentent pas deux facteurs indépendants. Un mot de passe et une clé matérielle peuvent constituer des facteurs différents selon la méthode utilisée. Le choix dépend du niveau de risque, du matériel, de l’accès hors ligne et des procédures de récupération.

Il est particulièrement important d’ajouter des contrôles renforcés aux accès administratifs, VPN et comptes capables de changer des règles de pare-feu, d’attribuer des droits ou de désactiver les journaux. Mais MFA ne corrige pas à elle seule une mauvaise autorisation. Un utilisateur fortement authentifié ne doit toujours recevoir que les permissions nécessaires.

### 1.14. Modèle de décision : de la demande à la session

Une architecture de contrôle d’accès peut être décrite par une séquence logique. Les implémentations réelles diffèrent, mais le modèle facilite le dépannage.

```text
1. Le client demande l'accès
           |
           v
2. Le dispositif identifie le type de service
   (SSH, VPN, 802.1X, administration Web...)
           |
           v
3. Une liste de méthodes AAA est sélectionnée
           |
           v
4. Une preuve d'identité est évaluée
           |
           +---- refus / preuve invalide ---> session refusée
           |
           v
5. Une politique d'autorisation est évaluée
           |
           +---- droits insuffisants -------> action refusée
           |
           v
6. Session ou service autorisé
           |
           v
7. Accounting et journaux sont transmis
           |
           v
8. Fin de session, révocation ou expiration
```

Une panne à chaque étape entraîne un symptôme différent. Un problème de transport entre équipement et serveur peut produire un délai dépassé. Un identifiant invalide peut générer un rejet. Un utilisateur authentifié mais non autorisé peut ouvrir une session limitée ou échouer à obtenir un service. Une panne d’accounting peut ne pas empêcher la connexion, mais compromettre l’audit selon la politique configurée.

### 1.15. Termes à connaître

| Terme | Définition simple | Exemple d’utilisation |
|---|---|---|
| AAA | Modèle d’authentification, d’autorisation et de traçabilité. | Contrôle d’un accès SSH et journalisation. |
| NAS | Équipement qui fournit un service d’accès au réseau ; dans RADIUS, client qui transmet une demande. | Commutateur ou concentrateur VPN. |
| RADIUS | Protocole AAA fréquent pour accès réseau. | Wi-Fi d’entreprise avec 802.1X. |
| TACACS+ | Protocole fréquent pour administrer les équipements réseau. | Contrôle des commandes d’un routeur. |
| Secret partagé | Valeur connue du client AAA et du serveur pour protéger/identifier leur relation selon le protocole. | Secret RADIUS unique entre un commutateur et le serveur. |
| EAP | Cadre d’authentification extensible. | Transport de l’authentification dans 802.1X. |
| 802.1X | Contrôle d’accès au réseau basé sur le port. | Autoriser un poste professionnel sur un port de commutateur. |
| MFA | Authentification utilisant plusieurs facteurs distincts. | Mot de passe plus clé de sécurité. |
| RBAC | Contrôle d’accès fondé sur les rôles. | Rôle « lecture seule » pour l’exploitation. |
| SIEM | Plateforme qui centralise et corrèle des journaux de sécurité. | Détecter des échecs répétés sur plusieurs équipements. |
| Fail-open | Autoriser dans certaines conditions de panne. | Peut être envisagé pour un service de faible sensibilité après analyse. |
| Fail-closed | Refuser lorsqu’une décision fiable ne peut pas être obtenue. | Souvent pertinent pour des ressources sensibles. |

### 1.16. Erreurs conceptuelles fréquentes

**Confondre authentification et autorisation.** Une identité peut être valide sans avoir le droit d’exécuter toutes les actions. Il faut une politique explicite pour passer de l’identité aux privilèges.

**Croire que RADIUS chiffre tout.** Le protocole RADIUS classique n’est pas un tunnel de chiffrement global. Les échanges doivent être protégés selon l’architecture retenue et les possibilités de la solution.

**Utiliser le même secret partagé partout.** Si un équipement est compromis, un secret réutilisé augmente l’impact. Définissez des secrets robustes et distincts par relation client-serveur lorsque la solution le permet, puis organisez leur rotation.

**Activer AAA sans tester le secours.** Un changement peut interrompre les connexions futures, même si la session d’administration actuelle demeure ouverte. Conservez une session de secours, vérifiez la méthode locale de récupération et faites un essai contrôlé.

**Laisser les accès distants sur Telnet.** Telnet n’assure pas la confidentialité du terminal comme SSH. Sur un réseau non fiable, les informations de connexion peuvent être exposées.

**Donner le privilège maximal à tous.** Un utilisateur ne doit pas recevoir de droits étendus par commodité si sa mission n’en a pas besoin.

**Croire qu’un journal suffit.** Les événements doivent être horodatés, protégés, centralisés et corrélés. Une trace locale effacée ou perdue ne fournit pas un audit fiable.

**Confondre un rejet avec une panne serveur.** Le premier est une décision de politique, le second un problème de disponibilité ou de communication. La méthode de secours doit éviter de contourner un rejet explicite.

> **Piège :** une liste AAA configurée avec un serveur central et une base locale n’implique pas que l’équipement essayera toujours la base locale après un rejet. Sur beaucoup de systèmes, le repli concerne plutôt l’absence de réponse du serveur. Vérifie ce comportement sur la version exacte, puis teste une authentification acceptée, un rejet explicite et une indisponibilité distincts.


## 2. Configuration et pratique

### 2.1. Objectif du laboratoire

L’objectif est de protéger l’accès administratif à un routeur Cisco IOS/IOS XE grâce à SSH et AAA, en commençant par une base locale de secours. Dans une deuxième étape, on ajoute un serveur RADIUS conceptuel et on prépare les éléments nécessaires pour le tester. Cette progression évite de dépendre d’un serveur qui n’a pas encore été validé.

Le laboratoire emploie des adresses de documentation : elles ne doivent pas être utilisées telles quelles sur un réseau de production. Adapte l’adressage, les noms, les méthodes d’authentification et les commandes à ta plateforme. Certaines options varient entre IOS, IOS XE, les commutateurs Catalyst, les routeurs ISR et les produits d’autres constructeurs.

### 2.2. Topologie

```text
             PC d'administration
             192.0.2.50/24
                    |
                    | SSH
                    |
        +-------------------------+
        | Routeur R1              |
        | G0/0 : 192.0.2.1/24     |
        | client AAA              |
        +-------------------------+
                    |
                    | réseau de gestion ou route dédiée
                    |
        +-------------------------+
        | Serveur AAA / RADIUS    |
        | 198.51.100.10           |
        +-------------------------+
```

Dans le schéma, le serveur AAA est représenté séparément pour expliquer les rôles. Le PC d’administration doit pouvoir joindre l’adresse de gestion de R1. R1 doit pouvoir joindre le serveur sur le réseau de gestion. Les routes, les VLAN, les listes de contrôle et les éventuels pare-feu doivent permettre uniquement les flux nécessaires.

### 2.3. Préparer l’accès local et SSH

Avant de configurer un serveur AAA, vérifie qu’un compte local de secours existe et que SSH fonctionne. Le compte ci-dessous est un exemple : remplace son secret par une valeur robuste générée et gérée de manière sûre. Ne réutilise pas ce texte fictif dans un environnement réel.

```text
configure terminal
hostname R1
ip domain name lab.example
username secours privilege 15 secret <REMPLACER_PAR_UN_SECRET_UNIQUE>
ip ssh version 2
crypto key generate rsa modulus 2048
line vty 0 4
 login local
 transport input ssh
 exec-timeout 10 0
end
write memory
```

Selon la version IOS/IOS XE, la génération de clés RSA peut demander une autre syntaxe ou un nombre de bits explicite. Certaines versions préfèrent un algorithme et une taille différents. Vérifie les recommandations actuelles du constructeur et les capacités de la plateforme avant d’utiliser cette commande en production.

Teste la connexion depuis le PC :

```text
ssh secours@192.0.2.1
```

Les systèmes Windows, macOS et Linux proposent souvent un client SSH intégré. Selon l’outil utilisé, le format exact de l’adresse et le nom d’utilisateur peuvent varier. Contrôle que l’invite SSH présente bien l’identité de l’équipement attendu. Une alerte de clé d’hôte inattendue doit être examinée au lieu d’être acceptée automatiquement.

### 2.4. Activer le modèle AAA

Sur de nombreux équipements Cisco, la commande globale `aaa new-model` active le cadre AAA. C’est une modification importante : les règles d’authentification, d’autorisation et d’accounting peuvent alors dépendre des listes de méthodes définies. Une erreur peut affecter les futures connexions. Conserve la session actuelle ouverte pendant les essais et garde un accès console ou une procédure de récupération testée.

```text
configure terminal
aaa new-model
aaa authentication login VTY-LOCAL local
line vty 0 4
 login authentication VTY-LOCAL
 transport input ssh
 exec-timeout 10 0
end
```

Cette liste nommée utilise la base locale. Selon l’équipement, d’autres lignes VTY peuvent exister, par exemple 5 à 15. Vérifie toutes les lignes réellement utilisées, puis applique une politique cohérente à chaque ligne distante pertinente. Certaines plateformes peuvent aussi fournir un canal d’administration distinct ou des outils d’orchestration nécessitant une politique séparée.

Teste une nouvelle session SSH avant de fermer la session initiale. Si l’essai échoue, ne ferme pas l’accès qui fonctionne. Vérifie la liste de méthodes, l’utilisateur local, le statut de SSH, la configuration VTY et la connectivité IP. Une session déjà ouverte ne prouve pas que la prochaine session utilisera la bonne méthode.

### 2.5. Configurer un serveur RADIUS conceptuel

L’exemple suivant illustre une syntaxe de configuration moderne courante sur certaines versions de Cisco IOS/IOS XE. Le nom de serveur, l’adresse, le secret et les listes doivent correspondre à la configuration côté serveur. La plateforme utilisée peut employer une autre syntaxe ; utilise le guide de configuration correspondant à la version installée.

```text
configure terminal
radius server AAA-RADIUS-1
 address ipv4 198.51.100.10 auth-port 1812 acct-port 1813
 key <REMPLACER_PAR_UN_SECRET_LONG_ET_UNIQUE>
exit
aaa group server radius AAA-RADIUS-GROUP
 server name AAA-RADIUS-1
exit
```

Le serveur doit être configuré pour reconnaître R1 comme client RADIUS, avec l’adresse source qui sera réellement utilisée par l’équipement et le même secret partagé. Une divergence entre le secret du client et celui du serveur entraîne souvent une absence de réponse exploitable, un paquet rejeté ou un message d’erreur côté serveur. N’écris jamais un secret réel dans un rapport, une capture d’écran publique ou un dépôt de code partagé.

Les ports classiques sont UDP 1812 pour l’authentification et UDP 1813 pour l’accounting. Les règles réseau doivent autoriser les échanges nécessaires du client vers le serveur et les réponses correspondantes. La supervision doit porter sur le service réel et pas seulement sur un ping : un serveur peut répondre à ICMP tout en ayant le service RADIUS arrêté ou mal configuré.

### 2.6. Ajouter un repli local pour l’authentification des connexions

Une méthode courante consiste à essayer le groupe RADIUS et à prévoir la base locale comme secours lorsque le serveur ne répond pas, sous réserve du comportement exact de la plateforme. Il faut étudier la sémantique du repli : un rejet explicite du serveur ne doit pas être transformé automatiquement en contournement de la politique centrale.

```text
aaa authentication login VTY-AAA group AAA-RADIUS-GROUP local
line vty 0 4
 login authentication VTY-AAA
 transport input ssh
 exec-timeout 10 0
```

Cette configuration est illustrative. Avant de l’utiliser, confirme que l’équipement reconnaît la liste de serveurs, accepte la syntaxe et applique le repli comme prévu. Utilise deux sessions de test : une pour rester connecté et l’autre pour vérifier les nouvelles connexions. La base locale de secours doit être surveillée, et son utilisation devrait produire une alerte quand c’est techniquement possible.

#### Matrice de tests obligatoire

| Test | Situation attendue | Pourquoi le test est important |
|---|---|---|
| 1 | RADIUS disponible, compte autorisé : connexion réussie. | Confirme le chemin normal. |
| 2 | RADIUS disponible, compte explicitement refusé : connexion refusée. | Confirme que le repli ne contourne pas le rejet. |
| 3 | RADIUS injoignable : comportement défini par la politique de secours. | Confirme le comportement de panne. |
| 4 | Secret partagé différent : erreur visible et absence d’accès non autorisé. | Contrôle la gestion d’une mauvaise configuration. |
| 5 | Base locale de secours valide : accès possible lorsque la politique autorise ce scénario. | Valide la procédure de continuité. |
| 6 | Compte local de secours erroné : connexion refusée. | Vérifie qu’un échec d’authentification ne laisse pas un accès implicite. |

### 2.7. Autorisation de l’accès EXEC

L’authentification indique qui se connecte ; l’autorisation EXEC détermine si la session de commande peut être lancée et selon quels paramètres. Sur Cisco IOS/IOS XE, la syntaxe et le support exacts varient avec la version et les méthodes choisies. Le principe général consiste à définir une liste d’autorisation puis à l’appliquer au service concerné.

```text
aaa authorization exec VTY-EXEC group AAA-RADIUS-GROUP local if-authenticated
line vty 0 4
 authorization exec VTY-EXEC
```

N’ajoute pas cette partie à une configuration sans comprendre les réponses que le serveur doit envoyer et les conséquences du repli. `if-authenticated` signifie que l’accès peut être accordé sur la base d’une authentification réussie dans les conditions prévues par la plateforme ; ce n’est pas un substitut à une politique détaillée et ce mot-clé n’a pas exactement le même sens dans tous les services AAA. Une autorisation trop permissive annule une partie de la valeur de l’authentification centralisée.

### 2.8. Activer l’accounting de session

L’accounting peut enregistrer le début et la fin des sessions administratives. L’exemple ci-dessous illustre une forme courante de configuration Cisco ; vérifie si ton modèle, ton image logicielle et ton serveur prennent en charge les méthodes demandées.

```text
aaa accounting exec VTY-ACCOUNTING start-stop group AAA-RADIUS-GROUP
line vty 0 4
 accounting exec VTY-ACCOUNTING
```

Il faut ensuite examiner les traces côté serveur et sur l’équipement. Une commande de configuration présente dans la configuration courante ne prouve pas que l’accounting fonctionne. Le serveur peut être indisponible, la route retour absente, le secret invalide ou la politique de journalisation non configurée. Contrôle aussi la synchronisation de l’heure par NTP.

L’accounting de commandes est un sujet différent. Sur de nombreuses plateformes Cisco, ce suivi granulaire est associé à TACACS+ plutôt qu’à RADIUS. Ne suppose pas que toutes les méthodes AAA ou tous les protocoles acceptent les mêmes types d’enregistrements.

### 2.9. Commandes de vérification et dépannage de base

Les commandes de lecture suivantes sont courantes sur les plateformes IOS/IOS XE, mais leur disponibilité et leur sortie varient. Commence par les commandes non intrusives avant d’activer le débogage.

```text
show running-config | section aaa
show running-config | section radius
show aaa servers
show users
show line
show ip ssh
show logging
```

Elles permettent, selon la plateforme, d’examiner les listes AAA, les serveurs configurés, les sessions, les lignes et les journaux. Pour RADIUS, recherche notamment la bonne adresse de destination, la bonne adresse source, l’état du serveur et les compteurs de délais d’attente. Une erreur de route ou d’ACL peut empêcher le paquet d’atteindre le serveur. Un secret incorrect peut créer un symptôme différent d’un simple problème de connectivité.

Le débogage doit être utilisé avec prudence. Sur un équipement chargé, des commandes `debug` peuvent produire un volume de messages important, affecter les performances ou exposer des données sensibles dans un terminal partagé. Préfère un test bref en fenêtre de maintenance et désactive le débogage immédiatement après l’observation. N’enregistre jamais une trace brute contenant des éléments sensibles dans un espace non protégé.

### 2.10. Sécuriser les lignes VTY et l’accès administratif

AAA ne remplace pas les contrôles du plan de gestion. Les lignes VTY doivent n’accepter que les protocoles prévus et être accessibles uniquement depuis des réseaux d’administration connus, via une ACL ou un contrôle équivalent si la plateforme le permet. La console, l’interface Web, l’API de gestion et les accès out-of-band doivent faire l’objet d’une politique séparée.

Exemple illustratif d’une ACL limitant les connexions SSH au poste d’administration du laboratoire :

```text
ip access-list standard ADMIN-SOURCES
 permit 192.0.2.50
 deny any log
line vty 0 4
 access-class ADMIN-SOURCES in
 transport input ssh
 exec-timeout 10 0
```

Cette ACL est volontairement simple et repose sur une seule adresse source de laboratoire. Dans un réseau réel, il faut définir précisément les sous-réseaux d’administration autorisés, vérifier l’accès de secours et s’assurer que la commande d’ACL correspond au type de terminal. Une règle incorrecte peut bloquer les opérateurs légitimes. `deny any log` peut aussi générer beaucoup de messages ; dimensionne la journalisation pour éviter de saturer les journaux lors d’un balayage ou d’une attaque.

### 2.11. Gestion des secrets et des comptes

Les secrets partagés RADIUS/TACACS+ sont des éléments de configuration sensibles. Stocke-les dans un gestionnaire de secrets ou un coffre adapté plutôt que dans des fichiers texte partagés. Pour chaque relation client-serveur, prévois une procédure de génération, distribution, rotation et révocation. La rotation doit être planifiée pour éviter qu’un client utilisant un ancien secret perde soudainement la capacité de joindre son service d’authentification.

Les comptes doivent être nominatifs lorsqu’une traçabilité individuelle est requise. Les comptes génériques rendent l’enquête difficile et facilitent le partage de secrets. Les comptes de service doivent être documentés, limités à un usage et régulièrement contrôlés. Les comptes d’urgence exigent une procédure différente : accès restreint, stockage sûr, alerte à l’utilisation et changement du secret si une exposition est possible.

N’enregistre pas des mots de passe réels dans des captures de configuration, tickets d’incident, dépôts publics ou documents de cours. Dans ce cours, toutes les chaînes montrées comme placeholders sont fictives ; remplace-les au laboratoire avec des valeurs de test puis supprime-les avant toute publication.

### 2.12. Cas pratique : réseau d’une petite entreprise

Une entreprise dispose d’un routeur d’accès, de deux commutateurs administrables, d’un contrôleur Wi-Fi et de vingt techniciens. Le responsable informatique veut éviter qu’un technicien puisse utiliser un compte partagé pour entrer en mode privilégié sur tous les équipements. Il souhaite également savoir quel compte s’est connecté et quand.

Une approche progressive est la suivante :

1. Inventorier les équipements, leurs versions, leurs adresses de gestion et les protocoles administratifs actifs.
2. Créer des comptes nominatifs et des groupes qui correspondent aux responsabilités réelles.
3. Déployer un serveur AAA de test et déclarer chaque équipement avec la bonne adresse source et un secret robuste.
4. Tester l’authentification centrale sur un appareil non critique, en conservant un accès console ou une session existante.
5. Mettre en place une politique d’autorisation claire : lecture seule pour l’observation, exploitation pour les opérations courantes et privilèges élevés uniquement pour les administrateurs désignés.
6. Activer l’accounting des sessions et vérifier que les enregistrements arrivent au serveur avec des horodatages cohérents.
7. Simuler une panne contrôlée et confirmer que le comportement de secours correspond à la politique décidée.
8. Étendre progressivement aux autres équipements, documenter les exceptions et vérifier qu’aucun ancien mécanisme de connexion faible ne reste actif.

Le projet ne se limite pas à saisir des commandes. Il doit définir le propriétaire du service AAA, le responsable des groupes, la procédure de départ d’un employé, la rotation des secrets, la gestion des certificats et la surveillance du serveur. La configuration technique n’est qu’une partie de la solution ; la gouvernance est indispensable pour garder des droits corrects dans le temps.

### 2.13. Cas pratique : borne Wi-Fi d’entreprise

Dans un réseau Wi-Fi d’entreprise, les terminaux peuvent utiliser 802.1X et un serveur RADIUS. Lorsqu’un appareil tente de se connecter, l’authentificateur transmet les échanges pertinents au serveur. Le serveur valide la méthode choisie puis renvoie une décision et éventuellement des attributs de politique. Le point d’accès ou le contrôleur applique la décision.

Le déploiement doit préparer les profils des terminaux et établir comment ceux-ci vérifieront le certificat du serveur. Une documentation utilisateur doit expliquer comment installer le profil approuvé sans inviter les personnes à ignorer systématiquement les avertissements de certificat. Les appareils non compatibles avec la méthode standard doivent recevoir une solution séparée et limitée, pas un accès illimité par défaut.

Un VLAN invité ne doit pas être assimilé au réseau interne. Les règles de pare-feu doivent limiter les flux des invités aux services requis, par exemple Internet et un service d’accès autorisé, et empêcher l’accès aux interfaces d’administration. Si le serveur RADIUS est indisponible, la politique doit préciser s’il existe un accès de secours et quelle zone celui-ci peut atteindre.

### 2.14. Exercices pratiques

**Exercice 1 — Concepts.** Un administrateur se connecte avec le bon mot de passe mais ne peut pas exécuter une commande de configuration. Quelle fonction AAA peut expliquer ce résultat ? Réponse : l’autorisation. L’identité peut être valide tandis que les permissions de la session ne comprennent pas cette commande.

**Exercice 2 — RADIUS sans réponse.** Le commutateur indique un délai dépassé vers le serveur. Donne quatre hypothèses et une vérification pour chacune. Réponse possible : mauvaise route (vérifier la table de routage), ACL qui bloque UDP (vérifier les règles et captures), adresse source inattendue (vérifier l’adresse utilisée et le client déclaré côté serveur), serveur arrêté ou service non à l’écoute (vérifier le service côté serveur). Un secret partagé erroné est aussi à vérifier, mais il peut produire des journaux spécifiques côté serveur.

**Exercice 3 — Rejet contre délai dépassé.** Pourquoi faut-il différencier les deux ? Réponse : un rejet signifie généralement que le serveur a traité la demande et refusé l’accès, alors qu’un délai dépassé signale une absence de réponse à temps. Le comportement de secours ne doit pas permettre de contourner un refus explicite.

**Exercice 4 — Compte local d’urgence.** Cite trois mesures de protection. Réponse : accès limité et secret robuste, stockage sûr et disponibilité contrôlée, alerte à l’utilisation et rotation après usage ou exposition. On peut ajouter des tests périodiques et une procédure documentée.

**Exercice 5 — Accounting absent.** L’utilisateur se connecte correctement, mais aucune trace de démarrage n’apparaît. Donne un plan de vérification. Réponse : vérifier que l’accounting est activé et appliqué à la ligne ou au service ; vérifier la destination et la connectivité ; examiner les journaux du serveur ; contrôler le secret, la route retour et les règles réseau ; valider l’heure et le format des événements.

**Exercice 6 — Wi-Fi d’entreprise.** Un poste se connecte à un faux réseau qui présente un certificat inattendu. Quel comportement utilisateur faut-il enseigner ? Réponse : ne pas accepter aveuglément le certificat ; vérifier le profil officiel, le nom attendu et la chaîne de confiance, puis contacter l’équipe de support selon la procédure.

**Exercice 7 — Moindre privilège.** Un technicien chargé de consulter l’état des ports demande le privilège maximal pour gagner du temps. Quelle alternative proposer ? Réponse : définir un rôle lecture seule avec les commandes nécessaires, puis documenter une procédure d’escalade temporaire pour les opérations qui requièrent davantage de droits.

### 2.15. Checklist de validation du laboratoire

Avant de considérer le laboratoire opérationnel, vérifie chaque élément. Cette liste ne remplace pas un plan de changement, mais elle aide à éviter les oublis courants.

- [ ] Le compte local de secours existe et a été testé.
- [ ] SSH fonctionne depuis une source d’administration autorisée.
- [ ] AAA est activé avec une liste de méthodes comprise et documentée.
- [ ] Le serveur AAA connaît le client avec la bonne adresse source.
- [ ] Le secret partagé est cohérent, robuste et conservé de manière sûre.
- [ ] Les règles de pare-feu autorisent les échanges nécessaires et rien de plus.
- [ ] Une authentification acceptée a été testée.
- [ ] Un rejet explicite a été testé.
- [ ] Une panne serveur contrôlée a été testée.
- [ ] Le comportement du compte local de secours est conforme à la politique.
- [ ] L’autorisation ne donne pas de droits excessifs par défaut.
- [ ] L’accounting est visible côté serveur et les horloges sont cohérentes.
- [ ] Les services administratifs inutiles sont désactivés ou restreints.
- [ ] La configuration et la procédure de retour arrière sont documentées.
- [ ] Aucun secret de test n’est resté dans un document ou un dépôt partagé.

> **Astuce :** fais les tests en ouvrant une deuxième session SSH et garde la première ouverte jusqu’à validation complète. Si tu disposes d’un accès console hors bande, vérifie-le avant la modification. Une procédure de retour arrière utile doit pouvoir être exécutée même si AAA centralisé ne répond plus.


## 3. Dépannage et sécurité

### 3.1. Méthode de diagnostic : partir de la couche la plus simple

Un problème d’authentification peut provenir de plusieurs endroits : terminal, réseau, configuration de l’équipement, protocole, serveur AAA, annuaire ou politique. Modifier directement les règles de sécurité sans isoler le domaine du problème peut créer une faille ou rendre le diagnostic plus difficile.

Utilise une séquence stable :

1. **Identifier le service concerné.** S’agit-il de SSH, d’une connexion VPN, de 802.1X filaire, de Wi-Fi ou d’une interface d’administration Web ? Chaque service peut utiliser une liste de méthodes AAA distincte.
2. **Vérifier le client.** Confirmer l’adresse source réelle, l’identité du client déclarée côté serveur, l’heure et les paramètres de transport.
3. **Vérifier la connectivité.** Tester route, résolution DNS si un nom est utilisé, ACL, pare-feu, ports et route retour. Un ping réussi ne valide pas l’application AAA.
4. **Examiner les journaux côté équipement.** Chercher une demande envoyée, une réponse reçue, un rejet, un délai dépassé ou une erreur de configuration.
5. **Examiner les journaux côté serveur.** Ils peuvent expliquer la méthode choisie, la règle appliquée, un secret incohérent, une identité inconnue ou un certificat invalide.
6. **Tester l’autorisation.** Si l’identité est acceptée, vérifier le rôle, le groupe, les attributs et l’action refusée.
7. **Vérifier l’accounting.** Si la connexion fonctionne, s’assurer que les événements sont créés et reçus.
8. **Reproduire avec un compte de test.** Éviter de répéter les essais avec un compte de production ou de verrouiller le compte d’un administrateur.

### 3.2. Erreurs fréquentes et pistes de résolution

| Symptôme | Cause possible | Vérification | Action prudente |
|---|---|---|---|
| Tous les utilisateurs échouent | Serveur arrêté, route ou ACL incorrecte, mauvaise configuration du client. | Journaux du serveur, reachability applicative, adresse source, compteurs de timeout. | Restaurer le chemin prévu ou appliquer le secours documenté. |
| Un seul utilisateur échoue | Compte désactivé, mauvais secret utilisateur, groupe absent, méthode incompatible. | Logs de politique et état du compte. | Corriger le compte ou le groupe ; ne pas accorder des droits globaux pour dépanner. |
| Le serveur reçoit la demande mais rejette | Identité incorrecte, méthode interdite ou règle de politique négative. | Motif de rejet côté serveur. | Corriger la politique ou les données selon le besoin, sans contourner le refus. |
| Aucun paquet n’apparaît côté serveur | Mauvaise destination, route, ACL, source ou service configuré. | Capture au point source et au serveur, compteurs réseau. | Restaurer le chemin minimal requis. |
| SSH local fonctionne mais pas l’accès AAA | Liste de méthodes appliquée à la mauvaise ligne, serveur inaccessible ou règle centrale erronée. | Configuration VTY, serveur, méthodes et journaux. | Garder la session ouverte et revenir à la méthode testée si nécessaire. |
| Authentification réussie, privilèges incorrects | Autorisation EXEC, profil ou mapping de groupe. | Attributs reçus et rôle appliqué. | Corriger l’autorisation avec le moindre privilège. |
| Connexion OK, aucune trace accounting | Accounting non appliqué, serveur indisponible, règle de collecte incorrecte. | Configuration, journaux, réponses accounting et heure. | Restaurer la collecte et documenter l’éventuelle lacune d’audit. |
| Échec après changement de secret | Secrets différents de part et d’autre, mauvais client déclaré ou rotation incomplète. | Comparaison par procédure sûre, journaux et état des clients. | Reprendre la rotation contrôlée et valider les deux côtés. |
| Échecs 802.1X sur certains terminaux | Profil EAP, certificat expiré, chaîne de confiance ou supplicant incompatible. | Journaux EAP, certificat, profil et heure. | Déployer un profil approuvé ou corriger le cycle de vie du certificat. |
| Session ouverte trop longtemps après départ de l’utilisateur | Révocation ou déconnexion non propagée, session persistante. | État de session sur l’équipement et serveur. | Révoquer selon la méthode supportée, documenter puis améliorer le délai de réévaluation. |

### 3.3. Sécuriser le transport AAA

Les échanges AAA transportent ou influencent des décisions sensibles. Ils doivent emprunter un chemin maîtrisé : réseau de gestion dédié ou segment contrôlé, filtrage source/destination, supervision, et options de transport sécurisé prises en charge. RADIUS classique ne fournit pas le chiffrement global attendu d’un tunnel moderne. Si la solution supporte RADIUS sur TLS/DTLS, évalue son modèle de certificats, sa compatibilité et ses procédures d’exploitation avant de le déployer.

Les serveurs AAA ne doivent pas être exposés directement à Internet sans architecture spécialement conçue et validée. Place-les sur un segment protégé, limite les clients connus et autorise uniquement les flux nécessaires. Le client doit envoyer les demandes depuis une adresse source stable et déclarée côté serveur. Une traduction NAT imprévue peut faire apparaître une adresse différente et empêcher l’identification du client.

TACACS+ est également un service sensible. L’utiliser ne signifie pas que son trafic est automatiquement protégé contre toute interception par un chiffrement moderne de bout en bout. Suis les recommandations de l’implémentation, protège le chemin réseau et utilise des mécanismes de transport sûrs quand ils sont pris en charge dans l’architecture.

### 3.4. Protéger les identités et les secrets

Les identifiants réseau peuvent donner accès à des ressources critiques. Définis une politique de comptes nominatifs, de mots de passe robustes ou d’authentification par certificat, de MFA adaptée, de suppression des comptes obsolètes et de séparation des comptes standards et privilégiés.

Les secrets partagés doivent être uniques lorsque le système le permet, difficiles à deviner et stockés dans un coffre. N’utilise pas une valeur triviale comme `cisco`, `radius123` ou le nom de l’entreprise. Ne partage pas un même compte administrateur entre plusieurs techniciens : cela réduit la traçabilité et augmente le risque lorsqu’un secret est compromis.

Une procédure de départ d’un collaborateur doit couper les accès centraux, révoquer les certificats ou facteurs associés si nécessaire, supprimer les sessions persistantes et vérifier les comptes locaux ou de secours auxquels il aurait pu avoir accès. Une désactivation dans un annuaire ne garantit pas automatiquement que toutes les sessions existantes sont fermées.

### 3.5. Limiter le risque lié au compte de secours

Le compte local de secours répond à un besoin de continuité, mais il peut devenir une porte dérobée s’il est partagé, jamais testé ou jamais renouvelé. Attribue-lui un propriétaire, stocke son secret dans un coffre, limite les personnes autorisées, consigne les conditions d’usage et crée une alerte à chaque connexion si la plateforme le permet.

Dans les environnements critiques, on peut prévoir un accès console ou un réseau d’administration hors bande. Cet accès doit être protégé physiquement et logiquement. Un compte de secours n’est pas une justification pour laisser Telnet, des mots de passe faibles ou une interface Web exposée.

### 3.6. Distinguer les pannes de service et les erreurs de politique

Cette distinction est essentielle lors d’un incident. Si le serveur répond `Access-Reject`, la priorité consiste à comprendre pourquoi la politique refuse l’identité : mot de passe incorrect, groupe non autorisé, méthode incompatible, certificat expiré ou condition contextuelle. Modifier le timeout réseau ne résoudra pas un refus explicite.

Si le client attend sans réponse, il faut vérifier la route, l’ACL, la destination, le service, le secret, l’adresse source et les mécanismes de retransmission. Un secret incorrect ne se manifeste pas forcément de façon identique dans toutes les implémentations. Compare les journaux côté serveur et client avant de conclure.

Si l’authentification réussit mais l’accès reste limité, recherche une décision d’autorisation, un rôle, un profil ou un attribut incompatible. Si l’accès fonctionne mais qu’il n’existe aucune trace, le problème peut être lié à l’accounting plutôt qu’à l’authentification. Garder ces catégories distinctes évite les modifications inutiles et les contournements de sécurité.

### 3.7. Protection contre les attaques et les erreurs humaines

Un service AAA doit être surveillé pour détecter les tentatives répétées, les connexions en dehors des heures normales, les accès depuis une source inattendue ou les élévations de privilège inhabituelles. Ces signaux doivent être corrélés avec les journaux SSH, VPN, pare-feu et annuaire. Une seule alerte ne suffit pas toujours pour distinguer une erreur de saisie d’une attaque ; le contexte et le volume sont importants.

Les protections usuelles comprennent : limitation de l’accès aux interfaces de gestion, verrouillage ou temporisation lorsque cela est approprié, MFA pour les accès privilégiés, suppression des comptes partagés, rotation des secrets exposés, supervision de la disponibilité et contrôle de changement. Évite les règles d’auto-bloquage agressives qui pourraient couper tous les administrateurs en cas d’incident ; prévois une procédure de reprise maîtrisée.

Un compte administrateur compromis peut changer des ACL, créer de nouveaux comptes, désactiver la journalisation ou détourner le trafic. C’est pourquoi l’autorisation des commandes, la séparation des rôles et la conservation des journaux hors de l’équipement sont utiles. Pour les opérations particulièrement sensibles, exige une validation supplémentaire, un ticket de changement ou un accès temporaire approuvé.

### 3.8. Journalisation et confidentialité

Collecte seulement les données nécessaires pour gérer les accès et enquêter. Les journaux peuvent contenir des noms de comptes, des adresses IP, des identifiants d’appareils et des détails sur les habitudes de connexion. Limite leur lecture aux opérateurs autorisés, chiffre les transferts lorsque le système le permet et protège les sauvegardes de journaux.

Définis une rétention adaptée aux objectifs de sécurité et aux obligations applicables. Trop peu de rétention peut empêcher une investigation ; conserver tout indéfiniment peut augmenter le risque pour la vie privée et la sécurité. Documente les propriétaires, les formats, les systèmes de stockage et la procédure d’accès aux traces.

Une alerte de sécurité doit être actionnable : nom de l’événement, équipement et compte concernés, horodatage, niveau de gravité et première piste de diagnostic. Évite les règles qui produisent un volume immense de bruit sans procédure de tri. Les tableaux de bord doivent mesurer la disponibilité AAA, le taux de succès et de rejet, les délais de réponse et les erreurs de communication, sans transformer chaque erreur bénigne en incident majeur.

### 3.9. Haute disponibilité et continuité

Un serveur AAA centralisé est un service critique. Selon le design, on peut déployer plusieurs serveurs dans un groupe, les répartir entre sites ou placer des serveurs proches des équipements. Il faut tester ce que fait réellement le client lorsque le serveur primaire échoue, lorsqu’il est lent, lorsqu’il rejette une demande ou lorsqu’il revient en ligne.

Le failover doit être cohérent. Trop de temps d’attente ou trop de retransmissions peuvent rendre l’ouverture de session très lente. À l’inverse, passer immédiatement à un accès local trop permissif peut ouvrir une voie de contournement. Choisis les délais et méthodes à partir des besoins opérationnels et du niveau de risque, puis mesure les résultats dans des essais contrôlés.

La haute disponibilité du serveur n’est qu’un élément : le DNS, NTP, l’annuaire, les certificats, la PKI, les liaisons WAN, le stockage, le système de journalisation et la configuration du client peuvent également être des points de défaillance. Une conception fiable cartographie toutes ces dépendances et attribue un responsable à chacune.

### 3.10. Revue périodique des comptes et des politiques

Les droits vieillissent : une personne change d’équipe, un prestataire termine sa mission, un équipement est retiré ou un rôle temporaire devient permanent. Planifie une revue régulière des comptes, groupes, méthodes d’authentification, secrets de clients, règles d’autorisation et exceptions. Le rythme doit correspondre au risque et aux contraintes de l’organisation.

La revue devrait rechercher les comptes sans propriétaire, les identifiants partagés, les comptes de service trop puissants, les équipements qui n’utilisent plus le serveur attendu et les méthodes de secours oubliées. Compare la configuration effective avec l’architecture documentée. Les divergences doivent être corrigées par un changement contrôlé afin d’éviter de supprimer par erreur un accès critique.

Les exceptions doivent comporter une justification, un propriétaire, une date de révision et une manière de les retirer. Une exception sans date de fin tend à devenir permanente. Documenter une exception n’est pas la rendre sûre : il faut aussi réduire son périmètre et vérifier que les contrôles compensatoires fonctionnent.

### 3.11. Sécurité de 802.1X et des méthodes EAP

Un déploiement 802.1X mal préparé peut pousser les utilisateurs à contourner les contrôles lorsqu’ils rencontrent des erreurs de certificat ou des incompatibilités. La configuration des supplicants doit être distribuée par un canal fiable, avec les autorités de certification et identités serveur attendues. L’assistance doit enseigner aux utilisateurs à reconnaître un avertissement anormal au lieu de leur demander de cliquer systématiquement sur « accepter ».

Pour EAP-TLS, le cycle de vie des certificats comprend émission, stockage de la clé privée, renouvellement et révocation. Un certificat expiré ou absent peut bloquer un appareil légitime ; une clé privée compromise peut nécessiter une révocation urgente. La procédure de renouvellement doit prévoir les terminaux hors ligne et vérifier que la nouvelle chaîne de confiance est déployée avant l’expiration des certificats actuels.

Les appareils qui ne prennent pas en charge 802.1X nécessitent parfois une autre forme de contrôle. La solution ne doit pas leur donner automatiquement la même confiance qu’à un poste d’entreprise pleinement géré. Un segment restreint, des politiques de pare-feu et une surveillance renforcée peuvent limiter le risque, selon les besoins réels.

### 3.12. Mini-plan de réponse à incident AAA

Lorsqu’un compte privilégié semble compromis, les objectifs sont de limiter l’accès, de préserver les éléments utiles et de rétablir une identité fiable.

1. Identifier le compte, les équipements et la période concernés. Vérifier les journaux AAA et les traces des équipements.
2. Confirmer l’incident avec les responsables autorisés, en évitant d’effacer ou de modifier inutilement les preuves.
3. Révoquer ou désactiver l’identité selon la procédure d’urgence ; invalider les facteurs ou certificats compromis lorsque c’est nécessaire.
4. Terminer les sessions actives ou les accès persistants avec les méthodes supportées.
5. Vérifier les changements de configuration, comptes nouvellement créés, commandes sensibles et modifications de journalisation.
6. Préserver les journaux hors des appareils concernés et noter les horodatages, sources et actions réalisées.
7. Restaurer l’accès légitime par une procédure testée, puis changer les secrets exposés et réexaminer les droits.
8. Documenter la cause racine et les mesures correctives, sans réduire l’analyse à un simple changement de mot de passe.

La communication pendant l’incident doit être précise. Ne partage pas les secrets ou les journaux sensibles sur un canal ouvert. Si l’accès central est affecté, utiliser un compte de secours doit être autorisé, consigné et suivi d’une revue après rétablissement.

### 3.13. Étude de cas : un administrateur n’accède plus au routeur

**Situation.** Après une modification AAA, les connexions SSH échouent pour plusieurs administrateurs. La session déjà ouverte fonctionne encore. Le serveur central semble disponible parce qu’il répond aux tests ICMP.

**Étape 1 — préserver l’accès restant.** Ne ferme pas la session qui fonctionne. Si disponible, confirme l’accès console. Évite de redémarrer le routeur ou de modifier plusieurs règles à la fois.

**Étape 2 — déterminer le service affecté.** Vérifie si le problème concerne SSH uniquement, la console aussi ou plusieurs services. Examine les listes de méthodes associées aux lignes VTY et les éventuelles restrictions d’accès par ACL.

**Étape 3 — vérifier la demande AAA.** Consulte les journaux de l’équipement et du serveur. S’il n’y a aucune demande au serveur, recherche le routage, le filtrage, l’adresse source et la destination. Si la demande arrive mais est rejetée, examine l’identité, la règle et le groupe. Si le serveur accepte mais la connexion reste impossible, vérifie l’autorisation EXEC et les autres politiques appliquées.

**Étape 4 — appliquer le retour arrière prévu.** Utilise uniquement la procédure approuvée et documentée. Le compte local ne doit être utilisé que selon la politique, pas pour contourner un refus explicite de l’AAA central. Si la configuration a supprimé les accès de secours, utilise l’accès console ou la procédure de récupération du constructeur.

**Étape 5 — retester et analyser.** Vérifie les scénarios acceptés, refusés et indisponibles. Enregistre la cause racine, la correction et les tests qui éviteront une répétition.

Cet exemple montre qu’un serveur joignable par ping n’est pas forcément prêt à répondre à une demande AAA. Les services applicatifs, secrets, politiques et listes de méthodes doivent être validés séparément.

### 3.14. Recommandations opérationnelles à retenir

- Utilise des identités nominatives et un modèle de rôles compréhensible.
- Protège SSH et les autres interfaces de gestion ; n’expose pas inutilement les services d’administration.
- Déploie AAA progressivement, en conservant une voie de récupération contrôlée.
- Différencie un rejet explicite d’une indisponibilité du serveur.
- Vérifie les autorisations et l’accounting en plus de l’authentification.
- Protège et renouvelle les secrets partagés ; ne les publie jamais dans les tickets ou dépôts ouverts.
- Synchronise les horloges et centralise les traces utiles.
- Teste la haute disponibilité et les comptes de secours dans des conditions réalistes.
- Revois périodiquement les comptes, groupes et exceptions.
- Documente les changements, les responsables et la procédure de retour arrière.

> **Danger :** ne déploie pas une nouvelle liste AAA sur un équipement distant critique sans avoir validé un accès de secours indépendant, une procédure de retour arrière et les scénarios d’acceptation, de rejet et de panne. La perte d’accès administratif peut empêcher la correction de la configuration qui a provoqué la panne.


## Points à retenir

1. AAA signifie authentification, autorisation et accounting ; ces fonctions sont différentes et complémentaires.
2. RADIUS est largement utilisé pour l’accès réseau, le Wi-Fi, 802.1X et certains VPN. TACACS+ est fréquent pour l’administration des équipements réseau.
3. Le serveur AAA centralise les identités ou les politiques, mais il dépend du routage, du DNS éventuel, de l’heure, des certificats et de sa propre disponibilité.
4. Un rejet explicite n’équivaut pas à un délai dépassé. Le mécanisme de secours doit respecter cette différence.
5. Une authentification réussie ne signifie pas que l’utilisateur doit obtenir les privilèges maximaux.
6. Les journaux doivent être exploitables, horodatés, protégés et conservés selon une politique claire.
7. 802.1X contrôle l’accès à un port réseau ; EAP fournit un cadre pour les méthodes d’authentification.
8. Les certificats et MFA peuvent améliorer l’assurance d’identité, mais ne remplacent pas une politique d’autorisation correcte.
9. Pour administrer un équipement, SSH est préférable à Telnet et les interfaces de gestion doivent être limitées aux sources autorisées.
10. Tester le compte de secours, la disponibilité du serveur et le retour arrière fait partie du déploiement, pas d’une option à ajouter après un incident.

### Références techniques

- Cisco, *RADIUS Configuration Guide, Cisco IOS XE* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/sec-crypto/radius/radius-configuration-guide/radius.html
- RFC 2865, *Remote Authentication Dial In User Service (RADIUS)* : https://www.rfc-editor.org/rfc/rfc2865.html
- RFC 2866, *RADIUS Accounting* : https://www.rfc-editor.org/rfc/rfc2866.html
- RFC 8907, *The Terminal Access Controller Access-Control System Plus (TACACS+) Protocol* : https://www.rfc-editor.org/rfc/rfc8907.html
- IEEE 802.1X, *Port-Based Network Access Control* : https://standards.ieee.org/standard/802_1X-2020.html
- RFC 3580, *IEEE 802.1X Remote Authentication Dial In User Service (RADIUS) Usage Guidelines* : https://www.rfc-editor.org/rfc/rfc3580.html
- RFC 9190, *EAP-TLS 1.3: Using the Extensible Authentication Protocol with TLS 1.3* : https://www.rfc-editor.org/rfc/rfc9190.html
- NIST SP 800-63B, *Digital Identity Guidelines: Authentication and Lifecycle Management* : https://pages.nist.gov/800-63-3/sp800-63b.html
- NIST SP 800-53, *Security and Privacy Controls for Information Systems and Organizations* : https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
